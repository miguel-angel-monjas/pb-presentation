#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, inspect
from io import StringIO, BytesIO
from hashlib import sha1
from datetime import datetime
import pandas as pd
import textwrap
from math import sin, cos, pi
import random

try :
    import pywikibot as pb
    from pywikibot.specialbots import UploadRobot
except :
    current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    folder_parts = current_folder.split(os.sep)
    pywikibot_folder = os.sep.join(folder_parts[:-2])

    if current_folder not in sys.path:
        sys.path.insert(0, current_folder)
    if pywikibot_folder not in sys.path:
        sys.path.insert(0, pywikibot_folder)

    import pywikibot as pb
    from pywikibot.specialbots import UploadRobot

commons_site = pb.Site("commons", "commons")
distance = 0.008

additional_festivals_df = pd.DataFrame(
    data=[
        {'name': 'Fallas de Denia',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q47120057',
         'category': 'Falles de Dénia',
         'latitude': 38.840278,
         'longitude': 0.108611
        },
        {'name': 'Semana Santa de Aranjuez',
         'aut_com': 'Community of Madrid',
         'wikidata_id': 'Q47119796',
         'category': 'Holy Week in Aranjuez',
         'latitude': 40.033333,
        'longitude': -3.602778
        },
        {'name': 'Fiesta de la Virgen de Agosto y San Roque',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q47119479',
         'category': 'Fiesta de la Virgen de Agosto y San Roque, Requena',
         'latitude': 39.488538,
         'longitude': -1.102308
        },
        {'name': 'Gran Feria de Valencia',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q12175110',
         'category': 'Gran Fira de València',
         'latitude': 39.466667,
         'longitude': -0.375
        },
        {'name': 'Fiesta en honor de la Virgen de los Desamparados (Jérica)',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q47128911',
         'category': 'Fiesta en honor de la Virgen de los Desamparados, Jérica',
         'latitude': 39.911738,
         'longitude': -0.571874
        },
        {'name': 'Fallas de Alcácer',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q47129466',
         'category': "Falles d'Alcàsser",
         'latitude': 39.367712,
         'longitude': -0.444674 
        },
        {'name': 'Semana Santa de Candelario',
         'aut_com': 'Castile and León',
         'wikidata_id': 'Q47128318',
         'category': 'Holy Week in Candelario',
         'latitude': 40.368056,
         'longitude': -5.744444
        },
        {'name': 'Festividad de San Vicente Ferrer',
         'aut_com': 'Valencian Community',
         'wikidata_id': 'Q5861379',
         'category': 'Festivals of Saint Vincent Ferrer in the city of Valencia',
         'latitude': 39.466667,
         'longitude': -0.375
        }
    ]
)

def epoch_time(timestamp):
    tdelta = timestamp - datetime.utcfromtimestamp(0)
    return int(tdelta.total_seconds()*1000)

def is_commons_file (sha):
    pages = pb.site.APISite.allimages(commons_site, sha1=sha)
    result = False
    for page in pages :
        print (page)
        result = True
        break
    return result
    
def get_hash (file_path):
    image_file = open(file_path, "rb")
    byte_stream = BytesIO(image_file.read()).getvalue()
    image_file.close()
    hashObject = sha1()
    hashObject.update(byte_stream)
    return hashObject.hexdigest()
    
def upload_to_commons (plot, file_name, file_desc, desc_template, year, tag):
    current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    folder_parts = current_folder.split(os.sep)
    parent_folder = os.sep.join(folder_parts[0:-1])
    
    image_path = os.path.join(parent_folder,
                              'images',
                              file_name)
    try:
        plot.get_figure().savefig(image_path,
                                  transparent=False,
                                  bbox_inches='tight', 
                                  pad_inches=0, 
                                  dpi = (200)
                                 )
    except AttributeError:
        plot.savefig(image_path,
                        transparent=False, 
                        bbox_inches='tight', 
                        pad_inches=0, 
                        dpi = (200)
                        )

    # image already in Commons
    if not is_commons_file(get_hash(image_path)) :
        bot = UploadRobot([image_path],
                          description= desc_template.format(tag, year,
                                                            file_desc, 
                                                            datetime.now().strftime("%Y-%m-%d")),
                          useFilename=file_name,
                          keepFilename=True,
                          verifyDescription=False,
                          ignoreWarning=True,
                          targetSite=commons_site)
        bot.run()

    os.remove(image_path)
        
def dms2dd (degrees, minutes, seconds, direction):
    if degrees == '' : degrees = 0
    if minutes == '' : minutes = 0
    if seconds == '' : seconds = 0
    try:
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    except :
        print (degrees)
        print (minutes)
        print (seconds)
        print (direction)
    if direction == 'S' or direction == 'W' or direction == 'O':
        dd *= -1
    return dd

def coordinate_shaker (row) :
    random.seed(len(row['category']))
    coordinates = (row['latitude'], row['longitude'])
    if row['dup'] == True:
        # longitudes (eje x) y latitudes (eje y)
        theta = random.randint(0,360)
        theta_rad = pi/180.0 * theta
        return (row['latitude'] + distance*sin(theta_rad), row['longitude'] + distance*cos(theta_rad))
    else :
        return coordinates
    
def get_registration_time (user_id):
    """Function that retrieves the registration time of a given user"""
    try:
        # Too old users do not have a user registration time
        user_registration = pb.User(commons_site, title=user_id).registration()
        registration_time = user_registration.strftime("%Y-%m-%d")
    except :
        registration_time = ""
    return registration_time

def heat_color (grade) :
    """Function to assign colors to coverage tables"""
    if grade < 10.0 :
        percentage_color = 'ff6666'
    elif grade < 30.0 :
        percentage_color = 'ffb366'
    elif grade < 50.0 :
        percentage_color = 'ffff66'
    elif grade < 70.0 :
        percentage_color = 'd9ff66'
    elif grade < 90.0 :
        percentage_color = '66ff66'
    else :
        percentage_color = '668cff '
    return percentage_color

def get_project_name (hostname) :
    """Function to retrieve WMF roject name"""
    cwd = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    language_csv_path = os.path.join(cwd, 'languages.csv')
    language_df = pd.read_csv(language_csv_path, sep=';', names=['language', 'abbreviation'])

    tokens = hostname.split('.')
    if tokens[1] == 'wikidata' :
        return 'Wikidata'
    elif tokens[0] == 'meta' :
        return 'Meta'
    elif tokens[0] == 'outreach' :
        return 'Outreach'
    else :
        return '{0} {1}'.format((language_df[language_df['abbreviation'] == tokens[0]]['language']).iloc[0], 
                                tokens[1].capitalize())
    
def wrap_label (label, length=30) :
    """Function to wrap xtick labels in plots"""
    return '\n'.join(textwrap.wrap (label, length))