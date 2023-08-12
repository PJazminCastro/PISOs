from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import UserMixin
import pyodbc
import os
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
#inicialización del servidor Flask
app = Flask(__name__)

#Configuracion de la conexion
server = 'localhost' #nombre del servidor
bd = 'PrI'#nombre base de datos
usuario = 'PI'
contraseña = '12345'
 
try:
    conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL server}; SERVER='+server+'; DATABASE='+bd+'; UID='+usuario+'; PWD='+contraseña)

    print('Conexión exitosa')
except:
    print('Error al intentar conectarse')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Proyecto integrador/static/img'
app.secret_key = 'mysecretkey'


#Declaramos una ruta
#ruta Index http://localhost:5000
#ruta se compone de nombre y funcion
@app.route('/')
def index():
     return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        VFecha = datetime.now()
        rol = 2
        
        CS = conexion.cursor()
        CS.execute('INSERT INTO personas (nombre, ap, am, telefono, matricula, correo, contraseña, fechaalta, rol) VALUES (?,?,?,?,?,?,?,?,?)', (VNom, VAp, VAm, VTel, VMat, VCorr, VPass, VFecha, rol))
        conexion.commit()
        flash('Usuario agregado correctamente')
        return redirect(url_for('index'))
    return render_template('registro_usuarios.html')
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Matricula' not in session:
            flash('Debe iniciar sesión para acceder a esta página.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        CS = conexion.cursor()
        
        consulta = "SELECT Correo FROM personas WHERE Correo = ? AND Contraseña = ?"
        CS.execute(consulta, (VCorr, VPass))
        resultado = CS.fetchone()
        Rol = "Select Rol, Matricula from personas where correo = ? and contraseña = ?"
        
        if resultado is not None:
            CS.execute(Rol,(VCorr, VPass))
            rol_resultado = CS.fetchone()
            if rol_resultado is not None and rol_resultado[0] == 1:
                session['Matricula'] = rol_resultado[1]
                return redirect(url_for('main'))
            else:
                session['Matricula'] = rol_resultado[1]
                return redirect(url_for('cliente'))
        else:
            flash('Correo o contraseña incorrectos. Intente nuevamente.')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/main', methods=['GET'])
@login_required
def main():
    return render_template('main_menu.html')


@app.route('/cliente', methods=['GET'])
@login_required
def cliente():
    return render_template('mm_cl.html')


@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    productos = obtener_productos()
    ultimo_folio = obtener_ultimo_folio()
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad * platillos.costo) FROM ticket t INNER JOIN personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id where pedidos.idpersona = ? and pedidos.id = ? group by pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id, ultimo_folio))
    consBU = cursorBU.fetchall()
    flash("Su orden es la numero " + str(ultimo_folio) + ", Favor de pagar en caja") 
    return render_template('menu.html', productos=productos, listaPedido=consBU)

def obtener_productos():
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM platillos')
    productos = cursor.fetchall()
    cursor.close()
    return productos

def agregar_producto(nombre, precio, estatus):
    estatus = 'Disponible'
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos (nombreP, costo, estatus) VALUES (?,?,?)', (nombre, precio, estatus))
    cursor.commit()
    cursor.close()

@app.route('/orden', methods=['GET', 'POST'])
@login_required
def orden():
    productos = obtener_productos()
    nuevo_folio = obtener_ultimo_folio()
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON personas.id = pedidos.idpersona inner join platillos on pedidos.idplatillo = pedidos.id where pedidos.idpersona = ? and pedidos.id = ? group by pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id, nuevo_folio))
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

@app.route('/buscar', methods=['POST', 'GET'])
@login_required
def buscar():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas on pedidos.idpersona  = personas.id inner join platillos on perdidos.idplatillo = platillos.id group by pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo')

        else:
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillos = platillos.id WHERE pedidos.id = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo', (VBusc,))
        consBP = cursorBU.fetchall()
        
        if consBP is not None:
            return render_template('buscar_pedido.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_pedido.html', mensaje=mensaje)
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillos = platillos.id WHERE pedidos.id = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo')
    consBU = cursorBU.fetchall()
    return render_template('buscar_pedido.html', listaPedido=consBU)


