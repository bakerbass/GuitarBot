from GuitarBotUDP import GuitarBotUDP
import csv
import pandas as pd


#fret number is the fret number of the string
#fret command is whether or not its press
# 1: open string (will not move fret)
# 2: press - move to the commanded fret and press

def getChordArray(df, root, chordType):
    array = df[(df['LETTER'] == root) & (df['TYPE'] == chordType)].values[0][3:9]
    fretnum = []
    fretplay = []
    for i in array:
        if i == 0:
            fretplay.append(1)
            fretnum.append(5)
        else:
            fretplay.append(2)
            fretnum.append(int(i))
    return fretnum, fretplay

if __name__ == '__main__':
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 2
    ROBOT = "GuitarBot"
    PORT = 5004
    i = -1

    fname = 'all_chords_sixstrings.csv'
    # while True:
    root = input('chord')
    chordType = 'Minor984'
    # df = pd.read_csv(fname)
    # fretnum, fretplay = getChordArray(df, root, chordType)
    fretnum = [1, 2, 3, 4, 5, 6]
    fretplay = [2, 2, 2, 2, 2, 2]
    #fretnum = [2, 2, 2, 2, 1, 2]
    #fretplay = [1, 1, 2, 2, 2, 1]
    # guitarbot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)