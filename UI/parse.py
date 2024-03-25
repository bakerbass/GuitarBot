import pandas as pd
from chords.chord_dict import chord_dict

def get_chords_M(directory, chord_letter, chord_type):
    df_chords = pd.read_csv(directory)
    for new_x in range(334):
        if df_chords.iloc[new_x][0] == chord_letter:
            if df_chords.iloc[new_x][1] == chord_type:
                x = new_x
                break
    ftraj = False
    dtraj = []
    utraj = []
    try:
        s1 = int(df_chords.iloc[x][3])
        dtraj = [0, 6]
        utraj = [6, 0]
        ftraj = True
    except:
        s1 = -1
    try:
        s2 = int(df_chords.iloc[x][4])
        if ftraj == False:
            dtraj = [1, 6]
            utraj = [6, 1]
            ftraj = True
    except:
        s2 = -1

    try:
        s3 = int(df_chords.iloc[x][5])
        if ftraj == False:
            dtraj = [2, 6]
            utraj = [6, 2]
            ftraj = True
    except:
        s3 = -1
    try:
        s4 = int(df_chords.iloc[x][6])
        if ftraj == False:
            dtraj = [3, 6]
            utraj = [6, 3]
            ftraj = True
    except:
        s4 = -1
    try:
        s5 = int(df_chords.iloc[x][7])
        if ftraj == False:
            dtraj = [4, 6]
            utraj = [6, 4]
            ftraj = True
    except:
        s5 = -1
    try:
        s6 = int(df_chords.iloc[x][8])
        if ftraj == False:
            dtraj = [5, 6]
            utraj = [6, 5]
            ftraj = True
    except:
        s6 = -1
    fret_numbers = [s1, s2, s3, s4, s5, s6]
    fret_play = []
    if fret_numbers[0] == 0:
        fret_numbers[0] += 1
        fret_play.append(1)
    elif fret_numbers[0] == -1:
        fret_numbers[0] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[1] == 0:
        fret_numbers[1] += 1
        fret_play.append(1)
    elif fret_numbers[1] == -1:
        fret_numbers[1] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[2] == 0:
        fret_numbers[2] += 1
        fret_play.append(1)
    elif fret_numbers[2] == -1:
        fret_numbers[2] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[3] == 0:
        fret_numbers[3] += 1
        fret_play.append(1)
    elif fret_numbers[3] == -1:
        fret_numbers[3] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[4] == 0:
        fret_numbers[4] += 1
        fret_play.append(1)
    elif fret_numbers[4] == -1:
        fret_numbers[4] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[5] == 0:
        fret_numbers[5] += 1
        fret_play.append(1)
    elif fret_numbers[5] == -1:
        fret_numbers[5] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)
    print(fret_numbers, fret_play)
    print(dtraj, utraj)
    return fret_numbers, fret_play, dtraj, utraj


