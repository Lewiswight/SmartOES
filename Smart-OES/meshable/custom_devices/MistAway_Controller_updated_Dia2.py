# MistAway Core Driver

import os
from common.helpers.format_channels import iso_date
import types
import traceback
import binascii
import threading
# imports
import struct
import thread
from rci import process_request
from devices.device_base import DeviceBase
from devices.xbee.xbee_devices.xbee_base import XBeeBase
from devices.xbee.xbee_devices.xbee_serial import XBeeSerial
from settings.settings_base import SettingsBase, Setting
from channels.channel_source_device_property import *

from devices.xbee.common.prodid import parse_dd
from common.types.boolean import Boolean, STYLE_ONOFF
from devices.xbee.xbee_config_blocks.xbee_config_block_ddo \
    import XBeeConfigBlockDDO
from devices.xbee.xbee_device_manager.xbee_device_manager_event_specs \
    import *
from devices.xbee.common.addressing import *
from devices.xbee.common.prodid import  MISTAWAY_CONTROLLER_MC3, MISTAWAY_CONTROLLER_MC3Z, MISTAWAY_CONTROLLER_MC1, MISTAWAY_CONTROLLER_MC1Z, MISTAWAY_CONTROLLER_MC3D




from time import time as get_time
from time import strftime
from time import localtime
import time 
from common.abstract_service_manager import AbstractServiceManager

from core.tracing import get_tracer
#from custom_presentations.presentations.idigi_db.idigi_dbM import iDigi_DB

import Queue





# constants
TABLE = (
		0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
		0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
		0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
		0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
		0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
		0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
		0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
		0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
		0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
		0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
		0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
		0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
		0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
		0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
		0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
		0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
		0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
		0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
		0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
		0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
		0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
		0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
		0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
		0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
		0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
		0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
		0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
		0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
		0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
		0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
		0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
		0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )
# exception classes

# interface setions

# classes


class queue_runner(threading.Thread):
    """Threaded Queue runner for testing things"""
    def __init__(self, my_queue, mc):      
        threading.Thread.__init__(self)           
        self.my_queue = my_queue        
        self.mc = mc
                                                  
    def run(self):                                
        print "the Queue has been started!"                     
    
        while True:
    
            msg = self.my_queue.get()
            self.mc.send_data(msg)
            time.sleep(1)
            
            
            







class f_counter:

      
    def __init__(self, time):
        self.time = time
        
    def timeout(self):
        
        while self.time_o > 1:
            self.time_o -= 1
            time.sleep(.1)
            
        if self.line == 200:
            print "update success"
        else:
            print "restarting, device timed out"
            self.firm_update("a", 1)
    



