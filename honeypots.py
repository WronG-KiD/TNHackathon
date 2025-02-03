import socket
import threading
import paramiko
from pymongo import MongoClient
from flask import Flask, request

# 🔹 MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["honeypots_db"]
attacks_collection = db["attack_logs"]

# 🔹 Function to Store Attacker Data
def log_attack(source_ip, attack_type, details):
    """Logs attack data in MongoDB."""
    attacks_collection.insert_one({
        "source_ip": source_ip,
        "attack_type": attack_type,
        "details": details
    })
    print(f"⚠️ Attack Logged: {attack_type} from {source_ip}")

# 🔹 Simulated SSH Honeypot (Fake SSH Server)
def ssh_honeypot():
    """Simulates a fake SSH server to log brute-force attempts."""
    host_key = paramiko.RSAKey.generate(1024)
    server = paramiko.Transport(("0.0.0.0", 2222))  # SSH Honeypot Port
    server.add_server_key(host_key)

    class FakeSSH(paramiko.ServerInterface):
        def check_auth_password(self, username, password):
            log_attack("Unknown", "SSH Brute Force", f"Username: {username}, Password: {password}")
            return paramiko.AUTH_FAILED  # Always fail authentication

    server.start_server(server=FakeSSH())
    print("🛑 SSH Honeypot Running on Port 2222")

# 🔹 Simulated HTTP Honeypot (Fake Web Server)
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def web_honeypot():
    """Logs unauthorized HTTP requests."""
    attacker_ip = request.remote_addr
    log_attack(attacker_ip, "HTTP Request", f"Method: {request.method}, Path: {request.path}")
    return "404 Not Found", 404

def run_http_honeypot():
    """Starts Flask HTTP Honeypot."""
    print("🌐 HTTP Honeypot Running on Port 8080")
    app.run(host="0.0.0.0", port=8080)

# 🔹 Fake Open Port Scanner (Trap for Attackers)
def port_scan_honeypot():
    """Listens on multiple ports and logs connection attempts."""
    ports = [21, 23, 445, 3306, 3389]  # Common attack ports (FTP, Telnet, SMB, MySQL, RDP)
    sockets = []

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        sockets.append(sock)

    print("🕵️‍♂️ Port Scanner Honeypot Active")
    while True:
        for sock in sockets:
            conn, addr = sock.accept()
            log_attack(addr[0], "Port Scan Attempt", f"Port: {sock.getsockname()[1]}")
            conn.close()

# 🔹 Run Honeypots in Threads
if __name__ == "__main__":
    threading.Thread(target=ssh_honeypot, daemon=True).start()
    threading.Thread(target=run_http_honeypot, daemon=True).start()
    threading.Thread(target=port_scan_honeypot, daemon=True).start()

    print("🚀 Honeypots Deployed. Waiting for Attacker Activity...")
    while True:
        pass  # Keeps script running
