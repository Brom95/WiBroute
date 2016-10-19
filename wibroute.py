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
net_wrap.targetsList(curInt)