import pandas as pd
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt 
import random
import Graph
from Graph import Graph

class Reposition(object):
    
    def __init__(self, State, Action,Order_count):
        """ Load your trained model and initialize the parameters """
        self.State=State
        self.Action=Action
        self.Order_count=Order_count
    
    def Hotspot_reposition(self,Repositioning_Dirver,step):
        
        """Choose the action with maximum order count"""

        Repositioning_action={}

        for driver_id, action_list in Repositioning_Dirver.items():
        
            action_dic={a:self.Order_count[str(a)+'-'+str(step)] for a in action_list}

            if sum(action_dic.values())!=0:
            
                action_prob=[action_dic[a]/sum(action_dic.values()) for a in action_list]

                a=np.random.choice(list(action_dic.keys()), p=action_prob)

            else:

                a=np.random.choice(action_list)

            Repositioning_action[driver_id]=a
            
        return Repositioning_action

    def MCMF_reposition(self,Driver_list,Destination_list,Destination_Space,Cost_dic,Capacity_dic):

        '''
        Input: Driver_list,Destination_list,Destination_action,Cost_dic,Capacity_dic
        e.g.

        Driver_list=['d1','d2','d3']

        Destination_list=['g1','g2','g3','g4','g5']

        Destination_Space={'d1':['g1','g2','g3'],'d2':['g2','g3','g4'],'d3':['g3','g4','g5']}

        Cost_={'d1':{'g1':-2,'g2':-5,'g3':-3},'d2':{'g2':-4,'g3':-3,'g4':-5},'d3':{'g3':-2,'g4':-6,'g5':-7}}

        Capacity_={'g1':1,'g2':1,'g3':1,'g4':1,'g5':1}

        Output:

        Repositionning task

        '''

        '''Param'''

        Driver_dic={}

        for i in range(1,1+len(Driver_list),1):

            j=i-1

            Driver_dic[Driver_list[j]]=i

        Destination_dic={}

        for i in range(1+len(Driver_list),1+len(Driver_list)+len(Destination_list),1):

            j=i-len(Driver_list)-1

            Destination_dic[Destination_list[j]]=i

        '''Reverse'''

        Destination_Reverse={}

        for dest,dest_idx in Destination_dic.items():

            Destination_Reverse[dest_idx]=dest


        Node_size=2+len(Driver_list)+len(Destination_list)

        cost=np.ones([Node_size,Node_size])*float('inf')
        
        capacity=np.zeros([Node_size,Node_size])

        for i in range(Node_size):
            
            cost[i][i]=0.0

        '''Generate the cost matrix and capacity matrix'''

        for driver,driver_idx in Driver_dic.items():

            capacity[0][driver_idx]=1.0

            cost[0][driver_idx]=0.0

            for dest in Destination_Space[driver]:

                dest_idx=Destination_dic[dest]

                capacity[driver_idx][dest_idx]=1.0

                cost[driver_idx][dest_idx]=-1*Cost_dic[driver][dest]

                capacity[dest_idx][-1]=Capacity_dic[dest]

                cost[dest_idx][-1]=0.0

        source=0;sink=Node_size-1

        G=Graph(capacity,cost)

        flow=G.MCMF(source,sink)

        reposition_action={}

        for driver,driver_idx in Driver_dic.items():

            if 1.0 in flow[driver_idx]:

                dest_idx=np.argwhere(flow[driver_idx]==1.0)[0][0]

                reposition_action[driver]=Destination_Reverse[dest_idx]

        return reposition_action
        