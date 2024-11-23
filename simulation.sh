py start_tracker.py

py start_client.py --tracker_ip 127.0.0.1 --tracker_port 1108 --peer_name PEER_A --port 1109 --file "fileA1.txt" "fileA2.txt" "fileA3.txt"
py start_client.py --tracker_ip 127.0.0.1 --tracker_port 1108 --peer_name PEER_B --port 1110 --file "fileB1.txt" "fileB2.txt"
py start_client.py --tracker_ip 127.0.0.1 --tracker_port 1108 --peer_name PEER_C --port 1111 --request_file "fileA1.txt" "fileB1.txt" 
py start_client.py --tracker_ip 127.0.0.1 --tracker_port 1108 --peer_name PEER_D --port 1112 --file "fileD1.txt" "fileD2.txt" 