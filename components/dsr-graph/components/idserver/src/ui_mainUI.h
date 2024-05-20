/********************************************************************************
** Form generated from reading UI file 'mainUI.ui'
**
** Created by: Qt User Interface Compiler version 6.2.4
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINUI_H
#define UI_MAINUI_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_guiDlg
{
public:
    QAction *actionSave;
    QAction *actionSimulate;
    QAction *actionSaveToFile;
    QWidget *centralwidget;
    QMenuBar *menubar;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *guiDlg)
    {
        if (guiDlg->objectName().isEmpty())
            guiDlg->setObjectName(QString::fromUtf8("guiDlg"));
        guiDlg->resize(800, 600);
        actionSave = new QAction(guiDlg);
        actionSave->setObjectName(QString::fromUtf8("actionSave"));
        actionSimulate = new QAction(guiDlg);
        actionSimulate->setObjectName(QString::fromUtf8("actionSimulate"));
        actionSimulate->setCheckable(true);
        actionSaveToFile = new QAction(guiDlg);
        actionSaveToFile->setObjectName(QString::fromUtf8("actionSaveToFile"));
        centralwidget = new QWidget(guiDlg);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        guiDlg->setCentralWidget(centralwidget);
        menubar = new QMenuBar(guiDlg);
        menubar->setObjectName(QString::fromUtf8("menubar"));
        menubar->setGeometry(QRect(0, 0, 800, 22));
        guiDlg->setMenuBar(menubar);
        statusbar = new QStatusBar(guiDlg);
        statusbar->setObjectName(QString::fromUtf8("statusbar"));
        guiDlg->setStatusBar(statusbar);

        retranslateUi(guiDlg);

        QMetaObject::connectSlotsByName(guiDlg);
    } // setupUi

    void retranslateUi(QMainWindow *guiDlg)
    {
        guiDlg->setWindowTitle(QCoreApplication::translate("guiDlg", "DSRViewer", nullptr));
        actionSave->setText(QCoreApplication::translate("guiDlg", "Save", nullptr));
#if QT_CONFIG(tooltip)
        actionSave->setToolTip(QCoreApplication::translate("guiDlg", "<html><head/><body><p>Save file in JSON format</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        actionSimulate->setText(QCoreApplication::translate("guiDlg", "Simulate", nullptr));
        actionSaveToFile->setText(QCoreApplication::translate("guiDlg", "Save", nullptr));
    } // retranslateUi

};

namespace Ui {
    class guiDlg: public Ui_guiDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINUI_H
