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
from threading import Timer, Thread, Lock
import tkinter as tk

import numpy as np


class Pause:

    def __init__(self):
        self.lock = Lock()
        #self.lock.acquire()
        self._pause = True

    def pause(self):

        #self.lock.acquire()

        if self._pause:
            self._pause = False
        else:
            self._pause = True

        #self.lock.release()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

PAUSE = Pause()

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

    @runtime
    def __init__(self, width=100, height=100, chance=0.2):
        self.width = width
        self.height = height

        self.life_chance = chance
        self.count = 0

        self.count_time = 0
        self.cells = np.zeros((self.width, self.height), dtype=np.uint8)
        self.buffer = self.cells.copy()

        self.mask = np.ones(9)
        self.mask[4] = 0


        for i in range(self.width):
            for j in range(self.height):
                if np.random.random() < self.life_chance:
                    self.cells[i][j] = self.life
                else:
                    self.cells[i][j] = self.dead

        self.life_init_cells = self.cells.sum()
        self.life_cells = self.life_init_cells

    @runtime
    def Update(self):
        """更新一次"""
        start = time.time()
        for i in range(1, self.cells.shape[0] - 1):
            for j in range(1, self.cells.shape[1] - 1):
                #计算cell周围的存活细胞数
                neihbor = self.cells[i-1:i+2, j-1:j+2]
                neihbor = neihbor.reshape((-1,))
                num = np.convolve(self.mask, neihbor, 'valid')[0]

                if num == 3:
                    self.buffer[i, j] = self.life
                elif num == 2:
                    self.buffer[i, j] = self.cells[i, j]
                else:
                    self.buffer[i, j] = 0

        tmp = self.buffer
        self.buffer = self.cells
        self.cells = tmp

        self.life_cells = self.cells.sum()

        self.buffer.fill(0)

        self.count += 1

        end = time.time()
        self.count_time = round(end - start, 3)


