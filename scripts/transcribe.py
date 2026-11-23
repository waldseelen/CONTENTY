#!/usr/bin/env python3
"""transcribe.py — Local transcription via faster-whisper (Linux/Windows/CPU/CUDA)
with automatic mlx-whisper preference on Apple Silicon.

Usage:
  python3 transcribe.py INPUT.mp4 OUTPREFIX [--lang tr] [--words] [--model large-v3-turbo]
Outputs:
  transcript/<OUTPREFIX>_timed.json
  transcript/<OUTPREFIX>_narration.txt
"""
import argparse
import importlib.util
import json
import os
import platform
import sys
import time

try:
    import certifi

    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass


def transcribe_mlx(inp: str, lang: str, word_ts: bool, model_name: str) -> dict:
    import mlx_whisper

    repo = model_name if "/" in model_name else f"mlx-community/whisper-{model_name}"
    result = mlx_whisper.transcribe(
        inp,
        path_or_hf_repo=repo,
        language=lang,
        word_timestamps=word_ts,
    )
    segs = []
    for s in result.get("segments", []):
        item = {
            "start": round(s["start"], 2),
            "end": round(s["end"], 2),
            "text": s["text"].strip(),
        }
        if word_ts and "words" in s:
            item["words"] = [
                {
                    "word": w["word"].strip(),
                    "start": round(w["start"], 2),
                    "end": round(w["end"], 2),
                }
                for w in s["words"]
            ]
        segs.append(item)
    return {"text": result.get("text", "").strip(), "segments": segs}


def transcribe_faster_whisper(inp: str, lang: str, word_ts: bool, model_name: str) -> dict:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="auto", compute_type="auto")
    segments_iter, _ = model.transcribe(inp, language=lang, word_timestamps=word_ts)
    segs = []
    texts = []
    for s in segments_iter:
        txt = s.text.strip()
        texts.append(txt)
        item = {"start": round(s.start, 2), "end": round(s.end, 2), "text": txt}
        if word_ts and s.words:
            item["words"] = [
                {
                    "word": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                }
                for w in s.words
            ]
        segs.append(item)
    return {"text": " ".join(texts).strip(), "segments": segs}


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Whisper transcription")
    parser.add_argument("input", help="Input video/audio file")
    parser.add_argument("prefix", nargs="?", default="out", help="Output filename prefix")
    parser.add_argument("--lang", default="tr", help="Language code (default: tr)")
    parser.add_argument("--words", action="store_true", help="Include word-level timestamps")
    parser.add_argument("--model", default="large-v3-turbo", help="Whisper model name")
    parser.add_argument("--outdir", default=None, help="Output directory")
    args = parser.parse_args()

    outdir = args.outdir or os.path.join(os.path.dirname(os.path.abspath(args.input)), "transcript")
    os.makedirs(outdir, exist_ok=True)

    use_mlx = (
        platform.system() == "Darwin"
        and platform.machine() == "arm64"
        and importlib.util.find_spec("mlx_whisper") is not None
    )
    has_fw = importlib.util.find_spec("faster_whisper") is not None

    if not use_mlx and not has_fw:
        print(
            "HATA: faster-whisper (veya Apple Silicon'da mlx-whisper) kurulu degil.",
            file=sys.stderr,
        )
        return 1

    engine = "mlx-whisper" if use_mlx else "faster-whisper"
    print(f"transcribe basliyor ({engine}, {args.model}, {args.lang}): {os.path.basename(args.input)}", flush=True)
    t0 = time.time()

    data = (
        transcribe_mlx(args.input, args.lang, args.words, args.model)
        if use_mlx
        else transcribe_faster_whisper(args.input, args.lang, args.words, args.model)
    )

    segs = data["segments"]
    dur_min = segs[-1]["end"] / 60 if segs else 0.0

    timed_path = os.path.join(outdir, f"{args.prefix}_timed.json")
    text_path = os.path.join(outdir, f"{args.prefix}_narration.txt")
    with open(timed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(data["text"] + "\n")

    print(f"OK · segment:{len(segs)} · icerik:{dur_min:.1f}dk · islem:{time.time()-t0:.0f}sn", flush=True)
    print(f"kaydedildi: {timed_path} + {text_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
