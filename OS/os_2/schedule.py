import random
import string
import copy
from typing import List


class Processor(object):
    """单个进程类"""

    def __init__(self, name, arrive_time, service_time):
        """
        初始化进程
        :param name: 进程名称（ID）
        :param arrive_time: 到达时间
        :param service_time: 服务时间
        """
        assert arrive_time >= 0, "到达时间不能为负数"
        assert service_time > 0, "服务时间需要大于0"
        self.is_done = False  # 是否已经全部完成
        self.have_been_run = False  # 是否被运行过
        self.priority = 0  # 优先级，浮点数，根据大小判断
        self.name = name  # 进程名
        self.first_exe_time = 0  # 第一次执行时间
        self.arrive_time = arrive_time  # 到达时刻
        self.service_time = service_time  # 进程总服务时间
        self.exe_records = []  # 执行记录，记录每一次的开始时间和结束时间

        self.start_time = 0  # 本次运行开始时刻
        self.end_time = 0  # 本次运行结束时刻，此2项记录到exe_records里

        self.used_time = 0  # 已经运行了多少时间（总长是服务时间）
        self.rest_time = self.service_time  # 还有多少要运行
        self.period = 0  # 周转时间
        self.weight_period = 0  # 带权周转时间
        self.basis_info = [self.name, self.arrive_time, self.service_time]  # 进程基本信息

    def process(self, current_time, limit_time=-1) -> int:
        """
        进程运行，从current_time开始，返回结束时间
        如果有时间片限制limit_time，返回有时间片的结束时间

        :param current_time: 当前时间
        :param limit_time: 时间片长度
        :return: 结束时间
        """
        # 如果还没运行过，记录第一次运行的时间
        if not self.have_been_run:
            self.first_exe_time = current_time
            self.have_been_run = True
        self.start_time = current_time

        # 当limit_time 小于等于0，则没有时间片限制，全部完成
        if limit_time <= 0:
            self.used_time = self.service_time
            self.rest_time = 0
            self.end_time = self.start_time + self.service_time
            self.period = self.end_time - self.arrive_time
            self.weight_period = round(self.period / self.service_time, 5)
            self.is_done = True
        # 否则，只能在limit_time中完成有限的部分
        else:
            # 如果剩下的能在一个时间片完成，就全部完成，提前结束
            if self.rest_time <= limit_time:
                self.used_time = self.service_time
                self.end_time = self.start_time + self.rest_time
                self.rest_time = 0
                self.period = self.end_time - self.arrive_time
                self.weight_period = round(self.period / self.service_time, 5)
                self.is_done = True
            # 否则，完成一部分，不设置结束标志
            else:
                self.used_time += limit_time
                self.rest_time -= limit_time
                self.end_time = self.start_time + limit_time
        # 记录运行，用于画图
        self.exe_records.append([self.name, self.start_time, self.end_time])
        return self.end_time

    def get(self):
        """返回进程信息"""
        return [self.name, self.arrive_time, self.service_time,
                self.end_time, self.period, self.weight_period]


