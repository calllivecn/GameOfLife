#!/usr/bin/env python3
# coding=utf-8
# date 2019-03-13 16:17:00
# https://github.com/calllivecn

'''
Game of life
author: calllivecn
'''

import os
from threading import Timer
import tkinter as tk
from tkinter import Tk, Canvas, Button, Label, LabelFrame
from tkinter import ttk

from numpy import random, ones, zeros, uint8

#import patternsLoader

class GameOfLifeWorld:

    live = 1
    dead = 0
    life_chance = 0.4
    cells = []
    count = 0

    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height

        self.cells = zeros((self.width, self.height), dtype=uint8)
        self.buffer = self.cells.copy()

        self.mask = ones(9)
        self.mask[4] = 0

    def InitRandom(self):

        for i in range(self.width):
            for j in range(self.height):
                if random.random() > self.life_chance:
                    self.cells[i][j] = 1
                else:
                    self.cells[i][j] = 0
                    
    def TryGetCell(self, h, w):
        return self.cells[min(h, self.height - 1)][min(w, self.width - 1)]

    def GetNearbyCellsCount(self, h, w):
        nearby = [self.TryGetCell(h + dy, w + dx) for dx in [-1, 0, 1]
                  for dy in [-1, 0, 1] if not (dx == 0 and dy == 0)]
        return len(list(filter(lambda x: x == LIVE, nearby)))

    def GetNewCell(self, h, w):
        count = self.GetNearbyCellsCount(h, w)
        return LIVE if count == 3 else (DEAD if count < 2 or count > 3 else self.cells[h][w])

    def Update(self):
        #self.cells = [[self.GetNewCell(h, w) for w in range(self.width)]
                  #for h in range(self.height)]
        """更新一次"""
        for i in range(1, self.cells.shape[0] - 1):
            for j in range(1, self.cells.shape[1] - 1):
                #计算cell周围的存活细胞数
                neihbor = self.cells[i-1:i+2, j-1:j+2]
                neihbor = neihbor.reshape((-1,))
                num = convolve(self.mask, neighbor, 'valid')[0]
                if num == 3:
                    self.buffer[i, j] = 1
                elif num == 2:
                    self.buffer[i, j] = self.cells[i, j]
                else:
                    self.buffer[i, j] = self.cells[i, j]


        tmp = self.buffer
        self.buffer = self.cells
        self.cells = tmp

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
        self.world = None
        self.currentPattern = None
        self.interval=0.2
        self.world_width = self.canvasHorizentalCount * self.cellSize
        self.world_height = self.canvasVerticalCount * self.cellSize

        self.mainForm = Tk()
        self.mainForm.title('生命游戏 v0.1')
        size = '{}x{}'.format(self.formWidth, self.formHeight)
        self.mainForm.geometry(size)

        self.canvas = Canvas(self.mainForm, bg = 'black', width = self.world_width, height = self.world_height)

        self.canvas.grid(row=0, column=0)
    
        Button(self.mainForm, text='开始', command = self.BtnStart_OnClick).grid(row=1, column=0, sticky=tk.W, padx=50)
        Button(self.mainForm, text='下个周期', command = self.BtnNext_OnClick).grid(row=1, column=0, sticky=tk.E, padx=50)
    
        # right frame
        group = LabelFrame(self.mainForm, text="模式", padx=5, pady=5, width=120, height=500)
        group.grid(row=0, column=1, sticky=tk.NW)
    
        # draw category selector
        lbCategory = Label(group, text='Category:')
        lbCategory.pack(anchor=tk.W)

        """
        patterns = patternsLoader.LoadPatterns()
    
        cbCategory = ttk.Combobox(group, width=10, state='readonly')
        cateValues = []
    
        for category in patterns:
            cateValues.append(category)
    
        cbCategory['value'] = cateValues
    
        if(len(cateValues) > 0):
            cbCategory.current(0)
    
        cbCategory.pack(anchor=W)
    
        def onCategoryChanged(*args):
            currentCategory = cbCategory.get()
            print(currentCategory)
            patValues = []
    
            for pat in patterns[currentCategory]:
                patValues.append(pat['name'])
    
            cbPatterns['value'] = patValues
    
            if(len(patValues) > 0):
                cbPatterns.current(0)
    
            onPatternChanged()
    
        cbCategory.bind("<<ComboboxSelected>>", onCategoryChanged)
    
        # draw pattern selector
        lbPatterns = Label(group, text='Patterns:')
        lbPatterns.pack(anchor=W)
        cbPatterns = ttk.Combobox(group, width=10, state='readonly')
        cbPatterns.pack(anchor=W)
        
        # draw pattern previewer
        patCanvas = Canvas(group, bg='black', width=10 * cellSize, height=10 * cellSize)
        patCanvas.pack()
    
        # bind pattern canvas redraw event
        def onPatternChanged(*args):
            currentCategory = cbCategory.get()
            currentPatternName = cbPatterns.get()
    
            print(currentPatternName)
            global currentPattern
    
            for p in patterns[currentCategory]:
                if(p['name'] == currentPatternName):
                    currentPattern = p
    
            if(currentPattern == None):
                return
            h = 0
            for row in currentPattern['content']:
                w = 0
                for cell in row:
                    #print(cell)
                    tag_pos = '%d_%d' % (h, w)
                    if cell == '1':
                        found = patCanvas.find_withtag(tag_pos)
                        if len(found) == 0:
                            patCanvas.create_rectangle(w * cellSize, h * cellSize, (w + 1) *
                                                    cellSize, (h + 1) * cellSize, fill='blue', tags=('cell', tag_pos))
                    else:
                        patCanvas.delete(tag_pos)
                    w = w + 1
                h = h + 1
                #todo: preview canvas can be dynamic
            
        cbPatterns.bind("<<ComboboxSelected>>", onPatternChanged)
        onCategoryChanged()
        
    
        # init world
        global world
        world = GameOfLifeWorld(canvasHorizentalCount, canvasVerticalCount)
    
        world.InitRandom()
        UpdateScreen()
    
        #StartTimer()
    
        self.mainForm.mainloop()
        """

    def UpdateScreen(self, cells):
        for h in range(self.canvasHorizentalCount):
            for w in range(self.canvasHorizentalCount):
                tag_pos = '{}_{}'.format(h, w)
                if cells[h][w] == 1:

                    found = canvas.find_withtag(tag_pos)

                    if len(found) == 0:

                        canvas.create_rectangle(w * cells.cellSize, h * cells.cellSize, (w + 1) * cells.cellSize, (h + 1) * cells.cellSize, fill='blue', tags=('cell', tag_pos))
                else:
                    canvas.delete(tag_pos)

    def start(self):
        self.mainForm.mainloop()

    def BtnStart_OnClick(self):
        StartTimer()

    def BtnNext_OnClick(self):
        Loop()

    def Update(self):
        world.Update()
    
    def Loop(self):
        Update()
        UpdateScreen()

    def StartTimer(self):
        Loop()
        global timer
        timer = Timer(interval, StartTimer)
        timer.start()


def starttimer():
    cells = GameOfLifeWorld()
    
    canvas = CanvasWorld()

    canvas.start()

#timer = Timer(interval, StartTimer)

if __name__ == "__main__":
    starttimer()
