import numpy as np
import time
import matplotlib.pyplot as plt
from typing import NamedTuple
import threading
import logging
from queue import Queue
from GuitarBotUDP import GuitarBotUDP
from xarm.wrapper import XArmAPI
from pymidi import server
# import GBotData as gbd
from rtpmidi import RtpMidi
import pretty_midi
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# global constant
UDP_IP = "192.168.1.50"
XARM_IP = '192.168.1.215'
UDP_PORT = 1001
pre_count = 5
OFFSET = 17.5
STRUM_PT = [367.7, 357.7, 347.7, 337.7, 327.7, 317.7, 307.7]
PICK_PT = [371.6 - OFFSET, 365 - OFFSET, 351.4 - OFFSET, 340.8 - OFFSET, 331.3 - OFFSET, 321.4 - OFFSET]
INIT_POSE = [684.3, 246.8, PICK_PT[3], -90, 0, 0]
SYNC_RATE = 250
move_time = 0.1
ipickeracc = 200
ipickvel = 100
pgain = 15000


left_queue = Queue()
pick_queue = Queue()
robot_queue = Queue()
# left hand cmd trigger in sec
# pick_timing = np.array(
#     [5., 5.375, 5.810, 6., 6.185, 6.435, 6.875, 7.310, 7.75, 7.935, 8.125, 8.310,
#      8.75, 9.060, 9.435, 9.810]) * 1000
pick_timing = np.array(
    [5., 5.375, 5.810, 6.05, 6.44, 6.875, 7.310+0.05, 7.75, 7.93, 8.31,
     8.75, 9.060+0.15, 9.810]) * 1000 - 50
for i in range(len(pick_timing)):
    pick_timing[i] = int(pick_timing[i]/10)*10
# right hand pick cmd trigger in sec

#left_hand_timing = np.array([5.9, 6.095, 6.875, 7.85, 8.03, 9.22, 9.62]) * 1000
left_hand_timing = np.array([6.05-0.05, 6.26-0.14, 6.44, 7.75-0.05, 7.93-0.05, 8.12-0.14, 8.31, 9.06-0.05, 9.44-0.2, 9.81- 0.05]) * 1000
for i in range(len(left_hand_timing)):
    left_hand_timing[i] = int(left_hand_timing[i]/10)*10
# right hand pick cmd trigger in sec
# song length in sec
song_length = 15
robot_timing = 5000


def midi_info(file):
    pm = pretty_midi.PrettyMIDI(file)

    onsets = pm.get_onsets()
    onsets = onsets - onsets[0] + pre_count
    notes_duration = np.diff(onsets)
    notes_value = []
    notes_vel = []
    # notes_duration = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes_value = np.append(notes_value, note.pitch)
            notes_vel = np.append(notes_vel, note.velocity)
            # notes_duration = np.append(notes_duration, note.end - note.start)
    onsets = np.round(onsets, 2)
    return onsets, notes_duration, notes_vel


onsets, notes_duration, notes_vel = midi_info('IH230midi.MID')
print(onsets, notes_duration, notes_vel)


