# -*- coding: utf-8 -*-
"""
אוצרות ועיבוד תמונות לאתר.

עד אוגוסט 2026 המקורות היו צילומים שנשלפו מ-Airbnb ומ-rrr, בחציון
900x600 (0.5 מגה-פיקסל). כלומר האתר ניפח כל תמונה גדולה ממקור קטן.
עכשיו יש סט מקצועי: HDR ב-3000px עם שמיים מרוטשים, וצילומי רחפן
ב-6144x3456. לכן נוספה גם רמת 2000px, שקודם לא היה לה מקור אמיתי.

MEDIA/ הוא הסט החדש, photos-source/ הוא הישן. תמונה שאין לה תחליף
חדש (חדרי שינה, מקלחות, סנוקר) נשארת על המקור הישן, וזה בסדר:
עדיף מקור אמיתי בקטן מאשר ניפוח.
"""
import os, io, json, base64
from PIL import Image, ImageFilter

ROOT  = r"C:\users\y\desktop\david"
OUT   = os.path.join(ROOT, "site", "assets")

# כל מקור נפתר מול הרשימה הזו, לפי הסדר
SRC_ROOTS = [
    os.path.join(ROOT, "media-new"),        # sky/ , drone/ , svc/
    os.path.join(ROOT, "photos-source"),    # airbnb/ , rrr/
]

