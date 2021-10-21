# Trady


### Basics
This is a framework for writing trading algorithms on Binance using [python-binance](https://python-binance.readthedocs.io/en/latest/). 

### Config
To configure the framework, the `config.ini` file has to be filled in. Specifically the Binance api keys have to be acquired and the database established (using the [Sqlalchemy symbol](https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_connecting_to_database.htm)).

### Strategies
Strategies are defined in `lib.strategies` as packages. Some strategies trade a specific symbol and can therefore be initialized by a wrapper function.

### Tests
Repo implements two ways to test a given strategy.

- **Backtesting**: For strategies that depend solely on the previous candle data for featured symbols. Backtest by running `python <strategy> <symbol> -sd <start date> -ed <end date>` on cli. Here the database must contain candles in between`<start date>` and `<end date>` for `<symbol>`  (see Seeding). Note also that `<symbol>` is optional and can be ommited if `<strategy>` does not require it.
- **Livetesting**: For strategies that also depend on some outside factors (eg. scraping the web for crypto news). Livetest by running `python <strategy> <symbol>` (comming soon).

### Seeding
When backtesting, it is required to have candles saved in the database. You can load them by running `python seed.py <symbol> -sd <start date> -ed <end date>`, where `-ed` is optional, defaulting on the current day's midnight. 

### Notes

When backtesting a strategy make sure that it does not acquire earlier candles than those in the database (if a strategy's maximum lookback is eg. 4 days and the backtesting starts at eg. `-sd 2021 10 10`, you have to have candles in the database from `2021 10 6` on).

### Examples

```powershell
python seed.py ADAUSDT -sd 2021 9 28 -ed 2021 10 10
python backtest.py meanRevision ADAUSDT -sd 2021 10 1 -ed 2021 10 10
```