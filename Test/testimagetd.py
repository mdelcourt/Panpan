
from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
from Backend.imageGenerator import *

from Backend.western import *

import time


init_time = time.time()

if conf.useRoot:
    from ROOT import *
    print "ROOT imported"
else:
    print "ROOT not imported"
#Read image
im = Image.open( './Ressources/LPSK16001_3.png' )


openim=time.time()
print "open"+str(openim-init_time)
pix=im.load()
loadim=time.time()
print "loadim"+str(loadim-openim)
#copy image for output editing
outIm = im.copy()
copyim=time.time()
print "copyim"+str(copyim-loadim)
(sx,sy)=im.size

numTimes = 0

for w in getWesterns(pix,sx,sy):
  getw=time.time()
  print "getw"+str(getw-copyim)
  (bkg,sigma) = w.getBkg(pix)
  w.genLumiHist()
  print "Background = %s pm %s"%(bkg,sigma)
  if conf.useRoot:
    printWestern(pix,w,0)
  w.calcBkgProfile(pix,bkg,sigma)
  w.genBkgProfileHist()
  bkgPro = w.getBkgProfile()
  mask = w.getMask()
  lumi = w.getLumiProfile(pix,bkgPro)

  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  w.genLumiProfileHist()

  #outIm = w.addBkgMask(outIm)
  #tempwesternimage = w.getWesternImg()
  #tempwesternimage.show()

  numTimes+=1
  if numTimes == 1:
    break


#outIm.show()
term_time = time.time()

print "time: " + str(term_time-init_time)
print "AvTime: " + str((term_time-init_time)/numTimes)
