# PhotoDashPlus(Wear OS Watch Face Format)

Dimmed photo background + bold digital time + four data arcs.

Layout follows Samsung's Health Dashboard+ (geometry and colors taken from
its APK; each gauge fills one quadrant):
- Steps (9 -> 12 o'clock, complication, default step count) and battery
  (3 -> 6 o'clock, complication, default watch battery). The number rides just
  past the fill tip, and moves inside the fill in black once the fill passes 62°.
- Heart rate ticks (inner, 9 -> 12): gradient scale 40-220 bpm, an arrow marks
  the current rate with the reading centered on it. Read directly from the watch.
- UV ticks (inner, 3 -> 6): fill = UV index (0-11), level word on the fill tip.
- Date, weather-condition icon and temperature on one curved line, lower left
  (watch weather; icons are drawn by the generator, moon variants at night).
- Pickable, no default: action pill under the clock, three stats along the
  top right (green/blue/pink dots), and a round complication top right
  (ring = progress for ranged/goal data, icon over value).
- AM/PM only in 12-hour mode. Everything but the clock hides in always-on mode.
Font: Quicksand throughout (SIL OFL - licenses/Quicksand-OFL.txt), bundled in
res/font as static weights of the variable font (no regular: the lightest text uses medium). Quicksand has a Reserved Font
Name, so these modified copies are renamed "BU Rounded" (rounded_*.ttf).
FONTS/CLOCK_FONT in the generator pick the files; rounded_medium_bigdot is a
generated copy with a 1.6x bullet for the stats dots. The bpm and UV text use
Inter (SIL OFL, no Reserved Font Name - licenses/Inter-OFL.txt), inter_*.ttf.
Colors: Samsung's three themes (Lime mint, Coral pink, Blue violet) plus Berry,
Orchid, Sunset, Ocean, Ember, Mono.

Heart rate / UV / weather aren't complication slots: on Wear OS a slot with
no provider draws nothing, and there are no system providers for them.

## Editing
watchface.xml is generated: edit tools/generate.py (geometry, themes, photo
dimming PHOTO_ALPHA) and run `python3 tools/generate.py` (needs Pillow).
Runtime quirks the generator works around:
- Gradient `colors` can't use [CONFIGURATION...] colors: a tinted white alpha
  gradient is layered over solid color A instead.
- Slot content is clipped to its BoundingArc/BoundingBox region, so each
  slot's region must cover everything it draws (icons included).
- Part/slot geometry attributes are parsed as integers.
- TextCircular text is centered on its circle (not sat on it as a baseline).
- Text shadows: a <Shadow> wrapped around the Template. TimeText ignores it, so
  the clock is drawn as text from [HOUR_*]/[MINUTE].
- [WEATHER.CONDITION] codes: see WEATHER_ICONS in the generator.
- COUNTER_CLOCKWISE TextCircular needs startAngle > endAngle.
- The watch stores slot assignments by position: adding/removing/reordering
  ComplicationSlots shifts existing assignments, so re-pick them in the editor.

## Build & install (Linux)
    # needs JDK 17+ and Android SDK (set sdk.dir in local.properties)
    ./gradlew :photodashplus:assembleDebug
    adb connect <watch-ip>:<port>      # Wireless debugging on the watch
    adb install watchface/build/outputs/apk/debug/watchface-debug.apk
    # then set it: press-and-hold face > pick "Bold Utility"
    # (some Wear OS versions need: adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId com.alexankitty.photodashplus)
