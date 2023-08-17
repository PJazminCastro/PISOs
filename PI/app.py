from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
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
        VCorr = request.form['txtMat']
        VPass = request.form['txtPass']
        CS = conexion.cursor()
        consulta = "SELECT Correo FROM personas WHERE matricula = ? AND Contraseña = ? and estatus = 1"
        CS.execute(consulta, (VCorr, VPass))
        resultado = CS.fetchone()
        Rol = "Select Rol, Matricula from personas where matricula = ? and contraseña = ? and estatus = 1"
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
    user_id = session.get('matricula')
    estatus = "Disponible"
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad * platillos.costo) FROM pedidos INNER JOIN personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id where personas.matricula = ? and pedidos.id = ? and platillos.estatus = ? group by pedidos.ID, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id, ultimo_folio, estatus))
    consBU = cursorBU.fetchall()
    return render_template('menu.html', productosD=productos, listaPedido=consBU)

def obtener_productos():
    cursor = conexion.cursor()
    cursor.execute('SELECT nombreP, costo, estatus FROM platillos where estatus = "Disponible"')
    productos = cursor.fetchall()
    cursor.close()
    return productos

def agregar_producto(nombre, precio, estatus):
    estatus = 'Disponible'
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos (nombreP, costo, estatus) VALUES (?,?,?)', (nombre, precio, estatus))
    cursor.commit()
    cursor.close()

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
            cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id where entregas.id != 4 and entregas.id != 5 group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id')
        else:
            cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id WHERE pedidos.id = ? group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id', (VBusc,))
        consBP = cursorBU.fetchall()
        if consBP is not None:
            return render_template('buscar_pedido.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_pedido.html', mensaje=mensaje)
    cursorBU = conexion.cursor()
    cursorBU.execute('select pedidos.id, personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, cantidad, sum(pedidos.cantidad *  platillos.costo) from pedidos inner join personas on pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id inner join entregas on pedidos.identrega = entregas.id inner join metoPago on pedidos.idpago = metoPago.id where entregas.id != 4 and entregas.id != 5 group by personas.nombre, platillos.nombreP, entregas.estatus, metoPago.descripcion, pedidos.cantidad, pedidos.id')
    consBU = cursorBU.fetchall()
    return render_template('buscar_pedido.html', listaPedido=consBU)

@app.route('/visualizarAct/<string:id>')
@login_required
def visualizar(id):
    cursorId = conexion.cursor()
    cursorId.execute('select matricula from personas where id = ?', (id,))
    matricula = cursorId.fetchone()
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from personas where matricula = ?', (matricula[0],))
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
        cursorUpd.execute('update personas set Nombre = ?, Ap = ?, Am = ?, Telefono = ?,  Correo = ?, Contraseña = ?, fechaalta = ?, rol = ? where id = ?', (VNom, VAp, VAm, VTel, VCorr, VPass, VFecha, rol, id))
        conexion.commit()
    flash ('El usuario con matricula ' + id +  ' se actualizo correctamente.')
    return redirect(url_for('buscaru'))

