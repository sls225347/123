# -*- coding:utf8 -*-
import requests
import lxml
from bs4 import BeautifulSoup
import xlwt
import time 

cookie = """
UM_distinctid=166c7ce64464ce-00cbe158a3bc6f-8383268-1fa400-166c7ce64475ee; zg_did=%7B%22did%22%3A%20%22166c7ce6450176-0bacbefa7b5155-8383268-1fa400-166c7ce645138e%22%7D; _uab_collina=154095048420374760935281; acw_tc=73df0f9515409505015312459ed6da3f615411901d16a6ac66073445ed; QCCSESSID=ms5375jpfupombta3jmdlihfh6; CNZZDATA1254842228=394994080-1540948505-https%253A%252F%252Fmy.oschina.net%252F%7C1541238855; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201541384519729%2C%22updated%22%3A%201541384519731%2C%22info%22%3A%201540950484055%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%229b94d31c8aca4363be7daace79e602a7%22%7D; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1541123037,1541135672,1541220117,1541384520; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1541384520
"""
def craw(url):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Cookie': cookie.replace('\n', '').replace(' ', '')
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        response.encoding = 'utf-8'
        print(response.status_code)
        print('ERROR')
    soup = BeautifulSoup(response.text, 'lxml')
    com_names = soup.find_all(class_='ma_h1')
    com_detail = soup.find_all(class_='m-t-xs')
    com_detail_tuple = []
    step = 3
    for i in range(0, len(com_detail), step):
        com_detail_tuple.append(com_detail[i: i+step])
    for i in range(0, len(com_names)):
        com_name_list.append(com_names[i].get_text())
        peo_money_time, email_phone, address = com_detail_tuple[i]
        peo_name = peo_money_time.find_all(class_='text-primary')
        if peo_name:
            peo_name = peo_name[0].get_text()
        else:
            peo_name = ""
        peo_name_list.append(peo_name)

        zhuceziben, chenglishijian = peo_money_time.find_all(class_='m-l')
        zhuceziben_list.append(zhuceziben.get_text())
        chenglishijian_list.append(chenglishijian.get_text())

        phone = email_phone.find_all(class_='m-l')
        if phone:
            phone = phone[0].get_text()
        else:
            phone = ""
        peo_phone_list.append(phone)
        com_place_list.append(address.get_text().replace("\n", "").replace(" ", ""))

if __name__ == '__main__':
    com_name_list = []
    peo_name_list = []
    peo_phone_list = []
    zhuceziben_list = []
    chenglishijian_list = []
    com_place_list = []
    #$key_word = input('请输入您想搜索的关键词：')
    key_word = "重庆乔亚音乐"
    for x in range(1, 11):
        time.sleep(1)
        print("wait 1 s")
        url = 'https://www.qichacha.com/search_index?key={}&ajaxflag=1&p={}&'.format(key_word, x)
        craw(url)
    workbook = xlwt.Workbook(encoding="UTF-8")
    # 创建sheet对象，新建sheet
    sheet1 = workbook.add_sheet('xlwt', cell_overwrite_ok=True)
    # ---设置excel样式---
    # 初始化样式
    style = xlwt.XFStyle()
    # 创建字体样式
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.bold = True  # 加粗
    # 设置字体
    style.font = font
    # 使用样式写入数据
    # sheet.write(0, 1, "xxxxx", style)
    # 向sheet中写入数据
    name_list = ['公司名字', '法定代表人', '联系方式', '注册人资本', '成立时间', '公司地址']
    for cc in range(0, len(name_list)):
        sheet1.write(0, cc, name_list[cc], style)
    
    for i in range(0, len(com_name_list)):
        sheet1.write(i + 1, 0, com_name_list[i], style)  # 公司名字
        sheet1.write(i + 1, 1, peo_name_list[i], style)  # 法定代表人
        sheet1.write(i + 1, 2, peo_phone_list[i], style)  # 联系方式
        sheet1.write(i + 1, 3, zhuceziben_list[i], style)  # 注册人资本
        sheet1.write(i + 1, 4, chenglishijian_list[i], style)  # 成立时间
        sheet1.write(i + 1, 5, com_place_list[i], style)  # 公司地址
        # print com_name_list[i], peo_name_list[i], peo_phone_list[i], zhuceziben_list[i], chenglishijian_list[i], com_place_list[i]
    # 保存excel文件，有同名的直接覆盖
    workbook.save(r'D:\papapa\data12.xls')
    print('the excel save success')