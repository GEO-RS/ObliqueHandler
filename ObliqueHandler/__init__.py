# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ObliqueHandler
                                 A QGIS plugin
 Oblique Handler lets you work with Oblique images
                             -------------------
        begin                : 2018-01-28
        copyright            : (C) 2018 by Danish National Mapping Authority (sdfe.dk)
        email                : anfla@sdfe.dk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ObliqueHandler class from file ObliqueHandler.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .oblique_handler import ObliqueHandler
    return ObliqueHandler(iface)
