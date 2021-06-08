from biosimulators_utils.model_lang.sbml.utils import get_parameters_variables_for_simulation
from biosimulators_utils.sedml.data_model import (ModelLanguage, SteadyStateSimulation,
                                                  OneStepSimulation, UniformTimeCourseSimulation, Symbol)
from unittest import mock
import libsbml
import os
import unittest


class GetVariableForSimulationTestCase(unittest.TestCase):
    CORE_FIXTURE = os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'BIOMD0000000297.xml')
    CORE_FIXTURE_L3 = os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'BIOMD0000000075.xml')
    CORE_FIXTURE_WITH_EXTRAS_PARAMS_VARS = os.path.join(
        os.path.dirname(__file__), '..', '..', 'fixtures', 'BIOMD0000000297-params-vars.xml')
    FBC_FIXTURE = os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'sbml-fbc-textbook.xml')
    QUAL_FIXTURE = os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'Chaouiya-BMC-Syst-Biol-2013-EGF-TNFa-signaling.xml')
    QUAL_FIXTURE_WITH_EXTRAS_PARAMS_VARS = os.path.join(
        os.path.dirname(__file__), '..', '..', 'fixtures', 'Chaouiya-BMC-Syst-Biol-2013-EGF-TNFa-signaling-params-vars.xml')

    def test_core_steady_state(self):
        params, vars = get_parameters_variables_for_simulation(
            self.CORE_FIXTURE, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000019',
            include_compartment_sizes_in_simulation_variables=True,
            include_model_parameters_in_simulation_variables=True)

        self.assertEqual(params[0].id, 'init_conc_species_Trim')
        self.assertEqual(params[0].name, 'Initial concentration of species "CDC28_Clb2_Sic1_Complex"')
        self.assertEqual(params[0].new_value, '0.084410675')
        self.assertEqual(params[0].target, "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='Trim']/@initialConcentration")
        self.assertEqual(params[0].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        self.assertEqual(params[-3].id, 'value_parameter_mu')
        self.assertEqual(params[-3].new_value, '0.005')

        self.assertEqual(params[-1].id, 'value_parameter_Swe1T')
        self.assertEqual(params[-1].name, 'Value of parameter "Swe1T"')
        self.assertEqual(params[-1].new_value, '0')
        self.assertEqual(params[-1].target, "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter[@id='Swe1T']/@value")
        self.assertEqual(params[-1].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        param = next(param for param in params if param.id == 'init_size_compartment_compartment')
        self.assertEqual(param.name, 'Initial size of compartment "compartment"')
        self.assertEqual(param.new_value, '1')
        self.assertEqual(param.target, "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment[@id='compartment']/@size")
        self.assertEqual(param.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        self.assertNotEqual(vars[0].id, 'time')

        variable = next((variable for variable in vars if variable.id == 'dynamics_species_mass'), None)
        self.assertEqual(variable.name, 'Dynamics of species "mass"')
        self.assertEqual(variable.symbol, None)
        self.assertEqual(variable.target, "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='mass']")
        self.assertEqual(variable.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        variable = next((variable for variable in vars if variable.id == 'compartment'), None)
        self.assertEqual(variable, None)

        variable = next(variable for variable in vars if variable.id == 'value_parameter_kswe')
        self.assertEqual(variable.name, 'Value of parameter "kswe"')
        self.assertEqual(variable.target, "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter[@id='kswe']/@value")
        self.assertEqual(variable.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        variable = next((variable for variable in vars if variable.id == 'kswe_prime'), None)
        self.assertEqual(variable, None)

    def test_core_steady_state_with_more_params_and_vars(self):
        params, vars = get_parameters_variables_for_simulation(
            self.CORE_FIXTURE_WITH_EXTRAS_PARAMS_VARS, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000019',
            include_compartment_sizes_in_simulation_variables=True,
            include_model_parameters_in_simulation_variables=True)

        self.assertEqual(params[0].id, 'init_amount_species_Trim')
        self.assertEqual(params[0].name, 'Initial amount of species "CDC28_Clb2_Sic1_Complex"')
        self.assertEqual(params[0].new_value, '0.084410675')
        self.assertEqual(params[0].target, "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='Trim']/@initialAmount")
        self.assertEqual(params[0].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        param = next(param for param in params if param.id == 'init_size_compartment_compartment')
        self.assertEqual(param.name, 'Initial size of compartment "compartment"')
        self.assertEqual(param.new_value, '1')
        self.assertEqual(param.target, "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment[@id='compartment']/@size")
        self.assertEqual(param.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        param = next(param for param in params if param.id == 'value_parameter_local_param')
        self.assertEqual(param.name, 'Value of parameter "local_param" of reaction "Clb-Sic dissociation"')
        self.assertEqual(param.new_value, '10')
        self.assertEqual(param.target, ("/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='R1']/sbml:kineticLaw"
                                        "/sbml:listOfParameters/sbml:parameter[@id='local_param']/@value"))
        self.assertEqual(param.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        variable = next(variable for variable in vars if variable.id == 'size_compartment_compartment')
        self.assertEqual(variable.name, 'Size of compartment "compartment"')
        self.assertEqual(variable.symbol, None)
        self.assertEqual(variable.target, "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment[@id='compartment']/@size")
        self.assertEqual(variable.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        variable = next(variable for variable in vars if variable.id == 'value_parameter_local_param')
        self.assertEqual(variable.name, 'Value of parameter "local_param" of reaction "Clb-Sic dissociation"')
        self.assertEqual(variable.symbol, None)
        self.assertEqual(variable.target, ("/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='R1']/sbml:kineticLaw"
                                           "/sbml:listOfParameters/sbml:parameter[@id='local_param']/@value"))
        self.assertEqual(variable.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

        params, vars = get_parameters_variables_for_simulation(
            self.CORE_FIXTURE_WITH_EXTRAS_PARAMS_VARS, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000019',
            include_compartment_sizes_in_simulation_variables=False,
            include_model_parameters_in_simulation_variables=False)
        self.assertNotEqual(next((param for param in params if param.id == 'init_size_compartment_compartment'), None), None)
        self.assertEqual(next((variable for variable in vars if variable.id == 'size_compartment_compartment'), None), None)
        self.assertEqual(next((variable for variable in vars if variable.id == 'value_parameter_local_param'), None), None)

    def test_core_one_step(self):
        params, vars = get_parameters_variables_for_simulation(self.CORE_FIXTURE, ModelLanguage.SBML, OneStepSimulation, 'KISAO_0000019')

    def test_core_time_course(self):
        params, vars = get_parameters_variables_for_simulation(
            self.CORE_FIXTURE, ModelLanguage.SBML, UniformTimeCourseSimulation, 'KISAO_0000019')

        self.assertEqual(vars[0].id, 'time')
        self.assertEqual(vars[0].name, 'Time')
        self.assertEqual(vars[0].symbol, Symbol.time)
        self.assertEqual(vars[0].target, None)
        self.assertEqual(vars[0].target_namespaces, {})

        self.assertEqual(vars[-1].id, 'dynamics_species_mass')
        self.assertEqual(vars[-1].name, 'Dynamics of species "mass"')
        self.assertEqual(vars[-1].symbol, None)
        self.assertEqual(vars[-1].target, "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='mass']")
        self.assertEqual(vars[-1].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level2/version4'})

    def test_core_time_course_l3(self):
        params, vars = get_parameters_variables_for_simulation(
            self.CORE_FIXTURE_L3, ModelLanguage.SBML, UniformTimeCourseSimulation, 'KISAO_0000019')

        param = next(param for param in params if param.id == 'value_parameter_k_PIP2hyd')
        self.assertEqual(param.name, 'Value of parameter "k_PIP2hyd" of reaction "PIP2_hyd"')
        self.assertEqual(param.new_value, '2.4')
        self.assertEqual(param.target, ("/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='PIP2_hyd']/sbml:kineticLaw"
                                        "/sbml:listOfLocalParameters/sbml:localParameter[@id='k_PIP2hyd']/@value"))
        self.assertEqual(param.target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level3/version1/core'})

    def test_fbc_steady_state_fba(self):
        params, vars = get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000437')

        self.assertEqual(params[0].id, 'value_parameter_cobra_default_lb')
        self.assertEqual(params[0].name, 'Value of parameter "cobra_default_lb"')
        self.assertEqual(params[0].target, "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter[@id='cobra_default_lb']/@value")
        self.assertEqual(params[0].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
        })
        self.assertEqual(params[0].new_value, '-1000')

        self.assertEqual(params[-1].id, 'value_parameter_R_EX_glc__D_e_lower_bound')
        self.assertEqual(params[-1].name, 'Value of parameter "R_EX_glc__D_e_lower_bound"')
        self.assertEqual(params[-1].target,
                         "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter[@id='R_EX_glc__D_e_lower_bound']/@value")
        self.assertEqual(params[-1].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
        })
        self.assertEqual(params[-1].new_value, '-10')

        self.assertEqual(vars[0].id, 'value_objective_obj')
        self.assertEqual(vars[0].name, 'Value of objective "obj"')
        self.assertEqual(vars[0].symbol, None)
        self.assertEqual(vars[0].target, "/sbml:sbml/sbml:model/fbc:listOfObjectives/fbc:objective[@fbc:id='obj']/@value")
        self.assertEqual(vars[0].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
            'fbc': 'http://www.sbml.org/sbml/level3/version1/fbc/version2',
        })

        self.assertEqual(vars[-1].id, 'flux_reaction_R_TPI')
        self.assertEqual(vars[-1].name, 'Flux of reaction "triose-phosphate isomerase"')
        self.assertEqual(vars[-1].symbol, None)
        self.assertEqual(vars[-1].target, "/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='R_TPI']/@flux")
        self.assertEqual(vars[-1].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level3/version1/core'})

    def test_fbc_steady_state_fva(self):
        params, vars = get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000526')

        self.assertEqual(vars[0].id, 'min_flux_reaction_R_ACALD')
        self.assertEqual(vars[0].name, 'Minimum flux of reaction "acetaldehyde dehydrogenase (acetylating)"')
        self.assertEqual(vars[0].symbol, None)
        self.assertEqual(vars[0].target, "/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='R_ACALD']/@minFlux")
        self.assertEqual(vars[0].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level3/version1/core'})

        self.assertEqual(vars[-1].id, 'max_flux_reaction_R_TPI')
        self.assertEqual(vars[-1].name, 'Maximum flux of reaction "triose-phosphate isomerase"')
        self.assertEqual(vars[-1].symbol, None)
        self.assertEqual(vars[-1].target, "/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='R_TPI']/@maxFlux")
        self.assertEqual(vars[-1].target_namespaces, {'sbml': 'http://www.sbml.org/sbml/level3/version1/core'})

    def test_fbc_one_step(self):
        with self.assertRaises(NotImplementedError):
            get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, OneStepSimulation, None)

    def test_fbc_time_course(self):
        with self.assertRaises(NotImplementedError):
            get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, UniformTimeCourseSimulation, None)

    def test_qual_steady_state(self):
        params, vars = get_parameters_variables_for_simulation(
            self.QUAL_FIXTURE, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000450')

        self.assertEqual(vars[0].id, 'level_species_erk')
        self.assertEqual(vars[0].name, 'Level of species "erk"')
        self.assertEqual(vars[0].symbol, None)
        self.assertEqual(vars[0].target, "/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies[@qual:id='erk']")
        self.assertEqual(vars[0].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
            'qual': 'http://www.sbml.org/sbml/level3/version1/qual/version1',
        })

    def test_qual_steady_state_with_extra_vars(self):
        params, vars = get_parameters_variables_for_simulation(
            self.QUAL_FIXTURE_WITH_EXTRAS_PARAMS_VARS, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000450',
            include_compartment_sizes_in_simulation_variables=True,
            include_model_parameters_in_simulation_variables=True)

        param = next((param for param in params if param.id == 'init_level_species_erk'), None)
        self.assertEqual(param.name, 'Initial level of species "erk"')
        self.assertEqual(param.target,
                         "/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies[@qual:id='erk']/@qual:initialLevel")
        self.assertEqual(param.target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
            'qual': 'http://www.sbml.org/sbml/level3/version1/qual/version1',
        })
        self.assertEqual(param.new_value, "1")

        param = next((param for param in params if param.id == 'init_size_compartment_main'), None)
        self.assertEqual(param.name, 'Initial size of compartment "main"')
        self.assertEqual(param.target,
                         "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment[@id='main']/@size")
        self.assertEqual(param.target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
        })
        self.assertEqual(param.new_value, "2.5")

        variable = next((variable for variable in vars if variable.id == 'size_compartment_main'), None)
        self.assertEqual(variable.name, 'Size of compartment "main"')
        self.assertEqual(variable.target,
                         "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment[@id='main']/@size")
        self.assertEqual(variable.target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
        })

        params, vars = get_parameters_variables_for_simulation(
            self.QUAL_FIXTURE_WITH_EXTRAS_PARAMS_VARS, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000450',
            include_compartment_sizes_in_simulation_variables=False,
            include_model_parameters_in_simulation_variables=False)

        self.assertNotEqual(next((param for param in params if param.id == 'init_level_species_erk'), None), None)
        self.assertNotEqual(next((param for param in params if param.id == 'init_size_compartment_main'), None), None)
        self.assertEqual(next((variable for variable in vars if variable.id == 'size_compartment_main'), None), None)

    def test_qual_one_step(self):
        params, vars = get_parameters_variables_for_simulation(self.QUAL_FIXTURE, ModelLanguage.SBML, OneStepSimulation, 'KISAO_0000450')

        self.assertEqual(vars[0].id, 'time')
        self.assertEqual(vars[0].name, 'Time')
        self.assertEqual(vars[0].symbol, Symbol.time)
        self.assertEqual(vars[0].target, None)
        self.assertEqual(vars[0].target_namespaces, {})

        self.assertEqual(vars[-1].id, 'level_species_nik')
        self.assertEqual(vars[-1].name, 'Level of species "nik"')
        self.assertEqual(vars[-1].symbol, None)
        self.assertEqual(vars[-1].target, "/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies[@qual:id='nik']")
        self.assertEqual(vars[-1].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
            'qual': 'http://www.sbml.org/sbml/level3/version1/qual/version1',
        })

    def test_qual_time_course(self):
        params, vars = get_parameters_variables_for_simulation(
            self.QUAL_FIXTURE, ModelLanguage.SBML, UniformTimeCourseSimulation, 'KISAO_0000450')

        self.assertEqual(vars[0].id, 'time')
        self.assertEqual(vars[0].name, 'Time')
        self.assertEqual(vars[0].symbol, Symbol.time)
        self.assertEqual(vars[0].target, None)
        self.assertEqual(vars[0].target_namespaces, {})

        self.assertEqual(vars[-1].id, 'level_species_nik')
        self.assertEqual(vars[-1].name, 'Level of species "nik"')
        self.assertEqual(vars[-1].symbol, None)
        self.assertEqual(vars[-1].target, "/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies[@qual:id='nik']")
        self.assertEqual(vars[-1].target_namespaces, {
            'sbml': 'http://www.sbml.org/sbml/level3/version1/core',
            'qual': 'http://www.sbml.org/sbml/level3/version1/qual/version1',
        })

    def test_error_handling(self):
        with self.assertRaises(FileNotFoundError):
            get_parameters_variables_for_simulation('DOES-NOT-EXIST', ModelLanguage.SBML, UniformTimeCourseSimulation, None)

        with self.assertRaises(ValueError):
            get_parameters_variables_for_simulation(__file__, ModelLanguage.SBML, UniformTimeCourseSimulation, None)

        with mock.patch.object(libsbml.Model, 'getNumPlugins', return_value=1):
            with mock.patch.object(libsbml.Model, 'getPlugin', return_value=mock.Mock(getPackageName=lambda: 'other')):
                with self.assertRaises(NotImplementedError):
                    get_parameters_variables_for_simulation(self.CORE_FIXTURE, ModelLanguage.SBML, UniformTimeCourseSimulation, None)

        with self.assertRaises(NotImplementedError):
            get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, None, None)

        with self.assertRaises(NotImplementedError):
            get_parameters_variables_for_simulation(self.FBC_FIXTURE, ModelLanguage.SBML, SteadyStateSimulation, 'KISAO_0000019')
