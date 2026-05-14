from dateutil.relativedelta import relativedelta
from datetime import date


def create_spread_sheet(repayment_start, period, payments_per_year,
                        loan, interest_per, calculation_mode, today,
                        paid_stuff, month_sum, grace_period, penalty_waives,
                        interest_waives):
    months = int(12 / payments_per_year)
    nr_of_payments = int(period / months)
    payment_index = [i + 1 for i in range(nr_of_payments)]
    now = date.fromisoformat(repayment_start)
    now = now + relativedelta(months=months)
    payment_date = [i + 1 for i in range(nr_of_payments)]
    payment_date_formatted = [i + 1 for i in range(nr_of_payments)]
    remaining_credit = loan
    payment_date[0] = now
    payment_date_formatted[0] = now.strftime("%d/%m/%Y")
    for i in range(1, nr_of_payments):
        now = now + relativedelta(months=months)
        payment_date[i] = now
        payment_date_formatted[i] = now.strftime("%d/%m/%Y")

    principal_table = [i + 1 for i in range(nr_of_payments)]
    remaining_credit_table = [i + 1 for i in range(nr_of_payments)]
    interest_table = [i + 1 for i in range(nr_of_payments)]
    total_payment_table = [i + 1 for i in range(nr_of_payments)]
    new_interest = [i + 1 for i in range(nr_of_payments)]
    for i in range(nr_of_payments):
        remaining_credit_table[i] = round(remaining_credit, 2)
        if calculation_mode == "Fixed Flat":
            interest = round((loan * interest_per/100) / 12, 2)
            if i + 1 > grace_period:
                principal = round(loan / (nr_of_payments - grace_period), 2)
            else:
                principal = 0
        elif calculation_mode == "Declining Balance":
            interest = round((remaining_credit * interest_per/100) / 12, 2)
            if i + 1 > grace_period:
                principal = round(month_sum - interest, 2)
            else:
                principal = 0
        elif calculation_mode == "Declining Balance (OLD)":
            interest = round((remaining_credit * interest_per / 100) / 12, 2)
            if i + 1 > grace_period:
                principal = round(loan / (nr_of_payments - grace_period), 2)
            else:
                principal = 0
        interest_table[i] = round(interest, 2)
        new_interest[i] = round(interest, 2)
        principal_table[i] = round(principal, 2)
        remaining_credit -= principal
        total_payment_table[i] = round(interest + principal, 2)
    principal_to_pay = 0
    interest_to_pay = 0
    penalties_to_pay = 0
    today = date.fromisoformat(today)
    today_date_index = 0
    last_paid_date_index = 0
    penalty_paid = [0 for _ in range(nr_of_payments)]
    interest_paid = [0 for _ in range(nr_of_payments)]
    principal_paid = [0 for _ in range(nr_of_payments)]

    penalty_date = payment_date
    penalty_sum = [0 for _ in range(nr_of_payments)]
    month_range = []
    for i in range(nr_of_payments - 1):
        days_range = payment_date[i + 1] - payment_date[i]
        month_range.append(days_range.days)
    month_range.append(((payment_date[nr_of_payments - 1] + relativedelta(months=months)) - payment_date[nr_of_payments - 1]).days)
    for i in range(nr_of_payments):
        if today < penalty_date[i]:
            today_date_index = i
            break
    if today > payment_date[nr_of_payments - 1]:
        today_date_index = nr_of_payments
    penalty_days_table = [0 for _ in range(nr_of_payments)]
    advance = 0
    waived_penalty = 0
    waived_interest = 0
    penalty_waives_temp = []
    paid_stuff.sort(key=lambda x: x[1])
    for waive in penalty_waives:
        penalty_waives_temp.append(waive)
    paid_stuff.append((0, today))
    penalty_date_index = last_paid_date_index
    temp_advance = 0
    for payment, pay_date in paid_stuff:
        last = False
        if payment == 0:
            last = True
        payment += advance
        advance = 0
        pay_date = str(pay_date).split(" ")[0]
        pay_date = date.fromisoformat(pay_date)
        pay_date_index = 0
        for i in range(nr_of_payments):
            if pay_date < payment_date[i]:
                pay_date_index = i
                break
        if pay_date > payment_date[nr_of_payments - 1]:
            pay_date_index = nr_of_payments
        last_paid_date = payment_date[last_paid_date_index]
        if penalty_date_index < len(payment_date):
            if penalty_date_index < last_paid_date_index and last_paid_date_index <= today_date_index:
                penalty_date_index = last_paid_date_index
            penalty_periods = today - payment_date[penalty_date_index]
            penalty_days = penalty_periods.days
            penalty_days_temp = penalty_days
            while penalty_days_temp > 0:
                if penalty_date_index < nr_of_payments - 1 and penalty_days_temp > month_range[penalty_date_index]:
                    penalty_days_table[penalty_date_index] = penalty_days_temp
                    if penalty_days_table[penalty_date_index] > 180:
                        penalty_days_table[penalty_date_index] = 180
                    for i in range(penalty_days_table[penalty_date_index]):
                        penalty_sum[penalty_date_index] += 0.0004 * total_payment_table[penalty_date_index]
                    penalty_days_temp -= month_range[penalty_date_index]
                    penalty_date_index += 1
                else:
                    if penalty_days_temp > 180:
                        penalty_days_temp = 180
                    penalty_days_table[penalty_date_index] = penalty_days_temp
                    for i in range(penalty_days_temp):
                        penalty_sum[penalty_date_index] += 0.0004 * total_payment_table[penalty_date_index]
                    penalty_days_temp = 0
                    penalty_date_index += 1

        for waive in penalty_waives:
            if last:
                waived_penalty += penalty_sum[waive - 1]
                penalty_sum[waive - 1] = 0
                penalty_days_table[waive - 1] = 0
        for waive in interest_waives:
            waived_interest += interest_table[waive - 1]
            total_payment_table[waive-1] = round(total_payment_table[waive-1] - interest_table[waive - 1])
            interest_table[waive - 1] = 0
        for i in range(nr_of_payments):
            penalty_sum[i] = round(penalty_sum[i], 2)
        if last_paid_date_index <= pay_date_index and last is not True:
            for i in range(last_paid_date_index, pay_date_index):
                if penalty_sum[i] != penalty_paid[i] and i + 1 not in penalty_waives:
                    if payment > penalty_sum[i] - penalty_paid[i] and payment > 0:
                        temp = penalty_paid[i]
                        penalty_paid[i] += penalty_sum[i] - penalty_paid[i]
                        payment -= penalty_sum[i] - temp
                    else:
                        penalty_paid[i] += payment
                        payment = 0
