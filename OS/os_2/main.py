from schedule import Scheduling
from ui_mainwindow import *

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, arrive=None, service=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        if arrive:
            self.lineEdit_arrive.setText(arrive)
        if service:
            self.lineEdit_service.setText(service)
        self.s = Scheduling()
        self.pushButton_random.clicked.connect(self.set_random)
        self.comboBox_method.currentIndexChanged.connect(self.on_combobox_change)
        self.pushButton_schedule.clicked.connect(self.schedule)
        self.lineEdit_random.setText("5")
        self.lineEdit_time_slice.setText("1")
        self.on_combobox_change()
        # 图表
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        # toolbar = NavigationToolbar(self.fig, self)
        self.widget_plot.setLayout(QVBoxLayout())
        self.widget_plot.layout().addWidget(self.canvas)

    def schedule(self):
        method = self.comboBox_method.currentIndex()
        arrive = self.lineEdit_arrive.text()
        service = self.lineEdit_service.text()
        arrive = [int(item) for item in arrive.split()]
        service = [int(item) for item in service.split()]
        self.s.set_process(len(arrive), arrive=arrive, service=service)
        if method == 1:
            self.set_time_slice()
        self.s.schedule(method)
        self.set_ui()

    def on_combobox_change(self):
        """选择算法变动"""
        if self.comboBox_method.currentIndex() == 1:
            # RR算法
            self.frame_time_slice.setEnabled(True)
        else:
            self.frame_time_slice.setEnabled(False)

    def set_time_slice(self):
        """设置时间片"""
        ts = self.lineEdit_time_slice.text()
        if ts == "":
            self.qm("未输入时间片长度")
            return
        if not ts.isdigit():
            self.qm("输入数字")
            return
        ts = [int(item) for item in ts.split()][0]
        self.s.set_time_slice(ts)

    def set_ui(self):
        self.tableWidget_process.setRowCount(6)
        self.tableWidget_process.setColumnCount(1 + len(self.s.completed))

        results = self.s.get()
        vertical_head = ["进程名", "到达时间", "服务时间", "完成时间", "周转时间", "带权周转时间"]
        self.tableWidget_process.setVerticalHeaderLabels(vertical_head)
        self.tableWidget_process.horizontalHeader().setVisible(False)
        self.tableWidget_process.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_process.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_process.setEditTriggers(QTableWidget.NoEditTriggers)
        for col, result in enumerate(results):
            for row, it in enumerate(result):
                item = QTableWidgetItem(str(it))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                self.tableWidget_process.setItem(row, col, item)
        avg_period = sum([result[4] for result in results]) / len(results)
        avg_w_period = sum([result[5] for result in results]) / len(results)
        statistic = ["平均", "", "", "", str(avg_period), str(avg_w_period)]
        for row, s in enumerate(statistic):
            item = QTableWidgetItem(s)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
            self.tableWidget_process.setItem(row, len(results), item)
        self.plot_piecewise_func(self.s.completed)

    def set_random(self):
        num = self.lineEdit_random.text()
        num = [int(item) for item in num.split()][0]
        self.s.set_process(num)
        arrive = " ".join([str(p.arrive_time) for p in self.s.processors])
        service = " ".join([str(p.service_time) for p in self.s.processors])
        self.lineEdit_arrive.setText(arrive)
        self.lineEdit_service.setText(service)

    def qm(self, s):
        # QMessageBox.information()
        print(s)

    def plot_piecewise_func(self, ps):
        """绘制调度图"""
        self.fig.clf()
        ax = self.fig.subplots(1, 1)
        labels = [p.name for p in ps]
        ymax = []
        time_seq = []
        max_time = max([p.end_time for p in ps]) + 1
        for num, p in enumerate(ps):
            x = np.linspace(0, max_time, 1000)
            starts = [rec[1] for rec in p.exe_records]
            ends = [rec[2] for rec in p.exe_records]
            intervals = np.array([[1 if s <= i < e else 0 for i in x] for s, e in zip(starts, ends)])
            intervals = np.nansum(intervals, axis=0)
            intervals = np.where(intervals == 0, np.nan, intervals)
            y = (num + 1) * intervals
            for i, [s, e] in enumerate(zip(starts, ends)):
                time_seq += [s, e]
                ymax += [num + 1] * 2
            ax.step(x, y)
        ax.vlines(time_seq, [0] * len(ymax), ymax, linestyles="dotted")
        ax.legend(labels=labels, loc='best')
        ax.invert_yaxis()
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    init_arrive = "0 1 2 3 4"
    init_service = "4 3 4 2 4"
    myWin = MyWindow(arrive=init_arrive, service=init_service)
    myWin.show()
    sys.exit(app.exec_())
