# functions.py
from flask import session
from conexion import get_db_connection,mysql
from datetime import datetime
import smtplib
from email.message import EmailMessage
import ssl
import locale



#INCIO DE FUNCIONES DE SOLICITUD Y AGENDADOS 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
EMAIL_EMISOR = 'bcabcomitessena@gmail.com'
EMAIL_CONTRASENA = 'wjqusewsvylzfzci'

def enviar_correo(destinatarios,asunto,mensaje):
    try:
        em = EmailMessage()
        em['From'] = EMAIL_EMISOR
        em['To'] = ', '.join(destinatarios)
        em['Subject'] = asunto
        em.set_content(mensaje)
        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=contexto) as smtp:
            smtp.login(EMAIL_EMISOR, EMAIL_CONTRASENA)
            smtp.send_message(em)

        print("Correo enviado exitosamente a", destinatarios)

    except Exception as e:
        print("Error al enviar el correo:", e)
        

from datetime import datetime
import locale

def actualizar_estado_realizado():
    try:
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)

        # Obtener los comités agendados
        #cursor.execute("SELECT id_comite, fecha_agendacion FROM comite WHERE estado = 'agendado'")💚
        cursor.execute("SELECT id_comite, fechaAgendacion FROM comites WHERE estadoComite = 'agendado'")
        agendados = cursor.fetchall()

        for agendado in agendados:
            id_comite = agendado['id_comite']
            fecha_agendacion = agendado['fechaAgendacion']

            # Convertir la fecha de agendación al formato correcto
            locale.setlocale(locale.LC_TIME, 'es_ES')
            """ formato = '%Y-%m-%d %H:%M' """
            formato = '%Y-%m-%d %H:%M:%S'
            datetime_fecha = datetime.strptime(fecha_agendacion, formato)



            # Verificar si la fecha de agendación ha pasado
            if datetime_fecha <= datetime.now():
                # Actualizar el estado del comité a "realizado"
                #cursor.execute("UPDATE comite SET estado = 'realizado' WHERE id_comite = %s", (id_comite,))💚
                cursor.execute("UPDATE comites SET estadoComite = 'realizado' WHERE id_comite = %s", (id_comite,))
                mydb.commit()
                print(f"🔴🔴🔴🔴 acmbio a estado realizado perfecto")

        cursor.close()

    except Exception as e:
        print(f"Error al actualizar estado realizado: {str(e)}")
        # Manejo adicional de excepciones si es necesario
actualizar_estado_realizado()





def agendado(id_comite, fecha_formateada,lugar_enlace):
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        #cursor.execute("UPDATE comite SET fecha_agendacion = %s, estado = 'agendado' WHERE id_comite = %s", (fecha_formateada, id_comite))💚
        cursor.execute("UPDATE comites SET fechaAgendacion = %s, lugarComite = %s, estadoComite = 'agendado' WHERE id_comite = %s", (fecha_formateada, lugar_enlace, id_comite))

        conexion.commit()

        #cursor.execute("SELECT nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada, usuario_logueado FROM comite WHERE id_comite = %s", (id_comite,))💚
        cursor.execute("SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja FROM comites WHERE id_comite = %s", (id_comite,))

        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            competencia, resultadoAprendizaje,lugarComite,nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada  = resultado
            destinatarios = correos.split(", ")
            asunto = "Comité Agendado"
        fecha_original = fecha_formateada
        
        # Validar que la fecha no esté vacía o sea None
        if not fecha_original or fecha_original == '' or fecha_original is None:
            fecha_formateada = "Fecha no disponible"
        else:
            try:
                # Convertir la fecha a datetime
                if isinstance(fecha_original, str):
                    fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
                else:
                    fecha_dt = fecha_original  # Si ya es un objeto datetime
                
                # Formatear la fecha
                # Para español manual (si locale no funciona)
                dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                
                dia_semana = dias[fecha_dt.weekday()]
                dia = fecha_dt.day
                mes = meses[fecha_dt.month - 1]
                ano = fecha_dt.year
                
                # Formatear la hora en formato 12 horas 
                hora = fecha_dt.strftime('%I:%M')
                am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
                
                fecha_formateada = (f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}")
            
            except (ValueError, AttributeError) as e:
                print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
                fecha_formateada = "Fecha inválida"
        
            # Crear nueva tupla con la fecha formateada
            fila_con_fecha = fecha_formateada
            agendados_con_fecha_formateada = fila_con_fecha
            # Cuerpo del mensaje con formato HTML
            mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Comité Agendado</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">El comité <strong>{tipo_comite}</strong> con el número de ficha <strong>{id_ficha}</strong> ha sido <strong>AGENDADO</strong> para el <strong>{agendados_con_fecha_formateada}</strong>.</p>

            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">Detalles del Comité Agendado:</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="padding: 5px; font-size: 16px;"><strong>Nombre del Instructor:</strong> {nombre_instructor}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>INFO FALTA:</strong> {nombreCapituloFalla}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DESCRIPCIÓN:</strong> {descripcion}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DETALLE ART:</strong> {informacionArticulo}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CLASIFICACIÓN:</strong> {tipo_comite}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CALIFICACIÓN:</strong> {calificacionComite}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>COMPETENCIA:</strong> {competencia }</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>RESULTADO:</strong> {resultadoAprendizaje }</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FICHA:</strong> {id_ficha}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>PROGRAMA:</strong> {alias_ficha}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA QUEJA:</strong> {fecha_hora_formateada}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA/LUGAR AGENDACIÓN:</strong> {fechaAgendacion} - {lugarComite}</li>
                    <hr>
                    <p><strong>DATOS DE APRENDIZ</strong> :
                        <hr style=" border: none;">
                        -<strong>NOMBRE</strong> : {nombreAprendizCitado}<hr style=" border: none;"> 
                        -<strong>DOCUMENTO</strong> : {documentoAprendizCitado}<hr style=" border: none;">
                        -<strong>ESTADO</strong> : {estadoAprendizCitado}<hr style=" border: none;">
                        -<strong>CORREO</strong> : {correoAprendizCitado}<hr style=" border: none;">
                        -<strong>NUMERO</strong> : {telefonoAprendizCitado}</p>
                    <hr>

                    
                </ul>
            </div>

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.
            </p>
        </div>
    </body>
