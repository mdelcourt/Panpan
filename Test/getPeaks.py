
from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
import time

init_time = time.time()

if conf.useRoot:
    from ROOT import *
    print "ROOT imported"
else:
    print "ROOT not imported"
#Read image
im = Image.open( './Ressources/LPSK16001_3.png' )
#Display image
#im.show()

pix=im.load()
outIm = im.copy()
outPix = outIm.load()

(sx,sy)=im.size

listTimes=[]
listTimes2=[]

nWest = 0

for w in getWesterns(pix,sx,sy):
  nWest+=1
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

  print "Normalized intensity :"
  for i in range(len(intensity)):
    print "Peak %s : %s"%(i,intensity[i]*1./maxIntensity)
  init2 = time.time()
  #for i in range(1):

  outIm = getOutIm(outIm,w,mask)
  listTimes.append(time.time()-init2)
  break
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