def parseright_M(right_arm, measure_time):
    initialStrum = "D"
    firstbfound = False
    mra = 0
    pmra = 0
    pbra = 0
    deltaT = 0
    strumOnsets = []
    time = 0
    right_information = right_arm.copy()
    # print("right arm, parseright: ",right_arm)
    for measure in right_information:
        tempM = []
        bra = 0
        for beat in measure:
            if beat == "U" or beat == "D" or beat == "":
                if not firstbfound:
                    if beat == "D":
                        strumOnsets.append([time, 'D', 'N'])
                        right_information[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here
                    if beat == "U":
                        strumOnsets.append([time, 'U', 'N'])
                        right_information[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here

                    firstbfound = True
                    initialStrum = beat
                    pmra = mra
                    pbra = bra

                    bra += 1
                    deltaT += measure_time / 8
                    time += measure_time / 8
                    checkfirst = False
                    continue
                if beat == "U":
                    strumOnsets.append([time, 'U', 'N'])
                    right_information[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                    if right_information[pmra][pbra][0] == "U":
                        right_information[pmra][pbra][1] = "C"
                    right_arm[pmra][pbra][3] = deltaT
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    deltaT = 0
                    # print(pmra, pbra)
                if beat == "D":
                    strumOnsets.append([time, 'D', 'N'])
                    right_information[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                    if right_information[pmra][pbra][0] == "D":
                        right_information[pmra][pbra][1] = "C"
                    right_information[pmra][pbra][3] = deltaT
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    deltaT = 0
            else:
                print(right_information, mra, bra)
                raise Exception("Right Arm input incorrect")
            bra += 1
            time += (measure_time / 8)
            # print(right_information, mra, bra, "loop")
            deltaT += measure_time / 8
        mra += 1
    count = 0
    for x in strumOnsets:
        try:
            if x[1] == 'D' and strumOnsets[count + 1][1] == 'D':
                x[2] = 'C'
            if x[1] == 'U' and strumOnsets[count + 1][1] == 'U':
                x[2] = 'C'
            count += 1
        except:
            break
    print("ri", right_information, initialStrum)
    return right_information, initialStrum, strumOnsets


def parseleft_M(left_arm, measure_time):
    firstc = []
    firstcfound = False
    mcount = 0
    mtimings = []
    time = 0
    for measure in left_arm:
        bcount = 0
        for chords in measure:
            if len(chords) != 0:
                type = "MAJOR"
                key = chords[1]
                if key == ' ':
                    key = 'n'
                if chords[2:3] == "M":
                    type = "MAJOR"
                if chords[2:3] == "m":
                    type = "MINOR"
                    # print("MINOR CHORD")
                if chords[2:4] == "M7":
                    type = "MAJOR7"
                    # print("MAJOR7 CHORD")
                if chords[2:4] == "M9":
                    type = "MAJOR9"
                    # print("MAJOR9 CHORD")
                if chords[2:4] == "m9":
                    type = "MINOR9"
                    # print("MINOR9 CHORD")
                if chords[2:6] == "SUS2":
                    type = "SUS2"
                    # print("SUS2 CHORD")
                if chords[2:6] == "SUS4":
                    type = "SUS4"
                    # print("SUS4 CHORD")
                if chords[2:4] == "M6":
                    type = "MAJOR6"
                    # print("MAJOR6 CHORD")
                if chords[2:3] == "5":
                    type = "FIFTH"
                    # print("FIFTH CHORD")
                if chords[2:12] == "DIMINISHED":
                    type = "DIMINISHED"
                    # print("DIMINISHED CHORD")
                if chords[2:4] == "m7":
                    type = "MINOR7"
                    # print("MINOR CHORD")
                if chords[2:4] == "m6":
                    type = "MINOR6"
                    # print("MINOR6 CHORD")
                if chords[2:10] == "HALF-DIM":
                    type = "HALF-DIM"
                    # print("HALF-DIM CHORD")
                if chords[2:10] == "DOMINANT":
                    type = "DOMINANT"
                    # print("DOMINANT CHORD")
                if chords[2:7] == "TEST0":
                    type = "TEST0"
                    print("test 0 accepted")
                if chords[2:7] == "TEST1":
                    type = "TEST1"
                if chords[2:7] == "TEST2":
                    type = "TEST2"
                if chords[2:7] == "TEST2":
                    type = "TEST2"
                if chords[2:7] == "TEST3":
                    type = "TEST3"
                if chords[2:7] == "TEST4":
                    type = "TEST4"
                if chords[2:7] == "TEST5":
                    type = "TEST5"
                if chords[2:7] == "TEST6":
                    type = "TEST6"
                if chords[2:7] == "TEST7":
                    type = "TEST7"
                frets, command, dtraj, utraj = get_chords_M("Chords - Chords.csv", chords[0] + key, type)
                left_arm[mcount][bcount] = [frets, command]
                mtimings.append(time)
                if not firstcfound:
                    firstc.append(frets)
                    firstc.append(command)
                    firstcfound = True
            time += measure_time / 4
            bcount += 1
        mcount += 1
    print("queue: ", mtimings)
    # print(left_arm)
    justchords = []
    for m in left_arm:
        for b in m:
            if b == '':
                continue
            else:
                justchords.append(b)
    print("jc", justchords)
    # return left_arm, firstc, mtimings
    return justchords, firstc, mtimings


# chords = {
#     "AM": [5, 7, 7, 6, 5, 5],
#     "AM7": [],
#     "AM9": [],
#     "Am": [5, 0, 7, 6, 5, 5],
#     "Am7": ['X', 3, 1, 3, 1, 3],
#     "Am9": ['X', 3, 0, 3, 4, 3],
#     "ADim": ['X', 3, 1, 'X', 1, 2],
#     "ADom": ['X', 0, 2, 0, 2, 0],
#     "ASus2": ['X', 0, 'X', 'X', 0, 0],
#     "ASus4": ['X', 0, 2, 2, 3, 3],
#     "Am11": [8, 6, 5, 5, 6, 6],
#     "Am7b5": ['X', 3, 1, 3, 1, 2],
#     "A5": ['X', 0, 'X', 'X', 'X', 0],
#     "A7": ['X', 0, 2, 0, 2, 0],
#     "AM6": [5, 4, 4, 'X', 5, 5],
#     "Am6": [5, 3, 2, 2, 0, 0],
#     "BM": [7, 6, 4, 4, 0, 7],
#     "BM7": [7, 9, 8, 8, 7, 7],
#     "BM9": [],
#     "Bm": [7, 9, 9, 7, 7, 7],
#     "Bm7": ['X', 2, 0, 2, 0, 2],
#     "Bm9": [],
#     "BDim": [],
#     "BDom": [7, 0, 4, 4, 4, 5],
#     "BSus2": ['X', 2, 'X', 'X', 2, 2],
#     "BSus4": [7, 7, 9, 9, 7, 7],
#     "Bm11": [],
#     "Bm7b5": ['X', 2, 0, 2, 0, 1],
#     "B5": ['X', 2, 'X', 'X', 0, 2],
#     "B7": ['X', 2, 1, 2, 0, 2],
#     "BM6": ['X', 2, 1, 1, 0, 2],
#     "Bm6": [],
#     "CM": ['X', 3, 2, 0, 1, 0],
#     "CM7": ['X', 3, 2, 4, 0, 3],
#     "CM9": ['X', 3, 0, 3, 5, 3],
#     "Cm": [8, 6, 5, 0, 8, 8],
#     "Cm7": ['X', 3, 1, 3, 1, 3],
#     "Cm9": ['X', 3, 0, 3, 4, 3],
#     "CDim": ['X', 3, 1, 'X', 1, 2],
#     "CDom": ['X', 3, 2, 3, 'X', 3],
#     "CSus2": [8, 5, 5, 0, 8, 8, ],
#     "CSus4": [8, 8, 5, 5, 6, 8],
#     "Cm11": [8, 5, 5, 8, 6, 6],
#     "Cm7b5": ['X', 3, 1, 3, 1, 2],
#     "C5": ['X', 3, 'X', 0, 1, 3],
#     "C7": [3, 2, 0, 0, 0, 0],
#     "CM6": ['X', 3, 2, 2, 1, 3],
#     "Cm6": ['X', 3, 1, 2, 3, 3],
#     "DM": ['X', 'X', 0, 2, 3, 2],
#     "DM7": ['X', 'X', 0, 2, 2, 2],
#     "DM9": ['X', 2, 1, 'X', 2, 2],
#     "Dm": ['X', 'X', 0, 2, 3, 1],
#     "Dm7": ['X', 'X', 0, 2, 1, 1],
#     "Dm9": ['X', 5, 7, 5, 6, 0],
#     "DDim": ['X', 'X', 0, 1, 3, 1],
#     "DDom": ['X', 'X', 0, 2, 1, 2],
#     "DSus2": ['X', 'X', 0, 2, 'X', 0],
#     "DSus4": ['X', 5, 5, 0, 3, 5],
#     "Dm11": [10, 0, 10, 10, 8, 0],
#     "Dm7b5": ['X', 'X', 0, 1, 1, 1],
#     "D5": ['X', 'X', 0, 2, 'X', 'X'],
#     "D7": ['X', 'X', 0, 2, 1, 2],
#     "DM6": ['X', 5, 4, 4, 3, 5],
#     "Dm6": ['X', 5, 3, 4, 5, 5],
#     "EM": [0, 2, 2, 1, 0, 0],
#     "EM7": [0, 'X', 1, 1, 0, 0],
#     "EM9": [0, 2, 2, 1, 0, 2],
#     "Em": [0, 2, 2, 0, 0, 0],
#     "Em7": [0, 2, 0, 0, 3, 0],
#     "Em9": [0, 2, 0, 0, 0, 2],
#     "EDim": [0, 7, 8, 0, 8, 0],
#     "EDom": [0, 2, 0, 1, 0, 0],
#     "ESus2": ['X', 'X', 0, 2, 'X', 0],
#     "ESus4": [0, 2, 2, 2, 0, 0],
#     "Em11": [10, 0, 10, 10, 8, 10],
#     "Em7b5": [0, 1, 0, 0, 3, 3],
#     "E5": [0, 'X', 'X', 'X', 0, 0],
#     "E7": [0, 'X', 0, 1, 0, 0],
#     "EM6": [0, 2, 2, 4, 2, 4],
#     "Em6": [0, 2, 4, 0, 2, 2],
#     "FM": [1, 3, 3, 2, 1, 1],
#     "FM7": [1, 0, 3, 2, 1, 0],
#     "FM9": [1, 0, 1, 0, 1, 3],
#     "Fm": ['X', 'X', 3, 1, 1, 4],
#     "Fm7": [1, 3, 1, 1, 4, 1],
#     "Fm9": [1, 3, 1, 1, 1, 3],
#     "FDim": ['X', 'X', 3, 4, 6, 4],
#     "FDom": [1, 3, 1, 2, 1, 1],
#     "FSus2": [1, 'X', 'X', 0, 1, 1],
#     "FSus4": [1, 1, 3, 3, 1, 1],
#     "Fm11": [],
#     "Fm7b5": [1, 2, 3, 1, 4, 1],
#     "F5": [1, 'X', 'X', 'X', 1, 1],
#     "F7": [1, 0, 'X', 'X', 1, 0],
#     "FM6": [1, 0, 0, 2, 1, 1],
#     "Fm6": [1, 3, 0, 1, 1, 3],
#     "GM": [3, 2, 0, 0, 0, 3],
#     "GM7": [3, 1, 0, 0, 0, 2],
#     "GM9": [3, 0, 0, 2, 0, 1],
#     "Gm": [3, 1, 0, 0, 3, 3],
#     "Gm7": [3, 1, 0, 0, 3, 1],
#     "Gm9": [3, 0, 0, 3, 3, 1],
#     "GDim": [3, 1, 'X', 0, 2, 3],
#     "GDom": ['X', 10, 10, 0, 8, 10, 1],
#     "GSus2": [1, 'X', 'X', 0, 1, 1],
#     "GSus4": [3, 5, 3, 0, 0, 3],
#     "Gm11": [],
#     "Gm7b5": [3, 1, 3, 3, 2, 1],
#     "G5": [],
#     "G7": [],
#     "GM6": [3, 2, 0, 0, 3, 0],
#     "Gm6": [3, 1, 0, 2, 3, 0],
#     "A#M": ['X', 1, 0, 3, 3, 1],
#     "A#M7": [6, 0, 3, 3, 3, 5],
#     "A#M9": [],
#     "A#m": ['X', 1, 3, 3, 2, 1],
#     "A#m7": [6, 8, 8, 6, 9, 9],
#     "A#m9": [],
#     "A#Dim": [6, 4, 'X', 6, 5, 0],
#     "A#Dom": [],
#     "A#Sus2": [6, 3, 3, 3, 6, 6],
#     "A#Sus4": [6, 6, 3, 3, 4, 6],
#     "A#m11": [],
#     "A#m7b5": ['X', 1, 2, 1, 2, 0],
#     "A#5": ['X', 1, 3, 3, 'X', 1],
#     "A#7": [6, 8, 6, 7, 6, 6],
#     "A#M6": ['X', 1, 0, 0, 'X', 1],
#     "A#m6": [],
#     "C#M": ['X', 4, 6, 6, 6, 4],
#     "C#M7": [9, 8, 6, 6, 6, 8],
#     "C#M9": [9, 6, 6, 8, 6, 9],
#     "C#m": ['X', 4, 6, 6, 5, 0],
#     "C#m7": ['X', 4, 2, 4, 0, 4],
#     "C#m9": [9, 6, 6, 6, 0, 0],
#     "C#Dim": ['X', 4, 2, 0, 2, 0],
#     "C#Dom": ['X', 4, 6, 4, 6, 4],
#     "C#Sus2": ['X', 4, 6, 6, 4, 4],
#     "C#Sus4": ['X', 4, 4, 'X', 2, 4],
#     "C#m11": [9, 9, 6, 8, 6, 7],
#     "C#m7b5": ['X', 4, 2, 0, 0, 0],
#     "C#5": ['X', 4, 6, 6, 'X', 2],
#     "C#7": ['X', 4, 6, 5, 6, 4],
#     "C#M6": ['X', 4, 3, 3, 2, 4],
#     "C#m6": ['X', 4, 6, 3, 4, 0],
#     "D#M": ['X', 6, 5, 0, 4, 6],
#     "D#M7": ['X', 6, 0, 0, 4, 6],
#     "D#M9": ['X', 6, 8, 0, 6, 6],
#     "D#m": ['X', 6, 4, 'X', 4, 6],
#     "D#m7": ['X', 6, 4, 6, 4, 6],
#     "D#m9": [],
#     "D#Dim": ['X', 6, 4, 'X', 4, 5],
#     "D#Dom": ['X', 6, 8, 8, 8, 9],
#     "D#Sus2": ['X', 6, 8, 8, 6, 6],
#     "D#Sus4": ['X', 6, 6, 'X', 4, 6],
#     "D#m11": [],
#     "D#m7b5": ['X', 'X', 1, 2, 2, 2],
#     "D#5": ['X', 6, 8, 8, 'X', 6],
#     "D#7": ['X', 6, 8, 7, 8, 6],
#     "D#M6": ['X', 'X', 1, 3, 1, 3],
#     "D#m6": ['X', 6, 4, 5, 6, 6],
#     "F#M": [2, 4, 4, 3, 4, 4],
#     "F#M7": [2, 4, 3, 3, 2, 2],
#     "F#M9": [2, 1, 2, 1, 2, 0],
#     "F#m": ['X', 'X', 4, 2, 2, 2],
#     "F#m7": [2, 0, 4, 2, 2, 0],
#     "F#m9": [2, 0, 2, 1, 2, 0],
#     "F#Dim": [2, 0, 'X', 2, 1, 2],
#     "F#Dom": [2, 4, 4, 3, 2, 0],
#     "F#Sus2": [2, 'X', 'X', 1, 2, 2],
#     "F#Sus4": [2, 4, 4, 4, 2, 2],
#     "F#m11": [],
#     "F#m7b5": [2, 0, 2, 2, 1, 0],
#     "F#5": [2, 4, 4, 'X', 2, 2],
#     "F#7": ['X', 'X', 4, 3, 2, 1],
#     "F#M6": ['X', 'X', 4, 6, 4, 6],
#     "F#m6": [2, 0, 1, 1, 2, 2],
#     "G#M": [4, 6, 6, 5, 4, 4],
#     "G#M7": [4, 6, 5, 5, 4, 4],
#     "G#M9": [4, 6, 4, 5, 4, 6],
#     "G#m": [4, 6, 6, 4, 4, 4],
#     "G#m7": ['X', 'X', 6, 8, 7, 7],
#     "G#m9": [4, 6, 4, 4, 4, 6],
#     "G#Dim": [4, 2, 0, 4, 0, 4],
#     "G#Dom": [4, 6, 4, 5, 4, 4],
#     "G#Sus2": [4, 6, 6, 'X', 4, 6],
#     "G#Sus4": [4, 6, 6, 6, 4, 4],
#     "G#m11": [],
#     "G#m7b5": [4, 6, 4, 4, 4, 5],
#     "G#5": [4, 6, 6, 'X', 4, 4],
#     "G#7": [4, 3, 1, 0, 4, 4],
#     "G#M6": [4, 3, 3, 1, 4, 4],
#     "G#m6": [4, 2, 3, 3, 4, 4],
#     "AbM": [4, 6, 6, 5, 4, 4],
#     "AbM7": [],
#     "AbM9": [],
#     "Abm": [4, 6, 6, 4, 4, 4],
#     "Abm7": ['X', 'X', 6, 8, 7, 7],
#     "Abm9": [4, 6, 4, 4, 0, 6],
#     "AbDim": [4, 2, 0, 4, 0, 4],
#     "AbDom": [4, 6, 4, 5, 4, 6],
#     "AbSus2": [4, 1, 1, 3, 4, 4],
#     "AbSus4": [4, 4, 6, 6, 4, 4],
#     "Abm11": [],
#     "Abm7b5": [4, 2, 0, 4, 0, 2],
#     "Ab5": [4, 6, 6, 'X', 4, 4],
#     "Ab7": [4, 6, 5, 5, 4, 4],
#     "AbM6": [4, 6, 6, 5, 6, 4],
#     "Abm6": [],
#     "BbM": ['X', 1, 0, 3, 3, 1],
#     "BbM7": [6, 0, 0, 'X', 6, 5],
#     "BbM9": [],
#     "Bbm": ['X', 1, 3, 3, 2, 1],
#     "Bbm7": ['X', 1, 3, 1, 2, 1],
#     "Bbm9": [],
#     "BbDim": [],
#     "BbDom": ['X', 1, 3, 2, 1, 1],
#     "BbSus2": ['X', 1, 3, 3, 1, 1],
#     "BbSus4": [6, 8, 8, 8, 6, 6],
#     "Bbm11": [],
#     "Bbm7b5": [6, 4, 6, 6, 5, 4],
#     "Bb5": ['X', 1, 3, 3, 'X', 1],
#     "Bb7": ['X', 1, 0, 1, 3, 1],
#     "BbM6": ['X', 1, 0, 0, 3, 2],
#     "Bbm6": [],
#     "DbM": ['X', 4, 6, 6, 6, 4],
#     "DbM7": ['X', 4, 6, 5, 6, 4],
#     "DbM9": [9, 6, 6, 8, 6, 7],
#     "Dbm": [9, 7, 'X', 9, 9, 0],
#     "Dbm7": ['X', 4, 2, 4, 0, 4],
#     "Dbm9": ['X', 4, 6, 4, 4, 0],
#     "DbDim": ['X', 4, 2, 0, 2, 0],
#     "DbDom": ['X', 4, 6, 4, 6, 6],
#     "DbSus2": [9, 6, 6, 8, 9, 9],
#     "DbSus4": ['X', 4, 4, 1, 2, 2],
#     "Dbm11": [9, 9, 6, 8, 0, 0],
#     "Dbm7b5": ['X', 4, 2, 0, 0, 3],
#     "Db5": ['X', 4, 6, 6, 'X', 4],
#     "Db7": ['X', 4, 3, 1, 0, 1],
#     "DbM6": ['X', 4, 3, 3, 2, 4],
#     "Dbm6": ['X', 4, 2, 3, 4, 4],
#     "EbM": ['X', 6, 5, 0, 4, 6],
#     "EbM7": ['X', 6, 0, 0, 4, 6],
#     "EbM9": ['X', 6, 5, 0, 6, 6],
#     "Ebm": ['X', 6, 8, 8, 7, 6],
#     "Ebm7": ['X', 6, 8, 6, 7, 6],
#     "Ebm9": [],
#     "EbDim": ['X', 'X', 1, 2, 4, 2],
#     "EbDom": ['X', 6, 5, 6, 5, 6],
#     "EbSus2": ['X', 6, 8, 8, 6, 6],
#     "EbSus4": ['X', 6, 6, 'X', 4, 6],
#     "Ebm11": [],
#     "Ebm7b5": ['X', 6, 4, 6, 4, 5],
#     "Eb5": ['X', 6, 8, 8, 'X', 6],
#     "Eb7": ['X', 6, 8, 6, 8, 6],
#     "EbM6": ['X', 6, 5, 5, 4, 6],
#     "Ebm6": ['X', 6, 4, 5, 6, 6],
# }
