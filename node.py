
import messages_pb2
import socket
import threading
import time
import signal
from vcbc_state import VCBCState,ReadyState
from coin import Coin
from aba_state import ABAState
from timer import Timer
from logger import Logger

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

    def __init__(self,node_number,number_of_nodes,output_file = None, verbose = 2):

        # NODE CONFIGURATION
        self.node_number = node_number

        self.number_of_operators = number_of_nodes
        self.f = (number_of_nodes-1)//3

        self.vcbc_state = VCBCState(list(range(1,self.number_of_operators+1)))
        self.aba_state = ABAState(list(range(1,self.number_of_operators+1)))

        self.ready_state = ReadyState()
        
        self.priority = 0

        self.verbose = verbose
        
        self.output_file = f"out{self.node_number}.log"
        if output_file != None:
            self.output_file = output_file

        self.logger = Logger(self.output_file,verbose_mode=self.verbose)
    
        self.lock = threading.Lock()
        


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

    # def log(self,text):
    #     if self.verbose == 0:
    #         return
    #     if self.verbose == 2:
    #         if "Decided" in text or "microseconds" in text:
    #             print(text)
    #     else:
    #         print(text)

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
        self.logger.debug('Caught interrupt signal, closing connections...')
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
            self.logger.debug("Waiting for a connection...")
            conn, addr = self.sock.accept()

            # if the connection is already in the dictionary of connections, close it
            if addr in connections:
                self.logger.debug("Connection from %s:%d already exists, closing new connection" % addr)
                conn.close()
            else:
                # handle the connection in a new thread
                handle_thread = threading.Thread(target=self.handle_connection, args=(conn, addr, connections))
                handle_thread.start()
    
    # HANDLE CONNECTION FROM OTHER NODE
    # KEEPS CONNECTION PERSISTENT
    # GETS MESSAGE AND CALLS PROCESS_MSG
    def handle_connection(self,conn, addr, connections):
        self.logger.debug("Accepted connection from %s:%d" % addr)

        # add the connection to the dictionary of connections
        connections[addr] = conn

        try:
            while True:
                # receive a message from the client
                message = self.receive_message(conn)
                self.process_message(message)
        except Exception as e:
            self.logger.warning("Error handling connection from %s:%d: %s %s" % (addr[0], addr[1], str(e),str(e.__traceback__)))

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

        # acquire the lock
        self.lock.acquire()

        if isinstance(message,messages_pb2.VCBCSend):
            # new_logger = self.logger.newLogger("VCBCSend")
            self.uponVCBCSend(message,self.logger)
        elif isinstance(message,messages_pb2.VCBCReady):
            # new_logger = self.logger.newLogger("VCBCReady")
            self.uponVCBCReady(message,self.logger)
        elif isinstance(message,messages_pb2.VCBCFinal):
            # new_logger = self.logger.newLogger("VCBCFinal")
            self.uponVCBCFinal(message,self.logger)
        elif isinstance(message,messages_pb2.ABAInit):
            # new_logger = self.logger.newLogger("ABAInit")
            self.uponABAInit(message,self.logger)
        elif isinstance(message,messages_pb2.ABAAux):
            # new_logger = self.logger.newLogger("ABAAux")
            self.uponABAAux(message,self.logger)
        elif isinstance(message,messages_pb2.ABAConf):
            # new_logger = self.logger.newLogger("ABAConf")
            self.uponABAConf(message,self.logger)
        elif isinstance(message,messages_pb2.ABAFinish):
            # new_logger = self.logger.newLogger("ABAFinish")
            self.uponABAFinish(message,self.logger)
        

        # release the lock
        self.lock.release()

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

    def createPeriodicalVCBC(self,num_instances):
        step = 1
        while step <= num_instances+1:
            step += 1
            
            time.sleep(3)
            Timer.startTimer(f'{self.priority}')
            self.StartVCBC(f'data_from_priority{self.priority}')
            time.sleep(self.number_of_operators * 0.07)
            
        

            
                
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
    
    def uponVCBCSend(self,message,logger):
        data = message.data
        priority = message.priority
        author = message.author

        tag = logger.getTag()

        logger.debug(f"UponVCBCSend {tag}: {message}")

        if not self.vcbc_state.has(author,priority):
            self.vcbc_state.add(author,data,priority)
        
        message = messages_pb2.VCBCReady()
        message.priority = priority
        message.author = author
        message.sender = self.node_number
        msg_type = 2
        
        sock = self.getSocket(author)
        self.send_message(message,sock,msg_type=msg_type)
  
    def uponVCBCReady(self,message, logger):
        priority = message.priority
        author = message.author
        sender = message.sender

        tag = logger.getTag()


        logger.debug(f"UponVCBCReady {tag}: {message}")

        if author == self.node_number:
            already_has_quorum = (self.ready_state.getLen(priority) >= self.getQuorum())
            self.ready_state.add(priority,sender)
            
            logger.debug(f"UponVCBCReady {tag}: readys receiveds for {priority=}: {self.ready_state.getLen(priority)}. Quorum:{self.getQuorum()}. {already_has_quorum=} ")


            if not already_has_quorum:
                if self.ready_state.getLen(priority) >= self.getQuorum():
                    
                    message = messages_pb2.VCBCFinal()
                    message.priority = priority
                    message.author = author
                    message.sender = self.node_number
                    msg_type = 3
                    
                    self.broadcast(message,msg_type=msg_type)
        
    
    def uponVCBCFinal(self,message,logger):
        priority = message.priority
        author = message.author
        sender = message.sender
        
        tag = logger.getTag()


        logger.debug(f"UponVCBCFinal {tag}: {message}")

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

    def uponABAInit(self,message,logger):

        author = message.author
        priority = message.priority
        round = message.round
        vote = message.vote
        sender = message.sender

        tag = logger.getTag()

        logger.debug(f"UponABAInit {tag}: {message}")

        if self.aba_state.currentPriority(author) > priority:
            logger.debug(f"UponABAInit {tag}: old message. Current priority for {author=} is bigger than {priority=}")
            return
        if self.aba_state.currentRound(author,priority) > round:
            logger.debug(f"UponABAInit {tag}: old message. Current round for {author=} and {priority=} is bigger than {round=}")
            return

        self.aba_state.addInit(author,priority,round,vote,sender)

        if self.aba_state.hasSentAux(author,priority,round,vote):
            logger.debug(f"UponABAAux {tag}: return. Has sent aux for {author=},{priority=},{round=},{vote=}")
            return
        

        logger.debug(f"UponABAInit {tag}: current len for init {author=},{priority=},{round=},{vote=}: {self.aba_state.lenInit(author,priority,round,vote)}. Quorum={self.getQuorum()}. Partial Quorum={self.getPartialQuorum()}")
        
        if self.aba_state.lenInit(author,priority,round,vote) >= self.getQuorum():
            
            logger.debug(f"UponABAInit {tag}: Sending ABAAux {author=},{priority=},{vote=},{round=},{self.node_number=}. Has sent?{self.aba_state.hasSentAux(author,priority,round,vote)}")

            message = messages_pb2.ABAAux()
            message.author = author
            message.priority = priority
            message.vote = vote
            message.round = round
            message.sender = self.node_number
            msg_type = 5
            
            self.aba_state.setSentAux(author,priority,round,vote)
            self.broadcast(message,msg_type=msg_type)

        if self.aba_state.hasSentInit(author,priority,round,vote):
            return

        
        if self.aba_state.lenInit(author,priority,round,vote) >= self.getPartialQuorum():
                        
            logger.debug(f"UponABAInit {tag}: Sending ABAInit {author=},{priority=},{vote=},{round=},{self.node_number=}. Has sent?{self.aba_state.hasSentInit(author,priority,round,vote)}")

            message = messages_pb2.ABAInit()
            message.author = author
            message.priority = priority
            message.vote = vote
            message.round = round
            message.sender = self.node_number
            msg_type = 4
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentInit(author,priority,round,vote)

    
    def uponABAAux(self,message,logger):

        author = message.author
        priority = message.priority
        round = message.round
        vote = message.vote
        sender = message.sender        
        
        tag = logger.getTag()

        logger.debug(f"UponABAAux {tag}: {message}")

        if self.aba_state.currentPriority(author) > priority:
            logger.debug(f"UponABAAux {tag}: old message. Current priority for {author=} is bigger than {priority=}")
            return
        if self.aba_state.currentRound(author,priority) > round:
            logger.debug(f"UponABAAux {tag}: old message. Current round for {author=} and {priority=} is bigger than {round=}")
            return

        self.aba_state.addAux(author,priority,round,vote,sender)
        
        if self.aba_state.hasSentConf(author,priority,round):
            logger.debug(f"UponABAAux {tag}: return. Has sent conf for {author=},{priority=},{round=}")
            return

        logger.debug(f"UponABAAux {tag}: current len for aux {author=},{priority=},{round=}: {self.aba_state.lenAux(author,priority,round)}. Quorum={self.getQuorum()}")

        
        if self.aba_state.lenAux(author,priority,round) >= self.getQuorum():

            logger.debug(f"UponABAAux {tag}: sending ABAConf with {author=},{priority=},{self.aba_state.getConfValues(author,priority,round)=},{round=}")

            message = messages_pb2.ABAConf()
            message.author = author
            message.priority = priority
            message.votes.extend(self.aba_state.getConfValues(author,priority,round))
            message.round = round
            message.sender = self.node_number
            msg_type = 6
            
            self.broadcast(message,msg_type=msg_type)
            self.aba_state.setSentConf(author,priority,round)

    def uponABAConf(self,message,logger):

        author = message.author
        priority = message.priority
        round = message.round
        votes = list(message.votes)
        sender = message.sender

        tag = logger.getTag()

        logger.debug(f"UponABAConf {tag}: {message}")

        if self.aba_state.currentPriority(author) > priority:
            logger.debug(f"UponABAConf {tag}: old message. Current priority for {author=} is bigger than {priority=}")
            return
        if self.aba_state.currentRound(author,priority) > round:
            logger.debug(f"UponABAConf {tag}: old message. Current round for {author=} and {priority=} is bigger than {round=}")
            return
        
        self.aba_state.addConf(author,priority,round,votes,sender)

        logger.debug(f"UponABAConf {tag}: current len for conf {author=},{priority=},{round=}: {self.aba_state.lenConf(author,priority,round)}. Quorum={self.getQuorum()}")
        
        if self.aba_state.lenConf(author,priority,round) >= self.getQuorum():

            coin = Coin(author,priority,round)
            logger.debug(f"{coin=}")

            conf_values = self.aba_state.getConfValues(author,priority,round)
            
            init_vote = coin if len(conf_values) == 2 else conf_values[0]
            if not self.aba_state.hasSentInit(author,priority,round+1,init_vote):

                logger.debug(f"UponABAConf {tag}: sending ABAInit {author=},{priority=},round={round+1},{init_vote=}")
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
                                    
                    logger.debug(f"UponABAConf {tag}: sending ABAFinish {author=},{priority=},{coin=}")


                    message = messages_pb2.ABAFinish()
                    message.author = author
                    message.priority = priority
                    message.vote = coin
                    message.sender = self.node_number
                    msg_type = 7
                    
                    self.broadcast(message,msg_type=msg_type)
                    self.aba_state.setSentFinish(author,priority,coin)

    def uponABAFinish(self,message,logger):

        author = message.author
        priority = message.priority
        vote = message.vote
        sender = message.sender

        tag = logger.getTag()



        logger.debug(f"UponABAFinish {tag}: {message}")

        if self.aba_state.currentPriority(author) > priority:
            logger.debug(f"UponABAFinish {tag}: old message. Current priority for {author=} is bigger than {priority=}")
            return
        

        self.aba_state.addFinish(author,priority,vote,sender)

        logger.debug(f"UponABAFinish {tag}: current len for finish {author=},{priority=},{vote=}: {self.aba_state.lenFinish(author,priority,vote)}. Partial Quorum={self.getPartialQuorum()}")

        if self.aba_state.lenFinish(author,priority,vote) >= self.getPartialQuorum():

            if not self.aba_state.hasSentFinish(author,priority,vote):
                    
                logger.debug(f"UponABAFinish {tag}: sending ABAFinish {author=},{priority=},{vote=}")

                message = messages_pb2.ABAFinish()
                message.author = author
                message.priority = priority
                message.vote = vote
                message.sender = self.node_number
                msg_type = 7
                
                self.broadcast(message,msg_type=msg_type)
                self.aba_state.setSentFinish(author,priority,vote)
        
        logger.debug(f"UponABAFinish {tag}: current len for finish {author=},{priority=},{vote=}: {self.aba_state.lenFinish(author,priority,vote)}. Quorum={self.getQuorum()}. State for aba: {self.aba_state.isDecided(author,priority)}")


        if self.aba_state.lenFinish(author,priority,vote) >= self.getQuorum() and not self.aba_state.isDecided(author,priority):
            self.aba_state.setDecided(author,priority,vote)
            self.aba_state.setPriority(author,priority+1)
            logger.debug(f"UponABAFinish {tag}: Decided ABA for {author=},{priority=} : {vote=}")
            if author == self.node_number:
                logger.info(f"UponABAFinish {tag}: {Timer.endTimer(f'{priority}')} microseconds ({priority=})")
                # vcbc_thread = threading.Thread(target=self.startNewVCBC, args=(priority+1,))
                # vcbc_thread.start()
    
    def startNewVCBC(self,priority):

        if self.priority == priority:
            time.sleep(1)
            Timer.startTimer(f'{self.priority}')
            self.StartVCBC(f'data_from_priority{self.priority}')

            


import sys
import argparse


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='command', required=True)

# 'launch' sub-command
launch_parser = subparsers.add_parser('launch')
launch_parser.add_argument('-id', '--node_id', type=int, help='node id')
launch_parser.add_argument('-n', '--node_count', type=int, help='node count')
launch_parser.add_argument('-v', '--verbose', type=int, required = False, help='verbose style (0: silence mode, 1: full verbose, 2: log only metrics)')
launch_parser.add_argument('-o', '--output_file', type=str, required = False, help='output file name')

if __name__ == "__main__":

    args = parser.parse_args()

    if args.command == 'launch':
        id = args.node_id
        node_count = args.node_count
        verbose = 2
        if args.verbose != None:
            verbose = args.verbose
        
        output_filename = None
        if args.output_file != None:
            output_filename = None

        node_instance = node(id,node_count,output_file = output_filename,verbose = verbose)
        if id == 1:
            node_instance.createPeriodicalVCBC(40)
