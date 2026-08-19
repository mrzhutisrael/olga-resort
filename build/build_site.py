# -*- coding: utf-8 -*-
"""
מרכיב את index.html מתוך התוכן שכאן ומתוך manifest התמונות.

התמונות נכתבות מהמניפסט ולא ביד, כדי שכל srcset יהיה תמיד נכון
ולא יישאר קישור שבור אחרי שינוי באוצרות התמונות.

כלל כתיבה לכל הקובץ: מספרים נכתבים בספרות ולא במילים. "17 אורחים"
נסרק בחצי שנייה, "שבעה־עשר אורחים" מאלץ קריאה. באתר שנועד להמרה
זה ההבדל בין מידע שנקלט למידע שמדלגים עליו.
"""
import json, os, html

ROOT = r"C:\users\y\desktop\david\site"
MAN = json.load(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8"))
BY = {m["key"]: m for m in MAN}

# כתובת האתר ומצב תצוגה מקדימה נקבעים ממשתני סביבה, כדי שאותה בנייה
# תשרת גם ייצור וגם preview. preview מסומן noindex ו-Disallow, כדי
# שלא יתחרה באתר האמיתי בגוגל ולא יישאר באינדקס אחריו.
SITE_URL = os.environ.get("SITE_URL", "https://olgaresort.co.il/")
PREVIEW  = os.environ.get("PREVIEW", "") == "1"

PHONE_INTL = "972554540803"
PHONE_DISP = "055-4540803"
ADDRESS = "גבעת אולגה"
# הכתובת המדויקת נמסרת אחרי אישור ההזמנה, ולכן היא לא מופיעה באתר.

URL_AIRBNB  = "https://he.airbnb.com/rooms/1501272656310177604"
URL_BOOKING = "https://www.booking.com/hotel/il/laguna-resort-lgvnh-ryzvrt.he.html"
URL_MIT     = "https://www.mit4mit.co.il/biz/105425"
URL_INSTA   = "https://www.instagram.com/villa_olgaresort/"


def img(key, sizes="100vw", cls="", eager=False, cap=False):
    m = BY[key]
    widths = sorted(int(w) for w in m["srcs"])
    srcset = ", ".join(f'assets/{m["srcs"][str(w)]} {w}w' for w in widths)
    big = m["srcs"][str(widths[-1])]
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    style = f'background:url({m["lqip"]}) center/cover no-repeat'
    tag = (f'<img src="assets/{big}" srcset="{srcset}" sizes="{sizes}" '
           f'width="{m["w"]}" height="{m["h"]}" alt="{html.escape(m["caption"])}" '
           f'style="{style}" {loading} class="{cls}">')
    if cap:
        return f'<figure class="figure clip">{tag}<figcaption>{html.escape(m["caption"])}</figcaption></figure>'
    return tag


def gal_item(key, i):
    """
    כל תמונה בגלריה היא כפתור אמיתי: אפשר להגיע אליה ב-Tab ולפתוח ב-Enter.
    בלי זה הגלריה נגישה רק בעכבר, וזו שליש מהתמונות באתר.
    """
    m = BY[key]
    widths = sorted(int(w) for w in m["srcs"])
    srcset = ", ".join(f'assets/{m["srcs"][str(w)]} {w}w' for w in widths)
    big = m["srcs"][str(widths[-1])]
    cap = html.escape(m["caption"])
    return (f'<figure data-full="assets/{big}" data-cap="{cap}" role="button" tabindex="0" '
            f'aria-label="הגדלת התמונה: {cap}">'
            f'<img src="assets/{m["srcs"][str(widths[0])]}" srcset="{srcset}" '
            f'sizes="(max-width:560px) 100vw,(max-width:1000px) 50vw,33vw" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{cap}" '
            f'style="background:url({m["lqip"]}) center/cover no-repeat" '
            f'loading="lazy" decoding="async"></figure>')


def stepper(sid, label, value, lo, hi, hint=""):
    """
    בורר כמות במקום <select> עם 30 אפשרויות. בנייד גלגל של 30 שורות
    הוא עבודה; שני כפתורים הם הקשה אחת. השדה נשאר input אמיתי,
    כך שאפשר גם להקליד וגם להגיע אליו במקלדת.
    """
    h = f'<span class="sh">{hint}</span>' if hint else ""
    return f"""<div class="field"><label for="{sid}">{label}{h}</label>
      <div class="stepper" data-lo="{lo}" data-hi="{hi}">
        <button type="button" class="sdec" aria-label="הפחתת {label}" tabindex="-1">&minus;</button>
        <input type="number" id="{sid}" value="{value}" min="{lo}" max="{hi}" step="1"
               inputmode="numeric" aria-label="{label}">
        <button type="button" class="sinc" aria-label="הוספת {label}" tabindex="-1">+</button>
      </div></div>"""


# ------------------------------------------------------------------ תוכן
SEGMENTS = [
    ("garden-lawn",     "לינה",       "משפחות וקבוצות", "עד 17 אורחים ב-4 חדרי שינה. הווילה כולה שלכם, מהכניסה ועד היציאה."),
    ("pool-tree-golden","אירוח",      "אירועים פרטיים", "עד 50 איש בחצר ובבריכה. ימי הולדת, בר ובת מצווה, שבת חתן."),
    ("bride-room",      "היום הגדול", "התארגנות כלה",   "חללים מרווחים, אור טבעי, מראות גוף ופינות צילום. כמה דקות מגני האירועים בשרון."),
    ("living-dining",   "עסקים",      "ימי גיבוש",      "יום שלם לצוות מחוץ למשרד, במקום שמרגיש כמו בית ולא כמו חדר ישיבות."),
    ("night-lounge",    "חוגגים",     "רווקים ורווקות", "ג׳קוזי, תאורת לילה ומערכת סראונד. חוגגים בלי להפריע לאף אחד."),
    ("jacuzzi-view",    "זוגות",      "סוף שבוע זוגי",  "ג׳קוזי מול הים, בריכה פרטית, ואף אחד אחר בשטח."),
]

SEG_PURPOSE = {
    "משפחות וקבוצות": "לינה משפחתית",
    "אירועים פרטיים": "אירוע פרטי",
    "התארגנות כלה":   "התארגנות כלה",
    "ימי גיבוש":      "יום גיבוש לחברה",
    "רווקים ורווקות": "מסיבת רווקים / רווקות",
    "סוף שבוע זוגי":  "חופשה זוגית",
}

AMENITIES = [
    ("בריכה ומרפסת", ["בריכה חיצונית פרטית", "מחוממת בחורף, מקוררת בקיץ",
                      "דק עץ ופינות שיזוף", "ג׳קוזי ספא זרמים", "2 מיטות שיזוף",
                      "מקלחת חוץ", "בריכה מגודרת"]),
    ("חצר וגינה",    ["חצר היקפית מטופחת", "מדשאה", "פינת ברביקיו", "ערסל",
                      "כורסאות תלויות", "תאורת לילה", "פינות ישיבה", "צמחי תבלין"]),
    ("פנים הבית",    ["4 חדרי שינה", "2.5 חדרי רחצה", "סלון ופינת אוכל מעוצבת",
                      "מיזוג בכל חדר", "ממ״ד", "מכונת כביסה ומייבש", "מגהץ וקרש"]),
    ("מטבח",         ["מטבח מאובזר במלואו", "מכונת אספרסו", "מדיח כלים", "תנור אפייה",
                      "מיקרוגל", "מיני בר", "מקרר ומקפיא", "כלי הגשה"]),
    ("פנאי",         ["שולחן סנוקר", "פינג פונג", "הוקי אוויר", "מערכת סראונד",
                      "טלוויזיה 65 אינץ׳ עם נטפליקס", "משחקי ילדים עד גיל 5"]),
    ("שירות ונוחות", ["צ׳ק־אין עצמי עם כספת", "חניה חינם במקום", "מטען לרכב חשמלי",
                      "Wi-Fi ופינת עבודה", "שמירת שבת", "חיות מחמד מותרות",
                      "גישה ללא מדרגות"]),
]

REVIEWS = [
    ("Tom", "נסיעה קבוצתית · 9 חברים", "Airbnb", URL_AIRBNB,
     "הגענו 9 חברים ללילה בוילה. דוד והצוות שלו היו מקסימים, הוילה עמדה בציפיות "
     "והיתה מאוד מסודרת ונקייה. הם האריכו לנו את הצ׳ק אאוט ללא תוספת תשלום. "
     "בסך הכל ממליץ מאוד!"),
    ("עוזי", "סופ״ש אבות ובנים · יוני 2026", "Airbnb", URL_AIRBNB,
     "הוילה היתה מטופחת ומתוחזקת היטב. יש בה כל מה שצריך, החל מחצר גדולה עם בריכה "
     "וג׳קוזי ועד שולחן סנוקר, פינג פונג ועוד. הבעלים היו אדיבים, ענו וסייעו בכל "
     "שאלה או בעיה. שווה בהחלט!"),
    ("שלומית", "שהייה עם ילדים · ינואר 2026", "Airbnb", URL_AIRBNB,
     "המקום פשוט מושלם! הגענו והכל נראה אפילו יותר יפה מהתמונות. הוילה נקייה מאוד."),
    ("לינוי", "התארגנות כלה", "mit4mit", URL_MIT,
     "את יום החתונה שלי פתחתי באולגה ריזורט וזו הייתה אחת הבחירות הכי מוצלחות שעשיתי. "
     "מהרגע שנכנסנו הרגשנו בבית. שקט ומרווח, נעים ומלא באור."),
]

SCORES = [("5.0", "דירוג כללי"), ("5.0", "ניקיון"), ("5.0", "דיוק"),
          ("5.0", "תקשורת"), ("5.0", "תמורה"), ("10", "מיקום · Booking")]

FAQ = [
    ("איך מזמינים?",
     "בוחרים תאריכים בלוח הזמינות, מקבלים הערכת מחיר מיד, ושולחים בקשה בוואטסאפ "
     "או מתקשרים. המארחים חוזרים עם אישור לתאריך ועם המחיר הסופי."),
    ("מה כלול במחיר הלינה?",
     "הנכס כולו לעד 10 אורחים: 4 חדרי שינה, הבריכה, הג׳קוזי, החצר, המטבח וחדר "
     "המשחקים. אין שיתוף עם אורחים אחרים. מעל 10 אורחים יש תוספת לאדם."),
    ("הבריכה פעילה כל השנה?",
     "כן. הבריכה מחוממת בחורף ומקוררת בימי הקיץ החמים, כך שהיא נוחה לשימוש "
     "בכל עונה."),
    ("אפשר לקיים אירוע?",
     "כן, עד 50 איש. אירועים מתומחרים בנפרד מלינה ובתיאום מראש, כי המחיר תלוי "
     "באופי האירוע, בשעות ובתוספות. השאירו פרטים ונחזור אליכם עם הצעה."),
    ("יש אפשרות להתארגנות כלה?",
     "כן, וזה אחד השימושים המבוקשים במקום. יש חללים מרווחים, אור טבעי, מראות גוף "
     "ופינות צילום, והמיקום סמוך לגני אירועים באזור השרון. יש מחירים מיוחדים "
     "להתארגנות כלה."),
    ("לוח הזמינות באתר מדויק?",
     "הלוח נשלף מלוח השנה של הווילה ומתעדכן, והוא נועד לתת תמונה מהירה של מה "
     "שפנוי. האישור הסופי לתאריך נעשה מול המארחים לפני התשלום."),
    ("מה המרחק מהים?",
     "הים והטיילת של גבעת אולגה נמצאים במרחק הליכה קצר מהווילה."),
    ("מה שעות הצ׳ק־אין והצ׳ק־אאוט?",
     "הכניסה והיציאה נקבעות מול המארחים, ויש צ׳ק־אין עצמי באמצעות כספת מפתחות. "
     "בבקשות מיוחדות אפשר לתאם מראש."),
    ("האם המקום שומר שבת?",
     "כן, המתחם מותאם לשמירת שבת."),
    ("מותר להביא חיות מחמד?",
     "כן, בתיאום מראש עם המארחים."),
]

# הגלריה היא של הנכס. צילומי השירותים (שף, ספא, להקה, עיצוב) יושבים
# בסקציה משלהם, ומנה מוגשת בין שתי תמונות חדר שינה רק מבלבלת.
GALLERY = [m["key"] for m in MAN
           if m["key"] != "sunset-town" and not m["key"].startswith("svc-")]

# שלוש תמונות שנבדלות זו מזו באמת: בריכה ודק, גינה עם הצצה לבריכה,
# ומדשאה ירוקה בדמדומים.
#
# שלושה מבחנים שכל אחת עברה, ורוב הספרייה נכשלה בהם:
# 1. הבריכה או הגינה הן הנושא, ולא פרט בפינה של פריים שרובו שמיים.
# 2. הרקע נקי מבתי השכנים. במיקום הזה זה תנאי אמיתי: צילומי הרחפן
#    מראים מגרשי עפר, מגדלי מגורים, עגורן וארובה, ולכן כל מסגור
#    רחב פוסל את עצמו.
# 3. הפינה הימנית שקטה מספיק לכותרת, גם אחרי ההכהיה הצדדית.


def hero_media() -> str:
    """
    אם הועלה וידאו ל-assets/hero.mp4 הוא מקבל עדיפות, והתמונה הראשונה
    משמשת poster כדי שלא יהיה מסך שחור עד שהוא נטען. אין וידאו?
    נופלים למקבץ תמונות שמתחלפות עם זום איטי.
    """
    first = BY[HERO_KEYS[0]]
    widths = sorted(int(w) for w in first["srcs"])
    poster = f'assets/{first["srcs"][str(widths[-1])]}'
    if os.path.exists(os.path.join(ROOT, "assets", "hero.mp4")):
        return (f'<video autoplay muted loop playsinline preload="metadata" '
                f'poster="{poster}" class="on" '
                f'style="position:absolute;inset:0;width:100%;height:100%;'
                f'object-fit:cover;opacity:1">'
                f'<source src="assets/hero.webm" type="video/webm">'
                f'<source src="assets/hero.mp4" type="video/mp4">'
                f'</video>')
    # רק התמונה הראשונה נטענת מיד. שלוש תמונות ירו ב-2000px הן 1.2MB,
    # ושתיים מהן לא נחוצות לצביעה הראשונה: הרוטציה מתחילה אחרי 7 שניות.
    # loading="lazy" לא עוזר כאן, כי כולן בתוך המסך הנראה ולכן הדפדפן
    # טוען אותן בכל מקרה. לכן הן נכתבות ל-data-src ומאוכלסות ב-JS.
    out = [img(HERO_KEYS[0], "100vw", eager=True)]
    for k in HERO_KEYS[1:]:
        m = BY[k]
        widths = sorted(int(w) for w in m["srcs"])
        srcset = ", ".join(f'assets/{m["srcs"][str(w)]} {w}w' for w in widths)
        out.append(
            f'<img data-src="assets/{m["srcs"][str(widths[-1])]}" data-srcset="{srcset}" '
            f'sizes="100vw" width="{m["w"]}" height="{m["h"]}" alt="{html.escape(m["caption"])}" '
            f'style="background:url({m["lqip"]}) center/cover no-repeat" decoding="async">')
    return "".join(out)


def ver(name):
    """
    חתימת תוכן קצרה לקובץ, כדי לשבור מטמון דפדפן.

    בלי זה, גולש שכבר ביקר באתר מקבל אחרי עדכון את ה-CSS הישן עם
    ה-HTML החדש, והדף נראה שבור. קרה בפיתוח, ויקרה גם בייצור.
    השם נשאר יציב כשהתוכן לא משתנה, ולכן המטמון עדיין עובד.
    """
    import hashlib
    fp = os.path.join(ROOT, name)
    if not os.path.exists(fp):
        return "1"
    return hashlib.sha1(open(fp, "rb").read()).hexdigest()[:8]


# שלוש תמונות שנבדלות זו מזו באמת: מרפסת עליונה בשקיעה, גינה, בריכה.
HERO_KEYS = ["hero-pool", "garden-lawn", "garden-green"]

NOINDEX = '<meta name="robots" content="noindex,nofollow">\n' if PREVIEW else ""

# ------------------------------------------------------------------ תבנית
HEAD = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>אולגה ריזורט | וילה פרטית עם בריכה וג׳קוזי בגבעת אולגה, חדרה</title>
<meta name="description" content="וילה פרטית בגבעת אולגה, חדרה. בריכה חיצונית מחוממת ומקוררת, ג׳קוזי ספא עם נוף לים, עד 17 אורחים ללינה ועד 50 לאירוע. דירוג 5.0 באיירבנב.">
<meta name="theme-color" content="#161A17">
{NOINDEX}<link rel="canonical" href="{SITE_URL}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:site_name" content="אולגה ריזורט">
<meta property="og:title" content="אולגה ריזורט | וילה פרטית עם בריכה וג׳קוזי">
<meta property="og:description" content="הנכס כולו שלכם. בריכה מחוממת כל השנה, ג׳קוזי מול הים, צעדים מטיילת גבעת אולגה.">
<meta property="og:image" content="assets/{BY['jacuzzi-dusk']['srcs'][sorted(BY['jacuzzi-dusk']['srcs'], key=int)[-1]]}">
<meta property="og:locale" content="he_IL">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/{BY[HERO_KEYS[0]]['srcs'][sorted(BY[HERO_KEYS[0]]['srcs'], key=int)[-1]]}" as="image" fetchpriority="high">
<link rel="preload" href="fonts/Bellefair-400-hebrew.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/Heebo-var-hebrew.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css?v={ver("style.css")}">
<script>
/* כל התוכן מתחיל בשקיפות 0 ומתגלה ע"י IntersectionObserver. אם המנגנון
   הזה נשבר, הדף נשאר ריק. שומר הסף בודק אחרי 5 שניות: אם הדף גלוי
   ובכל זאת שום דבר לא התגלה, מסירים את ההסתרה לגמרי.
   התנאי על document.hidden חשוב: בלשונית רקע הדפדפן משהה את המנגנון
   בכוונה, וזה לא תקלה. */
document.documentElement.className+=" js";
setTimeout(function(){{
  if(!document.hidden && !document.querySelector(".rv.in"))
    document.documentElement.className+=" rvsafe";
}},5000);
</script>
<noscript><style>
  /* בלי JS אין IntersectionObserver, וכל מה שמחכה לחשיפה היה נשאר בלתי נראה.
     עדיף אתר בלי אנימציות מאשר אתר ריק. */
  .rv{{opacity:1!important;transform:none!important}}
  .mask>span{{transform:none!important}}
  .clip{{clip-path:none!important}}
  #availability,.herobook{{display:none!important}}
</style></noscript>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"LodgingBusiness",
 "name":"אולגה ריזורט","alternateName":"Olga Resort",
 "url":"{SITE_URL}",
 "description":"וילה פרטית עם בריכה חיצונית מחוממת וג׳קוזי בגבעת אולגה, חדרה.",
 "telephone":"+{PHONE_INTL}",
 "address":{{"@type":"PostalAddress","addressLocality":"גבעת אולגה, חדרה",
   "addressRegion":"מחוז חיפה","addressCountry":"IL"}},
 "petsAllowed":true,"numberOfRooms":4,
 "amenityFeature":[
   {{"@type":"LocationFeatureSpecification","name":"בריכה חיצונית מחוממת","value":true}},
   {{"@type":"LocationFeatureSpecification","name":"ג׳קוזי ספא","value":true}},
   {{"@type":"LocationFeatureSpecification","name":"חניה חינם","value":true}},
   {{"@type":"LocationFeatureSpecification","name":"Wi-Fi","value":true}}],
 "aggregateRating":{{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"14","bestRating":"5"}}}}
