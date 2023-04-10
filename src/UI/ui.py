import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import csv
import os.path

# GuitarBot UI
# TODO: scrollbar, load in csv, bug with adding sections in 2/4
sections = []
sectionsDict = {}

window = tk.Tk(className=' GuitarBot')
window.geometry("1300x600")

timeFrame = Frame(window)
timeFrame.pack()
sectionsFrame = Frame(window)
sectionsFrame.pack()

timeSigs = [
    "2/4",
    "3/4",
    "4/4"
]

beats = {
    "2/4": ["1", "+", "2", "+"],
    "3/4": ["1", "+", "2", "+", "3", "+"],
    "4/4": ["1", "+", "2", "+", "3", "+", "4", "+"]
}

strumOptions = [
    "Custom",
    "Down/Up",
    "Downs",
    "Ups",
]

strumPatterns = {
    "Down/Up": ["D", "U"],
    "Downs": ["D", ""],
    "Ups": ["", "U"]
}

timeSelection = StringVar(window)

#### Section class ####
# defines the chart module with chords and strumming inputs
# TODO:
class Section:
    def __init__(self, root):
        self.root = root
        self.barCount = 0
        self.lastCol = 0
        self.name = ""
        self.sectionNum = len(sections)
        self.offset = self.sectionNum * 5
        self.strumPattern = StringVar(root)
        self.numMeasures = 1

    def buildTable(self, num_cols, timeSelection, start, barCount):        
        # build chords/strum chart
        for i in range(0, 4):
            # print(i + self.offset)
            j = start
            while j <= num_cols:
                if i == 0 and barCount <= self.numMeasures:
                    # MEASURE LABELS
                    # account for bar label placement shift
                    if (j != 0 and j == start):
                        j -= 1

                    labelText = "Bar " + str(barCount)
                    self.cell = Label(self.root, width=4, text=labelText)
                    self.cell.grid(row=i + self.offset, column=j + int(timeSelection.get()[0]), sticky=W, columnspan=int(timeSelection.get()[0]) * 2)
                    j += int(timeSelection.get()[0]) * 2
                    barCount += 1
                    continue
                elif i == 1:
                    # BEAT LABELS
                    if j == 0:
                        # add empty label at beginning of row (placeholder to align w/ below rows)
                        self.cell = Label(self.root, width=6, text="")
                        self.cell.grid(row=i + self.offset, column=j)
                        j += 1
                        continue

                    self.cell = Entry(self.root, width=2, font=('Arial', 16, 'bold'))
                
                    # add space after last beat of measure
                    if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                        self.cell.grid(row=i + self.offset, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i + self.offset, column=j)

                    self.cell.insert(END, beats.get(timeSelection.get())[(j - 1) % len(beats.get(timeSelection.get()))])
                    self.cell.config(state=DISABLED)
                elif i == 2:
                        # CHORD INPUTS
                        if j == 0:
                            # add "Chords: " label at beginning of row
                            self.cell = Label(self.root, width=6, text="Chords: ")
                            self.cell.grid(row=i + self.offset, column=j)
                            j += 1
                            continue

                        self.cell = Entry(self.root, width=6, font=('Arial',16))

                        # add <BackSpace> event handler to first chord input in each measure
                        if j == 1 or j == start:
                            self.cell.bind("<BackSpace>", self.__backspacePressed)

                        # add <Return> event handler to last chord input in each measure
                        if j != 0 and (j + 1) % len(beats.get(timeSelection.get())) == 0:
                            self.cell.bind("<Return>", self.__returnPressed)

                        self.cell.grid(row=i + self.offset, column=j, sticky=W, columnspan=2)

                        self.cell.insert(END, "")
                        j += 1
                elif i == 3:
                    # STRUM INPUTS
                    if j == 0:
                        # add "Strum Pattern: " dropdown at beginning of row
                        if self.strumPattern.get() == "":
                            self.strumPattern.set("Custom")
                        
                        self.cell = OptionMenu(self.root, self.strumPattern, self.strumPattern.get(), *strumOptions, command=self.fillStrumPattern)
                        self.cell.grid(row=i + self.offset, column=j)
                        j += 1
                        continue

                    self.cell = Entry(self.root, width=2, font=('Arial',16))

                    # add spacing after last beat of measure
                    if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                        self.cell.grid(row=i + self.offset, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i + self.offset, column=j)

                    if self.strumPattern.get() != "Custom":
                        self.cell.insert(END, strumPatterns.get(self.strumPattern.get())[(j + 1) % 2]) # autofill newly added cells with selected strum pattern
                    else:
                        self.cell.insert(END, "")
                j += 1

        # set default focus to first input of last measure
        self.root.grid_slaves(row=2 + self.offset, column=start + 1)[0].focus_set()
        
        # update table fields barCount, lastCol
        self.barCount = barCount - 1
        self.lastCol = num_cols

        # place clear button
        self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=4 + self.offset, column=j - 3, columnspan=2, sticky=W)

        # components for section name input
        self.cell = Label(self.root, width=5, text="Name:")
        self.cell.grid(row=4 + self.offset, column=j - 7, columnspan=2, sticky=E)
        nameInput = Entry(self.root, width=6, font=('Arial',14))
        nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
        nameInput.grid(row=4 + self.offset, column=j - 5, columnspan=2, sticky=W)

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
        for e in self.root.grid_slaves(row=4 + self.offset):
            e.grid_forget()

        self.buildTable(num_cols, timeSelection, self.lastCol + 1, self.barCount + 1)
        # print("measure added")

    def removeMeasure(self):
        # delete all components in last measure
        for i in range(int(timeSelection.get()[0]) * 2):
            for j in range(5):
                for e in self.root.grid_slaves(column=self.lastCol - i, row=j + self.offset):
                    e.grid_forget()

        # update last column
        self.lastCol = self.lastCol - int(timeSelection.get()[0]) * 2
        self.barCount -= 1

        # set default focus to first input of last measure
        self.root.grid_slaves(row=2 + self.offset, column=self.lastCol - int(timeSelection.get()[0]) * 2 + 1)[0].focus_set()

        # put bar label back
        labelText = "Bar " + str(self.barCount)
        self.cell = Label(self.root, width=4, text=labelText)
        self.cell.grid(row=0 + self.offset, column=self.lastCol - int(timeSelection.get()[0]), sticky=W, columnspan=int(timeSelection.get()[0]) * 2)

        # put clear button back
        self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=4 + self.offset, column=self.lastCol - 2, columnspan=2, sticky=W)

        # put components for section name input back
        self.cell = Label(self.root, width=5, text="Name:")
        self.cell.grid(row=4 + self.offset, column=self.lastCol - 6, columnspan=2, sticky=E)
        nameInput = Entry(self.root, width=6, font=('Arial',14))
        nameInput.bind("<Key>", lambda c: self.__updateName(c, self, nameInput.get()))
        nameInput.grid(row=4 + self.offset, column=self.lastCol - 4, columnspan=2, sticky=W)
        # print("measure removed")

    def editTable(self, num_cols, timeSelection):
        # delete prev rows
        for w in self.root.grid_slaves():
            w.grid_forget()
        
        self.buildTable(num_cols, timeSelection, 0, 1)

    def clearTable(self):
        count = 0
        for e in reversed(self.root.grid_slaves(row=2 + self.offset)):
            if count != 0:
                e.delete(0, END)
            count += 1

        count = 0
        for e in reversed(self.root.grid_slaves(row=3 + self.offset)):
            if count != 0:
                e.delete(0, END)
            count += 1

        # clear name input
        self.root.grid_slaves(row=4 + self.offset, column=self.lastCol-4)[0].delete(0, END)
        
        print("table cleared")

    def fillStrumPattern(self, event):
        # implementation choice: autofill entire table on selection? Or just set that selection for new bars?      
        count = 0

        for e in reversed(self.root.grid_slaves(row=3 + self.offset)):
            if count != 0:
                e.delete(0, END)
                if self.strumPattern.get() != "Custom":
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
        for e in reversed(self.root.grid_slaves(row=2 + self.offset)):
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
        duration = (60/bpm)/(numBeatsPerMeasure * 2) # calculate duration of each strum
        for e in reversed(self.root.grid_slaves(row=3 + self.offset)):
            # code for appending duration to each strum stroke:
            # if (e.get() != ""):
            #     currMeasure.append((e.get(), duration))
            # else:
            #     currMeasure.append("")

            if count != 0:
                currMeasure.append(e.get()) # delete this line if using above code
                if count == numBeatsPerMeasure * 2:
                    rightArm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        return (leftArm, rightArm)
    
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

    # update sections list
    sections.clear()
    sections.append(initSection)
    sectionsDisplay.config(state="ENABLED")
    sectionsDisplay.delete(0, END)
    sectionsDisplay.insert(END, len(sections))
    sectionsDisplay.config(state=DISABLED)

    # update measures display
    # measuresDisplay.config(state="ENABLED")
    # measuresDisplay.delete(0, END)
    # measuresDisplay.insert(END, initSection.numMeasures)
    # measuresDisplay.config(state=DISABLED)

    num_cols = int(timeSelection.get()[0]) * initSection.numMeasures * 2
    initSection.editTable(num_cols, timeSelection)
    print("table updated")

