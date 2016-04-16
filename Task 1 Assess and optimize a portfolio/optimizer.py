import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np

def simulate(start,end,symbols,allocations):
    dt_start = dt.datetime(start[0],start[1],start[2])
    dt_end = dt.datetime(end[0],end[1],end[2])
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    i=0
    while i<4:
        na_normalized_price[:,i]=na_normalized_price[:,i]*allocations[i]
        i=i+1
    j=0
    cumu_port=[]
    while j<len(ldt_timestamps):
        sum=0
        for each in na_normalized_price[j,:]:
            sum=sum + each
        cumu_port.append(sum)
        j=j+1
    cumu_ret=cumu_port[-1]/cumu_port[0]
    k=1
    daire_port=[0]
    while k<len(cumu_port):
        daire_port.append(cumu_port[k]/cumu_port[k-1]-1)
        k=k+1
    daire_port=np.array(daire_port)
    average=np.average(daire_port)
    stdev=np.std(daire_port)
    return(math.sqrt(252)*average/stdev,average,stdev,cumu_ret)


def optimizer(start,end,symbols):
    best=-100
    sum=0
    i=j=k=0
    while i<=1:
        j=0
        while j<=1:
            k=0
            while k<=1:
                m=1-i-j-k
                if m >= 0:
                    #print("current allocations")
                    allocations=[float('%0.2f'%i),float('%0.2f'%j),float('%0.2f'%k),float('%0.2f'%m)]
                    #print(allocations)
                    current_sharpe,current_average,current_stdev,current_cumu=simulate(start,end,symbols,allocations)
                    #print("current sharpe")
                    #print(current_sharpe)
                    if current_sharpe>best:
                        best_allo=allocations
                        best=current_sharpe
                        best_average=current_average
                        best_stdev=current_stdev
                        best_cumu=current_cumu
                    #print("best allocation")
                    #print(best_allo)
                    #print("best sharpe")
                    #print(best)
                k=k+0.1
            j=j+0.1
        i=i+0.1
    print"Optimal Allocations:",best_allo
    print"Highest Sharpe Ratio:",best
    print"Volatility(stdev of daily return):",best_stdev
    print"Average of Daily Return:",best_average
    print "Cumulative Return:",best_cumu
    

    
    
            
    
    
    

    
    

    
    
