from random import randint
import time 
from rediscluster import StrictRedisCluster
from rediscluster.exceptions import ClusterError
from redis.exceptions import ConnectionError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest = "name", default = "a", help="Name that will be added to key")
args = parser.parse_args()
name = args.name


current_milli_time = lambda: int(round(time.time() * 1000))

startup_nodes = [{"host":"10.240.0.8","port":"6379"},{"host":"10.240.0.10","port":"6379"},{"host":"10.240.0.12","port":"6379"}]
r = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)

id = 0
sessions = {}

deletes = []

#Create 100 sessions
while id < 200:
  #Insert into redis
  sessions[id] = 0
  start = current_milli_time()
  r.set(name + str(id),0)
  end = current_milli_time()
  print(str(end-start)+'ms new '+str(id))
  id = id + 1


while id < 100000:
  try:
    action = randint(1, 3)
    if action == 1:
      #Create
      #Do insert to redis
      start = current_milli_time()
      r.set(name + str(id),1)
      end = current_milli_time()
      print(str(end-start)+'ms new '+str(id))
      sessions[id] = 1
      id = id + 1
    elif action == 2:
      #Update
      k = list(sessions.keys())
      if len(k):
        u = randint(0,len(k)-1)
        #Insert new value
        start = current_milli_time()
        r.set(name + str(k[u]),sessions[k[u]] + 1)
        end = current_milli_time()
        print(str(end-start)+'ms upd ' + str(k[u]))
        sessions[k[u]] = sessions[k[u]] + 1 
    else:
      #Delete
      k = list(sessions.keys())
      if len(k):
        u = randint(0,len(k)-1)
        #Insert into redis
        start = current_milli_time()
        r.delete(name + str(k[u]))
        end = current_milli_time()
        print(str(end-start)+'ms del ' + str(k[u]))
        deletes.append(k[u])
        del(sessions[k[u]])
  except (ClusterError, ConnectionError):
    print('Cluster Timeout') 


#Compare redis sessions to
for key in sessions.keys():
  a =  sessions[key]
  result = r.get(name + str(key))
  if not result:
    print('error missing ' + str(key))
  else:
   b = int(result)
   if a != b:
     print('error unequal '+str(a)+','+str(b))


for item in deletes:
  result = r.get(name + str(item))
  if result:
    print('error not deleted ' + str(item))






