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

"""\
A Dia Driver for the XBee Sensor /L/T(/H) Product.

Note: this is not the driver for the XBee Sensor Adapter product.

Settings:

    xbee_device_manager: must be set to the name of an XBeeDeviceManager
                         instance.
    
    extended_address: the extended address of the XBee Sensor device you
                      would like to monitor.

    sleep: True/False setting which determines if we should put the
           device to sleep between samples.  Default: True

    sample_rate_ms: the sample rate of the XBee adapter. Default:
                    60,000 ms or one minute.

    trace: On/Off; On prints trace line for every sample, Off makes quiet
           Defaults to On/True.

Advanced settings:

    awake_time_ms: how long should the sensor stay awake after taking
                   a sample?  The default is 1000 ms.

    sample_predelay: how long should the sensor be awake for before taking
                     its sample reading?  This delay is used to allow the
                     device's sensoring components to warm up before taking
                     a sample.  The default is 125ms.

    humidity_present: force a sensor which has not been detected to have
                      humidity capability to having humidity capability
                      present.  Writes the devices DD device-type value
                      as a side effect.

"""

# imports
import struct
import time

from devices.device_base import DeviceBase
from devices.xbee.xbee_devices.xbee_base import XBeeBase
from settings.settings_base import SettingsBase, Setting
from channels.channel_source_device_property import *


from common.types.boolean import Boolean, STYLE_ONOFF
from devices.xbee.xbee_config_blocks.xbee_config_block_ddo \
    import XBeeConfigBlockDDO
from devices.xbee.xbee_device_manager.xbee_device_manager_event_specs \
    import *
from devices.xbee.common.addressing import *
from devices.xbee.common.io_sample import parse_is, sample_to_mv
from devices.xbee.common.prodid import PROD_DIGI_XB_RPM_SMARTPLUG


# constants
ENTITY_MAP = {
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
}
# exception classes

# interface functions

