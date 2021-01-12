""" Common configuration for simulation tools

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2020-12-29
:Copyright: 2020, Center for Reproducible Biomedical Modeling
:License: MIT
"""

import os


class Config(object):
    """ Configuration

    Attributes:
        ALGORITHM_SUBSTITUTION_POLICY (:obj:`str`): algorithm substition policy
        REPORT_FORMATS (:obj:`list` of :obj:`str`): default formats to generate reports in
        PLOT_FORMATS (:obj:`list` of :obj:`str`): default formats to generate plots in
        H5_REPORTS_PATH (:obj:`str`): path to save reports in HDF5 format relative to base output directory
        REPORTS_PATH (:obj:`str`): path to save zip archive of reports relative to base output directory
        PLOTS_PATH (:obj:`str`): path to save zip archive of plots relative to base output directory
        BUNDLE_OUTPUTS (:obj:`bool`): indicates whether bundles of report and plot outputs should be produced
        KEEP_INDIVIDUAL_OUTPUTS (:obj:`bool`): indicates whether the individual output files should be kept
        LOG_PATH (:obj:`str`): path to save the execution status of a COMBINE/OMEX archive
        BIOSIMULATORS_API_ENDPOINT (:obj:`str`): URL for BioSimulators API
    """

    def __init__(self, ALGORITHM_SUBSTITUTION_POLICY, REPORT_FORMATS, PLOT_FORMATS,
                 H5_REPORTS_PATH, REPORTS_PATH, PLOTS_PATH, BUNDLE_OUTPUTS, KEEP_INDIVIDUAL_OUTPUTS,
                 LOG_PATH, BIOSIMULATORS_API_ENDPOINT):
        """
        Args:
            ALGORITHM_SUBSTITUTION_POLICY (:obj:`str`): algorithm substition policy
            REPORT_FORMATS (:obj:`list` of :obj:`str`): default formats to generate reports in
            PLOT_FORMATS (:obj:`list` of :obj:`str`): default formats to generate plots in
            H5_REPORTS_PATH (:obj:`str`): path to save reports in HDF5 format relative to base output directory
            REPORTS_PATH (:obj:`str`): path to save zip archive of reports relative to base output directory
            PLOTS_PATH (:obj:`str`): path to save zip archive of plots relative to base output directory
            BUNDLE_OUTPUTS (:obj:`bool`): indicates whether bundles of report and plot outputs should be produced
            KEEP_INDIVIDUAL_OUTPUTS (:obj:`bool`): indicates whether the individual output files should be kept
            LOG_PATH (:obj:`str`): path to save the execution status of a COMBINE/OMEX archive
            BIOSIMULATORS_API_ENDPOINT (:obj:`str`): URL for BioSimulators API
        """
        self.ALGORITHM_SUBSTITUTION_POLICY = ALGORITHM_SUBSTITUTION_POLICY
        self.REPORT_FORMATS = REPORT_FORMATS
        self.PLOT_FORMATS = PLOT_FORMATS
        self.H5_REPORTS_PATH = H5_REPORTS_PATH
        self.REPORTS_PATH = REPORTS_PATH
        self.PLOTS_PATH = PLOTS_PATH
        self.BUNDLE_OUTPUTS = BUNDLE_OUTPUTS
        self.KEEP_INDIVIDUAL_OUTPUTS = KEEP_INDIVIDUAL_OUTPUTS
        self.LOG_PATH = LOG_PATH
        self.BIOSIMULATORS_API_ENDPOINT = BIOSIMULATORS_API_ENDPOINT


def get_config():
    """ Get the configuration

    Returns:
        :obj:`Config`: configuration
    """
    return Config(
        ALGORITHM_SUBSTITUTION_POLICY=os.environ.get('ALGORITHM_SUBSTITUTION_POLICY', 'SIMILAR_VARIABLES'),
        REPORT_FORMATS=[format.strip().lower() for format in os.environ.get('REPORT_FORMATS', 'csv, h5').split(',')],
        PLOT_FORMATS=[format.strip().lower() for format in os.environ.get('PLOT_FORMATS', 'pdf').split(',')],
        H5_REPORTS_PATH=os.environ.get('H5_REPORTS_PATH', 'reports.h5'),
        REPORTS_PATH=os.environ.get('REPORTS_PATH', 'reports.zip'),
        PLOTS_PATH=os.environ.get('PLOTS_PATH', 'plots.zip'),
        BUNDLE_OUTPUTS=os.environ.get('BUNDLE_OUTPUTS', '1').lower() in ['1', 'true'],
        KEEP_INDIVIDUAL_OUTPUTS=os.environ.get('KEEP_INDIVIDUAL_OUTPUTS', '1').lower() in ['1', 'true'],
        LOG_PATH=os.environ.get('LOG_PATH', 'log.yml'),
        BIOSIMULATORS_API_ENDPOINT=os.environ.get('BIOSIMULATORS_API_ENDPOINT', 'https://api.biosimulators.org/'),
    )
