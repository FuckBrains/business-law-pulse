# thrift definition
# https://diwakergupta.github.io/thrift-missing-guide/#_constants

##################################################
# struct
##################################################

# thrift service 设备信息
struct Device {
    1: string agent;
    2: string ip;
    3: i32 port;
}

# thrift service 授权信息
struct Auth {
    1: required string type;        # user / admin
    2: required string id;
    3: string token;
    4: list<string> permissions;
    5: i64 expire;
    6: string signature;
}

# thrift service 上游信息
struct Upstream {
    1: required string app;
    2: required string host;
    3: required string ip;
    4: required string mac;
}

# thrift service 参数载体
struct Payload {
    1: required string gid;         # global sequence id
    2: required string sid;         # sub sequence id
    3: Upstream upstream;
    4: Auth auth;
    5: Device device;
    6: string data;
}

# thrift service 返回结果
struct Result {
    1: required i16 err = 0;
    2: required string data = "";
    3: required string msg = "";
    4: required string log = "";
}


##################################################
# const
##################################################

# 图片场景配置信息
typedef list<i16> DIMENSION
typedef list<DIMENSION> DIMENSIONS
const map<string,DIMENSIONS> SCENE = {
    'launch/image':                 [ [1242,2208] ],

    'admin/avatar':                 [ [150,150], [100,100], [50,50] ],
    'user/avatar':                  [ [150,150], [100,100], [50,50] ],
    'comment/picture':              [ [1000,750], [600,450], [200,150] ],
    'ueditor/picture':              [ [900,675] ],

    'news/cover':                   [ [320,180], [160,90] ],
    'video/cover':                  [ [270,180], [180,120] ],
    'contribution/cover':           [ [500,300], [250,150], [50,30] ],

    'law/client/logo':              [ [150,150], [100,100], [50,50] ],
    'law/firm/logo':                [ [150,150], [100,100], [50,50] ],
    'law/lawyer/avatar':            [ [150,150], [100,100], [50,50] ],
}

##################################################
# service
##################################################

# 配置
service ConfigService {
    # [ docs ]
    # 获取全局配置
    #
    # [ payload ]
    # device : 设备信息
    #
    # [ result ]
    # data : {
    #     upgrade : { 版本升级信息 },
    #     launch : { 启动图信息 },
    #     mqtt : { MQTT连接参数 },
    #     share : { 分享参数 },
    # }
    Result get_global(1:Payload payload);

    # [ docs ]
    # 获取应用市场列表
    #
    # [ payload ]
    # auth : 授权信息
    #
    # [ result ]
    # data : {
    #     markets : [ 市场列表 ],
    # }
    Result list_market(1:Payload payload);

    # [ docs ]
    # 更新应用市场列表
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #    markets : [ 市场列表 ]
    # }
    #
    # [ result ]
    # msg : 更新成功
    Result update_market(1:Payload payload);

    # [ docs ]
    # 获取应用启动图列表
    #
    # [ payload ]
    # auth : 授权信息
    #
    # [ result ]
    # data : {
    #     lanuches : [ 应用启动图列表 ],
    # }
    Result list_launch(1:Payload payload);

    # [ docs ]
    # 添加应用启动图
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #    image : { id: 图片ID },
    #    countdown : 倒计时（秒）,
    #    start : 有效起始时间戳,
    #    end : 有效起始时间戳,
    #    url : 点击跳转URL
    # }
    #
    # [ result ]
    # msg : 添加成功
    Result add_launch(1:Payload payload);

    # [ docs ]
    # 删除应用启动图
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #    image : { id: 图片ID },
    # }
    #
    # [ result ]
    # msg : 删除成功
    Result remove_launch(1:Payload payload);
}

# 图片
service ImageService {
    # [ docs ]
    # 保存图片
    #
    # [ payload ]
    # data : {
    #     scene : 图片场景,
    #     path : 图片存储路径,
    #     name : 图片文件名
    # }
    #
    # [ result ]
    # data : {
    #     image : { 图片结构体 }
    # }
    Result store(1:Payload payload);

    # [ docs ]
    # 下载网络图片
    #
    # [ payload ]
    # data : {
    #     scene : 图片场景,
    #     url : 网络图片地址
    # }
    #
    # [ result ]
    # data: {
    #     image : { 图片结构体 }
    # }
    Result download(1:Payload payload);

    # [ docs ]
    # 提取图片
    #
    # [ payload ]
    # data : {
    #     image: 图片ID
    # }
    #
    # [ result ]
    # data : {
    #     image : { 图片结构体 }
    # }
    Result extract(1:Payload payload);

    # [ docs ]
    # 构建默认图片
    #
    # [ payload ]
    # data : {
    #     scene : 图片场景,
    #     path : 默认图片
    # }
    #
    # [ result ]
    # data : {
    #     image : { 图片结构体 }
    # }
    Result construct(1:Payload payload);
}

# 文件
service FileService {
    # [ docs ]
    # 保存文件
    #
    # [ payload ]
    # data : {
    #     path : 图片存储路径,
    #     name : 图片文件名
    # }
    #
    # [ result ]
    # data : {
    #     file : { 文件结构体 }
    # }
    Result store(1:Payload payload);

    # [ docs ]
    # 提取文件
    #
    # [ payload ]
    # data : {
    #     id: 文件ID
    # }
    #
    # [ result ]
    # data : {
    #     file : { 文件结构体 }
    # }
    Result extract(1:Payload payload);
}


