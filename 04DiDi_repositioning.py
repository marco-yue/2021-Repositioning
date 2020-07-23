"""
Author: Marco Yue

Abstract: employing DiDi repositioning methods

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

def flatten(seq):
    s=str(seq).replace('[', '').replace(']', '') 
    s=[eval(x) for x in s.split(',') if x.strip()]
    return list(set(s))



if __name__ == '__main__':

    '''Basic Path'''

    Daily_path='./Data/Daily_Feature/'

    Load_path='./Data/Processed/'

    Save_path='./Data/MCMF/'


    '''Param'''

    End_step=144

    speed=3.0

    Prob_=0.8

    threshold=np.log(1/(1-Prob_)) 

    driver_num=3000

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

    '''Driver Vancant time'''

    Driver_Vacant={}

    for driver_id in range(driver_num):

        Driver_Vacant[driver_id]=0

    for step in range(End_step):

        print(data_str,step)

        driver_count=0

        unserved_order=0

        MCMF_count=0

        Hostspot_count=0

        '''Update drivers quantity'''

        Driver_count_dic={location:0 for location in Location_list}
        Driver_loc=Driver_data.loc[(Driver_data['step']==step)&(Driver_data['Order_id']==-1)].groupby(['Location_id']).count()[['Driver_id']]
        Driver_loc['Location_id']=Driver_loc.index
        Driver_loc=Driver_loc.rename(index=str, columns={"Driver_id": "Driver_Cnt"})
        Driver_loc=Driver_loc.reset_index(drop=True)
        for idx,row in Driver_loc.iterrows():

            Driver_count_dic[row['Location_id']]=row['Driver_Cnt']


        '''Ranking'''

        Locations_hots=[Driver_count_dic[location]-Request_count_dic[str(location)+'-'+str(step)] for location in Location_list]

        Ranked_locations=[y[0] for y in sorted(zip(Location_list, Locations_hots),key=lambda x:x[1],reverse=True)]

        '''enumerate the locations'''

        for location in Ranked_locations:

            MCMF_Driver={}

            Other_Driver={}

            state=str(location)+'-'+str(step)

            '''Construct the match pool: Request_arr and Driver_arr '''

            Request_arr=list(Request_data.loc[(Request_data['Pickup_step']==step)&(Request_data['Pickup_Location']==location),'Order_id'])

            Driver_arr=list(Driver_data.loc[(Driver_data['step']==step)&(Driver_data['Order_id']==-1)&(Driver_data['Location_id']==location),'Driver_id'])

            Vacant_Driver_arr=list()

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

                        unserved_order+=1

                '''Update the Driver info'''

                for driver_id,order_id in Matched_driver.items():

                    if order_id!=-1:

                        Driver_Vacant[driver_id]=0

                        '''Get the request info by given order_id'''

                        order_info=Request_data.loc[(Request_data['Pickup_step']==step)&(Request_data['Order_id']==order_id),['Dropoff_Location','Dropoff_step']]

                        dropoff_location=int(order_info['Dropoff_Location'])

                        dropoff_step=int(order_info['Dropoff_step'])

                        Driver_data.loc[(Driver_data['step']==step)&(Driver_data['Location_id']==location)&(Driver_data['Driver_id']==driver_id),'Order_id']=order_id

                        Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dropoff_location,'Order_id':-1,'step':dropoff_step}, ignore_index=True)

                        driver_count+=1

                    else:

                        Vacant_Driver_arr.append(driver_id)

                        '''Define the reposition strategy'''    

                        if step+1<End_step:

                            Driver_Vacant[driver_id]+=1

                            '''Calculate the capacity'''

                            Activated_action={}

                            for  a in Action[state]:

                                Order_quantity=Request_count_dic[str(a)+'-'+str(step+1)]

                                Driver_quantity=Driver_count_dic[a]

                                Driver_capacity=int(np.ceil(Order_quantity/threshold))

                                Activated_action[a]=Driver_capacity

                            '''Update drivers'''

                            if max(Activated_action.values())>0 and Driver_Vacant[driver_id]>1:

                                MCMF_Driver[driver_id]=[a for a,v in Activated_action.items() if v>0]

                            else:

                                Other_Driver[driver_id]=Action[state]

            if len(MCMF_Driver)!=0:

                '''Modeify the MCMF_Driver '''

                Candidate_driver=[d for d in Other_Driver.keys()]

                buf=int(sum(Activated_action.values())-len(MCMF_Driver))

                buf=min(buf,len(Candidate_driver))

                if buf >0:

                    for k in range(buf):

                        driver_id=Candidate_driver[k]

                        MCMF_Driver[driver_id]=[a for a,v in Activated_action.items() if v>0]

                        del Other_Driver[driver_id]
                
                '''Driver and Destination'''
            
                Driver_list=list(MCMF_Driver.keys())
            
                Destination_list=flatten(list(MCMF_Driver.values()))
                                    
                '''Cost matrix and Capacity matrix'''

                Cost_={}

                Capacity_={}

                for dest in Destination_list:

                    dest_state=str(dest)+'-'+str(step+1)

                    Order_quantity=Request_count_dic[dest_state]

                    Driver_quantity=Driver_count_dic[dest]

                    Driver_capacity=int(np.ceil(Order_quantity/threshold))

                    Capacity_[dest]=Driver_capacity

                    if Driver_quantity!=0:

                        Ratio=float(Order_quantity)/Driver_quantity

                        Match_prob=dispatch.Get_prob(Ratio)

                        cost=(float(Order_quantity)/(Driver_quantity**2))*(Match_prob+1)

                        Cost_[dest]=cost

                    else: 
                        
                        Driver_quantity=0.5

                        Ratio=float(Order_quantity)/Driver_quantity

                        Match_prob=dispatch.Get_prob(Ratio)

                        cost=(float(Order_quantity)/(Driver_quantity**2))*(Match_prob+1)

                        Cost_[dest]=cost
                
                MCMF_action=reposition.MCMF_reposition(Driver_list,Destination_list,MCMF_Driver,Cost_,Capacity_)

                MCMF_count+=len(MCMF_action)


                '''Update Drivers location'''

                for driver_id,dest in MCMF_action.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                    Driver_count_dic[location]-=1

                    Driver_count_dic[dest]+=1


                MCMF_Fail={d:Action[state] for d in MCMF_Driver.keys() if d not in MCMF_action.keys()}

                Other_Driver=dict(list(Other_Driver.items())+list(MCMF_Fail.items()))


            '''Other repositioning'''

            # Repositioning_action=reposition.Hotspot_reposition(Other_Driver,step)

            for driver_id,dest in Other_Driver.items():

                dest=location

                Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                Driver_count_dic[location]-=1

                Driver_count_dic[dest]+=1
                        

        print('Matched Driver:',driver_count)

        print('Serve ratio:',round(driver_count/float(unserved_order+driver_count),2))

    Driver_data.to_csv(os.path.join(Save_path,'Driver_data.csv'))

    Request_data.to_csv(os.path.join(Save_path,'Request_data.csv'))

