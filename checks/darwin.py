import os
import subprocess


def get_disk_encryption_macos():
    try:
        output = subprocess.check_output(["fdesetup", "status"], text=True)
        if "FileVault is On" in output:
            return {"enabled": True, "method": "FileVault"}
        elif "FileVault is Off" in output:
            return {"enabled": False, "method": "FileVault"}
        else:
            return {"enabled": False, "method": "Unknown"}
    except Exception:
        return {"enabled": False, "method": "Unknown"}


def get_macos_update_status():
    """
    Returns macOS version and whether updates are pending.
    """
    try:
        version = subprocess.check_output(
            ["sw_vers", "-productVersion"], text=True
        ).strip()
        
        result = subprocess.run(
            ["softwareupdate", "-l"],
            text=True,
            capture_output=True
        )

        updates = []
        if "No new software available." in result.stdout:
            updates_available = False
        else:
            updates_available = True
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith("*") and not line.startswith("Finding") and not line.startswith("Software Update found"):
                    updates.append(line)

        return {
            "osDescription": f"macOS {version}",
            "updatesAvailable": updates_available,
            "details": updates
        }
    except Exception as e:
        return {
            "osDescription": "macOS",
            "updatesAvailable": None,
            "error": str(e)
        }


KNOWN_MAC_AVS = {
    "ClamAV": ["/usr/local/bin/clamscan", "/usr/local/sbin/clamd"],
    "Norton": ["/Applications/Norton 360.app"],
    "Avast": ["/Applications/Avast.app"],
    "Sophos": ["/Applications/Sophos Endpoint.app"],
    "McAfee": ["/Library/McAfee/"],
    "Malwarebytes": ["/Applications/Malwarebytes.app"]
}

def get_macos_antivirus_status():
    av_status = []

    for av_name, paths in KNOWN_MAC_AVS.items():
        installed = any(os.path.exists(p) for p in paths)
        running = False

        if installed:
            try:
                ps_output = subprocess.check_output(["ps", "-A"], text=True)
                if any(av_name.lower() in line.lower() for line in ps_output.splitlines()):
                    running = True
            except Exception:
                pass

        av_status.append({
            "name": av_name,
            "installed": installed,
            "running": running
        })


    detected = [av for av in av_status if av["installed"]]
    if not detected:
        return [{"name": "None", "installed": False, "running": False}]

    return detected


def get_macos_inactivity_timeout():
    """
    Checks inactivity timeout on macOS using pmset.
    Returns display sleep timeout in seconds and compliance (<= 600).
    """
    timeout = None
    error = None

    try:
        result = subprocess.check_output(["pmset", "-g", "custom"], text=True)
        for line in result.splitlines():
            if "displaysleep" in line:
                try:
                    # Format: ' displaysleep        10'
                    timeout_minutes = int(line.split()[-1])
                    timeout = timeout_minutes * 60
                    break
                except Exception:
                    pass
    except FileNotFoundError:
        error = "pmset not found"
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
            "error": error or "Unable to detect"
        }
