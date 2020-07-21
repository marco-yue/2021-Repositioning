"""
Author: Marco Yue

Abstract: employing Hotspot distributed walking strategy

Date: 2020-07-21

"""

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


import Dispatch
from Dispatch import Dispatch

import Reposition
from Reposition import Reposition



if __name__ == '__main__':

    '''Basic Path'''

    Daily_path='./Data/Daily_Feature/'

    Load_path='./Data/Processed/'

    Save_path='./Data/Hot_spot/'


    '''Param'''

    End_step=144

    '''Location list'''

    Location_list=np.load(os.path.join(Load_path,'Location_list.npy'))

    Location_ID_dic=np.load(os.path.join(Load_path,'Location_ID_dic.npy')).item()

    Location_ID_dic_reverse=np.load(os.path.join(Load_path,'Location_ID_dic_reverse.npy')).item()

    '''Location Center'''

    Location_Center_dic=np.load(os.path.join(Load_path,'Location_Center_dic.npy')).item()


    '''Connection Matrix and Network distance Matrix'''

    Connect_matrix=np.load(os.path.join(Load_path,'Connect_matrix.npy'))

    Network_Distance=np.load(os.path.join(Load_path,'Network_Distance.npy'))

    '''Geometry_dic'''

    Geometry_dic=np.load(os.path.join(Load_path,'Geometry_dic.npy')).item()


    '''State and Action'''

    State=np.load(os.path.join(Load_path,'State.npy'))

    Action=np.load(os.path.join(Load_path,'Action.npy')).item()

    '''Driver group'''

    data_str='2019-11-01'

    '''Simulation'''

    '''Load the Request data'''

    Request_data=pd.read_csv(os.path.join(Daily_path,'Request_data'+data_str+'.csv'))

    Request_data=Request_data.drop(columns=['Unnamed: 0'])

    Request_data=Request_data[['Order_id','Pickup_Location','Dropoff_Location','Pickup_step','Dropoff_step','Reward_unit']]
    
    Request_data['Dropoff_step']=Request_data.apply(lambda x:x['Dropoff_step']+1 if x['Dropoff_step']==x['Pickup_step'] else x['Dropoff_step'],axis=1)

    Request_data['Driver_id']=-1

    '''Load the Driver data'''

    Driver_data=pd.read_csv(os.path.join(Load_path,'Driver_data.csv'))

    Driver_data=Driver_data.drop(columns=['Unnamed: 0'])
    
    Request_count_dic=np.load(os.path.join(Daily_path,'Request_count_dic'+data_str+'.npy')).item()

    reposition=Reposition(State,Action,Request_count_dic)

    for step in range(End_step):

        driver_count=0

        Unserved_count=0

        Repositioning_Dirver={}

        for location in Location_list:

            '''Construct the match pool: Request_arr and Driver_arr '''

            Request_arr=list(Request_data.loc[(Request_data['Pickup_step']==step)&(Request_data['Pickup_Location']==location),'Order_id'])

            Driver_arr=list(Driver_data.loc[(Driver_data['step']==step)&(Driver_data['Order_id']==-1)&(Driver_data['Location_id']==location),'Driver_id'])

            if len(Driver_arr)!=0:

                dispatch=Dispatch(Request_arr,Driver_arr)

                '''Generate the matched results'''

                Matched_driver,Matched_order=dispatch.random_dispatch()

                '''Update the Request info'''

                for order_id,driver_id in Matched_order.items():

                    if driver_id !=-1:

                        '''Update the matched driver info into the Request info'''

                        Request_data.loc[(Request_data['Pickup_step']==step)&(Request_data['Pickup_Location']==location)&(Request_data['Order_id']==order_id),'Driver_id']=driver_id

                    else:

                        Unserved_count+=1

                '''Update the Driver info'''

                for driver_id,order_id in Matched_driver.items():

                    if order_id!=-1:

                        '''Get the request info by given order_id'''

                        order_info=Request_data.loc[(Request_data['Pickup_step']==step)&(Request_data['Order_id']==order_id),['Dropoff_Location','Dropoff_step']]

                        dropoff_location=int(order_info['Dropoff_Location'])

                        dropoff_step=int(order_info['Dropoff_step'])

                        Driver_data.loc[(Driver_data['step']==step)&(Driver_data['Location_id']==location)&(Driver_data['Driver_id']==driver_id),'Order_id']=order_id

                        Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dropoff_location,'Order_id':-1,'step':dropoff_step}, ignore_index=True)

                        driver_count+=1

                    else:

                        state=str(location)+'-'+str(step)

                        '''Define the reposition strategy'''    

                        if step+1<End_step: 

                            Repositioning_Dirver[driver_id]=Action[state]



        Repositioning_action=reposition.Hotspot_reposition(Repositioning_Dirver,step)

        for driver_id,dest in Repositioning_action.items():

            Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

        print(data_str,step)

        print('Matched driver:',driver_count)

        print('Serve ratio:',round(driver_count/(Unserved_count+driver_count),2))

    Driver_data.to_csv(os.path.join(Save_path,'Driver_data.csv'))

    Request_data.to_csv(os.path.join(Save_path,'Request_data.csv'))





	

