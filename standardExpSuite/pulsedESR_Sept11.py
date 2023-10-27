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
######## SRS and FPGA #########
SRSDDS1.setamp(t, ODMR_SRSAmp)
SRSDDS1.setfreq(t, ODMR_freqCenter + freqMod)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)

######## make laser spot point to correct location #########
t+=0.5e-6 #need this if AO are not static
galvoX.constant(t, Vx_laser) 
galvoY.constant(t, Vy_laser)  

FPGA.set_repetitions(t, '2') #FPGA output will repeat
FPGA.set_delay_time(t,str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
FPGA.add_pulse(5,'const',0, ODMR_MWpulseDuration*1e9, 32766, freqMod,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'const',0, ODMR_MWpulseDuration*1e9, 32766, freqMod,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  

############################# polarize, collect ref ###########################
t+=1e-6
laser.go_high(t) 
t+=polDuration
ctrGate.go_high(t) #start reference counts
DAQCounter.acquire(numIterations=ODMR_numIterations, label='ref')
t+=ctrGateDuration
ctrGate.go_low(t) #stop reference counts


############################# MW pulse ########################################
FPGAtrig.go_high(t) #tells FPGA to output the loaded signal
t += 200e-9
FPGAtrig.go_low(t)
t += 460e-9 # calibrate and then make automatic 

laser.go_low(t) #laser turns off
t+=AOMDelay

MWswitch.go_high(t) #turn on MW switch
if ODMR_MWpulseDuration < 20e-9:
    MWswitch.go_low(t + 40e-9)
elif ODMR_MWpulseDuration >= 0:
    add_time_marker(t + ODMR_MWpulseDuration + 24e-9,'MW switch off')
    MWswitch.go_low(t + ODMR_MWpulseDuration + 24e-9) #turn it off

############################# collect signal ###################################
t+= ODMR_MWpulseDuration + 24e-9 #- ctrGateDuration
laser.go_high(t)
add_time_marker(t+AOMDelay,'sig detect start')
ctrGate.go_high(t+AOMDelay) #start reference counts
DAQCounter.acquire(numIterations=ODMR_numIterations, label='sig1')
t+=ctrGateDuration
ctrGate.go_low(t+AOMDelay) #stop reference counts
add_time_marker(t+AOMDelay,'sig detect end')
laser.go_low(t+2e-6)
t+=10e-6
pb.outerLoop(ODMR_numIterations)
stop(t+1e-6)
##############################
## END sequence ##
##############################
####################################################################################################################################################################################