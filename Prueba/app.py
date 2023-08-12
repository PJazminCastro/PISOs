#CONEXION A BD SQL server
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import UserMixin
import os
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime

#INFORMACION PARA CONECTARSE A UNA BASE DE DATOS
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

#HTML
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Proyecto integrador/static/img'
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
        return render_template('index.html')

#REGISTRO USUARIOS 
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VCorr = request.form['txtCorr']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VPass = request.form['txtPass']
        Vfecha = datetime.now()  # Agrega los paréntesis aquí para llamar a la función

        cursorReg = conexion.cursor()
        cursorReg.execute('INSERT INTO personas (nombre, ap, am, telefono, matricula, correo,  contraseña, fechaalta, rol) VALUES (?,?,?,?,?,?,?,?,2)', (VNom, VAp, VAm, VTel, VMat, VCorr, VPass, Vfecha))

        conexion.commit()  # Realiza el commit en la conexión, no en los cursores

        flash('Usuario agregado correctamente')
        return redirect(url_for('index'))
    return render_template('registro_usuarios.html')



#RUTA DEL LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        cursorLog = conexion.cursor()
        Vmatricula = request.form['matricula']
        Vcontrasena = request.form['contrasena']
        #VERIFICACION DE CREDENCIALES
        verificacion = "select * from personas where matricula = ? and contraseña = ?"
        cursorLog.execute(verificacion, (Vmatricula, Vcontrasena))
        resultado = cursorLog.fetchone()
        rol = "select rol from personas where matricula = ? and contraseña = ?"
        #VALIDAR CREDENCIALES
        if resultado is not None:
            cursorLog.execute(rol, (Vmatricula, Vcontrasena))
            rolResultado = cursorLog.fetchone()
            if rolResultado is not None and rolResultado[0] ==1:
                return redirect(url_for('main'))
            else:
                flash ('Correo o contraseña incorrectos.')
                return redirect(url_for('cliente'))
        else:
            flash('Correo o contraseña oncorrector.')
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/main', methods=['GET'])

def main():
    return render_template('main_menu.html')

@app.route('/cliente', methods=['GET'])

