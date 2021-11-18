# Trady


### Basics
This is a framework for developing trading algorithms on [Binance](https://www.binance.com/), using its api via [python-binance](https://python-binance.readthedocs.io/en/latest/) library.

### Config
To configure the framework, fill in the `config.ini` file. Specifically the Binance api keys have to be acquired and the database established (using the [sqlalchemy symbol](https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_connecting_to_database.htm)).

### Strategies and Symbols
Strategies are defined in `lib.strategies` as packages. Most strategies will be parametrized by the trading symbols. Thus every strategy has to be initialized by its wrapping function. The symbols that can be traded are defined in `Symbol` enum inside `lib.enums`.

### Trading
To trade a strategy (that is defined in `lib.strategies`), one only has to run `python trady.py trade <strategy> <symbol_1> ... <symbol_n> -ti <time_interval>`. This means that the chosen strategy will trade the given symbols and be called every `<time_interval>` minutes.

### Tests
Repo implements two ways to test a given strategy.

- **Backtesting**: For strategies that depend solely on the previous candle data for featured symbols. Backtest by running  `python trady.py backtest <strategy> <symbol_1> ... <symbol_n> -sd <start date> -ed <end date>` on cli. Here the database must contain candles in between`<start date>` and `<end date>` for every symbol `<symbol_i>`  (see Seeding).
- **Livetesting**: For strategies that also depend on some outside factors (eg. scraping the web for crypto news). Livetest by running `python trady.py livetest <strategy> <symbol_1> ... <symbol_n>` (comming soon).

### Seeding
When backtesting, it is required to have candles saved in the database. You can load them by running `python trady.py seed <symbol_1> ... <symbol_n> -sd <start date> -ed <end date>`, where `-ed` is optional, defaulting on the current day's midnight. 

### Candle Information
If you wish to check timeframe during which candles are obtained in the database for specific symbols, you can use `python trady.py info <symbol_1> ... <symbol_n>`.

### Notes

When backtesting a strategy make sure that it does not acquire earlier candles than those in the database (if a strategy's maximum lookback is eg. 4 days and the backtesting starts at eg. `-sd 2021 10 10`, you have to have candles in the database from `2021 10 6` on).

### Examples

```bash
python trady.py seed ADAUSDT -sd 2021 9 28 -ed 2021 10 10
python trady.py backtest meanRevision ADAUSDT -sd 2021 10 1 -ed 2021 10 10
python trady.py trade meanRevision ADAUSDT
```

