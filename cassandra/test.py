from random import randint
import time 
import argparse
from cassandra.cluster import Cluster,NoHostAvailable
from cassandra import Unavailable,WriteTimeout


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest = "name", default = "a", help="Name that will be added to key")
args = parser.parse_args()
name = args.name


current_milli_time = lambda: int(round(time.time() * 1000))


cluster = Cluster(['10.240.0.8','10.240.0.10','10.240.0.12'])
s = cluster.connect()
s.execute("create keyspace if not exists testing with replication = {'class': 'SimpleStrategy', 'replication_factor': 2}")
s.execute("create table if not exists testing.testing(row_key varchar PRIMARY KEY, row_value bigint )")
s = cluster.connect("testing")


id = 0
sessions = {}
create_time = {}
deletes = []

#Create 100 sessions
while id < 200:
  #Insert into redis
  sessions[id] = 1
  start = current_milli_time()
  s.execute("INSERT INTO testing (row_key,row_value) VALUES (%s,%s)", [name + str(id),1])
  end = current_milli_time()
  create_time[id] = current_milli_time()
  print(str(end-start)+'ms new '+str(id))
  id = id + 1


while id < 40000:
  try:
    action = randint(1, 3)
    if action == 1:
      #Create
      #Do insert to redis
      start = current_milli_time()
      s.execute("INSERT INTO testing (row_key,row_value) VALUES (%s,%s)", [name + str(id),1])
      end = current_milli_time()
      create_time[id] = current_milli_time()
      print(str(end-start)+'ms new '+str(id))
      sessions[id] = 1
      id = id + 1
    elif action == 2:
      #Update
      k = list(sessions.keys())
      if len(k):
        u = randint(0,len(k)-1)
        #Insert new value

        rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(k[u])])
        if not rows:
          end = current_milli_time()
          start = create_time[k[u]]
          print(str(end-start)+'ms insert missed')    

        start = current_milli_time()
        s.execute("UPDATE testing set row_value=%s where row_key=%s", [sessions[k[u]] + 1,name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms upd ' + str(k[u]))
        sessions[k[u]] = sessions[k[u]] + 1 
    else:
      #Delete
      k = list(sessions.keys())
      if len(k):
        u = randint(0,len(k)-1)

        rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(k[u])])
        if not rows:
          end = current_milli_time()
          start = create_time[k[u]]
          print(str(end-start)+'ms insert missed')

        start = current_milli_time()
        s.execute("DELETE from testing  where row_key=%s", [name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms del ' + str(k[u]))
        deletes.append(k[u])
        del(sessions[k[u]])
  except (Unavailable):
    print('Cassandra unavilable') 
  except(WriteTimeout):
    print('Write timeout')
  except(NoHostAvailable):
    print('No Host Available')

#Compare redis sessions to
for key in sessions.keys():
  a =  sessions[key]
  rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(key)])
  if not rows:
    print('error missing ' + str(key))
  else:
    for row in rows:
      b = row.row_value
      if a != b:
        print('error unequal '+str(a)+','+str(b))


for item in deletes:
  rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(item)])
  if rows:
    print('error not deleted ' + str(item))


