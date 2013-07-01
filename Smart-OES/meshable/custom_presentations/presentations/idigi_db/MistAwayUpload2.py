
"""
iDigi Database Synchronization Module
"""

# imports
import sys
from socket import *
from devices.xbee.common.addressing import *
from devices.xbee.common.ddo import retry_ddo_get_param
from devices.device_base import DeviceBase
from devices.xbee.xbee_devices.xbee_base import XBeeBase
from settings.settings_base import SettingsBase, Setting
from channels.channel_source_device_property import *
from rci import process_request

from settings.settings_base import SettingsBase, Setting
from presentations.presentation_base import PresentationBase
from samples.sample import Sample
from common.helpers.format_channels import iso_date
from common.digi_device_info import get_platform_name
from common.digi_device_info import get_device_id
from devices.xbee.xbee_device_manager.xbee_device_manager_event_specs \
    import *

import threading
from threading import Lock
import time
#import Queue
import cStringIO

import sys



import os


import httplib
#import digicli

try:
    from rci import process_request
except:
    print "DEBUG RCI IN PLACE, are you running on a PC?"
    mem = 500000
    # For debugging on a PC
    def process_request(s):
        global mem
        print s
        mem -= 100000
        print mem
        return '''\
<rci_reply version="1.1">
    <query_state>
        <device_stats>
            <cpu>3</cpu>
            <uptime>3307</uptime>
            <datetime>Mon Sep 28 10:59:38 2009</datetime>
            <totalmem>16777216</totalmem>
            <freemem>%d</freemem>
        </device_stats>
    </query_state>
</rci_reply>''' % mem



# constants
SM_TEMPLATE1 = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <XMLparser xmlns="http://houselynx.com/webservices">
      <XMLdump>"""

SM_TEMPLATE2 = """</XMLdump>
    </XMLparser>
  </soap:Body>
