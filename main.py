import pyads
from pyads import PLCTYPE_BOOL, PLCTYPE_INT, PLCTYPE_DINT, PLCTYPE_REAL, PLCTYPE_STRING, PLCTYPE_DWORD
import json
import influxdb_client 
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision  
import asyncio  
import subprocess
import time
import numpy as np
import configparser 

"""
structure_def = (
	('rVar', pyads.PLCTYPE_LREAL, 1),
	('sVar', pyads.PLCTYPE_STRING, 2, 35),
	('SVar1', pyads.PLCTYPE_STRING, 1),
	('rVar1', pyads.PLCTYPE_REAL, 1),
	('iVar', pyads.PLCTYPE_DINT, 1),
	('iVar1', pyads.PLCTYPE_INT, 3),
)

i.e ('Variable Name', variable type, arr size (1 if not array),
length of string (if defined in PLC))
"""

# ST_WSG_Connected Data Strcuture (example test)
structure_defin = (
   	("bWSG_BC_RH_AUT_ADJ_ENAB", PLCTYPE_BOOL, 1),
	("nWSG_WC_RH_ADJ_STEP", PLCTYPE_DINT,  1),
	("fWSG_WC_RH_AUT_ADJ_DB", PLCTYPE_REAL, 1),
	("nWSG_WC_RH_INIT_GAP", PLCTYPE_DINT, 1),
	("fWSG_WC_RLR_CAV_DPTH", PLCTYPE_REAL, 1), 
	("fWSG_WC_RH_ENC_PLS", PLCTYPE_REAL, 1),
	("fWSG_WC_RH_MOT_RATIO", PLCTYPE_REAL, 1),
	("fWSG_WC_RH_SCW_RATIO", PLCTYPE_REAL, 1),
	("arrWSG_WC_POS_SET_RH", PLCTYPE_DINT, 2),   # Array of size of two defined in the Twincat.
	("sWSG_MEM_WR_ID", PLCTYPE_STRING, 1, 11),   # String of the size 12 characters defined in the Twincat.
	("fWSG_MEM_WR_RLR_DIAM", PLCTYPE_REAL, 1),
	("nWSG_MEM_WR_RH_INIT_GAP", PLCTYPE_DINT, 1),
	("nWSG_MEM_WR_CNT", PLCTYPE_INT, 1),
	("sWSG_MEM_WR_DAN_ID", PLCTYPE_STRING, 1, 11),  # String of the size 12 characters defined in the Twincat.
	("nWSG_MEM_WR_STRK_RH1", PLCTYPE_DINT, 1) ,
	("nWSG_MEM_WR_STRK_RH2", PLCTYPE_DINT, 1),
	("nWSG_MEM_WR_POS_RH1", PLCTYPE_DINT, 1),
	("nWSG_MEM_WR_POS_RH2", PLCTYPE_DINT, 1)
)

