
import socket 
import select 
import sys 
import os
import thread
import Queue
import datetime
import time
from collections import defaultdict
from collections import Counter
import copy 
 

global TIMEOUT
TIMEOUT=0

global COST 
COST=0

global NEXT 
NEXT=1

global SUCCESS
SUCCESS=0

global meta_ID
meta_ID=""

global LOCALPORT 
LOCALPORT =0

global filePart
filePart=""

global LOCALHOST 
LOCALHOST = socket.gethostbyname(socket.getfqdn()) 

global NEIGHBOR
NEIGHBOR= {}

global TOTAL_NODES
TOTAL_NODES=[]

global memfile
memfile=""

def init_graph(): 
    return defaultdict(map_struct)

def map_struct(): 
    return dict(f = '', d='')

global GRAPH
GRAPH = defaultdict(init_graph)

INFINITY=100000

#_______________USER INTERFACE_________________

def handle(s):
	if s=="SHOWRT":
		showrt()
	if "LINKUP" in s:
		news=s.replace("LINKUP ", "")
		arr=news.split(" ")
		linkup(arr[0], arr[1])
	if "LINKDOWN" in s:
		news=s.replace("LINKDOWN ", "")
		arr=news.split(" ")
		linkdown(arr[0], arr[1])
	if "CLOSE" in s:
		close()
	if "TRANSFER" in s:
		news=s.replace("TRANSFER ", "")
		arr=news.split(" ")
		transfer(arr[0], arr[1])
	else:
		pass

def transfer(ip, port):
	print file_chunk_to_transfer + file_sequence_number + " transferred to next hop " + get_ID(ip, port)
		
	line= open(file_chunk_to_transfer, 'rb') #open the file
	st=""
	for l in line:
		st+=l 
	send_N=False
	des_ID=get_ID(ip, port)
	for x in NEIGHBOR:
		if get_ID(x, NEIGHBOR[x])==des_ID: 
			send_N=True
	if send_N:

			MSG= "TRANSFER " + des_ID + "\n"+ meta_ID + "\n" + file_sequence_number+ "\n" + st
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip ,int(port)))
			s.send(MSG)
			s.close()
	else:

		next_hop= GRAPH[meta_ID][des_ID][1].split(":")
		ip=next_hop[0]
		port=int(next_hop[1])

		
		MSG= "TRANSFER " + des_ID + "\n"+ meta_ID + "\n" + file_sequence_number+ "\n" + st
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip ,port))
		s.send(MSG)
		s.close()
		

def showrt():
	graph=GRAPH
	meta_ID=get_ID(LOCALHOST, LOCALPORT)
	current_time = str(datetime.datetime.now().time())
	print "<" + current_time + ">Distance vector list is:"
	for destination in graph[meta_ID]:
		if  destination == meta_ID:
			pass
		else:
			cost= str(graph[meta_ID][destination][0])
			next_hop = graph[meta_ID][destination][1] 
			print " Destination = " + destination + ", Cost = " + cost +", Link = (" + next_hop+ ")"


def linkup(ID, cost):
	meta_ID=get_ID(LOCALHOST, LOCALPORT)
	arr=ID.split(":")
	NEIGHBOR[arr[0]]=int(arr[1])
	N_COST[meta_ID][ID]=float(cost)
	GRAPH[meta_ID][ID]=[float(cost), meta_ID]
	bellman()

def close():
	print "closing down "
	for key in NEIGHBOR:
		if NEIGHBOR[key]!= "LINKDOWN":
			ip=key
			port=int(NEIGHBOR[key])
			msg="CLOSE " + meta_ID 
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip ,port))
			s.send(msg)
			s.close()
	sys.exit()

def linkdown(ip, port):
	#update distance vector
	neighbor_ID= get_ID(ip, port)
	GRAPH[meta_ID][neighbor_ID]=[INFINITY, ""]
	#remove from list of neighbors
	NEIGHBOR[ip] = "LINKDOWN"
	N_COST[meta_ID][neighbor_ID] = INFINITY
	#for each neighbor 
	for key in NEIGHBOR:
		if NEIGHBOR[key]!= "LINKDOWN":
			ip=key
			port=int(NEIGHBOR[key])
			msg="LINKDOWN " + meta_ID +  " " + neighbor_ID
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip ,port))
			s.send(msg)
			s.close()

	bellman()
	ROUTE_UPDATE()

			




