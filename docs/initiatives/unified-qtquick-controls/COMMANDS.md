# UQC-201 executed command record

Date: 2026-09-09. This is a transcript, not an unattended script: it includes
failed attempts retained for review. See [results and interpretation](INTEGRATION.md).
Paths are normalized to `UQC_ROOT` (the umbrella root). Each result records the
actual process exit status; the wrapper private D-Bus/XDG scope ends after each
command. No live authentication commands appear here.

```sh
UQC_ROOT="$PWD"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
UV_CACHE_DIR=/tmp/uqc201-uv-cache uv run --with patchelf --no-project python -c 'import shutil; print(shutil.which("patchelf"))'
```

The returned patchelf path is the one used in the configure commands below.
A future run must use its own returned path and fresh private build directories.
Initial `.source-install` failure commands are retained in that directory's
`results.jsonl`; the active-path transcript follows.

## Dependency order

`config-configure`: exit **0**, 0.25 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake -S "$UQC_ROOT/holonight-config" -B "$UQC_ROOT/.cache/uqc201/build/config" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTING=ON
```

`config-build`: exit **0**, 1.16 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --build "$UQC_ROOT/.cache/uqc201/build/config" -j 6
```

`config-full`: exit **0**, 0.71 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/config" --output-on-failure --no-tests=error -j 4
```

`config-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --install "$UQC_ROOT/.cache/uqc201/build/config"
```

`system-services-configure`: exit **0**, 0.54 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake -S "$UQC_ROOT/holonight-system-services" -B "$UQC_ROOT/.cache/uqc201/build/system-services" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`system-services-build`: exit **0**, 5.01 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --build "$UQC_ROOT/.cache/uqc201/build/system-services" -j 6
```

`system-services-full`: exit **0**, 9.67 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/system-services" --output-on-failure --no-tests=error -j 4
```

`system-services-install`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --install "$UQC_ROOT/.cache/uqc201/build/system-services"
```

`shell-config-configure`: exit **0**, 0.50 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake -S "$UQC_ROOT/holonight-shell/libs/holonight-shell-config" -B "$UQC_ROOT/.cache/uqc201/build/shell-config" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4
```

`shell-config-build`: exit **0**, 2.23 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --build "$UQC_ROOT/.cache/uqc201/build/shell-config" -j 6
```

`shell-config-install`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --install "$UQC_ROOT/.cache/uqc201/build/shell-config"
```

`qt-configure`: exit **0**, 1.67 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake -S "$UQC_ROOT/holonight-qt" -B "$UQC_ROOT/.cache/uqc201/build/qt" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON -DBUILD_DEMO=ON -DBUILD_CONTROLS_GALLERY=ON -DHOLONIGHT_PATCHELF_EXECUTABLE=/tmp/uqc201-uv-cache/archive-v0/mVGV6ox16yY-nm-6uMj4N/bin/patchelf
```

`qt-build`: exit **0**, 66.25 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
cmake --build "$UQC_ROOT/.cache/uqc201/build/qt" -j 6
```

`qt-focused`: exit **0**, 7.88 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`qt-full`: exit **8**, 17.77 s.

```sh
cd "$UQC_ROOT"
unset LD_LIBRARY_PATH
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" --output-on-failure --no-tests=error -j 4
```

`qt-configure`: exit **0**, 0.87 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-qt" -B "$UQC_ROOT/.cache/uqc201/build/qt" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON -DBUILD_DEMO=ON -DBUILD_CONTROLS_GALLERY=ON -DHOLONIGHT_PATCHELF_EXECUTABLE=/tmp/uqc201-uv-cache/archive-v0/mVGV6ox16yY-nm-6uMj4N/bin/patchelf
```

`qt-build`: exit **0**, 0.06 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/qt" -j 6
```

`qt-focused`: exit **0**, 7.74 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`qt-full`: exit **0**, 44.66 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" --output-on-failure --no-tests=error -j 4
```

`qt-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/qt"
```

`appearance-adapters-configure`: exit **0**, 0.80 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-appearance-adapters" -B "$UQC_ROOT/.cache/uqc201/build/appearance-adapters" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTING=ON "-DHOLONIGHT_QT_DIR=$UQC_ROOT/.cache/uqc201/prefix" "-DHOLONIGHT_CONFIG_DIR=$UQC_ROOT/.cache/uqc201/prefix"
```

`appearance-adapters-build`: exit **0**, 3.32 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/appearance-adapters" -j 6
```

`appearance-adapters-full`: exit **0**, 0.11 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/appearance-adapters" --output-on-failure --no-tests=error -j 4
```

`appearance-adapters-install`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/appearance-adapters"
```

