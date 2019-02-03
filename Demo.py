import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import re
import time

# 头文字，模仿浏览器，以防屏蔽IP
headers_one = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}
headers_two = {
    'user-agent': "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
}
headers_three = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}
headers_list = [headers_one, headers_two, headers_three]

# 定义 第一个页面的数据 的变量
name_list = []  # 项目名称
link_list = []  # 项目连链接
date_p_list = []  # 项目刊登日期

# t（tender）代表招标 、 w（winning bid）代表中标
w_f_name_bidder_list = []  # 第一中标候选人
w_s_name_bidder_list = []  # 第二中标候选人
w_t_name_bidder_list = []  # 第三中标候选人
w_price_list = []  # 中标价
t_name_list = []  # 项目招标人
t_num_list = []  # 项目招标编号
t_depa_list = []  # 招标代理机构
BRN_list = []  # 工商注册号
proposed_bidder = []  # 拟中标人
accept_com_depa_list = []  # 投诉受理部门
w_s_price_list = []  # 第二中标人价格
w_t_price_list = []  # 第三中标人价格

list_c_dict = {
    1: w_f_name_bidder_list, 2: w_s_name_bidder_list, 3: w_t_name_bidder_list,
    4: w_price_list, 5: t_name_list, 6: t_num_list, 7: t_depa_list, 8: BRN_list, 9: proposed_bidder,
    10: accept_com_depa_list, 11: w_s_price_list, 12: w_t_price_list
}


def parse_outer_page():
    domain = "https://www.cqggzy.com"
    start_url = ("http://www.cqggzy.com/web/services/PortalsWebservice/getInfoList?response=application/"
                 "json&pageIndex=15583&pageSize=1"  # 爬的两天，网站上传了两次新数据，在这里修改。
                 "&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=005002001&title="
                 "&infoC=&_=1548761616465")
    response = requests.get(start_url, headers=headers_list[random.randint(0, 2)], verify=False)

    # 将返回的JSON数据 转换为 列表
    response_items_list = eval(response.json().get("return"))

    # 获取 项目名称、项目链接、项目刊登日期 数据
    for item in response_items_list:
        name_list.append(item.get("title"))
        link_list.append(domain + item.get("infourl"))
        date_p_list.append(item.get("infodate"))


def parse_inner_page():
    count = 0
    for item in link_list:

        # 在控制台显示次数
        count = count + 1
        w_f_price_tmp = []
        w_s_price_tmp = []
        w_t_price_tmp = []
        accept_com_depa_tmp = []
        proposed_bidder_tmp = []
        BRN_tmp = []
        t_num_tmp = []
        t_name_tmp = []
        w_price_tmp = []
        w_f_name_bidder_tmp = []
        w_s_name_bidder_tmp = []
        w_t_name_bidder_tmp = []
        t_depa_tmp = []

        list_c_dict_tmp = {
            1: w_f_name_bidder_tmp, 2: w_s_name_bidder_tmp, 3: w_t_name_bidder_tmp,
            4: w_price_tmp, 5: t_name_tmp, 6: t_num_tmp, 7: t_depa_tmp, 8: BRN_tmp, 9: proposed_bidder_tmp,
            10: accept_com_depa_tmp, 11: w_s_price_tmp, 12: w_t_price_tmp, 13: w_f_price_tmp
        }
        response = requests.get(item, headers=headers_list[random.randint(0, 2)])
        print(response)
        print(count)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        s = BeautifulSoup(response.text, "html5lib")

        if len(s.find_all(name="tbody")) != 0:
            trs = s.find_all(name="tbody")[0].find_all("tr")
            list_c_dict_tmp = crawl_data(trs)

        # 整合
        for nc in range(1, 13):
            list_c_dict[nc].append(list_c_dict_tmp[nc])

        # 测试
        # for i in range(1, 13):
        # print(len(list_c_dict[i]))


