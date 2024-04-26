SELECT 
  Operator.OpName, 
  PlayerOperator.Username, 
  PlayerOperator.KD_Ratio, 
  PlayerOperator.Role, 
  PlayerOperator.KOST, 
  PlayerOperator.Round_Win_Percent, 
  PlayerOperator.Rounds_Played
FROM 
  Operator
JOIN 
  PlayerOperator ON Operator.OpName = PlayerOperator.OpName;
