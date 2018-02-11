# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-18 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(verbose_name='班级(期)')),
                ('price', models.IntegerField(verbose_name='学费')),
                ('start_date', models.DateField(verbose_name='开班日期')),
                ('graduate_date', models.DateField(blank=True, null=True, verbose_name='结业日期')),
                ('description', models.CharField(blank=True, max_length=256, null=True, verbose_name='说明')),
            ],
            options={
                'verbose_name_plural': '开班记录表',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='课程名称')),
            ],
            options={
                'verbose_name_plural': '课程表',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='校区名称')),
            ],
            options={
                'verbose_name_plural': '校区表',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('email', models.EmailField(max_length=64, verbose_name='邮箱')),
            ],
            options={
                'verbose_name_plural': '员工信息表',
            },
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name_plural': '部门表'},
        ),
        migrations.AddField(
            model_name='userinfo',
            name='depart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Department', verbose_name='部门'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course', verbose_name='课程名称'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.School', verbose_name='校区'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='teachers',
            field=models.ManyToManyField(related_name='teach_classes', to='crm.UserInfo', verbose_name='任课老师'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='crm.UserInfo', verbose_name='班主任'),
        ),
    ]