`shell-configure`: exit **0**, 1.77 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-shell" -B "$UQC_ROOT/.cache/uqc201/build/shell" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`shell-build`: exit **0**, 264.48 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/shell" -j 6
```

`shell-focused`: exit **0**, 131.66 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/shell" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`shell-full`: exit **8**, 152.85 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/shell" --output-on-failure --no-tests=error -j 4
```

`shell-configure`: exit **0**, 0.84 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-shell" -B "$UQC_ROOT/.cache/uqc201/build/shell" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`shell-build`: exit **0**, 0.04 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/shell" -j 6
```

`shell-focused`: exit **0**, 2.62 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/shell" -R QtNetworkManagerBackendTest --output-on-failure -j 1
```

`shell-full`: exit **0**, 226.93 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/shell" --output-on-failure --no-tests=error -j 1
```

`shell-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/shell"
```

`settings-configure`: exit **0**, 1.04 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-settings" -B "$UQC_ROOT/.cache/uqc201/build/settings" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`settings-build`: exit **0**, 26.60 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/settings" -j 6
```

`settings-focused`: exit **0**, 12.64 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/settings" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 1
```

`settings-full`: exit **0**, 43.49 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/settings" --output-on-failure --no-tests=error -j 1
```

`settings-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/settings"
```

`ai-configure`: exit **0**, 1.59 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-ai" -B "$UQC_ROOT/.cache/uqc201/build/ai" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`ai-build`: exit **0**, 151.53 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/ai" -j 6
```

`ai-focused`: exit **0**, 18.53 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`ai-full`: exit **0**, 29.60 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" --output-on-failure --no-tests=error -j 4
```

`ai-install`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/ai"
```

`pkg-manager-configure`: exit **0**, 0.94 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-pkg-manager" -B "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTS=ON
```

`pkg-manager-build`: exit **0**, 48.91 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -j 6
```

`pkg-manager-focused`: exit **0**, 9.85 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`pkg-manager-full`: exit **0**, 9.63 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/pkg-manager" --output-on-failure --no-tests=error -j 4
```

`pkg-manager-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/pkg-manager"
```

`greeter-configure`: exit **0**, 1.68 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake -S "$UQC_ROOT/holonight-greeter" -B "$UQC_ROOT/.cache/uqc201/build/greeter" -G Ninja -DCMAKE_BUILD_TYPE=Debug "-DCMAKE_INSTALL_PREFIX=$UQC_ROOT/.cache/uqc201/prefix" "-DCMAKE_PREFIX_PATH=$UQC_ROOT/.cache/uqc201/prefix" -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DBUILD_TESTING=ON
```

`greeter-build`: exit **0**, 31.46 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --build "$UQC_ROOT/.cache/uqc201/build/greeter" -j 6
```

`greeter-focused`: exit **0**, 2.49 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/greeter" -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
```

`greeter-full`: exit **0**, 6.52 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/greeter" --output-on-failure --no-tests=error -j 4
```

`greeter-install`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
cmake --install "$UQC_ROOT/.cache/uqc201/build/greeter"
```


## Launch and additional style checks

`ai-build-launches`: exit **0**, 12.93 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-ai/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/build/ai/holonight-chat" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/ai-build-launches"
```

`ai-installed-launches`: exit **0**, 12.94 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-ai/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-chat" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/ai-installed-launches" --forbid-path "$UQC_ROOT/.cache/uqc201/build"
```

`pkg-manager-build-launches`: exit **0**, 12.67 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-pkg-manager/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/build/pkg-manager/holonight-packages" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/pkg-manager-build-launches"
```

`pkg-manager-installed-launches`: exit **0**, 12.69 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-pkg-manager/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-packages" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/pkg-manager-installed-launches" --forbid-path "$UQC_ROOT/.cache/uqc201/build"
```

`greeter-build-launches`: exit **0**, 12.42 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-greeter/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/build/greeter/holonight-greeter" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/greeter-build-launches"
```

`greeter-installed-launches`: exit **0**, 12.44 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-greeter/scripts/check-runtime-launches.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-greeter" "$UQC_ROOT/.cache/uqc201/prefix" --logs "$UQC_ROOT/.cache/uqc201/logs/greeter-installed-launches" --forbid-path "$UQC_ROOT/.cache/uqc201/build"
```

`settings-installed-default`: exit **0**, 3.21 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-settings/tests/check_settings_startup.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-settings" "$UQC_ROOT/.cache/uqc201/prefix/lib/qt6/qml" default --forbid-qml-root "$UQC_ROOT/.cache/uqc201/build"
```

