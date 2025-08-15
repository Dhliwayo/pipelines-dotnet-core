# Test functions 

import unittest

from insert_if_not_present import build_clause, concat_clauses, where_from_iterables

class MyToolTestCase(unittest.TestCase):

    def testBuildClause(self):
        code = "Field"
        value = "Value"
        expected = "Field = 'Value'"
        actual = build_clause(code, value)
        self.assertEqual(expected, actual)


    def testConcatClauses(self):
        clauses = [
            "FieldA = 'ValueA'",
            "FieldB = 'ValueB'"
        ]
        andor = "AND"
        expected = "FieldA = 'ValueA' AND FieldB = 'ValueB'"
        actual = concat_clauses(clauses, andor)
        self.assertEqual(expected, actual)
    

    def testWhereFromIterables(self): 
        fields = ("FieldA", "FieldB")
        values = ("ValueA", "ValueB")
        expected = "FieldA = 'ValueA' AND FieldB = 'ValueB'"
        actual = where_from_iterables(fields, values)
        self.assertEqual(expected, actual)

    def testWhereFromIterablesInputLengthCheck(self):
        """
        Check that error is raised if inputs are different length
        https://ongspxm.gitlab.io/blog/2016/11/assertraises-testing-for-errors-in-unittest/
        """
        fields = ("FieldA", "FieldB")
        missing_values = ("ValueA")
        with self.assertRaises(ValueError): 
            where_from_iterables(fields, missing_values)
    

if __name__ == '__main__':
    
    unittest.main() # Kick things off 