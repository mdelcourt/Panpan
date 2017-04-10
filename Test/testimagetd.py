from PIL import Image, ImageFilter
import sys, os
from Backend.backendLib import *
from Backend.backendConfig import *
from Backend.western import *
import pylab



PanPanPath =  os.environ['PANPANPATH']   #TO BE UPDATED FOR SERVER (path of PanPan project)
OutputPath =  PanPanPath+"/Data_out/1/" # temporary (path  of output data - for tests, all westerns in one)
procConfPath = PanPanPath+"/Data_out/"
procConfName = "PConf.json"

westConfPath = PanPanPath+"/Data_out/1" # temporary   config path for one western (but for tests, all westerns)
westConfName = "testconf.json"

# load process config file.
conf = processConfig(procConfPath,procConfName)

if conf.useRoot:
    from ROOT import *


im = Image.open( PanPanPath+'/Ressources/LPSK16001_3.png' )  # TO BE UPDATED FOR SERVER



pix=im.load()
#copy image for output editing
outIm = im.copy()

(sx,sy)=im.size

intensitys=[] # for debug
w_index = -1 # for debug
a=0 # for debug



for w in getWesterns(pix,sx,sy,conf,westConfPath,westConfName): # generates western objects and iterates over them


# to limit the number of westerns analysed (a bit faster for testing)
  a+=1
  w_index +=1
  if a>0:

    print "analysing western nr "+str(w.ind)
    (bkg,sigma) = w.getBkg(pix)
    w.genLumiHist(path = OutputPath)
    #print "Background = %s pm %s"%(bkg,sigma)

    w.setWesternImg(im)
    w.genWesternImg(path = OutputPath)

    #westernimage.show()
    w.printWestern(pix,bkg,path = OutputPath)
    w.calcBkgProfile(pix,bkg,sigma)
    bkgPro = w.getBkgProfile()
    #mask = w.getMask() # not useful, except if you want the mask matrix
    lumi = w.getLumiProfile(pix,bkgPro)

    peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
    #creation des figures
    w.genBkgProfileHist(path = OutputPath)
    w.genBkgMatrix(path = OutputPath)
    w.genPeakLumiProfile(path = OutputPath)

    w.addBkgMask(outIm) # always after calcBkgProfile!
    w.genOutWesternImg(path = OutputPath)


    intens = w.computeIntensity() # on en fait rien mais toi oui, sans doute

# limit the number of westerns analysed (faster for testing)
  #if a == 10:
    #break

# save the outpu image with foreground contour masks.
outIm.save(OutputPath + "outim.png")

if conf.useNumpy:

  pylab.close()