</soap:Envelope>"""

          # ("infobel", "test")
ADDRESS_A = """<gateway>"""
        
ADDRESS_B = """</gateway>"""
        
        
        
        
#status, output = digicli.digicli('show net')
        
 
#if status:
#    for line in output:
#        if line.find('MAC Address') >= 0:
#            l = line.split(':')
#            st = "".join(l[1:]).strip()
                    
MAC = str(get_device_id())  #st
MAC = MAC.replace("0x0000000000000000", "")
MAC = MAC.replace("ffff", "")
MAC = MAC.upper()
print "Here is the MAC"
print MAC


# constants
ENTITY_MAP = {
    "<": "<",
    ">": ">",
    "&": "&amp;",
}

# exception classes

# interface functions

# classes

class f_counter:

      
    def __init__(self,):
        self.count = 0

        

class Uploader(PresentationBase, threading.Thread):

      
    def __init__(self, name, core_services):

       self.__name = name
       self.__core = core_services
       self.__event_timer = None
       self.__stopevent = core_services
       self.connected =  0
       self.trigger = 0
       cached_gw_address_tuple = None
       self.__xbee_manager = None
       self.filename = "file"
       self.filenumber = 0
       self.sending = False 
       self.send = False# True if I'm in the proccess of doing an uplaod
       #self.upload_lock = Lock() #lock for the upload

        # Settings
        #
        # interval: is the maximum interval in seconds that this module waits 
        #     before sending data to the iDigi Manager Database.
        # sample_threshold: is the mininum number of samples required before
        #     sending data to the iDigi Manager Database.
        # collection: is the collection on the database where the data will
        #     be stored.
        # file_count: the number of unique files we will keep on iDigi.
        # filename: the name of the xml file we will push to iDigi, with
        #     a number appended to the end (cycling from 1 to file_count)
        # channels: is the list of channels the module is subscribed to.
        #     If no channels are listed, all channels are subscribed to.
        # compact_xml: (when set to True) will produce output XML with the 
        #     information stored as attributes to the sample node instead of
        #     separately tagged, resulting in smaller XML output.
  
       settings_list = [
          Setting(
                name='xbee_device_manager', type=str, required=False, default_value="xbee_device_manager"),
          Setting(
             name='interval', type=int, required=False,
            default_value=60),
          Setting(
             name='sample_threshold', type=int, required=False,    
            default_value=10),
          Setting(
             name='collection', type=str, required=False,
             default_value=""),
          Setting(
             name="channels", type=list, required=False,
             default_value=[]),
          Setting(
             name='count', type=int, required=False,
             default_value=20),
          Setting(
             name='filename', type=str, required=False,
             default_value="sample"),
          Setting(
             name='secure', type=bool, required=False,
             default_value=True),
          Setting(
             name='compact_xml', type=bool, required=False,
             default_value=False),
       ]

       
       PresentationBase.__init__(self, name=name,
                                  settings_list=settings_list)
       self.__stopevent = threading.Event()
       threading.Thread.__init__(self, name=name)
       threading.Thread.setDaemon(self, True)

    def start(self):
        

        # Verify that the user has a reasonable iDigi host set on their device.
  

        # Start by appending 1 to filename of pushed data
        self.__current_file_number = 1

        # Event to use for notification of meeting the sample threshold
        self.__threshold_event = threading.Event()

        # Count of samples since last data push
        self.__sample_count = 0
        
        self.fc = f_counter()
        self.__core.set_service("fc", self.fc)

        # Here we grab the channel publisher
        channels = SettingsBase.get_setting(self, "channels")
        cm = self.__core.get_service("channel_manager")
        cp = cm.channel_publisher_get()

        # And subscribe to receive notification about new samples
    #    if len(channels) > 0:
    #        for channel in channels:
    #            cp.subscribe(channel, self.receive)
    #    else:
    #        cp.subscribe_to_all(self.receive)

        threading.Thread.start(self)
        self.apply_settings()
        return True


    def stop(self):
        self.__stopevent.set()
        return True

    def apply_settings(self):
        
        SettingsBase.merge_settings(self)
        accepted, rejected, not_found = SettingsBase.verify_settings(self)

        if len(rejected) or len(not_found):
            # There were problems with settings, terminate early:
            print "idigi_db (%s): Settings rejected/not found: %s %s" % \
                (self.__name, rejected, not_found)
            return (accepted, rejected, not_found)

        # Verify that if we are on the Digi ConnectPort X3, that the user
        # doesn't have the secure option set to True.
        # If they do, we MUST bail here and also warn the user that the
        # Digi ConnectPort X3 cannot do secure/encrypted idigi connections.
        if accepted['secure'] == True and get_platform_name() == 'digix3':
            print "idigi_db (%s): The Digi ConnectPort X3 product cannot " \
                  "do secure/encrypted connections to the iDigi Server.  " \
                  "Please set the 'secure' option to False!" % \
                                (self.__name)

            rejected['secure'] = accepted['secure']
            del accepted['secure']
            return (accepted, rejected, not_found)

        SettingsBase.commit_settings(self, accepted)
        
       # xbee_manager_name = SettingsBase.get_setting(self, "xbee_device_manager")
        dm = self.__core.get_service("device_driver_manager")
        self.__xbee_manager = dm.instance_get("xbee_device_manager")
        
        self.__last_upload_time = 0
        
        
       # self.repeat()
        
        
        return (accepted, rejected, not_found)

    

    
    
    
    
    def repeat(self):
        interval = SettingsBase.get_setting(self, "interval")
        
        if self.__event_timer is not None:
            try:
                self.__xbee_manager.xbee_device_schedule_cancel(
                    self.__event_timer)
            except:
                pass
            
        self.__event_timer = self.__xbee_manager.xbee_device_schedule_after(
                SettingsBase.get_setting(self, "interval"),
                self.repeat)
        
        
        
        try:
            self.send = True
            #self.my_queue.put(1)
        except:
            self.connected += 1
            print "error in sending from repeat function"
        
        
        
        
        
        
        
    
    
    def receive(self, channel):
        
        # Check how many samples it takes to meet the sample threshold
        sample_threshold = SettingsBase.get_setting(self, "sample_threshold")
        
        self.__sample_count += 1

        # print "idigi_db (%s): Received sample %i" % \
        #       (self.__name, self.__sample_count)

        # If we have exceeded the sample threshold, notify the thread
        # responsible for pushing up data
        if self.__sample_count >= sample_threshold:
            print "idigi_db (%s): Reached threshold of %i, setting event flag" % \
                   (self.__name, sample_threshold)
            self.__threshold_event.set()

    def run(self):
        
        try:
            count = 0
        
            #self.my_queue = Queue.Queue(maxsize=5)
            print "queue in uploader started"
            
            while True:
                
                count += 1
        
                #msg = self.my_queue.get()
                
                if self.send == True:
                    #if self.sending == False:
                    #if self.upload_lock.acquire(0) == False:
                        #time.sleep(3)
                        #continue
                    if self.sending == False:
                        self.__upload_data()
                        #self.upload_lock.release()
                        self.send = False
                    time.sleep(3)
                else:
                    time.sleep(5)
                    
                if count > 10:
                    count = 0
                    self.send = True
        except:
            print "rebooting now from MA uploader, see ya"
            process_request('<rci_request><reboot /></rci_request>')
                
                    
            
           
        
        #interval = SettingsBase.get_setting(self, "interval")
        
   #     self.__last_upload_time = 0
   #     while not self.__stopevent.isSet():
   #         try:
   #             print "idigi_db (%s): I'm waiting for an event or up to " \
   #                   "%i seconds" % (self.__name, interval)
   #             self.__threshold_event.wait(interval)
   #             print "idigi_db (%s): I'm done waiting" % (self.__name)
#
 #               self.__sample_count = 0
  #              self.__threshold_event.clear()
   #             
    #            self.__upload_data()
     #       except Exception, e:
      #          print "idigi_db (%s): exception while uploading: %s" % \
       #             (self.__name, str(e))


     #   print "idigi_db (%s): Out of run loop.  Shutting down..." % \
     #          (self.__name)
    def upload_data(self):
        
        #self.my_queue.put(1)
        self.send = True
        
    
    def __upload_data(self):
        
        now_time = time.time() 
        
        if self.sending == True:
            self.send = True
            return
        
        self.sending = True
        
        success = True
        
        xml = cStringIO.StringIO()
        
    #    xml.write("<?xml version=\"1.0\"?>")
        compact_xml = SettingsBase.get_setting(self, "compact_xml")    
        if compact_xml:
            xml.write("<idigi_data compact=\"True\">")
        else:
            xml.write("<idigi_data>")
        
        cm = self.__core.get_service("channel_manager")
        self.cdb = cm.channel_database_get()
        
        

        channel_list = SettingsBase.get_setting(self, "channels")
        if len(channel_list) == 0:
            channel_list = self.cdb.channel_list()

        new_sample_count = 0
      #  print channel_list

        for channel_name in channel_list:
           # print channel_name
           if self.trigger == 0:
                try:
                    channel = self.cdb.channel_get(channel_name) 
                    sample = channel.get()
                #    print channel_name 
                 #   print sample.unit
                 #   print sample.value 
                    if sample.timestamp >= self.__last_upload_time and sample.timestamp >= 1315351499.0 and sample.unit != "1":  
                        print "idigi_db (%s): Channel %s was updated since last " \
                               "push" % (self.__name, channel_name)
                        new_sample_count += 1
                        compact_xml = SettingsBase.get_setting(self, "compact_xml")    
                        if compact_xml:
                            xml.write(self.__make_compact_xml(channel_name, sample))
                        else:
                            xml.write(self.__make_xml(channel_name, sample))
                    else:
                       pass
                     #  print "idigi_db (%s): Channel %s was not updated since " \ 
                     #         "last push" % (self.__name, channel_name)
                except Exception, e:
                    # Failed to retrieve the data
                    print "idigi_db (%s): Exception in getting sample data: %s" \
                           % (self.__name, str(e))
           if self.trigger == 1:
                print "sending full uplaod"
                try:
                    channel = self.cdb.channel_get(channel_name) 
                    sample = channel.get()

                    if sample.timestamp >= 1315351499.0 and sample.unit != "1":
                        new_sample_count += 1
                        compact_xml = SettingsBase.get_setting(self, "compact_xml")    
                        if compact_xml:
                            xml.write(self.__make_compact_xml(channel_name, sample))
                        else:
                            xml.write(self.__make_xml(channel_name, sample))
                
                except Exception, e:
                    # Failed to retrieve the data
                    print "idigi_db (%s): Exception in getting sample data: %s" \
                           % (self.__name, str(e))
                    

        if self.trigger == 1:
            self.trigger = 0
        
        
        xml.write("</idigi_data>")

        if new_sample_count > 0:
            print "idigi_db (%s): Starting upload to HouseLynx" % (self.__name)
            try:
                self.__last_upload_time = now_time
                success = self.__send_to_idigi(xml.getvalue())
            except:
                success = False
                self.connected += 1
                print "could not send to HouseLynx"
            if success == True:
                print "idigi_db (%s): Finished upload to HouseLynx" % (self.__name)
                if self.connected > 0:
                    self.trigger = 1
                  #  DeviceBase.property_set("f_count", Sample(0, value=str(average), unit="aF"))
                    print "number of failed tries"
                    print self.connected
                    self.fc.count = self.connected
                    
                    
                self.connected = 0
            else:
                self.connected += 1
                print "idigi_db (%s): Upload failed to HouseLynx" % (self.__name)
        else:
            print "idigi_db (%s): No new Sample data to send to HouseLynx" % \
                   (self.__name)

        xml.close()
        self.sending = False
        
        if self.connected > 10:
            print "rebooting due to too many failed uploads"
            process_request('<rci_request><reboot /></rci_request>')

    def __make_xml(self, channel_name, sample):

        data = "<sample>"
        data += "<name>%s</name>"
        data += "<value>%s</value>"
        data += "<unit>%s</unit>"
        data += "<timestamp>%s</timestamp>"
        data += "</sample>"

        return data % (channel_name, self.__escape_entities(sample.value),
                       sample.unit, self.convert_timestamp(sample.timestamp))


    def __make_compact_xml(self, channel_name, sample):

        data = "<sample name=\"%s\" value=\"%s\" unit=\"%s\" timestamp=\"%s\" />"

        return data % (channel_name, self.__escape_entities(sample.value),
                       sample.unit, self.convert_timestamp(sample.timestamp))
    
    def convert_timestamp(self, timestamp):
        
        sec_time = int(timestamp)
        main_addr = "mainMistaway_" + gw_extended_address()
        timezone = self.cdb.channel_get(main_addr + ".offset")
        timezone = timezone.get()
        timezone = timezone.value
        offset = int(timezone)
        time_here = sec_time + offset 
        return time_here

    def __send_to_idigi(self, data):

        success = True
        
        Message = ADDRESS_A + MAC + data + ADDRESS_B 
        
        
        print "message compiled" 
        
  
       
        send_error1 = "error sending message to Dane's web service"


        try:
       
            string = "{'postedValue':" + "'" + Message + "'" + "}"
            
            print string
            
          #  self.filenumber += 1
            
            
            
          #  file = str(self.filenumber)
            
          #  file2 = open("WEB/python/XML" + file + ".txt", "w")
            
          #  file2.write(string)
            
          #  file2.close()

            webservice = httplib.HTTP("devbuildinglynx.apphb.com")
            #    print "line 1"
            webservice.putrequest(unicode("POST", "utf-8" ), unicode("/api/fromGateway", "utf-8" ), "HTTP/1.1")
            #        webservice.putheader("POST", "/NumericUpDown.asmx", "" )
            #    print "line 2"
            webservice.putheader(unicode("Host", "utf-8" ), unicode("devbuildinglynx.apphb.com", "utf-8" ))
            #        webservice.putheader("User-Agent: ", "Python Post")
            #    print "line 3"
            webservice.putheader(unicode("Content-Type", "utf-8" ), unicode("application/json; charset=\"UTF-8\"", "utf-8" ))
            #    print "line 4"
            webservice.putheader(unicode("Content-Length", "utf-8" ), unicode("%d", "utf-8" ) % len(string))
            #   print "line 5"
            #webservice.putheader(unicode("SOAPAction", "utf-8" ), unicode("\"http://houselynx.com/webservices/XMLparser\"", "utf-8" ))
            #  print "line 6"
            webservice.endheaders()
            # print "line 7"
            webservice.send(unicode(string, "utf-8" ))
            
            statuscode, statusmessage, header = webservice.getreply()
            print "Response: ", statuscode, statusmessage
            print "headers: ", header
            res = webservice.getfile().read()
            print res
            
          #  file3 = open("WEB/python/Resp" + file + ".txt", "w")
            
          #  file3.write(res)
            
          #  file3.close()
            
            
            
            #print "line 8"
            # statuscode, statusmessage, header = webservice.getreply()
            #print "line 9"
            webservice.close()
      
        
            
        except:
            self.sending = False
            return False
        self.sending = False
        return success  

    def __escape_entities(self, sample_value):

        if not isinstance(sample_value, str):
            return sample_value
        for ch in ENTITY_MAP:
            sample_value = sample_value.replace(ch, ENTITY_MAP[ch])

        return sample_value