`settings-installed-environment`: exit **0**, 3.20 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-settings/tests/check_settings_startup.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-settings" "$UQC_ROOT/.cache/uqc201/prefix/lib/qt6/qml" environment --forbid-qml-root "$UQC_ROOT/.cache/uqc201/build"
```

`settings-installed-command-line`: exit **0**, 3.22 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-settings/tests/check_settings_startup.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-settings" "$UQC_ROOT/.cache/uqc201/prefix/lib/qt6/qml" command-line --forbid-qml-root "$UQC_ROOT/.cache/uqc201/build"
```

`settings-installed-configuration`: exit **0**, 3.21 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-settings/tests/check_settings_startup.py" "$UQC_ROOT/.cache/uqc201/prefix/bin/holonight-settings" "$UQC_ROOT/.cache/uqc201/prefix/lib/qt6/qml" configuration --forbid-qml-root "$UQC_ROOT/.cache/uqc201/build"
```

`ai-source-Holonight`: exit **0**, 15.85 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Holonight
unset QT_SCALE_FACTOR
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" -R 'Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock' --output-on-failure -j 4
```

`ai-source-Fusion`: exit **8**, 15.78 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Fusion
unset QT_SCALE_FACTOR
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" -R 'Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock' --output-on-failure -j 4
```

`pkg-manager-source-Holonight`: exit **0**, 1.25 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Holonight
unset QT_SCALE_FACTOR
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -R InstalledPackagesViewTest --output-on-failure -j 4
```

`pkg-manager-source-Fusion`: exit **0**, 1.25 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Fusion
unset QT_SCALE_FACTOR
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -R InstalledPackagesViewTest --output-on-failure -j 4
```

`qt-source-Holonight`: exit **0**, 2.60 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Holonight
export QT_SCALE_FACTOR=1.25
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" -R runtime_composites --output-on-failure -j 4
```

`qt-source-Fusion`: exit **0**, 2.65 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Fusion
export QT_SCALE_FACTOR=1.25
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/qt" -R runtime_composites --output-on-failure -j 4
```

`ai-fusion-focused-recheck`: exit **8**, 0.31 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
export QT_QUICK_CONTROLS_STYLE=Fusion
unset QT_SCALE_FACTOR
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" -R ChatComposerActionsQml.PreservesDesktopAndCompactPresentation --output-on-failure -j 1
```


## Static checks

`qt-format`: exit **0**, 0.28 s.

```sh
cd "$UQC_ROOT/holonight-qt"
cmake --build "$UQC_ROOT/.cache/uqc201/build/qt" --target format-check
```

`qt-lint`: exit **0**, 0.95 s.

```sh
cd "$UQC_ROOT/holonight-qt"
cmake --build "$UQC_ROOT/.cache/uqc201/build/qt" --target all_qmllint
```

`qt-tidy-db`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT/holonight-qt"
cmake -P "$UQC_ROOT/.cache/uqc201/build/qt/strip_tidy_flags.cmake"
```

`qt-tidy`: exit **0**, 338.09 s.

```sh
cd "$UQC_ROOT/holonight-qt"
run-clang-tidy -quiet -j 4 -p "$UQC_ROOT/.cache/uqc201/build/qt/tidy" "^$UQC_ROOT/holonight-qt/"
```

`shell-format`: exit **0**, 0.73 s.

```sh
cd "$UQC_ROOT/holonight-shell"
cmake --build "$UQC_ROOT/.cache/uqc201/build/shell" --target format-check
```

`shell-lint`: exit **0**, 3.36 s.

```sh
cd "$UQC_ROOT/holonight-shell"
cmake --build "$UQC_ROOT/.cache/uqc201/build/shell" --target qml-lint
```

`shell-tidy-db`: exit **1**, 0.00 s.

```sh
cd "$UQC_ROOT/holonight-shell"
cmake -P "$UQC_ROOT/.cache/uqc201/build/shell/strip_tidy_flags.cmake"
```

`shell-tidy`: exit **1**, 0.07 s.

```sh
cd "$UQC_ROOT/holonight-shell"
run-clang-tidy -quiet -j 4 -p "$UQC_ROOT/.cache/uqc201/build/shell/tidy" "^$UQC_ROOT/holonight-shell/"
```

`settings-export-commands`: exit **0**, 0.81 s.

```sh
cd "$UQC_ROOT/holonight-settings"
cmake -S "$UQC_ROOT/holonight-settings" -B "$UQC_ROOT/.cache/uqc201/build/settings" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

`settings-format`: exit **0**, 0.14 s.

```sh
cd "$UQC_ROOT/holonight-settings"
cmake --build "$UQC_ROOT/.cache/uqc201/build/settings" --target format-check
```

`settings-lint`: exit **0**, 1.31 s.

