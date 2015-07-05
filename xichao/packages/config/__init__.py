# -*- coding: utf-8 -*-

GROUP=[u'广场',u'文章',u'专栏']
CATEGORY=[u'书评',u'影评',u'杂文',u'专栏文章']

#书评
_CATEGORY_BookReview_ = '1'
#影评
_CATEGORY_FilmReview_ = '2'
#杂文
_CATEGORY_Essay_ = '3'


#广场
_GROUP_Square_ = '1'
#文章
_GROUP_Article_ = '2'	# Not used
#专栏
_GROUP_Special_ = '3'


#普通用户
_ROLE_Normal_ = '1'
#专栏作家
_ROLE_Author_ = '2'
#编辑
_ROLE_Editor_ = '3'
#管理员
_ROLE_Root_ = '3'


_MEMBER_DOMAIN_ = 'http://shjdxcsd.xicp.net:4057'
_MEMBER_SECRET_ = '18A6E54B00574FD5C172C52C3D689C8E'
_MEMBERSHIP_READ_ = _MEMBER_DOMAIN_ + '/website_read.aspx?Secret=' + _MEMBER_SECRET_ + '&CardID='
_MEMBERSHIP_WRITE_ = _MEMBER_DOMAIN_ + '/website_write.aspx?Secret=' + _MEMBER_SECRET_ + '&CardID='

#本地
#_RDS_DB_URL_ = 'mysql://root:Xichao42@localhost/xichao?charset=utf8'
#RDS服务器
_RDS_DB_URL_ ='mysql://xichao:Xichao42@rdszfuv6jmjjbei.mysql.rds.aliyuncs.com:3306/xichao?charset=utf8'