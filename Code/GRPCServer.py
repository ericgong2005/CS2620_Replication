import time
from concurrent import futures
import sqlite3
import atexit
import signal
import sys
import os
import shutil
import subprocess

import grpc
import chat_pb2
import chat_pb2_grpc
from Constants import HEARTBEAT_INTERVAL, DATABASE_DIRECTORY, PASSWORD_DATABASE_SCHEMA, MESSAGES_DATABASE_SCHEMA

class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self, address, leader_stub, process_list, password_database_path, message_database_path):
        self.online_username = []
        self.process_list = process_list
        self.address = address
        self.leader_stub = leader_stub
        self.follower_stubs = {}

        if self.leader_stub != None:
            try:
                response = self.leader_stub.GetDatabases(chat_pb2.GetDatabasesRequest(origin=self.address))
                if response.status == chat_pb2.Status.SUCCESS:
                    self.process_list = response.process_list
                    self.online_username = response.online_username
                    new_subdir = f"Database_{address}"
                    output_dir = os.path.join("Databases", new_subdir)
                    os.makedirs(output_dir, exist_ok=True)
                    password_database_path = os.path.join(output_dir, "passwords.db")
                    message_database_path = os.path.join(output_dir, "messages.db")
                    with open(password_database_path, "wb") as f:
                        f.write(response.password_database)
                    with open(message_database_path, "wb") as f:
                        f.write(response.message_database)
            except Exception as e:
                print(f"{self.address} Encountered {e} upon setup, terminating")
                sys.exit(1)

        self.password_database_path = password_database_path
        self.message_database_path = message_database_path

        self.open()

        # Handle kills and interupts by closing
        atexit.register(self.close)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler) 
    
    def open(self):
        self.passwords = sqlite3.connect(self.password_database_path, check_same_thread=False)
        self.passwords_cursor = self.passwords.cursor()
        self.passwords_cursor.execute(f"CREATE TABLE IF NOT EXISTS {PASSWORD_DATABASE_SCHEMA}")
        self.passwords.commit()

        self.messages = sqlite3.connect(self.message_database_path, check_same_thread=False)
        self.messages_cursor = self.messages.cursor()
        self.messages_cursor.execute(f"CREATE TABLE IF NOT EXISTS {MESSAGES_DATABASE_SCHEMA}")
        self.messages.commit()

    def close(self):
        self.passwords.close()
        self.messages.close()

    def _signal_handler(self, signum, frame):
        self.close()
        sys.exit(0) 
    
    def SerializeDatabase(self):
        self.close()

        with open(self.password_database_path, "rb") as password_database_file:
            serialized_password_database = password_database_file.read()
        with open(self.message_database_path, "rb") as message_database_file:
            serialized_message_database = message_database_file.read()
        
        self.open()
        return (serialized_password_database, serialized_message_database)
        
    def PushChanges(self, database=False):
        print(f"{self.address} Pushing Changes to {self.process_list[1:]}")
        if self.leader_stub != None: # Error, should not be pushing changes as follower
            print("Inappropriate Change pushing")
            sys.exit(1)

        stub_dict = {}
        for follower in self.process_list[1:]:
            if follower not in self.follower_stubs:
                try:
                    channel = grpc.insecure_channel(follower)
                    temp_stub = chat_pb2_grpc.ChatServiceStub(channel)
                    grpc.channel_ready_future(channel).result(timeout=1)
                    self.follower_stubs[follower] = temp_stub
                    print(f"\tFollower {follower} found")
                except (grpc._channel._InactiveRpcError, grpc.FutureTimeoutError):
                    self.process_list.remove(follower)
                    print(f"\tFollower {follower} lost")
        
        print(f"\tFollowers {self.process_list[1:]} reached")

        if database:
            serialized_password_database, serialized_message_database = self.SerializeDatabase()

        success = True
        for follower in self.process_list[1:]:
            try:
                self.follower_stubs[follower].PushState(chat_pb2.PushStateRequest(
                    online_username = self.online_username,
                    process_list = self.process_list))
                if database:
                    self.follower_stubs[follower].PushDatabase(chat_pb2.PushDatabaseRequest(
                        password_database = serialized_password_database,
                        message_database = serialized_message_database))
            except (grpc._channel._InactiveRpcError, grpc.RpcError):
                self.process_list.remove(follower)
                del self.follower_stubs[follower]
                success = False
        
        print(f"\tFinished pushing to {self.process_list[1:]}")

        return success

    '''
    gRPC Functions
    '''

    # User Account Management
    
    def CheckUsername(self, request, context):
        print(f"Checking Username given {request}")
        if not request.username:
            return chat_pb2.CheckUsernameResponse(status=chat_pb2.Status.ERROR)
        self.passwords_cursor.execute("SELECT Username FROM Passwords WHERE Username = ?", (request.username,))
        result = self.passwords_cursor.fetchone()
        status = chat_pb2.Status.MATCH if result else chat_pb2.Status.NO_MATCH
        return chat_pb2.CheckUsernameResponse(status=status)

    def CheckPassword(self, request, context):
        print(f"Checking Password given {request}")
        if not request.username or not request.password:
            return chat_pb2.CheckPasswordResponse(status=chat_pb2.Status.ERROR)
        self.passwords_cursor.execute("SELECT Password FROM Passwords WHERE Username = ?", (request.username,))
        result = self.passwords_cursor.fetchone()
        print(f"Got: {result}")
        status = chat_pb2.Status.MATCH if (str(result[0]) == str(request.password)) else chat_pb2.Status.NO_MATCH
        return chat_pb2.CheckPasswordResponse(status=status)

    def CreateUser(self, request, context):
        print(f"Creating user given {request}")
        if not request.username or not request.password:
            return chat_pb2.CreateUserResponse(status=chat_pb2.Status.ERROR)
        try:
            self.passwords_cursor.execute("INSERT INTO Passwords (Username, Password) VALUES (?, ?)", (request.username, request.password))
            self.passwords.commit()
            while not self.PushChanges(True) : pass # Push changes until consistency
            return chat_pb2.CreateUserResponse(status=chat_pb2.Status.SUCCESS)
        except sqlite3.IntegrityError:
            return chat_pb2.CreateUserResponse(status=chat_pb2.Status.MATCH)

    def ConfirmLogin(self, request, context):
        print(f"Confirming Login given {request}")
        if not request.username:
            return chat_pb2.ConfirmLoginResponse(
            status=chat_pb2.Status.ERROR, 
            num_unread_msgs=0, 
            num_total_msgs=0,
            process_list=self.process_list)
        elif request.username in self.online_username:
            return chat_pb2.ConfirmLoginResponse(
            status=chat_pb2.Status.MATCH, 
            num_unread_msgs=0, 
            num_total_msgs=0,
            process_list=self.process_list)
        else:
            self.online_username.append(request.username)

            self.messages_cursor.execute(
            "SELECT COUNT(*) FROM Messages WHERE Recipient = ? AND Read = 0;", (request.username,))
            unread = self.messages_cursor.fetchone()[0]
            self.messages_cursor.execute(
                "SELECT COUNT(*) FROM Messages WHERE Recipient = ?", (request.username,))
            total = self.messages_cursor.fetchone()[0]

            while not self.PushChanges(False) : pass # Push changes until consistency
            return chat_pb2.ConfirmLoginResponse(
                status=chat_pb2.Status.SUCCESS, 
                num_unread_msgs=unread, 
                num_total_msgs=total,
                process_list=self.process_list
            )

    def ConfirmLogout(self, request, context):
        print(f"Confirming Logout given {request}")
        if request.username in self.online_username:
            self.online_username.remove(request.username)
            while not self.PushChanges(False) : pass # Push changes until consistency
        return chat_pb2.ConfirmLogoutResponse(status=chat_pb2.Status.SUCCESS)

    def GetOnlineUsers(self, request, context):
        print(f"Getting Online Users")
        return chat_pb2.GetOnlineUsersResponse(status=chat_pb2.Status.SUCCESS, users=self.online_username)

    def GetUsers(self, request, context):
        print(f"Getting Users given {request}")
        self.passwords_cursor.execute("SELECT Username FROM Passwords WHERE Username Like ?", (request.query, ))
        result = self.passwords_cursor.fetchall()
        final_result = [username[0] for username in result]
        return chat_pb2.GetUsersResponse(status=chat_pb2.Status.SUCCESS, users=final_result)
    
    # Messages

    def SendMessage(self, request, context):
        print(f"Sending Message given {request}")
        self.passwords_cursor.execute("SELECT Username FROM Passwords WHERE Username = ?", (request.message.recipient,))
        result = self.passwords_cursor.fetchall()
        if not result:
            return chat_pb2.SendMessageResponse(status=chat_pb2.Status.NO_MATCH)
        try:
            self.messages_cursor.execute(
                "INSERT INTO Messages (Sender, Recipient, Time_sent, Read, Subject, Body) VALUES (?, ?, ?, ?, ?, ?)",
                (request.message.sender, request.message.recipient, request.message.time_sent, 
                 int(request.message.read), request.message.subject, request.message.body)
            )
            request.message.id = self.messages_cursor.lastrowid
            self.messages.commit()
            print("Message Saved to Leader Database")
            while not self.PushChanges(True) : pass # Push changes until consistency
            print(f"Message Saved to All {self.process_list}")
            return chat_pb2.SendMessageResponse(status=chat_pb2.Status.SUCCESS)
        except sqlite3.IntegrityError:
            return chat_pb2.SendMessageResponse(status=chat_pb2.Status.ERROR)

    def GetMessage(self, request, context):
        print(f"Getting Message given {request}")
        if request.unread_only:
            self.messages_cursor.execute(
                "SELECT * FROM Messages WHERE Recipient = ? AND Read = 0 ORDER BY Time_sent DESC LIMIT ? OFFSET ?;",
                (request.username, request.limit, request.offset)
            )
        else:
            self.messages_cursor.execute(
                "SELECT * FROM Messages WHERE Recipient = ? ORDER BY Time_sent DESC LIMIT ? OFFSET ?;",
                (request.username, request.limit, request.offset)
            )
        result = self.messages_cursor.fetchall()
        messages = []
        for tuple in result:
            messages.append(chat_pb2.MessageObject(
            id = int(tuple[0]),
            sender = tuple[1],
            recipient = tuple[2],
            time_sent = tuple[3],
            read = bool(tuple[4]),
            subject = tuple[5],
            body = tuple[6]))
        return chat_pb2.GetMessageResponse(status=chat_pb2.Status.SUCCESS, messages=messages, process_list=self.process_list)

    def ConfirmRead(self, request, context):
        print(f"Confirming Read given {request}")
        if not request.username or not request.message_id:
            return chat_pb2.ConfirmReadResponse(status=chat_pb2.Status.ERROR)
        self.messages_cursor.execute(f"UPDATE Messages SET Read = 1 WHERE Recipient = ? AND Id = ?", (request.username, request.message_id,))
        self.messages.commit()
        while not self.PushChanges(True) : pass # Push changes until consistency
        return chat_pb2.ConfirmReadResponse(status=chat_pb2.Status.SUCCESS)

    def DeleteMessage(self, request, context):
        print(f"Deleting Message given {request}")
        if len(request.message_id) == 0:
            return chat_pb2.DeleteMessageResponse(status=chat_pb2.Status.ERROR)
        format = ','.join('?' for _ in request.message_id)
        values = []
        for id in request.message_id:
            values.append(int(id))
        self.messages_cursor.execute(f"DELETE FROM Messages WHERE Id IN ({format})", values)
        self.messages.commit()
        while not self.PushChanges(True) : pass # Push changes until consistency
        return chat_pb2.DeleteMessageResponse(status=chat_pb2.Status.SUCCESS)

    def DeleteUser(self, request, context):
        print(f"Deleting User given {request}")
        if not request.username:
            return chat_pb2.DeleteUserResponse(status=chat_pb2.Status.ERROR)
        self.messages_cursor.execute("UPDATE Messages SET Recipient = Sender, Subject = 'NOT SENT ' || Subject WHERE Recipient = ? AND Read = 0;", (request.username,))
        self.messages_cursor.execute("DELETE FROM Messages WHERE Recipient = ?", (request.username,))
        self.messages.commit()
        self.passwords_cursor.execute("DELETE FROM Passwords WHERE Username = ?", (request.username,))
        if self.passwords_cursor.rowcount == 0:
            return chat_pb2.DeleteUserResponse(status=chat_pb2.Status.ERROR)
        self.passwords.commit()
        while not self.PushChanges(True) : pass # Push changes until consistency
        return chat_pb2.DeleteUserResponse(status=chat_pb2.Status.SUCCESS)
    
    # Replication
    def GetDatabases(self, request, context):
        print(f"GetDatabase Request from {request.origin}")
        if request.origin != "Client":
            if request.origin not in self.process_list:
                self.process_list.append(request.origin)
                self.process_list.sort()
                print(f"New Process list {self.process_list}")
                if self.process_list[0] != self.address:
                    print("Rejecting invalid Follower")
                    self.process_list.remove(request.origin)
                    return chat_pb2.GetDatabasesResponse(status=chat_pb2.Status.ERROR,
                                                         password_database= None, message_database= None, 
                                                         online_username= None, process_list= None)
                print(f"Leader {self.address} manually added {request.origin}")

        serialized_password_database, serialized_message_database = self.SerializeDatabase()
        return chat_pb2.GetDatabasesResponse(status=chat_pb2.Status.SUCCESS,
                                             password_database=serialized_password_database, 
                                             message_database=serialized_message_database,
                                             online_username=self.online_username,
                                             process_list=self.process_list)
    
    def PushState(self, request, context):
        print(f"Recieved State Push")
        self.online_username = request.online_username
        self.process_list = request.process_list
        if self.address not in self.process_list:
            print("Left behind, Terminating")
            sys.exit(1)
        return chat_pb2.PushStateResponse(status=chat_pb2.Status.SUCCESS)

    def PushDatabase(self, request, context):
        print(f"Recieved Database Push")
        self.close()

        with open(self.password_database_path, "wb") as f:
            f.write(request.password_database)
        with open(self.message_database_path, "wb") as f:
            f.write(request.message_database)
        
        self.open()
        return chat_pb2.PushDatabaseResponse(status=chat_pb2.Status.SUCCESS)
    
    def Heartbeat(self, request, context):
        return chat_pb2.HeartbeatResponse(online_username=self.online_username, process_list=self.process_list)
    
    def LeaderDeath(self, request, context):
        try:
            # If you are the leader (leader_stub == None), you are alive, otherwise, ping the leader
            if self.leader_stub != None:
                self.leader_stub.Heartbeat(chat_pb2.HeartbeatRequest())
            return chat_pb2.LeaderDeathResponse(status=chat_pb2.Status.ERROR, leader_address=self.process_list[0])
        except grpc._channel._InactiveRpcError: # Leader confirmed dead, find new leader
            self.process_list = self.process_list[1:]
            self.leader_stub = None
            print(f"Finding leader from {self.process_list}")
            while self.leader_stub == None:
                if self.address == self.process_list[0]: # You are the leader
                    self.leader_stub = None
                    print("I am the New Leader")
                    self.PushChanges()
                    return chat_pb2.LeaderDeathResponse(status=chat_pb2.Status.SUCCESS, leader_address=self.address)
                try:
                    channel = grpc.insecure_channel(self.process_list[0])
                    self.leader_stub = chat_pb2_grpc.ChatServiceStub(channel)
                    # 1 second to connect to potential new leader
                    grpc.channel_ready_future(channel).result(timeout=1)
                    print(f"{self.address} connected to leader {self.process_list[0]}")
                    break
                except (grpc._channel._InactiveRpcError, grpc.FutureTimeoutError):
                    self.leader_stub = None
                    self.process_list = self.process_list[1:]
            if self.leader_stub == None:  # Could not find new leader
                print("Could not find new leader")
                sys.exit(1)
            else: # Confirm the leader
                try:
                    self.leader_stub.Heartbeat(chat_pb2.HeartbeatRequest())
                except grpc._channel._InactiveRpcError:
                    print("Could not find new leader")
                    sys.exit(1)
            return chat_pb2.LeaderDeathResponse(status=chat_pb2.Status.PENDING, leader_address=self.process_list[0])

