import time
import datetime
import pandas as pd

class Stamp_transition(object):
    
    def __init__(self, **kwargs):
        """ Load your trained model and initialize the parameters """
        pass
    
    def Get_date(self,stamp):
        dateArray = datetime.datetime.fromtimestamp(stamp)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        return otherStyleTime[:10]
    
    '''Time stamp'''
    def Get_stamp(self,time_str):
        timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp
    
    '''Time step'''
    def Get_step(self,stamp,date_str,step):
        baseline = date_str+" 00:00:00";
        baseline = int(self.Get_stamp(baseline))
        current_step=int((stamp-baseline)/step)
        return current_step
    
    def Get_datelist(self, beginDate, endDate):
        date_list=[datetime.datetime.strftime(x,'%Y-%m-%d') for x in list(pd.date_range(start=beginDate, end=endDate))]
        return date_list
    
    def Get_weekday(self,date_str):
        date_str = date_str+" 00:00:00";
        date_str = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_str.tm_wday+1

    def Get_normalization(self,end_step,t_step):
        if t_step>=end_step:
            return t_step-end_step
        else:
            return t_step
            
    def Get_Yesterday(self,date_str):

        Yesterday=datetime.datetime.strptime(date_str, "%Y-%m-%d").date() + datetime.timedelta(days = -1)

        return str(Yesterday.strftime('%Y-%m-%d'))

