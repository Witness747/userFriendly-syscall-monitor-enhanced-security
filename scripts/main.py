from bcc import BPF
import time
import os

# SILENCE KERNEL WARNINGS: Keeps the terminal clean for your recording
os.environ["BCC_LINUX_HELPER_QUIET"] = "1"

# 1. Load the C code from your file
b = BPF(src_file="src/monitor.c")
execve_name = b.get_syscall_fnname("execve")
b.attach_kprobe(event=execve_name, fn_name="syscall__execve")

# Color codes for the "User-Friendly" look
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

def print_event(cpu, data, size):
    event = b["events"].event(data)
    proc_name = event.comm.decode()
    full_path = event.fname.decode()

    # 1. NOISE FILTER (Ignore background tasks)
    noise_list = ["cpuUsage.sh", "venv", "sh", "code", "node", "plugins"]
    if any(n in proc_name for n in noise_list):
        return

    # 2. ANALYSIS LOGIC
    status = f"{GREEN}✓ Process Started{END}" # Default
    
    if "ping" in proc_name or "google" in full_path:
        status = f"{YELLOW}⚠ ALERT: Network Activity!{END}"
    elif "sudo" in proc_name or "root" in full_path:
        status = f"{RED}✖ CRITICAL: Administrative Access!{END}"

    # 3. FINAL OUTPUT
    print("%-18.9f %-16s %-6d %s" % (time.time(), proc_name, event.pid, status))

# 3. Main Loop
b["events"].open_perf_buffer(print_event)
print("Monitor ACTIVE. (Press Ctrl+C to stop and sync to GitHub)")

log_file = open("scripts/output.txt", "a")

# Inside print_event, add:
log_entry = f"{time.time()} | {proc_name} | {status}\n"
log_file.write(log_entry)
log_file.flush() # Forces it to write to disk immediately

while 1:
    try:
        b.perf_buffer_poll(timeout=100)
    except KeyboardInterrupt:
        print("\n[STOPPED] Cleaning up and exiting...") # Graceful exit for recording
        exit()