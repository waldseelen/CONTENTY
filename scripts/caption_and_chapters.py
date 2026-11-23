#!/usr/bin/env python3
"""caption_and_chapters.py — Apply ASR term corrections, emit SRT / 9:16 safe ASS,
and validate YouTube chapters.txt rules.

Usage:
  python3 scripts/caption_and_chapters.py transcript/raw_timed.json \
    --corrections brand/caption-corrections.example.json \
    --srt exports/captions.srt \
    --ass exports/shorts.ass

  python3 scripts/caption_and_chapters.py --validate-chapters metadata/chapters.txt --duration 620
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},72,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def fmt_srt_time(sec: float) -> str:
    ms_total = max(0, int(round(sec * 1000)))
    h, rem = divmod(ms_total, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass_time(sec: float) -> str:
    cs_total = max(0, int(round(sec * 100)))
    h, rem = divmod(cs_total, 360_000)
    m, rem = divmod(rem, 6_000)
    s, cs = divmod(rem, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def load_replacements(path: Path | None) -> list[tuple[re.Pattern[str], str]]:
    if path is None or not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_map = data.get("replace", {})
    pairs = sorted(raw_map.items(), key=lambda kv: len(kv[0]), reverse=True)
    compiled: list[tuple[re.Pattern[str], str]] = []
    for wrong, right in pairs:
        pat = re.compile(rf"(?<!\w){re.escape(wrong)}(?!\w)", re.IGNORECASE)
        compiled.append((pat, right))
    return compiled


def apply_corrections(text: str, rules: list[tuple[re.Pattern[str], str]]) -> str:
    out = text.strip()
    for pat, repl in rules:
        out = pat.sub(repl, out)
    return out


def wrap_caption(text: str, width: int, max_lines: int) -> str:
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    if len(lines) <= max_lines:
        return "\n".join(lines)
    kept = lines[: max_lines - 1]
    kept.append(" ".join(lines[max_lines - 1 :]))
    return "\n".join(kept)


def write_srt(segments: list[dict], out_path: Path) -> None:
    blocks: list[str] = []
    for idx, seg in enumerate(segments, start=1):
        wrapped = wrap_caption(seg["text"], width=42, max_lines=2)
        blocks.append(
            f"{idx}\n{fmt_srt_time(seg['start'])} --> {fmt_srt_time(seg['end'])}\n{wrapped}"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def write_ass(segments: list[dict], out_path: Path, font: str, margin_v: int) -> None:
    lines = [ASS_HEADER.format(font=font, margin_v=margin_v).rstrip()]
    for seg in segments:
        wrapped = wrap_caption(seg["text"], width=28, max_lines=2).replace("\n", r"\N")
        lines.append(
            f"Dialogue: 0,{fmt_ass_time(seg['start'])},{fmt_ass_time(seg['end'])},Default,,0,0,0,,{wrapped}"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_timestamp_sec(ts: str) -> int:
    parts = [int(p) for p in ts.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(f"Gecersiz zaman damgasi: {ts}")


def validate_chapters(chapters_path: Path, total_duration: float | None) -> list[str]:
    errors: list[str] = []
    if not chapters_path.is_file():
        return [f"Dosya bulunamadi: {chapters_path}"]

    entries: list[tuple[int, str]] = []
    for lineno, raw in enumerate(chapters_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$", line)
        if not m:
            errors.append(f"Satir {lineno}: bicim hatasi -> {line!r}")
            continue
        entries.append((parse_timestamp_sec(m.group(1)), m.group(2).strip()))

    if len(entries) < 3:
        errors.append(f"En az 3 bolum gerekli, mevcut: {len(entries)}")
    if entries and entries[0][0] != 0:
        errors.append(f"Ilk bolum 00:00 ile baslamali, mevcut: {entries[0][0]}s")

    for i in range(1, len(entries)):
        prev_t, _ = entries[i - 1]
        cur_t, title = entries[i]
        if cur_t <= prev_t:
            errors.append(f"Bolum sirasi hatali ({title}): {cur_t}s <= {prev_t}s")
        elif cur_t - prev_t < 10:
            errors.append(f"Bolum suresi < 10s ({entries[i - 1][1]}): {cur_t - prev_t}s")

    if total_duration is not None and entries:
        last_dur = total_duration - entries[-1][0]
        if last_dur < 10:
            errors.append(f"Son bolum suresi < 10s ({entries[-1][1]}): {last_dur:.1f}s")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="ASR corrections, SRT/ASS export, and YouTube chapters validator")
    parser.add_argument("timed_json", nargs="?", type=Path, help="transcribe.py *_timed.json ciktisi")
    parser.add_argument("--corrections", type=Path, default=None, help="caption-corrections.json yolu")
    parser.add_argument("--srt", type=Path, default=None, help="16:9 YouTube .srt cikti yolu")
    parser.add_argument("--ass", type=Path, default=None, help="9:16 Shorts .ass cikti yolu")
    parser.add_argument("--font", default="Noto Sans", help="ASS font adi")
    parser.add_argument("--margin-v", type=int, default=340, help="ASS alt guvenli alan boslugu (px)")
    parser.add_argument("--validate-chapters", type=Path, default=None, help="chapters.txt dogrula")
    parser.add_argument("--duration", type=float, default=None, help="Video toplam suresi (sn)")
    args = parser.parse_args()

    if args.timed_json is None and args.validate_chapters is None:
        parser.error("timed_json veya --validate-chapters verilmelidir.")

    if args.timed_json is not None:
        if not args.timed_json.is_file():
            print(f"HATA: Dosya bulunamadi: {args.timed_json}", file=sys.stderr)
            return 2
        data = json.loads(args.timed_json.read_text(encoding="utf-8"))
        rules = load_replacements(args.corrections)
        segs = [
            {
                "start": float(s["start"]),
                "end": float(s["end"]),
                "text": apply_corrections(s["text"], rules),
            }
            for s in data.get("segments", [])
            if s.get("text", "").strip()
        ]
        if args.srt:
            write_srt(segs, args.srt)
            print(f"SRT yazildi ({len(segs)} satir): {args.srt}")
        if args.ass:
            write_ass(segs, args.ass, args.font, args.margin_v)
            print(f"ASS yazildi ({len(segs)} satir): {args.ass}")

    if args.validate_chapters is not None:
        errs = validate_chapters(args.validate_chapters, args.duration)
        if errs:
            print("BOLUM DOGRULAMA HATALARI:", file=sys.stderr)
            for err in errs:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print(f"Bolumler gecerli: {args.validate_chapters}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
