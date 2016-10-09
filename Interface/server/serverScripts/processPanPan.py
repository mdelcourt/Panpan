import sys,os
from Backend.backendLib import *
from Backend.imageGenerator import *



from PIL import Image, ImageFilter
from Backend.backendLib import *
import time

init_time = time.time()

from ROOT import *

#Read image
im = Image.open( 'image.png' )
#Display image
#im.show()

pix=im.load()
outIm = im.copy()
outPix = outIm.load()

(sx,sy)=im.size

westernId = 0
result = []
for w in getWesterns(pix,sx,sy):
  (bkg,sigma) = getBkg(pix,w)
  print "Background = %s pm %s"%(bkg,sigma)
  if conf.useRoot:
    printWestern(pix,w,0)
  (bkgPro,mask) = getBkgProfile(pix,w,bkg,sigma)
  lumi = getLumiProfile(pix,w,bkgPro)
  peaks = getPeaks(lumi,w)
  intensity = computeIntensity(peaks,lumi)

  print "Intensity : %s"%intensity

  maxIntensity = sum(intensity)

  summary = "Normalized intensity :\n"
  for i in range(len(intensity)):
    summary+="Peak %s : %s\n"%(i,intensity[i]*1./maxIntensity)
  init2 = time.time()

  outIm = getOutIm(outIm,w,mask)
  canvasId=0
  os.system("mkdir w%s"%westernId)
  with open("w%s/summary.txt"%westernId,"w") as f:
    f.write(summary)
  print "Mem dump : %s"%len(memDump)
  for x in memDump:
    if type(x)==TCanvas:
      x.Print("w%s/canvas_%s.png"%(westernId,canvasId))
      memDump.remove(x)
      canvasId+=1
  westernId+=1

#print memDump


outIm.show()
term_time = time.time()

print "time: " + str(term_time-init_time)
