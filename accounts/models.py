from django.db import models
# Create your models here.


class Client(models.Model):
    PERSON = (
        ('Physical', 'Physical'),
        ('Juridical', 'Juridical')
    )

    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    company_name = models.CharField(max_length=200, null=True)
    jur_address = models.CharField(max_length=200, null=True, blank=True)
    administrator = models.CharField(max_length=200, null=True, blank=True)

    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    person = models.CharField(max_length=200, null=True,
                              choices=PERSON, default="Physical")
    gender = models.CharField(max_length=200, null=True,
                              choices=GENDER, default="Male")
    location = models.CharField(max_length=200, null=True, blank=True)
    phone_num = models.CharField(max_length=20, null=True, blank=True)
    idnp = models.CharField(max_length=20, null=True, blank=True)
    id_card_nr = models.CharField(max_length=200, null=True, blank=True)
    id_card_office = models.CharField(max_length=200, null=True, blank=True)
    id_card_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bank_name = models.CharField(max_length=200, null=True, blank=True)
    bank_code = models.CharField(max_length=200, null=True, blank=True)
    bank_account = models.CharField(max_length=200, null=True, blank=True)

    registration_date = models.DateField(null=True, blank=True)
    registration_nr = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        if self.person == "Physical":
            return str(self.first_name) + ' ' + str(self.last_name)
        else:
            return str(self.company_name)


class Contract(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Closed', 'Closed'),
        ('Colectare', 'Colectare'),
        ('Judecata', 'Judecata'),
        ('Bad Client', 'Bad Client'),
        ('Refinantare', 'Refinantare')
    )
    CALC_METHOD = (
        ('Declining Balance', 'Declining Balance'),
        ('Declining Balance (OLD)', 'Declining Balance (OLD)'),
        ('Fixed Flat', 'Fixed Flat'),
    )
    PRODUCT = {
        ('Classic', 'Classic'),
        ('Imobil', 'Imobil'),
        ('Special', 'Special'),
        ('Consum', 'Consum')
    }
    CURRENCY = {
        ('MDL', 'MDL'),
        ('EUR', 'EUR'),
    }
    ECONOMICAL_SECTOR = (
        ('Agricultură', 'Agricultură'),
        ('Comerț', 'Comerț'),
        ('Construcții', 'Construcții'),
        ('Consum', 'Consum'),
        ('Imobil', 'Imobil'),
        ('Transport', 'Transport'),
        ('Prestarea serviciilor', 'Prestarea serviciilor'),
        ('Industria energetică', 'Industria energetică'),
        ('Industria productivă', 'Industria productivă'),
        ('Industria Alim. și Procesare', 'Industria Alim. și Procesare'),
        ('Alte scopuri', 'Alte scopuri')
    )
    TERM = (
        ('Long', 'Long'),
        ('Short', 'Short')
    )
    id = models.IntegerField(primary_key=True)
    client = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, null=True,
                              choices=STATUS, default='Active')
    scope = models.CharField(max_length=200, null=True, blank=True)
    sector = models.CharField(max_length=200, null=True,
                              choices=ECONOMICAL_SECTOR, default='Agricultură')
    term = models.CharField(max_length=200, null=True,
                            choices=TERM, default='Long')
    date_created = models.DateField(null=True)
    date_closed = models.DateField(null=True, blank=True)
    product = models.CharField(max_length=200, null=True,
                               choices=PRODUCT, default='Classic')
    loan = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    months = models.IntegerField(null=True)
    interest_rate = models.DecimalField(max_digits=10,
                                        decimal_places=3, null=True)
    annual_payments = models.IntegerField(null=True)
    calc_method = models.CharField(max_length=100,
                                   null=True, choices=CALC_METHOD)
    month_sum = models.DecimalField(max_digits=10, decimal_places=3, null=True)
    grace_period = models.IntegerField(null=True)
    currency = models.CharField(max_length=100, null=True,
                                choices=CURRENCY, default='MDL')
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=3,
                                        default=1, blank=True)
    comments = models.TextField(null=True)
    comission = models.DecimalField(max_digits=10, decimal_places=3, null=True)
    residual = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    fee_issue = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)
    fee_issue_months = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        if self.client.person == "Physical":
            return str(self.date_created).split(" ")[0] + " " + \
                str(self.client.first_name) + " " + \
                str(self.client.last_name)
        else:
            return str(self.date_created).split(" ")[0] + " " + \
                str(self.client.company_name)


class Fidejusor(models.Model):
    num = models.IntegerField(null=True)
    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=200, null=True)
    phone_num = models.CharField(max_length=20, null=True)
    idnp = models.CharField(max_length=20, null=True)
    id_card_nr = models.CharField(max_length=200, null=True)
    id_card_office = models.CharField(max_length=200, null=True)
    id_card_date = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True)

    def __str__(self):
        return self.first_name


class Gajist(models.Model):
    num = models.IntegerField(null=True)
    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    idnp = models.CharField(max_length=20, null=True)
    domiciliul = models.CharField(max_length=200, null=True)
    marca = models.CharField(max_length=200, null=True)
    model = models.CharField(max_length=200, null=True)
    nr_de_inmatriculare = models.CharField(max_length=200, null=True)
    anul_fabricatiei = models.CharField(max_length=200, null=True)
    nr_caroserie = models.CharField(max_length=200, null=True)
    culoare = models.CharField(max_length=200, null=True)
    seria_certificat = models.CharField(max_length=200, null=True)
    nr_certificat = models.CharField(max_length=200, null=True)
    data_emiterii_certificat = models.CharField(max_length=200, null=True)
    valoarea_de_gaj = models.DecimalField(
        max_digits=15, decimal_places=2, null=True)
    phone_num = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.first_name


class Payment(models.Model):
    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    date_paid = models.DateField(null=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=3,
                                        default=1, blank=True)
    penalty = models.DecimalField(max_digits=15, decimal_places=2,
                                  null=True, blank=True, default=0)

    def __str__(self):
        if self.contract.client.person == "Physical":
            return str(self.date_paid) + " " + \
                str(self.contract.client.first_name) \
                + " " + str(self.contract.client.last_name)
        else:
            return str(self.date_paid) + " " + \
                str(self.contract.client.company_name)


class PenaltyWaive(models.Model):
    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    month = models.IntegerField(null=True)

    def __str__(self):
        return str(self.contract) + " " + str(self.month)


class InterestWaive(models.Model):
    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    month = models.IntegerField(null=True)

    def __str__(self):
        return str(self.contract) + " " + str(self.month)


class Prognosis(models.Model):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return 'bruh'


class Report(models.Model):
    start_date = models.DateField(null=True)

    def __str__(self):
        return 'bruh_report'


class Arrears(models.Model):
    PERSON = (
        ('Physical', 'Physical'),
        ('Juridical', 'Juridical')
    )
    date = models.DateField(null=True)
    person = models.CharField(max_length=200,
                              choices=PERSON,
                              null=True,
                              default='All')

    def __str__(self):
        return 'bruh'