# (מזהה, קובץ מקור, כתובית): הסדר הוא סדר התצוגה בגלריה
CURATED = [
 # --- ירו ---
 # תמונה ייעודית לירו ולא מיחזור של תמונת גלריה. שלושה תנאים שהיא
 # עומדת בהם ורוב האחרות לא: הבריכה היא הנושא ולא פרט בפינה, נוף
 # העץ ממלא את הפינה הימנית העליונה ונותן לכותרת רקע כהה טבעי,
 # והרקע נקי יחסית מבתי השכנים.
 ("hero-pool",         "sky/_DSC9481-HDRsky.jpg",      "הבריכה והדק בשעת השקיעה"),
 # --- בריכה ודק ---
 ("pool-tree-golden",  "sky/_DSC9516-HDRsky.jpg",      "הבריכה בשעת השקיעה"),
 ("pool-tree-day",     "sky/_DSC9476-HDRsky.jpg",      "מקלחת חוץ ודק העץ"),
 ("pool-lounger",      "sky/DJI_20260807140944_0725_Dsky.jpg", "פינת שיזוף לצד הבריכה"),
 ("pool-deck",         "sky/_DSC9521-HDRsky.jpg",      "הבריכה הפרטית"),
 ("pool-green",        "airbnb/ab035.jpg",             "הבריכה מבין הצמחייה"),
 ("pool-above",        "drone/DJI_20260629182547_0197_D.JPG",  "מבט מלמעלה על המתחם"),
 ("pool-aerial",       "drone/DJI_20260629182642_0201_D.JPG",  "הבריכה מהאוויר"),
 ("pool-blue",         "airbnb/ab028.jpg",             "מים צלולים"),
 ("pool-night",        "airbnb/ab027.jpg",             "הבריכה בלילה"),
 ("pool-flowers",      "airbnb/ab032.jpg",             "פינת הפרחים"),
 # --- ג'קוזי ומרפסת עליונה ---
 ("jacuzzi-dusk",      "drone/DJI_20260629193604_0210_D.JPG",  "הג׳קוזי בשעת השקיעה"),
 ("jacuzzi-view",      "drone/DJI_20260629193610_0211_D.JPG",  "המרפסת העליונה מול הנוף"),
 ("jacuzzi-terrace",   "drone/DJI_20260629182734_0203_D.JPG",  "ג׳קוזי מול הנוף"),
 ("terrace-view",      "sky/DJI_20260807141131_0727_Dsky sky.jpg", "מרפסת עם נוף פתוח"),
 ("terrace-dusk",      "drone/DJI_20260629193626_0212_D.JPG",  "הנוף מהמרפסת אחרי השקיעה"),
 ("layout-above",      "sky/DJI_20260807140204_0715_D1.jpg",   "הבריכה והמרפסת"),
 ("villa-aerial",      "drone/DJI_20260629093022_0150_D.JPG",  "המתחם כולו מלמעלה"),
 # --- גינה וחצר ---
 ("garden-lawn",       "sky/DJI_20260807140826_0722_Dsky.jpg", "המדשאה"),
 ("garden-path",       "sky/DJI_20260807140857_0724_Dsky.jpg", "השביל ההיקפי"),
 ("garden-sculpt",     "sky/_DSC9461-HDRSKY.jpg",      "פינת ישיבה מעוצבת"),
 ("garden-green",      "sky/_DSC9536-HDRSKY 1.jpg",    "צמחייה היקפית"),
 ("garden-hang",       "sky/_DSC9541-HDRsky.jpg",      "כורסאות תלויות"),
 ("garden-swing",      "sky/_DSC9546-HDRsky.jpg",      "פינות ישיבה בגינה"),
 ("garden-hammock",    "airbnb/bk011.jpg",             "ערסל בגינה"),
 # --- לילה ---
 ("night-lounge",      "airbnb/ab019.jpg",             "הגינה בלילה"),
 ("night-garden",      "airbnb/ab033.jpg",             "תאורת לילה"),
 # --- פנים הבית ---
 ("living-dining",     "sky/דוד מלכיאל (3).jpg",       "הסלון ופינת האוכל"),
 ("entry-bar",         "sky/דוד מלכיאל (1).jpg",       "הכניסה והמיני בר"),
 ("kitchen",           "airbnb/ab010.jpg",             "המטבח המאובזר"),
 ("bar-counter",       "sky/דוד מלכיאל (4).jpg",       "פינת הבר והישיבה"),
 ("living-wide",       "airbnb/ab040.jpg",             "החלל המרכזי"),
 ("living-open",       "airbnb/ab004.jpg",             "פתיחה אל החצר"),
 ("living-sofa",       "airbnb/ab023.jpg",             "פינת הסלון"),
 # --- חדרים ---
 ("bed-1",             "airbnb/ab000.jpg",             "חדר שינה 1"),
 ("bed-2",             "airbnb/ab006.jpg",             "חדר שינה 2"),
 ("bed-3",             "airbnb/ab015.jpg",             "חדר שינה 3"),
 ("bed-4",             "airbnb/ab037.jpg",             "חדר שינה 4"),
 ("bath-1",            "airbnb/ab042.jpg",             "חדר רחצה 1"),
 ("bath-2",            "rrr/v046.jpg",                 "חדר רחצה עם אמבט"),
 # --- משחקים ---
 ("game-hockey",       "sky/דוד מלכיאל (2).jpg",       "חדר המשחקים"),
 ("game-snooker",      "airbnb/ab038.jpg",             "שולחן סנוקר"),
 ("game-pingpong",     "airbnb/ab016.jpg",             "פינג פונג"),
 # --- שירותים שאפשר להוסיף ---
 # הצילומים האלה הם של השירות עצמו, לא של הנכס. שני כללים באוצרות:
 # לא לבחור תמונה שמראה סמל מסחרי (בתיקיית העיצוב יש פריטים עם
 # לוגו של מותג יוקרה), ולהעדיף פריים שרואים בו גם את המתחם.
 ("svc-chef",          "svc/chef/DSC00154-2.jpg",      "מנה של השף"),
 ("svc-chef-table",    "svc/chef/DSC09837-3.jpg",      "מגש הגשה"),
 ("svc-spa",           "svc/spa/DSC00254-2.jpg",       "טיפול על המרפסת"),
 ("svc-band",          "svc/band/DSB09534-2.jpg",      "הרכב אקוסטי בחצר"),
 ("svc-decor",         "svc/decor/DSC00413-2.jpg",     "עיצוב ונרות"),
 # --- כלה ונוף ---
 ("bride-room",        "airbnb/ab044.jpg",             "חדר התארגנות"),
 ("sunset-sea",        "sky/דוד.jpg",                  "הנוף מהמרפסת העליונה"),
 ("sunset-town",       "rrr/v024.jpg",                 "הנוף מהגג"),
]