# ST_WSG_INFLUX Data Strcuture
wsg_structure_defin = ( 
	("WSG_BA_GAP_ALR", PLCTYPE_BOOL, 1),
	("WSG_BA_DRV_ERR_RH", PLCTYPE_BOOL, 2),
	("WSG_BA_MOVE_ABS_RH", PLCTYPE_BOOL, 2),
	("WSG_BA_JOG_RH", PLCTYPE_BOOL, 2),
	("WSG_BA_LC_RH", PLCTYPE_BOOL, 2),
	("WSG_BA_STRK_WRN_RH", PLCTYPE_BOOL, 2),
	("WSG_BA_LC_DMG ", PLCTYPE_BOOL, 2),
	("WSG_BA_POS_DIFF ", PLCTYPE_BOOL, 2),
	("WSG_BA_STOP_MOVE_FWD ", PLCTYPE_BOOL, 2),
	("WSG_BA_STOP_MOVE_REV ", PLCTYPE_BOOL, 2),
	("WSG_BA_RH_NOT_LAM ", PLCTYPE_BOOL, 2),
	("INTF_BC_GD_MOV_CNS", PLCTYPE_BOOL, 1),
	("INTF_BS_GD_PRES", PLCTYPE_BOOL, 1),
	("INTF_BS_GD_MAT_PRES", PLCTYPE_BOOL, 1),
	("INTF_WS_RH_LC_DIF_WAIT", PLCTYPE_INT, 1),
	("INTF_WS_RH_LC_DIF_LAM", PLCTYPE_INT, 1),
	("INTF_WS_RH_LC_DIF_TOT", PLCTYPE_INT, 1),
	("INTF_WS_RH_LC_DIF_PCT", PLCTYPE_INT, 1),
	("INTF_WS_RH_GAP", PLCTYPE_INT, 1),
	("WSG_WS_GEN_PRMI_RH", PLCTYPE_INT, 2),
	("WSG_WS_GEN_PRMF_RH", PLCTYPE_INT, 2),
	("WSG_WS_MR_PRMI_RH", PLCTYPE_INT, 2),
	("WSG_WS_MR_PRMF_RH", PLCTYPE_INT, 2),
	("WSG_WS_TRIG", PLCTYPE_INT, 1),
	("WSG_WS_ID", PLCTYPE_STRING, 1, 11),
	("WSG_WS_CNT", PLCTYPE_INT, 1),
	("WSG_WS_RH_LC_DIF_WAIT", PLCTYPE_REAL, 1),
	("WSG_WS_RH_LC_DIF_LAM", PLCTYPE_REAL, 1),
	("WSG_WS_RH_LC_DIF_TOT", PLCTYPE_REAL, 1),
	("WSG_WS_RH_LC_DIF_PCT", PLCTYPE_REAL, 1),
	("WSG_WS_RH_GAP", PLCTYPE_DINT, 1),
	("WSG_WS_RH_LAM_TIM", PLCTYPE_REAL, 1),
	("WSG_WS_RH_IB_TIM", PLCTYPE_REAL, 1),
	("WSG_WS_RH_HIT_DLT_TIM", PLCTYPE_REAL, 1),
	("WSG_WS_HIT_CNT_RH", PLCTYPE_INT, 2),
	("WSG_WS_HIT_MAX_FRC_RH", PLCTYPE_REAL, 2),
	("WSG_WS_I_RH", PLCTYPE_REAL, 2),
	("WSG_WS_TRQ_RH", PLCTYPE_REAL, 2),
	("WSG_WS_V_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LC_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LAM_IMP_RH", PLCTYPE_REAL, 2),
	("WSG_WS_POS_RH", PLCTYPE_DINT, 2),
	("WSG_WS_POS_DLT_RH", PLCTYPE_DINT, 2),
	("WSG_WS_STRK_RH", PLCTYPE_DINT, 2),
	("WSG_WS_RC_STRK_RH", PLCTYPE_DINT, 2),
	("WSG_WS_SPD_RH", PLCTYPE_REAL, 2),
	("WSG_WS_MOT_SPD_RH", PLCTYPE_REAL, 2),
	("WSG_WS_I_SLP_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LC_SLP_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LC_WAIT_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LC_LAM_RH", PLCTYPE_REAL, 2),
	("WSG_WS_LC_DIF_RH", PLCTYPE_REAL, 2),
	("WSG_WS_MR_STRK_TIM_RH", PLCTYPE_REAL, 2),
	("WSG_WS_MR_STEP_RH", PLCTYPE_INT, 2),
	("WSG_WS_TRK_RH", PLCTYPE_INT, 2),
	("WSG_WS_DRV_ERR_RH", PLCTYPE_DWORD, 2),
	("WSG_WS_MOVE_ABS_ERR_RH", PLCTYPE_DWORD, 2),
	("WSG_WS_JOG_ERR_RH", PLCTYPE_DWORD, 2),
	("WSG_WS_REM_MOV_FWD ", PLCTYPE_DINT, 2),
	("WSG_WS_REM_MOV_REV ", PLCTYPE_DINT, 2),
	("WSG_BS_WSG_ACT", PLCTYPE_BOOL, 1),
	("WSG_BS_SEM_RED", PLCTYPE_BOOL, 1),
	("WSG_BS_SEM_YEL", PLCTYPE_BOOL, 1),
	("WSG_BS_SEM_GRN", PLCTYPE_BOOL, 1),
	("WSG_BS_MSG_BRK_OK", PLCTYPE_BOOL, 1),
	("WSG_BS_GD_PRES", PLCTYPE_BOOL, 1),
	("WSG_BS_GD_MAT_PRES", PLCTYPE_BOOL, 1),
	("WSG_BS_PRES_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_MAT_PRES_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_MR_ON_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_MR_DONE_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_RC_ON_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_DRV_ENAB_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_DRV_OPN_RUN_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_DRV_CLS_RUN_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_OPN_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_CLS_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_MID_RH", PLCTYPE_BOOL, 2),
	("WSG_BS_MOVE_END_RH", PLCTYPE_BOOL, 2)
)

