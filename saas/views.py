from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework import parsers, serializers
from .serializers import LoginSerializer, BusinessTeamMemberSerializer, ResetPasswordSerializer, \
                         SignupSerializer, ResetPasswordSerializer, ResetPasswordConfirmationSerializer, \
                         InviteTeamMemberSerialiser
from .permissions import IsBusiness
from .models import BusinessTeamMember, Subscription

class BusinessAPIView(APIView):
    """
    This view must by inherited by any view that should be accessed only
    if the user making the request is part of a business that is registered
    """

    def initial(self, request, *args, **kwargs):
		ret = super(BusinessAPIView, self).initial(request, *args, **kwargs)
		if not request.user.is_anonymous():
			try:
				team_member = BusinessTeamMember.objects.get(user=request.user)
				request.business = team_member.business
			except BusinessTeamMember.DoesNotExist:
				raise MemberDoesNotExist()
		return ret


class SubscriptionAPIView(BusinessAPIView):
    """
    This view must be inherited by any view that should be accessed only if
    there is an active subscription present for a business to which
    the user that is making the api call belongs to
    """
    def initial(self, request, *args, **kwargs):
		ret = super(SubscriptionAPIView, self).initial(request, *args, **kwargs)
		try:
			subscription = Subscription.objects.get(business=request.business, is_active=True)
			request.subscription = subscription
		except Subscription.DoesNotExist:
			raise NoActiveSubscriptionFound()
		return ret


class LoginView(CreateAPIView):
	serializer_class = LoginSerializer
	parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)


class PrefillSignupView(RetrieveAPIView):
	"""
	If signup form is accessed via an activation link, form will be prefilled with some information.
	To retrieve that information, use this API with the activation key
	"""
	serializer_class = BusinessTeamMemberSerializer

	def get_object(self):
		key = self.request.query_params.get('key', None)
		try:
			return BusinessTeamMember.objects.get(activation_key=key)
		except BusinessTeamMember.DoesNotExist:
			raise serializers.ValidationError('Activation key not found')

class SignupView(CreateAPIView):
	serializer_class = SignupSerializer
	parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)


class ResetPasswordView(CreateAPIView):
	"""
	Sending email to a team member with an activation key that will be used to reset password
	"""

	serializer_class = ResetPasswordSerializer
	parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)


class ResetPasswordConfirmationView(CreateAPIView):
	"""
	Using the activation key sent in the mail, password will be reset using new password
	"""

	serializer_class = ResetPasswordConfirmationSerializer
	parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)

class MeView(RetrieveAPIView, BusinessAPIView):
	"""
	Returns information about the user to which this auth token belongs to and the corresponding business.
	Can be used in settings
	"""

	serializer_class = BusinessTeamMemberSerializer
	permission_classes = [IsBusiness]

	def get_object(self):
		return BusinessTeamMember.objects.get(user=self.request.user, business=self.request.business)

class InviteTeamMemberView(CreateAPIView, SubscriptionAPIView):
    """
    Sending invitation to a team member to join SessionFox
    """

    permission_classes = [IsBusiness]
    serializer_class   = InviteTeamMemberSerialiser
