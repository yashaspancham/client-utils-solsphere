import json
import requests
import platform
import socket
from datetime import datetime, timezone
from checksfuns import (
    get_disk_encryption_status,
    get_os_updates_status,
    get_antivirus_status,
    get_inactivity_timeout,
)
from sendReport import send_report


def collect_basic_state():
    os = platform.system().lower()
    dist_encryption_status = get_disk_encryption_status(os_type=os)
    os_updates_info = get_os_updates_status(os_type=os)
    anti_virus_info = get_antivirus_status(os_type=os)
    inactivity_timeout_info = get_inactivity_timeout(os_type=os)
    state = {
        "os_type": os,  # 'linux', 'darwin', 'windows'
        "machine_id": socket.gethostname(),
        "checks": {
            "lastCheckedAt": datetime.now(timezone.utc).isoformat(),
            "diskEncryption": dist_encryption_status,
            "osUpdates": os_updates_info,
            "anitivirus": anti_virus_info,
            "inactivityTimeout": inactivity_timeout_info,
        },
    }
    return state


if __name__ == "__main__":
    state = collect_basic_state()
    print(json.dumps(state, indent=6))
    send_report(state)
