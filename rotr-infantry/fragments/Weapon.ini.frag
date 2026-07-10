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

Weapon ShockTrooperRocketRifle
  PrimaryDamage          = 10.0
  PrimaryDamageRadius    = 2.0 ; 0 primary radius means "hits only intended victim"
  AttackRange            = 180.0
  DamageType             = EXPLOSION
  DeathType              = EXTRA_4
  WeaponSpeed            = 600               
  ProjectileObject       = ShockTrooperGuidedMissile
  FireFX                 = WeaponFX_GenericShockTrooperRocketRifleFire
  VeterancyFireFX        = HEROIC WeaponFX_GenericShockTrooperRocketRifleFireWithRedTracers
  ProjectileDetonationFX = FX_ShockTrooperRocketExplosion
  FireSound              = RocketBuggyWeapon
  RadiusDamageAffects    = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots      = 80       ; time between shots, msec
  ClipSize               = 8        ; how many shots in a Clip (0 == infinite)
  ClipReloadTime         = 1500     ; how long to reload a Clip, msec
  AutoReloadWhenIdle     = 1510
  WeaponBonus            = GARRISONED RANGE  133%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus            = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus            = PLAYER_UPGRADE RANGE  133% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus            = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon ShockTrooperTeslaWeapon
  PrimaryDamage           = 30.0
  AttackRange             = 140.0
  PrimaryDamageRadius     = 5.0
  DamageType              = MELEE
  DeathType               = POISONED_GAMMA ; This is now a Tesla Death Animation
  WeaponSpeed             = 99999
  LaserName               = TeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  FireSoundLoopTime       = 40
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 50
  WeaponBonus             = GARRISONED RANGE  145%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus             = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus             = PLAYER_UPGRADE RANGE  145% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon ShockTrooperTeslaSubdualWeapon
  PrimaryDamage           = 10.0
  AttackRange             = 140.0
  DamageType              = SUBDUAL_UNRESISTABLE
  DeathType               = POISONED_GAMMA ; This is now a Tesla Death Animation
  WeaponSpeed             = 99999
  LaserName               = TeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  FireSoundLoopTime       = 40
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 50
  WeaponBonus             = GARRISONED RANGE  145%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus             = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus             = PLAYER_UPGRADE RANGE  145% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon HeroicShockTrooperTeslaWeapon
  PrimaryDamage           = 30.0
  AttackRange             = 140.0
  PrimaryDamageRadius     = 5.0
  DamageType              = MELEE
  DeathType               = POISONED_GAMMA ; This is now a Tesla Death Animation
  WeaponSpeed             = 99999
  LaserName               = HeroicTeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  FireSoundLoopTime       = 40
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 50
  WeaponBonus             = GARRISONED RANGE  145%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus             = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus             = PLAYER_UPGRADE RANGE  145% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon HeroicShockTrooperTeslaSubdualWeapon
  PrimaryDamage           = 10.0
  AttackRange             = 140.0
  DamageType              = SUBDUAL_UNRESISTABLE
  DeathType               = POISONED_GAMMA ; This is now a Tesla Death Animation
  WeaponSpeed             = 99999
  LaserName               = HeroicTeslaTrooperLaserBeam
  FireSound               = AvengerPointDefenseLaserPulse
  FireSoundLoopTime       = 40
  LaserBoneName           = MUZZLE01
  DelayBetweenShots       = 50
  WeaponBonus             = GARRISONED RANGE  145%     ;Bonus range when garrisoned default value is at 133% which translates to 33% extra range
  WeaponBonus             = GARRISONED DAMAGE 125%     ;Bonus damage when garrisoned default value is at 125% which translates to 25% extra damage
  WeaponBonus             = PLAYER_UPGRADE RANGE  145% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125% ;This makes sure that infantry inside containers get their garrison bonuses if turned on by the container.
End

Weapon ShockTrooperSwitchToRocketGunMode
  PrimaryDamage    = 0.0
  DamageType       = LASER
  FireOCL          = OCL_GenericDummyRider1_Normal
  ClipSize         = 1
  ClipReloadTime   = 1000
End

Weapon ShockTrooperSwitchToTeslaGunMode
  PrimaryDamage    = 0.0
  DamageType       = LASER
  FireOCL          = OCL_GenericDummyRider2_Normal
  ClipSize         = 1
  ClipReloadTime   = 1000
End

