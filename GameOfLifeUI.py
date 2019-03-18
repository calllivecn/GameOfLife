#!/usr/bin/env python3
# coding=utf-8
# date 2019-03-13 16:17:00
# https://github.com/calllivecn

'''
生命游戏
1. 当一个细胞周围有3个细胞时，它当成存活(不论之前是死是活，模拟生命繁殖)。
2. 当一个细胞周围有2个细胞时，它状态不变(活就是活，死就是死)。
3. 当一个细胞周围有大于3细胞存活时，它变为死亡。(它会由于缺少生命资源，而死亡)
4. 当一个细胞周围有小于2个细胞时，它变成死。
author: calllivecn
'''

__version__ = "v0.4"

import os
import time
import multiprocessing as mp
from threading import Timer, Thread, Lock
import tkinter as tk
from tkinter import ttk

import numpy as np


def runtime(func, *args, **kwargs):
    def f(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, "运行耗时：", round(end - start, 3), "s")
        return result
    return f

class GameOfLifeWorld:

    life = 1
    dead = 0

    def __init__(self, width=100, height=100, chance=0.2):
        self.width = width
        self.height = height

        self.life_chance = chance
        self.count = 0

        self.count_time = 0
        self.cells = np.zeros((self.width, self.height), dtype=np.uint8)

        for i in range(self.width):
            for j in range(self.height):
                if np.random.random() < self.life_chance:
                    self.cells[i][j] = self.life
                else:
                    self.cells[i][j] = self.dead

        self.life_cells = self.cells.sum()

    def updateinfo(self, cells):
        print("cells: ", cells.sum())
        self.cells = cells
        self.life_cells = self.cells.sum()
        self.count += 1


class CanvasWorld:
    """添加画板"""

    def __init__(self, cellSize=5):

        self.canvasHorizentalCount = 100
        self.canvasVerticalCount = 100
        self.cellSize = cellSize

        self.world_width = self.canvasHorizentalCount * self.cellSize
        self.world_height = self.canvasVerticalCount * self.cellSize

        self.refresh = 0.1

        self.count = 0
        self.display_time = 0

        self._pause = True

        self.win = tk.Tk()
        self.win.title('生命游戏 {}'.format(__version__))
        #self.win.geometry('{}x{}'.format(self.world_width, self.world_height))

        self.frame_world = ttk.Frame(self.win)
        self.frame_world.pack(anchor=tk.NW, side="left")

        self.frame_info = ttk.Frame(self.win)
        self.frame_info.pack(anchor=tk.NW, side="right", fill='both')

        self.canvas = tk.Canvas(self.frame_world, bg = 'black', width = self.world_width, height = self.world_height)

        self.canvas.pack()


        self.info_count = tk.StringVar(value="世代:{}代".format(0))
        self.info_cells_sum = tk.StringVar(value="生命数:{}个".format(0))
        #self.info_display_time = tk.StringVar(value="显示用时:{}s".format(0))
        #self.info_count_time = tk.StringVar(value="世代用时:{}s".format(0))

        self.start_pause = tk.StringVar(value="开始")

        # right frame
        ttk.Label(self.frame_info, text="信息:").pack(anchor=tk.W, side='top')
        ttk.Label(self.frame_info, textvariable=self.info_count, anchor=tk.W, width=20).pack(anchor=tk.W, side='top')
        ttk.Label(self.frame_info, textvariable=self.info_cells_sum, anchor=tk.W, width=20).pack(anchor=tk.W, side='top')
        #3ttk.Label(self.frame_info, textvariable=self.info_count_time, anchor=tk.W, width=20).pack(anchor=tk.W, side='top')
        #ttk.Label(self.frame_info, textvariable=self.info_display_time, anchor=tk.W, width=20).pack(anchor=tk.W, side='top')

        # 

        #frame_chance = ttk.Frame(self.frame_info).pack(side='top')
        #ttk.Label(frame_chance, text="设置:").pack(anchor=tk.W, side='top')
        #ttk.Label(frame_chance, text="初始概率:", anchor=tk.W).pack(anchor=tk.W, side='left')

        #entry_chance = ttk.Entry(frame_chance, width=4)
        #entry_chance.insert(0,"10")
        #entry_chance.pack(anchor=tk.W, side='right', fill='x')

        self.frame_btn = ttk.Frame(self.frame_info)
        self.frame_btn.pack(anchor=tk.W)

        self.entry_button1 = ttk.Frame(self.frame_btn)
        self.entry_button1.pack(fill='x')

        #ttk.Label(self.entry_button1, text=).pack(side='left')
        
        ttk.Button(self.entry_button1, text="快进:", command = self.skip).pack(side='left')
        
        self.info_skip = ttk.Entry(self.entry_button1,text="10", width=8)
        self.info_skip.insert(0, "10")
        self.info_skip.pack(fill='x')

    
        ttk.Button(self.frame_btn, textvariable = self.start_pause, command = lambda :self.__pause()).pack() #.grid(row=1, column=0, sticky=tk.W, padx=50)
        #ttk.Button(self.frame_btn, text='下个世代', command = self.UpdateOne).pack() #.grid(row=1, column=0, sticky=tk.E, padx=50)
    
    
    def InitScreen(self, cells):

        self.item_ids = np.zeros(cells.shape, dtype=np.uint32)
        i_s, j_s = cells.shape

        for i in range(i_s):
            for j in range(j_s):
                if cells[i][j] == 1:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='blue')
                else:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='black')
                self.item_ids[i][j] = item_id

    def UpdateScreen(self, cells):

        start = time.time()

        i_s, j_s = cells.shape
        for j in range(j_s):
            for i in range(i_s):
                tag = "{}_{}".format(i,j)
                
                if cells[i][j] == 1:
                    found = self.canvas.find_withtag(tag)
                    if len(found) == 0:
                        self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='blue', tag=("cell","{}_{}".format(i,j)))
                else:
                    self.canvas.delete(tag)


        end = time.time()
        self.count += 1
        self.life_sum = cells.sum()
        self.display_time = round(end - start, 3)

        self.__info()

    def __info(self):
        self.info_count.set("世代：{}代".format(self.count))
        self.info_cells_sum.set("生命数:{}个".format(self.life_sum))
        #self.info_display_time.set("显示用时:{}s".format(self.display_time))
        #self.info_count_time.set("世代用时:{}s".format(cells.count_time))

    def __pause(self):
        if self._pause:
            self._pause = False
            self.start_pause.set("暂停")
        else:
            self._pause = True
            self.start_pause.set("开始")

    def start(self):
        self.win.mainloop()

    def skip(self):

        if self._pause:
            self._pause = False

        try:
            count = int(self.info_skip.get())
        except ValueError:
            count = 10
            self.info_skip.set("10")
        
        skip(count)

        self._pause = True


