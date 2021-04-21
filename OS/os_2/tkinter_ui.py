import random
from typing import List
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import copy


class Processor(object):
    """单个进程类"""

    def __init__(self, name, arrive_time, serve_time):
        """
        初始化进程
        :param name: 进程名称（ID）
        :param arrive_time: 到达时间
        :param serve_time: 服务时间
        """
        assert arrive_time >= 0, "到达时间不能为负数"
        assert serve_time > 0, "服务时间需要大于0"
        self.is_done = False
        self.have_been_run = False
        self.priority = 0  # 优先级，浮点数，根据大小判断
        self.name = name  # 进程名
        self.first_exe_time = 0  # 第一次执行时间
        self.arrive_time = arrive_time  # 到达时刻
        self.serve_time = serve_time  # 进程总服务时间
        self.exe_records = []

        self.start_time = 0  # 本次运行开始时刻
        self.end_time = 0  # 本次运行结束时刻

        self.used_time = 0  # 已经运行了多少时间（总长是服务时间）
        self.rest_time = self.serve_time  # 还有多少要运行
        self.period = 0  # 周转时间
        self.weight_period = 0  # 带权周转时间
        self.output_info = ()  # 输出信息
        self.basis_info = (self.name, self.arrive_time, self.serve_time)  # 进程基本信息

    def process(self, current_time, limit_time=-1) -> int:
        """
        进程运行，从current_time开始，返回结束时间
        如果有时间片限制limit_time，返回有时间片的结束时间

        :param current_time: 当前时间
        :param limit_time: 时间片长度
        :return: 结束时间
        """
        # 记录第一次运行的时间
        if not self.have_been_run:
            self.first_exe_time = current_time
            self.have_been_run = True
        self.start_time = current_time

        # 当limit_time 小于等于0，则没有时间片限制，全部完成
        if limit_time <= 0:
            self.used_time = self.serve_time
            self.rest_time = 0
            self.end_time = self.start_time + self.serve_time
            self.period = self.end_time - self.arrive_time
            self.weight_period = round(self.period / self.serve_time, 5)
            self.__set_output()
            self.is_done = True
        # 否则，只能在limit_time中完成有限的部分
        else:
            # 如果剩下的能在一个时间片完成，就全部完成，提前结束
            if self.rest_time <= limit_time:
                self.used_time = self.serve_time
                self.end_time = self.start_time + self.rest_time
                self.rest_time = 0
                self.__set_output()
                self.is_done = True
            # 否则，完成一部分，不设置结束标志
            else:
                self.used_time += limit_time
                self.rest_time -= limit_time
                self.end_time = self.start_time + limit_time
                self.period = self.end_time - self.arrive_time
                self.weight_period = round(self.period / self.serve_time, 5)

        self.exe_records.append((self.name, self.start_time, self.end_time))
        return self.end_time

    def __set_output(self):
        self.output_info = (self.name, self.arrive_time, self.serve_time, self.first_exe_time,
                            self.end_time, self.period, self.weight_period)


