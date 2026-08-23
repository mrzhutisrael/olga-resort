/* ==========================================================================
   Olga Resort · התנהגות האתר
   בלי ספריות חיצוניות. הכל vanilla, עובד גם מקובץ מקומי.
   ========================================================================== */

/* מרחב משותף קטן. לוח הזמינות נטען אסינכרונית, ומחשבון המחיר צריך
   לדעת אילו לילות תפוסים כדי לא לתמחר תאריך שכבר נמכר. */
window.OLGA = { busy: null };

/* תאריכים: המרה מקומית ולא דרך UTC.
   toISOString מתרגם לזמן גריניץ׳, ובישראל (UTC+3) חצות מקומי הוא
   21:00 של אתמול. זה גרם ל-min של שדה הכניסה להיות אתמול, ולזיהוי
   שגוי של סופי שבוע אצל גולשים מחוץ לישראל. */
const ISO = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}` +
                 `-${String(d.getDate()).padStart(2, '0')}`;
const PARSE = s => { const [y, m, d] = String(s).split('-').map(Number);
                     return new Date(y, (m || 1) - 1, d || 1); };
/* תאריך לתצוגה. ISO הוא פורמט למכונה; בישראל קוראים 10.10.2026. */
const HEDATE = s => { const [y, m, d] = String(s).split('-'); return `${d}.${m}.${y}`; };

(() => {
'use strict';

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ---------------- header ---------------- */
const hdr = $('#hdr');
const onScroll = () => hdr.classList.toggle('solid', scrollY > 60);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

/* ---------------- mobile nav ---------------- */
const burger = $('#burger'), nav = $('#nav');
function setNav(open) {
  nav.classList.toggle('open', open);
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  burger.setAttribute('aria-label', open ? 'סגירת התפריט' : 'פתיחת התפריט');
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) nav.querySelector('a')?.focus({ preventScroll: true });
}
burger.addEventListener('click', () => setNav(!nav.classList.contains('open')));
$$('#nav a').forEach(a => a.addEventListener('click', () => setNav(false)));
addEventListener('keydown', e => {
  if (e.key === 'Escape' && nav.classList.contains('open')) { setNav(false); burger.focus(); }
});

/* ---------------- reveal on scroll ---------------- */
const io = new IntersectionObserver(es => {
  es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
$$('.rv').forEach(el => io.observe(el));

/* ---------------- lightbox ---------------- */
const lb = $('#lb'), lbImg = $('#lbImg'), lbCap = $('#lbCap'), lbCount = $('#lbCount');
const figs = $$('#gal figure');
let idx = 0, lastFocus = null;

function show(i) {
  idx = (i + figs.length) % figs.length;
  const f = figs[idx];
  lbImg.src = f.dataset.full;
  lbImg.alt = lbCap.textContent = f.dataset.cap || '';
  lbCount.textContent = `${idx + 1} / ${figs.length}`;
}
function openLb(i) {
  lastFocus = document.activeElement;
  show(i); lb.classList.add('on'); document.body.style.overflow = 'hidden';
  $('.lb .x').focus({ preventScroll: true });
}
function closeLb() {
  lb.classList.remove('on'); document.body.style.overflow = '';
  // מחזירים את המיקוד לתמונה שממנה נפתח, ולא לראש הדף
  lastFocus?.focus?.({ preventScroll: true });
}
figs.forEach((f, i) => {
  f.addEventListener('click', () => openLb(i));
  f.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLb(i); }
  });
});
$('.lb .x').addEventListener('click', closeLb);
// בעברית החץ ״הבא״ מצביע שמאלה, ולכן הכפתורים הפוכים מהאינטואיציה הלטינית
$('.lb .next').addEventListener('click', e => { e.stopPropagation(); show(idx + 1); });
$('.lb .prev').addEventListener('click', e => { e.stopPropagation(); show(idx - 1); });
lb.addEventListener('click', e => { if (e.target === lb || e.target === lbImg) closeLb(); });
addEventListener('keydown', e => {
  if (!lb.classList.contains('on')) return;
  if (e.key === 'Escape') return closeLb();
  if (e.key === 'ArrowLeft')  return show(idx + 1);
  if (e.key === 'ArrowRight') return show(idx - 1);
  // כליאת המיקוד: בלעדיה Tab בורח אל הדף שמאחורי החלון
  if (e.key === 'Tab') {
    const f = $$('button', lb);
    const i = f.indexOf(document.activeElement);
    e.preventDefault();
    f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
  }
});
// החלקה במגע
let tx = 0;
lb.addEventListener('touchstart', e => tx = e.touches[0].clientX, { passive: true });
lb.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - tx;
  if (Math.abs(dx) > 45) show(idx + (dx > 0 ? -1 : 1));
}, { passive: true });

/* ---------------- בוררי כמות ----------------
   מחליפים <select> בן 30 שורות. הכפתורים מחוץ לסדר ה-Tab בכוונה:
   הם משכפלים את חצי המקלדת שכבר עובדים על input[type=number]. */
$$('.stepper').forEach(box => {
  const inp = box.querySelector('input');
  const dec = box.querySelector('.sdec'), inc = box.querySelector('.sinc');
  const lo = +box.dataset.lo, hi = +box.dataset.hi;
  const sync = () => {
    let v = Math.round(+inp.value);
    if (!isFinite(v)) v = lo;
    v = Math.max(lo, Math.min(hi, v));
    if (String(v) !== inp.value) inp.value = v;
    dec.disabled = v <= lo; inc.disabled = v >= hi;
  };
  const bump = n => {
    inp.value = Math.round(+inp.value || lo) + n;
    sync();
    inp.dispatchEvent(new Event('change', { bubbles: true }));
  };
  dec.addEventListener('click', () => bump(-1));
  inc.addEventListener('click', () => bump(1));
  inp.addEventListener('input', sync);
  inp.addEventListener('change', sync);
  sync();
});

/* ---------------- price calculator ---------------- */
const RATE_MID = 5500, RATE_WEEKEND = 6400;
const EXTRA_ADULT = 350, EXTRA_CHILD = 250, BASE_GUESTS = 10;
const MAX_SLEEP = 17;

const ci = $('#ci'), co = $('#co'), ad = $('#ad'), ch = $('#ch'),
      pu = $('#pu'), nm = $('#nm'), ph = $('#ph'), nt = $('#nt');
const qEmpty = $('#qEmpty'), qBody = $('#qBody'), sendBtn = $('#send'), formErr = $('#formErr');
const SEND_LABEL = 'שליחת בקשה בוואטסאפ';

const nfmt = n => n.toLocaleString('en-US');
// עברית לא סופרת כמו אנגלית: "1 לילות" שגוי, וגם "2 לילות" פחות טבעי מ"שני לילות"
const nights_he = n => n === 1 ? 'לילה אחד' : n === 2 ? 'שני לילות' : `${n} לילות`;
const guests_he = n => n === 1 ? 'אורח אחד' : `${n} אורחים`;
const today = new Date(); today.setHours(0, 0, 0, 0);
ci.min = co.min = ISO(today);

ci.addEventListener('change', () => {
  // הצ׳ק־אאוט לא יכול להיות לפני הצ׳ק־אין
  const d = PARSE(ci.value);
  if (ci.value && !isNaN(d)) {
    d.setDate(d.getDate() + 1);
    co.min = ISO(d);
    if (!co.value || co.value <= ci.value) co.value = ISO(d);
  }
  calc();
});

function nightsBetween(a, b) {
  const out = [];
  const d = new Date(a);
  while (d < b) { out.push(new Date(d)); d.setDate(d.getDate() + 1); }
  return out;
}

/** אילו מהלילות בטווח כבר תפוסים לפי לוח הזמינות. ליל היציאה לא נספר. */
function blockedNights(a, b) {
  const busy = window.OLGA.busy;
  if (!busy || !busy.size) return [];
  const out = [];
  for (const d = new Date(a); d < b; d.setDate(d.getDate() + 1)) {
    const k = ISO(d);
    if (busy.has(k)) out.push(k);
  }
  return out;
}

function setSend(enabled, total) {
  sendBtn.disabled = !enabled;
  sendBtn.innerHTML = enabled && total != null
    ? `${SEND_LABEL} · <span class="num">${nfmt(total)} ₪</span>`
    : SEND_LABEL;
}

function calc() {
  const a = PARSE(ci.value), b = PARSE(co.value);
  const ok = ci.value && co.value && !isNaN(a) && !isNaN(b) && b > a;
  qEmpty.hidden = ok;
  qBody.hidden = !ok;
  formErr.classList.remove('on');
  if (!ok) { setSend(false); return; }

  // תאריך שכבר נמכר לא אמור לקבל הצעת מחיר בכלל
  const taken = blockedNights(a, b);
  if (taken.length) {
    // התאמת מין ומספר: "לילה אחד תפוס" מול "3 לילות תפוסים"
    formErr.textContent = (taken.length === 1
      ? `הלילה של ${HEDATE(taken[0])} כבר תפוס.`
      : `${taken.length} מהלילות בטווח הזה כבר תפוסים (הראשון ${HEDATE(taken[0])}).`) +
      ' בחרו תאריכים אחרים בלוח הזמינות.';
    formErr.classList.add('on');
  }

  const ns = nightsBetween(a, b);
  // בישראל סוף השבוע הוא ליל שישי וליל שבת
  let mid = 0, wk = 0;
  ns.forEach(d => (d.getDay() === 5 || d.getDay() === 6) ? wk++ : mid++);

  const adults = Math.max(1, +ad.value || 1), kids = Math.max(0, +ch.value || 0);
  const guests = adults + kids;
  const over = Math.max(0, guests - BASE_GUESTS);
  // התוספת נספרת קודם על הילדים, כי היא הזולה מהשתיים
  const exKids = Math.min(kids, over);
  const exAd = over - exKids;

  const base = mid * RATE_MID + wk * RATE_WEEKEND;
  const extra = (exAd * EXTRA_ADULT + exKids * EXTRA_CHILD) * ns.length;
  const total = base + extra;

  const rows = [];
  if (mid) rows.push([`${nights_he(mid)} באמצע שבוע`, `${nfmt(mid * RATE_MID)} ₪`]);
  if (wk)  rows.push([`${nights_he(wk)} בסוף שבוע`, `${nfmt(wk * RATE_WEEKEND)} ₪`]);
  if (over) rows.push([`תוספת ${guests_he(over)} מעל ${BASE_GUESTS} · ${nights_he(ns.length)}`,
                       `${nfmt(extra)} ₪`]);

  let warn = '';
  if (guests > MAX_SLEEP) {
    warn = `<div class="note" style="color:#E8A99E">${MAX_SLEEP} אורחים הם המקסימום ללינה.
            לאירוע ללא לינה אפשר עד 50 איש, במחיר שנקבע בהצעה אישית.</div>`;
  }

  qBody.innerHTML = `
    <div class="row"><span>תאריכים</span>
      <span><span class="num">${HEDATE(ci.value)}</span> עד <span class="num">${HEDATE(co.value)}</span></span></div>
    <div class="row"><span>שהייה</span><span>${nights_he(ns.length)}</span></div>
    <div class="row"><span>אורחים</span>
      <span class="num">${adults} מבוגרים${kids ? ` + ${kids} ילדים` : ''}</span></div>
    ${rows.map(r => `<div class="row"><span>${r[0]}</span><span class="num">${r[1]}</span></div>`).join('')}
    <div class="row total"><span>סך הכל</span><span class="num">${nfmt(total)} ₪</span></div>
    ${warn}
    <div class="note">המחיר משוער ולא כולל חגים, חופשות ותוספות.
      דוד או ולריה מאשרים את המחיר הסופי לפני התשלום.</div>`;

  setSend(!taken.length, total);
  return { total, nightsCount: ns.length, guests, adults, kids };
}

[co, ad, ch].forEach(el => el.addEventListener('change', calc));

/* הלוח מציג מחיר ברגע שנבחר טווח, ולכן הוא צריך גישה לתמחור.
   מחזיר טקסט מוכן להצגה ולא רק מספר, כדי שהפורמט יישאר במקום אחד. */
window.OLGA.quote = (aIso, bIso) => {
  const a = PARSE(aIso), b = PARSE(bIso);
  if (!(b > a)) return null;
  const ns = nightsBetween(a, b);
  let mid = 0, wk = 0;
  ns.forEach(d => (d.getDay() === 5 || d.getDay() === 6) ? wk++ : mid++);
  const adults = Math.max(1, +ad.value || 1), kids = Math.max(0, +ch.value || 0);
  const over = Math.max(0, adults + kids - BASE_GUESTS);
  const exKids = Math.min(kids, over), exAd = over - exKids;
  const total = mid * RATE_MID + wk * RATE_WEEKEND +
                (exAd * EXTRA_ADULT + exKids * EXTRA_CHILD) * ns.length;
  return { total, nights: ns.length, text: nfmt(total) + ' ₪' };
};
// לוח הזמינות נטען אחרי הטופס. כשהוא מגיע, מתמחרים מחדש.
addEventListener('olga:availability', () => calc());

/* ---------------- submit to WhatsApp ---------------- */
$('#bookform').addEventListener('submit', e => {
  e.preventDefault();
  const r = calc();
  if (!r) return;

  // אימות ידני עם הודעה בעברית. novalidate על הטופס מונע את בועית
  // ברירת המחדל של הדפדפן, שמופיעה באנגלית ונעלמת מיד.
  const miss = [];
  if (!nm.value.trim()) miss.push('שם');
  if (ph.value.replace(/\D/g, '').length < 9) miss.push('טלפון תקין');
  if (miss.length) {
    formErr.textContent = `חסר ${miss.join(' ו')}.`;
    formErr.classList.add('on');
    (miss[0] === 'שם' ? nm : ph).focus();
    return;
  }
  if (sendBtn.disabled) return;

  const lines = [
    'היי, הגעתי מהאתר של אולגה ריזורט.',
    '',
    `שם: ${nm.value.trim()}`,
    `טלפון: ${ph.value.trim()}`,
    `מטרה: ${pu.value}`,
    `תאריכים: ${HEDATE(ci.value)} עד ${HEDATE(co.value)} (${nights_he(r.nightsCount)})`,
    `אורחים: ${r.adults} מבוגרים${r.kids ? ` + ${r.kids} ילדים` : ''}`,
    `הערכת מחיר מהאתר: ${nfmt(r.total)} ש"ח`,
  ];
  if (nt.value.trim()) lines.push('', `הערות: ${nt.value.trim()}`);
  lines.push('', 'אפשר לדעת אם התאריכים האלה פנויים?');
  location.href = `https://wa.me/${window.WA}?text=${encodeURIComponent(lines.join('\n'))}`;
});

