alter  table comment add root int(11);
alter table comment add constraint root foreign key(root) REFERENCES user(user_id);
alter  table comment add father int(11);
alter table comment add constraint father foreign key(father) REFERENCES user(user_id);
alter table comment modify column content text;