# OLD EVENT HANDLERS
# def ret_pressed(event, section):
#     add_measure(section)

# def backspace_pressed(event, section):
#     remove_measure(section)

# def add_measure_all_sections():
#     for section in sections:
#         add_measure(section)

# def remove_measure_all_sections():
#     for section in sections:
#         remove_measure(section)

def add_measure(section):
    section.numMeasures = section.numMeasures + 1
    num_cols = int(timeSelection.get()[0]) * section.numMeasures * 2

    section.addMeasure(num_cols)

    # update display
    # measuresDisplay.config(state="ENABLED")
    # measuresDisplay.delete(0, END)
    # measuresDisplay.insert(END, numMeasures.get())
    # measuresDisplay.config(state=DISABLED)

def remove_measure(section):
    if section.numMeasures > 1:
        section.numMeasures = section.numMeasures - 1

        section.removeMeasure()

        # update display
        # measuresDisplay.config(state="ENABLED")
        # measuresDisplay.delete(0, END)
        # measuresDisplay.insert(END, numMeasures.get())
        # measuresDisplay.config(state=DISABLED)

# load default table
create_table(initSection, timeSelection)

# time signature / bpm / measure dropdowns
timeMenu = OptionMenu(timeFrame, timeSelection, "4/4", *timeSigs, command=update_table)
timeLabel = Label(timeFrame, text="Time Signature: ")
timeLabel.pack(side=LEFT)
timeMenu.pack(side=LEFT)

