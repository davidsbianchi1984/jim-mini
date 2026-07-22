package app.jim.guardian.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

/** JIM-mini / Guardian dark-OLED palette. */
object Jim {
    val ScrTop = Color(0xFF0E1626)
    val ScrBot = Color(0xFF0A0F1C)
    val Card = Color(0xFF182238)
    val Line = Color(0xFF26314E)
    val Txt = Color(0xFFEEF1F7)
    val T2 = Color(0xFF8A94AD)
    val T3 = Color(0xFF626D88)
    val BrandA = Color(0xFF7C5CFF)
    val BrandB = Color(0xFF3AA0FF)
    val Green = Color(0xFF43E08A)
    val Red = Color(0xFFFF3B30)
    val Amber = Color(0xFFF7B731)
    val Brand = Brush.linearGradient(listOf(BrandA, BrandB))
    val Bg = Brush.verticalGradient(listOf(ScrTop, ScrBot))
}

private val JimColors = darkColorScheme(
    primary = Jim.BrandA,
    background = Jim.ScrBot,
    surface = Jim.Card,
    onPrimary = Color.White,
    onBackground = Jim.Txt,
    onSurface = Jim.Txt,
)

@Composable
fun JimTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = JimColors, typography = Typography()) {
        Surface(color = Jim.ScrBot, content = content)
    }
}

/** Rounded, hairline-bordered card surface used across every screen. */
fun Modifier.card(): Modifier =
    this
        .clip(RoundedCornerShape(16.dp))
        .background(Jim.Card.copy(alpha = 0.9f))
        .border(1.dp, Jim.Line, RoundedCornerShape(16.dp))
        .padding(16.dp)