# ST_BMS_INFLUX Data Strcuture
bms_structure_defin = (
	("BMS_BA_SPD_DIF_THR_SET", PLCTYPE_BOOL, 1),
	("BMS_BA_SPD_DEC_TIM_SET", PLCTYPE_BOOL, 1),
	("BMS_BA_SPD_SLP_SET", PLCTYPE_BOOL, 1),
	("BMS_BA_RLR_SPD_DIF", PLCTYPE_BOOL, 1),
	("BMS_BA_RLR_DEC_TIM_DIF", PLCTYPE_BOOL, 1),
	("BMS_BA_FLT_RLR", PLCTYPE_BOOL, 2),
	("BMS_BA_RLR", PLCTYPE_BOOL, 2),
	("BMS_BA_ACC_FLG_RLR", PLCTYPE_BOOL, 2),
	("BMS_WS_TRIG", PLCTYPE_INT, 1),
	("BMS_WS_ID", PLCTYPE_STRING, 1, 11),
	("BMS_WS_BL_CNT", PLCTYPE_REAL, 1),
	("BMS_WS_BL_SPD", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_SPD_AVG", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_SPD_DIF", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_LAM_SPD_DIF", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_LAM_SPD_AVG", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_SPD_DEC_TIM_DIF", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_LAM_SPD_DIF_PCT", PLCTYPE_REAL, 1),
	("BMS_WS_RLR_SPD_DEC_DIF_PCT", PLCTYPE_REAL, 1),
	("BMS_WS_TRK_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_SLP_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_ACC_TIM_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_ACC_SLP_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_DEC_TIM_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_SPD_DEC_SLP_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_LAM_TIM_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_LAM_SPD_RLR", PLCTYPE_REAL, 2),
	("BMS_WS_HIST_LAM_SPD_RLR", PLCTYPE_REAL, 2),
	("BMS_BS_BMS_ACT", PLCTYPE_BOOL, 1),
	("BMS_BS_SEM_RED", PLCTYPE_BOOL, 1),
	("BMS_BS_SEM_YEL", PLCTYPE_BOOL, 1),
	("BMS_BS_SEM_GRN", PLCTYPE_BOOL, 1),
	("BMS_BS_SPD_ON_RLR", PLCTYPE_BOOL, 2),
	("BMS_BS_HIGH_SPD_ON_RLR", PLCTYPE_BOOL, 2),
	("BMS_BS_SNS_ON_RLR", PLCTYPE_BOOL, 2),
)


# WSG: output as dictionary
# wsg_devices_names = ["WSG20", "WSG22", "WSG24", "WSG26", "WSG28"]
# bms_devices_names = ["BMS20", "BMS22", "BMS24", "BMS26", "BMS28"]

wsg_devices_names = ["WSG20"]
bms_devices_names = ["BMS20"]
#
points = []

