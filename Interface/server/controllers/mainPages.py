from wsgiref.simple_server import make_server
from tg import expose, TGController, AppConfig
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from time import strftime
import os

def inputCleaner(text):
  toReturn=""
  for x in text:
    if x.lower() in "azertyuiopmlkjhgfdsqwxcvbn123456789_":
      toReturn+=x
  return(toReturn)

def checkGoodName(name):
  inputCleaner(name)
  try:
    os.listdir("results/%s"%name)
    return(True)
  except:
    return(False)

def getDefaultName():
  panpans = os.listdir("results")
  t = strftime("%y_%m_%d_%H%M%S")
  if not "MyPanPan" in panpans:
    return("MyPanPan")
  elif not "MyPanPan_"+t in panpans:
    return("MyPanPan_"+t)
  else:
    baseName="MyPanPan_"+t+"_"
    for i in range(1000):
      if not baseName+str(i) in panpans:
        return(panpans)
    return("UnableToGetName")

def getRequestValidity(page):
    page["goodImage"]="unknown"
    page["nWest"]="unknown number of "
    page["nWestComputed"]="unknown number of "
    if "name" in page.keys() or not page.name in os.listdir("results") or not "status.txt" in os.listdir("results/%s"%page.name):
      return()
    f = open("results/%s"%page.name)
    for line in f:
      if "goodImage" in line.split("="):
        page["goodImage"]=line.split("=")[-1].replace("\n","")
      if "nWest" in line.split("="):
        page["goodImage"]=line.split("=")[-1].replace("\n","")
      if "nWest" in line.split("="):
        page["goodImage"]=line.split("=")[-1].replace("\n","")
      f.close()

class RootController(TGController):
  @expose('templates.index')
  def index(self,message=""):
      """Handle the 'about' page."""
      r=os.listdir("results")
      return dict(savedResults=r,defaultName = "default",message_=message.replace("+",""))
  @expose('templates.header')
  def header(self):
    return({'message':"yo"})


  @expose('templates.submitPanpan')
  def sendPanPan(self,fName="",panpanName=""):
    panpanName=inputCleaner(panpanName)
    if panpanName=="default":
      panpanName = getDefaultName()
    if panpanName=="UnableToGetName":
      redirect("index?message=Unable+to+create+default+name")
    if panpanName in os.listdir("results"):
      redirect("index?message=PanPan+%s+already+exists+!"%panpanName)
    if not hasattr(fName,'value'):
      redirect("index?message=Cannot+read+input+file!")
    #print fName.value
    os.system("mkdir results/%s"%panpanName)
    panpanPic = open("results/%s/image.png"%panpanName,"w")
    panpanPic.write(fName.value)
    panpanPic.close()
    return dict(name=panpanName)

  @expose('templates.viewPanpan')
  def viewPanPan(self,name=""):
    if not name in os.listdir("results"):
      redirect("index?message=Cannot+read+Panpan!")
    page = {}
    if not "image.png" in os.listdir("results/%s"%name):
      page["hasImage"]=False
    else:
      page["hasImage"]=True

    if "w0" in os.listdir("results/%s"%name):
      page["hasWesterns"]=True
    else:
      page["hasWesterns"]=False
    page["westFolders"]=[]
    for f in os.listdir("results/%s"%name):
      if f[0]=="w" and f[1:].isdigit():
        page["westFolders"].append(f)
    page["name"]=name

    getRequestValidity(page)

    return(page)

  @expose()
  def launchJob(self,name="",action=""):
    if not(checkGoodName(name)):
      redirect("index?message=Invalid+request")
    else:
      if not action in ["all","getWesterns","computeBackground","getLumi"]:
        redirect("index?message=Invalid+request")
    os.system(". ../../init.sh; cd results/%s; python ../../serverScripts/processPanPan.py %s %s &"%(name,name,action))
    redirect("viewPanPan?name=%s"%name)

  @expose("templates.viewWest")
  def displayPlots(self,name="",west=""):
    print name
    if not(checkGoodName(name)):
      redirect("index?message=Invalid+request")
    page={}
    page["name"]=name
    page["west"]=west
    page["pict"]=[]
    for f in os.listdir("results/"+name+"/"+west):
      if ".png" in f:
        page["pict"].append(f)
    page["summary"]=""
    if "summary.txt" in os.listdir("results/"+name+"/"+west):
      page["summary"]=open("results/"+name+"/"+west+"/summary.txt","r").read()


    return(page)
