#!/usr/bin/python
# -*- coding:utf-8 -*-

from django import template
register = template.Library()

import re
from django.conf import settings

'''
    [
        {'url': '/userinfo/', 'menu_title': '用户管理菜单', 'title': '用户列表', 'menu_id': 4, 'id': 1, 'menu_gp_id': None}, 
        {'url': '/userinfo/add/', 'menu_title': '用户管理菜单', 'title': '添加用户', 'menu_id': 4, 'id': 2, 'menu_gp_id': 1}, 
        {'url': '/order/', 'menu_title': '订单管理菜单', 'title': '订单列表', 'menu_id': 5, 'id': 5, 'menu_gp_id': None}, 
        {'url': '/order/add/', 'menu_title': '订单管理菜单', 'title': '添加订单', 'menu_id': 5, 'id': 6, 'menu_gp_id': 5}, 
        {'url': '/index/', 'menu_title': '订单管理菜单', 'title': '首页', 'menu_id': 5, 'id': 9, 'menu_gp_id': None}
        ...
    ]
    
    转换成下面的结构，然后再前端进行展示
    
    {
        4:{
            'opened':False,
            'menu_title':'用户管理菜单',
            'children': [
                {'title': '用户列表', 'url': '/userinfo/', 'opened':False},
                {'title': '订单列表', 'url': '/order/', 'opened':False,}
            ]
        },
        6: {	
            'opened':False,
            'menu_title':'权限管理菜单',
            'children': [
                {'title': '权限列表', 'url': '/xxxinfo/', 'opened':False},
                {'title': '分类列表', 'url': '/xxxxxxxx/', 'opened':False,}
            ]
        },
        ...
    }
'''

@register.inclusion_tag('rbac/menu_tpl.html')
def menu_show(request):
    current_request_url = request.path_info
    menu_list = request.session.get(settings.PERMISSION_MENU_LIST)

    # 首先先把默认选中的组内权限ID为None的权限获取出来，即 用户列表,订单列表...
    menu_dict = {}
    for item in menu_list:
        if not item['menu_gp_id']:
            menu_dict[item['id']] = item

    # 遍历menu_list，根据 '默认选中的组内权限ID' 的值对菜单项进行选中，避免出现点击[增加/编辑]等操作导致的菜单闭合
    for item in menu_list:
        patten = settings.URL_FORMAT.format(item['url'])
        # 首先遍历所有的具体权限，与当前请求url做比较，匹配则把 opened置为 active，用于配合前端的 .active 属性
        if re.match(patten, current_request_url):
            menu_gp_id = item['menu_gp_id']
            if menu_gp_id:
                menu_dict[menu_gp_id]['opened'] = "active"
            else:
                menu_dict[item['id']]['opened'] = "active"

    # 遍历menu_dict，进行数据结构转换
    permission_menu_dict = {}
    for item in menu_dict.values():
        opened = item.get('opened')
        menu_id = item['menu_id']
        child = {'opened': opened, 'title': item['title'], 'url': item['url']}
        if menu_id in permission_menu_dict:
            # 更新已有menu
            permission_menu_dict[menu_id]['children'].append(child)
            if opened:
                permission_menu_dict[menu_id]['opened'] = opened
        else:
            # 初始化一个menu
            permission_menu_dict[menu_id] = {
                'opened': opened,
                'menu_title': item['menu_title'],
                'children': [child,]
            }
    return {'permission_menu_dict':permission_menu_dict}






















