import subprocess
import sys

def check_docker_running():
    try:
        # Check if docker daemon is reachable
        result = subprocess.run(
            ["docker", "info"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        if result.returncode != 0:
            print("\n❌ ERROR: Docker Desktop is not running!")
            print("Please start Docker Desktop and ensure the daemon is reachable before continuing.")
            print("If you are running on Windows/Mac, ensure the Docker Desktop application is open.")
            print(f"\nDetails:\n{result.stderr.decode('utf-8')}")
            sys.exit(1)
            
        print("✅ Docker daemon is running and reachable.")
    except FileNotFoundError:
        print("\n❌ ERROR: 'docker' command not found.")
        print("Please install Docker and ensure it is added to your system PATH.")
        sys.exit(1)

if __name__ == "__main__":
    check_docker_running()
