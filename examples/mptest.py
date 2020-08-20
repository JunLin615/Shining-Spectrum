# -*- coding: utf-8 -*-
"""
@Time:2020/8/20 22:46
@Auth"JunLin615
@File:mptest.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""

from multiprocessing import  Manager, Pool
import os, time, random

"""
multiprocessing.Pool常用函数解析：
    apply_async(func[, args[, kwds]]) ：使用非阻塞方式调用func（并行执行，堵塞方式必须等待上一个进程退出才能执行下一个进程），args为传递给func的参数列表，kwds为传递给func的关键字参数列表；
    apply(func[, args[, kwds]])：使用阻塞方式调用func
    close()：关闭Pool，使其不再接受新的任务；
    terminate()：不管任务是否完成，立即终止；
    join()：主进程阻塞，等待子进程的退出， 必须在close或terminate之后使用；
"""


def worker(msg,l1 ,l2):
    t_start = time.time()
    print("%s开始执行,进程号为%d" % (msg, os.getpid()))
    # random.random()随机生成0~1之间的浮点数
    time.sleep(1)
    try :
        l1.append(1)
    except:
        time.sleep(0.1)
        l1.append(1)

    try :
        l2.append(2)
    except:
        time.sleep(0.1)
        l2.append(2)
    t_stop = time.time()
    print(msg, "执行完毕，耗时%0.2f" % (t_stop - t_start))


def main():
    manager = Manager()
    l1 = manager.list()
    l2 = manager.list()
    po = Pool(3)  # 定义一个进程池，最大进程数3
    for i in range(10):
        # Pool.apply_async(要调用的目标,(传递给目标的参数元祖,))
        # 每次循环将会用空闲出来的子进程去调用目标
        po.apply_async(worker, (i,l1,l2))

    print("----start----")
    po.close()  # 关闭进程池，关闭后po不再接收新的请求
    po.join()  # 等待po中所有子进程执行完成，必须放在close语句之后
    print("l1:{}".format(l1))
    print("l2:{}".format(l2))
    print("-----end-----")


if __name__ == '__main__':
    main()

