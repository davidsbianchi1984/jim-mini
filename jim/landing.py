"""The page somebody lands on after scanning a care beacon.

`GET /c/{id}` answered JSON, which meant a neighbour who scanned a fridge
magnet got a wall of braces. This is the page that should have been there.

Why it is hand-written HTML rather than a route into the console:

* **It opens inside a camera app's in-app browser**, on cellular, from a cold
  start, possibly by somebody kneeling next to a person on the floor. One
  self-contained document — inline CSS, inline script, no font, image or
  stylesheet fetches. Nothing needs a second request to be legible.
* **The reader is a stranger** with no account and no idea what a Guardian is.
  They pointed a phone at a sticker.
* **The order matters more than the layout.** Stage one is a first name, one
  sentence, and a button — nothing clinical, no location, and no word about
  how the person is. Raising the alarm is the act that turns a passer-by into
  a responder, and *that* is what reveals the Medical ID, which arrives in the
  alarm's own response and is rendered in place.

Stage two never opens for a minor. The server decides that — :func:`alarm`
returns ``medical_id: None`` — and this page only renders what it is handed,
so there is no second place for it to leak from.

The form posts to a **relative** URL. An absolute one baked from
``JIM_PUBLIC_URL`` breaks every scan on a LAN deployment.
"""

from __future__ import annotations

import html
import json

from . import i18n

# Dark slate with the Medical ID's own red — a printed code on a person's
# things should look like the other printed code on a person's things.
_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0f1c;color:#eef1f7;min-height:100dvh;display:flex;
 align-items:center;justify-content:center;padding:20px;
 font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
 -webkit-font-smoothing:antialiased}