class Scheduling(object):
    """调度"""

    def __init__(self, processors_nums=5, is_random=True, arrive=None, serve=None):
        self.processors_nums = 0  # 总进程数
        self.processors: List[Processor] = []  # 进程列表
        self.processors_bkp = []  # 进程列表的备份
        self.output_infos = []  # 调度后的输出信息
        self.basis_infos = []  # 基本信息
        self.time_records = []
        self.time_slice = 1
        if is_random:
            self.random_produce(processors_nums)
        else:
            self.input_data(arrive, serve)

    def input_data(self, arrive: List[int], serve: List[int]):
        """
        根据到达时间列表和服务时间列表生成输入数据
        :param arrive: 到达时间列表
        :param serve: 服务时间列表
        :return: None
        """
        self.processors_nums = len(arrive)
        self.processors.clear()
        self.basis_infos.clear()
        for i in range(self.processors_nums):
            name = chr(ord('A') + i)
            arrive_time = arrive[i]
            serve_time = serve[i]
            processor = Processor(name, arrive_time, serve_time)
            self.processors.append(processor)
            self.basis_infos.append(processor.basis_info)
        self.processors_bkp = copy.deepcopy(self.processors)
        self.output_infos.clear()

    def random_produce(self, nums):
        """随机生成进程
            nums: 进程数量"""
        assert 26 >= nums >= 1, "随机生成的进程数在1-26之间，更多进程需手动输入"
        self.processors_nums = nums
        self.processors.clear()
        self.basis_infos.clear()
        for i in range(nums):
            name = chr(ord('A') + i)
            arrive_time = random.randint(0, 10)
            serve_time = random.randint(1, 10)
            processor = Processor(name, arrive_time, serve_time)
            self.processors.append(processor)
            self.basis_infos.append(processor.basis_info)
        self.processors_bkp = copy.deepcopy(self.processors)
        self.output_infos.clear()

    def schedule(self, option: str):
        print("调度方法" + option)
        if option == "FCFS":
            self.__fcfs()
        elif option == "RR":
            self.__rr(self.time_slice)
        elif option == "SJF":
            self.__sjf()
        else:
            self.__hrn()

    def __fcfs(self):
        """先来先到服务FCFS"""
        # 首先按照到达时间排序
        self.processors.sort(key=lambda p: p.arrive_time)
        current_time = 0
        for processor in self.processors:
            current_time = max(current_time, processor.arrive_time)
            current_time = processor.process(current_time)
            self.output_infos.append(processor.output_info)

    def __rr(self, time_slice=1):
        """
        时间轮转算法
        :param time_slice: 时间片长度
        :return: None
        """
        ready = self.processors
        ready.sort(key=lambda p: p.arrive_time)
        current_time = ready[0].arrive_time
        temp = []
        while ready:
            p = ready.pop(0)
            current_time = p.process(current_time, time_slice)
            if p.is_done:
                temp.append(p)
                self.output_infos.append(p.output_info)
            else:
                ready.append(p)
        self.processors = temp

    def __sjf(self):
        temp = [] # 为确保进程顺序的辅助数组

        # 先按到达时间排序
        ready = sorted(self.processors, key=lambda p: p.arrive_time)
        # 系统初始时间为 第一个进程到达时间
        start_time = ready[0].arrive_time

        # 循环n-1次，最后一个进程单独处理
        for i in range(len(ready) - 1):
            # 执行该进程
            end_time = ready[i].process(start_time)
            start_time = end_time
            temp.append(ready[i])
            # ps 是该在进程到达之后 且在该进程结束之前 到达的进程列表
            ps = [p for p in ready[i + 1:] if p.arrive_time <= end_time]
            # 按服务时间排序，因为SJF算法，短进程优先
            ps.sort(key=lambda p: p.serve_time)
            ready = ready[:i + 1] + ps + ready[i + len(ps) + 1:]
            # 如果PS列表为空，那说明该进程运行结束之后，下一个进程才到达，此时是正常的先来先到
            # 系统时间设置为 下一个的到达时间，准备下一个进程的执行
            if len(ps) == 0:
                start_time = ready[i + 1].arrive_time
            self.output_infos.append(ready[i].output_info)
        # 剩下最后一个进程，执行
        ready[-1].process(start_time)
        temp.append(ready[-1])
        self.output_infos.append(ready[-1].output_info)
        self.processors = temp

    def __hrn(self):
        temp = []
        ready_bkp: List[Processor] = sorted(self.processors, key=lambda p: p.arrive_time)
        ready: List[Processor] = []
        start_time = ready_bkp[0].arrive_time
        current_time = start_time
        #  计算优先权
        ready.append(ready_bkp.pop(0))
        while ready:
            current_time = ready[0].process(current_time)
            temp.append(ready[0])
            while ready_bkp and ready_bkp[0].arrive_time < current_time:
                ready.append(ready_bkp.pop(0))
            # 每执行完一个进程，根据等待时间，计算所有的进程的优先级，并按优先级排序
            for p in ready[1:]:
                wait_time = current_time - p.arrive_time
                p.priority = (wait_time + p.serve_time) / p.serve_time
            # 收集队首进程数据
            self.output_infos.append(ready[0].output_info)
            # 去除队首进程（已完成），且将后续已到达进程按优先级排序
            ready = sorted(ready[1:], key=lambda p: p.priority, reverse=True)
        self.processors = temp

    def reset(self):
        """调度的进程不变，重新设置，使其可以用其他的调度方法"""
        # 到达时间恢复
        arrive = [p.arrive_time for p in self.processors_bkp]
        # 服务时间恢复
        serve = [p.serve_time for p in self.processors_bkp]
        self.input_data(arrive, serve)


