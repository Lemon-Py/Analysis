"""This module includes the functions that handle the NDVI calculations"""
from osgeo import gdal
import sys, os, re, math, utm

def search_value_in_txt_file(string, file):
    """This function searches a file for the value that comes after a string

    Args:
        string (str): The string to search for.
        file (str): The file to be searched.

    Returns:
        float: The value that follows the string
    """
    regexp = re.compile(r' *'+ string +'.*?([E0-9.-]+)')
    with open(file, 'r') as f:
        for line in f.readlines():
            match = regexp.match(line)
            if match:
                return float(match.group(1))

def ndvi(value5, value4):
    """This function calculates the NDVI

    Args:
        value5 (float): Band 5 reflectance.
        value4 (float): Band 4 reflectance.

    Returns:
        float: Resulting NDVI value.
    """
    return (value5-value4)/(value5+value4)

def reflectance_correction(value, REFLECTANCE_MULT_BAND, REFLECTANCE_ADD_BAND):
    """This function corrects the NDVI for reflectance

    Args:
        value (float): NDVI value.
        REFLECTANCE_MULT_BAND (float): REFLECTANCE_MULT_BAND.
        REFLECTANCE_ADD_BAND (float): REFLECTANCE_ADD_BAND.

    Returns:
        float: Reflectance corrected NDVI value.
    """
    return (REFLECTANCE_MULT_BAND * value + REFLECTANCE_ADD_BAND)

def angle_correction(value, SUN_ELEVATION):
    """This function corrects the NDVI for angle

    Args:
        value (float): NDVI value.
        SUN_ELEVATION (float): SUN_ELEVATION.

    Returns:
        float: Reflectance corrected NDVI value.
    """
    return value / math.sin(SUN_ELEVATION)

def get_point_values(file, points, corners):
    """This function fetches the value of a series of points from a GeoTIF
    satellital image.

    Args:
        file (str): GeoTIF file path.
        points (list): List of tuples (points) where the first element is the
        point's proyected latitude and the second is the point's proyected
        longitude.
        corners (list): The first element is the proyected latitude and the
        second element is the proyected longitude of the upper left corner
        of the GeoTIF image.

    Returns:
        list: Values for each point passed as argument.
    """
    ds = gdal.Open(file)
    data = ds.ReadAsArray()

    transform = ds.GetGeoTransform()
    xOrigin = corners[0]
    yOrigin = corners[1]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    valores = []
    pixeles = []
    for point in points:
        x = float(point[0])
        y = float(point[1])

        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / (-pixelHeight))
        # get individual pixel values
        value = data[yOffset][xOffset]
        valores.append(value)
    return valores

def utm_from_latlon(list):
    """This function proyects a list of GPS locations (LAT, LON) using the UTM
    proyection and zone 21

    Args:
        list (list): List of tuples where the first element is the latitude and
        the second element is the longitude for each point.

    Returns:
        list: List of tuples where the first element is the proyected value for
        the latitude and the second element is the proyected value for the
        longitude of each point.
    """
    return [utm.from_latlon(float(t[0]),float(t[1]), force_zone_number=21) for t in list]

def generate_ndvi_csv(csv, GeoTIF_folder, points):
    """This function creates a csv file with the NDVI value and the corrected
    NDVI value for a list of proyected coordinates

    Args:
        csv (str): csv filename.
        points (list): List of tuples (points) where the first element is the
        point's proyected latitude and the second is the point's proyected
        longitude.
        of the GeoTIF image.

    Returns:
        Nothing
    """
    file = open(csv, 'a')

    carpetas = [file for file in os.listdir(GeoTIF_folder) if not file.endswith('.tar.gz')]

    for carpeta in carpetas:
        print("Analyzing " + carpeta + " image")
        b4 = '{0}/{1}/{1}_B4.TIF'.format('datos_finales', carpeta)
        b5 = '{0}/{1}/{1}_B5.TIF'.format('datos_finales', carpeta)
        mtl = '{0}/{1}/{1}_MTL.txt'.format('datos_finales', carpeta)

        corner_x = busca_valor('CORNER_UL_LAT_PRODUCT' , mtl)
        corner_y = busca_valor('CORNER_UL_LON_PRODUCT' , mtl)
        corners = [x for x in utm.from_latlon(corner_x, corner_y)[:2]]

        valor_puntual_b4 = valor_puntual(b4, puntos, corners)
        valor_puntual_b5 = valor_puntual(b5, puntos, corners)

        REFLECTANCE_MULT_BAND_4 = busca_valor("REFLECTANCE_MULT_BAND_4", mtl)
        REFLECTANCE_ADD_BAND_4 = busca_valor("REFLECTANCE_ADD_BAND_4", mtl)
        REFLECTANCE_MULT_BAND_5 = busca_valor("REFLECTANCE_MULT_BAND_5", mtl)
        REFLECTANCE_ADD_BAND_5 = busca_valor("REFLECTANCE_ADD_BAND_5", mtl)
        SUN_ELEVATION = busca_valor("SUN_ELEVATION", mtl)

        valor_puntual_b4_r = [correccion_reflectancia(i,REFLECTANCE_MULT_BAND_4,REFLECTANCE_ADD_BAND_4) for i in valor_puntual_b4]
        valor_puntual_b4_r_a = [correccion_angulo(i, SUN_ELEVATION) for i in valor_puntual_b4_r]

        valor_puntual_b5_r = [correccion_reflectancia(i,REFLECTANCE_MULT_BAND_5,REFLECTANCE_ADD_BAND_5) for i in valor_puntual_b5]
        valor_puntual_b5_r_a = [correccion_angulo(i, SUN_ELEVATION) for i in valor_puntual_b5_r]

        ndvi_c = [ndvi(i[0],i[1]) for i in zip(valor_puntual_b5, valor_puntual_b4)]
        ndvi_corregido = [ndvi(i[0],i[1]) for i in zip(valor_puntual_b5_r_a, valor_puntual_b4_r_a)]

        # Fecha - lat - log - ndvi - ndvi corregido
        line = '{0},{1},{2},{3},{4}\n'
        for punto, nd, nd_c in zip(puntos_gps, ndvi_c, ndvi_corregido):
            file.write(line.format(carpeta, punto[0], punto[1], nd, nd_c))

    file.close()
