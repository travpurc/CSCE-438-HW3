'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Vishal Anand

Purpose: Contains GUI functions
'''
#-------------------------------
# ----------- Import -----------
#-------------------------------
#from boto.mturk.connection import MTurkConnection
#import HITGeneration
#import SRTGenerator
#import GUI
#import CaptionAndValidate
import wx
import Tkinter, tkFileDialog
import panels
#TODO: Merge HW3 into this file or visa versa

class FirstWindow(wx.Frame):
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(400,300))
        self.InitWind()
        self.Centre()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    #self.Show()
    
    def InitWind(self):
        
        self.panel1 = panels.FirstPanel(self)
        # self.panel1.Show()
        self.panel2 = panels.SecondPanel(self)
        self.panel2.Hide()
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.Add(self.panel1,1,wx.EXPAND)
        vSizer.Add(self.panel2,1,wx.EXPAND)
        self.SetSizer(vSizer)

#self.Layout()
    
    def OnClose(self,e):
        dlg = wx.MessageDialog(None,'Are you sure you want to quit?','Question',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    
        ret = dlg.ShowModal()
    
        if ret== wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()

    def OnSubmit(self,e):
        
        id = self.panel1.uidInput.GetValue()
        secret_key = self.panel1.pwdInput.GetValue()
        print "Submit has been clicked. Key is %s. Password is %s" % (id, secret_key)
            # mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
            #                 aws_secret_access_key=SECRET_KEY,
            #                 host=HOST)
         #Call the MTurkConnection function - if valid next screen, else dialoguebox
        if id=="abc":
            self.IncorrectCredentials()
            self.panel1.uidInput.Clear()
            self.panel1.pwdInput.Clear()
        else:
            print "logged in"
            self.panel1.Hide()
            self.panel2.Show()
            self.Layout()

    def IncorrectCredentials(self):
        dlg = wx.MessageDialog(None,'Incorrect Credentials. Please try again.','Incorrect Credentials',wx.OK | wx.ICON_ERROR)
        
        ret = dlg.ShowModal()
        
        if ret== wx.OK:
            e.Veto()

    def OnCaption(self,e):
        print "caption the video"


if __name__ == '__main__':
    app = wx.App(False)
    FirstWindow = FirstWindow(None,-1,"Crowd Captioners")
    FirstWindow.Show(True)
    app.MainLoop()