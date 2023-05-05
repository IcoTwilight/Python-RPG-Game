import socket
import threading
import json

class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = []
		self.type = "server"

	def handle_client(self, client_socket, client_address):
		# receive data from the client and send a response
		while True:
			try:
				data = client_socket.recv(1024).decode()
				if not data:
					break
				print(f'Received data from client {client_address}: {data}')
				self.on_message(client_socket, client_address, data)
			except:
				print(f'Client {client_address} disconnected unexpectedly.')
				break

		# close the connection and remove the client from the list
		print(f'Client {client_address} disconnected.')
		self.on_message(client_socket, client_address, json.dumps({"type": "disconnect"}))
		client_socket.close()
		self.clients.remove((client_socket, client_address))

	def on_message(self, client_socket = None, client_address = None, data = None):
		# handle incoming messages from clients
		print(f'Handling message from client {client_address}: {data}')

	def start(self):
		# bind the socket to the host and port
		self.server_socket.bind((self.host, self.port))

		# set the server to listen for incoming connections
		self.server_socket.listen(5)
		print(f'Server listening on {self.host}:{self.port}')

		# start a new thread to handle incoming client connections
		threading.Thread(target=self.accept_clients).start()

	def accept_clients(self):
		# wait for clients to connect and handle each one in a separate thread
		while True:
			client_socket, client_address = self.server_socket.accept()
			print(f'Client {client_address} connected.')

			# add the client to the list
			self.clients.append((client_socket, client_address))

			# start a new thread to handle the client
			client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
			client_thread.start()
			self.on_message(client_socket, client_address, json.dumps({"type": "connect"}))
	
	def send_message(self, message):
		# send a message to all connected clients
		for client_socket, client_address in self.clients:
			client_socket.sendall(message.encode())
	
	def send_message_to_client(self, client_address, message):
		# send a message to a specific client
		for client_socket, address in self.clients:
			if address == client_address:
				client_socket.sendall(message.encode())
				break

	def stop(self):
		# close all client connections
		for client_socket, client_address in self.clients:
			client_socket.close()

		# close the server socket
		self.server_socket.close()

class Client:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.type = "client"

	def connect(self):
		# connect to the server
		self.client_socket.connect((self.host, self.port))
		print(f'Connected to server {self.host}:{self.port}')

		# start a new thread to receive messages from the server
		receive_thread = threading.Thread(target=self.receive_messages)
		receive_thread.start()

	def send_message(self, message):
		# send a message to the server
		if self.client_socket.fileno() != -1: # check if the socket is still open
			self.client_socket.sendall(message.encode())
		else:
			print('Socket is not open')

	def receive_messages(self):
		# receive messages from the server and call the on_message() method
		while self.client_socket.fileno() != -1: # check if the socket is still open
			try:
				message = self.client_socket.recv(1024).decode()
				if not message:
					break
				self.on_message(data = message)
			except socket.error:
				break

		# close the connection
		self.client_socket.close()

	def on_message(self, data):
		# handle incoming messages from the server
		print(f'Received message from server: {data}')

	def disconnect(self):
		# close the connection
		self.client_socket.close()
		print('Disconnected from server.')

if __name__ == "__main__":
	# create a server and start it
	server = Server('localhost', 5000)
	server.start()

	# create 10 clients and connect them to the server
	clients = []
	for i in range(10):
		client = Client('localhost', 5000)
		client.connect()
		clients.append(client)
	
	# send a message to all clients
	server.send_message('Hello from the server!')

	# have all clients send a message to the server
	for client in clients:
		client.send_message('Hello from the client!')