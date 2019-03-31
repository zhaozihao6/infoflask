from flask import Flask
from flask_session import Session
from config import Config,config_dict
#创建create_app类,设置形参
def create_app(schema_name):
    app = Flask(__name__)
    #config_dict字典中的key值映射value类,而类又继承与Config类
    app.config.from_object(config_dict[schema_name])
    # 使用Session类
    Session(app)
    #导入蓝图对象并注册蓝图，注意这个要写在Session(app)下面，避免循环导包
    from info.modules.news import news_blue
    #注册蓝图
    app.register_blueprint(news_blue)
    # 这个方法最终是要获取app的，需要返回app
    return app
