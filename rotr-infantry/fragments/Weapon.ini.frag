Weapon RussiaShmellTrooperMissileLauncher
  PrimaryDamage = 55.0
  PrimaryDamageRadius = 5.0
  SecondaryDamage = 15.0
  SecondaryDamageRadius = 25.0
  AttackRange = 175.0
  MinimumAttackRange = 5.0
  ScatterRadius = 10.0
  DamageType = FLAME
  DeathType = BURNED
  ProjectileObject = ShmelTrooperRocket
  ProjectileExhaust = ShmelRocketExhaust
  VeterancyProjectileExhaust = HEROIC HeroicShmelRocketExhaust
  RadiusDamageAffects = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots = 3500  ; time between shots, msec
  AutoReloadsClip = Yes 
  FireSound = TankHunterWeapon
  FireFX = FX_BuggyMissileIgnition
  ProjectileDetonationFX = WeaponFX_ShmelRocketExplosion
  ProjectileCollidesWith = STRUCTURES
  WeaponBonus = GARRISONED RANGE  133%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus = PLAYER_UPGRADE RANGE  133% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon RussiaShmellTrooperSmokeMissileLauncher
  PrimaryDamage           = 0.0
  PrimaryDamageRadius     = 0.0
  ScatterRadius           = 30.0
  AttackRange             = 220.0
  MinimumAttackRange      = 180.0
  DamageType              = FLAME
  DeathType               = EXPLODED
  WeaponSpeed             = 260         ; dist/sec 
  ProjectileObject        = ShmelTrooperSmokeRocketProjectile
  FireFX                  = FX_BuggyMissileIgnition
  FireSound               = TankHunterWeapon
  ProjectileDetonationFX  = FX_MoleBombEnterOrExitGround
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  ClipSize                = 1         ; how many shots in a Clip (0 == infinite)
  ClipReloadTime          = 25000     ; how long to reload a Clip, msec
  PreAttackDelay          = 100
  PreAttackType           = PER_SHOT
End

Weapon RussiaShmellTrooperSmokeMissileLauncherHeroic
  PrimaryDamage           = 0.0
  PrimaryDamageRadius     = 0.0
  ScatterRadius           = 30.0
  AttackRange             = 220.0
  MinimumAttackRange      = 180.0
  DamageType              = FLAME
  DeathType               = EXPLODED
  WeaponSpeed             = 260         ; dist/sec 
  ProjectileObject        = ShmelTrooperSmokeRocketHeroicProjectile
  FireFX                  = FX_BuggyMissileIgnition
  FireSound               = TankHunterWeapon
  ProjectileDetonationFX  = FX_MoleBombEnterOrExitGround
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  ClipSize                = 1         ; how many shots in a Clip (0 == infinite)
  ClipReloadTime          = 25000     ; how long to reload a Clip, msec
  PreAttackDelay          = 100
  PreAttackType           = PER_SHOT
End

Weapon RussiaShmellTrooperAntiToxinMissileLauncher
  PrimaryDamage           = 0.0
  PrimaryDamageRadius     = 0.0
  ScatterRadius           = 5.0
  AttackRange             = 220.0
  MinimumAttackRange      = 180.0
  DamageType              = POISON
  DeathType               = EXPLODED
  WeaponSpeed             = 260         ; dist/sec 
  ProjectileObject        = ShmelTrooperAntiToxinRocketProjectile
  FireFX                  = FX_BuggyMissileIgnition
  FireSound               = TankHunterWeapon
  ProjectileDetonationFX  = FX_ShmelTrooperAntiToxinRocketExplosion
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  ClipSize                = 1         ; how many shots in a Clip (0 == infinite)
  ClipReloadTime          = 25000     ; how long to reload a Clip, msec
  PreAttackDelay          = 100
  PreAttackType           = PER_SHOT
End

