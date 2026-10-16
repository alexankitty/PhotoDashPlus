<p align="center">
  <img width="426" height="426" alt="Photo Dash Plus watch face" src="https://github.com/user-attachments/assets/01481fee-6953-4d3b-b57e-4a30200969e5" />
</p>

# Photo Dash Plus

A Wear OS watch face built with the Watch Face Format: your own photo,
dimmed behind a bold digital clock, with four data arcs around the edge.

The layout is a remake of Samsung's Health Dashboard+, with its geometry and
colors taken from that face's APK. Photo Dash Plus adds a custom photo
background and more themes.

## Features

- **Photo background.** Pick any photo in the watch face editor. It's dimmed
  so the arcs and text stay readable.
- **Steps arc** (9 → 12 o'clock) and **battery arc** (3 → 6 o'clock). Both
  are complication slots, defaulting to step count and watch battery. The
  value follows the tip of the fill. They can also be set to **fixed** step
  count and battery that don't open an app when tapped (see Customization).
- **Heart rate scale** (inner, 9 → 12): a 40–220 bpm gradient with an arrow
  at your current rate. The face reads this from the watch sensor.
- **UV scale** (inner, 3 → 6): fills by UV index (0–11) and labels it
  low / moderate / high / very high / extreme.
- **Date, weather icon and temperature** on a curved line at the lower left.
  At night the icons switch to moon variants.
- **Optional complications** (empty until you pick them):
  - an action pill under the clock
  - three stats along the top right, marked with green, blue and pink dots
  - a round complication at the top right, with a progress ring for ranged
    or goal data
- **Always-on mode** shows everything except the photo.
- AM/PM only appears in 12-hour mode.

## Customization

Long-press the watch face, then tap **Customize**:

| Setting            | Options |
|--------------------|---------|
| Background photo   | Any photo |
| Colors             | Lime mint, Coral pink, Blue violet (Samsung's), Berry, Orchid, Sunset, Ocean, Ember, Mono |
| Health arcs        | Heart rate & UV, Heart rate only, UV only, None |
| Side arcs          | Complications (tappable, pick your own) or fixed Steps & battery |
| Complications      | Steps, Battery, Action button, Stats 1–3, Round complication |

**Side arcs** chooses how the left and right arcs work. As *Complications*
(the default) they're the editable steps/battery slots above, which — like any
Wear OS complication — open their provider's app when tapped. Set to *Steps &
battery*, they're drawn straight from the watch's step and battery data
instead: still the same arcs, but fixed to those two values and with no tap, so
you can't accidentally open the battery app and toggle battery saver. In that
mode those two arcs can't be re-pointed at another provider.

Heart rate, UV and weather aren't complication slots. A Wear OS slot with no
provider draws nothing, and Wear OS has no system providers for these values,
so the face reads them directly.

## Requirements

- Wear OS 6 or newer (Watch Face Format v4, needed for the photo background)
- Heart rate and weather data from the watch, for those elements

## Install

Download the APK from Releases, or build it yourself (see
[DEVELOPING.md](DEVELOPING.md)). Then install it with adb:

    adb connect <watch-ip>:<port>      # turn on Wireless debugging on the watch first
    adb install photodashplus-release.apk

To use it, long-press the current watch face and pick **Photo Dash Plus**.
Some Wear OS versions need this command to set it instead:

    adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE \
        --es operation set-watchface --es watchFaceId com.alexankitty.photodashplus

## Fonts & licenses

- [Quicksand](https://github.com/andrew-paglinawan/QuicksandFamily) (SIL OFL,
  [licenses/Quicksand-OFL.txt](licenses/Quicksand-OFL.txt)). Used for most
  text. Quicksand has a Reserved Font Name, so the modified copies bundled
  here are renamed "BU Rounded".
- [Inter](https://github.com/rsms/inter) (SIL OFL,
  [licenses/Inter-OFL.txt](licenses/Inter-OFL.txt)). Used for the bpm and UV
  text.

Photo Dash Plus is an independent remake and has no affiliation with Samsung.
