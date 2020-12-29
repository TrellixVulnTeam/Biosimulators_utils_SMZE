""" Data model for SED

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2020-12-06
:Copyright: 2020, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from ..biosimulations.data_model import Metadata  # noqa: F401
from ..utils.core import are_lists_equal, none_sorted
import abc
import enum
import math
import mpmath
import numpy  # noqa: F401


__all__ = [
    'ModelLanguage',
    'DataGeneratorVariableSymbol',
    'SedDocument',
    'Simulation',
    'SteadyStateSimulation',
    'OneStepSimulation',
    'UniformTimeCourseSimulation',
    'Algorithm',
    'AlgorithmParameterChange',
    'Model',
    'ModelChange',
    'ModelAttributeChange',
    'AbstractTask',
    'Task',
    'DataGenerator',
    'DataGeneratorVariable',
    'DataGeneratorParameter',
    'Output',
    'Report',
    'DataSet',
    'Plot2D',
    'Plot3D',
    'AxisScale',
    'Curve',
    'Surface',
]


class ModelLanguage(str, enum.Enum):
    """ Model language """
    BGNL = 'urn:sedml:language:bgnl'
    CellML = 'urn:sedml:language:cellml'
    NeuroML = 'urn:sedml:language:neuroml'
    SBML = 'urn:sedml:language:sbml'
    VCML = 'urn:sedml:language:vcml'


class DataGeneratorVariableSymbol(str, enum.Enum):
    """ Variable sumbol """
    time = 'urn:sedml:symbol:time'


class SedDocument(object):
    """ A SED-ML document

    Attributes:
        level (:obj:`int`): level
        version (:obj:`int`): version
        models (:obj:`list` of :obj:`Model`): models
        simulations (:obj:`list` of :obj:`Simulation`): simulations
        tasks (:obj:`list` of :obj:`AbstractTask`): tasks
        data_generators (:obj:`list` of :obj:`DataGenerator`): data generators
        outputs (:obj:`list` of :obj:`Output`): outputs
        metadata (:obj:`Metadata`): metadata
    """

    def __init__(self, level=1, version=3, models=None, simulations=None, tasks=None, data_generators=None, outputs=None, metadata=None):
        """
        Args:
            level (:obj:`int`, optional): level
            version (:obj:`int`, optional): version
            models (:obj:`list` of :obj:`Model`, optional): models
            simulations (:obj:`list` of :obj:`Simulation`, optional): simulations
            tasks (:obj:`list` of :obj:`AbstractTask`, optional): tasks
            data_generators (:obj:`list` of :obj:`DataGenerator`, optional): data generators
            outputs (:obj:`list` of :obj:`Output`, optional): outputs
            metadata (:obj:`Metadata`, optional): metadata
        """
        self.level = level
        self.version = version
        self.models = models or []
        self.simulations = simulations or []
        self.tasks = tasks or []
        self.data_generators = data_generators or []
        self.outputs = outputs or []
        self.metadata = metadata

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (
            self.level,
            self.version,
            tuple(none_sorted(model.to_tuple() for model in self.models)),
            tuple(none_sorted(simulation.to_tuple() for simulation in self.simulations)),
            tuple(none_sorted(task.to_tuple() for task in self.tasks)),
            tuple(none_sorted(data_generator.to_tuple() for data_generator in self.data_generators)),
            tuple(none_sorted(output.to_tuple() for output in self.outputs)),
            self.metadata.to_tuple() if self.metadata else None,
        )

    def is_equal(self, other):
        """ Determine if SED-ML documents are equal

        Args:
            other (:obj:`Simulation`): another SED-ML document

        Returns:
            :obj:`bool`: :obj:`True`, if two SED-ML documents are equal
        """
        return self.__class__ == other.__class__ \
            and self.level == other.level \
            and self.version == other.version \
            and are_lists_equal(self.models, other.models) \
            and are_lists_equal(self.simulations, other.simulations) \
            and are_lists_equal(self.tasks, other.tasks) \
            and are_lists_equal(self.data_generators, other.data_generators) \
            and are_lists_equal(self.outputs, other.outputs) \
            and ((self.metadata is None and self.metadata == other.metadata)
                 or (self.metadata is not None and self.metadata.is_equal(other.metadata)))


class Simulation(abc.ABC):
    """ A simulation

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        algorithm (:obj:`Algorithm`): algorithm
    """

    def __init__(self, id=None, name=None, algorithm=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            algorithm (:obj:`Algorithm`, optional): algorithm
        """
        self.id = id
        self.name = name
        self.algorithm = algorithm

    @abc.abstractmethod
    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        pass  # pragma: no cover

    def is_equal(self, other):
        """ Determine if simulations are equal

        Args:
            other (:obj:`Simulation`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two simulations are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and ((self.algorithm is None and self.algorithm == other.algorithm)
                 or (self.algorithm is not None and self.algorithm.is_equal(other.algorithm)))


class SteadyStateSimulation(Simulation):
    """ A steady-state simulation

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        algorithm (:obj:`Algorithm`): algorithm
    """

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.algorithm.to_tuple() if self.algorithm else None)


class OneStepSimulation(Simulation):
    """ A single simulation step

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        algorithm (:obj:`Algorithm`): algorithm
        step (:obj:`float`): step
    """

    def __init__(self, id=None, name=None, algorithm=None, step=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            algorithm (:obj:`Algorithm`, optional): algorithm
            step (:obj:`float`, optional): step
        """
        super(OneStepSimulation, self).__init__(id=id, name=name, algorithm=algorithm)
        self.step = step

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.algorithm.to_tuple() if self.algorithm else None, self.step)

    def is_equal(self, other):
        """ Determine if simulations are equal

        Args:
            other (:obj:`OneStepSimulation`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two simulations are equal
        """
        return super(OneStepSimulation, self).is_equal(other) \
            and self.step == other.step


