NUM_FRETS = 10
E_MNN = 40
A_MNN = 45
D_MNN = 50
G_MNN = 55
B_MNN = 59
e_MNN = 64
chord_message = [["On", 0]]
# pluck_message = [[note (midi value), duration, speed, slide_toggle, timestamp]]
def traverse_string(string, interval=1.0, duration=0.6, speed=0, slide_toggle=0):
    start_time = 1
    if string == 'E':
        start_MNN = E_MNN
    elif string == 'D':
        start_MNN = D_MNN
    elif string == 'B':
        start_MNN = B_MNN
    else:
        raise ValueError("Unsupported string. Use 'E', 'D', or 'B'")
    pluck_message = []

    for i in range(0, NUM_FRETS):
        pluck_message.append([start_MNN + i, duration, speed, slide_toggle, start_time+interval*i])
    
    return pluck_message