try:
	import kivy

	from kivy.app import App

	from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
	from kivy.uix.behaviors import ButtonBehavior
	from kivy.clock import Clock

	from kivy.uix.button import Button
	from kivy.uix.label import Label
	from kivy.uix.checkbox import CheckBox
	from kivy.uix.textinput import TextInput
	from kivy.uix.widget import Widget

	from kivy.uix.gridlayout import GridLayout
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.floatlayout import FloatLayout
	from kivy.uix.scrollview import ScrollView
	from kivy.core.window import Window

	from kivy.uix.image import Image
	from kivy.uix.videoplayer import VideoPlayer
	from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle

	from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
	from kivy.uix.slider import Slider
	from kivy.uix.popup import Popup

	from functools import partial
	from random import shuffle, randint, choice, sample
	from datetime import datetime

	from os import makedirs
	from os.path import exists,dirname,isfile
	from shutil import copyfile

	from datetime import datetime
	import threading
	import time
	import webbrowser

	from json_funs import *
	from os_funs import *
	from image_funs import *

	import cv2
	import numpy as np
	from os.path import splitext

except:
	pass

def PreProcessing():
	global Info, NowFolder, NowFolders, RecFolders, RecJson
	Info = read_json("/home/nil/Nil/My Codes/Projects/FileExplorer/Database/BasicInfo.json")

	Info["Rec"] = read_json(Info["RecPath"])
	Info["Font"] = read_json(Info["FontPath"])
	NowFolder = 0
	NowFolders = [Info["HomeFolder"],Info["NowFolder"]]
	RecFolders = [[],[]]

def PostProcessing():
	global Info
	write_json(Info,"/home/nil/Nil/My Codes/Projects/FileExplorer/Database/BasicInfo.json")
	write_json(Info["Rec"],Info["RecPath"])

def GetImageButton(source,bsize,center,fun):
	MyImage = ImageButton(source=source,size_hint=(bsize[0],bsize[1]),pos_hint={"center_x":center[0],"center_y":center[1]},on_press=fun)
	return MyImage

def GetButton(text,bsize,center,fun):
	MyBtn = Button(text=text,size_hint=(bsize[0],bsize[1]),pos_hint={"center_x":center[0],"center_y":center[1]},halign='center',font_size=30,font_name=FontDict["LobsterTwo-BoldItalic"],on_press=fun)
	return MyBtn

class ImageButton(ButtonBehavior, Image):
	keep_ratio = BooleanProperty(True)
	allow_stretch = BooleanProperty(False)
	anim_delay = NumericProperty(0.05)

