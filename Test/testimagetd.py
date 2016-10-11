
from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
from Backend.imageGenerator import *

from Backend.western import *

import time
import pylab


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

fignum = 0
intensitys=[]
w_index = -1
for w in getWesterns(pix,sx,sy):
  w_index +=1
  getw=time.time()
  print "getw"+str(getw-copyim)
  (bkg,sigma) = w.getBkg(pix)
  w.genLumiHist(fignum)
  print "Background = %s pm %s"%(bkg,sigma)

  w.setWesternImage(im)
  westernimage = w.getWesternImg()
  westernimage.show()
  w.printWestern(pix,fignum,bkg)
  w.calcBkgProfile(pix,bkg,sigma)
  w.genBkgProfileHist(fignum)
  w.genBkgMatrix(fignum)
  bkgPro = w.getBkgProfile()
  mask = w.getMask()
  lumi = w.getLumiProfile(pix,bkgPro)

  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  w.genPeakLumiProfile(fignum)

  outIm = w.addBkgMask(outIm)


  westernimage.save("western "+str(w_index)+".png")

  #test des intensites finales
  intensitys.append(w_index)
  intens = w.computeIntensity()
  normintens = [i/sum(intens) for i in intens]
  intensitys.append( normintens)


# to limit the number of westerns analysed (a bit faster for testing)
  numTimes+=1
  if numTimes == 10:
    break
outIm.save("outim.png")
print intensitys
#pylab.show()
#a= raw_input("input")
pylab.close()
#outIm.show()
term_time = time.time()

print "time: " + str(term_time-init_time)
print "AvTime: " + str((term_time-init_time)/numTimes)
