#!/usr/bin/env python3
"""Extend an existing user choice of Viewer to newly supported MIME types."""
import configparser
import os
from pathlib import Path
import stat
import sys
import tempfile

VIEWER = 'org.holonight.Viewer.desktop'
BASE = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')


def read(path):
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    if path.exists():
        parser.read_string(path.read_text())
    return parser


def extend(entry):
    home = Path.home()
    config = Path(os.environ.get('XDG_CONFIG_HOME') or home / '.config')
    data = Path(os.environ.get('XDG_DATA_HOME') or home / '.local/share')
    desktops = [d.lower() for d in os.environ.get('XDG_CURRENT_DESKTOP', '').split(':') if d]
    paths = []
    for directory in (config, data / 'applications'):
        paths.extend(directory / f'{d}-mimeapps.list' for d in desktops)
        paths.append(directory / 'mimeapps.list')
    paths.append(data / 'applications/defaults.list')
    preferences = [(path, read(path)) for path in paths]

    def default(mime):
        for _, parser in preferences:
            if parser.has_option('Default Applications', mime):
                return parser.get('Default Applications', mime).split(';')[0]
        return None

    def removed(mime):
        return any(VIEWER in parser.get('Removed Associations', mime, fallback='').split(';')
                   for _, parser in preferences)

    if any(default(mime) != VIEWER or removed(mime) for mime in BASE):
        print('Viewer defaults unchanged: no consistent existing user selection')
        return
    supported = read(entry).get('Desktop Entry', 'MimeType').strip(';').split(';')
    additions = [mime for mime in supported if default(mime) is None and not removed(mime)]
    if not additions:
        print('Viewer defaults already cover supported formats')
        return
    target = config / 'mimeapps.list'
    # Preserve symlink destinations as well as unrelated lines and file mode.
    target = target.resolve()
    original = ''
    if target.exists():
        with target.open(newline='') as stream:
            original = stream.read()
    lines = original.splitlines(keepends=True)
    insertion = len(lines)
    found = False
    for index, line in enumerate(lines):
        if line.strip() == '[Default Applications]':
            found = True
            insertion = index + 1
            break
    added = ''.join(f'{mime}={VIEWER};\n' for mime in additions)
    if not found:
        added = ('\n' if original and not original.endswith('\n') else '') + '[Default Applications]\n' + added
    if found and not lines[insertion - 1].endswith('\n'):
        lines[insertion - 1] += '\n'
    lines.insert(insertion, added)
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            os.fchmod(stream.fileno(), mode)
            stream.write(''.join(lines))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print('Extended Viewer defaults: ' + ', '.join(additions))


if __name__ == '__main__':
    try:
        extend(Path(sys.argv[1]))
    except (OSError, configparser.Error, ValueError) as error:
        sys.exit(f'error: could not extend Viewer defaults: {error}')
