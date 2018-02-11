from arya.service import arya
from . import models
from django.forms import ModelForm,fields,widgets
from django.urls.resolvers import RegexURLPattern
from crm.arya import PermissionConfig as PermissionControl
from django.forms.models import ModelChoiceField


# 获取全部url
def get_all_url(patterns,prev,is_first=False, result=[]):
    if is_first:
        result.clear()
    for item in patterns:
        v = item._regex.strip("^$")
        if isinstance(item, RegexURLPattern):
            val = prev + v
            result.append((val,val,))
            # result.append(val)
        else:
            get_all_url(item.urlconf_name, prev + v)
    return result

class PermissionModelForm(ModelForm):
    # 也可以自己在这里添加扩展字段
    # phone = fields.CharField()
    # city = fields.ChoiceField(choices=[(1,"北京"),(2,"上海"),(3,"深圳")])
    # city = fields.MultipleChoiceField(choices=[(1,"北京"),(2,"上海"),(3,"深圳")])
    # 注意：这里扩展的字段名如果和 models.Customer 里面的字段名相同就会覆盖 models.Customer的字段，否则则会添加一个新的字段
    url = fields.ChoiceField()

    class Meta:
        model = models.Permission
        fields = '__all__'
        # fields =  ['title','url']
        # exclude = ['title']
        error_messages = {
            'title':{
                'required':'用户名不能为空！',
            },
            'url': {
                'required': '密码不能为空！',
            },
            'code': {
                'required': '密码不能为空！',
            },
            'group': {
                'invalid': '邮箱格式不正确！',
            },
        }
        # 也可以自定义前端标签样式
        # widgets = {
            # 'username': form_widgets.Textarea(attrs={'class': 'c1'})
            # 'username': form_widgets.Input(attrs={'class': 'some_class'})
        # }
    def __init__(self, *args, **kwargs):
        super(PermissionModelForm,self).__init__(*args, **kwargs)
        from crm_rbac_arya.urls import urlpatterns
        # 获取全部url，并以下拉框的形式显示在前端
        # 也可以进一步把未加入权限的url列出来，就需要查一遍数据库过滤下。
        self.fields['url'].choices = get_all_url(urlpatterns, '/', True)


    """
    # 在用Form的时候遇到过这个问题，即用户关联部门（外键关联）的时候：
    # depart = fields.ChoiceField(choices=models.Department.objects.values_list('id','title'))
    # 如果按照上面方式写，那么如果在部门表新添加数据后，则在用户关联的时候是无法显示新添加的部门信息的！！！只有程序重启才能获得新添加的数据！
    # 因为 depart 在 UserInfoForm 类里属于静态字段，在程序刚启动的时候会从上到下执行一遍，把当前数据加载到内存。
    # 所以采用了  __init__() 方法，每次都去数据库拿最新的数据
    手动挡：
        depart = fields.ChoiceField()
        def __init__(self, *args, **kwargs):
            super(UserInfoForm,self).__init__(*args, **kwargs)
            self.fields['depart'].choices = models.Department.objects.values_list('id','title')
    自动挡：
        from django.forms.models import ModelChoiceField
        depart = ModelChoiceField(queryset=models.Department.objects.all())
        # 这种方式虽然简单，但是在前端<option value=pk>object</option>，即显示的是object，还依赖model里的 __str__方法。
        
    上面说的是Form的问题，而ModelForm是Form和Model的结合体，也存在这个问题，所以这里也采用 __init__() 的方式
    """

class UserInfoConfig(PermissionControl, arya.AryaConfig):
    list_display = ['name',]

arya.site.register(models.UserInfo, UserInfoConfig)


class GroupConfig(PermissionControl, arya.AryaConfig):
    list_display = ['title','parent',]

arya.site.register(models.Group, GroupConfig)


class PermissionConfig(PermissionControl, arya.AryaConfig):
    list_display = ['title','url','group',]
    # 定制添加权限页面
    model_form_class = PermissionModelForm

arya.site.register(models.Permission, PermissionConfig)


class RoleConfig(PermissionControl, arya.AryaConfig):
    list_display = ['title',]

arya.site.register(models.Role, RoleConfig)