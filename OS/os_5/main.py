#  bug:
#  ----1. 横向移动，高光会消失
#  ----2. messagebox一次触发会出现多个
# 3. 颜色不会变回去
# 5. 回收算法
from typing import List

from freespace import SimulatedFile, SimulatedDisk
import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_mainwindow import *


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, blocks, size_per_block, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.SD = SimulatedDisk(blocks, size_per_block, m=25, n=20)
        self.last_hover = [-1, -1]
        self.simulated_files = []
        self.random_one = []
        self.temp_files = []
        self.done = [False] * 3
        self.init_ui()

    def init_ui(self):
        # 设置信号和槽
        self.tableWidget_files.setMouseTracking(True)
        self.tableWidget_files.cellEntered.connect(self.highlight)
        self.pushButton_run.clicked.connect(self.run)
        self.pushButton_reset.clicked.connect(self.reset)

        # 设置样式
        self.tableWidget_files.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_files.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_files.verticalHeader().setVisible(False)
        self.tableWidget_files.setEditTriggers(QTableWidget.NoEditTriggers)

        self.tableWidget_bitmap.setColumnCount(self.SD.n)
        self.tableWidget_bitmap.setRowCount(self.SD.m)
        self.tableWidget_bitmap.setHorizontalHeaderLabels([str(i) for i in range(self.SD.n)])
        self.tableWidget_bitmap.setVerticalHeaderLabels([str(i) for i in range(self.SD.m)])
        self.tableWidget_bitmap.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_bitmap.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_bitmap.setEditTriggers(QTableView.NoEditTriggers)
        # self.tableWidget_bitmap.verticalHeader().setVisible(False)
        # self.tableWidget_bitmap.horizontalHeader().setVisible(False)

        self.update_ui()

    def run(self):
        index = self.comboBox_op.currentIndex()
        if 0 == index:
            self.reset()
            self.random_50_files()
            self.done[0] = True
        elif 1 == index and self.done[0]:
            self.delete_odd()
            self.done[1] = True
        elif self.done[0]:
            self.add_new_files()
        self.update_ui()
        self.plot(self.temp_files, 'blue')

    def random_50_files(self):
        num = 50
        ids = list(range(num))
        exist_ids = frozenset([sf.id for sf in self.simulated_files])  # 去重
        ids = [id for id in ids if id not in exist_ids]
        names = [str(id + 1) + '.txt' for id in ids]
        sizes = [round(random.uniform(2, 10), 2) for i in range(num)]
        new_files = [SimulatedFile(id, name, size) for id, name, size in zip(ids, names, sizes)]
        self.simulated_files += new_files
        self.SD.store_files(self.simulated_files)

    def delete_odd(self):
        odd_names = [sf.name for sf in self.SD.files if sf.id % 2 != 0]
        self.SD.delete_files(odd_names)

    def add_new_files(self):
        cur_id = max([sf.id for sf in self.simulated_files])
        ids = list(range(cur_id + 1, cur_id + 6))
        exist_ids = frozenset([sf.id for sf in self.simulated_files])  # 去重
        ids = [id for id in ids if id not in exist_ids]
        print(ids)
        names = [chr(ord('A') + i) + '.txt' for i in range(5)]
        sizes = [7, 5, 2, 9, 3.5]
        new_files = [SimulatedFile(id, name, size) for id, name, size in zip(ids, names, sizes)]
        self.temp_files = new_files
        self.simulated_files = self.simulated_files + new_files
        self.SD.store_files(new_files)

    def random(self, is_set=True):
        if is_set:
            self.random_one = [random.randint(0, 999) for i in range(1000)]
            for idx in self.random_one:
                i, j = idx // self.SD.n, idx % self.SD.n
                self.SD.bitmap[i][j] = True
                self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor(0, 0, 255)))
        else:
            for idx in self.random_one:
                i, j = idx // self.SD.n, idx % self.SD.n
                self.SD.bitmap[i][j] = False
                self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor(255, 0, 0)))

    def update_ui(self):
        # print("更新前")
        # 更新文件列表
        files = self.simulated_files
        self.tableWidget_files.setColumnCount(5)
        self.tableWidget_files.setRowCount(len(files))
        self.tableWidget_files.setHorizontalHeaderLabels(["ID", "文件名", "大小(k)", "起始", "终止"])
        for row, file in enumerate(files):
            for col, value in enumerate(file.get()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                self.tableWidget_files.setItem(row, col, item)

        self.last_color = QColor('red')
        # 更新位示图
        bm = self.SD.bitmap
        self.tableWidget_bitmap.hide()
        for i in range(len(bm)):
            for j in range(len(bm[0])):
                v = 1 if bm[i][j] else 0
                self.tableWidget_bitmap.setItem(i, j, QTableWidgetItem(str(v)))
                if v == 1:
                    self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor(255, 0, 0)))
                else:
                    self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor(0, 255, 0)))
        self.tableWidget_bitmap.show()
        # 显示随机
        # for idx in self.ramdom_one:
        #     i, j = idx // self.SD.n, idx % self.SD.n
        #     self.tableView_bitmap.model().item(i, j).setBackground(QBrush(QColor(0, 0, 255)))
        # print("更新后")

    def highlight(self, row, col):
        """突出显示"""
        print("current cursor: ", row, col)
        files = self.simulated_files
        old_start = files[self.last_hover[0]].start_pos
        old_end = files[self.last_hover[0]].end_pos
        old_items = [self.tableWidget_files.item(self.last_hover[0], i) for i in range(5)]
        start = files[row].start_pos
        end = files[row].end_pos
        items = [self.tableWidget_files.item(row, i) for i in range(5)]

        if self.last_hover[0] != row: # 上次位置和当前位置的行不一样，发生改变
            # 更改文件列表UI
            # 旧的文件项设为白色
            for old_item in old_items:
                old_item.setBackground(QBrush(QColor('white')))
            if -1 in [start, end]:
                # 如果没分配，就是橙色
                for item in items:
                    item.setBackground(QBrush(QColor('orange')))
            else:  # 分配了就是黄色
                for item in items:
                    item.setBackground(QBrush(QColor('yellow')))

            # 更改位示图
            if -1 not in [old_start, old_end]:
                # 把离开的位置设置为其旧颜色
                for idx in range(old_start, old_end + 1):
                    i, j = idx // self.SD.n, idx % self.SD.n
                    self.tableWidget_bitmap.item(i, j).setBackground(QBrush(self.last_color))
            if -1 not in [start, end]:
                # 如果分配了，记录旧颜色, 设置为黄色
                i, j = start // self.SD.n, start % self.SD.n
                self.last_color = self.tableWidget_bitmap.item(i, j).background().color()
                for idx in range(start, end + 1):
                    i, j = idx // self.SD.n, idx % self.SD.n
                    self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor("yellow")))
        self.last_hover = [row, col]

    def plot(self, files: List[SimulatedFile], color):
        for f in files:
            start = f.start_pos
            end = f.end_pos
            for b in range(start, end + 1):
                i, j = b // self.SD.n, b % self.SD.n
                self.tableWidget_bitmap.item(i, j).setBackground(QBrush(QColor(color)))

    def reset(self):
        # 清除磁盘和文件信息
        self.simulated_files.clear()
        self.random_one.clear()
        self.temp_files.clear()
        self.last_hover = [0, 0]
        self.last_color = QColor("red")
        self.SD.reset()
        self.done = [False] * 3
        self.update_ui()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow(blocks=500, size_per_block=2)
    myWin.show()
    sys.exit(app.exec_())