</script>
</head>
<body>

<a class="skip" href="#main">דילוג לתוכן</a>

<header id="hdr">
  <a class="brand" href="#top"><b>אולגה ריזורט</b><span>Olga Resort</span></a>
  <button class="burger" id="burger" aria-label="פתיחת התפריט"
          aria-expanded="false" aria-controls="nav"><i></i><i></i><i></i></button>
  <nav id="nav">
    <a href="#spaces">המתחם</a>
    <a href="#segments">למי זה מתאים</a>
    <a href="#services">תוספות</a>
    <a href="#gallery">גלריה</a>
    <a href="#reviews">אורחים</a>
    <a href="#pricing">מחירים</a>
    <a href="#book" class="navcta">בדיקת תאריכים</a>
  </nav>
</header>

<main id="main">
"""


def build():
    P = []
    A = P.append

    A(HEAD)

    # -------- hero
    A(f"""
<div class="prog" id="prog"></div>

<section class="hero" id="top">
  <div class="hero-stack">{hero_media()}</div>
  <div class="hero-in">
    <p class="eyebrow">גבעת אולגה · חדרה</p>
    <h1><span class="mask"><span>וילה אחת.</span></span><span class="mask"><span>בלי אורחים אחרים.</span></span></h1>
    <p class="lead">בריכה מחוממת בחורף ומקוררת בקיץ, ג׳קוזי עם נוף לים, והטיילת של
       גבעת אולגה במרחק הליכה. המתחם כולו שלכם, בלי לחלוק אותו עם אף אחד.</p>

    <form class="herobook" id="herobook">
      <div class="f"><label for="hbci">תאריך כניסה</label><input type="date" id="hbci"></div>
      <div class="f"><label for="hbco">תאריך יציאה</label><input type="date" id="hbco"></div>
      <div class="f"><label for="hbad">אורחים</label>
        <div class="stepper mini" data-lo="1" data-hi="30">
          <button type="button" class="sdec" aria-label="פחות אורחים" tabindex="-1">&minus;</button>
          <input type="number" id="hbad" value="8" min="1" max="30" step="1"
                 inputmode="numeric" aria-label="מספר אורחים">
          <button type="button" class="sinc" aria-label="עוד אורחים" tabindex="-1">+</button>
        </div></div>
      <button type="submit">בדיקת מחיר</button>
    </form>

    <a class="btn hero-cta" href="#book">בדיקת תאריכים ומחיר</a>

    <div class="hero-facts">
      <div><b class="num" data-count="17">17</b><small>אורחים ללינה</small></div>
      <div><b class="num" data-count="50">50</b><small>אורחים לאירוע</small></div>
      <div><b class="num" data-count="4">4</b><small>חדרי שינה</small></div>
      <div><b class="num" data-count="5.0">5.0</b><small>דירוג אורחים</small></div>
    </div>
  </div>
  <span class="scrollhint">גללו</span>
