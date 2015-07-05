# -*- coding: utf-8 -*-
from imports import *

##################################    广场 ##################################
#广场主页
@app.route('/square',methods=['get'])
def square():
    try:
        sort1 = request.args.get('sort1')
        sort2 = request.args.get('sort2')
        sort3 = request.args.get('sort3')

    except Exception:
        abort(404)

    if sort1 == 'time':
        book_review_list=get_article_group_by_time('1','1')
    else:
        book_review_list=get_article_group_by_coin('1','1')
        
        
    if sort2 == 'time':
        film_review_list=get_article_group_by_time('1','2')
    else:
        film_review_list=get_article_group_by_coin('1','2')

    if sort3 == 'time':
        essay_list=get_article_group_by_time('1','3')
    else: 
        essay_list=get_article_group_by_coin('1','3')

    ##拿9篇热门文章
    hot_ground_article_list=get_hot_ground_acticle()
    ##拿一篇推荐文章
    recommended_ground_article=get_recommended_ground_article()
    recommend_words=get_recommend_words()[0]
    ##参数1表示广场

    return render_template('square.html', type=1, hot_ground_article_list=hot_ground_article_list,\
        book_review_list=book_review_list,film_review_list=film_review_list,essay_list=essay_list,\
        recommended_ground_article=recommended_ground_article,recommend_words=recommend_words,\
    )