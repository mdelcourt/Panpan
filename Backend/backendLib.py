import sys
import backendConfig as conf
#import numpy optimisation


if conf.useRoot:
    from ROOT import *
    print "ROOT imported"
else:
    print "ROOT not imported"


memDump=[]

def getLumi(pix):
  #l = 3*((255-pix[0])*(255-pix[1])*(255-pix[2]))**1/3.
  l = 255.-((pix[0]+pix[1]+pix[2])/3.)
  return l

def isSquare(pix):
  if pix[0] == conf.squareCol[0] and pix[1] == conf.squareCol[1] and pix[2] == conf.squareCol[2]:
    return 1
  else:
    return 0

def getWesterns(pix,sx,sy):

  lines = []

  inLine = False
  (l0,l1,ly)=(0,0,0)
  for y in range(sy):
    for x in range(sx):
      if inLine:
        if not isSquare(pix[x,y]):
          l1=x-1
          inLine=False
          if (l1-l0)>conf.squareMinSize-1:
            lines.append((l0,l1,ly))
      else:
        if isSquare(pix[x,y]):
          inLine=True
          l0=x
          ly=y

  #print lines
  westerns=[]
  while len(lines)>0:
    candi = lines[0]
    for l in lines[1:]:
      if l[0]==candi[0] and l[1] == candi[1]:
        westerns.append((l[0]+1,l[1]-1,candi[2]+1,l[2]-1))
        lines.remove(l)
        break
    lines.remove(candi)
  #print westerns

  return(westerns)

def getBkg(pix,w):
  (x0,x1,y0,y1) = w

  lumi = [0 for i in range(0,255)]
  if conf.useRoot:
    h = TH1I("h%s"%len(memDump),"h",256,0,256)
    memDump.append(h)

  for x in range(x0,x1):
    for y in range(y0,y1):
      lumi[int(getLumi(pix[x,y]))]+=1
      if conf.useRoot:
        h.Fill(getLumi(pix[x,y]))
  if conf.useRoot:
    memDump.append(TCanvas())
    h.Draw()

  mLumi = max(lumi)
  inMaximum=False
  bkg0 = 0
  bkg1 = 0
  bkg  = 0
  for i in range(len(lumi)):
    l = lumi[i]
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




def printWestern(pix,w,bkg=0):
  h_west = TH2I("hist%s"%len(memDump),"Western",w[1]-w[0],w[0],w[1],w[3]-w[2],w[2],w[3])
  for x in range(w[0],w[1]):
    for y in range(w[2],w[3]):
      l = getLumi(pix[x,y])-bkg
      if l<0:
        l=0
      h_west.Fill(x,y,l)
  c = TCanvas()
  h_west.Draw("colz")
  memDump.append(h_west)
  memDump.append(c)


def getBkgProfile(pix,w,bkg=0,sBkg=0):
  (x0,x1,y0,y1) = w
  bkgProfile=[]
  mask = [[0 for i in range(y0,y1)] for j in range(x0,x1)]
  if conf.useRoot:
    h_bkgProfile= TH1F("h%s"%len(memDump),"Bkg profile",x1-x0,x0,x1)
    memDump.append(h_bkgProfile)
    h_west = TH2I("hist%s"%len(memDump),"Western",w[1]-w[0],w[0],w[1],w[3]-w[2],w[2],w[3])
    memDump.append(h_west)
  Lmin = 255
  LMax = 0
  for x in range(x0,x1):
    nPixBkg= 0
    bkgTot = 0
    for y in range(y0,y1):
      l = getLumi(pix[x,y])
      if l<(bkg+conf.nSigmaBkg*sBkg):
        if l>0 and l<Lmin:
          Lmin=l
        if l>LMax:
          LMax=l
        if conf.useRoot:
          h_west.Fill(x,y,l)
        bkgTot+=l
        nPixBkg+=1
      else:
	mask[x-x0][y-y0]=1
    if nPixBkg==0:
      nPixBkg=1
    bkgProfile.append(bkgTot*1./nPixBkg)
    if conf.useRoot:
      h_bkgProfile.Fill(x,bkgTot*1./nPixBkg)
  if conf.useRoot:
    memDump.append(TCanvas())
    h_bkgProfile.Draw()
    memDump.append(TCanvas())
    h_west.GetZaxis().SetRangeUser(Lmin-1,LMax+1)
    h_west.Draw("colz")


  return(bkgProfile,mask)

def getLumiProfile(pix,w,bkgPro):
  (x0,x1,y0,y1) = w
  profile = []
  i = 0
  #h_xLumiProfile= TH1F("h%s"%len(memDump),"xLumiProfile",x1-x0,x0,x1)
  #memDump.append(h_xLumiProfile)
  for x in range(x0,x1):
    sumX = 0
    for y in range(y0,y1):
      sumX += getLumi(pix[x,y])-bkgPro[i]
    i+=1
    profile.append(sumX)
    #h_xLumiProfile.Fill(x,sumX)
  #memDump.append(TCanvas())
  #h_xLumiProfile.Draw()
  return(profile)




