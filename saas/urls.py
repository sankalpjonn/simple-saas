from django.contrib import admin
from django.conf.urls import url
from .views import LoginView, SignupView, ResetPasswordView, \
                   ResetPasswordConfirmationView, MeView, \
                   InviteTeamMemberView, PrefillSignupView

urlpatterns = [
    url(r'^login$', LoginView.as_view()),
    url(r'^signup$', SignupView.as_view()),
    url(r'^signup/prefill$', PrefillSignupView.as_view()),
    url(r'^passwd/reset$', ResetPasswordView.as_view()),
    url(r'^passwd/reset/cnfrm$', ResetPasswordConfirmationView.as_view()),
    url(r'^me$', MeView.as_view()),
    url(r'^invite$', InviteTeamMemberView.as_view()),
]
