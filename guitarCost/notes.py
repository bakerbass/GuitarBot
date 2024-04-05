def notePossibilities(desired_note):
    if desired_note == "E":
        return [0, -1, -1, -1, -1, -1]
    elif desired_note == "F":
        return [1, -1, -1, -1, -1, -1]
    elif desired_note == "Gb":
        return [2, -1, -1, -1, -1, -1]
    elif desired_note == "G":
        return [3, -1, -1, -1, -1, -1]
    elif desired_note == "Ab":
        return [4, -1, -1, -1, -1, -1]
    elif desired_note == "A":
        return [5, 0, -1, -1, -1, -1]
    elif desired_note == "Bb":
        return [6, 1, -1, -1, -1, -1]
    elif desired_note == "B":
        return [7, 2, -1, -1, -1, -1]
    elif desired_note == "C":
        return [8, 3, -1, -1, -1, -1]
    elif desired_note == "Db":
        return [9, 4, -1, -1, -1, -1]
    elif desired_note == "D":
        return [10, 5, 0, -1, -1, -1]
    elif desired_note == "Eb":
        return [-1, 6, 1, -1, -1, -1]
    elif desired_note == "E2":
        return [-1, 7, 2, -1, -1, -1]
    elif desired_note == "F2":
        return [-1, 8, 3, -1, -1, -1]
    elif desired_note == "Gb2":
        return [-1, 9, 4, -1, -1, -1]
    elif desired_note == "G2":
        return [-1, 10, 5, 0, -1, -1]
    elif desired_note == "Ab2":
        return [-1, -1, 6, 1, -1, -1]
    elif desired_note == "A2":
        return [-1, -1, 7, 2, -1, -1]
    elif desired_note == "Bb2":
        return [-1, -1, 8, 3, -1, -1]
    elif desired_note == "B2":
        return [-1, -1, 9, 4, 0, -1]
    elif desired_note == "C2":
        return [-1, -1, 10, 5, 1, -1]
    elif desired_note == "Db2":
        return [-1, -1, -1, 6, 2, -1]
    elif desired_note == "D2":
        return [-1, -1, -1, 7, 3, -1]
    elif desired_note == "Eb2":
        return [-1, -1, -1, 8, 4, -1]
    elif desired_note == "E3":
        return [-1, -1, -1, 9, 5, 0]
    elif desired_note == "F3":
        return [-1, -1, -1, 10, 6, 1]
    elif desired_note == "Gb3":
        return [-1, -1, -1, -1, 7, 2]
    elif desired_note == "G3":
        return [-1, -1, -1, -1, 8, 3]
    elif desired_note == "Ab3":
        return [-1, -1, -1, -1, 9, 4]
    elif desired_note == "A3":
        return [-1, -1, -1, -1, 10, 5]
    elif desired_note == "Bb3":
        return [-1, -1, -1, -1, -1, 6]
    elif desired_note == "B3":
        return [-1, -1, -1, -1, -1, 7]
    elif desired_note == "C3":
        return [-1, -1, -1, -1, -1, 8]
    elif desired_note == "Db3":
        return [-1, -1, -1, -1, -1, 9]
    elif desired_note == "D3":
        return [-1, -1, -1, -1, -1, 10]
    else:
        return [-1, -1, -1, -1, -1, -1]
