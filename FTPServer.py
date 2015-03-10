# -*- coding: utf8 -*-
__author__ = 'Razy.Chen'
from pyftpdlib import ftpserver
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import socket

class FtpServer(QThread):

    def __init__(self,path,parent=None):
        QThread.__init__(self,parent)
        self.Path=path
        self.localIP = socket.gethostbyname(socket.gethostname()) #获得本地IP


    def run(self):
        try:
            authorizer = ftpserver.DummyAuthorizer()
            authorizer.add_user('anonymous', '',self.Path,perm="elradfmw")
            handler = ftpserver.FTPHandler
            handler.authorizer = authorizer
            address = (self.localIP, 54221)
            self.ftpd = ftpserver.FTPServer(address, handler)
            self.ftpd.serve_forever()
            print('ftp started')
        except BaseException,e:
            print(str(e))
        finally :
            self.ftpd.close_all()


    def close(self):
        self.ftpd.close_all()
        print 'ftp closed.'