class GuitarRobotController():
    def __init__(self):
        # self.cobot_controller = CobotController(250, INIT_POSE)
        self.xarm = XArmAPI(XARM_IP)
        self.guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
        self.left_thread = threading.Thread(target=self.lefthand_move)
        self.right_thread = threading.Thread(target=self.robot_move)
        self.pick_thread = threading.Thread(target=self.pick_move)

    def robot_init(self):

        self.xarm.set_simulation_robot(on_off=False)
        self.xarm.motion_enable(enable=True)
        self.xarm.clean_warn()
        self.xarm.set_mode(0)
        self.xarm.set_state(0)
        self.xarm.set_position(*INIT_POSE, wait=True)

    def xarm_start(self):
        self.xarm.set_mode(1)
        self.xarm.set_state(0)

    def thread_start(self):
        self.left_thread.start()
        self.right_thread.start()
        self.pick_thread.start()

    def thread_end(self):
        self.left_thread.join()
        self.right_thread.join()
        self.pick_thread.join()

    def _fifth_poly(self, q_i, q_f, time):
        # for picking, try 100 or 150 ms
        traj_t = np.linspace(0, time, int(time * SYNC_RATE))
        dq_i = 0
        dq_f = 0
        ddq_i = 0
        ddq_f = 0
        a0 = q_i
        a1 = dq_i
        a2 = 0.5 * ddq_i
        a3 = 1 / (2 * time ** 3) * (20 * (q_f - q_i) - (8 * dq_f + 12 * dq_i) * time - (3 * ddq_f - ddq_i) * time ** 2)
        a4 = 1 / (2 * time ** 4) * (
                30 * (q_i - q_f) + (14 * dq_f + 16 * dq_i) * time + (3 * ddq_f - 2 * ddq_i) * time ** 2)
        a5 = 1 / (2 * time ** 5) * (12 * (q_f - q_i) - (6 * dq_f + 6 * dq_i) * time - (ddq_f - ddq_i) * time ** 2)
        traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
        return traj_pos

    def get_traj(self, note_i, note_f, move_time):
        pos_z = self._fifth_poly(note_i, note_f, move_time)

        pos_y = np.ones(len(pos_z)) * INIT_POSE[1]
        return pos_y, pos_z

    def lefthand_move(self):
        # First Measure
        # Init
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 1, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])

        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 4, 3, 1, 3, 3], ifretnumber=[3, 2, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 2, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 0, 3, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 4, 3, 1, 3, 3], ifretnumber=[3, 2, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 2, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 0, 3, 1, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[5, 3, 3, 1, 3, 3], ifretnumber=[5, 2, 2, 0, 1, 1])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[1, 3, 3, 1, 3, 3], ifretnumber=[5, 2, 2, 0, 1, 1])
        # # STARTS ON FIRST MEASURE, NOTE 5
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 2, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 2, 3, 3], ifretnumber=[3, 2, 2, 0, 1, 1])
        #
        # # Second Measure
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 3, 3, 3], ifretnumber=[3, 0, 2, 0, 1, 1])
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 3, 3, 3], ifretnumber=[3, 1, 2, 0, 1, 1])
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 3, 3, 3, 3], ifretnumber=[3, 2, 2, 0, 1, 1])
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[2, 3, 3, 3, 3, 3], ifretnumber=[5, 0, 2, 0, 1, 1])
        #
        # # Third Measure
        # left_queue.get()
        # self.guitarbot_udp.send_msg_left(iplaycommand=[2, 3, 3, 3, 3, 3], ifretnumber=[0, 0, 2, 0, 1, 1])
        # # Ends after first note

        return 0

    def pick_move(self):
        # First Measure
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 9 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)


    def traj_generation(self):
        posZ = []
        posY = []
        # Starts on Fifth Note of Measure One



        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .375)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[1], move_time-0.02)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .337+0.02)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .188)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .188)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[2], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], .337)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        # Second Measure

        pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .337)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .438)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[1], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .088)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .187)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[1], .187)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[1], PICK_PT[2], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], .338)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .212)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[0], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        pos_y, pos_z = self.get_traj(PICK_PT[0], PICK_PT[0], .276)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        pos_y, pos_z = self.get_traj(PICK_PT[0], PICK_PT[0], move_time)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)
        # Third Measure, Ends on Note One
        pos_y, pos_z = self.get_traj(PICK_PT[0], PICK_PT[0], .274)
        posZ = np.append(posZ, pos_z)
        posY = np.append(posY, pos_y)

        # print(posZ, posY)
        # fig = plt.figure()
        # plt.plot(posZ)
        # plt.show()
        return posY, posZ

    def robot_move(self):
        posY, posZ = self.traj_generation()
        robot_queue.get()
        for i in range(len(posZ)):
            start = time.time()
            new_pose = [INIT_POSE[0], INIT_POSE[1], posZ[i], INIT_POSE[3], INIT_POSE[4], INIT_POSE[5]]
            self.xarm.set_servo_cartesian(new_pose)
            time.sleep(0.004 - (time.time() - start))

def main():

    grc = GuitarRobotController()
    #grc.traj_generation()
    grc.robot_init()
    time.sleep(1)
    grc.xarm_start()
    time.sleep(1)
    grc.thread_start()


    t_init = time.time()
    endOfSong = t_init + song_length
    # print(endOfSong)
    # print(t_init)
    Pi = 0
    Li = 0
    Ri = 0
    time_stamp = 0
    logging.info("start")
    logging.info(left_hand_timing)
    while time_stamp < song_length * 1000:
        t_i = time.time()
        if time_stamp == left_hand_timing[Li]:
            print("left hand triggered")
            print(time_stamp)
            left_queue.put(Li)
            Li += 1
            Li = Li % len(left_hand_timing)
        if time_stamp == pick_timing[Pi]:
            pick_queue.put(Pi)
            print("Right hand triggered")
            Pi += 1
            Pi = Pi % len(pick_timing)
        if time_stamp == robot_timing:
            robot_queue.put(1)

        time_stamp += 5
        #logging.info(time_stamp)
        time.sleep(0.005 - (time.time() - t_i))

        #print(time_stamp)
    logging.info("end")
    grc.thread_end()
if __name__ == '__main__':
    main()