</html>
"""

            # Enviar el correo con formato HTML
            em = EmailMessage()
            em['From'] = 'bcabcomitessena@gmail.com'
            em['To'] = ', '.join(destinatarios)
            em['Subject'] = asunto
            em.set_content(mensaje, subtype='html')

            contexto = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
                smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
                smtp.send_message(em)

    except mysql.connector.Error as err:
        print(f"Error al agendar el comité: {err}")
        conexion.rollback()
        cursor.close()
        conexion.close()    



def reagendado(id_comite, fecha_formateada,lugar_enlace):
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Actualizar la fecha de agendación del comité
        #cursor.execute("UPDATE comite SET fecha_agendacion = %s, estado = 'agendado' WHERE id_comite = %s", (fecha_formateada, id_comite))💚
        cursor.execute("UPDATE comites SET fechaAgendacion = %s, lugarComite = %s, estadoComite = 'agendado' WHERE id_comite = %s", (fecha_formateada, lugar_enlace, id_comite))

        conexion.commit()

        # Consultar los detalles del comité
        #cursor.execute("SELECT nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos FROM comite WHERE id_comite = %s", (id_comite,))💚
        cursor.execute("SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja FROM comites WHERE id_comite = %s", (id_comite,))

        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            # Asignar los valores obtenidos
            competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada = resultado

            # Crear lista de destinatarios
            destinatarios = correos.split(", ")

            # Asunto del correo
            asunto = "Comité Reagendado"

            fecha_original = fecha_formateada
        
        # Validar que la fecha no esté vacía o sea None
        if not fecha_original or fecha_original == '' or fecha_original is None:
            fecha_formateada = "Fecha no disponible"
        else:
            try:
                # Convertir la fecha a datetime
                if isinstance(fecha_original, str):
                    fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
                else:
                    fecha_dt = fecha_original  # Si ya es un objeto datetime
                
                # Formatear la fecha
                # Para español manual (si locale no funciona)
                dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                
                dia_semana = dias[fecha_dt.weekday()]
                dia = fecha_dt.day
                mes = meses[fecha_dt.month - 1]
                ano = fecha_dt.year
                
                # Formatear la hora en formato 12 horas 
                hora = fecha_dt.strftime('%I:%M')
                am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
                
                fecha_formateada = (f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}")
            
            except (ValueError, AttributeError) as e:
                print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
                fecha_formateada = "Fecha inválida"
        
            # Crear nueva tupla con la fecha formateada
            fila_con_fecha = fecha_formateada
            agendados_con_fecha_formateada = fila_con_fecha

            # Cuerpo del correo con formato HTML
            mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Comité Reagendado</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">El comité <strong>{tipo_comite}</strong> con el número de ficha <strong>{id_ficha}</strong> ha sido <strong>REAGENDADO</strong> para el <strong>{agendados_con_fecha_formateada}</strong>.</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">Detalles del Comité Reagendado:</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="padding: 5px; font-size: 16px;"><strong>Nombre del Instructor:</strong> {nombre_instructor}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>INFO FALTA:</strong> {nombreCapituloFalla}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DESCRIPCIÓN:</strong> {descripcion}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DETALLE ART:</strong> {informacionArticulo}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CLASIFICACIÓN:</strong> {tipo_comite}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CALIFICACIÓN:</strong> {calificacionComite}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>COMPETENCIA:</strong> {competencia }</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>RESULTADO:</strong> {resultadoAprendizaje }</li>
                    <hr>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FICHA:</strong> {id_ficha}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>PROGRAMA:</strong> {alias_ficha}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA QUEJA:</strong> {fecha_hora_formateada}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA/LUGAR AGENDACIÓN:</strong> {fechaAgendacion} - {lugar_enlace}</li>
                    <hr>
                    <p><strong>DATOS DE APRENDIZ</strong> :
                        <hr style=" border: none;">
                        -<strong>NOMBRE</strong> : {nombreAprendizCitado}<hr style=" border: none;"> 
                        -<strong>DOCUMENTO</strong> : {documentoAprendizCitado}<hr style=" border: none;">
                        -<strong>ESTADO</strong> : {estadoAprendizCitado}<hr style=" border: none;">
                        -<strong>CORREO</strong> : {correoAprendizCitado}<hr style=" border: none;">
                        -<strong>NUMERO</strong> : {telefonoAprendizCitado}</p>
                    <hr>

                    
                </ul>
            </div>

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.
            </p>
        </div>
    </body>
</html>
"""

            # Enviar el correo con formato HTML
            em = EmailMessage()
            em['From'] = 'bcabcomitessena@gmail.com'
            em['To'] = ', '.join(destinatarios)
            em['Subject'] = asunto
            em.set_content(mensaje, subtype='html')

            contexto = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
                smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
                smtp.send_message(em)

    except mysql.connector.Error as err:
        print(f"Error al reagendar el comité: {err}")
        conexion.rollback()
        cursor.close()
        conexion.close()





def rechazar(id_comite): 
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # Actualizar el estado del comité a 'rechazado'
        #cursor.execute("UPDATE comite SET estado = 'rechazado' WHERE id_comite = %s", (id_comite,))💚
        cursor.execute("UPDATE comites SET estadoComite = 'rechazado' WHERE id_comite = %s", (id_comite,))

        conexion.commit()

        # Consultar los detalles del comité
        #cursor.execute("SELECT nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada FROM comite WHERE id_comite = %s", (id_comite,))💚
        cursor.execute("SELECT competencia, resultadoAprendizaje, nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja FROM comites WHERE id_comite = %s", (id_comite,))

        resultado = cursor.fetchone()  # Cambiar fetchall() a fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            # Asignar los valores directamente
            competencia, resultadoAprendizaje,nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada = resultado
            
            # Crear lista de destinatarios
            destinatarios = correos.split(", ")

            # Asunto del correo
            asunto = "Comité rechazado"

            # Cuerpo del correo con formato HTML
            mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #e74c3c;">Comité Rechazado</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">La queja ha sido <strong>rechazada</strong>.</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="color: #e74c3c; font-size: 18px; margin-bottom: 10px;">Detalles de la queja:</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="padding: 5px; font-size: 16px;"><strong>Nombre del Instructor:</strong> {nombre_instructor}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>INFO FALTA:</strong> {nombreCapituloFalla}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DESCRIPCIÓN:</strong> {descripcion}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DETALLE ART:</strong> {informacionArticulo}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CLASIFICACIÓN:</strong> {tipo_comite}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CALIFICACIÓN:</strong> {calificacionComite}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>COMPETENCIA:</strong> {competencia }</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>RESULTADO:</strong> {resultadoAprendizaje }</li>
                    <hr>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FICHA:</strong> {id_ficha}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>PROGRAMA:</strong> {alias_ficha}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA QUEJA:</strong> {fecha_hora_formateada}</li>
                    <hr>
                    <p><strong>DATOS DE APRENDIZ</strong> :
                        <hr style=" border: none;">
                        -<strong>NOMBRE</strong> : {nombreAprendizCitado}<hr style=" border: none;"> 
                        -<strong>DOCUMENTO</strong> : {documentoAprendizCitado}<hr style=" border: none;">
                        -<strong>ESTADO</strong> : {estadoAprendizCitado}<hr style=" border: none;">
                        -<strong>CORREO</strong> : {correoAprendizCitado}<hr style=" border: none;">
                        -<strong>NUMERO</strong> : {telefonoAprendizCitado}</p>
                    <hr>

                    
                </ul>
            </div>

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.
            </p>
        </div>
    </body>
