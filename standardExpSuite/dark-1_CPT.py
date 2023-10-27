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
galvoX.constant(Vx_laser) 
galvoY.constant(Vy_laser)  

FPGA.set_repetitions(t, '1') #FPGA output will repeat
FPGA.set_delay_time(t,str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
delay_temp = -265e-9
FPGA.add_pulse(5,'buffer',0, bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer',0, bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
FPGA.add_pulse(5,'buffer', dark_T + (bright_Pitime)*1e-9 + 40e-9 + polDuration + 200e-9,
                 bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer', dark_T + (bright_Pitime)*1e-9 + 40e-9 + polDuration + 200e-9,
                 bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _
FPGA.add_pulse(5,'buffer', 2*dark_T + 2*((bright_Pitime)*1e-9 + 40e-9) + polDuration + 400e-9 + delay_temp,
                 bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer', 2*dark_T + 2*((bright_Pitime)*1e-9 + 40e-9) + polDuration + 400e-9 + delay_temp,
                 bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _

############################# polarize, collcet ref ###########################

t += 1e-6
laser.go_high(t)
t += polDuration
t += bright_ctrDelay*1e-9
tStart = t
t += 1e-6 # collect reference
#ctrGate.go_high(t) #start counter

############################# MW pulse ########################################

FPGAtrig.go_high(t) #tells FPGA to outpu/sig[0]t the loaded signal
t += 100e-9
FPGAtrig.go_low(t)
t += 560e-9 # calibrate and then make automatic 

MWswitch.go_high(t) #turn on MW switch
t += (bright_Pitime)*1e-9 + 40e-9
MWswitch.go_low(t) #turn it off
t += 200e-9
 
############################# collect bright signal ##################################

t += dark_T

############################# polarize, collect ref ###########################

buffer = 0e-9
buffer2 = 50e-9
t += polDuration-buffer

################### dark-1 part, MW 2nd and 3rd Pi^-1 pulse ####################
CPT_ctr_Delay = 40e-9
if dark_T < 1000e-9:
    MWswitch.go_high(t) #turn on MW switch
    t += buffer
    t += (bright_Pitime)*1e-9 + 40e-9
    #MWswitch.go_low(t + buffer) #turn it off
    #t += 200e-9 + buffer

    t += dark_T - buffer2
    tStart2 = t + CPT_ctr_Delay
    ctrGate.go_high(t + CPT_ctr_Delay) #start counter

    #MWswitch.go_high(t) #turn on MW switch
    t += buffer2
    t += (bright_Pitime)*1e-9 + 40e-9
    MWswitch.go_low(t + buffer2) #turn it off
    t += 200e-9 + buffer2
else:
    MWswitch.go_high(t) #turn on MW switch
    t += buffer
    t += (bright_Pitime)*1e-9 + 40e-9
    MWswitch.go_low(t + buffer) #turn it off
    t += buffer

    t += dark_T - buffer2
    tStart2 = t + CPT_ctr_Delay
    ctrGate.go_high(t + CPT_ctr_Delay) #start counter

    MWswitch.go_high(t) #turn on MW switch
    t += buffer2
    t += (bright_Pitime)*1e-9 + 40e-9
    MWswitch.go_low(t + buffer2) #turn it off
    t += 200e-9 + buffer2

t += 10000e-9
pb.outerLoop(bright_numIterations) #TODO test if working correctly
tStop = t
DAQCounter.acquire('CPT', numIterations=bright_numIterations, 
                    label='scan',start_time=tStart2,end_time=tStop,sample_freq=5e6)
# print(tStart, tStop, (tStop - tStart)*5e6)
stop(t + 1e-6)

## END sequence ##
###############################################################################