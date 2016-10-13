
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


pix=im.load()
#copy image for output editing
outIm = im.copy()

(sx,sy)=im.size

intensitys=[]
w_index = -1 # for debug

for w in getWesterns(pix,sx,sy):
  w_index +=1
  getw=time.time()
  (bkg,sigma) = w.getBkg(pix)
  w.genLumiHist()
  print "Background = %s pm %s"%(bkg,sigma)

  w.setWesternImage(im)
  westernimage = w.getWesternImg()
  #westernimage.show()
  w.printWestern(pix,bkg)
  w.calcBkgProfile(pix,bkg,sigma)
  bkgPro = w.getBkgProfile()
  mask = w.getMask()
  lumi = w.getLumiProfile(pix,bkgPro)

  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  #creation des figures
  w.genBkgProfileHist()
  w.genBkgMatrix()
  w.genPeakLumiProfile()
  #print "peaks"
  #print peaks

  outIm = w.addBkgMask(outIm)

  #westernimage.save("western "+str(w_index)+".png")

  #test des intensites finales
  intensitys.append(w_index)
  intens = w.computeIntensity()
  pctintens = [i/sum(intens) for i in intens]
  intensitys.append( pctintens)
  #break

# to limit the number of westerns analysed (a bit faster for testing)
  #numTimes+=1
  #if numTimes == 10:
    #break

term_time = time.time()

print "time: " + str(term_time-init_time)
print "AvTime: " + str((term_time-init_time)/w_index)

outIm.save("outim.png")
for i in intensitys:
  print i

#pylab.show()
#a= raw_input("input")
pylab.close()
#outIm.show()

