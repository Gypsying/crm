from django.shortcuts import HttpResponse,render,redirect
from django.conf.urls import url, include
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from ..utils.pager import Paginator
from copy import deepcopy
from django.db.models import ForeignKey, ManyToManyField
import functools
from types import FunctionType
from django.db.models import Q
from django.http.request import QueryDict

class FilterRow(object):
    """
    组合搜索项
    """
    def __init__(self, option, change_list, data_list, param_dict=None, is_choices=None):
        self.option = option
        self.change_list = change_list
        self.data_list = data_list
        self.param_dict = deepcopy(param_dict)
        self.param_dict._mutable = True
        self.is_choices = is_choices

    def __iter__(self):
        base_url = self.change_list.config.reverse_list_url
        tpl = "<a href='{0}' class='{1}'>{2}</a>"
        """
        点击 课程2 和 性别1 这两个条件进行筛选的情况下：
            self.option.name  分别是  consultant  course  gender
            self.param_dict   是     <QueryDict: {'gender': ['1'], 'course': ['2']}>
        """

        # 这里是给 全部btn 创建url链接
        if self.option.name in self.param_dict:
            # 注意这里需要先把option.name对应的item pop掉，再做 urlencode()操作！
            pop_value = self.param_dict.pop(self.option.name)
            url = "{0}?{1}".format(base_url, self.param_dict.urlencode())
            val = tpl.format(url, '', '全部')
            self.param_dict.setlist(self.option.name, pop_value)
        else:
            url = "{0}?{1}".format(base_url, self.param_dict.urlencode())
            val = tpl.format(url, 'active', '全部')

        # self.param_dict
        yield mark_safe("<div class='whole'>")
        yield mark_safe(val)
        yield mark_safe("</div>")

        yield mark_safe("<div class='others'>")
        for obj in self.data_list:
            param_dict = deepcopy(self.param_dict)
            if self.is_choices:
                # ((1, '男'), (2, '女'))
                pk = str(obj[0])
                text = obj[1]
            else:
                # url上要传递的值
                pk = self.option.val_func_name(obj) if self.option.val_func_name else obj.pk
                pk = str(pk)
                # a标签上显示的内容
                text = self.option.text_func_name(obj) if self.option.text_func_name else str(obj)

            exist = False
            if pk in param_dict.getlist(self.option.name):
                exist = True

            if self.option.is_multi:
                if exist:
                    values = param_dict.getlist(self.option.name)
                    values.remove(pk)
                    param_dict.setlist(self.option.name,values)
                else:
                    param_dict.appendlist(self.option.name, pk)
            else:
                param_dict[self.option.name] = pk
            url = "{0}?{1}".format(base_url, param_dict.urlencode())
            val = tpl.format(url, 'active' if exist else '', text)
            yield mark_safe(val)
        yield mark_safe("</div>")


