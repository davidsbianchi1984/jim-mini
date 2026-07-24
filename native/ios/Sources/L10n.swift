import Foundation

/// App-chrome localization: tab names and the most common actions, in every
/// language the backend supports. Guidance, coaching, and safety content are
/// localized server-side by the user's language setting; this table covers
/// the frame around them. Missing keys fall back to English.
enum L10n {
    static func t(_ key: String, _ lang: String) -> String {
        table[key]?[lang] ?? table[key]?["en"] ?? key
    }

    private static let table: [String: [String: String]] = [
        "tab.overview": ["en": "Overview", "es": "Resumen", "fr": "Aperçu",
                         "de": "Übersicht", "pt": "Visão geral", "it": "Panoramica",
                         "ja": "概要", "zh": "概览", "hi": "अवलोकन", "ar": "نظرة عامة"],
        "tab.care": ["en": "Care", "es": "Cuidado", "fr": "Soins",
                     "de": "Fürsorge", "pt": "Cuidado", "it": "Cura",
                     "ja": "ケア", "zh": "关怀", "hi": "देखभाल", "ar": "رعاية"],
        "tab.life": ["en": "Life", "es": "Vida", "fr": "Vie",
                     "de": "Leben", "pt": "Vida", "it": "Vita",
                     "ja": "ライフ", "zh": "生活", "hi": "जीवन", "ar": "الحياة"],
        "tab.safety": ["en": "Safety", "es": "Seguridad", "fr": "Sécurité",
                       "de": "Sicherheit", "pt": "Segurança", "it": "Sicurezza",
                       "ja": "安全", "zh": "安全", "hi": "सुरक्षा", "ar": "السلامة"],
        "tab.connect": ["en": "Connect", "es": "Conectar", "fr": "Connecter",
                        "de": "Verbinden", "pt": "Conectar", "it": "Connetti",
                        "ja": "接続", "zh": "连接", "hi": "कनेक्ट", "ar": "اتصال"],
        "tab.monitor": ["en": "Live Monitoring", "es": "Monitoreo", "fr": "Surveillance",
                        "de": "Überwachung", "pt": "Monitoramento", "it": "Monitoraggio",
                        "ja": "モニタリング", "zh": "实时监测", "hi": "निगरानी", "ar": "المراقبة"],
        "tab.checkin": ["en": "Check-in", "es": "Registro", "fr": "Bilan",
                        "de": "Check-in", "pt": "Check-in", "it": "Check-in",
                        "ja": "チェックイン", "zh": "签到", "hi": "चेक-इन", "ar": "تسجيل الحالة"],
        "tab.coach": ["en": "Coach", "es": "Coach", "fr": "Coach",
                      "de": "Coach", "pt": "Coach", "it": "Coach",
                      "ja": "コーチ", "zh": "教练", "hi": "कोच", "ar": "مدرب"],
        "tab.custody": ["en": "Vault Custody", "es": "Custodia", "fr": "Conservation",
                        "de": "Verwahrung", "pt": "Custódia", "it": "Custodia",
                        "ja": "保管", "zh": "保管记录", "hi": "अभिरक्षा", "ar": "الحفظ"],
        "tab.family": ["en": "Family", "es": "Familia", "fr": "Famille",
                       "de": "Familie", "pt": "Família", "it": "Famiglia",
                       "ja": "家族", "zh": "家庭", "hi": "परिवार", "ar": "العائلة"],
        "action.send": ["en": "Send", "es": "Enviar", "fr": "Envoyer",
                        "de": "Senden", "pt": "Enviar", "it": "Invia",
                        "ja": "送信", "zh": "发送", "hi": "भेजें", "ar": "إرسال"],
        "action.save": ["en": "Save", "es": "Guardar", "fr": "Enregistrer",
                        "de": "Speichern", "pt": "Salvar", "it": "Salva",
                        "ja": "保存", "zh": "保存", "hi": "सहेजें", "ar": "حفظ"],
        "action.translate": ["en": "Translate", "es": "Traducir", "fr": "Traduire",
                             "de": "Übersetzen", "pt": "Traduzir", "it": "Traduci",
                             "ja": "翻訳", "zh": "翻译", "hi": "अनुवाद", "ar": "ترجمة"],
        "action.sign_out": ["en": "Sign out", "es": "Cerrar sesión", "fr": "Se déconnecter",
                            "de": "Abmelden", "pt": "Sair", "it": "Esci",
                            "ja": "サインアウト", "zh": "退出登录", "hi": "साइन आउट",
                            "ar": "تسجيل الخروج"],
        "action.refresh": ["en": "Refresh", "es": "Actualizar", "fr": "Actualiser",
                           "de": "Aktualisieren", "pt": "Atualizar", "it": "Aggiorna",
                           "ja": "更新", "zh": "刷新", "hi": "रीफ़्रेश", "ar": "تحديث"],
    ]
}
