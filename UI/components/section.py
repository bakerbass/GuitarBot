import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *

beatLabelsDict = {
        "2/4": ["1", "+", "2", "+"],
        "3/4": ["1", "+", "2", "+", "3", "+"],
        "4/4": ["1", "+", "2", "+", "3", "+", "4", "+"]
    }

strumOptionList = [
        "Custom",
        "Down/Up",
        "Downs",
        "Ups",
        "WV",
        "WC",
        "WB"
    ]

strumPatternDict = {
        "Down/Up": ["D", "U"],
        "Downs": ["D", ""],
        "Ups": ["", "U"],

        # wonderwall strum patterns below (built for 4/4, 4 bars, double time) ->
        "WV": ["D", "", "D", "", "D", "", "", "U", "D", "U", "D", "", "D", "", "", "U",
               "D", "U", "D", "", "D", "", "D", "U", "", "U", "D", "U", "D", "U", "D", "U", ],
        "WC": ["D", "", "D", "", "D", "", "", "U", "D", "U", "D", "", "D", "", "", "U",
               "D", "U", "D", "", "D", "", "", "U", "D", "U", "D", "", "D", "", "", "U"],
        "WB": ["D", "", "D", "", "D", "U", "D", "U", "", "U", "D", "U", "D", "", "D", "",
               "D", "U", "D", "", "D", "", "D", "U", "", "U", "D", "U", "D", "U", "D", "U", ]
    }