</section>

<div class="trust">
  <div class="trust-in">
    <span class="st" aria-hidden="true">★★★★★</span>
    <span><b>5.0</b> מתוך 5 · 9 ביקורות ב-Airbnb</span>
    <span><b>10/10</b> ב-Booking.com</span>
    <span><b>מארח מצטיין</b> · Superhost</span>
    <span><b>הנכס כולו שלכם</b> · בלי שיתוף</span>
  </div>
</div>
""")

    # -------- intro
    A(f"""
<section id="about">
  <div class="wrap">
    <div class="sec-head narrow rv">
      <p class="eyebrow">אולגה ריזורט</p>
      <h2>לא מלון ולא צימר. וילה שלמה שרק אתם בתוכה</h2>
      <p class="lead">אין לובי. אין קבוצה נוספת בחצר. אין שעות ארוחה שנקבעו עבורכם,
        ואין קיר משותף עם החדר של מישהו אחר.</p>
      <p>מה שכן יש: בריכה שעובדת בינואר בדיוק כמו ביולי, ג׳קוזי במרפסת שרואים ממנה
        את הים, חצר שמקיפה את הבית מכל הצדדים, ו-4 חדרי שינה שמאפשרים ל-17 אורחים
        לישון בנוחות. הכל נמסר לקבוצה אחת בכל פעם.</p>
    </div>
    <div class="split">
      <div class="rv">{img('pool-tree-golden', '(max-width:900px) 100vw, 50vw', cap=True)}</div>
      <div class="rv">{img('jacuzzi-dusk', '(max-width:900px) 100vw, 50vw', cap=True)}</div>
    </div>
  </div>
