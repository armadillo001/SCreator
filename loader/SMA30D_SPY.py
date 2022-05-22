from datetime import date,timedelta
from fredapi import Fred
import talib
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")

def fun_load_data(start_date):
    import yfinance as yf
    pd_data = yf.download('SPY', start=start_date, end=(date.today() + timedelta(days=1)).strftime("%Y-%m-%d"))
    pd_data_ETH = pd_data.dropna()
    return pd_data_ETH

def fun_compute_data(pd_data):
    pd_data = pd_data['Close']
    pd_data = (pd_data - talib.SMA(pd_data, 30)) / talib.SMA(pd_data, 30)
    pd_data = pd_data.dropna()
    my_series = pd_data.squeeze()
    return my_series