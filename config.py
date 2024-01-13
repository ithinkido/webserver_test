import configparser

config = configparser.ConfigParser()

if config.read('config.ini'):
    print("Config file found. Reading config")
else:
    print("'config.ini' does not exist or could not be read. Creating a new one...")

    # Create 'config.ini' with default values
    # This is only run once on first strt to creat the config file if none id found 
    config['telegram'] = {
        'telegram_token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        'telegram_chatid': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    }
    
    config['tasmota'] = {
        'tasmota_enable': 'false',
        'tasmota_ip': '192.168.1.101'
    }

    config['timelapse'] = {
        'timelapse_enable': 'false',
        'timelapse_auto_start': 'false',
        'timelapse_preview': 'false'
    }

    config['plotter'] = {
        'name': 'My Plotter',
        'port': '/dev/ttyAMA0',
        'device': 'hp7475a',
        'baudrate': '9600',
        'flowControl': 'CTS/RTS'
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

