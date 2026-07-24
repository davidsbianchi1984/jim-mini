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
        "tab.overview" to mapOf(
            "en" to "Overview", "es" to "Resumen", "fr" to "Aperçu",
            "de" to "Übersicht", "pt" to "Visão geral", "it" to "Panoramica",
            "ja" to "概要", "zh" to "概览", "hi" to "अवलोकन", "ar" to "نظرة عامة"),
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
