package app.jim.guardian.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * The jim-mini OS lockup — the whole mark, as the ABRACADABRA menu button.
 *
 * Three stacked parts in the proportions of the artwork: the neon wordmark,
 * the amulet triangle with ABRACADABRA descending eleven rows, and the OS
 * plate. The console draws the same lockup from the same numbers
 * (`app/src/JimMiniOS.tsx`, `assets/brand/jim-mini-os.svg`).
 *
 *     asked     is the mark on the button
 *     mattered  is the whole mark on the button, big enough to read as itself
 *
 * **Built from layout and one Path, not from a canvas with text drawn into
 * it.** Text on a canvas means reaching for `nativeCanvas` and measuring
 * glyphs by hand; `Text` in a `Column` is the same drawing with the layout
 * engine doing the arithmetic, and it is the shape this shell already knows
 * how to render. The only hand-drawn thing is the triangle, which is three
 * points.
 *
 * Every dimension is a fraction of the requested size, so the mark is one
 * mark whether it sits on a tab strip or fills a splash. The fractions are
 * passed down as a plain `Float` rather than read back off a layout: inside a
 * `Canvas` the name `size` means the draw scope's size, and a composable that
 * silently measured the wrong thing is the sort of defect that only shows up
 * on a device.
 */
private val ROWS: List<String> = (0 until 11).map { "ABRACADABRA".take(11 - it) }

private val NEON = Color(0xFFE9F04E)
private val PARCHMENT = Color(0xFFF4EFDC)
private val TRIANGLE_FILL = Color(0xFF15120A)
private val EDGE = Brush.linearGradient(
    listOf(Color(0xFFDFE94B), Color(0xFFF2C230), Color(0xFFB8861F)))

/** The share of the triangle's height the letters occupy. The bottom fifth
 *  is empty on purpose — on the amulet the descent stops above the apex. */
private const val LETTER_BAND = 0.78f

@Composable
fun JimMiniOSMark(size: Dp = 72.dp) {
    val px = size.value
    Box(
        Modifier.size(size).background(Color.Black),
        contentAlignment = Alignment.TopCenter,
    ) {
        Column(
            Modifier.fillMaxWidth().padding(vertical = (px * 0.05f).dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top,
        ) {
            Text(
                "jim-mini",
                color = NEON,
                fontSize = (px * 0.15f).sp,
                fontStyle = FontStyle.Italic,
                fontFamily = FontFamily.Cursive,
                fontWeight = FontWeight.Medium,
                textAlign = TextAlign.Center,
                modifier = Modifier.height((px * 0.22f).dp),
            )
            AmuletTriangle(px)
            Box(
                Modifier
                    .padding(top = (px * 0.01f).dp)
                    .width((px * 0.82f).dp)
                    .height((px * 0.21f).dp)
                    .background(Color.White),
                contentAlignment = Alignment.Center,
            ) {
                Text("OS", color = Color.Black, fontSize = (px * 0.17f).sp,
                    fontWeight = FontWeight.Black)
            }
        }
    }
}

@Composable
private fun AmuletTriangle(px: Float) {
    val width = px * 0.42f
    val height = px * 0.37f
    Box(Modifier.width(width.dp).height(height.dp)) {
        Canvas(Modifier.matchParentSize()) {
            val path = Path().apply {
                moveTo(0f, 0f)
                lineTo(size.width, 0f)
                lineTo(size.width / 2f, size.height)
                close()
            }
            drawPath(path, TRIANGLE_FILL)
            drawPath(path, EDGE,
                style = Stroke(width = maxOf(1f, size.width * 0.05f)))
        }
        Column(
            Modifier
                .fillMaxWidth()
                .height((height * LETTER_BAND).dp)
                .padding(top = (height * 0.04f).dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            ROWS.forEach { row ->
                Text(
                    row,
                    color = PARCHMENT,
                    fontSize = (height * 0.075f).sp,
                    fontFamily = FontFamily.Serif,
                    maxLines = 1,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }
}
