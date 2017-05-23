# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 10:40:32 2015

@author: wanggd
"""
import datetime
import urllib 
from bs4 import BeautifulSoup
import time
import matplotlib as mpl
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkMessageBox
import numpy as np
#the parameter{date} is a string whose format is 
#'2015-01-01'
#return an interge between 0 and 6,which 0 means Sunday
def weekday(date):
    day=date.split("-")
    return int(datetime.datetime(int(day[0]),int(day[1]),int(day[2])).strftime("%w"))


#return a list containing the mean of aqi in every week in during 2015 
def get_aqi_mean_week():
    f=open('weather.txt','r')
    #each line has the fomat of 
    #'北京市 2015-01-01 65 良 NO2'
    #note:2015-06-05 the day has no any details about aqi
    lines=f.readlines()
    f.close()
    aqi_mean_week=[]
    temp=0 
    count=0
    weeks=[]
    for line in lines:
        dayInfo=line.split(' ')
        week_day=weekday(dayInfo[1])
        if week_day==6 or line==lines[-1]:
            weeks.append(dayInfo[1])
            temp+=int(dayInfo[2])
            count+=1
            aqi_day=temp/count
            temp=0
            count=0
            aqi_mean_week.append(aqi_day)
        else:
            if dayInfo[2]!='':           
                temp+=int(dayInfo[2])
                count+=1
    return aqi_mean_week,weeks
 
#return the aqi_level of every month in the form of dict with the key is '2015-12'
#and the aqi_level of the all data in database in the form of dict
def get_aqi_level():
    f=open('weather.txt','r')
    lines=f.readlines()
    f.close()
    aqi_level_month={}
    aqi_level_population={}
    for line in lines:
        dayInfo=line.split(' ')
        date=dayInfo[1]
        year_month=date[:-3]
        aqi_level=dayInfo[3]
        if aqi_level=='':
            continue
        if not aqi_level_month.has_key(year_month):
            aqi_level_month[year_month]={}
        if not aqi_level_month[year_month].has_key(aqi_level):
            aqi_level_month[year_month][aqi_level]=0
        if not aqi_level_population.has_key(aqi_level):
            aqi_level_population[aqi_level]=0
        aqi_level_month[year_month][aqi_level]+=1
        aqi_level_population[aqi_level]+=1        
        
    return aqi_level_month,aqi_level_population
 
  
#return sorted primary polution in population in the form of
#[('PM2.5', 139), ('\xb3\xf4\xd1\xf58\xd0\xa1\xca\xb1', 95), ('NO2', 32), ('PM10', 30), ('CO', 3)]
#and return sorted primary polution each month in the form of dict,
#whose key is the year-month as '2015-06'
#and whose value is a list and the member in the list is a tuple as ('CO', 3)
def get_primary_polution():
    f=open('weather.txt','r')
    lines=f.readlines()
    f.close()
    primary_polution_month={}
    primary_polution_population={}
    for line in lines:
        dayInfo=line.split(' ')
        polution=dayInfo[4].split(',')
        year_month=dayInfo[1][:-3]
        for i in range(len(polution)):
            if polution[i]=='' or polution[i]=='\n':
                continue
            if not primary_polution_month.has_key(year_month):
                primary_polution_month[year_month]={}
            if not primary_polution_month[year_month].has_key(polution[i]):
                primary_polution_month[year_month][polution[i]]=0
            if not primary_polution_population.has_key(polution[i]):
                primary_polution_population[polution[i]]=0
            primary_polution_month[year_month][polution[i]]+=1
            primary_polution_population[polution[i]]+=1        
    keys=primary_polution_month.keys()
    sorted_primary_polution_month={}
    for i in range(len(keys)):
        if not sorted_primary_polution_month.has_key(keys[i]):
            sorted_primary_polution_month[keys[i]]={}
        sorted_primary_polution_month[keys[i]]=sorted(primary_polution_month[keys[i]].iteritems(),
                                                     key=lambda asd:asd[1],reverse=True)
        
    sorted_primary_polution_population=sorted(primary_polution_population.iteritems(),
                                              key=lambda asd:asd[1],reverse=True)
    return sorted_primary_polution_month,sorted_primary_polution_population

#return the sorted primaryPolution and corresponding times in a specific month
#and its default return value is the population        
def get_primary_polution_month(year_month=0):
    primary_polution_month,primary_polution_population=get_primary_polution()
    primaryPolution=[]
    primaryPolutionTimes=[]
    if year_month:   
        primaryPolutionInMonth=primary_polution_month[year_month]
        for i in range(len(primaryPolutionInMonth)):
            primaryPolution.append(primaryPolutionInMonth[i][0])
            primaryPolutionTimes.append(primaryPolutionInMonth[i][1])
    else:
        for i in range(len(primary_polution_population)):
            primaryPolution.append(primary_polution_population[i][0])
            primaryPolutionTimes.append(primary_polution_population[i][1])
                
    return primaryPolution,primaryPolutionTimes


#add the lastest item into the dataprimary_polution_month,primary_polution_populationbase that contains all information of aqi
def update_db():
    #get the last date in the database
    def getLastDate():
        f=open('weather.txt','r')
        lines=f.readlines()
        f.close()
        lastLine=lines[-1].split(' ')
        return lastLine[1]     
    
    def getCurrentTime():
        return time.strftime("%Y-%m-%d",time.localtime(time.time()))

    def getHtml(startTime,endTime):
        url="http://datacenter.mep.gov.cn/report/air_daily/air_dairy.jsp?city=%E5%8C%97%E4%BA%AC%E5%B8%82%20&startdate="+startTime+"&enddate="+endTime+"&page=1"
        page=urllib.urlopen(url)
        return page.read()
    
    lastTime=str(getLastDate())
    newTime=str(datetime.date.today()-datetime.timedelta(days=1))
    if lastTime==newTime:
        tkMessageBox.showinfo("prompt", "The database is the lastest!")
        return 
    html_doc=getHtml(lastTime,newTime)
    soup=BeautifulSoup(html_doc,'html.parser')
    #the td tag may be different along the day
    tds=soup.find_all('td',class_='report1_11')
    count=0
    f=open('weather.txt','a')
    line=''
    new_lines=[]
    for td in tds[:-5]:
        count+=1
        if count==1:
            continue
        if count==6 and td!=tds[-5]:
            line+=td.text+" "
            new_lines.append(line)
            line=''
            count=0
        else:
            line+=td.text+" "
    new_lines.reverse()
    for i in range(len(new_lines)):
        f.write("\n"+new_lines[i].encode('gb2312'))
    f.close() 
    if len(new_lines)==0:
        tkMessageBox.showinfo("Error", "Update Failed!\nTry again or check your connection!")
    else:
        tkMessageBox.showinfo("prompt", "Update Succeed!")


def transfer(Chinese):
    return Chinese.decode('utf-8').encode('gb2312')
   
def transferToEnglish(s):
    result=[]
    for i in range(len(s)):
        if s[i]==transfer('优'):
            result.append('good')
        elif s[i]==transfer('良'):
            result.append('moderate')
        elif s[i]==transfer('轻度污染'):
            result.append('light polution')
        elif s[i]==transfer('中度污染'):
            result.append('medium polution')
        elif s[i]==transfer('重度污染'):
            result.append('heavy polution')
        else:
            result.append('server polution')
    return result
 
def getAllDate():
    f=open('weather.txt','r')
    lines=f.readlines()
    f.close()
    allDate=[]
    for line in lines:
        dayInfo=line.split(' ')
        date=dayInfo[1]
        year_month=date[:-3]
        allDate.append(year_month)
    return set(allDate)
         
#the parameter flag represents a different graph 
#flag=其他 折线图
#flag=2 饼图
#flag=3 柱状图
def drawPic(flag,year_month=''):
    
    if year_month!='' and year_month not in getAllDate():
        tkMessageBox.showinfo("Error", "Please input a right form of date!")
        return
    
    drawPic.f.clf()
    drawPic.a=drawPic.f.add_subplot(111)
        
    #饼图
    if flag==2:
        aqi_level_month,aqi_level_population=get_aqi_level()
        if year_month:
            aqi=aqi_level_month[year_month]
            drawPic.a.set_title('Rate of the Primary Polution in '+year_month)   
        else:
            aqi=aqi_level_population           
            drawPic.a.set_title('Rate of the Primary Polution in Database') 
        explode=[0.02 for i in range(len(aqi))]
        drawPic.a.pie(aqi.values(), labels=transferToEnglish(aqi.keys()), explode=explode,
                           labeldistance=1.1,shadow=True,autopct='%1.1f%%')       
        drawPic.canvas.show()
        return 
    
    #柱状图
    if flag==3:
        if year_month:
            drawPic.a.set_title('Types of pollutant in '+year_month)   
        else:
            drawPic.a.set_title('Types of pollutant in Database') 
        primaryPolution,primaryPolutionTimes=get_primary_polution_month(year_month) 
        drawPic.a.bar([i for i in range(1,1+len(primaryPolutionTimes))],
                       primaryPolutionTimes,color='c',width=0.5)
        drawPic.a.set_xlim(0,1+len(primaryPolutionTimes))
        drawPic.a.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1))
        ind=np.arange(len(primaryPolution))            
        drawPic.a.set_xticks(ind+1.25)
        drawPic.a.set_ylim(0,int(primaryPolutionTimes[0]*1.2))
        if transfer('臭氧8小时') in primaryPolution:
            primaryPolution[primaryPolution.index(transfer('臭氧8小时'))]='Ozone'
        '''
        try:
            drawPic.a.set_xticklabels(primaryPolution)
        except UnicodeDecodeError:
            for i in range(len(primaryPolution)):
                if len(primaryPolution[i])==9:
                    primaryPolution[i]='Ozone'
                    break              
            drawPic.a.set_xticklabels(primaryPolution)
         '''  
        drawPic.a.set_xticklabels(primaryPolution)
        xlabels = drawPic.a.get_xticklabels()
        for xl in xlabels:
            xl.set_size(16)
        drawPic.a.grid(True)
        drawPic.canvas.show()
        return    
        
        
    #折现图    
    aqi_mean_week,weeks=get_aqi_mean_week()
    global t      
    if flag==0:
        t=30
    elif flag==1:
        if t<len(weeks)-15:
            t+=1
    else:
        if t>=1:
            t-=1 
    aqi_mean_week=aqi_mean_week[t:t+15]
    weeks=weeks[t:t+15]
    weeks.insert(0,0)
    drawPic.a.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1))     

    x=[i for i in range(1,len(aqi_mean_week)+1)]     
     
    drawPic.a.plot(x,aqi_mean_week)
    drawPic.a.scatter(x,aqi_mean_week)
     
    drawPic.a.set_xlim(1,len(x))
    drawPic.a.set_ylim(0,500)
    
    drawPic.a.grid(True)
    drawPic.a.set_title('AQI_Mean_Week')

    drawPic.a.set_xticklabels(weeks)
    xlabels = drawPic.a.get_xticklabels()
    for xl in xlabels:
        xl.set_rotation(75)
        xl.set_size(9)
    
    drawPic.canvas.show()

def main():
 
    def getHelpManual():
        help_doc="欢迎使用:\n"+\
                 "菜单栏中的三个图表分别对应着折线图，饼图，柱状图，其中窗口中的最左边的"+\
                 "的两个按钮应用于折线图的向左和向右查看，中间的输入框为用户待查询的年月"+\
                 "，步骤为先填写输入框，后点击Start菜单下对应的查询方式，如果输入框为空白"+\
                 "则默认查询的是所有数据，右边的按钮用于更新数据库。"
                 
        tkMessageBox.showinfo("Help", help_doc)
        

    root=Tk()
    root.title("AQI Query")
    root.wm_resizable(width=False,height=False)#禁用窗口缩放
    
    frame1=Frame(root)
    frame1.grid(row=1,column=0)
    frame2=Frame(root)
    frame2.grid(row=1,column=1)

    drawPic.f = Figure(figsize=(8,8), dpi=75) 
    drawPic.canvas = FigureCanvasTkAgg(drawPic.f, master=root)
    drawPic.canvas.show()
    drawPic.canvas.get_tk_widget().grid(row=2,columnspan=4)

    Button(frame1,text=' previous ',command=lambda:drawPic(-1)).grid(row=0,column=1)
    Button(frame1,text=' next ',command=lambda:drawPic(1)).grid(row=0,column=2) 
     
    Label(frame2, text="Input a year-month:").grid(row=1,column=1)  
    entry=Entry(frame2,bd=2,width=15)
    entry.grid(row=1,column=2)
    Label(frame2, text="eg:'2015-01'").grid(row=1,column=3)
    
    Button(root,text='update database',command=update_db).grid(row=1,column=2)         
    
    menubar=Menu(root) 
    showmenu =Menu(menubar, tearoff=0)    
    showmenu.add_command(label="每周平均AQI折线图",command=lambda:drawPic(0))
    showmenu.add_command(label="各月空气质量等级饼图",command=lambda:drawPic(2,entry.get()))
    showmenu.add_command(label="各月各污染物柱状图",command=lambda:drawPic(3,entry.get()))
    showmenu.add_separator()    
    showmenu.add_command(label="退出",command=lambda:root.destroy())        
    menubar.add_cascade(label="Start", menu=showmenu)
    
    helpmenu=Menu(menubar,tearoff=0)  
    menubar.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="如何使用",command=getHelpManual)
    helpmenu.add_separator()
    helpmenu.add_command(label="联系我们")
    
    root.config(menu=menubar)

    root.mainloop()
    
if __name__=='__main__':    
    #initialize the arange of the line chart to be showed  
    #and t represents the t th week from when it begins
    t=30 
    main()   
















