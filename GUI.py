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
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(400,300))
        self.InitWind()
        self.Centre()
        self.Show()
    
    def InitWind(self):
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.uidText = wx.StaticText(panel,label="Access ID: ")
        self.uidInput = wx.TextCtrl(panel)
        
        hbox.Add(self.uidText, flag=wx.RIGHT,border=8)
        hbox.Add(self.uidInput,proportion=1,border = 30)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.pwdText = wx.StaticText(panel,label="Secret Key: ")
        self.pwdInput = wx.TextCtrl(panel)
        
        hbox2.Add(self.pwdText, flag=wx.RIGHT,border=8)
        hbox2.Add(self.pwdInput,proportion=1,border = 30)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.SubmitButton = wx.Button(panel,-1,"Submit")
        self.SubmitButton.Bind(wx.EVT_BUTTON,self.OnSubmit)
        
        hbox3.Add(self.SubmitButton,wx.CENTER,border=10)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        panel.SetSizer(vbox)
        
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Show()
    
    def OnClose(self,e):
        dlg = wx.MessageDialog(None,'Are you sure you want to quit?','Question',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    
        ret = dlg.ShowModal()
    
        if ret== wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()

    def OnSubmit(self,e):
        
        id = self.uidInput.GetValue()
        secret_key = self.pwdInput.GetValue()
        print "Submit has been clicked. Key is %s. Password is %s" % (id, secret_key)
        
         #Call the MTurkConnection function - if valid next screen, else dialoguebox
        if id=="abc":
            self.IncorrectCredentials()
            self.uidInput.Clear()
            self.pwdInput.Clear()
        else:
            print "logged in"
       
    def IncorrectCredentials(self):
        dlg = wx.MessageDialog(None,'Incorrect Credentials. Please try again.','Incorrect Credentials',wx.OK | wx.ICON_ERROR)
        
        ret = dlg.ShowModal()
        
        if ret== wx.OK:
            e.Veto()


if __name__ == '__main__':
    app = wx.App(False)
    MainWindow = Window(None,-1,"Crowd Captioners")
    
    
    app.MainLoop()