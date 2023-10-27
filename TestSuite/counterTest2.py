from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS


##############################
## Connection table ##
##############################
# The Pulseblaster is triggering the FPGA and the NI DAQ
PulseBlasterESRPro500(name='pb')#loop_number = numIterations
pb.setParams(numIterations)
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????


NI_PCIe_6343(name = 'Dev2',
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    static_AO = True,
    stop_order = -1,
    acquisition_rate = 1e5
    )
StaticAnalogOut('anaout_0', Dev2, 'ao0') #dev2 is the NI DAq...RENAME
StaticAnalogOut('anaout_1', Dev2, 'ao1')
GatedCounterIn("myCounter", Dev2, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
DigitalOut('daq_dout_9', Dev2, 'port0/line9') 


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
## START SEQUENCE ##
##############################
t = 0  
add_time_marker(t, "Start", verbose = True)
start()

############################################################
################################ set up instruments ##
############################################################
######## make laser spot point to correct location #########
# Piezo.setamp(t, objPiezoHeight)
# anaout_0.constant(V_laser_x)
# anaout_1.constant(V_laser_y)  

t+=10e-6
laser.go_high(t) 
ctrGate.go_high(t+ctrGateDelay) #start reference counts
myCounter.acquire(numIterations=numIterations, label='ref')
ctrGate.go_low(t+ctrGateDelay+ctrGateDuration) #stop reference counts
laser.go_low(t+2e-6) #laser turns off 
t+=10e-6

# laser.go_high(t)
ctrGate.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig1')
ctrGate.go_low(t+1.25*ctrGateDuration) #stop reference counts
t+=10e-6
# laser.go_low(t+polDuration)
ctrGate.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig2')
ctrGate.go_low(t+1.5*ctrGateDuration) #stop reference counts
t+=10e-6
ctrGate.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig3')
ctrGate.go_low(t+1.75*ctrGateDuration) #stop reference counts
t+=10e-6
ctrGate.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig4')
ctrGate.go_low(t+2*ctrGateDuration) #stop reference counts
t+=10e-6


t+=50e-6
stop(t)