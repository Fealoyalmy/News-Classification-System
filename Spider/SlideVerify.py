# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/22 22:59
# @Author : 寒露
# @File : .py

import cv2
import requests
from selenium.webdriver import Chrome, ActionChains
import random
import time


class SlideVerify:
    # 显示或保存图片
    @staticmethod
    def cv_show(name, img, save=False):
        if save:
            cv2.imwrite(name, img)
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # 获取滑块的大小
    @staticmethod
    def fix_img(filename):
        #  1.为了更高的准确率，使用二值图像
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 滑块图BGR转灰度
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # 2.将轮廓提取出来
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnt = contours[0]
        # 3.用绿色(0, 255, 0)来画出最小的矩形框架
        x, y, w, h = cv2.boundingRect(cnt)
        rect_x = x + w
        rect_y = y + h
        # print(x, y, rect_x, rect_y)  # x，y是矩阵左上点的坐标，w，h是矩阵的宽和高
        img = cv2.rectangle(img, (x, y), (rect_x, rect_y), (0, 255, 0), 1)
        # SlideVerify.cv_show('img.png', img, True)  # 用绿色线框画出滑块的大小
        # 高度和宽度
        mixintu = img[y:rect_y, x:rect_x]
        # SlideVerify.cv_show("mixintu.png", mixintu, True)  # 裁剪出滑块的区域
        return mixintu

    @staticmethod
    def get_distance(img_tp, img_bg):
        # 1.对滑块进行图片处理
        tp_img = SlideVerify.fix_img(img_tp)  # 裁掉透明部分，找出滑块的大小
        tp_edge = cv2.Canny(tp_img, 100, 200)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2BGR)
        # SlideVerify.cv_show("TTVerifyImg/1.jpg", tp_edge, True)  # 打印滑块的灰度转BGR图
        # 2.对背景进行图片处理
        bg_img = cv2.imread(img_bg)
        bg_edge = cv2.Canny(bg_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2BGR)
        # SlideVerify.cv_show("TTVerifyImg/2.jpg", bg_pic, True)  # 打印背景图灰度图
        # 3.模板匹配matchTemplate
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print(min_val, max_val, min_loc, max_loc)  # 最小值，最大值，最小值的位置，最大值的位置
        # 绘制方框方便查看
        X = max_loc[0]
        th, tw = tp_pic.shape[:2]
        t1 = max_loc  # 左上角点的位置
        br = (t1[0] + tw, t1[1] + th)  # 右下角点的坐标
        cv2.rectangle(bg_img, t1, br, (0, 0, 225), 2)  # 绘制矩形
        # SlideVerify.cv_show('TTVerifyImg/out.jpg', bg_img, True)
        print(t1, br)
        return t1, br

    @staticmethod
    def get_track(img_tp, img_bg):
        distance = SlideVerify.get_distance(img_tp, img_bg)[0][0]
        print(distance)
        v = 0  # 初速度
        t = 0.3  # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        tracks = []  # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        current = 0  # 当前的位移
        mid = distance * 5 / 8  # 到达mid值开始减速
        # distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:  # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(1, 3)  # 加速运动
            else:
                a = -random.randint(2, 4)  # 减速运动
            v0 = v  # 初速度
            s = v0 * t + 0.5 * a * (t ** 2)  # 0.2秒时间内的位移
            current += s  # 当前的位置
            tracks.append(round(s))  # 添加到轨迹列表
            v = v0 + a * t  # 速度已经达到v,该速度作为下次的初速度
        for i in range(4):  # 反着滑动到大概准确位置
            tracks.append(-random.randint(1, 3))
        random.shuffle(tracks)
        print(tracks)
        # return tracks
        return distance

    @staticmethod
    def movd_tp(tracks, driver):
          # 获取鼠标轨迹
        slider = driver.find_element_by_xpath('//*[@id="captcha_container"]/div/div[2]/img[2]')  # 找到滑块
        ActionChains(driver).click_and_hold(slider).perform()  # 鼠标点击滑块并按住不松
        # ActionChains(driver).move_by_offset(xoffset=0, yoffset=100).perform()  # 让鼠标随机往下移动一段距离
        time.sleep(0.15)
        # for item in tracks:
        #     ActionChains(driver).move_by_offset(xoffset=item, yoffset=random.randint(-2, 2)).perform()
        ActionChains(driver).move_by_offset(xoffset=tracks*0.75, yoffset=random.randint(-2, 2)).perform()
        time.sleep(0.3)  # 稳定0.3秒再松开
        ActionChains(driver).release(slider).perform()
        time.sleep(0.3)
        # 随机拿开鼠标
        # ActionChains(driver).move_by_offset(xoffset=random.randint(200, 300), yoffset=random.randint(200, 300)).perform()
        # time.sleep(0.2)
        # info = driver.find_element_by_xpath(
        #     '//*[@id="login-modal"]/div/div/div/div[2]/div[1]/div[2]/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/span[1]')
        # if '验证通过' in info.text:
        #     return 1
        # if '验证失败' in info.text:
        #     return 2
        # if '再来一次' in info.text:
        #     return 3
        # if '出现错误' in info.text:
        #     return 4

    @staticmethod
    def ttnews_vrf(driver):
        img_bg_url = driver.find_element_by_id("captcha-verify-image").get_attribute("src")  # 找到背景图url
        img_tp_url = driver.find_element_by_class_name(  # 找到滑块小图url
            "captcha_verify_img_slide, react-draggable, sc-VigVT, ggNWOG").get_attribute("src")
        img_bg = requests.get(img_bg_url)  # 进入图片网址下载图片
        with open('TTVerifyImg/bg.jpg', 'wb') as f:
            f.write(img_bg.content)  # 保存图片
            f.close()
        img_tp = requests.get(img_tp_url)
        with open('TTVerifyImg/tp.png', 'wb') as f:
            f.write(img_tp.content)
            f.close()
        tracks = SlideVerify.get_track('TTVerifyImg/tp.png', 'TTVerifyImg/bg.jpg')  # 对图片进行匹配识别得到鼠标拖动路径
        SlideVerify.movd_tp(tracks, driver)  # 控制鼠标执行拖动操作
        return tracks


if __name__ == '__main__':
    # cors = SlideVerify.get_distance('TTVerifyImg/0xt.png', 'TTVerifyImg/0dt.jpg')
    tracks = SlideVerify.get_track('TTVerifyImg/9xt.png', 'TTVerifyImg/9dt.jpg')
    # SlideVerify.movd_tp(tracks, driver)

