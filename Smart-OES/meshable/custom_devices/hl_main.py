############################################################################
#                                                                          #
# Copyright (c)2008, 2009, Digi International (Digi). All Rights Reserved. #
#                                                                          #
# Permission to use, copy, modify, and distribute this software and its    #
# documentation, without fee and without a signed licensing agreement, is  #
# hereby granted, provided that the software is used on Digi products only #
# and that the software contain this copyright notice,  and the following  #
# two paragraphs appear in all copies, modifications, and distributions as #
# well. Contact Product Management, Digi International, Inc., 11001 Bren   #
# Road East, Minnetonka, MN, +1 952-912-3444, for commercial licensing     #
# opportunities for non-Digi products.                                     #
#                                                                          #
# DIGI SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED   #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A          #
# PARTICULAR PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, #
# PROVIDED HEREUNDER IS PROVIDED "AS IS" AND WITHOUT WARRANTY OF ANY KIND. #
# DIGI HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,         #
# ENHANCEMENTS, OR MODIFICATIONS.                                          #
#                                                                          #
# IN NO EVENT SHALL DIGI BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,      #
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS,   #
# ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF   #
# DIGI HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.                #
#                                                                          #
############################################################################
from common.types.boolean import Boolean, STYLE_ONOFF
from devices.device_base import DeviceBase
from devices.xbee.common.addressing import *
from settings.settings_base import SettingsBase, Setting
from channels.channel_source_device_property import *
from common.digi_device_info import get_device_id
import threading
import time
import thread

#imports for weather
import urllib

MAC = str(get_device_id())  #st
MAC = MAC.replace("0x0000000000000000", "")
MAC = MAC.upper()
tMAC = MAC.split("FFFF")
MAC = tMAC[0] + "FF-FF" + tMAC[1]
print "Here is the MAC"
print MAC


# constants

# exception classes

# interface functions

# classes