bpmInput = Entry(timeFrame, width=2, font=('Arial',16))
bpmInput.insert(END, "60") # set default bpm
bpmLabel = Label(timeFrame, text="bpm: ")
bpmLabel.pack(side=LEFT)
bpmInput.pack(side=LEFT)

# OLD UI for Add/Remove Measures
# measuresLabel = Label(timeFrame, text="Measures: ")
# measuresDisplay = Entry(timeFrame, width=2, font=('Arial',16))

# set default numMeasures to 1 if not initialized
# if numMeasures.get() == "":
#     numMeasures.set("1")

# measuresDisplay.insert(END, initSection.numMeasures)
# measuresDisplay.config(state=DISABLED)

# removeMeasureBtn = Button(timeFrame, text="-", width=1, command=remove_measure_all_sections)
# addMeasureBtn = Button(timeFrame, text="+", width=1, command=add_measure_all_sections)

# measuresLabel.pack(side=LEFT)
# removeMeasureBtn.pack(side=LEFT)
# # measuresDisplay.pack(side=LEFT)
# addMeasureBtn.pack(side=LEFT)

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

def remove_section():
    if (len(sections) > 1):
        removedSection = sections.pop()
        for i in range(5):
            for e in removedSection.root.grid_slaves(row=removedSection.offset + 4 - i):
                e.grid_forget()

        # update display
        sectionsDisplay.config(state="ENABLED")
        sectionsDisplay.delete(0, END)
        sectionsDisplay.insert(END, len(sections))
        sectionsDisplay.config(state=DISABLED)

