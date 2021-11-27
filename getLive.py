import requests
import json
import re
import pathlib
import configparser, os
import time
import win32gui
import win32con


patStr=''
perTime='60'
roomID='92613'
curTitle=''

class TestTaskbarIcon:
    def __init__(self):
        # 注册一个窗口类
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = "PythonCheckLive"
        wc.lpfnWndProc = {win32con.WM_DESTROY: self.OnDestroy, }
        classAtom = win32gui.RegisterClass(wc)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom, "CheckLive", style,
                                          0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                          0, 0, hinst, None)
        hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        nid = (self.hwnd, 0, win32gui.NIF_ICON, win32con.WM_USER + 20, hicon, "CheckLive")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
 
    def showMsg(self, title, msg):
        # 原作者使用Shell_NotifyIconA方法代替包装后的Shell_NotifyIcon方法
        # 据称是不能win32gui structure, 我稀里糊涂搞出来了.
        # 具体对比原代码.
        nid = (self.hwnd,  # 句柄
               0,  # 托盘图标ID
               win32gui.NIF_INFO,  # 标识
               0,  # 回调消息ID
               0,  # 托盘图标句柄
               "LiveMessage",  # 图标字符串
               msg,  # 气球提示字符串
               0,  # 提示的显示时间
               title,  # 提示标题
               win32gui.NIIF_INFO  # 提示用到的图标
               )
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
 
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # Terminate the app.



def get():
    r=requests.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getOffLiveList?room_id='+roomID)

    rData=json.loads(r.text)

    title=rData['data']['record_list'][0]['title']

    pat=(patStr)
    matchObj=re.match(pat,title)
    global curTitle
    if matchObj and curTitle!=title:
        curTitle=title
        t = TestTaskbarIcon()
        t.showMsg("检测到直播间标题符合要求", '当前直播标题：'+title)


def readConfig():
    path=pathlib.Path('config.ini')        
    config=configparser.ConfigParser()

    encodingUser='utf-8'


    if not os.path.exists('config.ini'):
        print('检测到无配置文件，正在生成……')
        config['config'] = {'roomID': '92613', 'times': '60','pattern':''}
        config.write(open('config.ini', 'w'))
        print('配置文件生成成功，可以根据个人自定义修改后重新打开，roomid为房间号，times为检测的周期，单位：秒\npattern是正则表达式，例如想检测抓鬼和以撒则写：瓜|以撒')
    else:
        try:
            config.read('config.ini')
        except:
            config.read('config.ini',encoding=encodingUser)
        global patStr,perTime,roomID

        try:
            roomID=config.get('config','roomID')
        except configparser.NoOptionError:
            config.set('config','roomID',str(roomID))
            config.write(open('config.ini', 'w'))

        try:
            perTime=config.get('config','times')
        except configparser.NoOptionError:
            config.set('config','times',str(perTime))
            config.write(open('config.ini', 'w'))

        

        try:
            patStr=config.get('config','pattern')
        except configparser.NoOptionError:
            config.set('config','pattern',patStr)
            config.write(open('config.ini', 'w'))
        


readConfig()
while(1):
    get()
    print("直播间标题监控中……")
    time.sleep(int(perTime))
