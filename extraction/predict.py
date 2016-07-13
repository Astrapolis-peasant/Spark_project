# import dependencies                                                                                                                      
import pyspark
from pyspark.sql import HiveContext
import sys
import os

# zip rows(lists)                                                                                                                          
def parse_list(p):
    if p.Line!=None:
        return zip(p.Line,p.Latitude,p.Longitude,p.RecordedAtTime,p.vehicleID,p.Trip,p.TripDate,p.TripPattern,p.MonitoredCallRef,p.DistFro\
mCall,p.CallDistAlongRoute,p.PresentableDistance)
    else:
        return []

def unix_time(x):
    dt = dateutil.parser.parse(x)
    return time.mktime(dt.timetuple())

def predict(x):
    if len(x) >= 2:
        pre_y = [unix_time(p[3]) for p in x ]
        pre_x = [p[-2] for p in x ]
        f = interp1d(pre_x, pre_y)
    return [(p[-4],f(p[-2]+p[-3])) for p in x] 

if __name__=='__main__':
    sc = pyspark.SparkContext()
    sqlContext = HiveContext(sc)
    bus_file='BusTime/2015_12_03*.jsons' #read multiple_josns                                                                              
    bus = sqlContext.read.json(bus_file)
    bus.registerTempTable("bus") # register into table in order to use sql                                                                 
    with open(sys.argv[-2]) as fr: #read sql                                                                                               
        query = fr.read()
    output = sqlContext.sql(query)     
    output.flatMap(parse_list)\
          .map(lambda x: ",".join(map(str, x)))\
          .map(lambda x:((x[5],x[6]),x)).groupByKey().mapValues(list)\
          .map(lambda x: predict(x[1]))

