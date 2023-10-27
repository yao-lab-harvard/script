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

######## make laser spot point to correct location #########
t+=10e-6 #need this if AO are not static
galvoX.constant(t, Vx_laser) 
galvoY.constant(t, Vy_laser)  
######## FPGA #########
FPGA.set_repetitions(t, '2') #FPGA output will repeat
FPGA.set_delay_time(t,str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
FPGA.add_pulse(5,'buffer',0, ODMR_MWpulseDuration*1e9, 32766, freqMod,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer',0, ODMR_MWpulseDuration*1e9, 32766, freqMod,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  

############################# polarize, collect ref ########################################
t+=10e-6
laser.go_high(t) 
for i in range(timescan_Points):
    ctrGate.go_high(t) #start reference counts
    DAQCounter.acquire(numIterations=timescan_Points*timescan_numIterations, label='ref')
    t+=50e-9
    ctrGate.go_low(t) #stop reference counts
    t+=50e-9
t+=8e-6
laser.go_low(t)

############################# MW pulse ########################################
FPGAtrig.go_high(t) #tells FPGA to output the loaded signal
t += 100e-9
FPGAtrig.go_low(t)
t += 560e-9 # calibrate and then make automatic 


MWswitch.go_high(t) #turn on MW switch
if ODMR_MWpulseDuration < 20e-9:
    MWswitch.go_low(t + 40e-9)
elif ODMR_MWpulseDuration >= 0:
    MWswitch.go_low(t + ODMR_MWpulseDuration + 24e-9) #turn it off
# t+=ODMR_MWpulseDuration + 24e-9


############################# collect sig ########################################
laser.go_high(t)
for i in range(timescan_Points):
    ctrGate.go_high(t) 
    DAQCounter.acquire(numIterations=timescan_Points*timescan_numIterations, label='sig')
    t+=50e-9
    ctrGate.go_low(t) 
    t+=50e-9
t+=2e-6
laser.go_low(t)

t+=2.5e-6
# t+=100e-6
pb.outerLoop(ODMR_numIterations) 
stop(t+10e-6)
##############################
## END sequence ##
##############################
####################################################################################################################################################################################