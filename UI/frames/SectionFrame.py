import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from constants.strum_patterns import *
from constants.time_signatures import *

class SectionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, id, width, height, time_signature):
        super().__init__(master=master, width=width, height=height, orientation='horizontal')
        self.id = id

        self.width = width
        self.height = height

        self.time_signature = time_signature
        self.last_column = 0
        self.strum_pattern_sel = tk.StringVar(self, "Custom")
        self.num_measures = 0
        self.beats_per_measure = int(time_signature[0])
        self.subdiv_per_measure = self.beats_per_measure * 2
        self.beat_labels = beat_labels[time_signature]

        self.chords_tab_order = []
        self.strums_tab_order = []

        self.addMeasure()
        print(self.last_column)

    def update(self, startColumn):
        # build chords/strum chart
        for i in range(0, 4):
            # print(i + self.offset)
            j = startColumn
            while j <= self.subdiv_per_measure * self.num_measures:
                currMeasure = 0
                if i == 0 and currMeasure <= self.num_measures:
                    # MEASURE LABELS
                    # account for bar placement shift
                    if (j != 0 and j == startColumn):
                        j -= 1

                    self.cell = tk.Label(self, width=4, text="Bar " + str(currMeasure))
                    self.cell.grid(row=i, column=j + self.beats_per_measure, sticky='w',
                                    columnspan=self.subdiv_per_measure)
                    j += self.subdiv_per_measure
                    currMeasure += 1
                    continue
                elif i == 1:
                    # BEAT LABELS
                    if j == 0:
                        # add empty label at beginning of row (placeholder to align w/ below rows)
                        self.cell = tk.Label(self, width=6, text="")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = ttk.Entry(self, width=2, font=('Arial', 16, 'bold'))

                    # add space after last beat of measure
                    if j != 0 and j % self.subdiv_per_measure == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    self.cell.insert(tk.END,
                                        self.beat_labels[(j - 1) % self.beats_per_measure])
                    self.cell.config(state=tk.DISABLED)
                elif i == 2:
                    # CHORD INPUTS
                    if j == 0:
                        # add "Chords: " label at beginning of row
                        self.cell = tk.Label(self, width=6, text="Chords: ")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = ttk.Entry(self, width=6, font=('Arial', 16))

                    # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                    # add <Return> event handler to every input box (adds new measure if pressed)
                    self.cell.bind("<Return>", self.__returnPressed)

                    self.cell.grid(row=i, column=j, sticky='w', columnspan=2)
                    self.chords_tab_order.append(self.cell)

                    self.cell.insert(tk.END, "")
                    j += 1
                elif i == 3:
                    # STRUM INPUTS
                    if j == 0:
                        # add "Strum Pattern: " dropdown at beginning of row
                        if self.strum_pattern_sel.get() == "":
                            self.strum_pattern_sel.set("Custom")

                        self.cell = ttk.OptionMenu(self, self.strum_pattern_sel, self.strum_pattern_sel.get(), *strum_options,
                                                command=self.fillStrumPattern)
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = ttk.Entry(self, width=2, font=('Arial', 16))

                    # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                    # add <Return> event handler to every input box (adds new measure if pressed)
                    self.cell.bind("<Return>", self.__returnPressed)

                    # add spacing after last beat of measure
                    if j != 0 and j % self.beats_per_measure == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    if (self.strum_pattern_sel.get() != "") and self.strum_pattern_sel.get()[0] == "W":
                        # Wonderwall strum patterns
                        self.cell.insert(tk.END, strum_patterns.get(self.strum_pattern_sel.get())[(j - 1) % 32])
                    elif self.strum_pattern_sel.get() != "Custom":
                        self.cell.insert(tk.END, strum_patterns.get(self.strum_pattern_sel.get())[
                            (j + 1) % 2])  # autofill newly added cells with selected strum pattern
                    else:
                        self.cell.insert(tk.END, "")

                    self.strums_tab_order.append(self.cell)
                j += 1

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=startColumn + 1)[0].focus_set()

        # update lastColumn
        self.last_column = self.subdiv_per_measure * self.num_measures

        # components for section name input
        # NOTE: may be useful later
        #nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))

        # set tabbing order
        self.__setTabOrder()

    # TODO: fix bug when tabbing to name after removing a measure (not urgent)
    def __setTabOrder(self):
        # NOTE: if user presses tab on last chord input in a section, focus will go to the first strum input on the next row

        # iterate through the "Chords" row, set tabbing order from left -> right
        for cell in self.chords_tab_order:
            cell.lift()

        # iterate through the "Strums" row, set tabbing order from left -> right
        for cell in self.strums_tab_order:
            cell.lift()

    # event handler for add measure (Enter)
    def __returnPressed(self, event):
        self.addMeasure(self)

    def addMeasure(self):
        self.num_measures = self.num_measures + 1

        self.update(self.last_column + 1)
        # print("measure added")

    # event handler for remove measure (Shift+BackSpace)
    def __backspacePressed(self, event):
        self.removeMeasure(self)

    def removeMeasure(self):
        # minimum of 1 measure per section
        if self.num_measures > 1:
            self.num_measures = self.num_measures - 1

        # delete all components in last measure
        for i in range(self.subdiv_per_measure):
            for j in range(5):
                for e in self.grid_slaves(column=self.last_column - i, row=j):
                    e.grid_forget()

                    # remove deleted cells from tab orders
                    if j == 2:
                        self.chords_tab_order.pop()
                    if j == 3:
                        self.strums_tab_order.pop()

                    self.__setTabOrder()

        # update last column
        self.last_column = self.last_column - self.subdiv_per_measure

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=self.last_column - self.subdiv_per_measure + 1)[
            0].focus_set()

        # put bar labels back
        self.cell = tk.Label(self, width=4, text="Bar " + str(self.num_measures))
        self.cell.grid(row=0, column=self.last_column - self.beats_per_measure, sticky='w',
                        columnspan=self.subdiv_per_measure)

        # print("measure removed")

    # def editTable(self, num_cols):
    #     # delete prev rows
    #     for w in self.grid_slaves():
    #         w.grid_forget()

    #     self.update(num_cols, self.time_signature, 0, 1)

    def clear_table(self):
        for e in reversed(self.grid_slaves(row=2)):
            e.delete(0, tk.END)

        for e in reversed(self.grid_slaves(row=3)):
            e.delete(0, tk.END)

        # print("table cleared")

    def fillStrumPattern(self, event):
        # implementation choice: autofill entire table on selection? Or just set that selection for new bars?
        count = 0

        for e in reversed(self.grid_slaves(row=3)):
            if count != 0:
                e.delete(0, tk.END)
                if self.strum_pattern_sel.get()[0] == "W":
                    # Wonderwall strum patterns
                    e.insert(tk.END, strum_patterns.get(self.strum_pattern_sel.get())[(count - 1) % 32])
                elif self.strum_pattern_sel.get() != "Custom":
                    e.insert(tk.END, strum_patterns.get(self.strum_pattern_sel.get())[(count + 1) % 2])
            count += 1

    def build_arm_lists(self):
        left_arm = []
        right_arm = []
        numBeatsPerMeasure = (int)(self.time_signature[0])

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
                    left_arm.append(currMeasure)
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
                    right_arm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        return (left_arm, right_arm)

    def insertChordStrumData(self, left_arm, right_arm):
        # insert left arm data
        i = 0
        for e in reversed(self.grid_slaves(row=2)):
            if i != 0:
                e.delete(0, tk.END)
                e.insert(0, left_arm[i - 1])
            i += 1

        # insert right arm data
        i = 0
        for e in reversed(self.grid_slaves(row=3)):
            if i != 0:
                e.delete(0, tk.END)
                e.insert(0, right_arm[i - 1])
            i += 1
