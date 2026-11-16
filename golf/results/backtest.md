# Golf model backtest

Last 10 finished PGA Tour events, rated only on rounds before each event:
  Rocket Classic                         rank corr +0.44
  Wyndham Championship                   rank corr +0.45
  FedEx St. Jude Championship            rank corr +0.32
  BMW Championship                       rank corr +0.21
  Biltmore Championship Asheville        rank corr +0.41
  Bank of Utah Championship              rank corr +0.41
  Baycurrent Classic                     rank corr +0.31
  Butterfield Bermuda Championship       rank corr +0.41
  VidantaWorld Mexico Open               rank corr +0.35
  World Wide Technology Championship     rank corr +0.41

Avg rank correlation (rating vs finish): +0.37
top20: model error 0.1338 vs no-skill guess 0.1455 (+8% better)
top10: model error 0.0776 vs no-skill guess 0.0822 (+6% better)
cut: model error 0.1900 vs no-skill guess 0.2066 (+8% better)
(Positive % = model knows more than a coin-flip guess. Beating the sportsbooks is a higher bar — that's what CLV tracking tests.)
