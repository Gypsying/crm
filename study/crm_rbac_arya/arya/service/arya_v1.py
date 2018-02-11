from django.shortcuts import HttpResponse,render
from django.conf.urls import url
from django.urls import reverse
from django.utils.safestring import mark_safe


class AryaConfig(object):

    # 借助继承特性，实现定制列展示
    list_display = []

    def __init__(self, model, arya_site):
        self.model = model
        self.arya_site = arya_site

    def get_list_display(self):
        result = []
        result.extend(self.list_display)
        # 如果有编辑权限
        # 注意这里的参数不是方法self.row_edit 而是函数AryaConfig.row_edit
        result.append(AryaConfig.row_edit)
        # 如果有删除权限
        result.append(AryaConfig.row_del)
        # 加上checkbox
        result.insert(0, AryaConfig.check_box)
        return result

    # 定制 编辑 按钮
    def row_edit(self, row=None, is_header=None):
        if is_header:
            return "编辑"
        # 反向生成URL
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        reversed_url = reverse(viewname='arya:%s_%s_change' % (app_name, model_name), args=(row.id,))
        edit_a = mark_safe("<a href='{0}'>编辑</a>".format(reversed_url))
        return edit_a

    # 定制 删除 按钮
    def row_del(self, row=None, is_header=None):
        if is_header:
            return "删除"
        # 反向生成URL
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        reversed_url = reverse(viewname='arya:%s_%s_delete' % (app_name, model_name), args=(row.id,))
        del_a = mark_safe("<a href='{0}'>删除</a>".format(reversed_url))
        return del_a

    # 定制 checkbox
    def check_box(self, row=None, is_header=None):
        if is_header:
            return "选项"
        checkbox = mark_safe("<input type='checkbox' value='{0}' />".format(row.id))
        return checkbox

    @property
    def urls(self):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_list'%(app_name,model_name,)),
            url(r'^add/$', self.add_view, name='%s_%s_add'%(app_name,model_name,)),
            url(r'^(.+)/delete/$', self.delete_view, name='%s_%s_delete'%(app_name,model_name,)),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change'%(app_name,model_name,))
        ]
        return urlpatterns,None,None

    def changelist_view(self, request):
        """
        列表页面
        :param request: 
        :return: 
        """

        # 获取表头第一版
        '''
        header_data = []
        for str_or_func in self.get_list_display():
            if isinstance(str_or_func,str):
                val = self.model._meta.get_field(str_or_func).verbose_name
            else:
                val = str_or_func(self, is_header=True)
            header_data.append(val)
        '''
        # 获取表头改进版
        def header(list_display,config):
            for str_or_func in list_display:
                if isinstance(str_or_func, str):
                    val = config.model._meta.get_field(str_or_func).verbose_name
                else:
                    val = str_or_func(config, is_header=True)
                yield val
        header_generator = header(self.get_list_display(),self)

        # 获取表内容
        table_data = []
        queryset = self.model.objects.all()
        for row in queryset:
            if not self.list_display:
                # 用列表把对象做成列表集合是为了兼容有list_display的情况在前端展示（前端用2层循环展示）
                table_data.append([row,])
            else:
                tmp = []
                for str_or_func in self.get_list_display():
                    if isinstance(str_or_func,str):
                        # 如果是字符串则通过反射取值
                        tmp.append(getattr(row,str_or_func))
                    else:
                        # 否则就是函数，获取函数执行的结果
                        tmp.append(str_or_func(self,row))
                table_data.append(tmp)

        return render(request,'item_list.html',{'table_data':table_data,'header_data':header_generator})
    def add_view(self, request):
        """
        添加页面
        :param request: 
        :return: 
        """
        return HttpResponse("add_view")
    def delete_view(self, request, uid):
        """
        删除页面
        :param request: 
        :param uid: 
        :return: 
        """
        # obj = self.model.objects.filter(id=uid).first()
        return HttpResponse("delete_view {0}".format(uid))
    def change_view(self, request, uid):
        """
        编辑页面
        :param request: 
        :param uid: 
        :return: 
        """
        return HttpResponse("change_view {0}".format(uid))


class AryaSite(object):
    def __init__(self):
        self._registy = {}

    def register(self,class_name,config_class):
        self._registy[class_name] = config_class(class_name,self)

    @property
    def urls(self):
        urlpatterns = [
            url(r'^login/$', self.login),
            url(r'^logout/$', self.logout),
        ]
        for model,config_class in self._registy.items():
            pattern = r'^{0}/{1}/'.format(model._meta.app_label, model._meta.model_name)
            urlpatterns.append(url(pattern,config_class.urls))
        # return urlpatterns,None,None
        # 指定名称空间名字为 arya
        return urlpatterns,None,'arya'

    def login(self, request):
        return HttpResponse("登录页面")
    def logout(self, request):
        return HttpResponse("登出页面")

# 基于Python文件导入特性实现的单例模式
site = AryaSite()