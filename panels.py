import wx
class FirstPanel(wx.Panel):
    
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,wx.ID_ANY)
        self.parent = parent
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.introText = wx.StaticText(self,label="\t\t\tWelcome to Crowd Caption\n\t\tPlease enter your credentials to continue.")
        
        self.uidText = wx.StaticText(self,label="Access ID: ")
        self.uidInput = wx.TextCtrl(self)
        
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(self.introText,wx.CENTER,border=50)
        vbox.Add(hbox0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1,30))
        
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
        
        self.introText = wx.StaticText(self,label="\t\tPost a link to the Youtube Video you want captioned\n and chose a directory to save your .srt file.")
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(self.introText,wx.CENTER,border=50)
        vbox.Add(hbox0,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1,30))
        
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
        dirdlg = wx.DirDialog(None,"Select Directory",style=wx.DD_DEFAULT_STYLE)
        ret = dirdlg.ShowModal()
        if ret == wx.ID_OK:
            path = dirdlg.GetPath()
            self.dirInput.SetValue(path)
        else:
            path = None
        dirdlg.Destroy()