calc();
})();

/* ==========================================================================
   שכבה שנייה: תנועה מונעת גלילה והמרה
   ========================================================================== */
(() => {
'use strict';
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------------- ירו: החלפת תמונות עם זום איטי ---------------- */
const stack = $$('.hero-stack img');
if (stack.length) {
  stack[0].classList.add('on');
  // התמונות 2 ו-3 נשלחו בלי src כדי לא לטעון 1MB מיותר בצביעה
  // הראשונה. מאכלסים אותן אחרי שהדף נטען, הרבה לפני שהרוטציה
  // מגיעה אליהן בשנייה השביעית.
  const fill = () => stack.slice(1).forEach(im => {
    if (im.dataset.srcset) { im.srcset = im.dataset.srcset; delete im.dataset.srcset; }
    if (im.dataset.src)    { im.src    = im.dataset.src;    delete im.dataset.src; }
  });
  if (document.readyState === 'complete') setTimeout(fill, 400);
  else addEventListener('load', () => setTimeout(fill, 400), { once: true });
  if (!REDUCED && stack.length > 1) {
    let i = 0;
    // 7 שניות לתמונה. ה-keyframe של הזום ארוך יותר בכוונה,
    // כך שהזום ממשיך לזוז גם בזמן ההצלבה ואין קפיצה.
    setInterval(() => {
      stack[i].classList.remove('on');
      i = (i + 1) % stack.length;
      const next = stack[i];
      next.classList.remove('on');
      void next.offsetWidth;          // מאפס את האנימציה
      next.classList.add('on');
    }, 7000);
  }
}

/* ---------------- פרלקסה בירו + מחוון התקדמות ---------------- */
const hs = $('.hero-stack'), prog = $('.prog');
let raf = 0;
function frame() {
  raf = 0;
  const y = scrollY;
  if (hs && !REDUCED && y < innerHeight * 1.2) {
    hs.style.setProperty('--py', (y * 0.32) + 'px');
  }
  if (prog) {
    const h = document.documentElement.scrollHeight - innerHeight;
    prog.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
  }
}
addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(frame); },
                 { passive: true });