</html>
"""
            # Enviar el correo con formato HTML
            em = EmailMessage()
            em['From'] = 'bcabcomitessena@gmail.com'
            em['To'] = ', '.join(destinatarios)
            em['Subject'] = asunto
            em.set_content(mensaje, subtype='html')

            contexto = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
                smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
                smtp.send_message(em)

    except mysql.connector.Error as err:
        print(f"Error al rechazar el comité: {err}")
        conexion.rollback()
        cursor.close()
        conexion.close()



def mostrar_solicitud():
    nombre_logueado = session['nombre']
    apellido_instructor = session['apellido']
    usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    # ESTA CONSULTA TRAE LOS SOLICITADOS SOLO DE LAS FICHAS PERTENECIENTES AL COORDINADOR LOGUEADO
    # ORDENADOS POR fechaPresentacionQueja para facilitar el agrupamiento
    sql = """
        SELECT c.*
        FROM comites c
        JOIN fichas f ON c.ficha = f.numeroFicha
        WHERE f.nombreCoordinador = %s
          AND c.estadoComite = 'solicitud'
        ORDER BY c.fechaPresentacionQueja
    """
    cursor.execute(sql, (usuario_logueado,))
    
    datos_solicitud = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    # Agrupar por fechaPresentacionQueja programa y ficha y si existen datos que son exantamente iguales con en esos tres parametros los agrupa  
    solicitudes_agrupadas = {}
    for solicitud in datos_solicitud:
        fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
        
        if fecha_queja not in solicitudes_agrupadas:
            solicitudes_agrupadas[fecha_queja] = []
        
        solicitudes_agrupadas[fecha_queja].append(solicitud)
    
    return solicitudes_agrupadas  # devuelve el diccionario agrupados





def mostrar_agendados():
    nombre_logueado = session['nombre']
    apellido_instructor = session['apellido']
    usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

    conexion = get_db_connection()
    cursor = conexion.cursor()
    #ESTA CONSULTA TRAE LOS AGENDOS SOLO DE LAS FICHAS PERTENECIENTES AL COORDINADROR LOGUEADO 
    sql = """
        SELECT c.*
        FROM comites c
        JOIN fichas f ON c.ficha = f.numeroFicha
        WHERE f.nombreCoordinador = %s
          AND c.estadoComite = 'agendado'
        ORDER BY c.fechaPresentacionQueja
    """
    cursor.execute(sql, (usuario_logueado,))

    datos_agendados = cursor.fetchall()

    cursor.close()
    conexion.close()

    # Agrupar por fechaPresentacionQueja programa y ficha y si existen datos que son exantamente iguales con en esos tres parametros los agrupa  
    agendados_agrupadas = {}
    for solicitud in datos_agendados:
        fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
        
        if fecha_queja not in agendados_agrupadas:
            agendados_agrupadas[fecha_queja] = []
        
        agendados_agrupadas[fecha_queja].append(solicitud)
    
    return agendados_agrupadas  # devuelve el diccionario agrupados

    """ print(f"aca usuario coordi {usuario_logueado}")
    print(f"estos son pripra {datos_agendados}")
    return datos_agendados
 """






def mostrar_realizados():
    nombre_logueado = session['nombre']
    apellido_instructor = session['apellido']
    usuario_logueado = f"{nombre_logueado} {apellido_instructor}"
    
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    # ESTA CONSULTA TRAE LOS REALIZADOS SOLO DE LAS FICHAS PERTENECIENTES AL COORDINADOR LOGUEADO
    sql = """
        SELECT c.*
        FROM comites c
        JOIN fichas f ON c.ficha = f.numeroFicha
        WHERE f.nombreCoordinador = %s
          AND c.estadoComite = 'realizado'
        ORDER BY c.fechaPresentacionQueja
    """
    cursor.execute(sql, (usuario_logueado,))
    datos_realizados = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    # Agrupar por fechaPresentacionQueja, programa y ficha (igual que en agendados)
    realizados_agrupados = {}
    for solicitud in datos_realizados:
        fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
        
        if fecha_queja not in realizados_agrupados:
            realizados_agrupados[fecha_queja] = []
        
        realizados_agrupados[fecha_queja].append(solicitud)
    
    print(f"Usuario coordinador: {usuario_logueado}")
    print(f"Realizados agrupados: {len(realizados_agrupados)} grupos")
    print(f"Tipo de dato devuelto: {type(realizados_agrupados)}")
    print(f"Datos realizados: {realizados_agrupados}")
    
    return realizados_agrupados  # devuelve el diccionario agrupado






def solicitarComite(nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada ):
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        #sql = """
        #INSERT INTO comite (nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada)💚
        #VALUES (%s, %s, %s, %s, %s, %s)
        #"""
        sql = """
        INSERT INTO comites (usuario_logueado, clasificacionComite, ficha, nombreFicha, correos, fechaAgendacion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (nombreCapituloFalla, descripcion, informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada )
        cursor.execute(sql, val)
        conexion.commit()

        destinatarios = correos.split(", ")  

        email_emisor = 'bcabcomitessena@gmail.com'
        email_contrasena = 'wjqusewsvylzfzci'
        asunto = 'Nueva Solicitud de Comité'
        cuerpo = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Nueva Solicitud de Comité</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">Se ha realizado una nueva <strong>QUEJA</strong>.</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">Detalles de la queja:</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="padding: 5px; font-size: 16px;"><strong>Nombre del Instructor:</strong> {nombre_instructor}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>INFO FALTA:</strong> {nombreCapituloFalla}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DESCRIPCIÓN:</strong> {descripcion}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>DETALLE ART:</strong> {informacionArticulo}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CLASIFICACIÓN:</strong> {tipo_comite}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>CALIFICACIÓN:</strong> {calificacionComite}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FICHA:</strong> {id_ficha}</li>
                    <li style="padding: 5px; font-size: 16px;"><strong>PROGRAMA:</strong> {alias_ficha}</li>
                    <hr>
                    <li style="padding: 5px; font-size: 16px;"><strong>FECHA QUEJA:</strong> {fecha_hora_formateada}</li>
                    <hr>
                    <p><strong>DATOS DE APRENDIZ</strong> :
                        <hr style=" border: none;">
                        -<strong>NOMBRE</strong> : {nombreAprendizCitado}<hr style=" border: none;"> 
                        -<strong>DOCUMENTO</strong> : {documentoAprendizCitado}<hr style=" border: none;">
                        -<strong>ESTADO</strong> : {estadoAprendizCitado}<hr style=" border: none;">
                        -<strong>CORREO</strong> : {correoAprendizCitado}<hr style=" border: none;">
                        -<strong>NUMERO</strong> : {telefonoAprendizCitado}</p>
                    <hr>

                    
                </ul>
            </div>

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.
            </p>
        </div>
    </body>
</html>
"""


        em = EmailMessage()
        em['From'] = email_emisor
        em['To'] = ', '.join(destinatarios) 
        em['Subject'] = asunto
        em.set_content(cuerpo, subtype='html')

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
            smtp.login(email_emisor, email_contrasena)
            smtp.send_message(em)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conexion.close()

#-------------FIN DE LAS FUNCIONES DE AGENDADOS -------------------------------------

def consulta_instructor_agendados():
 if 'logueado' in session and session['logueado']:
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        
        usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

        conexion = get_db_connection()
        cursor = conexion.cursor()
        sql = "SELECT c.* FROM comites c JOIN fichas f ON c.ficha = f.numeroFicha WHERE estadoComite = 'agendado' AND usuario_logueado = %s ORDER BY fechaAgendacion ASC"
        cursor.execute(sql, (usuario_logueado,))

        datos_agendados = cursor.fetchall()

        cursor.close()
        conexion.close()

        # Agrupar por fechaPresentacionQueja programa y ficha y si existen datos que son exantamente iguales con en esos tres parametros los agrupa  
        agendados_agrupadas = {}
        for solicitud in datos_agendados:
            fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
            
            if fecha_queja not in agendados_agrupadas:
                agendados_agrupadas[fecha_queja] = []
            
            agendados_agrupadas[fecha_queja].append(solicitud)
        
        return agendados_agrupadas 
 



def consulta_instructor_solicitado():
 if 'logueado' in session and session['logueado']:
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        
        usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

        conexion = get_db_connection()
        cursor = conexion.cursor() 
        sql = "SELECT c.* FROM comites c JOIN fichas f ON c.ficha = f.numeroFicha WHERE estadoComite = 'solicitud' AND usuario_logueado = %s ORDER BY fechaPresentacionQueja ASC"
        cursor.execute(sql, (usuario_logueado,))

        datos_solicitud = cursor.fetchall()
    
        cursor.close()
        conexion.close()
        
        # Agrupar por fechaPresentacionQueja programa y ficha y si existen datos que son exantamente iguales con en esos tres parametros los agrupa  
        solicitudes_agrupadas = {}
        for solicitud in datos_solicitud:
            fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
            
            if fecha_queja not in solicitudes_agrupadas:
                solicitudes_agrupadas[fecha_queja] = []
            
            solicitudes_agrupadas[fecha_queja].append(solicitud)
        
        return solicitudes_agrupadas
 



