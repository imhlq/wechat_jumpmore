import os
import random
import time
import cv2

import numpy as np

# Environment Parameters
adb_path = 'D:/Phone/platform-tools/adb.exe'
screen_path = './jump_ss.png'
character_path = './character.png'
end_path = './end.png'


def shell(cmd):
    print('-> %s' % cmd)
    os.system(cmd)
    return 1


def pullScreen(way=1):
    picname = 'jump_ss.png'
    command1 = '{} shell screencap -p /sdcard/{}'.format(adb_path, picname)
    command2 = '{} pull /sdcard/{} {}'.format(adb_path, picname, screen_path)
    shell(command1)
    time.sleep(0.01)
    shell(command2)
    return screen_path


def getDistance(pic):
    # get position of Next Center By openCV
    img = cv2.imread(pic)  # Read image from file

    # Get position of character
    cimg = cv2.imread(character_path)
    csize = cimg.shape[:2]
    res = cv2.matchTemplate(img, cimg, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    cx = int(min_loc[0] + csize[1] / 2 + 3)
    cy = int(min_loc[1] + csize[0] - 10)

    # then
    img = cv2.GaussianBlur(img, (5, 5), 0)  # do GaussianBlur to decrease noise and extra boundary
    img_canny = cv2.Canny(img, 1, 10)  # Do canny

    # Avoid the influence of character itself
    for k in range(min_loc[1] - 10, min_loc[1] + 159):
        for b in range(min_loc[0] - 10, min_loc[0] + 80):
            img_canny[k][b] = 0

    # Get Top(Good)
    y_top = np.nonzero([max(x[:-200]) for x in img_canny[600:]])[0][0] + 600
    x_top = int(np.mean(np.nonzero(img_canny[y_top][:-200])))


    # with angle 30 deg
    dx = int(abs(x_top - cx))
    dy = int(dx * 0.5772)
    if cx < 550:
        x_c = cx + dx
    else:
        x_c = cx - dx
    y_c = cy - dy

    d_c = int((dx**2 + dy**2)**0.5)

    cv2.circle(img, (cx, cy), 10, (255, 0, 0), 3)
    cv2.circle(img, (x_c, y_c), 10, (255, 255, 0), 3)
    cv2.imwrite('new.png', img)

    return d_c


def oneJump(time):
    # generate click position
    x0 = 766 + random.random() * 20
    y0 = 1610 + random.random() * 2
    x1 = x0 + random.random() * 2
    y1 = y0 + random.random() * 2
    # generate command
    command = '{} shell input swipe {} {} {} {} {}'.format(adb_path, x0, y0, x1, y1, time)
    shell(command)
    return 1


def calcTime(distance, factor=1.37, rnd=0):
    # Calculate press time from distance, rnd < 20
    t = distance * factor
    t = int(t + np.random.normal(scale=rnd))
    t = max(t, 250)
    print('Distance: %.1f, ExpectTime:%d ms' % (distance, t))
    return t


def loop(rnd):
    pullScreen()
    # if over?
    img = cv2.imread(screen_path)
    endlogo = cv2.imread(end_path)
    res_end = cv2.matchTemplate(img, endlogo, cv2.TM_CCOEFF_NORMED)
    cimg = cv2.imread(character_path)
    res_end2 = cv2.matchTemplate(img, cimg, cv2.TM_SQDIFF)
    if cv2.minMaxLoc(res_end)[1] > 0.90:
        print('Game Over')
        return -1
    elif cv2.minMaxLoc(res_end2)[0] < 0.1:
        print('Cannot find character')
        return -1
    dis = getDistance(screen_path)
    t = calcTime(dis, rnd=rnd)
    oneJump(t)
    return 1


def auto_play(around, rnd):
    for i in range(around):
        res = loop(rnd)
        if res == 1:
            print('Good Turn')
            time.sleep(1 + random.random())
        else:
            print('Something wrong, exit')
            break


auto_play(100, 2)