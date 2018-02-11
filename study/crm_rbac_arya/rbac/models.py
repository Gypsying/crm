from django.db import models

class Group(models.Model):
    """
    权限组表
    """
    title = models.CharField(max_length=32)
    parent = models.ForeignKey(to="Group",related_name="xxx",null=True,blank=True)
    is_group = models.BooleanField(verbose_name="是否是组",default=True)

    class Meta:
        verbose_name_plural = "权限组表"
    def __str__(self):
        return self.title

class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name='标题',max_length=32)
    url = models.CharField(verbose_name="含正则的URL",max_length=128)
    code = models.CharField(verbose_name="权限代号",max_length=16)
    # group = models.ForeignKey(verbose_name="权限组",to="Group")  # 把具体的权限分组管理，类似省市县
    group = models.ForeignKey(verbose_name="权限组",to="Group",limit_choices_to={'is_group':True})
    is_menu = models.BooleanField(verbose_name="是否是菜单") # 用来筛选出可以在左侧菜单展示的选项

    # 20171119 由于删除和编辑时 左侧菜单无法默认展开（无法保持展开状态）
    # 所以 在权限表增加一个字段：访问时，默认被选中的组内权限ID
    sibling_permission = models.ForeignKey(
        verbose_name="默认选中的组内权限ID",
        to="Permission",
        related_name="sibling_perm",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = "权限表"

    def __str__(self):
        return self.title

class UserInfo(models.Model):
    """
    用户表
    """
    # username = models.CharField(verbose_name="用户名",max_length=32)
    # password = models.CharField(verbose_name="密码",max_length=64)
    # email = models.EmailField(verbose_name="邮箱")

    # 在crm的UserInfo里存储username和password以及email信息，这里就存储一个真是的名称吧
    # crm.UserInfo 和 rbac.UserInfo 那个里面存储username和password都可以的
    name = models.CharField(verbose_name="真实名称",max_length=32)
    roles = models.ManyToManyField(verbose_name='具有所有角色',to="Role",blank=True)

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(verbose_name='角色名称',max_length=32)
    permissions = models.ManyToManyField(verbose_name="具有所有权限",to='Permission',blank=True)

    class Meta:
        verbose_name_plural = "角色表"

    def __str__(self):
        return self.title
