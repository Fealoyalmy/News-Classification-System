# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/18 22:32
# @Author : 寒露
# @File : .py

import re
from urllib import request

import requests
import urllib
from urllib.error import URLError
import urllib3
import gzip
from io import StringIO
from Spider.SlideVerify import SlideVerify
from selenium import webdriver
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random
import pandas as pd
# import xlsxwriter

# 配置option初始化driver
from tqdm import tqdm


def init_driver():
    option = webdriver.ChromeOptions()
    # option.add_argument("--headless")
    # 无头浏览器需要添加user-agent来隐藏特征
    option.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')
    option.binary_location = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    chrome_driver_location = r'D:\ChromeDriver\98.0.4758.102\chromedriver'
    # 1.定义浏览器
    driver = webdriver.Chrome(chrome_driver_location, options=option)
    driver.implicitly_wait(5)
    with open('stealth.min.js') as f:
        js = f.read()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
      "source": js
    })
    driver.set_window_size(600, 800)
    return driver


def web_redirect(driver):
    """
    浏览器弹出新窗口后，selenium绑定新窗口
    :param driver: 传入driver
    :return: 无（driver移动至新开网页上）
    """
    windows = driver.current_window_handle  # 定位当前页面句柄
    all_handles = driver.window_handles  # 获取全部页面句柄
    for handle in all_handles:  # 遍历全部页面句柄
        if handle != windows:  # 判断条件
            driver.switch_to.window(handle)  # 切换到新页面
    print(all_handles)
    driver.switch_to.window(handle)


def ttnews_spider(news_label, news_links_path, driver, steps):
    """
    爬取头条新闻链接存txt文件
    :param news_label: 需要爬取的新闻分类
    :param news_links_path: 存储路径
    :param driver: 传入driver
    :param steps: 网页下划次数
    :return: 无（生成存有新闻链接的txt文件）
    """
    driver.get('https://www.toutiao.com/')  # 输入网址
    driver.implicitly_wait(5)
    more_list = driver.find_element_by_class_name('more-btn')  # 点击更多按钮
    more_list.click()
    items = driver.find_elements_by_class_name("feed-more-nav-item") + \
            driver.find_elements_by_class_name("feed-default-nav-item")  # 查找更多列表中的新闻栏目标签
    for item in items:  # 点击进入新闻栏目
        if item.text == news_label:
            item.click()
            news_links = []
            n = 0
            with open(news_links_path, "w", encoding="utf8") as fw:
                for i in range(steps):
                    js = "window.scrollBy(0,3000);"
                    driver.execute_script(js)
                    news_list = driver.find_element_by_class_name("ttp-feed-module").find_elements_by_class_name("feed-card-article-wrapper")
                    if i % 5 == 0:
                        print("%d：" % i, len(news_list))
                    while i > 5 and n < len(news_list):
                        news = news_list[n].find_element_by_class_name("feed-card-article-l").find_element_by_tag_name(
                            "a")
                        link = news.get_attribute("href")
                        title = news.get_attribute("aria-label")
                        news_links.append(link)
                        fw.write(link.strip() + "_!_" + title.strip() + "\n")
                        fw.flush()
                        n += 1
                    time.sleep(1)
            print("新闻链接数：", len(news_links))
            fw.close()


