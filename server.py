from os import path, listdir, mkdir
import requests
from flask import Flask, render_template
import pymysql.cursors
import datetime
import json
import configparser
import pathlib

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('db_settings.ini')

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


@app.route( '/' )
def home():
    lpath = config[ 'mysqlDB' ][ 'path' ].replace("'", "")

    filecontent = open( lpath + 'static/fechas.json' )
    fechajson = filecontent.readline()
    filecontent.close()

    filecontent = open( lpath + 'static/confirmed.json' )
    confirmed_json = json.loads( filecontent.readline() )
    filecontent.close()

    filecontent = open( lpath + 'static/death.json' )
    death_json = json.loads( filecontent.readline() )
    filecontent.close()

    filecontent = open( lpath + 'static/recovered.json' )
    recovered_json = json.loads( filecontent.readline() )
    filecontent.close()

    filecontent = open( lpath + 'static/discarted.json' )
    discarted_json = json.loads( filecontent.readline() )
    filecontent.close()

    return render_template( 'index.html', 
                            fechajson=fechajson, 
                            confirmed=confirmed_json, 
                            death=death_json, 
                            recovered=recovered_json, 
                            discarted=discarted_json, 
                            departments=departments 
                        )

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
