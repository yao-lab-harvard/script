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
######## make laser spot point to correct location #########
t+=10e-6 #need this if AO are not static
galvoX.constant(t, Vx_laser) 
galvoY.constant(t, Vy_laser)  


############################# polarize, collect ########################################
t+=10e-6
laser.go_high(t)
delta = 50e-9 

for i in range(timescan_Points):
    # pb.startLoop(t, ['outer', 1], timescan_Points)
    # t+=50e-9
    ctrGate.go_high(t+timescan_ctrDelay) #start reference counts
    DAQCounter.acquire(numIterations=timescan_Points*timescan_numIterations, label='scan')
    t+=delta
    ctrGate.go_low(t+timescan_ctrDelay) #stop reference counts
    t+=delta
    # pb.endLoop(t, ['outer', 1])     

############################# collect ref ########################################
t+=1e-6
laser.go_low(t+2e-6)

t+=2.5e-6
pb.outerLoop(timescan_numIterations) 
stop(t+10e-3)
##############################
## END sequence ##
##############################
####################################################################################################################################################################################