from dateutil.relativedelta import relativedelta
from datetime import date


def create_spread_sheet(repayment_start, period, payments_per_year,
                        loan, interest_per, calculation_mode, today,
                        paid_stuff, month_sum, grace_period,
                        fee_issue=0, fee_issue_months=1, monthly_commission_rate=0):
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
            interest = round((loan * interest_per / 100) / 12, 2)
            if i + 1 > grace_period:
                principal = round(loan / (nr_of_payments - grace_period), 2)
            else:
                principal = 0
        elif calculation_mode == "Declining Balance":
            interest = round((remaining_credit * interest_per / 100) / 12, 2)
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

    # Build commission schedule
    fee_issue_months = max(1, int(fee_issue_months))

    # CA fee: entire issuance fee due upfront when fee_issue_months == 1
    ca_fee = round(loan * fee_issue / 100, 2) if (fee_issue and fee_issue_months == 1) else 0.0

    # Distributed issuance fee: spread across months when fee_issue_months > 1
    fee_issue_per_period = round(loan * fee_issue / 100 / fee_issue_months, 2) if (fee_issue and fee_issue_months > 1) else 0.0

    monthly_commission = round(loan * monthly_commission_rate / 100, 2) if monthly_commission_rate else 0.0
    commission_table = [0.0 for _ in range(nr_of_payments)]
    for i in range(nr_of_payments):
        comm = monthly_commission
        if i < fee_issue_months and fee_issue_per_period:
            comm += fee_issue_per_period
        commission_table[i] = round(comm, 2)

    principal_to_pay = 0
    interest_to_pay = 0
    today = date.fromisoformat(today)
    today_date_index = 0
    last_paid_date_index = 0
    interest_paid = [0 for _ in range(nr_of_payments)]
    principal_paid = [0 for _ in range(nr_of_payments)]
    commission_paid = [0.0 for _ in range(nr_of_payments)]
    ca_fee_paid = 0.0
    penalty_sum = [0 for _ in range(nr_of_payments)]

    month_range = []
    for i in range(nr_of_payments - 1):
        days_range = payment_date[i + 1] - payment_date[i]
        month_range.append(days_range.days)
    month_range.append(
        ((payment_date[nr_of_payments - 1] + relativedelta(months=months))
         - payment_date[nr_of_payments - 1]).days
    )

    for i in range(nr_of_payments):
        if today < payment_date[i]:
            today_date_index = i
            break
    if today > payment_date[nr_of_payments - 1]:
        today_date_index = nr_of_payments

    advance = 0
    total_penalties_paid = 0
    paid_stuff.sort(key=lambda x: x[1])
    paid_stuff.append((0, today, 0))
    temp_advance = 0

    for payment, pay_date, payment_penalty in paid_stuff:
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

        # Deduct manual penalty from this payment before distributing to interest/principal
        if payment_penalty > 0 and not last and payment > 0:
            taken = min(payment_penalty, payment)
            total_penalties_paid += taken
            payment -= taken

        # Deduct CA fee (upfront issuance fee) before regular commission
        if ca_fee > 0 and ca_fee_paid < ca_fee and not last and payment > 0:
            due = ca_fee - ca_fee_paid
            taken = min(due, payment)
            ca_fee_paid += taken
            payment -= taken

        if last_paid_date_index <= pay_date_index and last is not True:
            for i in range(last_paid_date_index, pay_date_index):
                if commission_table[i] > commission_paid[i]:
                    due = commission_table[i] - commission_paid[i]
                    if payment >= due and payment > 0:
                        commission_paid[i] += due
                        payment -= due
                    else:
                        commission_paid[i] += payment
                        payment = 0
                if interest_table[i] != interest_paid[i]:
                    if payment > interest_table[i] - interest_paid[i] and payment > 0:
                        temp = interest_paid[i]
                        interest_paid[i] += interest_table[i] - interest_paid[i]
                        payment -= interest_table[i] - temp
                    else:
                        interest_paid[i] += payment
                        payment = 0
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
            if ca_fee > 0 and ca_fee_paid < ca_fee:
                due = ca_fee - ca_fee_paid
                if advance >= due:
                    ca_fee_paid += due
                    advance -= due
                else:
                    ca_fee_paid += advance
                    advance = 0
            if last_paid_date_index <= today_date_index:
                for i in range(last_paid_date_index, today_date_index):
                    if commission_table[i] > commission_paid[i]:
                        due = commission_table[i] - commission_paid[i]
                        if advance >= due:
                            commission_paid[i] += due
                            advance -= due
                        else:
                            commission_paid[i] += advance
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

    for i in range(today_date_index):
        principal_to_pay += principal_table[i]
        interest_to_pay += interest_table[i]

    ca_fee_paid = round(ca_fee_paid, 2)
    for i in range(nr_of_payments):
        interest_paid[i] = round(interest_paid[i], 2)
        principal_paid[i] = round(principal_paid[i], 2)
        commission_paid[i] = round(commission_paid[i], 2)

    for i in range(today_date_index):
        principal_to_pay -= principal_paid[i]
        interest_to_pay -= interest_paid[i]

    interest_to_pay = abs(interest_to_pay)
    principal_to_pay = abs(principal_to_pay)

    total_principal_paid = 0
    total_interest_paid = 0
    original_principal = round(loan, 2)
    original_interest = 0

    for i in range(nr_of_payments):
        total_principal_paid += principal_paid[i]
        total_interest_paid += interest_paid[i]
        original_interest += interest_table[i]

    total_commission_paid = round(ca_fee_paid + sum(commission_paid), 2)
    total_commission = round(ca_fee + sum(commission_table), 2)
    closure_commission = round(max(0.0, total_commission - total_commission_paid), 2)

    commission_to_pay = max(0.0, ca_fee - ca_fee_paid)
    for i in range(today_date_index):
        commission_to_pay += max(0.0, commission_table[i] - commission_paid[i])
    commission_to_pay = round(commission_to_pay, 2)

    closure_principal = round(original_principal - total_principal_paid, 2)
    closure_interest = original_interest - total_interest_paid
    total_paid = total_principal_paid + total_interest_paid + total_penalties_paid + total_commission_paid

    total_negative = principal_to_pay + interest_to_pay + commission_to_pay
    total_positive = temp_advance
    balance = round(total_positive - total_negative, 2)
    total_original = original_principal + original_interest + total_commission
    total_closure = closure_principal + closure_interest + closure_commission
    total_outstanding = closure_principal + interest_to_pay

    last_paid_date = payment_date[last_paid_date_index]
    period_delinquent = today - last_paid_date
    days_delinquent = period_delinquent.days

    repayment_date = 0
    if today_date_index >= len(payment_date):
        repayment_date = payment_date[today_date_index - 1]
    else:
        repayment_date = payment_date[today_date_index]

    close = False
    if principal_table[nr_of_payments - 1] == principal_paid[nr_of_payments - 1]:
        close = True
    if close:
        balance = 0.00
        total_closure -= closure_principal
        closure_principal = 0.00
        total_outstanding = 0.00
        days_delinquent = 0
        commission_to_pay = 0.0

    profile = [[
        today.strftime("%d/%m/%y"),                                           # [0]
        loan,                                                                  # [1]
        str(interest_per) + "%",                                               # [2]
        round(balance, 2),                                                     # [3]
        round(principal_to_pay, 2),                                            # [4]
        round(interest_to_pay, 2),                                             # [5]
        round(commission_to_pay, 2),                                           # [6] commission due now
        round(total_principal_paid, 2),                                        # [7]
        round(total_interest_paid, 2),                                         # [8]
        round(total_penalties_paid, 2),                                        # [9]
        round(original_principal, 2),                                          # [10]
        round(original_interest, 2),                                           # [11]
        round(closure_principal, 2),                                           # [12]
        round(closure_interest, 2),                                            # [13]
        round(closure_commission, 2),                                          # [14] closure commission remaining
        round(total_original, 2),                                              # [15]
        round(total_paid, 2),                                                  # [16]
        round(total_commission_paid, 2),                                       # [17] total commission paid
        round(total_outstanding, 2),                                           # [18]
        round(total_closure, 2),                                               # [19]
        round(total_commission, 2),                                            # [20] total commission (original)
        days_delinquent,                                                       # [21]
        round(principal_to_pay + interest_to_pay + commission_to_pay, 2),     # [22]
        0,                                                                     # [23] waived_interest
        0,                                                                     # [24] waived_penalty
        close,                                                                 # [25]
        False,                                                                 # [26]
        False,                                                                 # [27]
        round(principal_to_pay + interest_to_pay + commission_to_pay, 2),     # [28] base total for JS
        repayment_date                                                         # [29]
    ]]

    penalties = [0 for _ in range(nr_of_payments)]
    for i in range(nr_of_payments):
        penalties[i] = [payment_index[i], payment_date_formatted[i], 0, 0, 0]

    database = [i + 1 for i in range(nr_of_payments)]
    for i in range(nr_of_payments):
        database[i] = [
            payment_index[i],           # [0]
            payment_date_formatted[i],  # [1]
            remaining_credit_table[i],  # [2]
            principal_table[i],         # [3]
            interest_table[i],          # [4]
            total_payment_table[i],     # [5]
            commission_table[i],        # [6] commission per period
            principal_paid[i],          # [7]
            interest_paid[i],           # [8]
            commission_paid[i],         # [9] commission paid per period
            False,                       # [10] waived_interest_bool
            False,                       # [11] waived_penalty_bool
            new_interest[i],            # [12]
            month_range[i],             # [13]
            payment_date[i]             # [14]
        ]

    # Prepend the CA row for the one-time upfront issuance fee
    if ca_fee > 0:
        ca_start = date.fromisoformat(repayment_start)
        database = [[
            'CA',                              # [0] marker
            ca_start.strftime("%d/%m/%Y"),     # [1] contract start date
            round(loan, 2),                    # [2] balance at issuance
            0,                                 # [3] principal
            0,                                 # [4] interest
            round(ca_fee, 2),                  # [5] total = CA fee
            round(ca_fee, 2),                  # [6] commission = CA fee
            0,                                 # [7] principal paid
            0,                                 # [8] interest paid
            ca_fee_paid,                       # [9] CA fee paid so far
            False, False, 0, 0,                # [10-13]
            ca_start                           # [14] date object
        ]] + database

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
