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
PulseBlasterESRPro500(name='pb')
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
    static_AO = False,
    stop_order = -1,
    acquisition_rate = 1e5
    )
AnalogOut('galvoX', Dev2, 'ao0') #dev2 is the NI DAq...RENAME
AnalogOut('galvoY', Dev2, 'ao1')
AnalogOut('freqMod', Dev2, 'ao2')
AnalogOut('anaout_3', Dev2, 'ao3') #dummy

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
## START sequence ##
##############################
t = 0  
add_time_marker(t, "Start", verbose = True)
start()
############################################################
################################ set up instruments ##
############################################################
SRSDDS1.setamp(t, ESR_SRS_amp)
SRSDDS1.setfreq(t, ESR_freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_freq_sweep(t)
# SRSDDS1.set_sweep_rate(t, freq_sweep_rate) #TODO needed
SRSDDS1.set_sweep_dev(t, freq_dev)
SRSDDS2.enable_mod(t, False)
Piezo.setamp(t, objPiezoHeight)

t+=1e-6 # TODO need this if AO are not static type...why?

######## make laser spot point to correct location #########
galvoX.constant(t, V_laser_x) #TODO why can't t=0 here? put back to static?
galvoY.constant(t, V_laser_y)  
anaout_3.constant(t,0) #dummy

laser.go_high(t)
MWswitch.go_high(t)
for i in range(repetitions):
    pb.startLoop(t, ['outer', 1], repetitions)
    # ctrGate.go_high(t)
    freqMod.constant(t, .5)
    t+=SRS_dt #1123.4e-6#
    # ctrGate.go_low(t)
    # t+=7.8e-6
    for j in range(N_data_points):
        pb.startLoop(t, ['inner', 1, 1], N_data_points)
        if j < N_data_points/2:
            freqMod.constant(t, -1 + 2*j/(N_data_points/2 - 1))
        else:
            freqMod.constant(t,3 - 2*j/(N_data_points/2 - 1))
        ctrGate.go_high(t)
        myCounter.acquire(numIterations=repetitions*(N_data_points), label='ctrIn')
        t+=3*SRS_dt     #567e-6# 
        ctrGate.go_low(t)       
        t+=SRS_dt#123.4e-6#
        pb.endLoop(t, ['inner', 1, 1])
    # ctrGate.go_high(t)
    freqMod.constant(t, 0)
    # t+=3.42e-6
    # ctrGate.go_low(t)
    t+=123.4e-6#10e-3#300e-6#500e-6
    pb.endLoop(t, ['outer', 1])      
            
laser.go_low(t)
MWswitch.go_low(t)
t += 10e-6
pb.outerLoop(0)
stop(t)