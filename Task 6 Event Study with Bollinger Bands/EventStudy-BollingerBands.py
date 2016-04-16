import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *
import copy
import QSTK.qstkstudy.EventProfiler as ep

# the function of find events
def find_events(ls_symbols, d_data):
    adjcloses=d_data['close']
    adjcloses = adjcloses.fillna(1.0)
    adjcloses = adjcloses.fillna(method='backfill')
    means = pandas.rolling_mean(adjcloses,20,min_periods=20)
    stdev = pandas.rolling_std(adjcloses,20,min_periods=20)
    upper_band=means+stdev
    lower_band=means-stdev
    std_output=(adjcloses-means)/stdev
    std_output = std_output.fillna(method='backfill')
    #prepare the date data
    ldt_timestamps = adjcloses.index
    print "Finding Events"
    # Creating an empty dataframe
    df_events = copy.deepcopy(std_output)
    df_events = df_events * np.NAN
    #fill the event matrix
    for each_stock in ls_symbols:
        for i in range(1,len(ldt_timestamps)-1):
            if std_output[each_stock].values[i]<=-2.0 and std_output[each_stock].values[i-1]>=-2.0 and std_output['SPY'].values[i]>=1.4:
                df_events[each_stock].ix[ldt_timestamps[i]] = 1
    return(df_events)



# prepare the time data
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
timeofday=dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(startday,endday,timeofday)
dataobj=da.DataAccess('Yahoo')
ls_symbols=dataobj.get_symbols_from_list("sp5002012")
ls_symbols.append('SPY')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
    d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)  
#call the find event function
df_events = find_events(ls_symbols, d_data)
print("Creating Event")
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='EventStudyOnBollinger.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

