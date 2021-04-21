import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui_mainwindow import *
from replace import PageReplacement as Pr


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, pages=None, size=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_replace.clicked.connect(self.replace)
        if pages:
            self.lineEdit_page_seq.setText(pages)
        if size:
            self.lineEdit_size.setText(size)

    def replace(self):
        # 绑定按钮函数
        pages = self.lineEdit_page_seq.text()
        swap_size = self.lineEdit_size.text()
        pages = [int(page) for page in pages.split()]
        swap_size = [int(s) for s in swap_size.split()][0]
        fifo_results = Pr.replace(pages, 'fifo', swap_size)
        lru_results = Pr.replace(pages, 'lru', swap_size)
        self.update_by(fifo_results, lru_results)

    def update_by(self, fifo_results, lru_results):
        """根据两个运行结果更新UI"""
        self.set_text(self.textEdit_fifo, fifo_results)
        self.set_text(self.textEdit_lru, lru_results)
        self.set_table(self.tableView_fifo, fifo_results)
        self.set_table(self.tableView_lru, lru_results)

    def set_text(self, text_edit: QTextEdit, results):
        """设置统计信息"""
        st, dp, lt = results
        lack_rate = lt / len(st) # 缺页率
        string = '缺页率：' + str(lack_rate) + '\n\n缺页次数：' + str(lt) + \
                 '\n\n淘汰页：' + str(dp)
        text_edit.setPlainText(string)

    def set_table(self, table: QTableView, results):
        """设置表格信息"""
        status, dp, lt = results
        status = list(map(list, zip(*status)))  # 转置，一列为某一时刻的变化
        model = QStandardItemModel(len(status), len(status[0]))
        model.setHorizontalHeaderLabels([str(i) for i in range(len(status))])
        for row in range(len(status)):
            print(status[row])
            for col in range(len(status[0])):
                v = "" if status[row][col] == -1 else str(status[row][col])
                model.setItem(row, col, QStandardItem(str(v)))
        table.setModel(model)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initial_pages = "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1"
    initial_size = "3"
    myWin = MyWindow(pages=initial_pages, size=initial_size)
    myWin.show()
    sys.exit(app.exec_())
