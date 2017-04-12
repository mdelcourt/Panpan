from wsgiref.simple_server import make_server
from tg import expose, TGController, AppConfig
from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from time import strftime
import os,json,time

resultFolder = "panpan/public/results/"

def inputCleaner(text):
  toReturn=""
  for x in text:
    if x.lower() in "azertyuiopmlkjhgfdsqwxcvbn123456789_":
      toReturn+=x
  return(toReturn)

def checkGoodName(name):
  inputCleaner(name)
  try:
    os.listdir(resultFolder+name)
    return(True)
  except:
    return(False)

def getDefaultName():
  panpans = os.listdir(resultFolder)
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
    return()
    page["goodImage"]="unknown"
    page["nWest"]="unknown number of "
    page["nWestComputed"]="unknown number of "

    if "name" in page.keys() or not page.name in os.listdir(resultFolder) or not "status.txt" in os.listdir(resultFolder+page.name):
      return()
    f = open(resultFolder+page.name)
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
      r=os.listdir(resultFolder)
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
    if panpanName in os.listdir(resultFolder):
      redirect("index?message=PanPan+%s+already+exists+!"%panpanName)
    if not hasattr(fName,'value'):
      redirect("index?message=Cannot+read+input+file!")
    #print fName.value
    os.system("mkdir "+resultFolder+panpanName)
    panpanPic = open(resultFolder+"%s/image.png"%panpanName,"w")
    panpanPic.write(fName.value)
    panpanPic.close()
    return dict(name=panpanName)

  @expose('templates.viewPanpan')
  def viewPanPan(self,name=""):
    if not name in os.listdir(resultFolder):
      redirect("index?message=Cannot+read+Panpan!")
    page = {}
    fileList = os.listdir(resultFolder+name)
    page["hasImage"]="image.png" in fileList
    page["hasOutIm"]="outim.png" in fileList
    page["hasWesterns"] = "western_0" in fileList

    page["westFolders"]=[]
    for f in fileList:
      if f[0:7]=="western" and f[8:].isdigit():
        page["westFolders"].append(int(f[8:]))
    page["westFolders"].sort()
    page["name"]=name
    print page["westFolders"]
    return(page)

  @expose()
  def launchJob(self,name="",action=""):
    if not(checkGoodName(name)):
      redirect("index?message=Invalid+request")
    else:
      if not action in ["all","getWesterns","computeBackground","getLumi"]:
        redirect("index?message=Invalid+request")
    os.system(". ../../init.sh; cd %s%s; pwd; python ../../../serverScripts/processPanPanModular.py %s %s &"%(resultFolder,name,name,action))
    redirect("viewPanPan?name=%s"%name)

  @expose("templates.status")
  def jobStatus(self,name=""):
    if not "status.json" in os.listdir(resultFolder+name):
      return("Unable to get process status")
    else:
      page={}
      with open(resultFolder+name+"/status.json","r") as f:
        page=json.load(f)
      page['done'] = page['processingStep']=="done"
      page['stalled']=((time.time()-float(page['date']))>30)
      if page['done']:
        page['stalled']=False
      page['name']=name
      return(page)
  @expose('templates.include')
  def include(self):
     return {}

  @expose("templates.viewWest")
  def displayPlots(self,name="",west=""):
    print name
    if not(checkGoodName(name)):
      redirect("index?message=Invalid+request")
    page={}
    page["name"]=name
    page["west"]=west
    page["pict"]=[]
    fileList=os.listdir(resultFolder+name+"/western_"+west)
    for f in fileList:
      if ".png" in f or ".svg" in f:
        page["pict"].append("results/"+name+"/western_"+west+"/"+f)
    page["summary"]=""
    if "summary.txt" in fileList:
      page["summary"]=open(resultFolder+name+"/"+west+"/summary.txt","r").read()


    return(page)
