#!/usr/bin/env python3
"""qc_gate.py — Fail-closed broadcast & YouTube quality gate for rendered videos.

Checks:
  1. Container & streams via ffprobe (duration, resolution, VFR vs CFR, A/V drift)
  2. Loudness via ffmpeg ebur128 (integrated LUFS & true peak dBTP)
  3. Optional blackdetect & freezedetect scan
  4. Optional 3x2 visual contact sheet generation

Usage:
  python3 scripts/qc_gate.py final.mp4 --profile youtube --contact-sheet qc.jpg --json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Profile = Literal["youtube", "shorts", "podcast"]

PROFILE_TARGETS: dict[Profile, tuple[float, float, float]] = {
    # (target_lufs, tolerance_lufs, max_true_peak_dbtp)
    "youtube": (-14.0, 1.5, -1.0),
    "shorts": (-14.0, 1.5, -1.0),
    "podcast": (-16.0, 1.5, -1.0),
}


class QCError(RuntimeError):
    """Structured QC gate execution error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ProbeReport:
    duration_s: float
    width: int
    height: int
    fps_avg: float
    fps_r: float
    is_vfr: bool
    audio_sample_rate: int | None
    audio_channels: int | None
    av_drift_s: float | None


@dataclass(frozen=True)
class LoudnessReport:
    integrated_lufs: float
    true_peak_dbtp: float
    target_lufs: float
    max_true_peak_dbtp: float


def _require_bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise QCError("MISSING_BINARY", f"Gerekli arac bulunamadi: {name}")
    return path


def _parse_rate(rate_str: str | None) -> float:
    if not rate_str or rate_str == "0/0":
        return 0.0
    if "/" in rate_str:
        num, den = rate_str.split("/", 1)
        d = float(den)
        return float(num) / d if d != 0 else 0.0
    return float(rate_str)


def run_probe(ffprobe_bin: str, video_path: Path) -> ProbeReport:
    proc = subprocess.run(
        [
            ffprobe_bin,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise QCError("FFPROBE_FAILED", proc.stderr.strip() or "ffprobe failed")

    data = json.loads(proc.stdout)
    fmt_dur = float(data.get("format", {}).get("duration") or 0.0)
    v_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
        None,
    )
    if not v_stream:
        raise QCError("NO_VIDEO_STREAM", "Video akisi bulunamadi")

    a_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
        None,
    )
    fps_avg = _parse_rate(v_stream.get("avg_frame_rate"))
    fps_r = _parse_rate(v_stream.get("r_frame_rate"))
    is_vfr = (
        fps_avg > 0
        and fps_r > 0
        and abs(fps_avg - fps_r) / max(fps_avg, fps_r) > 0.02
    )

    v_dur = float(v_stream.get("duration") or fmt_dur)
    a_dur = float(a_stream.get("duration") or fmt_dur) if a_stream else None
    drift = round(abs(v_dur - a_dur), 4) if a_dur is not None else None

    return ProbeReport(
        duration_s=round(fmt_dur, 3),
        width=int(v_stream.get("width") or 0),
        height=int(v_stream.get("height") or 0),
        fps_avg=round(fps_avg, 3),
        fps_r=round(fps_r, 3),
        is_vfr=is_vfr,
        audio_sample_rate=int(a_stream["sample_rate"]) if a_stream and a_stream.get("sample_rate") else None,
        audio_channels=int(a_stream["channels"]) if a_stream and a_stream.get("channels") else None,
        av_drift_s=drift,
    )


