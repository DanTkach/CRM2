from django.db import models
# Create your models here.

class Client(models.Model):
	first_name = models.CharField(max_length=200, null=True)
	last_name = models.CharField(max_length=200, null=True)
	location = models.CharField(max_length=200, null=True)
	phone_num = models.CharField(max_length=20, null=True)
	idnp = models.IntegerField(null=True)
	birth_date = models.DateField(null=True)
	scope = models.CharField(max_length=200, null=True)
	bank_name = models.CharField(max_length=200, null=True)
	bank_code = models.CharField(max_length=200, null=True)
	bank_account = models.CharField(max_length=200, null=True)

	def __str__(self):
		return self.first_name


class Contract(models.Model):
	STATUS = (
		('Active', 'Active'),
		('Closed', 'Closed'),
		('Colectare', 'Colectare'),
		('Judecata', 'Judecata')
	)
	CALC_METHOD = (
		('Declining Balance', 'Declining Balance'),
		('Fixed Flat', 'Fixed Flat'),
	)
	PRODUCT = {
		('Classic', 'Classic'),
		('Imobil', 'Imobil'),
		('Special', 'Special'),
	}
	id = models.IntegerField(primary_key=True)
	client = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
	status = models.CharField(max_length=200, null=True, choices=STATUS, default='Active')
	date_created = models.DateField(null=True)
	product = models.CharField(max_length=200, null=True, choices=PRODUCT, default='Classic')
	loan = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	months = models.IntegerField(null=True)
	interest_rate = models.DecimalField(max_digits=10, decimal_places=3, null=True)
	annual_payments = models.IntegerField(null=True)
	calc_method = models.CharField(max_length=100, null=True, choices=CALC_METHOD)
	month_sum = models.DecimalField(max_digits=10, decimal_places=3, null=True)
	grace_period = models.IntegerField(null=True)
	def __str__(self):
		return str(self.date_created).split(" ")[0] + " " + str(self.client.first_name) + " " + \
			str(self.client.last_name)


class Payment(models.Model):
	contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
	sum = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	principal_paid = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	interest_paid = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	penalties_paid = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	advance = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	date_paid = models.DateField(null=True, blank=True)

	def __str__(self):
		return str(self.date_paid) + " " + str(self.contract.client.first_name) \
			+ " " + str(self.contract.client.last_name)


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
