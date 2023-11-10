import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename
from tkhtmlview import HTMLScrolledText, RenderHTML
import tkinter.messagebox
import os.path
import tkinter.messagebox
import pandas as pd
import numpy as np
import ast
from queue import Queue
import logging
import UIParse
import json

from UI.audio.AudioHelper import AudioHelper
from UI.constants.StrumPatterns import strum_patterns, strum_options
from UI.constants.TimeSignatures import time_signatures, beat_labels

# TODO: check with Marcus about removing the commented code below
#
# print("PLEASE READ: NOT ALL CHORDS ARE REPRESENTED, BE WARY OF ERROR MESSAGE 'INDEXING OUT OF BOUNDS")
# BPM = 60
# MAX_TIME = 1 / 3
# UDP_IP = "192.168.1.50"
# XARM_IP = '192.168.1.215'
# UDP_PORT = 1001
# pre_count = 1
# STRUM_LEN = 60 / BPM
# measure_time = STRUM_LEN * 4
# OFFSET = 20.5
# STRUM_PT = [372.7, 357.7, 347.7, 337.7, 327.7, 317.7, 292.7]
# PICK_PT = [371.6 - OFFSET, 362.4 - OFFSET, 351.4 - OFFSET, 340.8 - OFFSET, 331.3 - OFFSET, 321.4 - OFFSET]
# INIT_POSE = [684.3, 246.8, 367.7, -90, 0, 0]
# SYNC_RATE = 250
# move_time = 0.1
# ipickeracc = 200
# ipickvel = 50
# pgain = 8000
# right_information = []
# Measure_Timings = STRUM_LEN * 4
# fretnum = []
# fretplay = []
# Rhythm = ""
# rhythm = []
# onsets = [4, 8, 12, 16, 20, 24]

# firstc = []
# # left_arm = []

# repeat = 2
# is_play = False

# left_queue = Queue()
# pick_queue = Queue()
# robot_queue = Queue()
# # left hand cmd trigger in sec
# left_hand_timing = onsets * 1000
# HEADER = '/guitar'
# chords_dir = "Chords - Chords.csv"

# # left_hand_timing[6] -= 150
# # left_hand_timing[12] -= 150
# # left_hand_timing[18] -= 150
# for i in range(7):
#     left_hand_timing = np.insert(left_hand_timing, 3 + i * 3 + i, left_hand_timing[2 + i * 3 + i] + 750)

# left_hand_timing = np.append(1000, left_hand_timing)
# left_hand_timing[-1] += 5000
# for i in range(len(left_hand_timing)):
#     left_hand_timing[i] = np.ceil(left_hand_timing[i])

