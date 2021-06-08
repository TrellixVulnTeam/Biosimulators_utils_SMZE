from biosimulators_utils.sedml import model_utils
from biosimulators_utils.sedml.data_model import ModelLanguage, Variable, Symbol, UniformTimeCourseSimulation
from biosimulators_utils.sedml.exceptions import UnsupportedModelLanguageError
from unittest import mock
import os
import unittest


class ModelUtilsTestCase(unittest.TestCase):
    FIXTURES_DIRNAME = os.path.join(os.path.dirname(__file__), '..', 'fixtures')

    def test_get_parameters_variables_for_simulation(self):
        # BNGL
        filename = os.path.join(self.FIXTURES_DIRNAME, 'bngl', 'valid.bngl')
        params, vars = model_utils.get_parameters_variables_for_simulation(filename, ModelLanguage.BNGL, None, None)
        self.assertTrue(vars[0].is_equal(Variable(
            id='time',
            name='Time',
            symbol=Symbol.time.value,
        )))

        # SBML
        filename = os.path.join(self.FIXTURES_DIRNAME, 'BIOMD0000000297.xml')
        params, vars = model_utils.get_parameters_variables_for_simulation(
            filename, ModelLanguage.SBML, UniformTimeCourseSimulation, 'KISAO_0000019')
        self.assertTrue(vars[0].is_equal(Variable(
            id='time',
            name='Time',
            symbol=Symbol.time.value,
        )))

    def test_get_parameters_variables_for_simulation_error_handling(self):
        with self.assertRaisesRegex(UnsupportedModelLanguageError, 'are not supported'):
            model_utils.get_parameters_variables_for_simulation(None, 'not implemented', None, None)