@app.route('/visualizarAct/<string:id>')
@login_required
def visualizar(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from personas where Matricula = ?', (id,))
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_usuario.html', UpdUsuario = visualisarDatos)


@app.route('/actualizar/<id>', methods=['POST'])
@login_required
def actualizar(id):
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VTel = request.form['txtTel']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        VFecha = datetime.now()
        rol = 2
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update personas set Nombre = ?, Ap = ?, Am = ?, Telefono = ?,  Correo = ?, Contraseña = ?, fechaalta = ?, rol = ? where Matricula = ?', (VNom, VAp, VAm, VTel, VCorr, VPass, VFecha, rol, id))
        conexion.commit()
    flash ('El usuario con Matricula' + id +  'se actualizo correctamente.')
    return redirect(url_for('buscaru'))

@app.route("/confirmacion/<id>")
@login_required
def eliminar(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from personas where Matricula = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_usuarios.html', usuario=consuUsuario)

@app.route("/eliminar/<id>", methods=['POST'])
@login_required
def eliminarBD(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idpersonas = ?', (id,))
    conexion.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from personas where Matricula = ?', (id,))
    conexion.commit()
    flash('Se elimino el usuario con Matricula'+ id)
    return redirect(url_for('buscaru'))

@app.route('/buscaru', methods=['GET', 'POST'])
@login_required
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
    cursorBU.execute('SELECT * FROM personas')
    consBU = cursorBU.fetchall()
    return render_template('buscar_Usuario.html', listaUsuario=consBU)

@app.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre_producto = request.form['txtProd']
        precio_producto = request.form['txtPrec']
        imagen_producto = request.files['imagen_producto']
        estatus = 'Disponible'
        if imagen_producto and allowed_file(imagen_producto.filename):
            nombre_archivo = nombre_producto + '.jpg'
            imagen_producto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
            CS = conexion.cursor()
            CS.execute('INSERT INTO platillos (nombreP, costo, estatus) VALUES (%s,%s)', (nombre_producto, precio_producto, estatus))
            conexion.commit()
            flash(f'El producto {nombre_producto} se ha registrado correctamente', 'success')
            return redirect(url_for('vista_prev'))
    return render_template('Nuevo.html')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/buscarm', methods=['GET', 'POST'])
@login_required
def buscarm():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT * FROM platillos')
        else:
            cursorBU.execute('SELECT * FROM platillos WHERE nombreP = ?', (VBusc,))
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
@login_required
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

def agregar_producto(nombre, precio, estatus):
    estatus = 'Disponible'
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos(nombreP, costo, estatus) VALUES (?,?,?)', (nombre, precio, estatus))
    cursor.commit()
    cursor.close()

#VER ACTUALIZACIONES MENU
@app.route('/visualizarMen/<string:id>')
@login_required
def visualizarMen(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('SELECT * FROM platillos WHERE id = ?', (id, ))
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_menu.html', UpdMenu = visualisarDatos)

#ACTUALIZAR PRODUCTOS
@app.route('/actualizarm/<id>', methods=['POST'])
@login_required
def actualizarP(id):
    if request.method == 'POST':
        varPlatillo = request.form['txtPlatillo']
        varPrecio = request.form['txtPrecio']
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update platillos set nombreP = ?, costo = ? where id = ?', ( varPlatillo, varPrecio, id))
        conexion.commit()
    flash ('El platillo  ' + varPlatillo +  ' se actualizo correctamente.')
    return redirect(url_for('buscarm'))

@app.route("/confirmacionm/<id>")
@login_required
def eliminarm(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from platillos where ID = %s', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_menu.html', menu=consuUsuario)

@app.route("/eliminarm/<id>", methods=['POST'])
@login_required
def eliminarBDm(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idplatillos = ?', (id,))
    conexion.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from platillos where ID = ?', (id,))
    conexion.commit()
    flash('Se elimino el producto')
    return redirect(url_for('buscarm'))

@app.route('/registroa', methods=['GET', 'POST'])
@login_required
def registroa():
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        VFecha = datetime.now()
        rol = 1
        
        CS = conexion.cursor()
        CS.execute('INSERT INTO personas (nombre, ap, am, telefono, matricula, correo, contraseña, fechaalta, rol) VALUES (?,?,?,?,?,?,?,?,?)', (VNom, VAp, VAm, VTel, VMat, VCorr, VPass, VFecha, rol))
        conexion.commit()
        flash('Administrador agregado correctamente')
        return redirect(url_for('main'))

    return render_template('registro_Admin.html')


@app.route('/visualizarActc/<string:id>')
@login_required
def visualizarc(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from personas where Matricula = %s', (id,))
    visualisarDatos = cursorVis.fetchone()
    return render_template('act_mi_usu.html', UpdUsuario = visualisarDatos)


@app.route('/actualizarc/<id>', methods=['POST'])
@login_required
def actualizarc(id):
    if request.method == 'POST':
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VTel = request.form['txtTel']
        VMat = request.form['txtMat']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        VFecha = datetime.now()
        rol = 1
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update persona set nombre=?, ap=?, am=?, telefono=?, matricula=?, correo=?, contraseña=?, fechaalta=?, rol=? where Matricula = ?', ( VNom, VAp, VAm, VTel, VMat, VCorr, VPass, VFecha, rol, id))
        conexion.commit()
    flash ('El usuario se actualizo correctamente.')
    return redirect(url_for('mc'))

@app.route("/confirmacionc/<id>")
@login_required
def eliminarc(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from personas where Matricula = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('elim_mi_usu.html', usuario=consuUsuario)

@app.route("/eliminarc/<id>", methods=['POST'])
@login_required
def eliminarBDc(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idpersonas = ?', (id,))
    conexion.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from personas where Matricula = ?', (id,))
    conexion.commit()
    session.pop('Matricula', None)
    flash('Se elimino su cuenta')
    return redirect(url_for('login'))

@app.route('/mc', methods=['GET', 'POST'])
@login_required
def mc():
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM personas where Matricula = ?',(user_id,))
    consBU = cursorBU.fetchall()
    return render_template('mc.html', listaUsuario=consBU)


@app.route('/buscarp', methods=['POST', 'GET'])
@login_required
def buscarp():
    if request.method == 'POST':
        VBusc = request.form['busc']
        user_id = session.get('Matricula')
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillos = platillos.id WHERE pedidos.id = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id,))

        else:
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillos = platillos.id WHERE pedidos.id = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo', (user_id,VBusc, ))
        consBP = cursorBU.fetchall()
        
        if consBP is not None:
            return render_template('mis_pedidos.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('bmis_pedidos.html', mensaje=mensaje)
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillos = platillos.id WHERE pedidos.id = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id,))
    consBU = cursorBU.fetchall()
    return render_template('mis_pedidos.html', listaPedido=consBU)

@app.route('/conf/<id>', methods=['GET', 'POST'])
@login_required
def conf(id):
    curEditar = conexion.cursor()
    curEditar.execute('SELECT * FROM platillos WHERE nombreP = ?', (id,))
    producto_principal = curEditar.fetchone()

    if request.method == 'POST':
        Vcant = request.form['cantidad']
        user_id = session.get('Matricula')
        curID = conexion.cursor()
        curID.execute('select id from platillos where nombreP = ?', (id,))
        Vplatillos = curID.fetchone()
        Ventrega = 6
        Vpago = 2
        fecha = datetime.now()
        Vcafe = 1
        cursorBU = conexion.cursor()
        
        cursorBU.execute('INSERT INTO pedidos(idpersona, idplatillo, identrega, idpago, fecha, cantidad, idcafeteria) VALUES (?,?,?,?,?,?,?)', (user_id, Vplatillos, Ventrega, Vpago, fecha, Vcant, Vcafe))
        conexion.commit()
        cursorBU.close()
        return redirect(url_for('menu'))
    
    return render_template('compra.html', producto_principal=producto_principal)

@app.route('/cerrar')
def cerrar():
    session.pop('Matricula', None)
    return redirect(url_for('index'))

@app.route("/confirmacionp/<id>")
@login_required
def eliminarp(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from pedidos where ID = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_prod.html', menu=consuUsuario)

@app.route("/eliminarp/<id>", methods=['POST'])
@login_required
def eliminarBDp(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where ID = ?', (id,))
    conexion.commit()
    flash('Se elimino el producto')
    return redirect(url_for('menu'))

#Ejecucion de servidor
if __name__ =='__main__':
    app.run(port=3000,debug=True)
    
    

