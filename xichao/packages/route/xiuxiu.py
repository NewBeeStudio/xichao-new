# -*- coding: utf-8 -*-
from imports import *

#######################################  图片裁剪器  #########################################
@app.route('/upload/tailor/title_image')
def upload_title_image():
    return render_template('upload_title_image_tailor.html')

@app.route('/upload/tailor/avatar')
def upload_avatar():
    return render_template('upload_avatar_tailor.html')

@app.route('/upload/tailor/cover')
def upload_cover():
    return render_template('upload_cover_tailor.html')

@app.route('/upload/tailor/activity/title_image')
def upload_activity_title_image():
    return render_template('upload_activity_title_image_tailor.html')


##################################  美图秀秀配置文件  ##################################
#由于只需要crossdomain.xml，故单独路由
@app.route('/crossdomain.xml')
def xiuxiu_config():
    return send_from_directory(os.path.dirname(__file__),'crossdomain.xml')

