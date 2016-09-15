from ROOT import *
from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *

#Read image
im = Image.open( '../Ressources/LPSK16001_3.png' )
#Display image
#im.show()

pix=im.load()

(sx,sy)=im.size


for w in getWesterns(pix,sx,sy):
  (bkg,sigma) = getBkg(pix,w)
  print "Background = %s pm %s"%(bkg,sigma)
  printWestern(pix,w,0)
  bkgPro = getBkgProfile(pix,w,bkg,sigma)
  lumi = getLumiProfile(pix,w,bkgPro)
  peaks = getPeaks(lumi,w)
