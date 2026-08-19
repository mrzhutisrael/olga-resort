# -*- coding: utf-8 -*-
"""
מקטין את קובצי הפונט הלטיניים לתווים שבאמת מופיעים באתר.

הבעיה: חמישה קובצי לטינית שוקלים 132KB, שהם 29 אחוז מכל מה שנטען
בטעינה הראשונה. באתר עברי הם נחוצים בעיקר לספרות (מחירים, תאריכים,
מספרי טלפון) ולתשע מילים לטיניות. הסט המלא כולל לטינית מורחבת,
אותיות עם סימנים דיאקריטיים וליגטורות שלא יופיעו כאן לעולם.

טווח התווים כאן רחב יותר ממה שהאתר משתמש בו כרגע, בכוונה: ASCII
מלא ועוד סימנים נפוצים, כדי ששינוי קופי עתידי לא ישבור אות.

  python subset_fonts.py         # מקטין לתוך fonts/ ושומר גיבוי
"""
import os, shutil, sys

FONTS = r"C:\users\y\desktop\david\site\fonts"
BACKUP = os.path.join(FONTS, "_full")

# ASCII מלא + סימנים שמופיעים באתר או עשויים להופיע
RANGES = (
    "U+0020-007E,"          # ASCII בסיסי
    "U+00A0,U+00A9,U+00AB,U+00BB,U+00B7,U+00D7,"   # רווח קשיח, ©, מרכאות, ·, ×
    "U+2010-2015,U+2018-201E,U+2022,U+2026,"       # מקפים, מרכאות טיפוגרפיות, בולט, …
    "U+2039,U+203A,U+2032,U+2033,"                 # ‹ › ′ ″
    "U+20AA,"                                       # ₪
    "U+2190-2193,U+21D0-21D2,"                     # חצים
    "U+2212,U+2013,"                                # מינוס, מקף
    "U+2605,U+2606,U+2713"                          # כוכבים, וי
)


def main():
    from fontTools.subset import main as subset_main

    os.makedirs(BACKUP, exist_ok=True)
    files = [f for f in os.listdir(FONTS) if f.endswith("-latin.woff2")]
    if not files:
        raise SystemExit("לא נמצאו קובצי latin ב-" + FONTS)

    before = after = 0
    for fn in files:
        src = os.path.join(FONTS, fn)
        keep = os.path.join(BACKUP, fn)
        # הגיבוי נשמר פעם אחת בלבד, כדי שהרצה חוזרת לא תקטין קובץ מוקטן
        if not os.path.exists(keep):
            shutil.copy2(src, keep)
        b = os.path.getsize(keep)
        out = src + ".tmp"
        subset_main([
            keep,
            "--unicodes=" + RANGES,
            "--flavor=woff2",
            "--layout-features=kern,liga,tnum,lnum",
            "--no-hinting",
            "--desubroutinize",
            "--output-file=" + out,
        ])
        a = os.path.getsize(out)
        os.replace(out, src)
        before += b; after += a
        print(f"  {fn:32} {b/1024:5.0f}KB -> {a/1024:5.0f}KB")

    print(f"\n  סה\"כ {before/1024:.0f}KB -> {after/1024:.0f}KB "
          f"(חיסכון {(before-after)/1024:.0f}KB, {100*(1-after/before):.0f} אחוז)")
    print(f"  המקור המלא נשמר ב-{BACKUP}")


if __name__ == "__main__":
    main()
