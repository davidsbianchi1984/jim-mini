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
  "spec.ask": { en: "Ask them", es: "Preguntarles", fr: "Leur demander", de: "Sie fragen", pt: "Perguntar-lhes", it: "Chiedi a loro", ja: "\u3053\u306e\u4eba\u306b\u805e\u304f", zh: "\u53bb\u95ee\u4ed6\u4eec", hi: "\u0909\u0928\u0938\u0947 \u092a\u0942\u091b\u0947\u0902", ar: "\u0627\u0633\u0623\u0644\u0647\u0645" },
  "spec.fallback": { en: "Specialist", es: "Especialista", fr: "Sp\u00e9cialiste", de: "Fachperson", pt: "Especialista", it: "Specialista", ja: "\u5c02\u9580\u5bb6", zh: "\u4e13\u5bb6", hi: "\u0935\u093f\u0936\u0947\u0937\u091c\u094d\u091e", ar: "\u0627\u0644\u0645\u062e\u062a\u0635" },
  "spec.held": { en: "Their reply is waiting for its owner to approve it \u2014 held, not refused.", es: "Su respuesta espera la aprobaci\u00f3n de su propietario: retenida, no rechazada.", fr: "Leur r\u00e9ponse attend l'approbation de son propri\u00e9taire : retenue, pas refus\u00e9e.", de: "Ihre Antwort wartet auf die Freigabe ihres Eigent\u00fcmers \u2014 zur\u00fcckgehalten, nicht abgelehnt.", pt: "A resposta aguarda a aprova\u00e7\u00e3o do seu propriet\u00e1rio \u2014 retida, n\u00e3o recusada.", it: "La loro risposta attende l'approvazione del proprietario: trattenuta, non rifiutata.", ja: "\u8fd4\u4fe1\u306f\u30aa\u30fc\u30ca\u30fc\u306e\u627f\u8a8d\u5f85\u3061\u3067\u3059 \u2014 \u62d2\u5426\u3067\u306f\u306a\u304f\u4fdd\u7559\u3055\u308c\u3066\u3044\u307e\u3059\u3002", zh: "\u4ed6\u4eec\u7684\u56de\u590d\u6b63\u5728\u7b49\u5f85\u5176\u6240\u6709\u8005\u6279\u51c6 \u2014 \u662f\u88ab\u6682\u5b58\uff0c\u800c\u4e0d\u662f\u88ab\u62d2\u7edd\u3002", hi: "\u0909\u0928\u0915\u093e \u0909\u0924\u094d\u0924\u0930 \u0909\u0938\u0915\u0947 \u0938\u094d\u0935\u093e\u092e\u0940 \u0915\u0940 \u092e\u0902\u091c\u093c\u0942\u0930\u0940 \u0915\u0940 \u092a\u094d\u0930\u0924\u0940\u0915\u094d\u0937\u093e \u092e\u0947\u0902 \u0939\u0948 \u2014 \u0930\u094b\u0915\u093e \u0917\u092f\u093e \u0939\u0948, \u0905\u0938\u094d\u0935\u0940\u0915\u093e\u0930 \u0928\u0939\u0940\u0902\u0964", ar: "\u0631\u062f\u0651\u0647\u0645 \u0628\u0627\u0646\u062a\u0638\u0627\u0631 \u0645\u0648\u0627\u0641\u0642\u0629 \u0645\u0627\u0644\u0643\u0647 \u2014 \u0645\u062d\u062c\u0648\u0632\u060c \u0644\u0627 \u0645\u0631\u0641\u0648\u0636." },
  "spec.shared": { en: "Shared", es: "Se comparti\u00f3", fr: "Partag\u00e9", de: "Geteilt", pt: "Partilhado", it: "Condiviso", ja: "\u5171\u6709\u3057\u305f\u5185\u5bb9", zh: "\u5df2\u5171\u4eab", hi: "\u0938\u093e\u091d\u093e \u0915\u093f\u092f\u093e \u0917\u092f\u093e", ar: "\u0645\u0627 \u062a\u0645\u062a \u0645\u0634\u0627\u0631\u0643\u062a\u0647" },
  "spec.via": { en: "through the tandem", es: "a trav\u00e9s del t\u00e1ndem", fr: "via le tandem", de: "\u00fcber das Tandem", pt: "atrav\u00e9s do tandem", it: "tramite il tandem", ja: "\u30bf\u30f3\u30c7\u30e0\u7d4c\u7531", zh: "\u901a\u8fc7\u53cc\u8054", hi: "\u091f\u0948\u0902\u0921\u092e \u0915\u0947 \u092e\u093e\u0927\u094d\u092f\u092e \u0938\u0947", ar: "\u0639\u0628\u0631 \u0627\u0644\u0627\u0642\u062a\u0631\u0627\u0646" },
  "cont.title": { en: "What carries between sessions", es: "Lo que se mantiene entre sesiones", fr: "Ce qui persiste d'une session \u00e0 l'autre", de: "Was zwischen den Sitzungen bleibt", pt: "O que se mant\u00e9m entre sess\u00f5es", it: "Ci\u00f2 che resta tra una sessione e l'altra", ja: "\u30bb\u30c3\u30b7\u30e7\u30f3\u3092\u307e\u305f\u3044\u3067\u6b8b\u308b\u3082\u306e", zh: "\u5728\u4e0d\u540c\u4f1a\u8bdd\u4e4b\u95f4\u5ef6\u7eed\u7684\u90e8\u5206", hi: "\u091c\u094b \u0938\u0924\u094d\u0930\u094b\u0902 \u0915\u0947 \u092c\u0940\u091a \u092c\u0928\u093e \u0930\u0939\u0924\u093e \u0939\u0948", ar: "\u0645\u0627 \u064a\u0628\u0642\u0649 \u0628\u064a\u0646 \u0627\u0644\u062c\u0644\u0633\u0627\u062a" },
  "cont.lead": { en: "The profile above is a snapshot you rebuild. This is the part that moves on its own \u2014 it shifts a little every time you check in, talk to the coach, or say whether guidance helped, so the Guardian does not meet you on your fortieth day the way it met you on your first.", es: "El perfil de arriba es una instant\u00e1nea que t\u00fa reconstruyes. Esta es la parte que se mueve sola: cambia un poco cada vez que registras c\u00f3mo est\u00e1s, hablas con el coach o dices si la orientaci\u00f3n ayud\u00f3, para que el Guardi\u00e1n no te reciba en tu d\u00eda cuarenta como te recibi\u00f3 el primero.", fr: "Le profil ci-dessus est un instantan\u00e9 que vous reconstruisez. Voici la partie qui \u00e9volue d'elle-m\u00eame : elle change un peu chaque fois que vous faites un bilan, parlez au coach ou dites si les conseils ont aid\u00e9, pour que le Gardien ne vous accueille pas au quaranti\u00e8me jour comme au premier.", de: "Das Profil oben ist eine Momentaufnahme, die Sie neu erstellen. Dies ist der Teil, der sich von selbst bewegt \u2014 er verschiebt sich ein wenig, sooft Sie einen Check-in machen, mit dem Coach sprechen oder sagen, ob die Hinweise geholfen haben, damit der Guardian Ihnen am vierzigsten Tag nicht so begegnet wie am ersten.", pt: "O perfil acima \u00e9 um instant\u00e2neo que reconstr\u00f3i. Esta \u00e9 a parte que se move sozinha \u2014 muda um pouco sempre que faz um check-in, fala com o coach ou diz se a orienta\u00e7\u00e3o ajudou, para que o Guardi\u00e3o n\u00e3o o receba no quadrag\u00e9simo dia como o recebeu no primeiro.", it: "Il profilo qui sopra \u00e8 un'istantanea che ricostruisci tu. Questa \u00e8 la parte che si muove da sola: cambia un po' ogni volta che fai un check-in, parli con il coach o dici se i consigli hanno aiutato, cos\u00ec il Guardian non ti accoglie al quarantesimo giorno come al primo.", ja: "\u4e0a\u306e\u30d7\u30ed\u30d5\u30a3\u30fc\u30eb\u306f\u3001\u3042\u306a\u305f\u304c\u4f5c\u308a\u76f4\u3059\u30b9\u30ca\u30c3\u30d7\u30b7\u30e7\u30c3\u30c8\u3067\u3059\u3002\u3053\u3061\u3089\u306f\u81ea\u7136\u306b\u52d5\u304f\u90e8\u5206\u3067\u3001\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u3001\u30b3\u30fc\u30c1\u3068\u306e\u4f1a\u8a71\u3001\u52a9\u8a00\u304c\u5f79\u306b\u7acb\u3063\u305f\u304b\u306e\u56de\u7b54\u306e\u305f\u3073\u306b\u5c11\u3057\u305a\u3064\u5909\u308f\u308a\u307e\u3059\u3002\u56db\u5341\u65e5\u76ee\u306e\u3042\u306a\u305f\u3092\u3001\u4e00\u65e5\u76ee\u3068\u540c\u3058\u3088\u3046\u306b\u306f\u8fce\u3048\u307e\u305b\u3093\u3002", zh: "\u4e0a\u9762\u7684\u6863\u6848\u662f\u4f60\u624b\u52a8\u91cd\u5efa\u7684\u5feb\u7167\u3002\u8fd9\u91cc\u662f\u4f1a\u81ea\u884c\u53d8\u5316\u7684\u90e8\u5206 \u2014 \u6bcf\u6b21\u4f60\u7b7e\u5230\u3001\u4e0e\u6559\u7ec3\u4ea4\u8c08\u6216\u8bf4\u660e\u5efa\u8bae\u662f\u5426\u6709\u5e2e\u52a9\u65f6\uff0c\u5b83\u90fd\u4f1a\u7565\u5fae\u79fb\u52a8\uff0c\u8ba9\u5b88\u62a4\u8005\u5728\u7b2c\u56db\u5341\u5929\u4e0d\u4f1a\u7528\u7b2c\u4e00\u5929\u7684\u65b9\u5f0f\u6765\u8fce\u63a5\u4f60\u3002", hi: "\u090a\u092a\u0930 \u0915\u0940 \u092a\u094d\u0930\u094b\u092b\u093c\u093e\u0907\u0932 \u090f\u0915 \u0938\u094d\u0928\u0948\u092a\u0936\u0949\u091f \u0939\u0948 \u091c\u093f\u0938\u0947 \u0906\u092a \u092b\u093f\u0930 \u0938\u0947 \u092c\u0928\u093e\u0924\u0947 \u0939\u0948\u0902\u0964 \u092f\u0939 \u0935\u0939 \u0939\u093f\u0938\u094d\u0938\u093e \u0939\u0948 \u091c\u094b \u0905\u092a\u0928\u0947 \u0906\u092a \u092c\u0926\u0932\u0924\u093e \u0939\u0948 \u2014 \u0939\u0930 \u092c\u093e\u0930 \u091c\u092c \u0906\u092a \u091a\u0947\u0915-\u0907\u0928 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902, \u0915\u094b\u091a \u0938\u0947 \u092c\u093e\u0924 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902, \u092f\u093e \u092c\u0924\u093e\u0924\u0947 \u0939\u0948\u0902 \u0915\u093f \u092e\u093e\u0930\u094d\u0917\u0926\u0930\u094d\u0936\u0928 \u0938\u0947 \u092e\u0926\u0926 \u092e\u093f\u0932\u0940 \u092f\u093e \u0928\u0939\u0940\u0902, \u092f\u0939 \u0925\u094b\u0921\u093c\u093e \u0916\u093f\u0938\u0915\u0924\u093e \u0939\u0948, \u0924\u093e\u0915\u093f \u0917\u093e\u0930\u094d\u091c\u093f\u092f\u0928 \u0906\u092a\u0915\u0947 \u091a\u093e\u0932\u0940\u0938\u0935\u0947\u0902 \u0926\u093f\u0928 \u0906\u092a\u0938\u0947 \u0935\u0948\u0938\u0947 \u0928 \u092e\u093f\u0932\u0947 \u091c\u0948\u0938\u0947 \u092a\u0939\u0932\u0947 \u0926\u093f\u0928 \u092e\u093f\u0932\u093e \u0925\u093e\u0964", ar: "\u0627\u0644\u0645\u0644\u0641 \u0623\u0639\u0644\u0627\u0647 \u0644\u0642\u0637\u0629 \u062a\u0639\u064a\u062f \u0628\u0646\u0627\u0621\u0647\u0627 \u0628\u0646\u0641\u0633\u0643. \u0623\u0645\u0651\u0627 \u0647\u0630\u0627 \u0641\u0647\u0648 \u0627\u0644\u062c\u0632\u0621 \u0627\u0644\u0630\u064a \u064a\u062a\u062d\u0631\u0643 \u0645\u0646 \u062a\u0644\u0642\u0627\u0621 \u0646\u0641\u0633\u0647 \u2014 \u064a\u062a\u063a\u064a\u0651\u0631 \u0642\u0644\u064a\u0644\u064b\u0627 \u0641\u064a \u0643\u0644 \u0645\u0631\u0629 \u062a\u0633\u062c\u0651\u0644 \u0641\u064a\u0647\u0627 \u062d\u0627\u0644\u062a\u0643\u060c \u0623\u0648 \u062a\u062a\u062d\u062f\u062b \u0625\u0644\u0649 \u0627\u0644\u0645\u062f\u0631\u0651\u0628\u060c \u0623\u0648 \u062a\u0642\u0648\u0644 \u0625\u0646 \u0627\u0644\u0625\u0631\u0634\u0627\u062f \u0642\u062f \u0633\u0627\u0639\u062f\u060c \u062d\u062a\u0649 \u0644\u0627 \u064a\u0633\u062a\u0642\u0628\u0644\u0643 \u0627\u0644\u062d\u0627\u0631\u0633 \u0641\u064a \u064a\u0648\u0645\u0643 \u0627\u0644\u0623\u0631\u0628\u0639\u064a\u0646 \u0643\u0645\u0627 \u0627\u0633\u062a\u0642\u0628\u0644\u0643 \u0641\u064a \u064a\u0648\u0645\u0643 \u0627\u0644\u0623\u0648\u0644." },
  "cont.observations": { en: "observations", es: "observaciones", fr: "observations", de: "Beobachtungen", pt: "observa\u00e7\u00f5es", it: "osservazioni", ja: "\u4ef6\u306e\u89b3\u6e2c", zh: "\u6b21\u89c2\u5bdf", hi: "\u0905\u0935\u0932\u094b\u0915\u0928", ar: "\u0645\u0644\u0627\u062d\u0638\u0629" },
  "cont.shaping": { en: "shaping how the coach answers", es: "influye en c\u00f3mo responde el coach", fr: "influence la fa\u00e7on dont le coach r\u00e9pond", de: "beeinflusst, wie der Coach antwortet", pt: "influencia como o coach responde", it: "influenza come risponde il coach", ja: "\u30b3\u30fc\u30c1\u306e\u7b54\u3048\u65b9\u306b\u53cd\u6620\u3055\u308c\u3066\u3044\u307e\u3059", zh: "\u6b63\u5728\u5f71\u54cd\u6559\u7ec3\u7684\u56de\u7b54\u65b9\u5f0f", hi: "\u0915\u094b\u091a \u0915\u0947 \u0909\u0924\u094d\u0924\u0930 \u0926\u0947\u0928\u0947 \u0915\u0947 \u0924\u0930\u0940\u0915\u0947 \u0915\u094b \u0906\u0915\u093e\u0930 \u0926\u0947 \u0930\u0939\u093e \u0939\u0948", ar: "\u064a\u0624\u062b\u0631 \u0641\u064a \u0637\u0631\u064a\u0642\u0629 \u0631\u062f \u0627\u0644\u0645\u062f\u0631\u0651\u0628" },
  "cont.not_yet": { en: "not shaping anything yet \u2014 too little to mean much", es: "todav\u00eda no influye en nada: hay muy poco para significar algo", fr: "n'influence encore rien \u2014 trop peu pour vouloir dire grand-chose", de: "beeinflusst noch nichts \u2014 zu wenig, um etwas zu bedeuten", pt: "ainda n\u00e3o influencia nada \u2014 muito pouco para significar algo", it: "non influenza ancora nulla: troppo poco per significare qualcosa", ja: "\u307e\u3060\u4f55\u306b\u3082\u53cd\u6620\u3055\u308c\u3066\u3044\u307e\u305b\u3093 \u2014 \u5224\u65ad\u3059\u308b\u306b\u306f\u5c11\u306a\u3059\u304e\u307e\u3059", zh: "\u5c1a\u672a\u5f71\u54cd\u4efb\u4f55\u5185\u5bb9 \u2014 \u6570\u636e\u592a\u5c11\uff0c\u8bf4\u660e\u4e0d\u4e86\u4ec0\u4e48", hi: "\u0905\u092d\u0940 \u0915\u0941\u091b \u092d\u0940 \u0906\u0915\u093e\u0930 \u0928\u0939\u0940\u0902 \u0926\u0947 \u0930\u0939\u093e \u2014 \u0907\u0924\u0928\u093e \u0915\u092e \u0915\u093f \u0915\u094b\u0908 \u092e\u0924\u0932\u092c \u0928 \u0928\u093f\u0915\u0932\u0947", ar: "\u0644\u0627 \u064a\u0624\u062b\u0631 \u0641\u064a \u0634\u064a\u0621 \u0628\u0639\u062f \u2014 \u0623\u0642\u0644 \u0645\u0646 \u0623\u0646 \u064a\u0639\u0646\u064a \u0634\u064a\u0626\u064b\u0627" },
  "cont.forget": { en: "Forget it", es: "Olvidarlo", fr: "Tout oublier", de: "Verwerfen", pt: "Esquecer", it: "Dimenticalo", ja: "\u7834\u68c4\u3059\u308b", zh: "\u6e05\u9664\u5b83", hi: "\u0907\u0938\u0947 \u092d\u0942\u0932 \u091c\u093e\u090f\u0901", ar: "\u0627\u062d\u0630\u0641\u0647" },
  "cont.nothing": { en: "Nothing yet.", es: "Todav\u00eda nada.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Ainda nada.", it: "Ancora niente.", ja: "\u307e\u3060\u4f55\u3082\u3042\u308a\u307e\u305b\u3093\u3002", zh: "\u6682\u65f6\u8fd8\u6ca1\u6709\u3002", hi: "\u0905\u092d\u0940 \u0915\u0941\u091b \u0928\u0939\u0940\u0902\u0964", ar: "\u0644\u0627 \u0634\u064a\u0621 \u0628\u0639\u062f." },
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
    de: "Keine App nötig. Eine Automatisierung auf dem Telefon sendet Messwerte an die Adresse unten, und der Export Ihres Geräts lehrt JIM Ihre Basislinie aus der bereits aufgezeichneten Historie. Wählen Sie, was Sie tragen — die Schritte passen sich an.",
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
    de: "Basislinie aus dem Export Ihres Geräts speisen",
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
  "nav.home": {
    en: "Overview",
    es: "Resumen",
    fr: "Aperçu",
    de: "Übersicht",
    pt: "Resumo",
    it: "Panoramica",
    ja: "概要",
    zh: "总览",
    hi: "अवलोकन",
    ar: "نظرة عامة",
  },
  "nav.monitor": {
    en: "Live Monitoring",
    es: "Monitorización en vivo",
    fr: "Suivi en direct",
    de: "Live-Überwachung",
    pt: "Monitorização em direto",
    it: "Monitoraggio dal vivo",
    ja: "リアルタイム監視",
    zh: "实时监测",
    hi: "लाइव निगरानी",
    ar: "المراقبة المباشرة",
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
    de: "Ihr eigenes Profil",
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
    de: "Das QRME-Profil, das als Sie spricht. Der Guardian sagt ihm nichts, bis Sie festlegen, was er weitergeben darf, und Sie sehen genau, was ginge, bevor irgendetwas geht.",
    pt: "O perfil QRME que fala como você. O Guardião não lhe conta nada até dizer que partes pode transmitir, e vê exatamente o que iria antes de qualquer coisa ir.",
    it: "Il profilo QRME che parla come te. Il Guardian non gli dice nulla finché non indichi cosa può trasmettere, e vedi esattamente cosa partirebbe prima che parta.",
    ja: "あなたとして話す QRME のプロフィールです。どの部分を伝えてよいか決めるまで、ガーディアンは何も伝えません。送られる内容は送信前にそのまま確認できます。",
    zh: "以你的身份说话的 QRME 档案。在你指明可以转达哪些部分之前，守护者不会告诉它任何事，而且发送前你能看到确切会送出什么。",
    hi: "वह QRME प्रोफ़ाइल जो आपके रूप में बोलती है। जब तक आप यह न बताएँ कि कौन-से हिस्से भेजे जा सकते हैं, गार्जियन उसे कुछ नहीं बताता, और भेजे जाने से पहले आप ठीक-ठीक देख सकते हैं कि क्या जाएगा।",
    ar: "ملف QRME الذي يتحدث بصفتك. لا يخبره الحارس بشيء حتى تحدد ما يمكن نقله، ويمكنك أن ترى بالضبط ما سيُرسل قبل أن يُرسل أي شيء.",
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
    de: "Fügen Sie die Profil-ID und Ihr Eigentümer-Token aus QRME ein. Es muss ein Profil sein, das QRME als Ihr eigenes führt — ein erfundenes wird abgelehnt.",
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
    de: "Nichts wird weitergegeben, bis Sie es ankreuzen.",
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
    de: "Dies ist die Nachricht selbst, keine Beschreibung. Die Medikation ist der einzige Teil aus Ihren eigenen Worten, daher erscheinen die Namen so, wie Sie sie eingegeben haben.",
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
    de: "Das Trennen entfernt das Token und alles, was Sie angekreuzt hatten. Was dem Profil bereits mitgeteilt wurde, bleibt in dessen Quellenliste in QRME, wo Sie es löschen können.",
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
    fr: "Délier",
    de: "Trennen",
    pt: "Desligar",
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
    de: "Melden Sie sich zuerst an.",
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
    de: "Ihr eigenes Profil",
    pt: "O seu próprio perfil",
    it: "Il tuo profilo",
    ja: "あなた自身のプロフィール",
    zh: "你自己的档案",
    hi: "आपकी अपनी प्रोफ़ाइल",
    ar: "ملفك الشخصي",
  },
  "nav.coach": {
    en: "Coach",
    es: "Entrenador",
    fr: "Coach",
    de: "Coach",
    pt: "Treinador",
    it: "Coach",
    ja: "コーチ",
    zh: "教练",
    hi: "कोच",
    ar: "المدرّب",
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
    fr: "Point",
    de: "Check-in",
    pt: "Registo",
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
    ja: "ジャーナル",
    zh: "日志",
    hi: "जर्नल",
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
    zh: "你的名字",
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
  "ch.title": {
    en: "Channel & camera", es: "Canal y cámara", fr: "Canal et caméra", de: "Kanal & Kamera", pt: "Canal e câmara", it: "Canale e fotocamera", ja: "チャンネルとカメラ", zh: "通道与相机", hi: "चैनल और कैमरा", ar: "القناة والكاميرا",
  },
  "ch.signin": {
    en: "Sign in to set up the channel.", es: "Inicia sesión para configurar el canal.", fr: "Connectez-vous pour configurer le canal.", de: "Melden Sie sich an, um den Kanal einzurichten.", pt: "Inicie sessão para configurar o canal.", it: "Accedi per configurare il canale.", ja: "チャンネルを設定するにはサインインしてください。", zh: "登录以设置通道。", hi: "चैनल सेट करने के लिए साइन इन करें।", ar: "سجّل الدخول لإعداد القناة.",
  },
  "ch.devices": {
    en: "Devices", es: "Dispositivos", fr: "Appareils", de: "Geräte", pt: "Dispositivos", it: "Dispositivi", ja: "デバイス", zh: "设备", hi: "उपकरण", ar: "الأجهزة",
  },
  "ch.devices.lead": {
    en: "A microphone attaches to a device this account already knows, never to a name typed in the moment — so what is listening is always something you registered on purpose.", es: "Un micrófono se conecta a un dispositivo que esta cuenta ya conoce, nunca a un nombre escrito en el momento — así lo que escucha es siempre algo que registraste a propósito.", fr: "Un micro s'attache à un appareil que ce compte connaît déjà, jamais à un nom tapé sur le moment — ce qui écoute est donc toujours quelque chose que vous avez enregistré exprès.", de: "Ein Mikrofon hängt an einem Gerät, das dieses Konto bereits kennt, nie an einem eben eingetippten Namen — was zuhört, ist also immer etwas, das Sie absichtlich registriert haben.", pt: "Um microfone liga-se a um dispositivo que esta conta já conhece, nunca a um nome escrito no momento — o que está a ouvir é sempre algo que registou de propósito.", it: "Un microfono si collega a un dispositivo che questo account già conosce, mai a un nome digitato al momento — ciò che ascolta è sempre qualcosa che hai registrato apposta.", ja: "マイクはこのアカウントが既に知るデバイスにのみ接続され、その場で入力した名前には接続されません — 聞いているのは常にあなたが意図して登録したものです。", zh: "麦克风只连接到此账户已知的设备，绝不连接临时输入的名称 — 因此在聆听的始终是你有意注册的设备。", hi: "माइक्रोफ़ोन उसी उपकरण से जुड़ता है जिसे यह खाता पहले से जानता है, तुरंत टाइप किए नाम से कभी नहीं — तो जो सुन रहा है वह हमेशा आपका जानबूझकर पंजीकृत उपकरण है।", ar: "يرتبط الميكروفون بجهاز يعرفه هذا الحساب مسبقًا، لا باسم يُكتب في اللحظة — فما يستمع هو دائمًا شيء سجّلته عمدًا.",
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
  "ch.mic.capped": {
    en: "Narrowed for the moment — a call is in progress. Your setting ({gain}) comes back afterwards.", es: "Reducido por el momento — hay una llamada en curso. Tu ajuste ({gain}) vuelve después.", fr: "Restreint pour le moment — un appel est en cours. Votre réglage ({gain}) revient ensuite.", de: "Vorübergehend verengt — ein Anruf läuft. Ihre Einstellung ({gain}) kehrt danach zurück.", pt: "Reduzido por agora — há uma chamada em curso. O seu ajuste ({gain}) volta depois.", it: "Ridotto per il momento — c'è una chiamata in corso. La tua impostazione ({gain}) torna dopo.", ja: "通話中のため一時的に絞られています。設定（{gain}）は通話後に戻ります。", zh: "通话进行中，暂时收窄。你的设置（{gain}）稍后恢复。", hi: "फ़िलहाल सीमित — कॉल चल रही है। आपकी सेटिंग ({gain}) बाद में लौट आएगी।", ar: "مقيَّد مؤقتًا — هناك مكالمة جارية. إعدادك ({gain}) يعود بعدها.",
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
    en: "Choose a site first.", es: "Elige primero una zona.", fr: "Choisissez d'abord une zone.", de: "Wählen Sie zuerst eine Stelle.", pt: "Escolha primeiro uma zona.", it: "Scegli prima una zona.", ja: "まず部位を選んでください。", zh: "请先选择部位。", hi: "पहले स्थान चुनें।", ar: "اختر الموضع أولاً.",
  },
  "ch.cam.tick": {
    en: "Tick the box before choosing a file.", es: "Marca la casilla antes de elegir un archivo.", fr: "Cochez la case avant de choisir un fichier.", de: "Setzen Sie das Häkchen, bevor Sie eine Datei wählen.", pt: "Marque a caixa antes de escolher um ficheiro.", it: "Spunta la casella prima di scegliere un file.", ja: "ファイルを選ぶ前にチェックを入れてください。", zh: "选择文件前请先勾选。", hi: "फ़ाइल चुनने से पहले बॉक्स चिह्नित करें।", ar: "ضع علامة في المربع قبل اختيار ملف.",
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
    en: "Sensitivity", es: "Sensibilidad", fr: "Sensibilité", de: "Empfindlichkeit", pt: "Sensibilidade", it: "Sensibilità", ja: "感度", zh: "敏感度", hi: "संवेदनशीलता", ar: "الحساسية",
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
    en: "Ask", es: "Preguntar", fr: "Demander", de: "Fragen", pt: "Perguntar", it: "Chiedi", ja: "尋ねる", zh: "询问", hi: "पूछें", ar: "اسأل",
  },
  "att.alarm.what.ph": {
    en: "What is happening", es: "Qué está pasando", fr: "Que se passe-t-il", de: "Was gerade passiert", pt: "O que está a acontecer", it: "Cosa sta succedendo", ja: "何が起きているか", zh: "正在发生什么", hi: "क्या हो रहा है", ar: "ما الذي يحدث",
  },
  "att.alarm.raise": {
    en: "Raise an emergency", es: "Activar una emergencia", fr: "Déclencher une urgence", de: "Notfall auslösen", pt: "Acionar uma emergência", it: "Attiva un'emergenza", ja: "緊急事態を発報", zh: "发起紧急求助", hi: "आपातकाल उठाएँ", ar: "إطلاق حالة طوارئ",
  },
  "att.alarm.rule": {
    en: "This is the door that reaches emergency services, and it takes your own credential. The uncredentialed one is a scanned care code — a bystander at your front door can wake the people watching over you, and stops there. Only you can send an ambulance to yourself.", es: "Esta es la puerta que llega a los servicios de emergencia, y requiere tu propia credencial. La puerta sin credencial es un código de cuidado escaneado — un transeúnte en tu puerta puede despertar a quienes te cuidan, y ahí se detiene. Solo tú puedes enviarte una ambulancia.", fr: "C'est la porte qui atteint les services d'urgence, et elle exige votre propre référence. Celle sans référence est un code de soin scanné — un passant à votre porte peut réveiller ceux qui veillent sur vous, et s'arrête là. Vous seul pouvez vous envoyer une ambulance.", de: "Dies ist die Tür zu den Rettungsdiensten, und sie verlangt Ihre eigenen Zugangsdaten. Die ohne ist ein gescannter Pflegecode — ein Passant an Ihrer Haustür kann die Menschen wecken, die über Sie wachen, und dort endet es. Nur Sie können sich selbst einen Krankenwagen schicken.", pt: "Esta é a porta que chega aos serviços de emergência, e exige a sua própria credencial. A porta sem credencial é um código de cuidado lido — um transeunte à sua porta pode acordar quem vela por si, e fica por aí. Só você pode enviar uma ambulância a si próprio.", it: "Questa è la porta che raggiunge i servizi di emergenza, e richiede la tua credenziale. Quella senza è un codice di cura scansionato — un passante alla tua porta può svegliare chi veglia su di te, e si ferma lì. Solo tu puoi mandarti un'ambulanza.", ja: "これは救急サービスに届く扉で、あなた自身の資格情報が必要です。資格情報なしの扉はスキャンされたケアコードで、玄関先の通行人はあなたを見守る人々を起こせますが、そこまでです。自分に救急車を呼べるのはあなただけです。", zh: "这是通往急救服务的门，需要你本人的凭证。无凭证的那扇门是被扫描的护理码 — 你门前的路人可以唤醒守护你的人，仅止于此。只有你能为自己叫救护车。", hi: "यही वह द्वार है जो आपातकालीन सेवाओं तक पहुँचता है, और इसे आपकी अपनी क्रेडेंशियल चाहिए। बिना क्रेडेंशियल वाला द्वार स्कैन किया केयर कोड है — आपके दरवाज़े पर खड़ा राहगीर आपकी देखरेख करने वालों को जगा सकता है, बस वहीं तक। एम्बुलेंस केवल आप ही अपने लिए भेज सकते हैं।", ar: "هذا هو الباب الذي يصل إلى خدمات الطوارئ، ويتطلب اعتمادك الشخصي. الباب بلا اعتماد هو رمز رعاية ممسوح — عابر عند بابك يمكنه إيقاظ من يسهرون عليك، ويقف عند ذلك. وحدك من يستطيع إرسال إسعاف لنفسك.",
  },
  "att.med": {
    en: "Medical ID", es: "Identificación médica", fr: "Identité médicale", de: "Medizinischer Ausweis", pt: "Identificação médica", it: "ID medico", ja: "メディカルID", zh: "医疗ID", hi: "मेडिकल आईडी", ar: "الهوية الطبية",
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
  "bas.title": {
    en: "Your baseline", es: "Tu línea base", fr: "Votre ligne de base", de: "Ihre Basislinie", pt: "A sua linha de base", it: "La tua linea di base", ja: "あなたのベースライン", zh: "你的基线", hi: "आपकी आधार रेखा", ar: "خطك الأساسي",
  },
  "bas.what": {
    en: "What this is", es: "Qué es esto", fr: "Ce que c'est", de: "Was das ist", pt: "O que é isto", it: "Che cos'è", ja: "これは何か", zh: "这是什么", hi: "यह क्या है", ar: "ما هذا",
  },
  "bas.what.p1": {
    en: "Every resting reading nudges your own average for each metric. Once a metric has enough of them, a band is drawn around it — and when a reading lands outside that band, in either direction, your Guardian checks in and asks how you are. A drift check-in on its own never calls anybody — but the crash watch below is exactly the \"call somebody\" you can program: if a reading turns critical and you stop answering, help gets sent.", es: "Cada lectura en reposo ajusta tu propio promedio de cada métrica. Cuando una métrica tiene suficientes, se dibuja una banda a su alrededor — y cuando una lectura cae fuera de esa banda, en cualquier dirección, tu Guardián te consulta y pregunta cómo estás. Una consulta por deriva por sí sola nunca llama a nadie — pero la vigilancia de colapso de abajo es exactamente el «llamar a alguien» que puedes programar: si una lectura se vuelve crítica y dejas de responder, se envía ayuda.", fr: "Chaque mesure au repos ajuste votre propre moyenne pour chaque métrique. Quand une métrique en a assez, une bande est tracée autour — et quand une mesure tombe hors de cette bande, dans un sens ou dans l'autre, votre Gardien prend de vos nouvelles. Un contrôle de dérive seul n'appelle jamais personne — mais la veille d'effondrement ci-dessous est exactement le « appeler quelqu'un » que vous pouvez programmer : si une mesure devient critique et que vous ne répondez plus, de l'aide est envoyée.", de: "Jede Ruhemessung verschiebt Ihren eigenen Durchschnitt je Metrik. Hat eine Metrik genug davon, wird ein Band darum gezogen — und landet eine Messung außerhalb dieses Bandes, in beliebiger Richtung, meldet sich Ihr Guardian und fragt, wie es Ihnen geht. Eine Drift-Nachfrage allein ruft nie jemanden — aber die Absturzwache darunter ist genau das programmierbare »jemanden rufen«: wird eine Messung kritisch und Sie antworten nicht mehr, wird Hilfe geschickt.", pt: "Cada leitura em repouso ajusta a sua própria média de cada métrica. Quando uma métrica tem leituras suficientes, desenha-se uma banda à sua volta — e quando uma leitura cai fora dessa banda, em qualquer direção, o seu Guardião pergunta como está. Uma verificação de deriva por si só nunca chama ninguém — mas a vigília de colapso abaixo é exatamente o «chamar alguém» que pode programar: se uma leitura fica crítica e deixa de responder, envia-se ajuda.", it: "Ogni lettura a riposo aggiusta la tua media per ciascuna metrica. Quando una metrica ne ha abbastanza, le si disegna intorno una banda — e quando una lettura cade fuori da quella banda, in entrambe le direzioni, il tuo Guardian si fa vivo e ti chiede come stai. Un controllo di deriva da solo non chiama mai nessuno — ma la veglia anti-collasso qui sotto è esattamente il «chiama qualcuno» che puoi programmare: se una lettura diventa critica e smetti di rispondere, i soccorsi partono.", ja: "安静時の測定はそのたびに各指標のあなた自身の平均を少しずつ更新します。十分な数が集まると帯が引かれ、測定値がその帯の外にどちらの方向でも出ると、ガーディアンが様子を尋ねます。ドリフト確認だけでは誰にも連絡しません — しかし下のクラッシュウォッチこそが、あなたが設定できる「誰かを呼ぶ」です：測定値が危険域に入り応答が途絶えると、助けが送られます。", zh: "每次静息读数都会微调你各项指标的自身平均值。某项指标积累足够后，会围绕它画出一条带 — 当读数落在带外，无论哪个方向，你的守护者都会来问你怎么样。漂移问询本身绝不会呼叫任何人 — 而下方的骤变守护正是你可以设定的「呼叫某人」：读数转为危急且你不再应答时，就会派出援助。", hi: "हर विश्राम रीडिंग आपके हर मीट्रिक का अपना औसत थोड़ा समायोजित करती है। पर्याप्त रीडिंग होने पर उसके चारों ओर एक बैंड खिंच जाता है — और जब कोई रीडिंग उस बैंड से बाहर, किसी भी दिशा में, गिरती है तो आपका गार्जियन हालचाल पूछता है। ड्रिफ़्ट पूछताछ अपने आप कभी किसी को नहीं बुलाती — पर नीचे की क्रैश निगरानी ही वह «किसी को बुलाओ» है जिसे आप प्रोग्राम कर सकते हैं: रीडिंग गंभीर हो और आप जवाब देना बंद कर दें, तो मदद भेजी जाती है।", ar: "كل قراءة راحة تعدّل متوسطك الخاص لكل مقياس. ومتى توفر ما يكفي منها يُرسم نطاق حوله — وإذا وقعت قراءة خارج ذلك النطاق، في أي اتجاه، يطمئن عليك الحارس ويسألك كيف حالك. فحص الانحراف وحده لا يستدعي أحدًا أبدًا — لكن مراقبة الانهيار أدناه هي بالضبط «استدعِ أحدًا» التي يمكنك برمجتها: إذا صارت قراءة حرجة وتوقفت عن الرد، تُرسل النجدة.",
  },
  "bas.what.p2": {
    en: "The widths below are yours to set. Narrow one to be told sooner; widen it if a metric of yours naturally wanders.", es: "Los anchos de abajo los fijas tú. Estrecha uno para enterarte antes; ensánchalo si una métrica tuya vaga por naturaleza.", fr: "Les largeurs ci-dessous sont à vous. Resserrez-en une pour être prévenu plus tôt ; élargissez-la si une de vos métriques vagabonde naturellement.", de: "Die Breiten darunter bestimmen Sie. Verengen Sie eine, um früher Bescheid zu bekommen; weiten Sie sie, wenn eine Ihrer Metriken von Natur aus wandert.", pt: "As larguras abaixo são suas. Estreite uma para saber mais cedo; alargue-a se uma métrica sua vagueia por natureza.", it: "Le larghezze qui sotto le decidi tu. Restringine una per saperlo prima; allargala se una tua metrica vaga per natura.", ja: "下の幅はあなたが決めます。早く知りたければ狭く、生まれつき揺れやすい指標なら広く。", zh: "下面的宽度由你设定。调窄可更早得知；某项指标天生爱漂移就调宽。", hi: "नीचे की चौड़ाइयाँ आप तय करते हैं। जल्दी जानने के लिए संकरी करें; अगर आपका कोई मीट्रिक स्वभावतः भटकता है तो चौड़ी करें।", ar: "العروض أدناه أنت من يحددها. ضيّق نطاقًا لتُخبَر أبكر؛ ووسّعه إن كان أحد مقاييسك يتجول بطبيعته.",
  },
  "bas.ask.title": {
    en: "JIM is asking: are you okay?", es: "JIM pregunta: ¿estás bien?", fr: "JIM demande : ça va ?", de: "JIM fragt: Geht es Ihnen gut?", pt: "O JIM pergunta: está bem?", it: "JIM chiede: stai bene?", ja: "JIMが尋ねています：大丈夫ですか？", zh: "JIM在问：你还好吗？", hi: "JIM पूछ रहा है: क्या आप ठीक हैं?", ar: "JIM يسأل: هل أنت بخير؟",
  },
  "bas.ask.body": {
    en: "A concerning reading came in ({concern}). This is attempt {attempt} of {attempts} — after that, your crash watch contacts {name}{ems}.", es: "Llegó una lectura preocupante ({concern}). Este es el intento {attempt} de {attempts} — después, tu vigilancia de colapso contacta a {name}{ems}.", fr: "Une mesure préoccupante est arrivée ({concern}). Ceci est la tentative {attempt} sur {attempts} — ensuite, votre veille d'effondrement contacte {name}{ems}.", de: "Eine besorgniserregende Messung kam an ({concern}). Dies ist Versuch {attempt} von {attempts} — danach kontaktiert Ihre Absturzwache {name}{ems}.", pt: "Chegou uma leitura preocupante ({concern}). Esta é a tentativa {attempt} de {attempts} — depois disso, a sua vigília de colapso contacta {name}{ems}.", it: "È arrivata una lettura preoccupante ({concern}). Questo è il tentativo {attempt} di {attempts} — dopo, la tua veglia anti-collasso contatta {name}{ems}.", ja: "懸念される測定値が届きました（{concern}）。これは{attempts}回中{attempt}回目の呼びかけです — その後、クラッシュウォッチが{name}に連絡します{ems}。", zh: "收到一条令人担忧的读数（{concern}）。这是第{attempt}次尝试，共{attempts}次 — 之后，骤变守护将联系{name}{ems}。", hi: "एक चिंताजनक रीडिंग आई ({concern})। यह {attempts} में से {attempt}वाँ प्रयास है — उसके बाद आपकी क्रैश निगरानी {name} से संपर्क करेगी{ems}।", ar: "وصلت قراءة مقلقة ({concern}). هذه المحاولة {attempt} من {attempts} — بعدها تتصل مراقبة الانهيار بـ{name}{ems}.",
  },
  "bas.ask.ok": {
    en: "I'm okay", es: "Estoy bien", fr: "Ça va", de: "Mir geht es gut", pt: "Estou bem", it: "Sto bene", ja: "大丈夫です", zh: "我没事", hi: "मैं ठीक हूँ", ar: "أنا بخير",
  },
  "bas.trip": {
    en: "⚠ The crash watch tripped: {name} was contacted{ems}. Any normal reading — or the button above — stands it down.", es: "⚠ La vigilancia de colapso saltó: se contactó a {name}{ems}. Cualquier lectura normal — o el botón de arriba — la desactiva.", fr: "⚠ La veille d'effondrement s'est déclenchée : {name} a été contacté{ems}. Toute mesure normale — ou le bouton ci-dessus — la lève.", de: "⚠ Die Absturzwache hat ausgelöst: {name} wurde kontaktiert{ems}. Jede normale Messung — oder der Knopf oben — stellt sie zurück.", pt: "⚠ A vigília de colapso disparou: {name} foi contactado{ems}. Qualquer leitura normal — ou o botão acima — desativa-a.", it: "⚠ La veglia anti-collasso è scattata: {name} è stato contattato{ems}. Qualsiasi lettura normale — o il pulsante sopra — la rientra.", ja: "⚠ クラッシュウォッチが作動しました：{name}に連絡しました{ems}。正常な測定値 — または上のボタン — で解除されます。", zh: "⚠ 骤变守护已触发：已联系{name}{ems}。任何正常读数 — 或上方按钮 — 都会将其解除。", hi: "⚠ क्रैश निगरानी सक्रिय हुई: {name} से संपर्क किया गया{ems}। कोई भी सामान्य रीडिंग — या ऊपर का बटन — इसे शांत कर देती है।", ar: "⚠ انطلقت مراقبة الانهيار: تم الاتصال بـ{name}{ems}. أي قراءة طبيعية — أو الزر أعلاه — تُعيدها إلى وضعها.",
  },
  "bas.cw.title": {
    en: "Crash watch — if you stop answering, help gets sent", es: "Vigilancia de colapso — si dejas de responder, se envía ayuda", fr: "Veille d'effondrement — si vous ne répondez plus, de l'aide est envoyée", de: "Absturzwache — wenn Sie nicht mehr antworten, wird Hilfe geschickt", pt: "Vigília de colapso — se deixar de responder, envia-se ajuda", it: "Veglia anti-collasso — se smetti di rispondere, i soccorsi partono", ja: "クラッシュウォッチ — 応答が途絶えると助けが送られます", zh: "骤变守护 — 你不再应答时会派出援助", hi: "क्रैश निगरानी — जवाब देना बंद करें तो मदद भेजी जाती है", ar: "مراقبة الانهيار — إذا توقفت عن الرد تُرسل النجدة",
  },
  "bas.cw.lead": {
    en: "Off by default, programmed by you: when a reading turns critical — a fall the watch felt, a collapsing pulse, oxygen falling — JIM asks \"are you okay?\" — and if {n} attempts over {m} minutes all go unanswered, it contacts your trusted person{ems}. Any sign of you — the button, a normal reading — calls it off. Drift check-ins stay calm and never trigger this.", es: "Desactivada por defecto y programada por ti: cuando una lectura se vuelve crítica — una caída que el reloj sintió, un pulso que se desploma, oxígeno bajando — JIM pregunta «¿estás bien?» — y si {n} intentos a lo largo de {m} minutos quedan sin respuesta, contacta a tu persona de confianza{ems}. Cualquier señal tuya — el botón, una lectura normal — la cancela. Las consultas por deriva son tranquilas y nunca la disparan.", fr: "Désactivée par défaut, programmée par vous : quand une mesure devient critique — une chute sentie par la montre, un pouls qui s'effondre, l'oxygène qui baisse — JIM demande « ça va ? » — et si {n} tentatives sur {m} minutes restent toutes sans réponse, elle contacte votre personne de confiance{ems}. Tout signe de vous — le bouton, une mesure normale — l'annule. Les contrôles de dérive restent calmes et ne la déclenchent jamais.", de: "Standardmäßig aus, von Ihnen programmiert: Wird eine Messung kritisch — ein Sturz, den die Uhr spürte, ein einbrechender Puls, fallender Sauerstoff — fragt JIM »Geht es Ihnen gut?« — und bleiben {n} Versuche über {m} Minuten alle unbeantwortet, kontaktiert sie Ihre Vertrauensperson{ems}. Jedes Zeichen von Ihnen — der Knopf, eine normale Messung — bricht sie ab. Drift-Nachfragen bleiben ruhig und lösen das nie aus.", pt: "Desligada por defeito, programada por si: quando uma leitura fica crítica — uma queda que o relógio sentiu, um pulso a desabar, oxigénio a cair — o JIM pergunta «está bem?» — e se {n} tentativas ao longo de {m} minutos ficarem todas sem resposta, contacta a sua pessoa de confiança{ems}. Qualquer sinal seu — o botão, uma leitura normal — cancela-a. As verificações de deriva ficam calmas e nunca a disparam.", it: "Spenta per default, programmata da te: quando una lettura diventa critica — una caduta che l'orologio ha sentito, un polso che crolla, ossigeno in calo — JIM chiede «stai bene?» — e se {n} tentativi in {m} minuti restano tutti senza risposta, contatta la tua persona di fiducia{ems}. Qualsiasi segno di te — il pulsante, una lettura normale — la annulla. I controlli di deriva restano calmi e non la attivano mai.", ja: "初期状態ではオフで、設定するのはあなたです：測定値が危険域に入ると — 時計が感じた転倒、急落する脈拍、下がる酸素 — JIMが「大丈夫ですか？」と尋ね、{m}分間に{n}回の呼びかけがすべて無応答なら、信頼できる人に連絡します{ems}。あなたの気配 — ボタンや正常な測定値 — があれば中止します。ドリフト確認は穏やかなままで、これを作動させることはありません。", zh: "默认关闭，由你设定：当读数转为危急 — 手表感到的跌倒、骤降的脉搏、下降的血氧 — JIM会问「你还好吗？」— 若{m}分钟内{n}次尝试均无应答，就联系你的信任联系人{ems}。你的任何动静 — 按钮、一条正常读数 — 都会取消它。漂移问询保持平静，绝不会触发它。", hi: "डिफ़ॉल्ट रूप से बंद, आपके द्वारा प्रोग्राम की गई: जब कोई रीडिंग गंभीर हो — घड़ी को महसूस हुई गिरावट, गिरती नब्ज़, घटती ऑक्सीजन — JIM पूछता है «क्या आप ठीक हैं?» — और अगर {m} मिनटों में {n} प्रयास सब अनुत्तरित रहें, तो यह आपके भरोसेमंद व्यक्ति से संपर्क करती है{ems}। आपका कोई भी संकेत — बटन, एक सामान्य रीडिंग — इसे रद्द कर देता है। ड्रिफ़्ट पूछताछ शांत रहती है और इसे कभी सक्रिय नहीं करती।", ar: "معطلة افتراضيًا وأنت من يبرمجها: إذا صارت قراءة حرجة — سقطة شعرت بها الساعة، نبض ينهار، أكسجين يهبط — يسأل JIM «هل أنت بخير؟» — وإن بقيت {n} محاولات خلال {m} دقيقة كلها بلا رد، تتصل بشخصك الموثوق{ems}. أي إشارة منك — الزر أو قراءة طبيعية — تلغيها. فحوص الانحراف تبقى هادئة ولا تُطلقها أبدًا.",
  },
  "bas.cw.name": {
    en: "Trusted person", es: "Persona de confianza", fr: "Personne de confiance", de: "Vertrauensperson", pt: "Pessoa de confiança", it: "Persona di fiducia", ja: "信頼できる人", zh: "信任联系人", hi: "भरोसेमंद व्यक्ति", ar: "الشخص الموثوق",
  },
  "bas.cw.name.ph": {
    en: "Rosa", es: "Rosa", fr: "Rosa", de: "Rosa", pt: "Rosa", it: "Rosa", ja: "Rosa", zh: "Rosa", hi: "Rosa", ar: "Rosa",
  },
  "bas.cw.channel": {
    en: "How to reach them (email or phone)", es: "Cómo contactarla (correo o teléfono)", fr: "Comment la joindre (e-mail ou téléphone)", de: "Wie man sie erreicht (E-Mail oder Telefon)", pt: "Como contactá-la (email ou telefone)", it: "Come raggiungerla (email o telefono)", ja: "連絡方法（メールまたは電話）", zh: "如何联系（邮箱或电话）", hi: "उन तक कैसे पहुँचें (ईमेल या फ़ोन)", ar: "كيف تصل إليه (بريد أو هاتف)",
  },
  "bas.cw.channel.ph": {
    en: "rosa@example.com", es: "rosa@example.com", fr: "rosa@example.com", de: "rosa@example.com", pt: "rosa@example.com", it: "rosa@example.com", ja: "rosa@example.com", zh: "rosa@example.com", hi: "rosa@example.com", ar: "rosa@example.com",
  },
  "bas.cw.attempts": {
    en: "Attempts", es: "Intentos", fr: "Tentatives", de: "Versuche", pt: "Tentativas", it: "Tentativi", ja: "回数", zh: "尝试次数", hi: "प्रयास", ar: "المحاولات",
  },
  "bas.cw.window": {
    en: "Minutes per attempt", es: "Minutos por intento", fr: "Minutes par tentative", de: "Minuten pro Versuch", pt: "Minutos por tentativa", it: "Minuti per tentativo", ja: "1回あたりの分数", zh: "每次间隔分钟", hi: "प्रति प्रयास मिनट", ar: "دقائق لكل محاولة",
  },
  "bas.cw.ems": {
    en: "May request emergency services (this app relays the request to every connected system — it cannot itself place a call)", es: "Puede solicitar servicios de emergencia (esta app retransmite la solicitud a cada sistema conectado — no puede llamar por sí misma)", fr: "Peut demander les services d'urgence (cette appli relaie la demande à chaque système connecté — elle ne peut pas appeler elle-même)", de: "Darf Rettungsdienste anfordern (diese App leitet die Anforderung an jedes verbundene System weiter — selbst anrufen kann sie nicht)", pt: "Pode pedir serviços de emergência (esta app retransmite o pedido a cada sistema ligado — ela própria não pode ligar)", it: "Può richiedere i servizi di emergenza (questa app inoltra la richiesta a ogni sistema collegato — non può chiamare da sola)", ja: "救急要請を許可（このアプリは接続された各システムに要請を中継します — 自分で電話をかけることはできません）", zh: "可请求急救服务（本应用将请求转发给每个已连接的系统 — 它自己无法拨打电话）", hi: "आपातकालीन सेवाएँ माँग सकती है (यह ऐप अनुरोध हर जुड़े सिस्टम तक पहुँचाती है — खुद कॉल नहीं कर सकती)", ar: "يجوز طلب خدمات الطوارئ (يمرر هذا التطبيق الطلب إلى كل نظام متصل — ولا يستطيع الاتصال بنفسه)",
  },
  "bas.cw.disarm": {
    en: "Disarm", es: "Desactivar", fr: "Désarmer", de: "Entschärfen", pt: "Desativar", it: "Disattiva", ja: "解除", zh: "解除", hi: "निष्क्रिय करें", ar: "عطّل",
  },
  "bas.cw.armed": {
    en: "Armed — {name} will be contacted after {n} unanswered attempts.", es: "Activada — se contactará a {name} tras {n} intentos sin respuesta.", fr: "Armée — {name} sera contacté après {n} tentatives sans réponse.", de: "Scharf — {name} wird nach {n} unbeantworteten Versuchen kontaktiert.", pt: "Ativada — {name} será contactado após {n} tentativas sem resposta.", it: "Attiva — {name} sarà contattato dopo {n} tentativi senza risposta.", ja: "作動中 — {n}回の呼びかけが無応答なら{name}に連絡します。", zh: "已启用 — {n}次尝试无应答后将联系{name}。", hi: "सक्रिय — {n} अनुत्तरित प्रयासों के बाद {name} से संपर्क होगा।", ar: "مفعّلة — سيُتصل بـ{name} بعد {n} محاولات بلا رد.",
  },
  "bas.metrics": {
    en: "Your metrics", es: "Tus métricas", fr: "Vos métriques", de: "Ihre Metriken", pt: "As suas métricas", it: "Le tue metriche", ja: "あなたの指標", zh: "你的指标", hi: "आपके मीट्रिक", ar: "مقاييسك",
  },
  "bas.metrics.none": {
    en: "Nothing yet.", es: "Nada todavía.", fr: "Rien pour l'instant.", de: "Noch nichts.", pt: "Nada ainda.", it: "Ancora niente.", ja: "まだ何もありません。", zh: "尚无数据。", hi: "अभी कुछ नहीं।", ar: "لا شيء بعد.",
  },
  "bas.metrics.learning": {
    en: "learning — {n} resting reading{s} so far", es: "aprendiendo — {n} lecturas en reposo hasta ahora", fr: "apprentissage — {n} mesures au repos pour l'instant", de: "lernt — bisher {n} Ruhemessungen", pt: "a aprender — {n} leituras em repouso até agora", it: "in apprendimento — {n} letture a riposo finora", ja: "学習中 — これまでの安静時測定{n}件", zh: "学习中 — 目前{n}条静息读数", hi: "सीख रहा है — अब तक {n} विश्राम रीडिंग", ar: "قيد التعلم — {n} قراءات راحة حتى الآن",
  },
  "bas.metrics.usual": {
    en: "your usual {v}, checked in below {lo} or above {hi}", es: "tu habitual {v}, se consulta por debajo de {lo} o por encima de {hi}", fr: "votre habituel {v}, contrôle sous {lo} ou au-dessus de {hi}", de: "Ihr üblicher Wert {v}, nachgefragt unter {lo} oder über {hi}", pt: "o seu habitual {v}, verificado abaixo de {lo} ou acima de {hi}", it: "il tuo solito {v}, controllo sotto {lo} o sopra {hi}", ja: "普段は{v}、{lo}未満または{hi}超で確認します", zh: "你的常态{v}，低于{lo}或高于{hi}时问询", hi: "आपका सामान्य {v}, {lo} से नीचे या {hi} से ऊपर पर पूछा जाता है", ar: "معتادك {v}، يُسأل دون {lo} أو فوق {hi}",
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
    en: "What you call it", es: "Cómo lo llamas", fr: "Comment vous l'appelez", de: "Wie Sie ihn nennen", pt: "Como lhe chama", it: "Come lo chiami", ja: "呼び名", zh: "你怎么称呼它", hi: "आप इसे क्या कहते हैं", ar: "بمَ تسميه",
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
    en: "@you", es: "@tu", fr: "@vous", de: "@sie", pt: "@voce", it: "@tu", ja: "@you", zh: "@you", hi: "@aap", ar: "@انت",
  },
  "rch.acc.publish.opt": {
    en: "publish — words go out", es: "publicar — las palabras salen", fr: "publier — les mots sortent", de: "veröffentlichen — Worte gehen hinaus", pt: "publicar — as palavras saem", it: "pubblica — le parole escono", ja: "発信 — 言葉が出ていく", zh: "发布 — 话语向外", hi: "प्रकाशित — शब्द बाहर जाते हैं", ar: "نشر — الكلمات تخرج",
  },
  "rch.acc.collect.opt": {
    en: "collect — words come in", es: "recoger — las palabras entran", fr: "collecter — les mots entrent", de: "sammeln — Worte kommen herein", pt: "recolher — as palavras entram", it: "raccogli — le parole entrano", ja: "収集 — 言葉が入ってくる", zh: "收集 — 话语向内", hi: "एकत्र — शब्द अंदर आते हैं", ar: "جمع — الكلمات تدخل",
  },
  "rch.acc.connect": {
    en: "Connect", es: "Conectar", fr: "Connecter", de: "Verbinden", pt: "Ligar", it: "Collega", ja: "接続", zh: "连接", hi: "जोड़ें", ar: "اربط",
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
    en: "Say something", es: "Di algo", fr: "Dites quelque chose", de: "Sagen Sie etwas", pt: "Diga algo", it: "Di' qualcosa", ja: "何か言う", zh: "说点什么", hi: "कुछ कहें", ar: "قل شيئًا",
  },
  "rch.acc.publish": {
    en: "Publish", es: "Publicar", fr: "Publier", de: "Veröffentlichen", pt: "Publicar", it: "Pubblica", ja: "発信する", zh: "发布", hi: "प्रकाशित करें", ar: "انشر",
  },
  "rch.acc.collect": {
    en: "Collect", es: "Recoger", fr: "Collecter", de: "Sammeln", pt: "Recolher", it: "Raccogli", ja: "収集する", zh: "收集", hi: "एकत्र करें", ar: "اجمع",
  },
  "rch.beacon.note": {
    en: "{url} — the printable code for it is behind your own token, not a public link.", es: "{url} — su código imprimible está tras tu propio token, no en un enlace público.", fr: "{url} — son code imprimable est derrière votre propre jeton, pas un lien public.", de: "{url} — der druckbare Code dafür liegt hinter Ihrem eigenen Token, nicht hinter einem öffentlichen Link.", pt: "{url} — o código imprimível está atrás do seu próprio token, não de um link público.", it: "{url} — il suo codice stampabile è dietro il tuo token, non un link pubblico.", ja: "{url} — その印刷用コードは公開リンクではなく、あなた自身のトークンの向こうにあります。", zh: "{url} — 它的可打印码在你自己的令牌之后，而非公开链接。", hi: "{url} — इसका मुद्रण योग्य कोड आपके अपने टोकन के पीछे है, सार्वजनिक लिंक नहीं।", ar: "{url} — الرمز القابل للطباعة له خلف رمزك الخاص، لا رابط عام.",
  },
  "rch.ask": {
    en: "Send it to go and ask", es: "Envíalo a preguntar", fr: "L'envoyer demander", de: "Losschicken zum Fragen", pt: "Envie-o a perguntar", it: "Mandalo a chiedere", ja: "尋ねに行かせる", zh: "派它去问", hi: "पूछने भेजें", ar: "أرسله ليسأل",
  },
  "rch.ask.topic.ph": {
    en: "Topic", es: "Tema", fr: "Sujet", de: "Thema", pt: "Tema", it: "Argomento", ja: "トピック", zh: "主题", hi: "विषय", ar: "الموضوع",
  },
  "rch.ask.q.ph": {
    en: "What do you want to know?", es: "¿Qué quieres saber?", fr: "Que voulez-vous savoir ?", de: "Was wollen Sie wissen?", pt: "O que quer saber?", it: "Cosa vuoi sapere?", ja: "何を知りたいですか？", zh: "你想知道什么？", hi: "आप क्या जानना चाहते हैं?", ar: "ماذا تريد أن تعرف؟",
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
    en: "Redactions is how much of you was taken out before the question left, and left this host is whether it left at all. A screen that showed the findings and hid those two would be showing the answer and hiding what it cost.", es: "«Redactions» es cuánto de ti se quitó antes de que la pregunta saliera, y «left this host» es si salió siquiera. Una pantalla que mostrara los hallazgos y ocultara esos dos estaría mostrando la respuesta y escondiendo lo que costó.", fr: "« Redactions » dit combien de vous a été retiré avant que la question parte, et « left this host » dit si elle est partie tout court. Un écran qui montrerait les résultats en cachant ces deux-là montrerait la réponse en cachant son prix.", de: "»Redactions« sagt, wie viel von Ihnen entfernt wurde, bevor die Frage aufbrach, und »left this host«, ob sie überhaupt aufbrach. Ein Bildschirm, der die Befunde zeigte und diese beiden versteckte, zeigte die Antwort und verbärge ihren Preis.", pt: "«Redactions» é quanto de si foi retirado antes de a pergunta sair, e «left this host» é se sequer saiu. Um ecrã que mostrasse os resultados e escondesse esses dois estaria a mostrar a resposta e a esconder o que custou.", it: "«Redactions» è quanto di te è stato tolto prima che la domanda partisse, e «left this host» è se è partita affatto. Uno schermo che mostrasse i risultati nascondendo quei due mostrerebbe la risposta nascondendo quanto è costata.", ja: "「Redactions」は質問が出発する前にあなたのどれだけが取り除かれたかを、「left this host」はそもそも出発したかどうかを示します。所見を見せてこの二つを隠す画面は、答えを見せて代償を隠すことになります。", zh: "「Redactions」是问题出发前从你身上删去了多少，「left this host」是它究竟有没有离开。若屏幕只展示发现而隐藏这两项，就是展示答案而隐藏代价。", hi: "«Redactions» यह है कि प्रश्न निकलने से पहले आपका कितना हिस्सा हटाया गया, और «left this host» यह कि वह निकला भी या नहीं। जो स्क्रीन निष्कर्ष दिखाकर ये दोनों छिपाए, वह उत्तर दिखाकर उसकी कीमत छिपा रही होगी।", ar: "«Redactions» تعني كم أُخذ منك قبل أن يغادر السؤال، و«left this host» تعني هل غادر أصلًا. الشاشة التي تعرض النتائج وتخفي هذين تعرض الجواب وتخفي ثمنه.",
  },
  "rch.wrist": {
    en: "Elsewhere and the wrist", es: "Otros sitios y la muñeca", fr: "Ailleurs et le poignet", de: "Anderswo und das Handgelenk", pt: "Outros lugares e o pulso", it: "Altrove e il polso", ja: "よそと手首", zh: "别处与手腕", hi: "अन्यत्र और कलाई", ar: "أماكن أخرى والمعصم",
  },
  "rch.wrist.visits": {
    en: "{n} community visit{s} recorded — JIM points at QRME's rooms, QRME hosts them.", es: "{n} visitas comunitarias registradas — JIM apunta a las salas de QRME, QRME las aloja.", fr: "{n} visites communautaires enregistrées — JIM pointe vers les salles de QRME, QRME les héberge.", de: "{n} Community-Besuche verzeichnet — JIM zeigt auf QRMEs Räume, QRME beherbergt sie.", pt: "{n} visitas comunitárias registadas — o JIM aponta para as salas do QRME, o QRME aloja-as.", it: "{n} visite alla community registrate — JIM punta alle stanze di QRME, QRME le ospita.", ja: "コミュニティ訪問{n}件を記録 — JIMはQRMEのルームを指し示し、QRMEがホストします。", zh: "已记录{n}次社区访问 — JIM指向QRME的房间，由QRME托管。", hi: "{n} सामुदायिक भेंट दर्ज — JIM QRME के कमरों की ओर इशारा करता है, QRME उन्हें होस्ट करता है।", ar: "سُجلت {n} زيارة مجتمعية — يشير JIM إلى غرف QRME، وQRME يستضيفها.",
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
  "brg.title": {
    en: "Bearing", es: "Porte", fr: "Allure", de: "Haltung", pt: "Porte", it: "Portamento", ja: "たたずまい", zh: "姿态", hi: "आचरण", ar: "الهيئة",
  },
  "brg.sub": {
    en: "how it speaks, and what it made of you", es: "cómo habla, y qué ha hecho de ti", fr: "comment il parle, et ce qu'il a fait de vous", de: "wie er spricht, und was er aus Ihnen gemacht hat", pt: "como fala, e o que fez de si", it: "come parla, e cosa ha fatto di te", ja: "どう話すか、そしてあなたから何を読み取ったか", zh: "它如何说话，以及它对你的解读", hi: "यह कैसे बोलता है, और आपके बारे में क्या समझा", ar: "كيف يتكلم، وما استخلصه عنك",
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
  "brg.speak.cautious": {
    en: "cautious", es: "cauto", fr: "prudent", de: "vorsichtig", pt: "cauteloso", it: "cauto", ja: "慎重", zh: "谨慎", hi: "सतर्क", ar: "حذر",
  },
  "brg.speak.balanced": {
    en: "balanced", es: "equilibrado", fr: "équilibré", de: "ausgewogen", pt: "equilibrado", it: "equilibrato", ja: "バランス", zh: "均衡", hi: "संतुलित", ar: "متوازن",
  },
  "brg.speak.direct": {
    en: "direct", es: "directo", fr: "direct", de: "direkt", pt: "direto", it: "diretto", ja: "率直", zh: "直接", hi: "सीधा", ar: "مباشر",
  },
  "brg.speak.sens": {
    en: "Set sensitivity", es: "Fijar la sensibilidad", fr: "Définir la sensibilité", de: "Empfindlichkeit festlegen", pt: "Definir a sensibilidade", it: "Imposta la sensibilità", ja: "感度を設定", zh: "设定敏感度", hi: "संवेदनशीलता तय करें", ar: "حدد الحساسية",
  },
  "brg.speak.voice": {
    en: "Forget the voice", es: "Olvidar la voz", fr: "Oublier la voix", de: "Die Stimme vergessen", pt: "Esquecer a voz", it: "Dimentica la voce", ja: "声を忘れる", zh: "忘掉这把声音", hi: "आवाज़ भूल जाओ", ar: "انسَ الصوت",
  },
  "brg.speak.tr.ph": {
    en: "Something to translate", es: "Algo que traducir", fr: "Quelque chose à traduire", de: "Etwas zum Übersetzen", pt: "Algo para traduzir", it: "Qualcosa da tradurre", ja: "翻訳する文", zh: "要翻译的内容", hi: "अनुवाद के लिए कुछ", ar: "شيء للترجمة",
  },
  "brg.speak.tr": {
    en: "Translate", es: "Traducir", fr: "Traduire", de: "Übersetzen", pt: "Traduzir", it: "Traduci", ja: "翻訳", zh: "翻译", hi: "अनुवाद करें", ar: "ترجم",
  },
  "brg.told": {
    en: "What it was told", es: "Lo que se le dijo", fr: "Ce qu'on lui a dit", de: "Was ihm gesagt wurde", pt: "O que lhe foi dito", it: "Cosa gli è stato detto", ja: "伝えられたこと", zh: "它被告知的", hi: "इसे क्या बताया गया", ar: "ما قيل له",
  },
  "brg.told.note.ph": {
    en: "In your own words", es: "Con tus palabras", fr: "Avec vos mots", de: "In Ihren eigenen Worten", pt: "Nas suas palavras", it: "Con parole tue", ja: "自分の言葉で", zh: "用你自己的话", hi: "अपने शब्दों में", ar: "بكلماتك أنت",
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
    en: "Refused: {err} — consent the source over in What's Held first. The check is on the server; this screen is only reporting what it said.", es: "Rechazado: {err} — consiente la fuente primero en Lo Retenido. La comprobación está en el servidor; esta pantalla solo informa de lo que dijo.", fr: "Refusé : {err} — consentez d'abord la source dans Ce qui est détenu. Le contrôle est sur le serveur ; cet écran ne fait que rapporter ce qu'il a dit.", de: "Abgelehnt: {err} — willigen Sie zuerst drüben in »Was gehalten wird« in die Quelle ein. Die Prüfung liegt auf dem Server; dieser Bildschirm berichtet nur, was er sagte.", pt: "Recusado: {err} — consinta a fonte primeiro em O Que É Guardado. A verificação está no servidor; este ecrã apenas relata o que ele disse.", it: "Rifiutato: {err} — acconsenti prima la fonte in Ciò che è custodito. Il controllo è sul server; questa schermata riporta solo ciò che ha detto.", ja: "拒否: {err} — まず「保持されているもの」でそのソースに同意してください。チェックはサーバー側にあり、この画面はその返答を伝えているだけです。", zh: "被拒: {err} — 请先到「所持有的」里同意该来源。检查在服务器上；此屏幕只是转述它的答复。", hi: "अस्वीकृत: {err} — पहले «जो रखा गया है» में स्रोत की सहमति दें। जाँच सर्वर पर है; यह स्क्रीन केवल उसका कहा बता रही है।", ar: "مرفوض: {err} — وافق على المصدر أولًا في «ما هو محفوظ». الفحص على الخادم؛ هذه الشاشة تنقل ما قاله فحسب.",
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
    en: "Tell us about the app", es: "Cuéntanos sobre la app", fr: "Parlez-nous de l'appli", de: "Erzählen Sie uns von der App", pt: "Fale-nos da app", it: "Parlaci dell'app", ja: "アプリについて教えてください", zh: "跟我们聊聊这个应用", hi: "ऐप के बारे में बताएँ", ar: "أخبرنا عن التطبيق",
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
    en: "{n} suggestion{s} in all · {m} of them yours", es: "{n} sugerencias en total · {m} son tuyas", fr: "{n} suggestions en tout · {m} sont les vôtres", de: "{n} Vorschläge insgesamt · {m} davon Ihre", pt: "{n} sugestões no total · {m} são suas", it: "{n} suggerimenti in tutto · {m} sono tuoi", ja: "提案は計{n}件 · うち{m}件があなたのもの", zh: "共{n}条建议 · 其中{m}条是你的", hi: "कुल {n} सुझाव · उनमें {m} आपके", ar: "{n} اقتراحات إجمالًا · {m} منها لك",
  },
  "set.title": {
    en: "Privacy & Connection", es: "Privacidad y conexión", fr: "Confidentialité et connexion", de: "Datenschutz & Verbindung", pt: "Privacidade e ligação", it: "Privacy e connessione", ja: "プライバシーと接続", zh: "隐私与连接", hi: "गोपनीयता और कनेक्शन", ar: "الخصوصية والاتصال",
  },
  "set.api": {
    en: "API connection", es: "Conexión con la API", fr: "Connexion à l'API", de: "API-Verbindung", pt: "Ligação à API", it: "Connessione API", ja: "API接続", zh: "API 连接", hi: "API कनेक्शन", ar: "اتصال الواجهة",
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
    en: "Your model API key", es: "Tu clave de API del modelo", fr: "Votre clé d'API du modèle", de: "Ihr Modell-API-Schlüssel", pt: "A sua chave de API do modelo", it: "La tua chiave API del modello", ja: "あなたのモデルAPIキー", zh: "你的模型 API 密钥", hi: "आपकी मॉडल API कुंजी", ar: "مفتاح واجهة النموذج الخاص بك",
  },
  "set.key.pitch": {
    en: "Paste your own key (Anthropic sk-ant-…, or OpenAI / xAI / Gemini for those providers) and your Guardian's replies run on your credential. It stays on this device and rides only your own requests — the server never stores it. Leave it empty to use whatever key the deployment lends.", es: "Pega tu propia clave (Anthropic sk-ant-…, o de OpenAI / xAI / Gemini para esos proveedores) y las respuestas de tu Guardián correrán con tu credencial. Se queda en este dispositivo y viaja solo con tus propias peticiones — el servidor nunca la almacena. Déjala vacía para usar la clave que preste el despliegue.", fr: "Collez votre propre clé (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini pour ces fournisseurs) et les réponses de votre Gardien tournent sur votre identifiant. Elle reste sur cet appareil et n'accompagne que vos propres requêtes — le serveur ne la stocke jamais. Laissez-la vide pour utiliser la clé que prête le déploiement.", de: "Fügen Sie Ihren eigenen Schlüssel ein (Anthropic sk-ant-…, oder OpenAI / xAI / Gemini für diese Anbieter), und die Antworten Ihres Guardians laufen auf Ihrem Zugang. Er bleibt auf diesem Gerät und reist nur mit Ihren eigenen Anfragen — der Server speichert ihn nie. Lassen Sie ihn leer, um den Schlüssel zu nutzen, den das Deployment leiht.", pt: "Cole a sua própria chave (Anthropic sk-ant-…, ou OpenAI / xAI / Gemini para esses fornecedores) e as respostas do seu Guardião correm com a sua credencial. Fica neste dispositivo e viaja só com os seus próprios pedidos — o servidor nunca a guarda. Deixe-a vazia para usar a chave que o deployment empresta.", it: "Incolla la tua chiave (Anthropic sk-ant-…, oppure OpenAI / xAI / Gemini per quei provider) e le risposte del tuo Guardian girano sulla tua credenziale. Resta su questo dispositivo e viaggia solo con le tue richieste — il server non la memorizza mai. Lasciala vuota per usare la chiave che presta il deployment.", ja: "自分のキーを貼り付けてください（Anthropicは sk-ant-…、各プロバイダーはOpenAI / xAI / Gemini のもの）。するとガーディアンの返答はあなたの資格情報で動きます。キーはこの端末に留まり、あなた自身のリクエストにだけ同行します — サーバーが保存することはありません。空欄にすれば、この配備が貸すキーが使われます。", zh: "粘贴你自己的密钥（Anthropic 用 sk-ant-…，对应提供方则用 OpenAI / xAI / Gemini 的密钥），你的守护者的回复便以你的凭证运行。它留在本设备上，只随你自己的请求同行 — 服务器绝不存储它。留空则使用本部署出借的密钥。", hi: "अपनी कुंजी चिपकाएँ (Anthropic के लिए sk-ant-…, या उन प्रदाताओं के लिए OpenAI / xAI / Gemini) और आपके गार्जियन के जवाब आपकी क्रेडेंशियल पर चलेंगे। यह इसी डिवाइस पर रहती है और केवल आपके अपने अनुरोधों के साथ जाती है — सर्वर इसे कभी संग्रहित नहीं करता। खाली छोड़ें तो डिप्लॉयमेंट जो कुंजी उधार देता है वही चलेगी।", ar: "الصق مفتاحك الخاص (Anthropic بصيغة sk-ant-…، أو OpenAI / xAI / Gemini لتلك المزودات) فتعمل ردود حارسك على اعتمادك. يبقى على هذا الجهاز ويرافق طلباتك أنت فقط — ولا يخزّنه الخادم أبدًا. اتركه فارغًا لاستخدام المفتاح الذي يعيره هذا النشر.",
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
    en: "What JIM has learned about you", es: "Lo que JIM ha aprendido sobre ti", fr: "Ce que JIM a appris de vous", de: "Was JIM über Sie gelernt hat", pt: "O que o JIM aprendeu sobre si", it: "Cosa JIM ha imparato di te", ja: "JIMがあなたについて学んだこと", zh: "JIM 对你的了解", hi: "JIM ने आपके बारे में क्या सीखा", ar: "ما تعلّمه JIM عنك",
  },
  "set.adapt.pitch": {
    en: "A profile derived from your own history — the conditions you declared, how your check-ins trend, what you bring up, and which guidance has actually helped. It shapes how the coach answers. Nothing is sent to a model vendor to build it.", es: "Un perfil derivado de tu propio historial — las condiciones que declaraste, cómo evolucionan tus registros, lo que sacas a colación y qué orientación te ha ayudado de verdad. Da forma a cómo responde el coach. No se envía nada a un proveedor de modelos para construirlo.", fr: "Un profil dérivé de votre propre historique — les affections que vous avez déclarées, la tendance de vos pointages, ce que vous évoquez, et quels conseils ont réellement aidé. Il façonne la façon dont le coach répond. Rien n'est envoyé à un fournisseur de modèles pour le construire.", de: "Ein Profil aus Ihrer eigenen Historie — die Beschwerden, die Sie angaben, wie sich Ihre Check-ins entwickeln, was Sie ansprechen und welche Ratschläge tatsächlich geholfen haben. Es prägt, wie der Coach antwortet. Zum Bauen wird nichts an einen Modellanbieter gesendet.", pt: "Um perfil derivado do seu próprio histórico — as condições que declarou, como evoluem os seus check-ins, o que traz à conversa e que orientação ajudou realmente. Molda a forma como o coach responde. Nada é enviado a um fornecedor de modelos para o construir.", it: "Un profilo derivato dalla tua stessa storia — le condizioni che hai dichiarato, come vanno i tuoi check-in, cosa tiri fuori, e quale guida ha davvero aiutato. Modella il modo in cui il coach risponde. Nulla viene inviato a un fornitore di modelli per costruirlo.", ja: "あなた自身の履歴から導かれたプロフィールです — 申告した状態、チェックインの推移、話題にすること、そして実際に役立った助言。コーチの答え方を形づくります。これを作るためにモデルベンダーへ送られるものは何もありません。", zh: "由你自己的历史推导出的画像 — 你申报的状况、签到的趋势、你会提起的事，以及哪些指导真正有用。它塑造教练的回答方式。构建它不会向任何模型厂商发送任何东西。", hi: "आपके अपने इतिहास से बना एक प्रोफ़ाइल — आपने जो स्थितियाँ बताईं, आपके चेक-इन का रुझान, आप क्या उठाते हैं, और किस मार्गदर्शन ने वास्तव में मदद की। यह तय करता है कि कोच कैसे जवाब देता है। इसे बनाने के लिए किसी मॉडल विक्रेता को कुछ नहीं भेजा जाता।", ar: "ملف مستخلص من تاريخك أنت — الحالات التي أعلنتها، واتجاه تسجيلاتك، وما تثيره، وأي إرشاد أفاد فعلًا. يشكّل طريقة إجابة المدرب. ولا يُرسل شيء إلى مزود نماذج لبنائه.",
  },
  "set.adapt.conf": {
    en: "{pct}% confidence", es: "{pct}% de confianza", fr: "{pct}% de confiance", de: "{pct}% Konfidenz", pt: "{pct}% de confiança", it: "{pct}% di confidenza", ja: "確信度{pct}%", zh: "置信度{pct}%", hi: "{pct}% विश्वास", ar: "ثقة {pct}%",
  },
  "set.adapt.from": {
    en: "from {n} pieces of your own history", es: "de {n} fragmentos de tu propio historial", fr: "à partir de {n} éléments de votre propre historique", de: "aus {n} Teilen Ihrer eigenen Historie", pt: "de {n} peças do seu próprio histórico", it: "da {n} pezzi della tua stessa storia", ja: "あなた自身の履歴{n}件から", zh: "取自你自己历史中的{n}条", hi: "आपके अपने इतिहास के {n} टुकड़ों से", ar: "من {n} قطعة من تاريخك",
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
    en: "Your name here", es: "Tu nombre aquí", fr: "Votre nom ici", de: "Ihr Name hier", pt: "O seu nome aqui", it: "Il tuo nome qui", ja: "ここでのあなたの名前", zh: "你在这里的名字", hi: "यहाँ आपका नाम", ar: "اسمك هنا",
  },
  "set.anon.pseudo": {
    en: "You use JIM as {name} — a pseudonym. JIM never learned your real name.", es: "Usas JIM como {name} — un seudónimo. JIM nunca supo tu nombre real.", fr: "Vous utilisez JIM sous le nom {name} — un pseudonyme. JIM n'a jamais appris votre vrai nom.", de: "Sie nutzen JIM als {name} — ein Pseudonym. JIM hat Ihren echten Namen nie erfahren.", pt: "Usa o JIM como {name} — um pseudónimo. O JIM nunca soube o seu nome real.", it: "Usi JIM come {name} — uno pseudonimo. JIM non ha mai saputo il tuo vero nome.", ja: "あなたはJIMを{name}として使っています — 仮名です。JIMがあなたの本名を知ることはありませんでした。", zh: "你以{name}的身份使用 JIM — 那是化名。JIM 从未知道你的真名。", hi: "आप JIM का उपयोग {name} के रूप में करते हैं — यह छद्मनाम है। JIM ने आपका असली नाम कभी नहीं जाना।", ar: "تستخدم JIM باسم {name} — وهو اسم مستعار. لم يعرف JIM اسمك الحقيقي قط.",
  },
  "set.anon.keeps": {
    en: "Keeps: {x}", es: "Conserva: {x}", fr: "Garde : {x}", de: "Behält: {x}", pt: "Mantém: {x}", it: "Mantiene: {x}", ja: "保つもの: {x}", zh: "保留: {x}", hi: "रखता है: {x}", ar: "يحتفظ بـ: {x}",
  },
  "set.anon.costs": {
    en: "Costs: {x}", es: "Cuesta: {x}", fr: "Coûte : {x}", de: "Kostet: {x}", pt: "Custa: {x}", it: "Costa: {x}", ja: "失うもの: {x}", zh: "代价: {x}", hi: "क़ीमत: {x}", ar: "يكلّف: {x}",
  },
  "set.anon.own": {
    en: "You use JIM under your own name ({name}).", es: "Usas JIM con tu propio nombre ({name}).", fr: "Vous utilisez JIM sous votre vrai nom ({name}).", de: "Sie nutzen JIM unter Ihrem eigenen Namen ({name}).", pt: "Usa o JIM com o seu próprio nome ({name}).", it: "Usi JIM con il tuo vero nome ({name}).", ja: "あなたは本名（{name}）でJIMを使っています。", zh: "你以自己的真名（{name}）使用 JIM。", hi: "आप JIM का उपयोग अपने असली नाम ({name}) से करते हैं।", ar: "تستخدم JIM باسمك الحقيقي ({name}).",
  },
  "set.data": {
    en: "Your data", es: "Tus datos", fr: "Vos données", de: "Ihre Daten", pt: "Os seus dados", it: "I tuoi dati", ja: "あなたのデータ", zh: "你的数据", hi: "आपका डेटा", ar: "بياناتك",
  },
  "set.data.note": {
    en: "Guidance runs on-device; sensitive payloads seal into the PDI vault when the tandem is on. User: {uid}", es: "La orientación corre en el dispositivo; las cargas sensibles se sellan en la bóveda PDI cuando el tándem está activo. Usuario: {uid}", fr: "Les conseils tournent sur l'appareil ; les charges sensibles sont scellées dans le coffre PDI quand le tandem est actif. Utilisateur : {uid}", de: "Die Beratung läuft auf dem Gerät; sensible Daten werden im PDI-Tresor versiegelt, wenn das Tandem an ist. Nutzer: {uid}", pt: "A orientação corre no dispositivo; as cargas sensíveis selam-se no cofre PDI quando o tandem está ligado. Utilizador: {uid}", it: "La guida gira sul dispositivo; i payload sensibili si sigillano nel caveau PDI quando il tandem è attivo. Utente: {uid}", ja: "ガイダンスは端末上で動きます。タンデムが有効なとき、機微なペイロードはPDI保管庫に封印されます。ユーザー: {uid}", zh: "指导在设备上运行；串联开启时，敏感负载会封入 PDI 保险库。用户: {uid}", hi: "मार्गदर्शन डिवाइस पर चलता है; टेंडम चालू होने पर संवेदनशील पेलोड PDI तिजोरी में सील हो जाते हैं। उपयोगकर्ता: {uid}", ar: "يعمل الإرشاد على الجهاز؛ وتُختم الحمولات الحساسة في خزنة PDI عندما يكون الترادف مفعّلًا. المستخدم: {uid}",
  },
  "set.data.signout": {
    en: "Sign out & end session", es: "Cerrar sesión y terminar", fr: "Se déconnecter et clore la session", de: "Abmelden & Sitzung beenden", pt: "Terminar sessão e sair", it: "Esci e chiudi la sessione", ja: "サインアウトしてセッションを終了", zh: "登出并结束会话", hi: "साइन आउट करें और सत्र समाप्त करें", ar: "سجّل الخروج وأنهِ الجلسة",
  },
  "set.cloud": {
    en: "What you contribute", es: "Lo que aportas", fr: "Ce que vous contribuez", de: "Was Sie beitragen", pt: "O que contribui", it: "Cosa contribuisci", ja: "あなたが提供するもの", zh: "你贡献了什么", hi: "आप क्या योगदान देते हैं", ar: "ما تساهم به",
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
    en: "No mail server configured, so nothing can be emailed — verification messages are written to this app's log and signup on this machine simply goes straight in. Point it at a mail account below to send real verification links. For Gmail, turn on 2-Step Verification and create an App password; paste that here, not your normal password.", es: "No hay servidor de correo configurado, así que no se puede enviar nada por email — los mensajes de verificación se escriben en el registro de esta app y el alta en esta máquina simplemente entra directa. Apúntalo a una cuenta de correo abajo para enviar enlaces de verificación reales. Para Gmail, activa la verificación en dos pasos y crea una contraseña de aplicación; pega esa aquí, no tu contraseña normal.", fr: "Aucun serveur de messagerie configuré, donc rien ne peut être envoyé par e-mail — les messages de vérification sont écrits dans le journal de cette appli et l'inscription sur cette machine passe directement. Pointez-le vers un compte de messagerie ci-dessous pour envoyer de vrais liens de vérification. Pour Gmail, activez la validation en deux étapes et créez un mot de passe d'application ; collez celui-ci ici, pas votre mot de passe habituel.", de: "Kein Mailserver konfiguriert, also kann nichts per E-Mail gesendet werden — Bestätigungsnachrichten landen im Log dieser App, und die Anmeldung auf dieser Maschine geht einfach direkt durch. Richten Sie es unten auf ein Mailkonto, um echte Bestätigungslinks zu senden. Für Gmail: Bestätigung in zwei Schritten einschalten und ein App-Passwort erstellen; fügen Sie dieses hier ein, nicht Ihr normales Passwort.", pt: "Não há servidor de correio configurado, por isso nada pode ser enviado por email — as mensagens de verificação são escritas no registo desta app e o registo nesta máquina entra diretamente. Aponte-o a uma conta de correio abaixo para enviar links de verificação reais. Para o Gmail, ligue a verificação em duas etapas e crie uma palavra-passe de aplicação; cole essa aqui, não a sua palavra-passe normal.", it: "Nessun server di posta configurato, quindi non si può inviare nulla per email — i messaggi di verifica finiscono nel log di questa app e l'iscrizione su questa macchina passa direttamente. Puntalo a un account di posta qui sotto per inviare link di verifica veri. Per Gmail, attiva la verifica in due passaggi e crea una password per le app; incolla quella qui, non la tua password normale.", ja: "メールサーバーが設定されていないため、メールは一切送れません — 確認メッセージはこのアプリのログに書き出され、この端末での登録はそのまま通ります。実際の確認リンクを送るには、下でメールアカウントを指定してください。Gmailの場合は2段階認証を有効にしてアプリパスワードを作成し、通常のパスワードではなくそちらをここに貼り付けてください。", zh: "未配置邮件服务器，因此无法发送任何邮件 — 验证消息会写入本应用的日志，本机上的注册直接通过。请在下方指向一个邮件账户，以发送真实的验证链接。若用 Gmail，请开启两步验证并创建应用专用密码；把那个粘贴到这里，而不是你的常用密码。", hi: "कोई मेल सर्वर कॉन्फ़िगर नहीं है, इसलिए ईमेल से कुछ नहीं भेजा जा सकता — सत्यापन संदेश इस ऐप के लॉग में लिखे जाते हैं और इस मशीन पर साइनअप सीधे हो जाता है। असली सत्यापन लिंक भेजने के लिए नीचे किसी मेल खाते की ओर इंगित करें। Gmail के लिए 2-चरणीय सत्यापन चालू करें और ऐप पासवर्ड बनाएँ; वही यहाँ चिपकाएँ, अपना सामान्य पासवर्ड नहीं।", ar: "لا يوجد خادم بريد مهيأ، فلا يمكن إرسال أي بريد — تُكتب رسائل التحقق في سجل هذا التطبيق ويمر التسجيل على هذه الآلة مباشرة. وجّهه إلى حساب بريد أدناه لإرسال روابط تحقق حقيقية. في Gmail، فعّل التحقق بخطوتين وأنشئ كلمة مرور للتطبيقات؛ والصق تلك هنا لا كلمة مرورك المعتادة.",
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
    en: "Your Guardian's replies can run on any of these. Pick one and every reply uses it; Automatic uses whichever is configured.", es: "Las respuestas de tu Guardián pueden correr en cualquiera de estos. Elige uno y todas las respuestas lo usan; Automático usa el que esté configurado.", fr: "Les réponses de votre Gardien peuvent tourner sur n'importe lequel. Choisissez-en un et chaque réponse l'utilise ; Automatique utilise celui qui est configuré.", de: "Die Antworten Ihres Guardians können auf jedem davon laufen. Wählen Sie eines, und jede Antwort nutzt es; Automatisch nutzt das jeweils Konfigurierte.", pt: "As respostas do seu Guardião podem correr em qualquer um destes. Escolha um e todas as respostas o usam; Automático usa o que estiver configurado.", it: "Le risposte del tuo Guardian possono girare su uno qualsiasi. Scegline uno e ogni risposta lo usa; Automatico usa quello configurato.", ja: "ガーディアンの返答はどれでも動かせます。選べばすべての返答がそれを使い、「自動」は設定済みのものを使います。", zh: "你的守护者的回复可运行在任一模型上。选定后每条回复都用它；「自动」使用已配置的模型。", hi: "आपके गार्जियन के जवाब इनमें से किसी पर चल सकते हैं। एक चुनें और हर जवाब उसी का उपयोग करेगा; स्वचालित जो कॉन्फ़िगर है उसे लेता है।", ar: "يمكن أن تعمل ردود حارسك على أي منها. اختر واحدًا فتستخدمه كل الردود؛ التلقائي يستخدم ما هو مهيأ.",
  },
  "set.model.stub": {
    en: "⚠ Right now replies come from the built-in offline helper — no online model has a working key on this machine. Pick a provider above and add its key (“Your model API key” below works for all of them).", es: "⚠ Ahora mismo las respuestas vienen del asistente offline integrado — ningún modelo en línea tiene clave válida en esta máquina. Elige un proveedor arriba y añade su clave («Tu clave de API del modelo», abajo, sirve para todos).", fr: "⚠ En ce moment, les réponses viennent de l'assistant hors ligne intégré — aucun modèle en ligne n'a de clé valide sur cette machine. Choisissez un fournisseur ci-dessus et ajoutez sa clé (« Votre clé d'API du modèle », plus bas, vaut pour tous).", de: "⚠ Derzeit kommen Antworten vom eingebauten Offline-Helfer — kein Online-Modell hat auf dieser Maschine einen gültigen Schlüssel. Wählen Sie oben einen Anbieter und fügen Sie dessen Schlüssel hinzu (»Ihr Modell-API-Schlüssel« unten gilt für alle).", pt: "⚠ Neste momento as respostas vêm do assistente offline integrado — nenhum modelo online tem chave válida nesta máquina. Escolha um fornecedor acima e adicione a sua chave («A sua chave de API do modelo», abaixo, serve para todos).", it: "⚠ In questo momento le risposte vengono dall'assistente offline integrato — nessun modello online ha una chiave valida su questa macchina. Scegli un provider sopra e aggiungi la sua chiave («La tua chiave API del modello», qui sotto, vale per tutti).", ja: "⚠ 現在の返答は内蔵オフラインヘルパーからです — このマシンで有効なキーを持つオンラインモデルがありません。上でプロバイダーを選び、キーを追加してください（下の「あなたのモデルAPIキー」がすべてに使えます）。", zh: "⚠ 当前回复来自内置离线助手 — 本机上没有任何在线模型持有有效密钥。请在上方选择提供方并添加其密钥（下方的「你的模型 API 密钥」对所有提供方都适用）。", hi: "⚠ अभी जवाब अंतर्निहित ऑफ़लाइन सहायक से आ रहे हैं — इस मशीन पर किसी ऑनलाइन मॉडल की कुंजी नहीं है। ऊपर प्रदाता चुनें और उसकी कुंजी जोड़ें (नीचे «आपकी मॉडल API कुंजी» सभी के लिए काम करती है)।", ar: "⚠ الردود الآن من المساعد المدمج دون اتصال — لا يملك أي نموذج متصل مفتاحًا صالحًا على هذه الآلة. اختر مزودًا أعلاه وأضف مفتاحه («مفتاح واجهة النموذج الخاص بك» أدناه يصلح لها جميعًا).",
  },
  "set.model.resolves": {
    en: "⚠ Right now it resolves to {effective} — the one you picked has no key on this machine yet.", es: "⚠ Ahora mismo se resuelve a {effective} — el que elegiste aún no tiene clave en esta máquina.", fr: "⚠ En ce moment, cela se résout en {effective} — celui que vous avez choisi n'a pas encore de clé sur cette machine.", de: "⚠ Derzeit löst es zu {effective} auf — das gewählte hat auf dieser Maschine noch keinen Schlüssel.", pt: "⚠ Neste momento resolve para {effective} — o que escolheu ainda não tem chave nesta máquina.", it: "⚠ In questo momento si risolve in {effective} — quello scelto non ha ancora una chiave su questa macchina.", ja: "⚠ 現在は{effective}に解決されます — 選んだものはまだこのマシンにキーがありません。", zh: "⚠ 当前解析为{effective} — 你选的那个在本机上还没有密钥。", hi: "⚠ अभी यह {effective} पर हल होता है — आपके चुने हुए की इस मशीन पर अभी कुंजी नहीं है।", ar: "⚠ الآن يُحل إلى {effective} — الذي اخترته لا مفتاح له على هذه الآلة بعد.",
  },
  "set.voice": {
    en: "Voice", es: "Voz", fr: "Voix", de: "Stimme", pt: "Voz", it: "Voce", ja: "音声", zh: "语音", hi: "आवाज़", ar: "الصوت",
  },
  "set.voice.device": {
    en: "Replies are read aloud in your device's own voice — no account needed. Add an ElevenLabs or OpenAI key for a natural one, and to talk back by microphone.", es: "Las respuestas se leen en voz alta con la voz propia de tu dispositivo — sin cuenta. Añade una clave de ElevenLabs u OpenAI para una voz natural, y para responder por micrófono.", fr: "Les réponses sont lues à voix haute avec la voix de votre appareil — aucun compte nécessaire. Ajoutez une clé ElevenLabs ou OpenAI pour une voix naturelle, et pour répondre au micro.", de: "Antworten werden mit der geräteeigenen Stimme vorgelesen — ohne Konto. Fügen Sie einen ElevenLabs- oder OpenAI-Schlüssel hinzu für eine natürliche Stimme und um per Mikrofon zu antworten.", pt: "As respostas são lidas em voz alta com a voz do seu dispositivo — sem conta. Adicione uma chave ElevenLabs ou OpenAI para uma voz natural, e para responder por microfone.", it: "Le risposte sono lette ad alta voce con la voce del tuo dispositivo — nessun account necessario. Aggiungi una chiave ElevenLabs o OpenAI per una voce naturale, e per rispondere al microfono.", ja: "返答は端末自身の音声で読み上げられます — アカウントは不要です。自然な声とマイクでの応答には、ElevenLabsまたはOpenAIのキーを追加してください。", zh: "回复会用你设备自带的语音朗读 — 无需账户。添加 ElevenLabs 或 OpenAI 密钥即可获得自然嗓音，并可用麦克风回话。", hi: "जवाब आपके डिवाइस की अपनी आवाज़ में पढ़े जाते हैं — कोई खाता नहीं चाहिए। प्राकृतिक आवाज़ और माइक से जवाब देने के लिए ElevenLabs या OpenAI कुंजी जोड़ें।", ar: "تُقرأ الردود بصوت جهازك نفسه — دون حاجة لحساب. أضف مفتاح ElevenLabs أو OpenAI لصوت طبيعي وللرد بالميكروفون.",
  },
  "set.voice.through": {
    en: "Speaking through {provider}{env}. Talking back by microphone works too.", es: "Hablando a través de {provider}{env}. Responder por micrófono también funciona.", fr: "Parle via {provider}{env}. Répondre au micro fonctionne aussi.", de: "Spricht über {provider}{env}. Antworten per Mikrofon geht auch.", pt: "A falar através de {provider}{env}. Responder por microfone também funciona.", it: "Parla tramite {provider}{env}. Rispondere al microfono funziona anche.", ja: "{provider}{env}を通じて話します。マイクでの応答も使えます。", zh: "通过{provider}{env}发声。用麦克风回话同样可用。", hi: "{provider}{env} के ज़रिए बोल रहा है। माइक से जवाब देना भी चलता है।", ar: "يتحدث عبر {provider}{env}. والرد بالميكروفون يعمل أيضًا.",
  },
  "set.voice.hear": {
    en: "Hear it", es: "Escucharla", fr: "L'écouter", de: "Anhören", pt: "Ouvi-la", it: "Ascoltala", ja: "聞いてみる", zh: "听听看", hi: "सुनें", ar: "استمع إليه",
  },
  "set.watch.unreach": {
    en: "⚠ Your phone can't reach this address yet — JIM is only listening on this computer.", es: "⚠ Tu teléfono aún no puede alcanzar esta dirección — JIM solo escucha en este ordenador.", fr: "⚠ Votre téléphone ne peut pas encore atteindre cette adresse — JIM n'écoute que sur cet ordinateur.", de: "⚠ Ihr Telefon erreicht diese Adresse noch nicht — JIM lauscht nur auf diesem Computer.", pt: "⚠ O seu telefone ainda não alcança este endereço — o JIM só escuta neste computador.", it: "⚠ Il tuo telefono non raggiunge ancora questo indirizzo — JIM ascolta solo su questo computer.", ja: "⚠ このアドレスにはまだスマートフォンから届きません — JIMはこのコンピューター上でのみ待ち受けています。", zh: "⚠ 你的手机还无法访问此地址 — JIM 只在这台电脑上监听。", hi: "⚠ आपका फ़ोन अभी इस पते तक नहीं पहुँच सकता — JIM केवल इसी कंप्यूटर पर सुन रहा है।", ar: "⚠ لا يستطيع هاتفك بلوغ هذا العنوان بعد — JIM يستمع على هذا الحاسوب فقط.",
  },
  "set.watch.lan": {
    en: "Let my phone reach JIM on this Wi-Fi", es: "Permitir que mi teléfono alcance a JIM en esta Wi-Fi", fr: "Laisser mon téléphone joindre JIM sur ce Wi-Fi", de: "Mein Telefon JIM in diesem WLAN erreichen lassen", pt: "Deixar o meu telefone alcançar o JIM nesta Wi-Fi", it: "Fai raggiungere JIM al mio telefono su questa Wi-Fi", ja: "このWi-FiでスマートフォンからJIMに届くようにする", zh: "让我的手机在此 Wi-Fi 上访问 JIM", hi: "मेरे फ़ोन को इस Wi-Fi पर JIM तक पहुँचने दें", ar: "دع هاتفي يصل إلى JIM على شبكة Wi-Fi هذه",
  },
  "set.watch.lan.note": {
    en: "Restarts JIM listening on your network. Windows may ask to allow it through the firewall — say yes. Everything personal still requires your sign-in.", es: "Reinicia JIM escuchando en tu red. Windows puede pedir permiso en el cortafuegos — di que sí. Todo lo personal sigue requiriendo tu inicio de sesión.", fr: "Redémarre JIM en écoute sur votre réseau. Windows peut demander à l'autoriser dans le pare-feu — dites oui. Tout ce qui est personnel exige toujours votre connexion.", de: "Startet JIM neu, lauschend in Ihrem Netzwerk. Windows fragt womöglich nach einer Firewall-Freigabe — sagen Sie ja. Alles Persönliche verlangt weiterhin Ihre Anmeldung.", pt: "Reinicia o JIM a escutar na sua rede. O Windows pode pedir para o permitir na firewall — diga que sim. Tudo o que é pessoal continua a exigir a sua sessão iniciada.", it: "Riavvia JIM in ascolto sulla tua rete. Windows potrebbe chiedere di consentirlo nel firewall — di' di sì. Tutto ciò che è personale richiede ancora il tuo accesso.", ja: "JIMをネットワーク上で待ち受ける形で再起動します。Windowsがファイアウォールの許可を尋ねたら「はい」を選んでください。個人的なものはすべて、引き続きサインインが必要です。", zh: "重启 JIM 使其在你的网络上监听。Windows 可能会请求放行防火墙 — 请选择允许。所有个人内容仍需你登录。", hi: "JIM को आपके नेटवर्क पर सुनते हुए पुनः शुरू करता है। Windows फ़ायरवॉल से अनुमति माँग सकता है — हाँ कहें। सब कुछ निजी अब भी आपके साइन-इन की माँग करता है।", ar: "يعيد تشغيل JIM ليستمع على شبكتك. قد يطلب Windows السماح له عبر الجدار الناري — وافق. وكل ما هو شخصي ما زال يتطلب تسجيل دخولك.",
  },
  "set.watch.cli": {
    en: "Start the backend with network access: python -m jim phone", es: "Arranca el servidor con acceso de red: python -m jim phone", fr: "Démarrez le serveur avec accès réseau : python -m jim phone", de: "Backend mit Netzwerkzugriff starten: python -m jim phone", pt: "Inicie o servidor com acesso de rede: python -m jim phone", it: "Avvia il backend con accesso di rete: python -m jim phone", ja: "ネットワークアクセス付きでバックエンドを起動: python -m jim phone", zh: "以网络访问方式启动后端: python -m jim phone", hi: "बैकएंड को नेटवर्क पहुँच के साथ शुरू करें: python -m jim phone", ar: "شغّل الخادم مع وصول الشبكة: python -m jim phone",
  },
  "set.watch.ok": {
    en: "✓ Reachable from your phone on this Wi-Fi.", es: "✓ Accesible desde tu teléfono en esta Wi-Fi.", fr: "✓ Joignable depuis votre téléphone sur ce Wi-Fi.", de: "✓ Von Ihrem Telefon in diesem WLAN erreichbar.", pt: "✓ Acessível do seu telefone nesta Wi-Fi.", it: "✓ Raggiungibile dal tuo telefono su questa Wi-Fi.", ja: "✓ このWi-Fiでスマートフォンから到達できます。", zh: "✓ 在此 Wi-Fi 上可从你的手机访问。", hi: "✓ इस Wi-Fi पर आपके फ़ोन से पहुँच योग्य।", ar: "✓ يمكن الوصول إليه من هاتفك على هذه الشبكة.",
  },
  "set.watch.newaddr": {
    en: "New address", es: "Nueva dirección", fr: "Nouvelle adresse", de: "Neue Adresse", pt: "Novo endereço", it: "Nuovo indirizzo", ja: "新しいアドレス", zh: "新地址", hi: "नया पता", ar: "عنوان جديد",
  },
  "set.watch.received": {
    en: "Received {n} reading{s} · last {when}", es: "Recibidas {n} lecturas · última {when}", fr: "{n} mesures reçues · dernière {when}", de: "{n} Messungen empfangen · zuletzt {when}", pt: "Recebidas {n} leituras · última {when}", it: "Ricevute {n} letture · ultima {when}", ja: "測定値{n}件を受信 · 最終 {when}", zh: "已收到{n}条读数 · 最近 {when}", hi: "{n} रीडिंग प्राप्त · अंतिम {when}", ar: "استُلمت {n} قراءات · آخرها {when}",
  },
  "set.watch.signin": {
    en: "Sign in to mint your drip address.", es: "Inicia sesión para acuñar tu dirección de goteo.", fr: "Connectez-vous pour créer votre adresse de goutte-à-goutte.", de: "Melden Sie sich an, um Ihre Drip-Adresse zu prägen.", pt: "Inicie sessão para cunhar o seu endereço de gotejamento.", it: "Accedi per coniare il tuo indirizzo drip.", ja: "サインインしてドリップアドレスを発行してください。", zh: "登录以生成你的滴流地址。", hi: "अपना ड्रिप पता बनाने के लिए साइन इन करें।", ar: "سجّل الدخول لإنشاء عنوان التقطير الخاص بك.",
  },
  "set.watch.seeded": {
    en: "{metric}: {d} day{s} folded, baseline {b}{tail}", es: "{metric}: {d} días incorporados, línea base {b}{tail}", fr: "{metric} : {d} jours intégrés, ligne de base {b}{tail}", de: "{metric}: {d} Tage eingearbeitet, Basislinie {b}{tail}", pt: "{metric}: {d} dias incorporados, linha de base {b}{tail}", it: "{metric}: {d} giorni integrati, linea di base {b}{tail}", ja: "{metric}: {d}日分を取り込み、ベースライン {b}{tail}", zh: "{metric}: 已并入{d}天，基线 {b}{tail}", hi: "{metric}: {d} दिन समेटे गए, आधार रेखा {b}{tail}", ar: "{metric}: أُدمج {d} أيام، الخط الأساسي {b}{tail}",
  },
  "set.vigil": {
    en: "The vigil", es: "La vigilia", fr: "La veille", de: "Die Wache", pt: "A vigília", it: "La veglia", ja: "見守り", zh: "守夜", hi: "पहरा", ar: "السهر",
  },
  "set.vigil.pitch": {
    en: "Every other alarm fires on a reading. This one fires on the absence of readings: name someone, and if nothing is heard from you for longer than the quiet period, they are asked to check on you. Any reading stands it down. It never calls emergency services — it knocks on a door.", es: "Todas las demás alarmas se disparan por una lectura. Esta se dispara por la ausencia de lecturas: nombra a alguien, y si no se sabe nada de ti durante más tiempo que el periodo de silencio, se le pide que vaya a ver cómo estás. Cualquier lectura la desactiva. Nunca llama a los servicios de emergencia — llama a una puerta.", fr: "Toutes les autres alertes se déclenchent sur une mesure. Celle-ci se déclenche sur l'absence de mesures : nommez quelqu'un, et si l'on n'a rien de vous plus longtemps que la période de silence, on lui demande de prendre de vos nouvelles. Toute mesure la lève. Elle n'appelle jamais les secours — elle frappe à une porte.", de: "Jeder andere Alarm löst auf eine Messung hin aus. Dieser löst auf das Ausbleiben von Messungen hin aus: nennen Sie jemanden, und hört man länger als die Stillperiode nichts von Ihnen, wird diese Person gebeten, nach Ihnen zu sehen. Jede Messung stellt ihn zurück. Er ruft nie den Rettungsdienst — er klopft an eine Tür.", pt: "Todos os outros alarmes disparam com uma leitura. Este dispara com a ausência de leituras: nomeie alguém, e se nada se souber de si por mais tempo do que o período de silêncio, pedem-lhe que veja como está. Qualquer leitura o desativa. Nunca chama os serviços de emergência — bate a uma porta.", it: "Ogni altro allarme scatta su una lettura. Questo scatta sull'assenza di letture: nomina qualcuno, e se non si sa nulla di te per più del periodo di silenzio, gli si chiede di venire a vedere come stai. Qualsiasi lettura lo rientra. Non chiama mai i soccorsi — bussa a una porta.", ja: "他のあらゆる警報は測定値によって鳴ります。これは測定値がないことによって鳴ります：誰かを指名しておくと、静穏期間を超えてあなたから何の知らせもない場合、その人に様子を見に行くよう頼まれます。どんな測定値でも解除されます。救急を呼ぶことは決してなく — 扉を叩くだけです。", zh: "其他所有警报都因某条读数而触发。这一个因读数的缺席而触发：指定一个人，若超过静默期仍未收到你的任何消息，就会请他来看看你。任何读数都会将其解除。它绝不呼叫急救 — 它只是去敲一扇门。", hi: "बाक़ी हर अलार्म किसी रीडिंग पर बजता है। यह रीडिंग की अनुपस्थिति पर बजता है: किसी का नाम दें, और यदि शांत अवधि से अधिक समय तक आपका कोई हाल न मिले, तो उनसे आपकी ख़बर लेने को कहा जाता है। कोई भी रीडिंग इसे शांत कर देती है। यह कभी आपातकालीन सेवाएँ नहीं बुलाता — यह एक दरवाज़ा खटखटाता है।", ar: "كل إنذار آخر ينطلق بقراءة. هذا ينطلق بغياب القراءات: سمِّ شخصًا، وإن لم يُسمع عنك شيء أطول من فترة الصمت، يُطلب منه أن يطمئن عليك. وأي قراءة تُعيده. لا يستدعي الطوارئ أبدًا — بل يطرق بابًا.",
  },
  "set.vigil.tripped": {
    en: "⚠ The vigil has tripped — {name} was asked to check on you{after}.", es: "⚠ La vigilia se ha disparado — se pidió a {name} que fuera a ver cómo estás{after}.", fr: "⚠ La veille s'est déclenchée — on a demandé à {name} de prendre de vos nouvelles{after}.", de: "⚠ Die Wache hat ausgelöst — {name} wurde gebeten, nach Ihnen zu sehen{after}.", pt: "⚠ A vigília disparou — pediram a {name} que visse como está{after}.", it: "⚠ La veglia è scattata — è stato chiesto a {name} di venire a vedere come stai{after}.", ja: "⚠ 見守りが作動しました — {name}にあなたの様子を見るよう依頼しました{after}。", zh: "⚠ 守夜已触发 — 已请{name}来看看你{after}。", hi: "⚠ पहरा सक्रिय हुआ — {name} से आपकी ख़बर लेने को कहा गया{after}।", ar: "⚠ انطلق السهر — طُلب من {name} أن يطمئن عليك{after}.",
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
    en: "In your own words", es: "Con tus palabras", fr: "Avec vos mots", de: "In Ihren eigenen Worten", pt: "Nas suas palavras", it: "Con parole tue", ja: "自分の言葉で", zh: "用你自己的话", hi: "अपने शब्दों में", ar: "بكلماتك أنت",
  },
  "set.vigil.words.note": {
    en: "— what they'll read, written now", es: "— lo que leerá, escrito ahora", fr: "— ce qu'elle lira, écrit maintenant", de: "— was sie lesen wird, jetzt geschrieben", pt: "— o que ele lerá, escrito agora", it: "— ciò che leggerà, scritto ora", ja: "— その人が読む言葉を、いま書いておく", zh: "— 他将读到的内容，此刻写下", hi: "— वे क्या पढ़ेंगे, अभी लिखा हुआ", ar: "— ما سيقرؤه، مكتوبًا الآن",
  },
  "set.vigil.words.ph": {
    en: "I live alone — please knock.", es: "Vivo solo — llama a la puerta, por favor.", fr: "Je vis seul — frappez, s'il vous plaît.", de: "Ich lebe allein — bitte klopfen Sie.", pt: "Vivo sozinho — por favor bata à porta.", it: "Vivo da solo — bussa, per favore.", ja: "一人暮らしです — どうか扉を叩いてください。", zh: "我独自居住 — 请敲门。", hi: "मैं अकेला रहता हूँ — कृपया दरवाज़ा खटखटाएँ।", ar: "أعيش وحدي — من فضلك اطرق الباب.",
  },
  "set.vigil.disarm": {
    en: "Disarm", es: "Desactivar", fr: "Désarmer", de: "Entschärfen", pt: "Desativar", it: "Disattiva", ja: "解除", zh: "解除", hi: "निष्क्रिय करें", ar: "عطّل",
  },
  "set.vigil.check": {
    en: "Just check it", es: "Solo comprobarla", fr: "Juste vérifier", de: "Nur nachsehen", pt: "Só verificar", it: "Solo controlla", ja: "確認するだけ", zh: "只查看", hi: "बस जाँच लें", ar: "تفقّده فقط",
  },
  "set.vigil.armed": {
    en: "Armed · last heard from you {when} · steward: {name}", es: "Activada · última señal tuya {when} · persona de guardia: {name}", fr: "Armée · dernières nouvelles de vous {when} · personne de confiance : {name}", de: "Scharf · zuletzt von Ihnen gehört {when} · Verwalter: {name}", pt: "Ativada · última notícia sua {when} · guardião: {name}", it: "Attiva · ultime tue notizie {when} · custode: {name}", ja: "作動中 · 最後の便り {when} · 見守り役: {name}", zh: "已启用 · 最近一次得知你的消息 {when} · 受托人: {name}", hi: "सक्रिय · आपकी अंतिम ख़बर {when} · संरक्षक: {name}", ar: "مفعّل · آخر خبر عنك {when} · القيّم: {name}",
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

/** The string, in the reader's language, falling back to English per key. */
export function t(key: string, lang: Lang): string {
  const row = TABLE[key];
  if (!row) return key;
  return row[lang] ?? row.en ?? key;
}
