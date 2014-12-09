import tkinter as tk
from tkinter import ttk
import time
import serial
import xml.etree.ElementTree as ET
import os
import tkinter.scrolledtext as tkst
import threading

configDir = os.path.dirname(__file__)
configFilename = os.path.join(configDir, 'config.xml')
configTree = ET.parse(configFilename)
configRoot = configTree.getroot()

#Setup Serial connection based on config file
try:
    ser = serial.Serial(port =3, baudrate=9600)
    print("connected to: " + ser.portstr)
except serial.SerialException:
    print("No serial connection available")

def read_from_port(ser, hVoltage):
        while True:
            reading = ser.readline().decode()
            hVoltage.set(reading)

def loadConfig():
    global configTree, configRoot
    configTree = ET.parse(configFilename)
    configRoot = configTree.getroot()

def configure():

    window = tk.Toplevel()
    label = tk.Label(window,text="Configuration")
    label.pack(side="top", fill="both", padx=10, pady=10)
    #build interface to adjust configuration of connection to arduino

    #OK button should reload config on the way out
    loadConfig()

    #DEBUG
    for child in configRoot:
        print(child.tag, child.attrib)

#Before we do anything, let's load the configuration
loadConfig()

def update():
    #Update the time
    timeStr = time.strftime("%I:%M:%S",time.localtime(time.time()))
    timeLabel.configure(text="Time: " +timeStr)
    timeLabel.after(1000, update)
    
    #Update the values
    hVoltageLabel.configure(text="House Bank Voltage = " + hVoltage.get())
    print(hVoltage.get())
    
    #Update the guages
    
    #Update the alarms
    alarmText.config(state=tk.NORMAL)
    #Display only alarms that haven't been displayed before
    #Start as unankloweded and alarming
    #Check for awklodgement
    #Clear when possible after being awklodged
    #alarmText.insert('1.0', "COM port not available\n")
    #alarmText.insert('1.0', "Fuel low\n")
    alarmText.config(state=tk.DISABLED)
    
if __name__ == "__main__":

    root = tk.Tk()
    root.grid_rowconfigure(0,weight=1)
    root.grid_columnconfigure(0,weight=1)

    root.title("Yacht Monitor V0.1")
    dir = os.path.dirname(__file__)
    root.iconbitmap(default=os.path.join(dir, 'icon.ico'))
    
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(tk.NSEW))
    mainframe.grid_columnconfigure(0, weight=1)
    mainframe.grid_rowconfigure(0, weight=1)

    menubar = tk.Menu(root)
    menubar.add_command(label="Configure", command=configure)
    menubar.add_command(label="Quit!", command=root.quit)
    root.config(menu=menubar)

    hVoltage = tk.StringVar()
        
    #Build hVoltageGuage and add Static Components
    hVoltageCanvas = tk.Canvas(mainframe,width=300, height=100)
    hVoltageCanvas.grid(column=0, row =0, sticky=(tk.NW))
    hVoltageCanvas.create_rectangle(10,10,300,50)

    hVoltageLabel = ttk.Label(mainframe, text="House Bank Voltage = " +hVoltage.get())
    hVoltageLabel.grid(column=0, row=1,sticky=(tk.NW))

    alarmFrame = ttk.LabelFrame(mainframe, text="Alarm Summary",padding=(6, 6, 12, 12))
    alarmFrame.grid(column=0,row=2, sticky=tk.NSEW, columnspan=2)
    alarmFrame.grid_columnconfigure(0, weight=1)
    alarmFrame.grid_rowconfigure(0, weight=1)
    
    alarmText = tkst.ScrolledText(alarmFrame,width=100,height=5)
    alarmText.grid(row=0,column=0,sticky=tk.NSEW)


    timeLabel = ttk.Label(mainframe)
    timeLabel.grid(column=1,row=4,sticky=(tk.W))

    #for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
    thread = threading.Thread(target=read_from_port, args=(ser, hVoltage))
    thread.daemon = True
    thread.start()
    update()
    root.mainloop()