</section>
""")

    # -------- קיר הרילס (סרטונים אנכיים)
    # המקור צולם לרילס ב-9:16. במקום למתוח אותו לרוחב מסך ולהרוס את
    # הקומפוזיציה, הסקציה בנויה סביב הפורמט: רצועה אופקית של כרטיסים
    # אנכיים. הווידאו עצמו preload="none" ויורד רק בלחיצה.
    rj = os.path.join(ROOT, "assets", "reels", "reels.json")
    if os.path.exists(rj):
        RE = json.load(open(rj, encoding="utf-8"))
        A("""
<section class="reels" id="reels">
  <div class="wrap"><div class="day-head rv">
    <div class="sec-head narrow" style="margin-bottom:0">
      <p class="eyebrow">וידאו</p>
      <h2>המקום בתנועה</h2>
      <p class="lead">שישה סרטונים קצרים מהמתחם. לחיצה מפעילה, והם
         נטענים רק אז.</p></div>
    <div class="day-nav">
      <button type="button" id="reelPrev" aria-label="לסרטון הקודם">&#8250;</button>
      <button type="button" id="reelNext" aria-label="לסרטון הבא">&#8249;</button>
    </div></div></div>
  <div class="rtrack" id="rtrack" tabindex="0" aria-label="סרטונים מהמתחם">""")
        for r in RE:
            A(f"""<article class="reel" data-src="assets/{r['mp4']}"
        role="button" tabindex="0" aria-label="הפעלת הסרטון: {r['title']}">
      <img src="assets/{r['poster']}" alt="{r['title']}" width="{r['w']}" height="{r['h']}"
           loading="lazy" decoding="async">
      <span class="play" aria-hidden="true"></span>
      <div class="r-in"><b>{r['title']}</b><span class="num">0:{r['dur']:02d}</span></div>
    </article>""")
        A("""</div>
  <p class="dayhint">גללו לצדדים לשאר הסרטונים</p>
