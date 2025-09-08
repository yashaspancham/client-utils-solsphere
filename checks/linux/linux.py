import shutil
from checks.linux.osUpdates import detect_package_manager, get_linux_update_status

def get_disk_encryption_linux():
    import subprocess
    try:
        lsblk = subprocess.check_output(
            ["lsblk", "-o", "NAME,TYPE,MOUNTPOINT"], text=True
        )
        if "crypt" in lsblk:
            return {"enabled": True, "method": "LUKS/dm-crypt"}
        try:
            with open("/etc/crypttab") as f:
                if f.read().strip():
                    return {"enabled": True, "method": "LUKS"}
        except FileNotFoundError:
            pass
        return {"enabled": False, "method": "None"}
    except Exception:
        return {"enabled": False, "method": "Unknown"}


def get_linux_packageManager_updates_status():
    package_manager = detect_package_manager()
    if not package_manager:
        return {
            "osDescription": "Unknown",
            "packageManager": None,
            "updatesAvailable": False,
            "method": "Unsupported"
        }
    try:
        updates_info = get_linux_update_status(pm=package_manager)
        return updates_info
    except Exception as e:
        return {
            "osDescription": "Unknown",
            "packageManager": package_manager,
            "updatesAvailable": None,
            "error": str(e)
        }


KNOWN_AVS = {
    "ClamAV": ["clamscan", "clamd"],
    "Sophos": ["/opt/sophos-av/bin/savdstatus"],
    "ESET": ["/opt/eset/esets/sbin/esets_daemon"],
    "Kaspersky": ["/opt/kaspersky/kesl/bin/kesl"],
    "AVG": ["/usr/lib/avg/av/bin/avgscan"]
}

def get_linux_antivirus_status():
    installed_avs = []

    for av_name, binaries in KNOWN_AVS.items():
        installed = False
        for binary in binaries:
            if shutil.which(binary) or shutil.which(binary.split("/")[-1]):
                installed = True
                break

        if installed:
            installed_avs.append({"name": av_name, "installed": True})

    if not installed_avs:
        return [{"name": "None", "installed": False}]

    return installed_avs


import os
import subprocess

def get_linux_inactivity_timeout():
    timeout = None
    error = None


    try:
        result = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.session", "idle-delay"],
            text=True
        ).strip()
        timeout = int(result.split()[-1])
    except FileNotFoundError:
        error = "gsettings not found (not GNOME)"
    except Exception as e:
        error = str(e)

    if timeout is None:
        try:

            result = subprocess.check_output(
                ["qdbus", "org.freedesktop.ScreenSaver", "/ScreenSaver", "GetSessionIdleTime"],
                text=True
            ).strip()
            timeout = int(result)
        except FileNotFoundError:

            config_path = os.path.expanduser("~/.config/kscreenlockerrc")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        for line in f:
                            if "Timeout=" in line:
                                timeout = int(line.split("=")[-1].strip())
                                break
                except Exception as e:
                    error = f"KDE config read error: {e}"
        except Exception as e:
            error = str(e)

    if timeout is not None:
        return {
            "timeoutSeconds": timeout,
            "compliant": timeout <= 600
        }
    else:
        return {
            "timeoutSeconds": None,
            "compliant": False,
            "error": error or "Unsupported desktop environment"
        }
