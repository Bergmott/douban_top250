#-*- coding: utf-8 -*-

from multiprocessing.dummy import current_process
from urllib import response
from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import pymysql
import openpyxl


def main():
    baseurl= "https://movie.douban.com/top250?start="
    datalist=getData(baseurl)
    saveData(datalist)
    saveData2db(datalist)


#获取超链接规则
findLink=re.compile(r'<a href="(.*?)">')   
#获取影片图片规则
findImgSrc=re.compile(r'<img.*src="(.*?)"',re.S)    #re.S 表示忽略换行符，即全文匹配而非按行匹配
#影片片名
findTitle=re.compile(r'<span class="title">(.*)</span>')
#影片评分    
findMark=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudgeNumber=re.compile(r'<span>(\d*)人评价</span>')
#概括
findQuote=re.compile(r'<span class="inq">(.*)</span>')
#影片相关内容
findBd=re.compile(r'<p class="">(.*?)</p>',re.S)


def getData(baseurl):   
    datalist=[]
    rank=1#电影排名递增变量
    for i in range(0,10):
        url=baseurl+str(i*25)
        html=askURL(url)   #保存获取到的网页源码

        #逐一解析数据
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            data=[rank]  #保存一部电影的全部信息
            item=str(item)
            #影片名
            title=re.findall(findTitle,item)
            data.append(title[0])
            #影片其他信息
            bd=re.findall(findBd,item)[0]
            #获取导演
            findDirector=re.compile(r'导演:(.*)\xa0\xa0\xa0')
            Director=re.findall(findDirector,bd)
            if len(Director)==0:
                data.append("")
            else:
                data.append(Director[0])
            #获取主演
            findActor=re.compile(r'主演:(.*?)<br/>')
            Actor=re.findall(findActor,bd)
            if len(Actor)==0:
                data.append("")
            else:
                data.append(Actor[0])
            #获取年份
            findYear=re.compile(r'<br/>\s*(\d+)',re.S)
            year=re.findall(findYear,bd)
            data.append(year[0])          
            #获取地区和电影类型
            findArea=re.compile(r'\xa0/\xa0(.*)\xa0/\xa0(.*)')
            Area=re.findall(findArea,bd)
            data.append(Area[0][0])
            data.append(Area[0][1])    
            #影片概括
            quote=re.findall(findQuote,item)
            if len(quote)==0:
                data.append(" ")
            else:
                data.append(quote[0])
            #影片分数
            mark=re.findall(findMark,item)[0]
            data.append(mark)
            #影片评分人数
            JudgeNumber=re.findall(findJudgeNumber,item)[0]
            data.append(JudgeNumber)       
            #获取影片详情链接
            link=re.findall(findLink,item)[0]
            data.append(link)
            #影片宣传图
            imgSrc=re.findall(findImgSrc,item)[0]
            data.append(imgSrc)
            #该电影信息解析结束
            datalist.append(data)
            rank+=1
    return datalist


#得到指定单一url的网页内容
def askURL(url):
    head={     #模拟浏览器头部信息，想豆瓣服务器发送消息
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62",

        }  #用户代理
    request=urllib.request.Request(url,headers=head) #因为需要加入headers所以需要构造request
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e: 
        if hasattr(e, 'code') :
            print(e.code)
        if hasattr(e, 'reason') :
            print(e.reason)
    return html



def saveData(datalist):
    book=openpyxl.Workbook()
    sheet=book.active
    sheet.title="豆瓣电影Top250"
    first=("电影排名","影名","导演","主演","年份","地区","类型","概括","分数","评分人数","详情链接","图片链接")
    sheet.append(first)
    for i in range(0,len(datalist)):
        sheet.append(datalist[i])
    
    book.save("豆瓣电影Top250.xlsx")


def saveData2db(datalist):
    try:
        db=pymysql.connect(host='localhost',user='root',password='158705',database="data_douban")
        print("数据库连接成功")
    except pymysql.Error as e:
        print("数据库连接失败："+str(e))
    cursor=db.cursor()
    for data in datalist:
        for index in range(len(data)):
            data[index]='"'+str(data[index])+'"'
        sql='''
        insert into top250(mv_rank,name,director,actor,year,area,type,info,mark,judgenumber,info_link,pic_link)
        values(%s)'''%",".join(data)
        #print(sql)
        try:
            cursor.execute(sql)#创建表
            db.commit()
            print("数据插入成功")
        except pymysql.Error as e:
            db.rollback()
            print(data[0],"数据插入失败"+str(e))
            break
    db.close()



def init_db():
    sql ='''create table top250(                               
        mv_rank         int,             
        name            varchar(255),                        
        director        varchar(255),                        
        actor           varchar(255),                        
        year            int,                            
        area            varchar(255),                        
        type            varchar(255),                        
        info            text,                           
        mark            numeric,                        
        judgenumber     int,                            
        info_link       text,                           
        pic_link        text,                           
        primary key (mv_rank)                              
    )'''
    try:
        db=pymysql.connect(host='localhost',user='root',password='158705',database="data_douban")
        print("数据库连接成功")
    except pymysql.Error as e:
        print("数据库连接失败："+str(e))
    cursor=db.cursor()
    
    #cursor.execute("CREATE DATABASE data_douban DEFAULT CHARACTER SET utf8")#创建数据库
    try:
        cursor.execute(sql)#创建表
        db.commit()
        print("创建表成功")
    except pymysql.Error as e:
        db.rollback()
        print("创建表失败"+str(e))
    db.close()
    

if __name__ == "__main__":#控制函数执行顺序
    #init_db()
    main()
