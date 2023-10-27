from labscript import *
from labscript_devices.connection_table import do_connectiontable
###################################################################################################
## START SEQUENCE ##
###################################################################################################
do_connectiontable() 
start()
t = 0  
Piezo.setamp(t, objPiezoHeight)


t += 1e-6
# anaout_3.constant(t,0) #dummy
laser.go_high(t)
t+= 1e-6

for i in range(xPoints):
    pb.startLoop(t, ['outer', 1], xPoints)
    galvoX.constant(t, Vx_offset+Vx_min + i*(Vx_max-Vx_min)/xPoints) 
    t+=100e-6#123.4e-6#dt
    for j in range(yPoints):    
        pb.startLoop(t, ['inner', 1, 1], yPoints)
        if j < yPoints/2:
            galvoY.constant(t, Vy_offset+Vy_min + j*(Vy_max-Vy_min)/(yPoints/2)) 
        else:
            galvoY.constant(t, Vy_offset+Vy_max + (Vy_max-Vy_min) - j*(Vy_max-Vy_min)/(yPoints/2)) 
        t+=dt
        ctrGate.go_high(t)
        DAQCounter.acquire(numIterations=xPoints*yPoints, label='scan')
        t+=3*dt        
        ctrGate.go_low(t) 
        pb.endLoop(t, ['inner', 1, 1])
    t+=10e-6    
    pb.endLoop(t, ['outer', 1])

t += 10e-6
laser.go_low(t)
pb.outerLoop(0)
stop(t+1e-6)
##############################
## END sequence ##
##############################
####################################################################################################################################################################################