""" Methods for validating XPP files

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-06
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from ...config import Config  # noqa: F401
import collections
import glob
import os
import re
import subprocess
import tempfile


__all__ = ['validate_model', 'get_xpp_input_configuration_from_directory', 'sanitize_model']


def validate_model(filename,
                   set_filename=None, parameter_filename=None, initial_conditions_filename=None,
                   name=None, config=None):
    """ Check that a model is valid

    Args:
        filename (:obj:`str`): path to model file or directory with ``.ode`` and possibly set (``.set``),
            parameter (``.par``), andd initial conditions (``.ic``) files
        set_filename (:obj:`str`, optional): path to XPP set file
        parameter_filename (:obj:`str`, optional): path to XPP parameters file
        initial_conditions_filename (:obj:`str`, optional): path to XPP initial conditions file
        name (:obj:`str`, optional): name of model for use in error messages
        config (:obj:`Config`, optional): whether to fail on missing includes

    Returns:
        :obj:`tuple`:

            * nested :obj:`list` of :obj:`str`: nested list of errors (e.g., required ids missing or ids not unique)
            * nested :obj:`list` of :obj:`str`: nested list of errors (e.g., required ids missing or ids not unique)
            * :obj:`dict`: values of parameters of initial conditions of variables
    """
    errors = []
    warnings = []
    simulation = None

    if filename and os.path.isdir(filename):
        (
            filename, temp_set_filename, temp_parameter_filename,
            temp_initial_conditions_filename,
        ) = get_xpp_input_configuration_from_directory(filename)
        set_filename = set_filename or temp_set_filename
        parameter_filename = parameter_filename or temp_parameter_filename
        initial_conditions_filename = initial_conditions_filename or temp_initial_conditions_filename

    # check model file exists and is valid
    if not isinstance(filename, str):
        errors.append(['`{}` is not a path to an XPP file.'.format(filename)])
        return (errors, warnings, simulation)

    if not os.path.isfile(filename):
        errors.append(['XPP file `{}` does not exist.'.format(filename)])
        return (errors, warnings, simulation)

    sanitized_filename = sanitize_model(filename, exclude_options=['output'])

    var_param_fid, var_param_filename = tempfile.mkstemp()
    os.close(var_param_fid)

    cmd = ['xppaut', os.path.basename(sanitized_filename), '-qics', '-qpars', '-outfile', var_param_filename, '-quiet', '0']
    if set_filename is not None:
        cmd.append('-setfile')
        cmd.append(set_filename)
    if parameter_filename is not None:
        cmd.append('-parfile')
        cmd.append(parameter_filename)
    if initial_conditions_filename is not None:
        cmd.append('-icfile')
        cmd.append(initial_conditions_filename)
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        cwd=os.path.dirname(sanitized_filename),
    )

    stdout = result.stdout.decode(errors='ignore').strip()

    if result.returncode != 0:
        errors.append(['`{}` is not a valid XPP file.'.format(filename), [[stdout]]])

    elif re.search(r'\berror\b', stdout, re.IGNORECASE):
        errors.append(['`{}` is not a valid XPP file.'.format(filename), [[stdout]]])

    if not errors:
        cmd = ['xppaut', os.path.basename(sanitized_filename), '-qics', '-qpars', '-outfile', var_param_filename, '-quiet', '1']
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            cwd=os.path.dirname(sanitized_filename),
        )
        stdout = result.stdout.decode(errors='ignore').strip()
        if stdout:
            warnings.append([
                'The XPP file may be not be formulated correctly',
                [
                    [line] for line in stdout.split('\n')
                ],
            ])

        simulation = {
            'parameters': collections.OrderedDict(),
            'initial_conditions': collections.OrderedDict(),
            'sets': {},
            'auxiliary_variables': collections.OrderedDict(),
            'simulation_method': {},
            'range': {},
            'other_numerics': {},
            'auto': {},
            'plot': {},
            'nullcline_plot': {},
            'poincare_map': {},
            'output': {},
            'ui': {},
            'other': {},
        }
        block = None
        with open(var_param_filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    if line == '#Parameters query:':
                        block = 'parameters'
                    elif line == '#Initial conditions query:':
                        block = 'initial_conditions'
                elif block:
                    id, _, value = line.partition(' ')
                    simulation[block][id] = float(value)

        el_keys = ['xp', 'yp', 'zp']
        for i_el in range(7):
            el_keys.append('xp' + str(i_el + 2))
            el_keys.append('yp' + str(i_el + 2))
            el_keys.append('zp' + str(i_el + 2))

        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('aux '):
                    name, _, expr = line[4:].strip().partition('=')
                    name = name.strip().upper()
                    expr = expr.strip()

                    if name.endswith(']'):
                        name, _, start_end = name[0:-1].partition('[')
                        start, _, end = start_end.partition('..')
                        for i_var in range(int(start), int(end) + 1):
                            simulation['auxiliary_variables'][name + str(i_var)] = expr.replace('[j]', f'[{i_var}]')

                    else:
                        simulation['auxiliary_variables'][name] = expr

                if line.startswith('set '):
                    name, _, values = line[4:].strip().partition(' ')
                    name = name.strip().lower()
                    simulation['sets'][name] = {
                        'parameters': {},
                        'initial_conditions': {},
                    }
                    for val in values[1:-1].split(','):
                        paramVar, _, val = val.partition('=')
                        paramVar = paramVar.strip()
                        val = float(val.strip())

                        if paramVar in simulation['parameters']:
                            paramVar = paramVar.lower()
                            simulation['sets'][name]['parameters'][paramVar] = val
                            # simulation['parameters'][paramVar] = val
                        else:
                            paramVar = paramVar.upper()
                            simulation['sets'][name]['initial_conditions'][paramVar] = val
                            simulation['initial_conditions'][paramVar] = val

                elif line.startswith('@'):
                    line = line[1:]
                    i_comment = line.find('#')
                    if i_comment > -1:
                        line = line[0:i_comment]
                    for cmd in line.split(','):
                        parts = cmd.split('=')
                        if len(parts) > 1:
                            key = parts[0].lstrip()
                            val = parts[1].rstrip()
                            if ' ' not in key and ' ' not in val:
                                key = key.lower()
                                if key == 'transient':
                                    key = 'trans'
                                elif key == 'nout':
                                    key = 'njmp'
                                elif key == 'method':
                                    key = 'meth'
                                elif key.startswith('xplot'):
                                    key = key.replace('xplot', 'xp')
                                elif key.startswith('yplot'):
                                    key = key.replace('yplot', 'yp')
                                elif key.startswith('zplot'):
                                    key = key.replace('zplot', 'zp')
                                elif key == 'atol':
                                    key = 'atoler'
                                elif key in ['rtol', 'tol', 'rtolerance', 'tolerance']:
                                    key = 'toler'
                                elif key == 'xp1':
                                    key = 'xp'
                                elif key == 'yp1':
                                    key = 'yp'
                                elif key == 'zp1':
                                    key = 'zp'
                                elif key == 'xlow':
                                    key = 'xlo'
                                elif key == 'ylow':
                                    key = 'ylo'
                                elif key == 'bounds':
                                    key = 'bound'
                                elif key == 'maxstore':
                                    key = 'maxstor'
                                elif key == 'background':
                                    key = 'back'

                                if key in [
                                    'total', 'dt', 'njmp', 't0', 'trans',
                                    'meth',
                                    'bandup', 'bandlo',
                                    'dtmin', 'dtmax',
                                    'vmaxpts',
                                    'jac_eps', 'newt_tol', 'newt_iter',
                                    'atoler', 'toler',
                                    'seed',
                                ]:
                                    simulation['simulation_method'][key] = val

                                elif key in [
                                    'rangelow', 'rangehigh', 'rangestep',
                                ]:
                                    simulation['range'][key] = float(val)

                                elif key in [
                                    'range', 'rangereset', 'rangeoldic',
                                ]:
                                    simulation['range'][key] = val.lower() in ['yes', 'on', 'true', '1']

                                elif key in [
                                    'rangeover',
                                ]:
                                    simulation['range'][key] = val

                                elif key in [
                                    'ntst', 'nmax', 'npr',
                                    'dsmin', 'dsmax', 'ds',
                                    'parmin', 'parmax',
                                    'normmin', 'normmax',
                                    'autoxmin', 'autoxmax', 'autoymin', 'autoymax', 'autovar',
                                    'epsl', 'epsu', 'epss',  # undocumented tolerances for AUTO
                                    'smc', 'umc',  # manifold colors (0 - 10)
                                ]:
                                    # AUTO options
                                    simulation['auto'][key] = val

                                elif key in [
                                    'maxstor',  # total number of time steps that will be kept in memory
                                    'bound',  # maximum any plotted variable can reach in magnitude
                                    'delay',  # maximum delay allowed in the integration
                                    'tor_per',  # period for a toroidal phasespace
                                    'fold',  # name of variable to be considered modulo the period
                                    'autoeval',  # whether or not to automatically re-evaluate tables everytime a parameter is changed
                                ]:
                                    simulation['other_numerics'][key] = val

                                elif key in el_keys:
                                    axis = key[0]
                                    i_el = int(float(key[2:] or '1'))

                                    if 'elements' not in simulation['plot']:
                                        simulation['plot']['elements'] = {}
                                    if i_el not in simulation['plot']['elements']:
                                        simulation['plot']['elements'][i_el] = {}
                                    simulation['plot']['elements'][i_el][axis] = val.upper()

                                elif key in [
                                    'xlo', 'xhi', 'ylo', 'yhi',  # axes limits for 2D plots
                                    'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax',  # axes limits for 3D plots
                                    'phi', 'theta',  # angles for 3D plots
                                ]:
                                    simulation['plot'][key] = float(val)

                                elif key in [
                                    'axes',  # number of dimensions to plot (2 or 3)
                                    'nplot',  # number of curves to plot
                                    'lt',  # line type (-6 - 2)
                                ]:
                                    simulation['plot'][key] = int(float(val))

                                elif key in [
                                    'xnc', 'ync',  # null cline colors (0 - 10)
                                    'nmesh',  # mesh size for computing nullclines
                                ]:
                                    simulation['nullcline_plot'][key] = val

                                elif key in ['poimap', 'poivar', 'poipln', 'poisgn', 'poistop']:
                                    # Poincare map options
                                    simulation['poincare_map'][key] = val

                                elif key in [
                                    'back',  # background color
                                    'small', 'big',  # font size
                                    'bell',
                                ]:
                                    # UI options
                                    simulation['ui'][key] = val

                                elif key in [
                                    'output',  # file to save results
                                ]:
                                    simulation['output'][key] = val

                                elif key in [
                                    'create',  # undocumented option used by ModelDB:239039
                                ]:
                                    simulation['other'][key] = val

                                else:
                                    simulation['other'][key] = val
                                    # raise NotImplementedError('Option `{}` is not supported'.format(key))

                elif line.startswith('d') and not ('=' in line and (' ' not in line or line.find('=') < line.find(' '))):
                    # check for "done" line; note just the singular character ``d`` defines the "done" line
                    break

        if set_filename is not None:
            with open(set_filename, 'r') as file:
                block = None
                for line in file:
                    if line.startswith('#'):
                        block = line[1:].strip()
                    elif line:
                        if block == 'Old ICs':
                            val, _, var = line.partition(' ')
                            val = float(val.strip())
                            var = var.strip().upper()
                            simulation['initial_conditions'][var] = val

                        elif block == 'Parameters':
                            val, _, var = line.partition(' ')
                            val = float(val.strip())
                            var = var.strip().lower()
                            simulation['parameters'][var] = val

        if parameter_filename is not None:
            with open(parameter_filename, 'r') as file:
                file.readline()
                for line in file:
                    val, _, param = line.partition(' ')
                    simulation['parameters'][param.strip()] = float(val.strip())

        if initial_conditions_filename is not None:
            with open(initial_conditions_filename, 'r') as file:
                for val, var in zip(file, simulation['initial_conditions'].keys()):
                    simulation['initial_conditions'][var] = float(val.strip())

        t_0 = simulation['simulation_method'].get('t0', 0.)
        try:
            t_0 = float(t_0)
        except ValueError:
            errors.append(['T0 must be a float, not `{}`'.format(t_0)])

        duration = simulation['simulation_method'].get('total', 20.)
        try:
            duration = float(duration)
        except ValueError:
            errors.append(['TOTAL must be a float, not `{}`'.format(duration)])

        d_t = simulation['simulation_method'].get('dt', 0.05)
        try:
            d_t = float(d_t)
        except ValueError:
            errors.append(['DT must be a float, not `{}`'.format(d_t)])

        n_jmp = simulation['simulation_method'].get('njmp', 1)
        try:
            n_jmp = float(n_jmp)
            if n_jmp != int(n_jmp) or n_jmp < 1:
                errors.append(['NJMP must be a positive integer, not `{}`'.format(n_jmp)])
        except ValueError:
            errors.append(['NJMP must be a positive integer, not `{}`'.format(n_jmp)])

        if not errors:
            number_of_steps = duration / (d_t * n_jmp)
            if (number_of_steps % 1.) > 1e-8:
                errors.append([
                    'Number of steps must be an integer',
                    [
                        ['t0: {}'.format(t_0)],
                        ['total: {}'.format(duration)],
                        ['dt: {}'.format(d_t)],
                        ['njmp: {}'.format(n_jmp)],
                    ],
                ])

    os.remove(sanitized_filename)
    os.remove(var_param_filename)

    if simulation:
        variable_ids = set(simulation['initial_conditions'].keys()) | set(simulation['auxiliary_variables'].keys()) | set('T')
        missing_plot_variables = set()
        for plot_element in simulation['plot'].get('elements', {}).values():
            if 'x' in plot_element and plot_element['x'] not in variable_ids:
                missing_plot_variables.add(plot_element['x'])
            if 'y' in plot_element and plot_element['y'] not in variable_ids:
                missing_plot_variables.add(plot_element['y'])
            if 'z' in plot_element and plot_element['z'] not in variable_ids:
                missing_plot_variables.add(plot_element['z'])
        if missing_plot_variables:
            errors.append([
                '{} variables required for plots are not defined'.format(len(missing_plot_variables)),
                [[variable] for variable in sorted(missing_plot_variables)],
            ])

        for key, val in simulation.items():
            if not val:
                simulation[key] = None
        simulation['sets'] = simulation['sets'] or {}
        simulation['auxiliary_variables'] = simulation['auxiliary_variables'] or collections.OrderedDict()

    return (errors, warnings, simulation)


def get_xpp_input_configuration_from_directory(dirname):
    """ Get input file configuration from a directory of files

    * ``*.ode``: Main model model
    * ``*.set``: Set file
    * ``*.par``: Parameters file
    * ``*.ic``: Initial conditions file

    Args:
        dirname (:obj:`str`): path to directory of XPP files

    Returns:
        :obj:`tuple`:

            * :obj:`str`: path to main model file
            * :obj:`str`: path to set file
            * :obj:`str`: path to parameters file
            * :obj:`str`: path to initial conditions file
            * :obj:`str`: name of a set to use
            * :obj:`str`: name of a set not to use
    """
    errors = []

    ode_filenames = glob.glob(os.path.join(dirname, "*.ode"))
    if len(ode_filenames) > 1:
        errors.append('Only 1 ODE file can be used at a time.')
    elif ode_filenames:
        ode_filename = ode_filenames[0]
    else:
        errors.append('The directory must contain an ODE file.')

    set_filenames = glob.glob(os.path.join(dirname, "*.set"))
    if len(set_filenames) > 1:
        errors.append('Only 1 set file can be used at a time.')
    elif set_filenames:
        set_filename = set_filenames[0]
    else:
        set_filename = None

    parameter_filenames = glob.glob(os.path.join(dirname, "*.par"))
    if len(parameter_filenames) > 1:
        errors.append('Only 1 parameter file can be used at a time.')
    elif parameter_filenames:
        parameter_filename = parameter_filenames[0]
    else:
        parameter_filename = None

    initial_conditions_filenames = glob.glob(os.path.join(dirname, "*.ic"))
    if len(initial_conditions_filenames) > 1:
        errors.append('Only 1 initial conditions file can be used at a time.')
    elif initial_conditions_filenames:
        initial_conditions_filename = initial_conditions_filenames[0]
    else:
        initial_conditions_filename = None

    if errors:
        raise ValueError('`{}` does not contain a valid set of XPP files:\n  - {}'.format(dirname, '\n  - '.join(errors)))

    return (ode_filename, set_filename, parameter_filename, initial_conditions_filename)


def sanitize_model(filename, keep_only_directives=True, exclude_options=None):
    """ Sanitize an ODE file for interrogation

    * Join continued statements into individual lines
    * Remove statements

    Args:
        filename (:obj:`str`): path to model file or directory with ``.ode`` and possibly set (``.set``),
            parameter (``.par``), andd initial conditions (``.ic``) files
        keep_only_directives (:obj:`bool`, optional): whether to keep `only` directives which limit output variables
        exclude_options (:obj:`list` of :obj:`str`, optional): list of directives to exclude

    Returns:
        :obj:`str`: path to sanitized model file
    """
    exclude_options = exclude_options or []

    statements = []
    with open(filename, 'rb') as file:
        statement = b''
        for line in file:
            if line.endswith(b'\\\n'):
                statement += re.sub(b'\\\\+$', b'', line[0:-1]) + b' '
            else:
                statement += line

                statements.append(statement)
                statement = b''

        if statement:
            raise ValueError('Models cannot end with continued statements (lines that end in `\\`')

    fid, sanitized_filename = tempfile.mkstemp(suffix='.ode', dir=os.path.dirname(filename))
    os.close(fid)

    with open(sanitized_filename, 'wb') as sanitized_file:
        for statement in statements:
            if not keep_only_directives and statement.startswith(b'only'):
                continue

            elif statement.startswith(b'@'):
                statement = statement[1:]
                i_comment = statement.find(b'#')
                if i_comment > -1:
                    statement = statement[0:i_comment]

                args = {}
                for cmd in re.split(b'[, ]+', statement):
                    parts = cmd.split(b'=')
                    if len(parts) > 1:
                        key = parts[0].lstrip().lower()
                        val = parts[1].rstrip()
                        args[key] = val

                for exclude_directive in exclude_options:
                    args.pop(exclude_directive.encode(), None)

                if args:
                    sanitized_statement = b'@ ' + b', '.join(key + b'=' + val for key, val in args.items()) + b'\n'
                else:
                    sanitized_statement = b''
            else:
                sanitized_statement = statement

            sanitized_file.write(sanitized_statement)

    return sanitized_filename
