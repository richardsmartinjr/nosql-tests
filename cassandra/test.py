from random import randint
import time 
import argparse
from cassandra.cluster import Cluster

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest = "name", default = "a", help="Name that will be added to key")
args = parser.parse_args()
name = args.name


current_milli_time = lambda: int(round(time.time() * 1000))


cluster = Cluster(['127.0.0.1'])
s = cluster.connect()
s.execute("create keyspace if not exists testing with replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
s.execute("create table if not exists testing.testing(row_key varchar PRIMARY KEY, row_value bigint )")
s = cluster.connect("testing")


id = 0
sessions = {}

deletes = []

#Create 100 sessions
while id < 200:
  #Insert into redis
  sessions[id] = 1
  start = current_milli_time()
  s.execute("INSERT INTO testing (row_key,row_value) VALUES (%s,%d)", [name + str(id),1])
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
      s.execute("INSERT INTO testing (row_key,row_value) VALUES (%s,%d)", [name + str(id),1])
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
        s.execute("UPDATE testing set row_value=%d where row_key=%s", [name + str(k[u]),sessions[k[u]] + 1])
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
        s.execute("DELETE from testing  where row_key=%s", [name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms del ' + str(k[u]))
        deletes.append(k[u])
        del(sessions[k[u]])
  except (ClusterError, ConnectionError):
    print('Cluster Timeout') 


#Compare redis sessions to
for key in sessions.keys():
  a =  sessions[key]
  rows = session.execute('SELECT row_value FROM testing where row_key=%s',[name + str(key)])
  if not rows:
    print('error missing ' + str(key))
  else:
   for row in rows:
    b = row.row_value
    if a != b:
      print('error unequal '+str(a)+','+str(b))


for item in deletes:
  rows = session.execute('SELECT row_value FROM testing where row_key=%s',[name + str(key)])
  if rows:
    print('error not deleted ' + str(item))






