import subprocess
# return list of all available Network-Device Names 
def interfacesList():
	return subprocess.check_output("ifconfig -a | sed 's/[ \t].*//;/^$/d'", shell=True).decode("utf-8").split("\n")