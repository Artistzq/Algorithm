#  bug:
#  ----1. 横向移动，高光会消失
#  ----2. messagebox一次触发会出现多个
# 3. 位示图显示无此文件,但消息列表提示已存在
# 4. 颜色显示出错
# 5. 回收算法

from freespace import SimulatedFile, SimulatedDisk
import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_mainwindow_bkp import *


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, blocks, size_per_block, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.SD = SimulatedDisk(blocks, size_per_block, m=25, n=40)
        self.pushButton_assign.clicked.connect(self.assign)
        self.pushButton_reset.clicked.connect(self.reset)
        self.tableWidget_files.setMouseTracking(True)
        self.current_hover = [0, 0]
        self.tableWidget_files.cellEntered.connect(self.highlight)
        self.listView_msg.clicked.connect(self.show_msg)
        self.ramdom_one = []
        # 是否随机置1
        if self.radioButton_set1.isChecked():
            self.random_set()
        self.init_ui()

    def assign(self):
        # 是否随机置1
        if self.radioButton_set1.isChecked():
            self.random_set()

        if self.comboBox_assign.currentIndex() == 0:
            print("随机生成")
            num = 50
            ids = list(range(num))
            names = [str(id) + '.text' for id in ids]
            sizes = [random.randint(2, 10) for i in range(num)]
            simulated_files = [SimulatedFile(id, name, size) for id, name, size in zip(ids, names, sizes)]
            self.SD.store_files(simulated_files)
        else:
            print("手动输入")
        self.update_ui()

    def on_combobox_change(self):
        pass

    def random_set(self):
        bm = self.SD.bitmap
        self.ramdom_one = [random.randint(0, 999) for i in range(1000)]
        for idx in self.ramdom_one:
            i, j = idx // self.SD.n, idx % self.SD.n
            self.SD.bitmap[i][j] = True
            self.tableView_bitmap.model().item(i, j).setBackground(QBrush(QColor(0, 0, 255)))

    def init_ui(self):
        # 设置样式
        self.tableWidget_files.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_files.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget_files.verticalHeader().setVisible(False)
        self.tableWidget_files.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableView_bitmap.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_bitmap.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_bitmap.setEditTriggers(QTableView.NoEditTriggers)
        self.listView_msg.setEditTriggers(QListView.NoEditTriggers)

        self.data_to_ui()

    def data_to_ui(self):
        # 获取文件列表
        files = self.SD.files
        self.tableWidget_files.setColumnCount(5)
        self.tableWidget_files.setRowCount(len(files))
        self.tableWidget_files.setHorizontalHeaderLabels(["ID", "文件名", "文件大小(k)", "文件起始盘块号", "结束盘块号"])
        for row, file in enumerate(files):
            for col, value in enumerate(file.get()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                self.tableWidget_files.setItem(row, col, item)

        # 获取位示图
        bm = self.SD.bitmap
        bm_model = QStandardItemModel(len(bm), len(bm[0]))
        for i in range(len(bm)):
            for j in range(len(bm[0])):
                v = 1 if bm[i][j] else 0
                bm_model.setItem(i, j, QStandardItem(str(v)))
                if v == 1:
                    bm_model.item(i, j).setBackground(QBrush(QColor(255, 0, 0)))
                else:
                    bm_model.item(i, j).setBackground(QBrush(QColor(0, 255, 0)))
        self.tableView_bitmap.setModel(bm_model)
        # 显示随机
        # for idx in self.ramdom_one:
        #     i, j = idx // self.SD.n, idx % self.SD.n
        #     self.tableView_bitmap.model().item(i, j).setBackground(QBrush(QColor(0, 0, 255)))

        # 获取消息队列
        msgs = [msg.split('\n')[0] for msg in self.SD.messages]
        msg_model = QStringListModel()
        msg_model.setStringList(msgs)
        self.listView_msg.setModel(msg_model)

    def highlight(self, row, col):
        print("current: ", row, col)
        old_start = self.SD.files[self.current_hover[0]].start_pos
        old_end = self.SD.files[self.current_hover[0]].end_pos
        start = self.SD.files[row].start_pos
        end = self.SD.files[row].end_pos
        items = [self.tableWidget_files.item(row, i) for i in range(5)]
        old_items = [self.tableWidget_files.item(self.current_hover[0], i) for i in range(5)]
        if self.current_hover[0] != row:
            for old_item in old_items:
                old_item.setBackground(QBrush(QColor('white')))
            if -1 in [start, end]:
                for item in items:
                    item.setBackground(QBrush(QColor('red')))
            else:
                for item in items:
                    item.setBackground(QBrush(QColor('yellow')))
        if self.current_hover != [row, col]:
            if old_start != -1 and old_end != -1:
                for idx in range(old_start, old_end + 1):
                    i, j = idx // self.SD.n, idx % self.SD.n
                    mdl = self.tableView_bitmap.model()
                    mdl.item(i, j).setBackground(QBrush(QColor('red')))
            if start != -1 and end != -1:
                for idx in range(start, end + 1):
                    i, j = idx // self.SD.n, idx % self.SD.n
                    mdl = self.tableView_bitmap.model()
                    mdl.item(i, j).setBackground(QBrush(QColor('yellow')))
            if old_start == -1 or old_end == -1:
                pass
        self.current_hover = [row, col]

    def show_msg(self, qModelIndex):
        msg = self.SD.messages[qModelIndex.row()]
        QMessageBox.warning(self, "警告", msg, QMessageBox.Ok | QMessageBox.No)

    def update_ui(self):
        # 更新UI
        # 设置数据
        self.data_to_ui()

    def reset(self):
        # 清除磁盘和文件信息
        self.SD.reset()
        self.update_ui()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow(blocks=500, size_per_block=2)
    myWin.show()
    sys.exit(app.exec_())
