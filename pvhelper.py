# coding: utf-8

import os
import datetime
import time
from plotly import tools, offline, graph_objs as go
import json

#程序当前运行的目录
currentdir = os.getcwd()

# 返回当前日期字符串（eg.20170302）
def getcurrentdatenum():
    return datetime.date.today().strftime('%Y%m%d')

#记录网站访问量-----------------------------------------------------------------------
#方案和报表等可下载文件保存的路径
pvtodayfile = os.path.join(currentdir, 'data', 'pvtoday.txt')
pvhistoryfile = os.path.join(currentdir, 'data', 'pvhistory.txt')


#返回统计信息
def get_pv():
    pv = {}

    pvtoday = read_today_pvcount()
    pv["pvToday"] = pvtoday

    pvall = read_pvhistory()
    # print(pvtoday)
    # print(pvall)
    pv["pvAll"] = pvtoday
    pv["pvWeek"] = pvtoday
    pv["pvMonth"] = pvtoday
    pv["pvMax"] = pvtoday
    pvall.reverse()
    num = 0
    for pvday in pvall:
        pvtodaynum = int(pvday[1])
        pv["pvAll"] += pvtodaynum
        if num < 7:
            pv["pvWeek"] += pvtodaynum
        if num < 30:
            pv["pvMonth"] += pvtodaynum
        num += 1
        if pv["pvMax"] < pvtodaynum:
            pv["pvMax"] = pvtodaynum
            pv["pvMaxDay"] = pvday[0]

    pv["pvAverage"] = round(pv["pvAll"] / num)

    return pv


# (用户访问首页时)PV值自增+1
def pv_inc():
    # 判断如果日期值与实际不相等，则需要切换日期
    if read_today_date() != getcurrentdatenum():
        print('Sitch Day---------------------------------')
        # 保存昨天的记录到pvhistory
        pv_yesterday = read_today_pvcount()
        add_pvhistory(pv_yesterday)

        # 清空pvtoday
        clear_pvtoday()

    # 添加今天的分时访问记录
    print('PV Inc---------------------------------')
    add_pvtoday()


# 读取记录的今天日期的字符串
def read_today_date():
    with open(pvtodayfile, 'r') as f:
        return f.readline().strip('\n')


# 读取今天的访问总量
def read_today_pvcount():
    with open(pvtodayfile, 'r') as f:
        lines = f.readlines()
        return len(lines) - 1


# 读取今天的历史访问记录（分时）
def read_pvtoday():
    result = []
    with open(pvtodayfile, 'r') as f:
        f.readline()
        lines = f.readlines()
        for line in lines:
            result.append(line.strip('\n'))
    return result


# 读取总体的历史访问记录（以天为单位）
def read_pvhistory():
    result = []
    with open(pvhistoryfile, 'r') as f:
        lines = f.readlines()
        for line in lines:
            result.append(line.strip('\n').split(':'))
    return result


# 清空今天的分时记录
def clear_pvtoday():
    with open(pvtodayfile, 'w') as f:
        f.write(getcurrentdatenum())


#将今天的分时pv历史值追加写进文件中去
def add_pvtoday():
    with open(pvtodayfile, 'a') as f:
        f.write('\n' + time.strftime('%H:%M:%S'))


#将pv历史值(以天为单位)追加写进总的历史记录文件中去
def add_pvhistory(pv):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today-oneday
    yesterdaystr = yesterday.strftime('%Y%m%d')
    pvhistorystr = '\n' + yesterdaystr + ':' + str(pv)
    with open(pvhistoryfile, 'a') as f:
        f.write(pvhistorystr)


# ------------------------------------------------------------------------
#注册
tools.set_credentials_file(username='cjtlp2006', api_key='Zsr7ENJQJPDeYNVQU8Pw')


# 获取PV历史曲线
def get_pvline(lineType):
    if lineType == 'today':
        pvtoday = read_pvtoday()
        x0 = []
        y0 = []
        for pv in pvtoday:
            hour = str(pv.split(':')[0])+'点'
            if x0.count(hour) == 0:
                x0.append(hour)
                y0.append(1)
            else:
                y0[-1] += 1
        data = [{'x': x0, 'y': y0, 'type': 'bar'}]
        return json.dumps(data)
    else:
        pvhistory = read_pvhistory()
        if lineType == 'week' or lineType == 'month':
            pvcount = pvhistory[-7:-1]
            if lineType == 'month':
                pvcount = pvhistory[-30:-1]
            pvcount.append(pvhistory[-1])
            x0 = [str(i[0]) for i in pvcount]
            x0 = [i[0:4]+'年'+i[4:6]+'月'+i[6:8]+'日' for i in x0]
            y0 = [i[1] for i in pvcount]
            data = [{'x': x0, 'y': y0, 'type': 'bar'}]
            return json.dumps(data)
        elif lineType == 'all':
            x0 = [str(i[0]) for i in pvhistory]
            x0 = [i[0:4]+'-'+i[4:6]+'-'+i[6:8] for i in x0]
            y0 = [i[1] for i in pvhistory]
            data = [{'x': x0, 'y': y0, 'type': 'scatter'}]
            return json.dumps(data)
        else:
            return 'param lineType is not correct!'
