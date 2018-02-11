#!/usr/bin/python
# -*- coding:utf-8 -*-
# 这是用户登录后初始化用户权限信息的模块

from django.conf import settings

def init_permission(request,user):
    """
    用户登录后初始化用户权限信息
    :param request: request
    :param user: rbac的  用户对象
    :return: 
    """
    # 获取当前用户的权限信息
    """
        外键和多对多  都可以用  __(双下划线)  跨表获取对应字段
        [].distinct()  进行去重 
    """
    permission_list = user.roles.filter(permissions__id__isnull=False).values(
        'permissions__id',
        'permissions__title',
        'permissions__url',
        'permissions__code',
        'permissions__group',                   # 权限所属组
        'permissions__sibling_permission_id',   # 当前权限默认选中的组内权限ID
        'permissions__is_menu',
        'permissions__group__parent_id',        # 即：当前权限所在组的所属菜单ID
        'permissions__group__parent__title',    # 即：当前权限所在组的所属菜单名称
    ).distinct()

    # 权限部分：格式化当前用户的权限信息；主要用于中间件认证以及控制是否显示增加、修改、删除等button
    """
        {
            1: {
                'codes': ['list', 'add'], 
                'urls': ['/userinfo/', '/userinfo/add/']
            }, 
            2: {
                'codes': ['list'], 
                'urls': ['/order/']
            },
            ...
        }
    """
    permission_dict = {}
    for item in permission_list:
        url = item.get('permissions__url')
        code = item.get('permissions__code')
        group_id = item.get('permissions__group')
        if group_id in permission_dict:
            permission_dict[group_id]['urls'].append(url)
            permission_dict[group_id]['codes'].append(code)
        else:
            permission_dict[group_id] = {'codes': [code, ], 'urls': [url, ]}
    # 把当前用户权限信息存储到session中
    request.session[settings.PERMISSION_DICT] = permission_dict


    # 菜单部分：格式化当前用户的菜单列表信息 （因为 code和group和菜单显示无关，所以去掉）
    # 最终的目的就是要把菜单和具体的is_menu=True的权限item关联起来并在前端构成 两级菜单
    '''
        [
            {'url': '/userinfo/', 'menu_title': '用户管理菜单', 'title': '用户列表', 'menu_id': 4, 'id': 1, 'menu_gp_id': None}, 
            {'url': '/userinfo/add/', 'menu_title': '用户管理菜单', 'title': '添加用户', 'menu_id': 4, 'id': 2, 'menu_gp_id': 1}, 
            {'url': '/order/', 'menu_title': '订单管理菜单', 'title': '订单列表', 'menu_id': 5, 'id': 5, 'menu_gp_id': None}, 
            {'url': '/order/add/', 'menu_title': '订单管理菜单', 'title': '添加订单', 'menu_id': 5, 'id': 6, 'menu_gp_id': 5}, 
            {'url': '/index/', 'menu_title': '订单管理菜单', 'title': '首页', 'menu_id': 5, 'id': 9, 'menu_gp_id': None}
        ]
    '''
    permission_menu_list = []
    for item in permission_list:
        # if item['permissions__is_menu']:
        tpl = {
            'id': item['permissions__id'],
            'title': item['permissions__title'],
            'url': item['permissions__url'],
            'menu_gp_id': item['permissions__sibling_permission_id'],
            'menu_id': item['permissions__group__parent_id'],
            'menu_title': item['permissions__group__parent__title'],
        }
        permission_menu_list.append(tpl)
    # 把当前用户菜单信息存储到session中
    request.session[settings.PERMISSION_MENU_LIST] = permission_menu_list

    # 设置session的超时时间：30min
    request.session.set_expiry(1800)
