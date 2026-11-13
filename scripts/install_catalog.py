# SPDX-License-Identifier: GPL-3.0-or-later
"""Source installer components, in provider order; CMake enforces package versions."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    dependencies: tuple = ()
    options: tuple = ()
    packages: tuple = ()
    hooks: tuple = ()


CATALOG = {
    'holonight-config': Component(packages=('tomlplusplus',)),
    'holonight-system-services': Component(packages=('libpulse', 'udisks2', 'systemd')),
    'holonight-qt': Component(('holonight-config', 'holonight-system-services'),
                             ('BUILD_DEMO=OFF', 'BUILD_CONTROLS_GALLERY=OFF', 'BUILD_QT5_PROBES=OFF'),
                             ('layer-shell-qt', 'kconfig'), ('libraries',)),
    'holonight-appearance-adapters': Component(('holonight-qt', 'holonight-config'), ('BUILD_GTK_PROBES=OFF',),
                                              ('json-glib',)),
    'holonight-icons': Component(hooks=('icons',)),
    'holonight-images': Component(options=('HOLONIGHT_IMAGES_ISOLATED=ON',),
                                  packages=('bubblewrap', 'libexif', 'libwebp', 'qt6-imageformats', 'kimageformats')),
    'holonight-thumbnails': Component(('holonight-images',), ('HOLONIGHT_THUMBNAILS_ISOLATED=ON',)),
    'holonight-search': Component(packages=('sqlite',)),
    'holonight-file-browser': Component(('holonight-search', 'holonight-system-services', 'holonight-images',
                                        'holonight-thumbnails'), packages=('qmarkdown', 'md4c')),
    'holonight-shell': Component(('holonight-qt', 'holonight-system-services'), packages=('libsecret', 'polkit', 'polkit-qt6', 'uwsm', 'tomlplusplus'), hooks=('services',)),
    'holonightd': Component(packages=('sqlite', 'ripgrep'), hooks=('services',)),
    'holonight-settings': Component(('holonight-config', 'holonight-shell', 'holonight-system-services',
                                    'holonight-qt', 'holonight-file-browser'), hooks=('desktop',)),
    'holonight-viewer': Component(('holonight-qt', 'holonight-images', 'holonight-thumbnails',
                                  'holonight-file-browser'), hooks=('desktop', 'viewer')),
    'holonight-files': Component(('holonight-file-browser', 'holonight-qt', 'holonight-images',
                                 'holonight-thumbnails', 'holonight-search', 'holonight-system-services'),
                                hooks=('desktop',)),
    'xdg-desktop-portal-holonight': Component(('holonight-qt', 'holonight-search', 'holonight-file-browser'),
                                            hooks=('services',)),
    'holonight-ai': Component(('holonight-qt',), packages=('libsecret', 'syntax-highlighting', 'qmarkdown'), hooks=('desktop',)),
    'holonight-pkg-manager': Component(('holonight-qt',), packages=('appstream-qt', 'archlinux-appstream-data', 'polkit-qt6', 'pacman'),
                                      hooks=('desktop', 'services')),
    'holonight-greeter': Component(('holonight-qt',), packages=('greetd', 'cage'), hooks=('greeter',)),
    'holonight-hyprlock': Component(packages=('hyprlock',)),
}
BASE_PACKAGES = ('base-devel', 'cmake', 'ninja', 'git', 'pkgconf', 'python', 'qt6-base',
                 'qt6-declarative', 'qt6-svg', 'wayland', 'wayland-protocols', 'nlohmann-json')


def select(names, installed, removing=False):
    unknown = set(names) - CATALOG.keys()
    if unknown:
        raise ValueError(f'unknown components: {", ".join(sorted(unknown))}')
    chosen = set(names) if names else (set(installed) & CATALOG.keys() if removing else set(CATALOG))
    while True:
        dependents = {name for name in installed if name in CATALOG
                      and set(CATALOG[name].dependencies) & chosen} - chosen
        if not dependents:
            break
        if removing:
            raise ValueError(f'installed dependents must also be removed: {", ".join(sorted(dependents))}')
        chosen |= dependents
    return [name for name in CATALOG if name in chosen]


if __name__ == '__main__':
    print(' '.join(CATALOG))
