#!/usr/bin/env python3
"""
Recompute 2026 release schedules ensuring minimum working-day gaps
and keeping activities as close as possible to Prod while respecting
UK bank holidays.
"""

from datetime import datetime, timedelta
from calendar import day_name

RELEASES = [
    ("2026.01", datetime(2026, 2, 1), "CHG0098149"),
    ("2026.02", datetime(2026, 3, 1), None),
    ("2026.03", datetime(2026, 3, 29), None),
    ("2026.04", datetime(2026, 5, 3), None),
    ("2026.05", datetime(2026, 5, 31), None),
    ("2026.06", datetime(2026, 6, 28), None),
    ("2026.07", datetime(2026, 8, 2), None),
    ("2026.08", datetime(2026, 8, 30), None),
    ("2026.09", datetime(2026, 10, 4), None),
    ("2026.10", datetime(2026, 11, 1), None),
    ("2026.11", datetime(2026, 11, 29), None),
]

BANK_HOLIDAYS = {
    datetime(2026, 1, 1).date(),
    datetime(2026, 4, 3).date(),
    datetime(2026, 4, 6).date(),
    datetime(2026, 5, 4).date(),
    datetime(2026, 5, 25).date(),
    datetime(2026, 8, 31).date(),
    datetime(2026, 12, 25).date(),
    datetime(2026, 12, 28).date(),
}


def is_weekend(day: datetime) -> bool:
    return day.weekday() >= 5


def is_working_day(day: datetime) -> bool:
    return (not is_weekend(day)) and (day.date() not in BANK_HOLIDAYS)


def count_working_days(start: datetime, end: datetime) -> int:
    """Count working days strictly between start and end."""
    current = start + timedelta(days=1)
    count = 0
    while current < end:
        if is_working_day(current):
            count += 1
        current += timedelta(days=1)
    return count


def add_suffix(day: datetime) -> str:
    suffix = "th"
    if day.day % 10 == 1 and day.day != 11:
        suffix = "st"
    elif day.day % 10 == 2 and day.day != 12:
        suffix = "nd"
    elif day.day % 10 == 3 and day.day != 13:
        suffix = "rd"
    return day.strftime(f"%B {day.day}{suffix}")


def compute_schedule(prod: datetime):
    # Raise Prod: latest Friday with >=5 working days before Prod
    candidate = prod - timedelta(days=2)
    while True:
        if (
            candidate.weekday() == 4
            and is_working_day(candidate)
            and count_working_days(candidate, prod) >= 5
        ):
            raise_prod = candidate
            break
        candidate -= timedelta(days=1)

    # PreProd QA: latest Thursday before Raise Prod
    preprod_qa = raise_prod - timedelta(days=1)
    while not (preprod_qa.weekday() == 3 and is_working_day(preprod_qa)):
        preprod_qa -= timedelta(days=1)

    # PreProd: latest Wednesday before QA
    preprod = preprod_qa - timedelta(days=1)
    while not (preprod.weekday() == 2 and is_working_day(preprod)):
        preprod -= timedelta(days=1)

    # Raise PreProd: Thursday before PreProd with >=3 working days gap
    raise_preprod = preprod - timedelta(days=1)
    while True:
        if (
            raise_preprod.weekday() == 3
            and is_working_day(raise_preprod)
            and count_working_days(raise_preprod, preprod) >= 3
        ):
            break
        raise_preprod -= timedelta(days=1)

    # FINT QA: Wednesday before Raise PreProd
    fint_qa = raise_preprod - timedelta(days=1)
    while not (fint_qa.weekday() == 2 and is_working_day(fint_qa)):
        fint_qa -= timedelta(days=1)

    # FINT: Tuesday before FINT QA
    fint = fint_qa - timedelta(days=1)
    while not (fint.weekday() == 1 and is_working_day(fint)):
        fint -= timedelta(days=1)

    # Staging QA: Thursday + Friday before FINT
    staging_qa_thu = fint - timedelta(days=1)
    while staging_qa_thu.weekday() != 3 or not is_working_day(staging_qa_thu):
        staging_qa_thu -= timedelta(days=1)

    staging_qa_fri = staging_qa_thu + timedelta(days=1)
    if not is_working_day(staging_qa_fri):
        # Move pair back a week if Friday is not working
        staging_qa_thu -= timedelta(days=7)
        staging_qa_fri = staging_qa_thu + timedelta(days=1)

    # Staging: four working days ending on Staging QA Thursday
    staging_end = staging_qa_thu
    staging_start = staging_end - timedelta(days=3)
    note = ""
    if not is_working_day(staging_start):
        # Shift block forward to the next working day (Tue-Fri)
        while not is_working_day(staging_start):
            staging_start += timedelta(days=1)
        staging_end = staging_start + timedelta(days=3)
        staging_qa_thu = staging_end - timedelta(days=1)
        staging_qa_fri = staging_end
        note = " (Tue-Fri, adjusted to avoid bank holiday)"

    # Prod QA: Monday after Prod, or Tuesday if Monday is holiday
    prod_qa = prod + timedelta(days=1)
    if not is_working_day(prod_qa):
        prod_qa = prod + timedelta(days=2)

    return {
        "staging_start": staging_start,
        "staging_end": staging_end,
        "staging_note": note,
        "staging_qa_thu": staging_qa_thu,
        "staging_qa_fri": staging_qa_fri,
        "fint": fint,
        "fint_qa": fint_qa,
        "raise_preprod": raise_preprod,
        "preprod": preprod,
        "preprod_qa": preprod_qa,
        "raise_prod": raise_prod,
        "prod": prod,
        "prod_qa": prod_qa,
    }


def main():
    for code, prod_date, change_id in RELEASES:
        data = compute_schedule(prod_date)
        print(f"{code}:")
        staging_label = (
            f"Staging - {add_suffix(data['staging_start'])}->{add_suffix(data['staging_end'])}"
            f"{data['staging_note']}"
        )
        print(staging_label)
        print(
            f"Staging QA - {add_suffix(data['staging_qa_thu'])}/{add_suffix(data['staging_qa_fri'])}"
        )
        print(f"FINT - {add_suffix(data['fint'])}")
        print(f"FINT QA - {add_suffix(data['fint_qa'])}")
        print(f"Raise PreProd - {add_suffix(data['raise_preprod'])}")
        print(f"PreProd - {add_suffix(data['preprod'])}")
        print(f"PreProd QA - {add_suffix(data['preprod_qa'])}")
        print(f"Raise Prod - {add_suffix(data['raise_prod'])}")
        prod_line = f"Prod - {add_suffix(data['prod'])}"
        if change_id:
            prod_line += f" ({change_id})"
        print(prod_line)
        print(f"Prod QA - {add_suffix(data['prod_qa'])}")
        print()


if __name__ == "__main__":
    main()