class Scheduling(object):

    def __init__(self):
        self.processors: List[Processor] = []  # 进程列表
        self.completed: List[Processor] = []  # 完成队列
        self.processors_bkp: List[Processor] = []  # 备份，用于运行其他算法
        self.time_slice = 0

    def set_process(self, num=None, names=None, arrive=None, service=None):
        """
        根据传入的进程名、到达时间和服务时间设置进程列表
        :param num: 进程个数，若为空则随机
        :param names: 进程名列表，若位空则按顺序命令，超出则随机命名
        :param arrive: 到达时间列表，若为空则随机（0-10）
        :param service: 服务时间列表，若为空则随机（1-10）
        """
        if num is None:
            num = random.randint(0, 25)
        if names is None:
            names = [chr(ord('A') + i) for i in range(num)]
            if num > 25:
                for _ in range(25, num):
                    names.append(''.join(random.sample(
                        string.ascii_letters + string.digits, 6)))
        if arrive is None:
            arrive = [random.randint(0, 10) for _ in range(num)]
        if service is None:
            service = [random.randint(1, 10) for _ in range(num)]
        self.processors = [Processor(n, a, s) for n, a, s in zip(names, arrive, service)]
        self.processors_bkp = copy.deepcopy(self.processors)

    def set_time_slice(self, time_slice):
        """设置RR算法时间片长度"""
        self.time_slice = time_slice

    def reset(self):
        """重置进程列表，供其他算法调度测试"""
        self.processors = copy.deepcopy(self.processors_bkp)
        # print(self.processors, self.processors_bkp)
        self.completed.clear()

    def schedule(self, option: 0):
        """
        根据option选择算法进行进程调度
        :param option: 0:FCFS, 1:RR, 2:HRN, 3:SJF
        :return:
        """
        self.reset()
        assert len(self.processors) != 0, "未设置进程列表"
        if option == 0 or option == 'FCFS':
            self.__fcfs()
        elif option == 1 or option == 'RR':
            assert self.time_slice != 0, "未设置时间片长度"
            self.__rr(self.time_slice)
        elif option == 2 or option == 'HRN':
            self.__hrn()
        elif option == 3 or option == 'SJF':
            self.__sjf()

    def get(self, sort_by='arrive'):
        """
        返回完成进程的信息，按sort_by排序
        :param sort_by: 排序方法
        :return: 进程信息列表
        """
        if sort_by == 'arrive':
            self.completed.sort(key=lambda p: p.arrive_time)
        elif sort_by == 'id':
            self.completed.sort(key=lambda p: p.arrive_time)
        elif sort_by == 'first_exe':
            self.completed.sort(key=lambda p: p.first_exe_time)
        return [p.get() for p in self.completed]

    def __fcfs(self):
        """先来先服务"""
        # 进程队列按到达时间排序，按顺序执行
        self.processors.sort(key=lambda p: p.arrive_time)
        current_time = 0
        for processor in self.processors:
            # 迭代更新开始时间为：上一个进程的结束时间，和下一个进程的到达时间中，最大的那个
            current_time = max(current_time, processor.arrive_time)
            current_time = processor.process(current_time)
        # 设置完成队列
        self.completed = copy.deepcopy(self.processors)

    def __rr(self, time_slice):
        """轮转算法"""
        # 进程队列按到达时间排序
        self.processors.sort(key=lambda p: p.arrive_time)
        # 取出队首进程，加入就绪队列
        ready = [self.processors.pop(0)]
        # 开始时间为第一个进程的到达时间
        current_time = ready[0].arrive_time
        # 循环，直到就绪队列为空
        while ready:
            # 取出就绪列队的队首进程p
            p = ready.pop(0)
            # 设置当前时间为：当前时间和进程p的到达时间中的最大值
            current_time = max(current_time, p.arrive_time)
            # 以时间片time_slice，运行该进程，迭代当前时间
            current_time = p.process(current_time, time_slice)
            # 将进程队列中，到达时间比当前时间小（即在当前进程p运行的过程中到达）的进程，加入就绪队列
            ready = [p for p in self.processors if p.arrive_time <= current_time] + ready
            # 进程队列中去掉上述进程
            self.processors = [p for p in self.processors if p.arrive_time > current_time]
            # 如果就绪队列已空，且进程队列非空，则该进程p运行完后，下一个进程还没到达
            # 此时将进程队列队首加入就绪队列
            if not ready and self.processors:
                ready.append(self.processors.pop(0))
            # 如果进程p全部运行完，则加入完成队列
            if p.is_done:
                self.completed.append(p)
            # 否则，重新加入就绪队列，等待下一次轮转
            else:
                ready.append(p)

    def __hrn(self):
        """高响应比优先"""
        # 进程队列按到达时间排序
        self.processors.sort(key=lambda p: p.arrive_time)
        # 取出队首进程，加入就绪队列
        ready = [self.processors.pop(0)]
        # 开始时间为第一个进程的到达时间
        current_time = ready[0].arrive_time
        # 循环，直到就绪队列为空
        while ready:
            # 取出就绪列队的队首进程p
            p = ready.pop(0)
            # 设置当前时间为：当前时间和进程p的到达时间中的最大值
            current_time = max(current_time, p.arrive_time)
            # 以时间片time_slice，运行该进程，迭代当前时间
            current_time = p.process(current_time)
            # 运行完毕，将进程p直接加入完成队列
            self.completed.append(p)
            # 将进程队列中，到达时间比当前时间小（即在当前进程p运行的过程中到达）的进程，加入就绪队列
            ready += [p for p in self.processors if p.arrive_time <= current_time]
            # 进程队列中去掉上述进程
            self.processors = [p for p in self.processors if p.arrive_time > current_time]
            # 如果就绪队列已空，且进程队列非空，则该进程p运行完后，下一个进程还没到达
            # 此时将进程队列队首加入就绪队列
            if not ready and self.processors:
                ready.append(self.processors.pop(0))
            # 计算就绪队列中进程的响应比作为优先级
            for p in ready:
                wait_time = current_time - p.arrive_time
                p.priority = (wait_time + p.service_time) / p.service_time
            # 就绪队列按响应比排序
            ready.sort(key=lambda p: p.priority, reverse=True)

    def __sjf(self):
        """短作业优先"""
        # 进程队列按到达时间排序
        self.processors.sort(key=lambda p: p.arrive_time)
        ready = [self.processors.pop(0)]
        current_time = ready[0].arrive_time
        # 当就绪队列非空
        while ready:
            # 取出就绪队列队首进程p，执行，并加入完成队列
            p = ready.pop(0)
            current_time = max(current_time, p.arrive_time)
            current_time = p.process(current_time)
            self.completed.append(p)
            # 选取在当前进程p运行的过程中到达的进程加入就绪队列，进程队列去掉上述进程
            ready += [p for p in self.processors if p.arrive_time <= current_time]
            self.processors = [p for p in self.processors if p.arrive_time > current_time]
            # 如果就绪队列已空，且进程队列非空，则该进程p运行完后，下一个进程还没到达
            # 此时将进程队列队首加入就绪队列
            if not ready and self.processors:
                ready.append(self.processors.pop(0))
            # 就绪队列按服务时间排序，短作业优先
            ready.sort(key=lambda p: p.service_time)


if __name__ == '__main__':
    arr = [0, 1, 2, 3, 4]
    ser = [4, 3, 4, 2, 4]
    s = Scheduling()
    s.set_process(5, arrive=arr, service=ser)
    s.set_time_slice(1)
    print('FCFS')
    s.schedule('FCFS')
    print("iD，到达，服务，开始，结束，周转，带权")
    print(s.get(sort_by='id')) # 按id排序
    print()

    print('RR')
    s.schedule('RR')
    print("iD，到达，服务，开始，结束，周转，带权")
    print(s.get(sort_by='id')) # 按id排序
    print()

    print('HRN')
    s.schedule('HRN')
    print("iD，到达，服务，开始，结束，周转，带权")
    print(s.get(sort_by='id')) # 按id排序
    print()

    print('SJF')
    s.schedule('SJF')
    print("iD，到达，服务，开始，结束，周转，带权")
    print(s.get(sort_by='id')) # 按id排序
    print()