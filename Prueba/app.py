#CONEXION A BD SQL server
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session, flash

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
#cursor.execute("select * from entregas;")

#entrega = cursor.fetchone() #trae uno por uno de los datos
#while entrega:
#    print(entrega)
#    entrega = cursor.fetchone()

#entregas = cursor.fetchall()
#for entrega in entregas:
#    print (entrega)

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

#HTML
app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
        return render_template('index.html')

#RUTA DEL LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        cursorLog = conexion.cursor()
        Vmatricula = request.form['matricula']
        Vcontrasena = request.form['contrasena']
        #VERIFICACION DE CREDENCIALES
        verificacion = "select * from Usuarios where matricula = ? and contraseña = ?"
        cursorLog.execute(verificacion, Vmatricula, Vcontrasena)
        resultado = cursorLog.fetchone()
        rol = "select rol from Usuarios where matricula = ? and contraseña = ?"
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

@app.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

#CIERRE DE SESIÓN
@app.route('/logout')
def logout():
    session.pop('matricula', None)
    return redirect(url_for('login'))

#REGISTRO USUARIOS 
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        VMat = request.form['txtMat']
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        
        cursorReg = conexion.cursor()
        cursorReg.execute('INSERT INTO usuarios (Matricula,Nombre, Ap, Am, Correo, Contraseña, Rol) VALUES (?,?,?,?,?,?,2)', (VMat, VNom, VAp, VAm, VCorr, VPass))
        cursorReg.commit()
        flash('Usuario agregado correctamente')
        return redirect(url_for('index'))

    return render_template('registro_usuarios.html')

#BUSCAR PEDIDOS
@app.route('/buscar', methods=['POST', 'GET'])
def buscar():
    if request.method == 'POST':
        VBusc = request.form['busc']
        
        cursorBU = conexion.cursor()
        if not VBusc:
            cursorBU.execute('SELECT tickets.ID, tickets.folio_ticket, tickets.idcliente, platillos.nombreP, tickets.cantidad FROM tickets  INNER JOIN platillos ON tickets.idplatillo = platillos.ID')

        else:
            cursorBU.execute('SELECT tickets.ID, tickets.folio_ticket, personas.nombre, platillos.nombreP, tickets.cantidad, sum(tickets.cantidad *  platillos.costo) FROM tickets  INNER JOIN platillos ON tickets.idplatillo = platillos.ID INNER JOIN clientes on tickets.idcliente = clientes.id INNER JOIN personas on clientes.idpersona = personas.id  WHERE folio_ticket = ? group by tickets.id, Tickets.folio_ticket, personas.nombre, platillos.nombreP, Tickets.cantidad', (VBusc,))
        consBP = cursorBU.fetchall()
        
        if consBP is not None:
            return render_template('buscar_pedido.html', listaPedido=consBP)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_pedido.html', mensaje=mensaje)
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT tickets.ID, tickets.folio_ticket, personas.nombre, platillos.nombreP, tickets.cantidad, sum(tickets.cantidad *  platillos.costo) FROM tickets  INNER JOIN platillos ON tickets.idplatillo = platillos.ID INNER JOIN clientes on tickets.idcliente = clientes.id INNER JOIN personas on clientes.idpersona = personas.id group by tickets.id, Tickets.folio_ticket, personas.nombre, platillos.nombreP, Tickets.cantidad')
    consBU = cursorBU.fetchall()
    return render_template('buscar_pedido.html', listaPedido=consBU)

