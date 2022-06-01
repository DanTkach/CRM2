import dateutil.utils
from django.shortcuts import render, redirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.request import QueryDict
from django.template.loader import get_template
from .process import render_to_pdf
from django.views.generic import View
from django.http import HttpResponse

# Create your views here.
from .models import *
from .forms import CreateUserForm, ClientForm, ContractForm, PaymentForm
from .filters import ClientFilter
from .decorators import unauthenticated_user, allowed_users, admin_only
from .functions import create_spread_sheet

from datetime import date
from decimal import Decimal


class GeneratePDF(View):
    def get(self, request, pk, *args, **kwargs):
        template = get_template('pdf/download.html')
        contract = Contract.objects.get(id=pk)
        payments = Payment.objects.filter(contract_id=pk)
        penalty_waives = PenaltyWaive.objects.filter(contract_id=pk)
        interest_waives = InterestWaive.objects.filter(contract_id=pk)
        table, profile, penalties = create_spread_sheet(
            str(contract.date_created).split(" ")[0],
            contract.months,
            contract.annual_payments,
            float(contract.loan),
            float(contract.interest_rate),
            contract.calc_method,
            str(date.today()),
            [(float(payment.sum), payment.date_paid) for payment in payments],
            float(contract.month_sum),
            contract.grace_period,
            [int(waive.month) for waive in penalty_waives],
            [int(waive.month) for waive in interest_waives]
        )
        context = {'table': table, 'profile': profile, 'penalties': penalties, 'all_payments': payments, 'contract': contract}
        html = template.render(context)
        pdf = render_to_pdf('pdf/download.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Contract_%s.pdf" %("12341231")
            content = "inline; filename='%s'" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    clients = Client.objects.all()

    total_clients = clients.count()

    myFilter = ClientFilter(request.GET, queryset=clients)
    clients = myFilter.qs

    context = {'clients': clients,
               'total_clients': total_clients,
               'myFilter': myFilter}

    return render(request, 'accounts/my_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def arrears(request):
    contracts_list = Contract.objects.all()
    contracts = []
    for contract_data in contracts_list:
        payments = Payment.objects.filter(contract_id=contract_data.id)
        client = Client.objects.get(id=contract_data.client_id)
        penalty_waives = PenaltyWaive.objects.filter(contract_id=contract_data.id)
        interest_waives = InterestWaive.objects.filter(contract_id=contract_data.id)
        contracts.append([
            contract_data.id,
            str(client.last_name) + " " + str(client.first_name),
            create_spread_sheet(
                str(contract_data.date_created).split(" ")[0],
                contract_data.months,
                contract_data.annual_payments,
                float(contract_data.loan),
                float(contract_data.interest_rate),
                contract_data.calc_method,
                str(date.today()),
                [(float(payment.sum), payment.date_paid) for payment in payments],
                float(contract_data.month_sum),
                contract_data.grace_period,
                [int(waive.month) for waive in penalty_waives],
                [int(waive.month) for waive in interest_waives]
            )[1]
        ])
        contracts.sort(key=lambda x: x[2][0][21])
        profile = [0, 0, 0, 0, 0]
        for contract in contracts:
            profile[0] += contract[2][0][10]
            profile[1] += contract[2][0][12]
            if contract[2][0][21] > 30:
                profile[2] += contract[2][0][4]
            profile[4] += contract[2][0][5]
        profile[3] = round((profile[2] / profile[1]) * 100, 2)

    context = {'contracts': contracts, 'profile': profile}
    return render(request, 'accounts/arrears.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def client(request, pk_test):
    client = Client.objects.get(id=pk_test)
    contracts_list = client.contract_set.all()
    contracts_count = contracts_list.count()
    contracts = []
    for contract_data in contracts_list:
        payments = Payment.objects.filter(contract_id=contract_data.id)
        penalty_waives = PenaltyWaive.objects.filter(contract_id=contract_data.id)
        interest_waives = InterestWaive.objects.filter(contract_id=contract_data.id)
        contracts.append([
            contract_data.id,
            contract_data.date_created,
            contract_data.product,
            contract_data.loan,
            contract_data.status,
            create_spread_sheet(
                str(contract_data.date_created).split(" ")[0],
                contract_data.months,
                contract_data.annual_payments,
                float(contract_data.loan),
                float(contract_data.interest_rate),
                contract_data.calc_method,
                str(date.today()),
                [(float(payment.sum), payment.date_paid) for payment in payments],
                float(contract_data.month_sum),
                contract_data.grace_period,
                [int(waive.month) for waive in penalty_waives],
                [int(waive.month) for waive in interest_waives]
            )[1]
            ])
    context = {'client': client, 'contracts': contracts, 'contracts_count': contracts_count}
    return render(request, 'accounts/client.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createContract(request, pk):
    client = Client.objects.get(id=pk)
    ContractForms = modelform_factory(Contract, form=ContractForm)
    form = ContractForms(initial={'client': client})
    client_id = client.pk
    # form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            contract = Contract.objects.get(id=form.data.get('id'))
            return redirect('/view_contract/' + str(contract.id) + '/')
    context = {'form': form}
    return render(request, 'accounts/contract_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateContract(request, pk):
    contract = Contract.objects.get(id=pk)
    form = ContractForm(instance=contract)
    print('Contract:', contract)
    if request.method == 'POST':

        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/contract_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def viewContract(request, pk):
    contract = Contract.objects.get(id=pk)
    client = Client.objects.get(id=contract.client_id)
    payments = Payment.objects.filter(contract_id=pk)
    penalty_waives = PenaltyWaive.objects.filter(contract_id=pk)
    interest_waives = InterestWaive.objects.filter(contract_id=pk)
    table, profile, penalties = create_spread_sheet(
        str(contract.date_created).split(" ")[0],
        contract.months,
        contract.annual_payments,
        float(contract.loan),
        float(contract.interest_rate),
        contract.calc_method,
        str(date.today()),
        [(float(payment.sum), payment.date_paid) for payment in payments],
        float(contract.month_sum),
        contract.grace_period,
        [int(waive.month) for waive in penalty_waives],
        [int(waive.month) for waive in interest_waives]
    )
    if request.method == 'POST':

        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'client': client,
               'table': table,
               'profile': profile,
               'penalties': penalties,
               'all_payments': payments,
               'contract': contract
               }
    return render(request, 'accounts/contract_table.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteContract(request, pk):
    contract = Contract.objects.get(id=pk)
    client = contract.client
    client_id = client.pk
    if request.method == "POST":
        contract.delete()
        return redirect(f'/client/{client.id}/')
    context = {'item': contract}
    return render(request, 'accounts/delete_contract.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createClient(request):
    ClientForms = modelform_factory(Client, form=ClientForm, fields=["first_name", "last_name", "location", "phone_num"])
    form = ClientForms()
    # form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            client = Client.objects.get(phone_num=form.data.get('phone_num'))
            return redirect('/client/' + str(client.id) + '/')
    context = {'form': form}
    return render(request, 'accounts/new_client.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateClient(request, pk):
    client = Client.objects.get(id=pk)
    form = ClientForm(instance=client)
    if request.method == 'POST':

        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect(f'/client/{client.id}/')

    context = {'form': form}
    return render(request, 'accounts/new_client.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteClient(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == "POST":
        client.delete()
        return redirect('/')

    context = {'item': client}
    return render(request, 'accounts/delete_client.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createPayment(request, pk):
    contract = Contract.objects.get(id=pk)
    payments = Payment.objects.filter(contract_id=pk)
    penalty_waives = PenaltyWaive.objects.filter(contract_id=pk)
    interest_waives = InterestWaive.objects.filter(contract_id=pk)
    PaymentForms = modelform_factory(Payment, form=PaymentForm)
    form = PaymentForms(initial={'contract': contract})
    contract_id = contract.pk
    # form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = PaymentForm(request.POST)
        new_form = Payment()
        if form.is_valid():
            database, profile, penalties = create_spread_sheet(
                str(contract.date_created).split(" ")[0],
                contract.months,
                contract.annual_payments,
                float(contract.loan),
                float(contract.interest_rate),
                contract.calc_method,
                str(date.today()),
                [(float(payment.sum), payment.date_paid) for payment in payments],
                float(contract.month_sum),
                contract.grace_period,
                [int(waive.month) for waive in penalty_waives],
                [int(waive.month) for waive in interest_waives]
            )
            sum = float(form.cleaned_data['sum'])
            new_form.sum = sum
            penalties_to_pay = profile[0][6]
            interest_to_pay = profile[0][5]
            principal_to_pay = profile[0][4]
            if sum >= penalties_to_pay:
                penalties_paid = sum - penalties_to_pay
                sum -= penalties_to_pay
            else:
                penalties_paid = sum
                sum = 0
            if sum >= interest_to_pay:
                interest_paid = sum - interest_to_pay
                sum -= interest_to_pay
            else:
                interest_paid = sum
                sum = 0
            if sum >= principal_to_pay:
                principal_paid = sum - principal_to_pay
                sum -= principal_to_pay
            else:
                principal_paid = sum
            new_form.date_paid = form.cleaned_data['date_paid']
            new_form.contract = form.cleaned_data['contract']
            new_form.penalties_paid = round(float(penalties_paid), 2)
            new_form.interest_paid = round(float(interest_paid), 2)
            new_form.principal_paid = round(float(principal_paid), 2)
            print(new_form)
            new_form.save()
            return redirect('/view_contract/' + str(contract_id) + '/')

    context = {'form': form}
    return render(request, 'accounts/payment_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updatePayment(request, pk):
    payment = Payment.objects.get(id=pk)
    form = PaymentForm(instance=payment)
    if request.method == 'POST':

        form = PaymentForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect(f'/view_contract/{payment.contract_id}/')

    context = {'form': form}
    return render(request, 'accounts/payment_form', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deletePayment(request, pk):
    payment = Payment.objects.get(id=pk)
    if request.method == "POST":
        payment.delete()
        return redirect(f'/view_contract/{payment.contract_id}/')

    context = {'item': payment}
    return render(request, 'accounts/delete_payment.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createPenaltyWaive(request, pk, pj):
    waive = PenaltyWaive(contract_id=pk, month=pj)
    waive.save()
    return redirect('/view_contract/' + str(waive.contract_id) + '/')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createInterestWaive(request, pk, pj):
    waive = InterestWaive(contract_id=pk, month=pj)
    waive.save()
    return redirect('/view_contract/' + str(waive.contract_id) + '/')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deletePenaltyWaive(request, pk, pj):
    waive = PenaltyWaive.objects.filter(contract_id=pk, month=pj)
    id = pk
    waive.delete()
    return redirect('/view_contract/' + str(id) + '/')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteInterestWaive(request, pk, pj):
    waive = InterestWaive.objects.filter(contract_id=pk, month=pj)
    id = pk
    waive.delete()
    return redirect('/view_contract/' + str(id) + '/')
