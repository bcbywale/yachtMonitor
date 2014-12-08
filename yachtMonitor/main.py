import tkinter as tk
from tkinter import ttk
from time import sleep
import serial
import xml.etree.ElementTree as ET
import os

configDir = os.path.dirname(__file__)
configFilename = os.path.join(configDir, 'config.xml')
configTree = ET.parse(configFilename)
configRoot = configTree.getroot()

#Setup Serial connection based on config file
ser = serial.Serial(3)
ser.baudrate = 9600

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set((0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

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
    root.update()
    reading.set(ser.readline())
    sleep(1)

if __name__ == "__main__":

    root = tk.Tk()

    root.title("Yacht Monitor V0.1")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    menubar = tk.Menu(root)
    menubar.add_command(label="Configure", command=configure)
    menubar.add_command(label="Quit!", command=root.quit)
    root.config(menu=menubar)

    feet = tk.StringVar()
    meters = tk.StringVar()
    reading = tk.StringVar()

    feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
    feet_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))

    ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(tk.W, tk.E))
    ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=tk.W)

    ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=tk.W)
    ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=tk.E)
    ttk.Label(mainframe, text=reading).grid(column=3, row=2, sticky=tk.W)

    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    feet_entry.focus()

    root.after(1, update)
    root.mainloop()