# print(left_hand_timing)
# # right hand pick cmd trigger in sec
# pick_timing = np.array([0, 1]) * 1000
# robot_timing = 5000
# # song length in sec
# song_length = 25
# logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def UI():
    # GuitarBot UI
    # TODO: scrollbar, bug with adding sections in 2/4
    sections = []
    sectionsDict = {}

    window = tk.Tk(className=' GuitarBot')
    window.geometry("1300x600")

    timeFrame = Frame(window)
    timeFrame.pack()
    sectionsFrame = Frame(window)
    sectionsFrame.pack()

    timeSelection = StringVar(window)

    # function to show popup window for chord notations
    def show_chord_notations_popup():
        popup = tk.Toplevel(window)
        popup.title("Chord Notations")
        popup.geometry('800x500')

        # Add chord notations list (HTML)
        htmlContent = HTMLScrolledText(popup, html=RenderHTML('./UI/components/chord_notation/ChordNotations.html'))
        htmlContent.pack(fill='both', expand=True)
        # htmlContent.fit_height()

        # Add close button
        closeButton = tk.Button(popup, text="Close", command=popup.destroy)
        closeButton.pack()

    #### Section class ####
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
                        if j != 0 and j % len(beat_labels.get(timeSelection.get())) == 0:
                            self.cell.grid(row=i + self.rowOffset, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i + self.rowOffset, column=j)

                        self.cell.insert(END,
                                         beat_labels.get(timeSelection.get())[(j - 1) % len(beat_labels.get(timeSelection.get()))])
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

                            self.cell = OptionMenu(self.root, self.strumPattern, self.strumPattern.get(), *strum_options,
                                                   command=self.fillStrumPattern)
                            self.cell.grid(row=i + self.rowOffset, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=2, font=('Arial', 16))

                        # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                        self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to every input box (adds new measure if pressed)
                        self.cell.bind("<Return>", self.__returnPressed)

                        # TODO: fix auto-tabbing with strums
                        # # jumps to next strum entry if <d, u, or space> pressed
                        # self.cell.bind("d", lambda e: self.__jump_to_next_strum_input(e, i + self.rowOffset, j))
                        # self.cell.bind("u", lambda e: self.__jump_to_next_strum_input(e, i + self.rowOffset, j))
                        # self.cell.bind("D", lambda e: self.__jump_to_next_strum_input(e, i + self.rowOffset, j))
                        # self.cell.bind("U", lambda e: self.__jump_to_next_strum_input(e, i + self.rowOffset, j))

                        # add spacing after last beat of measure
                        if j != 0 and j % len(beat_labels.get(timeSelection.get())) == 0:
                            self.cell.grid(row=i + self.rowOffset, column=j, padx=(0, 30))
                        else:
                            self.cell.grid(row=i + self.rowOffset, column=j)

                        if self.strumPattern.get()[0] == "W":
                            # Wonderwall strum patterns
                            self.cell.insert(END, strum_patterns.get(self.strumPattern.get())[(j - 1) % 32])
                        elif self.strumPattern.get() != "Custom":
                            self.cell.insert(END, strum_patterns.get(self.strumPattern.get())[
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

        # TODO: fix
        def __jump_to_next_strum_input(self, event, row, col):
            # print('got here')
            if (col < self.lastCol):
                self.root.grid_slaves(row=row, column=col + 1)[0].focus_set()

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
            count = 0

            for e in reversed(self.root.grid_slaves(row=3 + self.rowOffset)):
                if count != 0:
                    e.delete(0, END)
                    pattern = strum_patterns.get(self.strumPattern.get())
                    e.insert(END, pattern[(count - 1) % len(pattern)])
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

    initSection = Section(sectionsFrame)
    sections.append(initSection)

    def create_table(section, timeSelection):
        # set default values if needed
        if len(timeSelection.get()) == 0:
            timeSelection.set("4/4")

        num_cols = int(timeSelection.get()[0]) * section.numMeasures * 2
        section.buildTable(num_cols, timeSelection, 0, 1)
        # print("table created")

    def update_table(event):
        # set default values if needed
        if len(timeSelection.get()) == 0:
            timeSelection.set("4/4")

        # reset number of measures back to 1
        initSection.numMeasures = 1
        initSection.strumPattern.set("")

        # update sections list
        sections.clear()
        sections.append(initSection)
        sectionsDisplay.config(state="ENABLED")
        sectionsDisplay.delete(0, END)
        sectionsDisplay.insert(END, len(sections))
        sectionsDisplay.config(state=DISABLED)

        num_cols = int(timeSelection.get()[0]) * initSection.numMeasures * 2
        initSection.editTable(num_cols, timeSelection)
        # print("table updated")

    def add_measure(section):
        section.numMeasures = section.numMeasures + 1
        num_cols = int(timeSelection.get()[0]) * section.numMeasures * 2

        section.addMeasure(num_cols)

    def remove_measure(section):
        if section.numMeasures > 1:
            section.numMeasures = section.numMeasures - 1

            section.removeMeasure()

    # load default table
    create_table(initSection, timeSelection)

    # time signature / bpm / measure dropdowns
    timeMenu = OptionMenu(timeFrame, timeSelection, "4/4", *time_signatures, command=update_table)
    timeLabel = Label(timeFrame, text="Time Signature: ")
    timeLabel.pack(side=LEFT)
    timeMenu.pack(side=LEFT)

    bpmInput = Entry(timeFrame, width=3, font=('Arial', 16))
    bpmInput.insert(END, "60")  # set default bpm
    bpmLabel = Label(timeFrame, text="bpm: ")
    bpmLabel.pack(side=LEFT)
    bpmInput.pack(side=LEFT)

    # Chord Notations popup button
    notationsPopupBtn = Button(timeFrame, text="Chord Notations", width=12, command=show_chord_notations_popup)
    notationsPopupBtn.pack(pady=1)

    # add/remove sections
    def add_section():
        newSection = Section(sectionsFrame)
        sections.append(newSection)
        # print(newSection.name)
        # print(newSection.sectionNum)
        create_table(newSection, timeSelection)

        # update display
        sectionsDisplay.config(state="ENABLED")
        sectionsDisplay.delete(0, END)
        sectionsDisplay.insert(END, len(sections))
        sectionsDisplay.config(state=DISABLED)

        return newSection

    def remove_section():
        if (len(sections) > 1):
            removedSection = sections.pop()
            for i in range(5):
                for e in removedSection.root.grid_slaves(row=removedSection.rowOffset + 4 - i):
                    e.grid_forget()

            # update display
            sectionsDisplay.config(state="ENABLED")
            sectionsDisplay.delete(0, END)
            sectionsDisplay.insert(END, len(sections))
            sectionsDisplay.config(state=DISABLED)

    # buttons for adding/removing sections
    sectionBtnsFrame = Frame(window)

    sectionsLabel = Label(sectionBtnsFrame, text="Sections: ")
    sectionsDisplay = Entry(sectionBtnsFrame, width=2, font=('Arial', 16))
    sectionsDisplay.insert(END, len(sections))
    sectionsDisplay.config(state=DISABLED)

    addSectionBtn = Button(sectionBtnsFrame, text="+", width=1, command=add_section)
    removeSectionBtn = Button(sectionBtnsFrame, text="-", width=1, command=remove_section)

    sectionsLabel.pack(side=LEFT)
    removeSectionBtn.pack(side=LEFT)
    sectionsDisplay.pack(side=LEFT)
    addSectionBtn.pack(side=LEFT)
    sectionBtnsFrame.pack(pady=(10, 5))

    def build_arm_lists():
        # build section dict
        for section in sections:
            name = section.name
            data = section.buildChordStrumData(timeSelection)  # in form (left_arm, right_arm) for each section
            sectionsDict[name] = data

        # parse song input
        input = songInput.get()
        parsed_input = input.replace(", ", ",").split(",")

        # build complete left_arm, right_arm lists
        left_arm = []
        right_arm = []
        for section in parsed_input:
            if section in sectionsDict.keys():
                for m in sectionsDict[section][0]:
                    left_arm.append(m.copy())

                for m in sectionsDict[section][1]:
                    right_arm.append(m.copy())

        return (left_arm, right_arm)

    def collect_chord_strum_data():
        global left_arm
        global right_arm
        global mtime

        left_arm, right_arm = build_arm_lists()

        if songTitle.get() != "":
            name = songTitle.get()
        else:
            name = "default"

        write_to_json(name, songInput.get())

        # write left_arm, right_arm arrays to json file
        with open('output/output.json', 'w') as file:
            # write left_arm, right_arm to json
            file.write(json.dumps([left_arm, right_arm], indent=4))

        print("left arm: ", left_arm)
        print("right arm: ", right_arm)
        print("input: ", songInput.get())
        BeatsPerMinute = int(bpmInput.get())
        strumlen = 60 / BeatsPerMinute
        mtime = strumlen * 4
        tkinter.messagebox.showinfo("Alert", "Song sent to GuitarBot.")

    def write_to_json(name, input):
        # check to make sure user does not accidentally overwrite existing song
        if name != "default" and os.path.isfile('songs/' + name + '.json'):
            response = tkinter.messagebox.askquestion("Warning",
                                                      "A song with the same name is already saved. Would you like to overwrite the " +
                                                      "contents of the existing song? (If you select no, song will be saved as a new file.)")
            if response == 'no':
                name = name + "(1)"

        # organize general song data
        song_dict = {
            "name": name,
            "timeSig": timeSelection.get(),
            "bpm": bpmInput.get(),
            "input": input
        }

        json_data = []
        json_data.append(song_dict)

        # add individual section data to json_data
        for section in sections:
            data = section.buildChordStrumData(timeSelection)
            section_dict = {}
            section_dict["name"] = section.name
            section_dict["numMeasures"] = section.numMeasures
            section_dict["strumPattern"] = section.strumPattern.get()
            section_dict["leftArm"] = data[0]
            section_dict["rightArm"] = data[1]
            json_data.append(section_dict)

        with open('songs/' + name + '.json', 'w') as file:
            # write data to json
            file.write(json.dumps(json_data, indent=4))

    def load_from_json():
        path = askopenfilename()
        print(str(path))
        with open(path, 'r') as file:
            json_data = json.load(file)

        # set general song data
        song_dict = json_data.pop(0)

        # update UI components
        songTitle.delete(0, END)
        songTitle.insert(0, song_dict["name"])
        songInput.delete(0, END)
        songInput.insert(0, song_dict["input"])
        bpmInput.delete(0, END)
        bpmInput.insert(0, song_dict["bpm"])
        timeSelection.set(song_dict["timeSig"])

        # reset UI to initial state
        update_table(None)

        # create and populate sections with data
        count = 0
        for section_dict in json_data:
            if count == 0:
                section = initSection
            else:
                section = add_section()

            section.name = section_dict["name"]
            section.nameInput.insert(0, section.name)

            for i in range(1, int(section_dict["numMeasures"])):
                add_measure(section)

            section.strumPattern.set(section_dict["strumPattern"])
            # flatten input arrays
            leftArm = [item for sublist in section_dict["leftArm"] for item in sublist]
            rightArm = [item for sublist in section_dict["rightArm"] for item in sublist]
            section.insertChordStrumData(leftArm, rightArm)
            count += 1


    def preview_song():
        left_arm, right_arm = build_arm_lists()
        AudioHelper.preview_song(left_arm, right_arm, int(bpmInput.get()), 2)

    # create inputs for song title/structure to send to bot
    # song components should be comma delimited (Ex: Verse, Chorus, Bridge)
    # TODO: update UI to be more like a series of dropdowns
    songFrame = Frame(window)
    titleFrame = Frame(songFrame)
    inputFrame = Frame(songFrame)
    btnFrame = Frame(window)

    songTitle = Entry(titleFrame, width=12, font=('Arial', 14))
    titleLabel = Label(titleFrame, text="Song Title:", width=10)
    titleLabel.pack(side=LEFT)
    songTitle.pack(side=LEFT)

    songInput = Entry(inputFrame, width=25, font=('Arial', 14))
    inputLabel = Label(inputFrame, text="Input (v, c,...):", width=10)
    inputLabel.pack(side=LEFT)
    songInput.pack(side=LEFT)

    titleFrame.pack()
    inputFrame.pack()
    songFrame.pack(pady=(20, 5))

    send = Button(btnFrame, text="Send", width=6, command=collect_chord_strum_data)
    preview = Button(btnFrame, text="Preview", width=6, command=preview_song)
    load = Button(btnFrame, text="Load", width=6, command=load_from_json)
    send.pack(pady=1)
    preview.pack(pady=1)
    load.pack(pady=1)

    btnFrame.pack()

    # add keyboard shortcut Ctrl + S to send data to bot
    def ctrlS_send(e):
        collect_chord_strum_data()

    window.bind('<Control-s>', lambda e: ctrlS_send(e))

    window.mainloop()

    return right_arm, left_arm, mtime


# for testing purposes
UI()