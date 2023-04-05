
import messages_pb2
import socket
import threading
import time
import signal
from vcbc_state import VCBCState,ReadyState
from coin import Coin
from aba_state import ABAState
from timer import Timer

# msg = messages_pb2.VCBCSend()
# msg.data = "text"
# msg.author = 1
# msg.priority = 0

# print(f"{msg.data=}")
# serialized_msg = msg.SerializeToString()
# print(f"{serialized_msg=}")

# deserialized_msg = messages_pb2.VCBCSend()
# deserialized_msg.ParseFromString(serialized_msg)
# print(f"{deserialized_msg.data=}")

# Define message types
MESSAGE_TYPES = {
    1: messages_pb2.VCBCSend,
    2: messages_pb2.VCBCReady,
    3: messages_pb2.VCBCFinal,
    4: messages_pb2.ABAInit,
    5: messages_pb2.ABAAux,
    6: messages_pb2.ABAConf,
    7: messages_pb2.ABAFinish
}


def create_connection(addr,port):
    # create a persistent TCP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    return sock


class node:

    def __init__(self,node_number,number_of_nodes):

        # NODE CONFIGURATION
        self.node_number = node_number

        self.number_of_operators = number_of_nodes
        self.f = (number_of_nodes-1)//3

        self.vcbc_state = VCBCState(list(range(1,self.number_of_operators+1)))
        self.aba_state = ABAState(list(range(1,self.number_of_operators+1)))

        self.ready_state = ReadyState()
        
        self.priority = 0

        # NETWORK CONFIGURATION
        self.addr = 'localhost'
        self.port = 1350

        # START SERVER
        start_server_tread = threading.Thread(target=self.server, args=())
        start_server_tread.start()

        # WAIT OTHER NODES TO START
        time.sleep(self.number_of_operators*0.15)

        # SOCKETS WITH OTHER NODES
        self.connections = {n: create_connection(self.addr,self.port+n) for n in range(1,self.number_of_operators+1)}
        # self.connections = {}

        # CREATES SIGINT HANDLER -> TO CLOSE CONNECTIONS
        signal.signal(signal.SIGINT, self.signal_handler)

    def getSocket(self,node_number):
        if node_number in self.connections:
            return self.connections[node_number]
        else:
            self.connections[node_number] = create_connection(self.addr,self.port+node_number)
            return self.connections[node_number]

    def getQuorum(self):
        return 2*self.f+1
        # return 1

    def getPartialQuorum(self):
        return self.f+1
        # return 1

    # SIGNIT HANDLER -> CLOSE CONNECTIONS
    def signal_handler(self, sig, frame):
        print('Caught interrupt signal, closing connections...')
        self.close()

    # CLOSE NODE -> CLOSE CONNECTIONS (+ SERVER SOCKET)
    def close(self):
        # Close the connections
        for sock in self.connections.values():
            sock.close()

        # Close the server socket
        self.sock.close()


    # SERVER FUNCTION
    def server(self):
        # create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to a specific address and port
        server_address = (self.addr, self.port + self.node_number)
        self.sock.bind(server_address)

        # listen for incoming connections
        self.sock.listen(self.number_of_operators+1)

        # dictionary of persistent connections
        connections = {}

        while True:
            # wait for a connection
            print("Waiting for a connection...")
            conn, addr = self.sock.accept()

            # if the connection is already in the dictionary of connections, close it
            if addr in connections:
                print("Connection from %s:%d already exists, closing new connection" % addr)
                conn.close()
            else:
                # handle the connection in a new thread
                handle_thread = threading.Thread(target=self.handle_connection, args=(conn, addr, connections))
                handle_thread.start()
    
    # HANDLE CONNECTION FROM OTHER NODE
    # KEEPS CONNECTION PERSISTENT
    # GETS MESSAGE AND CALLS PROCESS_MSG
    def handle_connection(self,conn, addr, connections):
        print("Accepted connection from %s:%d" % addr)

        # add the connection to the dictionary of connections
        connections[addr] = conn

        try:
            while True:
                # receive a message from the client
                message = self.receive_message(conn)
                # print("Received message from %s:%d" % addr)
                # print("  data: %s" % message.data)
                # print("  priority: %d" % message.priority)
                # print("  author: %d" % message.author)
                self.process_message(message)
        except Exception as e:
            print("Error handling connection from %s:%d: %s" % (addr[0], addr[1], str(e),print(e.__traceback__)))

        # remove the connection from the dictionary of connections
        del connections[addr]

        # close the connection
        conn.close()
    
    # RECEIVE MESSAGE AND RETURNS
    def receive_message(self,sock):

        # ===================
        #   Message length
        # ===================
        # receive the message length header
        header_bytes = b''
        while len(header_bytes) < 4:
            header_chunk = sock.recv(4 - len(header_bytes))
            if not header_chunk:
                raise Exception("Connection closed before message length header received")
            header_bytes += header_chunk

        # parse the message length
        message_length = int.from_bytes(header_bytes, byteorder='big')
        # message_length = struct.unpack('>I', header_bytes)[0]

        # ===================
        #   Message type
        # ===================
        # receive the message length header
        mgs_type_bytes = b''
        while len(mgs_type_bytes) < 2:
            header_chunk = sock.recv(2 - len(mgs_type_bytes))
            if not header_chunk:
                raise Exception("Connection closed before message type header received")
            mgs_type_bytes += header_chunk

        # parse the message length
        message_type = int.from_bytes(mgs_type_bytes, byteorder='big')

        # ===================
        #   Message data
        # ===================
        # receive the message body in chunks
        message_bytes = b''
        while len(message_bytes) < message_length:
            chunk_size = min(4096, message_length - len(message_bytes))
            message_chunk = sock.recv(chunk_size)
            if not message_chunk:
                raise Exception("Connection closed before message received")
            message_bytes += message_chunk


        # ===================
        #   Message deserialization
        # ===================

        # deserialize the message from the received bytes
        msg_type = MESSAGE_TYPES[message_type]
        message = msg_type.FromString(message_bytes)

        # return the message
        return message
    
    # PROCESS MESSAGE
    def process_message(self,message):
        # print(message)

        if isinstance(message,messages_pb2.VCBCSend):
            print(f"VCBCSend:{message}")
            self.uponVCBCSend(message)
        elif isinstance(message,messages_pb2.VCBCReady):
            print(f"VCBCReady:{message}")
            self.uponVCBCReady(message)
        elif isinstance(message,messages_pb2.VCBCFinal):
            print(f"VCBCFinal:{message}")
            self.uponVCBCFinal(message)
        elif isinstance(message,messages_pb2.ABAInit):
            print(f"ABAInit:{message}")
            self.uponABAInit(message)
        elif isinstance(message,messages_pb2.ABAAux):
            print(f"ABAAux:{message}")
            self.uponABAAux(message)
        elif isinstance(message,messages_pb2.ABAConf):
            print(f"ABAConf:{message}")
            self.uponABAConf(message)
        elif isinstance(message,messages_pb2.ABAFinish):
            print(f"ABAFinish:{message}")
            self.uponABAFinish(message)

    # SEND MESSAGE
    def send_message(self,message,sock,msg_type = 1):
        # serialize the message to bytes
        message_bytes = message.SerializeToString()

        # prepend the message length to the byte string
        message_length = len(message_bytes)
        message_length_bytes = message_length.to_bytes(4, byteorder='big')

        message_type_bytes = msg_type.to_bytes(2,byteorder='big')
        # message_length_bytes = struct.pack('>I', message_length)
        data = message_length_bytes + message_type_bytes +  message_bytes

        # send the data over the socket
        sock.sendall(data)
    
    def broadcast(self,message,msg_type = 1):
        # serialize the message to bytes
        message_bytes = message.SerializeToString()

        # prepend the message length to the byte string
        message_length = len(message_bytes)
        message_length_bytes = message_length.to_bytes(4, byteorder='big')

        message_type_bytes = msg_type.to_bytes(2,byteorder='big')
        # message_length_bytes = struct.pack('>I', message_length)
        data = message_length_bytes + message_type_bytes +  message_bytes

        # send the data over the socket
        # for sock in self.connections.values():
        #     sock.sendall(data)
        for i in range(1,self.number_of_operators+1):
            sock = self.getSocket(i)
            sock.sendall(data)

    def createPeriodicalVCBC(self):
        step = 0
        while True:
            
            time.sleep(3)
            Timer.startTimer(f'{self.priority}')
            self.StartVCBC(f'data_from_priority{self.priority}')
            # time.sleep(20)
            break
            
        while True:
            pass

            
                
    def StartVCBC(self,data):
        message = messages_pb2.VCBCSend()
        message.data = data
        message.priority = self.priority
        message.author = self.node_number
        msg_type = 1

        self.priority += 1

        self.broadcast(message,msg_type=msg_type)

    # ================================================================================================
    # uponMessage methods
    # ================================================================================================
    
    def uponVCBCSend(self,message):
        data = message.data
        priority = message.priority
        author = message.author

        if not self.vcbc_state.has(author,priority):
            self.vcbc_state.add(author,data,priority)
        
        message = messages_pb2.VCBCReady()
        message.priority = priority
        message.author = author
        message.sender = self.node_number
        msg_type = 2
        
        sock = self.getSocket(author)
        self.send_message(message,sock,msg_type=msg_type)
  
    def uponVCBCReady(self,message):
        priority = message.priority
        author = message.author
        sender = message.sender

        if author == self.node_number:
            already_has_quorum = (self.ready_state.getLen(priority) >= self.getQuorum())
            self.ready_state.add(priority,sender)

            if not already_has_quorum:
                if self.ready_state.getLen(priority) >= self.getQuorum():
                    
                    message = messages_pb2.VCBCFinal()
                    message.priority = priority
                    message.author = author
                    message.sender = self.node_number
                    msg_type = 3
                    
                    self.broadcast(message,msg_type=msg_type)
        
    
    def uponVCBCFinal(self,message):
        priority = message.priority
        author = message.author
        sender = message.sender



        print(f"Receveid VCBCFinal: {author=},{priority=}")
        print("="*50)

        if not self.aba_state.hasSentInit(author,priority,0,1):
            message = messages_pb2.ABAInit()
            message.author = author
            message.priority = priority
            message.vote = 1
            message.round = 0
            message.sender = self.node_number
            msg_type = 4
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentInit(author,priority,0,1)

    def uponABAInit(self,message):

        author = message.author
        priority = message.priority
        round = message.round
        vote = message.vote
        sender = message.sender

        if self.aba_state.currentPriority(author) > priority:
            return
        if self.aba_state.currentRound(author,priority) > round:
            return

        self.aba_state.addInit(author,priority,round,vote,sender)

        if self.aba_state.hasSentAux(author,priority,round,vote):
            return
        
        if self.aba_state.lenInit(author,priority,round,vote) >= self.getQuorum():
            message = messages_pb2.ABAAux()
            message.author = author
            message.priority = priority
            message.vote = vote
            message.round = round
            message.sender = self.node_number
            msg_type = 5
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentAux(author,priority,round,vote)

        if self.aba_state.hasSentInit(author,priority,round,vote):
            return
        
        if self.aba_state.lenInit(author,priority,round,vote) >= self.getPartialQuorum():
            message = messages_pb2.ABAInit()
            message.author = author
            message.priority = priority
            message.vote = vote
            message.round = round
            message.sender = self.node_number
            msg_type = 4
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentInit(author,priority,round,vote)

    
    def uponABAAux(self,message):

        author = message.author
        priority = message.priority
        round = message.round
        vote = message.vote
        sender = message.sender

        if self.aba_state.currentPriority(author) > priority:
            return
        if self.aba_state.currentRound(author,priority) > round:
            return

        self.aba_state.addAux(author,priority,round,vote,sender)
        
        if self.aba_state.hasSentConf(author,priority,round):
            return
        
        if self.aba_state.lenAux(author,priority,round) >= self.getQuorum():
            message = messages_pb2.ABAConf()
            message.author = author
            message.priority = priority
            message.votes.extend(self.aba_state.getConfValues(author,priority,round))
            message.round = round
            message.sender = self.node_number
            msg_type = 6
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentConf(author,priority,round)

    def uponABAConf(self,message):

        author = message.author
        priority = message.priority
        round = message.round
        votes = list(message.votes)
        sender = message.sender

        if self.aba_state.currentPriority(author) > priority:
            return
        if self.aba_state.currentRound(author,priority) > round:
            return
        
        self.aba_state.addConf(author,priority,round,votes,sender)
        
        print(f"will test quorum, {self.aba_state.lenConf(author,priority,round)=},{self.getQuorum()=}")
        if self.aba_state.lenConf(author,priority,round) >= self.getQuorum():

            coin = Coin(author,priority,round)
            print(f"{coin=}")

            conf_values = self.aba_state.getConfValues(author,priority,round)
            
            init_vote = coin if len(conf_values) == 2 else conf_values[0]
            if not self.aba_state.hasSentInit(author,priority,round+1,init_vote):

                message = messages_pb2.ABAInit()
                message.author = author
                message.priority = priority
                message.vote = init_vote
                message.round = round+1
                message.sender = self.node_number
                msg_type = 4
                
                self.broadcast(message,msg_type=msg_type)
                self.aba_state.setSentInit(author,priority,round+1,init_vote)
                self.aba_state.setRound(author,priority,round+1)
            
            if len(conf_values) == 1 and conf_values[0] == coin:

                if not self.aba_state.hasSentFinish(author,priority,coin):

                    message = messages_pb2.ABAFinish()
                    message.author = author
                    message.priority = priority
                    message.vote = coin
                    message.sender = self.node_number
                    msg_type = 7
                    
                    self.broadcast(message,msg_type=msg_type)
                    self.aba_state.setSentFinish(author,priority,coin)

    def uponABAFinish(self,message):

        author = message.author
        priority = message.priority
        vote = message.vote
        sender = message.sender

        if self.aba_state.currentPriority(author) > priority:
            return
        

        self.aba_state.addFinish(author,priority,vote,sender)

        if self.aba_state.lenFinish(author,priority,vote) >= self.getPartialQuorum():

            if not self.aba_state.hasSentFinish(author,priority,vote):

                message = messages_pb2.ABAFinish()
                message.author = author
                message.priority = priority
                message.vote = vote
                message.sender = self.node_number
                msg_type = 7
                
                self.broadcast(message,msg_type=msg_type)
                self.aba_state.setSentFinish(author,priority,vote)
        
        if self.aba_state.lenFinish(author,priority,vote) >= self.getQuorum() and not self.aba_state.isDecided(author,priority):
            self.aba_state.setDecided(author,priority,vote)
            self.aba_state.setPriority(author,priority+1)
            print(f"Decided ABA for: {author=},{priority=}")
            if author == self.node_number:
                print(f"{Timer.endTimer(f'{priority}')} microseconds ({priority=})")
                vcbc_thread = threading.Thread(target=self.startNewVCBC, args=(priority+1,))
                vcbc_thread.start()
    
    def startNewVCBC(self,priority):

        if self.priority == priority:
            time.sleep(3)
            Timer.startTimer(f'{self.priority}')
            self.StartVCBC(f'data_from_priority{self.priority}')

            


import sys

if __name__ == '__main__':
    # serverT = threading.Thread(target=server, args=())
    # serverT.start()
    # clientT = threading.Thread(target=client, args=())
    # clientT.start()
    print(sys.argv)
    node1 = node(int(sys.argv[1]),int(sys.argv[2]))
    if int(sys.argv[1]) == 1:
        node1.createPeriodicalVCBC()
    # node1_thread = threading.Thread(target=node, args=(1))
    # node1_thread.start()
    # node2_thread = threading.Thread(target=node, args=(2))
    # node2_thread.start()