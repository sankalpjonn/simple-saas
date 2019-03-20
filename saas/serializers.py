from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from .models import Plan, Subscription, Business, BusinessTeamMember
from django.contrib.auth.models import User
from .exceptions import CustomValidation
from django.contrib.auth import authenticate

import helpers

class LoginSerializer(serializers.Serializer):
	email    = serializers.CharField(write_only=True)
	password = serializers.CharField(write_only=True)
	token    = serializers.CharField(read_only=True)


	def validate(self, data):
		data = super(LoginSerializer, self).validate(data)
		user = authenticate(username=data['email'], password=data['password'])
		if user:
			data['user'] = user
		else:
			raise serializers.ValidationError('Unable to login with provided credentials')
		return data

	def create(self, validated_data):
		token, _ = Token.objects.get_or_create(user=validated_data['user'])
		validated_data['token'] = token.key
		return validated_data

class BusinessSerializer(serializers.ModelSerializer):
	id                = serializers.IntegerField(required=False)
	api_key           = serializers.CharField(required=False)

	class Meta:
		model = Business
		fields = ('id', 'name', 'api_key')


class PlanSerializer(serializers.ModelSerializer):

	class Meta:
		model = Plan
		fields = '__all__'

class BusinessTeamMemberSerializer(serializers.ModelSerializer):
    business        = BusinessSerializer(read_only=True)
    first_name      = serializers.CharField(required=False, read_only=True)
    last_name       = serializers.CharField(required=False, read_only=True)
    email           = serializers.CharField(required=False, read_only=True)
    plan            = PlanSerializer(required=False, read_only=True)

    class Meta:
    	model  = BusinessTeamMember
    	fields = ('business', 'email', 'first_name', 'last_name', 'plan')

    def to_representation(self, obj):
        try:
            subscription = Subscription.objects.get(business=obj.business, is_active=True)
            obj.plan = subscription.plan
        except Subscription.DoesNotExist:
        	pass
        obj.first_name = obj.user.first_name
        obj.last_name = obj.user.last_name
        obj.email = obj.user.email
        return super(BusinessTeamMemberSerializer, self).to_representation(obj)

class SignupSerializer(serializers.Serializer):
    business   = BusinessSerializer(write_only=True)
    email      = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name  = serializers.CharField(write_only=True)
    password1  = serializers.CharField(write_only=True)
    password2  = serializers.CharField(write_only=True)
    token      = serializers.CharField(read_only=True)


    # used to determine create() or update()
    def save(self):
		if self.validated_data['business'].get('id'):
            # this calls update()
			self.instance = self.validated_data

        # this calls create()
		return super(SignupSerializer, self).save()

    def validate(self, data):
    	data = super(SignupSerializer, self).validate(data)
    	if data['password1'] != data['password2']:
    		raise serializers.ValidationError('Passwords do not match')

    	if User.objects.filter(username=data['email'], is_active=True).exists():
    		raise CustomValidation('Duplicate Email', data['email'], status_code=status.HTTP_409_CONFLICT)

    	return data

    def _send_welcome_mail(self):
        # send mail here
	    pass


    def update(self, instance, validated_data):
    	# user for the client to log into his business' dashboard
    	client_user_email = validated_data['email']
    	try:
    		client_user = User.objects.get(username=client_user_email)
    	except User.DoesNotExist:
    		raise serializers.ValidationError("this email was not invited")
    	client_user.is_active=True
        client_user.first_name = validated_data["first_name"]
        client_user.last_name = validated_data["last_name"]
    	client_user.set_password(validated_data['password1'])
    	client_user.save()

    	token, _ = Token.objects.get_or_create(user=client_user)
    	validated_data['token'] = token.key
    	return validated_data

    def create(self, validated_data):
    	# create business
    	business = Business.objects.create(**validated_data['business'])
    	validated_data['business'] = business

    	# create subscription for free trial
    	free_trial_plan, _ = Plan.objects.get_or_create(
            id=Plan.PLAN_FREE_TIER_ID,
            defaults = {
                "usd_price": 0,
                "name": "free trial",
                "description": "default plan attached to a new signup"
            }
        )
    	subscription = {
    		"business": business,
    		"plan": free_trial_plan,
    		"is_active": True,
    	}
    	Subscription.objects.create(**subscription)

    	# create more users here if required

    	# user for the client to log into his business' dashboard
    	client_user_email = validated_data['email']
    	client_user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            username=client_user_email,
            email=client_user_email,
            password=validated_data['password1'])
    	BusinessTeamMember.objects.create(
    		business= business,
    		user= client_user,
    		activation_key= helpers.generate_activation_key(),
    	)

    	self._send_welcome_mail()

    	validated_data['token'] = Token.objects.create(user=client_user).key
    	return validated_data

class ResetPasswordSerializer(serializers.Serializer):
    email          = serializers.EmailField(write_only=True)
    activation_key = serializers.CharField(read_only=True)

    def _send_password_reset_mail(self, activation_key):
        # TODO send activation mail here
        print "ACTIVATION KEY : {}".format(activation_key)

    def validate(self, data):
    	data = super(ResetPasswordSerializer, self).validate(data)
    	if not User.objects.filter(username=data['email']).exists():
    		raise serializers.ValidationError('This email does not exist in the system')
    	return data

    def create(self, validated_data):
    	business_team_member = BusinessTeamMember.objects.get(user=User.objects.get(username=validated_data['email']))
    	business_team_member.activation_key = helpers.generate_activation_key()
    	business_team_member.save()
    	self.business_team_member = business_team_member
    	self._send_password_reset_mail(business_team_member.activation_key)
    	validated_data['activation_key'] = business_team_member.activation_key
    	return validated_data

class ResetPasswordConfirmationSerializer(serializers.Serializer):
    activation_key = serializers.CharField(write_only=True)
    password1      = serializers.CharField(write_only=True)
    password2      = serializers.CharField(write_only=True)
    token          = serializers.CharField(read_only=True)

    def validate(self, data):
    	data = super(ResetPasswordConfirmationSerializer, self).validate(data)
    	if data['password1'] != data['password2']:
    		raise serializers.ValidationError('Passwords do not match')
    	if not BusinessTeamMember.objects.filter(activation_key=data['activation_key']).exists():
    		raise serializers.ValidationError('This activation key does not exist')
    	return data

    def create(self, validated_data):
    	user = BusinessTeamMember.objects.get(activation_key=validated_data['activation_key']).user
    	user.set_password(validated_data['password1'])
    	user.save()
    	validated_data['token'], _ = Token.objects.get_or_create(user=user)
	return validated_data


class InviteTeamMemberSerialiser(serializers.Serializer):
	email          = serializers.EmailField(write_only=True)
	no_email       = serializers.BooleanField(required=False)
	activation_key = serializers.CharField(read_only=True)

	def _send_invitation_email(self, email):
        # TODO: send email here
		pass

	def create(self, validated_data):
		self.user, _ = helpers.get_or_create_user(email=validated_data['email'])
		self.user.is_active = False
		self.user.save()
		self.business = self.context['request'].business
		self.business_team_member, _ = BusinessTeamMember.objects.get_or_create(
			user=self.user,
			business=self.business,
			defaults={
				'activation_key': helpers.generate_activation_key()
			}
		)
		if not validated_data.get('no_email'):
			self._send_invitation_email(validated_data['email'])

		validated_data['activation_key'] = self.business_team_member.activation_key
		return validated_data
