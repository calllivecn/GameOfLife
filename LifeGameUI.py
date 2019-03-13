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
from tkinter import *
from tkinter import ttk

from numpy import random, ones, zeros, uint8

import patternsLoader

class GameOfLifeWorld:

    live = 1
    dead = 0
    life_chance = 0.4
    width = 100
    height = 100
    cells = []

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def InitRandom(self):
        self.cells = zeros((self.width, self.height), dtype=uint8)

        for i in range(self.width):
            for j in range(self.height):
                if random.random() > self.life_chance:
                    cells[i][j] = 1
                else:
                    cells[i][j] = 0
                    
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
        self.cells = [[self.GetNewCell(h, w) for w in range(self.width)]
                  for h in range(self.height)]


formWidth = 650
formHeight = 550
canvasHorizentalCount = 100
canvasVerticalCount = 100
mainForm = None
canvas = None
cellSize = 5
world = None
currentPattern = None

interval=0.2

def PrintScreen():
    global canvas
    for h in range(canvasHorizentalCount):
        for w in range(canvasHorizentalCount):
            tag_pos = '%d_%d' % (h, w)
            if world.cells[h][w] == LIVE:
                found = canvas.find_withtag(tag_pos)
                if len(found) == 0:
                    canvas.create_rectangle(w * cellSize, h * cellSize, (w + 1) *
                                            cellSize, (h + 1) * cellSize, fill='blue', tags=('cell', tag_pos))
            else:
                canvas.delete(tag_pos)


def Update():
    world.Update()


def Loop():
    Update()
    PrintScreen()


def BtnNext_OnClick():
    Loop()

def BtnStart_OnClick():
    StartTimer()


def StartTimer():
    Loop()
    global timer
    timer = threading.Timer(interval, StartTimer)
    timer.start()




def Start():
    global mainForm
    mainForm = Tk()
    mainForm.title('生命游戏 v0.1')
    size = '%dx%d' % (formWidth, formHeight)
    mainForm.geometry(size)
    global canvas

    canvas = Canvas(mainForm, bg='black', width=canvasHorizentalCount *
                    cellSize, height=canvasVerticalCount * cellSize)
    canvas.grid(row=0, column=0)

    Button(mainForm, text='开始', command=BtnStart_OnClick).grid(row=1, column=0, sticky=W, padx=50)
    Button(mainForm, text='下个周期', command=BtnNext_OnClick).grid(row=1, column=0, sticky=E, padx=50)

    # right frame
    group = LabelFrame(mainForm, text="Patterns", padx=5, pady=5, width=120, height=500)
    group.grid(row=0, column=1, sticky=NW)

    # draw category selector
    lbCategory = Label(group, text='Category:')
    lbCategory.pack(anchor=W)

    global patterns
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
    PrintScreen()

    #StartTimer()

    mainForm.mainloop()


timer = threading.Timer(interval, StartTimer)

if __name__ == "__main__":
    Start()
