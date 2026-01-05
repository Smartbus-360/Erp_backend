from datetime import date

def calculate_fine(due_date, rule, paid_on=None):
    # 🔐 SAFETY CHECKS
    if not rule:
        return 0

    if not due_date:
        return 0   # 👈 PREVENT CRASH

    if not paid_on:
        paid_on = date.today()

    delay_days = (paid_on - due_date).days

    if delay_days <= rule.grace_days:
        return 0

    overdue = delay_days - rule.grace_days

    if rule.fine_type == "daily":
        return overdue * rule.fine_amount

    if rule.fine_type == "weekly":
        weeks = (overdue + 6) // 7
        return weeks * rule.fine_amount

    if rule.fine_type == "monthly":
        months = (overdue + 29) // 30
        return months * rule.fine_amount

    return 0
