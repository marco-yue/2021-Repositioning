import os, sys
import time
import datetime
import pandas as pd
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt 
import random
import copy

class Dynamic_programming(object):
    
    def __init__(self,Location_list,State,Action,End_step,Gain_dic,Match_PROB_dic,Dest_PROB_dic):
        
        '''Param'''

        self.Location_list=Location_list

        self.State=State

        self.Action=Action

        self.End_step=End_step

        self.gamma=0.8

        '''Reward'''

        self.Gain_dic=Gain_dic

        self.V_table={state:0.0 for state in self.State}

        self.Q_table={}

        for state in self.State:

            self.Q_table[state]={}

            for action in self.Action[state]:

                self.Q_table[state][action]=0.0

        '''Prob'''

        self.Match_PROB_dic=Match_PROB_dic

        self.Dest_PROB_dic=Dest_PROB_dic

        '''Iteration'''

        self.Policy={state:int(state.split('-')[0]) for state in self.State}

        self.Backwards()
        
    def Backwards(self):
        
        for t in range(self.End_step-2,-1,-1):
            
            for loc in self.Location_list:
                
                state=str(int(loc))+'-'+str(int(t))
                
                for action in self.Action[state]:
                    
                     self.Q_table[state][action]= self.Compute_Q(state,action)
                        
                self.V_table[state]=max(self.Q_table[state].values())
                
                self.Policy[state]=max(self.Q_table[state], key=self.Q_table[state].get)
                    
    def Compute_Q(self,state,action):
        
        Prob=self.Match_PROB_dic[state]
        
        step=int(state.split('-')[1])
        
        action_state=str(int(action))+'-'+str(step+1)
        
        '''Matching'''
        
        r_1=0
        
        if action_state in self.Dest_PROB_dic.keys():
        
            for dest_state,dest_prob in self.Dest_PROB_dic[action_state].items():

                dest_step=int(dest_state.split('-')[1])
                
                if dest_step<self.End_step:

                    r_1+=dest_prob*(self.Gain_dic[action_state][dest_state]+self.gamma**(dest_step-step)*self.V_table[dest_state])

        
        '''Not matching'''
        
        r_2=self.gamma*self.V_table[action_state]
        
        return Prob*r_2+(1-Prob)*r_1
        