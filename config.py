#导入redis数据库
from redis import StrictRedis
class Config:
    #设置secret key 密钥值,通过os.urandom和base64.b64encode（）来实现
    SECRET_KEY = '0FkqKfUFJcBQbfveExNUdbuAILmAxm6WXyWSm7uCsuzL48sRArlIR+k6b8GI'
        #设置链接数据库名称,
    SESSION_TYPE = 'redis'
        #实例strictredis方法，并传入链接数据库的ip默认端口为6379
    SESSION_REDIS = StrictRedis(host='127.0.0.1')
        #设置签证
    SESSION_USE_SIGNER = True
        #设置数据库的过期时间值
    PERMANENT_SESSION_LIFETIME = 86400
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/info'
        # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = True
        #设置debug模式为空
    DEBUG = None

#定义开发模式下的DEBUG
class DevelopmentConfig(Config):
    DEBUG = True

# 定义生产情况下的debug
class ProductionConfig(Config):
    DEBUG = False

#定义字典映射不同配置下的类
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}