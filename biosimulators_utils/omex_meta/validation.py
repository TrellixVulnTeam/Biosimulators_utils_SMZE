""" Methods for validate BioSimulations metadata

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-06-23
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .data_model import BIOSIMULATIONS_PREDICATE_TYPES
import dateutil.parser
import os
import re
import requests
import validators

__all__ = [
    'validate_biosimulations_metadata',
]


def validate_biosimulations_metadata(metadata, working_dir=None):
    """ Validate BioSimulations metadata for a file in a COMBINE/OMEX archive

    Args:
        metadata (:obj:`dict`): BioSimulations metadata
        working_dir (:obj:`str`, optional): working directory (e.g., directory of the parent COMBINE/OMEX archive)

    Returns:
        :obj:`tuple`:

            * nested :obj:`list` of :obj:`str`: nested list of errors with the metadata
            * nested :obj:`list` of :obj:`str`: nested list of warnings with the metadata
    """
    errors = []
    warnings = []

    # required attributes are present
    if metadata['uri'] == '.':
        for predicate_type in BIOSIMULATIONS_PREDICATE_TYPES.values():
            if predicate_type['required'] and (
                (not predicate_type['multiple_allowed'] and metadata[predicate_type['attribute']] is None)
                or (predicate_type['multiple_allowed'] and metadata[predicate_type['attribute']] == [])
            ):
                errors.append(['Attribute `{}` ({}) is required.'.format(
                    predicate_type['attribute'], predicate_type['uri'])])

    # URIs are URLs
    # Identifiers.org URLs point to valid identifiers
    for predicate_type in BIOSIMULATIONS_PREDICATE_TYPES.values():
        if predicate_type['has_uri'] and predicate_type['has_label']:
            if predicate_type['multiple_allowed']:
                objects = metadata[predicate_type['attribute']]
            else:
                objects = [metadata[predicate_type['attribute']]]

            for object in objects:
                if object and object['uri']:
                    if not validators.url(object['uri']):
                        errors.append(['URI `{}` of attribute `{}` ({}) is not a valid URL.'.format(
                            object['uri'], predicate_type['attribute'], predicate_type['uri'])])
                    else:
                        match = re.match(r'^https?://identifiers\.org/(.*?)$', object['uri'])
                        if match:
                            response = requests.get('https://resolver.api.identifiers.org/' + match.group(1))
                            if response.status_code == 400:
                                errors.append(['URI `{}` of attribute `{}` ({}) is not a valid identifier.'.format(
                                    object['uri'], predicate_type['attribute'], predicate_type['uri'])])
                            elif not response.ok:
                                warnings.append(['URI `{}` of attribute `{}` ({}) could not be validated.'.format(
                                    object['uri'], predicate_type['attribute'], predicate_type['uri'])])

    # thumbnail is a file; file type is checked by COMBINE validation
    if working_dir:
        for thumbnail in metadata['thumbnails']:
            thumbnail_filename = os.path.join(working_dir, thumbnail)
            if not os.path.isfile(thumbnail_filename):
                errors.append(['Thumbnail `{}` is not a file.'.format(thumbnail)])
    else:
        if metadata['thumbnails']:
            warnings.append([('The locations of the thumbnails could not be validated '
                              'because a working directory was not provided.')])

    # created is a date
    if metadata['created'] is not None:
        try:
            dateutil.parser.parse(metadata['created'])
        except dateutil.parser.ParserError:
            errors.append(['Created date `{}` is not a valid date.'.format(metadata['created'])])

    # modified are dates
    for date in metadata['modified']:
        try:
            dateutil.parser.parse(date)
        except dateutil.parser.ParserError:
            errors.append(['Modified date `{}` is not a valid date.'.format(date)])

    # return errors and warnings
    return (errors, warnings)
