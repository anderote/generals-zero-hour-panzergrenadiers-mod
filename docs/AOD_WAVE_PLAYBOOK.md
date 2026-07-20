# AOD / Survival Map Script Playbook

Distilled from full binary script decodes of 8 maps (dumps/ *.txt, decoded with
mapscript.py — every chunk re-parsed to exact boundaries, zero errors):
Noobzillas Gambit v12, AOD SWARM by wWw, AOD World War 3, AOD Pasha Challenges
You (4P), AOD Pasha's Pentagram, Time To Kill (NeoMaurice), TTK Testing
Grounds, plus the stock "A River Divided (2x6) V5" as a non-AOD baseline.

## 1. Wave engine archetypes

**A. Clear-gated ladder (Noobzillas — cleanest design).** One team per wave per
lane (`Wave_N_A/B/C`, maxInstances=1). Every wave team carries generic hook
`IncreaseCounterOnTeamKilled`:

    SCRIPT 'IncreaseCounterOnTeamKilled'  (subroutine, attached via teamGenericScriptHook2)
      IF TEAM_DESTROYED '<This Team>'
      DO INCREMENT_COUNTER 1, 'WaveKilledCounter'

Wave N+1 arms when the counter proves all 3 lanes of wave N died:

    SCRIPT 'Wave_6_TimerStart' (one-shot)
      IF COUNTER 'WaveKilledCounter', 3, 15        ; comparison 3 = EQUAL, value 15 = 5 waves x 3 lanes
      DO SET_MILLISECOND_TIMER 'Wave_6_Timer', 20.00
      DO SHOW_MILITARY_CAPTION 'Wave 5 Defeated', 8000
      DO DISPLAY_COUNTDOWN_TIMER 'Wave_6_Timer', 'SCRIPT:CHI02xReinforcementTimer'

    SCRIPT 'Wave_6_Spawn' (one-shot)
      IF TIMER_EXPIRED 'Wave_6_Timer'
      DO CREATE_REINFORCEMENT_TEAM 'Wave_6_A', 'spawnPosA'   (x3 lanes)

**B. Fixed-schedule chain (TTK NeoMaurice — pressure design).** Each wave is a
one-shot script that enables the next and sets its timer; waves come whether or
not you cleared the last one:

    SCRIPT 'USA_Wave1' (one-shot)
      IF TIMER_EXPIRED 'TIMER_A_USA_Wave1'
      DO ENABLE_SCRIPT 'USA_Wave2'
      DO SET_MILLISECOND_TIMER 'TIMER_A_USA_Wave2', 90.00
      DO SHOW_MILITARY_CAPTION 'Wave 1', 8000
      DO CREATE_REINFORCEMENT_TEAM 'Wave_A_1', 'SPAWN_1'      (x6 spawn points)
      DO INCREMENT_COUNTER 1, 'COUNTER_Waves'

**C. Randomized lanes (SWARM, Pasha).** Dozens of independent timers armed with
`SET_RANDOM_MSEC_TIMER 'l5-2', 30.00, 150.00`; each lane script re-arms its own
random timer -> unpredictable composition ("100+ different combinations").
Pasha layers `SET_FLAG` + `ENABLE_SCRIPT/DISABLE_SCRIPT` chains for phase logic
(10 ground waves, 3 air strikes, 3 amphibious, 3 tunnel sneaks, 1 air drop).

## 2. Wave content & escalation

- Composition lives in TEAM DICTS, not scripts: `teamUnitType1..7` +
  min/max counts, `teamMaxInstances=1` per wave-team.
- Noobzillas ramp (per lane): technicals -> rocket buggies -> combat bikes ->
  battle buses -> MiGs -> Helixes -> buggy+Chinook mix -> Spectre gunships ->
  Raptors -> mixed elite air + Colonel Burton (wave 10 = boss mix).
  Infantry first, then light vehicles, then air, then mixed elite is the
  standard ladder across all harvested maps.
- **Veterancy is a team-dict key**: `teamVeterancy = 3` (HEROIC) on late waves
  (engine reads TheKey_teamVeterancy in TeamTemplateInfo; no script action
  needed). Noobzillas gives waves 7-10 veterancy 3.
- Movement: `teamOnCreateScript` -> subroutine doing
  `TEAM_FOLLOW_WAYPOINTS_EXACT '<This Team>', 'path_A', 0` (parade to the
  defense line), or `TEAM_HUNT '<This Team>'` (TTK bosses) to seek players
  anywhere. `teamEnemySightedScript`/`teamAllClearScript` re-issue the path so
  teams don't stall after skirmishes.

## 3. Boss waves

TTK: dedicated end-boss team (`EndBoss_MOAG`) spawned by an armed one-shot;
victory gated on its death; boss gets its own behavior subroutine cycling
attitude + forced moves + voice barks:

    SCRIPT 'ZeBoss_RoutineSETUP' (sub, teamOnCreateScript)
      DO TEAM_HUNT '<This Team>' ; DO SET_MILLISECOND_TIMER 'ZeBoss_RoutineTimer1', 30.00
    SCRIPT 'Victory!'  IF TEAM_DESTROYED 'EndBoss_MOAG' -> ENABLE_SCRIPT 'Victory! Closing Game'

