import sys
sys.path.insert(0,"/home/xichao/git/XiChao/xichao-new/")
activate_this = '/home/xichao/git/XiChao/xichao-new/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from xichao import app as application
