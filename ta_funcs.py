import talib as ta
import pandas as pd

class IND_TA(object):

    def __init__(self,data, symbol):
        self.df = data
        self.symbol = symbol

    def sma(self, periodsma):
        #periodsma = kwargs.get('periodsma')
        return  pd.DataFrame(ta.SMA(self.df.Close, timeperiod=periodsma), columns = ["sma"])

    def ema(self, periodema):
        return  pd.DataFrame(ta.EMA(self.df.Close, timeperiod=periodema), columns = ["ema"])
    
    def adx(self, periodadx):
        return  pd.DataFrame(ta.ADX(self.df.High, self.df.Low, self.df.Close, timeperiod=periodadx), columns = ["adx"])

    def sar(self, acc = 0.02, maximum = 0.2):
        return  pd.DataFrame(ta.SAR(self.df.High, self.df.Low, acceleration=acc, maximum=maximum), columns = ["sar"])
        # return ta.SAREXT(self.df.High, self.df.Low, startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0)
    
    def rsi(self, periodsar):
        return  pd.DataFrame(ta.RSI(self.df.Close, timeperiod=periodsar), columns = ["rsi"]) 
    
    def cci (self,periodcci):
        return  pd.DataFrame(ta.CCI(self.df.High, self.df.Low, self.df.Close, timeperiod=periodcci), columns = ["cci"])

    def stoch(self, fastk_period=5, slowk_period=3, slowk_matype=0,slowd_period=3, slowd_matype=0):
        slowk, slowd = ta.STOCH(self.df.High, self.df.Low, self.df.Close, \
            fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=slowk_matype, \
            slowd_period=slowd_period, slowd_matype=slowd_matype)
        stoch = pd.concat([slowk,slowd], axis=1)
        stoch.columns = ['stoch_slowk', 'stoch_slowd']
        return stoch

    def macd(self,fastperiod=12, slowperiod=26, signalperiod=9):
        macd, macdsignal, macdhist = ta.MACD(self.df.Close, fastperiod=fastperiod, \
            slowperiod=slowperiod, signalperiod=signalperiod)
        macd_aux = pd.concat([macd.T, macdsignal.T, macdhist.T], axis=1)
        macd_aux.columns = ['macd', 'macdsignal','macdhist']
        return macd_aux
        
    def bbands(self,periodbbands, matype=0):
        upper, middle, lower = ta.BBANDS(self.df.Close, timeperiod=periodbbands, matype=matype)
        bbands = pd.concat([upper,middle,lower], axis=1)
        bbands.columns = ['bbands_upper', 'bbands_middle','bbands_lower']
        return bbands

    def obv(self):
        return  pd.DataFrame(ta.OBV(self.df.Close, self.df.Volume), columns = ['obv'])