def crawl_data(trs):
    # 初始化数据
    w_f_price_tmp = []
    w_s_price_tmp = []
    w_t_price_tmp = []
    accept_com_depa_tmp = []
    proposed_bidder_tmp = []
    BRN_tmp = []
    t_num_tmp = []
    t_name_tmp = []
    w_price_tmp = []
    w_f_name_bidder_tmp = []
    w_s_name_bidder_tmp = []
    w_t_name_bidder_tmp = []
    t_depa_tmp = []

    list_c_dict_tmp = {
        1: w_f_name_bidder_tmp, 2: w_s_name_bidder_tmp, 3: w_t_name_bidder_tmp,
        4: w_price_tmp, 5: t_name_tmp, 6: t_num_tmp, 7: t_depa_tmp, 8: BRN_tmp, 9: proposed_bidder_tmp,
        10: accept_com_depa_tmp, 11: w_s_price_tmp, 12: w_t_price_tmp, 13: w_s_price_tmp
    }
    for tr in trs:
        ps = tr.find_all("p")
        if not ps:
            tds = tr.find_all("td")
            count = -1
            for td in tds:
                count = count + 1
                print(td.get_text())
                tmp = re.sub(r"\s+[:：\"“”\']", "", td.get_text())
                # 属性class=B的标签里找第一、二、三中标候选人及价格
                td_tmp = td.find_all(attrs={"class": "B"})
                print(tmp)
                if tmp != '':
                    if tmp == "工程编码":
                        t_num_tmp.append(tds[1].get_text())
                    elif tmp == "标段编号":
                        t_num_tmp.append(tds[1].get_text())
                    elif tmp == "填报人":  # 理解为招标人
                        t_name_tmp.append(tds[1].get_text())
                    elif tmp == "项目法人":
                        t_name_tmp.append(tds[1].get_text())
                    elif tmp == "填报单位":  # 理解为招标代理机构
                        t_depa_tmp.append(tds[1].get_text())
                    elif tmp == "招标代理机构":
                        t_depa_tmp.append(tds[1].get_text())
                    elif len(td_tmp) > 15:
                        for i in range(0, len(td_tmp)):
                            # 第一中标候选人及价格
                            if td_tmp[i].get_text() == "1":
                                w_f_name_bidder_tmp.append(td_tmp[i + 1].get_text())
                                w_price_tmp.append(td_tmp[i + 2].get_text())
                            # 第二中标候选人及价格
                            if td_tmp[i].get_text() == "2":
                                w_s_name_bidder_tmp.append(td_tmp[i + 1].get_text())
                                w_s_price_tmp.append(td_tmp[i + 2].get_text())
                            # 第三中标候选人及价格
                            if td_tmp[i].get_text() == "3":
                                w_t_name_bidder_tmp.append(td_tmp[i + 1].get_text())
                                w_t_price_tmp.append(td_tmp[i + 2].get_text())

                    elif td.get_text() == "第一中标（选）候选人":
                        w_f_name_bidder_tmp.append(tds[count + 1].get_text())
                    elif td.get_text() == "第二中标（选）候选人":
                        w_s_name_bidder_tmp.append(tds[count + 1].get_text())
                    elif td.get_text() == "第三中标（选）候选人":
                        w_t_name_bidder_tmp.append(tds[count + 1].get_text())
                    elif td.get_text() == "中标（选）人":
                        proposed_bidder_tmp.append(tds[count + 1].get_text())
                    elif td.get_text() == "中标（选）价（万元）":
                        w_price_tmp.append(tds[count + 1].get_text())

        else:
            # 记录有多少个item（进行了多少次循环）用于最后判断 本页面 抓取数据 是否完成
            # count = count + 1
            # 抓取数据
            if ps and (len(ps) > 1):
                tmp = re.sub(r"\s+", "", ps[0].get_text().strip())

                # print(ps)
                # print(len(ps))
                # print(tmp)

                # 招标编码、招标人（填报人）、招标代理机构
                if tmp == "招标公告编号":
                    t_num_tmp.append(ps[1].get_text().strip())
                elif tmp == "招标编码":
                    t_num_tmp.append(ps[1].get_text().strip())
                elif tmp == "招标人":
                    if ps[1].get_text() == "单位名称":
                        t_name_tmp.append(ps[2].get_text().strip())
                    else:
                        t_name_tmp.append(ps[1].get_text().strip())
                elif tmp == "填报人":
                    t_name_tmp.append(ps[1].get_text().strip())
                elif tmp == "招标代理机构":
                    t_depa_tmp.append(ps[1].get_text().strip())

                # 第二中标人 及 价格
                elif tmp == "第二中标候选人":
                    w_s_name_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_s_price_tmp.append(spider_price(ps))
                elif tmp == "第二中标（选）候选人":
                    w_s_name_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_s_price_tmp.append(spider_price(ps))

                # 第三中标人 及 价格
                elif tmp == "第三中标候选人":
                    w_t_name_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_t_price_tmp.append(spider_price(ps))
                elif tmp == "第三中标（选）候选人":
                    w_t_name_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_t_price_tmp.append(spider_price(ps))

                # 中标人、拟中标人、中标（选）人
                elif tmp == "中标人":
                    proposed_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_price_tmp.append(spider_price(ps))
                        # print()
                elif tmp == "中标（选）人":
                    proposed_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        w_price_tmp.append(spider_price(ps))
                elif tmp == "拟中标人":
                    proposed_bidder_tmp.append(ps[1].get_text().strip())
                    if len(ps) > 3:
                        # print(2)
                        w_price_tmp.append(spider_price(ps))

                # 中标人、拟中标人、中标（选）人 的 中标金额
                elif tmp == "中标金额(万元)":
                    w_price_tmp.append(ps[1].get_text().strip())
                elif tmp == "中标金额(元)":
                    w_price_tmp.append(ps[1].get_text().strip())
                elif tmp == "中标（选）价（元）":
                    w_price_tmp.append(ps[1].get_text().strip())
                elif tmp == "中标价":
                    w_price_tmp.append(ps[1].get_text().strip())

                # 工商注册号、投诉受理部门
                elif tmp == "工商注册号":
                    BRN_tmp.append(ps[1].get_text().strip())
                    # print(ps[1].get_text())
                elif tmp == "投诉受理部门":
                    accept_com_depa_tmp.append(ps[1].get_text().strip())

                # 第一中标候选人 及 价格
                elif len(ps) > 4:
                    for i in range(0, len(ps)):
                        if ps[i].get_text() == "第一中标候选人":
                            if i + 2 <= len(ps):
                                w_f_name_bidder_tmp.append(ps[i + 1].get_text().strip())
                            # print(len(ps))
                            # print(i)
                            if i + 4 <= len(ps):
                                w_f_price_tmp.append(ps[i + 3].get_text().strip())
                                # print(ps[i + 3].get_text())
                elif len(ps) > 4:
                    for i in range(0, len(ps)):
                        if ps[i].get_text() == "第一中标（选）候选人":
                            w_f_name_bidder_tmp.append(ps[i + 1].get_text().strip())
                            if i + 4 <= len(ps):
                                w_f_price_tmp.append(ps[i + 2].get_text().strip())
    return list_c_dict_tmp


