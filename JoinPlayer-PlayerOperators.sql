SELECT 
  Player.Username, 
  Player.KD_Ratio AS PlayerKD, 
  PlayerOperator.OpName, 
  PlayerOperator.KD_Ratio AS OperatorKD, 
  PlayerOperator.Role, 
  PlayerOperator.KOST, 
  PlayerOperator.Round_Win_Percent, 
  PlayerOperator.Rounds_Played
FROM 
  Player
JOIN 
  PlayerOperator ON Player.Username = PlayerOperator.Username;
