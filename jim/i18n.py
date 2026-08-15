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
        raise ValueError(f"unknown language {language!r}")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
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
        raise ValueError(f"unknown language {target!r}")
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
        cue = pace.get("cue")
        if cue:
            pace["cue"] = {k: tr(v, language) for k, v in cue.items()}
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

#: Derived from the table below rather than repeated.
TEMPLATES = (MUST_BE_ONE_OF, PLAN_GATE)

_TEMPLATES: dict[str, dict[str, str]] = {
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
    if isinstance(detail, dict) and isinstance(detail.get("detail"), str):
        return {**detail, "detail": tr_refusal(detail["detail"], language)}
    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
        return {**detail, "message": tr_refusal(detail["message"], language)}
    # One level further in. `api.py` wraps every `HTTPException` as
    # `{"detail": exc.detail}` before this runs, so a structured refusal — the
    # plan gate — arrives as a dict inside a dict, and the branches above see
    # an outer dict whose `detail` is neither a string nor carrying a
    # `message`. Its sentence went out untranslated in every language.
    #
    #     asked     is a structured refusal localized
    #     mattered  is it localized where the wrapper actually puts it
    if isinstance(detail, dict) and isinstance(detail.get("detail"), dict):
        return {**detail,
                "detail": localize_detail(detail["detail"], language)}
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
    'tone': {'en': 'Tone', 'es': 'Tono', 'fr': 'Ton', 'de': 'Ton', 'pt': 'Tom', 'it': 'Tono', 'ja': 'トーン', 'zh': '语气', 'hi': 'लहजा', 'ar': 'النبرة'},
    'trusted_channel': {'en': 'Trusted channel', 'es': 'Canal de confianza', 'fr': 'Canal de confiance', 'de': 'Vertrauenskanal', 'pt': 'Canal de confiança', 'it': 'Canale di fiducia', 'ja': '信頼できる連絡先', 'zh': '可信渠道', 'hi': 'विश्वसनीय चैनल', 'ar': 'القناة الموثوقة'},
    'trusted_name': {'en': 'Trusted name', 'es': 'Nombre de confianza', 'fr': 'Nom de confiance', 'de': 'Vertrauensperson', 'pt': 'Nome de confiança', 'it': 'Nome di fiducia', 'ja': '信頼できる人の名前', 'zh': '可信联系人姓名', 'hi': 'विश्वसनीय नाम', 'ar': 'الاسم الموثوق'},
    'username': {'en': 'Username', 'es': 'Nombre de usuario', 'fr': 'Nom d’utilisateur', 'de': 'Benutzername', 'pt': 'Nome de utilizador', 'it': 'Nome utente', 'ja': 'ユーザー名', 'zh': '用户名', 'hi': 'उपयोगकर्ता नाम', 'ar': 'اسم المستخدم'},
    'window_minutes': {'en': 'Window (minutes)', 'es': 'Ventana (minutos)', 'fr': 'Fenêtre (minutes)', 'de': 'Zeitfenster (Minuten)', 'pt': 'Janela (minutos)', 'it': 'Finestra (minuti)', 'ja': 'ウィンドウ（分）', 'zh': '时间窗（分钟）', 'hi': 'विंडो (मिनट)', 'ar': 'النافذة (بالدقائق)'},    'voice_id': {'en': 'Voice', 'es': 'Voz', 'fr': 'Voix', 'de': 'Stimme', 'pt': 'Voz', 'it': 'Voce', 'ja': '音声', 'zh': '语音', 'hi': 'आवाज़', 'ar': 'الصوت'},

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
    'what': {'en': 'What', 'es': 'Qué', 'fr': 'Quoi', 'de': 'Was', 'pt': 'O quê', 'it': 'Cosa', 'ja': '内容', 'zh': '事项', 'hi': 'क्या', 'ar': 'ماذا'},
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
