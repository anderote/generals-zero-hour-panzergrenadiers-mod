# Panzergrenadiers — Research & Upgrade Overview (Kwai / China Tank General)

A single authoritative reference to **every purchasable upgrade in the mod,
grouped by the building that researches it**, with cost, research time,
prerequisite and effect. This is the out-of-game companion to the in-game
research tree.

**Provenance.** Every row below was *harvested from the real effective game
data* — the merged `Data\INI\Upgrade.ini`, `CommandSet.ini`,
`CommandButton.ini` and `Data\Generals.str` as they resolve after all layered
`.big` archives in `~/GeneralsX/mods/ShockWaveSPE/` are applied
(later-alphabetical archive wins). It is not hand-copied from the design specs;
costs/times are read straight from the installed `Upgrade` blocks, effects from
the installed button tooltips, prerequisites from the installed `RequiredUpgrade`
fields and the documented `CommandSetUpgrade` tier chains. Effective owners at
harvest time: `CommandSet.ini` / `CommandButton.ini` / `Generals.str` →
`zzz-ZZZZZZZZZZZZZ0TeslaFinish.big`; `Upgrade.ini` →
`zzz-ZZZZZZZZZZZZ0EmperorDefense.big`.

> **Scope.** "Purchasable upgrade" = a `PLAYER_UPGRADE` or `OBJECT_UPGRADE`
> command button that sits in a Kwai (`Tank_China…`) command set and costs
> money. Buildable units, special powers (UAV, paradrops), generals' promotion
> sciences and the pure command-swap buttons (scroll / taunt / options) are
> **not** upgrades and are listed separately or omitted. Where a stock ShockWave
> tooltip still says "Red Guard" or "Overlord", the Kwai roster has renamed /
> replaced those (Red Guard → **Panzergrenadier**, plain Overlord removed, the
> **Emperor** is Kwai's Overlord-class tank) — see *Stale-tooltip notes*.

---

## Building research trees

### Propaganda Center — the doctrine tree (15 researches)

Kwai's centerpiece. Two four-tier **sequential** ladders (each tier's button
replaces the previous via `CommandSetUpgrade` state chaining — buy I to reveal
II, etc.) plus the base-tech and vanilla-China propaganda upgrades.

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Composite Armor I** | $1000 | 45 s | — | +10% max health for **all** Kwai vehicles, aircraft **and** structures. Unlocks II. |
| **Composite Armor II** | $1500 | 45 s | Composite Armor I | +10% max health (stacks → +20%). Unlocks III. |
| **Composite Armor III** | $2000 | 45 s | Composite Armor II | +10% max health (stacks → +30%). Unlocks IV. |
| **Composite Armor IV** | $2500 | 45 s | Composite Armor III | +10% max health (stacks → +40% of base). |
| **Infantry Conditioning I** | $500 | 30 s | — | +15% max health for Kwai infantry (Panzergrenadier/Red Guard, Panzerjäger/Tank Hunter, Hacker, Black Lotus). Unlocks II. |
| **Infantry Conditioning II** | $750 | 30 s | Inf. Conditioning I | +15% max health (stacks → +30%). Unlocks III. |
| **Infantry Conditioning III** | $1000 | 30 s | Inf. Conditioning II | +15% max health (stacks → +45%). Unlocks IV. |
| **Infantry Conditioning IV** | $1250 | 30 s | Inf. Conditioning III | +15% max health (stacks → +60% of base). |
| **Tungsten Shells** | $2000 | 60 s | — | +25% damage, +15% range for Battlemaster & Emperor main guns. |
| **Advanced Infantry Doctrine** | $1500 | 45 s | — | +25% damage, +20% range for Panzergrenadier/Red Guard rifles & Panzerjäger/Tank Hunter missiles. |
| **Automated Repair Systems** | $1500 | 45 s | — | All Kwai structures self-repair ~1%/s of base max health. |
| **Base Armaments** | $2000 | 60 s | — | 7 main buildings (Command Center, Barracks, War Factory, Supply Center, Internet Center, Propaganda Center, Power Plant) gain a defensive anti-infantry machine gun (range 175). |
| **Chain Guns** | $1500 | 45 s | — | +25% damage on Gattling weapons (Gattling Tank, Reaper, gattling towers). |
| **Nationalism** | $1500 | 60 s | — | +25% horde bonus. |
| **Subliminal Messaging** | $1500 | 40 s | — | +100% propaganda effectiveness. |
| **Black Napalm** | $2000 | 45 s | — | +25% damage for all napalm weapons. |
| **Neutron Bomb** | $4000 | 60 s | — | Upgrades the EMP Bomb superweapon into a Neutron Bomb. |

