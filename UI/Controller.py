from Model import Model
from View import View, ChordNotationsPopup, HelpPopup
from vis_entities.DraggableSectionLabel import DraggableSectionLabel
from copy import copy, deepcopy

class Controller:
    def __init__(self, view: View, model: Model):
        self.view = view
        self.model = model

        self.song_controls_frame = view.song_controls_frame
        self.song_frame = view.song_frame
        self.song_builder_frame = view.song_builder_frame
        self.new_section_btn = view.new_section_btn

        self._create_event_bindings()

        # manually add the first section to the UI
        self._add_section()

    def start(self):
        self.view.start_mainloop()        

    #region EventBindings
    def _create_event_bindings(self):
        # Song title entry
        self.song_controls_frame.song_title.trace_add(('write'), self._update_song_title_handler)

        # BPM spinbox
        self.song_controls_frame.bpm_spinbox.bind('<KeyRelease>', lambda e: self._update_bpm_handler(e, 'KeyRelease'))
        self.song_controls_frame.bpm_spinbox.bind('<<Increment>>', lambda e: self._update_bpm_handler(e, 'Increment'))
        self.song_controls_frame.bpm_spinbox.bind('<<Decrement>>', lambda e: self._update_bpm_handler(e, 'Decrement'))

        # Time signature options
        self.song_controls_frame.time_signature.trace_add('write', self._update_time_sig_handler)

        # Chord mode options
        self.song_controls_frame.chord_mode.trace_add('write', self._update_chord_mode_handler)

        # Chord notations btn
        self.song_controls_frame.chord_notation_btn.config(command=self._show_chord_notations_popup)

        # Save btn
        self.song_controls_frame.save_btn.config(command=self._save_song_handler)

        # Load btn
        self.song_controls_frame.load_btn.config(command=self._load_song_handler)

        # Send btn
        self.song_controls_frame.send_btn.config(command=self._send_song_handler)

        # Help icon
        self.song_controls_frame.help_btn.configure(command=lambda: self._show_help_popup()) # use configure for CTk btn

        # New section btn
        self.new_section_btn.configure(command=self._new_section_handler) # use configure for CTk btn
        
    def _create_section_event_bindings(self, section):
        section_frame, labels_frame = section

        # Trash, eraser button icons
        labels_frame.eraser_btn.configure(command=lambda: self._clear_section_handler(section_frame, labels_frame)) # use configure for CTk btn
        labels_frame.trash_btn.configure(command=lambda: self._remove_section_handler(section_frame.id)) # use configure for CTk btn

        # Strum options dropdown
        labels_frame.strum_pattern.trace_add(('write'), lambda e1, e2, e3: self._update_section_strum_pattern_handler(e1, e2, e3, section_frame, labels_frame))

        # Eraser (clear measure) icons
        for tuple in section_frame.eraser_btns:
            btn, measure_num = tuple
            # TODO: measure_num is only passing the last measure num. copy, deepcopy didn't fix it
            btn.configure(command=lambda: self._clear_measure_handler(section_frame, measure_num)) # use configure for CTk btn

        # Trash (remove measure) icons
        for tuple in section_frame.trash_btns:
            btn, measure_num = tuple
            btn.configure(command=lambda: self._remove_measure_handler(section_frame, measure_num)) # use configure for CTk btn

    #endregion EventBindings
        
    #region EventHandlers
    
    #region SongControls
    def _update_song_title_handler(self, event, *args):
        self.model.song_title = self.song_controls_frame.song_title.get()

    def _update_bpm_handler(self, event, type):
        # This event handler will run before increment/decrement buttons update the actual Entry, so we need to manually increment/decrement to account for that
        if type == 'Increment':
            self.model.bpm = int(self.song_controls_frame.bpm_spinbox.get()) + 1
        elif type == 'Decrement':
            self.model.bpm = int(self.song_controls_frame.bpm_spinbox.get()) - 1
        elif type == 'KeyRelease':
            self.model.bpm = int(self.song_controls_frame.bpm_spinbox.get())

    def _update_time_sig_handler(self, event, *args):
        time_sig = self.song_controls_frame.time_signature.get()

        # update model
        self.model.time_signature = time_sig

        # reset view w/ updated time signature
        for section in self.song_frame.sections:
            section_frame, section_label = section
            section_frame.rebuild_table(time_sig)

    def _update_chord_mode_handler(self, event, *args):
        self.model.chord_mode = self.song_controls_frame.chord_mode.get()

    def _show_chord_notations_popup(self):
        popup = ChordNotationsPopup(self.view)

        # when "Close" button is clicked, popup will be destroyed
        popup.close_btn.config(command=popup.destroy)

    def _show_help_popup(self):
        popup = HelpPopup(self.view)

        # when "Close" button is clicked, popup will be destroyed
        popup.close_btn.config(command=popup.destroy)

    # Save btn
    def _save_song_handler(self):
        self._update_model_sections()

    # Load btn
    def _load_song_handler(self):
        self._update_model_sections()

    # Send btn
    def _send_song_handler(self):
        self._update_model_sections()
        section_ids = []

        # loop through song builder and keep track of section order
        for section in DraggableSectionLabel.existing_draggables_list:
            section_ids.append(section.section_id)

        #print(section_ids)

        # send ordered section ids to model
        self.model.send_arm_lists(section_ids)

    #endregion SongControls

    #region Sections
        
    def _update_section_strum_pattern_handler(self, e1, e2, e3, section_frame, labels_frame):
        # NOTE e1, e2, e3 are dummy parameters but needed to prevent erroring
        strum_pattern = labels_frame.strum_pattern.get()
        section_frame.fill_strum_pattern(strum_pattern)
        self._update_model_sections()
        
    def _clear_section_handler(self, section_frame, labels_frame):
        # clear section data in View
        section_frame.clear_table()
        labels_frame.clear() # this will set strum options dropdown back to default value
        
        # get updated section data from View
        left_arm, right_arm = section_frame.build_arm_lists()

        # update section data in model
        self.model.update_section_data(section_frame.id, left_arm, right_arm)

    def _clear_measure_handler(self, section_frame, measure_num):
        # clear section data in View
        section_frame.clear_measure(measure_num)
        
        # get updated section data from View
        left_arm, right_arm = section_frame.build_arm_lists()

        # update section data in model
        self.model.update_section_data(section_frame.id, left_arm, right_arm)
        print(self.model.sections[section_frame.id].left_arm, self.model.sections[section_frame.id].right_arm)

    def _remove_section_handler(self, id):
        # remove section from View
        self.song_frame.remove_section(id)
        self.song_builder_frame.remove_section_button_and_draggables(id)

        # update Model accordingly
        self.model.remove_section(id)

    def _remove_measure_handler(self, section_frame, measure_num):
        print(f'Remove measure handler, {measure_num} from section {section_frame.id}')
        # remove measure from View
        section_frame.remove_measure(measure_num)

        # get updated section data from View
        left_arm, right_arm = section_frame.build_arm_lists()

        # update section data in model
        self.model.update_section_data(section_frame.id, left_arm, right_arm)
        print(self.model.sections[section_frame.id].left_arm, self.model.sections[section_frame.id].right_arm)

    # New section btn
    def _new_section_handler(self):
        self._add_section()

    #endregion Sections
        
    #endregion EventHandlers
    
    #region Helpers
        
    # Helper method for saving, loading, sending
    # Saves all the current section data in the View to the Model
    def _update_model_sections(self):
        # iterate over each section
        for section_tuple in self.view.song_frame.sections:
            section_frame, labels_frame = section_tuple

            # get section data from View
            id = section_frame.id
            name = labels_frame.name.get()
            left_arm, right_arm = section_frame.build_arm_lists()

            # update section data in model
            self.model.update_section_data(id, left_arm, right_arm, name)

    # Helper method to add a new section to the View and Model accordingly
    def _add_section(self):
        # manually add new section to the UI
        section = self.view.song_frame.add_section()
        section_frame, labels_frame = section
        id, name = section_frame.id, labels_frame.name

        # add section button to song builder buttons list (this will also automatically drop the very first section onto the song)
        self.song_builder_frame.add_section_button(id, name)

        # now update the model accordingly
        self.model.add_section(id, name)

        # add event bindings for new section
        self._create_section_event_bindings(section)


    #endregion Helpers