def obtener_fallas_por_comite(i_comite):
    conexion = get_db_connection()
    cursor = conexion.cursor()

    sql = """
    SELECT nombreCapituloFalla, articuloFalla, informacionArticulo 
    FROM comites 
    WHERE id_comite = %s
    """
    cursor.execute(sql, (i_comite,))
    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    if resultado:
        capitulos = resultado[0].split(" || ")
        articulos = resultado[1].split(" || ")
        informacion = resultado[2].split(" || ")

        fallas = []
        for i in range(4):
            capitulo = f"Capítulo {capitulos[i]} /" if i < len(capitulos) else ""
            articulo = f"Artículo: {articulos[i]} /" if i < len(articulos) else ""
            info = informacion[i] if i < len(informacion) else ""

            if capitulo or articulo or info:
                fallas.append({
                    "capitulo": capitulo.strip(),
                    "articulo": articulo.strip(),
                    "informacion": info.strip()
                })

        return fallas
    else:
        return []






def consulta_comites_solicitado():
 if 'logueado' in session and session['logueado']:
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        
        usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

        conexion = get_db_connection()
        cursor = conexion.cursor() 
        sql = "SELECT c.* FROM comites c JOIN fichas f ON c.ficha = f.numeroFicha WHERE estadoComite = 'solicitud' AND usuario_logueado = %s ORDER BY fechaPresentacionQueja ASC"
        cursor.execute(sql, (usuario_logueado,))

        datos_solicitud = cursor.fetchall()
    
        cursor.close()
        conexion.close()
        
        # Agrupar por fechaPresentacionQueja programa y ficha y si existen datos que son exantamente iguales con en esos tres parametros los agrupa  
        solicitudes_agrupadas = {}
        for solicitud in datos_solicitud:
            fecha_queja = f'{solicitud[3]} - {solicitud[2]} - Queja {solicitud[15]}'  
            
            if fecha_queja not in solicitudes_agrupadas:
                solicitudes_agrupadas[fecha_queja] = []
            
            solicitudes_agrupadas[fecha_queja].append(solicitud)
        
        return solicitudes_agrupadas


#---------------------------------------pdfs------------------------------------------
import os
import mysql.connector
from fpdf import FPDF
from werkzeug.utils import secure_filename
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.utf8')  # Configura el idioma a español





# Clase personalizada para el PDF
class PDF(FPDF):        

    def footer(self):
        self.set_y(-20)  
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, "Regional Valle / Centro Agropecuario de Buga", 0, 1, 'C')
        self.cell(0, 5, "Dirección Carretera Central Variante Buga  Tuluá - PBX 57 602 2376300", 0, 1, 'C')


    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf(datos, carpeta_destino, firma_imagen):
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    fecha_creacion = datetime.now().strftime("%B %d del %Y")

    conexion = get_db_connection()
    cursor = conexion.cursor()
    sql = "SELECT nombreCapituloFalla, articuloFalla, informacionArticulo FROM comites"
    cursor.execute(sql)

    # Acceder al último registro
    datosCapturados = cursor.fetchall()
    ultimo_fila = datosCapturados[-1]
    capitulos = ultimo_fila[0]
    articulos = ultimo_fila[1]
    informacionArticulos = ultimo_fila[2]


    lista_capitulos = capitulos.split(" || ")
    lista_articulos = articulos.split(" || ")
    lista_informacion = informacionArticulos.split(" || ")


    # Asignar capitulos a variables individuales si existen, esto se hace en caso de recibir alguna variable vacia, que no nos tire error
    primerCapituloFalla = (f"{lista_capitulos[0]} /") if len(lista_capitulos) > 0 else ""
    segundoCapituloFalla = (f"{lista_capitulos[1]} /") if len(lista_capitulos) > 1 else ""
    tercerCapituloFalla = (f"{lista_capitulos[2]} /") if len(lista_capitulos) > 2 else ""
    cuartoCapituloFalla = (f"{lista_capitulos[3]} /") if len(lista_capitulos) > 3 else ""
    # Asignar artículos a variables individuales si existen, esto se hace en caso de recibir alguna variable vacia, que no nos tire error
    primerArticuloFalla = (f"Artículo: {lista_articulos[0]} /") if len(lista_articulos) > 0 else ""
    segundoArticuloFalla = (f"Artículo: {lista_articulos[1]} /") if len(lista_articulos) > 1 else ""
    tercerArticuloFalla = (f"Artículo: {lista_articulos[2]} /") if len(lista_articulos) > 2 else ""
    cuartoArticuloFalla = (f"Artículo: {lista_articulos[3]} /") if len(lista_articulos) > 3 else ""
    # Asignar informaciones a variables individuales si existen, esto se hace en caso de recibir alguna variable vacia, que no nos tire error
    primerInformacionArticuloFalla = lista_informacion[0] if len(lista_informacion) > 0 else ""
    segundoInformacionArticuloFalla = lista_informacion[1] if len(lista_informacion) > 1 else ""
    tercerInformacionArticuloFalla = lista_informacion[2] if len(lista_informacion) > 2 else ""
    cuartoInformacionArticuloFalla = lista_informacion[3] if len(lista_informacion) > 3 else ""




        


 
    for dato in datos:# fila[2] contiene fechaAgendacion según tu consulta SQL
        fecha_original = dato[16]
        
        # Validar que la fecha no esté vacía o sea None
        if not fecha_original or fecha_original == '' or fecha_original is None:
            fecha_formateada = "Fecha no disponible"
        else:
            try:
                # Convertir la fecha a datetime
                if isinstance(fecha_original, str):
                    fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
                else:
                    fecha_dt = fecha_original  # Si ya es un objeto datetime
                
                # Formatear la fecha
                # Para español manual (si locale no funciona)
                dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                
                dia_semana = dias[fecha_dt.weekday()]
                dia = fecha_dt.day
                mes = meses[fecha_dt.month - 1]
                ano = fecha_dt.year
                
                # Formatear la hora en formato 12 horas 
                hora = fecha_dt.strftime('%I:%M')
                am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
                
                fecha_formateada = (f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}")
            
            except (ValueError, AttributeError) as e:
                print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
                fecha_formateada = "Fecha inválida"
        
        # Crear nueva tupla con la fecha formateada
        fila_con_fecha = fecha_formateada
        agendados_con_fecha_formateada = fila_con_fecha

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', '', 10)

        # Encabezado
        ruta_imagen = r"static/img/logoSena.png"
        pdf.image(ruta_imagen, x=95, y=6, w=25)
        pdf.ln(12)
        # Fecha y lugar con fecha automática
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(30, 35)
        pdf.cell(0, 5, f".76-9124-4", 0, 1, 'C')
        pdf.cell(0, 5, f"Guadalajara de Buga, {fecha_creacion}", 0, 1, 'R')
        pdf.ln(6)

        # Datos del aprendiz
        pdf.set_xy(10, 45)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "APRECIADO APRENDIZ:", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"{dato[6]}", 0, 1)
        pdf.cell(0, 5, f"C.C. {dato[5]}", 0, 1)
        pdf.cell(0, 5, f"{dato[8]}", 0, 1)
        pdf.cell(0, 5, f"{dato[9]}", 0, 1)
        pdf.cell(0, 5, f"Ficha: {dato[2]}", 0, 1)
        pdf.cell(0, 5, f"{dato[3]}", 0, 1)
        pdf.cell(0, 5, "Centro Agropecuario de Buga.", 0, 1)
        pdf.ln(8)

        # Asunto
        pdf.set_xy(10, 80)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 5, "Asunto:                                                          ", 0, 1,'R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, "Citación comité de evaluación y seguimiento.", 0, 1,'R')
        
        pdf.ln(4)
        
        pdf.set_xy(10, 100)
        pdf.multi_cell(0, 5, "Cordial Saludo Aprendiz e Instructores,\n\n"
                        "En pro del seguimiento y evaluación de la ejecución de la formación profesional integral y "
                        "al cumplimiento de los lineamientos establecidos por la entidad para un adecuado desarrollo "
                        f"de nuestros procesos, se convoca para el {agendados_con_fecha_formateada}, a comité de evaluación y "
                        "seguimiento, el cual se realizará de manera PRESENCIAL.")
        pdf.ln(6)

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 5, "Lugar o enlace:", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"{dato[21]}", 0, 1)
        pdf.ln(6)

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 5, "Fecha/hora:", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"{agendados_con_fecha_formateada}", 0, 1)
        pdf.ln(6)

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 5, "Presuntas faltas cometidas según reglamento del aprendiz:", 0, 1)
        pdf.set_font('Arial', '', 10)

        """ # Dividir los campos múltiples por coma
        capitulos = [c.strip() for c in dato[13].split(' || ')]
        articulos = [a.strip() for a in dato[19].split(' || ')]
        infos = [i.strip() for i in dato[22].split(' || ')]

        # Combinar y mostrar en el formato correcto
        for cap, art, info in zip(capitulos, articulos, infos):
            pdf.multi_cell(0, 5, f"{cap} / Articulo {art} / {info}", 0, 1)

        pdf.ln(6)  """

      

        pdf.multi_cell(0, 5, f"{primerCapituloFalla} {primerArticuloFalla} {primerInformacionArticuloFalla}", 0, 1)
        pdf.multi_cell(0, 5, f"{segundoCapituloFalla} {segundoArticuloFalla} {segundoInformacionArticuloFalla}", 0, 1)
        pdf.multi_cell(0, 5, f"{tercerCapituloFalla} {tercerArticuloFalla} {tercerInformacionArticuloFalla}", 0, 1)
        pdf.multi_cell(0, 5, f"{cuartoCapituloFalla} {cuartoArticuloFalla} {cuartoInformacionArticuloFalla}", 0, 1)


        pdf.ln(6)

        pdf.set_font('Arial', 'B', 11)
        pdf.multi_cell(0, 5, "Se solicita presentación de descargos ante el Comité de Evaluación y Seguimiento," \
        "en forma escrita o verbal.", 0, 1)

        pdf.ln(2)
        pdf.cell(0, 5, "POR FAVOR PUNTUAL ASISTENCIA.", 0, 1)
        pdf.ln(4)


        
        
        


        pdf.cell(0, 10, "Firma:", 0, 1)
        if firma_imagen and os.path.exists(firma_imagen):
            pdf.image(firma_imagen, x=20, y=pdf.get_y() + 3, w=38)
        pdf.line(10, pdf.get_y() + 20, 100, pdf.get_y() + 20)
        
        pdf.set_y(-34)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(52, 168, 83) 
        pdf.cell(0, 5, "Regional Valle / Centro Agropecuario de Buga", 0, 1, 'C')
        pdf.cell(0, 5, "Dirección Carretera Central Variante Buga  Tuluá - PBX 57 602 2376300", 0, 1, 'C')
        ruta_imagen2 = r"static/img/senaimgredes .png"
        pdf.image(ruta_imagen2, x=90, w=20)
       
        pdf.set_font("Arial",'B', size=10)
        pdf.rotate(90, x=200, y=50)
        pdf.set_text_color(200, 200, 200)
        pdf.text(-30, 50, "GD-F-011-V.010")
        pdf.rotate(0)
        pdf.ln(1)
        
        
        archivo_pdf = os.path.join(carpeta_destino, f'Citacion_comite_{dato[6]}_{dato[5]}_{dato[0]}.pdf')
        pdf.output(archivo_pdf)