def run_ebur128(ffmpeg_bin: str, video_path: Path, profile: Profile) -> LoudnessReport:
    target, _, max_tp = PROFILE_TARGETS[profile]
    proc = subprocess.run(
        [
            ffmpeg_bin,
            "-nostats",
            "-i",
            str(video_path),
            "-af",
            "ebur128=peak=true",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise QCError("EBUR128_FAILED", proc.stderr[-400:].strip())

    lines = proc.stderr.splitlines()
    summary_idx = next(
        (i for i in range(len(lines) - 1, -1, -1) if "Summary:" in lines[i]),
        None,
    )
    tail = "\n".join(lines[summary_idx:]) if summary_idx is not None else proc.stderr[-800:]

    m_i = re.search(r"\bI:\s*([-\d.]+)\s*LUFS", tail)
    m_tp = re.search(r"\bPeak:\s*([-\d.]+)\s*dBFS", tail)
    if not m_i or not m_tp:
        raise QCError("EBUR128_PARSE_ERROR", "ebur128 ozeti ayristirilamadi")

    return LoudnessReport(
        integrated_lufs=float(m_i.group(1)),
        true_peak_dbtp=float(m_tp.group(1)),
        target_lufs=target,
        max_true_peak_dbtp=max_tp,
    )


def run_visual_anomalies(
    ffmpeg_bin: str, video_path: Path
) -> tuple[list[tuple[float, float]], list[float]]:
    proc = subprocess.run(
        [
            ffmpeg_bin,
            "-nostats",
            "-i",
            str(video_path),
            "-vf",
            "blackdetect=d=0.5:pix_th=0.10,freezedetect=n=0.003:d=2.0",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise QCError("VISUAL_SCAN_FAILED", proc.stderr[-400:].strip())

    blacks: list[tuple[float, float]] = []
    freezes: list[float] = []
    for line in proc.stderr.splitlines():
        mb = re.search(r"black_start:([-\d.]+)\s+black_end:([-\d.]+)", line)
        if mb:
            blacks.append((float(mb.group(1)), float(mb.group(2))))
        mf = re.search(r"freeze_start:\s*([-\d.]+)", line)
        if mf:
            freezes.append(float(mf.group(1)))
    return blacks, freezes


def generate_contact_sheet(
    ffmpeg_bin: str, video_path: Path, out_path: Path, duration_s: float
) -> None:
    interval = max(duration_s / 6.0, 0.2)
    vf = f"fps=1/{interval:.4f},scale=640:-1,tile=3x2"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-v",
            "error",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-frames:v",
            "1",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not out_path.exists():
        raise QCError("CONTACT_SHEET_FAILED", proc.stderr.strip() or "Tile render failed")


def evaluate_failures(
    probe: ProbeReport,
    loudness: LoudnessReport | None,
    blacks: list[tuple[float, float]],
    freezes: list[float],
    profile: Profile,
    expected_duration: float | None,
) -> list[str]:
    failures: list[str] = []
    if probe.duration_s <= 0:
        failures.append("Video suresi 0 sn veya gecersiz.")
    if expected_duration is not None:
        tol = max(1.5 / probe.fps_avg, 0.05) if probe.fps_avg > 0 else 0.1
        if abs(probe.duration_s - expected_duration) > tol:
            failures.append(
                f"Sure uyusmazligi: gercek={probe.duration_s}s, hedef={expected_duration}s (tol={tol:.3f}s)"
            )
    if probe.is_vfr:
        failures.append(
            f"VFR tespit edildi (avg={probe.fps_avg}, r={probe.fps_r}); CFR donusumu gerekir."
        )
    if profile == "shorts" and probe.width > probe.height:
        failures.append(f"Shorts dikey olmali, mevcut boyut: {probe.width}x{probe.height}")
    if probe.av_drift_s is not None and probe.av_drift_s > 0.08:
        failures.append(f"A/V sure farki yuksek: {probe.av_drift_s}s (> 0.08s)")

    if loudness is None:
        failures.append("Ses akisi yok; loudness olculemedi.")
    else:
        _, tol_lufs, max_tp = PROFILE_TARGETS[profile]
        if abs(loudness.integrated_lufs - loudness.target_lufs) > tol_lufs:
            failures.append(
                f"Loudness hedef disi: {loudness.integrated_lufs:.1f} LUFS (hedef {loudness.target_lufs:.1f} ± {tol_lufs:.1f})"
            )
        if loudness.true_peak_dbtp > max_tp:
            failures.append(
                f"True peak asimi: {loudness.true_peak_dbtp:.2f} dBTP (> {max_tp:.1f})"
            )

    if blacks:
        failures.append(f"{len(blacks)} adet >=0.5s siyah bolum bulundu: {blacks[:3]}")
    if freezes:
        failures.append(f"{len(freezes)} adet >=2.0s donuk kare bulundu: {freezes[:3]}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Contenty Broadcast & YouTube QC Gate")
    parser.add_argument("video", type=Path, help="Kontrol edilecek MP4/MKV/MOV dosyasi")
    parser.add_argument("--profile", choices=["youtube", "shorts", "podcast"], default="youtube")
    parser.add_argument("--expected-duration", type=float, default=None, help="EDL hedef suresi (sn)")
    parser.add_argument("--contact-sheet", type=Path, default=None, help="3x2 temas sayfasi cikti yolu")
    parser.add_argument("--skip-visual-scan", action="store_true", help="blackdetect/freezedetect atla")
    parser.add_argument("--json", action="store_true", help="Sonucu JSON yaz")
    args = parser.parse_args()

    try:
        if not args.video.is_file():
            raise QCError("FILE_NOT_FOUND", f"Dosya bulunamadi: {args.video}")
        ffmpeg_bin = _require_bin("ffmpeg")
        ffprobe_bin = _require_bin("ffprobe")

        probe = run_probe(ffprobe_bin, args.video)
        loudness = (
            run_ebur128(ffmpeg_bin, args.video, args.profile)
            if probe.audio_sample_rate is not None
            else None
        )
        blacks, freezes = (
            ([], [])
            if args.skip_visual_scan
            else run_visual_anomalies(ffmpeg_bin, args.video)
        )
        if args.contact_sheet is not None:
            generate_contact_sheet(ffmpeg_bin, args.video, args.contact_sheet, probe.duration_s)

        failures = evaluate_failures(
            probe, loudness, blacks, freezes, args.profile, args.expected_duration
        )
        passed = len(failures) == 0

        payload = {
            "passed": passed,
            "profile": args.profile,
            "file": str(args.video),
            "probe": asdict(probe),
            "loudness": asdict(loudness) if loudness else None,
            "black_segments": blacks,
            "freeze_starts": freezes,
            "contact_sheet": str(args.contact_sheet) if args.contact_sheet else None,
            "failures": failures,
        }

        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            status = "PASS" if passed else "FAIL"
            print(f"[QC {status}] {args.video} ({args.profile})")
            print(
                f"  Video: {probe.width}x{probe.height} @ {probe.fps_avg}fps | {probe.duration_s}s | VFR={probe.is_vfr}"
            )
            if loudness:
                print(
                    f"  Audio: {loudness.integrated_lufs:.1f} LUFS | True Peak {loudness.true_peak_dbtp:.2f} dBTP"
                )
            for err in failures:
                print(f"  FAIL: {err}")

        return 0 if passed else 1
    except QCError as exc:
        if args.json:
            print(json.dumps({"passed": False, "error": {"code": exc.code, "message": exc.message}}, ensure_ascii=False))
        else:
            print(f"HATA [{exc.code}]: {exc.message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