def cliente():
    return render_template('mm_cl.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    productos = obtener_productos()
    ultimo_folio = obtener_ultimo_folio()
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.ID,  personas.nombre, platillos.nombreP, pedidos.cantidad, sum(platillos.costo * pedidos.cantidad) FROM pedidos INNER JOIN platillos ON pedidos.idplatillo = platillos.id inner join personas on pedidos.idpersona = personas.id where pedidos.idpersona = ? and pedidos.id = ? group by pedidos.ID,  personas.nombre, platillos.nombreP, pedidos.cantidad',(user_id, ultimo_folio))
    consBU = cursorBU.fetchall()
    flash("Su orden es la numero " + str(ultimo_folio) + ", Favor de pagar en caja") 
    return render_template('menu.html', productos=productos, listaPedido=consBU)    

def obtener_productos():
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM platillos')
    productos = cursor.fetchall()
    cursor.close()
    return productos

def agregar_producto(nombre, precio):
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos (nombreP, costo) VALUES (?, ?)', (nombre, precio))
    cursor.commit()
    cursor.close()

@app.route('/orden', methods=['GET', 'POST'])
def orden():
    productos = obtener_productos()
    nuevo_folio = obtener_ultimo_folio()
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN platillos ON pedidos.idplatillo = platillos.id inner join personas on pedidos.idpersona = personas.id where pedidos.idpersona = ? and pedidos.id = ? group by pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad',(user_id, nuevo_folio))
    consBU = cursorBU.fetchall()
    if not consBU:
        flash('No se realizó ninguna orden, por favor ordene algun producto.')
        return redirect(url_for('menu'))
    else:
        CS = conexion.cursor()
        CS.execute('INSERT INTO orden (x) VALUES (1)')
        conexion.commit()
        return render_template('orden.html', productos=productos, listaPedido=consBU, nuevo_folio=nuevo_folio)
    

def obtener_ultimo_folio():
    cursor = conexion.cursor()
    cursor.execute('SELECT MAX(ID) FROM orden')
    ultimo_folio = cursor.fetchone()[0]
    cursor.close()
    return ultimo_folio or 1

#BUSCAR PEDIDOS
@app.route('/buscar', methods=['POST', 'GET'])

def buscar():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id  group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id')

        else:
            cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id WHERE pedidos.id = ? group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id', (VBusc,))
        consBP = cursorBU.fetchall()
        
        if consBP is not None:
            return render_template('buscar_pedido.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_pedido.html', mensaje=mensaje)
    cursorBU = conexion.cursor()
    cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id  group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id')
    consBU = cursorBU.fetchall()
    return render_template('buscar_pedido.html', listaPedido=consBU)

#VER ACTUALIZACIONES USUARIOS
@app.route('/visualizarAct/<string:id>')
def visualizar(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from personas where Matricula = ?', id)
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_usuario.html', UpdUsuario = visualisarDatos)

#ACTUALIZAR USUARIOS
@app.route('/actualizar/<id>', methods=['POST'])

def actualizar(id):
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VCorr = request.form['txtCorr']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VPass = request.form['txtPass']
        Vfecha = datetime.now()  # Agrega los paréntesis aquí para llamar a la función

        cursorUpd = conexion.cursor()
        cursorUpd.execute('update personas set nombre=?, ap=?, am=?, telefono=?, matricula=?, correo=?,  contraseña=?, fechaalta=?, rol=2)', (VNom, VAp, VAm, VTel, VMat, VCorr, VPass, Vfecha))
        cursorUpd.commit()
    flash ('El usuario con Matricula' + id +  'se actualizo correctamente.')
    return redirect(url_for('buscaru'))

#CONFIRMACION ELIMINAR USUARIO
@app.route("/confirmacion/<id>")

def eliminar(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from personas where Matricula = ?', id)
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_usuarios.html', usuario=consuUsuario)

#ELIMINAR USUARIO
@app.route("/eliminar/<id>", methods=['POST'])

def eliminarBD(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from tarjetas where cliente = ?', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from ticket where id_cliente = ?', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from usuario where Matricula = ?', (id,))
    cursorDlt.commit()
    flash('Se elimino el usuario con Matricula'+ id)
    return redirect(url_for('buscaru'))

#BUSCAR USUARIOS
@app.route('/buscaru', methods=['GET', 'POST'])

def buscaru():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT * FROM personas')
        else:
            cursorBU.execute('SELECT * FROM personas WHERE Matricula = ?', (VBusc,))
        consBU = cursorBU.fetchall()
        
        if consBU is not None:
            return render_template('buscar_Usuario.html', listaUsuario=consBU)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_Usuario.html', mensaje=mensaje)
    
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM personas where rol = 2')
    consBU = cursorBU.fetchall()
    return render_template('buscar_Usuario.html', listaUsuario=consBU)

#METODO DE PAGO
@app.route('/metodo/<string:id>')

def metodo(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from usuarios where Matricula = ?', (id,))
    visualisarDatos = cursorVis.fetchone()
    return render_template('metodo_pago.html', UpdUsuario = visualisarDatos)

@app.route('/met/<matricula>', methods=['GET', 'POST'])
def met(id):
    if request.method == 'POST':
        if request.form['txtMet'] == 'efectivo':
            flash('Eligio efectivo')
            return redirect(url_for('main'))
        
        elif request.form['txtMet'] == 'tarjeta':
            VNum = request.form['txtNum']
            VNom = request.form['txtNom']
            VVen = request.form['txtVen']
            CVV = request.form['txtCVV']            
            CS = conexion.cursor()
            CS.execute('INSERT INTO tarjetas (numero, nombre, vencimiento, CVV, cliente) VALUES (?, ?, ?, ?, ?)', VNum, VNom, VVen, CVV, id)
            CS.commit()
            flash('Tarjeta agregada correctamente')
            return redirect(url_for('consultar'))

#NUEVO PLATILLO
@app.route('/nuevo', methods=['GET', 'POST'])

def nuevo():
    if request.method == 'POST':
        VProd = request.form['txtProd']
        VPrec = request.form['txtPrec']
        imagen_producto = request.files['imagen_producto']
        Vestatus = 'Disponible'
        if imagen_producto and allowed_file(imagen_producto.filename):
            nombre_archivo = secure_filename(VProd) + '.jpg'
            imagen_producto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
            CS = conexion.cursor()
            CS.execute('INSERT INTO platillos (nombreP, costo, estatus) VALUES (?,?,?)', (VProd, VPrec, Vestatus))
            CS.commit()
            flash(f'El producto {VProd} se ha registrado correctamente', 'success')
            return redirect(url_for('vista_prev'))
    return render_template('Nuevo.html')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#BUSCAR MENU DEL DIA
@app.route('/buscarm', methods=['GET', 'POST'])

def buscarm():
    if request.method == 'POST':
        VBusc = request.form['busc']
        VDisp = "Disponible"
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT * FROM platillos')
        else:
            cursorBU.execute('SELECT * FROM platillos WHERE nombreP = ? and estatus = ?', VBusc, VDisp)
        consBU = cursorBU.fetchall()
        
        if consBU is not None:
            return render_template('cons_Menu.html', listaUsuario=consBU)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('cons_Menu.html', mensaje=mensaje)
    
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM platillos')
    consBU = cursorBU.fetchall()
    return render_template('cons_Menu.html', listaUsuario=consBU)

@app.route('/vista_prev', methods=['GET', 'POST'])

def vista_prev():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        precio_producto = request.form['precio_producto']
        agregar_producto(nombre_producto, precio_producto)
    productos = obtener_productos()
    return render_template('vp.html', productos=productos)

def obtener_productos():
    cursor = conexion.cursor()
    cursor.execute('SELECT nombreP, costo FROM platillos')
    productos = cursor.fetchall()
    cursor.close()
    return productos

def agregar_producto(nombre, precio):
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos (nombreP, costo) VALUES (%s, %s)', (nombre, precio))
    cursor.commit()
    cursor.close()

#VER ACTUALIZACIONES MENU
@app.route('/visualizarMen/<string:id>')

def visualizarMen(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from platillos where id = ?', id)
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_menu.html', UpdMenu = visualisarDatos)

#ACTUALIZAR PRODUCTOS
@app.route('/actualizarm/<id>', methods=['POST'])

def actualizarP(id):
    if request.method == 'POST':
        varPlatillo = request.form['txtPlatillo']
        varPrecio = request.form['txtPrecio']
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update platillos set nombreP = ?, costo = ? where id = ?', ( varPlatillo, varPrecio, id))
        cursorUpd.commit()
    flash ('El platillo  ' + varPlatillo +  ' se actualizo correctamente.')
    return redirect(url_for('buscarm'))

#CONFIRMACION ELIMINAR MENU
@app.route("/confirmacionm/<id>")
def eliminarm(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from platillos where ID = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_menu.html', menu=consuUsuario)

#ELIMINAR PRODUCTO Y PEDIDO
@app.route("/eliminarm/<id>", methods=['POST'])
def eliminarBDm(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idplatillo = ?', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from platillos where ID = ?', (id,))
    cursorDlt.commit()
    flash('Se elimino el producto')
    return redirect(url_for('buscarm'))

#REGISTRO ADMINISTRADOR
@app.route('/registroa', methods=['GET', 'POST'])
def registroa():
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VCorr = request.form['txtCorr']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VPass = request.form['txtPass']
        Vfecha = datetime.now()  # Agrega los paréntesis aquí para llamar a la función

        cursorReg = conexion.cursor()
        cursorReg.execute('INSERT INTO personas (nombre, ap, am, telefono, matricula, correo,  contraseña, fechaalta, rol) VALUES (?,?,?,?,?,?,?,?,1)', (VNom, VAp, VAm, VTel, VMat, VCorr, VPass, Vfecha))

        conexion.commit()
        flash('Administrador agregado correctamente')
        return redirect(url_for('main'))
    return render_template('registro_Admin.html')

@app.route('/visualizarActc/<string:id>')

def visualizarc(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select personas.nombre, personas.ap, personas.correro, clientes.matricula from clientes inner join personas on clientes.idpersona = personas.id where matricula = ?', (id,))
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_usuario.html', UpdUsuario = visualisarDatos)


@app.route('/actualizarc/<id>', methods=['POST'])

def actualizarc(id):
    if request.method == 'POST':
 
        varNombre = request.form['txtNombre']
        varAp = request.form['txtAp']
        varAm = request.form['txtAm']
        varCorreo = request.form['txtCorreo']
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update usuarios set Nombre = ?, Ap = ?, Am = ?, Correo = ? where Matricula = ?', ( varNombre, varAp, varAm, varCorreo, id))
        cursorUpd.connection.commit()
    flash ('El usuario con Matricula' + id +  'se actualizo correctamente.')
    return redirect(url_for('mc'))

@app.route("/confirmacionc/<id>")

def eliminarc(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from usuario where Matricula = %s', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_usuarios.html', usuario=consuUsuario)

@app.route("/eliminarc/<id>", methods=['POST'])

def eliminarBDc(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from tarjetas where cliente = %s', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from ticket where id_cliente = %s', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from usuario where Matricula = %s', (id,))
    cursorDlt.commit()
    flash('Se elimino el usuario con Matricula'+ id)
    return redirect(url_for('mc'))

@app.route('/mc', methods=['GET', 'POST'])

def mc():

    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM usuarios')
    consBU = cursorBU.fetchall()
    return render_template('mc.html', listaUsuario=consBU)

@app.route('/conf/<id>', methods=['GET', 'POST'])
def conf(id):
    curEditar = conexion.cursor()
    curEditar.execute('SELECT * FROM platillos WHERE nombreP = ?', (id,))
    producto_principal = curEditar.fetchone()

    if request.method == 'POST':
        Vcant = request.form['cantidad']
        user_id = session.get('Matricula')
        cursorBU = conexion.cursor()
        Vestatus = 6
        Vpago = 2
        fecha = datetime.now()
        Vcafe = 1
        
        cursorBU.execute('INSERT INTO pedidos(idpersona, idplatillo, identrega, idpago, fecha, cantidad, idcafeteria) VALUES (?,?,?,?,?,?,?)', (user_id, id, Vestatus, Vpago, fecha, Vcant, Vcafe))
        conexion.commit()  # Commit the changes to the database
        cursorBU.close()
        return redirect(url_for('menu'))
    return render_template('compra.html', producto_principal=producto_principal)


#CIERRE DE SESIÓN
@app.route('/cerrar')
def cerrar():
    session.pop('Matricula', None)
    return redirect(url_for('index'))

#BUSCAR INGREDIENTES
@app.route('/buscari', methods=['GET', 'POST'])
def buscarI():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT * FROM ingredientes')
        else:
            cursorBU.execute('SELECT * FROM ingredientes WHERE nombre = ?', str(VBusc))
        consBU = cursorBU.fetchall()
        
        if consBU is not None:
            return render_template('ingredientes.html', listaIngredientes=consBU)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('ingredientes.html', mensaje=mensaje)
    
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM ingredientes')
    consBU = cursorBU.fetchall()
    return render_template('ingredientes.html', listaIngredientes=consBU)

if __name__ == '__main__':
    app.run(port=300, debug=True)

conexion.close() 