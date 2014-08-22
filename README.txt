Jessica Fan jcf2167

a.) 

sample config.txt file given: 

55555 3 file.jpg 2 
128.59.15.34:20002  2
128.59.15.35:20007 7

Client process reads from config.txt and maintains distance vectors and exchanges information with neighbors 128.59.15.34:20002  and 128.59.15.35:20007 to get shortest distance to all nodes with distributed bellman-ford algorithm with poison reverse. 

The follow commands are supported:
LINKDOWN ip_address port 
LINKUP ip_address port weight 
SHOWRT
CLOSE
TRANSFER destination_ip_address port 

b.) coded in sublime and python

c.) Run code as following:

$ python bellman.py config.txt 

On two more machines, you could run neighbors: 128.59.15.34:20002  and 128.59.15.35:20007

d.) sample commands assuming all routers are up and running :

SHOWRT

<23:05:38.270639>Distance vector list is:
 Destination = 128.59.15.35:20007, Cost = 3.0, Link = (128.59.15.34:20002)
 Destination = 128.59.15.34:20002, Cost = 2.0, Link = (160.39.167.228:55555)

LINKDOWN 128.59.15.34 20002

gives the following: 
SHOWRT

<23:06:02.078890>Distance vector list is:
 Destination = 128.59.15.35:20007, Cost = 3.0, Link = (128.59.15.34:20002)
 Destination = 128.59.15.34:20002, Cost = 8.0, Link = (128.59.15.35:20007)

LINKUP 128.59.15.34:20002 2 
CLOSE 
TRANSFER 128.59.15.34 20002



