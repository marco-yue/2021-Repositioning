"""
Author: Marco Yue

Abstract: employing CMMDP and Columns Generations

Date: 2020-08-16

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

from Dynamic_programming import Dynamic_programming

def Get_prob(ratio):
        
    prob = 1- np.exp(-1*ratio)

    return prob

def flatten(seq):
    s=str(seq).replace('[', '').replace(']', '') 
    s=[eval(x) for x in s.split(',') if x.strip()]
    return list(set(s))

def Compute_Delta(threhold,O_num):
    denominator=np.log(1/(1-threhold))
    return int(O_num/denominator)

def Get_utility(O_num,D_num):
    
    ratio=float(O_num)/D_num
    
    return (float(O_num)/(D_num**2))*(Get_prob(ratio)+1)



if __name__ == '__main__':


    '''Basic Path'''

    Daily_path='./Data/Daily_Feature/'

    Load_path='./Data/Processed/'

    Save_path='./Data/CMMDP/'

    End_step=144

    speed=3.0

    Prob_={}

    for t in range(12):
        Prob_[t]=0.5
    for t in range(12,42,1):
        Prob_[t]=0.3
    for t in range(42,108,1):
        Prob_[t]=0.7
    for t in range(108,End_step,1):
        Prob_[t]=0.85





    driver_num=3000


    '''
    ***************************************************************************************************************************************

    ***************************************************************************************************************************************

    '''

    '''Basic Data'''


    stamp_transition=Stamp_transition()

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


    '''
    ***************************************************************************************************************************************

    ***************************************************************************************************************************************

    '''


    Date_range=stamp_transition.Get_datelist("2019-11-01", "2019-11-07")

    for date_str in Date_range:

    

        '''
        Dynamic programming for Q values

        '''


        Yesterday=stamp_transition.Get_Yesterday(date_str)


        '''Prob matrix'''

        Dest_PROB_dic=np.load(os.path.join(Daily_path,'Dest_PROB_dic'+Yesterday+'.npy')).item()

        Gain_dic=np.load(os.path.join(Daily_path,'Gain_dic'+Yesterday+'.npy')).item()

        '''Get Matching Probability'''

        Request_count_dic=np.load(os.path.join(Daily_path,'Request_count_dic'+Yesterday+'.npy')).item()


        '''Historical Driver data '''

        Driver_data=pd.read_csv(os.path.join(Save_path,'Driver_data'+Yesterday+'.csv'))

        Driver_count=Driver_data.groupby(['Location_id','step']).count()[['Driver_id']]

        Driver_count['Transition']=Driver_count.index

        Driver_count['Pickup_Location']=Driver_count.apply(lambda x:x['Transition'][0],axis=1)

        Driver_count['Pickup_step']=Driver_count.apply(lambda x:x['Transition'][1],axis=1)

        Driver_count=Driver_count.rename(index=str, columns={"Driver_id": "Driver_Sum"})

        Driver_count=Driver_count.reset_index(drop=True)

        Driver_count=Driver_count[['Pickup_Location','Pickup_step','Driver_Sum']]


        Match_PROB_dic={state:0.0 for state in State}

        for idx,row in Driver_count.iterrows():
            
            if row['Pickup_step']<End_step:
            
                state=str(int(row['Pickup_Location']))+'-'+str(int(row['Pickup_step']))

                if row['Driver_Sum']==0:

                    ratio=999

                    Match_PROB_dic[state]=Get_prob(ratio)

                else:

                    ratio=Request_count_dic[state]/row['Driver_Sum']

                    Match_PROB_dic[state]=Get_prob(ratio)

        Dynamic_P=Dynamic_programming(Location_list,State,Action,End_step,Gain_dic,Match_PROB_dic,Dest_PROB_dic)

        Q_table=Dynamic_P.Q_table


        '''Planning'''

        '''Instant Reward'''

        Request_fee_dic=np.load(os.path.join(Daily_path,'Request_fee_dic'+date_str+'.npy')).item()
        

        '''Load the Request data'''

        Request_data=pd.read_csv(os.path.join(Daily_path,'Request_data'+date_str+'.csv'))

        Request_data=Request_data.drop(columns=['Unnamed: 0'])

        Request_data=Request_data[['Order_id','Pickup_Location','Dropoff_Location','Pickup_step','Dropoff_step','Reward_unit']]
        
        Request_data['Dropoff_step']=Request_data.apply(lambda x:x['Dropoff_step']+1 if x['Dropoff_step']==x['Pickup_step'] else x['Dropoff_step'],axis=1)

        Request_data['Driver_id']=-1

        '''Load the Driver data'''

        Driver_data=pd.read_csv(os.path.join(Load_path,'Driver_data.csv'))

        Driver_data=Driver_data.drop(columns=['Unnamed: 0'])
        
        Request_count_dic=np.load(os.path.join(Daily_path,'Request_count_dic'+date_str+'.npy')).item()

        reposition=Reposition(State,Action,Request_count_dic)

        '''Driver Vancant time'''

        Driver_Vacant={}

        for driver_id in range(driver_num):

            Driver_Vacant[driver_id]=0

        for step in range(End_step):

            print(date_str,step)

            driver_count=0

            unserved_order=0

            Rep_Driver={}

            Rep_Driver_state={}


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

                                    Activated_action[a]=Compute_Delta(Prob_[step],Order_quantity)

                                '''Update drivers'''

                                if max(Activated_action.values())>0:

                                    Rep_Driver[driver_id]=[a for a,v in Activated_action.items() if v>0]

                                    Rep_Driver_state[driver_id]=state

                                else:

                                    Other_Driver[driver_id]=Action[state]

            if len(Other_Driver)!=0:

                Repositioning_action=reposition.Hotspot_reposition(Other_Driver,step)

                for driver_id,dest in Repositioning_action.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                    Driver_count_dic[dest]+=1


            if len(Rep_Driver)!=0:

                '''Update Driver quantity'''

                for driver,loc_list in Rep_Driver.items():

                    prob=1.0/float(len(loc_list))

                    for loc in loc_list:

                        Driver_count_dic[loc]+=prob
                
                '''Driver and Destination'''
            
                Driver_list=list(Rep_Driver.keys())
            
                Destination_list=flatten(list(Rep_Driver.values()))
                                        
                '''Cost matrix and Capacity matrix'''

                Capacity_={}


                for dest in Destination_list:

                    dest_state=str(dest)+'-'+str(step+1)

                    Order_quantity=Request_count_dic[dest_state]

                    Capacity_[dest]=Compute_Delta(Prob_[step],Order_quantity)


                Cost_={}

                for driver_id in Rep_Driver.keys():

                    Cost_[driver_id]={}

                    for dest in Destination_list:

                        dest_state=str(dest)+'-'+str(step+1)

                        if dest not in Rep_Driver[driver_id]:

                            Cost_[driver_id][dest]=0.0

                        else:

                            Order_quantity=Request_count_dic[dest_state]

                            Driver_quantity=Driver_count_dic[dest]

                            ratio=float(Order_quantity)/Driver_quantity

                            # utility=Get_utility(Order_quantity,Driver_quantity)

                            Match_prob=Get_prob(ratio)

                            Expected_reward=Q_table[Rep_Driver_state[driver_id]][dest]

                            Instant_reward=Request_fee_dic[dest_state]*Match_prob

                            Cost_[driver_id][dest]=Expected_reward+Instant_reward
                    
                Rep_action=reposition.MILP_Optimization(Driver_list,Destination_list,Cost_,Capacity_)

                '''Update Drivers location'''

                for driver_id,dest in Rep_action.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)


                Rep_fail={d:Action[state][0] for d in Rep_Driver.keys() if d not in Rep_action.keys()}


                '''Other repositioning'''

                for driver_id,dest in Rep_fail.items():

                    Driver_data=Driver_data.append({'Driver_id': driver_id,'Location_id':dest,'Order_id':-1,'step':step+1}, ignore_index=True)

                            
            print('Matched Driver:',driver_count)

            print('Serve ratio:',round(driver_count/(1+float(unserved_order+driver_count)),2))

            print('*'*50)

        

        Driver_data.to_csv(os.path.join(Save_path,'Driver_data'+date_str+'.csv'))

        Request_data.to_csv(os.path.join(Save_path,'Request_data'+date_str+'.csv'))



            
    