Noobzillas wave 10 doubles as boss (elite air mix + hero infantry).

## 4. Money: starting cash + bounties

- Difficulty-scaled starting money via the e/n/h script flags (the game's own
  difficulty selector — no custom UI needed):

    SCRIPT 'money e' (easy-only: enh=100)   DO PLAYER_GIVE_MONEY 'player0', 20000  (x8 slots)
    SCRIPT 'money n' (normal-only: enh=010) ... 15000
    SCRIPT 'money h' (hard-only: enh=001)   ... 10000        (AOD SWARM)
    TTK equivalent uses PLAYER_SET_MONEY 50000 + DISABLE_SCRIPT of the other two.

- Clean bounty idiom = per-wave-cleared grants (COUNTER gate + PLAYER_GIVE_MONEY
  to every `playerN` lobby slot). No per-kill action exists in the engine's
  script set; kill income is otherwise done data-side (INI Bounty) — map-side,
  wave-cleared grants are what the good maps ship.

## 5. Difficulty selectors

Two proven mechanisms:
1. e/n/h script flags (per-script easy/normal/hard bits) — SWARM & TTK gate
   whole script variants on lobby difficulty. Zero extra machinery.
2. Flag/counter votes (Pasha): `SET_FLAG`/`FLAG` conditions +
   `PLAYER_HAS_COMPARISON_UNIT_TYPE_IN_TRIGGER_AREA` (drive a dozer into a
   marked area to pick a mode; also used as "TestMode"/anti-cheat toggles).

## 6. Population / anti-lag management

- `teamMaxInstances = 1` on every wave team (all maps).
- Pasha's cleanup idiom — bulk-delete stale teams on a timer (TEAM_DELETE pops
  one instance per call, hence repeats):

    SCRIPT 'KK_1'  IF TIMER_EXPIRED 'kk1'
      DO TEAM_DELETE 'K1.1. 1' ; DO TEAM_DELETE 'K1.1. 2' ; ...

- Noobzillas' KillZone: `TEAM_ENTERED_AREA_PARTIALLY '<This Team>','KillZone',3
  -> TEAM_KILL '<This Team>'` (leakers die at the back line instead of piling).
- TTK deletes named helper objects (`NAMED_DELETE`) as phases end.

## 7. Defeat / objective logic

- Noobzillas: `SKIRMISH_PLAYER_HAS_UNITS_IN_AREA '<This Player>','DefeatArea'
  -> DEFEAT` (enemy list owner reaching the protected zone = players lose);
  `COUNTER 'WaveKilledCounter' == 30 -> VICTORY`.
- TTK: boss reaching `AREA_FinishLine` (TEAM_INSIDE_AREA_PARTIALLY) -> DEFEAT;
  boss death -> VICTORY. Also an "Anti-Dummkopf" lobby-shape check that ends
  the match if the AI player is in the wrong slot.
- Announcements: SHOW_MILITARY_CAPTION for wave n/incoming/defeated;
  DISPLAY_COUNTDOWN_TIMER + HIDE_COUNTDOWN_TIMER for next-wave clocks
  (label can be any 'SCRIPT:...' string key; stock keys reused).

## 8. Ownership of the attacking side

- Noobzillas/SWARM/Pasha: waves owned by a Skirmish AI side (`SkirmishGLA`) —
  requires the lobby to include that faction ("Enemy AI must be set to easy
  GLA..." caption).
- TTK: waves owned by MAP-DEFINED sides (`PlyrCivilian`/custom players) with
  `PLAYER_RELATES_PLAYER 'Civ_Evil','playerN', 0` (0=ENEMIES) against every
  lobby slot — works regardless of lobby AI composition. This is the superior
  pattern for a survival variant and the one used in the Phase 3 build.

## 9. Wire-format facts used by the builder (from engine source + dumps)

- Script chunks: ScriptList v1 > ScriptGroup v2 > Script v2 (4 strings, 6 flag
  bytes active/oneshot/easy/normal/hard/subroutine, i32 delayEvalSeconds) >
  OrCondition v1 (ANDed Conditions; multiple OrConditions = OR) > Condition v4 /
  ScriptAction v2 (i32 enum, u32 (symbolId<<8)|3 NameKey, i32 nParms, params).
- Parameter: i32 type, then COORD3D(16) = 3 floats, else i32/f32/lenstr.
  UNIT=14, OBJECT_TYPE=15, COORD3D=16, ANGLE=17, DIALOG=21 (verified in dumps).
- COUNTER condition params: (COUNTER name, COMPARISON int, INT value);
  comparison observed: 3 = equal (Noobzillas' ladder), <(0/1/2/4/5) per
  Scripts.h Parameter comparison enum.
- SET_TIMER takes FRAMES; SET_MILLISECOND_TIMER takes REAL seconds.
- `teamVeterancy` int (REGULAR..HEROIC=3, patched engine adds HEROIC2..6),
  `teamGenericScriptHook0..15`, `teamOnCreateScript`, `teamOnDestroyedScript`,
  `teamEnemySightedScript`, `teamAllClearScript` are all team-dict keys.
- New symbol-table entries may be appended for dict keys absent from a map.
