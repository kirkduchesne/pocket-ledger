import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('ledger.py')


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'expenses.csv'

    def run_command(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--file', str(self.path)] + list(args),
            capture_output=True, text=True)

    def add(self, description='Coffee', amount='3.50', day='2020-12-05'):
        result = self.run_command('add', description, amount, '--date', day)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_list(self):
        result = self.run_command('list')
        self.assertEqual(result.returncode, 0)
        self.assertIn('No expenses yet', result.stdout)
        self.assertFalse(self.path.exists())

    def test_add_and_list_persist_quoted_description(self):
        self.add('Lunch, with "friends"')
        result = self.run_command('list')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Lunch, with "friends"', result.stdout)
        self.assertIn('2020-12-05', result.stdout)
        self.assertIn('3.50', result.stdout)

    def test_month_summary_uses_exact_decimals(self):
        self.add(amount='0.10')
        self.add(amount='0.20')
        self.add(amount='9.00', day='2020-11-30')
        result = self.run_command('summary', '--month', '2020-12')
        self.assertEqual(result.returncode, 0)
        self.assertIn('2 expenses | Total: 0.30', result.stdout)
        self.assertIn('9.30', self.run_command('summary').stdout)

    def test_invalid_amounts_do_not_create_file(self):
        for amount in ['abc', 'NaN', 'Infinity', '-1', '0', '1.234', '1000000']:
            with self.subTest(amount=amount):
                result = self.run_command('add', 'Coffee', amount)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Error:', result.stderr)
                self.assertFalse(self.path.exists())

    def test_invalid_date_description_and_month(self):
        for args in [('add', 'Coffee', '1', '--date', '2020-02-30'),
                     ('add', ' ', '1'), ('add', 'line\nbreak', '1'),
                     ('summary', '--month', '2020-13')]:
            with self.subTest(args=args):
                self.assertNotEqual(self.run_command(*args).returncode, 0)
        self.assertFalse(self.path.exists())

    def test_corrupt_file_is_preserved(self):
        for data in ['bad header\n', 'date,description,amount\n2020-12-05,Coffee\n',
                     'date,description,amount\n2020-12-05,Coffee,NaN\n']:
            self.path.write_text(data, encoding='utf-8')
            result = self.run_command('add', 'Tea', '2')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(self.path.read_text(encoding='utf-8'), data)
            self.assertNotIn('Traceback', result.stderr)

    def test_unwritable_destination_has_clear_error(self):
        self.path.mkdir()
        result = self.run_command('add', 'Tea', '2')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Error:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_no_matching_month(self):
        self.add()
        result = self.run_command('summary', '--month', '2021-01')
        self.assertEqual(result.returncode, 0)
        self.assertIn('0 expenses | Total: 0.00', result.stdout)


if __name__ == '__main__':
    unittest.main()