class GUI:
    """
    图形用户界面
    """
    # 静态界面结构
    scheduling = None
    root = tk.Tk()
    headings_schedule = ["进程名", "到达时间", "服务时间", "首次运行时间", "完成时间", "周转时间", "带权周转时间"]
    headings_basis = ["进程名", "到达时间", "服务时间"]
    colors = []

    frame_0 = ttk.Frame(root, height=200, width=200)
    input_panel = ttk.Frame(frame_0)
    input_array: List[ttk.Frame] = []
    table_basis = ttk.Treeview(frame_0, show="headings")

    frame_1 = ttk.Frame(root)
    label_pro_nums = ttk.Label(frame_1, text="进程数目")
    entry_pro_nums_default = tk.StringVar(value="5")
    entry_pro_nums = ttk.Entry(frame_1, textvariable=entry_pro_nums_default, width=20)
    btn_pro_nums = ttk.Button(frame_1, text="随机设置进程")
    btn_get_data_console = ttk.Button(frame_1, text="输入进程数据（控制台）")
    frame_1_1 = ttk.Frame(frame_1)
    label_method = ttk.Label(frame_1_1, text="选择调度方式")
    values_cmb_method = ["FCFS", "RR", "SJF", "HRN"]
    cmb_method = ttk.Combobox(frame_1_1)
    entry_time_slice_default = tk.StringVar(value='1')
    entry_time_slice = ttk.Entry(frame_1_1, textvariable=entry_time_slice_default, width=10)
    btn_run = ttk.Button(frame_1, text="调度")

    # 调度表格
    frame_2 = ttk.Frame(root)
    table_schedule = ttk.Treeview(frame_2, show="headings")
    # pie_schedule = None

    # 折线图
    frame_3 = ttk.Frame(root, height=100, width=100)
    canvas_line = tk.Canvas(frame_3)
    figure_line = plt.figure(num=2, figsize=(8, 4))
    subp_line = figure_line.add_subplot(1, 1, 1)

    btn_reset = ttk.Button(frame_3, text="重置")

    # 扇形图
    frame_4 = ttk.Frame(root)
    canvas_schedule = tk.Canvas(frame_4, height=500, width=500)
    figure_schedule = plt.figure(figsize=(4, 4), dpi=80, edgecolor='green', frameon=True)
    subps_schedule = [figure_schedule.add_subplot(1, 3, 1), figure_schedule.add_subplot(1, 3, 2),
                      figure_schedule.add_subplot(1, 3, 3)]

    @classmethod
    def start(cls):
        cls.scheduling = Scheduling()
        cls.init_input()
        cls.root.title("调度模拟程序")
        cls.root.protocol("WM_DELETE_WINDOW", cls.quit)
        cls.root.geometry("800x1000")

        # 创建固定的原进程表格
        cls.table_basis["columns"] = tuple(list(range(len(cls.headings_basis))))
        for i, heading in enumerate(cls.headings_basis):
            cls.table_basis.column(i, width=100, anchor="center")
            cls.table_basis.heading(i, text=heading)
        for i, item in enumerate(cls.scheduling.basis_infos):
            cls.table_basis.insert("", i, str(i), values=item)
        # 创建动态变化的调度结果表格
        cls.table_schedule["columns"] = tuple(list(range(len(cls.headings_schedule))))
        for i, heading in enumerate(cls.headings_schedule):
            cls.table_schedule.column(i, width=100, anchor="center")
            cls.table_schedule.heading(i, text=heading)

        # 操作面板0
        cls.frame_0.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        cls.table_basis.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # cls.input_panel.pack(side=tk.LEFT)

        # 创建操作面板1
        cls.frame_1.pack(side=tk.TOP, anchor=tk.N, expand=tk.NO)
        cls.label_pro_nums.pack(side=tk.LEFT)
        cls.entry_pro_nums.pack(side=tk.LEFT)
        cls.btn_pro_nums["command"] = cls.set_data_random
        cls.btn_pro_nums.pack(side=tk.LEFT)
        cls.btn_get_data_console.pack(side=tk.LEFT)
        cls.btn_get_data_console["command"] = cls.get_data_from_console
        cls.frame_1_1.pack(side=tk.LEFT)
        cls.label_method.pack(side=tk.LEFT)
        cls.cmb_method["values"] = cls.values_cmb_method
        cls.cmb_method.set(cls.values_cmb_method[0])
        cls.cmb_method.pack(side=tk.LEFT)
        cls.cmb_method.config(state='readonly')
        cls.cmb_method.bind("<<ComboboxSelected>>", cls.on_cmb_change)
        cls.btn_run["command"] = cls.run
        cls.btn_run.pack(side=tk.LEFT, anchor=tk.E)

        # 面板3 运行重置
        cls.frame_3.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        cls.canvas_line = FigureCanvasTkAgg(cls.figure_line, cls.frame_3)
        cls.canvas_line.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

        # 创建操作面板2（图像）
        cls.frame_2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        cls.table_schedule.pack(side=tk.TOP, fill=tk.X)
        #
        # cls.canvas_schedule = FigureCanvasTkAgg(cls.figure_schedule, cls.frame_2)
        # cls.canvas_schedule.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

        cls.root.mainloop()

    @classmethod
    def run(cls):
        """开始调度"""
        cls.scheduling.reset()
        cls.set_time_slice()
        cls.scheduling.schedule(cls.cmb_method.get())
        cls.update_ui()

    @classmethod
    def set_data_random(cls):
        """随机设置进程"""
        num = int('0' + cls.entry_pro_nums.get())
        cls.scheduling.random_produce(num)
        cls.run()
        print("随机重新设置进程")

    @classmethod
    def set_time_slice(cls):
        """设置时间片"""
        num = int('0' + cls.entry_time_slice.get())
        cls.scheduling.time_slice = num
        print("设置时间片长度：", num)

    @classmethod
    def on_cmb_change(cls, event):
        """当算法下拉框的值变化"""
        value = cls.cmb_method.get()
        if value == "RR":
            print("rr算法，时间片选项开启")
            cls.entry_time_slice.pack(side=tk.LEFT)
            cls.set_time_slice()
        else:
            print("非时间片算法，输入框无效")
            cls.entry_time_slice.pack_forget()

    @classmethod
    def update_ui(cls):
        """根据当前数据，更新UI界面"""
        # 设置原表格数值
        for i in cls.table_basis.get_children():
            cls.table_basis.delete(i)
        for i, item in enumerate(cls.scheduling.basis_infos):
            cls.table_basis.insert("", i, str(i), values=item)

        # 设置调度表格
        index = 0
        cls.scheduling.output_infos.sort(key=lambda i: i[1])
        for i in cls.table_schedule.get_children():
            cls.table_schedule.delete(i)
        for i, item in enumerate(cls.scheduling.output_infos):
            cls.table_schedule.insert("", i, str(i), values=item)
            index = i
        cls.table_schedule.insert("", index+1, str(index+1), values=[""]*7)
        cls.table_schedule.insert("", index+2, str(index+2), values=[""]*7)
        cls.table_schedule.insert("", index+3, str(index+3), values=[""]*5+["平均周转时间", "平均加权周转时间"])
        avg_period = sum([p.period for p in cls.scheduling.processors]) / cls.scheduling.processors_nums
        avg_weight_period = sum([p.weight_period for p in cls.scheduling.processors]) / cls.scheduling.processors_nums
        cls.table_schedule.insert("", index+4, str(index+4), values=[""]*5+[str(avg_period), str(avg_weight_period)])

        # 重新绘图
        # for subps in cls.subps_schedule:
        #     subps.cla()
        # data_0 = [p.period for p in cls.scheduling.processors]
        # data_1 = [p.weight_period for p in cls.scheduling.processors]
        # # 创建一副子图
        # els = [p.name for p in sorted(cls.scheduling.processors, key=lambda p: p.name)]
        # cls.subps_schedule[0].pie(data_0, labels=els)
        # cls.subps_schedule[0].legend(loc='best')
        # cls.subps_schedule[1].pie(data_1)
        # cls.canvas_schedule.draw()

        ps = sorted(cls.scheduling.processors, key=lambda p: p.first_exe_time)
        cls.plot_piecewise_func(ps)
        cls.canvas_line.draw()

    @classmethod
    def plot_piecewise_func(cls, ps: List[Processor]):
        """绘制调度图"""
        cls.subp_line.cla()
        cls.subp_line.invert_yaxis()
        # els = [p.name for p in sorted(cls.scheduling.processors, key=lambda p: p.name)]
        el = [p.name for p in ps]
        ymax = []
        time_seq = []
        for num, p in enumerate(ps):
            # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
            x = np.linspace(0, 100, 1000)
            starts = [rec[1] for rec in p.exe_records]
            ends = [rec[2] for rec in p.exe_records]
            intervals = np.array([[1 if s <= i < e else 0 for i in x] for s, e in zip(starts, ends)])
            intervals = np.nansum(intervals, axis=0)
            intervals = np.where(intervals==0, np.nan, intervals)
            y = (num+1) * intervals
            for i, [s, e] in enumerate(zip(starts, ends)):
                time_seq += [s, e]
                ymax += [num+1]*2
            cls.subp_line.step(x, y)
        cls.subp_line.vlines(time_seq, [0]*5, ymax, linestyles="dotted")
        cls.subp_line.legend(labels=el, loc='best')

    @classmethod
    def init_input_panel(cls, num=5):
        cls.input_array.clear()
        for i in range(num):
            temp_frame = ttk.Frame(cls.input_panel)
            entry_0 = ttk.Entry(temp_frame)
            entry_1 = ttk.Entry(temp_frame)
            temp_frame.pack(side=tk.TOP)
            entry_0.pack(side=tk.LEFT)
            entry_1.pack(side=tk.LEFT)
            cls.input_array.append(temp_frame)

    @classmethod
    def init_input(cls):
        arrive = [0, 10, 12, 3, 4]
        serve = [4, 3, 5, 2, 4]
        arrive = [0, 20, 20, 30, 35]
        serve = [25, 20, 10, 20, 15]
        cls.scheduling.input_data(arrive, serve)

    @classmethod
    def get_data_from_console(cls):
        """通过控制台输入进程信息"""
        cls.scheduling.processors_nums = int(input("输入进程数（名称自动从A生成）："))
        arrive = []
        server = []
        for i in range(cls.scheduling.processors_nums):
            a, s = map(float, input("输入" + chr(ord('A') + i) + "进程的到达时间和服务时间，用空格隔开：").split())
            arrive.append(a)
            server.append(s)
        print("输入完成，切换到显示界面，点击调度按钮进行调度")
        cls.scheduling.input_data(arrive, server)

    @classmethod
    def quit(cls):
        """退出程序"""
        cls.root.quit()
        cls.root.destroy()


if __name__ == '__main__':
    GUI.start()
