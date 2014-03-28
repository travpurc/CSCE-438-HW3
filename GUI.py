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
from boto.mturk.connection import MTurkConnection
import HITGeneration
import SRTGenerator
import CaptionAndValidate
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
        self.SetBackgroundColour(wx.Colour(191,239,255))
    
    def InitWind(self):
        
        self.panel1 = panels.FirstPanel(self)
        self.panel2 = panels.SecondPanel(self)
        self.panel2.Hide()
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.Add(self.panel1,1,wx.EXPAND)
        vSizer.Add(self.panel2,1,wx.EXPAND)
        self.SetSizer(vSizer)
    
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
        print 'Submit has been clicked. Key is %s' %id
        print 'Password is %s' %secret_key
         #Call the MTurkConnection function - if valid next screen, else dialoguebox
        HOST = 'mechanicalturk.sandbox.amazonaws.com'
        try:
            self.mtc = MTurkConnection(aws_access_key_id=id, aws_secret_access_key=secret_key,host=HOST)
            #Display balance for user
            print self.mtc.get_account_balance()
            print "logged in"
            self.panel1.Hide()
            self.panel2.Show()
            self.Layout()
        except mtc.MTurkRequestError as err:
            print 'error', err.code
            self.IncorrectCredentials()
            self.panel1.uidInput.Clear()
            self.panel1.pwdInput.Clear()


    def IncorrectCredentials(self):
        dlg = wx.MessageDialog(None,'Incorrect Credentials. Please try again.','Incorrect Credentials',wx.OK | wx.ICON_ERROR)
        
        ret = dlg.ShowModal()
        
        if ret== wx.OK:
            e.Veto()

    def OnCaption(self,e):
        print "caption the video"
        count = 1
        assignmentNum = 2
        embedded_urls  = ['http://www.youtube.com/watch?v=KaqC5FnvAEc']
        HIT_IDs = HITGeneration.GenerateCaptionHIT(self.mtc, count, assignmentNum, embedded_urls)
        Completed_HITs = []         #Used to link caption and validation HITs
        Accepted_Answers = []       #Used to build the SRT File
        CaptionAndValidate.CaptionAndValidationLoop(self.mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)
        
        print "Completed Hits: "
        print Completed_HITs
        print "Accepted Answers: "
        print Accepted_Answers
        e.Veto()


if __name__ == '__main__':
    app = wx.App(False)
    FirstWindow = FirstWindow(None,-1,"Crowd Captioners")
    FirstWindow.Show(True)
    app.MainLoop()