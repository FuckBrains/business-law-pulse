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

# 授权Token
service AuthService {
    # [ docs ]
    # 验证管理员授权Token
    #
    # [ payload ]
    # data : {
    #     id : 管理员ID,
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
    # 创建管理员授权Token，用于登录场景
    #
    # [ payload ]
    # device : 设备信息
    # data : {
    #     type : 登录方式（password/weixin/qq）,
    #     identifier : 唯一标识（手机/邮箱/微信OpenID/ＱＱOpenID）,
    #     password : 登录密码
    # }
    #
    # [ result ]
    # data : {
    #     admin : { id: 管理员ID, token : 授权Token }
    # }
    Result create_token(1:Payload payload);

    # [ docs ]
    # 销毁管理员授权Token
    #
    # [ payload ]
    # auth : 授权信息
    # device : 设备信息
    # data : { }
    #
    # [ result ]
    # msg : 注销成功
    Result destroy_token(1:Payload payload);
}

# 管理员资料
service ProfileService {
    # [ docs ]
    # 搜索管理员
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
    #     admins : [ 管理员列表 ]
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 创建管理员
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     avatar : { id : 头像图片ID },
    #     realname : 真实姓名,
    #     gender : 性别（M-男，F-女）,
    #     email : 电子邮箱,
    #     cellphone : 手机号码,
    # }
    #
    # [ result ]
    # msg : '创建成功'
    Result create(1:Payload payload);

    # [ docs ]
    # 根据唯一标识获取管理员基本信息
    #
    # [ payload ]
    # data : {
    #     type : 标识类型（mobile-手机, email-邮箱）,
    #     identifier : 唯一标识
    # }
    #
    # [ result ]
    # data : {
    #     admin : { 管理员信息 }
    # }
    Result with_identifier(1:Payload payload);

    # [ docs ]
    # 获取管理员基本信息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admin : 管理员ID
    # }
    #
    # [ result ]
    # data : {
    #     admin : { 管理员信息 }
    # }
    Result get_digest(1:Payload payload);

    # [ docs ]
    # 获取管理员详细信息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admin : 管理员ID
    # }
    #
    # [ result ]
    # data : {
    #     admin : { 管理员信息 }
    # }
    Result get_detail(1:Payload payload);

    # [ docs ]
    # 获取多个管理员基本信息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admins : [ 管理员ID, ... ]
    # }
    #
    # [ result ]
    # data : {
    #     admins : [ { 管理员信息 }, ... ]
    # }
    Result get_multiple(1:Payload payload);

    # [ docs ]
    # 更新管理员资料
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     avatar : { id : 头像图片ID },
    #     realname : 真实姓名,
    #     gender : 性别（M-男，F-女）,
    #     email : 电子邮箱,
    #     cellphone : 手机号码,
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_info(1:Payload payload);

    # [ docs ]
    # 更改管理员密码
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
    # 重置管理员密码
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admin : 管理员ID,
    #     password : 新密码,
    # }
    #
    # [ result ]
    # msg : 重置成功
    Result reset_password(1:Payload payload);

    # [ docs ]
    # 更改管理员状态
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admin : 管理员ID,
    #     status : 状态,
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_status(1:Payload payload);

    # [ docs ]
    # 修改管理员权限
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     admin : 管理员ID,
    #     permissions : 权限
    # }
    #
    # [ result ]
    # msg : 修改成功
    Result update_permission(1:Payload payload);

    # [ docs ]
    # 获取管理员权限定义表
    #
    # [ payload ]
    # auth : 授权信息
    #
    # [ result ]
    # data : {
    #     permissions : { 管理员权限定义表 }
    # }
    Result load_permissions(1:Payload payload);
}




