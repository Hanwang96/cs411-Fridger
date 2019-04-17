from django.urls import path

from . import views

app_name = 'fridge'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.signup, name='register'),
    path('new_user', views.newuser, name='new_user'),



    path('<int:r_id>/', views.detail, name='detail'),
    path('content', views.content, name='content'),
    path('mypage', views.myhistory, name='profile'),
    path('search', views.search, name='search'),

    path('modify_amount', views.edit, name='modify_amount'),

    path('add_food', views.add_food, name='add_food'),
    path('new_food', views.new_food, name='new_food'),
]

'''
# ex: /polls/5/
path('<int:question_id>/', views.detail, name='detail'),
# ex: /polls/5/results/
path('<int:question_id>/results/', views.results, name='results'),
# get argument and pass to view
# ex: /polls/5/vote/
path('<int:question_id>/vote/', views.vote, name='vote'),
'''