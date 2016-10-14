import os
print os.environ['PYTHONPATH']

from PIL import Image, ImageFilter
import sys,json,time
from Backend.backendLib import *

from Backend.western import *

if conf.useRoot:
    from ROOT import *

if conf.useNumpy:
  import pylab

status = {'imageRecognised':'?',
          'nWestern':'?',
          'processingStep':'starting',
          'date':time.time(),
          'beingProcessed':'none'
           }
with open('status.json','w') as statusJSON:
  statusJSON.write(json.dumps(status))

def updateJSON(key,value):
  status[key]=value
  status['date']=time.time()
  with open('status.json','w') as statusJSON:
    statusJSON.write(json.dumps(status))


#Read image
im = Image.open( 'image.png' )

pix=im.load()
#copy image for output editing
outIm = im.copy()
updateJSON('imageRecognised',True)
(sx,sy)=im.size

intensitys=[] # for debug
w_index = -1 # for debug
a=0 # for debug
westernList = getWesterns(pix,sx,sy)
updateJSON('nWestern',len(westernList))

for w in getWesterns(pix,sx,sy):
# to limit the number of westerns analysed (a bit faster for testing)
  a+=1
  updateJSON('beingProcessed',a)
  updateJSON('processingStep','creating dir...')
  w_index +=1
  os.system("mkdir western_%s"%w_index)
  path_="./western_%s/"%w_index
  updateJSON('processingStep','getting bkg...')
  (bkg,sigma) = w.getBkg(pix)
  updateJSON('processingStep','generating bkg plot...')
  w.genLumiHist(path=path_)
  print "Background = %s pm %s"%(bkg,sigma)
  updateJSON('processingStep','cropping western...')
  w.setWesternImage(im)
  westernimage = w.getWesternImg()
  westernimage.save(path_+"western_raw_"+str(w_index)+".png")
  #westernimage.show()
  w.printWestern(pix,bkg,path=path_)
  updateJSON('processingStep','computing background...')
  w.calcBkgProfile(pix,bkg,sigma)
  bkgPro = w.getBkgProfile()
  #mask = w.getMask() # not useful, except if you want the mask matrix
  updateJSON('processingStep','computing luminosity...')
  lumi = w.getLumiProfile(pix,bkgPro)

  updateJSON('processingStep','computing peaks...')
  peaks = w.getPeaks() # always after getLumiProfile in order to create lumiProfile.
  #creation des figures
  updateJSON('processingStep','generating plots...')
  w.genBkgProfileHist(path=path_)
  w.genBkgMatrix(path=path_)
  w.genPeakLumiProfile(path=path_)
  updateJSON('processingStep','generating out image...')
  outIm = w.addBkgMask(outIm) # always after calcBkgProfile!

  updateJSON('processingStep','integrating luminosity')
  intens = w.computeIntensity() # on en fait rien mais toi oui, sans doute

# limit the number of westerns analysed (faster for testing)
  #if a == 10:
    #break
updateJSON('processingStep','done')
# save the outpu image with foreground contour masks.
outIm.save("outim.png")

if conf.useNumpy:

  pylab.close()
