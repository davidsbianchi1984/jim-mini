import Foundation

/// The three settings of the sensitivity dial, in the reader's language.
///
/// A switch rather than one lookup on a key built by concatenating the
/// prefix with the API value, which is shorter and wrong: a key assembled
/// at runtime is a key no guard can find. The dead-key check reads literals,
/// so a row asked for only that way reads as *nothing asks for this* — and
/// the fix somebody reaches for when a guard says that is to delete the row.
///
///     asked     does the screen ask the table for this word
///     mattered  can anything tell that it does
///
/// Two screens need it: the dial itself on Safety, and the Family card that
/// names the level a new child's account was created with. Windows keeps its
/// own copy in each page because its `L10n.T` takes the language from
/// `AppState`.
func sensitivityLabel(_ level: String, _ lang: String) -> String {
    switch level {
    case "cautious": return L10n.t("cw.cautious", lang)
    case "assertive": return L10n.t("cw.assertive", lang)
    default: return L10n.t("cw.balanced", lang)
    }
}
