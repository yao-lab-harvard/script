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
galvoX.constant(Vx_laser)
galvoY.constant(Vy_laser)
######## make laser spot point to correct location #########
t+=0.5e-6 #need this if AO are not static
# galvoX.constant(t, Vx_laser) 
# galvoY.constant(t, Vy_laser)  

FPGA.set_repetitions(t, '2') #FPGA output will repeat
FPGA.set_delay_time(t,str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
FPGA.add_pulse(5,'buffer',0, bright_Pitime, 32766, bright_freqMod, 0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer',0, bright_Pitime, 32766, bright_freqMod, 90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  

############################# polarize, collect ref ###########################
t += 1e-6
laser.go_high(t)
t += polDuration
tStart = t
ctrGate.go_high(t + bright_ctrDelay*1e-9) #start counter

############################# MW pulse ########################################

FPGAtrig.go_high(t) #tells FPGA to outpu/sig[0]t the loaded signal
t += 100e-9
FPGAtrig.go_low(t)
t += 560e-9 # calibrate and then make automatic 

MWswitch.go_high(t) #turn on MW switch
MWswitch.go_low(t + (bright_Pitime)*1e-9 + 24e-9) #turn it off
t+=200e-9
############################# collect signal ##################################

t += 20e-6
laser.go_low(t + 2e-6)
ctrGate.go_low(t + 2e-6)

t += 5e-6
pb.outerLoop(bright_numIterations) #TODO test if working correctly
tStop = t
DAQCounter.acquire('CPT', numIterations=bright_numIterations, 
                    label='scan',start_time=tStart,end_time=tStop,sample_freq=5e6)
stop(t + 1e-6)

## END sequence ##
###############################################################################