frame();

/* ---------------- חשיפת הירו בטעינה ---------------- */
requestAnimationFrame(() => $('.hero')?.classList.add('in'));

/* המספרים המתגלגלים הוסרו יחד עם רצועת המספרים בירו. הם היו האפקט
   היחיד שהשתמש בהם, ו-"5.0" שמטפס מ-0.0 קרא לעצמו תשומת לב בלי
   להוסיף מידע. */

/* ---------------- סקציית "יום אחד כאן" ----------------
   הגרסה הקודמת חטפה את הגלגלת והפכה גלילה אנכית לתנועה אופקית.
   זה לכד כל מי שרק רצה להמשיך למטה. עכשיו הגלילה טבעית לגמרי,
   ובמקומה יש חצים מפורשים ומקלדת. */
const track = $('#track');
if (track) {
  const panels = $$('.panel', track);
  const prev = $('#dayPrev'), next = $('#dayNext');

  // סימן ה-scrollLeft ב-RTL אינו אחיד בין דפדפנים, ולכן משווים בערך מוחלט
  const pos = () => Math.abs(track.scrollLeft);
  const max = () => track.scrollWidth - track.clientWidth;

  function sync() {
    // במסך רחב כל ארבעת הפאנלים נכנסים, ואז אין מה לגלול. הצגת חצים
    // מתים והנחיה "גללו לצדדים" נראית שבורה, ולכן שניהם נעלמים.
    const scrollable = max() > 8;
    track.closest('.day')?.classList.toggle('nofit', !scrollable);
    if (!prev || !next) return;
    prev.disabled = !scrollable || pos() < 6;
    next.disabled = !scrollable || pos() > max() - 6;
  }
  function nearest() {
    const mid = track.getBoundingClientRect().left + track.clientWidth / 2;
    let best = 0, bd = Infinity;
    panels.forEach((p, i) => {
      const r = p.getBoundingClientRect();
      const d = Math.abs(r.left + r.width / 2 - mid);
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }
  // scrollIntoView במקום חשבון scrollLeft: הוא עובד נכון בשני הכיוונים
  function go(n) {
    panels[Math.max(0, Math.min(panels.length - 1, n))]
      ?.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth',
                         inline: 'center', block: 'nearest' });
    // אירוע ה-scroll האחרון של גלילה חלקה לא תמיד מגיע, ואז מצב
    // הכפתורים נשאר תקוע על המיקום הקודם. שני סנכרונים מאוחרים סוגרים את זה.
    setTimeout(sync, 420); setTimeout(sync, 950);
  }

  prev?.addEventListener('click', () => go(nearest() - 1));
  next?.addEventListener('click', () => go(nearest() + 1));
  track.addEventListener('scroll', sync, { passive: true });
  if ('onscrollend' in track) track.addEventListener('scrollend', sync, { passive: true });
  addEventListener('resize', sync, { passive: true });
  sync();
}