Weapon RussiaShmellTrooperAntiToxinMissileLauncherHeroic
  PrimaryDamage           = 0.0
  PrimaryDamageRadius     = 0.0
  ScatterRadius           = 5.0
  AttackRange             = 220.0
  MinimumAttackRange      = 180.0
  DamageType              = POISON
  DeathType               = EXPLODED
  WeaponSpeed             = 260         ; dist/sec 
  ProjectileObject        = ShmelTrooperAntiToxinRocketHeroicProjectile
  FireFX                  = FX_BuggyMissileIgnition
  FireSound               = TankHunterWeapon
  ProjectileDetonationFX  = FX_ShmelTrooperAntiToxinRocketExplosion
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  ClipSize                = 1         ; how many shots in a Clip (0 == infinite)
  ClipReloadTime          = 25000     ; how long to reload a Clip, msec
  PreAttackDelay          = 100
  PreAttackType           = PER_SHOT
End

Weapon RussiaShmellTrooperSmokeMissilePellets
  PrimaryDamage             = 0.0
  ScatterRadius             = 50.0
  WeaponSpeed               = 9999.0
  DamageType                = EXPLOSION
  DeathType                 = EXPLODED
  ProjectileObject          = GenericHitScanProjectile
  ProjectileDetonationOCL   = OCL_ShmelTrooperSmokeScreen
End

Weapon RussiaShmellTrooperExtraDamageWithInfantryMunitionUpgrade
  PrimaryDamage = 20.0
  PrimaryDamageRadius = 10.0
  SecondaryDamage = 15.0
  SecondaryDamageRadius = 30.0
  DamageType = FLAME
  DeathType = BURNED
  FireOCL = OCL_ShmellRocketFire
  FireFX = WeaponFX_ShmelRocketExplosionUpgraded
  RadiusDamageAffects = ALLIES ENEMIES NEUTRALS
End

Weapon RussianShmelTrooperAntiToxinSmokeWeapon
  PrimaryDamage = 50.0
  PrimaryDamageRadius = 100.0
  DamageType = HAZARD_CLEANUP
  WeaponSpeed = 600
  FireFX = WeaponFX_ShmelTrooperAntiToxinSmoke
  RadiusDamageAffects = ALLIES ENEMIES NEUTRALS NOT_AIRBORNE
  DelayBetweenShots = 200
End

Weapon RussianSmokeGrenadeSmokeScreenWeapon
  PrimaryDamage = 0.0
  DamageType = LASER
  WeaponSpeed = 600
  FireFX = WeaponFX_SmokeScreenWeaponFX
  RadiusDamageAffects = ALLIES ENEMIES NEUTRALS NOT_AIRBORNE
  DelayBetweenShots = 200
End

Weapon PyroFireWalFieldWeapon
  PrimaryDamage               = 1.0
  PrimaryDamageRadius         = 20.0
  DamageType                  = FLAME
  DeathType                   = BURNED
  DelayBetweenShots           = 250
  RadiusDamageAffects         = ALLIES ENEMIES NEUTRALS NOT_SIMILAR
End

Weapon ShockTrooperTeslaWeapon
  ; tesla shock beam: the anti-vehicle component (AP because base
  ; TankArmor takes 0% MELEE damage -- the donor value was dead)
  PrimaryDamage           = 60.0
  PrimaryDamageRadius     = 5.0
  AttackRange             = 140.0
  DamageType              = ARMOR_PIERCING
  DeathType               = POISONED_GAMMA ; tesla death animation
  WeaponSpeed             = 99999
  LaserName               = TeslaTrooperLaserBeam
  LaserBoneName           = MUZZLE01
  FireSound               = AvengerPointDefenseLaserPulse
  DelayBetweenShots       = 1200
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
  WeaponBonus             = GARRISONED RANGE  145%
  WeaponBonus             = GARRISONED DAMAGE 125%
  WeaponBonus             = PLAYER_UPGRADE RANGE  145%
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125%
End

