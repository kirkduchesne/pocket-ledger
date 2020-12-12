import argparse
import csv
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ['date', 'description', 'amount']


def parse_amount(value):
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValueError('Amount must be a positive number with at most two decimal places.')
    if not amount.is_finite() or amount <= 0 or amount > Decimal('999999.99'):
        raise ValueError('Amount must be between 0.01 and 999999.99.')
    if amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Amount must have at most two decimal places.')
    return format(amount, '.2f')


def parse_date(value):
    parsed = datetime.strptime(value, '%Y-%m-%d').date()
    if parsed.isoformat() != value:
        raise ValueError('Use YYYY-MM-DD for dates.')
    return value


def read_expenses(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != FIELDS:
            raise ValueError('The expense file has an invalid header.')
        rows = list(reader)
    for row in rows:
        if set(row) != set(FIELDS) or any(value is None for value in row.values()):
            raise ValueError('The expense file contains an incomplete row.')
        parse_date(row['date'])
        parse_amount(row['amount'])
        if not row['description'].strip():
            raise ValueError('The expense file contains an empty description.')
    return rows


def add_expense(path, description, amount, expense_date):
    description = description.strip()
    if not description or len(description) > 120 or not description.isprintable():
        raise ValueError('Description must be 1-120 printable characters.')
    row = {'date': parse_date(expense_date), 'description': description,
           'amount': parse_amount(amount)}
    read_expenses(path)
    exists = path.exists()
    with path.open('a', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def list_expenses(path):
    rows = read_expenses(path)
    if not rows:
        print('No expenses yet. Use add to record your first expense.')
        return
    for row in rows:
        print('{}  {:>10}  {}'.format(row['date'], row['amount'], row['description']))


def summarize_expenses(path, month):
    if month:
        parse_date(month + '-01')
    rows = read_expenses(path)
    if month:
        rows = [row for row in rows if row['date'].startswith(month + '-')]
    total = sum((Decimal(row['amount']) for row in rows), Decimal('0.00'))
    print('{} expenses | Total: {:.2f}'.format(len(rows), total))


def main():
    parser = argparse.ArgumentParser(description='Keep a simple personal expense log.')
    parser.add_argument('--file', type=Path, default=Path('expenses.csv'))
    commands = parser.add_subparsers(dest='command', required=True)
    add = commands.add_parser('add', help='Record an expense')
    add.add_argument('description')
    add.add_argument('amount')
    add.add_argument('--date', default=date.today().isoformat())
    commands.add_parser('list', help='Show recorded expenses')
    summary = commands.add_parser('summary', help='Show an expense total')
    summary.add_argument('--month', help='Filter by YYYY-MM')
    args = parser.parse_args()
    try:
        if args.command == 'add':
            add_expense(args.file, args.description, args.amount, args.date)
            print('Expense saved.')
        elif args.command == 'list':
            list_expenses(args.file)
        else:
            summarize_expenses(args.file, args.month)
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        parser.exit(1, 'Error: {}\n'.format(error))


if __name__ == '__main__':
    main()
