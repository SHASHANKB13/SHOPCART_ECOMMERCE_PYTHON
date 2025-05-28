import util.configFile as conf

config = conf.init()

CONTENT_TYPE = "application/json"

SECRET_KEY = "cherry"

# API PORT configurations
API_HOST = config.get('SERVER', 'host')
API_PORT = config.get('SERVER', 'port')
DEBUG = config.get('SERVER', 'debug')

# DATABASE CONFIGURATIONS
DB_USER = config.get('DATABASE', 'db_user')
DB_PASSWORD = config.get('DATABASE', 'db_password')
DB_HOST = config.get('DATABASE', 'db_host')
DB_PORT = config.get('DATABASE', 'db_port')
DB_NAME = config.get('DATABASE', 'db_database')