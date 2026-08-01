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