#VER ACTUALIZACIONES USUARIOS
@app.route('/visualizarAct/<string:id>')
def visualizar(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from usuarios where Matricula = ?', id)
    visualisarDatos = cursorVis.fetchone()
    return render_template('actualizar_usuario.html', UpdUsuario = visualisarDatos)

#ACTUALIZAR USUARIOS
@app.route('/actualizar/<id>', methods=['POST'])
def actualizar(id):
    if request.method == 'POST':
        varNombre = request.form['txtNombre']
        varAp = request.form['txtAp']
        varAm = request.form['txtAm']
        varCorreo = request.form['txtCorreo']
        varContraseña = request.form['txtContraseña']
        cursorUpd = conexion.cursor()
        cursorUpd.execute('update usuarios set Nombre = ?, Ap = ?, Am = ?, Correo = ?, Contraseña = ? where Matricula = ?', ( varNombre, varAp, varAm, varCorreo, varContraseña, id))
        cursorUpd.commit()
    flash ('El usuario con Matricula' + id +  'se actualizo correctamente.')
    return redirect(url_for('buscaru'))

#CONFIRMACION ELIMINAR USUARIO
@app.route("/confirmacion/<id>")
def eliminar(id):
    cursorConfi = conexion.cursor()
    cursorConfi.execute('select * from usuarios where Matricula = ?', id)
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
            cursorBU.execute('SELECT * FROM usuarios')
        else:
            cursorBU.execute('SELECT * FROM usuarios WHERE Matricula = ?', (VBusc,))
        consBU = cursorBU.fetchall()
        
        if consBU is not None:
            return render_template('buscar_Usuario.html', listaUsuario=consBU)
        else:
            mensaje = 'No se encontraron resultados.'
            return render_template('buscar_Usuario.html', mensaje=mensaje)
    
    cursorBU = conexion.cursor()
    cursorBU.execute('SELECT * FROM usuarios')
    consBU = cursorBU.fetchall()
    return render_template('buscar_Usuario.html', listaUsuario=consBU)

#METODO DE PAGO
@app.route('/metodo/<string:id>')
def metodo(id):
    cursorVis = conexion.cursor()
    cursorVis.execute('select * from usuarios where Matricula = ?', (id,))
    visualisarDatos = cursorVis.fetchone()
    return render_template('metodo_pago.html', UpdUsuario = visualisarDatos)

@app.route('/met/<id>', methods=['GET', 'POST'])
def met(id):
    if request.method == 'POST':
        if request.form['txtMet'] == 'efectivo':
            flash('Eligio efectivo')
            return redirect(url_for('main'))
        
        elif request.form['txtMet'] == 'tarjeta':
            VMat = request.form['txtNum']
            VEnom = request.form['txtNom']
            VNom = request.form['txtVen']
            VAp = request.form['txtCVV']
    
            
            CS = conexion.cursor()
            CS.execute('INSERT INTO tarjetas (cliente, numero, nombre, vencimiento, CVV) VALUES (?, ?, ?, ?, ?)', id,VMat, VEnom, VNom, VAp)
            CS.commit()
            flash('Tarjeta agregada correctamente')
            return redirect(url_for('consultar'))

#NUEVO PLATILLO
@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        VProd = request.form['txtProd']
        VPrec = request.form['txtPrec']
        VDisp = request.form['txtDisp']
        
        CS = conexion.cursor()
        CS.execute('INSERT INTO platillos(nombreP, costo, estatus) VALUES (?,?,?)', VProd, VPrec, VDisp)
        CS.commit()
        flash('Producto agregado correctamente')
        return redirect(url_for('main'))
    return render_template('Nuevo.html')

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

#CONFIRMACON ELIMINAR MENU
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
    cursorDlt.execute('delete from ticket where idplatillo = ?', (id,))
    cursorDlt.commit()
    cursorDlt = conexion.cursor()
    cursorDlt.execute('delete from platillo where ID = ?', (id,))
    cursorDlt.commit()
    flash('Se elimino el producto')
    return redirect(url_for('buscarm'))

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

#REGISTRO ADMINISTRADOR
@app.route('/registroa', methods=['GET', 'POST'])
def registroa():
    if request.method == 'POST':
        VMat = request.form['txtMat']
        VNom = request.form['txtNom']
        VAp = request.form['txtAp']
        VAm = request.form['txtAm']
        VCorr = request.form['txtCorr']
        VPass = request.form['txtPass']
        
        CS = conexion.cursor()
        CS.execute('INSERT INTO usuarioS (Matricula,Nombre, Ap, am, Correo, Contraseña, Rol) VALUES (?,?,?,?,?,?,1)', (VMat, VNom, VAp, VAm, VCorr, VPass))
        CS.commit()
        flash('Administrador agregado correctamente')
        return redirect(url_for('main'))

    return render_template('registro_Admin.html')


if __name__ == '__main__':
    app.run(port=300, debug=True)

conexion.close() 