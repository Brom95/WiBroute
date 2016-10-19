import subprocess
# return list of all available Network-Device Names 
def interfacesList():
	return subprocess.check_output("ifconfig -a | sed 's/[ \t].*//;/^$/d'", shell=True).decode("utf-8")[:-1].split("\n")

def interfaceUp(interface="lo"):
	subprocess.run("ifconfig "+interface+" up", shell=True, check=True)

def interfaceDown(interface="lo"):
	subprocess.run("ifconfig "+interface+" down", shell=True, check=True)

def wifiList(interface="lo"):
	sysOut=subprocess.check_output("iwlist "+interface+" scan", shell=True).decode("utf-8")[:-1].split("Cell ")

	resultList=[]

	for cell in sysOut:
		cellDic={}
		
		for line in cell.split("\n"):
			if line.find("Address:")>=0:
				cellDic['Address']=line.split("Address: ")[1]
			elif line.find("Channel:")>=0:
				cellDic['Channel']=line.split("Channel:")[1]
			elif line.find("Frequency:")>=0:
				cellDic['Frequency']=line.split("Frequency:")[1]
			elif line.find("Signal level=")>=0:
				cellDic['Signal level']=line.split("Signal level=")[1]
			elif line.find("Encryption key:")>=0:
				cellDic['Encryption key']=line.split("Encryption key:")[1]
			elif line.find("ESSID:")>=0:
				cellDic['ESSID']=line.split("ESSID:")[1]
		if len(cellDic)>0:
			resultList.append(cellDic)
	return resultList
def tryConnect(ssid, password, interface):
	try:
		sysOut=subprocess.check_output("nmcli d wifi connect "+ssid+" password "+password.replace("!","\\!")+" iface "+ interface, shell=True).decode("utf-8")[:-1]
	except:
		return False
	if sysOut.find('successfully')>0:
		return True
	else:
		return False