"""
The RAD record format defines what a flat record should look like. It's
an unifying format that is used through out the application.

This record is passed around the different components of the application
to keep a consistent data format. Also it is a good model for other people
in the team looking for data. It gives our data collection some backbone.

For example a scraper is ran, it returns a list of "RadRecord"s, some
middleware takes these records and calls a function that accepts "RadRecord"s
and creates and saves database records from them. That way the scraper doesn't
know about the database and the database models aren't structured around the
scrapers.

Use the rad_record function to create new records. It allows you to create
objects without specifying all of the fields.

>>> r = rad_record('Some Hospital')
>>> r.city is None # True
>>> r2 = rad_record('Other Hospital', city='Chicago', state='Illinois')
>>> r2.city is None # False

The rad_record function will return an instance of RadRecord.

>>> r3 = rad_record('Vida Sida')
>>> r3.is_valid() # True
>>> r4 = rad_record(None)
>>> r4.is_valid() # False

To be valid, all records must have a name. In addition, if a
date_verified value is provided, it must be successfully
parsed into a date using 'YYYY-MM-DD' format.
"""

from datetime import datetime
from collections import namedtuple


"""
A record contains the following fields.
The procedure type and category name are
optional. They are transformed by middleware
into relationships at the database.

The one field that is completely necessary is
`name`. This might be an institutions name, or
a doctor to name some examples.

Underneath the hood a RadRecord is a Python named
tuple, read it's documentation if you aren't familiar
with it. It is a very nice and slick data structure.

"""
RadRecord = namedtuple('RadRecord', [
    'name',
    'organization',
    'description',
    'address',
    'street',
    'city',
    'state',
    'country',
    'zipcode',
    'email',
    'phone',
    'fax',
    'url',
    'source',
    'category_name',
    'category_names',
    'population_names',
    'population_tags',
    'procedure_type',
    'hours',
    'npi',
    'visible',
    'notes',
    'date_verified'])


def is_valid(record):
    """
    A function to help validate RadRecords.
    A RadRecord's name should not be None, an empty string,
    or consist entirely of whitespace. In addition, if
    date_verified is provided, it must parse into a date
    using the 'YYYY-MM-DD' format.

    Args:
        record: The record to validate.
    
    Returns:
        A boolean indicating whether the provided record is valid.
    """
    # First validate name
    if record.name is None or \
        len(record.name) == 0 or \
        record.name.isspace():
        return False

    # Validate date_verified if provided
    if record.date_verified is not None and \
        len(record.date_verified) > 0 and \
        not record.date_verified.isspace():
        # Try to parse it out using 'YYYY-MM-DD'
        try:
            datetime.strptime(record.date_verified, '%Y-%m-%d')
        except ValueError:
            # Parsing error, return false
            return False

    # Fall-through case
    return True


def parse_delimited_list(liststr):
    """
    Parses the provided string, which is assumed
    to be a semicolon-delimited list of items,
    into the corresponding unique list of strings.

    Args:
        liststr: The delimited string to parse.

    Returns:
        The resulting unique list of strings.
    """
    # Handle null/empty/whitespace values
    if liststr is None or \
        len(liststr) == 0 or \
        liststr.isspace():
        return list()

    # Split on semicolons, filter out blank entries,
    # turn the transformed list into a set (to ensure
    # duplicates don't go in), and then convert it
    # back to a list.
    return list(set((cat.strip() for cat \
        in liststr.split(';')
        if cat is not None and \
            len(cat) > 0 and \
            not cat.isspace())))

# Store some lowercase sets for true/false strings
true_values = set([u'true', u't', u'yes', u'y', u'1'])
false_values = set([u'false', u'f', u'no', u'n', u'0'])

def convert_boolean(boolVal):
    """
    Coerces the provided value to a Boolean value, falling back to
    None if the value could not be converted.

    Args:
        boolVal: The value to convert.

    Returns:
        True, False, or None depending on the result of the conversion.
    """
    # Handle None types
    if boolVal is None:
        return None

    # Handle Boolean types
    if isinstance(boolVal, bool):
        return boolVal

    # Handle strings
    if isinstance(boolVal, str) or isinstance(boolVal, unicode):
        # Handle empty values
        if len(boolVal) == 0 or boolVal.isspace():
            return None

        # Normalize the string to Unicode, trim it, and lowercase it
        boolVal = unicode(boolVal).strip().lower()

        # Now look for it in our sets, falling back to None if
        # we don't find anything
        if boolVal in true_values:
            return True
        elif boolVal in false_values:
            return False
        else:
            return None

    # Handle integer/float types
    if isinstance(boolVal, int) or isinstance(boolVal, float):
        if boolVal == 1:
            return True
        elif boolVal == 0:
            return False
        else:
            return None

    # Fall-through case
    return None


def convert_category_name(record):
    """
    Converts a RadRecord's category_name field to
    a list of category_names (separated by semicolons)
    and returns the updated RadRecord.

    Will bypass processing if category_names is already
    populated with data.

    Args:
        record: The record to convert.

    Returns:
        An updated version of the RadRecord with category_names
        set appropriately. 
    """
    if record is None:
        return record

    # Don't bother if we already have category_names
    if record.category_names is not None and \
        len(record.category_names) > 0:
        return record

    new_category_names = parse_delimited_list(record.category_name)

    # Replace the category_names field in the tuple
    return record._replace(category_names=new_category_names)


def convert_population_names(record):
    """
    Converts a RadRecord's population_names field to
    a list of population_tags (separated by semicolons)
    and returns the updated RadRecord.
    
    Will bypass processing if population_tags is already
    populated with data.

    Args:
        record: The record to convert.

    Returns:
        An updated version of the RadRecord with population_tags
        set appropriately. 
    """
    if record is None:
        return record

    # Don't bother if we already have population_tags
    if record.population_tags is not None and \
        len(record.population_tags) > 0:
        return record

    new_population_tags = parse_delimited_list(record.population_names)

    # Replace the population_tags field in the tuple
    return record._replace(population_tags=new_population_tags)


def normalize_record(record):
    """
    Normalizes all fields on the provided RadRecord.

    Args:
        record: The RadRecord to normalize.

    Returns:
        A normalized verion of the RadRecord.
    """
    if record is None:
        return None

    return record.convert_category_name(). \
        convert_population_names()


# Give every RadRecord a method to help with validation.
RadRecord.is_valid = is_valid

# Also attach the conversion functions.
RadRecord.convert_category_name = convert_category_name
RadRecord.convert_population_names = convert_population_names
RadRecord.normalize_record = normalize_record

def rad_record(name, organization=None, description=None, 
    address=None, street=None, city=None, state=None, zipcode=None, country=None, 
    email=None, phone=None, fax=None, url=None,
    source=None, category_name=None, category_names=None, 
    population_names=None, population_tags=None, procedure_type=None, 
    hours=None, npi=None, visible=True, notes=None, date_verified=None):
    """
    Convenience method to create RadRecords with optional fields.
    Use this instead of the class constructor so you don't have to
    specify all of the fields.
    """
    return RadRecord(name, organization, description,
        address, street, city, state, country, zipcode, 
        email, phone, fax, url,
        source, category_name, category_names, 
        population_names, population_tags, procedure_type,
        hours, npi, visible, notes, date_verified)
