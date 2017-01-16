#!/usr/bin/python

import os,csv,commands
print os.environ['PYTHONPATH']

from PIL import Image, ImageFilter
import matplotlib
matplotlib.use('Agg')
import sys,json,time
from Backend.backendLib import *

from Backend.western import *

if conf.useRoot:
    from ROOT import *

if conf.useNumpy:
  import pylab

status = {'imageRecognised':'?',
          'nWestern':'?',
          'processingStep':'starting',
          'date':time.time(),
          'beingProcessed':'none',
          'pid':os.getpid(),
          'pName':commands.getstatusoutput("ps -p %s -o comm="%os.getpid())[1]
           }
with open('status.json','w') as statusJSON:
  statusJSON.write(json.dumps(status))

def updateJSON(key,value):
  status[key]=value
  status['date']=time.time()
  with open('status.json','w') as statusJSON:
    statusJSON.write(json.dumps(status))


#Read image
im = Image.open( 'image.png' )

pix=im.load()
#copy image for output editing
outIm = im.copy()
updateJSON('imageRecognised',True)
(sx,sy)=im.size

intensitys=[] # for debug
w_index = -1 # for debug
a=0 # for debug
westernList = getWesterns(pix,sx,sy)
updateJSON('nWestern',len(westernList))

finalResult = []

for w in getWesterns(pix,sx,sy):
# to limit the number of westerns analysed (a bit faster for testing)
  a+=1
  updateJSON('beingProcessed',a)
  updateJSON('processingStep','creating dir...')
  w_index +=1
  os.system("mkdir western_%s"%w_index)
  path_="./western_%s/"%w_index
  updateJSON('processingStep','getting bkg...')
  (bkg,sigma) = w.getBkg(pix)
  updateJSON('processingStep','generating bkg plot...')
  w.genLumiHist(path=path_)
  print "Background = %s pm %s"%(bkg,sigma)
  updateJSON('processingStep','cropping western...')
  w.setWesternImage(im)
  westernimage = w.getWesternImg()
  westernimage.save(path_+"western_raw_"+str(w_index)+".png")
  #westernimage.show()
  w.printWestern(pix,bkg,path=path_)
  updateJSON('processingStep','computing background...')
  w.calcBkgProfile(pix,bkg,sigma)
  bkgPro = w.getBkgProfile()
  #mask = w.getMask() # not useful, except if you want the mask matrix
  updateJSON('processingStep','computing luminosity...')
  lumi = w.getLumiProfile(pix,bkgPro)

  updateJSON('processingStep','computing peaks...')
  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  #creation des figures
  updateJSON('processingStep','generating plots...')
  w.genBkgProfileHist(path=path_)
  w.genBkgMatrix(path=path_)
  w.genPeakLumiProfile(path=path_)
  updateJSON('processingStep','generating out image...')
  outIm = w.addBkgMask(outIm) # always after calcBkgProfile!

  updateJSON('processingStep','integrating luminosity')
  intens = w.computeIntensity() # on en fait rien mais toi oui, sans doute
  finalResult.append(intens)
  maxIntensity = sum(intens)

  summary = "Normalized intensity :\n"
  for i in range(len(intens)):
    summary+="Peak %s : %s\n"%(i,intens[i]*1./maxIntensity)

  with open("western_%s/summary.txt"%w_index,"w") as f:
    f.write(summary)

# limit the number of westerns analysed (faster for testing)
  #if a == 10:
    #break
updateJSON('processingStep','done')
# save the outpu image with foreground contour masks.
outIm.save("outim.png")

maxSize = 0
for w in finalResult:
  if len(w)>maxSize:
    maxSize = len(w)

csvList = []

line = ['' for i in range(3*maxSize+2+1)]

line[1]               = "Raw intensity"
line[maxSize+2+1]     = "Relative intensity"
line[2*(maxSize+2)+1] = "Normalized intensity"
csvList.append(line)
wId = 0
for w in finalResult:
  line = ['' for i in range(3*(maxSize+2)+1)]
  maxIntens   = max(w)
  totalIntens = sum(w)
  line[0] = "Western %s"%wId
  wId+=1
  for i in range(len(w)):
    line[i+1]           = w[i]
    line[maxSize+2+i+1] = w[i]*1./maxIntens
    line[2*(maxSize+2)+i+1] = w[i]*1./totalIntens
  csvList.append(line)

csvName="results.csv"
with open(csvName,"wb") as csvFile:
    r=csv.writer(csvFile,delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE)
    for l in csvList:
      r.writerow([i for i in l])

csvName="results_comma.csv"
with open(csvName,"wb") as csvFile:
    r=csv.writer(csvFile,delimiter=';', quotechar='|', quoting=csv.QUOTE_NONE)
    for l in csvList:
      r.writerow([str(i).replace(".",",") for i in l])




if conf.useNumpy:

  pylab.close()