</section>""")

    # -------- spaces
    spaces = [
        ("pool-tree-day", "הבריכה", "בריכה שלא נסגרת בחורף",
         "מחוממת בחודשים הקרים ומקוררת בימי החום, מגודרת, עם דק עץ ומקלחת חוץ "
         "בצל עץ זית. בפועל זה אומר שאפשר להיכנס אליה 12 חודשים בשנה, ולא רק בקיץ.", False),
        ("jacuzzi-view", "הקומה העליונה", "ג׳קוזי במרפסת שפונה לים",
         "ג׳קוזי זרמים עם 2 מיטות שיזוף, על מרפסת שפונה מערבה אל הים. "
         "בשעה הנכונה זה המקום שממנו לא מתחשק לזוז.", True),
        ("garden-hang", "החצר", "חצר שמקיפה את הבית",
         "מדשאה, פינת ברביקיו, ערסל, כורסאות תלויות ופינות ישיבה מפוזרות. "
         "אחרי שמחשיך התאורה נותנת למקום אופי אחר לגמרי.", False),
        ("living-wide", "פנים הבית", "הסלון שנפתח אל החצר",
         "סלון ופינת אוכל שנפתחים ברוחב מלא אל הדק, מטבח מאובזר עד הפרט האחרון, "
         "ו-4 חדרי שינה עם מזרנים אורתופדיים.", True),
        ("game-snooker", "פנאי", "מה עושים כשלא שוחים",
         "שולחן סנוקר, פינג פונג והוקי אוויר, מערכת סראונד וטלוויזיה 65 אינץ׳. "
         "גם יום גשום כאן לא מתבזבז.", False),
    ]
    A('<section id="spaces" style="background:var(--paper-2);padding-block-end:0">')
    A("""<div class="wrap"><div class="sec-head narrow rv"><p class="eyebrow">המתחם</p>
         <h2>5 מרחבים, גדר אחת</h2>
         <p class="lead">כל אחד מהם עומד בזכות עצמו, וכולם בתוך אותה חצר סגורה
            שרק אתם נכנסים אליה.</p></div></div>""")
    A('<div class="rows">')
    for key, eyebrow, title, body, rev in spaces:
        m = BY[key]
        widths = sorted(int(w) for w in m["srcs"])
        srcset = ", ".join(f'assets/{m["srcs"][str(w)]} {w}w' for w in widths)
        big = m["srcs"][str(widths[-1])]
        pic = (f'<figure class="pic clip"><img src="assets/{big}" srcset="{srcset}" '
               f'sizes="(max-width:820px) 100vw, 56vw" alt="{html.escape(m["caption"])}" '
               f'style="background:url({m["lqip"]}) center/cover no-repeat" '
               f'loading="lazy" decoding="async">'
               f'<figcaption>{html.escape(m["caption"])}</figcaption></figure>')
        txt = (f'<div class="txt"><p class="eyebrow">{eyebrow}</p>'
               f'<h3>{title}</h3><p class="lead">{body}</p></div>')
        # סדר ה-DOM קובע באיזה צד תופיע התמונה, וההחלפה יוצרת קצב מתחלף
        inner = (txt + pic) if rev else (pic + txt)
        A(f'<div class="row2 rv">{inner}</div>')
    A('</div></section>')

    # -------- segments
    A('<section id="segments"><div class="wrap">')
    A("""<div class="sec-head narrow rv"><p class="eyebrow">למי זה מתאים</p>
         <h2>אותו מתחם, 6 שימושים</h2>
         <p class="lead">לכל שימוש יש תמחור והיערכות אחרת. לחצו על מה שמתאים לכם,
            ותגיעו לטופס כשמטרת השהייה כבר מסומנת.</p></div>""")
    A('<div class="segs rv stag">')
    for key, cap, title, body in SEGMENTS:
        purpose = SEG_PURPOSE.get(title, "")
        A(f"""<article class="seg" data-purpose="{purpose}" role="button" tabindex="0"
        aria-label="{title}: מעבר לטופס בדיקת התאריכים">{img(key, '(max-width:700px) 100vw, (max-width:1080px) 50vw, 33vw')}
      <div class="seg-in"><span class="cap">{cap}</span><h3>{title}</h3><p>{body}</p>
        <span class="seg-go" aria-hidden="true">לבדיקת תאריכים</span></div>
    </article>""")
    A('</div></div></section>')

    # -------- שירותים שאפשר להוסיף
    A(f"""
<section id="services" style="background:var(--paper-2)"><div class="wrap">
  <div class="sec-head narrow rv">
    <p class="eyebrow">תוספות</p>
    <h2>מה אפשר להוסיף לשהייה</h2>
    <p class="lead">המתחם עצמו כלול במחיר. את אלה מזמינים מראש והם מגיעים
       אליכם. כל תוספת מתומחרת בהצעה אישית, לפי מה שאתם מתכננים.</p>
  </div>
  <div class="svcs rv stag">
    <article class="svc" data-service="שף פרטי" role="button" tabindex="0"
             aria-label="שף פרטי: מעבר לטופס">
      {img('svc-chef', '(max-width:700px) 100vw, (max-width:1080px) 50vw, 25vw')}
      <div class="svc-in"><h3>שף פרטי</h3>
        <p>תפריט שנבנה אתכם, מבושל ומוגש במקום. מארוחת ערב אחת ועד
           אירוח מלא לאורך היום.</p>
        <span class="svc-go">לבקשת הצעה</span></div>
    </article>
    <article class="svc" data-service="עיסוי וספא" role="button" tabindex="0"
             aria-label="עיסוי וספא: מעבר לטופס">
      {img('svc-spa', '(max-width:700px) 100vw, (max-width:1080px) 50vw, 25vw')}
      <div class="svc-in"><h3>עיסוי וספא</h3>
        <p>מטפלת מגיעה למתחם עם מיטת טיפולים. אפשר גם על המרפסת העליונה,
           מול הנוף.</p>
        <span class="svc-go">לבקשת הצעה</span></div>
    </article>
    <article class="svc" data-service="מוזיקה חיה" role="button" tabindex="0"
             aria-label="מוזיקה חיה: מעבר לטופס">
      {img('svc-band', '(max-width:700px) 100vw, (max-width:1080px) 50vw, 25vw')}
      <div class="svc-in"><h3>מוזיקה חיה</h3>
        <p>הרכב אקוסטי שמנגן בחצר. מתאים לאירוע, לשבת חתן ולערב שקט
           באותה מידה.</p>
        <span class="svc-go">לבקשת הצעה</span></div>
    </article>
    <article class="svc" data-service="עיצוב ואווירה" role="button" tabindex="0"
             aria-label="עיצוב ואווירה: מעבר לטופס">
      {img('svc-decor', '(max-width:700px) 100vw, (max-width:1080px) 50vw, 25vw')}
      <div class="svc-in"><h3>עיצוב ואווירה</h3>
        <p>נרות, כלים וסידור שולחן. אותו מתחם מקבל אופי אחר לגמרי
           כשמעצבים אותו לאירוע.</p>
        <span class="svc-go">לבקשת הצעה</span></div>
    </article>
  </div>
  <p class="svc-note rv">אין מחירון קבוע לתוספות. ספרו לנו מה מעניין אתכם
     ותקבלו הצעה מותאמת.</p>
