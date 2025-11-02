# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Login.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QVBoxLayout, QWidget)
import RemoteVNCBooking_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(328, 195)
        icon = QIcon()
        icon.addFile(u":/pic/icons/login.png", QSize(), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_Point = QLabel(Dialog)
        self.label_Point.setObjectName(u"label_Point")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_Point.sizePolicy().hasHeightForWidth())
        self.label_Point.setSizePolicy(sizePolicy)
        self.label_Point.setMinimumSize(QSize(0, 30))
        font = QFont()
        font.setPointSize(14)
        font.setBold(False)
        self.label_Point.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_Point)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.formPanel = QWidget(Dialog)
        self.formPanel.setObjectName(u"formPanel")
        sizePolicy.setHeightForWidth(self.formPanel.sizePolicy().hasHeightForWidth())
        self.formPanel.setSizePolicy(sizePolicy)
        self.formPanel.setMinimumSize(QSize(310, 90))
        font1 = QFont()
        font1.setUnderline(False)
        self.formPanel.setFont(font1)
        self.formLayout = QFormLayout(self.formPanel)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_Name = QLabel(self.formPanel)
        self.label_Name.setObjectName(u"label_Name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_Name.sizePolicy().hasHeightForWidth())
        self.label_Name.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(False)
        font2.setUnderline(False)
        self.label_Name.setFont(font2)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_Name)

        self.lineEdit_Name = QLineEdit(self.formPanel)
        self.lineEdit_Name.setObjectName(u"lineEdit_Name")
        self.lineEdit_Name.setFont(font2)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_Name)

        self.label_Wwid = QLabel(self.formPanel)
        self.label_Wwid.setObjectName(u"label_Wwid")
        self.label_Wwid.setFont(font2)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_Wwid)

        self.lineEdit_Wwid = QLineEdit(self.formPanel)
        self.lineEdit_Wwid.setObjectName(u"lineEdit_Wwid")
        self.lineEdit_Wwid.setFont(font2)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_Wwid)


        self.verticalLayout.addWidget(self.formPanel)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 12)
        self.checkBox_remember = QCheckBox(Dialog)
        self.checkBox_remember.setObjectName(u"checkBox_remember")
        sizePolicy.setHeightForWidth(self.checkBox_remember.sizePolicy().hasHeightForWidth())
        self.checkBox_remember.setSizePolicy(sizePolicy)
        font3 = QFont()
        font3.setPointSize(12)
        self.checkBox_remember.setFont(font3)
        self.checkBox_remember.setIconSize(QSize(5, 5))
        self.checkBox_remember.setTristate(False)

        self.horizontalLayout.addWidget(self.checkBox_remember)

        self.buttonBox_Start = QDialogButtonBox(Dialog)
        self.buttonBox_Start.setObjectName(u"buttonBox_Start")
        sizePolicy.setHeightForWidth(self.buttonBox_Start.sizePolicy().hasHeightForWidth())
        self.buttonBox_Start.setSizePolicy(sizePolicy)
        self.buttonBox_Start.setMinimumSize(QSize(0, 0))
        self.buttonBox_Start.setSizeIncrement(QSize(0, 0))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(12)
        font4.setBold(False)
        self.buttonBox_Start.setFont(font4)
        self.buttonBox_Start.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.buttonBox_Start.setLayoutDirection(Qt.LeftToRight)
        self.buttonBox_Start.setAutoFillBackground(False)
        self.buttonBox_Start.setOrientation(Qt.Horizontal)
        self.buttonBox_Start.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox_Start.setCenterButtons(True)

        self.horizontalLayout.addWidget(self.buttonBox_Start)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)
        self.buttonBox_Start.accepted.connect(Dialog.accept)
        self.buttonBox_Start.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Login", None))
        self.label_Point.setText(QCoreApplication.translate("Dialog", u"Please enter your Name and ID", None))
        self.label_Name.setText(QCoreApplication.translate("Dialog", u"Display Name", None))
        self.lineEdit_Name.setPlaceholderText(QCoreApplication.translate("Dialog", u"Enter your name", None))
        self.label_Wwid.setText(QCoreApplication.translate("Dialog", u"ID", None))
        self.lineEdit_Wwid.setPlaceholderText(QCoreApplication.translate("Dialog", u"Enter your ID", None))
        self.checkBox_remember.setText(QCoreApplication.translate("Dialog", u"Remember", None))
    # retranslateUi

