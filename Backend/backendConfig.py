class processConfig(object):
  """ Configs for the main process
  """
  def __init__(self):
    self.squareCol = [128,255,128]
    self.squareMinSize = 10
    self.useRoot = False #use ROOT library or not. If not, no ROOT images generated
    self.debug = True
    self.useNumpy = True


class westernConfig(processConfig):
  """ Configs of the western class
  """
  def __init__(self,westernPath,WIndex=""):

    #super(processConfig, self).__init__()
    processConfig.__init__(self)

    self.bkgEstim  = "Average" #Can be Average or Peak
    self.nSigmaBkg = 3  #Number of sigma to cut bkg

    self.lumiThresh = 50
    self.nTrend = 3 #Number of consecutive pixels needed for trend


    self.peakMergeThresh  = 0.75    #max prop of average peak size for peak merging
    self.peakAfterMergeThresh  = 1.50   #max prop size after merging


  def createConfig():
    pass
