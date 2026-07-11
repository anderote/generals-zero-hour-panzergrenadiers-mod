# Multiplayer / Replay Compatibility

**Status: PASS.** A full read-only determinism audit of both the engine fork
(`feature/graphics-quality`) and the mod data stack found **zero desync-causing
defects**. The project is MP/replay-safe **provided both peers run the identical
engine build and the identical mod stack** (see the headline caveat below).

GeneralsX/SAGE is a lockstep-deterministic RTS: every peer runs the same
simulation from the same inputs. A desync happens only if gameplay-affecting
state diverges between peers, or if a peer consumes the shared simulation RNG
stream a different number of times or in a different order.

## Engine features — all deterministic-safe

Every gameplay-affecting engine feature added this project was audited against
its actual source:

| Feature | Why it's safe |
|---|---|
| Combat stances (`MSG_SET_UNIT_STANCE`) | Sim mutation lives in the dispatch handler, not the client emit; xfer append-only, default = vanilla |
| Multi-select bulk build / shift-x5 (`MSG_QUEUE_UNIT_CREATE`) | N ordinary networked messages, each carrying an explicit producer objectID validated in dispatch; unique-ID mutation is retail-inherited and not in the frame CRC |
| Guard-moving-unit (`MSG_DO_GUARD_OBJECT`) | Local pick/relationship read in the input layer only; target objectID goes on the wire, follow-math is in-sim |
| Line-move (`MSG_DO_MOVETO_LINE`) | Two terrain endpoints on the wire; in-sim fan-out uses a stable insertion sort, no RNG |
| Waypoints (`MSG_ADD_WAYPOINT`) + patrol (`MSG_DO_PATROL`) | Reuses the existing networked waypoint path; patrol loop is an index reset over already-xfer'd `m_goalPath`; xfer v1→v2 symmetric |
| Persistent wrecks (`WreckLifetimeScale`) | The sim-RNG draw runs unconditionally first; the scale multiply consumes no RNG, so the stream stays aligned. HULK-only, config-identical on all peers |
| Weapon tracers (`ExtraTracers`) | Client RNG only, object-less self-expiring drawable, zero sim writes. Default off |
| 8-veterancy, vision-scaling, kill-counter, RequiredUpgrade | All recompute from synchronized template/player state at sim time; no local/mouse/client-RNG reads |
| Crash-hardening guards | All branch on deterministic tombstones (`isDestroyed()` / null members set identically on every peer by the same event); live path is byte-identical; guarded early-returns add/remove no RNG draw |
| Health bars, stats panel, rank insignia, XP readout | Client display only — read sim state, write only to client `DisplayString`s |

New message enums are appended at the tail in the same order in both engine
trees, so wire ordinals stay consistent.

## Mod data stack

Data INI cannot desync a deterministic engine (all peers load the same INIs).
The per-layer closure artifacts show the gameplay def graph (Object / Weapon /
Locomotor / OCL / Upgrade) closes; the flagged cross-layer refs resolve. No data
mechanism introduces non-sim randomness or reads system state — all data-driven
randomness routes through the engine's `GameLogicRandomValue`. The Kwai shellmap
recast is menu-background only and cannot affect a match sim.

Residual flags are asset-presence (audio/art), not dangling gameplay defs — and
a missing asset fails **identically on both peers** (a shared content bug, not a
desync).

## Headline caveat

This is a **client-side mod**. MP and replays only work if **both** players have:

1. the **same engine build**, and
2. a **byte-identical mod stack** — every `.big`, same load order.

There is no runtime version handshake. A mismatch produces a one-sided crash or
dangling-ref drop, not graceful failure. Coordinate builds and mods out-of-band.

## Non-blocking notes

- Rank-gated command buttons restrict the **cameo display** only; there is no
  execution-side enforcement yet. A modified client could issue a rank-gated
  order below rank — a fairness/cheat surface, **not** a desync (the order
  dispatches identically on all peers). Enforce when a concrete rank-gated
  order is wired.
- Xfer version gating depends on the `RETAIL_COMPATIBLE_CRC` / `_XFER_SAVE`
  compile flags — subsumed by the same-build requirement.
