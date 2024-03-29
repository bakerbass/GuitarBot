import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from constants.strum_patterns import *
from constants.time_signatures import *
from PIL import Image

class SectionFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, id, width, height, time_signature):
        super().__init__(master=master, width=width, height=height, orientation='horizontal')
        self.id = id

        self.width = width
        self.height = height

        self.time_signature = time_signature
        self.last_col = -1
        self.num_measures = 0
        self.curr_measure = 0
        self.beats_per_measure = int(time_signature[0])
        self.subdiv_per_measure = self.beats_per_measure * 2
        self.beat_labels = beat_labels[time_signature]
        
        self.plus_btns = []
        self.trash_btns = []
        self.eraser_btns = []

        self.chords_tab_order = []
        self.strums_tab_order = []

        # create intial measure
        self.add_measure() # start each section with an initial measure
        # self.add_measure()
        # self.add_measure()
        # self.add_measure()

    def _reset_instance_variables(self, time_signature):
        self.time_signature = time_signature
        self.last_col = -1
        self.num_measures = 0
        self.curr_measure = 0
        self.beats_per_measure = int(time_signature[0])
        self.subdiv_per_measure = self.beats_per_measure * 2
        self.beat_labels = beat_labels[time_signature]
        
        self.plus_btns = []
        self.trash_btns = []
        self.eraser_btns = []

        self.chords_tab_order = []
        self.strums_tab_order = []

    def build_measure(self, start_col):
        # get underlying frame's background color
        frame_bg = self.master.cget('bg')

        # build chords/strum inputs
        for row in range(0, 4):
            col = start_col

            while col < self.subdiv_per_measure * self.num_measures:
                if row == 0 and self.curr_measure <= self.num_measures:
                    # BAR LABELS
                    #print(self.curr_measure)
                    self.cell = tk.Label(self, width=4, text="Bar " + str(self.curr_measure), bg=frame_bg, justify="center")
                    self.cell.grid(row=row, column=col + self.beats_per_measure - 2, sticky='e',
                                    columnspan=2)
                    
                    img = Image.open('UI/icons/trash-16px.png')
                    self.trash_icon = ctk.CTkImage(img, size=(16, 16)) # this must be an instance variable so python doesn't garbage collect it
                    self.trash_btn = ctk.CTkButton(self, image=self.trash_icon, width=0, border_width=0, border_spacing=0, text='', fg_color='transparent')
                    self.trash_btn.grid(row=row, column=col + self.beats_per_measure, sticky='w')
                    self.trash_btns.append(self.trash_btn)

                    img = Image.open('UI/icons/eraser-16px.png')
                    self.eraser_icon = ctk.CTkImage(img, size=(16, 16)) # this must be an instance variable so python doesn't garbage collect it
                    self.eraser_btn = ctk.CTkButton(self, image=self.eraser_icon, width=0, border_width=0, border_spacing=0, text='', fg_color='transparent')
                    self.eraser_btn.grid(row=row, column=col + self.beats_per_measure + 1, sticky='w')
                    self.eraser_btns.append(self.eraser_btn)
                    
                    col += self.subdiv_per_measure
                    continue
                elif row == 1:
                    # BEAT LABELS
                    # if col != 0 and col % (self.subdiv_per_measure + 1) == 0:
                    #     continue

                    self.cell = ttk.Entry(self, width=2, font=('Arial', 16, 'bold'))

                    #check if this is the last beat of the measure
                    # if col != 0 and (col % self.subdiv_per_measure) == 0:
                    #     # add a space afterwards
                    #     self.cell.grid(row=row, column=col, padx=(0, 30))
                    # else:
                    self.cell.grid(row=row, column=col)

                    self.cell.insert(tk.END,
                                        self.beat_labels[col % (self.subdiv_per_measure)])
                    
                    # disable entry
                    self.cell.config(state=tk.DISABLED)
                elif row == 2:
                    # CHORD INPUTS
                    self.cell = ttk.Entry(self, width=6, font=('Arial', 16))

                    # TODO: add these to controller
                    # # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    # self.cell.bind("<Shift-BackSpace>", self._backspacePressed)

                    # # add <Return> event handler to every input box (adds new measure if pressed)
                    # self.cell.bind("<Return>", self._return_pressed)

                    self.cell.grid(row=row, column=col, sticky='w', columnspan=2)
                    self.chords_tab_order.append(self.cell)

                    self.cell.insert(tk.END, "")
                    col += 1
                elif row == 3:
                    # STRUM INPUTS
                    self.cell = ttk.Entry(self, width=2, font=('Arial', 16))

                    # TODO add these to controller
                    # # add <Shift-BackSpace> event handler to every input box (deletes current measure if pressed)
                    # self.cell.bind("<Shift-BackSpace>", self.__backspacePressed)

                    # # add <Return> event handler to every input box (adds new measure if pressed)
                    # self.cell.bind("<Return>", self._return_pressed)

                    # check if this is the last beat of the measure
                    # if col != 0 and col % (self.subdiv_per_measure) == 0:
                    #     # add a space afterwards
                    #     self.cell.grid(row=row, column=col, padx=(0, 30))
                    # else:
                    self.cell.grid(row=row, column=col)

                    self.cell.insert(tk.END, "")

                    self.strums_tab_order.append(self.cell)
                col += 1

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=start_col)[0].focus_set()

        # TODO plus sign icon between measures
        # add plus sign icon
        print(col)
        img = Image.open('UI/icons/plus-sign-24px.png')
        self.plus_icon = ctk.CTkImage(img, size=(24, 24)) # this must be an instance variable so python doesn't garbage collect it
        self.plus_btn = ctk.CTkButton(self, image=self.plus_icon, width=0, border_width=0, border_spacing=0, text='', fg_color='transparent')
        self.plus_btn.grid(row=2, column=col, sticky='w', columnspan=1)

        # update last_column
        self.last_col = self.subdiv_per_measure * self.num_measures + 1 # add 1 to account for plus sign icon

        # set tabbing order
        self._set_tab_order()

    #TODO
    def clear_measure(self, start_col):
        pass

    #TODO
    def remove_measure(self, start_col):
        pass

    def _set_tab_order(self):
        # NOTE: if user presses tab on last chord input in a section, focus will go to the first strum input on the next row
        
        # iterate through the "Chords" row, set tabbing order from left -> right
        for cell in self.chords_tab_order:
            cell.lift()

        # iterate through the "Strums" row, set tabbing order from left -> right
        for cell in self.strums_tab_order:
            cell.lift()

    # event handler for add measure (Enter)
    def _return_pressed(self, event):
        self.add_measure(self)

    def add_measure(self):
        self.num_measures += 1
        self.curr_measure += 1

        self.build_measure(self.last_col + 1)

        # if self.num_measures == 1:
        #     self.last_col += 1
        # print("measure added")

    # event handler for remove measure (Shift+BackSpace)
    def _backspace_pressed(self, event):
        self.remove_measure(self)

    def remove_measure(self):
        # minimum of 1 measure per section
        if self.num_measures > 1:
            self.num_measures = self.num_measures - 1

        # delete all components in last measure
        for i in range(self.subdiv_per_measure):
            for j in range(5):
                for e in self.grid_slaves(column=self.last_col - i, row=j):
                    e.grid_forget()

                    # remove deleted cells from tab orders
                    if j == 2:
                        self.chords_tab_order.pop()
                    if j == 3:
                        self.strums_tab_order.pop()

                    self._set_tab_order()

        # update last column
        self.last_col = self.last_col - self.subdiv_per_measure

        # set default focus to first input of last measure
        self.grid_slaves(row=2, column=self.last_col - self.subdiv_per_measure + 1)[
            0].focus_set()

        # put bar labels back
        self.cell = tk.Label(self, width=4, text="Bar " + str(self.num_measures))
        self.cell.grid(row=0, column=self.last_col - self.beats_per_measure, sticky='w',
                        columnspan=self.subdiv_per_measure)

        # print("measure removed")

    # called when time signature changes
    def rebuild_table(self, time_signature):
        # delete prev rows
        for w in self.grid_slaves():
            w.grid_forget()

        self._reset_instance_variables(time_signature)
        self.add_measure()
        self.add_measure()
        self.add_measure()
        self.add_measure()

    def clear_table(self):
        for e in reversed(self.grid_slaves(row=2)):
            e.delete(0, tk.END)

        for e in reversed(self.grid_slaves(row=3)):
            e.delete(0, tk.END)

        # print("table cleared")
            
    def fill_strum_pattern(self, strum_pattern):
        # print(strum_pattern)
        # print(strum_patterns.get(strum_pattern))
        count = 0
        for e in reversed(self.grid_slaves(row=3)):
            e.delete(0, tk.END)

            if strum_pattern != "Custom":
                length = len(strum_patterns.get(strum_pattern))
                e.insert(tk.END, strum_patterns.get(strum_pattern)[count % length])

            count += 1

    def build_arm_lists(self):
        left_arm = []
        right_arm = []

        # generate left arm data
        curr_measure = []
        count = 0
        for e in reversed(self.grid_slaves(row=2)):
            # print("count: ", count)
            # print("value: ", e.get())
            # print("numbeats: ", numBeatsPerMeasure)

            curr_measure.append(e.get())
            if count == self.beats_per_measure:
                left_arm.append(curr_measure)
                curr_measure = []
                count = 1
                continue
            count += 1

        # generate right arm data
        curr_measure = []
        count = 0
        for e in reversed(self.grid_slaves(row=3)):
            curr_measure.append(e.get())
            if count == self.beats_per_measure * 2:
                right_arm.append(curr_measure)
                curr_measure = []
                count = 1
                continue
            count += 1

        return (left_arm, right_arm)

    def insert_chord_strum_data(self, left_arm, right_arm):
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
