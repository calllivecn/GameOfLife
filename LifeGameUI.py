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

from numpy import random, ones, zeros, uint8, convolve

#import patternsLoader

class GameOfLifeWorld:

    life = 1
    dead = 0
    life_chance = 0.1
    count = 0

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

    def Update(self):
        """更新一次"""
        for i in range(1, self.cells.shape[0] - 1):
            for j in range(1, self.cells.shape[1] - 1):
                #计算cell周围的存活细胞数
                neihbor = self.cells[i-1:i+2, j-1:j+2]
                neihbor = neihbor.reshape((-1,))
                num = convolve(self.mask, neihbor, 'valid')[0]
                if num == 3:
                    self.buffer[i, j] = 1
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

    def __init__(self):

        self.formWidth = 650
        self.formHeight = 550
        self.canvasHorizentalCount = 100
        self.canvasVerticalCount = 100

        self.mainForm = None
        self.canvas = None

        self.cellSize = 5

        self.currentPattern = None
        self.refresh=0.2
        self.world_width = self.canvasHorizentalCount * self.cellSize
        self.world_height = self.canvasVerticalCount * self.cellSize

        self.mainForm = tk.Tk()
        self.mainForm.title('生命游戏 v0.1')
        size = '{}x{}'.format(self.formWidth, self.formHeight)
        self.mainForm.geometry(size)

        self.canvas = tk.Canvas(self.mainForm, bg = 'black', width = self.world_width, height = self.world_height)

        self.canvas.grid(row=0, column=0)
    
        #tk.Button(self.mainForm, text='开始', command = self.BtnStart_OnClick).grid(row=1, column=0, sticky=tk.W, padx=50)
        #tk.Button(self.mainForm, text='下个周期', command = self.BtnNext_OnClick).grid(row=1, column=0, sticky=tk.E, padx=50)
    
        # right frame
        group = tk.LabelFrame(self.mainForm, text="信息", padx=5, pady=5, width=120, height=500)
        group.grid(row=0, column=1, sticky=tk.NW)
    

    def UpdateScreen(self, cell):
        for h in range(self.canvasHorizentalCount):
            for w in range(self.canvasHorizentalCount):
                tag_pos = '{}_{}'.format(h, w)

                if cell[h][w] == 1:
                    found = self.canvas.find_withtag(tag_pos)
                    if len(found) == 0:
                        self.canvas.create_rectangle(w * self.cellSize, h * self.cellSize, (w + 1) * self.cellSize, (h + 1) * self.cellSize, fill='blue', tags=('cell', tag_pos))
                else:
                    self.canvas.delete(tag_pos)

        # 更新信息


    def start(self):
        self.mainForm.mainloop()



def info(cells):
    print("迭代计数：{} cells数量：{}".format(cells.count, cells.life_cells))

def run(cell, canvas):

    try:
        while True:
            info(cell)
            canvas.UpdateScreen(cell.cells)
            cell.Update()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass


def starttimer():
    cells = GameOfLifeWorld()
    canvas = CanvasWorld()

    runer = Thread(target=run, args=(cells, canvas), daemon=True)
    runer.start()

    canvas.start()


if __name__ == "__main__":
    starttimer()
    #test()