#       if last_paid_date_index <= pay_date_index and last is not True:
#           for i in range(last_paid_date_index, pay_date_index):
                if interest_table[i] != interest_paid[i]:
                    if payment > interest_table[i] - interest_paid[i] and payment > 0:
                        temp = interest_paid[i]
                        interest_paid[i] += interest_table[i] - interest_paid[i]
                        payment -= interest_table[i] - temp
                    else:
                        interest_paid[i] += payment
                        payment = 0
#       if last_paid_date_index <= pay_date_index and last is not True:
#           for i in range(last_paid_date_index, pay_date_index):
                if principal != principal_paid[i]:
                    if payment >= principal_table[i] - principal_paid[i] and payment > 0:
                        temp = principal_paid[i]
                        principal_paid[i] += principal_table[i] - principal_paid[i]
                        payment -= principal_table[i] - temp
                        if last_paid_date_index < len(payment_date) - 1:
                            last_paid_date_index += 1
                    else:
                        principal_paid[i] += payment
                        payment = 0
        if payment > 0:
            advance += payment
        while advance > 0:
            if last_paid_date_index <= today_date_index:
                for i in range(last_paid_date_index, today_date_index):
                    if penalty_sum[i] != penalty_paid[i] and i + 1 not in penalty_waives:
                        if advance >= penalty_sum[i] - penalty_paid[i]:
                            temp = penalty_paid[i]
                            penalty_paid[i] += penalty_sum[i] - penalty_paid[i]
                            advance -= penalty_sum[i] - temp
                        else:
                            penalty_paid[i] += advance
                            advance = 0
                            break
                    if interest_table[i] != interest_paid[i]:
                        if advance >= interest_table[i] - interest_paid[i]:
                            temp = interest_paid[i]
                            interest_paid[i] += interest_table[i] - interest_paid[i]
                            advance -= interest_table[i] - temp
                        else:
                            interest_paid[i] += advance
                            advance = 0
                            break
                    if principal != principal_paid[i]:
                        if advance >= principal_table[i] - principal_paid[i]:
                            temp = principal_paid[i]
                            principal_paid[i] += principal_table[i] - principal_paid[i]
                            advance -= principal_table[i] - temp
                            if last_paid_date_index < len(payment_date) - 1:
                                last_paid_date_index += 1
                        else:
                            principal_paid[i] += advance
                            advance = 0
                            break
            temp_advance = advance
            if advance > 0:
                for i in range(last_paid_date_index, nr_of_payments):
                    if principal != principal_paid[i]:
                        if advance >= principal_table[i] - principal_paid[i]:
                            temp = principal_paid[i]
                            principal_paid[i] += principal_table[i] - principal_paid[i]
                            advance -= principal_table[i] - temp
                        else:
                            principal_paid[i] += advance
                            advance = 0
            break
    for i in range(nr_of_payments):
        if i + 1 in penalty_waives:
            penalty_paid[i] = 0

    for i in range(today_date_index):
        principal_to_pay += principal_table[i]
        interest_to_pay += interest_table[i]

    for i in range(nr_of_payments):
        penalty_paid[i] = round(penalty_paid[i], 2)
        interest_paid[i] = round(interest_paid[i], 2)
        principal_paid[i] = round(principal_paid[i], 2)

    for i in range(today_date_index):
        principal_to_pay -= principal_paid[i]
        interest_to_pay -= interest_paid[i]
        penalties_to_pay += penalty_sum[i]
        penalties_to_pay -= penalty_paid[i]

    interest_to_pay = abs(interest_to_pay)
    principal_to_pay = abs(principal_to_pay)
    interest_to_pay = abs(interest_to_pay)

    total_principal_paid = 0
    total_interest_paid = 0
    total_penalties_paid = 0
    total_penalty = 0
    original_principal = round(loan, 2)
    original_interest = 0
    total_waived = waived_penalty + waived_interest

    for i in range(nr_of_payments):
        total_principal_paid += principal_paid[i]
        total_interest_paid += interest_paid[i]
        total_penalties_paid += penalty_paid[i]
        original_interest += interest_table[i]
        total_penalty += penalty_sum[i]
    closure_principal = round(original_principal - total_principal_paid, 2)
    closure_interest = original_interest - total_interest_paid
    closure_penalty = total_penalty - total_penalties_paid

    total_negative = principal_to_pay + interest_to_pay + penalties_to_pay
    total_positive = temp_advance

    balance = round(total_positive - total_negative, 2)
    total_original = original_principal + original_interest
    total_paid = total_principal_paid + total_interest_paid + total_penalties_paid
    total_closure = closure_principal + closure_interest + closure_penalty
    total_outstanding = closure_principal + interest_to_pay + closure_penalty
    last_paid_date = payment_date[last_paid_date_index]
    period_delinquent = today - last_paid_date
    days_delinquent = period_delinquent.days

    repayment_date = 0
    if today_date_index >= len(payment_date):
        repayment_date = payment_date[today_date_index - 1]
    else:
        repayment_date = payment_date[today_date_index]

    waived_penalty_bool = [i + 1 for i in range(nr_of_payments)]
    waived_interest_bool = [i + 1 for i in range(nr_of_payments)]
    waive_all_p = True
    waive_all_i = True

    for i in range(nr_of_payments):
        if i + 1 in penalty_waives:
            waived_penalty_bool[i] = True
        else:
            waived_penalty_bool[i] = False
            waive_all_p = False

    for i in range(nr_of_payments):
        if i + 1 in interest_waives:
            waived_interest_bool[i] = True
        else:
            waived_interest_bool[i] = False
            waive_all_i = False

    close = False
    if principal_table[nr_of_payments - 1] == principal_paid[nr_of_payments - 1]:
        close = True
    if close:
        balance = 0.00
        total_closure -= closure_principal
        closure_principal = 0.00
        closure_penalty = 0.00
        total_outstanding = 0.00
        days_delinquent = 0

    profile = [[
        today.strftime("%d/%m/%y"),
        loan,
        str(interest_per) + "%",
        round(balance, 2),
        round(principal_to_pay, 2),
        round(interest_to_pay, 2),
        round(penalties_to_pay, 2),
        round(total_principal_paid, 2),
        round(total_interest_paid, 2),
        round(total_penalties_paid, 2),
        round(original_principal, 2),
        round(original_interest, 2),
        round(closure_principal, 2),
        round(closure_interest, 2),
        round(closure_penalty, 2),
        round(total_original, 2),
        round(total_paid, 2),
        round(total_waived, 2),
        round(total_outstanding, 2),
        round(total_closure, 2),
        round(total_penalty, 2),
        days_delinquent,
        round(round(principal_to_pay, 2) + round(interest_to_pay, 2), 2),
        round(waived_interest, 2),
        round(waived_penalty, 2),
        close,
        waive_all_p,
        waive_all_i,
        round(round(principal_to_pay, 2) + round(interest_to_pay, 2) + round(penalties_to_pay, 2), 2),
        repayment_date
    ]]

    penalties = [0 for _ in range(nr_of_payments)]
    for i in range(nr_of_payments):
        penalties[i] = [
            payment_index[i],
            payment_date_formatted[i],
            penalty_sum[i],
            penalty_days_table[i],
            penalty_paid[i]
        ]

    database = [i + 1 for i in range(nr_of_payments)]
    for i in range(nr_of_payments):
        database[i] = [
            payment_index[i],
            payment_date_formatted[i],
            remaining_credit_table[i],
            principal_table[i],
            interest_table[i],
            total_payment_table[i],
            penalty_sum[i],
            principal_paid[i],
            interest_paid[i],
            penalty_paid[i],
            waived_interest_bool[i],
            waived_penalty_bool[i],
            new_interest[i],
            month_range[i],
            payment_date[i]
        ]
    return database, profile, penalties


