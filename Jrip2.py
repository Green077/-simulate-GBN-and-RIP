import os,sys, socket, argparse, json, threading, time, random, select
from sets import Set
parser = argparse.ArgumentParser()
parser.add_argument('-l', action="store", dest="l", type=float)
parser.add_argument('-p', action="store", dest="p",type=int)
parser.add_argument('target_server', action="store")
args = parser.parse_args()


def islost():
	random_num = random.uniform(0,100)
	if random_num >= args.l * 100:
		return False
	else:
		return True

def startTimer():
	timestamp = time.time()
	return timestamp

def new_thread_send(ipp, clientSocket):
	message_init = {'SEQ': 0, 'ACK': 0, 'DATA': 'EMPTY'}
	window_size = 5
	time_out = 0.5
	while True:
		if Info[ipp]['nextSeq'] < Info[ipp]['base'] + window_size:
			message_init['SEQ'] = Info[ipp]['nextSeq']
			message_init['ACK'] = -1
			if islost() == False:
				clientSocket.sendto(json.dumps(message_init).encode(), ipp)
				print 'SEND', message_init
			Info[ipp]['nextSeq'] += 1

		if Info[ipp]['base'] == Info[ipp]['nextSeq']:
			Info[ipp]['timer'] = startTimer()

		if time.time() - Info[ipp]['timer'] >= time_out:
			for i in range(Info[ipp]['base'], Info[ipp]['nextSeq']):
				message_init['SEQ'] = i
				message_init['ACK'] = -1
				clientSocket.sendto(json.dumps(message_init).encode(), ipp)
				print 'RETRAMISSION', message_init

def new_thread_recv(ipp, clientSocket):
	message_init = {'SEQ': 0, 'ACK': 0, 'DATA': 'EMPTY'}
	while True:
		#print 'NEW_ADDRESS_TUPLE', new_address_tuple
		#print 'Info[base]', Info[new_address_tuple]['base']
		#print 'Info[nextSeq]', Info[new_address_tuple]['nextSeq']
		rec_message, address = clientSocket.recvfrom(2048)
		rec_message_js = json.loads(rec_message)
		print 'Message', rec_message
		new_address_tuple = ('localhost', address[1])

		if Info[new_address_tuple]['base'] != rec_message_js['ACK'] + 1:
			Info[new_address_tuple]['timer'] = startTimer()

		if rec_message_js['SEQ'] == -1:
			Info[new_address_tuple]['base'] = rec_message_js['ACK'] + 1
			#This is an acknowledgement packet and we need to update the window
		else:	
			if Info[new_address_tuple]['count_seq'] == 100:
				with open('logfile.txt %s' % str(new_address_tuple), 'a') as f:
					f.write('Goodput rate at' + str(new_address_tuple) + ' ' + str(len(Info[new_address_tuple]['count_set'])) + '/' + str(Info[new_address_tuple]['count_seq']) + '\n')
			Info[new_address_tuple]['count_seq'] += 1
			Info[new_address_tuple]['count_set'].add(rec_message)
			print '----------', len(Info[new_address_tuple]['count_set']),'/', Info[new_address_tuple]['count_seq'], '----------'
			if rec_message_js['SEQ'] == Info[new_address_tuple]['ack'] + 1:
				#This is a segment and we need to send acknowledgment back
				#Also, update the global ack number
				message_init['SEQ'] = -1
				message_init['ACK'] = rec_message_js['SEQ']
				Info[new_address_tuple]['ack'] += 1
				clientSocket.sendto(json.dumps(message_init).encode(), address)
			else:
				#No need to update global ack number
				message_init['SEQ'] = -1
				message_init['ACK'] = Info[new_address_tuple]['ack']
				clientSocket.sendto(json.dumps(message_init).encode(), address)
		
hosts = args.target_server.split(",")
#parse the argument, serverIp is a list consists of ip addresses(serverIp[0] for first ip)
#serverPort is a list of port numbers(serverPort[0] for first port)
serverIp = []
serverPort = []
for i in range(0, len(hosts)):
	serverIp.append(hosts[i].split(":")[0])
	serverPort.append(hosts[i].split(":")[1])
dest = []
for i in range(0, len(hosts)):
	dest.append((serverIp[i], int(serverPort[i])))

Info = {}
for i in range(0, len(dest)):
	Info[dest[i]] = {}
	Info[dest[i]]['base'] = 0
	Info[dest[i]]['nextSeq'] = 0
	Info[dest[i]]['timer'] = time.time()
	Info[dest[i]]['ack'] = -1
	Info[dest[i]]['count_seq'] = 0
	Info[dest[i]]['count_set'] = Set([])
	# actually, ack = base - 1
print Info


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('', args.p))

for ipp in dest:
	ts =threading.Thread(target = new_thread_send, args=(ipp, clientSocket))
	ts.daemon = True
	ts.start()

tc = threading.Thread(target = new_thread_recv, args = (ipp, clientSocket))
tc.daemon = True
tc.start()

while True:
	time.sleep(1)