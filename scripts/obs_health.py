#!/usr/bin/env python3
"""OBS machine health check. Prints JSON; every check is {status: ok|warn|fail|info, ...}.

Usage: python3 health.py [--record-path PATH] [--min-free-gb N]

Read-only. Needs no websocket; if OBS is running with websocket enabled, run
`obs_ws.py status` as well for live state.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def sh(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def config_dir():
    for c in [os.environ.get("OBS_CONFIG_PATH", ""), "~/.config/obs-studio",
              "~/.var/app/com.obsproject.Studio/config/obs-studio",
              "~/snap/obs-studio/current/.config/obs-studio"]:
        if c and (Path(c).expanduser() / "global.ini").exists():
            return Path(c).expanduser()
    return None


def ver_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def check_install():
    out = {}
    pkg = sh("dpkg-query", "-W", "-f=${Version}", "obs-studio")
    flat = sh("flatpak", "info", "com.obsproject.Studio")
    if pkg:
        out = {"type": "native", "installed": pkg}
        policy = sh("apt-cache", "policy", "obs-studio")
        cand = re.search(r"Candidate:\s*(\S+)", policy)
        out["apt_candidate"] = cand.group(1) if cand else None
        # A version table with only /var/lib/dpkg/status means no repo in the *local apt lists*
        # ships it. Usually the lists are just stale (seen 2026-11-13: after `apt update` the
        # distro archive listed it again), so report the list age instead of a verdict.
        lists = [f for f in glob.glob("/var/lib/apt/lists/*_Packages*")]
        age_days = round((time.time() - max(map(os.path.getmtime, lists))) / 86400, 1) if lists else None
        out["apt_lists_age_days"] = age_days
        out["apt_source"] = "ppa:obsproject" if "obsproject" in policy else (
            "not in apt lists (run `sudo apt update`, then recheck)"
            if re.search(r"\*\*\*.*\n\s+100 /var/lib/dpkg/status\s*$", policy) else "distro archive")
    elif flat:
        m = re.search(r"Version:\s*(\S+)", flat)
        out = {"type": "flatpak", "installed": m.group(1) if m else "?"}
    elif shutil.which("obs"):
        out = {"type": "other", "installed": sh("obs", "--version")}
    else:
        return {"status": "fail", "detail": "OBS not installed"}
    try:
        req = urllib.request.Request("https://api.github.com/repos/obsproject/obs-studio/releases/latest",
                                     headers={"User-Agent": "obs-mgmt-health"})
        out["upstream_latest"] = json.load(urllib.request.urlopen(req, timeout=10))["tag_name"]
    except Exception as e:
        out["upstream_latest"] = None
        out["upstream_error"] = str(e)[:120]
    behind = out.get("upstream_latest") and ver_tuple(out["installed"]) < ver_tuple(out["upstream_latest"])
    out["status"] = "warn" if behind or "not in apt lists" in str(out.get("apt_source")) else "ok"
    return out


def check_running(cfg):
    pids = sh("pgrep", "-x", "obs").split()
    ws = {}
    f = cfg / "plugin_config/obs-websocket/config.json" if cfg else None
    if f and f.exists():
        d = json.loads(f.read_text())
        ws = {"enabled": d.get("server_enabled"), "port": d.get("server_port"), "auth": d.get("auth_required")}
    listening = bool(ws.get("port")) and f":{ws['port']} " in sh("ss", "-ltn")
    return {"status": "ok" if ws.get("enabled") else "warn", "obs_running": bool(pids),
            "websocket": ws, "websocket_listening": listening}


def check_storage(cfg, record_path, min_free):
    path = Path(record_path).expanduser() if record_path else None
    if not path and cfg:
        for ini in sorted((cfg / "basic/profiles").glob("*/basic.ini")):
            m = re.search(r"^(?:FilePath|RecFilePath)=(.+)$", ini.read_text(), re.M)
            if m:
                path = Path(m.group(1))
                break
    path = path or Path.home()  # OBS default when the profile sets no path
    target = path if path.exists() else path.parent
    free = shutil.disk_usage(target).free / 1e9
    return {"status": "ok" if path.exists() and free >= min_free else "warn",
            "record_path": str(path), "exists": path.exists(), "free_gb": round(free, 1)}


def check_devices():
    cams = sorted(glob.glob("/dev/v4l/by-id/*-video-index0"))
    mics = [l.split("\t")[1] for l in sh("pactl", "list", "short", "sources").splitlines()
            if "\t" in l and ".monitor" not in l]
    return {"status": "ok" if cams and mics else "warn", "cameras": cams, "microphones": mics,
            "default_source": sh("pactl", "get-default-source"),
            "session": os.environ.get("XDG_SESSION_TYPE"), "desktop": os.environ.get("XDG_CURRENT_DESKTOP")}


def check_encoders():
    render = glob.glob("/dev/dri/renderD*")
    vainfo = sh("vainfo") if shutil.which("vainfo") else None
    h264 = bool(vainfo and "VAProfileH264" in vainfo and "VAEntrypointEncSlice" in vainfo)
    return {"status": "ok" if h264 else "info", "render_nodes": render,
            "vaapi_h264_encode": h264 if vainfo is not None else "unknown (install vainfo)"}


# Startup noise on every Linux OBS install: no DeckLink/AJA card, no NVIDIA GPU (nvenc), missing translations,
# DroidCam probing for iOS devices without usbmuxd.
BENIGN = re.compile(r"decklink|aja|obs-nvenc|Failed to load '[\w-]+' text for module|usbmuxd|failed to log status")


def check_logs(cfg):
    logs = sorted((cfg / "logs").glob("*.txt")) if cfg else []
    if not logs:
        return {"status": "info", "detail": "no OBS logs yet"}
    text = logs[-1].read_text(errors="replace")
    lag = re.findall(r"skipped frames due to encoding lag: (\d+) \(([\d.]+)%\)", text)
    render = re.findall(r"frames missed due to rendering lag: (\d+) \(([\d.]+)%\)", text)
    errors = [l.split(": ", 1)[-1] for l in text.splitlines()
              if re.search(r"\berror\b|failed", l, re.I) and not BENIGN.search(l)]
    worst = max([float(p) for _, p in lag + render] or [0])
    return {"status": "warn" if worst > 1 or errors else "ok", "latest_log": logs[-1].name,
            "encoding_lag": lag[-3:], "rendering_lag": render[-3:], "worst_drop_pct": worst,
            "errors": sorted(set(errors))[:10]}


def check_system():
    load1, _, _ = os.getloadavg()
    mem = dict(re.findall(r"^(\w+):\s+(\d+)", Path("/proc/meminfo").read_text(), re.M))
    avail = int(mem.get("MemAvailable", 0)) / 1e6
    temps = []
    for z in glob.glob("/sys/class/thermal/thermal_zone*/temp") + glob.glob("/sys/class/hwmon/hwmon*/temp*_input"):
        try:
            temps.append(int(Path(z).read_text()) / 1000)
        except (OSError, ValueError):
            pass
    hot = temps and max(temps) > 85
    return {"status": "warn" if load1 > os.cpu_count() or avail < 2 or hot else "ok",
            "load1": round(load1, 2), "cpus": os.cpu_count(), "mem_available_gb": round(avail, 1),
            "max_temp_c": max(temps) if temps else None}


def main():
    cfg = config_dir()
    checks = {
        "install": check_install(),
        "runtime": check_running(cfg),
        "storage": check_storage(cfg, arg("--record-path", None), float(arg("--min-free-gb", 20))),
        "devices": check_devices(),
        "encoders": check_encoders(),
        "logs": check_logs(cfg),
        "system": check_system(),
    }
    rank = {"ok": 0, "info": 0, "warn": 1, "fail": 2}
    overall = max((c["status"] for c in checks.values()), key=lambda s: rank[s])
    print(json.dumps({"host": os.uname().nodename, "config_dir": str(cfg), "overall": overall,
                      "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