/* ---------------- טופס הירו ----------------
   קודם ישבו כאן שני <input type="date">. הם פותחים את בורר מערכת
   ההפעלה, שהוא קטן, שונה בכל דפדפן, ובעיקר לא יודע אילו תאריכים
   כבר תפוסים. באותו עמוד כבר יש לוח שיודע בדיוק את זה, ולכן היו
   שני בוררים שסותרים זה את זה. עכשיו יש אחד, והירו מוביל אליו. */
const hb = $('#herobook');
if (hb) {
  const pushGuests = () => {
    const ad = $('#hbad'), dstAd = $('#ad');
    if (ad && dstAd && ad.value) {
      dstAd.value = ad.value;
      dstAd.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  /** מגלגל לסקציית ההזמנה ומעביר את תשומת הלב לבחירת התאריך.
      הגלילה חלקה, ולכן המיקוד מחכה לה: מיקוד באמצע גלילה חלקה
      קופץ באופן שנראה כמו תקלה. */
  const toBooking = () => {
    $('#book').scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth' });
    setTimeout(() => {
      const cal = $('#cal');
      if (cal) {
        cal.classList.add('ping');
        setTimeout(() => cal.classList.remove('ping'), 1400);
        // הלוח מנהל roving tabindex: התא היחיד עם tabindex=0 הוא
        // התאריך שכבר נבחר, או הראשון שאפשר לבחור.
        cal.querySelector('.d[data-d][tabindex="0"]')?.focus({ preventScroll: true });
      } else {
        $('#ci')?.focus({ preventScroll: true });
      }
    }, REDUCED ? 0 : 620);
  };

  $('#hbDates')?.addEventListener('click', () => { pushGuests(); toBooking(); });
  hb.addEventListener('submit', e => { e.preventDefault(); pushGuests(); toBooking(); });
}

/** מציג בירו את מה שנבחר בלוח, כדי שמי שגלל בחזרה למעלה יראה
    את הבחירה שלו ולא כפתור ריק. */
window.OLGA.showDates = (a, b) => {
  const el = $('#hbDatesVal'), btn = $('#hbDates');
  if (!el || !btn) return;
  if (a && b) {
    el.textContent = HEDATE(a) + ' עד ' + HEDATE(b);
    btn.classList.add('set');
  } else if (a) {
    el.textContent = 'כניסה ' + HEDATE(a);
    btn.classList.add('set');
  } else {
    el.textContent = 'בחירה בלוח';
    btn.classList.remove('set');
  }
};

/* ---------------- קלפי הסגמנטים מובילים לטופס ---------------- */
function pickSegment(card) {
  const want = card.dataset.purpose;
  const sel = $('#pu');
  if (sel) {
    const opt = [...sel.options].find(o => o.value === want || o.textContent.trim() === want);
    if (opt) { sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); }
  }
  $('#book').scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth' });
}
$$('[data-purpose]').forEach(card => {
  card.addEventListener('click', () => pickSegment(card));
  // הקלף הוגדר role="button" אבל לא הגיב למקלדת בכלל
  card.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pickSegment(card); }
  });
});

/* ---------------- סמן מותאם על הגלריה ---------------- */
const cur = $('#cursor'), gal = $('#gal');
if (cur && gal && matchMedia('(hover:hover)').matches) {
  gal.addEventListener('pointerenter', () => cur.classList.add('on'));
  gal.addEventListener('pointerleave', () => cur.classList.remove('on'));
  gal.addEventListener('pointermove', e => {
    cur.style.transform =
      `translate(${e.clientX}px,${e.clientY}px) translate(-50%,-50%) scale(1)`;
  });
}
})();

/* ==========================================================================
   מומנט החתימה: גלילה שמניעה רצף פריימים
   --------------------------------------------------------------------------
   מצייר על canvas ולא מחליף src של <img>, כי החלפת src מייצרת הבהוב
   בכל פריים. הפריימים נטענים רק כשמתקרבים לסקציה, ולא בטעינת הדף.
   ========================================================================== */
