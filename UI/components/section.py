import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox

# defines the chart module with chords and strumming inputs
class Section:
        def __init__(self, root):
            self.root = root
            self.barCount = 0
            self.lastCol = 0
            self.name = ""
            self.nameInput = None
            self.sectionNum = len(sections)
            self.rowOffset = self.sectionNum * 5
            self.strumPattern = StringVar(root)
            self.numMeasures = 1

            self.chordRowTabOrder = []
            self.strumRowTabOrder = []

        def buildTable(self, numColumns, timeSelection, startColumn, barCount):
            # build chords/strum chart
            for i in range(0, 4):
                # print(i + self.offset)
                j = startColumn
                while j <= numColumns:
                    if i == 0 and barCount <= self.numMeasures:
                        # MEASURE LABELS
                        # account for bar label placement shift
                        if (j != 0 and j == startColumn):
                            j -= 1

                        labelText = "Bar " + str(barCount)
                        self.cell = Label(self.root, width=4, text=labelText)
                        self.cell.grid(row=i + self.rowOffset, column=j + int(timeSelection.get()[0]), sticky=W,
                                       columnspan=int(timeSelection.get()[0]) * 2)
                        j += int(timeSelection.get()[0]) * 2
                        barCount += 1
                        continue
                    elif i == 1:
                        # BEAT LABELS
                        if j == 0:
                            # add empty label at beginning of row (placeholder to align w/ below rows)
                            self.cell = Label(self.root, width=6, text="")
                            self.cell.grid(row=i + self.rowOffset, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=2, font=('Arial', 16, 'bold'))

                        # add space after last beat of measure
                        if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                            self.cell.grid(row=i + self.rowOffset, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i + self.rowOffset, column=j)

                        self.cell.insert(END,
                                         beats.get(timeSelection.get())[(j - 1) % len(beats.get(timeSelection.get()))])
                        self.cell.config(state=DISABLED)
                    elif i == 2:
                        # CHORD INPUTS
                        if j == 0:
                            # add "Chords: " label at beginning of row
                            self.cell = Label(self.root, width=6, text="Chords: ")
                            self.cell.grid(row=i + self.rowOffset, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=6, font=('Arial', 16))

                        # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                        self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to every input box (adds new measure if pressed)
                        self.cell.bind("<Return>", self.__returnPressed)

                        self.cell.grid(row=i + self.rowOffset, column=j, sticky=W, columnspan=2)
                        self.chordRowTabOrder.append(self.cell)

                        self.cell.insert(END, "")
                        j += 1
                    elif i == 3:
                        # STRUM INPUTS
                        if j == 0:
                            # add "Strum Pattern: " dropdown at beginning of row
                            if self.strumPattern.get() == "":
                                self.strumPattern.set("Custom")

                            self.cell = OptionMenu(self.root, self.strumPattern, self.strumPattern.get(), *strumOptions,
                                                   command=self.fillStrumPattern)
                            self.cell.grid(row=i + self.rowOffset, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=2, font=('Arial', 16))

                        # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                        self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to every input box (adds new measure if pressed)
                        self.cell.bind("<Return>", self.__returnPressed)

                        # add spacing after last beat of measure
                        if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                            self.cell.grid(row=i + self.rowOffset, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i + self.rowOffset, column=j)

                        if self.strumPattern.get()[0] == "W":
                            # Wonderwall strum patterns
                            self.cell.insert(END, strumPatterns.get(self.strumPattern.get())[(j - 1) % 32])
                        elif self.strumPattern.get() != "Custom":
                            self.cell.insert(END, strumPatterns.get(self.strumPattern.get())[
                                (j + 1) % 2])  # autofill newly added cells with selected strum pattern
                        else:
                            self.cell.insert(END, "")

                        self.strumRowTabOrder.append(self.cell)
                    j += 1

            # set default focus to first input of last measure
            self.root.grid_slaves(row=2 + self.rowOffset, column=startColumn + 1)[0].focus_set()

            # update table fields barCount, lastCol
            self.barCount = barCount - 1
            self.lastCol = numColumns

            # place clear button
            self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
            self.cell.grid(row=4 + self.rowOffset, column=j - 3, columnspan=2, sticky=W)

            # components for section name input
            self.cell = Label(self.root, width=5, text="Name:")
            self.cell.grid(row=4 + self.rowOffset, column=j - 7, columnspan=2, sticky=E)
            nameInput = Entry(self.root, width=6, font=('Arial', 14))
            self.nameInput = nameInput
            nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
            nameInput.grid(row=4 + self.rowOffset, column=j - 5, columnspan=2, sticky=W)

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

        def __returnPressed(self, event):
            add_measure(self)

        def __backspacePressed(self, event):
            remove_measure(self)

        def addMeasure(self, num_cols):
            # delete previous clear button, name label/input (will get re-added during the buildTable() call)
            for e in self.root.grid_slaves(row=4 + self.rowOffset):
                e.grid_forget()

            self.buildTable(num_cols, timeSelection, self.lastCol + 1, self.barCount + 1)
            self.nameInput.insert(0, self.name)
            # print("measure added")

        def removeMeasure(self):
            # delete all components in last measure
            for i in range(int(timeSelection.get()[0]) * 2):
                for j in range(5):
                    for e in self.root.grid_slaves(column=self.lastCol - i, row=j + self.rowOffset):
                        e.grid_forget()

                        # remove deleted cells from tab orders
                        if j == 2:
                            self.chordRowTabOrder.pop()
                        if j == 3:
                            self.strumRowTabOrder.pop()

                        self.__setTabOrder()

            # update last column
            self.lastCol = self.lastCol - int(timeSelection.get()[0]) * 2
            self.barCount -= 1

            # set default focus to first input of last measure
            self.root.grid_slaves(row=2 + self.rowOffset, column=self.lastCol - int(timeSelection.get()[0]) * 2 + 1)[
                0].focus_set()

            # put bar label back
            labelText = "Bar " + str(self.barCount)
            self.cell = Label(self.root, width=4, text=labelText)
            self.cell.grid(row=0 + self.rowOffset, column=self.lastCol - int(timeSelection.get()[0]), sticky=W,
                           columnspan=int(timeSelection.get()[0]) * 2)

            # put clear button back
            self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
            self.cell.grid(row=4 + self.rowOffset, column=self.lastCol - 2, columnspan=2, sticky=W)

            # put components for section name input back
            self.cell = Label(self.root, width=5, text="Name:")
            self.cell.grid(row=4 + self.rowOffset, column=self.lastCol - 6, columnspan=2, sticky=E)
            nameInput = Entry(self.root, width=6, font=('Arial', 14))
            nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
            nameInput.grid(row=4 + self.rowOffset, column=self.lastCol - 4, columnspan=2, sticky=W)
            # print("measure removed")

        def editTable(self, num_cols, timeSelection):
            # delete prev rows
            for w in self.root.grid_slaves():
                w.grid_forget()

            self.buildTable(num_cols, timeSelection, 0, 1)

        def clearTable(self):
            count = 0
            for e in reversed(self.root.grid_slaves(row=2 + self.rowOffset)):
                if count != 0:
                    e.delete(0, END)
                count += 1

            count = 0
            for e in reversed(self.root.grid_slaves(row=3 + self.rowOffset)):
                if count != 0:
                    e.delete(0, END)
                count += 1

            # clear name input
            self.root.grid_slaves(row=4 + self.rowOffset, column=self.lastCol - 4)[0].delete(0, END)

            # print("table cleared")

        def fillStrumPattern(self, event):
            # implementation choice: autofill entire table on selection? Or just set that selection for new bars?
            count = 0

            for e in reversed(self.root.grid_slaves(row=3 + self.rowOffset)):
                if count != 0:
                    e.delete(0, END)
                    if self.strumPattern.get()[0] == "W":
                        # Wonderwall strum patterns
                        e.insert(END, strumPatterns.get(self.strumPattern.get())[(count - 1) % 32])
                    elif self.strumPattern.get() != "Custom":
                        e.insert(END, strumPatterns.get(self.strumPattern.get())[(count + 1) % 2])
                count += 1

        def buildChordStrumData(self, timeSelection):
            leftArm = []
            rightArm = []
            numBeatsPerMeasure = (int)(timeSelection.get()[0])
            bpm = (int)(bpmInput.get())

            # generate left arm data
            currMeasure = []
            count = 0
            for e in reversed(self.root.grid_slaves(row=2 + self.rowOffset)):
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
            for e in reversed(self.root.grid_slaves(row=3 + self.rowOffset)):
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
            for e in reversed(self.root.grid_slaves(row=2 + self.rowOffset)):
                if i != 0:
                    e.delete(0, END)
                    e.insert(0, leftArm[i - 1])
                i += 1

            # insert right arm data
            i = 0
            for e in reversed(self.root.grid_slaves(row=3 + self.rowOffset)):
                if i != 0:
                    e.delete(0, END)
                    e.insert(0, rightArm[i - 1])
                i += 1

    ##### end of Section class ####