def obtener_datos():
    nombre_logueado = session['nombre']
    apellido_instructor = session['apellido']
    usuario_logueado = f"{nombre_logueado} {apellido_instructor}"

    conexion = get_db_connection()
    cursor = conexion.cursor()

    sql = """
        SELECT c.*
        FROM comites c
        JOIN fichas f ON c.ficha = f.numeroFicha
        WHERE f.nombreCoordinador = %s
          AND c.estadoComite = 'agendado'
    """
    cursor.execute(sql, (usuario_logueado,))
    datos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return datos


    

    
# ✅✅✅-----------------------------CONVERSOR EXCEL A SCV------------------------------✅✅✅

import os
import pandas as pd
import csv
from tkinter import Tk, Label, Button, filedialog, messagebox
from datetime import datetime

def seleccionar_carpeta_entrada():
    carpeta = filedialog.askdirectory()
    if carpeta:
        entrada_label.config(text=carpeta)

def seleccionar_carpeta_salida():
    carpeta = filedialog.askdirectory()
    if carpeta:
        salida_label.config(text=carpeta)

def convertir_archivos():
    input_folder = entrada_label.cget("text")
    output_folder = salida_label.cget("text")

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Selecciona ambas carpetas")
        return

    os.makedirs(output_folder, exist_ok=True)
    convertidos = 0

    for filename in os.listdir(input_folder):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            filepath = os.path.join(input_folder, filename)
            try:
                df = pd.read_excel(filepath)

                # Convertir columnas de tipo fecha/hora
                for col in df.columns:
                    if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                        try:
                            df[col] = pd.to_datetime(df[col], dayfirst=True)
                        except:
                            pass

                output_path = os.path.join(output_folder, filename.rsplit('.', 1)[0] + '.csv')

                # Guardar CSV con comas y textos entre comillas
                df.to_csv(output_path,
                          index=False,
                          date_format='%Y-%m-%d %H:%M:%S',
                          quoting=csv.QUOTE_ALL,
                          sep=',')

                convertidos += 1
            except Exception as e:
                print(f"Error con {filename}: {e}")

    messagebox.showinfo("Proceso completado", f"Se convirtieron {convertidos} archivos.")

# Interfaz gráfica
app = Tk()
app.title("Convertidor de Excel a CSV (SQL-ready)")
app.geometry("500x250")

Label(app, text="Carpeta de entrada (Excel):").pack(pady=5)
entrada_label = Label(app, text="", bg="white", relief="sunken", width=60, anchor='w')
entrada_label.pack(pady=5)
Button(app, text="Seleccionar carpeta", command=seleccionar_carpeta_entrada).pack()

Label(app, text="Carpeta de salida (CSV):").pack(pady=10)
salida_label = Label(app, text="", bg="white", relief="sunken", width=60, anchor='w')
salida_label.pack(pady=5)
Button(app, text="Seleccionar carpeta", command=seleccionar_carpeta_salida).pack()

Button(app, text="Convertir archivos", command=convertir_archivos, bg="green", fg="white").pack(pady=20)