# defines the chart module with chords and strumming inputs
class Section:
        def __init__(self, root, timeSignature):
            self.root = root
            self.lastColumn = 0
            self.name = ""
            self.nameInput = None
            self.strumPatternSelection = StringVar(root)
            self.numMeasures = 1
            self.beatsPerMeasure = int(timeSignature[0])
            self.subdivisionsPerMeasure = 16 / int(timeSignature[2]) * self.beatsPerMeasure
            self.beatLabels = beatLabelsDict[timeSignature]

            self.chordRowTabOrder = []
            self.strumRowTabOrder = []

        def update(self, startColumn):
            # build chords/strum chart
            for i in range(0, 4):
                # print(i + self.offset)
                j = startColumn
                while j <= self.subdivisionsPerMeasure * self.numMeasures:
                    currMeasure = 0
                    if i == 0 and currMeasure <= self.numMeasures:
                        # MEASURE LABELS
                        # account for bar label placement shift
                        if (j != 0 and j == startColumn):
                            j -= 1

                        labelText = "Bar " + str(currMeasure)
                        self.cell = Label(self.root, width=4, text=labelText)
                        self.cell.grid(row=i, column=j + self.beatsPerMeasure, sticky=W,
                                       columnspan=self.subdivisionsPerMeasure)
                        j += self.subdivisionsPerMeasure
                        currMeasure += 1
                        continue
                    elif i == 1:
                        # BEAT LABELS
                        if j == 0:
                            # add empty label at beginning of row (placeholder to align w/ below rows)
                            self.cell = Label(self.root, width=6, text="")
                            self.cell.grid(row=i, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=2, font=('Arial', 16, 'bold'))

                        # add space after last beat of measure
                        if j != 0 and j % self.beatsPerMeasure == 0:
                            self.cell.grid(row=i, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i, column=j)

                        self.cell.insert(END,
                                         self.beatLabels[(j - 1) % self.beatsPerMeasure])
                        self.cell.config(state=DISABLED)
                    elif i == 2:
                        # CHORD INPUTS
                        if j == 0:
                            # add "Chords: " label at beginning of row
                            self.cell = Label(self.root, width=6, text="Chords: ")
                            self.cell.grid(row=i, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=6, font=('Arial', 16))

                        # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                        self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to every input box (adds new measure if pressed)
                        self.cell.bind("<Return>", self.__returnPressed)

                        self.cell.grid(row=i, column=j, sticky=W, columnspan=2)
                        self.chordRowTabOrder.append(self.cell)

                        self.cell.insert(END, "")
                        j += 1
                    elif i == 3:
                        # STRUM INPUTS
                        if j == 0:
                            # add "Strum Pattern: " dropdown at beginning of row
                            if self.strumPatternSelection.get() == "":
                                self.strumPatternSelection.set("Custom")

                            self.cell = OptionMenu(self.root, self.strumPatternSelection, self.strumPatternSelection.get(), *strumOptionList,
                                                   command=self.fillStrumPattern)
                            self.cell.grid(row=i, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=2, font=('Arial', 16))

                        # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                        self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to every input box (adds new measure if pressed)
                        self.cell.bind("<Return>", self.__returnPressed)

                        # add spacing after last beat of measure
                        if j != 0 and j % self.beatsPerMeasure == 0:
                            self.cell.grid(row=i, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i, column=j)

                        if self.strumPatternSelection.get()[0] == "W":
                            # Wonderwall strum patterns
                            self.cell.insert(END, strumPatternDict.get(self.strumPatternSelection.get())[(j - 1) % 32])
                        elif self.strumPatternSelection.get() != "Custom":
                            self.cell.insert(END, strumPatternDict.get(self.strumPatternSelection.get())[
                                (j + 1) % 2])  # autofill newly added cells with selected strum pattern
                        else:
                            self.cell.insert(END, "")

                        self.strumRowTabOrder.append(self.cell)
                    j += 1

            # set default focus to first input of last measure
            self.root.grid_slaves(row=2, column=startColumn + 1)[0].focus_set()

            # update lastColumn
            self.lastColumn = self.subdivisionsPerMeasure * self.numMeasures

            # place clear button
            self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
            self.cell.grid(row=4, column=j - 3, columnspan=2, sticky=W)

            # components for section name input
            self.cell = Label(self.root, width=5, text="Name:")
            self.cell.grid(row=4, column=j - 7, columnspan=2, sticky=E)
            nameInput = Entry(self.root, width=6, font=('Arial', 14))
            self.nameInput = nameInput
            nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
            nameInput.grid(row=4, column=j - 5, columnspan=2, sticky=W)

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

            # delete previous clear button, name label/input (will get re-added during the buildTable() call)
            for e in self.root.grid_slaves(row=4):
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
                    for e in self.root.grid_slaves(column=self.lastColumn - i, row=j):
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
            self.root.grid_slaves(row=2, column=self.lastColumn - self.subdivisionsPerMeasure + 1)[
                0].focus_set()

            # put bar label back
            labelText = "Bar " + str(self.numMeasures)
            self.cell = Label(self.root, width=4, text=labelText)
            self.cell.grid(row=0, column=self.lastColumn - self.beatsPerMeasure, sticky=W,
                           columnspan=self.subdivisionsPerMeasure)

            # put clear button back
            self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
            self.cell.grid(row=4, column=self.lastColumn - 2, columnspan=2, sticky=W)

            # put components for section name input back
            self.cell = Label(self.root, width=5, text="Name:")
            self.cell.grid(row=4, column=self.lastColumn - 6, columnspan=2, sticky=E)
            nameInput = Entry(self.root, width=6, font=('Arial', 14))
            nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
            nameInput.grid(row=4, column=self.lastColumn - 4, columnspan=2, sticky=W)
            # print("measure removed")

        def editTable(self, num_cols, timeSignature):
            # delete prev rows
            for w in self.root.grid_slaves():
                w.grid_forget()

            self.update(num_cols, timeSignature, 0, 1)

        def clearTable(self):
            count = 0
            for e in reversed(self.root.grid_slaves(row=2)):
                if count != 0:
                    e.delete(0, END)
                count += 1

            count = 0
            for e in reversed(self.root.grid_slaves(row=3)):
                if count != 0:
                    e.delete(0, END)
                count += 1

            # clear name input
            self.root.grid_slaves(row=4, column=self.lastColumn - 4)[0].delete(0, END)

            # print("table cleared")

        def fillStrumPattern(self, event):
            # implementation choice: autofill entire table on selection? Or just set that selection for new bars?
            count = 0

            for e in reversed(self.root.grid_slaves(row=3)):
                if count != 0:
                    e.delete(0, END)
                    if self.strumPatternSelection.get()[0] == "W":
                        # Wonderwall strum patterns
                        e.insert(END, strumPatternDict.get(self.strumPatternSelection.get())[(count - 1) % 32])
                    elif self.strumPatternSelection.get() != "Custom":
                        e.insert(END, strumPatternDict.get(self.strumPatternSelection.get())[(count + 1) % 2])
                count += 1

        def buildChordStrumData(self, timeSignature):
            leftArm = []
            rightArm = []
            numBeatsPerMeasure = (int)(timeSignature.get()[0])

            # generate left arm data
            currMeasure = []
            count = 0
            for e in reversed(self.root.grid_slaves(row=2)):
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
            for e in reversed(self.root.grid_slaves(row=3)):
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
            for e in reversed(self.root.grid_slaves(row=2)):
                if i != 0:
                    e.delete(0, END)
                    e.insert(0, leftArm[i - 1])
                i += 1

            # insert right arm data
            i = 0
            for e in reversed(self.root.grid_slaves(row=3)):
                if i != 0:
                    e.delete(0, END)
                    e.insert(0, rightArm[i - 1])
                i += 1