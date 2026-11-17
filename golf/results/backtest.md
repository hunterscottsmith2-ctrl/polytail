# Golf model backtest

Last 39 finished PGA Tour events, rated only on rounds before each event:
  WM Phoenix Open                        rank corr +0.48
  AT&T Pebble Beach Pro-Am               rank corr +0.42
  The Genesis Invitational               rank corr +0.25
  Cognizant Classic in The Palm Beaches  rank corr +0.41
  Arnold Palmer Invitational pres. by Ma rank corr +0.16
  Puerto Rico Open                       rank corr +0.31
  THE PLAYERS Championship               rank corr +0.41
  Valspar Championship                   rank corr +0.26
  Texas Children's Houston Open          rank corr +0.33
  Valero Texas Open                      rank corr +0.46
  Masters Tournament                     rank corr +0.64
  RBC Heritage                           rank corr +0.37
  Cadillac Championship                  rank corr +0.35
  Truist Championship                    rank corr +0.11
  ONEflight Myrtle Beach Classic         rank corr +0.37
  PGA Championship                       rank corr +0.55
  THE CJ CUP Byron Nelson                rank corr +0.48
  Charles Schwab Challenge               rank corr +0.47
  the Memorial Tournament pres. by Workd rank corr +0.33
  RBC Canadian Open                      rank corr +0.32
  U.S. Open                              rank corr +0.50
  Travelers Championship                 rank corr +0.38
  John Deere Classic                     rank corr +0.34
  Genesis Scottish Open                  rank corr +0.37
  ISCO Championship                      rank corr +0.46
  The Open                               rank corr +0.50
  Corales Puntacana Championship         rank corr +0.37
  3M Open                                rank corr +0.46
  Rocket Classic                         rank corr +0.48
  Wyndham Championship                   rank corr +0.45
  FedEx St. Jude Championship            rank corr +0.33
  BMW Championship                       rank corr +0.24
  Biltmore Championship Asheville        rank corr +0.44
  Bank of Utah Championship              rank corr +0.40
  Baycurrent Classic                     rank corr +0.29
  Butterfield Bermuda Championship       rank corr +0.45
  VidantaWorld Mexico Open               rank corr +0.38
  World Wide Technology Championship     rank corr +0.41
  Austin Championship pres. by Complianc rank corr +0.25

Avg rank correlation (rating vs finish): +0.38
top20: model error 0.1271 vs no-skill guess 0.1397 (+9% better)
top10: model error 0.0724 vs no-skill guess 0.0780 (+7% better)
cut: model error 0.2194 vs no-skill guess 0.2476 (+11% better)

Top-20 calibration (what the model said vs what happened):
  said 5% -> happened 5%  (1399 player-events)
  said 15% -> happened 14%  (1520 player-events)
  said 24% -> happened 25%  (997 player-events)
  said 34% -> happened 36%  (410 player-events)
  said 44% -> happened 51%  (131 player-events)
  said 62% -> happened 53%  (70 player-events)
(Positive % = model knows more than a coin-flip guess. Beating the sportsbooks is a higher bar — that's what CLV tracking tests.)
