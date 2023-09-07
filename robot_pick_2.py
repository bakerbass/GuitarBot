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
INIT_POSE = [684.3, 246.8, PICK_PT[5], -90, 0, 0]
SYNC_RATE = 250
move_time = 0.1
ipickeracc = 100
ipickvel = 10
pgain = 15000

left_queue = Queue()
pick_queue = Queue()
robot_queue = Queue()
# left hand cmd trigger in sec
pick_timing = np.array(
    [5., 5.312, 6.75, 7.062, 7.312, 7.562, 7.938, 8.625, 9.375, 9.75, 10.125, 10.5, 12.812, 13.062, 13.312, 13.5,
     13.875, 14.25]) * 1000 - 50
# right hand pick cmd trigger in sec
left_hand_timing = np.array(
    [7.06 - 0.18, 7.31 - 0.18, 7.56 - 0.18, 9.26, 9.92, 10.34, 11.5, 12.93, 13, 13.415]) * 1000
# song length in sec

for i in range(len(pick_timing)):
    pick_timing[i] = int(pick_timing[i] / 10) * 10
# right hand pick cmd trigger in sec

for i in range(len(left_hand_timing)):
    left_hand_timing[i] = int(left_hand_timing[i] / 10) * 10
# right hand pick cmd trigger in sec
# song length in sec
song_length = 20
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


onsets, notes_duration, notes_vel = midi_info('IHS26midi.MID')
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

    # def get_traj(self, note_i, note_f, move_time):
    #     pos_z = self._fifth_poly(note_i, note_f, move_time)
    #
    #     pos_y = np.ones(len(pos_z)) * INIT_POSE[1]
    #     return pos_y, pos_z
    def get_traj(self, note_i, note_f, move_time, wait_time):
        pos_z = self._fifth_poly(note_i, note_f, move_time)

        pos_y = np.ones(len(pos_z)) * INIT_POSE[1]
        pos_z = np.append(pos_z, np.ones(int(wait_time * SYNC_RATE)) * pos_z[-1])
        pos_y = np.append(pos_y, np.ones(int(wait_time * SYNC_RATE)) * INIT_POSE[1])
        return pos_y, pos_z

    def lefthand_move(self):
        # First Measure
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 2], ifretnumber=[1, 1, 7, 5, 3, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 2], ifretnumber=[1, 1, 7, 5, 3, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 2], ifretnumber=[1, 1, 7, 5, 3, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 2], ifretnumber=[1, 1, 7, 5, 3, 5])
        # Second Measure

        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 3, 2, 2, 3], ifretnumber=[1, 1, 7, 7, 6, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 3, 2, 2, 3], ifretnumber=[1, 1, 7, 7, 6, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 3, 2, 2, 3], ifretnumber=[1, 1, 7, 7, 6, 5])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 3], ifretnumber=[1, 1, 7, 5, 6, 5])
        # Third Measure
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 3, 2, 2, 2, 3], ifretnumber=[1, 1, 7, 5, 3, 5])
        # Fourth Measure (No shape changes)
        return 0

    def pick_move(self):
        # First Measure
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 8 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        angle = 7 * -1
        pick_queue.get()
        self.guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pgain, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

    def traj_generation(self):
        posZ = []
        posY = []
        # Starts on Fifth Note of Measure One
        init = np.array([6, 6, 3, 4, 3, 4, 5, 6, 5, 4, 5, 4, 3, 4, 3, 4, 5]) - 1
        end = np.array([6, 3, 4, 3, 4, 5, 6, 5, 4, 5, 4, 3, 4, 3, 4, 5, 5]) - 1

        for i in range(len(onsets) - 1):
            pos_y, pos_z = self.get_traj(PICK_PT[init[i]], PICK_PT[end[i]], move_time,
                                         onsets[1 + i] - onsets[i] - move_time)
            posZ = np.append(posZ, pos_z)
            posY = np.append(posY, pos_y)

        # pos_y, pos_z = self.get_traj(PICK_PT[5], PICK_PT[5], .312)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[5], PICK_PT[2], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], 1.338)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .212)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[2], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], .15)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .276)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[4], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[4], .587)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[5], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[5], PICK_PT[5], .65)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[5], PICK_PT[4], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[4], .275)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .275)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[4], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[4], .275)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .275)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # # 12.81
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[2], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], 2.212)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # # 13.06
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .15)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # # 13.31
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[2], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[2], .3)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[2], PICK_PT[3], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[3], .3)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[3], PICK_PT[4], move_time)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[4], .275)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
        # pos_y, pos_z = self.get_traj(PICK_PT[4], PICK_PT[4], .375)
        # posZ = np.append(posZ, pos_z)
        # posY = np.append(posY, pos_y)
        #
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
    # grc.traj_generation()
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
        # logging.info(time_stamp)
        time.sleep(0.005 - (time.time() - t_i))

        # print(time_stamp)
    logging.info("end")
    grc.thread_end()


if __name__ == '__main__':
    main()
