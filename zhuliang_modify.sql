alter table book modify column author varchar(255);
alter table homepage add ground_recommended_article int(11) not null default 1;
alter table homepage add constraint FK_ID foreign key(ground_recommended_article) references article(article_id);
alter table message add is_read char(1) not null default '0';
create index is_read on message(is_read);
alter table comment add is_read char(1) not null default '0';
create index is_read on comment(is_read);