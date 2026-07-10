Locomotor ShockTrooperLocomotor
  Surfaces = GROUND RUBBLE
  Speed = 20               ; in dist/sec
  SpeedDamaged = 20        ; in dist/sec
  TurnRate = 500           ; in degrees/sec
  TurnRateDamaged = 500    ; in degrees/sec
  Acceleration = 100       ; in dist/(sec^2)
  AccelerationDamaged = 50 ; in dist/(sec^2)
  Braking = 100            ; in dist/(sec^2)
  MinTurnSpeed = 0         ; in dist/sec
  ZAxisBehavior = NO_Z_MOTIVE_FORCE
  Appearance = TWO_LEGS
  StickToGround = Yes      ; walking guys aren't allowed to catch huge (or even small) air.
  GroupMovementPriority = MOVES_FRONT;   Moves in the front of a group, behind small arms, ahead of artillery
End

Locomotor ShmelRocketLocomotor
  Surfaces = AIR
  Speed = 300               ; in dist/sec
  MinSpeed = 120            ; in dist/sec. (THRUST items must have nonzero minspeeds!)
  Acceleration = 600        ; in dist/(sec^2)
  Braking = 0               ; in dist/(sec^2)
  TurnRate = 100            ; in degrees/sec
  MaxThrustAngle = 45       ; in degrees (NOT degrees/sec)
  AllowAirborneMotiveForce = Yes
  Appearance = THRUST
End

Locomotor ShocktrooperRocketRifleLocomotor
  Surfaces = AIR
  Speed = 750               ; in dist/sec
  MinSpeed = 120            ; in dist/sec. (THRUST items must have nonzero minspeeds!)
  Acceleration = 1000       ; in dist/(sec^2)
  Braking = 0               ; in dist/(sec^2)
  TurnRate = 100            ; in degrees/sec
  MaxThrustAngle = 45       ; in degrees (NOT degrees/sec)
  AllowAirborneMotiveForce = Yes
  Appearance = THRUST
End

Locomotor BerkutMissileDodgeJetLocomotor
  Surfaces = AIR
  Speed = 400                ; in dist/sec
  MinSpeed = 0               ; in dist/sec
  TurnRate = 9999            ; in degrees/sec
  Acceleration = 9999        ; in dist/(sec^2)
  Lift = 400                 ; in dist/(sec^2)
  Braking = 4000             ; in dist/(sec^2)
  MinTurnSpeed = 360         ; in dist/sec
  PreferredHeight = 100
  AllowAirborneMotiveForce = Yes
  ZAxisBehavior = RELATIVE_TO_HIGHEST_LAYER
  Appearance = HOVER
End

