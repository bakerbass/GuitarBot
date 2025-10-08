import matplotlib.pyplot as plt
import GuitarBotParser as gpb
start_pos = 838
qf_encoder_picker = 512.0
NUM_PLUCK_POINTS = 11
TRAJECTORY_BLEND_PERCENT = 0.2
all_points = gpb.GuitarBotParser.interp_with_blend(start_pos, qf_encoder_picker, NUM_PLUCK_POINTS, TRAJECTORY_BLEND_PERCENT)
plt.plot(all_points)
plt.show()