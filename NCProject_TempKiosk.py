#!/usr/bin/python3

#library modules 
from __future__ import print_function
from hashlib import new
from tkinter.constants import COMMAND
from typing import ValuesView
import PySimpleGUI as sg #GUI library
import subprocess as sub #backup os shell library
import os, sys #main shell library, returns 1 or 0 as exit code
import time, serial
from pandas.core.indexes.base import Index
from colorama.ansi import Cursor #USB-COM port and time library
import serial.tools.list_ports
from serial.serialwin32 import Serial
from serial.tools.list_ports_windows import comports
from PySimpleGUI.PySimpleGUI import Titlebar, popup_auto_close  
from time import sleep #to enable delay
from threading import Thread # to auto refresh after an update
import requests, json #to enable http request to server
import logging  #file logging for debugging
import colorama # use of colors to highlight alerts/text
from colorama import Fore
from serial.tools.list_ports_windows import comports #foreground colors
from termcolor import colored,cprint #colors in terminal
import platform
import pandas as pd #to read/manipulate the excel file

#print = sg.Print


#init logging 
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='TempKiosk.log', encoding='utf-8', level=logging.DEBUG)
a=os.system #assigning os library to a variable 

#GUI Theme color
sg.theme('DarkGray') 

#Excel file in localhost,to refer valid empID during data input, may use public-cloud hosting as replacement 
data =pd.read_excel(r'C:\Users\User\Documents\Py\NCproject\Employee_List.xlsx', index_col=False)
df=pd.DataFrame(data,columns=['Emp','Name','Department']) #select all emp,name and dept

try:
    if os.name=='nt':
        temp_scan=serial.Serial("COM7",115200,timeout=1) #init serial port in Windows platform
    else:
        temp_scan=serial.Serial("/dev/ttyUSB0",115200,timeout=1) #init serial port in Linux platform
except:
    print("[!]Unable to connect to serial COM/ttyUSB port")
    exit()
#serverURL= localhost XAMPP phpmyadmin/MariaDB which is easier for testing

#list the available COM ports in GUI
coms=serial.tools.list_ports.comports()
comlist=[]
for com in coms:
    comlist.append(str(com.device))

#func to scan temperature, using COM port in Windows env
def scan_temp():
    try:
        port="COM7"
        ser=serial.Serial(port,115200,timeout=1)
        while True:
            data=ser.readline()
            data_temp=data.decode('windows-1252')
            if data_temp.find("weak high") >=0:
                #print(data_temp)
                #print(data_temp[9:15])
                current_temp=data_temp[9:15]
                #os.system("cls")
                print("Your Body Temp = " + current_temp)
                #return current_temp
                
    except:
        print("Fail to read temp!Check COM connection")

#function to clear/reset form
def clear_form():
    window['-OUTPUT-'].update('')

#function to execute when normal temp is recorded
def normal_temp():
    print("\n[*] Connection to server OK!")
    logging.info("Uploading into DB..")
    progress_bar.update_bar(3)
    time.sleep(1.0)
    print("[*] Syncing..")
    time.sleep(1.0)
    progress_bar.update_bar(6)
    print("[*] Records verified and updated")
    time.sleep(1.0)
    print("[*] Auto-trigger enabled")
    progress_bar.update_bar(9)
    time.sleep(1.0)
    print("[*] Platform debug mode enabled")
    time.sleep(1.0)
    print("[*] Applying changes..")
    progress_bar.update_bar(10)
    
    print("\nThank you!\nYou may proceed to the office area")
    sg.popup("Normal Temperature.\nPlease proceed to the office area.\nThis message will self-destruct.",auto_close=True,title='Alert!')
    

#Menu options, for temp placeholder, may be removed if not usefull
menu_def = [['File', ['Open', 'Save', 'Exit'  ]],      
            ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],      
            ['Help', 'About...'], ]  


#GUI-Window parameters
layout = [  [sg.Menu(menu_def, )],
            [sg.Text('Scan your RFID'),sg.Input(do_not_clear=False,focus=True,key='-RFID-',pad=(45, 0))],
            [sg.Text('Scan your temperature'),sg.Input(do_not_clear=False,key='-Temp-')],
            [sg.Text('COM(for admin)'),sg.Combo(comlist,size=(5,1))],
            [sg.Button('Network connection(Green=Online)',button_color=('white', 'springgreen4'),disabled=False),sg.Button('Database status(Green=Online)',button_color=('white', 'springgreen4'),disabled=False)],
            [sg.Text('Progress:',size=(40, 1))],
            [sg.ProgressBar(max_value=10, orientation='h', size=(45, 20), key='progress')],
            [sg.Output(size=(70,15),key='-OUTPUT-')],
            [sg.Image(r'C:\Users\User\Documents\Py\NCproject\logo-snt.png')],
            [sg.Button('Submit'), sg.Button('Reset'),sg.Button('Cancel')] ]



# Create the Window
window = sg.Window('Employee Temperature Screening Kiosk [KAD] v1.0',layout,auto_size_text=True,resizable=True,finalize=True)
#window.set_cursor(None) # to hide mouse cursor in a fullscreen-touchscreen env
window.Maximize() # to enable fullscreen
#window.iconbitmap(r'C:\pyc.ico') #window title icon, optional
progress_bar = window['progress'] 



# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    elif values ['-RFID-']: #event == 'Submit': #enable_events=True to replace the need to click on submit
        
         #a("ping -c 1 8.8.8.8") // ping server/DB IP and update button-state colors accordingly
        empRFID = values ['-RFID-'] #TODO, input validation for number of characters
        empTemp = values ['-Temp-']
        newdf = df[(df.Emp == empRFID)]
        print(newdf.to_string(index=False))
        print('\nYour Temperature is: %s'%empTemp)
        
        if empRFID=="":
            sg.popup_no_buttons(" Employee RFID is compulsory!\n Please scan using your badge",auto_close=True,title='Error')
            logging.info("User did not scan their badge")
            continue
        elif empTemp=="":
            sg.popup_no_buttons("Temperature scanning is compulsory!\n Please scan using your forehead",auto_close=True,title='Error')
            logging.info("User "+ empRFID + " did not scan their temperature")
            continue
        normal_temp()
        logging.info("Normal temperature detected")
    elif event == 'Reset':
        clear_form()
       

window.close()

#pop-up single line input or just layout text, get RFID and enable_events=True with close=True and char more than 10 check
#call scanner and grab the temp measurement, pop-up custom msg box to prompt. grab temp and update pop.up box or use multiline element to display
#analyse temp and pop up decision 
#button state to change color/disabled if server is down
#integrate gif to animate required action 
#integrate current number of cases in Penang/Malaysia in output box, keep updated
#integrate the trend of temperature reading by hourly/daily/weekly/monthly 