################################################

def add_node(destination_ID, cost):

	TOTAL_NODES.append(destination_ID)

	GRAPH[meta_ID][destination_ID]=[float(cost), meta_ID]
	#initializes row 
	GRAPH[destination_ID][""]=[]

	#for all nodes in network (from)
	for i in TOTAL_NODES:
		#for all nodes in network (destination)
		for j in TOTAL_NODES:
			#if from to dest doesn't exist 
			if j not in GRAPH[i]:
				if j is i:
					#if is self, make it zerooooo
					GRAPH[i][j]=[0, ""]
				else:
					#add it 
					GRAPH[i][j]=[INFINITY,""]

def remove_node(ID):

	GRAPH[meta_ID][ID]=[INFINITY, ""]
	GRAPH.delete(ID)
	for x in GRAPH:
		for y in GRAPH[x]: 
			if y==ID:
				GRAPH[x][y]=[INFINITY,""]
			if x==ID:
				GRAPH[x][y]=[INFINITY,""]
	bellman()
	
def print_graph(graph):
	meta_ID=get_ID(LOCALHOST, LOCALPORT)
	for x in graph[meta_ID]:
		print graph[meta_ID][x][0]
	s=""
	for x in graph:
		if x:
			newline=True
			for y in graph[x]:
				if y:
					if newline:
						s+=str(graph[x][y][0])
						newline=False
						s.strip()
					else:
						s+=" "+ str(graph[x][y][0])
						s.strip()
			s+="\n"
	print s 
	
def parse_output(graph):
	s=meta_ID+"\n"
	for dest in graph[meta_ID]:
		s += dest + "=" + str(graph[meta_ID][dest][COST])+"\n"
	return s


def bellman():
	#for each destination 
	for y in GRAPH[meta_ID]:
		#if the destinatino isnt me
		if y != meta_ID:
			#for each neighbor find least cost path to desintaiton
			for key in NEIGHBOR:	
				if NEIGHBOR[key] != "LINKDOWN":
					#V is the neighbor ID 
				
					v= get_ID(key, NEIGHBOR[key])
					#bellman 

					dv_X_Y= float(GRAPH[meta_ID][y][COST])
					cost_X_V=float(N_COST[meta_ID][v])
					dv_V_Y=float(GRAPH[v][y][COST])
				
					if dv_X_Y>cost_X_V+dv_V_Y:
						
						GRAPH[meta_ID][y]=[float(N_COST[meta_ID][v])+float(GRAPH[v][y][COST]),v]
		
	ROUTE_UPDATE()


def parse_input(s):
		arr= [line for line in s.split('\n') if s.strip() != '']
		while '' in arr:
			arr.remove('')
	 	#NEIGHBOR who sent dv to you 
	 	v=arr[0]
	 	arr.pop(0)

	 	#for every entry of neighbors distance vector 
	 	for i in arr:
	 		y=i.split("=")[0]
	 		y.split()

	 		cost=float(i.split("=")[1])

	 		GRAPH[v][y][COST]=float(cost)
	 		GRAPH[v][y][NEXT]=v
	 		if y not in GRAPH[meta_ID]:
	 			add_node(y, cost)
	 		bellman()
		ROUTE_UPDATE()

def get_ID(host, port):
	return host+":"+str(port)


def isNeighbor(i):

	b=False
	for key in NEIGHBOR:
		if NEIGHBOR[key] != "LINKDOWN":
			temp = get_ID(key, NEIGHBOR[key])
			if temp ==i:
				b= True
				break
	return b



def COMPUTE_POISON_GRAPH(GRAPH, neighbor_x):
	meta_ID=get_ID(LOCALHOST, LOCALPORT)
	#send revised graph
	DUPLICATED= defaultdict(init_graph)
	DUPLICATED=copy.deepcopy(GRAPH)
	#for each destination from ME 
	for y in GRAPH[meta_ID]:
		#if the destination isnt me, proceed 
		if y!=meta_ID:
				next_hop=GRAPH[meta_ID][y][1]
				#if go through THIS neighbor to get to dest 
				if isNeighbor(GRAPH[meta_ID][y][1]) and GRAPH[meta_ID][y][1]==neighbor_x :
						#change cost from me to desitnation to INFINITY and send back to neighbor 
						DUPLICATED[meta_ID][y]=[INFINITY, ""]
	return DUPLICATED

