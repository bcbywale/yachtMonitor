import os
import threading
import time
from tkinter import ttk

import serial
import socketserver

import tkinter as tk
import tkinter.scrolledtext as tkst
import xml.etree.ElementTree as ET

configDir = os.path.dirname(__file__)
configFilename = os.path.join(configDir, 'config.xml')
configTree = ET.parse(configFilename)
configRoot = configTree.getroot()

#Serial Port Thread
def read_from_port(ser, hVoltage):
		while True:
			reading = ser.readline().decode()
			print(reading)

#TCPhandler Class
class TCPHandler(socketserver.BaseRequestHandler):
	global dataStr

	def handle(self):
		data = str(self.request.recv(2048).strip())
		dataStr.set(data)
		#hvoltageG.valuetext.set(data)
		data = data.replace("'","")
		parsedData = data.split(",")
		hVoltage.value = float(parsedData[1])
		hVoltage.update(hVoltage.value)
		hAmp.value = float(parsedData[2])
		hAmp.update(hAmp.value)
		sVoltage.value = float(parsedData[3])
		sVoltage.update(sVoltage.value)

#wrapper to start a threaded TCP server
class ThreadedTCPServer(socketserver.ThreadingMixIn,socketserver.TCPServer):
	pass

#Function to read xml configuration
def loadConfig():
	global configTree, configRoot
	configTree = ET.parse(configFilename)
	configRoot = configTree.getroot()

#Configure GUI
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

#Alarm Class TODO: Going to need to expand class to be an alarm point so that alarms are associated with variables!
class AlarmPoint(object):
	def __init__(self, value=None, lowerLimit=None, upperLimit=None, units=None, meterType=None, lowerText=None, upperText=None, status=None, alarmType=None, buzzer=None, display = False, source = None):
		self.value = value
		self.lowerLimit = lowerLimit
		self.upperLimit = upperLimit
		self.lowerText = lowerText #text describing a low alarm
		self.upperText = upperText #text describing a high alarm
		self.status = status #is alarm still active? 1 yes 0 no
		self.alarmType = alarmType #is alarm a warning or a fault, faults cannot be removed by acknoledgement, 1 is fault, 0 is warning
		self.buzzer = buzzer #Should this alarm cause the buzzer to ring
		self.display = display #has this been displayed?
		self.source = source #did this alarm come from the sensor or the monitor
		self.units = units #What units should we put after the values
		self.meterType = meterType

	def ack(self):
		if self.alarmType == 1:
			status = 0
			buzzer = False
		else:
			buzzer = False

	def description(self):
		descString = ""
		if self.alarmType == 0:
			descString ="  Fault: "
		if self.alarmType == 1:
			descString ="Warning: "
		descString = descString + self.text
		return descString

	def makeBarMeter(self,Frame,x,y,title):
		#hVoltage = tk.StringVar()

		self.Frame = Frame
		self.barCanvas = tk.Canvas(self.Frame,width=250, height=75)
		self.valuetext = tk.StringVar()

		#Build hVoltageGuage and add Static Components
		self.barCanvas.grid(column=x, sticky=(tk.NW))
		self.barCanvas.create_rectangle(20,20,220,50)
		self.barCanvas.create_text(125,10,text=title)
		self.barCanvas.create_text(20,60,text=str(self.lowerLimit)+self.units)
		self.barCanvas.create_text(220,60,text=str(self.upperLimit)+self.units)
		self.valueFill = self.barCanvas.create_rectangle(21,21,220,50,fill="green",width=0)

	def update(self, value):
		#check for alarm condition
		if self.value < self.lowerLimit and self.lowerText != None:
			self.status = 1
			self.barCanvas.itemconfigure(self.valueFill,fill="red")
			if self.display == False:
				alarmText.insert(1.0, self.lowerText)
				acknButton.state(["!disabled"])
				self.display = True
				self.buzzer = True
		elif self.value > self.upperLimit and self.upperText != None:
			self.status = 1
			self.barCanvas.itemconfigure(self.valueFill,fill="red")
			if self.display == False:
				alarmText.insert(1.0, self.upperText)
				self.display = True
				self.buzzer = True
		else:
			self.status = 0
			self.barCanvas.itemconfigure(self.valueFill,fill="green")
			self.dislpay = False
			self.buzzer = False

		if self.meterType == "bar":
			barValue = 20+((self.value-self.lowerLimit)/(self.upperLimit-self.lowerLimit))*(220-20)
			if barValue > 220:
				barValue = 220
			elif barValue < 20:
				barValue = 21
			self.barCanvas.coords(self.valueFill,21,21,barValue,50)

