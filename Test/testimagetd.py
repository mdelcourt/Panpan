from PIL import Image, ImageFilter
import sys
from Backend.backendLib import *
from Backend.backendConfig import *
from Backend.western import *
import pylab


conf = processConfig()
if conf.useRoot:
    from ROOT import *

#from pylab import *
#from numpy import outer
#rc('text', usetex=False)
#a=outer(arange(0,1,0.01),ones(10))
#figure(figsize=(10,5))
#subplots_adjust(top=0.8,bottom=0.05,left=0.01,right=0.99)
#maps=[m for m in cm.datad if not m.endswith("_r")]
#maps.sort()
#l=len(maps)+1
#for i, m in enumerate(maps):
    #subplot(1,l,i+1)
    #axis("off")
    #imshow(a,aspect='auto',cmap=get_cmap(m),origin="lower")
    #title(m,rotation=90,fontsize=10)
#savefig("colormaps.png",dpi=100,facecolor='gray')

#Read image
im = Image.open( './Ressources/LPSK16001_3.png' )



pix=im.load()
#copy image for output editing
outIm = im.copy()

(sx,sy)=im.size

intensitys=[] # for debug
w_index = -1 # for debug
a=0 # for debug

westernPath = "./Data_out/1/" # temporary
for w in getWesterns(pix,sx,sy,conf,westernPath):


# to limit the number of westerns analysed (a bit faster for testing)
  a+=1
  w_index +=1
  (bkg,sigma) = w.getBkg(pix)
  w.genLumiHist()
  print "Background = %s pm %s"%(bkg,sigma)

  w.setWesternImg(im)
  w.genWesternImg()

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

  w.addBkgMask(outIm) # always after calcBkgProfile!
  w.genOutWesternImg()

  intens = w.computeIntensity() # on en fait rien mais toi oui, sans doute

# limit the number of westerns analysed (faster for testing)
  #if a == 10:
    #break

# save the outpu image with foreground contour masks.
outIm.save("outim.png")

if conf.useNumpy:

  pylab.close()
