import sys
import backendConfig
from Backend.western import *
#import numpy optimisation

conf = backendConfig
if conf.useRoot:
    from ROOT import *
    print "ROOT imported"
else:
    print "ROOT not imported"


memDump=[]


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

        print (l[0]+1,l[1]-1,candi[2]+1,l[2]-1)
        w = western(l[0]+1,l[1]-1,candi[2]+1,l[2]-1)
        westerns.append(w)
        lines.remove(l)
        break
    lines.remove(candi)
  #print westerns

  return(westerns)



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
