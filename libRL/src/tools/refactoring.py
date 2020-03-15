"""
:code:`refactoring.py`
======================

refactoring.py provides the data refactoring protocols for the
libRL module.

functions include:

::

    refactoring.file_refactor(data=None):

resultant is the processed Nx5 data array of [frequency, e1, e2, mu1, mu2].
Gives the user options for inputting data, from a file location string to the
data array already formatted.

::

    refactoring.interpolate(data, **kwargs):


resultant is the four scipy-derived interpolating functions for e1, e2, mu1,
and mu2. Default is cubic spline interpolation (piece-wise 3rd order
polynomials) but user has the option to override with linear interpolation.

::

    refactoring.f_set_ref(f_set, data):

resultant is the Nx1 array of frequency values determined from user inputs.
see refactoring.f_set_ref? for complete documentation

::

    refactoring.d_set_ref(f_set):

resultant is the Nx1 array of thickness values determined from user inputs.
see refactoring.d_set_ref? for complete documentation

::

    refactoring.m_set_ref(m_set):

resultant is the Nx1 array of band values determined from user inputs.
see refactoring.m_set_ref? for complete documentation

"""

import cmath, time
from werkzeug.datastructures import FileStorage

from numpy import (
    arange, delete, abs, array,
    argmin, float64, average, sqrt
)

from pandas import (
    read_csv, ExcelWriter,
    read_excel, DataFrame
)

from scipy.interpolate import interp1d

from os.path import splitext, split, join


