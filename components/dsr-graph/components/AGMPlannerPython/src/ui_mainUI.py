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
        """
        Sets the name of a UI object, resizes it to 400x300 pixels, and connects
        slot functions to the object using its metaobject.

        Args:
            guiDlg (object reference.): `QDialog` widget instance to which the
                functions' retranslation and slot connections will be applied.
                
                		- `objectName()` returns the object's name. It is set to "guiDlg"
                upon initialization.
                		- `resize(width, height)` resizes the dialog window to a fixed
                size (400x300 in this case).
                		- `retranslateUi()` is called to update the translated strings
                in the UI elements.
                		- `connectSlotsByName()` connects any slot functions to their
                corresponding signal names.

        """
        if not guiDlg.objectName():
            guiDlg.setObjectName(u"guiDlg")
        guiDlg.resize(400, 300)

        self.retranslateUi(guiDlg)

        QMetaObject.connectSlotsByName(guiDlg)
    # setupUi

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QCoreApplication.translate("guiDlg", u"AGMPlannerPython", None))
    # retranslateUi