</div></section>""")

    # -------- signature scroll-scrub (drone sequence)
    seqdir = os.path.join(ROOT, "assets", "seq")
    if os.path.exists(os.path.join(seqdir, "seq.json")):
        sq = json.load(open(os.path.join(seqdir, "seq.json"), encoding="utf-8"))
        A(f"""
<section class="scrub" id="scrub" data-frames="{sq['count']}" data-w="{sq['w']}" data-h="{sq['h']}">
  <div class="scrub-pin">
    <canvas id="scrubc" width="{sq['w']}" height="{sq['h']}"
            style="background:url({sq['lqip']}) center/cover no-repeat"
            aria-label="צילום רחפן מעל גבעת אולגה"></canvas>
    <div class="veil"></div>
    <div class="scrub-txt">
      <div class="step" data-at="0.06">
        <p class="eyebrow">גבעת אולגה</p>
        <h2>הים במרחק הליכה</h2>
        <p>הטיילת של גבעת אולגה מתחילה כמה רחובות מכאן.</p>
      </div>
      <div class="step" data-at="0.42">
        <p class="eyebrow">המיקום</p>
        <h2>בין נתניה לחיפה</h2>
        <p>דקות נסיעה מכביש 2 ומכביש 4.</p>
      </div>
      <div class="step" data-at="0.78">
        <p class="eyebrow">המתחם</p>
        <h2>וילה אחת בתוך כל זה</h2>
        <p>קבוצה אחת בכל פעם. אף אחד אחר בשטח.</p>
      </div>
    </div>
    <span class="hint">המשיכו לגלול</span>
  </div>
</section>""")

    # -------- a day here (horizontal scroll)
    DAYPANELS = [
        ("garden-path",  "07:00", "בוקר",   "קפה בחצר לפני שכולם קמים. השמש עוד נמוכה והמדשאה עדיין קרירה."),
        ("pool-deck",    "13:00", "צהריים", "הבריכה בשיאה. מקלחת חוץ, דק חם, ואין תור לשום דבר."),
        ("jacuzzi-dusk", "19:00", "שקיעה",  "עולים לקומה העליונה. הג׳קוזי דלוק והשמש נכנסת לים."),
        ("night-lounge", "23:00", "לילה",   "התאורה מתחלפת, המוזיקה נשארת, והשכנים רחוקים מספיק."),
    ]
    A('<section class="day" id="day">')
    A("""<div class="wrap"><div class="day-head rv">
         <div class="sec-head narrow" style="margin-bottom:0">
           <p class="eyebrow">יום אחד כאן</p>
           <h2>מהקפה הראשון ועד אחרי חצות</h2>
           <p class="lead">אותו מתחם נראה אחרת בכל שעה, וכולן שלכם.</p></div>
         <div class="day-nav">
           <button id="dayPrev" aria-label="לפאנל הקודם">&#8250;</button>
           <button id="dayNext" aria-label="לפאנל הבא">&#8249;</button>
         </div></div></div>""")
    A('<div class="track" id="track" tabindex="0" aria-label="שעות היום במתחם, גלילה לצדדים">')
    for key, hour, title, body in DAYPANELS:
        m = BY[key]
        widths = sorted(int(w) for w in m["srcs"])
        srcset = ", ".join(f'assets/{m["srcs"][str(w)]} {w}w' for w in widths)
        A(f"""<article class="panel">
      <img src="assets/{m['srcs'][str(widths[0])]}" srcset="{srcset}"
           sizes="(max-width:700px) 80vw, 29vw" alt="{html.escape(title)} במתחם"
           style="background:url({m['lqip']}) center/cover no-repeat"
           loading="lazy" decoding="async">
      <div class="p-in"><span class="hour num">{hour}</span><h3>{title}</h3><p>{body}</p></div>
    </article>""")
    A('</div>')
    A('<p class="dayhint">גללו לצדדים כדי לראות את שאר השעות</p>')
    A('</section>')

    # -------- mid-page conversion band
    A(f"""
<section class="band rv" style="padding:0">
  {img('pool-night', '100vw')}
  <div class="band-in">
    <h2>התאריך שאתם רוצים עוד פנוי?</h2>
    <p>יש כאן וילה אחת בלבד, ולכן כל תאריך נמסר פעם אחת. הבדיקה בלוח לוקחת פחות מדקה.</p>
    <a class="btn" href="#book">בדיקת תאריכים</a>
  </div>