```sh
cd "$UQC_ROOT/holonight-settings"
cmake --build "$UQC_ROOT/.cache/uqc201/build/settings" --target qml-lint
```

`ai-export-commands`: exit **0**, 1.24 s.

```sh
cd "$UQC_ROOT/holonight-ai"
cmake -S "$UQC_ROOT/holonight-ai" -B "$UQC_ROOT/.cache/uqc201/build/ai" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

`ai-format`: exit **0**, 1.12 s.

```sh
cd "$UQC_ROOT/holonight-ai"
cmake --build "$UQC_ROOT/.cache/uqc201/build/ai" --target format-check
```

`ai-lint`: exit **0**, 3.16 s.

```sh
cd "$UQC_ROOT/holonight-ai"
cmake --build "$UQC_ROOT/.cache/uqc201/build/ai" --target qml-lint
```

`settings-tidy`: exit **0**, 205.85 s.

```sh
cd "$UQC_ROOT/holonight-settings"
run-clang-tidy -quiet -j 4 -p "$UQC_ROOT/.cache/uqc201/build/settings" -removed-arg=-mno-direct-extern-access "^$UQC_ROOT/holonight-settings/"
```

`settings-qmltypes`: exit **0**, 0.02 s.

```sh
cd "$UQC_ROOT/holonight-settings"
bash "$UQC_ROOT/holonight-settings/scripts/check-qmltypes.sh" "$UQC_ROOT/.cache/uqc201/build/settings"
```

`pkg-manager-export-commands`: exit **0**, 0.86 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
cmake -S "$UQC_ROOT/holonight-pkg-manager" -B "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

`pkg-manager-format`: exit **0**, 0.25 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
cmake --build "$UQC_ROOT/.cache/uqc201/build/pkg-manager" --target format-check
```

`pkg-manager-lint`: exit **0**, 1.74 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
cmake --build "$UQC_ROOT/.cache/uqc201/build/pkg-manager" --target qml-lint
```

`pkg-manager-tidy`: exit **0**, 55.50 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
run-clang-tidy -quiet -j 4 -p "$UQC_ROOT/.cache/uqc201/build/pkg-manager" -removed-arg=-mno-direct-extern-access "^$UQC_ROOT/holonight-pkg-manager/"
```

`pkg-manager-qmltypes`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
bash "$UQC_ROOT/holonight-pkg-manager/scripts/check-qmltypes.sh" "$UQC_ROOT/.cache/uqc201/build/pkg-manager"
```

`greeter-export-commands`: exit **0**, 1.16 s.

```sh
cd "$UQC_ROOT/holonight-greeter"
cmake -S "$UQC_ROOT/holonight-greeter" -B "$UQC_ROOT/.cache/uqc201/build/greeter" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

`greeter-format`: exit **0**, 0.14 s.

```sh
cd "$UQC_ROOT/holonight-greeter"
cmake --build "$UQC_ROOT/.cache/uqc201/build/greeter" --target format-check
```

`greeter-lint`: exit **0**, 7.44 s.

```sh
cd "$UQC_ROOT/holonight-greeter"
cmake --build "$UQC_ROOT/.cache/uqc201/build/greeter" --target qml-lint
```

`greeter-static`: exit **0**, 97.34 s.

```sh
cd "$UQC_ROOT/holonight-greeter"
python3 "$UQC_ROOT/holonight-greeter/scripts/check-static.py" "$UQC_ROOT/.cache/uqc201/build/greeter"
```

`ai-tidy`: exit **0**, 337.50 s.

```sh
cd "$UQC_ROOT/holonight-ai"
run-clang-tidy -quiet -j 4 -p "$UQC_ROOT/.cache/uqc201/build/ai" -removed-arg=-mno-direct-extern-access "^$UQC_ROOT/holonight-ai/"
```

`ai-qmltypes`: exit **0**, 0.01 s.

```sh
cd "$UQC_ROOT/holonight-ai"
bash "$UQC_ROOT/holonight-ai/scripts/check-qmltypes.sh" "$UQC_ROOT/.cache/uqc201/build/ai"
```


## Third-party bounded probes

`haruna`: exit **124**, 12.20 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/haruna
```

Evidence: /tmp/uqc-audit-d3ftreus exit_status=124

`neochat`: exit **124**, 12.26 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/neochat
```

Evidence: /tmp/uqc-audit-p0ur_8ps exit_status=124

`tokodon`: exit **124**, 12.18 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/tokodon
```

Evidence: /tmp/uqc-audit-yp29b23m exit_status=124

`haruna`: exit **124**, 12.21 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" env QT_QPA_PLATFORMTHEME=holonight python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/haruna
```

Evidence: /tmp/uqc-audit-o7_ap6fu exit_status=124

