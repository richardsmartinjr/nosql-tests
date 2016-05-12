from random import randint
from time import sleep, time
import argparse
from cassandra.cluster import Cluster,NoHostAvailable
from cassandra import Unavailable,WriteTimeout,ReadTimeout


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest = "name", default = "a", help="Name that will be added to key")
args = parser.parse_args()
name = args.name


current_milli_time = lambda: int(round(time() * 1000))


cluster = Cluster(['10.240.0.8','10.240.0.9'])
s = cluster.connect()
s.execute("create keyspace if not exists testing with replication = {'class': 'SimpleStrategy', 'replication_factor': 2}")
s.execute("create table if not exists testing.testing(row_key varchar PRIMARY KEY, row_value bigint )")
s = cluster.connect("testing")


id = 0
sessions = {}
create_time = {}
deletes = []

writing = True


#Create 100 sessions
while id < 200:
  sleep(0.025)
  #Insert into redis
  sessions[id] = 1
  start = current_milli_time()
  s.execute("INSERT INTO testing (row_key,row_value) VALUES (%s,%s)", [name + str(id),1])
  end = current_milli_time()
  create_time[id] = current_milli_time()
  print(str(end-start)+'ms new '+str(id))
  id = id + 1


while id < 30000:
  sleep(0.025)
  try:
    action = randint(1, 3)
    if action == 1:
      #Create
      #Do insert to redis
      writing = True
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
        u = 0
        if randint(1,3) == 1:
          u = randint(0,len(k)-1)
        else:
          u = randint(int(0.95*len(k)),len(k)-1)
        #Insert new value

        writing = False
        start = current_milli_time()
        rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms read '+str(id))
        start = create_time[k[u]]
        if not rows:
          print(str(end-start)+'ms insert missed')    
        else:
          print(str(end-start)+'ms insert success')

        writing = True
        start = current_milli_time()
        s.execute("UPDATE testing set row_value=%s where row_key=%s", [sessions[k[u]] + 1,name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms upd ' + str(k[u]))
        sessions[k[u]] = sessions[k[u]] + 1 
    else:
      #Delete
      k = list(sessions.keys())
      if len(k):
        u = 0
        if randint(1,3) == 1:
          u = randint(0,len(k)-1)
        else:
          u = randint(int(0.95*len(k)),len(k)-1)


        writing = False
        start = current_milli_time()
        rows = s.execute('SELECT row_value FROM testing where row_key=%s',[name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms read '+str(id))
        start = create_time[k[u]]
        if not rows:
          print(str(end-start)+'ms insert missed')
        else:
          print(str(end-start)+'ms insert success')

        writing = True
        start = current_milli_time()
        s.execute("DELETE from testing  where row_key=%s", [name + str(k[u])])
        end = current_milli_time()
        print(str(end-start)+'ms del ' + str(k[u]))
        deletes.append(k[u])
        del(sessions[k[u]])
  except (Unavailable):
    if writing:
      print('Cassandra writing unavailable error')
    else:
      print('Cassandra reading unavailable error')
  except(WriteTimeout):
    print('Write timeout error')
  except(NoHostAvailable):
    print('No Host Available error')
  except(ReadTimeout):
    print('Read timeout error')

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


