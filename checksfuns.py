from checks.linux.linux import (
    get_disk_encryption_linux,
    get_linux_packageManager_updates_status,
    get_linux_antivirus_status,
    get_linux_inactivity_timeout
)
from checks.darwin import (
    get_disk_encryption_macos,
    get_macos_update_status,
    get_macos_antivirus_status,
    get_macos_inactivity_timeout
)
from checks.windows import (
    get_disk_encryption_windows,
    check_windows_updates_pending,
    get_windows_antivirus_status,
    get_windows_inactivity_timeout
)


def get_disk_encryption_status(os_type:str):
    if os_type == "windows":
        return get_disk_encryption_windows()
    elif os_type == "darwin":
        return get_disk_encryption_macos()
    elif os_type == "linux":
        return get_disk_encryption_linux()
    else:
        return {"enabled": False, "method": "Unsupported"}


def get_os_updates_status(os_type: str):
    if os_type == "windows":
        return check_windows_updates_pending()
    elif os_type == "darwin":
        return get_macos_update_status()
    elif os_type == "linux":
        return get_linux_packageManager_updates_status()
    else:
        return {
            "osDescription": "Unknown",
            "updatesAvailable": False,
            "method": "Unsupported"
        }

def get_antivirus_status(os_type: str):
    if os_type == "windows":
        return get_windows_antivirus_status()
    elif os_type == "darwin":
        return get_macos_antivirus_status()
    elif os_type == "linux":
        return get_linux_antivirus_status()
    else:
        return {
            "antivirus": None,
            "installed": False,
            "running": False,
            "details": "Unsupported OS"
        }


def get_inactivity_timeout(os_type: str):
    if os_type == "windows":
        return get_windows_inactivity_timeout()
    elif os_type == "darwin":
        return get_macos_inactivity_timeout()
    elif os_type == "linux":
        return get_linux_inactivity_timeout()
    else:
        return {
            "timeoutSeconds": None,
            "error": "Unsupported OS"
        }