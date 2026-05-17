from django.urls import path
from . import views

urlpatterns = [
    path('load-more/', views.load_more_posts, name='load_more_posts'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('report/', views.report_content, name='report_content'),
]