def agendado_lote(comite_ids, fecha_formateada, lugar_enlace):
    """
    Agenda múltiples comités con la misma fecha y lugar
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    try:
        # Lista para almacenar los datos de todos los comités agendados
        comites_agendados = []
        
        # Actualizar cada comité en el lote
        for id_comite in comite_ids:
            # Actualizar el estado del comité
            cursor.execute(
                "UPDATE comites SET fechaAgendacion = %s, lugarComite = %s, estadoComite = 'agendado' WHERE id_comite = %s", 
                (fecha_formateada, lugar_enlace, id_comite)
            )
            
            # Obtener los datos del comité actualizado para el correo
            cursor.execute("""
                SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
                       informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
                       documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
                       usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja 
                FROM comites WHERE id_comite = %s
            """, (id_comite,))
            
            resultado = cursor.fetchone()
            if resultado:
                comites_agendados.append(resultado)
        
        conexion.commit()
        
        # Enviar correo con todos los comités del lote
        if comites_agendados:
            enviar_correo_lote_agendado(comites_agendados, fecha_formateada, lugar_enlace)
            
        print(f"Se agendaron {len(comite_ids)} comités exitosamente")
        
    except mysql.connector.Error as err:
        print(f"Error al agendar el lote de comités: {err}")
        conexion.rollback()
        raise err
    finally:
        cursor.close()
        conexion.close()

def enviar_correo_lote_agendado(comites_agendados, fecha_formateada, lugar_enlace):
    """
    Envía un correo con todos los comités agendados en el lote
    """
    if not comites_agendados:
        return
    
    # Formatear la fecha para mostrar
    fecha_original = fecha_formateada
    
    # Validar que la fecha no esté vacía o sea None
    if not fecha_original or fecha_original == '' or fecha_original is None:
        fecha_formateada_display = "Fecha no disponible"
    else:
        try:
            # Convertir la fecha a datetime
            if isinstance(fecha_original, str):
                fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
            else:
                fecha_dt = fecha_original  # Si ya es un objeto datetime
            
            # Formatear la fecha
            dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            dia_semana = dias[fecha_dt.weekday()]
            dia = fecha_dt.day
            mes = meses[fecha_dt.month - 1]
            ano = fecha_dt.year
            
            # Formatear la hora en formato 12 horas 
            hora = fecha_dt.strftime('%I:%M')
            am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
            
            fecha_formateada_display = f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}"
        
        except (ValueError, AttributeError) as e:
            print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
            fecha_formateada_display = "Fecha inválida"
    
    # Obtener todos los correos únicos del lote
    todos_correos = set()
    for comite in comites_agendados:
        correos = comite[17]  # índice de correos
        if correos:
            todos_correos.update(correos.split(", "))
    
    destinatarios = list(todos_correos)
    
    # Crear el contenido HTML del correo
    comites_html = ""
    for i, comite in enumerate(comites_agendados, 1):
        (competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
         informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
         documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
         nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada) = comite
        
        comites_html += f"""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
            <h4 style="color: #4CAF50; margin-top: 0;">Comité #{i}</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="padding: 3px; font-size: 14px;"><strong>Instructor:</strong> {nombre_instructor}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Ficha:</strong> {id_ficha} - {alias_ficha}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Aprendiz:</strong> {nombreAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Documento:</strong> {documentoAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Falta:</strong> {nombreCapituloFalla}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Clasificación:</strong> {tipo_comite}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Calificación:</strong> {calificacionComite}</li>
            </ul>
        </div>
        """
    
    asunto = f"Lote de Comités Agendados - {len(comites_agendados)} comités"
    
    mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Lote de Comités Agendados</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">Se han <strong>AGENDADO {len(comites_agendados)} comités</strong> para el <strong>{fecha_formateada_display}</strong> en <strong>{lugar_enlace}</strong>.</p>

            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #4CAF50; margin-top: 0;">📅 Información General del Lote</h3>
                <p style="margin: 5px 0;"><strong>Fecha y Hora:</strong> {fecha_formateada_display}</p>
                <p style="margin: 5px 0;"><strong>Lugar/Enlace:</strong> {lugar_enlace}</p>
                <p style="margin: 5px 0;"><strong>Cantidad de Comités:</strong> {len(comites_agendados)}</p>
            </div>

            <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">📋 Detalles de los Comités:</h3>
            {comites_html}

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                <strong>ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.</strong>
            </p>
        </div>
    </body>
</html>
"""

    try:
        # Enviar el correo con formato HTML
        em = EmailMessage()
        em['From'] = 'bcabcomitessena@gmail.com'
        em['To'] = ', '.join(destinatarios)
        em['Subject'] = asunto
        em.set_content(mensaje, subtype='html')

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
            smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
            smtp.send_message(em)
            
        print(f"Correo de lote enviado exitosamente a {len(destinatarios)} destinatarios")
        
    except Exception as e:
        print(f"Error al enviar correo del lote: {e}")

def rechazar_lote(comite_ids):
    """
    Rechaza múltiples comités a la vez y envía correo de notificación
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    try:
        # Lista para almacenar los datos de todos los comités rechazados
        comites_rechazados = []
        
        # Actualizar cada comité en el lote
        for id_comite in comite_ids:
            # Actualizar el estado del comité
            cursor.execute(
                "UPDATE comites SET estadoComite = 'rechazado' WHERE id_comite = %s",
                (id_comite,)
            )
            
            # Obtener los datos del comité actualizado para el correo
            cursor.execute("""
                SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
                       informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
                       documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
                       usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja 
                FROM comites WHERE id_comite = %s
            """, (id_comite,))
            
            resultado = cursor.fetchone()
            if resultado:
                comites_rechazados.append(resultado)
        
        conexion.commit()
        
        # Enviar correo con todos los comités rechazados del lote
        if comites_rechazados:
            enviar_correo_lote_rechazado(comites_rechazados)
            
        print(f"Se rechazaron {len(comite_ids)} comités exitosamente")
        
    except mysql.connector.Error as err:
        print(f"Error al rechazar el lote de comités: {err}")
        conexion.rollback()
        raise err
    finally:
        cursor.close()
        conexion.close()

def enviar_correo_lote_rechazado(comites_rechazados):
    """
    Envía un correo con todos los comités rechazados en el lote
    """
    if not comites_rechazados:
        return
    
    # Obtener todos los correos únicos del lote
    todos_correos = set()
    for comite in comites_rechazados:
        correos = comite[17]  # índice de correos
        if correos:
            todos_correos.update(correos.split(", "))
    
    destinatarios = list(todos_correos)
    
    # Crear el contenido HTML del correo
    comites_html = ""
    for i, comite in enumerate(comites_rechazados, 1):
        (competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
         informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
         documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
         nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada) = comite
        
        comites_html += f"""
        <div style="background-color: #fef9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #f44336;">
            <h4 style="color: #f44336; margin-top: 0;">Comité #{i}</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="padding: 3px; font-size: 14px;"><strong>Instructor:</strong> {nombre_instructor}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Ficha:</strong> {id_ficha} - {alias_ficha}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Aprendiz:</strong> {nombreAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Documento:</strong> {documentoAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Falta:</strong> {nombreCapituloFalla}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Clasificación:</strong> {tipo_comite}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Calificación:</strong> {calificacionComite}</li>
            </ul>
        </div>
        """
    
    asunto = f"Lote de Comités Rechazados - {len(comites_rechazados)} comités"
    
    mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #f44336;">Lote de Comités Rechazados</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">Se han <strong>RECHAZADO {len(comites_rechazados)} comités</strong>. Por favor, revise los detalles.</p>

            <div style="background-color: #ffebee; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f44336;">
                <h3 style="color: #f44336; margin-top: 0;">❌ Información del Lote Rechazado</h3>
                <p style="margin: 5px 0;"><strong>Estado:</strong> RECHAZADO</p>
                <p style="margin: 5px 0;"><strong>Cantidad de Comités:</strong> {len(comites_rechazados)}</p>
                <p style="margin: 5px 0;"><strong>Fecha de Rechazo:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>

            <h3 style="color: #f44336; font-size: 18px; margin-bottom: 10px;">📋 Detalles de los Comités Rechazados:</h3>
            {comites_html}

            

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                <strong>ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.</strong>
            </p>
        </div>
    </body>
</html>
"""

    try:
        # Enviar el correo con formato HTML
        em = EmailMessage()
        em['From'] = 'bcabcomitessena@gmail.com'
        em['To'] = ', '.join(destinatarios)
        em['Subject'] = asunto
        em.set_content(mensaje, subtype='html')

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
            smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
            smtp.send_message(em)
            
        print(f"Correo de lote rechazado enviado exitosamente a {len(destinatarios)} destinatarios")
        
    except Exception as e:
        print(f"Error al enviar correo del lote rechazado: {e}")






