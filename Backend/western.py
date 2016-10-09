from backendConfig import backendConfig
from PIL import Image
#import numpy as np
import pylab


import time

conf = backendConfig


class western(object,conf):
  """Class western. """

  classType = "western"
  count = 0

  def __init__(self,x0=0,x1=0,y0=0,y1=0):
    self.__class__.count += 1

    self.setCoordinates((x0,x1,y0,y1))

    self.ind = self.__class__.count

    self.mask = list()
    self.listRootObjects = list()
    self.bkgProfile = list()
    self.bkgProfileHist = list()
    self.lumiProfile = list()
    self.lumiProfileHist = list()
    self.lumiList = list()
    self.trends = list()
    self.mergedTrends = list()
    self.stableTrends = list()
    self.mergedPeaks = list()
    self.westernImg = Image.Image()
    self.westernImgset = False

  def getInd(self):
    return self.ind

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

  def getBkg(self,pix):
    if conf.debug:
      print 'getBkg'

    self.lumiProfile = [0 for i in range(0,255)]
    if conf.useRoot:
      h = TH1I("h%s"%len(memDump),"h",256,0,256)
      memDump.append(h)
    t_avant_listes = time.time()

    if conf.useRoot:
      for x in range(self.x0,self.x1):
        for y in range(self.y0,self.y1):
          self.lumiProfile[int(self.getLumi(pix[x,y]))]+=1
          h.Fill(self.getLumi(pix[x,y]))

    for x in range(self.x0,self.x1):
      for y in range(self.y0,self.y1):
        self.lumiProfile[int(self.getLumi(pix[x,y]))]+=1

    #pour histogramme
    #self.lumiList = [self.getLumi(pix[x,y]) for x in range(self.x0,self.x1) for y in range(self.y0,self.y1)]

    if conf.useRoot:
      memDump.append(TCanvas())
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

  def genLumiHist(self,name=""):
    if conf.useNumpy:
      if name == "":
        name = "Histogramme Luminosite.Western "+str(self.ind)

      #t1 = time.time()
      #pylab.hist(self.lumiList,256)
      #pylab.close()
      #print "hist "+str(time.time()-t1)
      ##t1 = time.time()
      #pylab.plot([i for i in range(len(self.lumiProfile))],self.lumiProfile)
      #pylab.close()
      #print "plot "+str(time.time()-t1)
      ##t1 = time.time()
      pylab.bar([i for i in range(len(self.lumiProfile))],self.lumiProfile,width=1,color="#3C0D6E",edgecolor="#220740",linewidth=0.1)
      pylab.axis([0,256,0,10000])


      #pylab.close()
      #print "bar "+str(time.time()-t1)
      #t_apres_pylab = time.time()
      #print "t 3 liste"+str(t_apres_pylab-t_apres_listes)
      #print self.lumiProfile
      pylab.title(name)
      #pylab.show()
      pylab.savefig(name+".svg",format='svg')
      pylab.close()
      #self.lumiHistPlot.show()



  def getLumi(self,pix):
    #l = 3*((255-pix[0])*(255-pix[1])*(255-pix[2]))**1/3.
    l = 255.-((pix[0]+pix[1]+pix[2])/3.)
    return l


  def initMask(self):
    self.mask = [[0 for i in range(self.y0,self.y1)] for j in range(self.x0,self.x1)]

  def calcBkgProfile(self,pix,bkg=0,sBkg=0):
    if conf.debug:
      print 'calcBkgProfile'

    self.initMask()
    if conf.useRoot:
      h_bkgProfile= TH1F("h%s"%len(memDump),"Bkg profile",self.x1-self.x0,self.x0,self.x1)
      memDump.append(h_bkgProfile)
      h_west = TH2I("hist%s"%len(memDump),"Western",w[1]-w[0],w[0],w[1],w[3]-w[2],w[2],w[3])
      memDump.append(h_west)
    #if conf.useNumpy:
    #array inverse (y puis x)
    self.bkgProfileHist = [[0 for x in range(self.x0,self.x1) ] for y in range(self.y0,self.y1)]
    Lmin = 255
    LMax = 0
    #print self.x1-self.x0
    #print self.y1-self.y0
    #a=input()
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
            self.bkgProfileHist[y-self.y0][x-self.x0] = l
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
      memDump.append(TCanvas())
      h_bkgProfile.Draw("hist")
      memDump.append(TCanvas())
      h_west.GetZaxis().SetRangeUser(Lmin-1,LMax+1)
      h_west.Draw("colz")

  def genBkgProfileHist(self,name=""):

    if name == "":
      name = "background profile histo"
    if conf.useNumpy:
      fig = pylab.figure()
      pylab.matshow(self.bkgProfileHist, cmap=pylab.cm.gnuplot2)
      pylab.title(name)
      pylab.colorbar()
      pylab.savefig(name+".svg",format='svg')
      #pylab.show()
      pylab.close()


  def getBkgProfile (self):
    return self.bkgProfile

  def getMask(self):
    return self.mask


  def getLumiProfile(self,pix,bkgPro):
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
      self.lumiProfile.append(sumX)
      #h_xLumiProfile.Fill(x,sumX)
    #memDump.append(TCanvas())
    #h_xLumiProfile.Draw("hist")
    return(self.lumiProfile)


  def getPeaks(self):
    if conf.debug:
      print 'getPeaks'
    print self.x0
    self.getTrends()
    #print trends

    for t in self.trends:
      if t[1]-t[0]>=conf.nTrend:
        self.stableTrends.append(t)
    if conf.useRoot:
      self.h_lumiProfile = TH1F("h%s"%len(memDump),"xLumiProfile",len(self.lumiProfile),0,len(self.lumiProfile))
      memDump.append(self.h_lumiProfile)
    #if conf.useNumpy:
    self.lumiProfileHist = [0 for x in range(len(self.lumiProfile))]
    for x in range(len(self.lumiProfile)):
      l=self.lumiProfile[x]
      if conf.useRoot:
        self.h_lumiProfile.Fill(x,l)
      if conf.useNumpy:
        self.lumiProfileHist [x] = l
    if conf.useRoot:
      memDump.append(TCanvas())
      self.h_lumiProfile.Draw("hist")

    self.trendMerger()
    for t in self.mergedTrends:
      if conf.useRoot:
        h_line = TLine(t[0],self.lumiProfile[t[0]],t[1],self.lumiProfile[t[1]])
        if t[2]>0:
          h_line.SetLineColor(kGreen+1)
        else:
          h_line.SetLineColor(kRed+1)
        h_line.SetLineWidth(3)
        memDump.append(h_line)
        h_line.Draw()
      #if conf.useNumpy:



    for t in self.stableTrends:
      if conf.useRoot:
        h_line = TLine(t[0],self.lumiProfile[t[0]],t[1],self.lumiProfile[t[1]])
        if t[2]>0:
          h_line.SetLineColor(kGreen+1)
        else:
          h_line.SetLineColor(kRed+1)
        h_line.SetLineWidth(1)
        memDump.append(h_line)
        h_line.Draw()

    mins = []
    prevT = [0,0,-1]
    for t in self.mergedTrends:
      if prevT[2]<0 and t[2]>0:
        print "Found minimum at : %s %s"%(prevT[1],t[1])
        mins.append((prevT[1]+t[0])/2.)
      prevT=t
    if prevT[2]<0:
      print "Added boundary min at %s"%prevT[1]
      mins.append(prevT[1])
    if len(mins)<1:
      print "ERROR, no minimums found..."
      return([])
    if conf.useRoot:
      for m in mins:
        h_line = TLine(m,0,m,2000)
        h_line.SetLineWidth(1)
        h_line.SetLineStyle(3)
        memDump.append(h_line)
        h_line.Draw("hist")

    peaks = []
    peakStart = mins[0]
    peakStop = 0
    prevMin = mins[0]
    for m in mins[1:]:
      print peakStart
      print m
      maxi = max(self.lumiProfile[int(peakStart):int(m)])
      minLum = self.lumiProfile[int(m)]
      if minLum>0.5*maxi:
        print "Removing minimum %s (%s >50%% of max (%s))"%(m,minLum,maxi)
      else:
        peakStop = m
        peaks.append([peakStart,peakStop])
        peakStart= m

    #Merging peaks if too small
    avSize=0
    for p in peaks:
      pSize = p[1]-p[0]
      avSize +=pSize*1./len(peaks)


    for i in range(len(peaks)):
      p = peaks[i]
      pSize = p[1]-p[0]
      if pSize<conf.peakMergeThresh*avSize:
        print "Peak under threshold !"
        print "Attempt to merge..."
        if i == len(peaks)-1:
          print "Last peak ! Unable to merge !"
        else:
          nP = peaks[i+1]
          if pSize+(nP[1]-nP[0])>conf.peakAfterMergeThresh*avSize:
            print "Peak would be too big after merging, aborting !"
          else:
            print "Merging peaks..."
            peaks[i+1][0]=p[0]
      else:
        self.mergedPeaks.append(p)

    if len(self.mergedPeaks)<1:
      print "ERROR, no merged peaks..."
      return([])
    if conf.useRoot:
      for p in self.mergedPeaks:
        h_line = TLine(p[0],0,p[0],2000)
        h_line.SetLineWidth(3)
        memDump.append(h_line)
        h_line.Draw("hist")
      h_line = TLine(p[1],0,p[1],2000)
      h_line.SetLineWidth(3)
      memDump.append(h_line)
      h_line.Draw("hist")
    return(self.mergedPeaks)

  def genLumiProfileHist (self,name=""):

    if name == "":
      name = "Luminosity profile histo"
    if conf.useNumpy:
      fig = pylab.figure()
      pylab.bar([i for i in range(len(self.lumiProfileHist))],self.lumiProfileHist,width=1,color="#3C0D6E",edgecolor="#220740",linewidth=0.1)
      pylab.title(name)
      pylab.savefig(name+".svg",format='svg')
      #pylab.show()
      pylab.close()

  def getTrends(self):
    if conf.debug:
      print 'getTrends'
    t                 = [0,0,-1]
    prevLumi          = -1
    for x in range(len(self.lumiProfile)):
      l=self.lumiProfile[x]

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
    if conf.debug:
      print 'trendMerger'
    prevSign = 0
    prevTrend = [0,0,0]
    for t in self.trends:
      if not t[2] == prevTrend[2]:
        if not prevTrend[2] == 0:
          self.mergedTrends.append(prevTrend)
        prevTrend = [t[0],t[1],t[2]]
      else:
        prevTrend[1] = t[1]
    self.mergedTrends.append(prevTrend)
    print self.mergedTrends

  def setWesternImage(self,mainImg):
    self.westernImg = mainImg.crop((self.x0,self.y0, self.x1,self.y1))
    #self.westernImg  = self.westernImg.load()
    self.westernImgset = True


  def addBkgMask(self,outIm):
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

  def getWesternImg(self):
    return self.westernImg


  def computeIntensity(peaks):
    intensity = []
    for p in peaks:
      lum = 0
      for x in range(int(p[0])+1,int(p[1])):
        lum+=self.lumiProfile[x]
      lum+=self.lumiProfile[int(p[0])]*0.5
      lum+=self.lumiProfile[int(p[1])]*0.5
      intensity.append(lum)
    return(intensity)

