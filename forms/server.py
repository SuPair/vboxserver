# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server.ui'
#
# Created: Thu Dec 18 15:32:04 2014
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_frm_server(object):
    def setupUi(self, frm_server):
        frm_server.setObjectName(_fromUtf8("frm_server"))
        frm_server.setWindowModality(QtCore.Qt.WindowModal)
        frm_server.resize(417, 703)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frm_server.sizePolicy().hasHeightForWidth())
        frm_server.setSizePolicy(sizePolicy)
        frm_server.setMinimumSize(QtCore.QSize(0, 0))
        frm_server.setMaximumSize(QtCore.QSize(170000, 170000))
        self.btn_run = QtGui.QPushButton(frm_server)
        self.btn_run.setGeometry(QtCore.QRect(60, 120, 91, 31))
        self.btn_run.setObjectName(_fromUtf8("btn_run"))
        self.btn_stop = QtGui.QPushButton(frm_server)
        self.btn_stop.setGeometry(QtCore.QRect(250, 120, 91, 31))
        self.btn_stop.setObjectName(_fromUtf8("btn_stop"))
        self.btn_pwd = QtGui.QPushButton(frm_server)
        self.btn_pwd.setGeometry(QtCore.QRect(250, 50, 91, 31))
        self.btn_pwd.setObjectName(_fromUtf8("btn_pwd"))
        self.le_pwd = QtGui.QLineEdit(frm_server)
        self.le_pwd.setGeometry(QtCore.QRect(60, 50, 171, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.le_pwd.sizePolicy().hasHeightForWidth())
        self.le_pwd.setSizePolicy(sizePolicy)
        self.le_pwd.setEchoMode(QtGui.QLineEdit.Password)
        self.le_pwd.setObjectName(_fromUtf8("le_pwd"))
        self.tb_sock = QtGui.QTextBrowser(frm_server)
        self.tb_sock.setGeometry(QtCore.QRect(20, 210, 371, 471))
        self.tb_sock.setObjectName(_fromUtf8("tb_sock"))
        self.label = QtGui.QLabel(frm_server)
        self.label.setGeometry(QtCore.QRect(20, 180, 91, 21))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(frm_server)
        QtCore.QObject.connect(self.btn_stop, QtCore.SIGNAL(_fromUtf8("clicked()")), frm_server.stop)
        QtCore.QObject.connect(self.btn_run, QtCore.SIGNAL(_fromUtf8("clicked()")), frm_server.btn_run)
        QtCore.QObject.connect(self.btn_pwd, QtCore.SIGNAL(_fromUtf8("clicked()")), frm_server.setpwd)
        QtCore.QMetaObject.connectSlotsByName(frm_server)
        frm_server.setTabOrder(self.btn_run, self.btn_stop)

    def retranslateUi(self, frm_server):
        frm_server.setWindowTitle(_translate("frm_server", "vbox server", None))
        self.btn_run.setText(_translate("frm_server", "run", None))
        self.btn_stop.setText(_translate("frm_server", "stop", None))
        self.btn_pwd.setText(_translate("frm_server", "set password", None))
        self.label.setText(_translate("frm_server", "sock info. :", None))

