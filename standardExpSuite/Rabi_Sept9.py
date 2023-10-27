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
SRSDDS1.setamp(t, rabi_SRSAmp)
SRSDDS1.setfreq(t, rabi_freqCenter + rabi_freqMod)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)

######## make laser spot point to correct location #########
t+=0.5e-6 #need this if AO are not static
galvoX.constant(t, Vx_laser) 
galvoY.constant(t, Vy_laser)
#galvoX.constant(Vx_laser) 
#galvoY.constant(Vy_laser)  

FPGA.set_repetitions(t, '2') #FPGA output will repeat
FPGA.set_delay_time(t, str(2)) #ejd #this is the delay between repetitions. Will be 500ns + whatever the argument is.
FPGA.set_start_src(t, 'external') #FPGA will be triggered
FPGA.add_TTL(4, 0, 10e-9) #ejd what is this?
#ejd where can I read about the gain 32766?
FPGA.add_pulse(5,'buffer',0, rabi_pulse_time, 32766, rabi_freqMod,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
FPGA.add_pulse(6,'buffer',0, rabi_pulse_time, 32766, rabi_freqMod,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  

############################# polarize, collect ref ########################################

t+=1e-6
laser.go_high(t) 
t+=rabi_polDuration
ctrGate.go_high(t) #start reference counts
#DAQCounter.acquire(numIterations=rabi_numIterations, label='ref', method = ) #method can be gated or CPT
DAQCounter.acquire(numIterations=rabi_numIterations, label='ref')
t+=rabi_ctrGateDuration
ctrGate.go_low(t) #stop reference counts
laser.go_low(t) #laser turns off 

############################# MW pulse ########################################

FPGAtrig.go_high(t) #tells FPGA to output the loaded signal
t += 300e-9
FPGAtrig.go_low(t)
t += 360e-9 # calibrate and then make automatic 

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
stop(t+1e-6)
##############################
## END sequence ##
##############################
####################################################################################################################################################################################