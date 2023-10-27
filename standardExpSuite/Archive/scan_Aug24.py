# from labscript import *
# from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
# from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
# from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
# from labscript_devices.NI_DAQmx.models import NI_PCIe_6343#NI_USB_6363
# from labscript_devices.SRS384 import SRS384, SRS384DDS


# ##############################
# ## Connection table ##
# ##############################
# # The Pulseblaster is triggering the FPGA and the NI DAQ
# PulseBlasterESRPro500(name='pb')
# ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
# ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

# DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
# DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
# DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
# DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
# DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????

# NI_PCIe_6343(name = 'Dev2',
#     parent_device = pb_clockline,
#     clock_terminal = '/Dev2/PFI5',
#     MAX_name = 'Dev2',
#     static_AO = False,
#     stop_order = -1,
#     acquisition_rate = 1e5
#     )
# AnalogOut('galvoX', Dev2, 'ao0') #dev2 is the NI DAq...RENAME
# AnalogOut('galvoY', Dev2, 'ao1')
# # AnalogOut('freqMod', Dev2, 'ao2')
# # AnalogOut('anaout_3', Dev2, 'ao3') #dummy

# GatedCounterIn("myCounter", Dev2, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
# DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
# DigitalOut('daq_dout_9', Dev2, 'port0/line9') 


# ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
# ZCU111DDS('ZCUDDS', ZCU, 'a')


# PiezoEO(name = 'EO', parent_device = pb_clockline_2)
# PiezoEODDS('Piezo', EO, 'a')


# SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
# SRS384DDS('SRSDDS1', SRS1, 'a1')
# SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
# SRS384DDS('SRSDDS2', SRS2, 'a2')
# ##############################
# ## END Connection table ##
# ##############################
from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_USB_6343 #NI_PCIe_6343 #why are we using 6343? I thought we use 6363....
# from labscript_devices.NI_DAQmx.models import NI_PCIe_6343 #why are we using 6343? I thought we use 6363....
from labscript_devices.SRS384 import SRS384, SRS384DDS
##############################
## Connection table ##
##############################
# The Pulseblaster is triggering the FPGA and the NI DAQ
PulseBlasterESRPro500(name='pb')#loop_number = numIterations
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????


NI_USB_6343(name = 'NIDAQ',
    parent_device = pb_clockline,
    clock_terminal = '/Dev1/PFI5',
    MAX_name = 'Dev1',
    static_AO = False,
    stop_order = -1,
    acquisition_rate = 1e5
    )
AnalogOut('galvoX', NIDAQ, 'ao0') 
AnalogOut('galvoY', NIDAQ, 'ao1')
# AnalogOut('freqMod', NIDAQ, 'ao2')
# AnalogOut('anaout_3', NIDAQ, 'ao3') #dummy
GatedCounterIn("myCounter", NIDAQ, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
DigitalOut('daq_dout_8', NIDAQ, 'port0/line8') 
DigitalOut('daq_dout_9', NIDAQ, 'port0/line9') 


ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
ZCU111DDS('ZCUDDS', ZCU, 'a')


PiezoEO(name = 'EO', parent_device = pb_clockline_2)
PiezoEODDS('Piezo', EO, 'a')


SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
SRS384DDS('SRSDDS1', SRS1, 'a1')
SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
SRS384DDS('SRSDDS2', SRS2, 'a2')
##############################
## END Connection table ##
##############################
##############################
## START sequence ##
##############################
t = 0  
add_time_marker(t, "Start", verbose = True)
start()
Piezo.setamp(t, objPiezoHeight)


t += 100e-6
# anaout_3.constant(t,0) #dummy
galvoX.constant(t, 0.25)
galvoY.constant(t, 0.25)
laser.go_high(t)
t+= 100e-6
galvoX.constant(t, 0.5)
galvoY.constant(t, 0.5)
t+= 100e-6

for i in range(x_points):
    pb.startLoop(t, ['outer', 1], x_points)
    galvoX.constant(t, V_x_offset+V_x_min + i*(V_x_max-V_x_min)/x_points) 
    t+=100e-6#123.4e-6#dt
    for j in range(y_points):    
        pb.startLoop(t, ['inner', 1, 1], y_points)
        if j < y_points/2:
            galvoY.constant(t, V_y_offset+V_y_min + j*(V_y_max-V_y_min)/(y_points/2)) 
        else:
            galvoY.constant(t, V_y_offset+V_y_max + (V_y_max-V_y_min) - j*(V_y_max-V_y_min)/(y_points/2)) 
        t+=dt
        ctrGate.go_high(t)
        myCounter.acquire(numIterations=x_points*y_points, label='scan')
        t+=3*dt        
        ctrGate.go_low(t) 
        pb.endLoop(t, ['inner', 1, 1])
    t+=1e-3#dt    
    pb.endLoop(t, ['outer', 1])

t += 10e-6
laser.go_low(t)
pb.outerLoop(0)
stop(t)
##############################
## END sequence ##
##############################