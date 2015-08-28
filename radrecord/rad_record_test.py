"""
rad_record_test.py

Contains unit tests for normalization and validation of RadRecords.
"""
import unittest

from rad_record import rad_record, parse_delimited_list

class TestRadRecords(unittest.TestCase):


    def test_is_valid_valid(self):
        """
        Tests that is_valid properly recognizes valid values.
        """
        # Test with just a name
        record = rad_record(name='Valid')
        self.assertTrue(record.is_valid())

        # Test with a date_verified value
        record = rad_record(name='Valid', date_verified='2015-08-27')
        self.assertTrue(record.is_valid())


    def test_is_valid_bad_name(self):
        """
        Tests that is_valid detects a missing name.
        """
        self.assertFalse(rad_record(name=None).is_valid())
        self.assertFalse(rad_record(name='').is_valid())
        self.assertFalse(rad_record(name='    ').is_valid())


    def test_is_valid_bad_date_verified(self):
        """
        Tests that is_valid detects an improperly-formatted date_verified value.
        """
        # Test with a date_verified value
        record = rad_record(name='Valid', date_verified='9/9/99')
        self.assertFalse(record.is_valid())


    def test_parse_delimited_list_empty(self):
        """
        Tests that parse_delimited_list handles empty/null list values.
        """
        self.assertEqual(len(parse_delimited_list(None)), 0)
        self.assertEqual(len(parse_delimited_list('')), 0)
        self.assertEqual(len(parse_delimited_list('    ')), 0)


    def test_parse_delimited_list_one(self):
        """
        Tests that parse_delimited_list handles a single item in a delimited string.
        """
        # Add whitespace and extra semicolons to mess with the parser
        parsed_list = parse_delimited_list('; Item A ;')

        self.assertEqual(len(parsed_list), 1)
        self.assertIn('Item A', parsed_list)


    def test_parse_delimited_list_many(self):
        """
        Tests that parse_delimited_list handles multiple list values (with some duplicates).
        """
        parsed_list = parse_delimited_list('Item A ;Item B; Item C; Item A; Item B;;')

        self.assertEqual(len(parsed_list), 3)
        self.assertIn('Item A', parsed_list)
        self.assertIn('Item B', parsed_list)
        self.assertIn('Item C', parsed_list)


    def test_convert_category_str(self):
        """
        Tests that convert_category_name will appropriately parse
        category_name into category_names.
        """
        record = rad_record(name='Record', category_name='Category 1')
        updated_record = record.convert_category_name()

        self.assertEqual(len(updated_record.category_names), 1)
        self.assertIn('Category 1', updated_record.category_names)


    def test_convert_category_haslist(self):
        """
        Tests that convert_category_name will do nothing when
        there are already items in category_names.
        """
        record = rad_record(name='Record', category_name='New Category 1',
            category_names=['Category A', 'Category B'])
        updated_record = record.convert_category_name()

        self.assertEqual(len(updated_record.category_names), 2)
        self.assertIn('Category A', updated_record.category_names)
        self.assertIn('Category B', updated_record.category_names)
        self.assertNotIn('New Category 1', updated_record.category_names)


    def test_convert_population_str(self):
        """
        Tests that convert_population_names will appropriately parse
        population_names into population_tags.
        """
        record = rad_record(name='Record', population_names='Population 1;Population 2')
        updated_record = record.convert_population_names()

        self.assertEqual(len(updated_record.population_tags), 2)
        self.assertIn('Population 1', updated_record.population_tags)
        self.assertIn('Population 2', updated_record.population_tags)


    def test_convert_population_haslist(self):
        """
        Tests that convert_population_names will do nothing when
        there are already items in population_tags.
        """
        record = rad_record(name='Record', population_names='New Population 1;New Population 2',
            population_tags=['Population A'])
        updated_record = record.convert_population_names()

        self.assertEqual(len(updated_record.population_tags), 1)
        self.assertIn('Population A', updated_record.population_tags)
        self.assertNotIn('New Population 1', updated_record.population_tags)
        self.assertNotIn('New Population 2', updated_record.population_tags)


if __name__ == '__main__':
    unittest.main()