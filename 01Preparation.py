import os, sys
import time
import datetime
import pandas as pd
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt 
import random


ROOTDIR = os.path.abspath(os.path.realpath('./')) + '/Py'

sys.path.append(os.path.join(ROOTDIR, ''))

from Stamp_transition import Stamp_transition

if __name__ == '__main__':

	'''Path'''

	Load_path='./Data/Processed/'

	speed=3.0

	End_step=144

	Network_Distance=np.load(os.path.join(Load_path,'Network_Distance.npy'))

	Location_list=np.load(os.path.join(Load_path,'Location_list.npy'))

	Location_range=pd.DataFrame(Location_list,columns=['LocationID'])

	Location_ID_dic=np.load(os.path.join(Load_path,'Location_ID_dic.npy')).item()

	Location_ID_dic_reverse=np.load(os.path.join(Load_path,'Location_ID_dic_reverse.npy')).item()

	'''State'''

	State=np.load(os.path.join(Load_path,'State.npy'))

	Action=np.load(os.path.join(Load_path,'Action.npy')).item()


	# ''''Order'''

	stamp_transition=Stamp_transition()

	Request_data=pd.read_csv('./Data/Source/yellow_tripdata_2019-11.csv')

	Request_data=Request_data[['PULocationID','DOLocationID','tpep_pickup_datetime','tpep_dropoff_datetime','fare_amount']]

	Request_data.columns =['Pickup_Location','Dropoff_Location','Pickup_time','Dropoff_time','Reward_unit']

	'''Location filtering'''

	Request_data=Request_data.merge(Location_range,left_on='Pickup_Location',right_on='LocationID')

	Request_data=Request_data[['Pickup_Location','Dropoff_Location','Pickup_time','Dropoff_time','Reward_unit']]

	Request_data=Request_data.merge(Location_range,left_on='Dropoff_Location',right_on='LocationID')

	Request_data=Request_data[['Pickup_Location','Dropoff_Location','Pickup_time','Dropoff_time','Reward_unit']]

	'''Time filtering'''

	Request_data['Pickup_Date']=Request_data.apply(lambda x:x['Pickup_time'][:10],axis=1)

	Request_data['Dropoff_Date']=Request_data.apply(lambda x:x['Dropoff_time'][:10],axis=1)

	Request_data['Pickup_step']=Request_data.apply(lambda x:stamp_transition.Get_step(stamp_transition.Get_stamp(x['Pickup_time']),x['Pickup_Date'],600),axis=1)

	Get_Travel_time=lambda loc1,loc2:int(np.ceil(Network_Distance[Location_ID_dic_reverse[loc1]][Location_ID_dic_reverse[loc2]]/speed))

	Request_data['Dropoff_step']=Request_data.apply(lambda x:x['Pickup_step']+Get_Travel_time(x['Pickup_Location'],x['Dropoff_Location']),axis=1)

	Request_data['Dropoff_step']=Request_data.apply(lambda x:x['Dropoff_step']+1 if x['Dropoff_step']==x['Pickup_step'] else x['Dropoff_step'],axis=1)

	Request_data['Order_id']=Request_data.index

	Request_data=Request_data[['Order_id','Pickup_Location','Dropoff_Location','Pickup_step','Dropoff_step','Reward_unit','Pickup_Date','Dropoff_Date']]

	Request_data.to_csv('./Data/Processed/Request_data.csv')


	'''Split by date'''

	Request_data=pd.read_csv(os.path.join(Load_path,'Request_data.csv'))

	Request_data=Request_data.drop(columns=['Unnamed: 0'])

	Date_range=stamp_transition.Get_datelist("2019-11-01", "2019-11-30")

	for date_ in Date_range:
	    
	    R=Request_data.loc[Request_data['Pickup_Date']==date_]
	    
	    R.to_csv('./Data/Daily_Feature/Request_data'+date_+'.csv')
	    
	    
	    '''Count Feature'''
	    
	    Request_count=R.groupby(['Pickup_Location','Pickup_step']).count()[['Reward_unit']]

	    Request_count['Transition']=Request_count.index

	    Request_count['Pickup_Location']=Request_count.apply(lambda x:x['Transition'][0],axis=1)

	    Request_count['Pickup_step']=Request_count.apply(lambda x:x['Transition'][1],axis=1)

	    Request_count=Request_count.reset_index(drop=True)

	    Request_count['Pickup_state']=Request_count.apply(lambda x:str(x['Pickup_Location'])+'-'+str(x['Pickup_step']),axis=1)

	    Request_count=Request_count.rename(index=str, columns={'Reward_unit': 'Order_Cnt'})

	    Request_count=Request_count[['Pickup_state','Order_Cnt']]

	    Request_count_dic={state:0.0 for state in State}

	    for idx,row in Request_count.iterrows():
	    
	        state=row['Pickup_state']
	    
	        Request_count_dic[state]=row['Order_Cnt']
	    
	    np.save('./Data/Daily_Feature/Request_count_dic'+date_+'.npy',Request_count_dic)
	    
	    '''Compute the total quantity'''

	    Dest_PROB=R.groupby(['Pickup_Location','Pickup_step','Dropoff_Location','Dropoff_step']).count()[['Order_id']]

	    Dest_PROB['Transition']=Dest_PROB.index

	    Dest_PROB['Pickup_Location']=Dest_PROB.apply(lambda x:x['Transition'][0],axis=1)

	    Dest_PROB['Pickup_step']=Dest_PROB.apply(lambda x:x['Transition'][1],axis=1)

	    Dest_PROB['Dropoff_Location']=Dest_PROB.apply(lambda x:x['Transition'][2],axis=1)

	    Dest_PROB['Dropoff_step']=Dest_PROB.apply(lambda x:x['Transition'][3],axis=1)

	    Dest_PROB=Dest_PROB.reset_index(drop=True)

	    Dest_PROB=Dest_PROB.rename(index=str, columns={"Order_id": "Order_Cnt"})

	    Dest_PROB=Dest_PROB[['Pickup_Location','Pickup_step','Dropoff_Location','Dropoff_step','Order_Cnt']]

	    '''Compute the destination quantity'''

	    TEMP=R.groupby(['Pickup_Location','Pickup_step']).count()[['Order_id']]

	    TEMP['Transition']=TEMP.index

	    TEMP['Pickup_Location']=TEMP.apply(lambda x:x['Transition'][0],axis=1)

	    TEMP['Pickup_step']=TEMP.apply(lambda x:x['Transition'][1],axis=1)

	    TEMP=TEMP.rename(index=str, columns={"Order_id": "Order_Sum"})

	    TEMP=TEMP.reset_index(drop=True)

	    TEMP=TEMP[['Pickup_Location','Pickup_step','Order_Sum']]

	    Dest_PROB=Dest_PROB.merge(TEMP,on=['Pickup_Location','Pickup_step'])


	    '''Compute the probability'''

	    Dest_PROB['Prob']=Dest_PROB.apply(lambda x:round(float(x['Order_Cnt']/x['Order_Sum']),2),axis=1)

	    Dest_PROB=Dest_PROB[['Pickup_Location','Pickup_step','Dropoff_Location','Dropoff_step','Prob']]

	    Dest_PROB['Pickup_state']=Dest_PROB.apply(lambda x:str(int(x['Pickup_Location']))+'-'+str(int(x['Pickup_step'])),axis=1)

	    Dest_PROB['Dropoff_state']=Dest_PROB.apply(lambda x:str(int(x['Dropoff_Location']))+'-'+str(int(x['Dropoff_step'])),axis=1)

	    Dest_PROB=Dest_PROB[['Pickup_state','Dropoff_state','Prob']]

	    Dest_PROB_dic={}

	    for idx,row in Dest_PROB.iterrows():

	        if row['Pickup_state'] not in Dest_PROB_dic.keys():

	            Dest_PROB_dic[row['Pickup_state']]={}

	            Dest_PROB_dic[row['Pickup_state']][row['Dropoff_state']]=row['Prob']

	        else:

	            Dest_PROB_dic[row['Pickup_state']][row['Dropoff_state']]=row['Prob']

	    np.save('./Data/Daily_Feature/Dest_PROB_dic'+date_+'.npy',Dest_PROB_dic)
	    
	    
	    '''Gain'''
	    
	    Gain_data=R.groupby(['Pickup_Location','Pickup_step','Dropoff_Location','Dropoff_step']).mean()[['Reward_unit']]

	    Gain_data['Transition']=Gain_data.index

	    Gain_data['Pickup_Location']=Gain_data.apply(lambda x:x['Transition'][0],axis=1)

	    Gain_data['Pickup_step']=Gain_data.apply(lambda x:x['Transition'][1],axis=1)

	    Gain_data['Dropoff_Location']=Gain_data.apply(lambda x:x['Transition'][2],axis=1)

	    Gain_data['Dropoff_step']=Gain_data.apply(lambda x:x['Transition'][3],axis=1)

	    Gain_data=Gain_data.reset_index(drop=True)

	    Gain_data['Pickup_state']=Gain_data.apply(lambda x:str(int(x['Pickup_Location']))+'-'+str(int(x['Pickup_step'])),axis=1)

	    Gain_data['Dropoff_state']=Gain_data.apply(lambda x:str(int(x['Dropoff_Location']))+'-'+str(int(x['Dropoff_step'])),axis=1)

	    Gain_data=Gain_data[['Pickup_state','Dropoff_state','Reward_unit']]

	    Gain_dic={}

	    for idx,row in Gain_data.iterrows():

	        if row['Pickup_state'] not in Gain_dic.keys():

	            Gain_dic[row['Pickup_state']]={}

	            Gain_dic[row['Pickup_state']][row['Dropoff_state']]=row['Reward_unit']

	        else:

	            Gain_dic[row['Pickup_state']][row['Dropoff_state']]=row['Reward_unit']
	    
	    np.save('./Data/Daily_Feature/Gain_dic'+date_+'.npy',Gain_dic)
	    
	    print(date_)
    

	