@app.route("/confirmacion/<string:id>")
@login_required
def eliminar(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from personas where id = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_usuarios.html', usuario=consuUsuario)

@app.route("/eliminar/<string:id>", methods=['POST'])
@login_required
def eliminarBD(id):
    if request.method == 'POST':
        cursorDlt = conexion.cursor()
        cursorDlt.execute('update pedidos set identrega = 5 where idpersona = ?', (id,))
        conexion.commit()
        cursorDlt.execute('update personas set estatus = 0 where id = ?', (id,))
        conexion.commit()
    flash('Se eliminó el usuario con Matricula ' + id)
    return redirect(url_for('buscaru'))

@app.route('/buscaru', methods=['GET', 'POST'])
@login_required
def buscaru():
    if request.method == 'POST':
        VBusc = request.form['busc']
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT * FROM personas where estatus = 1')
        else:
            cursorBU.execute('SELECT * FROM personas WHERE Matricula = ? and estatus = 1', (VBusc,))
        consBU = cursorBU.fetchall()
        if consBU is not None:
            return render_template('buscar_Usuario.html', listaUsuario=consBU)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_Usuario.html', mensaje=mensaje)
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM personas where estatus = 1')
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
            CS.execute('INSERT INTO platillos (nombreP, costo, estatus) VALUES (?,?,?)', (nombre_producto, precio_producto, estatus))
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
    return render_template('vp.html', productosD=productos)

def obtener_productos():
    cursor = conexion.cursor()
    cursor.execute('SELECT nombreP, costo, estatus FROM platillos')
    productosD = cursor.fetchall()
    cursor.close()
    return productosD

def agregar_producto(nombre, precio, estatus):
    estatus = 'Disponible'
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos(nombreP, costo, estatus) VALUES (?,?,?)', (nombre, precio, estatus))
    cursor.commit()
    cursor.close()

@app.route('/visualizarMen/<string:id>')
@login_required
def visualizarMen(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('SELECT * FROM platillos WHERE id = ?', (id, ))
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_menu.html', UpdMenu = visualisarDatos)

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
    cursorConfi.execute('select * from platillos where ID = ?', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('borrar_menu.html', menu=consuUsuario)

@app.route("/eliminarm/<id>", methods=['POST'])
@login_required
def eliminarBDm(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idplatillo = ?', (id,))
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
    cursorId = conexion.cursor()
    cursorId.execute('select matricula from personas where id = ?', (id,))
    matricula = cursorId.fetchone()
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from personas where matricula = ?', (matricula[0],))
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_usuario.html', UpdUsuario = visualisarDatos)

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
    cursorConfi.execute('select * from personas where Matricula = ? and estatus = 1', (id,))
    consuUsuario = cursorConfi.fetchone()
    return render_template('elim_mi_usu.html', usuario=consuUsuario)

@app.route("/eliminarc/<id>", methods=['POST'])
@login_required
def eliminarBDc(id):
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from pedidos where idpersonas = ? and estatus = 1', (id,))
    conexion.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from personas where Matricula = ? and estatus = 1', (id,))
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
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id WHERE personas.matricula = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id,))
        else:
            cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id WHERE pedidos.id = ? and personas.matricula = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo', (VBusc, user_id,))
        consBP = cursorBU.fetchall()
        if consBP is not None:
            return render_template('mis_pedidos.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('mis_pedidos.html', mensaje=mensaje)
    user_id = session.get('Matricula')
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad *  platillos.costo) FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id inner join platillos on pedidos.idplatillo = platillos.id WHERE personas.matricula = ? group by pedidos.id, personas.nombre, platillos.nombreP, pedidos.cantidad, platillos.costo',(user_id,))
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
        cursoridp = conexion.cursor()
        cursoridp.execute('select id from personas where matricula = ?', (user_id))
        Vidp = cursoridp.fetchone()
        curID = conexion.cursor()
        curID.execute('select id from platillos where id = ?', (id,))
        Vplatillos = curID.fetchone()
        Ventrega = 6
        Vpago = 1
        fecha = datetime.now()
        Vcafe = 1
        with conexion.cursor() as cursorBU:
            cursorBU.execute('INSERT INTO pedidos(idpersona, idplatillo, identrega, idpago, fecha, cantidad, idcafeteria) VALUES (?,?,?,?,?,?,?)', (Vidp[0], Vplatillos[0], Ventrega, Vpago, fecha, Vcant, Vcafe))
            cursorBU.commit()
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
    cursorDlt.execute('update platillos set estatus = "No disponible" where id = ', (id,))
    conexion.commit()
    flash('Se elimino el producto')
    return redirect(url_for('menu'))

@app.route('/buscari', methods=['GET', 'POST'])
def buscari():
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

#Procedimiento 2: Cancelar un pedido

#Funcion 1: Mostrar los datos que tendria un ticket de una compra [fecha, nombrecafe, productos, total, metodopago]
@app.route('/ver_ticket/<int:pedido_id>')
@login_required
def ver_ticket(pedido_id):
    cursor = conexion.cursor()
    cursor.execute('SELECT pedidos.fecha, personas.nombre, platillos.nombreP, pedidos.cantidad, sum(pedidos.cantidad * platillos.costo) AS total, metoPago.descripcion FROM pedidos INNER JOIN personas ON pedidos.idpersona = personas.id INNER JOIN platillos ON pedidos.idplatillo = platillos.id INNER JOIN metoPago ON pedidos.idpago = metoPago.id WHERE pedidos.id = ? group by pedidos.fecha, personas.nombre, platillos.nombreP, pedidos.cantidad, metoPago.descripcion', (pedido_id,))
    resultado = cursor.fetchone()

    if resultado:
        fecha = resultado.fecha
        cliente = resultado.nombre
        producto = resultado.nombreP
        cantidad = resultado.cantidad
        total = resultado.total
        metodo_pago = resultado.descripcion

        return render_template('ticket.html', fecha=fecha, cliente=cliente, producto=producto, cantidad=cantidad, total=total, metodo_pago=metodo_pago)
    else:
        flash('Pedido no encontrado.')
        return redirect(url_for('buscar'))

#Funcion 2: Obtener el corte de caja de un dia [total vendido, stock de ingredientes actualizados, platillos disponibles]
@app.route('/corte', methods=['POST'])
def corte():
    cursor = conexion.cursor()
    fecha = request.form['fecha']
    query = f"""
        SELECT SUM(pedidos.cantidad * platillos.costo) AS Total_Vendido,
               platillos.nombreP AS Platillo,
               ingredientes.stock AS Stock_Ingredientes
        FROM platillos
        INNER JOIN receta ON receta.idplatillo = platillos.id
        INNER JOIN ingredientes ON ingredientes.id = receta.idingrediente
        INNER JOIN pedidos ON pedidos.idplatillo = platillos.id AND CONVERT(DATE, pedidos.fecha) = '{fecha}'
        GROUP BY platillos.nombreP, ingredientes.stock
    """
    cursor.execute(query)
    results = cursor.fetchall()

    result_data = [
        {
            "Platillo": row.Platillo,
            "Total_Vendido": row.Total_Vendido if row.Total_Vendido is not None else 0,
            "Stock_Ingredientes": row.Stock_Ingredientes
        }
        for row in results
    ]
    return jsonify(result_data)

#Ejecucion de servidor
if __name__ =='__main__':
    app.run(port=3000,debug=True)