using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Windows.UI;

namespace JimGuardian.Views;

/// <summary>The jim-mini OS lockup — the whole mark, as the ABRACADABRA menu
/// button. The wordmark, the triangle and the OS plate are in the XAML; the
/// eleven rows of the descent are built here.
///
/// <para>Built in code rather than typed out as eleven <c>TextBlock</c>s:
/// the rows are ABRACADABRA one letter shorter each line, which is a fact
/// about the word and not a fact about this file. Written by hand it is
/// eleven chances to drop a letter, and nothing in this repository would
/// catch it — the console builds the same descent the same way.</para></summary>
public sealed partial class JimMiniOSMark : UserControl
{
    private const string Word = "ABRACADABRA";
    /// <summary>Triangle height, and the share of it the letters occupy. The
    /// bottom fifth is empty on purpose — on the amulet the descent stops
    /// above the apex.</summary>
    private const double TriangleHeight = 37;
    private const double LetterBand = 0.78;

    public JimMiniOSMark()
    {
        InitializeComponent();
        var rowHeight = TriangleHeight * LetterBand / Word.Length;
        for (var i = 0; i < Word.Length; i++)
        {
            Descent.Children.Add(new TextBlock
            {
                Text = Word[..(Word.Length - i)],
                FontSize = TriangleHeight * 0.075,
                FontFamily = new FontFamily("Georgia, Times New Roman"),
                Foreground = new SolidColorBrush(
                    Color.FromArgb(0xFF, 0xF4, 0xEF, 0xDC)),
                TextAlignment = Microsoft.UI.Xaml.TextAlignment.Center,
                Height = rowHeight,
                LineHeight = rowHeight,
                HorizontalAlignment = Microsoft.UI.Xaml.HorizontalAlignment.Stretch,
            });
        }
    }
}
