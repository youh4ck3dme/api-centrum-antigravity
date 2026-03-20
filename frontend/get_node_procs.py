
import subprocess
import json

def get_node_processes():
    try:
        # Get ProcessId and CommandLine using PowerShell
        ps_cmd = 'Get-CimInstance Win32_Process -Filter "Name = \'node.exe\'" | Select-Object ProcessId, CommandLine | ConvertTo-Json'
        result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return []
            
        if not result.stdout.strip():
            print("No node.exe processes found.")
            return []
            
        processes = json.loads(result.stdout)
        # Handle single process case
        if isinstance(processes, dict):
            processes = [processes]
            
        return processes
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    procs = get_node_processes()
    print("NODE PROCESSES:")
    for p in procs:
        print(f"PID: {p.get('ProcessId')}")
        print(f"Cmd: {p.get('CommandLine')}")
        print("-" * 20)
