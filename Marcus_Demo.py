import UIGen
import UIParse
# import UIParseTest
# import RobotController
# import RobotControllerMPWonderWall
import RobotControllerAmit

UI_Out_rightHand, UI_Out_leftHand, measure_time = UIGen.UI()
print("UOrH: ", UI_Out_rightHand)
ri, initStrum, strumOnsets = UIParse.parseright_M(UI_Out_rightHand, measure_time)
li, firstc, mtimings, pi = UIParse.parseleft_M(UI_Out_leftHand, measure_time)

# To save strum
save = False
# to play saved
runsaved = False
# to test
test = False

ri_str = str(ri)
li_str = str(li)
firstc_str = str(firstc)
measure_time_str = str(measure_time)

if save:
    with open('savedPatterns.txt', 'w') as f:
        f.write("ri =  " + ri_str)
        f.write('\n')
        f.write("li =  " + li_str)
        f.write('\n')
        f.write("first_c =  " + firstc_str)
        f.write('\n')
        f.write("measure_time = " + measure_time_str)
        f.close()

if runsaved:
    ri = [[['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''],
          [['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'N', 0.5, 1.0], '']]
    li = [[[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]],
          [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]],
          [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]],
          [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]],
          [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]],
          [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[5, 1, 7, 6, 5, 5], [2, 1, 2, 2, 2, 2]]]
    first_c = [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]]
    measure_time = 4.0
if test:
    ri = [[['D', 'N', 0.5, 1.0], '', ['U', 'N', 0.5, 1.0], '', ['D', 'N', 0.5, 1.0], '', ['U', 'N', 0.5, 1.0], ''], [['D', 'N', 0.5, 1.0], '', ['U', 'N', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], '', ['D', 'C', 0.5, 1.0], ''], [['D', 'N', 0.5, 1.0], '', ['U', 'N', 0.5, 1.0], '', ['D', 'N', 0.5, 1.0], '', ['U', 'N', 0.5, 1.0], '']]
    li = [[[1, 2, 2, 1, 1, 1], [1, 2, 2, 2, 1, 1]], [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], [[8, 7, 5, 5, 5, 1], [2, 2, 2, 2, 2, 1]]]
    firstc =  [[1, 2, 2, 1, 1, 1], [1, 2, 2, 2, 1, 1]]
    measure_time = 4.0

print("ri", ri)
print("li", li)
print("firstc: ", firstc)
print("measure_time: ", measure_time)

RobotControllerAmit.main(ri, li, firstc, measure_time, mtimings, strumOnsets, pi)