#Fucntion to review alarms when acknoleg buttons is pressed
def reviewAlarms():
	for alarm in alarmPoints:
		if alarm.buzzer  == True:
			alarm.buzzer = False
			alarm.display = False
	alarmText.delete(,"end")
	acknButton.config(style='TButton')
	acknButton.state(["disabled"])

alarmPoints = []

#define external alarms
hVoltage = AlarmPoint(0.0,11.8,12.7,"V","bar","House bank voltage low.\n","House bank voltage high.",1,0,False,False,"Monitor")
alarmPoints.append(hVoltage)
hAmp = AlarmPoint(0.0,0,50,"A","bar","Low A alarm.","House amp draw exceeding 50 A\n",1,0,False,False,"Monitor")
alarmPoints.append(hAmp)
sVoltage = AlarmPoint(0.0,11.8,12.7,"V","bar","Starting bank voltage low.\n","Starting bank voltage high.",1,0,False,False,"Monitor")
alarmPoints.append(sVoltage)

j = 0

def update():
	global j, dataStr

	#Update the time
	timeStr = time.strftime("%I:%M:%S",time.localtime(time.time()))
	timeLabel.configure(text="Time: " +timeStr)
	for alarm in alarmPoints:
		if alarm.buzzer == True:
			color = alarmText.cget("background")
			next_color = "white" if color == "red" else "red"
			alarmText.config(background=next_color)
		else:
			alarmText.config(background = "white")

	#Update the values
	#hVoltageCanvas.itemconfig(hVoltageRecLabel,text=hVoltage.get())

	#===========================================================================
	# #Update the alarms
	# alarmText.config(state=tk.NORMAL)
	# alarmText.delete(1.0,tk.END)
	# for item in alarms:
	# 	if item.status == 1:
	# 		alarmText.insert(1.0, item.description())
	# 	if item.display == False:
	# 		item.display = True
	# 	if item.buzzer == 1:
	# 		acknButton.config(style='acknButton.TButton')
	# 		acknButton.state(["!disabled"])
	# alarmText.config(state=tk.DISABLED)
	# j = j + 1
	#===========================================================================

	timeLabel.after(1000, update)

HOST, PORT = "localhost", 9999

if __name__ == "__main__":
	#Before we do anything, let's load the configuration
	loadConfig()

	#Setup Serial connection based on config file
	try:
		ser = serial.Serial(port =3, baudrate=9600)
		print("connected to: " + ser.portstr)
		connectionStatus = "serial"
	except serial.SerialException:
		connectionStatus = "TCP"
		print("No serial connection available. Trying TCP")
		t = ThreadedTCPServer((HOST, PORT), TCPHandler)

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
	menubar.add_command(label="Quit!", command=root.quit())
	root.config(menu=menubar)

	hVoltage.makeBarMeter(mainframe,0,0,"House Voltage")
	hAmp.makeBarMeter(mainframe,0,1,"House Amp Draw")
	sVoltage.makeBarMeter(mainframe,0,2,"Start Voltage")


	alarmFrame = ttk.LabelFrame(mainframe, text="Alarm Summary",padding=(6, 6, 12, 12))
	alarmFrame.grid(column=0, sticky=tk.NSEW, columnspan=2) #no row called out means it will be first unused row
	alarmFrame.grid_columnconfigure(0, weight=1)
	#alarmFrame.grid_columnconfigure(1, weight=1)
	alarmFrame.grid_rowconfigure(0, weight=1)

	alarmText = tkst.ScrolledText(alarmFrame,width=100,height=3)
	alarmText.grid(row=0,column=0,sticky=tk.NSEW)


	acknButtonStyle = ttk.Style()
	acknButtonStyle.configure('acknButton.TButton', foreground="red")

	acknButton = ttk.Button(alarmFrame,  text="Ackn", command=reviewAlarms, state=tk.DISABLED)
	acknButton.grid(row=0, column=1, sticky=tk.NS )

	dataStr = tk.StringVar()
	dataLabel = ttk.Label(mainframe)
	dataLabel.grid(column = 0, row = 4, sticky=(tk.W))
	dataLabel.configure(textvariable=dataStr)

	timeLabel = ttk.Label(mainframe)
	timeLabel.grid(column=1,row=4,sticky=(tk.E))

	#if serial connection is available start thread listening to it
	if connectionStatus == "serial":
		thread = threading.Thread(target=read_from_port, args=(ser, alarmPoints))
		thread.daemon = True
		thread.start()
	#if serial connection is not available start thread listening to TCP server
	elif connectionStatus == "TCP":
		server_thread = threading.Thread(target=t.serve_forever)
		server_thread.daemon = True
		server_thread.start()
		print("Server loop running in thread:", server_thread.name)

	update()
	root.mainloop()