.card{width:100%;max-width:440px}
.panel{background:#182238;border:1px solid #26314e;border-radius:20px;
 padding:22px;box-shadow:0 20px 50px rgba(0,0,0,.5);
 animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
/* Transform only, never opacity: if the animation does not run, the page must
   still be on screen. Somebody is reading this in a hurry. */
@keyframes rise{from{transform:translateY(10px)}to{transform:none}}
@media (prefers-reduced-motion:reduce){.panel{animation:none}}
h1{font-size:26px;line-height:1.2;margin-bottom:6px}
.watched{color:#8a94ad;font-size:15px;margin-bottom:18px}
/* The loudest thing on the page, and deliberately above the button: the one
   mistake that matters here is somebody waiting for this page instead of
   dialling. */
.first{background:rgba(255,61,48,.12);border:1px solid rgba(255,61,48,.5);
 border-radius:14px;padding:14px 16px;font-size:15px;line-height:1.45;
 color:#ffc9c4;margin-bottom:18px}
.first b{color:#fff}
button{width:100%;font:inherit;font-size:17px;font-weight:700;color:#fff;
 background:linear-gradient(90deg,#b3261e,#ff4d5e);border:0;border-radius:14px;
 padding:17px;cursor:pointer}
button:disabled{opacity:.55;cursor:default}
.badge{display:block;margin-top:16px;font-size:12.5px;font-weight:700;
 line-height:1.45;color:#8a94ad;border:1px solid #26314e;border-radius:12px;
 padding:9px 12px;text-align:center}
.status{min-height:20px;margin-top:12px;font-size:14px;color:#43e08a;
 text-align:center}
label{display:block;font-size:13px;color:#8a94ad;margin:16px 0 6px}
textarea{width:100%;font:inherit;font-size:16px;color:#eef1f7;background:#0f1626;
 border:1px solid #26314e;border-radius:12px;padding:12px 14px;
 -webkit-appearance:none}
textarea:focus{outline:2px solid #ff4d5e;outline-offset:-1px}
.med{margin-top:16px}
.med h2{font-size:15px;color:#ff8f88;margin-bottom:10px;letter-spacing:.3px}
.row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;
 border-top:1px solid #26314e;font-size:15px}
.row span:first-child{color:#8a94ad}
.row span:last-child{text-align:right;font-weight:600}
.conds{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.cond{font-size:12px;font-weight:700;color:#f7b731;
 border:1px solid rgba(247,183,49,.5);border-radius:999px;padding:3px 9px}
a.tel{color:#43e08a;font-weight:700;text-decoration:none}
.foot{color:#626d88;font-size:12px;text-align:center;margin-top:18px}
.ask{margin-top:18px;border-top:1px solid #26314e;padding-top:15px}
.ask h2{font-size:15px;color:#eef1f7;margin-bottom:4px}
.ask .lead{color:#8a94ad;font-size:13px}
.ans{margin-top:14px;background:#0f1626;border:1px solid #26314e;
 border-radius:12px;padding:13px 15px;font-size:15px;line-height:1.5;
 white-space:pre-wrap}
.ans .src{display:block;margin-top:10px;font-size:11.5px;font-weight:700;
 color:#8a94ad;letter-spacing:.2px;white-space:normal}
"""


def _page(title: str, body: str, language: str = "en") -> str:
    # `lang` is not decoration: it is what a screen reader picks a voice from,
    # and this page may well be read aloud by somebody whose hands are busy.
    # `dir` because Arabic is one of the ten languages this product supports.
    direction = "rtl" if language == "ar" else "ltr"
    return (
        f'<!doctype html><html lang="{language}" dir="{direction}">'
        '<head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,'
        'viewport-fit=cover"><meta name="theme-color" content="#0a0f1c">'
        f"<title>{html.escape(title)}</title><style>{_CSS}</style></head>"
        f'<body><main class="card">{body}</main></body></html>')


def _js(value: str) -> str:
    return json.dumps(value)


def gone(language: str = "en") -> str:
    """A code that never existed, or has been peeled off. One page for both —
    somebody at a dead sticker should not learn which.

    Localized for the same reason the live page is, and it matters here too:
    a dead sticker is still somebody standing over a person, and the sentence
    that tells them to call anyway is the only useful thing on this page.
    """
    return _page(i18n.tr(GONE_PAGE_TITLE, language), (
        '<div class="panel">'
        f"<h1>{html.escape(i18n.tr(GONE_TITLE, language))}</h1>"
        f'<p class="watched">{html.escape(i18n.tr(GONE_BODY, language))}</p>'
        "</div>"), language)


#: The `<title>`. Not decoration: it is what a phone shows in the tab, what
#: a shared link previews as, and what a screen reader announces first — and
#: it was English on both pages while everything under it was translated.
GONE_PAGE_TITLE = "Nothing here"
CARE_TITLE = "Someone is watching over this person"

#: Whole sentences with named holes, so each language puts the name where its
#: own grammar wants it instead of being handed "You've found".
FOUND_NAMED = "You've found {name}."

FOOT_SITE = ("This is a workplace site. Raising the alarm reaches whoever is "
             "on call.")
FOOT_HOME = ("Raising the alarm alerts the people who watch over this "
             "person. It does not tell you how they are, and nothing on this "
             "page says where they live.")

GONE_TITLE = "This code doesn't resolve to anything"
GONE_BODY = ("It may have been removed, or it may never have been one of "
             "ours. If someone in front of you needs help, call your local "
             "emergency number — this page cannot.")


_ALARM_JS = """
(function(){
 var S=%(strings)s;
 var f=document.getElementById('f'),b=document.getElementById('go'),
     s=document.getElementById('st');
 if(!f)return;
 f.addEventListener('submit',function(e){
  e.preventDefault();b.disabled=true;b.textContent=S.raising;
  fetch(%(endpoint)s,{method:'POST',
   headers:{'content-type':'application/json'},
   body:JSON.stringify({message:document.getElementById('m').value||null})})
  .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
  .then(function(o){
   if(!o.ok){b.disabled=false;b.textContent=S.raise_;
    s.textContent=(o.j&&o.j.detail)||S.failed;return;}
   var j=o.j;
   b.remove();document.getElementById('m').parentNode.removeChild(
     document.getElementById('m'));
   var lb=document.getElementById('ml');if(lb)lb.remove();
   s.textContent=j.note||'';
   var bd=document.getElementById('bg');if(bd)bd.textContent=j.badge||'';
   var m=j.medical_id;
   if(m){
    var d=document.createElement('div');d.className='med';
    var h='<h2>'+esc(S.medid)+'</h2>';
    if(m.name)h+=row(esc(S.name),esc(m.name));
    if(m.age!==null&&m.age!==undefined)h+=row(esc(S.age),String(m.age));
    if(m.known_conditions&&m.known_conditions.length){
     h+=row(esc(S.conds),'<span class="conds">'+m.known_conditions.map(
       function(c){return '<span class="cond">'+esc(c)+'</span>';}).join('')
       +'</span>');}
    if(m.resting_heart_rate)h+=row(esc(S.hr),m.resting_heart_rate+' bpm');
    if(m.emergency_contact&&m.emergency_contact.phone){
     h+=row(esc(S.contact),'<a class="tel" href="tel:'
       +esc(m.emergency_contact.phone)+'">'
       +esc(m.emergency_contact.name||m.emergency_contact.phone)+'</a>');}
    d.innerHTML=h;f.parentNode.appendChild(d);}
   // Unconditional, and deliberately outside the block above: a minor's
   // beacon opens no clinical stage to anybody, and the person kneeling
   // over a child needs to know what to do more than anyone, not less.
   ask(j.alarm);
  }).catch(function(){b.disabled=false;b.textContent='Raise the alarm';
   s.textContent=S.noconn;});
 });
 function ask(id){
  if(!id)return;
  var w=document.createElement('div');w.className='ask';
  w.innerHTML='<h2>'+esc(S.whatdo)+'</h2>'
   +'<p class="lead">'+esc(S.notclin)+'</p>'
   +'<label for="q">'+esc(S.whathap)+'</label>'
   +'<textarea id="q" rows="2" placeholder="'+esc(S.egq)+'">'
   +'</textarea><button id="qb" type="button">'+esc(S.ask)+'</button>'
   +'<div id="qa"></div>';
  f.parentNode.appendChild(w);
  var qb=document.getElementById('qb'),qa=document.getElementById('qa');
  qb.addEventListener('click',function(){
   var q=document.getElementById('q').value.trim();
   if(!q)return;
   qb.disabled=true;qb.textContent=S.asking;
   fetch(%(guidance)s+encodeURIComponent(id)+'/guidance',{method:'POST',
    headers:{'content-type':'application/json'},
    body:JSON.stringify({question:q})})
   .then(function(r){return r.json();})
   .then(function(g){
    qb.disabled=false;qb.textContent=S.askagain;
    var a=document.createElement('div');a.className='ans';
    a.textContent=g.answer||'';
    if(g.note){var n=document.createElement('span');n.className='src';
     n.textContent=g.note;a.appendChild(n);}
    qa.appendChild(a);})
   .catch(function(){
    qb.disabled=false;qb.textContent=S.ask;
    var a=document.createElement('div');a.className='ans';
    // The one instruction that is always right and never needs a network.
    a.textContent=S.offline;
    qa.appendChild(a);});
  });
 }
 function row(k,v){return '<div class="row"><span>'+k+'</span><span>'+v
  +'</span></div>';}
 function esc(t){var d=document.createElement('div');d.textContent=t;
  return d.innerHTML;}
})();
"""


def care_page(card: dict, language: str = "en") -> str:
    """Stage one, and the button that buys stage two.

    Renders only what ``beacons.card`` returned — a first name and a sentence.
    The Medical ID is not on this page at any point before the alarm; it
    arrives in the alarm's own response, so there is nothing here to reveal
    early even by mistake.

    ``language`` is **the finder's**, negotiated from their own
    ``Accept-Language`` by :func:`i18n.negotiate`, not the watched person's.
    Every other localization path in this product takes a ``user_id``, which
    is exactly the thing the reader of this page does not have — so until
    this argument existed, a passer-by anywhere in the world was told in
    English that somebody was being watched over and what to do about it.

    Unknown strings fall back to English through :func:`i18n.tr` rather than
    being machine-translated, which is the same rule the CPR playbooks and
    the waiver terms already follow. A stranger reading instructions about a
    person on the floor is the last reader who should get a guess.
    """
    def t(text: str) -> str:
        return i18n.tr(text, language)

    first = card.get("first_name")
    # Both branches translated, and the named one as a whole sentence with
    # its hole named rather than an f-string around a fragment. Only the
    # anonymous branch went through `t` until now, so a Spanish finder
    # holding a beacon for somebody with a first name on it got the one
    # sentence at the top of the page in English — the greeting, on the
    # page's largest type, above everything else.
    who = (t(FOUND_NAMED).replace("{name}", html.escape(first)) if first
           else t("You've found someone."))
    site = card.get("site")
    body = (
        '<div class="panel">'
        f"<h1>{who}</h1>"
        f'<p class="watched">{html.escape(card.get("note") or "")}</p>'
        '<div class="first"><b>'
        + html.escape(t("If this is an emergency, call your local emergency "
                        "number first."))
        + "</b> "
        + html.escape(t("This page cannot call anyone for you, and it is not "
                        "an emergency service."))
        + "</div>"
        '<form id="f">'
        f'<label id="ml" for="m">{html.escape(t("Anything you can tell them? (optional)"))}</label>'
        '<textarea id="m" name="m" rows="3" '
        f'placeholder="{html.escape(t("where you are, what you can see"))}">'
        "</textarea>"
        f'<button id="go" type="submit">{html.escape(t("Raise the alarm"))}</button>'
        "</form>"
        '<div class="status" id="st"></div>'
        f'<div class="badge" id="bg">{html.escape(card.get("badge") or "")}'
        "</div>"
        "</div>"
        # Neither foot went through `t` before this round. They are the
        # sentence that tells a finder what pressing the button will and will
        # not do, which is the thing somebody hesitating most needs.
        + f'<p class="foot">{html.escape(t(FOOT_SITE if site else FOOT_HOME))}'
          "</p>"
        + "<script>"
        + _ALARM_JS % {"endpoint": _js(f"/c/{card['beacon']}/alarm"),
                       # A prefix, not a URL: the alarm id only exists once
                       # the alarm has been raised. Relative, for the same
                       # reason the alarm endpoint is — an absolute one baked
                       # from JIM_PUBLIC_URL breaks every scan on a LAN.
                       "guidance": _js("/alarms/"),
                       # Every string the script writes after the page has
                       # loaded. Handed in already translated rather than
                       # looked up in the browser: there is no second request
                       # on this page by design, and a dictionary shipped
                       # inline costs nothing next to a font.
                       # `ensure_ascii=False` because the document declares
                       # UTF-8 and this page is deliberately one small file:
                       # \u-escaping every accented character roughly doubles
                       # the blob for a reader on cellular in a hurry.
                       "strings": json.dumps(ensure_ascii=False, obj={
                           "raising": t("Raising…"),
                           "raise_": t("Raise the alarm"),
                           "failed": t("That did not go through."),
                           "noconn": t("No connection — call your local "
                                       "emergency number."),
                           "medid": t("MEDICAL ID"),
                           "name": t("Name"),
                           "age": t("Age"),
                           "conds": t("Known conditions"),
                           "hr": t("Resting heart rate"),
                           "contact": t("Emergency contact"),
                           "whatdo": t("What do I do while you wait?"),
                           "notclin": t("Guidance, not a clinician — it "
                                        "cannot see them, and it cannot call "
                                        "anyone."),
                           "whathap": t("What is happening?"),
                           "egq": t("breathing, but will not wake up"),
                           "ask": t("Ask"),
                           "askagain": t("Ask again"),
                           "asking": t("Asking…"),
                           "offline": t(
                               "No connection. Call your local emergency "
                               "number if you have not already. Do not move "
                               "them unless they are in danger where they "
                               "are. Stay with them until someone arrives."),
                       })}
        + "</script>")
    return _page(t(CARE_TITLE), body, language)
