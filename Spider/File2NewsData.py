# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/19 20:20
# @Author : 寒露
# @File : .py

import re

# 读取链接存储文件
with open("ttnews_sports_links.txt", "r", encoding="utf8") as fo:
    links = [link.strip() for link in fo]
print(len(links))  # 原链接数
print(links)
bad_words = []  # 应去除的链接所包含的字符串pattern
bad_words.append(re.compile(r'www.ixigua'))
bad_words.append(re.compile(r'c/user'))
real_news = re.compile(r'www.toutiao.com/group/')  # 可用新闻链接所包含的字符串pattern
news_links = []  # 可用新闻链接
# 遍历链接list筛选可用新闻链接
for link in links:
    if real_news.search(link):
        news_links.append(link)
print(len(news_links))  # 可用新闻链接数
print(news_links)
# 将可用新闻链接写入文件存储
with open("ttnews_sports_links.txt", "w", encoding="utf8") as fw:
    for link in news_links:
        fw.write(link + "\n")
    fw.write("体育新闻链接数：" + str(len(news_links)))
fw.close()


