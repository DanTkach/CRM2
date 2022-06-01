from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from .models import *


class ClientForm(ModelForm):
	class Meta:
		model = Client
		fields = '__all__'
		exclude = ['balance']


class DateInput(forms.DateInput):
	input_type = 'date'


class ContractForm(ModelForm):
	class Meta:
		model = Contract
		fields = '__all__'
		exclude = ['status']
		widgets = {
			'date_created': DateInput()
		}


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']


class PaymentForm(ModelForm):
	class Meta:
		model = Payment
		fields = '__all__'
		exclude = ['principal_paid', 'interest_paid', 'penalties_paid', 'advance']
		widgets = {
			'date_paid': DateInput()
		}
