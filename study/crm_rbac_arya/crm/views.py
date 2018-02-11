from django.shortcuts import render,HttpResponse,redirect
from crm import models
from rbac.service.init_permission import init_permission
from django.conf import settings

def login(request):
    if "GET" == request.method:
        return render(request,'login.html')
    else:
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        obj = models.UserInfo.objects.filter(username=user,password=pwd).first()
        if obj:
            # 把用户登录信息写入session
            request.session['user_info'] = {'uid':obj.id, 'name':obj.username}
            # 设置session的超时时间：30min
            request.session.set_expiry(1800)
            # 权限初始化
            # init_permission(request=request, user=obj)  注意这个user应该是rbac里面的用户对象！！！
            init_permission(request=request, user=obj.auth)
            return redirect('/index/')

        return render(request,'login.html',{'error':"用户名或密码错误！"})

def index(request):
    return render(request,'index.html')


def clear(request):
    # 手动清空session
    request.session.clear()
    return redirect(settings.RBAC_LOGIN_URL)