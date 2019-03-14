#!/usr/bin/env python3
# coding=utf-8
# date 2019-03-13 16:17:00
# https://github.com/calllivecn

'''
生命游戏
1. 当一个细胞周围有3个细胞时，它当成存活。
2. 当一个细胞周围有2个细胞时，它状态不变(活就是活，死就是死)。
3. 当一个细胞周围有大于3细胞存活时，它为死。(它会由于缺少生命资源，而死亡)
author: calllivecn
'''

import os
import time
from threading import Timer,Thread
import tkinter as tk
from tkinter import ttk

from numpy import random, ones, zeros, uint8, uint32, convolve

#import patternsLoader

def runtime(func, *args, **kwargs):
    def f(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, "运行耗时：", end - start, "s")
        return result
    return f

class GameOfLifeWorld:

    life = 1
    dead = 0
    life_chance = 0.3
    count = 0

    @runtime
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height


        self.cells = zeros((self.width, self.height), dtype=uint8)
        self.buffer = self.cells.copy()

        self.mask = ones(9)
        self.mask[4] = 0


        for i in range(self.width):
            for j in range(self.height):
                if random.random() < self.life_chance:
                    self.cells[i][j] = self.life
                else:
                    self.cells[i][j] = self.dead

        self.life_init_cells = self.cells.sum()
        self.life_cells = self.life_init_cells

    @runtime
    def Update(self):
        """更新一次"""
        for i in range(1, self.cells.shape[0] - 1):
            for j in range(1, self.cells.shape[1] - 1):
                #计算cell周围的存活细胞数
                neihbor = self.cells[i-1:i+2, j-1:j+2]
                neihbor = neihbor.reshape((-1,))
                num = convolve(self.mask, neihbor, 'valid')[0]

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



class CanvasWorld:
    """添加画板"""

    def __init__(self, cells_width, cells_height, cellSize=5, skip=0):

        self.canvasHorizentalCount = cells_width
        self.canvasVerticalCount = cells_height
        self.cellSize = cellSize

        self.world_width = self.canvasHorizentalCount * self.cellSize
        self.world_height = self.canvasVerticalCount * self.cellSize

        self.skip_count = skip
        self.refresh = 0.1

        self.win = tk.Tk()
        self.win.title('生命游戏 v0.1')
        #self.win.geometry('{}x{}'.format(self.world_width, self.world_height))

        self.canvas = tk.Canvas(self.win, bg = 'black', width = self.world_width, height = self.world_height)

        self.canvas.pack(anchor=tk.NE,side="left")

        # right frame
        group = tk.LabelFrame(self.win, text="信息", padx=5, pady=5, width=120, height=500)
        group.pack(anchor=tk.W, side='right')
    
        tk.Button(self.win, text='开始', command = lambda :run(self)).pack(anchor=tk.S, side='bottom') #.grid(row=1, column=0, sticky=tk.W, padx=50)
        tk.Button(self.win, text='下个周期', command = lambda :print("pass")).pack(anchor=tk.S, side='bottom') #.grid(row=1, column=0, sticky=tk.E, padx=50)
    
    
    @runtime
    def InitScreen(self, cells):

        self.item_ids = zeros(cells.shape, dtype=uint32)
        i_s, j_s = cells.shape

        for i in range(i_s):
            for j in range(j_s):
                if cells[i][j] == 1:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='blue')
                else:
                   item_id = self.canvas.create_rectangle(i * self.cellSize, j * self.cellSize, (i + 1) * self.cellSize, (j + 1) * self.cellSize, fill='black')
                self.item_ids[i][j] = item_id

    @runtime
    def UpdateScreen(self, cells):
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


    def start(self):
        self.win.mainloop()


def info(cells):
    print("-"*60)
    print("迭代计数：{} cells数量：{}".format(cells.count, cells.life_cells))

def skip(cell):
    if cell.skip_count > 0:
        for _ in range(cell.skip_count):
            cell.Update()

        cell.skip_count = 0

def run(cell, canvas):

    try:
        while True:
            t1 = time.time()
            info(cell)

            canvas.UpdateScreen(cell.cells)

            skip(cell)
            cell.Update()

            t2 = time.time()

            if (t2 - t1) < 0.1:
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass


def starttimer():
    cells = GameOfLifeWorld(100,100)

    canvas = CanvasWorld(cells.width, cells.height,5)

    runer = Thread(target=run, args=(cells, canvas), daemon=True)
    runer.start()

    canvas.start()


if __name__ == "__main__":
    starttimer()
    #test()