(() => {
'use strict';
const sec = document.querySelector('#scrub');
const cv  = document.querySelector('#scrubc');
if (!sec || !cv) return;

const N = +sec.dataset.frames;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const ctx = cv.getContext('2d', { alpha: false });
const imgs = new Array(N);
const steps = [...sec.querySelectorAll('.step')];
let loaded = 0, cur = -1, ready = false, raf = 0;

const src = i => `assets/seq/${String(i).padStart(3, '0')}.webp`;

function draw(i) {
  i = Math.max(0, Math.min(N - 1, i));
  if (i === cur) return;
  const im = imgs[i];
  if (!im || !im.complete || !im.naturalWidth) return;
  ctx.drawImage(im, 0, 0, cv.width, cv.height);
  cur = i;
}

function load() {
  if (ready) return;
  ready = true;
  // הפריים הראשון קודם, כדי שיהיה מה להראות מיד
  for (let i = 0; i < N; i++) {
    const im = new Image();
    im.decoding = 'async';
    im.onload = () => {
      loaded++;
      if (i === 0) draw(0);
      // כשהכל נטען מציירים את הפריים שמתאים למקום הגלילה הנוכחי
      if (loaded === N) { cur = -1; update(); }
    };
    im.src = src(i);
    imgs[i] = im;
  }
}

function progress() {
  const r = sec.getBoundingClientRect();
  const total = r.height - innerHeight;
  if (total <= 0) return 0;
  return Math.max(0, Math.min(1, -r.top / total));
}

function update() {
  raf = 0;
  const p = progress();
  draw(Math.round(p * (N - 1)));
  // הטקסט מתחלף לפי מקטעים, כך שכל שלב יושב על רגע אחר בתנועת הרחפן
  let active = -1;
  steps.forEach((s, i) => { if (p >= +s.dataset.at) active = i; });
  steps.forEach((s, i) => s.classList.toggle('on', i === active));
  sec.classList.toggle('done', p > 0.9);
}

if (REDUCED) {
  // בלי תנועה: פריים אחד סטטי וכל הטקסטים גלויים
  const im = new Image();
  im.onload = () => ctx.drawImage(im, 0, 0, cv.width, cv.height);
  im.src = src(Math.floor(N * 0.7));
  steps.forEach(s => s.classList.add('on'));
  return;
}

// טוענים רק כשהסקציה מתקרבת, לא בטעינת הדף
new IntersectionObserver((es, o) => {
  if (es[0].isIntersecting) { load(); o.disconnect(); }
}, { rootMargin: '120% 0px' }).observe(sec);

addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(update); },
                 { passive: true });
addEventListener('resize', () => { if (!raf) raf = requestAnimationFrame(update); },
                 { passive: true });
steps[0]?.classList.add('on');
})();

/* ==========================================================================
   קיר הרילס ושירותים נלווים
   --------------------------------------------------------------------------
   הסרטונים אנכיים (9:16) כי כך הם צולמו. הפוסטר נטען עם הדף, הווידאו
   עצמו נוצר רק בלחיצה, ולכן הסקציה עולה בכ-320KB ולא ב-36MB.
   ========================================================================== */
(() => {
'use strict';
const track = document.querySelector('#rtrack');
if (!track) return;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const cards = [...track.querySelectorAll('.reel')];
let playing = null;

function play(card) {
  if (card.classList.contains('playing')) return;
  stop();                                   // סרטון אחד בכל רגע
  const v = document.createElement('video');
  v.src = card.dataset.src;
  v.controls = true;
  v.autoplay = true;
  v.playsInline = true;
  v.preload = 'auto';
  v.poster = card.querySelector('img')?.src || '';
  card.appendChild(v);
  card.classList.add('playing');
  card.removeAttribute('role');
  card.removeAttribute('tabindex');
  playing = card;
  v.play().catch(() => { /* הדפדפן חסם הפעלה; יש controls */ });
  card.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth',
                        inline: 'center', block: 'nearest' });
}

function stop() {
  if (!playing) return;
  playing.querySelector('video')?.remove();
  playing.classList.remove('playing');
  playing.setAttribute('role', 'button');
  playing.setAttribute('tabindex', '0');
  playing = null;
}

cards.forEach(c => {
  c.addEventListener('click', e => {
    if (e.target.tagName === 'VIDEO') return;   // הקליק על הפקדים אינו לחיצה על הכרטיס
    play(c);
  });
  c.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(c); }
  });
});
addEventListener('keydown', e => { if (e.key === 'Escape') stop(); });

/* חצים, באותה לוגיקה של הסקציה האופקית: הסימן של scrollLeft ב-RTL
   אינו אחיד בין דפדפנים, ולכן משווים בערך מוחלט. */
const prev = document.querySelector('#reelPrev'), next = document.querySelector('#reelNext');
const pos = () => Math.abs(track.scrollLeft);
const max = () => track.scrollWidth - track.clientWidth;
function sync() {
  const scrollable = max() > 8;
  track.closest('.reels')?.classList.toggle('nofit', !scrollable);
  if (!prev || !next) return;
  prev.disabled = !scrollable || pos() < 6;
  next.disabled = !scrollable || pos() > max() - 6;
}
function nearest() {
  const mid = track.getBoundingClientRect().left + track.clientWidth / 2;
  let best = 0, bd = Infinity;
  cards.forEach((c, i) => {
    const r = c.getBoundingClientRect();
    const d = Math.abs(r.left + r.width / 2 - mid);
    if (d < bd) { bd = d; best = i; }
  });
  return best;
}
function go(n) {
  cards[Math.max(0, Math.min(cards.length - 1, n))]
    ?.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth',
                       inline: 'center', block: 'nearest' });
  // אירוע ה-scroll האחרון של גלילה חלקה לא תמיד מגיע
  setTimeout(sync, 420); setTimeout(sync, 950);
}
prev?.addEventListener('click', () => go(nearest() - 1));
next?.addEventListener('click', () => go(nearest() + 1));
track.addEventListener('scroll', sync, { passive: true });
if ('onscrollend' in track) track.addEventListener('scrollend', sync, { passive: true });
addEventListener('resize', sync, { passive: true });
sync();
})();

