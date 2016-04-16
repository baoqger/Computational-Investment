import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *
import copy
import QSTK.qstkstudy.EventProfiler as ep
from collections import defaultdict
import math

def update(cash,num,price,stock_index):
    cash-=num*price
    share[stock_index]=share[stock_index]+num
    #print(cash)
    #print(share)
    return(cash,share[stock_index])

# the function of find events
def find_events(ls_symbols, d_data):
    orders=[]
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
    #fill the event matrix
    for each_stock in ls_symbols:
        for i in range(1,len(ldt_timestamps)-1):
            if std_output[each_stock].values[i]<=-2.0 and std_output[each_stock].values[i-1]>=-2.0 and std_output['SPY'].values[i]>=1.0:
                buy_date=(ldt_timestamps[i].year,ldt_timestamps[i].month,ldt_timestamps[i].day)
                if (i+5)<=(len(ldt_timestamps)-1):
                    sell_date=(ldt_timestamps[i+5].year,ldt_timestamps[i+5].month,ldt_timestamps[i+5].day)
                else:
                    sell_date=(ldt_timestamps[-1].year,ldt_timestamps[-1].month,ldt_timestamps[-1].day)
                orders.append((buy_date[0],buy_date[1],buy_date[2],each_stock,'Buy',100))
                orders.append((sell_date[0],sell_date[1],sell_date[2],each_stock,'Sell',100))           
    return(orders)



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
order_list = find_events(ls_symbols, d_data)

orders= {}
orders = defaultdict(list)  #dict's element is list
symbols_orders=[]       #the stock symbols traded in orders
for each in order_list:
    orders[(int(each[0]), int(each[1]), int(each[2]))].append((each[3], each[4], int(each[5])))
    symbols_orders.append(each[3])
date=orders.keys()
date.sort()
symbols_orders=list(set(symbols_orders))
#print(date)
#get the actual close price for the stocks inside orders
na_price = d_data['close'].values
# shares of each stock in hand
share=[]
for j in range(0,len(symbols_orders)):
    share.append(0)
#deal with the orders
cash=100000
value=[]
for i,t in enumerate(ldt_timestamps):
    port_value=0
    if (t.year,t.month,t.day) in date:
        current_order=orders[(t.year,t.month,t.day)]
        #print(current_order)
        for each_order in current_order:
            sym=each_order[0]
            sym_index=symbols_orders.index(sym)
            action=each_order[1]
            num=each_order[2]
            if action=='Sell':
                num=-num
            (cash,share[sym_index])=update(cash,num,na_price[i][sym_index],sym_index)
    for k in range(0,len(symbols_orders)):
        port_value+=share[k]*na_price[i][k]
    value.append(cash+port_value)
    print(t.year,t.month,t.day,cash,port_value)
#print(value)

k=2
daire_port=[0]
while k<len(value)-2:
    daire_port.append(value[k]/value[k-1]-1)
    k=k+1
daire_port=np.array(daire_port)
average=np.average(daire_port)
stdev=np.std(daire_port)
sharpe=math.sqrt(252)*average/stdev
print("sharpe ratio")
print(sharpe)
total_re=value[-1]/value[0]
print("total_re")
print(total_re)
