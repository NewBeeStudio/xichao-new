use xichao;
alter table book modify column author varchar(255);
alter table homepage add ground_recommended_article int(11) not null default 1;
alter table homepage add constraint FK_ID foreign key(ground_recommended_article) references article(article_id);
alter table message add is_read char(1) not null default '0';
create index is_read on message(is_read);
alter table comment add is_read char(1) not null default '0';
create index is_read on comment(is_read);





alter table user add cover varchar(255) not null default '/upload/cover/default.jpg';







alter table homepage add column recommended_activity int(11) not null default 1;





alter table homepage add recommended_activity int(11) not null default 1;
alter table homepage add constraint FK_ID foreign key(recommended_activity) references activity(activity_id);