/* ---------------- כרטיסי השירותים ----------------
   לחיצה מעבירה לטופס ומוסיפה להערות את השירות שנבחר, כך שהבקשה
   מגיעה למארחים כשכתוב בה מה מעניין את הפונה. */
(() => {
'use strict';
const cards = [...document.querySelectorAll('[data-service]')];
if (!cards.length) return;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

function pick(card) {
  const want = card.dataset.service;
  const nt = document.querySelector('#nt');
  if (nt) {
    const line = 'מעניין אותנו: ' + want;
    const cur = nt.value.trim();
    // לא מוסיפים פעמיים את אותו שירות, ולא דורסים מה שהמשתמש כתב
    if (!cur.includes(want)) nt.value = cur ? cur + '\n' + line : line;
    nt.dispatchEvent(new Event('input', { bubbles: true }));
  }
  document.querySelector('#book')
    ?.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth' });
  setTimeout(() => document.querySelector('#nm')?.focus({ preventScroll: true }), 800);
}

cards.forEach(c => {
  c.addEventListener('click', () => pick(c));
  c.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(c); }
  });
});
})();

/* ==========================================================================
   לוח הזמינות
   --------------------------------------------------------------------------
   הנתון מגיע מ-assets/availability.json שנשלף מ-Airbnb.

   שלושה דברים שהופכים בורר תאריכים לנוח, וכולם היו חסרים כאן:
   1. תצוגה מקדימה בריחוף. אחרי בחירת כניסה רואים את הטווח לפני שלוחצים.
   2. פס רציף בין הקצוות במקום ריבועים מנותקים.
   3. מחיר מיד בבחירה, בלי לרדת לטופס כדי לגלות כמה זה עולה.
   ========================================================================== */
