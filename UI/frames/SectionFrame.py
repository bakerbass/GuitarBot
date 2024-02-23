import tkinter as tk
import customtkinter as ctk
from frames.BarFrame import BarFrame
from components.Section import Section
from constants.strum_patterns import *
from constants.time_signatures import *

class SectionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, timeSignature):
        super().__init__(master=master, orientation='horizontal')

        self.lastColumn = 0
        self.name = ""
        self.nameInput = None
        self.strumPatternSelection = tk.StringVar(self)
        self.numMeasures = 1
        self.beatsPerMeasure = int(timeSignature[0])
        self.subdivisionsPerMeasure = int(16 / int(timeSignature[2]) * self.beatsPerMeasure)
        self.beatLabels = beat_labels[timeSignature]

        self.chordRowTabOrder = []
        self.strumRowTabOrder = []

        self.strumPatternSelection.set("Downs")
        self.addMeasure()

    def update(self, startColumn):
        # build chords/strum chart
        for i in range(0, 4):
            # print(i + self.offset)
            j = startColumn
            while j <= self.subdivisionsPerMeasure * self.numMeasures:
                currMeasure = 0
                if i == 0 and currMeasure <= self.numMeasures:
                    # MEASURE tk.LabelS
                    # account for bar tk.Label placement shift
                    if (j != 0 and j == startColumn):
                        j -= 1

                    tk.LabelText = "Bar " + str(currMeasure)
                    self.cell = tk.Label(self, width=4, text=tk.LabelText)
                    self.cell.grid(row=i, column=j + self.beatsPerMeasure, sticky='w',
                                    columnspan=self.subdivisionsPerMeasure)
                    j += self.subdivisionsPerMeasure
                    currMeasure += 1
                    continue
                elif i == 1:
                    # BEAT tk.LabelS
                    if j == 0:
                        # add empty tk.Label at beginning of row (placeholder to align w/ below rows)
                        self.cell = tk.Label(self, width=6, text="")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = tk.Entry(self, width=2, font=('Arial', 16, 'bold'))

                    # add space after last beat of measure
                    if j != 0 and j % self.beatsPerMeasure == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    self.cell.insert(tk.END,
                                        self.beatLabels[(j - 1) % self.beatsPerMeasure])
                    self.cell.config(state=tk.DISABLED)
                elif i == 2:
                    # CHORD INPUTS
                    if j == 0:
                        # add "Chords: " tk.Label at beginning of row
                        self.cell = tk.Label(self, width=6, text="Chords: ")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = tk.Entry(self, width=6, font=('Arial', 16))

                    # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                    # add <Return> event handler to every input box (adds new measure if pressed)
                    self.cell.bind("<Return>", self.__returnPressed)

                    self.cell.grid(row=i, column=j, sticky='w', columnspan=2)
                    self.chordRowTabOrder.append(self.cell)

                    self.cell.insert(tk.END, "")
                    j += 1
                elif i == 3:
                    # STRUM INPUTS
                    if j == 0:
                        # add "Strum Pattern: " dropdown at beginning of row
                        if self.strumPatternSelection.get() == "":
                            self.strumPatternSelection.set("Custom")

                        self.cell = tk.OptionMenu(self, self.strumPatternSelection, self.strumPatternSelection.get(), *strum_options,
                                                command=self.fillStrumPattern)
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = tk.Entry(self, width=2, font=('Arial', 16))

                    # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                    # add <Return> event handler to every input box (adds new measure if pressed)
                    self.cell.bind("<Return>", self.__returnPressed)

                    # add spacing after last beat of measure
                    if j != 0 and j % self.beatsPerMeasure == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    if (self.strumPatternSelection.get() != "") and self.strumPatternSelection.get()[0] == "W":
                        # Wonderwall strum patterns
                        self.cell.insert(tk.END, strum_patterns.get(self.strumPatternSelection.get())[(j - 1) % 32])
                    elif self.strumPatternSelection.get() != "Custom":
                        self.cell.insert(tk.END, strum_patterns.get(self.strumPatternSelection.get())[
                            (j + 1) % 2])  # autofill newly added cells with selected strum pattern
                    else:
                        self.cell.insert(tk.END, "")

                    self.strumRowTabOrder.append(self.cell)
                j += 1

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=startColumn + 1)[0].focus_set()

        # update lastColumn
        self.lastColumn = self.subdivisionsPerMeasure * self.numMeasures

        # place clear tk.Button
        self.cell = tk.Button(self, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=4, column=j - 3, columnspan=2, sticky='w')

        # components for section name input
        self.cell = tk.Label(self, width=5, text="Name:")
        self.cell.grid(row=4, column=j - 7, columnspan=2, sticky='e')
        nameInput = tk.Entry(self, width=6, font=('Arial', 14))
        self.nameInput = nameInput
        nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
        nameInput.grid(row=4, column=j - 5, columnspan=2, sticky='w')

        # set tabbing order
        self.__setTabOrder()

    # TODO: fix bug when tabbing to name after removing a measure (not urgent)
    def __setTabOrder(self):
        # NOTE: if user presses tab on last chord input in a section, focus will go to the first strum input on the next row

        # iterate through the "Chords" row, set tabbing order from left -> right
        for cell in self.chordRowTabOrder:
            cell.lift()

        # iterate through the "Strums" row, set tabbing order from left -> right
        for cell in self.strumRowTabOrder:
            cell.lift()

        self.nameInput.lift()

    def __updateName(event, c, self, name):
        if c.keysym == "BackSpace":
            # slice off last char
            self.name = self.name[:len(self.name) - 1]
        else:
            # append pressed char
            self.name = name + c.char

    # event handler for add measure (Enter)
    def __returnPressed(self, event):
        self.addMeasure(self)

    def addMeasure(self):
        self.numMeasures = self.numMeasures + 1

        # delete previous clear tk.Button, name tk.Label/input (will get re-added during the buildTable() call)
        for e in self.grid_slaves(row=4):
            e.grid_forget()

        self.update(self.lastColumn + 1)
        self.nameInput.insert(0, self.name)
        # print("measure added")

    # event handler for remove measure (Shift+BackSpace)
    def __backspacePressed(self, event):
        self.removeMeasure(self)

    def removeMeasure(self):
        # minimum of 1 measure per section
        if self.numMeasures > 1:
            self.numMeasures = self.numMeasures - 1

        # delete all components in last measure
        for i in range(self.subdivisionsPerMeasure):
            for j in range(5):
                for e in self.grid_slaves(column=self.lastColumn - i, row=j):
                    e.grid_forget()

                    # remove deleted cells from tab orders
                    if j == 2:
                        self.chordRowTabOrder.pop()
                    if j == 3:
                        self.strumRowTabOrder.pop()

                    self.__setTabOrder()

        # update last column
        self.lastColumn = self.lastColumn - self.subdivisionsPerMeasure

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=self.lastColumn - self.subdivisionsPerMeasure + 1)[
            0].focus_set()

        # put bar tk.Label back
        tk.LabelText = "Bar " + str(self.numMeasures)
        self.cell = tk.Label(self, width=4, text=tk.LabelText)
        self.cell.grid(row=0, column=self.lastColumn - self.beatsPerMeasure, sticky='w',
                        columnspan=self.subdivisionsPerMeasure)

        # put clear tk.Button back
        self.cell = tk.Button(self, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=4, column=self.lastColumn - 2, columnspan=2, sticky='w')

        # put components for section name input back
        self.cell = tk.Label(self, width=5, text="Name:")
        self.cell.grid(row=4, column=self.lastColumn - 6, columnspan=2, sticky='e')
        nameInput = tk.Entry(self, width=6, font=('Arial', 14))
        nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
        nameInput.grid(row=4, column=self.lastColumn - 4, columnspan=2, sticky='w')
        # print("measure removed")

    def editTable(self, num_cols, timeSignature):
        # delete prev rows
        for w in self.grid_slaves():
            w.grid_forget()

        self.update(num_cols, timeSignature, 0, 1)

    def clearTable(self):
        count = 0
        for e in reversed(self.grid_slaves(row=2)):
            if count != 0:
                e.delete(0, tk.END)
            count += 1

        count = 0
        for e in reversed(self.grid_slaves(row=3)):
            if count != 0:
                e.delete(0, tk.END)
            count += 1

        # clear name input
        self.grid_slaves(row=4, column=self.lastColumn - 4)[0].delete(0, tk.END)

        # print("table cleared")

    def fillStrumPattern(self, event):
        # implementation choice: autofill entire table on selection? Or just set that selection for new bars?
        count = 0

        for e in reversed(self.grid_slaves(row=3)):
            if count != 0:
                e.delete(0, tk.END)
                if self.strumPatternSelection.get()[0] == "W":
                    # Wonderwall strum patterns
                    e.insert(tk.END, strum_patterns.get(self.strumPatternSelection.get())[(count - 1) % 32])
                elif self.strumPatternSelection.get() != "Custom":
                    e.insert(tk.END, strum_patterns.get(self.strumPatternSelection.get())[(count + 1) % 2])
            count += 1

    def buildChordStrumData(self, timeSignature):
        leftArm = []
        rightArm = []
        numBeatsPerMeasure = (int)(timeSignature.get()[0])

        # generate left arm data
        currMeasure = []
        count = 0
        for e in reversed(self.grid_slaves(row=2)):
            # print("count: ", count)
            # print("value: ", e.get())
            # print("numbeats: ", numBeatsPerMeasure)

            if count != 0:
                currMeasure.append(e.get())
                if count == numBeatsPerMeasure:
                    leftArm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        # generate right arm data
        currMeasure = []
        count = 0
        # duration = (60 / bpm) / (numBeatsPerMeasure * 2)  # calculate duration of each strum
        for e in reversed(self.grid_slaves(row=3)):
            if count != 0:
                currMeasure.append(e.get())
                if count == numBeatsPerMeasure * 2:
                    rightArm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        return (leftArm, rightArm)

    def insertChordStrumData(self, leftArm, rightArm):
        # insert left arm data
        i = 0
        for e in reversed(self.grid_slaves(row=2)):
            if i != 0:
                e.delete(0, tk.END)
                e.insert(0, leftArm[i - 1])
            i += 1

        # insert right arm data
        i = 0
        for e in reversed(self.grid_slaves(row=3)):
            if i != 0:
                e.delete(0, tk.END)
                e.insert(0, rightArm[i - 1])
            i += 1

# def add_bar(self):
#     self.bar = BarFrame(master=self)
#     self.bar.grid(row=0, column=1, padx=20)
