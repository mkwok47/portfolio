# Quant Portfolio
Samples of reflections, code, & findings from 2000+ hours of self-taught algorithmic trading 2019-present as a hobby. Portfolio focus is development and infrastructure rather than meaningful research findings.

1. My Approach:
    1. [overview.txt](https://github.com/mkwok47/quant_portfolio/blob/main/01_my_approach/overview.txt)
    2. [pillars_of_truth.txt](https://github.com/mkwok47/quant_portfolio/blob/main/01_my_approach/pillars_of_truth.txt)
2. Research:
    1. [utils/alpaca_table2.py](https://github.com/mkwok47/quant_portfolio/blob/main/02_research/utils/alpaca_table2.py): create and maintain stock price datasets in local SQL database via sqlite3
    2. [utils/minute_functions.py](https://github.com/mkwok47/quant_portfolio/blob/main/02_research/utils/minute_functions.py): functions that assist with researching and backtesting at the minutely-level
    3. [ucsb_competition_paper.pdf](https://github.com/mkwok47/quant_portfolio/blob/main/02_research/ucsb_competition_paper.pdf): in-depth analysis of a profitable theoretical trading strategy I made
    4. [selling_option_prem.ipynb](https://github.com/mkwok47/quant_portfolio/blob/main/02_research/selling_option_prem.ipynb): analyze probabilities of ITM/OTM option expiration and associated premiums
    5. [top_gainers_effect.ipynb](https://github.com/mkwok47/quant_portfolio/blob/main/02_research/top_gainers_effect.ipynb): analyze the following interday gap and intraday change for top gainers
3. Deployment:
    1. [utils/production_functions.py](https://github.com/mkwok47/quant_portfolio/blob/main/03_deployment/utils/production_functions.py): functions that assist with production, including order-execution
    2. [production_script.py](https://github.com/mkwok47/quant_portfolio/blob/main/03_deployment/production_script.py): a generalized production script I use to automate trading strategies

Tools & Technologies:
1. Python/Pandas, SQL, Linux Command Line, Git
2. Alpaca Markets and TD Ameritrade APIs for data and brokerage
3. Amazon Web Services cloud EC2 instance, crontab automation
