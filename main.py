#!/usr/bin/env python
# coding: utf-8

from bottle import get, post, request, static_file, template, run
from datahelper import postImgs, listdatenums, getcurrentdatenum
from pvhelper import pv_inc, get_pv, get_pvline


###############################################################
#获取各个静态资源文件文件
###############################################################
#获取favicon.ico
@get('/favicon.ico')
def GetFavicon():
    return static_file('favicon.ico', root='.')


#robots.txt
@get('/robots.txt')
def GetRobots():
    return static_file('robots.txt', root='.')


#背景音乐（获取多首背景音乐，随机播放其中一首）
@get('/bgmusic.mp3')
def GetMp3():
    # bgmusics = ['guantade', 'zhuimengchizixin']
    # current_music = random.randint(0, 1)
    # return static_file(bgmusics[current_music]+'.mp3', root='data')
    return static_file('xuqirongyao20170817.mp3', root='data')


#获取各个img文件
@get('/img/head/<imgName>')
def GetHeadImage(imgName):
    return static_file(imgName, root='img/head')


@get('/img/contents/<imgName>')
def GetImage(imgName):
    imgdir = imgName.split('_')
    return static_file(imgdir[1], root='img/contents/'+imgdir[0])


#获取各个pic文件
@get('/pic/<picName>')
def GetPic(picName):
    return static_file(picName, root='pic')


#获取各个js文件
@get('/js/<jsName>')
def GetJs(jsName):
    return static_file(jsName, root='js')


#获取各个css文件
@get('/css/<cssName>')
def GetCss(cssName):
    return static_file(cssName, root='css')


#错误页面定义
@get('/error')
def raiseError():
    return static_file('error404.jpg', 'img')


###############################################################
#默认获取首页
###############################################################
@get('/')
@get('/index')
def GetIndex():
    pv_inc()
    datenums = listdatenums(7)
    mydatenum = getcurrentdatenum()
    return template('index', datenumLst=datenums, datenum=mydatenum)


###############################################################
#获取view中的内容
###############################################################
# 主页今天
@get('/homeToday')
def GetHomeToday():
    datenums = listdatenums(7)
    mydatenum = getcurrentdatenum()
    return template('home', datenumLst=datenums, datenum=mydatenum)


# 主页往期历史数据
@get('/homeHistory')
def GetHomeHistory():
    datenums = listdatenums(7)
    mydatenum = request.query.get('datenum', '')
    return template('homehistory', datenumLst=datenums, datenum=mydatenum)


@get('/contentPic')
def GetContentPic():
    my_img = request.query.get('myImg', '')
    return template('contentPic', myImg=my_img)


###############################################################
#上传与下载文件相关
###############################################################
#登陆页面
@get('/login')
def Login():
    return template('login')


#验证密码是否正确
@post('/validpwd')
def validPwd():
    pwd = request.POST.get('pwd')
    print('-----------------------------------------------------'+pwd)
    if pwd == '123321':
        return template('uploadpic')
    else:
        return 'err'


#上传文件OK
@post('/uploadok/<imgName>')
def PostUploadOK(imgName):
    imgFile = request.files.get('file')
    result = postImgs(imgName, imgFile)
    return result


#下载数据
@get('/download/<fileName>')
def download(fileName):
    return static_file(fileName, root='data', download=fileName)


#获取网站访问量
@post('/getpv')
def getPV():
    pwd = request.POST.get('pwd')
    print('-----------------------------------------------------'+pwd)
    if pwd == '123321':
        return get_pv()
    else:
        return 'err'


#历史网站访问量曲线页面
@get('/pvline/<lineType>')
def PVLine(lineType):
    return get_pvline(lineType)


###############################################################
#启动服务器
###############################################################
if __name__ == "__main__":
    # Interactive mode
    run(host='0.0.0.0', port=80, debug=True, reloader=False)
