package app.jim.guardian

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.viewmodel.compose.viewModel
import app.jim.guardian.ui.Jim
import app.jim.guardian.ui.JimTheme
import app.jim.guardian.ui.CareScreen
import app.jim.guardian.ui.ConnectScreen
import app.jim.guardian.ui.LifeScreen
import app.jim.guardian.ui.OverviewScreen
import app.jim.guardian.ui.SafetyScreen
import app.jim.guardian.ui.WelcomeScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            JimTheme {
                val vm: GuardianViewModel = viewModel()
                if (!vm.isEnrolled) {
                    WelcomeScreen(vm)
                } else {
                    HomeShell(vm)
                }
            }
        }
    }
}

@androidx.compose.runtime.Composable
private fun HomeShell(vm: GuardianViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf(
        Triple(L10n.t("tab.overview", vm.language), Icons.Filled.GridView, 0),
        Triple(L10n.t("tab.care", vm.language), Icons.Filled.Favorite, 1),
        Triple(L10n.t("tab.life", vm.language), Icons.Filled.Star, 2),
        Triple(L10n.t("tab.safety", vm.language), Icons.Filled.Warning, 3),
        Triple(L10n.t("tab.connect", vm.language), Icons.Filled.Link, 4),
    )
    Scaffold(
        containerColor = Jim.ScrBot,
        bottomBar = {
            NavigationBar(containerColor = Color(0xFF0B1220)) {
                tabs.forEach { (label, icon, index) ->
                    NavigationBarItem(
                        selected = tab == index,
                        onClick = { tab = index },
                        icon = { Icon(icon, contentDescription = label) },
                        label = { Text(label) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Jim.BrandA,
                            selectedTextColor = Jim.BrandA,
                            unselectedIconColor = Jim.T2,
                            unselectedTextColor = Jim.T2,
                            indicatorColor = Color(0x337C5CFF),
                        ),
                    )
                }
            }
        },
    ) { pad ->
        Box(Modifier.fillMaxSize().background(Jim.Bg).padding(pad)) {
            when (tab) {
                0 -> OverviewScreen(vm)
                1 -> CareScreen(vm)
                2 -> LifeScreen(vm)
                3 -> SafetyScreen(vm)
                else -> ConnectScreen(vm)
            }
        }
    }
}
