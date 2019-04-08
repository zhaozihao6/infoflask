#导入flask和session对象,模板对象和应用上下文对象
from flask import session, render_template, current_app, jsonify
from . import news_blue
from info.models import User, Category, News
from info.utils.response_code import RET
from info import constants


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

    #查询数据库获取分类信息
    try:
        #数据库存了6个数据对象的引用[<Category 1>, <Category 2>, <Category 3>, <Category 4>, <Category 5>, <Category 6>]
        categoryies = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg='查询新闻分类数据失败')
    #判断新闻分类是否有数据
    if not categoryies:
        return jsonify(erron=RET.NODATA,errmsg='无新闻分类数据')
    #定义列表来存储循环出来的字典值[{'name': '最新', 'id': 1}, {'name': '股市', 'id': 2}, {'name': '债市', 'id': 3},
    #  {'name': '商品', 'id': 4}, {'name': '外汇', 'id': 5}, {'name': '公司', 'id': 6}]
    category_list = []
    #遍历对象的引用
    for category in categoryies:

        category_list.append(category.to_dict())



    #实现新闻排序
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='查询数据库失败')
    #判断查询数据是否为空
    if not news_list:
        return jsonify(erron=RET.DATAERR, errmsg='无新闻点击排行数据')
    news_click_list = []
    #循环遍历news_list对象
    for news in news_list:
        news_click_list.append(news.to_dict())


    # 定义字典，存储数据 if user_id:user.to_dict() else None
    data = {
        'user_info': user.to_dict() if user else None,
        'category_list': category_list,
        'news_click_list':news_click_list
    }

    return render_template('news/index.html', data=data)

#logo图标的加载
# 浏览器会默认加载，且需要启动manage文件时清除浏览器缓存并，重新启动浏览器。
@news_blue.route('/favicon.ico')


def favicon():
    #使用应用上下文对象返回logo图标文件
    return current_app.send_static_file('news/favicon.ico')

#新闻分类下的新闻数据加载实现