def ROUTE_UPDATE():
	#each neighbor gets diff graph bc poison reverse
	for key in NEIGHBOR:
		if NEIGHBOR[key]!= "LINKDOWN":
			ip=key
			port=int(NEIGHBOR[key])
			# take neighbor x and graph and revise graph for neighbor x
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			sock.sendto((parse_output(COMPUTE_POISON_GRAPH(GRAPH, get_ID(key, NEIGHBOR[key])))), (ip, port))

def timeout_start():

	while True:
		time.sleep(3)
		ROUTE_UPDATE()

def listen():
	global SUCCESS
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((LOCALHOST, int(LOCALPORT)))
	s.listen(1)
	while 1:
		conn, addr = s.accept()
		data = conn.recv(4096)
		if "LINKDOWN" in data:
			data.strip()
			t=data.replace("LINKDOWN ", "")
			arr=t.split(" ")
			sender= arr[0]
			dead= arr[1]
			GRAPH[sender][dead]=[INFINITY, ""]
			GRAPH[dead][sender]=[INFINITY, ""]
			GRAPH[meta_ID][sender] = [INFINITY, ""]
			bellman()
	
		if "CLOSE" in data:
			closing=data.strip().replace("CLOSE ", "")
			remove_node(closing)
		if "TRANSFER" in data:
			SUCCESS=SUCCESS+1
			data=data.replace("TRANSFER ","")
			arr=data.split("\n")
		
			des_ID=arr[0]
			path = arr[1]
			seq_n=arr[2]
			arr.pop(0)
			arr.pop(1)
			arr.pop(2)
			f='\n'.join(arr)
			
			if des_ID==meta_ID:
				if SUCCESS==1:
					memfile=f
					current_time = str(datetime.datetime.now().time())
					size= os.stat(file_chunk_to_transfer)
					print " Recieved one of the chunks. Here is data:\n Path: "+ path + " Current Time: " + current_time + " Size: " + str(size.st_size)
				
				if SUCCESS==2:
					if seq_n==1:
						newfile= f +memfile
					else:
						newfile= memfile+ f

						fi = open('output.txt','w')
						fi.write(newfile)
						print "The two chunks have been concatenated and are in output.txt!"
					success=0
					memfile=""
				

			else:
	
				next_hop= GRAPH[meta_ID][des_ID][1].split(":")
				ip=next_hop[0]
				port=int(next_hop[1])
				path += path + "|" + meta_ID
				sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
				MSG= "TRANSFER " + des_ID + "\n"+ path_ + "\n" + f
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((ip ,port))
				s.send(MSG)
				s.close()
		


#________________________________



#N_COST displays cost to neighbors 
N_COST= defaultdict(init_graph)

# opens file, parse first line into PORT, TIMEOUT, and file chunk/seq #
lines = [line.strip() for line in open(sys.argv[1])]
selfarray=lines[0].split() 
LOCALPORT= selfarray[0]
TIMEOUT = int(selfarray[1])
file_chunk_to_transfer = selfarray[2]
file_sequence_number = selfarray[3]
lines.pop(0)

meta_ID=get_ID(LOCALHOST,LOCALPORT)

#initialize self distance to 0 in distance vector 
GRAPH[meta_ID][meta_ID]=[0, ""]

#keep track of total nodes in network 
TOTAL_NODES.append(meta_ID)

for line in lines:
	if line != '':
		#parses file 
	
		neighbor_ID=line.split()[0]
		cost_to_neighbor=line.split()[1].strip()

		IP=neighbor_ID.split(":")[0]
		port=neighbor_ID.split(":")[1]

		#creates dictionary of neighbors --> NEIGHBOR[IP]=PORT
		NEIGHBOR[IP] = int(port)
		#creates array of neighbor cost 
		N_COST[meta_ID][neighbor_ID] = float(cost_to_neighbor)

		#add neighbor node to graph 
		add_node(neighbor_ID, cost_to_neighbor)

thread.start_new_thread(timeout_start,())
thread.start_new_thread(listen,())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((LOCALHOST, int(LOCALPORT)))

#send graph
ROUTE_UPDATE()

input=[sock, sys.stdin]

while True:
	in_r, out_r, except_r = select.select(input,[],[]) 
	for s in in_r:
		if s == sys.stdin:
			command = sys.stdin.readline().strip()
			handle(command)

		else:
			data, addr = sock.recvfrom(7000)
			parse_input(data)
		
	