def txnews_spider(news_label, news_links_path, driver, steps):
    """
    爬取腾讯新闻链接存txt文件
    :param news_label: 需要爬取的新闻分类
    :param news_links_path: 存储路径
    :param driver: 传入driver
    :param steps: 网页下划次数
    :return: 无（生成存有新闻链接的txt文件）
    """
    driver.get('https://news.qq.com/')  # 输入网址
    more_list = driver.find_element_by_class_name('more-icon')  # 点击更多按钮
    more_list.click()
    items = driver.find_elements_by_class_name("item")
    for item in items:
        if item.text == news_label:  # 进入对应标签新闻栏目
            item.click()
            news_links = []
            n = 0
            with open(news_links_path, "w", encoding="utf8") as fw:
                for i in range(steps):
                    js = "window.scrollBy(0,3000);"
                    driver.execute_script(js)
                    news_list = driver.find_elements_by_class_name("item-pics,cf,item-ls")
                    if i % 5 == 0:
                        print("%d：" % i, len(news_list))
                    while i > 5 and n < len(news_list):
                        news = news_list[n].find_element_by_tag_name("a")
                        link = news.get_attribute("href")
                        title = news_list[n].find_element_by_tag_name("h3").text
                        news_links.append(link)
                        fw.write(link.strip() + "_!_" + title.strip() + "\n")
                        fw.flush()
                        n += 1
                    time.sleep(1)
            print("新闻链接数：", len(news_links))
            fw.close()


def get_ttnews_label(news_url, driver, n):
    """
    获取该条新闻网页js代码中的label数据
    :param news_url: 该条新闻链接
    :param driver: 传入driver
    :return: 该条新闻label
    """
    try:
        driver.get(news_url)  # 输入网址
        driver.implicitly_wait(5)
        js_label = driver.find_element_by_id("RENDER_DATA").get_attribute('innerText')
        label = re.findall(r'\d(news_.*?)%', js_label)[0]
        print("该条新闻label=", label)
        return label
    except:
        print("第%d条新闻无label!" % n)
        return False


def spider(news_links_path, driver, steps):
    """
    爬取头条新闻链接存txt文件
    :param news_links_path: 存储路径
    :param driver: 传入driver
    :param steps: 网页下划次数
    :return: 无（生成存有新闻链接的txt文件）
    """
    news_driver = init_driver()
    driver.get('https://www.toutiao.com/')  # 输入网址
    driver.implicitly_wait(5)
    news_links = []
    n = 5
    with open(news_links_path, "w", encoding="utf8") as fw:
        for i in range(steps):
            js = "window.scrollBy(0,3000);"
            driver.execute_script(js)
            news_list = driver.find_element_by_class_name("ttp-feed-module").find_elements_by_class_name("feed-card-article-wrapper")
            if i % 5 == 0:
                print("%d：" % i, len(news_list))
            while i > 5 and n < len(news_list):
                news = news_list[n].find_element_by_class_name("feed-card-article-l").find_element_by_tag_name(
                    "a")
                link = news.get_attribute("href")
                title = news.get_attribute("aria-label")
                news_links.append(link)
                news_driver.get(link)
                label = get_ttnews_label(link, news_driver, n)
                if label:
                    fw.write(label + "_!_" + link.strip() + "_!_" + title.strip() + "\n")
                    fw.flush()
                n += 1
            time.sleep(1)
    print("新闻链接数：", len(news_links))
    fw.close()


