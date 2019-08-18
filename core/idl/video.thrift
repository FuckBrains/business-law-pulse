# thrift definition

##################################################
# include
##################################################
include "common.thrift"


##################################################
# const
##################################################


##################################################
# typedef
##################################################
typedef common.Payload Payload
typedef common.Result Result


##################################################
# service
##################################################


service VideoService{
    # [ docs ]
    # 筛选视频列表
    #
    # [ payload ]
    # data : {
    #     keyword : 搜索关键字,
    #     page : { size : 页面大小, no : 页码编号, base : {  id : 基准ID } }
    # }
    #
    # [ result ]
    # data : {
    #     videos : [ 视频列表 ],
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 添加视频
    Result create(1:Payload payload);

    # [ docs ]
    # 修改视频
    Result update(1:Payload payload);

    # [ docs ]
    # 删除视频
    Result remove(1:Payload payload);

    # [ docs ]
    # 绑定节目
    Result bind_program(1:Payload payload);

    # [ docs ]
    # 获取视频详情
    Result get_detail(1:Payload payload);

    # [ docs ]
    # 获取多个视频
    Result get_multiple(1:Payload payload);

    # [ docs ]
    # 增加视频点赞数
    Result thumbup(1:Payload payload);

    # [ docs ]
    # 增加视频观看数
    Result view(1:Payload payload);

    # [ docs ]
    # 获取相关视频
    Result list_relavant(1:Payload payload);

    # [ docs ]
    # 获取视频分类
    Result categorize(1:Payload payload);

    # [ docs ]
    # 注入视频代码
    Result inject_script(1:Payload payload);

    # [ docs ]
    # 提取网页视频
    Result extract_webpage(1:Payload payload);
}


