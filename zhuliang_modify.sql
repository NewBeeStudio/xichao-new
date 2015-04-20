alter table book modify column author varchar(255);
alter table homepage add ground_recommended_article int(11) not null default 1;
alter table homepage add constraint FK_ID foreign key(ground_recommended_article) references article(article_id);