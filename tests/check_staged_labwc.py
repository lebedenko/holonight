#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Andrii L <lebeden@gmail.com>
"""Validate a source-install staged prefix without touching user configuration."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

prefix = Path(sys.argv[1])
theme = prefix / 'share/themes/HoloNight/labwc'
buttons = ['close', 'iconify', 'max', 'max_toggled', 'menu', 'shade', 'shade_toggled', 'desk', 'desk_toggled']
expected = {'themerc'} | {f'{button}{hover}-{state}.svg' for button in buttons for hover in ['', '_hover'] for state in ['active', 'inactive']}
assert {x.name for x in theme.iterdir()} == expected
for svg in theme.glob('*.svg'):
    root = ET.parse(svg).getroot()
    assert root.attrib['width'] == '30' and root.attrib['height'] == '30'
    assert 'currentColor' not in svg.read_text()
text = (theme / 'themerc').read_text()
assert 'window.active.title.bg: Solid' in text
assert 'window.active.shadow.size: 48' in text
assert 'window.inactive.shadow.size: 24' in text
example = ET.parse(prefix / 'share/doc/HoloNightAppearanceAdapters/labwc-theme.xml')
assert example.find('name').text == 'HoloNight'
assert example.find('titlebar/layout').text == ':iconify,max,close'
print('HoloNight labwc staged payload: 37 theme files and XML example verified')
