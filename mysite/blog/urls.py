from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),                            # blog/
    path('tag/<slug:tag_slug>/',                                            # blog/tag/标签名
         views.post_list,
         name='post_list_by_tag',
    ),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',                   # blog/年/月/日/文章名
         views.post_detail,
         name='post_detail',
    ),
    path('<int:post_id>/share/', views.post_share, name='post_share'),      # blog/文章编号/share/
    path('feed/', LatestPostsFeed(), name='post_feed'),                     # blog/feed/
    path('search/', views.post_search, name='post_search'),                 # blog/search/
]