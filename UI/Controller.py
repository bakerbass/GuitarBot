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

    def _create_event_bindings(self):
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

    def start(self):
        self.view.start_mainloop()

    # Event handlers below

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