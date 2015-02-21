# -*- coding: utf-8 -*-
'''

	应用启动模块

	启动应用
	
'''
from xichao import app
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)



if __name__ == '__main__':
	app.run()