`neochat`: exit **124**, 12.29 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" env QT_QPA_PLATFORMTHEME=holonight python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/neochat
```

Evidence: /tmp/uqc-audit-nqt51_ni exit_status=124

`tokodon`: exit **124**, 12.24 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib"
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" env QT_QPA_PLATFORMTHEME=holonight python3 "$UQC_ROOT/holonight-qt/docs/sdd/unified-qtquick-controls/audit/launch.py" --prefix "$UQC_ROOT/.cache/uqc201/prefix" --mode isolated --seconds 12 -- /usr/bin/tokodon
```

Evidence: /tmp/uqc-audit-ibreaq84 exit_status=124


## Copied manual kit

`kit-holonight_demo-default`: exit **0**, 3.13 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_demo /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml default
```

`kit-holonight_demo-environment`: exit **0**, 3.13 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_demo /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml environment
```

`kit-holonight_demo-command-line`: exit **0**, 3.12 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_demo /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml command-line
```

`kit-holonight_demo-configuration`: exit **0**, 3.12 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_demo /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml configuration
```

`kit-holonight_controls_gallery-default`: exit **0**, 3.12 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml default
```

`kit-holonight_controls_gallery-environment`: exit **0**, 3.13 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml environment
```

`kit-holonight_controls_gallery-command-line`: exit **0**, 3.12 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml command-line
```

`kit-holonight_controls_gallery-configuration`: exit **0**, 3.12 s.

```sh
cd "$UQC_ROOT"
export LD_LIBRARY_PATH=/tmp/holonight-uqc201-manual/prefix/lib
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" python3 "$UQC_ROOT/holonight-qt/tests/check_example_startup.py" /tmp/holonight-uqc201-manual/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-manual/prefix/lib/qt6/qml configuration
```


## Installer and licensing

`installer-preflight`: exit **1**, 0.22 s.

```sh
cd "$UQC_ROOT"
bash scripts/install.sh --check
```

`umbrella-reuse`: exit **0**, 0.65 s.

```sh
cd "$UQC_ROOT"
reuse --no-multiprocessing lint
```

`config-reuse`: exit **0**, 0.37 s.

```sh
cd "$UQC_ROOT/holonight-config"
reuse --no-multiprocessing lint
```

`system-services-reuse`: exit **0**, 0.36 s.

```sh
cd "$UQC_ROOT/holonight-system-services"
reuse --no-multiprocessing lint
```

`qt-reuse`: exit **0**, 2.17 s.

```sh
cd "$UQC_ROOT/holonight-qt"
reuse --no-multiprocessing lint
```

`appearance-adapters-reuse`: exit **0**, 0.39 s.

```sh
cd "$UQC_ROOT/holonight-appearance-adapters"
reuse --no-multiprocessing lint
```

`shell-reuse`: exit **0**, 4.67 s.

```sh
cd "$UQC_ROOT/holonight-shell"
reuse --no-multiprocessing lint
```

`settings-reuse`: exit **0**, 1.07 s.

```sh
cd "$UQC_ROOT/holonight-settings"
reuse --no-multiprocessing lint
```

`ai-reuse`: exit **0**, 2.15 s.

```sh
cd "$UQC_ROOT/holonight-ai"
reuse --no-multiprocessing lint
```

`pkg-manager-reuse`: exit **0**, 0.90 s.

```sh
cd "$UQC_ROOT/holonight-pkg-manager"
reuse --no-multiprocessing lint
```

`greeter-reuse`: exit **0**, 0.65 s.

```sh
cd "$UQC_ROOT/holonight-greeter"
reuse --no-multiprocessing lint
```

## Additional recorded checks

Shell compile-database export succeeded. The first tidy invocation from the
umbrella root failed with “No checks enabled”; the final invocation below ran
from the shell root and exited 0 (234 translation units).

```sh
cd "$UQC_ROOT"
cmake -S holonight-shell -B .cache/uqc201/build/shell -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake -P .cache/uqc201/build/shell/strip_tidy_flags.cmake
cd "$UQC_ROOT/holonight-shell"
run-clang-tidy -quiet -j4 -p ../.cache/uqc201/build/shell/tidy "^$UQC_ROOT/holonight-shell/"
bash scripts/check-qmltypes.sh ../.cache/uqc201/build/shell
bash scripts/check-architecture-boundaries.sh
```

Manual-kit preparation copied the shared prefix (239 regular files checked with
SHA-256), the provider's unchanged `auth-test.py`, `registration.py`, `terminal.sh`,
and this initiative's AUTHENTICATION.md/MANUAL.md. Hyprland config paths were
updated to `/tmp/holonight-uqc201-manual`; Sway's minimal config starts the same
terminal and provides Super+Return/Shift+E/q bindings. No agent autostarts.

The following validations passed; tux-only refusal intentionally exits 1:

```sh
python3 -m py_compile /tmp/holonight-uqc201-manual/auth-test.py /tmp/holonight-uqc201-manual/registration.py
bash -n /tmp/holonight-uqc201-manual/terminal.sh
Hyprland --verify-config --config /tmp/holonight-uqc201-manual/hyprland.conf
WLR_BACKENDS=headless WLR_RENDERER=pixman sway --validate --config /tmp/holonight-uqc201-manual/sway.conf
/usr/bin/python3 /tmp/holonight-uqc201-manual/auth-test.py preflight
```

The optional historical audit fixture was built with CMake/Ninja in
`.cache/uqc201/build/audit`; its `check-fixture.py` invocation exited 1 because its
pre-implementation Basic expectations are obsolete. The copied kit instead
passes the current provider's eight example startup checks above.

## UQC-202/UQC-203 targeted recheck — 2026-09-09

Run at published umbrella `730be066e78c4cf5c0d65f3f78fb669f5fcbb229`, after
accepting the canonically published AI handoff. Both commands exit 0; Fusion
passes 59/59 in 15.37 seconds. The earlier failing commands/results above remain.

```sh
cd "$UQC_ROOT"
bash scripts/install.sh --check
env LD_LIBRARY_PATH="$UQC_ROOT/.cache/uqc201/prefix/lib" \
  QT_QUICK_CONTROLS_STYLE=Fusion QT_SCALE_FACTOR=1 \
  bwrap --die-with-parent --bind / / --dev /dev --proc /proc \
  --tmpfs /usr/lib/qt6/qml/Holonight \
  --ro-bind /dev/null /usr/lib/libholonight_config.so \
  --setenv UQC_ISOLATED 1 -- \
  python3 "$UQC_ROOT/holonight-shell/scripts/run-isolated-test.py" \
  ctest --test-dir "$UQC_ROOT/.cache/uqc201/build/ai" \
  -R 'Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock' \
  --output-on-failure -j4
