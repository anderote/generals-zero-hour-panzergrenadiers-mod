FXList FX_MoleBombEnterOrExitGround
  TerrainScorch
    Type = RANDOM 
    Radius = 8
  End
  ParticleSystem
    Name = ArtilleryBarrageDebris
    CreateAtGroundHeight = Yes
  End
  ParticleSystem
    Name = ArtilleryBarrageShockwave
    Offset = X:0 Y:0 Z:2
    CreateAtGroundHeight = Yes
  End
  Sound
    Name = ExplosionDirt
  End
End

FXList FX_ShmelTrooperAntiToxinRocketExplosion

  TerrainScorch
    Type = RANDOM 
    Radius = 5
  End
  
  ParticleSystem
    Name = ShmelRocketAntiToxinExplosion
    Offset = X:-12 Y:0 Z:0
  End
  
  ParticleSystem
    Name = ShmelRocketAntiToxinDetonationCloud
  End
  
  ParticleSystem
    Name = MammothTankExplosionLenzflare
    Offset = X:0.0 Y:0.0 Z:10.0
  End
  
  ParticleSystem
    Name = ShmelRocketAntiToxinDebris
  End
  
  Sound
    Name = ExplosionFlashBang
  End
  
  Sound
    Name = ExplosionFlashBang
  End
  
End

FXList WeaponFX_ShmelRocketExplosion

  TerrainScorch
    Type = RANDOM 
    Radius = 20
  End

  ParticleSystem
    Name   = ShmelExplosion
    Offset = X:0.0 Y:0.0 Z:5.0
  End

  ParticleSystem
    Name = SpectreHowitzerExplosionCloud
  End
  
  ParticleSystem
    Name = CarpetBombWave
    Offset = X:0.0 Y:0.0 Z:2.0
  End
  
  ParticleSystem
    Name = MammothTankExplosionLenzflare
    Offset = X:0.0 Y:0.0 Z:10.0
  End

  Sound
    Name = ExplosionFire
  End
  
End

FXList WeaponFX_ShmelRocketExplosionUpgraded
  
  ParticleSystem
    Name = SpectreGunshipExplosionLight
  End

  ParticleSystem
    Name   = ShmelDetonationDustWave
    Offset = X:0.0 Y:0.0 Z:3.0
  End
  
End

FXList WeaponFX_ShmelTrooperAntiToxinSmoke
  ParticleSystem
    Name = ShmelRocketAntiToxinSmoke
    Radius = 0  20 UNIFORM
    Height = 12 18 UNIFORM
  End
End

FXList FX_ShockTrooperRocketExplosion
  Sound
    Name = ExplosionRocketBuggyMissile
  End
  ParticleSystem
    Name = StructureDamagedFlash
  End
  ParticleSystem
    Name = TankStruckDebris
    OrientToObject = Yes
    Ricochet = Yes
  End
End

FXList WeaponFX_GenericShockTrooperRocketRifleFire
  LightPulse 
    Color = R:255 G:255 B:128
    Radius = 10
    IncreaseTime = 0
    DecreaseTime = 200
  End
  ParticleSystem
    Name = GattlingCannonLenzflare
    OrientToObject = Yes
    Offset = X:0.0 Y:0.0 Z:0.0
  End
  ParticleSystem
    Name = EmptyShockRocketCassingsFalling
    OrientToObject = Yes
    Offset = X:-4.0 Y:0.0 Z:0.0
  End
End

FXList WeaponFX_GenericShockTrooperRocketRifleFireWithRedTracers
  LightPulse 
    Color = R:128 G:0 B:0
    Radius = 25
    IncreaseTime = 0
    DecreaseTime = 200
  End
  ParticleSystem
    Name = HeroicGattlingCannonLenzflare
    OrientToObject = Yes
    Offset = X:0.0 Y:0.0 Z:0.0
  End
  ParticleSystem
    Name = EmptyShockRocketCassingsFalling
    OrientToObject = Yes
    Offset = X:-4.0 Y:0.0 Z:0.0
  End
End

FXList FX_IfantryTeslaDie
  TerrainScorch
    Type = RANDOM 
    Radius = 7
  End
  Sound
    Name = ExplosionPatriotEMP
  End
End

