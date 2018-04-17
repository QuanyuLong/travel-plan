#!/usr/bin/env python
#encoding: utf-8

import web
from web import form
import urllib2
import os
from SearchAPI import Search
from searchEngine import searchEngine
import cv2

urls = (
    '/', 'index',
    '/sf', 'search_food',
    '/ss', 'search_scene',
    '/sr', 'route',
    '/si', 'search_image',
    '/sii', 'search_image_by_image',
)


render = web.template.render('templates') # your templates

login = form.Form(
    form.Textbox('keyword'),
    form.Button('Search'),
)

def search_where(province, kind, query):
    province = 'shanghai'
    result_dict = Search(province, kind, query)
    if not type(result_dict) == type(''):
        if 'introduction' in result_dict.keys():
            result_dict['introduction'] = result_dict['introduction'].split('\n')
        if 'img_list' in result_dict.keys():
            result_dict['img_list'] = result_dict['img_list'].split('\n')
        return result_dict
    else:
        return None
#    result_dict = { 'location':'共青国家森林公园', 'introduction':'景点介绍\n共青国家森林公园位于上海市区东北部、黄浦江畔，是距离上海市区最近的森林公园。共青森林公园中的大片森林是20世纪50年代积植树造林的成果，这里还有丘陵、大草坪、湖泊、溪流等景观，环境优美。可以来公园划船、烧烤、骑马，或是玩海盗船、打靶射击等娱乐项目，即使在公园里散散步、骑骑车、呼吸清新空气，也是一种享受。\n共青森林公园有四个门，其中南大门和西大门是主要入口。坐公交车通常可从西门进入，门口的公交线路较多，自驾车则可到南门，因为公园的大型停车场建在南门。从公园西门进入，首先是娱乐区域，左边有海盗船、激流勇进、溜冰场等设施，右手边有过山车、旋转木马、碰碰车、彩弹射击场等项目，还有森林小火车可以乘坐。每逢周末，有些娱乐项目要排很久的队才能玩到。\n从左手边往里走，有专门的烧烤野营区和跑马场，周末和节假日时烧烤区相当火爆。继续往公园深处，有人工湖泊，可以划船泛舟，也可以坐一次滑索从湖上滑到对岸。公园深处主要是树林和草坪，环境更为安静，适合散步或小憩，走到公园最东南端是黄浦江畔，可以看到浦江上的往来船只。\n森林公园内有不少小卖部，出售饮料和零食小吃，价格比外面略贵。公园内也有餐厅，但菜价较贵，建议自带些干粮。另外，在森林公园南门斜对面，还有一个小景点“万竹园”，它是森林公园的一部分。万竹园不大，里面遍布竹林，可见小桥流水的江南景观，凭森林公园门票即可入内游览。', 'score':'4.5' ,'img_list':'https://dimg06.c-ctrip.com/images/fd/tg/g1/M07/80/F1/CghzfFWxCLiAJqsaAAx-SkpYmHY852_C_350_230.jpg\nhttps://dimg08.c-ctrip.com/images/100c0e00000073gd3264F_C_350_230.jpg\nhttps://dimg06.c-ctrip.com/images/10030e00000073gm733C9_C_350_230.jpg'}


class index:
    def GET(self):
        f = login()
        return render.index(f)

class search_food:
    def GET(self):
        return render.food()
    def POST(self):
        f = web.input()
        #vm_env.attachCurrentThread()
        content = f.key
        print content
        result_dict= search_where('province', 'food', content.encode('utf8'))
        return render.food_result(result_dict)

class search_scene:
    def GET(self):
        return render.scene()
    def POST(self):
        f = web.input()
        #vm_env.attachCurrentThread()
        content = f.key
        print content
        result_dict= search_where('province', 'trip', content.encode('utf8'))
        return render.scene_result(result_dict)

class route:
    def GET(self):
        f= login()
        return render.route_new()
        
class search_image:
    def GET(self):
        f = login()
        return render.image()
    def POST(self):
        f = web.input()
        content = f.key
        print content
        content = content.encode('utf8')
        imageName = searchEngine('colorindex','structureindex',content)
        for i in range(len(imageName)):
            if imageName[i] == '_':
                imageName = imageName[:i]
                break
        print imageName
        result_dict= search_where('province', 'trip', imageName)
        return render.image_result(result_dict)

class search_image_by_image:
    def POST(self):
        f = web.input(image={})
        content = f.image
        imageName = searchEngine('colorindex','structureindex',content)
        for i in range(len(imageName)):
            if imageName[i] == '_':
                imageName = imageName[:i]
                break
        print imageName
        result_dict= search_where('province', 'trip', imageName)
        return render.image_result(result_dict)
#        name, ext = os.path.splitext(filename)
#        ext = ext.lower()
#        safeImageExts = ('.png','.jpg','.jpeg','.gif')
#        if not ext in safeImageExts:
#            print 'Error!'
#        saveToDir = "/"
#        if not os.path.exists(saveToDir):
#            os.makedirs(saveToDir)
#        newName = "%s%s" % (urlName, ext)
#        saveToPath = os.path.join(saveToDir, newName)
#        
#        img.save(saveToPath)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
