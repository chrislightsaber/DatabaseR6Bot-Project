SELECT 
  Player.Username, 
  Player.KD_Ratio, 
  Player.Ranked_Points, 
  Player.KOST, 
  Player.Ranked_Win_Percent, 
  Player.Games_Played,
  PlayerMap.MapName, 
  PlayerMap.Win_Percent, 
  PlayerMap.Matches_Played
FROM 
  Player
JOIN 
  PlayerMap ON Player.Username = PlayerMap.Username;