class HomeScreen(Screen):
	def __init__(self,**kwargs):
		super(HomeScreen,self).__init__(**kwargs)
		self.DefineView()
		self.DefineSpecials()

	def DefineSpecials(self):
		self.NumOfTabs = 1
		self.TimeAllow = 1
		self.LastClickTime = 1
		self.PointOn = -1
		self.LastCLickOn = "nothing"

	def DefineView(self):
		self.HomeW, self.HomeH = 0.099,0.099
		self.HomeX, self.HomeY = 0.15,0.95
		self.BackW, self.BackH = 0.099,0.099
		self.BackX, self.BackY = 0.05,0.95

		self.PathW, self.PathH = 0.599,0.099
		self.PathX, self.PathY = 0.5,0.95
		self.TabsW, self.TabsH = 0.799,0.0749
		self.TabsX, self.TabsY = 0.6,0.8625

		self.MainW, self.MainH = 0.599,0.8249
		self.MainX, self.MainY = 0.5,0.4125

		self.FavW, self.FavH = 0.199,0.8249
		self.FavX, self.FavY = 0.1,0.4125
		self.InfoW, self.InfoH = 0.199,0.8249
		self.InfoX, self.InfoY = 0.9,0.4125

	def on_pre_enter(self):
		self.ShowView()

	def ShowView(self):
		self.clear_widgets()
		self.LastClickOn = "nothing"
		self.ShowHomeIcon()
		self.ShowPathScroll()
		self.ShowTabs()
		self.ShowFolderContains()
		self.ShowFavContains()
		self.ShowItemInfo()

	def ShowHomeIcon(self):
		self.HomeButton = ImageButton(source=Info["RootIcon"]["home"],size_hint=(self.HomeW,self.HomeH),pos_hint={"center_x":self.HomeX,"center_y":self.HomeY},on_press=self.GoHome)
		self.add_widget(self.HomeButton)
		try:
			fold = NowFolders[NowFolder][:-(1+NowFolders[NowFolder][:-1][::-1].index("/"))]
			fun = partial(self.GoBack,fold,False)
		except:
			fun = time.time
		if len(RecFolders[NowFolder]):
			fold = RecFolders[NowFolder][-1]
			fun = partial(self.GoBack,fold,False)
		self.BackButton = ImageButton(source=Info["RootIcon"]["back"],size_hint=(self.BackW,self.BackH),pos_hint={"center_x":self.BackX,"center_y":self.BackY},on_press=fun)
		self.add_widget(self.BackButton)

	def ShowPathScroll(self):
		self.PathScroll = ScrollView(size_hint=(self.PathW,self.PathH),pos_hint={"center_x":self.PathX,"center_y":self.PathY}, size=(Window.width, Window.height))
		self.PathRoll = GridLayout(cols=10,spacing=3, size_hint_x=None,padding=5)
		self.PathRoll.bind(minimum_width=self.PathRoll.setter('width'))
		self.PathScroll.add_widget(self.PathRoll)
		self.add_widget(self.PathScroll)

		splitted = NowFolders[NowFolder][1:-1].replace("//","/").split("/")
		FolderPath = "/"
		for fold in splitted:
			if not(fold==""):
				FolderPath += fold + "/"
				pathbtn = Button(text="  "+fold+"  ",size_hint_x=None,halign='center',font_size=25,background_color=(0.5,0.5,0.5,0.5),font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=partial(self.ChangeFolder,FolderPath,True))
				pathbtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
				pathbtn.bind(texture_size=pathbtn.setter("size"))
				self.PathRoll.add_widget(pathbtn)

	def ShowTabs(self):
		self.TabRoll = GridLayout(cols=len(NowFolders),size_hint=(self.TabsW,self.TabsH),pos_hint={"center_x":self.TabsX,"center_y":self.TabsY},spacing=1,padding=3)
		self.add_widget(self.TabRoll)

		for foldernum in range(len(NowFolders)):
			MiniTab = GridLayout(cols=2,spacing=1,padding=2)
			folderpath = NowFolders[foldernum]
			fold = folderpath[1:-1].replace("//","/").split("/")[-1]
			pathbtn = Button(text="  "+fold+"  ",size_hint_x=0.8,background_color=(0.5,0.5,0.5,0.5),halign='center',font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=partial(self.ChangeTab,foldernum))
			pathbtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			pathbtn.bind(texture_size=pathbtn.setter("size"))
			MiniTab.add_widget(pathbtn)
			pathbtn = Button(text=" X ",size_hint_x=0.2,background_color=(0.5,0.5,0.5,0.75),halign='center',font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=partial(self.CloseTab,foldernum))
			pathbtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			pathbtn.bind(texture_size=pathbtn.setter("size"))
			MiniTab.add_widget(pathbtn)
			self.TabRoll.add_widget(MiniTab)

	def ShowFolderContains(self):
		self.MainScroll = ScrollView(size_hint=(self.MainW,self.MainH),pos_hint={"center_x":self.MainX,"center_y":self.MainY}, size=(Window.width, Window.height))
		self.MainRoll = GridLayout(cols=6,spacing=3, size_hint_y=None,padding=5)
		self.MainRoll.bind(minimum_height=self.MainRoll.setter('height'))
		self.MainScroll.add_widget(self.MainRoll)
		self.add_widget(self.MainScroll)
		self.FolderContains = {}

		self.GetFolders()
		self.GetFiles()

	def GetFolders(self):
		self.Folders = get_folders(NowFolders[NowFolder])
		for folder in self.Folders:
			MiniFold = GridLayout(cols=1,size_hint_y=None,height=110,spacing=1,padding=2)
			fun = partial(self.ClickedOn,NowFolders[NowFolder]+folder+"/","Folder")
			x_code = len(self.FolderContains)
			self.FolderContains[x_code] = {}
			self.FolderContains[x_code]["image"] = ImageButton(source=Info["RootIcon"]["folder"],size_hint_y=None,height=70,on_press=fun)

			self.FolderContains[x_code]["btn"] = Button(text=folder[:20],halign="center",valign="center",size_hint_y=None,height=35,background_color=(0.5,0.5,0.5,0.5),font_size=18,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			self.FolderContains[x_code]["btn"].bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))

	def GetFiles(self):
		self.Files = get_files(NowFolders[NowFolder])
		self.FileBtns = {}
		for file in self.Files:
			# MiniFold = GridLayout(cols=1,size_hint_y=None,height=110,spacing=1,padding=2)
			ext = file.split(".")[-1]
			source = Info["RootIcon"]["unknown"]
			MakeThumb = False
			if ext.lower() in Info["Exts"]:
				if(Info["Exts"][ext.lower()]=="image" or Info["Exts"][ext.lower()]=="video"):
					make = Info["Exts"][ext.lower()]
					source = Info["IconFolder"] + NowFolders[NowFolder] + file + Info["IconExt"]
					if not(exists(source)):
						ensure_dir(source)
						copyfile(Info["RootIcon"]["unknown"],source)
						MakeThumb = True
				else:
					source = Info["RootIcon"][Info["Exts"][ext.lower()]]
			fun = partial(self.ClickedOn,NowFolders[NowFolder]+file,ext)
			# self.FileBtns[NowFolders[NowFolder]+file] = ObjectProperty(None)
			x_code = len(self.FolderContains)
			self.FolderContains[x_code]["image"] = ObjectProperty(None)
			# self.FileBtns[NowFolders[NowFolder]+file] = ImageButton(source=source,size_hint_y=None,height=70,on_press=fun)
			self.FolderContains[x_code]["image"] = ImageButton(source=source,size_hint_y=None,height=70,on_press=fun)
			if(MakeThumb):
				print("sleeping")
				threading.Thread(target=partial(self.MakeThumb2,NowFolders[NowFolder]+file,source,make)).start()
				# Clock.schedule_once(partial(self.MakeThumb,NowFolders[NowFolder]+file,source,make))
				print("wake up")
			# MiniFold.add_widget(self.FileBtns[NowFolders[NowFolder]+file])
			self.FolderContains[x_code]["btn"] = Button(text=file[:20],halign="center",valign="center",size_hint_y=None,height=35,background_color=(0.5,0.5,0.5,0.5),font_size=18,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			self.FolderContains[x_code]["btn"].bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			# MiniFold.add_widget(this)
			# self.MainRoll.add_widget(MiniFold)

	def ShowFavContains(self):
		self.FavScroll = ScrollView(size_hint=(self.FavW,self.FavH),pos_hint={"center_x":self.FavX,"center_y":self.FavY}, size=(Window.width, Window.height))
		self.FavRoll = GridLayout(cols=1,spacing=5, size_hint_y=None,padding=5)
		self.FavRoll.bind(minimum_height=self.FavRoll.setter('height'))
		self.FavScroll.add_widget(self.FavRoll)
		self.add_widget(self.FavScroll)

		self.ShowDisks()
		self.ShowFavFolders()
		self.ShowRecFolders()
		self.ShowRecFiles()

	def ShowDisks(self):
		this = Button(text="Disks",halign="center",valign="center",size_hint_y=None,height=40,background_color=(0,0,0,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
		this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
		self.FavRoll.add_widget(this)
		for Disk in Info["Favs"]["Disks"]:
			MiniFold = GridLayout(cols=1,size_hint_y=None,height=40,spacing=1,padding=2)
			fun = partial(self.ChangeFolder,Info["Favs"]["Disks"][Disk],True)
			this = Button(text=Disk,halign="center",valign="center",size_hint_y=None,height=40,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			MiniFold.add_widget(this)
			self.FavRoll.add_widget(MiniFold)

	def ShowFavFolders(self):
		this = Button(text="Favourites",halign="center",valign="center",size_hint_y=None,height=40,background_color=(0,0,0,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
		this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
		self.FavRoll.add_widget(this)
		for Folder in Info["Favs"]["Folders"]:
			MiniFold = GridLayout(cols=1,size_hint_y=None,height=40,spacing=1,padding=2)
			fun = partial(self.ChangeFolder,Info["Favs"]["Folders"][Folder],True)
			this = Button(text=Folder,halign="center",valign="center",size_hint_y=None,height=40,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			MiniFold.add_widget(this)
			self.FavRoll.add_widget(MiniFold)

	def ShowRecFolders(self):
		RecFolds = Info["Rec"]["Folders"]
		RecList = {}
		for fold in RecFolds:
			if not fold in RecList:
				RecList[fold] = 0
			RecList[fold] += 1
		ShowFold = []
		for key,value in sorted(RecList.iteritems(), key=lambda(k,v):(v,k)):
			ShowFold.append(key)
		ShowFold = ShowFold[::-1]

		if len(ShowFold):
			this = Button(text="Recent Folders",halign="center",valign="center",size_hint_y=None,height=40,background_color=(0,0,0,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.FavRoll.add_widget(this)
			show = min(4,len(ShowFold))
			for i in range(show):
				folder = ShowFold[i][1:-1].split("/")[-1]
				fun = partial(self.ClickedOn,ShowFold[i],"Folder")
				# fun = partial(self.ClickedOn,ShowFiles[i],ShowFiles[i].split(".")[-1])
				this = Button(text=folder,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
				this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
				this.bind(texture_size=this.setter("size"))
				self.FavRoll.add_widget(this)

	def ShowRecFiles(self):
		RecFiles = Info["Rec"]["Files"]
		RecList = {}
		for fold in RecFiles:
			if not fold in RecList:
				RecList[fold] = 0
			RecList[fold] += 1
		ShowFiles = []
		for key,value in sorted(RecList.iteritems(), key=lambda(k,v):(v,k)):
			ShowFiles.append(key)
		ShowFiles = ShowFiles[::-1]

		if len(ShowFiles):
			this = Button(text="Recent Files",halign="center",valign="center",size_hint_y=None,height=40,background_color=(0,0,0,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.FavRoll.add_widget(this)
			show = min(4,len(ShowFiles))
			for i in range(show):
				folder = ShowFiles[i].split("/")[-1]
				fun = partial(self.ClickedOn,ShowFiles[i],ShowFiles[i].split(".")[-1])
				this = Button(text=folder,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
				this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
				this.bind(texture_size=this.setter("size"))
				self.FavRoll.add_widget(this)

	def ShowItemInfo(self):
		self.InfoScroll = ScrollView(size_hint=(self.InfoW,self.InfoH),pos_hint={"center_x":self.InfoX,"center_y":self.InfoY}, size=(Window.width, Window.height))
		self.InfoRoll = GridLayout(cols=1,spacing=5, size_hint_y=None,padding=5)
		self.InfoRoll.bind(minimum_height=self.InfoRoll.setter('height'))
		self.InfoScroll.add_widget(self.InfoRoll)
		self.add_widget(self.InfoScroll)

		self.ShowInfo(NowFolders[NowFolder],"Folder")

	def ShowInfo(self,filepath,filetype):
		self.InfoRoll.clear_widgets()
		if filetype=="Folder":
			this = ImageButton(source=Info["RootIcon"]["folder"],size_hint_y=None,height=200)
			self.InfoRoll.add_widget(this)

			self.WantInfo = filepath
			folder = filepath[1:-1].split("/")[-1]
			fun = partial(self.ChangeFolder,filepath,True)
			this = Button(text=folder,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.InfoRoll.add_widget(this)
	
			text = "Size : -"
			self.SizeInfo = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.SizeInfo.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.SizeInfo.bind(texture_size=self.SizeInfo.setter("size"))
			self.InfoRoll.add_widget(self.SizeInfo)
			threading.Thread(target=partial(self.UpdateInfo,"size",filepath)).start()

			text = "Modified : -"# + str(get_modified_time(filepath))
			self.ModiBtn = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.ModiBtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.ModiBtn.bind(texture_size=self.ModiBtn.setter("size"))
			self.InfoRoll.add_widget(self.ModiBtn)
			threading.Thread(target=partial(self.UpdateInfo,"modi",filepath)).start()

			text = "Folders : -"# + str(len(get_folders(filepath)))
			self.FoldNumBtn = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.FoldNumBtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.FoldNumBtn.bind(texture_size=self.FoldNumBtn.setter("size"))
			self.InfoRoll.add_widget(self.FoldNumBtn)
			threading.Thread(target=partial(self.UpdateInfo,"fold",filepath)).start()

			text = "Files : -"# + str(len(get_files(filepath)))
			self.FileNumBtn = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.FileNumBtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.FileNumBtn.bind(texture_size=self.FileNumBtn.setter("size"))
			self.InfoRoll.add_widget(self.FileNumBtn)
			threading.Thread(target=partial(self.UpdateInfo,"file",filepath)).start()

			this = Button(text=filepath,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.InfoRoll.add_widget(this)

		else:
			if(filetype in Info["Exts"]):
				if(Info["Exts"][filetype]=="video"):
					source = Info["IconFolder"] + filepath + Info["IconExt"]
				elif(Info["Exts"][filetype]=="image"):
					source = filepath
				else:
					source = Info["RootIcon"][Info["Exts"][filetype]]				
			else:
				source = Info["RootIcon"]["unknown"]
			this = ImageButton(source=source,size_hint_y=None,height=200)
			self.InfoRoll.add_widget(this)

			self.WantInfo = filepath
			folder = filepath[:].split("/")[-1]
			fun = partial(self.ChangeFolder,filepath,True)
			this = Button(text=folder,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.5),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.InfoRoll.add_widget(this)
	
			text = "Size : -"
			self.SizeInfo = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.SizeInfo.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.SizeInfo.bind(texture_size=self.SizeInfo.setter("size"))
			self.InfoRoll.add_widget(self.SizeInfo)
			threading.Thread(target=partial(self.UpdateInfo,"size",filepath)).start()

			text = "Modified : -"
			self.ModiBtn = Button(text=text,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			self.ModiBtn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.ModiBtn.bind(texture_size=self.ModiBtn.setter("size"))
			self.InfoRoll.add_widget(self.ModiBtn)
			threading.Thread(target=partial(self.UpdateInfo,"modi",filepath)).start()

			this = Button(text=filepath,halign="center",valign="center",size_hint_y=None,background_color=(0.5,0.5,0.5,0.25),font_size=25,font_name=Info["Font"]["LobsterTwo-BoldItalic"])
			this.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			this.bind(texture_size=this.setter("size"))
			self.InfoRoll.add_widget(this)

	def ClickedOn(self,filepath,filetype="Folder",_="_"):
		NowTime = time.time()
		if((NowTime-self.LastClickTime)<self.TimeAllow):
			if(filepath==self.LastClickOn):
				if filetype=="Folder":
					self.ChangeFolder(filepath,True)
					return
				if filetype in Info["Exts"]:
					Info["Rec"]["Folders"].append(filepath[:-len(filepath.split("/")[-1])])
					Info["Rec"]["Folders"] = Info["Rec"]["Folders"][-100:]
					Info["Rec"]["Files"].append(filepath)
					Info["Rec"]["Files"] = Info["Rec"]["Files"][-100:]
					PostProcessing()
					webbrowser.open(filepath)
					return
		self.LastClickTime = NowTime
		self.LastClickOn = filepath
		self.ShowInfo(filepath,filetype)
		return

	def ChangeFolder(self,folder,addRec=True,_="_"):
		global NowFolders, NowFolder, RecFolders
		if addRec:
			RecFolders[NowFolder].append(NowFolders[NowFolder])
		NowFolders[NowFolder] = folder
		self.on_pre_enter()

	def GoBack(self,folder,addRec=False,_="_"):
		global NowFolders, NowFolder, RecFolders
		if(len(RecFolders[NowFolder])):
			RecFolders[NowFolder] = RecFolders[NowFolder][:-1]
		self.ChangeFolder(folder,addRec)

	def ChangeTab(self,foldernum,_="_"):
		global NowFolder
		NowFolder = foldernum
		self.on_pre_enter()

	def CloseTab(self,foldernum,_="_"):
		global NowFolder, NowFolders, RecFolders
		if not len(NowFolders)==1:
			NowFolders = NowFolders[:foldernum] + NowFolders[foldernum+1:]
			RecFolders = RecFolders[:foldernum] + RecFolders[foldernum+1:]
			NowFolder = foldernum-1
			self.on_pre_enter()

	def UpdateInfo(self,make,name,_="-"):
		if(make=="size"):
			size_,fold = get_size(name)
			if(self.WantInfo==fold):
				self.SizeInfo.text = "Size : " + str(size_)
		elif(make=="modi"):
			text = "Modified : " + str(get_modified_time(name))
			if(name==self.WantInfo):
				self.ModiBtn.text = text
		elif(make=="fold"):
			text = "Folders : " + str(len(get_folders(name)))
			if(name==self.WantInfo):
				self.FoldNumBtn.text = text
		elif(make=="file"):
			text = "Files : " + str(len(get_files(name)))
			if(name==self.WantInfo):
				self.FileNumBtn.text = text

	def GoHome(self,_="_"):
		global NowFolders, NowFolder
		NowFolders[NowFolder] = Info["HomeFolder"]
		self.on_pre_enter()

	def MakeThumb2(self,filepath,source,make,_="_"):
		Clock.schedule_once(partial(self.MakeThumb,filepath,source,make))
		return

	def MakeThumb(self,filepath,source,make,_="_"):
		if(make=="image"):
			make_img_thumb(filepath,source)
		elif(make=="video"):
			make_vid_thumb(filepath,source)
		self.FileBtns[filepath].reload()

class MainClass(App):
	def build(self):
		ScreenMan = ScreenManagerbuild()

		ScreenMan.add_widget(HomeScreen(name='HomeWindow'))

		return ScreenMan

class ScreenManagerbuild(ScreenManager):
	pass

if __name__ == '__main__':
	PreProcessing()
	MainClass().run()
	PostProcessing()
