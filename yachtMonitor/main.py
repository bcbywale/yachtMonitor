import os
import threading
import time
from tkinter import ttk

import serial

import tkinter as tk
import tkinter.scrolledtext as tkst
import xml.etree.ElementTree as ET


configDir = os.path.dirname(__file__)
configFilename = os.path.join(configDir, 'config.xml')
configTree = ET.parse(configFilename)
configRoot = configTree.getroot()

connectionStatus = "offline"

def read_from_port(ser, hVoltage):
		while True:
			reading = ser.readline().decode()
			hVoltage.set(reading)
			hVoltageFloat = float(reading)

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

#Alarm Class TODO: Going to need to expand class to be an alarm point so that alarms are associated with variables!
class Alarm(object):
	def __init__(self, text=None, status=None, type=None, buzzer=None, display = None, source = None):
		self.text = text #text describing the alarm
		self.status = status #is alarm still active? 1 yes 0 no
		self.type = type #is alarm a warning or a fault, faults cannot be removed by acknoledgement, 1 is fault, 0 is warning
		self.buzzer = buzzer #Should this alarm cause the buzzer to ring
		self.display = display #has this been displayed?
		self.source = source #did this alarm come from the sensor or the monitor

	def ack():
		if type == 1:
			status = 0
			buzzer = 0
		else:
			buzzer = 0

	def description(self):
		descString = ""
		if self.type == 0:
			descString ="  Fault: "
		if self.type == 1:
			descString ="Warning: "
		descString = descString + self.text
		return descString

#Fucntion to review alarms when acknoleg buttons is pressed
def reviewAlarms():
	for item in alarms:
		if item.display == True:
			item.buzzer = 0
			if item.type == 1:
				item.status = 0
	acknButton.config(style='TButton')
	acknButton.state(["disabled"])

i = 0

def update():
	global i

	#Update the time
	timeStr = time.strftime("%I:%M:%S",time.localtime(time.time()))
	timeLabel.configure(text="Time: " +timeStr)
	timeLabel.after(1000, update)

	#Update the values
	hVoltageLabel.configure(text="House Bank Voltage = " + hVoltage.get())
	if hVoltageFloat < 10:
		alarms.append(Alarm("House bank voltage low.\n",1,0,1,False,"Monitor"))

	#Update the guages

	#Update the alarms
	alarmText.config(state=tk.NORMAL)
	alarmText.delete(1.0,tk.END)
	for item in alarms:
		if item.status == 1:
			alarmText.insert(1.0, item.description())
		if item.display == False:
			item.display = True
		if item.buzzer == 1:
			acknButton.config(style='acknButton.TButton')
			acknButton.state(["!disabled"])
	alarmText.config(state=tk.DISABLED)
	i = i + 1
	if i == 10:
		alarms.append(Alarm("10 Seconds has elapsed\n",1,1,1,False,"Monitor"))

if __name__ == "__main__":

	#generator list of alarms
	alarms = []

	hVoltageFloat = 12.0

	#Setup Serial connection based on config file
	try:
		ser = serial.Serial(port =3, baudrate=9600)
		print("connected to: " + ser.portstr)
		connectionStatus = "serial"
	except serial.SerialException:
		print("No serial connection available")
		connectionStatus = "offline"

	if connectionStatus == "offline":
		alarms.append(Alarm("No connection available. Restart required to clear.",1,0,1,False,"Monitor"))

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
	#alarmFrame.grid_columnconfigure(1, weight=1)
	alarmFrame.grid_rowconfigure(0, weight=1)

	alarmText = tkst.ScrolledText(alarmFrame,width=100,height=3)
	alarmText.grid(row=0,column=0,sticky=tk.NSEW)

	acknButtonStyle = ttk.Style()
	acknButtonStyle.configure('acknButton.TButton', foreground="red")

	acknButton = ttk.Button(alarmFrame,  text="Ackn", command=reviewAlarms, state=tk.DISABLED)
	acknButton.grid(row=0, column=1, sticky=tk.NS )

	timeLabel = ttk.Label(mainframe)
	timeLabel.grid(column=1,row=4,sticky=(tk.W))

	#if serial connection is available start thread listening to it
	if connectionStatus == "serial":
		thread = threading.Thread(target=read_from_port, args=(ser, hVoltage))
		thread.daemon = True
		thread.start()

	update()
	root.mainloop()
