#导入flask和session对象
from flask import session
from . import news_blue
@news_blue.route('/')
def hello():
    #定义sessionkey值
    session['name']='zhaozan'
    return 'hello,world'