QUEUE = mp.Queue(8)


def skip(count):
    for _ in range(count):
        QUEUE.get()

    canvas.__info()

def run(canvas, cells, queue):
    while True:
        if canvas._pause:
            time.sleep(0.1)
        else:
            t1 = time.time()

            data = queue.get()

            canvas.UpdateScreen(data)

            t2 = time.time()

            interval = round(t2 - t1, 3)
            if interval < 0.1:
                time.sleep(0.1 - interval)

def task(queue, cell):
    """更新一次"""

    life = 1
    dead = 0

    buffer = np.zeros(cell.shape, dtype=np.uint8)
    mask = np.ones(9)
    mask[4] = 0

    print("cell: ",cell.sum())

    while True:
        #print("task: queue")

        for i in range(1, cell.shape[0] - 1):
            for j in range(1, cell.shape[1] - 1):
                #计算cell周围的存活细胞数
                neihbor = cell[i-1:i+2, j-1:j+2]
                neihbor = neihbor.reshape((-1,))
                num = np.convolve(mask, neihbor, 'valid')[0]

                if num == 3:
                    buffer[i, j] = life
                elif num == 2:
                    buffer[i, j] = cell[i, j]
                else:
                    buffer[i, j] = dead

        queue.put(buffer)

        tmp = cell
        cell = buffer
        buffer = tmp

        buffer.fill(0)


def starttimer():
    cells = GameOfLifeWorld(100,100)

    canvas = CanvasWorld()

    canvas.UpdateScreen(cells.cells)

    runer = Thread(target=run, args=(canvas, cells, QUEUE), daemon=True)
    runer.start()

    calculate = mp.Process(target=task, args=(QUEUE, cells.cells), daemon=True)
    calculate.start()

    canvas.start()

if __name__ == "__main__":
    try:
        starttimer()
    except KeyboardInterrupt:
        exi(0)
