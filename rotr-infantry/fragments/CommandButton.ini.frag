CommandButton Tank_Command_ShmelTrooperSmokeRocket
  Command                 = FIRE_WEAPON
  WeaponSlot              = SECONDARY
  Options                 = OK_FOR_MULTI_SELECT NEED_TARGET_POS
  TextLabel               = CONTROLBAR:TankShmelSmokeRocket
  ButtonImage             = SSRocketShmelSmoke
  ButtonBorderType        = ACTION ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipTankShmelSmokeRocket
  CursorName              = LaserGuidedMissiles
  InvalidCursorName       = GenericInvalid
  SpecialPower            = TomahawkGroundAttack
  RadiusCursorType        = SPYSATELLITE
End

CommandButton Tank_Command_ShmelTrooperAntiToxinRocket
  Command                 = FIRE_WEAPON
  WeaponSlot              = TERTIARY
  Options                 = OK_FOR_MULTI_SELECT NEED_TARGET_POS
  TextLabel               = CONTROLBAR:TankShmelAntiToxinRocket
  ButtonImage             = SSRocketShmelAntiTox
  ButtonBorderType        = ACTION ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipTankShmelAntiToxinRocket
  CursorName              = LaserGuidedMissiles
  InvalidCursorName       = GenericInvalid
  SpecialPower            = NukeGroundAttack
  RadiusCursorType        = SPYSATELLITE
End

CommandButton Tank_Command_ConstructChinaInfantryShmelTrooper
  Command           = UNIT_BUILD
  Object            = Tank_ChinaInfantryShmelTrooper
  TextLabel         = CONTROLBAR:ConstructTankShmelTrooper
  ButtonImage       = SRShmelTrooper
  ButtonBorderType  = BUILD
  DescriptLabel     = CONTROLBAR:ToolTipTankBuildShmelTrooper
  UnitSpecificSound = MoneyWithdraw
End

CommandButton Tank_Command_ConstructChinaInfantryShockTrooper
  Command           = UNIT_BUILD
  Object            = Tank_ChinaInfantryShockTrooper
  TextLabel         = CONTROLBAR:ConstructTankShockTrooper
  ButtonImage       = SRShockTrooper
  ButtonBorderType  = BUILD
  DescriptLabel     = CONTROLBAR:ToolTipTankShockTrooper
  UnitSpecificSound = MoneyWithdraw
End
