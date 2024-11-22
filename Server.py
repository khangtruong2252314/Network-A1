import asyncio
import json
from Action import *
from colorama import Fore, Style
from collections import defaultdict
from ConfigClass import DefaultConfig

class PeerTracker:
    def __init__(self, port=1108):
        self.config = DefaultConfig()
        self.port = port
        self.peers = {}
        self.lock = asyncio.Lock()
        self.hash_table = defaultdict(list)
        self.torrent_directory = self.config.meta_file_path()
        self.meta = {}
        self.hash_dict = {}
        self.meta_path = self.config.meta_path()
        self.hash_file_path = self.config.hash_file_path()

    def log_message(self, message):
        print(f"{Fore.GREEN}[MESSAGE-TRACKER]{Style.RESET_ALL} {message}")

    def log_error(self, message):
        print(f'{Fore.RED}[ERROR-TRACKER]{Style.RESET_ALL} {message}')

    async def start(self):
        server = await asyncio.start_server(self.handle_peer, '0.0.0.0', self.port)
        print(f"{Fore.GREEN}[TRACKER]{Style.RESET_ALL} Tracker started on port {self.port}")
        async with server:
            await server.serve_forever()

    async def handle_peer(self, reader, writer):
        """Handles communication with peers for registration and file requests."""
        peer_ip, peer_port = writer.get_extra_info('peername')
        print(f"{Fore.GREEN}[TRACKER]{Style.RESET_ALL} Connected with peer: {peer_ip}:{peer_port}")
        while True:
            self.log('Waiting...')
            try:
                data = await reader.readuntil(b'\n')
                if not data:
                    continue 
                raw_message = data.decode('utf-8')
                if raw_message:
                    self.log_message(f"Received message from peer: {raw_message}")
                    message = json.loads(raw_message)
                    action_type = message['type']
                    # Instantiate the appropriate action class based on the action type
                    action_classes = {
                        'REGISTER': Register,
                        'GET_N_IDLE_PEERS': GetNIdlePeers,
                        'REQUEST_FILE': RequestFile,
                        'COMPLETE': CompleteTransfer,                
                        'GET_N_FILE_IDLE_PEERS': GetNFileIdlePeers,
                    }

                    if action_type in action_classes:
                        action = action_classes[action_type](self, message, writer, peer_ip, peer_port)
                        await action.execute()
                    else:
                        self.log(f"Unknown action type: {action_type}")
            except asyncio.IncompleteReadError:
                self.log_error(f"Peer {peer_ip}:{peer_port} disconnected.")
                break

        print(f"{Fore.GREEN}[TRACKER]{Style.RESET_ALL} Connection with peer {peer_ip} closed.")
        writer.close()
        await writer.wait_closed()

    def log(self, message):
        """Log a message to the console."""
        print(f"{Fore.GREEN}[TRACKER]{Style.RESET_ALL} {message}")
