.. _gdal_viewshed:

================================================================================
gdal_viewshed
================================================================================

.. only:: html

    .. versionadded:: 3.1.0

    Calculates a viewshed raster from an input raster DEM using method defined in [Wang2000]_ for a user defined point.

.. Index:: gdal_viewshed

Synopsis
--------

.. program-output:: gdal_viewshed --help-doc

Description
-----------

By default the :program:`gdal_viewshed` generates a binary visibility raster from one band
of the input raster elevation model (DEM). The output raster will be of type
Byte. With the -mode flag can also return a minimum visible height raster of type Float64.

.. note::
    The algorithm as implemented currently will only output meaningful results
    if the georeferencing is in a projected coordinate reference system.

.. program:: gdal_viewshed

.. include:: options/help_and_help_general.rst

.. include:: options/co.rst

.. option:: -b <band>

   Select an input band **band** containing the DEM data. Bands are numbered from 1.
   Only a single band can be used. Only the part of the raster within the specified
   maximum distance around the observer point is processed.

.. option:: -a_nodata <value>

   The value to be set for the cells in the output raster that have no data.

   .. note::
        Currently, no special processing of input cells at a nodata
        value is done (which may result in erroneous results).

.. option:: -ox <value>

   The X position of the observer (in SRS units).  If the coordinate is outside of the
   raster, all space between the observer and the raster is assumed not to occlude
   visibility of the raster. (Not supported in cumulative mode.)

.. option:: -oy <value>

   The Y position of the observer (in SRS units).  If the coordinate is outside of the
   raster, all space between the observer and the raster is assumed not to occlude
   visibility of the raster. (Not supported in cumulative mode.)

.. option:: -oz <value>

   The height of the observer above the DEM surface in the height unit of the DEM. Default: 2

.. option:: -tz <value>

   The height of the target above the DEM surface in the height unit of the DEM. Default: 0

.. option:: -md <value>

   Maximum distance from observer to compute visibility.
   It is also used to clamp the extent of the output raster.
   (Not supported in cumulative mode)

.. option:: -cc <value>

   Coefficient to consider the effect of the curvature and refraction.
   When calculating visibility between two points (i.e. Line Of Sight or Viewshed),
   The magnitude of this effect varies with atmospheric conditions and depends on the wavelength.

   Different applications for calculating visibility use different interchangeable notation to describe this phenomena:
   Refraction Coefficient, Curvature Coefficient, and Sphere Diameter Factor.
   gdal_viewshed uses the Curvature Coefficient notation.

   .. math::

     {CurvCoeff}=1-{RefractionCoeff}

   Changes in air density curve the light downward causing an observer to see further and the earth to appear less curved,
   as if the sphere (earth) diameter is larger then it actually is.
   The ratio between that imaginary sphere diameter and the actual sphere diameter is given by the formula:

   .. math::
     {SphereDiameterFactor}=1/{CurvCoeff}=1/(1-{RefractionCoeff})

   For visible light, the standard atmospheric refraction coefficient that is generally used is 1/7.
   Thus the default value (since GDAL 3.4) for CurvCoeff that gdal_viewshed uses is 0.85714 (=~ 1-1/7)
   for Earth CRS. Starting with GDAL 3.6, for non-Earth CRS (those whole semi-major axis differs
   by more than 5% with the one of WGS 84), CurvCoeff default value is 1.0, to account for
   the no refraction use case.

   The height of the DEM is corrected according to the following formula:

   .. math::

      Height_{Corrected}=Height_{DEM}-{CurvCoeff}\frac{{TargetDistance}^2}{SphereDiameter}

   Typical coefficient values are given in the table below (use Curvature Coeff value for the cc option)

   ================  ==================  ===================  =====================
   Use Case          Refraction Coeff    **Curvature Coeff**  Sphere Diameter Factor
   No Refraction     0                   1                    1
   Visible Light     1/7                 6/7 (=~0.85714)      7/6 (=~1.1666)
   Radio Waves       0.25 ~ 0.325        0.75 ~ 0.675         1.33 ~ 1.48
   Flat Earth        1                   0                    inf
   ================  ==================  ===================  =====================

.. option:: -iv <value>

   Pixel value to set for invisible areas. (Not supported in cumulative mode) Default: 0

.. option:: -ov <value>

   Pixel value to set for the cells that fall outside of the range specified by
   the observer location and the maximum distance. (Not supported in cumulative mode) Default: 0

.. option:: -vv <value>

   Pixel value to set for visible areas. (Not supported in cumulative mode) Default: 255

.. option:: -om <output mode>

  Sets what information the output contains.

  Possible values: NORMAL, DEM, GROUND, ACCUM

  NORMAL returns a raster of type Byte containing visible locations.

  DEM and GROUND will return a raster of type Float64 containing the minimum target
  height for target to be visible from the DEM surface or ground level respectively.
  That is to say, if the minimum target height for the target to be visible at a
  point is ``h`` and the value of the input raster at that point is ``E``,
  for ``DEM``, ``E + h`` will be the output value.
  For ``ground``, ``h`` will be output value.
  Flags -tz, -iv and -vv will be ignored.

  Cumulative (ACCUM) mode will create an eight bit raster the same size as the input raster
  where each cell represents the relative observability from a grid of observer points.
  See the -os option.

  Default NORMAL

.. option:: -os <value>

   Cell Spacing between observers (only supported in cumulative mode) Default: 10

.. option:: -j <value>

   Number of jobs to run at once. (only supported in cumulative mode) Default: 3


C API
-----

Functionality of this utility can be done from C with :cpp:func:`GDALViewshedGenerate`.

Examples
--------

.. example::

   Screenshot of 2 combined viewshed analysis, with the yellow pixels showing the area that is
   visible from the both observation locations (the green dots), while the small green area is
   only visible from one location.


   .. figure:: ../../images/gdal_viewshed.png


   Create a viewshed raster with a radius of 500 for a person standing at location (-10147017, 5108065).

   .. code-block:: bash

       gdal_viewshed -md 500 -ox -10147017 -oy 5108065 source.tif destination.tif

Reference
---------

.. [Wang2000] Generating Viewsheds without Using Sightlines. Wang, Jianjun,
   Robinson, Gary J., and White, Kevin. Photogrammetric Engineering and Remote
   Sensing. p81. https://www.asprs.org/wp-content/uploads/pers/2000journal/january/2000_jan_87-90.pdf
