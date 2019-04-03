#导入flask类
from flask import Flask
#导入Session类
from flask_session import Session
#导入配置字典
from config import config_dict,Config
#导入flask_sqlalchemy下的SQLAlchemy类
from flask_sqlalchemy import SQLAlchemy
#导入redis,并实例对象
from redis import StrictRedis
#实例StrictRedis对象
redis_store = StrictRedis(host=Config.Config_REDIS_HOST,port=Config.Config_REDIS_PORT,decode_responses=True)
#创建create_app类,设置形参
# 实力sqlalchemy对象
db = SQLAlchemy()
def create_app(schema_name):
    app = Flask(__name__)
    #config_dict字典中的key值映射value类,而类又继承与Config类
    app.config.from_object(config_dict[schema_name])
    # 使用Session类
    Session(app)
    #建立数据库和app的关联
    db.init_app(app)
    #导入蓝图对象并注册蓝图，注意这个要写在Session(app)下面，避免循环导包
    from info.modules.news import news_blue
    #注册蓝图
    app.register_blueprint(news_blue)
    # 这个方法最终是要获取app的，需要返回app
    #导入蓝图对象并注册蓝图
    from info.modules.passport import passport_blue
    # 注册蓝图
    app.register_blueprint(passport_blue)
    return app