Weapon ShockTrooperTeslaSubdualWeapon
  ; subdual buildup rider: vehicles accumulate this until it
  ; passes their MaxHealth -> DISABLED_SUBDUED for a few seconds
  ; (decays at the target body's SubdualDamageHealRate/Amount)
  PrimaryDamage           = 250.0
  PrimaryDamageRadius     = 10.0
  AttackRange             = 140.0
  DamageType              = SUBDUAL_UNRESISTABLE
  DeathType               = POISONED_GAMMA
  WeaponSpeed             = 99999
  LaserName               = TeslaTrooperLaserBeam
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 1200
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

Weapon ShockTrooperTeslaArcWeapon
  ; anti-infantry fry + chain trigger: FLAME one-shots standard
  ; infantry (<=110.0*1.5 HP) and BURNED lights them up; the hitscan
  ; projectile detonation spawns the chain-lightning node
  PrimaryDamage           = 110.0
  PrimaryDamageRadius     = 20.0
  AttackRange             = 140.0
  DamageType              = FLAME
  DeathType               = BURNED
  WeaponSpeed             = 99999
  ProjectileObject        = GenericHitScanProjectile
  ProjectileDetonationFX  = FX_ShockTrooperElectricRocketExplosion
  ProjectileDetonationOCL = OCL_ShockTrooperTeslaChain
  DelayBetweenShots       = 1200
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

Weapon HeroicShockTrooperTeslaWeapon
  ; tesla shock beam: the anti-vehicle component (AP because base
  ; TankArmor takes 0% MELEE damage -- the donor value was dead)
  PrimaryDamage           = 80.0
  PrimaryDamageRadius     = 5.0
  AttackRange             = 140.0
  DamageType              = ARMOR_PIERCING
  DeathType               = POISONED_GAMMA ; tesla death animation
  WeaponSpeed             = 99999
  LaserName               = HeroicTeslaTrooperLaserBeam
  LaserBoneName           = MUZZLE01
  FireSound               = AvengerPointDefenseLaserPulse
  DelayBetweenShots       = 1200
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
  WeaponBonus             = GARRISONED RANGE  145%
  WeaponBonus             = GARRISONED DAMAGE 125%
  WeaponBonus             = PLAYER_UPGRADE RANGE  145%
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125%
End

Weapon HeroicShockTrooperTeslaSubdualWeapon
  ; subdual buildup rider: vehicles accumulate this until it
  ; passes their MaxHealth -> DISABLED_SUBDUED for a few seconds
  ; (decays at the target body's SubdualDamageHealRate/Amount)
  PrimaryDamage           = 325.0
  PrimaryDamageRadius     = 10.0
  AttackRange             = 140.0
  DamageType              = SUBDUAL_UNRESISTABLE
  DeathType               = POISONED_GAMMA
  WeaponSpeed             = 99999
  LaserName               = HeroicTeslaTrooperLaserBeam
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 1200
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

Weapon HeroicShockTrooperTeslaArcWeapon
  ; anti-infantry fry + chain trigger: FLAME one-shots standard
  ; infantry (<=140.0*1.5 HP) and BURNED lights them up; the hitscan
  ; projectile detonation spawns the chain-lightning node
  PrimaryDamage           = 140.0
  PrimaryDamageRadius     = 20.0
  AttackRange             = 140.0
  DamageType              = FLAME
  DeathType               = BURNED
  WeaponSpeed             = 99999
  ProjectileObject        = GenericHitScanProjectile
  ProjectileDetonationFX  = FX_ShockTrooperElectricRocketExplosion
  ProjectileDetonationOCL = OCL_ShockTrooperTeslaChainHeroic
  DelayBetweenShots       = 1200
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

Weapon ShockTrooperTeslaChainZap
  ; the chain-lightning arc fired by the spawned node
  PrimaryDamage           = 100.0
  PrimaryDamageRadius     = 12.0
  AttackRange             = 90.0
  DamageType              = FLAME
  DeathType               = BURNED
  WeaponSpeed             = 99999
  LaserName               = TeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  DelayBetweenShots       = 500
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

Weapon HeroicShockTrooperTeslaChainZap
  ; the chain-lightning arc fired by the spawned node
  PrimaryDamage           = 120.0
  PrimaryDamageRadius     = 12.0
  AttackRange             = 90.0
  DamageType              = FLAME
  DeathType               = BURNED
  WeaponSpeed             = 99999
  LaserName               = HeroicTeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  DelayBetweenShots       = 500
  RadiusDamageAffects     = ENEMIES NEUTRALS
  AntiGround              = Yes
  AntiAirborneVehicle     = No
  AntiAirborneInfantry    = No
End

