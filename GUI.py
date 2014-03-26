'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell

Purpose: Contains GUI functions
'''

import wx

class Window(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(500,500))
        self.InitWind()
        self.Centre()
        self.Show()
    
    def InitWind(self):
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        uidText = wx.StaticText(panel,label="Username: ")
        uidInput = wx.TextCtrl(panel)
        
        hbox.Add(uidText, flag=wx.RIGHT,border=8)
        hbox.Add(uidInput,proportion=1,border = 30)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        uidText = wx.StaticText(panel,label="Password: ")
        uidInput = wx.TextCtrl(panel)
        
        hbox2.Add(uidText, flag=wx.RIGHT,border=8)
        hbox2.Add(uidInput,proportion=1,border = 30)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        SubmitButton = wx.Button(panel,-1,"Submit")
        
        hbox3.Add(SubmitButton,border=10)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        panel.SetSizer(vbox)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    MainWindow = Window(None,-1,"Crowd Captioners")
    
    
    app.MainLoop()