""" ----------------------------------------------------------------------------------------------------- """

def reagendado_lote_multiple_mejorado(comite_ids, fecha_formateada, lugar_enlace):
    """
    Reagenda múltiples comités de diferentes lotes con la misma fecha y lugar
    Versión mejorada que maneja mejor los errores y la transacción
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    try:
        # Lista para almacenar los datos de todos los comités reagendados
        comites_reagendados = []
        comites_fallidos = []
        
        # Iniciar transacción
        conexion.start_transaction()
        
        # Actualizar cada comité individualmente
        for id_comite in comite_ids:
            try:
                # Verificar que el comité existe y está en estado 'agendado'
                cursor.execute(
                    "SELECT estadoComite FROM comites WHERE id_comite = %s", 
                    (id_comite,)
                )
                resultado_estado = cursor.fetchone()
                
                if not resultado_estado:
                    print(f"Comité {id_comite} no encontrado")
                    comites_fallidos.append(id_comite)
                    continue
                
                # Actualizar el estado del comité
                cursor.execute(
                    """UPDATE comites 
                       SET fechaAgendacion = %s, lugarComite = %s, estadoComite = 'agendado' 
                       WHERE id_comite = %s""", 
                    (fecha_formateada, lugar_enlace, id_comite)
                )
                
                # Verificar que la actualización fue exitosa
                if cursor.rowcount == 0:
                    print(f"No se pudo actualizar el comité {id_comite}")
                    comites_fallidos.append(id_comite)
                    continue
                
                # Obtener los datos del comité actualizado para el correo
                cursor.execute("""
                    SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
                           informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
                           documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
                           usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja,
                           id_comite
                    FROM comites WHERE id_comite = %s
                """, (id_comite,))
                
                resultado = cursor.fetchone()
                if resultado:
                    comites_reagendados.append(resultado)
                else:
                    comites_fallidos.append(id_comite)
                    
            except Exception as e:
                print(f"Error al reagendar comité {id_comite}: {e}")
                comites_fallidos.append(id_comite)
        
        # Si hay comités reagendados exitosamente, confirmar la transacción
        if comites_reagendados:
            conexion.commit()
            
            # Enviar correo con todos los comités reagendados
            enviar_correo_lote_multiple_reagendado(comites_reagendados, fecha_formateada, lugar_enlace)
            
            print(f"Se reagendaron {len(comites_reagendados)} comités exitosamente")
            
            if comites_fallidos:
                print(f"No se pudieron reagendar {len(comites_fallidos)} comités: {comites_fallidos}")
        else:
            # Si no hay comités reagendados, hacer rollback
            conexion.rollback()
            print("No se reagendó ningún comité")
            
        return {
            'exito': len(comites_reagendados),
            'fallidos': len(comites_fallidos),
            'ids_fallidos': comites_fallidos
        }
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos al reagendar lotes múltiples: {err}")
        conexion.rollback()
        raise err
    except Exception as e:
        print(f"Error general al reagendar lotes múltiples: {e}")
        conexion.rollback()
        raise e
    finally:
        cursor.close()
        conexion.close()


def enviar_correo_lote_multiple_reagendado(comites_reagendados, fecha_formateada, lugar_enlace):
    """
    Envía un correo con todos los comités reagendados de múltiples lotes
    """
    if not comites_reagendados:
        return
    
    # Formatear la fecha para mostrar
    fecha_formateada_display = formatear_fecha_para_mostrar(fecha_formateada)
    
    # Obtener todos los correos únicos
    todos_correos = set()
    for comite in comites_reagendados:
        correos = comite[17]  # índice de correos
        if correos:
            todos_correos.update(correos.split(", "))
    
    destinatarios = list(todos_correos)
    
    # Agrupar comités por instructor/ficha para mejor organización
    comites_por_instructor = {}
    for comite in comites_reagendados:
        instructor = comite[13]  # usuario_logueado (instructor)
        ficha = f"{comite[15]} - {comite[16]}"  # ficha y nombreFicha
        
        key = f"{instructor} - {ficha}"
        if key not in comites_por_instructor:
            comites_por_instructor[key] = []
        comites_por_instructor[key].append(comite)
    
    # Crear el contenido HTML del correo
    comites_html = ""
    contador_comite = 1
    
    for grupo_key, comites_grupo in comites_por_instructor.items():
        comites_html += f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
            <h4 style="color: #2196F3; margin-top: 0;">📚 {grupo_key}</h4>
        """
        
        for comite in comites_grupo:
            (competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
             informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
             documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
             nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada, id_comite) = comite
            
            comites_html += f"""
            <div style="background-color: #ffffff; padding: 12px; border-radius: 6px; margin: 10px 0; border: 1px solid #e0e0e0;">
                <h5 style="color: #4CAF50; margin-top: 0;">Comité #{contador_comite}</h5>
                <ul style="list-style-type: none; padding-left: 0; margin: 0;">
                    <li style="padding: 2px; font-size: 14px;"><strong>Aprendiz:</strong> {nombreAprendizCitado}</li>
                    <li style="padding: 2px; font-size: 14px;"><strong>Documento:</strong> {documentoAprendizCitado}</li>
                    <li style="padding: 2px; font-size: 14px;"><strong>Falta:</strong> {nombreCapituloFalla}</li>
                    <li style="padding: 2px; font-size: 14px;"><strong>Clasificación:</strong> {tipo_comite}</li>
                    <li style="padding: 2px; font-size: 14px;"><strong>Calificación:</strong> {calificacionComite}</li>
                </ul>
            </div>
            """
            contador_comite += 1
        
        comites_html += "</div>"
    
    asunto = f"Reagendación Múltiple de Lotes - {len(comites_reagendados)} comités"
    
    mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 1000px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #2196F3; margin-bottom: 20px;">🔄 Reagendación Múltiple de Lotes</h2>
            
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196F3;">
                <h3 style="color: #2196F3; margin-top: 0;">📅 Información General</h3>
                <p style="margin: 8px 0; font-size: 16px;"><strong>Nueva Fecha y Hora:</strong> {fecha_formateada_display}</p>
                <p style="margin: 8px 0; font-size: 16px;"><strong>Nuevo Lugar/Enlace:</strong> {lugar_enlace}</p>
                <p style="margin: 8px 0; font-size: 16px;"><strong>Total de Comités Reagendados:</strong> {len(comites_reagendados)}</p>
                <p style="margin: 8px 0; font-size: 16px;"><strong>Instructores/Fichas Afectados:</strong> {len(comites_por_instructor)}</p>
            </div>

            <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800;">
                <h4 style="color: #ff9800; margin-top: 0;">⚠️ Importante</h4>
                <p style="margin: 5px 0;">Esta es una <strong>REAGENDACIÓN MÚLTIPLE</strong> que afecta a varios lotes de comités.</p>
                <p style="margin: 5px 0;">Todos los comités listados han sido reagendados para la misma fecha y lugar.</p>
            </div>

            <h3 style="color: #2196F3; font-size: 18px; margin-bottom: 15px;">📋 Comités Reagendados por:{comites_html}</h3>
            

            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 30px; text-align: center;">
                <p style="margin: 5px 0; font-size: 14px; color: #666;">
                    <strong>ESTA ES SOLO UNA NOTIFICACIÓN AUTOMÁTICA</strong><br>
                    No responda a este correo. Para consultas, contacte directamente con la coordinación.
                </p>
            </div>
        </div>
    </body>