class CanvasWorld:
    """添加画板"""

    def __init__(self, cells, cellSize=5, skip=0):
        self.cells = cells

        self.canvasHorizentalCount = self.cells.width
        self.canvasVerticalCount = self.cells.height
        self.cellSize = cellSize

        self.world_width = self.canvasHorizentalCount * self.cellSize
        self.world_height = self.canvasVerticalCount * self.cellSize

        self.skip_count = skip
        self.refresh = 0.1

        self.display_time = 0

        self._pause = True

        self.win = tk.Tk()
        self.win.title('生命游戏 {}'.format(__version__))
        #self.win.geometry('{}x{}'.format(self.world_width, self.world_height))

        self.frame_world = tk.Frame(self.win)
        self.frame_world.pack(anchor=tk.NE, side="left")

        self.frame_info = tk.Frame(self.win)
        self.frame_info.pack(anchor=tk.W, side="right", fill='both')

        self.canvas = tk.Canvas(self.frame_world, bg = 'black', width = self.world_width, height = self.world_height)

        self.canvas.pack()


        self.info_count = tk.StringVar(value="世代:{}代".format(self.cells.count))
        self.info_cells_sum = tk.StringVar(value="生命数:{}个".format(self.cells.life_cells))
        self.info_display_time = tk.StringVar(value="显示用时:{}s".format(self.display_time))
        self.info_count_time = tk.StringVar(value="世代用时:{}s".format(self.cells.count_time))

        self.start_pause = tk.StringVar(value="开始")

        # right frame
        tk.Label(self.frame_info, text="信息:", padx=1, pady=1).pack(anchor=tk.W, side='top')
        tk.Label(self.frame_info, textvariable=self.info_count, anchor=tk.W, padx=1, pady=1, width=20).pack(anchor=tk.W, side='top')
        tk.Label(self.frame_info, textvariable=self.info_cells_sum, anchor=tk.W, padx=1, pady=1, width=20).pack(anchor=tk.E, side='top')
        tk.Label(self.frame_info, textvariable=self.info_count_time, anchor=tk.W, padx=1, pady=1, width=20).pack(anchor=tk.E, side='top')
        tk.Label(self.frame_info, textvariable=self.info_display_time, anchor=tk.W, padx=1, pady=1, width=20).pack(anchor=tk.E, side='top')

        # 
        tk.Label(self.frame_info, text="设置:", padx=1, pady=1).pack(anchor=tk.E, side='top')

        frame_chance = tk.Frame(self.frame_info).pack(anchor=tk.W, side='top')
        tk.Label(frame_chance, text="初始概率:", padx=1,pady=1, anchor=tk.W).pack(anchor=tk.W, side='left')

        entry_chance = tk.Entry(frame_chance, width=4)
        entry_chance.insert(0,self.cells.life_chance)
        entry_chance.pack(anchor=tk.W, side='right', fill='x')

        self.frame_btn = tk.Frame(self.frame_info)
        self.frame_btn.pack(anchor=tk.W)

        self.entry_button1 = tk.Frame(self.frame_btn)
        self.entry_button1.pack(fill='x')

        #tk.Label(self.entry_button1, text=).pack(side='left')
        
        tk.Button(self.entry_button1, text="快进世代:", command = self.button_skip).pack(side='left')
        
        self.info_skip = tk.Entry(self.entry_button1,text="10", width=8)
        self.info_skip.insert(0, "10")
        self.info_skip.pack(fill='y')

    
        tk.Button(self.frame_btn, textvariable=self.start_pause, command = self.__pause).pack() #.grid(row=1, column=0, sticky=tk.W, padx=50)
        tk.Button(self.frame_btn, text='下个世代', command = self.UpdateOne).pack() #.grid(row=1, column=0, sticky=tk.E, padx=50)
    
    
    @runtime
    def InitScreen(self):

        self.item_ids = np.zeros(self.cells.cells.shape, dtype=np.uint32)
        i_s, j_s = self.cells.cells.shape

        for i in range(i_s):
            for j in range(j_s):
                if self.cells.cells[i][j] == 1:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='blue')
                else:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='black')
                self.item_ids[i][j] = item_id

    @runtime
    def UpdateScreen(self):

        start = time.time()

        i_s, j_s = self.cells.cells.shape
        for j in range(j_s):
            for i in range(i_s):
                tag = "{}_{}".format(i,j)
                
                if self.cells.cells[i][j] == 1:
                    found = self.canvas.find_withtag(tag)
                    if len(found) == 0:
                        self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='blue', tag=("cell","{}_{}".format(i,j)))
                else:
                    self.canvas.delete(tag)


        # 更新cells信息
        end = time.time()
        self.display_time = round(end - start, 3)

        self.__info()

    def UpdateOne(self):
        self.cells.Update()
        self.__info()
        self.start_pause.set("开始")

        if self._pause:
            self.UpdateScreen()
        else:
            self._pause = True
            self.UpdateScreen()



    def __info(self):
        self.info_count.set("世代：{}代".format(self.cells.count))
        self.info_cells_sum.set("生命数:{}个".format(self.cells.life_cells))
        self.info_display_time.set("显示用时:{}s".format(self.display_time))
        self.info_count_time.set("世代用时:{}s".format(self.cells.count_time))

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

        for _ in range(self.skip_count):
            self.cells.Update()

        self.skip_count = 0

    def button_skip(self):
        if self._pause:
            self._pause = False
        else:
            self._pause = True

        try:
            count = int(self.info_skip.get())
        except ValueError:
            count = 10
            self.info_skip.set("10")
        
        self.skip_count = count 
        self.skip()

        self._pause = True

def info(cells):
    print("-"*60)
    print("迭代计数：{} cells数量：{}".format(cells.count, cells.life_cells))


def run(cell, canvas):
    try:

        while True:

            if canvas._pause:
                time.sleep(0.1)
            else:
                t1 = time.time()

                canvas.UpdateScreen()

                cell.Update()

                t2 = time.time()

                interval = t2 -t1
                if interval < 0.1:
                    time.sleep(0.1 - interval)



    except KeyboardInterrupt:
        pass


def starttimer():
    cells = GameOfLifeWorld(100,100)

    canvas = CanvasWorld(cells, 5)

    canvas.UpdateScreen()
    #canvas.InitScreen()

    runer = Thread(target=run, args=(cells, canvas), daemon=True)
    runer.start()

    canvas.start()


if __name__ == "__main__":
    starttimer()
    #test()
