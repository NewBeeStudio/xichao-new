CREATE TABLE pay_record (
	pay_record_id INTEGER NOT NULL AUTO_INCREMENT, 
	coins INTEGER NOT NULL, 
	user_id INTEGER, 
	article_id INTEGER, 
	PRIMARY KEY (pay_record_id), 
	FOREIGN KEY(user_id) REFERENCES user (user_id), 
	FOREIGN KEY(article_id) REFERENCES article (article_id)
)ENGINE=InnoDB CHARSET=utf8
