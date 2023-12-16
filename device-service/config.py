import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """
    Base configuration class with common configurations.

    :param SECRET_KEY: Key for encrypting session data.
    :param ITEMS_PER_PAGE: Default number of items per page for pagination.
    :param DEVICES_MANAGER_PORT: Port for the device manager service.
    :param DATA_WIZARD_PORT: Port for the data wizard service.
    :param SYS_CONTROL_PORT: Port for the system control service.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'some secret words')
    ITEMS_PER_PAGE = 10
    DEVICES_MANAGER_PORT = os.environ.get('DEVICES_MANAGER_PORT')
    DATA_DISPATCHER_PORT = os.environ.get('DATA_WIZARD_PORT')
    SYS_CONTROL_PORT = os.environ.get('SYS_CONTROL_PORT')




class DevelopmentConfig(BaseConfig):
    """
    Configuration settings specific to the development environment.

    :param DEBUG: Indicates whether debugging should be enabled.
    :param SQLALCHEMY_DATABASE_URI: URI for the development database.
    """
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:0818@localhost:3306/fabwork'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    # raw_sql_config = {
    #     'user': ,
    #     'password': 'password',
    #     'host': 'localhost',
    #     'database': 'db',
    #     'pool_name': 'mypool',
    #     'pool_size': 5
    # }

class TestingConfig(BaseConfig):
    """
    Configuration settings specific to the testing environment.

    :param TESTING: Indicates whether the app is in testing mode.
    :param SQLALCHEMY_DATABASE_URI: URI for the testing database.
    :param WTF_CSRF_ENABLED: Indicates if CSRF protection should be enabled.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """
    Configuration settings specific to the production environment.

    :param SQLALCHEMY_DATABASE_URI: URI for the production database.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
