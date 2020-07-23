from taggit.models import Tag

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail
from django.db.models import Count

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    # 利用标签分类
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    # 分页器
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    # 评论
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 利用聚合函数对tag做操作得到推荐文章
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    # 默认页面为'GET'，也就是没有发送邮件 sent=False
    sent = False
    # 请求类型判断
    if request.method == 'POST':
        # 解析邮件表单
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # 生成邮件内容并发送
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{user} recommends you read {post}".format(
                user=cd['name'], 
                post=post.title)
            message = "Read {post} at {url}\n\n{user}'s comments: {comments}".format(
                post=post.title,
                url=post_url,
                user=cd['name'],
                comments=cd['comments'])
            send_mail(subject, message, 'admin@blog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 
                  "blog/post/share.html",
                  {"post": post,
                   "form": form,
                   "sent": sent})
                   