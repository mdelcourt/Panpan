# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from panpan.model import DBSession, metadata
import os,sys,json,time,commands
from time import strftime
from panpan.lib.base import BaseController
from panpan.controllers.error import ErrorController

__all__ = ['RootController']

PANPAN_PATH = os.environ['PANPANPATH']
SERVER_PATH = os.environ['SERVERPATH']
resultFolder = SERVER_PATH+"/panpan/public/results/"

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

def getDefaultName(prefix="MyPanPan"):
  panpans = os.listdir(resultFolder)
  t = strftime("%y_%m_%d_%H%M%S")
  if not prefix in panpans:
    return(prefix)
  elif not prefix+t in panpans:
    return(prefix+t)
  else:
    baseName=prefix+t+"_"
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


class RootController(BaseController):
  """
  The root controller for the panpan application.

  All the other controllers and WSGI applications should be mounted on this
  controller. For example::

      panel = ControlPanelController()
      another_app = AnotherWSGIApplication()

  Keep in mind that WSGI applications shouldn't be mounted directly: They
  must be wrapped around with :class:`tg.controllers.WSGIAppController`.

  """

  error = ErrorController()

  def _before(self, *args, **kw):
      tmpl_context.project_name = "panpan"

  @expose('panpan.templates.index')
  def index(self,message="",mType="error"):
      """Handle the 'about' page."""
      r=os.listdir(resultFolder)
      r.sort()
      color_ = "red"
      if mType.lower()=="info":
        color_="blue"
      return dict(savedResults=r,defaultName = "default",message_=message.replace("+",""),colour=color_)
  @expose('panpan.templates.header')
  def header(self):
    return({'message':"yo"})


  @expose('panpan.templates.submitPanpan')
  def sendPanPan(self,fName="",panpanName=""):
    panpanName=inputCleaner(panpanName)
    if panpanName=="default":
      panpanName = getDefaultName()
    if len(panpanName)>7 and panpanName[-7:]=="default":
      print panpanName[-7:]
      print panpanName[:-7]
      panpanName=getDefaultName(panpanName[:-7])
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

  @expose('panpan.templates.viewPanpan')
  def viewPanPan(self,name="",message="",mType="Error"):
    if not name in os.listdir(resultFolder):
      redirect("index?message=Cannot+read+Panpan!")
    page = {}
    page["message"]=message
    page["colour"]="black"
    if mType.lower()=="error":
      page["colour"]="red"
    elif mType.lower()=="info":
      page["colour"]="green"

    fileList = os.listdir(resultFolder+name)
    page["hasLog"] = "log.txt" in fileList
    page["hasImage"]="image.png" in fileList
    page["hasOutIm"]="outim.png" in fileList
    page["hasWesterns"] = "western_0" in fileList
    page["hasCSV"] = "results.csv" in fileList
    page["hasCSV_comma"] = "results_comma.csv" in fileList

    page["westFolders"]=[]
    for f in fileList:
      if f[0:7]=="western" and f[8:].isdigit():
        page["westFolders"].append(int(f[8:]))
    page["westFolders"].sort()
    page["name"]=name
    print page["westFolders"]
    return(page)

  @expose()
  def killPanpan(self,name=""):
    if not name in os.listdir(resultFolder):
      redirect("index?message=Cannot+read+Panpan!")
    if not "status.json" in os.listdir(resultFolder+name):
      redirect("viewPanPan?name=%s&message=Cannot+get+panpan+status!"%name)
    pInfo={}
    with open(resultFolder+name+"/status.json","r") as f:
        pInfo=json.load(f)
    if commands.getstatusoutput("ps -p %s -o comm="%pInfo['pid'])[1]!=pInfo['pName']:
      redirect("viewPanPan?name=%s&message=Cannot+find+process+to+kill!"%name)
    else:
      os.system("kill %s"%pInfo['pid'])
    pInfo['pid']=-1
    pInfo['date']=-1
    #pInfo['processingStep']='killed'
    with open(resultFolder+name+"/status.json",'w') as statusJSON:
      statusJSON.write(json.dumps(pInfo))
    redirect("viewPanPan?name=%s&message=Panpan+killed+successfully!&mType=Info"%name)

  @expose()
  def launchJob(self,name="",action=""):
    if not(checkGoodName(name)):
      redirect("index?message=Invalid+request")
    else:
      if not action in ["all","getWesterns","computeBackground","getLumi"]:
        redirect("index?message=Invalid+request")
    os.system("pwd")
    cmd = "%s/panpan/serverScripts/launchJob.sh %s %s %s %s &"%(SERVER_PATH,PANPAN_PATH,SERVER_PATH,resultFolder,name)
    #print cmd
    os.system(cmd)
    redirect("viewPanPan?name=%s"%name)

  @expose("panpan.templates.about")
  def about(self):
    return({})
  
  @expose("panpan.templates.status")
  def jobStatus(self,name=""):
    os.system("pwd")
    os.system("ls "+resultFolder+name)
    print resultFolder+name
    if not "status.json" in os.listdir(resultFolder+name):
      page={}
      page['name']=name
      page['gotJSON']=False
      return(page)
    else:
      page={}
      with open(resultFolder+name+"/status.json","r") as f:
        page=json.load(f)
      page['gotJSON']=True
      page['done'] = page['processingStep']=="done"
      page['stalled']=((time.time()-float(page['date']))>30)
      if page['done']:
        page['stalled']=False
      page['name']=name
      return(page)

  @expose('panpan.templates.include')
  def include(self):
     return {}

  @expose()
  def deletePanpan(self,name):
    if not (checkGoodName(name)):
      redirect("index?message=Invalid+request")
    if not name in os.listdir(resultFolder):
      redirect("index?message=Invalid+request")
    os.system("rm -r %s/%s"%(resultFolder,name))
    redirect("index?message=Panpan+deleted+successfully.&mType=info")

  @expose("panpan.templates.viewWest")
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
      page["summary"]=open(resultFolder+name+"/western_"+west+"/summary.txt","r").read()


    return(page)
