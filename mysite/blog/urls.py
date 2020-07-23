from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),                             # blog/
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),  # blog/tag/[tag]
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',                    # blog/yy/mm/dd/post
         views.post_detail, 
         name='post_detail'
    ),
    path('<int:post_id>/share/',                                             # blog/id/share
         views.post_share,
         name='post_share'
    ),
]