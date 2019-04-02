#导入flask和session对象,模板对象和应用上下文对象
from flask import session,render_template, current_app
from . import news_blue


@news_blue.route('/')

def hello():
    #定义sessionkey值
    session['name']='zhaozan'
    return render_template('news/index.html')

#logo图标的加载
# 浏览器会默认加载，且需要启动manage文件时清除浏览器缓存并，重新启动浏览器。
@news_blue.route('/favicon.ico')

def favicon():
    #使用应用上下文对象返回logo图标文件
    return current_app.send_static_file('news/favicon.ico')


