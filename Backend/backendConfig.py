import json

class processConfig(object):
  """ Configs for the main process
  """
  def __init__(self,confPath,confName):
    if confPath[-1] != "/":
      confPath = confPath + "/"
    self.confPath = confPath
    self.confName = confName
    self.squareCol = list()
    self.squareMinSize = int()
    self.useRoot = bool()
    self.debug = bool()
    self.useNumpy = bool()
    self.FontPath = str()
    self.FontSize = int()

    self.loadPConf()

  def savePConf(self):
    """ Save configs of this western config class instance to Json file.
    """
    with open(self.confPath+self.confName,"w") as fout:
      fout.write(json.dumps(self.__dict__))


  def loadPConf(self):
    """ load config for this process from json file.
    """


    with open(self.confPath+self.confName,"r") as f_in:
      dct = json.loads(f_in.readlines()[0])

      self.squareCol = dct["squareCol"]
      self.squareMinSize = dct["squareMinSize"]
      self.useRoot = dct["useRoot"]
      self.debug = dct["debug"]
      self.useNumpy = dct["useNumpy"]
      self.FontPath = dct["FontPath"]
      self.FontSize = dct["FontSize"]

    if self.debug:
      print "loaded Pconf from: "
      print self.confPath+self.confName


class westernConfig(object):
  """ Configs of the western class
  """

  def __init__(self,westConfPath,westConfName,PConf):
    #print("western is being initialised")
    if westConfPath[-1] != "/":
      westConfPath = westConfPath+"/"
    self.westConfPath = westConfPath
    self.westConfName = westConfName
    self.bkgEstim  = str() #Can be Average or Peak
    self.nSigmaBkg = int()  #Number of sigma to cut bkg
    self.lumiThresh = int()
    self.nTrend = int() #Number of consecutive pixels needed for trend
    self.peakMergeThresh  = int()    #max prop of average peak size for peak merging
    self.peakAfterMergeThresh  = int()   #max prop size after merging
    self.numPeaks = int()   # expected number of peaks to find (can be -1 for auto)

    self.__ownDict__ = dict(self.__dict__) # dictionary of this class level instance.

    self.loadWConf()

  def saveConfig(self, westConfPath):
    """ Save configs of this western config class instance to Json file.
    """
    with open(westConfPath,"w") as fout:
      fout.write(json.dumps(self.__ownDict__))


  def loadWConf(self):
    """ load config for this western instance from json file.
    """
    #confName = "testconf.json"
    with open(self.westConfPath+self.westConfName,"r") as f_in:
      dct = json.loads(f_in.readlines()[0])

      self.bkgEstim  = dct["bkgEstim"]
      self.nSigmaBkg = dct["nSigmaBkg"]
      self.lumiThresh = dct["lumiThresh"]
      self.nTrend = dct["nTrend"]
      self.peakMergeThresh  = dct["peakMergeThresh"]
      self.peakAfterMergeThresh  = dct["peakAfterMergeThresh"]
      self.numPeaks = dct["numPeaks"]
