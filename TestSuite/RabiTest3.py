from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_USB_6363 
from labscript_devices.SRS384 import SRS384, SRS384DDS
####################################################################################################################################################################################
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


NI_USB_6363(name = 'NIDAQ',
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    static_AO = False,
    stop_order = -1,
    acquisition_rate = 1e5
    )
AnalogOut('galvoX', NIDAQ, 'ao0') 
AnalogOut('galvoY', NIDAQ, 'ao1')
AnalogOut('freqMod', NIDAQ, 'ao2')
AnalogOut('anaout_3', NIDAQ, 'ao3') #dummy
GatedCounterIn("DAQCounter", NIDAQ, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
DigitalOut('daq_dout_8', NIDAQ, 'port0/line8') 
DigitalOut('daq_dout_9', NIDAQ, 'port0/line9') 


ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
ZCU111DDS('FPGA', ZCU, 'a')


PiezoEO(name = 'EO', parent_device = pb_clockline_2)
PiezoEODDS('Piezo', EO, 'a')


SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
SRS384DDS('SRSDDS1', SRS1, 'a1')
SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
SRS384DDS('SRSDDS2', SRS2, 'a2')
##############################
## END Connection table ##
##############################
####################################################################################################################################################################################
###################################################################################################
## START SEQUENCE ##
###################################################################################################
t = 0  
start()
######## set up instruments ##
Piezo.setamp(t, objPiezoHeight)
######## SRS and FPGA #########
SRSDDS1.setamp(t, rabi_SRSAmp)
SRSDDS1.setfreq(t, rabi_freqCenter + rabi_freqMod)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)

t+=1e-6 # TODO need this if AO are not static type...why?
######## make laser spot point to correct location #########
galvoX.constant(t, Vx_laser) #TODO why can't t=0 here? put back to static?
galvoY.constant(t, Vy_laser)  

FPGA.set_repetitions(t, '2')
FPGA.set_delay_time(t,str(0)) #ejd why string? #us #6.447 + (60 - rabi_pulse_time)/1000
FPGA.set_start_src(t, 'external')
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
if rabi_pulse_time == 0: #ejd can we delete?
    FPGA.add_pulse(3,'buffer',3e-6+ 200e-9, rabi_pulse_time, 0,1000,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    FPGA.add_pulse(4,'buffer',3e-6+ 200e-9, rabi_pulse_time, 0,1000,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
else: #ejd where can I read about the gain 32766?
    #FPGA.add_pulse(2,'buffer',5e-6+ 200e-9, rabi_pulse_time, 32766,100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    FPGA.add_pulse(5,'buffer',0, rabi_pulse_time, 32766, rabi_freqMod,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    FPGA.add_pulse(6,'buffer',0, rabi_pulse_time, 32766, rabi_freqMod,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  

############################# polarize, collect ref ########################################
t+=1e-6
laser.go_high(t) 
t+=rabi_polDuration
ctrGate.go_high(t) #start reference counts
DAQCounter.acquire(numIterations=rabi_numIterations, label='ref')
t+=rabi_ctrGateDuration
ctrGate.go_low(t) #stop reference counts
laser.go_low(t) #laser turns off 


############################# MW pulse ########################################
FPGAtrig.go_high(t) #tells FPGA to output the loaded signal
t += 100e-9
FPGAtrig.go_low(t)
t += 560e-9 # calibrate and then make automatic 


MWswitch.go_high(t) #turn on MW switch
if rabi_pulse_time < 20:
    MWswitch.go_low(t + 40e-9)
elif rabi_pulse_time>= 0:
    add_time_marker(t + (rabi_pulse_time)*(10**(-9)) + 24e-9,'MW switch off')
    MWswitch.go_low(t + (rabi_pulse_time)*(10**(-9)) + 24e-9) #turn it off

############################# collect signal ########################################
laser.go_high(t)
ctrGate.go_high(t+rabi_AOMDelay) #start reference counts
DAQCounter.acquire(numIterations=rabi_numIterations, label='sig1')
ctrGate.go_low(t+rabi_AOMDelay+rabi_ctrGateDuration) #stop reference counts
laser.go_low(t+2e-6)

t+=2.5e-6
pb.outerLoop(rabi_numIterations) #TODO test if working correctly
stop(t)