#!/usr/bin/env python3
"""Apply a declarative hotkey spec to OBS (and optionally KDE global shortcuts).

Usage: python3 hotkeys.py <hotkeys.json> [--dry-run]

Spec (all sections optional):
{
  "frontend": {"OBSBasic.StartRecording": [{"key": "OBS_KEY_F9", "control": true}]},
  "scenes":   {"Talking Head": [{"key": "OBS_KEY_2", "control": true, "alt": true}]},
  "global":   [{"id": "obs-toggle-record", "name": "OBS: toggle recording",
                "shortcut": "Meta+Shift+R", "args": ["trigger", "ToggleRecord"]}]
}

- frontend -> [Hotkeys] in the active profile's basic.ini
- scenes   -> per-scene OBSBasic.SelectScene in the active scene collection JSON
- global   -> KDE service shortcuts (.desktop with X-KDE-Shortcuts) that run obs_ws.py.
  Needed on Wayland, where OBS's own hotkeys only fire while OBS has focus.

OBS rewrites its config on exit, so frontend/scenes edits require OBS to be closed.
Originals are copied to <file>.bak-<timestamp> before writing.
"""
import configparser
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STABLE_DIR = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser() / "obs-mgmt"
APPS_DIR = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser() / "applications"


def config_dir():
    for c in [os.environ.get("OBS_CONFIG_PATH", ""), "~/.config/obs-studio",
              "~/.var/app/com.obsproject.Studio/config/obs-studio",
              "~/snap/obs-studio/current/.config/obs-studio"]:
        if c and (Path(c).expanduser() / "global.ini").exists():
            return Path(c).expanduser()
    sys.exit("OBS config dir not found (set OBS_CONFIG_PATH)")


def active_names(cfg):
    ini = configparser.RawConfigParser(strict=False)
    ini.optionxform = str
    for f in ("user.ini", "global.ini"):  # OBS 31+ moved [Basic] to user.ini
        if (cfg / f).exists():
            ini.read(cfg / f)
            if ini.has_section("Basic"):
                b = ini["Basic"]
                return b.get("ProfileDir", b.get("Profile")), b.get("SceneCollectionFile", b.get("SceneCollection"))
    sys.exit("could not find [Basic] Profile/SceneCollection in user.ini or global.ini")


def backup(path):
    dst = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(path, dst)
    return dst


def binding(b):
    out = {"key": b["key"]}
    for mod in ("shift", "control", "alt", "command"):
        if b.get(mod):
            out[mod] = True
    return out


def apply_frontend(cfg, profile, frontend, dry):
    path = cfg / "basic/profiles" / profile / "basic.ini"
    lines = path.read_text().splitlines()
    # Plain line edit: configparser would mangle OBS's ini (case, ordering, JSON values).
    start = next((i for i, l in enumerate(lines) if l.strip() == "[Hotkeys]"), None)
    if start is None:
        lines += ["", "[Hotkeys]"]
        start = len(lines) - 1
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[")), len(lines))
    section = {l.split("=", 1)[0]: l for l in lines[start + 1:end] if "=" in l}
    for name, binds in frontend.items():
        section[name] = f"{name}=" + json.dumps({"bindings": [binding(b) for b in binds]}, separators=(",", ":"))
    lines[start + 1:end] = list(section.values()) + [""]
    if dry:
        print(f"[dry-run] {path}:\n" + "\n".join(section.values()))
        return
    print(f"backup {backup(path)}")
    path.write_text("\n".join(lines).rstrip("\n") + "\n")
    print(f"wrote {len(frontend)} frontend hotkey(s) to {path}")


def apply_scenes(cfg, collection, scenes, dry):
    path = cfg / "basic/scenes" / f"{collection.removesuffix('.json')}.json"
    data = json.loads(path.read_text())
    by_name = {s["name"]: s for s in data["sources"] if s.get("id") == "scene"}
    missing = [n for n in scenes if n not in by_name]
    if missing:
        print(f"WARNING scenes not in collection (create them first): {missing}")
    for name, binds in scenes.items():
        if name in by_name:
            by_name[name].setdefault("hotkeys", {})["OBSBasic.SelectScene"] = [binding(b) for b in binds]
    if dry:
        print(f"[dry-run] {path}: scene hotkeys for {[n for n in scenes if n in by_name]}")
        return
    print(f"backup {backup(path)}")
    path.write_text(json.dumps(data, indent=4))
    print(f"wrote scene hotkeys to {path}")


def apply_global(entries, dry):
    STABLE_DIR.mkdir(parents=True, exist_ok=True)
    stable = STABLE_DIR / "obs_ws.py"
    uv = shutil.which("uv") or "uv"
    for e in entries:
        args = " ".join(f"'{a}'" if any(c in a for c in ' {}"') else a for a in e["args"])
        desktop = (
            "[Desktop Entry]\nType=Application\nNoDisplay=true\n"
            f"Name={e['name']}\n"
            f"Exec={uv} run -q --with obsws-python python3 {stable} {args}\n"
            f"X-KDE-Shortcuts={e['shortcut']}\n"
        )
        target = APPS_DIR / f"{e['id']}.desktop"
        if dry:
            print(f"[dry-run] {target}:\n{desktop}")
            continue
        APPS_DIR.mkdir(parents=True, exist_ok=True)
        target.write_text(desktop)
        print(f"wrote {target} ({e['shortcut']})")
    if not dry and entries:
        shutil.copy2(HERE / "obs_ws.py", stable)
        for tool in ("kbuildsycoca6", "kbuildsycoca5"):
            if shutil.which(tool):
                subprocess.run([tool], capture_output=True)
                break


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec = json.loads(Path(sys.argv[1]).read_text())
    dry = "--dry-run" in sys.argv
    needs_closed = spec.get("frontend") or spec.get("scenes")
    if needs_closed and not dry and subprocess.run(["pgrep", "-x", "obs"], capture_output=True).returncode == 0:
        sys.exit("OBS is running: close it first (it overwrites hotkey config on exit)")
    cfg = config_dir()
    profile, collection = active_names(cfg)
    if spec.get("frontend"):
        apply_frontend(cfg, profile, spec["frontend"], dry)
    if spec.get("scenes"):
        apply_scenes(cfg, collection, spec["scenes"], dry)
    if spec.get("global"):
        apply_global(spec["global"], dry)


if __name__ == "__main__":
    main()
