import csv
import pickle
import locale
from operator import truediv
import requests
import datetime
import json
from os.path import exists

# CONFIGURATION

# attribute -  money_spent
PAGINA_MAX = 35 # max entries you can update at once in exist.io
FILE_INPUT_CSV = "C:\\temp\\movimientos.csv" # csv - extract from Fintonic
FILETMP_LASTDATA = "c:\\temp\\Fintonic_Exist_io.bin" # pickle file used as a cache so we only update what changed - it will be created on first run
BEARER_TOKEN = '1111 BEARER TOKEN 1111' # bearer token for exist.io
url = 'https://exist.io/oauth2/access_token' # url to update values in exist.io
locale._override_localeconv["thousands_sep"] = "." # separator in the fintonic file
locale._override_localeconv["decimal_point"] = "," # separator in the fintonic file

# Fintonic categories to exclude (exclude those categories that do not represent your daily lifestyle)
# ALL CATEGORIES  = {'Otros organismos', 'Otros ocio', 'Ropa', 'Electrónica', 'Comunidad', 'Impuestos', 'Transferencias', 'Otros salud, saber y deporte', 'Televisión', 'Belleza', 'Material deportivo', 'Seguro auto', 'Hogar', 'Servicio doméstico', 'Otros servicios', 'Mantenimiento hogar', 'Electricidad', 'Hotel', 'Óptica y dentista', 'Otros gastos', 'Seguro viaje', 'Parking y peaje', 'Solidaridad', 'Regalos', 'Asociaciones', 'Supermercado', 'Médico', 'Niños y mascotas', 'Espectáculos', 'Asesores y abogados', 'Efectivo', 'Ayuntamiento', 'Otras compras', 'Cargos bancarios', 'Gasolina', 'Transportes', 'Farmacia', 'Deporte', 'Servicios y productos online', 'Multas y licencias', 'Estudios', 'Alquiler vehículos', 'Internet', 'Librería', 'Loterías', 'Mantenimiento vehículo', 'Restaurante', 'Préstamos', 'Seguro hogar'}
excluir = {'Otros organismos', 'Otros ocio', 'Comunidad', 'Impuestos', 'Transferencias', 'Otros salud, saber y deporte', 'Televisión', 'Seguro auto', 'Hogar', 'Servicio doméstico', 'Otros servicios', 'Mantenimiento hogar', 'Electricidad', 'Seguro viaje', 'Parking y peaje', 'Solidaridad', 'Asociaciones', 'Médico', 'Efectivo', 'Ayuntamiento', 'Otras compras', 'Cargos bancarios', 'Deporte', 'Servicios y productos online', 'Multas y licencias', 'Estudios', 'Internet', 'Mantenimiento vehículo', 'Préstamos', 'Seguro hogar'}


with open(FILE_INPUT_CSV, encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    dicc = {}
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            fechaValor = row[0]
            fechaOperacion =  row[1]
            importe =  row[2]
            moneda =  row[3]
            concepto =  row[4]
            entidad =  row[5]
            nombreProducto =  row[6]
            tipoProducto =  row[7]
            tipoMovimiento =  row[8]
            categoria =  row[9]
            nota =  row[10]

            if tipoMovimiento == "Gasto" and categoria not in excluir:
                
                dinero = -1 * locale.atof(importe)

                if fechaOperacion == "":
                    fechaOperacion = fechaValor
        
                keyFecha = datetime.datetime.strptime(fechaOperacion, "%d/%m/%y").strftime("%Y-%m-%d")
                valorexistente = dicc.get(keyFecha, 0.0)
                dicc[keyFecha] = valorexistente + dinero

            line_count += 1
    print(f'Processed {line_count} lines --> ', len(dicc.keys()))


# BEFORE calling exist.io you must
# 0. Create client https://exist.io/account/apps/
# 1. authorise, by opening in chrome the following URL 
# https://exist.io/oauth2/authorize?response_type=code&client_id=xxxxx&redirect_uri=https://localhost/&scope=read+write
# 2. Get bearer token
# 3. Activate money_spent attribute
#url = 'https://exist.io/api/1/attributes/acquire/'
#attributes = [{"name":"money_spent", "active":True}]
#response = requests.post(url, headers={'Authorization':'Bearer 58bearertoken27272', 'Content-Type': 'application/json; charset=utf-8'},data=json.dumps(attributes))


# 4. Update!

if exists(FILETMP_LASTDATA):

    with open(FILETMP_LASTDATA, 'rb') as handle:
        diccFromFile = pickle.load(handle)

else:
    diccFromFile = {}


diccFromFileChanged = False


attributes = []
i = 0
url = 'https://exist.io/api/1/attributes/update/'

for x in dicc:

    newItem = False

    if x in diccFromFile:
        if diccFromFile[x] != dicc[x]:
            diccFromFile[x] = dicc[x]
            diccFromFileChanged = True
            newItem = True
    else:
        diccFromFile[x] = dicc[x]
        diccFromFileChanged = True
        newItem = True

    if newItem:

        if dicc[x]<0:
            dineroPositivo = 0
        else:
            dineroPositivo = dicc[x]

        print({x}, " - ", {dineroPositivo})
        attributes.append({"name": "money_spent", "date": x, "value": dineroPositivo})
        
        i=i+1
        if i==PAGINA_MAX:
            data = json.dumps(attributes)
            response = requests.post(url, headers={'Authorization':f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json; charset=utf-8'}, data=data)
            print("RESET")
            i=0
            attributes = []

if len(attributes)>0:
    data = json.dumps(attributes)
    response = requests.post(url, headers={'Authorization':f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json; charset=utf-8'}, data=data)


if diccFromFileChanged:
    
    with open(FILETMP_LASTDATA, 'wb') as handle:
        pickle.dump(diccFromFile, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Process ends")
