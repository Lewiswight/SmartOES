#####################################################################
# Automatically generated file
# Created on: 17 April 2013
# Author: lewiswight
#####################################################################

"""
    Custom iDigi Dia 'FCT' Device
    
    

"""

# imports
from devices.device_base import DeviceBase
from settings.settings_base import SettingsBase, Setting
from channels.channel_source_device_property import *

from devices.xbee.xbee_devices.xbee_base import XBeeBase
from devices.xbee.xbee_config_blocks.xbee_config_block_ddo \
    import XBeeConfigBlockDDO
from devices.xbee.xbee_device_manager.xbee_device_manager_event_specs \
    import *
from devices.xbee.common.addressing import *
from devices.xbee.common.prodid import PROD_DIGI_UNSPECIFIED

from devices.xbee.xbee_config_blocks.xbee_config_block_sleep \
    import SM_DISABLED, XBeeConfigBlockSleep

import threading
import time

# constants

# exception classes

# interface functions

# classes
class FCT(XBeeBase, threading.Thread):
    
    # Define a set of endpoints that this device will send in on.
    ADDRESS_TABLE = [ [0xe8, 0xc105, 0x92], [0xe8, 0xc105, 0x11] ]

    # The list of supported products that this driver supports.
    SUPPORTED_PRODUCTS = [ PROD_DIGI_UNSPECIFIED, ]

    def __init__(self, name, core_services):
        ## Initialize and declare class variables
        self.__name = name
        self.__core = core_services

        ## Local State Variables:
        self.__xbee_manager = None

        # Settings already defined and inherit from XBeeBase:
        #
        # xbee_device_manager: Must be set to the name of an XBeeDeviceManager
        #                      instance.
        # extended_address: Is the extended address of the XBee device you
        #                   would like to monitor.

        # Sleep Settings:
        #
        # sleep_ms: Number of milliseconds the XBee Board will be sleeping in 
        #           each sleep period. Minimum value for this setting is 320 
        #           ms, 0 means no sleep.
        # awake_time_ms: How long, in milliseconds, should the board stay 
        #                awake between each sleep period.

        ## Settings Table Definition:
        settings_list = [
            # Sleep Settings
              Setting(
                name='sleep_ms', 
                type=int, 
                required=False, 
                default_value=0, 
                verify_function=lambda x: x >= 320 or x == 0 
                     ),
              Setting(
                name='awake_time_ms', 
                type=int, 
                required=False, 
                default_value=1500, 
                verify_function=lambda x: x >= 0 and x <= 0xffff 
                     ),
            # TODO: Declare your device settings here. 
            #       Follow this pattern:
            # Setting(
            #   name="<setting_name>", 
            #   type=str/int/float/bool, 
            #   required=True/False, 
            #   default_value=<default_value>, 
            #   verify_function=<verification_method> (optional)
            #        ),
                         ]

        ## Channel Properties Definition:
        property_list = [
            # gettable properties
            # TODO: Declare your gettable channels here. 
            #       Follow this pattern:
            # ChannelSourceDeviceProperty(
            #   name="<channel_name>", 
            #   type=str/int/float/bool,
            #   initial=Sample(timestamp=0, value=<initial_value>),
            #   perms_mask=DPROP_PERM_GET, 
            #   options=DPROP_OPT_AUTOTIMESTAMP
            #                            ),
            #
            # settable properties
            # TODO: Declare your settable channels here. 
            #       Follow this pattern:
            # ChannelSourceDeviceProperty(
            #   name="<channel_name>", 
            #   type=str/int/float/bool,
            #   initial=Sample(timestamp=0, value=<initial_value>),
            #   perms_mask=(DPROP_PERM_GET|DPROP_PERM_SET), 
            #   options=DPROP_OPT_AUTOTIMESTAMP
            #   set_cb=<channel_set_callback>
            #                            ),
                         ]

        ## Initialize the XBeeBase interface:
        XBeeBase.__init__(self, self.__name, self.__core,
                                settings_list, property_list)

        ## Thread initialization:
        self.__stopevent = threading.Event()
        threading.Thread.__init__(self, name=name)
        threading.Thread.setDaemon(self, True)


    ## Functions which must be implemented to conform to the XBeeBase
    ## interface:
    @staticmethod
    def probe():
        #   Collect important information about the driver.
        #
        #   .. Note::
        #
        #       This method is a static method.  As such, all data returned
        #       must be accessible from the class without having a instance
        #       of the device created.
        #
        #   Returns a dictionary that must contain the following 2 keys:
        #           1) address_table:
        #              A list of XBee address tuples with the first part of the
        #              address removed that this device might send data to.
        #              For example: [ 0xe8, 0xc105, 0x95 ]
        #           2) supported_products:
        #              A list of product values that this driver supports.
        #              Generally, this will consist of Product Types that
        #              can be found in 'devices/xbee/common/prodid.py'

        probe_data = XBeeBase.probe()

        for address in FCT.ADDRESS_TABLE:
            probe_data['address_table'].append(address)
        for product in FCT.SUPPORTED_PRODUCTS:
            probe_data['supported_products'].append(product)

        return probe_data

    ## Functions which must be implemented to conform to the DeviceBase
    ## interface:
    def apply_settings(self):
        """
            Apply settings as they are defined by the configuration file.
        """
        
        SettingsBase.merge_settings(self)
        accepted, rejected, not_found = SettingsBase.verify_settings(self)
        if len(rejected) or len(not_found):
            print "Settings rejected/not found: %s %s" % (rejected, not_found)

        SettingsBase.commit_settings(self, accepted)

        return (accepted, rejected, not_found)

    def start(self):
        """
            Start the device object.
        """
        
        # Fetch the XBee Manager name from the Settings Manager:
        xbee_manager_name = SettingsBase.get_setting(self, "xbee_device_manager")
        dm = self.__core.get_service("device_driver_manager")
        self.__xbee_manager = dm.instance_get(xbee_manager_name)

        # Register ourselves with the XBee Device Manager instance:
        self.__xbee_manager.xbee_device_register(self)

        # Get the extended address of the device:
        extended_address = SettingsBase.get_setting(self, "extended_address")

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

        # TODO: Configure the XBee pins to be Digital/Analog IO
        #
        # I.E.: Configure pins DI0 .. DI3 for digital input and 
        #       enable line monitoring on pins DIO0 .. DIO3:
        #for io_pin in [ 'D0', 'D1', 'D2', 'D3' ]:
        #    xbee_ddo_cfg.add_parameter(io_pin, 3)
        # Enable I/O line monitoring on pins DIO0 .. DIO3:
        #xbee_ddo_cfg.add_parameter('IC', 0xf)
        #
        # I.E.: Configure pins DI1 .. DI3 for analog input:
        #for io_pin in [ 'D1', 'D2', 'D3' ]:
        #    xbee_ddo_cfg.add_parameter(io_pin, 2)

        # Configure node sleep behavior:
        sleep_ms = SettingsBase.get_setting(self, "sleep_ms")
        awake_time_ms = SettingsBase.get_setting(self, "awake_time_ms")
        xbee_sleep_cfg = XBeeConfigBlockSleep(extended_address)
        if sleep_ms > 0:
            # Configure node to sleep for the specified interval:
            xbee_sleep_cfg.sleep_cycle_set(awake_time_ms, sleep_ms)
        else:
            # If sleep_ms is 0, disable sleeping on the node altogether:
            xbee_sleep_cfg.sleep_mode_set(SM_DISABLED)

        # Register the Sleep configuration block with the XBee Device Manager:
        self.__xbee_manager.xbee_device_config_block_add(self, xbee_sleep_cfg)

        # Register the DDO configuration block with the XBee Device Manager:
        self.__xbee_manager.xbee_device_config_block_add(self, xbee_ddo_cfg)

        # Indicate that we have no more configuration to add:
        self.__xbee_manager.xbee_device_configure(self)

        # Start the thread
        threading.Thread.start(self)

        return True

    def stop(self):
        """
            Stop the device object.
        """
        
        self.__stopevent.set()

        return True

    ## Threading related functions:
    def run(self):
        
        while True:
            if self.__stopevent.isSet():
                self.__stopevent.clear()
                break

            # TODO: Perform your threading actions here.
            print "FCT(%s): threading action" % (self.__name)
            time.sleep(10)

# Internal functions & classes

    def running_indication(self):
        print "FCT(%s): running indication" % (self.__name)
        # Our device is now running
        # TODO: Perform initial operations.

    def sample_indication(self, buf, addr):
        print "FCT(%s): sample indication" % (self.__name)
        # Data received from the XBee device
        # TODO: Read and decode the data. Perform corresponding operations 
        #       depending on the data read such as changing channel values.

