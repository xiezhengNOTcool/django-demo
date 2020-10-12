from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status') # 展示内容
    list_filter = ('status', 'created', 'publish', 'author')        # 过滤器
    search_fields = ('title', 'body')                               # 搜索字段
    prepopulated_fields = {'slug': ('title',)}                      # 预生成字段
    raw_id_fields = ('author',)                                     
    date_hierarchy = 'publish'                                      # 日期层级
    ordering = ('status', 'publish')                                # 排序


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')