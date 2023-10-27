from labscript import *

def do_connectiontable():
    print('doing connection table!')
    from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
    from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
    from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
    from labscript_devices.NI_DAQmx.models import NI_USB_6363 #NI_PCIe_6343
    from labscript_devices.SRS384 import SRS384, SRS384DDS


    ##### The Pulseblaster is triggering the FPGA and the NI DAQ
    PulseBlasterESRPro500(name='pb')
    ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
    ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

    DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
    DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
    DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
    DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
    DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????

    ##### NI DAQ
    NI_USB_6363(name = 'NIDAQ',
        parent_device = pb_clockline,
        clock_terminal = '/Dev2/PFI5',
        MAX_name = 'Dev2',
        #static_AO = False,
        static_AO = True,
        stop_order = -1,
        acquisition_rate = 1e5
        )
    # if static_AO:
    StaticAnalogOut('galvoX', NIDAQ, 'ao0')
    StaticAnalogOut('galvoY', NIDAQ, 'ao1')
    # else:
    #     AnalogOut('galvoX', NIDAQ, 'ao0') 
    #     AnalogOut('galvoY', NIDAQ, 'ao1')
    # AnalogOut('galvoX', NIDAQ, 'ao0') 
    # AnalogOut('galvoY', NIDAQ, 'ao1')        
    # AnalogOut('ESRfreqMod', NIDAQ, 'ao2')
    # AnalogOut('AO_3', NIDAQ, 'ao3') #dummy; need an even number of AO`
    #CounterIn("DAQCounter", NIDAQ, connection = "ctr2", CPT_connection = "ctr1", gate = "PFI1", trigger = "")
    GatedCounterIn("DAQCounter", NIDAQ, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
    DigitalOut('DO_8', NIDAQ, 'port0/line8') 
    DigitalOut('DO_9', NIDAQ, 'port0/line9') 

    ##### FPGA
    ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
    ZCU111DDS('FPGA', ZCU, 'a')

    ##### Piezo for objective
    PiezoEO(name = 'EO', parent_device = pb_clockline_2)
    PiezoEODDS('Piezo', EO, 'a')

    ##### SRS 
    SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
    SRS384DDS('SRSDDS1', SRS1, 'a1')
    SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
    SRS384DDS('SRSDDS2', SRS2, 'a2')
    ##############################
    ## END Connection table ##
    ##############################


if __name__ == '__main__':
    do_connectiontable()
    start()
    t=0
    stop(t+1e-6)