git submodule foreach --quiet 'git status --porcelain'
reuse --no-multiprocessing lint
git diff --check
```

Submodule status produces no output; REUSE passes 47/47 and whitespace passes.
The final repair fixtures also pass `task test:installer` (eight tests),
`bash -n scripts/install.sh scripts/install-dependencies.sh`, and CI YAML parsing.

## UQC-201 accessible kit — 2026-09-09

Baseline `7fcc8bb48a451185b9412950ac7f651ee75975c7`. Fresh work directory:
`.cache/uqc201-guided-qht3_tjs`; configured kit `/tmp/holonight-uqc201-8r1jtlln`.
Commands below are the executed argument vectors, with the umbrella root normalized
to `$UQC_ROOT`. Set `UQC_ROOT` to the umbrella root and export
`LD_LIBRARY_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix/lib` for these commands.
The private patchelf executable from the prior verified tool cache is unchanged.
All output and timings remain in `results.jsonl`, `extra-results.jsonl`,
`kit-results.jsonl`, `third-party-results.jsonl` and `logs/` under the new work directory.

<details>
<summary>Fresh dependency-order commands and exits</summary>

```sh
# config-configure: exit 0, 0.24s
cmake -S $UQC_ROOT/holonight-config -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/config -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON
# config-build: exit 0, 1.17s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/config -j 6
# config-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/config
# config-full: exit 1, 0.04s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/config --output-on-failure --no-tests=error -j 4
# config-full: exit 0, 0.77s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/config --output-on-failure --no-tests=error -j 4
# system-services-configure: exit 0, 0.51s
cmake -S $UQC_ROOT/holonight-system-services -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/system-services -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON
# system-services-build: exit 0, 5.00s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/system-services -j 6
# system-services-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/system-services
# system-services-full: exit 0, 9.63s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/system-services --output-on-failure --no-tests=error -j 4
# shell-config-configure: exit 0, 0.39s
cmake -S $UQC_ROOT/holonight-shell/libs/holonight-shell-config -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell-config -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
# shell-config-build: exit 0, 2.20s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell-config -j 6
# shell-config-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell-config
# qt-configure: exit 0, 1.77s
cmake -S $UQC_ROOT/holonight-qt -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON -DBUILD_DEMO=ON -DBUILD_CONTROLS_GALLERY=ON -DHOLONIGHT_PATCHELF_EXECUTABLE=/tmp/uqc201-uv-cache/archive-v0/mVGV6ox16yY-nm-6uMj4N/bin/patchelf
# qt-build: exit 0, 65.61s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt -j 6
# qt-install: exit 0, 0.03s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt
# qt-focused: exit 0, 7.94s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
# qt-full: exit 0, 42.17s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt --output-on-failure --no-tests=error -j 4
# appearance-adapters-configure: exit 0, 1.18s
cmake -S $UQC_ROOT/holonight-appearance-adapters -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/appearance-adapters -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON -DHOLONIGHT_QT_DIR=/tmp/holonight-uqc201-8r1jtlln/prefix -DHOLONIGHT_CONFIG_DIR=/tmp/holonight-uqc201-8r1jtlln/prefix
# appearance-adapters-build: exit 0, 2.75s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/appearance-adapters -j 6
# appearance-adapters-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/appearance-adapters
# appearance-adapters-full: exit 0, 0.11s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/appearance-adapters --output-on-failure --no-tests=error -j 4
# shell-configure: exit 0, 2.59s
cmake -S $UQC_ROOT/holonight-shell -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON
# shell-build: exit 0, 232.66s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell -j 6
# shell-install: exit 0, 0.06s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell
# shell-focused: exit 0, 2.61s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell -R QtNetworkManagerBackendTest --output-on-failure -j 1
# shell-full: exit 0, 228.60s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/shell --output-on-failure --no-tests=error -j 1
# settings-configure: exit 0, 1.03s
cmake -S $UQC_ROOT/holonight-settings -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/settings -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON
# settings-build: exit 0, 26.54s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/settings -j 6
# settings-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/settings
# settings-focused: exit 0, 12.60s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/settings -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 1
# settings-full: exit 0, 42.91s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/settings --output-on-failure --no-tests=error -j 1
# ai-configure: exit 0, 1.51s
cmake -S $UQC_ROOT/holonight-ai -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON
# ai-build: exit 0, 104.96s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai -j 6
# ai-install: exit 0, 0.03s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai
# ai-focused: exit 0, 29.50s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
# ai-full: exit 0, 23.79s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai --output-on-failure --no-tests=error -j 4
# pkg-manager-configure: exit 0, 0.81s
cmake -S $UQC_ROOT/holonight-pkg-manager -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTS=ON
# pkg-manager-build: exit 0, 25.30s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager -j 6
# pkg-manager-install: exit 0, 0.01s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager
# pkg-manager-focused: exit 0, 10.89s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
# pkg-manager-full: exit 0, 8.40s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager --output-on-failure --no-tests=error -j 4
# greeter-configure: exit 0, 0.90s
cmake -S $UQC_ROOT/holonight-greeter -B $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_PREFIX_PATH=/tmp/holonight-uqc201-8r1jtlln/prefix -DCMAKE_INSTALL_LIBDIR=lib -DTIDY_JOBS=4 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON
# greeter-build: exit 0, 14.49s
cmake --build $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter -j 6
# greeter-install: exit 0, 0.02s
cmake --install $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter
# greeter-focused: exit 0, 1.83s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter -R 'runtime|startup|import.*policy|uqc_|control_palette|palette_dark|palette_hybrid|core_isolation' --output-on-failure -j 4
# greeter-full: exit 0, 5.44s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter --output-on-failure --no-tests=error -j 4
# ai-build-launches: exit 0, 12.48s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-ai/scripts/check-runtime-launches.py $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai/holonight-chat /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/ai-build-launches
# ai-installed-launches: exit 0, 12.50s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-ai/scripts/check-runtime-launches.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-chat /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/ai-installed-launches --forbid-path $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# pkg-manager-build-launches: exit 0, 12.45s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-pkg-manager/scripts/check-runtime-launches.py $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager/holonight-packages /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/pkg-manager-build-launches
# pkg-manager-installed-launches: exit 0, 12.39s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-pkg-manager/scripts/check-runtime-launches.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-packages /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/pkg-manager-installed-launches --forbid-path $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# greeter-build-launches: exit 0, 12.29s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-greeter/scripts/check-runtime-launches.py $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/greeter/holonight-greeter /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/greeter-build-launches
# greeter-installed-launches: exit 0, 12.37s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-greeter/scripts/check-runtime-launches.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-greeter /tmp/holonight-uqc201-8r1jtlln/prefix --logs $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/logs/greeter-installed-launches --forbid-path $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# settings-installed-default: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-settings/tests/check_settings_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-settings /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml default --forbid-qml-root $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# settings-installed-environment: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-settings/tests/check_settings_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-settings /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml environment --forbid-qml-root $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# settings-installed-command-line: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-settings/tests/check_settings_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-settings /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml command-line --forbid-qml-root $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# settings-installed-configuration: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-settings/tests/check_settings_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-settings /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml configuration --forbid-qml-root $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build
# ai-source-Holonight: exit 0, 15.46s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai -R 'Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock' --output-on-failure -j 4
# ai-source-Fusion: exit 0, 15.45s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/ai -R 'Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock' --output-on-failure -j 4
# pkg-manager-source-Holonight: exit 0, 0.62s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager -R InstalledPackagesViewTest --output-on-failure -j 4
# pkg-manager-source-Fusion: exit 0, 0.57s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/pkg-manager -R InstalledPackagesViewTest --output-on-failure -j 4
# qt-source-Holonight: exit 0, 1.72s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt -R runtime_composites --output-on-failure -j 4
# qt-source-Fusion: exit 0, 1.63s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so --setenv UQC_ISOLATED 1 -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py ctest --test-dir $UQC_ROOT/.cache/uqc201-guided-qht3_tjs/build/qt -R runtime_composites --output-on-failure -j 4
# kit-holonight_demo-default: exit 1, 0.05s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_demo /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml default
# kit-holonight_demo-default: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_demo /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml default
# kit-holonight_demo-environment: exit 0, 3.14s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_demo /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml environment
# kit-holonight_demo-command-line: exit 0, 3.13s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_demo /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml command-line
# kit-holonight_demo-configuration: exit 0, 3.14s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_demo /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml configuration
# kit-holonight_controls_gallery-default: exit 0, 3.14s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml default
# kit-holonight_controls_gallery-environment: exit 0, 3.14s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml environment
# kit-holonight_controls_gallery-command-line: exit 0, 3.14s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml command-line
# kit-holonight_controls_gallery-configuration: exit 0, 3.12s
bwrap --die-with-parent --bind / / --dev /dev --proc /proc --tmpfs /usr/lib/qt6/qml/Holonight --ro-bind /dev/null /usr/lib/libholonight_config.so -- python3 $UQC_ROOT/holonight-shell/scripts/run-isolated-test.py python3 $UQC_ROOT/holonight-qt/tests/check_example_startup.py /tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight_controls_gallery /tmp/holonight-uqc201-8r1jtlln/prefix/lib/qt6/qml configuration
```

</details>

The first config-full and example-default attempts fail because the command
sandbox denies private D-Bus sockets. Subsequent commands use approved execution
outside that sandbox, retaining bwrap host-provider masking and disposable private
buses. Their earlier logs are preserved with `-sandbox-failure` suffixes.
Shell tests are serial; no consumer Taskfile substitution runs.

Additional preparation commands/checks:

```sh
bash scripts/install.sh --check
Hyprland --verify-config --config /tmp/holonight-uqc201-8r1jtlln/hyprland.conf
env WLR_BACKENDS=headless WLR_RENDERER=pixman sway --validate --config /tmp/holonight-uqc201-8r1jtlln/sway.conf
bash -n /tmp/holonight-uqc201-8r1jtlln/terminal.sh
desktop-file-validate /tmp/holonight-uqc201-8r1jtlln/prefix/share/applications/org.holonight.Settings.desktop
python3 docs/initiatives/unified-qtquick-controls/prepare-guided-kit.py /tmp/holonight-uqc201-helpers-z5cjj5wb
reuse --no-multiprocessing lint
git diff --check
git submodule foreach --quiet 'git status --porcelain'
git ls-remote --exit-code origin refs/heads/main
git submodule foreach --quiet 'git ls-remote --exit-code origin refs/heads/main'
```

All final commands pass. The helper-generation directory is a separate fresh
syntax/reproduction kit, not an installed acceptance prefix. Its auth/terminal
files match the acceptance kit byte for byte. Python AST parsing passes for the
three umbrella helpers and copied auth helpers. The session/app/auth helpers
intentionally refuse the current user (1/2/1); these are expected guard outcomes.
A non-authentication child verifies the non-dumpable start-time correlation.
Details: `helper-checks.json`, `helper-generation.txt`, `non-dumpable-check.txt`.

The initial Sway validation exits 134 after sandbox socket denial; approved
headless validation exits 0. The initial canonical SSH query exits 128 on system
SSH configuration access; approved read-only queries confirm all pins. No live
session, pointer/focus interaction or authentication is performed by these checks.

The third-party runner executes the same recorded platform-theme probes above,
substituting the new prefix and work directory; all three return expected timeout
124. Metadata/executable checks and `ldd` over 18 unique installed ELF files pass;
`metadata-inventory.json` and `elf-linkage.json` retain results. Prefix permission,
symlink containment and SHA-256 inventory checks pass for 239 regular files.
Only diagnostic summaries are published; raw application/authentication logs are
not added to Git. The [guided handoff](GUIDED.md) contains the pending user steps.
