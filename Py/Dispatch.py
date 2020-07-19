import math
import random
import numpy as np

class Dispatch(object):
    
    def __init__(self, order_arr, driver_arr):
        self.order_arr=order_arr
        self.driver_arr=driver_arr
    
    def Get_prob(self,ratio):
        
        prob= 1/(1+np.exp(-1*ratio))
        
        if prob>ratio:
            
            return ratio
        
        else:
        
            return prob

    def random_dispatch(self):
        
        ratio=float(len(self.order_arr))/len(self.driver_arr)
        prob=self.Get_prob(ratio)
        if np.random.rand()<=prob:
            dispatched_num=int(np.ceil(prob*len(self.driver_arr)))
            dispatched_num=min(dispatched_num,len(self.order_arr))
        else:
            dispatched_num=0
        dispatched_order={};dispatched_driver={}
        
        driver_pool=random.sample(self.driver_arr,dispatched_num)
        
        for i in range(dispatched_num):
            dispatched_driver[driver_pool[i]]=self.order_arr[i]
            dispatched_order[self.order_arr[i]]=driver_pool[i]
            
        for d in self.driver_arr:
            if d not in dispatched_driver.keys():
                dispatched_driver[d]=-1
            
        for o in self.order_arr:
            if o not in dispatched_order.keys():
                dispatched_order[o]=-1
                
            
        return dispatched_driver,dispatched_order