def get_news_content():
    driver = init_driver()
    # with open("id_label_title.txt", "r", encoding="utf8") as fo:
    with open("data_set/ttnews_travel_links.txt", "r", encoding="utf8") as fo:
        all_lines = fo.readlines()  # 读所有行
        file = open('data_set/news_travel.txt', 'a', encoding="utf8")
        for line in tqdm(all_lines[135:]):  # 按每行新闻加载进度条   [4472:]
            # news_id, label, title, data = line.strip().split("_|_")
            news_url, title = line.strip().split("_!_")
            try:
                # news_url = "https://www.toutiao.com/group/" + news_id  # 组合每条新闻的url
                driver.get(news_url)  # 进入网址
                # error_title = re.compile(r'问题不存在')  # 设置标题为“问题不存在”的pattern
                # head_title = driver.find_element_by_tag_name("head").find_element_by_tag_name("title").get_attribute("innerText")  # 获取新闻网页标题文本
                # body_type = driver.find_element_by_tag_name("body").get_attribute("data-log-from")  # 获取新闻网页代码body中的元素
                # 如果出现 404错误页/问题不存在页面/头条问答 等情况时特殊写入
                """
                if head_title == "404错误页":
                    file.write("404Error_|_" + label + "404_|_" + title + "_|_\n")
                    file.flush()
                    continue
                elif error_title.search(head_title):
                    file.write("NoneError_|_" + label + "404_|_" + title + "_|_\n")
                    file.flush()
                    continue
                elif body_type == "Question":
                    file.write("QuestionError_|_" + label + "404_|_" + title + "_|_\n")
                    file.flush()
                    continue
                # driver.implicitly_wait(5)
                try:
                    SlideVerify.ttnews_vrf(driver)
                    print(label, title, news_id, "滑动验证成功！")
                except:
                    print("无需验证！")
                """
                article = driver.find_element_by_class_name("syl-article-base, tt-article-content, syl-page-article, syl-device-pc")
                datas = article.find_elements_by_tag_name("p")  # 获取所有正文内容p元素
                # print(label, title, "段数：", len(datas))
                print(title, "段数：", len(datas))
                content = ""
                for data in datas:  # 写入正文内容
                    content += data.text.strip() + " "
                file.write(news_url + "_|_" + title + "_|_" + content + "\n")
                file.flush()
                # print(content)
            except:
                pass
                # file.write("010Error" + "_|_" + title + "_|_\n")
                # file.flush()
    file.close()


# 类别序列
# category_lists = ["news_story", "news_culture", "news_entertainment", "news_sports", "news_finance", "news_house",
#                       "news_car", "news_edu", "news_tech", "news_military", "news_travel", "news_world", "stock",
#                       "news_agriculture", "news_game"]

# driver = init_driver()
# ttnews_spider("历史", "ttnews_history_links.txt", driver, 5000)
# txnews_spider("汽车", "txnews_car_links.txt", driver, 5000)
# spider("ttnews_links.txt", driver, 5000)

# get_news_content()


def test():
    driver = init_driver()
    i = 0
    with open("id_label_title.txt", "r", encoding="utf8") as fo:
        all_lines = fo.readlines()  # 读所有行
    for line in all_lines:
        print(i)
        try:
            news_id, label, title, data = line.strip().split("_|_")
            driver.get("https://www.toutiao.com/group/" + news_id)
            # if driver.find_element_by_id("captcha-verify-image"):
            #     dis = SlideVerify.ttnews_vrf(driver)
            #     slider = driver.find_element_by_xpath('//*[@id="captcha_container"]/div/div[2]/img[2]')  # 找到滑块
            #     ActionChains(driver).click_and_hold(slider).perform()  # 鼠标点击滑块并按住不松
            #     # ActionChains(driver).move_by_offset(xoffset=0, yoffset=100).perform()  # 让鼠标随机往下移动一段距离
            #     # time.sleep(0.3)
            #     # for item in tracks:
            #     #     ActionChains(driver).move_by_offset(xoffset=item, yoffset=random.randint(-2, 2)).perform()
            #     ActionChains(driver).move_by_offset(xoffset=dis, yoffset=random.randint(-2, 2)).perform()
            #     # time.sleep(0.3)  # 稳定0.3秒再松开
            #     ActionChains(driver).release(slider).perform()
            i += 1
        except:
            i += 1
            continue


# test()


# url = 'https://www.toutiao.com/'
# proxy = {'http': '124.239.216.14:2060', 'https': '124.239.216.14:2060'}
# proxies = request.ProxyHandler(proxy)  # 创建代理处理器
# opener = request.build_opener(proxies)  # 创建opener对象
# resp = opener.open(url).read().decode("utf-8")
# print(resp)

# data = {'abc': '123'}
# proxy = urllib3.ProxyManager('http://50.233.137.33:80', headers={'connection': 'keep-alive'})
# resp1 = proxy.request('POST', 'https://www.toutiao.com/', fields=data)
# print(resp1.data.decode())

if __name__ == "__main__":
    get_news_content()




