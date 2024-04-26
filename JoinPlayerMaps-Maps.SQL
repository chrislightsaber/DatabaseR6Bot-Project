SELECT 
  Map.MapName, 
  PlayerMap.Username, 
  PlayerMap.Win_Percent, 
  PlayerMap.Matches_Played
FROM 
  Map
JOIN 
  PlayerMap ON Map.MapName = PlayerMap.MapName;
