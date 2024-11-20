__artifacts_v2__ = {
    "userPayByPhone": {  # Same name as the main function
        "name": "PayByPhone - Users and Vehicules Info",  # Title used in html report sidebar
        "description": "Permet de recueillir les données de l'application PayByPhone",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.1",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  # Category used in html report sidebar and also in selection menu...
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*'),  # list of paths containing useful information
        "output_types": "all",
        "artifact_icon": "users"

    },
    "sessionPayByPhone": {  # Same name as the main function
        "name": "PayByPhone - Parking Sessions",  # Title used in html report sidebar
        "description": "Liste de sessions des parking",
        "author": "@flashesc, @thibgav, @borelmo",
        "version": "1.1",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Parking",  # Category used in html report sidebar and also in selection menu...
        "notes": "",
        "paths": ('*/var/mobile/Containers/Data/Application/*/Documents/PayByPhone.sqlite*', '*/var/mobile/Containers/Data/Application/*/Documents/*.png'),
        # list of paths containing useful information
        "output_types": "all",
        "artifact_icon": "map"
    }

}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset, \
    media_to_html


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
            media_file = f'{row[7]}.png'
            media_tag = media_to_html(media_file, files_found, report_folder)
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], media_tag)
                )

    data_headers = ('Email',
                    'ID Membre',
                    'Téléphone',
                    'Pays',
                    'Numéro plaque',
                    'Description véhicule',
                    'Catégorie',
                    'Photo véhicule'
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
        SELECT v.ZVEHICLEDESCRIPTION as Voiture,
                   ps.ZAMOUNT as Prix,
                   l.ZCURRENCY as Devise,
                   ps.ZCOORDINATELATITUDE as Latitude,
                   ps.ZCOORDINATELONGITUDE as Longitude,
                   datetime(ps.ZSTARTTIME + 978307200,'unixepoch') AS "Heure_arrivee",
                   datetime(ps.ZEXPIRETIME + 978307200,'unixepoch') AS "Heure_depart",
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
            timestamp_1 = convert_ts_human_to_timezone_offset(row[5], timezone_offset)
            timestamp_2 = convert_ts_human_to_timezone_offset(row[6], timezone_offset)
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], timestamp_1, timestamp_2,
                    row[7], row[8], row[9], row[10], row[11],)
                )

    data_headers = (
            'Voiture',
            'Prix',
            'Devise',
            'Latitude',
            'Longitude',
            'Heure arrivée',
            'Heure départ',
            'Tarif/zone',
            'Nom_parking',
            'Ville',
            'Pays',
            'Info')


    return data_headers, data_list, db_file
