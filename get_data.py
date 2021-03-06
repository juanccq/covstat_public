from os import path, listdir, mkdir
import requests
import pymysql.cursors
import datetime
import json
import configparser
import pathlib

lpath = str( pathlib.Path().absolute() )

config = configparser.ConfigParser()
config.read( lpath + '/db_settings.ini' )

departments = { 
    'lp': 'La Paz', 
    'cb': 'Cochabamba', 
    'sc': 'Santa Cruz', 
    'or': 'Oruro', 
    'pt': 'Potosí', 
    'tj': 'Tarija', 
    'ch': 'Chuquisaca', 
    'bn': 'Beni', 
    'pn': 'Pando' 
}


def get_today_data():
    url = 'https://boliviasegura.agetic.gob.bo/wp-content/json/api.php'
    res = requests.get(url)

    return save_api_data(res.json())

def save_api_data(res):
    fecha = res['fecha']
    fechaObj = datetime.datetime.strptime( res['fecha'], '%d/%m/%y %H:%M' )
    host = config[ 'mysqlDB' ][ 'host' ].replace("'","")
    user = config[ 'mysqlDB' ][ 'user' ].replace("'","")
    passw = config[ 'mysqlDB' ][ 'pass' ].replace("'","")
    db = config[ 'mysqlDB' ][ 'db' ].replace("'","")
    
    # connect to db
    conn = pymysql.connect( host=host,
                            user=user,
                            password=passw,
                            db=db,
                            charset="utf8",
                            cursorclass=pymysql.cursors.DictCursor 
                            )
    
    try:
        with conn.cursor() as cursor:
            for item in departments.keys():
                contdata = res['departamento'][item]['contador']

                # Create a new record
                sql = "INSERT INTO cov_data (date, departament, confirmed, deaths, recovered, suspects, discarded, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, ( fechaObj.strftime( '%Y-%m-%d' ), item, contdata['confirmados'], contdata['decesos'], contdata['recuperados'], contdata['sospechosos'], contdata['descartados'], res['departamento'][item]['total'] ) )
            
        conn.commit()
    
        # prepare data for graph
        with conn.cursor() as cursor:
            sql = "SELECT * FROM ( SELECT `date` FROM cov_data_per_day GROUP BY `date` ORDER BY `date` DESC LIMIT 20 ) res ORDER BY `date` ASC"
            cursor.execute(sql)
            fechas = cursor.fetchall()
            fechaJson = []
            firstDate = None
            lastDate = None

            for item in fechas:
                fechaJson.append( item['date'].strftime('%d/%m/%y') )

                if not firstDate:
                    firstDate = item['date'].strftime('%Y-%m-%d')

                lastDate = item['date'].strftime('%y-%m-%d')

            with open( lpath + '/static/fechas.json', 'w' ) as jsonfile:
                json.dump( fechaJson, jsonfile )

            sql = f"SELECT * FROM cov_data_per_day WHERE `date` >= '{firstDate}' AND `date` <= '{lastDate}'  ORDER BY `date` ASC"
            cursor.execute( sql )
            data = cursor.fetchall()
            data_json_confirmed = {}
            data_json_death = {}
            data_json_recovered = {}
            data_json_suspects = {}
            data_json_discarted = {}

            for dep in departments.keys():
                data_json_confirmed[ dep ] = []
                data_json_death[ dep ] = []
                data_json_recovered[ dep ] = []
                data_json_suspects[ dep ] = []
                data_json_discarted[ dep ] = []
            
                for item in data:
                    if item['departament'] == dep:
                        data_json_confirmed[ dep ].append( item['confirmed'] )
                        data_json_death[ dep ].append( item['deaths'] )
                        data_json_recovered[ dep ].append( item['recovered'] )
                        data_json_suspects[ dep ].append( item['suspects'] )
                        data_json_discarted[ dep ].append( item['discarded'] )

            with open( lpath + '/static/confirmed.json' , 'w' ) as jsonfile:
                json.dump( data_json_confirmed, jsonfile )

            with open( lpath + '/static/death.json' , 'w' ) as jsonfile:
                json.dump( data_json_death, jsonfile )

            with open( lpath + '/static/recovered.json' , 'w' ) as jsonfile:
                json.dump( data_json_recovered, jsonfile )

            with open( lpath + '/static/suspects.json' , 'w' ) as jsonfile:
                json.dump( data_json_suspects, jsonfile )

            with open( lpath + '/static/discarted.json' , 'w' ) as jsonfile:
                json.dump( data_json_discarted, jsonfile )
    finally:
        conn.close()

get_today_data()

