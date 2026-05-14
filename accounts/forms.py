from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Client, Contract, Payment, Prognosis, Fidejusor, Arrears, Report, Gajist


class DateInput(forms.DateInput):
    input_type = 'date'


class PhysicalClientForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = [
            'company_name',
            'jur_address',
            'administrator',
            'registration_date',
            'registration_nr',
        ]
        widgets = {
            'id_card_date': DateInput(),
            'birth_date': DateInput()
        }


class JuridicalClientForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = [
            'first_name',
            'last_name',
            'gender',
            'id_card_nr',
            'id_card_office',
            'id_card_date',
            'birth_date',
        ]
        widgets = {
            'registration_date': DateInput()
        }


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        exclude = ['comments']
        widgets = {
            'date_created': DateInput(),
            'date_closed': DateInput()
        }


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        widgets = {
            'date_paid': DateInput()
        }


class GuarantorForm(ModelForm):
    class Meta:
        model = Fidejusor
        fields = '__all__'
        exclude = []
        widgets = {
            'id_card_date': DateInput(),
            'birth_date': DateInput()
        }


class GajistForm(ModelForm):
    class Meta:
        model = Gajist
        fields = '__all__'
        exclude = []


class PrognosisForm(ModelForm):
    PRODUCT = {
        ('All', 'All'),
        ('Classic', 'Classic'),
        ('Special', 'Special'),
        ('Imobil', 'Imobil')
    }
    product = forms.ChoiceField(choices=PRODUCT)

    class Meta:
        model = Prognosis
        fields = '__all__'
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }


class ReportForm(ModelForm):
    PRODUCT = {
        ('All', 'All'),
        ('Classic', 'Classic'),
        ('Special', 'Special'),
        ('Imobil', 'Imobil')
    }
    product = forms.ChoiceField(choices=PRODUCT)

    class Meta:
        model = Report
        fields = '__all__'
        widgets = {
            'start_date': DateInput(),
        }


class ArrearsForm(ModelForm):
    PERSON = (
        ('All', 'All'),
        ('Physical', 'Physical'),
        ('Juridical', 'Juridical')
    )
    person = forms.ChoiceField(choices=PERSON)

    class Meta:
        model = Arrears
        fields = '__all__'
        widgets = {
            'date': DateInput()
        }


class CommentsForm(ModelForm):
    class Meta:
        model = Contract
        fields = ['comments']


class PaymentsForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())
