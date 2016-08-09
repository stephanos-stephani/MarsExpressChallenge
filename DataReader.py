import pandas as pd
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import numpy as np
import xgboost as xgb
import cPickle as pickle
from sklearn import cross_validation
from scipy import stats
from my_features import *

class RawData:
    def __init__(self):
        DIR = '/home/users/DE/sstephani/shared/ms/clean/mars-express-power-3years/'
        self.context = ['dmop', 'evtf', 'ftl', 'ltdata', 'saaf']
        self.files = dict(zip(['train_set','test_set'],
                 [[join('%s/%s/'%(DIR,x), f) \
                   for f in listdir('%s/%s/'%(DIR,x)) \
                   if isfile(join('%s/%s/'%(DIR,x), f))] \
                  for x in ['train_set','test_set']]))
        self.years = sorted(list(set([x.split("--")[1] for x in self.files['train_set'] if 'context'  in x])))
    
    def get_data(self,year=None):
        if year is None:
            return self.file_dict(self.files['test_set'])
        else:
            rets = []
            for i in self.files['train_set']:
                if self.years[year-1] in i:
                    rets.append(i)
            return self.file_dict(rets)
        
    def file_dict(self, fList):
        d = {}
        for ctype in self.context:
            for i in fList:
                if ctype in i:
                    d[ctype] = i
                elif 'context' not in i:
                    d['power'] = i

        return d