class hl_main(DeviceBase, threading.Thread):
    """
    This class extends one of our base classes and is intended as an
    example of a concrete, example implementation, but it is not itself
    meant to be included as part of our developer API. Please consult the
    base class documentation for the API and the source code for this file
    for an example implementation.

    """

    def __init__(self, name, core_services):
        self.myName = name
        self.__name = name
        self.__core = core_services
        self.__xbee_manager = None
        
        
        # global veriables 
        self.w_retry = 0 #number of failed retrys in a row for the weather
        self.__event_timer4 = None #event timer for weather repeats
        self.__event_timer_offest = None
        self. mc_list = []
        self.dst_old = False
        self.first_try = False
        ## Settings Table Definition:
        settings_list = [
            
            Setting(
                name='xbee_device_manager', type=str, required=False, default_value="xbee_device_manager"),
            Setting(
                name='sample_rate_sec_w', type=int, required=False,
                default_value=600,
                verify_function=lambda x: x >= 1 and x < 0xffff),
            Setting(
                name='update_rate', type=float, required=False, 
                default_value=600.0,
                verify_function=lambda x: x > 0.0),
        ]

        ## Channel Properties Definition:
        property_list = [
            # gettable properties
            
            
            
            ChannelSourceDeviceProperty(name="zip", type=str,
                initial=Sample(timestamp=time.time() + 600, unit="zip", value="10001"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.update_name("zip", x)),
                
            ChannelSourceDeviceProperty(name="w_t", type=str,
                initial=Sample(timestamp=time.time(), unit="degF", value="60"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
            
            
            ChannelSourceDeviceProperty(name="offset", type=int,
                initial=Sample(timestamp=time.time(), unit="UTC", value=-21600),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
            
            ChannelSourceDeviceProperty(name="hb", type=str,
                initial=Sample(timestamp=time.time() + 600, unit="", value="On"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=lambda x: self.update_hb("hb", x)),
            
            ChannelSourceDeviceProperty(name="w_h", type=str,
                initial=Sample(timestamp=time.time(), unit="percent", value="O"),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP),
                
        ]
                                            
        ## Initialize the DeviceBase interface:
        DeviceBase.__init__(self, self.__name, self.__core,
                                settings_list, property_list)

        ## Thread initialization:
        self.__stopevent = threading.Event()
        threading.Thread.__init__(self, name=name)
        threading.Thread.setDaemon(self, True)
        self.apply_settings()
        self.start()

    ## Functions which must be implemented to conform to the DeviceBase
    ## interface:

    def apply_settings(self):
        
        SettingsBase.merge_settings(self)
        accepted, rejected, not_found = SettingsBase.verify_settings(self)
        if len(rejected) or len(not_found):
            print "Settings rejected/not found: %s %s" % (rejected, not_found)

        SettingsBase.commit_settings(self, accepted)

        return (accepted, rejected, not_found)

    def start(self):
        
        
        xbee_manager_name = SettingsBase.get_setting(self, "xbee_device_manager")
        dm = self.__core.get_service("device_driver_manager")
        self.__xbee_manager = dm.instance_get(xbee_manager_name)
        
        extended_address = self.myName.split("_")
        extended_address = extended_address[1]
        print extended_address
        """
        id = self.__xbee_manager.xbee_device_ddo_get_param(extended_address, "ID", use_cache=True)
        
        print id
        try:
            #dd = struct.unpack(">B", db)
            pan = struct.unpack(">i", id)
            print pan
        except:
            print "failed 8" 
        
        """
        
        
        

        mac = gw_extended_address()
        print mac
        
    #    self.reset_stored_values()
        #self.weather()
        self.time_offest()
        
    #    thread.start_new_thread(self.get_temp(), ())
        
        #threading.Thread.start(self)

        return True

    def stop(self):
        self.__stopevent.set()
        return True


    ## Locally defined functions:
    # Property callback functions:
    

    # Threading related functions:
    def run(self):
        self.weather()
        #self.time_offest()
        #self.property_set("hb", Sample(time.time(), "On", ""))
        """count = 4
        hb_count = 0
        hb_count = 120
        while True:
            count += 1
            if count == 5:
                count = 0
                hb_count += 1
                self.property_set("hb", Sample(time.time(), "On", ""))
                time.sleep(60)
            if hb_count == 120:
                hb_count = 0
                self.time_offest()
                time.sleep(60)
        pass
        
        self.weather()
        
      #  time.sleep(SettingsBase.get_setting(self,"update_rate"))"""
        
        
        
    def update_name(self, register_name, val):
        
    

        
        self.property_set(register_name, val)
        
        
        val = self.property_get(str(register_name)).value      
        val = str(val)
        register_name = str(register_name)
        
  #      self.update_list(register_name, val)
              
        if register_name == "zip":
            self.weather()
        else:
            self.update()
    
    
  
        
    
    def time_offest(self):
        
        self.property_set("hb", Sample(time.time(), "On", ""))
        
        
        if self.__event_timer_offest is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer_offest)
            except:
                pass
            
        self.__event_timer_offest = self.__xbee_manager.xbee_device_schedule_after(1800, self.time_offest)
    

        url = "http://devbuildinglynx.apphb.com/api/gateway?macaddressForTimezone=" + MAC
         
        try:
            f = urllib.urlopen(url)
        except:
           print "Error opening url"
           return
        
        try:
            
            
            
            
            
            
            
            s = f.read()
            
            offset = ""
            place_temp = s.find("gmt_offset")
            temp_offset = s[place_temp + 12 : place_temp + 20]
            for i in temp_offset:
                if i != ",":
                    offset = offset + i 
                else:
                    break
            offset = int(offset)
            self.property_set("offset", Sample(0, offset, "UTC"))
            print offset
            
            
            dst = ""
            place_dst = s.find("dst")
            temp_dst = s[place_dst + 6 : place_dst + 7]
            dst = temp_dst
            print dst
            dst = dst.strip()
            if dst == "0":
                dst = False
            if dst == "1":
                dst = True
            print "here is your DST value"
            print dst
            
            if self.first_try == False:
                self.first_try = True
                self.dst_old = dst
                
                if self.__event_timer_offest is not None:
                    try:
                        self.__xbee_manager.xbee_device_schedule_cancel(
                            self.__event_timer_offest)
                    except:
                        pass
                    
                self.__event_timer_offest = self.__xbee_manager.xbee_device_schedule_after(30, self.time_offest)
                return
            
            
            if self.dst_old != dst:
                direction = ""
                if self.dst_old == False and dst == True:
                    direction = "forward"
                
                if self.dst_old == True and dst == False:
                    direction = "backward"
                
                if direction != "":
                    ddm = self.__core.get_service("device_driver_manager")
                    nodes = ddm.get_instance_list()
                    print "here are the nodes"
                    
                    for i in nodes:
                        print i
                        if i.startswith("mc"):
                            if i not in self.mc_list:
                                self.mc_list.append(i)
                    
                    
                    for i in self.mc_list:
                        print "executing DST in node"
                        node = ddm.get_driver_object(i)
                        node.dst(direction)
            
            
            
            self.dst_old = dst
        except:
            print "error getting current offset and DST info from main driver"
        
        
        
           

            
            
     
            
            
        
    
    
    def weather(self):
        
        
       
    
        
       
        """try:
           
            temp = self.globe_get("thermostat_[00:13:a2:00:40:33:50:bf]!.current_temp")
            temp = float(temp.value)
            if temp > 75:
                 self.property_set_globe("outlet_[00:13:a2:00:40:49:a9:72]!.power_on", Sample(0, value=Boolean(bool(True),
                                                style=STYLE_ONOFF)))
            else:
                 self.property_set_globe("outlet_[00:13:a2:00:40:49:a9:72]!.power_on", Sample(0, value=Boolean(bool(False),
                                                style=STYLE_ONOFF)))
        except:
            print "this time it didnt' work"
            """
        print "weather"
        zip = self.property_get("zip").value
        
        url = "http://free.worldweatheronline.com/feed/weather.ashx?q=" +str(zip) + "&format=xml&num_of_days=2&key=1c41e63707211139120310" 

       
        try: 
       
            f = urllib.urlopen(url)
        except:
            self.w_retry += 1
            print "Error opening url"
        
        try:
            s = f.read()
        
            # extract weather condition data from xml string
            
            
         
       
        
            place_temp = s.find("temp_F")
            weather_temp = s[place_temp + 7 : place_temp + 9]
            place_hum = s.find("humidity")
            weather_hum = s[place_hum + 9 : place_hum + 11]
            print weather_temp
            print weather_hum
            
            if len(weather_temp) == 2:
                self.w_retry = 0
            
            if weather_temp == "<?xml version=" or weather_hum == "<?xml version=":
                self.w_retry += 1
            else:
                self.property_set("w_t", Sample(0, weather_temp, "degF"))
                self.property_set("w_h", Sample(0, weather_hum, "percent"))
              
        
      
        except:
            self.w_retry += 1
        
        repeat_val = SettingsBase.get_setting(self, "sample_rate_sec_w")
        
        if self.w_retry > 8:
            #self.property_set("ot_on", Sample(0, 0, "degF"))
            self.property_set("w_h", Sample(0, "broken", "percent"))
            self.w_retry = 0
        
        if self.w_retry > 1 and self.w_retry < 9:
            self.update_update(300)
            self.property_set("w_h", Sample(0, "retry mode", "percent"))
        else:
            self.update_update(repeat_val)
            
        
            
        
        
    
    def update_hb(self, register_name, val):
        
        
        self.property_set(register_name, val)   
    
    
    def update_update(self, repeat_val):    
       
        
        if self.__event_timer4 is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer4)
            except:
                pass
            
        self.__event_timer4 = self.__xbee_manager.xbee_device_schedule_after(
                repeat_val,
                self.weather)
        



# internal functions & classes

