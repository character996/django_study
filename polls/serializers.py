# 创建序列化器，把木星转换成需要返回的json、xml类型数据。
from rest_framework import serializers
from .models import Teacher, Subject


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ('subject', )


class SubjectSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('no', 'name')