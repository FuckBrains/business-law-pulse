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

service CrawlService {
    # [ docs ]
    # 筛选爬虫新闻列表
    #
    # [ payload ]
    # data : {
    #     keyword : 搜索关键字,
    #     page : { size : 页面大小, no : 页码编号, base : {  id : 基准ID } }
    # }
    #
    # [ result ]
    # data : {
    #     articles : [ 新闻列表 ],
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 删除爬虫新闻
    Result remove(1:Payload payload);

    # [ docs ]
    # 获取爬虫新闻详情
    Result get_detail(1:Payload payload);

    # [ docs ]
    # 获取多个爬虫新闻
    Result get_multiple(1:Payload payload);

    # [ docs ]
    # 增加爬虫新闻阅读数
    Result view(1:Payload payload);

    # [ docs ]
    # 重置爬虫新闻重复标识
    Result reset_duplicate(1:Payload payload);

    # [ docs ]
    # 获取爬虫统计数据
    Result get_stats(1:Payload payload);
}

service EditService {
    # [ docs ]
    # 筛选手工新闻列表
    #
    # [ payload ]
    # data : {
    #     keyword : 搜索关键字,
    #     page : { size : 页面大小, no : 页码编号, base : {  id : 基准ID } }
    # }
    #
    # [ result ]
    # data : {
    #     articles : [ 新闻列表 ],
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 添加手工新闻
    Result create(1:Payload payload);

    # [ docs ]
    # 修改手工新闻
    Result update(1:Payload payload);

    # [ docs ]
    # 删除手工新闻
    Result remove(1:Payload payload);

    # [ docs ]
    # 获取手工新闻详情
    Result get_detail(1:Payload payload);

    # [ docs ]
    # 获取多个手工新闻
    Result get_multiple(1:Payload payload);

    # [ docs ]
    # 增加手工新闻阅读数
    Result view(1:Payload payload);
}

service NewsService {
    # [ docs ]
    # 筛选新闻列表
    #
    # [ payload ]
    # data : {
    #     keyword : 搜索关键字,
    #     page : { size : 页面大小, no : 页码编号, base : {  id : 基准ID } }
    # }
    #
    # [ result ]
    # data : {
    #     articles : [ 新闻列表 ],
    #     total : 记录总数
    # }
    Result filter(1:Payload payload);

    # [ docs ]
    # 获取热门新闻列表
    Result list_hot(1:Payload payload);

    # [ docs ]
    # 添加热门新闻
    Result add_hot(1:Payload payload);

    # [ docs ]
    # 更新热门新闻列表
    Result update_hot(1:Payload payload);

    # [ docs ]
    # 获取新闻分类
    Result categorize_tag(1:Payload payload);

    # [ docs ]
    # 注入新闻代码
    Result inject_script(1:Payload payload);
}


