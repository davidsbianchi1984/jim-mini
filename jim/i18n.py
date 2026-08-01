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
    'The people watching over this person have been alerted. If this is an emergency, call your local emergency number — this page cannot.': {
        'es': 'Se ha avisado a las personas que velan por ella. Si esto es una emergencia, llame usted al número de emergencias local: esta página no puede.',
        'fr': "Les personnes qui veillent sur elle ont été prévenues. En cas d'urgence, appelez vous-même le numéro d'urgence local — cette page ne le peut pas.",
        'de': 'Die Menschen, die über sie wachen, wurden benachrichtigt. Wenn dies ein Notfall ist, rufen Sie selbst den örtlichen Notruf — diese Seite kann es nicht.',
        'pt': 'As pessoas que velam por ela foram avisadas. Se isto for uma emergência, ligue você para o número de emergência local — esta página não pode.',
        'it': "Le persone che vegliano su di lei sono state avvisate. Se questa è un'emergenza, chiama tu il numero di emergenza locale — questa pagina non può.",
        'ja': 'この人を見守っている人たちに知らせが届きました。緊急の場合は、あなたご自身で地域の緊急通報番号にかけてください。このページにはできません。',
        'zh': '照看这个人的人已收到通知。如果情况紧急，请你自己拨打当地急救电话 — 本页面无法代劳。',
        'hi': 'इस व्यक्ति का ध्यान रखने वालों को सूचित कर दिया गया है। यदि यह आपात स्थिति है तो आप स्वयं अपने स्थानीय आपातकालीन नंबर पर कॉल करें — यह पृष्ठ ऐसा नहीं कर सकता।',
        'ar': 'أُبلغ من يرعون هذا الشخص. إن كانت هذه حالة طارئة فاتصل أنت برقم الطوارئ المحلي — هذه الصفحة لا تستطيع.',
    },
    "This person's guardian has been alerted. If this is an emergency, call your local emergency number.": {
        'es': 'Se ha avisado a su tutor. Si esto es una emergencia, llame al número de emergencias local.',
        'fr': "Son responsable légal a été prévenu. En cas d'urgence, appelez le numéro d'urgence local.",
        'de': 'Die Erziehungsberechtigten wurden benachrichtigt. Wenn dies ein Notfall ist, rufen Sie den örtlichen Notruf.',
        'pt': 'O responsável desta pessoa foi avisado. Se isto for uma emergência, ligue para o número de emergência local.',
        'it': "Il tutore di questa persona è stato avvisato. Se questa è un'emergenza, chiama il numero di emergenza locale.",
        'ja': '保護者に知らせが届きました。緊急の場合は、地域の緊急通報番号にかけてください。',
        'zh': '该人的监护人已收到通知。如果情况紧急，请拨打当地急救电话。',
        'hi': 'इस व्यक्ति के अभिभावक को सूचित कर दिया गया है। यदि यह आपात स्थिति है तो स्थानीय आपातकालीन नंबर पर कॉल करें।',
        'ar': 'أُبلغ وليّ أمر هذا الشخص. إن كانت هذه حالة طارئة فاتصل برقم الطوارئ المحلي.',
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
