"""Per-user language: everything the Guardian drafts or delivers, localized.

Two mechanisms, matched to how each kind of content is produced:

- **Model-generated text** (guidance counsel, coaching, robot speech) is
  generated *in the user's language*: the language directive is appended to
  the system prompt, so a configured LLM answers natively rather than
  translating after the fact. The offline stub cannot translate free text —
  responses carry a ``translation_note`` when that happens, so the UI never
  silently misrepresents localization.
- **Deterministic safety content** (the CPR/AED playbooks, pace cues, waiver
  terms) is *hand-translated here* for every supported language,
  string-keyed against the English source so an edit to the English
  invalidates the translation loudly (fallback to English) instead of
  silently drifting. Safety text is never machine-mangled.
"""

from __future__ import annotations

import re

SUPPORTED: dict[str, str] = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
    "ja": "日本語",
    "zh": "中文",
    "hi": "हिन्दी",
    "ar": "العربية",
}

# Every supported language carries hand-translated safety content
# (playbooks, pace cues, waiver terms).
HAND_TRANSLATED = tuple(code for code in SUPPORTED if code != "en")

DEFAULT = "en"

# How translation is applied:
# - "pre":       everything drafted for the user arrives already in their
#                language (generation in-language, safety text hand-swapped);
# - "on_demand": originals are kept and the user translates selectively via
#                POST /translate — some prefer original medical text plus a
#                translation beside it.
MODES = ("pre", "on_demand")


def get_pref(user_id: str) -> tuple[str, str]:
    from . import db
    row = db.connect().execute(
        "SELECT language, mode FROM language_prefs WHERE user_id=?",
        (user_id,)).fetchone()
    return (row["language"], row["mode"]) if row else (DEFAULT, "pre")


def get_language(user_id: str) -> str:
    return get_pref(user_id)[0]


def effective_language(user_id: str) -> str:
    """The language content is *delivered* in: the chosen language when the
    mode is "pre", English when the user opted for on-demand translation."""
    language, mode = get_pref(user_id)
    return language if mode == "pre" else DEFAULT


def set_language(user_id: str, language: str, mode: str = "pre") -> str:
    if language not in SUPPORTED:
        raise ValueError(fill(UNKNOWN_VALUE, field="language",
                              got=repr(language)))
    if mode not in MODES:
        raise ValueError(fill(MUST_BE_ONE_OF, field="mode",
                              choices=", ".join(MODES)))
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO language_prefs (user_id, language, mode, updated_at)"
        " VALUES (?,?,?,?)"
        " ON CONFLICT(user_id) DO UPDATE SET language=excluded.language,"
        " mode=excluded.mode, updated_at=excluded.updated_at",
        (user_id, language, mode, db.utcnow()))
    conn.commit()
    return language


def translate(user_id: str, text: str, to: str | None = None) -> dict:
    """Translate anything the user runs across. Hand translations win when
    the string is a known safety string; otherwise the user's own LLM
    translates; the offline stub cannot, and says so instead of pretending."""
    from . import llm
    target = to or get_language(user_id)
    if target not in SUPPORTED:
        raise ValueError(fill(UNKNOWN_VALUE, field="language",
                              got=repr(target)))
    if target == DEFAULT:
        return {"text": text, "translation": text, "language": target,
                "engine": "none", "note": "target language is English"}
    hand = tr(text, target)
    if hand != text:
        return {"text": text, "translation": hand, "language": target,
                "engine": "hand"}
    effective = llm.resolve_choice(llm.get_choice(user_id))
    if effective == "stub":
        return {"text": text, "translation": text, "language": target,
                "engine": "stub",
                "note": "the offline stub cannot translate free text — "
                        "configure a model provider for live translation"}
    system = (f"You are a precise translator. Translate the user's text into "
              f"{SUPPORTED[target]} ({target}). Preserve meaning, tone, and "
              "formatting. Output only the translation.")
    translation = llm.provider_for_user(user_id).generate(system, text)
    return {"text": text, "translation": translation, "language": target,
            "engine": effective}


def directive(language: str) -> str:
    """The system-prompt line that makes a model answer in-language."""
    if language == DEFAULT:
        return ""
    return (f"\nRespond entirely in {SUPPORTED[language]} ({language}) — "
            "every sentence, including safety instructions.")


# --------------------------------------------------------------------------- #
# hand translations, string-keyed against the English source
# --------------------------------------------------------------------------- #

_STRINGS: dict[str, dict[str, str]] = {
    # -- CPR playbook -------------------------------------------------------
    "Call emergency services now (or have someone else call).": {
        "es": "Llame ahora a los servicios de emergencia (o pida a otra "
              "persona que llame).",
        "fr": "Appelez immédiatement les services d'urgence (ou demandez à "
              "quelqu'un d'appeler).",
        "de": "Rufen Sie jetzt den Notruf an (oder lassen Sie jemand anderen "
              "anrufen).",
        "pt": "Ligue agora para os serviços de emergência (ou peça a outra "
              "pessoa que ligue).",
        "it": "Chiami subito i servizi di emergenza (o faccia chiamare "
              "qualcun altro).",
        "ja": "今すぐ救急に通報してください（または他の人に通報を頼んでください）。",
        "zh": "立即拨打急救电话（或请他人拨打）。",
        "hi": "तुरंत आपातकालीन सेवाओं को कॉल करें (या किसी और से कॉल करवाएँ)।",
        "ar": "اتصل بخدمات الطوارئ الآن (أو اطلب من شخص آخر الاتصال).",
    },
    "Lay the person on their back on a firm surface; tilt the head back.": {
        "es": "Acueste a la persona boca arriba sobre una superficie firme; "
              "incline su cabeza hacia atrás.",
        "fr": "Allongez la personne sur le dos sur une surface ferme ; "
              "basculez sa tête en arrière.",
        "de": "Legen Sie die Person auf einer festen Unterlage auf den "
              "Rücken; neigen Sie den Kopf nach hinten.",
        "pt": "Deite a pessoa de costas numa superfície firme; incline a "
              "cabeça para trás.",
        "it": "Sdrai la persona sulla schiena su una superficie rigida; "
              "inclini la testa all'indietro.",
        "ja": "硬い床の上に仰向けに寝かせ、頭を後ろに傾けてください。",
        "zh": "让患者仰卧在坚硬的平面上，使其头部后仰。",
        "hi": "व्यक्ति को किसी सख़्त सतह पर पीठ के बल लिटाएँ; सिर को पीछे की ओर झुकाएँ।",
        "ar": "ضع الشخص على ظهره على سطح صلب؛ وأمل رأسه إلى الخلف.",
    },
    "Place the heel of one hand on the center of the chest, other hand on "
    "top, arms straight.": {
        "es": "Coloque el talón de una mano en el centro del pecho, la otra "
              "mano encima, con los brazos rectos.",
        "fr": "Placez le talon d'une main au centre de la poitrine, l'autre "
              "main par-dessus, bras tendus.",
        "de": "Legen Sie den Ballen einer Hand auf die Mitte des Brustkorbs, "
              "die andere Hand darauf, Arme gestreckt.",
        "pt": "Coloque a base de uma mão no centro do peito, a outra mão por "
              "cima, braços esticados.",
        "it": "Posizioni il palmo di una mano al centro del torace, l'altra "
              "mano sopra, braccia tese.",
        "ja": "片方の手のひらの付け根を胸の中央に置き、もう片方の手を重ね、腕をまっすぐ伸ばしてください。",
        "zh": "将一只手的掌根放在胸部正中，另一只手叠放其上，双臂伸直。",
        "hi": "एक हथेली के निचले हिस्से को छाती के बीच में रखें, दूसरा हाथ ऊपर रखें, बाँहें सीधी रखें।",
        "ar": "ضع كعب إحدى يديك في منتصف الصدر، واليد الأخرى فوقها، مع فرد الذراعين.",
    },
    "Push hard and fast — at least 2 inches (5 cm) deep — and let the "
    "chest fully recoil between compressions.": {
        "es": "Comprima fuerte y rápido — al menos 5 cm de profundidad — y "
              "deje que el pecho se expanda por completo entre compresiones.",
        "fr": "Appuyez fort et vite — au moins 5 cm de profondeur — et "
              "laissez la poitrine se relever complètement entre les "
              "compressions.",
        "de": "Drücken Sie fest und schnell — mindestens 5 cm tief — und "
              "lassen Sie den Brustkorb zwischen den Kompressionen "
              "vollständig zurückfedern.",
        "pt": "Comprima com força e rapidez — pelo menos 5 cm de "
              "profundidade — e deixe o peito voltar completamente entre as "
              "compressões.",
        "it": "Prema con forza e rapidità — almeno 5 cm di profondità — e "
              "lasci che il torace risalga completamente tra le compressioni.",
        "ja": "強く速く押してください（少なくとも5cmの深さ）。圧迫の合間には胸が完全に戻るようにしてください。",
        "zh": "用力快速按压——深度至少5厘米——每次按压之间让胸部完全回弹。",
        "hi": "ज़ोर से और तेज़ दबाएँ — कम से कम 5 सेमी गहराई तक — और हर दबाव के बीच छाती को पूरी तरह ऊपर आने दें।",
        "ar": "اضغط بقوة وبسرعة — بعمق 5 سم على الأقل — ودع الصدر يرتد تمامًا بين الضغطات.",
    },
    "Follow the pace cue below; after 30 compressions give 2 rescue "
    "breaths, then continue 30:2.": {
        "es": "Siga la señal de ritmo de abajo; tras 30 compresiones dé 2 "
              "ventilaciones de rescate y continúe 30:2.",
        "fr": "Suivez le rythme indiqué ci-dessous ; après 30 compressions, "
              "donnez 2 insufflations, puis continuez 30:2.",
        "de": "Folgen Sie der Taktvorgabe unten; geben Sie nach 30 "
              "Kompressionen 2 Beatmungen und fahren Sie mit 30:2 fort.",
        "pt": "Siga o ritmo indicado abaixo; após 30 compressões, faça 2 "
              "ventilações de resgate e continue 30:2.",
        "it": "Segua il ritmo indicato sotto; dopo 30 compressioni effettui "
              "2 ventilazioni di soccorso, poi continui 30:2.",
        "ja": "下のリズム表示に従ってください。圧迫30回ごとに人工呼吸を2回行い、30:2を続けてください。",
        "zh": "按照下方的节奏提示进行；每按压30次做2次人工呼吸，然后按30:2继续。",
        "hi": "नीचे दिए गए ताल संकेत का पालन करें; 30 दबावों के बाद 2 बचाव-श्वास दें, फिर 30:2 जारी रखें।",
        "ar": "اتبع إيقاع الضغط أدناه؛ بعد 30 ضغطة أعطِ نفسين إنقاذيين، ثم واصل بمعدل 30:2.",
    },
    "Do not stop until help arrives, an AED is ready, or the person "
    "responds.": {
        "es": "No se detenga hasta que llegue la ayuda, un DEA esté listo o "
              "la persona responda.",
        "fr": "Ne vous arrêtez pas tant que les secours ne sont pas arrivés, "
              "qu'un DEA n'est pas prêt ou que la personne ne réagit pas.",
        "de": "Hören Sie nicht auf, bis Hilfe eintrifft, ein AED bereit ist "
              "oder die Person reagiert.",
        "pt": "Não pare até a ajuda chegar, um DEA estar pronto ou a pessoa "
              "responder.",
        "it": "Non si fermi finché non arrivano i soccorsi, un DAE è pronto "
              "o la persona risponde.",
        "ja": "救助が到着するか、AEDの準備ができるか、本人が反応するまで中断しないでください。",
        "zh": "在救援到达、AED就绪或患者有反应之前，不要停止。",
        "hi": "जब तक मदद न आ जाए, AED तैयार न हो जाए, या व्यक्ति प्रतिक्रिया न दे, तब तक न रुकें।",
        "ar": "لا تتوقف حتى تصل المساعدة، أو يجهز جهاز الصدمات (AED)، أو يستجيب الشخص.",
    },
    # -- pace cue -----------------------------------------------------------
    "green flashes on each compression beat; red means you've drifted off "
    "pace": {
        "es": "la luz verde parpadea con cada compresión; roja significa que "
              "ha perdido el ritmo",
        "fr": "la lumière verte clignote à chaque compression ; rouge "
              "signifie que vous avez perdu le rythme",
        "de": "grünes Blinken bei jedem Kompressionstakt; rot bedeutet, dass "
              "Sie aus dem Takt sind",
        "pt": "verde pisca a cada compressão; vermelho significa que saiu do "
              "ritmo",
        "it": "verde lampeggia a ogni compressione; rosso significa che ha "
              "perso il ritmo",
        "ja": "圧迫のリズムごとに緑が点滅します。赤はリズムがずれているサインです",
        "zh": "每次按压节拍绿灯闪烁；红灯表示您偏离了节奏",
        "hi": "हर दबाव की ताल पर हरी बत्ती चमकती है; लाल का अर्थ है कि आपकी ताल बिगड़ गई है",
        "ar": "يومض الضوء الأخضر مع كل ضغطة؛ الأحمر يعني أنك خرجت عن الإيقاع",
    },
    "metronome tick at 110 beats per minute": {
        "es": "tic de metrónomo a 110 pulsaciones por minuto",
        "fr": "tic de métronome à 110 battements par minute",
        "de": "Metronomtakt mit 110 Schlägen pro Minute",
        "pt": "tique de metrônomo a 110 batidas por minuto",
        "it": "ticchettio del metronomo a 110 battiti al minuto",
        "ja": "毎分110拍のメトロノーム音",
        "zh": "每分钟110拍的节拍器声",
        "hi": "प्रति मिनट 110 धड़कनों पर मेट्रोनोम टिक",
        "ar": "نقرات بندول الإيقاع بمعدل 110 نبضة في الدقيقة",
    },
    # -- AED playbook ---------------------------------------------------------
    "Call emergency services and send someone for the nearest AED.": {
        "es": "Llame a los servicios de emergencia y envíe a alguien por el "
              "DEA más cercano.",
        "fr": "Appelez les services d'urgence et envoyez quelqu'un chercher "
              "le DEA le plus proche.",
        "de": "Rufen Sie den Notruf und schicken Sie jemanden nach dem "
              "nächsten AED.",
        "pt": "Ligue para os serviços de emergência e mande alguém buscar o "
              "DEA mais próximo.",
        "it": "Chiami i servizi di emergenza e mandi qualcuno a prendere il "
              "DAE più vicino.",
        "ja": "救急に通報し、最寄りのAEDを誰かに取りに行かせてください。",
        "zh": "拨打急救电话，并派人去取最近的AED。",
        "hi": "आपातकालीन सेवाओं को कॉल करें और किसी को निकटतम AED लाने भेजें।",
        "ar": "اتصل بخدمات الطوارئ وأرسل شخصًا لإحضار أقرب جهاز صدمات (AED).",
    },
    "Turn the AED on and follow its voice prompts.": {
        "es": "Encienda el DEA y siga sus instrucciones de voz.",
        "fr": "Allumez le DEA et suivez ses instructions vocales.",
        "de": "Schalten Sie den AED ein und folgen Sie seinen "
              "Sprachanweisungen.",
        "pt": "Ligue o DEA e siga as instruções de voz.",
        "it": "Accenda il DAE e segua le istruzioni vocali.",
        "ja": "AEDの電源を入れ、音声ガイダンスに従ってください。",
        "zh": "打开AED电源，按照语音提示操作。",
        "hi": "AED चालू करें और उसकी आवाज़ के निर्देशों का पालन करें।",
        "ar": "شغّل جهاز الصدمات واتبع إرشاداته الصوتية.",
    },
    "Expose the chest and attach the pads as shown on the pad diagrams.": {
        "es": "Descubra el pecho y coloque los parches como muestran los "
              "diagramas.",
        "fr": "Dégagez la poitrine et placez les électrodes comme indiqué "
              "sur les schémas.",
        "de": "Machen Sie den Brustkorb frei und kleben Sie die Elektroden "
              "wie auf den Abbildungen gezeigt auf.",
        "pt": "Exponha o peito e aplique as pás conforme mostrado nos "
              "diagramas.",
        "it": "Scopra il torace e applichi le piastre come mostrato nei "
              "diagrammi.",
        "ja": "胸をはだけ、図に示されたとおりにパッドを貼り付けてください。",
        "zh": "露出胸部，按电极片图示位置贴好电极片。",
        "hi": "छाती को खोलें और पैड को चित्रों में दिखाए अनुसार लगाएँ।",
        "ar": "اكشف الصدر وثبّت اللصائق كما هو موضح في الرسوم التوضيحية.",
    },
    "Stand clear while the AED analyzes the rhythm — touch no one.": {
        "es": "Apártese mientras el DEA analiza el ritmo — que nadie toque a "
              "la persona.",
        "fr": "Écartez-vous pendant que le DEA analyse le rythme — que "
              "personne ne touche la personne.",
        "de": "Treten Sie zurück, während der AED den Rhythmus analysiert — "
              "niemanden berühren.",
        "pt": "Afaste-se enquanto o DEA analisa o ritmo — ninguém deve tocar "
              "na pessoa.",
        "it": "Si allontani mentre il DAE analizza il ritmo — nessuno tocchi "
              "la persona.",
        "ja": "AEDが心リズムを解析する間は離れてください。誰も触れてはいけません。",
        "zh": "AED分析心律时请远离——任何人都不要接触患者。",
        "hi": "जब AED हृदय-गति का विश्लेषण करे तो दूर रहें — कोई भी व्यक्ति को न छुए।",
        "ar": "ابتعد أثناء تحليل الجهاز لنظم القلب — ولا يلمس أحد المصاب.",
    },
    "If a shock is advised, make sure no one is touching the person, "
    "then press the shock button.": {
        "es": "Si se aconseja una descarga, asegúrese de que nadie toque a "
              "la persona y pulse el botón de descarga.",
        "fr": "Si un choc est conseillé, assurez-vous que personne ne touche "
              "la personne, puis appuyez sur le bouton de choc.",
        "de": "Wird ein Schock empfohlen, stellen Sie sicher, dass niemand "
              "die Person berührt, und drücken Sie dann die Schocktaste.",
        "pt": "Se um choque for indicado, garanta que ninguém está tocando "
              "na pessoa e pressione o botão de choque.",
        "it": "Se viene consigliata una scarica, si assicuri che nessuno "
              "tocchi la persona, poi prema il pulsante di scarica.",
        "ja": "ショックが必要と判断されたら、誰も触れていないことを確認し、ショックボタンを押してください。",
        "zh": "如果建议电击，确认无人接触患者后按下电击按钮。",
        "hi": "यदि शॉक की सलाह दी जाए, तो सुनिश्चित करें कि कोई व्यक्ति को नहीं छू रहा है, फिर शॉक बटन दबाएँ।",
        "ar": "إذا نُصح بالصدمة، فتأكد من عدم لمس أي شخص للمصاب، ثم اضغط زر الصدمة.",
    },
    "Resume CPR immediately after the shock (30:2) until the AED "
    "re-analyzes or help arrives.": {
        "es": "Reanude la RCP inmediatamente después de la descarga (30:2) "
              "hasta que el DEA vuelva a analizar o llegue la ayuda.",
        "fr": "Reprenez la RCP immédiatement après le choc (30:2) jusqu'à ce "
              "que le DEA analyse de nouveau ou que les secours arrivent.",
        "de": "Setzen Sie die HLW sofort nach dem Schock fort (30:2), bis "
              "der AED erneut analysiert oder Hilfe eintrifft.",
        "pt": "Retome a RCP imediatamente após o choque (30:2) até o DEA "
              "reanalisar ou a ajuda chegar.",
        "it": "Riprenda la RCP subito dopo la scarica (30:2) finché il DAE "
              "non rianalizza o arrivano i soccorsi.",
        "ja": "ショック後は直ちに心肺蘇生を再開し（30:2）、AEDが再解析するか救助が到着するまで続けてください。",
        "zh": "电击后立即恢复心肺复苏（30:2），直到AED再次分析或救援到达。",
        "hi": "शॉक के तुरंत बाद सीपीआर (30:2) फिर से शुरू करें, जब तक AED दोबारा विश्लेषण न करे या मदद न आ जाए।",
        "ar": "استأنف الإنعاش القلبي الرئوي فورًا بعد الصدمة (30:2) حتى يعيد الجهاز التحليل أو تصل المساعدة.",
    },
    # -- waiver terms ---------------------------------------------------------
    "I authorize my bound, CPR-rated robots to begin hands-only CPR "
    "automatically when a cardiac arrest is detected, without waiting for "
    "an on-scene confirmation.": {
        "es": "Autorizo a mis robots vinculados con certificación de RCP a "
              "iniciar automáticamente la RCP solo con las manos cuando se "
              "detecte un paro cardíaco, sin esperar una confirmación en el "
              "lugar.",
        "fr": "J'autorise mes robots liés certifiés RCP à commencer "
              "automatiquement la RCP à mains seules lorsqu'un arrêt "
              "cardiaque est détecté, sans attendre de confirmation sur "
              "place.",
        "de": "Ich ermächtige meine gekoppelten, CPR-zertifizierten Roboter, "
              "bei Erkennung eines Herzstillstands automatisch mit der "
              "Herzdruckmassage zu beginnen, ohne auf eine Bestätigung vor "
              "Ort zu warten.",
        "pt": "Autorizo meus robôs vinculados com certificação de RCP a "
              "iniciar automaticamente a RCP somente com as mãos quando uma "
              "parada cardíaca for detectada, sem aguardar confirmação no "
              "local.",
        "it": "Autorizzo i miei robot associati certificati per la RCP ad "
              "avviare automaticamente la RCP con le sole mani quando viene "
              "rilevato un arresto cardiaco, senza attendere una conferma "
              "sul posto.",
        "ja": "心停止が検知された際、現場での確認を待たずに、連携済みのCPR対応ロボットが自動的に胸骨圧迫のみの心肺蘇生を開始することを許可します。",
        "zh": "我授权与我绑定的具备CPR能力的机器人在检测到心脏骤停时自动开始单纯胸外按压心肺复苏，无需等待现场确认。",
        "hi": "मैं अपने बंधे हुए, सीपीआर-प्रमाणित रोबोटों को अधिकृत करता/करती हूँ कि हृदय-गति रुकने का पता चलने पर, स्थल पर पुष्टि की प्रतीक्षा किए बिना, स्वचालित रूप से केवल-हाथों से सीपीआर शुरू करें।",
        "ar": "أُفوِّض روبوتاتي المرتبطة والمعتمدة للإنعاش القلبي الرئوي ببدء الإنعاش بالضغط اليدوي تلقائيًا عند اكتشاف توقف القلب، دون انتظار تأكيد في الموقع.",
    },
    "I authorize the use of a fully-automatic AED: the device analyzes my "
    "heart rhythm and delivers a shock on its own analysis after the robot "
    "verifies everyone is clear — no button press.": {
        "es": "Autorizo el uso de un DEA totalmente automático: el "
              "dispositivo analiza mi ritmo cardíaco y administra una "
              "descarga según su propio análisis, después de que el robot "
              "verifique que nadie está en contacto — sin pulsar botón.",
        "fr": "J'autorise l'utilisation d'un DEA entièrement automatique : "
              "l'appareil analyse mon rythme cardiaque et délivre un choc "
              "selon sa propre analyse, après que le robot a vérifié que "
              "personne n'est en contact — sans appui sur un bouton.",
        "de": "Ich ermächtige den Einsatz eines vollautomatischen AED: Das "
              "Gerät analysiert meinen Herzrhythmus und gibt auf Grundlage "
              "seiner eigenen Analyse einen Schock ab, nachdem der Roboter "
              "sichergestellt hat, dass niemand die Person berührt — ohne "
              "Tastendruck.",
        "pt": "Autorizo o uso de um DEA totalmente automático: o aparelho "
              "analisa meu ritmo cardíaco e aplica um choque com base em sua "
              "própria análise, depois que o robô verifica que ninguém está "
              "em contato — sem apertar botão.",
        "it": "Autorizzo l'uso di un DAE completamente automatico: il "
              "dispositivo analizza il mio ritmo cardiaco ed eroga una "
              "scarica in base alla propria analisi, dopo che il robot ha "
              "verificato che nessuno è a contatto — senza premere alcun "
              "pulsante.",
        "ja": "全自動AEDの使用を許可します。装置が心リズムを解析し、ロボットが誰も触れていないことを確認した後、装置自身の判断で電気ショックを実施します（ボタン操作なし）。",
        "zh": "我授权使用全自动AED：设备分析我的心律，在机器人确认无人接触后，依据其自身分析自动施放电击——无需按键。",
        "hi": "मैं पूर्ण-स्वचालित AED के उपयोग को अधिकृत करता/करती हूँ: उपकरण मेरी हृदय-गति का विश्लेषण करता है और रोबोट द्वारा यह सत्यापित करने के बाद कि कोई नहीं छू रहा है, अपने विश्लेषण के आधार पर शॉक देता है — बिना बटन दबाए।",
        "ar": "أُفوِّض استخدام جهاز صدمات آلي بالكامل: يحلل الجهاز نظم قلبي ويُطلق الصدمة بناءً على تحليله بعد أن يتحقق الروبوت من ابتعاد الجميع — دون ضغط زر.",
    },
    "I understand a shock is only ever delivered when the AED's rhythm "
    "analysis advises it — never on the robot's own judgement.": {
        "es": "Entiendo que una descarga solo se administra cuando el "
              "análisis del ritmo del DEA la aconseja — nunca por decisión "
              "propia del robot.",
        "fr": "Je comprends qu'un choc n'est délivré que lorsque l'analyse "
              "du rythme du DEA le conseille — jamais sur le seul jugement "
              "du robot.",
        "de": "Ich verstehe, dass ein Schock nur dann abgegeben wird, wenn "
              "die Rhythmusanalyse des AED ihn empfiehlt — niemals nach "
              "eigenem Ermessen des Roboters.",
        "pt": "Entendo que um choque só é aplicado quando a análise de ritmo "
              "do DEA o indica — nunca pelo julgamento próprio do robô.",
        "it": "Comprendo che una scarica viene erogata solo quando l'analisi "
              "del ritmo del DAE la consiglia — mai per decisione autonoma "
              "del robot.",
        "ja": "電気ショックはAEDのリズム解析が必要と判断した場合にのみ実施され、ロボット自身の判断では決して行われないことを理解しています。",
        "zh": "我理解只有当AED的心律分析建议时才会施放电击——绝不会由机器人自行判断。",
        "hi": "मैं समझता/समझती हूँ कि शॉक केवल तभी दिया जाता है जब AED का हृदय-गति विश्लेषण इसकी सलाह दे — कभी भी रोबोट के अपने निर्णय से नहीं।",
        "ar": "أفهم أن الصدمة لا تُعطى إلا عندما يوصي بها تحليل نظم القلب في الجهاز — وليس أبدًا بقرار من الروبوت نفسه.",
    },
    "I accept liability for automatic operation and waive claims arising "
    "from resuscitation performed in good faith under this authorization.": {
        "es": "Acepto la responsabilidad por el funcionamiento automático y "
              "renuncio a reclamaciones derivadas de una reanimación "
              "realizada de buena fe bajo esta autorización.",
        "fr": "J'accepte la responsabilité du fonctionnement automatique et "
              "renonce à toute réclamation découlant d'une réanimation "
              "effectuée de bonne foi en vertu de cette autorisation.",
        "de": "Ich übernehme die Haftung für den automatischen Betrieb und "
              "verzichte auf Ansprüche aus einer in gutem Glauben unter "
              "dieser Ermächtigung durchgeführten Wiederbelebung.",
        "pt": "Aceito a responsabilidade pela operação automática e renuncio "
              "a reivindicações decorrentes de reanimação realizada de "
              "boa-fé sob esta autorização.",
        "it": "Accetto la responsabilità del funzionamento automatico e "
              "rinuncio a rivendicazioni derivanti da una rianimazione "
              "eseguita in buona fede in base a questa autorizzazione.",
        "ja": "自動動作に伴う責任を受け入れ、本許可の下で誠実に行われた蘇生行為に起因する請求を放棄します。",
        "zh": "我接受自动操作的责任，并放弃因依据本授权善意实施的复苏行为而产生的索赔。",
        "hi": "मैं स्वचालित संचालन की ज़िम्मेदारी स्वीकार करता/करती हूँ और इस प्राधिकरण के तहत सद्भावना से किए गए पुनर्जीवन से उत्पन्न दावों का त्याग करता/करती हूँ।",
        "ar": "أقبل المسؤولية عن التشغيل التلقائي وأتنازل عن المطالبات الناشئة عن إنعاش أُجري بحسن نية بموجب هذا التفويض.",
    },
    "Emergency services are always called first; automatic operation ends "
    "the moment human responders take over.": {
        "es": "Siempre se llama primero a los servicios de emergencia; el "
              "funcionamiento automático termina en cuanto los socorristas "
              "humanos toman el control.",
        "fr": "Les services d'urgence sont toujours appelés en premier ; le "
              "fonctionnement automatique cesse dès que les secouristes "
              "humains prennent le relais.",
        "de": "Der Notruf wird immer zuerst abgesetzt; der automatische "
              "Betrieb endet, sobald menschliche Einsatzkräfte übernehmen.",
        "pt": "Os serviços de emergência são sempre chamados primeiro; a "
              "operação automática termina no momento em que socorristas "
              "humanos assumem.",
        "it": "I servizi di emergenza vengono sempre chiamati per primi; il "
              "funzionamento automatico termina nel momento in cui i "
              "soccorritori umani subentrano.",
        "ja": "常にまず救急に通報します。人間の救助者が引き継いだ時点で自動動作は終了します。",
        "zh": "始终先呼叫急救服务；人类救援人员接手的那一刻，自动操作即告结束。",
        "hi": "आपातकालीन सेवाओं को हमेशा पहले बुलाया जाता है; जैसे ही मानव बचावकर्मी संभालते हैं, स्वचालित संचालन समाप्त हो जाता है।",
        "ar": "يُستدعى الطوارئ دائمًا أولًا؛ وينتهي التشغيل التلقائي لحظة تولي المسعفين البشر.",
    },
    "I may revoke this waiver at any time, restoring confirm-gated "
    "operation.": {
        "es": "Puedo revocar esta exención en cualquier momento, "
              "restableciendo el funcionamiento con confirmación.",
        "fr": "Je peux révoquer cette décharge à tout moment, rétablissant "
              "le fonctionnement avec confirmation.",
        "de": "Ich kann diese Einwilligung jederzeit widerrufen; dann gilt "
              "wieder der Betrieb mit Bestätigung.",
        "pt": "Posso revogar esta autorização a qualquer momento, "
              "restaurando a operação com confirmação.",
        "it": "Posso revocare questa liberatoria in qualsiasi momento, "
              "ripristinando il funzionamento con conferma.",
        "ja": "この同意はいつでも撤回でき、その場合は確認を要する動作に戻ります。",
        "zh": "我可以随时撤销本弃权书，恢复需确认的操作模式。",
        "hi": "मैं इस छूट-पत्र को किसी भी समय रद्द कर सकता/सकती हूँ, जिससे पुष्टि-आधारित संचालन बहाल हो जाएगा।",
        "ar": "يمكنني إلغاء هذا التنازل في أي وقت، فيعود التشغيل المشروط بالتأكيد.",
    },

    # ---- the scanned care beacon (jim/landing.py) ----------------------
    #
    # Safety text on the one page in this product read by somebody with no
    # account, chosen from their own Accept-Language rather than from a
    # setting they have never had. Hand-translated like every other string
    # here, and for the same reason: a person reading instructions about a
    # body on the floor is the last person who should be handed a machine
    # translation.
    # `relay.STANDING` — the answer the guidance route gives when no
    # specialist is reachable. The most-read sentence in the product on the
    # worst day somebody has, and the one a machine translation is least
    # welcome in.
    "Call your local emergency number if you have not already. Do not move "
    "them unless they are in danger where they are. Stay with them until "
    "someone arrives.": {
        "es": "Llame al número de emergencias local si aún no lo ha hecho. No "
              "les mueva salvo que corran peligro donde están. Quédese con "
              "ellos hasta que llegue alguien.",
        "fr": "Appelez votre numéro d'urgence local si ce n'est pas déjà "
              "fait. Ne les déplacez pas sauf s'ils sont en danger là où ils "
              "sont. Restez avec eux jusqu'à l'arrivée des secours.",
        "de": "Rufen Sie den örtlichen Notruf an, falls noch nicht geschehen. "
              "Bewegen Sie die Person nicht, außer sie ist dort in Gefahr. "
              "Bleiben Sie bei ihr, bis Hilfe eintrifft.",
        "pt": "Ligue para o número de emergência local se ainda não o fez. "
              "Não os mova, a menos que estejam em perigo onde estão. Fique "
              "com eles até alguém chegar.",
        "it": "Chiama il numero di emergenza locale se non l'hai già fatto. "
              "Non spostarli, a meno che non siano in pericolo dove si "
              "trovano. Resta con loro finché non arriva qualcuno.",
        "ja": "まだであれば地域の緊急通報番号に電話してください。その場に危険がない限り"
              "動かさないでください。誰かが到着するまでそばにいてください。",
        "zh": "若尚未拨打，请拨打当地急救电话。除非原地有危险，否则不要移动对方。"
              "请陪在他们身边，直到有人到达。",
        "hi": "यदि अभी तक नहीं किया है तो अपने स्थानीय आपातकालीन नंबर पर कॉल करें। जब तक "
              "वे वहाँ खतरे में न हों, उन्हें हिलाएँ नहीं। किसी के आने तक उनके साथ रहें।",
        "ar": "اتصل برقم الطوارئ المحلي إن لم تكن قد فعلت. لا تحرّكهم إلا إذا كانوا في "
              "خطر في مكانهم. ابقَ معهم حتى يصل أحد.",
    },
    "standing guidance — no specialist was reachable": {
        "es": "orientación estándar: no se pudo contactar con un especialista",
        "fr": "conseils par défaut — aucun spécialiste joignable",
        "de": "Standardhinweise — kein Fachdienst erreichbar",
        "pt": "orientação padrão — nenhum especialista contactável",
        "it": "indicazioni standard — nessuno specialista raggiungibile",
        "ja": "標準の案内 — 専門家に接続できませんでした",
        "zh": "标准指引 — 未能联系到专业人员",
        "hi": "मानक मार्गदर्शन — कोई विशेषज्ञ उपलब्ध नहीं था",
        "ar": "إرشادات قياسية — تعذّر الوصول إلى مختص",
    },
    "This code doesn't resolve to anything": {
        "es": "Este código no corresponde a nada",
        "fr": "Ce code ne correspond à rien",
        "de": "Dieser Code führt zu nichts",
        "pt": "Este código não corresponde a nada",
        "it": "Questo codice non corrisponde a nulla",
        "ja": "このコードは何にも対応していません",
        "zh": "此二维码没有对应的内容",
        "hi": "यह कोड किसी से मेल नहीं खाता",
        "ar": "هذا الرمز لا يشير إلى شيء",
    },
    "It may have been removed, or it may never have been one of ours. If "
    "someone in front of you needs help, call your local emergency number — "
    "this page cannot.": {
        "es": "Puede haberse retirado, o puede que nunca fuera nuestro. Si "
              "alguien delante de usted necesita ayuda, llame al número de "
              "emergencias local: esta página no puede.",
        "fr": "Il a pu être retiré, ou n'a peut-être jamais été le nôtre. Si "
              "quelqu'un devant vous a besoin d'aide, appelez votre numéro "
              "d'urgence local — cette page ne le peut pas.",
        "de": "Er wurde vielleicht entfernt oder war nie einer von unseren. "
              "Wenn jemand vor Ihnen Hilfe braucht, rufen Sie den örtlichen "
              "Notruf — diese Seite kann das nicht.",
        "pt": "Pode ter sido removido, ou pode nunca ter sido nosso. Se "
              "alguém à sua frente precisa de ajuda, ligue para o número de "
              "emergência local — esta página não pode.",
        "it": "Può essere stato rimosso, o non essere mai stato nostro. Se "
              "qualcuno davanti a te ha bisogno di aiuto, chiama il numero "
              "di emergenza locale — questa pagina non può farlo.",
        "ja": "取り外されたか、もともと当方のものではない可能性があります。"
              "目の前の人に助けが必要なら、地域の緊急通報番号に電話してください — "
              "このページにはできません。",
        "zh": "它可能已被取下，也可能从来就不是我们的。如果你面前的人需要帮助，"
              "请拨打当地急救电话 — 本页面做不到。",
        "hi": "हो सकता है इसे हटा दिया गया हो, या यह कभी हमारा रहा ही न हो। यदि आपके "
              "सामने किसी को मदद चाहिए, तो अपने स्थानीय आपातकालीन नंबर पर कॉल करें — "
              "यह पृष्ठ ऐसा नहीं कर सकता।",
        "ar": "ربما أُزيل، أو ربما لم يكن لنا أصلًا. إذا كان أمامك شخص يحتاج المساعدة، "
              "فاتصل برقم الطوارئ المحلي — هذه الصفحة لا تستطيع.",
    },
    "You've found someone.": {
        "es": "Has encontrado a alguien.",
        "fr": "Vous avez trouvé quelqu'un.",
        "de": "Sie haben jemanden gefunden.",
        "pt": "Encontrou alguém.",
        "it": "Hai trovato qualcuno.",
        "ja": "誰かを見つけました。",
        "zh": "你发现了一个人。",
        "hi": "आपको कोई मिला है।",
        "ar": "لقد وجدت شخصًا ما.",
    },
    "If this is an emergency, call your local emergency number first.": {
        "es": "Si es una emergencia, llame primero al número de emergencias "
              "local.",
        "fr": "En cas d'urgence, appelez d'abord votre numéro d'urgence "
              "local.",
        "de": "Rufen Sie im Notfall zuerst Ihren örtlichen Notruf an.",
        "pt": "Se for uma emergência, ligue primeiro para o número de "
              "emergência local.",
        "it": "Se è un'emergenza, chiama prima il numero di emergenza "
              "locale.",
        "ja": "緊急の場合は、まず地域の緊急通報番号に電話してください。",
        "zh": "如果情况紧急，请先拨打当地急救电话。",
        "hi": "यदि यह आपात स्थिति है, तो पहले अपने स्थानीय आपातकालीन नंबर पर कॉल करें।",
        "ar": "إذا كانت هذه حالة طارئة، اتصل أولًا برقم الطوارئ المحلي.",
    },
    "This page cannot call anyone for you, and it is not an emergency "
    "service.": {
        "es": "Esta página no puede llamar a nadie por usted y no es un "
              "servicio de emergencias.",
        "fr": "Cette page ne peut appeler personne à votre place et n'est "
              "pas un service d'urgence.",
        "de": "Diese Seite kann für Sie niemanden anrufen und ist kein "
              "Notdienst.",
        "pt": "Esta página não pode ligar para ninguém por si e não é um "
              "serviço de emergência.",
        "it": "Questa pagina non può chiamare nessuno per te e non è un "
              "servizio di emergenza.",
        "ja": "このページはあなたの代わりに電話をかけることはできず、緊急サービスでもありません。",
        "zh": "本页面无法替你拨打电话，也不是急救服务。",
        "hi": "यह पृष्ठ आपकी ओर से किसी को कॉल नहीं कर सकता, और यह आपातकालीन सेवा नहीं है।",
        "ar": "لا يمكن لهذه الصفحة الاتصال بأحد نيابة عنك، وهي ليست خدمة طوارئ.",
    },
    "Anything you can tell them? (optional)": {
        "es": "¿Algo que pueda decirles? (opcional)",
        "fr": "Quelque chose à leur dire ? (facultatif)",
        "de": "Etwas, das Sie ihnen sagen können? (optional)",
        "pt": "Algo que lhes possa dizer? (opcional)",
        "it": "Qualcosa da dire loro? (facoltativo)",
        "ja": "伝えられることはありますか？（任意）",
        "zh": "有什么可以告诉他们的吗？（可选）",
        "hi": "कुछ बता सकते हैं? (वैकल्पिक)",
        "ar": "هل من شيء يمكنك إخبارهم به؟ (اختياري)",
    },
    "where you are, what you can see": {
        "es": "dónde está, qué puede ver",
        "fr": "où vous êtes, ce que vous voyez",
        "de": "wo Sie sind, was Sie sehen",
        "pt": "onde está, o que consegue ver",
        "it": "dove sei, cosa vedi",
        "ja": "どこにいるか、何が見えるか",
        "zh": "你在哪里，你看到了什么",
        "hi": "आप कहाँ हैं, आपको क्या दिख रहा है",
        "ar": "أين أنت، وما الذي تراه",
    },
    "Raise the alarm": {
        "es": "Dar la alarma",
        "fr": "Donner l'alerte",
        "de": "Alarm auslösen",
        "pt": "Dar o alarme",
        "it": "Dai l'allarme",
        "ja": "通報する",
        "zh": "发出警报",
        "hi": "अलार्म बजाएँ",
        "ar": "أطلق الإنذار",
    },
    "Raising…": {
        "es": "Enviando…",
        "fr": "Envoi…",
        "de": "Wird ausgelöst…",
        "pt": "A enviar…",
        "it": "Invio…",
        "ja": "通報中…",
        "zh": "正在发出…",
        "hi": "भेजा जा रहा है…",
        "ar": "جارٍ الإرسال…",
    },
    "That did not go through.": {
        "es": "No se ha podido enviar.",
        "fr": "L'envoi n'a pas abouti.",
        "de": "Das hat nicht funktioniert.",
        "pt": "Não foi possível enviar.",
        "it": "Non è andato a buon fine.",
        "ja": "送信できませんでした。",
        "zh": "未能发送。",
        "hi": "यह नहीं भेजा जा सका।",
        "ar": "لم يتم الإرسال.",
    },
    "No connection — call your local emergency number.": {
        "es": "Sin conexión: llame al número de emergencias local.",
        "fr": "Pas de connexion — appelez votre numéro d'urgence local.",
        "de": "Keine Verbindung — rufen Sie Ihren örtlichen Notruf an.",
        "pt": "Sem ligação — ligue para o número de emergência local.",
        "it": "Nessuna connessione — chiama il numero di emergenza locale.",
        "ja": "接続がありません — 地域の緊急通報番号に電話してください。",
        "zh": "没有网络连接 — 请拨打当地急救电话。",
        "hi": "कोई कनेक्शन नहीं — अपने स्थानीय आपातकालीन नंबर पर कॉल करें।",
        "ar": "لا يوجد اتصال — اتصل برقم الطوارئ المحلي.",
    },
    "MEDICAL ID": {
        "es": "IDENTIFICACIÓN MÉDICA",
        "fr": "FICHE MÉDICALE",
        "de": "NOTFALLPASS",
        "pt": "IDENTIFICAÇÃO MÉDICA",
        "it": "SCHEDA MEDICA",
        "ja": "メディカルID",
        "zh": "医疗卡",
        "hi": "मेडिकल आईडी",
        "ar": "البطاقة الطبية",
    },
    "Name": {
        "es": "Nombre", "fr": "Nom", "de": "Name", "pt": "Nome",
        "it": "Nome", "ja": "氏名", "zh": "姓名", "hi": "नाम",
        "ar": "الاسم",
    },
    "Age": {
        "es": "Edad", "fr": "Âge", "de": "Alter", "pt": "Idade",
        "it": "Età", "ja": "年齢", "zh": "年龄", "hi": "आयु",
        "ar": "العمر",
    },
    "Known conditions": {
        "es": "Afecciones conocidas",
        "fr": "Pathologies connues",
        "de": "Bekannte Erkrankungen",
        "pt": "Condições conhecidas",
        "it": "Patologie note",
        "ja": "既往症",
        "zh": "已知病症",
        "hi": "ज्ञात स्थितियाँ",
        "ar": "حالات معروفة",
    },
    "Resting heart rate": {
        "es": "Frecuencia cardíaca en reposo",
        "fr": "Fréquence cardiaque au repos",
        "de": "Ruhepuls",
        "pt": "Frequência cardíaca em repouso",
        "it": "Frequenza cardiaca a riposo",
        "ja": "安静時心拍数",
        "zh": "静息心率",
        "hi": "विश्राम हृदय गति",
        "ar": "معدل ضربات القلب أثناء الراحة",
    },
    "Emergency contact": {
        "es": "Contacto de emergencia",
        "fr": "Contact d'urgence",
        "de": "Notfallkontakt",
        "pt": "Contacto de emergência",
        "it": "Contatto di emergenza",
        "ja": "緊急連絡先",
        "zh": "紧急联系人",
        "hi": "आपातकालीन संपर्क",
        "ar": "جهة اتصال للطوارئ",
    },
    "What do I do while you wait?": {
        "es": "¿Qué hago mientras espera?",
        "fr": "Que faire en attendant ?",
        "de": "Was tue ich, während Sie warten?",
        "pt": "O que faço enquanto espera?",
        "it": "Cosa faccio nell'attesa?",
        "ja": "待っている間、何をすればよいですか？",
        "zh": "等待期间我该做什么？",
        "hi": "प्रतीक्षा के दौरान मैं क्या करूँ?",
        "ar": "ماذا أفعل في أثناء الانتظار؟",
    },
    "Guidance, not a clinician — it cannot see them, and it cannot call "
    "anyone.": {
        "es": "Orientación, no un profesional sanitario: no puede verles ni "
              "llamar a nadie.",
        "fr": "Des conseils, pas un soignant — il ne les voit pas et ne peut "
              "appeler personne.",
        "de": "Hinweise, keine ärztliche Beratung — sie sieht die Person "
              "nicht und kann niemanden anrufen.",
        "pt": "Orientação, não um clínico — não os vê nem pode ligar a "
              "ninguém.",
        "it": "Indicazioni, non un medico — non può vederli né chiamare "
              "nessuno.",
        "ja": "案内であり、医療者ではありません。相手を見ることも、電話をかけることもできません。",
        "zh": "这是指引，不是临床医生 — 它看不到对方，也无法拨打电话。",
        "hi": "मार्गदर्शन, चिकित्सक नहीं — यह उन्हें देख नहीं सकता, और किसी को कॉल नहीं कर सकता।",
        "ar": "إرشادات، وليست طبيبًا — لا يمكنها رؤيتهم ولا الاتصال بأحد.",
    },
    "What is happening?": {
        "es": "¿Qué está pasando?",
        "fr": "Que se passe-t-il ?",
        "de": "Was ist passiert?",
        "pt": "O que está a acontecer?",
        "it": "Cosa sta succedendo?",
        "ja": "何が起きていますか？",
        "zh": "发生了什么？",
        "hi": "क्या हो रहा है?",
        "ar": "ماذا يحدث؟",
    },
    "breathing, but will not wake up": {
        "es": "respira, pero no despierta",
        "fr": "respire, mais ne se réveille pas",
        "de": "atmet, wacht aber nicht auf",
        "pt": "respira, mas não acorda",
        "it": "respira, ma non si sveglia",
        "ja": "呼吸はあるが、目を覚まさない",
        "zh": "有呼吸，但叫不醒",
        "hi": "साँस चल रही है, पर होश नहीं आ रहा",
        "ar": "يتنفّس، لكنه لا يستيقظ",
    },
    "Ask": {
        "es": "Preguntar", "fr": "Demander", "de": "Fragen",
        "pt": "Perguntar", "it": "Chiedi", "ja": "きく", "zh": "询问",
        "hi": "पूछें", "ar": "اسأل",
    },
    "Ask again": {
        "es": "Preguntar otra vez",
        "fr": "Redemander",
        "de": "Erneut fragen",
        "pt": "Perguntar de novo",
        "it": "Chiedi di nuovo",
        "ja": "もう一度きく",
        "zh": "再次询问",
        "hi": "फिर पूछें",
        "ar": "اسأل مرة أخرى",
    },
    "Asking…": {
        "es": "Preguntando…", "fr": "Envoi…", "de": "Wird gefragt…",
        "pt": "A perguntar…", "it": "Invio…", "ja": "問い合わせ中…",
        "zh": "正在询问…", "hi": "पूछा जा रहा है…", "ar": "جارٍ السؤال…",
    },
    # The offline answer. Identical in meaning to relay.guidance's fallback,
    # and it has to be, because this is the copy shown when the network is
    # gone and the server's version cannot arrive.
    "No connection. Call your local emergency number if you have not "
    "already. Do not move them unless they are in danger where they are. "
    "Stay with them until someone arrives.": {
        "es": "Sin conexión. Llame al número de emergencias local si aún no "
              "lo ha hecho. No les mueva salvo que corran peligro donde "
              "están. Quédese con ellos hasta que llegue alguien.",
        "fr": "Pas de connexion. Appelez votre numéro d'urgence local si ce "
              "n'est pas déjà fait. Ne les déplacez pas sauf s'ils sont en "
              "danger là où ils sont. Restez avec eux jusqu'à l'arrivée des "
              "secours.",
        "de": "Keine Verbindung. Rufen Sie den örtlichen Notruf an, falls "
              "noch nicht geschehen. Bewegen Sie die Person nicht, außer sie "
              "ist dort in Gefahr. Bleiben Sie bei ihr, bis Hilfe eintrifft.",
        "pt": "Sem ligação. Ligue para o número de emergência local se ainda "
              "não o fez. Não os mova, a menos que estejam em perigo onde "
              "estão. Fique com eles até alguém chegar.",
        "it": "Nessuna connessione. Chiama il numero di emergenza locale se "
              "non l'hai già fatto. Non spostarli, a meno che non siano in "
              "pericolo dove si trovano. Resta con loro finché non arriva "
              "qualcuno.",
        "ja": "接続がありません。まだであれば地域の緊急通報番号に電話してください。"
              "その場に危険がない限り動かさないでください。誰かが到着するまで"
              "そばにいてください。",
        "zh": "没有网络连接。若尚未拨打，请拨打当地急救电话。除非原地有危险，"
              "否则不要移动对方。请陪在他们身边，直到有人到达。",
        "hi": "कोई कनेक्शन नहीं। यदि अभी तक नहीं किया है तो अपने स्थानीय आपातकालीन नंबर पर "
              "कॉल करें। जब तक वे वहाँ खतरे में न हों, उन्हें हिलाएँ नहीं। किसी के आने तक "
              "उनके साथ रहें।",
        "ar": "لا يوجد اتصال. اتصل برقم الطوارئ المحلي إن لم تكن قد فعلت. لا تحرّكهم "
              "إلا إذا كانوا في خطر في مكانهم. ابقَ معهم حتى يصل أحد.",
    },
    'Someone is watching over this person': {
        'es': 'Alguien vela por esta persona',
        'fr': "Quelqu'un veille sur cette personne",
        'de': 'Jemand wacht über diese Person',
        'pt': 'Alguém está a velar por esta pessoa',
        'it': 'Qualcuno veglia su questa persona',
        'ja': 'この人を見守っている人がいます',
        'zh': '有人在照看这个人',
        'hi': 'कोई इस व्यक्ति का ध्यान रख रहा है',
        'ar': 'هناك من يرعى هذا الشخص',
    },
    'Nothing here': {
        'es': 'Nada aquí',
        'fr': 'Rien ici',
        'de': 'Nichts hier',
        'pt': 'Nada aqui',
        'it': 'Niente qui',
        'ja': '何もありません',
        'zh': '这里没有内容',
        'hi': 'यहाँ कुछ नहीं',
        'ar': 'لا شيء هنا',
    },
    "You've found {name}.": {
        'es': 'Ha encontrado a {name}.',
        'fr': 'Vous avez trouvé {name}.',
        'de': 'Sie haben {name} gefunden.',
        'pt': 'Encontrou {name}.',
        'it': 'Hai trovato {name}.',
        'ja': '{name} さんを見つけました。',
        'zh': '你找到了 {name}。',
        'hi': 'आपको {name} मिले हैं।',
        'ar': 'لقد وجدت {name}.',
    },
    'This is a workplace site. Raising the alarm reaches whoever is on call.': {
        'es': 'Este es un centro de trabajo. Dar la alarma avisa a quien esté de guardia.',
        'fr': "Ceci est un site professionnel. Donner l'alerte joint la personne d'astreinte.",
        'de': 'Dies ist ein Arbeitsstandort. Der Alarm erreicht die Person mit Bereitschaft.',
        'pt': 'Este é um local de trabalho. Dar o alarme chega a quem está de plantão.',
        'it': "Questo è un sito di lavoro. Dare l'allarme raggiunge chi è di turno.",
        'ja': 'ここは職場の拠点です。通報すると、待機している担当者に届きます。',
        'zh': '这里是工作场所。发出警报会通知当班的人。',
        'hi': 'यह एक कार्यस्थल है। अलार्म देने पर वह व्यक्ति तक पहुँचता है जो ड्यूटी पर है।',
        'ar': 'هذا موقع عمل. إطلاق الإنذار يصل إلى المناوب.',
    },
    'Raising the alarm alerts the people who watch over this person. It does not tell you how they are, and nothing on this page says where they live.': {
        'es': 'Dar la alarma avisa a las personas que velan por ella. No le dice a usted cómo se encuentra, y nada en esta página indica dónde vive.',
        'fr': "Donner l'alerte prévient les personnes qui veillent sur elle. Cela ne vous dit pas comment elle va, et rien sur cette page n'indique où elle habite.",
        'de': 'Der Alarm benachrichtigt die Menschen, die über sie wachen. Er sagt Ihnen nicht, wie es ihr geht, und nichts auf dieser Seite verrät, wo sie wohnt.',
        'pt': 'Dar o alarme avisa as pessoas que velam por ela. Não lhe diz como ela está, e nada nesta página indica onde vive.',
        'it': "Dare l'allarme avvisa le persone che vegliano su di lei. Non ti dice come sta, e nulla in questa pagina indica dove abita.",
        'ja': '通報すると、この人を見守っている人たちに知らせが届きます。容体があなたに伝えられることはなく、このページに住所は一切ありません。',
        'zh': '发出警报会通知照看这个人的人。它不会告诉你他们的状况，本页面也不会透露他们住在哪里。',
        'hi': 'अलार्म देने पर उन लोगों को सूचना जाती है जो इस व्यक्ति का ध्यान रखते हैं। यह आपको नहीं बताता कि वे कैसे हैं, और इस पृष्ठ पर कहीं नहीं लिखा कि वे कहाँ रहते हैं।',
        'ar': 'إطلاق الإنذار يُنبّه من يرعون هذا الشخص. لا يخبرك بحاله، ولا شيء في هذه الصفحة يذكر مكان سكنه.',
    },
    'The alarm is raised. This is not an emergency service.': {
        'es': 'La alarma está dada. Esto no es un servicio de emergencias.',
        'fr': "L'alerte est donnée. Ceci n'est pas un service d'urgence.",
        'de': 'Der Alarm ist ausgelöst. Dies ist kein Notdienst.',
        'pt': 'O alarme foi dado. Isto não é um serviço de emergência.',
        'it': "L'allarme è stato dato. Questo non è un servizio di emergenza.",
        'ja': '通報しました。これは緊急通報サービスではありません。',
        'zh': '警报已发出。这不是紧急服务。',
        'hi': 'अलार्म दे दिया गया है। यह कोई आपातकालीन सेवा नहीं है।',
        'ar': 'أُطلق الإنذار. هذه ليست خدمة طوارئ.',
    },
    'A message has been sent to the people watching over this person. If this is an emergency, call your local emergency number — this page cannot.': {
        'es': 'Se ha enviado un mensaje a las personas que velan por ella. Si esto es una emergencia, llame usted al número de emergencias local: esta página no puede.',
        'fr': "Un message a été envoyé aux personnes qui veillent sur elle. En cas d'urgence, appelez vous-même le numéro d'urgence local — cette page ne le peut pas.",
        'de': 'Eine Nachricht wurde an die Menschen gesendet, die über sie wachen. Wenn dies ein Notfall ist, rufen Sie selbst den örtlichen Notruf — diese Seite kann es nicht.',
        'pt': 'Uma mensagem foi enviada às pessoas que velam por ela. Se isto for uma emergência, ligue você para o número de emergência local — esta página não pode.',
        'it': "Un messaggio è stato inviato alle persone che vegliano su di lei. Se questa è un'emergenza, chiama tu il numero di emergenza locale — questa pagina non può.",
        'ja': 'この人を見守っている人たちにメッセージを送信しました。緊急の場合は、あなたご自身で地域の緊急通報番号にかけてください。このページにはできません。',
        'zh': '已向照看这个人的人发送了消息。如果情况紧急，请你自己拨打当地急救电话 — 本页面无法代劳。',
        'hi': 'इस व्यक्ति का ध्यान रखने वालों को एक संदेश भेज दिया गया है। यदि यह आपात स्थिति है तो आप स्वयं अपने स्थानीय आपातकालीन नंबर पर कॉल करें — यह पृष्ठ ऐसा नहीं कर सकता।',
        'ar': 'أُرسلت رسالة إلى من يرعون هذا الشخص. إن كانت هذه حالة طارئة فاتصل أنت برقم الطوارئ المحلي — هذه الصفحة لا تستطيع.',
    },
    "This person's guardian has been sent a message. If this is an emergency, call your local emergency number.": {
        'es': 'Se ha enviado un mensaje a su tutor. Si esto es una emergencia, llame al número de emergencias local.',
        'fr': "Un message a été envoyé à son responsable légal. En cas d'urgence, appelez le numéro d'urgence local.",
        'de': 'Eine Nachricht wurde an die Erziehungsberechtigten gesendet. Wenn dies ein Notfall ist, rufen Sie den örtlichen Notruf.',
        'pt': 'Uma mensagem foi enviada ao responsável desta pessoa. Se isto for uma emergência, ligue para o número de emergência local.',
        'it': "Un messaggio è stato inviato al tutore di questa persona. Se questa è un'emergenza, chiama il numero di emergenza locale.",
        'ja': '保護者にメッセージを送信しました。緊急の場合は、地域の緊急通報番号にかけてください。',
        'zh': '已向该人的监护人发送了消息。如果情况紧急，请拨打当地急救电话。',
        'hi': 'इस व्यक्ति के अभिभावक को एक संदेश भेज दिया गया है। यदि यह आपात स्थिति है तो स्थानीय आपातकालीन नंबर पर कॉल करें।',
        'ar': 'أُرسلت رسالة إلى وليّ أمر هذا الشخص. إن كانت هذه حالة طارئة فاتصل برقم الطوارئ المحلي.',
    },
    'No message went out from this page — the alarm is recorded on this person\'s account. If this is an emergency, call your local emergency number yourself; this page cannot call anyone.': {
        'es': 'Desde esta página no salió ningún mensaje: la alarma queda registrada en su cuenta. Si esto es una emergencia, llame usted mismo al número de emergencias local; esta página no puede llamar a nadie.',
        'fr': "Aucun message n'est parti de cette page — l'alarme est enregistrée sur son compte. En cas d'urgence, appelez vous-même le numéro d'urgence local ; cette page ne peut appeler personne.",
        'de': 'Von dieser Seite ging keine Nachricht hinaus — der Alarm ist auf dem Konto dieser Person vermerkt. Wenn dies ein Notfall ist, rufen Sie selbst den örtlichen Notruf; diese Seite kann niemanden anrufen.',
        'pt': 'Nenhuma mensagem saiu desta página — o alarme fica registado na conta desta pessoa. Se isto for uma emergência, ligue você mesmo para o número de emergência local; esta página não pode ligar para ninguém.',
        'it': "Da questa pagina non è partito alcun messaggio — l'allarme è registrato sull'account di questa persona. Se questa è un'emergenza, chiama tu stesso il numero di emergenza locale; questa pagina non può chiamare nessuno.",
        'ja': 'このページからメッセージは送信されませんでした。警報はこの人のアカウントに記録されています。緊急の場合は、あなたご自身で地域の緊急通報番号にかけてください。このページは誰にも電話をかけられません。',
        'zh': '本页面没有发出任何消息 — 警报已记录在这个人的账户上。如果情况紧急，请你自己拨打当地急救电话；本页面无法给任何人打电话。',
        'hi': 'इस पृष्ठ से कोई संदेश नहीं गया — अलार्म इस व्यक्ति के खाते पर दर्ज है। यदि यह आपात स्थिति है तो आप स्वयं अपने स्थानीय आपातकालीन नंबर पर कॉल करें; यह पृष्ठ किसी को कॉल नहीं कर सकता।',
        'ar': 'لم تخرج أي رسالة من هذه الصفحة — الإنذار مسجَّل في حساب هذا الشخص. إن كانت هذه حالة طارئة فاتصل أنت بنفسك برقم الطوارئ المحلي؛ هذه الصفحة لا تستطيع الاتصال بأحد.',
    },
    'this code does not resolve to anything': {
        'es': 'este código no corresponde a nada',
        'fr': 'ce code ne correspond à rien',
        'de': 'dieser Code führt zu nichts',
        'pt': 'este código não corresponde a nada',
        'it': 'questo codice non corrisponde a nulla',
        'ja': 'このコードは何にも結びついていません',
        'zh': '此代码未对应任何内容',
        'hi': 'यह कोड किसी चीज़ से मेल नहीं खाता',
        'ar': 'هذا الرمز لا يقابل أي شيء',
    },
}


def negotiate(header: str | None) -> str:
    """Pick a supported language from an ``Accept-Language`` header.

    Every other localization path in this product keys off an account
    setting — :func:`get_language` takes a ``user_id``. That is right for
    everything a user reads, and useless for the one page written for
    somebody who has no account: the stranger who scanned a care beacon.

    Their browser has been sending the answer on every request. Nothing read
    it, so a passer-by in Madrid was told in English that they had ninety
    seconds and what to do for the person on the ground.

    Deliberately small: quality values are honoured, the region is dropped
    (``es-419`` and ``es-ES`` are both ``es``), and anything unrecognised
    falls back to English rather than guessing. It chooses **the finder's**
    language, not the watched person's — the text is for whoever is holding
    the phone, and they are by definition not the subject.
    """
    if not header:
        return DEFAULT
    ranked: list[tuple[float, int, str]] = []
    for index, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        quality = 1.0
        for param in params.split(";"):
            key, _, value = param.partition("=")
            if key.strip() == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        base = tag.strip().split("-")[0].lower()
        # `q=0` means **not acceptable** — RFC 9110 is explicit, and a browser
        # that sends `ar;q=0` is refusing Arabic rather than requesting it.
        # This appended regardless, so a header refusing the only tag it named
        # got that tag back: the passer-by's phone said "not this one" and
        # this page answered in it. A malformed `q` lands here too, since the
        # parse failure sets it to zero.
        if base in SUPPORTED and quality > 0:
            # `-index` keeps the header's own order as the tie-break, which
            # is what a client means by listing one tag before another at
            # the same q.
            ranked.append((quality, -index, base))
    if not ranked:
        return DEFAULT
    return max(ranked)[2]


def tr(text: str, language: str) -> str:
    """Hand translation for a known string; English when none exists."""
    if language == DEFAULT:
        return text
    return _STRINGS.get(text, {}).get(language, text)


def localize_strings(items: list[str], language: str) -> list[str]:
    return [tr(s, language) for s in items]


def localize_playbook(playbook: dict, language: str) -> dict:
    """A translated copy of a first-aid playbook (steps + pace cue). Numbers
    and ratios pass through; unknown strings fall back to English."""
    if language == DEFAULT:
        return playbook
    out = dict(playbook)
    out["language"] = language
    out["steps"] = localize_strings(playbook.get("steps", []), language)
    pace = playbook.get("pace")
    if pace:
        pace = dict(pace)
        cue = pace.get("pace_cue")
        if cue:
            pace["pace_cue"] = {k: tr(v, language) for k, v in cue.items()}
        out["pace"] = pace
    return out


# --------------------------------------------------------------------------- #
# The product's own refusals
# --------------------------------------------------------------------------- #
#
# This module's first line says "everything the Guardian drafts or delivers,
# localized", and its second bullet is specific: *deterministic safety content
# is hand-translated here ... Safety text is never machine-mangled.* The
# playbooks are. The pace cues are. The waiver terms are.
#
# The sentences the Guardian says when it says **no** were English — all
# sixty-four of them, including every refusal the medication cabinet, the
# vigil and the crash watch can produce. A person setting up a fall alarm for
# their mother, in Portuguese, on a Portuguese phone, was told in English what
# was wrong with it.
#
#     asked     is the safety content the Guardian drafts translated
#     mattered  is the safety content it refuses with
#
# ## Why one handler is not enough here
#
# QRME has one `HTTPException` handler and that covers its whole surface. JIM
# has **eight more** exception handlers, one per health domain — storage,
# watch, crash watch, calm, fitness, nutrition, vigil, medication — each
# building its own `JSONResponse`. Porting the single handler across would
# have localized the framework's refusals and left every domain's own
# untouched, which in this product is the wrong eight: they are the ones
# somebody reads while a health feature is failing them.
#
#     asked     are the refusals localized
#     mattered  are all of them
#
# `jim/api.py` routes all nine through `refuse()` below, and a guard fails the
# next handler added that does not.
#
# ## Whose language, and which stored value
#
# The credential names the reader — a `user` token means that user's stored
# setting, anything else means the browser header, which is all a stranger on
# a beacon page carries. And `get_language`, not `effective_language`: the
# latter answers English whenever the mode is `on_demand`, which is a
# statement about how *drafted* text arrives ("keep the original medical
# wording, I will translate what I choose") and says nothing about what the
# person reads when something is refused.


#: What a slot may hold and still be dropped into a translated frame.
#:
#: The rule is whitespace. A token — `en`, `openai`, `usr_9f2`, `12.00` — has
#: none. English prose has spaces in it, and so does every other language's.
#: The one allowed exception is a comma-separated list of tokens, because the
#: refusals this exists for are "must be one of".
#:
#: Conservative in one direction only: it refuses some slots that would have
#: been safe and never accepts one that is not. A refused slot costs an English
#: sentence, which is the state everything was already in. An accepted prose
#: slot costs a sentence half in one language and half in another, in front of
#: somebody who is already being told no.
_SLOT_TOKEN = re.compile(r"^\S*$")


def _is_token(value) -> bool:
    return all(_SLOT_TOKEN.match(part.strip())
               for part in str(value).split(","))


class Templated(str):
    """A refusal whose English text is not a constant, carried so it can be.

    `f"language must be one of {', '.join(SUPPORTED)}"` cannot be keyed on its
    English source, because at the moment it is raised there is no English
    source — only a result. `tests/refusals_untranslated.txt` named these and
    counted none of them.

        asked     is the refusal a constant we can translate
        mattered  is every part of it something we can translate

    This is a `str`, and its value is the finished English sentence, so
    everything that already treats a detail as text keeps working unchanged.
    What it adds is a memory of how it was built, so `localize_detail` can look
    up the *template* and refill it in the reader's language.

    A slot that does not look like a token sets `translatable = False` and the
    whole sentence stays English — the state it was in before, chosen rather
    than stumbled into. Nothing raises: a refusal path is the last place to add
    a way to fail.

    The known limit, stated because a rule this simple has one: a *single*
    English word has no whitespace either, and is indistinguishable from an
    identifier. QRME's copy of this carries a `Term` marker and a translated
    vocabulary for the closed sets it interpolates; this product has no refusal
    that interpolates one, and the guard fails if that stops being true.
    """

    template: str
    slots: dict
    translatable: bool

    def __new__(cls, template: str, **slots):
        # `Opening` applies here too, not only at translation. This value *is*
        # the English sentence — the one an English reader gets and the one
        # every driven test reads.
        english = {k: _open(v) if isinstance(v, Opening) else v
                   for k, v in slots.items()}
        text = template.format(**english)
        self = super().__new__(cls, text)
        self.template = template
        self.slots = slots
        # A `Term` is exempt from the whitespace rule, and that is the point
        # of it. The rule exists to catch prose *this product did not author*,
        # which cannot be translated because nobody wrote a translation. A
        # `Term` is drawn from a closed set this product does author, so its
        # whitespace is not a warning sign.
        #
        #     asked     does this slot contain whitespace
        #     mattered  is this slot something we have a translation for
        #
        # Safe by construction either way: an unmapped `Term` keeps the whole
        # refusal English in `localize_detail`, the same as a prose slot.
        self.translatable = all(isinstance(v, Term) or _is_token(v)
                                for v in slots.values())
        return self


def fill(template: str, **slots) -> Templated:
    """`raise HTTPException(422, i18n.fill(TEMPLATE, field=..., choices=...))`.

    A function rather than the class directly, so a raise site reads as a
    sentence being built and not as an object being constructed.
    """
    return Templated(template, **slots)


#: Several routes said this about several different fields. One sentence, one
#: translation, `field` as a slot: the field name is the API's own and is the
#: same string in every language.
MUST_BE_ONE_OF = "{field} must be one of {choices}"

#: The refusal `refusals_untranslated.txt` named as the one thing it would not
#: half-do. Its slots are prose — a capability description and a billing period
#: — so translating the frame alone would have produced a sentence half in each
#: language at the one moment in this product that stands between somebody and
#: a decision to pay. Both are `Term`s, so the whole sentence arrives in one
#: language or none of it does.
#:
#: The plan titles are deliberately not translated: `Basic` and `Pro` are what
#: the product is called on the pricing page and on a receipt.
#:
#: The emergency clause is part of the frame rather than an afterthought. A
#: person meeting this refusal needs to know the alarm still works, and that
#: reassurance arriving in English on a Portuguese sentence is the shape this
#: whole mechanism exists to prevent.
PLAN_GATE = ("{capability} needs {needs} (${price}/{period}). "
             "This account is on {have}. Billing here is simulated — "
             "subscribing records a row and moves no real funds. "
             "Emergency paths are never affected.")

#: The day's errands are used up. The slot is a **count**, not prose, so
#: translating the frame around it is safe — the rule that keeps a template
#: honest is about slots holding sentences, and `3` is `3` in every language.
#:
#: The second half is the part worth translating carefully: nothing has
#: stopped. The coach goes on answering from what it already knows, offline
#: and for nothing, which is the ordinary state of this product rather than a
#: degraded one.
ERRANDS_SPENT = ("the day's {count} errands are used up; the coach keeps "
                 "answering from what it already knows, and this begins "
                 "again tomorrow")

#: A monitor nobody switched on. The slot is what the thing does, in the
#: person's own words, from the closed set in `jim/monitors.py` — so it goes
#: through `Term` and arrives translated rather than as English in a frame.
MONITOR_NOT_ON = ("nothing is sensing that: you have not switched on the one "
                  "that would {doing}")

#: Channel 2 is lent to one wearable. A delivery under another device's
#: name would make the audit line — which microphone heard this — a guess.
MIC_LENT_ELSEWHERE = ("channel 2 is lent to your {yours}, not to {theirs}. "
                      "One channel, one device — otherwise the record cannot "
                      "say which microphone heard this")

#: Derived from the table below rather than repeated.
#: The eyes could not be reached, and the eyes said no. Both name what
#: leaves — one frame, sent to be described — rather than a bare code.
SIGHT_UNREACHABLE = ("could not reach the service that describes what a "
                     "monitor sees: {why}")
SIGHT_REFUSED = "the eyes refused it: HTTP {code} {detail}"

# -- the voice's refusals, from the round that made every refusal a template.
# `provider` is a token ("elevenlabs", "device"); `detail` is usually the
# provider's own prose and marks the fill untranslatable at runtime, which is
# the SIGHT_* precedent: the frame is translated for the day the slot is
# clean, and an English slot keeps the whole sentence English on purpose.
NEEDS_API_KEY = "{provider} needs an API key"
KEYS_NOT_CHECKED_HERE = ("{provider} keys are not checked here — this check "
                         "is the ElevenLabs account read")
NO_PUBLISHED_ALLOWANCE = ("{provider} does not publish a remaining allowance "
                          "— its balance is only visible on the provider's "
                          "own dashboard")
PROVIDER_REFUSED = "{provider} refused it: HTTP {code} {detail}"
PROVIDER_UNREACHABLE = "could not reach {provider}: {detail}"
TRANSCRIPTION_REFUSED = "transcription refused it: HTTP {code} {detail}"
#: The provider said the key itself is bad (401/403). The raw JSON body is
#: an operator's fact; the person mid-conversation needs the switch.
KEY_REFUSED = ("the {provider} key was refused — paste a fresh one on the "
               "Voice card, or fix the key in the deployment's settings")
TRANSCRIPTION_UNREACHABLE = ("could not reach the transcription service: "
                             "{detail}")

# -- the problem intake's refusals. Read by the developer of a client that
# sent a malformed report, in whatever language that person set — a protocol
# error is still a sentence somebody reads. `got` carries the offending
# value and usually marks the fill untranslatable; the key lists are joined
# with commas so they stay tokens and the sentence still translates.
SHORT_STRING_REQUIRED = ("'{field}' must be a short plain string (≤{max} "
                         "chars, no newlines or punctuation beyond "
                         "._-()/;:+) — got {got}")
OP_SHAPE = "'op' must look like 'VERB /template/path' — got {got}"
OP_IDENTIFIER_SEGMENT = ("'op' contains a segment that looks like an "
                         "identifier ({got}) — the client's redaction has "
                         "stopped working, and accepting this would hide "
                         "that")
UNKNOWN_KEYS = ("unknown top-level keys {keys} — this intake accepts exactly "
                "{accepts}. A new key is refused rather than ignored: "
                "silently dropping it would let a client start sending "
                "content and never learn that nobody wanted it.")
MISSING_KEYS = "missing keys {keys}"
MAX_PROBLEMS_PER_REPORT = "at most {max} problems per report"
UNKNOWN_PROBLEM_KEYS = "unknown problem keys {keys}"
PROBLEM_MISSING_KEYS = "problem missing keys {keys}"

# -- the microphone's own refusals, same round. Every slot is a token: a
# device name, a mic type, a route. The long ones are the sentences this
# product is proudest of — the reasons a microphone is refused — and they
# were the ones going out in English.
NO_SUCH_DEVICE = "no device called {device} on this account"
UNKNOWN_MIC_TYPE = "unknown microphone type {got} — one of {choices}"
ROOM_MIC_REFUSED = ("a {mic_type} microphone is pointed at a room, not at "
                    "you. Everyone it picks up would be lending their voice "
                    "without being asked, so it cannot be channel 2. A worn "
                    "or clipped-on microphone can: {choices}")
STATIONARY_DEVICE = ("{device} is registered as a stationary device. "
                     "Something bolted to a room hears the room, whatever "
                     "kind of microphone is in it")
MIC_ALREADY_ON_CALL = ("your {device} is already carrying the call — one "
                       "microphone cannot be both channels. Attach a "
                       "different one as channel 2, or take the call on "
                       "something else")
REASON_MUST_BE = ("reason must be one of {choices} — what is occupying your "
                  "microphone is what justifies lending another one")
SPEAKER_ROUTE_REFUSED = ("not while the call is on {route}. On speaker the "
                         "watch hears whoever you are talking to, and they "
                         "are not a user here — they were never asked and "
                         "could not revoke it. Switch to an earpiece or a "
                         "headset and it can listen to you alone")

# -- the API surface's own interpolated refusals, same round.
UNKNOWN_METRIC = "unknown metric {got}"
MAIL_SERVER_REFUSED = "the mail server refused it: {detail}"
SIGNATURE_MUST_MATCH = "signature must match the enrolled name ({name})"
SOURCE_NOT_CONSENTED = "source {source} is not consented for this user"
COULD_NOT_FETCH = "could not fetch — {kind}: {detail}"
UNKNOWN_CONNECTOR = "unknown connector: {provider}/{app}"
APP_DOES_NOT_OFFER = "{app} does not offer: {capabilities}"
NO_COLLECT_SUPPORT = "{app} does not support collecting context"
CAPABILITY_NOT_GRANTED = "this {app} connector was not granted {capability}"

# -- the dock's refusals, same round.
NO_SUCH_FACE = "no such face {got}; one of {choices}"
PANE_BOTTOM_CORNER = "the pane sits in a bottom corner — {choices}"
UNKNOWN_STATE = "unknown state {got}; one of {choices}"
FACE_NOT_CARRIED = "{got} is not one of the faces this dock carries"
FACE_CANNOT_BE_REMOVED = ("{face} cannot be removed from the pane — it is "
                          "the face that appears when something is wrong, "
                          "and a pane somebody configured out of the way "
                          "months ago is not a decision they made about the "
                          "day it fires")
FACE_NEEDS_A_SURFACE = "the {face} face is about a particular one — tell it which"

# -- the rota's and the money module's refusals, same round.
ROTA_NOT_JSON = "JIM_SITE_ROTA is not valid JSON: {detail}"
ROTA_ENTRY_NEEDS_NAME = "rota entry {index} needs a name"
UNKNOWN_DAY_RANGE = "unknown day range {got}"
UNKNOWN_DAY = "unknown day {got}"
UNREADABLE_TIME = "unreadable time {got} — use HH:MM"
UNKNOWN_ACCOUNT_KIND = "unknown account kind {got}; expected one of {choices}"
UNKNOWN_AGGREGATOR = ("unknown aggregator {got}; this module holds consents "
                      "for {choices}")
UNKNOWN_ASSET_CLASSES = ("unknown asset class(es): {got}; expected among "
                         "{choices}")
NO_AGGREGATOR_CREDENTIALS = ("this deployment holds no {aggregator} "
                             "credentials — the consent stands and will "
                             "sync when the aggregator is configured; until "
                             "then, drop a statement or observe a balance "
                             "by hand")
AGGREGATOR_NOT_WIRED = ("the {aggregator} client is not wired into this "
                        "build; the consent stands, and nothing was "
                        "invented in its name")

# -- the last of the round: every module's remaining one-liners.
UNKNOWN_CHOICE = "unknown {field} {got}; one of {choices}"
UNKNOWN_VALUE = "unknown {field} {got}"
UNKNOWN_MODE_ONE_OF = "unknown mode {got} — one of {choices}"
UNKNOWN_FEATURE_SWITCHES = "unknown feature {got}; the switches are {choices}"
UNKNOWN_ROBOT_MODEL = "unknown robot model {got}"
COMMAND_NOT_PERMITTED = "{command} is not permitted for {label}; allowed: {choices}"
NO_BEARING = "no bearing called {got} — it is companion or professional"
NO_PERMIT_AREA = "no permit area called {got}"
NO_SUCH_STEP = "no such step {got}"
NO_SURFACE = "no surface called {got}"
FILE_TOO_LARGE = "that is {size}MB; the limit is {limit}MB"
TOP_FRIENDS_MAX = ("top friends is at most {max} — that is what makes it a "
                   "ranking")
MAX_LINKS = "up to {max} links; a homepage is a page, not a directory"
NOTHING_READABLE = "{url} answered with nothing readable"
CANNOT_RUN_ONBOARD_LLM = "{label} cannot run an onboard LLM"
INTIMATE_NEEDS_CONSENT = ("{site} needs an explicit confirmation before it "
                          "is stored. It will be kept out of anything "
                          "automatic — no synthetic agent ever receives it, "
                          "and it is never folded into an assembled summary; "
                          "a clinician opens it deliberately or not at all.")

TEMPLATES = (MUST_BE_ONE_OF, PLAN_GATE, ERRANDS_SPENT, MONITOR_NOT_ON,
             MIC_LENT_ELSEWHERE, SIGHT_UNREACHABLE, SIGHT_REFUSED,
             NEEDS_API_KEY, KEYS_NOT_CHECKED_HERE, NO_PUBLISHED_ALLOWANCE,
             PROVIDER_REFUSED, PROVIDER_UNREACHABLE, TRANSCRIPTION_REFUSED,
             TRANSCRIPTION_UNREACHABLE, SHORT_STRING_REQUIRED, OP_SHAPE,
             OP_IDENTIFIER_SEGMENT, UNKNOWN_KEYS, MISSING_KEYS,
             MAX_PROBLEMS_PER_REPORT, UNKNOWN_PROBLEM_KEYS,
             PROBLEM_MISSING_KEYS, NO_SUCH_DEVICE, UNKNOWN_MIC_TYPE,
             ROOM_MIC_REFUSED, STATIONARY_DEVICE, MIC_ALREADY_ON_CALL,
             REASON_MUST_BE, SPEAKER_ROUTE_REFUSED, UNKNOWN_METRIC,
             MAIL_SERVER_REFUSED, SIGNATURE_MUST_MATCH, SOURCE_NOT_CONSENTED,
             COULD_NOT_FETCH, UNKNOWN_CONNECTOR, APP_DOES_NOT_OFFER,
             NO_COLLECT_SUPPORT, CAPABILITY_NOT_GRANTED, NO_SUCH_FACE,
             PANE_BOTTOM_CORNER, UNKNOWN_STATE, FACE_NOT_CARRIED,
             FACE_CANNOT_BE_REMOVED, FACE_NEEDS_A_SURFACE, ROTA_NOT_JSON,
             ROTA_ENTRY_NEEDS_NAME, UNKNOWN_DAY_RANGE, UNKNOWN_DAY,
             UNREADABLE_TIME, UNKNOWN_ACCOUNT_KIND, UNKNOWN_AGGREGATOR,
             UNKNOWN_ASSET_CLASSES, NO_AGGREGATOR_CREDENTIALS,
             AGGREGATOR_NOT_WIRED, UNKNOWN_CHOICE, UNKNOWN_VALUE,
             UNKNOWN_MODE_ONE_OF, UNKNOWN_FEATURE_SWITCHES,
             UNKNOWN_ROBOT_MODEL, COMMAND_NOT_PERMITTED, NO_BEARING,
             NO_PERMIT_AREA, NO_SUCH_STEP, NO_SURFACE, FILE_TOO_LARGE,
             TOP_FRIENDS_MAX, MAX_LINKS, NOTHING_READABLE,
             CANNOT_RUN_ONBOARD_LLM, INTIMATE_NEEDS_CONSENT)

_TEMPLATES: dict[str, dict[str, str]] = {
    ("the {provider} key was refused — paste a fresh one on the "
     "Voice card, or fix the key in the deployment's settings"): {
        "es": "la clave de {provider} fue rechazada — pega una nueva en la tarjeta de Voz, o corrige la clave en la configuración del despliegue",
        "fr": "la clé {provider} a été refusée — collez-en une nouvelle sur la carte Voix, ou corrigez la clé dans les réglages du déploiement",
        "de": "der {provider}-Schlüssel wurde abgelehnt — füge auf der Stimme-Karte einen frischen ein oder korrigiere den Schlüssel in den Einstellungen der Installation",
        "pt": "a chave {provider} foi recusada — cole uma nova no cartão de Voz, ou corrija a chave nas definições da instalação",
        "it": "la chiave {provider} è stata rifiutata — incollane una nuova sulla scheda Voce, o correggi la chiave nelle impostazioni dell'installazione",
        "ja": "{provider}のキーが拒否されました。ボイスカードに新しいキーを貼るか、環境設定のキーを修正してください",
        "zh": "{provider} 密钥被拒绝——在语音卡片粘贴新密钥，或修正部署设置中的密钥",
        "hi": "{provider} कुंजी अस्वीकार हुई — वॉइस कार्ड पर नई कुंजी चिपकाएँ, या परिनियोजन सेटिंग्स में कुंजी ठीक करें",
        "ar": "رُفض مفتاح {provider} — الصق مفتاحًا جديدًا في بطاقة الصوت، أو صحّح المفتاح في إعدادات النشر",
    },
    SIGHT_UNREACHABLE: {
        'es': 'no se pudo contactar con el servicio que describe lo que ve un monitor: {why}',
        'fr': "impossible de joindre le service qui décrit ce qu'un capteur voit : {why}",
        'de': 'der Dienst, der beschreibt, was ein Melder sieht, war nicht erreichbar: {why}',
        'pt': 'não foi possível alcançar o serviço que descreve o que um monitor vê: {why}',
        'it': 'non è stato possibile raggiungere il servizio che descrive ciò che un sensore vede: {why}',
        'ja': 'モニターが見ているものを説明するサービスに到達できませんでした: {why}',
        'zh': '无法连接到描述监测项所见内容的服务: {why}',
        'hi': 'उस सेवा तक नहीं पहुँच सके जो बताती है कि मॉनिटर क्या देख रहा है: {why}',
        'ar': 'تعذّر الوصول إلى الخدمة التي تصف ما يراه المِرقاب: {why}',
    },
    SIGHT_REFUSED: {
        'es': 'los ojos lo rechazaron: HTTP {code} {detail}',
        'fr': 'les yeux ont refusé : HTTP {code} {detail}',
        'de': 'die Augen haben es abgelehnt: HTTP {code} {detail}',
        'pt': 'os olhos recusaram: HTTP {code} {detail}',
        'it': 'gli occhi lo hanno rifiutato: HTTP {code} {detail}',
        'ja': '目がそれを拒みました: HTTP {code} {detail}',
        'zh': '眼睛拒绝了它: HTTP {code} {detail}',
        'hi': 'आँखों ने इसे अस्वीकार किया: HTTP {code} {detail}',
        'ar': 'رفضته العيون: HTTP {code} {detail}',
    },
    MIC_LENT_ELSEWHERE: {
        'es': "el canal 2 está cedido a tu {yours}, no a {theirs}. Un canal, un dispositivo — de otro modo el registro no puede decir qué micrófono oyó esto",
        'fr': "le canal 2 est cédé à votre {yours}, pas à {theirs}. Un canal, un appareil — sinon le registre ne peut pas dire quel microphone a entendu cela",
        'de': "Kanal 2 ist an dein {yours} verliehen, nicht an {theirs}. Ein Kanal, ein Gerät — sonst kann der Eintrag nicht sagen, welches Mikrofon das gehört hat",
        'pt': "o canal 2 está cedido ao seu {yours}, não a {theirs}. Um canal, um dispositivo — caso contrário o registo não consegue dizer que microfone ouviu isto",
        'it': "il canale 2 è ceduto al tuo {yours}, non a {theirs}. Un canale, un dispositivo — altrimenti il registro non può dire quale microfono ha sentito questo",
        'ja': "チャンネル2はあなたの{yours}に貸し出されており、{theirs}にではありません。1つのチャンネルに1つの機器 — そうでなければ、どのマイクが聞いたのかを記録が言えません",
        'zh': "第二通道借给的是你的{yours}，而不是{theirs}。一个通道对应一台设备 — 否则记录无法说明是哪个麦克风听到的",
        'hi': "चैनल 2 आपके {yours} को दिया गया है, {theirs} को नहीं। एक चैनल, एक उपकरण — अन्यथा रिकॉर्ड यह नहीं बता सकता कि किस माइक्रोफ़ोन ने यह सुना",
        'ar': "القناة 2 مُعارة إلى {yours} الخاص بك، لا إلى {theirs}. قناة واحدة لجهاز واحد — وإلا لن يستطيع السجل أن يقول أي ميكروفون سمع هذا",
    },
    MONITOR_NOT_ON: {
        'es': "no hay nada detectando eso: no has activado lo que serviría para {doing}",
        'fr': "rien ne capte cela : vous n'avez pas activé ce qui permettrait de {doing}",
        'de': "nichts erfasst das: du hast nicht eingeschaltet, was {doing} würde",
        'pt': "nada está a detetar isso: não ativou aquilo que serviria para {doing}",
        'it': "nulla sta rilevando questo: non hai attivato ciò che servirebbe a {doing}",
        'ja': "それを感知しているものはありません。{doing}ためのものが有効になっていません",
        'zh': "没有任何设备在感知这一点：你还没有开启用来{doing}的那一项",
        'hi': "उसे कुछ भी महसूस नहीं कर रहा: जो {doing} के लिए है उसे आपने चालू नहीं किया",
        'ar': "لا شيء يستشعر ذلك: لم تفعّل ما من شأنه {doing}",
    },
    ERRANDS_SPENT: {
        'es': "los {count} recados del día están agotados; el coach sigue respondiendo con lo que ya sabe, y esto vuelve a empezar mañana",
        'fr': "les {count} sorties du jour sont épuisées ; le coach continue de répondre avec ce qu'il sait déjà, et cela reprend demain",
        'de': "die {count} Erkundungen des Tages sind aufgebraucht; der Coach antwortet weiter aus dem, was er schon weiß, und morgen beginnt das von vorn",
        'pt': "as {count} diligências do dia estão esgotadas; o coach continua a responder com o que já sabe, e isto recomeça amanhã",
        'it': "le {count} commissioni della giornata sono esaurite; il coach continua a rispondere con ciò che già sa, e domani si ricomincia",
        'ja': "本日の{count}件の調べものは使い切りました。コーチはすでに知っていることから答え続けます。明日またはじまります",
        'zh': "今天的 {count} 次外出学习已用完；教练仍会用它已经知道的内容回答，明天重新开始",
        'hi': "आज की {count} खोज-यात्राएँ पूरी हो चुकीं; कोच जो पहले से जानता है उसी से उत्तर देता रहेगा, और यह कल फिर शुरू होगा",
        'ar': "استُنفدت مهام اليوم الـ{count}؛ يواصل المدرّب الإجابة مما يعرفه أصلًا، ويبدأ هذا من جديد غدًا",
    },
    PLAN_GATE: {
        'es': '{capability} requiere {needs} (${price}/{period}). Esta cuenta '
              'está en {have}. La facturación aquí es simulada: suscribirse '
              'registra una fila y no mueve fondos reales. Las vías de '
              'emergencia nunca se ven afectadas.',
        'fr': '{capability} nécessite {needs} ({price} $/{period}). Ce compte '
              'est en {have}. La facturation est simulée ici : souscrire '
              "enregistre une ligne et ne déplace aucun fonds réel. Les voies "
              "d'urgence ne sont jamais affectées.",
        'de': '{capability} erfordert {needs} ({price} $/{period}). Dieses '
              'Konto ist auf {have}. Die Abrechnung ist hier simuliert — ein '
              'Abo legt eine Zeile an und bewegt kein echtes Geld. Notfallwege '
              'sind davon nie betroffen.',
        'pt': '{capability} requer {needs} (${price}/{period}). Esta conta '
              'está no {have}. A cobrança aqui é simulada: assinar regista uma '
              'linha e não movimenta fundos reais. As vias de emergência nunca '
              'são afetadas.',
        'it': '{capability} richiede {needs} ({price} $/{period}). Questo '
              'account è su {have}. La fatturazione qui è simulata: abbonarsi '
              'registra una riga e non muove fondi reali. I percorsi di '
              'emergenza non sono mai interessati.',
        'ja': '{capability}には{needs}が必要です（${price}／{period}）。'
              'このアカウントは{have}です。ここでの課金はシミュレーションです — '
              '購読しても記録が残るだけで、実際の資金は動きません。'
              '緊急時の経路が影響を受けることはありません。',
        'zh': '{capability}需要 {needs}（${price}/{period}）。'
              '此账户当前为 {have}。此处的计费为模拟 — 订阅只会记录一行，'
              '不会转移真实资金。紧急通路始终不受影响。',
        'hi': '{capability} के लिए {needs} चाहिए (${price}/{period})। '
              'यह खाता {have} पर है। यहाँ बिलिंग नकली है — सदस्यता लेने पर '
              'केवल एक पंक्ति दर्ज होती है, असली पैसा नहीं जाता। '
              'आपातकालीन रास्ते कभी प्रभावित नहीं होते।',
        'ar': '{capability} يتطلب {needs} (${price}/{period}). هذا الحساب على '
              '{have}. الفوترة هنا محاكاة — الاشتراك يسجل صفًا ولا ينقل '
              'أموالًا حقيقية. مسارات الطوارئ لا تتأثر أبدًا.',
    },
    MUST_BE_ONE_OF: {
        'es': '{field} debe ser uno de {choices}',
        'fr': "{field} doit être l'un de {choices}",
        'de': '{field} muss eines von {choices} sein',
        'pt': '{field} deve ser um de {choices}',
        'it': '{field} deve essere uno tra {choices}',
        'ja': '{field} は次のいずれかにしてください: {choices}',
        'zh': '{field} 必须是以下之一：{choices}',
        'hi': '{field} इनमें से एक होना चाहिए: {choices}',
        'ar': '{field} يجب أن يكون أحد التالي: {choices}',
    },
    NEEDS_API_KEY: {
        'es': '{provider} necesita una clave de API',
        'fr': '{provider} nécessite une clé API',
        'de': '{provider} benötigt einen API-Schlüssel',
        'pt': '{provider} precisa de uma chave de API',
        'it': '{provider} richiede una chiave API',
        'ja': '{provider} には API キーが必要です',
        'zh': '{provider} 需要 API 密钥',
        'hi': '{provider} के लिए API कुंजी चाहिए',
        'ar': '{provider} يتطلب مفتاح API',
    },
    KEYS_NOT_CHECKED_HERE: {
        'es': 'las claves de {provider} no se comprueban aquí — esta '
              'comprobación lee la cuenta de ElevenLabs',
        'fr': 'les clés {provider} ne sont pas vérifiées ici — cette '
              'vérification lit le compte ElevenLabs',
        'de': '{provider}-Schlüssel werden hier nicht geprüft — diese '
              'Prüfung liest das ElevenLabs-Konto',
        'pt': 'as chaves de {provider} não são verificadas aqui — esta '
              'verificação lê a conta ElevenLabs',
        'it': "le chiavi di {provider} non vengono verificate qui — questa "
              "verifica legge l'account ElevenLabs",
        'ja': '{provider} のキーはここでは確認されません — この確認は '
              'ElevenLabs アカウントの読み取りです',
        'zh': '此处不检查 {provider} 密钥 — 该检查读取的是 ElevenLabs 账户',
        'hi': '{provider} कुंजियाँ यहाँ जाँची नहीं जातीं — यह जाँच ElevenLabs '
              'खाते को पढ़ती है',
        'ar': 'مفاتيح {provider} لا تُفحص هنا — هذا الفحص يقرأ حساب ElevenLabs',
    },
    NO_PUBLISHED_ALLOWANCE: {
        'es': '{provider} no publica un saldo restante — su balance solo es '
              'visible en el panel del propio proveedor',
        'fr': "{provider} ne publie pas de solde restant — il n'est visible "
              'que sur le tableau de bord du fournisseur',
        'de': '{provider} veröffentlicht kein Restguthaben — der Stand ist '
              'nur im Dashboard des Anbieters sichtbar',
        'pt': '{provider} não publica um saldo restante — o saldo só é '
              'visível no painel do próprio fornecedor',
        'it': '{provider} non pubblica un saldo residuo — il saldo è '
              'visibile solo nella dashboard del fornitore',
        'ja': '{provider} は残量を公開していません — 残高はプロバイダー自身の'
              'ダッシュボードでのみ確認できます',
        'zh': '{provider} 不公布剩余额度 — 余额只能在提供商自己的控制台查看',
        'hi': '{provider} शेष सीमा प्रकाशित नहीं करता — शेष राशि केवल प्रदाता '
              'के अपने डैशबोर्ड पर दिखती है',
        'ar': '{provider} لا ينشر رصيدًا متبقيًا — الرصيد يظهر فقط في لوحة '
              'تحكم المزوّد نفسه',
    },
    PROVIDER_REFUSED: {
        'es': '{provider} lo rechazó: HTTP {code} {detail}',
        'fr': "{provider} l'a refusé : HTTP {code} {detail}",
        'de': '{provider} hat es abgelehnt: HTTP {code} {detail}',
        'pt': '{provider} recusou: HTTP {code} {detail}',
        'it': '{provider} lo ha rifiutato: HTTP {code} {detail}',
        'ja': '{provider} に拒否されました: HTTP {code} {detail}',
        'zh': '{provider} 拒绝了请求：HTTP {code} {detail}',
        'hi': '{provider} ने अस्वीकार किया: HTTP {code} {detail}',
        'ar': '{provider} رفض الطلب: HTTP {code} {detail}',
    },
    PROVIDER_UNREACHABLE: {
        'es': 'no se pudo contactar con {provider}: {detail}',
        'fr': 'impossible de joindre {provider} : {detail}',
        'de': '{provider} war nicht erreichbar: {detail}',
        'pt': 'não foi possível contactar {provider}: {detail}',
        'it': 'impossibile raggiungere {provider}: {detail}',
        'ja': '{provider} に接続できませんでした: {detail}',
        'zh': '无法连接 {provider}：{detail}',
        'hi': '{provider} से संपर्क नहीं हो सका: {detail}',
        'ar': 'تعذّر الوصول إلى {provider}: {detail}',
    },
    TRANSCRIPTION_REFUSED: {
        'es': 'la transcripción lo rechazó: HTTP {code} {detail}',
        'fr': "la transcription l'a refusé : HTTP {code} {detail}",
        'de': 'die Transkription hat es abgelehnt: HTTP {code} {detail}',
        'pt': 'a transcrição recusou: HTTP {code} {detail}',
        'it': 'la trascrizione lo ha rifiutato: HTTP {code} {detail}',
        'ja': '文字起こしに拒否されました: HTTP {code} {detail}',
        'zh': '转写服务拒绝了请求：HTTP {code} {detail}',
        'hi': 'प्रतिलेखन ने अस्वीकार किया: HTTP {code} {detail}',
        'ar': 'رفضت خدمة التفريغ الطلب: HTTP {code} {detail}',
    },
    TRANSCRIPTION_UNREACHABLE: {
        'es': 'no se pudo contactar con el servicio de transcripción: {detail}',
        'fr': 'impossible de joindre le service de transcription : {detail}',
        'de': 'der Transkriptionsdienst war nicht erreichbar: {detail}',
        'pt': 'não foi possível contactar o serviço de transcrição: {detail}',
        'it': 'impossibile raggiungere il servizio di trascrizione: {detail}',
        'ja': '文字起こしサービスに接続できませんでした: {detail}',
        'zh': '无法连接转写服务：{detail}',
        'hi': 'प्रतिलेखन सेवा से संपर्क नहीं हो सका: {detail}',
        'ar': 'تعذّر الوصول إلى خدمة التفريغ: {detail}',
    },
    SHORT_STRING_REQUIRED: {
        'es': "'{field}' debe ser una cadena corta y simple (≤{max} "
              'caracteres, sin saltos de línea ni signos más allá de '
              '._-()/;:+) — se recibió {got}',
        'fr': "'{field}' doit être une chaîne courte et simple (≤{max} "
              'caractères, sans retour à la ligne ni ponctuation au-delà de '
              '._-()/;:+) — reçu {got}',
        'de': "'{field}' muss eine kurze einfache Zeichenkette sein (≤{max} "
              'Zeichen, keine Zeilenumbrüche, keine Zeichen außer '
              '._-()/;:+) — erhalten: {got}',
        'pt': "'{field}' deve ser um texto curto e simples (≤{max} "
              'caracteres, sem quebras de linha nem pontuação além de '
              '._-()/;:+) — recebido {got}',
        'it': "'{field}' deve essere una stringa breve e semplice (≤{max} "
              'caratteri, senza a capo né punteggiatura oltre '
              '._-()/;:+) — ricevuto {got}',
        'ja': "'{field}' は短い単純な文字列にしてください（{max} 文字以内、"
              '改行や ._-()/;:+ 以外の記号は不可）— 受け取った値: {got}',
        'zh': "'{field}' 必须是简短的纯字符串（≤{max} 个字符，不含换行，"
              '标点仅限 ._-()/;:+）— 收到 {got}',
        'hi': "'{field}' एक छोटी सादी स्ट्रिंग होनी चाहिए (≤{max} अक्षर, "
              'कोई नई पंक्ति नहीं, विराम केवल ._-()/;:+) — मिला {got}',
        'ar': "'{field}' يجب أن يكون نصًا قصيرًا بسيطًا (≤{max} حرفًا، دون "
              'أسطر جديدة أو علامات غير ._-()/;:+) — الوارد {got}',
    },
    OP_SHAPE: {
        'es': "'op' debe tener la forma 'VERB /template/path' — se recibió {got}",
        'fr': "'op' doit avoir la forme 'VERB /template/path' — reçu {got}",
        'de': "'op' muss die Form 'VERB /template/path' haben — erhalten: {got}",
        'pt': "'op' deve ter a forma 'VERB /template/path' — recebido {got}",
        'it': "'op' deve avere la forma 'VERB /template/path' — ricevuto {got}",
        'ja': "'op' は 'VERB /template/path' の形式にしてください — 受け取った値: {got}",
        'zh': "'op' 必须形如 'VERB /template/path' — 收到 {got}",
        'hi': "'op' का रूप 'VERB /template/path' होना चाहिए — मिला {got}",
        'ar': "'op' يجب أن يكون بالشكل 'VERB /template/path' — الوارد {got}",
    },
    OP_IDENTIFIER_SEGMENT: {
        'es': "'op' contiene un segmento que parece un identificador ({got}) "
              '— la redacción del cliente ha dejado de funcionar, y '
              'aceptarlo lo ocultaría',
        'fr': "'op' contient un segment qui ressemble à un identifiant "
              '({got}) — la rédaction côté client ne fonctionne plus, et '
              "l'accepter le masquerait",
        'de': "'op' enthält ein Segment, das wie ein Bezeichner aussieht "
              '({got}) — die Schwärzung des Clients funktioniert nicht '
              'mehr, und es anzunehmen würde das verbergen',
        'pt': "'op' contém um segmento que parece um identificador ({got}) "
              '— a redação do cliente deixou de funcionar, e aceitá-lo '
              'esconderia isso',
        'it': "'op' contiene un segmento che sembra un identificatore "
              '({got}) — la redazione del client ha smesso di funzionare, '
              'e accettarlo lo nasconderebbe',
        'ja': "'op' に識別子のようなセグメントが含まれています（{got}）— "
              'クライアントの伏せ字処理が機能しておらず、受け入れると'
              'それが隠れてしまいます',
        'zh': "'op' 包含一个看似标识符的片段（{got}）— 客户端的脱敏已失效，"
              '接受它会掩盖这一点',
        'hi': "'op' में एक खंड है जो पहचानकर्ता जैसा दिखता है ({got}) — "
              'क्लाइंट की गोपन प्रक्रिया काम नहीं कर रही, और इसे स्वीकारना '
              'उसे छिपा देगा',
        'ar': "'op' يحتوي على مقطع يبدو كمعرّف ({got}) — إخفاء البيانات لدى "
              'العميل توقف عن العمل، وقبوله سيخفي ذلك',
    },
    UNKNOWN_KEYS: {
        'es': 'claves de primer nivel desconocidas: {keys} — esta entrada '
              'acepta exactamente {accepts}. Una clave nueva se rechaza en '
              'vez de ignorarse: descartarla en silencio dejaría al cliente '
              'enviando contenido sin enterarse nunca de que nadie lo quería.',
        'fr': 'clés de premier niveau inconnues : {keys} — cette entrée '
              "accepte exactement {accepts}. Une nouvelle clé est refusée "
              "plutôt qu'ignorée : la supprimer en silence laisserait le "
              "client envoyer du contenu sans jamais apprendre que personne "
              "n'en voulait.",
        'de': 'unbekannte Schlüssel auf oberster Ebene: {keys} — diese '
              'Annahme akzeptiert genau {accepts}. Ein neuer Schlüssel wird '
              'abgelehnt statt ignoriert: ihn still zu verwerfen ließe einen '
              'Client Inhalte senden, ohne je zu erfahren, dass sie niemand '
              'wollte.',
        'pt': 'chaves de nível superior desconhecidas: {keys} — esta entrada '
              'aceita exatamente {accepts}. Uma chave nova é recusada em vez '
              'de ignorada: descartá-la em silêncio deixaria o cliente a '
              'enviar conteúdo sem nunca saber que ninguém o queria.',
        'it': 'chiavi di primo livello sconosciute: {keys} — questo intake '
              'accetta esattamente {accepts}. Una chiave nuova viene '
              'rifiutata anziché ignorata: scartarla in silenzio lascerebbe '
              'il client a inviare contenuti senza mai sapere che nessuno li '
              'voleva.',
        'ja': '不明なトップレベルキー: {keys} — この受け口が受け付けるのは '
              '{accepts} だけです。新しいキーは無視ではなく拒否されます。'
              '黙って捨てると、誰も求めていない内容をクライアントが送り'
              '続け、それを知る機会が失われます。',
        'zh': '未知的顶层键：{keys} — 此入口只接受 {accepts}。新键会被拒绝'
              '而不是被忽略：静默丢弃会让客户端持续发送没人需要的内容，'
              '且永远不会得知。',
        'hi': 'अज्ञात शीर्ष-स्तरीय कुंजियाँ: {keys} — यह इनटेक केवल {accepts} '
              'स्वीकार करता है। नई कुंजी को अनदेखा करने के बजाय अस्वीकार '
              'किया जाता है: चुपचाप हटाने से क्लाइंट सामग्री भेजता रहेगा और '
              'कभी नहीं जान पाएगा कि वह किसी को नहीं चाहिए थी।',
        'ar': 'مفاتيح عليا غير معروفة: {keys} — هذا المدخل يقبل بالضبط '
              '{accepts}. المفتاح الجديد يُرفض بدل تجاهله: إسقاطه بصمت '
              'سيترك العميل يرسل محتوى دون أن يعلم أبدًا أن أحدًا لم يرده.',
    },
    MISSING_KEYS: {
        'es': 'faltan las claves {keys}',
        'fr': 'clés manquantes : {keys}',
        'de': 'fehlende Schlüssel: {keys}',
        'pt': 'faltam as chaves {keys}',
        'it': 'chiavi mancanti: {keys}',
        'ja': 'キーが不足しています: {keys}',
        'zh': '缺少键：{keys}',
        'hi': 'कुंजियाँ अनुपस्थित हैं: {keys}',
        'ar': 'مفاتيح ناقصة: {keys}',
    },
    MAX_PROBLEMS_PER_REPORT: {
        'es': 'como máximo {max} problemas por informe',
        'fr': 'au plus {max} problèmes par rapport',
        'de': 'höchstens {max} Probleme pro Bericht',
        'pt': 'no máximo {max} problemas por relatório',
        'it': 'al massimo {max} problemi per segnalazione',
        'ja': '1 レポートにつき最大 {max} 件までです',
        'zh': '每份报告最多 {max} 个问题',
        'hi': 'प्रति रिपोर्ट अधिकतम {max} समस्याएँ',
        'ar': 'بحد أقصى {max} مشكلة لكل تقرير',
    },
    UNKNOWN_PROBLEM_KEYS: {
        'es': 'claves de problema desconocidas: {keys}',
        'fr': 'clés de problème inconnues : {keys}',
        'de': 'unbekannte Problem-Schlüssel: {keys}',
        'pt': 'chaves de problema desconhecidas: {keys}',
        'it': 'chiavi di problema sconosciute: {keys}',
        'ja': '不明な問題キー: {keys}',
        'zh': '未知的问题键：{keys}',
        'hi': 'अज्ञात समस्या कुंजियाँ: {keys}',
        'ar': 'مفاتيح مشكلة غير معروفة: {keys}',
    },
    PROBLEM_MISSING_KEYS: {
        'es': 'al problema le faltan las claves {keys}',
        'fr': 'clés manquantes pour le problème : {keys}',
        'de': 'dem Problem fehlen die Schlüssel: {keys}',
        'pt': 'faltam chaves ao problema: {keys}',
        'it': 'al problema mancano le chiavi: {keys}',
        'ja': '問題にキーが不足しています: {keys}',
        'zh': '问题缺少键：{keys}',
        'hi': 'समस्या में कुंजियाँ अनुपस्थित हैं: {keys}',
        'ar': 'المشكلة تنقصها المفاتيح: {keys}',
    },
    NO_SUCH_DEVICE: {
        'es': 'no hay ningún dispositivo llamado {device} en esta cuenta',
        'fr': 'aucun appareil nommé {device} sur ce compte',
        'de': 'kein Gerät namens {device} auf diesem Konto',
        'pt': 'não há nenhum dispositivo chamado {device} nesta conta',
        'it': 'nessun dispositivo chiamato {device} su questo account',
        'ja': 'このアカウントに {device} という機器はありません',
        'zh': '此账户上没有名为 {device} 的设备',
        'hi': 'इस खाते पर {device} नाम का कोई उपकरण नहीं है',
        'ar': 'لا يوجد جهاز باسم {device} على هذا الحساب',
    },
    UNKNOWN_MIC_TYPE: {
        'es': 'tipo de micrófono desconocido {got} — uno de {choices}',
        'fr': 'type de micro inconnu {got} — parmi {choices}',
        'de': 'unbekannter Mikrofontyp {got} — einer von {choices}',
        'pt': 'tipo de microfone desconhecido {got} — um de {choices}',
        'it': 'tipo di microfono sconosciuto {got} — uno tra {choices}',
        'ja': '不明なマイクの種類 {got} — 次のいずれか: {choices}',
        'zh': '未知的麦克风类型 {got} — 应为 {choices} 之一',
        'hi': 'अज्ञात माइक्रोफ़ोन प्रकार {got} — इनमें से एक: {choices}',
        'ar': 'نوع ميكروفون غير معروف {got} — أحد التالي: {choices}',
    },
    ROOM_MIC_REFUSED: {
        'es': 'un micrófono {mic_type} apunta a una habitación, no a ti. '
              'Todos los que capta estarían prestando su voz sin que se les '
              'pregunte, así que no puede ser el canal 2. Uno llevado puesto '
              'o de pinza sí puede: {choices}',
        'fr': 'un micro {mic_type} est pointé vers une pièce, pas vers '
              "vous. Tous ceux qu'il capte prêteraient leur voix sans qu'on "
              'le leur demande, il ne peut donc pas être le canal 2. Un '
              'micro porté ou à pince le peut : {choices}',
        'de': 'ein {mic_type}-Mikrofon zeigt auf einen Raum, nicht auf '
              'dich. Alle, die es aufnimmt, würden ihre Stimme ungefragt '
              'hergeben, deshalb kann es nicht Kanal 2 sein. Ein getragenes '
              'oder angestecktes Mikrofon kann es: {choices}',
        'pt': 'um microfone {mic_type} aponta para uma sala, não para ti. '
              'Todos os que ele capta estariam a emprestar a voz sem serem '
              'perguntados, por isso não pode ser o canal 2. Um usado no '
              'corpo ou de prender pode: {choices}',
        'it': 'un microfono {mic_type} è puntato su una stanza, non su di '
              'te. Chiunque venga captato presterebbe la voce senza essere '
              'stato interpellato, quindi non può essere il canale 2. Uno '
              'indossato o a clip può: {choices}',
        'ja': '{mic_type} マイクはあなたではなく部屋に向いています。拾われる'
              '人はみな、同意なく声を貸すことになるため、チャンネル 2 には'
              'できません。身に着けるマイクやクリップ式ならできます: '
              '{choices}',
        'zh': '{mic_type} 麦克风对着的是房间，不是你。它拾取到的每个人都'
              '在未被询问的情况下出借自己的声音，所以它不能作为通道 2。'
              '佩戴式或夹式麦克风可以：{choices}',
        'hi': '{mic_type} माइक्रोफ़ोन कमरे की ओर है, आपकी ओर नहीं। जो भी '
              'इसमें सुनाई देगा वह बिना पूछे अपनी आवाज़ दे रहा होगा, इसलिए '
              'यह चैनल 2 नहीं हो सकता। पहनने वाला या क्लिप वाला हो सकता '
              'है: {choices}',
        'ar': 'ميكروفون {mic_type} موجه نحو غرفة، لا نحوك. كل من يلتقطه '
              'سيُعير صوته دون أن يُسأل، لذا لا يمكن أن يكون القناة 2. '
              'الميكروفون المحمول أو المثبت بمشبك يمكنه ذلك: {choices}',
    },
    STATIONARY_DEVICE: {
        'es': '{device} está registrado como dispositivo fijo. Algo '
              'atornillado a una habitación oye la habitación, sea cual sea '
              'el micrófono que lleve',
        'fr': "{device} est enregistré comme appareil fixe. Ce qui est fixé "
              'à une pièce entend la pièce, quel que soit le micro qui '
              "l'équipe",
        'de': '{device} ist als stationäres Gerät registriert. Was in einem '
              'Raum verschraubt ist, hört den Raum, egal welches Mikrofon '
              'darin steckt',
        'pt': '{device} está registado como dispositivo fixo. Algo '
              'aparafusado a uma sala ouve a sala, seja qual for o '
              'microfone que tiver',
        'it': '{device} è registrato come dispositivo fisso. Qualcosa di '
              'fissato a una stanza sente la stanza, qualunque microfono '
              'contenga',
        'ja': '{device} は据え置き機器として登録されています。部屋に固定'
              'されたものは、どんなマイクが入っていても部屋の音を聞きます',
        'zh': '{device} 登记为固定设备。固定在房间里的东西听到的是整个'
              '房间，无论装的是哪种麦克风',
        'hi': '{device} स्थिर उपकरण के रूप में पंजीकृत है। कमरे में लगा '
              'हुआ कुछ भी कमरे को सुनता है, चाहे उसमें कोई भी माइक्रोफ़ोन हो',
        'ar': '{device} مسجل كجهاز ثابت. ما هو مثبت في غرفة يسمع الغرفة، '
              'أيًا كان الميكروفون فيه',
    },
    MIC_ALREADY_ON_CALL: {
        'es': 'tu {device} ya lleva la llamada — un micrófono no puede ser '
              'los dos canales. Conecta otro como canal 2, o pasa la '
              'llamada a otro aparato',
        'fr': 'votre {device} porte déjà l’appel — un micro ne peut pas '
              'être les deux canaux. Attachez-en un autre comme canal 2, ou '
              "prenez l'appel sur autre chose",
        'de': 'dein {device} trägt bereits den Anruf — ein Mikrofon kann '
              'nicht beide Kanäle sein. Häng ein anderes als Kanal 2 an, '
              'oder nimm den Anruf auf etwas anderem an',
        'pt': 'o teu {device} já leva a chamada — um microfone não pode ser '
              'os dois canais. Liga outro como canal 2, ou atende a chamada '
              'noutro aparelho',
        'it': 'il tuo {device} sta già portando la chiamata — un microfono '
              'non può essere entrambi i canali. Collegane un altro come '
              'canale 2, o prendi la chiamata su altro',
        'ja': 'あなたの {device} はすでに通話を担っています — 1 本のマイクが'
              '両方のチャンネルにはなれません。別のマイクをチャンネル 2 と'
              'して接続するか、通話を別の機器に移してください',
        'zh': '你的 {device} 已经承载着通话 — 一个麦克风不能同时是两个'
              '通道。请再接一个作为通道 2，或改用其他设备接听',
        'hi': 'आपका {device} पहले से कॉल संभाल रहा है — एक माइक्रोफ़ोन दोनों '
              'चैनल नहीं हो सकता। चैनल 2 के लिए दूसरा जोड़ें, या कॉल किसी '
              'और उपकरण पर लें',
        'ar': 'جهازك {device} يحمل المكالمة بالفعل — ميكروفون واحد لا يمكن '
              'أن يكون القناتين. صِل آخر كقناة 2، أو خذ المكالمة على جهاز '
              'آخر',
    },
    REASON_MUST_BE: {
        'es': 'el motivo debe ser uno de {choices} — lo que ocupa tu '
              'micrófono es lo que justifica prestar otro',
        'fr': 'le motif doit être parmi {choices} — ce qui occupe votre '
              "micro est ce qui justifie d'en prêter un autre",
        'de': 'der Grund muss einer von {choices} sein — was dein Mikrofon '
              'belegt, ist die Rechtfertigung, ein weiteres zu leihen',
        'pt': 'o motivo deve ser um de {choices} — o que ocupa o teu '
              'microfone é o que justifica emprestar outro',
        'it': 'il motivo deve essere uno tra {choices} — ciò che occupa il '
              'tuo microfono è ciò che giustifica prestarne un altro',
        'ja': '理由は次のいずれかにしてください: {choices} — あなたのマイクを'
              '塞いでいるものこそが、もう 1 本を貸す理由になります',
        'zh': '原因必须是 {choices} 之一 — 占用你麦克风的事，正是出借另'
              '一个的理由',
        'hi': 'कारण इनमें से एक होना चाहिए: {choices} — आपके माइक्रोफ़ोन को '
              'जो घेर रहा है वही दूसरा उधार देने का औचित्य है',
        'ar': 'السبب يجب أن يكون أحد التالي: {choices} — ما يشغل '
              'ميكروفونك هو ما يبرر إعارة آخر',
    },
    SPEAKER_ROUTE_REFUSED: {
        'es': 'no mientras la llamada esté en {route}. En altavoz el reloj '
              'oye a la persona con la que hablas, y no es usuaria aquí — '
              'nunca se le preguntó y no podría revocarlo. Cambia a un '
              'auricular y podrá escucharte solo a ti',
        'fr': "pas tant que l'appel est sur {route}. En haut-parleur la "
              'montre entend votre interlocuteur, qui n’est pas un '
              "utilisateur ici — on ne le lui a jamais demandé et il ne "
              'pourrait pas le révoquer. Passez à une oreillette ou un '
              'casque et elle ne pourra écouter que vous',
        'de': 'nicht, solange der Anruf auf {route} läuft. Über den '
              'Lautsprecher hört die Uhr dein Gegenüber, das hier kein '
              'Nutzer ist — es wurde nie gefragt und könnte nicht '
              'widerrufen. Wechsle auf Hörer oder Headset, dann hört sie '
              'nur dich',
        'pt': 'não enquanto a chamada estiver em {route}. Em alta-voz o '
              'relógio ouve a pessoa com quem falas, e ela não é utilizadora '
              'aqui — nunca lhe perguntaram e não poderia revogar. Passa '
              'para um auricular e ele passa a ouvir-te só a ti',
        'it': 'non finché la chiamata è su {route}. In vivavoce '
              "l'orologio sente il tuo interlocutore, che qui non è un "
              'utente — non gli è mai stato chiesto e non potrebbe '
              'revocarlo. Passa a un auricolare o a cuffie e potrà '
              'ascoltare solo te',
        'ja': '通話が {route} にある間はできません。スピーカーでは、時計が'
              '通話相手の声も聞きますが、その人はここのユーザーではありま'
              'せん — 同意を求められたことも、取り消すこともできません。'
              'イヤホンかヘッドセットに切り替えれば、あなただけを聞けます',
        'zh': '通话在 {route} 上时不行。开着扬声器，手表会听到与你通话的'
              '人，而对方不是这里的用户 — 从未被询问，也无法撤回。换成'
              '耳机后它就只听你一个人',
        'hi': 'जब कॉल {route} पर हो तब नहीं। स्पीकर पर घड़ी उस व्यक्ति को '
              'भी सुनती है जिससे आप बात कर रहे हैं, और वह यहाँ उपयोगकर्ता '
              'नहीं है — उससे कभी पूछा नहीं गया और वह इसे रद्द नहीं कर '
              'सकता। इयरपीस या हेडसेट पर जाएँ तो यह केवल आपको सुनेगी',
        'ar': 'ليس والمكالمة على {route}. على مكبر الصوت تسمع الساعة من '
              'تتحدث معه، وهو ليس مستخدمًا هنا — لم يُسأل قط ولا يمكنه '
              'الإلغاء. انتقل إلى سماعة أذن أو رأس فتسمعك وحدك',
    },
    UNKNOWN_METRIC: {
        'es': 'métrica desconocida {got}',
        'fr': 'métrique inconnue {got}',
        'de': 'unbekannte Messgröße {got}',
        'pt': 'métrica desconhecida {got}',
        'it': 'metrica sconosciuta {got}',
        'ja': '不明な指標 {got}',
        'zh': '未知指标 {got}',
        'hi': 'अज्ञात मीट्रिक {got}',
        'ar': 'مقياس غير معروف {got}',
    },
    MAIL_SERVER_REFUSED: {
        'es': 'el servidor de correo lo rechazó: {detail}',
        'fr': "le serveur de courrier l'a refusé : {detail}",
        'de': 'der Mailserver hat es abgelehnt: {detail}',
        'pt': 'o servidor de correio recusou: {detail}',
        'it': 'il server di posta lo ha rifiutato: {detail}',
        'ja': 'メールサーバーに拒否されました: {detail}',
        'zh': '邮件服务器拒绝了它：{detail}',
        'hi': 'मेल सर्वर ने अस्वीकार किया: {detail}',
        'ar': 'رفضه خادم البريد: {detail}',
    },
    SIGNATURE_MUST_MATCH: {
        'es': 'la firma debe coincidir con el nombre inscrito ({name})',
        'fr': "la signature doit correspondre au nom inscrit ({name})",
        'de': 'die Unterschrift muss dem eingetragenen Namen entsprechen '
              '({name})',
        'pt': 'a assinatura deve corresponder ao nome inscrito ({name})',
        'it': 'la firma deve corrispondere al nome registrato ({name})',
        'ja': '署名は登録された名前と一致する必要があります（{name}）',
        'zh': '签名必须与登记的姓名一致（{name}）',
        'hi': 'हस्ताक्षर पंजीकृत नाम से मेल खाना चाहिए ({name})',
        'ar': 'يجب أن يطابق التوقيع الاسم المسجل ({name})',
    },
    SOURCE_NOT_CONSENTED: {
        'es': 'la fuente {source} no tiene consentimiento para este usuario',
        'fr': "la source {source} n'a pas de consentement pour cet "
              'utilisateur',
        'de': 'für die Quelle {source} liegt keine Einwilligung dieses '
              'Nutzers vor',
        'pt': 'a fonte {source} não tem consentimento para este utilizador',
        'it': 'la fonte {source} non ha il consenso per questo utente',
        'ja': 'ソース {source} はこのユーザーについて同意されていません',
        'zh': '来源 {source} 未获得该用户的同意',
        'hi': 'स्रोत {source} के लिए इस उपयोगकर्ता की सहमति नहीं है',
        'ar': 'المصدر {source} غير مأذون به لهذا المستخدم',
    },
    COULD_NOT_FETCH: {
        'es': 'no se pudo obtener — {kind}: {detail}',
        'fr': 'récupération impossible — {kind} : {detail}',
        'de': 'Abruf fehlgeschlagen — {kind}: {detail}',
        'pt': 'não foi possível obter — {kind}: {detail}',
        'it': 'impossibile recuperare — {kind}: {detail}',
        'ja': '取得できませんでした — {kind}: {detail}',
        'zh': '无法获取 — {kind}：{detail}',
        'hi': 'प्राप्त नहीं हो सका — {kind}: {detail}',
        'ar': 'تعذّر الجلب — {kind}: {detail}',
    },
    UNKNOWN_CONNECTOR: {
        'es': 'conector desconocido: {provider}/{app}',
        'fr': 'connecteur inconnu : {provider}/{app}',
        'de': 'unbekannter Connector: {provider}/{app}',
        'pt': 'conector desconhecido: {provider}/{app}',
        'it': 'connettore sconosciuto: {provider}/{app}',
        'ja': '不明なコネクタ: {provider}/{app}',
        'zh': '未知连接器：{provider}/{app}',
        'hi': 'अज्ञात कनेक्टर: {provider}/{app}',
        'ar': 'موصل غير معروف: {provider}/{app}',
    },
    APP_DOES_NOT_OFFER: {
        'es': '{app} no ofrece: {capabilities}',
        'fr': "{app} n'offre pas : {capabilities}",
        'de': '{app} bietet nicht an: {capabilities}',
        'pt': '{app} não oferece: {capabilities}',
        'it': '{app} non offre: {capabilities}',
        'ja': '{app} は提供していません: {capabilities}',
        'zh': '{app} 不提供：{capabilities}',
        'hi': '{app} यह प्रदान नहीं करता: {capabilities}',
        'ar': '{app} لا يقدم: {capabilities}',
    },
    NO_COLLECT_SUPPORT: {
        'es': '{app} no admite recopilar contexto',
        'fr': '{app} ne prend pas en charge la collecte de contexte',
        'de': '{app} unterstützt kein Einsammeln von Kontext',
        'pt': '{app} não suporta recolher contexto',
        'it': '{app} non supporta la raccolta di contesto',
        'ja': '{app} はコンテキストの収集に対応していません',
        'zh': '{app} 不支持收集上下文',
        'hi': '{app} संदर्भ एकत्र करने का समर्थन नहीं करता',
        'ar': '{app} لا يدعم جمع السياق',
    },
    CAPABILITY_NOT_GRANTED: {
        'es': 'a este conector de {app} no se le concedió {capability}',
        'fr': "ce connecteur {app} n'a pas reçu {capability}",
        'de': 'diesem {app}-Connector wurde {capability} nicht gewährt',
        'pt': 'a este conector de {app} não foi concedido {capability}',
        'it': 'a questo connettore {app} non è stato concesso {capability}',
        'ja': 'この {app} コネクタには {capability} が許可されていません',
        'zh': '这个 {app} 连接器未被授予 {capability}',
        'hi': 'इस {app} कनेक्टर को {capability} नहीं दिया गया',
        'ar': 'هذا الموصل {app} لم يُمنح {capability}',
    },
    NO_SUCH_FACE: {
        'es': 'no existe la cara {got}; una de {choices}',
        'fr': 'aucune face {got} ; parmi {choices}',
        'de': 'keine Kachel {got}; eine von {choices}',
        'pt': 'não existe a face {got}; uma de {choices}',
        'it': 'nessuna faccia {got}; una tra {choices}',
        'ja': '{got} という面はありません。次のいずれか: {choices}',
        'zh': '没有 {got} 这个面板；应为 {choices} 之一',
        'hi': '{got} नाम का कोई फ़ेस नहीं; इनमें से एक: {choices}',
        'ar': 'لا يوجد وجه {got}؛ أحد التالي: {choices}',
    },
    PANE_BOTTOM_CORNER: {
        'es': 'el panel va en una esquina inferior — {choices}',
        'fr': 'le panneau se place dans un coin inférieur — {choices}',
        'de': 'die Leiste sitzt in einer unteren Ecke — {choices}',
        'pt': 'o painel fica num canto inferior — {choices}',
        'it': 'il pannello sta in un angolo inferiore — {choices}',
        'ja': 'パネルは下側の隅に置かれます — {choices}',
        'zh': '面板位于底部角落 — {choices}',
        'hi': 'पैन नीचे के किसी कोने में रहता है — {choices}',
        'ar': 'اللوحة تكون في زاوية سفلية — {choices}',
    },
    UNKNOWN_STATE: {
        'es': 'estado desconocido {got}; uno de {choices}',
        'fr': 'état inconnu {got} ; parmi {choices}',
        'de': 'unbekannter Zustand {got}; einer von {choices}',
        'pt': 'estado desconhecido {got}; um de {choices}',
        'it': 'stato sconosciuto {got}; uno tra {choices}',
        'ja': '不明な状態 {got}。次のいずれか: {choices}',
        'zh': '未知状态 {got}；应为 {choices} 之一',
        'hi': 'अज्ञात स्थिति {got}; इनमें से एक: {choices}',
        'ar': 'حالة غير معروفة {got}؛ أحد التالي: {choices}',
    },
    FACE_NOT_CARRIED: {
        'es': '{got} no es una de las caras que lleva este panel',
        'fr': "{got} n'est pas une des faces portées par ce panneau",
        'de': '{got} gehört nicht zu den Kacheln dieser Leiste',
        'pt': '{got} não é uma das faces que este painel transporta',
        'it': '{got} non è una delle facce di questo pannello',
        'ja': '{got} はこのドックが載せている面ではありません',
        'zh': '{got} 不在这个面板承载的面之中',
        'hi': '{got} इस डॉक की फ़ेसों में से नहीं है',
        'ar': '{got} ليس من الوجوه التي تحملها هذه اللوحة',
    },
    FACE_CANNOT_BE_REMOVED: {
        'es': '{face} no se puede quitar del panel — es la cara que aparece '
              'cuando algo va mal, y un panel que alguien apartó hace meses '
              'no es una decisión que tomara sobre el día en que salta',
        'fr': '{face} ne peut pas être retirée du panneau — c’est la face '
              'qui apparaît quand quelque chose va mal, et un panneau '
              'écarté il y a des mois n’est pas une décision prise pour le '
              'jour où il se déclenche',
        'de': '{face} kann nicht aus der Leiste entfernt werden — es ist '
              'die Kachel, die erscheint, wenn etwas nicht stimmt, und eine '
              'vor Monaten beiseitegeschobene Leiste ist keine Entscheidung '
              'über den Tag, an dem sie anschlägt',
        'pt': '{face} não pode ser removida do painel — é a face que '
              'aparece quando algo está mal, e um painel que alguém afastou '
              'há meses não é uma decisão sobre o dia em que ele dispara',
        'it': '{face} non può essere tolta dal pannello — è la faccia che '
              'compare quando qualcosa va male, e un pannello messo da '
              'parte mesi fa non è una decisione presa sul giorno in cui '
              'scatta',
        'ja': '{face} はパネルから外せません — 何かが起きたときに現れる面'
              'であり、何か月も前に脇へ寄せた設定は、それが鳴る日について'
              'の判断ではありません',
        'zh': '{face} 不能从面板中移除 — 它是出问题时出现的那个面，几个月'
              '前被人挪开的面板并不是对它响起那天做出的决定',
        'hi': '{face} को पैन से हटाया नहीं जा सकता — यही वह फ़ेस है जो कुछ '
              'गलत होने पर दिखती है, और महीनों पहले किनारे किया गया पैन उस '
              'दिन के बारे में लिया गया निर्णय नहीं है जिस दिन वह बजे',
        'ar': '{face} لا يمكن إزالته من اللوحة — إنه الوجه الذي يظهر حين '
              'يسوء شيء، ولوحة أزاحها أحدهم قبل أشهر ليست قرارًا اتخذه '
              'بشأن اليوم الذي تنطلق فيه',
    },
    FACE_NEEDS_A_SURFACE: {
        'es': 'la cara {face} trata de una en particular — dile cuál',
        'fr': 'la face {face} concerne une en particulier — dites-lui '
              'laquelle',
        'de': 'die Kachel {face} bezieht sich auf eine bestimmte — sag ihr '
              'welche',
        'pt': 'a face {face} é sobre uma em particular — diz-lhe qual',
        'it': 'la faccia {face} riguarda una in particolare — dille quale',
        'ja': '{face} の面は特定の対象についてのものです — どれかを指定して'
              'ください',
        'zh': '{face} 面针对的是特定的一个 — 请告诉它是哪一个',
        'hi': '{face} फ़ेस किसी विशेष के बारे में है — बताएँ किसके',
        'ar': 'وجه {face} يخص واحدًا بعينه — حدد أيها',
    },
    ROTA_NOT_JSON: {
        'es': 'JIM_SITE_ROTA no es JSON válido: {detail}',
        'fr': "JIM_SITE_ROTA n'est pas du JSON valide : {detail}",
        'de': 'JIM_SITE_ROTA ist kein gültiges JSON: {detail}',
        'pt': 'JIM_SITE_ROTA não é JSON válido: {detail}',
        'it': 'JIM_SITE_ROTA non è JSON valido: {detail}',
        'ja': 'JIM_SITE_ROTA が有効な JSON ではありません: {detail}',
        'zh': 'JIM_SITE_ROTA 不是有效的 JSON：{detail}',
        'hi': 'JIM_SITE_ROTA मान्य JSON नहीं है: {detail}',
        'ar': 'JIM_SITE_ROTA ليس JSON صالحًا: {detail}',
    },
    ROTA_ENTRY_NEEDS_NAME: {
        'es': 'la entrada {index} de la rota necesita un nombre',
        'fr': "l'entrée {index} du planning a besoin d'un nom",
        'de': 'Rota-Eintrag {index} braucht einen Namen',
        'pt': 'a entrada {index} da escala precisa de um nome',
        'it': 'la voce {index} del turno ha bisogno di un nome',
        'ja': 'ロタの項目 {index} には名前が必要です',
        'zh': '排班条目 {index} 需要一个名字',
        'hi': 'रोटा प्रविष्टि {index} को एक नाम चाहिए',
        'ar': 'مدخل الجدول {index} يحتاج إلى اسم',
    },
    UNKNOWN_DAY_RANGE: {
        'es': 'rango de días desconocido {got}',
        'fr': 'plage de jours inconnue {got}',
        'de': 'unbekannter Tagesbereich {got}',
        'pt': 'intervalo de dias desconhecido {got}',
        'it': 'intervallo di giorni sconosciuto {got}',
        'ja': '不明な曜日範囲 {got}',
        'zh': '未知的日期范围 {got}',
        'hi': 'अज्ञात दिन-सीमा {got}',
        'ar': 'نطاق أيام غير معروف {got}',
    },
    UNKNOWN_DAY: {
        'es': 'día desconocido {got}',
        'fr': 'jour inconnu {got}',
        'de': 'unbekannter Tag {got}',
        'pt': 'dia desconhecido {got}',
        'it': 'giorno sconosciuto {got}',
        'ja': '不明な曜日 {got}',
        'zh': '未知的日子 {got}',
        'hi': 'अज्ञात दिन {got}',
        'ar': 'يوم غير معروف {got}',
    },
    UNREADABLE_TIME: {
        'es': 'hora ilegible {got} — usa HH:MM',
        'fr': 'heure illisible {got} — utilisez HH:MM',
        'de': 'unlesbare Zeit {got} — HH:MM verwenden',
        'pt': 'hora ilegível {got} — usa HH:MM',
        'it': 'orario illeggibile {got} — usa HH:MM',
        'ja': '読み取れない時刻 {got} — HH:MM で指定してください',
        'zh': '无法读取的时间 {got} — 请用 HH:MM',
        'hi': 'अपठनीय समय {got} — HH:MM प्रयोग करें',
        'ar': 'وقت غير مقروء {got} — استخدم HH:MM',
    },
    UNKNOWN_ACCOUNT_KIND: {
        'es': 'tipo de cuenta desconocido {got}; se esperaba uno de {choices}',
        'fr': 'type de compte inconnu {got} ; attendu parmi {choices}',
        'de': 'unbekannte Kontoart {got}; erwartet: eine von {choices}',
        'pt': 'tipo de conta desconhecido {got}; esperava-se um de {choices}',
        'it': 'tipo di conto sconosciuto {got}; atteso uno tra {choices}',
        'ja': '不明な口座種別 {got}。次のいずれかが必要です: {choices}',
        'zh': '未知的账户类型 {got}；应为 {choices} 之一',
        'hi': 'अज्ञात खाता प्रकार {got}; इनमें से एक अपेक्षित: {choices}',
        'ar': 'نوع حساب غير معروف {got}؛ المتوقع أحد التالي: {choices}',
    },
    UNKNOWN_AGGREGATOR: {
        'es': 'agregador desconocido {got}; este módulo guarda '
              'consentimientos para {choices}',
        'fr': 'agrégateur inconnu {got} ; ce module détient des '
              'consentements pour {choices}',
        'de': 'unbekannter Aggregator {got}; dieses Modul hält '
              'Einwilligungen für {choices}',
        'pt': 'agregador desconhecido {got}; este módulo guarda '
              'consentimentos para {choices}',
        'it': 'aggregatore sconosciuto {got}; questo modulo conserva '
              'consensi per {choices}',
        'ja': '不明なアグリゲータ {got}。このモジュールが同意を保持するのは '
              '{choices} です',
        'zh': '未知的聚合方 {got}；本模块保存的同意仅涵盖 {choices}',
        'hi': 'अज्ञात एग्रीगेटर {got}; यह मॉड्यूल {choices} के लिए सहमतियाँ '
              'रखता है',
        'ar': 'مجمّع غير معروف {got}؛ هذه الوحدة تحفظ الموافقات لـ {choices}',
    },
    UNKNOWN_ASSET_CLASSES: {
        'es': 'clase(s) de activo desconocida(s): {got}; se esperaba entre '
              '{choices}',
        'fr': "classe(s) d'actifs inconnue(s) : {got} ; attendu parmi "
              '{choices}',
        'de': 'unbekannte Anlageklasse(n): {got}; erwartet unter {choices}',
        'pt': 'classe(s) de ativos desconhecida(s): {got}; esperava-se '
              'entre {choices}',
        'it': 'classe/i di attivo sconosciuta/e: {got}; attese tra {choices}',
        'ja': '不明な資産クラス: {got}。{choices} のいずれかが必要です',
        'zh': '未知的资产类别：{got}；应在 {choices} 之中',
        'hi': 'अज्ञात परिसंपत्ति वर्ग: {got}; {choices} में से अपेक्षित',
        'ar': 'فئة/فئات أصول غير معروفة: {got}؛ المتوقع من بين {choices}',
    },
    NO_AGGREGATOR_CREDENTIALS: {
        'es': 'este despliegue no tiene credenciales de {aggregator} — el '
              'consentimiento sigue en pie y sincronizará cuando el '
              'agregador esté configurado; hasta entonces, deja un extracto '
              'o registra un saldo a mano',
        'fr': "ce déploiement ne détient pas d'identifiants {aggregator} — "
              'le consentement demeure et synchronisera quand '
              "l'agrégateur sera configuré ; d'ici là, déposez un relevé ou "
              'notez un solde à la main',
        'de': 'diese Installation hält keine {aggregator}-Zugangsdaten — '
              'die Einwilligung bleibt bestehen und synchronisiert, sobald '
              'der Aggregator eingerichtet ist; bis dahin lege einen '
              'Kontoauszug ab oder trage einen Stand von Hand ein',
        'pt': 'esta instalação não guarda credenciais de {aggregator} — o '
              'consentimento mantém-se e sincronizará quando o agregador '
              'estiver configurado; até lá, deixa um extrato ou regista um '
              'saldo à mão',
        'it': 'questa installazione non detiene credenziali {aggregator} — '
              "il consenso resta e sincronizzerà quando l'aggregatore sarà "
              'configurato; fino ad allora, deposita un estratto o annota '
              'un saldo a mano',
        'ja': 'この環境は {aggregator} の資格情報を持っていません — 同意は'
              '有効なままで、アグリゲータが設定されれば同期します。それ'
              'までは明細を置くか、残高を手で記録してください',
        'zh': '此部署没有 {aggregator} 的凭据 — 同意仍然有效，待聚合方配置'
              '好后会同步；在那之前，请上传对账单或手工记录余额',
        'hi': 'इस परिनियोजन में {aggregator} की साख नहीं है — सहमति बनी '
              'रहेगी और एग्रीगेटर सेट होने पर समन्वय होगा; तब तक विवरण डालें '
              'या शेष हाथ से दर्ज करें',
        'ar': 'هذا النشر لا يحمل بيانات اعتماد {aggregator} — الموافقة '
              'قائمة وستتزامن عند تهيئة المجمّع؛ حتى ذلك الحين، أودع كشفًا '
              'أو سجّل رصيدًا يدويًا',
    },
    AGGREGATOR_NOT_WIRED: {
        'es': 'el cliente de {aggregator} no está integrado en esta '
              'compilación; el consentimiento sigue en pie, y nada se '
              'inventó en su nombre',
        'fr': "le client {aggregator} n'est pas câblé dans cette version ; "
              "le consentement demeure, et rien n'a été inventé en son nom",
        'de': 'der {aggregator}-Client ist in diesem Build nicht verdrahtet; '
              'die Einwilligung bleibt bestehen, und nichts wurde in ihrem '
              'Namen erfunden',
        'pt': 'o cliente de {aggregator} não está ligado nesta compilação; '
              'o consentimento mantém-se, e nada foi inventado em seu nome',
        'it': 'il client {aggregator} non è collegato in questa build; il '
              'consenso resta, e nulla è stato inventato a suo nome',
        'ja': 'このビルドには {aggregator} クライアントが組み込まれていま'
              'せん。同意は有効なままで、その名の下に何も作り出されて'
              'いません',
        'zh': '此构建未接入 {aggregator} 客户端；同意仍然有效，也没有以其'
              '名义虚构任何数据',
        'hi': 'इस बिल्ड में {aggregator} क्लाइंट जुड़ा नहीं है; सहमति बनी '
              'है, और उसके नाम पर कुछ भी गढ़ा नहीं गया',
        'ar': 'عميل {aggregator} غير موصول في هذا الإصدار؛ الموافقة قائمة، '
              'ولم يُختلق شيء باسمها',
    },
    UNKNOWN_CHOICE: {
        'es': '{field} desconocido {got}; uno de {choices}',
        'fr': '{field} inconnu {got} ; parmi {choices}',
        'de': 'unbekannte(r) {field} {got}; eine(r) von {choices}',
        'pt': '{field} desconhecido {got}; um de {choices}',
        'it': '{field} sconosciuto {got}; uno tra {choices}',
        'ja': '不明な {field} {got}。次のいずれか: {choices}',
        'zh': '未知的 {field} {got}；应为 {choices} 之一',
        'hi': 'अज्ञात {field} {got}; इनमें से एक: {choices}',
        'ar': '{field} غير معروف {got}؛ أحد التالي: {choices}',
    },
    UNKNOWN_VALUE: {
        'es': '{field} desconocido {got}',
        'fr': '{field} inconnu {got}',
        'de': 'unbekannte(r) {field} {got}',
        'pt': '{field} desconhecido {got}',
        'it': '{field} sconosciuto {got}',
        'ja': '不明な {field} {got}',
        'zh': '未知的 {field} {got}',
        'hi': 'अज्ञात {field} {got}',
        'ar': '{field} غير معروف {got}',
    },
    UNKNOWN_MODE_ONE_OF: {
        'es': 'modo desconocido {got} — uno de {choices}',
        'fr': 'mode inconnu {got} — parmi {choices}',
        'de': 'unbekannter Modus {got} — einer von {choices}',
        'pt': 'modo desconhecido {got} — um de {choices}',
        'it': 'modalità sconosciuta {got} — una tra {choices}',
        'ja': '不明なモード {got} — 次のいずれか: {choices}',
        'zh': '未知模式 {got} — 应为 {choices} 之一',
        'hi': 'अज्ञात मोड {got} — इनमें से एक: {choices}',
        'ar': 'وضع غير معروف {got} — أحد التالي: {choices}',
    },
    UNKNOWN_FEATURE_SWITCHES: {
        'es': 'función desconocida {got}; los interruptores son {choices}',
        'fr': 'fonction inconnue {got} ; les interrupteurs sont {choices}',
        'de': 'unbekannte Funktion {got}; die Schalter sind {choices}',
        'pt': 'função desconhecida {got}; os interruptores são {choices}',
        'it': 'funzione sconosciuta {got}; gli interruttori sono {choices}',
        'ja': '不明な機能 {got}。スイッチは {choices} です',
        'zh': '未知功能 {got}；开关有 {choices}',
        'hi': 'अज्ञात फ़ीचर {got}; स्विच ये हैं: {choices}',
        'ar': 'ميزة غير معروفة {got}؛ المفاتيح هي {choices}',
    },
    UNKNOWN_ROBOT_MODEL: {
        'es': 'modelo de robot desconocido {got}',
        'fr': 'modèle de robot inconnu {got}',
        'de': 'unbekanntes Robotermodell {got}',
        'pt': 'modelo de robô desconhecido {got}',
        'it': 'modello di robot sconosciuto {got}',
        'ja': '不明なロボットモデル {got}',
        'zh': '未知的机器人型号 {got}',
        'hi': 'अज्ञात रोबोट मॉडल {got}',
        'ar': 'طراز روبوت غير معروف {got}',
    },
    COMMAND_NOT_PERMITTED: {
        'es': '{command} no está permitido para {label}; permitidos: {choices}',
        'fr': "{command} n'est pas permis pour {label} ; autorisés : {choices}",
        'de': '{command} ist für {label} nicht erlaubt; erlaubt: {choices}',
        'pt': '{command} não é permitido para {label}; permitidos: {choices}',
        'it': '{command} non è permesso per {label}; consentiti: {choices}',
        'ja': '{command} は {label} には許可されていません。許可: {choices}',
        'zh': '{command} 不允许用于 {label}；允许的有：{choices}',
        'hi': '{command} {label} के लिए अनुमत नहीं; अनुमत: {choices}',
        'ar': '{command} غير مسموح به لـ {label}؛ المسموح: {choices}',
    },
    NO_BEARING: {
        'es': 'no hay porte llamado {got} — es companion o professional',
        'fr': "aucune posture nommée {got} — c'est companion ou professional",
        'de': 'keine Haltung namens {got} — companion oder professional',
        'pt': 'não há postura chamada {got} — é companion ou professional',
        'it': 'nessun portamento chiamato {got} — è companion o professional',
        'ja': '{got} という立ち位置はありません — companion か professional です',
        'zh': '没有名为 {got} 的姿态 — 只有 companion 或 professional',
        'hi': '{got} नाम की कोई भूमिका नहीं — companion या professional है',
        'ar': 'لا توجد هيئة باسم {got} — إنها companion أو professional',
    },
    NO_PERMIT_AREA: {
        'es': 'no hay área de permiso llamada {got}',
        'fr': "aucune zone d'autorisation nommée {got}",
        'de': 'kein Freigabebereich namens {got}',
        'pt': 'não há área de permissão chamada {got}',
        'it': 'nessuna area di permesso chiamata {got}',
        'ja': '{got} という許可領域はありません',
        'zh': '没有名为 {got} 的许可区域',
        'hi': '{got} नाम का कोई अनुमति क्षेत्र नहीं',
        'ar': 'لا توجد منطقة تصريح باسم {got}',
    },
    NO_SUCH_STEP: {
        'es': 'no existe el paso {got}',
        'fr': 'aucune étape {got}',
        'de': 'kein Schritt {got}',
        'pt': 'não existe o passo {got}',
        'it': 'nessun passo {got}',
        'ja': '{got} という手順はありません',
        'zh': '没有 {got} 这一步',
        'hi': '{got} नाम का कोई चरण नहीं',
        'ar': 'لا توجد خطوة {got}',
    },
    NO_SURFACE: {
        'es': 'no hay superficie llamada {got}',
        'fr': 'aucune surface nommée {got}',
        'de': 'keine Oberfläche namens {got}',
        'pt': 'não há superfície chamada {got}',
        'it': 'nessuna superficie chiamata {got}',
        'ja': '{got} というサーフェスはありません',
        'zh': '没有名为 {got} 的表面',
        'hi': '{got} नाम की कोई सतह नहीं',
        'ar': 'لا يوجد سطح باسم {got}',
    },
    FILE_TOO_LARGE: {
        'es': 'eso son {size}MB; el límite es {limit}MB',
        'fr': 'cela fait {size}Mo ; la limite est de {limit}Mo',
        'de': 'das sind {size}MB; die Grenze liegt bei {limit}MB',
        'pt': 'isso são {size}MB; o limite é {limit}MB',
        'it': 'sono {size}MB; il limite è {limit}MB',
        'ja': 'それは {size}MB です。上限は {limit}MB です',
        'zh': '这有 {size}MB；上限是 {limit}MB',
        'hi': 'यह {size}MB है; सीमा {limit}MB है',
        'ar': 'هذا {size} ميغابايت؛ الحد هو {limit} ميغابايت',
    },
    TOP_FRIENDS_MAX: {
        'es': 'los mejores amigos son como máximo {max} — eso es lo que lo '
              'hace un ranking',
        'fr': 'les meilleurs amis sont au plus {max} — c’est ce qui en fait '
              'un classement',
        'de': 'Top-Freunde sind höchstens {max} — genau das macht es zu '
              'einer Rangliste',
        'pt': 'os melhores amigos são no máximo {max} — é isso que faz dele '
              'um ranking',
        'it': 'i migliori amici sono al massimo {max} — è questo che lo '
              'rende una classifica',
        'ja': 'トップフレンドは最大 {max} 人です — だからこそランキングに'
              'なります',
        'zh': '挚友最多 {max} 位 — 正因如此它才是个排名',
        'hi': 'शीर्ष मित्र अधिकतम {max} — यही इसे रैंकिंग बनाता है',
        'ar': 'أفضل الأصدقاء بحد أقصى {max} — هذا ما يجعله ترتيبًا',
    },
    MAX_LINKS: {
        'es': 'hasta {max} enlaces; una página de inicio es una página, no '
              'un directorio',
        'fr': "jusqu'à {max} liens ; une page d'accueil est une page, pas "
              'un annuaire',
        'de': 'bis zu {max} Links; eine Startseite ist eine Seite, kein '
              'Verzeichnis',
        'pt': 'até {max} ligações; uma página inicial é uma página, não um '
              'diretório',
        'it': 'fino a {max} link; una homepage è una pagina, non una '
              'directory',
        'ja': 'リンクは最大 {max} 件です。ホームページはページであって、'
              'ディレクトリではありません',
        'zh': '最多 {max} 个链接；主页是一个页面，不是目录',
        'hi': 'अधिकतम {max} लिंक; होमपेज एक पन्ना है, निर्देशिका नहीं',
        'ar': 'حتى {max} روابط؛ الصفحة الرئيسية صفحة، وليست دليلًا',
    },
    NOTHING_READABLE: {
        'es': '{url} respondió sin nada legible',
        'fr': "{url} a répondu sans rien de lisible",
        'de': '{url} hat nichts Lesbares geliefert',
        'pt': '{url} respondeu sem nada legível',
        'it': '{url} ha risposto senza nulla di leggibile',
        'ja': '{url} からは読めるものが返ってきませんでした',
        'zh': '{url} 的响应中没有可读内容',
        'hi': '{url} ने कुछ भी पठनीय नहीं लौटाया',
        'ar': '{url} أجاب دون أي شيء مقروء',
    },
    CANNOT_RUN_ONBOARD_LLM: {
        'es': '{label} no puede ejecutar un LLM a bordo',
        'fr': '{label} ne peut pas exécuter de LLM embarqué',
        'de': '{label} kann kein Onboard-LLM ausführen',
        'pt': '{label} não pode executar um LLM a bordo',
        'it': '{label} non può eseguire un LLM a bordo',
        'ja': '{label} はオンボード LLM を実行できません',
        'zh': '{label} 无法运行板载 LLM',
        'hi': '{label} ऑनबोर्ड LLM नहीं चला सकता',
        'ar': '{label} لا يمكنه تشغيل LLM مدمج',
    },
    INTIMATE_NEEDS_CONSENT: {
        'es': '{site} necesita una confirmación explícita antes de '
              'guardarse. Quedará fuera de todo lo automático — ningún '
              'agente sintético lo recibe jamás, y nunca se incorpora a un '
              'resumen compuesto; un clínico lo abre deliberadamente o no '
              'lo abre',
        'fr': '{site} demande une confirmation explicite avant '
              "d'être conservé. Il restera hors de tout automatisme — aucun "
              "agent synthétique ne le reçoit jamais, et il n'est jamais "
              'intégré à un résumé assemblé ; un clinicien l’ouvre '
              'délibérément ou pas du tout',
        'de': '{site} braucht eine ausdrückliche Bestätigung, bevor es '
              'gespeichert wird. Es bleibt aus allem Automatischen heraus — '
              'kein synthetischer Agent erhält es je, und es fließt nie in '
              'eine zusammengestellte Übersicht ein; eine Fachkraft öffnet '
              'es bewusst oder gar nicht',
        'pt': '{site} precisa de uma confirmação explícita antes de ser '
              'guardado. Ficará fora de tudo o que é automático — nenhum '
              'agente sintético o recebe, e nunca é incorporado num resumo '
              'montado; um clínico abre-o deliberadamente ou não o abre',
        'it': '{site} richiede una conferma esplicita prima di essere '
              'conservato. Resterà fuori da tutto ciò che è automatico — '
              'nessun agente sintetico lo riceve mai, e non viene mai '
              'incluso in un riepilogo assemblato; un clinico lo apre '
              'deliberatamente o non lo apre affatto',
        'ja': '{site} は保存の前に明示的な確認が必要です。自動処理からは'
              '一切外されます — 合成エージェントが受け取ることはなく、'
              '組み立てられた要約に折り込まれることもありません。臨床医が'
              '意図して開くか、まったく開かないかのどちらかです',
        'zh': '{site} 在存储前需要明确确认。它将被排除在一切自动处理之外 '
              '— 任何合成代理都不会收到它，也绝不会被并入汇总摘要；只有'
              '临床医生有意打开，或根本不打开',
        'hi': '{site} को संग्रहित करने से पहले स्पष्ट पुष्टि चाहिए। यह हर '
              'स्वचालित चीज़ से बाहर रहेगा — कोई सिंथेटिक एजेंट इसे कभी नहीं '
              'पाता, और यह कभी किसी संकलित सारांश में नहीं जुड़ता; चिकित्सक '
              'इसे जान-बूझकर खोलता है या बिल्कुल नहीं',
        'ar': '{site} يحتاج إلى تأكيد صريح قبل تخزينه. سيبقى خارج كل ما هو '
              'تلقائي — لا يتلقاه أي وكيل اصطناعي أبدًا، ولا يُدمج في '
              'ملخص مجمّع؛ يفتحه الطبيب عمدًا أو لا يفتحه إطلاقًا',
    },
}


class Term(str):
    """A slot drawn from the product's own closed vocabulary.

    `f"objection is already {obj['status']}"` has a slot holding `open`,
    `upheld` or `dismissed` — the API's words, which a client branches on. They
    stay those words on the wire. But inside a sentence a person reads, an
    English key in a Portuguese frame is the mixed sentence this whole
    mechanism exists to prevent, and `_SLOT_TOKEN` cannot catch it: `upheld` is
    one word with no whitespace, indistinguishable from an identifier.

    So the author marks it, and the marking is what makes it translatable:

        i18n.fill(i18n.OBJECTION_ALREADY, status=i18n.Term(obj["status"]))

    Translated at render, not at raise: the reader's language is not known at
    the raise site, which is the reason the handler does this work at all.
    """


class Opening(Term):
    """A `Term` that begins its sentence, and so is capitalised.

    After translation, never before. The vocabulary holds one form of each
    phrase — `create and run your own synthetic profiles` — and each language
    raises its own first letter from that; a capitalised table would need a
    second copy of every entry, free to drift from the first.

    `str.capitalize()` is wrong here: it lower-cases everything after the first
    character, which would turn German's `im Marktplatz einstellen` into
    something with its nouns flattened. Only the first character moves.
    """


def _open(text: str) -> str:
    return text[:1].upper() + text[1:]


def term(word: str, language: str) -> str:
    """One vocabulary word in the reader's language.

    Unknown words come back unchanged, which is a visible gap rather than a
    confident error — and `test_every_state_a_refusal_can_name_has_a_word`
    fails on any this product can actually reach.
    """
    if language == DEFAULT:
        return word
    return _VOCABULARY.get(word, {}).get(language, word)


def tr_refusal(text: str, language: str) -> str:
    """Translate one of the sentences this product refuses with."""
    if language == DEFAULT:
        return text
    return (_REFUSALS.get(text) or _TEMPLATES.get(text)
            or _VALIDATION.get(text)
            or _STRINGS.get(text, {})).get(language, text)


def localize_detail(detail, language: str):
    """A refusal payload, translated in whichever shape it arrives.

    Only the sentence. `_storage_refusal` sends `reason`, `have`, `needs` and
    `period` alongside it, and the console branches on those: what a person
    reads is translated, what a client compares is not.
    """
    if language == DEFAULT:
        return detail
    # Before the plain-string branch: a Templated *is* a str, and its value is
    # the finished English sentence, which is not a key in any table. Looking
    # it up would find nothing and return the English — silently, and
    # indistinguishably from a sentence nobody has translated yet.
    if isinstance(detail, Templated):
        if not detail.translatable:
            return str(detail)
        # A vocabulary word with no translation would land in the frame as an
        # English key — the mixed sentence `Term` exists to prevent, arriving
        # through the mechanism built to prevent it. Structural rather than
        # enumerated.
        vocabulary = [v for v in detail.slots.values() if isinstance(v, Term)]
        if any(str(v) not in _VOCABULARY for v in vocabulary):
            return str(detail)
        frame = tr_refusal(detail.template, language)
        filling = {}
        for key, value in detail.slots.items():
            if isinstance(value, Opening):
                filling[key] = _open(term(value, language))
            elif isinstance(value, Term):
                filling[key] = term(value, language)
            else:
                filling[key] = value
        try:
            return frame.format(**filling)
        except (KeyError, IndexError, ValueError):
            # A translation whose braces do not match the template's. The
            # English sentence is correct and complete; a half-formatted one
            # in the reader's language is not.
            return str(detail)
    if isinstance(detail, str):
        return tr_refusal(detail, language)
    if isinstance(detail, dict) and "detail" in detail:
        # Recursion rather than `tr_refusal`, and this is the whole fix.
        #
        # A `Templated` **is** a `str`, so the version of this branch that
        # asked `isinstance(detail["detail"], str)` caught every built
        # sentence the wrapper had put here and looked it up by its finished
        # English — which is a key in no table. `MUST_BE_ONE_OF` went out in
        # English from seven raise sites, in every language, silently, and
        # indistinguishably from a sentence nobody had translated yet.
        #
        #     asked     is the refusal translated
        #     mattered  is it translated where the wrapper actually puts it
        #
        # Recursing sends it back through the `Templated` branch at the top,
        # which is the one that knows how it was built.
        return {**detail, "detail": localize_detail(detail["detail"], language)}
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        return {**detail, "message": tr_refusal(detail["message"], language)}
    return detail


def refusal_language(request) -> str:
    """The language the person receiving this refusal reads.

    Never raises. This runs inside exception handlers, and a diagnostic that
    can fail turns a refusal into a 500 — telling somebody the server broke
    when it was really telling them no.
    """
    from . import auth
    try:
        who = auth.principal(request)
        if who and who.get("role") == "user":
            return get_language(who["subject_id"])
    except Exception:
        pass
    try:
        return negotiate(request.headers.get("accept-language"))
    except Exception:
        return DEFAULT


#: The product's own closed sets, for the moment one lands inside a sentence a
#: person reads. `Term` marks them at the raise site; `term()` resolves them at
#: render, when the reader's language is finally known.
#:
#: The keys are the exact strings in `tiers.CAPABILITIES`, and
#: `test_every_capability_the_gate_names_has_a_translation` holds them to it —
#: a description edited there and not here keeps the refusal English rather
#: than mixing, but silently, which is the state this table exists to leave.
_VOCABULARY: dict[str, dict[str, str]] = {
    # The notice an assisted call plays, in the words a support line has
    # always used. Translated because the person hearing it is on the other
    # end of somebody else's phone call and did not choose this product's
    # language — see jim/oncall.py, which picks the language from the
    # dialling code.
    'This call may be monitored or recorded to better assist you.': {
        'es': "Esta llamada puede ser supervisada o grabada para poder atenderle mejor.",
        'fr': "Cet appel est susceptible d'être écouté ou enregistré afin de mieux vous servir.",
        'de': "Dieses Gespräch kann mitgehört oder aufgezeichnet werden, um Sie besser betreuen zu können.",
        'pt': "Esta chamada pode ser acompanhada ou gravada para melhor o atendermos.",
        'it': "Questa chiamata può essere ascoltata o registrata per servirla meglio.",
        'ja': "このお電話は、より良い対応のため、モニタリングまたは録音させていただく場合がございます。",
        'zh': "为了更好地为您服务，本次通话可能会被监听或录音。",
        'hi': "आपकी बेहतर सहायता के लिए इस कॉल की निगरानी या रिकॉर्डिंग की जा सकती है।",
        'ar': "قد تتم مراقبة هذه المكالمة أو تسجيلها لخدمتك على نحو أفضل.",
    },
    'month': {'es': 'mes', 'fr': 'mois', 'de': 'Monat', 'pt': 'mês',
              'it': 'mese', 'ja': '月', 'zh': '月', 'hi': 'माह', 'ar': 'شهر'},
    'the Guardian — conditions, guidance, journal, habits and goals': {
        'es': 'el Guardián: afecciones, orientación, diario, hábitos y objetivos',
        'fr': 'le Gardien — pathologies, conseils, journal, habitudes et objectifs',
        'de': 'der Guardian — Beschwerden, Hinweise, Journal, Gewohnheiten und Ziele',
        'pt': 'o Guardião — condições, orientação, diário, hábitos e objetivos',
        'it': 'il Guardiano — condizioni, indicazioni, diario, abitudini e obiettivi',
        'ja': 'ガーディアン — 症状、ガイダンス、ジャーナル、習慣、目標',
        'zh': '守护者 — 状况、指导、日志、习惯与目标',
        'hi': 'गार्जियन — स्थितियाँ, मार्गदर्शन, जर्नल, आदतें और लक्ष्य',
        'ar': 'الحارس — الحالات والإرشاد واليوميات والعادات والأهداف'},
    'alarms, escalation, the medical ID and incident history — never withheld '
    'for non-payment': {
        'es': 'alarmas, escalado, la identificación médica y el historial de '
              'incidentes: nunca se retienen por falta de pago',
        'fr': "alarmes, escalade, l'identité médicale et l'historique des "
              'incidents — jamais retenus pour défaut de paiement',
        'de': 'Alarme, Eskalation, der medizinische Ausweis und die '
              'Vorfallhistorie — werden nie wegen Nichtzahlung vorenthalten',
        'pt': 'alarmes, escalonamento, a identificação médica e o histórico de '
              'incidentes — nunca retidos por falta de pagamento',
        'it': "allarmi, escalation, l'identificativo medico e lo storico degli "
              'incidenti — mai trattenuti per mancato pagamento',
        'ja': 'アラーム、エスカレーション、医療IDおよびインシデント履歴 — '
              '未払いを理由に止められることはありません',
        'zh': '警报、升级、医疗身份标识与事件历史 — 绝不会因未付款而被扣留',
        'hi': 'अलार्म, एस्केलेशन, मेडिकल आईडी और घटना इतिहास — भुगतान न होने पर '
              'कभी रोके नहीं जाते',
        'ar': 'التنبيهات والتصعيد والهوية الطبية وسجل الحوادث — لا تُحجب أبدًا '
              'بسبب عدم الدفع'},
    'paired wearables, the watch face, and lending the Guardian your '
    'microphone': {
        'es': 'dispositivos vinculados, la esfera del reloj y prestar el '
              'micrófono al Guardián',
        'fr': 'objets connectés appairés, le cadran de la montre et le prêt de '
              'votre microphone au Gardien',
        'de': 'gekoppelte Wearables, das Zifferblatt und das Verleihen Ihres '
              'Mikrofons an den Guardian',
        'pt': 'dispositivos emparelhados, o mostrador do relógio e emprestar o '
              'microfone ao Guardião',
        'it': "dispositivi indossabili accoppiati, il quadrante dell'orologio e "
              'il prestito del microfono al Guardiano',
        'ja': 'ペアリングしたウェアラブル、ウォッチフェイス、'
              'ガーディアンへのマイクの貸与',
        'zh': '已配对的可穿戴设备、表盘，以及把麦克风借给守护者',
        'hi': 'युग्मित पहनने योग्य उपकरण, वॉच फ़ेस, और गार्जियन को अपना माइक्रोफ़ोन देना',
        'ar': 'الأجهزة القابلة للارتداء المقترنة وواجهة الساعة وإعارة الميكروفون '
              'للحارس'},
    'early warning — the trend model that says something is about to go wrong '
    'before any threshold is crossed. Evaluating a sample you just submitted '
    'is not this, and is never withheld': {
        'es': 'aviso temprano: el modelo de tendencia que anuncia que algo va '
              'a ir mal antes de que se cruce cualquier umbral. Evaluar una '
              'muestra que acabas de enviar no es esto, y nunca se retiene',
        'fr': "alerte précoce — le modèle de tendance qui signale qu'un "
              'problème approche avant tout franchissement de seuil. Évaluer '
              "un échantillon que vous venez d'envoyer n'est pas cela, et "
              "n'est jamais retenu",
        'de': 'Frühwarnung — das Trendmodell, das meldet, dass etwas schiefgeht, '
              'bevor ein Schwellenwert überschritten ist. Die Auswertung einer '
              'gerade eingereichten Probe ist das nicht und wird nie '
              'vorenthalten',
        'pt': 'aviso precoce — o modelo de tendência que diz que algo vai '
              'correr mal antes de qualquer limiar ser ultrapassado. Avaliar '
              'uma amostra que acabou de enviar não é isto, e nunca é retido',
        'it': 'allerta precoce — il modello di tendenza che segnala che '
              'qualcosa sta per andare storto prima che una soglia venga '
              'superata. Valutare un campione appena inviato non è questo, e '
              'non viene mai trattenuto',
        'ja': '早期警告 — しきい値を超える前に異常の兆しを知らせる傾向モデル。'
              '送信したばかりのサンプルの評価はこれには当たらず、'
              '止められることはありません',
        'zh': '早期预警 — 在任何阈值被跨越之前就指出情况将要变糟的趋势模型。'
              '评估你刚提交的样本不属于此项，且绝不会被扣留',
        'hi': 'प्रारंभिक चेतावनी — वह प्रवृत्ति मॉडल जो किसी सीमा के पार होने से पहले '
              'बताता है कि कुछ बिगड़ने वाला है। अभी भेजे गए नमूने का मूल्यांकन '
              'यह नहीं है, और कभी रोका नहीं जाता',
        'ar': 'الإنذار المبكر — نموذج الاتجاه الذي ينبه إلى وقوع خلل قبل تجاوز '
              'أي عتبة. تقييم عينة أرسلتها للتو ليس هذا، ولا يُحجب أبدًا'},
    'specialists and the connected-apps marketplace': {
        'es': 'especialistas y el mercado de aplicaciones conectadas',
        'fr': 'spécialistes et la place de marché des applications connectées',
        'de': 'Spezialisten und der Marktplatz für verbundene Apps',
        'pt': 'especialistas e o mercado de aplicações ligadas',
        'it': 'specialisti e il marketplace delle app collegate',
        'ja': 'スペシャリストと連携アプリのマーケットプレイス',
        'zh': '专家与已连接应用的市场',
        'hi': 'विशेषज्ञ और कनेक्टेड-ऐप्स मार्केटप्लेस',
        'ar': 'المتخصصون وسوق التطبيقات المتصلة'},
    'summoning a QRME synthetic agent, and excursions': {
        'es': 'convocar un agente sintético de QRME, y las excursiones',
        'fr': 'convoquer un agent synthétique QRME, et les excursions',
        'de': 'einen synthetischen QRME-Agenten rufen und Ausflüge',
        'pt': 'convocar um agente sintético QRME, e as excursões',
        'it': 'convocare un agente sintetico QRME e le escursioni',
        'ja': 'QRMEの合成エージェントの召喚と外出',
        'zh': '召唤 QRME 合成代理，以及外出行程',
        'hi': 'QRME सिंथेटिक एजेंट को बुलाना, और भ्रमण',
        'ar': 'استدعاء وكيل QRME الاصطناعي والرحلات'},
}


def raised(exc: Exception):
    """The sentence an exception was raised with, in the shape it was raised.

    `str(exc)` looks equivalent and is not. `str()` on a `str` subclass returns
    a plain `str`, so a `Templated` carried by a domain exception and passed on
    as `HTTPException(403, str(exc))` reaches the handler having forgotten its
    template — English, silently, and indistinguishable from a sentence nobody
    has translated yet.

        asked     is the refusal translated
        mattered  did it still know how it was built when it got there

    QRME shipped that defect on its sealed-dialer sentence — the one somebody
    reads while something is going wrong — translated into nine languages and
    reaching none of them. Nothing here launders a template that way today, and
    `test_a_built_sentence_is_not_laundered_through_str` is what keeps it so.
    A route that refuses with a template uses this instead.
    """
    return exc.args[0] if exc.args else ""


def sentence_of(detail) -> str | None:
    """The part of a refusal a person is meant to read, whatever shape it has.

    `detail` is a string for most refusals, a dict for the plan gate, and a
    list of rows for a 422. Three shapes, and every client had to know which
    one it was looking at — which is why the plan gate reached three of the
    four as a bare status code.

        asked     does the sentence ride beside the structure
        mattered  does every structured refusal put it in the same place

    Returns `None` when there is nothing readable rather than inventing
    something: a bare status is more honest than a sentence this module made
    up.

    The 422's list is deliberately not handled here. Its sentence needs the
    reader's language and the field-name rules, which is `validation_message`'s
    job, and its handler passes the result in directly.
    """
    if isinstance(detail, str):
        return detail or None
    if isinstance(detail, dict):
        said = detail.get("message")
        return said if isinstance(said, str) and said else None
    return None


def refuse(request, status: int, content, headers: dict | None = None):
    """The one place a refusal becomes a response.

    Every exception handler in `jim/api.py` returns through here, so a domain
    that grows its own error class cannot also grow its own untranslated
    sentence.

    `headers` is carried rather than dropped: an `HTTPException` may set
    `WWW-Authenticate` or `Retry-After`, and a translation round is no reason
    for a 401 to stop saying how to authenticate.
    """
    from fastapi.responses import JSONResponse
    body = localize_detail(content, refusal_language(request))
    # One place the sentence is, whatever shape the structure has.
    #
    # The plan gate raises a dict whose `message` sits *inside* it, and the
    # handler wraps that as `{"detail": {...}}`. The three native shells look
    # for a top-level `message` and then for a string `detail`; a dict is
    # neither, so the one refusal that stands between somebody and a decision
    # to pay rendered as the status code alone — no price, no plan name.
    #
    #     asked     does the sentence ride beside the structure
    #     mattered  does every structured refusal put it in the same place
    #
    # Lifted here rather than at each raise site, for the reason this function
    # exists at all: a refusal shape added later cannot forget to do it.
    # `detail` is untouched — the console reads the dict to build the upgrade
    # card with its price and button.
    if isinstance(body, dict) and not isinstance(body.get("message"), str):
        said = sentence_of(body.get("detail"))
        if said is not None:
            body = {**body, "message": said}
    return JSONResponse(status_code=status, content=body, headers=headers)


#: The one sentence a person can meet on any route in this product,
#: because it is the answer to a route that failed. Named here so
#: `_REFUSALS` can carry it and the middleware can look it up — a
#: refusal built inline is a refusal in English.
SERVER_ERROR = ("Something went wrong on our side. "
                "Nothing you sent was recorded.")


#: Keyed on the English source, so editing the English falls back loudly to
#: the new English rather than quietly serving the old sentence in nine
#: languages. What is not here is recorded in
#: `jim/tests/refusals_untranslated.txt` and ratcheted.
#: What the attach bracket may say about a QRME profile it found, keyed the
#: way `guardian.standing` reports it.
#:
#: Keys on the wire and sentences here, for the reason the widget runner
#: keeps its refusals this way: the search results carry the key so each
#: client renders the caveat in its own table beside the row, while the
#: attach door raises the sentence and the ordinary refusal handler
#: translates it. One reading of a profile's standing, two renderings.
SPECIALIST_STANDING: dict[str, str] = {
    "specialist.departed":
        "that specialist has departed — their memorial remains on QRME, but "
        "they cannot stand behind a condition",
    "specialist.not_active":
        "that profile is not active on QRME, so it cannot stand behind a "
        "condition",
    "specialist.adults_only":
        "that specialist is age-restricted — it will answer for an adult "
        "and be stepped around for anybody else",
    "specialist.unreachable":
        "QRME could not be reached, so this profile's standing is unknown",
}

_REFUSALS: dict[str, dict[str, str]] = {
    # The phone line (jim/telephony.py, jim/auth.require_voice_adapter) — 3.0.8.
    'voice adapter token required': {
        'es': 'se requiere el token del adaptador de voz',
        'fr': "jeton de l'adaptateur vocal requis",
        'de': 'Token des Sprachadapters erforderlich',
        'pt': 'token do adaptador de voz obrigatório',
        'it': "token dell'adattatore vocale richiesto",
        'ja': '音声アダプターのトークンが必要です',
        'zh': '需要语音适配器令牌',
        'hi': 'वॉइस अडैप्टर टोकन आवश्यक है',
        'ar': 'رمز محوّل الصوت مطلوب',
    },
    'invalid voice adapter token': {
        'es': 'token del adaptador de voz no válido',
        'fr': "jeton de l'adaptateur vocal invalide",
        'de': 'ungültiges Token des Sprachadapters',
        'pt': 'token do adaptador de voz inválido',
        'it': "token dell'adattatore vocale non valido",
        'ja': '音声アダプターのトークンが無効です',
        'zh': '语音适配器令牌无效',
        'hi': 'वॉइस अडैप्टर टोकन अमान्य है',
        'ar': 'رمز محوّل الصوت غير صالح',
    },
    'this deployment is reachable beyond localhost but has no JIM_VOICE_SECRET configured — the reach-out call handlers stay closed until it is': {
        'es': 'este despliegue es accesible más allá de localhost pero no tiene JIM_VOICE_SECRET configurado — los manejadores de llamadas de contacto permanecen cerrados hasta que lo esté',
        'fr': "ce déploiement est joignable au-delà de localhost mais n'a pas de JIM_VOICE_SECRET configuré — les portes d'appel de contact restent fermées tant qu'il ne l'est pas",
        'de': 'diese Installation ist über localhost hinaus erreichbar, hat aber kein JIM_VOICE_SECRET gesetzt — die Anruf-Türen bleiben geschlossen, bis es gesetzt ist',
        'pt': 'esta instalação é alcançável além de localhost mas não tem JIM_VOICE_SECRET configurado — as portas das chamadas de contacto ficam fechadas até que esteja',
        'it': 'questa installazione è raggiungibile oltre localhost ma non ha JIM_VOICE_SECRET configurato — le porte delle chiamate ai contatti restano chiuse finché non lo è',
        'ja': 'このデプロイは localhost の外から到達できますが JIM_VOICE_SECRET が設定されていません — 設定されるまで連絡先通話の窓口は閉じたままです',
        'zh': '此部署可从 localhost 之外访问，但未配置 JIM_VOICE_SECRET — 在配置之前，联系人通话入口保持关闭',
        'hi': 'यह परिनियोजन localhost के बाहर से पहुँचा जा सकता है पर JIM_VOICE_SECRET सेट नहीं है — जब तक सेट न हो, संपर्क कॉल के द्वार बंद रहेंगे',
        'ar': 'هذا النشر يمكن الوصول إليه خارج localhost لكن لم يُضبط JIM_VOICE_SECRET — تبقى أبواب اتصال جهات الاتصال مغلقة حتى يُضبط',
    },
    'that is not an event the phone line reports': {
        'es': 'eso no es un evento que la línea telefónica reporte',
        'fr': "ce n'est pas un événement que la ligne téléphonique signale",
        'de': 'das ist kein Ereignis, das die Telefonleitung meldet',
        'pt': 'isso não é um evento que a linha telefónica reporte',
        'it': 'non è un evento che la linea telefonica riporti',
        'ja': 'それは電話回線が報告するイベントではありません',
        'zh': '这不是电话线路会报告的事件',
        'hi': 'यह ऐसी घटना नहीं जिसकी सूचना फ़ोन लाइन देती है',
        'ar': 'هذا ليس حدثًا يبلّغ عنه خط الهاتف',
    },
    "a line's then is not one of the four then words": {
        'es': 'el «then» de una línea no es una de las cuatro palabras «then»',
        'fr': "le « then » d'une ligne n'est pas l'un des quatre mots « then »",
        'de': 'das „then“ einer Zeile ist keines der vier „then“-Wörter',
        'pt': 'o «then» de uma linha não é uma das quatro palavras «then»',
        'it': 'il «then» di una riga non è una delle quattro parole «then»',
        'ja': '行の「then」は4つの「then」語のいずれでもありません',
        'zh': '该行的「then」不是四个「then」词之一',
        'hi': 'पंक्ति का «then» चार «then» शब्दों में से एक नहीं है',
        'ar': 'كلمة «then» في السطر ليست واحدة من كلمات «then» الأربع',
    },
    'no call answers to that reference': {
        'es': 'ninguna llamada responde a esa referencia',
        'fr': "aucun appel ne répond à cette référence",
        'de': 'kein Anruf antwortet auf diese Referenz',
        'pt': 'nenhuma chamada responde a essa referência',
        'it': 'nessuna chiamata risponde a quel riferimento',
        'ja': 'その参照に該当する通話はありません',
        'zh': '没有与该参考号对应的通话',
        'hi': 'उस संदर्भ से कोई कॉल मेल नहीं खाती',
        'ar': 'لا توجد مكالمة تطابق ذلك المرجع',
    },
    "the assistant's box is not available on this host": {
        'es': 'la caja del asistente no está disponible en este servidor',
        'fr': "la boîte de l'assistant n'est pas disponible sur cet hôte",
        'de': 'die Box des Assistenten ist auf diesem Host nicht verfügbar',
        'pt': 'a caixa do assistente não está disponível neste anfitrião',
        'it': "la scatola dell'assistente non è disponibile su questo host",
        'ja': 'このホストではアシスタントのボックスを利用できません',
        'zh': '此主机上无法使用助手的沙箱',
        'hi': 'इस होस्ट पर सहायक का बॉक्स उपलब्ध नहीं है',
        'ar': 'صندوق المساعد غير متاح على هذا المضيف',
    },
    'the draft is not a unified diff, so the box cannot try it': {
        'es': 'el borrador no es un diff unificado, así que la caja no puede probarlo',
        'fr': "le brouillon n'est pas un diff unifié, la boîte ne peut donc pas l'essayer",
        'de': 'der Entwurf ist kein Unified Diff, daher kann die Box ihn nicht ausprobieren',
        'pt': 'o rascunho não é um diff unificado, por isso a caixa não o pode experimentar',
        'it': 'la bozza non è un diff unificato, quindi la scatola non può provarla',
        'ja': '下書きが統一diff形式ではないため、ボックスで試せません',
        'zh': '草稿不是统一 diff 格式，沙箱无法试运行',
        'hi': 'मसौदा यूनिफ़ाइड diff नहीं है, इसलिए बॉक्स इसे आज़मा नहीं सकता',
        'ar': 'المسودة ليست diff موحّدًا، لذا لا يستطيع الصندوق تجربتها',
    },
    'the draft reaches outside the tree, so the box cannot try it': {
        'es': 'el borrador sale fuera del árbol, así que la caja no puede probarlo',
        'fr': "le brouillon sort de l'arborescence, la boîte ne peut donc pas l'essayer",
        'de': 'der Entwurf greift außerhalb des Baums, daher kann die Box ihn nicht ausprobieren',
        'pt': 'o rascunho sai da árvore, por isso a caixa não o pode experimentar',
        'it': "la bozza esce dall'albero, quindi la scatola non può provarla",
        'ja': '下書きがツリーの外に及ぶため、ボックスで試せません',
        'zh': '草稿触及目录树之外，沙箱无法试运行',
        'hi': 'मसौदा ट्री के बाहर पहुँचता है, इसलिए बॉक्स इसे आज़मा नहीं सकता',
        'ar': 'المسودة تتجاوز الشجرة، لذا لا يستطيع الصندوق تجربتها',
    },
    "the draft's hunk header cannot be read, so the box cannot try it": {
        'es': 'no se puede leer el encabezado de un fragmento del borrador, así que la caja no puede probarlo',
        'fr': "l'en-tête d'un bloc du brouillon est illisible, la boîte ne peut donc pas l'essayer",
        'de': 'die Hunk-Kopfzeile des Entwurfs ist nicht lesbar, daher kann die Box ihn nicht ausprobieren',
        'pt': 'o cabeçalho de um bloco do rascunho não se consegue ler, por isso a caixa não o pode experimentar',
        'it': "l'intestazione di un blocco della bozza non si legge, quindi la scatola non può provarla",
        'ja': '下書きのハンクヘッダーが読み取れないため、ボックスで試せません',
        'zh': '无法读取草稿的 hunk 头部，沙箱无法试运行',
        'hi': 'मसौदे का हंक हेडर पढ़ा नहीं जा सकता, इसलिए बॉक्स इसे आज़मा नहीं सकता',
        'ar': 'تعذّر قراءة ترويسة مقطع المسودة، لذا لا يستطيع الصندوق تجربتها',
    },
    'the draft does not fit the file it changes, so the box cannot try it': {
        'es': 'el borrador no encaja en el archivo que cambia, así que la caja no puede probarlo',
        'fr': "le brouillon ne correspond pas au fichier qu'il modifie, la boîte ne peut donc pas l'essayer",
        'de': 'der Entwurf passt nicht zu der Datei, die er ändert, daher kann die Box ihn nicht ausprobieren',
        'pt': 'o rascunho não encaixa no ficheiro que altera, por isso a caixa não o pode experimentar',
        'it': 'la bozza non combacia con il file che modifica, quindi la scatola non può provarla',
        'ja': '下書きが変更対象のファイルと合わないため、ボックスで試せません',
        'zh': '草稿与其修改的文件不匹配，沙箱无法试运行',
        'hi': 'मसौदा उस फ़ाइल से मेल नहीं खाता जिसे वह बदलता है, इसलिए बॉक्स इसे आज़मा नहीं सकता',
        'ar': 'المسودة لا تطابق الملف الذي تغيّره، لذا لا يستطيع الصندوق تجربتها',
    },
    'no such edit': {
        'es': 'no existe esa edición',
        'fr': "cette modification n'existe pas",
        'de': 'keine solche Änderung',
        'pt': 'essa edição não existe',
        'it': 'nessuna modifica del genere',
        'ja': 'その編集は存在しません',
        'zh': '没有这条编辑',
        'hi': 'ऐसा कोई संपादन नहीं',
        'ar': 'لا يوجد تعديل بهذا الاسم',
    },
    # The reach-out cascade (jim/reachout.py). JIM calling emergency
    # contacts one after another — these are the three ways that can be
    # asked to do something it cannot.
    'a reach-out needs at least one emergency contact': {
        'es': 'un aviso necesita al menos un contacto de emergencia',
        'fr': "un appel en cascade a besoin d'au moins un contact d'urgence",
        'de': 'ein Notruf-Durchlauf braucht mindestens einen Notfallkontakt',
        'pt': 'um alerta precisa de pelo menos um contacto de emergência',
        'it': 'un avviso richiede almeno un contatto di emergenza',
        'ja': '緊急連絡先が少なくとも一人必要です',
        'zh': '至少需要一位紧急联系人',
        'hi': 'कम से कम एक आपातकालीन संपर्क चाहिए',
        'ar': 'يلزم جهة اتصال طوارئ واحدة على الأقل',
    },
    'no such reach-out': {
        'es': 'no existe ese aviso',
        'fr': "cet appel en cascade n'existe pas",
        'de': 'diesen Notruf-Durchlauf gibt es nicht',
        'pt': 'esse alerta não existe',
        'it': 'questo avviso non esiste',
        'ja': 'その緊急連絡はありません',
        'zh': '没有这个求助流程',
        'hi': 'ऐसा कोई अलर्ट नहीं है',
        'ar': 'لا يوجد هذا الطلب',
    },
    'this call is not in a conversation': {
        'es': 'esta llamada no está en una conversación',
        'fr': "cet appel n'est pas dans une conversation",
        'de': 'dieser Anruf ist in keinem Gespräch',
        'pt': 'esta chamada não está numa conversa',
        'it': 'questa chiamata non è in una conversazione',
        'ja': 'この通話は会話中ではありません',
        'zh': '此通话不在对话中',
        'hi': 'यह कॉल किसी बातचीत में नहीं है',
        'ar': 'هذه المكالمة ليست في محادثة',
    },
    # The moderated mailbox. Every send is held for a person, and these are
    # what it says when a request cannot stand — the address that is missing,
    # the draft that is not there, the moderation word it did not understand.
    'an inbound email needs a sender address': {
        'es': 'un correo entrante necesita una dirección de remitente',
        'fr': "un e-mail entrant a besoin d'une adresse d'expéditeur",
        'de': 'eine eingehende E-Mail braucht eine Absenderadresse',
        'pt': 'um e-mail recebido precisa de um endereço de remetente',
        'it': "un'email in arrivo ha bisogno di un indirizzo mittente",
        'ja': '受信メールには送信元アドレスが必要です',
        'zh': '收到的邮件需要一个发件人地址',
        'hi': 'आने वाले ईमेल के लिए प्रेषक का पता चाहिए',
        'ar': 'البريد الوارد يحتاج إلى عنوان مُرسِل',
    },
    'an inbound email needs a body': {
        'es': 'un correo entrante necesita un cuerpo',
        'fr': "un e-mail entrant a besoin d'un contenu",
        'de': 'eine eingehende E-Mail braucht einen Textinhalt',
        'pt': 'um e-mail recebido precisa de um corpo',
        'it': "un'email in arrivo ha bisogno di un testo",
        'ja': '受信メールには本文が必要です',
        'zh': '收到的邮件需要正文',
        'hi': 'आने वाले ईमेल के लिए मुख्य पाठ चाहिए',
        'ar': 'البريد الوارد يحتاج إلى نص',
    },
    'an outbound email needs a recipient address': {
        'es': 'un correo saliente necesita una dirección de destinatario',
        'fr': "un e-mail sortant a besoin d'une adresse de destinataire",
        'de': 'eine ausgehende E-Mail braucht eine Empfängeradresse',
        'pt': 'um e-mail a enviar precisa de um endereço de destinatário',
        'it': "un'email in uscita ha bisogno di un indirizzo destinatario",
        'ja': '送信メールには宛先アドレスが必要です',
        'zh': '发出的邮件需要一个收件人地址',
        'hi': 'भेजे जाने वाले ईमेल के लिए प्राप्तकर्ता का पता चाहिए',
        'ar': 'البريد الصادر يحتاج إلى عنوان مُستلِم',
    },
    'no such mail thread': {
        'es': 'no existe ese hilo de correo',
        'fr': "ce fil d'e-mail n'existe pas",
        'de': 'diesen E-Mail-Verlauf gibt es nicht',
        'pt': 'esse tópico de correio não existe',
        'it': 'questo thread di posta non esiste',
        'ja': 'そのメールスレッドはありません',
        'zh': '没有这个邮件会话',
        'hi': 'ऐसा कोई मेल थ्रेड नहीं है',
        'ar': 'لا يوجد هذا المسار البريدي',
    },
    'no such mail message': {
        'es': 'no existe ese mensaje de correo',
        'fr': "ce message d'e-mail n'existe pas",
        'de': 'diese E-Mail-Nachricht gibt es nicht',
        'pt': 'essa mensagem de correio não existe',
        'it': 'questo messaggio di posta non esiste',
        'ja': 'そのメールメッセージはありません',
        'zh': '没有这封邮件',
        'hi': 'ऐसा कोई मेल संदेश नहीं है',
        'ar': 'لا توجد هذه الرسالة البريدية',
    },
    'this message is not a draft awaiting moderation': {
        'es': 'este mensaje no es un borrador pendiente de moderación',
        'fr': "ce message n'est pas un brouillon en attente de modération",
        'de': 'diese Nachricht ist kein Entwurf, der auf Freigabe wartet',
        'pt': 'esta mensagem não é um rascunho à espera de moderação',
        'it': 'questo messaggio non è una bozza in attesa di moderazione',
        'ja': 'このメッセージは承認待ちの下書きではありません',
        'zh': '此消息不是等待审核的草稿',
        'hi': 'यह संदेश मॉडरेशन की प्रतीक्षा में मसौदा नहीं है',
        'ar': 'هذه الرسالة ليست مسودة بانتظار المراجعة',
    },
    'an edited reply needs a body': {
        'es': 'una respuesta editada necesita un cuerpo',
        'fr': "une réponse modifiée a besoin d'un contenu",
        'de': 'eine bearbeitete Antwort braucht einen Textinhalt',
        'pt': 'uma resposta editada precisa de um corpo',
        'it': 'una risposta modificata ha bisogno di un testo',
        'ja': '編集した返信には本文が必要です',
        'zh': '编辑后的回复需要正文',
        'hi': 'संपादित उत्तर के लिए मुख्य पाठ चाहिए',
        'ar': 'الرد المُعدَّل يحتاج إلى نص',
    },
    # The model menu by region, and app edits held at apply.
    'that is not a region this product offers a menu for': {
        'es': 'esa no es una región para la que este producto ofrezca un menú',
        'fr': "ce n'est pas une région pour laquelle ce produit propose un menu",
        'de': 'für diese Region bietet dieses Produkt kein Menü an',
        'pt': 'essa não é uma região para a qual este produto ofereça um menu',
        'it': 'questa non è una regione per cui questo prodotto offra un menu',
        'ja': 'この製品がメニューを提供している地域ではありません',
        'zh': '本产品未为该地区提供菜单',
        'hi': 'यह ऐसा क्षेत्र नहीं है जिसके लिए यह उत्पाद मेन्यू देता हो',
        'ar': 'هذه ليست منطقة يقدّم لها هذا المنتج قائمة',
    },
    'the tests ran longer than the box allows': {
        'es': 'las pruebas tardaron más de lo que la caja permite',
        'fr': 'les tests ont duré plus longtemps que la boîte ne le permet',
        'de': 'die Tests liefen länger, als die Box erlaubt',
        'pt': 'os testes demoraram mais do que a caixa permite',
        'it': 'i test hanno impiegato più di quanto la scatola consenta',
        'ja': 'テストがボックスの許容時間を超えました',
        'zh': '测试运行时间超过了盒子的允许范围',
        'hi': 'परीक्षण बॉक्स की अनुमति से अधिक देर चले',
        'ar': 'طالت الاختبارات أكثر مما يسمح به الصندوق',
    },
    'the named tests collected nothing, so nothing was tried': {
        'es': 'las pruebas indicadas no recogieron nada, así que no se probó nada',
        'fr': "les tests nommés n'ont rien collecté, donc rien n'a été essayé",
        'de': 'die genannten Tests haben nichts gesammelt, also wurde nichts ausprobiert',
        'pt': 'os testes indicados não recolheram nada, por isso nada foi experimentado',
        'it': 'i test indicati non hanno raccolto nulla, quindi nulla è stato provato',
        'ja': '指定されたテストは何も収集しなかったため、何も試されませんでした',
        'zh': '指定的测试没有收集到任何内容，因此什么也没有试',
        'hi': 'नामित परीक्षणों ने कुछ नहीं जुटाया, इसलिए कुछ आज़माया नहीं गया',
        'ar': 'لم تجمع الاختبارات المسماة شيئًا، لذا لم يُجرَّب شيء',
    },
    'this app edit is already decided': {
        'es': 'esta edición de la app ya está decidida',
        'fr': "cette modification de l'app est déjà décidée",
        'de': 'diese App-Änderung ist bereits entschieden',
        'pt': 'esta edição da app já está decidida',
        'it': "questa modifica dell'app è già decisa",
        'ja': 'このアプリ編集はすでに決定済みです',
        'zh': '这个应用编辑已经决定',
        'hi': 'यह ऐप संपादन पहले ही तय हो चुका है',
        'ar': 'تم البتّ في هذا التعديل على التطبيق بالفعل',
    },
    'this app edit was decided while the box was running': {
        'es': 'esta edición de la app se decidió mientras la caja estaba en marcha',
        'fr': "cette modification de l'app a été décidée pendant que la boîte tournait",
        'de': 'diese App-Änderung wurde entschieden, während die Box lief',
        'pt': 'esta edição da app foi decidida enquanto a caixa corria',
        'it': "questa modifica dell'app è stata decisa mentre la scatola era in esecuzione",
        'ja': 'ボックスの実行中にこのアプリ編集が決定されました',
        'zh': '盒子运行期间这个应用编辑已被决定',
        'hi': 'बॉक्स चलते समय यह ऐप संपादन तय कर दिया गया',
        'ar': 'تم البتّ في هذا التعديل على التطبيق أثناء عمل الصندوق',
    },
    'that edit is already in the box': {
        'es': 'esa edición ya está en la caja',
        'fr': 'cette modification est déjà dans la boîte',
        'de': 'diese Änderung ist bereits in der Box',
        'pt': 'essa edição já está na caixa',
        'it': 'quella modifica è già nella scatola',
        'ja': 'その編集はすでにボックスの中です',
        'zh': '该编辑已经在盒子里',
        'hi': 'वह संपादन पहले से बॉक्स में है',
        'ar': 'ذلك التعديل موجود في الصندوق بالفعل',
    },
    "the assistant's box is busy, so try again in a moment": {
        'es': 'la caja del asistente está ocupada; inténtalo de nuevo en un momento',
        'fr': "la boîte de l'assistant est occupée ; réessayez dans un instant",
        'de': 'die Box des Assistenten ist beschäftigt, versuche es gleich noch einmal',
        'pt': 'a caixa do assistente está ocupada, tenta de novo daqui a pouco',
        'it': "la scatola dell'assistente è occupata, riprova tra un momento",
        'ja': 'アシスタントのボックスは使用中です。少し待ってからもう一度お試しください',
        'zh': '助手的盒子正忙，请稍后再试',
        'hi': 'सहायक का बॉक्स व्यस्त है, थोड़ी देर में फिर कोशिश करें',
        'ar': 'صندوق المساعد مشغول، فحاول مجددًا بعد لحظة',
    },
    'no such app edit': {
        'es': 'no existe esa edición de la app',
        'fr': "cette modification de l'app n'existe pas",
        'de': 'diese App-Änderung gibt es nicht',
        'pt': 'essa edição da app não existe',
        'it': "questa modifica dell'app non esiste",
        'ja': 'そのアプリ編集はありません',
        'zh': '没有这个应用编辑',
        'hi': 'ऐसा कोई ऐप संपादन नहीं है',
        'ar': 'لا يوجد هذا التعديل على التطبيق',
    },
    'an app edit needs a title': {
        'es': 'una edición de la app necesita un título',
        'fr': "une modification de l'app a besoin d'un titre",
        'de': 'eine App-Änderung braucht einen Titel',
        'pt': 'uma edição da app precisa de um título',
        'it': "una modifica dell'app ha bisogno di un titolo",
        'ja': 'アプリ編集にはタイトルが必要です',
        'zh': '应用编辑需要一个标题',
        'hi': 'ऐप संपादन के लिए शीर्षक चाहिए',
        'ar': 'تعديل التطبيق يحتاج إلى عنوان',
    },
    'an app edit needs a description of the change': {
        'es': 'una edición de la app necesita una descripción del cambio',
        'fr': "une modification de l'app a besoin d'une description du changement",
        'de': 'eine App-Änderung braucht eine Beschreibung der Änderung',
        'pt': 'uma edição da app precisa de uma descrição da alteração',
        'it': "una modifica dell'app ha bisogno di una descrizione del cambiamento",
        'ja': 'アプリ編集には変更内容の説明が必要です',
        'zh': '应用编辑需要对改动的描述',
        'hi': 'ऐप संपादन के लिए बदलाव का विवरण चाहिए',
        'ar': 'تعديل التطبيق يحتاج إلى وصف للتغيير',
    },
    'the assistant needs an instruction to draft from': {
        'es': 'el asistente necesita una instrucción para redactar',
        'fr': "l'assistant a besoin d'une instruction pour rédiger",
        'de': 'der Assistent braucht eine Anweisung, aus der er entwerfen kann',
        'pt': 'o assistente precisa de uma instrução para redigir',
        'it': "l'assistente ha bisogno di un'istruzione da cui partire",
        'ja': 'アシスタントには下書きの元になる指示が必要です',
        'zh': '助手需要一条指令才能起草',
        'hi': 'सहायक को मसौदा बनाने के लिए निर्देश चाहिए',
        'ar': 'يحتاج المساعد إلى تعليمات ليصوغ منها',
    },
    'that model is not on the menu for your region': {
        'es': 'ese modelo no está en el menú de tu región',
        'fr': "ce modèle n'est pas au menu de votre région",
        'de': 'dieses Modell steht in deiner Region nicht im Menü',
        'pt': 'esse modelo não está no menu da tua região',
        'it': 'quel modello non è nel menu della tua regione',
        'ja': 'そのモデルはお住まいの地域のメニューにありません',
        'zh': '该模型不在你所在地区的菜单中',
        'hi': 'वह मॉडल आपके क्षेत्र के मेन्यू में नहीं है',
        'ar': 'هذا النموذج ليس في قائمة منطقتك',
    },
    'this app edit is not awaiting a decision': {
        'es': 'esta edición de la app no está pendiente de decisión',
        'fr': "cette modification de l'app n'attend pas de décision",
        'de': 'diese App-Änderung wartet auf keine Entscheidung',
        'pt': 'esta edição da app não está à espera de decisão',
        'it': "questa modifica dell'app non è in attesa di decisione",
        'ja': 'このアプリ編集は判断待ちではありません',
        'zh': '此应用编辑并未等待决定',
        'hi': 'यह ऐप संपादन निर्णय की प्रतीक्षा में नहीं है',
        'ar': 'هذا التعديل على التطبيق لا ينتظر قرارًا',
    },
    'a decision on an app edit is approve or reject': {
        'es': 'una decisión sobre una edición de la app es aprobar o rechazar',
        'fr': "une décision sur une modification de l'app est approuver ou rejeter",
        'de': 'eine Entscheidung über eine App-Änderung ist freigeben oder ablehnen',
        'pt': 'uma decisão sobre uma edição da app é aprovar ou rejeitar',
        'it': "una decisione su una modifica dell'app è approvare o rifiutare",
        'ja': 'アプリ編集の判断は承認か却下のいずれかです',
        'zh': '对应用编辑的决定为批准或拒绝',
        'hi': 'ऐप संपादन पर निर्णय स्वीकृत या अस्वीकृत है',
        'ar': 'القرار بشأن تعديل التطبيق هو الموافقة أو الرفض',
    },
    'a moderation action is approve, edit, or discard': {
        'es': 'una acción de moderación es aprobar, editar o descartar',
        'fr': "une action de modération est approuver, modifier ou rejeter",
        'de': 'eine Moderationsaktion ist freigeben, bearbeiten oder verwerfen',
        'pt': 'uma ação de moderação é aprovar, editar ou descartar',
        'it': 'un\'azione di moderazione è approvare, modificare o scartare',
        'ja': 'モデレーション操作は承認・編集・破棄のいずれかです',
        'zh': '审核操作为批准、编辑或丢弃',
        'hi': 'मॉडरेशन क्रिया है स्वीकृत करें, संपादित करें, या हटाएँ',
        'ar': 'إجراء المراجعة هو الموافقة أو التعديل أو التجاهل',
    },
    # The hands. Carried from the sibling word for word — a refusal a
    # person meets on one console and then on the other has to say the
    # same thing in their own language.
    'no such reach': {
        'es': 'no existe esa sesión de control',
        'fr': "cette prise en main n'existe pas",
        'de': 'diesen Zugriff gibt es nicht',
        'pt': 'essa sessão de controlo não existe',
        'it': 'questa sessione di controllo non esiste',
        'ja': 'その操作セッションはありません',
        'zh': '没有这个操作会话',
        'hi': 'ऐसा कोई नियंत्रण सत्र नहीं है',
        'ar': 'لا توجد هذه الجلسة',
    },
    # -- the coach's eye (jim/api.py, coach_reply). A shown picture that
    # cannot be read is refused out loud — a coach that quietly ignores
    # what it was shown is agreeing to a lie.
    ("the eyes read JPEG, PNG and WebP pictures — this file "
     "is none of them"): {
        'es': "los ojos leen imágenes JPEG, PNG y WebP — este archivo no es ninguna de ellas",
        'fr': "les yeux lisent les images JPEG, PNG et WebP — ce fichier n'en est aucune",
        'de': "die Augen lesen JPEG-, PNG- und WebP-Bilder — diese Datei ist keines davon",
        'pt': "os olhos leem imagens JPEG, PNG e WebP — este arquivo não é nenhuma delas",
        'it': "gli occhi leggono immagini JPEG, PNG e WebP — questo file non è nessuna di esse",
        'ja': "目が読めるのは JPEG・PNG・WebP の画像です。このファイルはどれでもありません",
        'zh': "眼睛能读取 JPEG、PNG 和 WebP 图片——这个文件都不是",
        'hi': "आँखें JPEG, PNG और WebP चित्र पढ़ती हैं — यह फ़ाइल इनमें से कोई नहीं है",
        'ar': "العيون تقرأ صور JPEG وPNG وWebP — هذا الملف ليس أيًا منها",
    },
    ("the shown picture is not valid base64"): {
        'es': "la imagen mostrada no es base64 válido",
        'fr': "l'image montrée n'est pas du base64 valide",
        'de': "das gezeigte Bild ist kein gültiges Base64",
        'pt': "a imagem mostrada não é base64 válido",
        'it': "l'immagine mostrata non è base64 valido",
        'ja': "見せられた画像は有効な base64 ではありません",
        'zh': "所展示的图片不是有效的 base64",
        'hi': "दिखाई गई तस्वीर मान्य base64 नहीं है",
        'ar': "الصورة المعروضة ليست base64 صالحًا",
    },
    # -- the meeting-recording door (jim/api.py, stretch_heard). Both
    # sentences reached the wire with the door; a sentence on the wire is
    # a sentence somebody reads.
    ("the recording arrived empty"): {
        'es': "la grabación llegó vacía",
        'fr': "l'enregistrement est arrivé vide",
        'de': "die Aufnahme kam leer an",
        'pt': "a gravação chegou vazia",
        'it': "la registrazione è arrivata vuota",
        'ja': "録音が空のまま届きました",
        'zh': "收到的录音是空的",
        'hi': "रिकॉर्डिंग खाली पहुंची",
        'ar': "وصل التسجيل فارغًا",
    },
    # -- the synced book's two vault sentences (jim/contacts.py). They
    # reached the wire when the doors opened, and a sentence on the wire is
    # a sentence somebody reads.
    ("this book is sealed into the vault and no vault was supplied"): {
        'es': "esta libreta está sellada en la bóveda y no se proporcionó ninguna bóveda",
        'fr': "ce carnet est scellé dans le coffre et aucun coffre n'a été fourni",
        'de': "dieses Buch ist im Tresor versiegelt und kein Tresor wurde bereitgestellt",
        'pt': "esta lista está selada no cofre e nenhum cofre foi fornecido",
        'it': "questa rubrica è sigillata nel caveau e nessun caveau è stato fornito",
        'ja': "この連絡帳は保管庫に封印されていますが、保管庫が渡されていません",
        'zh': "这本通讯录封存在保管库中，但没有提供保管库",
        'hi': "यह सूची तिजोरी में सील है और कोई तिजोरी नहीं दी गई",
        'ar': "هذا الدفتر مختوم في الخزانة ولم تُقدَّم أي خزانة",
    },
    ("the sealed book is not in the vault"): {
        'es': "la libreta sellada no está en la bóveda",
        'fr': "le carnet scellé n'est pas dans le coffre",
        'de': "das versiegelte Buch ist nicht im Tresor",
        'pt': "a lista selada não está no cofre",
        'it': "la rubrica sigillata non è nel caveau",
        'ja': "封印された連絡帳が保管庫にありません",
        'zh': "封存的通讯录不在保管库中",
        'hi': "सील की गई सूची तिजोरी में नहीं है",
        'ar': "الدفتر المختوم ليس في الخزانة",
    },
    'a meal needs a note or a photo — there is nothing to log in an empty plate': {
        'es': 'una comida necesita una nota o una foto: no hay nada que registrar en un plato vacío',
        'fr': "un repas a besoin d'une note ou d'une photo — il n'y a rien à consigner dans une assiette vide",
        'de': 'eine Mahlzeit braucht eine Notiz oder ein Foto — an einem leeren Teller gibt es nichts festzuhalten',
        'pt': 'uma refeição precisa de uma nota ou de uma foto — não há nada a registar num prato vazio',
        'it': "un pasto ha bisogno di una nota o di una foto — in un piatto vuoto non c'è nulla da registrare",
        'ja': '食事にはメモか写真が必要です — 空のお皿には記録するものがありません',
        'zh': '记录一餐需要一段备注或一张照片 — 空盘子里没有什么可记的',
        'hi': 'भोजन के लिए एक नोट या तस्वीर चाहिए — ख़ाली थाली में दर्ज करने को कुछ नहीं है',
        'ar': 'تحتاج الوجبة إلى ملاحظة أو صورة — لا شيء يُسجَّل في طبق فارغ',
    },
    'a meal photo needs the vault the clinical captures use — this deployment has none configured, so log the meal by note alone': {
        'es': 'una foto de comida necesita la misma bóveda que usan las capturas clínicas: esta instalación no tiene ninguna configurada, así que registra la comida solo con una nota',
        'fr': "une photo de repas a besoin du coffre qu'utilisent les captures cliniques — ce déploiement n'en a aucun de configuré, consigne donc le repas par une note seule",
        'de': 'ein Mahlzeitenfoto braucht denselben Tresor wie die klinischen Aufnahmen — diese Installation hat keinen eingerichtet, halte die Mahlzeit also nur mit einer Notiz fest',
        'pt': 'uma foto de refeição precisa do cofre que as capturas clínicas usam — esta instalação não tem nenhum configurado, por isso regista a refeição apenas com uma nota',
        'it': 'una foto del pasto ha bisogno della cassaforte che usano le acquisizioni cliniche — questa installazione non ne ha, quindi registra il pasto con la sola nota',
        'ja': '食事の写真には臨床の取り込みと同じ保管庫が必要です — この導入には設定がないため、メモだけで記録してください',
        'zh': '记录餐食照片需要临床采集所用的保险库 — 此部署未配置，请仅用备注记录这一餐',
        'hi': 'भोजन की तस्वीर के लिए वही वॉल्ट चाहिए जो क्लिनिकल कैप्चर इस्तेमाल करते हैं — इस परिनियोजन में कोई नहीं है, इसलिए भोजन सिर्फ़ नोट से दर्ज करो',
        'ar': 'تحتاج صورة الوجبة إلى الخزنة التي تستخدمها الالتقاطات السريرية — لا خزنة مُهيّأة في هذا النشر، فسجّل الوجبة بملاحظة فقط',
    },
    "a pane with no faces is the helper button on its own — set the state to 'handle' instead": {
        'es': "un panel sin caras es solo el botón de ayuda: pon el estado en 'handle' en su lugar",
        'fr': "un volet sans visages n'est que le bouton d'aide — mets plutôt l'état sur 'handle'",
        'de': "eine Fläche ohne Gesichter ist nur die Hilfe-Schaltfläche — setze den Zustand stattdessen auf 'handle'",
        'pt': "um painel sem rostos é só o botão de ajuda — define o estado como 'handle' em vez disso",
        'it': "un pannello senza volti è solo il pulsante di aiuto — imposta invece lo stato su 'handle'",
        'ja': "顔のないペインは補助ボタンだけの状態です — 代わりに state を 'handle' にしてください",
        'zh': "没有头像的面板就只剩助手按钮 — 请改将状态设为 'handle'",
        'hi': "बिना चेहरों वाला पैनल सिर्फ़ हेल्पर बटन रह जाता है — इसके बजाय स्टेट 'handle' कर दो",
        'ar': "اللوحة بلا وجوه ليست إلا زرّ المساعدة وحده — اضبط الحالة على 'handle' بدلًا من ذلك",
    },
    'an appointment needs a title you will recognise': {
        'es': 'una cita necesita un título que vayas a reconocer',
        'fr': "un rendez-vous a besoin d'un titre que tu reconnaîtras",
        'de': 'ein Termin braucht einen Titel, den du wiedererkennst',
        'pt': 'uma marcação precisa de um título que vais reconhecer',
        'it': 'un appuntamento ha bisogno di un titolo che riconoscerai',
        'ja': '予定には、あとで自分がわかる名前が必要です',
        'zh': '日程需要一个你日后能认出来的标题',
        'hi': 'अपॉइंटमेंट को ऐसा शीर्षक चाहिए जिसे तुम पहचान सको',
        'ar': 'يحتاج الموعد إلى عنوان تتعرّف عليه',
    },
    'no such appointment': {
        'es': 'no existe esa cita',
        'fr': 'aucun rendez-vous de ce type',
        'de': 'einen solchen Termin gibt es nicht',
        'pt': 'não existe essa marcação',
        'it': 'nessun appuntamento del genere',
        'ja': 'そのような予定はありません',
        'zh': '没有这个日程',
        'hi': 'ऐसा कोई अपॉइंटमेंट नहीं है',
        'ar': 'لا يوجد موعد بهذا الوصف',
    },
    "that appointment is somebody else's": {
        'es': 'esa cita es de otra persona',
        'fr': "ce rendez-vous appartient à quelqu'un d'autre",
        'de': 'dieser Termin gehört jemand anderem',
        'pt': 'essa marcação é de outra pessoa',
        'it': "quell'appuntamento è di un'altra persona",
        'ja': 'その予定は別の人のものです',
        'zh': '该日程属于其他人',
        'hi': 'वह अपॉइंटमेंट किसी और का है',
        'ar': 'هذا الموعد يخصّ شخصًا آخر',
    },
    'that time has already passed': {
        'es': 'esa hora ya pasó',
        'fr': 'cette heure est déjà passée',
        'de': 'dieser Zeitpunkt ist schon vorbei',
        'pt': 'essa hora já passou',
        'it': "quell'ora è già passata",
        'ja': 'その時刻はもう過ぎています',
        'zh': '那个时间已经过去了',
        'hi': 'वह समय बीत चुका है',
        'ar': 'لقد مضى ذلك الوقت',
    },
    'an empty answer drills nothing — say it out loud, then write what you said': {
        'es': 'una respuesta vacía no ejercita nada: dilo en voz alta y luego escribe lo que dijiste',
        'fr': "une réponse vide n'entraîne rien — dis-le à voix haute, puis écris ce que tu as dit",
        'de': 'eine leere Antwort übt nichts — sag es laut und schreib dann auf, was du gesagt hast',
        'pt': 'uma resposta vazia não treina nada — di-lo em voz alta e depois escreve o que disseste',
        'it': 'una risposta vuota non allena nulla — dillo ad alta voce, poi scrivi quello che hai detto',
        'ja': '空の答えでは練習になりません — 声に出して言ってから、言ったことを書いてください',
        'zh': '空白的回答起不到练习作用 — 先说出声，再把说的写下来',
        'hi': 'ख़ाली जवाब से कोई अभ्यास नहीं होता — पहले बोलकर कहो, फिर जो कहा वह लिखो',
        'ar': 'الإجابة الفارغة لا تُدرّب على شيء — قلها بصوتك، ثم اكتب ما قلته',
    },
    'no such drill': {
        'es': 'no existe ese ejercicio',
        'fr': 'aucun exercice de ce type',
        'de': 'eine solche Übung gibt es nicht',
        'pt': 'não existe esse exercício',
        'it': 'nessuna esercitazione del genere',
        'ja': 'そのような練習はありません',
        'zh': '没有这个练习',
        'hi': 'ऐसा कोई अभ्यास नहीं है',
        'ar': 'لا يوجد تمرين بهذا الوصف',
    },
    'this drill is already answered — deal another question': {
        'es': 'este ejercicio ya está respondido: reparte otra pregunta',
        'fr': 'cet exercice a déjà une réponse — distribue une autre question',
        'de': 'diese Übung ist schon beantwortet — gib eine andere Frage aus',
        'pt': 'este exercício já está respondido — dá outra pergunta',
        'it': "questa esercitazione ha già una risposta — pesca un'altra domanda",
        'ja': 'この練習にはすでに答えがあります — 別の問題を配ってください',
        'zh': '这个练习已经答过了 — 请再发一道题',
        'hi': 'इस अभ्यास का जवाब पहले ही दिया जा चुका है — दूसरा सवाल निकालो',
        'ar': 'هذا التمرين مُجاب عليه بالفعل — وزّع سؤالًا آخر',
    },
    'an empty drop holds no statement': {
        'es': 'un envío vacío no contiene ninguna declaración',
        'fr': 'un dépôt vide ne contient aucune déclaration',
        'de': 'eine leere Ablage enthält keine Aussage',
        'pt': 'uma entrega vazia não contém qualquer declaração',
        'it': 'un deposito vuoto non contiene alcuna dichiarazione',
        'ja': '空の投函には、何の申し立ても入っていません',
        'zh': '空的投递里没有任何陈述',
        'hi': 'ख़ाली ड्रॉप में कोई कथन नहीं होता',
        'ar': 'الإيداع الفارغ لا يحمل أي إفادة',
    },
    'that would be a note to yourself; the journal is better at those': {
        'es': 'eso sería una nota para ti; el diario es mejor para eso',
        'fr': 'ce serait une note pour toi-même ; le journal est meilleur pour ça',
        'de': 'das wäre eine Notiz an dich selbst; dafür ist das Journal besser',
        'pt': 'isso seria uma nota para ti; o diário é melhor para essas',
        'it': 'sarebbe una nota per te stesso; il diario è più adatto',
        'ja': 'それは自分あてのメモになります。そういうものはジャーナルのほうが得意です',
        'zh': '那更像是写给自己的便条；这类内容更适合放在日志里',
        'hi': 'वह ख़ुद के लिए एक नोट होगा; ऐसी चीज़ों के लिए जर्नल बेहतर है',
        'ar': 'ستكون تلك ملاحظة لنفسك؛ اليوميات أنسب لمثلها',
    },
    'nothing was logged this week — a letter about an empty week would have to invent its contents': {
        'es': 'esta semana no se registró nada: una carta sobre una semana vacía tendría que inventarse su contenido',
        'fr': "rien n'a été consigné cette semaine — une lettre sur une semaine vide devrait en inventer le contenu",
        'de': 'diese Woche wurde nichts festgehalten — ein Brief über eine leere Woche müsste sich seinen Inhalt ausdenken',
        'pt': 'nada foi registado esta semana — uma carta sobre uma semana vazia teria de inventar o seu conteúdo',
        'it': 'questa settimana non è stato registrato nulla — una lettera su una settimana vuota dovrebbe inventarsi il contenuto',
        'ja': '今週は何も記録されていません — 空の一週間についての手紙は、中身を作り話にするしかありません',
        'zh': '这一周没有任何记录 — 关于空白一周的信，只能凭空编造内容',
        'hi': 'इस हफ़्ते कुछ भी दर्ज नहीं हुआ — ख़ाली हफ़्ते पर लिखे ख़त को अपनी सामग्री गढ़नी पड़ती',
        'ar': 'لم يُسجَّل شيء هذا الأسبوع — رسالة عن أسبوع فارغ سيكون عليها أن تختلق محتواها',
    },
    'no such capture': {
        'es': 'no existe esa captura',
        'fr': 'aucune capture de ce type',
        'de': 'eine solche Aufnahme gibt es nicht',
        'pt': 'não existe essa captura',
        'it': 'nessuna acquisizione del genere',
        'ja': 'そのような取り込みはありません',
        'zh': '没有这次采集',
        'hi': 'ऐसा कोई कैप्चर नहीं है',
        'ar': 'لا يوجد التقاط بهذا الوصف',
    },
    'the capture could not be read — it is not base64': {
        'es': 'no se pudo leer la captura: no es base64',
        'fr': "la capture n'a pas pu être lue — ce n'est pas du base64",
        'de': 'die Aufnahme konnte nicht gelesen werden — sie ist kein Base64',
        'pt': 'não foi possível ler a captura — não é base64',
        'it': "non è stato possibile leggere l'acquisizione — non è base64",
        'ja': '取り込んだ内容を読み取れませんでした — base64 ではありません',
        'zh': '无法读取这次采集 — 它不是 base64',
        'hi': 'कैप्चर पढ़ा नहीं जा सका — यह base64 नहीं है',
        'ar': 'تعذّرت قراءة الالتقاط — إنه ليس base64',
    },
    'the photo could not be read — it is not base64': {
        'es': 'no se pudo leer la foto: no es base64',
        'fr': "la photo n'a pas pu être lue — ce n'est pas du base64",
        'de': 'das Foto konnte nicht gelesen werden — es ist kein Base64',
        'pt': 'não foi possível ler a foto — não é base64',
        'it': 'non è stato possibile leggere la foto — non è base64',
        'ja': '写真を読み取れませんでした — base64 ではありません',
        'zh': '无法读取这张照片 — 它不是 base64',
        'hi': 'तस्वीर पढ़ी नहीं जा सकी — यह base64 नहीं है',
        'ar': 'تعذّرت قراءة الصورة — إنها ليست base64',
    },
    'the statement could not be read — it is not base64': {
        'es': 'no se pudo leer el extracto: no es base64',
        'fr': "le relevé n'a pas pu être lu — ce n'est pas du base64",
        'de': 'der Auszug konnte nicht gelesen werden — er ist kein Base64',
        'pt': 'não foi possível ler o extracto — não é base64',
        'it': "non è stato possibile leggere l'estratto — non è base64",
        'ja': '明細を読み取れませんでした — base64 ではありません',
        'zh': '无法读取该对账单 — 它不是 base64',
        'hi': 'स्टेटमेंट पढ़ा नहीं जा सका — यह base64 नहीं है',
        'ar': 'تعذّرت قراءة الكشف — إنه ليس base64',
    },
    'the image lives in the vault and no vault is configured on this deployment': {
        'es': 'la imagen vive en la bóveda y esta instalación no tiene ninguna configurada',
        'fr': "l'image vit dans le coffre et aucun coffre n'est configuré sur ce déploiement",
        'de': 'das Bild lebt im Tresor, und auf dieser Installation ist kein Tresor eingerichtet',
        'pt': 'a imagem vive no cofre e não há nenhum cofre configurado nesta instalação',
        'it': "l'immagine vive nella cassaforte e in questa installazione non ne è configurata alcuna",
        'ja': '画像は保管庫の中にありますが、この導入には保管庫が設定されていません',
        'zh': '图像存放在保险库中，而此部署未配置保险库',
        'hi': 'तस्वीर वॉल्ट में रहती है और इस परिनियोजन में कोई वॉल्ट कॉन्फ़िगर नहीं है',
        'ar': 'تعيش الصورة داخل الخزنة ولا توجد خزنة مُهيّأة في هذا النشر',
    },
    'the vault has no record under that key': {
        'es': 'la bóveda no tiene ningún registro bajo esa clave',
        'fr': "le coffre n'a aucun enregistrement sous cette clé",
        'de': 'der Tresor hat unter diesem Schlüssel keinen Eintrag',
        'pt': 'o cofre não tem qualquer registo sob essa chave',
        'it': 'la cassaforte non ha alcun record sotto quella chiave',
        'ja': 'その鍵に対応する記録は保管庫にありません',
        'zh': '保险库中没有该键对应的记录',
        'hi': 'उस कुंजी के अंतर्गत वॉल्ट में कोई रिकॉर्ड नहीं है',
        'ar': 'لا يوجد سجلّ في الخزنة تحت ذلك المفتاح',
    },
    'nothing attached — attach a microphone first': {
        'es': 'no hay nada conectado: conecta primero un micrófono',
        'fr': "rien n'est branché — branche d'abord un micro",
        'de': 'nichts angeschlossen — schließ zuerst ein Mikrofon an',
        'pt': 'nada ligado — liga primeiro um microfone',
        'it': 'niente collegato — collega prima un microfono',
        'ja': '何も接続されていません — 先にマイクを接続してください',
        'zh': '没有连接任何设备 — 请先接上麦克风',
        'hi': 'कुछ भी जुड़ा नहीं है — पहले माइक जोड़ो',
        'ar': 'لا شيء موصول — وصّل ميكروفونًا أولًا',
    },
    'nothing attached — attach a microphone before handing it over': {
        'es': 'no hay nada conectado: conecta un micrófono antes de cederlo',
        'fr': "rien n'est branché — branche un micro avant de le confier",
        'de': 'nichts angeschlossen — schließ ein Mikrofon an, bevor du es übergibst',
        'pt': 'nada ligado — liga um microfone antes de o entregar',
        'it': 'niente collegato — collega un microfono prima di cederlo',
        'ja': '何も接続されていません — 引き渡す前にマイクを接続してください',
        'zh': '没有连接任何设备 — 交出之前请先接上麦克风',
        'hi': 'कुछ भी जुड़ा नहीं है — सौंपने से पहले माइक जोड़ो',
        'ar': 'لا شيء موصول — وصّل ميكروفونًا قبل تسليمه',
    },
    "no listening service is configured — the app will use the device's own recogniser": {
        'es': 'no hay ningún servicio de escucha configurado: la aplicación usará el reconocedor del propio dispositivo',
        'fr': "aucun service d'écoute n'est configuré — l'application utilisera le module de reconnaissance de l'appareil",
        'de': 'es ist kein Hördienst eingerichtet — die App nutzt die Spracherkennung des Geräts selbst',
        'pt': 'não há nenhum serviço de escuta configurado — a aplicação vai usar o reconhecedor do próprio dispositivo',
        'it': "nessun servizio di ascolto configurato — l'app userà il riconoscitore del dispositivo",
        'ja': '聞き取りサービスが設定されていません — 端末自身の音声認識を使います',
        'zh': '未配置听写服务 — 应用将使用设备自带的识别功能',
        'hi': 'कोई सुनने की सेवा कॉन्फ़िगर नहीं है — ऐप डिवाइस के अपने रिकग्नाइज़र का इस्तेमाल करेगा',
        'ar': 'لا توجد خدمة استماع مُهيّأة — سيستخدم التطبيق مُميّز الكلام في الجهاز نفسه',
    },
    "no speaking service is configured — the app will use the device's own voice": {
        'es': 'no hay ningún servicio de voz configurado: la aplicación usará la voz del propio dispositivo',
        'fr': "aucun service de synthèse vocale n'est configuré — l'application utilisera la voix de l'appareil",
        'de': 'es ist kein Sprachdienst eingerichtet — die App nutzt die Stimme des Geräts selbst',
        'pt': 'não há nenhum serviço de voz configurado — a aplicação vai usar a voz do próprio dispositivo',
        'it': "nessun servizio vocale configurato — l'app userà la voce del dispositivo",
        'ja': '読み上げサービスが設定されていません — 端末自身の音声を使います',
        'zh': '未配置语音服务 — 应用将使用设备自带的声音',
        'hi': 'कोई बोलने की सेवा कॉन्फ़िगर नहीं है — ऐप डिवाइस की अपनी आवाज़ इस्तेमाल करेगा',
        'ar': 'لا توجد خدمة نطق مُهيّأة — سيستخدم التطبيق صوت الجهاز نفسه',
    },
    "no speaking service is configured — the device's own voice has no allowance to run out": {
        'es': 'no hay ningún servicio de voz configurado: la voz del propio dispositivo no tiene ningún saldo que agotar',
        'fr': "aucun service de synthèse vocale n'est configuré — la voix de l'appareil n'a aucun quota à épuiser",
        'de': 'es ist kein Sprachdienst eingerichtet — die Stimme des Geräts hat kein Kontingent, das zur Neige gehen könnte',
        'pt': 'não há nenhum serviço de voz configurado — a voz do próprio dispositivo não tem saldo que possa acabar',
        'it': 'nessun servizio vocale configurato — la voce del dispositivo non ha un credito da esaurire',
        'ja': '読み上げサービスが設定されていません — 端末自身の音声には、使い切る残量がありません',
        'zh': '未配置语音服务 — 设备自带的声音没有会用尽的额度',
        'hi': 'कोई बोलने की सेवा कॉन्फ़िगर नहीं है — डिवाइस की अपनी आवाज़ की कोई सीमा नहीं जो ख़त्म हो',
        'ar': 'لا توجد خدمة نطق مُهيّأة — صوت الجهاز نفسه بلا رصيد ينفد',
    },
    'no speaking service is configured — there is no key to check': {
        'es': 'no hay ningún servicio de voz configurado: no hay ninguna clave que comprobar',
        'fr': "aucun service de synthèse vocale n'est configuré — il n'y a aucune clé à vérifier",
        'de': 'es ist kein Sprachdienst eingerichtet — es gibt keinen Schlüssel zu prüfen',
        'pt': 'não há nenhum serviço de voz configurado — não há nenhuma chave para verificar',
        'it': "nessun servizio vocale configurato — non c'è alcuna chiave da controllare",
        'ja': '読み上げサービスが設定されていません — 確認すべき鍵がありません',
        'zh': '未配置语音服务 — 没有可供校验的密钥',
        'hi': 'कोई बोलने की सेवा कॉन्फ़िगर नहीं है — जाँचने के लिए कोई कुंजी ही नहीं है',
        'ar': 'لا توجد خدمة نطق مُهيّأة — لا يوجد مفتاح لفحصه',
    },
    'offline: this deployment sends nothing off the machine, so the page cannot be fetched — paste the content into collect instead': {
        'es': 'sin conexión: esta instalación no envía nada fuera de la máquina, así que no se puede traer la página; pega el contenido en collect en su lugar',
        'fr': "hors ligne : ce déploiement n'envoie rien hors de la machine, la page ne peut donc pas être récupérée — colle plutôt le contenu dans collect",
        'de': 'offline: diese Installation sendet nichts von der Maschine weg, die Seite kann also nicht geholt werden — füge den Inhalt stattdessen in collect ein',
        'pt': 'offline: esta instalação não envia nada para fora da máquina, por isso a página não pode ser obtida — cola antes o conteúdo em collect',
        'it': 'offline: questa installazione non manda nulla fuori dalla macchina, quindi la pagina non può essere scaricata — incolla invece il contenuto in collect',
        'ja': 'オフライン：この導入はマシンの外へ何も送らないため、ページを取得できません — 代わりに内容を collect に貼り付けてください',
        'zh': '离线：此部署不向机器外发送任何内容，因此无法抓取该页面 — 请改为把内容粘贴到 collect 中',
        'hi': 'ऑफ़लाइन: यह परिनियोजन मशीन से बाहर कुछ नहीं भेजता, इसलिए पेज नहीं लाया जा सकता — इसके बजाय सामग्री collect में चिपकाओ',
        'ar': 'دون اتصال: هذا النشر لا يرسل شيئًا خارج الجهاز، لذلك تعذّر جلب الصفحة — الصق المحتوى في collect بدلًا من ذلك',
    },
    'openai refused it: HTTP 401 bad key': {
        'es': 'openai lo rechazó: HTTP 401 clave incorrecta',
        'fr': "openai l'a refusé : HTTP 401 clé incorrecte",
        'de': 'openai hat es abgelehnt: HTTP 401 falscher Schlüssel',
        'pt': 'o openai recusou-o: HTTP 401 chave inválida',
        'it': "openai l'ha rifiutato: HTTP 401 chiave errata",
        'ja': 'openai が拒否しました：HTTP 401 鍵が正しくありません',
        'zh': 'openai 拒绝了：HTTP 401 密钥无效',
        'hi': 'openai ने इसे अस्वीकार किया: HTTP 401 ग़लत कुंजी',
        'ar': 'رفضه openai: \u200fHTTP 401 مفتاح غير صالح',
    },
    'this app will not store an image of that area for an account belonging to a minor, under any circumstance. Please contact a clinician or a paediatric service directly — they can examine in person, which is the right way to handle this.': {
        'es': 'esta aplicación no guardará una imagen de esa zona en una cuenta de un menor, bajo ninguna circunstancia. Contacta directamente con un profesional clínico o un servicio pediátrico: pueden examinar en persona, que es la forma correcta de tratar esto.',
        'fr': "cette application n'enregistrera en aucun cas une image de cette zone pour un compte appartenant à un mineur. Contacte directement un clinicien ou un service pédiatrique — ils peuvent examiner en personne, et c'est la bonne façon de traiter cela.",
        'de': 'diese App speichert unter keinen Umständen ein Bild dieser Körperregion für ein Konto, das einem Minderjährigen gehört. Wende dich direkt an eine Ärztin, einen Arzt oder einen kinderärztlichen Dienst — sie können persönlich untersuchen, und das ist der richtige Weg.',
        'pt': 'esta aplicação não vai guardar uma imagem dessa zona numa conta pertencente a um menor, em circunstância alguma. Contacta directamente um clínico ou um serviço pediátrico — podem examinar presencialmente, que é a forma correcta de tratar isto.',
        'it': "questa applicazione non salverà in nessun caso un'immagine di quella zona per un account che appartiene a un minore. Contatta direttamente un medico o un servizio pediatrico — possono visitare di persona, ed è il modo giusto di affrontarlo.",
        'ja': 'このアプリは、未成年のアカウントについてその部位の画像をいかなる場合も保存しません。臨床医または小児科のサービスに直接ご連絡ください — 対面で診察できることが、これを扱う正しい方法です。',
        'zh': '本应用在任何情况下都不会为未成年人的账户存储该部位的图像。请直接联系临床医生或儿科服务 — 他们可以当面检查，这才是处理此事的正确方式。',
        'hi': 'यह ऐप किसी नाबालिग के खाते के लिए उस हिस्से की तस्वीर किसी भी हाल में संग्रहीत नहीं करेगा। कृपया सीधे किसी चिकित्सक या बाल-चिकित्सा सेवा से संपर्क करो — वे व्यक्तिगत रूप से जाँच कर सकते हैं, और यही इसे संभालने का सही तरीक़ा है।',
        'ar': 'لن يخزّن هذا التطبيق صورة لتلك المنطقة لحساب يخصّ قاصرًا، تحت أي ظرف. تواصل مباشرة مع طبيب أو خدمة أطفال — يمكنهم الفحص شخصيًا، وهذه هي الطريقة الصحيحة للتعامل مع الأمر.',
    },
    'a photograph of your body is only stored in the encrypted vault, and this deployment has none configured. Nothing was saved. Colocation is free — see the hosting options — and everything else in the app works without it.': {
        'es': 'una fotografía de tu cuerpo solo se guarda en la bóveda cifrada, y esta instalación no tiene ninguna configurada. No se guardó nada. La colocación es gratuita — mira las opciones de alojamiento — y todo lo demás en la aplicación funciona sin ella.',
        'fr': "une photographie de ton corps n'est conservée que dans le coffre chiffré, et ce déploiement n'en a aucun de configuré. Rien n'a été enregistré. La colocation est gratuite — vois les options d'hébergement — et tout le reste de l'application fonctionne sans elle.",
        'de': 'eine Fotografie deines Körpers wird nur im verschlüsselten Tresor gespeichert, und diese Installation hat keinen eingerichtet. Es wurde nichts gespeichert. Colocation ist kostenlos — sieh dir die Hosting-Optionen an — und alles andere in der App funktioniert auch ohne.',
        'pt': 'uma fotografia do teu corpo só é guardada no cofre cifrado, e esta instalação não tem nenhum configurado. Nada foi guardado. A colocação é gratuita — vê as opções de alojamento — e tudo o resto na aplicação funciona sem ela.',
        'it': "una fotografia del tuo corpo viene conservata solo nella cassaforte cifrata, e questa installazione non ne ha nessuna configurata. Non è stato salvato nulla. La colocazione è gratuita — guarda le opzioni di hosting — e tutto il resto dell'app funziona senza.",
        'ja': '身体の写真は暗号化された保管庫にのみ保存されますが、この導入には保管庫が設定されていません。何も保存されていません。コロケーションは無料です — ホスティングの選択肢をご覧ください — そして、アプリの他のすべては保管庫なしでも動きます。',
        'zh': '你身体的照片只会存放在加密保险库中，而此部署未配置保险库。未保存任何内容。托管是免费的 — 请查看托管选项 — 应用中的其他一切在没有它的情况下也能正常使用。',
        'hi': 'तुम्हारे शरीर की तस्वीर सिर्फ़ एन्क्रिप्टेड वॉल्ट में ही रखी जाती है, और इस परिनियोजन में कोई वॉल्ट कॉन्फ़िगर नहीं है। कुछ भी सहेजा नहीं गया। कोलोकेशन मुफ़्त है — होस्टिंग विकल्प देखो — और ऐप की बाक़ी हर चीज़ इसके बिना भी काम करती है।',
        'ar': 'لا تُحفظ صورة جسدك إلا في الخزنة المشفّرة، وهذا النشر لا يملك واحدة مُهيّأة. لم يُحفظ شيء. الاستضافة المشتركة مجانية — انظر خيارات الاستضافة — وكل ما عدا ذلك في التطبيق يعمل بدونها.',
    },
    'auto_defib requires a signed autonomous-resuscitation waiver; without one, use fetch_aed / guide_first_aid — the AED advises and a human presses the button': {
        'es': 'auto_defib requiere una renuncia firmada de reanimación autónoma; sin ella, usa fetch_aed / guide_first_aid: el DEA aconseja y una persona pulsa el botón',
        'fr': "auto_defib exige une décharge signée de réanimation autonome ; sans elle, utilise fetch_aed / guide_first_aid — le DAE conseille et c'est un humain qui appuie sur le bouton",
        'de': 'auto_defib erfordert eine unterschriebene Verzichtserklärung zur autonomen Wiederbelebung; ohne sie nimm fetch_aed / guide_first_aid — der AED berät, und ein Mensch drückt den Knopf',
        'pt': 'auto_defib exige uma declaração assinada de reanimação autónoma; sem ela, usa fetch_aed / guide_first_aid — o DAE aconselha e é uma pessoa que carrega no botão',
        'it': 'auto_defib richiede una liberatoria firmata per la rianimazione autonoma; senza, usa fetch_aed / guide_first_aid — il DAE consiglia e una persona preme il pulsante',
        'ja': 'auto_defib には署名済みの自動蘇生同意書が必要です。ない場合は fetch_aed / guide_first_aid を使ってください — AED は助言し、ボタンを押すのは人間です',
        'zh': 'auto_defib 需要已签署的自主复苏免责书；没有的话请使用 fetch_aed / guide_first_aid — AED 负责建议，由人来按下按钮',
        'hi': 'auto_defib के लिए हस्ताक्षरित स्वायत्त-पुनर्जीवन छूट ज़रूरी है; उसके बिना fetch_aed / guide_first_aid इस्तेमाल करो — AED सलाह देता है और बटन कोई इंसान दबाता है',
        'ar': 'يتطلّب auto_defib تنازلًا موقّعًا عن الإنعاش الذاتي؛ بدونه استخدم fetch_aed / guide_first_aid — جهاز الصدمات ينصح، والإنسان هو من يضغط الزر',
    },
    'not while other people are in earshot — the agent would be listening to them too, and they did not agree to that': {
        'es': 'no mientras haya otras personas al alcance del oído: el agente también las estaría escuchando, y ellas no aceptaron eso',
        'fr': "pas tant que d'autres personnes sont à portée de voix — l'agent les écouterait elles aussi, et elles n'ont pas donné leur accord",
        'de': 'nicht, solange andere in Hörweite sind — der Agent würde ihnen ebenfalls zuhören, und dem haben sie nicht zugestimmt',
        'pt': 'não enquanto houver outras pessoas ao alcance do ouvido — o agente também estaria a ouvi-las, e elas não concordaram com isso',
        'it': "non mentre altre persone sono a portata d'orecchio — l'agente ascolterebbe anche loro, e loro non hanno acconsentito",
        'ja': 'ほかの人の声が届く場所では行いません — エージェントはその人たちの声も聞くことになり、その人たちは同意していません',
        'zh': '旁边有其他人时不行 — 智能体也会听到他们，而他们并未同意',
        'hi': 'जब आसपास दूसरे लोग सुन सकते हों तब नहीं — एजेंट उन्हें भी सुनेगा, और उन्होंने इसकी सहमति नहीं दी',
        'ar': 'ليس بينما يوجد آخرون على مسمع — سيستمع الوكيل إليهم أيضًا، وهم لم يوافقوا على ذلك',
    },
    'an adult enrolls themselves — guardian setup is for under-18s': {
        'es': 'una persona adulta se inscribe a sí misma: la configuración de tutor es para menores de 18',
        'fr': "un adulte s'inscrit lui-même — la configuration du tuteur est réservée aux moins de 18 ans",
        'de': 'eine erwachsene Person meldet sich selbst an — die Einrichtung als Vormund ist für Minderjährige',
        'pt': 'um adulto inscreve-se a si próprio — a configuração de tutor é para menores de 18',
        'it': 'una persona adulta si iscrive da sé — la configurazione del tutore è per i minori di 18 anni',
        'ja': '大人はご自身で登録します — 保護者の設定は 18 歳未満のためのものです',
        'zh': '成年人自行注册 — 监护人设置是给未满 18 岁的人用的',
        'hi': 'वयस्क ख़ुद पंजीकरण करते हैं — अभिभावक सेटअप 18 से कम उम्र वालों के लिए है',
        'ar': 'البالغ يسجّل نفسه — إعداد وليّ الأمر مخصّص لمن هم دون الثامنة عشرة',
    },
    'only a verified-adult guardian can enroll a child': {
        'es': 'solo un tutor con edad adulta verificada puede inscribir a un menor',
        'fr': "seul un tuteur dont l'âge adulte est vérifié peut inscrire un enfant",
        'de': 'nur ein Vormund mit bestätigter Volljährigkeit kann ein Kind anmelden',
        'pt': 'só um tutor com idade adulta verificada pode inscrever uma criança',
        'it': 'solo un tutore con età adulta verificata può iscrivere un minore',
        'ja': '成人であることが確認された保護者だけが、子どもを登録できます',
        'zh': '只有经过成年验证的监护人才能为孩子注册',
        'hi': 'सिर्फ़ सत्यापित वयस्क अभिभावक ही किसी बच्चे का पंजीकरण कर सकता है',
        'ar': 'لا يمكن تسجيل طفل إلا من وليّ أمر مُتحقَّق من بلوغه',
    },
    "only this child's guardian can place a beacon for them": {
        'es': 'solo el tutor de este menor puede colocar una baliza para él',
        'fr': 'seul le tuteur de cet enfant peut poser une balise pour lui',
        'de': 'nur der Vormund dieses Kindes kann für es einen Beacon anbringen',
        'pt': 'só o tutor desta criança pode colocar uma baliza por ela',
        'it': 'solo il tutore di questo minore può collocare un beacon per lui',
        'ja': 'この子どものビーコンを設置できるのは、その保護者だけです',
        'zh': '只有这个孩子的监护人才能为其放置信标',
        'hi': 'इस बच्चे के लिए बीकन सिर्फ़ उसका अभिभावक ही लगा सकता है',
        'ar': 'لا يمكن وضع منارة لهذا الطفل إلا من وليّ أمره',
    },
    'this account has no guardian link, and a minor cannot place their own beacon': {
        'es': 'esta cuenta no tiene ningún tutor vinculado, y un menor no puede colocar su propia baliza',
        'fr': "ce compte n'a aucun tuteur associé, et un mineur ne peut pas poser sa propre balise",
        'de': 'dieses Konto hat keine Vormund-Verknüpfung, und ein Minderjähriger kann keinen eigenen Beacon anbringen',
        'pt': 'esta conta não tem nenhum tutor ligado, e um menor não pode colocar a sua própria baliza',
        'it': 'questo account non ha alcun tutore collegato, e un minore non può collocare il proprio beacon',
        'ja': 'このアカウントには保護者の紐付けがなく、未成年は自分でビーコンを設置できません',
        'zh': '此账户没有关联监护人，未成年人不能自行放置信标',
        'hi': 'इस खाते से कोई अभिभावक जुड़ा नहीं है, और नाबालिग अपना बीकन ख़ुद नहीं लगा सकता',
        'ar': 'لا يوجد وليّ أمر مرتبط بهذا الحساب، والقاصر لا يمكنه وضع منارته بنفسه',
    },
    "the child's birthdate is required": {
        'es': 'se requiere la fecha de nacimiento del menor',
        'fr': "la date de naissance de l'enfant est requise",
        'de': 'das Geburtsdatum des Kindes ist erforderlich',
        'pt': 'a data de nascimento da criança é obrigatória',
        'it': 'la data di nascita del minore è obbligatoria',
        'ja': 'お子さんの生年月日が必要です',
        'zh': '需要孩子的出生日期',
        'hi': 'बच्चे की जन्मतिथि ज़रूरी है',
        'ar': 'تاريخ ميلاد الطفل مطلوب',
    },
    "a responder needs a name — 'someone accepted it' is the thing this relay exists to stop being enough": {
        'es': 'quien responde necesita un nombre: «alguien lo aceptó» es precisamente lo que este relevo existe para que deje de bastar',
        'fr': "un intervenant a besoin d'un nom — « quelqu'un a accepté » est exactement ce que ce relais existe pour ne plus laisser suffire",
        'de': 'wer übernimmt, braucht einen Namen — „irgendwer hat zugesagt“ ist genau das, was dieser Melder nicht mehr genügen lassen soll',
        'pt': 'quem responde precisa de um nome — «alguém aceitou» é justamente aquilo que este relé existe para deixar de bastar',
        'it': 'chi risponde ha bisogno di un nome — «qualcuno ha accettato» è esattamente ciò che questo relè esiste per non far più bastare',
        'ja': '対応する人には名前が必要です — 「誰かが引き受けた」で済ませないために、この中継はあります',
        'zh': '响应者需要有名字 — 这个中继存在的意义，正是让“有人接下了”不再算数',
        'hi': "जवाब देने वाले का नाम चाहिए — 'किसी ने स्वीकार कर लिया' — यही वह बात है जिसे काफ़ी न रहने देने के लिए यह रिले बना है",
        'ar': 'من يستجيب يحتاج اسمًا — «قبِلها أحدهم» هو بالضبط ما وُجد هذا الوسيط لكي لا يكفي بعد اليوم',
    },
    'no care team linked (PUT /users/{id}/care-team)': {
        'es': 'no hay ningún equipo de cuidados vinculado (PUT /users/{id}/care-team)',
        'fr': 'aucune équipe soignante liée (PUT /users/{id}/care-team)',
        'de': 'kein Behandlungsteam verknüpft (PUT /users/{id}/care-team)',
        'pt': 'nenhuma equipa de cuidados ligada (PUT /users/{id}/care-team)',
        'it': 'nessuna équipe di cura collegata (PUT /users/{id}/care-team)',
        'ja': 'ケアチームが紐付けられていません（PUT /users/{id}/care-team）',
        'zh': '未关联照护团队（PUT /users/{id}/care-team）',
        'hi': 'कोई केयर टीम नहीं जुड़ी है (PUT /users/{id}/care-team)',
        'ar': 'لا يوجد فريق رعاية مرتبط (PUT /users/{id}/care-team)',
    },
    'the care team needs at least two departments to coordinate — staff another desk in QRME first': {
        'es': 'el equipo de cuidados necesita al menos dos departamentos para coordinarse: dota primero otro puesto en QRME',
        'fr': "l'équipe soignante a besoin d'au moins deux services pour se coordonner — dote d'abord un autre poste dans QRME",
        'de': 'das Behandlungsteam braucht mindestens zwei Abteilungen, um sich abzustimmen — besetze zuerst einen weiteren Platz in QRME',
        'pt': 'a equipa de cuidados precisa de pelo menos dois departamentos para se coordenar — preenche primeiro outro balcão no QRME',
        'it': "l'équipe di cura ha bisogno di almeno due reparti per coordinarsi — assegna prima un altro banco in QRME",
        'ja': '連携には少なくとも二つの部門が必要です — まず QRME でもう一つのデスクに人を置いてください',
        'zh': '照护团队需要至少两个科室才能协作 — 请先在 QRME 里再配置一个坐席',
        'hi': 'समन्वय के लिए केयर टीम को कम से कम दो विभाग चाहिए — पहले QRME में एक और डेस्क पर कोई नियुक्त करो',
        'ar': 'يحتاج فريق الرعاية إلى قسمين على الأقل للتنسيق — عيّن أولًا مكتبًا آخر في QRME',
    },
    'that department is not part of the organization': {
        'es': 'ese departamento no forma parte de la organización',
        'fr': "ce service ne fait pas partie de l'organisation",
        'de': 'diese Abteilung gehört nicht zur Organisation',
        'pt': 'esse departamento não faz parte da organização',
        'it': "quel reparto non fa parte dell'organizzazione",
        'ja': 'その部門はこの組織の一部ではありません',
        'zh': '该科室不属于本组织',
        'hi': 'वह विभाग इस संगठन का हिस्सा नहीं है',
        'ar': 'هذا القسم ليس جزءًا من المؤسسة',
    },
    'no such referral request on this account': {
        'es': 'no existe esa solicitud de derivación en esta cuenta',
        'fr': "aucune demande d'orientation de ce type sur ce compte",
        'de': 'eine solche Überweisungsanfrage gibt es auf diesem Konto nicht',
        'pt': 'não existe esse pedido de encaminhamento nesta conta',
        'it': 'nessuna richiesta di invio del genere su questo account',
        'ja': 'このアカウントにそのような紹介の依頼はありません',
        'zh': '此账户中没有这项转介请求',
        'hi': 'इस खाते पर ऐसा कोई रेफ़रल अनुरोध नहीं है',
        'ar': 'لا يوجد طلب إحالة بهذا الوصف على هذا الحساب',
    },
    'a beacon needs a label so its owner can tell their codes apart once several are printed and stuck to different things': {
        'es': 'una baliza necesita una etiqueta para que su dueño distinga sus códigos cuando haya varios impresos y pegados en cosas distintas',
        'fr': "une balise a besoin d'une étiquette pour que son propriétaire distingue ses codes une fois que plusieurs sont imprimés et collés sur des objets différents",
        'de': 'ein Beacon braucht eine Beschriftung, damit seine Besitzerin ihre Codes auseinanderhalten kann, sobald mehrere gedruckt und auf verschiedene Dinge geklebt sind',
        'pt': 'uma baliza precisa de uma etiqueta para que o dono distinga os seus códigos quando vários estiverem impressos e colados em coisas diferentes',
        'it': "un beacon ha bisogno di un'etichetta perché chi lo possiede distingua i propri codici quando ne ha stampati e attaccati diversi",
        'ja': 'ビーコンにはラベルが必要です。いくつも印刷していろいろな場所に貼ったとき、持ち主が見分けられるようにするためです',
        'zh': '信标需要一个标签，这样在打印了好几个、贴在不同东西上之后，主人才能分得清',
        'hi': 'बीकन को एक लेबल चाहिए, ताकि कई कोड छापकर अलग-अलग चीज़ों पर चिपकाने के बाद मालिक उन्हें पहचान सके',
        'ar': 'تحتاج المنارة إلى عنوان كي يميّز صاحبها بين رموزه بعد طباعة عدّة منها ولصقها على أشياء مختلفة',
    },
    'nobody by that id lives on this deployment': {
        'es': 'nadie con ese id vive en esta instalación',
        'fr': 'personne avec cet identifiant ne vit sur ce déploiement',
        'de': 'niemand mit dieser Kennung lebt auf dieser Installation',
        'pt': 'ninguém com esse id vive nesta instalação',
        'it': "nessuno con quell'id vive in questa installazione",
        'ja': 'その id を持つ人は、この導入にはいません',
        'zh': '此部署上没有该 id 对应的人',
        'hi': 'उस id वाला कोई इस परिनियोजन पर नहीं है',
        'ar': 'لا أحد بهذا المعرّف يقيم في هذا النشر',
    },
    'unknown user': {
        'es': 'usuario desconocido',
        'fr': 'utilisateur inconnu',
        'de': 'unbekannte Person',
        'pt': 'utilizador desconhecido',
        'it': 'utente sconosciuto',
        'ja': '不明なユーザーです',
        'zh': '未知用户',
        'hi': 'अज्ञात उपयोगकर्ता',
        'ar': 'مستخدم غير معروف',
    },
    'no such account': {
        'es': 'no existe esa cuenta',
        'fr': 'aucun compte de ce type',
        'de': 'ein solches Konto gibt es nicht',
        'pt': 'não existe essa conta',
        'it': 'nessun account del genere',
        'ja': 'そのようなアカウントはありません',
        'zh': '没有这个账户',
        'hi': 'ऐसा कोई खाता नहीं है',
        'ar': 'لا يوجد حساب بهذا الوصف',
    },
    'that account belongs to somebody else': {
        'es': 'esa cuenta es de otra persona',
        'fr': "ce compte appartient à quelqu'un d'autre",
        'de': 'dieses Konto gehört jemand anderem',
        'pt': 'essa conta pertence a outra pessoa',
        'it': "quell'account appartiene a un'altra persona",
        'ja': 'そのアカウントは別の人のものです',
        'zh': '该账户属于其他人',
        'hi': 'वह खाता किसी और का है',
        'ar': 'هذا الحساب يخصّ شخصًا آخر',
    },
    "no public address to visit — reconnect with the account's handle": {
        'es': 'no hay ninguna dirección pública que visitar: vuelve a conectar con el identificador de la cuenta',
        'fr': "aucune adresse publique à visiter — reconnecte-toi avec l'identifiant du compte",
        'de': 'keine öffentliche Adresse zum Besuchen — verbinde neu mit dem Kürzel des Kontos',
        'pt': 'não há nenhuma morada pública para visitar — volta a ligar com o identificador da conta',
        'it': "nessun indirizzo pubblico da visitare — riconnetti con l'handle dell'account",
        'ja': '訪問できる公開アドレスがありません — アカウントのハンドルで接続し直してください',
        'zh': '没有可访问的公开地址 — 请用该账户的用户名重新连接',
        'hi': 'जाने के लिए कोई सार्वजनिक पता नहीं है — खाते के हैंडल से दोबारा जोड़ो',
        'ar': 'لا يوجد عنوان عام لزيارته — أعِد الاتصال باسم الحساب',
    },
    "a bank link's tokens are private data and only ever live in the vault; this plan has no vault, so no link was made": {
        'es': 'los tokens de un enlace bancario son datos privados y solo viven en la bóveda; este plan no tiene bóveda, así que no se creó ningún enlace',
        'fr': "les jetons d'un lien bancaire sont des données privées et ne vivent que dans le coffre ; ce forfait n'a pas de coffre, aucun lien n'a donc été créé",
        'de': 'die Token einer Bankverknüpfung sind private Daten und leben ausschließlich im Tresor; dieser Tarif hat keinen Tresor, deshalb wurde keine Verknüpfung angelegt',
        'pt': 'os tokens de uma ligação bancária são dados privados e vivem apenas no cofre; este plano não tem cofre, por isso não foi criada nenhuma ligação',
        'it': 'i token di un collegamento bancario sono dati privati e vivono solo nella cassaforte; questo piano non ne ha una, quindi non è stato creato alcun collegamento',
        'ja': '銀行連携のトークンは私的なデータで、保管庫の中にしか存在しません。このプランには保管庫がないため、連携は作成されませんでした',
        'zh': '银行关联的令牌属于私密数据，只存放在保险库中；此方案没有保险库，因此未建立关联',
        'hi': 'बैंक लिंक के टोकन निजी डेटा हैं और सिर्फ़ वॉल्ट में ही रहते हैं; इस प्लान में वॉल्ट नहीं है, इसलिए कोई लिंक नहीं बना',
        'ar': 'رموز ربط البنك بيانات خاصة ولا تعيش إلا داخل الخزنة؛ هذه الخطة بلا خزنة، لذلك لم يُنشأ أي ربط',
    },
    'a bank statement is private data and only ever lives in the vault; this plan has no vault, so nothing was stored': {
        'es': 'un extracto bancario es un dato privado y solo vive en la bóveda; este plan no tiene bóveda, así que no se guardó nada',
        'fr': "un relevé bancaire est une donnée privée et ne vit que dans le coffre ; ce forfait n'a pas de coffre, rien n'a donc été conservé",
        'de': 'ein Kontoauszug ist ein privates Datum und lebt ausschließlich im Tresor; dieser Tarif hat keinen Tresor, deshalb wurde nichts gespeichert',
        'pt': 'um extracto bancário é um dado privado e vive apenas no cofre; este plano não tem cofre, por isso nada foi guardado',
        'it': 'un estratto conto è un dato privato e vive solo nella cassaforte; questo piano non ne ha una, quindi non è stato salvato nulla',
        'ja': '取引明細は私的なデータで、保管庫の中にしか存在しません。このプランには保管庫がないため、何も保存されませんでした',
        'zh': '银行对账单属于私密数据，只存放在保险库中；此方案没有保险库，因此未保存任何内容',
        'hi': 'बैंक स्टेटमेंट निजी डेटा है और सिर्फ़ वॉल्ट में ही रहता है; इस प्लान में वॉल्ट नहीं है, इसलिए कुछ भी संग्रहीत नहीं हुआ',
        'ar': 'كشف الحساب بيانات خاصة ولا يعيش إلا داخل الخزنة؛ هذه الخطة بلا خزنة، لذلك لم يُحفظ شيء',
    },
    'account credentials are private data and only ever live in the vault; this plan has no vault, so they were not stored — upgrade to a private plan or register the account without numbers': {
        'es': 'las credenciales de una cuenta son datos privados y solo viven en la bóveda; este plan no tiene bóveda, así que no se guardaron: pasa a un plan privado o registra la cuenta sin números',
        'fr': "les identifiants d'un compte sont des données privées et ne vivent que dans le coffre ; ce forfait n'a pas de coffre, ils n'ont donc pas été conservés — passe à un forfait privé ou enregistre le compte sans numéros",
        'de': 'Zugangsdaten sind private Daten und leben ausschließlich im Tresor; dieser Tarif hat keinen Tresor, deshalb wurden sie nicht gespeichert — wechsle zu einem privaten Tarif oder registriere das Konto ohne Nummern',
        'pt': 'as credenciais de uma conta são dados privados e vivem apenas no cofre; este plano não tem cofre, por isso não foram guardadas — muda para um plano privado ou regista a conta sem números',
        'it': 'le credenziali di un conto sono dati privati e vivono solo nella cassaforte; questo piano non ne ha una, quindi non sono state salvate — passa a un piano privato o registra il conto senza numeri',
        'ja': 'アカウントの資格情報は私的なデータで、保管庫の中にしか存在しません。このプランには保管庫がないため保存されませんでした — プライベートプランに変更するか、番号なしで登録してください',
        'zh': '账户凭据属于私密数据，只存放在保险库中；此方案没有保险库，因此未予保存 — 请升级到私密方案，或不带号码登记该账户',
        'hi': 'खाते की क्रेडेंशियल निजी डेटा हैं और सिर्फ़ वॉल्ट में ही रहती हैं; इस प्लान में वॉल्ट नहीं है, इसलिए वे संग्रहीत नहीं हुईं — निजी प्लान लो, या बिना नंबरों के खाता दर्ज करो',
        'ar': 'بيانات اعتماد الحساب بيانات خاصة ولا تعيش إلا داخل الخزنة؛ هذه الخطة بلا خزنة، لذلك لم تُحفظ — انتقل إلى خطة خاصة أو سجّل الحساب دون أرقام',
    },
    'a mandate needs a written scope: what JIM may do with your money, in words you would show your own accountant': {
        'es': 'un mandato necesita un alcance por escrito: qué puede hacer JIM con tu dinero, en palabras que le enseñarías a tu propio contable',
        'fr': "un mandat a besoin d'une portée écrite : ce que JIM peut faire de ton argent, dans des mots que tu montrerais à ton propre comptable",
        'de': 'ein Mandat braucht einen schriftlichen Rahmen: was JIM mit deinem Geld tun darf, in Worten, die du deinem eigenen Steuerberater zeigen würdest',
        'pt': 'um mandato precisa de um âmbito escrito: o que o JIM pode fazer com o teu dinheiro, em palavras que mostrarias ao teu próprio contabilista',
        'it': 'un mandato ha bisogno di un ambito scritto: cosa può fare JIM con i tuoi soldi, con parole che mostreresti al tuo commercialista',
        'ja': '委任には書かれた範囲が必要です。JIM があなたのお金に対して何をしてよいのかを、自分の会計士に見せられる言葉で書いてください',
        'zh': '授权需要写明范围：JIM 可以拿你的钱做什么，用你愿意拿给自己会计看的措辞',
        'hi': 'मैंडेट के लिए लिखित दायरा चाहिए: JIM तुम्हारे पैसे के साथ क्या कर सकता है, ऐसे शब्दों में जो तुम अपने अकाउंटेंट को दिखाओ',
        'ar': 'يحتاج التفويض إلى نطاق مكتوب: ما الذي يجوز لـ JIM فعله بمالك، بكلمات تعرضها على محاسبك',
    },
    'a mandate needs positive caps — per order and per month': {
        'es': 'un mandato necesita topes positivos: por pedido y por mes',
        'fr': 'un mandat a besoin de plafonds positifs — par commande et par mois',
        'de': 'ein Mandat braucht positive Obergrenzen — je Auftrag und je Monat',
        'pt': 'um mandato precisa de tectos positivos — por encomenda e por mês',
        'it': 'un mandato ha bisogno di tetti positivi — per ordine e per mese',
        'ja': '委任には正の上限が必要です — 1 回あたりと 1 か月あたり',
        'zh': '授权需要设定正数上限 — 每笔和每月',
        'hi': 'मैंडेट के लिए धनात्मक सीमाएँ चाहिए — प्रति ऑर्डर और प्रति माह',
        'ar': 'يحتاج التفويض إلى حدود موجبة — لكل طلب ولكل شهر',
    },
    'name at least one asset class the mandate covers': {
        'es': 'nombra al menos una clase de activo que cubra el mandato',
        'fr': "nomme au moins une classe d'actifs couverte par le mandat",
        'de': 'nenne mindestens eine Anlageklasse, die das Mandat abdeckt',
        'pt': 'nomeia pelo menos uma classe de activos que o mandato cobre',
        'it': 'indica almeno una classe di attività coperta dal mandato',
        'ja': '委任が対象とする資産クラスを少なくとも一つ挙げてください',
        'zh': '至少写明该授权涵盖的一类资产',
        'hi': 'कम से कम एक ऐसी संपत्ति-श्रेणी बताओ जिसे मैंडेट कवर करता है',
        'ar': 'سمِّ فئة أصول واحدة على الأقل يغطيها التفويض',
    },
    'name the institution — a bank, a broker, an exchange': {
        'es': 'nombra la institución: un banco, un bróker, un mercado',
        'fr': "nomme l'établissement — une banque, un courtier, une bourse",
        'de': 'nenne das Institut — eine Bank, einen Broker, eine Börse',
        'pt': 'nomeia a instituição — um banco, uma corretora, uma bolsa',
        'it': "indica l'istituto — una banca, un intermediario, una borsa",
        'ja': '機関の名前を挙げてください — 銀行、証券会社、取引所',
        'zh': '写明机构名称 — 银行、券商或交易所',
        'hi': 'संस्था का नाम बताओ — बैंक, ब्रोकर या एक्सचेंज',
        'ar': 'سمِّ المؤسسة — بنك أو وسيط أو بورصة',
    },
    'no such bank link': {
        'es': 'no existe ese enlace bancario',
        'fr': 'aucun lien bancaire de ce type',
        'de': 'eine solche Bankverknüpfung gibt es nicht',
        'pt': 'não existe essa ligação bancária',
        'it': 'nessun collegamento bancario del genere',
        'ja': 'そのような銀行連携はありません',
        'zh': '没有这个银行关联',
        'hi': 'ऐसा कोई बैंक लिंक नहीं है',
        'ar': 'لا يوجد ربط بنكي بهذا الوصف',
    },
    'that bank link belongs to somebody else': {
        'es': 'ese enlace bancario es de otra persona',
        'fr': "ce lien bancaire appartient à quelqu'un d'autre",
        'de': 'diese Bankverknüpfung gehört jemand anderem',
        'pt': 'essa ligação bancária pertence a outra pessoa',
        'it': "quel collegamento bancario appartiene a un'altra persona",
        'ja': 'その銀行連携は別の人のものです',
        'zh': '该银行关联属于其他人',
        'hi': 'वह बैंक लिंक किसी और का है',
        'ar': 'هذا الربط البنكي يخصّ شخصًا آخر',
    },
    'this bank link was revoked; link again to sync': {
        'es': 'este enlace bancario fue revocado; vuelve a enlazar para sincronizar',
        'fr': 'ce lien bancaire a été révoqué ; relie à nouveau pour synchroniser',
        'de': 'diese Bankverknüpfung wurde widerrufen; verknüpfe erneut, um zu synchronisieren',
        'pt': 'esta ligação bancária foi revogada; volta a ligar para sincronizar',
        'it': 'questo collegamento bancario è stato revocato; ricollega per sincronizzare',
        'ja': 'この銀行連携は取り消されています。同期するには再度連携してください',
        'zh': '此银行关联已被撤销；请重新关联以同步',
        'hi': 'यह बैंक लिंक रद्द कर दिया गया था; सिंक करने के लिए दोबारा जोड़ो',
        'ar': 'أُلغي هذا الربط البنكي؛ أعِد الربط للمزامنة',
    },
    'no such order in your history': {
        'es': 'no existe ese pedido en tu historial',
        'fr': 'aucune commande de ce type dans ton historique',
        'de': 'eine solche Bestellung gibt es in deinem Verlauf nicht',
        'pt': 'não existe essa encomenda no teu histórico',
        'it': 'nessun ordine del genere nella tua cronologia',
        'ja': 'あなたの履歴にそのような注文はありません',
        'zh': '你的记录中没有这笔订单',
        'hi': 'तुम्हारे इतिहास में ऐसा कोई ऑर्डर नहीं है',
        'ar': 'لا يوجد طلب بهذا الوصف في سجلّك',
    },
    'the shop refused the cancellation': {
        'es': 'la tienda rechazó la cancelación',
        'fr': "la boutique a refusé l'annulation",
        'de': 'der Shop hat die Stornierung abgelehnt',
        'pt': 'a loja recusou o cancelamento',
        'it': "il negozio ha rifiutato l'annullamento",
        'ja': '店舗がキャンセルを断りました',
        'zh': '商家拒绝了取消',
        'hi': 'दुकान ने रद्द करने से इनकार किया',
        'ar': 'رفض المتجر الإلغاء',
    },
    'the shop refused the order or could not be reached; nothing was placed': {
        'es': 'la tienda rechazó el pedido o no se pudo contactar; no se hizo ningún pedido',
        'fr': "la boutique a refusé la commande ou était injoignable ; rien n'a été commandé",
        'de': 'der Shop hat die Bestellung abgelehnt oder war nicht erreichbar; es wurde nichts bestellt',
        'pt': 'a loja recusou a encomenda ou não foi possível contactá-la; nada foi encomendado',
        'it': "il negozio ha rifiutato l'ordine o non era raggiungibile; non è stato ordinato nulla",
        'ja': '店舗が注文を断ったか、connect できませんでした。注文は行われていません',
        'zh': '商家拒绝了订单或无法连接；未下任何订单',
        'hi': 'दुकान ने ऑर्डर अस्वीकार किया या उस तक नहीं पहुँचा जा सका; कुछ भी ऑर्डर नहीं हुआ',
        'ar': 'رفض المتجر الطلب أو تعذّر الوصول إليه؛ لم يُنفَّذ أي طلب',
    },
    'booking a service names both the shop and the offering': {
        'es': 'reservar un servicio nombra tanto la tienda como la oferta',
        'fr': 'réserver un service nomme à la fois la boutique et la prestation',
        'de': 'eine Dienstleistung zu buchen nennt sowohl den Shop als auch das Angebot',
        'pt': 'marcar um serviço nomeia tanto a loja como o serviço',
        'it': 'prenotare un servizio indica sia il negozio sia la prestazione',
        'ja': 'サービスの予約には店舗と提供内容の両方が必要です',
        'zh': '预约服务需同时写明商家与服务项目',
        'hi': 'सेवा बुक करने में दुकान और सेवा दोनों का नाम आता है',
        'ar': 'حجز خدمة يذكر المتجر والخدمة معًا',
    },
    'the tandem is not configured; shops live on QRME and there is no QRME to reach': {
        'es': 'el tándem no está configurado; las tiendas viven en QRME y no hay ningún QRME al que llegar',
        'fr': "le tandem n'est pas configuré ; les boutiques vivent sur QRME et il n'y a aucun QRME à joindre",
        'de': 'das Tandem ist nicht eingerichtet; Shops leben auf QRME, und es gibt kein QRME, das erreichbar wäre',
        'pt': 'o tandem não está configurado; as lojas vivem no QRME e não há nenhum QRME para contactar',
        'it': "il tandem non è configurato; i negozi vivono su QRME e non c'è alcun QRME da raggiungere",
        'ja': 'タンデムが設定されていません。店舗は QRME 上にあり、接続できる QRME がありません',
        'zh': '未配置联体；商家在 QRME 上，而当前没有可连接的 QRME',
        'hi': 'टैंडम कॉन्फ़िगर नहीं है; दुकानें QRME पर रहती हैं और पहुँचने के लिए कोई QRME नहीं है',
        'ar': 'التوأمة غير مُهيّأة؛ المتاجر تعيش على QRME ولا يوجد QRME يمكن الوصول إليه',
    },
    'the tandem is not reachable to carry the cancellation': {
        'es': 'no se puede contactar con el tándem para llevar la cancelación',
        'fr': "le tandem est injoignable pour transmettre l'annulation",
        'de': 'das Tandem ist nicht erreichbar, um die Stornierung zu übermitteln',
        'pt': 'o tandem não está acessível para levar o cancelamento',
        'it': "il tandem non è raggiungibile per trasmettere l'annullamento",
        'ja': 'キャンセルを伝えるためのタンデムに接続できません',
        'zh': '无法连接联体来传达取消',
        'hi': 'रद्दीकरण पहुँचाने के लिए टैंडम तक नहीं पहुँचा जा सकता',
        'ar': 'التوأمة غير متاحة لنقل الإلغاء',
    },
    'no QRME tandem configured on this deployment (QRME_URL)': {
        'es': 'no hay ningún tándem QRME configurado en esta instalación (QRME_URL)',
        'fr': 'aucun tandem QRME configuré sur ce déploiement (QRME_URL)',
        'de': 'auf dieser Installation ist kein QRME-Tandem eingerichtet (QRME_URL)',
        'pt': 'não há nenhum tandem QRME configurado nesta instalação (QRME_URL)',
        'it': 'nessun tandem QRME configurato in questa installazione (QRME_URL)',
        'ja': 'この導入には QRME タンデムが設定されていません（QRME_URL）',
        'zh': '此部署未配置 QRME 联体（QRME_URL）',
        'hi': 'इस परिनियोजन में कोई QRME टैंडम कॉन्फ़िगर नहीं है (QRME_URL)',
        'ar': 'لا توجد توأمة QRME مُهيّأة في هذا النشر (QRME_URL)',
    },
    'top friends are chosen from your actual contacts': {
        'es': 'los amigos destacados se eligen entre tus contactos reales',
        'fr': 'les amis en tête sont choisis parmi tes vrais contacts',
        'de': 'deine Top-Freunde werden aus deinen echten Kontakten gewählt',
        'pt': 'os amigos de topo são escolhidos entre os teus contactos reais',
        'it': 'gli amici in cima si scelgono tra i tuoi contatti reali',
        'ja': 'トップの友だちは、実際の連絡先の中から選びます',
        'zh': '置顶好友是从你真实的联系人中选择的',
        'hi': 'टॉप दोस्त तुम्हारे असली संपर्कों में से चुने जाते हैं',
        'ar': 'يُختار أفضل الأصدقاء من جهات اتصالك الفعلية',
    },
    'you are already in your own circle': {
        'es': 'ya estás en tu propio círculo',
        'fr': 'tu es déjà dans ton propre cercle',
        'de': 'du bist bereits in deinem eigenen Kreis',
        'pt': 'já estás no teu próprio círculo',
        'it': 'sei già nella tua cerchia',
        'ja': 'あなたはすでに自分のサークルにいます',
        'zh': '你已经在自己的圈子里了',
        'hi': 'तुम पहले से ही अपने ही दायरे में हो',
        'ar': 'أنت بالفعل داخل دائرتك',
    },
    'that person has messaging turned off': {
        'es': 'esa persona tiene los mensajes desactivados',
        'fr': 'cette personne a désactivé la messagerie',
        'de': 'diese Person hat Nachrichten ausgeschaltet',
        'pt': 'essa pessoa tem as mensagens desligadas',
        'it': 'quella persona ha disattivato i messaggi',
        'ja': 'その人はメッセージをオフにしています',
        'zh': '对方已关闭私信',
        'hi': 'उस व्यक्ति ने संदेश बंद कर रखे हैं',
        'ar': 'أوقف هذا الشخص المراسلة',
    },
    'your messaging is turned off; turn the switch back on to send': {
        'es': 'tienes los mensajes desactivados; vuelve a activar el interruptor para enviar',
        'fr': "ta messagerie est désactivée ; réactive l'interrupteur pour envoyer",
        'de': 'deine Nachrichten sind ausgeschaltet; schalte den Schalter wieder ein, um zu senden',
        'pt': 'tens as mensagens desligadas; volta a ligar o interruptor para enviar',
        'it': "i tuoi messaggi sono disattivati; riattiva l'interruttore per inviare",
        'ja': 'あなたのメッセージはオフです。送るにはスイッチを戻してください',
        'zh': '你的私信已关闭；重新打开开关才能发送',
        'hi': 'तुम्हारे संदेश बंद हैं; भेजने के लिए स्विच फिर से चालू करो',
        'ar': 'مراسلتك موقوفة؛ أعِد تشغيل المفتاح لترسل',
    },
    'messages travel inside your circle; invite them first, and they must invite you back': {
        'es': 'los mensajes viajan dentro de tu círculo; invítalos primero, y ellos tienen que invitarte a ti',
        'fr': "les messages circulent dans ton cercle ; invite-les d'abord, et il faut qu'ils t'invitent en retour",
        'de': 'Nachrichten bewegen sich innerhalb deines Kreises; lade sie erst ein, und sie müssen dich zurück einladen',
        'pt': 'as mensagens viajam dentro do teu círculo; convida-os primeiro, e eles têm de te convidar de volta',
        'it': 'i messaggi viaggiano dentro la tua cerchia; invitali prima, e devono invitarti a loro volta',
        'ja': 'メッセージはサークルの中を行き来します。まず相手を招待し、相手からも招待してもらってください',
        'zh': '消息只在你的圈子内传递；先邀请对方，对方也要邀请你',
        'hi': 'संदेश तुम्हारे दायरे के भीतर चलते हैं; पहले उन्हें न्योता दो, और उन्हें भी तुम्हें न्योता देना होगा',
        'ar': 'تنتقل الرسائل داخل دائرتك؛ ادعُهم أولًا، وعليهم دعوتك بالمقابل',
    },
    "'count' must be a positive integer": {
        'es': "'count' debe ser un entero positivo",
        'fr': "'count' doit être un entier positif",
        'de': "'count' muss eine positive ganze Zahl sein",
        'pt': "'count' tem de ser um inteiro positivo",
        'it': "'count' deve essere un intero positivo",
        'ja': "'count' は正の整数である必要があります",
        'zh': "'count' 必须是正整数",
        'hi': "'count' एक धनात्मक पूर्णांक होना चाहिए",
        'ar': "يجب أن يكون 'count' عددًا صحيحًا موجبًا",
    },
    "'day' must be YYYY-MM-DD": {
        'es': "'day' debe ser AAAA-MM-DD",
        'fr': "'day' doit être AAAA-MM-JJ",
        'de': "'day' muss JJJJ-MM-TT sein",
        'pt': "'day' tem de ser AAAA-MM-DD",
        'it': "'day' deve essere AAAA-MM-GG",
        'ja': "'day' は YYYY-MM-DD 形式である必要があります",
        'zh': "'day' 必须是 YYYY-MM-DD 格式",
        'hi': "'day' YYYY-MM-DD होना चाहिए",
        'ar': "يجب أن يكون 'day' بصيغة YYYY-MM-DD",
    },
    "'fingerprint' must be 8 hex characters": {
        'es': "'fingerprint' debe tener 8 caracteres hexadecimales",
        'fr': "'fingerprint' doit comporter 8 caractères hexadécimaux",
        'de': "'fingerprint' muss 8 Hexadezimalzeichen haben",
        'pt': "'fingerprint' tem de ter 8 caracteres hexadecimais",
        'it': "'fingerprint' deve avere 8 caratteri esadecimali",
        'ja': "'fingerprint' は16進数8文字である必要があります",
        'zh': "'fingerprint' 必须是 8 个十六进制字符",
        'hi': "'fingerprint' 8 हेक्स अक्षरों का होना चाहिए",
        'ar': "يجب أن يتكوّن 'fingerprint' من 8 أحرف ست عشرية",
    },
    "'op' must be a string": {
        'es': "'op' debe ser una cadena",
        'fr': "'op' doit être une chaîne",
        'de': "'op' muss eine Zeichenkette sein",
        'pt': "'op' tem de ser uma cadeia de texto",
        'it': "'op' deve essere una stringa",
        'ja': "'op' は文字列である必要があります",
        'zh': "'op' 必须是字符串",
        'hi': "'op' एक स्ट्रिंग होना चाहिए",
        'ar': "يجب أن يكون 'op' نصًا",
    },
    "'problems' must be a non-empty list": {
        'es': "'problems' debe ser una lista no vacía",
        'fr': "'problems' doit être une liste non vide",
        'de': "'problems' muss eine nicht leere Liste sein",
        'pt': "'problems' tem de ser uma lista não vazia",
        'it': "'problems' deve essere un elenco non vuoto",
        'ja': "'problems' は空でないリストである必要があります",
        'zh': "'problems' 必须是非空列表",
        'hi': "'problems' एक ग़ैर-ख़ाली सूची होनी चाहिए",
        'ar': "يجب أن يكون 'problems' قائمة غير فارغة",
    },
    "'status' must be an HTTP status code (0 for no answer)": {
        'es': "'status' debe ser un código de estado HTTP (0 si no hubo respuesta)",
        'fr': "'status' doit être un code d'état HTTP (0 si aucune réponse)",
        'de': "'status' muss ein HTTP-Statuscode sein (0 für keine Antwort)",
        'pt': "'status' tem de ser um código de estado HTTP (0 se não houve resposta)",
        'it': "'status' deve essere un codice di stato HTTP (0 se nessuna risposta)",
        'ja': "'status' は HTTP ステータスコードである必要があります（応答なしは 0）",
        'zh': "'status' 必须是 HTTP 状态码（无响应填 0）",
        'hi': "'status' एक HTTP स्टेटस कोड होना चाहिए (कोई उत्तर न मिलने पर 0)",
        'ar': "يجب أن يكون 'status' رمز حالة HTTP (0 عند عدم وجود ردّ)",
    },
    'JIM_SITE_ROTA must be a JSON list of shifts': {
        'es': 'JIM_SITE_ROTA debe ser una lista JSON de turnos',
        'fr': 'JIM_SITE_ROTA doit être une liste JSON de gardes',
        'de': 'JIM_SITE_ROTA muss eine JSON-Liste von Schichten sein',
        'pt': 'JIM_SITE_ROTA tem de ser uma lista JSON de turnos',
        'it': 'JIM_SITE_ROTA deve essere un elenco JSON di turni',
        'ja': 'JIM_SITE_ROTA はシフトの JSON リストである必要があります',
        'zh': 'JIM_SITE_ROTA 必须是班次的 JSON 列表',
        'hi': 'JIM_SITE_ROTA शिफ़्टों की JSON सूची होनी चाहिए',
        'ar': 'يجب أن يكون JIM_SITE_ROTA قائمة JSON من المناوبات',
    },
    'QRME did not recognize that organization with this token': {
        'es': 'QRME no reconoció esa organización con este token',
        'fr': "QRME n'a pas reconnu cette organisation avec ce jeton",
        'de': 'QRME hat diese Organisation mit diesem Token nicht erkannt',
        'pt': 'O QRME não reconheceu essa organização com este token',
        'it': "QRME non ha riconosciuto quell'organizzazione con questo token",
        'ja': 'QRME はこのトークンでその組織を認識できませんでした',
        'zh': 'QRME 无法用此令牌识别该组织',
        'hi': 'QRME ने इस टोकन के साथ उस संगठन को नहीं पहचाना',
        'ar': 'لم يتعرّف QRME على تلك المؤسسة بهذا الرمز',
    },
    'QRME refused the coordination — the link may be stale; relink with a fresh owner token': {
        'es': 'QRME rechazó la coordinación: el enlace puede estar caducado; vuelve a enlazar con un token de propietario nuevo',
        'fr': 'QRME a refusé la coordination — le lien est peut-être périmé ; relie avec un nouveau jeton de propriétaire',
        'de': 'QRME hat die Koordination abgelehnt — die Verknüpfung ist vielleicht veraltet; verknüpfe neu mit einem frischen Besitzer-Token',
        'pt': 'O QRME recusou a coordenação — a ligação pode estar desactualizada; volta a ligar com um token de proprietário novo',
        'it': 'QRME ha rifiutato il coordinamento — il collegamento potrebbe essere scaduto; ricollega con un token proprietario nuovo',
        'ja': 'QRME が連携を拒否しました — リンクが古い可能性があります。新しいオーナートークンで再リンクしてください',
        'zh': 'QRME 拒绝了此次协调 — 链接可能已失效；请用新的所有者令牌重新关联',
        'hi': 'QRME ने समन्वय अस्वीकार किया — लिंक पुराना हो सकता है; नए ओनर टोकन से दोबारा जोड़ो',
        'ar': 'رفض QRME التنسيق — قد تكون الوصلة قديمة؛ أعِد الربط برمز مالك جديد',
    },
    'a band must have a width above zero': {
        'es': 'una banda debe tener un ancho mayor que cero',
        'fr': 'une bande doit avoir une largeur supérieure à zéro',
        'de': 'ein Band muss eine Breite über null haben',
        'pt': 'uma banda tem de ter uma largura acima de zero',
        'it': 'una banda deve avere una larghezza maggiore di zero',
        'ja': '帯には 0 より大きい幅が必要です',
        'zh': '区间的宽度必须大于零',
        'hi': 'बैंड की चौड़ाई शून्य से अधिक होनी चाहिए',
        'ar': 'يجب أن يكون عرض النطاق أكبر من صفر',
    },
    'a mail server host is required': {
        'es': 'se requiere un host de servidor de correo',
        'fr': 'un hôte de serveur de messagerie est requis',
        'de': 'ein Mailserver-Host ist erforderlich',
        'pt': 'é necessário um host de servidor de correio',
        'it': 'è richiesto un host del server di posta',
        'ja': 'メールサーバーのホストが必要です',
        'zh': '需要一个邮件服务器主机',
        'hi': 'मेल सर्वर होस्ट ज़रूरी है',
        'ar': 'يلزم مضيف خادم بريد',
    },
    'a message needs words': {
        'es': 'un mensaje necesita palabras',
        'fr': 'un message a besoin de mots',
        'de': 'eine Nachricht braucht Worte',
        'pt': 'uma mensagem precisa de palavras',
        'it': 'un messaggio ha bisogno di parole',
        'ja': 'メッセージには言葉が必要です',
        'zh': '消息需要内容',
        'hi': 'संदेश में शब्द चाहिए',
        'ar': 'الرسالة تحتاج كلمات',
    },
    'a savings goal is a positive number': {
        'es': 'una meta de ahorro es un número positivo',
        'fr': "un objectif d'épargne est un nombre positif",
        'de': 'ein Sparziel ist eine positive Zahl',
        'pt': 'um objectivo de poupança é um número positivo',
        'it': 'un obiettivo di risparmio è un numero positivo',
        'ja': '貯蓄目標は正の数です',
        'zh': '储蓄目标是一个正数',
        'hi': 'बचत का लक्ष्य एक धनात्मक संख्या है',
        'ar': 'هدف الادّخار رقم موجب',
    },
    'a theme color is a hex code like #10251c': {
        'es': 'un color de tema es un código hexadecimal como #10251c',
        'fr': 'une couleur de thème est un code hexadécimal comme #10251c',
        'de': 'eine Themenfarbe ist ein Hex-Code wie #10251c',
        'pt': 'uma cor de tema é um código hexadecimal como #10251c',
        'it': 'un colore del tema è un codice esadecimale come #10251c',
        'ja': 'テーマ色は #10251c のような16進コードです',
        'zh': '主题颜色是形如 #10251c 的十六进制代码',
        'hi': 'थीम का रंग #10251c जैसा हेक्स कोड होता है',
        'ar': 'لون السمة رمز ست عشري مثل \u200e#10251c',
    },
    'an error report is an object': {
        'es': 'un informe de error es un objeto',
        'fr': "un rapport d'erreur est un objet",
        'de': 'ein Fehlerbericht ist ein Objekt',
        'pt': 'um relatório de erro é um objecto',
        'it': 'una segnalazione di errore è un oggetto',
        'ja': 'エラーレポートはオブジェクトです',
        'zh': '错误报告是一个对象',
        'hi': 'त्रुटि रिपोर्ट एक ऑब्जेक्ट है',
        'ar': 'تقرير الخطأ كائن',
    },
    'each problem is an object': {
        'es': 'cada problema es un objeto',
        'fr': 'chaque problème est un objet',
        'de': 'jedes Problem ist ein Objekt',
        'pt': 'cada problema é um objecto',
        'it': 'ogni problema è un oggetto',
        'ja': '各問題はオブジェクトです',
        'zh': '每个问题都是一个对象',
        'hi': 'हर समस्या एक ऑब्जेक्ट है',
        'ar': 'كل مشكلة كائن',
    },
    'links start with http:// or https://': {
        'es': 'los enlaces empiezan por http:// o https://',
        'fr': 'les liens commencent par http:// ou https://',
        'de': 'Links beginnen mit http:// oder https://',
        'pt': 'as ligações começam por http:// ou https://',
        'it': 'i link iniziano con http:// o https://',
        'ja': 'リンクは http:// または https:// で始まります',
        'zh': '链接以 http:// 或 https:// 开头',
        'hi': 'लिंक http:// या https:// से शुरू होते हैं',
        'ar': 'تبدأ الروابط بـ \u200ehttp://\u200e أو \u200ehttps://\u200e',
    },
    'when is an ISO timestamp, e.g. 2026-08-05T15:00:00+00:00': {
        'es': 'when es una marca de tiempo ISO, p. ej. 2026-08-05T15:00:00+00:00',
        'fr': 'when est un horodatage ISO, par ex. 2026-08-05T15:00:00+00:00',
        'de': 'when ist ein ISO-Zeitstempel, z. B. 2026-08-05T15:00:00+00:00',
        'pt': 'when é uma marca temporal ISO, p. ex. 2026-08-05T15:00:00+00:00',
        'it': 'when è un timestamp ISO, ad es. 2026-08-05T15:00:00+00:00',
        'ja': 'when は ISO 形式のタイムスタンプです。例：2026-08-05T15:00:00+00:00',
        'zh': 'when 是 ISO 时间戳，例如 2026-08-05T15:00:00+00:00',
        'hi': 'when एक ISO टाइमस्टैम्प है, जैसे 2026-08-05T15:00:00+00:00',
        'ar': '\u200fwhen طابع زمني بصيغة ISO، مثل \u200e2026-08-05T15:00:00+00:00',
    },
    'relationship must be parent or legal_guardian': {
        'es': 'relationship debe ser parent o legal_guardian',
        'fr': 'relationship doit être parent ou legal_guardian',
        'de': 'relationship muss parent oder legal_guardian sein',
        'pt': 'relationship tem de ser parent ou legal_guardian',
        'it': 'relationship deve essere parent o legal_guardian',
        'ja': 'relationship は parent または legal_guardian である必要があります',
        'zh': 'relationship 必须是 parent 或 legal_guardian',
        'hi': 'relationship या तो parent होना चाहिए या legal_guardian',
        'ar': 'يجب أن تكون relationship إمّا parent أو legal_guardian',
    },
    'the capture is empty': {
        'es': 'la captura está vacía',
        'fr': 'la capture est vide',
        'de': 'die Aufnahme ist leer',
        'pt': 'a captura está vazia',
        'it': "l'acquisizione è vuota",
        'ja': '取り込んだ内容が空です',
        'zh': '这次采集是空的',
        'hi': 'कैप्चर ख़ाली है',
        'ar': 'الالتقاط فارغ',
    },
    'frame_base64 is not valid base64': {
        'es': 'frame_base64 no es base64 válido',
        'fr': "frame_base64 n'est pas du base64 valide",
        'de': 'frame_base64 ist kein gültiges Base64',
        'pt': 'frame_base64 não é base64 válido',
        'it': 'frame_base64 non è base64 valido',
        'ja': 'frame_base64 は有効な base64 ではありません',
        'zh': 'frame_base64 不是有效的 base64',
        'hi': 'frame_base64 मान्य base64 नहीं है',
        'ar': 'frame_base64 ليس ترميز base64 صالحًا',
    },
    'there was no frame in that': {
        'es': 'no había ningún fotograma en eso',
        'fr': "il n'y avait aucune image là-dedans",
        'de': 'darin war kein Bild',
        'pt': 'não havia nenhum fotograma nisso',
        'it': 'in quello non c\'era alcun fotogramma',
        'ja': 'そこにはフレームがありませんでした',
        'zh': '那里面没有画面',
        'hi': 'उसमें कोई फ़्रेम नहीं था',
        'ar': 'لم يكن هناك أي إطار في ذلك',
    },
    'nothing is set up to look: this deployment has no key for describing what a camera or a screen sees. The monitor stays switched on and reports nothing until one is added': {
        'es': 'no hay nada configurado para mirar: esta instalación no tiene clave para describir lo que ve una cámara o una pantalla. El monitor sigue encendido y no informa de nada hasta que se añada una',
        'fr': "rien n'est configuré pour regarder : cette installation n'a pas de clé pour décrire ce que voit une caméra ou un écran. Le capteur reste allumé et ne rapporte rien tant qu'on n'en ajoute pas une",
        'de': 'nichts ist zum Schauen eingerichtet: diese Installation hat keinen Schlüssel, um zu beschreiben, was eine Kamera oder ein Bildschirm sieht. Der Melder bleibt eingeschaltet und meldet nichts, bis einer hinzugefügt wird',
        'pt': 'nada está configurado para ver: esta instalação não tem chave para descrever o que uma câmara ou um ecrã vê. O monitor continua ligado e não reporta nada até que se adicione uma',
        'it': 'non c\'è nulla configurato per guardare: questa installazione non ha una chiave per descrivere ciò che una telecamera o uno schermo vede. Il sensore resta acceso e non riporta nulla finché non ne viene aggiunta una',
        'ja': '見るための設定がありません。この配備には、カメラや画面が見ているものを説明するための鍵がありません。モニターは入ったままで、鍵が追加されるまで何も報告しません',
        'zh': '没有任何东西被配置为观看：此部署没有用于描述摄像头或屏幕所见内容的密钥。该监测项保持开启，在添加密钥之前不会报告任何内容',
        'hi': 'देखने के लिए कुछ भी सेट नहीं है: इस परिनियोजन के पास यह बताने की कुंजी नहीं है कि कैमरा या स्क्रीन क्या देख रहा है। मॉनिटर चालू रहेगा और कुंजी जुड़ने तक कुछ भी रिपोर्ट नहीं करेगा',
        'ar': 'لا شيء مُهيَّأ للنظر: هذا النشر لا يملك مفتاحًا لوصف ما تراه كاميرا أو شاشة. يبقى المِرقاب مشغَّلًا ولا يبلّغ عن شيء حتى يُضاف مفتاح',
    },
    'a moment is either the words or the frame it was read from, not both': {
        'es': 'un momento son las palabras o el fotograma del que se leyeron, no ambos',
        'fr': "un moment, ce sont les mots ou l'image dont ils ont été tirés, pas les deux",
        'de': 'ein Moment sind die Worte oder das Bild, aus dem sie gelesen wurden — nicht beides',
        'pt': 'um momento são as palavras ou o fotograma de onde foram lidas, não ambos',
        'it': 'un momento sono le parole oppure il fotogramma da cui sono state lette, non entrambi',
        'ja': '一つの瞬間は、言葉か、その読み取り元のフレームのどちらかであって、両方ではありません',
        'zh': '一个瞬间要么是文字，要么是读出文字的那一帧，不能两者兼有',
        'hi': 'एक क्षण या तो शब्द है या वह फ़्रेम जिससे वे पढ़े गए — दोनों नहीं',
        'ar': 'اللحظة إمّا الكلمات وإمّا الإطار الذي قُرئت منه، لا الاثنان معًا',
    },
    'no such monitor': {
        'es': 'no existe ese monitor',
        'fr': "ce capteur n'existe pas",
        'de': 'diesen Melder gibt es nicht',
        'pt': 'não existe esse monitor',
        'it': 'quel sensore non esiste',
        'ja': 'そのモニターはありません',
        'zh': '没有这个监测项',
        'hi': 'ऐसा कोई मॉनिटर नहीं है',
        'ar': 'لا يوجد مِرقاب بهذا الاسم',
    },
    'nothing is attached as channel 2, so there is no second microphone to have heard this. Attach a worn microphone first': {
        'es': 'no hay nada conectado como canal 2, así que no existe un segundo micrófono que haya podido oír esto. Conecta primero un micrófono que se lleve puesto',
        'fr': "rien n'est attaché comme canal 2, il n'y a donc pas de second microphone qui aurait pu entendre cela. Attachez d'abord un microphone porté sur soi",
        'de': 'nichts ist als Kanal 2 angeschlossen, also gibt es kein zweites Mikrofon, das dies gehört haben könnte. Schließe zuerst ein getragenes Mikrofon an',
        'pt': 'nada está ligado como canal 2, por isso não existe um segundo microfone que pudesse ter ouvido isto. Ligue primeiro um microfone que se use no corpo',
        'it': 'nulla è collegato come canale 2, quindi non esiste un secondo microfono che possa aver sentito questo. Collega prima un microfono indossato',
        'ja': 'チャンネル2として何も接続されていないため、これを聞いた第2のマイクは存在しません。まず身につけるマイクを接続してください',
        'zh': '没有任何设备作为第二通道接入，因此不存在能听到这段话的第二个麦克风。请先接入一个佩戴式麦克风',
        'hi': 'चैनल 2 के रूप में कुछ भी जुड़ा नहीं है, इसलिए ऐसा कोई दूसरा माइक्रोफ़ोन नहीं है जिसने यह सुना हो। पहले पहना जाने वाला माइक्रोफ़ोन जोड़ें',
        'ar': 'لا شيء متصل كقناة ثانية، لذا لا يوجد ميكروفون ثانٍ يمكن أن يكون قد سمع هذا. صِل أولًا ميكروفونًا يُرتدى',
    },
    'the agent is not listening on channel 2 right now. A microphone delivers what it heard during a handover, not outside one — hand the channel over first, and it will be recorded with the reason it was lent': {
        'es': 'el agente no está escuchando por el canal 2 en este momento. Un micrófono entrega lo que oyó durante una cesión, no fuera de ella — cede primero el canal y quedará registrado con el motivo por el que se prestó',
        'fr': "l'agent n'écoute pas sur le canal 2 en ce moment. Un microphone remet ce qu'il a entendu pendant une cession, pas en dehors — cédez d'abord le canal, et ce sera enregistré avec la raison du prêt",
        'de': 'der Agent hört gerade nicht auf Kanal 2. Ein Mikrofon liefert, was es während einer Übergabe gehört hat, nicht außerhalb davon — übergib den Kanal zuerst, und es wird mit dem Grund der Leihe festgehalten',
        'pt': 'o agente não está a ouvir no canal 2 neste momento. Um microfone entrega o que ouviu durante uma cedência, não fora dela — ceda primeiro o canal e ficará registado com o motivo pelo qual foi emprestado',
        'it': "l'agente non sta ascoltando sul canale 2 in questo momento. Un microfono consegna ciò che ha sentito durante una cessione, non al di fuori — cedi prima il canale e verrà registrato con il motivo del prestito",
        'ja': '今、エージェントはチャンネル2で聞いていません。マイクは引き渡しの間に聞いたものを渡すのであって、その外では渡しません — まずチャンネルを引き渡してください。貸した理由とともに記録されます',
        'zh': '此刻代理并未在第二通道上聆听。麦克风交付的是移交期间听到的内容，而非移交之外的内容 — 请先移交通道，系统会连同出借原因一并记录',
        'hi': 'अभी एजेंट चैनल 2 पर नहीं सुन रहा है। माइक्रोफ़ोन वही सौंपता है जो उसने सौंपे जाने की अवधि में सुना, उसके बाहर का नहीं — पहले चैनल सौंपें, और यह उस कारण सहित दर्ज होगा जिसके लिए उसे दिया गया',
        'ar': 'الوكيل لا يستمع على القناة 2 الآن. الميكروفون يسلّم ما سمعه أثناء التسليم، لا خارجه — سلّم القناة أولًا، وسيُسجَّل مع سبب إعارتها',
    },
    'nothing arrived in that — an empty delivery is not something the microphone heard': {
        'es': 'no llegó nada en eso — una entrega vacía no es algo que el micrófono haya oído',
        'fr': "rien n'est arrivé là-dedans — une remise vide n'est pas quelque chose que le microphone a entendu",
        'de': 'darin kam nichts an — eine leere Lieferung ist nichts, was das Mikrofon gehört hat',
        'pt': 'não chegou nada nisso — uma entrega vazia não é algo que o microfone tenha ouvido',
        'it': 'in quello non è arrivato nulla — una consegna vuota non è qualcosa che il microfono abbia sentito',
        'ja': 'そこには何も届いていません — 空の受け渡しは、マイクが聞いたものではありません',
        'zh': '那里面什么也没送到 — 空的交付并不是麦克风听到的东西',
        'hi': 'उसमें कुछ नहीं आया — खाली सुपुर्दगी वह नहीं है जो माइक्रोफ़ोन ने सुना हो',
        'ar': 'لم يصل شيء في ذلك — التسليم الفارغ ليس شيئًا سمعه الميكروفون',
    },
    'a low-balance floor is a positive amount — send null to go back to the derived default': {
        'es': 'el suelo de saldo bajo es una cantidad positiva — envía null para volver al valor derivado',
        'fr': 'le plancher de solde bas est un montant positif — envoyez null pour revenir à la valeur dérivée',
        'de': 'die Untergrenze für den Kontostand ist ein positiver Betrag — senden Sie null, um zum abgeleiteten Standard zurückzukehren',
        'pt': 'o piso de saldo baixo é um montante positivo — envie null para voltar ao valor derivado',
        'it': 'la soglia di saldo basso è un importo positivo — invia null per tornare al valore derivato',
        'ja': '残高の下限は正の金額です — 導出された既定値に戻すには null を送ってください',
        'zh': '低余额下限必须是正数 — 发送 null 可回到派生的默认值',
        'hi': 'न्यून शेष की सीमा एक धनात्मक राशि है — व्युत्पन्न डिफ़ॉल्ट पर लौटने के लिए null भेजें',
        'ar': 'الحد الأدنى للرصيد مبلغ موجب — أرسل null للعودة إلى القيمة المشتقة',
    },
    'that does not look like an email address': {
        'es': 'eso no parece una dirección de correo',
        'fr': "cela ne ressemble pas à une adresse e-mail",
        'de': 'das sieht nicht wie eine E-Mail-Adresse aus',
        'pt': 'isso não parece um endereço de e-mail',
        'it': 'questo non sembra un indirizzo email',
        'ja': 'メールアドレスの形式ではないようです',
        'zh': '这看起来不像一个邮箱地址',
        'hi': 'यह ईमेल पते जैसा नहीं लगता',
        'ar': 'هذا لا يبدو كعنوان بريد إلكتروني',
    },
    'no such lookout': {
        'es': 'no existe esa vigilancia',
        'fr': 'aucune surveillance de ce nom',
        'de': 'keine solche Beobachtung',
        'pt': 'não existe essa vigilância',
        'it': 'nessuna sorveglianza di questo tipo',
        'ja': 'そのような見守りはありません',
        'zh': '没有该关注项',
        'hi': 'ऐसी कोई निगरानी नहीं',
        'ar': 'لا توجد مراقبة بهذا الوصف',
    },
    'the lookout needs the standing study permit — grant it under Permissions': {
        'es': 'la vigilancia necesita el permiso de estudio permanente — concédelo en Permisos',
        'fr': "la surveillance nécessite le permis d'étude permanent — accordez-le sous Permissions",
        'de': 'die Beobachtung braucht die stehende Studien-Erlaubnis — erteile sie unter Berechtigungen',
        'pt': 'a vigilância precisa da permissão de estudo permanente — conceda-a em Permissões',
        'it': 'la sorveglianza richiede il permesso di studio permanente — concedilo in Permessi',
        'ja': '見守りには常設の学習許可が必要です — 「許可」から付与してください',
        'zh': '关注功能需要常设学习许可——请在“权限”中授予',
        'hi': 'निगरानी के लिए स्थायी अध्ययन अनुमति चाहिए — इसे अनुमतियों में दें',
        'ar': 'تحتاج المراقبة إلى إذن الدراسة الدائم — امنحه من قسم الأذونات',
    },
    "no such call": {
        'es': "no existe esa llamada",
        'fr': "aucun appel de ce type",
        'de': "dieses Gespräch gibt es nicht",
        'pt': "não existe essa chamada",
        'it': "questa chiamata non esiste",
        'ja': "そのような通話はありません",
        'zh': "没有这通通话",
        'hi': "ऐसी कोई कॉल नहीं है",
        'ar': "لا توجد مكالمة كهذه",
    },
    # -- two guardians working together (jim/liaison.py) ---------------------
    "these two are not each other's contacts — a guardian only reaches another when both people already had the other, and one side alone reaches nothing": {
        'es': "estas dos personas no son contactos entre sí: un guardián solo alcanza a otro cuando cada una ya tenía a la otra, y un solo lado no alcanza nada",
        'fr': "ces deux personnes ne sont pas en contact : un gardien n'en atteint un autre que si chacune avait déjà l'autre, et un seul côté n'atteint rien",
        'de': "diese beiden sind keine Kontakte: ein Wächter erreicht einen anderen nur, wenn beide den anderen schon hatten — eine Seite allein erreicht nichts",
        'pt': "estas duas pessoas não são contactos uma da outra: um guardião só alcança outro quando ambas já tinham a outra, e um só lado não alcança nada",
        'it': "queste due persone non sono contatti: un guardiano ne raggiunge un altro solo se entrambe avevano già l'altra, e un lato solo non raggiunge nulla",
        'ja': "このお二人は互いの連絡先ではありません。ガーディアンが別のガーディアンに届くのは双方がすでに相手を登録している場合だけで、片側だけでは何にも届きません",
        'zh': "这两人并非彼此的联系人：只有双方原本都存有对方，一位守护者才能触及另一位；单方面则触及不到任何东西",
        'hi': "ये दोनों एक-दूसरे के संपर्क नहीं हैं — एक गार्जियन दूसरे तक तभी पहुँचता है जब दोनों ने पहले से एक-दूसरे को रखा हो; अकेला एक पक्ष कहीं नहीं पहुँचता",
        'ar': "هذان ليسا جهتَي اتصال لبعضهما — لا يصل حارس إلى آخر إلا إذا كان كلاهما يحتفظ بالآخر أصلًا، والطرف الواحد وحده لا يصل إلى شيء",
    },
    "this guardian has not been allowed to handle what it notices on its own — turn it on in what it may do for you, where it says what it looks at and what it does about it": {
        'es': "este guardián no tiene permiso para ocuparse por su cuenta de lo que detecta: actívalo en lo que puede hacer por ti, donde dice qué observa y qué hace al respecto",
        'fr': "ce gardien n'a pas le droit de traiter seul ce qu'il remarque — activez-le dans ce qu'il peut faire pour vous, où il est dit ce qu'il observe et ce qu'il en fait",
        'de': "dieser Wächter darf sich nicht selbstständig um das kümmern, was ihm auffällt — schalte es dort frei, wo steht, worauf er achtet und was er damit tut",
        'pt': "este guardião não tem permissão para tratar sozinho do que repara — ative-o no que ele pode fazer por si, onde diz o que observa e o que faz a respeito",
        'it': "questo guardiano non ha il permesso di occuparsi da solo di ciò che nota: attivalo in ciò che può fare per te, dove dice cosa osserva e cosa ne fa",
        'ja': "このガーディアンは、気づいたことに自分だけで対処する許可を得ていません。「あなたのためにできること」で有効にしてください。そこに、何を見ていて、それに対して何をするかが書かれています",
        'zh': "这位守护者尚未获准自行处理它注意到的情况 — 请在「它可以为你做什么」中开启，那里写明了它会关注什么、又会如何应对",
        'hi': "इस अभिभावक को यह अनुमति नहीं मिली है कि जो वह नोटिस करे उसे अपने आप सँभाले — इसे \"यह आपके लिए क्या कर सकता है\" में चालू करें, जहाँ लिखा है कि यह क्या देखता है और उसके बारे में क्या करता है",
        'ar': "لم يُسمح لهذا الحارس بمعالجة ما يلاحظه من تلقاء نفسه — فعّله في ما يمكنه فعله لك، حيث يُذكر ما الذي يراقبه وما الذي يفعله حياله",
    },
    "these two are not each other's contacts — a channel pairs only where both people already had the other, and one side alone pairs with nothing": {
        'es': "estas dos personas no son contactos entre sí: un canal se empareja solo cuando cada una ya tenía a la otra, y un solo lado no se empareja con nada",
        'fr': "ces deux personnes ne sont pas en contact : un canal ne s'apparie que si chacune avait déjà l'autre, et un seul côté ne s'apparie avec rien",
        'de': "diese beiden sind keine Kontakte: ein Kanal paart sich nur, wenn beide den anderen schon hatten — eine Seite allein paart sich mit nichts",
        'pt': "estas duas pessoas não são contactos uma da outra: um canal só emparelha quando ambas já tinham a outra, e um só lado não emparelha com nada",
        'it': "queste due persone non sono contatti: un canale si accoppia solo se entrambe avevano già l'altra, e un lato solo non si accoppia con nulla",
        'ja': "このお二人は互いの連絡先ではありません。チャンネルが対になるのは双方がすでに相手を登録している場合だけで、片側だけでは何とも対になりません",
        'zh': "这两人并非彼此的联系人：只有双方原本都存有对方，通道才能配对；单方面配不上任何东西",
        'hi': "ये दोनों एक-दूसरे के संपर्क नहीं हैं — चैनल तभी जुड़ता है जब दोनों ने पहले से एक-दूसरे को रखा हो; अकेला एक पक्ष किसी से नहीं जुड़ता",
        'ar': "هذان ليسا جهتَي اتصال لبعضهما — لا تقترن قناة إلا إذا كان كلاهما يحتفظ بالآخر أصلًا، والطرف الواحد وحده لا يقترن بشيء",
    },
    "your agent is not listening on a second microphone yet — hand one over first, and then say who else is on the call": {
        'es': "tu agente aún no está escuchando por un segundo micrófono: préstale uno primero y después di quién más está en la llamada",
        'fr': "votre agent n'écoute pas encore sur un second microphone — prêtez-lui-en un d'abord, puis dites qui d'autre est en ligne",
        'de': "dein Agent hört noch nicht über ein zweites Mikrofon mit — leih ihm zuerst eines, und sag dann, wer sonst im Gespräch ist",
        'pt': "o seu agente ainda não está a ouvir por um segundo microfone — empreste-lhe um primeiro e depois diga quem mais está na chamada",
        'it': "il tuo agente non sta ancora ascoltando su un secondo microfono: prestagliene uno prima, e poi dì chi altro è in chiamata",
        'ja': "エージェントはまだ第2のマイクで聞いていません。先に1つ貸してから、通話に誰がいるかを伝えてください",
        'zh': "你的助理还没有在第二个麦克风上收听 — 先借出一个，再说明通话中还有谁",
        'hi': "आपका एजेंट अभी दूसरे माइक्रोफ़ोन पर नहीं सुन रहा — पहले एक सौंपें, फिर बताएँ कि कॉल पर और कौन है",
        'ar': "وكيلك لا يستمع بعد عبر ميكروفون ثانٍ — أعِره واحدًا أولًا، ثم قل من غيرك في المكالمة",
    },
    "that stretch belongs to somebody else": {
        'es': "ese tramo pertenece a otra persona",
        'fr': "cette plage appartient à quelqu'un d'autre",
        'de': "dieser Abschnitt gehört jemand anderem",
        'pt': "esse período pertence a outra pessoa",
        'it': "quell'intervallo appartiene a un'altra persona",
        'ja': "その時間帯は別の人のものです",
        'zh': "该时段属于其他人",
        'hi': "वह अवधि किसी और की है",
        'ar': "تلك الفترة تخص شخصًا آخر",
    },
    "no such stretch": {
        'es': "no existe ese tramo",
        'fr': "cette plage n'existe pas",
        'de': "diesen Abschnitt gibt es nicht",
        'pt': "não existe esse período",
        'it': "quell'intervallo non esiste",
        'ja': "その時間帯はありません",
        'zh': "没有这个时段",
        'hi': "ऐसी कोई अवधि नहीं है",
        'ar': "لا توجد فترة كهذه",
    },
    "no such moment": {
        'es': "no existe ese momento",
        'fr': "cet instant n'existe pas",
        'de': "diesen Moment gibt es nicht",
        'pt': "não existe esse momento",
        'it': "quel momento non esiste",
        'ja': "その記録はありません",
        'zh': "没有这个时刻",
        'hi': "ऐसा कोई क्षण नहीं है",
        'ar': "لا توجد لحظة كهذه",
    },
    "there is no task on this link yet — one side names the work first, and the other agrees to it": {
        'es': "todavía no hay ninguna tarea en este enlace: una parte nombra el trabajo primero y la otra lo acepta",
        'fr': "il n'y a encore aucune tâche sur ce lien : un côté nomme le travail d'abord, et l'autre l'accepte",
        'de': "auf dieser Verbindung gibt es noch keine Aufgabe — eine Seite benennt die Arbeit zuerst, die andere stimmt ihr zu",
        'pt': "ainda não há nenhuma tarefa nesta ligação: um lado nomeia o trabalho primeiro e o outro concorda com ele",
        'it': "su questo collegamento non c'è ancora alcun compito: un lato nomina il lavoro per primo e l'altro lo accetta",
        'ja': "このリンクにはまだタスクがありません。まず一方が作業に名前をつけ、もう一方がそれに同意します",
        'zh': "这条链接上还没有任务：先由一方为这项工作命名，另一方再表示同意",
        'hi': "इस कड़ी पर अभी कोई कार्य नहीं है — पहले एक पक्ष काम को नाम देता है, और दूसरा उससे सहमत होता है",
        'ar': "لا توجد بعد أي مهمة على هذه الصلة — يسمّي أحد الطرفين العمل أولًا، ثم يوافق عليه الطرف الآخر",
    },
    "your guardian has not been allowed to speak for you to somebody else's — turn it on in what it may do for you, where it says what it may say": {
        'es': "tu guardián no tiene permiso para hablar por ti con el de otra persona: actívalo en lo que puede hacer por ti, donde dice qué puede decir",
        'fr': "votre gardien n'a pas le droit de parler en votre nom à celui de quelqu'un d'autre — activez-le dans ce qu'il peut faire pour vous, où il est dit ce qu'il peut dire",
        'de': "dein Wächter darf nicht in deinem Namen mit dem eines anderen sprechen — schalte es dort frei, wo steht, was er für dich tun und sagen darf",
        'pt': "o seu guardião não foi autorizado a falar por si com o de outra pessoa — ative-o no que ele pode fazer por si, onde diz o que pode dizer",
        'it': "il tuo guardiano non è autorizzato a parlare per te con quello di un altro: attivalo in ciò che può fare per te, dove dice cosa può dire",
        'ja': "あなたのガーディアンは、他の人のガーディアンにあなたの代わりに話す許可を得ていません。「あなたのためにできること」で有効にしてください。何を言えるかもそこに書かれています",
        'zh': "你的守护者尚未获准代表你与他人的守护者交谈——请在“它能为你做什么”中开启，那里写明了它可以说什么",
        'hi': "आपके गार्जियन को किसी और के गार्जियन से आपकी ओर से बात करने की अनुमति नहीं है — «यह आपके लिए क्या कर सकता है» में इसे चालू कीजिए, जहाँ लिखा है कि यह क्या कह सकता है",
        'ar': "لم يُسمح لحارسك بأن يتحدث نيابة عنك إلى حارس شخص آخر — فعّله في «ما يمكنه فعله من أجلك»، حيث يُذكر ما يمكنه قوله",
    },
    "no such link": {
        'es': "no existe ese enlace", 'fr': "aucune liaison de ce type",
        'de': "diese Verbindung gibt es nicht", 'pt': "não existe essa ligação",
        'it': "questo collegamento non esiste", 'ja': "そのようなリンクはありません",
        'zh': "没有这条连接", 'hi': "ऐसा कोई लिंक नहीं है",
        'ar': "لا توجد صلة كهذه",
    },
    "that link has closed": {
        'es': "ese enlace ya se ha cerrado", 'fr': "cette liaison est fermée",
        'de': "diese Verbindung ist geschlossen", 'pt': "essa ligação já fechou",
        'it': "quel collegamento è chiuso", 'ja': "そのリンクは終了しています",
        'zh': "该连接已经结束", 'hi': "वह लिंक बंद हो चुका है",
        'ar': "أُغلقت تلك الصلة",
    },
    "that link is between two other people": {
        'es': "ese enlace es entre otras dos personas",
        'fr': "cette liaison est entre deux autres personnes",
        'de': "diese Verbindung besteht zwischen zwei anderen Menschen",
        'pt': "essa ligação é entre duas outras pessoas",
        'it': "quel collegamento è tra due altre persone",
        'ja': "そのリンクは別の二人のあいだのものです",
        'zh': "那条连接属于另外两个人",
        'hi': "वह लिंक दो अन्य लोगों के बीच है",
        'ar': "تلك الصلة بين شخصين آخرين",
    },
    "say what the task is, in one line": {
        'es': "di cuál es el trabajo, en una línea",
        'fr': "dites en une ligne quel est le travail",
        'de': "sag in einer Zeile, worum es bei der Arbeit geht",
        'pt': "diga qual é o trabalho, numa linha",
        'it': "di' qual è il lavoro, in una riga",
        'ja': "その作業が何かを一行で書いてください",
        'zh': "用一句话说明这项工作是什么",
        'hi': "एक पंक्ति में बताइए कि काम क्या है",
        'ar': "قل ما هو العمل، في سطر واحد",
    },
    # -- this person's own address book (jim/contacts.py) --------------------
    # -- the people in your phone (jim/contacts.py) --------------------------
    "nothing here can see the people in your phone: turn on contacts in what the agent may see. It is off until you do, because most of what is in there is somebody else": {
        'es': "aquí nada puede ver a las personas de tu teléfono: activa los contactos en lo que el agente puede ver. Está desactivado hasta que lo hagas, porque casi todo lo que hay ahí es otra gente",
        'fr': "rien ici ne peut voir les personnes de votre téléphone : activez les contacts dans ce que l'agent peut voir. C'est désactivé jusque-là, car l'essentiel de ce qui s'y trouve concerne d'autres gens",
        'de': "hier kann nichts die Menschen in deinem Telefon sehen: schalte Kontakte in dem ein, was der Agent sehen darf. Bis dahin ist es aus, denn das meiste darin sind andere Leute",
        'pt': "aqui nada consegue ver as pessoas do seu telefone: ative os contactos naquilo que o agente pode ver. Está desligado até o fazer, porque quase tudo o que está lá é outra gente",
        'it': "qui nulla può vedere le persone nel tuo telefono: attiva i contatti in ciò che l'agente può vedere. Resta spento finché non lo fai, perché quasi tutto ciò che c'è dentro riguarda altri",
        'ja': "ここからは電話帳の人たちを見ることはできません。エージェントが見てよいものの中で連絡先を有効にしてください。有効にするまでは切ったままです。そこにあるものの大半は他人のものだからです",
        'zh': "这里无法看到你手机里的人：请在「代理可以看到的内容」中开启通讯录。在你开启之前它一直是关闭的，因为里面绝大部分是别人的信息",
        'hi': "यहाँ से आपके फ़ोन के लोग नहीं दिखते: एजेंट जो देख सकता है, उसमें संपर्क चालू कीजिए। तब तक यह बंद रहता है, क्योंकि उसमें अधिकांश जानकारी किसी और की है",
        'ar': "لا شيء هنا يمكنه رؤية الأشخاص في هاتفك: فعّل جهات الاتصال ضمن ما يجوز للوكيل رؤيته. يظل معطّلًا حتى تفعل ذلك، لأن معظم ما فيه يخص أشخاصًا آخرين",
    },
    # -- what may sense you (jim/monitors.py) --------------------------------
    "this one senses people who did not choose it — say that the people in that space have been told before switching it on": {
        'es': "esta detecta a personas que no la eligieron: indica que se ha informado a quienes están en ese espacio antes de activarla",
        'fr': "celui-ci capte des personnes qui ne l'ont pas choisi — indiquez que les personnes présentes ont été prévenues avant de l'activer",
        'de': "dieser erfasst Menschen, die ihn nicht gewählt haben — bestätige, dass die Anwesenden informiert wurden, bevor du ihn einschaltest",
        'pt': "este deteta pessoas que não o escolheram — indique que as pessoas nesse espaço foram avisadas antes de o ativar",
        'it': "questo rileva persone che non l'hanno scelto: dichiara che chi si trova in quello spazio è stato avvisato prima di attivarlo",
        'ja': "これは選んでいない人まで感知します。その場にいる人に伝えたことを示してから有効にしてください",
        'zh': "这一项会感知到并未选择它的人——请先确认该空间中的人已被告知，再开启它",
        'hi': "यह उन लोगों को भी महसूस करती है जिन्होंने इसे नहीं चुना — चालू करने से पहले बताइए कि उस जगह के लोगों को सूचित कर दिया गया है",
        'ar': "هذا يستشعر أشخاصًا لم يختاروه — أقرّ بأن من في ذلك المكان قد أُبلغوا قبل تفعيله",
    },
    # -- an aid on the call (jim/oncall.py) ----------------------------------
    #
    # The notice itself is *not* interpolated into this sentence. It is a
    # script to be spoken to somebody else, in that person's language, and
    # putting it inside a sentence the account holder reads would produce
    # exactly the mixed refusal `Term` exists to prevent — while also
    # translating a script out of the language it has to be read aloud in.
    # It rides beside the sentence as structure, the way the plan gate's
    # price does.
    "nothing is listening yet: the other person has not been told. Play the notice on the line first": {
        'es': "todavía no se está escuchando nada: la otra persona no ha sido informada. Reproduce primero el aviso en la línea",
        'fr': "rien n'écoute encore : l'autre personne n'a pas été prévenue. Diffusez d'abord l'avis sur la ligne",
        'de': "es hört noch nichts zu: die andere Person wurde nicht informiert. Spiele zuerst den Hinweis auf der Leitung ab",
        'pt': "ainda não está a ouvir nada: a outra pessoa não foi informada. Reproduza primeiro o aviso na linha",
        'it': "non sta ancora ascoltando nulla: l'altra persona non è stata informata. Riproduci prima l'avviso sulla linea",
        'ja': "まだ何も聞いていません。相手にまだ伝えていないからです。まず回線でお知らせを流してください",
        'zh': "目前还没有开始收听：对方尚未被告知。请先在通话中播放这段告知",
        'hi': "अभी कुछ भी सुना नहीं जा रहा: दूसरे व्यक्ति को बताया नहीं गया है। पहले लाइन पर सूचना चलाइए",
        'ar': "لا شيء يستمع بعد: لم يُبلَّغ الطرف الآخر. شغّل التنبيه على الخط أولًا",
    },
    # -- the unattended study pass (jim/errands.py) ---------------------------
    #
    # Refused because nobody said it could. The sentence names where to say so
    # and what saying so covers, because "not allowed" with no door in it is a
    # dead end rather than a refusal.
    "this guardian has not been allowed to go and study on its own — turn it on in what it may do for you, where it says what it sends and what it keeps": {
        'es': "no se ha permitido a este guardián ir a estudiar por su cuenta: actívalo en lo que puede hacer por ti, donde dice qué envía y qué guarda",
        'fr': "ce gardien n'a pas été autorisé à aller étudier de lui-même — activez-le dans ce qu'il peut faire pour vous, où il est dit ce qu'il envoie et ce qu'il conserve",
        'de': "dieser Wächter darf nicht von sich aus nachforschen — schalte es dort frei, wo steht, was er für dich tun darf, was er sendet und was er behält",
        'pt': "este guardião não foi autorizado a ir estudar por conta própria — ative-o no que ele pode fazer por si, onde diz o que envia e o que guarda",
        'it': "questo guardiano non è stato autorizzato ad andare a studiare da solo: attivalo in ciò che può fare per te, dove dice cosa invia e cosa conserva",
        'ja': "このガーディアンは自分で調べに行く許可を得ていません。「あなたのためにできること」で有効にしてください。何を送り、何を保持するかもそこに書かれています",
        'zh': "这位守护者尚未获准自行外出学习——请在“它能为你做什么”中开启，那里写明了它会发送什么、保留什么",
        'hi': "इस गार्जियन को स्वयं जाकर अध्ययन करने की अनुमति नहीं दी गई है — इसे «यह आपके लिए क्या कर सकता है» में चालू कीजिए, जहाँ लिखा है कि यह क्या भेजता है और क्या रखता है",
        'ar': "لم يُسمح لهذا الحارس بأن يذهب ليدرس من تلقاء نفسه — فعّله في «ما يمكنه فعله من أجلك»، حيث يُذكر ما يرسله وما يحتفظ به",
    },
    # -- the Studio (jim/widgets.py REFUSALS) ---------------------------------
    #
    # Somebody writing their own tool is doing the least clinical thing this
    # product offers, and is exactly as entitled to be refused in their own
    # language as somebody being told an alarm did not go out. The five
    # "nothing will run here" rows say *which* wall could not be built,
    # because "nothing will run here" is useless to whoever has to fix it.
    "give this widget a name": {
        'es': "ponle un nombre a este widget",
        'fr': "donnez un nom à ce widget",
        'de': "gib diesem Widget einen Namen",
        'pt': "dê um nome a este widget",
        'it': "dai un nome a questo widget",
        'ja': "このウィジェットに名前をつけてください",
        'zh': "给这个小工具起个名字",
        'hi': "इस विजेट को एक नाम दें",
        'ar': "أعطِ هذه الأداة اسمًا",
    },
    "no such widget": {
        'es': "no existe ese widget",
        'fr': "ce widget n'existe pas",
        'de': "dieses Widget gibt es nicht",
        'pt': "não existe esse widget",
        'it': "quel widget non esiste",
        'ja': "そのウィジェットはありません",
        'zh': "没有这个小工具",
        'hi': "ऐसा कोई विजेट नहीं है",
        'ar': "لا توجد أداة بهذا الاسم",
    },
    "this widget is longer than the editor will store": {
        'es': "este widget es más largo de lo que el editor puede guardar",
        'fr': "ce widget dépasse ce que l'éditeur peut enregistrer",
        'de': "dieses Widget ist länger, als der Editor speichern kann",
        'pt': "este widget é maior do que o editor consegue guardar",
        'it': "questo widget è più lungo di quanto l'editor possa salvare",
        'ja': "このウィジェットはエディタが保存できる長さを超えています",
        'zh': "这个小工具超过了编辑器能保存的长度",
        'hi': "यह विजेट उतना लंबा है जितना संपादक सहेज नहीं सकता",
        'ar': "هذه الأداة أطول مما يستطيع المحرر حفظه",
    },
    "you are holding as many widgets as one person may": {
        'es': "ya tienes tantos widgets como puede tener una persona",
        'fr': "vous avez déjà autant de widgets qu'une personne peut en garder",
        'de': "du hast bereits so viele Widgets, wie eine Person haben darf",
        'pt': "já tens tantos widgets quantos uma pessoa pode ter",
        'it': "hai già tutti i widget che una persona può tenere",
        'ja': "一人が持てる数のウィジェットをすでに持っています",
        'zh': "你持有的小工具已达到一个人的上限",
        'hi': "आपके पास उतने विजेट हैं जितने एक व्यक्ति रख सकता है",
        'ar': "لديك من الأدوات ما يبلغ الحد المسموح به لشخص واحد",
    },
    "your widget stopped on an error": {
        'es': "tu widget se detuvo por un error",
        'fr': "votre widget s'est arrêté sur une erreur",
        'de': "dein Widget ist mit einem Fehler abgebrochen",
        'pt': "o teu widget parou com um erro",
        'it': "il tuo widget si è fermato su un errore",
        'ja': "ウィジェットがエラーで停止しました",
        'zh': "你的小工具因错误停止了",
        'hi': "आपका विजेट एक त्रुटि पर रुक गया",
        'ar': "توقّفت أداتك عند خطأ",
    },
    "your widget ran longer than it is allowed to": {
        'es': "tu widget se ejecutó más tiempo del permitido",
        'fr': "votre widget a tourné plus longtemps qu'il n'y est autorisé",
        'de': "dein Widget lief länger, als es darf",
        'pt': "o teu widget correu mais tempo do que lhe é permitido",
        'it': "il tuo widget ha girato più a lungo di quanto gli sia concesso",
        'ja': "ウィジェットが許された時間を超えて動き続けました",
        'zh': "你的小工具运行时间超过了允许的上限",
        'hi': "आपका विजेट अनुमत समय से अधिक चला",
        'ar': "استغرقت أداتك وقتًا أطول مما هو مسموح لها",
    },
    "your widget was stopped for using more than it is allowed": {
        'es': "tu widget se detuvo por usar más de lo permitido",
        'fr': "votre widget a été arrêté pour avoir consommé plus qu'il n'y est autorisé",
        'de': "dein Widget wurde gestoppt, weil es mehr verbraucht hat, als es darf",
        'pt': "o teu widget foi parado por usar mais do que lhe é permitido",
        'it': "il tuo widget è stato fermato perché consumava più del consentito",
        'ja': "ウィジェットが許された量を超えて使ったため停止されました",
        'zh': "你的小工具因占用超过允许的资源而被停止",
        'hi': "आपका विजेट अनुमत से अधिक उपयोग करने पर रोक दिया गया",
        'ar': "أُوقفت أداتك لأنها استهلكت أكثر مما هو مسموح لها",
    },
    "your widget finished without returning anything": {
        'es': "tu widget terminó sin devolver nada",
        'fr': "votre widget s'est terminé sans rien renvoyer",
        'de': "dein Widget ist beendet, ohne etwas zurückzugeben",
        'pt': "o teu widget terminou sem devolver nada",
        'it': "il tuo widget è finito senza restituire nulla",
        'ja': "ウィジェットは何も返さずに終了しました",
        'zh': "你的小工具结束了，但没有返回任何内容",
        'hi': "आपका विजेट बिना कुछ लौटाए समाप्त हो गया",
        'ar': "انتهت أداتك دون أن تُعيد شيئًا",
    },
    "this deployment cannot build the box a widget runs in, so nothing will run here": {
        'es': "esta instalación no puede construir la caja donde corre un widget, así que aquí no se ejecutará nada",
        'fr': "cette installation ne peut pas construire la boîte où tourne un widget ; rien ne s'exécutera ici",
        'de': "diese Installation kann die Box, in der ein Widget läuft, nicht bauen — hier wird nichts ausgeführt",
        'pt': "esta instalação não consegue construir a caixa onde um widget corre, por isso aqui nada será executado",
        'it': "questa installazione non può costruire la scatola in cui gira un widget, quindi qui non verrà eseguito nulla",
        'ja': "この環境ではウィジェットを走らせる箱を作れないため、ここでは何も実行されません",
        'zh': "此部署无法搭建运行小工具所需的沙箱，因此这里不会运行任何东西",
        'hi': "यह इंस्टॉलेशन वह डिब्बा नहीं बना सकता जिसमें विजेट चलता है, इसलिए यहाँ कुछ नहीं चलेगा",
        'ar': "لا يستطيع هذا التنصيب بناء الصندوق الذي تعمل داخله الأداة، فلن يُشغَّل شيء هنا",
    },
    "this deployment cannot cut the network for a widget, so nothing will run here": {
        'es': "esta instalación no puede cortar la red para un widget, así que aquí no se ejecutará nada",
        'fr': "cette installation ne peut pas couper le réseau pour un widget ; rien ne s'exécutera ici",
        'de': "diese Installation kann einem Widget das Netz nicht abschneiden — hier wird nichts ausgeführt",
        'pt': "esta instalação não consegue cortar a rede a um widget, por isso aqui nada será executado",
        'it': "questa installazione non può tagliare la rete a un widget, quindi qui non verrà eseguito nulla",
        'ja': "この環境ではウィジェットのネットワークを遮断できないため、ここでは何も実行されません",
        'zh': "此部署无法为小工具切断网络，因此这里不会运行任何东西",
        'hi': "यह इंस्टॉलेशन विजेट के लिए नेटवर्क नहीं काट सकता, इसलिए यहाँ कुछ नहीं चलेगा",
        'ar': "لا يستطيع هذا التنصيب قطع الشبكة عن الأداة، فلن يُشغَّل شيء هنا",
    },
    "this deployment has no interpreter for widgets, so nothing will run here": {
        'es': "esta instalación no tiene intérprete para widgets, así que aquí no se ejecutará nada",
        'fr': "cette installation n'a pas d'interpréteur pour les widgets ; rien ne s'exécutera ici",
        'de': "diese Installation hat keinen Interpreter für Widgets — hier wird nichts ausgeführt",
        'pt': "esta instalação não tem interpretador para widgets, por isso aqui nada será executado",
        'it': "questa installazione non ha un interprete per i widget, quindi qui non verrà eseguito nulla",
        'ja': "この環境にはウィジェット用のインタプリタがないため、ここでは何も実行されません",
        'zh': "此部署没有运行小工具的解释器，因此这里不会运行任何东西",
        'hi': "इस इंस्टॉलेशन में विजेट के लिए कोई इंटरप्रेटर नहीं है, इसलिए यहाँ कुछ नहीं चलेगा",
        'ar': "لا يوجد في هذا التنصيب مفسّر للأدوات، فلن يُشغَّل شيء هنا",
    },
    "this deployment's interpreter is too old to hold a widget in, so nothing will run here": {
        'es': "el intérprete de esta instalación es demasiado antiguo para contener un widget, así que aquí no se ejecutará nada",
        'fr': "l'interpréteur de cette installation est trop ancien pour contenir un widget ; rien ne s'exécutera ici",
        'de': "der Interpreter dieser Installation ist zu alt, um ein Widget zu halten — hier wird nichts ausgeführt",
        'pt': "o interpretador desta instalação é demasiado antigo para conter um widget, por isso aqui nada será executado",
        'it': "l'interprete di questa installazione è troppo vecchio per contenere un widget, quindi qui non verrà eseguito nulla",
        'ja': "この環境のインタプリタは古すぎてウィジェットを閉じ込められないため、ここでは何も実行されません",
        'zh': "此部署的解释器过旧，无法约束小工具，因此这里不会运行任何东西",
        'hi': "इस इंस्टॉलेशन का इंटरप्रेटर इतना पुराना है कि विजेट को रोक नहीं सकता, इसलिए यहाँ कुछ नहीं चलेगा",
        'ar': "مفسّر هذا التنصيب أقدم من أن يحتوي أداة، فلن يُشغَّل شيء هنا",
    },
    "this deployment cannot cap what a widget may use, so nothing will run here": {
        'es': "esta instalación no puede limitar lo que un widget puede usar, así que aquí no se ejecutará nada",
        'fr': "cette installation ne peut pas plafonner ce qu'un widget consomme ; rien ne s'exécutera ici",
        'de': "diese Installation kann nicht begrenzen, was ein Widget verbraucht — hier wird nichts ausgeführt",
        'pt': "esta instalação não consegue limitar o que um widget pode usar, por isso aqui nada será executado",
        'it': "questa installazione non può limitare quanto un widget consuma, quindi qui non verrà eseguito nulla",
        'ja': "この環境ではウィジェットの使用量に上限をかけられないため、ここでは何も実行されません",
        'zh': "此部署无法限制小工具可占用的资源，因此这里不会运行任何东西",
        'hi': "यह इंस्टॉलेशन सीमित नहीं कर सकता कि विजेट कितना उपयोग करे, इसलिए यहाँ कुछ नहीं चलेगा",
        'ar': "لا يستطيع هذا التنصيب تحديد ما تستهلكه الأداة، فلن يُشغَّل شيء هنا",
    },
    "that specialist has departed — their memorial remains on QRME, but they cannot stand behind a condition": {
        'es': "ese especialista ha fallecido: su memorial permanece en QRME, pero no puede respaldar una afección",
        'fr': "ce spécialiste s'en est allé — son mémorial demeure sur QRME, mais il ne peut plus répondre d'une condition",
        'de': "diese Fachperson ist verstorben — ihre Gedenkseite bleibt auf QRME, aber sie kann für kein Anliegen mehr einstehen",
        'pt': "esse especialista partiu — o seu memorial permanece no QRME, mas não pode responder por uma condição",
        'it': "quello specialista se n'è andato: il suo memoriale resta su QRME, ma non può più farsi carico di una condizione",
        'ja': "その専門家は旅立ちました。QRME に追悼のページは残りますが、症状を受け持つことはできません。",
        'zh': "那位专家已经离世——他的纪念页仍在 QRME 上，但无法再为某个状况把关。",
        'hi': "वह विशेषज्ञ जा चुके हैं — उनका स्मृति-पृष्ठ QRME पर बना रहेगा, पर वे किसी स्थिति के पीछे खड़े नहीं हो सकते।",
        'ar': "لقد رحل ذلك المختص — تبقى صفحة تأبينه على QRME، لكنه لا يستطيع أن يقف خلف حالة.",
    },
    "that profile is not active on QRME, so it cannot stand behind a condition": {
        'es': "ese perfil no está activo en QRME, así que no puede respaldar una afección",
        'fr': "ce profil n'est pas actif sur QRME ; il ne peut donc pas répondre d'une condition",
        'de': "dieses Profil ist auf QRME nicht aktiv und kann daher für kein Anliegen einstehen",
        'pt': "esse perfil não está ativo no QRME, por isso não pode responder por uma condição",
        'it': "quel profilo non è attivo su QRME, quindi non può farsi carico di una condizione",
        'ja': "そのプロフィールは QRME で有効ではないため、症状を受け持つことはできません。",
        'zh': "该档案在 QRME 上并非活跃状态，因此不能为某个状况把关。",
        'hi': "वह प्रोफ़ाइल QRME पर सक्रिय नहीं है, इसलिए वह किसी स्थिति के पीछे खड़ी नहीं हो सकती।",
        'ar': "هذا الملف غير نشط على QRME، فلا يمكنه أن يقف خلف حالة.",
    },
    "that specialist is age-restricted — it will answer for an adult and be stepped around for anybody else": {
        'es': "ese especialista tiene restricción de edad: responderá a una persona adulta y se omitirá para cualquier otra",
        'fr': "ce spécialiste est réservé aux adultes — il répondra à une personne majeure et sera contourné pour toute autre",
        'de': "diese Fachperson ist altersbeschränkt — sie antwortet Erwachsenen und wird für alle anderen übergangen",
        'pt': "esse especialista tem restrição de idade — responderá a um adulto e será contornado para qualquer outra pessoa",
        'it': "quello specialista è riservato agli adulti: risponderà a una persona adulta e verrà aggirato per chiunque altro",
        'ja': "その専門家は年齢制限つきです。成人には応じますが、それ以外の方には迂回されます。",
        'zh': "该专家有年龄限制——它会为成年人作答，对其他人则会被绕过。",
        'hi': "वह विशेषज्ञ आयु-प्रतिबंधित है — वयस्क के लिए जवाब देगा, बाकी किसी के लिए उसे छोड़ दिया जाएगा।",
        'ar': "ذلك المختص مقيَّد بالعمر — سيجيب البالغين ويُتجاوَز مع سواهم.",
    },
    "QRME could not be reached, so this profile's standing is unknown": {
        'es': "no se pudo contactar con QRME, así que no se conoce la situación de este perfil",
        'fr': "QRME est injoignable ; l'état de ce profil est donc inconnu",
        'de': "QRME war nicht erreichbar, daher ist der Stand dieses Profils unbekannt",
        'pt': "não foi possível contactar o QRME, por isso a situação deste perfil é desconhecida",
        'it': "non è stato possibile raggiungere QRME, quindi la posizione di questo profilo è ignota",
        'ja': "QRME に接続できなかったため、このプロフィールの状態は分かりません。",
        'zh': "无法连接 QRME，因此这个档案的状态未知。",
        'hi': "QRME तक पहुँच नहीं हो सकी, इसलिए इस प्रोफ़ाइल की स्थिति अज्ञात है।",
        'ar': "تعذّر الوصول إلى QRME، فحالة هذا الملف غير معروفة.",
    },
    "an engaged session needs the online model — the offline one can answer you, but it cannot do anything for you. Nothing was changed.": {
        'es': "una sesión activa necesita el modelo en línea: el sin conexión puede responderte, pero no puede hacer nada por ti. No se cambió nada.",
        'fr': "une session engagée a besoin du modèle en ligne — celui hors ligne peut vous répondre, mais il ne peut rien faire pour vous. Rien n'a été modifié.",
        'de': "eine laufende Sitzung braucht das Online-Modell — das Offline-Modell kann Ihnen antworten, aber nichts für Sie tun. Es wurde nichts geändert.",
        'pt': "uma sessão em curso precisa do modelo online — o offline pode responder-lhe, mas não pode fazer nada por si. Nada foi alterado.",
        'it': "una sessione in corso ha bisogno del modello online: quello offline può risponderti, ma non può fare nulla per te. Non è stato cambiato nulla.",
        'ja': "接続中のセッションにはオンラインのモデルが必要です — オフラインのモデルは答えられますが、あなたの代わりに何かをすることはできません。何も変更されていません。",
        'zh': "会话中的它需要在线模型——离线的那个可以回答你，但不能替你做事。什么也没有改动。",
        'hi': "चालू सत्र के लिए ऑनलाइन मॉडल चाहिए — ऑफ़लाइन वाला जवाब दे सकता है, पर आपके लिए कुछ कर नहीं सकता। कुछ भी नहीं बदला।",
        'ar': "تحتاج الجلسة القائمة إلى النموذج المتصل — أما غير المتصل فيستطيع أن يجيبك، لكنه لا يستطيع أن يفعل شيئًا نيابة عنك. لم يتغيّر شيء.",
    },
    # Engaged sessions (jim/engaged.py). The first sixteen are raised as
    # keys and resolved through `engaged.REFUSALS`; the last two are the
    # doors an undo trail needed and a person should always have had.
    "check-in not found": {
        'es': "registro no encontrado",
        'fr': "point non trouvé",
        'de': "Check-in nicht gefunden",
        'pt': "registo não encontrado",
        'it': "check-in non trovato",
        'ja': "チェックインが見つかりません",
        'zh': "未找到该次记录",
        'hi': "चेक-इन नहीं मिला",
        'ar': "لم يُعثر على التسجيل",
    },
    "journal entry not found": {
        'es': "entrada del diario no encontrada",
        'fr': "entrée de journal non trouvée",
        'de': "Tagebucheintrag nicht gefunden",
        'pt': "entrada de diário não encontrada",
        'it': "voce del diario non trovata",
        'ja': "日誌の項目が見つかりません",
        'zh': "未找到该条日志",
        'hi': "जर्नल प्रविष्टि नहीं मिली",
        'ar': "لم يُعثر على مدخل اليوميات",
    },
    # Not "you may not" — "you have not said yes yet", which is a different
    # sentence and the only honest one. Every translation keeps the pointer to
    # where the switch is: a refusal that names no door is the menu problem
    # this whole feature answers, reproduced inside the conversation.
    ("that group of switches has not been turned on for this session — it is "
     "in the list of what it may touch, and switching it on there is all it "
     "needs"): {
        'es': "ese grupo de opciones no está activado para esta sesión: está en la lista de lo que puede tocar, y basta con activarlo ahí",
        'fr': "ce groupe de réglages n'est pas activé pour cette session : il figure dans la liste de ce qu'elle peut toucher, et il suffit de l'activer là",
        'de': "diese Gruppe von Schaltern ist für diese Sitzung nicht eingeschaltet — sie steht in der Liste dessen, was sie anfassen darf, und dort einzuschalten genügt",
        'pt': "esse grupo de opções não está ligado para esta sessão — está na lista do que ela pode tocar, e ligá-lo aí é tudo o que falta",
        'it': "quel gruppo di interruttori non è attivo per questa sessione: è nell'elenco di ciò che può toccare, e attivarlo lì è tutto ciò che serve",
        'ja': "その設定グループはこのセッションでオンになっていません。触れてよいものの一覧にありますので、そこでオンにするだけです",
        'zh': "这一组开关在本次会话中没有打开 —— 它就在“它可以碰到什么”的清单里，在那里打开即可",
        'hi': "स्विचों का वह समूह इस सत्र के लिए चालू नहीं है — यह उसकी पहुँच की सूची में है, और वहीं चालू कर देना काफ़ी है",
        'ar': "مجموعة المفاتيح تلك ليست مُفعَّلة لهذه الجلسة — إنها ضمن قائمة ما يجوز له لمسه، ويكفي تشغيلها من هناك",
    },
    "that is not something an engaged session can do": {
        'es': "eso no es algo que una sesión activa pueda hacer",
        'fr': "ce n'est pas quelque chose qu'une session engagée peut faire",
        'de': "das kann eine laufende Sitzung nicht tun",
        'pt': "isso não é algo que uma sessão em curso possa fazer",
        'it': "non è una cosa che una sessione in corso possa fare",
        'ja': "それは接続中のセッションにできることではありません",
        'zh': "这不是会话中的它能做的事",
        'hi': "यह ऐसा काम नहीं है जो चालू सत्र कर सके",
        'ar': "هذا ليس مما تستطيع جلسة قائمة فعله",
    },
    "the model asked for a tool in a shape this could not read": {
        'es': "el modelo pidió una herramienta con una forma que no se pudo leer",
        'fr': "le modèle a demandé un outil dans une forme illisible ici",
        'de': "das Modell hat ein Werkzeug in einer Form angefordert, die hier nicht lesbar war",
        'pt': "o modelo pediu uma ferramenta numa forma que não foi possível ler",
        'it': "il modello ha chiesto uno strumento in una forma che non si è potuta leggere",
        'ja': "モデルが読み取れない形でツールを求めました",
        'zh': "模型请求工具的格式无法读取",
        'hi': "मॉडल ने ऐसे रूप में उपकरण माँगा जिसे पढ़ा नहीं जा सका",
        'ar': "طلب النموذج أداة بصيغة تعذّرت قراءتها",
    },
    "that needs something it was not given": {
        'es': "eso necesita algo que no se le dio",
        'fr': "cela demande quelque chose qui n'a pas été fourni",
        'de': "dafür fehlt etwas, das nicht mitgegeben wurde",
        'pt': "isso precisa de algo que não lhe foi dado",
        'it': "per questo serve qualcosa che non è stato fornito",
        'ja': "それには渡されなかったものが必要です",
        'zh': "这需要一样没有提供的东西",
        'hi': "इसके लिए कुछ चाहिए जो दिया नहीं गया",
        'ar': "يحتاج ذلك إلى شيء لم يُعطَ له",
    },
    "that did not go through, and nothing was changed": {
        'es': "eso no salió adelante y no se cambió nada",
        'fr': "cela n'est pas passé, et rien n'a été modifié",
        'de': "das ist nicht durchgegangen, und nichts wurde geändert",
        'pt': "isso não passou, e nada foi alterado",
        'it': "non è andato a buon fine e non è stato cambiato nulla",
        'ja': "それは通らず、何も変更されていません",
        'zh': "这一步没有成功，什么也没有改动",
        'hi': "वह नहीं हो पाया, और कुछ भी नहीं बदला",
        'ar': "لم يمرّ ذلك، ولم يتغيّر شيء",
    },
    "there was nothing in that message": {
        'es': "ese mensaje estaba vacío",
        'fr': "ce message était vide",
        'de': "diese Nachricht war leer",
        'pt': "essa mensagem estava vazia",
        'it': "quel messaggio era vuoto",
        'ja': "そのメッセージには何もありませんでした",
        'zh': "那条消息是空的",
        'hi': "उस संदेश में कुछ नहीं था",
        'ar': "لم يكن في تلك الرسالة شيء",
    },
    "no session is open — engage first, or you are talking to the coach a turn at a time": {
        'es': "no hay ninguna sesión abierta: inicia una, o estás hablando con el coach turno a turno",
        'fr': "aucune session n'est ouverte — engagez-en une, sinon vous parlez au coach un tour à la fois",
        'de': "es ist keine Sitzung offen — beginnen Sie eine, sonst sprechen Sie mit dem Coach Zug um Zug",
        'pt': "não há sessão aberta — inicie uma, ou está a falar com o coach um turno de cada vez",
        'it': "nessuna sessione è aperta: avviane una, altrimenti stai parlando col coach un turno alla volta",
        'ja': "開いているセッションがありません — 接続してください。さもなければ一往復ずつコーチと話していることになります",
        'zh': "当前没有开着的会话——先开一个，否则你只是在一轮一轮地和教练说话",
        'hi': "कोई सत्र खुला नहीं है — पहले जुड़ें, वरना आप कोच से एक-एक बारी करके बात कर रहे हैं",
        'ar': "لا توجد جلسة مفتوحة — ابدأ واحدة، وإلا فأنت تحادث المدرب دورًا بدور",
    },
    "no such act on this account": {
        'es': "no hay tal acción en esta cuenta",
        'fr': "aucune action de ce type sur ce compte",
        'de': "eine solche Handlung gibt es auf diesem Konto nicht",
        'pt': "não existe tal ação nesta conta",
        'it': "non esiste un'azione simile su questo account",
        'ja': "このアカウントにその操作はありません",
        'zh': "该账户上没有这项操作",
        'hi': "इस खाते पर ऐसी कोई क्रिया नहीं है",
        'ar': "لا يوجد إجراء كهذا على هذا الحساب",
    },
    "that one has already been taken back": {
        'es': "esa ya se deshizo",
        'fr': "celle-là a déjà été annulée",
        'de': "das wurde bereits zurückgenommen",
        'pt': "essa já foi desfeita",
        'it': "quella è già stata annullata",
        'ja': "それはすでに取り消されています",
        'zh': "那一项已经撤回过了",
        'hi': "वह पहले ही वापस ली जा चुकी है",
        'ar': "تم التراجع عن ذلك بالفعل",
    },
    "that one cannot be taken back — it left this app, and nothing here can unsay it": {
        'es': "esa no se puede deshacer: salió de esta app y nada de aquí puede desdecirla",
        'fr': "celle-là ne peut pas être annulée — elle a quitté cette app, et rien ici ne peut la dédire",
        'de': "das lässt sich nicht zurücknehmen — es hat diese App verlassen, und nichts hier kann es widerrufen",
        'pt': "essa não pode ser desfeita — saiu desta app, e nada aqui pode desdizê-la",
        'it': "quella non si può annullare: è uscita da questa app e niente qui può ritrattarla",
        'ja': "それは取り消せません — このアプリの外に出ており、ここからは撤回できません",
        'zh': "那一项无法撤回——它已经离开这个应用，这里没有办法收回",
        'hi': "वह वापस नहीं ली जा सकती — वह इस ऐप से बाहर जा चुकी है, और यहाँ से उसे अनकहा नहीं किया जा सकता",
        'ar': "لا يمكن التراجع عن ذلك — فقد غادر هذا التطبيق، ولا شيء هنا ينقضه",
    },
    "taking that back did not work, so it is still listed as done": {
        'es': "deshacer eso no funcionó, así que sigue figurando como hecho",
        'fr': "l'annulation n'a pas fonctionné, cela reste donc listé comme fait",
        'de': "das Zurücknehmen hat nicht funktioniert, es steht also weiter als erledigt",
        'pt': "desfazer isso não funcionou, por isso continua listado como feito",
        'it': "annullarla non ha funzionato, quindi resta elencata come fatta",
        'ja': "取り消しはうまくいかなかったので、まだ実行済みとして残っています",
        'zh': "撤回没有成功，所以它仍然列为已完成",
        'hi': "उसे वापस लेना नहीं हो पाया, इसलिए वह अब भी किया हुआ दर्ज है",
        'ar': "لم ينجح التراجع، فما زال مُدرجًا على أنه تمّ",
    },
    "nothing is being watched under that name": {
        'es': "no se está vigilando nada con ese nombre",
        'fr': "rien n'est surveillé sous ce nom",
        'de': "unter diesem Namen wird nichts beobachtet",
        'pt': "nada está a ser vigiado com esse nome",
        'it': "con quel nome non si sta osservando nulla",
        'ja': "その名前で見守っているものはありません",
        'zh': "没有以那个名字留意的事项",
        'hi': "उस नाम से किसी चीज़ पर नज़र नहीं रखी जा रही",
        'ar': "لا شيء تحت المتابعة بهذا الاسم",
    },
    "name the thing to watch for": {
        'es': "nombra lo que hay que vigilar",
        'fr': "nommez la chose à surveiller",
        'de': "nennen Sie, worauf geachtet werden soll",
        'pt': "diga o que há para vigiar",
        'it': "dì che cosa tenere d'occhio",
        'ja': "見守る対象を挙げてください",
        'zh': "请说明要留意什么",
        'hi': "बताइए किस बात पर नज़र रखनी है",
        'ar': "سمِّ الشيء المطلوب متابعته",
    },
    "the watch list is full — clear one before adding another": {
        'es': "la lista de vigilancia está llena: quita una antes de añadir otra",
        'fr': "la liste de surveillance est pleine — retirez-en une avant d'en ajouter une autre",
        'de': "die Beobachtungsliste ist voll — nehmen Sie eine herunter, bevor Sie eine weitere hinzufügen",
        'pt': "a lista de vigilância está cheia — tire uma antes de acrescentar outra",
        'it': "l'elenco delle cose da osservare è pieno: togline una prima di aggiungerne un'altra",
        'ja': "見守りの一覧がいっぱいです — 一つ外してから追加してください",
        'zh': "留意清单已满——先清掉一项再添加",
        'hi': "नज़र की सूची भर चुकी है — नई जोड़ने से पहले एक हटाइए",
        'ar': "قائمة المتابعة ممتلئة — أزل واحدًا قبل إضافة آخر",
    },
    "a specialist outside JIM has read this; nothing here can unsay it": {
        'es': "un especialista fuera de JIM ha leído esto; nada de aquí puede desdecirlo",
        'fr': "un spécialiste hors de JIM a lu ceci ; rien ici ne peut le dédire",
        'de': "ein Spezialist außerhalb von JIM hat das gelesen; nichts hier kann es widerrufen",
        'pt': "um especialista fora do JIM leu isto; nada aqui o pode desdizer",
        'it': "uno specialista fuori da JIM lo ha letto; niente qui può ritrattarlo",
        'ja': "JIM の外の専門家がこれを読みました。ここからは撤回できません",
        'zh': "JIM 之外的专家已经读过这个；这里没有办法收回",
        'hi': "JIM के बाहर के एक विशेषज्ञ ने इसे पढ़ लिया है; यहाँ से इसे अनकहा नहीं किया जा सकता",
        'ar': "قرأ هذا أخصائي خارج JIM؛ ولا شيء هنا ينقضه",
    },
    "this session has changed enough for one sitting — sign off and start another": {
        'es': "esta sesión ya ha cambiado bastante de una vez: despídete y empieza otra",
        'fr': "cette session a assez changé de choses d'un coup — déconnectez-vous et recommencez-en une",
        'de': "diese Sitzung hat für einmal genug geändert — melden Sie sich ab und beginnen Sie eine neue",
        'pt': "esta sessão já mudou o suficiente de uma vez — despeça-se e comece outra",
        'it': "questa sessione ha cambiato abbastanza per una volta: congedati e aprine un'altra",
        'ja': "このセッションは一度に十分な変更を行いました — サインオフして別のセッションを始めてください",
        'zh': "这次会话一口气改得够多了——请先签退，再开一个",
        'hi': "इस सत्र में एक बार के लिए काफ़ी बदल चुका है — साइन ऑफ़ करके नया शुरू कीजिए",
        'ar': "غيّرت هذه الجلسة ما يكفي لجلسة واحدة — سجّل خروجك وابدأ أخرى",
    },
    "it kept reaching for things and never answered": {
        'es': "siguió recurriendo a cosas y nunca respondió",
        'fr': "il n'a cessé de solliciter des choses sans jamais répondre",
        'de': "es griff immer weiter nach Dingen und antwortete nie",
        'pt': "continuou a recorrer a coisas e nunca respondeu",
        'it': "ha continuato a ricorrere a cose senza mai rispondere",
        'ja': "あれこれ手を伸ばし続けて、結局答えませんでした",
        'zh': "它一直在取用东西，却始终没有回答",
        'hi': "यह चीज़ों तक पहुँचता रहा और जवाब कभी नहीं दिया",
        'ar': "ظلّ يمدّ يده إلى الأشياء ولم يجب قط",
    },
    'Something went wrong on our side. Nothing you sent was recorded.': {
        'es': 'Algo falló de nuestro lado. No se registró nada de lo que envió.',
        'fr': "Quelque chose a échoué de notre côté. Rien de ce que vous avez envoyé n'a été enregistré.",
        'de': 'Auf unserer Seite ist etwas schiefgegangen. Nichts von dem, was Sie gesendet haben, wurde gespeichert.',
        'pt': 'Algo correu mal do nosso lado. Nada do que enviou ficou registado.',
        'it': 'Qualcosa è andato storto dalla nostra parte. Nulla di ciò che ha inviato è stato registrato.',
        'ja': 'こちら側で問題が発生しました。送信された内容は記録されていません。',
        'zh': '我们这边出了问题。您发送的内容没有被记录。',
        'hi': 'हमारी ओर से कुछ गड़बड़ हो गई। आपने जो भेजा, वह दर्ज नहीं हुआ।',
        'ar': 'حدث خطأ من جانبنا. لم يُسجَّل أي شيء أرسلته.',
    },
    'reading the failure map requires the JIM_PROBLEMS_KEY bearer token': {
        'es': 'leer el mapa de fallos requiere el token portador '
              'JIM_PROBLEMS_KEY',
        'fr': 'lire la carte des échecs exige le jeton porteur '
              'JIM_PROBLEMS_KEY',
        'de': 'das Lesen der Fehlerkarte erfordert das '
              'JIM_PROBLEMS_KEY-Bearer-Token',
        'pt': 'ler o mapa de falhas requer o token portador '
              'JIM_PROBLEMS_KEY',
        'it': 'leggere la mappa dei guasti richiede il token bearer '
              'JIM_PROBLEMS_KEY',
        'ja': '障害マップの閲覧には JIM_PROBLEMS_KEY のベアラートークンが必要です',
        'zh': '读取故障图需要 JIM_PROBLEMS_KEY 持有者令牌',
        'hi': 'विफलता मानचित्र पढ़ने के लिए JIM_PROBLEMS_KEY बियरर टोकन चाहिए',
        'ar': 'قراءة خريطة الأعطال تتطلب رمز JIM_PROBLEMS_KEY الحامل',
    },
    'wrong problems key': {
        'es': 'clave de problemas incorrecta',
        'fr': 'mauvaise clé des problèmes',
        'de': 'falscher Problems-Schlüssel',
        'pt': 'chave de problemas errada',
        'it': 'chiave dei problemi sbagliata',
        'ja': 'problemsキーが違います',
        'zh': '问题密钥不正确',
        'hi': 'समस्याओं की कुंजी ग़लत है',
        'ar': 'مفتاح المشاكل خاطئ',
    },
    'the failure aggregate is readable from this machine only until '
    'JIM_PROBLEMS_KEY is set — behind a proxy, set it': {
        'es': 'el agregado de fallos solo se puede leer desde esta máquina '
              'hasta que se fije JIM_PROBLEMS_KEY — tras un proxy, fíjala',
        'fr': "l'agrégat des échecs n'est lisible que depuis cette machine "
              "tant que JIM_PROBLEMS_KEY n'est pas définie — derrière un "
              'proxy, définissez-la',
        'de': 'das Fehleraggregat ist nur von dieser Maschine lesbar, bis '
              'JIM_PROBLEMS_KEY gesetzt ist — hinter einem Proxy: setzen',
        'pt': 'o agregado de falhas só pode ser lido a partir desta máquina '
              'até JIM_PROBLEMS_KEY estar definida — atrás de um proxy, '
              'defina-a',
        'it': "l'aggregato dei guasti è leggibile solo da questa macchina "
              'finché JIM_PROBLEMS_KEY non è impostata — dietro un proxy, '
              'impostala',
        'ja': '障害の集計は JIM_PROBLEMS_KEY を設定するまでこの機械からしか読めません — '
              'プロキシの背後では設定してください',
        'zh': '在设置 JIM_PROBLEMS_KEY 之前，故障汇总只能从本机读取——在代理之后请务必设置',
        'hi': 'जब तक JIM_PROBLEMS_KEY निर्धारित नहीं होती, विफलता समग्र केवल इसी '
              'मशीन से पढ़ा जा सकता है — प्रॉक्सी के पीछे इसे निर्धारित करें',
        'ar': 'لا يمكن قراءة مجمّع الأعطال إلا من هذا الجهاز حتى يُعيَّن '
              'JIM_PROBLEMS_KEY — خلف وكيل، عيِّنه',
    },
    "a responder needs a name — 'someone accepted it' is the thing this loop exists to stop being enough": {
        'es': "quien responde necesita un nombre — 'alguien lo aceptó' es justo lo que este circuito existe para que deje de bastar",
        'fr': "un répondant a besoin d'un nom — « quelqu'un l'a accepté » est précisément ce que cette boucle existe pour rendre insuffisant",
        'de': "wer kommt, braucht einen Namen — 'jemand hat es angenommen' ist genau das, was diese Schleife nicht mehr genügen lassen soll",
        'pt': "quem responde precisa de um nome — 'alguém aceitou' é exatamente o que este circuito existe para deixar de bastar",
        'it': "chi risponde ha bisogno di un nome — 'qualcuno ha accettato' è proprio ciò che questo anello esiste per non far più bastare",
        'ja': "対応者には名前が必要です — 「誰かが引き受けた」で済ませないために、この仕組みはあります",
        'zh': "响应者需要一个名字 — “有人接受了”正是这个环节要终结的说法",
        'hi': "जवाब देने वाले का नाम चाहिए — 'किसी ने स्वीकार कर लिया' को नाकाफ़ी बनाने के लिए ही यह कड़ी है",
        'ar': "المستجيب يحتاج إلى اسم — «قبِلها أحدهم» هو بالضبط ما وُجدت هذه الحلقة لكي لا يعود كافيًا",
    },
    "a minor's verification code goes to their parent or guardian — provide guardian_email": {
        'es': 'el código de verificación de un menor va a su padre, madre o tutor — indique guardian_email',
        'fr': "le code de vérification d'un mineur est envoyé à son parent ou tuteur — renseignez guardian_email",
        'de': 'der Bestätigungscode eines Minderjährigen geht an Eltern oder Erziehungsberechtigte — guardian_email angeben',
        'pt': 'o código de verificação de um menor vai para o pai, mãe ou responsável — indique guardian_email',
        'it': 'il codice di verifica di un minore va al genitore o tutore — indicare guardian_email',
        'ja': '未成年者の確認コードは保護者に送られます — guardian_email を入力してください',
        'zh': '未成年人的验证码会发送给其父母或监护人 — 请提供 guardian_email',
        'hi': 'नाबालिग का सत्यापन कोड उनके माता-पिता या अभिभावक के पास जाता है — guardian_email दें',
        'ar': 'رمز التحقق للقاصر يُرسل إلى الوالد أو الوصي — قدّم guardian_email',
    },
    "the guardian's address must be different from the minor's own": {
        'es': 'la dirección del tutor debe ser distinta de la del menor',
        'fr': "l'adresse du tuteur doit être différente de celle du mineur",
        'de': 'die Adresse des Erziehungsberechtigten muss sich von der des Minderjährigen unterscheiden',
        'pt': 'o endereço do responsável deve ser diferente do endereço do menor',
        'it': "l'indirizzo del tutore deve essere diverso da quello del minore",
        'ja': '保護者のアドレスは未成年者本人のものと別である必要があります',
        'zh': '监护人的邮箱必须与未成年人本人的不同',
        'hi': 'अभिभावक का पता नाबालिग के अपने पते से अलग होना चाहिए',
        'ar': 'يجب أن يكون عنوان الوصي مختلفًا عن عنوان القاصر نفسه',
    },
    'reviewer token required': {
        'es': 'se requiere el token de revisor',
        'fr': 'jeton de réviseur requis',
        'de': 'Prüfer-Token erforderlich',
        'pt': 'token de revisor necessário',
        'it': 'è richiesto il token del revisore',
        'ja': 'レビュアートークンが必要です',
        'zh': '需要审阅者令牌',
        'hi': 'समीक्षक टोकन आवश्यक है',
        'ar': 'رمز المراجع مطلوب',
    },
    'invalid reviewer token': {
        'es': 'token de revisor no válido',
        'fr': 'jeton de réviseur invalide',
        'de': 'ungültiges Prüfer-Token',
        'pt': 'token de revisor inválido',
        'it': 'token del revisore non valido',
        'ja': 'レビュアートークンが無効です',
        'zh': '审阅者令牌无效',
        'hi': 'अमान्य समीक्षक टोकन',
        'ar': 'رمز المراجع غير صالح',
    },
    'this deployment is reachable beyond localhost but has no '
    'JIM_ADMIN_TOKEN configured — the accessibility reports stay closed '
    'until it is': {
        'es': 'esta instalación es accesible más allá de localhost pero no '
              'tiene JIM_ADMIN_TOKEN configurado — los informes de '
              'accesibilidad permanecen cerrados hasta que lo esté',
        'fr': "cette installation est accessible au-delà de localhost mais "
              "n'a pas de JIM_ADMIN_TOKEN configuré — les signalements "
              "d'accessibilité restent fermés jusqu'à ce qu'il le soit",
        'de': 'diese Installation ist über localhost hinaus erreichbar, hat '
              'aber kein JIM_ADMIN_TOKEN konfiguriert — die '
              'Barrierefreiheits-Berichte bleiben geschlossen, bis eines '
              'gesetzt ist',
        'pt': 'esta instalação é acessível além de localhost mas não tem '
              'JIM_ADMIN_TOKEN configurado — os relatos de acessibilidade '
              'permanecem fechados até que esteja',
        'it': 'questa installazione è raggiungibile oltre localhost ma non '
              'ha JIM_ADMIN_TOKEN configurato — le segnalazioni di '
              'accessibilità restano chiuse finché non lo è',
        'ja': 'この環境は localhost の外から到達できますが JIM_ADMIN_TOKEN が'
              '設定されていません — 設定されるまでアクセシビリティ報告は閉じられたままです',
        'zh': '此部署可从 localhost 之外访问，但未配置 JIM_ADMIN_TOKEN — '
              '在配置之前，无障碍报告保持关闭',
        'hi': 'यह परिनियोजन localhost से परे पहुँचा जा सकता है लेकिन '
              'JIM_ADMIN_TOKEN कॉन्फ़िगर नहीं है — जब तक यह नहीं होता, '
              'सुलभता रिपोर्टें बंद रहती हैं',
        'ar': 'هذا النشر يمكن الوصول إليه من خارج localhost لكن لا يوجد '
              'JIM_ADMIN_TOKEN مضبوط — تبقى بلاغات إمكانية الوصول مغلقة '
              'حتى يُضبط',
    },
    'say what you were trying to do and what stood in the way': {
        'es': 'di qué intentabas hacer y qué se interpuso',
        'fr': "dites ce que vous essayiez de faire et ce qui s'y est opposé",
        'de': 'sag, was du versucht hast und was im Weg stand',
        'pt': 'diga o que você estava tentando fazer e o que ficou no caminho',
        'it': 'di\' cosa stavi cercando di fare e cosa ti ha ostacolato',
        'ja': '何をしようとして、何が妨げになったかを書いてください',
        'zh': '请写出你想做什么，以及是什么挡住了你',
        'hi': 'बताइए कि आप क्या करने की कोशिश कर रहे थे और क्या आड़े आया',
        'ar': 'اذكر ما كنت تحاول فعله وما الذي وقف في طريقك',
    },
    'nothing has been trained yet': {
        'es': 'todavía no se ha entrenado nada',
        'fr': "rien n'a encore été entraîné",
        'de': 'es wurde noch nichts trainiert',
        'pt': 'ainda não foi treinado nada',
        'it': 'non è stato ancora addestrato nulla',
        'ja': 'まだ何も学習していません',
        'zh': '尚未训练任何模型',
        'hi': 'अभी तक कुछ भी प्रशिक्षित नहीं हुआ',
        'ar': 'لم يُدرَّب أي شيء بعد',
    },
    # --- 0.40.2: the 42 recorded in jim/tests/refusals_untranslated.txt ----
    #
    # Every one of these was a sentence the Guardian said when it said no, in
    # English, to somebody who had chosen otherwise. The record is the reason
    # they could be finished rather than rediscovered.
    #
    #     asked     is the refusal translated
    #     mattered  is every refusal translated
    #
    # Field names, header names and env vars stay as they are:
    # `audio_base64`, `qrme_profile_id`, `x-signup-key`, `JIM_QRME_URL`.
    'PDI vault unreachable': {
        'es': 'bóveda PDI inaccesible',
        'fr': 'coffre PDI injoignable',
        'de': 'PDI-Tresor nicht erreichbar',
        'pt': 'cofre PDI inacessível',
        'it': 'cassaforte PDI irraggiungibile',
        'ja': 'PDI 保管庫に接続できません',
        'zh': '无法连接 PDI 保险库',
        'hi': 'PDI वॉल्ट अगम्य',
        'ar': 'تعذّر الوصول إلى خزنة PDI',
    },
    'a message is required': {
        'es': 'se requiere un mensaje',
        'fr': 'un message est requis',
        'de': 'eine Nachricht ist erforderlich',
        'pt': 'é necessária uma mensagem',
        'it': 'è richiesto un messaggio',
        'ja': 'メッセージが必要です',
        'zh': '需要填写消息内容',
        'hi': 'संदेश आवश्यक है',
        'ar': 'الرسالة مطلوبة',
    },
    'a typed legal-name signature is required': {
        'es': 'se requiere una firma con el nombre legal escrito',
        'fr': 'une signature du nom légal saisie au clavier est requise',
        'de': 'eine getippte Unterschrift mit dem vollständigen Namen ist erforderlich',
        'pt': 'é necessária uma assinatura com o nome legal escrito',
        'it': 'è richiesta una firma con il nome legale digitato',
        'ja': '法的な氏名を入力した署名が必要です',
        'zh': '需要键入法定姓名作为签名',
        'hi': 'टाइप किया गया कानूनी-नाम हस्ताक्षर आवश्यक है',
        'ar': 'يلزم توقيع بالاسم القانوني مكتوبًا',
    },
    'app connector not found': {
        'es': 'conector de aplicación no encontrado',
        'fr': 'connecteur d\'application introuvable',
        'de': 'App-Connector nicht gefunden',
        'pt': 'conector de aplicação não encontrado',
        'it': 'connettore dell\'app non trovato',
        'ja': 'アプリコネクタが見つかりません',
        'zh': '未找到应用连接器',
        'hi': 'ऐप कनेक्टर नहीं मिला',
        'ar': 'لم يُعثر على موصّل التطبيق',
    },
    'audio_base64 is not valid base64': {
        'es': 'audio_base64 no es base64 válido',
        'fr': 'audio_base64 n\'est pas du base64 valide',
        'de': 'audio_base64 ist kein gültiges Base64',
        'pt': 'audio_base64 não é base64 válido',
        'it': 'audio_base64 non è base64 valido',
        'ja': 'audio_base64 が有効な base64 ではありません',
        'zh': 'audio_base64 不是有效的 base64',
        'hi': 'audio_base64 वैध base64 नहीं है',
        'ar': 'القيمة audio_base64 ليست base64 صالحًا',
    },
    'beacon not found': {
        'es': 'baliza no encontrada',
        'fr': 'balise introuvable',
        'de': 'Beacon nicht gefunden',
        'pt': 'baliza não encontrada',
        'it': 'beacon non trovato',
        'ja': 'ビーコンが見つかりません',
        'zh': '未找到信标',
        'hi': 'बीकन नहीं मिला',
        'ar': 'لم يُعثر على المنارة',
    },
    'beacons are for publish connections': {
        'es': 'las balizas son para conexiones de publicación',
        'fr': 'les balises servent aux connexions de publication',
        'de': 'Beacons sind für Veröffentlichungsverbindungen',
        'pt': 'as balizas são para ligações de publicação',
        'it': 'i beacon sono per le connessioni di pubblicazione',
        'ja': 'ビーコンは公開用の接続に使うものです',
        'zh': '信标用于发布类连接',
        'hi': 'बीकन प्रकाशन कनेक्शनों के लिए हैं',
        'ar': 'المنارات مخصّصة لاتصالات النشر',
    },
    'connection has been revoked': {
        'es': 'la conexión ha sido revocada',
        'fr': 'la connexion a été révoquée',
        'de': 'die Verbindung wurde widerrufen',
        'pt': 'a ligação foi revogada',
        'it': 'la connessione è stata revocata',
        'ja': 'この接続は取り消されました',
        'zh': '该连接已被撤销',
        'hi': 'कनेक्शन रद्द कर दिया गया है',
        'ar': 'تم إلغاء الاتصال',
    },
    'connector has been revoked': {
        'es': 'el conector ha sido revocado',
        'fr': 'le connecteur a été révoqué',
        'de': 'der Connector wurde widerrufen',
        'pt': 'o conector foi revogado',
        'it': 'il connettore è stato revocato',
        'ja': 'このコネクタは取り消されました',
        'zh': '该连接器已被撤销',
        'hi': 'कनेक्टर रद्द कर दिया गया है',
        'ar': 'تم إلغاء الموصّل',
    },
    'consent to terms of use is required to enroll': {
        'es': 'es necesario consentir las condiciones de uso para darse de alta',
        'fr': 'le consentement aux conditions d\'utilisation est requis pour s\'inscrire',
        'de': 'für die Anmeldung ist die Zustimmung zu den Nutzungsbedingungen erforderlich',
        'pt': 'é necessário consentir os termos de utilização para se inscrever',
        'it': 'per iscriversi è necessario accettare le condizioni d\'uso',
        'ja': '登録には利用条件への同意が必要です',
        'zh': '注册需先同意使用条款',
        'hi': 'नामांकन हेतु उपयोग की शर्तों पर सहमति आवश्यक है',
        'ar': 'التسجيل يتطلّب الموافقة على شروط الاستخدام',
    },
    'excursion not found': {
        'es': 'excursión no encontrada',
        'fr': 'excursion introuvable',
        'de': 'Exkursion nicht gefunden',
        'pt': 'excursão não encontrada',
        'it': 'escursione non trovata',
        'ja': 'エクスカーションが見つかりません',
        'zh': '未找到外出探索',
        'hi': 'भ्रमण नहीं मिला',
        'ar': 'لم يُعثر على الرحلة',
    },
    'goal not found': {
        'es': 'objetivo no encontrado',
        'fr': 'objectif introuvable',
        'de': 'Ziel nicht gefunden',
        'pt': 'objetivo não encontrado',
        'it': 'obiettivo non trovato',
        'ja': '目標が見つかりません',
        'zh': '未找到目标',
        'hi': 'लक्ष्य नहीं मिला',
        'ar': 'لم يُعثر على الهدف',
    },
    'habit not found': {
        'es': 'hábito no encontrado',
        'fr': 'habitude introuvable',
        'de': 'Gewohnheit nicht gefunden',
        'pt': 'hábito não encontrado',
        'it': 'abitudine non trovata',
        'ja': '習慣が見つかりません',
        'zh': '未找到习惯',
        'hi': 'आदत नहीं मिली',
        'ar': 'لم يُعثر على العادة',
    },
    'minors require parent/guardian consent': {
        'es': 'los menores requieren el consentimiento de su padre, madre o tutor',
        'fr': 'les mineurs doivent avoir le consentement d\'un parent ou tuteur',
        'de': 'Minderjährige benötigen die Einwilligung der Eltern oder Erziehungsberechtigten',
        'pt': 'os menores requerem consentimento parental ou do tutor',
        'it': 'i minori richiedono il consenso di un genitore o tutore',
        'ja': '未成年者には保護者の同意が必要です',
        'zh': '未成年人需要父母或监护人同意',
        'hi': 'नाबालिगों हेतु माता-पिता/अभिभावक की सहमति आवश्यक है',
        'ar': 'يحتاج القاصرون إلى موافقة أحد الوالدين أو الوصي',
    },
    'no Medical ID card to revoke': {
        'es': 'no hay ninguna tarjeta de identificación médica que revocar',
        'fr': 'aucune carte d\'identification médicale à révoquer',
        'de': 'keine Medical-ID-Karte zum Widerrufen vorhanden',
        'pt': 'não há nenhum cartão de identificação médica para revogar',
        'it': 'nessuna tessera di identificazione medica da revocare',
        'ja': '取り消せる医療 ID カードがありません',
        'zh': '没有可撤销的医疗身份卡',
        'hi': 'रद्द करने हेतु कोई मेडिकल आईडी कार्ड नहीं',
        'ar': 'لا توجد بطاقة هوية طبية لإلغائها',
    },
    'no PDI vault configured (set JIM_PDI_URL / JIM_PDI_TOKEN)': {
        'es': 'no hay bóveda PDI configurada (defina JIM_PDI_URL / JIM_PDI_TOKEN)',
        'fr': 'aucun coffre PDI configuré (définissez JIM_PDI_URL / JIM_PDI_TOKEN)',
        'de': 'kein PDI-Tresor konfiguriert (JIM_PDI_URL / JIM_PDI_TOKEN setzen)',
        'pt': 'não há cofre PDI configurado (defina JIM_PDI_URL / JIM_PDI_TOKEN)',
        'it': 'nessuna cassaforte PDI configurata (imposta JIM_PDI_URL / JIM_PDI_TOKEN)',
        'ja': 'PDI 保管庫が設定されていません（JIM_PDI_URL / JIM_PDI_TOKEN を設定してください）',
        'zh': '未配置 PDI 保险库（请设置 JIM_PDI_URL / JIM_PDI_TOKEN）',
        'hi': 'कोई PDI वॉल्ट कॉन्फ़िगर नहीं है (JIM_PDI_URL / JIM_PDI_TOKEN सेट करें)',
        'ar': 'لا توجد خزنة PDI مُهيّأة (اضبط JIM_PDI_URL / JIM_PDI_TOKEN)',
    },
    'no QRME endpoint configured (set JIM_QRME_URL)': {
        'es': 'no hay endpoint de QRME configurado (defina JIM_QRME_URL)',
        'fr': 'aucun point de terminaison QRME configuré (définissez JIM_QRME_URL)',
        'de': 'kein QRME-Endpunkt konfiguriert (JIM_QRME_URL setzen)',
        'pt': 'não há endpoint QRME configurado (defina JIM_QRME_URL)',
        'it': 'nessun endpoint QRME configurato (imposta JIM_QRME_URL)',
        'ja': 'QRME のエンドポイントが設定されていません（JIM_QRME_URL を設定してください）',
        'zh': '未配置 QRME 端点（请设置 JIM_QRME_URL）',
        'hi': 'कोई QRME एंडपॉइंट कॉन्फ़िगर नहीं है (JIM_QRME_URL सेट करें)',
        'ar': 'لا توجد نقطة نهاية QRME مُهيّأة (اضبط JIM_QRME_URL)',
    },
    'no QRME endpoint configured (set JIM_QRME_URL) — the community lives in QRME and JIM shows the door': {
        'es': 'no hay endpoint de QRME configurado (defina JIM_QRME_URL) — la comunidad vive en QRME y JIM muestra la puerta',
        'fr': 'aucun point de terminaison QRME configuré (définissez JIM_QRME_URL) — la communauté vit dans QRME et JIM en indique la porte',
        'de': 'kein QRME-Endpunkt konfiguriert (JIM_QRME_URL setzen) — die Community lebt in QRME, und JIM zeigt die Tür dorthin',
        'pt': 'não há endpoint QRME configurado (defina JIM_QRME_URL) — a comunidade vive no QRME e o JIM mostra a porta',
        'it': 'nessun endpoint QRME configurato (imposta JIM_QRME_URL) — la comunità vive in QRME e JIM ne mostra la porta',
        'ja': 'QRME のエンドポイントが設定されていません（JIM_QRME_URL を設定してください）— コミュニティは QRME にあり、JIM はその入口を示します',
        'zh': '未配置 QRME 端点（请设置 JIM_QRME_URL）— 社区位于 QRME，JIM 只是指出入口',
        'hi': 'कोई QRME एंडपॉइंट कॉन्फ़िगर नहीं है (JIM_QRME_URL सेट करें) — समुदाय QRME में रहता है और JIM उसका द्वार दिखाता है',
        'ar': 'لا توجد نقطة نهاية QRME مُهيّأة (اضبط JIM_QRME_URL) — المجتمع يقيم في QRME وJIM يدلّ على بابه',
    },
    'no QRME endpoint configured (set JIM_QRME_URL) — the feed lives in QRME and JIM shows the door': {
        'es': 'no hay endpoint de QRME configurado (defina JIM_QRME_URL) — el feed vive en QRME y JIM muestra la puerta',
        'fr': 'aucun point de terminaison QRME configuré (définissez JIM_QRME_URL) — le fil vit dans QRME et JIM en indique la porte',
        'de': 'kein QRME-Endpunkt konfiguriert (JIM_QRME_URL setzen) — der Feed lebt in QRME, und JIM zeigt die Tür dorthin',
        'pt': 'não há endpoint QRME configurado (defina JIM_QRME_URL) — o feed vive no QRME e o JIM mostra a porta',
        'it': 'nessun endpoint QRME configurato (imposta JIM_QRME_URL) — il feed vive in QRME e JIM ne mostra la porta',
        'ja': 'QRME のエンドポイントが設定されていません（JIM_QRME_URL を設定してください）— フィードは QRME にあり、JIM はその入口を示します',
        'zh': '未配置 QRME 端点（请设置 JIM_QRME_URL）— 信息流位于 QRME，JIM 只是指出入口',
        'hi': 'कोई QRME एंडपॉइंट कॉन्फ़िगर नहीं है (JIM_QRME_URL सेट करें) — फ़ीड QRME में रहती है और JIM उसका द्वार दिखाता है',
        'ar': 'لا توجد نقطة نهاية QRME مُهيّأة (اضبط JIM_QRME_URL) — التدفق يقيم في QRME وJIM يدلّ على بابه',
    },
    'no QRME endpoint configured (set JIM_QRME_URL) — the people live in QRME and JIM shows the door': {
        'es': 'no hay endpoint de QRME configurado (defina JIM_QRME_URL) — las personas viven en QRME y JIM muestra la puerta',
        'fr': 'aucun point de terminaison QRME configuré (définissez JIM_QRME_URL) — les gens vivent dans QRME et JIM en indique la porte',
        'de': 'kein QRME-Endpunkt konfiguriert (JIM_QRME_URL setzen) — die Menschen leben in QRME, und JIM zeigt die Tür dorthin',
        'pt': 'não há endpoint QRME configurado (defina JIM_QRME_URL) — as pessoas vivem no QRME e o JIM mostra a porta',
        'it': 'nessun endpoint QRME configurato (imposta JIM_QRME_URL) — le persone vivono in QRME e JIM ne mostra la porta',
        'ja': 'QRME のエンドポイントが設定されていません（JIM_QRME_URL を設定してください）— 人びとは QRME にいて、JIM はその入口を示します',
        'zh': '未配置 QRME 端点（请设置 JIM_QRME_URL）— 人在 QRME，JIM 只是指出入口',
        'hi': 'कोई QRME एंडपॉइंट कॉन्फ़िगर नहीं है (JIM_QRME_URL सेट करें) — लोग QRME में हैं और JIM उसका द्वार दिखाता है',
        'ar': 'لا توجد نقطة نهاية QRME مُهيّأة (اضبط JIM_QRME_URL) — الناس في QRME وJIM يدلّ على بابه',
    },
    'no alarm with that id': {
        'es': 'no hay ninguna alarma con ese id',
        'fr': 'aucune alerte avec cet identifiant',
        'de': 'kein Alarm mit dieser Kennung',
        'pt': 'não há nenhum alarme com esse id',
        'it': 'nessun allarme con quell\'id',
        'ja': 'その id のアラームはありません',
        'zh': '不存在具有该 id 的警报',
        'hi': 'उस आईडी वाला कोई अलार्म नहीं',
        'ar': 'لا يوجد إنذار بهذا المعرّف',
    },
    'no audio': {
        'es': 'no hay audio',
        'fr': 'aucun audio',
        'de': 'kein Audio',
        'pt': 'não há áudio',
        'it': 'nessun audio',
        'ja': '音声がありません',
        'zh': '没有音频',
        'hi': 'कोई ऑडियो नहीं',
        'ar': 'لا يوجد صوت',
    },
    'no lesson covers that screen': {
        'es': 'ninguna lección cubre esa pantalla',
        'fr': 'aucune leçon ne couvre cet écran',
        'de': 'keine Lektion behandelt diesen Bildschirm',
        'pt': 'nenhuma lição cobre esse ecrã',
        'it': 'nessuna lezione copre quella schermata',
        'ja': 'その画面を扱うレッスンはありません',
        'zh': '没有课程涵盖该屏幕',
        'hi': 'उस स्क्रीन को कोई पाठ नहीं समेटता',
        'ar': 'لا يغطّي أي درس تلك الشاشة',
    },
    'no mail server is configured — save one first': {
        'es': 'no hay ningún servidor de correo configurado — guarde uno primero',
        'fr': 'aucun serveur de messagerie n\'est configuré — enregistrez-en un d\'abord',
        'de': 'es ist kein Mailserver konfiguriert — legen Sie zuerst einen an',
        'pt': 'não há nenhum servidor de e-mail configurado — guarde um primeiro',
        'it': 'nessun server di posta configurato — salvane prima uno',
        'ja': 'メールサーバーが設定されていません — まず登録してください',
        'zh': '未配置邮件服务器 — 请先保存一个',
        'hi': 'कोई मेल सर्वर कॉन्फ़िगर नहीं है — पहले एक सहेजें',
        'ar': 'لا يوجد خادم بريد مُهيّأ — احفظ واحدًا أولًا',
    },
    'no open alarm with that id': {
        'es': 'no hay ninguna alarma abierta con ese id',
        'fr': 'aucune alerte en cours avec cet identifiant',
        'de': 'kein offener Alarm mit dieser Kennung',
        'pt': 'não há nenhum alarme em aberto com esse id',
        'it': 'nessun allarme aperto con quell\'id',
        'ja': 'その id の未対応アラームはありません',
        'zh': '不存在具有该 id 的未处理警报',
        'hi': 'उस आईडी वाला कोई खुला अलार्म नहीं',
        'ar': 'لا يوجد إنذار مفتوح بهذا المعرّف',
    },
    'no signed waiver on file': {
        'es': 'no hay ninguna renuncia firmada en el expediente',
        'fr': 'aucune décharge signée au dossier',
        'de': 'keine unterzeichnete Verzichtserklärung hinterlegt',
        'pt': 'não há nenhuma renúncia assinada em arquivo',
        'it': 'nessuna liberatoria firmata agli atti',
        'ja': '署名済みの同意免責書が保管されていません',
        'zh': '档案中没有已签署的免责声明',
        'hi': 'फ़ाइल पर कोई हस्ताक्षरित छूट-पत्र नहीं',
        'ar': 'لا يوجد تنازل موقَّع في السجل',
    },
    'no such child on this guardian': {
        'es': 'no existe ese menor a cargo de este tutor',
        'fr': 'aucun enfant de ce nom pour ce tuteur',
        'de': 'kein solches Kind bei dieser erziehungsberechtigten Person',
        'pt': 'não existe essa criança sob este tutor',
        'it': 'nessun minore di questo tipo per questo tutore',
        'ja': 'この保護者に、そのお子さまの登録はありません',
        'zh': '该监护人名下没有此儿童',
        'hi': 'इस अभिभावक पर ऐसा कोई बच्चा नहीं',
        'ar': 'لا يوجد طفل بهذا الوصف لدى هذا الوصي',
    },
    'no such custody record': {
        'es': 'no existe ese registro de custodia',
        'fr': 'aucun enregistrement de garde de ce nom',
        'de': 'kein solcher Sorgerechtseintrag',
        'pt': 'não existe esse registo de custódia',
        'it': 'nessun record di affidamento di questo tipo',
        'ja': 'そのような監護の記録はありません',
        'zh': '没有该监护记录',
        'hi': 'ऐसा कोई अभिरक्षा अभिलेख नहीं',
        'ar': 'لا يوجد سجلّ حضانة بهذا الوصف',
    },
    'no such task': {
        'es': 'no existe esa tarea',
        'fr': 'aucune tâche de ce nom',
        'de': 'keine solche Aufgabe',
        'pt': 'não existe essa tarefa',
        'it': 'nessun compito di questo tipo',
        'ja': 'そのようなタスクはありません',
        'zh': '没有该任务',
        'hi': 'ऐसा कोई कार्य नहीं',
        'ar': 'لا توجد مهمة بهذا الوصف',
    },
    'nothing to say': {
        'es': 'nada que decir',
        'fr': 'rien à dire',
        'de': 'nichts zu sagen',
        'pt': 'nada a dizer',
        'it': 'niente da dire',
        'ja': '話す内容がありません',
        'zh': '没有可说的内容',
        'hi': 'कहने को कुछ नहीं',
        'ar': 'لا شيء يُقال',
    },
    'rating must be 1–5': {
        'es': 'la valoración debe estar entre 1 y 5',
        'fr': 'la note doit être comprise entre 1 et 5',
        'de': 'die Bewertung muss zwischen 1 und 5 liegen',
        'pt': 'a avaliação deve estar entre 1 e 5',
        'it': 'la valutazione deve essere compresa tra 1 e 5',
        'ja': '評価は1〜5の範囲で指定してください',
        'zh': '评分必须为 1–5',
        'hi': 'रेटिंग 1–5 के बीच होनी चाहिए',
        'ar': 'يجب أن يكون التقييم بين 1 و5',
    },
    'robot not found': {
        'es': 'robot no encontrado',
        'fr': 'robot introuvable',
        'de': 'Roboter nicht gefunden',
        'pt': 'robô não encontrado',
        'it': 'robot non trovato',
        'ja': 'ロボットが見つかりません',
        'zh': '未找到机器人',
        'hi': 'रोबोट नहीं मिला',
        'ar': 'لم يُعثر على الروبوت',
    },
    'session not found': {
        'es': 'sesión no encontrada',
        'fr': 'session introuvable',
        'de': 'Sitzung nicht gefunden',
        'pt': 'sessão não encontrada',
        'it': 'sessione non trovata',
        'ja': 'セッションが見つかりません',
        'zh': '未找到会话',
        'hi': 'सत्र नहीं मिला',
        'ar': 'لم يُعثر على الجلسة',
    },
    'social connection not found': {
        'es': 'conexión social no encontrada',
        'fr': 'connexion sociale introuvable',
        'de': 'soziale Verbindung nicht gefunden',
        'pt': 'ligação social não encontrada',
        'it': 'connessione social non trovata',
        'ja': 'ソーシャル接続が見つかりません',
        'zh': '未找到社交连接',
        'hi': 'सोशल कनेक्शन नहीं मिला',
        'ar': 'لم يُعثر على الاتصال الاجتماعي',
    },
    'tandem specialists require a qrme_profile_id': {
        'es': 'los especialistas en tándem requieren un qrme_profile_id',
        'fr': 'les spécialistes en tandem requièrent un qrme_profile_id',
        'de': 'Tandem-Fachpersonen erfordern eine qrme_profile_id',
        'pt': 'os especialistas em tandem requerem um qrme_profile_id',
        'it': 'gli specialisti in tandem richiedono un qrme_profile_id',
        'ja': 'タンデムの専門家には qrme_profile_id が必要です',
        'zh': '双联专家需要 qrme_profile_id',
        'hi': 'टैंडम विशेषज्ञों हेतु qrme_profile_id आवश्यक है',
        'ar': 'يتطلّب المختصّون في الاقتران معرّف qrme_profile_id',
    },
    'that capture belongs to somebody else': {
        'es': 'esa captura pertenece a otra persona',
        'fr': 'cette capture appartient à quelqu\'un d\'autre',
        'de': 'diese Aufnahme gehört jemand anderem',
        'pt': 'essa captura pertence a outra pessoa',
        'it': 'quell\'acquisizione appartiene a qualcun altro',
        'ja': 'そのキャプチャは別の方のものです',
        'zh': '该采集记录属于其他人',
        'hi': 'वह कैप्चर किसी और का है',
        'ar': 'ذلك التسجيل يخصّ شخصًا آخر',
    },
    'the autonomous-resuscitation waiver can never be signed for a minor — not by the minor and not by a guardian; confirm-gated operation is the ceiling': {
        'es': 'la renuncia de reanimación autónoma nunca puede firmarse para un menor — ni por el menor ni por un tutor; la operación con confirmación es el techo',
        'fr': 'la décharge de réanimation autonome ne peut jamais être signée pour un mineur — ni par le mineur ni par un tuteur ; l\'opération sous confirmation est le plafond',
        'de': 'die Verzichtserklärung für autonome Reanimation kann für Minderjährige nie unterzeichnet werden — weder von der minderjährigen Person noch von einer erziehungsberechtigten; bestätigungspflichtiger Betrieb ist die Obergrenze',
        'pt': 'a renúncia de reanimação autónoma nunca pode ser assinada para um menor — nem pelo menor nem por um tutor; a operação com confirmação é o limite',
        'it': 'la liberatoria per la rianimazione autonoma non può mai essere firmata per un minore — né dal minore né da un tutore; l\'operazione con conferma è il limite massimo',
        'ja': '自律的な蘇生に関する免責書は、未成年者について決して署名できません — 本人によっても保護者によってもです。確認を要する運用が上限です',
        'zh': '自主复苏免责声明绝不可为未成年人签署 — 无论由未成年人本人还是监护人；须确认后执行是上限',
        'hi': 'स्वायत्त पुनर्जीवन छूट-पत्र किसी नाबालिग के लिए कभी हस्ताक्षरित नहीं हो सकता — न नाबालिग द्वारा, न अभिभावक द्वारा; पुष्टि-सहित संचालन ही अधिकतम सीमा है',
        'ar': 'لا يمكن إطلاقًا توقيع تنازل الإنعاش الذاتي لقاصر — لا من القاصر ولا من وصيّه؛ والتشغيل المشروط بالتأكيد هو الحد الأقصى',
    },
    'the user has not consented to provider access': {
        'es': 'el usuario no ha consentido el acceso del proveedor',
        'fr': 'l\'utilisateur n\'a pas consenti à l\'accès du prestataire',
        'de': 'die Nutzerin oder der Nutzer hat dem Zugriff des Anbieters nicht zugestimmt',
        'pt': 'o utilizador não consentiu o acesso do prestador',
        'it': 'l\'utente non ha acconsentito all\'accesso del fornitore',
        'ja': 'ご本人は、提供者によるアクセスに同意していません',
        'zh': '用户未同意该提供方访问',
        'hi': 'उपयोगकर्ता ने प्रदाता की पहुँच पर सहमति नहीं दी',
        'ar': 'لم يوافق المستخدم على وصول المزوّد',
    },
    'the waiver terms must be explicitly accepted': {
        'es': 'las condiciones de la renuncia deben aceptarse explícitamente',
        'fr': 'les termes de la décharge doivent être explicitement acceptés',
        'de': 'den Bedingungen der Verzichtserklärung muss ausdrücklich zugestimmt werden',
        'pt': 'os termos da renúncia devem ser explicitamente aceites',
        'it': 'i termini della liberatoria devono essere accettati esplicitamente',
        'ja': '免責書の条件には明示的な同意が必要です',
        'zh': '免责声明条款必须获得明确接受',
        'hi': 'छूट-पत्र की शर्तें स्पष्ट रूप से स्वीकार की जानी चाहिए',
        'ar': 'يجب قبول شروط التنازل صراحةً',
    },
    'this Medical ID card is not valid': {
        'es': 'esta tarjeta de identificación médica no es válida',
        'fr': 'cette carte d\'identification médicale n\'est pas valide',
        'de': 'diese Medical-ID-Karte ist ungültig',
        'pt': 'este cartão de identificação médica não é válido',
        'it': 'questa tessera di identificazione medica non è valida',
        'ja': 'この医療 ID カードは無効です',
        'zh': '此医疗身份卡无效',
        'hi': 'यह मेडिकल आईडी कार्ड वैध नहीं है',
        'ar': 'بطاقة الهوية الطبية هذه غير صالحة',
    },
    'this connection is for collecting, not publishing': {
        'es': 'esta conexión es para recopilar, no para publicar',
        'fr': 'cette connexion sert à collecter, pas à publier',
        'de': 'diese Verbindung dient dem Sammeln, nicht dem Veröffentlichen',
        'pt': 'esta ligação é para recolher e não para publicar',
        'it': 'questa connessione serve a raccogliere, non a pubblicare',
        'ja': 'この接続は収集用であり、公開用ではありません',
        'zh': '此连接用于收集，而非发布',
        'hi': 'यह कनेक्शन एकत्र करने के लिए है, प्रकाशन के लिए नहीं',
        'ar': 'هذا الاتصال للجمع لا للنشر',
    },
    'this connection is for publishing, not collecting': {
        'es': 'esta conexión es para publicar, no para recopilar',
        'fr': 'cette connexion sert à publier, pas à collecter',
        'de': 'diese Verbindung dient dem Veröffentlichen, nicht dem Sammeln',
        'pt': 'esta ligação é para publicar e não para recolher',
        'it': 'questa connessione serve a pubblicare, non a raccogliere',
        'ja': 'この接続は公開用であり、収集用ではありません',
        'zh': '此连接用于发布，而非收集',
        'hi': 'यह कनेक्शन प्रकाशन के लिए है, एकत्र करने के लिए नहीं',
        'ar': 'هذا الاتصال للنشر لا للجمع',
    },
    'this deployment requires a signup key to enroll — send it as the x-signup-key header': {
        'es': 'esta instalación requiere una clave de alta para darse de alta — envíela en la cabecera x-signup-key',
        'fr': 'ce déploiement exige une clé d\'inscription — envoyez-la dans l\'en-tête x-signup-key',
        'de': 'diese Installation erfordert einen Anmeldeschlüssel — senden Sie ihn im Header x-signup-key',
        'pt': 'esta instalação requer uma chave de inscrição — envie-a no cabeçalho x-signup-key',
        'it': 'questa installazione richiede una chiave di iscrizione — inviala nell\'intestazione x-signup-key',
        'ja': 'この環境で登録するにはサインアップキーが必要です — x-signup-key ヘッダーで送信してください',
        'zh': '此部署需要注册密钥才能注册 — 请通过 x-signup-key 标头发送',
        'hi': 'इस परिनियोजन में नामांकन हेतु साइनअप कुंजी चाहिए — इसे x-signup-key हेडर में भेजें',
        'ar': 'يتطلّب هذا النشر مفتاح تسجيل — أرسله في ترويسة x-signup-key',
    },
    'nothing to study — the curriculum is empty and no topic was named': {
        'es': 'nada que estudiar — el plan de estudio está vacío y no se nombró ningún tema',
        'fr': 'rien à étudier — le programme est vide et aucun sujet n\'a été nommé',
        'de': 'nichts zu studieren — der Lehrplan ist leer und kein Thema wurde genannt',
        'pt': 'nada para estudar — o currículo está vazio e nenhum tema foi indicado',
        'it': 'niente da studiare — il programma è vuoto e nessun argomento è stato indicato',
        'ja': '学ぶものがありません — カリキュラムは空で、テーマも指定されていません',
        'zh': '没有可学习的内容——学习计划为空，也未指定主题',
        'hi': 'पढ़ने के लिए कुछ नहीं — पाठ्यक्रम खाली है और कोई विषय नहीं बताया गया',
        'ar': 'لا شيء للدراسة — المنهج فارغ ولم يُذكر أي موضوع',
    },
    'this excursion has no findings to learn': {
        'es': 'esta excursión no tiene hallazgos que aprender',
        'fr': 'cette excursion n\'a aucun résultat à apprendre',
        'de': 'diese Exkursion hat keine Erkenntnisse zum Lernen',
        'pt': 'esta excursão não tem descobertas para aprender',
        'it': 'questa escursione non ha risultati da apprendere',
        'ja': 'このエクスカーションには、学べる知見がありません',
        'zh': '此次外出探索没有可供学习的发现',
        'hi': 'इस भ्रमण में सीखने योग्य कोई निष्कर्ष नहीं',
        'ar': 'لا توجد نتائج قابلة للتعلّم في هذه الرحلة',
    },
    'authentication required': {
        'es': 'se requiere autenticación',
        'fr': 'authentification requise',
        'de': 'Authentifizierung erforderlich',
        'pt': 'autenticação necessária',
        'it': 'autenticazione richiesta',
        'ja': '認証が必要です',
        'zh': '需要身份验证',
        'hi': 'प्रमाणीकरण आवश्यक है',
        'ar': 'المصادقة مطلوبة',
    },
    'not authorized for this user': {
        'es': 'sin autorización para este usuario',
        'fr': 'non autorisé pour cet utilisateur',
        'de': 'keine Berechtigung für diesen Benutzer',
        'pt': 'sem autorização para este utilizador',
        'it': 'non autorizzato per questo utente',
        'ja': 'このユーザーへの権限がありません',
        'zh': '无权访问此用户',
        'hi': 'इस उपयोगकर्ता के लिए अधिकार नहीं है',
        'ar': 'غير مخوَّل لهذا المستخدم',
    },
    'user not found': {
        'es': 'usuario no encontrado',
        'fr': 'utilisateur introuvable',
        'de': 'Benutzer nicht gefunden',
        'pt': 'utilizador não encontrado',
        'it': 'utente non trovato',
        'ja': 'ユーザーが見つかりません',
        'zh': '未找到用户',
        'hi': 'उपयोगकर्ता नहीं मिला',
        'ar': 'لم يتم العثور على المستخدم',
    },
    'this homepage is not shared': {
        'es': 'esta página personal no está compartida',
        'fr': "cette page personnelle n'est pas partagée",
        'de': 'diese Seite wird nicht geteilt',
        'pt': 'esta página pessoal não está partilhada',
        'it': 'questa pagina personale non è condivisa',
        'ja': 'このホームページは共有されていません',
        'zh': '这个主页未被分享',
        'hi': 'यह पन्ना साझा नहीं किया गया है',
        'ar': 'هذه الصفحة غير مُشارَكة',
    },

    # --- the medication cabinet ------------------------------------------
    "a medication has a name and a dose — your words are fine ('the little "
    "white one, 10 mg')": {
        'es': 'un medicamento tiene un nombre y una dosis — tus propias '
              'palabras valen («la pastillita blanca, 10 mg»)',
        'fr': 'un médicament a un nom et une dose — vos propres mots '
              'suffisent (« le petit blanc, 10 mg »)',
        'de': 'ein Medikament hat einen Namen und eine Dosis — Ihre eigenen '
              'Worte genügen („das kleine weiße, 10 mg“)',
        'pt': 'um medicamento tem um nome e uma dose — as suas próprias '
              'palavras servem («o branquinho, 10 mg»)',
        'it': 'un farmaco ha un nome e una dose — bastano le tue parole '
              '(«quello bianco piccolo, 10 mg»)',
        'ja': '薬には名前と用量があります — ご自身の言葉で構いません'
              '（「小さい白いの、10 mg」）',
        'zh': '一种药有名称和剂量 — 用你自己的说法就行（“那个白色的小药片，'
              '10 毫克”）',
        'hi': 'दवा का एक नाम और एक खुराक होती है — आपके अपने शब्द ठीक हैं '
              "('वह छोटी सफ़ेद वाली, 10 mg')",
        'ar': 'للدواء اسم وجرعة — كلماتك الخاصة تكفي '
              '(”تلك البيضاء الصغيرة، 10 ملغ“)',
    },
    "a schedule names times (e.g. ['08:00','20:00']) or is "
    "{'as_needed': true}": {
        'es': "un horario indica horas (p. ej. ['08:00','20:00']) o es "
              "{'as_needed': true}",
        'fr': "un horaire indique des heures (p. ex. ['08:00','20:00']) ou "
              "vaut {'as_needed': true}",
        'de': "ein Zeitplan nennt Uhrzeiten (z. B. ['08:00','20:00']) oder "
              "ist {'as_needed': true}",
        'pt': "um horário indica horas (p. ex. ['08:00','20:00']) ou é "
              "{'as_needed': true}",
        'it': "un orario indica delle ore (es. ['08:00','20:00']) oppure è "
              "{'as_needed': true}",
        'ja': "スケジュールには時刻を並べるか（例 ['08:00','20:00']）、"
              "{'as_needed': true} を指定します",
        'zh': "用药时间表要列出时刻（例如 ['08:00','20:00']），或写成 "
              "{'as_needed': true}",
        'hi': "समय-सारणी में समय दिए जाते हैं (जैसे ['08:00','20:00']) या वह "
              "{'as_needed': true} होती है",
        'ar': "الجدول يذكر أوقاتًا (مثل ['08:00','20:00']) أو يكون "
              "{'as_needed': true}",
    },
    "action is 'taken' or 'skipped'": {
        'es': "la acción es 'taken' o 'skipped'",
        'fr': "l'action vaut 'taken' ou 'skipped'",
        'de': "die Aktion ist 'taken' oder 'skipped'",
        'pt': "a ação é 'taken' ou 'skipped'",
        'it': "l'azione è 'taken' oppure 'skipped'",
        'ja': "action は 'taken' か 'skipped' です",
        'zh': "action 只能是 'taken' 或 'skipped'",
        'hi': "क्रिया 'taken' या 'skipped' होती है",
        'ar': "الإجراء إما 'taken' أو 'skipped'",
    },
    'an as-needed medication has no slots': {
        'es': 'un medicamento a demanda no tiene franjas horarias',
        'fr': 'un médicament pris au besoin n’a pas de créneaux',
        'de': 'ein Bedarfsmedikament hat keine Zeitfenster',
        'pt': 'um medicamento em SOS não tem faixas horárias',
        'it': 'un farmaco al bisogno non ha fasce orarie',
        'ja': '頓服の薬に服用枠はありません',
        'zh': '按需服用的药没有固定时段',
        'hi': 'आवश्यकतानुसार ली जाने वाली दवा के लिए कोई समय-खंड नहीं होता',
        'ar': 'الدواء عند اللزوم ليس له مواعيد محددة',
    },
    'max_per_day must be at least 1': {
        'es': 'max_per_day debe ser al menos 1',
        'fr': 'max_per_day doit valoir au moins 1',
        'de': 'max_per_day muss mindestens 1 sein',
        'pt': 'max_per_day tem de ser pelo menos 1',
        'it': 'max_per_day deve essere almeno 1',
        'ja': 'max_per_day は 1 以上にしてください',
        'zh': 'max_per_day 至少为 1',
        'hi': 'max_per_day कम से कम 1 होना चाहिए',
        'ar': 'يجب ألا يقل max_per_day عن 1',
    },
    'no such medication': {
        'es': 'no existe ese medicamento',
        'fr': 'ce médicament n’existe pas',
        'de': 'dieses Medikament gibt es nicht',
        'pt': 'não existe esse medicamento',
        'it': 'quel farmaco non esiste',
        'ja': 'その薬はありません',
        'zh': '没有这种药',
        'hi': 'ऐसी कोई दवा नहीं',
        'ar': 'لا يوجد دواء بهذا الاسم',
    },
    'schedule must be an object': {
        'es': 'schedule debe ser un objeto',
        'fr': 'schedule doit être un objet',
        'de': 'schedule muss ein Objekt sein',
        'pt': 'schedule tem de ser um objeto',
        'it': 'schedule deve essere un oggetto',
        'ja': 'schedule はオブジェクトにしてください',
        'zh': 'schedule 必须是一个对象',
        'hi': 'schedule एक ऑब्जेक्ट होना चाहिए',
        'ar': 'يجب أن يكون schedule كائنًا',
    },

    # --- the vigil and the crash watch -----------------------------------
    "a vigil needs a steward's name and a way to reach them": {
        'es': 'una vigilia necesita el nombre de un custodio y una forma de '
              'contactarlo',
        'fr': 'une veille a besoin du nom d’un référent et d’un moyen de le '
              'joindre',
        'de': 'eine Wache braucht den Namen einer vertrauten Person und '
              'einen Weg, sie zu erreichen',
        'pt': 'uma vigília precisa do nome de um responsável e de uma forma '
              'de o contactar',
        'it': 'una veglia ha bisogno del nome di un referente e di un modo '
              'per contattarlo',
        'ja': '見守りには世話役の名前と連絡手段が必要です',
        'zh': '守护需要一位负责人的姓名和联系方式',
        'hi': 'निगरानी के लिए एक संरक्षक का नाम और उन तक पहुँचने का तरीका चाहिए',
        'ar': 'يحتاج السهر إلى اسم القيّم وطريقة للوصول إليه',
    },
    'quiet_days must be between half a day and 60': {
        'es': 'quiet_days debe estar entre medio día y 60',
        'fr': 'quiet_days doit être compris entre une demi-journée et 60',
        'de': 'quiet_days muss zwischen einem halben Tag und 60 liegen',
        'pt': 'quiet_days tem de estar entre meio dia e 60',
        'it': 'quiet_days deve essere compreso tra mezza giornata e 60',
        'ja': 'quiet_days は半日から 60 のあいだにしてください',
        'zh': 'quiet_days 必须在半天到 60 之间',
        'hi': 'quiet_days आधे दिन से 60 के बीच होना चाहिए',
        'ar': 'يجب أن يكون quiet_days بين نصف يوم و60',
    },
    "the crash watch needs a trusted person's name and a way to reach them": {
        'es': 'la vigilancia de caídas necesita el nombre de una persona de '
              'confianza y una forma de contactarla',
        'fr': 'la veille d’urgence a besoin du nom d’une personne de '
              'confiance et d’un moyen de la joindre',
        'de': 'die Notfallwache braucht den Namen einer vertrauten Person '
              'und einen Weg, sie zu erreichen',
        'pt': 'a vigilância de quedas precisa do nome de uma pessoa de '
              'confiança e de uma forma de a contactar',
        'it': 'la sorveglianza di emergenza ha bisogno del nome di una '
              'persona fidata e di un modo per contattarla',
        'ja': '緊急見守りには信頼できる人の名前と連絡手段が必要です',
        'zh': '紧急守护需要一位可信赖的人的姓名和联系方式',
        'hi': 'क्रैश वॉच के लिए एक भरोसेमंद व्यक्ति का नाम और उन तक पहुँचने का '
              'तरीका चाहिए',
        'ar': 'تحتاج مراقبة الطوارئ إلى اسم شخص موثوق وطريقة للوصول إليه',
    },

    # --- the watch bridge -------------------------------------------------
    'no readings recognized — use keys like heart_rate, blood_oxygen, '
    'respiratory_rate, or movement: fall': {
        'es': 'no se reconoció ninguna lectura — usa claves como heart_rate, '
              'blood_oxygen, respiratory_rate o movement: fall',
        'fr': 'aucune mesure reconnue — utilisez des clés comme heart_rate, '
              'blood_oxygen, respiratory_rate ou movement: fall',
        'de': 'keine Messwerte erkannt — verwenden Sie Schlüssel wie '
              'heart_rate, blood_oxygen, respiratory_rate oder movement: fall',
        'pt': 'nenhuma leitura reconhecida — use chaves como heart_rate, '
              'blood_oxygen, respiratory_rate ou movement: fall',
        'it': 'nessuna lettura riconosciuta — usa chiavi come heart_rate, '
              'blood_oxygen, respiratory_rate o movement: fall',
        'ja': '認識できる測定値がありません — heart_rate、blood_oxygen、'
              'respiratory_rate、movement: fall などのキーを使ってください',
        'zh': '未识别到任何读数 — 请使用 heart_rate、blood_oxygen、'
              'respiratory_rate 或 movement: fall 之类的键',
        'hi': 'कोई रीडिंग पहचानी नहीं गई — heart_rate, blood_oxygen, '
              'respiratory_rate या movement: fall जैसी कुंजियाँ इस्तेमाल करें',
        'ar': 'لم يتم التعرف على أي قراءات — استخدم مفاتيح مثل heart_rate أو '
              'blood_oxygen أو respiratory_rate أو movement: fall',
    },
    'no such channel — check the drip URL, or rotate the token in Settings '
    'and re-copy it': {
        'es': 'no existe ese canal — revisa la URL del enlace, o rota el '
              'token en Ajustes y vuelve a copiarlo',
        'fr': 'ce canal n’existe pas — vérifiez l’URL du flux, ou renouvelez '
              'le jeton dans Réglages et recopiez-le',
        'de': 'diesen Kanal gibt es nicht — prüfen Sie die Drip-URL, oder '
              'erneuern Sie das Token in den Einstellungen und kopieren Sie '
              'es neu',
        'pt': 'não existe esse canal — verifique o URL do fluxo, ou rode o '
              'token em Definições e copie-o de novo',
        'it': 'quel canale non esiste — controlla l’URL del flusso, oppure '
              'ruota il token in Impostazioni e ricopialo',
        'ja': 'そのチャンネルはありません — 送信 URL を確認するか、設定で'
              'トークンを更新してコピーし直してください',
        'zh': '没有这个通道 — 请检查推送 URL，或在设置中轮换令牌后重新复制',
        'hi': 'ऐसा कोई चैनल नहीं — ड्रिप URL जाँचें, या सेटिंग्स में टोकन बदलकर '
              'उसे फिर से कॉपी करें',
        'ar': 'لا توجد قناة بهذا الاسم — تحقق من رابط الإرسال، أو غيّر الرمز '
              'في الإعدادات وانسخه من جديد',
    },
    "no usable readings in that export — it may predate the watch, or hold "
    "only types JIM doesn't track": {
        'es': 'no hay lecturas utilizables en esa exportación — puede ser '
              'anterior al reloj, o contener solo tipos que JIM no sigue',
        'fr': 'aucune mesure exploitable dans cet export — il peut être '
              'antérieur à la montre, ou ne contenir que des types que JIM '
              'ne suit pas',
        'de': 'keine verwertbaren Messwerte in diesem Export — er kann älter '
              'als die Uhr sein oder nur Typen enthalten, die JIM nicht '
              'verfolgt',
        'pt': 'não há leituras utilizáveis nessa exportação — pode ser '
              'anterior ao relógio, ou conter apenas tipos que o JIM não '
              'acompanha',
        'it': 'nessuna lettura utilizzabile in quell’esportazione — potrebbe '
              'precedere l’orologio, o contenere solo tipi che JIM non segue',
        'ja': 'そのエクスポートに使える測定値がありません — 時計より前のもの'
              'か、JIM が扱わない種類だけかもしれません',
        'zh': '该导出中没有可用的读数 — 它可能早于这块手表，或只包含 JIM '
              '不追踪的类型',
        'hi': 'उस निर्यात में कोई उपयोगी रीडिंग नहीं — वह घड़ी से पुराना हो सकता '
              'है, या उसमें केवल वे प्रकार हैं जिन्हें JIM नहीं रखता',
        'ar': 'لا توجد قراءات صالحة في ذلك التصدير — قد يكون أقدم من الساعة، '
              'أو يحتوي فقط على أنواع لا يتتبعها JIM',
    },
    "that file isn't a Health export — expected export.zip or export.xml "
    "from the Health app": {
        'es': 'ese archivo no es una exportación de Salud — se esperaba '
              'export.zip o export.xml de la app Salud',
        'fr': 'ce fichier n’est pas un export Santé — export.zip ou '
              'export.xml de l’app Santé était attendu',
        'de': 'diese Datei ist kein Health-Export — erwartet wurden '
              'export.zip oder export.xml aus der Health-App',
        'pt': 'esse ficheiro não é uma exportação da Saúde — esperava-se '
              'export.zip ou export.xml da app Saúde',
        'it': 'quel file non è un’esportazione di Salute — attesi export.zip '
              'o export.xml dall’app Salute',
        'ja': 'そのファイルはヘルスケアの書き出しではありません — ヘルスケア '
              'App の export.zip か export.xml が必要です',
        'zh': '该文件不是“健康”导出 — 需要“健康”App 导出的 export.zip 或 '
              'export.xml',
        'hi': 'वह फ़ाइल Health निर्यात नहीं है — Health ऐप से export.zip या '
              'export.xml अपेक्षित है',
        'ar': 'هذا الملف ليس تصديرًا من تطبيق الصحة — المتوقع export.zip أو '
              'export.xml من تطبيق الصحة',
    },
    'that zip has no export.xml and no Fitbit files inside — export again '
    'from the Health app, or from Google Takeout for a Fitbit': {
        'es': 'ese zip no contiene export.xml ni archivos de Fitbit — vuelve '
              'a exportar desde la app Salud, o desde Google Takeout para un '
              'Fitbit',
        'fr': 'ce zip ne contient ni export.xml ni fichiers Fitbit — '
              'refaites l’export depuis l’app Santé, ou depuis Google '
              'Takeout pour un Fitbit',
        'de': 'in diesem Zip fehlen export.xml und Fitbit-Dateien — '
              'exportieren Sie erneut aus der Health-App oder über Google '
              'Takeout für ein Fitbit',
        'pt': 'esse zip não contém export.xml nem ficheiros Fitbit — '
              'exporte de novo a partir da app Saúde, ou do Google Takeout '
              'para um Fitbit',
        'it': 'quel zip non contiene export.xml né file Fitbit — esporta di '
              'nuovo dall’app Salute, o da Google Takeout per un Fitbit',
        'ja': 'そのzipにはexport.xmlもFitbitのファイルも含まれていません — '
              'ヘルスケアアプリから再度書き出すか、FitbitならGoogle '
              'Takeoutから書き出してください',
        'zh': '该zip中没有export.xml，也没有Fitbit文件——请从健康App重新导出，'
              'Fitbit则从Google Takeout导出',
        'hi': 'उस zip में export.xml नहीं है और न ही Fitbit फ़ाइलें — Health '
              'ऐप से दोबारा निर्यात करें, या Fitbit के लिए Google Takeout से',
        'ar': 'هذا الملف المضغوط لا يحتوي على export.xml ولا ملفات Fitbit — '
              'صدّر مجددًا من تطبيق الصحة، أو من Google Takeout لجهاز Fitbit',
    },
    'that zip has no export.xml inside — export again from the Health app': {
        'es': 'ese zip no contiene export.xml — vuelve a exportar desde la '
              'app Salud',
        'fr': 'ce zip ne contient pas export.xml — refaites l’export depuis '
              'l’app Santé',
        'de': 'in diesem Zip fehlt export.xml — exportieren Sie erneut aus '
              'der Health-App',
        'pt': 'esse zip não contém export.xml — exporte de novo a partir da '
              'app Saúde',
        'it': 'quello zip non contiene export.xml — esporta di nuovo dall’app '
              'Salute',
        'ja': 'その zip に export.xml が入っていません — ヘルスケア App から'
              '書き出し直してください',
        'zh': '该 zip 中没有 export.xml — 请从“健康”App 重新导出',
        'hi': 'उस zip में export.xml नहीं है — Health ऐप से दोबारा निर्यात करें',
        'ar': 'لا يحتوي هذا الملف المضغوط على export.xml — صدِّر مرة أخرى من '
              'تطبيق الصحة',
    },
    'the upload was empty': {
        'es': 'el archivo subido estaba vacío',
        'fr': 'le fichier envoyé était vide',
        'de': 'der Upload war leer',
        'pt': 'o ficheiro enviado estava vazio',
        'it': 'il file caricato era vuoto',
        'ja': 'アップロードが空でした',
        'zh': '上传的内容为空',
        'hi': 'अपलोड खाली था',
        'ar': 'كان الملف المرفوع فارغًا',
    },

    # --- movement and food ------------------------------------------------
    'days must be between 1 and 7': {
        'es': 'los días deben estar entre 1 y 7',
        'fr': 'le nombre de jours doit être compris entre 1 et 7',
        'de': 'die Tage müssen zwischen 1 und 7 liegen',
        'pt': 'os dias têm de estar entre 1 e 7',
        'it': 'i giorni devono essere compresi tra 1 e 7',
        'ja': '日数は 1 から 7 のあいだにしてください',
        'zh': '天数必须在 1 到 7 之间',
        'hi': 'दिन 1 से 7 के बीच होने चाहिए',
        'ar': 'يجب أن تكون الأيام بين 1 و7',
    },
    'minutes must be between 5 and 90': {
        'es': 'los minutos deben estar entre 5 y 90',
        'fr': 'les minutes doivent être comprises entre 5 et 90',
        'de': 'die Minuten müssen zwischen 5 und 90 liegen',
        'pt': 'os minutos têm de estar entre 5 e 90',
        'it': 'i minuti devono essere compresi tra 5 e 90',
        'ja': '分数は 5 から 90 のあいだにしてください',
        'zh': '分钟数必须在 5 到 90 之间',
        'hi': 'मिनट 5 से 90 के बीच होने चाहिए',
        'ar': 'يجب أن تكون الدقائق بين 5 و90',
    },
}


# --------------------------------------------------------------------------- #
# The refusal that handed the body back
# --------------------------------------------------------------------------- #
#
# The round before this one put every refusal this product *writes* into the
# reader's language, through nine handlers that all return by one door. It
# missed every refusal this product *returns*.
#
#     asked     is every refusal this product writes translated
#     mattered  is every refusal this product returns
#
# `RequestValidationError` is not an `HTTPException` and is not one of the
# eight domain errors either. FastAPI raises it before routing finishes and
# renders it with its own handler, so a 422 — the refusal a person meets most
# often, because it is what a mistyped form produces — went out past all nine.
#
# ## The larger half
#
# Pydantic's error rows carry an `input` key holding **the value that failed**,
# which for a missing field is the entire submitted body. So a journal entry
# came straight back out:
#
#     {"type": "missing", "loc": ["body", "text"], "msg": "Field required",
#      "input": {"entry": "chest pain since Tuesday, have not told my
#                daughter", "mood": 3}}
#
# Every other part of this product's error design refuses to carry content.
# `app/src/errors.ts` and the three `Problems` shells record a method, a
# redacted path and a status, and have no parameter a message could arrive
# through. `cloudgw` refuses a report whole if it finds prose in it rather
# than sanitising it. The one place content left the process was the
# framework's default renderer, because nobody had looked at it as ours.
#
#     asked     does this product record anything private
#     mattered  does this product return anything private
#
# ## What is returned now
#
# `type` and `loc`, which are the console's vocabulary — it highlights the
# field `loc` names — and `msg`. Not `input`, and not `ctx`: `ctx` carries a
# validator's own exception on `value_error`, which is a second door into the
# same room.
#
# Two narrower rules, both for text that comes from *our* code rather than
# pydantic's fixed catalogue:
#
# * `value_error` and `assertion_error` messages are replaced outright. Their
#   text is whatever a validator raised, and a validator that quotes the value
#   it rejected is the same leak wearing a different key.
# * On `extra_forbidden`, the last element of `loc` is the caller's own key
#   name rather than a field this product declares — so it is echoed only when
#   it is *shaped* like a field name. Naming the key is the point of that
#   refusal; a key with spaces in it is not a typo, it is content.


#: What is said instead of a validator's own words. Deliberately useless as a
#: hint: `loc` still names the field, and a sentence that explained more would
#: be quoting the thing this exists to stop quoting.
UNSPECIFIED_VALUE_ERROR = "that value is not acceptable here"

#: Where a caller's own key name would otherwise be echoed.
UNRECOGNISED_FIELD = "<unrecognised field>"

#: What a mistyped field name looks like. A key matching this is echoed back on
#: `extra_forbidden`, because naming it is the whole value of that refusal:
#: `test_a_write_that_answers_200_did_something` exists because two routes used
#: to accept `dials` for `values` and `years` for `period`, discard them, and
#: answer 200. A round was spent making those strict so the caller is *told*
#: which key was wrong, and the first version of this file redacted it away
#: again — caught by that guard, which is what it was written for.
#:
#:     asked     can a key carry content
#:     mattered  does this key look like content
#:
#: Anything else — a key with spaces in it, a sentence, something longer than a
#: field name has any business being — is replaced. A client that builds an
#: object keyed on what somebody typed produces exactly that shape.
_FIELD_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,39}$")

_OUR_OWN_WORDS = ("value_error", "assertion_error")


def validation_detail(errors, language: str) -> list[dict]:
    """Pydantic's error rows, with everything the caller sent taken out.

    Built by allowing three keys rather than by removing `input`. A denylist
    would have to be revisited every time pydantic adds a key; this cannot
    grow a leak by someone else's release.
    """
    rows = []
    for error in errors:
        kind = str(error.get("type", ""))
        where = list(error.get("loc", ()))
        if (kind == "extra_forbidden" and where
                and not _FIELD_NAME.match(str(where[-1]))):
            where[-1] = UNRECOGNISED_FIELD
        message = (UNSPECIFIED_VALUE_ERROR if kind in _OUR_OWN_WORDS
                   else str(error.get("msg", "")))
        rows.append({
            "type": kind,
            "loc": [p if isinstance(p, int) else str(p) for p in where],
            "msg": tr_refusal(message, language),
        })
    return rows


#: The first element of a pydantic `loc`, naming which part of the request the
#: field was in rather than naming a field. Dropped when composing the
#: sentence: a person reading "body.display_name" learns nothing from "body"
#: that the form they are looking at has not already told them.
_WHERE_MARKERS = ("body", "query", "path", "header", "cookie")


#: The label the form shows, for the fields a person types into one.
#:
#: `validation_message` used to render pydantic's own field name, so a mistyped
#: form said `display_name — Field required` while the form beside it said
#: something a person could read, in ten languages.
#:
#:     asked     is the refusal a sentence in the reader's language
#:     mattered  does it name the field the reader can see
#:
#: Server-side, where the sentence is composed, for the reason it is composed
#: here at all: nine clients rendering it is nine chances to render it
#: differently.
#:
#: The rows shared with the sibling products carry the sibling products'
#: wording, byte for byte. One vocabulary across three products is one thing to
#: keep right; three is three, and the drift shows up first in the language
#: nobody here reads.
#:
#: A field with no row keeps its identifier — an identifier a reader can match
#: to the form beats a word invented for them — and is recorded in
#: `jim/tests/field_labels_unmapped.txt`.
_FIELD_LABELS: dict[str, dict[str, str]] = {
    # The phone line's event body (jim/models.ReachOutEvent) — 3.0.8.
    'caller': {'en': 'The number calling', 'es': 'El número que llama', 'fr': 'Le numéro qui appelle', 'de': 'Die anrufende Nummer', 'pt': 'O número que liga', 'it': 'Il numero che chiama', 'ja': '発信元の番号', 'zh': '来电号码', 'hi': 'कॉल करने वाला नंबर', 'ar': 'الرقم المتصل'},
    'called': {'en': 'The number they rang', 'es': 'El número al que llamaron', 'fr': 'Le numéro composé', 'de': 'Die gewählte Nummer', 'pt': 'O número para que ligaram', 'it': 'Il numero chiamato', 'ja': 'かけられた番号', 'zh': '被叫号码', 'hi': 'जिस नंबर पर कॉल की गई', 'ar': 'الرقم الذي اتصلوا به'},
    'house': {'en': 'The phone house', 'es': 'La operadora telefónica', 'fr': "L'opérateur téléphonique", 'de': 'Der Telefonanbieter', 'pt': 'A operadora telefónica', 'it': "L'operatore telefonico", 'ja': '電話事業者', 'zh': '电话服务商', 'hi': 'फ़ोन सेवा प्रदाता', 'ar': 'مزوّد خدمة الهاتف'},
    'vendor_ref': {'en': "The phone house's reference for the call", 'es': 'La referencia de la operadora para la llamada', 'fr': "La référence de l'opérateur pour l'appel", 'de': 'Die Referenz des Anbieters für den Anruf', 'pt': 'A referência da operadora para a chamada', 'it': "Il riferimento dell'operatore per la chiamata", 'ja': '事業者側の通話参照番号', 'zh': '服务商的通话参考号', 'hi': 'कॉल के लिए सेवा प्रदाता का संदर्भ', 'ar': 'مرجع مزوّد الخدمة للمكالمة'},
    'event': {'en': 'What the phone line reported', 'es': 'Lo que reportó la línea telefónica', 'fr': 'Ce que la ligne téléphonique a signalé', 'de': 'Was die Telefonleitung gemeldet hat', 'pt': 'O que a linha telefónica reportou', 'it': 'Cosa ha riportato la linea telefonica', 'ja': '電話回線が報告した内容', 'zh': '电话线路报告的内容', 'hi': 'फ़ोन लाइन ने क्या सूचना दी', 'ar': 'ما أبلغ عنه خط الهاتف'},
    'seconds': {'en': 'Seconds', 'es': 'Segundos', 'fr': 'Secondes', 'de': 'Sekunden', 'pt': 'Segundos', 'it': 'Secondi', 'ja': '秒', 'zh': '秒', 'hi': 'सेकंड', 'ar': 'الثواني'},
    "detail": {"en": "The move's argument", "es": "El argumento del movimiento", "fr": "L'argument du geste", "de": "Das Argument der Bewegung", "pt": "O argumento do movimento", "it": "L'argomento della mossa", "ja": "動作の引数", "zh": "该动作的参数", "hi": "चाल का तर्क", "ar": "معطى الحركة"},
    # The hands (jim/hands.py), worded exactly as the sibling product
    # words them. Somebody who read the grant card on one console and
    # then meets a refusal on the other has to be reading the same
    # noun for the same box.
    "about_step": {"en": "The step this is a report about", "es": "El paso del que se informa", "fr": "L'étape dont il s'agit", "de": "Der Schritt, um den es geht", "pt": "O passo de que se trata", "it": "Il passo di cui si riferisce", "ja": "報告の対象となる手順", "zh": "此报告所指的步骤", "hi": "वह चरण जिसकी यह रिपोर्ट है", "ar": "الخطوة التي يتعلق بها هذا التقرير"},
    # The reach-out cascade (jim/reachout.py, jim/models.py): the fields a
    # provider's webhook or a caller fills to run a call to an emergency
    # contact.
    "contacts": {"en": "The emergency contacts, in order", "es": "Los contactos de emergencia, en orden", "fr": "Les contacts d'urgence, dans l'ordre", "de": "Die Notfallkontakte, der Reihe nach", "pt": "Os contactos de emergência, por ordem", "it": "I contatti di emergenza, in ordine", "ja": "緊急連絡先（順番）", "zh": "紧急联系人（按顺序）", "hi": "आपातकालीन संपर्क, क्रम में", "ar": "جهات اتصال الطوارئ بالترتيب"},
    "digit": {"en": "The key they pressed", "es": "La tecla que pulsaron", "fr": "La touche qu'ils ont pressée", "de": "Die gedrückte Taste", "pt": "A tecla que premiram", "it": "Il tasto premuto", "ja": "押されたキー", "zh": "所按的按键", "hi": "दबाई गई कुंजी", "ar": "المفتاح الذي ضُغط"},
    "heard": {"en": "What the contact said", "es": "Lo que dijo el contacto", "fr": "Ce que le contact a dit", "de": "Was der Kontakt sagte", "pt": "O que o contacto disse", "it": "Cosa ha detto il contatto", "ja": "連絡先が話した内容", "zh": "联系人所说的话", "hi": "संपर्क ने क्या कहा", "ar": "ما قاله جهة الاتصال"},
    "life_threatening": {"en": "Whether it is life-threatening", "es": "Si es potencialmente mortal", "fr": "S'il y a danger de mort", "de": "Ob Lebensgefahr besteht", "pt": "Se é potencialmente fatal", "it": "Se è pericoloso per la vita", "ja": "生命に関わるかどうか", "zh": "是否危及生命", "hi": "क्या यह जानलेवा है", "ar": "ما إذا كان يهدد الحياة"},
    "detail": {"en": "The move's argument", "es": "El argumento del movimiento", "fr": "L'argument du geste", "de": "Das Argument der Bewegung", "pt": "O argumento do movimento", "it": "L'argomento della mossa", "ja": "動作の引数", "zh": "该动作的参数", "hi": "चाल का तर्क", "ar": "معطى الحركة"},
    "errand": {"en": "What it should do", "es": "Qué debe hacer", "fr": "Ce qu'il doit faire", "de": "Was es tun soll", "pt": "O que deve fazer", "it": "Cosa deve fare", "ja": "してほしいこと", "zh": "它该做什么", "hi": "इसे क्या करना है", "ar": "ما ينبغي أن يفعله"},
    "frame": {"en": "The picture of the screen", "es": "La imagen de la pantalla", "fr": "L'image de l'écran", "de": "Das Bild vom Bildschirm", "pt": "A imagem do ecrã", "it": "L'immagine dello schermo", "ja": "画面の画像", "zh": "屏幕的图像", "hi": "स्क्रीन की तस्वीर", "ar": "صورة الشاشة"},
    "grant_id": {"en": "Which permission", "es": "Qué permiso", "fr": "Quelle permission", "de": "Welche Erlaubnis", "pt": "Que permissão", "it": "Quale permesso", "ja": "どの許可", "zh": "用哪个许可", "hi": "कौन-सी अनुमति", "ar": "أي إذن"},
    "in_words": {"en": "The permission, in your own words", "es": "El permiso, con tus propias palabras", "fr": "La permission, avec vos propres mots", "de": "Die Erlaubnis, in deinen eigenen Worten", "pt": "A permissão, nas suas próprias palavras", "it": "Il permesso, con parole tue", "ja": "許可を、あなた自身の言葉で", "zh": "用你自己的话说出这个许可", "hi": "अनुमति, आपके अपने शब्दों में", "ar": "الإذن، بكلماتك أنت"},
    "landed": {"en": "What became of that step on the machine", "es": "Qué fue de ese paso en la máquina", "fr": "Ce qu'est devenue cette étape sur la machine", "de": "Was aus diesem Schritt auf der Maschine wurde", "pt": "O que aconteceu a esse passo na máquina", "it": "Che ne è stato di quel passo sulla macchina", "ja": "その手順がマシン上でどうなったか", "zh": "该步骤在那台机器上的结果", "hi": "मशीन पर उस चरण का क्या हुआ", "ar": "ما آل إليه ذلك الإجراء على الآلة"},
    "landed_note": {"en": "Why it did not happen", "es": "Por qué no ocurrió", "fr": "Pourquoi cela n'a pas eu lieu", "de": "Warum es nicht passiert ist", "pt": "Porque não aconteceu", "it": "Perché non è successo", "ja": "実行されなかった理由", "zh": "未能发生的原因", "hi": "यह क्यों नहीं हुआ", "ar": "لماذا لم يحدث"},
    "learned": {"en": "How it was learned", "es": "Cómo se aprendió", "fr": "Comment il a été appris", "de": "Wie es gelernt wurde", "pt": "Como foi aprendido", "it": "Come è stato imparato", "ja": "どう覚えたか", "zh": "是怎么学会的", "hi": "यह कैसे सीखा गया", "ar": "كيف تعلَّمه"},
    "places": {"en": "Apps or sites", "es": "Aplicaciones o sitios", "fr": "Applications ou sites", "de": "Apps oder Seiten", "pt": "Aplicações ou sites", "it": "App o siti", "ja": "アプリまたはサイト", "zh": "应用或网站", "hi": "ऐप या साइट", "ar": "تطبيقات أو مواقع"},
    "reach_id": {"en": "Which session", "es": "Qué sesión", "fr": "Quelle session", "de": "Welche Sitzung", "pt": "Que sessão", "it": "Quale sessione", "ja": "どのセッション", "zh": "哪一次会话", "hi": "कौन-सा सत्र", "ar": "أي جلسة"},
    "saw": {"en": "What the eyes read on the screen", "es": "Lo que los ojos leyeron en la pantalla", "fr": "Ce que les yeux ont lu à l'écran", "de": "Was die Augen auf dem Bildschirm lasen", "pt": "O que os olhos leram no ecrã", "it": "Cosa hanno letto gli occhi sullo schermo", "ja": "目が画面から読み取った内容", "zh": "眼睛在屏幕上读到的内容", "hi": "आँखों ने स्क्रीन पर क्या पढ़ा", "ar": "ما قرأته العينان على الشاشة"},
    "steps": {"en": "Steps", "es": "Pasos", "fr": "Étapes", "de": "Schritte", "pt": "Passos", "it": "Passi", "ja": "手数", "zh": "步数", "hi": "चरण", "ar": "خطوات"},
    'surface': {'en': 'Surface', 'es': 'Superficie', 'fr': 'Surface', 'de': 'Fläche', 'pt': 'Superfície', 'it': 'Superficie', 'ja': 'サーフェス', 'zh': '表面', 'hi': 'सतह', 'ar': 'السطح'},
    "to_user_id": {"en": "Who it is handed to", "es": "A quién se le entrega", "fr": "À qui c'est confié", "de": "Wem es übergeben wird", "pt": "A quem é entregue", "it": "A chi viene passato", "ja": "誰に渡すか", "zh": "交给谁", "hi": "किसे सौंपा जा रहा है", "ar": "إلى مَن يُسلَّم"},
    "verb": {"en": "The move", "es": "El movimiento", "fr": "Le geste", "de": "Die Bewegung", "pt": "O movimento", "it": "La mossa", "ja": "動作", "zh": "动作", "hi": "चाल", "ar": "الحركة"},
    "verbs": {"en": "The moves it may make", "es": "Los movimientos que puede hacer", "fr": "Les gestes qu'il peut faire", "de": "Die Bewegungen, die es machen darf", "pt": "Os movimentos que pode fazer", "it": "Le mosse che può fare", "ja": "許される動作", "zh": "它可以做的动作", "hi": "जो चालें यह चल सकता है", "ar": "الحركات المسموح بها"},
    "watched": {"en": "Only while somebody is watching", "es": "Solo mientras alguien mira", "fr": "Seulement pendant que quelqu'un regarde", "de": "Nur solange jemand zusieht", "pt": "Apenas enquanto alguém observa", "it": "Solo mentre qualcuno guarda", "ja": "誰かが見ている間だけ", "zh": "仅在有人看着时", "hi": "केवल जब कोई देख रहा हो", "ar": "فقط بينما يراقب أحد"},
    "why": {"en": "Why it stopped", "es": "Por qué se detuvo", "fr": "Pourquoi il s'est arrêté", "de": "Warum es aufgehört hat", "pt": "Porque parou", "it": "Perché si è fermato", "ja": "止まった理由", "zh": "为何停下", "hi": "यह क्यों रुका", "ar": "لماذا توقّف"},
    "shown": {"en": "The picture being shown for this turn", "es": "La imagen que se muestra en este turno", "fr": "L'image montrée pour ce tour", "de": "Das für diesen Zug gezeigte Bild", "pt": "A imagem mostrada nesta vez", "it": "L'immagine mostrata per questo turno", "ja": "このターンで見せる画像", "zh": "本轮展示的图片", "hi": "इस बारी में दिखाई जा रही तस्वीर", "ar": "الصورة المعروضة لهذا الدور"},
    'url': {'en': 'Page address', 'es': 'Dirección de la página', 'fr': 'Adresse de la page', 'de': 'Adresse der Seite', 'pt': 'Endereço da página', 'it': 'Indirizzo della pagina', 'ja': 'ページのアドレス', 'zh': '页面地址', 'hi': 'पेज का पता', 'ar': 'عنوان الصفحة'},
    # The far end (jim/farend.py): worded as the Held screen's box asks it.
    'emergency_email': {'en': "Emergency contact's email", 'es': 'Correo del contacto de emergencia', 'fr': "E-mail du contact d'urgence", 'de': 'E-Mail des Notfallkontakts', 'pt': 'E-mail do contacto de emergência', 'it': "Email del contatto di emergenza", 'ja': '緊急連絡先のメールアドレス', 'zh': '紧急联系人的邮箱', 'hi': 'आपातकालीन संपर्क का ईमेल', 'ar': 'البريد الإلكتروني لجهة اتصال الطوارئ'},
    'consent': {'en': 'Consent', 'es': 'Consentimiento', 'fr': 'Consentement', 'de': 'Einwilligung', 'pt': 'Consentimento', 'it': 'Consenso', 'ja': '同意', 'zh': '同意', 'hi': 'सहमति', 'ar': 'الموافقة'},
    'every_hours': {'en': 'Repeats every (hours)', 'es': 'Se repite cada (horas)', 'fr': 'Se répète toutes les (heures)', 'de': 'Wiederholt sich alle (Stunden)', 'pt': 'Repete-se a cada (horas)', 'it': 'Si ripete ogni (ore)', 'ja': '繰り返し間隔（時間）', 'zh': '重复间隔（小时）', 'hi': 'हर (घंटे) में दोहराए', 'ar': 'يتكرر كل (ساعات)'},
    # The work two guardians took on. Worded as the box asks it: this is what
    # keeps the link open after the call, so the label says so.
    'task': {'en': 'What has to be finished', 'es': 'Qué hay que terminar', 'fr': "Ce qu'il reste à faire", 'de': 'Was noch zu erledigen ist', 'pt': 'O que tem de ser terminado', 'it': 'Cosa resta da finire', 'ja': '終わらせるべきこと', 'zh': '需要完成的事', 'hi': 'क्या पूरा करना है', 'ar': 'ما يجب إنجازه'},
    # Switching on something that senses a room. `others_told` is the claim
    # somebody makes, so the label is the claim rather than the column name;
    # `keeping` is the second decision, separate from sensing at all.
    'others_told': {'en': 'The people in that space have been told', 'es': 'Se ha informado a las personas de ese espacio', 'fr': "Les personnes présentes ont été prévenues", 'de': 'Die Menschen in diesem Raum wurden informiert', 'pt': 'As pessoas nesse espaço foram avisadas', 'it': 'Le persone in quello spazio sono state avvisate', 'ja': 'その場にいる人には伝えてあります', 'zh': '该空间中的人已被告知', 'hi': 'उस जगह के लोगों को बता दिया गया है', 'ar': 'أُبلغ من في ذلك المكان'},
    'keeping': {'en': 'Keep what it senses', 'es': 'Guardar lo que detecta', 'fr': "Conserver ce qu'il capte", 'de': 'Behalten, was es erfasst', 'pt': 'Guardar o que deteta', 'it': 'Conservare ciò che rileva', 'ja': '感知した内容を保持する', 'zh': '保留它感知到的内容', 'hi': 'जो यह महसूस करे उसे रखें', 'ar': 'الاحتفاظ بما يستشعره'},
    # Beginning a meeting or working stretch (jim/daybook.py). `monitor` is
    # which of the roster's rows the stretch runs on, and `stretch_id` is the
    # meeting a moment fell inside — named as the form asks them rather than
    # as the column stores them.
    'monitor': {'en': 'Which one is sensing', 'es': 'Cuál está detectando', 'fr': "Lequel capte", 'de': 'Welches erfasst gerade', 'pt': 'Qual está a detetar', 'it': 'Quale sta rilevando', 'ja': 'どれが感知しているか', 'zh': '哪一项在感知', 'hi': 'कौन-सा महसूस कर रहा है', 'ar': 'أيّها يستشعر'},
    # The staleness contract's two stamps (jim/freshness.py), worded as a
    # device would be asked for them rather than as the columns store them.
    'observed_at': {'en': 'When the device took the reading', 'es': 'Cuándo tomó el dispositivo la lectura', 'fr': "Quand l'appareil a pris la mesure", 'de': 'Wann das Gerät die Messung nahm', 'pt': 'Quando o dispositivo fez a leitura', 'it': 'Quando il dispositivo ha preso la lettura', 'ja': 'デバイスが測定した時刻', 'zh': '设备测量的时间', 'hi': 'डिवाइस ने रीडिंग कब ली', 'ar': 'متى أخذ الجهاز القراءة'},
    'device_now': {'en': "The device's clock, at sending", 'es': 'El reloj del dispositivo al enviar', 'fr': "L'horloge de l'appareil à l'envoi", 'de': 'Die Geräteuhr beim Senden', 'pt': 'O relógio do dispositivo ao enviar', 'it': "L'orologio del dispositivo all'invio", 'ja': '送信時のデバイスの時計', 'zh': '发送时设备的时钟', 'hi': 'भेजते समय डिवाइस की घड़ी', 'ar': 'ساعة الجهاز عند الإرسال'},
    'stretch_id': {'en': 'The meeting this belongs to', 'es': 'La reunión a la que pertenece', 'fr': "La réunion à laquelle ceci appartient", 'de': 'Die Besprechung, zu der dies gehört', 'pt': 'A reunião a que isto pertence', 'it': 'La riunione a cui appartiene', 'ja': 'これが属する会議', 'zh': '这属于哪场会议', 'hi': 'यह किस बैठक का हिस्सा है', 'ar': 'الاجتماع الذي ينتمي إليه هذا'},
    # The assisted-call form. `number` is not asked for so it can be kept —
    # it is read for which language the notice is spoken in and dropped — so
    # the label says what it is for rather than what it is.
    'number': {'en': "Their number, for the language", 'es': 'Su número, para el idioma', 'fr': "Leur numéro, pour la langue", 'de': 'Ihre Nummer, für die Sprache', 'pt': 'O número deles, para o idioma', 'it': 'Il loro numero, per la lingua', 'ja': '相手の番号（言語の判断用）', 'zh': '对方号码（用于判断语言）', 'hi': 'उनका नंबर, भाषा के लिए', 'ar': 'رقمهم، لتحديد اللغة'},
    'recording': {'en': 'Whether this call is being recorded', 'es': 'Si esta llamada se está grabando', 'fr': "Si cet appel est enregistré", 'de': 'Ob dieses Gespräch aufgezeichnet wird', 'pt': 'Se esta chamada está a ser gravada', 'it': 'Se questa chiamata viene registrata', 'ja': 'この通話を録音するかどうか', 'zh': '本次通话是否录音', 'hi': 'क्या यह कॉल रिकॉर्ड हो रही है', 'ar': 'ما إذا كانت هذه المكالمة تُسجَّل'},
    # The box on "beside you while you write". A refusal naming `draft` reads
    # as an error about a schema; this is what the box itself asks for.
    'draft': {'en': 'What you are writing', 'es': 'Lo que estás escribiendo', 'fr': "Ce que vous écrivez", 'de': 'Woran du schreibst', 'pt': 'O que está a escrever', 'it': 'Ciò che stai scrivendo', 'ja': '書いている内容', 'zh': '你正在写的内容', 'hi': 'आप क्या लिख रहे हैं', 'ar': 'ما تكتبه'},
    # The Studio's run form (jim/models.py WidgetRun). Worded exactly as
    # QRME words it: `test_the_shared_vocabulary_matches_the_sibling_products`
    # holds the three products to one sentence per field, and it is right
    # to — a field named the same in two products that reads differently in
    # each is two products disagreeing about what it is.
    'inputs': {'en': 'Inputs', 'es': 'Entradas', 'fr': 'Entrées', 'de': 'Eingaben', 'pt': 'Entradas', 'it': 'Ingressi', 'ja': '入力', 'zh': '输入', 'hi': 'इनपुट', 'ar': 'المدخلات'},
    # The sign-off form's one field (jim/engaged.py): what the offline
    # Guardian should keep an eye on while somebody is away.
    'topics': {'en': 'What to watch for while you are away', 'es': 'Qué vigilar mientras no estás', 'fr': 'Ce qu’il faut surveiller en votre absence', 'de': 'Worauf geachtet werden soll, während Sie weg sind', 'pt': 'O que vigiar enquanto está fora', 'it': 'Che cosa tenere d’occhio mentre non ci sei', 'ja': '留守のあいだ見守ってほしいこと', 'zh': '你不在时要留意什么', 'hi': 'आपकी अनुपस्थिति में किस पर नज़र रखनी है', 'ar': 'ما الذي يُتابَع في غيابك'},
    # The accessibility report's three questions, worded as the form asks
    # them — a refusal that names one of these should read like the form.
    'doing': {'en': 'What were you trying to do?', 'es': '¿Qué intentabas hacer?', 'fr': 'Qu’essayiez-vous de faire ?', 'de': 'Was hast du versucht zu tun?', 'pt': 'O que você estava tentando fazer?', 'it': 'Cosa stavi cercando di fare?', 'ja': '何をしようとしていましたか？', 'zh': '你当时想做什么？', 'hi': 'आप क्या करने की कोशिश कर रहे थे?', 'ar': 'ما الذي كنت تحاول فعله؟'},
    'wall': {'en': 'What stood in the way?', 'es': '¿Qué se interpuso?', 'fr': 'Qu’est-ce qui a fait obstacle ?', 'de': 'Was stand im Weg?', 'pt': 'O que ficou no caminho?', 'it': 'Cosa ti ha ostacolato?', 'ja': '何が妨げになりましたか？', 'zh': '是什么挡住了你？', 'hi': 'क्या आड़े आया?', 'ar': 'ما الذي وقف في الطريق؟'},
    'help': {'en': 'What would help?', 'es': '¿Qué ayudaría?', 'fr': 'Qu’est-ce qui aiderait ?', 'de': 'Was würde helfen?', 'pt': 'O que ajudaria?', 'it': 'Cosa aiuterebbe?', 'ja': '何があれば助かりますか？', 'zh': '什么会有帮助？', 'hi': 'क्या मदद करेगा?', 'ar': 'ما الذي قد يساعد؟'},
    'metric': {'en': 'Metric', 'es': 'Métrica', 'fr': 'Métrique', 'de': 'Messgröße', 'pt': 'Métrica', 'it': 'Metrica', 'ja': '指標', 'zh': '指标', 'hi': 'मीट्रिक', 'ar': 'المقياس'},
    'value': {'en': 'Value', 'es': 'Valor', 'fr': 'Valeur', 'de': 'Wert', 'pt': 'Valor', 'it': 'Valore', 'ja': '値', 'zh': '数值', 'hi': 'मान', 'ar': 'القيمة'},
    'lang': {'en': 'Language', 'es': 'Idioma', 'fr': 'Langue', 'de': 'Sprache', 'pt': 'Idioma', 'it': 'Lingua', 'ja': '言語', 'zh': '语言', 'hi': 'भाषा', 'ar': 'اللغة'},
    'stress_level': {'en': 'Stress level', 'es': 'Nivel de estrés', 'fr': "Niveau de stress", 'de': 'Stressniveau', 'pt': 'Nível de stress', 'it': 'Livello di stress', 'ja': 'ストレスの度合い', 'zh': '压力水平', 'hi': 'तनाव का स्तर', 'ar': 'مستوى التوتر'},
    'active': {'en': 'Use the trained model', 'es': 'Usar el modelo entrenado', 'fr': 'Utiliser le modèle entraîné', 'de': 'Trainiertes Modell verwenden', 'pt': 'Usar o modelo treinado', 'it': 'Usa il modello addestrato', 'ja': '学習済みモデルを使う', 'zh': '使用已训练的模型', 'hi': 'प्रशिक्षित मॉडल का उपयोग करें', 'ar': 'استخدام النموذج المدرَّب'},
    'granted': {'en': 'Let it change these', 'es': 'Dejarle cambiar esto', 'fr': 'Le laisser modifier ceci', 'de': 'Das ändern lassen', 'pt': 'Permitir que altere isto', 'it': 'Lasciagli cambiare questo', 'ja': 'これの変更を許す', 'zh': '允许它改动这些', 'hi': 'इसे ये बदलने दें', 'ar': 'السماح له بتغيير هذه'},
    'bearing': {'en': 'How it carries itself', 'es': 'Cómo se comporta', 'fr': 'Comment il se tient', 'de': 'Wie es sich gibt', 'pt': 'Como se porta', 'it': 'Come si pone', 'ja': 'どう構えるか', 'zh': '以什么姿态', 'hi': 'कैसा रुख़ रखे', 'ar': 'كيف يتصرّف'},
    'speaks_on': {'en': 'Where it speaks', 'es': 'Dónde habla', 'fr': 'Où il parle', 'de': 'Wo es spricht', 'pt': 'Onde fala', 'it': 'Dove parla', 'ja': 'どこで話すか', 'zh': '在哪儿说话', 'hi': 'कहाँ बोले', 'ar': 'أين يتحدّث'},
    'email_reminder': {'en': 'Email me a reminder', 'es': 'Enviarme un recordatorio por correo', 'fr': "M'envoyer un rappel par e-mail", 'de': 'Erinnerung per E-Mail', 'pt': 'Enviar-me um lembrete por e-mail', 'it': 'Promemoria via e-mail', 'ja': 'メールでリマインド', 'zh': '邮件提醒', 'hi': 'ईमेल अनुस्मारक', 'ar': 'تذكير بالبريد'},
    'when': {'en': 'When', 'es': 'Cuándo', 'fr': 'Quand', 'de': 'Wann', 'pt': 'Quando', 'it': 'Quando', 'ja': '日時', 'zh': '时间', 'hi': 'कब', 'ar': 'متى'},
    'where': {'en': 'Where', 'es': 'Dónde', 'fr': 'Où', 'de': 'Wo', 'pt': 'Onde', 'it': 'Dove', 'ja': '場所', 'zh': '地点', 'hi': 'कहाँ', 'ar': 'أين'},
    'offering_id': {'en': 'Offering', 'es': 'Artículo', 'fr': 'Article', 'de': 'Angebot', 'pt': 'Artigo', 'it': 'Articolo', 'ja': '商品', 'zh': '商品', 'hi': 'पेशकश', 'ar': 'المعروض'},
    'qrme_order_id': {'en': 'Order', 'es': 'Pedido', 'fr': 'Commande', 'de': 'Bestellung', 'pt': 'Pedido', 'it': 'Ordine', 'ja': '注文', 'zh': '订单', 'hi': 'ऑर्डर', 'ar': 'الطلب'},
    'quantity': {'en': 'Quantity', 'es': 'Cantidad', 'fr': 'Quantité', 'de': 'Menge', 'pt': 'Quantidade', 'it': 'Quantità', 'ja': '数量', 'zh': '数量', 'hi': 'मात्रा', 'ar': 'الكمية'},
    'shop_id': {'en': 'Shop', 'es': 'Tienda', 'fr': 'Boutique', 'de': 'Laden', 'pt': 'Loja', 'it': 'Negozio', 'ja': 'ショップ', 'zh': '商店', 'hi': 'दुकान', 'ar': 'المتجر'},
    'feature': {'en': 'Feature', 'es': 'Función', 'fr': 'Fonction', 'de': 'Funktion', 'pt': 'Função', 'it': 'Funzione', 'ja': '機能', 'zh': '功能', 'hi': 'सुविधा', 'ar': 'الميزة'},
    'other_id': {'en': 'Who', 'es': 'Quién', 'fr': 'Qui', 'de': 'Wer', 'pt': 'Quem', 'it': 'Chi', 'ja': '相手', 'zh': '对方', 'hi': 'कौन', 'ar': 'من'},
    'body': {'en': 'Message', 'es': 'Mensaje', 'fr': 'Message', 'de': 'Nachricht', 'pt': 'Mensagem', 'it': 'Messaggio', 'ja': 'メッセージ', 'zh': '消息', 'hi': 'संदेश', 'ar': 'الرسالة'},
    'headline': {'en': 'Headline', 'es': 'Titular', 'fr': 'Accroche', 'de': 'Überschrift', 'pt': 'Título', 'it': 'Titolo', 'ja': '見出し', 'zh': '标题', 'hi': 'शीर्षक', 'ar': 'العنوان'},
    'about': {'en': 'About', 'es': 'Acerca de', 'fr': 'À propos', 'de': 'Über', 'pt': 'Sobre', 'it': 'Info', 'ja': '自己紹介', 'zh': '关于', 'hi': 'परिचय', 'ar': 'نبذة'},
    'theme': {'en': 'Theme', 'es': 'Tema', 'fr': 'Thème', 'de': 'Design', 'pt': 'Tema', 'it': 'Tema', 'ja': 'テーマ', 'zh': '主题', 'hi': 'थीम', 'ar': 'السمة'},
    'links': {'en': 'Links', 'es': 'Enlaces', 'fr': 'Liens', 'de': 'Links', 'pt': 'Ligações', 'it': 'Collegamenti', 'ja': 'リンク', 'zh': '链接', 'hi': 'लिंक', 'ar': 'الروابط'},
    'top_friends': {'en': 'Top friends', 'es': 'Mejores amigos', 'fr': 'Meilleurs amis', 'de': 'Beste Freunde', 'pt': 'Melhores amigos', 'it': 'Migliori amici', 'ja': 'トップフレンド', 'zh': '挚友', 'hi': 'खास दोस्त', 'ar': 'أفضل الأصدقاء'},
    'account_id': {'en': 'Account', 'es': 'Cuenta', 'fr': 'Compte', 'de': 'Konto', 'pt': 'Conta', 'it': 'Conto', 'ja': '口座', 'zh': '账户', 'hi': 'खाता', 'ar': 'الحساب'},
    'account_number': {'en': 'Account number', 'es': 'Número de cuenta', 'fr': 'Numéro de compte', 'de': 'Kontonummer', 'pt': 'Número de conta', 'it': 'Numero di conto', 'ja': '口座番号', 'zh': '账号', 'hi': 'खाता संख्या', 'ar': 'رقم الحساب'},
    'api_key': {'en': 'API key', 'es': 'Clave API', 'fr': 'Clé API', 'de': 'API-Schlüssel', 'pt': 'Chave API', 'it': 'Chiave API', 'ja': 'APIキー', 'zh': 'API 密钥', 'hi': 'API कुंजी', 'ar': 'مفتاح API'},
    'asset_classes': {'en': 'Asset classes', 'es': 'Clases de activos', 'fr': "Classes d'actifs", 'de': 'Anlageklassen', 'pt': 'Classes de ativos', 'it': 'Classi di attivi', 'ja': '資産クラス', 'zh': '资产类别', 'hi': 'परिसंपत्ति वर्ग', 'ar': 'فئات الأصول'},
    'balance': {'en': 'Balance', 'es': 'Saldo', 'fr': 'Solde', 'de': 'Saldo', 'pt': 'Saldo', 'it': 'Saldo', 'ja': '残高', 'zh': '余额', 'hi': 'शेष राशि', 'ar': 'الرصيد'},
    'cap_per_order': {'en': 'Cap per order', 'es': 'Límite por orden', 'fr': 'Plafond par ordre', 'de': 'Limit pro Auftrag', 'pt': 'Limite por ordem', 'it': 'Tetto per ordine', 'ja': '注文ごとの上限', 'zh': '单笔上限', 'hi': 'प्रति आदेश सीमा', 'ar': 'الحد لكل أمر'},
    'enabled': {'en': 'Enabled', 'es': 'Activado', 'fr': 'Activé', 'de': 'Aktiviert', 'pt': 'Ativado', 'it': 'Attivo', 'ja': '有効', 'zh': '启用', 'hi': 'सक्रिय', 'ar': 'مفعّل'},
    'institution': {'en': 'Institution', 'es': 'Institución', 'fr': 'Établissement', 'de': 'Institut', 'pt': 'Instituição', 'it': 'Istituto', 'ja': '金融機関', 'zh': '机构', 'hi': 'संस्था', 'ar': 'المؤسسة'},
    'aggregator': {'en': 'Aggregator', 'es': 'Agregador', 'fr': 'Agrégateur', 'de': 'Aggregator', 'pt': 'Agregador', 'it': 'Aggregatore', 'ja': 'アグリゲーター', 'zh': '聚合服务', 'hi': 'एग्रीगेटर', 'ar': 'المجمّع'},
    'filename': {'en': 'File name', 'es': 'Nombre del archivo', 'fr': 'Nom du fichier', 'de': 'Dateiname', 'pt': 'Nome do ficheiro', 'it': 'Nome del file', 'ja': 'ファイル名', 'zh': '文件名', 'hi': 'फ़ाइल का नाम', 'ar': 'اسم الملف'},
    'answer': {'en': 'Your answer', 'es': 'Tu respuesta', 'fr': 'Votre réponse', 'de': 'Ihre Antwort', 'pt': 'A sua resposta', 'it': 'La tua risposta', 'ja': 'あなたの答え', 'zh': '你的回答', 'hi': 'आपका उत्तर', 'ar': 'إجابتك'},
    'kind': {'en': 'Kind', 'es': 'Tipo', 'fr': 'Type', 'de': 'Art', 'pt': 'Tipo', 'it': 'Tipo', 'ja': '種類', 'zh': '类型', 'hi': 'प्रकार', 'ar': 'النوع'},
    'label': {'en': 'Label', 'es': 'Etiqueta', 'fr': 'Libellé', 'de': 'Bezeichnung', 'pt': 'Etiqueta', 'it': 'Etichetta', 'ja': 'ラベル', 'zh': '标签', 'hi': 'लेबल', 'ar': 'التسمية'},
    'monthly_cap': {'en': 'Monthly cap', 'es': 'Límite mensual', 'fr': 'Plafond mensuel', 'de': 'Monatslimit', 'pt': 'Limite mensal', 'it': 'Tetto mensile', 'ja': '月間上限', 'zh': '每月上限', 'hi': 'मासिक सीमा', 'ar': 'الحد الشهري'},
    'routing_number': {'en': 'Routing number', 'es': 'Número de ruta', 'fr': "Numéro d'acheminement", 'de': 'Routingnummer', 'pt': 'Número de encaminhamento', 'it': 'Numero di instradamento', 'ja': 'ルーティング番号', 'zh': '路由号', 'hi': 'राउटिंग नंबर', 'ar': 'رقم التوجيه'},
    'scope': {'en': 'Scope', 'es': 'Alcance', 'fr': 'Périmètre', 'de': 'Umfang', 'pt': 'Âmbito', 'it': 'Ambito', 'ja': '範囲', 'zh': '范围', 'hi': 'दायरा', 'ar': 'النطاق'},
    'guardian_email': {'en': 'Parent or guardian email', 'es': 'Correo del padre, madre o tutor', 'fr': 'Courriel du parent ou tuteur', 'de': 'E-Mail der Eltern oder Erziehungsberechtigten', 'pt': 'Email do pai, mãe ou responsável', 'it': 'Email del genitore o tutore', 'ja': '保護者のメールアドレス', 'zh': '父母或监护人邮箱', 'hi': 'माता-पिता या अभिभावक का ईमेल', 'ar': 'البريد الإلكتروني للوالد أو الوصي'},
    'birthdate': {'en': 'Date of birth', 'es': 'Fecha de nacimiento', 'fr': 'Date de naissance', 'de': 'Geburtsdatum', 'pt': 'Data de nascimento', 'it': 'Data di nascita', 'ja': '生年月日', 'zh': '出生日期', 'hi': 'जन्म तिथि', 'ar': 'تاريخ الميلاد'},
    'content': {'en': 'Content', 'es': 'Contenido', 'fr': 'Contenu', 'de': 'Inhalt', 'pt': 'Conteúdo', 'it': 'Contenuto', 'ja': '内容', 'zh': '内容', 'hi': 'सामग्री', 'ar': 'المحتوى'},
    'display_name': {'en': 'Profile name', 'es': 'Nombre del perfil', 'fr': 'Nom du profil', 'de': 'Profilname', 'pt': 'Nome do perfil', 'it': 'Nome del profilo', 'ja': 'プロフィール名', 'zh': '资料名称', 'hi': 'प्रोफ़ाइल नाम', 'ar': 'اسم الملف'},
    'dose': {'en': 'Dose', 'es': 'Dosis', 'fr': 'Dose', 'de': 'Dosis', 'pt': 'Dose', 'it': 'Dose', 'ja': '用量', 'zh': '剂量', 'hi': 'खुराक', 'ar': 'الجرعة'},
    'email': {'en': 'Email', 'es': 'Correo electrónico', 'fr': 'E-mail', 'de': 'E-Mail', 'pt': 'E-mail', 'it': 'E-mail', 'ja': 'メールアドレス', 'zh': '电子邮箱', 'hi': 'ईमेल', 'ar': 'البريد الإلكتروني'},
    'energy': {'en': 'Energy', 'es': 'Energía', 'fr': 'Énergie', 'de': 'Energie', 'pt': 'Energia', 'it': 'Energia', 'ja': '体力', 'zh': '精力', 'hi': 'ऊर्जा', 'ar': 'الطاقة'},
    'goal': {'en': 'Goal', 'es': 'Objetivo', 'fr': 'Objectif', 'de': 'Ziel', 'pt': 'Objetivo', 'it': 'Obiettivo', 'ja': '目標', 'zh': '目标', 'hi': 'लक्ष्य', 'ar': 'الهدف'},
    'handle': {'en': 'Handle', 'es': 'Identificador', 'fr': 'Identifiant', 'de': 'Kürzel', 'pt': 'Identificador', 'it': 'Handle', 'ja': 'ハンドル名', 'zh': '账号名', 'hi': 'हैंडल', 'ar': 'المعرّف'},
    # Sent by the voice screens when somebody speaks or types over the
    # Guardian mid-answer. Nobody types it, which is why it needs wording
    # rather than why it does not: a refusal that names `cut_off_heard` is an
    # error about this API's own vocabulary, shown to a person who was having
    # a conversation.
    'cut_off_heard': {'en': 'How much of the answer you heard', 'es': 'Cuánto alcanzaste a oír de la respuesta', 'fr': "Ce que vous avez entendu de la réponse", 'de': 'Wie viel der Antwort du gehört hast', 'pt': 'Quanto ouviu da resposta', 'it': "Quanto hai sentito della risposta", 'ja': '答えをどこまで聞いたか', 'zh': '这句回答你听到了多少', 'hi': 'उत्तर आपने कितना सुना', 'ar': 'ما سمعته من الإجابة'},
    'message': {'en': 'Message', 'es': 'Mensaje', 'fr': 'Message', 'de': 'Nachricht', 'pt': 'Mensagem', 'it': 'Messaggio', 'ja': 'メッセージ', 'zh': '消息', 'hi': 'संदेश', 'ar': 'الرسالة'},
    'mood': {'en': 'Mood', 'es': 'Ánimo', 'fr': 'Humeur', 'de': 'Stimmung', 'pt': 'Humor', 'it': 'Umore', 'ja': '気分', 'zh': '心情', 'hi': 'मनोदशा', 'ar': 'المزاج'},
    'name': {'en': 'Name', 'es': 'Nombre', 'fr': 'Nom', 'de': 'Name', 'pt': 'Nome', 'it': 'Nome', 'ja': '名前', 'zh': '名称', 'hi': 'नाम', 'ar': 'الاسم'},
    'note': {'en': 'Note', 'es': 'Nota', 'fr': 'Note', 'de': 'Notiz', 'pt': 'Nota', 'it': 'Nota', 'ja': 'メモ', 'zh': '备注', 'hi': 'टिप्पणी', 'ar': 'ملاحظة'},
    'password': {'en': 'Password', 'es': 'Contraseña', 'fr': 'Mot de passe', 'de': 'Passwort', 'pt': 'Palavra-passe', 'it': 'Password', 'ja': 'パスワード', 'zh': '密码', 'hi': 'पासवर्ड', 'ar': 'كلمة المرور'},
    'plan': {'en': 'Plan', 'es': 'Plan', 'fr': 'Formule', 'de': 'Tarif', 'pt': 'Plano', 'it': 'Piano', 'ja': 'プラン', 'zh': '方案', 'hi': 'योजना', 'ar': 'الخطة'},
    'profile_id': {'en': 'Profile id', 'es': 'Id del perfil', 'fr': 'Identifiant du profil', 'de': 'Profil-ID', 'pt': 'Id do perfil', 'it': 'Id del profilo', 'ja': 'プロフィールID', 'zh': '资料 id', 'hi': 'प्रोफ़ाइल आईडी', 'ar': 'معرّف الملف'},
    'purpose': {'en': 'Purpose', 'es': 'Propósito', 'fr': 'Objectif', 'de': 'Zweck', 'pt': 'Finalidade', 'it': 'Scopo', 'ja': '目的', 'zh': '用途', 'hi': 'उद्देश्य', 'ar': 'الغرض'},
    'reason': {'en': 'Reason', 'es': 'Motivo', 'fr': 'Motif', 'de': 'Grund', 'pt': 'Motivo', 'it': 'Motivo', 'ja': '理由', 'zh': '原因', 'hi': 'कारण', 'ar': 'السبب'},
    'signal_quality': {'en': 'Signal quality', 'es': 'Calidad de la señal', 'fr': 'Qualité du signal', 'de': 'Signalqualität', 'pt': 'Qualidade do sinal', 'it': 'Qualità del segnale', 'ja': '信号品質', 'zh': '信号质量', 'hi': 'सिग्नल गुणवत्ता', 'ar': 'جودة الإشارة'},
    'title': {'en': 'Title', 'es': 'Título', 'fr': 'Titre', 'de': 'Titel', 'pt': 'Título', 'it': 'Titolo', 'ja': 'タイトル', 'zh': '标题', 'hi': 'शीर्षक', 'ar': 'العنوان'},
    'topic': {'en': 'Topic', 'es': 'Tema', 'fr': 'Sujet', 'de': 'Thema', 'pt': 'Tema', 'it': 'Argomento', 'ja': 'トピック', 'zh': '主题', 'hi': 'विषय', 'ar': 'الموضوع'},
    'activity': {'en': 'Activity', 'es': 'Actividad', 'fr': 'Activité', 'de': 'Aktivität', 'pt': 'Atividade', 'it': 'Attività', 'ja': 'アクティビティ', 'zh': '活动', 'hi': 'गतिविधि', 'ar': 'النشاط'},
    'anonymous': {'en': 'Anonymous', 'es': 'Anónimo', 'fr': 'Anonyme', 'de': 'Anonym', 'pt': 'Anónimo', 'it': 'Anonimo', 'ja': '匿名', 'zh': '匿名', 'hi': 'गुमनाम', 'ar': 'مجهول'},
    'area': {'en': 'Area', 'es': 'Área', 'fr': 'Domaine', 'de': 'Bereich', 'pt': 'Área', 'it': 'Area', 'ja': '分野', 'zh': '领域', 'hi': 'क्षेत्र', 'ar': 'المجال'},
    'attempts': {'en': 'Attempts', 'es': 'Intentos', 'fr': 'Tentatives', 'de': 'Versuche', 'pt': 'Tentativas', 'it': 'Tentativi', 'ja': '試行回数', 'zh': '尝试次数', 'hi': 'प्रयास', 'ar': 'المحاولات'},
    'category': {'en': 'Category', 'es': 'Categoría', 'fr': 'Catégorie', 'de': 'Kategorie', 'pt': 'Categoria', 'it': 'Categoria', 'ja': 'カテゴリー', 'zh': '类别', 'hi': 'श्रेणी', 'ar': 'الفئة'},
    'code': {'en': 'Code', 'es': 'Código', 'fr': 'Code', 'de': 'Code', 'pt': 'Código', 'it': 'Codice', 'ja': 'コード', 'zh': '验证码', 'hi': 'कोड', 'ar': 'الرمز'},
    'command': {'en': 'Command', 'es': 'Comando', 'fr': 'Commande', 'de': 'Befehl', 'pt': 'Comando', 'it': 'Comando', 'ja': 'コマンド', 'zh': '指令', 'hi': 'कमांड', 'ar': 'الأمر'},
    'condition': {'en': 'Condition', 'es': 'Afección', 'fr': 'Affection', 'de': 'Erkrankung', 'pt': 'Condição', 'it': 'Condizione', 'ja': '症状', 'zh': '状况', 'hi': 'स्थिति', 'ar': 'الحالة'},
    'entries': {'en': "The address book, as the device holds it", 'es': 'La libreta, tal como la tiene el dispositivo', 'fr': "Le carnet, tel que l'appareil le détient", 'de': 'Das Adressbuch, wie das Gerät es hält', 'pt': 'A lista, tal como o dispositivo a tem', 'it': 'La rubrica, come la tiene il dispositivo', 'ja': '端末が持つままの連絡帳', 'zh': '设备中原样的通讯录', 'hi': 'सूची, जैसी डिवाइस में है', 'ar': 'الدفتر كما يحمله الجهاز'},
    'jim_user_id': {'en': "Their guardian's account, when the shell matched one", 'es': 'La cuenta de su guardián, cuando la app la reconoció', 'fr': "Le compte de leur gardien, quand l'application l'a reconnu", 'de': 'Das Konto ihres Wächters, wenn eine App es erkannt hat', 'pt': 'A conta do guardião deles, quando a app a reconheceu', 'it': "L'account del loro guardiano, quando un'app l'ha riconosciuto", 'ja': '相手のガーディアンのアカウント（アプリが照合できた場合）', 'zh': '对方守护者的账户（应用匹配到时）', 'hi': 'उनके गार्जियन का खाता, जब ऐप ने मिलाया हो', 'ar': 'حساب وصيّهم، عندما يطابقه تطبيق'},
    'consented': {'en': 'Consent', 'es': 'Consentimiento', 'fr': 'Consentement', 'de': 'Einwilligung', 'pt': 'Consentimento', 'it': 'Consenso', 'ja': '同意', 'zh': '同意', 'hi': 'सहमति', 'ar': 'الموافقة'},
    'contact_emergency_services': {'en': 'Contact emergency services', 'es': 'Contactar a emergencias', 'fr': 'Contacter les secours', 'de': 'Notdienste rufen', 'pt': 'Contactar os serviços de emergência', 'it': 'Contattare i soccorsi', 'ja': '救急機関へ連絡', 'zh': '联系急救服务', 'hi': 'आपातकालीन सेवाओं से संपर्क करें', 'ar': 'الاتصال بخدمات الطوارئ'},
    'critical': {'en': 'Critical', 'es': 'Crítico', 'fr': 'Critique', 'de': 'Kritisch', 'pt': 'Crítico', 'it': 'Critico', 'ja': '重要', 'zh': '关键', 'hi': 'अति आवश्यक', 'ar': 'حرج'},
    'days': {'en': 'Days', 'es': 'Días', 'fr': 'Jours', 'de': 'Tage', 'pt': 'Dias', 'it': 'Giorni', 'ja': '日数', 'zh': '天数', 'hi': 'दिन', 'ar': 'الأيام'},
    'department_id': {'en': 'Department id', 'es': 'Id del departamento', 'fr': 'Id du service', 'de': 'Abteilungs-ID', 'pt': 'Id do departamento', 'it': 'Id del reparto', 'ja': '部門ID', 'zh': '部门 id', 'hi': 'विभाग आईडी', 'ar': 'معرّف القسم'},
    'device_name': {'en': 'Device name', 'es': 'Nombre del dispositivo', 'fr': 'Nom de l’appareil', 'de': 'Gerätename', 'pt': 'Nome do dispositivo', 'it': 'Nome del dispositivo', 'ja': 'デバイス名', 'zh': '设备名称', 'hi': 'डिवाइस का नाम', 'ar': 'اسم الجهاز'},
    'direction': {'en': 'Direction', 'es': 'Sentido', 'fr': 'Sens', 'de': 'Richtung', 'pt': 'Direção', 'it': 'Direzione', 'ja': '方向', 'zh': '方向', 'hi': 'दिशा', 'ar': 'الاتجاه'},
    'focus': {'en': 'Focus', 'es': 'Enfoque', 'fr': 'Axe', 'de': 'Schwerpunkt', 'pt': 'Foco', 'it': 'Focus', 'ja': 'フォーカス', 'zh': '重点', 'hi': 'फोकस', 'ar': 'التركيز'},
    'heart_rate': {'en': 'Heart rate', 'es': 'Frecuencia cardíaca', 'fr': 'Fréquence cardiaque', 'de': 'Herzfrequenz', 'pt': 'Frequência cardíaca', 'it': 'Frequenza cardiaca', 'ja': '心拍数', 'zh': '心率', 'hi': 'हृदय गति', 'ar': 'معدل نبض القلب'},
    'paired': {'en': 'Paired', 'es': 'Emparejado', 'fr': 'Appairé', 'de': 'Gekoppelt', 'pt': 'Emparelhado', 'it': 'Associato', 'ja': 'ペアリング済み', 'zh': '已配对', 'hi': 'युग्मित', 'ar': 'مقترن'},
    'host': {'en': 'Host', 'es': 'Servidor', 'fr': 'Hôte', 'de': 'Host', 'pt': 'Servidor', 'it': 'Host', 'ja': 'ホスト', 'zh': '主机', 'hi': 'होस्ट', 'ar': 'المضيف'},
    'language': {'en': 'Language', 'es': 'Idioma', 'fr': 'Langue', 'de': 'Sprache', 'pt': 'Idioma', 'it': 'Lingua', 'ja': '言語', 'zh': '语言', 'hi': 'भाषा', 'ar': 'اللغة'},
    'legal_name': {'en': 'Legal name', 'es': 'Nombre legal', 'fr': 'Nom légal', 'de': 'Amtlicher Name', 'pt': 'Nome legal', 'it': 'Nome legale', 'ja': '法的氏名', 'zh': '法定姓名', 'hi': 'कानूनी नाम', 'ar': 'الاسم القانوني'},
    'level': {'en': 'Level', 'es': 'Nivel', 'fr': 'Niveau', 'de': 'Stufe', 'pt': 'Nível', 'it': 'Livello', 'ja': 'レベル', 'zh': '级别', 'hi': 'स्तर', 'ar': 'المستوى'},
    'locality': {'en': 'Locality', 'es': 'Localidad', 'fr': 'Localité', 'de': 'Ort', 'pt': 'Localidade', 'it': 'Località', 'ja': '地域', 'zh': '地区', 'hi': 'इलाक़ा', 'ar': 'المنطقة'},
    'mic_type': {'en': 'Microphone type', 'es': 'Tipo de micrófono', 'fr': 'Type de micro', 'de': 'Mikrofontyp', 'pt': 'Tipo de microfone', 'it': 'Tipo di microfono', 'ja': 'マイクの種類', 'zh': '麦克风类型', 'hi': 'माइक का प्रकार', 'ar': 'نوع الميكروفون'},
    'minutes': {'en': 'Minutes', 'es': 'Minutos', 'fr': 'Minutes', 'de': 'Minuten', 'pt': 'Minutos', 'it': 'Minuti', 'ja': '分', 'zh': '分钟', 'hi': 'मिनट', 'ar': 'الدقائق'},
    'model': {'en': 'Model', 'es': 'Modelo', 'fr': 'Modèle', 'de': 'Modell', 'pt': 'Modelo', 'it': 'Modello', 'ja': 'モデル', 'zh': '模型', 'hi': 'मॉडल', 'ar': 'النموذج'},
    'new_password': {'en': 'New password', 'es': 'Nueva contraseña', 'fr': 'Nouveau mot de passe', 'de': 'Neues Passwort', 'pt': 'Nova palavra-passe', 'it': 'Nuova password', 'ja': '新しいパスワード', 'zh': '新密码', 'hi': 'नया पासवर्ड', 'ar': 'كلمة المرور الجديدة'},
    'org_id': {'en': 'Organization id', 'es': 'Id de la organización', 'fr': 'Id de l’organisation', 'de': 'Organisations-ID', 'pt': 'Id da organização', 'it': 'Id dell’organizzazione', 'ja': '組織ID', 'zh': '组织 id', 'hi': 'संगठन आईडी', 'ar': 'معرّف المنظمة'},
    'owner_token': {'en': 'Owner token', 'es': 'Token del propietario', 'fr': 'Jeton du propriétaire', 'de': 'Inhaber-Token', 'pt': 'Token do proprietário', 'it': 'Token del proprietario', 'ja': 'オーナートークン', 'zh': '所有者令牌', 'hi': 'स्वामी टोकन', 'ar': 'رمز المالك'},
    'placement': {'en': 'Placement', 'es': 'Colocación', 'fr': 'Emplacement', 'de': 'Platzierung', 'pt': 'Colocação', 'it': 'Posizionamento', 'ja': '設置場所', 'zh': '放置位置', 'hi': 'स्थान निर्धारण', 'ar': 'الموضع'},
    'platform': {'en': 'Platform', 'es': 'Plataforma', 'fr': 'Plateforme', 'de': 'Plattform', 'pt': 'Plataforma', 'it': 'Piattaforma', 'ja': 'プラットフォーム', 'zh': '平台', 'hi': 'प्लेटफ़ॉर्म', 'ar': 'المنصة'},
    'port': {'en': 'Port', 'es': 'Puerto', 'fr': 'Port', 'de': 'Port', 'pt': 'Porta', 'it': 'Porta', 'ja': 'ポート', 'zh': '端口', 'hi': 'पोर्ट', 'ar': 'المنفذ'},
    'preferences': {'en': 'Preferences', 'es': 'Preferencias', 'fr': 'Préférences', 'de': 'Vorlieben', 'pt': 'Preferências', 'it': 'Preferenze', 'ja': '好み', 'zh': '偏好', 'hi': 'पसंद', 'ar': 'التفضيلات'},
    'public_url': {'en': 'Public URL', 'es': 'URL pública', 'fr': 'URL publique', 'de': 'Öffentliche URL', 'pt': 'URL pública', 'it': 'URL pubblico', 'ja': '公開URL', 'zh': '公开 URL', 'hi': 'सार्वजनिक URL', 'ar': 'عنوان URL العام'},
    'question': {'en': 'Question', 'es': 'Pregunta', 'fr': 'Question', 'de': 'Frage', 'pt': 'Pergunta', 'it': 'Domanda', 'ja': '質問', 'zh': '问题', 'hi': 'प्रश्न', 'ar': 'السؤال'},
    'quiet_days': {'en': 'Quiet days', 'es': 'Días de silencio', 'fr': 'Jours calmes', 'de': 'Ruhetage', 'pt': 'Dias de silêncio', 'it': 'Giorni di silenzio', 'ja': '静かな日', 'zh': '免打扰日', 'hi': 'शांत दिन', 'ar': 'أيام الهدوء'},
    'relationship': {'en': 'Relationship', 'es': 'Relación', 'fr': 'Relation', 'de': 'Beziehung', 'pt': 'Relação', 'it': 'Relazione', 'ja': '関係', 'zh': '关系', 'hi': 'रिश्ता', 'ar': 'العلاقة'},
    'responder': {'en': 'Responder', 'es': 'Quien responde', 'fr': 'Répondant', 'de': 'Ersthelfer', 'pt': 'Quem responde', 'it': 'Chi risponde', 'ja': '対応者', 'zh': '响应者', 'hi': 'प्रतिक्रिया देने वाला', 'ar': 'المستجيب'},
    'sender': {'en': 'Sender', 'es': 'Remitente', 'fr': 'Expéditeur', 'de': 'Absender', 'pt': 'Remetente', 'it': 'Mittente', 'ja': '送信者', 'zh': '发件人', 'hi': 'प्रेषक', 'ar': 'المرسِل'},
    'signature': {'en': 'Signature', 'es': 'Firma', 'fr': 'Signature', 'de': 'Unterschrift', 'pt': 'Assinatura', 'it': 'Firma', 'ja': '署名', 'zh': '签名', 'hi': 'हस्ताक्षर', 'ar': 'التوقيع'},
    'site': {'en': 'Site', 'es': 'Sitio', 'fr': 'Site', 'de': 'Standort', 'pt': 'Local', 'it': 'Sito', 'ja': 'サイト', 'zh': '站点', 'hi': 'साइट', 'ar': 'الموقع'},
    'situation': {'en': 'Situation', 'es': 'Situación', 'fr': 'Situation', 'de': 'Situation', 'pt': 'Situação', 'it': 'Situazione', 'ja': '状況', 'zh': '情况', 'hi': 'स्थिति', 'ar': 'الوضع'},
    'source': {'en': 'Source', 'es': 'Fuente', 'fr': 'Source', 'de': 'Quelle', 'pt': 'Fonte', 'it': 'Fonte', 'ja': 'ソース', 'zh': '来源', 'hi': 'स्रोत', 'ar': 'المصدر'},
    'steward_channel': {'en': 'Steward channel', 'es': 'Canal del custodio', 'fr': 'Canal du référent', 'de': 'Kanal der Vertrauensperson', 'pt': 'Canal do responsável', 'it': 'Canale del referente', 'ja': '世話役の連絡先', 'zh': '守护人渠道', 'hi': 'संरक्षक चैनल', 'ar': 'قناة الوصي'},
    'steward_name': {'en': 'Steward name', 'es': 'Nombre del custodio', 'fr': 'Nom du référent', 'de': 'Name der Vertrauensperson', 'pt': 'Nome do responsável', 'it': 'Nome del referente', 'ja': '世話役の名前', 'zh': '守护人姓名', 'hi': 'संरक्षक का नाम', 'ar': 'اسم الوصي'},
    'stress': {'en': 'Stress', 'es': 'Estrés', 'fr': 'Stress', 'de': 'Stress', 'pt': 'Stress', 'it': 'Stress', 'ja': 'ストレス', 'zh': '压力', 'hi': 'तनाव', 'ar': 'التوتر'},
    'target': {'en': 'Target', 'es': 'Objetivo', 'fr': 'Cible', 'de': 'Ziel', 'pt': 'Alvo', 'it': 'Obiettivo', 'ja': 'ターゲット', 'zh': '目标', 'hi': 'लक्ष्य', 'ar': 'الهدف'},
    'terms_consent': {'en': 'Terms consent', 'es': 'Aceptación de los términos', 'fr': 'Acceptation des conditions', 'de': 'Zustimmung zu den Bedingungen', 'pt': 'Aceitação dos termos', 'it': 'Accettazione dei termini', 'ja': '利用規約への同意', 'zh': '条款同意', 'hi': 'शर्तों की सहमति', 'ar': 'الموافقة على الشروط'},
    'text': {'en': 'Text', 'es': 'Texto', 'fr': 'Texte', 'de': 'Text', 'pt': 'Texto', 'it': 'Testo', 'ja': 'テキスト', 'zh': '文本', 'hi': 'पाठ', 'ar': 'النص'},
    'to': {'en': 'To', 'es': 'Para', 'fr': 'À', 'de': 'An', 'pt': 'Para', 'it': 'A', 'ja': '宛先', 'zh': '发给', 'hi': 'किसे', 'ar': 'إلى'},
    'from_addr': {'en': 'From', 'es': 'De', 'fr': 'De', 'de': 'Von', 'pt': 'De', 'it': 'Da', 'ja': '差出人', 'zh': '发件人', 'hi': 'भेजने वाला', 'ar': 'من'},
    # Word-for-word QRME's `region` — one wording across the products.
    'region': {'en': 'Region', 'es': 'Región', 'fr': 'Région', 'de': 'Region', 'pt': 'Região', 'it': 'Regione', 'ja': '地方', 'zh': '区域', 'hi': 'क्षेत्र', 'ar': 'الإقليم'},
    'description': {'en': 'What changes', 'es': 'Qué cambia', 'fr': 'Ce qui change', 'de': 'Was sich ändert', 'pt': 'O que muda', 'it': 'Cosa cambia', 'ja': '変更内容', 'zh': '改动内容', 'hi': 'क्या बदलता है', 'ar': 'ما الذي يتغير'},
    'patch': {'en': 'The change', 'es': 'El cambio', 'fr': 'La modification', 'de': 'Die Änderung', 'pt': 'A alteração', 'it': 'La modifica', 'ja': '変更', 'zh': '改动', 'hi': 'बदलाव', 'ar': 'التغيير'},
    'instruction': {'en': 'What should change', 'es': 'Qué debería cambiar', 'fr': 'Ce qui devrait changer', 'de': 'Was sich ändern soll', 'pt': 'O que deve mudar', 'it': 'Cosa dovrebbe cambiare', 'ja': '変えてほしいこと', 'zh': '应该改什么', 'hi': 'क्या बदलना चाहिए', 'ar': 'ما الذي ينبغي تغييره'},
    'subject': {'en': 'Subject', 'es': 'Asunto', 'fr': 'Sujet', 'de': 'Betreff', 'pt': 'Assunto', 'it': 'Oggetto', 'ja': '件名', 'zh': '主题', 'hi': 'विषय', 'ar': 'الموضوع'},
    'role': {'en': 'Role', 'es': 'Rol', 'fr': 'Rôle', 'de': 'Rolle', 'pt': 'Função', 'it': 'Ruolo', 'ja': '役割', 'zh': '角色', 'hi': 'भूमिका', 'ar': 'الدور'},
    'objective': {'en': 'What it should accomplish', 'es': 'Qué debe lograr', 'fr': "Ce qu'il doit accomplir", 'de': 'Was es erreichen soll', 'pt': 'O que deve alcançar', 'it': 'Cosa deve ottenere', 'ja': '達成すべきこと', 'zh': '要达成什么', 'hi': 'इससे क्या हासिल हो', 'ar': 'ما ينبغي أن يحققه'},
    'edited': {'en': 'Edited', 'es': 'Editado', 'fr': 'Modifié', 'de': 'Bearbeitet', 'pt': 'Editado', 'it': 'Modificato', 'ja': '編集済み', 'zh': '已编辑', 'hi': 'संपादित', 'ar': 'معدّل'},
    'tone': {'en': 'Tone', 'es': 'Tono', 'fr': 'Ton', 'de': 'Ton', 'pt': 'Tom', 'it': 'Tono', 'ja': 'トーン', 'zh': '语气', 'hi': 'लहजा', 'ar': 'النبرة'},
    'trusted_channel': {'en': 'Trusted channel', 'es': 'Canal de confianza', 'fr': 'Canal de confiance', 'de': 'Vertrauenskanal', 'pt': 'Canal de confiança', 'it': 'Canale di fiducia', 'ja': '信頼できる連絡先', 'zh': '可信渠道', 'hi': 'विश्वसनीय चैनल', 'ar': 'القناة الموثوقة'},
    'trusted_name': {'en': 'Trusted name', 'es': 'Nombre de confianza', 'fr': 'Nom de confiance', 'de': 'Vertrauensperson', 'pt': 'Nome de confiança', 'it': 'Nome di fiducia', 'ja': '信頼できる人の名前', 'zh': '可信联系人姓名', 'hi': 'विश्वसनीय नाम', 'ar': 'الاسم الموثوق'},
    'username': {'en': 'Username', 'es': 'Nombre de usuario', 'fr': 'Nom d’utilisateur', 'de': 'Benutzername', 'pt': 'Nome de utilizador', 'it': 'Nome utente', 'ja': 'ユーザー名', 'zh': '用户名', 'hi': 'उपयोगकर्ता नाम', 'ar': 'اسم المستخدم'},
    'window_minutes': {'en': 'Window (minutes)', 'es': 'Ventana (minutos)', 'fr': 'Fenêtre (minutes)', 'de': 'Zeitfenster (Minuten)', 'pt': 'Janela (minutos)', 'it': 'Finestra (minuti)', 'ja': 'ウィンドウ（分）', 'zh': '时间窗（分钟）', 'hi': 'विंडो (मिनट)', 'ar': 'النافذة (بالدقائق)'},    # Aligned to QRME's wording when the sibling-vocabulary guard ran for
    # real the first time: this field IS the engine's voice id, here too.
    'voice_id': {'en': 'Voice ID from the engine', 'es': 'ID de voz del motor', 'fr': 'ID de voix du moteur', 'de': 'Stimm-ID der Engine', 'pt': 'ID de voz do motor', 'it': 'ID voce del motore', 'ja': 'エンジンのボイスID', 'zh': '引擎的声音 ID', 'hi': 'इंजन की वॉइस ID', 'ar': 'معرّف الصوت من المحرّك'},
    'frame_base64': {'en': 'The frame', 'es': 'El fotograma', 'fr': "L'image", 'de': 'Das Bild', 'pt': 'O fotograma', 'it': 'Il fotogramma', 'ja': 'フレーム', 'zh': '画面', 'hi': 'फ़्रेम', 'ar': 'الإطار'},
    'watching_for': {'en': 'What this monitor is watching for', 'es': 'Qué vigila este monitor', 'fr': 'Ce que ce capteur surveille', 'de': 'Worauf dieser Melder achtet', 'pt': 'O que este monitor vigia', 'it': 'Che cosa sorveglia questo sensore', 'ja': 'このモニターが見張っているもの', 'zh': '此监测项在留意什么', 'hi': 'यह मॉनिटर किस बात पर नज़र रखता है', 'ar': 'ما يراقبه هذا المِرقاب'},
    'words': {'en': 'What it heard', 'es': 'Lo que oyó', 'fr': "Ce qu'il a entendu", 'de': 'Was es gehört hat', 'pt': 'O que ouviu', 'it': 'Ciò che ha sentito', 'ja': '聞き取った内容', 'zh': '它听到的内容', 'hi': 'उसने जो सुना', 'ar': 'ما سمعه'},
    'floor': {'en': 'Low-balance floor', 'es': 'Suelo de saldo bajo', 'fr': 'Plancher de solde bas', 'de': 'Untergrenze für den Kontostand', 'pt': 'Piso de saldo baixo', 'it': 'Soglia di saldo basso', 'ja': '残高の下限ライン', 'zh': '低余额下限', 'hi': 'न्यून शेष की सीमा', 'ar': 'الحد الأدنى للرصيد'},

}


def field_label(name: str, language: str) -> str:
    """The label a person sees beside this field, or its identifier."""
    row = _FIELD_LABELS.get(name)
    if not row:
        return name
    return row.get(language) or row.get(DEFAULT) or name


def validation_message(rows: list[dict], language: str) -> str:
    """One sentence, from rows a person was never going to read.

    `validation_detail` above puts pydantic's rows into the reader's language.
    Nine clients then rendered them: the three consoles printed the array as
    JSON, the three Android shells did the same by coercion, and the iOS and
    Windows shells asked for a string, got an array, and fell back to the
    status code. So a mistyped form said either `[{"type":"missing",...}]` or
    `HTTP 422`.

        asked     is the refusal translated
        mattered  is the refusal a sentence

    Composed here rather than in each client for the reason the refusal
    handler is one handler: nine renderings of one thing are nine chances to
    render it differently, and six of these are in languages with no test
    runner in this repository.

    ## What stays an identifier

    The field name is not translated and is not meant to read as a word. It is
    the API's name for the field — `display_name` — which is the same string in
    every language, and it is joined to the sentence with an em dash rather
    than declined into it, so nothing here is half in one language and half in
    another — the one thing `tests/refusals_untranslated.txt` will not record
    its way out of.

    Mapping those names to the labels a form actually shows — *"Nome de
    exibição"* rather than `display_name` — is a per-client table this does not
    have, and is recorded as the remaining gap rather than guessed at.

    Carries nothing `detail` does not: the same `loc` and the same already
    redacted `msg`, which is what `test_the_sentence_says_no_more_than_the_rows`
    holds it to.
    """
    parts = []
    for row in rows:
        where = [str(p) for p in row.get("loc", ())]
        if where and where[0] in _WHERE_MARKERS:
            where = where[1:]
        name = ".".join(tr_refusal(p, language) if p == UNRECOGNISED_FIELD
                        else field_label(p, language) for p in where)
        said = str(row.get("msg", ""))
        parts.append(f"{name} — {said}" if name else said)
    return "; ".join(p for p in parts if p)


#: Pydantic's own catalogue, for the messages this product's forms can
#: produce. Safe to pass through untranslated as well as translated: these
#: sentences interpolate limits, never the value that failed. Anything not
#: here falls through as English, which is a visible gap rather than a
#: confident error.
_VALIDATION: dict[str, dict[str, str]] = {
    # Not a message but a field name, and the one field name that is prose:
    # `validation_detail` substitutes it where a caller's own key would
    # otherwise be echoed, so it lands in the sentence `validation_message`
    # composes and has to be readable there.
    UNRECOGNISED_FIELD: {
        'es': '<campo no reconocido>',
        'fr': '<champ non reconnu>',
        'de': '<unbekanntes Feld>',
        'pt': '<campo não reconhecido>',
        'it': '<campo non riconosciuto>',
        'ja': '<認識できない項目>',
        'zh': '<无法识别的字段>',
        'hi': '<अपरिचित फ़ील्ड>',
        'ar': '<حقل غير معروف>',
    },
    UNSPECIFIED_VALUE_ERROR: {
        'es': 'ese valor no es aceptable aquí',
        'fr': "cette valeur n'est pas acceptable ici",
        'de': 'dieser Wert ist hier nicht zulässig',
        'pt': 'esse valor não é aceitável aqui',
        'it': 'questo valore non è accettabile qui',
        'ja': 'この値はここでは使えません',
        'zh': '此处不接受该值',
        'hi': 'यह मान यहाँ स्वीकार्य नहीं है',
        'ar': 'هذه القيمة غير مقبولة هنا',
    },
    'Field required': {
        'es': 'campo obligatorio',
        'fr': 'champ requis',
        'de': 'Pflichtfeld',
        'pt': 'campo obrigatório',
        'it': 'campo obbligatorio',
        'ja': '必須項目です',
        'zh': '此字段为必填项',
        'hi': 'यह फ़ील्ड आवश्यक है',
        'ar': 'حقل مطلوب',
    },
    'Extra inputs are not permitted': {
        'es': 'no se admiten campos adicionales',
        'fr': 'les champs supplémentaires ne sont pas autorisés',
        'de': 'zusätzliche Felder sind nicht zulässig',
        'pt': 'não são permitidos campos adicionais',
        'it': 'non sono ammessi campi aggiuntivi',
        'ja': '追加の項目は指定できません',
        'zh': '不允许提供额外字段',
        'hi': 'अतिरिक्त फ़ील्ड की अनुमति नहीं है',
        'ar': 'لا يُسمح بحقول إضافية',
    },
    'Input should be a valid string': {
        'es': 'debe ser una cadena de texto válida',
        'fr': 'doit être une chaîne de caractères valide',
        'de': 'muss eine gültige Zeichenkette sein',
        'pt': 'tem de ser uma cadeia de texto válida',
        'it': 'deve essere una stringa valida',
        'ja': '有効な文字列を指定してください',
        'zh': '应为有效的字符串',
        'hi': 'यह एक मान्य स्ट्रिंग होनी चाहिए',
        'ar': 'يجب أن تكون سلسلة نصية صالحة',
    },
    'Input should be a valid integer': {
        'es': 'debe ser un número entero válido',
        'fr': 'doit être un entier valide',
        'de': 'muss eine gültige ganze Zahl sein',
        'pt': 'tem de ser um número inteiro válido',
        'it': 'deve essere un numero intero valido',
        'ja': '有効な整数を指定してください',
        'zh': '应为有效的整数',
        'hi': 'यह एक मान्य पूर्णांक होना चाहिए',
        'ar': 'يجب أن يكون عددًا صحيحًا صالحًا',
    },
    'Input should be a valid number': {
        'es': 'debe ser un número válido',
        'fr': 'doit être un nombre valide',
        'de': 'muss eine gültige Zahl sein',
        'pt': 'tem de ser um número válido',
        'it': 'deve essere un numero valido',
        'ja': '有効な数値を指定してください',
        'zh': '应为有效的数字',
        'hi': 'यह एक मान्य संख्या होनी चाहिए',
        'ar': 'يجب أن يكون رقمًا صالحًا',
    },
    'Input should be a valid boolean': {
        'es': 'debe ser un valor booleano válido',
        'fr': 'doit être un booléen valide',
        'de': 'muss ein gültiger Wahrheitswert sein',
        'pt': 'tem de ser um valor booleano válido',
        'it': 'deve essere un valore booleano valido',
        'ja': '有効な真偽値を指定してください',
        'zh': '应为有效的布尔值',
        'hi': 'यह एक मान्य बूलियन मान होना चाहिए',
        'ar': 'يجب أن تكون قيمة منطقية صالحة',
    },
    'Input should be a valid list': {
        'es': 'debe ser una lista válida',
        'fr': 'doit être une liste valide',
        'de': 'muss eine gültige Liste sein',
        'pt': 'tem de ser uma lista válida',
        'it': 'deve essere un elenco valido',
        'ja': '有効なリストを指定してください',
        'zh': '应为有效的列表',
        'hi': 'यह एक मान्य सूची होनी चाहिए',
        'ar': 'يجب أن تكون قائمة صالحة',
    },
    'Input should be a valid dictionary': {
        'es': 'debe ser un objeto válido',
        'fr': 'doit être un objet valide',
        'de': 'muss ein gültiges Objekt sein',
        'pt': 'tem de ser um objeto válido',
        'it': 'deve essere un oggetto valido',
        'ja': '有効なオブジェクトを指定してください',
        'zh': '应为有效的对象',
        'hi': 'यह एक मान्य ऑब्जेक्ट होना चाहिए',
        'ar': 'يجب أن يكون كائنًا صالحًا',
    },
    'Input should be a valid date': {
        'es': 'debe ser una fecha válida',
        'fr': 'doit être une date valide',
        'de': 'muss ein gültiges Datum sein',
        'pt': 'tem de ser uma data válida',
        'it': 'deve essere una data valida',
        'ja': '有効な日付を指定してください',
        'zh': '应为有效的日期',
        'hi': 'यह एक मान्य दिनांक होनी चाहिए',
        'ar': 'يجب أن يكون تاريخًا صالحًا',
    },
}


# --------------------------------------------------------------------------
# The money guardian (jim/money.py).
#
# Sentences and labels both live server-side, and the reason is the console
# backlog: the desktop console has no translation table of its own, and
# every English literal a screen adds is a row in a ratchet that only
# shrinks. So the Money card renders what `GET /money/{id}` hands it —
# composed here, in the reader's language, by the same code that raises the
# warnings. The screen shows; the server speaks.

_MONEY_TEXT: dict[str, dict[str, str]] = {
    'low_balance': {
        'en': 'Your liquid balance is {balance}, under your {floor} cushion. Worth a look before the next bill — the finance coach and a specialist are one tap away.',
        'es': 'Tu saldo líquido es {balance}, por debajo de tu colchón de {floor}. Vale la pena mirarlo antes de la próxima factura: el coach financiero y un especialista están a un toque.',
        'fr': 'Votre solde liquide est de {balance}, sous votre coussin de {floor}. Un coup d\'œil s\'impose avant la prochaine facture — le coach financier et un spécialiste sont à un geste.',
        'de': 'Dein liquides Guthaben liegt bei {balance}, unter deinem Polster von {floor}. Ein Blick lohnt sich vor der nächsten Rechnung — der Finanz-Coach und ein Spezialist sind einen Tipp entfernt.',
        'pt': 'O seu saldo líquido é {balance}, abaixo da sua almofada de {floor}. Vale a pena olhar antes da próxima conta — o coach financeiro e um especialista estão a um toque.',
        'it': 'Il tuo saldo liquido è {balance}, sotto il tuo cuscinetto di {floor}. Vale un\'occhiata prima della prossima bolletta — il coach finanziario e uno specialista sono a un tocco.',
        'ja': '流動残高は{balance}で、クッションの{floor}を下回っています。次の請求の前に確認を — ファイナンスコーチと専門家がワンタップで呼べます。',
        'zh': '你的流动余额为 {balance}，低于 {floor} 的缓冲线。下一笔账单前值得看一眼——理财教练和专家一键可达。',
        'hi': 'आपकी तरल शेष राशि {balance} है, जो आपके {floor} के कुशन से कम है। अगले बिल से पहले देख लेना ठीक रहेगा — वित्त कोच और विशेषज्ञ एक टैप की दूरी पर हैं।',
        'ar': 'رصيدك السائل {balance}، وهو دون وسادتك البالغة {floor}. يستحق نظرة قبل الفاتورة القادمة — مدرب المال والاختصاصي على بُعد لمسة.',
    },
    'goal_reached': {
        'en': 'You reached your savings goal of {goal}. Set the next one, or talk to the coach about what this cushion makes possible.',
        'es': 'Alcanzaste tu meta de ahorro de {goal}. Fija la siguiente, o habla con el coach sobre lo que este colchón hace posible.',
        'fr': 'Vous avez atteint votre objectif d\'épargne de {goal}. Fixez le prochain, ou parlez au coach de ce que ce coussin rend possible.',
        'de': 'Du hast dein Sparziel von {goal} erreicht. Setz dir das nächste — oder sprich mit dem Coach darüber, was dieses Polster möglich macht.',
        'pt': 'Atingiu a sua meta de poupança de {goal}. Defina a próxima, ou fale com o coach sobre o que esta almofada torna possível.',
        'it': 'Hai raggiunto il tuo obiettivo di risparmio di {goal}. Fissane un altro, o parla con il coach di cosa rende possibile questo cuscinetto.',
        'ja': '貯蓄目標の{goal}に到達しました。次の目標を立てるか、この余裕で何ができるかコーチに相談してみましょう。',
        'zh': '你达成了 {goal} 的储蓄目标。设定下一个，或和教练聊聊这份缓冲能带来什么。',
        'hi': 'आपने {goal} का बचत लक्ष्य पा लिया। अगला लक्ष्य तय करें, या कोच से बात करें कि यह कुशन क्या संभव बनाता है।',
        'ar': 'بلغت هدف ادخارك البالغ {goal}. حدّد الهدف التالي، أو تحدث مع المدرب عمّا تتيحه هذه الوسادة.',
    },
    'order_rationale': {
        'en': 'Liquid cash exceeds your cushion by {excess} (cushion {cushion}); proposing the excess into your first mandated asset class, within your caps.',
        'es': 'El efectivo líquido supera tu colchón en {excess} (colchón {cushion}); se propone invertir el exceso en tu primera clase de activo autorizada, dentro de tus límites.',
        'fr': 'Les liquidités dépassent votre coussin de {excess} (coussin {cushion}) ; proposition de placer l\'excédent dans votre première classe d\'actifs mandatée, dans vos plafonds.',
        'de': 'Die liquiden Mittel übersteigen dein Polster um {excess} (Polster {cushion}); vorgeschlagen wird, den Überschuss in deine erste mandatierte Anlageklasse zu legen, innerhalb deiner Obergrenzen.',
        'pt': 'O dinheiro líquido excede a sua almofada em {excess} (almofada {cushion}); propõe-se investir o excedente na sua primeira classe de ativos mandatada, dentro dos seus limites.',
        'it': 'La liquidità supera il tuo cuscinetto di {excess} (cuscinetto {cushion}); si propone di destinare l\'eccedenza alla prima classe di attivi del mandato, entro i tuoi tetti.',
        'ja': '流動資金がクッションを{excess}上回っています（クッション{cushion}）。超過分を委任された最初の資産クラスへ、上限内で回すことを提案します。',
        'zh': '流动资金超出缓冲 {excess}（缓冲为 {cushion}）；建议在你的上限内，将超出部分投入你授权的第一个资产类别。',
        'hi': 'तरल नकदी आपके कुशन से {excess} अधिक है (कुशन {cushion}); अतिरिक्त राशि को आपकी सीमाओं के भीतर, आपके पहले अधिदिष्ट परिसंपत्ति वर्ग में लगाने का प्रस्ताव है।',
        'ar': 'النقد السائل يتجاوز وسادتك بمقدار {excess} (الوسادة {cushion})؛ يُقترح توجيه الفائض إلى فئة الأصول الأولى في تفويضك، ضمن حدودك.',
    },
    'custody_note': {
        'en': 'Account and routing numbers are sealed in your vault and never shown here; JIM keeps only the institution, the kind, and the last four digits. Orders are proposals — nothing executes without a brokerage connector, and the mandate is yours to revoke at any time.',
        'es': 'Los números de cuenta y de ruta están sellados en tu bóveda y nunca se muestran aquí; JIM guarda solo la institución, el tipo y los últimos cuatro dígitos. Las órdenes son propuestas: nada se ejecuta sin un conector de corretaje, y el mandato es tuyo y puedes revocarlo en cualquier momento.',
        'fr': 'Les numéros de compte et d\'acheminement sont scellés dans votre coffre et jamais affichés ici ; JIM ne conserve que l\'établissement, le type et les quatre derniers chiffres. Les ordres sont des propositions — rien ne s\'exécute sans connecteur de courtage, et le mandat vous appartient, révocable à tout moment.',
        'de': 'Konto- und Routingnummern liegen versiegelt in deinem Tresor und werden hier nie gezeigt; JIM behält nur Institut, Art und die letzten vier Ziffern. Aufträge sind Vorschläge — ohne Broker-Anbindung wird nichts ausgeführt, und das Mandat gehört dir und ist jederzeit widerrufbar.',
        'pt': 'Os números de conta e de encaminhamento estão selados no seu cofre e nunca aparecem aqui; o JIM guarda apenas a instituição, o tipo e os últimos quatro dígitos. As ordens são propostas — nada é executado sem um conector de corretagem, e o mandato é seu, revogável a qualquer momento.',
        'it': 'I numeri di conto e di instradamento sono sigillati nel tuo caveau e non compaiono mai qui; JIM conserva solo l\'istituto, il tipo e le ultime quattro cifre. Gli ordini sono proposte — nulla viene eseguito senza un connettore di intermediazione, e il mandato è tuo, revocabile in qualsiasi momento.',
        'ja': '口座番号とルーティング番号はあなたの金庫に封印され、ここには表示されません。JIMが保持するのは機関名・種類・下4桁のみです。注文は提案であり、証券コネクタなしには何も執行されません。委任はいつでも取り消せます。',
        'zh': '账号与路由号封存在你的保险库中，永不在此显示；JIM 只保留机构、类型和末四位。指令均为提案——没有券商连接器不会执行任何操作，且授权随时可由你撤销。',
        'hi': 'खाता और राउटिंग नंबर आपकी तिजोरी में सीलबंद हैं और यहाँ कभी नहीं दिखते; JIM केवल संस्था, प्रकार और अंतिम चार अंक रखता है। आदेश प्रस्ताव हैं — ब्रोकरेज कनेक्टर के बिना कुछ भी निष्पादित नहीं होता, और अधिदेश आपका है, किसी भी समय रद्द किया जा सकता है।',
        'ar': 'أرقام الحساب والتوجيه مختومة في خزانتك ولا تُعرض هنا أبدًا؛ لا يحتفظ JIM إلا بالمؤسسة والنوع وآخر أربعة أرقام. الأوامر مقترحات — لا يُنفَّذ شيء دون موصل وساطة، والتفويض ملكك وقابل للإلغاء في أي وقت.',
    },
}

_MONEY_LABELS: dict[str, dict[str, str]] = {
    'title': {'en': 'Money', 'es': 'Dinero', 'fr': 'Argent', 'de': 'Geld', 'pt': 'Dinheiro', 'it': 'Denaro', 'ja': 'マネー', 'zh': '财务', 'hi': 'धन', 'ar': 'المال'},
    'accounts': {'en': 'Accounts', 'es': 'Cuentas', 'fr': 'Comptes', 'de': 'Konten', 'pt': 'Contas', 'it': 'Conti', 'ja': '口座', 'zh': '账户', 'hi': 'खाते', 'ar': 'الحسابات'},
    'add_account': {'en': 'Add an account', 'es': 'Añadir una cuenta', 'fr': 'Ajouter un compte', 'de': 'Konto hinzufügen', 'pt': 'Adicionar uma conta', 'it': 'Aggiungi un conto', 'ja': '口座を追加', 'zh': '添加账户', 'hi': 'खाता जोड़ें', 'ar': 'أضف حسابًا'},
    'institution': {'en': 'Institution', 'es': 'Institución', 'fr': 'Établissement', 'de': 'Institut', 'pt': 'Instituição', 'it': 'Istituto', 'ja': '金融機関', 'zh': '机构', 'hi': 'संस्था', 'ar': 'المؤسسة'},
    'account_number': {'en': 'Account number', 'es': 'Número de cuenta', 'fr': 'Numéro de compte', 'de': 'Kontonummer', 'pt': 'Número de conta', 'it': 'Numero di conto', 'ja': '口座番号', 'zh': '账号', 'hi': 'खाता संख्या', 'ar': 'رقم الحساب'},
    'routing_number': {'en': 'Routing number', 'es': 'Número de ruta', 'fr': 'Numéro d\'acheminement', 'de': 'Routingnummer', 'pt': 'Número de encaminhamento', 'it': 'Numero di instradamento', 'ja': 'ルーティング番号', 'zh': '路由号', 'hi': 'राउटिंग नंबर', 'ar': 'رقم التوجيه'},
    'balance': {'en': 'Balance', 'es': 'Saldo', 'fr': 'Solde', 'de': 'Saldo', 'pt': 'Saldo', 'it': 'Saldo', 'ja': '残高', 'zh': '余额', 'hi': 'शेष राशि', 'ar': 'الرصيد'},
    'record_balance': {'en': 'Record a balance', 'es': 'Registrar un saldo', 'fr': 'Enregistrer un solde', 'de': 'Saldo erfassen', 'pt': 'Registar um saldo', 'it': 'Registra un saldo', 'ja': '残高を記録', 'zh': '记录余额', 'hi': 'शेष दर्ज करें', 'ar': 'سجّل رصيدًا'},
    'savings_goal': {'en': 'Savings goal', 'es': 'Meta de ahorro', 'fr': 'Objectif d\'épargne', 'de': 'Sparziel', 'pt': 'Meta de poupança', 'it': 'Obiettivo di risparmio', 'ja': '貯蓄目標', 'zh': '储蓄目标', 'hi': 'बचत लक्ष्य', 'ar': 'هدف الادخار'},
    'low_floor': {'en': 'Low-balance floor', 'es': 'Suelo de saldo bajo', 'fr': 'Plancher de solde bas', 'de': 'Untergrenze für den Kontostand', 'pt': 'Piso de saldo baixo', 'it': 'Soglia di saldo basso', 'ja': '残高の下限ライン', 'zh': '低余额下限', 'hi': 'न्यून शेष की सीमा', 'ar': 'الحد الأدنى للرصيد'},
    'set_floor': {'en': 'Set the floor', 'es': 'Fijar el suelo', 'fr': 'Fixer le plancher', 'de': 'Untergrenze festlegen', 'pt': 'Definir o piso', 'it': 'Imposta la soglia', 'ja': '下限を設定', 'zh': '设定下限', 'hi': 'सीमा तय करें', 'ar': 'حدد الحد الأدنى'},
    'set_goal': {'en': 'Set the goal', 'es': 'Fijar la meta', 'fr': 'Fixer l\'objectif', 'de': 'Ziel festlegen', 'pt': 'Definir a meta', 'it': 'Fissa l\'obiettivo', 'ja': '目標を設定', 'zh': '设定目标', 'hi': 'लक्ष्य तय करें', 'ar': 'حدّد الهدف'},
    'mandate': {'en': 'Investing mandate', 'es': 'Mandato de inversión', 'fr': 'Mandat d\'investissement', 'de': 'Anlagemandat', 'pt': 'Mandato de investimento', 'it': 'Mandato di investimento', 'ja': '投資委任', 'zh': '投资授权', 'hi': 'निवेश अधिदेश', 'ar': 'تفويض الاستثمار'},
    'mandate_save': {'en': 'Write the mandate', 'es': 'Escribir el mandato', 'fr': 'Rédiger le mandat', 'de': 'Mandat festhalten', 'pt': 'Escrever o mandato', 'it': 'Scrivi il mandato', 'ja': '委任を記す', 'zh': '写下授权', 'hi': 'अधिदेश लिखें', 'ar': 'اكتب التفويض'},
    'mandate_revoke': {'en': 'Revoke it', 'es': 'Revocarlo', 'fr': 'Le révoquer', 'de': 'Widerrufen', 'pt': 'Revogá-lo', 'it': 'Revocalo', 'ja': '取り消す', 'zh': '撤销', 'hi': 'रद्द करें', 'ar': 'ألغِه'},
    'cap_per_order': {'en': 'Cap per order', 'es': 'Límite por orden', 'fr': 'Plafond par ordre', 'de': 'Limit pro Auftrag', 'pt': 'Limite por ordem', 'it': 'Tetto per ordine', 'ja': '注文ごとの上限', 'zh': '单笔上限', 'hi': 'प्रति आदेश सीमा', 'ar': 'الحد لكل أمر'},
    'monthly_cap': {'en': 'Monthly cap', 'es': 'Límite mensual', 'fr': 'Plafond mensuel', 'de': 'Monatslimit', 'pt': 'Limite mensal', 'it': 'Tetto mensile', 'ja': '月間上限', 'zh': '每月上限', 'hi': 'मासिक सीमा', 'ar': 'الحد الشهري'},
    'scope': {'en': 'Scope, in your own words', 'es': 'Alcance, con tus palabras', 'fr': 'Périmètre, avec vos mots', 'de': 'Umfang, in deinen Worten', 'pt': 'Âmbito, nas suas palavras', 'it': 'Ambito, con parole tue', 'ja': '範囲（自分の言葉で）', 'zh': '范围（用你自己的话）', 'hi': 'दायरा, आपके अपने शब्दों में', 'ar': 'النطاق، بكلماتك أنت'},
    'orders': {'en': 'Proposed orders', 'es': 'Órdenes propuestas', 'fr': 'Ordres proposés', 'de': 'Vorgeschlagene Aufträge', 'pt': 'Ordens propostas', 'it': 'Ordini proposti', 'ja': '提案された注文', 'zh': '拟议指令', 'hi': 'प्रस्तावित आदेश', 'ar': 'الأوامر المقترحة'},
    'statements': {'en': 'Statements', 'es': 'Extractos', 'fr': 'Relevés', 'de': 'Kontoauszüge', 'pt': 'Extratos', 'it': 'Estratti conto', 'ja': '取引明細', 'zh': '对账单', 'hi': 'विवरण-पत्र', 'ar': 'كشوف الحساب'},
    'drop_statement': {'en': 'Drop a statement into the vault', 'es': 'Depositar un extracto en la bóveda', 'fr': 'Déposer un relevé dans le coffre', 'de': 'Einen Auszug in den Tresor legen', 'pt': 'Depositar um extrato no cofre', 'it': 'Deposita un estratto nel caveau', 'ja': '明細を保管庫に入れる', 'zh': '把对账单放入保险库', 'hi': 'विवरण-पत्र तिजोरी में डालें', 'ar': 'ضع كشف الحساب في الخزنة'},
    'links': {'en': 'Linked banks', 'es': 'Bancos vinculados', 'fr': 'Banques liées', 'de': 'Verknüpfte Banken', 'pt': 'Bancos ligados', 'it': 'Banche collegate', 'ja': '連携済みの銀行', 'zh': '已关联的银行', 'hi': 'जुड़े बैंक', 'ar': 'البنوك المرتبطة'},
    'link_bank': {'en': 'Link a bank', 'es': 'Vincular un banco', 'fr': 'Lier une banque', 'de': 'Bank verknüpfen', 'pt': 'Ligar um banco', 'it': 'Collega una banca', 'ja': '銀行を連携', 'zh': '关联银行', 'hi': 'बैंक जोड़ें', 'ar': 'اربط بنكًا'},
    'aggregator': {'en': 'Aggregator', 'es': 'Agregador', 'fr': 'Agrégateur', 'de': 'Aggregator', 'pt': 'Agregador', 'it': 'Aggregatore', 'ja': 'アグリゲーター', 'zh': '聚合服务', 'hi': 'एग्रीगेटर', 'ar': 'المجمّع'},
    'sync': {'en': 'Sync', 'es': 'Sincronizar', 'fr': 'Synchroniser', 'de': 'Synchronisieren', 'pt': 'Sincronizar', 'it': 'Sincronizza', 'ja': '同期', 'zh': '同步', 'hi': 'सिंक करें', 'ar': 'مزامنة'},
    'revoke_link': {'en': 'Unlink', 'es': 'Desvincular', 'fr': 'Délier', 'de': 'Trennen', 'pt': 'Desligar', 'it': 'Scollega', 'ja': '連携解除', 'zh': '解除关联', 'hi': 'अलग करें', 'ar': 'افصل الربط'},
    'warnings': {'en': 'Warnings', 'es': 'Avisos', 'fr': 'Alertes', 'de': 'Warnungen', 'pt': 'Avisos', 'it': 'Avvisi', 'ja': '警告', 'zh': '提醒', 'hi': 'चेतावनियाँ', 'ar': 'تنبيهات'},
    'doors': {'en': 'Where help is', 'es': 'Dónde está la ayuda', 'fr': 'Où trouver de l\'aide', 'de': 'Wo Hilfe ist', 'pt': 'Onde está a ajuda', 'it': 'Dove trovare aiuto', 'ja': '助けの窓口', 'zh': '求助入口', 'hi': 'मदद कहाँ है', 'ar': 'أين المساعدة'},
}


_SCHEDULE_TEXT: dict[str, dict[str, str]] = {
    'reminder': {'en': 'Coming up: {title} — {when}.', 'es': 'Próximamente: {title} — {when}.', 'fr': 'À venir : {title} — {when}.', 'de': 'Steht an: {title} — {when}.', 'pt': 'Em breve: {title} — {when}.', 'it': 'In arrivo: {title} — {when}.', 'ja': 'まもなく：{title} — {when}。', 'zh': '即将到来：{title} — {when}。', 'hi': 'आने वाला है: {title} — {when}।', 'ar': 'قادم: {title} — {when}.'},
    'mail_subject': {'en': 'Reminder: {title}', 'es': 'Recordatorio: {title}', 'fr': 'Rappel : {title}', 'de': 'Erinnerung: {title}', 'pt': 'Lembrete: {title}', 'it': 'Promemoria: {title}', 'ja': 'リマインダー：{title}', 'zh': '提醒：{title}', 'hi': 'अनुस्मारक: {title}', 'ar': 'تذكير: {title}'},
    'mail_note': {'en': 'Email reminders go to the verified address that owns this account — and to no other address, ever.', 'es': 'Los recordatorios por correo van a la dirección verificada de esta cuenta — y a ninguna otra, nunca.', 'fr': "Les rappels par e-mail vont à l'adresse vérifiée de ce compte — et à aucune autre, jamais.", 'de': 'E-Mail-Erinnerungen gehen an die verifizierte Adresse dieses Kontos — und nie an eine andere.', 'pt': 'Os lembretes por e-mail vão para o endereço verificado desta conta — e para nenhum outro, nunca.', 'it': "I promemoria via e-mail vanno all'indirizzo verificato di questo account — e a nessun altro, mai.", 'ja': 'メールのリマインダーは、このアカウントの確認済みアドレスにのみ送られます。ほかの宛先には決して送られません。', 'zh': '邮件提醒只发送到本账户的已验证地址 — 绝不发送到其他任何地址。', 'hi': 'ईमेल अनुस्मारक केवल इस खाते के सत्यापित पते पर जाते हैं — कभी किसी और पते पर नहीं।', 'ar': 'تذهب تذكيرات البريد إلى العنوان الموثّق لهذا الحساب فقط — ولا إلى أي عنوان آخر أبدًا.'},
}

_SCHEDULE_LABELS: dict[str, dict[str, str]] = {
    'title': {'en': 'Schedule', 'es': 'Agenda', 'fr': 'Agenda', 'de': 'Kalender', 'pt': 'Agenda', 'it': 'Agenda', 'ja': '予定', 'zh': '日程', 'hi': 'कार्यक्रम', 'ar': 'الجدول'},
    'book': {'en': 'Book it', 'es': 'Reservar', 'fr': 'Réserver', 'de': 'Buchen', 'pt': 'Marcar', 'it': 'Prenota', 'ja': '予約する', 'zh': '预订', 'hi': 'बुक करें', 'ar': 'احجز'},
    'what': {'en': 'What', 'es': 'Qué', 'fr': 'Quoi', 'de': 'Was', 'pt': 'O quê', 'it': 'Cosa', 'ja': '内容', 'zh': '内容', 'hi': 'क्या', 'ar': 'ماذا'},
    'when': {'en': 'When', 'es': 'Cuándo', 'fr': 'Quand', 'de': 'Wann', 'pt': 'Quando', 'it': 'Quando', 'ja': '日時', 'zh': '时间', 'hi': 'कब', 'ar': 'متى'},
    'where': {'en': 'Where', 'es': 'Dónde', 'fr': 'Où', 'de': 'Wo', 'pt': 'Onde', 'it': 'Dove', 'ja': '場所', 'zh': '地点', 'hi': 'कहाँ', 'ar': 'أين'},
    'email_me': {'en': 'Email me a reminder', 'es': 'Envíame un recordatorio por correo', 'fr': "M'envoyer un rappel par e-mail", 'de': 'Erinnerung per E-Mail senden', 'pt': 'Enviar-me um lembrete por e-mail', 'it': 'Inviami un promemoria via e-mail', 'ja': 'メールでリマインドする', 'zh': '给我发邮件提醒', 'hi': 'मुझे ईमेल अनुस्मारक भेजें', 'ar': 'أرسل لي تذكيرًا بالبريد'},
    'no_email': {'en': 'No verified email on this account', 'es': 'Esta cuenta no tiene correo verificado', 'fr': "Pas d'e-mail vérifié sur ce compte", 'de': 'Keine verifizierte E-Mail für dieses Konto', 'pt': 'Sem e-mail verificado nesta conta', 'it': 'Nessuna e-mail verificata su questo account', 'ja': 'このアカウントに確認済みメールがありません', 'zh': '此账户没有已验证的邮箱', 'hi': 'इस खाते में कोई सत्यापित ईमेल नहीं', 'ar': 'لا بريد موثّق في هذا الحساب'},
    'upcoming': {'en': 'Coming up', 'es': 'Próximas', 'fr': 'À venir', 'de': 'Anstehend', 'pt': 'Próximas', 'it': 'In arrivo', 'ja': 'これからの予定', 'zh': '即将到来', 'hi': 'आगामी', 'ar': 'القادم'},
    'cancel': {'en': 'Cancel', 'es': 'Cancelar', 'fr': 'Annuler', 'de': 'Absagen', 'pt': 'Cancelar', 'it': 'Annulla', 'ja': 'キャンセル', 'zh': '取消', 'hi': 'रद्द करें', 'ar': 'إلغاء'},
    'service': {'en': 'Book a shop service', 'es': 'Reservar un servicio de tienda', 'fr': 'Réserver un service de boutique', 'de': 'Laden-Dienstleistung buchen', 'pt': 'Marcar um serviço de loja', 'it': 'Prenota un servizio del negozio', 'ja': 'ショップのサービスを予約', 'zh': '预订店铺服务', 'hi': 'दुकान की सेवा बुक करें', 'ar': 'احجز خدمة من متجر'},
}


def schedule_text(key: str, language: str) -> str:
    row = _SCHEDULE_TEXT[key]
    return row.get(language) or row['en']


def schedule_labels(language: str) -> dict[str, str]:
    return {k: (row.get(language) or row['en'])
            for k, row in _SCHEDULE_LABELS.items()}


_FAREND_TEXT: dict[str, dict[str, str]] = {
    'alert_subject': {'en': 'JIM-mini: {name} may need help', 'es': 'JIM-mini: {name} puede necesitar ayuda', 'fr': "JIM-mini : {name} a peut-être besoin d'aide", 'de': 'JIM-mini: {name} braucht möglicherweise Hilfe', 'pt': 'JIM-mini: {name} pode precisar de ajuda', 'it': 'JIM-mini: {name} potrebbe avere bisogno di aiuto', 'ja': 'JIM-mini：{name} さんに助けが必要かもしれません', 'zh': 'JIM-mini：{name} 可能需要帮助', 'hi': 'JIM-mini: {name} को मदद की ज़रूरत हो सकती है', 'ar': 'JIM-mini: قد يحتاج {name} إلى مساعدة'},
    'alert_body': {
        'en': 'JIM-mini detected {condition} — {reason}\n\nYou are {name}\'s emergency contact, and the escalation decision was: {tier}. Please check on them now.\n\nWhen you have seen this, press the link below so JIM knows a person is aware:\n{link}',
        'es': 'JIM-mini detectó {condition} — {reason}\n\nEres el contacto de emergencia de {name}, y la decisión de escalada fue: {tier}. Por favor, ve a ver cómo está ahora.\n\nCuando hayas visto esto, pulsa el enlace para que JIM sepa que una persona está al tanto:\n{link}',
        'fr': 'JIM-mini a détecté {condition} — {reason}\n\nVous êtes le contact d\'urgence de {name}, et la décision d\'escalade était : {tier}. Merci d\'aller voir comment il ou elle va, maintenant.\n\nQuand vous aurez vu ceci, appuyez sur le lien ci-dessous pour que JIM sache qu\'une personne est au courant :\n{link}',
        'de': 'JIM-mini hat {condition} erkannt — {reason}\n\nDu bist der Notfallkontakt von {name}, und die Eskalationsentscheidung war: {tier}. Bitte sieh jetzt nach.\n\nWenn du das gesehen hast, drücke den Link, damit JIM weiß, dass ein Mensch Bescheid weiß:\n{link}',
        'pt': 'O JIM-mini detetou {condition} — {reason}\n\nÉ o contacto de emergência de {name}, e a decisão de escalada foi: {tier}. Por favor, vá ver como está agora.\n\nQuando tiver visto isto, prima a ligação abaixo para que o JIM saiba que uma pessoa está a par:\n{link}',
        'it': 'JIM-mini ha rilevato {condition} — {reason}\n\nSei il contatto di emergenza di {name}, e la decisione di escalation è stata: {tier}. Per favore, vai a controllare adesso.\n\nQuando avrai visto questo, premi il link qui sotto così JIM sa che una persona ne è al corrente:\n{link}',
        'ja': 'JIM-mini が {condition} を検知しました — {reason}\n\nあなたは {name} さんの緊急連絡先です。エスカレーションの判断は「{tier}」でした。いますぐ様子を確認してください。\n\n確認したら、下のリンクを押してください。人が把握したことを JIM が記録します：\n{link}',
        'zh': 'JIM-mini 检测到 {condition} — {reason}\n\n你是 {name} 的紧急联系人，升级决定为：{tier}。请立即去看看他们的情况。\n\n看到此消息后，请点击下面的链接，让 JIM 知道已有人知晓：\n{link}',
        'hi': 'JIM-mini ने {condition} का पता लगाया — {reason}\n\nआप {name} के आपातकालीन संपर्क हैं, और एस्केलेशन निर्णय था: {tier}। कृपया अभी जाकर उनका हाल देखें।\n\nइसे देख लेने पर नीचे दिया लिंक दबाएँ ताकि JIM जान सके कि कोई व्यक्ति अवगत है:\n{link}',
        'ar': 'اكتشف JIM-mini {condition} — {reason}\n\nأنت جهة اتصال الطوارئ لـ {name}، وكان قرار التصعيد: {tier}. يرجى الاطمئنان عليه الآن.\n\nعندما ترى هذا، اضغط الرابط أدناه ليعلم JIM أن إنسانًا على دراية:\n{link}'},
    'refusal': {'en': 'There is no one on the far end of this today — no consented email address is set, so no person was notified.', 'es': 'Hoy no hay nadie al otro extremo — no hay una dirección de correo consentida, así que no se avisó a ninguna persona.', 'fr': "Il n'y a personne à l'autre bout aujourd'hui — aucune adresse e-mail consentie n'est définie, donc aucune personne n'a été prévenue.", 'de': 'Am anderen Ende steht heute niemand — keine eingewilligte E-Mail-Adresse ist hinterlegt, also wurde kein Mensch benachrichtigt.', 'pt': 'Hoje não há ninguém do outro lado — não há um endereço de e-mail consentido, por isso nenhuma pessoa foi avisada.', 'it': "Oggi non c'è nessuno all'altro capo — nessun indirizzo email consentito è impostato, quindi nessuna persona è stata avvisata.", 'ja': '今日はこの先に誰もいません — 同意済みのメールアドレスが設定されていないため、誰にも通知されませんでした。', 'zh': '今天这条线的另一端没有人 — 未设置经同意的邮箱地址，因此没有通知到任何人。', 'hi': 'आज इसके दूसरे छोर पर कोई नहीं है — कोई सहमति-प्राप्त ईमेल पता सेट नहीं है, इसलिए किसी व्यक्ति को सूचित नहीं किया गया।', 'ar': 'لا يوجد أحد على الطرف الآخر اليوم — لا يوجد بريد إلكتروني موافق عليه، لذا لم يُخطر أي شخص.'},
    'ack_title': {'en': 'Seen, and recorded', 'es': 'Visto y registrado', 'fr': 'Vu, et enregistré', 'de': 'Gesehen und festgehalten', 'pt': 'Visto e registado', 'it': 'Visto e registrato', 'ja': '確認を記録しました', 'zh': '已看到，已记录', 'hi': 'देखा गया, और दर्ज किया गया', 'ar': 'تمت الرؤية والتسجيل'},
    'ack_body': {'en': 'JIM has recorded that a person has seen this alert. Thank you for standing on the far end.', 'es': 'JIM ha registrado que una persona ha visto esta alerta. Gracias por estar al otro extremo.', 'fr': "JIM a enregistré qu'une personne a vu cette alerte. Merci d'être à l'autre bout.", 'de': 'JIM hat festgehalten, dass ein Mensch diese Warnung gesehen hat. Danke, dass du am anderen Ende stehst.', 'pt': 'O JIM registou que uma pessoa viu este alerta. Obrigado por estar do outro lado.', 'it': 'JIM ha registrato che una persona ha visto questo avviso. Grazie per essere all\'altro capo.', 'ja': '人がこのアラートを確認したことを JIM が記録しました。見守ってくださってありがとうございます。', 'zh': 'JIM 已记录有人看到了此警报。谢谢你守在线的另一端。', 'hi': 'JIM ने दर्ज किया है कि एक व्यक्ति ने यह अलर्ट देख लिया है। दूसरे छोर पर खड़े रहने के लिए धन्यवाद।', 'ar': 'سجل JIM أن إنسانًا رأى هذا التنبيه. شكرًا لوقوفك على الطرف الآخر.'},
    'ack_already_title': {'en': 'Already recorded', 'es': 'Ya registrado', 'fr': 'Déjà enregistré', 'de': 'Bereits festgehalten', 'pt': 'Já registado', 'it': 'Già registrato', 'ja': '記録済みです', 'zh': '已记录过', 'hi': 'पहले से दर्ज', 'ar': 'مسجل مسبقًا'},
    'ack_already_body': {'en': 'This alert was acknowledged earlier — nothing more is needed.', 'es': 'Esta alerta ya fue confirmada antes — no hace falta nada más.', 'fr': 'Cette alerte a déjà été confirmée — rien de plus n\'est nécessaire.', 'de': 'Diese Warnung wurde schon früher bestätigt — mehr ist nicht nötig.', 'pt': 'Este alerta já foi confirmado antes — não é preciso mais nada.', 'it': 'Questo avviso era già stato confermato — non serve altro.', 'ja': 'このアラートは先ほど確認済みです — これ以上の操作は不要です。', 'zh': '此警报早前已被确认 — 无需再做任何事。', 'hi': 'यह अलर्ट पहले ही स्वीकृत किया जा चुका है — और कुछ करने की ज़रूरत नहीं।', 'ar': 'تم تأكيد هذا التنبيه سابقًا — لا حاجة إلى المزيد.'},
    'ack_bad_title': {'en': "That link didn't work", 'es': 'Ese enlace no funcionó', 'fr': "Ce lien n'a pas fonctionné", 'de': 'Dieser Link hat nicht funktioniert', 'pt': 'Essa ligação não funcionou', 'it': 'Quel link non ha funzionato', 'ja': 'このリンクは無効です', 'zh': '该链接无效', 'hi': 'वह लिंक काम नहीं किया', 'ar': 'هذا الرابط لم يعمل'},
    'ack_bad_body': {'en': 'This acknowledgment link is unknown. If it came from a real JIM alert, ask the person who set JIM up.', 'es': 'Este enlace de confirmación es desconocido. Si vino de una alerta real de JIM, pregunta a quien configuró JIM.', 'fr': "Ce lien de confirmation est inconnu. S'il vient d'une vraie alerte JIM, demandez à la personne qui a configuré JIM.", 'de': 'Dieser Bestätigungslink ist unbekannt. Wenn er aus einer echten JIM-Warnung stammt, frage die Person, die JIM eingerichtet hat.', 'pt': 'Esta ligação de confirmação é desconhecida. Se veio de um alerta real do JIM, pergunte a quem configurou o JIM.', 'it': 'Questo link di conferma è sconosciuto. Se proviene da un vero avviso di JIM, chiedi a chi ha configurato JIM.', 'ja': 'この確認リンクは不明です。本物の JIM アラートからのものであれば、JIM を設定した人に確認してください。', 'zh': '此确认链接无法识别。如果它来自真实的 JIM 警报，请询问设置 JIM 的人。', 'hi': 'यह पुष्टि लिंक अज्ञात है। अगर यह किसी असली JIM अलर्ट से आया है, तो JIM सेट करने वाले व्यक्ति से पूछें।', 'ar': 'رابط التأكيد هذا غير معروف. إن كان من تنبيه JIM حقيقي، فاسأل من قام بإعداد JIM.'},
    'undelivered': {'en': 'A letter was written, but this machine has no mail server configured — it was printed on the server instead of sent, so no person was notified.', 'es': 'Se escribió una carta, pero esta máquina no tiene servidor de correo configurado — se imprimió en el servidor en lugar de enviarse, así que no se avisó a ninguna persona.', 'fr': "Une lettre a été rédigée, mais aucun serveur de messagerie n'est configuré sur cette machine — elle a été imprimée sur le serveur au lieu d'être envoyée, donc aucune personne n'a été prévenue.", 'de': 'Ein Brief wurde verfasst, aber auf dieser Maschine ist kein Mailserver eingerichtet — er wurde auf dem Server ausgegeben statt versendet, also wurde kein Mensch benachrichtigt.', 'pt': 'Foi escrita uma carta, mas esta máquina não tem servidor de e-mail configurado — foi impressa no servidor em vez de enviada, por isso nenhuma pessoa foi avisada.', 'it': "È stata scritta una lettera, ma su questa macchina non è configurato alcun server di posta — è stata stampata sul server invece di essere inviata, quindi nessuna persona è stata avvisata.", 'ja': '手紙は書かれましたが、この機械にはメールサーバーが設定されていません — 送信されずサーバー上に出力されたため、誰にも通知されていません。', 'zh': '信已经写好，但这台机器没有配置邮件服务器 — 它被打印在服务器上而不是寄出，因此没有通知到任何人。', 'hi': 'पत्र लिखा गया, लेकिन इस मशीन पर कोई मेल सर्वर सेट नहीं है — वह भेजा नहीं गया बल्कि सर्वर पर छप गया, इसलिए किसी व्यक्ति को सूचित नहीं किया गया।', 'ar': 'كُتبت رسالة، لكن لا يوجد خادم بريد مُعدّ على هذا الجهاز — طُبعت على الخادم بدل أن تُرسل، لذا لم يُخطر أي شخص.'},
    'ping_subject': {'en': "JIM-mini: a monthly note for {name}'s far end", 'es': 'JIM-mini: nota mensual para el otro extremo de {name}', 'fr': "JIM-mini : note mensuelle pour l'autre bout de {name}", 'de': 'JIM-mini: monatliche Notiz an das andere Ende von {name}', 'pt': 'JIM-mini: nota mensal para o outro lado de {name}', 'it': "JIM-mini: nota mensile per l'altro capo di {name}", 'ja': 'JIM-mini：{name} さんの見守り先への月次のお知らせ', 'zh': 'JIM-mini：给 {name} 的守护端的每月便条', 'hi': 'JIM-mini: {name} के दूसरे छोर के लिए मासिक नोट', 'ar': 'JIM-mini: رسالة شهرية إلى الطرف الآخر لـ {name}'},
    'ping_body': {
        'en': 'You are the address JIM-mini writes to if {name} needs help. Nothing is wrong and nothing is asked of you: in the last {days} days JIM stood watch and recorded {events} events. This note exists so a dead mailbox is discovered on a calm day, not during an emergency.',
        'es': 'Tú eres la dirección a la que JIM-mini escribe si {name} necesita ayuda. No pasa nada y no se te pide nada: en los últimos {days} días JIM montó guardia y registró {events} eventos. Esta nota existe para que un buzón muerto se descubra en un día tranquilo, no durante una emergencia.',
        'fr': "Vous êtes l'adresse à laquelle JIM-mini écrit si {name} a besoin d'aide. Tout va bien et rien ne vous est demandé : ces {days} derniers jours, JIM a monté la garde et enregistré {events} événements. Cette note existe pour qu'une boîte morte soit découverte un jour calme, pas pendant une urgence.",
        'de': 'Du bist die Adresse, an die JIM-mini schreibt, wenn {name} Hilfe braucht. Nichts ist passiert und nichts wird von dir verlangt: In den letzten {days} Tagen hielt JIM Wache und verzeichnete {events} Ereignisse. Diese Notiz gibt es, damit ein totes Postfach an einem ruhigen Tag entdeckt wird — nicht im Notfall.',
        'pt': 'É para este endereço que o JIM-mini escreve se {name} precisar de ajuda. Está tudo bem e nada lhe é pedido: nos últimos {days} dias o JIM montou guarda e registou {events} eventos. Esta nota existe para que uma caixa morta seja descoberta num dia calmo, não durante uma emergência.',
        'it': "Sei l'indirizzo a cui JIM-mini scrive se {name} ha bisogno di aiuto. Va tutto bene e non ti si chiede nulla: negli ultimi {days} giorni JIM ha fatto la guardia e registrato {events} eventi. Questa nota esiste perché una casella morta si scopra in un giorno tranquillo, non durante un'emergenza.",
        'ja': 'あなたは {name} さんに助けが必要なとき JIM-mini が手紙を送る宛先です。何も起きておらず、お願いもありません。この {days} 日間、JIM は見守りを続け、{events} 件の出来事を記録しました。このお知らせは、使われなくなったメールボックスを緊急時ではなく平穏な日に発見するためのものです。',
        'zh': '如果 {name} 需要帮助，JIM-mini 会写信到这个地址。现在一切正常，也不需要你做任何事：过去 {days} 天里，JIM 一直在守护，记录了 {events} 个事件。这张便条的意义在于：让失效的邮箱在平静的日子被发现，而不是在紧急关头。',
        'hi': 'अगर {name} को मदद चाहिए तो JIM-mini इसी पते पर लिखता है। सब ठीक है और आपसे कुछ नहीं माँगा जा रहा: पिछले {days} दिनों में JIM पहरे पर रहा और {events} घटनाएँ दर्ज कीं। यह नोट इसलिए है ताकि एक बंद पड़ा मेलबॉक्स किसी शांत दिन पकड़ में आ जाए, आपातकाल में नहीं।',
        'ar': 'أنت العنوان الذي يكتب إليه JIM-mini إذا احتاج {name} إلى مساعدة. كل شيء على ما يرام ولا يُطلب منك شيء: خلال آخر {days} يومًا ظل JIM يراقب وسجل {events} حدثًا. هذه الرسالة موجودة كي يُكتشف صندوق بريد ميت في يوم هادئ، لا أثناء طارئ.'},
}


def farend_text(key: str, language: str) -> str:
    row = _FAREND_TEXT[key]
    return row.get(language) or row['en']


_SHOP_TEXT: dict[str, dict[str, str]] = {
    'held_here': {'en': 'Your purchase history is held here, in your own JIM — QRME is never asked what you bought.', 'es': 'Tu historial de compras se guarda aquí, en tu propio JIM — nunca se le pregunta a QRME qué compraste.', 'fr': "Votre historique d'achats est conservé ici, dans votre propre JIM — on ne demande jamais à QRME ce que vous avez acheté.", 'de': 'Deine Kaufhistorie liegt hier, in deinem eigenen JIM — QRME wird nie gefragt, was du gekauft hast.', 'pt': 'O seu histórico de compras fica aqui, no seu próprio JIM — nunca se pergunta ao QRME o que comprou.', 'it': 'La tua cronologia acquisti resta qui, nel tuo JIM — a QRME non viene mai chiesto cosa hai comprato.', 'ja': '購入履歴はあなた自身の JIM に保管されます — 何を買ったかを QRME に尋ねることはありません。', 'zh': '你的购买记录保存在你自己的 JIM 里 — 绝不会向 QRME 询问你买了什么。', 'hi': 'आपका ख़रीद इतिहास यहीं, आपके अपने JIM में रहता है — QRME से कभी नहीं पूछा जाता कि आपने क्या खरीदा।', 'ar': 'سجل مشترياتك محفوظ هنا في JIM الخاص بك — لا يُسأل QRME أبدًا عمّا اشتريته.'},
}

_SHOP_LABELS: dict[str, dict[str, str]] = {
    'title': {'en': 'Shops', 'es': 'Tiendas', 'fr': 'Boutiques', 'de': 'Läden', 'pt': 'Lojas', 'it': 'Negozi', 'ja': 'ショップ', 'zh': '商店', 'hi': 'दुकानें', 'ar': 'المتاجر'},
    'browse': {'en': 'Browse', 'es': 'Ver', 'fr': 'Parcourir', 'de': 'Ansehen', 'pt': 'Ver', 'it': 'Sfoglia', 'ja': '見る', 'zh': '逛逛', 'hi': 'देखें', 'ar': 'تصفّح'},
    'order': {'en': 'Order', 'es': 'Pedir', 'fr': 'Commander', 'de': 'Bestellen', 'pt': 'Encomendar', 'it': 'Ordina', 'ja': '注文', 'zh': '下单', 'hi': 'ऑर्डर करें', 'ar': 'اطلب'},
    'quantity': {'en': 'Quantity', 'es': 'Cantidad', 'fr': 'Quantité', 'de': 'Menge', 'pt': 'Quantidade', 'it': 'Quantità', 'ja': '数量', 'zh': '数量', 'hi': 'मात्रा', 'ar': 'الكمية'},
    'receipts': {'en': 'Your orders', 'es': 'Tus pedidos', 'fr': 'Vos commandes', 'de': 'Deine Bestellungen', 'pt': 'Os seus pedidos', 'it': 'I tuoi ordini', 'ja': 'あなたの注文', 'zh': '你的订单', 'hi': 'आपके ऑर्डर', 'ar': 'طلباتك'},
    'cancel': {'en': 'Cancel', 'es': 'Cancelar', 'fr': 'Annuler', 'de': 'Stornieren', 'pt': 'Cancelar', 'it': 'Annulla', 'ja': 'キャンセル', 'zh': '取消', 'hi': 'रद्द करें', 'ar': 'إلغاء'},
    'offerings': {'en': 'Offerings', 'es': 'Artículos', 'fr': 'Articles', 'de': 'Angebote', 'pt': 'Artigos', 'it': 'Articoli', 'ja': '商品', 'zh': '商品', 'hi': 'पेशकशें', 'ar': 'المعروضات'},
    'seller': {'en': 'Seller', 'es': 'Vendedor', 'fr': 'Vendeur', 'de': 'Verkäufer', 'pt': 'Vendedor', 'it': 'Venditore', 'ja': '販売者', 'zh': '卖家', 'hi': 'विक्रेता', 'ar': 'البائع'},
}


def shop_text(key: str, language: str) -> str:
    row = _SHOP_TEXT[key]
    return row.get(language) or row['en']


def shop_labels(language: str) -> dict[str, str]:
    return {k: (row.get(language) or row['en'])
            for k, row in _SHOP_LABELS.items()}


def money_text(key: str, language: str) -> str:
    row = _MONEY_TEXT[key]
    return row.get(language) or row['en']


def money_labels(language: str) -> dict[str, str]:
    return {k: (row.get(language) or row['en'])
            for k, row in _MONEY_LABELS.items()}


_CIRCLE_TEXT: dict[str, dict[str, str]] = {
    'kept_here': {'en': 'Your circle lives on this deployment alone — invitations, messages and pages never leave it.', 'es': 'Tu círculo vive solo en esta instalación — las invitaciones, los mensajes y las páginas nunca salen de ella.', 'fr': "Votre cercle vit uniquement dans cette installation — les invitations, les messages et les pages n'en sortent jamais.", 'de': 'Dein Kreis lebt allein in dieser Installation — Einladungen, Nachrichten und Seiten verlassen sie nie.', 'pt': 'O seu círculo vive apenas nesta instalação — os convites, as mensagens e as páginas nunca saem dela.', 'it': 'La tua cerchia vive solo in questa installazione — inviti, messaggi e pagine non la lasciano mai.', 'ja': 'あなたのサークルはこの環境の中だけにあります — 招待もメッセージもページも外へ出ることはありません。', 'zh': '你的圈子只存在于这套部署中 — 邀请、消息和主页永远不会离开它。', 'hi': 'आपका दायरा केवल इसी इंस्टॉलेशन में रहता है — निमंत्रण, संदेश और पन्ने इससे बाहर कभी नहीं जाते।', 'ar': 'دائرتك تعيش في هذا التثبيت وحده — الدعوات والرسائل والصفحات لا تغادره أبدًا.'},
}

_CIRCLE_LABELS: dict[str, dict[str, str]] = {
    'title': {'en': 'Your circle', 'es': 'Tu círculo', 'fr': 'Votre cercle', 'de': 'Dein Kreis', 'pt': 'O seu círculo', 'it': 'La tua cerchia', 'ja': 'あなたのサークル', 'zh': '你的圈子', 'hi': 'आपका दायरा', 'ar': 'دائرتك'},
    'contacts': {'en': 'Contacts', 'es': 'Contactos', 'fr': 'Contacts', 'de': 'Kontakte', 'pt': 'Contactos', 'it': 'Contatti', 'ja': '連絡先', 'zh': '联系人', 'hi': 'संपर्क', 'ar': 'جهات الاتصال'},
    'invited_me': {'en': 'Invited you', 'es': 'Te invitaron', 'fr': 'Vous ont invité', 'de': 'Haben dich eingeladen', 'pt': 'Convidaram-no', 'it': 'Ti hanno invitato', 'ja': '招待されています', 'zh': '邀请了你', 'hi': 'आपको आमंत्रित किया', 'ar': 'دعوك'},
    'awaiting': {'en': 'Awaiting reply', 'es': 'Esperando respuesta', 'fr': 'En attente', 'de': 'Wartet auf Antwort', 'pt': 'A aguardar resposta', 'it': 'In attesa', 'ja': '返事待ち', 'zh': '等待回应', 'hi': 'प्रतीक्षा में', 'ar': 'بانتظار الرد'},
    'invite': {'en': 'Invite', 'es': 'Invitar', 'fr': 'Inviter', 'de': 'Einladen', 'pt': 'Convidar', 'it': 'Invita', 'ja': '招待', 'zh': '邀请', 'hi': 'आमंत्रित करें', 'ar': 'دعوة'},
    'leave': {'en': 'Leave', 'es': 'Salir', 'fr': 'Quitter', 'de': 'Verlassen', 'pt': 'Sair', 'it': 'Esci', 'ja': '外れる', 'zh': '退出', 'hi': 'छोड़ें', 'ar': 'مغادرة'},
    'messages': {'en': 'Messages', 'es': 'Mensajes', 'fr': 'Messages', 'de': 'Nachrichten', 'pt': 'Mensagens', 'it': 'Messaggi', 'ja': 'メッセージ', 'zh': '消息', 'hi': 'संदेश', 'ar': 'الرسائل'},
    'to': {'en': 'To', 'es': 'Para', 'fr': 'À', 'de': 'An', 'pt': 'Para', 'it': 'A', 'ja': '宛先', 'zh': '发给', 'hi': 'किसे', 'ar': 'إلى'},
    'send': {'en': 'Send', 'es': 'Enviar', 'fr': 'Envoyer', 'de': 'Senden', 'pt': 'Enviar', 'it': 'Invia', 'ja': '送信', 'zh': '发送', 'hi': 'भेजें', 'ar': 'إرسال'},
    'open': {'en': 'Open', 'es': 'Abrir', 'fr': 'Ouvrir', 'de': 'Öffnen', 'pt': 'Abrir', 'it': 'Apri', 'ja': '開く', 'zh': '打开', 'hi': 'खोलें', 'ar': 'فتح'},
    'page': {'en': 'Your page', 'es': 'Tu página', 'fr': 'Votre page', 'de': 'Deine Seite', 'pt': 'A sua página', 'it': 'La tua pagina', 'ja': 'あなたのページ', 'zh': '你的主页', 'hi': 'आपका पन्ना', 'ar': 'صفحتك'},
    'headline': {'en': 'Headline', 'es': 'Titular', 'fr': 'Accroche', 'de': 'Überschrift', 'pt': 'Título', 'it': 'Titolo', 'ja': '見出し', 'zh': '标题', 'hi': 'शीर्षक', 'ar': 'العنوان'},
    'about': {'en': 'About you', 'es': 'Sobre ti', 'fr': 'À propos de vous', 'de': 'Über dich', 'pt': 'Sobre si', 'it': 'Su di te', 'ja': '自己紹介', 'zh': '关于你', 'hi': 'आपके बारे में', 'ar': 'نبذة عنك'},
    'background': {'en': 'Background', 'es': 'Fondo', 'fr': 'Fond', 'de': 'Hintergrund', 'pt': 'Fundo', 'it': 'Sfondo', 'ja': '背景', 'zh': '背景', 'hi': 'पृष्ठभूमि', 'ar': 'الخلفية'},
    'accent': {'en': 'Accent', 'es': 'Acento', 'fr': 'Accent', 'de': 'Akzent', 'pt': 'Realce', 'it': 'Accento', 'ja': 'アクセント', 'zh': '强调色', 'hi': 'उभार रंग', 'ar': 'اللون المميز'},
    'links': {'en': 'Links', 'es': 'Enlaces', 'fr': 'Liens', 'de': 'Links', 'pt': 'Ligações', 'it': 'Collegamenti', 'ja': 'リンク', 'zh': '链接', 'hi': 'लिंक', 'ar': 'الروابط'},
    'top': {'en': 'Top friends', 'es': 'Mejores amigos', 'fr': 'Meilleurs amis', 'de': 'Beste Freunde', 'pt': 'Melhores amigos', 'it': 'Migliori amici', 'ja': 'トップフレンド', 'zh': '挚友', 'hi': 'खास दोस्त', 'ar': 'أفضل الأصدقاء'},
    'save': {'en': 'Save', 'es': 'Guardar', 'fr': 'Enregistrer', 'de': 'Speichern', 'pt': 'Guardar', 'it': 'Salva', 'ja': '保存', 'zh': '保存', 'hi': 'सहेजें', 'ar': 'حفظ'},
    'visit': {'en': 'Look at a page', 'es': 'Ver una página', 'fr': 'Voir une page', 'de': 'Eine Seite ansehen', 'pt': 'Ver uma página', 'it': 'Guarda una pagina', 'ja': 'ページを見る', 'zh': '看看别人的主页', 'hi': 'कोई पन्ना देखें', 'ar': 'عرض صفحة'},
    'visit_id': {'en': 'Their id', 'es': 'Su id', 'fr': 'Leur id', 'de': 'Deren ID', 'pt': 'O id deles', 'it': 'Il loro id', 'ja': '相手のID', 'zh': '对方的ID', 'hi': 'उनकी ID', 'ar': 'معرّفهم'},
    'switches': {'en': 'Your switches', 'es': 'Tus interruptores', 'fr': 'Vos interrupteurs', 'de': 'Deine Schalter', 'pt': 'Os seus interruptores', 'it': 'I tuoi interruttori', 'ja': 'スイッチ', 'zh': '你的开关', 'hi': 'आपके स्विच', 'ar': 'مفاتيحك'},
    'sw_messaging': {'en': 'Messaging', 'es': 'Mensajería', 'fr': 'Messagerie', 'de': 'Nachrichten', 'pt': 'Mensagens', 'it': 'Messaggistica', 'ja': 'メッセージ機能', 'zh': '消息功能', 'hi': 'संदेश सुविधा', 'ar': 'المراسلة'},
    'sw_homepage': {'en': 'Homepage', 'es': 'Página personal', 'fr': 'Page personnelle', 'de': 'Eigene Seite', 'pt': 'Página pessoal', 'it': 'Pagina personale', 'ja': 'ホームページ', 'zh': '个人主页', 'hi': 'निजी पन्ना', 'ar': 'الصفحة الشخصية'},
}


def circle_text(key: str, language: str) -> str:
    row = _CIRCLE_TEXT[key]
    return row.get(language) or row['en']


def circle_labels(language: str) -> dict[str, str]:
    return {k: (row.get(language) or row['en'])
            for k, row in _CIRCLE_LABELS.items()}

#: The fixed sentences the phone line speaks on its own — the re-prompt
#: after no key was pressed, the opt-out acknowledgement, the no-choice
#: closing, the silence prompt, the closing, and the trouble line when JIM
#: cannot be reached mid-call. Everything else the line says comes from JIM
#: turn by turn; these are what the voice sidecar may say without asking.
_SPOKEN_LINES: dict[str, dict[str, str]] = {
    "unknown_caller": {
        "en": "This is a guardian line that cannot take calls. If this is an emergency, please call your local emergency number. Goodbye.",
        "es": "Esta es una línea de guardián que no puede atender llamadas. Si se trata de una emergencia, llama al número de emergencias de tu zona. Adiós.",
        "fr": "Ceci est une ligne de gardien qui ne peut pas prendre d'appels. En cas d'urgence, appelez le numéro d'urgence de votre région. Au revoir.",
        "de": "Dies ist eine Wächterleitung, die keine Anrufe entgegennehmen kann. Im Notfall rufen Sie bitte Ihre örtliche Notrufnummer an. Auf Wiederhören.",
        "pt": "Esta é uma linha de guardião que não pode atender chamadas. Se for uma emergência, ligue para o número de emergência da sua região. Adeus.",
        "it": "Questa è una linea di custode che non può ricevere chiamate. In caso di emergenza, chiama il numero di emergenza della tua zona. Arrivederci.",
        "ja": "こちらは見守り用の回線で、通話をお受けできません。緊急の場合は、お住まいの地域の緊急番号におかけください。失礼します。",
        "zh": "这是一条守护专线，无法接听来电。如遇紧急情况，请拨打当地的紧急电话。再见。",
        "hi": "यह एक संरक्षक लाइन है जो कॉल नहीं ले सकती। यदि यह आपातकाल है, तो कृपया अपने स्थानीय आपातकालीन नंबर पर कॉल करें। अलविदा।",
        "ar": "هذا خط حارس لا يمكنه تلقي المكالمات. إذا كانت هذه حالة طارئة، فيرجى الاتصال برقم الطوارئ المحلي. مع السلامة.",
    },
    "repeat": {
        "en": "I did not catch a key. Press 1 to hear the message, or 2 to not be called this way again.",
        "es": "No detecté ninguna tecla. Pulsa 1 para escuchar el mensaje, o 2 para que no te llamen así de nuevo.",
        "fr": "Je n'ai pas détecté de touche. Appuyez sur 1 pour entendre le message, ou sur 2 pour ne plus être appelé ainsi.",
        "de": "Ich habe keine Taste erkannt. Drücken Sie 1, um die Nachricht zu hören, oder 2, um so nicht mehr angerufen zu werden.",
        "pt": "Não detetei nenhuma tecla. Prima 1 para ouvir a mensagem, ou 2 para não voltar a ser contactado assim.",
        "it": "Non ho rilevato alcun tasto. Premi 1 per ascoltare il messaggio, o 2 per non essere più chiamato così.",
        "ja": "キーが押されませんでした。メッセージを聞くには1を、この方法で二度と電話を受けない場合は2を押してください。",
        "zh": "没有检测到按键。按1收听消息，按2则不再以此方式接到来电。",
        "hi": "कोई कुंजी नहीं मिली। संदेश सुनने के लिए 1 दबाएँ, या इस तरह दोबारा कॉल न पाने के लिए 2 दबाएँ।",
        "ar": "لم ألتقط أي ضغطة. اضغط 1 لسماع الرسالة، أو 2 لعدم الاتصال بك بهذه الطريقة مجددًا.",
    },
    "declined": {
        "en": "Understood. This number will not be called this way again. Goodbye.",
        "es": "Entendido. No se volverá a llamar a este número de esta forma. Adiós.",
        "fr": "Compris. Ce numéro ne sera plus appelé de cette façon. Au revoir.",
        "de": "Verstanden. Diese Nummer wird so nicht mehr angerufen. Auf Wiederhören.",
        "pt": "Entendido. Este número não voltará a ser contactado desta forma. Adeus.",
        "it": "Capito. Questo numero non sarà più chiamato in questo modo. Arrivederci.",
        "ja": "承知しました。この番号にこの方法で再び電話することはありません。失礼します。",
        "zh": "明白了。不会再以此方式拨打此号码。再见。",
        "hi": "समझ गया। इस नंबर पर इस तरह दोबारा कॉल नहीं की जाएगी। अलविदा।",
        "ar": "مفهوم. لن يُتصل بهذا الرقم بهذه الطريقة مجددًا. وداعًا.",
    },
    "no_choice": {
        "en": "No choice was made, so I will try the next person. Goodbye.",
        "es": "No se eligió nada, así que probaré con la siguiente persona. Adiós.",
        "fr": "Aucun choix n'a été fait, je vais donc essayer la personne suivante. Au revoir.",
        "de": "Es wurde keine Wahl getroffen, daher versuche ich es bei der nächsten Person. Auf Wiederhören.",
        "pt": "Não foi feita nenhuma escolha, por isso vou tentar a próxima pessoa. Adeus.",
        "it": "Nessuna scelta è stata fatta, quindi proverò con la persona successiva. Arrivederci.",
        "ja": "選択がなかったので、次の方に連絡します。失礼します。",
        "zh": "未作选择，我将联系下一位。再见。",
        "hi": "कोई चुनाव नहीं हुआ, इसलिए मैं अगले व्यक्ति से संपर्क करूँगा। अलविदा।",
        "ar": "لم يُتخذ أي خيار، لذا سأجرّب الشخص التالي. وداعًا.",
    },
    "silence": {
        "en": "I did not hear anything. Is there anything you would like to ask?",
        "es": "No escuché nada. ¿Hay algo que quieras preguntar?",
        "fr": "Je n'ai rien entendu. Y a-t-il quelque chose que vous voulez demander ?",
        "de": "Ich habe nichts gehört. Möchten Sie etwas fragen?",
        "pt": "Não ouvi nada. Há alguma coisa que queira perguntar?",
        "it": "Non ho sentito nulla. C'è qualcosa che vorresti chiedere?",
        "ja": "何も聞こえませんでした。何か質問はありますか？",
        "zh": "我没有听到任何内容。你有什么想问的吗？",
        "hi": "मुझे कुछ सुनाई नहीं दिया। क्या आप कुछ पूछना चाहेंगे?",
        "ar": "لم أسمع شيئًا. هل هناك ما تودّ سؤاله؟",
    },
    "closing": {
        "en": "Thank you for listening. Please check on them. Goodbye.",
        "es": "Gracias por escuchar. Por favor, ve a ver cómo está. Adiós.",
        "fr": "Merci de m'avoir écouté. Veuillez aller voir comment il va. Au revoir.",
        "de": "Danke fürs Zuhören. Bitte sehen Sie nach der Person. Auf Wiederhören.",
        "pt": "Obrigado por ouvir. Por favor, vá ver como está. Adeus.",
        "it": "Grazie per l'ascolto. Per favore, vai a controllare come sta. Arrivederci.",
        "ja": "お聞きいただきありがとうございます。様子を見に行ってください。失礼します。",
        "zh": "感谢您的倾听。请去看看他们。再见。",
        "hi": "सुनने के लिए धन्यवाद। कृपया उनका हाल देखें। अलविदा।",
        "ar": "شكرًا لإصغائك. من فضلك اطمئنّ عليهم. وداعًا.",
    },
    "trouble": {
        "en": "I am having trouble continuing this call. Please check on them and call your local emergency number if you believe this is an emergency. Goodbye.",
        "es": "Tengo problemas para continuar esta llamada. Por favor, ve a ver cómo está y llama a tu número de emergencias local si crees que es una emergencia. Adiós.",
        "fr": "J'ai du mal à poursuivre cet appel. Veuillez aller voir comment il va et appeler votre numéro d'urgence local si vous pensez qu'il s'agit d'une urgence. Au revoir.",
        "de": "Ich kann diesen Anruf nicht fortsetzen. Bitte sehen Sie nach der Person und rufen Sie Ihre örtliche Notrufnummer an, wenn Sie glauben, dass es ein Notfall ist. Auf Wiederhören.",
        "pt": "Estou com dificuldade em continuar esta chamada. Por favor, vá ver como está e ligue para o seu número de emergência local se acha que é uma emergência. Adeus.",
        "it": "Ho difficoltà a continuare questa chiamata. Per favore, vai a controllare come sta e chiama il tuo numero di emergenza locale se pensi sia un'emergenza. Arrivederci.",
        "ja": "この通話を続けることができません。様子を見に行き、緊急だと思われる場合はお住まいの地域の緊急番号に電話してください。失礼します。",
        "zh": "我无法继续这通电话。请去看看他们，如果您认为这是紧急情况，请拨打当地的紧急电话。再见。",
        "hi": "मैं यह कॉल जारी रखने में असमर्थ हूँ। कृपया उनका हाल देखें और यदि आपको लगे कि यह आपातकाल है तो अपने स्थानीय आपातकालीन नंबर पर कॉल करें। अलविदा।",
        "ar": "أواجه صعوبة في متابعة هذه المكالمة. من فضلك اطمئنّ عليهم واتصل برقم الطوارئ المحلي إن كنت تعتقد أنها حالة طارئة. وداعًا.",
    },
}
