import subprocess
import time
import os
import sys

def start_servers():
    print("Starting consolidated backend and frontend servers...")
    
    # Get the directory where this script is located (backend/)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.abspath(os.path.join(backend_dir, "..", "frontend"))
    
    # Start unified Flask backend (port 5000)
    p1 = subprocess.Popen([sys.executable, "main.py"], cwd=backend_dir)
    
    # Start Python simple HTTP server for frontend (port 3000)
    p2 = subprocess.Popen([sys.executable, "-m", "http.server", "3000"], cwd=frontend_dir)
    
    print("\nServers are running:")
    print("- Unified Backend API : http://localhost:5000")
    print("- Frontend Web Portal : http://localhost:3000/login.html")
    print("- Admin Feedback Panel: http://localhost:3000/feedback_admin.html")
    print("\nPress Ctrl+C to stop all servers.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        p1.terminate()
        p2.terminate()
        p1.wait()
        p2.wait()
        print("Servers stopped.")

if __name__ == '__main__':
    start_servers()
