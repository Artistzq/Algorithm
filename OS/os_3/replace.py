class PageReplacement(object):

    @classmethod
    def first_in_first_out(cls, pages, swap_size):
        """
        先进先出FIFO
        :param pages: 页面序列
        :param swap_size: 物理块数
        :return: 置换过程的矩阵表示
        """
        times = [0] * swap_size # 时间
        status = [] # 状态
        drop_page = []  # 换出页
        lack_times = 0  # 缺页次数
        swap_space = [-1] * swap_size   # 物理块，当作队列使用
        for seq, page in enumerate(pages):
            # 对每个物理块，时间都+1
            times = [i + 1 for i in times]

            # 如果页面存在于分配的物理块中，那就不用换，不用处理
            if page in swap_space:
                pass
            # 否则即页面不存在，
            # 但是还有空间，则也不用换，加入即可
            elif -1 in swap_space:
                # 找到空闲的位置
                idx = swap_space.index(-1)
                swap_space[idx] = page
                times[idx] = 0  # 该位置时间置0，重新计数
                lack_times += 1 # 缺页次数+1

            # 页面不存在，且无剩余空间，则需替换页面
            else:
                # 选择物理块中停留最久，即时间值最大的位置换出
                idx = times.index(max(times))
                # 换出页加入换出队列
                drop_page.append(swap_space[idx])
                swap_space[idx] = page
                times[idx] = 0  # 该位置时间置0，重新计数
                lack_times += 1 # 缺页次数+1
            # 记录状态
            status.append(swap_space.copy())
        # 为状态矩阵中空值部分填充-1，方便统一处理
        status = [state + [-1] * (swap_size - len(state)) if len(state) < swap_size else state for state in status]
        return status, drop_page, lack_times

    @classmethod
    def least_recently_used(cls, pages, swap_size):
        """
        最近最少使用LRU
        :param pages: 页面序列
        :param swap_size: 物理块数（栈空间大小）
        :return: 结果
        """
        status = [] # 状态矩阵
        stack = []  # 栈，栈顶表示最新访问
        drop_pages = [] # 换出页
        lack_times = 0  # 缺页次数
        # 遍历页面序列中的每个序列号
        for page in pages:
            # 如果该序列号在栈中
            if page in stack:
                # 则将其移到栈顶
                idx = stack.index(page)
                stack.append(stack.pop(idx))
            # 否则该序列不在栈中
            # 但若栈未满，则压栈，缺页次数+1
            elif len(stack) < swap_size:
                stack.append(page)
                lack_times += 1
            # 否则，该序列号既不存在于栈中，栈也满了，
            # 则替换栈底序列号，缺页次数+1，换出页加入换出页序列
            else:
                drop_pages.append(stack.pop(0))
                stack.append(page)
                lack_times += 1
            # 记录状态
            status.append(stack.copy())
        # 为状态矩阵中空值部分填充-1，方便统一处理
        status = [statu + [-1] * (swap_size - len(statu)) if len(statu) < swap_size else statu for statu in status]
        return status, drop_pages, lack_times

    @classmethod
    def replace(cls, pages, method='fifo', swap_size=3):
        """
        选择替换算法进行替换
        :param pages: 页面序列
        :param method: 替换算法，'fifo'或'lru'
        :param swap_size: 置换空间
        :return: 结果
        """
        assert method in ['fifo', 'lru'], "未提供此置换算法：" + method
        if method == 'fifo':
            results = cls.first_in_first_out(pages, swap_size)
        elif method == 'lru':
            results = cls.least_recently_used(pages, swap_size)
        return results


if __name__ == '__main__':
    pages1 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    status, dp, lt = PageReplacement.first_in_first_out(pages1, swap_size=3)
    print(status)
    print("换出页：", dp, "置换次数：", len(dp))
    print("缺页次数：", lt)
    print("缺页率：", lt / len(pages1))
    print()
    pages2 = [4, 7, 0, 7, 1, 0, 1, 2, 1, 2, 6]
    status, dp, lt = PageReplacement.least_recently_used(pages2, swap_size=5)
    # 转置展示
    # status = list(map(list, zip(*status)))
    print(status)
    print("换出页：", dp, "置换次数：", len(dp))
    print("缺页次数：", lt)
    print("缺页率：", lt / len(pages1))
    print()