def RenameDatabaseDirectory(current_name):
    rename = os.path.join(DATABASE_DIRECTORY, "Database_Leader")
    if current_name == rename:
        return current_name
    if os.path.exists(rename):
        shutil.rmtree(rename)
    os.rename(current_name, rename)
    return rename

def DeleteDatabaseDirectory(protected="Database_Leader"):
    instance_directories = [
        os.path.join(DATABASE_DIRECTORY, instances)
        for instances in os.listdir(DATABASE_DIRECTORY)
        if os.path.isdir(os.path.join(DATABASE_DIRECTORY, instances))
    ]
    protected = os.path.join(DATABASE_DIRECTORY, protected)
    for subdir in instance_directories:
        if subdir != protected:
            shutil.rmtree(subdir)

def MostRecentDatabase():
    instance_directories = [
        os.path.join(DATABASE_DIRECTORY, instances)
        for instances in os.listdir(DATABASE_DIRECTORY)
        if os.path.isdir(os.path.join(DATABASE_DIRECTORY, instances))
    ]
    
    if not instance_directories:
        raise Exception("No Databases present")

    most_recent_instance = max(instance_directories, key=os.path.getmtime)

    for subdir in instance_directories:
        if subdir != most_recent_instance:
            shutil.rmtree(subdir)
    
    return RenameDatabaseDirectory(most_recent_instance)

