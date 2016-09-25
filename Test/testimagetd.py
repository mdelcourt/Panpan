
from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
from Backend.imageGenerator import *
import time


init_time = time.time()

if conf.useRoot:
    from ROOT import *
    print "ROOT imported"
else:
    print "ROOT not imported"
#Read image
im = Image.open( './Ressources/LPSK16001_3.png' )

pix=im.load()

#copy image for output editing
outIm = im.copy()

(sx,sy)=im.size

listTimes=[]
listTimes2=[]


for w in getWesterns(pix,sx,sy):
  (bkg,sigma) = getBkg(pix,w)
  print "Background = %s pm %s"%(bkg,sigma)
  if conf.useRoot:
    printWestern(pix,w,0)
  (bkgPro,mask) = getBkgProfile(pix,w,bkg,sigma)
  lumi = getLumiProfile(pix,w,bkgPro)
  peaks = getPeaks(lumi,w)

  init2 = time.time()
  #for i in range(1):

  outIm = getOutIm(im,w,mask)
  listTimes.append(time.time()-init2)

  #init3 = time.time()
  #for i in range(1):

     #outIm = getOutIm2(outIm,w,mask)
     #listTimes2.append(time.time()-init3)

outIm.show()
term_time = time.time()

print "time: " + str(term_time-init_time)

#avtimes = 0
#for i in listTimes:
    #avtimes+=i
#print str(avtimes/len(listTimes))

#avtimes = 0
#for i in listTimes2:
    #avtimes+=i
#print str(avtimes/len(listTimes2))
