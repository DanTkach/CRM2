from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (ExportDocx, ExportDocx_Fide, ExportXlsx,
                    ExportDocxPaymentsMDL, ExportDocxChestionar, ExportDocx_Lien,
                    ExportDocx_LienAviz)

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),
    path('arrears/', views.arrears, name='arrears'),
    path('client/<str:pk_test>/', views.client, name="client"),
    path('new_client', views.createClient, name="createClient"),
    path('create_contract/<str:pk>/',
         views.createContract, name="create_contract"),
    path('update_contract/<str:pk>/',
         views.updateContract, name="update_contract"),
    path('view_contract/<str:pk>/', views.viewContract, name="view_contract"),
    path('download_contract/<str:pk>/',
         ExportDocx.as_view(), name="downloadContract"),
    path('download_fide_contract/<str:pk>/',
         ExportDocx_Fide.as_view(), name="downloadFideContract"),
    path('download_payments/<str:pk>/',
         ExportDocxPaymentsMDL.as_view(), name="download_payments"),
    path('download_chestionar/<str:pk>',
         ExportDocxChestionar.as_view(), name="download_chestionar"),
    path('download_gaj_contract/<str:pk>',
         ExportDocx_Lien.as_view(), name="download_gaj_contract"),
    path('download_gaj_aviz/<str:pk>',
         ExportDocx_LienAviz.as_view(), name="download_gaj_aviz"),

    path('update_client/<str:pk>/', views.updateClient, name="update_client"),
    path('delete_contract/<str:pk>/',
         views.deleteContract, name="delete_contract"),
    path('delete_client/<str:pk>/', views.deleteClient, name="delete_client"),

    path('create_payment/<str:pk>/', views.createPayment, name="create_payment"),
    path('delete_payment/<str:pk>/', views.deletePayment, name="delete_payment"),
    path('update_payment/<str:pk>/', views.updatePayment, name="update_payment"),

    path('download_statistics/', ExportXlsx.as_view(), name="download_statistics"),
    path('prognosis/<str:pk>/<str:pj>/<str:pl>/',
         views.prognosis, name="prognosis"),
    path('report/<str:pk>/<str:pj>/', views.report, name="report"),

    path('penalty_waive/<str:pk>/<str:pj>',
         views.createPenaltyWaive, name="penalty_waive"),
    path('interest_waive/<str:pk>/<str:pj>',
         views.createInterestWaive, name="interest_waive"),
    path('delete_p_waive/<str:pk>/<str:pj>/',
         views.deletePenaltyWaive, name="delete_p_waive"),
    path('delete_i_waive/<str:pk>/<str:pj>/',
         views.deleteInterestWaive, name="delete_i_waive"),
    path('waive_all_p/<str:pk>/', views.waiveAllPenalty, name="waive_all_p"),
    path('waive_all_i/<str:pk>/', views.waiveAllInterest, name="waive_all_i"),
    path('delete_all_p/<str:pk>/', views.deleteAllPenalty, name="delete_all_p"),
    path('delete_all_i/<str:pk>/', views.deleteAllInterest, name="delete_all_i"),

    path('create_guarantor/<str:pk>/',
         views.createGuarantor, name="create_guarantor"),
    path('delete_guarantor/<str:pk>/',
         views.deleteGuarantor, name="delete_guarantor"),
    path('update_guarantor/<str:pk>/',
         views.updateGuarantor, name="update_guarantor"),

    path('create_lienholder/<str:pk>/',
         views.createLienholder, name="create_lienholder"),
    path('delete_lienholder/<str:pk>/',
         views.deleteLienholder, name="delete_lienholder"),
    path('update_lienholder/<str:pk>/',
         views.updateLienholder, name="update_lienholder"),

    path('payments/', views.payments, name="payments"),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name="accounts/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="accounts/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="accounts/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="accounts/password_reset_done.html"),
         name="password_reset_complete"),

]

'''
1 - Submit email form                         //PasswordResetView.as_view()
2 - Email sent success message                //PasswordResetDoneView.as_view()
3 - Link to password Rest form in email       //PasswordResetConfirmView.as_view()
4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
'''
