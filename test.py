#!/usr/bin/env python3
# coding=utf-8
# date 2019-03-18 11:06:26
# https://github.com/calllivecn


from threading import Thread, Lock
import multiprocessing as mp
import tkinter as tk
from tkinter import ttk

import numpy as np



task_queue = mp.Queue(4)


def func1(queue):
    while True:
        data = queue.get()
        print("接收:",data)

def func2(queue):
    data = np.random.random((3, 3, 4))
    while True:
        queue.put(data)
        print("发送。")


pids = []

p1 = mp.Process(target=func1, args=(task_queue,))
p1.start()

pids.append(p1)

p2 = mp.Process(target=func2, args=(task_queue,))
p2.start()

pids.append(p2)


try:
    for p in pids:
        p.join()
except KeyboardInterrupt:
    for p in pids:
        p.terminate()


