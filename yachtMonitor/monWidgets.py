'''
Created on 21 Dec,2014

@author: bryan.bywalec
'''

class monWidgets(object, type,x,y ):
    '''
    classdocs
    '''


    def __init__(self, params):
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
