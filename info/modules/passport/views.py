from info.constants import IMAGE_CODE_REDIS_EXPIRES
from . import passport_blue
#导入captcha扩展,实现图片验证码
from info.utils.captcha.captcha import captcha
from flask import request,jsonify,current_app,make_response
from info.utils.response_code import RET
from info import redis_store
import re,random
from info import constants
from info.libs.yuntongxun.sms import ccp

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
    print(image_code_id)
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
        redis_store.setex('Image_Code_'+image_code_id,IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        #使用应用上下文，current_app来进行项目日志记错。
        current_app.logger.error(e)
        return jsonify(erron = RET.DBERR,errmsg = '保存数据错误')
    else:
        #返回前端图片,并修改返回类型，make_response
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response


#发送短信验证码

@passport_blue.route('/sms_code',methods = ['POST'])
def send_sms_code():
    # 发送短信验证码流程
    """
    发送短信
    获取参数---检查参数---业务处理---返回结果
    1、获取参数，mobile(用户的手机号)，image_code(用户输入的图片验证码),image_code_id(UUID)
    2、检查参数的完整性
    3、检查手机号格式，正则
    4、尝试从redis中获取真实的图片验证码
    5、判断获取结果，如果不存在图片验证码已经过期
    6、需要删除redis中存储的图片验证码,图片验证码只能比较一次，本质是只能对redis数据库get一次。
    7、比较图片验证码是否正确
    8、生成短信验证码，六位数
    9、存储在redis数据库中
    10、调用云通讯，发送短信
    11、保存发送结果，判断发送是否成功
    12、返回结果

    :return:
    """
    # 1、获取参数，mobile(用户的手机号)，image_code(用户输入的图片验证码), image_code_id(UUID)
    mobile = request.args.get("mobile")
    image_code = request.args.get('image_code')
    image_code_id = request.args.get("image_code_id")
    # 2、检查参数的完整性
    # 方法1：if not mobile and image_code and image_code_id:
    #判断方法2：
    if not all([mobile,image_code, image_code_id]):
        return jsonify(erron=RET.PARAMERR,errmsg='参数不完整')
    # 3、检查手机号格式，正则
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(erron=RET.PARAMERR,errmsg='手机号格式错误')
    #尝试从redis中查询图片验证码
    try:
        real_image_code = redis_store.get('Image_Code_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron = RET.DBERR,errmsg = '获取数据失败')
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg='图片验证码已过期')
    # 删除redis中存储的图片验证码，因为图片验证码只能get一次，只能比较一次,留着也没用
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    #比较图片验证码的数据是否一直,lower（）函数可以把字符串转化成小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(erron=RET.DATAERR,errmsg='图片验证码不一致')
    #生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    # 存储在redis中，key可以拼接手机号
    try:
        redis_store.setex('SMSCode_'+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    #使用云通讯发送短信验证码
    try:
        result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
    #判断短信是否发送成功
    if result == 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')