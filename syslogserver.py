import socketserver, re, sqlite3
SYSLOG_HOST="0.0.0.0"
SYSLOG_PORT=514
RAW_LOG_FILE="syslog.log"
DB_FILE="logs.db"
pattern = re.compile(
    r"<(\d+)>"  # Matches the priority field (e.g., <30>)
    r"(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})"  # Matches timestamp (e.g., Jan 30 00:17:36)
    r" (\S+)"  # Matches hostname (e.g., vyos)
    r" (\S+)\[(\d+)\]:"  # Matches process name and PID (e.g., systemd[1])
    r" ([\w.-]+@[\w.-]+\.\w+)"  # Matches the email-like field (e.g., serial-getty@ttyS0.service)
    r": (.+)"  # Matches the message
)


class SyslogServer(socketserver.BaseRequestHandler):
    def handle(self):
        data=bytes.decode(self.request[0].strip())
        print(f"{data}")
        # with open(RAW_LOG_FILE, "a") as raw_log_file:
        #     raw_log_file.write(f"{data}\n")
        match = pattern.match(data)
        if match:
            # Extracting parameters
            priority = match.group(1)  
            severity = int(priority) % 8 
            facility = int(priority) // 8  
            
            timestamp = match.group(2)
            hostname = match.group(3)
            process = match.group(4)
            pid = int(match.group(5))
            email = match.group(6)  # email like field (rfc mail)
            message = match.group(7)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Insert OP (Research on how to avoid sql injection here)
            cursor.execute("""
                INSERT INTO logs (priority, severity, facility, timestamp, hostname, process, pid, mail, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (priority, severity, facility, timestamp, hostname, process, pid, email, message))

            
            conn.commit()
            conn.close()

if __name__ == "__main__":
    with socketserver.UDPServer((SYSLOG_HOST, SYSLOG_PORT), SyslogServer) as server:
        print(f"Syslog server running on {SYSLOG_HOST}:{SYSLOG_PORT}...")
        try:
            server.serve_forever() 
             
        except KeyboardInterrupt:
            print("\nSyslog server shutting down...")
            server.shutdown()
            server.server_close()

    
