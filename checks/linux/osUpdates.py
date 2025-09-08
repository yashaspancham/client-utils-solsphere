import subprocess
import shutil

def detect_package_manager():
    managers = ["apt", "dnf", "yum", "pacman", "zypper"]

    found = []
    for manager in managers:
        if shutil.which(manager):
            found.append(manager)

    if found:
        return found[0]
    else:
        return None

 
def check_apt_updates():
    try:
        desc = subprocess.check_output(["lsb_release", "-d"], text=True).strip()
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            text=True, capture_output=True
        )
        lines = result.stdout.strip().split("\n")
        updates = lines[1:] if len(lines) > 1 else []
        return {
            "osDescription": desc,
            "packageManager": "apt",
            "updatesAvailable": len(updates) > 0,
            "details": updates
        }
    except Exception as e:
        return {"packageManager": "apt", "error": str(e)}


def check_pacman_updates():
    try:
        desc = subprocess.check_output(["lsb_release", "-d"], text=True).strip()
        result = subprocess.run(
            ["checkupdates"],
            text=True, capture_output=True
        )
        updates = result.stdout.strip().split("\n") if result.stdout else []
        return {
            "osDescription": desc,
            "packageManager": "pacman",
            "updatesAvailable": len(updates) > 0,
            "details": updates
        }
    except Exception as e:
        return {"packageManager": "pacman", "error": str(e)}


def check_dnf_updates():
    try:
        desc = "Unknown Linux"
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        desc = line.split("=")[1].strip().strip('"')
                        break
        except Exception:
            pass

        result = subprocess.run(
            ["dnf", "check-update"],
            text=True, capture_output=True
        )

        updates = []
        if result.returncode == 100:  # 100 = updates available
            updates = result.stdout.strip().splitlines()

        return {
            "osDescription": desc,
            "packageManager": "dnf",
            "updatesAvailable": len(updates) > 0,
            "details": updates
        }

    except Exception as e:
        return {
            "packageManager": "dnf",
            "osDescription": "Unknown",
            "updatesAvailable": None,
            "error": str(e)
        }


def check_yum_updates():
    try:
        try:
            desc = subprocess.check_output(["cat", "/etc/redhat-release"], text=True).strip()
        except Exception:
            desc = "RedHat/CentOS (release info not found)"

        result = subprocess.run(
            ["yum", "check-update"],
            text=True,
            capture_output=True
        )

        # Yum exits with:
        #   100 → updates available
        #   0   → system up-to-date
        #   1   → error
        updates = []
        if result.returncode == 100:
            updates = [line for line in result.stdout.splitlines() if line.strip()]
            return {
                "osDescription": desc,
                "packageManager": "yum",
                "updatesAvailable": True,
                "details": updates
            }
        elif result.returncode == 0:
            return {
                "osDescription": desc,
                "packageManager": "yum",
                "updatesAvailable": False,
                "details": []
            }
        else:
            return {
                "osDescription": desc,
                "packageManager": "yum",
                "updatesAvailable": None,
                "error": "yum check-update failed"
            }
    except Exception as e:
        return {
            "packageManager": "yum",
            "updatesAvailable": None,
            "error": str(e)
        }


def check_zypper_updates():
    try:
        try:
            with open("/etc/os-release") as f:
                lines = f.readlines()
            desc = next((line.split("=")[1].strip().strip('"')
                         for line in lines if line.startswith("PRETTY_NAME=")), "openSUSE/SLE")
        except Exception:
            desc = "openSUSE/SLE (release info not found)"

        result = subprocess.run(
            ["zypper", "lu"],
            text=True,
            capture_output=True
        )

        updates = []
        if result.returncode == 100: 
            updates = [line for line in result.stdout.splitlines() if line.strip()]
            return {
                "osDescription": desc,
                "packageManager": "zypper",
                "updatesAvailable": True,
                "details": updates
            }
        elif result.returncode == 0: 
            return {
                "osDescription": desc,
                "packageManager": "zypper",
                "updatesAvailable": False,
                "details": []
            }
        else: 
            return {
                "osDescription": desc,
                "packageManager": "zypper",
                "updatesAvailable": None,
                "error": "zypper lu failed"
            }
    except Exception as e:
        return {
            "packageManager": "zypper",
            "updatesAvailable": None,
            "error": str(e)
        }

def get_linux_update_status(pm: str = None):
    if not pm:
        pm = detect_package_manager()

    if pm == "apt":
        return check_apt_updates()
    elif pm == "pacman":
        return check_pacman_updates()
    elif pm == "dnf":
        return check_dnf_updates()
    elif pm == "yum":
        return check_yum_updates()
    elif pm == "zypper":
        return check_zypper_updates()
    else:
        return {
            "osDescription": "Unknown",
            "packageManager": pm,
            "updatesAvailable": None,
            "method": "Unsupported"
        }
