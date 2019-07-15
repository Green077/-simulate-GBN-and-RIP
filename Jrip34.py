import socket, argparse, time, json, threading
from prettytable import PrettyTable
parser = argparse.ArgumentParser()
parser.add_argument('-p', action="store", dest="p",type=int)
parser.add_argument('target_server', action="store")
args = parser.parse_args()

hosts = args.target_server.split(",")
dest = []
cost = []

# represent if the table is updated
falg = False

for i in range(0, len(hosts)):
	dest.append(":".join(hosts[i].split(":")[:2]))
	cost.append(hosts[i].split(":")[-1])

dir_cost = {}
def costTable(dest, cost):
	for i in range(0, len(dest)):
		dir_cost[dest[i]] = int(cost[i])
	return dir_cost

def table_init():
	table = {}
	table['localhost:%s' % (args.p)] = {}
	table['localhost:%s' % (args.p)]['localhost:%s' % (args.p)] = [0, 'localhost:%s' % (args.p)]
	for i in range(0, len(dest)):
		table['localhost:%s' % (args.p)][dest[i]] = [int(cost[i]), dest[i]]
		table[str(dest[i])] = {}
		for j in range(0, len(dest)):
			table[dest[i]]['localhost:%s' % (args.p)] = [float("inf"), 'null']
			table[dest[i]][dest[j]] = [float("inf"), 'null']
	return table


table = table_init()
Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Socket.bind(('', args.p))
#print 'INITIAL TABLE', table
#print '-------------------------------------------------------------'

def new_thread(dest, Socket, table):
	while True:
		for x in dest:
			ip = x.split(":")[0]
			port = int(x.split(":")[1])
			Socket.sendto(json.dumps(table), (ip, port))
		time.sleep(10)
		format_table = tableDisplay(table)
		print format_table

def tableDisplay(table):
	destinations = table['localhost:%s' % (args.p)].keys()
	t = PrettyTable(['IP/PORT DESTINATION', 'DISTANCE', 'NEXT_HOP'])
	for i in range(0, len(destinations)):
		distance = table['localhost:%s' % (args.p)][destinations[i]][0]
		next_hop = table['localhost:%s' % (args.p)][destinations[i]][1]
		t.add_row([destinations[i], distance, next_hop])
	return t

t =threading.Thread(target = new_thread, args=(dest, Socket, table))
t.daemon = True
t.start()
flag = True

def update(directionary1, directionary2, address, cost):
	address = parseAddr(address)
	destionations1 = directionary1[address].keys()
	destionations2 = directionary2['localhost:%s' % (args.p)].keys()
	for item in destionations1:
		if item not in destionations2:
			flag = True
			directionary2['localhost:%s' % (args.p)][item] = [cost[address] + directionary1[address][item][0], 'null']
			directionary2['localhost:%s' % (args.p)][item][1] = address
		else:
			if directionary2['localhost:%s' % (args.p)][item][0] > cost[address] + directionary1[address][item][0]:
				flag = True
				directionary2['localhost:%s' % (args.p)][item][0] = cost[address] + directionary1[address][item][0]
				directionary2['localhost:%s' % (args.p)][item][1] = address
	return directionary2

def parseAddr(address):
	# change to be first element to be 'localhost'
	#change the second element to be a string
	new_tuple_addr = ('localhost', str(list(address)[1]))
	address_str = ":".join(new_tuple_addr)
	return address_str

def replace(directionary1, directionary2, address):
	# directionary1 is received message
	# directionary2 is the table to be repalced
	address_str = parseAddr(address)
	directionary2[address_str] = directionary1[address_str]
	return directionary2

while True:
	rec_message, addr = Socket.recvfrom(2048)
	try:
		message_j = json.loads(rec_message)
	except:
		pass
		print 'Keys:', message_j.keys()
	if 'Data' in message_j.keys():
		message_j['Data']['TRACE'].append('localhost:%s' % (args.p))
		if message_j['Data']['Destination'] == 'localhost:%s' % (args.p):
			origin_ip = message_j['Data']['Origin'].split(":")[0]
			origin_port = int(message_j['Data']['Origin'].split(":")[1])
			# send message back to the Origin
			Socket.sendto(json.dumps(message_j), (origin_ip, origin_port))
		else:
			next_Hop = table['localhost:%s' % (args.p)][message_j['Data']['Destination']][1]
			next_ip = next_Hop.split(":")[0]
			next_port = int(next_Hop.split(":")[1])
			# send message to the next hop
			Socket.sendto(json.dumps(message_j), (next_ip, next_port))
	else:
		dir_cost = costTable(dest, cost)
		if flag == True:
			for x in dest:
				ip = x.split(":")[0]
				port = int(x.split(":")[1])
				Socket.sendto(json.dumps(table), (ip, port))
			flag = False
		table = replace(message_j, table, addr)
		table = update(message_j, table, addr, dir_cost)