def spider_price(ps):
    """
    There is code duplication when crawling prices
    Param ps
    Return: price
    """
    # 去除所有空格
    ps_tmp = re.sub(r"\s+", "", ps[2].get_text().strip())
    ps_tmp_t = re.sub(r"\s+", "", ps[3].get_text().strip())
    # print(ps_tmp)
    # print(ps_tmp_t)
    # 关于括号的全角 和 半角 的不同情况 应该有更好的解决办法吧！！
    if ps_tmp == "中标金额（万元）":
        return ps[3].get_text()
    elif ps_tmp == "中标金额(万元)":
        return ps[3].get_text()
    elif ps_tmp == "中标金额":
        if ps[3].get_text() == "（元）":
            return ps[4].get_text()
    elif ps_tmp == "中标金额(元)":
        return ps[3].get_text()
    elif ps_tmp == "中标金额（元）":
        return ps[3].get_text()
    elif ps_tmp == "中标（选）价（元）":
        return ps[3].get_text()

    elif ps_tmp_t == "中标金额(万元)":
        return ps[4].get_text()
    if ps_tmp == "中标金额（万元）":
        return ps[3].get_text()
    elif ps_tmp_t == "中标金额(元)":
        return ps[4].get_text()
    elif ps_tmp == "中标金额（元）":
        return ps[4].get_text()
    elif ps_tmp_t == "中标（选）价（元）":
        return ps[4].get_text()
    elif ps_tmp_t == "中标金额":
        return ps[4].get_text()


if __name__ == "__main__":
    parse_outer_page()
    data_outer_dict = {
        '项目名称': name_list, '项目链接': link_list, '刊登日期': date_p_list
    }

    parse_inner_page()
    data_inner_dict = {
        '项目名称': name_list, '项目链接': link_list, '刊登日期': date_p_list, '项目招标人': t_name_list,
        '项目招标编号': t_num_list, '项目代理机构': t_depa_list, '工商注册号': BRN_list, '拟中标人': proposed_bidder,
        '中标价（费率）': w_price_list, '第二中标候选人': w_s_name_bidder_list, '第二中标价格': w_s_price_list,
        '第三中标候选人': w_t_name_bidder_list, '第三中标价格': w_t_price_list, '第一中标人': w_f_name_bidder_list
    }

    print(data_inner_dict)
    pd.DataFrame(data_outer_dict).to_csv(r'C:\Users\13754\Desktop\SpidersDemo(1).csv')
    pd.DataFrame(data_inner_dict).to_csv(r'C:\Users\13754\Desktop\SpidersDemo(3).csv')