(() => {
'use strict';
const wrap = document.querySelector('#calWrap');
if (!wrap) return;

const $ = s => document.querySelector(s);
const DOW  = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ש'];
const DOWL = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];
const MON  = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני',
              'יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];

let busy = new Set(), first = null, last = null, offset = 0, months = 3;
let selA = null, selB = null, tent = null, cells = [], focusIdx = 0;

const today = new Date(); today.setHours(0, 0, 0, 0);
const todayIso = ISO(today);
const nightsHe = n => n === 1 ? 'לילה אחד' : n === 2 ? 'שני לילות' : `${n} לילות`;
const visibleMonths = () => innerWidth < 1020 ? 2 : 3;

/** האם התאריך בר בחירה בכלל: לא עבר, לא תפוס, ובתוך טווח הנתונים. */
function selectable(k) {
  if (k < todayIso) return false;
  if (busy.has(k)) return false;
  if (first && k < first) return false;
  if (last && k > last) return false;
  return true;
}

/** אחרי בחירת כניסה, הלילה התפוס הקרוב הוא גם היציאה המאוחרת האפשרית. */
function limitFrom(a) {
  const stop = last || '9999-12-31';
  for (const d = PARSE(a); ; d.setDate(d.getDate() + 1)) {
    const k = ISO(d);
    if (k > stop) return stop;
    if (busy.has(k)) return k;          // אפשר עוד לצאת בבוקר של אותו יום
  }
}

/* ---------------- ציור ---------------- */
function render() {
  months = visibleMonths();
  const start = new Date(today.getFullYear(), today.getMonth() + offset, 1);
  let html = '';
  for (let m = 0; m < months; m++) {
    const d0 = new Date(start.getFullYear(), start.getMonth() + m, 1);
    const dim = new Date(d0.getFullYear(), d0.getMonth() + 1, 0).getDate();
    let cs = '';
    // ריפוד לפי יום השבוע של ה-1 בחודש. בעברית השבוע מתחיל בראשון,
    // ו-getDay() מחזיר 0 לראשון, כך שאין צורך בהיסט.
    for (let i = 0; i < d0.getDay(); i++) cs += '<span class="d pad" aria-hidden="true"></span>';
    for (let day = 1; day <= dim; day++) {
      const dd = new Date(d0.getFullYear(), d0.getMonth(), day);
      const k = ISO(dd);
      const ok = selectable(k);
      const why = k < todayIso ? 'עבר' : busy.has(k) ? 'תפוס' : ok ? 'פנוי' : 'לא זמין';
      const cls = ok ? 'free' : k < todayIso ? 'past' : busy.has(k) ? 'busy' : 'off';
      const lbl = day + ' ב' + MON[d0.getMonth()] + ' ' + d0.getFullYear() +
                  ', יום ' + DOWL[dd.getDay()] + ', ' + why;
      cs += '<button type="button" class="d ' + cls + (k === todayIso ? ' today' : '') +
            '" data-d="' + k + '" tabindex="-1"' + (ok ? '' : ' aria-disabled="true"') +
            ' aria-label="' + lbl + '"><span class="n">' + day + '</span></button>';
    }
    html += '<div class="mon"><h3>' + MON[d0.getMonth()] + ' ' + d0.getFullYear() + '</h3>' +
            '<div class="dow" aria-hidden="true">' +
            DOW.map(x => '<span>' + x + '</span>').join('') + '</div>' +
            '<div class="grid7">' + cs + '</div></div>';
  }
  wrap.innerHTML = html;
  cells = [...wrap.querySelectorAll('.d[data-d]')];

  $('#calPrev').disabled = offset <= 0;
  if (last) {
    const lastD = PARSE(last);
    const lastShown = new Date(start.getFullYear(), start.getMonth() + months - 1, 1);
    $('#calNext').disabled = lastShown >= new Date(lastD.getFullYear(), lastD.getMonth(), 1);
  }
  // המיקוד נשאר על תאריך אמיתי גם אחרי החלפת חודש
  const keep = cells.findIndex(c => c.dataset.d === (selA || todayIso));
  focusIdx = keep >= 0 ? keep : Math.max(0, cells.findIndex(c => c.classList.contains('free')));
  roving();
  paint();
}

function roving() {
  cells.forEach((c, i) => { c.tabIndex = i === focusIdx ? 0 : -1; });
}

function paint() {
  const end = selB || tent;                 // tent = תצוגה מקדימה בריחוף
  const preview = !selB && !!tent;
  const lim = selA && !selB ? limitFrom(selA) : null;

  for (const c of cells) {
    const k = c.dataset.d;
    ['band','tent','tent-edge','edge','edge-a','edge-b','dim'].forEach(x => c.classList.remove(x));

    if (selectable(k)) {
      c.classList.add('free');
      c.removeAttribute('aria-disabled');
      // מעבר ללילה התפוס הקרוב אי אפשר לצאת, ולכן התאריך מעומעם.
      // הוא נשאר לחיץ בכוונה: לחיצה עליו פשוט מתחילה בחירה חדשה משם,
      // וזה עדיף על לוח שנראה מת ומחייב ללחוץ "ניקוי" קודם.
      c.classList.toggle('dim', !!(lim && k > lim));
    }

    if (!selA) continue;
    if (k === selA) {
      c.classList.add('edge', 'edge-a');
      if (preview) c.classList.add('tent-edge');
    }
    if (end && k === end && end !== selA) {
      c.classList.add('edge', 'edge-b');
      if (preview) c.classList.add('tent-edge');
    }
    if (end && k >= selA && k <= end) c.classList.add(preview ? 'tent' : 'band');
  }
  summary();
}

/* ---------------- סיכום ומחיר ---------------- */
function summary() {
  const hint = $('#calHint'), warn = $('#calWarn'), cal = $('#cal'), clr = $('#calClear');
  warn.classList.remove('on');
  clr.hidden = !selA;

  if (!selA) {
    hint.innerHTML = 'לחצו על <b>תאריך הכניסה</b>';
    cal.classList.remove('done');
    return;
  }
  if (!selB) {
    const lim = limitFrom(selA);
    const far = !last || lim < last;
    // בלי פסיק לפני התאריך: מספר מבודד ל-LTR אחרי פסיק בעברית
    // מסודר מחדש ע"י הדפדפן, והפסיק מתנתק מהמילה שלפניו.
    hint.innerHTML = 'כניסה <b class="num">' + HEDATE(selA) +
      '</b>. עכשיו לחצו על <b>תאריך היציאה</b>' +
      (far ? ' עד <b class="num">' + HEDATE(lim) + '</b>' : '');
    cal.classList.remove('done');
    return;
  }

  // רשת ביטחון: לילה תפוס בתוך הטווח כבר לא אמור להיות אפשרי, אבל אם
  // בכל זאת קרה, עדיף להגיד את זה מפורש מלהציג מחיר שגוי.
  const bad = [];
  for (const d = PARSE(selA); ISO(d) < selB; d.setDate(d.getDate() + 1)) {
    if (busy.has(ISO(d))) bad.push(ISO(d));
  }
  if (bad.length) {
    warn.textContent = bad.length === 1
      ? 'הלילה של ' + HEDATE(bad[0]) + ' תפוס. בחרו טווח אחר.'
      : 'בטווח שבחרתם יש ' + bad.length + ' לילות תפוסים (הראשון ' +
        HEDATE(bad[0]) + '). בחרו טווח אחר.';
    warn.classList.add('on');
    return;
  }

  const q = window.OLGA.quote ? window.OLGA.quote(selA, selB) : null;
  const n = Math.round((PARSE(selB) - PARSE(selA)) / 864e5);
  // המחיר מוצג בלוח המחיר שממש כאן ליד, ואין טעם לחזור עליו פעמיים
  hint.innerHTML = '<b class="num">' + HEDATE(selA) + '</b> עד <b class="num">' +
                   HEDATE(selB) + '</b> · ' + nightsHe(n);
  cal.classList.add('done');
  $('#calLive').textContent = 'נבחרו ' + HEDATE(selA) + ' עד ' + HEDATE(selB) +
    ', ' + nightsHe(n) + (q ? ', ' + q.text : '');
}

/* ---------------- בחירה ---------------- */
function pick(k) {
  if (!selA || (selA && selB)) { selA = k; selB = null; }
  else if (k === selA) { selA = null; selB = null; }      // לחיצה חוזרת מבטלת
  else if (k < selA) { selA = k; selB = null; }
  else if (k > limitFrom(selA)) { selA = k; selB = null; } // מעבר לגבול: מתחילים משם
  else selB = k;
  tent = null;
  paint();
  sync();
}

/** מזרים את הבחירה לשדות הטופס. הלוח והטופס הם עכשיו אותה סקציה,
    ולכן אין יותר כפתור "המשך" שמעביר ביניהם: המחיר פשוט מתעדכן. */
function sync() {
  const ci = $('#ci'), co = $('#co');
  if (!ci || !co) return;
  ci.value = selA || '';
  ci.dispatchEvent(new Event('change', { bubbles: true }));
  // אחרי ה-dispatch ולא לפניו: המטפל של שדה הכניסה ממלא יציאה
  // אוטומטית ליום אחד, וזה היה מציג מחיר לפני שנבחרה יציאה.
  co.value = (selA && selB) ? selB : '';
  co.dispatchEvent(new Event('change', { bubbles: true }));
  // הכפתור בירו מציג את אותה בחירה, כדי שגלילה חזרה למעלה לא תראה
  // שדה ריק בזמן שהלוח למטה כבר מלא.
  window.OLGA.showDates?.(selA, selB);
}

wrap.addEventListener('click', e => {
  const el = e.target.closest('.d[data-d]');
  if (!el || el.getAttribute('aria-disabled') === 'true') return;
  focusIdx = cells.indexOf(el); roving();
  pick(el.dataset.d);
});

// תצוגה מקדימה של הטווח לפני הלחיצה השנייה
wrap.addEventListener('pointerover', e => {
  if (!selA || selB) return;
  const el = e.target.closest('.d[data-d]');
  if (!el || el.getAttribute('aria-disabled') === 'true') return;
  const k = el.dataset.d;
  if (k <= selA || k === tent || k > limitFrom(selA)) return;
  tent = k; paint();
});
wrap.addEventListener('pointerleave', () => { if (tent) { tent = null; paint(); } });

/* ---------------- מקלדת ----------------
   tabindex נודד: תא אחד בסדר ה-Tab, והחצים מזיזים בין הימים.
   בעברית החץ שמאלה מתקדם ביום, כי הלוח נקרא מימין לשמאל. */
wrap.addEventListener('keydown', e => {
  const step = { ArrowLeft: 1, ArrowRight: -1, ArrowDown: 7, ArrowUp: -7,
                 PageDown: 30, PageUp: -30 }[e.key];
  if (step !== undefined) {
    e.preventDefault();
    const next = focusIdx + step;
    if (next < 0) { if (offset > 0) { offset--; render(); cells[focusIdx]?.focus(); } return; }
    if (next >= cells.length) {
      if (!$('#calNext').disabled) { offset++; render(); cells[focusIdx]?.focus(); }
      return;
    }
    focusIdx = next; roving(); cells[focusIdx].focus();
    return;
  }
  if (e.key === 'Home' || e.key === 'End') {
    e.preventDefault();
    focusIdx = e.key === 'Home' ? 0 : cells.length - 1;
    roving(); cells[focusIdx].focus(); return;
  }
  if (e.key === 'Escape' && selA) {
    e.preventDefault(); selA = selB = tent = null; paint(); sync();
  }
});

$('#calPrev').addEventListener('click', () => { if (offset > 0) { offset--; render(); } });
$('#calNext').addEventListener('click', () => { offset++; render(); });
$('#calClear').addEventListener('click', () => {
  selA = selB = tent = null; paint(); sync();
  cells[focusIdx]?.focus();
});

/* טופס הירו בוחר תאריכים לפני שהמשתמש מגיע ללוח. בלי הדרך הזו
   המחיר היה מתעדכן והלוח היה נשאר ריק, כלומר שני מקומות שסותרים
   זה את זה באותו מסך. */
window.OLGA.setDates = (a, b) => {
  if (!a) return false;
  if (!selectable(a)) {
    // תאריך תפוס או שעבר: מנקים במקום להשאיר בחירה ישנה שסותרת
    // את מה שהמשתמש הרגע ביקש, והרמז מחזיר אותו לבחירה.
    selA = selB = tent = null;
    render(); sync();
    const h = $('#calHint');
    if (h) h.innerHTML = 'התאריך הזה כבר תפוס. <b>לחצו על תאריך אחר</b>';
    return true;                      // הלוח טיפל, אין צורך בגיבוי
  }
  selA = a;
  selB = (b && b > a && b <= limitFrom(a) && selectable(b)) ? b : null;
  tent = null;
  // מגלגלים את הלוח לחודש שבו נמצא התאריך, אחרת הבחירה לא נראית
  const m = (PARSE(a).getFullYear() - today.getFullYear()) * 12 +
            (PARSE(a).getMonth() - today.getMonth());
  if (m < offset || m > offset + months - 1) offset = Math.max(0, m);
  render();
  sync();
  return true;
};

let rt = 0;
addEventListener('resize', () => {
  clearTimeout(rt);
  rt = setTimeout(() => { if (visibleMonths() !== months) render(); }, 180);
});

fetch('assets/availability.json?h=' + Math.floor(Date.now() / 36e5), { cache: 'no-cache' })
  .then(r => r.ok ? r.json() : Promise.reject())
  .then(d => {
    busy = new Set(d.blockedDates || []);
    first = d.from; last = d.to;
    window.OLGA.busy = busy;
    // השדות הידניים הם ברירת המחדל וגם הגיבוי: הם עובדים בלי JS
    // ובלי הנתון. ברגע שהלוח באמת עלה, הוא לוקח את התפקיד.
    const df = document.querySelector('#dateFields');
    if (df) { df.hidden = true; $('#ci').required = false; $('#co').required = false; }
    // מחשבון המחיר כבר רץ פעם אחת בלי הנתון הזה. עכשיו הוא יכול לתמחר נכון.
    dispatchEvent(new CustomEvent('olga:availability'));

    const days = Math.floor((Date.now() - new Date(d.fetchedAt)) / 864e5);
    const ago = days <= 0 ? 'היום' : days === 1 ? 'אתמול' : 'לפני ' + days + ' ימים';

    /* כאן היה "323 לילות פנויים בשנה הקרובה". זה מידע תפעולי שאומר
       ללקוח שהווילה ריקה רוב השנה, כלומר בדיוק ההפך ממה שצריך.
       במקומו: כמה לילות כבר תפוסים בחודש הקרוב. אותו מקור נתונים,
       אמירה נכונה, והיא גם זו שמעניינת מי ששוקל תאריך.
       התנאי חשוב: במספר נמוך עדיף לא להציג שורה בכלל. */
    const in30 = ISO(new Date(Date.now() + 30 * 864e5));
    const soon = [...busy].filter(k => k <= in30).length;
    $('#calNote').innerHTML =
      '<span>עודכן <b>' + ago + '</b> מלוח השנה של הווילה</span>' +
      (soon >= 3 ? '<span><b class="num">' + soon + '</b> לילות כבר תפוסים בחודש הקרוב</span>' : '');
    render();
  })
  .catch(() => {
    // בלי הנתון עדיף לא להראות לוח בכלל מלהראות לוח שקרי.
    // שדות התאריך הידניים כבר גלויים, ולכן ההזמנה ממשיכה לעבוד.
    document.querySelector('#cal')?.remove();
    document.querySelector('#calPick')?.remove();
  });
})();