*(The Land Mines / EMP Mines building-defense pair, below, is also available here.)*

**Ladder maths.** Fully-laddered Kwai = +40% vehicle/building HP and +60%
infantry HP plus both weapon doctrines, for **$13,750** across the two ladders +
Tungsten + Advanced Doctrine. Health is applied `ADD_CURRENT_HEALTH_TOO` (units
heal by the added amount); units built after research still receive every owned
tier.

---

### Industrial Plant — the grenadier & tank tech chain (5 researches)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Panzergrenadiers** | $1500 | 45 s | — | Battle tanks / Emperor / artillery roll out **pre-crewed** with fire-out infantry riding their bays: Battlemaster & Emperor get 2 Panzergrenadier + 2 Panzerjäger; each artillery 1 + 1. |
| **Waffen Grenadiers** | $2500 | 60 s | Panzergrenadiers | New Battlemasters are instead crewed with a combined-arms squad: 1 Minigunner + 1 Panzerjäger + 1 Flame Trooper + 1 Shock Trooper (replaces the Panzergrenadier crew via `ConflictsWith`). |
| **Emperor's Guard** | $2000 | 50 s | Panzergrenadiers | Emperors *additionally* embark 1 Flame + 1 Shock + 1 Sharpshooter + 1 Minigunner, filling the Emperor's 8-seat bay (additive with the Panzergrenadier crew). |
| **Auto Loader** | $2500 | 60 s | — | Battlemasters burst-fire 3 shells (autoloader). |
| **Reactive Armor** | $2500 | 60 s | — | +25% armor for Battlemaster, WarMaster, Reaper, Emperor. |

---

### War Factory (page 2) — the Emperor Defense Suite (4 researches)

Player-wide upgrades that apply to every Emperor tank; two `RequiredUpgrade`
chains.

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Hull Point-Defense Laser** | $1500 | 40 s | — | Emperors gain a *reactive* PDL: when struck they pulse an anti-missile LASER burst destroying incoming rockets/missiles nearby (never self-damages — LASER vs TankArmor = 0%). |
| **ABM Interceptor Array** | $2500 | 60 s | Hull PDL | Wider, harder-hitting point-defense that also intercepts ballistic (SCUD-class) missiles. |
| **Projected Energy Shield** | $2500 | 50 s | — | +2000 HP absorbing buffer on the Emperor hull (1320 → ~3320), continuously recharging at 40 HP/s. |
| **Fleet Shield Projection** | $2000 | 45 s | Projected Energy Shield | The Emperor extends a weaker regenerative shield aura (2%/s, radius 200) to nearby friendly units. |

---

### Nuclear Missile Silo (2 researches)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Nuclear Tanks** | $1500 | 45 s | — | +25% movement speed for Battlemaster, WarMaster, Reaper, Emperor. |
| **Uranium Shells** | $2000 | 60 s | — | +25% damage for Battlemaster, WarMaster, Emperor. |

---

### Internet Center (2 researches)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Satellite Hack I** | $1000 | 20 s | — | Reveals the Command Centers of all opponents. |
| **System Hack** | $1500 | 55 s | — | Allows Black Lotus to request an enemy airstrike. |

---

### Airfield (2 researches)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Aircraft Armor** | $1000 | 40 s | — | +25% armor for MiG aircraft. |
| **Helicopter Armor** | $1500 | 40 s | — | +25% armor for helicopters (Helix). |

---

### Command Center (1 research)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Radar** | $500 | 20 s | — | Builds radar for the Command Center. |

