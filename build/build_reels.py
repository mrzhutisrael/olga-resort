# -*- coding: utf-8 -*-
"""
מכין את סרטוני הרילס לאתר.

הסרטונים המקוריים הם 1440x2560 ו-1080x1920, בסך הכל 315MB. אי אפשר
להגיש אותם כמו שהם. כאן הם יורדים ל-720px רוחב עם H.264, ומכל אחד
נשלף גם פוסטר. הפוסטר הוא מה שנטען בדף; הווידאו עצמו preload="none"
ויורד רק בלחיצה.

למה 720 ולא יותר: הכרטיס ברוחב 300px בערך, ובמסך פי 2 זה 600px.
720 נותן מרווח ולא יותר מזה.
"""
import json, os, re, subprocess, sys

FFMPEG  = r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
FFPROBE = r"C:\ProgramData\chocolatey\bin\ffprobe.exe"
SRC     = r"C:\users\y\desktop\david\media-new\edit"
OUT     = r"C:\users\y\desktop\david\site\assets\reels"

# (קובץ מקור, מזהה, כותרת, שנייה לפוסטר)
REELS = [
    ("Olga Facillities 7.mp4", "facilities", "המתחם",        6),
    ("POV 3.mp4",              "pov",        "סיבוב בבית",   3),
    ("FOOD 4.mp4",             "food",       "האוכל",        4),
    ("Wedding vid 2.mp4",      "wedding",    "אירוע",        8),
    ("Olga resort 6.mp4",      "resort",     "ערב במתחם",    5),
    ("Vid 1.mp4",              "coast",      "החוף שלידנו",  2),
]


def probe(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,duration",
         "-of", "json", path], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"]), float(s.get("duration") or 0)


def main():
    os.makedirs(OUT, exist_ok=True)
    man = []
    for fn, key, title, poster_at in REELS:
        src = os.path.join(SRC, fn)
        if not os.path.exists(src):
            print("  חסר:", fn); continue
        w, h, dur = probe(src)

        mp4 = os.path.join(OUT, key + ".mp4")
        subprocess.run([
            FFMPEG, "-y", "-loglevel", "error", "-i", src,
            "-vf", "scale=720:-2",
            "-c:v", "libx264", "-crf", "30", "-preset", "slow",
            "-profile:v", "main", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "64k", "-ac", "1",
            "-movflags", "+faststart", mp4], check=True)

        jpg = os.path.join(OUT, key + ".webp")
        subprocess.run([
            FFMPEG, "-y", "-loglevel", "error", "-ss", str(min(poster_at, max(0, dur - 1))),
            "-i", src, "-frames:v", "1", "-vf", "scale=560:-2",
            "-quality", "80", jpg], check=True)

        man.append({"key": key, "title": title,
                    "w": 720, "h": round(720 * h / w),
                    "dur": round(dur),
                    "mp4": f"reels/{key}.mp4", "poster": f"reels/{key}.webp",
                    "mb": round(os.path.getsize(mp4) / 1e6, 1)})
        print(f"  {title:12} {w}x{h} {dur:5.1f}s  ->  {man[-1]['mb']:.1f}MB")

    with open(os.path.join(OUT, "reels.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    tot = sum(m["mb"] for m in man)
    print(f"\n  {len(man)} סרטונים, {tot:.1f}MB בסך הכל (נטענים רק בלחיצה)")


if __name__ == "__main__":
    main()