num2words = {1: 'o ', 2: 'două ', 3: 'trei ', 4: 'patru ', 5: 'cinci ',
             6: 'șase ', 7: 'șapte ', 8: 'opt ', 9: 'nouă ', 10: 'zece ',
             11: 'unsprezece ', 12: 'doisprezece ',
             13: 'treisprezece ', 14: 'paisprezece ',
             15: 'cinsprezece ', 16: 'șaisprezece ',
             17: 'șaptesprezece ', 18: 'optsprezece ',
             19: 'nouăsprezece ', 20: 'douăzeci ',
             30: 'treizeci ', 40: 'patruzeci ',
             50: 'cincizeci ', 60: 'șaizeci ',
             70: 'șaptezeci ', 80: 'optzeci ',
             90: 'nouăzeci ', 0: ''}

def verbose_loan(num):
    full = str("{:.2f}".format(num)).split('.')
    num = full[0]
    b = full[1]
    v = ""
    last_num = 0
    while len(num) != 0:
        if len(str(num)) in [3, 4, 6, 7] and int(num[0]) != 1:
            v += num2words[int(num[0])]
            last_num = int(num[0])
            num = num[1:]
            start = False
        elif int(num[0]) == 1 and len(str(num)) in [3, 4, 6]:
            v += num2words[int(num[0])]
            last_num = int(num[0])
            num = num[1:]
            start = False
        elif int(num[0]) == 1 and len(str(num)) == 7:
            v += "un "
            last_num = 1
            num = num[1:]
            start = False
        elif int(num[0]) == 1 and len(str(num)) == 1:
            v += "una "
            last_num = 1
            num = num[1:]
            start = False
        else:
            try:
                v += num2words[int(num[0:2])]
                num = num[2:]
                start = False
            except KeyError:
                v += num2words[int(num[0]) * 10]
                v += "și "
                if int(num[1]) != 1:
                    v += num2words[int(num[1])]
                    num = num[2:]
                    start = False
                else:
                    v += "una "
                    num = num[2:]
                    start = False
        if len(str(num)) == 3:
            v += "mii "
        elif len(str(num)) == 6:
            v += "milion "
        elif len(str(num)) in [2, 5] and last_num != 1 and last_num != 0:
            v += "sute "
        elif len(str(num)) in [2, 5] and last_num == 1:
            v += "sută "
    v += "Lei "
    while len(b) != 0:
        if b[0] == "0":
            v += 'zero '
            b = b[1:]
        else:
            try:
                v += num2words[int(b[0:2])]
                b = ''
            except KeyError:
                v += num2words[int(b[0]) * 10]
                v += "și "
                if int(b[1]) != 1:
                    v += num2words[int(b[1])]
                    b = ''
                else:
                    v += "una "
                    b = ''
    v += "Bani"
    return v


def verbose_interest(num):
    full_vb = verbose_loan(num)
    v = full_vb.replace('Lei ', 'punct ')
    v = v.replace(' Bani', '')
    return v
