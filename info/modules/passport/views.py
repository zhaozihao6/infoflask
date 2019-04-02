from info.constants import IMAGE_CODE_REDIS_EXPIRES
from . import passport_blue
#导入captcha扩展,实现图片验证码
from info.utils.captcha.captcha import captcha
from flask import request,jsonify,current_app,make_response
from info.utils.response_code import RET
from info import redis_store

@passport_blue.route('/image_code')

def generate_image_code():

    """
    1:获取uuid（全局唯一标识符,这里是有前端实现：代表不易重复,因为是要存入redis中当key值来使用的不
    能重复）通过查询字符串的形式来传入进来,request.args.get()
    2：判断uuid是否存在，如果不存在return
    3：使用captcha生成图片验证码  name text image
    4：再次实例化redis对象来进行redis存储text操作
    5：返回图片验证码

    """
    #获取uuid
    image_code_id = request.args.get("image_code_id")
    #判断uuid是否传入,没传直接return
    if not image_code_id:
        # 前后端交互使用jsonfy,并自定义返回错误类型
        return jsonify(erron = RET.PARAMERR,errmsg = '参数缺失')
    #调用该函数可以返回三个内容 name,text,image
    name,text,image = captcha.generate_captcha()
    
    #数据库操作需要自己手动捕捉异常
    try:
        # 调用redis实例对象来存储text
        #setex这个函数可以设置过期时间单位为（秒）,
        redis_store.setex('Image_Code'+image_code_id,IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        #使用应用上下文，current_app来进行项目日志记错。
        current_app.logger.error(e)
        return jsonify(erron = RET.DBERR,errmsg = '保存数据错误')
    else:
        #返回前端图片,并修改返回类型，make_response
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response

