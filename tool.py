#!/usr/bin/env python3
"""Build/install a proxy launcher without modifying the original application."""
import argparse
import datetime
import pathlib
import plistlib
import shlex
import shutil
import subprocess

BUNDLE_ID = 'local.antigravity.proxy-launcher'
ROOT = pathlib.Path(__file__).resolve().parent
STATE = pathlib.Path.home() / 'Library/Application Support/Antigravity Proxy Launcher'


def dock_read():
    return plistlib.loads(subprocess.check_output(['defaults', 'export', 'com.apple.dock', '-']))


def dock_write(data):
    subprocess.run(['defaults', 'import', 'com.apple.dock', '-'], input=plistlib.dumps(data), check=True)
    subprocess.run(['killall', 'Dock'], check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'install', 'restore-dock'])
    parser.add_argument('--app', type=pathlib.Path, default=pathlib.Path('/Applications/Antigravity.app'))
    parser.add_argument('--output', type=pathlib.Path)
    parser.add_argument('--dock', action='store_true', help='Replace an existing original-app Dock entry')
    args = parser.parse_args()
    if args.action == 'restore-dock':
        saved = plistlib.loads((STATE / 'entry.plist').read_bytes())
        data = dock_read()
        for i, item in enumerate(data.get('persistent-apps', [])):
            if item.get('tile-data', {}).get('bundle-identifier') == BUNDLE_ID:
                data['persistent-apps'][i] = saved
                dock_write(data)
                print('Original Dock entry restored. Launcher files retained.')
                return
        raise SystemExit('Launcher Dock entry not found; no changes made.')
    original = args.app.expanduser().resolve()
    info_path = original / 'Contents/Info.plist'
    if not info_path.is_file():
        raise SystemExit(f'Application not found: {original}')
    info = plistlib.loads(info_path.read_bytes())
    binary = original / 'Contents/MacOS' / info['CFBundleExecutable']
    if not binary.is_file():
        raise SystemExit(f'Executable not found: {binary}')
    destination = (args.output or (pathlib.Path.home() / 'Applications/Antigravity Proxy.app')).expanduser().absolute()
    if destination.exists():
        raise SystemExit(f'Destination already exists; choose another --output: {destination}')
    if args.action == 'build' and args.dock:
        raise SystemExit('--dock is only available with install')
    data = dock_read() if args.dock else None
    index = None
    if data is not None:
        for i, item in enumerate(data.get('persistent-apps', [])):
            if item.get('tile-data', {}).get('bundle-identifier') == info['CFBundleIdentifier']:
                index = i
                break
        if index is None:
            raise SystemExit('Original application is not pinned to Dock; no changes made.')
        if (STATE / 'entry.plist').exists():
            raise SystemExit('A saved Dock entry already exists; restore it before another Dock installation.')
    contents = destination / 'Contents'
    (contents / 'MacOS').mkdir(parents=True)
    (contents / 'Resources').mkdir()
    app_info = dict(CFBundleIdentifier=BUNDLE_ID, CFBundleName='Antigravity Proxy',
                    CFBundleDisplayName='Antigravity Proxy', CFBundleExecutable='launcher',
                    CFBundlePackageType='APPL', CFBundleVersion='1', LSUIElement=False)
    icon = original / 'Contents/Resources' / info.get('CFBundleIconFile', 'icon.icns')
    if not icon.suffix:
        icon = icon.with_suffix('.icns')
    if icon.is_file():
        shutil.copy2(icon, contents / 'Resources/icon.icns')
        app_info['CFBundleIconFile'] = 'icon.icns'
    (contents / 'Info.plist').write_bytes(plistlib.dumps(app_info))
    script = (ROOT / 'src/launcher.zsh').read_text()
    script = script.replace('/Applications/Antigravity.app/Contents/MacOS/Antigravity', shlex.quote(str(binary)))
    launcher = contents / 'MacOS/launcher'
    launcher.write_text(script)
    launcher.chmod(0o755)
    subprocess.run(['/bin/zsh', '-n', str(launcher)], check=True)
    if data is not None:
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / 'entry.plist').write_bytes(plistlib.dumps(data['persistent-apps'][index]))
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        (STATE / f'dock-{stamp}.plist').write_bytes(plistlib.dumps(data))
        tile = data['persistent-apps'][index]['tile-data']
        tile['file-data']['_CFURLString'] = destination.as_uri() + '/'
        tile['file-label'] = 'Antigravity Proxy'
        tile['bundle-identifier'] = BUNDLE_ID
        dock_write(data)
        actual = dock_read()
        if not any(x.get('tile-data', {}).get('file-data', {}).get('_CFURLString') == destination.as_uri() + '/'
                   for x in actual.get('persistent-apps', [])):
            raise SystemExit('Dock read-back failed; saved original entry is available for restore-dock.')
    print(f'Created: {destination}')
    print('Quit Antigravity completely, then open the new launcher.')


if __name__ == '__main__':
    main()