class PdData(RawData):
    def __init__(self):
        RawData.__init__(self)
    
    def get_df_dict(self, year):
        d = self.get_data(year)
        for k in d.keys():
            d[k] = pd.read_csv(d[k])
            try:
                d[k].index = d[k]['ut_ms']
                del d[k]['ut_ms']
            except KeyError:
                continue
        return d
    
    def make_hourly(self,df):
        df['ut_ms'] = df.index
        interesting = dependent + [x for x in df.columns if "NPWD" in x ] + ["ut_ms"]
        for i in interesting:
            if i not in df.columns:
                df[i] = 0
        df=df[interesting]
        dt = pd.to_datetime(df['ut_ms'], unit='ms')
        df.index=dt
        start = dt.iloc[0].date()
        end = dt.iloc[-1].date() + pd.Timedelta('1 days')
        index = pd.date_range(start=start,end=end, freq='H')[:-1]
        pairs = []
        L = index
        pairs = [(L[x], L[x+1]-pd.Timedelta('1 millisecond')) for x in range(len(L)-1)]
        pairs.append((L[-1], L[-1] + pd.Timedelta('1 hour')))
        h = [df[pairs[x][0]:pairs[x][1]].mean() for x in range(len(pairs))]
        
        hourly=pd.concat(h,axis=1).transpose()
        hourly.index = L[:len(pairs)]
        hourly['UMBRA_season']=pd.ewma(hourly['UMBRA_time'],240) > 10000
        hourly['UMBRA_time1']=hourly['UMBRA_time'].shift(1).fillna(method='bfill')
        hourly['UMBRA_time2']=hourly['UMBRA_time'].shift(2).fillna(method='bfill')
        hourly['UMBRA_time3']=hourly['UMBRA_time'].shift(3).fillna(method='bfill')
        hourly['PENUMBRA_time1']=hourly['PENUMBRA_time'].shift(1).fillna(method='bfill')
        hourly['PENUMBRA_time2']=hourly['PENUMBRA_time'].shift(2).fillna(method='bfill')
        hourly['PENUMBRA_time3']=hourly['PENUMBRA_time'].shift(3).fillna(method='bfill')
        hourly['conjuction'] = (pd.rolling_std(hourly['sa'],window=50, center=False) < 0.5) | (hourly['sunmarsearthangle_deg'].abs() < 3)
        hourly['conjuction'] = hourly['conjuction'].fillna(method='bfill')
        
        hourly['thisisit']=(((hourly['sunmarsearthangle_deg']-pd.rolling_min(hourly['sunmarsearthangle_deg'],window=300,center=True)).abs() < 1e-5) & (hourly['sunmarsearthangle_deg'] < hourly['sunmarsearthangle_deg'].shift(-1)-1e-6))

       
        hourly['mult'] = 1
        hourly.loc[hourly['thisisit'], 'mult']=-1
        
        hourly['sunmarsearthangle_deg2'] = hourly['mult'].cumprod() * hourly['sunmarsearthangle_deg']
        del hourly['height_change']

        height_change = pd.read_pickle('height_change_hourly.pkl')
        hourly = pd.concat([hourly, height_change], axis=1)
        hourly['height_change'] = hourly['height_change'].fillna(0)
        del hourly['mult']
        del hourly['thisisit']
        del hourly['ut_ms']
        return hourly
    
   
    def massaged_data(self, year, no_power_sub = False, hourly=False):
        d = self.get_df_dict(year)
        master = copy.deepcopy(d['power'])
        master = self.add_lt_data(master, d,no_power_sub)
        master = self.add_saaf_data(master, d,no_power_sub)        
        master = self.add_evtf_data(master, d,no_power_sub)
        master = self.add_dmop_data(master, d,no_power_sub)
        master = self.add_ftl_data(master, d,no_power_sub)

        if hourly:
            master=self.make_hourly(master)
        return master

    def add_lt_data(self, master, d, no_power_sub = False):
        # ltdata
        master=pd.concat([master,d['ltdata'][['solarconstantmars','sunmarsearthangle_deg',
                                             'eclipseduration_min', 'occultationduration_min']]], axis=1)
        master['solarconstantmars'] = master['solarconstantmars'].fillna(method='ffill')
        master['sunmarsearthangle_deg'] = master['sunmarsearthangle_deg'].fillna(method='ffill')
        master['eclipseduration_min'] = master['eclipseduration_min'].fillna(method='ffill')
        master['occultationduration_min'] = master['occultationduration_min'].fillna(method='ffill')
        if not no_power_sub: 
            master=master.loc[d['power'].index]
        return master
    
    def add_saaf_data(self, master, d, no_power_sub = False):
        master=pd.concat([master, d['saaf']], axis=1)
        for i in ['sa','sx','sy','sz']:
            master[i]=master[i].fillna(method='ffill')
        if not no_power_sub: 
            master=master.loc[d['power'].index]

        return master
    
    def add_evtf_data(self, master, d, no_power_sub = False):
        d['evtf']['des_short'] = \
            d['evtf']['description'].apply(lambda x: \
                ("_").join(x.split("_")[0:2]) if "CENTRE" in x else x)
        
        d['evtf']['ut_ms'] = d['evtf'].index
        d['evtf'].loc[d['evtf']['ut_ms'].diff() < 1, 'ut_ms'] = d['evtf'].loc[d['evtf']['ut_ms'].diff() < 1, 'ut_ms'] + 1
        d['evtf'].index=d['evtf']['ut_ms']
        del d['evtf']['ut_ms']
         
       
        master=pd.concat([master,d['evtf']], axis=1)
        master['ut'] = master.index
        master['time_to_pericenter_w'] = master['ut'].diff().cumsum()
        master['adj'] = 0
        master.loc[master['des_short'] =='PERICENTRE_PASSAGE','adj'] \
            = master.loc[master['des_short'] =='PERICENTRE_PASSAGE','time_to_pericenter_w']
        master['adj2']=master['adj'].replace(to_replace=0, method='ffill')
        master['ttp'] = (master['time_to_pericenter_w'] - master['adj2'])
        del master['time_to_pericenter_w']
        del master['adj']
        del master['adj2']
        
        del master['description'] # whaaaaat
        
        um = d['evtf'].loc[d['evtf']['description'].apply(lambda x: 'UMBRA' in x)]
        um['ut_ms'] = um.index
        um.loc[um['ut_ms'].diff() < 1, 'ut_ms'] = um.loc[um['ut_ms'].diff() < 1, 'ut_ms'] + 1
        um.index = um['ut_ms']
        del um['ut_ms']
        master=pd.concat([master, um], axis=1)
        master['description'] = master['description'].fillna(method='ffill')
      
        master['UMBRA']=master['description'].apply(lambda x: '_UMBRA_START' in str(x))
        master['PENUMBRA']=master['description'].apply(lambda x: '_PENUMBRA_START' in str(x) \
                                               or '_UMBRA_START' in str(x)\
                                               or '_UMBRA_END' in str(x))
        
        for att in ['UMBRA', 'PENUMBRA']:
            master['cs'] = np.nan
            master.loc[master[att],'cs'] = master['ut'].diff().loc[master[att]].cumsum()
            master['cs'] = master['cs'].fillna(method='ffill')
            master['baseline'] = master['cs']
            master.loc[master[att],'baseline']=np.nan
            master['baseline']=master['baseline'].fillna(method='ffill')
            master[att+'_time'] = master['cs']- master['baseline']
            master['cs']
            master['baseline']
            del master['cs']
            del master['baseline']
            master[att+'_time']=master[att+'_time'].fillna(value=0)
        
        if not no_power_sub: 
            master=master.loc[d['power'].index]

        
        
        
        return master
    
    def add_ftl_data(self, master, d, no_power_sub = False):
        # This is really shaky
        cols = ['ACROSS_TRACK',
                 'D1PVMC',
                 'D2PLND',
                 'D3POCM',
                 'D4PNPO',
                 'D7PLTS',
                 'D8PLTP',
                 'D9PSPO',
                 'EARTH',
                 'INERTIAL',
                 'MAINTENANCE',
                 'NADIR',
                 'NADIR_LANDER',
                 'SLEW',
                 'SPECULAR',
                 'WARMUP',
                 'flagcomms']
        x = d['ftl']
        x.index=x['utb_ms']
        x['time']=x['ute_ms']-x['utb_ms']
        dummies=pd.get_dummies(x['type'])
        dummies['flagcomms'] = x['flagcomms'].astype('float')
        
        dummies = dummies.multiply(x['time'], axis="index")
        for i in cols:
            if i not in dummies.columns:
                dummies[i]=0
        
        master = pd.concat([master, dummies[cols]], axis=1)
        master[cols] = master[cols].fillna(method='ffill')
        if not no_power_sub: 
            master=master.loc[d['power'].index]

        master=master.fillna(method='bfill')
        return master
    
    def add_dmop_data(self, master, d, no_power_sub = False):
        # This is really shaky as well
        dummies = pd.ewma(pd.get_dummies(d['dmop']['subsystem'].apply(lambda x: x[:4])), span=100)
        master = pd.concat([master, dummies], axis=1)
        master[dummies.columns] = master[dummies.columns].fillna(method='ffill')
        pairs = [['AAAAF40B0','AAAAF40C0'],
        ['AAAAF40E0','AAAAF40F0'],
        ['AAAAF40D0','AAAAF40P0'],
        ['ASSSF01P0', 'ASSSF06P0'],
        ['AACFM01A','AACFM02A'],
        ['AACF325C','AACF325D'],
        ['AMMMF52D3','AMMMF52D4'],
        ['AMMMF18A0','AMMMF40A0'],
        ['AHHHF01P1','AHHHF50A2'],
        ['ATTTF030A', 'ATTTF030B'],
        ['ATTTF321P','ATTTF321R'],
        ['AACFM01A','AACFM02A'],
        ['AMMMF18A0','AMMMF19A0'],
        ['PENS','PENE'],
        ['MOCS','MOCE'],
         ['PDNS','PDNE'],
         ['PPNS','PPNE'],
         ['UPBS','UPBE']]
        tmp=[d['dmop'][d['dmop']['subsystem'].apply(lambda x: y[0] in x.split(".")[0] or y[1] in x.split(".")[0] )]['subsystem'].apply(lambda x: 1 if y[0] in x else -1) for y in pairs]
        #tmp=[d['dmop'][d['dmop']['subsystem'].apply(lambda x: y[0] in x or y[1] in x )]['subsystem'].apply(lambda x: 1 if y[0] in x else -1) for y in pairs]
        x=pd.concat(tmp, axis=1).fillna(method='ffill').fillna(0)
        x.columns=['pair%d'%z for z in range(len(x.columns))]

        p = []
        for idx,i in enumerate(pairs):
            p.append(d['dmop']['subsystem'].apply(lambda x: 1 if i[1] in x.split(".")[0] else (0 if i[0] in x.split(".")[0] else np.nan)))

        y = pd.concat(p, axis=1).fillna(method='ffill').fillna(0)
        y.columns=['pair_c_%d'%z for z in range(len(x.columns))]

        if not no_power_sub: 
            master=master.loc[d['power'].index]

        master=master.fillna(method='bfill')
        master=pd.concat([master, x,y], axis=1).fillna(method='ffill').fillna(0)
        return master
    
