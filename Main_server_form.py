# -*- coding: utf8 -*-
__author__ = '54'
import sys,os
sys.path.append('forms')
import time
import socket
import select
import threading
from forms.server import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Main_server_processor import Main_processor

class Main_form(QtGui.QMainWindow):
    #thread_stop_flag=False#业务处理线程停止信号
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent=None)
        self.ui=Ui_frm_server()
        self.ui.setupUi(self)
        self.ui.btn_stop.setEnabled(False)
        self.server_thread=Main_processor()
        self.running_flag=False
        self.password=None
        #预留初始密码复制操作
        #self.password=PASSWORD
        #定义信号
        self.connect(self.server_thread,SIGNAL('set_info(QString)'),self.set_tb_sock)#绑定给server_thread对象的信号,用以发送tb_sock上显示的信息
        self.connect(self,SIGNAL('stop()'),self.server_thread.stop)#绑定给self的信号,用以向server_thread对象发送调用stop的信号
        self.connect(self.server_thread,SIGNAL('set_flag(int)'),self.set_flag)#定义集中可能出现的通知情况,用以让服务线程通知界面


    #设置密码按钮对应click()方法
    def setpwd(self):
        self.ui.le_pwd.setText('123')
        if self.ui.le_pwd.text() != '':
            self.password = self.ui.le_pwd.text()#设定密码,使用变量password储存;目前储存在内存中,之后版本将写入文件
            self.ui.tb_sock.append(time.asctime()+':  Password set to '+ self.password)
        else:
            self.ui.tb_sock.append(time.asctime()+':  Password is None !')

    #运行按钮对应的click()方法
    def btn_run(self):
        #负责宿主服务器整体业务处理的子进程(避免业务阻塞Qt界面在主进程中的运行)
        print('1')
        self.server_thread.reset()
        self.server_thread.set_server(self.password,self.ui)
        print('2')
        self.server_thread.server_stop_flag=False
        self.server_thread.start()
        print('3')
        # self.f=fun()
        # self.f.start()

    #停止按钮对应的click方法
    def stop(self):
        if self.running_flag==True:
            self.emit(SIGNAL('stop()'))
        else:
            self.ui.tb_sock.append(time.asctime()+':  Server is not running !')

    #信号对应处理方法
    def set_flag(self,flag):
        if flag==1: #服务启动成功信号
            self.running_flag=True
            self.ui.btn_run.setEnabled(False)
            self.ui.btn_stop.setEnabled(True)
        if flag==2: #服务停止成功信号
            self.running_flag=False
            self.ui.btn_run.setEnabled(True)
            self.ui.btn_stop.setEnabled(False)
        if flag==3: #操作失败信号
            self.ui.tb_sock.append(time.asctime()+':  An error occurred,operation failed ')


    #接收tb_sock信息的方法
    def set_tb_sock(self,sock_info):
        if sock_info is not None or sock_info!='':
            self.ui.tb_sock.append(sock_info)
        else:
            print('None')


# class Main_processor(QThread): #注意继承QThread
#     #thread_stop_flag=False#业务处理线程停止信号
#     def __init__(self,parent=None):
#         QThread.__init__(self, parent)#添加QThread初始化方法
#         self.listen_sock=None
#         self.thread_sock=None#负责socket通讯与业务处理的子线程
#         self.server_stop_flag=False#服务停止信号
#
#     def test(self):
#         while True:
#             print('i')
#
#     def set_password(self,password):
#         self.password=password
#
#     def run(self):  #启动socket线程,开始监听端口
#         if self.password==None:
#             self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  set password first! ')
#             print('4')
#         else:
#             try:
#                 print('5')
#                 #配置socket
#                 self.listen_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#                 self.listen_sock.setblocking(1)#socket使用阻塞模式
#                 self.listen_sock.bind(('0.0.0.0',54254))
#                 self.listen_sock.listen(1) #只监听1个连接
#                 self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is running,waiting for connect...')
#                 list_socket=[self.listen_sock]
#                 print('sock')
#                 while True: #监听socket连接的循环
#                     self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  starting')
#                     if self.server_stop_flag==True:#循环开始时监测是否有关闭服务运行的信号,如果有,跳出循环
#                         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopping...')
#                         break
#                     else:
#                         re,ws,es=select.select(list_socket,[],[],5)
#                         for r in re:
#                             if r is self.listen_sock:
#                                 sock,addr=listen_sock.accept()
#                                 #建立新线程用于处理TCP连接(二期改造为多center连接时的多线程施工点)
#                                 self.thread_sock=threading.current_thread(target=link_processor,args=(sock,addr))
#                                 self.thread_sock.start()
#                             else:
#                                 data=r.recv(1024)
#                                 if not data:
#                                     continue
#                 self.listen_sock.close()
#                 self.listen_sock=None
#                 self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopped')
#             except Socket.error,e:
#                 self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket error '+e)
#             finally:
#                 pass
#                 #self.listen_sock.close()
#
#     def stop(self):
#         if self.listen_sock is not None:
#             self.server_stop_flag=True
#         else:
#             self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket is not open !')
#
#     def link_processor(self,sock,addr): #连接处理函数
#         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Accept new center connection form '+addr)
#         #进入密码验证循环
#         try:
#             while True: #密码验证处理外层循环
#                 while True:#循环recv()循环
#                     recv_data=sock.recv(4096)
#                     if len(recv_data) !=0:
#                         break
#                 #监测是否有关闭服务运行的信号,如果有,跳出循环
#                 if self.server_stop_flag==True:
#                         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopping...')
#                         sock.sendall('exit')
#                         break
#                 list=recv_data.split('♂')
#                 if list[0]=='login':
#                     if list[1]==self.password:
#                         sock.sendall('login♂success')
#                         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  login success! welcome center from '+addr)
#                         break
#                     else:
#                         sock.send('login♂wrong password')
#                         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  wrong password,login fail from '+addr)
#                         continue
#                 if list[0]=='exit':
#                      self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  exit received,link close '+addr)
#                      break
#             sock.close()
#         #验证通过,进入命令处理循环,此处开始循环接收与处理命令
#             while True:
#                 while True:#循环recv()循环
#                     recv_data=sock.recv(4096)
#                     if len(recv_data) !=0:break
#                 #监测是否有关闭服务运行的信号,如果有,跳出循环
#                 if self.server_stop_flag==True:
#                         self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  Server is stopping...')
#                         sock.sendall('exit')
#                         break
#                 list=recv_data.split('♂')
#                 if list[0]=='exit':#判断是否为关闭连接的命令,如果是,跳出循环
#                     self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [exit] received from'+addr)
#                     break
#                 #传递拆分好的命令与参数list到vbox功能处理模块
#                 #vbox_funcation(list)
#                 self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [ '+recv_data+' ] is received from '+addr)
#                 #self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  [ '+send_data+' ] is send to '+addr)
#             sock.close()
#         except socket.error,e:
#             self.emit(SIGNAL("set_info(QString)"),time.asctime()+':  socket error '+e)
#         finally:
#             sock.close()

if __name__ == "__main__":
    app=QtGui.QApplication(sys.argv)
    myapp=Main_form()
    myapp.show()
    sys.exit(app.exec_())
