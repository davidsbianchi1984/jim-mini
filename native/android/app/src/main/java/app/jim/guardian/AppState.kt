package app.jim.guardian

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.launch

/**
 * App-wide state: the enrolled identity + token (persisted to SharedPreferences)
 * and the async calls the screens invoke.
 */
class GuardianViewModel(app: Application) : AndroidViewModel(app) {
    private val prefs = app.getSharedPreferences("jim", 0)

    var uid by mutableStateOf<String?>(prefs.getString("uid", null))
        private set
    var token by mutableStateOf<String?>(prefs.getString("token", null))
        private set
    var displayName by mutableStateOf(prefs.getString("name", "") ?: "")
        private set
    // The user's chosen language also drives the app chrome via L10n.
    var language by mutableStateOf(prefs.getString("lang", "en") ?: "en")
        private set

    fun rememberLanguage(code: String) {
        language = code
        prefs.edit().putString("lang", code).apply()
    }

    val isEnrolled get() = uid != null && token != null

    fun enroll(name: String, birthdate: String, language: String? = null,
               onError: (String) -> Unit, onBusy: (Boolean) -> Unit) {
        onBusy(true)
        viewModelScope.launch {
            runCatching { ApiClient.enroll(name, birthdate, language) }
                .onSuccess { r ->
                    uid = r.id; token = r.userToken; displayName = r.displayName
                    prefs.edit().putString("uid", r.id).putString("token", r.userToken)
                        .putString("name", r.displayName).apply()
                }
                .onFailure { onError(it.message ?: "Couldn't reach your Guardian — is the backend running?") }
            onBusy(false)
        }
    }

    fun signOut() {
        uid = null; token = null; displayName = ""
        prefs.edit().clear().apply()
    }

    fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {
        viewModelScope.launch { onResult(runCatching { block() }) }
    }
}
