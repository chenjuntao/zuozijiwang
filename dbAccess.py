import os
from datetime import datetime
import sqlite3
import json


#数据库存放位置
pvdb = 'data/pv.db'


###############################################################
# 公开给外部调用的接口
###############################################################

#用户访问首页时，各个PV值自增+1
def pv_inc():
    # 日期（eg.20170302）
    currentdate = datetime.today().strftime('%Y%m%d')
    # 一年中的第几个星期
    week = datetime.today().isocalendar()[1]
    # 月份
    month = datetime.today().month

    cur = query_pvcurrent()
    # 判断如果日期值与实际不相等，则需要切换日期
    if cur['curday'] != currentdate:
        #如果星期与实际不一样，则需要切换星期
        if cur['curweek'] != week:
            cur['curweek'] = week
            print('Sitch Week---------------------------------')
            #清空上周的历史PV记录
            del_pv_week()

            #记录昨天的日pv
            insert_pv_week(pv)

        #如果月份与实际不一致，则需要切换月份
        if cur['curmonth'] != month:
            cur['curmonth'] = month
            print('Sitch Month---------------------------------')
            #清空上个月的历史PV记录
            del_pv_month()
        else:
            #保存昨天的纪录
            pvhistorystr = currentdate + ':' + str(PV['pvToday']) + '\n'
            add_pvhistory(pvhistorystr)
            print('Save Yesterday PV------------------------------')

        PV['pvDays'] += 1
        PV['pvToday'] = 0
        PV['today'] = currentdate
        print('Sitch Day---------------------------------')

    #各个PV值加1
    PV['pvToday'] += 1
    PV['pvWeek'] += 1
    PV['pvMonth'] += 1
    PV['pvAll'] += 1
    if PV['pvToday'] > PV['pvMax']:
        PV['pvMax'] = PV['pvToday']
        PV['pvMaxDay'] = currentdate

    pvstr = json.dumps(PV)
    write_pv(pvstr)


#获取各个PV值，返回json字符串
def get_pv():
    # pv = read_pv()
    global PV
    jsonstr = json.dumps(PV)
    return jsonstr


#将各个pv值写进文件中去
def write_pv(str):
    with open(pvfile, 'w') as f:
        f.write(str)


#将pv历史值追加写进文件中去
def add_pvhistory(str):
    with open(pvhistoryfile, 'a') as f:
        f.write(str)


#将pv历史值清空
def clear_pvhistory():
    with open(pvhistoryfile, 'w') as f:
        f.write('')

###############################################################
#公共函数
###############################################################
#有返回值的查询
def sqlQuery(sqltxt, *parmas):
    conn = sqlite3.connect(pvdb)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    #处理中文字符需要这一句
    conn.text_factory = str
    c.execute(sqltxt, parmas)
    #读取表中的行
    result = c.fetchall()
    c.close()
    return result


#无返回值的查询
def sqlExe(sqltxt, *parmas):
    conn = sqlite3.connect(pvdb)
    c = conn.cursor()
    #处理中文字符需要这一句
    conn.text_factory = str
    c.execute(sqltxt, parmas)
    conn.commit()
    c.close()


###############################################################
#新建一个数据库，以及相关的数据表
###############################################################
def init_db():
    try:
        if not os.access(pvdb, os.R_OK):
            sqlExe("CREATE TABLE pvtoday (timenum INTEGER, pv INTEGER)")
            sqlExe("CREATE TABLE pvweek (datenum INTEGER, pv INTEGER)")
            sqlExe("CREATE TABLE pvmonth (datenum INTEGER, pv INTEGER)")
            sqlExe("CREATE TABLE pvall (datestr TEXT, pv INTEGER)")
            sqlExe("CREATE TABLE pvcurrent (curday TEXT, curweek TEXT, curmonth TEXT)")
            # 日期（eg.20170302）
            dates_tr = datetime.today().strftime('%Y%m%d')
            # 一年中的第几个星期
            week = datetime.today().isocalendar()[1]
            # 月份
            month = datetime.today().month
            sqlExe("INSERT INTO pvcurrent (curday, curweek, curmonth) VALUES (?,?,?)", dates_tr, week, month)
            return False
        else:
            return True
    except sqlite3.OperationalError:
        return False