# 地理位置（国家、省份、城市）
service GeoService {
    # [ docs ]
    # 获取全部地理数据
    #
    # [ result ]
    # data : {
    #     storage : [ 地理信息 ]
    # }
    Result get_storage(1:Payload payload);

    # [ docs ]
    # 获取全球大洲国家地理信息
    #
    # [ result ]
    # data : {
    #     globe : [ 大洲列表 ]
    # }
    Result get_globe(1:Payload payload);

    # [ docs ]
    # 获取国家省份城市地理信息
    #
    # [ payload ]
    # data : {
    #     country : 国家ID
    # }
    #
    # [ result ]
    # data : {
    #     storage : [ 省份列表 ]
    # }
    Result get_country(1:Payload payload);

    # [ docs ]
    # 解析省份城市名称
    #
    # [ payload ]
    # data : {
    #     province : 省份,
    #     city : 城市
    # }
    #
    # [ result ]
    # data : {
    #     province : { 省份信息 },
    #     city : { 城市信息 }
    # }
    Result parse(1:Payload payload);
}

# UEditor
service UEditorService {
    # [ docs ]
    # 获取图片列表
    #
    # [ payload ]
    # data : {
    #     page : { size : 页面大小, no : 页码编号 }
    # }
    #
    # [ result ]
    # data : {
    #     images : [ 图片列表 ],
    #     total : 记录总数
    # }
    Result list_image(1:Payload payload);

    # [ docs ]
    # 获取文件列表
    #
    # [ payload ]
    # data : {
    #     page : { size : 页面大小, no : 页码编号 }
    # }
    #
    # [ result ]
    # data : {
    #     files : [ 文件列表 ],
    #     total : 记录总数
    # }
    Result list_file(1:Payload payload);
}

# 推送
service PushService {
    # [ docs ]
    # 单设备推送
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     title : 标题,
    #     content : 内容,
    #     url : 点击跳转URL,
    #     platform : 设备类型（android/ios）,
    #     token : 设备Token
    # }
    #
    # [ result ]
    # msg : 推送成功
    Result unicast(1:Payload payload);

    # [ docs ]
    # 多设备推送
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     title : 标题,
    #     content : 内容,
    #     url : 点击跳转URL,
    #     platform : 设备类型（android/ios）,
    #     tokens : [ 设备Token列表 ]
    # }
    #
    # [ result ]
    # msg : 推送成功
    Result listcast(1:Payload payload);

    # [ docs ]
    # 全设备推送
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     title : 标题,
    #     content : 内容,
    #     url : 点击跳转URL,
    #     platform : 设备类型（android/ios）,
    # }
    #
    # [ result ]
    # msg : 推送成功
    Result broadcast(1:Payload payload);
}

# MQTT
service MqttService {
    # [ docs ]
    # 推送指定主题的消息
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     topic : 主题,
    #     content : 内容
    # }
    #
    # [ result ]
    # msg : 推送成功
    Result push(1:Payload payload);

    # [ docs ]
    # 加密文本
    #
    # [ payload ]
    # data : {
    #     text : 明文,
    #     key : 公钥
    # }
    #
    # [ result ]
    # data : {
    #     text : 密文
    # }
    Result encrypt(1:Payload payload);

    # [ docs ]
    # 解密文本
    #
    # [ payload ]
    # data : {
    #     text : 密本,
    #     key : 公钥
    # }
    #
    # [ result ]
    # data : {
    #     text : 明文
    # }
    Result decrypt(1:Payload payload);
}

# 短信
service SmsService {
    # [ docs ]
    # 发送验证码
    #
    # [ payload ]
    # device : 设备信息
    # data : {
    #     cellphone : 手机号码,
    #     validation : 验证码,
    #     account : 帐号（可选，UserID / OpenID）,
    #     scene : 场景码
    # }
    #
    # [ result ]
    # msg : 发送成功
    Result send_validation(1:Payload payload);
}

# 邮件
service EmailService {
    # [ docs ]
    # 发送验证邮件
    #
    # [ payload ]
    # data : {
    #     scene : 场景码,
    #     email : 邮箱,
    #     user : 用户名称
    # }
    #
    # [ result ]
    # msg : 发送成功
    Result send_validation(1:Payload payload);
}

# OAuth认证
service OAuthService {
    Result check_qq_access(1:Payload payload);
    Result check_weixin_access(1:Payload payload);
    Result get_qq_access_by_code(1:Payload payload);
    Result get_weixin_access_by_code(1:Payload payload);
    Result get_weixin_access_by_credential(1:Payload payload);
    Result sign_weixin_jsapi(1:Payload payload);
    Result get_qq_user_info(1:Payload payload);
    Result get_weixin_user_info(1:Payload payload);
}


# Feedback
service FeedbackService {
    # [ docs ]
    # 获取反馈列表
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     keyword : 关键字,
    #     page : { size : 页面大小, no : 页码编号 }
    # }
    #
    # [ result ]
    # data : {
    #     feedbacks : [ 反馈列表 ],
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 添加反馈
    #
    # [ payload ]
    # data : {
    #     content : 内容,
    #     contact : 联系方式
    # }
    #
    # [ result ]
    # msg : 提交成功
    Result add(1:Payload payload);

    # [ docs ]
    # 删除反馈
    #
    # [ payload ]
    # auth : 授权信息
    # data : {
    #     feedback : { id : 反馈ID }
    # }
    #
    # [ result ]
    # msg : 删除成功
    Result remove(1:Payload payload);
}

# Doc
service DocService {
    Result list_modules(1:Payload payload);
    Result create_module(1:Payload payload);
    Result update_module(1:Payload payload);
    Result get_module(1:Payload payload);
    Result list_items(1:Payload payload);
    Result create_item(1:Payload payload);
    Result update_item(1:Payload payload);
    Result remove_item(1:Payload payload);
    Result get_item(1:Payload payload);
    Result seq_item(1:Payload payload);
}