</section>""")

    # -------- amenities
    A('<section id="amenities" style="background:var(--paper-2)"><div class="wrap">')
    A("""<div class="sec-head narrow rv"><p class="eyebrow">מה יש במקום</p>
         <h2>הרשימה המלאה</h2>
         <p class="lead">כל מה שברשימה נמצא בתוך הגדר וכלול בשהייה,
            בלי תוספת תשלום ובלי לצאת מהמתחם.</p></div>""")
    A('<div class="amen rv stag">')
    for title, items in AMENITIES:
        lis = "".join(f"<li>{i}</li>" for i in items)
        A(f'<div><h3>{title}</h3><ul>{lis}</ul></div>')
    A('</div></div></section>')

    # -------- gallery
    A('<section id="gallery"><div class="wrap">')
    A(f"""<div class="sec-head narrow rv"><p class="eyebrow">גלריה</p>
         <h2>{len(GALLERY)} תמונות מהמתחם</h2>
         <p class="lead">כולן צולמו במקום עצמו, בלי תמונות סטוק. לחיצה על תמונה
            פותחת אותה בגודל מלא.</p></div>""")
    A('<div class="gal" id="gal">')
    for i, k in enumerate(GALLERY):
        A(gal_item(k, i))
    A('</div></div></section>')

    # -------- reviews
    A('<section id="reviews" style="background:var(--paper-2)"><div class="wrap">')
    A(f"""<div class="sec-head narrow rv"><p class="eyebrow">אורחים</p>
         <h2>14 ביקורות, כולן בציון מלא</h2>
         <p class="lead">9 ב-<a href="{URL_AIRBNB}" target="_blank" rel="noopener">Airbnb</a>,
            3 ב-<a href="{URL_BOOKING}" target="_blank" rel="noopener">Booking.com</a>
            ו-2 ב-<a href="{URL_MIT}" target="_blank" rel="noopener">mit4mit</a>.
            כולן פורסמו שם ואפשר לקרוא אותן במקור.</p></div>""")
    A('<div class="revs rv stag">')
    for name, ctx, src, url, text in REVIEWS:
        A(f"""<div class="rev"><div class="stars" aria-label="5 מתוך 5 כוכבים">★★★★★</div>
      <blockquote>{text}</blockquote>
      <cite><b>{name}</b>{ctx} ·
        <a href="{url}" target="_blank" rel="noopener">{src}</a></cite></div>""")
    A('</div><div class="scores rv stag">')
    for v, l in SCORES:
        A(f'<div class="score"><b class="num">{v}</b><small>{l}</small></div>')
    A('</div></div></section>')

    # -------- pricing
    A('<section id="pricing"><div class="wrap">')
    A("""<div class="sec-head narrow rv"><p class="eyebrow">מחירים</p>
         <h2>מחיר אחד, לווילה כולה</h2>
         <p class="lead">הבריכה, הג׳קוזי, החצר וחדר המשחקים כלולים במחיר ואין עליהם
            תוספת. המחירים בטבלה הם לעד 10 אורחים. אירועים, חגים וחופשות מתומחרים
            בנפרד.</p></div>""")
    A(f"""<div class="split rv" style="align-items:start">
      <div>
        <table class="ptable">
          <caption class="sr-only">מחירון לינה בווילה</caption>
          <tr><th>סוג לילה</th><th style="text-align:end">מחיר ללילה</th></tr>
          <tr><td>אמצע שבוע · ראשון עד חמישי</td><td class="num">5,500 ₪</td></tr>
          <tr><td>סופ״ש · שישי ושבת</td><td class="num">6,400 ₪</td></tr>
          <tr><td>מבוגר נוסף מעל 10 אורחים</td><td class="num">350 ₪</td></tr>
          <tr><td>ילד נוסף מעל 10 אורחים</td><td class="num">250 ₪</td></tr>
          <tr><td>אירוע עד 50 איש</td><td class="pword">בהצעה אישית</td></tr>
          <tr><td>חגים וחופשות</td><td class="pword">תמחור נפרד</td></tr>
        </table>
        <p class="muted" style="font-size:.88rem;margin-top:20px">
          להתארגנות כלה יש מחירים מיוחדים. המחיר הסופי מאושר מול המארחים
          לפני התשלום.</p>
      </div>
      <div>{img('pool-above', '(max-width:900px) 100vw, 46vw', cap=True)}</div>
    </div></div></section>""")

    # -------- הזמנה: לוח, פרטים ומחיר בסקציה אחת
    # קודם היו שתי סקציות נפרדות שעשו כמעט אותו דבר: "מה פנוי בפועל"
    # עם לוח, ו"בדיקת זמינות ומחיר" עם שדות תאריך משלה. הכותרת השנייה
    # אפילו תיארה את מה שהראשונה עושה. עכשיו זו זרימה אחת.
    has_cal = os.path.exists(os.path.join(ROOT, "assets", "availability.json"))
    A(f"""
<section class="book" id="book"><div class="wrap">
  <div class="sec-head narrow rv">
    <p class="eyebrow">הזמנה</p>
    <h2>מתי אתם רוצים להגיע?</h2>
    <p class="lead">הלוח מראה מה באמת פנוי, והמחיר מתעדכן מיד עם הבחירה.
       שליחת הבקשה לא מחייבת אתכם בכלום.</p>
  </div>""")

    if has_cal:
        A("""
  <div class="cal rv" id="cal">
    <div class="cal-top">
      <p class="cal-hint" id="calHint">לחצו על תאריך הכניסה</p>
      <button type="button" class="cal-clr" id="calClear" hidden>שינוי תאריכים</button>
      <div class="cal-nav">
        <button type="button" id="calPrev" aria-label="לחודשים הקודמים">&#8250;</button>
        <button type="button" id="calNext" aria-label="לחודשים הבאים">&#8249;</button>
      </div>
    </div>
    <div class="cal-wrap" id="calWrap"></div>
    <div class="cal-foot">
      <div class="legend">
        <span><i class="sw-free"></i>פנוי</span>
        <span><i class="sw-busy"></i>תפוס</span>
        <span><i class="sw-sel"></i>הבחירה שלכם</span>
      </div>
      <p class="cal-note" id="calNote"></p>
    </div>
  </div>
  <p class="cal-warn" id="calWarn" role="alert"></p>
  <p class="sr-only" id="calLive" role="status" aria-live="polite"></p>""")

    A(f"""
  <div class="bookgrid rv">
    <form id="bookform" autocomplete="on" novalidate>
      <!-- שדות התאריך גלויים כברירת מחדל וגם עובדים בלי JS.
           כשהלוח עולה בהצלחה, הוא לוקח את התפקיד והם נסגרים. -->
      <div class="datefields" id="dateFields">
        <div class="two">
          <div class="field"><label for="ci">תאריך כניסה</label>
            <input type="date" id="ci" required></div>
          <div class="field"><label for="co">תאריך יציאה</label>
            <input type="date" id="co" required></div>
        </div>
      </div>
      <div class="two">
        {stepper('ad', 'מבוגרים', 8, 1, 30)}
        {stepper('ch', 'ילדים', 0, 0, 15)}
      </div>
      <div class="field"><label for="pu">מה מתוכנן?</label>
        <select id="pu">
          <option>לינה משפחתית</option>
          <option>נופש עם חברים</option>
          <option>אירוע פרטי</option>
          <option>התארגנות כלה</option>
          <option>יום גיבוש לחברה</option>
          <option>מסיבת רווקים / רווקות</option>
          <option>חופשה זוגית</option>
        </select></div>
      <div class="field"><label for="nm">שם מלא</label>
        <input type="text" id="nm" required autocomplete="name" autocapitalize="words"></div>
      <div class="field"><label for="ph">טלפון</label>
        <input type="tel" id="ph" required autocomplete="tel" inputmode="tel"
               placeholder="050-0000000"></div>
      <div class="field"><label for="nt">הערות<span class="sh">לא חובה</span></label>
        <textarea id="nt" rows="2" placeholder="שעת הגעה, אירוע מיוחד, בקשה מהמארחים"></textarea></div>
      <button class="btn" type="submit" id="send">שליחת בקשה בוואטסאפ</button>
      <p class="formerr" id="formErr" role="alert"></p>
      <p class="callalt">מעדיפים לדבר? <a href="tel:+{PHONE_INTL}" class="num">{PHONE_DISP}</a></p>
    </form>
    <div class="quote" id="quote" aria-live="polite">
      <div class="empty" id="qEmpty">בחרו תאריכים והמחיר יופיע כאן</div>
      <div id="qBody" hidden></div>
    </div>
  </div>
</div></section>
""")

    # -------- location + faq
    # נתונים מובנים לשאלות הנפוצות. גוגל מציג אותם כתוצאה עשירה,
    # וזה תופס שטח בעמוד התוצאות בלי לשלם על פרסום.
    faq_ld = ",".join(
        json.dumps({"@type": "Question", "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}},
                   ensure_ascii=False)
        for q, a in FAQ)
    A(f"""
