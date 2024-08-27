def send_email():
    sender_email = 
    receiver_email = 
    if contact:
        receiver_email = []
    password = 
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    SUBJECT = script_name
    message = 'Subject: {}\n\n{}'.format(SUBJECT, global_message)

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def handle_message(message, append_global=True, print_mess=not production, raise_error=False):
    global global_message, expected_error
    if append_global:
        global_message += message
    if print_mess:
        print(message)
    if raise_error:
        raise ValueError(message)

def sleep_func(wake_time):
    wake = pytz.timezone("US/Pacific").localize(datetime.strptime(wake_time,"%H:%M:%S")).time()
    start = datetime.now(pytz.timezone("US/Pacific")).time()
    sleep_time = (datetime.combine(date.min, wake) - datetime.combine(date.min, start)).seconds
    handle_message(f'\n\nEntering sleep for {sleep_time//3600} hr {int(sleep_time/3600%1*60)} min \
                   {int(sleep_time/3600%1*60%1*60-2)} sec at {datetime.now(pytz.timezone("US/Pacific"))} \
                       PST to {wake_time} PST\n==============================')
    if production:
        time.sleep(sleep_time)

def auth_tda():
    token_path = 'token.json'
    api_key =
    redirect_uri = 'https://127.0.0.1'
    try:
        c = auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        handle_message('\n\nToken path not found, initiating chromedriver creation')
        from selenium import webdriver
        with webdriver.Chrome(executable_path=) as driver:
            c = auth.client_from_login_flow(
                driver, api_key, redirect_uri, token_path)
        handle_message('\nCode ran fine (please verify)')
    handle_message('\n\nAccount authorized')
    return c

def check_delist(ticker): # TDA
    handle_message(f'\n\ncheck_delist({ticker}) running at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    delisted = c.get_quote(ticker).json()[ticker]['securityStatus'] == 'Halted'
    handle_message(f'\ncheck_delist({ticker}) (result: {delisted}) finished at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')            
    return delisted

def get_last_price(ticker): # TDA
    handle_message(f'\n\nget_last_price({ticker}) running at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    price = c.get_quote(ticker).json()[ticker]['lastPrice']
    handle_message(f'\nget_last_price({ticker}) (result: {price}) finished at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    return price

def buy_market(ticker, qty):
    handle_message(f'\n\nbuy_market({ticker}, {qty}) running at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    OB = OrderBuilder() # this just becomes a dictionary
    OB.add_equity_leg(EquityInstruction.BUY, ticker, qty)
    OB.set_order_type(OrderType.MARKET)
    OB.set_session(Session.NORMAL)
    OB.set_duration(Duration.DAY)
    OB.set_order_strategy_type(OrderStrategyType.SINGLE)
    c.place_order(account_id, OB.build())
    handle_message(f'\nbuy_market({ticker}, {qty}) finished at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')

def sell_market(ticker, qty):
    handle_message(f'\n\nsell_market({ticker}, {qty}) running at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    OB = OrderBuilder() # this just becomes a dictionary
    OB.add_equity_leg(EquityInstruction.SELL, ticker, qty)
    OB.set_order_type(OrderType.MARKET)
    OB.set_session(Session.NORMAL)
    OB.set_duration(Duration.DAY)
    OB.set_order_strategy_type(OrderStrategyType.SINGLE)
    c.place_order(account_id, OB.build())
    handle_message(f'\nsell_market({ticker}, {qty}) finished at \
                   {datetime.now(pytz.timezone("US/Pacific")).time()} PST')
    
