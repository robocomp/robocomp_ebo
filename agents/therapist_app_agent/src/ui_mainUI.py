# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_guiDlg(object):
    def setupUi(self, guiDlg):
        if not guiDlg.objectName():
            guiDlg.setObjectName(u"guiDlg")
        guiDlg.resize(462, 274)
        self.iniciarJ = QPushButton(guiDlg)
        self.iniciarJ.setObjectName(u"iniciarJ")
        self.iniciarJ.setGeometry(QRect(140, 210, 191, 25))
        self.textEdit = QTextEdit(guiDlg)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(60, 130, 381, 31))
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setStyleSheet(u"background-color: transparent;")
        self.textEdit.setFrameShape(QFrame.NoFrame)
        self.textEdit.setFrameShadow(QFrame.Sunken)
        self.textEdit.setReadOnly(True)
        self.textEdit_2 = QTextEdit(guiDlg)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(60, 60, 381, 31))
        self.textEdit_2.setAutoFillBackground(True)
        self.textEdit_2.setStyleSheet(u"background-color: transparent;")
        self.textEdit_2.setFrameShape(QFrame.NoFrame)
        self.textEdit_2.setFrameShadow(QFrame.Sunken)
        self.textEdit_2.setReadOnly(True)
        self.comboBoxJugadores = QComboBox(guiDlg)
        self.comboBoxJugadores.setObjectName(u"comboBoxJugadores")
        self.comboBoxJugadores.setGeometry(QRect(260, 60, 151, 31))
        self.comboBoxJuego = QComboBox(guiDlg)
        self.comboBoxJuego.setObjectName(u"comboBoxJuego")
        self.comboBoxJuego.setGeometry(QRect(260, 130, 151, 31))

        self.retranslateUi(guiDlg)

        QMetaObject.connectSlotsByName(guiDlg)
    # setupUi

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QCoreApplication.translate("guiDlg", u"therapist_app_agent", None))
        self.iniciarJ.setText(QCoreApplication.translate("guiDlg", u"INICIAR JUEGO", None))
        self.textEdit.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Selecci\u00f3n de juego:</span></p></body></html>", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("guiDlg", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Selecci\u00f3n de usuario:</span></p></body></html>", None))
    # retranslateUi

