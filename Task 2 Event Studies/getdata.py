import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import copy
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import QSTK.qstkstudy.EventProfiler as ep

def find_events(ls_symbols, d_data):
    df_close = d_data['actual_close']
    ldt_timestamps = df_close.index
    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    
    num_event=0
    for each_stock in ls_symbols:
        for i in range(1,len(ldt_timestamps)-1):
            if df_close[each_stock].ix[ldt_timestamps[i]]<8.0 and df_close[each_stock].ix[ldt_timestamps[i-1]]>=8.0:
                df_events[each_stock].ix[ldt_timestamps[i]] = 1
                num_event=num_event+1
    
    print(num_event)
    return(df_events)
                

dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

dataobj=da.DataAccess('Yahoo')
symbols=dataobj.get_symbols_from_list("sp5002012")
symbols.append('SPY')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
df_events = find_events(symbols, d_data)
print "Creating Study"
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy128.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')   



