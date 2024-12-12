import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


__artifacts_v2__ = {
    "userPayByPhone": {  
        "name": "PayByPhone - Users and Vehicules Info",
        "description": "Permet de recueillir les données de l'application PayByPhone",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.1",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*'),  
        "output_types": "all",
        "artifact_icon": "users"

    },
    "sessionPayByPhone": { 
        "name": "PayByPhone - Parking Sessions",  
        "description": "Liste de sessions des parking",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.2",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*', '*/var/mobile/Containers/Data/Application/*/Documents/*.png'),
        "output_types": "all",
        "artifact_icon": "map"
    }

}


from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def convert_to_zurich_time(timestamp):
    # Convertir un timestamp Cocoa Core Data en heure locale Zurich
    cocoa_base = datetime(2001, 1, 1, tzinfo=ZoneInfo("UTC"))
    utc_time = cocoa_base + timedelta(seconds=timestamp)
    zurich_time = utc_time.astimezone(ZoneInfo("Europe/Zurich"))
    # Format final avec indication du fuseau horaire
    utc_offset = zurich_time.strftime('%z')  # UTC+0100 or UTC+0200
    utc_offset_formatted = f"UTC+{int(utc_offset[:3])}"
    return zurich_time.strftime(f"%d-%m-%Y %H:%M:%S ({utc_offset_formatted})")


def format_price(value):
    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return value  # Retourne la valeur brute si la conversion échoue
    

def lisible_text(html):
    """
    Nettoie une chaîne HTML en supprimant les balises et en remplaçant les entités HTML courantes.

    :param html: Chaîne HTML à nettoyer (peut être None).
    :return: Chaîne nettoyée et lisible.
    """
    # Vérifie si html est None ou vide
    if not html:
        return ""  # Retourne une chaîne vide si aucune donnée

    try:
        # Supprimer toutes les balises HTML avec une expression régulière
        texte_sans_balises = re.sub(r'<[^>]+>', '', html)
        
        # Remplacer les entités HTML courantes
        texte_sans_balises = texte_sans_balises.replace('&quot;', '"')
        texte_sans_balises = texte_sans_balises.replace('&nbsp;', ' ')
        texte_sans_balises = texte_sans_balises.replace('&amp;', '&')
        
        # Nettoyer les espaces inutiles et structurer
        lignes = [ligne.strip() for ligne in texte_sans_balises.split('\n') if ligne.strip()]
        texte_lisible = "\n".join(lignes)
        
        return texte_lisible
    except Exception as e:
        # Capture toute exception et retourne une chaîne vide
        print(f"Erreur lors du traitement du texte HTML : {e}")
        return ""


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, media_to_html


@artifact_processor
def userPayByPhone(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('PayByPhone.sqlite'):
            db_file = file_found
            break


    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
                ZUSERACCOUNT.ZEMAIL AS "EMAIL",
                ZUSERACCOUNT.ZMEMBERID AS "ID Membre",
                ZUSERACCOUNT.ZUSERNAME AS "Telephone",
                ZVEHICLE.ZCOUNTRY AS "Pays",
                ZVEHICLE.ZLICENSEPLATE AS "Numero plaque",
                ZVEHICLE.ZVEHICLEDESCRIPTION AS "Description véhicule",
                ZVEHICLE.ZVEHICLETYPESTRING AS "Catégorie",
                ZVEHICLE.ZVEHICLEID
            FROM 
                ZUSERACCOUNT
            LEFT JOIN 
                ZVEHICLE 
            ON 
                ZUSERACCOUNT.Z_PK = ZVEHICLE.ZUSERACCOUNT;
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            media_file = f'{row[-1]}.png'
            media_tag = media_to_html(media_file, files_found, report_folder)
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], media_tag)
                )

    data_headers = ('Email',
                    'ID Membre',
                    'Téléphone',
                    'Pays',
                    'Numéro d\'immatriculation',
                    'Description du véhicule',
                    'Catégorie',
                    'Photo du véhicule'
                    )

    return data_headers, data_list, db_file


@artifact_processor
def sessionPayByPhone(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('PayByPhone.sqlite'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
                ps.ZSTARTTIME AS "Heure_arrivee",
                ps.ZEXPIRETIME AS "Heure_depart",
                u.ZEMAIL,
                v.ZVEHICLEDESCRIPTION as Voiture,
                ps.ZAMOUNT as Prix,
                l.ZCURRENCY as Devise,
                ps.ZCOORDINATELATITUDE as Latitude,
                ps.ZCOORDINATELONGITUDE as Longitude,
                ps.ZLOCATIONNUMBER AS "tarif/zone",             
                l.ZNAME as Nom_parking,
                l.ZVENDORNAME as Ville,
                l.ZCOUNTRY as Pays,
                l.ZLOTMESSAGE as Info
            FROM ZVEHICLE AS v
            JOIN ZPARKINGSESSION AS ps
                ON v.Z_PK = ps.ZVEHICLE
            JOIN ZLOCATION AS l
                ON ps.ZLOCATIONNUMBER = l.ZLOCATIONNUMBER
            JOIN ZUSERACCOUNT as u
                ON ps.ZUSERACCOUNT = u.ZPARKINGACCOUNT;
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            timestamp_1 = convert_to_zurich_time(row[0])
            timestamp_2 = convert_to_zurich_time(row[1])
            price_adapted = format_price(row[4])
            info_lisible = lisible_text(row[12])
            data_list.append(
                (timestamp_1, timestamp_2, row[2],row[3], price_adapted,row[5], row[6], row[7], 
                    row[8], row[9], row[10], row[11], info_lisible,)
                )

    data_headers = (
            'Heure arrivée',
            'Heure départ',
            'Email',
            'Véhicule',
            'Prix',
            'Devise',
            'Latitude',
            'Longitude',
            'Tarif/zone',
            'Nom du parking',
            'Ville',
            'Pays',
            'Info')


    return data_headers, data_list, db_file
