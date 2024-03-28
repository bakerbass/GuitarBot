from Model import Model
from View import View, ChordNotationsPopup

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

        # New section btn
        self.new_section_btn.configure(command=self._new_section_handler) # use configure for CTk btn
        
    def _create_section_event_bindings(self):
        # Clear, delete icon event handlers for each section
        for section in self.song_frame.sections:
            section_frame, labels_frame = section

            labels_frame.eraser_btn.configure(command=lambda: self._clear_section_handler(section_frame, labels_frame)) # use configure for CTk btn
            labels_frame.trash_btn.configure(command=lambda: self._remove_section_handler(section_frame, labels_frame)) # use configure for CTk btn

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
        self.model.time_signature = self.song_controls_frame.time_signature.get()

    def _update_chord_mode_handler(self, event, *args):
        self.model.chord_mode = self.song_controls_frame.chord_mode.get()

    def _show_chord_notations_popup(self):
        popup = ChordNotationsPopup(self.view)

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
        #TODO: uncomment once UI is fully functional
        #self._update_model_sections()
        self.model.send_arm_lists()

    #endregion SongControls

    #region Sections
        
    def _clear_section_handler(self, section_frame, labels_frame):
        # clear section data in View
        section_frame.clear()
        labels_frame.clear() # this will set strum options dropdown back to default value
        
        # update Model accordingly
        self.model.clear_section_data(section_frame.id)

    # TODO
    def _remove_section_handler(self, section_frame, labels_frame):
        print('remove icon pressed')
        # remove section from View
        #TODO implement this

        # uncomment below code once implemented
        # # update Model accordingly
        # self.model.remove_section(section_frame.id)
        # print(self.model.sections)

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
            self.model.update_section_data(id, name, left_arm, right_arm)

    # Helper method to add a new section to the View and Model accordingly
    def _add_section(self):
        # manually add new section to the UI
        section_frame, labels_frame = self.view.song_frame.add_section()
        id, name = section_frame.id, labels_frame.name

        self.song_builder_frame.add_section_button(id, name)

        # now update the model accordingly
        self.model.add_section(id, name)

        # add event bindings for new section
        self._create_section_event_bindings()


    #endregion Helpers