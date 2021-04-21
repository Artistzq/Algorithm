# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(861, 735)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_header = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_header.setFont(font)
        self.label_header.setAlignment(QtCore.Qt.AlignCenter)
        self.label_header.setObjectName("label_header")
        self.verticalLayout_2.addWidget(self.label_header)
        self.tableView_result = QtWidgets.QTableView(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.tableView_result.setFont(font)
        self.tableView_result.setObjectName("tableView_result")
        self.verticalLayout_2.addWidget(self.tableView_result)
        self.horizontalLayout.addWidget(self.frame_3)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setObjectName("formLayout")
        self.label_seq = QtWidgets.QLabel(self.frame)
        self.label_seq.setObjectName("label_seq")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_seq)
        self.lineEdit_seq = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_seq.setObjectName("lineEdit_seq")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_seq)
        self.lineEdit_start = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_start.setObjectName("lineEdit_start")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_start)
        self.label_start = QtWidgets.QLabel(self.frame)
        self.label_start.setObjectName("label_start")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_start)
        self.verticalLayout.addWidget(self.frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.frame_2 = QtWidgets.QFrame(self.groupBox)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBox_alg = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_alg.setObjectName("comboBox_alg")
        self.comboBox_alg.addItem("")
        self.comboBox_alg.addItem("")
        self.comboBox_alg.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox_alg)
        self.checkBox_is_greater = QtWidgets.QCheckBox(self.frame_2)
        self.checkBox_is_greater.setObjectName("checkBox_is_greater")
        self.horizontalLayout_2.addWidget(self.checkBox_is_greater)
        self.pushButton_schedule = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_schedule.setObjectName("pushButton_schedule")
        self.horizontalLayout_2.addWidget(self.pushButton_schedule)
        self.verticalLayout.addWidget(self.frame_2)
        self.horizontalLayout.addWidget(self.groupBox)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 861, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "磁盘移臂调度"))
        self.label_header.setText(_translate("MainWindow", "调度算法"))
        self.groupBox.setTitle(_translate("MainWindow", "输入"))
        self.label_seq.setText(_translate("MainWindow", "磁道号序列"))
        self.label_start.setText(_translate("MainWindow", "起始磁道"))
        self.comboBox_alg.setItemText(0, _translate("MainWindow", "先来先服务"))
        self.comboBox_alg.setItemText(1, _translate("MainWindow", "最短寻道时间优先"))
        self.comboBox_alg.setItemText(2, _translate("MainWindow", "扫描算法"))
        self.checkBox_is_greater.setText(_translate("MainWindow", "初始方向增大"))
        self.pushButton_schedule.setText(_translate("MainWindow", "调度"))