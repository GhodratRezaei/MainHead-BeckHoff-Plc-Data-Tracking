import pyads
from pyads import PLCTYPE_BOOL, PLCTYPE_INT, PLCTYPE_DINT, PLCTYPE_REAL, PLCTYPE_STRING

structure_defin = [
   	("bWSG_BC_RH_AUT_ADJ_ENAB", PLCTYPE_BOOL),
	("nWSG_WC_RH_ADJ_STEP", PLCTYPE_DINT),
	("fWSG_WC_RH_AUT_ADJ_DB", PLCTYPE_REAL),
	("nWSG_WC_RH_INIT_GAP", PLCTYPE_DINT),
	("fWSG_WC_RLR_CAV_DPTH", PLCTYPE_REAL),
	("fWSG_WC_RH_ENC_PLS", PLCTYPE_REAL),
	("fWSG_WC_RH_MOT_RATIO", PLCTYPE_REAL),
	("fWSG_WC_RH_SCW_RATIO", PLCTYPE_REAL),
	("arrWSG_WC_POS_SET_RH", [PLCTYPE_DINT] * 5),
	("sWSG_MEM_WR_ID", PLCTYPE_STRING(12)),
	("fWSG_MEM_WR_RLR_DIAM", PLCTYPE_REAL),
	("nWSG_MEM_WR_RH_INIT_GAP", PLCTYPE_DINT),
	("nWSG_MEM_WR_CNT", PLCTYPE_INT),
	("sWSG_MEM_WR_DAN_ID", PLCTYPE_STRING(12)),
	("nWSG_MEM_WR_STRK_RH1", PLCTYPE_DINT),
	("nWSG_MEM_WR_STRK_RH2", PLCTYPE_DINT),
	("nWSG_MEM_WR_POS_RH1", PLCTYPE_DINT),
	("nWSG_MEM_WR_POS_RH2", PLCTYPE_DINT)
]



# connect to plc and open connection
plc = pyads.Connection('192.168.92.62.1.1', pyads.PORT_TC3PLC1)
plc.open()
 
## read int value by name
bool_signal_data = plc.read_by_name("IoT_MAIN.WSG20.bSignal")

structure_data = plc.read_structure_by_name("IoT_MAIN.WSG20.stConnected", structure_defin)
 

print(bool_signal_data) 
print("######################################################################")
print(structure_data)


# close connection
plc.close()