# coding: utf-8

import os
import datetime

#程序当前运行的目录
currentdir = os.getcwd()


# 返回当前日期字符串（eg.20170302）
def getcurrentdatenum():
    return datetime.date.today().strftime('%Y%m%d')


# 上传图片文件相关---------------------------------------------------------------------
# 往期历史数据
def listdatenums(num):
    imgpath = os.path.join(currentdir, "img", "contents")
    datenums = os.listdir(imgpath)
    datenums.sort()
    datenums.reverse()

    return datenums[0:num]


# 处理上传的文件
def postImgs(imgName, imgFile):
    #方案和报表等可下载文件保存的路径
    dataDir = os.path.join(currentdir, "data")
    #headImage保存的路径
    headDir = os.path.join(currentdir, "img", "head")
    # 获取当天的年月日字符串
    currentdate = datetime.date.today().strftime('%Y%m%d')
    #contentImage保存的路径
    contentDir = os.path.join(currentdir, "img", "contents", currentdate)
    #如果当天的文件夹不存在，就创建一个
    if not os.path.exists(contentDir):
        os.mkdir(contentDir)

    #下划线分割
    imgNames = imgName.split('_')

    if imgNames[0] == 'head':
        hpath = os.path.join(headDir, imgNames[1] + ".jpg")
        imgFile.save(hpath, overwrite=True)
        return "上传滚动图片成功！"
    elif imgNames[0] == 'content':
        cpath = os.path.join(contentDir, imgNames[1] + ".jpg")
        imgFile.save(cpath, overwrite=True)
        return "上传内容图片成功！"
    elif imgNames[0] == 'logo':
        cpath = os.path.join(headDir, imgName + ".jpg")
        imgFile.save(cpath, overwrite=True)
        return "上传logo图片成功！"
    elif imgNames[0] == 'schema':
        cpath = os.path.join(dataDir, "schema.pdf")
        imgFile.save(cpath, overwrite=True)
        return "上传方案pdf文件成功！"
    elif imgNames[0] == 'report':
        cpath = os.path.join(dataDir, "report.xlsx")
        imgFile.save(cpath, overwrite=True)
        return "上传继续率报表成功！"
    else:
        print('upload content image %s fail!' % imgName)
        return "上传失败，请重试！"