if __name__ == '__main__':
     # Confirm validity of commandline arguments
    if len(sys.argv) < 3:
        print("Usage: python server.py 'SELFHOST:SELFPORT' '# of Others' 'Other HOST:PORT'")
        sys.exit(1)
    address, other_count = sys.argv[1], int(sys.argv[2])
    if len(sys.argv) != other_count + 3:
        print("Usage: python server.py 'SELFHOST:SELFPORT' '# of Others' 'Other HOST:PORT'")
        sys.exit(1)
    others = sys.argv[3:]
    print(f"{address} has Other Processes", others)

    process_list = others + [address]
    process_list.sort()

    password_database_path = None
    message_database_path = None
    leader_stub = None

    # If smallest address, then assigned to be the leader, choose most recent database
    if address == process_list[0]:
        print(f"I {address} am the Leader")
        database_directory = MostRecentDatabase()
        password_database_path = os.path.join(database_directory, "passwords.db")
        message_database_path = os.path.join(database_directory, "messages.db")

        if not (os.path.isfile(password_database_path) and os.path.isfile(message_database_path)):
            raise Exception(f"Missing messages.db or passwords.db in {database_directory}")
    else: # Establish a connection to the leader
        while True:
            try:
                channel = grpc.insecure_channel(f"{process_list[0]}")
                leader_stub = chat_pb2_grpc.ChatServiceStub(channel)
                grpc.channel_ready_future(channel).result(timeout=1)
                print(f"{address} connected to leader {process_list[0]}")
                break 
            except grpc.FutureTimeoutError:
                time.sleep(0.1)
                print("Waiting to connect to Leader")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceServicer(address, leader_stub, process_list, password_database_path, message_database_path), server)
    port = server.add_insecure_port(address)
    server.start()
    print(f"gRPC Server started on {address}")
    try:
        channel = grpc.insecure_channel(address)
        self_stub = chat_pb2_grpc.ChatServiceStub(channel)
        grpc.channel_ready_future(channel).result(timeout=1)
        print("Stub to self established")
        if leader_stub == None:
            leader_stub = self_stub
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            try:
                response = leader_stub.Heartbeat(chat_pb2.HeartbeatRequest())
                process_list = response.process_list
            except grpc._channel._InactiveRpcError: # Leader has died!
                print("Detected Leader Death")
                if leader_stub == self_stub:
                    sys.exit(1)
                response = self_stub.LeaderDeath(chat_pb2.LeaderDeathRequest())
                if response.status == chat_pb2.Status.ERROR:
                    print("Lost connection to leader")
                    server.stop(0)
                    sys.exit(1)
                elif response.status == chat_pb2.Status.SUCCESS:
                    print("I confirm I am the new leader")
                    leader_stub = self_stub
                else:
                    try:
                        channel = grpc.insecure_channel(response.leader_address)
                        leader_stub = chat_pb2_grpc.ChatServiceStub(channel)
                        # 1 second to connect to new leader
                        grpc.channel_ready_future(channel).result(timeout=1)
                        print(f"Monitor on {address} connected to leader {response.leader_address}")
                    except grpc.FutureTimeoutError:
                        print("Failed to Connect to New Leader")
                        server.stop(0)
                        sys.exit(1)
    except KeyboardInterrupt:
        server.stop(0)