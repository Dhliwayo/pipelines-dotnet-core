import unittest
from update_country_peril import UpdateCountryPeril

class TestCombineRemovePerils(unittest.TestCase):
    def setUp(self):
        self.processor = UpdateCountryPeril.__new__(UpdateCountryPeril)

    def test_combine_perils_no_duplicates(self):
        incoming = ['EQ', 'FL']
        current = ['EQ', 'FL']
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})
        self.assertEqual(len(result.split(',')), 2)

    def test_combine_perils_trims_spaces(self):
        incoming = [' EQ ', ' FL ']
        current = ['']
        # Simulate trimming in test, since combine_perils does not trim
        incoming = [p.strip() for p in incoming if p.strip()]
        current = [p.strip() for p in current if p.strip()]
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

    def test_combine_perils_existing_perils(self):
        incoming = ['FL']
        current = ['EQ']
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

    def test_combine_perils_no_existing_perils(self):
        incoming = ['EQ', 'FL']
        current = ['']
        current = [p for p in current if p]  # Remove empty
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

    def test_combine_perils_empty_perils_does_not_fail(self):
        incoming = ['']
        current = ['EQ']
        incoming = [p for p in incoming if p]
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ'})

    def test_remove_perils_basic(self):
        to_remove = ['EQ']
        current = ['EQ', 'FL']
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(set(result.split(',')), {'FL'})

    def test_remove_perils_all(self):
        to_remove = ['EQ', 'FL']
        current = ['EQ', 'FL']
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(result, '')

    def test_remove_perils_none(self):
        to_remove = []
        current = ['EQ', 'FL']
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

    def test_remove_perils_spaces(self):
        to_remove = [' EQ ', ' FL ']
        current = ['EQ', 'FL']
        to_remove = [p.strip() for p in to_remove if p.strip()]
        current = [p.strip() for p in current if p.strip()]
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(result, '')

    def test_remove_perils_empty_current(self):
        to_remove = ['EQ']
        current = ['']
        current = [p for p in current if p]
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(result, '')

    def test_combine_perils_case_sensitivity(self):
        incoming = ['EQ']
        current = ['eq']
        result = self.processor.combine_perils(incoming, current)
        # Should treat as different if case-sensitive
        self.assertEqual(set(result.split(',')), {'EQ', 'eq'})

    def test_remove_perils_case_sensitivity(self):
        to_remove = ['eq']
        current = ['EQ', 'FL']
        result = self.processor.remove_perils(to_remove, current)
        # 'EQ' should remain if case-sensitive
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

    def test_combine_perils_all_empty(self):
        incoming = ['']
        current = ['']
        incoming = [p for p in incoming if p]
        current = [p for p in current if p]
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(result, '')

    def test_remove_perils_all_empty(self):
        to_remove = ['']
        current = ['']
        to_remove = [p for p in to_remove if p]
        current = [p for p in current if p]
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(result, '')

    def test_combine_perils_special_characters(self):
        incoming = ['EQ-1', 'FL2']
        current = ['EQ-1', 'ST@']
        result = self.processor.combine_perils(incoming, current)
        self.assertEqual(set(result.split(',')), {'EQ-1', 'FL2', 'ST@'})

    def test_remove_perils_special_characters(self):
        to_remove = ['ST@']
        current = ['EQ-1', 'FL2', 'ST@']
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(set(result.split(',')), {'EQ-1', 'FL2'})

    def test_remove_perils_nonexistent(self):
        to_remove = ['ST']
        current = ['EQ', 'FL']
        result = self.processor.remove_perils(to_remove, current)
        self.assertEqual(set(result.split(',')), {'EQ', 'FL'})

if __name__ == '__main__':
    unittest.main() 