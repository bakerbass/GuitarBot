import socket
import struct
import time

def send_msg(pos):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_ip = "10.2.1.177"
    udp_port = 8888

    # print("pos: ", pos)
    pCommand = struct.pack('f' * len(pos), *pos)
    sock.sendto(pCommand, (udp_ip, udp_port))

    return 0

def main(song_trajs):
    # print("4")
    # time.sleep(1)
    # print("3")
    # time.sleep(1)
    # print("2")
    # time.sleep(1)
    # print("1")
    # time.sleep(1)

    # print("SONG TRAJS: ", song_trajs)
    interval = 0.005 
    total_start_time = time.time()

    for i, point in enumerate(song_trajs):
        start_time = time.time()
        # print(f"Sending {i}")
        send_msg(point)

        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        time.sleep(sleep_time)

    total_elapsed_time = time.time() - total_start_time
    print(f"Total elapsed time: {total_elapsed_time:.4f} seconds")
    return 0