# classes
class XBeeSensor(XBeeBase):

    # Define a set of endpoints that this device will send in on.  
    ADDRESS_TABLE = [ [0xe8, 0xc105, 0x92], [0xe8, 0xc105, 0x11] ]

    # The list of supported products that this driver supports.
    SUPPORTED_PRODUCTS = [ PROD_DIGI_XB_RPM_SMARTPLUG ]

    def __init__(self, name, core_services):
        self.__name = name
        self.__core = core_services

        ## Local State Variables:
        self.__xbee_manager = None

        ## Settings Table Definition:
        settings_list = [
            Setting(
                name='sleep', type=bool, required=False,
                default_value=False),
            Setting(
                name='sample_rate_ms', type=int, required=False,
                default_value=10000),
                

            # These settings are provided for advanced users, they
            # are not required:

            Setting(
                name='default_state', type=str, required=False,
                default_value="off",
                parser=lambda s: s.lower(),
                verify_function=lambda s: s in initial_states),
            Setting(name="power_on_source", type=str, required=False),
            Setting(
                name='trace', type=Boolean, required=False,
                default_value=Boolean("On", STYLE_ONOFF)),
            Setting(
                name='awake_time_ms', type=int, required=False,
                default_value=10000,
                verify_function=lambda x: x >= 0 and x <= 0xffff),
            Setting(
                name='sample_predelay', type=int, required=False,
                default_value=125,
                verify_function=lambda x: x >= 0 and x <= 0xffff),
            Setting(
                name='humidity_present', type=bool, required=False,
                default_value=False),
            Setting(
                name='count_init', type=int, required=False, default_value=0,
                  verify_function=lambda x: x >= 0),
            Setting(
                name='update_rate', type=float, required=False, default_value=1.0,
                  verify_function=lambda x: x > 0.0),
            Setting(
                name='temp', type=float, required=False, default_value=1.0),
        ]

        ## Channel Properties Definition:
        property_list = [
            # gettable properties            
            ChannelSourceDeviceProperty(name="aa", type=str,
                initial=Sample(timestamp=0, value="on_off"),
                 perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET), options=DPROP_OPT_AUTOTIMESTAMP),            
            ChannelSourceDeviceProperty(name="light", type=float,
                initial=Sample(timestamp=0, value=0.0, unit="F"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            ChannelSourceDeviceProperty(name="temperature", type=float,
                initial=Sample(timestamp=0, value=0.0, unit="F"),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            ChannelSourceDeviceProperty(name="low_battery", type=bool,
                initial=Sample(timestamp=0, value=False),
                perms_mask=DPROP_PERM_GET, options=DPROP_OPT_AUTOTIMESTAMP),
            ChannelSourceDeviceProperty(name="power_on", type=Boolean,
                initial=Sample(timestamp=0,
                    value=Boolean(False, style=STYLE_ONOFF)),
                perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET),
                options=DPROP_OPT_AUTOTIMESTAMP,
                set_cb=self.prop_set_power_control),
           
                      

        ]

        ## Initialize the XBeeBase interface:
        XBeeBase.__init__(self, self.__name, self.__core,
                                settings_list, property_list)


        
   



    ## Functions which must be implemented to conform to the XBeeBase
    ## interface:

    @staticmethod
    def probe():
        """\
            Collect important information about the driver.

            .. Note::

                * This method is a static method.  As such, all data returned
                  must be accessible from the class without having a instance
                  of the device created.

            Returns a dictionary that must contain the following 2 keys:
                    1) address_table:
                       A list of XBee address tuples with the first part of the
                       address removed that this device might send data to.
                       For example: [ 0xe8, 0xc105, 0x95 ]
                    2) supported_products:
                       A list of product values that this driver supports.
                       Generally, this will consist of Product Types that
                       can be found in 'devices/xbee/common/prodid.py'
        """
        probe_data = XBeeBase.probe()

        for address in XBeeSensor.ADDRESS_TABLE:
            probe_data['address_table'].append(address)
        for product in XBeeSensor.SUPPORTED_PRODUCTS:
            probe_data['supported_products'].append(product)

        return probe_data

    ## Functions which must be implemented to conform to the DeviceBase
    ## interface:

    def apply_settings(self):
        """\
            Called when new configuration settings are available.
       
            Must return tuple of three dictionaries: a dictionary of
            accepted settings, a dictionary of rejected settings,
            and a dictionary of required settings that were not
            found.
        """

        SettingsBase.merge_settings(self)
        accepted, rejected, not_found = SettingsBase.verify_settings(self)

        if len(rejected) or len(not_found):
            # there were problems with settings, terminate early:
            print "Settings rejected/not found: %s %s" % (rejected, not_found)
            return (accepted, rejected, not_found)

        # Verify that the sample predelay time when added to the awake time
        # is not over 0xffff.
        if accepted['sample_predelay'] + accepted['awake_time_ms'] > 0xffff:
            print "XBeeSensor(%s): The awake_time_ms value (%d) "\
                                "and sample_predelay value (%d) "\
                                "when added together cannot exceed 65535." % \
                                (self.__name, accepted['sample_predelay'],\
                                accepted['awake_time_ms'])

            rejected['awake_time_ms'] = accepted['awake_time_ms']
            del accepted['awake_time_ms']
            rejected['sample_predelay'] = accepted['sample_predelay']
            del accepted['sample_predelay']
            return (accepted, rejected, not_found)

        SettingsBase.commit_settings(self, accepted)

        return (accepted, rejected, not_found)


    def start(self):
        """Start the device driver.  Returns bool."""

        # Fetch the XBee Manager name from the Settings Manager:
        xbee_manager_name = SettingsBase.get_setting(self, "xbee_device_manager")
        dm = self.__core.get_service("device_driver_manager")
        self.__xbee_manager = dm.instance_get(xbee_manager_name)

        # Register ourselves with the XBee Device Manager instance:
        self.__xbee_manager.xbee_device_register(self)

        # Get the extended address of the device:
        extended_address = SettingsBase.get_setting(self, "extended_address")

        # Retrieve the flag which tells us if we should sleep:

        # Create a callback specification for our device address, endpoint
        # Digi XBee profile and sample cluster id:
        xbdm_rx_event_spec = XBeeDeviceManagerRxEventSpec()
        xbdm_rx_event_spec.cb_set(self.sample_indication)
        xbdm_rx_event_spec.match_spec_set(
            (extended_address, 0xe8, 0xc105, 0x92),
            (True, True, True, True))
        self.__xbee_manager.xbee_device_event_spec_add(self,
                                xbdm_rx_event_spec)

        # Create a callback specification that calls back this driver when
        # our device has left the configuring state and has transitioned
        # to the running state:
        xbdm_running_event_spec = XBeeDeviceManagerRunningEventSpec()
        xbdm_running_event_spec.cb_set(self.running_indication)
        self.__xbee_manager.xbee_device_event_spec_add(self,
                                                        xbdm_running_event_spec)

        # Create a DDO configuration block for this device:
        xbee_ddo_cfg = XBeeConfigBlockDDO(extended_address)

        # Get the gateway's extended address:
        gw_xbee_sh, gw_xbee_sl = gw_extended_address_tuple()

        # Set the destination for I/O samples to be the gateway:
        xbee_ddo_cfg.add_parameter('DH', gw_xbee_sh)
        xbee_ddo_cfg.add_parameter('DL', gw_xbee_sl)

        # Configure pins DI1 .. DI3 for analog input:
        for io_pin in [ 'D1', 'D2', 'D3' ]:
            xbee_ddo_cfg.add_parameter(io_pin, 2)

        # Configure battery-monitor pin DIO11/P1 for digital input:
        xbee_ddo_cfg.add_parameter('P1', 3)
        # Enable change detection on DIO11:
        #
        # 0x   8    0    0
        #   1000 0000 0000 (b)
        #   DDDD DDDD DDDD
        #   IIII IIII IIII
        #   OOOO OOOO OOOO
        #   1198 7654 3210
        #   10
        #
        xbee_ddo_cfg.add_parameter('IC', 0x800)

        
            
        

        # Configure the IO Sample Rate:
        # Clip sample_rate_ms to the max value of IR:
        sample_rate_ms = SettingsBase.get_setting(self, "sample_rate_ms")
        sample_rate_ms = min(sample_rate_ms, 0xffff)
        xbee_ddo_cfg.add_parameter('IR', sample_rate_ms)

        # Register this configuration block with the XBee Device Manager:
        self.__xbee_manager.xbee_device_config_block_add(self, xbee_ddo_cfg)

     
        
        

        # Handle subscribing the devices output to a named channel,
        # if configured to do so:
        power_on_source = SettingsBase.get_setting(self, 'power_on_source')
        if power_on_source is not None:
            cm = self.__core.get_service("channel_manager")
            cp = cm.channel_publisher_get()
            cp.subscribe(power_on_source, self.update_power_state)
            

        # Indicate that we have no more configuration to add:
        self.__xbee_manager.xbee_device_configure(self)


 
        return True

    def stop(self):
        """Stop the device driver.  Returns bool."""

        # Unregister ourselves with the XBee Device Manager instance:
        self.__xbee_manager.xbee_device_unregister(self)
       

        return True
        

    ## Locally defined functions:
    def running_indication(self):
        # request initial status here.
        print "XBeeSensor(%s): running indication" % (self.__name)
        extended_address = SettingsBase.get_setting(self, "extended_address")

        # this is a flawed design - if the gateway has just rebooted,
        # and the Xbee sensor sleeps (which it should), then an actual
        # GET_DDO will be issued, which causes Dia to freeze here and
        # almost certainly throw exception and put the device off line.
        

    def sample_indication(self, buf, addr):

        # check if we want to scroll a trace line or not
        do_trace = SettingsBase.get_setting(self, "trace")
        if do_trace:
            msg = ['XBeeSensor(%s): ' % self.__name]

        # Parse the I/O sample:
        io_sample = parse_is(buf)
        
        # Calculate sensor channel values:
        if io_sample.has_key("AD1") and io_sample.has_key("AD2") and io_sample.has_key("AD3"):
            light_mv, temperature_mv, humidity_mv = \
                map(lambda cn: sample_to_mv(io_sample[cn]), ("AD1", "AD2", "AD3"))

            #
            # handle temperature - first as celsius
            #
            scale = "F"
            temperature = (((temperature_mv - 500.0) / 10.0) * (1.8) ) + 32
            if not SettingsBase.get_setting(self, "sleep"):
                # self-heating correction if running full-time - reduce 2 DegC
                temperature -= .001
            temperature = round(temperature, 2)
            
                
    
            self.property_set("temperature", Sample(0, temperature, scale))
            if do_trace:
                msg.append( "%d %s" % (temperature, scale))
    
            #
            # handle the light value
            #
            light = round((light_mv / 10), 2)
            if light < 0:
                # clamp to be zero or higher
                light = 0
            self.property_set("light", Sample(0, light, "F"))
            if do_trace:
                msg.append( ", %d brightness" % light)
    
            #
            # handle humidity - might be missing
            #
            if self.property_exists("humidity"):
                humidity = ((humidity_mv * 108.2 / 33.2) / 5000.0 - 0.16) / 0.0062
                if humidity < 0.0:
                    # clamp to min of 0%
                    humidity = 0.0
                elif humidity > 100.0:
                    # clamp to be max of 100%
                    humidity = 100.0
                self.property_set("humidity", Sample(0, humidity, "%"))
                if do_trace:
                    msg.append( ", %d RH%%" % humidity)
            else: # it remains the original default
                humidity = 0

        # Low battery check (attached to DIO11/P1):
        # Invert the signal it is actually not_low_battery:
        if io_sample.has_key("DIO11"):
            low_battery = not bool(io_sample["DIO11"])
            if low_battery != bool(self.property_get("low_battery").value):
                self.property_set("low_battery", Sample(0, low_battery))
    
            if do_trace:
                if low_battery:
                    msg.append( ", low_battery")
                # try to keep memory use from dragging out
                msg = "".join( msg)
                print msg
                del msg

        temp = self.property_get("temperature").value
        SettingsBase.set_pending_setting(self, 'temp', temp)
        
        
        


        return
    

    
    
    
    def update_power_state(self, chan):
        # Perform power control:
        self.prop_set_power_control(chan.get())
 
    def prop_set_power_control(self, bool_sample):

        if bool_sample.value:
            ddo_io_value = 5 # on
            self.__power_on_time = time.time()
        else:
            ddo_io_value = 4 # off


        extended_address = SettingsBase.get_setting(self, "extended_address")
        try:
            self.__xbee_manager.xbee_device_ddo_set_param(
                                    extended_address, 'D4', ddo_io_value,
                                    apply=True)
        except:
            pass

        self.property_set("power_on",
            Sample(0, Boolean(bool_sample.value, style=STYLE_ONOFF)))

# internal functions & classes

def main():
    pass

if __name__ == '__main__':
    import sys
    status = main()
    sys.exit(status)

