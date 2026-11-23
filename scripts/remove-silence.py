#!/usr/bin/env python3
"""Klasik bosluk silme — ffmpeg silencedetect ile sessiz araliklari kesip
konusma parcalarini birlestirir (A/V senkron korunur, tek re-encode).

Kullanim:
  python3 remove-silence.py <input.mp4> [output.mp4] [--db -30] [--min 0.6] [--pad 0.12]
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile


def probe_duration(path: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            path,
        ]
    )
    return float(out.decode().strip())


def detect_silences(path: str, noise_db: float, min_sil: float) -> list[tuple[float, float]]:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-i",
            path,
            "-af",
            f"silencedetect=noise={noise_db}dB:d={min_sil}",
            "-f",
            "null",
            "-",
        ],
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    sils: list[tuple[float, float]] = []
    cur: float | None = None
    for line in proc.stderr.splitlines():
        m_start = re.search(r"silence_start:\s*([-\d.]+)", line)
        if m_start:
            cur = float(m_start.group(1))
        m_end = re.search(r"silence_end:\s*([-\d.]+)", line)
        if m_end and cur is not None:
            sils.append((cur, float(m_end.group(1))))
            cur = None
    return sils


def build_keep_ranges(
    sils: list[tuple[float, float]], dur: float, pad: float
) -> list[list[float]]:
    keeps: list[list[float]] = []
    pos = 0.0
    for start, end in sils:
        if start - pos > 0.05:
            keeps.append([max(0.0, pos - pad), min(dur, start + pad)])
        pos = end
    if dur - pos > 0.05:
        keeps.append([max(0.0, pos - pad), dur])

    merged: list[list[float]] = []
    for k in keeps:
        if merged and k[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], k[1])
        else:
            merged.append(k)
    return [k for k in merged if k[1] - k[0] > 0.10]


def main() -> int:
    parser = argparse.ArgumentParser(description="FFmpeg silencedetect rough-cut")
    parser.add_argument("input", help="Girdi video/ses dosyasi")
    parser.add_argument("output", nargs="?", default=None, help="Cikti dosyasi")
    parser.add_argument("--db", type=float, default=-30.0, help="Sessizlik esigi (dB)")
    parser.add_argument("--min", type=float, default=0.6, help="Min sessizlik suresi (sn)")
    parser.add_argument("--pad", type=float, default=0.12, help="Konusma kenar tamponu (sn)")
    args = parser.parse_args()

    inp = args.input
    out = args.output or f"{os.path.splitext(inp)[0]}-cut.mp4"
    dur = probe_duration(inp)

    print(f"silencedetect (noise={args.db}dB, d={args.min}s)...", flush=True)
    sils = detect_silences(inp, args.db, args.min)
    keeps = build_keep_ranges(sils, dur, args.pad)

    kept = sum(k[1] - k[0] for k in keeps)
    pct = 100.0 * (1.0 - kept / dur) if dur > 0 else 0.0
    print(
        f"{len(sils)} sessiz aralik, {len(keeps)} konusma parcasi. "
        f"{dur:.1f}s -> {kept:.1f}s ({pct:.0f}% kesildi)",
        flush=True,
    )
    if not keeps:
        print("kesilecek bir sey yok")
        return 0

    fc_parts: list[str] = []
    for i, (s, e) in enumerate(keeps):
        fc_parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}];")
        fc_parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}];")
    fc_parts.append(
        "".join(f"[v{i}][a{i}]" for i in range(len(keeps)))
        + f"concat=n={len(keeps)}:v=1:a=1[v][a]"
    )

    fc_fd, fcpath = tempfile.mkstemp(prefix="rs_filter_", suffix=".txt")
    try:
        with os.fdopen(fc_fd, "w", encoding="utf-8") as f:
            f.write("".join(fc_parts))
        print("re-encode...", flush=True)
        res = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-stats",
                "-i",
                inp,
                "-filter_complex_script",
                fcpath,
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                out,
            ],
            check=False,
        )
    finally:
        if os.path.exists(fcpath):
            os.unlink(fcpath)

    if res.returncode != 0:
        print(f"HATA: ffmpeg exit {res.returncode}", file=sys.stderr)
        return res.returncode

    new_dur = probe_duration(out)
    size_mb = os.path.getsize(out) / 1e6
    print(f"\nBITTI: {new_dur/60:.1f} dk · {size_mb:.0f} MB · {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