async def plc_read(plc_read_period):
    global props, plc
    
    while True:
        start_time = time.time()

	    # WSG 
        wsg_devices_list = []
        for wsg_device_name in wsg_devices_names:
            # device_address = "IoT_MAIN." + wsg_device_name + ".stWsgInfluxdb"
            structure_data_wsg_dict = plc.read_structure_by_name("IoT_MAIN." + wsg_device_name + ".stWsgInfluxdb", wsg_structure_defin)
            wsg_devices_list.append((wsg_device_name, list(structure_data_wsg_dict.items())))    
        # BMS  
        bms_devices_list = []
        for bms_device_name in bms_devices_names:
            structure_data_bms_dict = plc.read_structure_by_name("IoT_MAIN." + bms_device_name + ".stBmsInfluxdb", bms_structure_defin)
            bms_devices_list.append((bms_device_name, list(structure_data_bms_dict.items()))) 
            
        timestamp_ns = int(time.time() * 1e9) % 9223372036854775806


		# WSG 
        for wsg_device in wsg_devices_list:
            wsg_device_name = str(wsg_device[0])
            for tuple in wsg_device[1]:
                if (type(tuple[1]) == list):
                    for (index, single_data) in enumerate(tuple[1]):
                        points.append(Point(props["influx"]["measurement"]).tag("WSG Device Number", wsg_device_name)
					.field(str(tuple[0]) + str(index), single_data)
					.time(timestamp_ns, WritePrecision.NS) )
                else:
                    points.append(Point(props["influx"]["measurement"]).tag("WSG Device Number", wsg_device_name)
					.field(str(tuple[0]), tuple[1])
					.time(timestamp_ns, WritePrecision.NS) )
        
		# BMS
        for bms_device in bms_devices_list:
            bms_device_name = str(bms_device[0])
            for tuple in bms_device[1]:
                if (type(tuple[1]) == list):
                    for (index, single_data) in enumerate(tuple[1]):
                        points.append(Point(props["influx"]["measurement"]).tag("BMS Device Number", bms_device_name)
										.field(str(tuple[0]) + str(index), single_data)
										.time(timestamp_ns, WritePrecision.NS) )
                else:
                    points.append(Point(props["influx"]["measurement"]).tag("BMS Device Number", bms_device_name)
									.field(str(tuple[0]), tuple[1])
									.time(timestamp_ns, WritePrecision.NS) )


            
        end_time = time.time()                    
        reference_time = end_time - start_time 
        print("[PLC Reading Data] (points length) {}, in;        {:.5f} [s]" \
                                            .format(len(points), reference_time))
        # sleep and wait for the others asyncio functions
        await asyncio.sleep(plc_read_period) 
        

# write_influxdb_pressPLCTYPE_RealTime coroutine
async def write_local_influxdb(influxdb_write_period):          
    # print("[write pressPLCTYPE_RealTime_recipe coroutine starting .... ]")       
    global write_local_api, influx_bucket, props, influx_organization, points
    try: 
        while True:
            await asyncio.sleep(influxdb_write_period)  
            start_time = time.time()  
            
            # Scrivi i dati nel bucket
            write_local_api.write(bucket = influx_bucket, org=influx_organization, record=points)  
            
            end_time = time.time()    
            reference_time = end_time - start_time   
            print(f"[Influx Writting Data] (points length)  {len(points)}, in:     {reference_time} [s]")  
            print("---------------------------------------------------------------------------------------------------------------------------------------------------")
            points = []              
    except:     
        pass            




async def main(plc_read_period, influxdb_write_period, enable_gzip_option):
    global write_local_api, influx_bucket, plc, props, influx_organization
    
    # Reading the set.json file 
    try:
        with open("set.json", "r") as file:
            props = json.load(file)
    except:
        print("set.json file was not read.")
        
    # Local InfluxDB connection
    influx_url = props["influx"]["url"]
    influx_token = props["influx"]["token"]
    influx_organization = props["influx"]["org"]
    influx_bucket = props["influx"]["bucket"]
    client_pc_amsNetId = props['plc']["amsNetID"]
    
    config = configparser.ConfigParser()
    config.read("config.ini") 
    
    # # Specify the path to influxd.exe
    influxd_path = config.get("Local InfluxDB", "INFLUXD_EXE_PATH").strip('"')  

    # Run influxd.exe in a new cmd.exe terminal
    subprocess.Popen(['cmd.exe', '/c', 'start', 'influxd.exe'], cwd=influxd_path, shell=True) 

    # Defining the python client for the plc  
	# connect to plc and open connection
    plc = pyads.Connection(client_pc_amsNetId, pyads.PORT_TC3PLC1)
    plc.open()

    # Create write to local InfluxDB API
    write_local_client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token,
                                                  org=influx_organization, enable_gzip = enable_gzip_option)  
    write_local_api = write_local_client.write_api()
    
    # Defining Asynchromous Processing Strcture  
    await asyncio.gather(
        plc_read(plc_read_period),
        write_local_influxdb(influxdb_write_period) 
        )
    
	# close the plc connection
    plc.close()



if __name__ == "__main__": 
    plc_read_period_time = 0.005   # seconds  
    influxdb_write_period_time = 0.01   # seconds.  
    enable_client_gzip_option = True      
    asyncio.run(main(plc_read_period = plc_read_period_time, influxdb_write_period = influxdb_write_period_time, enable_gzip_option = enable_client_gzip_option))
