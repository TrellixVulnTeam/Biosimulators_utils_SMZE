""" Utilities for executing tasks in SED documents

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2020-12-06
:Copyright: 2020, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from ..config import get_config
from ..plot.data_model import PlotFormat
from ..report.data_model import DataGeneratorVariableResults, DataGeneratorResults, OutputResults, ReportFormat
from ..report.io import ReportWriter
from .data_model import SedDocument, Task, Report, Plot2D, Plot3D, SedmlFeatureNotSupportedWarning, IllogicalSedmlWarning
from .io import SedmlSimulationReader
from .utils import apply_changes_to_xml_model, get_variables_for_task, calc_data_generator_results
import copy
import numpy
import os
import pandas
import tempfile
import types  # noqa: F401
import warnings


__all__ = [
    'exec_doc',
]


def exec_doc(doc, working_dir, task_executer, base_out_path, rel_out_path=None,
             apply_xml_model_changes=False, report_formats=None, plot_formats=None,
             indent=0):
    """ Execute the tasks specified in a SED document and generate the specified outputs

    Args:
        doc (:obj:`SedDocument` of :obj:`str`): SED document or a path to SED-ML file which defines a SED document
        working_dir (:obj:`str`): working directory of the SED document (path relative to which models are located)
        task_executer (:obj:`types.FunctionType`): function to execute each task in the SED-ML file.
            The function must implement the following interface::

                def exec_task(task, variables):
                    ''' Execute a simulation and return its results

                    Args:
                       task (:obj:`Task`): task
                       variables (:obj:`list` of :obj:`DataGeneratorVariable`): variables that should be recorded

                    Returns:
                       :obj:`DataGeneratorVariableResults`: results of variables
                    '''
                    pass

        out_path (:obj:`str`): path to store the outputs

            * CSV: directory in which to save outputs to files
              ``{out_path}/{rel_out_path}/{report.id}.csv``
            * HDF5: directory in which to save a single HDF5 file (``{out_path}/reports.h5``),
              with reports at keys ``{rel_out_path}/{report.id}`` within the HDF5 file

        rel_out_path (:obj:`str`, optional): path relative to :obj:`out_path` to store the outputs
        apply_xml_model_changes (:obj:`bool`, optional): if :obj:`True`, apply any model changes specified in the SED-ML file before
            calling :obj:`task_executer`.
        report_formats (:obj:`list` of :obj:`ReportFormat`, optional): report format (e.g., csv or h5)
        plot_formats (:obj:`list` of :obj:`PlotFormat`, optional): plot format (e.g., pdf)
        indent (:obj:`int`, optional): degree to indent status messages
    """
    # process arguments
    if not isinstance(doc, SedDocument):
        doc = SedmlSimulationReader().run(doc)
    else:
        doc = copy.deepcopy(doc)

    if report_formats is None:
        report_formats = [ReportFormat(format_value) for format_value in get_config().REPORT_FORMATS]

    if plot_formats is None:
        plot_formats = [PlotFormat(format_value) for format_value in get_config().PLOT_FORMATS]

    # apply changes to models
    modified_model_filenames = []
    for model in doc.models:
        if not os.path.isabs(model.source):
            model.source = os.path.join(working_dir, model.source)

        if apply_xml_model_changes and model.changes:
            original_model_filename = model.source

            modified_model_file, modified_model_filename = tempfile.mkstemp(suffix='.xml')
            os.close(modified_model_file)

            apply_changes_to_xml_model(model.changes, original_model_filename, modified_model_filename)

            model.source = modified_model_filename

            modified_model_filenames.append(modified_model_filename)

    # execute simulations
    variable_results = DataGeneratorVariableResults()
    doc.tasks.sort(key=lambda task: task.id)
    print('{}Found {} tasks\n{}{}'.format(' ' * 2 * indent,
                                          len(doc.tasks),
                                          ' ' * 2 * (indent + 1),
                                          ('\n' + ' ' * 2 * (indent + 1)).join([task.id for task in doc.tasks])))
    for i_task, task in enumerate(doc.tasks):
        print('{}Executing task {}: {}'.format(' ' * 2 * indent, i_task + 1, task.id))
        if isinstance(task, Task):
            # get a list of the variables that the task needs to record
            task_vars = get_variables_for_task(doc, task)

            # execute task and record variables
            task_variable_results = task_executer(task, task_vars)

            for var in task_vars:
                variable_results[var.id] = task_variable_results.get(var.id, None)
                if variable_results[var.id] is None:
                    raise ValueError('Variable {} must be generated for task {}'.format(var.id, task.id))

        else:
            raise NotImplementedError('Tasks of type {} are not supported'.format(task.__class__.__name__))

    # calculate data generators
    data_gen_results = DataGeneratorResults()
    for data_gen in doc.data_generators:
        data_gen_results[data_gen.id] = calc_data_generator_results(data_gen, variable_results)

    # generate outputs
    report_results = OutputResults()
    for output in doc.outputs:
        if isinstance(output, Report):
            dataset_labels = []
            dataset_results = []
            dataset_shapes = set()

            for data_set in output.data_sets:
                dataset_labels.append(data_set.label)
                data_gen_res = data_gen_results[data_set.data_generator.id]
                dataset_results.append(data_gen_res)
                dataset_shapes.add(data_gen_res.shape)

            if len(dataset_shapes) > 1:
                raise ValueError('Data generators for report {} must have consistent shapes'.format(output.id))

            if len(set(dataset_labels)) < len(dataset_labels):
                warnings.warn('To facilitate machine interpretation, data sets should have unique ids',
                              IllogicalSedmlWarning)

            output_df = pandas.DataFrame(numpy.array(dataset_results), index=dataset_labels)
            report_results[output.id] = output_df

            for report_format in report_formats:
                ReportWriter().run(output_df,
                                   base_out_path,
                                   os.path.join(rel_out_path, output.id) if rel_out_path else output.id,
                                   format=report_format)

        elif isinstance(output, Plot2D):
            warnings.warn('Output {} skipped because outputs of type {} are not yet supported'.format(
                output.id, output.__class__.__name__), SedmlFeatureNotSupportedWarning)
            # write_plot_2d()

        elif isinstance(output, Plot3D):
            warnings.warn('Output {} skipped because outputs of type {} are not yet supported'.format(
                output.id, output.__class__.__name__), SedmlFeatureNotSupportedWarning)
            # write_plot_3d()

        else:
            raise NotImplementedError('Outputs of type {} are not supported'.format(output.__class__.__name__))

    # cleanup modified models
    for modified_model_filename in modified_model_filenames:
        os.remove(modified_model_filename)

    return (report_results, variable_results)
