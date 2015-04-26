alter  table comment add reply_to_comment_id int(11) default 0;



alter table homepage drop foreign key FK_ID;