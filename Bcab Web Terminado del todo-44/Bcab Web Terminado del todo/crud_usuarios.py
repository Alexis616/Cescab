from flask import Blueprint, render_template, request, redirect, flash,url_for
from conexion import get_db_connection,mysql
import hashlib
import subprocess

crud = Blueprint('crud', __name__)  # sirve para importar todo a otro py correctamente

# Función para cifrar contraseña en SHA-256 UTF-8
def cifrar_contrasena(contrasena):
    return hashlib.sha512(contrasena.encode('utf-8')).hexdigest()

@crud.route('/inicio_crud', methods=['GET'])
def index():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM usuarios  ORDER BY `usuarios`.`nombre` ASC")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM fichas")
    ficha = cursor.fetchone()

    cursor.close()
    conexion.close()
    return render_template('crud_usuarios.html', usuarios=usuarios, ficha=ficha)



@crud.route('/agregar', methods=['POST'])
def agregar():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    contrasena_cifrada = cifrar_contrasena(request.form['contrasena'])

    datos = (
        request.form['nombre'],
        request.form['apellido'],
        request.form['cedula'],
        request.form['correo_electronico'],
        contrasena_cifrada,  # Contraseña cifrada
        request.form['telefono'],
        request.form['tipo_vinculacion'],
        request.form['fecha_fin_contrato'],
        request.form['token'],
        request.form['codigo'],
        request.form['rol']
    )
    cursor.execute("""INSERT INTO usuarios 
        (nombre, apellido, cedula, correo_electronico, contrasena, telefono, tipo_vinculacion, fecha_fin_contrato, token, codigo, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, datos)
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect('/inicio_crud')

@crud.route('/eliminar_usuarios_seleccionados', methods=['POST'])
def eliminar_usuarios_seleccionados():
    ids = request.form.getlist('ids[]')
    if not ids:
        flash('No se seleccionaron usuarios para eliminar.')
        return redirect('/inicio_crud')
    
    conexion = get_db_connection()
    cursor = conexion.cursor()

    format_strings = ','.join(['%s'] * len(ids))
    sql = f"DELETE FROM usuarios WHERE id IN ({format_strings})"
    cursor.execute(sql, tuple(ids))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash(f'Se eliminaron {len(ids)} usuario(s) correctamente.')
    return redirect('/inicio_crud')


@crud.route('/editar/<int:id>')
def editar(id):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_usuario.html', usuario=usuario)

@crud.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    contrasena = request.form['contrasena']
    if contrasena.strip():
        contrasena_cifrada = cifrar_contrasena(contrasena)
        query = """UPDATE usuarios SET
            nombre=%s, apellido=%s, cedula=%s, correo_electronico=%s,
            contrasena=%s, telefono=%s, fecha_fin_contrato=%s, rol=%s
            WHERE id=%s"""
        datos = (
            request.form['nombre'],
            request.form['apellido'],
            request.form['cedula'],
            request.form['correo_electronico'],
            contrasena_cifrada,
            request.form['telefono'],
            request.form['fecha_fin_contrato'],
            request.form['rol'],
            id
        )
    else:
        query = """UPDATE usuarios SET
            nombre=%s, apellido=%s, cedula=%s, correo_electronico=%s,
            telefono=%s, fecha_fin_contrato=%s, rol=%s
            WHERE id=%s"""
        datos = (
            request.form['nombre'],
            request.form['apellido'],
            request.form['cedula'],
            request.form['correo_electronico'],
            request.form['telefono'],
            request.form['fecha_fin_contrato'],
            request.form['rol'],
            id
        )

    cursor.execute(query, datos)
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect('/inicio_crud')





# coordinaciones de fichas 


@crud.route('/editar_coordinador/<int:numeroFicha>')
def editar_coordinador(numeroFicha):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener la ficha
    cursor.execute("SELECT * FROM fichas WHERE numeroFicha = %s", (numeroFicha,))
    ficha = cursor.fetchone()
    
    # Obtener los usuarios con rol 'coordinador'
    cursor.execute("SELECT nombre, apellido, correo_electronico FROM usuarios WHERE rol = 'coordinador'")
    usuarios = cursor.fetchall()
    
    cursor.close()
    conexion.close()

    return render_template('coordinaciones.html', ficha=ficha, usuarios=usuarios)



@crud.route('/actualizar_coordinador', methods=['POST'])
def actualizar_coordinador():
    numeroFicha = request.form['numeroFicha']
    nombre_completo, correo = request.form['nuevoCoordinador'].split('|')

    cursor = get_db_connection()
    cursor.execute("""
        UPDATE fichas
        SET nombreCoordinador = %s, correoCoordinador = %s
        WHERE numeroFicha = %s
    """, (nombre_completo.strip(), correo.strip(), numeroFicha))
    mysql.connection.commit()
    cursor.close()

    # Redirige de nuevo a la página de edición de esa ficha
    return redirect(f'/editar_coordinador/{numeroFicha}')







@crud.route('/reemplazar_coordinador', methods=['POST'])
def reemplazar_coordinador():
    correo_actual = request.form['correo_actual']
    nuevo_correo = request.form['nuevo_correo']

    # Buscar el nombre del nuevo coordinador por correo
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT nombre, apellido FROM usuarios WHERE correo_electronico = %s", (nuevo_correo,))
    nuevo = cursor.fetchone()

    if nuevo:
        nuevo_nombre = f"{nuevo['nombre']} {nuevo['apellido']}"

        # Reemplazar todas las fichas
        cursor.execute("""
            UPDATE fichas
            SET nombreCoordinador = %s,
                correoCoordinador = %s
            WHERE correoCoordinador = %s
        """, (nuevo_nombre, nuevo_correo, correo_actual))
        conexion.commit()

    cursor.close()
    conexion.close() 
    flash('Cambio ejecutado con éxito')
    return redirect('/coordinaciones')
   
    


@crud.route('/coordinaciones')
def coordinaciones():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Traer todos los usuarios con rol coordinador
    cursor.execute("SELECT id, nombre, apellido, correo_electronico FROM usuarios WHERE LOWER(rol) = 'coordinador'")
    coordinadores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('coordinaciones.html', coordinadores=coordinadores)




# ✅✅✅-----------------------------CONVERSOR EXCEL A SCV------------------------------✅✅✅


@crud.route('/convertir_excel')
def convertir_excel():
    try:
        subprocess.Popen(['python', 'funciones.py'])  # Usa la ruta correcta aquí
        return redirect(url_for('crud.index'))

    except Exception as e:
        return f"Error al ejecutar el conversor: {e}"
    





""" ✅✅APRENDICES CANCELADOS ✅✅  """
@crud.route('/cancelados')
def cancelados():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener el término de búsqueda
    buscar = request.args.get('buscar', '').strip()
    
    if buscar:
        # Búsqueda por nombre, apellido o número de documento
        query = """
        SELECT numeroDocumento, ficha, nombres, apellidos, correo_electronico, estado 
        FROM aprendices 
        WHERE estado = 'cancelado' 
        AND (
            nombres LIKE %s 
            OR apellidos LIKE %s 
            OR numeroDocumento LIKE %s
            OR CONCAT(nombres, ' ', apellidos) LIKE %s
        )
        ORDER BY nombres, apellidos
        """
        # Preparar el término de búsqueda con comodines
        termino_busqueda = f"%{buscar}%"
        cursor.execute(query, (termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda))
    else:
        # Consulta normal sin filtros
        query = """
        SELECT numeroDocumento, ficha, nombres, apellidos, correo_electronico, estado 
        FROM aprendices 
        WHERE estado = 'cancelado'
        ORDER BY nombres, apellidos
        """
        cursor.execute(query)
    
    cancelados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template('aprendices_cancelados.html', cancelados=cancelados)


@crud.route('/actualizar_estado_aprendiz/<numeroDocumento>', methods=['POST'])
def actualizar_estado_aprendiz(numeroDocumento):
    try:
        nuevo_estado = request.form.get('nuevo_estado')
        
        # Validar que el nuevo estado sea válido (con F mayúscula)
        if nuevo_estado not in ['Formacion', 'cancelado']:
            flash('Estado no válido', 'error')
            return redirect(url_for('crud.cancelados'))
        
        # Conectar a la base de datos
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Actualizar el estado del aprendiz
        query = "UPDATE aprendices SET estado = %s WHERE numeroDocumento = %s"
        cursor.execute(query, (nuevo_estado, numeroDocumento))
        
        # Verificar si se actualizó algún registro
        if cursor.rowcount > 0:
            conexion.commit()
            if nuevo_estado == 'Formacion':
                flash(f'Estado del aprendiz actualizado correctamente a "Formación"', 'success')
            else:
                flash(f'Estado del aprendiz actualizado correctamente a "{nuevo_estado.title()}"', 'success')
        else:
            flash('No se encontró el aprendiz especificado', 'error')
        
        cursor.close()
        conexion.close()
        
    except Exception as e:
        flash(f'Error al actualizar el estado: {str(e)}', 'error')
    
    return redirect(url_for('crud.cancelados'))