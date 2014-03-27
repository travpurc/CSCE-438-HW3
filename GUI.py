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
import GUI
import CaptionAndValidate
import wx
import Tkinter, tkFileDialog

#TODO: Merge HW3 into this file or visa versa
class FirstPanel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self,parent,wx.ID_ANY)
        self.parent = parent
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.uidText = wx.StaticText(self,label="Access ID: ")
        self.uidInput = wx.TextCtrl(self)
        
        hbox.Add(self.uidText, flag=wx.RIGHT,border=8)
        hbox.Add(self.uidInput,proportion=1,border = 30)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.pwdText = wx.StaticText(self,label="Secret Key: ")
        self.pwdInput = wx.TextCtrl(self)
        
        hbox2.Add(self.pwdText, flag=wx.RIGHT,border=8)
        hbox2.Add(self.pwdInput,proportion=1,border = 30)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.SubmitButton = wx.Button(self,-1,"Submit")
        self.SubmitButton.Bind(wx.EVT_BUTTON,parent.OnSubmit)
        
        hbox3.Add(self.SubmitButton,wx.CENTER,border=10)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        self.SetSizer(vbox)
        self.GetParent().Layout()

class SecondPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,wx.ID_ANY)
        self.parent = parent
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.vidText = wx.StaticText(self,label="Youtube Link: ")
        self.vidInput = wx.TextCtrl(self)
        
        hbox.Add(self.vidText, flag=wx.RIGHT,border=8)
        hbox.Add(self.vidInput,proportion=1,border = 30)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.dirText = wx.StaticText(self,label="Save Location: ")
        self.dirInput = wx.TextCtrl(self)
        self.selectdir = wx.Button(self,-1,"Dir")
        self.selectdir.Bind(wx.EVT_BUTTON,self.DisplayDirDlg)

        hbox2.Add(self.dirText, flag=wx.RIGHT,border=8)
        hbox2.Add(self.dirInput,proportion=1,border = 30)
        hbox2.Add((10,-1))
        hbox2.Add(self.selectdir,proportion=0,border=30)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        vbox.Add((-1,10))
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.CaptionButton = wx.Button(self,-1,"Caption!")
        self.CaptionButton.Bind(wx.EVT_BUTTON,parent.OnCaption)
        
        hbox3.Add(self.CaptionButton,wx.CENTER,border=10)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        self.SetSizer(vbox)
    
    def DisplayDirDlg(self,e):
        print 'selecting directory'
        #dirdlg = wx.MessageDialog(None,"Select Directory",style=wx.DD_DEFAULT_STYLE)
#test = EasyDialogs.AskFolder()

#Windows
#  root = Tkinter.Tk()
#       dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",titl='Please select a directory')
#       if len(dirname ) > 0:
#           print "You chose %s" % dirname
#ret = dirdlg.ShowModal()
    



class FirstWindow(wx.Frame):
    
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(400,300))
        self.InitWind()
        self.Centre()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    #self.Show()
    
    def InitWind(self):
        
        self.panel1 = FirstPanel(self)
        # self.panel1.Show()
        self.panel2 = SecondPanel(self)
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
            #self.panel2 = SecondPanel(self)
            self.panel2.Show()
            self.Layout()
            #self.Destroy()
       
    def IncorrectCredentials(self):
        dlg = wx.MessageDialog(None,'Incorrect Credentials. Please try again.','Incorrect Credentials',wx.OK | wx.ICON_ERROR)
        
        ret = dlg.ShowModal()
        
        if ret== wx.OK:
            e.Veto()

    def OnCaption(self,e):
        print "Time to caption the video"


if __name__ == '__main__':
    app = wx.App(False)
    FirstWindow = FirstWindow(None,-1,"Crowd Captioners")
    #SecondWindow = Window(None,-1,"Crowd Captioners")
    FirstWindow.Show(True)
    app.MainLoop()