class UniformTimeCourseSimulation(Simulation):
    """ A uniform time course simulation

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        algorithm (:obj:`Algorithm`): algorithm
        initial_time (:obj:`float`): initial time
        output_start_time (:obj:`float`): output start time
        output_end_time (:obj:`float`): output end time
        number_of_points (:obj:`int`): number of time points
    """

    def __init__(self, id=None, name=None, algorithm=None,
                 initial_time=None, output_start_time=None, output_end_time=None, number_of_points=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            algorithm (:obj:`Algorithm`, optional): algorithm
            initial_time (:obj:`float`, optional): initial time
            output_start_time (:obj:`float`, optional): output start time
            output_end_time (:obj:`float`, optional): output end time
            number_of_points (:obj:`int`, optional): number of time points
        """
        super(UniformTimeCourseSimulation, self).__init__(id=id, name=name, algorithm=algorithm)
        self.initial_time = initial_time
        self.output_start_time = output_start_time
        self.output_end_time = output_end_time
        self.number_of_points = number_of_points

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.algorithm.to_tuple() if self.algorithm else None,
                self.initial_time, self.output_start_time, self.output_end_time, self.number_of_points)

    def is_equal(self, other):
        """ Determine if simulations are equal

        Args:
            other (:obj:`UniformTimeCourseSimulation`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two simulations are equal
        """
        return super(UniformTimeCourseSimulation, self).is_equal(other) \
            and self.initial_time == other.initial_time \
            and self.output_start_time == other.output_start_time \
            and self.output_end_time == other.output_end_time \
            and self.number_of_points == other.number_of_points


class Algorithm(object):
    """ A simulation algorithm

    Attributes:
        kisao_id (:obj:`str`): KiSAO id (e.g., `KISAO_0000029`)
        changes (:obj:`list` of :obj:`AlgorithmParameterChange`): parameter changes
    """

    def __init__(self, kisao_id=None, changes=None):
        """
        Args:
            kisao_id (:obj:`str`, optional): KiSAO id (e.g., `KISAO_0000029`)
            changes (:obj:`list` of :obj:`AlgorithmParameterChange`, optional): parameter changes
        """
        self.kisao_id = kisao_id
        self.changes = changes or []

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.kisao_id,
                tuple(none_sorted(change.to_tuple() for change in self.changes)))

    def is_equal(self, other):
        """ Determine if algorithms are equal

        Args:
            other (:obj:`Algorithm`): another algorithm

        Returns:
            :obj:`bool`: :obj:`True`, if two algorithms are equal
        """
        return self.__class__ == other.__class__ \
            and self.kisao_id == other.kisao_id \
            and are_lists_equal(self.changes, other.changes)


class AlgorithmParameterChange(object):
    """ A changed parameter of an algorithm

    Attributes:
        kisao_id (:obj:`str`): KiSAO id (e.g., `KISAO_0000029`)
        new_value (:obj:`str`): new value
    """

    def __init__(self, kisao_id=None, new_value=None):
        """
        Args:
            kisao_id (:obj:`str`, optional): KiSAO id (e.g., `KISAO_0000029`)
            new_value (:obj:`str`, optional): new value
        """
        self.kisao_id = kisao_id
        self.new_value = new_value

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.kisao_id, self.new_value)

    def is_equal(self, other):
        """ Determine if parameter changes are equal

        Args:
            other (:obj:`AlgorithmParameterChange`): another parameter change

        Returns:
            :obj:`bool`: :obj:`True`, if two parameter changes are equal
        """
        return self.__class__ == other.__class__ \
            and self.kisao_id == other.kisao_id \
            and self.new_value == other.new_value


class Model(object):
    """ A model

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        source (:obj:`str`): path to the model file
        language (:obj:`str`): URN of the format of the model
        changes (:obj:`list` of :obj:`ModelChange`): model changes
    """

    def __init__(self, id=None, name=None, source=None, language=None, changes=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            source (:obj:`str`), optional: path to the model file
            language (:obj:`str`, optional): URN of the format of the model
            changes (:obj:`list` of :obj:`ModelChange`, optional): model changes
        """
        self.id = id
        self.name = name
        self.source = source
        self.language = language
        self.changes = changes or []

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.source, self.language,
                tuple(none_sorted(change.to_tuple() for change in self.changes)))

    def is_equal(self, other):
        """ Determine if models are equal

        Args:
            other (:obj:`Model`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two models are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.source == other.source \
            and self.language == other.language \
            and are_lists_equal(self.changes, other.changes)


class ModelChange(abc.ABC):
    """ A change to a model

    Attributes:
        name (:obj:`str`): name
        target (:obj:`str`): path to the model element that should be changed
    """

    def __init__(self, name=None, target=None):
        """
        Args:
            name (:obj:`str`, optional): name
            target (:obj:`str`, optional): path to the model element that should be changed
        """
        self.name = name
        self.target = target

    @abc.abstractmethod
    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        pass  # pragma: no cover

    def is_equal(self, other):
        """ Determine if model changes are equal

        Args:
            other (:obj:`ModelChange`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two model changes are equal
        """
        return self.__class__ == other.__class__ \
            and self.name == other.name \
            and self.target == other.target


class ModelAttributeChange(ModelChange):
    """ A change of an attribute of a model

    Attributes:
        target (:obj:`str`): path to the model element that should be changed
        new_value (:obj:`str`): new value
    """

    def __init__(self, target=None, new_value=None):
        """
        Args:
            target (:obj:`str`, optional): path to the model element that should be changed
            new_value (:obj:`str`, optional): new value
        """
        super(ModelAttributeChange, self).__init__(target=target)
        self.new_value = new_value

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.target, self.new_value)

    def is_equal(self, other):
        """ Determine if model attribute changes are equal

        Args:
            other (:obj:`ModelAttributeChange`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two model attribute changes are equal
        """
        return super(ModelAttributeChange, self).is_equal(other) \
            and self.new_value == other.new_value


class AbstractTask(abc.ABC):
    """ Base class for tasks

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
    """

    def __init__(self, id=None, name=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
        """
        self.id = id
        self.name = name

    @abc.abstractmethod
    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        pass  # pragma: no cover

    def is_equal(self, other):
        """ Determine if tasks are equal

        Args:
            other (:obj:`AbstractTask`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two tasks are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name


class Task(AbstractTask):
    """ A task

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        model (:obj:`Model`): model
        simulation (:obj:`Simulation`): simulation
    """

    def __init__(self, id=None, name=None, model=None, simulation=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            model (:obj:`Model`, optional): model
            simulation (:obj:`Simulation`, optional): simulation
        """
        super(Task, self).__init__(id=id, name=name)
        self.model = model
        self.simulation = simulation

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                self.model.to_tuple() if self.model else None,
                self.simulation.to_tuple() if self.simulation else None)

    def is_equal(self, other):
        """ Determine if tasks are equal

        Args:
            other (:obj:`Task`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two tasks are equal
        """
        return super(Task, self).is_equal(other) \
            and ((self.model is None and self.model == other.model)
                 or (self.model is not None and self.model.is_equal(other.model))) \
            and ((self.simulation is None and self.simulation == other.simulation)
                 or (self.simulation is not None and self.simulation.is_equal(other.simulation)))


class DataGenerator(object):
    """ A data generator

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        variables (:obj:`list` of :obj:`DataGeneratorVariable`): variables
        parameters (:obj:`list` of :obj:`DataGeneratorParameters`): variables
        math (:obj:`str`): mathematical expression
    """

    def __init__(self, id=None, name=None, variables=None, parameters=None, math=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            variables (:obj:`list` of :obj:`DataGeneratorVariable`, optional): variables
            parameters (:obj:`list` of :obj:`DataGeneratorParameters`, optional): variables
            math (:obj:`str`, optional): mathematical expression
        """
        self.id = id
        self.name = name
        self.variables = variables or []
        self.parameters = parameters or []
        self.math = math

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                tuple(none_sorted(variable.to_tuple() for variable in self.variables)),
                tuple(none_sorted(parameter.to_tuple() for parameter in self.parameters)),
                self.math)

    def is_equal(self, other):
        """ Determine if data generators
         are equal

        Args:
            other (:obj:`DataGenerator`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two data generators are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and are_lists_equal(self.variables, other.variables) \
            and are_lists_equal(self.parameters, other.parameters) \
            and self.math == other.math


class DataGeneratorVariable(object):
    """ A model variable involved in a data generator

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        target (:obj:`str`): target
        symbol (:obj:`str`): symbol
        task (:obj:`AbstractTask`): task
        model (:obj:`Model`): model
    """

    def __init__(self, id=None, name=None, target=None, symbol=None, task=None, model=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            target (:obj:`str`, optional): target
            symbol (:obj:`str`, optional): symbol
            task (:obj:`AbstractTask`, optional): task
            model (:obj:`Model`, optional): model
        """
        self.id = id
        self.name = name
        self.target = target
        self.symbol = symbol
        self.task = task
        self.model = model

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.target, self.symbol,
                self.task.to_tuple() if self.task else None,
                self.model.to_tuple() if self.model else None)

    def is_equal(self, other):
        """ Determine if data generator variables are equal

        Args:
            other (:obj:`DataGeneratorVariable`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two data generator variables are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.target == other.target \
            and self.symbol == other.symbol \
            and ((self.task is None and self.task == other.task)
                 or (self.task is not None and self.task.is_equal(other.task))) \
            and ((self.model is None and self.model == other.model)
                 or (self.model is not None and self.model.is_equal(other.model)))


class DataGeneratorParameter(object):
    """ A parameter involved in a data generator

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        value (:obj:`float`): value
    """

    def __init__(self, id=None, name=None, value=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            value (:obj:`float`, optional): value
        """
        self.id = id
        self.name = name
        self.value = value

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.value)

    def is_equal(self, other):
        """ Determine if data generator parameters are equal

        Args:
            other (:obj:`DataGeneratorParameter`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two data generator parameters are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.value == other.value


MATHEMATICAL_FUNCTIONS = {
    'root': lambda x, n: x**(1 / float(n)),
    'abs': abs,
    'exp': math.exp,
    'ln': math.log,
    'log': math.log,
    'floor': math.floor,
    'ceiling': math.ceil,
    'factorial': math.factorial,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sec': mpmath.sec,
    'csc': mpmath.csc,
    'cot': mpmath.cot,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'sech': mpmath.sech,
    'csch': mpmath.csch,
    'coth': mpmath.coth,
    'arcsin': math.asin,
    'arccos': math.acos,
    'arctan': math.atan,
    'arcsec': mpmath.asec,
    'arccsc': mpmath.acsc,
    'arccot': mpmath.acot,
    'arcsinh': math.asinh,
    'arccosh': math.acosh,
    'arctanh': math.atanh,
    'arcsech': mpmath.asech,
    'arccsch': mpmath.acsch,
    'arccoth': mpmath.acoth,
}


class Output(abc.ABC):
    """ An output

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
    """

    def __init__(self, id=None, name=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
        """
        self.id = id
        self.name = name

    @abc.abstractmethod
    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        pass  # pragma: no cover

    def is_equal(self, other):
        """ Determine if outputs are equal

        Args:
            other (:obj:`Output`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two outputs are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name


class Report(Output):
    """ A report

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        data_sets (:obj:`list` of :obj:`DataSet`): data sets
    """

    def __init__(self, id=None, name=None, data_sets=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            data_sets (:obj:`list` of :obj:`DataSet`, optional): data sets
        """
        super(Report, self).__init__(id=id, name=name)
        self.data_sets = data_sets or []

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                tuple(none_sorted(data_set.to_tuple() for data_set in self.data_sets)))

    def is_equal(self, other):
        """ Determine if reports are equal

        Args:
            other (:obj:`Report`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two reports are equal
        """
        return super(Report, self).is_equal(other) \
            and are_lists_equal(self.data_sets, other.data_sets)


class DataSet(object):
    """ A data set in a report

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        label (:obj:`str`): label
        data_generator (:obj:`DataGenerator`): data generator
    """

    def __init__(self, id=None, name=None, label=None, data_generator=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            label (:obj:`str`, optional): label
            data_generator (:obj:`DataGenerator`, optional): data generator
        """
        self.id = id
        self.name = name
        self.label = label
        self.data_generator = data_generator

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name, self.label,
                self.data_generator.to_tuple() if self.data_generator is not None else None)

    def is_equal(self, other):
        """ Determine if data sets are equal

        Args:
            other (:obj:`DataSet`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two data sets are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.label == other.label \
            and ((self.data_generator is None and self.data_generator == other.data_generator)
                 or (self.data_generator is not None and self.data_generator.is_equal(other.data_generator))) \



class Plot2D(Output):
    """ A 2D plot

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        curves (:obj:`list` of :obj:`Curve`): curves
    """

    def __init__(self, id=None, name=None, curves=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            curves (:obj:`list` of :obj:`Curve`, optional): curves
        """
        self.id = id
        self.name = name
        self.curves = curves or []

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                tuple(none_sorted(curve.to_tuple() for curve in self.curves)))

    def is_equal(self, other):
        """ Determine if plots are equal

        Args:
            other (:obj:`Plot2D`): another plot

        Returns:
            :obj:`bool`: :obj:`True`, if two plots are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and are_lists_equal(self.curves, other.curves)


class Plot3D(Output):
    """ A 3D plot

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        surfaces (:obj:`list` of :obj:`Surface`): surfaces
    """

    def __init__(self, id=None, name=None, surfaces=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            surfaces (:obj:`list` of :obj:`Surface`, optional): surfaces
        """
        self.id = id
        self.name = name
        self.surfaces = surfaces or []

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                tuple(none_sorted(surface.to_tuple() for surface in self.surfaces)))

    def is_equal(self, other):
        """ Determine if plots are equal

        Args:
            other (:obj:`Plot3D`): another plot

        Returns:
            :obj:`bool`: :obj:`True`, if two plots are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and are_lists_equal(self.surfaces, other.surfaces)


class AxisScale(str, enum.Enum):
    """ Scale of an axis """
    linear = 'linear'
    log = 'log'


class Curve(object):
    """ A curve in a 2D plot

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        x_scale (:obj:`AxisScale`): x axis scale
        y_scale (:obj:`AxisScale`): y axis scale
        x_data_generator (:obj:`DataGenerator`): x data generator
        y_data_generator (:obj:`DataGenerator`): y data generator
    """

    def __init__(self, id=None, name=None, x_scale=None, y_scale=None, x_data_generator=None, y_data_generator=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            x_scale (:obj:`AxisScale`, optional): x axis scale
            y_scale (:obj:`AxisScale`, optional): y axis scale
            x_data_generator (:obj:`DataGenerator`, optional): x data generator
            y_data_generator (:obj:`DataGenerator`, optional): y data generator
        """
        self.id = id
        self.name = name
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.x_data_generator = x_data_generator
        self.y_data_generator = y_data_generator

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                self.x_scale.value if self.x_scale else None,
                self.y_scale.value if self.y_scale else None,
                self.x_data_generator.to_tuple() if self.x_data_generator else None,
                self.y_data_generator.to_tuple() if self.y_data_generator else None)

    def is_equal(self, other):
        """ Determine if curves are equal

        Args:
            other (:obj:`Curve`): another curve

        Returns:
            :obj:`bool`: :obj:`True`, if two curves are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.x_scale == other.x_scale \
            and self.y_scale == other.y_scale \
            and ((self.x_data_generator is None and self.x_data_generator == other.x_data_generator)
                 or (self.x_data_generator is not None and self.x_data_generator.is_equal(other.x_data_generator))) \
            and ((self.y_data_generator is None and self.y_data_generator == other.y_data_generator)
                 or (self.y_data_generator is not None and self.y_data_generator.is_equal(other.y_data_generator)))


class Surface(object):
    """ A surface in a 3D plot

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        x_scale (:obj:`AxisScale`): x axis scale
        y_scale (:obj:`AxisScale`): y axis scale
        z_scale (:obj:`AxisScale`): z axis scale
        x_data_generator (:obj:`DataGenerator`): x data generator
        y_data_generator (:obj:`DataGenerator`): y data generator
        z_data_generator (:obj:`DataGenerator`): z data generator
    """

    def __init__(self, id=None, name=None,
                 x_scale=None, y_scale=None, z_scale=None,
                 x_data_generator=None, y_data_generator=None, z_data_generator=None):
        """
        Args:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            x_scale (:obj:`AxisScale`, optional): x axis scale
            y_scale (:obj:`AxisScale`, optional): y axis scale
            z_scale (:obj:`AxisScale`, optional): z axis scale
            x_data_generator (:obj:`DataGenerator`, optional): x data generator
            y_data_generator (:obj:`DataGenerator`, optional): y data generator
            z_data_generator (:obj:`DataGenerator`, optional): z data generator
        """
        self.id = id
        self.name = name
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.z_scale = z_scale
        self.x_data_generator = x_data_generator
        self.y_data_generator = y_data_generator
        self.z_data_generator = z_data_generator

    def to_tuple(self):
        """ Get a tuple representation

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation
        """
        return (self.id, self.name,
                self.x_scale.value if self.x_scale else None,
                self.y_scale.value if self.y_scale else None,
                self.z_scale.value if self.z_scale else None,
                self.x_data_generator.to_tuple() if self.x_data_generator else None,
                self.y_data_generator.to_tuple() if self.y_data_generator else None,
                self.z_data_generator.to_tuple() if self.z_data_generator else None)

    def is_equal(self, other):
        """ Determine if surfaces are equal

        Args:
            other (:obj:`Surface`): another surface

        Returns:
            :obj:`bool`: :obj:`True`, if two surfaces are equal
        """
        return self.__class__ == other.__class__ \
            and self.id == other.id \
            and self.name == other.name \
            and self.x_scale == other.x_scale \
            and self.y_scale == other.y_scale \
            and self.z_scale == other.z_scale \
            and ((self.x_data_generator is None and self.x_data_generator == other.x_data_generator)
                 or (self.x_data_generator is not None and self.x_data_generator.is_equal(other.x_data_generator))) \
            and ((self.y_data_generator is None and self.y_data_generator == other.y_data_generator)
                 or (self.y_data_generator is not None and self.y_data_generator.is_equal(other.y_data_generator))) \
            and ((self.z_data_generator is None and self.z_data_generator == other.z_data_generator)
                 or (self.z_data_generator is not None and self.z_data_generator.is_equal(other.z_data_generator)))
