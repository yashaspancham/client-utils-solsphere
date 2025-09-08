import json
import platform
import socket
from datetime import datetime,timezone
from checksfuns import (
    get_disk_encryption_status,
    get_os_updates_status,
    get_antivirus_status,
    get_inactivity_timeout
)

def collect_basic_state():
    os=platform.system().lower()
    dist_encryption_status=get_disk_encryption_status(os_type=os)
    os_updates_info=get_os_updates_status(os_type=os)
    anti_virus_info=get_antivirus_status(os_type=os)
    inactivity_timeout_info=get_inactivity_timeout(os_type=os)
    state = {
        "machineId": "demo-machine-id",
        "os": os,   # 'linux', 'darwin', 'windows'
        "hostname": socket.gethostname(),
        "lastCheckedAt": datetime.now(timezone.utc).isoformat(),
        "diskEncryption": dist_encryption_status,
        "osUpdates": os_updates_info,
        "anitivirus": anti_virus_info,
        "inactivityTimeout": inactivity_timeout_info
    }
    return state

if __name__ == "__main__":
    state = collect_basic_state()
    print(json.dumps(state, indent=6))