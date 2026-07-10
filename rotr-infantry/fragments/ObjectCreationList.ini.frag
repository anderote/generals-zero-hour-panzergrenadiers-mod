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

ObjectCreationList OCL_ShockTrooperRocketRifleModeTrigger
  CreateObject
    ObjectNames = ShockTrooperRemoveUpgradeRocketRifleObject
    IgnorePrimaryObstacle = Yes
    Disposition = LIKE_EXISTING
    Count = 1
    RequiresLivePlayer = Yes
  End
End

ObjectCreationList OCL_GenericDummyRider2Trigger
  CreateObject
    ObjectNames = ShockTrooperRemoveUpgradeTeslaGunObject
    IgnorePrimaryObstacle = Yes
    Disposition = LIKE_EXISTING
    Count = 1
    RequiresLivePlayer = Yes
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

