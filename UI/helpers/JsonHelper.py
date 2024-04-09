import json
import os.path
import tkinter.messagebox
from tkinter.filedialog import askopenfilename

class JsonHelper:
    @staticmethod
    def write_song_to_json(name, input):
        # check to make sure that user does not accidentally overwrite existing song
        if name != "default" and os.path.isfile('./songs/' + name + '.json'):
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

        with open('./UI/songs/' + name + '.json', 'w') as file:
            # write data to json
            file.write(json.dumps(json_data, indent=4))

    @staticmethod
    def load_song_from_json():
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