/** Chrome localization for the JIM console.
 *
 * The three native shells have carried an `L10n` table in ten languages for
 * several releases. This console had none — no table, no language type, no
 * negotiation — so every string on it was English and could only be English.
 * The gap was recorded and measured last release; this is the layer.
 *
 * `visitorLang()` reads what the browser asked for, not what a profile stored:
 * the screen this is first used on belongs to somebody who has no account yet,
 * so a stored setting is guaranteed to be the default. Region is dropped, so
 * `es-419` and `es-ES` both find `es`, and anything unrecognised falls back to
 * English rather than guessing.
 */

export type Lang = "en" | "es" | "fr" | "de" | "pt" | "it" | "ja" | "zh"
  | "hi" | "ar";

const TABLE: Record<string, Partial<Record<Lang, string>>> = {
  // The footsteps chip in the corner. The same two rows stand verbatim in
  // the sibling consoles — one wording, one translation.
  "steps.count": {
    en: "{n} footsteps here", es: "{n} pasos por aquí", fr: "{n} pas par ici", de: "{n} Fußspuren hier", pt: "{n} passos por aqui", it: "{n} passi qui", ja: "ここに{n}の足あと", zh: "这里有 {n} 个足迹", hi: "यहाँ {n} क़दमों के निशान", ar: "{n} أثر أقدام هنا",
  },
  "steps.tip": {
    en: "How many people hold accounts here", es: "Cuántas personas tienen cuenta aquí", fr: "Combien de personnes ont un compte ici", de: "Wie viele Menschen hier ein Konto haben", pt: "Quantas pessoas têm conta aqui", it: "Quante persone hanno un account qui", ja: "ここにアカウントを持つ人の数", zh: "这里有多少人持有账户", hi: "यहाँ कितने लोगों के खाते हैं", ar: "كم شخصًا يملك حسابًا هنا",
  },
  "spec.ask": { en: "Ask them", es: "Preguntarles", fr: "Leur demander", de: "Frag sie", pt: "Perguntar-lhes", it: "Chiedi a loro", ja: "\u3053\u306e\u4eba\u306b\u805e\u304f", zh: "\u53bb\u95ee\u4ed6\u4eec", hi: "\u0909\u0928\u0938\u0947 \u092a\u0942\u091b\u0947\u0902", ar: "\u0627\u0633\u0623\u0644\u0647\u0645" },
  "spec.fallback": { en: "Specialist", es: "Especialista", fr: "Sp\u00e9cialiste", de: "Fachperson", pt: "Especialista", it: "Specialista", ja: "\u5c02\u9580\u5bb6", zh: "\u4e13\u5bb6", hi: "\u0935\u093f\u0936\u0947\u0937\u091c\u094d\u091e", ar: "\u0627\u0644\u0645\u062e\u062a\u0635" },
  "spec.held": { en: "Their reply is waiting for its owner to approve it \u2014 held, not refused.", es: "Su respuesta espera la aprobaci\u00f3n de su propietario: retenida, no rechazada.", fr: "Leur r\u00e9ponse attend l'approbation de son propri\u00e9taire : retenue, pas refus\u00e9e.", de: "Ihre Antwort wartet auf die Freigabe ihres Eigent\u00fcmers \u2014 zur\u00fcckgehalten, nicht abgelehnt.", pt: "A resposta aguarda a aprova\u00e7\u00e3o do seu propriet\u00e1rio \u2014 retida, n\u00e3o recusada.", it: "La loro risposta attende l'approvazione del proprietario: trattenuta, non rifiutata.", ja: "\u8fd4\u4fe1\u306f\u30aa\u30fc\u30ca\u30fc\u306e\u627f\u8a8d\u5f85\u3061\u3067\u3059 \u2014 \u62d2\u5426\u3067\u306f\u306a\u304f\u4fdd\u7559\u3055\u308c\u3066\u3044\u307e\u3059\u3002", zh: "\u4ed6\u4eec\u7684\u56de\u590d\u6b63\u5728\u7b49\u5f85\u5176\u6240\u6709\u8005\u6279\u51c6 \u2014 \u662f\u88ab\u6682\u5b58\uff0c\u800c\u4e0d\u662f\u88ab\u62d2\u7edd\u3002", hi: "\u0909\u0928\u0915\u093e \u0909\u0924\u094d\u0924\u0930 \u0909\u0938\u0915\u0947 \u0938\u094d\u0935\u093e\u092e\u0940 \u0915\u0940 \u092e\u0902\u091c\u093c\u0942\u0930\u0940 \u0915\u0940 \u092a\u094d\u0930\u0924\u0940\u0915\u094d\u0937\u093e \u092e\u0947\u0902 \u0939\u0948 \u2014 \u0930\u094b\u0915\u093e \u0917\u092f\u093e \u0939\u0948, \u0905\u0938\u094d\u0935\u0940\u0915\u093e\u0930 \u0928\u0939\u0940\u0902\u0964", ar: "\u0631\u062f\u0651\u0647\u0645 \u0628\u0627\u0646\u062a\u0638\u0627\u0631 \u0645\u0648\u0627\u0641\u0642\u0629 \u0645\u0627\u0644\u0643\u0647 \u2014 \u0645\u062d\u062c\u0648\u0632\u060c \u0644\u0627 \u0645\u0631\u0641\u0648\u0636." },
  "spec.shared": { en: "Shared", es: "Se comparti\u00f3", fr: "Partag\u00e9", de: "Geteilt", pt: "Partilhado", it: "Condiviso", ja: "\u5171\u6709\u3057\u305f\u5185\u5bb9", zh: "\u5df2\u5171\u4eab", hi: "\u0938\u093e\u091d\u093e \u0915\u093f\u092f\u093e \u0917\u092f\u093e", ar: "\u0645\u0627 \u062a\u0645\u062a \u0645\u0634\u0627\u0631\u0643\u062a\u0647" },
  "spec.via": { en: "through the tandem", es: "a trav\u00e9s del t\u00e1ndem", fr: "via le tandem", de: "\u00fcber das Tandem", pt: "atrav\u00e9s do tandem", it: "tramite il tandem", ja: "\u30bf\u30f3\u30c7\u30e0\u7d4c\u7531", zh: "\u901a\u8fc7\u53cc\u8054", hi: "\u091f\u0948\u0902\u0921\u092e \u0915\u0947 \u092e\u093e\u0927\u094d\u092f\u092e \u0938\u0947", ar: "\u0639\u0628\u0631 \u0627\u0644\u0627\u0642\u062a\u0631\u0627\u0646" },
  "lkt.changed": {
    en: "Changed {when}",
    es: "Cambió el {when}",
    fr: "A changé le {when}",
    de: "Geändert am {when}",
    pt: "Mudou em {when}",
    it: "È cambiata il {when}",
    ja: "{when} に変化",
    zh: "{when} 有变化",
    hi: "{when} को बदला",
    ar: "تغيّرت في {when}",
  },
  "lkt.title": {
    en: "Watched pages",
    es: "Páginas vigiladas",
    fr: "Pages surveillées",
    de: "Beobachtete Seiten",
    pt: "Páginas vigiadas",
    it: "Pagine sorvegliate",
    ja: "見守り中のページ",
    zh: "被关注的页面",
    hi: "निगरानी में पेज",
    ar: "صفحات مراقَبة",
  },
  "lkt.lead": {
    en: "The vault re-reads each page on its schedule — JIM never does the watching, and the capture stays sealed in the tandem.",
    es: "La bóveda relee cada página según su horario — JIM nunca hace la vigilancia, y la captura queda sellada en el tándem.",
    fr: "Le coffre relit chaque page selon son horaire — JIM ne fait jamais la surveillance, et la capture reste scellée dans le tandem.",
    de: "Der Tresor liest jede Seite nach ihrem Zeitplan neu — JIM übernimmt das Beobachten nie, und die Aufnahme bleibt im Tandem versiegelt.",
    pt: "O cofre relê cada página no seu horário — o JIM nunca faz a vigilância, e a captura fica selada no tandem.",
    it: "Il vault rilegge ogni pagina secondo il suo orario — JIM non fa mai la sorveglianza, e la cattura resta sigillata nel tandem.",
    ja: "ボールトが各ページを予定どおり読み直します。JIM が見張ることはなく、取得内容はタンデムに封緘されたままです。",
    zh: "保险库按计划重读每个页面——JIM 从不亲自盯着，抓取内容始终封存在串联库中。",
    hi: "वॉल्ट हर पेज को उसके शेड्यूल पर दोबारा पढ़ता है — निगरानी JIM कभी नहीं करता, और कैप्चर टैंडम में सील रहता है।",
    ar: "تعيد الخزنة قراءة كل صفحة وفق جدولها — لا يقوم JIM بالمراقبة أبدًا، ويبقى الالتقاط مختومًا في الترادف.",
  },
  "lkt.unreadable": {
    en: "The vault cannot be reached right now — the lookouts are listed, their status is not.",
    es: "La bóveda no responde ahora mismo: las vigilancias se listan, su estado no.",
    fr: "Le coffre est injoignable pour l'instant — les surveillances sont listées, leur état non.",
    de: "Der Tresor ist gerade nicht erreichbar — die Beobachtungen stehen in der Liste, ihr Status nicht.",
    pt: "O cofre não responde agora — as vigilâncias estão listadas, o estado não.",
    it: "Il vault ora non risponde: le sorveglianze sono elencate, il loro stato no.",
    ja: "現在ボールトに接続できません — 一覧は出ますが、状態は表示できません。",
    zh: "目前无法连接保险库 — 列表已列出，但状态无法显示。",
    hi: "वॉल्ट अभी पहुँच से बाहर है — निगरानियाँ सूचीबद्ध हैं, उनकी स्थिति नहीं।",
    ar: "تعذّر الوصول إلى الخزنة الآن — المراقبات مدرجة، أمّا حالتها فلا.",
  },
  "lkt.url": {
    en: "Page address",
    es: "Dirección de la página",
    fr: "Adresse de la page",
    de: "Adresse der Seite",
    pt: "Endereço da página",
    it: "Indirizzo della pagina",
    ja: "ページのアドレス",
    zh: "页面地址",
    hi: "पेज का पता",
    ar: "عنوان الصفحة",
  },
  "lkt.hours": {
    en: "Repeats every (hours)",
    es: "Se repite cada (horas)",
    fr: "Se répète toutes les (heures)",
    de: "Wiederholt sich alle (Stunden)",
    pt: "Repete-se a cada (horas)",
    it: "Si ripete ogni (ore)",
    ja: "繰り返し間隔（時間）",
    zh: "重复间隔（小时）",
    hi: "हर (घंटे) में दोहराए",
    ar: "يتكرر كل (ساعات)",
  },
  "lkt.plant": {
    en: "Watch this page",
    es: "Vigilar esta página",
    fr: "Surveiller cette page",
    de: "Diese Seite beobachten",
    pt: "Vigiar esta página",
    it: "Sorveglia questa pagina",
    ja: "このページを見守る",
    zh: "关注这个页面",
    hi: "इस पेज पर नज़र रखें",
    ar: "راقب هذه الصفحة",
  },
  "lkt.read": {
    en: "Read the capture",
    es: "Leer la captura",
    fr: "Lire la capture",
    de: "Die Aufnahme lesen",
    pt: "Ler a captura",
    it: "Leggi la cattura",
    ja: "取得内容を読む",
    zh: "查看抓取内容",
    hi: "कैप्चर पढ़ें",
    ar: "اقرأ الالتقاط",
  },
  "lkt.drop": {
    en: "Stop watching",
    es: "Dejar de vigilar",
    fr: "Ne plus surveiller",
    de: "Nicht mehr beobachten",
    pt: "Deixar de vigiar",
    it: "Smetti di osservare",
    ja: "見守りをやめる",
    zh: "不再留意",
    hi: "नज़र रखना बंद करें",
    ar: "أوقف المتابعة",
  },
  "lkt.nocapture": {
    en: "Nothing captured yet.",
    es: "Aún no hay ninguna captura.",
    fr: "Rien de capturé pour l'instant.",
    de: "Noch nichts aufgenommen.",
    pt: "Ainda não há captura.",
    it: "Ancora nessuna cattura.",
    ja: "まだ何も取得されていません。",
    zh: "还没有任何抓取内容。",
    hi: "अभी कोई कैप्चर नहीं है।",
    ar: "لا التقاط بعد.",
  },
  "mem.title": {
    en: "Remembered moments",
    es: "Momentos recordados",
    fr: "Moments retenus",
    de: "Erinnerte Momente",
    pt: "Momentos recordados",
    it: "Momenti ricordati",
    ja: "覚えている出来事",
    zh: "记住的时刻",
    hi: "याद रखे गए पल",
    ar: "لحظات محفوظة",
  },
  "mem.lead": {
    en: "What the coach can find again, sealed in the vault and searched by meaning. Yours to read, yours to drop — one by one here, all at once by erasing the account.",
    es: "Lo que el coach puede volver a encontrar: sellado en la bóveda y buscado por significado. Tuyo para leer y tuyo para borrar — uno a uno aquí, todo de una vez al borrar la cuenta.",
    fr: "Ce que le coach peut retrouver, scellé dans le coffre et cherché par le sens. À vous de le lire, à vous de le supprimer — un par un ici, tout d'un coup en effaçant le compte.",
    de: "Was der Coach wiederfinden kann — versiegelt im Tresor, gesucht nach Bedeutung. Du kannst es lesen und du kannst es fallen lassen — einzeln hier, alles auf einmal beim Löschen des Kontos.",
    pt: "O que o coach consegue reencontrar, selado no cofre e procurado por significado. Seu para ler, seu para largar — um a um aqui, tudo de uma vez ao apagar a conta.",
    it: "Ciò che il coach può ritrovare: sigillato nel vault e cercato per significato. Tuo da leggere, tuo da eliminare — uno alla volta qui, tutto insieme cancellando l'account.",
    ja: "コーチが後から見つけ出せるもの。ボールトに封緘され、意味で検索されます。読むのもあなた、消すのもあなた — ここでは1件ずつ、アカウント消去ではまとめて。",
    zh: "教练能再次找到的内容：封存在保险库中，按含义检索。你可以查看，也可以删除 — 在这里逐条删，注销账户时一次全删。",
    hi: "जो कोच दोबारा खोज सकता है — वॉल्ट में सील, अर्थ से खोजा गया। पढ़ना आपका हक़, हटाना भी — यहाँ एक-एक करके, खाता मिटाने पर एक साथ।",
    ar: "ما يستطيع المدرب العثور عليه مجددًا — مختوم في الخزنة ويُبحث فيه بالمعنى. لك أن تقرأه ولك أن تحذفه — واحدًا واحدًا هنا، ودفعة واحدة عند محو الحساب.",
  },
  "mem.unreadable": {
    en: "The vault cannot be reached right now — the moments are listed, their words are not.",
    es: "La bóveda no responde ahora mismo: los momentos se listan, sus palabras no.",
    fr: "Le coffre est injoignable pour l'instant — les moments sont listés, leurs mots non.",
    de: "Der Tresor ist gerade nicht erreichbar — die Momente stehen in der Liste, ihre Worte nicht.",
    pt: "O cofre não responde agora — os momentos estão listados, as palavras não.",
    it: "Il vault ora non risponde: i momenti sono elencati, le loro parole no.",
    ja: "現在ボールトに接続できません — 一覧は出ますが、言葉は表示できません。",
    zh: "目前无法连接保险库 — 时刻已列出，但内容无法显示。",
    hi: "वॉल्ट अभी पहुँच से बाहर है — पल सूचीबद्ध हैं, उनके शब्द नहीं।",
    ar: "تعذّر الوصول إلى الخزنة الآن — اللحظات مدرجة، أمّا كلماتها فلا.",
  },
  "cont.title": { en: "What carries between sessions", es: "Lo que se mantiene entre sesiones", fr: "Ce qui persiste d'une session \u00e0 l'autre", de: "Was zwischen den Sitzungen bleibt", pt: "O que se mant\u00e9m entre sess\u00f5es", it: "Ci\u00f2 che resta tra una sessione e l'altra", ja: "\u30bb\u30c3\u30b7\u30e7\u30f3\u3092\u307e\u305f\u3044\u3067\u6b8b\u308b\u3082\u306e", zh: "\u5728\u4e0d\u540c\u4f1a\u8bdd\u4e4b\u95f4\u5ef6\u7eed\u7684\u90e8\u5206", hi: "\u091c\u094b \u0938\u0924\u094d\u0930\u094b\u0902 \u0915\u0947 \u092c\u0940\u091a \u092c\u0928\u093e \u0930\u0939\u0924\u093e \u0939\u0948", ar: "\u0645\u0627 \u064a\u0628\u0642\u0649 \u0628\u064a\u0646 \u0627\u0644\u062c\u0644\u0633\u0627\u062a" },
  "cont.lead": { en: "The profile above is a snapshot you rebuild. This is the part that moves on its own \u2014 it shifts a little every time you check in, talk to the coach, or say whether guidance helped, so the Guardian does not meet you on your fortieth day the way it met you on your first.", es: "El perfil de arriba es una instant\u00e1nea que t\u00fa reconstruyes. Esta es la parte que se mueve sola: cambia un poco cada vez que registras c\u00f3mo est\u00e1s, hablas con el coach o dices si la orientaci\u00f3n ayud\u00f3, para que el Guardi\u00e1n no te reciba en tu d\u00eda cuarenta como te recibi\u00f3 el primero.", fr: "Le profil ci-dessus est un instantan\u00e9 que vous reconstruisez. Voici la partie qui \u00e9volue d'elle-m\u00eame : elle change un peu chaque fois que vous faites un bilan, parlez au coach ou dites si les conseils ont aid\u00e9, pour que le Gardien ne vous accueille pas au quaranti\u00e8me jour comme au premier.", de: "Das Profil oben ist eine Momentaufnahme, die du neu erstellst. Dies ist der Teil, der sich von selbst bewegt \u2014 er verschiebt sich ein wenig, sooft du einen Check-in machst, mit dem Coach sprichst oder sagst, ob die Hinweise geholfen haben, damit der Guardian dir am vierzigsten Tag nicht so begegnet wie am ersten.", pt: "O perfil acima \u00e9 um instant\u00e2neo que reconstr\u00f3i. Esta \u00e9 a parte que se move sozinha \u2014 muda um pouco sempre que faz um check-in, fala com o coach ou diz se a orienta\u00e7\u00e3o ajudou, para que o Guardi\u00e3o n\u00e3o o receba no quadrag\u00e9simo dia como o recebeu no primeiro.", it: "Il profilo qui sopra \u00e8 un'istantanea che ricostruisci tu. Questa \u00e8 la parte che si muove da sola: cambia un po' ogni volta che fai un check-in, parli con il coach o dici se i consigli hanno aiutato, cos\u00ec il Guardian non ti accoglie al quarantesimo giorno come al primo.", ja: "\u4e0a\u306e\u30d7\u30ed\u30d5\u30a3\u30fc\u30eb\u306f\u3001\u3042\u306a\u305f\u304c\u4f5c\u308a\u76f4\u3059\u30b9\u30ca\u30c3\u30d7\u30b7\u30e7\u30c3\u30c8\u3067\u3059\u3002\u3053\u3061\u3089\u306f\u81ea\u7136\u306b\u52d5\u304f\u90e8\u5206\u3067\u3001\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u3001\u30b3\u30fc\u30c1\u3068\u306e\u4f1a\u8a71\u3001\u52a9\u8a00\u304c\u5f79\u306b\u7acb\u3063\u305f\u304b\u306e\u56de\u7b54\u306e\u305f\u3073\u306b\u5c11\u3057\u305a\u3064\u5909\u308f\u308a\u307e\u3059\u3002\u56db\u5341\u65e5\u76ee\u306e\u3042\u306a\u305f\u3092\u3001\u4e00\u65e5\u76ee\u3068\u540c\u3058\u3088\u3046\u306b\u306f\u8fce\u3048\u307e\u305b\u3093\u3002", zh: "\u4e0a\u9762\u7684\u6863\u6848\u662f\u4f60\u624b\u52a8\u91cd\u5efa\u7684\u5feb\u7167\u3002\u8fd9\u91cc\u662f\u4f1a\u81ea\u884c\u53d8\u5316\u7684\u90e8\u5206 \u2014 \u6bcf\u6b21\u4f60\u7b7e\u5230\u3001\u4e0e\u6559\u7ec3\u4ea4\u8c08\u6216\u8bf4\u660e\u5efa\u8bae\u662f\u5426\u6709\u5e2e\u52a9\u65f6\uff0c\u5b83\u90fd\u4f1a\u7565\u5fae\u79fb\u52a8\uff0c\u8ba9\u5b88\u62a4\u8005\u5728\u7b2c\u56db\u5341\u5929\u4e0d\u4f1a\u7528\u7b2c\u4e00\u5929\u7684\u65b9\u5f0f\u6765\u8fce\u63a5\u4f60\u3002", hi: "\u090a\u092a\u0930 \u0915\u0940 \u092a\u094d\u0930\u094b\u092b\u093c\u093e\u0907\u0932 \u090f\u0915 \u0938\u094d\u0928\u0948\u092a\u0936\u0949\u091f \u0939\u0948 \u091c\u093f\u0938\u0947 \u0906\u092a \u092b\u093f\u0930 \u0938\u0947 \u092c\u0928\u093e\u0924\u0947 \u0939\u0948\u0902\u0964 \u092f\u0939 \u0935\u0939 \u0939\u093f\u0938\u094d\u0938\u093e \u0939\u0948 \u091c\u094b \u0905\u092a\u0928\u0947 \u0906\u092a \u092c\u0926\u0932\u0924\u093e \u0939\u0948 \u2014 \u0939\u0930 \u092c\u093e\u0930 \u091c\u092c \u0906\u092a \u091a\u0947\u0915-\u0907\u0928 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902, \u0915\u094b\u091a \u0938\u0947 \u092c\u093e\u0924 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902, \u092f\u093e \u092c\u0924\u093e\u0924\u0947 \u0939\u0948\u0902 \u0915\u093f \u092e\u093e\u0930\u094d\u0917\u0926\u0930\u094d\u0936\u0928 \u0938\u0947 \u092e\u0926\u0926 \u092e\u093f\u0932\u0940 \u092f\u093e \u0928\u0939\u0940\u0902, \u092f\u0939 \u0925\u094b\u0921\u093c\u093e \u0916\u093f\u0938\u0915\u0924\u093e \u0939\u0948, \u0924\u093e\u0915\u093f \u0917\u093e\u0930\u094d\u091c\u093f\u092f\u0928 \u0906\u092a\u0915\u0947 \u091a\u093e\u0932\u0940\u0938\u0935\u0947\u0902 \u0926\u093f\u0928 \u0906\u092a\u0938\u0947 \u0935\u0948\u0938\u0947 \u0928 \u092e\u093f\u0932\u0947 \u091c\u0948\u0938\u0947 \u092a\u0939\u0932\u0947 \u0926\u093f\u0928 \u092e\u093f\u0932\u093e \u0925\u093e\u0964", ar: "\u0627\u0644\u0645\u0644\u0641 \u0623\u0639\u0644\u0627\u0647 \u0644\u0642\u0637\u0629 \u062a\u0639\u064a\u062f \u0628\u0646\u0627\u0621\u0647\u0627 \u0628\u0646\u0641\u0633\u0643. \u0623\u0645\u0651\u0627 \u0647\u0630\u0627 \u0641\u0647\u0648 \u0627\u0644\u062c\u0632\u0621 \u0627\u0644\u0630\u064a \u064a\u062a\u062d\u0631\u0643 \u0645\u0646 \u062a\u0644\u0642\u0627\u0621 \u0646\u0641\u0633\u0647 \u2014 \u064a\u062a\u063a\u064a\u0651\u0631 \u0642\u0644\u064a\u0644\u064b\u0627 \u0641\u064a \u0643\u0644 \u0645\u0631\u0629 \u062a\u0633\u062c\u0651\u0644 \u0641\u064a\u0647\u0627 \u062d\u0627\u0644\u062a\u0643\u060c \u0623\u0648 \u062a\u062a\u062d\u062f\u062b \u0625\u0644\u0649 \u0627\u0644\u0645\u062f\u0631\u0651\u0628\u060c \u0623\u0648 \u062a\u0642\u0648\u0644 \u0625\u0646 \u0627\u0644\u0625\u0631\u0634\u0627\u062f \u0642\u062f \u0633\u0627\u0639\u062f\u060c \u062d\u062a\u0649 \u0644\u0627 \u064a\u0633\u062a\u0642\u0628\u0644\u0643 \u0627\u0644\u062d\u0627\u0631\u0633 \u0641\u064a \u064a\u0648\u0645\u0643 \u0627\u0644\u0623\u0631\u0628\u0639\u064a\u0646 \u0643\u0645\u0627 \u0627\u0633\u062a\u0642\u0628\u0644\u0643 \u0641\u064a \u064a\u0648\u0645\u0643 \u0627\u0644\u0623\u0648\u0644." },
  "cont.observations": { en: "observations", es: "observaciones", fr: "observations", de: "Beobachtungen", pt: "observa\u00e7\u00f5es", it: "osservazioni", ja: "\u4ef6\u306e\u89b3\u6e2c", zh: "\u6b21\u89c2\u5bdf", hi: "\u0905\u0935\u0932\u094b\u0915\u0928", ar: "\u0645\u0644\u0627\u062d\u0638\u0629" },
  "cont.shaping": { en: "shaping how the coach answers", es: "influye en c\u00f3mo responde el coach", fr: "influence la fa\u00e7on dont le coach r\u00e9pond", de: "beeinflusst, wie der Coach antwortet", pt: "influencia como o coach responde", it: "influenza come risponde il coach", ja: "\u30b3\u30fc\u30c1\u306e\u7b54\u3048\u65b9\u306b\u53cd\u6620\u3055\u308c\u3066\u3044\u307e\u3059", zh: "\u6b63\u5728\u5f71\u54cd\u6559\u7ec3\u7684\u56de\u7b54\u65b9\u5f0f", hi: "\u0915\u094b\u091a \u0915\u0947 \u0909\u0924\u094d\u0924\u0930 \u0926\u0947\u0928\u0947 \u0915\u0947 \u0924\u0930\u0940\u0915\u0947 \u0915\u094b \u0906\u0915\u093e\u0930 \u0926\u0947 \u0930\u0939\u093e \u0939\u0948", ar: "\u064a\u0624\u062b\u0631 \u0641\u064a \u0637\u0631\u064a\u0642\u0629 \u0631\u062f \u0627\u0644\u0645\u062f\u0631\u0651\u0628" },
  "cont.not_yet": { en: "not shaping anything yet \u2014 too little to mean much", es: "todav\u00eda no influye en nada: hay muy poco para significar algo", fr: "n'influence encore rien \u2014 trop peu pour vouloir dire grand-chose", de: "beeinflusst noch nichts \u2014 zu wenig, um etwas zu bedeuten", pt: "ainda n\u00e3o influencia nada \u2014 muito pouco para significar algo", it: "non influenza ancora nulla: troppo poco per significare qualcosa", ja: "\u307e\u3060\u4f55\u306b\u3082\u53cd\u6620\u3055\u308c\u3066\u3044\u307e\u305b\u3093 \u2014 \u5224\u65ad\u3059\u308b\u306b\u306f\u5c11\u306a\u3059\u304e\u307e\u3059", zh: "\u5c1a\u672a\u5f71\u54cd\u4efb\u4f55\u5185\u5bb9 \u2014 \u6570\u636e\u592a\u5c11\uff0c\u8bf4\u660e\u4e0d\u4e86\u4ec0\u4e48", hi: "\u0905\u092d\u0940 \u0915\u0941\u091b \u092d\u0940 \u0906\u0915\u093e\u0930 \u0928\u0939\u0940\u0902 \u0926\u0947 \u0930\u0939\u093e \u2014 \u0907\u0924\u0928\u093e \u0915\u092e \u0915\u093f \u0915\u094b\u0908 \u092e\u0924\u0932\u092c \u0928 \u0928\u093f\u0915\u0932\u0947", ar: "\u0644\u0627 \u064a\u0624\u062b\u0631 \u0641\u064a \u0634\u064a\u0621 \u0628\u0639\u062f \u2014 \u0623\u0642\u0644 \u0645\u0646 \u0623\u0646 \u064a\u0639\u0646\u064a \u0634\u064a\u0626\u064b\u0627" },
  "cont.forget": { en: "Forget it", es: "Olvidarlo", fr: "Tout oublier", de: "Verwerfen", pt: "Esquecer", it: "Dimenticalo", ja: "\u7834\u68c4\u3059\u308b", zh: "\u6e05\u9664\u5b83", hi: "\u0907\u0938\u0947 \u092d\u0942\u0932 \u091c\u093e\u090f\u0901", ar: "\u0627\u062d\u0630\u0641\u0647" },
  "cont.nothing": { en: "Nothing yet.", es: "Todav\u00eda nada.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Ainda nada.", it: "Ancora niente.", ja: "\u307e\u3060\u4f55\u3082\u3042\u308a\u307e\u305b\u3093\u3002", zh: "\u6682\u65f6\u8fd8\u6ca1\u6709\u3002", hi: "\u0905\u092d\u0940 \u0915\u0941\u091b \u0928\u0939\u0940\u0902\u0964", ar: "\u0644\u0627 \u0634\u064a\u0621 \u0628\u0639\u062f." },
  // The task window (jim/underway.py), pinned like the lights beside it.
  // `kind` and `why` arrive as closed-set words and are said here, so the
  // server never composes a sentence somebody reads in the wrong language.
  "und.title": {
    en: "Underway", es: "En curso", fr: "En cours", de: "Läuft gerade",
    pt: "Em curso", it: "In corso", ja: "進行中", zh: "进行中",
    hi: "चल रहा है", ar: "قيد التشغيل",
  },
  "und.quiet": {
    en: "nothing running", es: "nada en marcha", fr: "rien en cours",
    de: "nichts läuft", pt: "nada em curso", it: "niente in corso",
    ja: "動いているものはありません", zh: "没有正在运行的内容",
    hi: "कुछ भी नहीं चल रहा", ar: "لا شيء قيد التشغيل",
  },
  "und.hide": {
    en: "Hide what is running", es: "Ocultar lo que está en marcha",
    fr: "Masquer ce qui est en cours", de: "Ausblenden, was läuft",
    pt: "Ocultar o que está em curso", it: "Nascondi cosa è in corso",
    ja: "進行中のものを隠す", zh: "隐藏正在运行的内容",
    hi: "जो चल रहा है उसे छिपाएँ", ar: "إخفاء ما يعمل الآن",
  },
  "und.show": {
    en: "Show what is running", es: "Mostrar lo que está en marcha",
    fr: "Afficher ce qui est en cours", de: "Anzeigen, was läuft",
    pt: "Mostrar o que está em curso", it: "Mostra cosa è in corso",
    ja: "進行中のものを表示", zh: "显示正在运行的内容",
    hi: "जो चल रहा है वह दिखाएँ", ar: "إظهار ما يعمل الآن",
  },
  "und.unreachable": {
    en: "Cannot reach the Guardian — press to try again",
    es: "No se puede contactar con el Guardián: pulsa para reintentar",
    fr: "Le Gardien est injoignable — appuyez pour réessayer",
    de: "Der Wächter ist nicht erreichbar — zum Wiederholen drücken",
    pt: "Não é possível contactar o Guardião — prima para tentar de novo",
    it: "Il Guardiano non è raggiungibile — premi per riprovare",
    ja: "ガーディアンに接続できません — 押すと再試行します",
    zh: "无法连接守护者 — 按此重试",
    hi: "अभिभावक तक नहीं पहुँच सके — दोबारा कोशिश करने के लिए दबाएँ",
    ar: "تعذّر الوصول إلى الحارس — اضغط للمحاولة مرة أخرى",
  },
  "und.kind.engaged": {
    en: "agent session", es: "sesión del agente", fr: "session de l'agent",
    de: "Agentensitzung", pt: "sessão do agente", it: "sessione dell'agente",
    ja: "エージェントのセッション", zh: "代理会话", hi: "एजेंट सत्र",
    ar: "جلسة الوكيل",
  },
  "und.kind.liaison": {
    en: "with another guardian", es: "con otro guardián",
    fr: "avec un autre gardien", de: "mit einem anderen Wächter",
    pt: "com outro guardião", it: "con un altro guardiano",
    ja: "別のガーディアンと", zh: "与另一位守护者",
    hi: "दूसरे अभिभावक के साथ", ar: "مع حارس آخر",
  },
  "und.kind.call": {
    en: "call", es: "llamada", fr: "appel", de: "Anruf", pt: "chamada",
    it: "chiamata", ja: "通話", zh: "通话", hi: "कॉल", ar: "مكالمة",
  },
  "und.kind.listening": {
    en: "second microphone", es: "segundo micrófono",
    fr: "second microphone", de: "zweites Mikrofon",
    pt: "segundo microfone", it: "secondo microfono", ja: "第2マイク",
    zh: "第二麦克风", hi: "दूसरा माइक्रोफ़ोन", ar: "الميكروفون الثاني",
  },
  // The kind is a noun now, not a verb. It said "sensing" for every
  // switched-on row, which printed a permission as an activity — a field
  // report read the window against a house with nothing paired and
  // called it: nothing was sensing anything. The verb moved to `why`,
  // where it can tell the truth per row.
  "und.kind.monitor": {
    en: "monitor", es: "monitor", fr: "capteur", de: "Melder",
    pt: "monitor", it: "sensore", ja: "モニター", zh: "监测",
    hi: "मॉनिटर", ar: "مِرقاب",
  },
  "und.why.sensing": {
    en: "sensing", es: "detectando", fr: "capte", de: "erfasst",
    pt: "a detetar", it: "sta rilevando", ja: "感知中", zh: "正在感知",
    hi: "महसूस कर रहा है", ar: "يستشعر",
  },
  "und.why.waiting": {
    en: "waiting — nothing has come from it yet",
    es: "esperando — aún no ha llegado nada de él",
    fr: "en attente — rien n'en est encore venu",
    de: "wartet — es kam noch nichts davon",
    pt: "à espera — ainda não chegou nada dele",
    it: "in attesa — non è ancora arrivato nulla",
    ja: "待機中 — まだ何も届いていません",
    zh: "等待中 — 尚未收到任何数据",
    hi: "प्रतीक्षा में — अभी तक इससे कुछ नहीं आया",
    ar: "في الانتظار — لم يصل منه شيء بعد",
  },
  // Why a row is still open. `proposed` and `agreed` are the two states of a
  // link's task, and only the second survives the call — so they are said
  // differently rather than both reading "task".
  "und.why.proposed": {
    en: "task proposed — not agreed yet",
    es: "tarea propuesta: aún sin acordar",
    fr: "tâche proposée — pas encore acceptée",
    de: "Aufgabe vorgeschlagen — noch nicht vereinbart",
    pt: "tarefa proposta — ainda não acordada",
    it: "compito proposto — non ancora concordato",
    ja: "タスクを提案中 — まだ合意されていません",
    zh: "已提议任务 — 尚未达成一致",
    hi: "कार्य प्रस्तावित — अभी सहमति नहीं",
    ar: "مهمة مقترحة — لم يُتفق عليها بعد",
  },
  "und.why.agreed": {
    en: "task agreed by both", es: "tarea acordada por ambos",
    fr: "tâche acceptée des deux côtés", de: "von beiden vereinbarte Aufgabe",
    pt: "tarefa acordada por ambos", it: "compito concordato da entrambi",
    ja: "双方が合意したタスク", zh: "双方已同意的任务",
    hi: "दोनों की सहमति वाला कार्य", ar: "مهمة اتفق عليها الطرفان",
  },
  "und.why.announced": {
    en: "the notice went out", es: "el aviso ya se dio",
    fr: "l'avertissement a été diffusé", de: "der Hinweis ging hinaus",
    pt: "o aviso já foi dado", it: "l'avviso è stato dato",
    ja: "告知は伝えられました", zh: "提示音已播出",
    hi: "सूचना दी जा चुकी है", ar: "أُذيع التنبيه",
  },
  "und.why.not_announced": {
    en: "nothing is listening until the notice goes out",
    es: "nada escucha hasta que se dé el aviso",
    fr: "rien n'écoute tant que l'avertissement n'a pas été diffusé",
    de: "nichts hört zu, bis der Hinweis hinausgeht",
    pt: "nada escuta até o aviso ser dado",
    it: "nulla ascolta finché non viene dato l'avviso",
    ja: "告知が伝えられるまで、何も聞いていません",
    zh: "在提示音播出前，没有任何东西在收听",
    hi: "जब तक सूचना नहीं दी जाती, कुछ भी नहीं सुन रहा",
    ar: "لا شيء يستمع حتى يُذاع التنبيه",
  },
  "und.today": {
    en: "Learned today", es: "Aprendido hoy", fr: "Appris aujourd'hui",
    de: "Heute gelernt", pt: "Aprendido hoje", it: "Imparato oggi",
    ja: "今日学んだこと", zh: "今天学到的", hi: "आज सीखा गया",
    ar: "ما تعلّمه اليوم",
  },
  "und.spend": {
    en: "{n} of {daily} errands today",
    es: "{n} de {daily} recados hoy",
    fr: "{n} sorties sur {daily} aujourd'hui",
    de: "{n} von {daily} Erkundungen heute",
    pt: "{n} de {daily} diligências hoje",
    it: "{n} di {daily} commissioni oggi",
    ja: "本日 {daily} 件中 {n} 件の調べもの",
    zh: "今天 {daily} 次外出学习中的 {n} 次",
    hi: "आज {daily} में से {n} खोज-यात्राएँ",
    ar: "{n} من {daily} مهام اليوم",
  },
  // The day as it was taken in (jim/daybook.py). `day.why.*` are the
  // closed-set reasons a moment's content did not survive.
  // What a room saw and heard (jim/cues.py).
  // Both parties on channel 2 (jim/mic.py).
  "pair.head": { en: "Both of you, each on your own", es: "Los dos, cada uno con el suyo", fr: "Vous deux, chacun le sien", de: "Ihr beide, jeder mit dem eigenen", pt: "Os dois, cada um com o seu", it: "Entrambi, ciascuno con il proprio", ja: "二人とも、それぞれ自分のマイクで", zh: "你们两人，各用各的", hi: "आप दोनों, हर एक अपने साथ", ar: "كلاكما، كلٌّ بميكروفونه" },
  "pair.lead": { en: "On a call where both guardians are listening, each of you is entitled to know the other's is. Nothing crosses but that — not what theirs hears, on what, or at what range.", es: "En una llamada donde ambos guardianes escuchan, cada uno tiene derecho a saber que el del otro también. No cruza nada más: ni qué oye el suyo, ni con qué, ni a qué distancia.", fr: "Lors d'un appel où les deux gardiens écoutent, chacun a le droit de savoir que celui de l'autre écoute aussi. Rien d'autre ne passe : ni ce que le leur entend, ni sur quoi, ni à quelle portée.", de: "In einem Gespräch, in dem beide Wächter mithören, darf jeder wissen, dass der andere es auch tut. Mehr geht nicht hinüber — nicht, was deren hört, womit oder auf welche Entfernung.", pt: "Numa chamada em que ambos os guardiões ouvem, cada um tem direito a saber que o do outro também ouve. Nada mais atravessa: nem o que o deles ouve, nem com quê, nem a que distância.", it: "In una chiamata in cui entrambi i guardiani ascoltano, ognuno ha diritto di sapere che anche quello dell'altro lo fa. Non passa altro: né cosa sente il loro, né con cosa, né a che distanza.", ja: "双方のガーディアンが聞いている通話では、相手のも聞いていることを互いに知る権利があります。それ以外は何も渡りません — 相手が何を、何で、どの距離で聞いているかは渡りません。", zh: "在双方守护者都在收听的通话中，你们各自都有权知道对方的也在听。除此之外什么都不会传递 — 对方听到什么、用什么听、听多远，都不会。", hi: "जिस कॉल में दोनों अभिभावक सुन रहे हों, वहाँ हर एक को यह जानने का हक़ है कि दूसरे का भी सुन रहा है। इसके अलावा कुछ नहीं जाता — न यह कि उनका क्या सुनता है, न किस पर, न कितनी दूरी तक।", ar: "في مكالمة يستمع فيها الحارسان، لكلٍّ منكما الحق في معرفة أن حارس الآخر يستمع أيضًا. ولا يعبر سوى ذلك — لا ما يسمعه حارسهم، ولا بأي جهاز، ولا على أي مدى." },
  "pair.go": { en: "Say who else is on this call", es: "Indicar quién más está en la llamada", fr: "Indiquer qui d'autre est en ligne", de: "Sagen, wer sonst im Gespräch ist", pt: "Indicar quem mais está na chamada", it: "Indica chi altro è in chiamata", ja: "通話にいる相手を伝える", zh: "说明通话中还有谁", hi: "बताएँ कि कॉल पर और कौन है", ar: "قل من غيرك في المكالمة" },
  "pair.both": { en: "theirs is listening too", es: "el suyo también está escuchando", fr: "le leur écoute aussi", de: "deren hört ebenfalls mit", pt: "o deles também está a ouvir", it: "anche il loro sta ascoltando", ja: "相手のも聞いています", zh: "对方的也在收听", hi: "उनका भी सुन रहा है", ar: "وحارسهم يستمع أيضًا" },
  "pair.waiting": { en: "waiting for them to say the same", es: "esperando a que digan lo mismo", fr: "en attente qu'ils en disent autant", de: "wartet darauf, dass sie dasselbe sagen", pt: "à espera que digam o mesmo", it: "in attesa che dicano lo stesso", ja: "相手が同じことを伝えるのを待っています", zh: "等待对方也这样说明", hi: "उनके भी यही कहने की प्रतीक्षा", ar: "في انتظار أن يقولوا المثل" },
  "pair.end": { en: "Stop saying so", es: "Dejar de indicarlo", fr: "Cesser de l'indiquer", de: "Nicht mehr angeben", pt: "Deixar de o indicar", it: "Smetti di indicarlo", ja: "伝えるのをやめる", zh: "不再说明", hi: "बताना बंद करें", ar: "توقف عن ذكر ذلك" },
  "cue.head": { en: "What the rooms noticed", es: "Lo que notaron las habitaciones", fr: "Ce que les pièces ont remarqué", de: "Was die Räume bemerkt haben", pt: "O que as divisões repararam", it: "Ciò che le stanze hanno notato", ja: "部屋が気づいたこと", zh: "房间注意到的事", hi: "कमरों ने क्या देखा", ar: "ما لاحظته الغرف" },
  "cue.lead": { en: "Read as it passes, never out of anything kept — so a camera with keeping switched off notices a fall exactly as well as one keeping everything, and stores exactly as little as it promised.", es: "Se lee al pasar, nunca de algo guardado: una cámara con la conservación desactivada detecta una caída igual de bien que una que lo guarda todo, y almacena exactamente tan poco como prometió.", fr: "Lu au passage, jamais dans ce qui est conservé : une caméra dont la conservation est désactivée remarque une chute aussi bien qu'une autre qui garde tout, et n'enregistre que ce qu'elle avait promis.", de: "Beim Durchgang gelesen, nie aus Gespeichertem — eine Kamera mit ausgeschaltetem Behalten bemerkt einen Sturz genauso gut wie eine, die alles behält, und speichert genau so wenig, wie sie versprochen hat.", pt: "Lido de passagem, nunca a partir do que foi guardado: uma câmara com a conservação desligada repara numa queda tão bem como uma que guarda tudo, e armazena exatamente tão pouco como prometeu.", it: "Letto al passaggio, mai da ciò che è conservato: una telecamera con la conservazione disattivata nota una caduta bene quanto una che conserva tutto, e memorizza esattamente quanto poco aveva promesso.", ja: "通り過ぎる時に読み取り、保存されたものからは決して読みません。保持をオフにしたカメラも、すべてを保持するカメラと同じように転倒に気づき、約束どおり何も残しません。", zh: "在经过时读取，绝不从保存的内容中读取 — 关闭了保留的摄像头，识别跌倒的能力与保留一切的摄像头完全相同，而存下的东西恰如它所承诺的那样少。", hi: "गुज़रते समय पढ़ा जाता है, कभी रखी गई किसी चीज़ से नहीं — इसलिए जिस कैमरे का रखना बंद है वह गिरने को उतनी ही अच्छी तरह पहचानता है जितना सब कुछ रखने वाला, और उतना ही कम संग्रहीत करता है जितना उसने वादा किया था।", ar: "يُقرأ أثناء المرور، لا من شيء محفوظ — فالكاميرا التي أُوقف احتفاظها تلاحظ السقوط تمامًا كتلك التي تحتفظ بكل شيء، ولا تخزّن إلا القليل الذي وعدت به." },
  "cue.none": { en: "nothing noticed", es: "nada detectado", fr: "rien de remarqué", de: "nichts bemerkt", pt: "nada reparado", it: "nulla di notato", ja: "気づいたことはありません", zh: "没有注意到任何情况", hi: "कुछ नहीं देखा गया", ar: "لم يُلاحظ شيء" },
  "cue.canread": { en: "What this one could ever notice", es: "Lo que este podría llegar a detectar", fr: "Ce que celui-ci pourrait remarquer", de: "Was dieser überhaupt bemerken könnte", pt: "O que este poderia chegar a reparar", it: "Ciò che questo potrebbe mai notare", ja: "これが気づける範囲", zh: "这一项可能注意到的内容", hi: "यह क्या-क्या देख सकता है", ar: "ما يمكن لهذا ملاحظته" },
  "cue.canread.none": { en: "nothing — it does not see or hear", es: "nada: no ve ni oye", fr: "rien — il ne voit ni n'entend", de: "nichts — es sieht und hört nicht", pt: "nada — não vê nem ouve", it: "niente: non vede né sente", ja: "なし — 見ることも聞くこともありません", zh: "没有 — 它既不看也不听", hi: "कुछ नहीं — यह न देखता है न सुनता है", ar: "لا شيء — فهو لا يرى ولا يسمع" },
  "day.head": { en: "Your day, as it was taken in", es: "Tu día, tal como se registró", fr: "Votre journée, telle qu'elle a été captée", de: "Dein Tag, so wie er aufgenommen wurde", pt: "O seu dia, tal como foi captado", it: "La tua giornata, così com'è stata raccolta", ja: "取り込まれたままの一日", zh: "你的一天，如其被记录的样子", hi: "आपका दिन, जैसा दर्ज हुआ", ar: "يومك كما جرى تسجيله" },
  "day.lead": { en: "Every moment a monitor sensed something is here, whether or not any of it was kept — and each one says which promise dropped it. What survived is the short list.", es: "Aquí está cada momento en que algo te detectó, se haya guardado o no, y cada uno dice qué promesa lo descartó. Lo que sobrevivió es la lista corta.", fr: "Chaque instant capté figure ici, qu'il ait été conservé ou non, et chacun dit quelle promesse l'a écarté. Ce qui a survécu est la liste courte.", de: "Jeder Moment, in dem etwas erfasst wurde, steht hier — ob behalten oder nicht — und jeder nennt das Versprechen, das ihn verworfen hat. Was blieb, ist die kurze Liste.", pt: "Cada momento em que algo o detetou está aqui, tenha sido guardado ou não, e cada um diz que promessa o descartou. O que sobreviveu é a lista curta.", it: "Ogni momento in cui qualcosa ti ha rilevato è qui, che sia stato conservato o no, e ognuno dice quale promessa l'ha scartato. Ciò che è rimasto è l'elenco breve.", ja: "何かが感知したすべての瞬間が、保持されたかどうかにかかわらずここにあります。それぞれ、どの約束によって破棄されたかを示します。残ったものは短いリストです。", zh: "每一个被感知到的时刻都在这里，无论是否被保留 — 每一条都会说明是哪项承诺将它丢弃。留存下来的只是很短的一份清单。", hi: "जिस भी क्षण किसी मॉनिटर ने कुछ महसूस किया वह यहाँ है, चाहे कुछ रखा गया हो या नहीं — और हर एक बताता है कि किस वादे ने उसे छोड़ा। जो बचा वह छोटी सूची है।", ar: "كل لحظة استشعر فيها جهازٌ شيئًا موجودة هنا، سواء حُفظ منها شيء أم لا — وكل واحدة تذكر الوعد الذي أسقطها. وما بقي هو القائمة القصيرة." },
  "day.sensed": { en: "sensed", es: "detectado", fr: "capté", de: "erfasst", pt: "detetado", it: "rilevato", ja: "感知", zh: "已感知", hi: "महसूस किया", ar: "استُشعر" },
  "day.kept": { en: "kept", es: "guardado", fr: "conservé", de: "behalten", pt: "guardado", it: "conservato", ja: "保持", zh: "已保留", hi: "रखा गया", ar: "محفوظ" },
  "day.quiet": { en: "nothing sensed today", es: "hoy no se detectó nada", fr: "rien de capté aujourd'hui", de: "heute nichts erfasst", pt: "hoje não se detetou nada", it: "oggi non è stato rilevato nulla", ja: "本日、感知したものはありません", zh: "今天没有感知到任何内容", hi: "आज कुछ भी महसूस नहीं हुआ", ar: "لم يُستشعر شيء اليوم" },
  "day.why.holds_nothing": { en: "this one never keeps anything — that is what it promised", es: "este nunca guarda nada: eso es lo que prometió", fr: "celui-ci ne conserve jamais rien — c'est ce qu'il a promis", de: "dieser behält nie etwas — das hat er versprochen", pt: "este nunca guarda nada — foi o que prometeu", it: "questo non conserva mai nulla: è ciò che ha promesso", ja: "これは何も保持しません — それが約束です", zh: "这一项从不保留任何内容 — 这正是它的承诺", hi: "यह कभी कुछ नहीं रखता — यही इसका वादा है", ar: "هذا لا يحتفظ بشيء أبدًا — هذا ما وعد به" },
  "day.why.keeping_is_off": { en: "keeping is switched off for this one", es: "la conservación está desactivada para este", fr: "la conservation est désactivée pour celui-ci", de: "das Behalten ist für diesen ausgeschaltet", pt: "a conservação está desligada para este", it: "la conservazione è disattivata per questo", ja: "これは保持がオフになっています", zh: "这一项的保留已关闭", hi: "इसके लिए रखना बंद है", ar: "الاحتفاظ مُعطَّل لهذا" },
  "day.why.nothing_to_keep": { en: "there was nothing in it to keep", es: "no había nada que guardar", fr: "il n'y avait rien à conserver", de: "es war nichts da, was man behalten könnte", pt: "não havia nada para guardar", it: "non c'era nulla da conservare", ja: "保持するものがありませんでした", zh: "其中没有可保留的内容", hi: "उसमें रखने लायक कुछ नहीं था", ar: "لم يكن فيه ما يُحفظ" },
  "day.why.forgotten": { en: "you asked it to forget this one", es: "le pediste que olvidara este", fr: "vous lui avez demandé d'oublier celui-ci", de: "du hast es gebeten, dies zu vergessen", pt: "pediu-lhe que esquecesse este", it: "gli hai chiesto di dimenticare questo", ja: "これは忘れるよう指示しました", zh: "你要求它忘记这一条", hi: "आपने इसे भूलने को कहा", ar: "طلبت منه أن ينسى هذا" },
  "day.forget": { en: "Forget this", es: "Olvidar esto", fr: "Oublier ceci", de: "Dies vergessen", pt: "Esquecer isto", it: "Dimentica questo", ja: "これを忘れる", zh: "忘记这条", hi: "इसे भूल जाएँ", ar: "انسَ هذا" },
  "day.meet.heard": {
    en: "Hand it a recording — the words survive as the monitor promises; the audio never does", es: "Entrégale una grabación: las palabras sobreviven según promete el monitor; el audio nunca", fr: "Donnez-lui un enregistrement — les mots survivent selon la promesse du moniteur ; l'audio jamais", de: "Gib ihr eine Aufnahme — die Worte überleben, wie es der Monitor verspricht; das Audio nie", pt: "Entregue-lhe uma gravação — as palavras sobrevivem conforme o monitor promete; o áudio nunca", it: "Consegnale una registrazione — le parole sopravvivono come promette il monitor; l'audio mai", ja: "録音を渡す — 言葉はモニターの約束の範囲で残り、音声は決して残りません", zh: "交给它一段录音——文字按监视器的承诺留存；音频绝不留存", hi: "इसे एक रिकॉर्डिंग दें — शब्द मॉनिटर के वादे तक रहते हैं; ऑडियो कभी नहीं", ar: "سلّمه تسجيلًا — تبقى الكلمات بقدر ما يعِد المراقب؛ أما الصوت فلا يبقى أبدًا",
  },
  "day.meet": { en: "Meetings and stretches", es: "Reuniones y tramos", fr: "Réunions et plages", de: "Besprechungen und Abschnitte", pt: "Reuniões e períodos", it: "Riunioni e intervalli", ja: "会議と時間帯", zh: "会议与时段", hi: "बैठकें और अवधियाँ", ar: "الاجتماعات والفترات" },
  "day.meet.open": { en: "Start one here", es: "Iniciar uno aquí", fr: "En démarrer une ici", de: "Hier eine starten", pt: "Iniciar um aqui", it: "Avviane una qui", ja: "ここで開始", zh: "在此开始", hi: "यहाँ शुरू करें", ar: "ابدأ واحدة هنا" },
  "day.meet.told": { en: "the people in the room were told", es: "se informó a las personas en la sala", fr: "les personnes présentes ont été informées", de: "die Anwesenden wurden informiert", pt: "as pessoas na sala foram informadas", it: "le persone presenti sono state informate", ja: "その場の人たちに伝えました", zh: "房间里的人已被告知", hi: "कमरे में मौजूद लोगों को बताया गया", ar: "أُبلغ من في الغرفة" },
  "day.meet.end": { en: "End the meeting", es: "Terminar la reunión", fr: "Terminer la réunion", de: "Die Besprechung beenden", pt: "Terminar a reunião", it: "Termina la riunione", ja: "会議を終了する", zh: "结束这场会议", hi: "बैठक समाप्त करें", ar: "أنهِ الاجتماع" },
  "lights.title": {
    en: "Guardian", es: "Guardián", fr: "Gardien", de: "Wächter",
    pt: "Guardião", it: "Guardiano", ja: "ガーディアン", zh: "守护者",
    hi: "अभिभावक", ar: "الحارس",
  },
  "lights.alarms": {
    en: "alarms", es: "alarmas", fr: "alarmes", de: "Alarme",
    pt: "alarmes", it: "allarmi", ja: "アラーム", zh: "警报",
    hi: "अलार्म", ar: "إنذارات",
  },
  "lights.vigil": {
    en: "vigil", es: "vigilia", fr: "veille", de: "Wache",
    pt: "vigília", it: "veglia", ja: "見守り", zh: "值守",
    hi: "पहरा", ar: "السهر",
  },
  "watch.title": {
    en: "Watch", es: "Reloj", fr: "Montre", de: "Uhr",
    pt: "Relógio", it: "Orologio", ja: "ウォッチ", zh: "手表",
    hi: "घड़ी", ar: "الساعة",
  },
  "watch.lead": {
    en: "No app to install. An automation on your phone drips readings to the address below, and your wearable's export teaches JIM your baseline from the history it already recorded. Pick what you wear — the steps change to match.",
    es: "Sin app que instalar. Una automatización en tu teléfono envía lecturas a la dirección de abajo, y la exportación de tu dispositivo enseña a JIM tu línea base con el historial ya registrado. Elige lo que llevas puesto: los pasos cambian según el dispositivo.",
    fr: "Rien à installer. Une automatisation sur votre téléphone envoie les mesures à l'adresse ci-dessous, et l'export de votre appareil apprend à JIM votre référence à partir de l'historique déjà enregistré. Choisissez ce que vous portez — les étapes s'adaptent.",
    de: "Keine App nötig. Eine Automatisierung auf dem Telefon sendet Messwerte an die Adresse unten, und der Export deines Geräts lehrt JIM deine Basislinie aus der bereits aufgezeichneten Historie. Wähl, was du trägst — die Schritte passen sich an.",
    pt: "Sem app para instalar. Uma automação no telefone envia leituras para o endereço abaixo, e a exportação do seu dispositivo ensina ao JIM a sua linha de base com o histórico já registado. Escolha o que usa — os passos mudam conforme o aparelho.",
    it: "Nessuna app da installare. Un'automazione sul telefono invia le letture all'indirizzo qui sotto, e l'esportazione del tuo dispositivo insegna a JIM la tua linea di base dalla cronologia già registrata. Scegli cosa indossi: i passaggi cambiano di conseguenza.",
    ja: "アプリのインストールは不要。スマホの自動化が下のアドレスへ測定値を送り、ウェアラブルのエクスポートが記録済みの履歴からベースラインをJIMに教えます。着けている機器を選ぶと手順が変わります。",
    zh: "无需安装应用。手机上的自动化把读数发送到下面的地址，穿戴设备的导出用已有历史教会JIM你的基线。选择你佩戴的设备——步骤会随之变化。",
    hi: "कोई ऐप इंस्टॉल नहीं करना। फ़ोन पर एक ऑटोमेशन नीचे दिए पते पर रीडिंग भेजता है, और आपके डिवाइस का निर्यात पहले से दर्ज इतिहास से JIM को आपकी बेसलाइन सिखाता है। जो पहनते हैं उसे चुनें — कदम उसी के अनुसार बदलते हैं।",
    ar: "لا حاجة لتثبيت تطبيق. أتمتة على هاتفك ترسل القراءات إلى العنوان أدناه، وتصدير جهازك يعلّم JIM خط الأساس من السجل المسجّل مسبقًا. اختر ما ترتديه — تتغير الخطوات وفقًا له.",
  },
  "watch.address": {
    en: "Drip address (paste into the automation's URL field)",
    es: "Dirección de envío (pégala en el campo URL de la automatización)",
    fr: "Adresse d'envoi (à coller dans le champ URL de l'automatisation)",
    de: "Empfangsadresse (in das URL-Feld der Automatisierung einfügen)",
    pt: "Endereço de envio (cole no campo URL da automação)",
    it: "Indirizzo di invio (incollalo nel campo URL dell'automazione)",
    ja: "送信先アドレス（自動化のURL欄に貼り付け）",
    zh: "投递地址（粘贴到自动化的URL栏）",
    hi: "ड्रिप पता (ऑटोमेशन के URL फ़ील्ड में चिपकाएँ)",
    ar: "عنوان الإرسال (الصقه في حقل URL في الأتمتة)",
  },
  "watch.seed": {
    en: "Seed the baseline from your wearable's export",
    es: "Sembrar la línea base con la exportación de tu dispositivo",
    fr: "Amorcer la référence avec l'export de votre appareil",
    de: "Basislinie aus dem Export deines Geräts speisen",
    pt: "Semear a linha de base com a exportação do seu dispositivo",
    it: "Avvia la linea di base dall'esportazione del tuo dispositivo",
    ja: "ウェアラブルのエクスポートからベースラインを作成",
    zh: "用穿戴设备的导出建立基线",
    hi: "अपने डिवाइस के निर्यात से बेसलाइन बनाएँ",
    ar: "أنشئ خط الأساس من تصدير جهازك",
  },
  "watch.setup": {
    en: "Set it up (one time)", es: "Configúralo (una sola vez)",
    fr: "Configurez-le (une seule fois)", de: "Einrichten (einmalig)",
    pt: "Configure (uma única vez)", it: "Configuralo (una volta sola)",
    ja: "設定する（初回のみ）", zh: "设置（仅一次）",
    hi: "सेट करें (एक बार)", ar: "قم بالإعداد (مرة واحدة)",
  },
  "dev.bluetooth": {
    en: "Add Bluetooth device", es: "Añadir dispositivo Bluetooth",
    fr: "Ajouter un appareil Bluetooth", de: "Bluetooth-Gerät hinzufügen",
    pt: "Adicionar dispositivo Bluetooth",
    it: "Aggiungi dispositivo Bluetooth", ja: "Bluetooth機器を追加",
    zh: "添加蓝牙设备", hi: "ब्लूटूथ डिवाइस जोड़ें", ar: "أضف جهاز بلوتوث",
  },
  "dev.paired": {
    en: "paired", es: "emparejado", fr: "appairé", de: "gekoppelt",
    pt: "emparelhado", it: "associato", ja: "ペアリング済み", zh: "已配对",
    hi: "युग्मित", ar: "مقترن",
  },
  "dev.my": {
    en: "My devices", es: "Mis dispositivos", fr: "Mes appareils",
    de: "Meine Geräte", pt: "Os meus dispositivos", it: "I miei dispositivi",
    ja: "自分のデバイス", zh: "我的设备", hi: "मेरे डिवाइस", ar: "أجهزتي",
  },
  "dev.other": {
    en: "Other devices", es: "Otros dispositivos", fr: "Autres appareils",
    de: "Andere Geräte", pt: "Outros dispositivos", it: "Altri dispositivi",
    ja: "その他のデバイス", zh: "其他设备", hi: "अन्य डिवाइस",
    ar: "أجهزة أخرى",
  },
  "dev.connected": {
    en: "Connected", es: "Conectado", fr: "Connecté", de: "Verbunden",
    pt: "Conectado", it: "Connesso", ja: "接続済み", zh: "已连接",
    hi: "कनेक्टेड", ar: "متصل",
  },
  "dev.notconn": {
    en: "Not connected", es: "No conectado", fr: "Non connecté",
    de: "Nicht verbunden", pt: "Não conectado", it: "Non connesso",
    ja: "未接続", zh: "未连接", hi: "कनेक्ट नहीं", ar: "غير متصل",
  },
  "dev.details": {
    en: "Details", es: "Detalles", fr: "Détails", de: "Details",
    pt: "Detalhes", it: "Dettagli", ja: "詳細", zh: "详细信息",
    hi: "विवरण", ar: "التفاصيل",
  },
  "dev.kind.wearable": {
    en: "wearable", es: "vestible", fr: "portable", de: "Wearable",
    pt: "vestível", it: "indossabile", ja: "ウェアラブル", zh: "穿戴设备",
    hi: "पहनने योग्य", ar: "قابل للارتداء",
  },
  "dev.kind.glasses": {
    en: "glasses (Google, Meta)", es: "gafas (Google, Meta)",
    fr: "lunettes (Google, Meta)", de: "Brille (Google, Meta)",
    pt: "óculos (Google, Meta)", it: "occhiali (Google, Meta)",
    ja: "グラス（Google・Meta）", zh: "智能眼镜（Google、Meta）",
    hi: "चश्मा (Google, Meta)", ar: "نظارات (Google وMeta)",
  },
  "dev.kind.headset": {
    en: "AR/VR headset", es: "visor AR/VR", fr: "casque AR/VR",
    de: "AR/VR-Headset", pt: "headset AR/VR", it: "visore AR/VR",
    ja: "AR/VRヘッドセット", zh: "AR/VR头显", hi: "AR/VR हेडसेट",
    ar: "نظارة AR/VR",
  },
  "dev.kind.speaker": {
    en: "speaker", es: "altavoz", fr: "enceinte", de: "Lautsprecher",
    pt: "coluna", it: "altoparlante", ja: "スピーカー", zh: "音箱",
    hi: "स्पीकर", ar: "مكبر صوت",
  },
  "dev.kind.phone": {
    en: "phone", es: "teléfono", fr: "téléphone", de: "Telefon",
    pt: "telefone", it: "telefono", ja: "スマートフォン", zh: "手机",
    hi: "फ़ोन", ar: "هاتف",
  },
  "dev.kind.stationary": {
    en: "stationary (2-D)", es: "fijo (2-D)", fr: "fixe (2-D)",
    de: "stationär (2-D)", pt: "fixo (2-D)", it: "fisso (2-D)",
    ja: "据え置き（2D）", zh: "固定设备（2-D）", hi: "स्थिर (2-D)",
    ar: "ثابت (ثنائي الأبعاد)",
  },
  "dev.kind.spatial": {
    en: "spatial (3-D)", es: "espacial (3-D)", fr: "spatial (3-D)",
    de: "räumlich (3-D)", pt: "espacial (3-D)", it: "spaziale (3-D)",
    ja: "空間（3D）", zh: "空间设备（3-D）", hi: "स्थानिक (3-D)",
    ar: "مكاني (ثلاثي الأبعاد)",
  },
  "dev.kind.other": {
    en: "other", es: "otro", fr: "autre", de: "sonstiges", pt: "outro",
    it: "altro", ja: "その他", zh: "其他", hi: "अन्य", ar: "أخرى",
  },
  "lights.crash": {
    en: "crash watch", es: "vigilancia de caídas", fr: "veille d’incident",
    de: "Absturzwache", pt: "vigília de queda", it: "veglia di crisi",
    ja: "クラッシュウォッチ", zh: "跌倒监护", hi: "आपात निगरानी",
    ar: "مراقبة الطوارئ",
  },
  "lights.quiet": {
    en: "all quiet", es: "todo en calma", fr: "tout est calme",
    de: "alles ruhig", pt: "tudo calmo", it: "tutto tranquillo",
    ja: "異常なし", zh: "一切平静", hi: "सब शांत", ar: "كل شيء هادئ",
  },
  "lights.asking": {
    en: "asking for you", es: "preguntando por ti", fr: "vous demande",
    de: "fragt nach dir", pt: "a perguntar por si", it: "ti sta chiedendo",
    ja: "確認を求めています", zh: "正在等你确认", hi: "आपसे पूछ रहा है",
    ar: "يسأل عنك",
  },
  "lights.alarm": {
    en: "needs you now", es: "te necesita ahora", fr: "besoin de vous",
    de: "braucht dich jetzt", pt: "precisa de si agora",
    it: "ha bisogno di te ora", ja: "今すぐ対応が必要", zh: "现在需要你",
    hi: "अभी आपकी ज़रूरत है", ar: "يحتاجك الآن",
  },
  "lights.show": {
    en: "Show the Guardian lights", es: "Mostrar las luces del Guardián",
    fr: "Afficher les voyants du Gardien", de: "Wächter-Lichter zeigen",
    pt: "Mostrar as luzes do Guardião", it: "Mostra le luci del Guardiano",
    ja: "ガーディアンライトを表示", zh: "显示守护者指示灯",
    hi: "अभिभावक लाइटें दिखाएँ", ar: "إظهار أضواء الحارس",
  },
  "lights.hide": {
    en: "Minimize the Guardian lights", es: "Minimizar las luces del Guardián",
    fr: "Réduire les voyants du Gardien", de: "Wächter-Lichter minimieren",
    pt: "Minimizar as luzes do Guardião", it: "Riduci le luci del Guardiano",
    ja: "ガーディアンライトを最小化", zh: "最小化守护者指示灯",
    hi: "अभिभावक लाइटें छोटी करें", ar: "تصغير أضواء الحارس",
  },
  "lights.unreachable": {
    en: "The Guardian lights can’t reach the backend — press to retry",
    es: "Las luces del Guardián no alcanzan el servidor — pulsa para reintentar",
    fr: "Les voyants du Gardien n’atteignent pas le serveur — appuyez pour réessayer",
    de: "Die Wächter-Lichter erreichen das Backend nicht — zum Wiederholen drücken",
    pt: "As luzes do Guardião não alcançam o servidor — toque para tentar de novo",
    it: "Le luci del Guardiano non raggiungono il server — premi per riprovare",
    ja: "ガーディアンライトがバックエンドに届きません — 押して再試行",
    zh: "守护者指示灯无法连接后端 — 点按重试",
    hi: "अभिभावक लाइटें बैकएंड तक नहीं पहुँच पा रहीं — फिर से आज़माने के लिए दबाएँ",
    ar: "أضواء الحارس لا تصل إلى الخادم — اضغط لإعادة المحاولة",
  },
  "lights.ear": {
    en: "standing ear", es: "oído atento", fr: "oreille attentive",
    de: "wachsames Ohr", pt: "ouvido atento", it: "orecchio attento",
    ja: "見守りの耳", zh: "守护之耳", hi: "सतर्क कान", ar: "أذن يقظة",
  },
  "lights.ear.start": {
    en: "Start listening", es: "Empezar a escuchar",
    fr: "Commencer l’écoute", de: "Zuhören starten",
    pt: "Começar a escutar", it: "Inizia ad ascoltare",
    ja: "リスニングを開始", zh: "开始聆听", hi: "सुनना शुरू करें",
    ar: "بدء الاستماع",
  },
  "lights.ear.stop": {
    en: "Stop listening", es: "Dejar de escuchar", fr: "Arrêter l’écoute",
    de: "Zuhören beenden", pt: "Parar de escutar",
    it: "Smetti di ascoltare", ja: "リスニングを停止", zh: "停止聆听",
    hi: "सुनना बंद करें", ar: "إيقاف الاستماع",
  },
  "lights.ear.on": {
    en: "listening for the words that call for help",
    es: "escuchando las palabras que piden ayuda",
    fr: "à l’écoute des mots qui appellent à l’aide",
    de: "hört auf die Worte, die um Hilfe rufen",
    pt: "a escutar as palavras que pedem ajuda",
    it: "in ascolto delle parole che chiedono aiuto",
    ja: "助けを求める言葉を聞き取っています",
    zh: "正在聆听呼救的话语",
    hi: "मदद पुकारने वाले शब्दों को सुन रहा है",
    ar: "يستمع إلى الكلمات التي تطلب النجدة",
  },
  "lights.ear.refused": {
    en: "the microphone was refused — allow it in this browser and switch the ear back on",
    es: "el micrófono fue rechazado — permítelo en este navegador y vuelve a activar el oído",
    fr: "le microphone a été refusé — autorisez-le dans ce navigateur puis réactivez l’oreille",
    de: "das Mikrofon wurde verweigert — erlaube es in diesem Browser und schalte das Ohr wieder ein",
    pt: "o microfone foi recusado — permita-o neste navegador e volte a ligar o ouvido",
    it: "il microfono è stato rifiutato — consentilo in questo browser e riaccendi l’orecchio",
    ja: "マイクが拒否されました — ブラウザで許可してから、もう一度オンにしてください",
    zh: "麦克风被拒绝 — 请在此浏览器中允许后重新开启",
    hi: "माइक्रोफ़ोन अस्वीकार हुआ — इस ब्राउज़र में अनुमति दें और फिर से चालू करें",
    ar: "رُفض الميكروفون — اسمح به في هذا المتصفح ثم أعد تشغيل الأذن",
  },
  "lights.ear.asleep": {
    en: "this tab is in the background — the ear starts again when you come back to it",
    es: "esta pestaña está en segundo plano — el oído vuelve a empezar cuando regreses a ella",
    fr: "cet onglet est en arrière-plan — l’oreille reprend dès que vous y revenez",
    de: "dieser Tab läuft im Hintergrund — das Ohr beginnt wieder, sobald du zurückkommst",
    pt: "este separador está em segundo plano — o ouvido recomeça quando voltares a ele",
    it: "questa scheda è in secondo piano — l’orecchio riparte quando ci torni",
    ja: "このタブはバックグラウンドです — 戻ると耳はまた立ち上がります",
    zh: "此标签页在后台 — 回到它时耳朵会重新开始",
    hi: "यह टैब पृष्ठभूमि में है — जब आप लौटेंगे तो कान फिर से सुनने लगेगा",
    ar: "هذه التبويبة في الخلفية — تعود الأذن للاستماع حين ترجع إليها",
  },
  "lights.ear.none": {
    en: "this browser has no recogniser to listen with — nothing is being heard",
    es: "este navegador no tiene reconocedor con el que escuchar — no se está oyendo nada",
    fr: "ce navigateur n’a pas de reconnaisseur pour écouter — rien n’est entendu",
    de: "dieser Browser hat keinen Erkenner zum Zuhören — es wird nichts gehört",
    pt: "este navegador não tem reconhecedor para escutar — nada está a ser ouvido",
    it: "questo browser non ha un riconoscitore con cui ascoltare — non si sta sentendo nulla",
    ja: "このブラウザには音声認識がなく、聞き取りできません — 何も聞こえていません",
    zh: "此浏览器没有语音识别器可用 — 目前什么也听不到",
    hi: "इस ब्राउज़र में सुनने के लिए कोई पहचानकर्ता नहीं है — कुछ भी सुना नहीं जा रहा",
    ar: "لا يملك هذا المتصفح مُتعرِّفًا للاستماع — لا يُسمع شيء",
  },
  "feed.title": {
    en: "Feed", es: "Muro", fr: "Fil", de: "Feed", pt: "Fluxo",
    it: "Flusso", ja: "フィード", zh: "动态", hi: "फ़ीड", ar: "التدفّق",
  },
  "feed.sub": {
    en: "QRME's public stream, shown here",
    es: "el flujo público de QRME, mostrado aquí",
    fr: "le flux public de QRME, affiché ici",
    de: "QRMEs öffentlicher Stream, hier gezeigt",
    pt: "o fluxo público do QRME, mostrado aqui",
    it: "il flusso pubblico di QRME, mostrato qui",
    ja: "QRME の公開ストリームを、ここに表示しています",
    zh: "QRME 的公开流，在这里显示",
    hi: "QRME की सार्वजनिक धारा, यहाँ दिखाई गई",
    ar: "تدفّق QRME العلني، معروضًا هنا",
  },
  "feed.cannotpost": {
    en: "You cannot post from JIM. Publishing happens in QRME, under your own QRME identity.",
    es: "No puedes publicar desde JIM. Publicar ocurre en QRME, con tu propia identidad de QRME.",
    fr: "Vous ne pouvez pas publier depuis JIM. La publication se fait dans QRME, sous votre propre identité QRME.",
    de: "Aus JIM heraus kann nichts veröffentlicht werden. Das Veröffentlichen geschieht in QRME, unter deiner eigenen QRME-Identität.",
    pt: "Não podes publicar a partir do JIM. Publicar acontece no QRME, com a tua própria identidade QRME.",
    it: "Da JIM non si pubblica. La pubblicazione avviene in QRME, con la tua identità QRME.",
    ja: "JIM からは投稿できません。投稿は QRME で、あなた自身の QRME の身元で行います。",
    zh: "不能从 JIM 发布。发布发生在 QRME，用你自己的 QRME 身份。",
    hi: "आप JIM से पोस्ट नहीं कर सकते। प्रकाशन QRME में होता है, आपकी अपनी QRME पहचान से।",
    ar: "لا يمكنك النشر من JIM. النشر يجري في QRME، بهويتك الخاصة هناك.",
  },
  "feed.openinqrme": {
    en: "Open it in QRME", es: "Abrirlo en QRME", fr: "L'ouvrir dans QRME",
    de: "In QRME öffnen", pt: "Abrir no QRME", it: "Aprirlo in QRME",
    ja: "QRME で開く", zh: "在 QRME 中打开",
    hi: "QRME में खोलें", ar: "افتحه في QRME",
  },
  "feed.empty": {
    en: "Nothing public right now.", es: "Nada público ahora mismo.",
    fr: "Rien de public pour l'instant.", de: "Gerade nichts Öffentliches.",
    pt: "Nada público neste momento.", it: "Nulla di pubblico al momento.",
    ja: "いま公開されているものはありません。", zh: "此刻没有公开内容。",
    hi: "अभी कुछ भी सार्वजनिक नहीं।", ar: "لا شيء علني الآن.",
  },
  "feed.kind.video": {
    en: "Video", es: "Vídeo", fr: "Vidéo", de: "Video", pt: "Vídeo",
    it: "Video", ja: "動画", zh: "视频", hi: "वीडियो", ar: "فيديو",
  },
  "feed.kind.offsite": {
    en: "Elsewhere", es: "En otro sitio", fr: "Ailleurs", de: "Anderswo",
    pt: "Noutro sítio", it: "Altrove", ja: "よそのサイト", zh: "站外",
    hi: "अन्यत्र", ar: "في موقع آخر",
  },
  "feed.kind.room": {
    en: "Live room", es: "Sala en directo", fr: "Salon en direct",
    de: "Live-Raum", pt: "Sala em direto", it: "Sala dal vivo",
    ja: "ライブの部屋", zh: "直播房间", hi: "लाइव रूम", ar: "غرفة حيّة",
  },
  "feed.kind.desk": {
    en: "Desk", es: "Mostrador", fr: "Comptoir", de: "Theke", pt: "Balcão",
    it: "Banco", ja: "受付", zh: "服务台", hi: "डेस्क", ar: "المكتب",
  },
  "feed.kind.party": {
    en: "Watch party", es: "Sala de visionado", fr: "Séance partagée",
    de: "Watch-Party", pt: "Sessão conjunta", it: "Visione insieme",
    ja: "ウォッチパーティ", zh: "放映会", hi: "वॉच पार्टी", ar: "جلسة مشاهدة",
  },
  "feed.play": {
    en: "Play it", es: "Reproducirlo", fr: "Le lire", de: "Abspielen",
    pt: "Reproduzir", it: "Riproducilo", ja: "再生する", zh: "播放",
    hi: "चलाएँ", ar: "شغّله",
  },
  "feed.enter": {
    en: "Walk in", es: "Entrar", fr: "Entrer", de: "Hineingehen",
    pt: "Entrar", it: "Entrare", ja: "入る", zh: "走进去",
    hi: "अंदर जाएँ", ar: "ادخل",
  },
  "feed.ring": {
    en: "Ring the bell", es: "Tocar el timbre", fr: "Sonner",
    de: "Klingeln", pt: "Tocar a campainha", it: "Suonare il campanello",
    ja: "呼び鈴を鳴らす", zh: "按响门铃", hi: "घंटी बजाएँ",
    ar: "اقرع الجرس",
  },
  "feed.room.untitled": {
    en: "No topic", es: "Sin tema", fr: "Sans sujet", de: "Kein Thema",
    pt: "Sem tema", it: "Nessun argomento", ja: "話題なし", zh: "无话题",
    hi: "कोई विषय नहीं", ar: "بلا موضوع",
  },
  // "Previous", not "Back" — the same reasoning QRME's table carries: this
  // control moves one card up a stream, it does not leave a screen, and the
  // same English under two keys is what the desktop/phone guard catches.
  "feed.back": {
    en: "Previous", es: "Anterior", fr: "Précédent", de: "Vorheriges",
    pt: "Anterior", it: "Precedente", ja: "前へ", zh: "上一个",
    hi: "पिछला", ar: "السابق",
  },
  "feed.next": {
    en: "Next", es: "Siguiente", fr: "Suivant", de: "Weiter",
    pt: "Seguinte", it: "Avanti", ja: "次へ", zh: "下一个",
    hi: "अगला", ar: "التالي",
  },
  "nav.feed": {
    en: "Feed", es: "Muro", fr: "Fil", de: "Feed", pt: "Fluxo",
    it: "Flusso", ja: "フィード", zh: "动态", hi: "फ़ीड", ar: "التدفّق",
  },
  // The one tab of twenty-four with no row, found on a phone rather than by
  // anything here: the strip read `nav.presence` in Latin letters between
  // Community and Feed, in every language, since the screen shipped.
  //
  // Named for what it does rather than transliterated — `Presence.tsx` calls
  // itself "the coach that speaks first", and a tab called Presence tells a
  // person nothing about why they would press it.
  "nav.presence": {
    en: "Speaks first", es: "Habla primero", fr: "Parle en premier",
    de: "Spricht zuerst", pt: "Fala primeiro", it: "Parla per primo",
    ja: "先に話す", zh: "先开口", hi: "पहले बोलता है",
    ar: "يبدأ الحديث",
  },
  // The eight the general check found behind the tab: a whole Settings card
  // rendering its own key names, in every language, since it shipped.
  "set.saving": {
    en: "Saving…", es: "Guardando…", fr: "Enregistrement…", de: "Wird gespeichert…", pt: "A guardar…", it: "Salvataggio…", ja: "保存中…", zh: "保存中…", hi: "सहेजा जा रहा है…", ar: "جارٍ الحفظ…",
  },
  "set.saved": {
    en: "Saved ✓", es: "Guardado ✓", fr: "Enregistré ✓", de: "Gespeichert ✓", pt: "Guardado ✓", it: "Salvato ✓", ja: "保存しました ✓", zh: "已保存 ✓", hi: "सहेजा गया ✓", ar: "تم الحفظ ✓",
  },
  "set.key.save": {
    en: "Save key", es: "Guardar clave", fr: "Enregistrer la clé", de: "Schlüssel speichern", pt: "Guardar chave", it: "Salva chiave", ja: "キーを保存", zh: "保存密钥", hi: "कुंजी सहेजें", ar: "احفظ المفتاح",
  },
  "set.key.clear": {
    en: "Clear key", es: "Borrar clave", fr: "Effacer la clé", de: "Schlüssel löschen", pt: "Limpar chave", it: "Cancella chiave", ja: "キーを消去", zh: "清除密钥", hi: "कुंजी हटाएँ", ar: "امسح المفتاح",
  },
  "set.adapt.vaulted": {
    en: " · sealed in the vault", es: " · sellado en la bóveda", fr: " · scellé dans le coffre", de: " · im Tresor versiegelt", pt: " · selado no cofre", it: " · sigillato nel caveau", ja: " · 保管庫に封印済み", zh: " · 已封入保险库", hi: " · तिजोरी में सील", ar: " · مختوم في الخزنة",
  },
  "set.adapt.none": {
    en: "Nothing built yet.", es: "Todavía no se ha construido nada.", fr: "Rien de construit pour l'instant.", de: "Noch nichts aufgebaut.", pt: "Ainda nada construído.", it: "Ancora nulla di costruito.", ja: "まだ何も作られていません。", zh: "尚未构建任何内容。", hi: "अभी कुछ भी नहीं बना है।", ar: "لم يُبنَ شيء بعد.",
  },
  "set.cloud.not": {
    en: "Not contributing. Nothing from this account has gone to the shared model.", es: "Sin contribuir. Nada de esta cuenta ha ido al modelo compartido.", fr: "Aucune contribution. Rien de ce compte n'est allé au modèle partagé.", de: "Kein Beitrag. Von diesem Konto ist nichts an das gemeinsame Modell gegangen.", pt: "Sem contribuir. Nada desta conta foi para o modelo partilhado.", it: "Nessun contributo. Nulla di questo account è finito nel modello condiviso.", ja: "提供していません。このアカウントからは共有モデルへ何も送られていません。", zh: "未参与贡献。此账户的任何内容都未进入共享模型。", hi: "योगदान नहीं। इस खाते से कुछ भी साझा मॉडल में नहीं गया।", ar: "لا مساهمة. لم يذهب شيء من هذا الحساب إلى النموذج المشترك.",
  },
  "set.mail.save": {
    en: "Save mail settings", es: "Guardar ajustes de correo", fr: "Enregistrer les réglages e-mail", de: "Mail-Einstellungen speichern", pt: "Guardar definições de correio", it: "Salva impostazioni e-mail", ja: "メール設定を保存", zh: "保存邮件设置", hi: "मेल सेटिंग सहेजें", ar: "احفظ إعدادات البريد",
  },
  "set.mail.test.send": {
    en: "Send test email", es: "Enviar correo de prueba", fr: "Envoyer un e-mail de test", de: "Test-E-Mail senden", pt: "Enviar e-mail de teste", it: "Invia e-mail di prova", ja: "テストメールを送信", zh: "发送测试邮件", hi: "परीक्षण ईमेल भेजें", ar: "أرسل بريد اختبار",
  },
  "set.mail.sending": {
    en: "Sending…", es: "Enviando…", fr: "Envoi…", de: "Wird gesendet…", pt: "A enviar…", it: "Invio…", ja: "送信中…", zh: "发送中…", hi: "भेजा जा रहा है…", ar: "جارٍ الإرسال…",
  },
  "set.voice.device.label": {
    en: "Device voice", es: "Voz del dispositivo", fr: "Voix de l'appareil", de: "Gerätestimme", pt: "Voz do dispositivo", it: "Voce del dispositivo", ja: "端末の音声", zh: "设备语音", hi: "डिवाइस की आवाज़", ar: "صوت الجهاز",
  },
  "set.voice.save": {
    en: "Save voice settings", es: "Guardar ajustes de voz", fr: "Enregistrer les réglages vocaux", de: "Sprach-Einstellungen speichern", pt: "Guardar definições de voz", it: "Salva impostazioni vocali", ja: "音声設定を保存", zh: "保存语音设置", hi: "आवाज़ सेटिंग सहेजें", ar: "احفظ إعدادات الصوت",
  },
  "set.copy": {
    en: "Copy address", es: "Copiar dirección", fr: "Copier l'adresse", de: "Adresse kopieren", pt: "Copiar endereço", it: "Copia indirizzo", ja: "アドレスをコピー", zh: "复制地址", hi: "पता कॉपी करें", ar: "انسخ العنوان",
  },
  "set.copied": {
    en: "Copied ✓", es: "Copiado ✓", fr: "Copié ✓", de: "Kopiert ✓", pt: "Copiado ✓", it: "Copiato ✓", ja: "コピーしました ✓", zh: "已复制 ✓", hi: "कॉपी हो गया ✓", ar: "تم النسخ ✓",
  },
  "set.hook.none": {
    en: "Nothing has arrived yet — run the automation once by hand to test it.", es: "Todavía no ha llegado nada — ejecuta la automatización una vez a mano para probarla.", fr: "Rien n'est encore arrivé — lancez l'automatisation une fois à la main pour la tester.", de: "Noch ist nichts angekommen — führe die Automatisierung einmal von Hand aus, um sie zu testen.", pt: "Ainda não chegou nada — corra a automação uma vez à mão para a testar.", it: "Non è ancora arrivato nulla — esegui l'automazione una volta a mano per provarla.", ja: "まだ何も届いていません — 動作確認のため自動化を一度手動で実行してください。", zh: "尚未收到任何内容 — 手动运行一次自动化以进行测试。", hi: "अभी कुछ नहीं आया — जाँचने के लिए ऑटोमेशन एक बार हाथ से चलाएँ।", ar: "لم يصل شيء بعد — شغّل الأتمتة مرة يدويًا لاختبارها.",
  },
  "set.vigil.arm": {
    en: "Arm the vigil", es: "Activar la vigilia", fr: "Armer la veille", de: "Die Wache scharf stellen", pt: "Armar a vigília", it: "Attiva la veglia", ja: "見守りを有効にする", zh: "开启守夜", hi: "पहरा सक्रिय करें", ar: "تفعيل السهر",
  },
  "set.vigil.update": {
    en: "Update the vigil", es: "Actualizar la vigilia", fr: "Mettre à jour la veille", de: "Die Wache aktualisieren", pt: "Atualizar a vigília", it: "Aggiorna la veglia", ja: "見守りを更新する", zh: "更新守夜", hi: "पहरा अद्यतन करें", ar: "تحديث السهر",
  },
  "set.posture.offline": {
    en: "Offline — nothing leaves this host", es: "Sin conexión — nada sale de este host", fr: "Hors ligne — rien ne quitte cet hôte", de: "Offline — nichts verlässt diesen Host", pt: "Offline — nada sai deste host", it: "Offline — nulla lascia questo host", ja: "オフライン — このホストから何も出ません", zh: "离线 — 没有任何内容离开这台主机", hi: "ऑफ़लाइन — इस होस्ट से कुछ भी बाहर नहीं जाता", ar: "غير متصل — لا شيء يغادر هذا المضيف",
  },
  "set.posture.online": {
    en: "Online", es: "En línea", fr: "En ligne", de: "Online", pt: "Online", it: "Online", ja: "オンライン", zh: "在线", hi: "ऑनलाइन", ar: "متصل",
  },
  "set.posture.reach": {
    en: "This deployment can reach other machines.", es: "Este despliegue puede alcanzar otras máquinas.", fr: "Ce déploiement peut atteindre d'autres machines.", de: "Diese Installation kann andere Maschinen erreichen.", pt: "Esta instalação consegue alcançar outras máquinas.", it: "Questa installazione può raggiungere altre macchine.", ja: "この配備は他のマシンに到達できます。", zh: "此部署可以访问其他机器。", hi: "यह परिनियोजन अन्य मशीनों तक पहुँच सकता है।", ar: "يستطيع هذا النشر الوصول إلى أجهزة أخرى.",
  },
  "set.posture.refuse": {
    en: "Every path out of this host refuses any address that is not this machine or its own network.", es: "Toda salida de este host rechaza cualquier dirección que no sea esta máquina o su propia red.", fr: "Chaque sortie de cet hôte refuse toute adresse autre que cette machine ou son propre réseau.", de: "Jeder Weg aus diesem Host heraus weist jede Adresse ab, die nicht diese Maschine oder ihr eigenes Netz ist.", pt: "Todos os caminhos de saída deste host recusam qualquer endereço que não seja esta máquina ou a sua própria rede.", it: "Ogni via d'uscita da questo host rifiuta qualsiasi indirizzo che non sia questa macchina o la sua stessa rete.", ja: "このホストから出るすべての経路は、この端末またはその自身のネットワーク以外のアドレスを拒否します。", zh: "离开这台主机的每条路径都会拒绝除本机或其自身网络之外的任何地址。", hi: "इस होस्ट से बाहर जाने वाला हर रास्ता उस हर पते को अस्वीकार करता है जो यह मशीन या इसका अपना नेटवर्क नहीं है।", ar: "كل مسار خارج من هذا المضيف يرفض أي عنوان ليس هذا الجهاز أو شبكته الخاصة.",
  },
  "set.ft.title": {
    en: "A model shaped by you", es: "Un modelo moldeado por ti", fr: "Un modèle façonné par vous", de: "Ein von dir geformtes Modell", pt: "Um modelo moldado por ti", it: "Un modello plasmato da te", ja: "あなたが形づくるモデル", zh: "由你塑造的模型", hi: "आपके द्वारा ढाला गया मॉडल", ar: "نموذج شكّلته أنت",
  },
  "set.ft.sub": {
    en: "Trained on this device from your own turns. Weights, not a prompt — the difference is that this one keeps what it learned when the conversation ends.", es: "Entrenado en este dispositivo a partir de tus propios turnos. Pesos, no un prompt: la diferencia es que este conserva lo aprendido cuando termina la conversación.", fr: "Entraîné sur cet appareil à partir de vos propres échanges. Des poids, pas une consigne — la différence, c'est qu'il garde ce qu'il a appris quand la conversation se termine.", de: "Auf diesem Gerät aus deinen eigenen Beiträgen trainiert. Gewichte, kein Prompt — der Unterschied: dieses behält, was es gelernt hat, wenn das Gespräch endet.", pt: "Treinado neste dispositivo a partir dos teus próprios turnos. Pesos, não um prompt — a diferença é que este guarda o que aprendeu quando a conversa acaba.", it: "Addestrato su questo dispositivo dai tuoi turni. Pesi, non un prompt — la differenza è che questo conserva ciò che ha imparato quando la conversazione finisce.", ja: "この端末で、あなたの発言から学習します。プロンプトではなく重み——会話が終わっても学んだことが残るのが違いです。", zh: "在这台设备上，用你自己的对话训练。是权重而不是提示词——区别在于对话结束后它仍留着学到的东西。", hi: "इसी डिवाइस पर, आपकी अपनी बातचीत से प्रशिक्षित। यह वेट्स हैं, प्रॉम्प्ट नहीं — फ़र्क़ यह कि बातचीत ख़त्म होने पर भी सीखा हुआ बचा रहता है।", ar: "مُدرَّب على هذا الجهاز من مداخلاتك أنت. أوزان لا موجّه — والفرق أنّ هذا يحتفظ بما تعلّمه بعد انتهاء المحادثة.",
  },
  "set.ft.trained": {
    en: "Trained on {n} of your turns · {backend}", es: "Entrenado con {n} de tus turnos · {backend}", fr: "Entraîné sur {n} de vos échanges · {backend}", de: "Trainiert an {n} deiner Beiträge · {backend}", pt: "Treinado com {n} dos teus turnos · {backend}", it: "Addestrato su {n} dei tuoi turni · {backend}", ja: "あなたの発言 {n} 件で学習済み · {backend}", zh: "已用你的 {n} 轮对话训练 · {backend}", hi: "आपकी {n} बारियों पर प्रशिक्षित · {backend}", ar: "مُدرَّب على {n} من مداخلاتك · {backend}",
  },
  "set.ft.retrain": {
    en: "Train again", es: "Entrenar otra vez", fr: "Réentraîner", de: "Erneut trainieren", pt: "Treinar de novo", it: "Riaddestra", ja: "再学習", zh: "重新训练", hi: "फिर से प्रशिक्षित करें", ar: "درِّب مجددًا",
  },
  "set.ft.use": {
    en: "Answer me with it", es: "Respóndeme con él", fr: "Réponds-moi avec", de: "Damit antworten", pt: "Responde-me com ele", it: "Rispondimi con questo", ja: "これで答える", zh: "用它来回答我", hi: "इसी से मुझे उत्तर दें", ar: "أجبني به",
  },
  "set.ft.offswitch": {
    en: "Switch it off and the ordinary model answers instead. What it learned is kept, not discarded.", es: "Desactívalo y responderá el modelo normal. Lo aprendido se conserva, no se descarta.", fr: "Désactivez-le et le modèle ordinaire répond à la place. Ce qu'il a appris est conservé, pas jeté.", de: "Schalte es aus, und das gewöhnliche Modell antwortet. Das Gelernte bleibt erhalten, es wird nicht verworfen.", pt: "Desliga-o e responde o modelo normal. O que aprendeu fica guardado, não é deitado fora.", it: "Spegnilo e risponde il modello ordinario. Ciò che ha imparato resta, non viene buttato.", ja: "切ると通常のモデルが答えます。学んだ内容は破棄されず保持されます。", zh: "关掉它，就由普通模型来回答。它学到的会保留，不会丢弃。", hi: "इसे बंद कर दें तो सामान्य मॉडल उत्तर देगा। सीखा हुआ रखा जाता है, मिटाया नहीं जाता।", ar: "أطفئه فيجيبك النموذج العادي. ما تعلّمه يُحفَظ ولا يُمحى.",
  },
  "set.ft.none": {
    en: "Nothing trained yet. It needs a stretch of conversation to learn from first.", es: "Todavía no hay nada entrenado. Primero necesita un tramo de conversación del que aprender.", fr: "Rien d'entraîné pour l'instant. Il lui faut d'abord un peu de conversation dont apprendre.", de: "Noch nichts trainiert. Es braucht zuerst ein Stück Gespräch, aus dem es lernen kann.", pt: "Ainda nada treinado. Precisa primeiro de um bocado de conversa de onde aprender.", it: "Ancora niente di addestrato. Serve prima un po' di conversazione da cui imparare.", ja: "まだ学習していません。まず学ぶだけの会話が必要です。", zh: "还没有训练过。它需要先有一段可供学习的对话。", hi: "अभी कुछ प्रशिक्षित नहीं। पहले सीखने लायक़ बातचीत चाहिए।", ar: "لا شيء مُدرَّب بعد. يحتاج أولًا إلى قدر من الحديث ليتعلّم منه.",
  },
  "set.ft.train": {
    en: "Train it on me", es: "Entrénalo conmigo", fr: "L'entraîner sur moi", de: "Auf mich trainieren", pt: "Treiná-lo em mim", it: "Addestralo su di me", ja: "私で学習させる", zh: "用我来训练它", hi: "इसे मुझ पर प्रशिक्षित करें", ar: "درِّبه عليّ",
  },
  // And the signup error, which a person meets at the worst moment to be
  // shown an identifier: mid-form, having mistyped, being told `onb.password
  // .mismatch`.
  "onb.show": {
    en: "Show", es: "Mostrar", fr: "Afficher", de: "Anzeigen", pt: "Mostrar", it: "Mostra", ja: "表示", zh: "显示", hi: "दिखाएँ", ar: "أظهر",
  },
  "onb.hide": {
    en: "Hide", es: "Ocultar", fr: "Masquer", de: "Ausblenden", pt: "Ocultar", it: "Nascondi", ja: "非表示", zh: "隐藏", hi: "छिपाएँ", ar: "أخفِ",
  },
  "onb.creating": {
    en: "Creating…", es: "Creando…", fr: "Création…", de: "Wird erstellt…", pt: "A criar…", it: "Creazione…", ja: "作成中…", zh: "创建中…", hi: "बनाया जा रहा है…", ar: "جارٍ الإنشاء…",
  },
  "onb.verify": {
    en: "Verify & get started", es: "Verificar y empezar", fr: "Vérifier et commencer", de: "Bestätigen und loslegen", pt: "Verificar e começar", it: "Verifica e inizia", ja: "確認して始める", zh: "验证并开始", hi: "सत्यापित करें और शुरू करें", ar: "تحقّق وابدأ",
  },
  "onb.checking": {
    en: "Checking…", es: "Comprobando…", fr: "Vérification…", de: "Wird geprüft…", pt: "A verificar…", it: "Verifica…", ja: "確認中…", zh: "检查中…", hi: "जाँचा जा रहा है…", ar: "جارٍ التحقق…",
  },
  "onb.signing": {
    en: "Signing in…", es: "Iniciando sesión…", fr: "Connexion…", de: "Wird angemeldet…", pt: "A iniciar sessão…", it: "Accesso…", ja: "サインイン中…", zh: "登录中…", hi: "साइन इन हो रहा है…", ar: "جارٍ تسجيل الدخول…",
  },
  "onb.setpass": {
    en: "Set new password", es: "Establecer nueva contraseña", fr: "Définir un nouveau mot de passe", de: "Neues Passwort festlegen", pt: "Definir nova palavra-passe", it: "Imposta nuova password", ja: "新しいパスワードを設定", zh: "设置新密码", hi: "नया पासवर्ड सेट करें", ar: "عيّن كلمة مرور جديدة",
  },
  "onb.resetting": {
    en: "Resetting…", es: "Restableciendo…", fr: "Réinitialisation…", de: "Wird zurückgesetzt…", pt: "A repor…", it: "Reimpostazione…", ja: "リセット中…", zh: "重置中…", hi: "रीसेट हो रहा है…", ar: "جارٍ إعادة التعيين…",
  },
  "onb.password.mismatch": {
    en: "Those two do not match.", es: "Esas dos no coinciden.", fr: "Ces deux-là ne correspondent pas.", de: "Die beiden stimmen nicht überein.", pt: "Essas duas não coincidem.", it: "Le due non coincidono.", ja: "この二つが一致していません。", zh: "这两个不一致。", hi: "ये दोनों मेल नहीं खाते।", ar: "هاتان غير متطابقتين.",
  },
  "presence.notice.drift": {
    en: "Your {metric} has been sitting outside your usual for {days} days. Not an alarm — I just noticed.", es: "Tu {metric} lleva {days} días fuera de lo habitual en ti. No es una alarma — simplemente lo noté.", fr: "Ton {metric} sort de ton habituel depuis {days} jours. Ce n'est pas une alerte — je l'ai juste remarqué.", de: "Dein {metric} liegt seit {days} Tagen außerhalb deines Üblichen. Kein Alarm — mir ist es nur aufgefallen.", pt: "O teu {metric} está fora do teu habitual há {days} dias. Não é um alarme — só reparei.", it: "Il tuo {metric} è fuori dal tuo solito da {days} giorni. Non è un allarme — l'ho solo notato.", ja: "{metric}がいつもの範囲を{days}日外れています。警報ではなく、気づいただけです。", zh: "你的{metric}已经连续{days}天不在你平常的范围里。这不是警报，只是我注意到了。", hi: "आपका {metric} पिछले {days} दिनों से आपके सामान्य से बाहर है। यह अलार्म नहीं — मैंने बस ध्यान दिया।", ar: "ظلّ {metric} خارج معدّلك المعتاد {days} أيام. ليس إنذارًا — لاحظت ذلك فقط.",
  },
  "presence.notice.mood": {
    en: "Three check-ins in a row on the low side. I am not going to make a thing of it, but I am here.", es: "Tres registros seguidos por lo bajo. No voy a hacer un drama, pero aquí estoy.", fr: "Trois relevés d'affilée plutôt bas. Je n'en fais pas une affaire, mais je suis là.", de: "Drei Check-ins hintereinander eher niedrig. Ich mache keine Sache daraus, aber ich bin da.", pt: "Três registos seguidos em baixo. Não vou fazer disto um caso, mas estou aqui.", it: "Tre check-in di fila verso il basso. Non ne faccio un caso, ma ci sono.", ja: "チェックインが3回続けて低めでした。大げさにはしませんが、ここにいます。", zh: "连着三次记录都偏低。我不打算小题大做，但我在。", hi: "लगातार तीन चेक-इन कम रहे। मैं इसका मुद्दा नहीं बनाऊँगा, पर मैं यहाँ हूँ।", ar: "ثلاث تسجيلات متتالية منخفضة. لن أضخّم الأمر، لكنّي هنا.",
  },
  "presence.nudge.goal": {
    en: "That {area} goal has not moved in {days} days. Do you want to make it smaller, or let it go?", es: "Ese objetivo de {area} lleva {days} días sin moverse. ¿Lo hacemos más pequeño o lo sueltas?", fr: "Cet objectif de {area} n'a pas bougé depuis {days} jours. Le réduire, ou le lâcher ?", de: "Das Ziel in {area} bewegt sich seit {days} Tagen nicht. Kleiner machen — oder loslassen?", pt: "Esse objetivo de {area} não mexe há {days} dias. Queres torná-lo mais pequeno ou largá-lo?", it: "Quell'obiettivo di {area} è fermo da {days} giorni. Vuoi rimpicciolirlo o lasciarlo andare?", ja: "{area}の目標が{days}日動いていません。小さくしますか、それとも手放しますか。", zh: "那个{area}目标已经{days}天没动了。是把它改小，还是放下它？", hi: "{area} का वह लक्ष्य {days} दिनों से नहीं हिला। इसे छोटा करें, या छोड़ दें?", ar: "لم يتحرّك هدف {area} منذ {days} أيام. أتريد تصغيره أم تركه؟",
  },
  "presence.nudge.followup": {
    en: "I gave you something for {condition} and never heard back. Did it help?", es: "Te di algo para {condition} y nunca supe nada más. ¿Sirvió?", fr: "Je t'ai donné quelque chose pour {condition} et je n'ai jamais eu de retour. Est-ce que ça a aidé ?", de: "Ich habe dir etwas für {condition} gegeben und nie wieder davon gehört. Hat es geholfen?", pt: "Dei-te algo para {condition} e nunca mais soube. Ajudou?", it: "Ti ho dato qualcosa per {condition} e non ho più saputo nulla. Ha aiutato?", ja: "{condition}のために何かをお伝えしましたが、その後のお返事をいただいていません。役に立ちましたか。", zh: "我给过你针对{condition}的建议，一直没收到回复。它有用吗？", hi: "मैंने आपको {condition} के लिए कुछ दिया था और फिर कोई जवाब नहीं मिला। क्या उससे मदद हुई?", ar: "أعطيتك شيئًا من أجل {condition} ولم يصلني ردّ. هل نفع؟",
  },
  "presence.celebrate.streak": {
    en: "{days} days on {habit}. That is not luck any more.", es: "{days} días con {habit}. Eso ya no es suerte.", fr: "{days} jours sur {habit}. Ce n'est plus de la chance.", de: "{days} Tage {habit}. Das ist kein Zufall mehr.", pt: "{days} dias em {habit}. Isso já não é sorte.", it: "{days} giorni su {habit}. Non è più fortuna.", ja: "{habit}を{days}日続けています。もう偶然ではありません。", zh: "{habit}坚持了{days}天。这已经不是运气了。", hi: "{habit} पर {days} दिन। यह अब संयोग नहीं है।", ar: "{days} يومًا على {habit}. لم يعد هذا حظًّا.",
  },
  "presence.celebrate.goal": {
    en: "You finished it. I watched that one take a while.", es: "Lo terminaste. Vi lo que tardó.", fr: "Tu l'as fini. J'ai vu le temps que ça a pris.", de: "Du hast es abgeschlossen. Ich habe gesehen, wie lange das gedauert hat.", pt: "Terminaste. Vi o tempo que aquilo levou.", it: "L'hai finito. Ho visto quanto ci è voluto.", ja: "やり遂げましたね。時間がかかったのを見ていました。", zh: "你完成了。我看着这件事花了不少时间。", hi: "आपने इसे पूरा किया। मैंने देखा कि इसमें समय लगा।", ar: "أنجزته. رأيت كم استغرق ذلك.",
  },
  "presence.curious.area": {
    en: "Tell me something about your {area} that I would not know from the numbers.", es: "Cuéntame algo de tu {area} que los números no me digan.", fr: "Dis-moi sur ton {area} quelque chose que les chiffres ne me diraient pas.", de: "Erzähl mir etwas über dein {area}, das die Zahlen mir nicht sagen.", pt: "Conta-me algo do teu {area} que os números não digam.", it: "Raccontami del tuo {area} qualcosa che i numeri non mi direbbero.", ja: "{area}について、数字ではわからないことを教えてください。", zh: "跟我说说你{area}里数字看不出来的事。", hi: "अपने {area} के बारे में कुछ बताइए जो आँकड़ों से पता न चले।", ar: "أخبرني عن {area} شيئًا لا تقوله الأرقام.",
  },
  "presence.curious.open": {
    en: "What is the thing you keep meaning to think about and keep not thinking about?", es: "¿Qué es eso en lo que siempre piensas pensar y nunca piensas?", fr: "Quelle est la chose que tu comptes toujours penser et que tu ne penses jamais ?", de: "Was ist die Sache, über die du immer nachdenken willst und nie nachdenkst?", pt: "O que é aquilo em que andas sempre a tencionar pensar e nunca pensas?", it: "Qual è la cosa a cui pensi sempre di pensare e a cui non pensi mai?", ja: "考えようと思いながら、ずっと考えずにいることは何ですか。", zh: "有什么事你一直想想想，却一直没想？", hi: "वह कौन-सी बात है जिसके बारे में आप सोचना चाहते हैं और सोचते नहीं?", ar: "ما الشيء الذي تنوي التفكير فيه دائمًا ولا تفكّر فيه؟",
  },
  "presence.quiet.nothing": {
    en: "Nothing from me today. Everything I watch is where it usually is.", es: "Hoy nada de mi parte. Todo lo que vigilo está donde suele estar.", fr: "Rien de moi aujourd'hui. Tout ce que je surveille est là où c'est d'habitude.", de: "Heute nichts von mir. Alles, was ich beobachte, ist da, wo es sonst ist.", pt: "Hoje nada da minha parte. Tudo o que vigio está onde costuma estar.", it: "Oggi niente da parte mia. Tutto ciò che seguo è dov'è di solito.", ja: "今日は私からは何もありません。見ているものはどれもいつもの場所です。", zh: "今天我这边没有事。我看着的一切都在平常的位置。", hi: "आज मेरी ओर से कुछ नहीं। जो कुछ मैं देखता हूँ, सब सामान्य जगह पर है।", ar: "لا شيء منّي اليوم. كلّ ما أراقبه في مكانه المعتاد.",
  },
  "presence.quiet.held": {
    en: "I have something, but it is quiet hours. It will keep.", es: "Tengo algo, pero son horas de silencio. Puede esperar.", fr: "J'ai quelque chose, mais ce sont les heures calmes. Ça peut attendre.", de: "Ich hätte etwas, aber es sind Ruhezeiten. Das hat Zeit.", pt: "Tenho algo, mas são horas de silêncio. Pode esperar.", it: "Ho una cosa, ma sono ore di silenzio. Può aspettare.", ja: "お伝えしたいことはありますが、静かな時間です。あとにします。", zh: "我有话要说，但现在是安静时段。可以等。", hi: "मेरे पास कुछ है, पर यह शांत समय है। यह रुक सकता है।", ar: "لديّ شيء، لكنها ساعات هدوء. يمكنه الانتظار.",
  },
  "presence.tab": {
    en: "Presence", es: "Presencia", fr: "Présence", de: "Präsenz", pt: "Presença", it: "Presenza", ja: "そばにいる", zh: "陪伴", hi: "उपस्थिति", ar: "الحضور",
  },
  "presence.sub": {
    en: "what it noticed, unprompted", es: "lo que notó, sin que se lo pidieran", fr: "ce qu'il a remarqué, sans qu'on lui demande", de: "was ihm aufgefallen ist, ungefragt", pt: "o que reparou, sem lhe pedirem", it: "cosa ha notato, senza che glielo chiedessero", ja: "たずねられる前に気づいたこと", zh: "没人问，它自己注意到的", hi: "बिना पूछे उसने क्या देखा", ar: "ما لاحظه دون أن يُسأل",
  },
  "presence.what": {
    en: "What this is", es: "Qué es esto", fr: "Ce que c'est", de: "Was das ist", pt: "O que isto é", it: "Che cos'è", ja: "これは何か", zh: "这是什么", hi: "यह क्या है", ar: "ما هذا",
  },
  "presence.will.not": {
    en: "What it will not be", es: "Lo que no va a ser", fr: "Ce qu'il ne sera pas", de: "Was es nicht sein wird", pt: "O que não vai ser", it: "Ciò che non sarà", ja: "これがならないもの", zh: "它不会成为的", hi: "यह क्या नहीं बनेगा", ar: "ما لن يكونه",
  },
  "presence.baseline": {
    en: "Six areas", es: "Seis áreas", fr: "Six domaines", de: "Sechs Bereiche", pt: "Seis áreas", it: "Sei aree", ja: "6つの領域", zh: "六个方面", hi: "छह क्षेत्र", ar: "ستّة مجالات",
  },
  "presence.today": {
    en: "Today", es: "Hoy", fr: "Aujourd'hui", de: "Heute", pt: "Hoje", it: "Oggi", ja: "今日", zh: "今天", hi: "आज", ar: "اليوم",
  },
  "presence.deepen": {
    en: "Say more", es: "Decir más", fr: "En dire plus", de: "Mehr sagen", pt: "Dizer mais", it: "Dire di più", ja: "もっと話す", zh: "多说一点", hi: "और बताएँ", ar: "قل المزيد",
  },
  "presence.offline": {
    en: "decided here, with no network and no model", es: "decidido aquí, sin red ni modelo", fr: "décidé ici, sans réseau ni modèle", de: "hier entschieden, ohne Netz und ohne Modell", pt: "decidido aqui, sem rede nem modelo", it: "deciso qui, senza rete né modello", ja: "ネットワークもモデルも使わず、ここで決めています", zh: "在本机决定，不用网络也不用模型", hi: "यहीं तय हुआ — न नेटवर्क, न मॉडल", ar: "تقرَّر هنا، بلا شبكة ولا نموذج",
  },
  "presence.reach": {
    en: "People who are not me", es: "Personas que no soy yo", fr: "Des gens qui ne sont pas moi", de: "Menschen, die nicht ich sind", pt: "Pessoas que não sou eu", it: "Persone che non sono io", ja: "私ではない人たち", zh: "不是我的人", hi: "वे लोग जो मैं नहीं हूँ", ar: "أشخاص ليسوا أنا",
  },
  "presence.surfaces": {
    en: "Where I speak", es: "Dónde hablo", fr: "Où je parle", de: "Wo ich spreche", pt: "Onde falo", it: "Dove parlo", ja: "どこで話すか", zh: "我在哪儿说话", hi: "मैं कहाँ बोलूँ", ar: "أين أتحدّث",
  },

  // The nine surfaces, as words rather than as the names the wire uses. The
  // picker rendered `s.surface` straight onto its buttons, so the choice
  // between "phone_screen" and "desktop_screen" was a choice between two
  // identifiers — in every language, English included. The note under each
  // is here for the same reason: it arrives from the server in English and
  // could only ever be English.
  //
  // Keyed off `SURFACES` in `jim/presence.py`, which is the list the buttons
  // are built from, and guarded against it.
  "surface.earbuds": {
    en: "Earbuds", es: "Auriculares intraaurales", fr: "Écouteurs intra-auriculaires", de: "Ohrhörer", pt: "Auriculares intra-auriculares", it: "Auricolari", ja: "イヤホン", zh: "入耳式耳机", hi: "ईयरबड्स", ar: "سمّاعات الأذن",
  },
  "surface.earbuds.note": {
    en: "in your ear, nobody else's", es: "en tu oído, en el de nadie más", fr: "dans votre oreille, dans celle de personne d'autre", de: "in deinem Ohr, in keinem anderen", pt: "no seu ouvido, no de mais ninguém", it: "nel tuo orecchio, in quello di nessun altro", ja: "あなたの耳だけに、ほかの誰にも聞こえません", zh: "只在你耳朵里，别人听不到", hi: "आपके कान में, किसी और के नहीं", ar: "في أذنك وحدك، لا في أذن أحد سواك",
  },
  "surface.headphones": {
    en: "Headphones", es: "Auriculares", fr: "Casque audio", de: "Kopfhörer", pt: "Auscultadores", it: "Cuffie", ja: "ヘッドホン", zh: "头戴式耳机", hi: "हेडफ़ोन", ar: "سمّاعات الرأس",
  },
  "surface.headphones.note": {
    en: "in your ear, nobody else's", es: "en tu oído, en el de nadie más", fr: "dans votre oreille, dans celle de personne d'autre", de: "in deinem Ohr, in keinem anderen", pt: "no seu ouvido, no de mais ninguém", it: "nel tuo orecchio, in quello di nessun altro", ja: "あなたの耳だけに、ほかの誰にも聞こえません", zh: "只在你耳朵里，别人听不到", hi: "आपके कान में, किसी और के नहीं", ar: "في أذنك وحدك، لا في أذن أحد سواك",
  },
  "surface.phone_screen": {
    en: "Phone screen", es: "Pantalla del teléfono", fr: "Écran du téléphone", de: "Handybildschirm", pt: "Ecrã do telemóvel", it: "Schermo del telefono", ja: "スマホの画面", zh: "手机屏幕", hi: "फ़ोन की स्क्रीन", ar: "شاشة الهاتف",
  },
  "surface.phone_screen.note": {
    en: "text you read, at your own speed", es: "texto que lees a tu propio ritmo", fr: "du texte que vous lisez à votre rythme", de: "Text, den du in deinem Tempo liest", pt: "texto que lê ao seu ritmo", it: "testo che leggi al tuo ritmo", ja: "自分のペースで読める文字", zh: "你按自己的节奏读的文字", hi: "पाठ, जिसे आप अपनी गति से पढ़ें", ar: "نصّ تقرأه على مهلك",
  },
  "surface.watch": {
    en: "Watch", es: "Reloj", fr: "Montre", de: "Uhr", pt: "Relógio", it: "Orologio", ja: "腕時計", zh: "手表", hi: "घड़ी", ar: "الساعة",
  },
  "surface.watch.note": {
    en: "a glance and a tap, nothing long", es: "un vistazo y un toque, nada largo", fr: "un coup d'œil et une tape, rien de long", de: "ein Blick und ein Tippen, nichts Langes", pt: "um relance e um toque, nada longo", it: "un'occhiata e un tocco, niente di lungo", ja: "ちらっと見て、ひと触れ。長い話はしません", zh: "一瞥、一点，不说长话", hi: "एक नज़र और एक टैप, कुछ लंबा नहीं", ar: "نظرة ولمسة، لا شيء طويل",
  },
  "surface.desktop_screen": {
    en: "Desktop screen", es: "Pantalla del ordenador", fr: "Écran d'ordinateur", de: "Computerbildschirm", pt: "Ecrã do computador", it: "Schermo del computer", ja: "パソコンの画面", zh: "电脑屏幕", hi: "कंप्यूटर की स्क्रीन", ar: "شاشة الحاسوب",
  },
  "surface.desktop_screen.note": {
    en: "a screen other people walk past", es: "una pantalla por delante de la que pasa otra gente", fr: "un écran devant lequel d'autres passent", de: "ein Bildschirm, an dem andere vorbeigehen", pt: "um ecrã por onde outras pessoas passam", it: "uno schermo davanti a cui passano altri", ja: "ほかの人が通りかかる画面", zh: "别人会从旁边走过的屏幕", hi: "एक स्क्रीन जिसके पास से दूसरे गुज़रते हैं", ar: "شاشة يمرّ بها آخرون",
  },
  "surface.speaker": {
    en: "Speaker", es: "Altavoz", fr: "Enceinte", de: "Lautsprecher", pt: "Coluna", it: "Altoparlante", ja: "スピーカー", zh: "音箱", hi: "स्पीकर", ar: "مكبّر الصوت",
  },
  "surface.speaker.note": {
    en: "out loud, into a room", es: "en voz alta, en una habitación", fr: "à voix haute, dans une pièce", de: "laut, in einen Raum hinein", pt: "em voz alta, para a sala", it: "ad alta voce, in una stanza", ja: "部屋に向かって声に出します", zh: "出声说给整个房间", hi: "ज़ोर से, पूरे कमरे में", ar: "بصوت مسموع في الغرفة",
  },
  "surface.glasses": {
    en: "Glasses", es: "Gafas", fr: "Lunettes", de: "Brille", pt: "Óculos", it: "Occhiali", ja: "スマートグラス", zh: "智能眼镜", hi: "चश्मा", ar: "النظّارات",
  },
  "surface.glasses.note": {
    en: "audio in your ear, text in your view — and a camera other people did not agree to", es: "audio en tu oído, texto en tu vista, y una cámara que los demás no consintieron", fr: "du son dans votre oreille, du texte dans votre champ de vision — et une caméra que les autres n'ont pas acceptée", de: "Ton in deinem Ohr, Text in deinem Blickfeld — und eine Kamera, der andere nicht zugestimmt haben", pt: "áudio no seu ouvido, texto no seu campo de visão — e uma câmara que os outros não aceitaram", it: "audio nel tuo orecchio, testo nel tuo campo visivo — e una telecamera a cui gli altri non hanno acconsentito", ja: "耳に音、視界に文字 — そして、ほかの人が同意していないカメラ", zh: "声音在你耳边，文字在你视野里 — 还有一台别人没同意过的摄像头", hi: "आवाज़ आपके कान में, पाठ आपकी दृष्टि में — और एक कैमरा जिस पर दूसरों ने सहमति नहीं दी", ar: "صوت في أذنك ونصّ في مجال نظرك — وكاميرا لم يوافق عليها الآخرون",
  },
  "surface.ar": {
    en: "AR", es: "RA", fr: "RA", de: "AR", pt: "RA", it: "RA", ja: "AR（拡張現実）", zh: "增强现实", hi: "एआर", ar: "الواقع المعزَّز",
  },
  "surface.ar.note": {
    en: "over the room you are actually in", es: "sobre la habitación en la que estás de verdad", fr: "par-dessus la pièce où vous êtes réellement", de: "über den Raum gelegt, in dem du wirklich bist", pt: "sobre a sala onde está realmente", it: "sopra la stanza in cui sei davvero", ja: "いま実際にいる部屋の上に重ねて", zh: "叠在你真正身处的房间上", hi: "उसी कमरे के ऊपर जिसमें आप सचमुच हैं", ar: "فوق الغرفة التي أنت فيها فعلًا",
  },
  "surface.vr": {
    en: "VR", es: "RV", fr: "RV", de: "VR", pt: "RV", it: "RV", ja: "VR（仮想現実）", zh: "虚拟现实", hi: "वीआर", ar: "الواقع الافتراضي",
  },
  "surface.vr.note": {
    en: "a room that is only yours while you are in it", es: "una habitación que es solo tuya mientras estás en ella", fr: "une pièce qui n'est qu'à vous tant que vous y êtes", de: "ein Raum, der dir allein gehört, solange du darin bist", pt: "uma sala que é só sua enquanto lá estiver", it: "una stanza che è solo tua finché ci sei dentro", ja: "入っているあいだ、あなただけの部屋", zh: "你在里面时，只属于你的房间", hi: "एक कमरा जो तब तक सिर्फ़ आपका है जब तक आप उसमें हैं", ar: "غرفة لك وحدك ما دمت فيها",
  },

  // The six areas the baseline is drawn across, and the four words it uses
  // for standing. Both rendered raw beside the surfaces — `mental_health`
  // with its underscore swapped for a space, which is English wearing a
  // small disguise.
  "area.mental_health": {
    en: "Mental health", es: "Salud mental", fr: "Santé mentale", de: "Psychische Gesundheit", pt: "Saúde mental", it: "Salute mentale", ja: "こころの健康", zh: "心理健康", hi: "मानसिक स्वास्थ्य", ar: "الصحة النفسية",
  },
  "area.health_fitness": {
    en: "Health and fitness", es: "Salud y forma física", fr: "Santé et forme", de: "Gesundheit und Fitness", pt: "Saúde e forma física", it: "Salute e forma fisica", ja: "からだと運動", zh: "健康与体能", hi: "स्वास्थ्य और फ़िटनेस", ar: "الصحة واللياقة",
  },
  "area.career": {
    en: "Work", es: "Trabajo", fr: "Travail", de: "Beruf", pt: "Trabalho", it: "Lavoro", ja: "仕事", zh: "工作", hi: "काम", ar: "العمل",
  },
  // `zh` here is the shells' 财务 rather than 金钱, which this row was first
  // written with. Both are correct Chinese for money; only one of them is
  // what an iPhone already says under `life.money`, and a console and a phone
  // disagreeing about a word in one language out of ten is the kind of split
  // nobody finds by reading.
  "area.finance": {
    en: "Money", es: "Dinero", fr: "Argent", de: "Geld", pt: "Dinheiro", it: "Denaro", ja: "お金", zh: "财务", hi: "पैसा", ar: "المال",
  },
  "area.relationships": {
    en: "Relationships", es: "Relaciones", fr: "Relations", de: "Beziehungen", pt: "Relações", it: "Relazioni", ja: "人との関係", zh: "人际关系", hi: "रिश्ते", ar: "العلاقات",
  },
  "area.personal_growth": {
    en: "Personal growth", es: "Crecimiento personal", fr: "Développement personnel", de: "Persönliche Entwicklung", pt: "Crescimento pessoal", it: "Crescita personale", ja: "自分の成長", zh: "个人成长", hi: "व्यक्तिगत विकास", ar: "النموّ الشخصي",
  },
  "standing.steady": {
    en: "Steady", es: "Estable", fr: "Stable", de: "Stabil", pt: "Estável", it: "Stabile", ja: "安定", zh: "平稳", hi: "स्थिर", ar: "مستقرّ",
  },
  "standing.drifting": {
    en: "Drifting", es: "A la deriva", fr: "À la dérive", de: "Driftet", pt: "À deriva", it: "Alla deriva", ja: "ぶれている", zh: "有偏移", hi: "भटक रहा", ar: "ينحرف",
  },
  "standing.thin": {
    en: "Thin", es: "Con pocos datos", fr: "Peu de données", de: "Dünn", pt: "Com poucos dados", it: "Con pochi dati", ja: "手がかりが少ない", zh: "线索不足", hi: "जानकारी कम", ar: "قليل الدلائل",
  },
  "standing.unknown": {
    en: "Unknown", es: "Sin datos", fr: "Inconnu", de: "Unbekannt", pt: "Sem dados", it: "Sconosciuto", ja: "まだ分かりません", zh: "尚不清楚", hi: "अभी पता नहीं", ar: "غير معروف",
  },
  "presence.aloud.held": {
    en: "Held back — this surface is one other people can hear", es: "Retenido: en esta superficie pueden oírlo otras personas", fr: "Retenu — sur cette surface, d'autres peuvent entendre", de: "Zurückgehalten — auf dieser Fläche können andere mithören", pt: "Retido — nesta superfície outras pessoas podem ouvir", it: "Trattenuto — su questa superficie altri possono sentire", ja: "保留しました — ここは他の人にも聞こえます", zh: "已保留 — 这个设备旁边可能有别人", hi: "रोका गया — इस सतह पर दूसरे सुन सकते हैं", ar: "مُحتجَز — هذا السطح يسمعه آخرون",
  },
  "presence.aloud.nosound": {
    en: "No voice on this one — read it instead", es: "Esta no tiene voz: léelo", fr: "Pas de voix ici — à lire", de: "Hier ohne Stimme — zum Lesen", pt: "Esta não tem voz — leia", it: "Qui senza voce — da leggere", ja: "ここには声がありません — 読んでください", zh: "这个没有声音 — 请阅读", hi: "इस पर आवाज़ नहीं — पढ़ लें", ar: "لا صوت هنا — اقرأه",
  },
  "presence.aloud.said": {
    en: "Said out loud", es: "Dicho en voz alta", fr: "Dit à voix haute", de: "Laut gesagt", pt: "Dito em voz alta", it: "Detto ad alta voce", ja: "声に出しました", zh: "已读出", hi: "बोलकर कहा गया", ar: "قيل بصوت مسموع",
  },
  "presence.hands.free": {
    en: "Anything right now?", es: "¿Algo ahora mismo?", fr: "Quelque chose maintenant ?", de: "Gerade irgendwas?", pt: "Algo agora?", it: "Qualcosa adesso?", ja: "いま何かある？", zh: "现在有什么吗？", hi: "अभी कुछ है?", ar: "هل من شيء الآن؟",
  },
  "presence.bearing": {
    en: "How I carry myself", es: "Cómo me comporto", fr: "Comment je me tiens", de: "Wie ich mich gebe", pt: "Como me porto", it: "Come mi pongo", ja: "どう構えるか", zh: "我以什么姿态", hi: "मैं कैसा रुख़ रखूँ", ar: "كيف أتصرّف",
  },
  "presence.bearing.companion": {
    en: "Companion", es: "Compañía", fr: "Compagnon", de: "Begleiter", pt: "Companhia", it: "Compagno", ja: "そばにいる", zh: "陪伴", hi: "साथी", ar: "رفيق",
  },
  "presence.bearing.professional": {
    en: "Professional", es: "Profesional", fr: "Professionnel", de: "Sachlich", pt: "Profissional", it: "Professionale", ja: "きちんと", zh: "专业", hi: "पेशेवर", ar: "مِهَنيّ",
  },
  "presence.bearing.same": {
    en: "Unchanged either way", es: "Igual en ambos casos", fr: "Identique dans les deux cas", de: "In beiden Fällen gleich", pt: "Igual nos dois casos", it: "Uguale in entrambi", ja: "どちらでも変わらないこと", zh: "两者都不变", hi: "दोनों में अपरिवर्तित", ar: "لا يتغيّر في الحالتين",
  },
  "presence.growth": {
    en: "What I have become", es: "En qué me he convertido", fr: "Ce que je suis devenu", de: "Was ich geworden bin", pt: "No que me tornei", it: "Cosa sono diventato", ja: "私が何になったか", zh: "我变成了什么", hi: "मैं क्या बन गया हूँ", ar: "ما الذي صرتُ إليه",
  },
  "presence.aloud": {
    en: "read aloud here", es: "se lee en voz alta aquí", fr: "lu à voix haute ici", de: "wird hier vorgelesen", pt: "lido em voz alta aqui", it: "letto ad alta voce qui", ja: "ここでは読み上げます", zh: "这里会读出声", hi: "यहाँ ज़ोर से पढ़ा जाएगा", ar: "يُقرأ بصوت عالٍ هنا",
  },
  "presence.shown": {
    en: "shown, not spoken", es: "se muestra, no se dice", fr: "affiché, pas dit", de: "gezeigt, nicht gesprochen", pt: "mostrado, não dito", it: "mostrato, non detto", ja: "声には出さず表示します", zh: "显示，不出声", hi: "दिखाया जाएगा, बोला नहीं", ar: "يُعرض ولا يُقال",
  },
  "prob.server": {
    en: "What has reached the server",
    es: "Lo que ha llegado al servidor",
    fr: "Ce qui a atteint le serveur",
    de: "Was den Server erreicht hat",
    pt: "O que chegou ao servidor",
    it: "Cosa è arrivato al server",
    ja: "サーバーに届いたもの",
    zh: "已到达服务器的内容",
    hi: "सर्वर तक क्या पहुँचा",
    ar: "ما وصل إلى الخادم",
  },
  "prob.server.pitch": {
    en: "Every client of this deployment reports its failures here, folded into counters — an operation, a status, a count, never anyone's content. Reading them is the operator's: use the JIM_PROBLEMS_KEY, or ask from the machine the backend runs on.",
    es: "Cada cliente de esta instalación informa aquí sus fallos, plegados en contadores: una operación, un estado, un recuento, nunca el contenido de nadie. Leerlos es del operador: usa la JIM_PROBLEMS_KEY o consulta desde la máquina donde corre el backend.",
    fr: "Chaque client de ce déploiement rapporte ici ses échecs, repliés en compteurs — une opération, un statut, un total, jamais le contenu de quiconque. Leur lecture revient à l'opérateur : utilisez la JIM_PROBLEMS_KEY, ou interrogez depuis la machine du backend.",
    de: "Jeder Client dieser Installation meldet seine Fehler hierher, zu Zählern gefaltet — eine Operation, ein Status, eine Anzahl, nie jemandes Inhalte. Lesen ist Sache des Betreibers: mit dem JIM_PROBLEMS_KEY, oder von der Maschine aus, auf der das Backend läuft.",
    pt: "Cada cliente desta instalação comunica aqui as suas falhas, dobradas em contadores — uma operação, um estado, uma contagem, nunca o conteúdo de ninguém. Lê-las é do operador: use a JIM_PROBLEMS_KEY ou pergunte a partir da máquina onde corre o backend.",
    it: "Ogni client di questa installazione riporta qui i suoi errori, ripiegati in contatori — un'operazione, uno stato, un conteggio, mai il contenuto di qualcuno. Leggerli spetta all'operatore: usa la JIM_PROBLEMS_KEY, oppure chiedi dalla macchina su cui gira il backend.",
    ja: "この配備のすべてのクライアントが障害をここに報告し、カウンターに畳み込まれます — 操作、ステータス、件数だけで、誰かの内容は決して含まれません。読むのは運用者の役目です。JIM_PROBLEMS_KEY を使うか、バックエンドが動く機械から尋ねてください。",
    zh: "此部署的每个客户端都把故障报告到这里，折叠成计数——操作、状态码、次数，绝不含任何人的内容。读取属于运维者：使用 JIM_PROBLEMS_KEY，或从后端所在的机器上查询。",
    hi: "इस परिनियोजन का हर क्लाइंट अपनी विफलताएँ यहाँ भेजता है, गिनतियों में समेटी हुई — एक ऑपरेशन, एक स्थिति, एक संख्या, कभी किसी की सामग्री नहीं। इन्हें पढ़ना संचालक का काम है: JIM_PROBLEMS_KEY इस्तेमाल करें, या उसी मशीन से पूछें जिस पर बैकएंड चलता है।",
    ar: "كل عميل في هذا النشر يبلّغ أعطاله هنا، مطويةً في عدّادات — عملية وحالة وعدد، ولا محتوى لأحد أبدًا. قراءتها للمشغّل: استخدم JIM_PROBLEMS_KEY، أو اسأل من الجهاز الذي يعمل عليه الخادم.",
  },
  "prob.key.ph": {
    en: "the problems key, if this deployment set one",
    es: "la clave de problemas, si esta instalación fijó una",
    fr: "la clé des problèmes, si ce déploiement en a défini une",
    de: "der Problems-Schlüssel, falls diese Installation einen gesetzt hat",
    pt: "a chave de problemas, se esta instalação definiu uma",
    it: "la chiave dei problemi, se questa installazione ne ha una",
    ja: "この配備で設定されていれば、その「problems」キー",
    zh: "如果此部署设置了问题密钥，请输入",
    hi: "समस्याओं की कुंजी, अगर इस परिनियोजन ने कोई रखी है",
    ar: "مفتاح المشاكل، إن كان هذا النشر قد عيّن واحدًا",
  },
  "prob.fetch": {
    en: "Read the aggregate",
    es: "Leer el agregado",
    fr: "Lire l'agrégat",
    de: "Das Aggregat lesen",
    pt: "Ler o agregado",
    it: "Leggi l'aggregato",
    ja: "集計を読む",
    zh: "读取汇总",
    hi: "समग्र पढ़ें",
    ar: "اقرأ المجمّع",
  },
  "prob.none": {
    en: "Nothing has been reported to this server yet.",
    es: "Aún no se ha informado nada a este servidor.",
    fr: "Rien n'a encore été rapporté à ce serveur.",
    de: "Diesem Server wurde noch nichts gemeldet.",
    pt: "Ainda nada foi comunicado a este servidor.",
    it: "A questo server non è ancora stato segnalato nulla.",
    ja: "このサーバーにはまだ何も報告されていません。",
    zh: "尚未有任何报告到达此服务器。",
    hi: "इस सर्वर को अभी तक कुछ नहीं बताया गया।",
    ar: "لم يُبلَّغ هذا الخادم بشيء بعد.",
  },
  "nav.home": {
    en: "Overview",
    es: "Resumen",
    fr: "Aperçu",
    de: "Übersicht",
    pt: "Visão geral",
    it: "Panoramica",
    ja: "概要",
    zh: "概览",
    hi: "अवलोकन",
    ar: "نظرة عامة",
  },
  "nav.monitor": {
    en: "Live Monitoring",
    es: "Vigilancia en directo",
    fr: "Surveillance en direct",
    de: "Live-Überwachung",
    pt: "Vigilância em direto",
    it: "Monitoraggio dal vivo",
    ja: "ライブ・モニタリング",
    zh: "实时监测",
    hi: "लाइव निगरानी",
    ar: "المراقبة الحيّة",
  },
  "nav.safety": {
    en: "Safety",
    es: "Seguridad",
    fr: "Sécurité",
    de: "Sicherheit",
    pt: "Segurança",
    it: "Sicurezza",
    ja: "安全",
    zh: "安全",
    hi: "सुरक्षा",
    ar: "السلامة",
  },
  "nav.baseline": {
    en: "Your Baseline",
    es: "Tu línea base",
    fr: "Votre référence",
    de: "Deine Baseline",
    pt: "A sua linha de base",
    it: "La tua baseline",
    ja: "あなたのベースライン",
    zh: "你的基线",
    hi: "आपकी बेसलाइन",
    ar: "خط أساسك",
  },
  "nav.meds": {
    en: "Medications",
    es: "Medicamentos",
    fr: "Médicaments",
    de: "Medikamente",
    pt: "Medicamentos",
    it: "Farmaci",
    ja: "服薬",
    zh: "用药",
    hi: "दवाइयाँ",
    ar: "الأدوية",
  },
  "nav.careteam": {
    en: "Care Team",
    es: "Equipo de cuidados",
    fr: "Équipe de soins",
    de: "Betreuungsteam",
    pt: "Equipa de cuidados",
    it: "Team di cura",
    ja: "ケアチーム",
    zh: "护理团队",
    hi: "देखभाल टीम",
    ar: "فريق الرعاية",
  },
  "self.profile_id": {
    en: "prf_…",
    es: "prf_…",
    fr: "prf_…",
    de: "prf_…",
    pt: "prf_…",
    it: "prf_…",
    ja: "prf_…",
    zh: "prf_…",
    hi: "prf_…",
    ar: "prf_…",
  },
  "self.title": {
    en: "Your own profile",
    es: "Tu propio perfil",
    fr: "Votre propre profil",
    de: "Dein eigenes Profil",
    pt: "O seu próprio perfil",
    it: "Il tuo profilo",
    ja: "あなた自身のプロフィール",
    zh: "你自己的档案",
    hi: "आपकी अपनी प्रोफ़ाइल",
    ar: "ملفك الشخصي",
  },
  "self.lead": {
    en: "The QRME profile that speaks as you. The Guardian tells it nothing until you say which parts it may pass on, and you can see exactly what would go before any of it does.",
    es: "El perfil de QRME que habla como tú. El Guardián no le cuenta nada hasta que digas qué partes puede transmitir, y puedes ver exactamente qué se enviaría antes de que se envíe.",
    fr: "Le profil QRME qui parle en votre nom. Le Gardien ne lui dit rien tant que vous n’avez pas indiqué ce qu’il peut transmettre, et vous voyez exactement ce qui partirait avant que quoi que ce soit parte.",
    de: "Das QRME-Profil, das als du spricht. Der Guardian sagt ihm nichts, bis du festlegst, was er weitergeben darf, und du siehst genau, was ginge, bevor irgendetwas geht.",
    pt: "O perfil QRME que fala como você. O Guardião não lhe conta nada até dizer que partes pode transmitir, e vê exatamente o que iria antes de qualquer coisa ir.",
    it: "Il profilo QRME che parla come te. Il Guardian non gli dice nulla finché non indichi cosa può trasmettere, e vedi esattamente cosa partirebbe prima che parta.",
    ja: "あなたとして話す QRME のプロフィールです。どの部分を伝えてよいか決めるまで、ガーディアンは何も伝えません。送られる内容は送信前にそのまま確認できます。",
    zh: "以你的身份说话的 QRME 档案。在你指明可以转达哪些部分之前，守护者不会告诉它任何事，而且发送前你能看到确切会送出什么。",
    hi: "वह QRME प्रोफ़ाइल जो आपके रूप में बोलती है। जब तक आप यह न बताएँ कि कौन-से हिस्से भेजे जा सकते हैं, गार्जियन उसे कुछ नहीं बताता, और भेजे जाने से पहले आप ठीक-ठीक देख सकते हैं कि क्या जाएगा।",
    ar: "ملف QRME الذي يتحدث بصفتك. لا يخبره الحارس بشيء حتى تحدد ما يمكن نقله، ويمكنك أن ترى بالضبط ما سيُرسل قبل أن يُرسل أي شيء.",
  },
  // Linking by signing in, rather than by pasting a `prf_…` id and an owner
  // token nobody can find. The keys below the paste-it form stay: it is
  // still the right door for somebody who does hold both.
  "self.signin.title": {
    en: "Sign in to QRME",
    es: "Inicia sesión en QRME",
    fr: "Se connecter à QRME",
    de: "Bei QRME anmelden",
    pt: "Inicia sessão no QRME",
    it: "Accedi a QRME",
    ja: "QRME にサインイン",
    zh: "登录 QRME",
    hi: "QRME में साइन इन करें",
    ar: "تسجيل الدخول إلى QRME",
  },
  "self.signin.pitch": {
    en: "Your QRME email and password. The Guardian finds your own profile and gets its key for you — neither the password nor anything else from the sign-in is kept.",
    es: "Tu correo y contraseña de QRME. El Guardián encuentra tu propio perfil y obtiene su clave por ti; ni la contraseña ni nada más del inicio de sesión se guarda.",
    fr: "Votre e-mail et mot de passe QRME. Le Gardien trouve votre propre profil et en obtient la clé pour vous — ni le mot de passe ni rien d'autre de la connexion n'est conservé.",
    de: "Deine QRME-E-Mail und dein Passwort. Der Guardian findet dein eigenes Profil und holt dessen Schlüssel für dich — weder das Passwort noch sonst etwas aus der Anmeldung wird behalten.",
    pt: "O teu email e palavra-passe do QRME. O Guardião encontra o teu próprio perfil e obtém a chave por ti — nem a palavra-passe nem mais nada do início de sessão fica guardado.",
    it: "La tua email e password QRME. Il Guardian trova il tuo profilo e ne ottiene la chiave per te — né la password né altro dell'accesso viene conservato.",
    ja: "QRME のメールアドレスとパスワードです。ガーディアンがあなた自身のプロフィールを見つけ、その鍵を取得します。パスワードもサインインの内容も保存されません。",
    zh: "你的 QRME 邮箱和密码。守护者会找到你自己的档案并替你取得它的钥匙——密码和登录过程中的任何东西都不会被保存。",
    hi: "आपका QRME ईमेल और पासवर्ड। गार्जियन आपकी अपनी प्रोफ़ाइल ढूँढ़कर उसकी कुंजी आपके लिए ले लेता है — न पासवर्ड रखा जाता है, न साइन-इन से और कुछ।",
    ar: "بريدك وكلمة مرورك في QRME. يجد الحارس ملفك الشخصي ويحصل على مفتاحه نيابةً عنك — ولا تُحفظ كلمة المرور ولا أي شيء آخر من تسجيل الدخول.",
  },
  "self.signin.email": {
    en: "QRME email",
    es: "Correo de QRME",
    fr: "E-mail QRME",
    de: "QRME-E-Mail",
    pt: "Email do QRME",
    it: "Email QRME",
    ja: "QRME のメールアドレス",
    zh: "QRME 邮箱",
    hi: "QRME ईमेल",
    ar: "بريد QRME",
  },
  "self.signin.password": {
    en: "QRME password",
    es: "Contraseña de QRME",
    fr: "Mot de passe QRME",
    de: "QRME-Passwort",
    pt: "Palavra-passe do QRME",
    it: "Password QRME",
    ja: "QRME のパスワード",
    zh: "QRME 密码",
    hi: "QRME पासवर्ड",
    ar: "كلمة مرور QRME",
  },
  "self.signin.button": {
    en: "Find my profile",
    es: "Buscar mi perfil",
    fr: "Trouver mon profil",
    de: "Mein Profil finden",
    pt: "Encontrar o meu perfil",
    it: "Trova il mio profilo",
    ja: "自分のプロフィールを探す",
    zh: "找到我的档案",
    hi: "मेरी प्रोफ़ाइल ढूँढ़ें",
    ar: "ابحث عن ملفي",
  },
  "self.signin.choose": {
    en: "That account has more than one profile of you. Which one should the Guardian speak to?",
    es: "Esa cuenta tiene más de un perfil tuyo. ¿Con cuál debe hablar el Guardián?",
    fr: "Ce compte a plusieurs profils de vous. Auquel le Gardien doit-il parler ?",
    de: "Dieses Konto hat mehr als ein Profil von dir. Mit welchem soll der Guardian sprechen?",
    pt: "Essa conta tem mais do que um perfil teu. Com qual deve o Guardião falar?",
    it: "Quell'account ha più di un profilo di te. A quale deve parlare il Guardian?",
    ja: "そのアカウントにはあなた自身のプロフィールが複数あります。ガーディアンはどれに話しかけますか。",
    zh: "那个账户里有不止一个你自己的档案。守护者应该跟哪一个说话？",
    hi: "उस खाते में आपकी एक से अधिक प्रोफ़ाइल हैं। गार्जियन किससे बात करे?",
    ar: "يحتوي ذلك الحساب على أكثر من ملف شخصي لك. مع أيّها يتحدّث الحارس؟",
  },
  "self.signin.paste_instead": {
    en: "Or paste an id and token",
    es: "O pega un id y un token",
    fr: "Ou coller un identifiant et un jeton",
    de: "Oder ID und Token einfügen",
    pt: "Ou cola um id e um token",
    it: "Oppure incolla id e token",
    ja: "または ID とトークンを貼り付ける",
    zh: "或者粘贴 id 和令牌",
    hi: "या id और टोकन चिपकाएँ",
    ar: "أو الصق معرِّفًا ورمزًا",
  },
  // The talk surface: the composer, the `+` menu, and the scrolling rail.
  // The rail's strings name destinations that already exist, so each one
  // is the same sentence its own screen uses where there was one.
  "talk.ph": {
    en: "Ask JIM anything",
    es: "Pregúntale lo que sea a JIM",
    fr: "Demandez n'importe quoi à JIM",
    de: "Frag JIM irgendetwas",
    pt: "Pergunta qualquer coisa ao JIM",
    it: "Chiedi qualsiasi cosa a JIM",
    ja: "JIM に何でも聞いてください",
    zh: "问 JIM 任何事",
    hi: "JIM से कुछ भी पूछें",
    ar: "اسأل JIM أي شيء",
  },
  "talk.send": {
    en: "Send",
    es: "Enviar",
    fr: "Envoyer",
    de: "Senden",
    pt: "Enviar",
    it: "Invia",
    ja: "送信",
    zh: "发送",
    hi: "भेजें",
    ar: "إرسال",
  },
  "talk.plus": {
    en: "Add something",
    es: "Añadir algo",
    fr: "Ajouter quelque chose",
    de: "Etwas hinzufügen",
    pt: "Adicionar algo",
    it: "Aggiungi qualcosa",
    ja: "何かを追加",
    zh: "添加内容",
    hi: "कुछ जोड़ें",
    ar: "أضف شيئًا",
  },
  "talk.plus.camera": {
    en: "Camera",
    es: "Cámara",
    fr: "Appareil photo",
    de: "Kamera",
    pt: "Câmara",
    it: "Fotocamera",
    ja: "カメラ",
    zh: "相机",
    hi: "कैमरा",
    ar: "الكاميرا",
  },
  "talk.plus.photos": {
    en: "Photos",
    es: "Fotos",
    fr: "Photos",
    de: "Fotos",
    pt: "Fotografias",
    it: "Foto",
    ja: "写真",
    zh: "照片",
    hi: "तस्वीरें",
    ar: "الصور",
  },
  "talk.plus.voice": {
    en: "Microphone",
    es: "Micrófono",
    fr: "Microphone",
    de: "Mikrofon",
    pt: "Microfone",
    it: "Microfono",
    ja: "マイク",
    zh: "麦克风",
    hi: "माइक्रोफ़ोन",
    ar: "الميكروفون",
  },
  "widgets.no_rlimits": {
    en: "This deployment cannot cap what a widget may use, so nothing will run here.",
    es: "Esta instalación no puede limitar lo que un widget puede usar, así que aquí no se ejecutará nada.",
    fr: "Cette installation ne peut pas plafonner ce qu'un widget consomme ; rien ne s'exécutera ici.",
    de: "Diese Installation kann nicht begrenzen, was ein Widget verbraucht — hier wird nichts ausgeführt.",
    pt: "Esta instalação não consegue limitar o que um widget pode usar, por isso aqui nada será executado.",
    it: "Questa installazione non può limitare quanto un widget consuma, quindi qui non verrà eseguito nulla.",
    ja: "この環境ではウィジェットの使用量に上限をかけられないため、ここでは何も実行されません。",
    zh: "此部署无法限制小工具可占用的资源，因此这里不会运行任何东西。",
    hi: "यह इंस्टॉलेशन सीमित नहीं कर सकता कि विजेट कितना उपयोग करे, इसलिए यहाँ कुछ नहीं चलेगा।",
    ar: "لا يستطيع هذا التنصيب تحديد ما تستهلكه الأداة، فلن يُشغَّل شيء هنا.",
  },
  "widgets.no_unshare": {
    en: "This deployment cannot build the box a widget runs in, so nothing will run here.",
    es: "Esta instalación no puede construir la caja donde corre un widget, así que aquí no se ejecutará nada.",
    fr: "Cette installation ne peut pas construire la boîte où tourne un widget ; rien ne s'exécutera ici.",
    de: "Diese Installation kann die Box, in der ein Widget läuft, nicht bauen — hier wird nichts ausgeführt.",
    pt: "Esta instalação não consegue construir a caixa onde um widget corre, por isso aqui nada será executado.",
    it: "Questa installazione non può costruire la scatola in cui gira un widget, quindi qui non verrà eseguito nulla.",
    ja: "この環境ではウィジェットを走らせる箱を作れないため、ここでは何も実行されません。",
    zh: "此部署无法搭建运行小工具所需的沙箱，因此这里不会运行任何东西。",
    hi: "यह इंस्टॉलेशन वह डिब्बा नहीं बना सकता जिसमें विजेट चलता है, इसलिए यहाँ कुछ नहीं चलेगा।",
    ar: "لا يستطيع هذا التنصيب بناء الصندوق الذي تعمل داخله الأداة، فلن يُشغَّل شيء هنا.",
  },
  "widgets.no_node": {
    en: "This deployment has no interpreter for widgets, so nothing will run here.",
    es: "Esta instalación no tiene intérprete para widgets, así que aquí no se ejecutará nada.",
    fr: "Cette installation n'a pas d'interpréteur pour les widgets ; rien ne s'exécutera ici.",
    de: "Diese Installation hat keinen Interpreter für Widgets — hier wird nichts ausgeführt.",
    pt: "Esta instalação não tem interpretador para widgets, por isso aqui nada será executado.",
    it: "Questa installazione non ha un interprete per i widget, quindi qui non verrà eseguito nulla.",
    ja: "この環境にはウィジェット用のインタプリタがないため、ここでは何も実行されません。",
    zh: "此部署没有运行小工具的解释器，因此这里不会运行任何东西。",
    hi: "इस इंस्टॉलेशन में विजेट के लिए कोई इंटरप्रेटर नहीं है, इसलिए यहाँ कुछ नहीं चलेगा।",
    ar: "لا يوجد في هذا التنصيب مفسّر للأدوات، فلن يُشغَّل شيء هنا.",
  },
  "widgets.node_too_old": {
    en: "This deployment's interpreter is too old to hold a widget in, so nothing will run here.",
    es: "El intérprete de esta instalación es demasiado antiguo para contener un widget, así que aquí no se ejecutará nada.",
    fr: "L'interpréteur de cette installation est trop ancien pour contenir un widget ; rien ne s'exécutera ici.",
    de: "Der Interpreter dieser Installation ist zu alt, um ein Widget zu halten — hier wird nichts ausgeführt.",
    pt: "O interpretador desta instalação é demasiado antigo para conter um widget, por isso aqui nada será executado.",
    it: "L'interprete di questa installazione è troppo vecchio per contenere un widget, quindi qui non verrà eseguito nulla.",
    ja: "この環境のインタプリタは古すぎてウィジェットを閉じ込められないため、ここでは何も実行されません。",
    zh: "此部署的解释器过旧，无法约束小工具，因此这里不会运行任何东西。",
    hi: "इस इंस्टॉलेशन का इंटरप्रेटर इतना पुराना है कि विजेट को रोक नहीं सकता, इसलिए यहाँ कुछ नहीं चलेगा।",
    ar: "مفسّر هذا التنصيب أقدم من أن يحتوي أداة، فلن يُشغَّل شيء هنا.",
  },
  "widgets.no_netns": {
    en: "This deployment cannot cut the network for a widget, so nothing will run here.",
    es: "Esta instalación no puede cortar la red para un widget, así que aquí no se ejecutará nada.",
    fr: "Cette installation ne peut pas couper le réseau pour un widget ; rien ne s'exécutera ici.",
    de: "Diese Installation kann einem Widget das Netz nicht abschneiden — hier wird nichts ausgeführt.",
    pt: "Esta instalação não consegue cortar a rede a um widget, por isso aqui nada será executado.",
    it: "Questa installazione non può tagliare la rete a un widget, quindi qui non verrà eseguito nulla.",
    ja: "この環境ではウィジェットのネットワークを遮断できないため、ここでは何も実行されません。",
    zh: "此部署无法为小工具切断网络，因此这里不会运行任何东西。",
    hi: "यह इंस्टॉलेशन विजेट के लिए नेटवर्क नहीं काट सकता, इसलिए यहाँ कुछ नहीं चलेगा।",
    ar: "لا يستطيع هذا التنصيب قطع الشبكة عن الأداة، فلن يُشغَّل شيء هنا.",
  },
  "widgets.threw": {
    en: "Your widget stopped on an error.",
    es: "Tu widget se detuvo por un error.",
    fr: "Votre widget s'est arrêté sur une erreur.",
    de: "Dein Widget ist mit einem Fehler abgebrochen.",
    pt: "O teu widget parou com um erro.",
    it: "Il tuo widget si è fermato su un errore.",
    ja: "ウィジェットがエラーで停止しました。",
    zh: "你的小工具因错误停止了。",
    hi: "आपका विजेट एक त्रुटि पर रुक गया।",
    ar: "توقّفت أداتك عند خطأ.",
  },
  "widgets.timeout": {
    en: "Your widget ran longer than it is allowed to.",
    es: "Tu widget se ejecutó más tiempo del permitido.",
    fr: "Votre widget a tourné plus longtemps qu'il n'y est autorisé.",
    de: "Dein Widget lief länger, als es darf.",
    pt: "O teu widget correu mais tempo do que lhe é permitido.",
    it: "Il tuo widget ha girato più a lungo di quanto gli sia concesso.",
    ja: "ウィジェットが許された時間を超えて動き続けました。",
    zh: "你的小工具运行时间超过了允许的上限。",
    hi: "आपका विजेट अनुमत समय से अधिक चला।",
    ar: "استغرقت أداتك وقتًا أطول مما هو مسموح لها.",
  },
  "widgets.killed": {
    en: "Your widget was stopped for using more than it is allowed.",
    es: "Tu widget se detuvo por usar más de lo permitido.",
    fr: "Votre widget a été arrêté pour avoir consommé plus qu'il n'y est autorisé.",
    de: "Dein Widget wurde gestoppt, weil es mehr verbraucht hat, als es darf.",
    pt: "O teu widget foi parado por usar mais do que lhe é permitido.",
    it: "Il tuo widget è stato fermato perché consumava più del consentito.",
    ja: "ウィジェットが許された量を超えて使ったため停止されました。",
    zh: "你的小工具因占用超过允许的资源而被停止。",
    hi: "आपका विजेट अनुमत से अधिक उपयोग करने पर रोक दिया गया।",
    ar: "أُوقفت أداتك لأنها استهلكت أكثر مما هو مسموح لها.",
  },
  "widgets.no_answer": {
    en: "Your widget finished without returning anything.",
    es: "Tu widget terminó sin devolver nada.",
    fr: "Votre widget s'est terminé sans rien renvoyer.",
    de: "Dein Widget ist beendet, ohne etwas zurückzugeben.",
    pt: "O teu widget terminou sem devolver nada.",
    it: "Il tuo widget è finito senza restituire nulla.",
    ja: "ウィジェットは何も返さずに終了しました。",
    zh: "你的小工具结束了，但没有返回任何内容。",
    hi: "आपका विजेट बिना कुछ लौटाए समाप्त हो गया।",
    ar: "انتهت أداتك دون أن تُعيد شيئًا.",
  },
  // -- the Studio (app/src/screens/Studio.tsx) ------------------------------
  //
  // The five `widgets.no_*` rows and the four run-failure rows below are this
  // console's own copies of the server's refusal keys. The server sends the
  // key and never the sentence, so a person on a French install reads French
  // whatever language the backend happens to hold.
  "studio.title": {
    en: "Widgets",
    es: "Widgets",
    fr: "Widgets",
    de: "Widgets",
    pt: "Widgets",
    it: "Widget",
    ja: "ウィジェット",
    zh: "小工具",
    hi: "विजेट",
    ar: "الأدوات",
  },
  "studio.sub": {
    en: "tools you write, for yourself only",
    es: "herramientas que escribes, solo para ti",
    fr: "des outils que vous écrivez, pour vous seul",
    de: "Werkzeuge, die du schreibst — nur für dich",
    pt: "ferramentas que escreves, só para ti",
    it: "strumenti che scrivi, solo per te",
    ja: "あなたが書く、あなただけの道具",
    zh: "你自己编写、只属于你的小工具",
    hi: "आपके लिखे हुए औज़ार, केवल आपके लिए",
    ar: "أدوات تكتبها، لك وحدك",
  },
  "studio.yours": {
    en: "Your widgets",
    es: "Tus widgets",
    fr: "Vos widgets",
    de: "Deine Widgets",
    pt: "Os teus widgets",
    it: "I tuoi widget",
    ja: "あなたのウィジェット",
    zh: "你的小工具",
    hi: "आपके विजेट",
    ar: "أدواتك",
  },
  "studio.new": {
    en: "New",
    es: "Nuevo",
    fr: "Nouveau",
    de: "Neu",
    pt: "Novo",
    it: "Nuovo",
    ja: "新規",
    zh: "新建",
    hi: "नया",
    ar: "جديد",
  },
  "studio.none": {
    en: "None yet. Write one.",
    es: "Todavía ninguno. Escribe uno.",
    fr: "Aucun pour l'instant. Écrivez-en un.",
    de: "Noch keins. Schreib eines.",
    pt: "Ainda nenhum. Escreve um.",
    it: "Ancora nessuno. Scrivine uno.",
    ja: "まだありません。ひとつ書いてみましょう。",
    zh: "还没有。写一个吧。",
    hi: "अभी कोई नहीं। एक लिखिए।",
    ar: "لا شيء بعد. اكتب واحدة.",
  },
  "studio.revision": {
    en: "saved {n} time(s)",
    es: "guardado {n} vez/veces",
    fr: "enregistré {n} fois",
    de: "{n}-mal gespeichert",
    pt: "guardado {n} vez(es)",
    it: "salvato {n} volta/e",
    ja: "保存 {n} 回",
    zh: "已保存 {n} 次",
    hi: "{n} बार सहेजा गया",
    ar: "حُفظت {n} مرة",
  },
  "studio.remove": {
    en: "Remove",
    es: "Quitar",
    fr: "Supprimer",
    de: "Entfernen",
    pt: "Remover",
    it: "Rimuovi",
    ja: "削除",
    zh: "移除",
    hi: "हटाएँ",
    ar: "احذف",
  },
  "studio.editing": {
    en: "Editing",
    es: "Editando",
    fr: "Modification",
    de: "Bearbeiten",
    pt: "A editar",
    it: "In modifica",
    ja: "編集中",
    zh: "正在编辑",
    hi: "संपादन",
    ar: "تحرير",
  },
  "studio.writing": {
    en: "Writing a new one",
    es: "Escribiendo uno nuevo",
    fr: "Écriture d'un nouveau",
    de: "Ein neues schreiben",
    pt: "A escrever um novo",
    it: "Ne stai scrivendo uno nuovo",
    ja: "新しく書く",
    zh: "正在写一个新的",
    hi: "नया लिख रहे हैं",
    ar: "كتابة واحدة جديدة",
  },
  "studio.name": {
    en: "Name",
    es: "Nombre",
    fr: "Nom",
    de: "Name",
    pt: "Nome",
    it: "Nome",
    ja: "名前",
    zh: "名称",
    hi: "नाम",
    ar: "الاسم",
  },
  "studio.source": {
    en: "Code",
    es: "Código",
    fr: "Code",
    de: "Code",
    pt: "Código",
    it: "Codice",
    ja: "コード",
    zh: "代码",
    hi: "कोड",
    ar: "الشيفرة",
  },
  "studio.save": {
    en: "Save changes",
    es: "Guardar cambios",
    fr: "Enregistrer les modifications",
    de: "Änderungen speichern",
    pt: "Guardar alterações",
    it: "Salva le modifiche",
    ja: "変更を保存",
    zh: "保存更改",
    hi: "बदलाव सहेजें",
    ar: "احفظ التغييرات",
  },
  "studio.keep": {
    en: "Keep it",
    es: "Guardarlo",
    fr: "Le garder",
    de: "Behalten",
    pt: "Guardar",
    it: "Tienilo",
    ja: "保存する",
    zh: "保存",
    hi: "रखें",
    ar: "احتفظ بها",
  },
  "studio.tryit": {
    en: "Try it",
    es: "Probarlo",
    fr: "L'essayer",
    de: "Ausprobieren",
    pt: "Experimenta",
    it: "Provalo",
    ja: "試す",
    zh: "试运行",
    hi: "आज़माएँ",
    ar: "جرّبها",
  },
  "studio.inputs": {
    en: "What to hand it (JSON)",
    es: "Qué darle (JSON)",
    fr: "Ce qu'on lui donne (JSON)",
    de: "Was es bekommt (JSON)",
    pt: "O que lhe dar (JSON)",
    it: "Cosa passargli (JSON)",
    ja: "渡すもの（JSON）",
    zh: "传给它什么（JSON）",
    hi: "इसे क्या दें (JSON)",
    ar: "ما تُمرّره إليها (JSON)",
  },
  "studio.run": {
    en: "Run",
    es: "Ejecutar",
    fr: "Exécuter",
    de: "Ausführen",
    pt: "Executar",
    it: "Esegui",
    ja: "実行",
    zh: "运行",
    hi: "चलाएँ",
    ar: "شغّل",
  },
  "studio.cannotrun": {
    en: "Nothing can run on this deployment, so there is no run button — you can still write and keep your widgets.",
    es: "Aquí no se puede ejecutar nada, así que no hay botón de ejecución: aún puedes escribir y guardar tus widgets.",
    fr: "Rien ne peut s'exécuter sur cette installation ; il n'y a donc pas de bouton d'exécution — vous pouvez toujours écrire et conserver vos widgets.",
    de: "Auf dieser Installation kann nichts laufen, darum gibt es keinen Ausführen-Knopf — schreiben und behalten kannst du deine Widgets trotzdem.",
    pt: "Nesta instalação nada pode ser executado, por isso não há botão de execução — podes na mesma escrever e guardar os teus widgets.",
    it: "Su questa installazione non può girare nulla, quindi non c'è il pulsante di esecuzione — puoi comunque scrivere e tenere i tuoi widget.",
    ja: "この環境では何も実行できないため、実行ボタンはありません。ウィジェットを書いて保存することはできます。",
    zh: "此部署无法运行任何东西，因此没有运行按钮——你仍然可以编写并保存小工具。",
    hi: "इस इंस्टॉलेशन पर कुछ नहीं चल सकता, इसलिए चलाने का बटन नहीं है — आप फिर भी विजेट लिख और रख सकते हैं।",
    ar: "لا يمكن تشغيل شيء على هذا التنصيب، فلا يوجد زر تشغيل — ما زال بإمكانك كتابة أدواتك والاحتفاظ بها.",
  },
  "studio.took": {
    en: "took {ms} ms",
    es: "tardó {ms} ms",
    fr: "a pris {ms} ms",
    de: "dauerte {ms} ms",
    pt: "demorou {ms} ms",
    it: "ha impiegato {ms} ms",
    ja: "{ms} ミリ秒",
    zh: "用时 {ms} 毫秒",
    hi: "{ms} मि.से. लगे",
    ar: "استغرقت {ms} م.ث",
  },
  "studio.toobig": {
    en: "The answer was too large to show.",
    es: "La respuesta era demasiado grande para mostrarla.",
    fr: "La réponse était trop volumineuse pour être affichée.",
    de: "Die Antwort war zu groß, um sie zu zeigen.",
    pt: "A resposta era grande demais para mostrar.",
    it: "La risposta era troppo grande da mostrare.",
    ja: "答えが大きすぎて表示できません。",
    zh: "返回内容太大，无法显示。",
    hi: "उत्तर दिखाने के लिए बहुत बड़ा था।",
    ar: "كانت الإجابة أكبر من أن تُعرض.",
  },
  "studio.failed": {
    en: "That did not finish.",
    es: "Eso no terminó.",
    fr: "Cela ne s'est pas terminé.",
    de: "Das ist nicht durchgelaufen.",
    pt: "Isso não terminou.",
    it: "Non è arrivato in fondo.",
    ja: "最後まで終わりませんでした。",
    zh: "没有跑完。",
    hi: "वह पूरा नहीं हुआ।",
    ar: "لم تكتمل.",
  },
  "studio.badinputs": {
    en: "That is not JSON — check the braces and quotes.",
    es: "Eso no es JSON: revisa las llaves y las comillas.",
    fr: "Ce n'est pas du JSON — vérifiez les accolades et les guillemets.",
    de: "Das ist kein JSON — prüf Klammern und Anführungszeichen.",
    pt: "Isso não é JSON — verifica as chavetas e as aspas.",
    it: "Non è JSON — controlla parentesi e virgolette.",
    ja: "JSON になっていません。括弧と引用符を確認してください。",
    zh: "这不是 JSON——检查一下括号和引号。",
    hi: "यह JSON नहीं है — कोष्ठक और उद्धरण जाँचें।",
    ar: "هذه ليست JSON — تحقّق من الأقواس وعلامات الاقتباس.",
  },
  "studio.nobox": {
    en: "Nothing will run on this deployment.",
    es: "Aquí no se ejecutará nada.",
    fr: "Rien ne s'exécutera sur cette installation.",
    de: "Auf dieser Installation wird nichts ausgeführt.",
    pt: "Nesta instalação nada será executado.",
    it: "Su questa installazione non verrà eseguito nulla.",
    ja: "この環境では何も実行されません。",
    zh: "此部署不会运行任何东西。",
    hi: "इस इंस्टॉलेशन पर कुछ नहीं चलेगा।",
    ar: "لن يُشغَّل شيء على هذا التنصيب.",
  },
  "studio.limits": {
    en: "What a widget is allowed",
    es: "Lo que un widget puede usar",
    fr: "Ce qu'un widget a le droit d'utiliser",
    de: "Was ein Widget darf",
    pt: "O que um widget pode usar",
    it: "Cosa è concesso a un widget",
    ja: "ウィジェットに許されていること",
    zh: "小工具的限额",
    hi: "विजेट को क्या अनुमत है",
    ar: "ما هو مسموح للأداة",
  },
  "studio.limits.why": {
    en: "Read from the runner, not written here — a screen that stated its own number would go stale the first time the box changed.",
    es: "Se leen del ejecutor, no se escriben aquí: una pantalla con su propio número quedaría obsoleta al primer cambio de la caja.",
    fr: "Lus depuis l'exécuteur, non écrits ici : un écran qui annoncerait son propre chiffre deviendrait faux dès que la boîte change.",
    de: "Vom Runner gelesen, nicht hier geschrieben — ein Bildschirm mit eigener Zahl wäre bei der ersten Änderung veraltet.",
    pt: "Lidos do executor, não escritos aqui — um ecrã com o seu próprio número ficaria desatualizado à primeira mudança.",
    it: "Letti dall'esecutore, non scritti qui: uno schermo con un numero proprio sarebbe superato al primo cambiamento.",
    ja: "実行側から読み取っています。画面に数字を書き込むと、箱が変わった時点で嘘になります。",
    zh: "这些数字读自运行器，而不是写在界面里——界面上自己写的数字，在沙箱一改就过时了。",
    hi: "ये रनर से पढ़े जाते हैं, यहाँ लिखे नहीं — अपनी संख्या बताने वाला स्क्रीन पहले ही बदलाव पर पुराना हो जाता।",
    ar: "تُقرأ من المشغّل ولا تُكتب هنا — شاشة تذكر رقمها الخاص تصير قديمة عند أول تغيير.",
  },
  "studio.limit.wall_seconds": {
    en: "Seconds on the clock",
    es: "Segundos de reloj",
    fr: "Secondes au chronomètre",
    de: "Sekunden auf der Uhr",
    pt: "Segundos de relógio",
    it: "Secondi di orologio",
    ja: "経過時間（秒）",
    zh: "计时秒数",
    hi: "घड़ी के सेकंड",
    ar: "ثوانٍ على الساعة",
  },
  "studio.limit.cpu_seconds": {
    en: "Seconds of processor",
    es: "Segundos de procesador",
    fr: "Secondes de processeur",
    de: "Prozessorsekunden",
    pt: "Segundos de processador",
    it: "Secondi di processore",
    ja: "CPU 時間（秒）",
    zh: "处理器秒数",
    hi: "प्रोसेसर के सेकंड",
    ar: "ثوانٍ من المعالج",
  },
  "studio.limit.heap_mb": {
    en: "Memory, in MB",
    es: "Memoria, en MB",
    fr: "Mémoire, en Mo",
    de: "Speicher in MB",
    pt: "Memória, em MB",
    it: "Memoria, in MB",
    ja: "メモリ（MB）",
    zh: "内存（MB）",
    hi: "मेमोरी, MB में",
    ar: "الذاكرة بالميغابايت",
  },
  "studio.limit.address_space_mb": {
    en: "Address space, in MB",
    es: "Espacio de direcciones, en MB",
    fr: "Espace d'adressage, en Mo",
    de: "Adressraum in MB",
    pt: "Espaço de endereços, em MB",
    it: "Spazio di indirizzi, in MB",
    ja: "アドレス空間（MB）",
    zh: "地址空间（MB）",
    hi: "एड्रेस स्पेस, MB में",
    ar: "مساحة العناوين بالميغابايت",
  },
  "studio.limit.output_bytes": {
    en: "Answer size, in bytes",
    es: "Tamaño de la respuesta, en bytes",
    fr: "Taille de la réponse, en octets",
    de: "Antwortgröße in Bytes",
    pt: "Tamanho da resposta, em bytes",
    it: "Dimensione della risposta, in byte",
    ja: "答えの大きさ（バイト）",
    zh: "返回内容大小（字节）",
    hi: "उत्तर का आकार, बाइट में",
    ar: "حجم الإجابة بالبايت",
  },
  "studio.limit.source_bytes": {
    en: "Code size, in bytes",
    es: "Tamaño del código, en bytes",
    fr: "Taille du code, en octets",
    de: "Codegröße in Bytes",
    pt: "Tamanho do código, em bytes",
    it: "Dimensione del codice, in byte",
    ja: "コードの大きさ（バイト）",
    zh: "代码大小（字节）",
    hi: "कोड का आकार, बाइट में",
    ar: "حجم الشيفرة بالبايت",
  },
  "studio.limit.widgets_per_user": {
    en: "Widgets you may keep",
    es: "Widgets que puedes guardar",
    fr: "Widgets que vous pouvez garder",
    de: "Widgets, die du behalten darfst",
    pt: "Widgets que podes guardar",
    it: "Widget che puoi tenere",
    ja: "保存できるウィジェット数",
    zh: "可保存的小工具数",
    hi: "आप कितने विजेट रख सकते हैं",
    ar: "عدد الأدوات التي يمكنك الاحتفاظ بها",
  },
  "talk.rail.safety": {
    en: "Get help now",
    es: "Pedir ayuda ahora",
    fr: "Obtenir de l'aide",
    de: "Jetzt Hilfe holen",
    pt: "Pedir ajuda agora",
    it: "Chiedi aiuto ora",
    ja: "今すぐ助けを呼ぶ",
    zh: "立即求助",
    hi: "अभी मदद लें",
    ar: "اطلب المساعدة الآن",
  },
  "talk.rail.channel": {
    en: "Speak",
    es: "Hablar",
    fr: "Parler",
    de: "Sprechen",
    pt: "Falar",
    it: "Parla",
    ja: "話す",
    zh: "说话",
    hi: "बोलें",
    ar: "تحدّث",
  },
  "talk.rail.attending": {
    en: "Open camera",
    es: "Abrir cámara",
    fr: "Ouvrir l'appareil photo",
    de: "Kamera öffnen",
    pt: "Abrir câmara",
    it: "Apri fotocamera",
    ja: "カメラを開く",
    zh: "打开相机",
    hi: "कैमरा खोलें",
    ar: "افتح الكاميرا",
  },
  "talk.rail.checkin": {
    en: "Check in",
    es: "Registrarte",
    fr: "Faire le point",
    de: "Melden",
    pt: "Fazer o ponto",
    it: "Fai il punto",
    ja: "チェックイン",
    zh: "打卡",
    hi: "चेक-इन",
    ar: "تسجيل الحالة",
  },
  "talk.rail.meds": {
    en: "Medications",
    es: "Medicamentos",
    fr: "Médicaments",
    de: "Medikamente",
    pt: "Medicamentos",
    it: "Farmaci",
    ja: "服薬",
    zh: "用药",
    hi: "दवाइयाँ",
    ar: "الأدوية",
  },
  "talk.rail.monitor": {
    en: "Live monitoring",
    es: "Monitorización en vivo",
    fr: "Suivi en direct",
    de: "Live-Überwachung",
    pt: "Monitorização ao vivo",
    it: "Monitoraggio dal vivo",
    ja: "ライブ観測",
    zh: "实时监测",
    hi: "लाइव निगरानी",
    ar: "المراقبة المباشرة",
  },
  "talk.rail.careteam": {
    en: "Care team",
    es: "Equipo de cuidados",
    fr: "Équipe soignante",
    de: "Betreuungsteam",
    pt: "Equipa de cuidados",
    it: "Squadra di cura",
    ja: "ケアチーム",
    zh: "照护团队",
    hi: "देखभाल टीम",
    ar: "فريق الرعاية",
  },
  "talk.rail.permits": {
    en: "What it may do",
    es: "Lo que puede hacer",
    fr: "Ce qu'il peut faire",
    de: "Was es darf",
    pt: "O que pode fazer",
    it: "Cosa può fare",
    ja: "できること",
    zh: "它可以做什么",
    hi: "यह क्या कर सकता है",
    ar: "ما يُسمح له بفعله",
  },
  "talk.rail.journal": {
    en: "Journal",
    es: "Diario",
    fr: "Journal",
    de: "Tagebuch",
    pt: "Diário",
    it: "Diario",
    ja: "日記",
    zh: "日志",
    hi: "डायरी",
    ar: "اليوميات",
  },
  "talk.rail.studio": {
    en: "Widgets",
    es: "Widgets",
    fr: "Widgets",
    de: "Widgets",
    pt: "Widgets",
    it: "Widget",
    ja: "ウィジェット",
    zh: "小工具",
    hi: "विजेट",
    ar: "الأدوات",
  },
  "talk.rail.held": {
    en: "What's held",
    es: "Lo que se guarda",
    fr: "Ce qui est conservé",
    de: "Was gespeichert ist",
    pt: "O que está guardado",
    it: "Cosa è conservato",
    ja: "保管されているもの",
    zh: "保存了什么",
    hi: "क्या रखा है",
    ar: "ما هو محفوظ",
  },
  "self.link": {
    en: "Link it",
    es: "Vincúlalo",
    fr: "Le relier",
    de: "Verknüpfen",
    pt: "Ligar",
    it: "Collegalo",
    ja: "リンクする",
    zh: "关联它",
    hi: "इसे जोड़ें",
    ar: "اربطه",
  },
  "self.paste": {
    en: "Paste the profile's id and your owner token from QRME. It has to be a profile QRME calls your own — a made-up one will be refused.",
    es: "Pega el id del perfil y tu token de propietario de QRME. Tiene que ser un perfil que QRME considere tuyo; uno inventado será rechazado.",
    fr: "Collez l’identifiant du profil et votre jeton de propriétaire QRME. Ce doit être un profil que QRME reconnaît comme le vôtre ; un profil inventé sera refusé.",
    de: "Füg die Profil-ID und dein Eigentümer-Token aus QRME ein. Es muss ein Profil sein, das QRME als dein eigenes führt — ein erfundenes wird abgelehnt.",
    pt: "Cole o id do perfil e o seu token de proprietário do QRME. Tem de ser um perfil que o QRME considere seu — um inventado será recusado.",
    it: "Incolla l’id del profilo e il tuo token di proprietario da QRME. Deve essere un profilo che QRME riconosce come tuo — uno inventato verrà rifiutato.",
    ja: "QRME のプロフィール ID と所有者トークンを貼り付けてください。QRME があなた自身のものと認めるプロフィールに限られ、架空のものは拒否されます。",
    zh: "粘贴档案 id 和你在 QRME 的所有者令牌。必须是 QRME 认定属于你自己的档案 — 编造的会被拒绝。",
    hi: "QRME से प्रोफ़ाइल का id और अपना स्वामी टोकन चिपकाएँ। यह ऐसी प्रोफ़ाइल होनी चाहिए जिसे QRME आपकी अपनी मानता हो — बनावटी को अस्वीकार कर दिया जाएगा।",
    ar: "الصق معرِّف الملف ورمز المالك الخاص بك من QRME. يجب أن يكون ملفًا يعتبره QRME ملكك — وسيُرفض أي ملف مُختلق.",
  },
  "self.owner_token": {
    en: "owner token",
    es: "token de propietario",
    fr: "jeton de propriétaire",
    de: "Eigentümer-Token",
    pt: "token de proprietário",
    it: "token di proprietario",
    ja: "所有者トークン",
    zh: "所有者令牌",
    hi: "स्वामी टोकन",
    ar: "رمز المالك",
  },
  "self.link_button": {
    en: "Link this profile",
    es: "Vincular este perfil",
    fr: "Relier ce profil",
    de: "Dieses Profil verknüpfen",
    pt: "Ligar este perfil",
    it: "Collega questo profilo",
    ja: "このプロフィールをリンク",
    zh: "关联此档案",
    hi: "इस प्रोफ़ाइल को जोड़ें",
    ar: "اربط هذا الملف",
  },
  "self.may_know": {
    en: "What it may know",
    es: "Qué puede saber",
    fr: "Ce qu’il peut savoir",
    de: "Was es wissen darf",
    pt: "O que pode saber",
    it: "Cosa può sapere",
    ja: "伝えてよいこと",
    zh: "它可以知道什么",
    hi: "यह क्या जान सकता है",
    ar: "ما يمكن أن يعرفه",
  },
  "self.until_tick": {
    en: "Nothing is passed on until you tick it.",
    es: "No se transmite nada hasta que lo marques.",
    fr: "Rien n’est transmis tant que vous ne l’avez pas coché.",
    de: "Nichts wird weitergegeben, bis du es ankreuzt.",
    pt: "Nada é transmitido até o marcar.",
    it: "Non viene trasmesso nulla finché non lo spunti.",
    ja: "チェックするまで何も伝えられません。",
    zh: "在你勾选之前，不会转达任何内容。",
    hi: "जब तक आप चुनें नहीं, कुछ भी नहीं भेजा जाता।",
    ar: "لا يُنقل شيء حتى تحدده.",
  },
  "self.exactly": {
    en: "Exactly what would be sent",
    es: "Exactamente lo que se enviaría",
    fr: "Exactement ce qui serait envoyé",
    de: "Genau das, was gesendet würde",
    pt: "Exatamente o que seria enviado",
    it: "Esattamente ciò che verrebbe inviato",
    ja: "送られる内容そのもの",
    zh: "确切会发送的内容",
    hi: "ठीक वही जो भेजा जाएगा",
    ar: "ما سيُرسل بالضبط",
  },
  "self.nothing_ticked": {
    en: "Nothing, because nothing is ticked.",
    es: "Nada, porque no hay nada marcado.",
    fr: "Rien, parce que rien n’est coché.",
    de: "Nichts, weil nichts angekreuzt ist.",
    pt: "Nada, porque nada está marcado.",
    it: "Niente, perché non è spuntato nulla.",
    ja: "何もチェックされていないため、何もありません。",
    zh: "没有内容，因为没有勾选任何项。",
    hi: "कुछ नहीं, क्योंकि कुछ चुना नहीं गया है।",
    ar: "لا شيء، لأنه لم يتم تحديد أي شيء.",
  },
  "self.message_itself": {
    en: "This is the message itself, not a description of it. Medication is the one part made of your own words, so it shows the names as you typed them.",
    es: "Este es el mensaje en sí, no una descripción. La medicación es la única parte hecha con tus propias palabras, así que muestra los nombres tal como los escribiste.",
    fr: "Ceci est le message lui-même, pas sa description. Les médicaments sont la seule partie faite de vos propres mots : les noms s’affichent tels que vous les avez saisis.",
    de: "Dies ist die Nachricht selbst, keine Beschreibung. Die Medikation ist der einzige Teil aus deinen eigenen Worten, daher erscheinen die Namen so, wie du sie eingegeben hast.",
    pt: "Esta é a mensagem em si, não uma descrição. A medicação é a única parte feita das suas próprias palavras, por isso mostra os nomes tal como os escreveu.",
    it: "Questo è il messaggio stesso, non una sua descrizione. I farmaci sono l’unica parte fatta di parole tue, quindi i nomi appaiono come li hai scritti.",
    ja: "これは説明ではなく、メッセージそのものです。薬だけはご自身の言葉でできているため、入力したとおりの名称が表示されます。",
    zh: "这就是消息本身，而不是对它的描述。用药是唯一由你自己的措辞构成的部分，因此名称按你输入的原样显示。",
    hi: "यह संदेश स्वयं है, उसका विवरण नहीं। दवा ही एकमात्र हिस्सा है जो आपके अपने शब्दों से बना है, इसलिए नाम वैसे ही दिखते हैं जैसे आपने लिखे।",
    ar: "هذه هي الرسالة نفسها، لا وصفٌ لها. الدواء هو الجزء الوحيد المكوَّن من كلماتك، لذا تظهر الأسماء كما كتبتها.",
  },
  "self.send": {
    en: "Send this to my profile",
    es: "Enviar esto a mi perfil",
    fr: "Envoyer ceci à mon profil",
    de: "Dies an mein Profil senden",
    pt: "Enviar isto ao meu perfil",
    it: "Invia questo al mio profilo",
    ja: "これを自分のプロフィールに送る",
    zh: "把这个发送到我的档案",
    hi: "इसे मेरी प्रोफ़ाइल को भेजें",
    ar: "أرسل هذا إلى ملفي",
  },
  "self.stop": {
    en: "Stop",
    es: "Detener",
    fr: "Arrêter",
    de: "Beenden",
    pt: "Parar",
    it: "Ferma",
    ja: "やめる",
    zh: "停止",
    hi: "रोकें",
    ar: "إيقاف",
  },
  "self.unlink_note": {
    en: "Unlinking removes the token and everything you ticked. What the profile was already told stays in its own source list, in QRME, where you can delete it.",
    es: "Desvincular elimina el token y todo lo que marcaste. Lo que ya se le dijo al perfil permanece en su propia lista de fuentes, en QRME, donde puedes borrarlo.",
    fr: "Le fait de délier supprime le jeton et tout ce que vous aviez coché. Ce qui a déjà été dit au profil reste dans sa liste de sources, dans QRME, où vous pouvez le supprimer.",
    de: "Das Trennen entfernt das Token und alles, was du angekreuzt hattest. Was dem Profil bereits mitgeteilt wurde, bleibt in dessen Quellenliste in QRME, wo du es löschen kannst.",
    pt: "Desligar remove o token e tudo o que marcou. O que já foi dito ao perfil fica na sua própria lista de fontes, no QRME, onde o pode apagar.",
    it: "Scollegare rimuove il token e tutto ciò che avevi spuntato. Quanto già detto al profilo resta nel suo elenco di fonti, in QRME, dove puoi eliminarlo.",
    ja: "リンクを解除するとトークンとチェックした内容がすべて削除されます。すでにプロフィールに伝えた内容は QRME のソース一覧に残り、そこで削除できます。",
    zh: "取消关联会移除令牌和你勾选的全部内容。已经告诉档案的内容仍留在 QRME 的来源列表中，你可以在那里删除。",
    hi: "अनलिंक करने से टोकन और आपके चुने हुए सब कुछ हट जाता है। प्रोफ़ाइल को पहले जो बताया जा चुका है वह QRME की उसकी स्रोत सूची में रहता है, जहाँ आप उसे मिटा सकते हैं।",
    ar: "يؤدي إلغاء الربط إلى إزالة الرمز وكل ما حددته. ويبقى ما قيل للملف سابقًا في قائمة مصادره داخل QRME، حيث يمكنك حذفه.",
  },
  "self.unlink": {
    en: "Unlink",
    es: "Desvincular",
    fr: "Dissocier",
    de: "Trennen",
    pt: "Desvincular",
    it: "Scollega",
    ja: "リンク解除",
    zh: "取消关联",
    hi: "अनलिंक करें",
    ar: "إلغاء الربط",
  },
  "self.linked_note": {
    en: "Linked. Nothing is shared yet.",
    es: "Vinculado. Todavía no se comparte nada.",
    fr: "Relié. Rien n’est encore partagé.",
    de: "Verknüpft. Es wird noch nichts geteilt.",
    pt: "Ligado. Ainda não é partilhado nada.",
    it: "Collegato. Non è ancora condiviso nulla.",
    ja: "リンクしました。まだ何も共有されていません。",
    zh: "已关联。尚未共享任何内容。",
    hi: "जुड़ गया। अभी कुछ भी साझा नहीं किया गया।",
    ar: "تم الربط. لم تتم مشاركة أي شيء بعد.",
  },
  "self.saved": {
    en: "Saved.",
    es: "Guardado.",
    fr: "Enregistré.",
    de: "Gespeichert.",
    pt: "Guardado.",
    it: "Salvato.",
    ja: "保存しました。",
    zh: "已保存。",
    hi: "सहेजा गया।",
    ar: "تم الحفظ.",
  },
  "self.sent": {
    en: "Sent.",
    es: "Enviado.",
    fr: "Envoyé.",
    de: "Gesendet.",
    pt: "Enviado.",
    it: "Inviato.",
    ja: "送信しました。",
    zh: "已发送。",
    hi: "भेज दिया गया।",
    ar: "تم الإرسال.",
  },
  "self.unlinked": {
    en: "Unlinked.",
    es: "Desvinculado.",
    fr: "Délié.",
    de: "Getrennt.",
    pt: "Desligado.",
    it: "Scollegato.",
    ja: "リンクを解除しました。",
    zh: "已取消关联。",
    hi: "अनलिंक कर दिया गया।",
    ar: "تم إلغاء الربط.",
  },
  "self.signin": {
    en: "Sign in first.",
    es: "Inicia sesión primero.",
    fr: "Connectez-vous d’abord.",
    de: "Melde dich zuerst an.",
    pt: "Inicie sessão primeiro.",
    it: "Accedi prima.",
    ja: "先にサインインしてください。",
    zh: "请先登录。",
    hi: "पहले साइन इन करें।",
    ar: "سجّل الدخول أولاً.",
  },
  "nav.selfprofile": {
    en: "Your own profile",
    es: "Tu propio perfil",
    fr: "Votre propre profil",
    de: "Dein eigenes Profil",
    pt: "O seu próprio perfil",
    it: "Il tuo profilo",
    ja: "あなた自身のプロフィール",
    zh: "你自己的档案",
    hi: "आपकी अपनी प्रोफ़ाइल",
    ar: "ملفك الشخصي",
  },
  "nav.coach": {
    en: "Coach",
    es: "Coach",
    fr: "Coach",
    de: "Coach",
    pt: "Coach",
    it: "Coach",
    ja: "コーチ",
    zh: "教练",
    hi: "कोच",
    ar: "مدرب",
  },
  "nav.wellness": {
    en: "Wellness",
    es: "Bienestar",
    fr: "Bien-être",
    de: "Wohlbefinden",
    pt: "Bem-estar",
    it: "Benessere",
    ja: "ウェルネス",
    zh: "身心健康",
    hi: "कल्याण",
    ar: "العافية",
  },
  "nav.checkin": {
    en: "Check-in",
    es: "Registro",
    fr: "Bilan",
    de: "Check-in",
    pt: "Check-in",
    it: "Check-in",
    ja: "チェックイン",
    zh: "签到",
    hi: "चेक-इन",
    ar: "تسجيل الحالة",
  },
  "nav.journal": {
    en: "Journal",
    es: "Diario",
    fr: "Journal",
    de: "Tagebuch",
    pt: "Diário",
    it: "Diario",
    ja: "日記",
    zh: "日志",
    hi: "डायरी",
    ar: "اليوميات",
  },
  "nav.aims": {
    en: "What you're working on",
    es: "En qué estás trabajando",
    fr: "Ce sur quoi vous travaillez",
    de: "Woran du arbeitest",
    pt: "Aquilo em que está a trabalhar",
    it: "Su cosa stai lavorando",
    ja: "取り組んでいること",
    zh: "你正在努力的事",
    hi: "आप किस पर काम कर रहे हैं",
    ar: "ما تعمل عليه",
  },
  "nav.wards": {
    en: "Who you watch",
    es: "A quién vigilas",
    fr: "Qui vous surveillez",
    de: "Wen du im Blick hast",
    pt: "Quem acompanha",
    it: "Chi tieni d'occhio",
    ja: "見守っている人",
    zh: "你在照看的人",
    hi: "आप किसका ध्यान रखते हैं",
    ar: "من ترعاهم",
  },
  "nav.attending": {
    en: "Who else is looking",
    es: "Quién más está pendiente",
    fr: "Qui d'autre veille",
    de: "Wer sonst hinschaut",
    pt: "Quem mais está atento",
    it: "Chi altro sta guardando",
    ja: "ほかに見守っている人",
    zh: "还有谁在关注",
    hi: "और कौन देख रहा है",
    ar: "من غيرك يراقب",
  },
  // The hands. Carried verbatim from the sibling console — one
  // wording for one faculty, so somebody who has read the grant
  // card on one product has read it on the other.
  "hnd.again": {
    en: "Things it can do again", es: "Cosas que puede repetir", fr: "Ce qu'il peut refaire", de: "Was es wiederholen kann", pt: "Coisas que pode repetir", it: "Cose che può rifare", ja: "またできること", zh: "它能重复做的事", hi: "जो यह दोबारा कर सकता है", ar: "أشياء يمكنه تكرارها",
  },
  "hnd.again.go": {
    en: "Do it again", es: "Repetir", fr: "Refaire", de: "Wiederholen", pt: "Repetir", it: "Rifallo", ja: "もう一度", zh: "再做一次", hi: "फिर करें", ar: "كرّره",
  },
  "hnd.again.pitch": {
    en: "Learned by watching you, or dictated in words. Either way it is a memory of moves and never a stored permission — doing it again goes through a live grant like any fresh decision.", es: "Aprendido mirándote, o dictado con palabras. En ambos casos es un recuerdo de movimientos y nunca un permiso guardado — repetirlo pasa por un permiso vigente como cualquier decisión nueva.", fr: "Appris en vous regardant, ou dicté avec des mots. Dans les deux cas c'est un souvenir de gestes et jamais une permission stockée — le refaire passe par une permission en cours comme toute décision nouvelle.", de: "Durch Zusehen gelernt oder in Worten diktiert. So oder so ist es eine Erinnerung an Bewegungen und nie eine gespeicherte Erlaubnis — die Wiederholung geht durch eine gültige Erlaubnis wie jede neue Entscheidung.", pt: "Aprendido a observá-lo, ou ditado por palavras. Em qualquer dos casos é uma memória de movimentos e nunca uma permissão guardada — repeti-lo passa por uma permissão em vigor como qualquer decisão nova.", it: "Imparato guardandoti, o dettato a parole. In ogni caso è un ricordo di mosse e mai un permesso conservato — rifarlo passa da un permesso valido come ogni decisione nuova.", ja: "あなたを見て覚えたか、言葉で伝えられたもの。どちらも動作の記憶であって、保存された許可ではありません — 繰り返すときも、新しい判断と同じく有効な許可を通ります。", zh: "看你做而学会的，或是用话口述的。无论哪种，它都只是动作的记忆，绝不是存下来的许可 — 再做一次同样要经过一份有效的许可，和任何新决定一样。", hi: "आपको देखकर सीखा, या शब्दों में बताया गया। दोनों ही हाल में यह चालों की स्मृति है, कोई सहेजी हुई अनुमति नहीं — दोबारा करना भी किसी नए निर्णय की तरह एक जीवित अनुमति से होकर जाता है।", ar: "تعلّمه بمشاهدتك، أو أُملي عليه بالكلمات. في الحالتين هو ذاكرة حركات لا إذن مخزَّن — وتكراره يمرّ عبر إذن سارٍ كأي قرار جديد.",
  },
  "hnd.always": {
    en: "Looking, asking and stopping are always included — a hand that cannot see, ask or stop is a worse hand, not a safer one.", es: "Mirar, preguntar y detenerse van siempre incluidos: una mano que no puede ver, preguntar ni detenerse es una mano peor, no más segura.", fr: "Regarder, demander et s'arrêter sont toujours inclus : une main qui ne peut ni voir, ni demander, ni s'arrêter est une moins bonne main, pas une main plus sûre.", de: "Sehen, Fragen und Aufhören sind immer dabei — eine Hand, die nicht sehen, fragen oder aufhören kann, ist eine schlechtere Hand, keine sicherere.", pt: "Olhar, perguntar e parar estão sempre incluídos — uma mão que não pode ver, perguntar ou parar é uma mão pior, não mais segura.", it: "Guardare, chiedere e fermarsi sono sempre inclusi: una mano che non può vedere, chiedere o fermarsi è una mano peggiore, non più sicura.", ja: "見ること、尋ねること、やめることは常に含まれます — 見ることも尋ねることもやめることもできない手は、より安全な手ではなく、より悪い手です。", zh: "查看、询问和停止始终包含在内 — 一只不能看、不能问、不能停的手是更差的手，而不是更安全的手。", hi: "देखना, पूछना और रुकना हमेशा शामिल हैं — जो हाथ देख, पूछ या रुक नहीं सकता वह बेहतर नहीं, बदतर हाथ है।", ar: "النظر والسؤال والتوقّف مشمولة دائمًا — فاليد التي لا تستطيع أن ترى أو تسأل أو تتوقّف يد أسوأ لا أكثر أمانًا.",
  },
  "hnd.choose": {
    en: "Let it choose the next move", es: "Deja que elija el siguiente movimiento", fr: "Laissez-le choisir le geste suivant", de: "Lass es die nächste Bewegung wählen", pt: "Deixa-o escolher o próximo movimento", it: "Lascia che scelga la mossa successiva", ja: "次の一手を選ばせる", zh: "让它选择下一步", hi: "इसे अगली चाल चुनने दें", ar: "دعه يختار الحركة التالية",
  },
  "hnd.choose.go": {
    en: "Choose", es: "Elegir", fr: "Choisir", de: "Wählen", pt: "Escolher", it: "Scegli", ja: "選ぶ", zh: "选择", hi: "चुनें", ar: "اختر",
  },
  "hnd.choose.ph": {
    en: "what is on the screen, in your words", es: "qué hay en la pantalla, con tus palabras", fr: "ce qu'il y a à l'écran, avec vos mots", de: "was auf dem Bildschirm ist, in deinen Worten", pt: "o que está no ecrã, nas tuas palavras", it: "cosa c'è sullo schermo, con parole tue", ja: "画面に何があるか、あなたの言葉で", zh: "屏幕上有什么，用你的话说", hi: "स्क्रीन पर क्या है, आपके शब्दों में", ar: "ما على الشاشة، بكلماتك",
  },
  "hnd.dictate.go": {
    en: "Write it down", es: "Anotarlo", fr: "Le noter", de: "Aufschreiben", pt: "Anotar", it: "Annotalo", ja: "書き留める", zh: "记下来", hi: "लिख लें", ar: "دوّنه",
  },
  "hnd.dictate.ph": {
    en: "one step a line — press: New event", es: "un paso por línea — press: Nuevo evento", fr: "une étape par ligne — press: Nouvel événement", de: "ein Schritt pro Zeile — press: Neuer Termin", pt: "um passo por linha — press: Novo evento", it: "un passo per riga — press: Nuovo evento", ja: "1行に1手 — 「press」: 新しい予定", zh: "每行一步 — 「press」：新建事件", hi: "हर पंक्ति में एक चरण — press: नया इवेंट", ar: "خطوة في كل سطر — press: حدث جديد",
  },
  "hnd.errand": {
    en: "what it should do", es: "qué debe hacer", fr: "ce qu'il doit faire", de: "was es tun soll", pt: "o que deve fazer", it: "cosa deve fare", ja: "してほしいこと", zh: "它该做什么", hi: "इसे क्या करना है", ar: "ما ينبغي أن يفعله",
  },
  "hnd.gave": {
    en: "Hands given for {places}.", es: "Manos dadas para {places}.", fr: "Mains données pour {places}.", de: "Hände gegeben für {places}.", pt: "Mãos dadas para {places}.", it: "Mani date per {places}.", ja: "{places} に手を与えました。", zh: "已为 {places} 给出双手。", hi: "{places} के लिए हाथ दिए गए।", ar: "مُنحت اليدان لـ {places}.",
  },
  "hnd.give": {
    en: "Give it hands", es: "Darle manos", fr: "Lui donner des mains", de: "Ihm Hände geben", pt: "Dar-lhe mãos", it: "Dargli le mani", ja: "手を与える", zh: "给它双手", hi: "इसे हाथ दें", ar: "امنحه يدين",
  },
  "hnd.give.go": {
    en: "Give", es: "Dar", fr: "Donner", de: "Geben", pt: "Dar", it: "Dai", ja: "与える", zh: "给予", hi: "दें", ar: "امنح",
  },
  "hnd.give.pitch": {
    en: "Name the apps or sites, the moves, the minutes and the steps. All four are limits, and all four are enforced where the move happens rather than on this screen.", es: "Nombra las aplicaciones o sitios, los movimientos, los minutos y los pasos. Los cuatro son límites, y los cuatro se aplican donde ocurre el movimiento, no en esta pantalla.", fr: "Nommez les applications ou sites, les gestes, les minutes et les étapes. Ces quatre éléments sont des limites, appliquées là où le geste se produit et non sur cet écran.", de: "Nenn die Apps oder Seiten, die Bewegungen, die Minuten und die Schritte. Alle vier sind Grenzen, und alle vier gelten dort, wo die Bewegung geschieht, nicht auf diesem Bildschirm.", pt: "Nomeie as aplicações ou sites, os movimentos, os minutos e os passos. Os quatro são limites, e os quatro são impostos onde o movimento acontece, não neste ecrã.", it: "Indica le app o i siti, le mosse, i minuti e i passi. Tutti e quattro sono limiti, imposti dove avviene la mossa e non su questo schermo.", ja: "アプリまたはサイト、動作、分数、手数を指定します。四つとも上限であり、この画面ではなく動作が起きる場所で守られます。", zh: "写明应用或网站、动作、分钟数与步数。这四项都是上限，都在动作发生之处生效，而不是在这个屏幕上。", hi: "ऐप या साइट, चालें, मिनट और चरण बताएँ। चारों सीमाएँ हैं, और चारों वहीं लागू होती हैं जहाँ चाल चलती है, इस स्क्रीन पर नहीं।", ar: "سمِّ التطبيقات أو المواقع والحركات والدقائق والخطوات. الأربعة حدود، وتُطبَّق جميعها حيث تقع الحركة لا على هذه الشاشة.",
  },
  "hnd.heard": {
    en: "Heard: {places} · {verbs}", es: "Oído: {places} · {verbs}", fr: "Entendu : {places} · {verbs}", de: "Gehört: {places} · {verbs}", pt: "Ouvido: {places} · {verbs}", it: "Sentito: {places} · {verbs}", ja: "聞き取り: {places} · {verbs}", zh: "听到：{places} · {verbs}", hi: "सुना: {places} · {verbs}", ar: "المسموع: {places} · {verbs}",
  },
  "hnd.landed.landed": {
    en: "it happened", es: "ocurrió", fr: "c'est arrivé", de: "es ist passiert", pt: "aconteceu", it: "è successo", ja: "実行された", zh: "已发生", hi: "यह हुआ", ar: "حدث فعلًا",
  },
  "hnd.landed.missed": {
    en: "it did not happen", es: "no ocurrió", fr: "ce n'est pas arrivé", de: "es ist nicht passiert", pt: "não aconteceu", it: "non è successo", ja: "実行されなかった", zh: "未发生", hi: "यह नहीं हुआ", ar: "لم يحدث",
  },
  "hnd.landed.rehearsed": {
    en: "a rehearsal — nothing was touched", es: "un ensayo: no se tocó nada", fr: "une répétition — rien n'a été touché", de: "eine Probe — nichts wurde angefasst", pt: "um ensaio — nada foi tocado", it: "una prova: non è stato toccato nulla", ja: "リハーサル — 何にも触れていない", zh: "一次排练——什么都没碰", hi: "एक पूर्वाभ्यास — कुछ भी नहीं छुआ गया", ar: "بروفة — لم يُلمس شيء",
  },
  "hnd.landed.unknown": {
    en: "nobody said whether it happened", es: "nadie dijo si ocurrió", fr: "personne n'a dit si c'est arrivé", de: "niemand hat gesagt, ob es passiert ist", pt: "ninguém disse se aconteceu", it: "nessuno ha detto se è successo", ja: "実行されたかどうか、誰も報告していない", zh: "没人说它是否发生", hi: "किसी ने नहीं बताया कि यह हुआ या नहीं", ar: "لم يقل أحد إن كان قد حدث",
  },
  "hnd.minutes": {
    en: "Minutes", es: "Minutos", fr: "Minutes", de: "Minuten", pt: "Minutos", it: "Minuti", ja: "分", zh: "分钟", hi: "मिनट", ar: "دقائق",
  },
  "hnd.mode.act": {
    en: "do the work", es: "hacer el trabajo", fr: "faire le travail", de: "die Arbeit tun", pt: "fazer o trabalho", it: "fare il lavoro", ja: "作業する", zh: "动手做", hi: "काम करे", ar: "يؤدي العمل",
  },
  "hnd.mode.watch": {
    en: "watch only", es: "solo mirar", fr: "regarder seulement", de: "nur zusehen", pt: "apenas observar", it: "solo guardare", ja: "見るだけ", zh: "只观看", hi: "केवल देखे", ar: "المشاهدة فقط",
  },
  "hnd.motor": {
    en: "Run this on the machine you want worked", es: "Ejecuta esto en la máquina que quieres que maneje", fr: "Lancez ceci sur la machine à faire manœuvrer", de: "Führe das auf der Maschine aus, die bedient werden soll", pt: "Executa isto na máquina que queres que seja usada", it: "Esegui questo sulla macchina che vuoi far usare", ja: "操作させたいマシンでこれを実行してください", zh: "在你想让它操作的那台机器上运行这个", hi: "जिस मशीन पर काम कराना है, उस पर यह चलाएँ", ar: "شغّل هذا على الجهاز الذي تريد تشغيله",
  },
  "hnd.motor.copied": {
    en: "Copied. Paste it into a terminal on that machine.", es: "Copiado. Pégalo en una terminal de esa máquina.", fr: "Copié. Collez-le dans un terminal sur cette machine.", de: "Kopiert. Füg es in ein Terminal auf dieser Maschine ein.", pt: "Copiado. Cole-o num terminal dessa máquina.", it: "Copiato. Incollalo in un terminale su quella macchina.", ja: "コピーしました。そのマシンのターミナルに貼り付けてください。", zh: "已复制。粘贴到那台机器的终端里。", hi: "कॉपी हो गया। उस मशीन के टर्मिनल में चिपकाएँ।", ar: "نُسخ. الصقه في طرفية على تلك الآلة.",
  },
  "hnd.motor.copy": {
    en: "Copy the command", es: "Copiar el comando", fr: "Copier la commande", de: "Befehl kopieren", pt: "Copiar o comando", it: "Copia il comando", ja: "コマンドをコピー", zh: "复制命令", hi: "कमांड कॉपी करें", ar: "انسخ الأمر",
  },
  "hnd.motor.dry": {
    en: "It prints what it would do and touches nothing. Add --live when you want it to act.", es: "Imprime lo que haría y no toca nada. Añade --live cuando quieras que actúe.", fr: "Il imprime ce qu'il ferait et ne touche à rien. Ajoutez --live quand vous voulez qu'il agisse.", de: "Es druckt, was es tun würde, und rührt nichts an. Füge --live hinzu, wenn es handeln soll.", pt: "Imprime o que faria e não toca em nada. Acrescenta --live quando quiseres que aja.", it: "Stampa cosa farebbe e non tocca nulla. Aggiungi --live quando vuoi che agisca.", ja: "何をするかを表示するだけで、何にも触れません。実際に動かすときは --live を付けてください。", zh: "它只打印将要做什么，不碰任何东西。想让它真正动手时加上 --live。", hi: "यह बताता है कि क्या करता, छूता कुछ नहीं। जब चाहें कि यह सचमुच करे, --live जोड़ें।", ar: "يطبع ما كان سيفعله ولا يلمس شيئًا. أضف ‎--live حين تريده أن يتصرف.",
  },
  "hnd.motor.install": {
    en: "Copy the install line", es: "Copiar la línea de instalación", fr: "Copier la ligne d'installation", de: "Installationszeile kopieren", pt: "Copiar a linha de instalação", it: "Copia la riga di installazione", ja: "導入用の行をコピー", zh: "复制安装那一行", hi: "इंस्टॉल वाली पंक्ति कॉपी करें", ar: "انسخ سطر التثبيت",
  },
  "hnd.motor.installed": {
    en: "Copied. Run it once on that machine, then the command below.", es: "Copiado. Ejecútalo una vez en esa máquina y luego el comando de abajo.", fr: "Copié. Lancez-le une fois sur cette machine, puis la commande ci-dessous.", de: "Kopiert. Führ es einmal auf jener Maschine aus, dann den Befehl darunter.", pt: "Copiado. Execute-o uma vez nessa máquina e depois o comando abaixo.", it: "Copiato. Eseguilo una volta su quella macchina, poi il comando qui sotto.", ja: "コピーしました。そのマシンで一度実行し、次に下のコマンドを実行してください。", zh: "已复制。在那台机器上运行一次，然后运行下面的命令。", hi: "कॉपी हो गया। उस मशीन पर एक बार चलाएँ, फिर नीचे वाली कमांड।", ar: "نُسخ. شغّله مرة واحدة على تلك الآلة، ثم الأمر أدناه.",
  },
  "hnd.motor.select": {
    en: "This browser will not reach the clipboard — select the line above and copy it.", es: "Este navegador no llega al portapapeles: selecciona la línea de arriba y cópiala.", fr: "Ce navigateur n'accède pas au presse-papiers — sélectionnez la ligne ci-dessus et copiez-la.", de: "Dieser Browser kommt nicht an die Zwischenablage — markier die Zeile oben und kopier sie.", pt: "Este navegador não alcança a área de transferência — selecione a linha acima e copie-a.", it: "Questo browser non raggiunge gli appunti: seleziona la riga qui sopra e copiala.", ja: "このブラウザーはクリップボードに届きません — 上の行を選択してコピーしてください。", zh: "此浏览器无法访问剪贴板 — 请选中上面那行并复制。", hi: "यह ब्राउज़र क्लिपबोर्ड तक नहीं पहुँचता — ऊपर की पंक्ति चुनकर कॉपी करें।", ar: "هذا المتصفح لا يصل إلى الحافظة — حدّد السطر أعلاه وانسخه.",
  },
  "hnd.motor.sub": {
    en: "This deployment cannot move a cursor — a small program on that machine does, started by you and stopped by you. Install it once with the line below. It will ask for your token rather than take it here: the program photographs the screen it runs on, so a token typed into that window would be in every picture it sends.", es: "Este despliegue no puede mover un cursor: lo hace un pequeño programa en esa máquina, iniciado por ti y detenido por ti. Instálalo una vez con la línea de abajo. Te pedirá tu token en vez de tomarlo aquí: el programa fotografía la pantalla en la que se ejecuta, así que un token escrito en esa ventana estaría en cada imagen que envía.", fr: "Ce déploiement ne peut pas déplacer un curseur — un petit programme sur cette machine le fait, lancé par vous et arrêté par vous. Installez-le une fois avec la ligne ci-dessous. Il demandera votre jeton plutôt que de le prendre ici : le programme photographie l'écran sur lequel il tourne, donc un jeton tapé dans cette fenêtre serait dans chaque image qu'il envoie.", de: "Diese Installation kann keinen Cursor bewegen — das tut ein kleines Programm auf jener Maschine, von dir gestartet und von dir gestoppt. Richte es einmal mit der Zeile unten ein. Es fragt nach deinem Token, statt ihn hier zu nehmen: das Programm fotografiert den Bildschirm, auf dem es läuft, ein in jenes Fenster getippter Token wäre also in jedem Bild, das es schickt.", pt: "Esta instalação não pode mover um cursor — um pequeno programa nessa máquina fá-lo, iniciado por si e parado por si. Instale-o uma vez com a linha abaixo. Pedirá o seu token em vez de o receber aqui: o programa fotografa o ecrã em que corre, por isso um token escrito nessa janela estaria em cada imagem que envia.", it: "Questa installazione non può muovere un cursore: lo fa un piccolo programma su quella macchina, avviato da te e fermato da te. Installalo una volta con la riga qui sotto. Chiederà il tuo token invece di prenderlo qui: il programma fotografa lo schermo su cui gira, quindi un token digitato in quella finestra sarebbe in ogni immagine che invia.", ja: "この環境はカーソルを動かせません。動かすのは、あなたが起動し、あなたが止める、そのマシン上の小さなプログラムです。下の行で一度だけ導入してください。トークンはここで渡すのではなく、プログラムが尋ねます。プログラムは自分が動いている画面を撮影するので、その窓に打ち込まれたトークンは送られるすべての画像に写ります。", zh: "本部署无法移动光标——那台机器上的一个小程序才能，由你启动、由你停止。用下面这一行安装一次。它会向你索取令牌，而不是在这里取走：该程序会拍摄它自己所在的屏幕，写进那个窗口的令牌会出现在它发送的每一张图里。", hi: "यह तैनाती कर्सर नहीं हिला सकती — वह काम उस मशीन पर चलने वाला एक छोटा प्रोग्राम करता है, जिसे आप शुरू करते हैं और आप ही रोकते हैं। नीचे दी गई पंक्ति से इसे एक बार इंस्टॉल करें। वह आपका टोकन यहाँ लेने के बजाय पूछेगा: प्रोग्राम उसी स्क्रीन की तस्वीर लेता है जिस पर वह चलता है, इसलिए उस विंडो में टाइप किया टोकन उसकी भेजी हर तस्वीर में होगा।", ar: "هذا النشر لا يستطيع تحريك مؤشر — يفعل ذلك برنامج صغير على تلك الآلة، تشغّله أنت وتوقفه أنت. ثبّته مرة واحدة بالسطر أدناه. سيطلب منك الرمز بدل أخذه هنا: البرنامج يصوّر الشاشة التي يعمل عليها، فالرمز المكتوب في تلك النافذة سيكون في كل صورة يرسلها.",
  },
  "hnd.motor.token": {
    en: "Copy my token", es: "Copiar mi token", fr: "Copier mon jeton", de: "Mein Token kopieren", pt: "Copiar o meu token", it: "Copia il mio token", ja: "自分のトークンをコピー", zh: "复制我的令牌", hi: "मेरा टोकन कॉपी करें", ar: "انسخ رمزي",
  },
  "hnd.motor.token.copied": {
    en: "Copied, not shown. Paste it when the program asks — nothing will appear as you type.", es: "Copiado, no mostrado. Pégalo cuando el programa lo pida: no aparecerá nada mientras escribes.", fr: "Copié, non affiché. Collez-le quand le programme le demande — rien n'apparaîtra pendant la saisie.", de: "Kopiert, nicht angezeigt. Füg es ein, wenn das Programm fragt — beim Tippen erscheint nichts.", pt: "Copiado, não mostrado. Cole-o quando o programa pedir — nada aparecerá enquanto escreve.", it: "Copiato, non mostrato. Incollalo quando il programma lo chiede: mentre digiti non apparirà nulla.", ja: "コピーしました。画面には出していません。プログラムに聞かれたら貼り付けてください — 入力しても何も表示されません。", zh: "已复制，未显示。程序询问时粘贴即可 — 输入时不会有任何显示。", hi: "कॉपी हो गया, दिखाया नहीं गया। प्रोग्राम पूछे तब चिपकाएँ — टाइप करते समय कुछ नहीं दिखेगा।", ar: "نُسخ، ولم يُعرض. الصقه حين يطلبه البرنامج — لن يظهر شيء أثناء الكتابة.",
  },
  "hnd.motor.token.show": {
    en: "show it instead", es: "mostrarlo en su lugar", fr: "l'afficher plutôt", de: "stattdessen anzeigen", pt: "mostrá-lo em vez disso", it: "mostralo invece", ja: "代わりに表示する", zh: "改为显示它", hi: "इसके बजाय दिखाएँ", ar: "أظهره بدلًا من ذلك",
  },
  "hnd.motor.token.stuck": {
    en: "This browser will not reach the clipboard. Open the fold below and copy it by hand.", es: "Este navegador no llega al portapapeles. Abre el pliegue de abajo y cópialo a mano.", fr: "Ce navigateur n'accède pas au presse-papiers. Ouvrez le repli ci-dessous et copiez-le à la main.", de: "Dieser Browser kommt nicht an die Zwischenablage. Klapp unten auf und kopier es von Hand.", pt: "Este navegador não alcança a área de transferência. Abra a dobra abaixo e copie-o à mão.", it: "Questo browser non raggiunge gli appunti. Apri la piega qui sotto e copialo a mano.", ja: "このブラウザーはクリップボードに届きません。下の折りたたみを開いて手で写してください。", zh: "此浏览器无法访问剪贴板。展开下方的折叠内容，手动复制。", hi: "यह ब्राउज़र क्लिपबोर्ड तक नहीं पहुँचता। नीचे की तह खोलकर हाथ से कॉपी करें।", ar: "هذا المتصفح لا يصل إلى الحافظة. افتح الطيّة أدناه وانسخه يدويًا.",
  },
  "hnd.motor.token.warn": {
    en: "Opening this puts your token on the screen the hands are about to photograph. Close it again before you begin.", es: "Abrir esto pone tu token en la pantalla que las manos van a fotografiar. Ciérralo antes de empezar.", fr: "L'ouvrir met votre jeton sur l'écran que les mains vont photographier. Refermez-le avant de commencer.", de: "Das hier zu öffnen legt dein Token auf den Bildschirm, den die Hände gleich fotografieren. Mach es wieder zu, bevor du anfängst.", pt: "Abrir isto põe o seu token no ecrã que as mãos vão fotografar. Feche-o antes de começar.", it: "Aprirlo mette il tuo token sullo schermo che le mani stanno per fotografare. Richiudilo prima di cominciare.", ja: "これを開くと、手がこれから撮影する画面にトークンが載ります。始める前に閉じてください。", zh: "展开它会把你的令牌放在双手即将拍摄的屏幕上。开始前请合上。", hi: "इसे खोलने पर आपका टोकन उसी स्क्रीन पर आ जाता है जिसकी तस्वीर हाथ लेने वाले हैं। शुरू करने से पहले इसे बंद कर दें।", ar: "فتح هذا يضع رمزك على الشاشة التي توشك اليدان على تصويرها. أغلقه قبل أن تبدأ.",
  },
  "hnd.move": {
    en: "Make a move yourself", es: "Haz un movimiento tú", fr: "Faites un geste vous-même", de: "Mach selbst eine Bewegung", pt: "Faz tu um movimento", it: "Fai tu una mossa", ja: "自分で動かす", zh: "自己动一下", hi: "खुद एक चाल चलें", ar: "حرّك أنت",
  },
  "hnd.move.at": {
    en: "what it is aiming at", es: "a qué apunta", fr: "ce qu'il vise", de: "worauf es zielt", pt: "a que aponta", it: "a cosa mira", ja: "何を狙うか", zh: "瞄准什么", hi: "किस पर निशाना", ar: "ما يستهدفه",
  },
  "hnd.move.go": {
    en: "Move", es: "Mover", fr: "Faire", de: "Bewegen", pt: "Mover", it: "Muovi", ja: "動かす", zh: "执行", hi: "चलें", ar: "نفّذ",
  },
  "hnd.move.key": {
    en: "which key", es: "qué tecla", fr: "quelle touche", de: "welche Taste", pt: "que tecla", it: "quale tasto", ja: "どのキー", zh: "哪个键", hi: "कौन-सी कुंजी", ar: "أي مفتاح",
  },
  "hnd.move.text": {
    en: "what to type", es: "qué escribir", fr: "quoi écrire", de: "was getippt wird", pt: "o que escrever", it: "cosa scrivere", ja: "入力する内容", zh: "要输入什么", hi: "क्या टाइप करना है", ar: "ما يُكتب",
  },
  "hnd.moves": {
    en: "The moves it may make", es: "Los movimientos que puede hacer", fr: "Les gestes qu'il peut faire", de: "Die Bewegungen, die es machen darf", pt: "Os movimentos que pode fazer", it: "Le mosse che può fare", ja: "許される動作", zh: "它可以做的动作", hi: "जो चालें यह चल सकता है", ar: "الحركات المسموح بها",
  },
  "hnd.name": {
    en: "call this something", es: "llámalo de algún modo", fr: "donnez-lui un nom", de: "gib dem einen Namen", pt: "dê-lhe um nome", it: "dagli un nome", ja: "名前をつける", zh: "给它起个名字", hi: "इसे कोई नाम दें", ar: "سمِّ هذا",
  },
  "hnd.never": {
    en: "What it will never do", es: "Lo que nunca hará", fr: "Ce qu'il ne fera jamais", de: "Was es nie tun wird", pt: "O que nunca fará", it: "Cosa non farà mai", ja: "決してしないこと", zh: "它绝不会做的事", hi: "यह क्या कभी नहीं करेगा", ar: "ما لن يفعله أبدًا",
  },
  "hnd.none": {
    en: "Nothing. It has no hands until you give it some.", es: "Nada. No tiene manos hasta que se las des.", fr: "Rien. Il n'a pas de mains tant que vous ne lui en donnez pas.", de: "Nichts. Es hat keine Hände, bis du ihm welche gibst.", pt: "Nada. Não tem mãos até que lhas dê.", it: "Niente. Non ha mani finché non gliene dai.", ja: "何もありません。手を与えるまで、手はありません。", zh: "没有。在你给它之前，它没有手。", hi: "कुछ नहीं। जब तक आप न दें, इसके हाथ नहीं हैं।", ar: "لا شيء. لا يدين له حتى تمنحه إياهما.",
  },
  "hnd.noroutines": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien encore.", de: "Noch nichts.", pt: "Ainda nada.", it: "Ancora niente.", ja: "まだありません。", zh: "还没有。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "hnd.now": {
    en: "What it may do now", es: "Lo que puede hacer ahora", fr: "Ce qu'il peut faire maintenant", de: "Was es jetzt darf", pt: "O que pode fazer agora", it: "Cosa può fare adesso", ja: "いま許されていること", zh: "它现在可以做什么", hi: "अभी यह क्या कर सकता है", ar: "ما يُسمح له الآن",
  },
  "hnd.over": {
    en: "over", es: "terminado", fr: "terminé", de: "abgelaufen", pt: "terminado", it: "scaduto", ja: "終了", zh: "已结束", hi: "समाप्त", ar: "منتهٍ",
  },
  "hnd.pass.go": {
    en: "Hand it over", es: "Pasarlo", fr: "Le confier", de: "Übergeben", pt: "Passar", it: "Passalo", ja: "渡す", zh: "交出去", hi: "सौंपें", ar: "سلّمه",
  },
  "hnd.pass.note": {
    en: "The second profile can only ever hold less — the same apps or fewer, the same moves or fewer, and the steps that are left rather than a fresh budget.", es: "El segundo perfil solo puede tener menos: las mismas aplicaciones o menos, los mismos movimientos o menos, y los pasos que quedan en vez de un presupuesto nuevo.", fr: "Le second profil ne peut jamais détenir que moins : les mêmes applications ou moins, les mêmes gestes ou moins, et les étapes restantes plutôt qu'un nouveau budget.", de: "Das zweite Profil kann immer nur weniger halten — dieselben Apps oder weniger, dieselben Bewegungen oder weniger, und die verbleibenden Schritte statt eines neuen Budgets.", pt: "O segundo perfil só pode ter menos — as mesmas aplicações ou menos, os mesmos movimentos ou menos, e os passos que restam em vez de um orçamento novo.", it: "Il secondo profilo può solo avere meno — le stesse app o meno, le stesse mosse o meno, e i passi rimasti invece di un budget nuovo.", ja: "二つ目のプロフィールが持てるのは、常により少ないものだけです — 同じか少ないアプリ、同じか少ない動作、そして新しい持ち分ではなく残りの手数。", zh: "第二个资料只能拿到更少 — 同样或更少的应用、同样或更少的动作，以及剩下的步数，而不是重新一份额度。", hi: "दूसरा प्रोफ़ाइल हमेशा कम ही रख सकता है — वही या कम ऐप, वही या कम चालें, और बचे हुए चरण, नया बजट नहीं।", ar: "لا يمكن للملف الثاني أن يحمل إلا أقل — التطبيقات ذاتها أو أقل، والحركات ذاتها أو أقل، والخطوات المتبقية لا حصة جديدة.",
  },
  "hnd.pass.who": {
    en: "hand it to which profile", es: "a qué perfil se lo pasas", fr: "à quel profil le confier", de: "an welches Profil übergeben", pt: "a que perfil o passas", it: "a quale profilo passarlo", ja: "どのプロフィールに渡すか", zh: "交给哪个资料", hi: "किस प्रोफ़ाइल को सौंपें", ar: "إلى أي ملف تُسلّمه",
  },
  "hnd.pickgrant": {
    en: "Which permission", es: "Qué permiso", fr: "Quelle permission", de: "Welche Erlaubnis", pt: "Que permissão", it: "Quale permesso", ja: "どの許可", zh: "用哪个许可", hi: "कौन-सी अनुमति", ar: "أي إذن",
  },
  "hnd.pitch": {
    en: "It can already see and speak. This is where it is given permission to work a screen — and taken back in one press.", es: "Ya puede ver y hablar. Aquí se le da permiso para manejar una pantalla — y se le retira con una sola pulsación.", fr: "Il voit et parle déjà. Ici, on lui donne la permission de manœuvrer un écran — et on la reprend d'une seule pression.", de: "Sehen und sprechen kann es schon. Hier bekommt es die Erlaubnis, einen Bildschirm zu bedienen — und mit einem Druck ist sie wieder weg.", pt: "Já consegue ver e falar. Aqui dá-se-lhe permissão para trabalhar um ecrã — e retira-se num só toque.", it: "Vedere e parlare sa già farlo. Qui gli si dà il permesso di usare uno schermo — e lo si ritira con una sola pressione.", ja: "見ることも話すこともすでにできます。ここでは画面を操作する許可を与えます — そして一度の操作で取り戻せます。", zh: "它已经能看、能说。在这里给它操作屏幕的许可 — 也能一按收回。", hi: "यह पहले ही देख और बोल सकता है। यहाँ इसे स्क्रीन चलाने की अनुमति दी जाती है — और एक ही दबाव में वापस ले ली जाती है।", ar: "هو يرى ويتكلم بالفعل. هنا يُمنح إذن تشغيل شاشة — ويُسترد بضغطة واحدة.",
  },
  "hnd.places": {
    en: "Apps or sites", es: "Aplicaciones o sitios", fr: "Applications ou sites", de: "Apps oder Seiten", pt: "Aplicações ou sites", it: "App o siti", ja: "アプリまたはサイト", zh: "应用或网站", hi: "ऐप या साइट", ar: "تطبيقات أو مواقع",
  },
  "hnd.places.hint": {
    en: "calendar, mail — separated by commas", es: "calendario, correo — separados por comas", fr: "agenda, courrier — séparés par des virgules", de: "Kalender, Mail — durch Kommas getrennt", pt: "calendário, correio — separados por vírgulas", it: "calendario, posta — separati da virgole", ja: "カレンダー、メール — カンマ区切り", zh: "日历、邮件 — 用逗号分隔", hi: "कैलेंडर, मेल — अल्पविराम से अलग", ar: "التقويم، البريد — مفصولة بفواصل",
  },
  "hnd.put": {
    en: "Put its hands on something", es: "Poner sus manos en algo", fr: "Poser ses mains sur quelque chose", de: "Ihm etwas in die Hände geben", pt: "Pôr as mãos em algo", it: "Mettergli le mani su qualcosa", ja: "何かに手をかける", zh: "让它上手做事", hi: "इसे किसी काम पर लगाएँ", ar: "ضع يديه على شيء",
  },
  "hnd.put.go": {
    en: "Begin", es: "Comenzar", fr: "Commencer", de: "Beginnen", pt: "Começar", it: "Inizia", ja: "開始", zh: "开始", hi: "शुरू करें", ar: "ابدأ",
  },
  "hnd.reach.line": {
    en: "{state} · {left} steps left · {where}", es: "{state} · quedan {left} pasos · {where}", fr: "{state} · {left} étapes restantes · {where}", de: "{state} · noch {left} Schritte · {where}", pt: "{state} · restam {left} passos · {where}", it: "{state} · {left} passi rimasti · {where}", ja: "{state} · 残り{left}手 · {where}", zh: "{state} · 剩余 {left} 步 · {where}", hi: "{state} · {left} चरण शेष · {where}", ar: "{state} · بقيت {left} خطوة · {where}",
  },
  "hnd.refresh": {
    en: "Refresh", es: "Actualizar", fr: "Actualiser", de: "Aktualisieren", pt: "Atualizar", it: "Aggiorna", ja: "更新", zh: "刷新", hi: "ताज़ा करें", ar: "تحديث",
  },
  "hnd.steps": {
    en: "Steps", es: "Pasos", fr: "Étapes", de: "Schritte", pt: "Passos", it: "Passi", ja: "手数", zh: "步数", hi: "चरण", ar: "خطوات",
  },
  "hnd.stepsword": {
    en: "steps", es: "pasos", fr: "étapes", de: "Schritte", pt: "passos", it: "passi", ja: "手", zh: "步", hi: "चरण", ar: "خطوات",
  },
  "hnd.stop": {
    en: "Take the screen back", es: "Recuperar la pantalla", fr: "Reprendre l'écran", de: "Bildschirm zurücknehmen", pt: "Recuperar o ecrã", it: "Riprendi lo schermo", ja: "画面を取り戻す", zh: "收回屏幕", hi: "स्क्रीन वापस लें", ar: "استرجع الشاشة",
  },
  "hnd.surface": {
    en: "Where", es: "Dónde", fr: "Où", de: "Wo", pt: "Onde", it: "Dove", ja: "場所", zh: "何处", hi: "कहाँ", ar: "أين",
  },
  "hnd.takeback": {
    en: "Take back", es: "Retirar", fr: "Reprendre", de: "Zurücknehmen", pt: "Retirar", it: "Ritira", ja: "取り消す", zh: "收回", hi: "वापस लें", ar: "استرداد",
  },
  "hnd.title": {
    en: "Hands", es: "Manos", fr: "Mains", de: "Hände", pt: "Mãos", it: "Mani", ja: "手", zh: "双手", hi: "हाथ", ar: "اليدان",
  },
  "hnd.told": {
    en: "Or just say it", es: "O simplemente dilo", fr: "Ou dites-le simplement", de: "Oder sag es einfach", pt: "Ou basta dizê-lo", it: "Oppure dillo e basta", ja: "または、言うだけ", zh: "或者直接说出来", hi: "या बस कह दीजिए", ar: "أو قُلها فحسب",
  },
  "hnd.told.go": {
    en: "Say it", es: "Dilo", fr: "Dites-le", de: "Sag es", pt: "Diga-o", it: "Dillo", ja: "言う", zh: "说出来", hi: "कहो", ar: "قلها",
  },
  "hnd.told.hint": {
    en: "you can click and type in my calendar for the next hour", es: "puedes hacer clic y escribir en mi calendario durante la próxima hora", fr: "tu peux cliquer et écrire dans mon agenda pendant la prochaine heure", de: "du darfst in der nächsten Stunde in meinem Kalender klicken und tippen", pt: "podes clicar e escrever no meu calendário durante a próxima hora", it: "puoi cliccare e scrivere nel mio calendario per la prossima ora", ja: "これから一時間、私のカレンダーでクリックと入力をしていい", zh: "接下来一小时你可以在我的日历里点击和输入", hi: "अगले एक घंटे तक तुम मेरे कैलेंडर में क्लिक और टाइप कर सकते हो", ar: "يمكنك النقر والكتابة في تقويمي خلال الساعة القادمة",
  },
  "hnd.told.pitch": {
    en: "The same permission, said instead of picked. Words that name no app or site grant nothing — the refusal quotes back what was heard so you can say it better.", es: "El mismo permiso, dicho en vez de elegido. Palabras que no nombran ninguna aplicación o sitio no conceden nada — el rechazo repite lo que se oyó para que puedas decirlo mejor.", fr: "La même permission, dite au lieu d'être choisie. Des mots qui ne nomment aucune application ni aucun site n'accordent rien — le refus cite ce qui a été entendu pour que vous puissiez mieux le dire.", de: "Dieselbe Erlaubnis, gesagt statt ausgewählt. Worte, die keine App und keine Seite nennen, gewähren nichts — die Ablehnung zitiert das Gehörte zurück, damit du es besser sagen kannst.", pt: "A mesma permissão, dita em vez de escolhida. Palavras que não nomeiam nenhuma aplicação ou site não concedem nada — a recusa cita o que foi ouvido para que possa dizê-lo melhor.", it: "Lo stesso permesso, detto invece che scelto. Parole che non nominano alcuna app o sito non concedono nulla — il rifiuto ripete ciò che ha sentito perché tu possa dirlo meglio.", ja: "同じ許可を、選ぶ代わりに言葉で。アプリやサイトを挙げない言葉は何も許可しません — 拒否は聞き取った内容をそのまま返すので、言い直せます。", zh: "同一个许可，用说的而不是选的。没有点名应用或网站的话什么也不授予 — 拒绝会把听到的原话回给你，好让你说得更清楚。", hi: "वही अनुमति, चुनने के बजाय कही गई। जो शब्द किसी ऐप या साइट का नाम नहीं लेते वे कुछ नहीं देते — इनकार सुनी हुई बात दोहरा देता है ताकि आप बेहतर कह सकें।", ar: "الإذن نفسه، مقولًا بدل أن يكون مختارًا. الكلمات التي لا تسمّي تطبيقًا أو موقعًا لا تمنح شيئًا — والرفض يقتبس ما سُمع كي تقولها على نحو أوضح.",
  },
  "hnd.tookback": {
    en: "Taken back. Anything running stops at its next step.", es: "Retirado. Lo que esté en marcha se detiene en su próximo paso.", fr: "Repris. Ce qui est en cours s'arrête à l'étape suivante.", de: "Zurückgenommen. Was läuft, hält beim nächsten Schritt an.", pt: "Retirado. O que estiver a decorrer para no passo seguinte.", it: "Ritirato. Ciò che è in corso si ferma al passo successivo.", ja: "取り消しました。実行中のものは次の一手で止まります。", zh: "已收回。正在进行的会在下一步停下。", hi: "वापस ले लिया। जो चल रहा है वह अगले चरण पर रुक जाएगा।", ar: "تم الاسترداد. ما يجري يتوقف عند خطوته التالية.",
  },
  "hnd.undrivable": {
    en: "Nothing can operate another app's interface on an iPhone — Apple provides no way, so there is no permission to ask for. It can still watch this screen and tell you where to press.", es: "Nada puede manejar la interfaz de otra aplicación en un iPhone — Apple no ofrece ninguna vía, así que no hay permiso que pedir. Aún puede mirar esta pantalla y decirte dónde pulsar.", fr: "Rien ne peut manœuvrer l'interface d'une autre application sur un iPhone — Apple n'offre aucun moyen, il n'y a donc aucune permission à demander. Il peut toujours regarder cet écran et vous dire où appuyer.", de: "Auf einem iPhone kann nichts die Oberfläche einer anderen App bedienen — Apple bietet keinen Weg, also gibt es keine Erlaubnis zu erfragen. Zusehen und dir sagen, wo du drücken sollst, kann es weiterhin.", pt: "Nada consegue operar a interface de outra aplicação num iPhone — a Apple não oferece qualquer via, por isso não há permissão a pedir. Ainda pode observar este ecrã e dizer-lhe onde carregar.", it: "Su un iPhone nulla può usare l'interfaccia di un'altra app — Apple non offre alcuna via, quindi non c'è alcun permesso da chiedere. Può comunque guardare questo schermo e dirti dove premere.", ja: "iPhone では、他アプリの画面を操作できるものはありません — Apple がその手段を用意していないため、求めるべき許可自体が存在しません。画面を見て、どこを押せばよいか伝えることはできます。", zh: "在 iPhone 上，任何程序都无法操作另一个应用的界面 — 苹果没有提供途径，因此根本没有可申请的权限。它仍然可以看这块屏幕并告诉你按哪里。", hi: "iPhone पर कोई भी दूसरे ऐप का इंटरफ़ेस नहीं चला सकता — Apple कोई रास्ता नहीं देता, इसलिए माँगने को कोई अनुमति ही नहीं है। यह फिर भी यह स्क्रीन देख सकता है और बता सकता है कि कहाँ दबाना है।", ar: "لا شيء يستطيع تشغيل واجهة تطبيق آخر على الآيفون — لا توفّر آبل أي سبيل لذلك، فلا وجود لإذن يُطلب. ويظل بوسعه مشاهدة هذه الشاشة وإخبارك أين تضغط.",
  },
  "hnd.watched": {
    en: "only while somebody is watching", es: "solo mientras alguien mira", fr: "seulement pendant que quelqu'un regarde", de: "nur solange jemand zusieht", pt: "apenas enquanto alguém observa", it: "solo mentre qualcuno guarda", ja: "誰かが見ている間だけ", zh: "仅在有人看着时", hi: "केवल जब कोई देख रहा हो", ar: "فقط بينما يراقب أحد",
  },
  "hnd.write": {
    en: "Write it down", es: "Anotarlo", fr: "Le noter", de: "Aufschreiben", pt: "Anotar", it: "Annotalo", ja: "書き留める", zh: "记下来", hi: "लिख लें", ar: "دوّنه",
  },
  "hnd.wrotedown": {
    en: "Written down. It can do that again.", es: "Anotado. Puede hacerlo de nuevo.", fr: "Noté. Il peut le refaire.", de: "Aufgeschrieben. Es kann das wieder tun.", pt: "Anotado. Pode fazê-lo outra vez.", it: "Annotato. Può rifarlo.", ja: "書き留めました。同じことをまたできます。", zh: "已记下。它可以再做一次。", hi: "लिख लिया गया। यह इसे फिर कर सकता है।", ar: "دُوّن. يستطيع فعل ذلك مجددًا.",
  },
  "nav.hands": {
    en: "Hands", es: "Manos", fr: "Mains", de: "Hände", pt: "Mãos", it: "Mani", ja: "手", zh: "双手", hi: "हाथ", ar: "اليدان",
  },
  "nav.reach": {
    en: "What reaches out",
    es: "Qué se pone en contacto",
    fr: "Ce qui prend contact",
    de: "Was sich meldet",
    pt: "O que entra em contacto",
    it: "Cosa si fa vivo",
    ja: "働きかけるもの",
    zh: "主动联系的功能",
    hi: "क्या संपर्क करता है",
    ar: "ما الذي يتواصل",
  },
  "nav.bearing": {
    en: "Bearing",
    es: "Rumbo",
    fr: "Cap",
    de: "Kurs",
    pt: "Rumo",
    it: "Rotta",
    ja: "方位",
    zh: "方向",
    hi: "दिशा",
    ar: "الاتجاه",
  },
  "nav.community": {
    en: "Community",
    es: "Comunidad",
    fr: "Communauté",
    de: "Gemeinschaft",
    pt: "Comunidade",
    it: "Comunità",
    ja: "コミュニティ",
    zh: "社区",
    hi: "समुदाय",
    ar: "المجتمع",
  },
  "nav.channel": {
    en: "Channel & camera",
    es: "Canal y cámara",
    fr: "Canal et caméra",
    de: "Kanal & Kamera",
    pt: "Canal e câmara",
    it: "Canale e fotocamera",
    ja: "チャンネルとカメラ",
    zh: "频道与摄像头",
    hi: "चैनल और कैमरा",
    ar: "القناة والكاميرا",
  },
  // The menu label matches the screen's own title (`permits.title`) so the
  // door and the room say the same thing. "What you have let it change"
  // came back from the field as not quite fitting the tile — the words a
  // reporter reached for describing the same screen were "the list of what
  // I can touch", and the door now says that.
  "nav.permits": {
    en: "What JIM can touch",
    es: "Lo que JIM puede tocar",
    fr: "Ce que JIM peut toucher",
    de: "Was JIM anfassen darf",
    pt: "O que o JIM pode tocar",
    it: "Cosa può toccare JIM",
    ja: "JIMが触れられること",
    zh: "JIM 能触及的部分",
    hi: "JIM क्या छू सकता है",
    ar: "ما يمكن لـJIM لمسه",
  },
  "nav.held": {
    en: "What's held about you",
    es: "Qué se guarda sobre ti",
    fr: "Ce qui est conservé sur vous",
    de: "Was über dich gespeichert ist",
    pt: "O que é guardado sobre si",
    it: "Cosa viene conservato su di te",
    ja: "あなたについて保持されているもの",
    zh: "关于你所保存的内容",
    hi: "आपके बारे में क्या रखा गया है",
    ar: "ما المحفوظ عنك",
  },
  "nav.settings": {
    en: "Privacy",
    es: "Privacidad",
    fr: "Confidentialité",
    de: "Privatsphäre",
    pt: "Privacidade",
    it: "Privacy",
    ja: "プライバシー",
    zh: "隐私",
    hi: "गोपनीयता",
    ar: "الخصوصية",
  },
  "onb.pitch": {
    en: "Monitor, predict, guide, escalate — grounded in your baseline, on your device.",
    es: "Vigila, predice, guía y escala — anclado en tu línea base, en tu dispositivo.",
    fr: "Surveiller, prédire, guider, alerter — ancré sur votre référence, sur votre appareil.",
    de: "Beobachten, vorhersagen, führen, eskalieren — verankert in deiner Baseline, auf deinem Gerät.",
    pt: "Monitorizar, prever, orientar, escalar — ancorado na sua linha de base, no seu dispositivo.",
    it: "Monitora, prevede, guida, allerta — ancorato alla tua baseline, sul tuo dispositivo.",
    ja: "見守り、予測し、導き、必要なら知らせる — あなたのベースラインに基づき、あなたの端末で。",
    zh: "监测、预测、引导、升级——基于你的基线，在你的设备上。",
    hi: "निगरानी, पूर्वानुमान, मार्गदर्शन, एस्केलेशन — आपकी बेसलाइन पर आधारित, आपके डिवाइस पर।",
    ar: "يراقب ويتوقّع ويوجّه ويُنبّه — مستندًا إلى خط أساسك، على جهازك.",
  },
  "onb.anon": {
    en: "Keep me anonymous — use a pseudonym instead of my name",
    es: "Mantenerme anónimo — usar un seudónimo en lugar de mi nombre",
    fr: "Garder l'anonymat — utiliser un pseudonyme à la place de mon nom",
    de: "Anonym bleiben — ein Pseudonym statt meines Namens verwenden",
    pt: "Manter-me anónimo — usar um pseudónimo em vez do meu nome",
    it: "Mantienimi anonimo — usa uno pseudonimo al posto del mio nome",
    ja: "匿名にする — 名前の代わりに仮名を使う",
    zh: "保持匿名——使用化名代替我的姓名",
    hi: "मुझे गुमनाम रखें — मेरे नाम के बजाय छद्म नाम का उपयोग करें",
    ar: "أبقني مجهولًا — استخدم اسمًا مستعارًا بدل اسمي",
  },
  "onb.legalname.why": {
    en: "JIM won't keep the name above. Every emergency path works exactly the same; the one difference is that a dispatcher briefing can't give responders a legal name. Leave one below only if you want it used for that.",
    es: "JIM no conservará el nombre de arriba. Todas las vías de emergencia funcionan igual; la única diferencia es que un aviso al despachador no podrá dar a los servicios un nombre legal. Escribe uno abajo solo si quieres que se use para eso.",
    fr: "JIM ne conservera pas le nom ci-dessus. Toutes les procédures d'urgence fonctionnent à l'identique ; la seule différence est qu'un signalement au régulateur ne pourra pas donner de nom légal aux secours. N'en indiquez un ci-dessous que si vous voulez qu'il serve à cela.",
    de: "JIM behält den Namen oben nicht. Alle Notfallwege funktionieren genau gleich; der einzige Unterschied ist, dass eine Leitstellenmeldung den Einsatzkräften keinen amtlichen Namen nennen kann. Trage unten nur einen ein, wenn er dafür verwendet werden soll.",
    pt: "O JIM não guardará o nome acima. Todos os percursos de emergência funcionam igual; a única diferença é que um aviso à central não poderá dar às equipas um nome legal. Indique um abaixo apenas se quiser que seja usado para isso.",
    it: "JIM non conserverà il nome qui sopra. Tutti i percorsi di emergenza funzionano allo stesso modo; l'unica differenza è che una segnalazione alla centrale non potrà fornire ai soccorritori un nome legale. Inseriscine uno sotto solo se vuoi che venga usato a quello scopo.",
    ja: "JIMは上の名前を保持しません。緊急時の経路はすべて同じように機能します。唯一の違いは、指令員への連絡で救助者に法的な氏名を伝えられない点です。その用途に使ってよい場合のみ、下に記入してください。",
    zh: "JIM 不会保留上面的名字。所有紧急流程完全一样；唯一的区别是调度通报无法向救援人员提供法定姓名。只有当你希望用于此用途时，才在下方填写。",
    hi: "JIM ऊपर दिया गया नाम नहीं रखेगा। सभी आपातकालीन रास्ते बिल्कुल एक जैसे काम करते हैं; फ़र्क़ सिर्फ़ इतना है कि डिस्पैचर ब्रीफ़िंग बचावकर्मियों को कानूनी नाम नहीं दे सकेगी। नीचे नाम तभी लिखें जब आप उसे इसी काम के लिए इस्तेमाल करवाना चाहें।",
    ar: "لن يحتفظ JIM بالاسم أعلاه. تعمل جميع مسارات الطوارئ بالطريقة نفسها؛ الفارق الوحيد أن إبلاغ المرسل لن يتمكن من إعطاء المستجيبين اسمًا قانونيًا. اكتب اسمًا أدناه فقط إن أردت استخدامه لذلك.",
  },
  "onb.noemail.why": {
    en: "No email address? You can start without one. There is no way to recover an account made this way — this device holds the only key to it — but you do not have to have an address to be looked after.",
    es: "¿Sin correo electrónico? Puedes empezar sin uno. No hay forma de recuperar una cuenta creada así — este dispositivo guarda la única llave — pero no hace falta tener una dirección para que cuiden de ti.",
    fr: "Pas d'adresse e-mail ? Vous pouvez commencer sans. Un compte créé ainsi est irrécupérable — cet appareil en détient la seule clé — mais vous n'avez pas besoin d'une adresse pour être pris en charge.",
    de: "Keine E-Mail-Adresse? Du kannst ohne beginnen. Ein so erstelltes Konto lässt sich nicht wiederherstellen — dieses Gerät hält den einzigen Schlüssel — aber du brauchst keine Adresse, um betreut zu werden.",
    pt: "Sem endereço de e-mail? Pode começar sem um. Não há forma de recuperar uma conta criada assim — este dispositivo guarda a única chave — mas não precisa de um endereço para ser acompanhado.",
    it: "Nessun indirizzo email? Puoi iniziare senza. Un account creato così non è recuperabile — questo dispositivo ne custodisce l'unica chiave — ma non serve un indirizzo per essere seguito.",
    ja: "メールアドレスがなくても始められます。この方法で作成したアカウントは復旧できません（この端末が唯一の鍵を保持します）が、見守られるためにアドレスは必須ではありません。",
    zh: "没有电子邮箱？你也可以开始。以这种方式创建的账户无法找回——本设备持有唯一的密钥——但被照护并不需要一个邮箱地址。",
    hi: "ईमेल पता नहीं है? आप बिना उसके शुरू कर सकते हैं। इस तरह बने खाते को वापस पाने का कोई तरीका नहीं है — इस डिवाइस के पास ही उसकी एकमात्र कुंजी है — पर देखभाल पाने के लिए पता होना ज़रूरी नहीं।",
    ar: "لا تملك بريدًا إلكترونيًا؟ يمكنك البدء بدونه. لا سبيل لاستعادة حساب أُنشئ بهذه الطريقة — فهذا الجهاز يحمل مفتاحه الوحيد — لكنك لست بحاجة إلى عنوان كي يُعتنى بك.",
  },
  "onb.localservice": {
    en: "This window is only the console — the Guardian runs as a local service. Start it with",
    es: "Esta ventana es solo la consola: el Guardián se ejecuta como servicio local. Inícialo con",
    fr: "Cette fenêtre n'est que la console — le Gardien tourne comme service local. Démarrez-le avec",
    de: "Dieses Fenster ist nur die Konsole — der Guardian läuft als lokaler Dienst. Starte ihn mit",
    pt: "Esta janela é apenas a consola — o Guardião corre como serviço local. Inicie-o com",
    it: "Questa finestra è solo la console: il Guardian gira come servizio locale. Avvialo con",
    ja: "このウィンドウはコンソールにすぎません。ガーディアンはローカルサービスとして動作します。次のコマンドで起動してください：",
    zh: "此窗口只是控制台——守护者作为本地服务运行。用以下命令启动它",
    hi: "यह विंडो केवल कंसोल है — गार्जियन एक स्थानीय सेवा के रूप में चलता है। इसे इससे शुरू करें",
    ar: "هذه النافذة ليست سوى وحدة التحكم — يعمل الحارس كخدمة محلية. شغّله بـ",
  },
  "onb.orpoint": {
    en: ", or point this console at a machine already running one:",
    es: ", o apunta esta consola a una máquina que ya lo esté ejecutando:",
    fr: ", ou pointez cette console vers une machine qui en exécute déjà un :",
    de: ", oder richte diese Konsole auf einen Rechner, auf dem er bereits läuft:",
    pt: ", ou aponte esta consola para uma máquina que já o esteja a executar:",
    it: ", oppure punta questa console a una macchina che ne esegue già uno:",
    ja: "、または既に稼働しているマシンをこのコンソールに指定してください：",
    zh: "，或将此控制台指向已在运行它的机器：",
    hi: ", या इस कंसोल को उस मशीन पर इंगित करें जहाँ यह पहले से चल रहा है:",
    ar: "، أو وجّه وحدة التحكم هذه إلى جهاز يشغّله بالفعل:",
  },
  "onb.unreachable": {
    en: "⚠ The Guardian backend isn't reachable at",
    es: "⚠ No se puede acceder al backend del Guardián en",
    fr: "⚠ Le backend du Gardien est injoignable à",
    de: "⚠ Das Guardian-Backend ist nicht erreichbar unter",
    pt: "⚠ O backend do Guardião não está acessível em",
    it: "⚠ Il backend del Guardian non è raggiungibile su",
    ja: "⚠ ガーディアンのバックエンドに接続できません：",
    zh: "⚠ 无法连接到守护者后端：",
    hi: "⚠ गार्जियन बैकएंड यहाँ पहुँच योग्य नहीं है",
    ar: "⚠ تعذّر الوصول إلى خلفية الحارس على",
  },
  "onb.retry": {
    en: "Save & retry",
    es: "Guardar y reintentar",
    fr: "Enregistrer et réessayer",
    de: "Speichern und erneut versuchen",
    pt: "Guardar e tentar de novo",
    it: "Salva e riprova",
    ja: "保存して再試行",
    zh: "保存并重试",
    hi: "सहेजें और पुनः प्रयास करें",
    ar: "حفظ وإعادة المحاولة",
  },
  "onb.openlog": {
    en: "Open the log with the code",
    es: "Abrir el registro con el código",
    fr: "Ouvrir le journal contenant le code",
    de: "Log mit dem Code öffnen",
    pt: "Abrir o registo com o código",
    it: "Apri il log con il codice",
    ja: "コードが記録されたログを開く",
    zh: "打开含有验证码的日志",
    hi: "कोड वाला लॉग खोलें",
    ar: "افتح السجل الذي يحوي الرمز",
  },
  "onb.verify.sent": {
    en: "We emailed a verification link to",
    es: "Enviamos un enlace de verificación a",
    fr: "Nous avons envoyé un lien de vérification à",
    de: "Wir haben einen Bestätigungslink gesendet an",
    pt: "Enviámos um link de verificação para",
    it: "Abbiamo inviato un link di verifica a",
    ja: "確認リンクを次の宛先に送信しました：",
    zh: "我们已将验证链接发送至",
    hi: "हमने सत्यापन लिंक भेजा है",
    ar: "أرسلنا رابط تحقق إلى",
  },
  "onb.verify.click": {
    en: "Click the link and this screen continues on its own.",
    es: "Haz clic en el enlace y esta pantalla continuará sola.",
    fr: "Cliquez sur le lien et cet écran continuera tout seul.",
    de: "Klicke auf den Link, und dieser Bildschirm macht von allein weiter.",
    pt: "Clique no link e este ecrã continua sozinho.",
    it: "Fai clic sul link e questa schermata proseguirà da sola.",
    ja: "リンクをクリックすると、この画面は自動的に進みます。",
    zh: "点击链接后，此页面会自动继续。",
    hi: "लिंक पर क्लिक करें और यह स्क्रीन अपने आप आगे बढ़ जाएगी।",
    ar: "انقر الرابط وستتابع هذه الشاشة من تلقاء نفسها.",
  },
  "onb.verify.type": {
    en: "Prefer typing? Enter the 6-digit code from the same email instead. Your account exists only after one or the other.",
    es: "¿Prefieres escribir? Introduce el código de 6 dígitos del mismo correo. Tu cuenta existe solo después de una u otra cosa.",
    fr: "Vous préférez taper ? Saisissez le code à 6 chiffres du même e-mail. Votre compte n'existe qu'après l'une ou l'autre.",
    de: "Lieber tippen? Gib den sechsstelligen Code aus derselben E-Mail ein. Dein Konto existiert erst nach einem von beidem.",
    pt: "Prefere escrever? Introduza o código de 6 dígitos do mesmo e-mail. A sua conta só existe depois de uma das duas.",
    it: "Preferisci digitare? Inserisci il codice a 6 cifre della stessa email. Il tuo account esiste solo dopo una delle due.",
    ja: "入力の方がよろしいですか？同じメールの6桁のコードを入力してください。どちらか一方の完了後にアカウントが作成されます。",
    zh: "更想手动输入？请使用同一封邮件里的 6 位验证码。二者完成其一后，账户才会存在。",
    hi: "टाइप करना पसंद करेंगे? उसी ईमेल का 6 अंकों का कोड दर्ज करें। इनमें से एक के बाद ही आपका खाता बनेगा।",
    ar: "تفضّل الكتابة؟ أدخل الرمز المكوّن من ٦ أرقام من الرسالة نفسها. لا يوجد حسابك إلا بعد إحدى الطريقتين.",
  },
  "onb.reset.hint": {
    en: "Enter your account's email; we'll send a 6-digit reset code",
    es: "Introduce el correo de tu cuenta; enviaremos un código de 6 dígitos",
    fr: "Saisissez l'e-mail de votre compte ; nous enverrons un code à 6 chiffres",
    de: "Gib die E-Mail deines Kontos ein; wir senden einen sechsstelligen Code",
    pt: "Introduza o e-mail da sua conta; enviaremos um código de 6 dígitos",
    it: "Inserisci l'email del tuo account; invieremo un codice a 6 cifre",
    ja: "アカウントのメールアドレスを入力してください。6桁のリセットコードを送信します",
    zh: "请输入账户邮箱，我们会发送 6 位重置码",
    hi: "अपने खाते का ईमेल दर्ज करें; हम 6 अंकों का रीसेट कोड भेजेंगे",
    ar: "أدخل بريد حسابك؛ سنرسل رمز إعادة تعيين من ٦ أرقام",
  },
  "onb.nomail": {
    en: "— this deployment has no mail service configured, so the code was",
    es: "— este despliegue no tiene servicio de correo configurado, así que el código se",
    fr: "— ce déploiement n'a pas de service de messagerie configuré, le code a donc été",
    de: "— diese Installation hat keinen Mailversand konfiguriert, der Code wurde daher",
    pt: "— esta implementação não tem serviço de e-mail configurado, por isso o código foi",
    it: "— questa installazione non ha un servizio di posta configurato, quindi il codice è stato",
    ja: "— この環境ではメール送信が設定されていないため、コードは",
    zh: "——此部署未配置邮件服务，因此验证码已",
    hi: "— इस परिनियोजन में मेल सेवा कॉन्फ़िगर नहीं है, इसलिए कोड",
    ar: "— لم يُضبط في هذا النشر خدمة بريد، لذا فإن الرمز",
  },
  "onb.nomail.log": {
    en: "written to the app's backend log",
    es: "escribió en el registro del backend de la app",
    fr: "écrit dans le journal du backend de l'application",
    de: "ins Backend-Log der App geschrieben",
    pt: "escrito no registo do backend da aplicação",
    it: "scritto nel log del backend dell'app",
    ja: "アプリのバックエンドログに記録されました",
    zh: "写入了应用后端日志",
    hi: "ऐप के बैकएंड लॉग में लिखा गया",
    ar: "كُتب في سجل الخلفية للتطبيق",
  },
  "onb.nomail.terminal": {
    en: "printed in the terminal running the backend",
    es: "imprimió en la terminal que ejecuta el backend",
    fr: "affiché dans le terminal exécutant le backend",
    de: "im Terminal ausgegeben, das das Backend ausführt",
    pt: "impresso no terminal que executa o backend",
    it: "stampato nel terminale che esegue il backend",
    ja: "バックエンドを実行しているターミナルに出力されました",
    zh: "打印在运行后端的终端中",
    hi: "बैकएंड चला रहे टर्मिनल में प्रिंट किया गया",
    ar: "طُبع في الطرفية التي تشغّل الخلفية",
  },
  "onb.nomail.open": {
    en: "(button below opens it)",
    es: "(el botón de abajo lo abre)",
    fr: "(le bouton ci-dessous l'ouvre)",
    de: "(die Schaltfläche unten öffnet es)",
    pt: "(o botão abaixo abre-o)",
    it: "(il pulsante sotto lo apre)",
    ja: "（下のボタンで開けます）",
    zh: "（下方按钮可打开）",
    hi: "(नीचे का बटन इसे खोलता है)",
    ar: "(الزر أدناه يفتحه)",
  },
  "onb.oauth.absent": {
    en: "· not configured here",
    es: "· no configurado aquí",
    fr: "· non configuré ici",
    de: "· hier nicht konfiguriert",
    pt: "· não configurado aqui",
    it: "· non configurato qui",
    ja: "・この環境では未設定",
    zh: "· 此处未配置",
    hi: "· यहाँ कॉन्फ़िगर नहीं",
    ar: "· غير مُهيَّأ هنا",
  },
  "onb.tagline": {
    en: "Your Guardian, always here",
    es: "Tu Guardián, siempre presente",
    fr: "Votre Gardien, toujours là",
    de: "Dein Guardian, immer da",
    pt: "O seu Guardião, sempre presente",
    it: "Il tuo Guardian, sempre qui",
    ja: "あなたのガーディアンは、いつもここに",
    zh: "你的守护者，始终在这里",
    hi: "आपका गार्जियन, हमेशा साथ",
    ar: "حارسك، حاضر دائمًا",
  },
  "onb.invite": {
    en: "Invite key",
    es: "Clave de invitación",
    fr: "Clé d’invitation",
    de: "Einladungsschlüssel",
    pt: "Chave de convite",
    it: "Chiave di invito",
    ja: "招待キー",
    zh: "邀请密钥",
    hi: "आमंत्रण कुंजी",
    ar: "مفتاح الدعوة",
  },
  "onb.invite.hint": {
    en: "This deployment requires an invite key to create an account — the person who runs it can give you one.",
    es: "Esta instalación requiere una clave de invitación para crear una cuenta; quien la administra puede dártela.",
    fr: "Cette installation exige une clé d’invitation pour créer un compte — la personne qui la gère peut vous en fournir une.",
    de: "Diese Installation verlangt zum Erstellen eines Kontos einen Einladungsschlüssel — die betreibende Person kann ihn dir geben.",
    pt: "Esta instalação exige uma chave de convite para criar uma conta — quem a administra pode fornecê-la.",
    it: "Questa installazione richiede una chiave di invito per creare un account: chi la gestisce può fornirtela.",
    ja: "この環境でアカウントを作成するには招待キーが必要です。運営者から受け取ってください。",
    zh: "此部署需要邀请密钥才能创建账户——请向运营者索取。",
    hi: "इस परिनियोजन में खाता बनाने के लिए आमंत्रण कुंजी आवश्यक है — इसे चलाने वाला व्यक्ति आपको दे सकता है।",
    ar: "يتطلب هذا النشر مفتاح دعوة لإنشاء حساب — يمكن لمن يديره أن يعطيك إياه.",
  },
  // --- the accessibility statement and its door --------------------------
  // Every sentence below states only what the console actually does today.
  // If a claim stops being true, fix the behavior, not the sentence.
  "nav.access": {
    en: "Accessibility", es: "Accesibilidad", fr: "Accessibilité",
    de: "Barrierefreiheit", pt: "Acessibilidade", it: "Accessibilità",
    ja: "アクセシビリティ", zh: "无障碍", hi: "सुलभता", ar: "إمكانية الوصول",
  },
  "acc.title": {
    en: "Ability is not a gate",
    es: "La capacidad no es una puerta",
    fr: "La capacité n’est pas une barrière",
    de: "Fähigkeit ist kein Tor",
    pt: "Capacidade não é um portão",
    it: "L’abilità non è un cancello",
    ja: "能力は門ではありません",
    zh: "能力不是门槛",
    hi: "क्षमता कोई द्वार नहीं है",
    ar: "القدرة ليست بوابة",
  },
  "acc.lead": {
    en: "If how your body or mind works stands between you and this product, that is a defect in the product — not in you. We work on these defects need by need, in the open, and everything on this page works without an account.",
    es: "Si el modo en que funciona tu cuerpo o tu mente se interpone entre tú y este producto, eso es un defecto del producto, no tuyo. Trabajamos en estos defectos necesidad por necesidad, abiertamente, y todo en esta página funciona sin cuenta.",
    fr: "Si le fonctionnement de votre corps ou de votre esprit s’interpose entre vous et ce produit, c’est un défaut du produit — pas le vôtre. Nous traitons ces défauts besoin par besoin, ouvertement, et tout sur cette page fonctionne sans compte.",
    de: "Wenn die Art, wie dein Körper oder dein Geist arbeitet, zwischen dir und diesem Produkt steht, ist das ein Fehler des Produkts — nicht deiner. Wir arbeiten an diesen Fehlern Bedürfnis für Bedürfnis, offen, und alles auf dieser Seite funktioniert ohne Konto.",
    pt: "Se o modo como seu corpo ou sua mente funciona fica entre você e este produto, isso é um defeito do produto — não seu. Trabalhamos nesses defeitos necessidade por necessidade, abertamente, e tudo nesta página funciona sem conta.",
    it: "Se il modo in cui funziona il tuo corpo o la tua mente si frappone tra te e questo prodotto, è un difetto del prodotto — non tuo. Lavoriamo su questi difetti bisogno per bisogno, apertamente, e tutto in questa pagina funziona senza account.",
    ja: "あなたの体や心の働き方がこの製品との間に立ちはだかるなら、それは製品の欠陥であって、あなたの欠陥ではありません。私たちはその欠陥にひとつずつ公開で取り組んでいます。このページのすべてはアカウントなしで使えます。",
    zh: "如果你的身体或思维方式挡在你与这个产品之间，那是产品的缺陷——不是你的。我们逐项公开地修复这些缺陷，本页的一切无需账户即可使用。",
    hi: "अगर आपके शरीर या मन के काम करने का तरीका आपके और इस उत्पाद के बीच आता है, तो वह उत्पाद का दोष है — आपका नहीं। हम इन दोषों पर ज़रूरत-दर-ज़रूरत, खुले तौर पर काम करते हैं, और इस पृष्ठ की हर चीज़ बिना खाते के काम करती है।",
    ar: "إذا كانت طريقة عمل جسدك أو عقلك تقف بينك وبين هذا المنتج، فذلك عيب في المنتج — لا فيك. نعالج هذه العيوب حاجةً حاجةً وبشكل علني، وكل ما في هذه الصفحة يعمل دون حساب.",
  },
  "acc.needs.title": {
    en: "Who is expected here",
    es: "A quién esperamos aquí",
    fr: "Qui est attendu ici",
    de: "Wer hier erwartet wird",
    pt: "Quem é esperado aqui",
    it: "Chi è atteso qui",
    ja: "ここに来ることが想定されている人",
    zh: "这里期待谁的到来",
    hi: "यहाँ किनकी अपेक्षा है",
    ar: "من ننتظر هنا",
  },
  "acc.needs.blind": {
    en: "Blind and low-vision: every function works by text, images carry descriptions, and the screens use standard controls a screen reader can walk.",
    es: "Personas ciegas o con baja visión: cada función opera por texto, las imágenes llevan descripciones y las pantallas usan controles estándar que un lector de pantalla puede recorrer.",
    fr: "Personnes aveugles ou malvoyantes : chaque fonction passe par le texte, les images portent des descriptions et les écrans utilisent des contrôles standard qu’un lecteur d’écran peut parcourir.",
    de: "Blinde und sehbehinderte Menschen: jede Funktion geht über Text, Bilder tragen Beschreibungen, und die Oberfläche nutzt Standard-Elemente, die ein Screenreader ablaufen kann.",
    pt: "Pessoas cegas ou com baixa visão: toda função opera por texto, as imagens têm descrições e as telas usam controles padrão que um leitor de tela consegue percorrer.",
    it: "Persone cieche o ipovedenti: ogni funzione passa dal testo, le immagini hanno descrizioni e le schermate usano controlli standard che uno screen reader può percorrere.",
    ja: "全盲・弱視の方：すべての機能はテキストで使え、画像には説明が付き、画面はスクリーンリーダーがたどれる標準コントロールでできています。",
    zh: "盲人和低视力者：一切功能都可通过文字完成，图像带有描述，界面使用屏幕阅读器可以遍历的标准控件。",
    hi: "दृष्टिहीन और कम दृष्टि वाले: हर कार्य पाठ से होता है, चित्रों के साथ विवरण है, और स्क्रीन में मानक नियंत्रण हैं जिन्हें स्क्रीन रीडर पढ़ सकता है।",
    ar: "المكفوفون وضعاف البصر: كل وظيفة تعمل بالنص، والصور تحمل أوصافًا، والشاشات تستخدم عناصر قياسية يستطيع قارئ الشاشة تتبعها.",
  },
  "acc.needs.deaf": {
    en: "Deaf and hard of hearing: nothing here requires sound — voice is always optional, never the only way.",
    es: "Personas sordas o con pérdida auditiva: nada aquí requiere sonido; la voz es siempre opcional, nunca el único camino.",
    fr: "Personnes sourdes ou malentendantes : rien ici n’exige de son — la voix est toujours facultative, jamais le seul chemin.",
    de: "Gehörlose und schwerhörige Menschen: nichts hier verlangt Ton — Sprache ist immer optional, nie der einzige Weg.",
    pt: "Pessoas surdas ou com perda auditiva: nada aqui exige som — a voz é sempre opcional, nunca o único caminho.",
    it: "Persone sorde o con perdita d’udito: niente qui richiede l’audio — la voce è sempre facoltativa, mai l’unica via.",
    ja: "ろう・難聴の方：ここでは音を必要とするものはありません。音声は常に任意で、唯一の手段になることはありません。",
    zh: "聋人和听障者：这里没有任何功能依赖声音——语音永远是可选的，绝不是唯一途径。",
    hi: "बधिर और कम सुनने वाले: यहाँ किसी चीज़ के लिए ध्वनि आवश्यक नहीं — आवाज़ हमेशा वैकल्पिक है, कभी एकमात्र रास्ता नहीं।",
    ar: "الصم وضعاف السمع: لا شيء هنا يتطلب صوتًا — الصوت اختياري دائمًا، وليس الطريق الوحيد أبدًا.",
  },
  "acc.needs.mute": {
    en: "Mute and nonspeaking: nothing here requires speaking — anywhere a microphone is offered, typing does the same job.",
    es: "Personas mudas o que no hablan: nada aquí requiere hablar; donde se ofrece un micrófono, escribir hace el mismo trabajo.",
    fr: "Personnes muettes ou non verbales : rien ici n’exige de parler — partout où un micro est proposé, écrire fait le même travail.",
    de: "Stumme und nicht sprechende Menschen: nichts hier verlangt Sprechen — überall, wo ein Mikrofon angeboten wird, tut Tippen denselben Dienst.",
    pt: "Pessoas mudas ou não falantes: nada aqui exige falar — onde houver microfone, digitar faz o mesmo trabalho.",
    it: "Persone mute o non parlanti: niente qui richiede di parlare — ovunque ci sia un microfono, scrivere fa lo stesso lavoro.",
    ja: "発話しない方・発話が難しい方：ここでは話すことを必要とするものはありません。マイクがある場所ではどこでも、入力が同じ役割を果たします。",
    zh: "失语和不说话的人：这里没有任何功能要求开口——凡是提供麦克风的地方，打字都能完成同样的事。",
    hi: "मूक और न बोलने वाले: यहाँ बोलना आवश्यक नहीं — जहाँ भी माइक्रोफ़ोन है, वहाँ टाइप करना वही काम करता है।",
    ar: "البُكم ومن لا يتكلمون: لا شيء هنا يتطلب الكلام — أينما وُجد ميكروفون، تقوم الكتابة بالمهمة نفسها.",
  },
  "acc.needs.motor": {
    en: "Limited mobility, amputation, tremor: every control is a standard element the keyboard alone can reach, and no step in this console is timed.",
    es: "Movilidad reducida, amputación, temblor: cada control es un elemento estándar alcanzable solo con el teclado, y ningún paso de esta consola tiene límite de tiempo.",
    fr: "Mobilité réduite, amputation, tremblement : chaque contrôle est un élément standard atteignable au clavier seul, et aucune étape de cette console n’est chronométrée.",
    de: "Eingeschränkte Mobilität, Amputation, Tremor: jedes Element ist ein Standard-Element, das die Tastatur allein erreicht, und kein Schritt in dieser Konsole hat ein Zeitlimit.",
    pt: "Mobilidade reduzida, amputação, tremor: todo controle é um elemento padrão alcançável só pelo teclado, e nenhum passo neste console é cronometrado.",
    it: "Mobilità ridotta, amputazione, tremore: ogni controllo è un elemento standard raggiungibile con la sola tastiera, e nessun passaggio in questa console è a tempo.",
    ja: "運動機能の制約・切断・振戦のある方：すべてのコントロールはキーボードだけで届く標準要素で、このコンソールに制限時間のある操作はありません。",
    zh: "行动不便、截肢、震颤者：每个控件都是仅用键盘即可到达的标准元素，本控制台没有任何限时步骤。",
    hi: "सीमित गतिशीलता, अंग-विच्छेद, कंपन: हर नियंत्रण एक मानक तत्व है जिस तक केवल कीबोर्ड से पहुँचा जा सकता है, और इस कंसोल में कोई चरण समयबद्ध नहीं है।",
    ar: "محدودية الحركة والبتر والرُعاش: كل عنصر تحكم قياسي تصل إليه لوحة المفاتيح وحدها، ولا خطوة في هذه الواجهة مقيدة بوقت.",
  },
  "acc.needs.cognitive": {
    en: "Autistic and cognitively different people: plain words, one step at a time, nothing flashes, and asking again is always free.",
    es: "Personas autistas y cognitivamente diversas: palabras llanas, un paso a la vez, nada parpadea, y volver a preguntar es siempre gratis.",
    fr: "Personnes autistes et cognitivement différentes : des mots simples, une étape à la fois, rien ne clignote, et redemander est toujours gratuit.",
    de: "Autistische und kognitiv verschiedene Menschen: einfache Worte, ein Schritt nach dem anderen, nichts blinkt, und noch einmal fragen kostet nie etwas.",
    pt: "Pessoas autistas e cognitivamente diversas: palavras simples, um passo de cada vez, nada pisca, e perguntar de novo é sempre grátis.",
    it: "Persone autistiche e cognitivamente diverse: parole semplici, un passo alla volta, niente lampeggia, e chiedere di nuovo non costa mai nulla.",
    ja: "自閉スペクトラムの方・認知の仕方が異なる方：平易な言葉、一度にひとつの手順、点滅するものはなく、もう一度尋ねることはいつでも自由です。",
    zh: "自闭症和认知方式不同的人：语言平实，一次一步，没有闪烁的内容，再问一遍永远无妨。",
    hi: "ऑटिस्टिक और संज्ञानात्मक रूप से भिन्न लोग: सरल शब्द, एक समय में एक कदम, कुछ नहीं चमकता, और दोबारा पूछना हमेशा निःशुल्क है।",
    ar: "المصابون بالتوحد والمختلفون إدراكيًا: كلمات بسيطة، خطوة واحدة في كل مرة، لا شيء يومض، والسؤال مرة أخرى مجاني دائمًا.",
  },
  "acc.needs.dyslexia": {
    en: "Dyslexia and reading differences: short sentences, real headings, and nothing that punishes rereading.",
    es: "Dislexia y diferencias de lectura: frases cortas, encabezados reales y nada que castigue releer.",
    fr: "Dyslexie et différences de lecture : phrases courtes, vrais titres, et rien qui punisse la relecture.",
    de: "Dyslexie und Leseunterschiede: kurze Sätze, echte Überschriften, und nichts bestraft erneutes Lesen.",
    pt: "Dislexia e diferenças de leitura: frases curtas, títulos de verdade e nada que puna reler.",
    it: "Dislessia e differenze di lettura: frasi brevi, titoli veri e niente che punisca il rileggere.",
    ja: "ディスレクシア・読み方の異なる方：短い文、本物の見出し、読み返しても不利にならない画面。",
    zh: "阅读障碍者：短句、真实的标题，重读不会受到任何惩罚。",
    hi: "डिस्लेक्सिया और पढ़ने की भिन्नताएँ: छोटे वाक्य, वास्तविक शीर्षक, और दोबारा पढ़ने पर कोई दंड नहीं।",
    ar: "عسر القراءة وفروق القراءة: جمل قصيرة وعناوين حقيقية ولا شيء يعاقب على إعادة القراءة.",
  },
  "acc.needs.motion": {
    en: "Motion sensitivity: when your device asks for reduced motion, this console stops animating.",
    es: "Sensibilidad al movimiento: cuando tu dispositivo pide movimiento reducido, esta consola deja de animar.",
    fr: "Sensibilité au mouvement : quand votre appareil demande une animation réduite, cette console cesse d’animer.",
    de: "Bewegungsempfindlichkeit: wenn dein Gerät reduzierte Bewegung verlangt, hört diese Konsole auf zu animieren.",
    pt: "Sensibilidade a movimento: quando seu dispositivo pede movimento reduzido, este console para de animar.",
    it: "Sensibilità al movimento: quando il tuo dispositivo chiede movimento ridotto, questa console smette di animare.",
    ja: "動きに敏感な方：端末が「視差効果を減らす」を求めると、このコンソールはアニメーションを止めます。",
    zh: "对动态敏感者：当你的设备要求减少动态效果时，本控制台会停止动画。",
    hi: "गति के प्रति संवेदनशीलता: जब आपका उपकरण कम गति माँगता है, यह कंसोल एनिमेशन बंद कर देता है।",
    ar: "الحساسية للحركة: عندما يطلب جهازك تقليل الحركة، تتوقف هذه الواجهة عن التحريك.",
  },
  "acc.needs.more": {
    en: "Not on this list? The gap is in the list, not in you. Name it below and it becomes our work.",
    es: "¿No estás en esta lista? El vacío está en la lista, no en ti. Nómbralo abajo y se convierte en nuestro trabajo.",
    fr: "Pas sur cette liste ? Le manque est dans la liste, pas en vous. Nommez-le ci-dessous et cela devient notre travail.",
    de: "Nicht auf dieser Liste? Die Lücke ist in der Liste, nicht in dir. Benenne sie unten, und sie wird unsere Arbeit.",
    pt: "Não está nesta lista? A lacuna está na lista, não em você. Nomeie-a abaixo e ela vira nosso trabalho.",
    it: "Non sei in questa lista? La lacuna è nella lista, non in te. Nominala qui sotto e diventa il nostro lavoro.",
    ja: "この一覧にありませんか？足りないのは一覧であって、あなたではありません。下で名前を付けてください。それが私たちの仕事になります。",
    zh: "不在这份清单上？缺的是清单，不是你。在下方写出来，它就成为我们的工作。",
    hi: "इस सूची में नहीं हैं? कमी सूची में है, आप में नहीं। नीचे उसे नाम दें और वह हमारा काम बन जाएगा।",
    ar: "لست في هذه القائمة؟ النقص في القائمة لا فيك. اذكره أدناه وسيصبح عملنا.",
  },
  "acc.report.title": {
    en: "Say what stood in the way",
    es: "Di qué se interpuso",
    fr: "Dites ce qui a fait obstacle",
    de: "Sag, was im Weg stand",
    pt: "Diga o que ficou no caminho",
    it: "Di’ cosa ti ha ostacolato",
    ja: "何が妨げになったかを教えてください",
    zh: "写出是什么挡住了你",
    hi: "बताइए क्या आड़े आया",
    ar: "اذكر ما الذي وقف في طريقك",
  },
  "acc.report.lead": {
    en: "Three questions. No account, no diagnosis, no name. Your words stay on this deployment, are read by the person who runs it, and become tracked work.",
    es: "Tres preguntas. Sin cuenta, sin diagnóstico, sin nombre. Tus palabras se quedan en esta instalación, las lee quien la administra y se convierten en trabajo registrado.",
    fr: "Trois questions. Pas de compte, pas de diagnostic, pas de nom. Vos mots restent sur cette installation, sont lus par la personne qui la gère et deviennent du travail suivi.",
    de: "Drei Fragen. Kein Konto, keine Diagnose, kein Name. Deine Worte bleiben auf dieser Installation, werden von der betreibenden Person gelesen und werden zu verfolgter Arbeit.",
    pt: "Três perguntas. Sem conta, sem diagnóstico, sem nome. Suas palavras ficam nesta instalação, são lidas por quem a administra e viram trabalho registrado.",
    it: "Tre domande. Niente account, niente diagnosi, niente nome. Le tue parole restano su questa installazione, le legge chi la gestisce e diventano lavoro tracciato.",
    ja: "質問は3つ。アカウントも診断名も名前も要りません。あなたの言葉はこの環境にとどまり、運営者が読み、追跡される作業になります。",
    zh: "三个问题。无需账户、无需诊断、无需姓名。你的话留在此部署中，由运营者阅读，并成为被追踪的工作。",
    hi: "तीन प्रश्न। न खाता, न निदान, न नाम। आपके शब्द इसी परिनियोजन में रहते हैं, इसे चलाने वाला व्यक्ति उन्हें पढ़ता है, और वे दर्ज कार्य बन जाते हैं।",
    ar: "ثلاثة أسئلة. لا حساب ولا تشخيص ولا اسم. تبقى كلماتك على هذا النشر، يقرؤها من يديره، وتصبح عملًا متتبعًا.",
  },
  "acc.report.doing": {
    en: "What were you trying to do?",
    es: "¿Qué intentabas hacer?",
    fr: "Qu’essayiez-vous de faire ?",
    de: "Was hast du versucht zu tun?",
    pt: "O que você estava tentando fazer?",
    it: "Cosa stavi cercando di fare?",
    ja: "何をしようとしていましたか？",
    zh: "你当时想做什么？",
    hi: "आप क्या करने की कोशिश कर रहे थे?",
    ar: "ما الذي كنت تحاول فعله؟",
  },
  "acc.report.wall": {
    en: "What stood in the way?",
    es: "¿Qué se interpuso?",
    fr: "Qu’est-ce qui a fait obstacle ?",
    de: "Was stand im Weg?",
    pt: "O que ficou no caminho?",
    it: "Cosa ti ha ostacolato?",
    ja: "何が妨げになりましたか？",
    zh: "是什么挡住了你？",
    hi: "क्या आड़े आया?",
    ar: "ما الذي وقف في الطريق؟",
  },
  "acc.report.help": {
    en: "What would help? (optional)",
    es: "¿Qué ayudaría? (opcional)",
    fr: "Qu’est-ce qui aiderait ? (facultatif)",
    de: "Was würde helfen? (optional)",
    pt: "O que ajudaria? (opcional)",
    it: "Cosa aiuterebbe? (facoltativo)",
    ja: "何があれば助かりますか？（任意）",
    zh: "什么会有帮助？（可选）",
    hi: "क्या मदद करेगा? (वैकल्पिक)",
    ar: "ما الذي قد يساعد؟ (اختياري)",
  },
  "acc.report.send": {
    en: "Send report",
    es: "Enviar informe",
    fr: "Envoyer le signalement",
    de: "Bericht senden",
    pt: "Enviar relato",
    it: "Invia la segnalazione",
    ja: "報告を送る",
    zh: "发送报告",
    hi: "रिपोर्ट भेजें",
    ar: "أرسل البلاغ",
  },
  "acc.report.sent": {
    en: "Received — thank you.",
    es: "Recibido. Gracias.",
    fr: "Reçu — merci.",
    de: "Angekommen — danke.",
    pt: "Recebido — obrigado.",
    it: "Ricevuto — grazie.",
    ja: "受け取りました。ありがとうございます。",
    zh: "已收到——谢谢。",
    hi: "प्राप्त हुआ — धन्यवाद।",
    ar: "وصل البلاغ — شكرًا لك.",
  },
  "acc.review.title": {
    en: "The reports",
    es: "Los informes",
    fr: "Les signalements",
    de: "Die Berichte",
    pt: "Os relatos",
    it: "Le segnalazioni",
    ja: "届いた報告",
    zh: "收到的报告",
    hi: "रिपोर्टें",
    ar: "البلاغات",
  },
  "acc.review.lead": {
    en: "For whoever stands for this deployment: read with the reviewer token, the same role that adjudicates objections.",
    es: "Para quien responde por esta instalación: se leen con el token de revisor, el mismo rol que resuelve objeciones.",
    fr: "Pour la personne qui répond de cette installation : lecture avec le jeton de réviseur, le même rôle qui tranche les objections.",
    de: "Für die Person, die für diese Installation einsteht: gelesen mit dem Prüfer-Token, derselben Rolle, die Einsprüche entscheidet.",
    pt: "Para quem responde por esta instalação: leia com o token de revisor, o mesmo papel que julga objeções.",
    it: "Per chi risponde di questa installazione: si leggono con il token del revisore, lo stesso ruolo che giudica le obiezioni.",
    ja: "この環境に責任を持つ人へ：異議を裁定するのと同じレビュアートークンで読みます。",
    zh: "供为此部署负责的人使用：用审阅者令牌读取，与裁决异议的是同一角色。",
    hi: "जो इस परिनियोजन के लिए उत्तरदायी है: समीक्षक टोकन से पढ़ें — वही भूमिका जो आपत्तियों का निर्णय करती है।",
    ar: "لمن يتحمل مسؤولية هذا النشر: تُقرأ برمز المراجع، الدور نفسه الذي يفصل في الاعتراضات.",
  },
  "acc.review.token": {
    en: "Reviewer token",
    es: "Token de revisor",
    fr: "Jeton de réviseur",
    de: "Prüfer-Token",
    pt: "Token de revisor",
    it: "Token del revisore",
    ja: "レビュアートークン",
    zh: "审阅者令牌",
    hi: "समीक्षक टोकन",
    ar: "رمز المراجع",
  },
  "acc.review.load": {
    en: "Load reports",
    es: "Cargar informes",
    fr: "Charger les signalements",
    de: "Berichte laden",
    pt: "Carregar relatos",
    it: "Carica le segnalazioni",
    ja: "報告を読み込む",
    zh: "载入报告",
    hi: "रिपोर्टें लोड करें",
    ar: "حمّل البلاغات",
  },
  "acc.review.empty": {
    en: "No reports yet.",
    es: "Aún no hay informes.",
    fr: "Aucun signalement pour l’instant.",
    de: "Noch keine Berichte.",
    pt: "Ainda não há relatos.",
    it: "Ancora nessuna segnalazione.",
    ja: "まだ報告はありません。",
    zh: "还没有报告。",
    hi: "अभी कोई रिपोर्ट नहीं।",
    ar: "لا بلاغات بعد.",
  },
  "acc.review.sealed": {
    en: "sealed to the vault",
    es: "sellado en la bóveda",
    fr: "scellé dans le coffre",
    de: "im Tresor versiegelt",
    pt: "selado no cofre",
    it: "sigillato nel caveau",
    ja: "ボールトに封印済み",
    zh: "已封存到保险库",
    hi: "वॉल्ट में सील किया गया",
    ar: "مختوم في الخزنة",
  },
  "onb.create": {
    en: "Create account",
    es: "Crear cuenta",
    fr: "Créer un compte",
    de: "Konto erstellen",
    pt: "Criar conta",
    it: "Crea account",
    ja: "アカウントを作成",
    zh: "创建账户",
    hi: "खाता बनाएँ",
    ar: "إنشاء حساب",
  },
  "onb.signin": {
    en: "Sign in",
    es: "Iniciar sesión",
    fr: "Se connecter",
    de: "Anmelden",
    pt: "Entrar",
    it: "Accedi",
    ja: "サインイン",
    zh: "登录",
    hi: "साइन इन करें",
    ar: "تسجيل الدخول",
  },
  "onb.noemail": {
    en: "Start without an email address",
    es: "Empezar sin correo electrónico",
    fr: "Commencer sans adresse e-mail",
    de: "Ohne E-Mail-Adresse beginnen",
    pt: "Começar sem endereço de e-mail",
    it: "Inizia senza indirizzo email",
    ja: "メールアドレスなしで始める",
    zh: "不使用电子邮箱开始",
    hi: "बिना ईमेल के शुरू करें",
    ar: "ابدأ بدون بريد إلكتروني",
  },
  "onb.name": {
    en: "Name",
    es: "Nombre",
    fr: "Nom",
    de: "Name",
    pt: "Nome",
    it: "Nome",
    ja: "名前",
    zh: "姓名",
    hi: "नाम",
    ar: "الاسم",
  },
  "onb.yourname": {
    en: "Your name",
    es: "Tu nombre",
    fr: "Votre nom",
    de: "Dein Name",
    pt: "O seu nome",
    it: "Il tuo nome",
    ja: "お名前",
    zh: "你的姓名",
    hi: "आपका नाम",
    ar: "اسمك",
  },
  "onb.email": {
    en: "Email",
    es: "Correo electrónico",
    fr: "E-mail",
    de: "E-Mail",
    pt: "E-mail",
    it: "Email",
    ja: "メールアドレス",
    zh: "电子邮箱",
    hi: "ईमेल",
    ar: "البريد الإلكتروني",
  },
  "onb.password.min": {
    en: "At least 8 characters",
    es: "Al menos 8 caracteres",
    fr: "Au moins 8 caractères",
    de: "Mindestens 8 Zeichen",
    pt: "Pelo menos 8 caracteres",
    it: "Almeno 8 caratteri",
    ja: "8文字以上",
    zh: "至少 8 个字符",
    hi: "कम से कम 8 अक्षर",
    ar: "٨ أحرف على الأقل",
  },
  "onb.password.same": {
    en: "Same password again",
    es: "La misma contraseña otra vez",
    fr: "Le même mot de passe",
    de: "Dasselbe Passwort erneut",
    pt: "A mesma palavra-passe",
    it: "La stessa password",
    ja: "同じパスワードをもう一度",
    zh: "再输入一次相同的密码",
    hi: "वही पासवर्ड दोबारा",
    ar: "نفس كلمة المرور مرة أخرى",
  },
  "onb.code": {
    en: "Verification code",
    es: "Código de verificación",
    fr: "Code de vérification",
    de: "Bestätigungscode",
    pt: "Código de verificação",
    it: "Codice di verifica",
    ja: "確認コード",
    zh: "验证码",
    hi: "सत्यापन कोड",
    ar: "رمز التحقق",
  },
  "onb.code.resend": {
    en: "Resend code",
    es: "Reenviar código",
    fr: "Renvoyer le code",
    de: "Code erneut senden",
    pt: "Reenviar código",
    it: "Invia di nuovo il codice",
    ja: "コードを再送",
    zh: "重新发送验证码",
    hi: "कोड फिर भेजें",
    ar: "إعادة إرسال الرمز",
  },
  "onb.reset.code": {
    en: "Reset code",
    es: "Código de restablecimiento",
    fr: "Code de réinitialisation",
    de: "Zurücksetz-Code",
    pt: "Código de reposição",
    it: "Codice di reimpostazione",
    ja: "リセットコード",
    zh: "重置码",
    hi: "रीसेट कोड",
    ar: "رمز إعادة التعيين",
  },
  "onb.reset.send": {
    en: "Send reset code",
    es: "Enviar código de restablecimiento",
    fr: "Envoyer le code de réinitialisation",
    de: "Zurücksetz-Code senden",
    pt: "Enviar código de reposição",
    it: "Invia codice di reimpostazione",
    ja: "リセットコードを送信",
    zh: "发送重置码",
    hi: "रीसेट कोड भेजें",
    ar: "إرسال رمز إعادة التعيين",
  },
  "onb.forgot": {
    en: "Forgot password?",
    es: "¿Olvidaste tu contraseña?",
    fr: "Mot de passe oublié ?",
    de: "Passwort vergessen?",
    pt: "Esqueceu-se da palavra-passe?",
    it: "Password dimenticata?",
    ja: "パスワードをお忘れですか？",
    zh: "忘记密码？",
    hi: "पासवर्ड भूल गए?",
    ar: "هل نسيت كلمة المرور؟",
  },
  "onb.back": {
    en: "Back to sign in",
    es: "Volver a iniciar sesión",
    fr: "Retour à la connexion",
    de: "Zurück zur Anmeldung",
    pt: "Voltar a entrar",
    it: "Torna all'accesso",
    ja: "サインインに戻る",
    zh: "返回登录",
    hi: "साइन इन पर वापस जाएँ",
    ar: "العودة إلى تسجيل الدخول",
  },
  "onb.guardian": {
    en: "Parent or guardian email — the activation code goes to them",
    es: "Correo del padre, madre o tutor — el código de activación les llega a ellos",
    fr: "Courriel du parent ou tuteur — le code d'activation leur est envoyé",
    de: "E-Mail der Eltern oder Erziehungsberechtigten — der Aktivierungscode geht an sie",
    pt: "Email do pai, mãe ou responsável — o código de ativação vai para eles",
    it: "Email del genitore o tutore — il codice di attivazione arriva a loro",
    ja: "保護者のメールアドレス — 有効化コードは保護者に届きます",
    zh: "父母或监护人邮箱 — 激活码会发送给他们",
    hi: "माता-पिता या अभिभावक का ईमेल — सक्रियण कोड उन्हें जाता है",
    ar: "بريد الوالد أو الوصي — يُرسل رمز التفعيل إليهم",
  },
  "onb.birthdate": {
    en: "Birthdate",
    es: "Fecha de nacimiento",
    fr: "Date de naissance",
    de: "Geburtsdatum",
    pt: "Data de nascimento",
    it: "Data di nascita",
    ja: "生年月日",
    zh: "出生日期",
    hi: "जन्म तिथि",
    ar: "تاريخ الميلاد",
  },
  "onb.legalname": {
    en: "Legal name, for emergencies only (optional)",
    es: "Nombre legal, solo para emergencias (opcional)",
    fr: "Nom légal, pour les urgences seulement (facultatif)",
    de: "Amtlicher Name, nur für Notfälle (optional)",
    pt: "Nome legal, apenas para emergências (opcional)",
    it: "Nome legale, solo per emergenze (facoltativo)",
    ja: "法的な氏名（緊急時のみ・任意）",
    zh: "法定姓名，仅用于紧急情况（可选）",
    hi: "कानूनी नाम, केवल आपात स्थिति के लिए (वैकल्पिक)",
    ar: "الاسم القانوني، للطوارئ فقط (اختياري)",
  },
  "onb.legalname.blank": {
    en: "leaving this blank is fine",
    es: "dejarlo en blanco está bien",
    fr: "le laisser vide convient",
    de: "es leer zu lassen ist in Ordnung",
    pt: "deixar em branco não faz mal",
    it: "lasciarlo vuoto va bene",
    ja: "空欄のままで構いません",
    zh: "留空也可以",
    hi: "इसे खाली छोड़ना ठीक है",
    ar: "تركه فارغًا لا بأس به",
  },
  "onb.consent": {
    en: "I consent to the terms of use",
    es: "Acepto las condiciones de uso",
    fr: "J'accepte les conditions d'utilisation",
    de: "Ich stimme den Nutzungsbedingungen zu",
    pt: "Aceito os termos de utilização",
    it: "Accetto i termini d'uso",
    ja: "利用規約に同意します",
    zh: "我同意使用条款",
    hi: "मैं उपयोग की शर्तों से सहमत हूँ",
    ar: "أوافق على شروط الاستخدام",
  },
  "onb.backend": {
    en: "Backend URL",
    es: "URL del servidor",
    fr: "URL du serveur",
    de: "Backend-URL",
    pt: "URL do servidor",
    it: "URL del backend",
    ja: "バックエンドURL",
    zh: "后端地址",
    hi: "बैकएंड URL",
    ar: "عنوان الخادم",
  },
  "ch.intimate": {
    en: " (intimate)", es: " (íntimo)", fr: " (intime)", de: " (intim)", pt: " (íntimo)", it: " (intimo)", ja: "（親密）", zh: "（亲密）", hi: " (अंतरंग)", ar: " (حميم)",
  },
  "ch.reaches": {
    en: " ·  reaches others", es: " ·  llega a otras personas", fr: " ·  atteint d'autres personnes", de: " ·  erreicht andere", pt: " ·  chega a outras pessoas", it: " ·  raggiunge altri", ja: " ·  他の人に届きます", zh: " ·  会触及他人", hi: " ·  दूसरों तक पहुँचता है", ar: " ·  يصل إلى آخرين",
  },
  "ch.sealed.plan": {
    en: " Sealed in the vault; a private plan is required.", es: " Sellado en la bóveda; se requiere un plan privado.", fr: " Scellé dans le coffre ; un forfait privé est requis.", de: " Im Tresor versiegelt; ein privater Tarif ist erforderlich.", pt: " Selado no cofre; é necessário um plano privado.", it: " Sigillato nel caveau; serve un piano privato.", ja: "保管庫に封印されます。プライベートプランが必要です。", zh: "已封入保险库；需要私有方案。", hi: " तिजोरी में सील; निजी योजना आवश्यक है।", ar: " مختوم في الخزنة؛ يلزم اشتراك خاص.",
  },
  "ch.shown": {
    en: "Shown", es: "Mostrado", fr: "Affiché", de: "Angezeigt", pt: "Mostrado", it: "Mostrato", ja: "表示中", zh: "已显示", hi: "दिखाया गया", ar: "معروض",
  },
  "ch.look": {
    en: "Look at it", es: "Míralo", fr: "Regarder", de: "Ansehen", pt: "Ver", it: "Guardalo", ja: "見る", zh: "查看", hi: "इसे देखें", ar: "انظر إليه",
  },
  "ch.title": {
    en: "Channel & camera", es: "Canal y cámara", fr: "Canal et caméra", de: "Kanal & Kamera", pt: "Canal e câmara", it: "Canale e fotocamera", ja: "チャンネルとカメラ", zh: "通道与相机", hi: "चैनल और कैमरा", ar: "القناة والكاميرا",
  },
  "ch.signin": {
    en: "Sign in to set up the channel.", es: "Inicia sesión para configurar el canal.", fr: "Connectez-vous pour configurer le canal.", de: "Melde dich an, um den Kanal einzurichten.", pt: "Inicie sessão para configurar o canal.", it: "Accedi per configurare il canale.", ja: "チャンネルを設定するにはサインインしてください。", zh: "登录以设置通道。", hi: "चैनल सेट करने के लिए साइन इन करें।", ar: "سجّل الدخول لإعداد القناة.",
  },
  "ch.devices": {
    en: "Devices", es: "Dispositivos", fr: "Appareils", de: "Geräte", pt: "Dispositivos", it: "Dispositivi", ja: "デバイス", zh: "设备", hi: "उपकरण", ar: "الأجهزة",
  },
  "ch.devices.lead": {
    en: "A microphone attaches to a device this account already knows, never to a name typed in the moment — so what is listening is always something you registered on purpose.", es: "Un micrófono se conecta a un dispositivo que esta cuenta ya conoce, nunca a un nombre escrito en el momento — así lo que escucha es siempre algo que registraste a propósito.", fr: "Un micro s'attache à un appareil que ce compte connaît déjà, jamais à un nom tapé sur le moment — ce qui écoute est donc toujours quelque chose que vous avez enregistré exprès.", de: "Ein Mikrofon hängt an einem Gerät, das dieses Konto bereits kennt, nie an einem eben eingetippten Namen — was zuhört, ist also immer etwas, das du absichtlich registriert hast.", pt: "Um microfone liga-se a um dispositivo que esta conta já conhece, nunca a um nome escrito no momento — o que está a ouvir é sempre algo que registou de propósito.", it: "Un microfono si collega a un dispositivo che questo account già conosce, mai a un nome digitato al momento — ciò che ascolta è sempre qualcosa che hai registrato apposta.", ja: "マイクはこのアカウントが既に知るデバイスにのみ接続され、その場で入力した名前には接続されません — 聞いているのは常にあなたが意図して登録したものです。", zh: "麦克风只连接到此账户已知的设备，绝不连接临时输入的名称 — 因此在聆听的始终是你有意注册的设备。", hi: "माइक्रोफ़ोन उसी उपकरण से जुड़ता है जिसे यह खाता पहले से जानता है, तुरंत टाइप किए नाम से कभी नहीं — तो जो सुन रहा है वह हमेशा आपका जानबूझकर पंजीकृत उपकरण है।", ar: "يرتبط الميكروفون بجهاز يعرفه هذا الحساب مسبقًا، لا باسم يُكتب في اللحظة — فما يستمع هو دائمًا شيء سجّلته عمدًا.",
  },
  "ch.dev.model": {
    en: "runs a model", es: "ejecuta un modelo", fr: "exécute un modèle", de: "führt ein Modell aus", pt: "executa um modelo", it: "esegue un modello", ja: "モデル搭載", zh: "运行模型", hi: "मॉडल चलाता है", ar: "يشغّل نموذجًا",
  },
  "ch.dev.name": {
    en: "Device name", es: "Nombre del dispositivo", fr: "Nom de l'appareil", de: "Gerätename", pt: "Nome do dispositivo", it: "Nome del dispositivo", ja: "デバイス名", zh: "设备名称", hi: "उपकरण का नाम", ar: "اسم الجهاز",
  },
  "ch.dev.register": {
    en: "Register", es: "Registrar", fr: "Enregistrer", de: "Registrieren", pt: "Registar", it: "Registra", ja: "登録", zh: "登记", hi: "पंजीकृत करें", ar: "تسجيل",
  },
  "ch.mic": {
    en: "Channel 2 — what JIM hears", es: "Canal 2 — lo que oye JIM", fr: "Canal 2 — ce que JIM entend", de: "Kanal 2 — was JIM hört", pt: "Canal 2 — o que o JIM ouve", it: "Canale 2 — ciò che JIM sente", ja: "チャンネル2 — JIMに聞こえるもの", zh: "通道2 — JIM听到的", hi: "चैनल 2 — JIM क्या सुनता है", ar: "القناة 2 — ما يسمعه JIM",
  },
  "ch.mic.handover": {
    en: "Hand channel 2 over", es: "Ceder el canal 2", fr: "Céder le canal 2", de: "Kanal 2 übergeben", pt: "Ceder o canal 2", it: "Cedi il canale 2", ja: "チャンネル2を引き渡す", zh: "移交通道2", hi: "चैनल 2 सौंपें", ar: "تسليم القناة 2",
  },
  "mon.screen.watch": {
    en: "Let JIM see this screen", es: "Deja que JIM vea esta pantalla", fr: "Laisser JIM voir cet écran", de: "JIM diesen Bildschirm sehen lassen", pt: "Deixar o JIM ver este ecrã", it: "Lascia che JIM veda questo schermo", ja: "この画面をJIMに見せる", zh: "让 JIM 看这个屏幕", hi: "JIM को यह स्क्रीन देखने दें", ar: "دع جيم يرى هذه الشاشة",
  },
  "mon.screen.stop": {
    en: "Stop showing the screen", es: "Dejar de mostrar la pantalla", fr: "Ne plus montrer l'écran", de: "Bildschirm nicht mehr zeigen", pt: "Parar de mostrar o ecrã", it: "Smetti di mostrare lo schermo", ja: "画面を見せるのをやめる", zh: "停止显示屏幕", hi: "स्क्रीन दिखाना बंद करें", ar: "توقّف عن عرض الشاشة",
  },
  "ch.mic.heard": {
    en: "what your microphone picked up", es: "lo que captó tu micrófono", fr: "ce que votre microphone a capté", de: "was dein Mikrofon aufgenommen hat", pt: "o que o seu microfone captou", it: "ciò che il tuo microfono ha captato", ja: "マイクが拾った内容", zh: "你的麦克风拾取到的内容", hi: "आपके माइक्रोफ़ोन ने जो पकड़ा", ar: "ما التقطه الميكروفون الخاص بك",
  },
  "ch.mic.capped": {
    en: "Narrowed for the moment — a call is in progress. Your setting ({gain}) comes back afterwards.", es: "Reducido por el momento — hay una llamada en curso. Tu ajuste ({gain}) vuelve después.", fr: "Restreint pour le moment — un appel est en cours. Votre réglage ({gain}) revient ensuite.", de: "Vorübergehend verengt — ein Anruf läuft. Deine Einstellung ({gain}) kehrt danach zurück.", pt: "Reduzido por agora — há uma chamada em curso. O seu ajuste ({gain}) volta depois.", it: "Ridotto per il momento — c'è una chiamata in corso. La tua impostazione ({gain}) torna dopo.", ja: "通話中のため一時的に絞られています。設定（{gain}）は通話後に戻ります。", zh: "通话进行中，暂时收窄。你的设置（{gain}）稍后恢复。", hi: "फ़िलहाल सीमित — कॉल चल रही है। आपकी सेटिंग ({gain}) बाद में लौट आएगी।", ar: "مقيَّد مؤقتًا — هناك مكالمة جارية. إعدادك ({gain}) يعود بعدها.",
  },
  "ch.mic.release": {
    en: "Release", es: "Liberar", fr: "Libérer", de: "Freigeben", pt: "Libertar", it: "Rilascia", ja: "解放", zh: "释放", hi: "छोड़ें", ar: "تحرير",
  },
  "ch.mic.detach": {
    en: "Detach", es: "Desconectar", fr: "Détacher", de: "Trennen", pt: "Desligar", it: "Scollega", ja: "取り外す", zh: "断开", hi: "हटाएँ", ar: "فصل",
  },
  "ch.mic.none": {
    en: "Nothing attached. JIM is not listening.", es: "Nada conectado. JIM no está escuchando.", fr: "Rien d'attaché. JIM n'écoute pas.", de: "Nichts angeschlossen. JIM hört nicht zu.", pt: "Nada ligado. O JIM não está a ouvir.", it: "Niente collegato. JIM non sta ascoltando.", ja: "何も接続されていません。JIMは聞いていません。", zh: "未连接任何设备。JIM没有在听。", hi: "कुछ नहीं जुड़ा। JIM सुन नहीं रहा।", ar: "لا شيء موصول. JIM لا يستمع.",
  },
  "ch.mic.which": {
    en: "Which device…", es: "Qué dispositivo…", fr: "Quel appareil…", de: "Welches Gerät…", pt: "Que dispositivo…", it: "Quale dispositivo…", ja: "どのデバイス…", zh: "哪个设备…", hi: "कौन-सा उपकरण…", ar: "أي جهاز…",
  },
  "ch.mic.kind": {
    en: "What kind of microphone…", es: "Qué tipo de micrófono…", fr: "Quel type de micro…", de: "Welche Art Mikrofon…", pt: "Que tipo de microfone…", it: "Che tipo di microfono…", ja: "どの種類のマイク…", zh: "哪种麦克风…", hi: "किस तरह का माइक…", ar: "أي نوع من الميكروفون…",
  },
  "ch.mic.attach": {
    en: "Attach", es: "Conectar", fr: "Attacher", de: "Anschließen", pt: "Ligar", it: "Collega", ja: "接続", zh: "连接", hi: "जोड़ें", ar: "توصيل",
  },
  "ch.mic.refused": {
    en: "Not offered: {list} — {rule}", es: "No se ofrecen: {list} — {rule}", fr: "Non proposés : {list} — {rule}", de: "Nicht angeboten: {list} — {rule}", pt: "Não oferecidos: {list} — {rule}", it: "Non offerti: {list} — {rule}", ja: "提供されません: {list} — {rule}", zh: "不提供：{list} — {rule}", hi: "उपलब्ध नहीं: {list} — {rule}", ar: "غير معروض: {list} — {rule}",
  },
  "ch.hist": {
    en: "When it was open", es: "Cuándo estuvo abierto", fr: "Quand il était ouvert", de: "Wann er offen war", pt: "Quando esteve aberto", it: "Quando era aperto", ja: "開いていた時間", zh: "开启的时段", hi: "कब खुला था", ar: "متى كانت مفتوحة",
  },
  "ch.hist.live": {
    en: "live", es: "en vivo", fr: "en direct", de: "live", pt: "em direto", it: "in diretta", ja: "ライブ", zh: "直播中", hi: "लाइव", ar: "مباشر",
  },
  "ch.cam": {
    en: "Clinical camera", es: "Cámara clínica", fr: "Caméra clinique", de: "Klinische Kamera", pt: "Câmara clínica", it: "Fotocamera clinica", ja: "臨床カメラ", zh: "临床相机", hi: "क्लिनिकल कैमरा", ar: "الكاميرا السريرية",
  },
  "ch.cam.intimate": {
    en: "intimate", es: "íntimo", fr: "intime", de: "intim", pt: "íntimo", it: "intimo", ja: "プライベート", zh: "隐私部位", hi: "निजी", ar: "حسّاس",
  },
  "ch.cam.withdraw": {
    en: "Withdraw", es: "Retirar", fr: "Retirer", de: "Zurückziehen", pt: "Retirar", it: "Ritira", ja: "取り下げる", zh: "撤回", hi: "वापस लें", ar: "سحب",
  },
  "ch.cam.attach": {
    en: "Attach {n}to a referral", es: "Adjuntar {n}a una derivación", fr: "Joindre {n}à une orientation", de: "{n}an eine Überweisung anhängen", pt: "Anexar {n}a um encaminhamento", it: "Allega {n}a un referto", ja: "{n}件を紹介状に添付", zh: "将{n}附到转诊", hi: "{n}रेफ़रल में जोड़ें", ar: "إرفاق {n}بإحالة",
  },
  "ch.cam.where": {
    en: "Where on the body…", es: "En qué parte del cuerpo…", fr: "Où sur le corps…", de: "Wo am Körper…", pt: "Onde no corpo…", it: "Dove sul corpo…", ja: "体のどこ…", zh: "身体哪个部位…", hi: "शरीर पर कहाँ…", ar: "أين في الجسم…",
  },
  "ch.cam.for": {
    en: "What it is for (optional)", es: "Para qué es (opcional)", fr: "À quoi ça sert (facultatif)", de: "Wofür es ist (optional)", pt: "Para que serve (opcional)", it: "A cosa serve (facoltativo)", ja: "何のためか（任意）", zh: "用途（可选）", hi: "किसलिए है (वैकल्पिक)", ar: "لأي غرض (اختياري)",
  },
  "ch.cam.note": {
    en: "Note (optional)", es: "Nota (opcional)", fr: "Note (facultatif)", de: "Notiz (optional)", pt: "Nota (opcional)", it: "Nota (facoltativa)", ja: "メモ（任意）", zh: "备注（可选）", hi: "नोट (वैकल्पिक)", ar: "ملاحظة (اختياري)",
  },
  "ch.cam.consent": {
    en: "This is an intimate site and I am choosing to record it.", es: "Es una zona íntima y elijo registrarla.", fr: "C'est une zone intime et je choisis de l'enregistrer.", de: "Dies ist eine intime Stelle, und ich entscheide mich, sie aufzunehmen.", pt: "É uma zona íntima e escolho registá-la.", it: "È una zona intima e scelgo di registrarla.", ja: "これはプライベートな部位であり、私は記録することを選びます。", zh: "这是隐私部位，我选择记录它。", hi: "यह निजी अंग है और मैं इसे दर्ज करना चुन रहा/रही हूँ।", ar: "هذا موضع حسّاس وأنا أختار تسجيله.",
  },
  "ch.cam.site": {
    en: "Choose a site first.", es: "Elige primero una zona.", fr: "Choisissez d'abord une zone.", de: "Wähl zuerst eine Stelle.", pt: "Escolha primeiro uma zona.", it: "Scegli prima una zona.", ja: "まず部位を選んでください。", zh: "请先选择部位。", hi: "पहले स्थान चुनें।", ar: "اختر الموضع أولاً.",
  },
  "ch.cam.tick": {
    en: "Tick the box before choosing a file.", es: "Marca la casilla antes de elegir un archivo.", fr: "Cochez la case avant de choisir un fichier.", de: "Setz das Häkchen, bevor du eine Datei wählst.", pt: "Marque a caixa antes de escolher um ficheiro.", it: "Spunta la casella prima di scegliere un file.", ja: "ファイルを選ぶ前にチェックを入れてください。", zh: "选择文件前请先勾选。", hi: "फ़ाइल चुनने से पहले बॉक्स चिह्नित करें।", ar: "ضع علامة في المربع قبل اختيار ملف.",
  },
  "att.ch.configured": {
    en: "configured", es: "configurado", fr: "configuré", de: "eingerichtet", pt: "configurado", it: "configurato", ja: "設定済み", zh: "已配置", hi: "कॉन्फ़िगर किया गया", ar: "مُهيّأ",
  },
  "att.ch.unconfigured": {
    en: "not configured", es: "sin configurar", fr: "non configuré", de: "nicht eingerichtet", pt: "por configurar", it: "non configurato", ja: "未設定", zh: "未配置", hi: "कॉन्फ़िगर नहीं", ar: "غير مُهيّأ",
  },
  "att.ch.signed": {
    en: ", signed", es: ", firmado", fr: ", signé", de: ", signiert", pt: ", assinado", it: ", firmato", ja: "、署名済み", zh: "，已签名", hi: ", हस्ताक्षरित", ar: "، موقَّع",
  },
  "att.rota.nobody": {
    en: "Nobody is on shift", es: "Nadie está de turno", fr: "Personne n'est de service", de: "Niemand hat Dienst", pt: "Ninguém está de turno", it: "Nessuno è di turno", ja: "当番は誰もいません", zh: "无人当班", hi: "कोई शिफ़्ट पर नहीं", ar: "لا أحد في النوبة",
  },
  "att.title": {
    en: "Who else is looking", es: "Quién más está mirando", fr: "Qui d'autre regarde", de: "Wer sonst noch hinschaut", pt: "Quem mais está a olhar", it: "Chi altro sta guardando", ja: "他に見ている人", zh: "还有谁在看", hi: "और कौन देख रहा है", ar: "من غيرك يراقب",
  },
  "att.tag": {
    en: "specialists, clinicians, and the ladder", es: "especialistas, clínicos y la escalera", fr: "spécialistes, cliniciens et l'échelle", de: "Spezialisten, Kliniker und die Leiter", pt: "especialistas, clínicos e a escada", it: "specialisti, clinici e la scala", ja: "専門家、臨床医、そしてはしご", zh: "专家、临床医生与阶梯", hi: "विशेषज्ञ, चिकित्सक और सीढ़ी", ar: "المتخصصون والأطباء والسلّم",
  },
  "att.spec": {
    en: "Specialists", es: "Especialistas", fr: "Spécialistes", de: "Spezialisten", pt: "Especialistas", it: "Specialisti", ja: "専門家", zh: "专家", hi: "विशेषज्ञ", ar: "المتخصصون",
  },
  "att.spec.local": {
    en: "Install the local set", es: "Instalar el conjunto local", fr: "Installer le jeu local", de: "Lokales Set installieren", pt: "Instalar o conjunto local", it: "Installa il set locale", ja: "ローカルセットを導入", zh: "安装本地集合", hi: "स्थानीय सेट स्थापित करें", ar: "تثبيت المجموعة المحلية",
  },
  "att.spec.hosted": {
    en: "Install the QRME-hosted set", es: "Instalar el conjunto alojado en QRME", fr: "Installer le jeu hébergé par QRME", de: "Das QRME-gehostete Set installieren", pt: "Instalar o conjunto alojado no QRME", it: "Installa il set ospitato su QRME", ja: "QRMEホストのセットを導入", zh: "安装QRME托管集合", hi: "QRME-होस्टेड सेट स्थापित करें", ar: "تثبيت مجموعة QRME المستضافة",
  },
  "att.spec.none": {
    en: "None installed. Without one, handing a thing over answers no tandem specialist and does nothing — a refusal, not a silent drop.", es: "Ninguno instalado. Sin uno, entregar algo responde no hay especialista en tándem y no hace nada — un rechazo, no una omisión silenciosa.", fr: "Aucun installé. Sans, confier une chose répond aucun spécialiste en tandem et ne fait rien — un refus, pas un abandon silencieux.", de: "Keiner installiert. Ohne einen antwortet die Übergabe kein Tandem-Spezialist und tut nichts — eine Ablehnung, kein stilles Verschlucken.", pt: "Nenhum instalado. Sem um, entregar algo responde nenhum especialista em tandem e não faz nada — uma recusa, não uma queda silenciosa.", it: "Nessuno installato. Senza, consegnare qualcosa risponde nessuno specialista in tandem e non fa nulla — un rifiuto, non una caduta silenziosa.", ja: "未導入です。ないまま引き渡すと「タンデム専門家なし」と答えて何もしません — 静かな握りつぶしではなく拒否です。", zh: "尚未安装。没有它，移交会回答「无协作专家」且什么也不做 — 是拒绝，而非静默丢弃。", hi: "कोई स्थापित नहीं। इसके बिना, सौंपने पर जवाब मिलता है कोई टैंडम विशेषज्ञ नहीं और कुछ नहीं होता — इनकार, चुपचाप गिराना नहीं।", ar: "لا شيء مثبت. بدونه، يجيب التسليم لا متخصص مرافق ولا يفعل شيئًا — رفض لا إسقاط صامت.",
  },
  "att.hand": {
    en: "Hand something over", es: "Entregar algo", fr: "Confier quelque chose", de: "Etwas übergeben", pt: "Entregar algo", it: "Consegna qualcosa", ja: "何かを引き渡す", zh: "移交事项", hi: "कुछ सौंपें", ar: "سلّم شيئًا",
  },
  "att.hand.ph": {
    en: "Get through the week", es: "Superar la semana", fr: "Tenir la semaine", de: "Die Woche überstehen", pt: "Aguentar a semana", it: "Superare la settimana", ja: "今週を乗り切る", zh: "撑过这一周", hi: "यह हफ़्ता पार करें", ar: "اجتياز الأسبوع",
  },
  "att.hand.go": {
    en: "Hand it over", es: "Entregarlo", fr: "Le confier", de: "Übergeben", pt: "Entregar", it: "Consegnalo", ja: "引き渡す", zh: "移交", hi: "सौंप दें", ar: "سلّمه",
  },
  "att.hand.who": {
    en: "Who could see me for this?", es: "¿Quién podría atenderme por esto?", fr: "Qui pourrait me recevoir pour ça ?", de: "Wer könnte mich damit sehen?", pt: "Quem me poderia ver por isto?", it: "Chi potrebbe vedermi per questo?", ja: "これで診てくれるのは誰？", zh: "这事谁能接诊我？", hi: "इसके लिए मुझे कौन देख सकता है?", ar: "من يمكنه استقبالي لهذا؟",
  },
  "att.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "att.advance": {
    en: "Advance", es: "Avanzar", fr: "Avancer", de: "Weiter", pt: "Avançar", it: "Avanza", ja: "進める", zh: "推进", hi: "आगे बढ़ाएँ", ar: "تقدّم",
  },
  "att.ref": {
    en: "Referrals", es: "Derivaciones", fr: "Orientations", de: "Überweisungen", pt: "Encaminhamentos", it: "Referti", ja: "紹介", zh: "转诊", hi: "रेफ़रल", ar: "الإحالات",
  },
  "att.ref.prep": {
    en: "Prepare one for {c}", es: "Preparar una para {c}", fr: "En préparer une pour {c}", de: "Eine für {c} vorbereiten", pt: "Preparar um para {c}", it: "Preparane uno per {c}", ja: "{c}向けに準備", zh: "为{c}准备一份", hi: "{c} के लिए तैयार करें", ar: "حضّر واحدة لـ {c}",
  },
  "att.ref.none": {
    en: "No referral has been prepared.", es: "No se ha preparado ninguna derivación.", fr: "Aucune orientation n'a été préparée.", de: "Keine Überweisung vorbereitet.", pt: "Nenhum encaminhamento preparado.", it: "Nessun referto preparato.", ja: "紹介状は準備されていません。", zh: "尚未准备任何转诊。", hi: "कोई रेफ़रल तैयार नहीं हुआ।", ar: "لم تُحضَّر أي إحالة.",
  },
  "att.ref.released": {
    en: "Mark released", es: "Marcar entregada", fr: "Marquer transmise", de: "Als freigegeben markieren", pt: "Marcar como entregue", it: "Segna rilasciato", ja: "送付済みにする", zh: "标记已交付", hi: "जारी चिह्नित करें", ar: "وضع علامة مُسلَّمة",
  },
  "att.ladder": {
    en: "The ladder", es: "La escalera", fr: "L'échelle", de: "Die Leiter", pt: "A escada", it: "La scala", ja: "はしご", zh: "阶梯", hi: "सीढ़ी", ar: "السلّم",
  },
  "att.ladder.sens": {
    en: "Sensitivity", es: "Sensibilidad", fr: "Sensibilité", de: "Empfindlichkeit", pt: "Sensibilidade", it: "Sensibilità", ja: "感度", zh: "灵敏度", hi: "संवेदनशीलता", ar: "الحساسية",
  },
  "att.ladder.floors": {
    en: "Floors — {list}", es: "Suelos — {list}", fr: "Planchers — {list}", de: "Böden — {list}", pt: "Pisos — {list}", it: "Piani — {list}", ja: "下限 — {list}", zh: "下限 — {list}", hi: "न्यूनतम — {list}", ar: "الحدود الدنيا — {list}",
  },
  "att.ladder.ceiling": {
    en: "Ceiling — {v}", es: "Techo — {v}", fr: "Plafond — {v}", de: "Decke — {v}", pt: "Teto — {v}", it: "Soffitto — {v}", ja: "上限 — {v}", zh: "上限 — {v}", hi: "अधिकतम — {v}", ar: "السقف — {v}",
  },
  "att.relay": {
    en: "The relay", es: "El relevo", fr: "Le relais", de: "Die Staffel", pt: "O revezamento", it: "La staffetta", ja: "リレー", zh: "接力", hi: "रिले", ar: "التتابع",
  },
  "att.relay.channel": {
    en: "Channel", es: "Canal", fr: "Canal", de: "Kanal", pt: "Canal", it: "Canale", ja: "チャンネル", zh: "通道", hi: "चैनल", ar: "القناة",
  },
  "att.relay.roster": {
    en: "Roster: {list} · ceiling {c}", es: "Turnos: {list} · techo {c}", fr: "Effectif : {list} · plafond {c}", de: "Dienstplan: {list} · Decke {c}", pt: "Escala: {list} · teto {c}", it: "Turni: {list} · soffitto {c}", ja: "当番: {list} · 上限 {c}", zh: "名册：{list} · 上限{c}", hi: "रोस्टर: {list} · अधिकतम {c}", ar: "القائمة: {list} · السقف {c}",
  },
  "att.sit": {
    en: "This sitting", es: "Esta sesión", fr: "Cette séance", de: "Diese Sitzung", pt: "Esta sessão", it: "Questa seduta", ja: "今回の対話", zh: "本次会谈", hi: "यह बैठक", ar: "هذه الجلسة",
  },
  "att.sit.start": {
    en: "Start a session", es: "Iniciar una sesión", fr: "Démarrer une séance", de: "Sitzung starten", pt: "Iniciar uma sessão", it: "Avvia una seduta", ja: "セッションを開始", zh: "开始会谈", hi: "सत्र शुरू करें", ar: "بدء جلسة",
  },
  "att.sit.end": {
    en: "End it", es: "Terminarla", fr: "La terminer", de: "Beenden", pt: "Terminar", it: "Terminala", ja: "終了する", zh: "结束", hi: "समाप्त करें", ar: "إنهاؤها",
  },
  "att.sit.prior": {
    en: "{id} · {n} sittings before this one", es: "{id} · {n} sesiones antes de esta", fr: "{id} · {n} séances avant celle-ci", de: "{id} · {n} Sitzungen vor dieser", pt: "{id} · {n} sessões antes desta", it: "{id} · {n} sedute prima di questa", ja: "{id} · これまでの対話{n}回", zh: "{id} · 此前{n}次会谈", hi: "{id} · इससे पहले {n} बैठकें", ar: "{id} · {n} جلسات قبل هذه",
  },
  "att.alarm": {
    en: "An alarm, and the way out", es: "Una alarma, y la salida", fr: "Une alarme, et la sortie", de: "Ein Alarm, und der Ausweg", pt: "Um alarme, e a saída", it: "Un allarme, e la via d'uscita", ja: "警報と、その出口", zh: "警报与出路", hi: "एक अलार्म, और निकास", ar: "إنذار، وطريق الخروج",
  },
  "att.alarm.id.ph": {
    en: "alarm id", es: "id de la alarma", fr: "id de l'alarme", de: "Alarm-Id", pt: "id do alarme", it: "id dell'allarme", ja: "警報ID", zh: "警报ID", hi: "अलार्म आईडी", ar: "معرّف الإنذار",
  },
  "att.alarm.q.ph": {
    en: "What should I do right now?", es: "¿Qué debo hacer ahora mismo?", fr: "Que dois-je faire maintenant ?", de: "Was soll ich jetzt tun?", pt: "O que devo fazer agora?", it: "Cosa devo fare adesso?", ja: "今すぐ何をすべき？", zh: "我现在该怎么做？", hi: "मुझे अभी क्या करना चाहिए?", ar: "ماذا أفعل الآن؟",
  },
  "att.alarm.ask": {
    en: "Ask", es: "Preguntar", fr: "Demander", de: "Fragen", pt: "Perguntar", it: "Chiedi", ja: "たずねる", zh: "询问", hi: "पूछें", ar: "اسأل",
  },
  "att.alarm.what.ph": {
    en: "What is happening", es: "Qué está pasando", fr: "Que se passe-t-il", de: "Was gerade passiert", pt: "O que está a acontecer", it: "Cosa sta succedendo", ja: "何が起きているか", zh: "正在发生什么", hi: "क्या हो रहा है", ar: "ما الذي يحدث",
  },
  "att.alarm.raise": {
    en: "Raise an emergency", es: "Activar una emergencia", fr: "Déclencher une urgence", de: "Notfall auslösen", pt: "Acionar uma emergência", it: "Attiva un'emergenza", ja: "緊急事態を発報", zh: "发起紧急求助", hi: "आपातकाल उठाएँ", ar: "إطلاق حالة طوارئ",
  },
  "att.alarm.rule": {
    en: "This is the door that reaches emergency services, and it takes your own credential. The uncredentialed one is a scanned care code — a bystander at your front door can wake the people watching over you, and stops there. Only you can send an ambulance to yourself.", es: "Esta es la puerta que llega a los servicios de emergencia, y requiere tu propia credencial. La puerta sin credencial es un código de cuidado escaneado — un transeúnte en tu puerta puede despertar a quienes te cuidan, y ahí se detiene. Solo tú puedes enviarte una ambulancia.", fr: "C'est la porte qui atteint les services d'urgence, et elle exige votre propre référence. Celle sans référence est un code de soin scanné — un passant à votre porte peut réveiller ceux qui veillent sur vous, et s'arrête là. Vous seul pouvez vous envoyer une ambulance.", de: "Dies ist die Tür zu den Rettungsdiensten, und sie verlangt deine eigenen Zugangsdaten. Die ohne ist ein gescannter Pflegecode — ein Passant an deiner Haustür kann die Menschen wecken, die über dich wachen, und dort endet es. Nur du kannst dir selbst einen Krankenwagen schicken.", pt: "Esta é a porta que chega aos serviços de emergência, e exige a sua própria credencial. A porta sem credencial é um código de cuidado lido — um transeunte à sua porta pode acordar quem vela por si, e fica por aí. Só você pode enviar uma ambulância a si próprio.", it: "Questa è la porta che raggiunge i servizi di emergenza, e richiede la tua credenziale. Quella senza è un codice di cura scansionato — un passante alla tua porta può svegliare chi veglia su di te, e si ferma lì. Solo tu puoi mandarti un'ambulanza.", ja: "これは救急サービスに届く扉で、あなた自身の資格情報が必要です。資格情報なしの扉はスキャンされたケアコードで、玄関先の通行人はあなたを見守る人々を起こせますが、そこまでです。自分に救急車を呼べるのはあなただけです。", zh: "这是通往急救服务的门，需要你本人的凭证。无凭证的那扇门是被扫描的护理码 — 你门前的路人可以唤醒守护你的人，仅止于此。只有你能为自己叫救护车。", hi: "यही वह द्वार है जो आपातकालीन सेवाओं तक पहुँचता है, और इसे आपकी अपनी क्रेडेंशियल चाहिए। बिना क्रेडेंशियल वाला द्वार स्कैन किया केयर कोड है — आपके दरवाज़े पर खड़ा राहगीर आपकी देखरेख करने वालों को जगा सकता है, बस वहीं तक। एम्बुलेंस केवल आप ही अपने लिए भेज सकते हैं।", ar: "هذا هو الباب الذي يصل إلى خدمات الطوارئ، ويتطلب اعتمادك الشخصي. الباب بلا اعتماد هو رمز رعاية ممسوح — عابر عند بابك يمكنه إيقاظ من يسهرون عليك، ويقف عند ذلك. وحدك من يستطيع إرسال إسعاف لنفسك.",
  },
  "att.med": {
    en: "Medical ID", es: "Identificación médica", fr: "Fiche médicale", de: "Notfallpass", pt: "Identificação médica", it: "Scheda medica", ja: "メディカル ID", zh: "医疗卡", hi: "मेडिकल आईडी", ar: "البطاقة الطبية",
  },
  "att.med.make": {
    en: "Make a code", es: "Crear un código", fr: "Créer un code", de: "Code erstellen", pt: "Criar um código", it: "Crea un codice", ja: "コードを作る", zh: "生成代码", hi: "कोड बनाएँ", ar: "إنشاء رمز",
  },
  "att.med.see": {
    en: "See what a stranger sees", es: "Ver lo que ve un desconocido", fr: "Voir ce qu'un inconnu voit", de: "Sehen, was ein Fremder sieht", pt: "Ver o que um estranho vê", it: "Vedi ciò che vede un estraneo", ja: "他人に見えるものを確認", zh: "查看陌生人所见", hi: "देखें अजनबी को क्या दिखता है", ar: "شاهد ما يراه الغريب",
  },
  "att.med.revoke": {
    en: "Revoke", es: "Revocar", fr: "Révoquer", de: "Widerrufen", pt: "Revogar", it: "Revoca", ja: "失効させる", zh: "撤销", hi: "रद्द करें", ar: "إلغاء",
  },
  "att.med.at": {
    en: "{view} · the printable code is at {qr}", es: "{view} · el código imprimible está en {qr}", fr: "{view} · le code imprimable est à {qr}", de: "{view} · der druckbare Code liegt unter {qr}", pt: "{view} · o código imprimível está em {qr}", it: "{view} · il codice stampabile è su {qr}", ja: "{view} · 印刷用コードは{qr}にあります", zh: "{view} · 可打印代码位于{qr}", hi: "{view} · प्रिंट योग्य कोड {qr} पर है", ar: "{view} · الرمز القابل للطباعة في {qr}",
  },
  "bas.band.yours": {
    en: " (yours)", es: " (tuyo)", fr: " (le vôtre)", de: " (deins)", pt: " (seu)", it: " (tuo)", ja: "（あなたのもの）", zh: "（你的）", hi: " (आपका)", ar: " (خاصتك)",
  },
  "bas.sens.title": {
    en: "How readily the Guardian speaks up",
    es: "Con qué prontitud habla el Guardián",
    fr: "Avec quelle promptitude le Gardien se manifeste",
    de: "Wie schnell sich der Wächter meldet",
    pt: "Com que prontidão o Guardião se manifesta",
    it: "Con quanta prontezza interviene il Guardiano",
    ja: "ガーディアンが声を上げる早さ",
    zh: "守护者发声的敏捷程度",
    hi: "अभिभावक कितनी जल्दी बोलता है",
    ar: "مدى سرعة تنبيه الحارس",
  },
  "bas.sens.lead": {
    en: "One dial for the whole product: it shifts the alarm thresholds and widens or narrows every band below.",
    es: "Un solo mando para todo el producto: desplaza los umbrales de alarma y ensancha o estrecha cada banda de abajo.",
    fr: "Un seul réglage pour tout le produit : il déplace les seuils d'alarme et élargit ou resserre chaque bande ci-dessous.",
    de: "Ein Regler für das ganze Produkt: Er verschiebt die Alarmschwellen und weitet oder verengt jedes Band unten.",
    pt: "Um único botão para todo o produto: desloca os limiares de alarme e alarga ou estreita cada banda abaixo.",
    it: "Una sola manopola per tutto il prodotto: sposta le soglie di allarme e allarga o restringe ogni banda qui sotto.",
    ja: "製品全体でひとつのダイヤル：アラームのしきい値を動かし、下の各バンドを広げたり狭めたりします。",
    zh: "整个产品只有一个旋钮：它会移动警报阈值，并加宽或收窄下方的每条区间。",
    hi: "पूरे उत्पाद के लिए एक ही डायल: यह अलार्म सीमाएँ खिसकाता है और नीचे की हर पट्टी को चौड़ा या संकरा करता है।",
    ar: "قرص واحد للمنتج كله: يحرّك عتبات الإنذار ويوسّع أو يضيّق كل نطاق أدناه.",
  },
  "bas.money.title": {
    en: "Your money limits",
    es: "Tus límites de dinero",
    fr: "Vos limites d'argent",
    de: "Deine Geldgrenzen",
    pt: "Os seus limites de dinheiro",
    it: "I tuoi limiti di denaro",
    ja: "お金のリミット",
    zh: "你的资金限额",
    hi: "आपकी धन सीमाएँ",
    ar: "حدودك المالية",
  },
  "bas.money.lead": {
    en: "Where the money guardian draws its lines. It can warn and suggest — it never moves funds on its own.",
    es: "Dónde traza sus líneas el guardián del dinero. Puede avisar y sugerir — nunca mueve fondos por su cuenta.",
    fr: "Là où le gardien de l'argent trace ses lignes. Il peut avertir et suggérer — il ne déplace jamais de fonds de lui-même.",
    de: "Wo der Geld-Wächter seine Linien zieht. Er kann warnen und vorschlagen — Geld bewegt er nie von selbst.",
    pt: "Onde o guardião do dinheiro traça as suas linhas. Pode avisar e sugerir — nunca move fundos por conta própria.",
    it: "Dove il guardiano del denaro traccia le sue linee. Può avvisare e suggerire — non sposta mai fondi da solo.",
    ja: "マネーガーディアンが線を引く場所。警告と提案はしますが、自分で資金を動かすことはありません。",
    zh: "资金守护者划线的地方。它会提醒和建议 — 绝不会自行动用资金。",
    hi: "जहाँ धन अभिभावक अपनी रेखाएँ खींचता है। यह चेता सकता है और सुझा सकता है — अपने आप कभी धन नहीं हिलाता।",
    ar: "حيث يرسم حارس المال خطوطه. يمكنه التحذير والاقتراح — ولا يحرّك الأموال من تلقاء نفسه أبدًا.",
  },
  "bas.money.floor": {
    en: "Low-balance floor",
    es: "Suelo de saldo bajo",
    fr: "Plancher de solde bas",
    de: "Untergrenze für den Kontostand",
    pt: "Piso de saldo baixo",
    it: "Soglia di saldo basso",
    ja: "残高の下限ライン",
    zh: "低余额下限",
    hi: "न्यून शेष की सीमा",
    ar: "الحد الأدنى للرصيد",
  },
  "bas.money.floor.note": {
    en: "tell me when cash in checking and savings falls below this",
    es: "avísame cuando el efectivo en cuenta corriente y ahorro caiga por debajo de esto",
    fr: "prévenez-moi quand le liquide du courant et de l'épargne passe sous ce niveau",
    de: "sag mir, wenn das Guthaben auf Giro- und Sparkonto darunter fällt",
    pt: "avisa-me quando o dinheiro à ordem e nas poupanças cair abaixo disto",
    it: "avvisami quando la liquidità su conto e risparmi scende sotto questa cifra",
    ja: "普通・貯蓄口座の残高がこれを下回ったら知らせて",
    zh: "当活期和储蓄账户的现金低于此数时提醒我",
    hi: "जब चालू और बचत खातों की नकदी इससे नीचे जाए तो मुझे बताएँ",
    ar: "أخبرني عندما ينخفض النقد في الحسابين الجاري والتوفير عن هذا الحد",
  },
  "bas.money.goal": {
    en: "Savings goal",
    es: "Meta de ahorro",
    fr: "Objectif d'épargne",
    de: "Sparziel",
    pt: "Meta de poupança",
    it: "Obiettivo di risparmio",
    ja: "貯蓄目標",
    zh: "储蓄目标",
    hi: "बचत लक्ष्य",
    ar: "هدف الادخار",
  },
  "bas.money.goal.note": {
    en: "celebrated once when your savings first reach it",
    es: "se celebra una vez cuando tus ahorros lo alcanzan por primera vez",
    fr: "célébré une fois quand votre épargne l'atteint pour la première fois",
    de: "einmal gefeiert, wenn dein Erspartes es zum ersten Mal erreicht",
    pt: "celebrado uma vez quando as suas poupanças o alcançam pela primeira vez",
    it: "festeggiato una volta quando i tuoi risparmi lo raggiungono per la prima volta",
    ja: "貯蓄が初めて到達したとき一度だけお祝いします",
    zh: "当储蓄首次达到时庆祝一次",
    hi: "जब आपकी बचत पहली बार इस तक पहुँचे तो एक बार जश्न",
    ar: "يُحتفى به مرة واحدة عندما تبلغه مدخراتك أول مرة",
  },
  "bas.money.caps": {
    en: "Standing-order caps",
    es: "Topes del mandato",
    fr: "Plafonds du mandat",
    de: "Obergrenzen des Mandats",
    pt: "Tetos do mandato",
    it: "Massimali del mandato",
    ja: "自動投資の上限",
    zh: "授权上限",
    hi: "अधिदेश की ऊपरी सीमाएँ",
    ar: "سقوف التفويض",
  },
  "bas.money.caps.none": {
    en: "No mandate is written — hand one over in Settings and its caps appear here.",
    es: "No hay mandato escrito — otórgalo en Ajustes y sus topes aparecerán aquí.",
    fr: "Aucun mandat n'est rédigé — accordez-en un dans Réglages et ses plafonds apparaîtront ici.",
    de: "Kein Mandat erteilt — vergib eines in den Einstellungen und seine Grenzen erscheinen hier.",
    pt: "Nenhum mandato foi escrito — conceda um nas Definições e os seus tetos aparecem aqui.",
    it: "Nessun mandato è stato scritto — concedine uno nelle Impostazioni e i suoi massimali appariranno qui.",
    ja: "委任はまだありません — 設定で委任すると、その上限がここに表示されます。",
    zh: "尚未写下授权 — 在设置中授予后，其上限会显示在这里。",
    hi: "कोई अधिदेश नहीं लिखा गया — सेटिंग्स में सौंपें और उसकी सीमाएँ यहाँ दिखेंगी।",
    ar: "لا يوجد تفويض مكتوب — امنح واحدًا في الإعدادات وستظهر سقوفه هنا.",
  },
  "bas.money.cap.order": {
    en: "per order",
    es: "por orden",
    fr: "par ordre",
    de: "pro Order",
    pt: "por ordem",
    it: "per ordine",
    ja: "1回あたり",
    zh: "每笔",
    hi: "प्रति आदेश",
    ar: "لكل أمر",
  },
  "bas.money.cap.month": {
    en: "per month",
    es: "por mes",
    fr: "par mois",
    de: "pro Monat",
    pt: "por mês",
    it: "al mese",
    ja: "月あたり",
    zh: "每月",
    hi: "प्रति माह",
    ar: "في الشهر",
  },
  "bas.learning": {
    en: "learning — wear the watch and sleep in it", es: "aprendiendo — lleva el reloj y duerme con él", fr: "en apprentissage — portez la montre et dormez avec", de: "lernt — trag die Uhr und schlaf damit", pt: "a aprender — use o relógio e durma com ele", it: "sta imparando — indossa l'orologio e dormici", ja: "学習中 — 時計を着けたまま眠ってください", zh: "学习中 — 请佩戴手表并戴着睡觉", hi: "सीख रहा है — घड़ी पहनें और उसी में सोएँ", ar: "قيد التعلّم — ارتدِ الساعة ونم بها",
  },
  "bas.watch.arm": {
    en: "Arm the crash watch", es: "Activar la vigilancia de caídas", fr: "Armer la veille d'accident", de: "Sturzwache scharfschalten", pt: "Armar a vigilância de queda", it: "Attiva la sorveglianza incidenti", ja: "クラッシュウォッチを作動させる", zh: "启用跌倒守护", hi: "क्रैश वॉच सक्रिय करें", ar: "فعّل مراقبة الحوادث",
  },
  "bas.watch.update": {
    en: "Update the crash watch", es: "Actualizar la vigilancia de caídas", fr: "Mettre à jour la veille de chute", de: "Sturzwache aktualisieren", pt: "Atualizar a vigilância de queda", it: "Aggiorna la vigilanza di caduta", ja: "クラッシュ監視を更新する", zh: "更新倒地守望", hi: "क्रैश वॉच अपडेट करें", ar: "حدّث مراقبة الانهيار",
  },
  "bas.title": {
    en: "Your baseline", es: "Tu línea base", fr: "Votre ligne de base", de: "Deine Basislinie", pt: "A sua linha de base", it: "La tua linea di base", ja: "あなたのベースライン", zh: "你的基线", hi: "आपकी आधार रेखा", ar: "خطك الأساسي",
  },
  "bas.what": {
    en: "What this is", es: "Qué es esto", fr: "Ce que c'est", de: "Was das ist", pt: "O que é isto", it: "Che cos'è", ja: "これは何か", zh: "这是什么", hi: "यह क्या है", ar: "ما هذا",
  },
  "bas.what.p1": {
    en: "Every resting reading nudges your own average for each metric. Once a metric has enough of them, a band is drawn around it — and when a reading lands outside that band, in either direction, your Guardian checks in and asks how you are. A drift check-in on its own never calls anybody — but the crash watch below is exactly the \"call somebody\" you can program: if a reading turns critical and you stop answering, help gets sent.", es: "Cada lectura en reposo ajusta tu propio promedio de cada métrica. Cuando una métrica tiene suficientes, se dibuja una banda a su alrededor — y cuando una lectura cae fuera de esa banda, en cualquier dirección, tu Guardián te consulta y pregunta cómo estás. Una consulta por deriva por sí sola nunca llama a nadie — pero la vigilancia de colapso de abajo es exactamente el «llamar a alguien» que puedes programar: si una lectura se vuelve crítica y dejas de responder, se envía ayuda.", fr: "Chaque mesure au repos ajuste votre propre moyenne pour chaque métrique. Quand une métrique en a assez, une bande est tracée autour — et quand une mesure tombe hors de cette bande, dans un sens ou dans l'autre, votre Gardien prend de vos nouvelles. Un contrôle de dérive seul n'appelle jamais personne — mais la veille d'effondrement ci-dessous est exactement le « appeler quelqu'un » que vous pouvez programmer : si une mesure devient critique et que vous ne répondez plus, de l'aide est envoyée.", de: "Jede Ruhemessung verschiebt deinen eigenen Durchschnitt je Metrik. Hat eine Metrik genug davon, wird ein Band darum gezogen — und landet eine Messung außerhalb dieses Bandes, in beliebiger Richtung, meldet sich dein Guardian und fragt, wie es dir geht. Eine Drift-Nachfrage allein ruft nie jemanden — aber die Absturzwache darunter ist genau das programmierbare »jemanden rufen«: wird eine Messung kritisch und du antwortest nicht mehr, wird Hilfe geschickt.", pt: "Cada leitura em repouso ajusta a sua própria média de cada métrica. Quando uma métrica tem leituras suficientes, desenha-se uma banda à sua volta — e quando uma leitura cai fora dessa banda, em qualquer direção, o seu Guardião pergunta como está. Uma verificação de deriva por si só nunca chama ninguém — mas a vigília de colapso abaixo é exatamente o «chamar alguém» que pode programar: se uma leitura fica crítica e deixa de responder, envia-se ajuda.", it: "Ogni lettura a riposo aggiusta la tua media per ciascuna metrica. Quando una metrica ne ha abbastanza, le si disegna intorno una banda — e quando una lettura cade fuori da quella banda, in entrambe le direzioni, il tuo Guardian si fa vivo e ti chiede come stai. Un controllo di deriva da solo non chiama mai nessuno — ma la veglia anti-collasso qui sotto è esattamente il «chiama qualcuno» che puoi programmare: se una lettura diventa critica e smetti di rispondere, i soccorsi partono.", ja: "安静時の測定はそのたびに各指標のあなた自身の平均を少しずつ更新します。十分な数が集まると帯が引かれ、測定値がその帯の外にどちらの方向でも出ると、ガーディアンが様子を尋ねます。ドリフト確認だけでは誰にも連絡しません — しかし下のクラッシュウォッチこそが、あなたが設定できる「誰かを呼ぶ」です：測定値が危険域に入り応答が途絶えると、助けが送られます。", zh: "每次静息读数都会微调你各项指标的自身平均值。某项指标积累足够后，会围绕它画出一条带 — 当读数落在带外，无论哪个方向，你的守护者都会来问你怎么样。漂移问询本身绝不会呼叫任何人 — 而下方的骤变守护正是你可以设定的「呼叫某人」：读数转为危急且你不再应答时，就会派出援助。", hi: "हर विश्राम रीडिंग आपके हर मीट्रिक का अपना औसत थोड़ा समायोजित करती है। पर्याप्त रीडिंग होने पर उसके चारों ओर एक बैंड खिंच जाता है — और जब कोई रीडिंग उस बैंड से बाहर, किसी भी दिशा में, गिरती है तो आपका गार्जियन हालचाल पूछता है। ड्रिफ़्ट पूछताछ अपने आप कभी किसी को नहीं बुलाती — पर नीचे की क्रैश निगरानी ही वह «किसी को बुलाओ» है जिसे आप प्रोग्राम कर सकते हैं: रीडिंग गंभीर हो और आप जवाब देना बंद कर दें, तो मदद भेजी जाती है।", ar: "كل قراءة راحة تعدّل متوسطك الخاص لكل مقياس. ومتى توفر ما يكفي منها يُرسم نطاق حوله — وإذا وقعت قراءة خارج ذلك النطاق، في أي اتجاه، يطمئن عليك الحارس ويسألك كيف حالك. فحص الانحراف وحده لا يستدعي أحدًا أبدًا — لكن مراقبة الانهيار أدناه هي بالضبط «استدعِ أحدًا» التي يمكنك برمجتها: إذا صارت قراءة حرجة وتوقفت عن الرد، تُرسل النجدة.",
  },
  "bas.what.p2": {
    en: "The widths below are yours to set. Narrow one to be told sooner; widen it if a metric of yours naturally wanders.", es: "Los anchos de abajo los fijas tú. Estrecha uno para enterarte antes; ensánchalo si una métrica tuya vaga por naturaleza.", fr: "Les largeurs ci-dessous sont à vous. Resserrez-en une pour être prévenu plus tôt ; élargissez-la si une de vos métriques vagabonde naturellement.", de: "Die Breiten darunter bestimmst du. Vereng eine, um früher Bescheid zu bekommen; weite sie, wenn eine deiner Metriken von Natur aus wandert.", pt: "As larguras abaixo são suas. Estreite uma para saber mais cedo; alargue-a se uma métrica sua vagueia por natureza.", it: "Le larghezze qui sotto le decidi tu. Restringine una per saperlo prima; allargala se una tua metrica vaga per natura.", ja: "下の幅はあなたが決めます。早く知りたければ狭く、生まれつき揺れやすい指標なら広く。", zh: "下面的宽度由你设定。调窄可更早得知；某项指标天生爱漂移就调宽。", hi: "नीचे की चौड़ाइयाँ आप तय करते हैं। जल्दी जानने के लिए संकरी करें; अगर आपका कोई मीट्रिक स्वभावतः भटकता है तो चौड़ी करें।", ar: "العروض أدناه أنت من يحددها. ضيّق نطاقًا لتُخبَر أبكر؛ ووسّعه إن كان أحد مقاييسك يتجول بطبيعته.",
  },
  "bas.ask.title": {
    en: "JIM is asking: are you okay?", es: "JIM pregunta: ¿estás bien?", fr: "JIM demande : est-ce que ça va ?", de: "JIM fragt: Geht es dir gut?", pt: "O JIM pergunta: está bem?", it: "JIM chiede: stai bene?", ja: "JIM が確認しています：大丈夫ですか？", zh: "JIM 在询问：你还好吗？", hi: "JIM पूछ रहा है: क्या आप ठीक हैं?", ar: "يسأل JIM: هل أنت بخير؟",
  },
  "bas.ask.body": {
    en: "A concerning reading came in ({concern}). This is attempt {attempt} of {attempts} — after that, your crash watch contacts {name}{ems}.", es: "Llegó una lectura preocupante ({concern}). Este es el intento {attempt} de {attempts} — después, tu vigilancia de colapso contacta a {name}{ems}.", fr: "Une mesure préoccupante est arrivée ({concern}). Ceci est la tentative {attempt} sur {attempts} — ensuite, votre veille d'effondrement contacte {name}{ems}.", de: "Eine besorgniserregende Messung kam an ({concern}). Dies ist Versuch {attempt} von {attempts} — danach kontaktiert deine Absturzwache {name}{ems}.", pt: "Chegou uma leitura preocupante ({concern}). Esta é a tentativa {attempt} de {attempts} — depois disso, a sua vigília de colapso contacta {name}{ems}.", it: "È arrivata una lettura preoccupante ({concern}). Questo è il tentativo {attempt} di {attempts} — dopo, la tua veglia anti-collasso contatta {name}{ems}.", ja: "懸念される測定値が届きました（{concern}）。これは{attempts}回中{attempt}回目の呼びかけです — その後、クラッシュウォッチが{name}に連絡します{ems}。", zh: "收到一条令人担忧的读数（{concern}）。这是第{attempt}次尝试，共{attempts}次 — 之后，骤变守护将联系{name}{ems}。", hi: "एक चिंताजनक रीडिंग आई ({concern})। यह {attempts} में से {attempt}वाँ प्रयास है — उसके बाद आपकी क्रैश निगरानी {name} से संपर्क करेगी{ems}।", ar: "وصلت قراءة مقلقة ({concern}). هذه المحاولة {attempt} من {attempts} — بعدها تتصل مراقبة الانهيار بـ{name}{ems}.",
  },
  "bas.ask.ok": {
    en: "I'm okay", es: "Estoy bien", fr: "Ça va", de: "Mir geht es gut", pt: "Estou bem", it: "Sto bene", ja: "大丈夫です", zh: "我没事", hi: "मैं ठीक हूँ", ar: "أنا بخير",
  },
  "bas.trip": {
    en: "⚠ The crash watch tripped: {name} was contacted{ems}. Any normal reading — or the button above — stands it down.", es: "⚠ La vigilancia de colapso saltó: se contactó a {name}{ems}. Cualquier lectura normal — o el botón de arriba — la desactiva.", fr: "⚠ La veille d'effondrement s'est déclenchée : {name} a été contacté{ems}. Toute mesure normale — ou le bouton ci-dessus — la lève.", de: "⚠ Die Absturzwache hat ausgelöst: {name} wurde kontaktiert{ems}. Jede normale Messung — oder der Knopf oben — stellt sie zurück.", pt: "⚠ A vigília de colapso disparou: {name} foi contactado{ems}. Qualquer leitura normal — ou o botão acima — desativa-a.", it: "⚠ La veglia anti-collasso è scattata: {name} è stato contattato{ems}. Qualsiasi lettura normale — o il pulsante sopra — la rientra.", ja: "⚠ クラッシュウォッチが作動しました：{name}に連絡しました{ems}。正常な測定値 — または上のボタン — で解除されます。", zh: "⚠ 骤变守护已触发：已联系{name}{ems}。任何正常读数 — 或上方按钮 — 都会将其解除。", hi: "⚠ क्रैश निगरानी सक्रिय हुई: {name} से संपर्क किया गया{ems}। कोई भी सामान्य रीडिंग — या ऊपर का बटन — इसे शांत कर देती है।", ar: "⚠ انطلقت مراقبة الانهيار: تم الاتصال بـ{name}{ems}. أي قراءة طبيعية — أو الزر أعلاه — تُعيدها إلى وضعها.",
  },
  "bas.cw.title": {
    en: "Crash watch — if you stop answering, help gets sent", es: "Vigilancia de colapso — si dejas de responder, se envía ayuda", fr: "Veille d'effondrement — si vous ne répondez plus, de l'aide est envoyée", de: "Absturzwache — wenn du nicht mehr antwortest, wird Hilfe geschickt", pt: "Vigília de colapso — se deixar de responder, envia-se ajuda", it: "Veglia anti-collasso — se smetti di rispondere, i soccorsi partono", ja: "クラッシュウォッチ — 応答が途絶えると助けが送られます", zh: "骤变守护 — 你不再应答时会派出援助", hi: "क्रैश निगरानी — जवाब देना बंद करें तो मदद भेजी जाती है", ar: "مراقبة الانهيار — إذا توقفت عن الرد تُرسل النجدة",
  },
  "bas.cw.lead": {
    en: "Off by default, programmed by you: when a reading turns critical — a fall the watch felt, a collapsing pulse, oxygen falling — JIM asks \"are you okay?\" — and if {n} attempts over {m} minutes all go unanswered, it contacts your trusted person{ems}. Any sign of you — the button, a normal reading — calls it off. Drift check-ins stay calm and never trigger this.", es: "Desactivada por defecto y programada por ti: cuando una lectura se vuelve crítica — una caída que el reloj sintió, un pulso que se desploma, oxígeno bajando — JIM pregunta «¿estás bien?» — y si {n} intentos a lo largo de {m} minutos quedan sin respuesta, contacta a tu persona de confianza{ems}. Cualquier señal tuya — el botón, una lectura normal — la cancela. Las consultas por deriva son tranquilas y nunca la disparan.", fr: "Désactivée par défaut, programmée par vous : quand une mesure devient critique — une chute sentie par la montre, un pouls qui s'effondre, l'oxygène qui baisse — JIM demande « ça va ? » — et si {n} tentatives sur {m} minutes restent toutes sans réponse, elle contacte votre personne de confiance{ems}. Tout signe de vous — le bouton, une mesure normale — l'annule. Les contrôles de dérive restent calmes et ne la déclenchent jamais.", de: "Standardmäßig aus, von dir programmiert: Wird eine Messung kritisch — ein Sturz, den die Uhr spürte, ein einbrechender Puls, fallender Sauerstoff — fragt JIM »Geht es dir gut?« — und bleiben {n} Versuche über {m} Minuten alle unbeantwortet, kontaktiert sie deine Vertrauensperson{ems}. Jedes Zeichen von dir — der Knopf, eine normale Messung — bricht sie ab. Drift-Nachfragen bleiben ruhig und lösen das nie aus.", pt: "Desligada por defeito, programada por si: quando uma leitura fica crítica — uma queda que o relógio sentiu, um pulso a desabar, oxigénio a cair — o JIM pergunta «está bem?» — e se {n} tentativas ao longo de {m} minutos ficarem todas sem resposta, contacta a sua pessoa de confiança{ems}. Qualquer sinal seu — o botão, uma leitura normal — cancela-a. As verificações de deriva ficam calmas e nunca a disparam.", it: "Spenta per default, programmata da te: quando una lettura diventa critica — una caduta che l'orologio ha sentito, un polso che crolla, ossigeno in calo — JIM chiede «stai bene?» — e se {n} tentativi in {m} minuti restano tutti senza risposta, contatta la tua persona di fiducia{ems}. Qualsiasi segno di te — il pulsante, una lettura normale — la annulla. I controlli di deriva restano calmi e non la attivano mai.", ja: "初期状態ではオフで、設定するのはあなたです：測定値が危険域に入ると — 時計が感じた転倒、急落する脈拍、下がる酸素 — JIMが「大丈夫ですか？」と尋ね、{m}分間に{n}回の呼びかけがすべて無応答なら、信頼できる人に連絡します{ems}。あなたの気配 — ボタンや正常な測定値 — があれば中止します。ドリフト確認は穏やかなままで、これを作動させることはありません。", zh: "默认关闭，由你设定：当读数转为危急 — 手表感到的跌倒、骤降的脉搏、下降的血氧 — JIM会问「你还好吗？」— 若{m}分钟内{n}次尝试均无应答，就联系你的信任联系人{ems}。你的任何动静 — 按钮、一条正常读数 — 都会取消它。漂移问询保持平静，绝不会触发它。", hi: "डिफ़ॉल्ट रूप से बंद, आपके द्वारा प्रोग्राम की गई: जब कोई रीडिंग गंभीर हो — घड़ी को महसूस हुई गिरावट, गिरती नब्ज़, घटती ऑक्सीजन — JIM पूछता है «क्या आप ठीक हैं?» — और अगर {m} मिनटों में {n} प्रयास सब अनुत्तरित रहें, तो यह आपके भरोसेमंद व्यक्ति से संपर्क करती है{ems}। आपका कोई भी संकेत — बटन, एक सामान्य रीडिंग — इसे रद्द कर देता है। ड्रिफ़्ट पूछताछ शांत रहती है और इसे कभी सक्रिय नहीं करती।", ar: "معطلة افتراضيًا وأنت من يبرمجها: إذا صارت قراءة حرجة — سقطة شعرت بها الساعة، نبض ينهار، أكسجين يهبط — يسأل JIM «هل أنت بخير؟» — وإن بقيت {n} محاولات خلال {m} دقيقة كلها بلا رد، تتصل بشخصك الموثوق{ems}. أي إشارة منك — الزر أو قراءة طبيعية — تلغيها. فحوص الانحراف تبقى هادئة ولا تُطلقها أبدًا.",
  },
  "bas.cw.name": {
    en: "Trusted person", es: "Persona de confianza", fr: "Personne de confiance", de: "Vertrauensperson", pt: "Pessoa de confiança", it: "Persona di fiducia", ja: "信頼する人", zh: "信任的人", hi: "भरोसेमंद व्यक्ति", ar: "الشخص الموثوق",
  },
  "bas.cw.name.ph": {
    en: "Rosa", es: "Rosa", fr: "Rosa", de: "Rosa", pt: "Rosa", it: "Rosa", ja: "ローザ", zh: "罗莎", hi: "रोज़ा", ar: "روزا",
  },
  "bas.cw.channel": {
    en: "How to reach them (email or phone)", es: "Cómo contactarla (correo o teléfono)", fr: "Comment la joindre (e-mail ou téléphone)", de: "Wie sie erreichbar ist (E-Mail oder Telefon)", pt: "Como contactá-la (email ou telefone)", it: "Come raggiungerla (email o telefono)", ja: "連絡方法（メールまたは電話）", zh: "如何联系他们（邮箱或电话）", hi: "उन तक कैसे पहुँचें (ईमेल या फ़ोन)", ar: "كيفية الوصول إليه (بريد أو هاتف)",
  },
  "bas.cw.channel.ph": {
    en: "rosa@example.com", es: "rosa@example.com", fr: "rosa@example.com", de: "rosa@example.com", pt: "rosa@example.com", it: "rosa@example.com", ja: "rosa@example.com", zh: "rosa@example.com", hi: "rosa@example.com", ar: "rosa@example.com",
  },
  "bas.cw.attempts": {
    en: "Attempts", es: "Intentos", fr: "Tentatives", de: "Versuche", pt: "Tentativas", it: "Tentativi", ja: "回数", zh: "尝试次数", hi: "प्रयास", ar: "المحاولات",
  },
  "bas.cw.window": {
    en: "Minutes per attempt", es: "Minutos por intento", fr: "Minutes par tentative", de: "Minuten pro Versuch", pt: "Minutos por tentativa", it: "Minuti per tentativo", ja: "1回あたりの分数", zh: "每次尝试的分钟数", hi: "प्रति प्रयास मिनट", ar: "الدقائق لكل محاولة",
  },
  "bas.cw.ems": {
    en: "May request emergency services (this app relays the request to every connected system — it cannot itself place a call)", es: "Puede solicitar servicios de emergencia (esta app retransmite la solicitud a cada sistema conectado — no puede llamar por sí misma)", fr: "Peut demander les services d'urgence (cette appli relaie la demande à chaque système connecté — elle ne peut pas appeler elle-même)", de: "Darf Rettungsdienste anfordern (diese App leitet die Anforderung an jedes verbundene System weiter — selbst anrufen kann sie nicht)", pt: "Pode pedir serviços de emergência (esta app retransmite o pedido a cada sistema ligado — ela própria não pode ligar)", it: "Può richiedere i servizi di emergenza (questa app inoltra la richiesta a ogni sistema collegato — non può chiamare da sola)", ja: "救急要請を許可（このアプリは接続された各システムに要請を中継します — 自分で電話をかけることはできません）", zh: "可请求急救服务（本应用将请求转发给每个已连接的系统 — 它自己无法拨打电话）", hi: "आपातकालीन सेवाएँ माँग सकती है (यह ऐप अनुरोध हर जुड़े सिस्टम तक पहुँचाती है — खुद कॉल नहीं कर सकती)", ar: "يجوز طلب خدمات الطوارئ (يمرر هذا التطبيق الطلب إلى كل نظام متصل — ولا يستطيع الاتصال بنفسه)",
  },
  "bas.cw.disarm": {
    en: "Disarm", es: "Desactivar", fr: "Désarmer", de: "Entschärfen", pt: "Desarmar", it: "Disattiva", ja: "解除する", zh: "停用", hi: "निष्क्रिय करें", ar: "ألغِ التفعيل",
  },
  "bas.cw.armed": {
    en: "Armed — {name} will be contacted after {n} unanswered attempts.", es: "Activada — se contactará a {name} tras {n} intentos sin respuesta.", fr: "Armée — {name} sera contacté après {n} tentatives sans réponse.", de: "Scharf — {name} wird nach {n} unbeantworteten Versuchen benachrichtigt.", pt: "Armada — {name} será contactado após {n} tentativas sem resposta.", it: "Attiva — {name} verrà contattato dopo {n} tentativi senza risposta.", ja: "作動中 — 応答のない確認が {n} 回続くと {name} に連絡します。", zh: "已启用 — 在 {n} 次无人应答后将联系 {name}。", hi: "सक्रिय — {n} बार उत्तर न मिलने पर {name} से संपर्क किया जाएगा।", ar: "مُفعَّلة — سيجري الاتصال بـ {name} بعد {n} محاولات دون رد.",
  },
  "bas.metrics": {
    en: "Your metrics", es: "Tus métricas", fr: "Vos métriques", de: "Deine Metriken", pt: "As suas métricas", it: "Le tue metriche", ja: "あなたの指標", zh: "你的指标", hi: "आपके मीट्रिक", ar: "مقاييسك",
  },
  "bas.metrics.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无数据。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "bas.metrics.learning": {
    en: "learning — {n} resting reading{s} so far", es: "aprendiendo — {n} lecturas en reposo hasta ahora", fr: "apprentissage — {n} mesures au repos pour l'instant", de: "lernt — bisher {n} Ruhemessungen", pt: "a aprender — {n} leituras em repouso até agora", it: "in apprendimento — {n} letture a riposo finora", ja: "学習中 — これまでの安静時測定{n}件", zh: "学习中 — 目前{n}条静息读数", hi: "सीख रहा है — अब तक {n} विश्राम रीडिंग", ar: "قيد التعلم — {n} قراءات راحة حتى الآن",
  },
  "bas.metrics.usual": {
    en: "your usual {v}, checked in below {lo} or above {hi}", es: "tu habitual {v}, se consulta por debajo de {lo} o por encima de {hi}", fr: "votre habituel {v}, contrôle sous {lo} ou au-dessus de {hi}", de: "Dein üblicher Wert {v}, nachgefragt unter {lo} oder über {hi}", pt: "o seu habitual {v}, verificado abaixo de {lo} ou acima de {hi}", it: "il tuo solito {v}, controllo sotto {lo} o sopra {hi}", ja: "普段は{v}、{lo}未満または{hi}超で確認します", zh: "你的常态{v}，低于{lo}或高于{hi}时问询", hi: "आपका सामान्य {v}, {lo} से नीचे या {hi} से ऊपर पर पूछा जाता है", ar: "معتادك {v}، يُسأل دون {lo} أو فوق {hi}",
  },
  "bas.metrics.drop": {
    en: "tell me when it drops", es: "avísame cuando baje", fr: "prévenez-moi quand ça baisse", de: "sag mir, wenn es fällt", pt: "avisa-me quando descer", it: "dimmi quando scende", ja: "下がったら知らせて", zh: "下降时告诉我", hi: "गिरे तो बताएँ", ar: "أخبرني إذا انخفض",
  },
  "bas.metrics.climb": {
    en: "tell me when it climbs", es: "avísame cuando suba", fr: "prévenez-moi quand ça monte", de: "sag mir, wenn es steigt", pt: "avisa-me quando subir", it: "dimmi quando sale", ja: "上がったら知らせて", zh: "上升时告诉我", hi: "चढ़े तो बताएँ", ar: "أخبرني إذا ارتفع",
  },
  "bas.metrics.reset": {
    en: "Reset", es: "Restablecer", fr: "Réinitialiser", de: "Zurücksetzen", pt: "Repor", it: "Reimposta", ja: "リセット", zh: "重置", hi: "रीसेट", ar: "إعادة ضبط",
  },
  "rch.left": {
    en: "left this host", es: "salió de este host", fr: "a quitté cet hôte", de: "hat diesen Host verlassen", pt: "saiu deste host", it: "ha lasciato questo host", ja: "このホストを出ました", zh: "离开了这台主机", hi: "इस होस्ट से बाहर गया", ar: "غادر هذا المضيف",
  },
  "rch.stayed": {
    en: "stayed here", es: "se quedó aquí", fr: "est resté ici", de: "ist hiergeblieben", pt: "ficou aqui", it: "è rimasto qui", ja: "ここに留まりました", zh: "留在了这里", hi: "यहीं रहा", ar: "بقي هنا",
  },
  // Who actually wrote the findings (jim/research.py's answered_by): the
  // model's registry name, "vault" for the resident, "stub" for a degrade —
  // the row's provenance, worn on the screen rather than left in the wire.
  "rch.by": {
    en: "answered by {who}", es: "respondió {who}", fr: "répondu par {who}", de: "beantwortet von {who}", pt: "respondido por {who}", it: "risposta di {who}", ja: "{who} が回答", zh: "由 {who} 回答", hi: "{who} ने उत्तर दिया", ar: "أجاب {who}",
  },
  "rch.title": {
    en: "What reaches out", es: "Lo que sale al mundo", fr: "Ce qui tend la main", de: "Was hinausreicht", pt: "O que alcança lá fora", it: "Ciò che si spinge fuori", ja: "外へ届くもの", zh: "向外伸出的东西", hi: "जो बाहर पहुँचता है", ar: "ما يمتد إلى الخارج",
  },
  "rch.sub": {
    en: "a body, a code, an account, an errand", es: "un cuerpo, un código, una cuenta, un recado", fr: "un corps, un code, un compte, une course", de: "ein Körper, ein Code, ein Konto, ein Botengang", pt: "um corpo, um código, uma conta, um recado", it: "un corpo, un codice, un account, una commissione", ja: "身体、コード、アカウント、お使い", zh: "一个身体、一个码、一个账号、一趟差事", hi: "एक शरीर, एक कोड, एक खाता, एक काम", ar: "جسد، رمز، حساب، مهمة",
  },
  "rch.body": {
    en: "A body in the house", es: "Un cuerpo en la casa", fr: "Un corps dans la maison", de: "Ein Körper im Haus", pt: "Um corpo na casa", it: "Un corpo in casa", ja: "家の中の身体", zh: "屋里的身体", hi: "घर में एक शरीर", ar: "جسد في المنزل",
  },
  "rch.body.pick": {
    en: "Pick a model…", es: "Elige un modelo…", fr: "Choisissez un modèle…", de: "Modell wählen…", pt: "Escolha um modelo…", it: "Scegli un modello…", ja: "モデルを選択…", zh: "选择型号…", hi: "मॉडल चुनें…", ar: "اختر طرازًا…",
  },
  "rch.body.model": {
    en: "{label} — {maker} · first aid: {aid}", es: "{label} — {maker} · primeros auxilios: {aid}", fr: "{label} — {maker} · premiers secours : {aid}", de: "{label} — {maker} · Erste Hilfe: {aid}", pt: "{label} — {maker} · primeiros socorros: {aid}", it: "{label} — {maker} · primo soccorso: {aid}", ja: "{label} — {maker} · 応急手当: {aid}", zh: "{label} — {maker} · 急救: {aid}", hi: "{label} — {maker} · प्राथमिक चिकित्सा: {aid}", ar: "{label} — {maker} · إسعاف أولي: {aid}",
  },
  "rch.body.name.ph": {
    en: "What you call it", es: "Cómo lo llamas", fr: "Comment vous l'appelez", de: "Wie du ihn nennst", pt: "Como lhe chama", it: "Come lo chiami", ja: "呼び名", zh: "你怎么称呼它", hi: "आप इसे क्या कहते हैं", ar: "بمَ تسميه",
  },
  "rch.body.bind": {
    en: "Bind it", es: "Vincularlo", fr: "Le lier", de: "Binden", pt: "Vinculá-lo", it: "Vincolalo", ja: "紐付ける", zh: "绑定", hi: "बाँधें", ar: "اربطه",
  },
  "rch.body.rating": {
    en: "A model rated perform will do compressions itself once the automatic waiver is signed; one rated assist will talk a person through them and nothing more. The rating is the machine's, not the plan's.", es: "Un modelo con calificación «perform» hará las compresiones él mismo una vez firmada la renuncia automática; uno con «assist» guiará a una persona y nada más. La calificación es de la máquina, no del plan.", fr: "Un modèle noté « perform » fera les compressions lui-même une fois la décharge automatique signée ; un modèle « assist » guidera une personne et rien de plus. La note est celle de la machine, pas du forfait.", de: "Ein Modell mit Einstufung »perform« führt die Kompressionen selbst aus, sobald der automatische Verzicht unterzeichnet ist; eines mit »assist« leitet eine Person an und nicht mehr. Die Einstufung gehört der Maschine, nicht dem Tarif.", pt: "Um modelo classificado «perform» fará as compressões ele próprio depois de assinada a renúncia automática; um «assist» orientará uma pessoa e nada mais. A classificação é da máquina, não do plano.", it: "Un modello classificato «perform» eseguirà le compressioni da solo una volta firmata la liberatoria automatica; uno «assist» guiderà una persona e nulla più. La classificazione è della macchina, non del piano.", ja: "「perform」評価のモデルは自動免責への署名後、自ら圧迫を行います。「assist」評価のモデルは人に手順を伝えるだけです。この評価は機械のものであり、プランのものではありません。", zh: "评级为「perform」的型号在自动豁免签署后会自己做按压；评级为「assist」的只会口头指导他人，仅此而已。评级属于机器，不属于套餐。", hi: "«perform» रेटेड मॉडल स्वचालित छूट पर हस्ताक्षर होते ही स्वयं कम्प्रेशन करेगा; «assist» रेटेड केवल व्यक्ति को निर्देश देगा, इससे अधिक नहीं। रेटिंग मशीन की है, योजना की नहीं।", ar: "الطراز المصنّف «perform» سيجري الضغطات بنفسه بعد توقيع الإعفاء التلقائي؛ والمصنّف «assist» سيرشد شخصًا لا أكثر. التصنيف للآلة لا للخطة.",
  },
  "rch.body.send": {
    en: "Send", es: "Enviar", fr: "Envoyer", de: "Senden", pt: "Enviar", it: "Invia", ja: "送信", zh: "发送", hi: "भेजें", ar: "أرسل",
  },
  "rch.body.unbind": {
    en: "Unbind", es: "Desvincular", fr: "Délier", de: "Lösen", pt: "Desvincular", it: "Svincola", ja: "解除", zh: "解绑", hi: "अलग करें", ar: "افصله",
  },
  "rch.code": {
    en: "A code somebody can scan", es: "Un código que alguien puede escanear", fr: "Un code que quelqu'un peut scanner", de: "Ein Code, den jemand scannen kann", pt: "Um código que alguém pode digitalizar", it: "Un codice che qualcuno può scansionare", ja: "誰かがスキャンできるコード", zh: "谁都能扫的码", hi: "एक कोड जिसे कोई स्कैन कर सके", ar: "رمز يمكن لأحد مسحه",
  },
  "rch.code.bid.ph": {
    en: "beacon id", es: "id de baliza", fr: "id de balise", de: "Baken-Id", pt: "id da baliza", it: "id del beacon", ja: "ビーコンID", zh: "信标ID", hi: "बीकन आईडी", ar: "معرّف المنارة",
  },
  "rch.code.see": {
    en: "What a scanner sees", es: "Lo que ve quien escanea", fr: "Ce que voit le scanneur", de: "Was ein Scanner sieht", pt: "O que vê quem digitaliza", it: "Cosa vede chi scansiona", ja: "スキャンした人に見えるもの", zh: "扫描者看到的内容", hi: "स्कैन करने वाले को क्या दिखता है", ar: "ما يراه الماسح",
  },
  "rch.code.card": {
    en: "The card", es: "La tarjeta", fr: "La carte", de: "Die Karte", pt: "O cartão", it: "La scheda", ja: "カード", zh: "卡片", hi: "कार्ड", ar: "البطاقة",
  },
  "rch.code.printable": {
    en: "Printable", es: "Imprimible", fr: "Imprimable", de: "Druckbar", pt: "Imprimível", it: "Stampabile", ja: "印刷用", zh: "可打印", hi: "मुद्रण योग्य", ar: "قابل للطباعة",
  },
  "rch.code.raise": {
    en: "Raise it as a stranger would", es: "Actívalo como lo haría un desconocido", fr: "Le déclencher comme un inconnu", de: "Auslösen wie ein Fremder", pt: "Acioná-lo como um estranho faria", it: "Attivalo come farebbe un estraneo", ja: "見知らぬ人として発報する", zh: "像陌生人那样触发", hi: "अजनबी की तरह उठाएँ", ar: "أطلقه كما يفعل غريب",
  },
  "rch.code.down": {
    en: "Take the code down", es: "Retirar el código", fr: "Retirer le code", de: "Den Code abnehmen", pt: "Retirar o código", it: "Togli il codice", ja: "コードを取り下げる", zh: "撤下此码", hi: "कोड हटाएँ", ar: "أنزل الرمز",
  },
  "rch.code.pitch": {
    en: "Raising from a scanned code takes no account. It reaches the people watching and stops there — a stranger at a door can wake a household, never an ambulance.", es: "Activar desde un código escaneado no requiere cuenta. Llega a quienes vigilan y ahí se detiene — un desconocido en la puerta puede despertar a la casa, nunca llamar una ambulancia.", fr: "Déclencher depuis un code scanné ne demande aucun compte. Cela atteint les personnes qui veillent et s'arrête là — un inconnu à la porte peut réveiller un foyer, jamais une ambulance.", de: "Auslösen über einen gescannten Code braucht kein Konto. Es erreicht die Wachenden und endet dort — ein Fremder an der Tür kann einen Haushalt wecken, nie einen Krankenwagen.", pt: "Acionar a partir de um código digitalizado não requer conta. Chega às pessoas que vigiam e para aí — um estranho à porta pode acordar a casa, nunca uma ambulância.", it: "Attivare da un codice scansionato non richiede account. Raggiunge chi veglia e si ferma lì — un estraneo alla porta può svegliare una casa, mai un'ambulanza.", ja: "スキャンしたコードからの発報にアカウントは要りません。見守る人々に届き、そこで止まります — 玄関先の見知らぬ人は家の人を起こせても、救急車は決して呼べません。", zh: "从扫描的码触发无需账户。它抵达守望的人便止步于此 — 门口的陌生人能唤醒一户人家，却永远叫不来救护车。", hi: "स्कैन किए कोड से उठाने में कोई खाता नहीं लगता। यह देखने वालों तक पहुँचता है और वहीं रुक जाता है — दरवाज़े पर खड़ा अजनबी घर को जगा सकता है, कभी एम्बुलेंस नहीं।", ar: "الإطلاق من رمز ممسوح لا يتطلب حسابًا. يصل إلى المراقبين ويتوقف هناك — غريب على الباب يمكنه إيقاظ أهل البيت، لا استدعاء إسعاف أبدًا.",
  },
  "rch.code.scanned": {
    en: "The scan page is {n} characters of HTML — it is a page for a stranger's phone, not a document for this console. It is served at {path}.", es: "La página de escaneo son {n} caracteres de HTML — es una página para el teléfono de un desconocido, no un documento para esta consola. Se sirve en {path}.", fr: "La page de scan fait {n} caractères de HTML — c'est une page pour le téléphone d'un inconnu, pas un document pour cette console. Elle est servie à {path}.", de: "Die Scan-Seite umfasst {n} Zeichen HTML — sie ist eine Seite für das Telefon eines Fremden, kein Dokument für diese Konsole. Sie wird unter {path} ausgeliefert.", pt: "A página de digitalização são {n} caracteres de HTML — é uma página para o telefone de um estranho, não um documento para esta consola. É servida em {path}.", it: "La pagina di scansione è {n} caratteri di HTML — è una pagina per il telefono di un estraneo, non un documento per questa console. È servita a {path}.", ja: "スキャンページは{n}文字のHTMLです — 見知らぬ人の電話のためのページであり、このコンソールの文書ではありません。{path}で提供されます。", zh: "扫描页是{n}个字符的HTML — 它是给陌生人手机看的页面，不是这个控制台的文档。它在{path}提供。", hi: "स्कैन पेज {n} अक्षरों का HTML है — यह अजनबी के फ़ोन के लिए पेज है, इस कंसोल का दस्तावेज़ नहीं। यह {path} पर परोसा जाता है।", ar: "صفحة المسح {n} حرفًا من HTML — إنها صفحة لهاتف غريب لا وثيقة لهذه اللوحة. تُقدَّم على {path}.",
  },
  "rch.code.qr.alt": {
    en: "the printable code", es: "el código imprimible", fr: "le code imprimable", de: "der druckbare Code", pt: "o código imprimível", it: "il codice stampabile", ja: "印刷用コード", zh: "可打印的码", hi: "मुद्रण योग्य कोड", ar: "الرمز القابل للطباعة",
  },
  "rch.acc": {
    en: "Accounts elsewhere", es: "Cuentas en otros sitios", fr: "Comptes ailleurs", de: "Konten anderswo", pt: "Contas noutros lugares", it: "Account altrove", ja: "よそのアカウント", zh: "别处的账号", hi: "अन्यत्र खाते", ar: "حسابات في أماكن أخرى",
  },
  "rch.acc.platform.ph": {
    en: "mastodon", es: "mastodon", fr: "mastodon", de: "mastodon", pt: "mastodon", it: "mastodon", ja: "mastodon", zh: "mastodon", hi: "mastodon", ar: "mastodon",
  },
  "rch.acc.handle.ph": {
    en: "@you", es: "@tú", fr: "@vous", de: "@du", pt: "@você", it: "@tu", ja: "@あなた", zh: "@你", hi: "@आप", ar: "@أنت",
  },
  "rch.acc.publish.opt": {
    en: "publish — words go out", es: "publicar — las palabras salen", fr: "publier — les mots sortent", de: "veröffentlichen — Worte gehen hinaus", pt: "publicar — as palavras saem", it: "pubblica — le parole escono", ja: "発信 — 言葉が出ていく", zh: "发布 — 话语向外", hi: "प्रकाशित — शब्द बाहर जाते हैं", ar: "نشر — الكلمات تخرج",
  },
  "rch.acc.collect.opt": {
    en: "collect — words come in", es: "recoger — las palabras entran", fr: "collecter — les mots entrent", de: "sammeln — Worte kommen herein", pt: "recolher — as palavras entram", it: "raccogli — le parole entrano", ja: "収集 — 言葉が入ってくる", zh: "收集 — 话语向内", hi: "एकत्र — शब्द अंदर आते हैं", ar: "جمع — الكلمات تدخل",
  },
  "rch.acc.connect": {
    en: "Connect", es: "Conectar", fr: "Connecter", de: "Verbinden", pt: "Ligar", it: "Connetti", ja: "接続", zh: "连接", hi: "कनेक्ट", ar: "اتصال",
  },
  "rch.acc.beacon": {
    en: "Beacon", es: "Baliza", fr: "Balise", de: "Bake", pt: "Baliza", it: "Beacon", ja: "ビーコン", zh: "信标", hi: "बीकन", ar: "منارة",
  },
  "rch.acc.code": {
    en: "Code", es: "Código", fr: "Code", de: "Code", pt: "Código", it: "Codice", ja: "コード", zh: "码", hi: "कोड", ar: "الرمز",
  },
  "rch.acc.disconnect": {
    en: "Disconnect", es: "Desconectar", fr: "Déconnecter", de: "Trennen", pt: "Desligar", it: "Scollega", ja: "切断", zh: "断开", hi: "हटाएँ", ar: "افصل",
  },
  "rch.acc.say.ph": {
    en: "Say something", es: "Di algo", fr: "Dites quelque chose", de: "Sag etwas", pt: "Diga algo", it: "Di' qualcosa", ja: "何か言う", zh: "说点什么", hi: "कुछ कहें", ar: "قل شيئًا",
  },
  "rch.acc.publish": {
    en: "Publish", es: "Publicar", fr: "Publier", de: "Veröffentlichen", pt: "Publicar", it: "Pubblica", ja: "発信する", zh: "发布", hi: "प्रकाशित करें", ar: "انشر",
  },
  "rch.acc.scrape": {
    en: "Fetch the page", es: "Traer la página", fr: "Récupérer la page", de: "Die Seite holen", pt: "Buscar a página", it: "Recupera la pagina", ja: "ページを取得", zh: "抓取页面", hi: "पेज लाएँ", ar: "جلب الصفحة",
  },
  "rch.acc.collect": {
    en: "Collect", es: "Recopilar", fr: "Collecter", de: "Sammeln", pt: "Recolher", it: "Raccogli", ja: "集める", zh: "收集", hi: "एकत्र करें", ar: "اجمع",
  },
  "rch.beacon.note": {
    en: "{url} — the printable code for it is behind your own token, not a public link.", es: "{url} — su código imprimible está tras tu propio token, no en un enlace público.", fr: "{url} — son code imprimable est derrière votre propre jeton, pas un lien public.", de: "{url} — der druckbare Code dafür liegt hinter deinem eigenen Token, nicht hinter einem öffentlichen Link.", pt: "{url} — o código imprimível está atrás do seu próprio token, não de um link público.", it: "{url} — il suo codice stampabile è dietro il tuo token, non un link pubblico.", ja: "{url} — その印刷用コードは公開リンクではなく、あなた自身のトークンの向こうにあります。", zh: "{url} — 它的可打印码在你自己的令牌之后，而非公开链接。", hi: "{url} — इसका मुद्रण योग्य कोड आपके अपने टोकन के पीछे है, सार्वजनिक लिंक नहीं।", ar: "{url} — الرمز القابل للطباعة له خلف رمزك الخاص، لا رابط عام.",
  },
  "rch.ask": {
    en: "Send it to go and ask", es: "Envíalo a preguntar", fr: "L'envoyer demander", de: "Losschicken zum Fragen", pt: "Envie-o a perguntar", it: "Mandalo a chiedere", ja: "尋ねに行かせる", zh: "派它去问", hi: "पूछने भेजें", ar: "أرسله ليسأل",
  },
  "rch.ask.topic.ph": {
    en: "Topic", es: "Tema", fr: "Sujet", de: "Thema", pt: "Tema", it: "Argomento", ja: "トピック", zh: "主题", hi: "विषय", ar: "الموضوع",
  },
  "rch.ask.q.ph": {
    en: "What do you want to know?", es: "¿Qué quieres saber?", fr: "Que voulez-vous savoir ?", de: "Was willst du wissen?", pt: "O que quer saber?", it: "Cosa vuoi sapere?", ja: "何を知りたいですか？", zh: "你想知道什么？", hi: "आप क्या जानना चाहते हैं?", ar: "ماذا تريد أن تعرف؟",
  },
  "rch.ask.go": {
    en: "Go", es: "Ir", fr: "Aller", de: "Los", pt: "Ir", it: "Vai", ja: "行く", zh: "出发", hi: "जाओ", ar: "انطلق",
  },
  "rch.ask.read": {
    en: "Read", es: "Leer", fr: "Lire", de: "Lesen", pt: "Ler", it: "Leggi", ja: "読む", zh: "阅读", hi: "पढ़ें", ar: "اقرأ",
  },
  "rch.ask.keep": {
    en: "Keep what it learned", es: "Conservar lo aprendido", fr: "Garder ce qu'il a appris", de: "Behalten, was er lernte", pt: "Guardar o que aprendeu", it: "Tieni ciò che ha imparato", ja: "学んだことを保持", zh: "保留它学到的", hi: "जो सीखा उसे रखें", ar: "احتفظ بما تعلّمه",
  },
  "rch.ask.price": {
    en: "Redactions is how much of you was taken out before the question left, and left this host is whether it left at all. A screen that showed the findings and hid those two would be showing the answer and hiding what it cost.", es: "«Redactions» es cuánto de ti se quitó antes de que la pregunta saliera, y «left this host» es si salió siquiera. Una pantalla que mostrara los hallazgos y ocultara esos dos estaría mostrando la respuesta y escondiendo lo que costó.", fr: "« Redactions » dit combien de vous a été retiré avant que la question parte, et « left this host » dit si elle est partie tout court. Un écran qui montrerait les résultats en cachant ces deux-là montrerait la réponse en cachant son prix.", de: "»Redactions« sagt, wie viel von dir entfernt wurde, bevor die Frage aufbrach, und »left this host«, ob sie überhaupt aufbrach. Ein Bildschirm, der die Befunde zeigte und diese beiden versteckte, zeigte die Antwort und verbärge ihren Preis.", pt: "«Redactions» é quanto de si foi retirado antes de a pergunta sair, e «left this host» é se sequer saiu. Um ecrã que mostrasse os resultados e escondesse esses dois estaria a mostrar a resposta e a esconder o que custou.", it: "«Redactions» è quanto di te è stato tolto prima che la domanda partisse, e «left this host» è se è partita affatto. Uno schermo che mostrasse i risultati nascondendo quei due mostrerebbe la risposta nascondendo quanto è costata.", ja: "「Redactions」は質問が出発する前にあなたのどれだけが取り除かれたかを、「left this host」はそもそも出発したかどうかを示します。所見を見せてこの二つを隠す画面は、答えを見せて代償を隠すことになります。", zh: "「Redactions」是问题出发前从你身上删去了多少，「left this host」是它究竟有没有离开。若屏幕只展示发现而隐藏这两项，就是展示答案而隐藏代价。", hi: "«Redactions» यह है कि प्रश्न निकलने से पहले आपका कितना हिस्सा हटाया गया, और «left this host» यह कि वह निकला भी या नहीं। जो स्क्रीन निष्कर्ष दिखाकर ये दोनों छिपाए, वह उत्तर दिखाकर उसकी कीमत छिपा रही होगी।", ar: "«Redactions» تعني كم أُخذ منك قبل أن يغادر السؤال، و«left this host» تعني هل غادر أصلًا. الشاشة التي تعرض النتائج وتخفي هذين تعرض الجواب وتخفي ثمنه.",
  },
  "rch.wrist": {
    en: "Elsewhere and the wrist", es: "Otros sitios y la muñeca", fr: "Ailleurs et le poignet", de: "Anderswo und das Handgelenk", pt: "Outros lugares e o pulso", it: "Altrove e il polso", ja: "よそと手首", zh: "别处与手腕", hi: "अन्यत्र और कलाई", ar: "أماكن أخرى والمعصم",
  },
  "rch.wrist.visits": {
    en: "{n} community visits recorded — JIM points at QRME's rooms, QRME hosts them.", es: "{n} visitas comunitarias registradas — JIM apunta a las salas de QRME, QRME las aloja.", fr: "{n} visites communautaires enregistrées — JIM pointe vers les salles de QRME, QRME les héberge.", de: "{n} Community-Besuche verzeichnet — JIM zeigt auf QRMEs Räume, QRME beherbergt sie.", pt: "{n} visitas comunitárias registadas — o JIM aponta para as salas do QRME, o QRME aloja-as.", it: "{n} visite alla community registrate — JIM punta alle stanze di QRME, QRME le ospita.", ja: "コミュニティ訪問{n}件を記録 — JIMはQRMEのルームを指し示し、QRMEがホストします。", zh: "已记录{n}次社区访问 — JIM指向QRME的房间，由QRME托管。", hi: "{n} सामुदायिक भेंट दर्ज — JIM QRME के कमरों की ओर इशारा करता है, QRME उन्हें होस्ट करता है।", ar: "سُجلت {n} زيارة مجتمعية — يشير JIM إلى غرف QRME، وQRME يستضيفها.",
  },
  "rch.wrist.token.ph": {
    en: "watch drip token", es: "token de goteo del reloj", fr: "jeton de goutte-à-goutte de la montre", de: "Watch-Drip-Token", pt: "token de gotejamento do relógio", it: "token drip dell'orologio", ja: "ウォッチのドリップトークン", zh: "手表滴流令牌", hi: "घड़ी ड्रिप टोकन", ar: "رمز تقطير الساعة",
  },
  "rch.wrist.send": {
    en: "Send a reading", es: "Enviar una lectura", fr: "Envoyer une mesure", de: "Eine Messung senden", pt: "Enviar uma leitura", it: "Invia una lettura", ja: "測定値を送る", zh: "发送一条读数", hi: "एक रीडिंग भेजें", ar: "أرسل قراءة",
  },
  "rch.wrist.pitch": {
    en: "The watch posts against a drip token rather than an account credential, because a watch cannot hold one.", es: "El reloj publica con un token de goteo en vez de una credencial de cuenta, porque un reloj no puede guardarla.", fr: "La montre publie avec un jeton de goutte-à-goutte plutôt qu'un identifiant de compte, parce qu'une montre ne peut pas en détenir un.", de: "Die Uhr sendet gegen ein Drip-Token statt einer Kontoberechtigung, weil eine Uhr keine halten kann.", pt: "O relógio publica com um token de gotejamento em vez de uma credencial de conta, porque um relógio não pode guardá-la.", it: "L'orologio pubblica con un token drip anziché una credenziale di account, perché un orologio non può custodirla.", ja: "ウォッチはアカウント資格情報ではなくドリップトークンで送信します。ウォッチは資格情報を保持できないからです。", zh: "手表凭滴流令牌上报，而非账户凭证，因为手表无法保管凭证。", hi: "घड़ी खाता क्रेडेंशियल के बजाय ड्रिप टोकन से भेजती है, क्योंकि घड़ी क्रेडेंशियल नहीं रख सकती।", ar: "تنشر الساعة برمز تقطير لا ببيانات اعتماد حساب، لأن الساعة لا تستطيع حفظها.",
  },
  "brg.safety.english": {
    en: " (safety text in English)", es: " (texto de seguridad en inglés)", fr: " (texte de sécurité en anglais)", de: " (Sicherheitstext auf Englisch)", pt: " (texto de segurança em inglês)", it: " (testo di sicurezza in inglese)", ja: "（安全に関する文は英語）", zh: "（安全文本为英文）", hi: " (सुरक्षा पाठ अंग्रेज़ी में)", ar: " (نص السلامة بالإنجليزية)",
  },
  "brg.dock.open": {
    en: "Open it", es: "Ábrelo", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Aprilo", ja: "開く", zh: "打开", hi: "इसे खोलें", ar: "افتحه",
  },
  "brg.dock.tuck": {
    en: "Tuck it away", es: "Guárdalo", fr: "Ranger", de: "Wegräumen", pt: "Guardar", it: "Riponilo", ja: "しまう", zh: "收起", hi: "इसे समेट दें", ar: "أخفِه",
  },
  "brg.title": {
    en: "Bearing", es: "Porte", fr: "Allure", de: "Haltung", pt: "Porte", it: "Portamento", ja: "たたずまい", zh: "姿态", hi: "आचरण", ar: "الهيئة",
  },
  "brg.sub": {
    en: "how it speaks, and what it made of you", es: "cómo habla, y qué ha hecho de ti", fr: "comment il parle, et ce qu'il a fait de vous", de: "wie er spricht, und was er aus dir gemacht hat", pt: "como fala, e o que fez de si", it: "come parla, e cosa ha fatto di te", ja: "どう話すか、そしてあなたから何を読み取ったか", zh: "它如何说话，以及它对你的解读", hi: "यह कैसे बोलता है, और आपके बारे में क्या समझा", ar: "كيف يتكلم، وما استخلصه عنك",
  },
  "brg.speak": {
    en: "How it speaks", es: "Cómo habla", fr: "Comment il parle", de: "Wie er spricht", pt: "Como fala", it: "Come parla", ja: "話し方", zh: "它如何说话", hi: "यह कैसे बोलता है", ar: "كيف يتكلم",
  },
  "brg.speak.go": {
    en: "Speak this", es: "Habla esto", fr: "Parle ceci", de: "Sprich das", pt: "Fala isto", it: "Parla questo", ja: "この言語で話す", zh: "用这个说", hi: "यह बोलो", ar: "تكلم بهذه",
  },
  "brg.speak.now": {
    en: "now:", es: "ahora:", fr: "actuellement :", de: "jetzt:", pt: "agora:", it: "ora:", ja: "現在:", zh: "当前:", hi: "अभी:", ar: "الآن:",
  },
  "brg.speak.tone.ph": {
    en: "Plainly. No cheerleading.", es: "Con claridad. Sin porras.", fr: "Simplement. Sans pom-pom girls.", de: "Schlicht. Kein Anfeuern.", pt: "Com clareza. Sem claque.", it: "Con chiarezza. Niente tifo.", ja: "率直に。応援口調は不要。", zh: "直白点。不要打鸡血。", hi: "साफ़-साफ़। कोई जयकारा नहीं।", ar: "ببساطة. دون تشجيع مبالغ.",
  },
  "brg.speak.tone": {
    en: "Set the tone", es: "Fijar el tono", fr: "Définir le ton", de: "Ton festlegen", pt: "Definir o tom", it: "Imposta il tono", ja: "口調を設定", zh: "设定语气", hi: "लहजा तय करें", ar: "حدد النبرة",
  },
  "brg.speak.voice": {
    en: "Forget the voice", es: "Olvidar la voz", fr: "Oublier la voix", de: "Die Stimme vergessen", pt: "Esquecer a voz", it: "Dimentica la voce", ja: "声を忘れる", zh: "忘掉这把声音", hi: "आवाज़ भूल जाओ", ar: "انسَ الصوت",
  },
  "brg.speak.tr.ph": {
    en: "Something to translate", es: "Algo que traducir", fr: "Quelque chose à traduire", de: "Etwas zum Übersetzen", pt: "Algo para traduzir", it: "Qualcosa da tradurre", ja: "翻訳する文", zh: "要翻译的内容", hi: "अनुवाद के लिए कुछ", ar: "شيء للترجمة",
  },
  "brg.speak.tr": {
    en: "Translate", es: "Traducir", fr: "Traduire", de: "Übersetzen", pt: "Traduzir", it: "Traduci", ja: "翻訳する", zh: "翻译", hi: "अनुवाद करें", ar: "ترجِم",
  },
  "brg.told": {
    en: "What it was told", es: "Lo que se le dijo", fr: "Ce qu'on lui a dit", de: "Was ihm gesagt wurde", pt: "O que lhe foi dito", it: "Cosa gli è stato detto", ja: "伝えられたこと", zh: "它被告知的", hi: "इसे क्या बताया गया", ar: "ما قيل له",
  },
  "brg.told.note.ph": {
    en: "In your own words", es: "Con tus palabras", fr: "Avec vos mots", de: "In deinen eigenen Worten", pt: "Nas suas palavras", it: "Con parole tue", ja: "自分の言葉で", zh: "用你自己的话", hi: "अपने शब्दों में", ar: "بكلماتك أنت",
  },
  "brg.told.tell": {
    en: "Tell it", es: "Díselo", fr: "Dites-le-lui", de: "Sag es ihm", pt: "Diga-lhe", it: "Diglielo", ja: "伝える", zh: "告诉它", hi: "बताएँ", ar: "أخبره",
  },
  "brg.told.src.ph": {
    en: "calendar", es: "calendario", fr: "calendrier", de: "Kalender", pt: "calendário", it: "calendario", ja: "カレンダー", zh: "日历", hi: "कैलेंडर", ar: "التقويم",
  },
  "brg.told.ctx": {
    en: "Give it context from here", es: "Darle contexto desde aquí", fr: "Lui donner du contexte d'ici", de: "Kontext von hier geben", pt: "Dar-lhe contexto daqui", it: "Dagli contesto da qui", ja: "ここからコンテキストを渡す", zh: "从这里给它上下文", hi: "यहाँ से संदर्भ दें", ar: "أعطه سياقًا من هنا",
  },
  "brg.told.say": {
    en: "Say something unprompted", es: "Que diga algo sin preguntarle", fr: "Qu'il dise quelque chose de lui-même", de: "Unaufgefordert etwas sagen", pt: "Que diga algo sem lhe pedirem", it: "Fagli dire qualcosa spontaneamente", ja: "促されずに何か言わせる", zh: "让它主动说点什么", hi: "बिना पूछे कुछ कहे", ar: "قل شيئًا دون طلب",
  },
  "brg.told.refused": {
    en: "Refused: {err} — consent the source over in What's Held first. The check is on the server; this screen is only reporting what it said.", es: "Rechazado: {err} — consiente la fuente primero en Lo Retenido. La comprobación está en el servidor; esta pantalla solo informa de lo que dijo.", fr: "Refusé : {err} — consentez d'abord la source dans Ce qui est détenu. Le contrôle est sur le serveur ; cet écran ne fait que rapporter ce qu'il a dit.", de: "Abgelehnt: {err} — willige zuerst drüben in »Was gehalten wird« in die Quelle ein. Die Prüfung liegt auf dem Server; dieser Bildschirm berichtet nur, was er sagte.", pt: "Recusado: {err} — consinta a fonte primeiro em O Que É Guardado. A verificação está no servidor; este ecrã apenas relata o que ele disse.", it: "Rifiutato: {err} — acconsenti prima la fonte in Ciò che è custodito. Il controllo è sul server; questa schermata riporta solo ciò che ha detto.", ja: "拒否: {err} — まず「保持されているもの」でそのソースに同意してください。チェックはサーバー側にあり、この画面はその返答を伝えているだけです。", zh: "被拒: {err} — 请先到「所持有的」里同意该来源。检查在服务器上；此屏幕只是转述它的答复。", hi: "अस्वीकृत: {err} — पहले «जो रखा गया है» में स्रोत की सहमति दें। जाँच सर्वर पर है; यह स्क्रीन केवल उसका कहा बता रही है।", ar: "مرفوض: {err} — وافق على المصدر أولًا في «ما هو محفوظ». الفحص على الخادم؛ هذه الشاشة تنقل ما قاله فحسب.",
  },
  "brg.told.med.ph": {
    en: "medication id", es: "id del medicamento", fr: "id du médicament", de: "Medikamenten-Id", pt: "id do medicamento", it: "id del farmaco", ja: "薬ID", zh: "药物ID", hi: "दवा आईडी", ar: "معرّف الدواء",
  },
  "brg.told.dose.ph": {
    en: "new dose", es: "nueva dosis", fr: "nouvelle dose", de: "neue Dosis", pt: "nova dose", it: "nuova dose", ja: "新しい用量", zh: "新剂量", hi: "नई ख़ुराक", ar: "جرعة جديدة",
  },
  "brg.told.med": {
    en: "Correct a medication", es: "Corregir un medicamento", fr: "Corriger un médicament", de: "Ein Medikament korrigieren", pt: "Corrigir um medicamento", it: "Correggi un farmaco", ja: "薬を修正", zh: "更正一种药物", hi: "दवा सुधारें", ar: "صحّح دواءً",
  },
  "brg.made": {
    en: "What it made of that", es: "Lo que ha hecho de ello", fr: "Ce qu'il en a fait", de: "Was er daraus gemacht hat", pt: "O que fez disso", it: "Cosa ne ha fatto", ja: "そこから読み取ったこと", zh: "它由此得出的", hi: "इसने उससे क्या समझा", ar: "ما استخلصه من ذلك",
  },
  "brg.made.stats": {
    en: "{c} check-ins · average mood {m} · {i} insights · {e} events · {s} calm sessions · {x} coach exchanges", es: "{c} registros · ánimo medio {m} · {i} observaciones · {e} eventos · {s} sesiones de calma · {x} intercambios con el coach", fr: "{c} pointages · humeur moyenne {m} · {i} aperçus · {e} événements · {s} séances de calme · {x} échanges avec le coach", de: "{c} Check-ins · Durchschnittsstimmung {m} · {i} Einsichten · {e} Ereignisse · {s} Ruhesitzungen · {x} Coach-Wechsel", pt: "{c} check-ins · humor médio {m} · {i} observações · {e} eventos · {s} sessões de calma · {x} trocas com o coach", it: "{c} check-in · umore medio {m} · {i} osservazioni · {e} eventi · {s} sessioni di calma · {x} scambi col coach", ja: "チェックイン{c}件 · 平均気分{m} · 洞察{i}件 · イベント{e}件 · カームセッション{s}件 · コーチとのやり取り{x}件", zh: "{c}次签到 · 平均心情{m} · {i}条洞察 · {e}条事件 · {s}次平静练习 · {x}次教练往来", hi: "{c} चेक-इन · औसत मनोदशा {m} · {i} अंतर्दृष्टियाँ · {e} घटनाएँ · {s} शांत सत्र · {x} कोच संवाद", ar: "{c} تسجيلات · متوسط المزاج {m} · {i} استبصارات · {e} أحداث · {s} جلسات هدوء · {x} تبادلات مع المدرب",
  },
  "brg.made.open": {
    en: "{n} follow-up question{s} still open — it asked and has not been answered.", es: "{n} preguntas de seguimiento siguen abiertas — preguntó y no se le ha respondido.", fr: "{n} questions de suivi encore ouvertes — il a demandé et n'a pas eu de réponse.", de: "{n} Nachfragen noch offen — er fragte und wurde nicht beantwortet.", pt: "{n} perguntas de seguimento ainda abertas — perguntou e não foi respondido.", it: "{n} domande di follow-up ancora aperte — ha chiesto e non ha avuto risposta.", ja: "未回答のフォローアップ質問が{n}件 — 尋ねたまま答えられていません。", zh: "{n}个跟进问题仍未回答 — 它问了，还没人答。", hi: "{n} अनुवर्ती प्रश्न अभी खुले हैं — इसने पूछा और उत्तर नहीं मिला।", ar: "{n} أسئلة متابعة ما زالت مفتوحة — سأل ولم يُجَب.",
  },
  "brg.guide": {
    en: "The guide", es: "La guía", fr: "Le guide", de: "Der Führer", pt: "O guia", it: "La guida", ja: "ガイド", zh: "向导", hi: "मार्गदर्शक", ar: "الدليل",
  },
  "brg.guide.start": {
    en: "Start the tour", es: "Empezar el recorrido", fr: "Commencer la visite", de: "Rundgang starten", pt: "Começar a visita", it: "Inizia il tour", ja: "ツアーを開始", zh: "开始导览", hi: "सैर शुरू करें", ar: "ابدأ الجولة",
  },
  "brg.guide.step": {
    en: "Read a step", es: "Leer un paso", fr: "Lire une étape", de: "Einen Schritt lesen", pt: "Ler um passo", it: "Leggi un passo", ja: "ステップを読む", zh: "读一步", hi: "एक चरण पढ़ें", ar: "اقرأ خطوة",
  },
  "brg.guide.screen": {
    en: "What is this screen?", es: "¿Qué es esta pantalla?", fr: "C'est quoi, cet écran ?", de: "Was ist dieser Bildschirm?", pt: "O que é este ecrã?", it: "Cos'è questa schermata?", ja: "この画面は何？", zh: "这个屏幕是什么？", hi: "यह स्क्रीन क्या है?", ar: "ما هذه الشاشة؟",
  },
  "brg.guide.done": {
    en: "Mark it done", es: "Marcarlo hecho", fr: "Le marquer fait", de: "Als erledigt markieren", pt: "Marcar como feito", it: "Segna come fatto", ja: "完了にする", zh: "标记完成", hi: "पूर्ण चिह्नित करें", ar: "علّمه منجزًا",
  },
  "brg.guide.progress": {
    en: "{d} of {t} done", es: "{d} de {t} hechos", fr: "{d} sur {t} faits", de: "{d} von {t} erledigt", pt: "{d} de {t} feitos", it: "{d} di {t} fatti", ja: "{t}件中{d}件完了", zh: "{t}项中已完成{d}项", hi: "{t} में से {d} पूर्ण", ar: "أُنجز {d} من {t}",
  },
  "brg.guide.topics": {
    en: "Help topics", es: "Temas de ayuda", fr: "Rubriques d'aide", de: "Hilfethemen", pt: "Temas de ajuda", it: "Argomenti di aiuto", ja: "ヘルプトピック", zh: "帮助主题", hi: "सहायता विषय", ar: "مواضيع المساعدة",
  },
  "brg.dock": {
    en: "The dock in the corner", es: "El muelle de la esquina", fr: "Le dock dans le coin", de: "Das Dock in der Ecke", pt: "A doca no canto", it: "Il dock nell'angolo", ja: "隅のドック", zh: "角落里的坞", hi: "कोने का डॉक", ar: "المرسى في الزاوية",
  },
  "brg.dock.line": {
    en: "{corner} · {state}{forced} · showing {face}", es: "{corner} · {state}{forced} · mostrando {face}", fr: "{corner} · {state}{forced} · affiche {face}", de: "{corner} · {state}{forced} · zeigt {face}", pt: "{corner} · {state}{forced} · a mostrar {face}", it: "{corner} · {state}{forced} · mostra {face}", ja: "{corner} · {state}{forced} · 表示中 {face}", zh: "{corner} · {state}{forced} · 正在显示{face}", hi: "{corner} · {state}{forced} · दिखा रहा {face}", ar: "{corner} · {state}{forced} · يعرض {face}",
  },
  "brg.dock.move": {
    en: "Move it to the other corner", es: "Moverlo a la otra esquina", fr: "Le déplacer dans l'autre coin", de: "In die andere Ecke schieben", pt: "Movê-lo para o outro canto", it: "Spostalo nell'altro angolo", ja: "反対の隅へ移動", zh: "移到另一个角落", hi: "दूसरे कोने में ले जाएँ", ar: "انقله إلى الزاوية الأخرى",
  },
  "brg.tell": {
    en: "Tell us about the app", es: "Cuéntanos sobre la app", fr: "Parlez-nous de l'appli", de: "Erzähl uns von der App", pt: "Fale-nos da app", it: "Parlaci dell'app", ja: "アプリについて教えてください", zh: "跟我们聊聊这个应用", hi: "ऐप के बारे में बताएँ", ar: "أخبرنا عن التطبيق",
  },
  "brg.tell.ph": {
    en: "What would make this better?", es: "¿Qué lo haría mejor?", fr: "Qu'est-ce qui rendrait cela meilleur ?", de: "Was würde das besser machen?", pt: "O que tornaria isto melhor?", it: "Cosa lo renderebbe migliore?", ja: "何があれば良くなりますか？", zh: "怎样能做得更好？", hi: "इसे बेहतर क्या बनाएगा?", ar: "ما الذي يجعله أفضل؟",
  },
  "brg.tell.send": {
    en: "Send it", es: "Enviarlo", fr: "L'envoyer", de: "Absenden", pt: "Enviá-lo", it: "Invialo", ja: "送信する", zh: "发送", hi: "भेजें", ar: "أرسله",
  },
  "brg.tell.good": {
    en: "Good answer", es: "Buena respuesta", fr: "Bonne réponse", de: "Gute Antwort", pt: "Boa resposta", it: "Buona risposta", ja: "良い回答", zh: "回答得好", hi: "अच्छा उत्तर", ar: "إجابة جيدة",
  },
  "brg.tell.bad": {
    en: "Bad answer", es: "Mala respuesta", fr: "Mauvaise réponse", de: "Schlechte Antwort", pt: "Má resposta", it: "Cattiva risposta", ja: "悪い回答", zh: "回答得差", hi: "ख़राब उत्तर", ar: "إجابة سيئة",
  },
  "brg.tell.board": {
    en: "{n} suggestion{s} in all · {m} of them yours", es: "{n} sugerencias en total · {m} son tuyas", fr: "{n} suggestions en tout · {m} sont les vôtres", de: "{n} Vorschläge insgesamt · {m} davon deine", pt: "{n} sugestões no total · {m} são suas", it: "{n} suggerimenti in tutto · {m} sono tuoi", ja: "提案は計{n}件 · うち{m}件があなたのもの", zh: "共{n}条建议 · 其中{m}条是你的", hi: "कुल {n} सुझाव · उनमें {m} आपके", ar: "{n} اقتراحات إجمالًا · {m} منها لك",
  },
  "set.title": {
    en: "Privacy & Connection", es: "Privacidad y conexión", fr: "Confidentialité et connexion", de: "Datenschutz & Verbindung", pt: "Privacidade e ligação", it: "Privacy e connessione", ja: "プライバシーと接続", zh: "隐私与连接", hi: "गोपनीयता और कनेक्शन", ar: "الخصوصية والاتصال",
  },
  "set.api": {
    en: "API connection", es: "Conexión con la API", fr: "Connexion à l'API", de: "API-Verbindung", pt: "Ligação à API", it: "Connessione API", ja: "API接続", zh: "API 连接", hi: "API कनेक्शन", ar: "اتصال الواجهة",
  },
  "set.look": {
    en: "How it looks", es: "Cómo se ve", fr: "Son apparence", de: "Aussehen", pt: "Como fica", it: "Aspetto", ja: "見た目", zh: "外观", hi: "यह कैसा दिखे", ar: "المظهر",
  },
  "set.look.blurb": {
    en: "Colors only — photos and tiles stay as they are. You can also just ask for it in a session: \"make it black and white\".",
    es: "Solo colores: las fotos y los mosaicos quedan como están. También puedes pedirlo en una sesión: «ponlo en blanco y negro».",
    fr: "Couleurs uniquement — photos et vignettes restent telles quelles. Vous pouvez aussi le demander en session : « mets-le en noir et blanc ».",
    de: "Nur Farben — Fotos und Kacheln bleiben, wie sie sind. Du kannst es auch einfach in einer Sitzung sagen: „mach es schwarz-weiß“.",
    pt: "Só cores — fotos e mosaicos ficam como estão. Também pode simplesmente pedir numa sessão: «põe a preto e branco».",
    it: "Solo colori: foto e riquadri restano come sono. Puoi anche chiederlo in una sessione: «mettilo in bianco e nero».",
    ja: "色だけが変わります。写真やタイルはそのままです。セッションで「白黒にして」と頼むこともできます。",
    zh: "只改颜色——照片和图块保持原样。你也可以在会话里直接说：“把它改成黑白的”。",
    hi: "सिर्फ़ रंग — फ़ोटो और टाइलें जैसी हैं वैसी रहती हैं। आप सत्र में बस कह भी सकते हैं: \"इसे ब्लैक एंड व्हाइट कर दो\"।",
    ar: "الألوان فقط — تبقى الصور والمربعات كما هي. يمكنك أيضًا طلب ذلك في جلسة: «اجعله أبيض وأسود».",
  },
  "look.standard": {
    en: "Standard", es: "Estándar", fr: "Standard", de: "Standard", pt: "Padrão", it: "Standard", ja: "標準", zh: "标准", hi: "मानक", ar: "قياسي",
  },
  "look.midnight": {
    en: "Midnight — black, white text", es: "Medianoche — negro, texto blanco", fr: "Minuit — noir, texte blanc", de: "Mitternacht — Schwarz, weißer Text", pt: "Meia-noite — preto, texto branco", it: "Mezzanotte — nero, testo bianco", ja: "ミッドナイト — 黒地に白文字", zh: "午夜 — 黑底白字", hi: "मिडनाइट — काला, सफ़ेद टेक्स्ट", ar: "منتصف الليل — أسود بنص أبيض",
  },
  "look.paper": {
    en: "Paper — white, black text", es: "Papel — blanco, texto negro", fr: "Papier — blanc, texte noir", de: "Papier — Weiß, schwarzer Text", pt: "Papel — branco, texto preto", it: "Carta — bianco, testo nero", ja: "ペーパー — 白地に黒文字", zh: "纸张 — 白底黑字", hi: "पेपर — सफ़ेद, काला टेक्स्ट", ar: "ورق — أبيض بنص أسود",
  },
  "set.api.base": {
    en: "Backend base URL", es: "URL base del servidor", fr: "URL de base du serveur", de: "Basis-URL des Backends", pt: "URL base do servidor", it: "URL base del backend", ja: "バックエンドのベースURL", zh: "后端基础 URL", hi: "बैकएंड बेस URL", ar: "عنوان الخادم الأساسي",
  },
  "set.api.backend": {
    en: "Backend:", es: "Servidor:", fr: "Serveur :", de: "Backend:", pt: "Servidor:", it: "Backend:", ja: "バックエンド:", zh: "后端:", hi: "बैकएंड:", ar: "الخادم:",
  },
  "set.save": {
    en: "Save", es: "Guardar", fr: "Enregistrer", de: "Speichern", pt: "Guardar", it: "Salva", ja: "保存", zh: "保存", hi: "सहेजें", ar: "احفظ",
  },
  "set.clear": {
    en: "Clear", es: "Borrar", fr: "Effacer", de: "Löschen", pt: "Limpar", it: "Cancella", ja: "クリア", zh: "清除", hi: "हटाएँ", ar: "امسح",
  },
  "set.key": {
    en: "Your model API key", es: "Tu clave de API del modelo", fr: "Votre clé d'API du modèle", de: "Dein Modell-API-Schlüssel", pt: "A sua chave de API do modelo", it: "La tua chiave API del modello", ja: "あなたのモデルAPIキー", zh: "你的模型 API 密钥", hi: "आपकी मॉडल API कुंजी", ar: "مفتاح واجهة النموذج الخاص بك",
  },
  "set.key.pitch": {
    en: "Paste your own key (Anthropic sk-ant-…, or OpenAI / xAI / Gemini for those providers) and your Guardian's replies run on your credential. It stays on this device and rides only your own requests — the server never stores it. Leave it empty to use whatever key the deployment lends.", es: "Pega tu propia clave (Anthropic sk-ant-…, o de OpenAI / xAI / Gemini para esos proveedores) y las respuestas de tu Guardián correrán con tu credencial. Se queda en este dispositivo y viaja solo con tus propias peticiones — el servidor nunca la almacena. Déjala vacía para usar la clave que preste el despliegue.", fr: "Collez votre propre clé (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini pour ces fournisseurs) et les réponses de votre Gardien tournent sur votre identifiant. Elle reste sur cet appareil et n'accompagne que vos propres requêtes — le serveur ne la stocke jamais. Laissez-la vide pour utiliser la clé que prête le déploiement.", de: "Füg deinen eigenen Schlüssel ein (Anthropic sk-ant-…, oder OpenAI / xAI / Gemini für diese Anbieter), und die Antworten deines Guardians laufen auf deinem Zugang. Er bleibt auf diesem Gerät und reist nur mit deinen eigenen Anfragen — der Server speichert ihn nie. Lass ihn leer, um den Schlüssel zu nutzen, den das Deployment leiht.", pt: "Cole a sua própria chave (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini para esses fornecedores) e as respostas do seu Guardião correm com a sua credencial. Fica neste dispositivo e viaja só com os seus próprios pedidos — o servidor nunca a guarda. Deixe-a vazia para usar a chave que o deployment empresta.", it: "Incolla la tua chiave (Anthropic sk-ant-…, oppure OpenAI / xAI / Gemini per quei provider) e le risposte del tuo Guardian girano sulla tua credenziale. Resta su questo dispositivo e viaggia solo con le tue richieste — il server non la memorizza mai. Lasciala vuota per usare la chiave che presta il deployment.", ja: "自分のキーを貼り付けてください（Anthropicは sk-ant-…、各プロバイダーはOpenAI / xAI / Gemini のもの）。するとガーディアンの返答はあなたの資格情報で動きます。キーはこの端末に留まり、あなた自身のリクエストにだけ同行します — サーバーが保存することはありません。空欄にすれば、この配備が貸すキーが使われます。", zh: "粘贴你自己的密钥（Anthropic 用 sk-ant-…，对应提供方则用 OpenAI / xAI / Gemini 的密钥），你的守护者的回复便以你的凭证运行。它留在本设备上，只随你自己的请求同行 — 服务器绝不存储它。留空则使用本部署出借的密钥。", hi: "अपनी कुंजी चिपकाएँ (Anthropic के लिए sk-ant-…, या उन प्रदाताओं के लिए OpenAI / xAI / Gemini) और आपके गार्जियन के जवाब आपकी क्रेडेंशियल पर चलेंगे। यह इसी डिवाइस पर रहती है और केवल आपके अपने अनुरोधों के साथ जाती है — सर्वर इसे कभी संग्रहित नहीं करता। खाली छोड़ें तो डिप्लॉयमेंट जो कुंजी उधार देता है वही चलेगी।", ar: "الصق مفتاحك الخاص (Anthropic بصيغة sk-ant-…، أو OpenAI / xAI / Gemini لتلك المزودات) فتعمل ردود حارسك على اعتمادك. يبقى على هذا الجهاز ويرافق طلباتك أنت فقط — ولا يخزّنه الخادم أبدًا. اتركه فارغًا لاستخدام المفتاح الذي يعيره هذا النشر.",
  },
  "set.key.whosebill": {
    en: "During the beta you are using this deployment's keys, and its owner is paying for them. Put your own key in this box and the charges become yours from that moment on.", es: "Durante la beta usas las claves de esta instalación y su dueño las paga. Si pones tu propia clave aquí, los cargos pasan a ser tuyos desde ese momento.", fr: "Pendant la bêta, vous utilisez les clés de ce déploiement et son propriétaire les paie. Mettez votre propre clé ici et les frais deviennent les vôtres à partir de ce moment.", de: "Während der Beta nutzt du die Schlüssel dieser Installation, und ihr Besitzer bezahlt sie. Trägst du hier deinen eigenen Schlüssel ein, gehen die Kosten ab diesem Moment auf dich über.", pt: "Durante a beta usa as chaves desta instalação, e o dono está a pagá-las. Se puser a sua própria chave aqui, os custos passam a ser seus a partir desse momento.", it: "Durante la beta stai usando le chiavi di questa installazione, e il proprietario le sta pagando. Se metti qui la tua chiave, da quel momento i costi diventano tuoi.", ja: "ベータ期間中はこの環境のキーを使っており、費用は所有者が負担しています。ここに自分のキーを入れると、その時点から請求はあなたのものになります。", zh: "测试期间你使用的是本部署的密钥，费用由其所有者承担。在此填入你自己的密钥后，从那一刻起费用由你承担。", hi: "बीटा के दौरान आप इस तैनाती की कुंजियाँ इस्तेमाल कर रहे हैं और उनका खर्च मालिक उठा रहा है। यहाँ अपनी कुंजी डालते ही उस क्षण से शुल्क आपका हो जाएगा।", ar: "خلال النسخة التجريبية أنت تستخدم مفاتيح هذا النظام، ومالكه هو من يدفع ثمنها. وبمجرد إدخال مفتاحك الخاص هنا تصبح التكاليف عليك من تلك اللحظة.",
  },
  "set.key.label": {
    en: "API key", es: "Clave de API", fr: "Clé d'API", de: "API-Schlüssel", pt: "Chave de API", it: "Chiave API", ja: "APIキー", zh: "API 密钥", hi: "API कुंजी", ar: "مفتاح الواجهة",
  },
  "set.key.ph": {
    en: "sk-…", es: "sk-…", fr: "sk-…", de: "sk-…", pt: "sk-…", it: "sk-…", ja: "sk-…", zh: "sk-…", hi: "sk-…", ar: "sk-…",
  },
  "set.pair": {
    en: "Open on your phone", es: "Abrir en tu teléfono", fr: "Ouvrir sur votre téléphone", de: "Auf dem Telefon öffnen", pt: "Abrir no seu telefone", it: "Apri sul telefono", ja: "スマートフォンで開く", zh: "在手机上打开", hi: "अपने फ़ोन पर खोलें", ar: "افتح على هاتفك",
  },
  "set.pair.alt": {
    en: "QR code for the console URL on this network", es: "Código QR de la URL de la consola en esta red", fr: "QR code de l'URL de la console sur ce réseau", de: "QR-Code der Konsolen-URL in diesem Netzwerk", pt: "Código QR do URL da consola nesta rede", it: "Codice QR dell'URL della console su questa rete", ja: "このネットワーク上のコンソールURLのQRコード", zh: "本网络上控制台网址的二维码", hi: "इस नेटवर्क पर कंसोल URL का QR कोड", ar: "رمز QR لعنوان اللوحة على هذه الشبكة",
  },
  "set.adapt": {
    en: "What JIM has learned about you", es: "Lo que JIM ha aprendido sobre ti", fr: "Ce que JIM a appris sur vous", de: "Was JIM über dich gelernt hat", pt: "O que o JIM aprendeu sobre si", it: "Ciò che JIM ha imparato su di te", ja: "JIM があなたについて学んだこと", zh: "JIM 对你的了解", hi: "JIM ने आपके बारे में क्या सीखा", ar: "ما تعلَّمه JIM عنك",
  },
  "set.adapt.pitch": {
    en: "A profile derived from your own history — the conditions you declared, how your check-ins trend, what you bring up, and which guidance has actually helped. It shapes how the coach answers. Nothing is sent to a model vendor to build it.", es: "Un perfil derivado de tu propio historial — las condiciones que declaraste, cómo evolucionan tus registros, lo que sacas a colación y qué orientación te ha ayudado de verdad. Da forma a cómo responde el coach. No se envía nada a un proveedor de modelos para construirlo.", fr: "Un profil dérivé de votre propre historique — les affections que vous avez déclarées, la tendance de vos pointages, ce que vous évoquez, et quels conseils ont réellement aidé. Il façonne la façon dont le coach répond. Rien n'est envoyé à un fournisseur de modèles pour le construire.", de: "Ein Profil aus deiner eigenen Historie — die Beschwerden, die du angabst, wie sich deine Check-ins entwickeln, was du ansprichst und welche Ratschläge tatsächlich geholfen haben. Es prägt, wie der Coach antwortet. Zum Bauen wird nichts an einen Modellanbieter gesendet.", pt: "Um perfil derivado do seu próprio histórico — as condições que declarou, como evoluem os seus check-ins, o que traz à conversa e que orientação ajudou realmente. Molda a forma como o coach responde. Nada é enviado a um fornecedor de modelos para o construir.", it: "Un profilo derivato dalla tua stessa storia — le condizioni che hai dichiarato, come vanno i tuoi check-in, cosa tiri fuori, e quale guida ha davvero aiutato. Modella il modo in cui il coach risponde. Nulla viene inviato a un fornitore di modelli per costruirlo.", ja: "あなた自身の履歴から導かれたプロフィールです — 申告した状態、チェックインの推移、話題にすること、そして実際に役立った助言。コーチの答え方を形づくります。これを作るためにモデルベンダーへ送られるものは何もありません。", zh: "由你自己的历史推导出的画像 — 你申报的状况、签到的趋势、你会提起的事，以及哪些指导真正有用。它塑造教练的回答方式。构建它不会向任何模型厂商发送任何东西。", hi: "आपके अपने इतिहास से बना एक प्रोफ़ाइल — आपने जो स्थितियाँ बताईं, आपके चेक-इन का रुझान, आप क्या उठाते हैं, और किस मार्गदर्शन ने वास्तव में मदद की। यह तय करता है कि कोच कैसे जवाब देता है। इसे बनाने के लिए किसी मॉडल विक्रेता को कुछ नहीं भेजा जाता।", ar: "ملف مستخلص من تاريخك أنت — الحالات التي أعلنتها، واتجاه تسجيلاتك، وما تثيره، وأي إرشاد أفاد فعلًا. يشكّل طريقة إجابة المدرب. ولا يُرسل شيء إلى مزود نماذج لبنائه.",
  },
  "set.adapt.conf": {
    en: "{pct}% confidence", es: "{pct}% de confianza", fr: "{pct}% de confiance", de: "{pct}% Konfidenz", pt: "{pct}% de confiança", it: "{pct}% di confidenza", ja: "確信度{pct}%", zh: "置信度{pct}%", hi: "{pct}% विश्वास", ar: "ثقة {pct}%",
  },
  "set.adapt.from": {
    en: "from {n} pieces of your own history", es: "de {n} fragmentos de tu propio historial", fr: "à partir de {n} éléments de votre propre historique", de: "aus {n} Teilen deiner eigenen Historie", pt: "de {n} peças do seu próprio histórico", it: "da {n} pezzi della tua stessa storia", ja: "あなた自身の履歴{n}件から", zh: "取自你自己历史中的{n}条", hi: "आपके अपने इतिहास के {n} टुकड़ों से", ar: "من {n} قطعة من تاريخك",
  },
  "set.adapt.rebuild": {
    en: "Rebuild", es: "Reconstruir", fr: "Reconstruire", de: "Neu aufbauen", pt: "Reconstruir", it: "Ricostruisci", ja: "再構築", zh: "重建", hi: "फिर बनाएँ", ar: "أعد البناء",
  },
  "set.adapt.helped": {
    en: "{cond}: guidance helped {h} of {a} times", es: "{cond}: la orientación ayudó {h} de {a} veces", fr: "{cond} : les conseils ont aidé {h} fois sur {a}", de: "{cond}: Rat half {h} von {a} Malen", pt: "{cond}: a orientação ajudou {h} de {a} vezes", it: "{cond}: la guida ha aiutato {h} volte su {a}", ja: "{cond}: 助言が役立ったのは{a}回中{h}回", zh: "{cond}: 指导在{a}次中有{h}次有用", hi: "{cond}: मार्गदर्शन {a} में से {h} बार काम आया", ar: "{cond}: أفاد الإرشاد {h} من {a} مرات",
  },
  "set.adapt.work": {
    en: "work: {what}", es: "trabajo: {what}", fr: "travail : {what}", de: "Arbeit: {what}", pt: "trabalho: {what}", it: "lavoro: {what}", ja: "仕事: {what}", zh: "工作: {what}", hi: "काम: {what}", ar: "العمل: {what}",
  },
  "set.adapt.tone": {
    en: "tone you asked for: {tone}", es: "tono que pediste: {tone}", fr: "ton que vous avez demandé : {tone}", de: "gewünschter Ton: {tone}", pt: "tom que pediu: {tone}", it: "tono che hai chiesto: {tone}", ja: "希望した口調: {tone}", zh: "你要求的语气: {tone}", hi: "आपने जो लहजा माँगा: {tone}", ar: "النبرة التي طلبتها: {tone}",
  },
  "set.adapt.build": {
    en: "Build it from my history", es: "Construirlo desde mi historial", fr: "Le construire depuis mon historique", de: "Aus meiner Historie aufbauen", pt: "Construí-lo a partir do meu histórico", it: "Costruiscilo dalla mia storia", ja: "自分の履歴から作る", zh: "用我的历史来构建", hi: "मेरे इतिहास से बनाएँ", ar: "ابنِه من تاريخي",
  },
  "set.anon": {
    en: "Your name here", es: "Tu nombre aquí", fr: "Votre nom ici", de: "Dein Name hier", pt: "O seu nome aqui", it: "Il tuo nome qui", ja: "ここでのあなたの名前", zh: "你在这里的名字", hi: "यहाँ आपका नाम", ar: "اسمك هنا",
  },
  "set.anon.pseudo": {
    en: "You use JIM as {name} — a pseudonym. JIM never learned your real name.", es: "Usas JIM como {name} — un seudónimo. JIM nunca supo tu nombre real.", fr: "Vous utilisez JIM sous le nom {name} — un pseudonyme. JIM n'a jamais appris votre vrai nom.", de: "Du nutzt JIM als {name} — ein Pseudonym. JIM hat deinen echten Namen nie erfahren.", pt: "Usa o JIM como {name} — um pseudónimo. O JIM nunca soube o seu nome real.", it: "Usi JIM come {name} — uno pseudonimo. JIM non ha mai saputo il tuo vero nome.", ja: "あなたはJIMを{name}として使っています — 仮名です。JIMがあなたの本名を知ることはありませんでした。", zh: "你以{name}的身份使用 JIM — 那是化名。JIM 从未知道你的真名。", hi: "आप JIM का उपयोग {name} के रूप में करते हैं — यह छद्मनाम है। JIM ने आपका असली नाम कभी नहीं जाना।", ar: "تستخدم JIM باسم {name} — وهو اسم مستعار. لم يعرف JIM اسمك الحقيقي قط.",
  },
  "set.anon.keeps": {
    en: "Keeps: {x}", es: "Conserva: {x}", fr: "Garde : {x}", de: "Behält: {x}", pt: "Mantém: {x}", it: "Mantiene: {x}", ja: "保つもの: {x}", zh: "保留: {x}", hi: "रखता है: {x}", ar: "يحتفظ بـ: {x}",
  },
  "set.anon.costs": {
    en: "Costs: {x}", es: "Cuesta: {x}", fr: "Coûte : {x}", de: "Kostet: {x}", pt: "Custa: {x}", it: "Costa: {x}", ja: "失うもの: {x}", zh: "代价: {x}", hi: "क़ीमत: {x}", ar: "يكلّف: {x}",
  },
  "set.anon.own": {
    en: "You use JIM under your own name ({name}).", es: "Usas JIM con tu propio nombre ({name}).", fr: "Vous utilisez JIM sous votre vrai nom ({name}).", de: "Du nutzt JIM unter deinem eigenen Namen ({name}).", pt: "Usa o JIM com o seu próprio nome ({name}).", it: "Usi JIM con il tuo vero nome ({name}).", ja: "あなたは本名（{name}）でJIMを使っています。", zh: "你以自己的真名（{name}）使用 JIM。", hi: "आप JIM का उपयोग अपने असली नाम ({name}) से करते हैं।", ar: "تستخدم JIM باسمك الحقيقي ({name}).",
  },
  "set.data": {
    en: "Your data", es: "Tus datos", fr: "Vos données", de: "Deine Daten", pt: "Os seus dados", it: "I tuoi dati", ja: "あなたのデータ", zh: "你的数据", hi: "आपका डेटा", ar: "بياناتك",
  },
  "set.data.note": {
    en: "Guidance runs on-device; sensitive payloads seal into the PDI vault when the tandem is on. User: {uid}", es: "La orientación corre en el dispositivo; las cargas sensibles se sellan en la bóveda PDI cuando el tándem está activo. Usuario: {uid}", fr: "Les conseils tournent sur l'appareil ; les charges sensibles sont scellées dans le coffre PDI quand le tandem est actif. Utilisateur : {uid}", de: "Die Beratung läuft auf dem Gerät; sensible Daten werden im PDI-Tresor versiegelt, wenn das Tandem an ist. Nutzer: {uid}", pt: "A orientação corre no dispositivo; as cargas sensíveis selam-se no cofre PDI quando o tandem está ligado. Utilizador: {uid}", it: "La guida gira sul dispositivo; i payload sensibili si sigillano nel caveau PDI quando il tandem è attivo. Utente: {uid}", ja: "ガイダンスは端末上で動きます。タンデムが有効なとき、機微なペイロードはPDI保管庫に封印されます。ユーザー: {uid}", zh: "指导在设备上运行；串联开启时，敏感负载会封入 PDI 保险库。用户: {uid}", hi: "मार्गदर्शन डिवाइस पर चलता है; टेंडम चालू होने पर संवेदनशील पेलोड PDI तिजोरी में सील हो जाते हैं। उपयोगकर्ता: {uid}", ar: "يعمل الإرشاد على الجهاز؛ وتُختم الحمولات الحساسة في خزنة PDI عندما يكون الترادف مفعّلًا. المستخدم: {uid}",
  },
  "set.data.signout": {
    en: "Sign out & end session", es: "Cerrar sesión y terminar", fr: "Se déconnecter et clore la session", de: "Abmelden & Sitzung beenden", pt: "Terminar sessão e sair", it: "Esci e chiudi la sessione", ja: "サインアウトしてセッションを終了", zh: "登出并结束会话", hi: "साइन आउट करें और सत्र समाप्त करें", ar: "سجّل الخروج وأنهِ الجلسة",
  },
  "set.cloud": {
    en: "What you contribute", es: "Lo que aportas", fr: "Ce que vous contribuez", de: "Was du beiträgst", pt: "O que contribui", it: "Cosa contribuisci", ja: "あなたが提供するもの", zh: "你贡献了什么", hi: "आप क्या योगदान देते हैं", ar: "ما تساهم به",
  },
  "set.cloud.stop": {
    en: "Stop contributing", es: "Dejar de aportar", fr: "Cesser de contribuer", de: "Beitragen beenden", pt: "Deixar de contribuir", it: "Smetti di contribuire", ja: "提供をやめる", zh: "停止贡献", hi: "योगदान बंद करें", ar: "أوقف المساهمة",
  },
  "set.loc": {
    en: "Where to look", es: "Dónde buscar", fr: "Où chercher", de: "Wo gesucht wird", pt: "Onde procurar", it: "Dove cercare", ja: "どこを探すか", zh: "在哪里查找", hi: "कहाँ देखना है", ar: "أين يُبحث",
  },
  "set.loc.pitch": {
    en: "Used only to find local rooms and events through the community door. Leave it empty and nothing local is searched for.", es: "Se usa solo para encontrar salas y eventos locales a través de la puerta comunitaria. Déjalo vacío y no se buscará nada local.", fr: "Utilisé uniquement pour trouver des salles et événements locaux via la porte communautaire. Laissez vide et rien de local n'est cherché.", de: "Wird nur genutzt, um lokale Räume und Veranstaltungen über die Community-Tür zu finden. Leer lassen, und es wird nichts Lokales gesucht.", pt: "Usado apenas para encontrar salas e eventos locais através da porta comunitária. Deixe vazio e nada local é procurado.", it: "Usato solo per trovare stanze ed eventi locali tramite la porta della community. Lascialo vuoto e non si cerca nulla di locale.", ja: "コミュニティの入口を通じて地元のルームやイベントを探すためだけに使われます。空欄にすれば地元の検索は一切行われません。", zh: "仅用于通过社区入口查找本地房间和活动。留空则不搜索任何本地内容。", hi: "केवल सामुदायिक द्वार से स्थानीय कमरे और आयोजन खोजने के लिए उपयोग होता है। खाली छोड़ें तो कुछ भी स्थानीय नहीं खोजा जाएगा।", ar: "يُستخدم فقط للعثور على الغرف والفعاليات المحلية عبر باب المجتمع. اتركه فارغًا فلا يُبحث عن شيء محلي.",
  },
  "set.loc.ph": {
    en: "Town or city", es: "Pueblo o ciudad", fr: "Ville ou commune", de: "Ort oder Stadt", pt: "Vila ou cidade", it: "Paese o città", ja: "市区町村", zh: "城镇或城市", hi: "क़स्बा या शहर", ar: "بلدة أو مدينة",
  },
  "set.mail": {
    en: "Email delivery", es: "Envío de correo", fr: "Envoi des e-mails", de: "E-Mail-Zustellung", pt: "Envio de email", it: "Recapito email", ja: "メール配送", zh: "邮件投递", hi: "ईमेल वितरण", ar: "تسليم البريد",
  },
  "set.mail.smtp": {
    en: "Mail goes out through {host}{env}. New accounts must verify by email.", es: "El correo sale por {host}{env}. Las cuentas nuevas deben verificarse por email.", fr: "Le courrier part via {host}{env}. Les nouveaux comptes doivent se vérifier par e-mail.", de: "Mail geht über {host}{env} hinaus. Neue Konten müssen sich per E-Mail bestätigen.", pt: "O correio sai por {host}{env}. As contas novas têm de verificar por email.", it: "La posta esce tramite {host}{env}. I nuovi account devono verificarsi via email.", ja: "メールは{host}{env}を通じて送信されます。新規アカウントはメールでの確認が必要です。", zh: "邮件经由{host}{env}发出。新账户须通过邮件验证。", hi: "मेल {host}{env} के ज़रिए जाता है। नए खातों को ईमेल से सत्यापन करना होगा।", ar: "يخرج البريد عبر {host}{env}. على الحسابات الجديدة التحقق بالبريد.",
  },
  "set.mail.none": {
    en: "No mail server configured, so nothing can be emailed — verification messages are written to this app's log and signup on this machine simply goes straight in. Point it at a mail account below to send real verification links. For Gmail, turn on 2-Step Verification and create an App password; paste that here, not your normal password.", es: "No hay servidor de correo configurado, así que no se puede enviar nada por email — los mensajes de verificación se escriben en el registro de esta app y el alta en esta máquina simplemente entra directa. Apúntalo a una cuenta de correo abajo para enviar enlaces de verificación reales. Para Gmail, activa la verificación en dos pasos y crea una contraseña de aplicación; pega esa aquí, no tu contraseña normal.", fr: "Aucun serveur de messagerie configuré, donc rien ne peut être envoyé par e-mail — les messages de vérification sont écrits dans le journal de cette appli et l'inscription sur cette machine passe directement. Pointez-le vers un compte de messagerie ci-dessous pour envoyer de vrais liens de vérification. Pour Gmail, activez la validation en deux étapes et créez un mot de passe d'application ; collez celui-ci ici, pas votre mot de passe habituel.", de: "Kein Mailserver konfiguriert, also kann nichts per E-Mail gesendet werden — Bestätigungsnachrichten landen im Log dieser App, und die Anmeldung auf dieser Maschine geht einfach direkt durch. Richte es unten auf ein Mailkonto, um echte Bestätigungslinks zu senden. Für Gmail: Bestätigung in zwei Schritten einschalten und ein App-Passwort erstellen; füg dieses hier ein, nicht dein normales Passwort.", pt: "Não há servidor de correio configurado, por isso nada pode ser enviado por email — as mensagens de verificação são escritas no registo desta app e o registo nesta máquina entra diretamente. Aponte-o a uma conta de correio abaixo para enviar links de verificação reais. Para o Gmail, ligue a verificação em duas etapas e crie uma palavra-passe de aplicação; cole essa aqui, não a sua palavra-passe normal.", it: "Nessun server di posta configurato, quindi non si può inviare nulla per email — i messaggi di verifica finiscono nel log di questa app e l'iscrizione su questa macchina passa direttamente. Puntalo a un account di posta qui sotto per inviare link di verifica veri. Per Gmail, attiva la verifica in due passaggi e crea una password per le app; incolla quella qui, non la tua password normale.", ja: "メールサーバーが設定されていないため、メールは一切送れません — 確認メッセージはこのアプリのログに書き出され、この端末での登録はそのまま通ります。実際の確認リンクを送るには、下でメールアカウントを指定してください。Gmailの場合は2段階認証を有効にしてアプリパスワードを作成し、通常のパスワードではなくそちらをここに貼り付けてください。", zh: "未配置邮件服务器，因此无法发送任何邮件 — 验证消息会写入本应用的日志，本机上的注册直接通过。请在下方指向一个邮件账户，以发送真实的验证链接。若用 Gmail，请开启两步验证并创建应用专用密码；把那个粘贴到这里，而不是你的常用密码。", hi: "कोई मेल सर्वर कॉन्फ़िगर नहीं है, इसलिए ईमेल से कुछ नहीं भेजा जा सकता — सत्यापन संदेश इस ऐप के लॉग में लिखे जाते हैं और इस मशीन पर साइनअप सीधे हो जाता है। असली सत्यापन लिंक भेजने के लिए नीचे किसी मेल खाते की ओर इंगित करें। Gmail के लिए 2-चरणीय सत्यापन चालू करें और ऐप पासवर्ड बनाएँ; वही यहाँ चिपकाएँ, अपना सामान्य पासवर्ड नहीं।", ar: "لا يوجد خادم بريد مهيأ، فلا يمكن إرسال أي بريد — تُكتب رسائل التحقق في سجل هذا التطبيق ويمر التسجيل على هذه الآلة مباشرة. وجّهه إلى حساب بريد أدناه لإرسال روابط تحقق حقيقية. في Gmail، فعّل التحقق بخطوتين وأنشئ كلمة مرور للتطبيقات؛ والصق تلك هنا لا كلمة مرورك المعتادة.",
  },
  "set.mail.host": {
    en: "Mail server", es: "Servidor de correo", fr: "Serveur de messagerie", de: "Mailserver", pt: "Servidor de correio", it: "Server di posta", ja: "メールサーバー", zh: "邮件服务器", hi: "मेल सर्वर", ar: "خادم البريد",
  },
  "set.mail.host.ph": {
    en: "smtp.gmail.com", es: "smtp.gmail.com", fr: "smtp.gmail.com", de: "smtp.gmail.com", pt: "smtp.gmail.com", it: "smtp.gmail.com", ja: "smtp.gmail.com", zh: "smtp.gmail.com", hi: "smtp.gmail.com", ar: "smtp.gmail.com",
  },
  "set.mail.port": {
    en: "Port", es: "Puerto", fr: "Port", de: "Port", pt: "Porta", it: "Porta", ja: "ポート", zh: "端口", hi: "पोर्ट", ar: "المنفذ",
  },
  "set.mail.user": {
    en: "Username", es: "Usuario", fr: "Nom d'utilisateur", de: "Benutzername", pt: "Utilizador", it: "Nome utente", ja: "ユーザー名", zh: "用户名", hi: "उपयोगकर्ता नाम", ar: "اسم المستخدم",
  },
  "set.mail.user.ph": {
    en: "you@gmail.com", es: "tu@gmail.com", fr: "vous@gmail.com", de: "sie@gmail.com", pt: "voce@gmail.com", it: "tu@gmail.com", ja: "you@gmail.com", zh: "you@gmail.com", hi: "aap@gmail.com", ar: "you@gmail.com",
  },
  "set.mail.pass": {
    en: "Password", es: "Contraseña", fr: "Mot de passe", de: "Passwort", pt: "Palavra-passe", it: "Password", ja: "パスワード", zh: "密码", hi: "पासवर्ड", ar: "كلمة المرور",
  },
  "set.mail.saved": {
    en: "(saved — type to replace)", es: "(guardada — escribe para reemplazar)", fr: "(enregistré — tapez pour remplacer)", de: "(gespeichert — tippen zum Ersetzen)", pt: "(guardada — escreva para substituir)", it: "(salvata — digita per sostituire)", ja: "（保存済み — 入力すると置き換わります）", zh: "（已保存 — 输入即替换）", hi: "(सहेजा गया — बदलने के लिए टाइप करें)", ar: "(محفوظة — اكتب للاستبدال)",
  },
  "set.mail.pass.ph": {
    en: "app password", es: "contraseña de aplicación", fr: "mot de passe d'application", de: "App-Passwort", pt: "palavra-passe de aplicação", it: "password per le app", ja: "アプリパスワード", zh: "应用专用密码", hi: "ऐप पासवर्ड", ar: "كلمة مرور التطبيق",
  },
  "set.mail.from": {
    en: "From address", es: "Dirección de remite", fr: "Adresse d'expéditeur", de: "Absenderadresse", pt: "Endereço de remetente", it: "Indirizzo mittente", ja: "差出人アドレス", zh: "发件地址", hi: "प्रेषक पता", ar: "عنوان المرسل",
  },
  "set.mail.link": {
    en: "Link address", es: "Dirección de los enlaces", fr: "Adresse des liens", de: "Link-Adresse", pt: "Endereço dos links", it: "Indirizzo dei link", ja: "リンクのアドレス", zh: "链接地址", hi: "लिंक पता", ar: "عنوان الروابط",
  },
  "set.mail.link.note": {
    en: "— what verification links point at", es: "— adónde apuntan los enlaces de verificación", fr: "— où pointent les liens de vérification", de: "— worauf Verifizierungslinks zeigen", pt: "— para onde apontam os links de verificação", it: "— dove puntano i link di verifica", ja: "— 確認リンクの宛先", zh: "— 验证链接指向何处", hi: "— सत्यापन लिंक कहाँ इंगित करते हैं", ar: "— إلى أين تشير روابط التحقق",
  },
  "set.mail.link.ph": {
    en: "http://127.0.0.1:8000", es: "http://127.0.0.1:8000", fr: "http://127.0.0.1:8000", de: "http://127.0.0.1:8000", pt: "http://127.0.0.1:8000", it: "http://127.0.0.1:8000", ja: "http://127.0.0.1:8000", zh: "http://127.0.0.1:8000", hi: "http://127.0.0.1:8000", ar: "http://127.0.0.1:8000",
  },
  "set.mail.test": {
    en: "Send a test message to", es: "Enviar un mensaje de prueba a", fr: "Envoyer un message de test à", de: "Testnachricht senden an", pt: "Enviar mensagem de teste para", it: "Invia un messaggio di prova a", ja: "テストメッセージの宛先", zh: "发送测试邮件至", hi: "परीक्षण संदेश भेजें", ar: "أرسل رسالة اختبار إلى",
  },
  "set.mail.test.ph": {
    en: "you@example.com", es: "tu@example.com", fr: "vous@example.com", de: "sie@example.com", pt: "voce@example.com", it: "tu@example.com", ja: "you@example.com", zh: "you@example.com", hi: "aap@example.com", ar: "you@example.com",
  },
  "set.model": {
    en: "Which model answers", es: "Qué modelo responde", fr: "Quel modèle répond", de: "Welches Modell antwortet", pt: "Que modelo responde", it: "Quale modello risponde", ja: "どのモデルが答えるか", zh: "由哪个模型作答", hi: "कौन-सा मॉडल जवाब देता है", ar: "أي نموذج يجيب",
  },
  "set.model.pitch": {
    en: "Your Guardian's replies can run on any of these. Pick one and every reply uses it; Automatic uses whichever is configured.", es: "Las respuestas de tu Guardián pueden correr en cualquiera de estos. Elige uno y todas las respuestas lo usan; Automático usa el que esté configurado.", fr: "Les réponses de votre Gardien peuvent tourner sur n'importe lequel. Choisissez-en un et chaque réponse l'utilise ; Automatique utilise celui qui est configuré.", de: "Die Antworten deines Guardians können auf jedem davon laufen. Wähl eines, und jede Antwort nutzt es; Automatisch nutzt das jeweils Konfigurierte.", pt: "As respostas do seu Guardião podem correr em qualquer um destes. Escolha um e todas as respostas o usam; Automático usa o que estiver configurado.", it: "Le risposte del tuo Guardian possono girare su uno qualsiasi. Scegline uno e ogni risposta lo usa; Automatico usa quello configurato.", ja: "ガーディアンの返答はどれでも動かせます。選べばすべての返答がそれを使い、「自動」は設定済みのものを使います。", zh: "你的守护者的回复可运行在任一模型上。选定后每条回复都用它；「自动」使用已配置的模型。", hi: "आपके गार्जियन के जवाब इनमें से किसी पर चल सकते हैं। एक चुनें और हर जवाब उसी का उपयोग करेगा; स्वचालित जो कॉन्फ़िगर है उसे लेता है।", ar: "يمكن أن تعمل ردود حارسك على أي منها. اختر واحدًا فتستخدمه كل الردود؛ التلقائي يستخدم ما هو مهيأ.",
  },
  "set.model.stub": {
    en: "⚠ Right now replies come from the built-in offline helper — no online model has a working key on this machine. Pick a provider above and add its key (“Your model API key” below works for all of them).", es: "⚠ Ahora mismo las respuestas vienen del asistente offline integrado — ningún modelo en línea tiene clave válida en esta máquina. Elige un proveedor arriba y añade su clave («Tu clave de API del modelo», abajo, sirve para todos).", fr: "⚠ En ce moment, les réponses viennent de l'assistant hors ligne intégré — aucun modèle en ligne n'a de clé valide sur cette machine. Choisissez un fournisseur ci-dessus et ajoutez sa clé (« Votre clé d'API du modèle », plus bas, vaut pour tous).", de: "⚠ Derzeit kommen Antworten vom eingebauten Offline-Helfer — kein Online-Modell hat auf dieser Maschine einen gültigen Schlüssel. Wähl oben einen Anbieter und füg dessen Schlüssel hinzu (»Dein Modell-API-Schlüssel« unten gilt für alle).", pt: "⚠ Neste momento as respostas vêm do assistente offline integrado — nenhum modelo online tem chave válida nesta máquina. Escolha um fornecedor acima e adicione a sua chave («A sua chave de API do modelo», abaixo, serve para todos).", it: "⚠ In questo momento le risposte vengono dall'assistente offline integrato — nessun modello online ha una chiave valida su questa macchina. Scegli un provider sopra e aggiungi la sua chiave («La tua chiave API del modello», qui sotto, vale per tutti).", ja: "⚠ 現在の返答は内蔵オフラインヘルパーからです — このマシンで有効なキーを持つオンラインモデルがありません。上でプロバイダーを選び、キーを追加してください（下の「あなたのモデルAPIキー」がすべてに使えます）。", zh: "⚠ 当前回复来自内置离线助手 — 本机上没有任何在线模型持有有效密钥。请在上方选择提供方并添加其密钥（下方的「你的模型 API 密钥」对所有提供方都适用）。", hi: "⚠ अभी जवाब अंतर्निहित ऑफ़लाइन सहायक से आ रहे हैं — इस मशीन पर किसी ऑनलाइन मॉडल की कुंजी नहीं है। ऊपर प्रदाता चुनें और उसकी कुंजी जोड़ें (नीचे «आपकी मॉडल API कुंजी» सभी के लिए काम करती है)।", ar: "⚠ الردود الآن من المساعد المدمج دون اتصال — لا يملك أي نموذج متصل مفتاحًا صالحًا على هذه الآلة. اختر مزودًا أعلاه وأضف مفتاحه («مفتاح واجهة النموذج الخاص بك» أدناه يصلح لها جميعًا).",
  },
  "set.model.resolves": {
    en: "⚠ Right now it resolves to {effective} — the one you picked has no key on this machine yet.", es: "⚠ Ahora mismo se resuelve a {effective} — el que elegiste aún no tiene clave en esta máquina.", fr: "⚠ En ce moment, cela se résout en {effective} — celui que vous avez choisi n'a pas encore de clé sur cette machine.", de: "⚠ Derzeit löst es zu {effective} auf — das gewählte hat auf dieser Maschine noch keinen Schlüssel.", pt: "⚠ Neste momento resolve para {effective} — o que escolheu ainda não tem chave nesta máquina.", it: "⚠ In questo momento si risolve in {effective} — quello scelto non ha ancora una chiave su questa macchina.", ja: "⚠ 現在は{effective}に解決されます — 選んだものはまだこのマシンにキーがありません。", zh: "⚠ 当前解析为{effective} — 你选的那个在本机上还没有密钥。", hi: "⚠ अभी यह {effective} पर हल होता है — आपके चुने हुए की इस मशीन पर अभी कुंजी नहीं है।", ar: "⚠ الآن يُحل إلى {effective} — الذي اخترته لا مفتاح له على هذه الآلة بعد.",
  },
  "set.voice": {
    en: "Voice", es: "Voz", fr: "Voix", de: "Stimme", pt: "Voz", it: "Voce", ja: "音声", zh: "语音", hi: "आवाज़", ar: "الصوت",
  },
  "set.voice.device": {
    en: "Replies are read aloud in your device's own voice — no account needed. Add an ElevenLabs or OpenAI key for a natural one, and to talk back by microphone.", es: "Las respuestas se leen en voz alta con la voz propia de tu dispositivo — sin cuenta. Añade una clave de ElevenLabs u OpenAI para una voz natural, y para responder por micrófono.", fr: "Les réponses sont lues à voix haute avec la voix de votre appareil — aucun compte nécessaire. Ajoutez une clé ElevenLabs ou OpenAI pour une voix naturelle, et pour répondre au micro.", de: "Antworten werden mit der geräteeigenen Stimme vorgelesen — ohne Konto. Füg einen ElevenLabs- oder OpenAI-Schlüssel hinzu für eine natürliche Stimme und um per Mikrofon zu antworten.", pt: "As respostas são lidas em voz alta com a voz do seu dispositivo — sem conta. Adicione uma chave ElevenLabs ou OpenAI para uma voz natural, e para responder por microfone.", it: "Le risposte sono lette ad alta voce con la voce del tuo dispositivo — nessun account necessario. Aggiungi una chiave ElevenLabs o OpenAI per una voce naturale, e per rispondere al microfono.", ja: "返答は端末自身の音声で読み上げられます — アカウントは不要です。自然な声とマイクでの応答には、ElevenLabsまたはOpenAIのキーを追加してください。", zh: "回复会用你设备自带的语音朗读 — 无需账户。添加 ElevenLabs 或 OpenAI 密钥即可获得自然嗓音，并可用麦克风回话。", hi: "जवाब आपके डिवाइस की अपनी आवाज़ में पढ़े जाते हैं — कोई खाता नहीं चाहिए। प्राकृतिक आवाज़ और माइक से जवाब देने के लिए ElevenLabs या OpenAI कुंजी जोड़ें।", ar: "تُقرأ الردود بصوت جهازك نفسه — دون حاجة لحساب. أضف مفتاح ElevenLabs أو OpenAI لصوت طبيعي وللرد بالميكروفون.",
  },
  "set.voice.through": {
    en: "Speaking through {provider}{env}. Talking back by microphone works too.", es: "Hablando a través de {provider}{env}. Responder por micrófono también funciona.", fr: "Parle via {provider}{env}. Répondre au micro fonctionne aussi.", de: "Spricht über {provider}{env}. Antworten per Mikrofon geht auch.", pt: "A falar através de {provider}{env}. Responder por microfone também funciona.", it: "Parla tramite {provider}{env}. Rispondere al microfono funziona anche.", ja: "{provider}{env}を通じて話します。マイクでの応答も使えます。", zh: "通过{provider}{env}发声。用麦克风回话同样可用。", hi: "{provider}{env} के ज़रिए बोल रहा है। माइक से जवाब देना भी चलता है।", ar: "يتحدث عبر {provider}{env}. والرد بالميكروفون يعمل أيضًا.",
  },
  "set.voice.hear": {
    en: "Hear it", es: "Escucharla", fr: "L'écouter", de: "Anhören", pt: "Ouvi-la", it: "Ascoltala", ja: "聞いてみる", zh: "听听看", hi: "सुनें", ar: "استمع إليه",
  },
  "set.watch.unreach": {
    en: "⚠ Your phone can't reach this address yet — JIM is only listening on this computer.", es: "⚠ Tu teléfono aún no puede alcanzar esta dirección — JIM solo escucha en este ordenador.", fr: "⚠ Votre téléphone ne peut pas encore atteindre cette adresse — JIM n'écoute que sur cet ordinateur.", de: "⚠ Dein Telefon erreicht diese Adresse noch nicht — JIM lauscht nur auf diesem Computer.", pt: "⚠ O seu telefone ainda não alcança este endereço — o JIM só escuta neste computador.", it: "⚠ Il tuo telefono non raggiunge ancora questo indirizzo — JIM ascolta solo su questo computer.", ja: "⚠ このアドレスにはまだスマートフォンから届きません — JIMはこのコンピューター上でのみ待ち受けています。", zh: "⚠ 你的手机还无法访问此地址 — JIM 只在这台电脑上监听。", hi: "⚠ आपका फ़ोन अभी इस पते तक नहीं पहुँच सकता — JIM केवल इसी कंप्यूटर पर सुन रहा है।", ar: "⚠ لا يستطيع هاتفك بلوغ هذا العنوان بعد — JIM يستمع على هذا الحاسوب فقط.",
  },
  "set.watch.lan": {
    en: "Let my phone reach JIM on this Wi-Fi", es: "Permitir que mi teléfono alcance a JIM en esta Wi-Fi", fr: "Laisser mon téléphone joindre JIM sur ce Wi-Fi", de: "Mein Telefon JIM in diesem WLAN erreichen lassen", pt: "Deixar o meu telefone alcançar o JIM nesta Wi-Fi", it: "Fai raggiungere JIM al mio telefono su questa Wi-Fi", ja: "このWi-FiでスマートフォンからJIMに届くようにする", zh: "让我的手机在此 Wi-Fi 上访问 JIM", hi: "मेरे फ़ोन को इस Wi-Fi पर JIM तक पहुँचने दें", ar: "دع هاتفي يصل إلى JIM على شبكة Wi-Fi هذه",
  },
  "set.watch.lan.note": {
    en: "Restarts JIM listening on your network. Windows may ask to allow it through the firewall — say yes. Everything personal still requires your sign-in.", es: "Reinicia JIM escuchando en tu red. Windows puede pedir permiso en el cortafuegos — di que sí. Todo lo personal sigue requiriendo tu inicio de sesión.", fr: "Redémarre JIM en écoute sur votre réseau. Windows peut demander à l'autoriser dans le pare-feu — dites oui. Tout ce qui est personnel exige toujours votre connexion.", de: "Startet JIM neu, lauschend in deinem Netzwerk. Windows fragt womöglich nach einer Firewall-Freigabe — sag ja. Alles Persönliche verlangt weiterhin deine Anmeldung.", pt: "Reinicia o JIM a escutar na sua rede. O Windows pode pedir para o permitir na firewall — diga que sim. Tudo o que é pessoal continua a exigir a sua sessão iniciada.", it: "Riavvia JIM in ascolto sulla tua rete. Windows potrebbe chiedere di consentirlo nel firewall — di' di sì. Tutto ciò che è personale richiede ancora il tuo accesso.", ja: "JIMをネットワーク上で待ち受ける形で再起動します。Windowsがファイアウォールの許可を尋ねたら「はい」を選んでください。個人的なものはすべて、引き続きサインインが必要です。", zh: "重启 JIM 使其在你的网络上监听。Windows 可能会请求放行防火墙 — 请选择允许。所有个人内容仍需你登录。", hi: "JIM को आपके नेटवर्क पर सुनते हुए पुनः शुरू करता है। Windows फ़ायरवॉल से अनुमति माँग सकता है — हाँ कहें। सब कुछ निजी अब भी आपके साइन-इन की माँग करता है।", ar: "يعيد تشغيل JIM ليستمع على شبكتك. قد يطلب Windows السماح له عبر الجدار الناري — وافق. وكل ما هو شخصي ما زال يتطلب تسجيل دخولك.",
  },
  "set.watch.cli": {
    en: "Start the backend with network access: python -m jim phone", es: "Arranca el servidor con acceso de red: python -m jim phone", fr: "Démarrez le serveur avec accès réseau : python -m jim phone", de: "Backend mit Netzwerkzugriff starten: python -m jim phone", pt: "Inicie o servidor com acesso de rede: python -m jim phone", it: "Avvia il backend con accesso di rete: python -m jim phone", ja: "ネットワークアクセス付きでバックエンドを起動: python -m jim phone", zh: "以网络访问方式启动后端: python -m jim phone", hi: "बैकएंड को नेटवर्क पहुँच के साथ शुरू करें: python -m jim phone", ar: "شغّل الخادم مع وصول الشبكة: python -m jim phone",
  },
  "set.watch.ok": {
    en: "✓ Reachable from your phone on this Wi-Fi.", es: "✓ Accesible desde tu teléfono en esta Wi-Fi.", fr: "✓ Joignable depuis votre téléphone sur ce Wi-Fi.", de: "✓ Von deinem Telefon in diesem WLAN erreichbar.", pt: "✓ Acessível do seu telefone nesta Wi-Fi.", it: "✓ Raggiungibile dal tuo telefono su questa Wi-Fi.", ja: "✓ このWi-Fiでスマートフォンから到達できます。", zh: "✓ 在此 Wi-Fi 上可从你的手机访问。", hi: "✓ इस Wi-Fi पर आपके फ़ोन से पहुँच योग्य।", ar: "✓ يمكن الوصول إليه من هاتفك على هذه الشبكة.",
  },
  "set.watch.newaddr": {
    en: "New address", es: "Nueva dirección", fr: "Nouvelle adresse", de: "Neue Adresse", pt: "Novo endereço", it: "Nuovo indirizzo", ja: "新しいアドレス", zh: "新地址", hi: "नया पता", ar: "عنوان جديد",
  },
  "set.watch.received": {
    en: "Received {n} reading{s} · last {when}", es: "Recibidas {n} lecturas · última {when}", fr: "{n} mesures reçues · dernière {when}", de: "{n} Messungen empfangen · zuletzt {when}", pt: "Recebidas {n} leituras · última {when}", it: "Ricevute {n} letture · ultima {when}", ja: "測定値{n}件を受信 · 最終 {when}", zh: "已收到{n}条读数 · 最近 {when}", hi: "{n} रीडिंग प्राप्त · अंतिम {when}", ar: "استُلمت {n} قراءات · آخرها {when}",
  },
  "set.watch.signin": {
    en: "Sign in to mint your drip address.", es: "Inicia sesión para acuñar tu dirección de goteo.", fr: "Connectez-vous pour créer votre adresse de goutte-à-goutte.", de: "Meld dich an, um deine Drip-Adresse zu prägen.", pt: "Inicie sessão para cunhar o seu endereço de gotejamento.", it: "Accedi per coniare il tuo indirizzo drip.", ja: "サインインしてドリップアドレスを発行してください。", zh: "登录以生成你的滴流地址。", hi: "अपना ड्रिप पता बनाने के लिए साइन इन करें।", ar: "سجّل الدخول لإنشاء عنوان التقطير الخاص بك.",
  },
  "set.watch.seeded": {
    en: "{metric}: {d} day{s} folded, baseline {b}{tail}", es: "{metric}: {d} días incorporados, línea base {b}{tail}", fr: "{metric} : {d} jours intégrés, ligne de base {b}{tail}", de: "{metric}: {d} Tage eingearbeitet, Basislinie {b}{tail}", pt: "{metric}: {d} dias incorporados, linha de base {b}{tail}", it: "{metric}: {d} giorni integrati, linea di base {b}{tail}", ja: "{metric}: {d}日分を取り込み、ベースライン {b}{tail}", zh: "{metric}: 已并入{d}天，基线 {b}{tail}", hi: "{metric}: {d} दिन समेटे गए, आधार रेखा {b}{tail}", ar: "{metric}: أُدمج {d} أيام، الخط الأساسي {b}{tail}",
  },
  "set.vigil": {
    en: "The vigil", es: "La vigilia", fr: "La veille", de: "Die Wache", pt: "A vigília", it: "La veglia", ja: "見守り", zh: "守夜", hi: "पहरा", ar: "السهر",
  },
  "set.vigil.pitch": {
    en: "Every other alarm fires on a reading. This one fires on the absence of readings: name someone, and if nothing is heard from you for longer than the quiet period, they are asked to check on you. Any reading stands it down. It never calls emergency services — it knocks on a door.", es: "Todas las demás alarmas se disparan por una lectura. Esta se dispara por la ausencia de lecturas: nombra a alguien, y si no se sabe nada de ti durante más tiempo que el periodo de silencio, se le pide que vaya a ver cómo estás. Cualquier lectura la desactiva. Nunca llama a los servicios de emergencia — llama a una puerta.", fr: "Toutes les autres alertes se déclenchent sur une mesure. Celle-ci se déclenche sur l'absence de mesures : nommez quelqu'un, et si l'on n'a rien de vous plus longtemps que la période de silence, on lui demande de prendre de vos nouvelles. Toute mesure la lève. Elle n'appelle jamais les secours — elle frappe à une porte.", de: "Jeder andere Alarm löst auf eine Messung hin aus. Dieser löst auf das Ausbleiben von Messungen hin aus: nenn jemanden, und hört man länger als die Stillperiode nichts von dir, wird diese Person gebeten, nach dir zu sehen. Jede Messung stellt ihn zurück. Er ruft nie den Rettungsdienst — er klopft an eine Tür.", pt: "Todos os outros alarmes disparam com uma leitura. Este dispara com a ausência de leituras: nomeie alguém, e se nada se souber de si por mais tempo do que o período de silêncio, pedem-lhe que veja como está. Qualquer leitura o desativa. Nunca chama os serviços de emergência — bate a uma porta.", it: "Ogni altro allarme scatta su una lettura. Questo scatta sull'assenza di letture: nomina qualcuno, e se non si sa nulla di te per più del periodo di silenzio, gli si chiede di venire a vedere come stai. Qualsiasi lettura lo rientra. Non chiama mai i soccorsi — bussa a una porta.", ja: "他のあらゆる警報は測定値によって鳴ります。これは測定値がないことによって鳴ります：誰かを指名しておくと、静穏期間を超えてあなたから何の知らせもない場合、その人に様子を見に行くよう頼まれます。どんな測定値でも解除されます。救急を呼ぶことは決してなく — 扉を叩くだけです。", zh: "其他所有警报都因某条读数而触发。这一个因读数的缺席而触发：指定一个人，若超过静默期仍未收到你的任何消息，就会请他来看看你。任何读数都会将其解除。它绝不呼叫急救 — 它只是去敲一扇门。", hi: "बाक़ी हर अलार्म किसी रीडिंग पर बजता है। यह रीडिंग की अनुपस्थिति पर बजता है: किसी का नाम दें, और यदि शांत अवधि से अधिक समय तक आपका कोई हाल न मिले, तो उनसे आपकी ख़बर लेने को कहा जाता है। कोई भी रीडिंग इसे शांत कर देती है। यह कभी आपातकालीन सेवाएँ नहीं बुलाता — यह एक दरवाज़ा खटखटाता है।", ar: "كل إنذار آخر ينطلق بقراءة. هذا ينطلق بغياب القراءات: سمِّ شخصًا، وإن لم يُسمع عنك شيء أطول من فترة الصمت، يُطلب منه أن يطمئن عليك. وأي قراءة تُعيده. لا يستدعي الطوارئ أبدًا — بل يطرق بابًا.",
  },
  "set.vigil.tripped": {
    en: "⚠ The vigil has tripped — {name} was asked to check on you{after}.", es: "⚠ La vigilia se ha disparado — se pidió a {name} que fuera a ver cómo estás{after}.", fr: "⚠ La veille s'est déclenchée — on a demandé à {name} de prendre de vos nouvelles{after}.", de: "⚠ Die Wache hat ausgelöst — {name} wurde gebeten, nach dir zu sehen{after}.", pt: "⚠ A vigília disparou — pediram a {name} que visse como está{after}.", it: "⚠ La veglia è scattata — è stato chiesto a {name} di venire a vedere come stai{after}.", ja: "⚠ 見守りが作動しました — {name}にあなたの様子を見るよう依頼しました{after}。", zh: "⚠ 守夜已触发 — 已请{name}来看看你{after}。", hi: "⚠ पहरा सक्रिय हुआ — {name} से आपकी ख़बर लेने को कहा गया{after}।", ar: "⚠ انطلق السهر — طُلب من {name} أن يطمئن عليك{after}.",
  },
  "set.vigil.after": {
    en: " after {n} quiet days", es: " tras {n} días de silencio", fr: " après {n} jours de silence", de: " nach {n} stillen Tagen", pt: " após {n} dias de silêncio", it: " dopo {n} giorni di silenzio", ja: "（静穏{n}日ののち）", zh: "（在{n}天静默之后）", hi: " {n} शांत दिनों के बाद", ar: " بعد {n} أيام من الصمت",
  },
  "set.vigil.okay": {
    en: "I'm okay", es: "Estoy bien", fr: "Ça va", de: "Mir geht es gut", pt: "Estou bem", it: "Sto bene", ja: "大丈夫です", zh: "我没事", hi: "मैं ठीक हूँ", ar: "أنا بخير",
  },
  "set.vigil.name": {
    en: "Steward's name", es: "Nombre de la persona de guardia", fr: "Nom de la personne de confiance", de: "Name des Verwalters", pt: "Nome do guardião", it: "Nome del custode", ja: "見守り役の名前", zh: "受托人姓名", hi: "संरक्षक का नाम", ar: "اسم القيّم",
  },
  "set.vigil.name.ph": {
    en: "Who to tell", es: "A quién avisar", fr: "Qui prévenir", de: "Wem Bescheid geben", pt: "A quem avisar", it: "Chi avvisare", ja: "誰に知らせるか", zh: "该通知谁", hi: "किसे बताना है", ar: "من تُخبر",
  },
  "set.vigil.reach": {
    en: "How to reach them", es: "Cómo contactarle", fr: "Comment la joindre", de: "Wie man sie erreicht", pt: "Como contactá-lo", it: "Come raggiungerlo", ja: "連絡方法", zh: "如何联系", hi: "उन तक कैसे पहुँचें", ar: "كيف تصل إليه",
  },
  "set.vigil.reach.ph": {
    en: "their@email.com", es: "su@email.com", fr: "son@email.com", de: "ihre@email.com", pt: "dele@email.com", it: "suo@email.com", ja: "their@email.com", zh: "their@email.com", hi: "unka@email.com", ar: "their@email.com",
  },
  "set.vigil.days": {
    en: "Quiet days before they're told", es: "Días de silencio antes de avisarle", fr: "Jours de silence avant qu'on la prévienne", de: "Stille Tage, bevor Bescheid gegeben wird", pt: "Dias de silêncio antes de o avisarem", it: "Giorni di silenzio prima di avvisarlo", ja: "知らせるまでの静穏日数", zh: "通知前的静默天数", hi: "बताने से पहले शांत दिन", ar: "أيام الصمت قبل إخباره",
  },
  "set.vigil.words": {
    en: "In your own words", es: "Con tus palabras", fr: "Avec vos mots", de: "In deinen eigenen Worten", pt: "Nas suas palavras", it: "Con parole tue", ja: "自分の言葉で", zh: "用你自己的话", hi: "अपने शब्दों में", ar: "بكلماتك أنت",
  },
  "set.vigil.words.note": {
    en: "— what they'll read, written now", es: "— lo que leerá, escrito ahora", fr: "— ce qu'elle lira, écrit maintenant", de: "— was sie lesen wird, jetzt geschrieben", pt: "— o que ele lerá, escrito agora", it: "— ciò che leggerà, scritto ora", ja: "— その人が読む言葉を、いま書いておく", zh: "— 他将读到的内容，此刻写下", hi: "— वे क्या पढ़ेंगे, अभी लिखा हुआ", ar: "— ما سيقرؤه، مكتوبًا الآن",
  },
  "set.vigil.words.ph": {
    en: "I live alone — please knock.", es: "Vivo solo — llama a la puerta, por favor.", fr: "Je vis seul — frappez, s'il vous plaît.", de: "Ich lebe allein — bitte klopf.", pt: "Vivo sozinho — por favor bata à porta.", it: "Vivo da solo — bussa, per favore.", ja: "一人暮らしです — どうか扉を叩いてください。", zh: "我独自居住 — 请敲门。", hi: "मैं अकेला रहता हूँ — कृपया दरवाज़ा खटखटाएँ।", ar: "أعيش وحدي — من فضلك اطرق الباب.",
  },
  "set.vigil.disarm": {
    en: "Disarm", es: "Desactivar", fr: "Désarmer", de: "Entschärfen", pt: "Desarmar", it: "Disattiva", ja: "解除する", zh: "停用", hi: "निष्क्रिय करें", ar: "ألغِ التفعيل",
  },
  "set.vigil.check": {
    en: "Just check it", es: "Solo comprobarla", fr: "Juste vérifier", de: "Nur nachsehen", pt: "Só verificar", it: "Solo controlla", ja: "確認するだけ", zh: "只查看", hi: "बस जाँच लें", ar: "تفقّده فقط",
  },
  "set.vigil.armed": {
    en: "Armed · last heard from you {when} · steward: {name}", es: "Activada · última señal tuya {when} · persona de guardia: {name}", fr: "Armée · dernières nouvelles de vous {when} · personne de confiance : {name}", de: "Scharf · zuletzt von dir gehört {when} · Verwalter: {name}", pt: "Ativada · última notícia sua {when} · guardião: {name}", it: "Attiva · ultime tue notizie {when} · custode: {name}", ja: "作動中 · 最後の便り {when} · 見守り役: {name}", zh: "已启用 · 最近一次得知你的消息 {when} · 受托人: {name}", hi: "सक्रिय · आपकी अंतिम ख़बर {when} · संरक्षक: {name}", ar: "مفعّل · آخر خبر عنك {when} · القيّم: {name}",
  },
  "med.add.button": {
    en: "Add to the cabinet", es: "Añadir al botiquín", fr: "Ajouter à l'armoire", de: "Zum Schrank hinzufügen", pt: "Adicionar ao armário", it: "Aggiungi all'armadietto", ja: "薬箱に追加", zh: "加入药柜", hi: "कैबिनेट में जोड़ें", ar: "أضف إلى الخزانة",
  },
  "med.critical.mark": {
    en: " · critical", es: " · crítico", fr: " · critique", de: " · kritisch", pt: " · crítico", it: " · critico", ja: " · 重要", zh: " · 关键", hi: " · अत्यावश्यक", ar: " · حرج",
  },
  "med.title": {
    en: "Medications", es: "Medicamentos", fr: "Médicaments", de: "Medikamente", pt: "Medicamentos", it: "Farmaci", ja: "薬", zh: "药物", hi: "दवाइयाँ", ar: "الأدوية",
  },
  "med.missed": {
    en: "⚠ {list} — marked critical and not logged today. If you took it, tap it below; if you didn't, that's worth a moment.", es: "⚠ {list} — marcados como críticos y sin registrar hoy. Si lo tomaste, tócalo abajo; si no, merece un momento.", fr: "⚠ {list} — marqués critiques et non consignés aujourd'hui. Si vous l'avez pris, touchez-le ci-dessous ; sinon, cela mérite un instant.", de: "⚠ {list} — als kritisch markiert und heute nicht erfasst. Wenn du es genommen hast, tipp unten darauf; wenn nicht, ist das einen Moment wert.", pt: "⚠ {list} — marcados como críticos e não registados hoje. Se o tomou, toque abaixo; se não, isso merece um momento.", it: "⚠ {list} — segnati come critici e non registrati oggi. Se l'hai preso, toccalo qui sotto; se no, vale un momento.", ja: "⚠ {list} — 重要と設定されていますが、今日はまだ記録がありません。飲んだなら下でタップを、飲んでいないなら少し立ち止まる価値があります。", zh: "⚠ {list} — 已标为关键，今天尚未记录。若你已服用，请在下方点选；若没有，这值得停下来想一想。", hi: "⚠ {list} — महत्वपूर्ण चिह्नित है और आज दर्ज नहीं हुआ। अगर आपने लिया है तो नीचे टैप करें; नहीं लिया तो यह एक पल ठहरने लायक़ है।", ar: "⚠ {list} — مُعلَّم كحرج ولم يُسجَّل اليوم. إن كنت تناولته فانقره أدناه؛ وإن لم تفعل، فالأمر يستحق لحظة.",
  },
  "med.today": {
    en: "Today", es: "Hoy", fr: "Aujourd'hui", de: "Heute", pt: "Hoje", it: "Oggi", ja: "今日", zh: "今天", hi: "आज", ar: "اليوم",
  },
  "med.none": {
    en: "Nothing here yet — add what you take below, in your own words.", es: "Aquí no hay nada todavía — añade abajo lo que tomas, con tus palabras.", fr: "Rien ici pour l'instant — ajoutez ci-dessous ce que vous prenez, avec vos mots.", de: "Hier ist noch nichts — füg unten hinzu, was du nimmst, in deinen eigenen Worten.", pt: "Ainda não há nada aqui — adicione abaixo o que toma, nas suas palavras.", it: "Qui non c'è ancora niente — aggiungi sotto ciò che prendi, con parole tue.", ja: "まだ何もありません — 服用しているものを、自分の言葉で下に追加してください。", zh: "这里还什么都没有 — 在下方用你自己的话添加你所服用的药。", hi: "यहाँ अभी कुछ नहीं — नीचे अपने शब्दों में जोड़ें कि आप क्या लेते हैं।", ar: "لا شيء هنا بعد — أضف أدناه ما تتناوله، بكلماتك أنت.",
  },
  "med.stop": {
    en: "stop", es: "dejar", fr: "arrêter", de: "beenden", pt: "parar", it: "smetti", ja: "中止", zh: "停止", hi: "रोकें", ar: "أوقف",
  },
  "med.take": {
    en: "Take", es: "Tomar", fr: "Prendre", de: "Nehmen", pt: "Tomar", it: "Prendi", ja: "服用", zh: "服用", hi: "लें", ar: "تناول",
  },
  "med.skip": {
    en: "Skip", es: "Saltar", fr: "Passer", de: "Auslassen", pt: "Saltar", it: "Salta", ja: "スキップ", zh: "跳过", hi: "छोड़ें", ar: "تخطَّ",
  },
  "med.actually": {
    en: "Actually took it", es: "En realidad sí lo tomé", fr: "En fait, je l'ai pris", de: "Doch genommen", pt: "Afinal tomei-o", it: "In realtà l'ho preso", ja: "やはり飲みました", zh: "其实我服用了", hi: "असल में ले लिया था", ar: "تناولته فعلًا",
  },
  "med.asneeded.line": {
    en: "as needed · {n} today{max}", es: "según necesidad · {n} hoy{max}", fr: "au besoin · {n} aujourd'hui{max}", de: "bei Bedarf · {n} heute{max}", pt: "conforme necessário · {n} hoje{max}", it: "al bisogno · {n} oggi{max}", ja: "頓用 · 今日{n}回{max}", zh: "按需 · 今天{n}次{max}", hi: "आवश्यकतानुसार · आज {n}{max}", ar: "عند الحاجة · {n} اليوم{max}",
  },
  "med.asneeded.max": {
    en: " of {max} max", es: " de {max} máx.", fr: " sur {max} max", de: " von {max} max.", pt: " de {max} máx.", it: " su {max} max", ja: "（上限{max}回）", zh: "（上限{max}次）", hi: " अधिकतम {max} में से", ar: " من أصل {max} كحد أقصى",
  },
  "med.tookone": {
    en: "Took one", es: "Tomé una", fr: "J'en ai pris un", de: "Eine genommen", pt: "Tomei um", it: "Ne ho preso uno", ja: "1回飲んだ", zh: "服用了一次", hi: "एक ले ली", ar: "تناولت واحدة",
  },
  "med.last": {
    en: "Last {n} days", es: "Últimos {n} días", fr: "Ces {n} derniers jours", de: "Letzte {n} Tage", pt: "Últimos {n} dias", it: "Ultimi {n} giorni", ja: "直近{n}日間", zh: "最近{n}天", hi: "पिछले {n} दिन", ar: "آخر {n} أيام",
  },
  "med.of": {
    en: "{taken} of {expected}", es: "{taken} de {expected}", fr: "{taken} sur {expected}", de: "{taken} von {expected}", pt: "{taken} de {expected}", it: "{taken} su {expected}", ja: "{expected}回中{taken}回", zh: "{expected}次中{taken}次", hi: "{expected} में से {taken}", ar: "{taken} من {expected}",
  },
  "med.add": {
    en: "Add a medication", es: "Añadir un medicamento", fr: "Ajouter un médicament", de: "Ein Medikament hinzufügen", pt: "Adicionar um medicamento", it: "Aggiungi un farmaco", ja: "薬を追加", zh: "添加一种药", hi: "दवा जोड़ें", ar: "أضف دواءً",
  },
  "med.add.pitch": {
    en: "Your words are fine — “the little white one, 10 mg” is a valid name and dose.", es: "Tus palabras valen — «la blanquita, 10 mg» es un nombre y una dosis válidos.", fr: "Vos mots suffisent — « le petit blanc, 10 mg » est un nom et une dose valables.", de: "Deine Worte genügen — »die kleine weiße, 10 mg« ist ein gültiger Name und eine gültige Dosis.", pt: "As suas palavras servem — «o branquinho, 10 mg» é um nome e uma dose válidos.", it: "Le tue parole vanno bene — «quella bianca piccola, 10 mg» è un nome e una dose validi.", ja: "あなたの言葉で構いません — 「小さい白いの、10 mg」も立派な名前と用量です。", zh: "用你自己的话就好 — 「那个白色小药片，10 mg」就是有效的名称和剂量。", hi: "आपके शब्द ठीक हैं — «वो छोटी सफ़ेद वाली, 10 mg» एक मान्य नाम और ख़ुराक है।", ar: "كلماتك تكفي — «الحبة البيضاء الصغيرة، 10 ملغ» اسم وجرعة صالحان.",
  },
  "med.name": {
    en: "Name", es: "Nombre", fr: "Nom", de: "Name", pt: "Nome", it: "Nome", ja: "名前", zh: "名称", hi: "नाम", ar: "الاسم",
  },
  "med.name.ph": {
    en: "Lisinopril", es: "Lisinopril", fr: "Lisinopril", de: "Lisinopril", pt: "Lisinopril", it: "Lisinopril", ja: "Lisinopril", zh: "Lisinopril", hi: "Lisinopril", ar: "Lisinopril",
  },
  "med.dose": {
    en: "Dose", es: "Dosis", fr: "Dose", de: "Dosis", pt: "Dose", it: "Dose", ja: "用量", zh: "剂量", hi: "ख़ुराक", ar: "الجرعة",
  },
  "med.dose.ph": {
    en: "10 mg", es: "10 mg", fr: "10 mg", de: "10 mg", pt: "10 mg", it: "10 mg", ja: "10 mg", zh: "10 mg", hi: "10 mg", ar: "10 ملغ",
  },
  "med.purpose": {
    en: "What it's for", es: "Para qué es", fr: "À quoi ça sert", de: "Wofür es ist", pt: "Para que serve", it: "A cosa serve", ja: "何のための薬か", zh: "用来治什么", hi: "यह किसलिए है", ar: "لماذا هو",
  },
  "med.optional": {
    en: "(optional)", es: "(opcional)", fr: "(facultatif)", de: "(optional)", pt: "(opcional)", it: "(facoltativo)", ja: "（任意）", zh: "（可选）", hi: "(वैकल्पिक)", ar: "(اختياري)",
  },
  "med.purpose.ph": {
    en: "blood pressure", es: "tensión arterial", fr: "tension artérielle", de: "Blutdruck", pt: "tensão arterial", it: "pressione sanguigna", ja: "血圧", zh: "血压", hi: "रक्तचाप", ar: "ضغط الدم",
  },
  "med.asneeded": {
    en: "As needed, not on a schedule", es: "Según necesidad, sin horario", fr: "Au besoin, pas selon un horaire", de: "Bei Bedarf, nicht nach Plan", pt: "Conforme necessário, sem horário", it: "Al bisogno, non a orario", ja: "定時ではなく頓用", zh: "按需服用，非定时", hi: "आवश्यकतानुसार, समय-सारणी पर नहीं", ar: "عند الحاجة، لا وفق جدول",
  },
  "med.ceiling": {
    en: "Ceiling per day", es: "Máximo por día", fr: "Plafond par jour", de: "Obergrenze pro Tag", pt: "Limite por dia", it: "Tetto giornaliero", ja: "1日の上限", zh: "每日上限", hi: "प्रतिदिन अधिकतम", ar: "الحد اليومي",
  },
  "med.ceiling.note": {
    en: "(optional — JIM will refuse to log past it)", es: "(opcional — JIM se negará a registrar por encima)", fr: "(facultatif — JIM refusera d'enregistrer au-delà)", de: "(optional — JIM verweigert Einträge darüber hinaus)", pt: "(opcional — o JIM recusará registar acima disso)", it: "(facoltativo — JIM rifiuterà di registrare oltre)", ja: "（任意 — これを超える記録をJIMは拒みます）", zh: "（可选 — 超过后 JIM 会拒绝记录）", hi: "(वैकल्पिक — इससे आगे JIM दर्ज करने से मना कर देगा)", ar: "(اختياري — سيرفض JIM التسجيل بعده)",
  },
  "med.times": {
    en: "Times", es: "Horas", fr: "Heures", de: "Zeiten", pt: "Horas", it: "Orari", ja: "時刻", zh: "时间", hi: "समय", ar: "الأوقات",
  },
  "med.times.note": {
    en: "— comma-separated, 24h", es: "— separadas por comas, 24 h", fr: "— séparées par des virgules, format 24 h", de: "— kommagetrennt, 24 h", pt: "— separadas por vírgulas, 24 h", it: "— separati da virgole, 24 h", ja: "— カンマ区切り、24時間表記", zh: "— 逗号分隔，24小时制", hi: "— अल्पविराम से अलग, 24 घंटे", ar: "— مفصولة بفواصل، بنظام 24 ساعة",
  },
  "med.critical": {
    en: "Missing this one is worth a check-in", es: "Saltarse este merece una consulta", fr: "Manquer celui-ci mérite qu'on prenne de vos nouvelles", de: "Dieses zu verpassen ist eine Nachfrage wert", pt: "Falhar este merece uma verificação", it: "Saltare questo vale un controllo", ja: "これを飲み忘れたら声をかけてほしい", zh: "漏服这一种值得来问一句", hi: "यह छूटे तो हालचाल पूछना बनता है", ar: "تفويت هذا يستحق اطمئنانًا",
  },
  "wel.title": {
    en: "Wellness", es: "Bienestar", fr: "Bien-être", de: "Wohlbefinden", pt: "Bem-estar", it: "Benessere", ja: "ウェルネス", zh: "身心健康", hi: "स्वस्थता", ar: "العافية",
  },
  "wel.sub": {
    en: "calm · movement · meals — on purpose, any hour", es: "calma · movimiento · comidas — a propósito, a cualquier hora", fr: "calme · mouvement · repas — à dessein, à toute heure", de: "Ruhe · Bewegung · Mahlzeiten — absichtlich, zu jeder Stunde", pt: "calma · movimento · refeições — de propósito, a qualquer hora", it: "calma · movimento · pasti — di proposito, a qualsiasi ora", ja: "静けさ · 動き · 食事 — 意図して、いつでも", zh: "静心 · 活动 · 饮食 — 有意为之，随时可做", hi: "शांति · गति · भोजन — सोच-समझकर, किसी भी घड़ी", ar: "هدوء · حركة · وجبات — عن قصد، في أي ساعة",
  },
  "wel.calm": {
    en: "Guided calm", es: "Calma guiada", fr: "Calme guidé", de: "Geführte Ruhe", pt: "Calma guiada", it: "Calma guidata", ja: "ガイド付きの静けさ", zh: "引导静心", hi: "निर्देशित शांति", ar: "هدوء موجَّه",
  },
  "wel.calm.pitch": {
    en: "Protocols, not generations — the counts never vary. Pick one; the app paces it{spoken}.", es: "Protocolos, no generaciones — las cuentas nunca varían. Elige uno; la app marca el ritmo{spoken}.", fr: "Des protocoles, pas des générations — les comptes ne varient jamais. Choisissez-en un ; l'appli donne le rythme{spoken}.", de: "Protokolle, keine Generierungen — die Zählungen ändern sich nie. Wähl eines; die App gibt den Takt{spoken}.", pt: "Protocolos, não gerações — as contagens nunca variam. Escolha um; a app marca o ritmo{spoken}.", it: "Protocolli, non generazioni — i conteggi non variano mai. Scegline uno; l'app scandisce il ritmo{spoken}.", ja: "生成ではなくプロトコルです — 数え方は決して変わりません。ひとつ選べば、アプリがペースを刻みます{spoken}。", zh: "是既定方案，不是即兴生成 — 计数从不变化。选一个，应用会为你计拍{spoken}。", hi: "प्रोटोकॉल हैं, जनरेशन नहीं — गिनती कभी नहीं बदलती। एक चुनें; ऐप उसकी लय बनाए रखेगा{spoken}।", ar: "بروتوكولات لا توليدات — الأعداد لا تتغير أبدًا. اختر واحدًا؛ والتطبيق يضبط الإيقاع{spoken}.",
  },
  "wel.calm.spoken": {
    en: " and speaks each step", es: " y dice cada paso", fr: " et énonce chaque étape", de: " und spricht jeden Schritt", pt: " e diz cada passo", it: " e pronuncia ogni passo", ja: "、各ステップを読み上げます", zh: "，并朗读每一步", hi: " और हर चरण बोलता है", ar: " وينطق كل خطوة",
  },
  "wel.calm.speak": {
    en: "Speak the steps out loud", es: "Decir los pasos en voz alta", fr: "Énoncer les étapes à voix haute", de: "Die Schritte laut sprechen", pt: "Dizer os passos em voz alta", it: "Pronuncia i passi ad alta voce", ja: "ステップを声に出す", zh: "把步骤朗读出来", hi: "चरणों को ज़ोर से बोलें", ar: "انطق الخطوات بصوت عالٍ",
  },
  "wel.calm.tile": {
    en: "{title} · {n} min", es: "{title} · {n} min", fr: "{title} · {n} min", de: "{title} · {n} Min.", pt: "{title} · {n} min", it: "{title} · {n} min", ja: "{title} · {n}分", zh: "{title} · {n}分钟", hi: "{title} · {n} मिनट", ar: "{title} · {n} دقيقة",
  },
  "wel.calm.step": {
    en: "step {i} of {n} · {sec}s", es: "paso {i} de {n} · {sec}s", fr: "étape {i} sur {n} · {sec}s", de: "Schritt {i} von {n} · {sec}s", pt: "passo {i} de {n} · {sec}s", it: "passo {i} di {n} · {sec}s", ja: "ステップ{i}/{n} · {sec}秒", zh: "第{i}步，共{n}步 · {sec}秒", hi: "चरण {i}/{n} · {sec} सेकंड", ar: "الخطوة {i} من {n} · {sec} ثانية",
  },
  "wel.calm.end": {
    en: "End early", es: "Terminar antes", fr: "Terminer plus tôt", de: "Früher beenden", pt: "Terminar mais cedo", it: "Termina prima", ja: "途中で終える", zh: "提前结束", hi: "जल्दी समाप्त करें", ar: "أنهِ مبكرًا",
  },
  "wel.calm.done": {
    en: "Session complete. Carry the pace with you.", es: "Sesión completa. Llévate el ritmo contigo.", fr: "Séance terminée. Emportez ce rythme avec vous.", de: "Sitzung abgeschlossen. Nimm den Takt mit.", pt: "Sessão concluída. Leve o ritmo consigo.", it: "Sessione completata. Porta con te il ritmo.", ja: "セッション終了。この呼吸のペースを持って行ってください。", zh: "本次完成。把这份节奏带走。", hi: "सत्र पूरा। इस लय को साथ ले जाएँ।", ar: "انتهت الجلسة. خذ الإيقاع معك.",
  },
  "wel.work": {
    en: "A workout for the time you have", es: "Un entrenamiento para el tiempo que tienes", fr: "Une séance pour le temps dont vous disposez", de: "Ein Training für die Zeit, die du hast", pt: "Um treino para o tempo que tem", it: "Un allenamento per il tempo che hai", ja: "あなたの持ち時間に合う運動", zh: "配合你时间的一套锻炼", hi: "आपके पास जितना समय है उसके लिए एक कसरत", ar: "تمرين يناسب وقتك المتاح",
  },
  "wel.work.minutes": {
    en: "Minutes", es: "Minutos", fr: "Minutes", de: "Minuten", pt: "Minutos", it: "Minuti", ja: "分数", zh: "分钟", hi: "मिनट", ar: "الدقائق",
  },
  "wel.work.level": {
    en: "Level", es: "Nivel", fr: "Niveau", de: "Niveau", pt: "Nível", it: "Livello", ja: "レベル", zh: "水平", hi: "स्तर", ar: "المستوى",
  },
  "wel.work.focus": {
    en: "Focus", es: "Enfoque", fr: "Cible", de: "Schwerpunkt", pt: "Foco", it: "Focus", ja: "重点", zh: "侧重", hi: "केंद्र", ar: "التركيز",
  },
  "wel.work.build": {
    en: "Build it", es: "Créalo", fr: "Construire", de: "Erstellen", pt: "Criá-lo", it: "Crealo", ja: "組み立てる", zh: "生成", hi: "बनाएँ", ar: "ابنِه",
  },
  "wel.work.block": {
    en: " · {sec}s — {cue}", es: " · {sec}s — {cue}", fr: " · {sec}s — {cue}", de: " · {sec}s — {cue}", pt: " · {sec}s — {cue}", it: " · {sec}s — {cue}", ja: " · {sec}秒 — {cue}", zh: " · {sec}秒 — {cue}", hi: " · {sec} सेकंड — {cue}", ar: " · {sec} ثانية — {cue}",
  },
  "wel.meals": {
    en: "A day of meals that fits you", es: "Un día de comidas que te encaja", fr: "Une journée de repas qui vous convient", de: "Ein Tag mit Mahlzeiten, der zu dir passt", pt: "Um dia de refeições que lhe assenta", it: "Una giornata di pasti che ti calza", ja: "あなたに合う一日の食事", zh: "适合你的一天三餐", hi: "आपके अनुकूल एक दिन का भोजन", ar: "يوم من الوجبات يناسبك",
  },
  "wel.meals.goal": {
    en: "Goal", es: "Objetivo", fr: "Objectif", de: "Ziel", pt: "Objetivo", it: "Obiettivo", ja: "目標", zh: "目标", hi: "लक्ष्य", ar: "الهدف",
  },
  "wel.meals.healthier": {
    en: "eat healthier", es: "comer más sano", fr: "manger plus sainement", de: "gesünder essen", pt: "comer mais saudável", it: "mangiare più sano", ja: "健康的に食べる", zh: "吃得更健康", hi: "स्वस्थ खाना", ar: "أكل أصح",
  },
  "wel.meals.lose": {
    en: "lose weight", es: "perder peso", fr: "perdre du poids", de: "abnehmen", pt: "perder peso", it: "perdere peso", ja: "減量する", zh: "减重", hi: "वज़न घटाना", ar: "إنقاص الوزن",
  },
  "wel.meals.gain": {
    en: "gain muscle", es: "ganar músculo", fr: "prendre du muscle", de: "Muskeln aufbauen", pt: "ganhar músculo", it: "mettere massa", ja: "筋肉をつける", zh: "增肌", hi: "मांसपेशी बढ़ाना", ar: "بناء العضلات",
  },
  "wel.meals.days": {
    en: "Days", es: "Días", fr: "Jours", de: "Tage", pt: "Dias", it: "Giorni", ja: "日数", zh: "天数", hi: "दिन", ar: "الأيام",
  },
  "wel.meals.plan": {
    en: "Plan it", es: "Planifícalo", fr: "Planifier", de: "Planen", pt: "Planeá-lo", it: "Pianificalo", ja: "計画する", zh: "规划", hi: "योजना बनाएँ", ar: "خطّط له",
  },
  "wel.meals.shape": {
    en: "{why} · about {kcal} kcal/day for orientation", es: "{why} · unas {kcal} kcal/día como orientación", fr: "{why} · environ {kcal} kcal/jour à titre indicatif", de: "{why} · etwa {kcal} kcal/Tag zur Orientierung", pt: "{why} · cerca de {kcal} kcal/dia para orientação", it: "{why} · circa {kcal} kcal/giorno come orientamento", ja: "{why} · 目安として1日およそ{kcal}kcal", zh: "{why} · 每天约{kcal}千卡，仅供参考", hi: "{why} · दिशा-निर्देश हेतु लगभग {kcal} kcal/दिन", ar: "{why} · نحو {kcal} سعرة/يوم للاسترشاد",
  },
  "wel.meals.day": {
    en: "Day {n}", es: "Día {n}", fr: "Jour {n}", de: "Tag {n}", pt: "Dia {n}", it: "Giorno {n}", ja: "{n}日目", zh: "第{n}天", hi: "दिन {n}", ar: "اليوم {n}",
  },
  "hld.farend": {
    en: "The far end", es: "El otro extremo", fr: "L'autre bout", de: "Das andere Ende", pt: "O outro lado", it: "L'altro capo", ja: "見守りの相手", zh: "线的另一端", hi: "दूसरा छोर", ar: "الطرف الآخر",
  },
  "hld.farend.set": {
    en: "Alerts go to {address} — a person, by email.", es: "Las alertas van a {address} — una persona, por correo.", fr: "Les alertes vont à {address} — une personne, par e-mail.", de: "Warnungen gehen an {address} — einen Menschen, per E-Mail.", pt: "Os alertas vão para {address} — uma pessoa, por e-mail.", it: "Gli avvisi vanno a {address} — una persona, via email.", ja: "アラートは {address} に届きます — 人に、メールで。", zh: "警报会发送到 {address} — 一个人，通过邮件。", hi: "अलर्ट {address} पर जाते हैं — एक व्यक्ति को, ईमेल से।", ar: "تذهب التنبيهات إلى {address} — إلى إنسان، عبر البريد.",
  },
  "hld.farend.email.ph": {
    en: "Emergency contact's email", es: "Correo del contacto de emergencia", fr: "E-mail du contact d'urgence", de: "E-Mail des Notfallkontakts", pt: "E-mail do contacto de emergência", it: "Email del contatto di emergenza", ja: "緊急連絡先のメールアドレス", zh: "紧急联系人的邮箱", hi: "आपातकालीन संपर्क का ईमेल", ar: "البريد الإلكتروني لجهة اتصال الطوارئ",
  },
  "hld.farend.save": {
    en: "They agreed — save", es: "Aceptó — guardar", fr: "Ils ont accepté — enregistrer", de: "Sie haben zugestimmt — speichern", pt: "Aceitou — guardar", it: "Hanno accettato — salva", ja: "同意済み — 保存", zh: "已同意 — 保存", hi: "सहमति दी — सहेजें", ar: "وافقوا — حفظ",
  },
  "hld.farend.clear": {
    en: "Clear", es: "Quitar", fr: "Effacer", de: "Entfernen", pt: "Limpar", it: "Rimuovi", ja: "クリア", zh: "清除", hi: "हटाएँ", ar: "مسح",
  },
  "hld.farend.pitch": {
    en: "When JIM decides to notify your contact, a letter really leaves — with a link that records that a person saw it. Once a month a short note proves the mailbox on a calm day.", es: "Cuando JIM decide avisar a tu contacto, una carta sale de verdad — con un enlace que registra que una persona la vio. Una vez al mes, una nota breve comprueba el buzón en un día tranquilo.", fr: "Quand JIM décide de prévenir votre contact, une lettre part vraiment — avec un lien qui enregistre qu'une personne l'a vue. Une fois par mois, une courte note vérifie la boîte un jour calme.", de: "Wenn JIM deinen Kontakt benachrichtigt, geht wirklich ein Brief hinaus — mit einem Link, der festhält, dass ein Mensch ihn gesehen hat. Einmal im Monat prüft eine kurze Notiz das Postfach an einem ruhigen Tag.", pt: "Quando o JIM decide avisar o seu contacto, uma carta sai mesmo — com uma ligação que regista que uma pessoa a viu. Uma vez por mês, uma nota breve prova a caixa num dia calmo.", it: "Quando JIM decide di avvisare il tuo contatto, una lettera parte davvero — con un link che registra che una persona l'ha vista. Una volta al mese una breve nota mette alla prova la casella in un giorno tranquillo.", ja: "JIM が連絡先への通知を決めると、本当に手紙が送られます — 人が見たことを記録するリンク付きで。月に一度、短いお知らせが平穏な日にメールボックスを確かめます。", zh: "当 JIM 决定通知你的联系人时，信真的会发出 — 附带一个记录“有人看到了”的链接。每月一次的简短便条会在平静的日子里验证邮箱。", hi: "जब JIM आपके संपर्क को सूचित करने का निर्णय लेता है, तो सच में एक पत्र जाता है — एक लिंक के साथ जो दर्ज करता है कि किसी व्यक्ति ने उसे देखा। महीने में एक बार एक छोटा नोट शांत दिन में मेलबॉक्स की जाँच करता है।", ar: "عندما يقرر JIM إخطار جهة اتصالك، تخرج رسالة حقًا — مع رابط يسجل أن إنسانًا رآها. ومرة في الشهر تتحقق رسالة قصيرة من صندوق البريد في يوم هادئ.",
  },
  "hld.farend.acked": {
    en: "{condition} · {when} — seen by a person", es: "{condition} · {when} — visto por una persona", fr: "{condition} · {when} — vu par une personne", de: "{condition} · {when} — von einem Menschen gesehen", pt: "{condition} · {when} — visto por uma pessoa", it: "{condition} · {when} — visto da una persona", ja: "{condition} · {when} — 人が確認済み", zh: "{condition} · {when} — 已有人看到", hi: "{condition} · {when} — एक व्यक्ति ने देखा", ar: "{condition} · {when} — رآه إنسان",
  },
  "hld.farend.unacked": {
    en: "{condition} · {when} — not yet seen", es: "{condition} · {when} — aún sin ver", fr: "{condition} · {when} — pas encore vu", de: "{condition} · {when} — noch nicht gesehen", pt: "{condition} · {when} — ainda não visto", it: "{condition} · {when} — non ancora visto", ja: "{condition} · {when} — まだ未確認", zh: "{condition} · {when} — 尚未有人看到", hi: "{condition} · {when} — अभी तक नहीं देखा गया", ar: "{condition} · {when} — لم يُرَ بعد",
  },
  "hld.yes": {
    en: "yes", es: "sí", fr: "oui", de: "ja", pt: "sim", it: "sì", ja: "はい", zh: "是", hi: "हाँ", ar: "نعم",
  },
  "hld.no": {
    en: "no", es: "no", fr: "non", de: "nein", pt: "não", it: "no", ja: "いいえ", zh: "否", hi: "नहीं", ar: "لا",
  },
  "hld.src.allow.button": {
    en: "Allow", es: "Permitir", fr: "Autoriser", de: "Erlauben", pt: "Permitir", it: "Consenti", ja: "許可する", zh: "允许", hi: "अनुमति दें", ar: "اسمح",
  },
  "hld.book": {
    en: "The people in your phone", es: "Las personas de tu teléfono", fr: "Les personnes de votre téléphone", de: "Die Menschen in deinem Telefon", pt: "As pessoas do seu telefone", it: "Le persone nel tuo telefono", ja: "電話の連絡先の人たち", zh: "你手机里的联系人", hi: "आपके फ़ोन के लोग", ar: "الأشخاص في هاتفك",
  },
  "hld.book.sync": {
    en: "Sync from this device", es: "Sincronizar desde este dispositivo", fr: "Synchroniser depuis cet appareil", de: "Von diesem Gerät synchronisieren", pt: "Sincronizar deste dispositivo", it: "Sincronizza da questo dispositivo", ja: "この端末から同期", zh: "从此设备同步", hi: "इस डिवाइस से सिंक करें", ar: "مزامنة من هذا الجهاز",
  },
  "hld.book.held": {
    en: "{n} people held — names only, never the numbers back out", es: "{n} personas guardadas — solo nombres, nunca los números", fr: "{n} personnes conservées — les noms seulement, jamais les numéros", de: "{n} Personen gehalten — nur Namen, nie die Nummern zurück", pt: "{n} pessoas guardadas — só nomes, nunca os números", it: "{n} persone conservate — solo i nomi, mai i numeri", ja: "{n} 人を保持 — 名前のみ、番号は返しません", zh: "已保存 {n} 人——只有名字，号码绝不返回", hi: "{n} लोग रखे गए — केवल नाम, नंबर कभी वापस नहीं", ar: "{n} شخصًا محفوظًا — الأسماء فقط، الأرقام لا تعود أبدًا",
  },
  "hld.book.empty": {
    en: "Nothing synced yet", es: "Aún no hay nada sincronizado", fr: "Rien de synchronisé pour l'instant", de: "Noch nichts synchronisiert", pt: "Ainda nada sincronizado", it: "Ancora niente di sincronizzato", ja: "まだ何も同期されていません", zh: "尚未同步任何内容", hi: "अभी तक कुछ सिंक नहीं हुआ", ar: "لم تتم مزامنة أي شيء بعد",
  },
  "hld.book.guardian": {
    en: "has a guardian", es: "tiene guardián", fr: "a un gardien", de: "hat einen Wächter", pt: "tem guardião", it: "ha un guardiano", ja: "ガーディアンあり", zh: "有守护者", hi: "गार्जियन है", ar: "لديه وصيّ",
  },
  "hld.book.more": {
    en: "…and {n} more", es: "…y {n} más", fr: "…et {n} de plus", de: "…und {n} weitere", pt: "…e mais {n}", it: "…e altri {n}", ja: "…ほか {n} 人", zh: "…还有 {n} 人", hi: "…और {n} लोग", ar: "…و{n} آخرون",
  },
  "hld.book.nopicker": {
    en: "This browser cannot hand its contacts over — sync from the phone app instead", es: "Este navegador no puede entregar sus contactos: sincroniza desde la aplicación del teléfono", fr: "Ce navigateur ne peut pas transmettre ses contacts — synchronisez depuis l'application du téléphone", de: "Dieser Browser kann seine Kontakte nicht übergeben — synchronisiere über die Telefon-App", pt: "Este navegador não pode entregar os contactos — sincronize pela aplicação do telefone", it: "Questo browser non può consegnare i contatti — sincronizza dall'app del telefono", ja: "このブラウザは連絡先を渡せません — スマホアプリから同期してください", zh: "此浏览器无法交出联系人——请通过手机应用同步", hi: "यह ब्राउज़र संपर्क नहीं दे सकता — फ़ोन ऐप से सिंक करें", ar: "لا يستطيع هذا المتصفح تسليم جهات الاتصال — زامِن من تطبيق الهاتف",
  },
  "hld.src.withdraw": {
    en: "Withdraw", es: "Retirar", fr: "Retirer", de: "Zurückziehen", pt: "Retirar", it: "Ritira", ja: "取り消す", zh: "撤回", hi: "वापस लें", ar: "اسحب",
  },
  "hld.title": {
    en: "What's held about you", es: "Lo que se guarda sobre ti", fr: "Ce qui est détenu sur vous", de: "Was über dich gehalten wird", pt: "O que é guardado sobre si", it: "Ciò che è custodito su di te", ja: "あなたについて保持されているもの", zh: "关于你所保存的一切", hi: "आपके बारे में जो रखा गया है", ar: "ما هو محفوظ عنك",
  },
  "hld.sub": {
    en: "who holds it, who has read it", es: "quién lo guarda, quién lo ha leído", fr: "qui le détient, qui l'a lu", de: "wer es hält, wer es gelesen hat", pt: "quem o guarda, quem o leu", it: "chi lo custodisce, chi l'ha letto", ja: "誰が保持し、誰が読んだか", zh: "谁保管，谁读过", hi: "कौन रखता है, किसने पढ़ा", ar: "من يحفظه، ومن قرأه",
  },
  "hld.log": {
    en: "Who has read your record", es: "Quién ha leído tu registro", fr: "Qui a lu votre dossier", de: "Wer deine Akte gelesen hat", pt: "Quem leu o seu registo", it: "Chi ha letto il tuo registro", ja: "あなたの記録を読んだ人", zh: "谁读过你的记录", hi: "आपका रिकॉर्ड किसने पढ़ा", ar: "من قرأ سجلك",
  },
  "hld.log.vaulted": {
    en: "Sealed in a vault:", es: "Sellado en una bóveda:", fr: "Scellé dans un coffre :", de: "In einem Tresor versiegelt:", pt: "Selado num cofre:", it: "Sigillato in un caveau:", ja: "保管庫に封印:", zh: "已封入保险库:", hi: "तिजोरी में सील:", ar: "مختوم في خزنة:",
  },
  "hld.log.kept": {
    en: "An access record is being kept:", es: "Se está llevando un registro de accesos:", fr: "Un registre des accès est tenu :", de: "Ein Zugriffsprotokoll wird geführt:", pt: "Está a ser mantido um registo de acessos:", it: "Si tiene un registro degli accessi:", ja: "アクセス記録の保持:", zh: "正在保留访问记录:", hi: "पहुँच रिकॉर्ड रखा जा रहा है:", ar: "يُحتفظ بسجل وصول:",
  },
  "hld.log.empty": {
    en: "The list below is empty because nothing is being recorded — not because nobody has looked. Those are different facts and this screen will not let them look the same.", es: "La lista de abajo está vacía porque no se está registrando nada — no porque nadie haya mirado. Son hechos distintos y esta pantalla no dejará que parezcan iguales.", fr: "La liste ci-dessous est vide parce que rien n'est enregistré — pas parce que personne n'a regardé. Ce sont deux faits différents et cet écran ne les laissera pas se ressembler.", de: "Die Liste unten ist leer, weil nichts aufgezeichnet wird — nicht, weil niemand hineingesehen hat. Das sind verschiedene Tatsachen, und dieser Bildschirm lässt sie nicht gleich aussehen.", pt: "A lista abaixo está vazia porque nada está a ser registado — não porque ninguém tenha olhado. São factos diferentes e este ecrã não os deixará parecer iguais.", it: "L'elenco qui sotto è vuoto perché non si sta registrando nulla — non perché nessuno abbia guardato. Sono fatti diversi e questa schermata non li lascerà sembrare uguali.", ja: "下のリストが空なのは、誰も見ていないからではなく、何も記録されていないからです。この二つは別の事実であり、この画面は両者を同じに見せません。", zh: "下面的列表为空，是因为什么都没被记录 — 而不是因为无人查看过。这是两个不同的事实，本屏幕不会让它们看起来一样。", hi: "नीचे की सूची इसलिए खाली है क्योंकि कुछ दर्ज ही नहीं हो रहा — इसलिए नहीं कि किसी ने देखा नहीं। ये दो अलग तथ्य हैं और यह स्क्रीन इन्हें एक जैसा नहीं दिखने देगी।", ar: "القائمة أدناه فارغة لأن شيئًا لا يُسجَّل — لا لأن أحدًا لم يطّلع. هاتان حقيقتان مختلفتان، وهذه الشاشة لن تدعهما تبدوان متشابهتين.",
  },
  "hld.audit": {
    en: "What was done, and whether the record was edited", es: "Qué se hizo, y si el registro fue editado", fr: "Ce qui a été fait, et si le registre a été modifié", de: "Was getan wurde — und ob der Eintrag nachträglich geändert wurde", pt: "O que foi feito, e se o registo foi editado", it: "Cosa è stato fatto, e se il registro è stato modificato", ja: "何が行われたか、そしてその記録が後から書き換えられていないか", zh: "做了什么，以及记录是否被改动过", hi: "क्या किया गया, और क्या रिकॉर्ड बाद में बदला गया", ar: "ما الذي جرى، وهل عُدِّل السجل بعدها",
  },
  "hld.audit.intact": {
    en: "The chain is intact: every entry still hashes to the one before it, so nothing here has been edited or removed since it was written.", es: "La cadena está intacta: cada entrada sigue enlazando por hash con la anterior, así que nada de esto se ha editado ni eliminado desde que se escribió.", fr: "La chaîne est intacte : chaque entrée hache toujours la précédente, donc rien ici n'a été modifié ni supprimé depuis son écriture.", de: "Die Kette ist unversehrt: Jeder Eintrag hasht weiterhin auf den vorherigen, es wurde hier also seit dem Schreiben nichts geändert oder entfernt.", pt: "A cadeia está intacta: cada entrada continua a fazer hash da anterior, portanto nada aqui foi editado ou removido desde que foi escrito.", it: "La catena è intatta: ogni voce continua a fare l'hash della precedente, quindi qui nulla è stato modificato o rimosso da quando è stato scritto.", ja: "チェーンは無傷です。各項目が直前の項目のハッシュを保持しており、書かれて以降に編集も削除もされていません。", zh: "链条完整：每条记录仍与前一条哈希相连，因此这里的内容自写入后未被改动或删除。", hi: "श्रृंखला अक्षुण्ण है: हर प्रविष्टि अब भी पिछली से हैश द्वारा जुड़ी है, इसलिए लिखे जाने के बाद यहाँ कुछ भी बदला या हटाया नहीं गया।", ar: "السلسلة سليمة: كل مدخل ما زال يُجزّئ ما قبله، فلم يُعدَّل هنا شيء ولم يُحذف منذ كتابته.",
  },
  "hld.audit.broken": {
    en: "The chain is broken at entry {seq}. Something was edited or removed after it was written. That is exactly what this record exists to tell you.", es: "La cadena está rota en la entrada {seq}. Algo se editó o se eliminó después de escribirse. Para decirte precisamente eso existe este registro.", fr: "La chaîne est rompue à l'entrée {seq}. Quelque chose a été modifié ou supprimé après son écriture. C'est exactement ce que ce registre existe pour vous dire.", de: "Die Kette ist bei Eintrag {seq} gebrochen. Etwas wurde nach dem Schreiben geändert oder entfernt. Genau dafür gibt es diesen Eintrag.", pt: "A cadeia está quebrada na entrada {seq}. Algo foi editado ou removido depois de escrito. É exatamente isso que este registo existe para lhe dizer.", it: "La catena è spezzata alla voce {seq}. Qualcosa è stato modificato o rimosso dopo la scrittura. È esattamente ciò che questo registro esiste per dirti.", ja: "チェーンは項目 {seq} で切れています。書かれた後に何かが編集または削除されました。この記録はまさにそれを伝えるために存在します。", zh: "链条在第 {seq} 条处断开。有内容在写入之后被改动或删除。这正是本记录存在的意义。", hi: "श्रृंखला प्रविष्टि {seq} पर टूटी है। लिखे जाने के बाद कुछ बदला या हटाया गया। यह रिकॉर्ड ठीक यही बताने के लिए है।", ar: "السلسلة مقطوعة عند المدخل {seq}. عُدِّل شيء أو حُذف بعد كتابته. وهذا بالضبط ما وُجد هذا السجل ليخبرك به.",
  },
  "hld.audit.none": {
    en: "Nothing has been recorded for you yet. The list below is what would be — an empty log here means nothing happened, not that nothing is watched.", es: "Todavía no se ha registrado nada tuyo. La lista de abajo es lo que se registraría: un registro vacío aquí significa que no ocurrió nada, no que no se vigile nada.", fr: "Rien n'a encore été consigné vous concernant. La liste ci-dessous est ce qui le serait — un journal vide ici signifie que rien ne s'est produit, pas que rien n'est surveillé.", de: "Zu dir wurde noch nichts aufgezeichnet. Die Liste unten zeigt, was aufgezeichnet würde — ein leeres Protokoll heißt hier: nichts ist geschehen, nicht: nichts wird beobachtet.", pt: "Ainda nada foi registado sobre si. A lista abaixo é o que seria — um registo vazio aqui significa que nada aconteceu, não que nada é vigiado.", it: "Non è ancora stato registrato nulla su di te. L'elenco qui sotto è ciò che lo sarebbe — un registro vuoto qui significa che non è successo nulla, non che nulla sia sorvegliato.", ja: "あなたについてはまだ何も記録されていません。下の一覧が記録される対象です。ここが空なのは「何も起きていない」という意味であり、「何も見張っていない」という意味ではありません。", zh: "尚未记录与你有关的任何事。下面列出的是会被记录的内容 — 此处为空意味着什么都没发生，而不是什么都没被记录。", hi: "आपके बारे में अभी कुछ भी दर्ज नहीं हुआ है। नीचे की सूची वही है जो दर्ज होती — यहाँ खाली लॉग का अर्थ है कि कुछ हुआ ही नहीं, यह नहीं कि कुछ देखा नहीं जा रहा।", ar: "لم يُسجَّل عنك شيء بعد. القائمة أدناه هي ما كان سيُسجَّل — والسجل الفارغ هنا يعني أن شيئًا لم يحدث، لا أن شيئًا لا يُراقَب.",
  },
  "hld.audit.watched": {
    en: "What is recorded here", es: "Qué se registra aquí", fr: "Ce qui est consigné ici", de: "Was hier aufgezeichnet wird", pt: "O que é registado aqui", it: "Cosa viene registrato qui", ja: "ここに記録されること", zh: "这里会记录什么", hi: "यहाँ क्या दर्ज होता है", ar: "ما الذي يُسجَّل هنا",
  },
  "hld.plan": {
    en: "Your plan", es: "Tu plan", fr: "Votre forfait", de: "Dein Tarif", pt: "O seu plano", it: "Il tuo piano", ja: "あなたのプラン", zh: "你的方案", hi: "आपकी योजना", ar: "خطتك",
  },
  "hld.plan.canread": {
    en: "Can read it: {list}", es: "Pueden leerlo: {list}", fr: "Peuvent le lire : {list}", de: "Dürfen es lesen: {list}", pt: "Podem lê-lo: {list}", it: "Possono leggerlo: {list}", ja: "読める者: {list}", zh: "可读取者: {list}", hi: "इसे पढ़ सकते हैं: {list}", ar: "يمكنهم قراءته: {list}",
  },
  "hld.plan.cancel": {
    en: "Cancel", es: "Cancelar", fr: "Annuler", de: "Abbrechen", pt: "Cancelar", it: "Annulla", ja: "キャンセル", zh: "取消", hi: "रद्द करें", ar: "ألغِ",
  },
  "hld.custody": {
    en: "Custody", es: "Custodia", fr: "Garde", de: "Verwahrung", pt: "Custódia", it: "Custodia", ja: "保管", zh: "保管", hi: "अभिरक्षा", ar: "الحفظ",
  },
  "hld.custody.key.ph": {
    en: "journal", es: "diario", fr: "journal", de: "Journal", pt: "diário", it: "diario", ja: "journal", zh: "journal", hi: "journal", ar: "journal",
  },
  "hld.custody.where": {
    en: "Where did this come from?", es: "¿De dónde vino esto?", fr: "D'où cela vient-il ?", de: "Woher kam das?", pt: "De onde veio isto?", it: "Da dove viene questo?", ja: "これはどこから来たのか？", zh: "这是从哪来的？", hi: "यह कहाँ से आया?", ar: "من أين جاء هذا؟",
  },
  "hld.custody.pitch": {
    en: "Provenance is asked one key at a time — the route requires the key, which is a small thing that a binding written from the route table would have got wrong and a call against a running server did not.", es: "La procedencia se pide de una clave en una — la ruta exige la clave, un detalle pequeño que un enlace escrito desde la tabla de rutas habría errado y una llamada contra un servidor en marcha no.", fr: "La provenance se demande une clé à la fois — la route exige la clé, un petit détail qu'une liaison écrite d'après la table des routes aurait manqué et qu'un appel contre un serveur en marche n'a pas manqué.", de: "Die Herkunft wird Schlüssel für Schlüssel erfragt — die Route verlangt den Schlüssel, eine Kleinigkeit, die eine aus der Routentabelle geschriebene Anbindung falsch gemacht hätte und ein Aufruf gegen einen laufenden Server nicht.", pt: "A proveniência pede-se uma chave de cada vez — a rota exige a chave, um pormenor pequeno que uma ligação escrita a partir da tabela de rotas teria errado e uma chamada contra um servidor a correr não errou.", it: "La provenienza si chiede una chiave alla volta — la rotta richiede la chiave, una piccolezza che un binding scritto dalla tabella delle rotte avrebbe sbagliato e una chiamata a un server in esecuzione no.", ja: "来歴は一度にひとつのキーで尋ねます — このルートはキーを必須とします。ルート表から書いたバインディングなら取り違えたはずの小さな点で、実際に動くサーバーへ呼び出して初めて分かることでした。", zh: "来历一次只问一个键 — 该路由要求提供键。这是个细节：照着路由表写的绑定会弄错，而对着运行中的服务器实测就不会。", hi: "उद्गम एक बार में एक कुंजी के लिए पूछा जाता है — रूट कुंजी माँगता है, यह छोटी बात रूट-तालिका से लिखी बाइंडिंग ग़लत कर देती, और चालू सर्वर पर की गई कॉल ने नहीं की।", ar: "يُسأل عن المنشأ مفتاحًا مفتاحًا — المسار يشترط المفتاح، وهي تفصيلة صغيرة كان الربط المكتوب من جدول المسارات ليخطئ فيها، ولم يخطئ نداءٌ على خادم يعمل.",
  },
  "hld.src": {
    en: "What it may look at", es: "Qué puede consultar", fr: "Ce qu'il peut consulter", de: "Was es einsehen darf", pt: "O que pode consultar", it: "Cosa può guardare", ja: "見てよいもの", zh: "它可以查看什么", hi: "यह क्या देख सकता है", ar: "ما يجوز له النظر فيه",
  },
  "hld.src.none": {
    en: "Nothing consented. Until a source is consented here, giving JIM context from it is refused — the server checks, it does not merely ask nicely.", es: "Nada consentido. Hasta que una fuente se consienta aquí, darle a JIM contexto desde ella se rechaza — el servidor lo comprueba, no se limita a pedirlo por favor.", fr: "Rien de consenti. Tant qu'une source n'est pas consentie ici, donner à JIM du contexte issu d'elle est refusé — le serveur vérifie, il ne se contente pas de demander gentiment.", de: "Nichts eingewilligt. Solange eine Quelle hier nicht freigegeben ist, wird verweigert, JIM Kontext daraus zu geben — der Server prüft, er bittet nicht bloß höflich.", pt: "Nada consentido. Até uma fonte ser consentida aqui, dar ao JIM contexto a partir dela é recusado — o servidor verifica, não se limita a pedir com jeitinho.", it: "Nulla acconsentito. Finché una fonte non è acconsentita qui, dare a JIM contesto da essa viene rifiutato — il server controlla, non si limita a chiedere gentilmente.", ja: "同意されたものはありません。ここでソースに同意するまで、そこからJIMにコンテキストを与えることは拒否されます — サーバーが検査しており、丁寧にお願いしているだけではありません。", zh: "尚未同意任何来源。在此同意某个来源之前，从它向 JIM 提供上下文会被拒绝 — 服务器会检查，而不只是客气地请求。", hi: "किसी की सहमति नहीं। जब तक यहाँ किसी स्रोत की सहमति न दी जाए, उससे JIM को संदर्भ देना अस्वीकार होता है — सर्वर जाँचता है, केवल विनती नहीं करता।", ar: "لا شيء تمت الموافقة عليه. حتى تُمنح الموافقة لمصدر هنا، يُرفض إعطاء JIM سياقًا منه — الخادم يفحص، ولا يكتفي بالطلب بلطف.",
  },
  "hld.src.allow": {
    en: "Allow {source}", es: "Permitir {source}", fr: "Autoriser {source}", de: "{source} erlauben", pt: "Permitir {source}", it: "Consenti {source}", ja: "{source}を許可", zh: "允许{source}", hi: "{source} की अनुमति दें", ar: "اسمح بـ{source}",
  },
  "hld.where": {
    en: "Where the answers come from", es: "De dónde vienen las respuestas", fr: "D'où viennent les réponses", de: "Woher die Antworten kommen", pt: "De onde vêm as respostas", it: "Da dove vengono le risposte", ja: "答えはどこから来るか", zh: "答案从哪来", hi: "उत्तर कहाँ से आते हैं", ar: "من أين تأتي الإجابات",
  },
  "hld.where.cloud": {
    en: "Cloud model: {model} · falls back to {fallback}", es: "Modelo en la nube: {model} · recurre a {fallback}", fr: "Modèle cloud : {model} · se rabat sur {fallback}", de: "Cloud-Modell: {model} · fällt zurück auf {fallback}", pt: "Modelo na nuvem: {model} · recorre a {fallback}", it: "Modello cloud: {model} · ripiega su {fallback}", ja: "クラウドモデル: {model} · 代替は{fallback}", zh: "云端模型: {model} · 回退到{fallback}", hi: "क्लाउड मॉडल: {model} · विकल्प {fallback}", ar: "نموذج سحابي: {model} · يعود إلى {fallback}",
  },
  "hld.where.provider": {
    en: "Provider for this account: {provider}", es: "Proveedor de esta cuenta: {provider}", fr: "Fournisseur de ce compte : {provider}", de: "Anbieter für dieses Konto: {provider}", pt: "Fornecedor desta conta: {provider}", it: "Provider di questo account: {provider}", ja: "このアカウントのプロバイダー: {provider}", zh: "此账户的提供方: {provider}", hi: "इस खाते का प्रदाता: {provider}", ar: "مزود هذا الحساب: {provider}",
  },
  "hld.where.connectors": {
    en: "{n} connector providers catalogued — Apple, Google and the rest, each with the apps and directions it can be asked for.", es: "{n} proveedores de conectores catalogados — Apple, Google y los demás, cada uno con las apps y direcciones que se le pueden pedir.", fr: "{n} fournisseurs de connecteurs catalogués — Apple, Google et les autres, chacun avec les applis et les directions qu'on peut lui demander.", de: "{n} Konnektor-Anbieter katalogisiert — Apple, Google und die übrigen, jeweils mit den Apps und Richtungen, um die man sie bitten kann.", pt: "{n} fornecedores de conectores catalogados — Apple, Google e os restantes, cada um com as apps e direções que lhe podem ser pedidas.", it: "{n} fornitori di connettori catalogati — Apple, Google e gli altri, ciascuno con le app e le direzioni che gli si possono chiedere.", ja: "コネクタ提供元を{n}社カタログ化 — Apple、Google、その他、それぞれ依頼できるアプリと方向とともに。", zh: "已收录{n}家连接器提供方 — Apple、Google 及其余各家，各自附有可请求的应用与方向。", hi: "{n} कनेक्टर प्रदाता सूचीबद्ध — Apple, Google और बाक़ी, हर एक उन ऐप और दिशाओं के साथ जो उससे माँगी जा सकती हैं।", ar: "{n} من مزودي الموصّلات مفهرسون — Apple وGoogle وسواهما، كل منهم مع التطبيقات والاتجاهات التي يمكن طلبها منه.",
  },
  "set.voice.saved": {
    en: "Saved — checking the key with the service…", es: "Guardado — comprobando la clave con el servicio…", fr: "Enregistré — vérification de la clé auprès du service…", de: "Gespeichert — der Schlüssel wird beim Dienst geprüft …", pt: "Guardado — a verificar a chave junto do serviço…", it: "Salvato — verifica della chiave presso il servizio…", ja: "保存しました — サービスにキーを確認しています…", zh: "已保存 — 正在向服务核对密钥…", hi: "सहेजा गया — सेवा से कुंजी की जाँच की जा रही है…", ar: "تم الحفظ — يجري التحقق من المفتاح لدى الخدمة…",
  },
  "set.voice.key.works": {
    en: "Saved, and the key works.", es: "Guardado, y la clave funciona.", fr: "Enregistré, et la clé fonctionne.", de: "Gespeichert, und der Schlüssel funktioniert.", pt: "Guardado, e a chave funciona.", it: "Salvato, e la chiave funziona.", ja: "保存しました。キーは有効です。", zh: "已保存，密钥可用。", hi: "सहेजा गया, और कुंजी काम करती है।", ar: "تم الحفظ، والمفتاح يعمل.",
  },
  "set.voice.key.is_an_id": {
    en: "That is the key's ID, not the key. The dashboard lists the ID beside every key and shows the key itself only once — when you create or rotate it. The one you want begins sk_ and is much longer.", es: "Eso es el ID de la clave, no la clave. El panel muestra el ID junto a cada clave y enseña la clave misma una sola vez: al crearla o rotarla. La que necesitas empieza por sk_ y es mucho más larga.", fr: "C'est l'identifiant de la clé, pas la clé. Le tableau de bord affiche l'identifiant à côté de chaque clé et ne montre la clé elle-même qu'une fois, à sa création ou à sa rotation. Celle qu'il vous faut commence par sk_ et est bien plus longue.", de: "Das ist die ID des Schlüssels, nicht der Schlüssel. Das Dashboard führt die ID neben jedem Schlüssel auf und zeigt den Schlüssel selbst nur einmal — beim Erstellen oder Erneuern. Der gesuchte beginnt mit sk_ und ist viel länger.", pt: "Isso é o ID da chave, não a chave. O painel lista o ID ao lado de cada chave e mostra a própria chave apenas uma vez — quando a cria ou roda. A que procura começa por sk_ e é bem mais longa.", it: "Quello è l'ID della chiave, non la chiave. Il pannello elenca l'ID accanto a ogni chiave e mostra la chiave stessa una sola volta, quando la crei o la ruoti. Quella che ti serve inizia con sk_ ed è molto più lunga.", ja: "それはキーの ID であって、キーではありません。ダッシュボードは各キーの横に ID を常に表示し、キー本体は作成時か更新時の一度だけ表示します。必要なのは sk_ で始まる、はるかに長いほうです。", zh: "那是密钥的 ID，不是密钥。控制台会在每个密钥旁边一直显示 ID，而密钥本身只在创建或轮换时显示一次。你需要的那个以 sk_ 开头，长得多。", hi: "वह कुंजी की ID है, कुंजी नहीं। डैशबोर्ड हर कुंजी के बगल में ID दिखाता रहता है, और कुंजी स्वयं केवल एक बार — बनाते या बदलते समय। जो चाहिए वह sk_ से शुरू होती है और कहीं ज़्यादा लंबी है।", ar: "ذلك مُعرِّف المفتاح، لا المفتاح نفسه. تعرض لوحة التحكم المُعرِّف بجانب كل مفتاح دائمًا، وتُظهر المفتاح ذاته مرة واحدة فقط — عند إنشائه أو تدويره. المطلوب يبدأ بـ sk_ وهو أطول بكثير.",
  },
  "set.voice.key.unpaid": {
    en: "The key works — the account behind it has an unpaid invoice. ElevenLabs stops serving until the latest one is settled; the Guardian will use the device's own voice until then.", es: "La clave funciona — la cuenta que hay detrás tiene una factura sin pagar. ElevenLabs deja de atender hasta que se salde la última; hasta entonces el Guardián usará la voz propia del dispositivo.", fr: "La clé fonctionne — le compte derrière elle a une facture impayée. ElevenLabs cesse de répondre tant que la dernière n'est pas réglée ; d'ici là le Gardien utilisera la voix propre de l'appareil.", de: "Der Schlüssel funktioniert — das Konto dahinter hat eine offene Rechnung. ElevenLabs liefert nichts mehr, bis die letzte beglichen ist; bis dahin nutzt der Guardian die eigene Stimme des Geräts.", pt: "A chave funciona — a conta por trás tem uma fatura por pagar. A ElevenLabs deixa de servir até a última ser liquidada; até lá o Guardião usará a voz do próprio dispositivo.", it: "La chiave funziona — l'account dietro ha una fattura non pagata. ElevenLabs smette di servire finché l'ultima non è saldata; fino ad allora il Guardiano userà la voce del dispositivo.", ja: "キーは有効です — その背後のアカウントに未払いの請求があります。ElevenLabs は最新の請求が精算されるまで提供を止めます。それまでガーディアンは端末自身の声を使います。", zh: "密钥是好的 — 其背后的账户有一张未付账单。在结清最新账单之前 ElevenLabs 会停止服务；在此之前守护者将使用设备自带的声音。", hi: "कुंजी काम करती है — उसके पीछे के खाते का एक बिल बकाया है। जब तक नवीनतम बिल नहीं चुकता, ElevenLabs सेवा रोक देता है; तब तक गार्जियन डिवाइस की अपनी आवाज़ का उपयोग करेगा।", ar: "المفتاح يعمل — الحساب خلفه عليه فاتورة غير مسدَّدة. تتوقف ElevenLabs عن الخدمة حتى تُسوَّى الأخيرة؛ وحتى ذلك الحين سيستخدم الحارس صوت الجهاز نفسه.",
  },
  "set.voice.key.refused": {
    en: "The service did not accept that key. Nothing else here is wrong — paste it again, or create a new key and use the one shown at that moment.", es: "El servicio no aceptó esa clave. No hay nada más mal aquí: pégala de nuevo, o crea una clave nueva y usa la que se muestre en ese momento.", fr: "Le service n'a pas accepté cette clé. Rien d'autre ne cloche ici : recollez-la, ou créez une nouvelle clé et utilisez celle affichée à ce moment-là.", de: "Der Dienst hat diesen Schlüssel nicht angenommen. Sonst ist hier nichts falsch — noch einmal einfügen, oder einen neuen Schlüssel anlegen und den nehmen, der dabei angezeigt wird.", pt: "O serviço não aceitou essa chave. Mais nada está errado aqui — cole-a outra vez, ou crie uma chave nova e use a que aparecer nesse momento.", it: "Il servizio non ha accettato quella chiave. Nient'altro qui è sbagliato: incollala di nuovo, oppure crea una chiave nuova e usa quella mostrata in quel momento.", ja: "サービスはそのキーを受け付けませんでした。他に問題はありません — 貼り直すか、新しいキーを作ってそのとき表示されたものを使ってください。", zh: "服务未接受该密钥。此处其他设置都没问题 — 重新粘贴一次，或新建一个密钥并使用创建时显示的那串。", hi: "सेवा ने वह कुंजी स्वीकार नहीं की। यहाँ और कुछ ग़लत नहीं है — इसे दोबारा चिपकाएँ, या नई कुंजी बनाकर उसी क्षण दिखी हुई कुंजी का उपयोग करें।", ar: "لم تقبل الخدمة ذلك المفتاح. لا شيء آخر هنا خاطئ — الصقه من جديد، أو أنشئ مفتاحًا جديدًا واستخدم ما يظهر عندها.",
  },
  "set.voice.key.unchecked": {
    en: "Saved, but nothing could be reached to check it — it will be tried the first time the Guardian speaks.", es: "Guardado, pero no se pudo contactar con nada para comprobarlo: se probará la primera vez que el Guardián hable.", fr: "Enregistré, mais rien n'a pu être joint pour la vérifier — elle sera essayée la première fois que le Gardien parlera.", de: "Gespeichert, aber es war nichts erreichbar, um ihn zu prüfen — er wird beim ersten Sprechen des Guardians versucht.", pt: "Guardado, mas não foi possível contactar nada para a verificar — será testada da primeira vez que o Guardião falar.", it: "Salvato, ma non è stato possibile raggiungere nulla per verificarla: sarà provata la prima volta che il Guardiano parla.", ja: "保存しましたが、確認のために接続できる先がありませんでした — 次にガーディアンが話すときに試されます。", zh: "已保存，但无法连接任何服务来核对 — 守护者第一次开口说话时会试用它。", hi: "सहेजा गया, पर जाँच के लिए कुछ भी संपर्क में नहीं आया — गार्जियन जब पहली बार बोलेगा तब इसे आज़माया जाएगा।", ar: "تم الحفظ، لكن تعذّر الوصول إلى أي جهة للتحقق منه — سيُجرَّب أول مرة يتحدث فيها الحارس.",
  },
  "hld.where.voice": {
    en: "Spoken through {provider}: {left} of {limit} characters left.", es: "Hablado a través de {provider}: quedan {left} de {limit} caracteres.", fr: "Parlé via {provider} : il reste {left} caractères sur {limit}.", de: "Gesprochen über {provider}: {left} von {limit} Zeichen übrig.", pt: "Falado através de {provider}: restam {left} de {limit} caracteres.", it: "Parlato tramite {provider}: restano {left} caratteri su {limit}.", ja: "{provider} を通して話します: 残り {left} / {limit} 文字。", zh: "通过 {provider} 发声：还剩 {left} / {limit} 个字符。", hi: "{provider} के ज़रिये बोला जाता है: {limit} में से {left} अक्षर बचे हैं।", ar: "يُنطق عبر {provider}: بقي {left} من {limit} حرفًا.",
  },
  "hld.where.voice.spent": {
    en: "Spoken through {provider}: the allowance is spent. Until it refills, everything is read in the device's own voice — nothing is lost, but it will not sound like the voice you chose.", es: "Hablado a través de {provider}: la asignación está agotada. Hasta que se reponga, todo se lee con la voz propia del dispositivo — no se pierde nada, pero no sonará como la voz que elegiste.", fr: "Parlé via {provider} : le crédit est épuisé. Jusqu'à son renouvellement, tout est lu avec la voix propre de l'appareil — rien n'est perdu, mais ce ne sera pas la voix que vous avez choisie.", de: "Gesprochen über {provider}: das Kontingent ist aufgebraucht. Bis es sich auffüllt, wird alles mit der eigenen Stimme des Geräts vorgelesen — nichts geht verloren, aber es klingt nicht nach der Stimme, die du gewählt hast.", pt: "Falado através de {provider}: a quota está esgotada. Até se repor, tudo é lido com a voz do próprio dispositivo — nada se perde, mas não soará como a voz que escolheu.", it: "Parlato tramite {provider}: il credito è esaurito. Finché non si ricarica, tutto viene letto con la voce del dispositivo — non si perde nulla, ma non sarà la voce che hai scelto.", ja: "{provider} を通して話します: 割り当てを使い切りました。補充されるまで、すべては端末自身の声で読み上げられます — 失われるものはありませんが、選んだ声の響きにはなりません。", zh: "通过 {provider} 发声：额度已用尽。在额度恢复之前，一切都会用设备自带的声音朗读 — 内容不会丢失，但听起来不是你选的那个声音。", hi: "{provider} के ज़रिये बोला जाता है: कोटा ख़त्म हो चुका है। दोबारा भरने तक सब कुछ डिवाइस की अपनी आवाज़ में पढ़ा जाएगा — कुछ खोता नहीं, पर वह आपकी चुनी हुई आवाज़ जैसी नहीं लगेगी।", ar: "يُنطق عبر {provider}: نفدت الحصة. وإلى أن تتجدد، يُقرأ كل شيء بصوت الجهاز نفسه — لا يضيع شيء، لكنه لن يبدو كالصوت الذي اخترته.",
  },
  "hld.where.voice.resets": {
    en: "It refills on {when}.", es: "Se repone el {when}.", fr: "Il se renouvelle le {when}.", de: "Es füllt sich am {when} wieder auf.", pt: "Repõe-se a {when}.", it: "Si ricarica il {when}.", ja: "{when} に補充されます。", zh: "将于 {when} 恢复。", hi: "यह {when} को दोबारा भरेगा।", ar: "يتجدّد في {when}.",
  },
  "hld.take": {
    en: "Take it with you", es: "Llévatelo", fr: "Emportez-le",
    de: "Nimm es mit", pt: "Leve-o consigo", it: "Portalo con te",
    ja: "持ち出す", zh: "带走它", hi: "इसे अपने साथ ले जाएँ",
    ar: "خذه معك",
  },
  "hld.take.pitch": {
    en: "Everything this deployment holds about you, as one file. Live "
        + "credentials are left out — the rest is yours.",
    es: "Todo lo que esta instalación tiene sobre ti, en un archivo. Las "
        + "credenciales activas quedan fuera; el resto es tuyo.",
    fr: "Tout ce que ce déploiement détient sur vous, en un fichier. Les "
        + "identifiants actifs sont exclus ; le reste est à vous.",
    de: "Alles, was diese Installation über dich hat, als eine Datei. Aktive "
        + "Zugangsdaten bleiben draußen — der Rest gehört Ihnen.",
    pt: "Tudo o que esta instalação tem sobre si, num ficheiro. As "
        + "credenciais activas ficam de fora; o resto é seu.",
    it: "Tutto ciò che questa installazione ha su di te, in un file. Le "
        + "credenziali attive restano fuori; il resto è tuo.",
    ja: "この導入があなたについて保持しているすべてを一つのファイルに。有効な資格情報は含みません。",
    zh: "本部署持有的关于您的全部内容，汇成一个文件。不含有效凭据，其余都是您的。",
    hi: "यह परिनियोजन आपके बारे में जो कुछ रखता है, एक फ़ाइल में। सक्रिय क्रेडेंशियल शामिल नहीं।",
    ar: "كل ما يحتفظ به هذا النشر عنك، في ملف واحد. لا تُدرج بيانات الاعتماد الفعّالة.",
  },
  "hld.take.go": {
    en: "Download everything", es: "Descargar todo",
    fr: "Tout télécharger", de: "Alles herunterladen",
    pt: "Descarregar tudo", it: "Scaricare tutto",
    ja: "すべてダウンロード", zh: "下载全部",
    hi: "सब कुछ डाउनलोड करें", ar: "تنزيل كل شيء",
  },
  "hld.end": {
    en: "End it", es: "Terminar con todo", fr: "Y mettre fin", de: "Beenden", pt: "Acabar com tudo", it: "Metterci fine", ja: "すべて終わらせる", zh: "结束这一切", hi: "इसे समाप्त करें", ar: "أنهِ كل شيء",
  },
  "hld.end.pitch": {
    en: "Erases everything held about you on this deployment. There is no undo, which is the point of it. Type erase to arm the button.", es: "Borra todo lo que se guarda sobre ti en este despliegue. No hay deshacer, y ese es justamente el punto. Escribe erase para armar el botón.", fr: "Efface tout ce qui est détenu sur vous sur ce déploiement. Il n'y a pas d'annulation, et c'est justement le but. Tapez erase pour armer le bouton.", de: "Löscht alles, was auf diesem Deployment über dich gehalten wird. Es gibt kein Rückgängig, und genau darum geht es. Tipp erase, um den Knopf scharf zu stellen.", pt: "Apaga tudo o que é guardado sobre si neste deployment. Não há como desfazer, e é essa a intenção. Escreva erase para armar o botão.", it: "Cancella tutto ciò che è custodito su di te in questo deployment. Non c'è annullamento, ed è proprio il punto. Digita erase per armare il pulsante.", ja: "この配備であなたについて保持されているすべてを消去します。取り消しはできません — それがこの機能の意味です。ボタンを有効にするには erase と入力してください。", zh: "抹除本部署上关于你的一切。没有撤销，这正是它的意义所在。输入 erase 以启用该按钮。", hi: "इस डिप्लॉयमेंट पर आपके बारे में रखा सब कुछ मिटा देता है। कोई पूर्ववत नहीं, और यही इसका मक़सद है। बटन सक्रिय करने के लिए erase टाइप करें।", ar: "يمحو كل ما هو محفوظ عنك على هذا النشر. لا تراجع، وهذا هو المقصود. اكتب erase لتفعيل الزر.",
  },
  "hld.end.ph": {
    en: "erase", es: "erase", fr: "erase", de: "erase", pt: "erase", it: "erase", ja: "erase", zh: "erase", hi: "erase", ar: "erase",
  },
  "hld.end.go": {
    en: "Erase everything", es: "Borrarlo todo", fr: "Tout effacer", de: "Alles löschen", pt: "Apagar tudo", it: "Cancella tutto", ja: "すべて消去", zh: "抹除一切", hi: "सब कुछ मिटाएँ", ar: "امحُ كل شيء",
  },
  "wrd.paused.mark": {
    en: " · paused", es: " · en pausa", fr: " · en pause", de: " · pausiert", pt: " · em pausa", it: " · in pausa", ja: " · 一時停止中", zh: " · 已暂停", hi: " · रुका हुआ", ar: " · موقوف مؤقتًا",
  },
  "wrd.pause": {
    en: "Pause guidance", es: "Pausar las indicaciones", fr: "Suspendre les conseils", de: "Hinweise pausieren", pt: "Pausar as orientações", it: "Metti in pausa le indicazioni", ja: "案内を一時停止", zh: "暂停指导", hi: "मार्गदर्शन रोकें", ar: "أوقِف الإرشاد مؤقتًا",
  },
  "wrd.resume": {
    en: "Resume guidance", es: "Reanudar la orientación", fr: "Reprendre les conseils", de: "Hinweise fortsetzen", pt: "Retomar a orientação", it: "Riprendi la guida", ja: "ガイダンスを再開", zh: "恢复引导", hi: "मार्गदर्शन जारी रखें", ar: "استأنف الإرشاد",
  },
  "wrd.resus": {
    en: "Automatic resuscitation", es: "Reanimación automática", fr: "Réanimation automatique", de: "Automatische Wiederbelebung", pt: "Reanimação automática", it: "Rianimazione automatica", ja: "自動蘇生", zh: "自动复苏", hi: "स्वचालित पुनर्जीवन", ar: "إنعاش تلقائي",
  },
  "wrd.waiver": {
    en: "Waiver", es: "Renuncia", fr: "Renonciation", de: "Verzicht", pt: "Renúncia", it: "Rinuncia", ja: "免除", zh: "弃权", hi: "छूट", ar: "تنازل",
  },
  "wrd.title": {
    en: "Who you watch", es: "A quién vigilas", fr: "Qui vous veillez", de: "Über wen du wachst", pt: "Quem você vigia", it: "Chi vegli", ja: "見守っている相手", zh: "你在看顾谁", hi: "आप किसका ध्यान रखते हैं", ar: "من ترعاه",
  },
  "wrd.sub": {
    en: "children linked to this account", es: "menores vinculados a esta cuenta", fr: "enfants liés à ce compte", de: "mit diesem Konto verknüpfte Kinder", pt: "crianças ligadas a esta conta", it: "bambini collegati a questo account", ja: "このアカウントに紐付いた子ども", zh: "关联到此账户的孩子", hi: "इस खाते से जुड़े बच्चे", ar: "الأطفال المرتبطون بهذا الحساب",
  },
  "wrd.link": {
    en: "Link a child", es: "Vincular a un menor", fr: "Lier un enfant", de: "Ein Kind verknüpfen", pt: "Ligar uma criança", it: "Collega un bambino", ja: "子どもを紐付ける", zh: "关联一个孩子", hi: "एक बच्चा जोड़ें", ar: "اربط طفلًا",
  },
  "wrd.link.name.ph": {
    en: "Their name", es: "Su nombre", fr: "Son prénom", de: "Ihr Name", pt: "O nome dele", it: "Il suo nome", ja: "その子の名前", zh: "他的名字", hi: "उनका नाम", ar: "اسمه",
  },
  "wrd.link.parent": {
    en: "I am their parent", es: "Soy su madre o padre", fr: "Je suis son parent", de: "Ich bin ein Elternteil", pt: "Sou o pai ou a mãe", it: "Sono un genitore", ja: "私はその子の親です", zh: "我是他的家长", hi: "मैं इनका अभिभावक (माता/पिता) हूँ", ar: "أنا والده",
  },
  "wrd.link.guardian": {
    en: "I am their legal guardian", es: "Soy su tutor legal", fr: "Je suis son tuteur légal", de: "Ich bin gesetzlicher Vormund", pt: "Sou o tutor legal", it: "Sono il tutore legale", ja: "私は法定後見人です", zh: "我是他的法定监护人", hi: "मैं इनका क़ानूनी संरक्षक हूँ", ar: "أنا وصيه القانوني",
  },
  "wrd.link.go": {
    en: "Link", es: "Vincular", fr: "Lier", de: "Verknüpfen", pt: "Ligar", it: "Collega", ja: "紐付ける", zh: "关联", hi: "जोड़ें", ar: "اربط",
  },
  "wrd.link.pitch": {
    en: "The child gets their own account and their own token — this links you to it, it does not make their record yours to read line by line. What you can see is on this page and nothing else.", es: "El menor tiene su propia cuenta y su propio token — esto te vincula a ella, no convierte su registro en algo tuyo para leer línea a línea. Lo que puedes ver está en esta página y nada más.", fr: "L'enfant a son propre compte et son propre jeton — ceci vous y relie, cela ne fait pas de son dossier quelque chose que vous pouvez lire ligne à ligne. Ce que vous pouvez voir est sur cette page et rien d'autre.", de: "Das Kind bekommt ein eigenes Konto und ein eigenes Token — dies verknüpft dich damit, es macht seine Akte nicht zu deiner, Zeile für Zeile zu lesen. Was du sehen kannst, steht auf dieser Seite und sonst nirgends.", pt: "A criança tem a sua própria conta e o seu próprio token — isto liga-o a ela, não torna o registo dela seu para ler linha a linha. O que pode ver está nesta página e mais nada.", it: "Il bambino ha un proprio account e un proprio token — questo ti collega a esso, non rende il suo registro tuo da leggere riga per riga. Ciò che puoi vedere è su questa pagina e nient'altro.", ja: "子どもは自分のアカウントと自分のトークンを持ちます — これはあなたをそこに結びつけるだけで、その子の記録を一行ずつ読める自分のものにするわけではありません。あなたが見られるのはこのページにあるものだけです。", zh: "孩子拥有自己的账户和自己的令牌 — 这只是把你与之关联，并不会让他的记录变成你可以逐行阅读的东西。你能看到的就在本页上，别无其他。", hi: "बच्चे का अपना खाता और अपना टोकन होता है — यह आपको उससे जोड़ता है, उसका रिकॉर्ड आपका नहीं बना देता कि आप पंक्ति-दर-पंक्ति पढ़ें। आप जो देख सकते हैं वह इसी पृष्ठ पर है, और कुछ नहीं।", ar: "للطفل حسابه ورمزه الخاصان — هذا يربطك به، ولا يجعل سجله ملكك لتقرأه سطرًا سطرًا. ما يمكنك رؤيته هو ما في هذه الصفحة لا غير.",
  },
  "wrd.board": {
    en: "The board", es: "El tablero", fr: "Le tableau", de: "Die Tafel", pt: "O painel", it: "Il quadro", ja: "ボード", zh: "看板", hi: "बोर्ड", ar: "اللوحة",
  },
  "wrd.board.none": {
    en: "Nobody linked.", es: "Nadie vinculado.", fr: "Personne de lié.", de: "Niemand verknüpft.", pt: "Ninguém ligado.", it: "Nessuno collegato.", ja: "誰も紐付いていません。", zh: "尚未关联任何人。", hi: "कोई नहीं जुड़ा।", ar: "لا أحد مرتبط.",
  },
  "wrd.board.oversight": {
    en: "{oversight} oversight", es: "supervisión {oversight}", fr: "supervision {oversight}", de: "Aufsicht {oversight}", pt: "supervisão {oversight}", it: "supervisione {oversight}", ja: "見守り {oversight}", zh: "{oversight}监护", hi: "{oversight} निगरानी", ar: "إشراف {oversight}",
  },
  "wrd.board.counts": {
    en: "{critical} critical · {escalations} escalations in the last day", es: "{critical} críticos · {escalations} escalados en el último día", fr: "{critical} critiques · {escalations} escalades sur le dernier jour", de: "{critical} kritisch · {escalations} Eskalationen am letzten Tag", pt: "{critical} críticos · {escalations} escalonamentos no último dia", it: "{critical} critici · {escalations} escalation nell'ultimo giorno", ja: "重大{critical}件 · 直近24時間のエスカレーション{escalations}件", zh: "{critical}项危急 · 最近一天{escalations}次升级", hi: "{critical} गंभीर · पिछले दिन {escalations} एस्केलेशन", ar: "{critical} حرجة · {escalations} تصعيدات في اليوم الأخير",
  },
  "wrd.board.open": {
    en: "Open", es: "Abrir", fr: "Ouvrir", de: "Öffnen", pt: "Abrir", it: "Apri", ja: "開く", zh: "打开", hi: "खोलें", ar: "افتح",
  },
  "wrd.board.quiet": {
    en: "Quiet 9pm–7am", es: "Silencio 21:00–7:00", fr: "Silence 21h–7h", de: "Ruhe 21–7 Uhr", pt: "Silêncio 21h–7h", it: "Silenzio 21–7", ja: "21時〜7時は静かに", zh: "21点至7点静默", hi: "रात 9 से सुबह 7 तक शांत", ar: "هدوء من 9 مساءً إلى 7 صباحًا",
  },
  "wrd.board.unlink": {
    en: "Unlink", es: "Desvincular", fr: "Dissocier", de: "Trennen", pt: "Desvincular", it: "Scollega", ja: "リンク解除", zh: "取消关联", hi: "अनलिंक करें", ar: "إلغاء الربط",
  },
  "wrd.detail": {
    en: "{age} · {relationship} · {oversight} oversight · {sensitivity} sensitivity · {critical} critical events on record", es: "{age} · {relationship} · supervisión {oversight} · sensibilidad {sensitivity} · {critical} eventos críticos registrados", fr: "{age} · {relationship} · supervision {oversight} · sensibilité {sensitivity} · {critical} événements critiques au dossier", de: "{age} · {relationship} · Aufsicht {oversight} · Empfindlichkeit {sensitivity} · {critical} kritische Ereignisse verzeichnet", pt: "{age} · {relationship} · supervisão {oversight} · sensibilidade {sensitivity} · {critical} eventos críticos registados", it: "{age} · {relationship} · supervisione {oversight} · sensibilità {sensitivity} · {critical} eventi critici a registro", ja: "{age} · {relationship} · 見守り {oversight} · 感度 {sensitivity} · 記録上の重大事象{critical}件", zh: "{age} · {relationship} · {oversight}监护 · {sensitivity}敏感度 · 记录在案的危急事件{critical}起", hi: "{age} · {relationship} · {oversight} निगरानी · {sensitivity} संवेदनशीलता · रिकॉर्ड में {critical} गंभीर घटनाएँ", ar: "{age} · {relationship} · إشراف {oversight} · حساسية {sensitivity} · {critical} أحداث حرجة في السجل",
  },
  "wrd.waiver.pitch": {
    en: "A bound, CPR-rated robot will not begin without somebody on scene saying so — unless you sign this, and then it will. Read all of it.", es: "Un robot vinculado y homologado para RCP no empezará sin que alguien presente lo diga — salvo que firmes esto, y entonces sí lo hará. Léelo entero.", fr: "Un robot lié et homologué RCP ne commencera pas sans que quelqu'un sur place le dise — sauf si vous signez ceci, et alors il le fera. Lisez tout.", de: "Ein gebundener, CPR-tauglicher Roboter beginnt nicht, ohne dass jemand vor Ort es sagt — es sei denn, du unterschreibst dies, dann tut er es. Lies alles.", pt: "Um robô vinculado e classificado para RCP não começará sem que alguém no local o diga — a não ser que assine isto, e então começará. Leia tudo.", it: "Un robot vincolato e abilitato alla RCP non inizierà senza che qualcuno sul posto lo dica — a meno che tu non firmi questo, e allora lo farà. Leggilo tutto.", ja: "紐付け済みでCPR対応のロボットは、その場にいる誰かがそう言わない限り開始しません — これに署名した場合を除いて。署名すれば開始します。全文を読んでください。", zh: "已绑定且具备心肺复苏资格的机器人，若无现场有人开口，就不会动手 — 除非你签署本项，届时它会动手。请通读全文。", hi: "बँधा हुआ, CPR-रेटेड रोबोट तब तक शुरू नहीं करेगा जब तक मौक़े पर कोई ऐसा न कहे — सिवाय इसके कि आप इस पर हस्ताक्षर करें, तब वह करेगा। इसे पूरा पढ़ें।", ar: "الآلي المربوط المصنّف للإنعاش لن يبدأ ما لم يقل ذلك أحد في الموقع — إلا إذا وقّعت هذا، عندها سيبدأ. اقرأه كاملًا.",
  },
  "wrd.waiver.signed": {
    en: "Signed as {signature}. Withdrawing restores the confirm-gated behaviour immediately.", es: "Firmado como {signature}. Retirarlo restaura de inmediato el comportamiento con confirmación.", fr: "Signé comme {signature}. Le retrait rétablit immédiatement le comportement soumis à confirmation.", de: "Unterschrieben als {signature}. Ein Widerruf stellt das bestätigungspflichtige Verhalten sofort wieder her.", pt: "Assinado como {signature}. Retirar restaura de imediato o comportamento com confirmação.", it: "Firmato come {signature}. Ritirarlo ripristina subito il comportamento con conferma.", ja: "{signature}として署名済み。撤回すれば、確認を要する挙動が直ちに戻ります。", zh: "已以{signature}签署。撤回后，需确认才动手的行为立即恢复。", hi: "{signature} के रूप में हस्ताक्षरित। वापस लेने पर पुष्टि-आधारित व्यवहार तुरंत लौट आता है।", ar: "موقّع باسم {signature}. السحب يعيد فورًا السلوك المشروط بالتأكيد.",
  },
  "wrd.waiver.withdraw": {
    en: "Withdraw", es: "Retirar", fr: "Retirer", de: "Widerrufen", pt: "Retirar", it: "Ritira", ja: "撤回", zh: "撤回", hi: "वापस लें", ar: "اسحب",
  },
  "wrd.waiver.sig.ph": {
    en: "Type your full name", es: "Escribe tu nombre completo", fr: "Tapez votre nom complet", de: "Gib deinen vollen Namen ein", pt: "Escreva o seu nome completo", it: "Scrivi il tuo nome completo", ja: "氏名を入力してください", zh: "输入你的全名", hi: "अपना पूरा नाम लिखें", ar: "اكتب اسمك الكامل",
  },
  "wrd.waiver.sign": {
    en: "Sign", es: "Firmar", fr: "Signer", de: "Unterschreiben", pt: "Assinar", it: "Firma", ja: "署名する", zh: "签署", hi: "हस्ताक्षर करें", ar: "وقّع",
  },
  "ct.coordinate": {
    en: "Coordinate", es: "Coordinar", fr: "Coordonner", de: "Koordinieren", pt: "Coordenar", it: "Coordina", ja: "調整する", zh: "协调", hi: "समन्वय करें", ar: "نسّق",
  },
  "ct.coordinating": {
    en: "Coordinating…", es: "Coordinando…", fr: "Coordination…", de: "Wird koordiniert …", pt: "A coordenar…", it: "Coordinamento…", ja: "調整しています…", zh: "正在协调…", hi: "समन्वय हो रहा है…", ar: "جارٍ التنسيق…",
  },
  "ct.sealed": {
    en: "sealed in the vault · ", es: "sellado en la bóveda · ", fr: "scellé dans le coffre · ", de: "im Tresor versiegelt · ", pt: "selado no cofre · ", it: "sigillato nel caveau · ", ja: "保管庫に封印済み · ", zh: "已封入保险库 · ", hi: "तिजोरी में सील · ", ar: "مختوم في الخزنة · ",
  },
  "ct.nobody": {
    en: "nobody yet", es: "todavía nadie", fr: "personne pour l'instant", de: "noch niemand", pt: "ainda ninguém", it: "ancora nessuno", ja: "まだ誰もいません", zh: "暂时无人", hi: "अभी कोई नहीं", ar: "لا أحد بعد",
  },
  "ct.title": {
    en: "Care Team", es: "Equipo de cuidados", fr: "Équipe de soins", de: "Betreuungsteam", pt: "Equipa de cuidados", it: "Squadra di cura", ja: "ケアチーム", zh: "照护团队", hi: "देखभाल टीम", ar: "فريق الرعاية",
  },
  "ct.sub": {
    en: "your own QRME organization, coordinated by the Guardian", es: "tu propia organización QRME, coordinada por el Guardián", fr: "votre propre organisation QRME, coordonnée par le Gardien", de: "Deine eigene QRME-Organisation, koordiniert vom Guardian", pt: "a sua própria organização QRME, coordenada pelo Guardião", it: "la tua organizzazione QRME, coordinata dal Guardian", ja: "ガーディアンが取りまとめる、あなた自身のQRME組織", zh: "你自己的 QRME 组织，由守护者统筹", hi: "आपका अपना QRME संगठन, गार्जियन द्वारा समन्वित", ar: "منظمتك الخاصة في QRME، ينسّقها الحارس",
  },
  "ct.link": {
    en: "Link your organization", es: "Vincula tu organización", fr: "Liez votre organisation", de: "Verknüpf deine Organisation", pt: "Ligue a sua organização", it: "Collega la tua organizzazione", ja: "組織を紐付ける", zh: "关联你的组织", hi: "अपना संगठन जोड़ें", ar: "اربط منظمتك",
  },
  "ct.link.pitch": {
    en: "Found the org and staff its desks in QRME first, then paste its id, the desk that speaks for JIM, and your own QRME owner token. The token is stored for coordinations only and deleted when you unlink; it is never shown again.", es: "Funda la organización y dota sus mostradores en QRME primero, luego pega su id, el mostrador que habla por JIM, y tu propio token de propietario de QRME. El token se guarda solo para las coordinaciones y se borra al desvincular; nunca se vuelve a mostrar.", fr: "Fondez l'organisation et dotez ses comptoirs dans QRME d'abord, puis collez son id, le comptoir qui parle pour JIM, et votre propre jeton de propriétaire QRME. Le jeton n'est conservé que pour les coordinations et supprimé au moment de délier ; il n'est jamais réaffiché.", de: "Gründe die Organisation und besetz ihre Schalter zuerst in QRME, füg dann ihre Id ein, den Schalter, der für JIM spricht, und dein eigenes QRME-Inhaber-Token. Das Token wird nur für Koordinationen gespeichert und beim Trennen gelöscht; es wird nie wieder angezeigt.", pt: "Funde a organização e preencha os seus balcões no QRME primeiro, depois cole o id dela, o balcão que fala pelo JIM, e o seu próprio token de proprietário QRME. O token é guardado só para coordenações e apagado quando desligar; nunca é mostrado outra vez.", it: "Fonda l'organizzazione e presidia i suoi banchi in QRME prima, poi incolla il suo id, il banco che parla per JIM, e il tuo token di proprietario QRME. Il token è conservato solo per i coordinamenti ed è cancellato quando scolleghi; non viene mai più mostrato.", ja: "まずQRMEで組織を設立してデスクに人を配置し、その組織ID、JIMを代弁するデスク、そしてあなた自身のQRMEオーナートークンを貼り付けてください。トークンは連携のためだけに保存され、紐付けを外すと削除されます。二度と表示されることはありません。", zh: "请先在 QRME 中创建组织并为其柜台配备人员，然后粘贴组织 id、代表 JIM 发言的柜台，以及你自己的 QRME 所有者令牌。该令牌仅为协同而保存，取消关联时即删除；且绝不会再次显示。", hi: "पहले QRME में संगठन स्थापित करें और उसकी डेस्कों पर लोग बिठाएँ, फिर उसका id, वह डेस्क जो JIM की ओर से बोलती है, और अपना QRME स्वामी टोकन चिपकाएँ। टोकन केवल समन्वय के लिए रखा जाता है और अलग करने पर मिटा दिया जाता है; यह दोबारा कभी नहीं दिखाया जाता।", ar: "أسّس المنظمة وزوّد مكاتبها في QRME أولًا، ثم الصق معرّفها، والمكتب الذي يتحدث باسم JIM، ورمز المالك الخاص بك في QRME. يُخزَّن الرمز للتنسيق فقط ويُحذف عند فك الارتباط؛ ولا يُعرض مرة أخرى أبدًا.",
  },
  "ct.link.org": {
    en: "Org id", es: "Id de la organización", fr: "Id de l'organisation", de: "Organisations-Id", pt: "Id da organização", it: "Id dell'organizzazione", ja: "組織ID", zh: "组织 id", hi: "संगठन id", ar: "معرّف المنظمة",
  },
  "ct.link.org.ph": {
    en: "org_…", es: "org_…", fr: "org_…", de: "org_…", pt: "org_…", it: "org_…", ja: "org_…", zh: "org_…", hi: "org_…", ar: "org_…",
  },
  "ct.link.dept": {
    en: "Department id", es: "Id del departamento", fr: "Id du département", de: "Abteilungs-Id", pt: "Id do departamento", it: "Id del reparto", ja: "部署ID", zh: "部门 id", hi: "विभाग id", ar: "معرّف القسم",
  },
  "ct.link.dept.ph": {
    en: "dep_…", es: "dep_…", fr: "dep_…", de: "dep_…", pt: "dep_…", it: "dep_…", ja: "dep_…", zh: "dep_…", hi: "dep_…", ar: "dep_…",
  },
  "ct.link.token": {
    en: "Your QRME owner token", es: "Tu token de propietario de QRME", fr: "Votre jeton de propriétaire QRME", de: "Dein QRME-Inhaber-Token", pt: "O seu token de proprietário QRME", it: "Il tuo token di proprietario QRME", ja: "あなたのQRMEオーナートークン", zh: "你的 QRME 所有者令牌", hi: "आपका QRME स्वामी टोकन", ar: "رمز مالك QRME الخاص بك",
  },
  "ct.link.token.ph": {
    en: "pasted, never echoed", es: "pegado, nunca mostrado", fr: "collé, jamais réaffiché", de: "eingefügt, nie wieder angezeigt", pt: "colado, nunca mostrado", it: "incollato, mai rimostrato", ja: "貼り付けるのみ、表示はされません", zh: "粘贴即可，绝不回显", hi: "चिपकाया गया, कभी दिखाया नहीं", ar: "يُلصق ولا يُعرض أبدًا",
  },
  "ct.link.go": {
    en: "Link", es: "Vincular", fr: "Lier", de: "Verknüpfen", pt: "Ligar", it: "Collega", ja: "紐付ける", zh: "关联", hi: "जोड़ें", ar: "اربط",
  },
  "ct.linked": {
    en: "Linked", es: "Vinculada", fr: "Liée", de: "Verknüpft", pt: "Ligada", it: "Collegata", ja: "紐付け済み", zh: "已关联", hi: "जुड़ा हुआ", ar: "مرتبطة",
  },
  "ct.linked.line": {
    en: "org {org} · desk {desk} · credential held", es: "org {org} · mostrador {desk} · credencial guardada", fr: "org {org} · comptoir {desk} · identifiant conservé", de: "Org {org} · Schalter {desk} · Zugang hinterlegt", pt: "org {org} · balcão {desk} · credencial guardada", it: "org {org} · banco {desk} · credenziale custodita", ja: "組織 {org} · デスク {desk} · 資格情報を保持", zh: "组织 {org} · 柜台 {desk} · 已持有凭证", hi: "संगठन {org} · डेस्क {desk} · क्रेडेंशियल रखा है", ar: "منظمة {org} · مكتب {desk} · الاعتماد محفوظ",
  },
  "ct.linked.pitch": {
    en: "When a reading drifts outside your band while doses slip, the Guardian takes it to the whole team — once a day at most, on the calm path only. Summaries cross, never raw readings.", es: "Cuando una lectura se sale de tu banda mientras se saltan dosis, el Guardián lo lleva a todo el equipo — una vez al día como mucho, y solo por la vía tranquila. Cruzan resúmenes, nunca lecturas en bruto.", fr: "Quand une mesure sort de votre plage alors que des doses sont manquées, le Gardien porte l'affaire à toute l'équipe — une fois par jour au plus, et seulement par la voie calme. Ce sont des résumés qui circulent, jamais des mesures brutes.", de: "Wenn eine Messung aus deinem Band läuft, während Dosen ausfallen, trägt der Guardian es dem ganzen Team vor — höchstens einmal am Tag und nur auf dem ruhigen Weg. Es kreuzen Zusammenfassungen, nie Rohmessungen.", pt: "Quando uma leitura sai da sua banda enquanto falham doses, o Guardião leva-o à equipa inteira — no máximo uma vez por dia, e só pela via calma. Cruzam resumos, nunca leituras em bruto.", it: "Quando una lettura esce dalla tua banda mentre saltano le dosi, il Guardian la porta a tutta la squadra — al massimo una volta al giorno, solo sulla via calma. Passano riassunti, mai letture grezze.", ja: "服薬が抜けている最中に測定値があなたの帯を外れたとき、ガーディアンはそれをチーム全体に持ち込みます — 一日一度までで、穏やかな経路に限ります。渡るのは要約であり、生の測定値は決して渡りません。", zh: "当读数偏出你的区间、而服药又开始漏掉时，守护者会把这件事带给整个团队 — 每天至多一次，且只走平静通道。跨越的是摘要，绝非原始读数。", hi: "जब कोई रीडिंग आपके बैंड से बाहर जाए और साथ ही ख़ुराकें छूट रही हों, तो गार्जियन इसे पूरी टीम तक ले जाता है — दिन में अधिकतम एक बार, केवल शांत मार्ग से। सारांश जाते हैं, कच्ची रीडिंग कभी नहीं।", ar: "حين تنحرف قراءة خارج نطاقك بينما تُفوَّت الجرعات، يعرضها الحارس على الفريق كله — مرة في اليوم على الأكثر، وعلى المسار الهادئ فقط. تعبر الملخصات، لا القراءات الخام أبدًا.",
  },
  "ct.linked.goal": {
    en: "Take a goal to the team by hand", es: "Llevar un objetivo al equipo a mano", fr: "Porter un objectif à l'équipe à la main", de: "Ein Ziel dem Team von Hand vorlegen", pt: "Levar um objetivo à equipa à mão", it: "Porta un obiettivo alla squadra a mano", ja: "目標を手動でチームに持ち込む", zh: "手动把一个目标带给团队", hi: "कोई लक्ष्य स्वयं टीम तक ले जाएँ", ar: "خذ هدفًا إلى الفريق يدويًا",
  },
  "ct.linked.goal.ph": {
    en: "e.g. plan the recovery week", es: "p. ej. planear la semana de recuperación", fr: "p. ex. planifier la semaine de récupération", de: "z. B. die Erholungswoche planen", pt: "p. ex. planear a semana de recuperação", it: "es. pianificare la settimana di recupero", ja: "例: 回復週間の計画を立てる", zh: "例如：规划康复周", hi: "जैसे: स्वस्थ होने के सप्ताह की योजना", ar: "مثلًا: خطط لأسبوع التعافي",
  },
  "ct.linked.unlink": {
    en: "Unlink", es: "Desvincular", fr: "Dissocier", de: "Trennen", pt: "Desvincular", it: "Scollega", ja: "リンク解除", zh: "取消关联", hi: "अनलिंक करें", ar: "إلغاء الربط",
  },
  "ct.plans.none": {
    en: "No joint plans yet.", es: "Todavía no hay planes conjuntos.", fr: "Pas encore de plans conjoints.", de: "Noch keine gemeinsamen Pläne.", pt: "Ainda não há planos conjuntos.", it: "Ancora nessun piano congiunto.", ja: "共同の計画はまだありません。", zh: "尚无联合计划。", hi: "अभी कोई संयुक्त योजना नहीं।", ar: "لا خطط مشتركة بعد.",
  },
  "ct.spec": {
    en: "Specialists — attach a QRME expert", es: "Especialistas — adjunta un experto de QRME", fr: "Spécialistes — rattachez un expert QRME", de: "Spezialisten — einen QRME-Experten anhängen", pt: "Especialistas — anexe um perito QRME", it: "Specialisti — collega un esperto QRME", ja: "専門家 — QRMEのエキスパートを紐付ける", zh: "专家 — 挂接一位 QRME 专家", hi: "विशेषज्ञ — एक QRME विशेषज्ञ जोड़ें", ar: "المختصون — أرفق خبير QRME",
  },
  "ct.spec.pitch": {
    en: "The Starter Collection: one expert per industry, each already carrying its industry's knowledge pack. Pick who stands behind each condition — guidance for it then routes through them in tandem. The mental-health trio is played straight on purpose.", es: "La Colección Inicial: un experto por sector, cada uno con el paquete de conocimiento de su sector. Elige quién respalda cada condición — la orientación para ella pasa entonces por él en tándem. El trío de salud mental se interpreta en serio, a propósito.", fr: "La Collection de départ : un expert par secteur, chacun portant déjà le pack de savoir de son secteur. Choisissez qui se tient derrière chaque situation — les conseils la concernant passent alors par lui en tandem. Le trio santé mentale est joué au premier degré, à dessein.", de: "Die Starter-Sammlung: ein Experte je Branche, jeder bereits mit dem Wissenspaket seiner Branche. Wähl, wer hinter jedem Zustand steht — die Beratung dazu läuft dann im Tandem über ihn. Das Trio für psychische Gesundheit wird absichtlich ernst gespielt.", pt: "A Coleção Inicial: um perito por setor, cada um já com o pacote de conhecimento do seu setor. Escolha quem está por trás de cada condição — a orientação para ela passa então por ele em tandem. O trio de saúde mental é levado a sério de propósito.", it: "La Collezione iniziale: un esperto per settore, ciascuno già con il pacchetto di conoscenza del suo settore. Scegli chi sta dietro a ogni condizione — la guida per quella passa poi attraverso di lui in tandem. Il trio della salute mentale è interpretato sul serio, di proposito.", ja: "スターターコレクション：業種ごとに一人の専門家がいて、それぞれ自分の業種の知識パックをすでに携えています。各症状の背後に誰が立つかを選んでください — その症状への助言は、以後タンデムでその専門家を経由します。メンタルヘルスの三人組は、意図してまっすぐに演じられています。", zh: "入门合集：每个行业一位专家，各自已随身带着本行业的知识包。挑选由谁来支撑每一种状况 — 针对它的指导此后就会串联着经由这位专家。心理健康三人组是刻意认真对待的。", hi: "स्टार्टर संग्रह: हर उद्योग के लिए एक विशेषज्ञ, हर एक अपने उद्योग का ज्ञान-पैक पहले से लिए हुए। चुनें कि हर स्थिति के पीछे कौन खड़ा हो — फिर उसके लिए मार्गदर्शन उसी के ज़रिए टेंडम में जाता है। मानसिक-स्वास्थ्य की तिकड़ी जान-बूझकर पूरी गंभीरता से निभाई गई है।", ar: "المجموعة الأولى: خبير لكل قطاع، كلٌّ يحمل مسبقًا حزمة معرفة قطاعه. اختر من يقف خلف كل حالة — عندها يمر الإرشاد الخاص بها عبره بالترادف. ثلاثي الصحة النفسية مؤدّى بجدية عن قصد.",
  },
  "ct.spec.choose": {
    en: "choose an expert…", es: "elige un experto…", fr: "choisissez un expert…", de: "einen Experten wählen…", pt: "escolha um perito…", it: "scegli un esperto…", ja: "専門家を選ぶ…", zh: "选择一位专家…", hi: "विशेषज्ञ चुनें…", ar: "اختر خبيرًا…",
  },
  "ct.spec.attach": {
    en: "Attach", es: "Adjuntar", fr: "Rattacher", de: "Anhängen", pt: "Anexar", it: "Collega", ja: "紐付ける", zh: "挂接", hi: "जोड़ें", ar: "أرفق",
  },
  "ct.spec.empty": {
    en: "The QRME tandem answered with an empty shelf — install the Starter Collection there (Discover → Install), then reload.", es: "El tándem de QRME respondió con un estante vacío — instala allí la Colección Inicial (Descubrir → Instalar) y luego recarga.", fr: "Le tandem QRME a répondu avec une étagère vide — installez-y la Collection de départ (Découvrir → Installer), puis rechargez.", de: "Das QRME-Tandem antwortete mit einem leeren Regal — installier dort die Starter-Sammlung (Entdecken → Installieren) und lad neu.", pt: "O tandem QRME respondeu com uma prateleira vazia — instale lá a Coleção Inicial (Descobrir → Instalar) e recarregue.", it: "Il tandem QRME ha risposto con uno scaffale vuoto — installa lì la Collezione iniziale (Scopri → Installa), poi ricarica.", ja: "QRMEタンデムは空の棚を返しました — 向こうでスターターコレクションを導入し（Discover → Install）、再読み込みしてください。", zh: "QRME 串联端返回的是一个空货架 — 请先在那边安装入门合集（发现 → 安装），然后重新加载。", hi: "QRME टेंडम ने ख़ाली शेल्फ़ लौटाया — वहाँ स्टार्टर संग्रह इंस्टॉल करें (Discover → Install), फिर पुनः लोड करें।", ar: "أجاب ترادف QRME برفٍّ فارغ — ثبّت المجموعة الأولى هناك (Discover ← Install)، ثم أعد التحميل.",
  },
  "ct.spec.find.capped": {
    en: "Showing the first {n} — narrower words will reach the rest.", es: "Se muestran los primeros {n}: con palabras más precisas verá el resto.", fr: "Les {n} premiers sont affichés — des mots plus précis atteindront les autres.", de: "Die ersten {n} werden gezeigt — genauere Wörter erreichen die übrigen.", pt: "A mostrar os primeiros {n} — palavras mais precisas alcançam os restantes.", it: "Mostra i primi {n}: parole più precise raggiungeranno gli altri.", ja: "最初の {n} 件を表示しています。絞った言葉で残りに届きます。", zh: "显示前 {n} 条——用更精确的词可以找到其余的。", hi: "पहले {n} दिखाए जा रहे हैं — अधिक सटीक शब्दों से बाकी तक पहुँचेंगे।", ar: "تُعرض أول {n} — كلمات أدقّ تصل إلى الباقي.",
  },
  "ct.spec.find.go": {
    en: "Search", es: "Buscar", fr: "Rechercher", de: "Suchen", pt: "Procurar", it: "Cerca", ja: "検索", zh: "搜索", hi: "खोजें", ar: "ابحث",
  },
  "ct.spec.find.hint": {
    en: "a name, an industry, a @handle, or a prof_… id", es: "un nombre, un sector, un @alias o un id prof_…", fr: "un nom, un secteur, un @pseudo ou un identifiant prof_…", de: "ein Name, eine Branche, ein @Handle oder eine prof_…-ID", pt: "um nome, um setor, um @identificador ou um id prof_…", it: "un nome, un settore, un @handle o un id prof_…", ja: "名前、業種、@ハンドル、または prof_… の ID", zh: "姓名、行业、@handle，或 prof_… 开头的 id", hi: "नाम, उद्योग, कोई @handle, या prof_… वाला id", ar: "اسم أو مجال أو @معرّف أو رقم prof_…",
  },
  "ct.spec.find.none": {
    en: "Nothing matched that.", es: "Nada coincidió con eso.", fr: "Rien ne correspond.", de: "Dazu passte nichts.", pt: "Nada correspondeu a isso.", it: "Non ha trovato nulla.", ja: "一致するものはありませんでした。", zh: "没有匹配的结果。", hi: "उससे कुछ मेल नहीं खाया।", ar: "لم يطابق ذلك شيء.",
  },
  "ct.spec.other": {
    en: "Someone not on the shelf", es: "Alguien que no está en el estante", fr: "Quelqu'un qui n'est pas sur l'étagère", de: "Jemand, der nicht im Regal steht", pt: "Alguém que não está na prateleira", it: "Qualcuno che non è sullo scaffale", ja: "棚にいない人", zh: "货架上没有的人", hi: "शेल्फ़ पर मौजूद नहीं कोई", ar: "شخص ليس على الرفّ",
  },
  "ct.spec.stand.adults_only": {
    en: "age-restricted — answers for an adult only", es: "con restricción de edad: solo responde a personas adultas", fr: "réservé aux adultes — ne répond qu'à une personne majeure", de: "altersbeschränkt — antwortet nur Erwachsenen", pt: "com restrição de idade — só responde a adultos", it: "riservato agli adulti: risponde solo a una persona adulta", ja: "年齢制限つき — 成人にのみ応じます", zh: "有年龄限制——仅为成年人作答", hi: "आयु-प्रतिबंधित — केवल वयस्क के लिए जवाब देता है", ar: "مقيَّد بالعمر — يجيب البالغين وحدهم",
  },
  "ct.spec.stand.departed": {
    en: "has departed — cannot stand behind a condition", es: "ha fallecido: no puede respaldar una afección", fr: "s'en est allé — ne peut pas répondre d'une condition", de: "ist verstorben — kann für kein Anliegen einstehen", pt: "partiu — não pode responder por uma condição", it: "se n'è andato: non può farsi carico di una condizione", ja: "旅立ちました — 症状を受け持てません", zh: "已离世——无法为某个状况把关", hi: "जा चुके हैं — किसी स्थिति के पीछे खड़े नहीं हो सकते", ar: "قد رحل — لا يستطيع أن يقف خلف حالة",
  },
  "ct.spec.stand.not_active": {
    en: "not active on QRME", es: "no está activo en QRME", fr: "pas actif sur QRME", de: "auf QRME nicht aktiv", pt: "não está ativo no QRME", it: "non è attivo su QRME", ja: "QRME で有効ではありません", zh: "在 QRME 上并非活跃状态", hi: "QRME पर सक्रिय नहीं", ar: "غير نشط على QRME",
  },
  "ct.spec.stand.unreachable": {
    en: "QRME unreachable — standing unknown", es: "QRME inaccesible: situación desconocida", fr: "QRME injoignable — état inconnu", de: "QRME nicht erreichbar — Stand unbekannt", pt: "QRME inacessível — situação desconhecida", it: "QRME irraggiungibile: posizione ignota", ja: "QRME に接続できません — 状態は不明です", zh: "无法连接 QRME——状态未知", hi: "QRME तक पहुँच नहीं — स्थिति अज्ञात", ar: "تعذّر الوصول إلى QRME — الحالة غير معروفة",
  },
  "sfy.delivered": {
    en: "delivered", es: "entregado", fr: "remis", de: "zugestellt", pt: "entregue", it: "consegnato", ja: "配信済み", zh: "已送达", hi: "पहुँचा दिया गया", ar: "تم التسليم",
  },
  "sfy.undelivered": {
    en: "not delivered", es: "no entregado", fr: "non remis", de: "nicht zugestellt", pt: "não entregue", it: "non consegnato", ja: "未配信", zh: "未送达", hi: "नहीं पहुँचा", ar: "لم يُسلَّم",
  },
  "sfy.title": {
    en: "Safety", es: "Seguridad", fr: "Sécurité", de: "Sicherheit", pt: "Segurança", it: "Sicurezza", ja: "安全", zh: "安全", hi: "सुरक्षा", ar: "السلامة",
  },
  "sfy.help": {
    en: "Get help now", es: "Pide ayuda ahora", fr: "Demander de l'aide maintenant", de: "Jetzt Hilfe holen", pt: "Pede ajuda agora", it: "Chiedi aiuto adesso", ja: "今すぐ助けを呼ぶ", zh: "立即求助", hi: "अभी मदद बुलाएँ", ar: "اطلب المساعدة الآن",
  },
  "sfy.help.pitch": {
    en: "One press reaches everything JIM can reach on your behalf — your emergency contact, your Medical ID, first aid, every connected device — and says plainly what it cannot do itself.", es: "Una pulsación llega a todo lo que JIM puede alcanzar por ti — tu contacto de emergencia, tu ficha médica, primeros auxilios, cada dispositivo conectado — y dice claramente lo que no puede hacer por sí mismo.", fr: "Une pression atteint tout ce que JIM peut atteindre pour vous — votre contact d'urgence, votre fiche médicale, les premiers secours, chaque appareil connecté — et dit clairement ce qu'il ne peut pas faire lui-même.", de: "Ein Druck erreicht alles, was JIM für dich erreichen kann — deinen Notfallkontakt, deinen Medizinausweis, Erste Hilfe, jedes verbundene Gerät — und sagt klar, was es selbst nicht kann.", pt: "Um toque alcança tudo o que o JIM pode alcançar por ti — o teu contacto de emergência, a tua ficha médica, primeiros socorros, cada dispositivo ligado — e diz claramente o que não pode fazer sozinho.", it: "Una pressione raggiunge tutto ciò che JIM può raggiungere per te — il tuo contatto di emergenza, la tua scheda medica, il primo soccorso, ogni dispositivo collegato — e dice chiaramente cosa non può fare da solo.", ja: "ワンタップで、JIMが代わりに届けられるすべて — 緊急連絡先、メディカルID、応急処置、接続されたすべてのデバイス — に届きます。そして自分でできないことは、はっきりそう言います。", zh: "一次按下即可触达 JIM 能替你触达的一切 — 紧急联系人、医疗卡、急救指引、每台已连接设备 — 并明确说明它自己做不到的事。", hi: "एक दबाव में JIM आपकी ओर से जो कुछ पहुँचा सकता है सब पहुँचता है — आपातकालीन संपर्क, मेडिकल आईडी, प्राथमिक उपचार, हर जुड़ा उपकरण — और जो वह खुद नहीं कर सकता, साफ़ कह देता है।", ar: "بضغطة واحدة يصل JIM إلى كل ما يمكنه الوصول إليه نيابةً عنك — جهة اتصال الطوارئ، البطاقة الطبية، الإسعافات الأولية، كل جهاز متصل — ويقول بوضوح ما لا يستطيع فعله بنفسه.",
  },
  "sfy.help.ph": {
    en: "What is happening? (optional)", es: "¿Qué está pasando? (opcional)", fr: "Que se passe-t-il ? (facultatif)", de: "Was ist los? (optional)", pt: "O que se passa? (opcional)", it: "Cosa sta succedendo? (facoltativo)", ja: "何が起きていますか？（任意）", zh: "发生了什么？（可选）", hi: "क्या हो रहा है? (वैकल्पिक)", ar: "ماذا يحدث؟ (اختياري)",
  },
  "sfy.help.go": {
    en: "Send for help", es: "Enviar por ayuda", fr: "Envoyer chercher de l'aide", de: "Hilfe losschicken", pt: "Mandar buscar ajuda", it: "Manda a chiamare aiuto", ja: "助けを送る", zh: "派出求助", hi: "मदद भेजें", ar: "أرسل طلب المساعدة",
  },
  "sfy.help.contacted": {
    en: "{who} has been notified.", es: "{who} ha sido avisado.", fr: "{who} a été prévenu.", de: "{who} wurde benachrichtigt.", pt: "{who} foi avisado.", it: "{who} è stato avvisato.", ja: "{who}に通知しました。", zh: "已通知 {who}。", hi: "{who} को सूचित कर दिया गया है।", ar: "تم إبلاغ {who}.",
  },
  "sfy.help.nocontact": {
    en: "No emergency contact is on record — add one in your profile.", es: "No hay contacto de emergencia registrado — añade uno en tu perfil.", fr: "Aucun contact d'urgence enregistré — ajoutez-en un dans votre profil.", de: "Kein Notfallkontakt hinterlegt — trag einen im Profil ein.", pt: "Não há contacto de emergência registado — adiciona um no teu perfil.", it: "Nessun contatto di emergenza registrato — aggiungine uno nel profilo.", ja: "緊急連絡先が登録されていません — プロフィールで追加してください。", zh: "未登记紧急联系人 — 请在个人资料中添加。", hi: "कोई आपातकालीन संपर्क दर्ज नहीं है — अपनी प्रोफ़ाइल में जोड़ें।", ar: "لا توجد جهة اتصال طوارئ مسجلة — أضف واحدة في ملفك.",
  },
  "sfy.help.devices": {
    en: "{n} connected device(s) alerted.", es: "{n} dispositivo(s) conectado(s) avisado(s).", fr: "{n} appareil(s) connecté(s) alerté(s).", de: "{n} verbundene(s) Gerät(e) alarmiert.", pt: "{n} dispositivo(s) ligado(s) alertado(s).", it: "{n} dispositivo/i collegato/i avvisato/i.", ja: "接続されたデバイス{n}台に警報を送りました。", zh: "已警示 {n} 台已连接设备。", hi: "{n} जुड़े उपकरण(ों) को सतर्क किया गया।", ar: "تم تنبيه {n} من الأجهزة المتصلة.",
  },
  "sfy.auto": {
    en: "When you can't answer", es: "Cuando no puedas responder", fr: "Quand vous ne pouvez pas répondre", de: "Wenn du nicht antworten kannst", pt: "Quando não consegues responder", it: "Quando non puoi rispondere", ja: "応答できないとき", zh: "当你无法应答时", hi: "जब आप जवाब न दे सकें", ar: "عندما لا تستطيع الرد",
  },
  "sfy.auto.on": {
    en: "Armed: {who} is contacted after {n} unanswered check-ins.", es: "Armado: se contacta a {who} tras {n} avisos sin respuesta.", fr: "Armé : {who} est contacté après {n} appels sans réponse.", de: "Scharf: {who} wird nach {n} unbeantworteten Nachfragen kontaktiert.", pt: "Armado: {who} é contactado após {n} verificações sem resposta.", it: "Attivo: {who} viene contattato dopo {n} richieste senza risposta.", ja: "作動中：応答のない確認が{n}回続くと{who}に連絡します。", zh: "已布防：{n} 次询问无应答后将联系 {who}。", hi: "सक्रिय: {n} अनुत्तरित पूछताछ के बाद {who} से संपर्क किया जाएगा।", ar: "مفعّل: يتم الاتصال بـ {who} بعد {n} من الاستفسارات دون رد.",
  },
  "sfy.auto.also": {
    en: "An emergency-services dispatch request is recorded too.", es: "También se registra una solicitud de envío a los servicios de emergencia.", fr: "Une demande d'envoi aux services d'urgence est aussi enregistrée.", de: "Auch eine Anforderung an den Rettungsdienst wird festgehalten.", pt: "Também fica registado um pedido de envio aos serviços de emergência.", it: "Viene registrata anche una richiesta di invio ai servizi di emergenza.", ja: "救急サービスへの出動要請も記録されます。", zh: "同时会记录一份紧急服务派遣请求。", hi: "आपातकालीन सेवाओं को भेजने का अनुरोध भी दर्ज होता है।", ar: "يُسجَّل أيضًا طلب إرسال إلى خدمات الطوارئ.",
  },
  "sfy.auto.off": {
    en: "The crash watch is not armed. Arm it on Your Baseline — name a trusted person while you are fine, and it fires only when you cannot answer.", es: "La vigilancia de colapso no está armada. Ármala en Tu línea base — nombra a alguien de confianza mientras estás bien, y solo actúa cuando no puedas responder.", fr: "La veille d'effondrement n'est pas armée. Armez-la dans Votre référence — nommez une personne de confiance pendant que tout va bien, elle n'agit que si vous ne pouvez pas répondre.", de: "Die Sturzwache ist nicht scharf. Aktiviere sie unter Deine Basislinie — benenne eine Vertrauensperson, solange es dir gut geht; sie greift nur, wenn du nicht antworten kannst.", pt: "A vigilância de colapso não está armada. Arma-a em A tua linha de base — nomeia alguém de confiança enquanto estás bem, e só dispara quando não consegues responder.", it: "La vigilanza da collasso non è attiva. Attivala in La tua linea di base — nomina una persona fidata mentre stai bene; scatta solo quando non puoi rispondere.", ja: "クラッシュウォッチは未設定です。「あなたのベースライン」で設定してください — 元気なうちに信頼できる人を指名し、応答できないときだけ作動します。", zh: "跌倒守护尚未布防。请在“你的基线”中布防 — 趁你安好时指定一位可信的人，只有当你无法应答时才会触发。", hi: "क्रैश वॉच सक्रिय नहीं है। इसे 'आपकी बेसलाइन' पर सक्रिय करें — ठीक रहते हुए किसी भरोसेमंद व्यक्ति को नामित करें; यह तभी चलती है जब आप जवाब न दे सकें।", ar: "مراقبة الانهيار غير مفعّلة. فعّلها في «خط الأساس» — سمِّ شخصًا موثوقًا وأنت بخير، ولا تعمل إلا عندما لا تستطيع الرد.",
  },
  "sfy.beacons.bystander": {
    en: "A beacon is the bystander's path — for somebody who finds you. If you can press anything yourself, Get help now above is the door.", es: "Una baliza es el camino del transeúnte — para quien te encuentre. Si tú puedes pulsar algo, la puerta es Pide ayuda ahora, arriba.", fr: "Une balise est la voie du passant — pour la personne qui vous trouve. Si vous pouvez appuyer vous-même, la porte est Demander de l'aide maintenant, ci-dessus.", de: "Ein Beacon ist der Weg für Umstehende — für jemanden, der dich findet. Wenn du selbst etwas drücken kannst, ist Jetzt Hilfe holen oben die Tür.", pt: "Um farol é o caminho de quem passa — para quem te encontrar. Se tu próprio consegues tocar em algo, a porta é Pede ajuda agora, acima.", it: "Un beacon è la via del passante — per chi ti trova. Se puoi premere qualcosa da solo, la porta è Chiedi aiuto adesso, qui sopra.", ja: "ビーコンは通りがかりの人のための道です — あなたを見つけた誰かのために。自分で押せるなら、上の「今すぐ助けを呼ぶ」が入口です。", zh: "信标是旁人的通道 — 供发现你的人使用。如果你自己还能按下按钮，上方的“立即求助”才是入口。", hi: "बीकन राहगीर का रास्ता है — जो आपको पाए उसके लिए। अगर आप खुद कुछ दबा सकते हैं, तो ऊपर 'अभी मदद बुलाएँ' ही दरवाज़ा है।", ar: "المنارة طريق المارّ — لمن يجدك. إن كنت تستطيع الضغط بنفسك، فالباب هو «اطلب المساعدة الآن» أعلاه.",
  },
  "sfy.signin": {
    en: "Sign in to see safety.", es: "Inicia sesión para ver la seguridad.", fr: "Connectez-vous pour voir la sécurité.", de: "Meld dich an, um Sicherheit zu sehen.", pt: "Inicie sessão para ver a segurança.", it: "Accedi per vedere la sicurezza.", ja: "安全画面を見るにはサインインしてください。", zh: "请登录以查看安全页面。", hi: "सुरक्षा देखने के लिए साइन इन करें।", ar: "سجّل الدخول لعرض السلامة.",
  },
  "sfy.needs": {
    en: "Needs a person", es: "Necesita a una persona", fr: "Demande une personne", de: "Braucht einen Menschen", pt: "Precisa de uma pessoa", it: "Serve una persona", ja: "人の対応が必要", zh: "需要有人处理", hi: "किसी व्यक्ति की ज़रूरत", ar: "يحتاج إلى شخص",
  },
  "sfy.needs.none": {
    en: "Nothing open. Nobody is waiting.", es: "Nada abierto. Nadie está esperando.", fr: "Rien d'ouvert. Personne n'attend.", de: "Nichts offen. Niemand wartet.", pt: "Nada em aberto. Ninguém está à espera.", it: "Niente di aperto. Nessuno sta aspettando.", ja: "未対応はありません。待っている人はいません。", zh: "没有未结事项。无人在等待。", hi: "कुछ खुला नहीं। कोई प्रतीक्षा में नहीं।", ar: "لا شيء مفتوح. لا أحد ينتظر.",
  },
  "sfy.onway": {
    en: "{who} is on the way.", es: "{who} va en camino.", fr: "{who} est en route.", de: "{who} ist unterwegs.", pt: "{who} vem a caminho.", it: "{who} sta arrivando.", ja: "{who}が向かっています。", zh: "{who}正在赶来。", hi: "{who} रास्ते में हैं।", ar: "{who} في الطريق.",
  },
  "sfy.responder.ph": {
    en: "Who is going?", es: "¿Quién va?", fr: "Qui y va ?", de: "Wer geht hin?", pt: "Quem vai?", it: "Chi ci va?", ja: "誰が行きますか？", zh: "谁去？", hi: "कौन जा रहा है?", ar: "من سيذهب؟",
  },
  "sfy.going": {
    en: "I'm going", es: "Voy yo", fr: "J'y vais", de: "Ich gehe", pt: "Vou eu", it: "Ci vado io", ja: "私が行きます", zh: "我去", hi: "मैं जा रहा हूँ", ar: "سأذهب أنا",
  },
  // The one sentence on this screen that changes what somebody does next, so
  // it is chrome this console writes and translates rather than server prose
  // rendered verbatim — the same call jim/api.py made for the stranger's page.
  "sfy.cannotdial": {
    en: "JIM cannot call for help. If this is an emergency, dial your local emergency number yourself.", es: "JIM no puede llamar pidiendo ayuda. Si esto es una emergencia, marca tú mismo el número de emergencias local.", fr: "JIM ne peut pas appeler les secours. En cas d'urgence, composez vous-même le numéro d'urgence local.", de: "JIM kann keine Hilfe rufen. Wähl im Notfall selbst die örtliche Notrufnummer.", pt: "O JIM não pode pedir ajuda por telefone. Se for uma emergência, ligue você mesmo para o número de emergência local.", it: "JIM non può chiamare i soccorsi. Se è un'emergenza, componi tu il numero di emergenza locale.", ja: "JIMは助けを呼ぶことができません。緊急の場合は、ご自身で地域の緊急通報番号にかけてください。", zh: "JIM 无法代为呼救。如属紧急情况，请自行拨打当地急救电话。", hi: "JIM मदद के लिए कॉल नहीं कर सकता। यदि यह आपात स्थिति है, तो स्वयं अपना स्थानीय आपातकालीन नंबर डायल करें।", ar: "لا يستطيع JIM طلب المساعدة هاتفيًا. إذا كانت هذه حالة طارئة، فاتصل بنفسك برقم الطوارئ المحلي.",
  },
  "sfy.escalate": {
    en: "Escalate", es: "Escalar", fr: "Escalader", de: "Eskalieren", pt: "Escalar", it: "Aumenta il livello", ja: "エスカレート", zh: "升级", hi: "आगे बढ़ाएँ", ar: "صعّद",
  },
  "sfy.clear": {
    en: "Clear", es: "Cerrar", fr: "Clore", de: "Abschließen", pt: "Encerrar", it: "Chiudi", ja: "解除", zh: "解除", hi: "बंद करें", ar: "أغلق",
  },
  "sfy.beacons": {
    en: "Beacons", es: "Balizas", fr: "Balises", de: "Baken", pt: "Balizas", it: "Beacon", ja: "ビーコン", zh: "信标", hi: "बीकन", ar: "المنارات",
  },
  "sfy.beacons.pitch": {
    en: "A sticker someone can scan to reach help on your behalf. The scanner needs no account and sees only what you chose to put on the card.", es: "Una pegatina que alguien puede escanear para pedir ayuda en tu nombre. Quien escanea no necesita cuenta y solo ve lo que decidiste poner en la tarjeta.", fr: "Un autocollant que quelqu'un peut scanner pour appeler de l'aide en votre nom. Le scanneur n'a besoin d'aucun compte et ne voit que ce que vous avez choisi de mettre sur la carte.", de: "Ein Aufkleber, den jemand scannen kann, um in deinem Namen Hilfe zu holen. Wer scannt, braucht kein Konto und sieht nur, was du auf die Karte setzen wolltest.", pt: "Um autocolante que alguém pode digitalizar para pedir ajuda em seu nome. Quem digitaliza não precisa de conta e vê apenas o que escolheu pôr no cartão.", it: "Un adesivo che qualcuno può scansionare per chiedere aiuto per te. Chi scansiona non ha bisogno di account e vede solo ciò che hai scelto di mettere sulla scheda.", ja: "誰かがスキャンして、あなたに代わって助けを呼べるステッカーです。スキャンする人にアカウントは要らず、見えるのはあなたがカードに載せると決めたものだけです。", zh: "一张贴纸，别人扫一下就能代你求助。扫描者无需账户，只能看到你选择放上卡片的内容。", hi: "एक स्टिकर जिसे कोई स्कैन करके आपकी ओर से मदद बुला सके। स्कैन करने वाले को खाता नहीं चाहिए और उसे केवल वही दिखता है जो आपने कार्ड पर रखना चुना।", ar: "ملصق يمكن لأحد مسحه ليطلب النجدة نيابة عنك. الماسح لا يحتاج حسابًا ولا يرى إلا ما اخترت وضعه على البطاقة.",
  },
  "sfy.beacons.scans": {
    en: "{n} scan{s}", es: "{n} escaneos", fr: "{n} scans", de: "{n} Scans", pt: "{n} digitalizações", it: "{n} scansioni", ja: "スキャン{n}件", zh: "{n}次扫描", hi: "{n} स्कैन", ar: "{n} مسحة",
  },
  "sfy.beacons.retired": {
    en: "retired", es: "retirada", fr: "retirée", de: "zurückgezogen", pt: "retirada", it: "ritirato", ja: "引退済み", zh: "已退役", hi: "सेवानिवृत्त", ar: "متقاعد",
  },
  "sfy.beacons.label.ph": {
    en: "Label (Front door)", es: "Etiqueta (Puerta principal)", fr: "Étiquette (Porte d'entrée)", de: "Beschriftung (Haustür)", pt: "Etiqueta (Porta da frente)", it: "Etichetta (Porta d'ingresso)", ja: "ラベル（玄関）", zh: "标签（前门）", hi: "लेबल (मुख्य द्वार)", ar: "التسمية (الباب الأمامي)",
  },
  "sfy.beacons.where.ph": {
    en: "Where it is (optional)", es: "Dónde está (opcional)", fr: "Où elle est (facultatif)", de: "Wo sie ist (optional)", pt: "Onde está (opcional)", it: "Dov'è (facoltativo)", ja: "設置場所（任意）", zh: "它在哪里（可选）", hi: "यह कहाँ है (वैकल्पिक)", ar: "أين هي (اختياري)",
  },
  "sfy.beacons.place": {
    en: "Place a beacon", es: "Colocar una baliza", fr: "Poser une balise", de: "Eine Bake platzieren", pt: "Colocar uma baliza", it: "Colloca un beacon", ja: "ビーコンを設置", zh: "放置信标", hi: "बीकन रखें", ar: "ضع منارة",
  },
  "sfy.pages": {
    en: "What went out", es: "Lo que salió", fr: "Ce qui est parti", de: "Was hinausging", pt: "O que saiu", it: "Cosa è uscito", ja: "送信されたもの", zh: "发出去的内容", hi: "क्या भेजा गया", ar: "ما الذي خرج",
  },
  "sfy.pages.pitch": {
    en: "Every page JIM sent on your behalf, and whether it arrived. Shown because a message that failed to deliver is the one you most need to know about.", es: "Cada aviso que JIM envió en tu nombre, y si llegó. Se muestra porque un mensaje que no se entregó es justo el que más necesitas conocer.", fr: "Chaque appel que JIM a envoyé en votre nom, et s'il est arrivé. Affiché parce qu'un message non délivré est celui qu'il faut le plus connaître.", de: "Jede Benachrichtigung, die JIM in deinem Namen sandte, und ob sie ankam. Gezeigt, weil eine nicht zugestellte Nachricht genau die ist, von der du wissen musst.", pt: "Cada aviso que o JIM enviou em seu nome, e se chegou. Mostrado porque uma mensagem que falhou a entrega é a que mais precisa de conhecer.", it: "Ogni avviso che JIM ha inviato per te, e se è arrivato. Mostrato perché un messaggio non consegnato è proprio quello che più ti serve sapere.", ja: "JIMがあなたに代わって送ったすべての呼び出しと、それが届いたかどうか。届かなかったメッセージこそ、最も知る必要があるものだからです。", zh: "JIM 代你发出的每一次呼叫，以及它是否送达。之所以展示，是因为没能送达的那条消息，正是你最需要知道的。", hi: "JIM ने आपकी ओर से भेजा हर संदेश, और वह पहुँचा या नहीं। इसलिए दिखाया गया क्योंकि जो संदेश पहुँच न सका, उसी के बारे में जानना सबसे ज़रूरी है।", ar: "كل نداء أرسله JIM نيابة عنك، وهل وصل. يُعرض لأن الرسالة التي أخفقت في الوصول هي أكثر ما تحتاج معرفته.",
  },
  "sfy.pages.none": {
    en: "No pages sent.", es: "No se enviaron avisos.", fr: "Aucun appel envoyé.", de: "Keine Benachrichtigungen gesendet.", pt: "Nenhum aviso enviado.", it: "Nessun avviso inviato.", ja: "送信された呼び出しはありません。", zh: "未发出任何呼叫。", hi: "कोई संदेश नहीं भेजा गया।", ar: "لم تُرسل أي نداءات.",
  },
  "sfy.history": {
    en: "History", es: "Historial", fr: "Historique", de: "Verlauf", pt: "Histórico", it: "Cronologia", ja: "履歴", zh: "历史", hi: "इतिहास", ar: "السجل",
  },
  "sfy.history.none": {
    en: "Nothing has happened yet.", es: "No ha pasado nada todavía.", fr: "Rien ne s'est encore passé.", de: "Bisher ist nichts geschehen.", pt: "Ainda não aconteceu nada.", it: "Non è ancora successo nulla.", ja: "まだ何も起きていません。", zh: "尚未发生任何事。", hi: "अभी कुछ नहीं हुआ।", ar: "لم يحدث شيء بعد.",
  },
  "sfy.history.cleared": {
    en: "cleared", es: "cerrada", fr: "clos", de: "abgeschlossen", pt: "encerrado", it: "chiuso", ja: "解除済み", zh: "已解除", hi: "बंद", ar: "مغلق",
  },
  "sfy.history.answered": {
    en: "answered by {who}", es: "atendida por {who}", fr: "répondu par {who}", de: "beantwortet von {who}", pt: "atendido por {who}", it: "risposto da {who}", ja: "{who}が対応", zh: "由{who}处理", hi: "{who} ने संभाला", ar: "تولّاه {who}",
  },
  // The reach-out operator — JIM ringing the emergency contacts one after
  // another, and the held-shut 911 line said plainly. The crash-watch trip
  // fires the same cascade; this screen is where a person starts and watches
  // one.
  "ro.title": {
    en: "When JIM reaches out", es: "Cuando JIM llama", fr: "Quand JIM prend contact", de: "Wenn JIM Kontakt aufnimmt", pt: "Quando o JIM contacta", it: "Quando JIM chiama", ja: "JIMが連絡を取るとき", zh: "当 JIM 主动联系时", hi: "जब JIM संपर्क करता है", ar: "عندما يتواصل JIM",
  },
  "ro.pitch": {
    en: "If you collapse and can't answer, JIM rings your trusted contacts one after another. Each can press 1 to hear what's happening, or 2 to never be called this way again. The 911 line is built and held shut.", es: "Si te desplomas y no puedes responder, JIM llama a tus contactos de confianza uno tras otro. Cada uno puede pulsar 1 para escuchar lo que ocurre, o 2 para no volver a recibir esta llamada. La línea de emergencias está construida y sellada.", fr: "Si vous vous effondrez et ne pouvez pas répondre, JIM appelle vos contacts de confiance l'un après l'autre. Chacun peut taper 1 pour entendre ce qui se passe, ou 2 pour ne plus jamais être appelé ainsi. La ligne d'urgence est construite et scellée.", de: "Wenn du zusammenbrichst und nicht antworten kannst, ruft JIM deine Vertrauenspersonen nacheinander an. Jede kann 1 drücken, um zu hören, was los ist, oder 2, um nie wieder so angerufen zu werden. Die Notrufleitung ist gebaut und verschlossen.", pt: "Se desmaiares e não conseguires responder, o JIM liga aos teus contactos de confiança um a um. Cada um pode premir 1 para ouvir o que se passa, ou 2 para nunca mais ser chamado assim. A linha de emergência está construída e selada.", it: "Se crolli e non puoi rispondere, JIM chiama i tuoi contatti fidati uno dopo l'altro. Ognuno può premere 1 per sentire cosa succede, o 2 per non essere più chiamato così. La linea di emergenza è costruita e sigillata.", ja: "あなたが倒れて応答できないとき、JIMは信頼できる連絡先を一人ずつ呼び出します。相手は1を押して状況を聞くか、2を押してこの方法で二度と呼ばれないようにできます。緊急通報の回線は用意され、閉じたままです。", zh: "如果你倒下且无法应答，JIM 会逐一致电你的可信联系人。对方可按 1 听取情况，或按 2 表示不再以此方式联系。急救专线已建好，并保持封闭。", hi: "अगर आप गिर पड़ें और जवाब न दे सकें, तो JIM आपके भरोसेमंद संपर्कों को एक-एक करके कॉल करता है। हर कोई 1 दबाकर स्थिति सुन सकता है, या 2 दबाकर दोबारा इस तरह कॉल न पाने का विकल्प चुन सकता है। आपातकालीन लाइन बनी है और बंद रखी गई है।", ar: "إذا انهرت ولم تستطع الرد، يتصل JIM بجهات اتصالك الموثوقة واحدة تلو الأخرى. يمكن لكل منها الضغط على 1 لسماع ما يجري، أو 2 لعدم الاتصال بها بهذه الطريقة مرة أخرى. خط الطوارئ مبني ومغلق.",
  },
  "ro.posture.held": {
    en: "The emergency line is built and held shut in the code. JIM cannot place a 911 call — that stays sealed until it is reviewed and a phone line is wired.", es: "La línea de emergencias está construida y sellada en el código. JIM no puede hacer una llamada al 911: eso permanece sellado hasta que se revise y se conecte una línea telefónica.", fr: "La ligne d'urgence est construite et scellée dans le code. JIM ne peut pas passer d'appel au 911 — cela reste scellé jusqu'à révision et raccordement d'une ligne téléphonique.", de: "Die Notrufleitung ist gebaut und im Code verschlossen. JIM kann keinen 911-Anruf tätigen — das bleibt versiegelt, bis es geprüft und eine Telefonleitung angeschlossen ist.", pt: "A linha de emergência está construída e selada no código. O JIM não pode fazer uma chamada para o 911 — isso permanece selado até ser revisto e ligada uma linha telefónica.", it: "La linea di emergenza è costruita e sigillata nel codice. JIM non può chiamare il 911 — resta sigillato finché non viene rivisto e collegata una linea telefonica.", ja: "緊急通報の回線は用意され、コード内で閉じられています。JIMは911に発信できません — それは審査され、電話回線が接続されるまで封印されたままです。", zh: "急救专线已建好，并在代码中保持封闭。JIM 无法拨打 911 — 在经过审核并接入电话线路之前，它始终封存。", hi: "आपातकालीन लाइन बनी है और कोड में बंद रखी गई है। JIM 911 पर कॉल नहीं कर सकता — जब तक इसकी समीक्षा न हो और फ़ोन लाइन न जोड़ी जाए, यह सील रहती है।", ar: "خط الطوارئ مبني ومغلق داخل الشيفرة. لا يستطيع JIM إجراء اتصال بالطوارئ — يبقى مختومًا حتى تُراجَع ويُوصَل خط هاتفي.",
  },
  "ro.posture.carry": {
    en: "Calls will be carried online through {provider} once a line is connected.", es: "Las llamadas se harán en línea a través de {provider} cuando se conecte una línea.", fr: "Les appels passeront en ligne via {provider} une fois une ligne raccordée.", de: "Anrufe laufen online über {provider}, sobald eine Leitung angeschlossen ist.", pt: "As chamadas serão feitas online através de {provider} assim que uma linha estiver ligada.", it: "Le chiamate passeranno online tramite {provider} una volta collegata una linea.", ja: "回線が接続されると、通話は{provider}を通じてオンラインで行われます。", zh: "接入线路后，通话将通过 {provider} 在线拨出。", hi: "लाइन जुड़ने पर कॉल {provider} के ज़रिए ऑनलाइन की जाएँगी।", ar: "ستُجرى المكالمات عبر الإنترنت من خلال {provider} بمجرد توصيل خط.",
  },
  "ro.posture.device": {
    en: "Calls will be placed from your own phone once it is connected.", es: "Las llamadas se harán desde tu propio teléfono cuando esté conectado.", fr: "Les appels seront passés depuis votre propre téléphone une fois connecté.", de: "Anrufe werden von deinem eigenen Telefon aus getätigt, sobald es verbunden ist.", pt: "As chamadas serão feitas a partir do teu próprio telefone assim que estiver ligado.", it: "Le chiamate partiranno dal tuo telefono una volta collegato.", ja: "接続されると、通話はあなた自身の電話から発信されます。", zh: "连接后，通话将从你自己的手机拨出。", hi: "जुड़ने पर कॉल आपके अपने फ़ोन से की जाएँगी।", ar: "ستُجرى المكالمات من هاتفك الخاص بمجرد توصيله.",
  },
  "ro.posture.waiting": {
    en: "No phone line is wired yet, so nothing rings — each call is prepared and documented.", es: "Todavía no hay línea telefónica conectada, así que nada suena: cada llamada se prepara y se documenta.", fr: "Aucune ligne téléphonique n'est encore raccordée, donc rien ne sonne — chaque appel est préparé et documenté.", de: "Noch ist keine Telefonleitung angeschlossen, also klingelt nichts — jeder Anruf wird vorbereitet und dokumentiert.", pt: "Ainda não há linha telefónica ligada, por isso nada toca — cada chamada é preparada e documentada.", it: "Nessuna linea telefonica è ancora collegata, quindi non squilla nulla: ogni chiamata viene preparata e documentata.", ja: "電話回線はまだ接続されていないため、何も鳴りません — 各通話は準備され、記録されます。", zh: "尚未接入电话线路，因此不会响铃 — 每通电话都已准备并记录在案。", hi: "अभी कोई फ़ोन लाइन नहीं जुड़ी है, इसलिए कुछ नहीं बजता — हर कॉल तैयार और दर्ज की जाती है।", ar: "لا يوجد خط هاتفي موصول بعد، لذا لا شيء يرن — كل مكالمة تُجهَّز وتُوثَّق.",
  },
  "ro.none": {
    en: "No reach-outs yet.", es: "Aún no hay llamadas.", fr: "Aucun contact pour l'instant.", de: "Noch keine Kontaktversuche.", pt: "Ainda não há contactos.", it: "Ancora nessun contatto.", ja: "まだ連絡はありません。", zh: "暂无联系记录。", hi: "अभी तक कोई संपर्क नहीं।", ar: "لا محاولات تواصل بعد.",
  },
  "ro.lifethreat": {
    en: "life-threatening", es: "riesgo vital", fr: "danger de mort", de: "lebensbedrohlich", pt: "risco de vida", it: "pericolo di vita", ja: "生命の危険", zh: "危及生命", hi: "जानलेवा", ar: "خطر على الحياة",
  },
  // Word-for-word the shells' `sos.what` — the same emergency prompt on the
  // desktop and the phone (test_the_desktop_and_the_phone_say_different_things).
  "ro.start.ph": {
    en: "What's happening? (optional)", es: "¿Qué está pasando? (opcional)", fr: "Que se passe-t-il ? (facultatif)", de: "Was ist los? (optional)", pt: "O que se passa? (opcional)", it: "Cosa sta succedendo? (facoltativo)", ja: "何が起きていますか？（任意）", zh: "发生了什么？（可选）", hi: "क्या हो रहा है? (वैकल्पिक)", ar: "ماذا يجري؟ (اختياري)",
  },
  "ro.start.lifethreat": {
    en: "Life-threatening", es: "Riesgo vital", fr: "Danger de mort", de: "Lebensbedrohlich", pt: "Risco de vida", it: "Pericolo di vita", ja: "生命の危険あり", zh: "危及生命", hi: "जानलेवा", ar: "خطر على الحياة",
  },
  "ro.start.go": {
    en: "Start reach-out", es: "Iniciar llamada", fr: "Lancer le contact", de: "Kontakt starten", pt: "Iniciar contacto", it: "Avvia contatto", ja: "連絡を開始", zh: "开始联系", hi: "संपर्क शुरू करें", ar: "ابدأ التواصل",
  },
  "ro.start.hint": {
    en: "JIM rings your trusted contacts in order — the trusted person first.", es: "JIM llama a tus contactos de confianza en orden: primero la persona de confianza.", fr: "JIM appelle vos contacts de confiance dans l'ordre — la personne de confiance d'abord.", de: "JIM ruft deine Vertrauenspersonen der Reihe nach an — die Vertrauensperson zuerst.", pt: "O JIM liga aos teus contactos de confiança por ordem — a pessoa de confiança primeiro.", it: "JIM chiama i tuoi contatti fidati in ordine — prima la persona di fiducia.", ja: "JIMは信頼できる連絡先を順番に呼び出します — まず信頼できる人から。", zh: "JIM 会按顺序致电你的可信联系人 — 先联系那位可信的人。", hi: "JIM आपके भरोसेमंद संपर्कों को क्रम से कॉल करता है — पहले भरोसेमंद व्यक्ति को।", ar: "يتصل JIM بجهات اتصالك الموثوقة بالترتيب — الشخص الموثوق أولًا.",
  },
  "ro.rs.calling": {
    en: "Ringing the contacts", es: "Llamando a los contactos", fr: "Appel des contacts", de: "Kontakte werden angerufen", pt: "A ligar aos contactos", it: "Sto chiamando i contatti", ja: "連絡先に発信中", zh: "正在致电联系人", hi: "संपर्कों को कॉल किया जा रहा है", ar: "يجري الاتصال بجهات الاتصال",
  },
  "ro.rs.reached": {
    en: "A contact was reached", es: "Se contactó a alguien", fr: "Un contact a été joint", de: "Ein Kontakt wurde erreicht", pt: "Um contacto foi alcançado", it: "Un contatto è stato raggiunto", ja: "連絡先とつながりました", zh: "已联系到一位联系人", hi: "एक संपर्क से बात हुई", ar: "تم الوصول إلى جهة اتصال",
  },
  "ro.rs.exhausted": {
    en: "Contacts exhausted", es: "Contactos agotados", fr: "Contacts épuisés", de: "Kontakte erschöpft", pt: "Contactos esgotados", it: "Contatti esauriti", ja: "連絡先を使い切りました", zh: "联系人已用尽", hi: "सभी संपर्क आज़मा लिए गए", ar: "استُنفدت جهات الاتصال",
  },
  "ro.cs.ringing": {
    en: "Ringing", es: "Llamando", fr: "Sonne", de: "Klingelt", pt: "A tocar", it: "Squilla", ja: "呼び出し中", zh: "正在响铃", hi: "घंटी बज रही है", ar: "يرن",
  },
  "ro.cs.consented": {
    en: "On the line", es: "En línea", fr: "En ligne", de: "In der Leitung", pt: "Em linha", it: "In linea", ja: "通話中", zh: "已接通", hi: "लाइन पर", ar: "على الخط",
  },
  "ro.cs.talking": {
    en: "Talking", es: "Hablando", fr: "En conversation", de: "Im Gespräch", pt: "A falar", it: "In conversazione", ja: "会話中", zh: "通话中", hi: "बातचीत जारी", ar: "يتحدث",
  },
  "ro.cs.reached": {
    en: "Reached", es: "Contactado", fr: "Joint", de: "Erreicht", pt: "Alcançado", it: "Raggiunto", ja: "つながった", zh: "已联系", hi: "संपर्क हुआ", ar: "تم الوصول",
  },
  "ro.cs.unreached": {
    en: "No answer", es: "Sin respuesta", fr: "Sans réponse", de: "Keine Antwort", pt: "Sem resposta", it: "Nessuna risposta", ja: "応答なし", zh: "无人应答", hi: "कोई जवाब नहीं", ar: "لا رد",
  },
  "ro.cs.declined": {
    en: "Asked not to be called", es: "Pidió no ser llamado", fr: "A demandé à ne plus être appelé", de: "Bat, nicht angerufen zu werden", pt: "Pediu para não ser chamado", it: "Ha chiesto di non essere chiamato", ja: "連絡しないよう希望", zh: "要求不要再联系", hi: "कॉल न करने को कहा", ar: "طلب عدم الاتصال به",
  },
  "aim.title": {
    en: "What you're working on", es: "En qué estás trabajando", fr: "Ce sur quoi vous travaillez", de: "Woran du arbeitest", pt: "No que está a trabalhar", it: "A cosa stai lavorando", ja: "取り組んでいること", zh: "你在努力的事", hi: "आप किस पर काम कर रहे हैं", ar: "ما تعمل عليه",
  },
  "aim.sub": {
    en: "goals, habits, and what the month costs", es: "metas, hábitos y lo que cuesta el mes", fr: "objectifs, habitudes, et ce que coûte le mois", de: "Ziele, Gewohnheiten und was der Monat kostet", pt: "metas, hábitos e o que custa o mês", it: "obiettivi, abitudini e quanto costa il mese", ja: "目標、習慣、そして今月の出費", zh: "目标、习惯，以及这个月的花费", hi: "लक्ष्य, आदतें, और महीने का ख़र्च", ar: "أهداف وعادات وكم يكلف الشهر",
  },
  "aim.goals": {
    en: "Goals", es: "Metas", fr: "Objectifs", de: "Ziele", pt: "Metas", it: "Obiettivi", ja: "目標", zh: "目标", hi: "लक्ष्य", ar: "الأهداف",
  },
  "aim.goals.title.ph": {
    en: "Walk thirty minutes", es: "Caminar treinta minutos", fr: "Marcher trente minutes", de: "Dreißig Minuten gehen", pt: "Caminhar trinta minutos", it: "Camminare trenta minuti", ja: "30分歩く", zh: "走三十分钟", hi: "तीस मिनट चलना", ar: "المشي ثلاثين دقيقة",
  },
  "aim.goals.target.ph": {
    en: "daily", es: "a diario", fr: "quotidien", de: "täglich", pt: "diariamente", it: "ogni giorno", ja: "毎日", zh: "每天", hi: "रोज़", ar: "يوميًا",
  },
  "aim.add": {
    en: "Add", es: "Añadir", fr: "Ajouter", de: "Hinzufügen", pt: "Adicionar", it: "Aggiungi", ja: "追加", zh: "添加", hi: "जोड़ें", ar: "أضف",
  },
  "aim.goals.none": {
    en: "Nothing set. A goal here is a thing the coach and the daily suggestion both read — it is not a list for its own sake.", es: "Nada fijado. Una meta aquí es algo que leen tanto el coach como la sugerencia diaria — no es una lista por sí misma.", fr: "Rien de défini. Un objectif ici est une chose que lisent à la fois le coach et la suggestion du jour — ce n'est pas une liste pour la forme.", de: "Nichts gesetzt. Ein Ziel hier ist etwas, das der Coach und der Tagesvorschlag beide lesen — keine Liste um ihrer selbst willen.", pt: "Nada definido. Uma meta aqui é algo que o coach e a sugestão diária leem — não é uma lista por si só.", it: "Niente impostato. Un obiettivo qui è una cosa che leggono sia il coach sia il suggerimento del giorno — non è una lista fine a se stessa.", ja: "未設定です。ここでの目標は、コーチと毎日の提案の両方が読むものです — ただのリストではありません。", zh: "尚未设定。这里的目标是教练和每日建议都会读的东西 — 它不是一份为了列而列的清单。", hi: "कुछ तय नहीं। यहाँ का लक्ष्य वह चीज़ है जिसे कोच और दैनिक सुझाव दोनों पढ़ते हैं — यह अपने आप में कोई सूची नहीं।", ar: "لا شيء محدد. الهدف هنا شيء يقرؤه المدرب والاقتراح اليومي كلاهما — وليس قائمة لذاتها.",
  },
  "aim.goals.done": {
    en: "Mark done", es: "Marcar hecha", fr: "Marquer atteint", de: "Als erledigt markieren", pt: "Marcar como feita", it: "Segna come fatto", ja: "完了にする", zh: "标记完成", hi: "पूर्ण चिह्नित करें", ar: "علّمه منجزًا",
  },
  "aim.habits": {
    en: "Habits", es: "Hábitos", fr: "Habitudes", de: "Gewohnheiten", pt: "Hábitos", it: "Abitudini", ja: "習慣", zh: "习惯", hi: "आदतें", ar: "العادات",
  },
  "aim.habits.ph": {
    en: "Water at eight", es: "Agua a las ocho", fr: "De l'eau à huit heures", de: "Um acht Wasser trinken", pt: "Água às oito", it: "Acqua alle otto", ja: "8時に水を飲む", zh: "八点喝水", hi: "आठ बजे पानी", ar: "ماء عند الثامنة",
  },
  "aim.habits.none": {
    en: "None yet.", es: "Ninguno todavía.", fr: "Aucune pour l'instant.", de: "Noch keine.", pt: "Nenhum ainda.", it: "Ancora nessuna.", ja: "まだありません。", zh: "尚无。", hi: "अभी कोई नहीं।", ar: "لا شيء بعد.",
  },
  "aim.habits.streak": {
    en: "streak {n}", es: "racha {n}", fr: "série {n}", de: "Serie {n}", pt: "sequência {n}", it: "serie {n}", ja: "連続{n}日", zh: "连续{n}次", hi: "लगातार {n}", ar: "تتابع {n}",
  },
  "aim.habits.did": {
    en: "Did it today", es: "Hecho hoy", fr: "Fait aujourd'hui", de: "Heute erledigt", pt: "Feito hoje", it: "Fatto oggi", ja: "今日やった", zh: "今天做了", hi: "आज किया", ar: "فعلتها اليوم",
  },
  "aim.budget": {
    en: "Budget", es: "Presupuesto", fr: "Budget", de: "Budget", pt: "Orçamento", it: "Budget", ja: "予算", zh: "预算", hi: "बजट", ar: "الميزانية",
  },
  "aim.budget.cat.ph": {
    en: "groceries", es: "comida", fr: "courses", de: "Lebensmittel", pt: "mercearia", it: "spesa", ja: "食料品", zh: "杂货", hi: "किराना", ar: "بقالة",
  },
  "aim.budget.set": {
    en: "Set a limit", es: "Poner un límite", fr: "Fixer une limite", de: "Grenze setzen", pt: "Definir um limite", it: "Imposta un limite", ja: "上限を設定", zh: "设定上限", hi: "सीमा तय करें", ar: "حدد سقفًا",
  },
  "aim.budget.none": {
    en: "No limits set. Financial stress is one of the eight conditions JIM will take on, and a budget is how it learns the shape of yours.", es: "Sin límites. El estrés financiero es una de las ocho condiciones que JIM atiende, y un presupuesto es como aprende la forma del tuyo.", fr: "Aucune limite. Le stress financier est l'une des huit situations dont JIM se charge, et un budget est la façon dont il apprend la forme du vôtre.", de: "Keine Grenzen gesetzt. Finanzieller Stress ist einer der acht Zustände, die JIM übernimmt, und ein Budget ist, wie es die Gestalt deines eigenen lernt.", pt: "Sem limites definidos. O stress financeiro é uma das oito condições que o JIM assume, e um orçamento é como aprende a forma do seu.", it: "Nessun limite impostato. Lo stress finanziario è una delle otto condizioni di cui JIM si occupa, e un budget è il modo in cui impara la forma del tuo.", ja: "上限は未設定です。経済的ストレスはJIMが引き受ける八つの状態のひとつで、予算はあなたのそれの形を学ぶ手がかりです。", zh: "尚未设定上限。财务压力是 JIM 会承接的八种状况之一，而预算正是它了解你这方面轮廓的途径。", hi: "कोई सीमा तय नहीं। आर्थिक तनाव उन आठ स्थितियों में से एक है जिन्हें JIM संभालता है, और बजट ही वह तरीक़ा है जिससे वह आपकी स्थिति का आकार समझता है।", ar: "لا حدود محددة. الضغط المالي أحد الحالات الثماني التي يتولاها JIM، والميزانية هي كيف يتعلم شكل حالتك.",
  },
  "aim.budget.line": {
    en: "{spent} of {limit} · {standing}", es: "{spent} de {limit} · {standing}", fr: "{spent} sur {limit} · {standing}", de: "{spent} von {limit} · {standing}", pt: "{spent} de {limit} · {standing}", it: "{spent} su {limit} · {standing}", ja: "{limit}中{spent} · {standing}", zh: "{limit}中已用{spent} · {standing}", hi: "{limit} में से {spent} · {standing}", ar: "{spent} من {limit} · {standing}",
  },
  "aim.budget.remove": {
    en: "Remove", es: "Quitar", fr: "Retirer", de: "Entfernen", pt: "Remover", it: "Rimuovi", ja: "削除", zh: "移除", hi: "हटाएँ", ar: "أزل",
  },
  "aim.activity": {
    en: "Tell it what you did", es: "Dile qué hiciste", fr: "Dites-lui ce que vous avez fait", de: "Sag ihm, was du getan hast", pt: "Diga-lhe o que fez", it: "Digli cosa hai fatto", ja: "何をしたか伝える", zh: "告诉它你做了什么", hi: "बताएँ आपने क्या किया", ar: "أخبره بما فعلت",
  },
  "aim.activity.ph": {
    en: "walk", es: "caminata", fr: "marche", de: "Spaziergang", pt: "caminhada", it: "camminata", ja: "散歩", zh: "散步", hi: "सैर", ar: "مشي",
  },
  "aim.activity.log": {
    en: "Log it", es: "Registrarlo", fr: "L'enregistrer", de: "Erfassen", pt: "Registá-lo", it: "Registralo", ja: "記録する", zh: "记录", hi: "दर्ज करें", ar: "سجّلها",
  },
  "aim.activity.pitch": {
    en: "An ordinary activity is context, not a reading. It tells the Guardian why a heart rate moved before it has to guess.", es: "Una actividad corriente es contexto, no una lectura. Le dice al Guardián por qué se movió una frecuencia cardíaca antes de que tenga que adivinarlo.", fr: "Une activité ordinaire est du contexte, pas une mesure. Elle dit au Gardien pourquoi un rythme cardiaque a bougé, avant qu'il ait à le deviner.", de: "Eine gewöhnliche Aktivität ist Kontext, keine Messung. Sie sagt dem Guardian, warum sich ein Puls bewegt hat, bevor er raten muss.", pt: "Uma atividade comum é contexto, não uma leitura. Diz ao Guardião porque é que uma frequência cardíaca se mexeu, antes de ele ter de adivinhar.", it: "Un'attività ordinaria è contesto, non una lettura. Dice al Guardian perché una frequenza cardiaca si è mossa, prima che debba indovinarlo.", ja: "ふつうの活動は測定値ではなく文脈です。心拍が動いた理由を、ガーディアンが推測する前に伝えてくれます。", zh: "日常活动是上下文，不是读数。它在守护者需要猜测之前，就告诉它心率为何变动。", hi: "सामान्य गतिविधि संदर्भ है, रीडिंग नहीं। यह गार्जियन को बताती है कि हृदय गति क्यों बदली — इससे पहले कि उसे अनुमान लगाना पड़े।", ar: "النشاط العادي سياق لا قراءة. يخبر الحارس لماذا تحرك معدل ضربات القلب قبل أن يضطر إلى التخمين.",
  },
  "cmy.show": {
    en: "Show places", es: "Mostrar lugares", fr: "Afficher les lieux", de: "Orte anzeigen", pt: "Mostrar lugares", it: "Mostra i luoghi", ja: "場所を表示", zh: "显示地点", hi: "जगहें दिखाएँ", ar: "أظهر الأماكن",
  },
  "cmy.looking": {
    en: "Looking…", es: "Buscando…", fr: "Recherche…", de: "Wird gesucht…", pt: "A procurar…", it: "Ricerca…", ja: "検索中…", zh: "查找中…", hi: "खोजा जा रहा है…", ar: "جارٍ البحث…",
  },
  "cmy.title": {
    en: "Community", es: "Comunidad", fr: "Communauté", de: "Gemeinschaft", pt: "Comunidade", it: "Comunità", ja: "コミュニティ", zh: "社区", hi: "समुदाय", ar: "المجتمع",
  },
  "cmy.sub": {
    en: "forums, rooms and local events — in QRME", es: "foros, salas y eventos locales — en QRME", fr: "forums, salles et événements locaux — dans QRME", de: "Foren, Räume und lokale Veranstaltungen — in QRME", pt: "fóruns, salas e eventos locais — no QRME", it: "forum, stanze ed eventi locali — in QRME", ja: "フォーラム、ルーム、地域のイベント — QRMEにて", zh: "论坛、房间与本地活动 — 都在 QRME 里", hi: "फ़ोरम, कमरे और स्थानीय आयोजन — QRME में", ar: "منتديات وغرف وفعاليات محلية — في QRME",
  },
  "cmy.unset": {
    en: "Community lives in QRME. Point this Guardian at your QRME deployment (JIM_QRME_URL) and the doors appear here.", es: "La comunidad vive en QRME. Apunta este Guardián a tu despliegue de QRME (JIM_QRME_URL) y las puertas aparecerán aquí.", fr: "La communauté vit dans QRME. Pointez ce Gardien vers votre déploiement QRME (JIM_QRME_URL) et les portes apparaîtront ici.", de: "Die Gemeinschaft lebt in QRME. Richte diesen Guardian auf dein QRME-Deployment (JIM_QRME_URL), und die Türen erscheinen hier.", pt: "A comunidade vive no QRME. Aponte este Guardião ao seu deployment QRME (JIM_QRME_URL) e as portas aparecem aqui.", it: "La community vive in QRME. Punta questo Guardian al tuo deployment QRME (JIM_QRME_URL) e le porte appariranno qui.", ja: "コミュニティはQRMEにあります。このガーディアンをあなたのQRME配備（JIM_QRME_URL）に向ければ、扉がここに現れます。", zh: "社区在 QRME 里。把这个守护者指向你的 QRME 部署（JIM_QRME_URL），门就会出现在这里。", hi: "समुदाय QRME में रहता है। इस गार्जियन को अपने QRME डिप्लॉयमेंट (JIM_QRME_URL) की ओर इंगित करें, और द्वार यहाँ दिखने लगेंगे।", ar: "المجتمع يعيش في QRME. وجّه هذا الحارس إلى نشر QRME الخاص بك (JIM_QRME_URL) فتظهر الأبواب هنا.",
  },
  "cmy.where": {
    en: "Where this happens", es: "Dónde ocurre esto", fr: "Où cela se passe", de: "Wo das stattfindet", pt: "Onde isto acontece", it: "Dove succede", ja: "これが起きる場所", zh: "这一切发生在哪里", hi: "यह कहाँ होता है", ar: "أين يحدث هذا",
  },
  "cmy.nocopy": {
    en: "Nothing from a room is copied into JIM.", es: "Nada de una sala se copia a JIM.", fr: "Rien d'une salle n'est copié dans JIM.", de: "Nichts aus einem Raum wird nach JIM kopiert.", pt: "Nada de uma sala é copiado para o JIM.", it: "Nulla di una stanza viene copiato in JIM.", ja: "ルームの内容がJIMに複製されることはありません。", zh: "房间里的任何内容都不会复制进 JIM。", hi: "किसी कमरे से कुछ भी JIM में कॉपी नहीं होता।", ar: "لا يُنسخ شيء من غرفة إلى JIM.",
  },
  "cmy.nopost": {
    en: "Nothing is ever posted on your behalf.", es: "Nunca se publica nada en tu nombre.", fr: "Rien n'est jamais publié en votre nom.", de: "Es wird nie etwas in deinem Namen gepostet.", pt: "Nunca é publicado nada em seu nome.", it: "Non viene mai pubblicato nulla a tuo nome.", ja: "あなたの名前で何かが投稿されることは決してありません。", zh: "绝不会以你的名义发布任何内容。", hi: "आपकी ओर से कभी कुछ पोस्ट नहीं किया जाता।", ar: "لا يُنشر شيء نيابة عنك أبدًا.",
  },
  "cmy.nohealth": {
    en: "No health data crosses over.", es: "Ningún dato de salud cruza.", fr: "Aucune donnée de santé ne passe.", de: "Keine Gesundheitsdaten gehen hinüber.", pt: "Nenhum dado de saúde atravessa.", it: "Nessun dato sanitario attraversa.", ja: "健康データが渡ることはありません。", zh: "没有任何健康数据越界。", hi: "कोई स्वास्थ्य डेटा पार नहीं जाता।", ar: "لا تعبر أي بيانات صحية.",
  },
  "cmy.lang": {
    en: "Rooms you can read in:", es: "Salas en las que puedes leer:", fr: "Salles que vous pouvez lire :", de: "Räume, in denen du lesen kannst:", pt: "Salas em que pode ler:", it: "Stanze in cui puoi leggere:", ja: "読めるルームの言語:", zh: "你可以阅读的房间语言:", hi: "जिन कमरों में आप पढ़ सकते हैं:", ar: "الغرف التي يمكنك القراءة بها:",
  },
  "cmy.rooms": {
    en: "Rooms & forums", es: "Salas y foros", fr: "Salles et forums", de: "Räume & Foren", pt: "Salas e fóruns", it: "Stanze e forum", ja: "ルームとフォーラム", zh: "房间与论坛", hi: "कमरे और फ़ोरम", ar: "الغرف والمنتديات",
  },
  "cmy.rooms.none": {
    en: "No rooms open right now. Start one in QRME — Rooms → new topic.", es: "No hay salas abiertas ahora. Abre una en QRME — Salas → nuevo tema.", fr: "Aucune salle ouverte pour l'instant. Ouvrez-en une dans QRME — Salles → nouveau sujet.", de: "Gerade sind keine Räume offen. Eröffne einen in QRME — Räume → neues Thema.", pt: "Não há salas abertas agora. Abra uma no QRME — Salas → novo tema.", it: "Nessuna stanza aperta ora. Aprine una in QRME — Stanze → nuovo argomento.", ja: "現在開いているルームはありません。QRMEで開いてください — ルーム → 新しいトピック。", zh: "目前没有开放的房间。去 QRME 里开一个 — 房间 → 新话题。", hi: "अभी कोई कमरा खुला नहीं। QRME में एक शुरू करें — कमरे → नया विषय।", ar: "لا غرف مفتوحة الآن. افتح واحدة في QRME — الغرف ← موضوع جديد.",
  },
  "cmy.rooms.here": {
    en: "{channel} · {n} here", es: "{channel} · {n} aquí", fr: "{channel} · {n} ici", de: "{channel} · {n} hier", pt: "{channel} · {n} aqui", it: "{channel} · {n} qui", ja: "{channel} · {n}人", zh: "{channel} · {n}人在此", hi: "{channel} · {n} यहाँ", ar: "{channel} · {n} هنا",
  },
  "cmy.rooms.open": {
    en: "Open in QRME", es: "Abrir en QRME", fr: "Ouvrir dans QRME", de: "In QRME öffnen", pt: "Abrir no QRME", it: "Apri in QRME", ja: "QRMEで開く", zh: "在 QRME 中打开", hi: "QRME में खोलें", ar: "افتح في QRME",
  },
  "cmy.events": {
    en: "Local events", es: "Eventos locales", fr: "Événements locaux", de: "Lokale Veranstaltungen", pt: "Eventos locais", it: "Eventi locali", ja: "地域のイベント", zh: "本地活动", hi: "स्थानीय आयोजन", ar: "فعاليات محلية",
  },
  "cmy.events.filter": {
    en: "Filter by place", es: "Filtrar por lugar", fr: "Filtrer par lieu", de: "Nach Ort filtern", pt: "Filtrar por lugar", it: "Filtra per luogo", ja: "場所で絞り込む", zh: "按地点筛选", hi: "स्थान से छाँटें", ar: "تصفية حسب المكان",
  },
  "cmy.events.ph": {
    en: "e.g. Bend", es: "p. ej. Bend", fr: "p. ex. Bend", de: "z. B. Bend", pt: "p. ex. Bend", it: "es. Bend", ja: "例: Bend", zh: "例如 Bend", hi: "जैसे Bend", ar: "مثل Bend",
  },
  "cmy.events.listed": {
    en: "({n} listed)", es: "({n} en lista)", fr: "({n} annoncés)", de: "({n} gelistet)", pt: "({n} listados)", it: "({n} in elenco)", ja: "（{n}件掲載）", zh: "（已列{n}项）", hi: "({n} सूचीबद्ध)", ar: "({n} مدرجة)",
  },
  "cmy.events.none": {
    en: "Nothing claimed for that place yet.", es: "Nada reclamado para ese lugar todavía.", fr: "Rien de signalé pour ce lieu pour l'instant.", de: "Für diesen Ort ist noch nichts eingetragen.", pt: "Nada reclamado para esse lugar ainda.", it: "Ancora nulla per quel luogo.", ja: "その場所についてはまだ何もありません。", zh: "该地点尚无任何登记。", hi: "उस स्थान के लिए अभी कुछ नहीं।", ar: "لا شيء مُدرج لذلك المكان بعد.",
  },
  "mon.send": {
    en: "Send to Guardian", es: "Enviar al Guardián", fr: "Envoyer au Gardien", de: "An den Guardian senden", pt: "Enviar ao Guardião", it: "Invia al Guardian", ja: "ガーディアンに送る", zh: "发送给守护者", hi: "गार्जियन को भेजें", ar: "أرسل إلى الحارس",
  },
  "mon.analyzing": {
    en: "Analyzing…", es: "Analizando…", fr: "Analyse…", de: "Wird analysiert…", pt: "A analisar…", it: "Analisi…", ja: "解析中…", zh: "分析中…", hi: "विश्लेषण हो रहा है…", ar: "جارٍ التحليل…",
  },
  "mon.firstaid": {
    en: "First aid, step by step", es: "Primeros auxilios, paso a paso", fr: "Premiers secours, étape par étape", de: "Erste Hilfe, Schritt für Schritt", pt: "Primeiros socorros, passo a passo", it: "Primo soccorso, passo per passo", ja: "応急手当、手順ごとに", zh: "急救，一步一步来", hi: "प्राथमिक उपचार, कदम दर कदम", ar: "الإسعافات الأولية، خطوة بخطوة",
  },
  "mon.title": {
    en: "Live Monitoring", es: "Vigilancia en directo", fr: "Surveillance en direct", de: "Live-Überwachung", pt: "Vigilância em direto", it: "Monitoraggio dal vivo", ja: "ライブ・モニタリング", zh: "实时监测", hi: "लाइव निगरानी", ar: "المراقبة الحيّة",
  },
  // The staleness contract's card (jim/freshness.py): which silence this
  // is, and the number "real-time" answers with.
  "mon.fresh.title": {
    en: "How fresh the readings are", es: "Qué tan recientes son las lecturas", fr: "Fraîcheur des mesures", de: "Wie frisch die Messwerte sind", pt: "Quão recentes são as leituras", it: "Quanto sono fresche le letture", ja: "読み取りの新しさ", zh: "读数有多新", hi: "रीडिंग कितनी ताज़ा हैं", ar: "مدى حداثة القراءات",
  },
  "mon.fresh.alive": {
    en: "Readings are current.", es: "Las lecturas están al día.", fr: "Les mesures sont à jour.", de: "Die Messwerte sind aktuell.", pt: "As leituras estão em dia.", it: "Le letture sono aggiornate.", ja: "読み取りは最新です。", zh: "读数是最新的。", hi: "रीडिंग ताज़ा हैं।", ar: "القراءات حديثة.",
  },
  "mon.fresh.person-quiet": {
    en: "The channel is alive but no readings — the watch may be off the wrist.", es: "El canal está activo pero sin lecturas: el reloj puede no estar en la muñeca.", fr: "Le canal est actif mais sans mesures — la montre n'est peut-être pas au poignet.", de: "Der Kanal lebt, aber keine Messwerte — die Uhr ist womöglich nicht am Handgelenk.", pt: "O canal está ativo mas sem leituras — o relógio pode não estar no pulso.", it: "Il canale è attivo ma senza letture — l'orologio potrebbe non essere al polso.", ja: "チャンネルは生きていますが読み取りがありません — 時計が手首にないかもしれません。", zh: "通道正常但没有读数——手表可能不在手腕上。", hi: "चैनल चालू है पर रीडिंग नहीं — घड़ी शायद कलाई पर नहीं है।", ar: "القناة تعمل لكن لا قراءات — قد تكون الساعة ليست على المعصم.",
  },
  "mon.fresh.phone-between": {
    en: "The phone sits between the wrist and the wire — its relay has gone quiet.", es: "El teléfono está entre la muñeca y la red: su relé se ha callado.", fr: "Le téléphone est entre le poignet et le réseau — son relais s'est tu.", de: "Das Telefon sitzt zwischen Handgelenk und Netz — sein Relais ist verstummt.", pt: "O telefone está entre o pulso e a rede — o seu relé silenciou.", it: "Il telefono sta tra il polso e la rete — il suo relè tace.", ja: "電話が手首と回線の間にあり、その中継が止まっています。", zh: "手机在手腕与网络之间——它的中继安静了。", hi: "फ़ोन कलाई और नेटवर्क के बीच है — उसका रिले चुप हो गया है।", ar: "الهاتف بين المعصم والشبكة — توقّف وسيطه عن الإرسال.",
  },
  "mon.fresh.network-dark": {
    en: "The network is dark — no channel pulse and no readings.", es: "La red está a oscuras: sin pulso del canal ni lecturas.", fr: "Le réseau est muet — ni pouls du canal ni mesures.", de: "Das Netz ist dunkel — kein Kanalpuls und keine Messwerte.", pt: "A rede está às escuras — sem pulso do canal nem leituras.", it: "La rete è muta — nessun battito del canale e nessuna lettura.", ja: "ネットワークが沈黙しています — チャンネルの鼓動も読み取りもありません。", zh: "网络无响应——没有通道脉冲也没有读数。", hi: "नेटवर्क अंधेरे में है — न चैनल की धड़कन, न रीडिंग।", ar: "الشبكة صامتة — لا نبض للقناة ولا قراءات.",
  },
  "mon.fresh.age": {
    en: "last reading {s}s old", es: "última lectura hace {s}s", fr: "dernière mesure il y a {s}s", de: "letzter Messwert {s}s alt", pt: "última leitura há {s}s", it: "ultima lettura {s}s fa", ja: "最新の読み取りは{s}秒前", zh: "最近读数 {s} 秒前", hi: "आख़िरी रीडिंग {s} सेकंड पुरानी", ar: "آخر قراءة قبل {s} ثانية",
  },
  "mon.fresh.p95": {
    en: "p95 age at decision: {s}s — measured, not designed", es: "edad p95 al decidir: {s}s — medida, no diseñada", fr: "âge p95 à la décision : {s}s — mesuré, pas conçu", de: "p95-Alter bei der Entscheidung: {s}s — gemessen, nicht entworfen", pt: "idade p95 na decisão: {s}s — medida, não desenhada", it: "età p95 alla decisione: {s}s — misurata, non progettata", ja: "判断時のp95経過時間: {s}秒 — 設計値ではなく実測値", zh: "决策时的 p95 年龄：{s} 秒——实测，而非设计", hi: "निर्णय के समय p95 आयु: {s} सेकंड — मापी गई, तय नहीं", ar: "عمر p95 عند القرار: {s} ثانية — مقاس لا مُصمَّم",
  },
  "mon.sub": {
    en: "detect → guide → escalate", es: "detectar → guiar → escalar", fr: "détecter → guider → escalader", de: "erkennen → anleiten → eskalieren", pt: "detetar → orientar → escalar", it: "rileva → guida → escala", ja: "検知 → 案内 → エスカレート", zh: "检测 → 指导 → 升级", hi: "पहचान → मार्गदर्शन → वृद्धि", ar: "اكتشاف ← إرشاد ← تصعيد",
  },
  "mon.submit": {
    en: "Submit a biometric sample", es: "Enviar una muestra biométrica", fr: "Envoyer un échantillon biométrique", de: "Eine biometrische Probe senden", pt: "Enviar uma amostra biométrica", it: "Invia un campione biometrico", ja: "生体サンプルを送信", zh: "提交一份生物特征样本", hi: "एक बायोमेट्रिक नमूना भेजें", ar: "أرسل عينة حيوية",
  },
  "mon.hr": {
    en: "Heart rate (bpm)", es: "Frecuencia cardíaca (lpm)", fr: "Fréquence cardiaque (bpm)", de: "Herzfrequenz (bpm)", pt: "Frequência cardíaca (bpm)", it: "Frequenza cardiaca (bpm)", ja: "心拍数（bpm）", zh: "心率（次/分）", hi: "हृदय गति (bpm)", ar: "نبض القلب (نبضة/د)",
  },
  "mon.resp": {
    en: "Respiration (/min)", es: "Respiración (/min)", fr: "Respiration (/min)", de: "Atmung (/min)", pt: "Respiração (/min)", it: "Respirazione (/min)", ja: "呼吸（回/分）", zh: "呼吸（次/分）", hi: "श्वसन (/मिनट)", ar: "التنفس (/دقيقة)",
  },
  "mon.stress": {
    en: "Stress (0–1)", es: "Estrés (0–1)", fr: "Stress (0–1)", de: "Stress (0–1)", pt: "Stress (0–1)", it: "Stress (0–1)", ja: "ストレス（0–1）", zh: "压力（0–1）", hi: "तनाव (0–1)", ar: "التوتر (0–1)",
  },
  "mon.calm": {
    en: "all calm", es: "todo en calma", fr: "tout est calme", de: "alles ruhig", pt: "tudo calmo", it: "tutto calmo", ja: "すべて平穏", zh: "一切平静", hi: "सब शांत", ar: "كل شيء هادئ",
  },
  "mon.taptohear": {
    en: "tap to hear it — the browser held the audio until you touch the screen", es: "toca para oírlo: el navegador retuvo el audio hasta que toques la pantalla", fr: "touchez pour l'entendre — le navigateur retient l'audio jusqu'à votre geste", de: "tippen, um es zu hören — der Browser hält den Ton zurück, bis du den Bildschirm berührst", pt: "toque para ouvir — o navegador reteve o áudio até você tocar no ecrã", it: "tocca per sentirlo — il browser trattiene l'audio finché non tocchi lo schermo", ja: "タップして聞いてください — 画面に触れるまでブラウザが音声を保留しています", zh: "点按即可收听——在你触摸屏幕前，浏览器暂不播放音频", hi: "सुनने के लिए टैप करें — स्क्रीन छूने तक ब्राउज़र ने ऑडियो रोक रखा है", ar: "انقر لسماعه — يحجب المتصفح الصوت حتى تلمس الشاشة",
  },
  "mon.drift": {
    en: "drift from your baseline — a check-in, not an alarm", es: "desviación de tu línea base — una consulta, no una alarma", fr: "écart par rapport à votre ligne de base — une prise de nouvelles, pas une alarme", de: "Abweichung von deiner Basislinie — eine Nachfrage, kein Alarm", pt: "desvio da sua linha de base — uma verificação, não um alarme", it: "scostamento dalla tua linea di base — un controllo, non un allarme", ja: "ベースラインからのずれ — 警報ではなく、様子うかがいです", zh: "偏离你的基线 — 这是问候，不是警报", hi: "आपकी आधार रेखा से विचलन — यह हालचाल है, अलार्म नहीं", ar: "انحراف عن خطك الأساسي — اطمئنان لا إنذار",
  },
  "mon.reading": {
    en: "{label}: {value}{unit} — {direction} your usual {baseline}{unit} (edge {edge}{unit})", es: "{label}: {value}{unit} — {direction} tu habitual {baseline}{unit} (borde {edge}{unit})", fr: "{label} : {value}{unit} — {direction} votre habituel {baseline}{unit} (limite {edge}{unit})", de: "{label}: {value}{unit} — {direction} deinem üblichen {baseline}{unit} (Rand {edge}{unit})", pt: "{label}: {value}{unit} — {direction} o seu habitual {baseline}{unit} (limite {edge}{unit})", it: "{label}: {value}{unit} — {direction} il tuo solito {baseline}{unit} (bordo {edge}{unit})", ja: "{label}: {value}{unit} — 普段の{baseline}{unit}より{direction}（境界 {edge}{unit}）", zh: "{label}: {value}{unit} — {direction}你平常的{baseline}{unit}（边界 {edge}{unit}）", hi: "{label}: {value}{unit} — आपके सामान्य {baseline}{unit} से {direction} (सीमा {edge}{unit})", ar: "{label}: {value}{unit} — {direction} معتادك {baseline}{unit} (الحد {edge}{unit})",
  },
  "mon.guidance": {
    en: "{source} guidance", es: "orientación de {source}", fr: "conseils de {source}", de: "{source}-Anleitung", pt: "orientação de {source}", it: "guida di {source}", ja: "{source}によるガイダンス", zh: "{source}指导", hi: "{source} मार्गदर्शन", ar: "إرشاد {source}",
  },
  "mon.helped": {
    en: "Yes, that helped", es: "Sí, eso ayudó", fr: "Oui, ça a aidé", de: "Ja, das half", pt: "Sim, isso ajudou", it: "Sì, ha aiutato", ja: "はい、役に立ちました", zh: "是的，有用", hi: "हाँ, इससे मदद मिली", ar: "نعم، أفاد",
  },
  "mon.nothelped": {
    en: "No, it didn't", es: "No, no ayudó", fr: "Non, pas vraiment", de: "Nein, hat es nicht", pt: "Não, não ajudou", it: "No, non ha aiutato", ja: "いいえ、役に立ちませんでした", zh: "没有用", hi: "नहीं, नहीं मिली", ar: "لا، لم يفد",
  },
  "mon.noted": {
    en: "Noted — monitoring resumes, and the Guardian remembers that this worked for you.", es: "Anotado — la monitorización se reanuda, y el Guardián recuerda que esto te funcionó.", fr: "Noté — la surveillance reprend, et le Gardien retient que cela a marché pour vous.", de: "Notiert — die Überwachung läuft weiter, und der Guardian merkt sich, dass das bei dir wirkte.", pt: "Anotado — a monitorização retoma, e o Guardião lembra-se de que isto resultou consigo.", it: "Annotato — il monitoraggio riprende, e il Guardian ricorda che con te ha funzionato.", ja: "記録しました — 監視を再開します。ガーディアンは、これがあなたに効いたことを覚えています。", zh: "已记下 — 监测继续，守护者也记住了这个方法对你有效。", hi: "दर्ज किया — निगरानी फिर शुरू, और गार्जियन याद रखता है कि यह आपके लिए काम आया।", ar: "سُجّل — تستأنف المراقبة، ويتذكر الحارس أن هذا نفعك.",
  },
  "mon.reaching": {
    en: "Reaching a person", es: "Contactando a una persona", fr: "Joindre une personne", de: "Einen Menschen erreichen", pt: "A contactar uma pessoa", it: "Raggiungere una persona", ja: "人へ連絡中", zh: "正在联系一个人", hi: "किसी व्यक्ति तक पहुँचना", ar: "الوصول إلى شخص",
  },
  "mon.escalated": {
    en: "escalated to {tier}", es: "escalado a {tier}", fr: "escaladé vers {tier}", de: "eskaliert zu {tier}", pt: "escalado para {tier}", it: "escalato a {tier}", ja: "{tier}へエスカレート", zh: "已升级至{tier}", hi: "{tier} तक बढ़ाया गया", ar: "صُعّد إلى {tier}",
  },
  "mon.companion": {
    en: "companion, in the background", es: "acompañante, en segundo plano", fr: "compagnon, en arrière-plan", de: "Begleiter, im Hintergrund", pt: "companheiro, em segundo plano", it: "compagno, in sottofondo", ja: "伴走者として、背後で", zh: "同伴，在后台", hi: "साथी, पृष्ठभूमि में", ar: "رفيق، في الخلفية",
  },
  "mon.relaying": {
    en: "Relaying a dispatcher briefing — who you are, your known conditions and critical medications, the latest readings, and what's being done — through every configured channel, updated with each new reading.", es: "Retransmitiendo un parte para el operador — quién eres, tus condiciones conocidas y medicamentos críticos, las últimas lecturas, y qué se está haciendo — por cada canal configurado, actualizado con cada nueva lectura.", fr: "Transmission d'un briefing au régulateur — qui vous êtes, vos affections connues et médicaments critiques, les dernières mesures, et ce qui est fait — par chaque canal configuré, mis à jour à chaque nouvelle mesure.", de: "Weitergabe eines Leitstellen-Briefings — wer du bist, deine bekannten Beschwerden und kritischen Medikamente, die letzten Messungen und was getan wird — über jeden konfigurierten Kanal, mit jeder neuen Messung aktualisiert.", pt: "A retransmitir um resumo para o operador — quem é, as suas condições conhecidas e medicamentos críticos, as últimas leituras, e o que está a ser feito — por cada canal configurado, atualizado a cada nova leitura.", it: "Ritrasmissione di un briefing per l'operatore — chi sei, le tue condizioni note e i farmaci critici, le ultime letture, e cosa si sta facendo — su ogni canale configurato, aggiornato a ogni nuova lettura.", ja: "指令員向けの申し送りを中継しています — あなたが誰か、既知の状態と重要な薬、最新の測定値、そして今行われていること — 設定済みのすべてのチャネルへ、新しい測定のたびに更新して。", zh: "正在转达给调度员的简报 — 你是谁、你已知的状况与关键用药、最新读数，以及正在采取的措施 — 通过每一个已配置的通道，并随每条新读数更新。", hi: "डिस्पैचर के लिए ब्रीफ़िंग पहुँचाई जा रही है — आप कौन हैं, आपकी ज्ञात स्थितियाँ और महत्वपूर्ण दवाएँ, नवीनतम रीडिंग, और क्या किया जा रहा है — हर कॉन्फ़िगर किए चैनल से, हर नई रीडिंग के साथ अद्यतन।", ar: "يُنقل إيجاز للمرسِل — من أنت، وحالاتك المعروفة وأدويتك الحرجة، وآخر القراءات، وما يجري فعله — عبر كل قناة مهيأة، ويُحدَّث مع كل قراءة جديدة.",
  },
  "hom.title": {
    en: "Overview", es: "Resumen", fr: "Aperçu", de: "Übersicht", pt: "Visão geral", it: "Panoramica", ja: "概要", zh: "概览", hi: "अवलोकन", ar: "نظرة عامة",
  },
  "hom.on": {
    en: "● Guardian on", es: "● Guardián activo", fr: "● Gardien actif", de: "● Guardian an", pt: "● Guardião ativo", it: "● Guardian attivo", ja: "● ガーディアン稼働中", zh: "● 守护者已启用", hi: "● गार्जियन चालू", ar: "● الحارس يعمل",
  },
  "hom.hi": {
    en: "Hi, {name}", es: "Hola, {name}", fr: "Bonjour, {name}", de: "Hallo, {name}", pt: "Olá, {name}", it: "Ciao, {name}", ja: "こんにちは、{name} さん", zh: "你好，{name}", hi: "नमस्ते, {name}", ar: "مرحبًا، {name}",
  },
  "hom.watching": {
    en: "Your Guardian is watching — rules are transparent.", es: "Tu Guardián está atento — las reglas son transparentes.", fr: "Votre Gardien veille — les règles sont transparentes.", de: "Dein Guardian wacht — die Regeln sind transparent.", pt: "O seu Guardião está atento — as regras são transparentes.", it: "Il tuo Guardian veglia — le regole sono trasparenti.", ja: "ガーディアンが見守っています — ルールは公開されています。", zh: "你的守护者正在看顾 — 规则是透明的。", hi: "आपका गार्जियन देख रहा है — नियम पारदर्शी हैं।", ar: "حارسك يراقب — والقواعد شفافة.",
  },
  "hom.baseline": {
    en: "Learned baseline", es: "Línea base aprendida", fr: "Référence apprise", de: "Gelernte Ausgangslage", pt: "Linha de base aprendida", it: "Base di riferimento appresa", ja: "学習したベースライン", zh: "已学习的基线", hi: "सीखी गई आधार-रेखा", ar: "خط الأساس المكتسب",
  },
  "hom.baseline.none": {
    en: "No baseline yet — it builds from calm samples in Live Monitoring.", es: "Aún no hay línea base — se construye con muestras en calma desde la Monitorización en vivo.", fr: "Pas encore de ligne de base — elle se construit à partir d'échantillons calmes dans la Surveillance en direct.", de: "Noch keine Basislinie — sie entsteht aus ruhigen Proben in der Live-Überwachung.", pt: "Ainda não há linha de base — constrói-se a partir de amostras calmas na Monitorização ao vivo.", it: "Ancora nessuna linea di base — si costruisce da campioni calmi nel Monitoraggio dal vivo.", ja: "ベースラインはまだありません — ライブモニタリングの安静時サンプルから作られます。", zh: "尚无基线 — 它由实时监测中的平静样本积累而成。", hi: "अभी कोई आधार रेखा नहीं — यह लाइव निगरानी के शांत नमूनों से बनती है।", ar: "لا خط أساسي بعد — يُبنى من عينات هادئة في المراقبة الحية.",
  },
  "hom.th.metric": {
    en: "metric", es: "métrica", fr: "métrique", de: "Metrik", pt: "métrica", it: "metrica", ja: "指標", zh: "指标", hi: "मीट्रिक", ar: "المقياس",
  },
  "hom.th.value": {
    en: "value", es: "valor", fr: "valeur", de: "Wert", pt: "valor", it: "valore", ja: "値", zh: "数值", hi: "मान", ar: "القيمة",
  },
  "hom.th.state": {
    en: "state", es: "estado", fr: "état", de: "Zustand", pt: "estado", it: "stato", ja: "状態", zh: "状态", hi: "स्थिति", ar: "الحالة",
  },
  "hom.th.samples": {
    en: "samples", es: "muestras", fr: "échantillons", de: "Proben", pt: "amostras", it: "campioni", ja: "サンプル数", zh: "样本数", hi: "नमूने", ar: "العينات",
  },
  "hom.go.monitor": {
    en: "Live Monitoring", es: "Vigilancia en directo", fr: "Surveillance en direct", de: "Live-Überwachung", pt: "Vigilância em direto", it: "Monitoraggio dal vivo", ja: "ライブ・モニタリング", zh: "实时监测", hi: "लाइव निगरानी", ar: "المراقبة الحيّة",
  },
  "hom.go.coach": {
    en: "Coach", es: "Coach", fr: "Coach", de: "Coach", pt: "Coach", it: "Coach", ja: "コーチ", zh: "教练", hi: "कोच", ar: "مدرب",
  },
  "hom.go.checkin": {
    en: "Check-in", es: "Registro", fr: "Bilan", de: "Check-in", pt: "Check-in", it: "Check-in", ja: "チェックイン", zh: "签到", hi: "चेक-इन", ar: "تسجيل الحالة",
  },
  "hom.go.meds": {
    en: "💊 Medications", es: "💊 Medicamentos", fr: "💊 Médicaments", de: "💊 Medikamente", pt: "💊 Medicamentos", it: "💊 Farmaci", ja: "💊 薬", zh: "💊 药物", hi: "💊 दवाइयाँ", ar: "💊 الأدوية",
  },
  "hom.go.careteam": {
    en: "👥 Care Team", es: "👥 Equipo de cuidados", fr: "👥 Équipe de soins", de: "👥 Betreuungsteam", pt: "👥 Equipa de cuidados", it: "👥 Squadra di cura", ja: "👥 ケアチーム", zh: "👥 照护团队", hi: "👥 देखभाल टीम", ar: "👥 فريق الرعاية",
  },
  "chk.save": {
    en: "Save check-in", es: "Guardar el registro", fr: "Enregistrer le point", de: "Check-in speichern", pt: "Guardar o registo", it: "Salva il check-in", ja: "チェックインを保存", zh: "保存签到", hi: "चेक-इन सहेजें", ar: "احفظ التسجيل",
  },
  "chk.title": {
    en: "Check-in", es: "Registro", fr: "Bilan", de: "Check-in", pt: "Check-in", it: "Check-in", ja: "チェックイン", zh: "签到", hi: "चेक-इन", ar: "تسجيل الحالة",
  },
  "chk.sub": {
    en: "mood, energy & stress · a worrying note runs the crisis check", es: "ánimo, energía y estrés · una nota preocupante dispara la comprobación de crisis", fr: "humeur, énergie et stress · une note inquiétante déclenche le contrôle de crise", de: "Stimmung, Energie & Stress · eine besorgniserregende Notiz löst die Krisenprüfung aus", pt: "humor, energia e stress · uma nota preocupante corre a verificação de crise", it: "umore, energia e stress · una nota preoccupante avvia il controllo di crisi", ja: "気分・活力・ストレス · 気がかりなメモは危機チェックを走らせます", zh: "心情、精力与压力 · 令人担忧的备注会触发危机检查", hi: "मनोदशा, ऊर्जा और तनाव · चिंताजनक टिप्पणी संकट-जाँच चलाती है", ar: "المزاج والطاقة والتوتر · ملاحظة مقلقة تُشغّل فحص الأزمة",
  },
  "chk.mood": {
    en: "Mood:", es: "Ánimo:", fr: "Humeur :", de: "Stimmung:", pt: "Humor:", it: "Umore:", ja: "気分:", zh: "心情:", hi: "मनोदशा:", ar: "المزاج:",
  },
  "chk.energy": {
    en: "Energy:", es: "Energía:", fr: "Énergie :", de: "Energie:", pt: "Energia:", it: "Energia:", ja: "活力:", zh: "精力:", hi: "ऊर्जा:", ar: "الطاقة:",
  },
  "chk.stress": {
    en: "Stress:", es: "Estrés:", fr: "Stress :", de: "Stress:", pt: "Stress:", it: "Stress:", ja: "ストレス:", zh: "压力:", hi: "तनाव:", ar: "التوتر:",
  },
  "chk.note": {
    en: "Note (optional)", es: "Nota (opcional)", fr: "Note (facultatif)", de: "Notiz (optional)", pt: "Nota (opcional)", it: "Nota (facoltativo)", ja: "メモ（任意）", zh: "备注（可选）", hi: "टिप्पणी (वैकल्पिक)", ar: "ملاحظة (اختياري)",
  },
  "chk.logged": {
    en: "Logged", es: "Registrado", fr: "Enregistré", de: "Erfasst", pt: "Registado", it: "Registrato", ja: "記録しました", zh: "已记录", hi: "दर्ज", ar: "سُجّل",
  },
  "chk.result": {
    en: "mood {mood} · energy {energy} · stress {stress}", es: "ánimo {mood} · energía {energy} · estrés {stress}", fr: "humeur {mood} · énergie {energy} · stress {stress}", de: "Stimmung {mood} · Energie {energy} · Stress {stress}", pt: "humor {mood} · energia {energy} · stress {stress}", it: "umore {mood} · energia {energy} · stress {stress}", ja: "気分{mood} · 活力{energy} · ストレス{stress}", zh: "心情{mood} · 精力{energy} · 压力{stress}", hi: "मनोदशा {mood} · ऊर्जा {energy} · तनाव {stress}", ar: "المزاج {mood} · الطاقة {energy} · التوتر {stress}",
  },
  "chk.guardian": {
    en: "guardian", es: "guardián", fr: "gardien", de: "Guardian", pt: "guardião", it: "guardian", ja: "ガーディアン", zh: "守护者", hi: "गार्जियन", ar: "الحارس",
  },
  "chk.flagged": {
    en: "flagged", es: "marcado", fr: "signalé", de: "markiert", pt: "assinalado", it: "segnalato", ja: "要注意", zh: "已标记", hi: "चिह्नित", ar: "مُعلَّم",
  },
  "chk.noconcern": {
    en: "No concern detected — logged to your day.", es: "Sin motivo de preocupación — registrado en tu día.", fr: "Rien d'inquiétant — enregistré dans votre journée.", de: "Nichts Besorgniserregendes — in deinen Tag eingetragen.", pt: "Sem motivo de preocupação — registado no seu dia.", it: "Nessuna preoccupazione — registrato nella tua giornata.", ja: "気がかりな点はありません — その日の記録に加えました。", zh: "未发现值得担忧之处 — 已记入你的一天。", hi: "कोई चिंता की बात नहीं — आपके दिन में दर्ज।", ar: "لا ما يقلق — سُجّل في يومك.",
  },
  "mea.title": {
    en: "Meals", es: "Comidas", fr: "Repas", de: "Mahlzeiten", pt: "Refeições", it: "Pasti", ja: "食事", zh: "餐食", hi: "भोजन", ar: "الوجبات",
  },
  "mea.ph": {
    en: "What was on the plate? A few words is enough", es: "¿Qué había en el plato? Bastan unas palabras", fr: "Qu'y avait-il dans l'assiette ? Quelques mots suffisent", de: "Was war auf dem Teller? Ein paar Worte genügen", pt: "O que estava no prato? Bastam algumas palavras", it: "Cosa c'era nel piatto? Bastano poche parole", ja: "お皿には何が？ひと言で十分です", zh: "盘子里有什么？几个字就够", hi: "थाली में क्या था? कुछ शब्द काफ़ी हैं", ar: "ماذا كان في الطبق؟ كلمات قليلة تكفي",
  },
  "mea.log": {
    en: "Log the meal", es: "Registrar la comida", fr: "Consigner le repas", de: "Mahlzeit erfassen", pt: "Registar a refeição", it: "Registra il pasto", ja: "食事を記録", zh: "记录餐食", hi: "भोजन दर्ज करें", ar: "سجّل الوجبة",
  },
  "mea.receipt": {
    en: "The photo is the receipt — sealed like a clinical capture, never read by anything automatic. The note is the log; when an online model is standing it tidies the note, and it never invents what the note doesn't say.", es: "La foto es el recibo — sellada como una captura clínica, nunca leída por nada automático. La nota es el registro; si hay un modelo en línea la ordena, y nunca inventa lo que la nota no dice.", fr: "La photo est le reçu — scellée comme une capture clinique, jamais lue par un automatisme. La note est le journal ; quand un modèle en ligne est là, il la met au propre, sans jamais inventer ce qu'elle ne dit pas.", de: "Das Foto ist der Beleg — versiegelt wie eine klinische Aufnahme, nie von etwas Automatischem gelesen. Die Notiz ist das Protokoll; steht ein Online-Modell bereit, ordnet es die Notiz, und es erfindet nie, was sie nicht sagt.", pt: "A foto é o recibo — selada como uma captura clínica, nunca lida por nada automático. A nota é o registo; quando há um modelo online, ele arruma a nota e nunca inventa o que ela não diz.", it: "La foto è la ricevuta — sigillata come una cattura clinica, mai letta da nulla di automatico. La nota è il registro; quando c'è un modello online la riordina, e non inventa mai ciò che la nota non dice.", ja: "写真はレシートです — 臨床キャプチャと同じく封印され、自動処理には読まれません。メモが記録です。オンラインモデルがあればメモを整えますが、メモにないことは決して作りません。", zh: "照片就是凭证 — 像临床拍摄一样封存，任何自动流程都不会读取。备注才是记录；在线模型可把备注整理成清单，但绝不编造备注没说的内容。", hi: "फ़ोटो रसीद है — क्लिनिकल कैप्चर की तरह सील, कोई स्वचालित चीज़ उसे नहीं पढ़ती। नोट ही लॉग है; ऑनलाइन मॉडल हो तो वह नोट को व्यवस्थित करता है, और जो नोट में नहीं है वह कभी नहीं गढ़ता।", ar: "الصورة هي الإيصال — مختومة كأي التقاط سريري، لا يقرؤها شيء آلي أبدًا. والملاحظة هي السجل؛ وإن وُجد نموذج متصل رتّبها، ولا يخترع أبدًا ما لم تقله الملاحظة.",
  },
  "mea.none": {
    en: "No meals logged yet.", es: "Aún no hay comidas registradas.", fr: "Aucun repas consigné pour l'instant.", de: "Noch keine Mahlzeiten erfasst.", pt: "Ainda não há refeições registadas.", it: "Nessun pasto registrato finora.", ja: "まだ食事の記録はありません。", zh: "还没有记录任何餐食。", hi: "अभी तक कोई भोजन दर्ज नहीं।", ar: "لا وجبات مسجلة بعد.",
  },
  "mea.sealed": {
    en: "photo sealed", es: "foto sellada", fr: "photo scellée", de: "Foto versiegelt", pt: "foto selada", it: "foto sigillata", ja: "写真は封印済み", zh: "照片已封存", hi: "फ़ोटो सील", ar: "الصورة مختومة",
  },
  "drl.title": {
    en: "Interview drill", es: "Simulacro de entrevista", fr: "Exercice d'entretien", de: "Interview-Übung", pt: "Treino de entrevista", it: "Simulazione di colloquio", ja: "面接ドリル", zh: "面试演练", hi: "साक्षात्कार अभ्यास", ar: "تدريب المقابلة",
  },
  "drl.pitch": {
    en: "Practice the answer before the room is real — the questions live on your device, so drilling works offline.", es: "Practica la respuesta antes de que la sala sea real — las preguntas viven en tu dispositivo, así que el ensayo funciona sin conexión.", fr: "Entraînez votre réponse avant que la salle ne soit réelle — les questions vivent sur votre appareil, l'exercice fonctionne donc hors ligne.", de: "Üb die Antwort, bevor der Raum echt ist — die Fragen liegen auf deinem Gerät, das Üben funktioniert also offline.", pt: "Pratique a resposta antes de a sala ser real — as perguntas vivem no seu dispositivo, por isso o treino funciona offline.", it: "Prova la risposta prima che la stanza sia reale — le domande vivono sul tuo dispositivo, quindi l'esercizio funziona offline.", ja: "本番の前に答えを練習しましょう — 質問は端末内にあるので、オフラインでも練習できます。", zh: "在真正走进面试间之前练习你的回答 — 题目就在你的设备上，离线也能演练。", hi: "कमरा असली होने से पहले उत्तर का अभ्यास करें — प्रश्न आपके डिवाइस पर हैं, इसलिए अभ्यास ऑफ़लाइन भी चलता है।", ar: "تدرّب على الإجابة قبل أن تصبح الغرفة حقيقية — الأسئلة على جهازك، فالتدريب يعمل دون اتصال.",
  },
  "drl.deal": {
    en: "Deal a question", es: "Sacar una pregunta", fr: "Tirer une question", de: "Eine Frage ziehen", pt: "Tirar uma pergunta", it: "Pesca una domanda", ja: "質問を引く", zh: "抽一道题", hi: "एक प्रश्न निकालें", ar: "اسحب سؤالًا",
  },
  "drl.probes": {
    en: "What it probes", es: "Qué sondea", fr: "Ce qu'elle sonde", de: "Was sie prüft", pt: "O que sonda", it: "Cosa sonda", ja: "問われていること", zh: "考察什么", hi: "यह क्या परखता है", ar: "ما الذي يسبره",
  },
  "drl.answer.ph": {
    en: "Say it out loud, then write what you said", es: "Dilo en voz alta y luego escribe lo que dijiste", fr: "Dites-le à voix haute, puis écrivez ce que vous avez dit", de: "Sag es laut, dann schreib auf, was du gesagt hast", pt: "Diga em voz alta e depois escreva o que disse", it: "Dillo ad alta voce, poi scrivi ciò che hai detto", ja: "声に出して言ってから、言ったことを書きましょう", zh: "先大声说出来，再写下你说的话", hi: "पहले ज़ोर से कहें, फिर जो कहा वह लिखें", ar: "قلها بصوت عالٍ ثم اكتب ما قلته",
  },
  "drl.read": {
    en: "Read my answer", es: "Leer mi respuesta", fr: "Lire ma réponse", de: "Meine Antwort lesen", pt: "Ler a minha resposta", it: "Leggi la mia risposta", ja: "答えを読む", zh: "点评我的回答", hi: "मेरा उत्तर पढ़ें", ar: "اقرأ إجابتي",
  },
  "drl.checklist": {
    en: "No online coach is standing — measure your answer against the probes above, honestly.", es: "No hay coach en línea — mide tu respuesta contra las sondas de arriba, con honestidad.", fr: "Aucun coach en ligne — mesurez votre réponse aux sondes ci-dessus, honnêtement.", de: "Kein Online-Coach verfügbar — miss deine Antwort ehrlich an den Prüfpunkten oben.", pt: "Nenhum coach online disponível — meça a sua resposta contra as sondas acima, com honestidade.", it: "Nessun coach online disponibile — misura la tua risposta sulle sonde qui sopra, onestamente.", ja: "オンラインコーチは不在です — 上の観点に照らして、自分の答えを正直に測ってください。", zh: "没有在线教练 — 请诚实地按上面的考察点衡量你的回答。", hi: "कोई ऑनलाइन कोच नहीं है — ऊपर के बिंदुओं पर अपना उत्तर ईमानदारी से परखें।", ar: "لا مدرب متصل الآن — قِس إجابتك على النقاط أعلاه بصدق.",
  },
  "let.title": {
    en: "Weekly letter", es: "Carta semanal", fr: "Lettre hebdomadaire", de: "Wochenbrief", pt: "Carta semanal", it: "Lettera settimanale", ja: "今週の手紙", zh: "每周信", hi: "साप्ताहिक पत्र", ar: "رسالة الأسبوع",
  },
  "let.pitch": {
    en: "What your week actually held, in words — written only from what you logged, never invented.", es: "Lo que tu semana realmente contuvo, en palabras — escrita solo a partir de lo que registraste, nunca inventada.", fr: "Ce que votre semaine a réellement contenu, en mots — écrite uniquement à partir de ce que vous avez consigné, jamais inventée.", de: "Was deine Woche wirklich enthielt, in Worten — geschrieben nur aus dem, was du eingetragen hast, nie erfunden.", pt: "O que a sua semana realmente conteve, em palavras — escrita apenas a partir do que registou, nunca inventada.", it: "Ciò che la tua settimana ha davvero contenuto, in parole — scritta solo da ciò che hai registrato, mai inventata.", ja: "あなたの一週間に実際にあったことを、言葉で — 記録したことだけから書かれ、決して創作しません。", zh: "你这一周真正发生了什么，用文字写出 — 只根据你记录的内容，绝不编造。", hi: "आपके सप्ताह में वास्तव में क्या था, शब्दों में — केवल आपके दर्ज किए से लिखा, कभी गढ़ा नहीं।", ar: "ما حملته أسبوعك فعلًا، بالكلمات — تُكتب فقط مما سجّلته، ولا تُخترع أبدًا.",
  },
  "let.write": {
    en: "Write this week's letter", es: "Escribir la carta de esta semana", fr: "Écrire la lettre de cette semaine", de: "Den Brief dieser Woche schreiben", pt: "Escrever a carta desta semana", it: "Scrivi la lettera di questa settimana", ja: "今週の手紙を書く", zh: "写这周的信", hi: "इस सप्ताह का पत्र लिखें", ar: "اكتب رسالة هذا الأسبوع",
  },
  "let.none": {
    en: "No letters yet.", es: "Aún no hay cartas.", fr: "Pas encore de lettre.", de: "Noch keine Briefe.", pt: "Ainda não há cartas.", it: "Nessuna lettera finora.", ja: "まだ手紙はありません。", zh: "还没有信。", hi: "अभी कोई पत्र नहीं।", ar: "لا رسائل بعد.",
  },
  "jrn.add": {
    en: "Add to the journal", es: "Añadir al diario", fr: "Ajouter au journal", de: "Zum Journal hinzufügen", pt: "Adicionar ao diário", it: "Aggiungi al diario", ja: "日誌に追加", zh: "写入日志", hi: "जर्नल में जोड़ें", ar: "أضف إلى اليوميات",
  },
  "jrn.vaulted": {
    en: " · sealed in the vault", es: " · sellado en la bóveda", fr: " · scellé dans le coffre", de: " · im Tresor versiegelt", pt: " · selado no cofre", it: " · sigillato nel caveau", ja: " · 保管庫に封印済み", zh: " · 已封入保险库", hi: " · तिजोरी में सील", ar: " · مختوم في الخزنة",
  },
  "jrn.speak": {
    en: "🎙 speak", es: "🎙 hablar", fr: "🎙 parler", de: "🎙 sprechen", pt: "🎙 falar", it: "🎙 parla", ja: "🎙 話す", zh: "🎙 说话", hi: "🎙 बोलें", ar: "🎙 تحدّث",
  },
  "jrn.listening": {
    en: "◼ listening…", es: "◼ escuchando…", fr: "◼ écoute…", de: "◼ hört zu…", pt: "◼ a ouvir…", it: "◼ in ascolto…", ja: "◼ 聞いています…", zh: "◼ 正在聆听…", hi: "◼ सुन रहा है…", ar: "◼ يستمع…",
  },
  "jrn.title": {
    en: "Journal", es: "Diario", fr: "Journal", de: "Tagebuch", pt: "Diário", it: "Diario", ja: "日記", zh: "日志", hi: "डायरी", ar: "اليوميات",
  },
  "jrn.sub": {
    en: "your words, typed or spoken", es: "tus palabras, escritas o habladas", fr: "vos mots, écrits ou dits", de: "Deine Worte, getippt oder gesprochen", pt: "as suas palavras, escritas ou faladas", it: "le tue parole, scritte o dette", ja: "あなたの言葉を、書いても話しても", zh: "你的话，打字或口述", hi: "आपके शब्द, टाइप किए या बोले", ar: "كلماتك، مكتوبة أو منطوقة",
  },
  "jrn.new": {
    en: "New entry", es: "Nueva entrada", fr: "Nouvelle entrée", de: "Neuer Eintrag", pt: "Nova entrada", it: "Nuova voce", ja: "新しい記録", zh: "新条目", hi: "नई प्रविष्टि", ar: "مدخل جديد",
  },
  "jrn.ph": {
    en: "How was today, really?", es: "¿Cómo fue hoy, de verdad?", fr: "Comment était cette journée, vraiment ?", de: "Wie war der Tag wirklich?", pt: "Como foi hoje, na verdade?", it: "Com'è andata oggi, davvero?", ja: "今日は本当のところ、どうでしたか？", zh: "今天到底过得怎么样？", hi: "आज सचमुच कैसा रहा?", ar: "كيف كان يومك، حقًا؟",
  },
  "jrn.sealed": {
    en: "Entries are sealed in your vault on a private plan. If an entry says you're in danger, your Guardian treats it exactly like a reading that says so.", es: "Las entradas se sellan en tu bóveda en un plan privado. Si una entrada dice que estás en peligro, tu Guardián la trata igual que una lectura que lo diga.", fr: "Les entrées sont scellées dans votre coffre sur un forfait privé. Si une entrée dit que vous êtes en danger, votre Gardien la traite exactement comme une mesure qui le dirait.", de: "Einträge werden bei einem privaten Tarif in deinem Tresor versiegelt. Sagt ein Eintrag, dass du in Gefahr bist, behandelt dein Guardian ihn genau wie eine Messung, die das sagt.", pt: "As entradas são seladas no seu cofre num plano privado. Se uma entrada disser que está em perigo, o seu Guardião trata-a exatamente como uma leitura que o diga.", it: "Le voci sono sigillate nel tuo caveau su un piano privato. Se una voce dice che sei in pericolo, il tuo Guardian la tratta esattamente come una lettura che lo dica.", ja: "プライベートプランでは、記録はあなたの保管庫に封印されます。危険を告げる記録があれば、ガーディアンはそれを同じことを告げる測定値とまったく同じに扱います。", zh: "在私有方案下，条目会封入你的保险库。若某条写着你身处危险，你的守护者会像对待同样内容的读数一样对待它。", hi: "निजी योजना पर प्रविष्टियाँ आपकी तिजोरी में सील होती हैं। यदि कोई प्रविष्टि कहती है कि आप ख़तरे में हैं, तो आपका गार्जियन उसे ठीक वैसे ही लेता है जैसे वैसा कहने वाली रीडिंग को।", ar: "تُختم المدخلات في خزنتك ضمن خطة خاصة. وإن قال مدخل إنك في خطر، عامله حارسك تمامًا كقراءة تقول ذلك.",
  },
  "jrn.entries": {
    en: "Entries", es: "Entradas", fr: "Entrées", de: "Einträge", pt: "Entradas", it: "Voci", ja: "記録", zh: "条目", hi: "प्रविष्टियाँ", ar: "المدخلات",
  },
  "jrn.none": {
    en: "Nothing yet — the first entry can be one sentence.", es: "Nada todavía — la primera entrada puede ser una frase.", fr: "Rien pour l'instant — la première entrée peut tenir en une phrase.", de: "Noch nichts — der erste Eintrag darf ein Satz sein.", pt: "Nada ainda — a primeira entrada pode ser uma frase.", it: "Ancora niente — la prima voce può essere una frase.", ja: "まだ何もありません — 最初の記録は一文で構いません。", zh: "尚无内容 — 第一条可以只写一句话。", hi: "अभी कुछ नहीं — पहली प्रविष्टि एक वाक्य भी हो सकती है।", ar: "لا شيء بعد — يكفي أن يكون المدخل الأول جملة واحدة.",
  },
  "cch.ask": {
    en: "Ask the coach", es: "Preguntar al coach", fr: "Demander au coach", de: "Den Coach fragen", pt: "Perguntar ao coach", it: "Chiedi al coach", ja: "コーチに尋ねる", zh: "询问教练", hi: "कोच से पूछें", ar: "اسأل المدرّب",
  },
  "cch.show.pic": {
    en: "Show it a picture", es: "Muéstrale una imagen", fr: "Montrez-lui une image", de: "Zeig ihm ein Bild", pt: "Mostre-lhe uma imagem", it: "Mostragli un'immagine", ja: "画像を見せる", zh: "给它看一张图片", hi: "इसे एक चित्र दिखाएँ", ar: "أرِه صورة",
  },
  "cch.show.screen": {
    en: "Show it your screen", es: "Muéstrale tu pantalla", fr: "Montrez-lui votre écran", de: "Zeig ihm deinen Bildschirm", pt: "Mostre-lhe o seu ecrã", it: "Mostragli il tuo schermo", ja: "画面を見せる", zh: "给它看你的屏幕", hi: "इसे अपनी स्क्रीन दिखाएँ", ar: "أرِه شاشتك",
  },
  "cch.show.grabbed": {
    en: "your screen, one frame", es: "tu pantalla, un fotograma", fr: "votre écran, une image", de: "dein Bildschirm, ein Einzelbild", pt: "o seu ecrã, um quadro", it: "il tuo schermo, un fotogramma", ja: "あなたの画面・1コマ", zh: "你的屏幕，一帧", hi: "आपकी स्क्रीन, एक फ़्रेम", ar: "شاشتك، إطار واحد",
  },
  "cch.show.drop": {
    en: "Put the picture down", es: "Retirar la imagen", fr: "Retirer l'image", de: "Das Bild weglegen", pt: "Retirar a imagem", it: "Mettere via l'immagine", ja: "画像を取り下げる", zh: "放下图片", hi: "चित्र हटाएँ", ar: "أنزِل الصورة",
  },
  "cch.thinking": {
    en: "Thinking…", es: "Pensando…", fr: "Réflexion…", de: "Denkt nach…", pt: "A pensar…", it: "Sto pensando…", ja: "考えています…", zh: "思考中…", hi: "सोच रहा है…", ar: "يفكّر…",
  },
  "cch.talk": {
    en: "🎙 Talk to it", es: "🎙 Háblale", fr: "🎙 Parlez-lui", de: "🎙 Sprich mit ihm", pt: "🎙 Fale com ele", it: "🎙 Parlagli", ja: "🎙 話しかける", zh: "🎙 对它说话", hi: "🎙 इससे बात करें", ar: "🎙 تحدّث إليه",
  },
  "cch.listening": {
    en: "◉ Listening — tap to send", es: "◉ Escuchando — toca para enviar", fr: "◉ Écoute — touchez pour envoyer", de: "◉ Hört zu — zum Senden tippen", pt: "◉ A ouvir — toque para enviar", it: "◉ In ascolto — tocca per inviare", ja: "◉ 聞いています — タップで送信", zh: "◉ 正在聆听 — 点按发送", hi: "◉ सुन रहा है — भेजने के लिए टैप करें", ar: "◉ يستمع — انقر للإرسال",
  },
  "cch.readaloud": {
    en: "🔊 Read it aloud", es: "🔊 Léelo en voz alta", fr: "🔊 Lire à voix haute", de: "🔊 Vorlesen", pt: "🔊 Ler em voz alta", it: "🔊 Leggilo ad alta voce", ja: "🔊 読み上げる", zh: "🔊 朗读", hi: "🔊 ज़ोर से पढ़ें", ar: "🔊 اقرأه بصوت عالٍ",
  },
  "cch.mute": {
    en: "Mute the microphone — the conversation stays open", es: "Silenciar el micrófono — la conversación sigue abierta", fr: "Couper le micro — la conversation reste ouverte", de: "Mikrofon stummschalten — das Gespräch bleibt offen", pt: "Silenciar o microfone — a conversa continua aberta", it: "Silenzia il microfono — la conversazione resta aperta", ja: "マイクをミュート — 会話は続いたままです", zh: "将麦克风静音 — 对话仍然继续", hi: "माइक्रोफ़ोन म्यूट करें — बातचीत खुली रहेगी", ar: "كتم الميكروفون — تبقى المحادثة مفتوحة",
  },
  "cch.unmute": {
    en: "Let it hear you again", es: "Deja que vuelva a oírte", fr: "Laissez-le vous entendre à nouveau", de: "Wieder zuhören lassen", pt: "Deixe-o ouvi-lo novamente", it: "Lascia che ti senta di nuovo", ja: "もう一度聞こえるようにする", zh: "让它重新听你说话", hi: "इसे फिर से सुनने दें", ar: "دعه يسمعك من جديد",
  },
  "cch.muted": {
    en: "muted — it cannot hear you, and the conversation is still open", es: "silenciado — no puede oírte y la conversación sigue abierta", fr: "micro coupé — il ne vous entend pas, la conversation reste ouverte", de: "stumm — es hört dich nicht, das Gespräch bleibt offen", pt: "silenciado — não o ouve, e a conversa continua aberta", it: "silenziato — non ti sente, e la conversazione resta aperta", ja: "ミュート中 — 聞こえていません。会話は続いています", zh: "已静音 — 它听不到你，对话仍在继续", hi: "म्यूट — यह आपको नहीं सुन सकता, बातचीत अब भी खुली है", ar: "مكتوم — لا يسمعك، والمحادثة ما زالت مفتوحة",
  },
  "cch.stop": {
    en: "■ Stop", es: "■ Detener", fr: "■ Arrêter", de: "■ Stopp", pt: "■ Parar", it: "■ Ferma", ja: "■ 停止", zh: "■ 停止", hi: "■ रोकें", ar: "■ أوقف",
  },
  "cch.listening.stop": {
    en: "listening — pause and it will answer, or tap to end the conversation", es: "escuchando — haz una pausa y responderá, o toca para terminar la conversación", fr: "écoute — marquez une pause et il répondra, ou touchez pour terminer la conversation", de: "hört zu — eine Pause, und es antwortet; oder tippen, um das Gespräch zu beenden", pt: "a ouvir — faça uma pausa e ele responde, ou toque para terminar a conversa", it: "in ascolto — fai una pausa e risponderà, o tocca per chiudere la conversazione", ja: "聞いています — 話し終えると自動で応答します。タップで会話を終了", zh: "正在聆听 — 停顿片刻即会回答，或点按结束对话", hi: "सुन रहा है — रुकिए तो यह उत्तर देगा, या बातचीत समाप्त करने के लिए टैप करें", ar: "يستمع — توقّف قليلاً وسيجيب، أو انقر لإنهاء المحادثة",
  },
  "cch.speaking.hush": {
    en: "speaking — interrupt any time, or tap to end the conversation", es: "hablando — interrumpe cuando quieras, o toca para terminar la conversación", fr: "parle — interrompez à tout moment, ou touchez pour terminer la conversation", de: "spricht — unterbrich jederzeit; oder tippen, um das Gespräch zu beenden", pt: "a falar — interrompa quando quiser, ou toque para terminar a conversa", it: "sta parlando — interrompi quando vuoi, o tocca per chiudere la conversazione", ja: "話しています — いつでも話しかけて遮れます。タップで会話を終了", zh: "正在说话 — 随时可以打断，或点按结束对话", hi: "बोल रहा है — कभी भी टोक सकते हैं, या बातचीत समाप्त करने के लिए टैप करें", ar: "يتحدث — قاطعه متى شئت، أو انقر لإنهاء المحادثة",
  },
  "cch.prov.online": {
    en: "an online model", es: "un modelo en línea", fr: "un modèle en ligne", de: "ein Online-Modell", pt: "um modelo online", it: "un modello online", ja: "オンラインのモデル", zh: "一个在线模型", hi: "एक ऑनलाइन मॉडल", ar: "نموذج عبر الإنترنت",
  },
  "cch.prov.unreached": {
    en: "the model could not be reached", es: "no se pudo contactar con el modelo", fr: "le modèle n'a pas pu être joint", de: "das Modell war nicht erreichbar", pt: "não foi possível contactar o modelo", it: "non è stato possibile raggiungere il modello", ja: "モデルに到達できませんでした", zh: "无法连接到该模型", hi: "मॉडल तक नहीं पहुँचा जा सका", ar: "تعذّر الوصول إلى النموذج",
  },
  "cch.title": {
    en: "Coach", es: "Coach", fr: "Coach", de: "Coach", pt: "Coach", it: "Coach", ja: "コーチ", zh: "教练", hi: "कोच", ar: "مدرب",
  },
  "cch.knows": {
    en: "What the coach holds", es: "Lo que el coach guarda", fr: "Ce que le coach détient", de: "Was der Coach bereithält", pt: "O que o coach guarda", it: "Ciò che il coach custodisce", ja: "コーチが持っている知識", zh: "教练掌握的内容", hi: "कोच के पास क्या है", ar: "ما يحتفظ به المدرب",
  },
  "cch.knows.counts": {
    en: "{pack} curated entries · {learned} learned by JIM · {deposits} deposited from model turns — answered offline, on this device", es: "{pack} entradas seleccionadas · {learned} aprendidas por JIM · {deposits} depositadas de turnos del modelo — respondido sin conexión, en este dispositivo", fr: "{pack} entrées sélectionnées · {learned} apprises par JIM · {deposits} déposées depuis des tours du modèle — répondu hors ligne, sur cet appareil", de: "{pack} kuratierte Einträge · {learned} von JIM gelernt · {deposits} aus Modell-Antworten hinterlegt — offline beantwortet, auf diesem Gerät", pt: "{pack} entradas selecionadas · {learned} aprendidas pelo JIM · {deposits} depositadas de respostas do modelo — respondido offline, neste dispositivo", it: "{pack} voci curate · {learned} apprese da JIM · {deposits} depositate dai turni del modello — risposto offline, su questo dispositivo", ja: "厳選エントリ {pack} 件 · JIM が学んだもの {learned} 件 · モデル回答からの蓄積 {deposits} 件 — この端末上でオフライン回答", zh: "{pack} 条精选条目 · JIM 学到 {learned} 条 · 模型回答沉淀 {deposits} 条——在本设备离线作答", hi: "{pack} चुनी हुई प्रविष्टियाँ · JIM ने {learned} सीखीं · मॉडल उत्तरों से {deposits} जमा — इसी डिवाइस पर ऑफ़लाइन उत्तर", ar: "{pack} مدخلات منسّقة · تعلّم JIM ‏{learned} · ‏{deposits} مودَعة من ردود النموذج — يُجاب دون اتصال، على هذا الجهاز",
  },
  "cal.listen": {
    en: "Start listening", es: "Empezar a escuchar", fr: "Commencer à écouter", de: "Zuhören beginnen", pt: "Começar a escutar", it: "Inizia ad ascoltare", ja: "聞き取りを開始", zh: "开始收听", hi: "सुनना शुरू करें", ar: "ابدأ الاستماع",
  },
  "cal.listening": {
    en: "It is listening now.", es: "Ahora está escuchando.", fr: "Il écoute maintenant.", de: "Es hört jetzt zu.", pt: "Está a escutar agora.", it: "Ora sta ascoltando.", ja: "現在、聞き取っています。", zh: "现在正在收听。", hi: "अब यह सुन रहा है।", ar: "إنه يستمع الآن.",
  },
  "cal.end": {
    en: "End the call", es: "Terminar la llamada", fr: "Terminer l'appel", de: "Gespräch beenden", pt: "Terminar a chamada", it: "Termina la chiamata", ja: "通話を終える", zh: "结束通话", hi: "कॉल समाप्त करें", ar: "أنهِ المكالمة",
  },
  "cal.ended": {
    en: "The call is over.", es: "La llamada ha terminado.", fr: "L'appel est terminé.", de: "Das Gespräch ist beendet.", pt: "A chamada terminou.", it: "La chiamata è finita.", ja: "通話は終了しました。", zh: "通话已结束。", hi: "कॉल समाप्त हो गई।", ar: "انتهت المكالمة.",
  },
  "mon.sense": {
    en: "Take a reading now", es: "Tomar una lectura ahora", fr: "Prendre une mesure maintenant", de: "Jetzt eine Messung nehmen", pt: "Fazer uma leitura agora", it: "Fai una rilevazione ora", ja: "いま計測する", zh: "立即读取一次", hi: "अभी एक रीडिंग लें", ar: "خُذ قراءة الآن",
  },
  "mon.sensing": {
    en: "It is sensing.", es: "Está detectando.", fr: "Il capte.", de: "Es erfasst.", pt: "Está a detetar.", it: "Sta rilevando.", ja: "感知しています。", zh: "正在感知。", hi: "यह महसूस कर रहा है।", ar: "إنه يستشعر.",
  },
  "lia.head": {
    en: "Two guardians working together", es: "Dos guardianes trabajando juntos", fr: "Deux gardiens qui travaillent ensemble", de: "Zwei Wächter, die zusammenarbeiten", pt: "Dois guardiões a trabalhar juntos", it: "Due guardiani che lavorano insieme", ja: "二つのガーディアンの連携", zh: "两位守护者协同工作", hi: "दो गार्जियन साथ काम करते हुए", ar: "حارسان يعملان معًا",
  },
  "lia.lead": {
    en: "Never on the line and never out loud: yours and theirs talk over the network, and only between people who are already each other's contacts. You can read what yours said afterwards — their half was never yours to read.", es: "Nunca en la línea ni en voz alta: el tuyo y el suyo hablan por la red, y solo entre personas que ya son contactos. Después puedes leer lo que dijo el tuyo; la parte del otro nunca fue tuya para leerla.", fr: "Jamais sur la ligne ni à voix haute : le vôtre et le leur se parlent par le réseau, et seulement entre personnes déjà en contact. Vous pourrez lire ce que le vôtre a dit — leur moitié ne vous a jamais appartenu.", de: "Nie auf der Leitung und nie laut: deiner und ihrer sprechen über das Netz, und nur zwischen Menschen, die schon Kontakte sind. Du kannst danach lesen, was deiner gesagt hat — ihre Hälfte war nie deine.", pt: "Nunca na linha nem em voz alta: o seu e o dele falam pela rede, e só entre pessoas que já são contactos. Depois pode ler o que o seu disse — a metade do outro nunca foi sua para ler.", it: "Mai sulla linea e mai ad alta voce: il tuo e il loro parlano in rete, e solo tra persone già in contatto. Dopo puoi leggere cosa ha detto il tuo — la metà dell'altro non è mai stata tua.", ja: "回線上でも声でもなく、ネットワーク越しに、すでに連絡先どうしの相手とだけ。自分のガーディアンが何を言ったかは後で読めます。相手の側はもともとあなたが読むものではありません。", zh: "不在通话中、也不出声：你的和对方的通过网络交谈，且仅限彼此已是联系人的双方。事后你可以读到自己这一半说了什么——对方那一半从来不属于你。", hi: "न लाइन पर, न आवाज़ में: आपका और उनका नेटवर्क पर बात करते हैं, और केवल उन लोगों के बीच जो पहले से एक-दूसरे के संपर्क हैं। बाद में आप पढ़ सकते हैं कि आपके वाले ने क्या कहा — उनका हिस्सा कभी आपका पढ़ने को नहीं था।", ar: "لا على الخط ولا بصوت مسموع: حارسك وحارسهم يتحدثان عبر الشبكة، وفقط بين من هم أصلًا جهات اتصال لبعضهم. يمكنك لاحقًا قراءة ما قاله حارسك — أما نصفهم فلم يكن لك يومًا.",
  },
  "lia.who.ph": {
    en: "Their id", es: "Su identificador", fr: "Leur identifiant", de: "Ihre Kennung", pt: "O id deles", it: "Il loro id", ja: "相手のID", zh: "对方的 ID", hi: "उनकी आईडी", ar: "معرّفهم",
  },
  "lia.open": {
    en: "Open a link", es: "Abrir un enlace", fr: "Ouvrir un lien", de: "Verbindung öffnen", pt: "Abrir uma ligação", it: "Apri un collegamento", ja: "リンクを開く", zh: "建立连接", hi: "लिंक खोलें", ar: "افتح صلة",
  },
  "lia.opened": {
    en: "Open.", es: "Abierto.", fr: "Ouvert.", de: "Offen.", pt: "Aberto.", it: "Aperto.", ja: "開きました。", zh: "已建立。", hi: "खुल गया।", ar: "مفتوح.",
  },
  "lia.running": {
    en: "still going", es: "sigue en marcha", fr: "toujours en cours", de: "läuft noch", pt: "ainda a decorrer", it: "ancora in corso", ja: "進行中", zh: "仍在进行", hi: "अब भी चल रहा है", ar: "ما زال جاريًا",
  },
  "lia.closed": {
    en: "closed", es: "cerrado", fr: "fermé", de: "geschlossen", pt: "fechado", it: "chiuso", ja: "終了", zh: "已结束", hi: "बंद", ar: "مغلق",
  },
  "lia.mine": {
    en: "What mine said", es: "Lo que dijo el mío", fr: "Ce que le mien a dit", de: "Was meiner gesagt hat", pt: "O que o meu disse", it: "Cosa ha detto il mio", ja: "自分のが言ったこと", zh: "我这边说了什么", hi: "मेरे वाले ने क्या कहा", ar: "ما قاله حارسي",
  },
  "lia.bymine": {
    en: "Mine said:", es: "El mío dijo:", fr: "Le mien a dit :", de: "Meiner sagte:", pt: "O meu disse:", it: "Il mio ha detto:", ja: "自分のガーディアン：", zh: "我这边说：", hi: "मेरे वाले ने कहा:", ar: "قال حارسي:",
  },
  "lia.tomine": {
    en: "Theirs said:", es: "El suyo dijo:", fr: "Le leur a dit :", de: "Ihrer sagte:", pt: "O deles disse:", it: "Il loro ha detto:", ja: "相手のガーディアン：", zh: "对方说：", hi: "उनके वाले ने कहा:", ar: "قال حارسهم:",
  },
  "lia.say": {
    en: "Say something across it", es: "Decir algo por él", fr: "Y dire quelque chose", de: "Etwas darüber sagen", pt: "Dizer algo por ela", it: "Di' qualcosa attraverso", ja: "これを通じて伝える", zh: "通过它说一句", hi: "इसके ज़रिए कुछ कहें", ar: "قل شيئًا عبرها",
  },
  "lia.saidit": {
    en: "Said, and on your half.", es: "Dicho, y en tu parte.", fr: "Dit, et dans votre moitié.", de: "Gesagt, und auf deiner Hälfte.", pt: "Dito, e na sua metade.", it: "Detto, e sulla tua metà.", ja: "伝えました。あなたの側に記録されています。", zh: "已说出，并记在你这一半。", hi: "कह दिया गया, और आपके हिस्से में।", ar: "قيل، وسُجّل في نصفك.",
  },
  "lia.said.example": {
    en: "the rate has not moved in three years", es: "la tarifa no ha cambiado en tres años", fr: "le tarif n'a pas bougé depuis trois ans", de: "der Satz hat sich seit drei Jahren nicht bewegt", pt: "a taxa não mudou em três anos", it: "la tariffa non cambia da tre anni", ja: "この三年、単価が変わっていません", zh: "这个费率三年没变过", hi: "दर तीन साल से नहीं बदली", ar: "لم يتغير السعر منذ ثلاث سنوات",
  },
  "lia.task": {
    en: "Name the work", es: "Nombrar el trabajo", fr: "Nommer le travail", de: "Die Arbeit benennen", pt: "Nomear o trabalho", it: "Dai un nome al lavoro", ja: "作業に名前をつける", zh: "为这项工作命名", hi: "काम को नाम दें", ar: "سمِّ العمل",
  },
  "lia.task.example": {
    en: "send the revised figures", es: "enviar las cifras revisadas", fr: "envoyer les chiffres révisés", de: "die überarbeiteten Zahlen senden", pt: "enviar os números revistos", it: "inviare i numeri rivisti", ja: "修正した数字を送る", zh: "发送修订后的数字", hi: "संशोधित आँकड़े भेजें", ar: "إرسال الأرقام المنقّحة",
  },
  // Naming it is this side's own yes and nothing more. The old wording here
  // said "It outlives the call now", which was true of the one-sided rule
  // this round replaced and would now be a promise the backend refuses.
  "lia.tasked": {
    en: "Named. It outlives the call once they agree too.", es: "Nombrado. Sobrevivirá a la llamada cuando la otra parte también acepte.", fr: "Nommé. Il survivra à l'appel quand l'autre l'aura accepté aussi.", de: "Benannt. Es überdauert das Gespräch, sobald die andere Seite ebenfalls zustimmt.", pt: "Nomeado. Sobreviverá à chamada quando a outra parte também concordar.", it: "Nominato. Sopravvivrà alla chiamata quando anche l'altra parte sarà d'accordo.", ja: "名前をつけました。相手も同意すれば、通話が終わっても続きます。", zh: "已命名。等对方也同意后，它会延续到通话之后。", hi: "नाम दे दिया गया। जब वे भी सहमत होंगे, तब यह कॉल के बाद भी रहेगा।", ar: "سُمّي. سيمتد بعد المكالمة متى وافق الطرف الآخر أيضًا.",
  },
  "lia.agree": {
    en: "Agree to it", es: "Aceptarlo", fr: "L'accepter", de: "Zustimmen", pt: "Concordar", it: "Accettalo", ja: "同意する", zh: "同意", hi: "सहमत हों", ar: "وافق عليها",
  },
  "lia.agreed": {
    en: "Agreed. It outlives the call now.", es: "Aceptado. Ahora sobrevive a la llamada.", fr: "Accepté. Il survit désormais à l'appel.", de: "Zugestimmt. Es überdauert jetzt das Gespräch.", pt: "Concordado. Agora sobrevive à chamada.", it: "Accettato. Ora sopravvive alla chiamata.", ja: "同意しました。通話が終わっても続きます。", zh: "已同意。它现在会延续到通话之后。", hi: "सहमति दे दी गई। अब यह कॉल के बाद भी रहेगा।", ar: "تمت الموافقة. صار يمتد بعد المكالمة.",
  },
  // Where the task has got to, from this person's side. Three states, and
  // the middle one is the whole point of the round: work you proposed that
  // nobody has agreed to holds nothing open.
  "lia.waiting": {
    en: "waiting for them to agree", es: "esperando a que acepten", fr: "en attente de leur accord", de: "wartet auf ihre Zustimmung", pt: "à espera que concordem", it: "in attesa del loro accordo", ja: "相手の同意を待っています", zh: "等待对方同意", hi: "उनकी सहमति की प्रतीक्षा", ar: "في انتظار موافقتهم",
  },
  "lia.yours": {
    en: "they proposed it — your turn to agree", es: "lo propusieron: te toca aceptar", fr: "ils l'ont proposé — à vous de l'accepter", de: "sie haben es vorgeschlagen — du bist mit der Zustimmung dran", pt: "propuseram-no — falta a sua concordância", it: "l'hanno proposto: tocca a te accettare", ja: "相手が提案しました — 次はあなたの同意です", zh: "对方已提议 — 轮到你同意了", hi: "उन्होंने प्रस्ताव रखा — अब आपकी सहमति की बारी", ar: "اقترحوها — دورك للموافقة",
  },
  "lia.holds": {
    en: "both agreed — this is what keeps the link open", es: "ambos aceptaron: esto es lo que mantiene abierto el enlace", fr: "les deux ont accepté — c'est ce qui maintient le lien ouvert", de: "beide zugestimmt — das hält die Verbindung offen", pt: "ambos concordaram — é isto que mantém a ligação aberta", it: "entrambi d'accordo: è questo che tiene aperto il collegamento", ja: "双方が合意しました — これがリンクを開いたままにしています", zh: "双方已同意 — 这就是让链接保持开启的原因", hi: "दोनों सहमत — यही कड़ी को खुला रखता है", ar: "وافق الطرفان — هذا ما يُبقي الصلة مفتوحة",
  },
  "lia.stop": {
    en: "Stop it", es: "Detenerlo", fr: "L'arrêter", de: "Beenden", pt: "Parar", it: "Fermalo", ja: "停止する", zh: "停止", hi: "रोकें", ar: "أوقفها",
  },
  "lia.stopped": {
    en: "Stopped.", es: "Detenido.", fr: "Arrêté.", de: "Beendet.", pt: "Parado.", it: "Fermato.", ja: "停止しました。", zh: "已停止。", hi: "रोक दिया गया।", ar: "أُوقفت.",
  },
  "mon.head": {
    en: "What may sense you", es: "Lo que puede detectarte", fr: "Ce qui peut vous capter", de: "Was dich erfassen darf", pt: "O que o pode detetar", it: "Cosa può rilevarti", ja: "あなたを感知してよいもの", zh: "什么可以感知你", hi: "आपको क्या महसूस कर सकता है", ar: "ما يُسمح له باستشعارك",
  },
  "mon.lead": {
    en: "Everything that can be plugged in, and what each one costs: what it takes in, who else it reaches, and what stays behind afterwards. Nothing that senses other people is ever on until you turn it on.", es: "Todo lo que se puede conectar y lo que cuesta cada cosa: qué capta, a quién más alcanza y qué queda después. Nada que detecte a otras personas está activo hasta que tú lo actives.", fr: "Tout ce qui peut être branché, et ce que cela coûte : ce qu'il capte, qui d'autre il atteint, et ce qui reste ensuite. Rien de ce qui capte autrui n'est actif tant que vous ne l'activez pas.", de: "Alles, was sich anschließen lässt, und was es kostet: was es aufnimmt, wen es sonst erreicht, und was danach bleibt. Nichts, was andere Menschen erfasst, ist an, bevor du es einschaltest.", pt: "Tudo o que pode ser ligado e o que cada coisa custa: o que capta, quem mais alcança, e o que fica depois. Nada que detete outras pessoas está ativo até o ativar.", it: "Tutto ciò che si può collegare e cosa costa: cosa capta, chi altro raggiunge e cosa resta dopo. Nulla che rilevi altre persone è attivo finché non lo attivi tu.", ja: "接続できるものすべてと、それぞれの代償：何を取り込み、ほかに誰まで届き、あとに何が残るか。他人を感知するものは、あなたが有効にするまで作動しません。", zh: "所有可以接入的东西，以及各自的代价：它接收什么、还会触及谁、事后留下什么。凡是会感知到他人的，在你开启之前都不会运行。", hi: "जो कुछ जोड़ा जा सकता है और हर एक की क़ीमत: वह क्या ग्रहण करता है, और किन तक पहुँचता है, और बाद में क्या बचा रहता है। जो दूसरों को महसूस करता है, वह तब तक चालू नहीं होता जब तक आप न करें।", ar: "كل ما يمكن توصيله وما تكلفته: ماذا يلتقط، ومن غيرك يطاله، وماذا يبقى بعده. لا شيء يستشعر أشخاصًا آخرين يعمل قبل أن تشغّله أنت.",
  },
  "mon.others": {
    en: "senses other people", es: "detecta a otras personas", fr: "capte d'autres personnes", de: "erfasst andere Menschen", pt: "deteta outras pessoas", it: "rileva altre persone", ja: "他人も感知します", zh: "会感知到他人", hi: "दूसरों को भी महसूस करता है", ar: "يستشعر أشخاصًا آخرين",
  },
  "mon.keeps": {
    en: "What stays behind:", es: "Qué queda después:", fr: "Ce qui reste :", de: "Was bleibt:", pt: "O que fica:", it: "Cosa resta:", ja: "あとに残るもの：", zh: "事后留下：", hi: "बाद में क्या बचता है:", ar: "ما يبقى:",
  },
  "mon.on": {
    en: "On.", es: "Activado.", fr: "Activé.", de: "An.", pt: "Ativo.", it: "Attivo.", ja: "有効です。", zh: "已开启。", hi: "चालू है।", ar: "مفعّل.",
  },
  "mon.off": {
    en: "Off. Nobody has switched this on.", es: "Desactivado. Nadie lo ha activado.", fr: "Désactivé. Personne ne l'a activé.", de: "Aus. Niemand hat das eingeschaltet.", pt: "Desativado. Ninguém o ativou.", it: "Disattivato. Nessuno l'ha attivato.", ja: "無効です。誰も有効にしていません。", zh: "未开启。没有人开启过它。", hi: "बंद है। किसी ने इसे चालू नहीं किया।", ar: "مغلق. لم يفعّله أحد.",
  },
  "mon.keeping": {
    en: "and keeping what it senses", es: "y guarda lo que detecta", fr: "et conserve ce qu'il capte", de: "und behält, was er erfasst", pt: "e guarda o que deteta", it: "e conserva ciò che rileva", ja: "感知した内容を保持します", zh: "并保留其感知到的内容", hi: "और जो महसूस करता है उसे रखता है", ar: "ويحتفظ بما يستشعره",
  },
  "mon.plug": {
    en: "Switch it on", es: "Activarlo", fr: "L'activer", de: "Einschalten", pt: "Ativar", it: "Attivalo", ja: "有効にする", zh: "开启", hi: "चालू करें", ar: "شغّله",
  },
  "mon.plug.told": {
    en: "They have been told — switch it on", es: "Ya se les ha informado: activarlo", fr: "Ils ont été prévenus — l'activer", de: "Sie wurden informiert — einschalten", pt: "Já foram avisados — ativar", it: "Sono stati avvisati — attivalo", ja: "伝えました — 有効にする", zh: "已经告知他们——开启", hi: "उन्हें बता दिया गया — चालू करें", ar: "أُبلغوا — شغّله",
  },
  "mon.plugged": {
    en: "Switched on.", es: "Activado.", fr: "Activé.", de: "Eingeschaltet.", pt: "Ativado.", it: "Attivato.", ja: "有効にしました。", zh: "已开启。", hi: "चालू कर दिया गया।", ar: "تم تشغيله.",
  },
  "mon.unplug": {
    en: "Switch it off", es: "Desactivarlo", fr: "Le désactiver", de: "Ausschalten", pt: "Desativar", it: "Disattivalo", ja: "無効にする", zh: "关闭", hi: "बंद करें", ar: "أوقفه",
  },
  "mon.unplugged": {
    en: "Switched off.", es: "Desactivado.", fr: "Désactivé.", de: "Ausgeschaltet.", pt: "Desativado.", it: "Disattivato.", ja: "無効にしました。", zh: "已关闭。", hi: "बंद कर दिया गया।", ar: "تم إيقافه.",
  },
  "cal.head": {
    en: "An aid on the call", es: "Una ayuda en la llamada", fr: "Une aide pendant l'appel", de: "Eine Hilfe im Gespräch", pt: "Uma ajuda na chamada", it: "Un aiuto durante la chiamata", ja: "通話に付き添う支援", zh: "通话中的协助", hi: "कॉल में सहायक", ar: "مساعدة أثناء المكالمة",
  },
  "cal.lead": {
    en: "On a call other people can hear, the other side is told first — the notice everybody has heard on a support line, in a language their number suggests they speak. Nothing listens until it has gone out.", es: "En una llamada que otros pueden oír, se avisa primero a la otra parte — el aviso que todos hemos oído en atención al cliente, en el idioma que sugiere su número. Nada escucha hasta que se haya reproducido.", fr: "Sur un appel que d'autres peuvent entendre, l'autre partie est prévenue d'abord — l'avis que tout le monde a entendu sur une ligne d'assistance, dans la langue que son numéro suggère. Rien n'écoute avant qu'il soit passé.", de: "Bei einem Gespräch, das andere mithören können, wird die Gegenseite zuerst informiert — der Hinweis, den alle von der Hotline kennen, in der Sprache, die ihre Nummer nahelegt. Nichts hört zu, bevor er gelaufen ist.", pt: "Numa chamada que outros podem ouvir, a outra parte é avisada primeiro — o aviso que todos já ouviram numa linha de apoio, no idioma que o número sugere. Nada escuta até ter sido reproduzido.", it: "In una chiamata che altri possono sentire, l'altra parte viene avvisata per prima — l'avviso che tutti hanno sentito su una linea di assistenza, nella lingua che il numero suggerisce. Nulla ascolta finché non è stato riprodotto.", ja: "他の人にも聞こえる通話では、まず相手に伝えます — サポートセンターで誰もが聞いたことのあるあの案内を、相手の番号から推測される言語で。流れるまでは何も聞き取りません。", zh: "在他人也能听到的通话中，先告知对方——就是大家在客服热线上都听过的那句话，用其号码所提示的语言播放。在播放之前，不会开始收听。", hi: "जिस कॉल को दूसरे भी सुन सकते हैं, वहाँ पहले दूसरे पक्ष को बताया जाता है — वही सूचना जो सब ने ग्राहक सेवा पर सुनी है, उनके नंबर से अनुमानित भाषा में। जब तक वह न चल जाए, कुछ भी नहीं सुना जाता।", ar: "في مكالمة يمكن لآخرين سماعها، يُبلَّغ الطرف الآخر أولًا — التنبيه الذي سمعه الجميع على خط الدعم، بلغة يرجّحها رقمه. ولا يستمع شيء قبل أن يُذاع.",
  },
  "cal.number.ph": {
    en: "Their number, for the language", es: "Su número, para el idioma", fr: "Leur numéro, pour la langue", de: "Ihre Nummer, für die Sprache", pt: "O número deles, para o idioma", it: "Il loro numero, per la lingua", ja: "相手の番号（言語の判断用）", zh: "对方号码（用于判断语言）", hi: "उनका नंबर, भाषा के लिए", ar: "رقمهم، لتحديد اللغة",
  },
  "cal.open": {
    en: "Set up the call", es: "Preparar la llamada", fr: "Préparer l'appel", de: "Gespräch vorbereiten", pt: "Preparar a chamada", it: "Prepara la chiamata", ja: "通話を準備する", zh: "准备通话", hi: "कॉल तैयार करें", ar: "جهّز المكالمة",
  },
  "cal.play": {
    en: "Play this on the line:", es: "Reproduce esto en la línea:", fr: "Diffusez ceci sur la ligne :", de: "Spiele das auf der Leitung ab:", pt: "Reproduza isto na linha:", it: "Riproduci questo sulla linea:", ja: "回線でこれを流してください：", zh: "请在通话中播放这段：", hi: "इसे लाइन पर चलाइए:", ar: "شغّل هذا على الخط:",
  },
  "cal.from": {
    en: "Language picked from", es: "Idioma elegido a partir de", fr: "Langue choisie d'après", de: "Sprache gewählt anhand von", pt: "Idioma escolhido a partir de", it: "Lingua scelta da", ja: "言語の判断根拠：", zh: "语言依据", hi: "भाषा इससे चुनी गई", ar: "اللغة اختيرت من",
  },
  "cal.played": {
    en: "It has been played", es: "Ya se ha reproducido", fr: "Il a été diffusé", de: "Er wurde abgespielt", pt: "Já foi reproduzido", it: "È stato riprodotto", ja: "流し終えました", zh: "已经播放", hi: "इसे चला दिया गया", ar: "تم تشغيله",
  },
  "cal.done": {
    en: "The other side has been told. It can listen now.", es: "Se ha informado a la otra parte. Ya puede escuchar.", fr: "L'autre partie a été prévenue. L'écoute peut commencer.", de: "Die Gegenseite wurde informiert. Jetzt darf zugehört werden.", pt: "A outra parte foi avisada. Já pode escutar.", it: "L'altra parte è stata avvisata. Ora può ascoltare.", ja: "相手に伝わりました。これから聞き取れます。", zh: "已告知对方，现在可以开始收听。", hi: "दूसरे पक्ष को बता दिया गया। अब यह सुन सकता है।", ar: "أُبلغ الطرف الآخر. يمكنه الاستماع الآن.",
  },
  "cal.told": {
    en: "told", es: "avisado", fr: "prévenu", de: "informiert", pt: "avisado", it: "avvisato", ja: "伝達済み", zh: "已告知", hi: "बताया गया", ar: "أُبلغ",
  },
  "cal.nevertold": {
    en: "never told, never listened", es: "nunca avisado, nunca escuchó", fr: "jamais prévenu, jamais écouté", de: "nie informiert, nie zugehört", pt: "nunca avisado, nunca escutou", it: "mai avvisato, mai ascoltato", ja: "未伝達・未聴取", zh: "未告知，也未收听", hi: "न बताया गया, न सुना गया", ar: "لم يُبلَّغ ولم يستمع",
  },
  "bes.head": {
    en: "Beside you while you write", es: "A tu lado mientras escribes", fr: "À vos côtés pendant que vous écrivez", de: "Neben dir, während du schreibst", pt: "Ao seu lado enquanto escreve", it: "Accanto a te mentre scrivi", ja: "書いているあいだ、そばで", zh: "你写作时在你身边", hi: "जब आप लिखते हैं, आपके साथ", ar: "بجانبك وأنت تكتب",
  },
  "bes.pitch": {
    en: "Paste what you are working on — a page for a customer, a strategy note. It is read here on this device, remarked on, and dropped: nothing is saved and nothing is edited.", es: "Pega lo que estés escribiendo — una página para un cliente, una nota de estrategia. Se lee aquí, en este dispositivo, se comenta y se descarta: no se guarda nada ni se edita nada.", fr: "Collez ce sur quoi vous travaillez — une page pour un client, une note de stratégie. C'est lu ici, sur cet appareil, commenté, puis abandonné : rien n'est enregistré et rien n'est modifié.", de: "Füge ein, woran du arbeitest — eine Seite für einen Kunden, eine Strategienotiz. Es wird hier auf diesem Gerät gelesen, kommentiert und verworfen: nichts wird gespeichert und nichts verändert.", pt: "Cole aquilo em que está a trabalhar — uma página para um cliente, uma nota de estratégia. É lido aqui, neste dispositivo, comentado e descartado: nada é guardado e nada é alterado.", it: "Incolla ciò a cui stai lavorando — una pagina per un cliente, una nota di strategia. Viene letto qui, su questo dispositivo, commentato e scartato: non si salva nulla e non si modifica nulla.", ja: "いま書いているものを貼ってください — 顧客向けのページでも、戦略メモでも。この端末の中だけで読み、気づいた点を返し、そのまま破棄します。保存も編集もしません。", zh: "把你正在写的内容贴进来——给客户的页面、策略备忘。它只在本设备上被阅读、给出意见，然后丢弃：不保存，也不改动。", hi: "आप जिस पर काम कर रहे हैं उसे यहाँ चिपकाइए — ग्राहक के लिए पन्ना, रणनीति नोट। यह इसी डिवाइस पर पढ़ा जाता है, टिप्पणी दी जाती है, और छोड़ दिया जाता है: कुछ भी सहेजा या बदला नहीं जाता।", ar: "الصق ما تعمل عليه — صفحة لعميل، مذكرة استراتيجية. يُقرأ هنا على هذا الجهاز، ويُعلَّق عليه، ثم يُطرح: لا يُحفظ شيء ولا يُعدَّل شيء.",
  },
  "bes.ph": {
    en: "What you are writing", es: "Lo que estás escribiendo", fr: "Ce que vous écrivez", de: "Woran du schreibst", pt: "O que está a escrever", it: "Ciò che stai scrivendo", ja: "書いている内容", zh: "你正在写的内容", hi: "आप क्या लिख रहे हैं", ar: "ما تكتبه",
  },
  "bes.go": {
    en: "Have a look", es: "Échale un vistazo", fr: "Jetez-y un œil", de: "Sieh es dir an", pt: "Dê uma olhada", it: "Dacci un'occhiata", ja: "見てもらう", zh: "看一看", hi: "एक नज़र डालो", ar: "ألقِ نظرة",
  },
  "bes.kind.forgot": {
    en: "You have not mentioned", es: "No has mencionado", fr: "Vous n'avez pas mentionné", de: "Du hast nicht erwähnt", pt: "Não mencionou", it: "Non hai menzionato", ja: "触れていない点：", zh: "你还没有提到", hi: "आपने ज़िक्र नहीं किया", ar: "لم تذكر",
  },
  "bes.kind.angle": {
    en: "Another angle", es: "Otro enfoque", fr: "Un autre angle", de: "Ein anderer Blickwinkel", pt: "Outro ângulo", it: "Un altro punto di vista", ja: "別の切り口：", zh: "另一个角度", hi: "एक और पहलू", ar: "زاوية أخرى",
  },
  "bes.kind.offer": {
    en: "I can do this part", es: "Puedo encargarme de esto", fr: "Je peux faire cette partie", de: "Diesen Teil kann ich übernehmen", pt: "Posso tratar desta parte", it: "Questa parte posso farla io", ja: "この部分は私がやれます：", zh: "这部分我可以做", hi: "यह हिस्सा मैं कर सकता हूँ", ar: "يمكنني تولّي هذا الجزء",
  },
  "err.head": {
    en: "What it studied on its own", es: "Lo que estudió por su cuenta", fr: "Ce qu'il a étudié de lui-même", de: "Was er von sich aus studiert hat", pt: "O que estudou por conta própria", it: "Cosa ha studiato da solo", ja: "自分で学んだこと", zh: "它自己学到的内容", hi: "इसने स्वयं क्या पढ़ा", ar: "ما درسه من تلقاء نفسه",
  },
  "err.today": {
    en: "studied today", es: "estudiado hoy", fr: "étudié aujourd'hui", de: "heute studiert", pt: "estudado hoje", it: "studiato oggi", ja: "本日の学習", zh: "今天已学习", hi: "आज पढ़ा गया", ar: "دُرس اليوم",
  },
  "err.notallowed": {
    en: "Not allowed to study on its own yet. Turn it on in what it may do for you — it says there what it sends and what it keeps.", es: "Aún no puede estudiar por su cuenta. Actívalo en lo que puede hacer por ti: allí dice qué envía y qué guarda.", fr: "Il n'a pas encore le droit d'étudier de lui-même. Activez-le dans ce qu'il peut faire pour vous — il y est dit ce qu'il envoie et ce qu'il conserve.", de: "Darf noch nicht von sich aus nachforschen. Schalte es dort frei, wo steht, was er für dich tun darf — und was er sendet und behält.", pt: "Ainda não pode estudar por conta própria. Ative-o no que ele pode fazer por si — aí diz o que envia e o que guarda.", it: "Non può ancora studiare da solo. Attivalo in ciò che può fare per te: lì dice cosa invia e cosa conserva.", ja: "まだ自分で調べることは許可されていません。「あなたのためにできること」で有効にしてください。何を送り何を保持するかもそこに書かれています。", zh: "尚未获准自行学习。请在“它能为你做什么”中开启——那里写明了它会发送什么、保留什么。", hi: "अभी स्वयं पढ़ने की अनुमति नहीं है। «यह आपके लिए क्या कर सकता है» में इसे चालू कीजिए — वहाँ लिखा है कि यह क्या भेजता है और क्या रखता है।", ar: "لا يُسمح له بعد بالدراسة من تلقاء نفسه. فعّله في «ما يمكنه فعله من أجلك» — هناك يُذكر ما يرسله وما يحتفظ به.",
  },
  "err.go": {
    en: "Go and study what I missed", es: "Ve y estudia lo que no supe", fr: "Va étudier ce que j'ai manqué", de: "Geh und studiere, was mir fehlte", pt: "Vai estudar o que me faltou", it: "Vai a studiare ciò che mi è mancato", ja: "答えられなかったことを調べてくる", zh: "去把我答不上来的学回来", hi: "जो मैं चूका उसे पढ़कर आओ", ar: "اذهب وادرس ما فاتني",
  },
  "err.left": {
    en: "a general topic left this device", es: "un tema general salió de este dispositivo", fr: "un sujet général a quitté cet appareil", de: "ein allgemeines Thema hat dieses Gerät verlassen", pt: "um tema geral saiu deste dispositivo", it: "un argomento generale ha lasciato questo dispositivo", ja: "一般的な話題がこの端末から出ました", zh: "一个一般性主题离开了本设备", hi: "एक सामान्य विषय इस डिवाइस से बाहर गया", ar: "غادر موضوع عام هذا الجهاز",
  },
  "err.stayed": {
    en: "nothing left this device", es: "nada salió de este dispositivo", fr: "rien n'a quitté cet appareil", de: "nichts hat dieses Gerät verlassen", pt: "nada saiu deste dispositivo", it: "niente ha lasciato questo dispositivo", ja: "この端末からは何も出ていません", zh: "没有任何内容离开本设备", hi: "इस डिवाइस से कुछ बाहर नहीं गया", ar: "لم يغادر شيء هذا الجهاز",
  },
  "err.redacted": {
    en: "taken out of it", es: "suprimido de ahí", fr: "retiré du texte", de: "daraus entfernt", pt: "retirado dali", it: "rimossi dal testo", ja: "を伏せ字にしました", zh: "处已被去除", hi: "बातें हटाई गईं", ar: "حُذفت منه",
  },
  // The situational half of the ladder (jim/noticed.py). `ntc.free` is the
  // number the whole thing exists to move: of what it handled unattended,
  // how much the free coach carried.
  "ntc.head": {
    en: "What it noticed and handled", es: "Lo que detectó y resolvió", fr: "Ce qu'il a remarqué et traité", de: "Was ihm auffiel und was es geregelt hat", pt: "O que reparou e resolveu", it: "Ciò che ha notato e gestito", ja: "気づいて対応したこと", zh: "它注意到并处理的事", hi: "जो इसने देखा और सँभाला", ar: "ما لاحظه وعالجه",
  },
  "ntc.notallowed": {
    en: "Not allowed to handle what it notices yet. Turn it on in what it may do for you — it says there what it looks at and what it does about it.", es: "Todavía no tiene permiso para ocuparse de lo que detecta. Actívalo en lo que puede hacer por ti: allí dice qué observa y qué hace al respecto.", fr: "Pas encore autorisé à traiter ce qu'il remarque. Activez-le dans ce qu'il peut faire pour vous — il y est dit ce qu'il observe et ce qu'il en fait.", de: "Darf sich noch nicht um das kümmern, was ihm auffällt. Schalte es dort frei, wo steht, worauf es achtet und was es damit tut.", pt: "Ainda não tem permissão para tratar do que repara. Ative-o no que ele pode fazer por si — diz lá o que observa e o que faz a respeito.", it: "Non ha ancora il permesso di occuparsi di ciò che nota. Attivalo in ciò che può fare per te: lì dice cosa osserva e cosa ne fa.", ja: "気づいたことに対処する許可がまだありません。「あなたのためにできること」で有効にしてください。何を見て、どう対応するかが書かれています。", zh: "尚未获准处理它注意到的情况。请在「它可以为你做什么」中开启 — 那里写明了它会关注什么、又会如何应对。", hi: "जो यह नोटिस करता है उसे सँभालने की अनुमति अभी नहीं है। इसे \"यह आपके लिए क्या कर सकता है\" में चालू करें — वहाँ लिखा है कि यह क्या देखता है और क्या करता है।", ar: "لم يُسمح له بعد بمعالجة ما يلاحظه. فعّله في ما يمكنه فعله لك — هناك يُذكر ما يراقبه وما يفعله حياله.",
  },
  "ntc.go": {
    en: "Deal with what you noticed", es: "Ocúpate de lo que detectaste", fr: "Traite ce que tu as remarqué", de: "Kümmere dich um das, was dir aufgefallen ist", pt: "Trata do que reparaste", it: "Occupati di ciò che hai notato", ja: "気づいたことに対応して", zh: "处理你注意到的事", hi: "जो आपने देखा उसे सँभालें", ar: "عالِج ما لاحظته",
  },
  "ntc.free": {
    en: "{n} of {total} handled for nothing by the offline coach", es: "{n} de {total} resueltos sin coste por el coach sin conexión", fr: "{n} sur {total} traités gratuitement par le coach hors ligne", de: "{n} von {total} kostenlos vom Offline-Coach erledigt", pt: "{n} de {total} resolvidos sem custo pelo coach offline", it: "{n} su {total} gestiti gratuitamente dal coach offline", ja: "{total}件中{n}件はオフラインのコーチが無償で対応", zh: "{total} 件中有 {n} 件由离线教练免费处理", hi: "{total} में से {n} ऑफ़लाइन कोच ने बिना किसी लागत के सँभाले", ar: "{n} من {total} عالجها المدرّب دون اتصال بلا تكلفة",
  },
  "ntc.by.coach": {
    en: "the offline coach settled this — no turn spent", es: "lo resolvió el coach sin conexión: no se gastó ningún turno", fr: "réglé par le coach hors ligne — aucun tour dépensé", de: "vom Offline-Coach geklärt — kein Durchgang verbraucht", pt: "resolvido pelo coach offline — nenhum turno gasto", it: "risolto dal coach offline — nessun turno speso", ja: "オフラインのコーチが解決 — 消費なし", zh: "由离线教练解决 — 未消耗任何回合", hi: "ऑफ़लाइन कोच ने सुलझाया — कोई टर्न ख़र्च नहीं", ar: "حلّه المدرّب دون اتصال — دون إنفاق أي جولة",
  },
  "ntc.by.jim": {
    en: "the coach could not, so JIM did — one turn", es: "el coach no pudo, así que lo hizo JIM: un turno", fr: "le coach n'a pas pu, JIM s'en est chargé — un tour", de: "der Coach konnte nicht, also übernahm JIM — ein Durchgang", pt: "o coach não conseguiu, por isso foi o JIM — um turno", it: "il coach non ci è riuscito, l'ha fatto JIM — un turno", ja: "コーチでは対応できずJIMが対応 — 1回分", zh: "教练无法处理，由 JIM 接手 — 一个回合", hi: "कोच नहीं कर सका, इसलिए JIM ने किया — एक टर्न", ar: "لم يستطع المدرّب فتولّاها JIM — جولة واحدة",
  },
  "ntc.waiting": {
    en: "waiting for tomorrow — today's turns are spent", es: "esperando a mañana: los turnos de hoy están agotados", fr: "en attente de demain — les tours du jour sont épuisés", de: "wartet auf morgen — die heutigen Durchgänge sind aufgebraucht", pt: "à espera de amanhã — os turnos de hoje estão gastos", it: "in attesa di domani: i turni di oggi sono esauriti", ja: "明日待ち — 本日分は使い切りました", zh: "等到明天 — 今天的回合已用完", hi: "कल का इंतज़ार — आज के टर्न ख़त्म", ar: "بانتظار الغد — نفدت جولات اليوم",
  },
  "cch.study.head": {
    en: "What JIM should study next", es: "Lo próximo que JIM debería estudiar", fr: "Ce que JIM devrait étudier ensuite", de: "Was JIM als Nächstes studieren sollte", pt: "O que o JIM deve estudar a seguir", it: "Cosa dovrebbe studiare JIM adesso", ja: "JIM が次に学ぶべきこと", zh: "JIM 接下来该学什么", hi: "JIM को आगे क्या पढ़ना चाहिए", ar: "ما الذي ينبغي أن يدرسه JIM تاليًا",
  },
  "cch.study.go": {
    en: "Study it", es: "Estudiarlo", fr: "L'étudier", de: "Studieren", pt: "Estudar", it: "Studialo", ja: "学ばせる", zh: "去学习", hi: "पढ़ो", ar: "ادرسه",
  },
  "cch.study.done": {
    en: "Studied — the offline coach reads it from now on", es: "Estudiado — el coach sin conexión lo consulta desde ahora", fr: "Étudié — le coach hors ligne le consulte désormais", de: "Studiert — der Offline-Coach liest es von jetzt an", pt: "Estudado — o coach offline passa a consultá-lo", it: "Studiato — il coach offline lo consulta d'ora in poi", ja: "学習完了 — 今後はオフラインのコーチが参照します", zh: "已学习——离线教练从现在起可以引用它", hi: "पढ़ लिया — ऑफ़लाइन कोच अब से इसे पढ़ेगा", ar: "تمت الدراسة — سيقرؤه المدرب دون اتصال من الآن فصاعدًا",
  },
  "cch.sub": {
    en: "24/7 across your life", es: "24/7 en toda tu vida", fr: "24h/24, dans toute votre vie", de: "rund um die Uhr, durch dein ganzes Leben", pt: "24/7 em toda a sua vida", it: "24 ore su 24, in tutta la tua vita", ja: "生活のあらゆる場面で、24時間365日", zh: "全天候陪伴你的生活", hi: "आपके जीवन भर, चौबीसों घंटे", ar: "على مدار الساعة في كل جوانب حياتك",
  },
  "cch.area": {
    en: "Area", es: "Área", fr: "Domaine", de: "Bereich", pt: "Área", it: "Area", ja: "分野", zh: "领域", hi: "क्षेत्र", ar: "المجال",
  },
  "cch.mind": {
    en: "What's on your mind?", es: "¿Qué tienes en mente?", fr: "Qu'avez-vous en tête ?", de: "Was beschäftigt dich?", pt: "O que tem em mente?", it: "Cosa hai in mente?", ja: "気になっていることは？", zh: "你在想什么？", hi: "आपके मन में क्या है?", ar: "ما الذي يدور في بالك؟",
  },
  "cch.guidance": {
    en: "{area} · guidance", es: "{area} · orientación", fr: "{area} · conseils", de: "{area} · Anleitung", pt: "{area} · orientação", it: "{area} · guida", ja: "{area} · ガイダンス", zh: "{area} · 指导", hi: "{area} · मार्गदर्शन", ar: "{area} · إرشاد",
  },
  "cch.fallback": {
    en: "⚠ This is the built-in fallback, not", es: "⚠ Este es el recurso integrado, no", fr: "⚠ Ceci est la solution de repli intégrée, pas", de: "⚠ Dies ist der eingebaute Rückfall, nicht", pt: "⚠ Este é o recurso integrado, não", it: "⚠ Questo è il ripiego integrato, non", ja: "⚠ これは内蔵のフォールバックであり、", zh: "⚠ 这是内置的后备回答，而非", hi: "⚠ यह अंतर्निहित फ़ॉलबैक है, न कि", ar: "⚠ هذا هو البديل المدمج، لا",
  },
  "cch.answered": {
    en: "Answered by {who}", es: "Respondido por {who}", fr: "Répondu par {who}", de: "Beantwortet von {who}", pt: "Respondido por {who}", it: "Risposto da {who}", ja: "{who}が回答", zh: "由{who}作答", hi: "{who} ने उत्तर दिया", ar: "أجاب {who}",
  },
  "onb.signwith": {
    en: "Sign {mode} with {provider}", es: "Iniciar {mode} con {provider}", fr: "{mode} avec {provider}", de: "{mode} mit {provider}", pt: "{mode} com {provider}", it: "{mode} con {provider}", ja: "{provider}で{mode}", zh: "用{provider}{mode}", hi: "{provider} से {mode}", ar: "{mode} عبر {provider}",
  },
  "onb.mode.up": {
    en: "up", es: "registro", fr: "S'inscrire", de: "Registrieren", pt: "Registar", it: "Registrati", ja: "登録", zh: "注册", hi: "साइन अप", ar: "إنشاء حساب",
  },
  "onb.mode.in": {
    en: "in", es: "sesión", fr: "Se connecter", de: "Anmelden", pt: "Entrar", it: "Accedi", ja: "サインイン", zh: "登录", hi: "साइन इन", ar: "تسجيل الدخول",
  },
  "onb.serve": {
    en: "python -m jim serve", es: "python -m jim serve", fr: "python -m jim serve", de: "python -m jim serve", pt: "python -m jim serve", it: "python -m jim serve", ja: "python -m jim serve", zh: "python -m jim serve", hi: "python -m jim serve", ar: "python -m jim serve",
  },
  "onb.email.ph": {
    en: "you@example.com", es: "tu@example.com", fr: "vous@example.com", de: "sie@example.com", pt: "voce@example.com", it: "tu@example.com", ja: "you@example.com", zh: "you@example.com", hi: "aap@example.com", ar: "you@example.com",
  },


  // -- ways back that were missing before an undo trail needed them ------
  "aim.goals.remove": {
    en: "Delete the goal",
    es: "Eliminar el objetivo",
    fr: "Supprimer l'objectif",
    de: "Ziel löschen",
    pt: "Eliminar o objetivo",
    it: "Elimina l'obiettivo",
    ja: "目標を削除",
    zh: "删除这个目标",
    hi: "यह लक्ष्य मिटाएँ",
    ar: "احذف الهدف"
  },
  "aim.habits.undid": {
    en: "Untick today",
    es: "Desmarcar hoy",
    fr: "Décocher aujourd'hui",
    de: "Heute abwählen",
    pt: "Desmarcar hoje",
    it: "Togli il segno di oggi",
    ja: "今日の記録を外す",
    zh: "取消今天",
    hi: "आज का निशान हटाएँ",
    ar: "ألغِ علامة اليوم",
  },
  "aim.habits.drop": {
    en: "Drop it",
    es: "Abandonarlo",
    fr: "L'abandonner",
    de: "Aufgeben",
    pt: "Largar",
    it: "Lascialo",
    ja: "やめる",
    zh: "放弃",
    hi: "छोड़ दें",
    ar: "اتركها",
  },
  "chk.remove": {
    en: "Take this check-in back",
    es: "Deshacer este registro",
    fr: "Annuler ce point",
    de: "Diesen Check-in zurücknehmen",
    pt: "Desfazer este registo",
    it: "Annulla questo check-in",
    ja: "このチェックインを取り消す",
    zh: "撤回这次记录",
    hi: "यह चेक-इन वापस लें",
    ar: "تراجع عن هذا التسجيل",
  },
  "jrn.remove": {
    en: "Delete",
    es: "Eliminar",
    fr: "Supprimer",
    de: "Löschen",
    pt: "Eliminar",
    it: "Elimina",
    ja: "削除",
    zh: "删除",
    hi: "मिटाएँ",
    ar: "احذف",
  },

  // -- engaged sessions (jim/engaged.py) ---------------------------------
  // The incantation, not the instruction. "Activate JIM" named the
  // mechanism; this names the moment. The 🜂 beside it stays — the triangle
  // is how the tab is found before the word is read.
  //
  // A borrowed word rather than a translated one: abracadabra is already
  // the same word in every language that has it, so the Latin scripts carry
  // it verbatim and the other four transliterate. Capitals throughout,
  // where the script has them to give.
  // A name, so it is the same in every language — the same way
  // `engaged.title` keeps "JIM" in Latin script below. The amulet drawn
  // beside it (JimMiniOS.tsx) keeps its incantation; the menu says what
  // the product is called.
  "nav.engaged": {
    en: "JIM-mini",
    es: "JIM-mini",
    fr: "JIM-mini",
    de: "JIM-mini",
    pt: "JIM-mini",
    it: "JIM-mini",
    ja: "JIM-mini",
    zh: "JIM-mini",
    hi: "JIM-mini",
    ar: "JIM-mini",
  },
  // The tab is the incantation; the screen it opens is just him. A name,
  // so it is the same in every language — the same way the other rows keep
  // "JIM" in Latin script inside an otherwise translated sentence.
  "engaged.title": {
    en: "JIM", es: "JIM", fr: "JIM", de: "JIM", pt: "JIM",
    it: "JIM", ja: "JIM", zh: "JIM", hi: "JIM", ar: "JIM",
  },
  "engaged.blurb": {
    en: "The coach answers one turn at a time. This stays open until you sign off, can do things for you while it is open, and lists everything it did so you can take it back.",
    es: "El coach responde turno a turno. Esto queda abierto hasta que te despides, puede hacer cosas por ti mientras está abierto y enumera todo lo que hizo para que puedas deshacerlo.",
    fr: "Le coach répond un tour à la fois. Ceci reste ouvert jusqu'à ce que vous vous déconnectiez, peut agir pour vous pendant ce temps, et liste tout ce qu'il a fait pour que vous puissiez l'annuler.",
    de: "Der Coach antwortet Zug um Zug. Dies bleibt offen, bis du dich abmeldest, kann in dieser Zeit Dinge für dich tun und listet alles auf, damit du es zurücknehmen kannst.",
    pt: "O coach responde um turno de cada vez. Isto fica aberto até você se despedir, pode fazer coisas por si enquanto está aberto e lista tudo o que fez para poder desfazer.",
    it: "Il coach risponde un turno alla volta. Questa resta aperta finché non ti congedi, può fare cose per te mentre è aperta ed elenca tutto ciò che ha fatto perché tu possa annullarlo.",
    ja: "コーチは一往復ずつ答えます。こちらはサインオフするまで開いたままで、その間あなたの代わりに操作でき、行ったことをすべて一覧にするので取り消せます。",
    zh: "教练一次回答一轮。这个会话在你签退前一直开着，其间可以替你操作，并列出它做过的每一件事，好让你撤回。",
    hi: "कोच एक बार में एक बारी जवाब देता है। यह तब तक खुला रहता है जब तक आप साइन ऑफ़ न करें, खुले रहने पर आपके लिए काम कर सकता है, और जो किया वह सब सूचीबद्ध करता है ताकि आप वापस ले सकें।",
    ar: "يجيب المدرب دورًا بدور. هذه تبقى مفتوحة حتى تسجّل خروجك، ويمكنها أن تفعل أشياء نيابة عنك ما دامت مفتوحة، وتُدرج كل ما فعلته لتستطيع التراجع عنه.",
  },
  "engaged.reach.title": {
    en: "What it can touch",
    es: "Lo que puede tocar",
    fr: "Ce qu'il peut toucher",
    de: "Was es anfassen kann",
    pt: "O que pode tocar",
    it: "Che cosa può toccare",
    ja: "触れられる範囲",
    zh: "它能碰到什么",
    hi: "यह क्या छू सकता है",
    ar: "ما الذي يمكنه لمسه",
  },
  "engaged.reach.blurb": {
    en: "A written list, not your whole account. Nothing here raises an alarm, moves money, or ends anything — those doors are not on it at all.",
    es: "Una lista escrita, no toda tu cuenta. Nada de esto activa una alarma, mueve dinero ni termina nada: esas puertas no están en la lista.",
    fr: "Une liste écrite, pas tout votre compte. Rien ici ne déclenche d'alarme, ne déplace d'argent ni ne met fin à quoi que ce soit — ces portes n'y figurent pas.",
    de: "Eine geschriebene Liste, nicht dein ganzes Konto. Nichts hier löst einen Alarm aus, bewegt Geld oder beendet etwas — diese Türen stehen gar nicht darauf.",
    pt: "Uma lista escrita, não a sua conta inteira. Nada aqui dispara um alarme, move dinheiro ou termina o que quer que seja — essas portas nem constam.",
    it: "Un elenco scritto, non tutto il tuo account. Niente qui fa scattare un allarme, muove denaro o chiude qualcosa: quelle porte non ci sono affatto.",
    ja: "書かれた一覧であって、アカウント全体ではありません。ここには警報を出すもの、お金を動かすもの、何かを終わらせるものは一つもありません — その扉は載っていません。",
    zh: "这是一份写下来的清单，不是你的整个账户。这里没有任何一项会触发警报、动用钱款或终止什么——那些门根本不在清单上。",
    hi: "यह एक लिखी हुई सूची है, आपका पूरा खाता नहीं। यहाँ कुछ भी अलार्म नहीं बजाता, पैसा नहीं हिलाता, कुछ ख़त्म नहीं करता — वे दरवाज़े इसमें हैं ही नहीं।",
    ar: "قائمة مكتوبة، لا حسابك كله. لا شيء هنا يطلق إنذارًا أو يحرّك مالًا أو ينهي شيئًا — تلك الأبواب ليست عليها أصلًا.",
  },
  "engaged.reach.reads": {
    en: "reads",
    es: "lee",
    fr: "lit",
    de: "liest",
    pt: "lê",
    it: "legge",
    ja: "読む",
    zh: "读取",
    hi: "पढ़ता है",
    ar: "يقرأ",
  },
  "engaged.reach.acts": {
    en: "changes",
    es: "cambia",
    fr: "modifie",
    de: "ändert",
    pt: "altera",
    it: "modifica",
    ja: "変更",
    zh: "更改",
    hi: "बदलता है",
    ar: "يغيّر",
  },
  "engaged.reach.forever": {
    en: "cannot be taken back",
    es: "no se puede deshacer",
    fr: "impossible à annuler",
    de: "nicht zurückzunehmen",
    pt: "não pode ser desfeito",
    it: "non si può annullare",
    ja: "取り消せません",
    zh: "无法撤回",
    hi: "वापस नहीं लिया जा सकता",
    ar: "لا يمكن التراجع عنه",
  },
  // The permits card (jim/permits.py). The `says` sentence under each row
  // comes from the server and is not translated here — it is one sentence per
  // area rather than one per language, and translating the group *names* is
  // what makes the list readable at a glance. The full sentences are the next
  // round's work, and are recorded as such rather than pretended away.
  "permits.title": {
    en: "What JIM can touch", es: "Lo que JIM puede tocar", fr: "Ce que JIM peut toucher", de: "Was JIM anfassen darf", pt: "O que o JIM pode tocar", it: "Cosa può toccare JIM", ja: "JIMが触れられること", zh: "JIM 能触及的部分", hi: "JIM क्या छू सकता है", ar: "ما يمكن لـJIM لمسه",
  },
  "permits.blurb": {
    en: "Tell it out loud what you want on or off and it will do it — for the groups you have switched on here. Each one goes off again the same way.", es: "Dile en voz alta qué quieres activar o desactivar y lo hará, en los grupos que hayas activado aquí. Cada uno se desactiva igual.", fr: "Dites-lui à voix haute ce que vous voulez activer ou désactiver et il le fera — pour les groupes que vous avez activés ici. Chacun se désactive de la même façon.", de: "Sag laut, was an oder aus sein soll, und es erledigt das — für die Gruppen, die du hier eingeschaltet hast. Jede lässt sich genauso wieder ausschalten.", pt: "Diga em voz alta o que quer ligado ou desligado e ele fá-lo — nos grupos que tiver ligado aqui. Cada um desliga-se da mesma forma.", it: "Digli ad alta voce cosa vuoi attivo o disattivo e lo farà, per i gruppi che hai attivato qui. Ognuno si disattiva allo stesso modo.", ja: "何をオンにしたいか、オフにしたいかを声で伝えれば、ここでオンにしたグループについては実行します。同じ手順でいつでもオフにできます。", zh: "把想开或想关的事情说出来，它就会去做 —— 限于你在这里打开的组。每一组都能用同样的方式关掉。", hi: "आप जो चालू या बंद करवाना चाहते हैं, बोलकर बता दें और यह कर देगा — उन समूहों के लिए जिन्हें आपने यहाँ चालू किया है। हर एक इसी तरह बंद भी होता है।", ar: "قل بصوتك ما تريد تشغيله أو إيقافه وسيفعله — في المجموعات التي شغّلتها هنا. وكل واحدة تُطفأ بالطريقة نفسها.",
  },
  "permits.on": {
    en: "On", es: "Activado", fr: "Activé", de: "An", pt: "Ligado", it: "Attivo", ja: "オン", zh: "已开启", hi: "चालू", ar: "مُفعَّل",
  },
  "permits.off": {
    en: "Off", es: "Desactivado", fr: "Désactivé", de: "Aus", pt: "Desligado", it: "Disattivo", ja: "オフ", zh: "已关闭", hi: "बंद", ar: "مُعطَّل",
  },
  "permits.switch.on": {
    en: "Switch on", es: "Activar", fr: "Activer", de: "Einschalten", pt: "Ligar", it: "Attiva", ja: "オンにする", zh: "开启", hi: "चालू करें", ar: "تشغيل",
  },
  "permits.switch.off": {
    en: "Switch off", es: "Desactivar", fr: "Désactiver", de: "Ausschalten", pt: "Desligar", it: "Disattiva", ja: "オフにする", zh: "关闭", hi: "बंद करें", ar: "إيقاف",
  },
  "permits.on.since": {
    en: "You switched this on {when}", es: "Lo activaste el {when}", fr: "Vous l'avez activé le {when}", de: "Du hast das am {when} eingeschaltet", pt: "Ligou isto em {when}", it: "L'hai attivato il {when}", ja: "{when} にオンにしました", zh: "你在 {when} 开启了它", hi: "आपने इसे {when} को चालू किया", ar: "شغّلتَ هذا في {when}",
  },
  "permits.off.since": {
    en: "You switched this off {when}", es: "Lo desactivaste el {when}", fr: "Vous l'avez désactivé le {when}", de: "Du hast das am {when} ausgeschaltet", pt: "Desligou isto em {when}", it: "L'hai disattivato il {when}", ja: "{when} にオフにしました", zh: "你在 {when} 关闭了它", hi: "आपने इसे {when} को बंद किया", ar: "أوقفتَ هذا في {when}",
  },
  "permits.area.your_records": {
    en: "Your own records", es: "Tus propios registros", fr: "Vos propres données", de: "Deine eigenen Aufzeichnungen", pt: "Os seus próprios registos", it: "I tuoi registri", ja: "あなた自身の記録", zh: "你自己的记录", hi: "आपके अपने रिकॉर्ड", ar: "سجلّاتك أنت",
  },
  "permits.area.how_it_speaks": {
    en: "How it speaks to you", es: "Cómo te habla", fr: "Comment il vous parle", de: "Wie es mit dir spricht", pt: "Como fala consigo", it: "Come ti parla", ja: "話しかけ方", zh: "它怎么跟你说话", hi: "यह आपसे कैसे बात करता है", ar: "كيف يخاطبك",
  },
  "permits.area.your_own_normal": {
    en: "Your own normal", es: "Tu propia normalidad", fr: "Votre normale à vous", de: "Dein eigener Normalzustand", pt: "O seu normal", it: "Il tuo normale", ja: "あなたにとっての平常", zh: "你自己的常态", hi: "आपका अपना सामान्य", ar: "ما هو طبيعيّ لك",
  },
  "permits.area.what_it_may_read": {
    en: "What it may read", es: "Lo que puede leer", fr: "Ce qu'il peut lire", de: "Was es lesen darf", pt: "O que pode ler", it: "Cosa può leggere", ja: "読んでよいもの", zh: "它可以读取什么", hi: "यह क्या पढ़ सकता है", ar: "ما يجوز له قراءته",
  },
  "permits.area.what_is_switched_on": {
    en: "What is switched on", es: "Qué está activado", fr: "Ce qui est activé", de: "Was eingeschaltet ist", pt: "O que está ligado", it: "Cosa è attivo", ja: "オンになっている機能", zh: "哪些功能开着", hi: "क्या-क्या चालू है", ar: "ما هو مُفعَّل",
  },
  "permits.area.outside_this_app": {
    en: "Outside this app", es: "Fuera de esta app", fr: "Hors de cette app", de: "Außerhalb dieser App", pt: "Fora desta app", it: "Fuori da questa app", ja: "このアプリの外", zh: "这个应用之外", hi: "इस ऐप के बाहर", ar: "خارج هذا التطبيق",
  },
  // Four groups rendered as their raw keys until a review of the same
  // screen caught it — the rows below are the headings the card always
  // meant to show.
  "permits.area.how_it_looks": {
    en: "How the app looks", es: "Cómo se ve la app", fr: "L'apparence de l'app", de: "Wie die App aussieht", pt: "Como a app fica", it: "L'aspetto dell'app", ja: "アプリの見た目", zh: "应用的外观", hi: "ऐप कैसा दिखता है", ar: "مظهر التطبيق",
  },
  "permits.area.speak_for_you": {
    en: "Speak for you", es: "Hablar por ti", fr: "Parler pour vous", de: "Für dich sprechen", pt: "Falar por si", it: "Parlare per te", ja: "あなたの代わりに話す", zh: "替你发言", hi: "आपकी ओर से बोलना", ar: "التحدث نيابةً عنك",
  },
  "permits.area.excursions_you_ask_for": {
    en: "Excursions you ask for", es: "Excursiones que pides", fr: "Excursions que vous demandez", de: "Ausflüge auf deine Bitte", pt: "Excursões que pede", it: "Escursioni che chiedi", ja: "あなたが頼む知識の外出", zh: "你请求的知识外出", hi: "आपके कहने पर ज्ञान-यात्राएँ", ar: "رحلات معرفية تطلبها أنت",
  },
  "permits.area.study_on_your_own": {
    en: "Study on its own", es: "Estudiar por su cuenta", fr: "Étudier de lui-même", de: "Eigenständig studieren", pt: "Estudar por conta própria", it: "Studiare da solo", ja: "自分で学びに行く", zh: "自行研究", hi: "अपने आप अध्ययन", ar: "الدراسة من تلقاء نفسه",
  },
  "permits.area.handle_what_you_notice": {
    en: "Handle what it notices", es: "Atender lo que nota", fr: "Traiter ce qu'il remarque", de: "Bearbeiten, was ihm auffällt", pt: "Tratar do que nota", it: "Gestire ciò che nota", ja: "気づいたことに対処する", zh: "处理它注意到的事", hi: "जो यह नोटिस करे उसे संभालना", ar: "معالجة ما يلاحظه",
  },

  "engaged.reach.ceilings": {
    en: "It may reach for {steps} things before it has to answer you, and change at most {acts} things in one session.",
    es: "Puede recurrir a {steps} cosas antes de tener que responderte, y cambiar como mucho {acts} cosas en una sesión.",
    fr: "Il peut solliciter {steps} choses avant de devoir vous répondre, et modifier au plus {acts} choses par session.",
    de: "Es darf nach {steps} Dingen greifen, bevor es antworten muss, und höchstens {acts} Dinge pro Sitzung ändern.",
    pt: "Pode recorrer a {steps} coisas antes de ter de responder, e mudar no máximo {acts} coisas numa sessão.",
    it: "Può ricorrere a {steps} cose prima di doverti rispondere, e cambiare al massimo {acts} cose in una sessione.",
    ja: "あなたに答える前に手を伸ばせるのは {steps} 件まで、1 セッションで変更できるのは最大 {acts} 件です。",
    zh: "在回答你之前，它最多可以取用 {steps} 项；一次会话中最多更改 {acts} 项。",
    hi: "आपको जवाब देने से पहले यह {steps} चीज़ों तक पहुँच सकता है, और एक सत्र में ज़्यादा से ज़्यादा {acts} चीज़ें बदल सकता है।",
    ar: "يمكنه أن يمدّ يده إلى {steps} أشياء قبل أن يجيبك، وأن يغيّر {acts} أشياء كحدّ أقصى في الجلسة الواحدة.",
  },
  "engaged.closed.title": {
    en: "Nobody is engaged",
    es: "Nadie está en sesión",
    fr: "Personne n'est en session",
    de: "Niemand ist verbunden",
    pt: "Ninguém está em sessão",
    it: "Nessuno è in sessione",
    ja: "接続していません",
    zh: "当前没有会话",
    hi: "कोई जुड़ा नहीं है",
    ar: "لا أحد في جلسة",
  },
  "engaged.closed.blurb": {
    en: "Open one and it stays open — through closing the app, through tomorrow — until you sign off.",
    es: "Abre una y se queda abierta — aunque cierres la app, aunque pase el día — hasta que te despidas.",
    fr: "Ouvrez-en une et elle reste ouverte — même si vous fermez l'app, même demain — jusqu'à ce que vous vous déconnectiez.",
    de: "Öffne eine, und sie bleibt offen — auch wenn du die App schließt, auch morgen — bis du dich abmeldest.",
    pt: "Abra uma e ela fica aberta — mesmo fechando a app, mesmo amanhã — até você se despedir.",
    it: "Aprine una e resta aperta — anche chiudendo l'app, anche domani — finché non ti congedi.",
    ja: "開けばそのまま — アプリを閉じても、翌日になっても — サインオフするまで開いています。",
    zh: "开一个，它就一直开着——关掉应用也好，到了明天也好——直到你签退。",
    hi: "एक खोलिए और वह खुला रहेगा — ऐप बंद करने पर भी, कल भी — जब तक आप साइन ऑफ़ न करें।",
    ar: "افتح واحدة وتبقى مفتوحة — حتى لو أغلقت التطبيق، وحتى غدًا — إلى أن تسجّل خروجك.",
  },
  "engaged.open.title": {
    en: "Engaged now",
    es: "En sesión ahora",
    fr: "En session",
    de: "Jetzt verbunden",
    pt: "Em sessão agora",
    it: "In sessione ora",
    ja: "接続中です",
    zh: "正在会话",
    hi: "अभी जुड़ा हुआ",
    ar: "في جلسة الآن",
  },
  "engaged.engage": {
    en: "Engage",
    es: "Iniciar sesión",
    fr: "Engager",
    de: "Verbinden",
    pt: "Iniciar sessão",
    it: "Avvia sessione",
    ja: "接続する",
    zh: "开始会话",
    hi: "जुड़ें",
    ar: "ابدأ الجلسة",
  },
  "engaged.you": {
    en: "You",
    es: "Tú",
    fr: "Vous",
    de: "Du",
    pt: "Você",
    it: "Tu",
    ja: "あなた",
    zh: "你",
    hi: "आप",
    ar: "أنت",
  },
  "engaged.jim": {
    en: "JIM",
    es: "JIM",
    fr: "JIM",
    de: "JIM",
    pt: "JIM",
    it: "JIM",
    ja: "JIM",
    zh: "JIM",
    hi: "JIM",
    ar: "JIM",
  },
  "engaged.say": {
    en: "Send it",
    es: "Enviarlo",
    fr: "L'envoyer",
    de: "Absenden",
    pt: "Enviar",
    it: "Invialo",
    ja: "送信する",
    zh: "发送",
    hi: "भेजें",
    ar: "أرسِلها"
  },
  "engaged.say.hint": {
    en: "Tell it what you want — it says what it will change before changing it. You can also send it out for knowledge: ask it to study a topic for the coach — physical or mental health, finance, career, relationships, fitness and nutrition.",
    es: "Dile lo que quieres: dirá qué va a cambiar antes de cambiarlo. También puedes enviarlo por conocimiento: pídele que estudie un tema para el coach — salud física o mental, finanzas, carrera, relaciones, fitness y nutrición.",
    fr: "Dites-lui ce que vous voulez — il annonce ce qu'il va changer avant de le changer. Vous pouvez aussi l'envoyer chercher du savoir : demandez-lui d'étudier un sujet pour le coach — santé physique ou mentale, finances, carrière, relations, forme et nutrition.",
    de: "Sag, was du willst — es nennt, was es ändern wird, bevor es das tut. Du kannst es auch nach Wissen ausschicken: Lass es ein Thema für den Coach studieren — körperliche oder mentale Gesundheit, Finanzen, Karriere, Beziehungen, Fitness und Ernährung.",
    pt: "Diga o que quer — dirá o que vai mudar antes de mudar. Também pode enviá-lo em busca de conhecimento: peça-lhe que estude um tema para o coach — saúde física ou mental, finanças, carreira, relações, fitness e nutrição.",
    it: "Digli che cosa vuoi: dirà che cosa sta per cambiare prima di cambiarlo. Puoi anche mandarlo a cercare conoscenza: chiedigli di studiare un tema per il coach — salute fisica o mentale, finanze, carriera, relazioni, fitness e nutrizione.",
    ja: "望むことを伝えてください。変更する前に、何を変えるかを先に言います。知識を取りに行かせることもできます。コーチのためにテーマを学ばせてください — 身体や心の健康、お金、キャリア、人間関係、フィットネスと栄養。",
    zh: "告诉它你想要什么——它会先说要改什么，然后再改。你也可以派它去获取知识：让它为教练研究一个主题——身体或心理健康、财务、职业、人际关系、健身与营养。",
    hi: "बताइए आप क्या चाहते हैं — बदलने से पहले यह बताएगा कि क्या बदलेगा। आप इसे ज्ञान के लिए भी भेज सकते हैं: कोच के लिए कोई विषय पढ़ने को कहें — शारीरिक या मानसिक स्वास्थ्य, वित्त, करियर, रिश्ते, फ़िटनेस और पोषण।",
    ar: "قل له ما تريد — سيقول ما الذي سيغيّره قبل أن يغيّره. يمكنك أيضًا إرساله بحثًا عن المعرفة: اطلب منه دراسة موضوع للمدرّب — الصحة الجسدية أو النفسية، المال، المسار المهني، العلاقات، اللياقة والتغذية.",
  },
  "engaged.study.yes": {
    en: "Yes — go study it", es: "Sí, ve a estudiarlo", fr: "Oui — va l'étudier", de: "Ja — geh es studieren", pt: "Sim — vai estudá-lo", it: "Sì — vai a studiarlo", ja: "はい — 調べてきて", zh: "好——去研究吧", hi: "हाँ — जाकर पढ़ो", ar: "نعم — اذهب وادرسه",
  },
  "engaged.study.no": {
    en: "No — stay here", es: "No, quédate aquí", fr: "Non — reste ici", de: "Nein — bleib hier", pt: "Não — fica aqui", it: "No — resta qui", ja: "いいえ — ここにいて", zh: "不——留在这里", hi: "नहीं — यहीं रहो", ar: "لا — ابقَ هنا",
  },
  "engaged.step.refused": {
    en: "refused:",
    es: "rechazado:",
    fr: "refusé :",
    de: "abgelehnt:",
    pt: "recusado:",
    it: "rifiutato:",
    ja: "拒否:",
    zh: "已拒绝：",
    hi: "अस्वीकृत:",
    ar: "مرفوض:",
  },
  "engaged.degraded": {
    en: "Answered by {who}, not the model you chose.",
    es: "Respondió {who}, no el modelo que elegiste.",
    fr: "Répondu par {who}, pas le modèle que vous avez choisi.",
    de: "Beantwortet von {who}, nicht dem von dir gewählten Modell.",
    pt: "Respondido por {who}, não pelo modelo que escolheu.",
    it: "Ha risposto {who}, non il modello che hai scelto.",
    ja: "回答したのは {who} で、あなたが選んだモデルではありません。",
    zh: "由 {who} 作答，不是你选的模型。",
    hi: "जवाब {who} ने दिया, आपके चुने मॉडल ने नहीं।",
    ar: "أجاب {who}، لا النموذج الذي اخترته.",
  },
  "engaged.trail.title": {
    en: "What it did",
    es: "Lo que hizo",
    fr: "Ce qu'il a fait",
    de: "Was es getan hat",
    pt: "O que fez",
    it: "Che cosa ha fatto",
    ja: "行ったこと",
    zh: "它做了什么",
    hi: "इसने क्या किया",
    ar: "ما الذي فعله",
  },
  "engaged.trail.blurb": {
    en: "Every change, newest first, with the way back beside it.",
    es: "Cada cambio, del más reciente al más antiguo, con la vuelta atrás al lado.",
    fr: "Chaque changement, du plus récent au plus ancien, avec le retour en arrière à côté.",
    de: "Jede Änderung, neueste zuerst, mit dem Weg zurück daneben.",
    pt: "Cada mudança, da mais recente para a mais antiga, com a volta atrás ao lado.",
    it: "Ogni modifica, dalla più recente, con accanto la via del ritorno.",
    ja: "変更のすべてを新しい順に、取り消す手立てを添えて。",
    zh: "每一处更改，最新的在前，旁边就是回退的路。",
    hi: "हर बदलाव, नया पहले, साथ में वापसी का रास्ता।",
    ar: "كل تغيير، الأحدث أولًا، وبجانبه طريق العودة.",
  },
  "engaged.trail.none": {
    en: "It has not changed anything.",
    es: "No ha cambiado nada.",
    fr: "Il n'a rien changé.",
    de: "Es hat nichts geändert.",
    pt: "Não mudou nada.",
    it: "Non ha cambiato nulla.",
    ja: "何も変更していません。",
    zh: "它没有改动任何东西。",
    hi: "इसने कुछ नहीं बदला।",
    ar: "لم يغيّر شيئًا.",
  },
  "engaged.trail.undo": {
    en: "Take it back",
    es: "Deshacer",
    fr: "Annuler",
    de: "Zurücknehmen",
    pt: "Desfazer",
    it: "Annulla",
    ja: "取り消す",
    zh: "撤回",
    hi: "वापस लें",
    ar: "تراجع",
  },
  "engaged.trail.undone": {
    en: "taken back",
    es: "deshecho",
    fr: "annulé",
    de: "zurückgenommen",
    pt: "desfeito",
    it: "annullato",
    ja: "取り消し済み",
    zh: "已撤回",
    hi: "वापस लिया",
    ar: "تم التراجع",
  },
  "engaged.trail.forever": {
    en: "this one left the app — nothing here can unsay it",
    es: "esto salió de la app: nada aquí puede desdecirlo",
    fr: "celui-ci a quitté l'app — rien ici ne peut le dédire",
    de: "dies hat die App verlassen — nichts hier kann es zurücknehmen",
    pt: "isto saiu da app — nada aqui pode desdizê-lo",
    it: "questo è uscito dall'app: niente qui può ritrattarlo",
    ja: "これはアプリの外に出ました — ここからは取り消せません",
    zh: "这一项已经离开应用——这里没有办法收回",
    hi: "यह ऐप से बाहर चला गया — यहाँ से इसे अनकहा नहीं किया जा सकता",
    ar: "هذا غادر التطبيق — لا شيء هنا يستطيع نقضه",
  },
  "engaged.off.title": {
    en: "Sign off",
    es: "Despedirse",
    fr: "Se déconnecter",
    de: "Abmelden",
    pt: "Despedir-se",
    it: "Congedati",
    ja: "サインオフ",
    zh: "签退",
    hi: "साइन ऑफ़",
    ar: "تسجيل الخروج",
  },
  "engaged.off": {
    en: "Sign off",
    es: "Despedirse",
    fr: "Se déconnecter",
    de: "Abmelden",
    pt: "Despedir-se",
    it: "Congedati",
    ja: "サインオフ",
    zh: "签退",
    hi: "साइन ऑफ़",
    ar: "تسجيل الخروج",
  },
  "engaged.off.blurb": {
    en: "Signing off does not mean going unwatched. What this session was about goes to the offline coach, and anything you name below it keeps an eye on while you are away.",
    es: "Despedirte no significa quedar sin vigilancia. De qué trató esta sesión pasa al coach sin conexión, y lo que nombres abajo lo seguirá vigilando mientras no estés.",
    fr: "Se déconnecter ne veut pas dire ne plus être suivi. Ce dont il était question passe au coach hors ligne, et tout ce que vous nommez ci-dessous, il le surveille en votre absence.",
    de: "Abmelden heißt nicht unbeobachtet. Worum es in dieser Sitzung ging, geht an den Offline-Coach, und was du unten nennst, behält er im Auge, während du weg bist.",
    pt: "Despedir-se não significa ficar sem vigilância. O tema desta sessão passa para o coach offline, e tudo o que nomear abaixo ele fica a vigiar enquanto está fora.",
    it: "Congedarti non significa restare senza qualcuno che guarda. Di che cosa parlava questa sessione passa al coach offline, e quello che scrivi qui sotto lo tiene d'occhio mentre non ci sei.",
    ja: "サインオフしても見守られなくなるわけではありません。このセッションの内容はオフラインのコーチに引き継がれ、下に挙げたことは留守のあいだ見ていてくれます。",
    zh: "签退不等于无人看顾。这次会话的内容会交给离线教练，你在下面写下的事，它会在你不在时替你留意。",
    hi: "साइन ऑफ़ का मतलब बिना निगरानी के रहना नहीं है। यह सत्र किस बारे में था वह ऑफ़लाइन कोच को चला जाता है, और नीचे जो आप लिखेंगे उस पर वह आपकी अनुपस्थिति में नज़र रखेगा।",
    ar: "تسجيل الخروج لا يعني أن يُترك أمرك. ما دارت حوله هذه الجلسة ينتقل إلى المدرب دون اتصال، وكل ما تسمّيه أدناه يبقى تحت عينه في غيابك.",
  },
  "engaged.off.hint": {
    en: "One thing per line — in your own words.",
    es: "Una cosa por línea, con tus propias palabras.",
    fr: "Une chose par ligne, avec vos propres mots.",
    de: "Eine Sache pro Zeile — in deinen eigenen Worten.",
    pt: "Uma coisa por linha — nas suas palavras.",
    it: "Una cosa per riga, con parole tue.",
    ja: "1 行に 1 つ、あなた自身の言葉で。",
    zh: "一行一件，用你自己的话。",
    hi: "हर पंक्ति में एक बात — अपने ही शब्दों में।",
    ar: "شيء واحد في كل سطر — بكلماتك أنت.",
  },
  "engaged.watch.title": {
    en: "Being watched for",
    es: "Bajo vigilancia",
    fr: "Sous surveillance",
    de: "Wird beobachtet",
    pt: "Sob vigilância",
    it: "Sotto osservazione",
    ja: "見守っていること",
    zh: "正在留意",
    hi: "जिस पर नज़र है",
    ar: "تحت المتابعة",
  },
  "engaged.watch.blurb": {
    en: "The offline coach carries these into every answer, and raises them unprompted.",
    es: "El coach sin conexión lleva esto a cada respuesta y lo saca sin que se lo pidan.",
    fr: "Le coach hors ligne les porte dans chaque réponse et les évoque sans qu'on le lui demande.",
    de: "Der Offline-Coach trägt diese in jede Antwort und spricht sie ungefragt an.",
    pt: "O coach offline leva isto para cada resposta e traz o assunto sem lhe pedirem.",
    it: "Il coach offline se li porta in ogni risposta e li tira fuori senza che glielo si chieda.",
    ja: "オフラインのコーチはこれらを毎回の答えに携え、こちらから言わなくても持ち出します。",
    zh: "离线教练会把这些带进每一次回答，并会主动提起。",
    hi: "ऑफ़लाइन कोच इन्हें हर जवाब में साथ रखता है और बिना पूछे उठाता भी है।",
    ar: "يحمل المدرب دون اتصال هذه في كل إجابة، ويطرحها من تلقاء نفسه.",
  },
  "engaged.watch.none": {
    en: "Nothing is on the list.",
    es: "No hay nada en la lista.",
    fr: "Rien sur la liste.",
    de: "Nichts auf der Liste.",
    pt: "Nada na lista.",
    it: "Non c'è niente in elenco.",
    ja: "一覧には何もありません。",
    zh: "清单上没有内容。",
    hi: "सूची में कुछ नहीं है।",
    ar: "لا شيء في القائمة.",
  },
  "engaged.watch.hint": {
    en: "Add something to watch for, then press Enter",
    es: "Añade algo que vigilar y pulsa Intro",
    fr: "Ajoutez quelque chose à surveiller, puis appuyez sur Entrée",
    de: "Etwas zum Beobachten hinzufügen, dann Eingabe drücken",
    pt: "Acrescente algo para vigiar e prima Enter",
    it: "Aggiungi qualcosa da tenere d'occhio, poi premi Invio",
    ja: "見守ってほしいことを足して Enter を押してください",
    zh: "添加一件要留意的事，然后按回车",
    hi: "नज़र रखने के लिए कुछ जोड़ें, फिर Enter दबाएँ",
    ar: "أضف شيئًا لمتابعته ثم اضغط Enter",
  },
  "engaged.watch.stop": {
    en: "Stop watching",
    es: "Dejar de vigilar",
    fr: "Ne plus surveiller",
    de: "Nicht mehr beobachten",
    pt: "Deixar de vigiar",
    it: "Smetti di osservare",
    ja: "見守りをやめる",
    zh: "不再留意",
    hi: "नज़र रखना बंद करें",
    ar: "أوقف المتابعة",
  },
  "refusal.engaged.needs_the_online_model": {
    en: "an engaged session needs the online model \u2014 the offline one can answer you, but it cannot do anything for you. Nothing was changed.",
    es: "una sesión activa necesita el modelo en línea: el sin conexión puede responderte, pero no puede hacer nada por ti. No se cambió nada.",
    fr: "une session engagée a besoin du modèle en ligne — celui hors ligne peut vous répondre, mais il ne peut rien faire pour vous. Rien n'a été modifié.",
    de: "eine laufende Sitzung braucht das Online-Modell — das Offline-Modell kann dir antworten, aber nichts für dich tun. Es wurde nichts geändert.",
    pt: "uma sessão em curso precisa do modelo online — o offline pode responder-lhe, mas não pode fazer nada por si. Nada foi alterado.",
    it: "una sessione in corso ha bisogno del modello online: quello offline può risponderti, ma non può fare nulla per te. Non è stato cambiato nulla.",
    ja: "接続中のセッションにはオンラインのモデルが必要です — オフラインのモデルは答えられますが、あなたの代わりに何かをすることはできません。何も変更されていません。",
    zh: "会话中的它需要在线模型——离线的那个可以回答你，但不能替你做事。什么也没有改动。",
    hi: "चालू सत्र के लिए ऑनलाइन मॉडल चाहिए — ऑफ़लाइन वाला जवाब दे सकता है, पर आपके लिए कुछ कर नहीं सकता। कुछ भी नहीं बदला।",
    ar: "تحتاج الجلسة القائمة إلى النموذج المتصل — أما غير المتصل فيستطيع أن يجيبك، لكنه لا يستطيع أن يفعل شيئًا نيابة عنك. لم يتغيّر شيء.",
  },
  "refusal.engaged.too_many_steps": {
    en: "It kept reaching for things and never answered. Ask again, more narrowly.",
    es: "Siguió recurriendo a cosas y nunca respondió. Pregunta otra vez, más concretamente.",
    fr: "Il n'a cessé de solliciter des choses sans jamais répondre. Redemandez, plus précisément.",
    de: "Es griff immer weiter nach Dingen und antwortete nie. Frag noch einmal, enger gefasst.",
    pt: "Continuou a recorrer a coisas e nunca respondeu. Pergunte outra vez, de forma mais restrita.",
    it: "Ha continuato a ricorrere a cose senza mai rispondere. Richiedi, in modo più circoscritto.",
    ja: "あれこれ手を伸ばし続けて、結局答えませんでした。もう少し絞ってもう一度どうぞ。",
    zh: "它一直在取用东西，却始终没有回答。请把问题问得更窄一些再试。",
    hi: "यह चीज़ों तक पहुँचता रहा और जवाब कभी नहीं दिया। थोड़ा संकीर्ण करके फिर पूछिए।",
    ar: "ظلّ يمدّ يده إلى الأشياء ولم يجب قط. اسأل مرة أخرى بصيغة أضيق.",
  },
  "refusal.engaged.acted_enough": {
    en: "This session has changed enough for one sitting. Sign off and start another.",
    es: "Esta sesión ya ha cambiado bastante de una sentada. Despídete y empieza otra.",
    fr: "Cette session a assez changé de choses d'un coup. Déconnectez-vous et recommencez-en une.",
    de: "Diese Sitzung hat für einmal genug geändert. Meld dich ab und beginn eine neue.",
    pt: "Esta sessão já mudou o suficiente de uma vez. Despeça-se e comece outra.",
    it: "Questa sessione ha cambiato abbastanza per una volta. Congedati e aprine un'altra.",
    ja: "このセッションは一度に十分な変更を行いました。サインオフして、別のセッションを始めてください。",
    zh: "这次会话一口气改得够多了。请先签退，再开一个。",
    hi: "इस सत्र में एक बार के लिए काफ़ी बदल चुका है। साइन ऑफ़ करके नया शुरू कीजिए।",
    ar: "غيّرت هذه الجلسة ما يكفي لجلسة واحدة. سجّل خروجك وابدأ أخرى.",
  },
  // The watch surface (`screens/Watch.tsx`): thirty-six faces and the
  // words on them. Wordings the phones already carry are copied from
  // their tables verbatim, so the wrist and the pocket say one thing.
  "nav.watch": {
    en: "Watch",
    es: "Reloj",
    fr: "Montre",
    de: "Uhr",
    pt: "Relógio",
    it: "Orologio",
    ja: "ウォッチ",
    zh: "手表",
    hi: "घड़ी",
    ar: "الساعة",
  },
  "w.title": {
    en: "The watch",
    es: "El reloj",
    fr: "La montre",
    de: "Die Uhr",
    pt: "O relógio",
    it: "L'orologio",
    ja: "ウォッチ画面",
    zh: "手表界面",
    hi: "घड़ी का तल",
    ar: "واجهة الساعة",
  },
  "w.signin": {
    en: "Sign in on the phone first — this face reads your account.",
    es: "Inicia sesión primero en el teléfono: esta cara lee tu cuenta.",
    fr: "Connectez-vous d'abord sur le téléphone — cette face lit votre compte.",
    de: "Melde dich zuerst am Telefon an — dieses Zifferblatt liest dein Konto.",
    pt: "Inicie sessão primeiro no telemóvel — este mostrador lê a sua conta.",
    it: "Accedi prima dal telefono: questo quadrante legge il tuo account.",
    ja: "先に電話でサインインしてください — この画面はアカウントを読み取ります。",
    zh: "请先在手机上登录 — 此表盘会读取你的账户。",
    hi: "पहले फ़ोन पर साइन इन करें — यह फलक आपका खाता पढ़ता है।",
    ar: "سجّل الدخول من الهاتف أولًا — هذه الواجهة تقرأ حسابك.",
  },
  "w.leave": {
    en: "Close the watch",
    es: "Cerrar el reloj",
    fr: "Fermer la montre",
    de: "Die Uhr schließen",
    pt: "Fechar o relógio",
    it: "Chiudi l'orologio",
    ja: "ウォッチを閉じる",
    zh: "关闭手表",
    hi: "घड़ी बंद करें",
    ar: "إغلاق الساعة",
  },
  "w.yes": {
    en: "Yes",
    es: "Sí",
    fr: "Oui",
    de: "Ja",
    pt: "Sim",
    it: "Sì",
    ja: "はい",
    zh: "是",
    hi: "हाँ",
    ar: "نعم",
  },
  "w.no": {
    en: "No",
    es: "No",
    fr: "Non",
    de: "Nein",
    pt: "Não",
    it: "No",
    ja: "いいえ",
    zh: "否",
    hi: "नहीं",
    ar: "لا",
  },
  "w.on": {
    en: "On",
    es: "Activado",
    fr: "Activé",
    de: "An",
    pt: "Ativado",
    it: "Attivo",
    ja: "オン",
    zh: "已开启",
    hi: "चालू",
    ar: "مفعّل",
  },
  "w.off": {
    en: "Off",
    es: "Desactivado",
    fr: "Désactivé",
    de: "Aus",
    pt: "Desativado",
    it: "Spento",
    ja: "オフ",
    zh: "已关闭",
    hi: "बंद",
    ar: "متوقف",
  },
  "w.prev": {
    en: "Previous face",
    es: "Cara anterior",
    fr: "Face précédente",
    de: "Vorheriges Zifferblatt",
    pt: "Mostrador anterior",
    it: "Quadrante precedente",
    ja: "前の画面",
    zh: "上一个表盘",
    hi: "पिछला फलक",
    ar: "الواجهة السابقة",
  },
  "w.next": {
    en: "Next face",
    es: "Cara siguiente",
    fr: "Face suivante",
    de: "Nächstes Zifferblatt",
    pt: "Mostrador seguinte",
    it: "Quadrante successivo",
    ja: "次の画面",
    zh: "下一个表盘",
    hi: "अगला फलक",
    ar: "الواجهة التالية",
  },
  "w.all": {
    en: "All faces",
    es: "Todas las caras",
    fr: "Toutes les faces",
    de: "Alle Zifferblätter",
    pt: "Todos os mostradores",
    it: "Tutti i quadranti",
    ja: "すべての画面",
    zh: "全部表盘",
    hi: "सभी फलक",
    ar: "كل الواجهات",
  },
  "w.provisional": {
    en: "still learning",
    es: "aún aprendiendo",
    fr: "apprend encore",
    de: "lernt noch",
    pt: "ainda a aprender",
    it: "sta ancora imparando",
    ja: "まだ学習中",
    zh: "仍在学习",
    hi: "अभी सीख रहा है",
    ar: "لا يزال يتعلم",
  },
  "w.f.home": {
    en: "Home",
    es: "Inicio",
    fr: "Accueil",
    de: "Start",
    pt: "Início",
    it: "Home",
    ja: "ホーム",
    zh: "主页",
    hi: "होम",
    ar: "الرئيسية",
  },
  "w.f.talk": {
    en: "Talk",
    es: "Hablar",
    fr: "Parler",
    de: "Sprechen",
    pt: "Falar",
    it: "Parla",
    ja: "トーク",
    zh: "交谈",
    hi: "बात करें",
    ar: "تحدث",
  },
  "w.f.voice": {
    en: "Voice",
    es: "Voz",
    fr: "Voix",
    de: "Stimme",
    pt: "Voz",
    it: "Voce",
    ja: "音声",
    zh: "语音",
    hi: "आवाज़",
    ar: "الصوت",
  },
  "w.f.health": {
    en: "Health",
    es: "Salud",
    fr: "Santé",
    de: "Gesundheit",
    pt: "Saúde",
    it: "Salute",
    ja: "ヘルス",
    zh: "健康",
    hi: "स्वास्थ्य",
    ar: "الصحة",
  },
  "w.f.heart": {
    en: "Heart",
    es: "Corazón",
    fr: "Cœur",
    de: "Herz",
    pt: "Coração",
    it: "Cuore",
    ja: "心拍",
    zh: "心率",
    hi: "हृदय",
    ar: "القلب",
  },
  "w.f.rings": {
    en: "Rings",
    es: "Anillos",
    fr: "Anneaux",
    de: "Ringe",
    pt: "Anéis",
    it: "Anelli",
    ja: "リング",
    zh: "圆环",
    hi: "रिंग्स",
    ar: "الحلقات",
  },
  "w.f.briefing": {
    en: "Briefing",
    es: "Resumen",
    fr: "Briefing",
    de: "Briefing",
    pt: "Resumo",
    it: "Briefing",
    ja: "ブリーフィング",
    zh: "简报",
    hi: "ब्रीफ़िंग",
    ar: "الموجز",
  },
  "w.f.streak": {
    en: "Streak",
    es: "Racha",
    fr: "Série",
    de: "Serie",
    pt: "Sequência",
    it: "Serie",
    ja: "連続記録",
    zh: "连续天数",
    hi: "सिलसिला",
    ar: "السلسلة",
  },
  "w.f.checkin": {
    en: "Check-in",
    es: "Registro",
    fr: "Bilan",
    de: "Check-in",
    pt: "Check-in",
    it: "Check-in",
    ja: "チェックイン",
    zh: "签到",
    hi: "चेक-इन",
    ar: "تسجيل الحالة",
  },
  "w.f.insight": {
    en: "Insight",
    es: "Percepción",
    fr: "Aperçu",
    de: "Einblick",
    pt: "Perceção",
    it: "Intuizione",
    ja: "インサイト",
    zh: "洞察",
    hi: "अंतर्दृष्टि",
    ar: "بصيرة",
  },
  "w.f.monitoring": {
    en: "Monitoring",
    es: "Vigilancia",
    fr: "Surveillance",
    de: "Überwachung",
    pt: "Vigilância",
    it: "Monitoraggio",
    ja: "モニタリング",
    zh: "监测",
    hi: "निगरानी",
    ar: "المراقبة",
  },
  "w.f.foresight": {
    en: "Foresight",
    es: "Previsión",
    fr: "Prévoyance",
    de: "Voraussicht",
    pt: "Previsão",
    it: "Previsione",
    ja: "先読み",
    zh: "预见",
    hi: "पूर्वानुमान",
    ar: "الاستشراف",
  },
  "w.f.emergency": {
    en: "Emergency",
    es: "Emergencia",
    fr: "Urgence",
    de: "Notfall",
    pt: "Emergência",
    it: "Emergenza",
    ja: "緊急",
    zh: "紧急",
    hi: "आपातकाल",
    ar: "الطوارئ",
  },
  "w.f.cpr": {
    en: "CPR",
    es: "RCP",
    fr: "RCP",
    de: "HLW",
    pt: "RCP",
    it: "RCP",
    ja: "心肺蘇生",
    zh: "心肺复苏",
    hi: "सीपीआर",
    ar: "الإنعاش القلبي",
  },
  "w.f.medicalid": {
    en: "Medical ID",
    es: "Identificación médica",
    fr: "Fiche médicale",
    de: "Notfallpass",
    pt: "Identificação médica",
    it: "Scheda medica",
    ja: "メディカル ID",
    zh: "医疗卡",
    hi: "मेडिकल आईडी",
    ar: "البطاقة الطبية",
  },
  "w.f.sensitivity": {
    en: "Sensitivity",
    es: "Sensibilidad",
    fr: "Sensibilité",
    de: "Empfindlichkeit",
    pt: "Sensibilidade",
    it: "Sensibilità",
    ja: "感度",
    zh: "灵敏度",
    hi: "संवेदनशीलता",
    ar: "الحساسية",
  },
  "w.f.ambient": {
    en: "Ambient",
    es: "Ambiente",
    fr: "Ambiant",
    de: "Ambient",
    pt: "Ambiente",
    it: "Ambientale",
    ja: "アンビエント",
    zh: "环境感知",
    hi: "परिवेश",
    ar: "محيطي",
  },
  "w.f.companion": {
    en: "Companion",
    es: "Compañía",
    fr: "Compagnon",
    de: "Begleiter",
    pt: "Companhia",
    it: "Compagno",
    ja: "そばにいる",
    zh: "陪伴",
    hi: "साथी",
    ar: "رفيق",
  },
  "w.f.notifications": {
    en: "Notifications",
    es: "Notificaciones",
    fr: "Notifications",
    de: "Mitteilungen",
    pt: "Notificações",
    it: "Notifiche",
    ja: "通知",
    zh: "通知",
    hi: "सूचनाएँ",
    ar: "الإشعارات",
  },
  "w.f.devices": {
    en: "Devices",
    es: "Dispositivos",
    fr: "Appareils",
    de: "Geräte",
    pt: "Dispositivos",
    it: "Dispositivi",
    ja: "デバイス",
    zh: "设备",
    hi: "डिवाइस",
    ar: "الأجهزة",
  },
  "w.f.guardian": {
    en: "Guardian",
    es: "Guardián",
    fr: "Gardien",
    de: "Wächter",
    pt: "Guardião",
    it: "Guardiano",
    ja: "ガーディアン",
    zh: "守护者",
    hi: "अभिभावक",
    ar: "الحارس",
  },
  "w.f.settings": {
    en: "Settings",
    es: "Ajustes",
    fr: "Réglages",
    de: "Einstellungen",
    pt: "Definições",
    it: "Impostazioni",
    ja: "設定",
    zh: "设置",
    hi: "सेटिंग्स",
    ar: "الإعدادات",
  },
  "w.f.breathe": {
    en: "Breathe",
    es: "Respira",
    fr: "Respirez",
    de: "Atme",
    pt: "Respire",
    it: "Respira",
    ja: "呼吸",
    zh: "呼吸",
    hi: "साँस",
    ar: "تنفّس",
  },
  "w.f.feedback": {
    en: "Feedback",
    es: "Valoración",
    fr: "Retour",
    de: "Feedback",
    pt: "Feedback",
    it: "Feedback",
    ja: "フィードバック",
    zh: "反馈",
    hi: "प्रतिक्रिया",
    ar: "الملاحظات",
  },
  "w.f.journal": {
    en: "Journal",
    es: "Diario",
    fr: "Journal",
    de: "Tagebuch",
    pt: "Diário",
    it: "Diario",
    ja: "日記",
    zh: "日志",
    hi: "डायरी",
    ar: "اليوميات",
  },
  "w.f.coach": {
    en: "Coach",
    es: "Coach",
    fr: "Coach",
    de: "Coach",
    pt: "Coach",
    it: "Coach",
    ja: "コーチ",
    zh: "教练",
    hi: "कोच",
    ar: "مدرب",
  },
  "w.f.baseline": {
    en: "Baseline",
    es: "Línea base",
    fr: "Référence",
    de: "Basislinie",
    pt: "Linha de base",
    it: "Linea di base",
    ja: "ベースライン",
    zh: "基线",
    hi: "आधार रेखा",
    ar: "خط الأساس",
  },
  "w.f.sources": {
    en: "Sources",
    es: "Fuentes",
    fr: "Sources",
    de: "Quellen",
    pt: "Fontes",
    it: "Fonti",
    ja: "出どころ",
    zh: "来源",
    hi: "स्रोत",
    ar: "المصادر",
  },
  "w.f.privacy": {
    en: "Privacy",
    es: "Privacidad",
    fr: "Confidentialité",
    de: "Privatsphäre",
    pt: "Privacidade",
    it: "Privacy",
    ja: "プライバシー",
    zh: "隐私",
    hi: "गोपनीयता",
    ar: "الخصوصية",
  },
  "w.f.handoff": {
    en: "Handoff",
    es: "Traspaso",
    fr: "Relais",
    de: "Übergabe",
    pt: "Passagem",
    it: "Passaggio",
    ja: "引き継ぎ",
    zh: "交接",
    hi: "हस्तांतरण",
    ar: "تسليم",
  },
  "w.f.offline": {
    en: "Offline",
    es: "Sin conexión",
    fr: "Hors ligne",
    de: "Offline",
    pt: "Offline",
    it: "Offline",
    ja: "オフライン",
    zh: "离线",
    hi: "ऑफ़लाइन",
    ar: "دون اتصال",
  },
  "w.f.conditions": {
    en: "Conditions",
    es: "Afecciones",
    fr: "Pathologies",
    de: "Erkrankungen",
    pt: "Condições",
    it: "Patologie",
    ja: "既往症",
    zh: "健康状况",
    hi: "स्थितियाँ",
    ar: "الحالات الصحية",
  },
  "w.f.style": {
    en: "Style",
    es: "Estilo",
    fr: "Style",
    de: "Stil",
    pt: "Estilo",
    it: "Stile",
    ja: "スタイル",
    zh: "风格",
    hi: "शैली",
    ar: "الأسلوب",
  },
  "w.f.history": {
    en: "History",
    es: "Historial",
    fr: "Historique",
    de: "Verlauf",
    pt: "Histórico",
    it: "Cronologia",
    ja: "履歴",
    zh: "历史",
    hi: "इतिहास",
    ar: "السجل",
  },
  "w.f.family": {
    en: "Family",
    es: "Familia",
    fr: "Famille",
    de: "Familie",
    pt: "Família",
    it: "Famiglia",
    ja: "家族",
    zh: "家庭",
    hi: "परिवार",
    ar: "العائلة",
  },
  "w.f.agents": {
    en: "Agents",
    es: "Agentes",
    fr: "Agents",
    de: "Agenten",
    pt: "Agentes",
    it: "Agenti",
    ja: "エージェント",
    zh: "智能体",
    hi: "एजेंट",
    ar: "الوكلاء",
  },
  "w.home.morning": {
    en: "Good morning",
    es: "Buenos días",
    fr: "Bonjour",
    de: "Guten Morgen",
    pt: "Bom dia",
    it: "Buongiorno",
    ja: "おはようございます",
    zh: "早上好",
    hi: "सुप्रभात",
    ar: "صباح الخير",
  },
  "w.home.afternoon": {
    en: "Good afternoon",
    es: "Buenas tardes",
    fr: "Bon après-midi",
    de: "Guten Tag",
    pt: "Boa tarde",
    it: "Buon pomeriggio",
    ja: "こんにちは",
    zh: "下午好",
    hi: "नमस्ते",
    ar: "نهارك سعيد",
  },
  "w.home.evening": {
    en: "Good evening",
    es: "Buenas noches",
    fr: "Bonsoir",
    de: "Guten Abend",
    pt: "Boa noite",
    it: "Buonasera",
    ja: "こんばんは",
    zh: "晚上好",
    hi: "शुभ संध्या",
    ar: "مساء الخير",
  },
  "w.home.you": {
    en: "You",
    es: "Tú",
    fr: "Vous",
    de: "Du",
    pt: "Você",
    it: "Tu",
    ja: "あなた",
    zh: "你",
    hi: "आप",
    ar: "أنت",
  },
  "w.home.talk": {
    en: "Talk to JIM",
    es: "Habla con JIM",
    fr: "Parler à JIM",
    de: "Mit JIM sprechen",
    pt: "Falar com o JIM",
    it: "Parla con JIM",
    ja: "JIMと話す",
    zh: "与JIM交谈",
    hi: "JIM से बात करें",
    ar: "تحدث إلى JIM",
  },
  "w.talk.how": {
    en: "What's on your mind?",
    es: "¿Qué te ronda la cabeza?",
    fr: "Qu'avez-vous en tête ?",
    de: "Was beschäftigt dich?",
    pt: "O que o preocupa?",
    it: "Cosa ti passa per la testa?",
    ja: "何を考えていますか？",
    zh: "你在想什么？",
    hi: "आपके मन में क्या है?",
    ar: "بمَ تفكر؟",
  },
  "w.talk.ph": {
    en: "Say it here",
    es: "Dilo aquí",
    fr: "Dites-le ici",
    de: "Sag es hier",
    pt: "Diga-o aqui",
    it: "Dillo qui",
    ja: "ここに書いてください",
    zh: "在这里说",
    hi: "यहाँ कहें",
    ar: "قله هنا",
  },
  "w.talk.send": {
    en: "Send",
    es: "Enviar",
    fr: "Envoyer",
    de: "Senden",
    pt: "Enviar",
    it: "Invia",
    ja: "送信",
    zh: "发送",
    hi: "भेजें",
    ar: "إرسال",
  },
  "w.voice.listening": {
    en: "Listening…",
    es: "Escuchando…",
    fr: "À l'écoute…",
    de: "Höre zu…",
    pt: "A ouvir…",
    it: "In ascolto…",
    ja: "聞いています…",
    zh: "正在聆听…",
    hi: "सुन रहा है…",
    ar: "يستمع…",
  },
  "w.voice.tap": {
    en: "Tap and speak",
    es: "Toca y habla",
    fr: "Touchez et parlez",
    de: "Tippen und sprechen",
    pt: "Toque e fale",
    it: "Tocca e parla",
    ja: "タップして話す",
    zh: "点按并说话",
    hi: "टैप करके बोलें",
    ar: "انقر وتكلم",
  },
  "w.voice.stop": {
    en: "Stop",
    es: "Detener",
    fr: "Arrêter",
    de: "Beenden",
    pt: "Parar",
    it: "Ferma",
    ja: "やめる",
    zh: "停止",
    hi: "रोकें",
    ar: "إيقاف",
  },
  "w.voice.speak": {
    en: "Speak",
    es: "Hablar",
    fr: "Parler",
    de: "Sprechen",
    pt: "Falar",
    it: "Parla",
    ja: "話す",
    zh: "说话",
    hi: "बोलें",
    ar: "تكلم",
  },
  "w.health.none": {
    en: "No readings yet — connect a source on the phone.",
    es: "Aún no hay lecturas: conecta una fuente en el teléfono.",
    fr: "Pas encore de mesures — connectez une source sur le téléphone.",
    de: "Noch keine Messwerte — verbinde eine Quelle am Telefon.",
    pt: "Ainda sem leituras — ligue uma fonte no telemóvel.",
    it: "Ancora nessuna lettura: collega una fonte dal telefono.",
    ja: "まだ計測値がありません — 電話でソースを接続してください。",
    zh: "还没有读数 — 请在手机上连接数据来源。",
    hi: "अभी कोई रीडिंग नहीं — फ़ोन पर एक स्रोत जोड़ें।",
    ar: "لا قراءات بعد — اربط مصدرًا من الهاتف.",
  },
  "w.heart.resting": {
    en: "resting heart rate",
    es: "frecuencia cardiaca en reposo",
    fr: "fréquence cardiaque au repos",
    de: "Ruhepuls",
    pt: "frequência cardíaca em repouso",
    it: "frequenza cardiaca a riposo",
    ja: "安静時心拍数",
    zh: "静息心率",
    hi: "विश्राम हृदय गति",
    ar: "معدل نبض القلب أثناء الراحة",
  },
  "w.rings.none": {
    en: "No goals yet — set one on the phone.",
    es: "Aún no hay metas: fija una en el teléfono.",
    fr: "Pas encore d'objectifs — fixez-en un sur le téléphone.",
    de: "Noch keine Ziele — lege eins am Telefon fest.",
    pt: "Ainda sem metas — defina uma no telemóvel.",
    it: "Ancora nessun obiettivo: fissane uno dal telefono.",
    ja: "まだ目標がありません — 電話で設定してください。",
    zh: "还没有目标 — 请在手机上设定一个。",
    hi: "अभी कोई लक्ष्य नहीं — फ़ोन पर एक तय करें।",
    ar: "لا أهداف بعد — حدد هدفًا من الهاتف.",
  },
  "w.brief.none": {
    en: "Nothing to brief yet.",
    es: "Todavía nada que resumir.",
    fr: "Rien à résumer pour l'instant.",
    de: "Noch nichts zu berichten.",
    pt: "Ainda nada para resumir.",
    it: "Ancora niente da riassumere.",
    ja: "まだ伝えることはありません。",
    zh: "暂时没有可简报的内容。",
    hi: "अभी बताने को कुछ नहीं।",
    ar: "لا شيء يُلخّص بعد.",
  },
  "w.streak.days": {
    en: "days in a row",
    es: "días seguidos",
    fr: "jours d'affilée",
    de: "Tage in Folge",
    pt: "dias seguidos",
    it: "giorni di fila",
    ja: "日連続",
    zh: "天连续",
    hi: "दिन लगातार",
    ar: "أيام متتالية",
  },
  "w.ci.mood": {
    en: "Mood",
    es: "Ánimo",
    fr: "Humeur",
    de: "Stimmung",
    pt: "Humor",
    it: "Umore",
    ja: "気分",
    zh: "心情",
    hi: "मनोदशा",
    ar: "المزاج",
  },
  "w.ci.energy": {
    en: "Energy",
    es: "Energía",
    fr: "Énergie",
    de: "Energie",
    pt: "Energia",
    it: "Energia",
    ja: "エネルギー",
    zh: "精力",
    hi: "ऊर्जा",
    ar: "الطاقة",
  },
  "w.ci.log": {
    en: "Log it",
    es: "Registrarlo",
    fr: "L'enregistrer",
    de: "Eintragen",
    pt: "Registar",
    it: "Registralo",
    ja: "記録する",
    zh: "记录",
    hi: "दर्ज करें",
    ar: "سجّله",
  },
  "w.ci.done": {
    en: "Logged — thank you.",
    es: "Registrado, gracias.",
    fr: "Enregistré — merci.",
    de: "Eingetragen — danke.",
    pt: "Registado — obrigado.",
    it: "Registrato — grazie.",
    ja: "記録しました — ありがとうございます。",
    zh: "已记录 — 谢谢。",
    hi: "दर्ज हो गया — धन्यवाद।",
    ar: "سُجّل — شكرًا لك.",
  },
  "w.insight.none": {
    en: "No insight yet — it grows from your check-ins.",
    es: "Aún no hay percepciones: crecen con tus registros.",
    fr: "Pas encore d'aperçu — il naît de vos bilans.",
    de: "Noch kein Einblick — er wächst aus deinen Check-ins.",
    pt: "Ainda sem perceções — crescem com os seus check-ins.",
    it: "Ancora nessuna intuizione: nasce dai tuoi check-in.",
    ja: "まだインサイトはありません — チェックインから育ちます。",
    zh: "还没有洞察 — 它会从你的签到中生长。",
    hi: "अभी कोई अंतर्दृष्टि नहीं — यह आपके चेक-इन से बनती है।",
    ar: "لا بصيرة بعد — تنمو من تسجيلات حالتك.",
  },
  "w.mon.quiet": {
    en: "All quiet — nothing needs you.",
    es: "Todo en calma: nada te necesita.",
    fr: "Tout est calme — rien ne vous demande.",
    de: "Alles ruhig — nichts braucht dich.",
    pt: "Tudo calmo — nada precisa de si.",
    it: "Tutto tranquillo: niente ha bisogno di te.",
    ja: "すべて平穏です — 対応は不要です。",
    zh: "一切平静 — 无需处理。",
    hi: "सब शांत है — किसी को आपकी ज़रूरत नहीं।",
    ar: "كل شيء هادئ — لا شيء يحتاجك.",
  },
  "w.mon.ok": {
    en: "I'm okay",
    es: "Estoy bien",
    fr: "Ça va",
    de: "Mir geht es gut",
    pt: "Estou bem",
    it: "Sto bene",
    ja: "大丈夫です",
    zh: "我没事",
    hi: "मैं ठीक हूँ",
    ar: "أنا بخير",
  },
  "w.mon.told": {
    en: "Told the Guardian.",
    es: "Se lo dije al Guardián.",
    fr: "Le Gardien est prévenu.",
    de: "Dem Wächter gesagt.",
    pt: "O Guardião foi avisado.",
    it: "Detto al Guardiano.",
    ja: "ガーディアンに伝えました。",
    zh: "已告知守护者。",
    hi: "अभिभावक को बता दिया।",
    ar: "أُخبر الحارس.",
  },
  "w.fore.learning": {
    en: "The baseline is still learning — a few more days sharpen it.",
    es: "La línea base aún aprende: unos días más la afinan.",
    fr: "La référence apprend encore — quelques jours de plus l'affineront.",
    de: "Die Basislinie lernt noch — ein paar Tage mehr schärfen sie.",
    pt: "A linha de base ainda aprende — mais uns dias afinam-na.",
    it: "La linea di base sta ancora imparando: qualche giorno in più la affina.",
    ja: "ベースラインはまだ学習中です — あと数日で精度が上がります。",
    zh: "基线仍在学习 — 再过几天会更精准。",
    hi: "आधार रेखा अभी सीख रही है — कुछ और दिन इसे बेहतर बनाएँगे।",
    ar: "خط الأساس لا يزال يتعلم — بضعة أيام أخرى تصقله.",
  },
  "w.fore.steady": {
    en: "Nothing ahead looks unusual.",
    es: "Nada por delante parece inusual.",
    fr: "Rien d'inhabituel à l'horizon.",
    de: "Nichts Ungewöhnliches in Sicht.",
    pt: "Nada à frente parece invulgar.",
    it: "Niente di insolito all'orizzonte.",
    ja: "この先に異常は見えません。",
    zh: "接下来没有异常迹象。",
    hi: "आगे कुछ भी असामान्य नहीं दिखता।",
    ar: "لا شيء غير معتاد في الأفق.",
  },
  "w.fore.breathe": {
    en: "Take a breath",
    es: "Respira hondo",
    fr: "Respirez un instant",
    de: "Atme durch",
    pt: "Respire fundo",
    it: "Fai un respiro",
    ja: "ひと呼吸",
    zh: "深呼吸一下",
    hi: "एक साँस लें",
    ar: "خذ نفسًا",
  },
  "w.em.call": {
    en: "Call emergency services",
    es: "Llamar a emergencias",
    fr: "Appeler les secours",
    de: "Notruf anrufen",
    pt: "Ligar para emergências",
    it: "Chiama i soccorsi",
    ja: "救急に電話する",
    zh: "拨打急救电话",
    hi: "आपातकालीन सेवा को कॉल करें",
    ar: "الاتصال بخدمات الطوارئ",
  },
  "w.em.device": {
    en: "This device places the call — JIM cannot dial.",
    es: "La llamada la hace este dispositivo: JIM no puede marcar.",
    fr: "C'est cet appareil qui passe l'appel — JIM ne peut pas composer.",
    de: "Dieses Gerät führt den Anruf aus — JIM kann nicht wählen.",
    pt: "É este aparelho que faz a chamada — o JIM não pode marcar.",
    it: "La chiamata la fa questo dispositivo: JIM non può comporre numeri.",
    ja: "電話をかけるのはこの端末です — JIMは発信できません。",
    zh: "由本设备拨出电话 — JIM 无法拨号。",
    hi: "कॉल यह डिवाइस करता है — JIM डायल नहीं कर सकता।",
    ar: "هذا الجهاز هو من يجري المكالمة — لا يستطيع JIM الاتصال.",
  },
  "w.em.cpr": {
    en: "CPR guide",
    es: "Guía de RCP",
    fr: "Guide RCP",
    de: "HLW-Anleitung",
    pt: "Guia de RCP",
    it: "Guida RCP",
    ja: "心肺蘇生ガイド",
    zh: "心肺复苏指南",
    hi: "सीपीआर गाइड",
    ar: "دليل الإنعاش القلبي",
  },
  "w.cpr.breaths": {
    en: "2 breaths",
    es: "2 respiraciones",
    fr: "2 insufflations",
    de: "2 Beatmungen",
    pt: "2 insuflações",
    it: "2 insufflazioni",
    ja: "人工呼吸2回",
    zh: "吹气2次",
    hi: "2 साँसें",
    ar: "نفسان",
  },
  "w.cpr.push": {
    en: "Push hard and fast",
    es: "Comprime fuerte y rápido",
    fr: "Appuyez fort et vite",
    de: "Fest und schnell drücken",
    pt: "Comprima com força e depressa",
    it: "Premi forte e veloce",
    ja: "強く速く押す",
    zh: "用力快速按压",
    hi: "ज़ोर से और तेज़ दबाएँ",
    ar: "اضغط بقوة وسرعة",
  },
  "w.cpr.stop": {
    en: "Stop",
    es: "Detener",
    fr: "Arrêter",
    de: "Beenden",
    pt: "Parar",
    it: "Ferma",
    ja: "やめる",
    zh: "停止",
    hi: "रोकें",
    ar: "إيقاف",
  },
  "w.cpr.rate": {
    en: "110/min · 30:2",
    es: "110/min · 30:2",
    fr: "110/min · 30:2",
    de: "110/min · 30:2",
    pt: "110/min · 30:2",
    it: "110/min · 30:2",
    ja: "毎分110回 · 30:2",
    zh: "每分钟110次 · 30:2",
    hi: "110/मिनट · 30:2",
    ar: "110/دقيقة · 30:2",
  },
  "w.cpr.start": {
    en: "Start metronome",
    es: "Iniciar metrónomo",
    fr: "Lancer le métronome",
    de: "Metronom starten",
    pt: "Iniciar metrónomo",
    it: "Avvia metronomo",
    ja: "メトロノーム開始",
    zh: "启动节拍器",
    hi: "मेट्रोनोम शुरू करें",
    ar: "تشغيل بندول الإيقاع",
  },
  "w.cpr.how": {
    en: "Center of the chest, at least 5 cm deep.",
    es: "Centro del pecho, al menos 5 cm de profundidad.",
    fr: "Au centre de la poitrine, à 5 cm de profondeur au moins.",
    de: "Mitte des Brustkorbs, mindestens 5 cm tief.",
    pt: "Centro do peito, pelo menos 5 cm de profundidade.",
    it: "Al centro del torace, almeno 5 cm di profondità.",
    ja: "胸の中央を、少なくとも5cm沈むまで。",
    zh: "胸部正中，按压深度至少5厘米。",
    hi: "छाती के बीच में, कम से कम 5 सेमी गहराई तक।",
    ar: "في منتصف الصدر، بعمق 5 سم على الأقل.",
  },
  "w.mid.title": {
    en: "Medical ID",
    es: "Identificación médica",
    fr: "Fiche médicale",
    de: "Notfallpass",
    pt: "Identificação médica",
    it: "Scheda medica",
    ja: "メディカル ID",
    zh: "医疗卡",
    hi: "मेडिकल आईडी",
    ar: "البطاقة الطبية",
  },
  "w.mid.show": {
    en: "Show my code",
    es: "Mostrar mi código",
    fr: "Afficher mon code",
    de: "Meinen Code zeigen",
    pt: "Mostrar o meu código",
    it: "Mostra il mio codice",
    ja: "コードを表示",
    zh: "显示我的码",
    hi: "मेरा कोड दिखाएँ",
    ar: "إظهار رمزي",
  },
  "w.mid.scan": {
    en: "A responder scans this to see what matters.",
    es: "Quien te atienda lo escanea y ve lo que importa.",
    fr: "Un secouriste le scanne et voit l'essentiel.",
    de: "Ersthelfende scannen ihn und sehen, was zählt.",
    pt: "Quem socorre digitaliza isto e vê o que importa.",
    it: "Chi soccorre lo scansiona e vede ciò che conta.",
    ja: "対応者がスキャンすると大事な情報が見えます。",
    zh: "急救人员扫描它即可看到关键信息。",
    hi: "मददगार इसे स्कैन कर ज़रूरी जानकारी देखता है।",
    ar: "يمسحه المسعف ليرى ما يهم.",
  },
  "w.sens.cautious": {
    en: "Cautious",
    es: "Cauteloso",
    fr: "Prudent",
    de: "Vorsichtig",
    pt: "Cauteloso",
    it: "Prudente",
    ja: "慎重",
    zh: "谨慎",
    hi: "सतर्क",
    ar: "حذر",
  },
  "w.sens.balanced": {
    en: "Balanced",
    es: "Equilibrado",
    fr: "Équilibré",
    de: "Ausgewogen",
    pt: "Equilibrado",
    it: "Equilibrato",
    ja: "バランス",
    zh: "均衡",
    hi: "संतुलित",
    ar: "متوازن",
  },
  "w.sens.assertive": {
    en: "Assertive",
    es: "Asertivo",
    fr: "Assertif",
    de: "Bestimmt",
    pt: "Assertivo",
    it: "Assertivo",
    ja: "積極的",
    zh: "果断",
    hi: "मुखर",
    ar: "حازم",
  },
  "w.amb.hand": {
    en: "JIM checks in when something seems off. Did the last nudge help?",
    es: "JIM pregunta cuando algo no cuadra. ¿Ayudó el último aviso?",
    fr: "JIM prend des nouvelles quand quelque chose cloche. Le dernier signe a-t-il aidé ?",
    de: "JIM meldet sich, wenn etwas nicht stimmt. Hat der letzte Anstoß geholfen?",
    pt: "O JIM pergunta quando algo parece estranho. O último toque ajudou?",
    it: "JIM si fa sentire quando qualcosa non torna. L'ultimo cenno è stato utile?",
    ja: "JIMは異変がありそうなとき声をかけます。前回の声かけは役に立ちましたか？",
    zh: "当情况似乎不对时，JIM 会来问候。上次的提醒有帮助吗？",
    hi: "जब कुछ ठीक न लगे तो JIM हाल पूछता है। पिछली दस्तक से मदद मिली?",
    ar: "يطمئن JIM عليك حين يبدو شيء غير طبيعي. هل أفادك التنبيه الأخير؟",
  },
  "w.amb.glad": {
    en: "Glad it helped.",
    es: "Me alegra que ayudara.",
    fr: "Content que ça ait aidé.",
    de: "Schön, dass es geholfen hat.",
    pt: "Ainda bem que ajudou.",
    it: "Bello che sia servito.",
    ja: "お役に立ててよかったです。",
    zh: "很高兴有帮助。",
    hi: "ख़ुशी है कि मदद मिली।",
    ar: "يسعدني أنه أفاد.",
  },
  "w.amb.more": {
    en: "Understood — it will try differently.",
    es: "Entendido: probará de otra forma.",
    fr: "Compris — il essaiera autrement.",
    de: "Verstanden — es versucht es anders.",
    pt: "Entendido — vai tentar de outra forma.",
    it: "Capito: proverà in un altro modo.",
    ja: "わかりました — 次は別のやり方で。",
    zh: "明白了 — 会换种方式。",
    hi: "समझ गया — अगली बार अलग तरीक़े से।",
    ar: "فهمت — سيحاول بطريقة مختلفة.",
  },
  "w.amb.later": {
    en: "Not now",
    es: "Ahora no",
    fr: "Pas maintenant",
    de: "Jetzt nicht",
    pt: "Agora não",
    it: "Non ora",
    ja: "今はいい",
    zh: "现在不",
    hi: "अभी नहीं",
    ar: "ليس الآن",
  },
  "w.comp.how": {
    en: "I'm here. How is it going?",
    es: "Estoy aquí. ¿Cómo va todo?",
    fr: "Je suis là. Comment ça va ?",
    de: "Ich bin da. Wie läuft es?",
    pt: "Estou aqui. Como vai isso?",
    it: "Sono qui. Come va?",
    ja: "ここにいますよ。調子はどうですか？",
    zh: "我在这里。最近怎么样？",
    hi: "मैं यहाँ हूँ। सब कैसा चल रहा है?",
    ar: "أنا هنا. كيف تسير الأمور؟",
  },
  "w.comp.ph": {
    en: "Tell me anything",
    es: "Cuéntame lo que sea",
    fr: "Dites-moi tout",
    de: "Erzähl mir alles",
    pt: "Conte-me o que quiser",
    it: "Dimmi qualsiasi cosa",
    ja: "なんでも話してください",
    zh: "想说什么都可以",
    hi: "कुछ भी बताइए",
    ar: "أخبرني بأي شيء",
  },
  "w.comp.reply": {
    en: "Reply",
    es: "Responder",
    fr: "Répondre",
    de: "Antworten",
    pt: "Responder",
    it: "Rispondi",
    ja: "返信",
    zh: "回复",
    hi: "जवाब दें",
    ar: "رد",
  },
  "w.comp.heard": {
    en: "Heard.",
    es: "Te escucho.",
    fr: "Bien reçu.",
    de: "Gehört.",
    pt: "Ouvido.",
    it: "Ricevuto.",
    ja: "聞きました。",
    zh: "听到了。",
    hi: "सुन लिया।",
    ar: "سمعتك.",
  },
  "w.notif.none": {
    en: "Nothing new.",
    es: "Nada nuevo.",
    fr: "Rien de nouveau.",
    de: "Nichts Neues.",
    pt: "Nada de novo.",
    it: "Niente di nuovo.",
    ja: "新しいものはありません。",
    zh: "没有新内容。",
    hi: "कुछ नया नहीं।",
    ar: "لا جديد.",
  },
  "w.dev.dripping": {
    en: "Phone reachable — the drip is flowing.",
    es: "El teléfono responde: el goteo fluye.",
    fr: "Téléphone joignable — le flux passe.",
    de: "Telefon erreichbar — der Tropf fließt.",
    pt: "Telemóvel acessível — o fluxo corre.",
    it: "Telefono raggiungibile: il flusso scorre.",
    ja: "電話に接続中 — データは流れています。",
    zh: "手机可达 — 数据正在流动。",
    hi: "फ़ोन पहुँच में है — प्रवाह चालू है।",
    ar: "الهاتف متاح — التدفق جارٍ.",
  },
  "w.dev.waiting": {
    en: "Waiting for the phone.",
    es: "Esperando al teléfono.",
    fr: "En attente du téléphone.",
    de: "Warte auf das Telefon.",
    pt: "À espera do telemóvel.",
    it: "In attesa del telefono.",
    ja: "電話を待っています。",
    zh: "正在等待手机。",
    hi: "फ़ोन की प्रतीक्षा में।",
    ar: "في انتظار الهاتف.",
  },
  "w.guard.rules": {
    en: "Watching by your rules — nothing leaves without them.",
    es: "Vigila según tus reglas: nada sale sin ellas.",
    fr: "Il veille selon vos règles — rien ne sort sans elles.",
    de: "Wacht nach deinen Regeln — nichts geht ohne sie hinaus.",
    pt: "Vigia pelas suas regras — nada sai sem elas.",
    it: "Veglia secondo le tue regole: niente esce senza di esse.",
    ja: "あなたのルールで見守ります — ルールなしには何も外に出ません。",
    zh: "按你的规则守护 — 没有规则，任何数据都不外传。",
    hi: "आपके नियमों से निगरानी — उनके बिना कुछ बाहर नहीं जाता।",
    ar: "يراقب وفق قواعدك — لا شيء يغادر من دونها.",
  },
  "w.set.sources": {
    en: "Sources on",
    es: "Fuentes activas",
    fr: "Sources actives",
    de: "Aktive Quellen",
    pt: "Fontes ativas",
    it: "Fonti attive",
    ja: "有効なソース",
    zh: "已开启的来源",
    hi: "सक्रिय स्रोत",
    ar: "المصادر المفعّلة",
  },
  "w.set.where": {
    en: "Everything else is set on the phone.",
    es: "Todo lo demás se ajusta en el teléfono.",
    fr: "Tout le reste se règle sur le téléphone.",
    de: "Alles Weitere stellst du am Telefon ein.",
    pt: "Tudo o resto define-se no telemóvel.",
    it: "Tutto il resto si imposta dal telefono.",
    ja: "そのほかの設定は電話で行います。",
    zh: "其余设置都在手机上完成。",
    hi: "बाक़ी सब फ़ोन पर सेट होता है।",
    ar: "كل ما عدا ذلك يُضبط من الهاتف.",
  },
  "w.br.ready": {
    en: "Ready when you are.",
    es: "Cuando tú quieras.",
    fr: "Quand vous voulez.",
    de: "Wenn du bereit bist.",
    pt: "Quando quiser.",
    it: "Quando vuoi.",
    ja: "準備ができたらどうぞ。",
    zh: "你准备好就开始。",
    hi: "जब आप तैयार हों।",
    ar: "متى ما كنت مستعدًا.",
  },
  "w.br.in": {
    en: "Breathe in",
    es: "Inhala",
    fr: "Inspirez",
    de: "Einatmen",
    pt: "Inspire",
    it: "Inspira",
    ja: "吸って",
    zh: "吸气",
    hi: "साँस लें",
    ar: "شهيق",
  },
  "w.br.hold": {
    en: "Hold",
    es: "Mantén",
    fr: "Retenez",
    de: "Halten",
    pt: "Sustenha",
    it: "Trattieni",
    ja: "止めて",
    zh: "屏住",
    hi: "साँस रोकें",
    ar: "احبس النفس",
  },
  "w.br.out": {
    en: "Breathe out",
    es: "Exhala",
    fr: "Expirez",
    de: "Ausatmen",
    pt: "Expire",
    it: "Espira",
    ja: "吐いて",
    zh: "呼气",
    hi: "साँस छोड़ें",
    ar: "زفير",
  },
  "w.br.begin": {
    en: "Begin",
    es: "Empezar",
    fr: "Commencer",
    de: "Beginnen",
    pt: "Começar",
    it: "Inizia",
    ja: "始める",
    zh: "开始",
    hi: "शुरू करें",
    ar: "ابدأ",
  },
  "w.br.done": {
    en: "Done",
    es: "Listo",
    fr: "Terminé",
    de: "Fertig",
    pt: "Concluído",
    it: "Fatto",
    ja: "完了",
    zh: "完成",
    hi: "हो गया",
    ar: "تم",
  },
  "w.fb.helpful": {
    en: "Was the guidance helpful?",
    es: "¿Te ayudó la orientación?",
    fr: "Les conseils ont-ils aidé ?",
    de: "Hat der Hinweis geholfen?",
    pt: "A orientação ajudou?",
    it: "I consigli sono stati utili?",
    ja: "ガイダンスは役に立ちましたか？",
    zh: "这次指导有帮助吗？",
    hi: "क्या मार्गदर्शन से मदद मिली?",
    ar: "هل أفادك الإرشاد؟",
  },
  "w.fb.trains": {
    en: "Thank you — this trains what comes next.",
    es: "Gracias: esto entrena lo que viene.",
    fr: "Merci — cela entraîne la suite.",
    de: "Danke — das formt, was als Nächstes kommt.",
    pt: "Obrigado — isto treina o que vem a seguir.",
    it: "Grazie: questo allena ciò che verrà.",
    ja: "ありがとうございます — 次の応答が良くなります。",
    zh: "谢谢 — 这会训练接下来的回应。",
    hi: "धन्यवाद — इससे आगे का जवाब बेहतर होगा।",
    ar: "شكرًا — هذا يدرّب ما يأتي لاحقًا.",
  },
  "w.jr.ph": {
    en: "A line for the journal",
    es: "Una línea para el diario",
    fr: "Une ligne pour le journal",
    de: "Eine Zeile fürs Tagebuch",
    pt: "Uma linha para o diário",
    it: "Una riga per il diario",
    ja: "日記にひとこと",
    zh: "给日志写一行",
    hi: "डायरी के लिए एक पंक्ति",
    ar: "سطر لليوميات",
  },
  "w.jr.stop": {
    en: "Stop",
    es: "Detener",
    fr: "Arrêter",
    de: "Beenden",
    pt: "Parar",
    it: "Ferma",
    ja: "やめる",
    zh: "停止",
    hi: "रोकें",
    ar: "إيقاف",
  },
  "w.jr.speak": {
    en: "Dictate",
    es: "Dictar",
    fr: "Dicter",
    de: "Diktieren",
    pt: "Ditar",
    it: "Detta",
    ja: "音声入力",
    zh: "口述",
    hi: "बोलकर लिखें",
    ar: "إملاء",
  },
  "w.jr.keep": {
    en: "Keep",
    es: "Guardar",
    fr: "Garder",
    de: "Behalten",
    pt: "Guardar",
    it: "Conserva",
    ja: "保存",
    zh: "保存",
    hi: "रखें",
    ar: "احتفظ",
  },
  "w.jr.kept": {
    en: "Kept.",
    es: "Guardado.",
    fr: "Gardé.",
    de: "Behalten.",
    pt: "Guardado.",
    it: "Conservato.",
    ja: "保存しました。",
    zh: "已保存。",
    hi: "रख लिया।",
    ar: "احتُفظ به.",
  },
  "w.co.mind": {
    en: "Mind",
    es: "Mente",
    fr: "Esprit",
    de: "Geist",
    pt: "Mente",
    it: "Mente",
    ja: "こころ",
    zh: "心智",
    hi: "मन",
    ar: "العقل",
  },
  "w.co.fitness": {
    en: "Fitness",
    es: "Forma física",
    fr: "Forme",
    de: "Fitness",
    pt: "Fitness",
    it: "Forma fisica",
    ja: "フィットネス",
    zh: "健身",
    hi: "फ़िटनेस",
    ar: "اللياقة",
  },
  "w.co.career": {
    en: "Career",
    es: "Carrera",
    fr: "Carrière",
    de: "Karriere",
    pt: "Carreira",
    it: "Carriera",
    ja: "キャリア",
    zh: "职业",
    hi: "करियर",
    ar: "المسيرة المهنية",
  },
  "w.co.money": {
    en: "Money",
    es: "Dinero",
    fr: "Argent",
    de: "Geld",
    pt: "Dinheiro",
    it: "Denaro",
    ja: "お金",
    zh: "财务",
    hi: "पैसा",
    ar: "المال",
  },
  "w.co.bonds": {
    en: "Bonds",
    es: "Vínculos",
    fr: "Liens",
    de: "Bindungen",
    pt: "Laços",
    it: "Legami",
    ja: "絆",
    zh: "情感纽带",
    hi: "रिश्ते",
    ar: "الروابط",
  },
  "w.co.growth": {
    en: "Growth",
    es: "Crecimiento",
    fr: "Épanouissement",
    de: "Wachstum",
    pt: "Crescimento",
    it: "Crescita",
    ja: "成長",
    zh: "成长",
    hi: "विकास",
    ar: "النمو",
  },
  "w.co.ph": {
    en: "Ask the coach",
    es: "Pregunta al coach",
    fr: "Demandez au coach",
    de: "Frag den Coach",
    pt: "Pergunte ao coach",
    it: "Chiedi al coach",
    ja: "コーチに聞く",
    zh: "问教练",
    hi: "कोच से पूछें",
    ar: "اسأل المدرب",
  },
  "w.co.ask": {
    en: "Ask",
    es: "Preguntar",
    fr: "Demander",
    de: "Fragen",
    pt: "Perguntar",
    it: "Chiedi",
    ja: "たずねる",
    zh: "询问",
    hi: "पूछें",
    ar: "اسأل",
  },
  "w.base.resting": {
    en: "resting rate, learned",
    es: "ritmo en reposo aprendido",
    fr: "rythme au repos appris",
    de: "gelernter Ruhepuls",
    pt: "ritmo em repouso aprendido",
    it: "ritmo a riposo appreso",
    ja: "学習した安静時心拍",
    zh: "已学习的静息心率",
    hi: "सीखी गई विश्राम गति",
    ar: "معدل الراحة المتعلَّم",
  },
  "w.base.learning": {
    en: "readings so far",
    es: "lecturas hasta ahora",
    fr: "mesures à ce jour",
    de: "Messwerte bisher",
    pt: "leituras até agora",
    it: "letture finora",
    ja: "これまでの計測",
    zh: "目前的读数",
    hi: "अब तक की रीडिंग",
    ar: "القراءات حتى الآن",
  },
  "w.src.none": {
    en: "No sources yet — grant one on the phone.",
    es: "Aún no hay fuentes: concede una en el teléfono.",
    fr: "Pas encore de sources — accordez-en une sur le téléphone.",
    de: "Noch keine Quellen — gib eine am Telefon frei.",
    pt: "Ainda sem fontes — autorize uma no telemóvel.",
    it: "Ancora nessuna fonte: concedine una dal telefono.",
    ja: "まだソースがありません — 電話で許可してください。",
    zh: "还没有来源 — 请在手机上授权一个。",
    hi: "अभी कोई स्रोत नहीं — फ़ोन पर अनुमति दें।",
    ar: "لا مصادر بعد — امنح إذنًا من الهاتف.",
  },
  "w.priv.chain": {
    en: "Every access is chained and checkable.",
    es: "Cada acceso queda encadenado y verificable.",
    fr: "Chaque accès est chaîné et vérifiable.",
    de: "Jeder Zugriff ist verkettet und prüfbar.",
    pt: "Cada acesso fica encadeado e verificável.",
    it: "Ogni accesso è concatenato e verificabile.",
    ja: "すべてのアクセスは連鎖記録され検証できます。",
    zh: "每次访问都被链式记录、可校验。",
    hi: "हर पहुँच शृंखला में दर्ज और जाँचने योग्य है।",
    ar: "كل وصول مُسلسل وقابل للتحقق.",
  },
  "w.priv.broken": {
    en: "The audit chain is broken — look on the phone.",
    es: "La cadena de auditoría está rota: revisa el teléfono.",
    fr: "La chaîne d'audit est rompue — voyez le téléphone.",
    de: "Die Prüfkette ist gebrochen — sieh am Telefon nach.",
    pt: "A cadeia de auditoria está quebrada — veja no telemóvel.",
    it: "La catena di audit è interrotta: controlla dal telefono.",
    ja: "監査チェーンが壊れています — 電話で確認してください。",
    zh: "审计链已断裂 — 请在手机上查看。",
    hi: "ऑडिट शृंखला टूटी है — फ़ोन पर देखें।",
    ar: "سلسلة التدقيق مكسورة — راجع الهاتف.",
  },
  "w.priv.entries": {
    en: "entries in the log",
    es: "entradas en el registro",
    fr: "entrées dans le journal",
    de: "Einträge im Protokoll",
    pt: "entradas no registo",
    it: "voci nel registro",
    ja: "件の記録",
    zh: "条日志记录",
    hi: "लॉग में प्रविष्टियाँ",
    ar: "إدخالات في السجل",
  },
  "w.ho.linked": {
    en: "Linked to a care team.",
    es: "Vinculado a un equipo de cuidado.",
    fr: "Relié à une équipe de soins.",
    de: "Mit einem Behandlungsteam verbunden.",
    pt: "Ligado a uma equipa de cuidados.",
    it: "Collegato a un team di cura.",
    ja: "ケアチームと連携しています。",
    zh: "已关联护理团队。",
    hi: "देखभाल टीम से जुड़ा है।",
    ar: "مرتبط بفريق رعاية.",
  },
  "w.ho.none": {
    en: "No care team linked.",
    es: "Sin equipo de cuidado vinculado.",
    fr: "Aucune équipe de soins reliée.",
    de: "Kein Behandlungsteam verbunden.",
    pt: "Nenhuma equipa de cuidados ligada.",
    it: "Nessun team di cura collegato.",
    ja: "ケアチームは未連携です。",
    zh: "未关联护理团队。",
    hi: "कोई देखभाल टीम नहीं जुड़ी।",
    ar: "لا فريق رعاية مرتبطًا.",
  },
  "w.ho.revocable": {
    en: "Revocable any time on the phone.",
    es: "Revocable en cualquier momento desde el teléfono.",
    fr: "Révocable à tout moment sur le téléphone.",
    de: "Jederzeit am Telefon widerrufbar.",
    pt: "Revogável a qualquer momento no telemóvel.",
    it: "Revocabile in ogni momento dal telefono.",
    ja: "いつでも電話で取り消せます。",
    zh: "随时可在手机上撤销。",
    hi: "फ़ोन पर कभी भी वापस लिया जा सकता है।",
    ar: "يمكن إلغاؤه في أي وقت من الهاتف.",
  },
  "w.offl.nothing": {
    en: "Offline — nothing leaves this device.",
    es: "Sin conexión: nada sale de este dispositivo.",
    fr: "Hors ligne — rien ne quitte cet appareil.",
    de: "Offline — nichts verlässt dieses Gerät.",
    pt: "Offline — nada sai deste aparelho.",
    it: "Offline: niente lascia questo dispositivo.",
    ja: "オフライン — この端末から何も出ていきません。",
    zh: "离线 — 任何数据都不离开此设备。",
    hi: "ऑफ़लाइन — इस डिवाइस से कुछ बाहर नहीं जाता।",
    ar: "دون اتصال — لا شيء يغادر هذا الجهاز.",
  },
  "w.offl.open": {
    en: "Cloud attached — sharing follows your rules.",
    es: "Nube conectada: compartir sigue tus reglas.",
    fr: "Cloud rattaché — le partage suit vos règles.",
    de: "Cloud verbunden — geteilt wird nach deinen Regeln.",
    pt: "Nuvem ligada — a partilha segue as suas regras.",
    it: "Cloud collegato: la condivisione segue le tue regole.",
    ja: "クラウド接続中 — 共有はあなたのルールに従います。",
    zh: "已连接云端 — 共享遵循你的规则。",
    hi: "क्लाउड जुड़ा है — साझा करना आपके नियमों से होता है।",
    ar: "السحابة متصلة — تتم المشاركة وفق قواعدك.",
  },
  "w.cond.none": {
    en: "No conditions recorded.",
    es: "Sin afecciones registradas.",
    fr: "Aucune pathologie enregistrée.",
    de: "Keine Erkrankungen erfasst.",
    pt: "Sem condições registadas.",
    it: "Nessuna patologia registrata.",
    ja: "既往症の記録はありません。",
    zh: "未记录健康状况。",
    hi: "कोई स्थिति दर्ज नहीं।",
    ar: "لا حالات مسجلة.",
  },
  "w.cond.adapts": {
    en: "Guidance adapts to what is recorded here.",
    es: "La orientación se adapta a lo registrado aquí.",
    fr: "Les conseils s'adaptent à ce qui est noté ici.",
    de: "Hinweise richten sich nach dem, was hier steht.",
    pt: "A orientação adapta-se ao que aqui está registado.",
    it: "I consigli si adattano a ciò che è registrato qui.",
    ja: "ガイダンスはここに記録された内容に合わせます。",
    zh: "指导会依据此处的记录进行调整。",
    hi: "मार्गदर्शन यहाँ दर्ज जानकारी के अनुसार ढलता है।",
    ar: "يتكيف الإرشاد مع ما هو مسجل هنا.",
  },
  "w.style.shapes": {
    en: "A word or two shapes how JIM speaks.",
    es: "Una o dos palabras moldean cómo habla JIM.",
    fr: "Un mot ou deux façonnent la voix de JIM.",
    de: "Ein, zwei Worte prägen, wie JIM spricht.",
    pt: "Uma ou duas palavras moldam como o JIM fala.",
    it: "Una parola o due plasmano il modo di parlare di JIM.",
    ja: "一言二言でJIMの話し方が決まります。",
    zh: "一两个词就能塑造 JIM 的说话方式。",
    hi: "एक-दो शब्द तय करते हैं कि JIM कैसे बोले।",
    ar: "كلمة أو كلمتان تشكلان طريقة كلام JIM.",
  },
  "w.style.ph": {
    en: "e.g. warm, brief",
    es: "p. ej. cálido, breve",
    fr: "ex. chaleureux, bref",
    de: "z. B. warm, knapp",
    pt: "p. ex. caloroso, breve",
    it: "es. caldo, breve",
    ja: "例：あたたかく、簡潔に",
    zh: "例如：温暖、简短",
    hi: "जैसे: गर्मजोशी, संक्षिप्त",
    ar: "مثلًا: دافئ، مقتضب",
  },
  "w.style.set": {
    en: "Set",
    es: "Fijar",
    fr: "Définir",
    de: "Festlegen",
    pt: "Definir",
    it: "Imposta",
    ja: "設定する",
    zh: "设定",
    hi: "सेट करें",
    ar: "تعيين",
  },
  "w.style.done": {
    en: "Set — the next reply wears it.",
    es: "Fijado: la próxima respuesta lo llevará.",
    fr: "Défini — la prochaine réponse le portera.",
    de: "Festgelegt — die nächste Antwort trägt es.",
    pt: "Definido — a próxima resposta já o veste.",
    it: "Impostato: la prossima risposta lo indosserà.",
    ja: "設定しました — 次の返事から反映されます。",
    zh: "已设定 — 下一条回复就会体现。",
    hi: "सेट हो गया — अगला जवाब इसी अंदाज़ में होगा।",
    ar: "تم التعيين — سيظهر في الرد التالي.",
  },
  "w.hist.none": {
    en: "Nothing yet.",
    es: "Todavía nada.",
    fr: "Rien pour l'instant.",
    de: "Noch nichts.",
    pt: "Ainda nada.",
    it: "Ancora niente.",
    ja: "まだ何もありません。",
    zh: "暂时还没有。",
    hi: "अभी कुछ नहीं।",
    ar: "لا شيء بعد.",
  },
  "w.fam.none": {
    en: "Nobody in your care yet.",
    es: "Aún no cuidas de nadie.",
    fr: "Personne sous votre garde pour l'instant.",
    de: "Noch niemand in deiner Obhut.",
    pt: "Ainda ninguém ao seu cuidado.",
    it: "Ancora nessuno sotto la tua cura.",
    ja: "まだ見守る相手がいません。",
    zh: "尚无你照护的人。",
    hi: "अभी आपकी देखरेख में कोई नहीं।",
    ar: "لا أحد في رعايتك بعد.",
  },
  "w.ag.running": {
    en: "Running",
    es: "En marcha",
    fr: "En cours",
    de: "Laufend",
    pt: "Em curso",
    it: "In corso",
    ja: "実行中",
    zh: "运行中",
    hi: "चल रहे",
    ar: "قيد التشغيل",
  },
  "w.ag.needhelp": {
    en: "Waiting on you",
    es: "Esperándote",
    fr: "En attente de vous",
    de: "Wartet auf dich",
    pt: "À sua espera",
    it: "In attesa di te",
    ja: "あなた待ち",
    zh: "等待你",
    hi: "आपकी प्रतीक्षा में",
    ar: "بانتظارك",
  },
  "w.ag.open": {
    en: "Open the phone to steer them.",
    es: "Abre el teléfono para dirigirlos.",
    fr: "Ouvrez le téléphone pour les piloter.",
    de: "Öffne das Telefon, um sie zu steuern.",
    pt: "Abra o telemóvel para os orientar.",
    it: "Apri il telefono per guidarli.",
    ja: "操作は電話から行えます。",
    zh: "打开手机来指挥它们。",
    hi: "उन्हें चलाने के लिए फ़ोन खोलें।",
    ar: "افتح الهاتف لتوجيهها.",
  },
  // -- the conversation you took with you ----------------------------------
  // Both of this console's conversations unmount when you change screens,
  // which is right for navigating away and wrong for walking away on
  // purpose. These name the strip that survives it.
  // Not "Take it with you": `hld.take` already carries that exact English
  // for the export file, and two keys with one English sentence and two sets
  // of translations show a reader of that language two different words for
  // one thing. They are also genuinely different acts — one takes a file,
  // this one takes a conversation — so the English says which.
  "walk.take": {
    en: "Take the conversation with you", es: "Llévate la conversación", fr: "Emmène la conversation avec toi", de: "Nimm das Gespräch mit", pt: "Leva a conversa contigo", it: "Porta con te la conversazione", ja: "会話を連れて行く", zh: "带着这段对话一起走", hi: "बातचीत को साथ ले जाओ", ar: "خُذ المحادثة معك",
  },
  "walk.end": {
    en: "End", es: "Terminar", fr: "Terminer", de: "Beenden", pt: "Terminar", it: "Termina", ja: "終了", zh: "结束", hi: "समाप्त", ar: "إنهاء",
  },
  "walk.again": {
    en: "Listen again", es: "Escuchar otra vez", fr: "Écouter à nouveau", de: "Wieder zuhören", pt: "Ouvir de novo", it: "Ascolta di nuovo", ja: "もう一度聞く", zh: "再次聆听", hi: "फिर से सुनो", ar: "استمع مرّة أخرى",
  },
  "walk.listening": {
    en: "listening", es: "escuchando", fr: "à l'écoute", de: "hört zu", pt: "a ouvir", it: "in ascolto", ja: "聞いています", zh: "正在聆听", hi: "सुन रहा है", ar: "يستمع",
  },
  "walk.speaking": {
    en: "answering", es: "respondiendo", fr: "répond", de: "antwortet", pt: "a responder", it: "sta rispondendo", ja: "応答しています", zh: "正在回答", hi: "जवाब दे रहा है", ar: "يجيب",
  },
  "walk.quiet": {
    en: "not listening", es: "sin escuchar", fr: "n'écoute pas", de: "hört nicht zu", pt: "sem ouvir", it: "non in ascolto", ja: "聞いていません", zh: "未在聆听", hi: "नहीं सुन रहा", ar: "لا يستمع",
  },
  // The page is minimised or behind another tab and the microphone is still
  // open, which is the point rather than an accident — the browser is
  // showing its own recording indicator the whole time. Said plainly,
  // because somebody who minimised the window on purpose still deserves to
  // know what is running.
  //
  // This is the state when the capture really did survive. iOS Safari
  // suspends the page instead, so an iPhone gets the sentence below rather
  // than this one — which is why both exist.
  "walk.aloft": {
    en: "still listening while you're away — the browser shows it is recording", es: "sigue escuchando mientras no estás — el navegador indica que está grabando", fr: "écoute toujours pendant ton absence — le navigateur indique qu'il enregistre", de: "hört weiter zu, während du weg bist — der Browser zeigt an, dass er aufnimmt", pt: "continua a ouvir enquanto estás fora — o navegador mostra que está a gravar", it: "continua ad ascoltare mentre non ci sei — il browser segnala che sta registrando", ja: "離れている間も聞いています — ブラウザーが録音中と表示しています", zh: "你离开时仍在聆听 — 浏览器会显示正在录音", hi: "तुम्हारे दूर रहते हुए भी सुन रहा है — ब्राउज़र दिखा रहा है कि रिकॉर्ड हो रहा है", ar: "ما زال يستمع أثناء غيابك — يُظهر المتصفّح أنه يسجّل",
  },
  // An answer from the offline stack is an answer — a deployment with no
  // model key still coaches, from stored knowledge — but it is not the model
  // somebody picked, and on the strip there is no screen to notice that on.
  "walk.offline": {
    en: "answered from what's stored here", es: "respondido con lo que hay guardado aquí", fr: "répondu à partir de ce qui est stocké ici", de: "beantwortet aus dem, was hier gespeichert ist", pt: "respondido a partir do que está guardado aqui", it: "risposto con ciò che è conservato qui", ja: "ここに保存されている知識から回答", zh: "由本机存有的知识作答", hi: "यहाँ संग्रहीत जानकारी से उत्तर", ar: "أُجيب من المحفوظ هنا",
  },
  // And when it did not survive. The strip asks its listener on the way
  // back whether the microphone is still open, and this is what it says
  // when the answer is no — an iPhone returning from the home screen, most
  // often. Naming the browser rather than the app, because the app did not
  // choose this and the person can do nothing about it from inside here.
  "walk.away.stopped": {
    en: "the browser stopped listening while you were away", es: "el navegador dejó de escuchar mientras no estabas", fr: "le navigateur a cessé d'écouter pendant ton absence", de: "der Browser hat aufgehört zuzuhören, während du weg warst", pt: "o navegador deixou de ouvir enquanto estavas fora", it: "il browser ha smesso di ascoltare mentre non c'eri", ja: "離れている間にブラウザーが聞くのをやめました", zh: "你离开时，浏览器停止了聆听", hi: "तुम्हारे दूर रहते हुए ब्राउज़र ने सुनना बंद कर दिया", ar: "توقّف المتصفّح عن الاستماع أثناء غيابك",
  },
  "walk.lost": {
    en: "that did not reach it", es: "eso no llegó", fr: "cela n'est pas arrivé", de: "das kam nicht an", pt: "isso não chegou", it: "non è arrivato", ja: "届きませんでした", zh: "没有送达", hi: "वह नहीं पहुँचा", ar: "لم يصل ذلك",
  },

  // ---- the capability register (screens/Capabilities.tsx) -------
  //
  // Named for what each faculty does, not for the body part it
  // resembles. The shorthand behind these rows is anatomical and
  // that shorthand is precisely wrong in front of a clinician, a
  // regulator or an attorney: "eyes" claims a faculty, where
  // "visual perception, described in words and not retained"
  // states a behaviour somebody else can hold this product to.
  "nav.capabilities": {
    en: "Capabilities", es: "Capacidades", fr: "Capacités", de: "Fähigkeiten", pt: "Capacidades", it: "Capacità", ja: "機能", zh: "功能权限", hi: "क्षमताएँ", ar: "القدرات",
  },
  "cap.title": {
    en: "Capabilities", es: "Capacidades", fr: "Capacités", de: "Fähigkeiten", pt: "Capacidades", it: "Capacità", ja: "機能", zh: "功能权限", hi: "क्षमताएँ", ar: "القدرات",
  },
  "cap.lead": {
    en: "Every faculty this Guardian can be given, what each one currently is, the permission it rests on, and the screen that withdraws it.", es: "Cada facultad que puede otorgarse a este Guardian, en qué estado se encuentra, el permiso en que se apoya y la pantalla que la retira.", fr: "Chaque faculté que ce Guardian peut recevoir, son état actuel, l'autorisation sur laquelle elle repose et l'écran qui la retire.", de: "Jede Fähigkeit, die dieser Guardian erhalten kann, ihr aktueller Stand, die zugrunde liegende Erlaubnis und der Bildschirm, der sie zurücknimmt.", pt: "Cada faculdade que pode ser dada a este Guardian, o estado atual, a permissão em que assenta e o ecrã que a retira.", it: "Ogni facoltà che questo Guardian può ricevere, il suo stato attuale, il permesso su cui si fonda e la schermata che lo revoca.", ja: "この Guardian に与えられる各機能と、その現在の状態、根拠となる許可、および取り消しを行う画面。", zh: "此 Guardian 可被授予的每项功能、当前状态、所依据的许可，以及撤销该功能的页面。", hi: "इस Guardian को दी जा सकने वाली हर क्षमता, उसकी वर्तमान स्थिति, जिस अनुमति पर वह टिकी है, और वह स्क्रीन जो उसे वापस लेती है।", ar: "كل قدرة يمكن منحها لهذا الـ Guardian، وحالتها الراهنة، والإذن الذي تستند إليه، والشاشة التي تسحبها.",
  },
  "cap.standing": {
    en: "Nothing on this screen grants or revokes. It reads the same routes the owning screens read, and routes to them. A capability shown here as absent is absent because no permission for it exists — not because this page is withholding it.", es: "Nada en esta pantalla otorga ni revoca. Lee las mismas rutas que leen las pantallas propietarias y conduce a ellas. Una capacidad que aquí aparece ausente lo está porque no existe permiso para ella, no porque esta página la oculte.", fr: "Rien sur cet écran n'accorde ni ne révoque. Il lit les mêmes routes que les écrans propriétaires et y conduit. Une capacité indiquée ici comme absente l'est parce qu'aucune autorisation n'existe pour elle, non parce que cette page la dissimule.", de: "Nichts auf diesem Bildschirm erteilt oder entzieht etwas. Er liest dieselben Routen wie die zuständigen Bildschirme und führt zu ihnen. Eine hier als fehlend angezeigte Fähigkeit fehlt, weil keine Erlaubnis dafür besteht — nicht weil diese Seite sie zurückhält.", pt: "Nada neste ecrã concede ou revoga. Lê as mesmas rotas que os ecrãs proprietários leem e encaminha para eles. Uma capacidade aqui indicada como ausente está ausente porque não existe permissão para ela, não porque esta página a esconda.", it: "Nulla in questa schermata concede o revoca. Legge le stesse rotte lette dalle schermate competenti e vi conduce. Una capacità qui indicata come assente lo è perché non esiste alcun permesso per essa, non perché questa pagina la nasconda.", ja: "この画面は許可の付与も取り消しも行いません。各機能を所管する画面と同じ経路を読み取り、そこへ案内するだけです。ここで「なし」と表示される機能は、そのための許可が存在しないからであり、このページが伏せているからではありません。", zh: "本页面不授予也不撤销任何权限。它读取与各功能所属页面相同的接口，并引导至这些页面。此处显示为「无」的功能，是因为不存在相应许可，而非本页面有所隐瞒。", hi: "इस स्क्रीन पर कुछ भी अनुमति नहीं देता और न ही वापस लेता है। यह वही मार्ग पढ़ती है जो सम्बंधित स्क्रीनें पढ़ती हैं, और उन तक पहुँचाती है। यहाँ जो क्षमता अनुपस्थित दिखती है वह इसलिए अनुपस्थित है कि उसके लिए कोई अनुमति मौजूद नहीं — इसलिए नहीं कि यह पृष्ठ उसे छिपा रहा है।", ar: "لا شيء في هذه الشاشة يمنح أو يسحب. إنّها تقرأ المسارات ذاتها التي تقرأها الشاشات المختصّة وتوجّه إليها. القدرة التي تظهر هنا غائبة فهي غائبة لعدم وجود إذن بها، لا لأنّ هذه الصفحة تحجبها.",
  },
  "cap.now": {
    en: "Now:", es: "Ahora:", fr: "Actuellement :", de: "Jetzt:", pt: "Agora:", it: "Ora:", ja: "現在:", zh: "当前：", hi: "अभी:", ar: "الآن:",
  },
  "cap.rests": {
    en: "Rests on:", es: "Se apoya en:", fr: "Repose sur :", de: "Beruht auf:", pt: "Assenta em:", it: "Si fonda su:", ja: "根拠:", zh: "依据：", hi: "किस पर टिका:", ar: "يستند إلى:",
  },
  "cap.open": {
    en: "Open {screen}", es: "Abrir {screen}", fr: "Ouvrir {screen}", de: "{screen} öffnen", pt: "Abrir {screen}", it: "Apri {screen}", ja: "{screen} を開く", zh: "打开{screen}", hi: "{screen} खोलें", ar: "فتح {screen}",
  },
  "cap.reading": {
    en: "reading…", es: "leyendo…", fr: "lecture…", de: "wird gelesen…", pt: "a ler…", it: "in lettura…", ja: "読み取り中…", zh: "读取中…", hi: "पढ़ा जा रहा है…", ar: "جارٍ القراءة…",
  },
  "cap.unreadable": {
    en: "could not be read from this device", es: "no se pudo leer desde este dispositivo", fr: "n'a pas pu être lu depuis cet appareil", de: "konnte von diesem Gerät nicht gelesen werden", pt: "não foi possível ler a partir deste dispositivo", it: "non è stato possibile leggerlo da questo dispositivo", ja: "この端末からは読み取れませんでした", zh: "无法从本设备读取", hi: "इस डिवाइस से पढ़ा नहीं जा सका", ar: "تعذّرت القراءة من هذا الجهاز",
  },
  "cap.sight.title": {
    en: "Visual perception", es: "Percepción visual", fr: "Perception visuelle", de: "Visuelle Wahrnehmung", pt: "Perceção visual", it: "Percezione visiva", ja: "視覚的知覚", zh: "视觉感知", hi: "दृश्य बोध", ar: "الإدراك البصري",
  },
  "cap.sight.what": {
    en: "A monitor with a lens describes what it is pointed at, in one sentence. The frame is held only long enough to describe it and is never written down.", es: "Un monitor con lente describe en una frase aquello a lo que apunta. El fotograma se retiene solo el tiempo necesario para describirlo y nunca se guarda.", fr: "Un moniteur doté d'un objectif décrit en une phrase ce qu'il vise. L'image n'est conservée que le temps de la décrire et n'est jamais enregistrée.", de: "Ein Monitor mit Objektiv beschreibt in einem Satz, worauf er gerichtet ist. Das Bild wird nur so lange gehalten, wie die Beschreibung dauert, und nie gespeichert.", pt: "Um monitor com lente descreve numa frase aquilo para onde aponta. O fotograma é retido apenas o tempo necessário para o descrever e nunca é guardado.", it: "Un monitor dotato di obiettivo descrive in una frase ciò che inquadra. Il fotogramma è trattenuto solo per il tempo della descrizione e non viene mai salvato.", ja: "レンズを備えたモニターが、向けられた対象を一文で説明します。映像は説明に要する間だけ保持され、記録されることはありません。", zh: "带镜头的监测设备用一句话描述其所对准的对象。画面仅在生成描述期间保留，不会被写入存储。", hi: "लेंस वाला मॉनिटर जिस ओर लक्षित है उसे एक वाक्य में बताता है। फ़्रेम केवल वर्णन जितनी देर रखा जाता है और कभी लिखा नहीं जाता।", ar: "تصف شاشة مزوّدة بعدسة ما هي موجّهة إليه في جملة واحدة. تُحتفظ الصورة بقدر ما يلزم لوصفها فقط ولا تُدوَّن أبدًا.",
  },
  "cap.sight.rests": {
    en: "A monitor switched on by the account holder, with a lens among its senses. Anything that senses other people is refused until they have been told.", es: "Un monitor encendido por la persona titular de la cuenta, con una lente entre sus sentidos. Todo lo que perciba a otras personas se rechaza hasta que se les haya informado.", fr: "Un moniteur activé par le titulaire du compte, dont les capteurs comprennent un objectif. Tout capteur percevant d'autres personnes est refusé tant qu'elles n'ont pas été informées.", de: "Ein von der kontoführenden Person eingeschalteter Monitor, dessen Sinne ein Objektiv umfassen. Alles, was andere Personen wahrnimmt, wird abgelehnt, bis diese informiert wurden.", pt: "Um monitor ligado pela pessoa titular da conta, com uma lente entre os seus sentidos. Tudo o que percecione outras pessoas é recusado até que estas tenham sido informadas.", it: "Un monitor acceso dal titolare dell'account, con un obiettivo fra i suoi sensi. Tutto ciò che percepisce altre persone è rifiutato finché non siano state informate.", ja: "アカウント保有者が有効にした、センサーにレンズを含むモニター。他者を感知するものは、その旨が伝えられるまで拒否されます。", zh: "由账户持有人开启、且传感方式包含镜头的监测设备。任何会感知他人的功能，在其被告知之前一律拒绝。", hi: "खाताधारक द्वारा चालू किया गया मॉनिटर, जिसकी इंद्रियों में लेंस शामिल हो। जो कुछ अन्य लोगों को भाँपता है, उसे तब तक अस्वीकार किया जाता है जब तक उन्हें बताया न गया हो।", ar: "شاشة شغّلها صاحب الحساب وتضمّ عدسة بين حواسّها. ويُرفض كل ما يستشعر أشخاصًا آخرين إلى أن يُبلَّغوا بذلك.",
  },
  "cap.sight.none": {
    en: "no monitor with a lens is switched on", es: "no hay ningún monitor con lente encendido", fr: "aucun moniteur doté d'un objectif n'est activé", de: "kein Monitor mit Objektiv ist eingeschaltet", pt: "nenhum monitor com lente está ligado", it: "nessun monitor con obiettivo è acceso", ja: "レンズ付きのモニターは有効になっていません", zh: "未开启任何带镜头的监测设备", hi: "लेंस वाला कोई मॉनिटर चालू नहीं है", ar: "لا توجد شاشة بعدسة مشغّلة",
  },
  "cap.sight.some": {
    en: "{n} switched on — {names}", es: "{n} encendidos — {names}", fr: "{n} activés — {names}", de: "{n} eingeschaltet — {names}", pt: "{n} ligados — {names}", it: "{n} accesi — {names}", ja: "{n} 台が有効 — {names}", zh: "已开启 {n} 台 — {names}", hi: "{n} चालू — {names}", ar: "{n} مشغّلة — {names}",
  },
  "cap.hearing.title": {
    en: "Auxiliary audio input", es: "Entrada de audio auxiliar", fr: "Entrée audio auxiliaire", de: "Zusätzlicher Audioeingang", pt: "Entrada de áudio auxiliar", it: "Ingresso audio ausiliario", ja: "補助音声入力", zh: "辅助音频输入", hi: "सहायक ऑडियो इनपुट", ar: "مدخل صوتي مساعد",
  },
  "cap.hearing.what": {
    en: "A second microphone — a watch, earbuds, a clip-on, glasses — lent to the agent as its own channel while the phone's own microphone is occupied.", es: "Un segundo micrófono —un reloj, auriculares, un micrófono de solapa, unas gafas— cedido al agente como canal propio mientras el micrófono del teléfono está ocupado.", fr: "Un second microphone — montre, écouteurs, micro-cravate, lunettes — prêté à l'agent comme canal propre tant que le microphone du téléphone est occupé.", de: "Ein zweites Mikrofon — eine Uhr, Ohrhörer, ein Ansteckmikrofon, eine Brille — das dem Agenten als eigener Kanal geliehen wird, solange das Mikrofon des Telefons belegt ist.", pt: "Um segundo microfone — um relógio, auriculares, um microfone de lapela, óculos — emprestado ao agente como canal próprio enquanto o microfone do telemóvel está ocupado.", it: "Un secondo microfono — un orologio, auricolari, un microfono a clip, occhiali — prestato all'agente come canale proprio mentre il microfono del telefono è occupato.", ja: "腕時計、イヤホン、クリップマイク、眼鏡といった第二のマイクを、端末本体のマイクが使用中の間、エージェント専用の入力として貸し出します。", zh: "在手机自身麦克风被占用期间，将第二个麦克风——手表、耳机、领夹麦克风、眼镜——借给该代理作为其专属通道。", hi: "दूसरा माइक्रोफ़ोन — घड़ी, इयरबड, क्लिप-ऑन या चश्मा — फ़ोन का अपना माइक्रोफ़ोन व्यस्त रहने तक एजेंट को उसके अपने चैनल के रूप में दिया जाता है।", ar: "ميكروفون ثانٍ — ساعة أو سمّاعات أو ميكروفون لاقط أو نظّارة — يُعار للوكيل كقناة خاصّة به ما دام ميكروفون الهاتف مشغولًا.",
  },
  "cap.hearing.rests": {
    en: "A device paired and switched on for this purpose, and consent recorded on this browser. Capture happens on the device; no audio sample is stored by this service.", es: "Un dispositivo emparejado y encendido para este fin, y el consentimiento registrado en este navegador. La captura ocurre en el dispositivo; este servicio no almacena ninguna muestra de audio.", fr: "Un appareil appairé et activé à cette fin, et un consentement enregistré sur ce navigateur. La capture a lieu sur l'appareil ; ce service ne conserve aucun échantillon audio.", de: "Ein für diesen Zweck gekoppeltes und eingeschaltetes Gerät sowie eine in diesem Browser hinterlegte Einwilligung. Die Aufnahme erfolgt auf dem Gerät; dieser Dienst speichert keine Audioprobe.", pt: "Um dispositivo emparelhado e ligado para este fim, e o consentimento registado neste navegador. A captura ocorre no dispositivo; este serviço não guarda qualquer amostra de áudio.", it: "Un dispositivo associato e acceso a questo scopo, e il consenso registrato su questo browser. L'acquisizione avviene sul dispositivo; questo servizio non conserva alcun campione audio.", ja: "この目的のためにペアリングされ有効化された機器と、このブラウザーに記録された同意。収音は機器側で行われ、本サービスは音声データを保存しません。", zh: "为此目的配对并开启的设备，以及记录在本浏览器中的同意。采集在设备端进行；本服务不存储任何音频样本。", hi: "इस प्रयोजन हेतु युग्मित और चालू किया गया उपकरण, तथा इस ब्राउज़र में दर्ज सहमति। कैप्चर उपकरण पर होता है; यह सेवा कोई ऑडियो नमूना संग्रहीत नहीं करती।", ar: "جهاز مقترن ومشغّل لهذا الغرض، وموافقة مسجّلة في هذا المتصفّح. يجري الالتقاط على الجهاز؛ ولا تخزّن هذه الخدمة أي عيّنة صوتية.",
  },
  "cap.hearing.none": {
    en: "no second microphone is attached", es: "no hay ningún segundo micrófono conectado", fr: "aucun second microphone n'est raccordé", de: "kein zweites Mikrofon ist angeschlossen", pt: "nenhum segundo microfone está ligado", it: "nessun secondo microfono è collegato", ja: "第二のマイクは接続されていません", zh: "未连接第二个麦克风", hi: "कोई दूसरा माइक्रोफ़ोन संलग्न नहीं है", ar: "لا يوجد ميكروفون ثانٍ موصول",
  },
  "cap.hearing.idle": {
    en: "{n} attached, not listening", es: "{n} conectados, sin escuchar", fr: "{n} raccordés, sans écoute", de: "{n} angeschlossen, hört nicht zu", pt: "{n} ligados, sem escutar", it: "{n} collegati, non in ascolto", ja: "{n} 台接続、待機中", zh: "已连接 {n} 台，未在聆听", hi: "{n} संलग्न, सुन नहीं रहा", ar: "{n} موصول، وغير مُنصِت",
  },
  "cap.hearing.live": {
    en: "listening on {device}", es: "escuchando en {device}", fr: "écoute sur {device}", de: "hört über {device} zu", pt: "a escutar em {device}", it: "in ascolto su {device}", ja: "{device} で受音中", zh: "正在通过 {device} 聆听", hi: "{device} पर सुन रहा है", ar: "يُنصِت عبر {device}",
  },
  "cap.speech.title": {
    en: "Speech output", es: "Salida de voz", fr: "Sortie vocale", de: "Sprachausgabe", pt: "Saída de voz", it: "Uscita vocale", ja: "音声出力", zh: "语音输出", hi: "वाक् आउटपुट", ar: "الإخراج الصوتي",
  },
  "cap.speech.what": {
    en: "Written replies spoken aloud through the configured speaking provider, in the reader's own language.", es: "Respuestas escritas pronunciadas en voz alta mediante el proveedor de voz configurado, en el idioma de quien lee.", fr: "Des réponses écrites énoncées à voix haute par le fournisseur vocal configuré, dans la langue du lecteur.", de: "Geschriebene Antworten, die über den eingerichteten Sprachanbieter vorgelesen werden, in der Sprache der lesenden Person.", pt: "Respostas escritas ditas em voz alta pelo fornecedor de voz configurado, na língua de quem lê.", it: "Risposte scritte pronunciate ad alta voce tramite il fornitore vocale configurato, nella lingua di chi legge.", ja: "設定済みの音声提供者を通じて、読み手の言語で回答を読み上げます。", zh: "通过已配置的语音服务提供方，以读者自身的语言朗读书面回复。", hi: "कॉन्फ़िगर किए गए वाक् प्रदाता के माध्यम से लिखित उत्तर पाठक की अपनी भाषा में बोलकर सुनाए जाते हैं।", ar: "ردود مكتوبة تُنطق بصوت مسموع عبر مزوّد الصوت المهيّأ، بلغة القارئ.",
  },
  "cap.speech.rests": {
    en: "A speaking provider configured for this deployment. With none configured the allowance route refuses, and this row says so rather than showing a balance of zero.", es: "Un proveedor de voz configurado para esta instalación. Si no hay ninguno, la ruta de saldo rechaza la petición y esta fila lo indica en lugar de mostrar un saldo de cero.", fr: "Un fournisseur vocal configuré pour ce déploiement. En l'absence de fournisseur, la route de quota refuse, et cette ligne le dit plutôt que d'afficher un solde nul.", de: "Ein für diese Installation eingerichteter Sprachanbieter. Ist keiner eingerichtet, lehnt die Kontingentroute ab, und diese Zeile sagt das, statt ein Guthaben von null anzuzeigen.", pt: "Um fornecedor de voz configurado para esta instalação. Sem nenhum, a rota de saldo recusa, e esta linha di-lo em vez de mostrar um saldo de zero.", it: "Un fornitore vocale configurato per questa installazione. Se non ve n'è alcuno la rotta del credito rifiuta, e questa riga lo dichiara invece di mostrare un saldo pari a zero.", ja: "この配備に設定された音声提供者。未設定の場合、残量の経路は拒否を返し、この行は残量ゼロと示す代わりにその旨を述べます。", zh: "为本次部署配置的语音服务提供方。若未配置，额度接口将予以拒绝，本行如实说明，而不是显示余额为零。", hi: "इस परिनियोजन के लिए कॉन्फ़िगर किया गया वाक् प्रदाता। कोई न होने पर शेष-राशि मार्ग अस्वीकार करता है, और यह पंक्ति शून्य शेष दिखाने के बजाय यही बताती है।", ar: "مزوّد صوت مهيّأ لهذا النشر. وفي غياب أي مزوّد يرفض مسار الرصيد، وتذكر هذه السطر ذلك بدل إظهار رصيد صفري.",
  },
  "cap.speech.none": {
    en: "no speaking provider is configured for this deployment", es: "no hay ningún proveedor de voz configurado para esta instalación", fr: "aucun fournisseur vocal n'est configuré pour ce déploiement", de: "für diese Installation ist kein Sprachanbieter eingerichtet", pt: "não há fornecedor de voz configurado para esta instalação", it: "nessun fornitore vocale è configurato per questa installazione", ja: "この配備には音声提供者が設定されていません", zh: "本次部署未配置语音服务提供方", hi: "इस परिनियोजन के लिए कोई वाक् प्रदाता कॉन्फ़िगर नहीं है", ar: "لا يوجد مزوّد صوت مهيّأ لهذا النشر",
  },
  "cap.speech.some": {
    en: "speaking through {provider}", es: "hablando mediante {provider}", fr: "énonce via {provider}", de: "spricht über {provider}", pt: "a falar através de {provider}", it: "parla tramite {provider}", ja: "{provider} を通じて発話", zh: "通过 {provider} 发声", hi: "{provider} के माध्यम से बोल रहा है", ar: "ينطق عبر {provider}",
  },
  "cap.appearance.title": {
    en: "Presented appearance", es: "Apariencia presentada", fr: "Apparence présentée", de: "Dargestellte Erscheinung", pt: "Aparência apresentada", it: "Aspetto presentato", ja: "提示される外観", zh: "呈现的外观", hi: "प्रस्तुत रूप", ar: "المظهر المعروض",
  },
  "cap.appearance.what": {
    en: "The face the Guardian shows in the helper dock — a small pane in the corner of the app that shows and routes, and never acts.", es: "El rostro que el Guardian muestra en el panel auxiliar: un recuadro pequeño en la esquina de la aplicación que muestra y conduce, y nunca actúa.", fr: "Le visage que le Guardian présente dans le bandeau d'assistance : un petit panneau au coin de l'application, qui affiche et oriente, et n'agit jamais.", de: "Das Gesicht, das der Guardian im Hilfsfenster zeigt — eine kleine Fläche in der Ecke der Anwendung, die anzeigt und weiterleitet und nie handelt.", pt: "O rosto que o Guardian mostra no painel auxiliar — um pequeno painel ao canto da aplicação, que mostra e encaminha, e nunca age.", it: "Il volto che il Guardian mostra nel riquadro di assistenza — un piccolo pannello nell'angolo dell'applicazione, che mostra e indirizza, e non agisce mai.", ja: "Guardian がヘルパードックに表示する顔。アプリの隅にある小さな枠で、表示と案内のみを行い、操作は一切行いません。", zh: "Guardian 在助手停靠面板中呈现的面孔——位于应用一角的小窗格，只做展示与跳转，从不执行操作。", hi: "सहायक डॉक में Guardian जो चेहरा दिखाता है — ऐप के कोने में एक छोटा फलक, जो दिखाता और मार्ग देता है, कभी कार्य नहीं करता।", ar: "الوجه الذي يعرضه الـ Guardian في لوحة المساعدة — لوحة صغيرة في زاوية التطبيق، تعرض وتوجّه، ولا تفعل شيئًا أبدًا.",
  },
  "cap.appearance.rests": {
    en: "A face chosen by the account holder. Until one is chosen the dock stays behind the helper button.", es: "Un rostro elegido por la persona titular de la cuenta. Hasta que se elija uno, el panel permanece tras el botón de ayuda.", fr: "Un visage choisi par le titulaire du compte. Tant qu'aucun n'est choisi, le bandeau reste derrière le bouton d'aide.", de: "Ein von der kontoführenden Person gewähltes Gesicht. Bis eines gewählt ist, bleibt das Fenster hinter der Hilfeschaltfläche.", pt: "Um rosto escolhido pela pessoa titular da conta. Até que um seja escolhido, o painel permanece atrás do botão de ajuda.", it: "Un volto scelto dal titolare dell'account. Finché non ne è scelto uno, il riquadro resta dietro il pulsante di aiuto.", ja: "アカウント保有者が選んだ顔。選ばれるまで、ドックはヘルプボタンの背後にとどまります。", zh: "由账户持有人选定的面孔。在选定之前，该面板始终留在帮助按钮之后。", hi: "खाताधारक द्वारा चुना गया चेहरा। जब तक एक चुना न जाए, डॉक सहायता बटन के पीछे ही रहता है।", ar: "وجه يختاره صاحب الحساب. وإلى أن يُختار واحد تبقى اللوحة خلف زر المساعدة.",
  },
  "cap.appearance.none": {
    en: "no face chosen", es: "no se ha elegido rostro", fr: "aucun visage choisi", de: "kein Gesicht gewählt", pt: "nenhum rosto escolhido", it: "nessun volto scelto", ja: "顔は選ばれていません", zh: "未选定面孔", hi: "कोई चेहरा नहीं चुना गया", ar: "لم يُختَر أي وجه",
  },
  "cap.appearance.some": {
    en: "showing face {face}", es: "mostrando el rostro {face}", fr: "affiche le visage {face}", de: "zeigt Gesicht {face}", pt: "a mostrar o rosto {face}", it: "mostra il volto {face}", ja: "顔 {face} を表示中", zh: "正在显示面孔 {face}", hi: "चेहरा {face} दिखा रहा है", ar: "يعرض الوجه {face}",
  },
  "cap.body.title": {
    en: "Physical embodiment", es: "Encarnación física", fr: "Incarnation physique", de: "Physische Verkörperung", pt: "Encarnação física", it: "Incarnazione fisica", ja: "物理的な身体の付与", zh: "实体化载体", hi: "भौतिक मूर्तरूप", ar: "التجسيد المادي",
  },
  "cap.body.what": {
    en: "A robot bound to this account as a guardian responder. It registers as a device, so an escalation dispatches to it like any other, with a directive appropriate to its kind.", es: "Un robot vinculado a esta cuenta como respondedor del Guardian. Se registra como dispositivo, de modo que un escalado se le despacha como a cualquier otro, con una directiva apropiada a su tipo.", fr: "Un robot rattaché à ce compte comme intervenant du Guardian. Il s'enregistre comme appareil, de sorte qu'une escalade lui est adressée comme à tout autre, avec une directive adaptée à son type.", de: "Ein Roboter, der diesem Konto als Guardian-Einsatzmittel zugeordnet ist. Er meldet sich als Gerät an, sodass eine Eskalation ihn wie jedes andere erreicht, mit einer seiner Art angemessenen Anweisung.", pt: "Um robô associado a esta conta como respondedor do Guardian. Regista-se como dispositivo, pelo que um escalonamento lhe é despachado como a qualquer outro, com uma diretiva adequada ao seu tipo.", it: "Un robot associato a questo account come soccorritore del Guardian. Si registra come dispositivo, così un'escalation gli viene inoltrata come a ogni altro, con una direttiva adeguata al suo tipo.", ja: "この口座に guardian responder として結び付けられたロボット。機器として登録されるため、エスカレーションは他の機器と同様にその種別に応じた指示とともに送られます。", zh: "绑定至本账户、作为 Guardian 响应装置的机器人。它以设备身份注册，因此升级事件会像分派给其他设备一样分派给它，并附带与其类型相称的指令。", hi: "इस खाते से guardian responder के रूप में जुड़ा एक रोबोट। यह एक उपकरण के रूप में पंजीकृत होता है, इसलिए कोई भी एस्केलेशन इसे अन्य उपकरणों की तरह ही, इसके प्रकार के अनुरूप निर्देश सहित भेजा जाता है।", ar: "روبوت مرتبط بهذا الحساب بوصفه مستجيبًا للـ Guardian. يُسجَّل كجهاز، فيُرسل إليه التصعيد كما يُرسل إلى أي جهاز آخر، مع توجيه يناسب نوعه.",
  },
  "cap.body.rests": {
    en: "An explicit binding to a named platform from the published catalogue. Only platforms that are shipping or open for preorder can be bound; an announced one is refused by name.", es: "Una vinculación explícita a una plataforma nombrada del catálogo publicado. Solo pueden vincularse plataformas en venta o en reserva; una simplemente anunciada se rechaza indicando su estado.", fr: "Un rattachement explicite à une plateforme nommée du catalogue publié. Seules les plateformes commercialisées ou ouvertes à la précommande peuvent être rattachées ; une plateforme seulement annoncée est refusée en la nommant.", de: "Eine ausdrückliche Zuordnung zu einer benannten Plattform aus dem veröffentlichten Katalog. Zuordnen lassen sich nur Plattformen, die ausgeliefert werden oder vorbestellbar sind; eine nur angekündigte wird unter Nennung ihres Status abgelehnt.", pt: "Uma associação explícita a uma plataforma nomeada do catálogo publicado. Só podem ser associadas plataformas à venda ou em pré-venda; uma apenas anunciada é recusada pelo nome.", it: "Un vincolo esplicito a una piattaforma nominata dal catalogo pubblicato. Possono essere vincolate solo piattaforme in vendita o prenotabili; una soltanto annunciata è rifiutata indicandone lo stato.", ja: "公開カタログに載る特定機種への明示的な結び付け。出荷中または予約受付中の機種のみを結び付けられます。発表のみの機種は、その状態を挙げて拒否されます。", zh: "与已公布目录中某一具名平台的明确绑定。仅可绑定已发货或已开放预订的平台；仅处于发布阶段的平台会被指名拒绝。", hi: "प्रकाशित सूची में से किसी नामित प्लेटफ़ॉर्म से स्पष्ट बंधन। केवल बिक्री पर या प्री-ऑर्डर हेतु खुले प्लेटफ़ॉर्म ही बाँधे जा सकते हैं; मात्र घोषित प्लेटफ़ॉर्म को नाम लेकर अस्वीकार किया जाता है।", ar: "ارتباط صريح بمنصّة مسمّاة من الفهرس المنشور. ولا يمكن ربط سوى المنصّات المتاحة للشحن أو المفتوحة للحجز المسبق؛ أمّا المعلَن عنها فحسب فتُرفض مع ذكر اسمها.",
  },
  "cap.body.none": {
    en: "no body bound", es: "ningún cuerpo vinculado", fr: "aucun corps rattaché", de: "kein Körper zugeordnet", pt: "nenhum corpo associado", it: "nessun corpo vincolato", ja: "身体は結び付けられていません", zh: "未绑定任何载体", hi: "कोई मूर्तरूप नहीं बाँधा गया", ar: "لا جسد مرتبط",
  },
  "cap.body.some": {
    en: "{n} bound — {names}", es: "{n} vinculados — {names}", fr: "{n} rattachés — {names}", de: "{n} zugeordnet — {names}", pt: "{n} associados — {names}", it: "{n} vincolati — {names}", ja: "{n} 台を結び付け済み — {names}", zh: "已绑定 {n} 台 — {names}", hi: "{n} बाँधे गए — {names}", ar: "{n} مرتبط — {names}",
  },
  "cap.movement.title": {
    en: "Locomotion directives", es: "Directivas de desplazamiento", fr: "Directives de déplacement", de: "Fortbewegungsanweisungen", pt: "Diretivas de deslocação", it: "Direttive di locomozione", ja: "移動の指示", zh: "移动指令", hi: "गमन निर्देश", ar: "توجيهات التنقّل",
  },
  "cap.movement.what": {
    en: "The movement a bound body may be told to make — come, follow, patrol, dock, stop — checked against a per-platform allowlist before anything reaches the robot.", es: "El movimiento que puede ordenarse a un cuerpo vinculado —venir, seguir, patrullar, acoplarse, detenerse— cotejado con una lista blanca propia de cada plataforma antes de que nada llegue al robot.", fr: "Le déplacement qu'un corps rattaché peut recevoir l'ordre d'effectuer — venir, suivre, patrouiller, s'amarrer, s'arrêter — vérifié contre une liste d'autorisation propre à la plateforme avant que quoi que ce soit n'atteigne le robot.", de: "Die Bewegung, zu der ein zugeordneter Körper angewiesen werden darf — kommen, folgen, patrouillieren, andocken, anhalten — geprüft gegen eine plattformeigene Positivliste, bevor irgendetwas den Roboter erreicht.", pt: "O movimento que um corpo associado pode ser mandado fazer — vir, seguir, patrulhar, acoplar, parar — confrontado com uma lista de permissões própria de cada plataforma antes de algo chegar ao robô.", it: "Il movimento che un corpo vincolato può ricevere l'ordine di compiere — venire, seguire, pattugliare, agganciarsi, fermarsi — verificato contro un elenco di consenso proprio della piattaforma prima che alcunché raggiunga il robot.", ja: "結び付けられた身体に指示できる動き — 来る、追従する、巡回する、ドックに戻る、停止する — は、ロボットに届く前に機種ごとの許可一覧と照合されます。", zh: "可命令已绑定载体执行的移动——前来、跟随、巡查、归位、停止——在任何指令抵达机器人之前，都会先与该平台专属的允许清单比对。", hi: "बाँधे गए मूर्तरूप को जो गति करने को कहा जा सकता है — आना, पीछे चलना, गश्त करना, डॉक होना, रुकना — रोबोट तक कुछ भी पहुँचने से पहले प्रति-प्लेटफ़ॉर्म अनुमति-सूची से जाँची जाती है।", ar: "الحركة التي يجوز أن يُؤمر بها جسد مرتبط — الإقبال والمتابعة والتجوال والرسوّ والتوقّف — تُطابَق مع قائمة سماح خاصّة بكل منصّة قبل أن يصل شيء إلى الروبوت.",
  },
  "cap.movement.rests": {
    en: "A bound body with mobility among its capabilities. This is not a separate switch: with no body bound there is nothing that could be told to move.", es: "Un cuerpo vinculado que tenga movilidad entre sus capacidades. No es un interruptor aparte: sin un cuerpo vinculado no hay nada a lo que pueda ordenarse moverse.", fr: "Un corps rattaché dont les capacités comprennent la mobilité. Ce n'est pas un interrupteur distinct : sans corps rattaché, rien ne peut recevoir l'ordre de se déplacer.", de: "Ein zugeordneter Körper, zu dessen Fähigkeiten Mobilität zählt. Das ist kein eigener Schalter: ohne zugeordneten Körper gibt es nichts, das zur Bewegung angewiesen werden könnte.", pt: "Um corpo associado com mobilidade entre as suas capacidades. Não é um interruptor à parte: sem corpo associado não há nada a que se possa mandar mover.", it: "Un corpo vincolato che abbia la mobilità fra le proprie capacità. Non è un interruttore a sé: senza un corpo vincolato non c'è nulla a cui si possa ordinare di muoversi.", ja: "移動性を備えた、結び付け済みの身体。これは独立した切り替えではありません。身体が結び付けられていなければ、動くよう指示できる対象自体が存在しません。", zh: "具备移动能力且已绑定的载体。这并非一个独立开关：未绑定载体时，根本不存在可被命令移动的对象。", hi: "ऐसा बाँधा गया मूर्तरूप जिसकी क्षमताओं में गतिशीलता हो। यह कोई अलग स्विच नहीं है: कोई मूर्तरूप बाँधा न हो तो ऐसा कुछ है ही नहीं जिसे चलने को कहा जा सके।", ar: "جسد مرتبط تندرج الحركة ضمن قدراته. وليس هذا مفتاحًا مستقلًّا: فمن دون جسد مرتبط لا يوجد ما يمكن أن يُؤمر بالتحرّك.",
  },
  "cap.movement.none": {
    en: "nothing bound that could be told to move", es: "no hay nada vinculado a lo que pueda ordenarse moverse", fr: "rien de rattaché ne peut recevoir l'ordre de se déplacer", de: "nichts zugeordnet, das zur Bewegung angewiesen werden könnte", pt: "nada associado a que se possa mandar mover", it: "nulla di vincolato a cui si possa ordinare di muoversi", ja: "動くよう指示できる結び付けはありません", zh: "未绑定任何可被命令移动的对象", hi: "ऐसा कुछ नहीं बाँधा गया जिसे चलने को कहा जा सके", ar: "لا شيء مرتبط يمكن أن يُؤمر بالتحرّك",
  },
  "cap.movement.some": {
    en: "limited to the bound platform's own list", es: "limitado a la lista propia de la plataforma vinculada", fr: "limité à la liste propre de la plateforme rattachée", de: "beschränkt auf die eigene Liste der zugeordneten Plattform", pt: "limitado à lista própria da plataforma associada", it: "limitato all'elenco proprio della piattaforma vincolata", ja: "結び付けた機種自身の一覧に限定されます", zh: "仅限于所绑定平台自身的清单", hi: "बाँधे गए प्लेटफ़ॉर्म की अपनी सूची तक सीमित", ar: "مقصور على قائمة المنصّة المرتبطة نفسها",
  },
  "cap.observation.title": {
    en: "Screen observation", es: "Observación de pantalla", fr: "Observation d'écran", de: "Bildschirmbeobachtung", pt: "Observação de ecrã", it: "Osservazione dello schermo", ja: "画面の観察", zh: "屏幕观察", hi: "स्क्रीन अवलोकन", ar: "مراقبة الشاشة",
  },
  "cap.observation.what": {
    en: "Reading a screen without acting on it. Text found on a screen is treated as data and can never widen what is allowed, whatever that text claims.", es: "Leer una pantalla sin actuar sobre ella. El texto hallado en una pantalla se trata como dato y nunca puede ampliar lo permitido, sea lo que sea que ese texto afirme.", fr: "Lire un écran sans agir dessus. Le texte trouvé sur un écran est traité comme une donnée et ne peut jamais élargir ce qui est permis, quoi que ce texte prétende.", de: "Einen Bildschirm lesen, ohne auf ihm zu handeln. Text auf einem Bildschirm gilt als Datum und kann das Erlaubte nie erweitern, was dieser Text auch behauptet.", pt: "Ler um ecrã sem agir sobre ele. O texto encontrado num ecrã é tratado como dado e nunca pode alargar o que é permitido, seja o que for que esse texto afirme.", it: "Leggere uno schermo senza agirvi. Il testo trovato su uno schermo è trattato come dato e non può mai ampliare ciò che è consentito, qualunque cosa quel testo affermi.", ja: "画面を操作せずに読み取ること。画面上の文字はデータとして扱われ、そこに何が書かれていようと、許可された範囲を広げることはできません。", zh: "只读取屏幕而不对其操作。屏幕上出现的文字被视为数据，无论其声称什么，都绝不能扩大已获许可的范围。", hi: "स्क्रीन पर कार्य किए बिना उसे पढ़ना। स्क्रीन पर मिला पाठ डेटा माना जाता है और वह जो भी दावा करे, अनुमत सीमा को कभी नहीं बढ़ा सकता।", ar: "قراءة شاشة دون التصرّف فيها. ويُعامَل النص الوارد على الشاشة بوصفه بيانات، ولا يمكنه قطّ توسيع ما هو مسموح به مهما ادّعى.",
  },
  "cap.observation.rests": {
    en: "A look permit naming its applications, its minutes and its steps. A wildcard is refused.", es: "Un permiso de observación que nombre sus aplicaciones, sus minutos y sus pasos. Un comodín se rechaza.", fr: "Une autorisation de lecture nommant ses applications, ses minutes et ses étapes. Un joker est refusé.", de: "Eine Leseerlaubnis, die ihre Anwendungen, ihre Minuten und ihre Schritte benennt. Ein Platzhalter wird abgelehnt.", pt: "Uma permissão de observação que nomeie as suas aplicações, os seus minutos e os seus passos. Um caráter universal é recusado.", it: "Un permesso di lettura che nomini le proprie applicazioni, i propri minuti e i propri passi. Un carattere jolly è rifiutato.", ja: "対象アプリ、分数、手数を明示した閲覧許可。ワイルドカードは拒否されます。", zh: "一份指明其应用范围、分钟数与步数的观察许可。通配符一律拒绝。", hi: "एक अवलोकन अनुमति जो अपने अनुप्रयोग, अपने मिनट और अपने चरण नाम से बताए। वाइल्डकार्ड अस्वीकार किया जाता है।", ar: "إذن اطّلاع يسمّي تطبيقاته ودقائقه وخطواته. ويُرفض رمز الشمول.",
  },
  "cap.observation.none": {
    en: "no look permit is live", es: "no hay ningún permiso de observación vigente", fr: "aucune autorisation de lecture n'est en cours", de: "keine Leseerlaubnis ist aktiv", pt: "nenhuma permissão de observação está em vigor", it: "nessun permesso di lettura è attivo", ja: "有効な閲覧許可はありません", zh: "当前没有生效的观察许可", hi: "कोई अवलोकन अनुमति सक्रिय नहीं है", ar: "لا يوجد إذن اطّلاع سارٍ",
  },
  "cap.observation.some": {
    en: "{n} live", es: "{n} vigentes", fr: "{n} en cours", de: "{n} aktiv", pt: "{n} em vigor", it: "{n} attivi", ja: "{n} 件が有効", zh: "{n} 项生效中", hi: "{n} सक्रिय", ar: "{n} سارٍ",
  },
  "cap.operation.title": {
    en: "Interface operation", es: "Manejo de la interfaz", fr: "Manipulation d'interface", de: "Bedienung der Oberfläche", pt: "Manuseio da interface", it: "Uso dell'interfaccia", ja: "画面操作", zh: "界面操作", hi: "इंटरफ़ेस संचालन", ar: "تشغيل الواجهة",
  },
  "cap.operation.what": {
    en: "Working a screen — moving a pointer, pressing a control, typing into a field — under a grant bounded in applications, moves, minutes and steps.", es: "Manejar una pantalla —mover un puntero, pulsar un control, escribir en un campo— bajo una concesión acotada en aplicaciones, movimientos, minutos y pasos.", fr: "Manipuler un écran — déplacer un pointeur, actionner un contrôle, saisir dans un champ — sous une autorisation bornée en applications, gestes, minutes et étapes.", de: "Einen Bildschirm bedienen — einen Zeiger bewegen, ein Element betätigen, in ein Feld schreiben — unter einer Erlaubnis, die in Anwendungen, Aktionen, Minuten und Schritten begrenzt ist.", pt: "Manusear um ecrã — mover um ponteiro, premir um controlo, escrever num campo — ao abrigo de uma concessão limitada em aplicações, movimentos, minutos e passos.", it: "Operare uno schermo — muovere un puntatore, premere un comando, scrivere in un campo — sotto una concessione limitata in applicazioni, azioni, minuti e passi.", ja: "画面を操作すること — ポインターを動かす、コントロールを押す、欄に入力する — 対象アプリ、動作、分数、手数で限られた許可のもとで行われます。", zh: "操作屏幕——移动指针、按下控件、在字段中输入——均在按应用、动作、分钟数与步数设限的授权之下进行。", hi: "स्क्रीन चलाना — पॉइंटर हिलाना, कोई नियंत्रण दबाना, किसी क्षेत्र में टाइप करना — ऐसी स्वीकृति के अधीन जो अनुप्रयोगों, क्रियाओं, मिनटों और चरणों में सीमित हो।", ar: "تشغيل شاشة — تحريك مؤشّر، والضغط على عنصر، والكتابة في حقل — بموجب إذن محدود بالتطبيقات والحركات والدقائق والخطوات.",
  },
  "cap.operation.rests": {
    en: "A grant naming all four limits, enforced where the move happens rather than on the screen that requested it. It never types passwords, PINs, one-time codes, card numbers or recovery phrases, and says so instead of trying.", es: "Una concesión que nombre los cuatro límites, aplicada allí donde ocurre el movimiento y no en la pantalla que lo pidió. Nunca escribe contraseñas, PIN, códigos de un solo uso, números de tarjeta ni frases de recuperación: lo dice en lugar de intentarlo.", fr: "Une autorisation nommant les quatre limites, appliquée là où le geste a lieu et non sur l'écran qui l'a demandé. Elle ne saisit jamais de mots de passe, de codes PIN, de codes à usage unique, de numéros de carte ni de phrases de récupération, et le dit plutôt que d'essayer.", de: "Eine Erlaubnis, die alle vier Grenzen benennt und dort durchgesetzt wird, wo die Aktion geschieht, nicht auf dem Bildschirm, der sie angefordert hat. Passwörter, PINs, Einmalcodes, Kartennummern und Wiederherstellungsphrasen werden nie getippt; statt eines Versuchs kommt der Hinweis darauf.", pt: "Uma concessão que nomeie os quatro limites, imposta onde o movimento acontece e não no ecrã que o pediu. Nunca escreve palavras-passe, PIN, códigos de uso único, números de cartão ou frases de recuperação, e di-lo em vez de tentar.", it: "Una concessione che nomini tutti e quattro i limiti, applicata dove l'azione avviene e non sulla schermata che l'ha richiesta. Non digita mai password, PIN, codici monouso, numeri di carta o frasi di recupero, e lo dichiara invece di provarci.", ja: "四つの限度をすべて明示した許可であり、要求した画面ではなく動作が起きる場所で適用されます。パスワード、暗証番号、ワンタイムコード、カード番号、復旧フレーズを入力することは決してなく、試みる代わりにその旨を述べます。", zh: "一份指明全部四项限度的授权，且在动作发生之处而非发出请求的页面上予以强制执行。它绝不输入密码、PIN、一次性验证码、卡号或恢复短语，而是如实说明，而非尝试。", hi: "ऐसी स्वीकृति जो चारों सीमाएँ नाम से बताए, और जो अनुरोध करने वाली स्क्रीन पर नहीं, बल्कि जहाँ क्रिया होती है वहाँ लागू की जाए। यह कभी पासवर्ड, पिन, एक-बार कोड, कार्ड नंबर या रिकवरी वाक्यांश टाइप नहीं करती, और प्रयास करने के बजाय यही बताती है।", ar: "إذن يسمّي الحدود الأربعة جميعًا، ويُنفَّذ حيث تقع الحركة لا على الشاشة التي طلبتها. ولا يكتب أبدًا كلمات مرور أو أرقامًا سرّية أو رموزًا لمرّة واحدة أو أرقام بطاقات أو عبارات استرداد، ويصرّح بذلك بدل أن يحاول.",
  },
  "cap.operation.none": {
    en: "no grant to act is live", es: "no hay ninguna concesión de actuación vigente", fr: "aucune autorisation d'agir n'est en cours", de: "keine Handlungserlaubnis ist aktiv", pt: "nenhuma concessão para agir está em vigor", it: "nessuna concessione ad agire è attiva", ja: "有効な操作許可はありません", zh: "当前没有生效的操作授权", hi: "कार्य करने की कोई स्वीकृति सक्रिय नहीं है", ar: "لا يوجد إذن بالتصرّف سارٍ",
  },
  "cap.operation.some": {
    en: "{n} live", es: "{n} vigentes", fr: "{n} en cours", de: "{n} aktiv", pt: "{n} em vigor", it: "{n} attive", ja: "{n} 件が有効", zh: "{n} 项生效中", hi: "{n} सक्रिय", ar: "{n} سارٍ",
  },
  "cap.unattended.title": {
    en: "Unattended operation", es: "Funcionamiento sin supervisión", fr: "Fonctionnement sans surveillance", de: "Unbeaufsichtigter Betrieb", pt: "Funcionamento sem supervisão", it: "Funzionamento non presidiato", ja: "無人での稼働", zh: "无人值守运行", hi: "अनिरीक्षित संचालन", ar: "التشغيل دون إشراف",
  },
  "cap.unattended.what": {
    en: "A session left running: open until it is signed off, acting across the account holder's own records through a written allowlist, with the request that would undo each act recorded beside it.", es: "Una sesión que se deja en marcha: abierta hasta que se cierre, que actúa sobre los registros de la propia persona titular mediante una lista blanca escrita, y que anota junto a cada acto la petición que lo desharía.", fr: "Une session laissée en cours : ouverte jusqu'à sa clôture, agissant sur les propres enregistrements du titulaire au moyen d'une liste d'autorisation écrite, la requête qui annulerait chaque acte étant consignée à côté de lui.", de: "Eine laufen gelassene Sitzung: offen bis zur Abmeldung, tätig auf den eigenen Aufzeichnungen der kontoführenden Person über eine geschriebene Positivliste, wobei neben jeder Handlung die Anfrage steht, die sie rückgängig machen würde.", pt: "Uma sessão deixada a correr: aberta até ser encerrada, agindo sobre os registos da própria pessoa titular através de uma lista de permissões escrita, com o pedido que desfaria cada ato registado ao lado dele.", it: "Una sessione lasciata in esecuzione: aperta finché non viene chiusa, che agisce sui registri del titolare stesso tramite un elenco di consenso scritto, con accanto a ogni atto la richiesta che lo annullerebbe.", ja: "動かしたままにできるセッション。終了操作を行うまで開いており、書かれた許可一覧を通じてアカウント保有者自身の記録に対して動作し、各操作の取り消しに必要な要求がその横に記録されます。", zh: "可持续运行的会话：在签退之前保持开启，通过成文的允许清单对账户持有人自己的记录执行操作，并在每项操作旁记录可将其撤销的请求。", hi: "चालू छोड़ा गया एक सत्र: साइन-ऑफ़ होने तक खुला, लिखित अनुमति-सूची के माध्यम से खाताधारक के अपने ही अभिलेखों पर कार्य करता हुआ, और हर कार्य के साथ वह अनुरोध दर्ज जो उसे पलट देगा।", ar: "جلسة تُترك عاملة: مفتوحة إلى أن تُنهى، تتصرّف في سجلّات صاحب الحساب نفسه عبر قائمة سماح مكتوبة، ويُدوَّن بجانب كل تصرّف الطلبُ الذي يبطله.",
  },
  "cap.unattended.rests": {
    en: "A session the account holder opened, an area they named, and a per-area permit they granted. Every act is listed with its reversal; signing off closes it.", es: "Una sesión abierta por la persona titular, un ámbito que ella nombró y un permiso por ámbito que ella concedió. Cada acto figura junto a su reversión; cerrar la sesión la termina.", fr: "Une session ouverte par le titulaire, un domaine qu'il a nommé et une autorisation par domaine qu'il a accordée. Chaque acte est consigné avec son annulation ; la clôture y met fin.", de: "Eine von der kontoführenden Person geöffnete Sitzung, ein von ihr benannter Bereich und eine von ihr erteilte Erlaubnis je Bereich. Jede Handlung ist mit ihrer Rücknahme verzeichnet; das Abmelden beendet sie.", pt: "Uma sessão aberta pela pessoa titular, uma área que nomeou e uma permissão por área que concedeu. Cada ato consta com a sua reversão; encerrar termina-a.", it: "Una sessione aperta dal titolare, un ambito da lui nominato e un permesso per ambito da lui concesso. Ogni atto è elencato con la sua revoca; la chiusura la termina.", ja: "アカウント保有者が開いたセッション、保有者が指定した領域、および保有者が領域ごとに与えた許可。各操作はその取り消し方とともに記載され、終了操作でセッションは閉じます。", zh: "由账户持有人开启的会话、其指定的范围，以及其按范围授予的许可。每项操作均连同其撤销方式一并列出；签退即结束该会话。", hi: "खाताधारक द्वारा खोला गया सत्र, उनके द्वारा नामित क्षेत्र, और उनके द्वारा प्रति-क्षेत्र दी गई अनुमति। हर कार्य अपने प्रत्यावर्तन सहित सूचीबद्ध है; साइन-ऑफ़ करने पर सत्र बंद हो जाता है।", ar: "جلسة فتحها صاحب الحساب، ومجال سمّاه، وإذن لكل مجال منحه. ويُدرج كل تصرّف مع سبيل الرجوع عنه؛ وإنهاء الجلسة يغلقها.",
  },
  "cap.unattended.none": {
    en: "no session open", es: "ninguna sesión abierta", fr: "aucune session ouverte", de: "keine Sitzung offen", pt: "nenhuma sessão aberta", it: "nessuna sessione aperta", ja: "開いているセッションはありません", zh: "没有开启的会话", hi: "कोई सत्र खुला नहीं है", ar: "لا جلسة مفتوحة",
  },
  "cap.unattended.some": {
    en: "open on {area} — {n} act(s) recorded", es: "abierta en {area} — {n} acto(s) registrado(s)", fr: "ouverte sur {area} — {n} acte(s) consigné(s)", de: "offen zu {area} — {n} Handlung(en) verzeichnet", pt: "aberta em {area} — {n} ato(s) registado(s)", it: "aperta su {area} — {n} atto/i registrato/i", ja: "{area} で開いています — 記録された操作 {n} 件", zh: "在 {area} 上开启 — 已记录 {n} 项操作", hi: "{area} पर खुला — {n} कार्य दर्ज", ar: "مفتوحة على {area} — {n} تصرّف مسجَّل",
  },
};

export function visitorLang(): Lang {
  const asked = typeof navigator === "undefined" ? [] :
    (navigator.languages ?? [navigator.language]).filter(Boolean);
  for (const tag of asked) {
    const base = String(tag).split("-")[0].toLowerCase();
    if (base in LANGS) return base as Lang;
  }
  return "en";
}

const LANGS: Record<string, true> = {
  en: true, es: true, fr: true, de: true, pt: true,
  it: true, ja: true, zh: true, hi: true, ar: true,
};

/** A row with holes in it, filled from the server's slots.
 *
 *  `jim/presence.py` deliberately emits a key and a `{metric: …, days: 3}`
 *  rather than a sentence: a sentence composed on the server is a sentence
 *  exactly one reader can read. This is the other half of that decision. */
export function fill(key: string, lang: Lang,
                     slots: Record<string, string | number>): string {
  return t(key, lang).replace(/\{(\w+)\}/g, (whole, name) =>
    name in slots ? String(slots[name]) : whole);
}

/** The string, in the reader's language, falling back to English per key. */
export function t(key: string, lang: Lang): string {
  const row = TABLE[key];
  if (!row) return key;
  return row[lang] ?? row.en ?? key;
}

/** A word for an identifier the server chose — not for a key a screen wrote.
 *
 *  `t()` falls back to the key, which is right for chrome: a missing row is
 *  a bug and should look like one. It is wrong for a value that arrives over
 *  the wire. If a backend grows a tenth surface this build has never heard
 *  of, rendering `surface.holodeck` is worse than rendering `holodeck` —
 *  the second is at least the thing itself.
 *
 *  So this falls back to the identifier with its underscores opened out, and
 *  the guard over `SURFACES` is what keeps the nine we do know from ever
 *  reaching that path. That is the division of labour: the fallback is for
 *  a server ahead of this build, the guard is for a build that forgot. */
export function word(prefix: string, id: string, lang: Lang): string {
  const key = `${prefix}.${id}`;
  return key in TABLE ? t(key, lang) : String(id ?? "").replace(/_/g, " ");
}

/** A sentence this console can say, falling back to the one the server sent.
 *
 *  For server prose rather than server identifiers. The API has been sending
 *  English notes and rules alongside its enums for several releases, and a
 *  translated label beside an untranslated sentence is half a job. Where a
 *  row exists it wins; where it does not, the English the server sent is
 *  still better than an empty span. */
export function phrase(key: string, lang: Lang, fallback: string): string {
  return key in TABLE ? t(key, lang) : fallback;
}
