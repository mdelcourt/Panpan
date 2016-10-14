from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
from Backend.backendConfig import *
from Backend.western import *


conf = backendConfig()
if conf.useRoot:
    from ROOT import *

if conf.useNumpy:
  import pylab

#Read image
im = Image.open( './Ressources/LPSK16001_3.png' )


pix=im.load()
#copy image for output editing
outIm = im.copy()

(sx,sy)=im.size

intensitys=[] # for debug
w_index = -1 # for debug
a=0 # for debug
for w in getWesterns(pix,sx,sy,conf):
# to limit the number of westerns analysed (a bit faster for testing)
  a+=1
  w_index +=1
  (bkg,sigma) = w.getBkg(pix)
  w.genLumiHist()
  print "Background = %s pm %s"%(bkg,sigma)

  w.setWesternImage(im)
  westernimage = w.getWesternImg()
  westernimage.save("western_raw_"+str(w_index)+".png")
  #westernimage.show()
  w.printWestern(pix,bkg)
  w.calcBkgProfile(pix,bkg,sigma)
  bkgPro = w.getBkgProfile()
  #mask = w.getMask() # not useful, except if you want the mask matrix
  lumi = w.getLumiProfile(pix,bkgPro)

  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  #creation des figures
  w.genBkgProfileHist()
  w.genBkgMatrix()
  w.genPeakLumiProfile()

  outIm = w.addBkgMask(outIm) # always after calcBkgProfile!

  intens = w.computeIntensity() # on en fait rien mais toi oui, sans doute

# limit the number of westerns analysed (faster for testing)
  #if a == 10:
    #break

# save the outpu image with foreground contour masks.
outIm.save("outim.png")

if conf.useNumpy:

  pylab.close()
