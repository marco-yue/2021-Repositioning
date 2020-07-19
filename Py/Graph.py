import pandas as pd
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt 
import random
import collections
from collections import deque

class Graph:
    
    def __init__(self,capacity,cost):
        
        '''capacity matrix'''
        self.capacity = capacity  
        
        '''cost matrix'''
        self.cost = cost
        
        '''flow matrix'''
        
        self.flow=np.zeros(np.shape(self.capacity))

        '''Node'''
        self.node = list(range(len(capacity)))
        
        '''Node size'''
        self.scale = len(self.node)
        
    '''Shortest Path(Minimum-cost) Algorithm'''
    
    def SPFA(self,source,sink):
        
        '''Create array cost_array to store shortest distance'''
        self.cost_array = [float('inf')]*self.scale
        self.cost_array[source]=0
        
        '''Boolean array to check if vertex in the shortest path'''
        self.inQueue = [False]*self.scale
        
        '''Queue'''
        self.queue = deque()
        self.queue.append(source)
        self.inQueue[source] = True
        
        '''Parent visiting Edge'''
        
        self.Parent=[0] * (self.scale)
        
        '''Visited Matrix'''
        
        self.visited = [False] * (self.scale)
        
        self.visited[source]= True
    
        
        while self.queue:
            
            '''Take the front vertex from Queue '''
            u=self.queue.popleft() 
            self.inQueue[u] = False
            
            '''Relaxing all the adjacent edges of vertex taken from the Queue '''
            for v in self.node:
                
                if self.cost[u][v]!=float('inf'):
                    
                    weight=self.cost[u][v]
                    
                    if self.cost_array[v] > self.cost_array[u] + weight and self.flow[u][v]<self.capacity[u][v]:
                        
                        self.cost_array[v]=self.cost_array[u] + weight
                        
                        self.Parent[v]=u
                        
                        self.visited[v]=True
                        
                        '''Check if vertex v is in Queue or not'''
                        if (self.inQueue[v] == False):
                            self.queue.append(v)
                            self.inQueue[v] = True
                            
        return self.visited[sink]
    
    def MCMF(self,source,sink):
        
        '''Initial flow and cost'''
        
        max_flow = 0
        
        min_cost=0
        
        while self.SPFA(source,sink):
            
            current_flow=float('inf')
            
            '''Caculating the current flow'''
            
            current_node=sink
            
            while current_node!=source:
                
                pre_node=self.Parent[current_node]
                
                gap=self.capacity[pre_node][current_node]-self.flow[pre_node][current_node]
                
                current_flow=min(current_flow,gap)
                
                current_node=pre_node
                
            max_flow+=current_flow
            
            '''Updating residual capacities of the edges and reverse edges'''
            
            current_node=sink
            
            while current_node!=source:
                
                pre_node=self.Parent[current_node]
                
                self.flow[pre_node][current_node] += current_flow
                
                self.flow[current_node][pre_node] -= current_flow
                
                current_node=pre_node
                
            min_cost+=self.cost_array[sink]*current_flow
            
        return self.flow