# buttons for adding/removing sections
sectionBtnsFrame = Frame(window)

sectionsLabel = Label(sectionBtnsFrame, text="Sections: ")
sectionsDisplay = Entry(sectionBtnsFrame, width=2, font=('Arial',16))
sectionsDisplay.insert(END, len(sections))
sectionsDisplay.config(state=DISABLED)

addSectionBtn = Button(sectionBtnsFrame, text="+", width=1, command=add_section)
removeSectionBtn = Button(sectionBtnsFrame, text="-", width=1, command=remove_section)

sectionsLabel.pack(side=LEFT)
removeSectionBtn.pack(side=LEFT)
sectionsDisplay.pack(side=LEFT)
addSectionBtn.pack(side=LEFT)
sectionBtnsFrame.pack(pady=(10,5))

def collect_chord_strum_data():
    # build section dict
    for section in sections:
        name = section.name
        data = section.buildChordStrumData(timeSelection) # in form (left_arm, right_arm) for each section
        sectionsDict[name] = data
        
    # parse song input
    input = songInput.get()
    parsed_input = input.replace(", ", ",").split(",")

    # build complete left_arm, right_arm lists
    left_arm = []
    right_arm = []
    for section in parsed_input:
        if section in sectionsDict.keys():
            left_arm += sectionsDict[section][0]
            right_arm += sectionsDict[section][1]

    # commands for getting the below values:
    # time signature -> timeSelection.get()
    # bpm -> bpmInput.get()
    # duration of each strum = (60/bpm)/(numBeatsPerMeasure * 2)

    if songTitle.get() != "":
        name = songTitle.get()
    else:
        name = "default"
    
    write_to_csv(name, input)

    print("left arm: ", left_arm)
    print("right arm: ", right_arm)
    print("input: ", input)
    tkinter.messagebox.showinfo("Alert", "Song sent to GuitarBot.")

def write_to_csv(name, input):
    # check to make sure user does not accidentally overwrite existing song
    if name != "default" and os.path.isfile('src/csv/' + name + '.csv'):
        response = tkinter.messagebox.askquestion("Warning", "A song with the same name is already saved. Would you like to overwrite the " +
                                    "contents of the existing song? (If you select no, song will be saved as a new file.)")
        if response == 'no':
            name = name + "1"

    file = open('src/csv/' + name + '.csv', 'w')
    writer = csv.writer(file)

    # csv vs txt??

    # write general song data
    writer.writerow(name)
    writer.writerow(timeSelection.get())
    writer.writerow(bpmInput.get())
    writer.writerow(input)

    # write individual section data
    for section in sections:
        writer.writerow(section.name)
        writer.writerow(section.numMeasures)
        data = section.buildChordStrumData(timeSelection)
        writer.writerow(data[0]) # write left arm data
        writer.writerow(data[1]) # write right arm data

    file.close()

def load_from_csv():
    print("load from csv")

# create inputs for song title/structure to send to bot
# song components should be comma delimited (Ex: Verse, Chorus, Bridge)
# TODO: update UI to be more like a series of dropdowns
songFrame = Frame(window)
titleFrame = Frame(songFrame)
inputFrame = Frame(songFrame)
btnFrame = Frame(window)

songTitle = Entry(titleFrame, width=12, font=('Arial',14))
titleLabel = Label(titleFrame, text="Song Title:", width=10)
titleLabel.pack(side=LEFT)
songTitle.pack(side=LEFT)

songInput = Entry(inputFrame, width=12, font=('Arial',14))
inputLabel = Label(inputFrame, text="Input (v, c,...):", width=10)
inputLabel.pack(side=LEFT)
songInput.pack(side=LEFT)

titleFrame.pack()
inputFrame.pack()
songFrame.pack(pady=(20,5))

send = Button(btnFrame, text="Send", width=4, command=collect_chord_strum_data)
load = Button(btnFrame, text="Load CSV", width=8, command=load_from_csv)
label = Label(btnFrame, text="OR")
send.pack(pady=1)
label.pack()
load.pack(pady=1)

btnFrame.pack()

window.mainloop()