def file_refactor(dataFile=None, **kwargs):
    """

refactors the given user data into actionable permittivity and permeability
data.

::

    :param dataFile:(file_path)

Permittivity and Permeability data of Nx5 dimensions. Can be a string
equivalent to the directory and file name of either a .csv or .xlsx of Nx5
dimensions. Text above and below data array will be automatically avoided by
the program (most network analysis instruments report data which is compatible
with the required format).

::

    :param kwargs:  override=
                    (None); 'chi zero', 'eps set'

provides response simulation functionality within libRL, common for discerning
which EM parameters are casual for reflection loss. 'chi zero' sets
mu = (1 - j*0). 'eps set' sets epsilon = (avg(e1)-j*0).

::

    :return:        data

refactored data set of Nx5 dimensionality in numpy array
    """

    if dataFile is None:
        error_msg = 'Data must be passed as an array which is mappable ' \
                   'to an Nx5 numpy array with columns ' \
                   '[freq, e1, e2, mu1, mu2]'
        raise RuntimeError(error_msg)
    
    # allows for file location to be passed as the data variable.
    elif isinstance(dataFile, str) is True:

        if splitext(dataFile)[1] == '.csv':
            data = read_csv(dataFile, sep=',').to_numpy()
            
            if data.shape[1] == 1 \
                    and "\t" in data[data.shape[0]//2][0]:
                data = read_csv(dataFile, sep='\t').to_numpy()
                
        elif splitext(dataFile)[1] == '.xlsx':
            data = read_excel(dataFile).to_numpy()

        else:
            error_msg = 'Error partitioning input data from string'
            raise RuntimeError(error_msg)

    # hook for GUI data input
    elif isinstance(dataFile, FileStorage) is True:
        ext = splitext(dataFile.filename)[1]
        if ext == '.xlsx':
            data = read_excel(dataFile.stream).to_numpy()
        elif ext == '.csv':
            data = read_csv(dataFile, sep=',').to_numpy()
            
            if data.shape[1] == 1 \
                    and "\t" in data[data.shape[0]//2][0]:
                data = read_csv(dataFile, sep='\t').to_numpy()            
        else:
            error_msg = 'Error partitioning input data from string'
            raise RuntimeError(error_msg)

    else:
        data = dataFile

    # check each position in numpy array
    # if it can be a number, make it a number
    index = [(row, col) 
        for row in range(data.shape[0]) 
        for col in range(data.shape[1])
    ]

    for coordinate in index:
        try:
            data[coordinate] = float64(data[coordinate])
        except:
            pass

    # finds all rows in numpy array which aren't
    # a part of the Nx5 data array expected.
    #
    # NOTE:
    # if the file contains more/less than
    # 5 columns this fails as the 6th row is
    # always filled with NaN. That being said,
    # most instruments output a Nx5 data file.

    set_to_del = {row for row in arange(data.shape[0]) for col in
                  arange(data.shape[1]) if
                  isinstance(data[row, col], (int, float)) is False
                  or data[row, col] != data[row, col]}

    # removes non-data rows from input array to yield the data array
    data = delete(data, list(set_to_del), axis=0)

    if 'override' in kwargs and kwargs['override'] == 'chi zero':
        data[:, 3:5] = array([1, 0])

    elif 'override' in kwargs and kwargs['override'] == 'eps set':
        avg = average(data[:,1])
        data[:, 1:3] = array([avg, 0])

    return data

def interpolate(data, **kwargs):
    """

uses SciPy's interpolation module to generate interpolating functions over the
input data.

::

    :param data:   (data)

Permittivity data of Nx5 form where N rows are [frequency, e1, e2, mu1, mu2]

::

    :param kwargs:  interp=
                    ('cubic'); 'linear'

Method for interpolation. Set to linear if user wants to linear interp instead
of cubic spline.

::

    :return:        e1f, e2f, mu1f, mu2f

returns four functions for Real Permittivity, Complex Permittivity, Real
Permeability, and Complex Permeability respectively
    """

    params = ['e1f', 'e2f', 'mu1f', 'mu2f']

    if 'interp' in kwargs and kwargs['interp'] == 'linear':

        funcs = {param: interp1d(
            array(data[:, 0], dtype=float64),
            array(data[:, count], dtype=float64),
            kind='linear', fill_value='extrapolate'
        ) for count, param in enumerate(params, start=1)
        }

    else:
        funcs = {param: interp1d(
            array(data[:, 0], dtype=float64),
            array(data[:, count], dtype=float64),
            kind='cubic', fill_value='extrapolate'
        ) for count, param in enumerate(params, start=1)
        }

    return funcs['e1f'], funcs['e2f'], funcs['mu1f'], funcs['mu2f']


def f_set_ref(f_set, data):
    """

refactors the input f_set to the corresponding Nx1 numpy array.

::

    :param f_set:   (start, end, [step])

tuple for frequency values in GHz

- if given as tuple of len 3, results are interpolated
- if given as tuple of len 2, results are data-derived with the calculation
  bound by the given start and end frequencies from the tuple
- is given as int or float of len 1, results are interpolated over the entire
  data set with a step size of the given tuple value.
- if f_set is None (default), frequency is bound to input data.

::

    :param data:   (data)

uses data as reference as frequencies are experimentally determined.

::

    :return:        f_set

refactored f_set of Nx1 numpy array
    """
    if f_set is None:
        f_set = array([
            m for m in data[:, 0]
        ], dtype=float64)

    elif f_set is float or int and isinstance(f_set, tuple) is False:
        f_set = array([
            m for m in arange(data[0, 0], data[-1, 0] + f_set, f_set)
        ], dtype=float64)

    elif len(f_set) == 2:

        if f_set[0] > f_set[1]:
            error_msg = "f_set must be of order (start, stop, [step]) where " \
                        "'start' is a value smaller than 'stop'"
            raise SyntaxError(error_msg)

        if f_set[0] < data[0,0] or f_set[1] > data[-1,0]:
            error_msg = "f_set must be of order (start, stop, [step]) where " \
                        "'start' and 'stop' are within the bounds of the data"
            raise SyntaxError(error_msg)

        f_set = array([
            m for m in data[
                       argmin(abs(f_set[0] - data[:, 0])):
                       argmin(abs(f_set[1] - data[:, 0])) + 1,
                       0]
        ], dtype=float64)

    elif len(f_set) == 3:

        if f_set[0] < data[0,0] or f_set[1] > data[-1,0]:
            error_msg = "f_set must be of order (start, stop, [step]) where " \
                       "'start' and 'stop' are within the bounds of the data"
            raise SyntaxError(error_msg)

        if f_set[0] > f_set[1]:
            error_msg = "f_set must be of order (start, stop, [step]) where " \
                       "'start' is a value smaller than 'stop'"
            raise SyntaxError(error_msg)

        f_set = array([
            m for m in arange(f_set[0], f_set[1] + f_set[2], f_set[2])
        ], dtype=float64)

    else:
        error_msg = 'Error in partitioning frequency values'
        raise SyntaxError(error_msg)

    return f_set


def d_set_ref(d_set):
    """

refactors the input d_set to the corresponding Nx1 numpy array.

::

    :param d_set:   (start, end, [step])

tuple for thickness values in mm.

- if d_set is of type list, then the thickness values calculated will only be
  of the values present in the list.

::

    :return:        d_set

refactored d_set of Nx1 numpy array
    """
    if d_set is None:
        error_msg = 'd_set must be given as a tuple of length 3 ' \
                   '(d_st, d_end, d_step) or a list [] of d values.'
        raise SyntaxError(error_msg)

    elif type(d_set) is list:
        d_set = array(d_set, dtype=float64)

    else:
        try:
            d_set = arange(
                d_set[0], d_set[1] + d_set[2], d_set[2], dtype=float64
            )

        except:
            error_msg = 'd_set must be a tuple type int or float of ' \
                       'structure (start, end, step) ' \
                       'or a list [] of type int or float values.'
            raise SyntaxError(error_msg)

    return d_set


def m_set_ref(m_set):
    """

refactors the input m_set to the corresponding Nx1 numpy array.

::

    :param m_set:   (start, end, [step])

tuple of ints which define the bands to be calculated.

- if m_set is given as a list [], the explicitly listed band integers will
  be calculated.

::

    :return:        refactored m_set of Nx1 numpy array
  """
    # partition band values
    if type(m_set) is list:
        m_set = array(m_set, dtype=int)

    else:

        try:
            m_set = arange(m_set[0], m_set[1] + m_set[2], m_set[2], dtype=int)

        except:
            error_msg = 'm_set must be a tuple of positive integers of ' \
                       'structure (start, end, step) ' \
                       'or a list [] of integer values.'

            raise SyntaxError(error_msg)

    return m_set

def reflection_loss_function(grid):
    e1f=grid[0]
    e2f=grid[1]
    mu1f=grid[2]
    mu2f=grid[3]
    f=grid[4]
    d=grid[5]

    # I know, it's super ugly.
    y = (20 * cmath.log10((abs(((1 * (cmath.sqrt((mu1f(f) - cmath.sqrt(-1) * mu2f(f)) /
        (e1f(f) - cmath.sqrt(-1) * e2f(f)))) * (cmath.tanh(cmath.sqrt(-1) *
        (2 * cmath.pi * (f * 10**9) * (d * 0.001) / 299792458) *
        cmath.sqrt((mu1f(f) - cmath.sqrt(-1) * mu2f(f)) * (e1f(f) - cmath.sqrt(-1) *
        e2f(f)))))) - 1) / ((1 * (cmath.sqrt((mu1f(f) - cmath.sqrt(-1) * mu2f(f)) /
        (e1f(f) - cmath.sqrt(-1) * e2f(f)))) * (cmath.tanh(cmath.sqrt(-1) * (2 *
        cmath.pi * (f * 10**9) * (d * 0.001) / 299792458) * cmath.sqrt(
        (mu1f(f) - cmath.sqrt(-1) * mu2f(f)) * (e1f(f) - cmath.sqrt(-1) *
        e2f(f)))))) + 1)))))

    # return inputted data for documentation and return
    # the real portion of y to drop complex portion
    # of form j*0
    return y.real, f, d


# to find the 1/2th integer wavelength, NOT quarter.
def dfind_half(e1f, e2f, mu1f, mu2f, f, m):
    y = ((299792458 / (f * 10**9)) * (1.0 / (
        sqrt((mu1f(f) - cmath.sqrt(-1) * mu2f(f)) *
        (e1f(f) - cmath.sqrt(-1) * e2f(f))).real)) * (
            ((2.0 * m) - 2.0) / 4.0)) * 1000
    return y


def qref(data):
    """
catches the argument references before initial calculation processing
and saves the information to an isolated variable for later use.

    """

    assert isinstance(data, str) is True, \
        'To use the True assertion for this **kwarg the user must ' \
        'pass a valid data file string as the data argument. The user may ' \
        'also pass a directory location instead.'

    if splitext(split(data)[1])[1] == '':
        error_msg = "error parsing out data file."
        raise SyntaxError(error_msg)

    else:
        output_location = split(data)[0]
        file_name = splitext(split(data)[1])[0]

    return output_location, file_name

def save_to_excel(data, location, file_name, parent, overview):
    """

uses the function arguments and resultants to generate an excel file to be 
saved locally.

    """

    writer = ExcelWriter(join(location, parent + ' ' + file_name) + '.xlsx') # pylint: disable=abstract-class-instantiated
    data.to_excel(writer, sheet_name=parent)

    overview.to_excel(writer, sheet_name='overview')

    writer.save()