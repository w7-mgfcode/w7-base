import subprocess
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9101
W7_BIN = "/usr/local/bin/w7"

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            
            try:
                # Run w7 doctor --json
                # W7_ROOT must be correctly set for the script to find zones
                result = subprocess.run([W7_BIN, "--json", "doctor"], capture_output=True, text=True)
                data = json.loads(result.stdout)
                
                metrics = []
                metrics.append(f"# HELP w7_error_count Total number of errors found by doctor")
                metrics.append(f"# TYPE w7_error_count gauge")
                metrics.append(f"w7_error_count {data.get('error_count', 0)}")
                
                metrics.append(f"# HELP w7_warning_count Total number of warnings found by doctor")
                metrics.append(f"# TYPE w7_warning_count gauge")
                metrics.append(f"w7_warning_count {data.get('warning_count', 0)}")
                
                status_val = 1 if data.get('status') == 'healthy' else 0
                metrics.append(f"# HELP w7_healthy 1 if the system is healthy, 0 otherwise")
                metrics.append(f"# TYPE w7_healthy gauge")
                metrics.append(f"w7_healthy {status_val}")
                
                # Add w7 stat metrics (container counts per zone)
                try:
                    stat_result = subprocess.run([W7_BIN, "stat"], capture_output=True, text=True)
                    import re
                    # Remove ANSI escape sequences
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    clean_stdout = ansi_escape.sub('', stat_result.stdout)
                    
                    zone_counts = {"ops": 0, "dev": 0, "prod": 0, "lab": 0}
                    for line in clean_stdout.splitlines():
                        if "|" in line and "@" in line:
                            parts = [p.strip() for p in line.split("|")]
                            if len(parts) >= 3:
                                zone = parts[0].replace("@", "")
                                status = parts[2]
                                if "Up" in status:
                                    count = 1
                                    match = re.search(r'\((\d+)\)', status)
                                    if match:
                                        count = int(match.group(1))
                                    if zone in zone_counts:
                                        zone_counts[zone] += count
                    
                    metrics.append(f"# HELP w7_containers_up Total number of containers running per zone")
                    metrics.append(f"# TYPE w7_containers_up gauge")
                    for zone, count in zone_counts.items():
                        metrics.append(f'w7_containers_up{{zone="{zone}"}} {count}')
                except:
                    pass

                # Dynamic policy violation metrics
                # errors often look like "@prod/stack violated policy.sh"
                for err in data.get('errors', []):
                    if "violated" in err:
                        parts = err.split()
                        stack_path = parts[0] # e.g. @prod/whoami
                        policy = parts[-1] # e.g. prod-privileged.sh
                        zone, stack = stack_path.split('/')
                        metrics.append(f'w7_policy_violation{{zone="{zone}",stack="{stack}",policy="{policy}"}} 1')

                self.wfile.write("\n".join(metrics).encode())
                self.wfile.write(b"\n")
            except Exception as e:
                self.wfile.write(f"# Error gathering metrics: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"Starting W7 Exporter on port {PORT}...")
    httpd = HTTPServer(('', PORT), MetricsHandler)
    httpd.serve_forever()
