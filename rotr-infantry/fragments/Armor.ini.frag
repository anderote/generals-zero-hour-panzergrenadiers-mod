Armor ShockTrooperArmor
  Armor = CRUSH             200%    ;humans are easily crushed ["I'm crushing your head"]
  Armor = MELEE             100%
  Armor = COMANCHE_VULCAN   80%
  Armor = SMALL_ARMS        80%
  Armor = EXPLOSION         80%
  Armor = AURORA_BOMB       80%
  Armor = ARMOR_PIERCING    10%     ;humans don't get hit by tank rounds.
  Armor = STEALTHJET_MISSILES 10%     ;humans don't get hit by tank rounds.
  Armor = JET_MISSILES      50%
  Armor = INFANTRY_MISSILE  10%
  Armor = FLAME             50%     ;humans don't like fire
  Armor = PARTICLE_BEAM     150%    ;humans don't fare well against orbital beams...
  Armor = RADIATION         50%     ;Radiation does less damage to tanks. 
  Armor = MICROWAVE          0%
  Armor = POISON            50%     ;Poison does a little damage, just for balance reasons.  
  Armor = SNIPER            100%
  Armor = LASER             999%    ;LASERs are anti-personnel and anti-projectile only (for point defense laser)
  Armor = HAZARD_CLEANUP    0%      ;Not harmed by cleaning weapons
  Armor = KILL_PILOT        0%
  Armor = SURRENDER         100%    ;Capture type weapons are effective only against infantry.
  Armor = SUBDUAL_MISSILE   0%
  Armor = SUBDUAL_VEHICLE   0%
  Armor = SUBDUAL_BUILDING  0%
  Armor = SUBDUAL_UNRESISTABLE  0%
  Armor = HACK              0%      ;Special damage should not be used for regulair weapons
  Armor = DEPLOY            0%      ;Special damage should not be used for regulair weapons
End

Armor InvulnerableArmorAll
  Armor = DEFAULT         0%      ;this sets the level for all nonspecified damage types
End

