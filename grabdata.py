import netmiko
import re
import csv
import xlsxwriter
import pandas as pd
import datetime
import getpass
nodenum = 1
# Update your pathto a CSV file with your nodes in it - just IP address in list #
device=open('/Python/PythonProjects/ciscoautomation/newplan/nodeip.csv','r')
c=device.readlines()
now = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

##### Getpass used so you do not need to hardcode the password into the configuration file ####
def get_credentials():
    username = input("Enter username: ")
    password = getpass.getpass()
    return username, password   

# update to your directory, this assumes Outputs.csv is always the same as we convert it to XLS later #
with open('/Python/PythonProjects/ciscoautomation/newplan/output/Outputs.csv', 'w', newline='') as device:
    username, password = get_credentials()
    write = csv.writer(device)
    write.writerow(['Hostname', 'IP Address', 'ConfigUsers', 'BGP', "VTY", "EIGRP", "Software Version", "Show AAA", "Interfaces"])
    for i in c:
        print("Node", nodenum, " - Checking IP -", i)
        try:
            connection = netmiko.ConnectHandler(ip=i, device_type="cisco_ios", username=username, password=password, secret=password)
        except:
            try:
                print("Cannot connect via SSH - Trying Telnet")
                connection = netmiko.ConnectHandler(ip=i, device_type="cisco_ios_telnet", username=username, password=password, secret=password)

            except:
                print("Cannot Connect via SSH or Telnet, check the device is up or if its using non standard connections, logging to error.log")
                print("")
                nowfull = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                logf = open("/Python/PythonProjects/ciscoautomation/newplan/output/error.log", "a")
                logf.write(nowfull)
                logf.write(" - Cannot Connect via SSH or Telnet to - ")
                nodenum = nodenum + 1
                logf.write(i)
                logf.close()
                continue
        #hostname = (connection.send_command("show run | include ^hostname"))
        hostname = connection.send_command("show run | inc hostname ").split()[1]

        configUsers = (connection.send_command("show run | inc username"))
        bgp = (connection.send_command("show run | sec bgp"))
        vty = (connection.send_command("show run | sec vty"))
        eigrp = (connection.send_command("show run | sec eigrp"))
        #showver = (connection.send_command("show ver | inc Software"))
        swver = (connection.send_command("show version | inc Software"))
        pattern = re.compile(r"Version (\S+)")
        version_match = pattern.search(swver)
        print ("Software Version = " + version_match.group(1))
        swverreg = version_match.group(1)



        showaaa = (connection.send_command("show run | sec aaa"))
        Interfaces = (connection.send_command("show ip int brief | exc unassigned"))
        nodenum = nodenum + 1
        connection.disconnect()
        print(hostname)
        write.writerow([hostname, i, configUsers, bgp, vty, eigrp, swverreg, showaaa, Interfaces])
        print("\n\n")
    device.close()

# make sure the below matches line 21's path and filename
# Reading the csv file
df_new = pd.read_csv('/Python/PythonProjects/ciscoautomation/newplan/output/Outputs.csv')

# make sure you update the path accordingly for the XLS file 
# saving xlsx file
GFG = pd.ExcelWriter('/Python/PythonProjects/ciscoautomation/newplan/output/Outputs'+now+'.xlsx')
df_new.to_excel(GFG, index=False)
 
GFG.save()
