# 这是页面权限验证的中间件
from django.shortcuts import HttpResponse,redirect
from django.conf import settings
import re


class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class RbacMiddleware(MiddlewareMixin):
    def process_request(self,request):

        # 1. 获取当前请求的 uri
        current_request_url = request.path_info

        # 2. 判断是否在白名单里，在则不进行验证，直接放行
        for url in settings.VALID_URL_LIST:
            if re.match(url, current_request_url):
                return None

        # 3. 验证用户是否有访问权限
        flag = False
        permission_dict = request.session.get(settings.PERMISSION_DICT)

        # 如果没有登录过就直接跳转到登录页面
        if not permission_dict:
            return redirect(settings.RBAC_LOGIN_URL)
        """
            {
                1: {
                    'codes': ['list', 'add'], 
                    'urls': ['/userinfo/', '/userinfo/add/']
                }, 
                2: {
                    'codes': ['list'], 
                    'urls': ['/order/']
                }
            }
        """
        for group_id, values in permission_dict.items():
            for url in values['urls']:
                # 必须精确匹配 URL ： "^{0}$"
                patten = settings.URL_FORMAT.format(url)
                if re.match(patten, current_request_url):
                    # 获取当前用户所具有的权限的代号列表，用于之后控制是否展示相关操作
                    request.permission_code_list = values['codes']
                    flag = True
                    break
            if flag:
                break
        if not flag:
            return HttpResponse("无权访问")

















