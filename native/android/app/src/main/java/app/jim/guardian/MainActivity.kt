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
import androidx.compose.material.icons.filled.Spa
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
import app.jim.guardian.ui.CheckinScreen
import app.jim.guardian.ui.MonitorScreen
import app.jim.guardian.ui.OverviewScreen
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
        Triple("Overview", Icons.Filled.GridView, 0),
        Triple("Monitor", Icons.Filled.Favorite, 1),
        Triple("Check-in", Icons.Filled.Spa, 2),
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
                1 -> MonitorScreen(vm)
                else -> CheckinScreen(vm)
            }
        }
    }
}
