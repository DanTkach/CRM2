from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import GeneratePDF

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),
    path('arrears/', views.arrears, name='arrears'),
    path('arrears/active/', views.arrearsActive, name='arrears_active'),
    path('arrears/closed/', views.arrearsClosed, name='arrears_closed'),
    path('arrears/collection/', views.arrearsCollection, name='arrears_collection'),
    path('arrears/suing/', views.arrearsSuing, name='arrears_suing'),
    path('client/<str:pk_test>/', views.client, name="client"),
    path('new_client', views.createClient, name="createClient"),
    path('create_contract/<str:pk>/', views.createContract, name="create_contract"),
    path('update_contract/<str:pk>/', views.updateContract, name="update_contract"),
    path('view_contract/<str:pk>/', views.viewContract, name="view_contract"),
    path('download_contract/<str:pk>/', GeneratePDF.as_view(), name="downloadContract"),

    path('update_client/<str:pk>/', views.updateClient, name="update_client"),
    path('delete_contract/<str:pk>/', views.deleteContract, name="delete_contract"),
    path('delete_client/<str:pk>/', views.deleteClient, name="delete_client"),

    path('create_payment/<str:pk>/', views.createPayment, name="create_payment"),
    path('delete_payment/<str:pk>/', views.deletePayment, name="delete_payment"),

    path('penalty_waive/<str:pk>/<str:pj>', views.createPenaltyWaive, name="penalty_waive"),
    path('interest_waive/<str:pk>/<str:pj>', views.createInterestWaive, name="interest_waive"),
    path('delete_p_waive/<str:pk>/<str:pj>/', views.deletePenaltyWaive, name="delete_p_waive"),
    path('delete_i_waive/<str:pk>/<str:pj>/', views.deleteInterestWaive, name="delete_i_waive"),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_complete"),

]

'''
1 - Submit email form                         //PasswordResetView.as_view()
2 - Email sent success message                //PasswordResetDoneView.as_view()
3 - Link to password Rest form in email       //PasswordResetConfirmView.as_view()
4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
'''
