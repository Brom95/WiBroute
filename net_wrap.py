import subprocess
# return list of all available Network-Device Names 
def interfacesList():
	return subprocess.check_output("ifconfig -a | sed 's/[ \t].*//;/^$/d'", shell=True).decode("utf-8")[:-1].split("\n")

def interfaceUp(interface="lo"):
	subprocess.run("ifconfig "+interface+" up", shell=True, check=True)

def interfaceDown(interface="lo"):
	subprocess.run("ifconfig "+interface+" down", shell=True, check=True)