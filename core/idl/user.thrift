# thrift definition

##################################################
# include
##################################################
include "common.thrift"


##################################################
# typedef
##################################################
typedef common.Payload Payload
typedef common.Result Result


##################################################
# service
##################################################

# 授权
service AuthService {
    # [ docs ]
    # 验证用户授权Token
    #
    # [ payload ]
    # device : 设备信息
    # data : {
    #     id : 用户ID,
    #     token : 授权Token
    # }
    #
    # [ result ]
    # msg : '校验成功'
    # data : {
    #     permissions : [ 权限列表 ],
    #     expire : 过期时间戳,
    #     signature : 签名
    # }
    Result validate_token(1:Payload payload);

    # [ docs ]
    # 创建用户授权Token，用于登录场景
    #
    # [ payload ]
    # device : 设备信息
    # data : {
    #     type : 登录方式（account/weixin/qq）,
    #     identifier : 唯一标识（手机/邮箱/微信OpenID/ＱＱOpenID）,
    #     password : 登录密码
    # }
    #
    # [ result ]
    # data : {
    #     user : { id : 用户ID, token : 授权Token }
    # }
    Result create_token(1:Payload payload);

    # [ docs ]
    # 销毁用户授权
    #
    # [ payload ]
    # auth : 授权信息
    # device : 设备信息
    # data : { }
    #
    # [ result ]
    # msg : 注销成功
    Result destroy_token(1:Payload payload);

    # [ docs ]
    # 管理员获取用户授权
    #
    # [ payload ]
    # auth : 授权信息
    # device : 设备信息
    # data: {
    #     user : 用户ID，
    # }
    #
    # [ result ]
    # data: {
    #     user : { id : 用户ID, token : 授权Token }
    # }
    Result admin_access(1:Payload payload);

    # [ docs ]
    # OTP获取用户授权
    #
    # [ payload ]
    # device : 设备信息
    # data: {
    #     mode : 模式（cellphone/email/weixin/qq）,
    #     cellphone : { identifier : 手机号码, validation : 验证信息 },
    #     email : { identifier : 邮箱, validation : 验证信息 },
    #     weixin : { openid : 微信OpenID, unionid : 微信UnionID, token : 授权Token },
    #     qq : { openid : ＱＱ OpenID, token : 授权Token },
    # }
    #
    # [ result ]
    # data: {
    #     user : { id : 用户ID, token : 授权Token }
    # }
    Result otp_access(1:Payload payload);

    # [ docs ]
    # 创建OTP信息
    #
    # [ payload ]
    # data : {
    #     scene : 验证场景,
    #     mode : 模式（cellphone/email）,
    #     identifier : 手机 / 邮箱,
    # }
    #
    # [ result ]
    # data : {
    #     validation : 验证信息
    # }
    Result create_otp(1:Payload payload);

    # [ docs ]
    # 校验OTP信息
    #
    # [ payload ]
    # data : {
    #     scene : 验证场景,
    #     mode : 模式（cellphone/email）,
    #     identifier : 手机 / 邮箱,
    #     validation : 验证信息
    # }
    #
    # [ result ]
    # msg : 校验成功
    Result check_otp(1:Payload payload);
}

# 用户资料
service ProfileService {
    # [ docs ]
    # 搜索用户
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     keyword : 搜索关键字,
    #     page : { size : 页面大小, no : 页码编号, base : {  id : 基准ID } }
    # }
    #
    # [ result ]
    # data : {
    #     users : [ 用户列表 ]
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 根据唯一标识获取用户基本信息
    #
    # [ payload ]
    # data : {
    #     mode : 模式（cellphone-手机, email-邮箱, weixin-微信, qq-ＱＱ）,
    #     identifier : 唯一标识
    # }
    #
    # [ result ]
    # data : {
    #     user : { 用户信息 }
    # }
    Result with_identifier(1:Payload payload);

    # [ docs ]
    # 获取用户基本信息
    #
    # [ payload ]
    # data : {
    #     user : 用户ID
    # }
    #
    # [ result ]
    # data : {
    #     user : { 用户信息 }
    # }
    Result get_digest(1:Payload payload);

    # [ docs ]
    # 获取用户详细信息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     user : 用户ID
    # }
    #
    # [ result ]
    # data : {
    #     user : { 用户信息 }
    # }
    Result get_detail(1:Payload payload);

    # [ docs ]
    # 获取多个用户基本信息
    #
    # [ payload ]
    # data : {
    #     users : [ 用户ID, ... ]
    # }
    #
    # [ result ]
    # data : {
    #     users : [ { 用户信息 }, ... ]
    # }
    Result get_multiple(1:Payload payload);

    # [ docs ]
    # 获取随机马甲用户
    #
    # [ payload ]
    # auth : 授权信息
    # data : { }
    #
    # [ result ]
    # data : {
    #     user : { 马甲用户信息, token : 授权Token }
    # }
    Result random_sockpuppet(1:Payload payload);

    # [ docs ]
    # 创建用户
    #
    # [ payload ]
    # data : {
    #     cellphone : { },
    #     email : 邮箱验证信息,
    #     openid : 微信/ＱＱ OpenID,
    #     unionid : 微信 UnionID,
    #     nickname : 昵称,
    #     password : 密码,
    #     gender : 性别（M-男，F-女）,
    #     avatar : { id : 头像图片ID },
    # }
    #
    # [ result ]
    # msg : 注册成功
    Result create(1:Payload payload);

    # [ docs ]
    # 更新用户资料
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     nickname : 昵称,
    #     avatar : { id : 头像图片ID },
    #     gender : 性别（M-男，F-女）,
    #     province : 省份,
    #     city : 城市,
    #     qq_account : QQ号,
    #     weixin_account : 微信号,
    #     weibo_account : 微博帐号
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_info(1:Payload payload);

    # [ docs ]
    # 更改用户密码
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     old_password : 旧密码,
    #     new_password : 新密码,
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_password(1:Payload payload);

    # [ docs ]
    # 重置用户密码
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     password : 新密码,
    # }
    #
    # [ result ]
    # msg : 重置成功
    Result reset_password(1:Payload payload);

    # [ docs ]
    # 更改用户绑定信息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     mode : 类型（cellphone/email/weixin/qq）,
    #     toggle : 1-绑定 / 2 - 解绑,
    #     cellphone : 手机号码,
    #     email : 邮箱地址,
    #     validation : 验证信息,
    #     weixin : 微信 Access 信息,
    #     qq : ＱＱ Access 信息,
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_bind(1:Payload payload);

    # [ docs ]
    # 更改用户状态
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     user : 用户ID,
    #     status : 状态（-1-黑名单，0-删除，1-正常，2-未激活，3-禁言）,
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_status(1:Payload payload);

    # [ docs ]
    # 修改用户权限
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     user : 用户ID,
    #     permissions : 权限
    # }
    #
    # [ result ]
    # msg : 修改成功
    Result update_permissions(1:Payload payload);
}