class FilterOption(object):
    def __init__(self, field_or_func, condition=None, is_multi=False, text_func_name=None, val_func_name=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: 在Model中定义函数，显示文本名称，默认使用 str(对象)
        :param val_func_name:  在Model中定义函数，显示文本名称，默认使用 对象.pk
        """
        self.field_or_func = field_or_func
        self.condition = condition                  # 筛选条件
        self.is_multi = is_multi                    # 是否允许多选
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name

    @property
    def is_func(self):
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func

    @property
    def get_condition(self):
        if self.condition:
            return self.condition
        con = Q()
        return con


class ChangeList(object):
    """
    专门用来处理列表页面部分的代码逻辑，简化 AryaConfig.changelist_view()
    """
    def __init__(self,config,queryset):
        self.config = config
        self.list_display = config.get_list_display()
        self.show_add = config.get_show_add()
        self.add_url = config.reverse_add_url
        # 模糊搜索
        self.search_list = config.get_search_list()
        self.keyword = config.keyword
        self.actions = config.get_actions()

        # 分页相关
        current_page = config.request.GET.get('page',1)
        all_count = queryset.count()
        base_url = config.reverse_list_url
        per_page = config.per_page
        per_page_count = config.per_page_count

        # 用于首先模糊查找了下数据的情况下要保留原来的 ?keyword=xxx ，在这基础上再进行分页
        # 但是如果在这里修改query_params则会影响 request.GET ，所以这里要进行深拷贝
        # 注意：request.GET 不是字典类型，而是django自己的QueryDict类型
        query_params = deepcopy(config.request.GET)
        query_params._mutable = True

        pager = Paginator(all_count,current_page,base_url,per_page,per_page_count,query_params)
        self.queryset = queryset[pager.start:pager.end]
        self.page_html = pager.page_html

        # 组合筛选
        self.list_filter = config.get_list_filter()


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
    def table_header(self):
        for str_or_func in self.list_display:
            if isinstance(str_or_func, str):
                val = self.config.model._meta.get_field(str_or_func).verbose_name
            else:
                val = str_or_func(self.config, is_header=True)
            yield val

    # 获取表内容
    # def table_body(self):
    #     table_data = []
    #     for row in self.queryset:
    #         if not self.list_display:
    #             # 用列表把对象做成列表集合是为了兼容有list_display的情况在前端展示（前端用2层循环展示）
    #             table_data.append([row, ])
    #         else:
    #             tmp = []
    #             for str_or_func in self.list_display:
    #                 if isinstance(str_or_func, str):
    #                     # 如果是字符串则通过反射取值
    #                     tmp.append(getattr(row, str_or_func))
    #                 else:
    #                     # 否则就是函数，获取函数执行的结果
    #                     tmp.append(str_or_func(self.config, row))
    #             table_data.append(tmp)
    #     return table_data
    def table_body(self):
        for row in self.queryset:
            if not self.list_display:
                # 用列表把对象做成列表集合是为了兼容有list_display的情况在前端展示（前端用2层循环展示）
                yield [row, ]
            else:
                tmp = []
                for str_or_func in self.list_display:
                    if isinstance(str_or_func, str):
                        # 如果是字符串则通过反射取值
                        tmp.append(getattr(row, str_or_func))
                    else:
                        # 否则就是函数，获取函数执行的结果
                        tmp.append(str_or_func(self.config, row))
                yield tmp

    # 定制批量操作的actions
    def action_options(self):
        options = []
        for func in self.actions:
            tmp = {'value':func.__name__, 'text':func.text}
            options.append(tmp)
        return options

    # 定制组合筛选
    def gen_list_filter(self):
        for option in self.list_filter:
            if option.is_func:
                data_list = option.field_or_func(self.config, self, option)
            else:
                _field = self.config.model._meta.get_field(option.field_or_func)
                """
                option.field_or_func   course                           咨询的课程
                _field                 crm.Customer.course              type  <class 'django.db.models.fields.related.ManyToManyField'>
                _field.rel             <ManyToManyRel: crm.customer>    type  <class 'django.db.models.fields.reverse_related.ManyToManyRel'>

                option.field_or_func   consultant                       课程顾问
                _field                 crm.Customer.consultant          type  <class 'django.db.models.fields.related.ForeignKey'>
                _field.rel             <ManyToOneRel: crm.customer>     type  <class 'django.db.models.fields.reverse_related.ManyToOneRel'>
                """
                if isinstance(_field, ForeignKey):
                    data_list = FilterRow(option, self, _field.rel.model.objects.filter(option.get_condition),
                                          self.config.request.GET)
                elif isinstance(_field, ManyToManyField):
                    data_list = FilterRow(option, self, _field.rel.model.objects.filter(option.get_condition),
                                          self.config.request.GET)
                else:
                    # print(_field.choices) # ((1, '男'), (2, '女'))
                    data_list = FilterRow(option, self, _field.choices, self.config.request.GET, is_choices=True)
            yield data_list

    def add_html(self):
        """
        添加按钮
        :return: 
        """
        add_html = mark_safe('<a class="btn btn-primary" href="%s">添加</a>' % (self.config.add_url_params,))
        return add_html

    def search_attr(self):
        val = self.config.request.GET.get(self.keyword)
        return {"value": val, 'name': self.keyword}


class AryaConfig(object):

    # 借助继承特性，实现定制列展示
    list_display = []

    # 定制是否显示添加按钮
    show_add = False
    def get_show_add(self):
        return self.show_add

    # 使用ModelForm
    model_form_class = None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        class DynamicModelForm(ModelForm):
            class Meta:
                model = self.model
                fields = '__all__'
        return DynamicModelForm
    """
    也可以使用 type 来生成
    def get_model_form_class(self):
        model_form_cls = self.model_form
        if not model_form_cls:
            _meta = type('Meta', (object,), {'model': self.model, "fields": "__all__"})
            model_form_cls = type('DynamicModelForm', (ModelForm,), {'Meta': _meta})
        return model_form_cls
    """

    # 分页相关配置
    per_page = 10
    per_page_count = 11

    # 定制actions，即结合checkbox进行批量操作
    actions = []
    def get_actions(self):
        result = []
        result.extend(self.actions)
        return result

    # 模糊搜索字段列表 (默认不支持搜索)
    search_list = []
    def get_search_list(self):
        result = []
        result.extend(self.search_list)
        return result

    @property
    def get_search_condition(self):
        con = Q()
        con.connector = "OR"
        # 加入搜索关键字是 kk, 并且如果我们在search_list里规定的只有 qq 和 name 这俩字段可以提供搜索条件
        # 那么 kk 这个关键字要么在 name里，要么在qq这个字段里，二者之间是 或 的关系
        val = self.request.GET.get(self.keyword)
        if not val:
            return con
        # ['qq','name']                         精确搜索
        # ['qq__contains','name__contains']     模糊搜索
        field_list = self.get_search_list()
        for field in field_list:
            field = "{0}__contains".format(field)
            con.children.append((field,val))
        return con

    @property
    def get_search_condition2(self):
        '''
        search_list = [
            {'key': 'qq', 'type': None},
            {'key': 'name', 'type': None},
            {'key': 'course__name', 'type': None},
        ]
        '''
        # condition = {}
        # keyword = request.GET.get('keyword')
        # search_list = self.get_search_list()
        # if keyword and search_list:
        #     # ['username','email','ut',]
        #     for field in search_list:
        #         condition[field] = keyword
        # condition = {
        #     'username':keyword,
        #     'email':keyword,
        #     'ut':keyword,
        # }
        # 这样去 filter(**condition) 过滤的时候是按照 且 关系过滤， 这样不太好，应该改成 或 关系过滤
        # 即 Django里的 Q 查询 :  from django.db.models import Q
        # queryset = self.model.objects.all()
        # queryset = self.model.objects.filter(**condition)
        # 增加这个属性，用于在ChangeList类里获取到查询的关键字（即通过self参数把request传递给ChangeList）
        condition = Q()
        condition.connector = "OR"
        keyword = self.request.GET.get(self.keyword)
        if not keyword:
            return condition
        search_list = self.get_search_list()
        for field_dict in search_list:
            field = "{0}__contains".format(field_dict.get('key'))
            field_type = field_dict.get('type')
            if field_type:
                try:
                    keyword = field_type(keyword)
                except Exception as e:
                    continue
            condition.children.append((field, keyword))
        return condition

    """定制查询组合条件"""
    list_filter = []
    def get_list_filter(self):
        return self.list_filter

    @property
    def get_list_filter_condition(self):
        # 获取model的字段，FK，choice，但是没有多对多的字段
        # fields1 = [obj.name for obj in self.model._meta.fields]
        # 只获取获取多对多的字段
        # fields2 = [obj.name for obj in self.model._meta.many_to_many]
        # 还包含了反向关联字段
        fields3 = [obj.name for obj in self.model._meta._get_fields()]
        """
        ['internal_referral', 'consultrecord', 'paymentrecord', 'student', 'id', 'qq', \
        'name', 'gender', 'education', 'graduation_school', 'major', 'experience', 'work_status', \
        'company', 'salary', 'source', 'referral_from', 'status', 'consultant', 'date', 'last_consult_date', 'course']
        """
        # fields = dir(self.model._meta)
        """
        ['FORWARD_PROPERTIES', 'REVERSE_PROPERTIES', '__class__', '__delattr__', '__dict__', '__dir__', \
        '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', \
        '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', \
        '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_expire_cache', '_forward_fields_map', \
        '_get_fields', '_get_fields_cache', '_ordering_clash', '_populate_directed_relation_graph', '_prepare', \
        '_property_names', '_relation_tree', 'abstract', 'add_field', 'add_manager', 'app_config', 'app_label', 'apps', \
        'auto_created', 'auto_field', 'base_manager', 'base_manager_name', 'can_migrate', 'concrete_fields', 'concrete_model', \
        'contribute_to_class', 'db_table', 'db_tablespace', 'default_apps', 'default_manager', 'default_manager_name', \
        'default_permissions', 'default_related_name', 'fields', 'fields_map', 'get_ancestor_link', 'get_base_chain', \
        'get_field', 'get_fields', 'get_latest_by', 'get_parent_list', 'get_path_from_parent', 'get_path_to_parent', \
        'has_auto_field', 'index_together', 'indexes', 'installed', 'label', 'label_lower', 'local_concrete_fields', \
        'local_fields', 'local_managers', 'local_many_to_many', 'managed', 'manager_inheritance_from_future', 'managers', \
        'managers_map', 'many_to_many', 'model', 'model_name', 'object_name', 'order_with_respect_to', 'ordering', \
        'original_attrs', 'parents', 'permissions', 'pk', 'private_fields', 'proxy', 'proxy_for_model', 'related_fkey_lookups', \
        'related_objects', 'required_db_features', 'required_db_vendor', 'select_on_save', 'setup_pk', 'setup_proxy', \
        'swappable', 'swapped', 'unique_together', 'verbose_name', 'verbose_name_plural', 'verbose_name_raw', 'virtual_fields']
        """

        # 去请求URL中获取参数
        # 根据参数生成条件
        con = {}
        params = self.request.GET
        # self.request.GET                    <QueryDict: {'gender': ['1'], 'course': ['1', '2']}>
        for k in params:
            # 判断k是否在数据库字段支持
            if k not in fields3:
                continue
            v = params.getlist(k)
            k = "{0}__in".format(k)
            con[k] = v
        """
        比如按照课程2和性别1这俩条件进行筛选的时候:
        {'gender__in': ['1'], 'course__in': ['2']}
        并且课程可以多选

        注意：这里课程之间是 或 的关系，即如果一个客户只咨询了课程1，但是筛选条件是 课程1和课程2，这种情况下，当前客户也会被筛选出来，
             尽管该用户并没有咨询课程2

             <QueryDict: {'gender': ['2'], 'course': ['1', '2']}>
             {'course__in': ['1', '2'], 'gender__in': ['2']}
        """
        return con

    def __init__(self, model, arya_site):
        self.model = model
        self.arya_site = arya_site
        self.app_label = model._meta.app_label
        self.model_name = model._meta.model_name
        self.change_filter_name = "_change_filter"
        self.keyword = 'keyword'
        self.request = None

    # 定制 编辑 按钮
    def row_edit(self, row=None, is_header=None):
        if is_header:
            return "编辑"
        # 反向生成URL
        edit_a = mark_safe("<a href='{0}?{1}'>编辑</a>".format(self.reverse_edit_url(row.id), self.back_url_param))
        return edit_a

    # 定制 删除 按钮
    def row_del(self, row=None, is_header=None):
        if is_header:
            return "删除"
        # 反向生成URL
        del_a = mark_safe("<a href='{0}?{1}'>删除</a>".format(self.reverse_del_url(row.id), self.back_url_param))
        return del_a

    # 定制 checkbox
    def check_box(self, row=None, is_header=None):
        if is_header:
            return "选项"
        checkbox = mark_safe("<input type='checkbox' name='item_id' value='{0}' />".format(row.id))
        return checkbox

    def get_list_display(self):
        result = []
        result.extend(self.list_display)
        # 如果有编辑权限
        """
        注意这里的参数不是方法self.row_edit 而是函数AryaConfig.row_edit
            class Foo(object):
                def func(self):
                    print('方法')

            方法和函数的区别：
                # - 如果被对象调用，则self不用传值
                    # obj = Foo()
                    # obj.func()

                # - 如果被类  调用，则self需要主动传值
                    # obj = Foo()
                    # Foo.func(obj)
        """
        result.append(AryaConfig.row_edit)
        # 如果有删除权限
        result.append(AryaConfig.row_del)
        # 加上checkbox
        result.insert(0, AryaConfig.check_box)
        return result


    # 装饰器：给 changelist_view add_view delete_view change_view 增加 self.request = request
    # 这样就不用在每个view里都写一遍 self.request = request
    # 每次请求进来记录下这个request，这样就能拿到rbac请求验证中间里面的permission_code_list
    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)
        return inner

    def get_urls(self):
        app_model_name = self.model._meta.app_label,self.model._meta.model_name
        urlpatterns = [
            url(r'^$', self.wrapper(self.changelist_view), name='%s_%s_list' % app_model_name),
            url(r'^add/$', self.wrapper(self.add_view), name='%s_%s_add' % app_model_name),
            url(r'^(.+)/delete/$', self.wrapper(self.delete_view), name='%s_%s_delete' % app_model_name),
            url(r'^(.+)/change/$', self.wrapper(self.change_view), name='%s_%s_change' % app_model_name)
        ]
        urlpatterns += self.extra_urls()
        return urlpatterns

    def extra_urls(self):
        """
        扩展URL预留的钩子函数
        :return:
        """
        return []

    @property
    def urls(self):
        return self.get_urls(), None, None

    def changelist_view(self, request):
        """
        列表页面
        :param request: 
        :return: 
        """
        # 执行批量actions，比如批量删除
        if 'POST' == request.method:
            func_name = request.POST.get('select_action')
            if func_name:
                # 通过反射获取要批量执行的函数对象
                func = getattr(self, func_name)
                func(request)

        '''先过滤组合搜索，然后过滤模糊搜索，最后去重拿到最后结果'''
        queryset = self.model.objects.filter(**self.get_list_filter_condition).filter(self.get_search_condition2).distinct()
        cl = ChangeList(self,queryset)
        return render(request,'arya/item_list.html',{'cl':cl})

    def add_view(self, request):
        """
        添加页面
        :param request: 
        :return: 
        """
        model_form_cls = self.get_model_form_class()
        if 'GET' == request.method:
            # 返回对应的添加页面
            form = model_form_cls()
            return render(request,'arya/add_view.html',{'form':form})
        else:
            # 保存
            form = model_form_cls(data=request.POST)
            if form.is_valid():
                form.save()
                # 获取反向生成URL，跳转回列表页面
                return redirect(self.list_url_with_params)
            return render(request,'arya/add_view.html',{'form':form})

    def delete_view(self, request, uid):
        """
        删除页面
        :param request: 
        :param uid: 
        :return: 
        """
        obj = self.model.objects.filter(id=uid).first()
        if not obj:
            return redirect(self.reverse_list_url)
        if 'GET' == request.method:
            return render(request,'arya/delete_view.html')
        else:
            obj.delete()
            return redirect(self.list_url_with_params)

    def change_view(self, request, uid):
        """
        编辑页面
        :param request: 
        :param uid: 
        :return: 
        """
        obj = self.model.objects.filter(id=uid).first()
        if not obj:
            return redirect(self.reverse_list_url)
        model_form_cls = self.get_model_form_class()
        if 'GET' == request.method:
            # 在input框里显示原来的值
            form = model_form_cls(instance=obj)
            return render(request,'arya/change_view.html',{'form':form})
        else:
            # 更新某个实例
            form = model_form_cls(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.list_url_with_params)
            return render(request, 'arya/change_view.html', {'form': form})


    # 反向生成url相关
    @property
    def back_url_param(self):
        '''反向生成base_url之外的其他参数，用于保留之前的操作'''
        query = QueryDict(mutable=True)
        if self.request.GET:
            """
            self.request.GET                    <QueryDict: {'gender': ['1'], 'course': ['1', '2']}>
            self.request.GET.urlencode()        gender=1&course=1&course=2
            query.urlencode()                   _change_filter=gender%3D1%26course%3D1%26course%3D2

            对应的编辑按钮的地址：     /arya/crm/customer/obj.id/change/?_change_filter=gender%3D1%26course%3D1%26course%3D2
            """
            query[self.change_filter_name] = self.request.GET.urlencode()  # gender=2&course=2&course=1
        return query.urlencode()

    def reverse_del_url(self, pk):
        '''反向生成删除按钮对应的基础URL（不带额外参数的），需要传入obj的id'''
        base_del_url = reverse(viewname='{0}:{1}_{2}_delete'.format(self.arya_site.namespace, self.app_label, self.model_name),args=(pk,))
        return base_del_url

    def reverse_edit_url(self, pk):
        '''反向生成编辑按钮对应的基础URL（不带额外参数的），需要传入obj的id'''
        base_edit_url = reverse(viewname='{0}:{1}_{2}_change'.format(self.arya_site.namespace, self.app_label, self.model_name),args=(pk,))
        return base_edit_url

    @property
    def reverse_add_url(self):
        '''反向生成添加按钮对应的基础URL（不带额外参数的）'''
        base_add_url = reverse(viewname='{0}:{1}_{2}_add'.format(self.arya_site.namespace, self.app_label, self.model_name))
        return base_add_url

    @property
    def reverse_list_url(self):
        '''反向生成列表页面对应的基础URL（不带额外参数的）'''
        base_list_url = reverse(viewname='{0}:{1}_{2}_list'.format(self.arya_site.namespace, self.app_label, self.model_name))
        return base_list_url

    @property
    def list_url_with_params(self):
        '''反向生成列表页面对应的URL（带了之前用户操作的一些参数）'''
        base_url = self.reverse_list_url
        query = self.request.GET.get(self.change_filter_name)
        return "{0}?{1}".format(base_url, query if query else "")

    @property
    def add_url_params(self):
        base_url = self.reverse_add_url
        if self.request.GET:
            return base_url
        else:
            query = QueryDict(mutable=True)
            query[self.change_filter_name] = self.request.GET.urlencode()
            return "{0}?{1}".format(base_url, query.urlencode())


class AryaSite(object):
    def __init__(self, name='arya'):
        self.name = name
        self.namespace = name
        self._registy = {}

    def register(self,class_name,config_class):
        self._registy[class_name] = config_class(class_name,self)

    def get_urls(self):
        urlpatterns = [
            url(r'^login/$', self.login),
            url(r'^logout/$', self.logout),
        ]
        for model, config_class in self._registy.items():
            pattern = r'^{0}/{1}/'.format(model._meta.app_label, model._meta.model_name)
            urlpatterns.append(url(pattern, config_class.urls))
            # return urlpatterns,None,None
            # 指定名称空间名字为 arya
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(),self.name,self.namespace

    def login(self, request):
        return HttpResponse("登录页面")
    def logout(self, request):
        return HttpResponse("登出页面")

# 基于Python文件导入特性实现的单例模式
site = AryaSite()