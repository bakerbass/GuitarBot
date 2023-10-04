class JsonHelper:
    def collect_chord_strum_data():
        global left_arm
        global right_arm
        global mtime

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

        # commands for getting the below values:
        # time signature -> timeSelection.get()
        # bpm -> bpmInput.get()
        # duration of each strum = (60/bpm)/(numBeatsPerMeasure * 2)

        if songTitle.get() != "":
            name = songTitle.get()
        else:
            name = "default"

        write_to_json(name, input)

        # write left_arm, right_arm arrays to json file
        with open('output/output.json', 'w') as file:
            # write left_arm, right_arm to json
            file.write(json.dumps([left_arm, right_arm], indent=4))

        print("left arm: ", left_arm)
        print("right arm: ", right_arm)
        print("input: ", input)
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