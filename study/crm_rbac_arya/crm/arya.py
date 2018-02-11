from arya.service import arya
from . import models
from django.forms import ModelForm,fields
from django.forms import widgets as form_widgets
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse,render,redirect
from django.db.models import Q

class UserInfoModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'
        # fields =  ['username','email']
        # exclude = ['username']
        error_messages = {
            'username':{
                'required':'用户名不能为空！',
            },
            'password': {
                'required': '密码不能为空！',
            },
            'email': {
                'required': '邮箱地址不能为空！',
                'invalid': '邮箱格式不正确！',
            },
            'depart':{
                'required': '所属部分不能为空！',
            }
        }
        # 也可以自定义前端标签样式
        # widgets = {
            # 'username': form_widgets.Textarea(attrs={'class': 'c1'})
            # 'username': form_widgets.Input(attrs={'class': 'some_class'})
        # }

class ClassListModelForm(ModelForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'
        error_messages = {
            'school':{
                'required':'校区不能为空！',
            },
            'course': {
                'required': '课程不能为空！',
            },
            'semester': {
                'required': '学期不能为空！',
            },
            'price': {
                'required': '价格不能为空！',
            },
            'start_date': {
                'required': '开班日期不能为空！',
            },
            'teachers': {
                'required': '任课老师不能为空！',
            },
            'tutor':{
                'required': '班主任不能为空！',
            }
        }
        # 也可以自定义前端标签样式
        widgets = {
            'description': form_widgets.Textarea(attrs={'class': 'desc',})
        }

class CustomerModelForm(ModelForm):

    # 也可以自己在这里添加一个字段
    # phone = fields.CharField()
    # city = fields.ChoiceField(choices=[(1,"北京"),(2,"上海"),(3,"深圳")])
    # 注意：这里扩展的字段名如果和 models.Customer 里面的字段名相同就会覆盖 models.Customer的字段，否则则会添加一个新的字段

    class Meta:
        model = models.Customer
        fields = '__all__'
        error_messages = {
            'qq':{
                'required':'qq不能为空！',
            },
            'name': {
                'required': '客户姓名不能为空！',
            },
            'gender': {
                'required': '性别不能为空！',
            },
            'source': {
                'required': '客户来源不能为空！',
            },
            'course': {
                'required': '咨询的课程不能为空！',
            },
            'status': {
                'required': '客户状态不能为空！',
            },
            'consultant':{
                'required': '课程顾问不能为空！',
            }
        }


class PermissionConfig(object):
    # 重写 AryaConfig 里面的方法，判断是否在前端显示 添加 button
    def get_show_add(self):
    #     因为在AryaConfig里面的增删改查views里面做了  self.request = request
        permission_code_list = self.request.permission_code_list
        if 'add' in permission_code_list:
            return True

    # 重写 AryaConfig 里面的方法，判断是否在前端显示 编辑 和 删除 button
    def get_list_display(self):
        # 因为在AryaConfig里面的增删改查views里面做了  self.request = request
        permission_code_list = self.request.permission_code_list
        result = []
        result.extend(self.list_display)
        # 如果有编辑权限
        # 注意这里的参数不是方法self.row_edit 而是函数AryaConfig.row_edit
        if 'edit' in permission_code_list:
            result.append(arya.AryaConfig.row_edit)
        # 如果有删除权限
        if 'del' in permission_code_list:
            result.append(arya.AryaConfig.row_del)
        # 加上checkbox
        result.insert(0, arya.AryaConfig.check_box)
        return result

    # def get_list_display(self):
    #     result = []
    #     result.extend(self.list_display)
    #     result.append(arya.AryaConfig.row_edit)
    #     result.append(arya.AryaConfig.row_del)
    #     加上checkbox
        # result.insert(0, arya.AryaConfig.check_box)
        # return result

class DepartmentConfig(PermissionConfig,arya.AryaConfig):
    list_display = ['id','title',]

arya.site.register(models.Department, DepartmentConfig)


class UserInfoConfig(PermissionConfig,arya.AryaConfig):
    list_display = ['username','email','depart',]
    # 定制自己的ModelForm
    model_form_class = UserInfoModelForm

arya.site.register(models.UserInfo, UserInfoConfig)


class CourseConfig(PermissionConfig,arya.AryaConfig):
    list_display = ['id','name',]

arya.site.register(models.Course, CourseConfig)


class SchoolConfig(PermissionConfig,arya.AryaConfig):
    list_display = ['id','title',]

arya.site.register(models.School, SchoolConfig)


class ClassListConfig(PermissionConfig,arya.AryaConfig):
    # 定制显示任课教师，因为有多个任课教师
    def show_teachers(self, row=None, is_header=None):
        if is_header:
            return "任课教师"
        teacher_obj_list = row.teachers.all()
        teachers = [teacher.username for teacher in teacher_obj_list]
        return ','.join(teachers)
    # 定制显示的列
    list_display = ['school','course','semester','price','start_date',show_teachers,'tutor']
    # 定制自己的ModelForm
    model_form_class = ClassListModelForm
    # 定制搜索功能
    # search_list = ['school__title__contains','course__name_contains','semester',]
    # 因为semester是数字，在Q查询的时候出现和字符串比较导致报错，所以这里要处理下
    search_list = [
        {'key':'semester','type':int},
        {'key':'course__name','type':None},
        {'key':'school__title','type':None},
    ]

arya.site.register(models.ClassList, ClassListConfig)


class CustomerConfig(PermissionConfig, arya.AryaConfig):
    def show_gender(self, row=None, is_header=None):
        if is_header:
            return "性别"
        # gender_choices = ((1, '男'), (2, '女'))
        # gender = models.SmallIntegerField(verbose_name='性别', choices=gender_choices)
        # obj.get_字段_display() 这个方法可以拿到 数字在元组里对应的描述
        return row.get_gender_display()
    def show_education(self, row=None, is_header=None):
        if is_header:
            return "学历"
        # obj.get_字段_display() 这个方法可以拿到 数字在元组里对应的描述
        return row.get_education_display()
    def show_work_status(self, row=None, is_header=None):
        if is_header:
            return "职业状态"
        # obj.get_字段_display() 这个方法可以拿到 数字在元组里对应的描述
        return row.get_work_status_display()
    def show_experience(self, row=None, is_header=None):
        if is_header:
            return "工作经验"
        # obj.get_字段_display() 这个方法可以拿到 数字在元组里对应的描述
        return row.get_experience_display()
    def show_course(self, row=None, is_header=None):
        if is_header:
            return "咨询的课程"
        tpl = "<span style='display:inline-block;padding:3px;margin:2px;border:1px solid #ddd;'>{0}</span>"
        course_obj_list = row.course.all()
        courses = [tpl.format(course.name) for course in course_obj_list]
        return mark_safe(' '.join(courses))

    def show_record(self, row=None, is_header=None):
        if is_header:
            return "跟进记录"
        return mark_safe("<a href='xxx/{0}'>查看跟进记录</a>".format(row.id))

    list_display = ['qq','name',show_gender,show_course,'consultant',show_record]

    model_form_class = CustomerModelForm

    # 定制批量删除的actions
    def multi_delete(self, request):
        item_list = request.POST.getlist('item_id')
        # 注意：filter(id__in=item_list) 这样写就不用使用for循环了
        self.model.objects.filter(id__in=item_list).delete()

    multi_delete.text = "批量删除"  # 可以这样赋值
    actions = [multi_delete,]

    # search_list = [
    #     {'key': 'qq__contains', 'type': None},
    #     {'key': 'name__contains', 'type': None},
    #     {'key': 'course__name__contains', 'type': None},
    # ]
    search_list = [
        {'key': 'qq', 'type': None},
        {'key': 'name', 'type': None},
        {'key': 'course__name', 'type': None},
    ]

    list_filter = [
        arya.FilterOption('consultant', condition=Q(depart_id=1)),
        arya.FilterOption('course', is_multi=True),
        arya.FilterOption('gender'),
    ]

arya.site.register(models.Customer, CustomerConfig)


class StudentConfig(PermissionConfig, arya.AryaConfig):

    def show_class_list(self, row=None, is_header=None):
        if is_header:
            return "已报班级"
        class_obj_list = row.class_list.all()
        classes = ["{0}({1}期)".format(class_obj.course.name, class_obj.semester) for class_obj in class_obj_list]
        return ','.join(classes)

    list_display = ['customer','username',show_class_list,]

    # 因为student是从customer转过来的，所以在save之前需要把customer里顾客的状态改为【已报名】
    # 所以在这里重写add_view逻辑
    def add_view(self, request):
        model_form_cls = self.get_model_form_class()
        if 'GET' == request.method:
            # 返回对应的添加页面
            form = model_form_cls()
            return render(request,'arya/add_view.html',{'form':form})
        else:
            # 保存
            form = model_form_cls(data=request.POST)
            customer_id = request.POST.get('customer')
            customer_obj = models.Customer.objects.filter(id=customer_id).first()
            customer_obj.status = 1
            customer_obj.save()
            if form.is_valid():
                form.save()
                # 获取反向生成URL，跳转回列表页面
                return redirect(self.reverse_list_url())
            return render(request,'arya/add_view.html',{'form':form})

arya.site.register(models.Student, StudentConfig)