# 2000 נוסף עכשיו כשיש מקורות אמיתיים בגודל הזה. גרסה רחבה מהמקור
# לעולם לא נוצרת, ולכן אין ניפוח.
WIDTHS = [2000, 1400, 900, 600]

# איכות לפי גודל. תמונה ב-2000px כמעט תמיד מוצגת מוקטנת (מסך 1536
# מציג אותה ב-1536), ולכן ארטיפקט דחיסה מתפרס על פחות פיקסלי מסך
# ולא נראה. בתמונה קטנה שמוצגת 1:1 הוא כן נראה, ושם האיכות נשארת.
QUALITY = {2000: 78, 1400: 80, 900: 82, 600: 82}


def resolve(rel):
    for r in SRC_ROOTS:
        p = os.path.join(r, rel.replace("/", os.sep))
        if os.path.exists(p):
            return p
    return None


def lqip(im: Image.Image) -> str:
    """
    תמונת ממלא זעירה שנטענת מיד ומונעת הבהוב לבן.

    WebP ולא JPEG: באותה איכות היא יוצאת פי חמישה קטנה יותר, כי כותרות
    ה-JPEG לבדן שוקלות יותר מהתמונה כולה בגודל הזה. כל 44 הממלאים יחד
    ירדו מ-208KB ל-כ-40KB בתוך ה-HTML. אין בעיית תאימות: האתר מגיש
    ממילא רק WebP.
    """
    t = im.copy()
    t.thumbnail((22, 22))
    t = t.filter(ImageFilter.GaussianBlur(0.6))
    buf = io.BytesIO()
    t.convert("RGB").save(buf, "WEBP", quality=45, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    os.makedirs(OUT, exist_ok=True)
    # מחיקה ממוקדת בלבד. rmtree על assets היה מוחק גם את סרטון הסיור,
    # את רצף הרחפן, את לוח הזמינות ואת האייקון.
    removed = 0
    for f in os.listdir(OUT):
        if f.endswith(".webp") and "-" in f and f.rsplit("-", 1)[-1][:-5].isdigit():
            os.remove(os.path.join(OUT, f)); removed += 1

    manifest, total, missing = [], 0, []
    for key, rel, caption in CURATED:
        path = resolve(rel)
        if not path:
            missing.append(rel); continue
        im = Image.open(path)
        im = im.convert("RGB")
        w0, h0 = im.size
        entry = {"key": key, "caption": caption, "w": w0, "h": h0,
                 "ratio": round(w0 / h0, 4), "lqip": lqip(im), "srcs": {}}
        for w in WIDTHS:
            if w > w0 * 1.02:
                continue
            r = im.copy()
            r.thumbnail((w, 10_000), Image.LANCZOS)
            fn = f"{key}-{w}.webp"
            r.save(os.path.join(OUT, fn), "WEBP", quality=QUALITY.get(w, 82), method=6)
            total += os.path.getsize(os.path.join(OUT, fn))
            entry["srcs"][w] = fn
        if not entry["srcs"]:                      # מקור קטן מכל הרזולוציות
            fn = f"{key}-{w0}.webp"
            im.save(os.path.join(OUT, fn), "WEBP", quality=82, method=6)
            total += os.path.getsize(os.path.join(OUT, fn))
            entry["srcs"][w0] = fn
        # שומרים את המידות של הגרסה הגדולה ביותר שנוצרה, כי width/height
        # ב-HTML חייבים להתאים ליחס האמיתי של מה שמוצג
        manifest.append(entry)

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    fresh = sum(1 for _, rel, _ in CURATED if rel.startswith(("sky/", "drone/")))
    print(f"נמחקו {removed} קבצי webp ישנים")
    print(f"{len(manifest)} תמונות, {total//1024}KB")
    print(f"  מקור חדש באיכות גבוהה: {fresh} מתוך {len(CURATED)}")
    big = sum(1 for m in manifest if 2000 in m["srcs"] or "2000" in m["srcs"])
    print(f"  יש גרסת 2000px: {big}")
    if missing:
        print("  חסרים:", missing)


if __name__ == "__main__":
    main()
