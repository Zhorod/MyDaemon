#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import paho.mqtt.publish as mqtt_publish
#import paho.mqtt.client as mqtt
#import paho.mqtt.client as mqtt_client
import json

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

class simpleapp_wx(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title='MyDaemonGUI')
        self.parent = parent
        self.initialize()
        self.move1 = 0.4
        self.move2 = 0.7
        self.move3 = 0.9
        self.move4 = 1.3
        self.rotate1 = 0.15
        self.rotate2 = 0.2
        self.rotate3 = 0.3
        self.rotate4 = 0.6


    def initialize(self):

        # init MQTT client
        #self.client = paho.client("client-001")
        #self.client.connect("test.mosquitto.org")

        sizer = wx.GridBagSizer()

        f1button = wx.Button(self, -1, label="F1", size=(30,30))
        sizer.Add(f1button, (3, 4))
        self.Bind(wx.EVT_BUTTON, self.OnF1ButtonClick, f1button)

        f2button = wx.Button(self, -1, label="F2", size=(30,30))
        sizer.Add(f2button, (2, 4))
        self.Bind(wx.EVT_BUTTON, self.OnF2ButtonClick, f2button)

        f3button = wx.Button(self, -1, label="F3", size=(30,30))
        sizer.Add(f3button, (1, 4))
        self.Bind(wx.EVT_BUTTON, self.OnF3ButtonClick, f3button)

        f4button = wx.Button(self, -1, label="F4", size=(30,30))
        sizer.Add(f4button, (0, 4))
        self.Bind(wx.EVT_BUTTON, self.OnF4ButtonClick, f4button)

        b1button = wx.Button(self, -1, label="B1", size=(30,30))
        sizer.Add(b1button, (5, 4))
        self.Bind(wx.EVT_BUTTON, self.OnB1ButtonClick, b1button)

        b2button = wx.Button(self, -1, label="B2", size=(30,30))
        sizer.Add(b2button, (6, 4))
        self.Bind(wx.EVT_BUTTON, self.OnB2ButtonClick, b2button)

        b3button = wx.Button(self, -1, label="B3", size=(30,30))
        sizer.Add(b3button, (7, 4))
        self.Bind(wx.EVT_BUTTON, self.OnB3ButtonClick, b3button)

        b4button = wx.Button(self, -1, label="B4", size=(30,30))
        sizer.Add(b4button, (8, 4))
        self.Bind(wx.EVT_BUTTON, self.OnB4ButtonClick, b4button)

        l1button = wx.Button(self, -1, label="L1", size=(30,30))
        sizer.Add(l1button, (4, 3))
        self.Bind(wx.EVT_BUTTON, self.OnL1ButtonClick, l1button)

        l2button = wx.Button(self, -1, label="L2", size=(30,30))
        sizer.Add(l2button, (4, 2))
        self.Bind(wx.EVT_BUTTON, self.OnL2ButtonClick, l2button)

        l3button = wx.Button(self, -1, label="L3", size=(30,30))
        sizer.Add(l3button, (4, 1))
        self.Bind(wx.EVT_BUTTON, self.OnL3ButtonClick, l3button)

        l4button = wx.Button(self, -1, label="L4", size=(30,30))
        sizer.Add(l4button, (4, 0))
        self.Bind(wx.EVT_BUTTON, self.OnL4ButtonClick, l4button)

        r1button = wx.Button(self, -1, label="R1", size=(30,30))
        sizer.Add(r1button, (4, 5))
        self.Bind(wx.EVT_BUTTON, self.OnR1ButtonClick, r1button)

        r2button = wx.Button(self, -1, label="R2", size=(30,30))
        sizer.Add(r2button, (4, 6))
        self.Bind(wx.EVT_BUTTON, self.OnR2ButtonClick, r2button)

        r3button = wx.Button(self, -1, label="R3", size=(30,30))
        sizer.Add(r3button, (4, 7))
        self.Bind(wx.EVT_BUTTON, self.OnR3ButtonClick, r3button)

        r4button = wx.Button(self, -1, label="R4", size=(30,30))
        sizer.Add(r4button, (4, 8))
        self.Bind(wx.EVT_BUTTON, self.OnR4ButtonClick, r4button)


        #self.label = wx.StaticText(self,-1,label=u'Hello !')
        #self.label.SetBackgroundColour(wx.BLUE)
        #self.label.SetForegroundColour(wx.WHITE)
        #sizer.Add( self.label, (1,0),(1,2), wx.EXPAND )

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1,self.GetSize().y,-1,self.GetSize().y );
        self.Show(True)

    def OnF1ButtonClick(self,event):

        #mqttBroker = "test.mosquitto.org"
        #mqttBroker = "mqtt.eclispeprojects.io"

        #client = mqtt.Client("mydaemon/move")
        #print("set up client")
        #client.connect(mqttBroker);
        #print("connected")
        #qa_json = {"command": "forward", "distance": self.move1}
        #qa_string = json.dumps(qa_json)
        #client.publish("mydaemon/move", qa_string)

        qa_json = {"command": "forward", "distance": self.move1}
        qa_string = json.dumps(qa_json)
        try:
            #self.client.publish("mydaemon/move", qa_string)  # publish
            mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        except:
            print("mgtt_publish_single returned an error in OnF1ButtonCLick")
        print("JSON published: ", qa_string)

    def OnF2ButtonClick(self, event):
        qa_json = {"command": "forward", "distance": self.move2}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnF3ButtonClick(self,event):
        qa_json = {"command": "forward", "distance": self.move3}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnF4ButtonClick(self,event):
        qa_json = {"command": "forward", "distance": self.move4}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnB1ButtonClick(self,event):
        qa_json = {"command": "back" , "distance": self.move1}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnB2ButtonClick(self, event):
        qa_json = {"command": "back", "distance": self.move2}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnB3ButtonClick(self,event):
        qa_json = {"command": "back", "distance": self.move3}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnB4ButtonClick(self,event):
        qa_json = {"command": "back", "distance": self.move4}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnL1ButtonClick(self,event):
        qa_json = {"command": "left" , "distance": self.rotate1}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnL2ButtonClick(self, event):
        qa_json = {"command": "left", "distance": self.rotate2}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnL3ButtonClick(self,event):
        qa_json = {"command": "left", "distance": self.rotate3}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnL4ButtonClick(self,event):
        qa_json = {"command": "left", "distance": self.rotate4}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnR1ButtonClick(self,event):
        qa_json = {"command": "right" , "distance": self.rotate1}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnR2ButtonClick(self, event):
        qa_json = {"command": "right", "distance": self.rotate2}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnR3ButtonClick(self,event):
        qa_json = {"command": "right", "distance": self.rotate3}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def OnR4ButtonClick(self,event):
        qa_json = {"command": "right", "distance": self.rotate4}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)


if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None,-1,'my application')

    app.MainLoop()