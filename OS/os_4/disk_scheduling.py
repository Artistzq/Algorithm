from typing import *
import sys


class Scheduling:

    @classmethod
    def fcfs(cls, start, request_sequence: List):
        """先来先服务"""
        access = request_sequence.copy()
        move = [abs(start - access[0])] + [abs(access[i + 1] - access[i]) for i in range(len(access) - 1)]
        avg = sum(move) / len(move)
        return access, move, avg

    @classmethod
    def sstf(cls, start, request_sequence):
        """
        SSTF算法
        :param start: 起始磁道号
        :param request_sequence: 请求序列
        :return: 访问序列，寻道距离列表，平均寻道距离
        """
        access = []  # 访问序列
        move = []  # 寻道距离列表
        # 设置访问位
        visited = [False] * len(request_sequence)
        for i in range(len(request_sequence)):
            # 对每个需要访问的磁道号，计算到其他所有磁道的距离
            min_dist = sys.maxsize
            min_idx = len(request_sequence)
            for j in range(len(request_sequence)):
                if not visited[j]:
                    # 对没访问过的磁道，进行距离比较，选择最小距离，和对应的序列号
                    dist = abs(request_sequence[j] - start)
                    if min_dist > dist:
                        min_dist = dist
                        min_idx = j
            # 将该序列号加入访问序列
            access.append(request_sequence[min_idx])
            # 访问位设置为1
            visited[min_idx] = True
            # 上述算法计算的最小距离加入寻道距离列表
            move.append(min_dist)
            # 开始磁道号设置为当前磁道
            start = request_sequence[min_idx]
        # 计算平均寻道距离
        avg = sum(move) / len(move)
        return access, move, avg

    @classmethod
    def scan(cls, start, request_sequence, outward=True):
        """
        SCAN算法
        :param start: 起始磁道号
        :param request_sequence: 请求序列
        :param outward: 寻道方向，默认先向外（增大），在向内
        :return: 访问序列，寻道距离列表，平均寻道距离
        """
        # 请求序列按磁道号大小，从小到大排列
        sequence = sorted(request_sequence)
        # 最小的、比起始磁道号大的磁道号的索引
        higher = len(request_sequence) - 1
        access = []
        move = []
        # 找到最小的、比起始磁道号大的磁道号的索引，设为higher
        for i, item in enumerate(sequence):
            if item >= start:
                higher = i
                break
        if outward:  # 先向外寻道再向内
            # 从higher 开始向外
            for i in range(higher, len(sequence)):
                access.append(sequence[i])  # 当前磁道加入请求序列
                move.append(abs(start - sequence[i]))  # 计算起始磁道号和当前磁道距离
                start = sequence[i]  # 设置起始磁道号为当前磁道
            # 从higher-1 开始向内
            for i in range(higher - 1, -1, -1):
                access.append(sequence[i])
                move.append(abs(start - sequence[i]))
                start = sequence[i]
        else:  # 现向内再向外
            # 从higher-1 开始向内
            for i in range(higher - 1, -1, -1):
                access.append(sequence[i])
                move.append(abs(start - sequence[i]))
                start = sequence[i]
            # 从higher 开始向外
            for i in range(higher, len(sequence)):
                access.append(sequence[i])
                move.append(abs(start - sequence[i]))
                start = sequence[i]
        # 平均寻道距离
        avg = sum(move) / len(move)
        return access, move, avg


if __name__ == '__main__':
    """比较简单的算法展示，复杂展示见GUI"""
    seq = [55, 58, 39, 18, 90, 160, 150, 38, 184]
    access, move, avg = Scheduling.fcfs(100, seq)
    print(access, move, avg)
    access, move, avg = Scheduling.sstf(100, seq)
    print(access, move, avg)
    access, move, avg = Scheduling.scan(100, seq)
    print(access, move, avg)
