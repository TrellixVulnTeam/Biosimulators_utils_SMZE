""" Utilities for working with RBA models

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-28
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from ...sedml.data_model import (  # noqa: F401
    ModelAttributeChange, Variable,
    Simulation, SteadyStateSimulation,
    Algorithm,
    )
from ...utils.core import flatten_nested_list_of_strings
from .validation import validate_model
import rba
import types  # noqa: F401

__all__ = ['get_parameters_variables_for_simulation']


def get_parameters_variables_for_simulation(model_filename, model_language, simulation_type, algorithm_kisao_id=None,
                                            include_compartment_sizes_in_simulation_variables=False,
                                            include_model_parameters_in_simulation_variables=False):
    """ Get the possible observables for a simulation of a model

    Args:
        model_filename (:obj:`str`): path to model file
        model_language (:obj:`str`): model language (e.g., ``urn:sedml:language:rba``)
        simulation_type (:obj:`types.Type`): subclass of :obj:`Simulation`
        algorithm_kisao_id (:obj:`str`, optional): KiSAO id of the algorithm for simulating the model (e.g., ``KISAO_0000669``
            for RBA)
        include_compartment_sizes_in_simulation_variables (:obj:`bool`, optional): whether to include the sizes of
            non-constant SBML compartments with assignment rules among the returned SED variables
        include_model_parameters_in_simulation_variables (:obj:`bool`, optional): whether to include the values of
            non-constant SBML parameters with assignment rules among the returned SED variables

    Returns:
        :obj:`list` of :obj:`ModelAttributeChange`: possible attributes of a model that can be changed and their default values
        :obj:`list` of :obj:`Simulation`: simulations of the model
        :obj:`list` of :obj:`Variable`: possible observables for a simulation of the model
    """
    # check model file exists and is valid
    errors, _, model = validate_model(model_filename)
    if errors:
        raise ValueError('Model file `{}` is not a valid RBA file.\n  {}'.format(
            model_filename, flatten_nested_list_of_strings(errors).replace('\n', '\n  ')))

    if simulation_type not in [SteadyStateSimulation]:
        raise NotImplementedError('`simulation_type` must be `SteadyStateSimulation`')

    # parameters
    params = []
    for function in model.parameters.functions:
        for parameter in function.parameters:
            params.append(ModelAttributeChange(
                id='parameter_{}_{}'.format(function.id, parameter.id),
                name='Value of parameter "{}" of function "{}"'.format(parameter.id, function.id),
                target='parameters.functions.{}.parameters.{}'.format(function.id, parameter.id),
                new_value=str(parameter.value),
            ))

    # simulation
    sim = SteadyStateSimulation(
        id='simulation',
        algorithm=Algorithm(
            kisao_id='KISAO_0000669',
        )
    )

    # observables
    vars = []

    vars.append(Variable(
        id='variable_objective',
        name='Value of objective',
        target='objective',
    ))

    constraint_matrix = rba.ConstraintMatrix(model)

    for row_name in constraint_matrix.row_names:
        vars.append(Variable(
            id='variable_variable_{}'.format(row_name),
            name='Primal of variable "{}"'.format(row_name),
            target='variables.{}'.format(row_name),
        ))

    for col_name in constraint_matrix.col_names:
        vars.append(Variable(
            id='variable_constraint_{}'.format(col_name),
            name='Dual of constraint "{}"'.format(col_name),
            target='constraints.{}'.format(col_name),
        ))

    return (params, [sim], vars)
