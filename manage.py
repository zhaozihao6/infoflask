#导入flask和session对象
from flask import Flask,session
#导入Session类来指定数据库的链接等操作
from flask_session import Session
#导入redis数据库
from redis import StrictRedis

#实例app对象
app = Flask(__name__)
#设置secret key 密钥值,通过os.urandom和base64.b64encode（）来实现
app.config['SECRET_KEY'] = '0FkqKfUFJcBQbfveExNUdbuAILmAxm6WXyWSm7uCsuzL48sRArlIR+k6b8GI'
#设置链接数据库名称,
app.config['SESSION_TYPE'] = 'redis'
#实例strictredis方法，并传入链接数据库的ip默认端口为6379
app.config['SESSION_REDIS'] = StrictRedis(host='127.0.0.1')
#设置签证
app.config['SESSION_USE_SIGNER'] = True
#设置数据库的过期时间值
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
# 使用Session类
Session(app)
@app.route('/')
def hello():
    #定义sessionkey值
    session['name']='zhaozan'
    return 'hello,world'


if __name__ == '__main__':
    app.run()