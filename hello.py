import os
import random
import time
import cv2
import numpy as np
import math

sign = False
start_x = 0
start_y = 0
end_x = 0
end_y = 0
distance = 0

font = cv2.FONT_HERSHEY_SIMPLEX  # 设置字体样式
kernel = np.ones((5, 5), np.uint8)  # 卷积核


def get_screenshot():
    # 截取手机的屏幕
    os.system('adb shell screencap -p /sdcard/01.png')
    # 图片传到电脑上
    os.system('adb pull /sdcard/01.png /Users/apple/Downloads/Cap')


def jump(distanceT):
    # 设置按压时间,系数为1.35
    press_time = int(distanceT * 2.45)

    # 生成随机手机屏幕模拟触摸点,防止成绩无效
    # 生成随机整数(0-9),最终数值为(0-90)
    rand = random.randint(0, 9) * 10

    # adb长按操作,即在手机屏幕上((320-410),(410-500))坐标处长按press_time毫秒
    cmd = ('adb shell input swipe %i %i %i %i ' + str(press_time)) % (320 + rand, 410 + rand, 320 + rand, 410 + rand)

    os.system(cmd)


def start(target):
    # 2.png作为模板图片，为脚部分。通过模板匹配，该函数返回脚坐标值
    template = cv2.imread("2.png")

    theight, twidth = template.shape[:2]

    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    return min_loc[0] + twidth // 2, min_loc[1] + theight // 2


def get_site(img):
    # 该函数功能是找到降落点中心位置并与脚坐标值计算求出两点间距离
    point_x = []
    point_y = []
    point = []
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([14, 40, 114])
    upper = np.array([58, 106, 255])
    imGray = cv2.inRange(hsv, lower, upper)
    cv2.imshow("1", imGray)
    ret, thresh = cv2.threshold(imGray, 100, 255, cv2.THRESH_BINARY)  # 127,255
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)  # contours为轮廓集，可以计算轮廓的长度、面积等
    for cnt in contours:

        if len(cnt) > 120:
            S1 = cv2.contourArea(cnt)
            ell = cv2.fitEllipse(cnt)
            S2 = math.pi * ell[1][0] * ell[1][1]
            if (S1 / S2) > 0.2:  # 面积比例，可以更改，根据数据集。。。0.2
                img = cv2.ellipse(img, ell, (0, 255, 0), 2)
                print(str(S1) + "    " + str(S2) + "   " + str(ell[0][0]) + "   " + str(ell[0][1]))
                point_x.append(int(ell[0][0]))
                point_y.append(int(ell[0][1]))
                point.append((int(ell[0][0]), int(ell[0][1])))
    distance111 = 0
    if len(point) == 2:
        start_point = start(refer)
        distance111 = ((start_point[0] - point[1][0]) ** 2 + (start_point[1] - point[1][1]) ** 2) ** 0.5  # 0.5
        cv2.line(img, (start_point[0], start_point[1]), (point[1][0], point[1][1]), (255, 0, 0), 2, 4)
    else:
        start_point = start(refer)
        print(point_x, point_y)
        if point_x:
            distance111 = ((start_point[0] - point_x[point_y.index(min(point_y))]) ** 2 + (
                        start_point[1] - min(point_y)) ** 2) ** 0.5
            cv2.line(img, (start_point[0], start_point[1]), (point_x[point_y.index(min(point_y))], min(point_y)),
                     (255, 0, 0), 2, 4)
        else:
            cv2.imwrite('error.png', img)

    print("distance" + str(distance111))
    cv2.imshow('img', img)
    jump(distance111)


if __name__ == "__main__":
    while True:
        start_time = time.time()
        get_screenshot()
        image = cv2.imread('/Users/apple/Downloads/Cap/01.png')
        image = cv2.resize(image, (500, 1020))
        refer = image.copy()
        get_site(image)
        time.sleep(2)
        if cv2.waitKey(20) & 0xFF == 27:
            break
