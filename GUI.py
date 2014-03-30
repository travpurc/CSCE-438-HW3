'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Vishal Anand, Ricardo Zavala

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
import YouTube
import threading

#-------------------------------
#-------- Config Globals -------
#-------------------------------

# Define video length, and declare arrays handling video information
embedded_video_length = 10;         #Embedded video length is n+1 watch time
video_start = []                    #Arrays of the sequential start and end times
video_end = []
embedded_urls = []

# Because of the way how the validation is implemented, the number of segments (assignments)
# MUST be 2!  (It was what the team decided during a meeting, anyhow)
assignmentNum = 2                   #Number of times the videos will be captioned
validationNum = 1                   #Number of times the Caption HITs will validated

#-------------------------------
#---------- Functions ----------
#-------------------------------

# Helper function to initialize the accepted_answers array
def initialize_captions(HIT_IDs):
    fixed_array = []
    number_of_hits = len(HIT_IDs)
    for r in xrange(0, number_of_hits):
        fixed_array.append([HIT_IDs[r], ""])
        fixed_array.append([HIT_IDs[r], ""])
    return fixed_array

#-------------------------------
#----------- Windows -----------
#-------------------------------
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
        except :
            print 'error'
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
#TODO: Here, code to open up a file can be implemented
#if loading up a file, first line is the HITTypeId and the following lines are the HITIds
#creating HIT_IDs would only require each of the HITIds to a string array
#and skip from here---------------
        url = self.panel2.vidInput.GetValue()
        #url = "http://www.youtube.com/watch?v=KaqC5FnvAEc"
        data_title = YouTube.GetYouTubeData(url, embedded_video_length, embedded_urls, video_start, video_end)
        count = len(embedded_urls)
        total_time = video_end.pop()
        video_end.append(total_time)
        HIT_IDs = HITGeneration.GenerateCaptionHIT(self.mtc, count, assignmentNum, embedded_urls, data_title)
#---------------to here
        print HIT_IDs
        Completed_HITs = initialize_captions(HIT_IDs)    #Used to link caption and validation HITs
        Accepted_Answers = [None]*len(HIT_IDs)           #Used to build the SRT File

        dlg = wx.GenericProgressDialog("Progress", "Loading...", maximum=count, parent=None, style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL)
        start(CaptionAndValidate.CaptionAndValidationLoop, dlg,self.mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)
        dlg.ShowModal()

        print "Completed Hits: "
        print Completed_HITs
        print "Accepted Answers: "
        print Accepted_Answers
        SRTGenerator.GenerateSRT(data_title, total_time, embedded_video_length, video_start, video_end, Completed_HITs, Accepted_Answers)

    def OnReset(self,e):
        dlg = wx.MessageDialog(None,'Are you sure you want to delete all previous HITs?','Question',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dlg.ShowModal()

        if ret== wx.ID_YES:
            Reset = self.mtc.get_all_hits()
            for hit in Reset:
                self.mtc.disable_hit(hit.HITId)
                print "Old HIT: " + hit.HITId + " - Disabled"

        #e.Veto() #return to previous screen

def start(func, *args): # helper method to run a function in another thread
    thread = threading.Thread(target=func, args=args)
    thread.setDaemon(True)
    thread.start()

if __name__ == '__main__':
    app = wx.App(False)
    FirstWindow = FirstWindow(None,-1,"Crowd Captioners")
    FirstWindow.Show(True)
    app.MainLoop()
