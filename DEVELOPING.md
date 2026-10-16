# Developing Photo Dash Plus

## Layout

    photodashplus/src/main/res/raw/watchface.xml   generated, don't edit by hand
    photodashplus/src/main/res/drawable/           weather icons, preview, default photo (partly generated)
    photodashplus/src/main/res/font/               bundled fonts (rounded_medium_bigdot is generated)
    photodashplus/src/main/res/values/strings.xml  editor labels
    tools/generate.py                              generates the face
    build-release.sh                               signed release build

## Editing the face

`watchface.xml` is generated because the gauges repeat the same drawing for
every complication type and every gradient layer. Make changes in
`tools/generate.py`, then run it from the repo root:

    python3 tools/generate.py      # needs Pillow

Settings in the generator:
- Geometry: Samsung's 360px canvas, scaled by `S` to the 450px WFF canvas.
  Angles follow WFF: 0 = 12 o'clock, clockwise.
- `PHOTO_ALPHA` sets how much the photo is dimmed (0 = black, 255 = full
  brightness).
- `SAMSUNG_THEMES` and `EXTRA_THEMES` define the colors. Extra themes are
  derived from two base colors.
- `TEXT_INSIDE_AFTER` sets how far the arc fills (62° by default) before its
  number moves inside the fill and turns black.
- `FONTS` and `CLOCK_FONT` choose the font files. `BULLET_SCALE` sets the
  size of the enlarged bullet in `rounded_medium_bigdot`, which the stats
  dots use.
- `WEATHER_ICONS` and `NIGHT_ICONS` map `[WEATHER.CONDITION]` codes to icons.
  The generator draws the icons.

### Fonts

Quicksand is bundled as static weights of the variable font. The set has no
regular weight because regular is too faint at watch size, so the lightest
text uses medium. Quicksand has a Reserved Font Name, so the modified copies
are renamed "BU Rounded" (`rounded_*.ttf`). Inter has no Reserved Font Name,
so its files (`inter_*.ttf`) keep the name.

### WFF runtime quirks the generator works around

- A gradient's `colors` can't use `[CONFIGURATION...]` colors. To get a
  gradient, the generator draws solid color A and layers a tinted white alpha
  gradient over it.
- Slot content is clipped to its BoundingArc/BoundingBox, so each slot's
  region must cover everything the slot draws, icons included.
- Part and slot geometry attributes are parsed as integers.
- TextCircular text is centered on its circle, not placed on it as a
  baseline.
- COUNTER_CLOCKWISE TextCircular needs `startAngle > endAngle`.
- To shadow text, wrap the Template in a `<Shadow>`. TimeText ignores the
  shadow, so the clock is drawn as text from `[HOUR_*]`/`[MINUTE]`.
- The system editor clips boolean switches, so "Health arcs" and "Side arcs"
  are ListConfigurations, not BooleanConfigurations.
- A complication slot is always tappable and launches its provider's app;
  WFF has no attribute to disable that. So the "Side arcs" setting instead
  switches the arcs between the slots (tappable) and copies drawn straight
  from `STEP_COUNT`/`BATTERY_PERCENT` (no slot, so no tap). The `arcMode`
  ListOption's `complicationSlotIds` enables slots 0 and 2 only on the
  "custom" option; the "fixed" option leaves them off and the scene draws
  the source versions. The fixed step count has no thousands separator (the
  complication's formatted text did).
- The `STEP_COUNT` system provider sends a value but no icon, so the steps
  slot draws a bundled `steps_icon` under the provider's image as a fallback.
- The watch stores slot assignments by position. If you add, remove or
  reorder ComplicationSlots, existing assignments shift and need to be
  re-picked in the editor.

## Build (Linux)

Requires JDK 17+ and the Android SDK (set `sdk.dir` in `local.properties`).

    ./gradlew :photodashplus:assembleDebug
    adb connect <watch-ip>:<port>      # turn on Wireless debugging on the watch first
    adb install photodashplus/build/outputs/apk/debug/photodashplus-debug.apk

### Release

Release builds must be signed. Set the signing values in `local.properties`
(gitignored) or in environment variables:

| local.properties        | Environment              | Default |
|-------------------------|--------------------------|---------|
| `release.storeFile`     | `RELEASE_STORE_FILE`     | (none) |
| `release.storePassword` | `RELEASE_STORE_PASSWORD` | (none) |
| `release.keyAlias`      | `RELEASE_KEY_ALIAS`      | `photodashplus` |
| `release.keyPassword`   | `RELEASE_KEY_PASSWORD`   | store password |

Then run `./gradlew :photodashplus:assembleRelease`. The build fails if
signing isn't set up, so it never produces an unsigned APK.
`build-release.sh` asks for the keystore password and runs this build. Its
keystore path is hardcoded, so edit it to match your setup.
