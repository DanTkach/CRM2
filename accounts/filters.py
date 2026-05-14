import django_filters

from .models import Client, Contract

PRODUCT = {
    ('Classic', 'Classic'),
    ('Imobil', 'Imobil'),
    ('Special', 'Special'),
    ('Consum', 'Consum')
}

STATUS = (
    ('Active', 'Active'),
    ('Closed', 'Closed'),
    ('Colectare', 'Colectare'),
    ('Judecata', 'Judecata'),
    ('Bad Client', 'Bad Client'),
    ('Refinantare', 'Refinantare')
)


class ClientFilter(django_filters.FilterSet):
    class Meta:
        model = Client
        fields = {
                'first_name': ['contains'],
                'last_name': ['contains'],
                'company_name': ['contains']
            }


class ArrearsFilter(django_filters.FilterSet):
    product = django_filters.ChoiceFilter(choices=PRODUCT, empty_label=('All'))
    status = django_filters.ChoiceFilter(choices=STATUS, empty_label=('All (Non Closed)'))

    class Meta:
        model = Contract
        fields = {'id'}


class PrognosisFilter(django_filters.FilterSet):
    product = django_filters.ChoiceFilter(choices=PRODUCT, empty_label=('All'))
