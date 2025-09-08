import subprocess

def get_disk_encryption_windows():
    try:
        output = subprocess.check_output(
            ["manage-bde", "-status", "C:"], text=True, stderr=subprocess.DEVNULL
        )
        if "Percentage Encrypted: 100%" in output:
            return {"enabled": True, "method": "BitLocker"}
        elif "Percentage Encrypted" in output:
            return {"enabled": True, "method": "BitLocker (partial)"}
        else:
            return {"enabled": False, "method": "None"}
    except Exception:
        return {"enabled": False, "method": "Unknown"}



def check_windows_updates_pending():
    try:
        cmd = [
            "powershell",
            "-Command",
            "(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search('IsInstalled=0').Updates.Count"
        ]
        output = subprocess.check_output(cmd, text=True).strip()
        pending_count = int(output)
        return {
            "osDescription": f"Windows {platform.release()} (build {platform.version()})",
            "updatesAvailable": pending_count > 0,
            "pendingUpdates": pending_count
        }
    except Exception as e:
        return {
            "osDescription": f"Windows {platform.release()}",
            "updatesAvailable": None,
            "error": str(e)
        }



def get_windows_antivirus_status():
    import wmi
    av_status = []
    try:
        w = wmi.WMI(namespace="root\\SecurityCenter2")
        for av in w.AntiVirusProduct():
            av_status.append({
                "name": av.displayName,
                "path": av.pathToSignedProductExe,
                "up_to_date": av.productUptoDate,
                "enabled": av.productState in (397568, 397584, 266240, 266256)  # heuristic
            })
    except Exception as e:
        av_status.append({
            "name": "Error",
            "installed": False,
            "running": False,
            "error": str(e)
        })
    
    if not av_status:
        av_status.append({
            "name": "None",
            "installed": False,
            "running": False
        })

    return av_status



def get_windows_inactivity_timeout():
    import winreg
    """
    Checks Windows inactivity timeout (sleep or screen lock).
    Returns timeout in seconds and compliance (<= 600).
    """
    timeout = None
    error = None

    # --- 1. Try registry for screensaver lock timeout ---
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Control Panel\Desktop")
        value, _ = winreg.QueryValueEx(key, "ScreenSaveTimeOut")
        timeout = int(value)
    except FileNotFoundError:
        error = "Registry key not found"
    except Exception as e:
        error = f"Registry error: {e}"

    # --- 2. Fallback: powercfg (sleep timeout) ---
    if timeout is None:
        try:
            result = subprocess.check_output(
                ["powercfg", "/query"],
                text=True, stderr=subprocess.DEVNULL
            )
            # Look for AC/DC sleep timeout
            for line in result.splitlines():
                if "AC Power Setting Index" in line or "DC Power Setting Index" in line:
                    val = line.split()[-1]
                    try:
                        timeout = int(val, 16)  # hex string
                        break
                    except Exception:
                        pass
        except Exception as e:
            error = f"powercfg error: {e}"

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
