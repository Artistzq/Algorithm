import random
from typing import List


class SimulatedFile:
    """模拟文件"""
    def __init__(self, id, name, size):
        self.id : int = id
        self.name = name
        self.size = size
        self.start_pos = -1
        self.end_pos = -1

    def get(self):
        """返回文件信息"""
        return [str(v) for v in self.__dict__.values()]


class SimulatedDisk:

    def __init__(self, blocks, size_per_block, unit='k', m=0, n=0):
        """
        初始化模拟磁盘
        :param blocks: 盘块数
        :param size_per_block: 每个盘块的大小
        :param unit: 单位，默认”k“
        :param m: 位示图行数
        :param n: 位示图列数，行数与列数成绩为盘块数
        """
        self.size = blocks * size_per_block
        self.size_per_block = size_per_block
        self.blocks = blocks
        self.m = m
        self.n = n
        self.files: List[SimulatedFile] = []
        self.files_names = []
        self.messages = []
        self.bitmap = [[False for i in range(self.n)] for j in range(self.m)]

    def reset(self):
        """重置磁盘，位置图置0，文件列表清空，信息列表清空"""
        self.bitmap = [[False for i in range(self.n)] for j in range(self.m)]
        self.files_names.clear()
        self.messages.clear()
        for file in self.files:
            file.start_pos = -1
            file.end_pos = -1
        self.files.clear()

    def store_files(self, sfs: List[SimulatedFile]):
        """存储一系列文件sfs"""
        for sf in sfs:
            self.assign(sf)

    def assign(self, sf: SimulatedFile):
        """
        分配单个文件sf
        :param sf: 单个文件
        """
        # 检查是否存在于磁盘，若存在则返回
        if sf.name in self.files_names:
            msg = sf.name + "已存在，未执行此文件的插入操作。\n该文件信息为：" + \
                  str(sf.__dict__.items())
            self.messages.append(msg)
            return

        # 分配空闲盘区
        start = 0   # 起始位置
        end = 0     # 结束位置
        content = False  # 是否找到满足文件大小的空闲区
        sf_size = sf.size // self.size_per_block  # 文件大小，除以每个盘块的大小
        if sf.size - self.size_per_block * sf_size != 0: #文件大小取整，一个盘块最多只能存一个文件
            sf_size += 1

        # 若未找到满足文件大小的空闲区
        while not content:
            # 先找开始位置
            while start < self.blocks:
                i, j = start // self.n, start % self.n
                # 找到第一个未被占用的盘块，bitmap位为False
                if not self.bitmap[i][j]:
                    break
                start += 1
            # 如果开始位置为最后一块之后的位置，则空间全部被占用了
            if start == self.blocks:
                self.messages.append("存储空间全满，无法存入该文件。\n该文件信息：" + \
                                     str(sf.__dict__.items()))
                return

            # 再找结束位置
            end = start
            while end < self.blocks:
                i, j = end // self.n, end % self.n
                # 碰到非空闲区，就退出循环，此步骤确保结束位置之前，开始位置之后，都是空闲区
                if self.bitmap[i][j]:
                    break
                # 如果空闲区比文件大小大，就找到了，退出循环
                if end - start >= sf_size:
                    break
                end += 1
            # 如果结束位置比盘块数还大，则文件过大，无法存入
            if end >= self.blocks:
                self.messages.append("该文件过大，未存入磁盘。\n该文件信息为：" + \
                                     str(sf.__dict__.items()))
                print("过大" + str(sf.__dict__.items()))
                return
            # 如果找到的空闲区小于文件大小，则进入下一个总循环，寻找一个连续空闲区
            if end - start < sf_size:
                start = end
                continue
            # 否则，就找到了空闲区
            else:
                content = True
        # 修改文件信息
        sf.start_pos = start
        sf.end_pos = end - 1
        # 分配空间后，空闲区置1
        for idx in range(start, end):
            i, j = idx // self.n, idx % self.n
            self.bitmap[i][j] = True

        self.files.append(sf)
        self.files_names.append(sf.name)

    def delete_files(self, sfs_names: List[str]):
        """
        删除一系列文件
        :param sfs_names: 要删除的文件名列表
        :return:
        """
        for sf_name in sfs_names:
            self.revoke(sf_name)

    def revoke(self, sf_name: str):
        """
        回收单个文件
        :param sf_name: 要回收的文件名
        :return:
        """
        # 磁盘文件列表中是否有此文件名
        find = False
        idx = 0
        # 在磁盘的文件列表中寻找此文件名
        for i, file in enumerate(self.files):
            if file.name == sf_name:
                idx = i
                find = True
                break
        # 若未找到，则返回
        if not find:
            msg = "该文件名不存在，未执行此文件的删除操作。欲删除的文件名为：" + sf_name
            self.messages.append(msg)
            return
        # 获得文件信息，包括开始位置，结束位置
        file = self.files[idx]
        start = file.start_pos
        end = file.end_pos
        # 将开始位置到结束位置之间的盘块置0，即空闲
        for b in range(start, end+1):
            i, j = b // self.n, b % self.n
            self.bitmap[i][j] = False
        file.start_pos = -1
        file.end_pos = -1
        # 文件列表中删去此文件
        self.files_names.remove(sf_name)
        self.files.remove(file)

if __name__ == '__main__':
    """仅测试用，完整见GUI界面"""
    # 500盘块，每个盘块2k大小，
    SD = SimulatedDisk(500, 2, m=25, n=20)
    num = 50
    ids = list(range(num))
    names = [str(id+1) + '.text' for id in ids]
    sizes = [round(random.uniform(2, 10), 2) for i in range(num)]
    simulated_files = [SimulatedFile(id, name, size) for id, name, size in zip(ids, names, sizes)]
    SD.store_files(simulated_files)

    print([f.get() for f in simulated_files])