###############################################################
#查询记录
###############################################################
def query_pvcurrent():
    cur = {}
    result = sqlQuery("SELECT curday, curweek, curmonth FROM pvcurrent")
    cur['curday'] = result[0][0]
    cur['curweek'] = result[0][1]
    cur['curmonth'] = result[0][2]
    return cur


def query_pv():
    pv = {}
    conn = sqlite3.connect(pvdb)
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM pvtoday")
    pv['pvToday'] = cur.fetchone()[0]

    cur.execute("SELECT sum(pv) FROM pvweek")
    pv['pvWeek'] = cur.fetchone()[0] + pv['pvToday']

    cur.execute("SELECT sum(pv) FROM pvmonth")
    pv['pvMonth'] = cur.fetchone()[0] + pv['pvToday']

    cur.execute("SELECT sum(pv) FROM pvall")
    pv['pvAll'] = cur.fetchone()[0] + pv['pvWeek']

    # 查询最早的日期，然后计算与今天的相差天数，得到总天数
    cur.execute("SELECT min(datestr) FROM pvall")
    s = cur.fetchone()[0]
    mindate = datetime(int(s[0:4]), int(s[4:6]), int(s[6:8]))
    daydelta = datetime.today() - mindate
    pv['pvDays'] = daydelta.days

    cur.execute("SELECT datestr, max(pv) FROM pvall")
    pv['pvMaxDay'] = cur.fetchone()[0]
    pv['pvMax'] = cur.fetchone()[1]

    cur.close()

    jsonstr = json.dumps(pv)
    return jsonstr

    return pv

def query_pvhistory():
    result = sqlQuery("SELECT timenum, sum(pv) FROM pvtoday GROUP BY timenum")
    return result

###############################################################
#增加记录
###############################################################
#据说从 SQLite 的 2.3.4 版本开始，如果将一个表中的一个字段声明为 INTEGER PRIMARY KEY，
#那么只需向该表的该字段插入一个NULL值或者不设值，这个字段的值将会自增
def insert_pv_today(pv):
    # 几点（0-24）
    timenum = datetime.now().hour
    sqlExe("INSERT INTO pvtoday (timenum, pv) VALUES (?,?)", timenum, pv)

def insert_pv_week(pv):
    # 星期几（1-7）
    datenum = datetime.today().isoweekday()
    sqlExe("INSERT INTO pvweek (datenum, pv) VALUES (?,?)", datenum, pv)

def insert_pv_month(pv):
    # 一个月的几号（1-31）
    datenum = datetime.today().day
    sqlExe("INSERT INTO pvmonth (datenum, pv) VALUES (?,?)", datenum, pv)

def insert_pv_all(pv):
    # 年月日（eg.20170302）
    datestr = datetime.today().strftime('%Y%m%d')
    sqlExe("INSERT INTO pvall (datestr, pv) VALUES (?,?)", str(datestr), pv)


###############################################################
#删除记录
###############################################################
def del_pv_today():
    sqlExe("DELETE FROM pvtoday")

def del_pv_week():
    sqlExe("DELETE FROM pvtweek")

def del_pv_month():
    sqlExe("DELETE FROM pvmonth")

#----------------------------------------
#注意事项
#c.execute("SELECT * FROM pv WHERE id = ?",(id,))最后的括号中的参数id后面一定要加一个逗号
#conn.text_factory = str        #插入中文字符需要这一句
#自增字段：据说从 SQLite 的 2.3.4 版本开始，如果将一个表中的一个字段声明为 INTEGER PRIMARY KEY，
#那么只需向该表的该字段插入一个NULL值或者不设值，这个字段的值将会自增
