# postgres 全文搜索
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    # 有标签参数，根据标签筛选文章
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    # 分页器
    paginator = Paginator(object_list, 3) # 每页三篇文章 
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:              # 请求页面数不是整数，返回第一页 
        posts = paginator.page(1) 
    except EmptyPage:                     # 请求页面为空，返回最后一页
        posts = paginator.page(paginator.num_pages)
    
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})

                 
# def post_list(request):
#     posts = Post.published.all()
#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts})


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    # 正常评论
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':  # 收到评论表单
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 创建评论对象，暂不写入数据库
            new_comment = comment_form.save(commit=False) 
            # 修改评论post值为当前文章
            new_comment.post = post 
            # 写入数据库
            new_comment.save() 
    else:
        comment_form = CommentForm()

    # 利用相同标签数量排序筛选最相似文章
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    # 根据 id 得到文章
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':  # 分享表单提交
        form = EmailPostForm(request.POST)
        if form.is_valid():       # 表单通过验证
            cd = form.cleaned_data
            # 发送分享邮件
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends your read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']], fail_silently=False)
            sent = True
    else:
        form = EmailPostForm()

    return render(request,
                  'blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'sent': sent})

    
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A')\
                            + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.published.annotate(
            #                             rank=SearchRank(search_vector, search_query)
            #                         )\
            #                         .filter(rank__gte=0.3)\
            #                         .order_by('-rank')
            results = Post.published.annotate(
                          similarity=TrigramSimilarity('title', query),)\
                                    .filter(similarity__gt=0.1)\
                                    .order_by('-similarity')
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})