<section id="location"><div class="wrap">
  <div class="split rv">
    <div>
      <p class="eyebrow">מיקום</p>
      <h2 style="margin-bottom:18px">גבעת אולגה, בין נתניה לחיפה</h2>
      <p class="lead">הווילה נמצאת בשכונת {ADDRESS} בחדרה, ברחוב שקט,
         במרחק הליכה מהים ומהטיילת.</p>
      <p>הכניסה לכביש 2 ולכביש 4 במרחק כמה דקות נסיעה. הכתובת המדויקת
         נשלחת עם אישור ההזמנה.</p>
      <table class="ptable" style="margin-top:22px">
        <caption class="sr-only">זמני נסיעה מהווילה</caption>
        <tr><th>יעד</th><th style="text-align:end">זמן נסיעה</th></tr>
        <tr><td>קיסריה</td><td class="num">12 דק׳</td></tr>
        <tr><td>נתניה</td><td class="num">20 דק׳</td></tr>
        <tr><td>חיפה</td><td class="num">40 דק׳</td></tr>
        <tr><td>תל אביב</td><td class="num">45 דק׳</td></tr>
      </table>
      <p style="margin-top:26px">
        <a class="btn ghost" target="_blank" rel="noopener"
           href="https://www.google.com/maps/search/?api=1&query=%D7%92%D7%91%D7%A2%D7%AA+%D7%90%D7%95%D7%9C%D7%92%D7%94+%D7%97%D7%93%D7%A8%D7%94">
          פתיחת האזור במפות גוגל</a></p>
    </div>
    <div>{img('sunset-sea', '(max-width:900px) 100vw, 50vw', cap=True)}</div>
  </div>
</div></section>

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
</script>

<section id="faq" style="background:var(--paper-2)"><div class="wrap narrow">
  <div class="sec-head rv"><p class="eyebrow">שאלות</p><h2>לפני שאתם שואלים</h2></div>
  <div class="faq rv">
    {''.join(f'<details><summary>{q}</summary><div class="a">{a}</div></details>' for q, a in FAQ)}
  </div>
</div></section>

</main>

<footer>
  <div class="wrap">
    <div class="fgrid">
      <div>
        <div class="brand" style="font-family:var(--serif)">אולגה ריזורט</div>
        <p style="max-width:34ch">וילה פרטית אחת בגבעת אולגה. בריכה מחוממת כל השנה,
           ג׳קוזי מול הים, וטיילת במרחק הליכה.</p>
      </div>
      <div>
        <h3>יצירת קשר</h3>
        <ul>
          <li><a href="tel:+{PHONE_INTL}" class="num">{PHONE_DISP}</a></li>
          <li><a href="https://wa.me/{PHONE_INTL}" target="_blank" rel="noopener">וואטסאפ</a></li>
          <li>{ADDRESS}</li>
          <li>המארחים: דוד וולריה</li>
        </ul>
      </div>
      <div>
        <h3>גם כאן</h3>
        <ul>
          <li><a href="{URL_AIRBNB}" target="_blank" rel="noopener">Airbnb</a></li>
          <li><a href="{URL_BOOKING}" target="_blank" rel="noopener">Booking.com</a></li>
          <li><a href="{URL_INSTA}" target="_blank" rel="noopener">אינסטגרם</a></li>
          <li><a href="{URL_MIT}" target="_blank" rel="noopener">mit4mit</a></li>
        </ul>
      </div>
    </div>
    <div class="fbot">
      <span>© אולגה ריזורט</span>
      <span>עד 17 אורחים ללינה · עד 50 לאירוע · שמירת שבת</span>
    </div>
  </div>
</footer>

<a class="wa" href="https://wa.me/{PHONE_INTL}" target="_blank" rel="noopener"
   aria-label="שליחת הודעה בוואטסאפ">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.12-.41-2.13-1.31-.79-.7-1.32-1.57-1.47-1.87-.15-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.01-1.04 2.47 0 1.46 1.06 2.87 1.21 3.07.15.2 2.09 3.19 5.06 4.35 2.47.96 2.97.77 3.51.72.54-.05 1.75-.71 2-1.41.25-.7.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.02 21.5h-.01a9.45 9.45 0 01-4.8-1.31l-.35-.2-3.57.93.96-3.48-.22-.36a9.42 9.42 0 01-1.45-5.04c0-5.21 4.25-9.45 9.46-9.45 2.53 0 4.9.99 6.68 2.77a9.38 9.38 0 012.77 6.69c0 5.21-4.25 9.45-9.47 9.45zM20.46 3.52A11.78 11.78 0 0012.02 0C5.5 0 .2 5.3.2 11.81c0 2.08.54 4.11 1.57 5.9L0 24l6.43-1.69a11.76 11.76 0 005.59 1.42h.01c6.51 0 11.81-5.3 11.81-11.81 0-3.16-1.23-6.12-3.38-8.4z"/></svg>
</a>

<div class="cursor" id="cursor" aria-hidden="true">הגדל</div>

<div class="sticky">
  <div class="p"><b class="num">מ־5,500 ₪ ללילה</b>הווילה כולה, עד 10 אורחים</div>
  <a href="#book">בדיקת תאריכים</a>
</div>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="תצוגת תמונה">
  <button class="x" aria-label="סגירת התמונה">&times;</button>
  <span class="count num" id="lbCount"></span>
  <button class="nav prev" aria-label="לתמונה הקודמת">&#8250;</button>
  <button class="nav next" aria-label="לתמונה הבאה">&#8249;</button>
  <img id="lbImg" alt="" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7">
  <div class="cap" id="lbCap"></div>
</div>

<script>window.WA="{PHONE_INTL}";</script>
<script src="app.js?v={ver('app.js')}" defer></script>
</body>
</html>
""")

    out = os.path.join(ROOT, "index.html")
    open(out, "w", encoding="utf-8").write("\n".join(P))
    print(f"wrote {out}  ({os.path.getsize(out)//1024}KB)")

    # robots ו-sitemap נוצרים כאן ולא ביד, כדי שלא ייצאו מסונכרנים
    # מה-canonical אם הדומיין ישתנה יום אחד.
    from datetime import date
    base = SITE_URL
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        # בתצוגה מקדימה חוסמים סריקה לגמרי: היא לא אמורה להתחרות
        # באתר האמיתי בגוגל, וגם לא להישאר באינדקס אחריו.
        f.write("User-agent: *\nDisallow: /\n" if PREVIEW
                else f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f'  <url><loc>{base}</loc><lastmod>{date.today()}</lastmod>'
                '<changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
                '</urlset>\n')
    print("wrote robots.txt, sitemap.xml")


if __name__ == "__main__":
    build()
