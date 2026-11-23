#!/usr/bin/env python3
"""Small obs-websocket v5 CLI for the obs-mgmt plugin.

Run with:  uv run --with obsws-python python3 obs_ws.py <command> [args]

Commands:
  status                      JSON: OBS/websocket versions, scenes, current scene, record state
  trigger <Request> [json]    Send any obs-websocket request, e.g. ToggleRecord,
                              SetCurrentProgramScene '{"sceneName":"Talking Head"}'
  scene <name>                Switch the program scene
  apply-scenes <file|dir>...  Create scenes from declarative specs (idempotent)

Connection: OBS_WEBSOCKET_URL (default ws://localhost:4455). Password from
OBS_WEBSOCKET_PASSWORD, else read from OBS's own websocket config on this machine
(<config>/plugin_config/obs-websocket/config.json), so nothing has to be stored.
"""
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

CANDIDATE_CONFIGS = [
    os.environ.get("OBS_CONFIG_PATH", ""),
    "~/.config/obs-studio",
    "~/.var/app/com.obsproject.Studio/config/obs-studio",
    "~/snap/obs-studio/current/.config/obs-studio",
]


def config_dir():
    for c in CANDIDATE_CONFIGS:
        if c and (Path(c).expanduser() / "global.ini").exists():
            return Path(c).expanduser()
    return None


def connect():
    try:
        import obsws_python as obs
    except ImportError:
        sys.exit("obsws-python missing: run via `uv run --with obsws-python python3 obs_ws.py ...`")
    url = urlparse(os.environ.get("OBS_WEBSOCKET_URL", "ws://localhost:4455"))
    password = os.environ.get("OBS_WEBSOCKET_PASSWORD")
    if not password:
        cfg = config_dir()
        ws = cfg / "plugin_config/obs-websocket/config.json" if cfg else None
        if ws and ws.exists():
            d = json.loads(ws.read_text())
            if not d.get("server_enabled"):
                sys.exit("obs-websocket is disabled in OBS (Tools > WebSocket Server Settings)")
            password = d.get("server_password", "") if d.get("auth_required") else ""
    try:
        return obs.ReqClient(host=url.hostname, port=url.port or 4455, password=password or "", timeout=5)
    except Exception as e:  # connection refused, auth failure
        sys.exit(f"cannot connect to OBS at {url.geturl()}: {e}")


def attrs(resp):
    return {k: getattr(resp, k) for k in getattr(resp, "attrs", lambda: [])()}


def cmd_status(cl):
    v = cl.get_version()
    scenes = cl.get_scene_list()
    rec = cl.get_record_status()
    video = cl.get_video_settings()
    print(json.dumps({
        "obs_version": v.obs_version,
        "websocket_version": v.obs_web_socket_version,
        "platform": v.platform_description,
        "canvas": [video.base_width, video.base_height],
        "fps": video.fps_numerator / video.fps_denominator,
        "current_scene": scenes.current_program_scene_name,
        "scenes": [s["sceneName"] for s in reversed(scenes.scenes)],
        "recording": rec.output_active,
        "record_directory": cl.get_record_directory().record_directory,
    }, indent=2))


def cmd_trigger(cl, request, payload=None):
    data = json.loads(payload) if payload else None
    resp = cl.send(request, data, raw=True)
    print(json.dumps(resp or {"ok": True}, indent=2))


def transform_for(fit, canvas, item):
    cw, ch = canvas
    if fit == "full":
        return {"positionX": 0, "positionY": 0, "alignment": 5,
                "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsAlignment": 0,
                "boundsWidth": cw, "boundsHeight": ch}
    if fit and fit.startswith("pip-"):
        w = round(cw * item.get("pip_width", 0.25))
        h = round(w * 9 / 16)
        m = item.get("pip_margin", 32)
        corner = fit[4:]
        x = m if corner.endswith("l") else cw - w - m
        y = m if corner.startswith("t") else ch - h - m
        return {"positionX": x, "positionY": y, "alignment": 5,
                "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsAlignment": 0,
                "boundsWidth": w, "boundsHeight": h}
    return None


def load_specs(paths):
    specs = []
    for p in map(Path, paths):
        files = sorted(p.glob("*.json")) if p.is_dir() else [p]
        for f in files:
            d = json.loads(f.read_text())
            specs.extend(d if isinstance(d, list) else [d])
    return specs


def cmd_apply(cl, *paths):
    video = cl.get_video_settings()
    canvas = (video.base_width, video.base_height)
    existing_scenes = {s["sceneName"] for s in cl.get_scene_list().scenes}
    existing_inputs = {i["inputName"] for i in cl.get_input_list().inputs}
    report = []
    for spec in load_specs(paths):
        name = spec["scene"]
        if name not in existing_scenes:
            cl.create_scene(name)
            existing_scenes.add(name)
            report.append(f"created scene {name}")
        present = {i["sourceName"]: i["sceneItemId"] for i in cl.get_scene_item_list(name).scene_items}
        # Spec lists items top-to-bottom; add bottom-most first so the first item ends on top.
        for item in reversed(spec.get("items", [])):
            src = item["input"]
            if src in present:
                item_id = present[src]
            elif src in existing_inputs:
                item_id = cl.create_scene_item(name, src, True).scene_item_id
                report.append(f"  added existing input {src} to {name}")
            else:
                item_id = cl.create_input(name, src, item["kind"], item.get("settings", {}), True).scene_item_id
                existing_inputs.add(src)
                report.append(f"  created input {src} ({item['kind']}) in {name}")
            t = transform_for(item.get("fit"), canvas, item)
            if t:
                cl.set_scene_item_transform(name, item_id, t)
    for line in report or ["nothing to do: all scenes and items already present"]:
        print(line)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cl = connect()
    cmd, args = argv[1], argv[2:]
    if cmd == "status":
        cmd_status(cl)
    elif cmd == "trigger":
        cmd_trigger(cl, *args)
    elif cmd == "scene":
        cl.set_current_program_scene(args[0])
    elif cmd == "apply-scenes":
        cmd_apply(cl, *args)
    else:
        sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    main(sys.argv)
