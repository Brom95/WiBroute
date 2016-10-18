#!/usr/bin/env python3
'''
Created on 13.10.2016

@author: Brom
@e-mail: wasalev@mail.ru
'''
import wifi
from wifi import Cell, Scheme
i=0
w_list=[]
for cell in Cell.all('wlp3s0'):
	print("["+str(i)+"] "+cell.ssid+" | "+str(cell.channel)+" | "+cell.address)
	w_list.append(cell)
	i+=1
cell=int(input("choose wirless: "))
# print(w_list[cell])
scheme = Scheme.for_cell('wlp3s0', w_list[cell].ssid, w_list[cell], "")
scheme.delete()
scheme.save()
scheme.activate()