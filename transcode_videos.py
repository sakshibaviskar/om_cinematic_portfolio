from pathlib import Path
import subprocess
import shutil
import tempfile

import imageio_ffmpeg

ROOT = Path(r"c:\Users\My Dell\Desktop\om_cinematic")
FFMPEG = Path(imageio_ffmpeg.get_ffmpeg_exe())
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".avi", ".mkv"}


def encode(source: Path) -> Path:
    if source.suffix.lower() == ".mp4":
        target = source.with_name(f"{source.stem}.optimized.mp4")
    else:
        target = source.with_suffix(".mp4")

    temp_target = target.with_name(f"{target.stem}.tmp{target.suffix}")
    if temp_target.exists():
        temp_target.unlink()

    command = [
        str(FFMPEG),
        "-y",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "slow",
        "-pix_fmt",
        "yuv420p",
        "-profile:v",
        "high",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ac",
        "2",
        "-ar",
        "44100",
        str(temp_target),
    ]

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed for {source}\n{completed.stdout}\n{completed.stderr}"
        )

    if target.exists():
        target.unlink()
    temp_target.replace(target)

    if source.suffix.lower() == ".mp4":
        source.unlink()
        target.replace(source)
        return source

    return target


def main() -> None:
    sources = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in VIDEO_EXTS
    )

    for source in sources:
        before = source.stat().st_size
        result = encode(source)
        after = result.stat().st_size
        print(f"{source.relative_to(ROOT)} -> {result.relative_to(ROOT)} | {before} -> {after}")


if __name__ == "__main__":
    main()
