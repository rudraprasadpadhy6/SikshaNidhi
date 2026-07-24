"""
run_servers.py — SikshaNidhi Local Dev Launcher
Starts the backend API + serves the frontend at localhost.
"""
import subprocess
import time
import os
import sys

def start_servers():
    backend_dir  = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.abspath(os.path.join(backend_dir, '..', 'frontend'))

    print("=" * 55)
    print("  SikshaNidhi — Starting Local Development Servers")
    print("=" * 55)

    # Backend: Flask API (port 5000)
    p1 = subprocess.Popen([sys.executable, 'main.py'], cwd=backend_dir)

    # Frontend: Python static file server (port 3000)
    p2 = subprocess.Popen([sys.executable, '-m', 'http.server', '3000'], cwd=frontend_dir)

    print()
    print('  Backend API   : https://sikshanidhi-p3lo.onrender.com')
    print('  Frontend      : http://localhost:3000/index.html')
    print('  Admin Panel   : http://localhost:3000/feedback_admin.html')
    print('  PixaBot       : http://localhost:3000/PixaBot.html')
    print()
    print('  Press Ctrl+C to stop all servers.')
    print("=" * 55)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping servers...')
        p1.terminate()
        p2.terminate()
        p1.wait()
        p2.wait()
        print('All servers stopped.')

if __name__ == '__main__':
    start_servers()
