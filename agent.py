import os
import sys
import json
import platform
import requests
from datetime import datetime, timezone
import socket
import time
from checksfuns import (
    get_disk_encryption_status,
    get_os_updates_status,
    get_antivirus_status,
    get_inactivity_timeout,
)
from sendReport import send_report


def collect_system_checks():
    os = platform.system().lower()
    dist_encryption_status = get_disk_encryption_status(os_type=os)
    os_updates_info = get_os_updates_status(os_type=os)
    anti_virus_info = get_antivirus_status(os_type=os)
    inactivity_timeout_info = get_inactivity_timeout(os_type=os)
    state = {
        "os_type": os,  # 'linux', 'darwin', 'windows'
        "machine_id": socket.gethostname(),
        "lastCheckedAt": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "diskEncryption": dist_encryption_status,
            "osUpdates": os_updates_info,
            "anitivirus": anti_virus_info,
            "inactivityTimeout": inactivity_timeout_info,
        },
    }
    return state


CHECK_INTERVAL = 60 * (1 / 8)  # 60*x = x minutes(in seconds)
last_state = None


def run_daemon():
    global last_state
    while True:
        report = collect_system_checks()
        print(json.dumps(report, indent=6))
        checks_str = json.dumps(report["checks"], sort_keys=True)
        # send_report(report) #forTesting
        if checks_str != last_state:
            print("Change detected, sending report...")
            if send_report(report):
                last_state = checks_str
            else:
                print("Failed to send report, will retry later.")
        else:
            print("No changes, skipping send.")

        time.sleep(CHECK_INTERVAL)


def daemonize_linux_macOS():
    if os.fork():
        sys.exit()

    os.setsid()
    if os.fork():
        sys.exit()

    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as devnull:
        os.dup2(devnull.fileno(), sys.stdin.fileno())
    with open("/dev/null", "a+") as devnull:
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())


def run_windows_daemon():
    global last_state
    while True:
        report = collect_system_checks("windows")
        checks_str = json.dumps(report["checks"], sort_keys=True)

        if checks_str != last_state:
            print("Change detected, sending report...")
            send_report(report)
            last_state = checks_str
        else:
            print("No changes, skipping send.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    os_type = platform.system().lower()
    if os_type == "linux" or os_type == "darwin":
        daemonize_linux_macOS()
        run_daemon()
    elif os_type == "windows":
        run_windows_daemon()
    else:
        print(f"Unsupported OS: {os_type}")
