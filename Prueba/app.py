#CONEXION A BD SQL server
import pyodbc

#INFORMACION PARA CONEXTARSE A UNA BASE DE DATOS
server = 'localhost' #nombre del servidor
bd = 'PrI'#nombre base de datos
usuario = 'PI'
contraseña = '12345'
 
try:
    conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL server}; SERVER='+server+'; DATABASE='+bd+'; UID='+usuario+'; PWD='+contraseña)

    print('Conexión exitosa')
except:
    print('Error al intentar conectarse')

#CONSULTA A LA BD

cursor = conexion.cursor()
cursor.execute("select * from entregas;")

#entrega = cursor.fetchone() #trae uno por uno de los datos
#while entrega:
#    print(entrega)
#    entrega = cursor.fetchone()

entregas = cursor.fetchall()
for entrega in entregas:
    print (entrega)

cursor.close()

#INSERTAR DATOS A LA BD
#cursorInsert = conexion.cursor()

#Vnombre = "Prueba"
#insert = "insert into estados(nombre) values (?);"
#cursorInsert.execute(insert, Vnombre)

#cursorInsert.commit()
#cursorInsert.close()

#ACTUALIZAR DATOS DE LA BD
#cursorUpd = conexion.cursor()
#VUnombre = "PruebaUpd"
#VUid = "16"
#update = "update estados set nombre = ? where id = ?"
#cursorUpd.execute(update, VUnombre, VUid)

#cursorUpd.commit()
#cursorUpd.close()

#ELIMINAR DATOS DE LA BD
#cursorDlt = conexion.cursor()
#VDid = 16
#delete = "delete from estados where id = ?"
#cursorDlt.execute(delete, VDid)

#cursorDlt.commit()
#cursorDlt.close()

conexion.close() 