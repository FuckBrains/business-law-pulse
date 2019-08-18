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


# law config
service ConfigService {
    Result load(1:Payload payload);
    Result update(1:Payload payload);
}


# law client
service ClientService {
    Result filter(1:Payload payload);
    Result create(1:Payload payload);
    Result update(1:Payload payload);
    Result remove(1:Payload payload);
    Result get_digest(1:Payload payload);
    Result get_detail(1:Payload payload);
    Result get_multiple(1:Payload payload);
}


# law firm
service FirmService {
    Result filter(1:Payload payload);
    Result create(1:Payload payload);
    Result update(1:Payload payload);
    Result remove(1:Payload payload);
    Result get_digest(1:Payload payload);
    Result get_detail(1:Payload payload);
    Result get_multiple(1:Payload payload);
    Result list_children(1:Payload payload);

    Result filter_feedbacks(1:Payload payload);
    Result create_feedback(1:Payload payload);
    Result remove_feedback(1:Payload payload);
}


# lawyer
service LawyerService {
    Result filter(1:Payload payload);
    Result create(1:Payload payload);
    Result update(1:Payload payload);
    Result remove(1:Payload payload);
    Result get_digest(1:Payload payload);
    Result get_detail(1:Payload payload);
    Result get_multiple(1:Payload payload);
    Result get_career(1:Payload payload);

    Result filter_feedbacks(1:Payload payload);
    Result create_feedback(1:Payload payload);
    Result remove_feedback(1:Payload payload);
}


# law deal
service DealService {
    Result filter(1:Payload payload);
    Result create(1:Payload payload);
    Result update(1:Payload payload);
    Result remove(1:Payload payload);
    Result get_digest(1:Payload payload);
    Result get_detail(1:Payload payload);
    Result get_multiple(1:Payload payload);
    Result get_relation(1:Payload payload);

    Result list_clients(1:Payload payload);
    Result add_client(1:Payload payload);
    Result update_client(1:Payload payload);
    Result remove_client(1:Payload payload);

    Result list_firms(1:Payload payload);
    Result add_firm(1:Payload payload);
    Result update_firm(1:Payload payload);
    Result remove_firm(1:Payload payload);

    Result list_lawyers(1:Payload payload);
    Result add_lawyer(1:Payload payload);
    Result update_lawyer(1:Payload payload);
    Result remove_lawyer(1:Payload payload);

    Result filter_feedbacks(1:Payload payload);
    Result create_feedback(1:Payload payload);
    Result remove_feedback(1:Payload payload);
}


# law stats
service StatsService {
    Result render_m1(1:Payload payload);
    Result render_m2(1:Payload payload);

    Result render_custom(1:Payload payload);

    Result list_ranking_firms(1:Payload payload);
    Result list_ranking_deals(1:Payload payload);

    Result analyse_recent_by_firm(1:Payload payload);
    Result analyse_recent_by_lawyer(1:Payload payload);
}



