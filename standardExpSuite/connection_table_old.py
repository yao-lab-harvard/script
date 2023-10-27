from labscript import *
# from labscript_utils.labconfig import labconfig

def do_connectiontable():

    required_config_params = {
        "DEFAULT": ["apparatus_name", "app_saved_configs"],
        "programs": ["text_editor", "text_editor_arguments"],
        "paths": ["shared_drive", "connection_table_h5", "connection_table_py"],
        "ports": ["BLACS", "lyse"]
    }
    # exp_config = LabConfig(required_params = required_config_params)

    from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
    from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
    from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
    from labscript_devices.NI_DAQmx.models import NI_USB_6363 #NI_PCIe_6343
    from labscript_devices.SRS384 import SRS384, SRS384DDS

    ##############################
    ## Connection table ##
    ##############################
    # The Pulseblaster is triggering the FPGA and the NI DAQ
    PulseBlasterESRPro500(name='pb')#loop_number = numIterations
    ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
    ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

    DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
    DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
    DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
    DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
    DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????


    NI_USB_6363(name = 'NIDAQ',
        parent_device = pb_clockline,
        clock_terminal = '/Dev2/PFI5',
        MAX_name = 'Dev2',
        static_AO = False,
        stop_order = -1,
        acquisition_rate = 1e5
        )
    AnalogOut('galvoX', NIDAQ, 'ao0') 
    AnalogOut('galvoY', NIDAQ, 'ao1')
    AnalogOut('freqMod', NIDAQ, 'ao2')
    AnalogOut('anaout_3', NIDAQ, 'ao3') #dummy; need an even number of AO
    GatedCounterIn("DAQCounter", NIDAQ, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
    DigitalOut('daq_dout_8', NIDAQ, 'port0/line8') 
    DigitalOut('daq_dout_9', NIDAQ, 'port0/line9') 


    ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
    ZCU111DDS('FPGA', ZCU, 'a')


    PiezoEO(name = 'EO', parent_device = pb_clockline_2)
    PiezoEODDS('Piezo', EO, 'a')


    SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
    SRS384DDS('SRSDDS1', SRS1, 'a1')
    SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
    SRS384DDS('SRSDDS2', SRS2, 'a2')
    ##############################
    ## END Connection table ##
    ##############################




















# from labscript import *
# from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
# from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
# from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
# from labscript_devices.NI_DAQmx.models import NI_USB_6363 #NI_PCIe_6343
# from labscript_devices.SRS384 import SRS384, SRS384DDS

# ##############################
# ## Connection table ##
# ##############################
# # The Pulseblaster is triggering the FPGA and the NI DAQ
# PulseBlasterESRPro500(name='pb')#loop_number = numIterations
# ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
# ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

# DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
# DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
# DigitalOut('FPGAtrig',pb.direct_outputs, 'flag 3') #FPGA trigger
# DigitalOut('MWswitch',pb.direct_outputs, 'flag 4') #MW gate
# DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate ?????????


# NI_USB_6363(name = 'NIDAQ',
#     parent_device = pb_clockline,
#     clock_terminal = '/Dev2/PFI5',
#     MAX_name = 'Dev2',
#     static_AO = False,
#     stop_order = -1,
#     acquisition_rate = 1e5
#     )
# AnalogOut('galvoX', NIDAQ, 'ao0') 
# AnalogOut('galvoY', NIDAQ, 'ao1')
# AnalogOut('freqMod', NIDAQ, 'ao2')
# AnalogOut('anaout_3', NIDAQ, 'ao3') #dummy; need an even number of AO
# GatedCounterIn("DAQCounter", NIDAQ, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
# DigitalOut('daq_dout_8', NIDAQ, 'port0/line8') 
# DigitalOut('daq_dout_9', NIDAQ, 'port0/line9') 


# ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
# ZCU111DDS('FPGA', ZCU, 'a')


# PiezoEO(name = 'EO', parent_device = pb_clockline_2)
# PiezoEODDS('Piezo', EO, 'a')


# SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
# SRS384DDS('SRSDDS1', SRS1, 'a1')
# SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
# SRS384DDS('SRSDDS2', SRS2, 'a2')
# ##############################
# ## END Connection table ##
# ##############################
# ##############################
# ## Connection table ##
# ##############################
# PulseBlasterESRPro500(name='pb')
# #PulseBlasterESRPro500(name= 'pb', loop_number = numIterations,  extra_flags = 3, extra_inst = 3, extra_inst_data = 3, extra_length= 10, inst_location = 13, additional_inst = 8, loop_start = 1, board_number = 0, programming_scheme = 'pb_start/BRANCH')
# ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
# ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

# NI_PCIe_6343(name = 'Dev2',
#     parent_device = pb_clockline,
#     clock_terminal = '/Dev2/PFI5',
#     MAX_name = 'Dev2',
#     static_AO = True,
#     stop_order = -1,
#     acquisition_rate = 1e5
#     )
# DigitalOut('pb_1',pb.direct_outputs, 'flag 1') #counter readout
# DigitalOut('pb_2',pb.direct_outputs, 'flag 2') #laser 
# DigitalOut('pb_3',pb.direct_outputs, 'flag 3') #MW trigger
# DigitalOut('pb_4',pb.direct_outputs, 'flag 4') #MW gate
# DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate

# StaticAnalogOut('anaout_0', Dev2, 'ao0')
# StaticAnalogOut('anaout_1', Dev2, 'ao1')

# GatedCounterIn("myCounter", Dev2, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
# # GatedCounterIn("counter", Dev2, connection = "ctr2", CPT_connection = "PFI0", trigger = "PFI1", numIterations = numIterations)
# #ctr 1 is cpt

# DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
# DigitalOut('daq_dout_9', Dev2, 'port0/line9') 
# ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
# ZCU111DDS('FPGA', ZCU, 'a')
# PiezoEO(name = 'EO', parent_device = pb_clockline_2)
# PiezoEODDS('Piezo', EO, 'a')
# SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
# SRS384DDS('SRSDDS1', SRS1, 'a1')
# SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
# SRS384DDS('SRSDDS2', SRS2, 'a2')



if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    do_connectiontable()
    start()
    t=0
    # Stop the experiment shot with stop()
    stop(t+10e-6)#1.0)

