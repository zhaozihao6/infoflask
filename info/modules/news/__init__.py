#导入蓝图
from flask import Blueprint

#实例蓝图对象
news_blue = Blueprint('news_blue', __name__ )

#把拆分出去的蓝图文件导入进来，告诉蓝图一声
from . import views