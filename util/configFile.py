import configparser

def init():
    CONFIG = r'/Users/shashank/Documents/python_projects/shopkart_be/data.properties'
    config = configparser.ConfigParser()
    config.read(CONFIG)
    return config