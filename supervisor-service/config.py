import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'some secret words')
    ITEMS_PER_PAGE = 10
    DEVICES_MANAGER_PORT = os.environ.get('DEVICES_MANAGER_PORT')
    DATA_WIZARD_PORT = os.environ.get('DATA_WIZARD_PORT')
    SYS_CONTROL_PORT = os.environ.get('SYS_CONTROL_PORT')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:0818@localhost:3306/fabwork'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