</html>
"""

    try:
        # Enviar el correo con formato HTML
        em = EmailMessage()
        em['From'] = 'bcabcomitessena@gmail.com'
        em['To'] = ', '.join(destinatarios)
        em['Subject'] = asunto
        em.set_content(mensaje, subtype='html')

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
            smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
            smtp.send_message(em)
            
        print(f"Correo de reagendación múltiple enviado exitosamente a {len(destinatarios)} destinatarios")
        
    except Exception as e:
        print(f"Error al enviar correo de reagendación múltiple: {e}")


def formatear_fecha_para_mostrar(fecha_original):
    """
    Formatea una fecha para mostrar en español
    """
    if not fecha_original or fecha_original == '' or fecha_original is None:
        return "Fecha no disponible"
    
    try:
        # Convertir la fecha a datetime si es necesario
        if isinstance(fecha_original, str):
            fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
        else:
            fecha_dt = fecha_original
        
        # Formatear la fecha
        dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        
        dia_semana = dias[fecha_dt.weekday()]
        dia = fecha_dt.day
        mes = meses[fecha_dt.month - 1]
        ano = fecha_dt.year
        
        # Formatear la hora en formato 12 horas
        hora = fecha_dt.strftime('%I:%M')
        am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
        
        return f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}"
    
    except (ValueError, AttributeError) as e:
        print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
        return "Fecha inválida"







def F_reagendado_lote(comite_ids, fecha_formateada, lugar_enlace):
    """
    reagenda múltiples comités con la misma fecha y lugar
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    try:
        # Lista para almacenar los datos de todos los comités agendados
        comites_reagendados = []
        
        # Actualizar cada comité en el lote
        for id_comite in comite_ids:
            # Actualizar el estado del comité
            cursor.execute(
                "UPDATE comites SET fechaAgendacion = %s, lugarComite = %s, estadoComite = 'agendado' WHERE id_comite = %s", 
                (fecha_formateada, lugar_enlace, id_comite)
            )
            
            # Obtener los datos del comité actualizado para el correo
            cursor.execute("""
                SELECT competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
                       informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
                       documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
                       usuario_logueado, ClasificacionComite, ficha, nombreFicha, correos, fechaPresentacionQueja 
                FROM comites WHERE id_comite = %s
            """, (id_comite,))
            
            resultado = cursor.fetchone()
            if resultado:
                comites_reagendados.append(resultado)
        
        conexion.commit()
        
        # Enviar correo con todos los comités del lote
        if comites_reagendados:
            enviar_correo_lote_reagendado(comites_reagendados, fecha_formateada, lugar_enlace)
            
        print(f"Se agendaron {len(comite_ids)} comités exitosamente")
        
    except mysql.connector.Error as err:
        print(f"Error al agendar el lote de comités: {err}")
        conexion.rollback()
        raise err
    finally:
        cursor.close()
        conexion.close()




def enviar_correo_lote_reagendado(comites_reagendados, fecha_formateada, lugar_enlace):
    """
    Envía un correo con todos los comités agendados en el lote
    """
    if not comites_reagendados:
        return
    
    # Formatear la fecha para mostrar
    fecha_original = fecha_formateada
    
    # Validar que la fecha no esté vacía o sea None
    if not fecha_original or fecha_original == '' or fecha_original is None:
        fecha_formateada_display = "Fecha no disponible"
    else:
        try:
            # Convertir la fecha a datetime
            if isinstance(fecha_original, str):
                fecha_dt = datetime.strptime(fecha_original, '%Y-%m-%d %H:%M:%S')
            else:
                fecha_dt = fecha_original  # Si ya es un objeto datetime
            
            # Formatear la fecha
            dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            
            dia_semana = dias[fecha_dt.weekday()]
            dia = fecha_dt.day
            mes = meses[fecha_dt.month - 1]
            ano = fecha_dt.year
            
            # Formatear la hora en formato 12 horas 
            hora = fecha_dt.strftime('%I:%M')
            am_pm = 'am' if fecha_dt.hour < 12 else 'pm'
            
            fecha_formateada_display = f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}"
        
        except (ValueError, AttributeError) as e:
            print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
            fecha_formateada_display = "Fecha inválida"
    
    # Obtener todos los correos únicos del lote
    todos_correos = set()
    for comite in comites_reagendados:
        correos = comite[17]  # índice de correos
        if correos:
            todos_correos.update(correos.split(", "))
    
    destinatarios = list(todos_correos)
    
    # Crear el contenido HTML del correo
    comites_html = ""
    for i, comite in enumerate(comites_reagendados, 1):
        (competencia, resultadoAprendizaje, lugarComite, nombreCapituloFalla, descripcion, 
         informacionArticulo, calificacionComite, fechaAgendacion, nombreAprendizCitado, 
         documentoAprendizCitado, estadoAprendizCitado, correoAprendizCitado, telefonoAprendizCitado, 
         nombre_instructor, tipo_comite, id_ficha, alias_ficha, correos, fecha_hora_formateada) = comite
        
        comites_html += f"""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
            <h4 style="color: #4CAF50; margin-top: 0;">Comité #{i}</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="padding: 3px; font-size: 14px;"><strong>Instructor:</strong> {nombre_instructor}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Ficha:</strong> {id_ficha} - {alias_ficha}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Aprendiz:</strong> {nombreAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Documento:</strong> {documentoAprendizCitado}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Falta:</strong> {nombreCapituloFalla}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Clasificación:</strong> {tipo_comite}</li>
                <li style="padding: 3px; font-size: 14px;"><strong>Calificación:</strong> {calificacionComite}</li>
            </ul>
        </div>
        """
    
    asunto = f"Lote de Comités Reagendados - {len(comites_reagendados)} comités"
    
    mensaje = f"""
<html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 900px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Lote de Comités Reagendados</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">Se han <strong>REAGENDADO {len(comites_reagendados)} comités</strong> para el <strong>{fecha_formateada_display}</strong> en <strong>{lugar_enlace}</strong>.</p>

            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #4CAF50; margin-top: 0;">📅 Información General del Lote</h3>
                <p style="margin: 5px 0;"><strong>Fecha y Hora:</strong> {fecha_formateada_display}</p>
                <p style="margin: 5px 0;"><strong>Lugar/Enlace:</strong> {lugar_enlace}</p>
                <p style="margin: 5px 0;"><strong>Cantidad de Comités:</strong> {len(comites_reagendados)}</p>
            </div>

            <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">📋 Detalles de los Comités:</h3>
            {comites_html}

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Saludos cordiales,<br>
                <strong>ESTA ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.</strong>
            </p>
        </div>
    </body>
</html>
"""

    try:
        # Enviar el correo con formato HTML
        em = EmailMessage()
        em['From'] = 'bcabcomitessena@gmail.com'
        em['To'] = ', '.join(destinatarios)
        em['Subject'] = asunto
        em.set_content(mensaje, subtype='html')

        contexto = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
            smtp.login('bcabcomitessena@gmail.com', 'wjqusewsvylzfzci')
            smtp.send_message(em)
            
        print(f"Correo de lote enviado exitosamente a {len(destinatarios)} destinatarios")
        
    except Exception as e:
        print(f"Error al enviar correo del lote: {e}")





def usuario_name():
    if 'logueado' in session and session['logueado']:
        nombre = session.get('nombre', '')
        apellido = session.get('apellido', '')
        usuario_logueado = f"{nombre} {apellido}"
        return usuario_logueado
    else:
        return "Usuario no logueado"







if __name__ == '__main__':
    app.mainloop()





