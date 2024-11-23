from run import run_peer
import asyncio
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', type=int, default=1109)
    parser.add_argument('--files', type=str, nargs='+', default=['fileA1.txt', 'fileA2.txt', 'fileA3.txt'])
    parser.add_argument('--peer_name', type=str, default='PEER')
    parser.add_argument('--request_files', type=str, nargs='+', default=[])
    parser.add_argument('--tracker_ip', type=str, default='127.0.0.1')
    parser.add_argument('--tracker_port', type=int, default=1108)
    args = parser.parse_args()
    tracker_port = args.port
    peer_port = args.port
    files = args.files
    request_files = args.request_files
    tracker_ip = args.tracker_ip
    tracker_port = args.tracker_port
    peer_name = args.peer_name

    asyncio.run(run_peer(
        peer_ip='127.0.0.1',
        tracker_ip=tracker_ip, 
        tracker_port=tracker_port, 
        peer_port=peer_port, 
        files=files, 
        peer_name=peer_name, 
        request_files=request_files))