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

		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down,on_key_up=self._on_keyboard_up)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down,on_key_up=self._on_keyboard_up)
		self._keyboard = None

	def _on_keyboard_up(self, keyboard, keycode):
		key_no, self.left_key = keycode
		if(self.left_key=="lctrl" or self.left_key=="rctrl"):
			self.IsCtrl = False
		elif(self.left_key=="shift" or self.left_key=="rshift"):
			self.IsShift = False

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		key_no, self.pressed_key = keycode
		print(self.pressed_key)
		if(self.pressed_key=="lctrl" or self.pressed_key=="rctrl"):
			self.IsCtrl = True
		elif(self.pressed_key=="shift" or self.pressed_key=="rshift"):
			self.IsShift = True
		elif(self.pressed_key=="backspace"):
			try:
				fold = NowFolders[NowFolder][:-(1+NowFolders[NowFolder][:-1][::-1].index("/"))]
				fun = partial(self.GoBack,fold,False)
			except:
				fun = time.time
			if len(RecFolders[NowFolder]):
				fold = RecFolders[NowFolder][-1]
				fun = partial(self.GoBack,fold,False)
			fun()
		elif(self.pressed_key=="right" or self.pressed_key=="left" or self.pressed_key=="down" or self.pressed_key=="up"):
			NewPoint = -1
			if(self.pressed_key=="right"):
				if(self.PointLast < (self.FolderItems-1)):
					NewPoint = self.PointLast + 1
			elif(self.pressed_key=="left"):
				if(self.PointLast > 0):
					NewPoint = self.PointLast - 1
			elif(self.pressed_key=="up"):
				if(self.PointLast > (self.RowItems - 1)):
					NewPoint = self.PointLast - self.RowItems
				else:
					NewPoint = 0
			elif(self.pressed_key=="down"):
				if(self.PointLast < (self.FolderItems - self.RowItems)):
					NewPoint = self.PointLast + self.RowItems
				else:
					NewPoint = self.FolderItems - 1
			if not (NewPoint == -1):
				self.ClickedOn(self.FolderContains[NewPoint]["path"],NewPoint,self.FolderContains[NewPoint]["type"])
				# self,filepath,x_code,filetype="Folder",_="_"
			# if not self.IsShift:
			# 	if(self.pressed_key=="right"):
			# 		if(self.PointLast < (self.FolderItems-1)):
			# 			self.PointLast += 1
			# 	elif(self.pressed_key=="left"):
			# 		if(self.PointLast > 0):
			# 			self.PointLast -= 1
			# 	elif(self.pressed_key=="up"):
			# 		if(self.PointLast > (self.RowItems - 1)):
			# 			self.PointLast -= self.RowItems
			# 	elif(self.pressed_key=="down"):
			# 		if(self.PointLast < (self.FolderItems - self.RowItems)):
			# 			self.PointLast += self.RowItems
			# 	self.PointOn = [0 for i in range(self.FolderItems)]
			# 	self.PointOn[self.PointLast] = 1
			# if self.IsShift:
			# 	if(self.pressed_key=="right"):
			# 		if(self.PointLast < (self.FolderItems-1)):
			# 			self.PointLast += 1
			# 			self.PointOn[self.PointLast] = 1
			# 	elif(self.pressed_key=="left"):
			# 		if(self.PointLast > 0):
			# 			self.PointLast -= 1
			# 			self.PointOn[self.PointLast] = 1
			# 	elif(self.pressed_key=="up"):
			# 		for i in range(max(0,self.PointLast-self.RowItems),self.PointLast):
			# 			self.PointOn[i] = 1
			# 		if(self.PointLast > (self.RowItems - 1)):
			# 			self.PointLast -= self.RowItems
			# 	elif(self.pressed_key=="down"):
			# 		for i in range(self.PointLast,min(self.FolderItems,self.PointLast+self.RowItems+1)):
			# 			self.PointOn[i] = 1
			# 		if(self.PointLast < (self.FolderItems - self.RowItems)):
			# 			self.PointLast += self.RowItems
			# self.HighButton()
		elif(self.pressed_key=="enter" or self.pressed_key=="numpadenter"):
			if not(self.LastClickOn=="nothing"):
				if(self.LastClickType=="Folder"):
					self.ChangeFolder(self.LastClickOn,True)
				elif self.LastClickType in Info["Exts"]:
					Info["Rec"]["Folders"].append(self.LastClickOn[:-len(self.LastClickOn.split("/")[-1])])
					Info["Rec"]["Folders"] = Info["Rec"]["Folders"][-100:]
					Info["Rec"]["Files"].append(self.LastClickOn)
					Info["Rec"]["Files"] = Info["Rec"]["Files"][-100:]
					PostProcessing()
					webbrowser.open(self.LastClickOn)

	def HighButton(self):
		print(self.PointOn)
		for i in range(self.FolderItems):
			if(self.PointOn[i]):
				self.FolderContains[i]["btn"].background_color = (0.75,0.75,0.75,0.75)
			else:
				self.FolderContains[i]["btn"].background_color = (0.5,0.5,0.5,0.5)
		return
		if(-1 < self.PointOn < len(self.FolderContains)):
			self.FolderContains[self.PointOn]["btn"].background_color = (0.5,0.5,0.5,0.5)
		# self.PointOn = NewPoint
		# self.LastClickOn = self.FolderContains[self.PointOn]["path"]
		# self.LastClickType = self.FolderContains[self.PointOn]["type"]
		# self.ShowInfo(self.LastClickOn,self.FolderContains[self.PointOn]["type"])

	def DefineSpecials(self):
		self.RowItems = 6
		self.NumOfTabs = 1
		self.TimeAllow = 1
		self.LastClickTime = 1
		self.PointOn = []
		self.PointLast = -1
		self.LastClickOn = "nothing"
		self.LastClickType = "nothing"
		self.IsCtrl = False
		self.IsShift = False

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
		self.LastClickType = "nothing"
		self.PointOn = []
		self.PointLast = -1
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
		self.MainRoll = GridLayout(cols=self.RowItems,spacing=3, size_hint_y=None,padding=5)
		self.MainRoll.bind(minimum_height=self.MainRoll.setter('height'))
		self.MainScroll.add_widget(self.MainRoll)
		self.add_widget(self.MainScroll)
		self.FolderContains = {}

		self.GetFolders()
		self.GetFiles()
		self.FolderItems = len(self.FolderContains)
		# x_code = len(self.FolderContains)
		self.PointOn = [0 for i in range(self.FolderItems)]
		if(self.FolderItems%self.RowItems!=0):
			for y in range(self.RowItems-(self.FolderItems%self.RowItems)):
				self.FolderContains[self.FolderItems+y] = {"image":Label(),"btn":Label()}
		for i in range(len(self.FolderContains)//self.RowItems):
			for j in range(self.RowItems):
				k = i*self.RowItems + j
				self.MainRoll.add_widget(self.FolderContains[k]["image"])
			for j in range(self.RowItems):
				k = i*self.RowItems + j
				self.MainRoll.add_widget(self.FolderContains[k]["btn"])

	def GetFolders(self):
		self.Folders = get_folders(NowFolders[NowFolder])
		for folder in self.Folders:
			x_code = len(self.FolderContains)
			fun = partial(self.ClickedOn,NowFolders[NowFolder]+folder+"/",x_code,"Folder")
			self.FolderContains[x_code] = {"path":NowFolders[NowFolder]+folder+"/","type":"Folder"}
			self.FolderContains[x_code]["image"] = ImageButton(source=Info["RootIcon"]["folder"],size_hint_y=None,height=70,on_press=fun)
			self.FolderContains[x_code]["btn"] = Button(text=folder[:20],halign="center",valign="center",size_hint_y=None,height=50,background_color=(0.5,0.5,0.5,0.5),font_size=18,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			self.FolderContains[x_code]["btn"].bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))

	def GetFiles(self):
		self.Files = get_files(NowFolders[NowFolder])
		self.FileBtns = {}
		for file in self.Files:
			ext = file.split(".")[-1]
			source = Info["RootIcon"]["unknown"]
			HaveThumb = False
			if ext.lower() in Info["Exts"]:
				if(Info["Exts"][ext.lower()]=="image" or Info["Exts"][ext.lower()]=="video"):
					make = Info["Exts"][ext.lower()]
					source = Info["IconFolder"] + NowFolders[NowFolder] + file + Info["IconExt"]
					if not(exists(source)):
						ensure_dir(source)
						copyfile(Info["RootIcon"]["unknown"],source)
						HaveThumb = True
				else:
					source = Info["RootIcon"][Info["Exts"][ext.lower()]]
			x_code = len(self.FolderContains)
			fun = partial(self.ClickedOn,NowFolders[NowFolder]+file,x_code,ext)
			self.FolderContains[x_code] = {"path":NowFolders[NowFolder] + file,"type":ext}
			self.FolderContains[x_code]["image"] = ObjectProperty(None)
			self.FolderContains[x_code]["image"] = ImageButton(source=source,size_hint_y=None,height=70,on_press=fun)
			if(HaveThumb):
				print("sleeping")
				threading.Thread(target=partial(self.MakeThumb2,NowFolders[NowFolder]+file,source,make,x_code)).start()
				# Clock.schedule_once(partial(self.MakeThumb,NowFolders[NowFolder]+file,source,make))
				print("wake up")
			self.FolderContains[x_code]["btn"] = Button(text=file[:20],halign="center",valign="center",size_hint_y=None,height=50,background_color=(0.5,0.5,0.5,0.5),font_size=18,font_name=Info["Font"]["LobsterTwo-BoldItalic"],on_press=fun)
			self.FolderContains[x_code]["btn"].bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))

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
			fun = partial(self.ClickedOn,Info["Favs"]["Folders"][Folder],-1,"Folder")
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
				fun = partial(self.ClickedOn,ShowFold[i],-1,"Folder")
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
				fun = partial(self.ClickedOn,ShowFiles[i],-1,ShowFiles[i].split(".")[-1])
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

	def ClickedOn(self,filepath,x_code,filetype="Folder",_="_"):
		NowTime = time.time()
		print(self.PointLast,x_code,self.IsShift,self.IsCtrl)
		if not(x_code==-1):
			if self.IsShift:
				if(x_code>self.PointLast):
					for i in range(self.PointLast+1,x_code+1):
						self.PointOn[i] = 1 - self.PointOn[i]
				elif(x_code<self.PointLast):
					for i in range(self.PointLast-1,x_code-1,-1):
						self.PointOn[i] = 1 - self.PointOn[i]
			elif(not self.IsCtrl):
				for i in range(self.FolderItems):
					self.PointOn[i] = 0
				self.PointOn[x_code] = 1
			elif(self.IsCtrl):
				self.PointOn[x_code] = 1 - self.PointOn[x_code]
		if((NowTime-self.LastClickTime)<self.TimeAllow):
			if(filepath==self.LastClickOn):
				if filetype=="Folder":
					self.ChangeFolder(filepath,True)
					if not(self.IsCtrl + self.IsShift):
						return
				if filetype in Info["Exts"]:
					Info["Rec"]["Folders"].append(filepath[:-len(filepath.split("/")[-1])])
					Info["Rec"]["Folders"] = Info["Rec"]["Folders"][-100:]
					Info["Rec"]["Files"].append(filepath)
					Info["Rec"]["Files"] = Info["Rec"]["Files"][-100:]
					PostProcessing()
					webbrowser.open(filepath)
					if not(self.IsCtrl + self.IsShift):
						return
		self.LastClickTime = NowTime
		self.LastClickOn = filepath
		self.LastClickType = filetype
		self.PointLast = x_code
		self.ShowInfo(filepath,filetype)
		self.HighButton()
		return

	def ChangeFolder(self,folder,addRec=True,_="_"):
		global NowFolders, NowFolder, RecFolders
		if not(self.IsCtrl + self.IsShift):
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

	def MakeThumb2(self,filepath,source,make,x_code,_="_"):
		Clock.schedule_once(partial(self.MakeThumb,filepath,source,make,x_code))
		return

	def MakeThumb(self,filepath,source,make,x_code,_="_"):
		if(make=="image"):
			make_img_thumb(filepath,source)
		elif(make=="video"):
			make_vid_thumb(filepath,source)
		self.FolderContains[x_code]["image"].reload()

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
