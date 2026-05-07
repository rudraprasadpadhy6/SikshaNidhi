import subprocess
import time
import os

def start_servers():
    print("Starting all backend servers...")
    
    # Get the directory where this script is located (backend/)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Start each server with the backend directory as the current working directory
    p1 = subprocess.Popen(["python", "Scholarserver.py"], cwd=backend_dir)
    p2 = subprocess.Popen(["python", "Capitalserver.py"], cwd=backend_dir)
    p3 = subprocess.Popen(["python", "pixabot7.py"], cwd=backend_dir)
    p4 = subprocess.Popen(["python", "feedbackserver.py"], cwd=backend_dir)
    
    print("\nServers are running:")
    print("- Scholarserver (port 5000)")
    print("- Capitalserver (port 8000)")
    print("- PixaBot (port 8001)")
    print("- FeedbackServer (port 8002)  -- Admin: http://localhost:8002/admin")
    print("\nPress Ctrl+C to stop all servers.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        p1.terminate()
        p2.terminate()
        p3.terminate()
        p4.terminate()
        p1.wait()
        p2.wait()
        p3.wait()
        p4.wait()
        print("Servers stopped.")

if __name__ == '__main__':
    start_servers()