*(The Command Center also hosts the ungated **Surveillance UAV** deploy special
power and, via the Industrial Plant, the three paradrop powers — these are
abilities, not purchasable research. See* Non-research abilities *below.)*

---

### Barracks (1 research)

| Upgrade | Cost | Time | Prereq | Effect |
|---|---|---|---|---|
| **Capture Building** | $1000 | 30 s | — | Allows Kwai infantry (Panzergrenadiers/Red Guards) to capture structures. |

---

### Every building — base-defense mines (2 researches, per building)

Available on essentially every Kwai structure (Command Center, Barracks, War
Factory, Supply Center, Power Plant, Airfield, Industrial Plant, Nuclear Silo,
Propaganda Center, Gattling Cannon…). Mutually exclusive per building — buying
Land Mines swaps the button to EMP Mines.

| Upgrade | Cost | Time | Effect |
|---|---|---|---|
| **Land Mines** | $300 | 10 s | Lays a minefield around this building. |
| **EMP Mines** | $300 | 10 s | Mines emit an EMP blast when triggered. |

---

## Vehicle field upgrades (`OBJECT_UPGRADE`, bought on the individual unit)

These are researched on a *selected vehicle*, not a building — one per unit.

| Upgrade | Cost | Time | Buyable on | Effect |
|---|---|---|---|---|
| **Point Defense Laser** | $500 | 10 s | Battlemaster, Emperor, WarMaster, Dragon, ECM Tank, Gattling Tank, Command Truck | PDL pod that auto-shoots down incoming rockets/missiles (Tomahawks, infantry rockets…) near the vehicle. |
| **Overlord Gattling Cannon** | $900 | 15 s | Emperor | Mounts a Gattling Cannon on the Emperor. |
| **Overlord Propaganda Tower** | $500 | 10 s | Battlemaster | Mounts a heal-aura Propaganda Tower. |
| **Helix Gattling Cannon** | $900 | 15 s | Helix | Mounts a Gattling Cannon on the Helix. |
| **Troop Crawler Auto Cannon** | $250 | 10 s | Troop Crawler | Builds an auto-cannon on the Troop Crawler. |

> PDL, Gattling and Prop-Tower mounts on the Emperor/Battlemaster stack with the
> building-researched Emperor Defense Suite and the crew/doctrine upgrades — they
> are separate mounts, not mutually exclusive.

---

## Non-research abilities (for completeness — not purchasable upgrades)

- **Surveillance UAV** — Command Center special power, deployable from game start
  (ungated; the `Tank_Upgrade_KwaiUAVProgram` block still exists in `Upgrade.ini`
  but is **dormant / wired to no purchasable button** after the UAV rework made
  the deploy free).
- **Grenadier / Panzergrenadier / Panzer-Waffen paradrops** — three escalating
  cargo-plane drop special powers hosted on the Industrial Plant, available once
  it is built, escalating by cooldown (150 / 240 / 420 s), not by cash.

---

## Stale-tooltip notes (in-game text vs. Kwai roster)

Some tooltips are inherited verbatim from stock ShockWave and predate the Kwai
roster changes; the *effect* is correct, only the noun is stale:

- "Allows **Red Guards** to capture Structures" → Kwai fields
  **Panzergrenadiers** in that Barracks slot.
- "Build a Gattling Cannon on this **Emperor**" / "…on this **Overlord**" — the
  Emperor *is* Kwai's Overlord-class tank; the plain Overlord was removed from
  Kwai's roster.
- Doctrine tooltips naming "Red Guard / Tank Hunter" cover the renamed
  **Panzergrenadier / Panzerjäger** (same underlying objects / weapons).

---

## Totals

- **Building researches:** 15 (Propaganda Center) + 5 (Industrial Plant) + 4
  (War Factory / Emperor Defense) + 2 (Nuclear Silo) + 2 (Internet Center) + 2
  (Airfield) + 1 (Command Center) + 1 (Barracks) = **32 distinct building
  researches**, plus the 2-way Land/EMP Mines pair available per structure.
- **Vehicle field upgrades:** 5.
- Data harvested from the effective installed stack on 2026-07-11; regenerate
  with `harvest3.py` in this directory if the stack changes.
