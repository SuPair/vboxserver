# -*- coding: utf8 -*-
__author__ = '54'

import sys
sys.path.append('forms')
from PyQt4.QtCore import *
import os
import socket
import time
import threading
import select
from forms.server import *
from VboxCtrl import VboxControl
from win32com import client
import pythoncom
from FTPServer import FtpServer


class Main_processor(QThread): #注意继承QThread
    #thread_stop_flag=False#业务处理线程停止信号
    def __init__(self,parent=None):
        QThread.__init__(self, parent)#添加QThread初始化方法
        self.listen_sock=None
        self.thread_sock=None#负责socket通讯与业务处理的子线程
        self.server_stop_flag=False#服务停止信号
        #创建FTP文件夹
        self.FtpPath=(os.getenv('VBOX_MSI_INSTALL_PATH'))[:2]+'\\VboxMachine\\Ftp_Folder'
        if os.path.isdir(self.FtpPath)==False:
            os.mkdir(self.FtpPath)
        #实例化FTPserver对象
        self.Ftp=FtpServer(self.FtpPath)
        pythoncom.CoInitialize()
    #设置服务器参数
    def set_server(self,password,ui):
        self.password=password
        self.ui=ui

    #封装的传递界面显示信息的方法
    def tb(self,msg,addr=''):
        self.ui.tb_sock.append(time.asctime()+':  '+msg+addr)

    #重置类实例(重新执行__init__)
    def reset(self):
        self.listen_sock=None
        self.thread_sock=None
        self.server_stop_flag=False
        pythoncom.CoInitialize()
    def run(self):  #启动socket线程,开始监听端口
        if self.password==None:
            self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  set password first! ')
        else:
            try:
                #配置socket
                self.listen_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.listen_sock.setblocking(1)#socket使用阻塞模式
                self.listen_sock.bind(('0.0.0.0',54254))
                self.listen_sock.listen(1) #只监听1个连接
                self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is running,waiting for connect...')
                self.emit(SIGNAL('set_flag(int)'),1)
                list_socket=[self.listen_sock]
                while True: #监听socket连接的循环
                    if self.server_stop_flag==True:#循环开始时监测是否有关闭服务运行的信号,如果有,跳出循环
                        print('stop=1')
                        break
                    else:
                        print('233')
                        re,ws,es=select.select(list_socket,[],[],5)
                        for r in re:
                            if r is self.listen_sock:
                                sock,addr=self.listen_sock.accept()
                                #建立新线程用于处理TCP连接(二期改造为多center连接时的多线程施工点)
                                self.thread_sock=threading.Thread(target=self.link_processor,args=(sock,addr))
                                self.thread_sock.start()
                            else:
                                data=r.recv(4096)
                                if not data:
                                    continue
                self.listen_sock.close()
                self.listen_sock=None
                self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopped')
                self.emit(SIGNAL('set_flag(int)'),2)
            except socket.error,e:
                self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket error '+str(e))
                self.listen_sock.close()
            finally:
                pass


    def stop(self):
        print('stop')
        if self.listen_sock is not None:
            self.server_stop_flag=True
            self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopping...')
        else:
            self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket is not open !')

    #socket收到的字符串,每一位字符后会被加上'\x00'.原因不明,以下的遍历用以除去'\x00'
    def remove(self,command):
        list_removed=''
        for tem in command:
            if tem=='\x00':
                continue
            list_removed=list_removed+tem
        return list_removed

    #多线程运行Ftp服务器函数
    def FtpRun(self):
        self.Ftp.start()
    #关闭FTP服务器函数
    def FtpClose(self):
        self.Ftp.close()

    def link_processor(self,sock,addr): #连接处理函数
        self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Accept new center connection form '+str(addr))
        #进入密码验证循环
        #vb=VboxControl()#实例化新的vboxAPI控制类对象
        try:
            while True: #密码验证处理外层循环
                print('password recv')
                #监测是否有关闭服务运行的信号,如果有,跳出循环
                if self.server_stop_flag==True:
                        sock.sendall('exit')
                        print('disconn')
                        raise ServerStop()
                while True:#循环recv()循环
                    #监测是否有关闭服务运行的信号,如果有,跳出循环
                    if self.server_stop_flag:
                        sock.sendall('exit')
                        raise ServerStop()
                    recv_data=sock.recv(4096)
                    if len(recv_data) !=0:
                        print(recv_data)
                        break
                print('password recv over')
                Authentication=self.remove(recv_data)
                Authentication=Authentication.split('|')
                print(Authentication)
                if Authentication[0]=='login':
                    print('password 1')
                    if Authentication[1]==self.password:
                        print('success')
                        sock.sendall('login|success')
                        self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  login success! welcome center from '+str(addr))
                        break
                    else:
                        sock.send('login|wrong password')
                        self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  wrong password,login fail from '+str(addr))
                        continue
                if Authentication[0]=='exit':
                     self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [exit] received,link close '+str(addr))
                     break
            #验证通过,进入命令处理循环,此处开始循环接收与处理命令
            vb=VboxControl()
            while True:
                #监测是否有关闭服务运行的信号,如果有,跳出循环
                if self.server_stop_flag==True:
                        if self.stoploop_flag==True:
                            sock.sendall('exit')
                            raise ServerStop()
                print('waiting command')
                while True:#循环recv()循环
                    #监测是否有关闭服务运行的信号,如果有,跳出循环
                    if self.server_stop_flag==True:
                        sock.sendall('exit')
                        raise ServerStop()
                    recv_data=sock.recv(4096)
                    if len(recv_data) !=0:break
                commandlist=self.remove(recv_data)
                commandlist=commandlist.split('|')
                self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [ '+commandlist[0]+' ] is received from '+str(addr))
                if commandlist[0]=='exit':#判断是否为关闭连接的命令,如果是,跳出循环
                    self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [exit] received ,link close'+str(addr))
                    break
                #------------定义了几种非VirtualBox控制命令的通讯关键字识别的操作----------------------
                #开启FTP服务器
                elif commandlist[0]=='ftp_start':
                    try:
                        self.FtpRun()
                        sock.sendall('success')
                        continue
                    except BaseException,e:
                        sock.sendall('|'.join('failure',str(e)))
                        continue
                #关闭FTP服务器
                elif commandlist[0]=='ftp_close':
                    try:
                        self.FtpClose()
                        sock.sendall('success')
                        continue
                    except BaseException,e:
                        result=('failure',str(e))
                        result='|'.join(result)
                        sock.sendall(result)
                        continue
                #心跳检测
                elif commandlist[0]=='heartbeat':
                    if self.server_stop_flag==True:
                        sock.sendall('exit')
                        break
                    else:
                        result=('heartbeating')
                        sock.sendall(result)
                        self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  heartbeating ')
                        continue
                #传递拆分好的命令与参数list到vbox功能处理模块
                pythoncom.CoInitialize()
                result=vb.vbox_funcation(commandlist)
                #循环遍历result,将非str类型的元素转换为str类型
                for i in range(0,len(result)):
                    if type(result[i]) is not str:
                        result[i]=str(result[i])
                #返回执行结果
                result='|'.join(result)
                sock.sendall(result)
                #self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [ '+send_data+' ] is send to '+addr)
            sock.close()
            #self.emit(SIGNAL('set_flag(int)'),2)
        except socket.error,e:
            self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket error '+str(e))
            sock.close()
            #self.emit(SIGNAL('set_flag(int)'),2)
        except ServerStop,e:
            sock.close()
            #self.emit(SIGNAL('set_flag(int)'),2)
        finally:
            sock.close()


class ServerStop(StandardError): #用于在停止服务时直接跳出link_processor的错误
    pass