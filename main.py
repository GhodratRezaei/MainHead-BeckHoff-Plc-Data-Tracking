import pyads
import struct
import json
import influxdb_client 
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision  
import asyncio  
import subprocess
import time



# import pyads

# # connect to plc and open connection
# plc = pyads.Connection('127.0.0.1.1.1', pyads.PORT_TC3PLC1)
# plc.open()

# # read int value by name
# i = plc.read_by_name("GVL.int_val")

# # write int value by name
# plc.write_by_name("GVL.int_val", i)

# # close connection
# plc.close()




TYPE ST_WSG_Connected :
STRUCT
	
	bWSG_BC_RH_AUT_ADJ_ENAB: PLCTYPE_BOOL;
	nWSG_WC_RH_ADJ_STEP: PLCTYPE_DINT;
	fWSG_WC_RH_AUT_ADJ_DB: PLCTYPE_REAL;
	nWSG_WC_RH_INIT_GAP: PLCTYPE_DINT;
	fWSG_WC_RLR_CAV_DPTH: PLCTYPE_REAL;
	fWSG_WC_RH_ENC_PLS: PLCTYPE_REAL;
	fWSG_WC_RH_MOT_RATIO: PLCTYPE_REAL;
	fWSG_WC_RH_SCW_RATIO: PLCTYPE_REAL;
	arrWSG_WC_POS_SET_RH: ARRAY[1..2] OF PLCTYPE_DINT;
	
	sWSG_MEM_WR_ID: PLCTYPE_STRING(12);
	fWSG_MEM_WR_RLR_DIAM: PLCTYPE_REAL;
	nWSG_MEM_WR_RH_INIT_GAP: PLCTYPE_DINT;
	nWSG_MEM_WR_CNT: PLCTYPE_INT;
	sWSG_MEM_WR_DAN_ID: PLCTYPE_STRING(12);
	nWSG_MEM_WR_STRK_RH1: PLCTYPE_DINT;
	nWSG_MEM_WR_STRK_RH2: PLCTYPE_DINT;
	nWSG_MEM_WR_POS_RH1: PLCTYPE_DINT;
	nWSG_MEM_WR_POS_RH2: PLCTYPE_DINT;

END_STRUCT
END_TYPE





structure_def = [

   	bWSG_BC_RH_AUT_ADJ_ENAB: PLCTYPE_BOOL;
	nWSG_WC_RH_ADJ_STEP: PLCTYPE_DINT;
	fWSG_WC_RH_AUT_ADJ_DB: PLCTYPE_REAL;
	nWSG_WC_RH_INIT_GAP: PLCTYPE_DINT;
	fWSG_WC_RLR_CAV_DPTH: PLCTYPE_REAL;
	fWSG_WC_RH_ENC_PLS: PLCTYPE_REAL;
	fWSG_WC_RH_MOT_RATIO: PLCTYPE_REAL;
	fWSG_WC_RH_SCW_RATIO: PLCTYPE_REAL;
	arrWSG_WC_POS_SET_RH: ARRAY[1..2] OF PLCTYPE_DINT;
	
	sWSG_MEM_WR_ID: PLCTYPE_STRING(12);
	fWSG_MEM_WR_RLR_DIAM: PLCTYPE_REAL;
	nWSG_MEM_WR_RH_INIT_GAP: PLCTYPE_DINT;
	nWSG_MEM_WR_CNT: PLCTYPE_INT;
	sWSG_MEM_WR_DAN_ID: PLCTYPE_STRING(12);
	nWSG_MEM_WR_STRK_RH1: PLCTYPE_DINT;
	nWSG_MEM_WR_STRK_RH2: PLCTYPE_DINT;
	nWSG_MEM_WR_POS_RH1: PLCTYPE_DINT;
	nWSG_MEM_WR_POS_RH2: PLCTYPE_DINT; 

]





points = []

async def plc_read(plc_read_period):
    global props, plc, db_number

    while True:
        start_time = time.time()
        
        # PLCTYPE_Real
        PLCTYPE_real_bytes_length = props['plc']['stop'] - props['plc']['start']
        PLCTYPE_real_area_data_bytearray = plc.read_area(Areas.DB, props['plc']['dbnumber'], props['plc']['start'],  PLCTYPE_real_bytes_length)
        PLCTYPE_real_byte_count = int(PLCTYPE_real_bytes_length / 4)
        prt_PLCTYPE_real = struct.unpack(">f" + " f " * (PLCTYPE_real_byte_count - 1), PLCTYPE_real_area_data_bytearray)  # Big_Endian (>i)

        PLCTYPE_real_values_list = list(prt_PLCTYPE_real)
        
        timestamp_ns = int(time.time() * 1e9) % 9223372036854775806
        for i in range(len(props["tags"]["Zone"])): 
            points.append(Point(props["influx"]["measurement"]).tag(props["tags"]["Zone"][i][0], props["tags"]["Zone"][i][1])
                                        .tag(props["tags"]["Unit"][i][0], props["tags"]["Unit"][i][1])
                                        .field(str(props["fields_names"][i]), PLCTYPE_real_values_list[i])
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
    global write_local_api, influx_bucket, plc, db_number, props, influx_organization
    
    
    # Reading the set.json file 
    try:
        with open("/app/PLC/set.json", "r") as file:
            props = json.load(file)
    except:
        print("set.json file was not read.")
        
    # Local InfluxDB connection
    influx_url = props["influx"]["url"]
    influx_token = props["influx"]["token"]
    influx_organization = props["influx"]["org"]
    influx_bucket = props["influx"]["bucket"]
    
    # Defining the python client for the plc        
    plc = snap7.client.Client()
    plc.connect(props['plc']['ip_address'], props['plc']['rack_number'], props['plc']['slot_number'])
    
    # Create write to local InfluxDB API
    write_local_client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token,
                                                  org=influx_organization, enable_gzip = enable_gzip_option)  
    write_local_api = write_local_client.write_api()
    
    # Defining Asynchromous Processing Strcture  
    await asyncio.gather(
        plc_read(plc_read_period),
        write_local_influxdb(influxdb_write_period) 
        )
    plc.disconnect()
    
    
if __name__ == "__main__": 
    plc_read_period_time = 0.005   # seconds  
    influxdb_write_period_time = 0.01   # seconds.  
    enable_client_gzip_option = True        
    asyncio.run(main(plc_read_period = plc_read_period_time, influxdb_write_period = influxdb_write_period_time, enable_gzip_option = enable_client_gzip_option ))
