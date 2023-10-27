from labscript import *
from labscript_devices.connection_table import do_connectiontable
###################################################################################################
## START SEQUENCE ##
###################################################################################################
do_connectiontable() 
start()
t = 0 
######## set up instruments ##
Piezo.setamp(t, objPiezoHeight)
######## SRS and FPGA ########
SRSDDS1.setamp(t, bright_SRSAmp)
SRSDDS1.setfreq(t, bright_freqCenter + bright_freqMod)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)

######## make laser spot point to correct location #########
t+=0.5e-6 #need this if AO are not static
galvoX.constant(t, Vx_laser) 
galvoY.constant(t, Vy_laser)  

FPGA.set_repetitions(t, '1') #FPGA output will repeat
FPGA.set_delay_time(t,str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
delay_temp = 0e-9
FPGA.add_pulse(5,'buffer',0, bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer',0, bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
FPGA.add_pulse(5,'buffer', dark_T + (bright_Pitime)*1e-9 + 40e-9 + polDuration + 100e-9 + dark_ctrduration,
                 bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer', dark_T + (bright_Pitime)*1e-9 + 40e-9 + polDuration + 100e-9 + dark_ctrduration,
                 bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _
FPGA.add_pulse(5,'buffer', 2*dark_T + 2*((bright_Pitime)*1e-9) + 40e-9 + polDuration + 100e-9 + dark_ctrduration,
                 bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer', 2*dark_T + 2*((bright_Pitime)*1e-9) + 40e-9 + polDuration + 100e-9 + dark_ctrduration,
                 bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _

############################# polarize, collcet ref ###########################

t += 1e-6
laser.go_high(t)
t += polDuration
t += bright_ctrDelay*1e-9
tStart = t
t += 1e-6 # collect reference

############################# MW pulse ########################################

FPGAtrig.go_high(t) #tells FPGA to outpu/sig[0]t the loaded signal
t += 100e-9
FPGAtrig.go_low(t)
t += 560e-9 # calibrate and then make automatic 

MWswitch.go_high(t) #turn on MW switch
t += (bright_Pitime)*1e-9 + 40e-9
MWswitch.go_low(t) #turn it off
t += 100e-9
 
############################# collect bright signal ##################################

t += dark_T

ctrGate.go_high(t) #start counter
DAQCounter.acquire(numIterations = bright_numIterations, label = 'sig1')
t += dark_ctrduration
ctrGate.go_low(t)

############################# polarize, collect ref ###########################

buffer = 50e-9
buffer2 = 50e-9
t += polDuration-buffer

################### dark-1 part, MW 2nd and 3rd Pi^-1 pulse ####################
if dark_T < 1000e-9:
    MWswitch.go_high(t) #turn on MW switch
    t += buffer
    t += (bright_Pitime)*1e-9
    t += dark_T
    t += buffer
    t += (bright_Pitime)*1e-9
    MWswitch.go_low(t + buffer2) #turn it off
    t += buffer2
    ctrGate.go_high(t) #start counter
    DAQCounter.acquire(numIterations = bright_numIterations, label = 'sig2')
    t += dark_ctrduration
    ctrGate.go_low(t)
else:
    MWswitch.go_high(t) #turn on MW switch
    t += buffer
    t += (bright_Pitime)*1e-9
    MWswitch.go_low(t + buffer) #turn it off
    t += buffer
    t += dark_T - buffer2
    MWswitch.go_high(t) #turn on MW switch
    t += buffer2
    t += (bright_Pitime)*1e-9
    MWswitch.go_low(t + buffer2) #turn it off
    t += buffer2
    ctrGate.go_high(t) #start counter
    DAQCounter.acquire(numIterations = bright_numIterations, label = 'sig2')
    t += dark_ctrduration
    ctrGate.go_low(t)

#t += 10000e-9

pb.outerLoop(bright_numIterations) #TODO test if working correctly
stop(t + 1e-6)

## END sequence ##
###############################################################################