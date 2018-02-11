# 检查是否登录的中间件
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

class UserAuthMiddleware(MiddlewareMixin):
    def process_request(self,request):

        # 设置login的白名单，避免陷入死循环
        if settings.RBAC_LOGIN_URL == request.path_info:
            return None
        user_info = request.session.get(settings.LOGIN_SESSION_KEY)
        if not user_info:
            return redirect(settings.RBAC_LOGIN_URL)



















