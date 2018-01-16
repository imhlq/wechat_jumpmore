import subprocess
import os
import random
import time
import cv2
import pickle
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

def recordScreen():
    cmd = '{} shell screenrecord /sdcard/demo.mp4'

def pullScreen(way=1):
    picname = 'jump_ss.png'
    command1 = '{} shell screencap -p /sdcard/{}'.format(adb_path, picname)
    command2 = '{} pull /sdcard/{} {}'.format(adb_path, picname, screen_path)
    shell(command1)
    time.sleep(0.01)
    shell(command2)
    return screen_path

def getCharacterPosition(pic):
    img = cv2.imread(pic)
    cimg = cv2.imread(character_path)
    csize = cimg.shape[:2]
    res = cv2.matchTemplate(img, cimg, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # cv2.rectangle(img,
    #               (min_loc[0], min_loc[1]),
    #               (min_loc[0] + csize[1], min_loc[1] + csize[0]),
    #               (255, 0, 0),
    #               4
    #               )
    # cv2.imwrite('jump_ok.png', img)
    return int(min_loc[0] + csize[1] / 2 + 3), int(min_loc[1] + csize[0] - 10), res


def getNextPosition(pic, **para):
    # get position of Next Center By openCV
    img = cv2.imread(pic)   # Read image from file
    img = cv2.GaussianBlur(img, (5, 5), 0)   # do GaussianBlur to decrease noise and extra boundary
    img_canny = cv2.Canny(img, 1, 10)   # Do canny
    # cv2.imwrite('jump_nn.png', img_canny)
    # Avoid the influence of character itself
    if para:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(para['para'])
        for k in range(min_loc[1] - 10, min_loc[1] + 159):
            for b in range(min_loc[0] - 10, min_loc[0] + 80):
                img_canny[k][b] = 0
    # Get Top(Good)
    y_top = np.nonzero([max(x[:-200]) for x in img_canny[600:]])[0][0] + 600
    x_top = int(np.mean(np.nonzero(img_canny[y_top][:-200])))
    # center
    nextPo = []
    for i in range(y_top+5, y_top + 350):
        if img_canny[i][x_top] != 0:
            nextPo.append(i)
    print(nextPo, len(nextPo))
    y_bottom = y_top + (nextPo[-1] - y_top) / 1.9

    if 4 < len(nextPo) < 11:
        # sp for long cylinder
        y_bottom = y_bottom - 30
        print('Long disk!')
    elif 100 < len(nextPo) < 150:
        y_bottom = y_bottom - 50
        print('O type')
    elif 13 < len(nextPo) < 22:
        y_bottom = y_bottom - 50
        print('drug')

    #     y_bottom = y_bottom - 70
    #     print('Long disk')
    # elif len(nextPo) < 4 and nextPo[-1] - nextPo[0] > 150:
    #     y_bottom = y_bottom + 25
    #     print('simple fix')
    # elif len(nextPo) < 4 and nextPo[-1] - nextPo[0] < 150:
    #     y_bottom = y_bottom - 20
    #     print('simple fix')
    # elif 15 < len(nextPo) < 23:
    #     y_bottom = y_bottom - 25
    #     print('drug')
    x_bottom = x_top
    x_center = int((x_top + x_bottom) / 2)
    y_center = int((y_top + y_bottom) / 2)
    # ==debug
    for yi in nextPo:
        cv2.circle(img_canny, (x_top, yi), 5, (255, 255, 0), 1)
    # cv2.rectangle(img_canny,
    #               (x_center - 10, y_center - 10),
    #               (x_center + 10, y_center + 10),
    #               (255, 0, 0),
    #               4
    #               )
    # cv2.imwrite('jump_nn_ok.png', img_canny)
    return x_center, y_center





def rndTouch():
    # Random noise to make it more human
    # generate click position
    x0 = 766 + random.random() * 50
    y0 = 1610 + random.random() * 50
    x1 = x0 + random.random() * 50
    y1 = y0 + random.random() * 50
    time = int(random.random() * 2)
    # generate command
    command = '{} shell input swipe {} {} {} {} {}'.format(adb_path, x0, y0, x1, y1, time)
    shell(command)
    return 1


def oneJump(time):
    # generate click position
    x0 = 766 + random.random() * 20
    y0 = 1610 + random.random() * 2
    x1 = x0 + random.random() * 3
    y1 = y0 + random.random() * 3
    # generate command
    command = '{} shell input swipe {} {} {} {} {}'.format(adb_path, x0, y0, x1, y1, time)
    shell(command)
    return 1


def calcTime(distance, factor=1.346, rnd=0):
    # Calculate press time from distance, rnd < 20
    t = distance * factor
    t = int(t + np.random.normal(scale=rnd))
    t = max(t, 250)
    print('Distance: %.1f, ExpectTime:%d ms' % (distance, t))
    return t


def loop():
    pos1 = getCharacterPosition(screen_path)
    pos2 = getNextPosition(screen_path, para=pos1[2])
    # calc distance, consider angle
    rx = abs(pos1[0] - pos2[0])
    ry = abs(pos1[1] - pos2[1])
    dis = rx ** 2 + ry ** 2
    dis = dis ** 0.5
    dis *= np.cos(np.arctan(rx / ry) - 1.0472)
    t = calcTime(dis, rnd=15)
    oneJump(t)
    # fake
    # if random.random() < 0.2:
    #     rndTouch()


def auto_play(gameround=100):
    for i in range(gameround):
        pullScreen()
        # if over?
        img = cv2.imread(screen_path)
        endlogo = cv2.imread(end_path)
        res_end = cv2.matchTemplate(img, endlogo, cv2.TM_CCOEFF_NORMED)
        cimg = cv2.imread(character_path)
        res_end2 = cv2.matchTemplate(img, cimg, cv2.TM_SQDIFF)
        if cv2.minMaxLoc(res_end)[1] > 0.90:
            print('Game Over')
            break
        elif cv2.minMaxLoc(res_end2)[0] < 0.1:
            print('Cannot find character, wait')
            break
        loop()
        print('\n== Loop %d Over ==\n' % i)
        time.sleep(1+random.random())
    print('Program over')


def createmldata():
    data = []
    while True:
        pullScreen()
        p1 = getCharacterPosition(screen_path)

        img = cv2.imread(screen_path)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        img_canny = cv2.Canny(img, 1, 10)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(p1[2])
        for k in range(min_loc[1] - 10, min_loc[1] + 159):
            for b in range(min_loc[0] - 10, min_loc[0] + 80):
                img_canny[k][b] = 0

        y_top = np.nonzero([max(x[:-200]) for x in img_canny[600:]])[0][0] + 600
        x_top = int(np.mean(np.nonzero(img_canny[y_top][:-200])))

        nextblock = []
        for yi in range(y_top-10, y_top+230):
            nextblock.append(np.copy(img_canny[yi, x_top - 120: x_top + 120]))

        nextPo = []
        for i in range(y_top + 5, y_top + 350):
            if img_canny[i][x_top] != 0:
                nextPo.append(i)

        y_bottom = y_top + (nextPo[-1] - y_top) / 1.9
        x_bottom = x_top
        x_center = int((x_top + x_bottom) / 2)
        y_center = int((y_top + y_bottom) / 2)

        cv2.rectangle(img_canny,
                      (x_center - 10, y_center - 10),
                      (x_center + 10, y_center + 10),
                      (255, 0, 0),
                      4
                      )

        nextblockimg = np.array(nextblock, np.int32)
        cv2.imwrite('jump_ml.png', img_canny)

        err = int(input('Please Input Position Error: '))
        if err == 404:
            exit()
        acc = y_center - y_top - err

        data.append((nextblockimg, acc))
        # save
        fr = open('data.ml', 'wb')
        pickle.dump(data, fr)
        fr.close()
        print('Ok!')
        loop()
        time.sleep(2)

def test():
    p1 = getCharacterPosition(screen_path)
    getNextPosition(screen_path, para=p1[2])


auto_play(200)