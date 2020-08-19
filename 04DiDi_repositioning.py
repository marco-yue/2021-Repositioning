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

from Stamp_transition import Stamp_transition

def flatten(seq):

    s=str(seq).replace('[', '').replace(']', '') 
    s=[eval(x) for x in s.split(',') if x.strip()]
    return list(set(s))


def Compute_Delta(threhold,O_num):

    denominator=np.log(1/(1-threhold))
    return int(O_num/denominator)

def Get_utility(O_num,D_num):
    
    ratio=float(O_num)/D_num
    
    return (float(O_num)/(D_num**2))*(dispatch.Get_prob(ratio)+1)



if __name__ == '__main__':

    '''Basic Path'''

    Daily_path='./Data/Daily_Feature/'

    Load_path='./Data/Processed/'

    Save_path='./Data/MCMF/'

    driver_num=3000


    '''Param'''

    End_step=144

    speed=3.0

    Prob_=0.7

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

    stamp_transition=Stamp_transition()

    Date_range=stamp_transition.Get_datelist("2019-11-01", "2019-11-07")

    for data_str in Date_range:


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

            MCMF_Driver={}

            Other_Driver={}

            '''Count the driver quantity at next step'''

            Driver_count_dic={location:0 for location in Location_list}

            '''enumerate the locations'''

            for location in Location_list:


                state=str(location)+'-'+str(step)

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

                            unserved_order+=1

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

                            Driver_Vacant[driver_id]=0

                            if dropoff_step==step+1:Driver_count_dic[dropoff_location]+=1

                        else:

                            '''Define the reposition strategy'''    

                            if step+1<End_step:

                                '''Calculate avaiable destinations'''

                                Driver_Vacant[driver_id]+=1

                                Activated_action={}

                                for  a in Action[state]:

                                    Order_quantity=Request_count_dic[str(a)+'-'+str(step+1)]

                                    Activated_action[a]=Compute_Delta(Prob_,Order_quantity)

                                '''Update drivers'''

                                if max(Activated_action.values())>0:

                                    MCMF_Driver[driver_id]=[a for a,v in Activated_action.items() if v>0]

                                else:

                                    Other_Driver[driver_id]=Action[state]

            if len(Other_Driver)!=0:

                Repositioning_action=reposition.Hotspot_reposition(Other_Driver,step)

                for driver_id,dest in Repositioning_action.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                    Driver_count_dic[dest]+=1

            if len(MCMF_Driver)!=0:

                '''Update Driver quantity'''

                for driver,loc_list in MCMF_Driver.items():

                    prob=1.0/float(len(loc_list))

                    for loc in loc_list:

                        Driver_count_dic[loc]+=prob
                
                '''Driver and Destination'''
            
                Driver_list=list(MCMF_Driver.keys())
            
                Destination_list=flatten(list(MCMF_Driver.values()))
                                        
                '''Cost matrix and Capacity matrix'''

                Capacity_={}


                for dest in Destination_list:

                    dest_state=str(dest)+'-'+str(step+1)

                    Order_quantity=Request_count_dic[dest_state]

                    Capacity_[dest]=Compute_Delta(Prob_,Order_quantity)


                Cost_={}

                for driver_id in MCMF_Driver.keys():

                    Cost_[driver_id]={}

                    for dest in Destination_list:

                        if dest not in MCMF_Driver[driver_id]:

                            Cost_[driver_id][dest]=0.0

                        else:
                            
                            dest_state=str(dest)+'-'+str(step+1)

                            Order_quantity=Request_count_dic[dest_state]

                            Driver_quantity=Driver_count_dic[dest]

                            if Driver_quantity!=0:

                                Cost_[driver_id][dest]=Driver_Vacant[driver_id]*Get_utility(Order_quantity,Driver_quantity)

                            else: 
                                
                                Driver_quantity=0.1

                                Cost_[driver_id][dest]=Driver_Vacant[driver_id]*Get_utility(Order_quantity,Driver_quantity)
                    
                MCMF_action=reposition.MILP_Optimization(Driver_list,Destination_list,Cost_,Capacity_)



                '''Update Drivers location'''

                for driver_id,dest in MCMF_action.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)


                MCMF_Fail={d:Action[state][0] for d in MCMF_Driver.keys() if d not in MCMF_action.keys()}

            
                for driver_id,dest in MCMF_Fail.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                            
            print('Matched Driver:',driver_count)

            print('Serve ratio:',round(driver_count/(1+float(unserved_order+driver_count)),2))

            print('*'*50)


        Driver_data.to_csv(os.path.join(Save_path,'Driver_data'+data_str+'.csv'))

        Request_data.to_csv(os.path.join(Save_path,'Request_data'+data_str+'.csv'))

