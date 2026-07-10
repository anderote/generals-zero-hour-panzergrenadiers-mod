#!/usr/bin/env python3
"""Final stat-tune layer: zzyzzzz_StatTune.big

- Battlemaster base HP -> 550 (vanilla/Nuke/Tank variants; Ravage untouched)
- Gattling tank base HP -> 450 (vanilla/Nuke/Spec/Tank; APC untouched)
- Gattling ground-gun AttackRange -> 250 (tank + APC gun families; air guns untouched)

Effective sources: Battlemaster INIs + Weapon.ini from zzyzzz_CoaxMG.big,
gattling object INIs from zzyz_GattlingBuff.big.
Rebuild-order: this is the LAST stat layer; rebuild after any lower layer changes.
"""
import sys, os, re, hashlib, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hotkey-addon'))
from bigfile import read_big, write_big_file, BigEntry

SPE = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
SW = os.path.expanduser('~/GeneralsX/mods/ShockWave')
OUT_NAME = 'zzyzzzz_StatTune.big'

HP_CHANGES = {  # internal path -> [(object_name, old_hp, new_hp)]
    'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\BattleMaster.ini': [('ChinaTankBattleMaster_Var1', 480.0, 550.0)],
    'Data\\INI\\Object\\China\\Nuke\\Vehicles\\BattleMaster.ini': [('Nuke_ChinaTankBattleMaster', 480.0, 550.0)],
    'Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini': [('Tank_ChinaTankBattleMaster', 480.0, 550.0)],
    'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\GattlingTank.ini': [('ChinaTankGattling', 414.0, 450.0)],
    'Data\\INI\\Object\\China\\Nuke\\Vehicles\\GattlingTank.ini': [('Nuke_ChinaTankGattling', 414.0, 450.0)],
    'Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\GattlingTank.ini': [('Spec_ChinaTankGattling', 414.0, 450.0)],
    'Data\\INI\\Object\\China\\Tank\\Vehicles\\GattlingTank.ini': [('Tank_ChinaTankGattling', 483.0, 450.0)],
}
# ground gattling guns -> 250 (current effective value 198)
RANGE_WEAPONS = [
    'GattlingTankGun', 'GattlingTankGunHeroic',
    'AdvancedGattlingTankGun', 'AdvancedGattlingTankGunHeroic',
    'NukeGattlingTankGun', 'NukeGattlingTankGunHeroic',
    'NukeAdvancedGattlingTankGun', 'NukeAdvancedGattlingTankGunHeroic',
    'Spec_GattlingTankGun', 'Spec_GattlingTankGunHeroic',
    'GattlingAPCGun', 'GattlingAPCGunHeroic',
    'UpgradedGattlingAPCGun', 'UpgradedGattlingAPCGunHeroic',
]
WEAPON_INI = 'Data\\INI\\Weapon.ini'


def effective(path):
    """Extract highest-priority copy of an internal path from the SPE mod dir."""
    order = ['zzyzzz_CoaxMG.big', 'zzyzz_PropTowers.big', 'zzyzy_NoAISuperweapons.big',
             'zzyz_GattlingBuff.big', 'zzyy_ChinaBunkers.big', 'zzy_MammothBunker.big',
             'zzx_ChinaTankBuff.big', 'zz_SPE_Shw_ini.big']
    for arch in order:
        ap = os.path.join(SPE, arch)
        if not os.path.exists(ap):
            continue
        for e in read_big(ap):
            if e.path == path:
                return e.data, arch
    raise SystemExit(f'not found in any layer: {path}')


def patch_hp(txt, obj, old, new):
    changed = 0
    for field in ('MaxHealth', 'InitialHealth'):
        pat = re.compile(r'(%s\s*=\s*)%s\b' % (field, re.escape('%g' % old)))
        txt, n = pat.subn(lambda m: m.group(1) + ('%g' % new), txt, count=1)
        changed += n
    assert changed >= 1, f'{obj}: no HP lines matched {old}'
    return txt, changed


def main():
    entries = []
    report = []
    for path, specs in HP_CHANGES.items():
        data, src = effective(path)
        txt = data.decode('latin-1')
        for obj, old, new in specs:
            txt, n = patch_hp(txt, obj, old, new)
            report.append(f'{obj}: {old:g} -> {new:g} ({n} lines) [src {src}]')
        entries.append(BigEntry(path, txt.encode('latin-1')))

    data, src = effective(WEAPON_INI)
    txt = data.decode('latin-1')
    for wname in RANGE_WEAPONS:
        pat = re.compile(r'(Weapon %s\b.*?\n\s*AttackRange\s*=\s*)198(?:\.0)?\b' % re.escape(wname), re.S)
        txt, n = pat.subn(lambda m: m.group(1) + '250.0', txt, count=1)
        assert n == 1, f'{wname}: AttackRange 198 not found'
        report.append(f'{wname}: range 198 -> 250 [src {src}]')
    entries.append(BigEntry(WEAPON_INI, txt.encode('latin-1')))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUT_NAME)
    write_big_file(entries, out)
    # verify round-trip
    back = read_big(out)
    assert len(back) == len(entries)
    for e in back:
        t = e.data.decode('latin-1')
        assert t.count('End') > 0
    for dest in (SPE, SW):
        shutil.copy2(out, os.path.join(dest, OUT_NAME))
    md5 = hashlib.md5(open(out, 'rb').read()).hexdigest()
    print('\n'.join(report))
    print(f'built {OUT_NAME} md5={md5}, installed to ShockWave + ShockWaveSPE')


if __name__ == '__main__':
    main()
