#class processConfig:


class westernConfig:


  def __init__(self,WIndex=""):


    self.bkgEstim  = "Average" #Can be Average or Peak
    self.nSigmaBkg = 3  #Number of sigma to cut bkg

    self.lumiThresh = 50
    self.nTrend = 3 #Number of consecutive pixels needed for trend


    self.peakMergeThresh  = 0.75    #max prop of average peak size for peak merging
    self.peakAfterMergeThresh  = 1.50   #max prop size after merging

    self.useRoot = False #use ROOT library or not. If not, no ROOT images generated
    self.debug = True
    self.useNumpy = True


class backendConfig:

    def __init__(self):
      self.squareCol = [128,255,128]
      self.squareMinSize = 10
