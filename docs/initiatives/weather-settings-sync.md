# Weather settings across Settings and Shell

Local designs: [Shell](../../holonight-shell/docs/sdd/weather-settings-sync.md),
[Settings](../../holonight-settings/docs/sdd/weather-settings-sync.md).

The existing `[weather]` keys remain the cross-repository contract. Settings stages changes;
Save patches the shared product document, and both applications watch that document. Pending
Settings edits retain their existing conflict semantics. No new TOML keys or third-party libraries
are introduced.

- `provider`: `open-meteo` or `openweathermap`; only OpenWeatherMap requires `api_key`.
- `location_source`: `manual` uses a validated coordinate pair or geocodes `city` with optional
  `country`; `auto` requires `geo_api_key` for ipgeolocation.io. Inactive values are preserved.
- `latitude` and `longitude` are optional doubles; zero is valid. Search selections stage the pair,
  city and country together. `lang` controls geocoding names and OpenWeatherMap descriptions;
  Open-Meteo condition descriptions are currently English.
- `temp_unit`, `wind_unit`, `pressure_unit` and display switches apply without a network request.
  `refresh_interval` reschedules polling. Provider, credentials, language and location changes
  cancel obsolete work and refetch, respecting idle/lid pauses.
- Absent provider/source fields preserve legacy OpenWeatherMap coordinate-first/IP fallback.
  Absent individual units use `units`: metric = Celsius/km/h, imperial = Fahrenheit/mph,
  standard = Kelvin/m/s. Pressure defaults to hPa. Explicit fields take precedence.

Build dependency order: build and stage Shell's standalone config package, then configure Settings
against that installed prefix and existing host providers. Do not link repository source targets
across boundaries. Verify the package consumer, focused document/provider/service tests, QML
preferences and layout, lint/import policy and generated qmltypes. Keep temporary config/cache
fixtures isolated; do not install or change live user documents for verification.

API contracts: [Open-Meteo geocoding](https://open-meteo.com/en/docs/geocoding-api),
[Open-Meteo forecast](https://open-meteo.com/en/docs). Air quality is excluded for Open-Meteo;
its AQI is unavailable. Attribution follows the active provider.
