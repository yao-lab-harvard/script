from labscript import *
from labscript_devices.connection_table import do_connectiontable
###################################################################################################
## START SEQUENCE ##
###################################################################################################
do_connectiontable() 
start()
t = 0 
############################################################
################################ set up instruments ##
############################################################
SRSDDS1.setamp(t, ESR_SRS_amp)
SRSDDS1.setfreq(t, ESR_freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_freq_sweep(t)
SRSDDS1.set_sweep_dev(t, freq_dev)
SRSDDS2.enable_mod(t, False)
Piezo.setamp(t, objPiezoHeight)

t+=1e-6 # TODO need this if AO are not static type...why?
######## make laser spot point to correct location #########
galvoX.constant(t, Vx_laser) #TODO why can't t=0 here? put back to static?
galvoY.constant(t, Vy_laser)  
AO_3.constant(t,0) #dummy

laser.go_high(t)
MWswitch.go_high(t)
for i in range(ESR_numIterations):
    pb.startLoop(t, ['outer', 1], ESR_numIterations)
    ESRfreqMod.constant(t, .5)
    t+=ESR_dt 
    for j in range(ESR_numPoints):
        pb.startLoop(t, ['inner', 1, 1], ESR_numPoints)
        if j < ESR_numPoints/2:
            ESRfreqMod.constant(t, -1 + 2*j/(ESR_numPoints/2 - 1))
        else:
            ESRfreqMod.constant(t,3 - 2*j/(ESR_numPoints/2 - 1))
        ctrGate.go_high(t)
        DAQCounter.acquire(numIterations=ESR_numIterations*(ESR_numPoints), label='ctrIn')
        t+=3*ESR_dt    
        ctrGate.go_low(t)       
        t+=ESR_dt
        pb.endLoop(t, ['inner', 1, 1])
    ESRfreqMod.constant(t, 0)
    t+=123.4e-6#10e-3#300e-6#500e-6
    pb.endLoop(t, ['outer', 1])      
            
laser.go_low(t)
MWswitch.go_low(t)
t += 10e-6
pb.outerLoop(0)
stop(t)