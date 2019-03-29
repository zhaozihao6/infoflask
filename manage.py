#导入flask和session对象
from flask import Flask,session
#导入Session类来指定数据库的链接等操作
from flask_session import Session
from config import Config

#实例app对象
app = Flask(__name__)
#把配置文件添加到config中
app.config.from_object(Config)
# 使用Session类
Session(app)
@app.route('/')
def hello():
    #定义sessionkey值
    session['name']='zhaozan'
    return 'hello,world'


if __name__ == '__main__':
    app.run()