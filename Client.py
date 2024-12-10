import asyncio
import json
import os
from colorama import Fore, Style
from util import check_file_size
from ConfigClass import DefaultConfig
from threading import Thread

class PeerClient:
    def __init__(self, tracker_ip, tracker_port, peer_port, files, peer_ip='127.0.0.1', peer_name="PEER"):
        self.config = DefaultConfig()
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.peer_port = peer_port
        self.tracker_reader = None
        self.tracker_writer = None
        self.files = files  # Store files that this peer has
        self.peer_ip = peer_ip
        self.file_path = self.config.client_directory()
        self.piece_size = self.config.piece_size()
        self.peer_name = peer_name
        self.lock = asyncio.Lock()
        self.read_lock = asyncio.Lock()
        self.server_thread = None

    def log(self, prompt):
        print(f'{Fore.BLUE}[{self.peer_name}]{Style.RESET_ALL} {prompt}')

    def log_message(self, message):
        print(f'{Fore.BLUE}[{self.peer_name} - MESSAGE]{Style.RESET_ALL} {message}')

    async def connect_to_tracker(self):
        """Connect to the tracker and register the peer."""
        self.tracker_reader, self.tracker_writer = await asyncio.open_connection(self.tracker_ip, self.tracker_port)
        file_sizes = [check_file_size(f"{self.file_path}/{file_path}") for file_path in self.files]
        register_message = {"type": "REGISTER", "port": self.peer_port, "files": self.files, "peer_ip": self.peer_ip, 'file_sizes': file_sizes}
        await self.send_to_tracker(register_message)
        self.log(f"Registered with tracker at {self.tracker_ip}:{self.tracker_port}")
        self.server_thread = Thread(target=asyncio.run, args=(self.start_server(),))
        self.server_thread.start()
        self.log(f"Finishing setup server")

    async def start_server(self):
        # Start listening for incoming peer connections
        server = await asyncio.start_server(self.listen_for_peers, '0.0.0.0', self.peer_port)
        self.log(f"{self.peer_name} listening on port {self.peer_port}")
        async with server:
            await server.serve_forever()

    async def send_to_tracker(self, message):
        """Send a JSON message to the tracker."""
        async with self.lock:
            str_message = json.dumps(message)
            self.log_message(f"Sending message to tracker: {str_message}")
            self.tracker_writer.write(f'{str_message}\n'.encode('utf-8'))
        await self.tracker_writer.drain()
        self.log(f"Sending done")

    async def read_from_tracker(self):
        """Read a JSON message from the tracker."""
        async with self.lock:
            self.log('Waiting...')
            response = await self.tracker_reader.readline()
            self.log_message(f"Received message from tracker: {response.decode('utf-8')}")
            response_data = json.loads(response.decode('utf-8'))
            return response_data

    async def get_n_idle_peers(self, n):
        """Request N idle peers from the tracker."""
        request_message = {"type": "GET_N_IDLE_PEERS", "count": n, 'peer_ip': self.peer_ip, 'peer_port': self.peer_port}
        await self.send_to_tracker(request_message)

        # Wait for tracker response
        
        response_data = await self.read_from_tracker()

        if response_data['type'] == 'PEERS_AVAILABLE':
            return response_data['peers']
        else:
            return []
        
    async def get_n_file_idle_peers(self, file_names):
        """Request N idle peers from the tracker."""
        request_message = {"type": "GET_N_FILE_IDLE_PEERS", "file_names": file_names, 'peer_ip': self.peer_ip, 'peer_port': self.peer_port}
        await self.send_to_tracker(request_message)
        self.log(f"Send to tracker: {request_message}")
        response_data = await self.read_from_tracker()

        if response_data['type'] == 'PEERS_AVAILABLE':
            return response_data | {'file_sizes': response_data['file_sizes']}
        else:
            return {}

    async def request_file(self, peer_ip, file_name, file_size):
        """Request a specific file from another peer."""
        request_message = {"type": "REQUEST_FILE", "peer_ip": peer_ip, "file_name": file_name}
        await self.send_to_tracker(request_message)
        # Wait for tracker response
        response_data = await self.read_from_tracker()

        if response_data['type'] == "PEER_CONTACT":
            peer_ip = response_data['peer_ip']
            peer_port = response_data['peer_port']
            self.log(f"Contacting peer {peer_ip}:{peer_port} for file transfer.")
            await self.connect_to_peer(peer_ip, peer_port, file_name, file_size)
        elif response_data['type'] == "PEER_BUSY":
            self.log(f"Requested peer {peer_ip} is busy or does not have the requested file.")

    async def connect_to_peer(self, peer_ip, peer_port, file_name, file_size):
        """Connect to another peer to request a specific file."""
        reader, writer = await asyncio.open_connection(peer_ip, peer_port)
        writer.write(f"REQUEST_FILE:{file_name}".encode('utf-8'))
        await writer.drain()
        
        file_data = b''
        for _ in range(file_size // self.piece_size + 1):
            file_data += await reader.read(self.config.buffer_size())
        try:
            true_file_data = file_data.decode('utf-8')
        except UnicodeDecodeError:
            true_file_data = '[BINARY CONTENT]'
        self.log(f"Received {file_name} from {peer_ip}:{peer_port}: |{true_file_data}|")
        if not os.path.exists("downloaded"):
            os.makedirs("downloaded")
        with open(f"downloaded/{file_name}", 'wb') as file:
            file.write(file_data)
        await self.notify_transfer_complete(peer_ip)
        writer.close()
        await writer.wait_closed()

    async def notify_transfer_complete(self, peer_ip):
        """Notify the tracker that the file transfer is complete."""
        complete_message = {"type": "COMPLETE", "peer_ip": peer_ip}
        await self.send_to_tracker(complete_message)

    async def listen_for_peers(self, reader, writer):
        """Listen for incoming peer connections to handle file requests."""
        request = await reader.read(self.config.buffer_size())
        if request.decode('utf-8').startswith("REQUEST_FILE:"):
            file_name = request.decode('utf-8').split(":")[1]
            if file_name in self.files:
                with open(f"{self.file_path}/{file_name}", 'rb') as file:
                    file_data = file.read()  # Placeholder for actual file data
                for i in range(len(file_data) // self.piece_size + 1):
                    writer.write(file_data[self.piece_size * i: self.piece_size * (i + 1)])
                    await writer.drain()
            else:
                self.log(f"{file_name} not found on this peer.")
        writer.close()
        await writer.wait_closed()
