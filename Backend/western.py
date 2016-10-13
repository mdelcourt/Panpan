from backendConfig import backendConfig
from PIL import Image

import time

conf = backendConfig

if conf.useNumpy:
  #import numpy as np
  import pylab


class western(object,conf):
  """Class western. """

  classType = "western"
  count = 0

  def __init__(self,x0=0,x1=0,y0=0,y1=0):
    self.__class__.count += 1

    self.setCoordinates((x0,x1,y0,y1))

    self.ind = self.__class__.count

    self.mask = list()
    self.memDump = list()
    self.westernMatrix = list()
    self.bkgProfile = list()
    self.bkgMatrix = list()
    self.bkgProfileHist = list()
    self.lumiProfile = list()
    self.blotLumiProfile = list()
    self.trends = list()
    self.mergedTrends = list()
    self.stableTrends = list()
    self.mergedPeaks = list()
    self.westernImg = Image.Image()
    self.westernImgset = False
    self.intensity = list()


  def getBkgProfile (self):
    return self.bkgProfile

  def getMask(self):
    return self.mask

  def getWesternImg(self):
    """ returns western image
    """
    return self.westernImg

  def saveWesternImg(self):
    """ returns western image
    """
    return self.westernImg

  def setCoordinates(self,coord):
    if self.checkInputCoordinates(coord):
      self.x0 = coord[0]
      self.x1 = coord[1]
      self.y0 = coord[2]
      self.y1 = coord[3]
    else:
      raise TypeError("Wrong coordinates: "+str(coord)+" Should be of type (int, int, int, int).")


  def checkInputCoordinates(self,coord):
    """ Returns True if coord is correctly formatted, False otherwise."""
    returnVal = True
    if type(coord) is tuple and len(coord)==4:
      for el in coord:
        if type(el) is not int or el < 0:
          returnVal = False
          break
    else:
      returnVal = False
    return returnVal

  def getCoordinates(self):
    return (self.x0, self.x1, self.y0, self.y1)

  def setMask(self,inMask):
    self.mask = inMask

  def initMask(self):
    self.mask = [[0 for i in range(self.y0,self.y1)] for j in range(self.x0,self.x1)]

  def setWesternImage(self,mainImg):
    self.westernImg = mainImg.crop((self.x0,self.y0, self.x1,self.y1))
    #self.westernImg  = self.westernImg.load()
    self.westernImgset = True

  def getBkg(self,pix):
    """ returns background and sigma."""
    if conf.debug:
      print 'getBkg'

    if conf.useRoot:
      self.lumiProfile = [0 for i in range(0,255)]
      h = TH1I("h%s"%len(self.memDump),"h",256,0,256)
      self.memDump.append(h)
      for x in range(self.x0,self.x1):
        for y in range(self.y0,self.y1):
          self.lumiProfile[int(self.getLumi(pix[x,y]))]+=1
          h.Fill(self.getLumi(pix[x,y]))

    if conf.useNumpy:
      self.lumiProfile = [0 for i in range(0,255)]
      for x in range(self.x0,self.x1):
        for y in range(self.y0,self.y1):
          self.lumiProfile[int(self.getLumi(pix[x,y]))]+=1

    if not conf.useNumpy and not conf.useRoot:
      self.lumiProfile = [0 for i in range(0,255)]
      for x in range(self.x0,self.x1):
        for y in range(self.y0,self.y1):
          self.lumiProfile[int(self.getLumi(pix[x,y]))]+=1


    if conf.useRoot:
      self.memDump.append(TCanvas())
      h.Draw("hist")

    mLumi = max(self.lumiProfile)
    inMaximum=False
    bkg0 = 0
    bkg1 = 0
    bkg  = 0
    for i in range(len(self.lumiProfile)):
      l = self.lumiProfile[i]
      if not inMaximum and l>mLumi/2.:
        inMaximum=True
        bkg0 = i
      if l==mLumi:
        bkg=i
      if inMaximum and l<mLumi/2.:
        inMaximum = False
        bkg1 = i
        if bkg<bkg1 and bkg>bkg0:
          break
    if conf.bkgEstim.lower()=="average":
      bkg=(bkg0+bkg1)/2.
    sigma = (bkg1-bkg0)/2.355
    return(bkg,sigma)
    #print "Background = %s, [between %s and %s]"%(bkg,bkg0,bkg1)


  def getLumi(self,pix):
    #l = 3*((255-pix[0])*(255-pix[1])*(255-pix[2]))**1/3.
    l = 255.-((pix[0]+pix[1]+pix[2])/3.)
    return l


  def calcBkgProfile(self,pix,bkg=0,sBkg=0):
    """ calculates background and also mask matrix to draw contours of foreground.
    """
    if conf.debug:
      print 'calcBkgProfile'

    self.initMask()
    if conf.useRoot:
      h_bkgProfile= TH1F("h%s"%len(self.memDump),"Bkg profile",self.x1-self.x0,self.x0,self.x1)
      self.memDump.append(h_bkgProfile)
      h_west = TH2I("hist%s"%len(self.memDump),"Western",self.x1-self.x0,self.x0,self.x1,self.y1-self.y0,self.y0,self.y1)
      self.memDump.append(h_west)
    #if conf.useNumpy:
    #array inverse (y puis x)
    self.bkgMatrix = [[int() for x in range(self.x0,self.x1) ] for y in range(self.y0,self.y1)]
    Lmin = 255
    LMax = 0
    for x in range(self.x0,self.x1):
      nPixBkg= 0
      bkgTot = 0
      for y in range(self.y0,self.y1):
        l = self.getLumi(pix[x,y])
        if l<(bkg+conf.nSigmaBkg*sBkg):
          if l>0 and l<Lmin:
            Lmin=l
          if l>LMax:
            LMax=l
          if conf.useRoot:
            h_west.Fill(x,y,l)
          if conf.useNumpy:
            self.bkgMatrix[y-self.y0][x-self.x0] = l
          bkgTot+=l
          nPixBkg+=1
        else:
          self.mask[x-self.x0][y-self.y0]=1
      if nPixBkg==0:
        nPixBkg=1
      self.bkgProfile.append(bkgTot*1./nPixBkg)
      if conf.useRoot:
        h_bkgProfile.Fill(x,bkgTot*1./nPixBkg)

    if conf.useRoot:
      self.memDump.append(TCanvas())
      h_bkgProfile.Draw("hist")
      self.memDump.append(TCanvas())
      h_west.GetZaxis().SetRangeUser(Lmin-1,LMax+1)
      h_west.Draw("colz")


  def getPeaks(self):
    """ returns merged peaks (i guess...) """
    if conf.debug:
      print 'getPeaks'
    self.getTrends()
    #print "trends"
    #print self.trends
    for t in self.trends:
      if t[1]-t[0]>=conf.nTrend:
        #print "%s %s %s"%(t[0],t[1],conf.nTrend)
        self.stableTrends.append(t)
    if conf.useRoot:
      self.h_lumiProfile = TH1F("h%s"%len(self.memDump),"xLumiProfile",len(self.blotLumiProfile),0,len(self.blotLumiProfile))
      self.memDump.append(self.h_lumiProfile)

    for x in range(len(self.blotLumiProfile)):
      l=self.blotLumiProfile[x]
      if conf.useRoot:
        self.h_lumiProfile.Fill(x,l)
    if conf.useRoot:
      self.memDump.append(TCanvas())
      self.h_lumiProfile.Draw("hist")

    self.trendMerger()
    for t in self.mergedTrends:
      if conf.useRoot:
        h_line = TLine(t[0],self.blotLumiProfile[t[0]],t[1],self.blotLumiProfile[t[1]])
        if t[2]>0:
          h_line.SetLineColor(kGreen+1)
        else:
          h_line.SetLineColor(kRed+1)
        h_line.SetLineWidth(3)
        self.memDump.append(h_line)
        h_line.Draw()

    for t in self.stableTrends:
      if conf.useRoot:
        h_line = TLine(t[0],self.blotLumiProfile[t[0]],t[1],self.blotLumiProfile[t[1]])
        if t[2]>0:
          h_line.SetLineColor(kGreen+1)
        else:
          h_line.SetLineColor(kRed+1)
        h_line.SetLineWidth(1)
        self.memDump.append(h_line)
        h_line.Draw()

    self.mins = []
    prevT = [0,0,-1]
    for t in self.mergedTrends:
      if prevT[2]<0 and t[2]>0:
        #print "Found minimum at : %s %s"%(prevT[1],t[1])
        self.mins.append((prevT[1]+t[0])/2.)

      prevT=t
    if prevT[2]<0:
      print "Added boundary min at %s"%prevT[1]
      self.mins.append(prevT[1])
    if len(self.mins)<1:
      print "ERROR, no minimums found..."
      return([])
    if conf.useRoot:
      for m in self.mins:
        h_line = TLine(m,0,m,2000)
        h_line.SetLineWidth(1)
        h_line.SetLineStyle(3)
        self.memDump.append(h_line)
        h_line.Draw("hist")
    self.peaks = []
    peakStart = self.mins[0]
    peakStop = 0
    prevMin = self.mins[0]

    for m in self.mins[1:]:
      #print peakStart
      #print m
      maxi = max(self.blotLumiProfile[int(peakStart):int(m)])
      minLum = self.blotLumiProfile[int(m)]
      if minLum>0.5*maxi:
        print "Removing minimum %s (%s >50%% of max (%s))"%(m,minLum,maxi)
      else:
        peakStop = m
        self.peaks.append([peakStart,peakStop])
        peakStart= m
    #Merging peaks if too small
    avSize=0
    for p in self.peaks:
      pSize = p[1]-p[0]
      avSize +=pSize*1./len(self.peaks)
    
    for i in range(len(self.peaks)):
      p = self.peaks[i]
      pSize = p[1]-p[0]
      if pSize<conf.peakMergeThresh*avSize:
        print "Peak under threshold !"
        print "Attempt to merge..."
        if i == len(self.peaks)-1:
          print "Last peak ! Unable to merge !"
        else:
          nP = self.peaks[i+1]
          if pSize+(nP[1]-nP[0])>conf.peakAfterMergeThresh*avSize:
            print "Peak would be too big after merging, aborting !"
          else:
            print "Merging peaks..."
            self.peaks[i+1][0]=p[0]
      else:
        self.mergedPeaks.append(p)

    if len(self.mergedPeaks)<1:
      print "ERROR, no merged peaks..."
      return([])
    if conf.useRoot:
      for p in self.mergedPeaks:
        h_line = TLine(p[0],0,p[0],2000)
        h_line.SetLineWidth(3)
        self.memDump.append(h_line)
        h_line.Draw("hist")
      h_line = TLine(p[1],0,p[1],2000)
      h_line.SetLineWidth(3)
      self.memDump.append(h_line)
      h_line.Draw("hist")
    return(self.mergedPeaks)


  def getTrends(self):
    """ get trends for peak definition
    """
    if conf.debug:
      print 'getTrends'
    t                 = [0,0,-1]
    prevLumi          = -1
    for x in range(len(self.blotLumiProfile)):
      l=self.blotLumiProfile[x]

      if l > prevLumi + 1e-5:
        if t[2]<0: #Previous trend was decreasing
          t[1] = x-1
          self.trends.append(t)
          t = [x,0,1]
      if l < prevLumi - 1e-5:
        if t[2]>0: #Previous trend was decreasing
          t[1] = x-1
          self.trends.append(t)
          t = [x,0,-1]
      if l<1e-5:
        t[1] = x-1
        self.trends.append(t)
        t = [x,0,-1]
      prevLumi=l
    #return (self.trends)


  def trendMerger(self):
    """ merge trends... I guess? for peak definition
    """

    if conf.debug:
      print 'trendMerger'
    prevSign = 0
    prevTrend = [0,0,0]
    for t in self.stableTrends:
      if not t[2] == prevTrend[2]:
        if not prevTrend[2] == 0:
          self.mergedTrends.append(prevTrend)
        prevTrend = [t[0],t[1],t[2]]
      else:
        prevTrend[1] = t[1]
    self.mergedTrends.append(prevTrend)

  def genPeakLumiProfile (self,name="",path=""):
    """ generate and save on disk luminosity profile of blots along X axis """
    if name == "":
      name = path+"Luminosity "+str(self.ind)+".svg"
    if conf.useNumpy:
      #print "lenself.blotLumiProfile"+str(len(self.blotLumiProfile))
      pylab.figure()
      pylab.bar(range(len(self.blotLumiProfile)),self.blotLumiProfile,width=1,color="#3C0D6E",edgecolor="#220740",linewidth=0.1)
      pylab.title(name)
      #for p in self.peaks:
        #pylab.plot([p[0],p[0]],[0,2000],color = "orange")
        #pylab.axvline(x=p[0], ymin=0, ymax=2000)
      #pylab.axvline(x=self.peaks[-1][1], ymin=0, ymax=0.2, color = "orange")
      for mp in self.mergedPeaks:
        pylab.plot([mp[0],mp[0]],[0,2000],linewidth=2,color = "blue")
        #pylab.axvline(x=mp[0], ymin=0, ymax=2000)
      pylab.plot([self.mergedPeaks[-1][1],self.mergedPeaks[-1][1]],[0,2000],linewidth=2,color = "blue")
      #pylab.axvline(x=self.mergedPeaks[-1][1], ymin=0, ymax=0.2, color = "blue")

      pylab.savefig(name,format='svg')
      #pylab.show()
      #pylab.close()


  def genLumiHist(self,name="",path=""):
    """ generates and saves on disk luminosity profile of western (not only blots; blots+bckgrnd)"""
    if conf.useNumpy:
      if name == "":
        name = path+"Luminosite. Western "+str(self.ind)+".svg"
      #print "lenself.lumiProfile"+str(len(self.lumiProfile))
      pylab.figure()
      pylab.bar([i for i in range(len(self.lumiProfile))],self.lumiProfile,width=1,color="#3C0D6E",edgecolor="#220740",linewidth=0.1)
      pylab.axis([0,256,0,10000])
      pylab.title(name)
      #pylab.show()
      pylab.savefig(name,format='svg')
      #pylab.close()


  def addBkgMask(self,outIm):
    """ add background/blot delimiting line on page image and western image.
    edits the western image but also the general page image.
    """
    if conf.debug:
      print 'addBkgMask'
    if not self.westernImgset:
      self.setWesternImage(outIm)

    for x in range(1,len (self.mask)-1):
      for y in range(1,len(self.mask[x])-1):
        if (self.mask[x][y] != self.mask[x][y+1]
        or self.mask[x][y] != self.mask[x+1][y]
        or self.mask[x][y] != self.mask[x+1][y+1]):
          outIm.putpixel((x+self.x0,y+self.y0),(0,0,255,255))
          self.westernImg.putpixel((x,y),(0,0,255,255))
    return outIm




  def getLumiProfile(self,pix,bkgPro):
    """ returns luminosity profile of blots along X axis"""
    if conf.debug:
      print 'getLumiProfile'
    i = 0
    #h_xLumiProfile= TH1F("h%s"%len(memDump),"xLumiProfile",x1-x0,x0,x1)
    #memDump.append(h_xLumiProfile)
    for x in range(self.x0,self.x1):
      sumX = 0
      for y in range(self.y0,self.y1):
        sumX += self.getLumi(pix[x,y])-bkgPro[i]
      i+=1
      self.blotLumiProfile.append(sumX)
      #h_xLumiProfile.Fill(x,sumX)
    #memDump.append(TCanvas())
    #h_xLumiProfile.Draw("hist")
    return(self.blotLumiProfile)

  def computeIntensity(self):
    """ compute intensity of peak. (+ half of last bin and half of next)
    """
    for p in self.mergedPeaks:
      lum = 0
      for x in range(int(p[0])+1,int(p[1])):
        lum+=self.blotLumiProfile[x]
      lum+=self.blotLumiProfile[int(p[0])]*0.5
      lum+=self.blotLumiProfile[int(p[1])]*0.5
      self.intensity.append(lum)
    return(self.intensity)

  def printWestern(self,pix,bkg=0,name="",title="",path=""):
    if name == "":
      name = path+"Western_"+str(self.ind)+".svg"
    if conf.useRoot:
      h_west = TH2I("hist%s"%len(self.memDump),"Western",self.x1-self.x0,self.x0,self.x1,self.y1-self.y0,self.y0,self.y1)
      for x in range(self.x0,self.x1):
        for y in range(self.y0,self.y1):
          l = self.getLumi(pix[x,y])-bkg
          if l<0:
            l=0
          h_west.Fill(x,y,l)
      c = TCanvas()
      h_west.Draw("colz")
      self.memDump.append(h_west)
      self.memDump.append(c)
    if conf.useNumpy:
      for y in range(self.y0,self.y1):
        self.westernMatrix.append(list())
        for x in range(self.x0,self.x1):
          self.westernMatrix[y-self.y0].append(self.getLumi(pix[x,y]))
      if title == "":
        title = "Western "+str(self.ind)
      pylab.figure()
      pylab.matshow(self.westernMatrix, cmap=pylab.cm.summer)
      pylab.title(title)
      pylab.colorbar()
      pylab.savefig(name,format='svg')


  def genBkgMatrix(self,name="",path="",title=""):
    """ generate background profile histogrm and saves it on disk"""
    if name == "":
      name = path+"bckgnd_"+str(self.ind)+".svg"
    if title == "":
        title = "background western "+str(self.ind)
    if conf.useNumpy:
      pylab.figure()
      pylab.matshow(self.bkgMatrix, cmap=pylab.cm.gnuplot2)
      pylab.title(title)
      pylab.colorbar()
      pylab.savefig(name,format='svg')
      #pylab.show()
      #pylab.close()


  def genBkgProfileHist(self,name="",path="",title=""):
    """ generate background profile histogrm and saves it on disk"""
    if name == "":
      name = path+"bckgnd_profile_"+str(self.ind)+".svg"
    if title == "":
      title = "background profile western "+str(self.ind)

    if conf.useNumpy:
      pylab.figure()
      #pylab.matshow(self.bkgProfile, cmap=pylab.cm.gnuplot2)
      #pylab.bar(range(len(self.bkgProfile)),self.bkgProfile,width=1,color="#3C0D6E",edgecolor="#220740",linewidth=0.1)
      pylab.plot(range(len(self.bkgProfile)),self.bkgProfile,color="#3C0D6E")
      pylab.title(title)
      #pylab.colorbar()
      pylab.savefig(name,format='svg')
      #pylab.show()
      #pylab.close()
