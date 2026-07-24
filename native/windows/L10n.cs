using System.Collections.Generic;

namespace JimGuardian;

/// <summary>
/// App-chrome localization: nav names and the most common actions, in every
/// language the backend supports. Guidance, coaching, and safety content are
/// localized server-side by the user's language setting; this table covers
/// the frame around them. Missing keys fall back to English.
/// </summary>
public static class L10n
{
    public static string T(string key)
    {
        var lang = AppState.Current.Language;
        if (Table.TryGetValue(key, out var row))
            return row.TryGetValue(lang, out var s) ? s
                 : row.TryGetValue("en", out var en) ? en : key;
        return key;
    }

    private static readonly Dictionary<string, Dictionary<string, string>> Table = new()
    {
        ["tab.overview"] = new() { ["en"] = "Overview", ["es"] = "Resumen", ["fr"] = "Aperçu", ["de"] = "Übersicht", ["pt"] = "Visão geral", ["it"] = "Panoramica", ["ja"] = "概要", ["zh"] = "概览", ["hi"] = "अवलोकन", ["ar"] = "نظرة عامة" },
        ["tab.monitor"] = new() { ["en"] = "Live Monitoring", ["es"] = "Monitoreo", ["fr"] = "Surveillance", ["de"] = "Überwachung", ["pt"] = "Monitoramento", ["it"] = "Monitoraggio", ["ja"] = "モニタリング", ["zh"] = "实时监测", ["hi"] = "निगरानी", ["ar"] = "المراقبة" },
        ["tab.checkin"] = new() { ["en"] = "Check-in", ["es"] = "Registro", ["fr"] = "Bilan", ["de"] = "Check-in", ["pt"] = "Check-in", ["it"] = "Check-in", ["ja"] = "チェックイン", ["zh"] = "签到", ["hi"] = "चेक-इन", ["ar"] = "تسجيل الحالة" },
        ["tab.coach"] = new() { ["en"] = "Coach", ["es"] = "Coach", ["fr"] = "Coach", ["de"] = "Coach", ["pt"] = "Coach", ["it"] = "Coach", ["ja"] = "コーチ", ["zh"] = "教练", ["hi"] = "कोच", ["ar"] = "مدرب" },
        ["tab.life"] = new() { ["en"] = "Life", ["es"] = "Vida", ["fr"] = "Vie", ["de"] = "Leben", ["pt"] = "Vida", ["it"] = "Vita", ["ja"] = "ライフ", ["zh"] = "生活", ["hi"] = "जीवन", ["ar"] = "الحياة" },
        ["tab.safety"] = new() { ["en"] = "Safety", ["es"] = "Seguridad", ["fr"] = "Sécurité", ["de"] = "Sicherheit", ["pt"] = "Segurança", ["it"] = "Sicurezza", ["ja"] = "安全", ["zh"] = "安全", ["hi"] = "सुरक्षा", ["ar"] = "السلامة" },
        ["tab.connect"] = new() { ["en"] = "Connect", ["es"] = "Conectar", ["fr"] = "Connecter", ["de"] = "Verbinden", ["pt"] = "Conectar", ["it"] = "Connetti", ["ja"] = "接続", ["zh"] = "连接", ["hi"] = "कनेक्ट", ["ar"] = "اتصال" },
        ["tab.custody"] = new() { ["en"] = "Vault Custody", ["es"] = "Custodia", ["fr"] = "Conservation", ["de"] = "Verwahrung", ["pt"] = "Custódia", ["it"] = "Custodia", ["ja"] = "保管", ["zh"] = "保管记录", ["hi"] = "अभिरक्षा", ["ar"] = "الحفظ" },
        ["tab.family"] = new() { ["en"] = "Family", ["es"] = "Familia", ["fr"] = "Famille", ["de"] = "Familie", ["pt"] = "Família", ["it"] = "Famiglia", ["ja"] = "家族", ["zh"] = "家庭", ["hi"] = "परिवार", ["ar"] = "العائلة" },
        ["action.send"] = new() { ["en"] = "Send", ["es"] = "Enviar", ["fr"] = "Envoyer", ["de"] = "Senden", ["pt"] = "Enviar", ["it"] = "Invia", ["ja"] = "送信", ["zh"] = "发送", ["hi"] = "भेजें", ["ar"] = "إرسال" },
        ["action.save"] = new() { ["en"] = "Save", ["es"] = "Guardar", ["fr"] = "Enregistrer", ["de"] = "Speichern", ["pt"] = "Salvar", ["it"] = "Salva", ["ja"] = "保存", ["zh"] = "保存", ["hi"] = "सहेजें", ["ar"] = "حفظ" },
        ["action.translate"] = new() { ["en"] = "Translate", ["es"] = "Traducir", ["fr"] = "Traduire", ["de"] = "Übersetzen", ["pt"] = "Traduzir", ["it"] = "Traduci", ["ja"] = "翻訳", ["zh"] = "翻译", ["hi"] = "अनुवाद", ["ar"] = "ترجمة" },
        ["action.refresh"] = new() { ["en"] = "Refresh", ["es"] = "Actualizar", ["fr"] = "Actualiser", ["de"] = "Aktualisieren", ["pt"] = "Atualizar", ["it"] = "Aggiorna", ["ja"] = "更新", ["zh"] = "刷新", ["hi"] = "रीफ़्रेश", ["ar"] = "تحديث" },
    };
}
