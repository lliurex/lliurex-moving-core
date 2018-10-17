import re
import fnmatch
import os
import commands
import subprocess
import shutil
import glob

import xmlrpclib

import locale
import gettext

locale.textdomain("xdg-user-dirs")
gettext.textdomain("xdg-user-dirs")


class MovingProfiles:
	
		
	
	def __init__(self,login,port=9779):
	
		self.ignore={"/":[".xinputrc"],".config":["/user-dirs.*","/google-chrome/Singleton*","/chromium/Singleton*","/libreoffice/4/.lock","/pulse"],".mozilla":["/firefox/*.default/storage","/firefox/*.default/lock"],".local":["/share/teamviewer*","/share/Trash/*","/share/gvfs-metadata/*"]}
		
		self.login=login
		server_port=str(port)
		
		server_name="server"
		
		self.connection_string = "https://"+server_name+":"+server_port
		proxy = xmlrpclib.ServerProxy(self.connection_string)
				
		#perform a cached read				
		self.cfg = proxy.get_list(login,"MovingProfiles")
		

		
	def isInclude(self,filename):
		
		reti=[]
		for name in self.cfg["include"]:
			value=self.cfg["include"][name]
			if fnmatch.fnmatchcase(filename,value):
				reti.append(name)
				
				
		if len(reti)==0:
			return None
		else:
			return reti
		
		
	def isExclude(self,filename):
		
		rete=[]
		for name in self.cfg["exclude"]:
			value=self.cfg["exclude"][name]
			if fnmatch.fnmatchcase(filename,value):
				rete.append(name)
				
		if len(rete)==0:
			return None
		else:
			return rete
	
	
	def Match(self,fname):
		
		include=False

		
		for name in self.cfg["include"]:
			value=self.cfg["include"][name]
			if fnmatch.fnmatchcase(fname,value):
				include=True

				break
				
		if include:
			for name in self.cfg["exclude"]:
				value=self.cfg["exclude"][name]
				if fnmatch.fnmatchcase(fname,value):

					return False
					
			return True
				
		else:
			return False
		
	
	def MatchFolder(self,path):
	
		mlist=[]
	
		for fname in os.listdir(path):
			if(self.Match(fname)):
				mlist.append(fname)
				
		return mlist
			
		
	
		
	def Clear(self):
		self.cfg={"include":{},"exclude":{}}
			
		
	def Save(self):
		proxy = xmlrpclib.ServerProxy(self.connection_string)	
		proxy.save_conf(self.login,"MovingProfiles",self.cfg)



	def GetProfilePath(self):
		
		try:
			
			home=os.path.expanduser("~")
			execfile(home+"/.config/user-dirs.dirs")
			documents_dir=locals()["XDG_DOCUMENTS_DIR"].split("/")[1]
			moving_profiles="%s/%s/.moving_profiles/"%(home,documents_dir)
			
		except Exception as e:
		
			try:
				user=os.getenv("USER")
				documents=gettext.gettext("Documents")
				moving_profiles = "/home/%s/%s/.moving_profiles/"%(user,documents)
				
			except:
				print ("[GetProfilePath] Failed constructing home path")
				raise
		

		return moving_profiles
		

	def FinalActions(self):
		
		path="/usr/share/lliurex-moving-core/postactions/"
		
		for f in sorted(glob.glob(path+"*")):
			print("* Executing %s ..."%f)
			os.system(f + " || true")		
		
	#def FinalActions

		
	def LoadSession(self):
		moving_path=self.GetProfilePath()
		home=os.path.expanduser("~")
		
		if not os.path.exists(moving_path):
			# at least execute final actions before exiting
			self.FinalActions()
			raise Exception("Profile dir not found, aborting load")
			
			
		print("[LoadSession] Synchronization")
		print("[LoadSession] Stage 1")
		
		
		cmd=["rsync","-aAX","--delete","--ignore-errors"]
		
		profile_files=self.MatchFolder(moving_path)
		
		for fname in profile_files:
			print("[rsync] "+fname)

			ecmd=[]
			if(fname in self.ignore):
				elist=self.ignore[fname]
				for erule in elist:
					ecmd.append("--exclude=%s"%erule)
					print("* excluding: "+erule)
					
			
			source = '%s/%s'%(moving_path,fname)
			destination='%s/%s'%(home,fname)

			if(os.path.isdir(source)):
				source=source+"/"
				destination=destination+"/"
			
			source = '"%s"'%source
			destination = '"%s"'%destination
			
			rcmd = cmd + ecmd + [source,destination]
			plain_cmd=" ".join(rcmd)
			plain_cmd+=" || true"
			
			subprocess.call(plain_cmd,shell=True)
			
		

		print("[LoadSession] Stage 2")

		home_files = self.MatchFolder(home)
		
		for hname in home_files:
			if not hname in profile_files:
				hpath=home+"/"+hname
				
				print("[rm] "+hname)
				
				rm=os.remove
				
				if(os.path.isdir(hpath)):
					rm=shutil.rmtree
				
				rm(hpath)

		# Stage 3
		print("[LoadSession] Stage 3")
		self.FinalActions()



	def SaveSession(self):
		moving_path=self.GetProfilePath()
		print("[SaveSession] moving path: "+moving_path)
		
		if not os.path.exists(moving_path):
			print("[SaveSession] Creating profile path")
			try:
				os.makedirs(moving_path)
			except:
				raise
				
				
		
		cmd=["rsync","-aAX","--delete","--ignore-errors"]
		
		

		print("rsync cmd:")
		for c in cmd:
			print(c)
		
		home=os.path.expanduser("~")
		print("[SaveSession] Synchronization")
		print("[SaveSession] Stage 1")
		
		home_files = self.MatchFolder(home)
		for fname in home_files:
			fpath=home+"/"+fname
			
			if(os.path.isdir(fpath)):
				fpath=fpath+"/"
			
			print("[rsync] "+fname)

			ecmd = []

			if(fname in self.ignore):
				elist = self.ignore[fname]
				for erule in elist:
					ecmd.append("--exclude=%s"%erule)
					print("* excluding: "+erule)		


			source = home +"/" + fname
			destination = moving_path+"/"+fname

			if(os.path.isdir(source)):
				source=source+"/"
				destination=destination+"/"

			source = '"%s"'%source
			destination = '"%s"'%destination
			
			rcmd = cmd + ecmd + [source,destination]
			plain_cmd = " ".join(rcmd)
			subprocess.call(plain_cmd,shell=True)
		
					
			
		print("[SaveSession] Stage 2")
		
		for fname in os.listdir(moving_path):
			if not fname in home_files:
				fpath=moving_path+"/"+fname
				
				print("[rm] "+fname)
				
				rm=os.remove

				if(os.path.isdir(fpath)):
					rm=shutil.rmtree
					
				rm(fpath)
				
				

	def Backup(self,name):
		backup_path=self.GetProfilePath()+"../.moving_profiles_backup/"+name
		
		print("[Backup] backup path: "+backup_path)
		
		if(os.path.exists(backup_path)):
			print("[Backup] "+name+" already exists")
			return
		else:
			try:
				os.makedirs(backup_path)
			except:
				raise
			
			
		
		cmd=["rsync","-az","--delete"]
		
		
		
		home=os.path.expanduser("~")
		
		print("[Backup] Backing up as "+name)

		
		home_files = self.MatchFolder(home)
		for fname in home_files:
			fpath=home+"/"+fname
			
			if(os.path.isdir(fpath)):
				fpath=fpath+"/"
			
			print("[rsync] "+fname)
			
			rcmd = cmd + [fpath, backup_path+"/"+fname ]			
			subprocess.call(rcmd)	

