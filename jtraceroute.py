import socket, argparse, time, json, threading
parser = argparse.ArgumentParser()
parser.add_argument('-p', action="store", dest="p",type=int)
parser.add_argument('target_server', action="store")
args = parser.parse_args()

Start = args.target_server.split(",")[0]
Destination = args.target_server.split(",")[1]


ip = Start.split(":")[0]
port = int(Start.split(":")[1])


packet = {
"uni" : "im2496",
"SEQ" : 1,
"ACK" : 0,
"Data" :
{
"Type" : "TRACE",
"Destination" : Destination,
"Origin": 'localhost:%s' % (args.p),
"TRACE": []
}
}

Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Socket.bind(('', args.p))
Socket.sendto(json.dumps(packet), (ip, port))
rec_message, addr = Socket.recvfrom(2048)

print 'TRACE TABLE', json.loads(rec_message)['Data']['TRACE']
