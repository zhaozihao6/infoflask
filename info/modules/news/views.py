#导入flask和session对象,模板对象和应用上下文对象
from flask import session,render_template, current_app
from . import news_blue
from info.models import User


@news_blue.route('/')

def index():
    """
     项目首页：
     1、页面右上角，检查用户登录状态，如果用户已登录，显示用户信息，否则提供登录注册入口
     2、使用请求上下文对象session从redis中获取user_id
     3、根据user_id查询mysql，获取用户信息
     4、传给模板
     :return:
     """
    user_id = session.get('user_id')#通过session请求上下文对象来获取登陆时设置的user_id
    user = None #当下面查询数据库的情况下,如果发生错误,那么user什么都没有,需要设置个变量暂存
    try:
        user = User.query.filter_by(id=user_id).first()#根据缓存信息来查看用户信息
    except Exception as e:
        current_app.logger.error(e)
        # 定义字典，存储数据 if user_id:user.to_dict() else None
    data = {
        'user_info': user.to_dict() if user else None
    }

    return render_template('news/index.html',data=data)

#logo图标的加载
# 浏览器会默认加载，且需要启动manage文件时清除浏览器缓存并，重新启动浏览器。
@news_blue.route('/favicon.ico')


def favicon():
    #使用应用上下文对象返回logo图标文件
    return current_app.send_static_file('news/favicon.ico')


