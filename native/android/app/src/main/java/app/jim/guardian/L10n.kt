package app.jim.guardian

/**
 * App-chrome localization: tab names and the most common actions, in every
 * language the backend supports. Guidance, coaching, and safety content are
 * localized server-side by the user's language setting; this table covers
 * the frame around them. Missing keys fall back to English.
 */
object L10n {
    fun t(key: String, lang: String): String =
        table[key]?.let { it[lang] ?: it["en"] } ?: key

    private val table: Map<String, Map<String, String>> = mapOf(
        "offline.title" to mapOf("en" to "What this deployment can reach", "es" to "Qué puede alcanzar esta instalación", "fr" to "Ce que ce déploiement peut atteindre", "de" to "Was diese Installation erreichen kann", "pt" to "O que esta instalação pode alcançar", "it" to "Cosa può raggiungere questa installazione", "ja" to "この環境が接続できる範囲", "zh" to "此部署可以连接到什么", "hi" to "यह परिनियोजन किस तक पहुँच सकता है", "ar" to "ما يمكن أن يصل إليه هذا النشر"),
        "offline.on" to mapOf("en" to "Offline — nothing leaves this machine", "es" to "Sin conexión — nada sale de esta máquina", "fr" to "Hors ligne — rien ne quitte cette machine", "de" to "Offline — nichts verlässt diesen Rechner", "pt" to "Offline — nada sai desta máquina", "it" to "Offline — nulla esce da questa macchina", "ja" to "オフライン — このマシンから何も出ません", "zh" to "离线 — 任何内容都不会离开这台机器", "hi" to "ऑफ़लाइन — इस मशीन से कुछ भी बाहर नहीं जाता", "ar" to "دون اتصال — لا شيء يغادر هذا الجهاز"),
        "offline.off" to mapOf("en" to "Online — this deployment can reach other machines", "es" to "En línea — esta instalación puede alcanzar otras máquinas", "fr" to "En ligne — ce déploiement peut atteindre d’autres machines", "de" to "Online — diese Installation kann andere Rechner erreichen", "pt" to "Online — esta instalação pode alcançar outras máquinas", "it" to "Online — questa installazione può raggiungere altre macchine", "ja" to "オンライン — この環境は他のマシンに接続できます", "zh" to "在线 — 此部署可以连接其他机器", "hi" to "ऑनलाइन — यह परिनियोजन अन्य मशीनों तक पहुँच सकता है", "ar" to "متصل — يمكن لهذا النشر الوصول إلى أجهزة أخرى"),
        "tab.overview" to mapOf(
            "en" to "Overview", "es" to "Resumen", "fr" to "Aperçu",
            "de" to "Übersicht", "pt" to "Visão geral", "it" to "Panoramica",
            "ja" to "概要", "zh" to "概览", "hi" to "अवलोकन", "ar" to "نظرة عامة"),
        "self.profile_id" to mapOf("en" to "prf_…", "es" to "prf_…", "fr" to "prf_…", "de" to "prf_…", "pt" to "prf_…", "it" to "prf_…", "ja" to "prf_…", "zh" to "prf_…", "hi" to "prf_…", "ar" to "prf_…"),
        "self.title" to mapOf("en" to "Your own profile", "es" to "Tu propio perfil", "fr" to "Votre propre profil", "de" to "Ihr eigenes Profil", "pt" to "O seu próprio perfil", "it" to "Il tuo profilo", "ja" to "あなた自身のプロフィール", "zh" to "你自己的档案", "hi" to "आपकी अपनी प्रोफ़ाइल", "ar" to "ملفك الشخصي"),
        "self.lead" to mapOf("en" to "The QRME profile that speaks as you. The Guardian tells it nothing until you say which parts it may pass on, and you can see exactly what would go before any of it does.", "es" to "El perfil de QRME que habla como tú. El Guardián no le cuenta nada hasta que digas qué partes puede transmitir, y puedes ver exactamente qué se enviaría antes de que se envíe.", "fr" to "Le profil QRME qui parle en votre nom. Le Gardien ne lui dit rien tant que vous n’avez pas indiqué ce qu’il peut transmettre, et vous voyez exactement ce qui partirait avant que quoi que ce soit parte.", "de" to "Das QRME-Profil, das als Sie spricht. Der Guardian sagt ihm nichts, bis Sie festlegen, was er weitergeben darf, und Sie sehen genau, was ginge, bevor irgendetwas geht.", "pt" to "O perfil QRME que fala como você. O Guardião não lhe conta nada até dizer que partes pode transmitir, e vê exatamente o que iria antes de qualquer coisa ir.", "it" to "Il profilo QRME che parla come te. Il Guardian non gli dice nulla finché non indichi cosa può trasmettere, e vedi esattamente cosa partirebbe prima che parta.", "ja" to "あなたとして話す QRME のプロフィールです。どの部分を伝えてよいか決めるまで、ガーディアンは何も伝えません。送られる内容は送信前にそのまま確認できます。", "zh" to "以你的身份说话的 QRME 档案。在你指明可以转达哪些部分之前，守护者不会告诉它任何事，而且发送前你能看到确切会送出什么。", "hi" to "वह QRME प्रोफ़ाइल जो आपके रूप में बोलती है। जब तक आप यह न बताएँ कि कौन-से हिस्से भेजे जा सकते हैं, गार्जियन उसे कुछ नहीं बताता, और भेजे जाने से पहले आप ठीक-ठीक देख सकते हैं कि क्या जाएगा।", "ar" to "ملف QRME الذي يتحدث بصفتك. لا يخبره الحارس بشيء حتى تحدد ما يمكن نقله، ويمكنك أن ترى بالضبط ما سيُرسل قبل أن يُرسل أي شيء."),
        "self.link" to mapOf("en" to "Link it", "es" to "Vincúlalo", "fr" to "Le relier", "de" to "Verknüpfen", "pt" to "Ligar", "it" to "Collegalo", "ja" to "リンクする", "zh" to "关联它", "hi" to "इसे जोड़ें", "ar" to "اربطه"),
        "self.paste" to mapOf("en" to "Paste the profile's id and your owner token from QRME. It has to be a profile QRME calls your own — a made-up one will be refused.", "es" to "Pega el id del perfil y tu token de propietario de QRME. Tiene que ser un perfil que QRME considere tuyo; uno inventado será rechazado.", "fr" to "Collez l’identifiant du profil et votre jeton de propriétaire QRME. Ce doit être un profil que QRME reconnaît comme le vôtre ; un profil inventé sera refusé.", "de" to "Fügen Sie die Profil-ID und Ihr Eigentümer-Token aus QRME ein. Es muss ein Profil sein, das QRME als Ihr eigenes führt — ein erfundenes wird abgelehnt.", "pt" to "Cole o id do perfil e o seu token de proprietário do QRME. Tem de ser um perfil que o QRME considere seu — um inventado será recusado.", "it" to "Incolla l’id del profilo e il tuo token di proprietario da QRME. Deve essere un profilo che QRME riconosce come tuo — uno inventato verrà rifiutato.", "ja" to "QRME のプロフィール ID と所有者トークンを貼り付けてください。QRME があなた自身のものと認めるプロフィールに限られ、架空のものは拒否されます。", "zh" to "粘贴档案 id 和你在 QRME 的所有者令牌。必须是 QRME 认定属于你自己的档案 — 编造的会被拒绝。", "hi" to "QRME से प्रोफ़ाइल का id और अपना स्वामी टोकन चिपकाएँ। यह ऐसी प्रोफ़ाइल होनी चाहिए जिसे QRME आपकी अपनी मानता हो — बनावटी को अस्वीकार कर दिया जाएगा।", "ar" to "الصق معرِّف الملف ورمز المالك الخاص بك من QRME. يجب أن يكون ملفًا يعتبره QRME ملكك — وسيُرفض أي ملف مُختلق."),
        "self.owner_token" to mapOf("en" to "owner token", "es" to "token de propietario", "fr" to "jeton de propriétaire", "de" to "Eigentümer-Token", "pt" to "token de proprietário", "it" to "token di proprietario", "ja" to "所有者トークン", "zh" to "所有者令牌", "hi" to "स्वामी टोकन", "ar" to "رمز المالك"),
        "self.link_button" to mapOf("en" to "Link this profile", "es" to "Vincular este perfil", "fr" to "Relier ce profil", "de" to "Dieses Profil verknüpfen", "pt" to "Ligar este perfil", "it" to "Collega questo profilo", "ja" to "このプロフィールをリンク", "zh" to "关联此档案", "hi" to "इस प्रोफ़ाइल को जोड़ें", "ar" to "اربط هذا الملف"),
        "self.may_know" to mapOf("en" to "What it may know", "es" to "Qué puede saber", "fr" to "Ce qu’il peut savoir", "de" to "Was es wissen darf", "pt" to "O que pode saber", "it" to "Cosa può sapere", "ja" to "伝えてよいこと", "zh" to "它可以知道什么", "hi" to "यह क्या जान सकता है", "ar" to "ما يمكن أن يعرفه"),
        "self.until_tick" to mapOf("en" to "Nothing is passed on until you tick it.", "es" to "No se transmite nada hasta que lo marques.", "fr" to "Rien n’est transmis tant que vous ne l’avez pas coché.", "de" to "Nichts wird weitergegeben, bis Sie es ankreuzen.", "pt" to "Nada é transmitido até o marcar.", "it" to "Non viene trasmesso nulla finché non lo spunti.", "ja" to "チェックするまで何も伝えられません。", "zh" to "在你勾选之前，不会转达任何内容。", "hi" to "जब तक आप चुनें नहीं, कुछ भी नहीं भेजा जाता।", "ar" to "لا يُنقل شيء حتى تحدده."),
        "self.exactly" to mapOf("en" to "Exactly what would be sent", "es" to "Exactamente lo que se enviaría", "fr" to "Exactement ce qui serait envoyé", "de" to "Genau das, was gesendet würde", "pt" to "Exatamente o que seria enviado", "it" to "Esattamente ciò che verrebbe inviato", "ja" to "送られる内容そのもの", "zh" to "确切会发送的内容", "hi" to "ठीक वही जो भेजा जाएगा", "ar" to "ما سيُرسل بالضبط"),
        "self.nothing_ticked" to mapOf("en" to "Nothing, because nothing is ticked.", "es" to "Nada, porque no hay nada marcado.", "fr" to "Rien, parce que rien n’est coché.", "de" to "Nichts, weil nichts angekreuzt ist.", "pt" to "Nada, porque nada está marcado.", "it" to "Niente, perché non è spuntato nulla.", "ja" to "何もチェックされていないため、何もありません。", "zh" to "没有内容，因为没有勾选任何项。", "hi" to "कुछ नहीं, क्योंकि कुछ चुना नहीं गया है।", "ar" to "لا شيء، لأنه لم يتم تحديد أي شيء."),
        "self.message_itself" to mapOf("en" to "This is the message itself, not a description of it. Medication is the one part made of your own words, so it shows the names as you typed them.", "es" to "Este es el mensaje en sí, no una descripción. La medicación es la única parte hecha con tus propias palabras, así que muestra los nombres tal como los escribiste.", "fr" to "Ceci est le message lui-même, pas sa description. Les médicaments sont la seule partie faite de vos propres mots : les noms s’affichent tels que vous les avez saisis.", "de" to "Dies ist die Nachricht selbst, keine Beschreibung. Die Medikation ist der einzige Teil aus Ihren eigenen Worten, daher erscheinen die Namen so, wie Sie sie eingegeben haben.", "pt" to "Esta é a mensagem em si, não uma descrição. A medicação é a única parte feita das suas próprias palavras, por isso mostra os nomes tal como os escreveu.", "it" to "Questo è il messaggio stesso, non una sua descrizione. I farmaci sono l’unica parte fatta di parole tue, quindi i nomi appaiono come li hai scritti.", "ja" to "これは説明ではなく、メッセージそのものです。薬だけはご自身の言葉でできているため、入力したとおりの名称が表示されます。", "zh" to "这就是消息本身，而不是对它的描述。用药是唯一由你自己的措辞构成的部分，因此名称按你输入的原样显示。", "hi" to "यह संदेश स्वयं है, उसका विवरण नहीं। दवा ही एकमात्र हिस्सा है जो आपके अपने शब्दों से बना है, इसलिए नाम वैसे ही दिखते हैं जैसे आपने लिखे।", "ar" to "هذه هي الرسالة نفسها، لا وصفٌ لها. الدواء هو الجزء الوحيد المكوَّن من كلماتك، لذا تظهر الأسماء كما كتبتها."),
        "self.send" to mapOf("en" to "Send this to my profile", "es" to "Enviar esto a mi perfil", "fr" to "Envoyer ceci à mon profil", "de" to "Dies an mein Profil senden", "pt" to "Enviar isto ao meu perfil", "it" to "Invia questo al mio profilo", "ja" to "これを自分のプロフィールに送る", "zh" to "把这个发送到我的档案", "hi" to "इसे मेरी प्रोफ़ाइल को भेजें", "ar" to "أرسل هذا إلى ملفي"),
        "self.stop" to mapOf("en" to "Stop", "es" to "Detener", "fr" to "Arrêter", "de" to "Beenden", "pt" to "Parar", "it" to "Ferma", "ja" to "やめる", "zh" to "停止", "hi" to "रोकें", "ar" to "إيقاف"),
        "self.unlink_note" to mapOf("en" to "Unlinking removes the token and everything you ticked. What the profile was already told stays in its own source list, in QRME, where you can delete it.", "es" to "Desvincular elimina el token y todo lo que marcaste. Lo que ya se le dijo al perfil permanece en su propia lista de fuentes, en QRME, donde puedes borrarlo.", "fr" to "Le fait de délier supprime le jeton et tout ce que vous aviez coché. Ce qui a déjà été dit au profil reste dans sa liste de sources, dans QRME, où vous pouvez le supprimer.", "de" to "Das Trennen entfernt das Token und alles, was Sie angekreuzt hatten. Was dem Profil bereits mitgeteilt wurde, bleibt in dessen Quellenliste in QRME, wo Sie es löschen können.", "pt" to "Desligar remove o token e tudo o que marcou. O que já foi dito ao perfil fica na sua própria lista de fontes, no QRME, onde o pode apagar.", "it" to "Scollegare rimuove il token e tutto ciò che avevi spuntato. Quanto già detto al profilo resta nel suo elenco di fonti, in QRME, dove puoi eliminarlo.", "ja" to "リンクを解除するとトークンとチェックした内容がすべて削除されます。すでにプロフィールに伝えた内容は QRME のソース一覧に残り、そこで削除できます。", "zh" to "取消关联会移除令牌和你勾选的全部内容。已经告诉档案的内容仍留在 QRME 的来源列表中，你可以在那里删除。", "hi" to "अनलिंक करने से टोकन और आपके चुने हुए सब कुछ हट जाता है। प्रोफ़ाइल को पहले जो बताया जा चुका है वह QRME की उसकी स्रोत सूची में रहता है, जहाँ आप उसे मिटा सकते हैं।", "ar" to "يؤدي إلغاء الربط إلى إزالة الرمز وكل ما حددته. ويبقى ما قيل للملف سابقًا في قائمة مصادره داخل QRME، حيث يمكنك حذفه."),
        "self.unlink" to mapOf("en" to "Unlink", "es" to "Desvincular", "fr" to "Délier", "de" to "Trennen", "pt" to "Desligar", "it" to "Scollega", "ja" to "リンク解除", "zh" to "取消关联", "hi" to "अनलिंक करें", "ar" to "إلغاء الربط"),
        "self.linked_note" to mapOf("en" to "Linked. Nothing is shared yet.", "es" to "Vinculado. Todavía no se comparte nada.", "fr" to "Relié. Rien n’est encore partagé.", "de" to "Verknüpft. Es wird noch nichts geteilt.", "pt" to "Ligado. Ainda não é partilhado nada.", "it" to "Collegato. Non è ancora condiviso nulla.", "ja" to "リンクしました。まだ何も共有されていません。", "zh" to "已关联。尚未共享任何内容。", "hi" to "जुड़ गया। अभी कुछ भी साझा नहीं किया गया।", "ar" to "تم الربط. لم تتم مشاركة أي شيء بعد."),
        "self.saved" to mapOf("en" to "Saved.", "es" to "Guardado.", "fr" to "Enregistré.", "de" to "Gespeichert.", "pt" to "Guardado.", "it" to "Salvato.", "ja" to "保存しました。", "zh" to "已保存。", "hi" to "सहेजा गया।", "ar" to "تم الحفظ."),
        "self.sent" to mapOf("en" to "Sent.", "es" to "Enviado.", "fr" to "Envoyé.", "de" to "Gesendet.", "pt" to "Enviado.", "it" to "Inviato.", "ja" to "送信しました。", "zh" to "已发送。", "hi" to "भेज दिया गया।", "ar" to "تم الإرسال."),
        "self.unlinked" to mapOf("en" to "Unlinked.", "es" to "Desvinculado.", "fr" to "Délié.", "de" to "Getrennt.", "pt" to "Desligado.", "it" to "Scollegato.", "ja" to "リンクを解除しました。", "zh" to "已取消关联。", "hi" to "अनलिंक कर दिया गया।", "ar" to "تم إلغاء الربط."),
        "tab.care" to mapOf(
            "en" to "Care", "es" to "Cuidado", "fr" to "Soins",
            "de" to "Fürsorge", "pt" to "Cuidado", "it" to "Cura",
            "ja" to "ケア", "zh" to "关怀", "hi" to "देखभाल", "ar" to "رعاية"),
        "tab.life" to mapOf(
            "en" to "Life", "es" to "Vida", "fr" to "Vie",
            "de" to "Leben", "pt" to "Vida", "it" to "Vita",
            "ja" to "ライフ", "zh" to "生活", "hi" to "जीवन", "ar" to "الحياة"),
        "tab.safety" to mapOf(
            "en" to "Safety", "es" to "Seguridad", "fr" to "Sécurité",
            "de" to "Sicherheit", "pt" to "Segurança", "it" to "Sicurezza",
            "ja" to "安全", "zh" to "安全", "hi" to "सुरक्षा", "ar" to "السلامة"),
        "tab.connect" to mapOf(
            "en" to "Connect", "es" to "Conectar", "fr" to "Connecter",
            "de" to "Verbinden", "pt" to "Conectar", "it" to "Connetti",
            "ja" to "接続", "zh" to "连接", "hi" to "कनेक्ट", "ar" to "اتصال"),
        "action.send" to mapOf(
            "en" to "Send", "es" to "Enviar", "fr" to "Envoyer",
            "de" to "Senden", "pt" to "Enviar", "it" to "Invia",
            "ja" to "送信", "zh" to "发送", "hi" to "भेजें", "ar" to "إرسال"),
        "action.save" to mapOf(
            "en" to "Save", "es" to "Guardar", "fr" to "Enregistrer",
            "de" to "Speichern", "pt" to "Salvar", "it" to "Salva",
            "ja" to "保存", "zh" to "保存", "hi" to "सहेजें", "ar" to "حفظ"),
        "action.translate" to mapOf(
            "en" to "Translate", "es" to "Traducir", "fr" to "Traduire",
            "de" to "Übersetzen", "pt" to "Traduzir", "it" to "Traduci",
            "ja" to "翻訳", "zh" to "翻译", "hi" to "अनुवाद", "ar" to "ترجمة"),
        "action.sign_out" to mapOf(
            "en" to "Sign out", "es" to "Cerrar sesión", "fr" to "Se déconnecter",
            "de" to "Abmelden", "pt" to "Sair", "it" to "Esci",
            "ja" to "サインアウト", "zh" to "退出登录", "hi" to "साइन आउट",
            "ar" to "تسجيل الخروج"),
        "action.refresh" to mapOf(
            "en" to "Refresh", "es" to "Actualizar", "fr" to "Actualiser",
            "de" to "Aktualisieren", "pt" to "Atualizar", "it" to "Aggiorna",
            "ja" to "更新", "zh" to "刷新", "hi" to "रीफ़्रेश", "ar" to "تحديث"),
    )
}
