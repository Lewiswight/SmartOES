


msg = """<sci_request version="1.0"><send_message><targets><device id="00000000-00000000-00409DFF-FF52299D"/></targets><rci_request version="1.1"><do_command target="dia"><data><channel_set name="gate_[00:13:a2:00:40:31:56:96]!.activate" value="On"/></data></do_command></rci_request></send_message></sci_request>"""

from xml.dom.minidom import parseString

e = parseString(msg)
deviceList = e.getElementsByTagName('device')
MAC = deviceList[0].attributes['id'].value
MAC = MAC.replace("00000000-00000000-", "") 
MAC = MAC.replace("FF-FF", "")
print MAC
data = e.getElementsByTagName('do_command') 
print data
data = data[0].childNodes
print data
data = data[0].toxml()

print data
data = str(data)

"""import MySQLdb 

myDB = MySQLdb.connect(host="ec2-50-16-188-172.compute-1.amazonaws.com", port=3306, user="dane", passwd="WjDPqJPIl40c")

db=myDB.cursor()
db.execute("USE mistaway_channels")
db.execute("SHOW TABLES")
tables = db.fetchall()

for (table_name,) in db:
        print(table_name)"""



#results=cHandler.fetchall()
#print "=========================", "<br>"
#for items in results:
#   print items[0]







"""import urllib




url = "http://devbuildinglynx.apphb.com/api/gateway?checkmac=00409DFF-FF3F2E7D&dummy1=0&dummy2=1" 
         
try:
    f = urllib.urlopen(url)
except:
   print "Error opening url"

    
    
    
    
    
    
s = f.read()
print s


listenting on 2 ports 
AES 128 bit set up
key has been shared semetric key
all data must be encripted.
unique ID, timestamp, semicolon demilited 
AES 128 bit encription """





"""offset = ""
place_temp = s.find("gmt_offset")
temp_offset = s[place_temp + 12 : place_temp + 20]
for i in temp_offset:
    if i != ",":
        offset = offset + i 
    else:
        break
offset = int(offset)
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
print dst"""