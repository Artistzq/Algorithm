from disk_scheduling import Scheduling
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from ui_mainwindow import *


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, sequence=None, start=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_schedule.clicked.connect(self.schedule)
        self.comboBox_alg.currentIndexChanged.connect(self.on_combobox_change)
        self.checkBox_is_greater.setVisible(False)
        if sequence:
            self.lineEdit_seq.setText(sequence)
        if start:
            self.lineEdit_start.setText(start)

    def on_combobox_change(self):
        if self.comboBox_alg.currentIndex() == 2:
            # scan算法
            self.checkBox_is_greater.setVisible(True)
        else:
            self.checkBox_is_greater.setVisible(False)

    def schedule(self):
        sequence = self.lineEdit_seq.text()
        start = self.lineEdit_start.text()
        sequence = [int(item) for item in sequence.split()]
        start = [int(item) for item in start.split()][0]
        if self.comboBox_alg.currentIndex() == 0:
            result = Scheduling.fcfs(start, sequence)
        elif self.comboBox_alg.currentIndex() == 1:
            result = Scheduling.sstf(start, sequence)
        elif self.comboBox_alg.currentIndex() == 2:
            outward = self.checkBox_is_greater.isChecked()
            result = Scheduling.scan(start, sequence, outward)
        else: pass
        self.label_header.setText(self.comboBox_alg.currentText())
        self.update_by(result)

    def update_by(self, result):
        access, move, avg = result
        model = QStandardItemModel(len(access) + 1, 2)
        model.setHorizontalHeaderLabels(["磁道号", "寻道距离"])
        for row in range(len(access)):
            for col in range(2):
                item = QStandardItem(str(result[col][row]))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                model.setItem(row, col, item)
        item = QStandardItem("平均寻道长度："+str(avg))
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
        model.setItem(len(access), 0, item)
        self.tableView_result.setModel(model)
        self.tableView_result.setSpan(len(access), 0, 1, 2)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_result.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_result.setEditTriggers(QTableView.NoEditTriggers)
        self.tableView_result.verticalHeader().setVisible(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initial_pages = "55 58 39 18 90 160 150 38 184"
    initial_size = "100"
    myWin = MyWindow(sequence=initial_pages, start = initial_size)
    myWin.show()
    sys.exit(app.exec_())
