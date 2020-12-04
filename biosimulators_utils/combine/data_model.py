from ..utils import are_lists_equal
import abc
import datetime

__all__ = [
    'CombineArchiveBase',
    'CombineArchive',
    'CombineArchiveContent',
    'CombineArchiveAuthor',
]


class CombineArchiveBase(abc.ABC):
    """ A COMBINE/OMEX archive

    Attributes:
        description (:obj:`str`): description
        authors (:obj:`list` of :obj:`Author`): authors
        created (:obj:`datetime.datetime`): created date
        updated (:obj:`datetime.datetime`): updated date
    """
    pass


class CombineArchive(CombineArchiveBase):
    """ A COMBINE/OMEX archive

    Attributes:
        contents (:obj:`list` of :obj:`CombineArchiveContent`): contents of the archive
        description (:obj:`str`): description
        authors (:obj:`list` of :obj:`Author`): authors
        created (:obj:`datetime.datetime`): created date
        updated (:obj:`datetime.datetime`): updated date
    """

    def __init__(self, contents=None, description=None, authors=None, created=None, updated=None):
        """
        Args:
            contents (:obj:`list` of :obj:`CombineArchiveContent`, optional): contents of the archive
            description (:obj:`str`, optional): description
            authors (:obj:`list` of :obj:`Author`, optional): authors
            created (:obj:`datetime.datetime`, optional): created date
            updated (:obj:`datetime.datetime`, optional): updated date
        """
        self.contents = contents or []
        self.description = description
        self.authors = authors or []
        self.created = created
        self.updated = updated

    def get_master_content(self):
        """ Get the master content of an archive

        Returns:
            :obj:`CombineArchiveContent` or :obj:`None`: master content

        Raises:
            :obj:`ValueError`: if more than one content item is marked as master
        """
        master_content = []
        for content in self.contents:
            if content.master:
                master_content.append(content)
        if not master_content:
            return None
        if len(master_content) == 1:
            return master_content[0]
        raise ValueError('Multiple content items are marked as master')

    def to_tuple(self):
        """ Tuple representation of a COMBINE/OMEX archive

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of a COMBINE/OMEX archive
        """
        contents = tuple(sorted(content.to_tuple() for content in self.contents))
        authors = tuple(sorted(author.to_tuple() for author in self.authors))
        return (contents, self.description, authors, self.created, self.updated)

    def is_equal(self, other):
        """ Determine if two content items are equal

        Args:
            other (:obj:`CombineArchiveContent`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two archives are equal
        """
        return self.__class__ == other.__class__ \
            and are_lists_equal(self.contents, other.contents) \
            and self.description == other.description \
            and are_lists_equal(self.authors, other.authors) \
            and self.created == other.created \
            and self.updated == other.updated


class CombineArchiveContent(CombineArchiveBase):
    """ A content item (e.g., file) in a COMBINE/OMEX archive

    Attributes:
        location (:obj:`str`): path to the content
        format (:obj:`str`): URL for the specification of the format of the content
        master (:obj:`bool`): :obj:`True`, if the content is the "primary" content of the parent archive
        description (:obj:`str`): description
        authors (:obj:`list` of :obj:`Author`): authors
        created (:obj:`datetime.datetime`): created date
        updated (:obj:`datetime.datetime`): updated date
    """

    def __init__(self, location, format, master=False, description=None, authors=None, created=None, updated=None):
        """
        Args:
            location (:obj:`str`): path to the content
            format (:obj:`str`): URL for the specification of the format of the content
            master (:obj:`bool`): :obj:`True`, if the content is the "primary" content of the parent archive
            description (:obj:`str`, optional): description
            authors (:obj:`list` of :obj:`Author`, optional): authors
            created (:obj:`datetime.datetime`, optional): created date
            updated (:obj:`datetime.datetime`, optional): updated date
        """
        self.location = location
        self.format = format
        self.master = master
        self.description = description
        self.authors = authors or []
        self.created = created
        self.updated = updated

    def to_tuple(self):
        """ Tuple representation of a content item of a COMBINE/OMEX archive

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of a content item of a COMBINE/OMEX archive
        """
        authors = tuple(sorted(author.to_tuple() for author in self.authors))
        return (self.location, self.format, self.master, self.description, authors, self.created, self.updated)

    def is_equal(self, other):
        """ Determine if two content items are equal

        Args:
            other (:obj:`CombineArchiveContent`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two content items are equal
        """
        return self.__class__ == other.__class__ \
            and self.location == other.location \
            and self.format == other.format \
            and self.master == other.master \
            and self.description == other.description \
            and are_lists_equal(self.authors, other.authors) \
            and self.created == other.created \
            and self.updated == other.updated


class CombineArchiveAuthor(object):
    """ An author of a COMBINE/OMEX archive of a content item of a COMBINE/OMEX archive

    Attributes:
        given_name (:obj:`str`): given/first name
        family_name (:obj:`str`): family/last name
    """

    def __init__(self, given_name=None, family_name=None):
        """
        Args:
            given_name (:obj:`str`, optional): given/first name
            family_name (:obj:`str`, optional): family/last name
        """
        self.given_name = given_name
        self.family_name = family_name

    def is_equal(self, other):
        """ Determine if two authors are equal

        Args:
            other (:obj:`CombineArchiveAuthor`): another author

        Returns:
            :obj:`bool`: :obj:`True`, if two authors are equal
        """
        return self.__class__ == other.__class__ \
            and self.given_name == other.given_name \
            and self.family_name == other.family_name

    def to_tuple(self):
        """ Tuple representation of an author

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of an author
        """
        return (self.family_name, self.given_name)