def getTrends(lumi):

  trends         = []
  t                 = [0,0,-1]
  prevLumi          = 0
  for x in range(len(lumi)):
    l=lumi[x]

    if l > prevLumi + 1e-5:
      if t[2]<0: #Previous trend was decreasing
        t[1] = x-1
        trends.append(t)
        t = [x,0,1]
    if l < prevLumi - 1e-5:
      if t[2]>0: #Previous trend was decreasing
        t[1] = x-1
        trends.append(t)
        t = [x,0,-1]
    if l<1e-5:
      t[1] = x-1
      trends.append(t)
      t = [x,0,-1]
    prevLumi=l
  return (trends)

def trendMerger(trends):

  tMerged = []
  prevSign = 0
  prevTrend = [0,0,0]
  for t in trends:
    if not t[2] == prevTrend[2]:
      if not prevTrend[2] == 0:
        tMerged.append(prevTrend)
      prevTrend = [t[0],t[1],t[2]]
    else:
      prevTrend[1] = t[1]
  tMerged.append(prevTrend)
  print tMerged
  return(tMerged)


def getPeaks(lumi,w):
  print w[0]
  (x0,x1,y0,y1) = w

  trends = getTrends(lumi)
  #print trends
  stableTrends = []
  for t in trends:
    if t[1]-t[0]>=conf.nTrend:
      stableTrends.append(t)
  if conf.useRoot:
    h_lumiProfile = TH1F("h%s"%len(memDump),"xLumiProfile",len(lumi),0,len(lumi))
    memDump.append(h_lumiProfile)
  for x in range(len(lumi)):
    l=lumi[x]
    if conf.useRoot:
      h_lumiProfile.Fill(x,l)
  if conf.useRoot:
    memDump.append(TCanvas())
    h_lumiProfile.Draw()

  mergedTrends = trendMerger(stableTrends)
  for t in mergedTrends:
    if conf.useRoot:
      h_line = TLine(t[0],lumi[t[0]],t[1],lumi[t[1]])
      if t[2]>0:
        h_line.SetLineColor(kGreen+1)
      else:
        h_line.SetLineColor(kRed+1)
      h_line.SetLineWidth(3)
      memDump.append(h_line)
      h_line.Draw()

  for t in stableTrends:
    if conf.useRoot:
      h_line = TLine(t[0],lumi[t[0]],t[1],lumi[t[1]])
      if t[2]>0:
        h_line.SetLineColor(kGreen+1)
      else:
        h_line.SetLineColor(kRed+1)
      h_line.SetLineWidth(1)
      memDump.append(h_line)
      h_line.Draw()

  mins = []
  prevT = mergedTrends[0]
  for t in mergedTrends[1:]:
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
      h_line.Draw()

  peaks = []
  peakStart = mins[0]
  peakStop = 0
  prevMin = mins[0]
  for m in mins[1:]:
    print peakStart
    print m
    maxi = max(lumi[int(peakStart):int(m)])
    minLum = lumi[int(m)]
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

  mergedPeaks = []

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
      mergedPeaks.append(p)

  if len(mergedPeaks)<1:
    print "ERROR, no merged peaks..."
    return([])
  if conf.useRoot:
    for p in mergedPeaks:
      h_line = TLine(p[0],0,p[0],2000)
      h_line.SetLineWidth(3)
      memDump.append(h_line)
      h_line.Draw()
    h_line = TLine(p[1],0,p[1],2000)
    h_line.SetLineWidth(3)
    memDump.append(h_line)
    h_line.Draw()


  return([])


def getOutIm(outIm, w, mask):
   (x0,x1,y0,y1) = w

   for y in range(1,len (mask)-1):
      for x in range(1,len(mask[y])-1):
         if (mask[y][x] != mask[y][x+1]
         or mask[y][x] != mask[y+1][x]
         or mask[y][x] != mask[y+1][x+1]):
            outIm.putpixel((x+x0,y+y0),(0,0,255,255))
   return outIm

def getOutIm2(outIm, w, mask):
   """ for testing if comprehension makes it faster. BTW It doesn't."""
   (x0,x1,y0,y1) = w

   listPixels = [(x+x0,y+y0) for x in range(1,len(mask[0])-1) for y in range(1,len (mask)-1) if (mask[y][x] != mask[y][x+1]
         or mask[y][x] != mask[y+1][x]
         or mask[y][x] != mask[y+1][x+1])]

   for (x,y) in listPixels:
      outIm.putpixel((x,y),(0,0,255,255))
   #print(len(listPixels))
   return outIm

