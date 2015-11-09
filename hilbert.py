"""
This is a module to convert between one dimensional distance along a
`Hilbert curve`_ (:math:`d`)and N-dimensional coordinates.  The two important
parameters are :math:`N` (the number of dimensions, must be > 0) and :math:`p`
(the number of iterations used in constructing the Hilbert curve, must be > 0).

We consider an :math:`N`-dimensional `hypercube`_ of side length :math:`2^p`.
This hypercube contains :math:`2^{N p}` unit hypercubes (:math:`2^p` along
each dimension).  The number of unit hypercubes determine the possible
discrete distances along the Hilbert curve (indexed from :math:`0` to
:math:`2^{N p} - 1`).  The image below illustrates the situation for
:math:`N=2` and :math:`p=3`.

.. figure:: nD=2_p=3.png

   This is the third iteration (:math:`p=3`) of the Hilbert curve in two
   (:math:`N=2`) dimensions.  Distances, :math:`d`, along the curve are
   labeled from 0 to 63 (i.e. from 0 to :math:`2^{N p}`).  The provided
   functions translate between :math:`N`-dimensional coordinates and the one
   dimensional distance.  For example, between (:math:`x_0=4, x_1=6`) and
   :math:`d=36`.


Reference
=========

This module is based on the C code provided in the 2004 article
"Programming the Hilbert Curve" by John Skilling,

  - http://adsabs.harvard.edu/abs/2004AIPC..707..381S

I was also helped by the discussion in the following stackoverflow post,

  - `mapping-n-dimensional-value-to-a-point-on-hilbert-curve`_

which points out a typo in the source code of the paper.  The Skilling code
provides two functions ``TransposetoAxes`` and ``AxestoTranspose``.  In this
case, Transpose refers to a specific packing of the integer that represents
distance along the Hilbert curve (see below for details) and
Axes refer to the N-dimensional coordinates.  Below is an excerpt of the docs
from that code that appears in the paper by Skilling, ::

//+++++++++++++++++++++++++++ PUBLIC-DOMAIN SOFTWARE ++++++++++++++++++++++++++
// Functions: TransposetoAxes  AxestoTranspose
// Purpose:   Transform in-place between Hilbert transpose and geometrical axes
// Example:   b=5 bits for each of n=3 coordinates.
//            15-bit Hilbert integer = A B C D E F G H I J K L M N O is stored
//            as its Transpose
//                   X[0] = A D G J M                X[2]|
//                   X[1] = B E H K N    <------->       | /X[1]
//                   X[2] = C F I L O               axes |/
//                          high  low                    0------ X[0]
//            Axes are stored conveniently as b-bit integers.
// Author:    John Skilling  20 Apr 2001 to 11 Oct 2003



.. _Hilbert curve: https://en.wikipedia.org/wiki/Hilbert_curve
.. _hypercube: https://en.wikipedia.org/wiki/Hypercube

.. _mapping-n-dimensional-value-to-a-point-on-hilbert-curve: http://stackoverflow.com/questions/499166/mapping-n-dimensional-value-to-a-point-on-hilbert-curve/10384110#10384110
"""


def _bit_at(integer, offset):
    """Returns a string representation of the bit `offset` places from the
    least significant bit in `integer`.

    :param integer: integer to inspect the bits of
    :type integer: ``int``
    :param offset: offset from the least significant bit
    :type offset: ``int``
    """
    mask = 1 << offset
    bitwise_and = integer & (1<<offset)
    if bitwise_and > 0:
        return '1'
    else:
        return '0'

def _pack_iH_into_x(iH, pH, nD):
    """Construct the variable `X` from `iH` (see module level docs.)

    :param iH: integer distance along curve to pack into `nD` pieces.
    :type iH: ``int``
    :param pH: number of iterations in Hilbert curve
    :type pH: ``int``
    :param nD: number of dimensions
    :type nD: ``int``
    """
    # create bit string from iH (most to least significant from left to right)
    iH_bit_str = ''
    for i in range(pH * nD):
        iH_bit_str += _bit_at(iH, i)
    iH_bit_str = iH_bit_str[::-1]

    # create bit strings for vector
    x = [''] * nD
    k = 0
    for ipH in range(pH):
        for inD in range(nD):
            x[inD] += iH_bit_str[k]
            k += 1

    # turn bit strings into integers
    for inD in range(nD):
        x[inD] = int('0b' + x[inD], 2)

    return x

def _extract_iH_from_x(x, pH, nD):
    """Construct the variable `iH` from `X` (see module level docs.)

    :param x: coordinates len(x) = nD
    :type x: ``list`` of ``int``
    :param pH: number of iterations in Hilbert curve
    :type pH: ``int``
    :param nD: number of dimensions
    :type nD: ``int``
    """
    # get a list of strings representing each component of x
    x_bit_str = [''] * nD
    for inD in range(nD):
        for ipH in range(pH):
            x_bit_str[inD] += _bit_at(x[inD], ipH)
        x_bit_str[inD] = x_bit_str[inD][::-1]

    # create iH bit string
    iH_str = ''
    for ipH in range(pH):
        for inD in range(nD):
            iH_str += x_bit_str[inD][ipH]

    # turn bit string into integer
    ih = int('0b' + iH_str, 2)

    return ih

def transpose2axes(iH, pH, nD):
    """
    :param ih: integer distance along the curve
    :type ih: ``int``
    :param pH: side length of hypercube is 2^pH
    :type pH: ``int``
    :param nD: number of dimensions
    :type nD: ``int``
    """
    x = _pack_iH_into_x(iH, pH, nD)
    N = 2 << (pH-1)

    # Gray decode by H ^ (H/2)
    t = x[nD-1] >> 1
    for i in range(nD-1, 0, -1):
        x[i] ^= x[i-1]
    x[0] ^= t

    # Undo excess work
    Q = 2
    while Q != N:
        P = Q - 1
        for i in range(nD-1, -1, -1):
            if x[i] & Q:
                # invert
                x[0] ^= P
            else:
                # excchange
                t = (x[0] ^ x[i]) & P
                x[0] ^= t
                x[i] ^= t
        Q <<= 1

    # done
    return x

def axes2transpose(x, pH, nD):
    """
    :param x: coordinates len(x) = nD
    :type x: ``list`` of ``int``
    :param pH: side length of hypercube is 2^p
    :type pH: ``int``
    :param nD: number of dimensions
    :type nD: ``int``
    """
    M = 1 << (pH - 1)

    # Inverse undo excess work
    Q = M
    while Q > 1:
        P = Q - 1
        for i in range(nD):
            if x[i] & Q:
                x[0] ^= P
            else:
                t = (x[0] ^ x[i]) & P
                x[0] ^= t
                x[i] ^= t
        Q >>= 1

    # Gray encode
    for i in range(1,nD):
        x[i] ^= x[i-1]
    t = 0
    Q = M
    while Q > 1:
        if x[nD-1] & Q:
            t ^= Q - 1
        Q >>= 1
    for i in range(nD):
        x[i] ^= t

    ih = _extract_iH_from_x(x, pH, nD)
    return ih