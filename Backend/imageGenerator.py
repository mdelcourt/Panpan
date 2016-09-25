
def getOutIm(outIm, w, mask):
  """"""
  (x0,x1,y0,y1) = w


  for x in range(1,len (mask)-1):
    for y in range(1,len(mask[x])-1):
      if (mask[x][y] != mask[x][y+1]
      or mask[x][y] != mask[x+1][y]
      or mask[x][y] != mask[x+1][y+1]):
        outIm.putpixel((x+x0,y+y0),(0,0,255,255))
  return outIm
