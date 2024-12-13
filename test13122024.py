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
from ctypes import Structure, c_float
import pyads.errorcodes 

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


str_1 = (("fActualPosRight", PLCTYPE_REAL, 1),
		("fActualPosLeft", PLCTYPE_REAL, 1)
		)


str_2 = ((
  	("fRightCellRatedOutput", PLCTYPE_REAL, 1),
	("fRightCellZeroBalance", PLCTYPE_REAL, 1),
	("fLeftCellRatedOutput", PLCTYPE_REAL, 1),
	("fLeftCellZeroBalance", PLCTYPE_REAL, 1)
))


# Define the structure in Python to match the TwinCAT PLC structure
class ST_CellData(Structure):
    _pack_ = 1  # Matches the 'pack_mode' attribute in TwinCAT
    _fields_ = [
        ("fRightCellRatedOutput", c_float),
        ("fRightCellZeroBalance", c_float),
        ("fLeftCellRatedOutput", c_float),
        ("fLeftCellZeroBalance", c_float),
    ]
ST_CellData_Array = ST_CellData * 30



# Read Function
def plc_read():

	position_conf = configparser.ConfigParser()
	localCell_conf = configparser.ConfigParser()

    
	try: 
		# Defining the python client for the plc  
		# connect to plc and open connection
		plc = pyads.Connection("192.168.92.11.1.1", pyads.PORT_TC3PLC1)
		plc.open()

		# # Getting the state of the PLC Connection
		# state = plc.read_state()
		# print(state)
			
		# # Getting all accesible symobols (variables) from the software in the plc
		# symbols = plc.get_all_symbols()
		# for symbol in symbols:
		# 	print(symbol)

		while True:  

			start_time = time.time()

			# Checking Triggers Status
			read_position = plc.read_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.bMoveAxis")
			read_localCell= plc.read_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.bWriteNewCellValues")    
			write_store_trigger = None
			print("read Trigger Position: ", read_position)
			print("read Trigger LocalCell: ", read_localCell)


			# Storing position data
			if read_position != True:
				# reading to-be-saved-data
				position_data_dict = plc.read_structure_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.stWsg", str_1)  
				# Add sections and key-value pairs
				position_conf['Actual Positions (Left and Right)'] = position_data_dict
				# Write the configuration to a file
				with open('position_data.ini', 'w') as configfile:
					position_conf.write(configfile)

			# Storing local cell data
			if read_localCell != True:
				# Reading the index of array to be read
				index_cell = plc.read_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.stMemoryData.nCellDataIndex",  pyads.PLCTYPE_INT)
				print("INDEX CELL: ", index_cell)

				# Read cell data array:  ARRAY_1..30_OF-ST_CellData
				cell_lists = plc.read_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.stCellData", ST_CellData_Array)
				print("Lenght:  ", len(cell_lists))

				# Access and print each cell's data
				for i, cell_data in enumerate(cell_lists):
					print(f"Cell {i+1}:")
					print(f"  Right Cell Rated Output: {cell_data.fRightCellRatedOutput}")
					print(f"  Right Cell Zero Balance: {cell_data.fRightCellZeroBalance}")
					print(f"  Left Cell Rated Output: {cell_data.fLeftCellRatedOutput}")
					print(f"  Left Cell Zero Balance: {cell_data.fLeftCellZeroBalance}")

				localCell_data_dict =  { "fRightCellRatedOutput": cell_lists[index_cell - 1].fRightCellRatedOutput ,
								"fRightCellZeroBalance": cell_lists[index_cell - 1].fRightCellZeroBalance,
								"fLeftCellRatedOutput": cell_lists[index_cell - 1].fLeftCellRatedOutput,
								"fLeftCellZeroBalance": cell_lists[index_cell - 1].fLeftCellZeroBalance
								}
				print(localCell_data_dict)
				
				
				# Add sections and key-value pairs
				localCell_conf['Load Cell Index'] = {"Index": index_cell}
				localCell_conf['Load Cell Data'] = localCell_data_dict
				# Write the configuration to a file
				with open('loadCell_data.ini', 'w') as configfile:
					localCell_conf.write(configfile)


			# Writting Data
			if write_store_trigger == True:
				# # plc.write_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.bWriteNewCellValues",  False)  
				# plc.write_by_name("PlcMain.fbSystemRoot.fbWsgWorkShop.bWriteNewCellValues",  not data, pyads.PLCTYPE_BOOL)
				# print("Successfully wrote to PLC!")	
				pass

			end_time = time.time()
			print("Reference Time is: {:.3f}".format(end_time - start_time))
			print("-------------------------------------------------------------------------------------------------")

	except pyads.pyads_ex.ADSError as e:
		print(e)

	finally:
		# close the plc connection
		plc.close()
	
if __name__ == "__main__": 
    plc_read()





# # #######################################################################################
# import pyads
# from ctypes import Structure, c_float

# # Define the structure in Python to match the TwinCAT PLC structure
# class ST_CellData(Structure):
#     _pack_ = 1  # Matches the 'pack_mode' attribute in TwinCAT
#     _fields_ = [
#         ("fRightCellRatedOutput", c_float),
#         ("fRightCellZeroBalance", c_float),
#         ("fLeftCellRatedOutput", c_float),
#         ("fLeftCellZeroBalance", c_float),
#     ]

# # Establish connection to the PLC
# plc = pyads.Connection('192.168.0.1.1.1', 851)  # Replace AMS ID and port with actual values

# try:
#     plc.open()
#     # Define the full array type in Python
#     num_cells = 30  # Adjust based on your TwinCAT array size
#     ST_CellData_Array = ST_CellData * num_cells

#     # Read the array from the PLC
#     array_name = "MAIN.stCellData"  # Replace with the actual variable path in your PLC
#     cell_lists = plc.read_by_name(array_name, ST_CellData_Array)

#     # Access and print each cell's data
#     for i, cell_data in enumerate(cell_lists):
#         print(f"Cell {i+1}:")
#         print(f"  Right Cell Rated Output: {cell_data.fRightCellRatedOutput}")
#         print(f"  Right Cell Zero Balance: {cell_data.fRightCellZeroBalance}")
#         print(f"  Left Cell Rated Output: {cell_data.fLeftCellRatedOutput}")
#         print(f"  Left Cell Zero Balance: {cell_data.fLeftCellZeroBalance}")
# finally:
#     plc.close()
