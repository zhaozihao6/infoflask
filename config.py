#导入redis数据库


from redis import StrictRedis
# 设置日志的记录等级
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)




class Config:
    #设置secret key 密钥值,通过os.urandom和base64.b64encode（）来实现
    SECRET_KEY = '0FkqKfUFJcBQbfveExNUdbuAILmAxm6WXyWSm7uCsuzL48sRArlIR+k6b8GI'
        #设置链接数据库名称,
    SESSION_TYPE = 'redis'
    Config_REDIS_HOST = '127.0.0.1'
    Config_REDIS_PORT = 6379
        #实例strictredis方法，并传入链接数据库的ip默认端口为6379
    SESSION_REDIS = StrictRedis(host=Config_REDIS_HOST,port=Config_REDIS_PORT)
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