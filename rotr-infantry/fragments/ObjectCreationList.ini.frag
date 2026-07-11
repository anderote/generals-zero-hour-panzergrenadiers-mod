ObjectCreationList OCL_RussiaExplodedDeath
  CreateDebris
    ModelNames = RIShmlTrp_SKN
    AnimationSet = NITHNT_SKL.NITHNT_ADTA1 NITHNT_SKL.NITHNT_ADTA2 NITHNT_SKL.NITHNT_ADTA3
    FXFinal = FX_TechnicalGunnerHitsGround
    OkToChangeModelColor = Yes
    IgnorePrimaryObstacle = Yes
    Mass = 5.0
    Disposition = RANDOM_FORCE
    OrientInForceDirection = Yes
    ExtraBounciness = -10.0 ; we don't want this guy to bounce at all.
    MinForceMagnitude = 8
    MaxForceMagnitude = 12
    MinForcePitch = 50
    MaxForcePitch = 60
    Shadow = SHADOW_DECAL
  End
End

ObjectCreationList OCL_RussiaExplodedDeathShockTrooper
  CreateDebris
    ModelNames = RITslTrp_SKN
    AnimationSet = NIGATT_SKL.NIGATT_ADTD1 NIGATT_SKL.NIGATT_ADTD2 NIGATT_SKL.NIGATT_ADTD3
    FXFinal = FX_TechnicalGunnerHitsGround
    OkToChangeModelColor = Yes
    IgnorePrimaryObstacle = Yes
    Mass = 5.0
    Disposition = RANDOM_FORCE
    OrientInForceDirection = Yes
    ExtraBounciness = -10.0 ; we don't want this guy to bounce at all.
    MinForceMagnitude = 8
    MaxForceMagnitude = 12
    MinForcePitch = 50
    MaxForcePitch = 60
    Shadow = SHADOW_DECAL
  End
End

ObjectCreationList OCL_ShmelTrooperSmokeScreen
 CreateObject
   ObjectNames = RussianSmokeGrenadeSmokeScreen
   Disposition = ON_GROUND_ALIGNED LIKE_EXISTING
 End
End

ObjectCreationList OCL_ShmelTrooperAntiToxinFoam
 CreateObject
   ObjectNames = RussianShmelTrooperAntiToxinFoam
   Disposition = ON_GROUND_ALIGNED LIKE_EXISTING
 End
End

ObjectCreationList OCL_ShmellRocketFire
 CreateObject
   ObjectNames = ShmellBurningEmbersFireField
   Disposition = ON_GROUND_ALIGNED
 End
End

ObjectCreationList OCL_ShockTrooperTeslaChain
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNode
    Count       = 1
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
End

ObjectCreationList OCL_ShockTrooperTeslaChainHeroic
  ; heroic Shock Troopers chain from TWO nodes (more arcs, longer-lived)
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNodeHeroic
    Count       = 1
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNodeHeroic
    Count       = 1
    Offset      = X:14.0 Y:10.0 Z:0.0
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
End

ObjectCreationList OCL_TeslaDeathInfantry
  CreateObject
    ObjectNames = TeslaInfantry
    Disposition = LIKE_EXISTING     
    SkipIfSignificantlyAirborne = Yes
  End
End

ObjectCreationList OCL_ViralInfantryDeath
  CreateObject
    ObjectNames = ToxicInfantryGamma
    Disposition = LIKE_EXISTING     
    SkipIfSignificantlyAirborne = Yes
  End
  CreateObject
    ObjectNames = ViralGasCloud
    Disposition = LIKE_EXISTING     
    SkipIfSignificantlyAirborne = Yes
  End
End

