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

hVoltageFloat = 0.0

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

j = 0

def update():
	global j, hVoltageFloat

	#Update the time
	timeStr = time.strftime("%I:%M:%S",time.localtime(time.time()))
	timeLabel.configure(text="Time: " +timeStr)
	timeLabel.after(1000, update)

	#Update the values
	hVoltageCanvas.itemconfig(hVoltageRecLabel,text=hVoltage.get())
	
	if hVoltageFloat < 12.0:
		alarms.append(Alarm("House bank voltage low.\n",1,0,1,False,"Monitor"))
	
	print(hVoltageFloat)
	#Update the guages
	if hVoltageFloat >12.7:
		recColor = 10
	elif hVoltageFloat >12.6:
		recColor = 9
	elif hVoltageFloat >12.5:
		recColor = 8
	elif hVoltageFloat >12.4:
		recColor = 7
	elif hVoltageFloat >12.3:
		recColor = 6
	elif hVoltageFloat >12.2:
		recColor = 5
	elif hVoltageFloat >12.1:
		recColor = 4
	elif hVoltageFloat >12.0:
		recColor = 3
	elif hVoltageFloat >11.9:
		recColor = 2
	elif hVoltageFloat >11.8:
		recColor = 1
	else:
		recColor = 0
 		
	for i, rec in enumerate(hVoltageRec): 
		if i < recColor: 
			hVoltageCanvas.itemconfig(hVoltageRec[i],fill="green")

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
	j = j + 1
	if j == 10:
		alarms.append(Alarm("10 Seconds has elapsed\n",1,1,1,False,"Monitor"))

if __name__ == "__main__":

	#generator list of alarms
	alarms = []

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

	mainframe = ttk.Frame(root, padding="5 5 12 12")
	mainframe.grid(column=0, row=0, sticky=(tk.NSEW))
	mainframe.grid_columnconfigure(0, weight=1)
	mainframe.grid_columnconfigure(1, weight=1)
	mainframe.grid_rowconfigure(0, weight=1)

	menubar = tk.Menu(root)
	menubar.add_command(label="Configure", command=configure)
	menubar.add_command(label="Quit!", command=root.quit)
	root.config(menu=menubar)

	hVoltage = tk.StringVar()
	
	hVoltageRec = []
	
	#Build hVoltageGuage and add Static Components
	hVoltageCanvas = tk.Canvas(mainframe,width=500, height=100)
	hVoltageCanvas.grid(column=0, row =0, sticky=(tk.NW))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(20,20,40,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(40,20,60,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(60,20,80,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(80,20,100,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(100,20,120,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(120,20,140,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(140,20,160,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(160,20,180,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(180,20,200,50))
	hVoltageRec.append(hVoltageCanvas.create_rectangle(200,20,220,50))
	
	hVoltageRecTitle = hVoltageCanvas.create_text(125,10,text="House Bank Voltage")
	hVoltageRecLabel = hVoltageCanvas.create_text(230,35,text=hVoltage.get(), anchor = tk.W)
	hVoltageRecLabelMin = hVoltageCanvas.create_text(20,60,text="11.7 V")
	hVoltageRecLabelMax = hVoltageCanvas.create_text(220,60,text="12.8 V")


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
	timeLabel.grid(column=1,row=4,sticky=(tk.E))

	#if serial connection is available start thread listening to it
	if connectionStatus == "serial":
		thread = threading.Thread(target=read_from_port, args=(ser, hVoltage))
		thread.daemon = True
		thread.start()

	update()
	root.mainloop()
