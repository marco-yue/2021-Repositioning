import pulp

import numpy as np

class Columns_generation(object):
    
    def __init__(self,Driver_list,Destination_list,Q_table,Capacity_):
        
        '''Param'''
        
        self.Driver_list=Driver_list
        self.Destination_list=Destination_list
        self.Q_table=Q_table
        self.Capacity_=Capacity_
        self.Get_param()
        
    def Get_param(self):
        
        '''Intermediate Param'''
        
        self.driver_num=len(self.Driver_list)
        self.dest_num=len(self.Destination_list)
        self.Driver_dic={self.Driver_list[i]:i for i in range(self.driver_num)}
        self.Driver_dic_inverse={i:self.Driver_list[i] for i in range(self.driver_num)}
        self.Destination_dic={self.Destination_list[i]:i for i in range(self.dest_num)}
        
        '''Inverse the Q table'''
        
        self.Inverse_Q={dest:{} for dest in self.Destination_list}

        for driver,q_table in self.Q_table.items():

            for dest in q_table.keys():

                self.Inverse_Q[dest][driver]=q_table[dest]
                
    def Get_initialization(self):
        
        '''Initialize Soulution'''
        
        Solution={dest:np.zeros([1,self.driver_num],dtype='int') for dest in self.Destination_list}

        for dest in self.Destination_list:

            assigned_capacity=0

            for driver,q_value in self.Inverse_Q[dest].items():

                if q_value>0:

                    driver_idx=self.Driver_dic[driver]

                    Solution[dest][0,driver_idx]=1

                    assigned_capacity+=1

                    if assigned_capacity >= self.Capacity_[dest]:

                        break
        
        K_num={dest:len(Solution[dest]) for dest in self.Destination_list}
        
        return Solution,K_num
        
    def Get_RMP(self,Solution,K_num):
        
        '''Model definition'''

        RMP = pulp.LpProblem('RMP',pulp.LpMaximize)

        '''Variable'''

        Lambda = pulp.LpVariable.dicts("Lambda",\
                                       ((a, k) for a in self.Destination_list for k in range(K_num[a])),\
                                       lowBound = 0,\
                                       cat='Continuous')

        '''Objective Function'''

        RMP += pulp.lpSum([pulp.lpSum([self.Q_table[d][a] *Solution[a][k][self.Driver_dic[d]] for d in self.Driver_list])*Lambda[(a,k)] for a in self.Destination_list for k in range(K_num[a])])

        '''Constraints'''

        '''Every action can be only assigned only one solution'''

        for a in self.Destination_list:

            RMP += pulp.lpSum([Lambda[(a,k)] for k in range(K_num[a])]) <=1

        '''Every driver can be only assigned one action'''

        for d in self.Driver_list:

            RMP += pulp.lpSum([Lambda[(a,k)]*Solution[a][k][self.Driver_dic[d]] for a in self.Destination_list for k in range(K_num[a])]) <=1

        return Lambda,RMP
    
    def Get_Pricing(self,Dual,a):
        
        '''Dual Solution'''

        Dual_a={self.Destination_list[i]:Dual[i] for i in range(len(self.Destination_list))}

        Dual_d={self.Driver_list[i-len(self.Destination_list)]:Dual[i] for i in range(len(self.Destination_list),len(Dual),1)}
        
        '''Pricing problems'''

        Pricing = pulp.LpProblem('Pricing',pulp.LpMaximize)

        '''Variable'''

        Y = pulp.LpVariable.dicts("Y",((a, d) for d in self.Driver_list),lowBound=0,upBound=1,cat='Integer')

        '''Objective'''

        Pricing +=pulp.lpSum([(self.Inverse_Q[a][d]-Dual_d[d])*Y[(a,d)] for d in self.Driver_list])-Dual_a[a] 

        '''Constraint'''

        Pricing += pulp.lpSum([Y[(a,d)] for d in self.Driver_list])<= self.Capacity_[a]
        
        return Y,Pricing
    
    def Get_solution(self,Lambda,Solution):

        repoosition_action={}
        
        '''Translate the solution of RMP'''
        for var in Lambda:
            if Lambda[var].varValue !=0:
                dest=var[0];k_dest=var[1]
                for i in range(self.driver_num):
                    if Solution[dest][k_dest][i]==1:
                        driver=self.Driver_dic_inverse[i]
                        repoosition_action[driver]=dest
        return repoosition_action

        
        
        
        