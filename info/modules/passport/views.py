#导入时间模块
from datetime import datetime
#导入常量
from info.constants import IMAGE_CODE_REDIS_EXPIRES
#导入蓝图对象
from . import passport_blue
#导入captcha扩展,实现图片验证码
from info.utils.captcha.captcha import captcha
# 导入flask内置的request请求上下文对象，current_app应用上下文
from flask import request,jsonify,current_app,make_response,session
#导入自定义错误信息
from info.utils.response_code import RET
#导入redis实例对象
from info import redis_store
#导入python中的正则模块和随机数模块
import re,random
#导入常量
from info import constants
#导入第三方云通讯sms对象
from info.libs.yuntongxun.sms import CCP
#导入模型类,使用模型类对象进行查库操作
from info.models import User
#导入数据库实例对象
from info import db

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

@passport_blue.route('/sms_code', methods=['POST'])
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
    mobile = request.json.get("mobile")
    image_code = request.json.get('image_code')
    image_code_id = request.json.get("image_code_id")
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
        #利用应用上下文对象,来记录错误日志信息
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg='获取数据失败')
    #判断验证码是否为空
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg='图片验证码已过期')
    # 删除redis中存储的图片验证码，因为图片验证码只能get一次，只能比较一次,留着也没用
    #用户只能输入一次验证码，如果输入错误，从新生成验证码输入
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    #比较图片验证码的数据是否一直,lower（）函数可以把大写字母转化成小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(erron=RET.DATAERR,errmsg='图片验证码不一致')

    #判断手机号是否注册(不允许一个手机号注册多次)：
    #通过查询mysql数据库查询手机号是否存在
    try:
        #查询数据库语句
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg='查询用户数据失败')
    #判断数据是否真实存在
    if user is not None:
        return jsonify(erron=RET.DATAEXIST,errmsg='手机号码已被注册')

    #生成短信验证码，'%06d' % 因为从0开始，有可能会出现5位，'%06d' % 这个可以在前多加一位
    sms_code = '%06d' % random.randint(0, 999999)
    # 存储在redis中，key可以拼接手机号来实现key唯一
    try:
        redis_store.setex('SMSCode_'+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST,errmsg='手机号已经注册')
    #使用云通讯发送短信验证码，send_template_sms(接收人手机号,[内容（下面代码有验证码/过期时间）],1)
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile,[sms_code,
                                            constants.SMS_CODE_REDIS_EXPIRES/60],1)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
    #判断短信是否发送成功，云通讯在发送时会接收一个响应信息0为发送成功-1为失败，后端需要根据响应来判断是
    #否发送成功
    if result == 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')



@passport_blue.route('/register',methods=['POST'])
def register():
    '''
    用户注册
    获取参数---检查参数---业务处理---返回结果
    1、获取前端ajax发送的post请求的三个参数，mobile，sms_code,password
    2、检查参数的完整性
    3、检查手机号的格式
    用户是否注册？
    4、尝试从redis数据库中获取真实的短信验证码
    5、判断获取结果是否过期
    6、比较短信验证码是否正确，因为短信验证码可以比较多次，图片验证码只能比较一次
    7、删除redis数据库中存储的短信验证码
    用户是否注册？
    8、构造模型类对象,准备保存用户信息
    user = User()
    user.password = password
    9、提交数据到mysql数据库中，如果发生异常，需要进行回滚
    10、缓存用户信息，使用session对象到redis数据库中；
    11、返回结果

    :return:
    '''
    # 1、获取前端ajax发送的post请求的三个参数，mobile，sms_code, password
    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    password = request.json.get('password')
    # 2、检查参数的完整性
    if not all([mobile, sms_code, password]):
        return jsonify(erron=RET.PARAMERR,errmsg='参数不完整')
    # 3、检查手机号的格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(erron=RET.PARAMERR,errmsg='手机号格式错误')
    #查询数据库,判断手机号是否注册过
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
       current_app.logger.error(e)
       return jsonify(erron=RET.DBERR, errmsg='查询手机号失败')
    if user is not None:
        return jsonify(erron=RET.DATAEXIST, errmsg='手机号码已被注册')
    # 4、尝试从redis数据库中获取真实的短信验证码
    try:
        real_sms_code=redis_store.get('SMSCode_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='获取数据失败')
    # 5、判断获取结果是否过期
    if real_sms_code is None:
        return jsonify(erron=RET.NODATA, errmsg='短信验证码过期')
    # 6、比较短信验证码是否正确，因为短信验证码可以比较多次，图片验证码只能比较一次
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR,errmsg='短信验证码不一致')
    # 7、删除redis数据库中存储的短信验证码
    try:
        redis_store.delete('SMSCode_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 8、用户是否注册？
        # 判断手机号是否注册(不允许一个手机号注册多次)：
        # 通过查询mysql数据库查询手机号是否存在
    try:
        # 查询数据库语句
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='查询用户数据失败')
        # 判断数据是否真实存在
    if user is not None:
        return jsonify(erron=RET.DATAEXIST, errmsg='手机号码已被注册')
    # 9、构造模型类对象, 准备保存用户信息
    user = User()
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile
    # 9、提交数据到mysql数据库中，如果发生异常，需要进行回滚
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 保存数据如果失败，进行回滚
        db.session.rollback()
        # 缓存用户信息
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')



#实现用户登陆
@passport_blue.route('/login',methods=['POST'])

def login():

    """
      用户登录
      1、获取参数，post请求，json数据，mobile，password
      2、检查参数的完整性
      3、检查手机号的格式
      4、根据手机号查询mysql，确认用户已注册
      5、判断查询结果
      6、判断密码是否正确
      7、保存用户登录时间，当前时间
      8、提交数据到mysql数据库
      9、缓存用户信息，注意：登录可以执行多次，用户有可能修改昵称，也有可能不改。
      session['nick_name'] = user.nick_name
      10、返回结果

      :return:
      """


    # 1、获取参数，post请求，json数据，mobile，password
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 2、检查参数的完整性
    if not all([mobile,password]):
        return jsonify(erron=RET.PARAMERR,erromsg='参数信息不完整')
    # 3、检查手机号的格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(erron=RET.PARAMERR,errmsg='手机号格式错误')
    # 4、根据手机号查询mysql，确认用户已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger(e)
        return jsonify(erron=RET.DBERR, errmsg='查询用户数据失败')
    # 4、根据手机号查询mysql，确认用户已注册
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 保存用户登录时间，当前时间
    user.last_login = datetime.now()
    #提交数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        #保存数据失败进行回滚操作
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    #session缓存
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    return jsonify(errno=RET.OK,errmsg='OK')

