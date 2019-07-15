# -simulate-GBN-and-RIP
The purpose for this project is to implement two key networking algorithms in transmission layer and network layer. 

Transmission Layer : Implement a basic bidirectional GBN reliability mechanism, without session establishment and without flow or congestion control, but with TCP-like cumulative acknowledgements. go-back-N follows the rules below: 
● Normal packet sending window moves, correct reply ACKs 
● If an ACK is lost, following ACK still moves the window
● If a packet is dropped, it will timeout and packet will be resent 
● If duplicate packets, correct ACK is replied 
● If duplicate ACKs, window will not move twice 

Network Layer : Implement a text-formatted version of the standard intra-domain routing protocol RIP which we call JSON-RIP or JRIP, using the same Bellman-Ford algorithm. RIP follows the rules below: 
● Routing table updates displayed correctly 
● Correct routing tables upon convergence 
● Trace packet shows correct trace according to routing tables
