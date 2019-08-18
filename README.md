# ############################################
# PROJECT README
# ############################################

# sys auth
username : test@businesslawpulse.com
password : vantageasia2007


# reinit mongodb
db.getCollection('user').find({ sid: { $gt: 20000 } });

db.getCollection('feedback').remove({});
db.getCollection('user_comment').remove({});
db.getCollection('user_complain').remove({});

db.getCollection('private_message_session').remove({});
db.getCollection('system_message_box').update({},{ $set: { messages: [] } },{ multi: true });
db.getCollection('comment_message_box').update({},{ $set: { messages: [] } },{ multi: true });