class XBeeSerialTerminal(XBeeSerial):
    """\
        This class extends one of our base classes and is intended as an
        example of a concrete, example implementation, but it is not itself
        meant to be included as part of our developer API. Please consult the
        base class documentation for the API and the source code for this file
        for an example implementation.

    """
    
    
    

    
 
    
			
    ADDRESS_TABLE = [ [0xe8, 0xc105, 0x92], [0xe8, 0xc105, 0x11] ]
    
    SUPPORTED_PRODUCTS = [ MISTAWAY_CONTROLLER_MC3, MISTAWAY_CONTROLLER_MC3Z, MISTAWAY_CONTROLLER_MC1, MISTAWAY_CONTROLLER_MC1Z, MISTAWAY_CONTROLLER_MC3D, ]
    
    def __init__(self, name, core_services):
        
        if name.startswith("mc3"):
            self.sys_type = 3
        else:
            self.sys_type = 1
        print "system type is going to be:" 
        print self.sys_type
        self.myName = name
        self.__name = name
        self.__core = core_services
        self.__event_timer2 = None
        self.__event_timer3 = None
        self.__event_timer_sig = None
        self.__event_timer_check = None
        self.event_timer_status = None
        self.fwu = 0
        self.m_mode = 0 # 0 = not misting, 1=user initiated, 2=user cancelled, 3=success
        self.list = 0
        self.__tracer = get_tracer(name)
        self.full_update = False
		

        ## Local State Variables:
        self.listen = True
        self._count = 0
        self.__xbee_manager = None
        self.update_timer = None
        self.modes = {"O":0, "H":1, "C":2, "A":3}
        self.count = 0
        self.retry_count = 0
        self.filename = None
        self.error = ""
        self.data = None
        self.file = None
        self.time_o = 0
        self.line = 0
        self.retry = 0
        self.push_all_settings = 0
        self.send_data_to_meshify = 0
        self.send_all_data_to_meshify = 0
        self.status_checking = False
        
        self.queue = Queue.Queue(maxsize=50)
        
        self.getting_all_values = 0 # true or false for if I'm looking for an r=6 return
        
        self.current = None

        ## Settings Table Definition:
        settings_list = [
            Setting(
                name='xbee_device_manager', type=str, required=True),
            Setting(
                name='compact_xml', type=bool, required=False, default_value=False),
            Setting(
                name="channels", type=list, required=False, default_value=[]),
            Setting(
                name='extended_address', type=str, required=True),
            Setting(
                name='sample_rate_sec', type=int, required=False,
                default_value=300),
        ]

        ## Channel Properties Definition:
        property_list = [
			
            #gettable only channles:
            
             ChannelSourceDeviceProperty(name="FOP1", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
             
             ChannelSourceDeviceProperty(name="FOP2", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
             
             ChannelSourceDeviceProperty(name="VER", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
                         
                         #mist away firmware version
             
             ChannelSourceDeviceProperty(name="GWF", type=str,
                initial=Sample(timestamp=time.time() + 30, unit="", value="2013-06-22 Dev 1"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
                         
                         #gateway firmware
             
             
             ChannelSourceDeviceProperty(name="last_com", type=str,
                initial=Sample(timestamp=time.time(), unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
             
             #last com from controller
             
             ChannelSourceDeviceProperty(name="CL0", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C1"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL1", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C2"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL2", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C3"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL3", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C4"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL4", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C5"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL5", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C6"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL6", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C7"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL7", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C8"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
             
            ChannelSourceDeviceProperty(name="CL8", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C9"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL9", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C10"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL10", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C11"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL11", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C12"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL12", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C13"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL13", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C14"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL14", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C15"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL15", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C16"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL16", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C17"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL17", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C18"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL18", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C19"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL19", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C20"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL20", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C21"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL21", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C22"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL22", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C23"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="CL23", type=str,
                initial=Sample(timestamp=time.time(), unit="", value="C24"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            			 
			
			ChannelSourceDeviceProperty(name="LF", type=str,
                initial=Sample(timestamp=0, unit="1", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
                         
            #Last Fill, this will be that last time the LVL goes up, not down.
            
            
			ChannelSourceDeviceProperty(name="LM", type=str,
                initial=Sample(timestamp=0, unit="1", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Last Mist, will be set every time SS=Mist
			
			ChannelSourceDeviceProperty(name="LSC", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
			
			#Last setting changed, send only a timestamp
			
			
			ChannelSourceDeviceProperty(name="PR", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
			
			# percent remaining in percent	
			
			ChannelSourceDeviceProperty(name="NSM", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# Next scheduled mist (today or tomorrow)
			
					
			
			ChannelSourceDeviceProperty(name="DM", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# seconds misted since midnight
			
			ChannelSourceDeviceProperty(name="TMH", type=str,
                initial=Sample(timestamp=0, unit="sec2hour", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
			
			ChannelSourceDeviceProperty(name="PRH", type=str,
                initial=Sample(timestamp=0, unit="tensec2hour", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# Dosing Pump Run Hours (might be in seconds**
			
			ChannelSourceDeviceProperty(name="SPD", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# Current Wind Speed
			
			ChannelSourceDeviceProperty(name="FL", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Volume (mL) of Last Mist
			
			
            
            ChannelSourceDeviceProperty(name="AF2", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            
            ChannelSourceDeviceProperty(name="AF1", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# Acutal Average Flow Rate Per Nozzle Last Mist
			
			ChannelSourceDeviceProperty(name="TF", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Target Mist Volume 
			
			
			ChannelSourceDeviceProperty(name="CF", type=str,
                initial=Sample(timestamp=0, unit="tenths2ml", value="0"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Cartridge Full Volume, mL
			
			ChannelSourceDeviceProperty(name="CR", type=str,
                initial=Sample(timestamp=0, unit="tenths2ml", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Cartridge Remaining Volume
			
			ChannelSourceDeviceProperty(name="DS", type=str,
                initial=Sample(timestamp=0, unit="tenths2ml", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Dose Volume of Last Mist
			
			ChannelSourceDeviceProperty(name="DUE", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			# Gen 3 Only Days Until Empty Hidden for now, in the future this will be a dirived channel on the server
			
			
			ChannelSourceDeviceProperty(name="st", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#placeholder for lowercast st, needs to be removed and cleaned up at some point
			
			ChannelSourceDeviceProperty(name="stat", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Status **not working** should return error codes
			
			ChannelSourceDeviceProperty(name="ST", type=str,
                initial=Sample(timestamp=0, unit="ST", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#System type, return 1 or 3, convert Gen 1.3 or Gen 3+
			
			ChannelSourceDeviceProperty(name="SS", type=str,
                initial=Sample(timestamp=0, unit="SS2code", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#System Status **we are working on this right now
			
			ChannelSourceDeviceProperty(name="CFV", type=str,
                initial=Sample(timestamp=0, unit="tenths2ml", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Cartridge Full Volume
			
			ChannelSourceDeviceProperty(name="LD", type=str,
                initial=Sample(timestamp=0, unit="LD", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
                         
            # Leak detection returns is there no float swtich, this value just needs to be inverted so 1 turns to 0 and 0 turns to 1
			
			ChannelSourceDeviceProperty(name="FS", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
			
			ChannelSourceDeviceProperty(name="ZK", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
						
			#Zone Kit, right now 0/1 needs to return a Bool print str(bool(1))
			
			
											
						
			# settable channels:
			
			
            ChannelSourceDeviceProperty(name="ping", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.__get_signal("ping", x)),
                         
            
            ChannelSourceDeviceProperty(name="TMC", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("TMC", x)),
						
			#Total Mist Cycles
			
			ChannelSourceDeviceProperty(name="TMM", type=str,
                initial=Sample(timestamp=0, unit="sec2min", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_sec2min("TMM", x)),
						
			#Total Mist Minutes, right now it comes out in Seconds, change to minutes
						 
			ChannelSourceDeviceProperty(name="MMC", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MMC", x)),			 
						 
			#Manual Mist Cycles
						 
			ChannelSourceDeviceProperty(name="RMC", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("RMC", x)),
						
			#Remote Mist Cycles
						
			ChannelSourceDeviceProperty(name="NFR", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("NFR", x)),	
						
			#Target Flow Rate Per Nozzle			
					 
						
			ChannelSourceDeviceProperty(name="TOL", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("TOL", x)),
						
			#Tolerance Level for Leak Detection
						 
			ChannelSourceDeviceProperty(name="J", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("J", x)),			 
						 
						 
			#Bellows Pump Dose Rate
						 
			ChannelSourceDeviceProperty(name="K", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("K", x)),
						
			#Max Mist Duration
						
			ChannelSourceDeviceProperty(name="L", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("L", x)),
						
			#Flow Meter Pulses Per Gallon
						
			ChannelSourceDeviceProperty(name="Hld", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("Hld", x)),
						
			#Depressurize Duration Following Mist
						
			ChannelSourceDeviceProperty(name="DST", type=str,
                initial=Sample(timestamp=0, unit="", value="1"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_dst("DST", x)),	
						
			#Daylight Savings Time Switch
			
			ChannelSourceDeviceProperty(name="DOW", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("DOW", x)),
						
			#Current Time Day Of Week
						 
			ChannelSourceDeviceProperty(name="TOD", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("TOD", x)),	
						
			#Current Time of Day		 
			
			
		#CT0-23 are the durations for the schedules CY0-23
			
			ChannelSourceDeviceProperty(name="CT0", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT0", x)),			 
			
			ChannelSourceDeviceProperty(name="CT1", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT1", x)),
			
			ChannelSourceDeviceProperty(name="CT2", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT2", x)),
			
			
			ChannelSourceDeviceProperty(name="CT3", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT3", x)),
			
			ChannelSourceDeviceProperty(name="CT4", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT4", x)),
			
			
			ChannelSourceDeviceProperty(name="CT5", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT5", x)),			 
			
			ChannelSourceDeviceProperty(name="CT6", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT6", x)),
			
			ChannelSourceDeviceProperty(name="CT7", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT7", x)),
			
			
			ChannelSourceDeviceProperty(name="CT8", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT8", x)),
			
			ChannelSourceDeviceProperty(name="CT9", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT9", x)),			 
			
			ChannelSourceDeviceProperty(name="CT10", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT10", x)),
			
			ChannelSourceDeviceProperty(name="CT11", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT11", x)),
			
			
			ChannelSourceDeviceProperty(name="CT12", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT12", x)),
			
			ChannelSourceDeviceProperty(name="CT13", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT13", x)),
			
			
			ChannelSourceDeviceProperty(name="CT14", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT14", x)),			 
			
			ChannelSourceDeviceProperty(name="CT15", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT15", x)),
			
			ChannelSourceDeviceProperty(name="CT16", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT16", x)),
			
			
			ChannelSourceDeviceProperty(name="CT17", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT17", x)),
			
			ChannelSourceDeviceProperty(name="CT18", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT18", x)),
			
			
			ChannelSourceDeviceProperty(name="CT19", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT19", x)),			 
			
			ChannelSourceDeviceProperty(name="CT20", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT20", x)),
			
			ChannelSourceDeviceProperty(name="CT21", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT21", x)),
			
			
			ChannelSourceDeviceProperty(name="CT22", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT22", x)),
			
			ChannelSourceDeviceProperty(name="CT23", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_cycle("CT23", x)),
						
			
		# CY0-23 are the Time of Day for the schedules 1-24
		# All CY values need to be converted to a time before being sent to the server	
		
			ChannelSourceDeviceProperty(name="CY0", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY0", x)),	
			
			ChannelSourceDeviceProperty(name="CY1", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY1", x)),	
			
			ChannelSourceDeviceProperty(name="CY2", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY2", x)),	
			
			ChannelSourceDeviceProperty(name="CY3", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY3", x)),	
			
			ChannelSourceDeviceProperty(name="CY4", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY4", x)),	
			
			ChannelSourceDeviceProperty(name="CY5", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY5", x)),
						
			ChannelSourceDeviceProperty(name="CY6", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY6", x)),	
			
			ChannelSourceDeviceProperty(name="CY7", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY7", x)),	
			
			ChannelSourceDeviceProperty(name="CY8", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY8", x)),	
			
			ChannelSourceDeviceProperty(name="CY9", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY9", x)),	
			
			ChannelSourceDeviceProperty(name="CY10", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY10", x)),	
			
			ChannelSourceDeviceProperty(name="CY11", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY11", x)),
			
			ChannelSourceDeviceProperty(name="CY12", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY12", x)),	
			
			ChannelSourceDeviceProperty(name="CY13", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY13", x)),	
			
			ChannelSourceDeviceProperty(name="CY14", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY14", x)),	
			
			ChannelSourceDeviceProperty(name="CY15", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY15", x)),	
			
			ChannelSourceDeviceProperty(name="CY16", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY16", x)),	
			
			ChannelSourceDeviceProperty(name="CY17", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY17", x)),
						
			ChannelSourceDeviceProperty(name="CY18", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY18", x)),	
			
			ChannelSourceDeviceProperty(name="CY19", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY19", x)),	
			
			ChannelSourceDeviceProperty(name="CY20", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY20", x)),	
			
			ChannelSourceDeviceProperty(name="CY21", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY21", x)),	
			
			ChannelSourceDeviceProperty(name="CY22", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY22", x)),	
			
			ChannelSourceDeviceProperty(name="CY23", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("CY23", x)),
			
		#CD 1- 7 are the custom days, they can be on/off which will stay 0/1 for now because dane made a mapper for those values
		#Sunday is 1 and Saturday is 7
			
			ChannelSourceDeviceProperty(name="CD1", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD1", x)),
						 
			ChannelSourceDeviceProperty(name="CD2", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD2", x)),			 
						 
			ChannelSourceDeviceProperty(name="CD3", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD3", x)),
						
			ChannelSourceDeviceProperty(name="CD4", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD4", x)),
						
			ChannelSourceDeviceProperty(name="CD5", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD5", x)),
						
			ChannelSourceDeviceProperty(name="CD6", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD6", x)),
			
			ChannelSourceDeviceProperty(name="CD7", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("CD7", x)),
						 
			ChannelSourceDeviceProperty(name="REM", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("REM", x)),
						
				#Remote Mist Duration			 
						 
			ChannelSourceDeviceProperty(name="RMZ", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("RMZ", x)),
						
				#
						
			ChannelSourceDeviceProperty(name="MAN", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MAN", x)),			 
						
			ChannelSourceDeviceProperty(name="MNZ", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MNZ", x)),
						 
			ChannelSourceDeviceProperty(name="ZNC", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ZNC", x)),			 
						 
			ChannelSourceDeviceProperty(name="NOZ", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("NOZ", x)),
						
			ChannelSourceDeviceProperty(name="NZ1", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("NZ1", x)),
						
			ChannelSourceDeviceProperty(name="NZ2", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("NZ2", x)),
						
			ChannelSourceDeviceProperty(name="AGTT", type=str,
                initial=Sample(timestamp=0, unit="sec2time", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_time("AGTT", x)),
						
			#agitation time of dat
			
			
			ChannelSourceDeviceProperty(name="AGTD", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("AGTD", x)),
						
			#agitation duration
						 
			ChannelSourceDeviceProperty(name="RAG", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("RAG", x)),	
						
			# remote agitation duration		 
						 
			ChannelSourceDeviceProperty(name="TNK", type=str,
                initial=Sample(timestamp=0, unit="", value="0"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("TNK", x)),
						
			# Gen 1.3 only** Tank Size (Gen 1.3) is in gallons done is gallons both ways, so it wont need to be changed
						
			ChannelSourceDeviceProperty(name="SEN", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("SEN", x)),			 
						
			ChannelSourceDeviceProperty(name="WND", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("WND", x)),
						 
			ChannelSourceDeviceProperty(name="ALT", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET), 
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ALT", x)),			 
						 
			ChannelSourceDeviceProperty(name="ER0", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ER0", x)),
						
			ChannelSourceDeviceProperty(name="ER2", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ER2", x)),
						
			ChannelSourceDeviceProperty(name="ER3", type=str,     
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ER3", x)),
						
			ChannelSourceDeviceProperty(name="ER6", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("ER6", x)),
			
			ChannelSourceDeviceProperty(name="FM", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("FM", x)),
						
			#Flow Meter Type LD: brs/PLS 0/1 is what I'm getting, Dane took care of this, so just pass it along
						 
			ChannelSourceDeviceProperty(name="VL", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("VL", x)),
						
			#ml returned from the flow meter test
			
			
			ChannelSourceDeviceProperty(name="LVL", type=str,
                initial=Sample(timestamp=0, unit="LVL", value="100"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_lvl("LVL", x)),
						
				# Level, will be set and got from the server as a percent. It is the % of BOT on Gen 3 and % of TNK on Gen 1.3
				#LVL is in 10/ml for gen 3 and ml for gen 1.3			 
						 
			ChannelSourceDeviceProperty(name="MIX", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MIX", x)),
						
			ChannelSourceDeviceProperty(name="BOT", type=str,
                initial=Sample(timestamp=0, unit="10ml2oz", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set_10ml2oz("BOT", x)),
						
			# Gen 3 only Bottle size Gets and sets in 10/ml Needs to be set and get in ounces.	 
						
			ChannelSourceDeviceProperty(name="FLT", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("FLT", x)),
						
			#Position of Float Switch
						 
			ChannelSourceDeviceProperty(name="MX", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MX", x)),			 
						 
			ChannelSourceDeviceProperty(name="MD", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.set("MD", x)),
						
			# System Mode 0 = Off 1 = Remote Only 2 = Auto Everyday 3 = Auto Custom
			
            

                         
                         
      
      # gettable properties
            
            
            
            
            ChannelSourceDeviceProperty(name="pause", type=float,
                initial=Sample(timestamp=0, unit="pause", value=.1),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.f_name("pause", x)),
            
            ChannelSourceDeviceProperty(name="block_size", type=int,
                initial=Sample(timestamp=0, unit="degF", value=10),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.f_name("block_size", x)),
            
            ChannelSourceDeviceProperty(name="file_name", type=str,
                initial=Sample(timestamp=0, unit="degF", value="output.txt"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.f_name("file_name", x)),
            
            
            ChannelSourceDeviceProperty(name="update_settings", type=Boolean,
                initial=Sample(timestamp=0,
                value=Boolean(False, style=STYLE_ONOFF)),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.replace_all_settings("update_settings", x)),
            
            
            ChannelSourceDeviceProperty(name="update_file", type=Boolean,
                initial=Sample(timestamp=0,
                value=Boolean(False, style=STYLE_ONOFF)),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.get_all_settings("update_file", x)),
            
            
            ChannelSourceDeviceProperty(name="fw_update", type=str,
                initial=Sample(timestamp=0, unit="", value="output.txt"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.firm_update("fw_update", x)),
            
            ChannelSourceDeviceProperty(name="signal", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="mc", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="pm", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="est", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="serialReceive", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="serialSend", type=str,
                initial=Sample(timestamp=0, unit="F", value=" "),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.serial_write("serialSend", x)),
            
            
            ChannelSourceDeviceProperty(name="g", type=str,
                initial=Sample(timestamp=0, unit="", value="not_set"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.get("g", x)),
            
            ChannelSourceDeviceProperty(name="r", type=str,
                initial=Sample(timestamp=0, unit="", value="not_set"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.new_update("r", x)),
            
            ChannelSourceDeviceProperty(name="cr", type=str,
                initial=Sample(timestamp=0, unit="", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
           #     set_cb=lambda x: self.set_sph("cartridge_remaining_volume", x)),
            
            ChannelSourceDeviceProperty(name="cfv", type=str,
                initial=Sample(timestamp=0, unit="F", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
        #        set_cb=lambda x: self.set_sph("cartridge_full_volume", x)),
            
            ChannelSourceDeviceProperty(name="line_number", type=int,
                initial=Sample(timestamp=0, unit="line", value=0),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="test", type=int,
                initial=Sample(timestamp=0, unit="T_O", value=0),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="crc", type=str,
                initial=Sample(timestamp=0, unit="F", value=""),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="error", type=str,
                initial=Sample(timestamp=0, unit="E", value=" "),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
        #        set_cb=lambda x: self.set_sph("crc", x)),
                
            
        ]

        ## Initialize the XBeeSerial interface:
        XBeeSerial.__init__(self, self.__name, self.__core,    
                                settings_list, property_list)


    
    
    @staticmethod
    def probe():
        
        probe_data = XBeeBase.probe()

        for address in XBeeSerialTerminal.ADDRESS_TABLE:
            probe_data['address_table'].append(address)
        for product in XBeeSerialTerminal.SUPPORTED_PRODUCTS:
            probe_data['supported_products'].append(product)

        return probe_data
       ## setions which must be implemented to conform to the XBeeSerial
    ## interface:
              
    
    
    def read_callback(self, buf):
        print buf
        self.serial_read(buf)


    ## setions which must be implemented to conform to the DeviceBase
    ## interface:

    def apply_settings(self):

        SettingsBase.merge_settings(self)
        accepted, rejected, not_found = SettingsBase.verify_settings(self)

        if len(rejected) or len(not_found):
            # there were problems with settings, terminate early:
            return (accepted, rejected, not_found)

        SettingsBase.commit_settings(self, accepted)

        return (accepted, rejected, not_found)

    def start(self):
    	
    	xbee_manager_name = SettingsBase.get_setting(self, "xbee_device_manager")
        dm = self.__core.get_service("device_driver_manager")
        self.__xbee_manager = dm.instance_get(xbee_manager_name)
    	
    	test = XBeeSerial.start(self)
    	
    	self._config_done_cb()

        return test

        

    def calcByte(self, ch, crc):
	    """Given a new Byte and previous CRC, Calc a new CRC-16"""
	    if type(ch) == type("c"): 
	        by = ord(ch)
	    else:
	        by = ch
	    crc = (crc >> 8) ^ TABLE[(crc ^ by) & 0xFF]
	    return (crc & 0xFFFF)
	 
    def calcString(self, st, crc):
	    """Given a bunary string and starting CRC, Calc a final CRC-16 """
	    for ch in st:
	        crc = (crc >> 8) ^ TABLE[(crc ^ ord(ch)) & 0xFF]
	    return crc  
    
    def __get_signal(self, register_name, val):
        val.timestamp = time.time()
        self.property_set(register_name, val)
        self.get_signal()
    
    def get_signal(self, send=True):
        
        if self.__event_timer_sig is not None:
            
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(self.__event_timer_sig)
            except:
                pass
            
        self.__event_timer_sig = self.__xbee_manager.xbee_device_schedule_after(3675, self.get_signal)
        
        try:
            i = 0
            extended_address = SettingsBase.get_setting(self, "extended_address")
            
            if self.fwu == 1:
                return
           
            #try: 
            
            try:
                
                path = '/WEB/python'
                file_list = [f for f in os.listdir(path) if f.endswith('.txt')]
                print file_list
            except:
                print "couldn't search flash for .txt files"
                
            """
            file_list = []
            os.chdir("/WEB/python")
            for files in os.listdir("."):
                if files.endswith(".txt"):
                    print files
                    file_list.append(files)"""
            try:        
                self.property_set("FOP1", Sample(time.time(), value=str(file_list[0]), unit=""))
            except:
                self.property_set("FOP1", Sample(time.time(), value="No File", unit=""))
                print "didn't find any files"
            try:
                self.property_set("FOP2", Sample(time.time(), value=str(file_list[1]), unit=""))
                
            except:
                self.property_set("FOP2", Sample(time.time(), value="No File", unit=""))
                print "didn't find second file"
            #except:
                #print "couldn't get files"
            
            id = None
            while i < 5:
                try:
                
                    db = self.__xbee_manager.xbee_device_ddo_get_param(extended_address, "DB", use_cache=True)
                    
                    
                    
                    
                    
                    #sv = self.__xbee_manager.xbee_device_ddo_get_param(extended_address, "%V", use_cache=True)
                    
                    
                    
                    try:
                        dd = struct.unpack(">B", db)
                    except:
                        i += 1
                        print "failed 1" 
                        continue    
                    
                    """try:
                        #dd = struct.unpack(">B", db)
                        pan = struct.unpack(">i", id)
                        print pan
                    except:
                        i += 1
                        print "failed 8" """ 
                    
                          
                    
                    #sv = struct.unpack(">H", sv)
                   # print sv
            
                    dd = str(dd)
                    dd = dd[1:3]
                    dd = dd
                    print "signal strength ="
                    print dd
                    self.property_set("signal", Sample(time.time(), value=str(dd), unit=""))
                    
                    
                    """sv = str(sv)
                    sv = sv[1:5]
                    sv = int(sv)
                    print sv
                    volts = (sv * 1.1719) / 1000
                    print "volts ="
                    print volts"""
                
        
                    i = 10
                    if send:
                        self.upload.upload_data()
                
                except:
                    i += 1
                    #self.property_set("signal", Sample(0, value="disconnected", unit=""))
                    print "failed to get signal and voltage"
                    continue
            
            if i == 5:
                self.property_set("signal", Sample(time.time(), value="0", unit=""))
                if send:
                    self.upload.upload_data()
                    
        except:
            pass
    
    
    
    
    def check_up(self):
        if self.__event_timer_check is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer_check)
            except:
                pass
            
        self.__event_timer_check = self.__xbee_manager.xbee_device_schedule_after(1800, self.check_up)
        
        try:
            last_time = self.property_get("last_com").timestamp
            time_dif =  time.time() - int(last_time)
            
            if time_dif > 7200:
                self.update()
            if time_dif > 10800:
                process_request('<rci_request><reboot /></rci_request>')
        except:
            print "check up didn't work"
            
        
        
    
    def update_loop(self):
        try:
        
            while True:
                self.heartBeat()
                print "update loop running!!"
                time.sleep(1800)
                
                last_time = self.property_get("last_com").timestamp
                time_dif =  time.time() - int(last_time)
                
                if time_dif > 7000:
                    print "restarting!!!! look out!!"
                    time.sleep(2)
                    process_request('<rci_request><reboot /></rci_request>')
                    
                
                
                  
                if self.fwu == 0:    
                    self.serial_send("g=6,")
                    self.full_update = True
        except:
            print "rebooting now from MA driver, see ya"
            process_request('<rci_request><reboot /></rci_request>')
                            
                            
                            
                            
                        
                            
                
    
    
    def update(self):
        
        
        """if self.__event_timer2 is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer2)
            except:
                pass
            
        self.__event_timer2 = self.__xbee_manager.xbee_device_schedule_after(3600, self.update)"""
        """
            Request the latest data from the device.
        """   
        #self.get_signal(send=False)
        try:   
            if self.fwu == 0:
                try:
                    
                    self.serial_send("g=6,")
                    self.full_update = True
                    
                    
                    
                    
                except:
                    print "error sending request to mistaway controller"
                    
        except:
            pass
	        
            #self.next_mist()
            
        

        #Reschedule this update method
        
    
    
    
    
    
      #  self.property_set("update",
       #                         Sample(0, value="0", unit=""))
    
    
    def stop(self):
    	
    	
		
        # Unregister ourselves with the XBee Device Manager instance:
        self.__xbee_manager.xbee_device_unregister(self)
        

        return True


    ## Locally defined setions:

    def _parse_return_message(self, msg):
        """ Take a status string from thermostat, and
            split it up into a dictionary::
            
                "A" "0" "T=74" -> {'A':0, 'T':74}
            
        """
        # msg.replace(",$", " ")
        #  msg.replace(",", " ")
        
        
        msg = msg.strip()
           
       
		#take off ,$ from end
        msg = msg[:-2]

        try:
            if not msg:
                return 0
            
            ret = {}
            split_msg = msg.split(",") #tokenize
    #        print split_msg
            for i in split_msg:
            	try:
	                i = i.split("=")
	                ret[i[0].strip()] = i[1].strip()
                except:
	            	continue
                

          #  print ret
            return ret

        except:
            print "Error parsing return message: " + repr(msg)
            return 0

    
    def get_all_settings (self, register_name, val):
    	
    	self.getting_all_values = 1
    	
    	self.update()
    	
    	
    
    
    def set_settings_to_file (self, d):
    	
    	
    	file = open("WEB/python/datafile.txt", "w")
    	
    	for i in d:
		        	
			try:
				file.writelines(str(i) + "=" + str(value) + ",")
			except:
				continue
    	
    	file.close()
    
    
    
    def replace_all_settings (self, register_name, val):
    	
    	test = bool(val.value)
        if test:
            self.dst("forward")
            
        if not test:
            self.dst("backward")
        
        
        #file = open("WEB/python/datafile.txt", "r")
    	
    	#f = file.readlines()
    	
    	#print f
    	
    	
    	
    	'''msg = msg.strip()
        
        if msg.startswith("1"):
            msg = msg[1:]
           
       
		#take off ,$ from end
        msg = msg[:-2]

        try:
            if not msg:
                return {}
            
            ret = {}
            split_msg = msg.split(",") #tokenize
    #        print split_msg
            for i in split_msg:
            	try:
	                i = i.split("=")
	                ret[i[0]] = i[1]
                except:
	            	continue
                

          #  print ret
            return ret

        except:
            print "Error parsing return message: " + repr(msg)
            return {}'''
    
    
    def get(self, register_name, val):
    	
    	self.property_set(register_name, val)
    	
    	data = "g=" + str(val.value) + ","
    	
    	self.serial_send(data)
    
    
    
    def set_time(self, register_name, val):
    	
    	#self.list += 1
    	
    	#time.sleep(self.list)
        val.timestamp = time.time()
    	val.unit = "sec2time"
    	self.property_set(register_name, val)
    	value = val.value
    	
    	new_val = value.split(":")
    	
    	print new_val[0]
    	print new_val[1]
    	# multiply hours by 3600 for seconds in the hours
    	hours_in_seconds = int(new_val[0]) * 3600
    	
    	#mulitply minutes by 60 to get seconds in the minutes
    	minutes_in_seconds = int(new_val[1]) * 60
    	
    	seconds = hours_in_seconds + minutes_in_seconds
    	
    	
    	data = "s(" + register_name + "=" + str(seconds) + ")"
     	#self.property_set(register_name, Sample(0, value=str(seconds), unit=""))
     	
     	print data
     	
     	self.serial_send(str(data))
         
        self.next_mist(total=False)
     	
     	
     	#self.list -= 1
    
    
    def set_lvl(self, register_name, val, bot=None):
        val.unit = "LVL"
        val.timestamp = time.time()
        
        old_lvl = self.property_get("LVL").value
        
        if float(val.value) > float(old_lvl):
            print "level increased"
            self.property_set("LF", Sample(time.time(), value=iso_date(self.current_time_get()), unit=""))
            self.upload.upload_data()
            
        if int(val.value) > 100:
            val.value = "100"
            
        self.property_set(register_name, val)
        
        
        status = self.property_get("SS").value
        
        if self.sys_type == 3:
            if status == "Empty" or self.current["SS"] == "e":
                self.serial_send("r=CE,")
                time.sleep(3)
                
        if self.sys_type == 3: 
            if bot == None:
                CF = (int(self.property_get("BOT").value) * 295.735)
            else:
                CF = bot * 295.735
            print "here is the CF value"
            print CF
        else:
            CF = (float(self.property_get("TNK").value) * 3785.41)
            
        percent = float(val.value)
        
        mlValue = int((percent / 100) * CF)
        print "here is the ml Value"
        print mlValue
        data = "s(" + register_name + "=" + str(mlValue) + ")"
        print data
        self.serial_send(data)
        time.sleep(2)
        
        if self.sys_type == 1:
            if status == "Empty" or self.current["SS"] == "e":
                self.serial_send("r=CE,")
                time.sleep(3)
        
        self.upload.upload_data()
        
    
    
    def set_10ml2oz(self, register_name, val):
        

        
        LVL = self.property_get("LVL").value
        
        print LVL + " is the value of Level (LVL)"
        
        LVL = float(LVL)
        val.timestamp = time.time()
        val.unit = "10ml2oz"
        self.property_set(register_name, val)
        
        
        
        oz = float(val.value)
        
        tenthMl = oz * 295.735
        
        tenthMl = int(tenthMl)
        
        
        data = "s(" + register_name + "=" + str(tenthMl) + ")"
        
        print "here is the BOT data"
        
        print data 
        
        self.serial_send(data)
        
        
        LVL_ml = (295.735 * oz) * (LVL / 100)
        LVL_ml = int(LVL_ml)
        data = "s(" + "LVL" + "=" + str(LVL_ml) + ")"
        
        self.serial_send(data)
        print "level data:"
        print data
    
    def set_cycle(self, register_name, val):
        
        #self.list += 1
        
        #time.sleep(self.list)
        val.timestamp = time.time()
        self.property_set(register_name, val)
        
        print val.value
        data = "s(" + register_name + "=" + str(val.value) + ")"
         
        self.serial_send(data)
        
        self.next_mist(total=False)
         
        #self.list -= 1
    
    def set_sec2min(self, register_name, val):
        
         #self.list += 1
        
         #time.sleep(self.list)
         val.timestamp = time.time()
         val.unit = "sec2min"
         new_value = int(val.value) * 60
         
         self.property_set(register_name, val)
         print val.value
         data = "s(" + register_name + "=" + str(new_value) + ")"
         
         self.serial_send(data)
         
         #self.list -= 1
        
    
    def set(self, register_name, val):
    	
    	#self.list += 1
    	
    	#time.sleep(self.list)
        val.timestamp = time.time()
    	
     	self.property_set(register_name, val)
     	print val.value
     	data = "s(" + register_name + "=" + str(val.value) + ")"
     	
     	self.serial_send(data)
         
        if register_name == "MD":
            if self.fwu == 0:    
                self.serial_send("g=6,")
                self.full_update = True
     	
     	#self.list -= 1
     	
     	
     	
    def set_dst(self, register_name, val):
        
        
         val.timestamp = time.time()
         self.property_set(register_name, val)
         
         value = val.value
         value = str(value)
         value = value.strip()
         
         if value == "2" or value == "3":
             print "this better work"
             self.dst("forward")
    
    
    
    
    
    def new_update(self, register_name, val):
        val.timestamp = time.time()
    	
    	self.property_set(register_name, val)
    	
    	r = self.property_get("r").value
    	
    	
    	
    	r = r.strip()
    	
    	print r
    	
    	if self.fwu == 0:
    		
            if r == "M":
                self.serial_send("r=M,")
                #self.property_set("LM", Sample(0, value="Last_Mist", unit=""))
            elif r == "FSP":
                self.serial_send("p=FLT,")
                time.sleep(3)
                self.upload.upload_data()
            elif r == "7":
                self.push_all_settings = 1
                self.update()
            elif r == "6":
                self.update()
            elif r == "1":
                self.update()
                #self.upload.upload_data()
            elif r == "S":
                self.serial_send("r=S,")
                time.sleep(.5)
                #self.serial_send("r=1,")
            elif r == "I":
                self.serial_send("r=I,")
            elif r == "CE":
                self.serial_send("r=CE,")
                time.sleep(.5)
                self.serial_send("r=S,")
            elif r == "CH":
                self.serial_send("r=CH,")
            elif r == "SM":
                self.serial_send("r=SM,")
            elif r == "CS":
                self.serial_send("r=CS,")
            elif r == "IZ1":
                self.serial_send("r=IZ1,")
            elif r == "IZ2":
                self.serial_send("r=IZ2,")
            elif r == "FT":
                self.serial_send("r=FT,")
                time.sleep(10)
                self.upload.upload_data()
				
    def _config_done_cb(self):
        """ Indicates config is done. """
        print self.__name + " is done configuring, starting polling"
  #      self.test = 0 #previous cr value
        p = queue_runner(self.queue, self)
        p.setDaemon(True)
        p.start()
  
        self.test2 = 0 #previous status
        self.count = 0
        self.string = ""

        upld = self.__core.get_service("presentation_manager")
        self.upload = upld.driver_get("Uploader")
        #self.upload = iDigi_DB("uploader", self.__core, )
       
        time.sleep(10)

        self.update()
        
        time.sleep(10)
        self.update()
        thread.start_new_thread(self.update_loop, ())
        
        time.sleep(15)
        
        self.get_signal(send=False)
        
        #time.sleep(10)
        
        #self.check_up()
        
        
        


    
            
    
    def serial_read(self, buf):
        self.send_data_to_meshify = False
        self.send_all_data_to_meshify = False
        print "XBeeSerialTerminal: Read Data: %s" % (buf)



        self.property_set("serialReceive", Sample(time.time(), buf, ""))
        
        if buf.startswith("?") or buf.endswith("?"):
            return
        
        if self.listen == False:
            return


        if self.fwu == 1:
            if buf == "O":
                self.retry_count = 0
                line = self.line + 1 
                self.line = line
                self.send_next_line(line)
            elif buf == "CE":
                time.sleep(10)
                self.retry_count += 1
                print "retry count ="
                print self.retry_count
                ere = "retry count =" + str(self.retry_count) + " on line number:" + str(self.line)
                self.property_set("error", Sample(time.time(), ere, "E"))
                if self.retry_count > 15:
                	self.line = 300
                	self.retry_count = 0
                	self.error = "error updating firmware. Program quitting"
                	self.property_set("error", Sample(time.time(), self.error, "E"))
                	self.property_set("line_number", Sample(time.time(), 300, "line"))
            	else:
                    self.send_repeat()
        elif self.fwu == 2:
            if buf == "O":
                self.fwu = 0
                self.execute()
            else:
                print "failed to validate file"


        else:
        
            if buf == "?":
                return

            if not buf.endswith("$"):
                self.string = self.string + buf

            if buf.endswith("$"):
                
                #on each com string update the timestamp of the last_com channel
                
                self.property_set("last_com", Sample(time.time(), value=iso_date(self.current_time_get()), unit=""))
                

                self.string = self.string + buf
                
                if self.string.startswith("crc="):
                    self.string = ""
                    return

                d = self._parse_return_message(self.string)
                
                
                
                self.string = ""
                
                if d == 0:
                    return
                
                
                
                if self.getting_all_values == 1:
                    
                    self.set_settings_to_file(d)

                    self.string = ""

                    self.getting_all_values = 0
                    return
                
                if self.push_all_settings == 1:
                    self.push_all_settings = 0
                    self.current = None

                
                #this next block is to make it only set data that has changed, this helps the uploader by keeping the timestaps the same and not clogging up the 
                #network with too much data
                
                #this first block builds a dictionary of current values for the system, this block is repeated until it comes up with no errors, at that point we can 
                #assume that the dictionary is complete and only start saving new values.
                
                
                
                error = 0
                if self.current == None:
                    self.current = {}
                    try:
                        for i in d:
                            name = str(i)
                            value = d[i]
                            old_value = None
                            if name == "VER":
                                self.property_set("VER", Sample(time.time(), str(value), unit=""))
                            try:
                                self.set_loop(name, value, old_value)
                            except:
                                time.sleep(1)
                                try:
                                    send_data = self.set_loop(name, value, old_value)
                                except:
                                    print str(name + "didn't set to value: " + value)
                                    continue
                    except:
                        self.current = None
                        return
                    d["VL"] = "0"
                    d["command not foundcrc"] = "0"
                    d["VER"] = "0"
                    self.current = d
                else:
                    self.upload.sending = True
                    #self.upload.upload_lock.acquire(0)
        
                    for i in d:
                        print "looping through dictionary"
                        name = str(i)
                        name = name.strip()
                        value = d[i]
                        value = str(value)
                        value = value.strip()
                        try:
                            old_value = self.current[i]
                            old_value = str(old_value)
                            old_value = old_value.strip()
                        except:
                            continue
                        
                        
                        if name == "VER":
                            self.property_set("VER", Sample(time.time(), str(value), unit=""))
                            
                        print "old value = " + str(old_value)
                        print "new value = " + str(value)
                        if value != old_value or name == "SS":
                            print "found new value for: " + name
                            try:
                                self.set_loop(name, value, old_value)
                            except:
                                time.sleep(1)
                                try:
                                    send_data = self.set_loop(name, value, old_value)
                                except:
                                    print str(name + "didn't set to value: " + value)
                                    continue
                    
                    self.upload.sending = False
                    self.current.update(d)
                    #self.upload.upload_lock.release()
                    if self.full_update != True:
                        if self.send_all_data_to_meshify == True:
                            self.update() 
                            return
                        if self.send_data_to_meshify == True:
                            self.upload.upload_data()
                        
                    if self.full_update == True:
                        self.full_update = False
                        self.next_mist()
                        time.sleep(5)
                        self.serial_send("p=VER,")
                    
                            
                        
                        
                        
                        
                        
                        
                        
            

	
    
    def set_loop(self, name, value, old_value): 
        if str(name) == "command not foundcrc":
           return
        
        
        funct = self.property_get(str(name)).unit
        
        
                
           
             
                
        
        if funct == "":
            print "setting: " + name + " to: " + value
            
            
            self.property_set(str(name), Sample(time.time(), str(value), unit=""))
            if name == "VL":
                self.send_data_to_meshify = True
             
             #If something is set, then set the last setting changed LSC so we know what was last changed      
                 
        elif funct == "sec2time":
             seconds = int(value)
             timeStr = self.sec2time(seconds)
             print "setting: " + name + " to: " + str(timeStr)
             self.property_set(str(name), Sample(time.time(), str(timeStr), unit="sec2time"))
        
        
        elif funct == "LVL":
            
            print "found LVL"
            self.ml2percent(int(value))
            print value
            print self.current[name]
            
            if old_value != None:
                if int(value) > int(old_value):
                    print "level increased"
                    
                    self.property_set("LF", Sample(time.time(), value=iso_date(self.current_time_get()), unit=""))
        
        
        elif funct == "LD":
            if value == "0":
                self.property_set(str(name), Sample(time.time(), "1", unit="LD"))
            if value == "1":
                self.property_set(str(name), Sample(time.time(), "0", unit="LD"))
        
        elif funct == "ST":
            if value == "1":
                self.property_set(str(name), Sample(time.time(), "Gen 1.3", unit="ST"))
            if value == "3":
                self.property_set(str(name), Sample(time.time(), "Gen 3+", unit="ST"))
        
        
        elif funct == "10ml2oz":
            ml = int(value)
            oz = self.ml2oz(ml)
            print "setting: " + name + " to: " + str(oz)
            self.property_set(str(name), Sample(time.time(), str(oz), unit="10ml2oz"))
        
        elif funct == "SS2code":
            
            if value == "s":
                value1 = "OK (SKIP)"
            if value == "a":
                value1 = "Misting"
            elif value == "i":
                value1 = "OK"
            elif value == "e":
                value1 = "Empty"
            elif value == "h":
                value1 = "Off"
            elif value == "0":
                value1 = "Error 0"
            elif value == "1":
                value1 = "Error 0"
            elif value == "2":
                value1 = "Error 2"
            elif value == "3":
                value1 = "Error 3"
            elif value == "4":
                value1 = "Error 4"
            elif value == "5":
                value1 = "Error 5"
            elif value == "6":
                value1 = "Error 6"
            elif value == "7":
                value1 = "Error 7"
            print value1
                 
            self.property_set(str(name), Sample(time.time(), str(value1), unit="SS2code"))
            print "setting: " + name + " to: " + str(value1)
            if value1 == "Misting":
                self.property_set("LM", Sample(time.time(), "Last_Mist", ""))
            #if value1 != "OK" and self.status_checking == False:
                #self.status_update()
        
        elif funct == "tenths2ml":
             val1 = self.tenths2ml(value)
             print "setting: " + name + " to: " + str(val1)
             self.property_set(str(name), Sample(time.time(), str(val1), unit="tenths2ml"))
        
        elif funct == "sec2hour":
            hours1 = self.sec2hour(value)
            self.property_set(str(name), Sample(time.time(), str(hours1), unit="sec2hour"))
        
        elif funct == "tensec2hour":
            hours1 = self.tensec2hour(value)
            self.property_set(str(name), Sample(time.time(), str(hours1), unit="tensec2hour"))
            
        elif funct == "sec2min":
             min = ( int(value) / 60)
             min = int(min)
             print "setting: " + name + " to: " + str(min)
             self.property_set(str(name), Sample(time.time(), str(min), unit="sec2min"))
        
        
        else:
            print "setting: " + name + " to: " + str(value)
            self.property_set(str(name), Sample(time.time(), str(value), unit=funct))
            
        try:
            
            if name == "SS":
                if old_value == "a": 
                    if value != "a":
                        self.property_set("LM", Sample(time.time(), "Last_Mist", ""))
                        self.send_all_data_to_meshify = True
                    
                if old_value == "a" or old_value == "i":
                    try:
                        if int(value) > -1:
                            self.send_all_data_to_meshify = True
                    except:
                        pass
                    
                if value == "e":
                    self.property_set("LVL", Sample(time.time(), "0", "LVL"))  
                
                self.send_data_to_meshify = True
                
        except: 
            print "didn't have old SS this time"
    
    
    def status_update(self):
        
        if self.event_timer_status == None:
                
            self.event_timer_status = self.__xbee_manager.xbee_device_schedule_after(30, self.status_update)
            return
        
        print "in the status update now"
        
        status = self.property_get("SS").value
        self.status_checking = True
        print status
        
        if status != "OK":
            
            if self.event_timer_status is not None:
                try:
                    self.__xbee_manager.xbee_device_schedule_cancel(
                        self.event_timer_status)
                except:
                    pass
                
            self.event_timer_status = self.__xbee_manager.xbee_device_schedule_after(30, self.status_update)
            print "getting SS"
            self.serial_send("p=SS,")
        else:
            self.status_checking = False
            self.event_timer_status = None
        
        
        
    
    
    def f_name(self, register_name, val):
        val.timestamp = time.time()
    	
    	self.property_set(register_name, val)
    	
    	fname = self.property_get("file_name").value
    	
    	self.filename = "WEB/python/" + fname
    	
    	
    
    def execute(self):
    	
    
    	print "starting program"
    	self.send("XX")
        time.sleep(15)
        self.push_all_settings = 1
        self.update()
        #time.sleep(45)
        #self.firm_update("a", self.filename)
        
        
        
    
    def firm_update(self, register_name, val):
        
        self.fwu = 0
    	
    	if self.file is not None:
	    	try:
	    		self.file.close()
	    	except:
	    		print "file did not need to be closed"
	        
        
        
        
        
        
        self.line = 0
        line = self.line
        
        if register_name != "a":
            val.timestamp = time.time()
            self.property_set(register_name, val)
        
        # I do this because I don't use the sample object if I call this function internally, instead I just pass it the filename
        if register_name != "a":
            self.filename = "WEB/python/" + val.value

        
            
        try:
            self.file = open(self.filename, "r")
        except:
            try:
                self.filename = "./" + val.value
                self.file = open(self.filename, "r")
            except:
                self.fwu = 0
                print "could not open file"
                self.error = "file could not open"
                self.property_set("error", Sample(time.time(), self.error, "E"))
                return
        
        
        
        print "sending q"
        self.send("q")
        time.sleep(1)
        self.send("q")
        
        
        time.sleep(4)
        
        
        
        
        print "puttng device in bootloader mode"
        self.send("r=F,crc=63902,$")
        time.sleep(1)
        self.send("r=F,crc=63902,$")
        time.sleep(1)
        self.send("r=F,crc=63902,$")
        
        time.sleep(20)
        self.fwu = 1
         
        print "sending N"
        
        
        
        self.send("N")
        time.sleep(10)
        
        self.listen = False
        
        
        
        
        
        
        
        data1 = self.file.readline()
        data1 = data1.strip()
        self.data = data1[1:]
        
        
        #for i in range(len(self.f)):         
         #   self.f[i] = self.f[i][1:]
          #  self.f[i] = self.f[i].strip()
        
        self.send("MM")
        print "sending M, clearing memory"
        
        print "sleeping 10 sec"
        
        time.sleep(10)
        
        self.last_line = 0
    	self.check = 0
        
        self.timeout()
     
        try:
        	lst = self.chunks(self.data, 20)
        except:
            self.fwu = 0
            self.listen = True
            self.error = "could not break up line:" + str(self.line) + " into pieces"
            self.property_set("error", Sample(time.time(), self.error, "E"))
            print self.error
            return
        
        

        try:
            self.listen = True
            self.send("@")
            time.sleep(1)
            for i in range(len(lst)):
                self.send(lst[i])
                time.sleep(.1)
            self.listen = True

        except:
            self.listen = True
            self.error = "error sending line:" + str(self.line)
            self.property_set("error", Sample(time.time(), self.error, "E"))
            print self.error

    def send_repeat(self):
    	
        
    	lst = self.chunks(self.data, 20)
    	self.send(chr(64))
    	time.sleep(.1)
        self.listen = False
    	for i in range(len(lst)):
    		self.send(lst[i])
    		time.sleep(.1)
        self.listen = True
    	
    	
    	
    	
    	
    
    def send_next_line(self, line):
        print "sending line number:"
        print line
        
        if line == 71:
            time.sleep(5)
        
        if line == 73:
        	time.sleep(5)
        
        if line == 74:
        	time.sleep(5)
        
        if line == 72:
        	time.sleep(5)
        
        if line == 84:
        	time.sleep(5)
        
        if line == 91:
            time.sleep(5)
        
        if line == 92:
            time.sleep(5)
        	
        	
        pause1 = self.property_get("pause").value
        size = self.property_get("block_size").value
        
        
        self.property_set("line_number", Sample(time.time(), line, "line"))
        
        if line < 50:
        	time.sleep(2)
        else:
        	time.sleep(2)
        
        try:
            data1 = self.file.readline()
            if len(data1) < 2:
                print "ending upload"
                self.fwu = 2
                time.sleep(10)
                self.property_set("line_number", Sample(time.time(), 200, "line"))
		    #	self.file.close()
                self.send("YY")
                time.sleep(10)
                self.update()
                self.line = 200
            if len(data1) > 2:
                data1 = data1.strip()
                self.data = data1[1:]
                lst = self.chunks(self.data, size)
                self.send(chr(64))
                time.sleep(.1)
                self.listen = False
                for i in range(len(lst)):
                    self.send(lst[i])
                    print lst[i]
                    time.sleep(pause1)
                self.listen = True
                    
              

        except:
            self.listen = True
            self.error = "error sending line:" + str(self.line)
            self.property_set("error", Sample(time.time(), self.error, "E"))
            print self.error
	    
	    
	    
	    
	    	
	      
        	
        
        
    
    def timeout(self):
    	
    	
    	
    	
    		
    	self.check += 1
    	print "number of times timeout has ran:"
    	print self.check
    	
    	
        if self.check > 1:	
            if self.line == self.last_line:
                print "restarting, device timed out"
                self.property_set("error", Sample(time.time(), "restarting, device timed out", "E"))
                self.retry += 1
	    		
                if self.retry < 5:
                    self.firm_update("a", self.filename)
                else:
                    self.send("q")
                    self.line = 300
                    self.fwu = 0
                    self.retry = 0
                    self.error = "error updating firmware. Program quitting"
                    self.property_set("error", Sample(time.time(), self.error, "E"))
                    self.property_set("line_number", Sample(time.time(), 300, "line"))
    				
    				
	    		
    			
    		
       
    	
    	self.last_line = self.line
    	
    	if self.__event_timer3 is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer3)
            except:
                pass
        
        if self.line == 200 or self.line == 300:
        	pass    
        else:
        	
        	self.__event_timer3 = self.__xbee_manager.xbee_device_schedule_after(
	                30,
	                self.timeout)
        	
	        	
        
        
        
        
        
  
    
    
    
    
    def chunks(self, seq, length):
    	return [seq[i:i+length] for i in range(0, len(seq), length)]
    
    
    def ml2percent(self, ml):
        SS = self.property_get("SS").value
        
        if SS == "Empty":
            self.property_set("LVL", Sample(time.time(), "0", "LVL"))
            return
        
        
        LVL = ml
        
        if self.sys_type == 3:
            CF = self.property_get("CF").value
        else:
            CF = (float(self.property_get("TNK").value) * 3785.41)
            
        if CF == 0:
            return
        
        print LVL
        print CF
        try:
            LVL = float(LVL)
            CF = float(CF)
        except:
            print "didn't work this time, maybe next time?"
            return
        
        if int(CF) != 0:
            remaining = (LVL / CF)
            print remaining
            if self.sys_type == 3:
                remaining = remaining * 10
            else:
                remaining = remaining * 100
                
            remaining = round(remaining, 2) 
            
            if remaining > 100:
                remaining = "100"
            #remaining = int(remaining)
            self.property_set("LVL", Sample(time.time(), str(remaining), "LVL"))
            print "precent remaining"
            print remaining
    
    
    
    
    
    def set_labels(self):
        try:
            zone = bool(int(self.property_get("ZK").value))
            znc = bool(int(self.property_get("ZNC").value))
            CL = self.property_get("CL0").value
            print zone
            print znc
            if zone and znc and CL == "C1":
                for i in range(0, 24 / 1):
                    if i < 12:
                        nameCL = "CL" + str(i)
                        x = i + 1
                        valueCL = "A" + str(x)
                        self.property_set(nameCL, Sample(time.time(), str(valueCL), ""))
                    else:
                        nameCL = "CL" + str(i)
                        x = i - 11
                        valueCL = "B" + str(x)
                        self.property_set(nameCL, Sample(time.time(), str(valueCL), ""))
            if not zone and CL == "A1":
                for i in range(0, 24 / 1):
                        nameCL = "CL" + str(i)
                        x = i + 1
                        valueCL = "C" + str(x)
                        self.property_set(nameCL, Sample(time.time(), str(valueCL), ""))
            if not znc and CL == "A1":
                for i in range(0, 24 / 1):
                        nameCL = "CL" + str(i)
                        x = i + 1
                        valueCL = "C" + str(x)
                        self.property_set(nameCL, Sample(time.time(), str(valueCL), ""))
        except:
            pass
            
        
    
    def next_mist(self, total=True):
        
        
        
        
    	#total means, I'm doing a total upload  of everything here, which means I need to 
        if total:
            self.set_labels()
               
               
        try:
            t = self.current_time_get()
        except:
            print "error getting timezone data from main driver "
            return
        #timezone = timezone1.value
    	#t = int(t) + int(timezone)
        print "time function"
        print strftime("%Y-%m-%d %H:%M:%S", localtime(t))
        hours = strftime("%H", localtime(t))
        minutes = strftime("%M", localtime(t))
        day = strftime("%w", localtime(t))
        hours = int(hours)
        minutes = int(minutes)
        
        print hours
        print minutes
        
        clock_time = str(hours) + ":" + str(minutes)
        
        #set clock on the controller to the current time
        
        day = str((int(day) + 1))
        
        # here I'm setting the local channel time of day and day of week, but only if a total sweep of setting changes is 
        # required 
        if total:
        
            self.property_set("TOD", Sample(time.time(), str(clock_time), "sec2time"))
            self.property_set("DOW", Sample(time.time(), str(day), ""))
        
        
        
        hoursSec = (3600 * hours)
        minutesSec = (60 * minutes)
        timeSec = (hoursSec + minutesSec)
        print "time of day in seconds"
        print timeSec
        
        
        # here I'm setting the veriables to the controller  
        if total:
            self.serial_send("s(TOD=" + str(timeSec) + ")") 
            time.sleep(2)
            self.serial_send("s(DOW=" + str(day) + ")")
        
    	time_list = {}
    	new_list = {}
    	
        for i in range(0, 24 / 1):
            try:
                nameCT = "CT" + str(i)
                nameCY = "CY" + str(i)
                CT = self.property_get(nameCT).value
                CY = self.property_get(nameCY).value
                CT = int(CT)
            except:
                continue
            
            if CT != 0:
                
                print CT
                print CY
                
                if ":" not in str(CY):
                    continue
                
                new_val = CY.split(":")
                
                
                # multiply hours by 3600 for seconds in the hours
                hours_in_seconds = int(new_val[0]) * 3600
                
                #mulitply minutes by 60 to get seconds in the minutes
                minutes_in_seconds = int(new_val[1]) * 60
                
                seconds = hours_in_seconds + minutes_in_seconds
                    
                
                time_list[seconds] = CT
            
            
        set = False
        
        for time1 in sorted(time_list.iterkeys()):
            print time1
            print timeSec
            print time_list[time1]
    		
            if int(time1) > int(timeSec) and int(time_list[time1]) > 1:
                if int(time1) == 0:
                   aTime = "12:00 AM"
                   self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                   return 
                if int(time1) < 60:
                    aTime = "12:00 AM"
                    self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                    return
                minutes, seconds= divmod(int(time1), 60)
                if minutes < 60:
                    hours = 0
                    minutes2 = minutes
                else:
                    hours, minutes2= divmod(minutes, 60)
                if int(minutes2) < 10:
                    if minutes2 == 0:
                        minutes2 = "00"
                    else:
                        minutes2 = "0" + str(minutes2)
                if hours == 0:
                    aTime = "12" + ":" + str(minutes2) + " AM" 
                elif hours == 12:
                    aTime = "12" + ":" + str(minutes2) + " PM"
                
                elif hours > 12:
                    hours = hours - 12
                    aTime = str(hours) + ":" + str(minutes2) + " PM"
                
                else:
                    aTime = str(hours) + ":" + str(minutes2) + " AM" 
                print "time of next mist is:"
                print aTime
                set = True
                self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                if total:
                    self.upload.upload_data()
                return
        
        #If we didn't find a time that is later today then pick up the first time for tomorrow from the beginning of the list

        print "checking for tomorrosw"
        for time1 in sorted(time_list.iterkeys()):
            if int(time_list[time1]) != 0:
                if int(time1) == 0:
                   aTime = "12:00 AM Tomorrow"
                   self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                   if total:
                        self.upload.upload_data()
                   return 
                
                if int(time1) < 60:
                    aTime = "12:00 AM Tomorrow"
                    self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                    if total:
                        self.upload.upload_data()
                    return
                minutes, seconds= divmod(int(time1), 60)
                if minutes < 60:
                    hours = 0
                    minutes2 = minutes
                else:
                    hours, minutes2= divmod(minutes, 60)
                if int(minutes2) < 10:
                    if minutes2 == 0:
                        minutes2 = "00"
                    else:
                        minutes2 = "0" + str(minutes2)
                if hours == 0:
                    aTime = "12" + ":" + str(minutes2) + " AM" + " Tomorrow"
                
                elif hours == 12:
                    aTime = "12" + ":" +  str(minutes2) + " PM" + " Tomorrow"
                
                elif hours > 12:
                    hours = hours - 12
                    aTime = str(hours) + ":" + str(minutes2) + " PM" + " Tomorrow"
                
                else:
                    aTime = str(hours) + ":" + str(minutes2) + " AM" + " Tomorrow"
                print "time of next mist is:"
                print aTime
                set = True
                self.property_set("NSM", Sample(time.time(), str(aTime), "E"))
                break
        if set == False:
            self.property_set("NSM", Sample(time.time(), "No Mist Scheduled", "E"))
        if total:
            self.upload.upload_data()
                
    	
        
    	

    def serial_write(self, register_name, val):
        val.timestamp = time.time()
    	
    	self.property_set(register_name, val)
    	
    	buf = self.property_get("serialSend").value
        buf = buf.strip()
        try:
            ret = self.write(buf)
            if ret == False:
                raise Exception, "write failed"
        except:
            print "XBeeSerialTerminal: Error writing data:"
    
    
    def send(self, data):
      #  print "XBeeSerialTerminal: Write Data: %s" % (data)
        #buf = data.value + chr(0x0D)
  #      buf = data.value
        

        
        try:
            ret = self.write(str(data)) 
          #  ret = self.write("r=1,crc=63902,$")
         #   print data1
  #          print self.calcByte( "r=1", INITIAL_DF1)
            if ret == False:
                raise Exception, "write failed"
        except:
            print "XBeeSerialTerminal: Error writing data:"
    
    
    def serial_send(self, data):
        self.queue.put(data)
        
    
    def send_data(self, data):
     #   print "XBeeSerialTerminal: Write Data: %s" % (data)
        #buf = data.value + chr(0x0D)
  #      buf = data.value
        if self.fwu == 0:
            data1 = data  + "crc=" + str(self.calcString(data, 0)) + ",$"
            
            try:
                ret = self.write(str(data1)) 
              #  ret = self.write("r=1,crc=63902,$")
             #   print data1
      #          print self.calcByte( "r=1", INITIAL_DF1)
                if ret == False:
                    raise Exception, "write failed"
            except:
                print "XBeeSerialTerminal: Error writing data: %s" % (buf)

# internal setions & classes
    
    def ml2oz(self, ml):
        
        oz = float(ml) * 0.0033814
        oz = round(oz, 2)
        print oz
        oz = int(oz)
        return str(oz)
    
    
    def dst(self, direction):
        
        self.update()
        
        time.sleep(8)
        
        on = self.property_get("DST").value
        on = str(on)
        on = on.strip()
        
        if on == "3":
            on = "1"
            direction = "backward"
            self.property_set("DST", Sample(time.time(), "1", ""))
        
        if on == "2":
            on = "1"
            direction = "forward"
            self.property_set("DST", Sample(time.time(), "1", ""))
        
        if on == "1":
            for i in range(0, 24 / 1):
                nameCY = "CY" + str(i)
                cy = self.property_get(nameCY).value
                print cy
                list = cy.split(":")
                sec_hours = int(list[0]) * 3600
                sec_min = int(list[1]) * 60
                sec = sec_hours + sec_min
                print sec
                
                if direction == "forward":
                    new_val = sec + 3600
                    if new_val > 86400:
                        new_val = new_val - 86400
                    data = "s(" + str(nameCY) + "=" + str(new_val) + ")"
                    print data
                    self.serial_send(data)
                    #time.sleep(1)
                if direction == "backward":
                    new_val = sec - 3600
                    if new_val < 0:
                        new_val = new_val + 86400
                    data = "s(" + str(nameCY) + "=" + str(new_val) + ")"
                    print data
                    self.serial_send(data)
                    #time.sleep(1)
                    
                
                
                
                
            
    def tenths2ml(self, tml):
        
        ml = float(tml) / 10
        ml = int(ml)
        return str(ml)
    
    def tensec2hour(self, seconds):
        seconds = (int(seconds) /10)
        
        hours = int((seconds / 3600))
        
        
        return str(hours)
    
    def sec2hour(self, seconds):
        seconds = int(seconds)
        
        hours = int((seconds / 3600))
        
        
        return str(hours)
        
    
    def sec2time(self, seconds):
        minutes, seconds= divmod(int(seconds), 60)
        hours, minutes2= divmod(minutes, 60)
        if int(minutes2) < 10:
           if minutes2 == 0:
               minutes2 = "00"
           else:
               minutes2 = "0" + str(minutes2)
               
        
        
        
        
        time = str(str(hours) + ":" + str(minutes2))
        
        

        return time
        
   
            
            
            
