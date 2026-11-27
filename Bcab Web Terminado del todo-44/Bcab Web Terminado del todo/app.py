from flask import Flask, render_template, request, redirect, session,jsonify
from flask import Flask, render_template, request, redirect, session,jsonify
from flask import Flask, render_template, request, redirect, session,jsonify
from flask import Flask, render_template, request, redirect, session,jsonify
from funciones import mostrar_realizados,mostrar_solicitud,mostrar_agendados, rechazar, agendado,solicitarComite,consulta_instructor_agendados,consulta_instructor_solicitado,reagendado,obtener_datos,generar_pdf,actualizar_estado_realizado
from conexion import get_db_connection,mysql
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime,timedelta
import locale
import hashlib
import smtplib
import ssl
import smtplib
from email.message import EmailMessage
import os
import pythoncom
from flask import send_file
from docx2pdf import convert  
from notifypy import Notify 
import random
import smtplib
from werkzeug.utils import secure_filename
from crud_usuarios import crud  # Importas el Blueprint
from alimentador import alimentador 

# En la parte superior de app.py, donde tienes los otros imports de funciones
from funciones import agendado_lote, rechazar_lote, F_reagendado_lote,reagendado_lote_multiple_mejorado,usuario_name



app = Flask(__name__)
app.register_blueprint(crud)
app.register_blueprint(alimentador)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
UPLOAD_FOLDER = r"C:\Users\AdminSena\Downloads\Bcab Web Terminado del todo\static\img"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


CORS(app)
jwt = JWTManager(app)

#------ INCIO DE  RUTAS --------------------------------------
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

@app.route('/manual_aprenidiz')
def manual_aprenidz():
    return render_template('manual_aprendiz.html')

@app.route('/manual_coordinador')
def manual_coordinador():
    return render_template('manual_coordinador.html')


@app.route('/manual_instructor')
def manual_instructor():
    return render_template('manual_instructor.html')

@app.route('/manual_super_user')
def manual_super_user():
    return render_template('manual_super_user.html')


@app.route('/atras')
def atras():
    return redirect('/mostrar_solicitados')

@app.route('/redactar_solicitud')
def redactar_solicitud():
    return render_template('instructor/solicitudcomite.html')

@app.route('/manual_usuarios')
def manual():
    return render_template('manual.html')

@app.route('/redactar_acta')
def redactar_acta():
    return render_template('instructor/solicitar_acta.html')

@app.route('/vista_manual')
def vista_manual():
    return render_template("manual.html")

#------FIN RUTAS----------------------------------------------------------------------------------
#----------------LOGIN-----------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        correo = request.form['correo_enviado']
        contrasena = request.form['contrasena']
        hashed_contrasena = hashlib.sha512(contrasena.encode("utf-8")).hexdigest()
        conexion = get_db_connection()
        cursor = conexion.cursor()
        #consulta = "SELECT contrasena, rol, nombre, apellido FROM usuarios WHERE correo_electronico = %s AND contrasena = %s"💚
        consulta = "SELECT contrasena, rol, nombre, apellido, correo_electronico FROM usuarios WHERE correo_electronico = %s AND contrasena = %s" 

        cursor.execute(consulta, (correo, hashed_contrasena))
        resultado = cursor.fetchone()
        

        if resultado:
            if resultado[0] == hashed_contrasena:
                session['logueado'] = True
                session['rol'] = resultado[1]
                session['nombre'] = resultado[2]
                session['apellido'] = resultado[3]
                session['correo_electronico'] = resultado[4]

                if session['rol'] == 'coordinador':    
                    return redirect('/mostrar_solicitados')
                elif session['rol'] == 'instructor':
                    return redirect('/home_instructor_solicitado_agendados')
                elif session['rol'] == 'heroe':
                    return redirect('/inicio_crud')
                else:
                    return redirect('/')
            else:
                return render_template('login.html', error2='Contraseña incorrecta')
        else:
            return render_template('login.html', error1='Email o Contraseña incorrecto')
    return render_template('login.html')



@app.route('/cambio_contrasena', methods=['POST'])
def cambio_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']
        conexion = get_db_connection()
        cursor = conexion.cursor()
        #cursor.execute(f"SELECT correo_electronico FROM usuarios WHERE correo_electronico = '{correo}'")💚
        cursor.execute(f"SELECT correo_electronico FROM usuarios WHERE correo_electronico = '{correo}'")
        resultado = cursor.fetchone()

        if resultado:
            verification_token = create_access_token(identity=correo)
            #cursor.execute(f"UPDATE usuarios SET token = '{verification_token}' WHERE correo_electronico = '{correo}'")💚
            cursor.execute(f"UPDATE usuarios SET token = '{verification_token}' WHERE correo_electronico = '{correo}'")

            conexion.commit()

            asunto = 'Código de Recuperación'
            cuerpo = f"""
<html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <h2 style="text-align: center; color: #4CAF50;">Recuperación de Contraseña</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hola,</p>
            <p style="font-size: 16px; line-height: 1.6;">Hemos recibido una solicitud para recuperar tu contraseña. Si no has solicitado este cambio, por favor ignora este correo.</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="color: #4CAF50; font-size: 18px; margin-bottom: 10px;">Haz clic en el siguiente enlace para restablecer tu contraseña:</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    <a href="http://127.0.0.1:5000/nueva/{verification_token}/{correo}" style="color: #ffffff; background-color: #4CAF50; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a>
                </p>
            </div>

            <p style="margin-top: 20px; text-align: center; font-size: 16px; color: #777;">
                Si no solicitaste este cambio, puedes ignorar este correo.<br>
                Saludos cordiales,<br>
                ESTE CORREO ES SOLO UNA NOTIFICACIÓN, NO ES UN CORREO OFICIAL.
            </p>
        </div>
    </body>
</html>
"""

            email_emisor = 'bcabcomitessena@gmail.com'
            email_contrasena = 'wjqusewsvylzfzci'

            em = EmailMessage()
            em['From'] = email_emisor
            em['To'] = correo
            em['Subject'] = asunto
            em.set_content(cuerpo, subtype='html')

            contexto = ssl.create_default_context()
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
                smtp.login(email_emisor, email_contrasena)
                smtp.sendmail(email_emisor, correo, em.as_string())

            """ este no cogio por el notify asi que use el player """
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
                smtp.login(email_emisor, email_contrasena)
                smtp.sendmail(email_emisor, correo, em.as_string())
                notification = Notify()
                notification.title = "¡Revisa tu correo!"
                notification.message = "Por favor, revisa tu correo electrónico para restablecer tu contraseña."
                notification.icon = r"C:\Users\AdminSena\Downloads\Bcab Web Terminado del todo\static\img\logo-sena-blanco.png" 

                notification.send()

            return render_template('login.html')
        else:
            return render_template('recuperar.html', mensaje='El correo no existe')


@app.route('/nueva/<tk>/<correo>')
def nueva(tk, correo):
    conexion = get_db_connection()
    cursor = conexion.cursor()
    #cursor.execute(f"SELECT token FROM usuarios WHERE correo_electronico = '{correo}'")💚
    cursor.execute(f"SELECT token FROM usuarios WHERE correo_electronico = '{correo}'")

    token_db = cursor.fetchall()
    
    if token_db[0][0] == tk:
        #cursor.execute(f"UPDATE usuarios SET token = ' ' WHERE correo_electronico = '{correo}'")💚
        cursor.execute(f"UPDATE usuarios SET token = ' ' WHERE correo_electronico = '{correo}'")

        return redirect(f'/nuevacontrasena/{correo}')
    else:
        return redirect('/')

@app.route('/nuevacontrasena/<correo>')
def nuevacontrasena(correo):
    return render_template('nuevacontrasena.html', email=correo)

@app.route('/guardanueva', methods=['POST'])
def guardanueva():
    email = request.form['email']
    contrasena1 = request.form['contrasena1']
    contrasena2 = request.form['contrasena2']
    if contrasena1 == contrasena2:
        contrasena_nueva = hashlib.sha512(contrasena1.encode("utf-8")).hexdigest()
        conexion = get_db_connection()
        cursor = conexion.cursor()
        #cursor.execute(f"UPDATE usuarios SET contrasena = '{contrasena_nueva}' WHERE correo_electronico = '{email}'")
        cursor.execute(f"UPDATE usuarios SET contrasena = '{contrasena_nueva}' WHERE correo_electronico = '{email}'")

        conexion.commit()
        return redirect('/')
    else:
        return render_template('nuevacontrasena.html', email=email, mensaje="Contraseñas no coinciden.")
#--------------------------FIN DEL LOGIN---------------------------------------------------------------------------------------------
#--- INICIO SOLICITUD Y AGENDADOS---------------------------------------------------------------------------------------------

@app.route("/mostrar_solicitados")
def mostrar_solicitados():
    datos_solicitud = mostrar_solicitud()
    perfil_name = usuario_name()
    return render_template('coordinador/solicitados.html', solicitud=datos_solicitud, usuario = perfil_name)
    


@app.route("/mostrar_agendados")
def mostrar_agendado():
    # Obtener agendados
    datos_agendados = mostrar_agendados()
    
    # Obtener realizados
    datos_realizados = mostrar_realizados()
    perfil_name = usuario_name()
    
    print("Datos de agendados:", len(datos_agendados), "grupos")
    print("Datos de realizados:", len(datos_realizados), "grupos")
    
    return render_template("coordinador/agendados.html", 
                         agendados=datos_agendados, 
                         realizados=datos_realizados, usuario = perfil_name)

@app.route('/rechazar/<id_comite>')
def rechazar_route(id_comite):
    rechazar(id_comite)
    return redirect('/mostrar_solicitados')
    

@app.route('/agendado/<id_comite>', methods=['POST'])
def agendado_route(id_comite):
    try:
        # Recoger la fecha del formulario
        fecha_agendacion = request.form['agendar_fecha']
        print(f"Fecha recibida: {fecha_agendacion}") 

        #lugar/enlace
        lugar_enlace = request.form['lugar/enlace']
        print(f"Fecha recibida: {lugar_enlace}")

        # Establecer la configuración regional en español
        locale.setlocale(locale.LC_TIME, 'es_ES')
        # Ajustar el formato de la cadena de fecha y hora
        fecha_agendacion = fecha_agendacion.replace('T', ' ')

    

        # Convertir la fecha a un objeto datetime
        formato = "%Y-%m-%d %H:%M"
        datetime_fecha = datetime.strptime(fecha_agendacion, formato)
        print(f"Fecha convertida: {datetime_fecha}")

        # Formatear la fecha como necesites (opcional)
        fecha_formateada = datetime_fecha
        
        print(f"Fecha formateada: {fecha_formateada}")
                # Llamar a la función 'agendado' con los datos
        agendado(id_comite, fecha_formateada,lugar_enlace) 

        # Redireccionar a la página mostrar_agendados
        return redirect('/mostrar_agendados')

    except locale.Error as e:
        print(f"Error en la configuración regional: {e}")
        return "Error en la configuración regional", 500

    except ValueError as e:
        print(f"Error al convertir la fecha: {e}")
        return "Error al convertir la fecha", 400

    except KeyError as e:
        print(f"Error en el formulario: {e}")
        return "Error en el formulario", 400

    except Exception as e:
        print(f"Error inesperado: {e}")
        return "Error inesperado", 500
    

@app.route('/reagendado/<id_comite>', methods=['POST'])
def reagendado_ruta(id_comite):
    try:
        # Recoger la fecha del formulario
        fecha_agendacion = request.form['Reagendar']
        print(f"Fecha recibida: {fecha_agendacion}") 

        #lugar/enlace
        lugar_enlace = request.form['lugar/enlace']
        print(f"Fecha recibida: {lugar_enlace}")

        # Establecer la configuración regional en español
        locale.setlocale(locale.LC_TIME, 'es_ES')
        # Ajustar el formato de la cadena de fecha y hora
        fecha_agendacion = fecha_agendacion.replace('T', ' ')

        ## Convertir la fecha a un objeto datetime
        formato = "%Y-%m-%d %H:%M"
        datetime_fecha = datetime.strptime(fecha_agendacion, formato)
        print(f"Fecha convertida: {datetime_fecha}")

        # Formatear la fecha como necesite
        
        fecha_formateada = datetime_fecha.strftime("%A %d de %B %Y %I:%M %p")
        print(f"Fecha formateada: {fecha_formateada}")
                # Llamar a la función 'agendado' con los datos
        reagendado(id_comite, fecha_formateada,lugar_enlace) 

        # Redireccionar a la página mostrar_agendados
        return redirect('/mostrar_agendados')

    except locale.Error as e:
        print(f"Error en la configuración regional: {e}")
        return "Error en la configuración regional", 500

    except ValueError as e:
        print(f"Error al convertir la fecha: {e}")
        return "Error al convertir la fecha", 400

    except KeyError as e:
        print(f"Error en el formulario: {e}")
        return "Error en el formulario", 400

    except Exception as e:
        print(f"Error inesperado: {e}")
        return "Error inesperado", 500
    




#----- FIN DE SOLICITUDES Y AGENDADOS--------------------------------------------------------------
# Configurar el locale para español (opcional, para los nombres de días y meses)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # En Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # En Windows
    except:
        pass  # Si no se puede configurar, usar inglés por defecto

# funcion para consultar los comites agendados
@app.route("/home_instructor_solicitado_agendados")
def home_instructor_solicitado():
    solicitados = consulta_instructor_solicitado()
    agendados = consulta_instructor_agendados()
    perfil_name = usuario_name()
    
    # CORRECCIÓN: Validar que los datos no sean None
    if solicitados is None:
        solicitados = {}
    if agendados is None:
        agendados = {}
    
    # Procesar las fechas de agendados para formatearlas
    agendados_con_fecha_formateada = {}
    solicitados_con_fecha_formateada = {}
    
    # Procesar agendados (que es un diccionario)
    for fecha_key, lista_comites in agendados.items():
        agendados_con_fecha_formateada[fecha_key] = []
        
        for fila in lista_comites:
            # Verificar que fila sea una lista o tupla
            if isinstance(fila, str):
                print(f"Advertencia: fila es una cadena: {fila}")
                continue
            
            # fila[16] contiene fechaAgendacion según tu estructura
            fecha_original = fila[16] if len(fila) > 16 else None
            
            # Validar que la fecha no esté vacía o sea None
            if not fecha_original or fecha_original == '' or fecha_original is None:
                fecha_formateada = "Fecha no disponible"
            else:
                try:
                    # Si la fecha ya está formateada (contiene palabras en español)
                    if any(palabra in str(fecha_original).lower() for palabra in ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']):
                        fecha_formateada = str(fecha_original)
                    else:
                        # Convertir la fecha a datetime
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
                        
                        fecha_formateada = f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}"
                
                except (ValueError, AttributeError) as e:
                    print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
                    fecha_formateada = "Fecha inválida"
            
            # Crear nueva tupla con la fecha formateada
            if isinstance(fila, (list, tuple)):
                fila_con_fecha = tuple(list(fila) + [fecha_formateada])
            else:
                print(f"Tipo de fila no esperado: {type(fila)}")
                continue
            
            agendados_con_fecha_formateada[fecha_key].append(fila_con_fecha)

    # Procesar solicitados (que es un diccionario)
    for fecha_key, lista_comites in solicitados.items():
        solicitados_con_fecha_formateada[fecha_key] = []
        
        for fila in lista_comites:
            # Verificar que fila sea una lista o tupla
            if isinstance(fila, str):
                print(f"Advertencia: fila es una cadena: {fila}")
                continue
            
            # fila[15] contiene fechaPresentacionQueja según tu consulta SQL
            fecha_original = fila[15] if len(fila) > 15 else None
            
            # Validar que la fecha no esté vacía o sea None
            if not fecha_original or fecha_original == '' or fecha_original is None:
                fecha_formateada = "Fecha no disponible"
            else:
                try:
                    # Si la fecha ya está formateada (contiene palabras en español)
                    if any(palabra in str(fecha_original).lower() for palabra in ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']):
                        fecha_formateada = str(fecha_original)
                    else:
                        # Convertir la fecha a datetime
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
                        
                        fecha_formateada = f"{dia_semana} {dia:02d} de {mes} {ano} {hora} {am_pm}"
                
                except (ValueError, AttributeError) as e:
                    print(f"Error al formatear fecha: {fecha_original}, Error: {e}")
                    fecha_formateada = "Fecha inválida"
            
            # Crear nueva tupla con la fecha formateada
            if isinstance(fila, (list, tuple)):
                fila_con_fecha = tuple(list(fila) + [fecha_formateada])
            else:
                print(f"Tipo de fila no esperado: {type(fila)}")
                continue
            
            solicitados_con_fecha_formateada[fecha_key].append(fila_con_fecha)

    # CORRECCIÓN: Manejo de errores para la consulta de la base de datos
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        sql = "SELECT nombreCapituloFalla, articuloFalla, informacionArticulo FROM comites"
        cursor.execute(sql)

        # Acceder al último registro
        datosCapturados = cursor.fetchall()
        print(f"Consulta respuesta 💙💙💙 {datosCapturados}")
        
        # CORRECCIÓN: Validar que hay datos antes de acceder al último registro
        if datosCapturados:
            ultimo_fila = datosCapturados[-1]
            print(f"Consulta respuesta 💛💛💛💛💛 {ultimo_fila}")
            capitulos = ultimo_fila[0] or ""  # Usar cadena vacía si es None
            articulos = ultimo_fila[1] or ""
            informacionArticulos = ultimo_fila[2] or ""

            lista_capitulos = capitulos.split(" || ") if capitulos else []
            lista_articulos = articulos.split(" || ") if articulos else []
            lista_informacion = informacionArticulos.split(" || ") if informacionArticulos else []
        else:
            # Si no hay datos, usar listas vacías
            lista_capitulos = []
            lista_articulos = []
            lista_informacion = []
            
        cursor.close()
        conexion.close()
        
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        # En caso de error, usar listas vacías
        lista_capitulos = []
        lista_articulos = []
        lista_informacion = []

    # CORRECCIÓN: Crear la lista de fallas de manera más robusta
    fallas = []
    max_items = max(len(lista_capitulos), len(lista_articulos), len(lista_informacion), 4)
    
    for i in range(min(max_items, 4)):  # Limitar a máximo 4 elementos
        capitulo = f"Capítulo {lista_capitulos[i]} /" if i < len(lista_capitulos) and lista_capitulos[i] else ""
        articulo = f"Artículo: {lista_articulos[i]} /" if i < len(lista_articulos) and lista_articulos[i] else ""
        informacion = lista_informacion[i] if i < len(lista_informacion) and lista_informacion[i] else ""

        # Solo agregar si al menos uno de los campos tiene contenido
        if capitulo or articulo or informacion:
            fallas.append({
                "capitulo": capitulo.strip(),
                "articulo": articulo.strip(),
                "informacion": informacion.strip()
            })

    return render_template(
        'instructor/home-instructor.html',
        solicitados=solicitados_con_fecha_formateada, 
        agendados=agendados_con_fecha_formateada,
        usuario=perfil_name,
        fallas=fallas
    )


 


#-----------------Inicio de modulo para solicitar actas--------------------------
@app.route('/instructor/acta_renderizada.html')
def comite():
    datos = request.args.get('datos', None)
    fecha_agendacion_comite = request.args.get('fecha_agendacion_comite', None)

    if datos and fecha_agendacion_comite:
        datos = datos.split(',')
        fecha_agendacion_comite = fecha_agendacion_comite.split(',')
        
        fecha_original = datetime.strptime(fecha_agendacion_comite, '%Y-%m-%d')
        fecha_agendacion_comite = fecha_original.strftime('%d de %B de %Y')
        fecha_agendacion_comite = fecha_agendacion_comite
    else:
        datos = []
        fecha_agendacion_comite = []

    return render_template('instructor/acta_renderizada.html', datos=datos, fecha_agendacion_comite=fecha_agendacion_comite)


    



    #-------------------------------------pdfs-----------------------------------------------------




# Obtener la ruta universal al Escritorio
escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

# Subcarpeta para organizar tus PDFs
carpeta_destino = os.path.join(escritorio, "pdfs_citaciones_individuales")

# Crear carpeta si no existe
os.makedirs(carpeta_destino, exist_ok=True)





@app.route('/ejecutar_clase', methods=['POST'])
def ejecutar_clase():
    ruta_firma = None
    if 'firma' in request.files and request.files['firma'].filename:
        archivo_firma = request.files['firma']
        ruta_firma = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(archivo_firma.filename))
        archivo_firma.save(ruta_firma)

    # 📍 Ruta dinámica al Escritorio del usuario que corre Flask
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    carpeta_destino = os.path.join(escritorio, "pdfs_citaciones_individuales")
    os.makedirs(carpeta_destino, exist_ok=True)

    datos = obtener_datos()
    generar_pdf(datos, carpeta_destino, ruta_firma)

    mensaje = f"PDFs generados correctamente en {carpeta_destino}." if datos else "No hay aprendices en estado 'agendado'."
    return jsonify({"mensaje": mensaje})


#------------------------------funciones de generacion de queja ↓↓↓↓↓↓↓  -----------------------------------------------------------------------------
""" ======================= RUTAS ======================= """
@app.route('/solicitar_comite')
def solicitar_comite():
    return render_template('instructor/solicitar_comite.html')

@app.route('/aprendices_seleccionados')
def aprendices_seleccionados():
    return render_template('instructor/aprendices_seleccionados.html')

@app.route('/aprendices_seleccionados_nuevoReglamento')
def aprendices_seleccionados_nuevoReglamento():
    return render_template('instructor/aprendices_seleccionados_nuevoReglamento.html')

@app.route('/instructor/inicio_instructor')
def inicio_instructor():
    return redirect('/')

""" ======================= FUNCIONES PARA INSTRUCTORES ======================= """
# Para esta interfaz falta: Area
@app.route('/buscar_ficha', methods=['POST'])
def buscar_ficha():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    buscarFicha = request.form.get('buscarFicha')

    fichas = []
    aprendices = []
    fichaInicio = None

    if buscarFicha:
        sql_fichas = "SELECT * FROM fichas WHERE numeroFicha = %s"
        cursor.execute(sql_fichas, (buscarFicha,))
        fichas = cursor.fetchall()

        if fichas:
            numeroFicha = fichas[0]['numeroFicha']
            # Filtrar aprendices solo con estados permitidos
            estados_permitidos = ('Inducción', 'Formación', 'Condicionado')
            sql_aprendices = """
                SELECT * FROM aprendices 
                WHERE ficha = %s AND estado IN (%s, %s, %s)
                ORDER BY apellidos, nombres
            """
            cursor.execute(sql_aprendices, (numeroFicha,) + estados_permitidos)
            aprendices = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'instructor/solicitar_comite.html',
        fichas=fichas,
        aprendices=aprendices,
        busqueda_realizada=True
    )



@app.route('/verificar_historial', methods=['POST'])
def verificar_historial():
    data = request.get_json()
    
    if not data or 'numeroDocumento_procesado' not in data:
        return jsonify({"success": False, "message": "No se recibieron documentos"}), 400

    numeroDocumento_procesado = data['numeroDocumento_procesado']
    if not numeroDocumento_procesado:
        return jsonify({"success": False, "message": "Lista de aprendices vacía"}), 400

    marcadores = ", ".join(["%s"] * len(numeroDocumento_procesado))
    conexion = get_db_connection()
    cursor = conexion.cursor()

    # Solo validar si ya hay llamados en medidas_formativas
    sql_llamados = f"SELECT numeroDocumento, fecha, nombre, descripcion, fase FROM medidas_formativas WHERE numeroDocumento IN ({marcadores})"
    cursor.execute(sql_llamados, numeroDocumento_procesado)
    llamados_existentes = cursor.fetchall()

    avisos_llamados = []
    if llamados_existentes:
        documentos_con_llamado = [(fila[0], fila[2], fila[1], fila[3], fila[4]) for fila in llamados_existentes]
        avisos_llamados = [
            f"{nombre} (Documento: {doc}, Fecha: {fecha.strftime('%Y-%m-%d')}, Descripción: {descripcion}, Fase de programa: {fase})"
            for doc, nombre, fecha, descripcion, fase in documentos_con_llamado
        ]

    cursor.close()
    conexion.close()

    return jsonify({
        "success": True,
        "tiene_historial": len(avisos_llamados) > 0,
        "avisos_llamados": avisos_llamados,
        "documentos": numeroDocumento_procesado  # Devolver los documentos para el siguiente paso
    })


# Segundo endpoint: Procesar después de confirmación
@app.route('/procesar_aprendices_confirmado', methods=['POST'])
def procesar_aprendices_confirmado():
    data = request.get_json()
    
    if not data or 'numeroDocumento_procesado' not in data:
        return jsonify({"success": False, "message": "No se recibieron documentos"}), 400

    numeroDocumento_procesado = data['numeroDocumento_procesado']
    if not numeroDocumento_procesado:
        return jsonify({"success": False, "message": "Lista de aprendices vacía"}), 400

    marcadores = ", ".join(["%s"] * len(numeroDocumento_procesado))
    conexion = get_db_connection()
    cursor = conexion.cursor()

    # Obtener nombres completos
    sql_nombres = f"SELECT DISTINCT numeroDocumento, nombres, apellidos, estado, ficha, correo_electronico, telefono FROM aprendices INNER JOIN juicios_evaluativos ON aprendices.numeroDocumento = juicios_evaluativos.documentoIdentidad WHERE juicios_evaluativos.documentoIdentidad IN ({marcadores})"
    cursor.execute(sql_nombres, numeroDocumento_procesado)
    nombres = cursor.fetchall() 

    nombres_completos = {nombre[0]: f"{nombre[1]} {nombre[2]}" for nombre in nombres}
    estado = {nombre[0]: nombre[3] for nombre in nombres}
    ficha = {nombre[0]: nombre[4] for nombre in nombres}
    correo_electronico = {nombre[0]: nombre[5] for nombre in nombres}
    telefono = {nombre[0]: nombre[6] for nombre in nombres}

    # Obtener competencias y resultados
    sql_competencias = f"SELECT DISTINCT competencia, documentoIdentidad FROM juicios_evaluativos WHERE documentoIdentidad IN ({marcadores})"
    cursor.execute(sql_competencias, numeroDocumento_procesado)
    competencias = cursor.fetchall()

    resultados_competencia = {}

    for competencia, documento in competencias:
        sql_resultados = "SELECT resultadoAprendizaje FROM juicios_evaluativos WHERE competencia = %s AND documentoIdentidad = %s"
        cursor.execute(sql_resultados, (competencia, documento))
        resultados = cursor.fetchall()

        if documento not in resultados_competencia:
            resultados_competencia[documento] = {}

        resultados_competencia[documento][competencia] = [resultado[0] for resultado in resultados]

    solo_numero_ficha = list({nombre[4] for nombre in nombres})
    marcadores_ficha = ", ".join(["%s"] * len(solo_numero_ficha))

    sql_fechaInicio = f"SELECT fechaInicio FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_fechaInicio, solo_numero_ficha)
    fechaInicio_capturada = cursor.fetchall()
    fechaInicio_consulta = fechaInicio_capturada[0][0]
    fechaInicio = fechaInicio_consulta.strftime('%Y-%m-%d')

    sql_fichas = f"SELECT nivel_formacion, programaFormacion FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_fichas, solo_numero_ficha)
    fichaPrograma_capturada = cursor.fetchall()

    fichaPrograma = " EN ".join(fichaPrograma_capturada[0])

    sql_datos_coordinadores = f"SELECT nombreCoordinador, correoCoordinador FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_datos_coordinadores, solo_numero_ficha)
    areaPrograma_y_correoCoordinador = cursor.fetchall()

    for nombreCoordinador, correoCoordinador in areaPrograma_y_correoCoordinador:
        nombreCoordinador = nombreCoordinador
        correoCoordinador = correoCoordinador    

    cursor.close()
    conexion.close()

    return jsonify({
        "success": True,
        "nombres_completos": nombres_completos,
        "resultados_competencia": resultados_competencia,
        "estado": estado,
        "ficha": ficha,
        "correo_electronico": correo_electronico,
        "telefono": telefono,
        "fichaPrograma": fichaPrograma,
        "nombreCoordinador": nombreCoordinador,
        "correoCoordinador": correoCoordinador,
        "fechaInicio": fechaInicio,
        "procesamiento_completado": True  # Indicador de que ya terminó el procesamiento
    }) 





@app.route('/procesar_aprendices', methods=['POST'])
def procesar_aprendices():
    avisos_llamados = []
    data = request.get_json()

# es esto------------------------------
    if not data or 'numeroDocumento_procesado' not in data:
        return jsonify({"success": False, "message": "No se recibieron documentos"}), 400

    numeroDocumento_procesado = data['numeroDocumento_procesado']
    if not numeroDocumento_procesado:
        return jsonify({"success": False, "message": "Lista de aprendices vacía"}), 400

    marcadores = ", ".join(["%s"] * len(numeroDocumento_procesado))
    conexion = get_db_connection()
    cursor = conexion.cursor()

    # Validar si ya hay llamados en medidas_formativas
    sql_llamados = f"SELECT numeroDocumento, fecha, nombre, descripcion, fase FROM medidas_formativas WHERE numeroDocumento IN ({marcadores})"
    cursor.execute(sql_llamados, numeroDocumento_procesado)
    llamados_existentes = cursor.fetchall()

    if llamados_existentes:
        documentos_con_llamado = [(fila[0], fila[2], fila[1], fila[3], fila[4] ) for fila in llamados_existentes]  # númeroDocumento, nombre, fecha,fase
        avisos_llamados = [
            f"{nombre} (Documento: {doc}, Fecha: {fecha.strftime('%Y-%m-%d')}, Descripciónis: {descripcion}, Fase: {fase})"for doc, nombre, fecha, descripcion, fase in documentos_con_llamado]

    # Obtener nombres completos
    sql_nombres = f"SELECT DISTINCT numeroDocumento, nombres, apellidos, estado, ficha, correo_electronico, telefono FROM aprendices INNER JOIN juicios_evaluativos ON aprendices.numeroDocumento = juicios_evaluativos.documentoIdentidad WHERE juicios_evaluativos.documentoIdentidad IN ({marcadores})"
    cursor.execute(sql_nombres, numeroDocumento_procesado)
    nombres = cursor.fetchall() 

    nombres_completos = {nombre[0]: f"{nombre[1]} {nombre[2]}" for nombre in nombres}
    estado = {nombre[0]: nombre[3] for nombre in nombres}
    ficha = {nombre[0]: nombre[4] for nombre in nombres}
    correo_electronico = {nombre[0]: nombre[5] for nombre in nombres}
    telefono = {nombre[0]: nombre[6] for nombre in nombres}

    # Obtener competencias y resultados
    sql_competencias = f"SELECT DISTINCT competencia, documentoIdentidad FROM juicios_evaluativos WHERE documentoIdentidad IN ({marcadores})"
    cursor.execute(sql_competencias, numeroDocumento_procesado)
    competencias = cursor.fetchall()

    resultados_competencia = {}

    for competencia, documento in competencias:
        sql_resultados = "SELECT resultadoAprendizaje FROM juicios_evaluativos WHERE competencia = %s AND documentoIdentidad = %s"
        cursor.execute(sql_resultados, (competencia, documento))
        resultados = cursor.fetchall()

        if documento not in resultados_competencia:
            resultados_competencia[documento] = {}

        resultados_competencia[documento][competencia] = [resultado[0] for resultado in resultados]

    solo_numero_ficha = list({nombre[4] for nombre in nombres})
    marcadores_ficha = ", ".join(["%s"] * len(solo_numero_ficha))


    sql_fechaInicio = f"SELECT fechaInicio FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_fechaInicio, solo_numero_ficha)
    fechaInicio_capturada = cursor.fetchall()
    fechaInicio_consulta = fechaInicio_capturada[0][0]
    fechaInicio = fechaInicio_consulta.strftime('%Y-%m-%d')


    sql_fichas = f"SELECT nivel_formacion, programaFormacion FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_fichas, solo_numero_ficha)
    fichaPrograma_capturada = cursor.fetchall()

    fichaPrograma = " EN ".join(fichaPrograma_capturada[0])

    sql_datos_coordinadores = f"SELECT nombreCoordinador, correoCoordinador FROM fichas WHERE numeroFicha IN ({marcadores_ficha})"
    cursor.execute(sql_datos_coordinadores, solo_numero_ficha)
    areaPrograma_y_correoCoordinador = cursor.fetchall()

    for nombreCoordinador, correoCoordinador in areaPrograma_y_correoCoordinador:
        nombreCoordinador = nombreCoordinador
        correoCoordinador = correoCoordinador    

    cursor.close()
    conexion.close()

    return jsonify({
        "success": True,
        "nombres_completos": nombres_completos,
        "resultados_competencia": resultados_competencia,
        "estado": estado,
        "ficha": ficha,
        "correo_electronico": correo_electronico,
        "telefono": telefono,
        "fichaPrograma": fichaPrograma,
        "nombreCoordinador": nombreCoordinador,
        "correoCoordinador": correoCoordinador,
        "fechaInicio": fechaInicio,
        "avisos_llamados": avisos_llamados,
    })


def obtener_datos_completos_viejoReglamento(articulo=None):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener datos únicos de `tituloCapitulo` y `articulos`
    sql_titulo_articulo = "SELECT DISTINCT tituloCapitulo, articulos FROM viejo_reglamento"
    cursor.execute(sql_titulo_articulo)
    titulo_articulo = cursor.fetchall()

    # Diccionario para capítulos con artículos permitidos
    opciones_por_titulo = {
        "Deberes del Aprendiz.": [9],
        "Prohibiciones.": [10]
    }

    # Diccionario para la información de cada artículo
    opciones_por_fila = {}
    for item in titulo_articulo:
        articulo_actual = item['articulos']
        titulo = item['tituloCapitulo']

        # Obtener información del artículo
        sql_contenido_articulo = "SELECT informacionArticulo FROM viejo_reglamento WHERE articulos = %s AND tituloCapitulo = %s"
        cursor.execute(sql_contenido_articulo, (articulo_actual, titulo,))
        contenido_articulo = [fila['informacionArticulo'] for fila in cursor.fetchall()]

        # Guardar en el diccionario con una clave string
        opciones_por_fila[f"{articulo_actual} - {titulo}"] = contenido_articulo  # 🔧 Cambio aquí


    # Si se solicita información de un solo artículo
    informacion_articulo = None
    if articulo:
        sql_informacion_articulo = "SELECT informacionArticulo FROM viejo_reglamento WHERE articulos = %s"
        cursor.execute(sql_informacion_articulo, (articulo,))
        informacion_articulo = [fila['informacionArticulo'] for fila in cursor.fetchall()]
        descripcion = ""

    cursor.close()
    conexion.close()

    return {
        "titulo_articulo": titulo_articulo,
        "opciones_por_titulo": opciones_por_titulo,
        "opciones_por_fila": opciones_por_fila,
        "informacion_articulo": informacion_articulo,
        "descripcion" : descripcion
    }

def obtener_datos_completos_nuevoReglamento(articulo=None):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener datos únicos de `tituloCapitulo` y `articulos`
    sql_titulo_articulo = "SELECT DISTINCT tituloCapitulo, articulos FROM nuevo_reglamento"
    cursor.execute(sql_titulo_articulo)
    titulo_articulo = cursor.fetchall()

    # Diccionario para capítulos con artículos permitidos
    opciones_por_titulo = {
        "Deberes del Aprendiz.": [9],
        "Prohibiciones.": [10]
    }

    # Diccionario para la información de cada artículo
    opciones_por_fila = {}
    for item in titulo_articulo:
        articulo_actual = item['articulos']
        titulo = item['tituloCapitulo']

        # Obtener información del artículo
        sql_contenido_articulo = "SELECT informacionArticulo FROM nuevo_reglamento WHERE articulos = %s AND tituloCapitulo = %s"
        cursor.execute(sql_contenido_articulo, (articulo_actual, titulo,))
        contenido_articulo = [fila['informacionArticulo'] for fila in cursor.fetchall()]

        # Guardar en el diccionario con una clave string
        opciones_por_fila[f"{articulo_actual} - {titulo}"] = contenido_articulo  # 🔧 Cambio aquí


    # Si se solicita información de un solo artículo
    informacion_articulo = None
    if articulo:
        sql_informacion_articulo = "SELECT informacionArticulo FROM nuevo_reglamento WHERE articulos = %s"
        cursor.execute(sql_informacion_articulo, (articulo,))
        informacion_articulo = [fila['informacionArticulo'] for fila in cursor.fetchall()]
        descripcion = ""

    cursor.close()
    conexion.close()

    return {
        "titulo_articulo": titulo_articulo,
        "opciones_por_titulo": opciones_por_titulo,
        "opciones_por_fila": opciones_por_fila,
        "informacion_articulo": informacion_articulo,
        "descripcion" : descripcion
    }

@app.route('/solicitar_comite_funcion', methods=['POST'])
def solicitar_comite_funcion():
    datos = request.get_json()
    aprendices = datos.get("aprendices", [])
    return subir_comite(aprendices)



@app.route('/subir_comite', methods=['POST'])
def subir_comite(aprendices):
    if 'logueado' in session and session['logueado']:
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        correo_electronico_instructor_queja = session['correo_electronico']
        
        nombre_instructor = f"{nombre_logueado} {apellido_instructor}"

        # Abrir la conexión UNA VEZ fuera del bucle
        conexion = get_db_connection()
        cursor = conexion.cursor()

        try:
            for aprendiz in aprendices:
                documento = aprendiz["documento"]
                nombre = aprendiz["nombre"]
                ficha = aprendiz["ficha"]
                fichaPrograma = aprendiz["fichaPrograma"]
                correo_electronico = aprendiz["correo_electronico"]
                telefono = aprendiz["telefono"]
                estado = aprendiz["estado"]
                clasificacion = aprendiz["clasificacion"]
                calificacion = aprendiz["calificacion"]
                fase = aprendiz["fase"]
                competencia = aprendiz["competencia"]
                resultados = ", ".join(aprendiz["resultados"]) if aprendiz["resultados"] else "No aplica"
                fecha_presentacion_queja = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                nombreCoordinador = aprendiz["nombreCoordinador"]
                correoCoordinador = aprendiz["correoCoordinador"]
                descripcionProblema = aprendiz["descripcion"]
                todos_los_correos = f"{correo_electronico},{correo_electronico_instructor_queja},{correoCoordinador},hfcarmonac@sena.edu.co,kmora@sena.edu.co,bienestaraprendizcab@sena.edu.co"
                
                print(f"Procesando aprendiz: {aprendiz}")

                # Procesar artículos
                capitulosArray = []
                articulosArray = []
                informacionArticuloArray = []

                for articulo_info in aprendiz["articulos"]:
                    capitulo = articulo_info["titulo"]
                    articulo = articulo_info["articulo"]
                    informacionArticulo = " ".join(articulo_info["informacion"])
                    
                    capitulosArray.append(capitulo)
                    articulosArray.append(articulo)
                    informacionArticuloArray.append(informacionArticulo)

                capitulos_concatenados = " || ".join(capitulosArray)
                articulos_concatenados = " || ".join(articulosArray)    
                informacionArticulos_concatenadas = " || ".join(informacionArticuloArray)

                # Insertar en tabla comites
                sql_solicitar_comite = "INSERT INTO comites (documentoAprendizCitado, nombreAprendizCitado, estadoAprendizCitado, clasificacionComite, competencia, resultadoAprendizaje, calificacionComite, estadoComite, fechaPresentacionQueja, ficha, correoAprendizCitado, telefonoAprendizCitado, nombreCapituloFalla, articuloFalla, informacionArticulo, descripcion, nombreFicha, correos, usuario_logueado, areaPrograma) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                
                cursor.execute(sql_solicitar_comite, (documento, nombre, estado, clasificacion, competencia, resultados, calificacion, "solicitud", fecha_presentacion_queja, ficha, correo_electronico, telefono, capitulos_concatenados, articulos_concatenados, informacionArticulos_concatenadas, descripcionProblema, fichaPrograma, todos_los_correos, nombre_instructor, nombreCoordinador))

                # Insertar en tabla medidas_formativas
                medidas_formativas_historial = "INSERT INTO medidas_formativas (instructor_citado, numeroDocumento, tipo, fecha, descripcion, nombre, fase) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                
                cursor.execute(medidas_formativas_historial, (nombre_instructor, documento, clasificacion, fecha_presentacion_queja, descripcionProblema, nombre, fase))

            # Confirmar la transacción DESPUÉS de procesar todos los aprendices
            conexion.commit()            
        except Exception as e:
            # En caso de error, hacer rollback
            conexion.rollback()
            print(f"❌ Error al procesar aprendices: {e}")
            raise e
            
        finally:
            cursor.close()
            conexion.close()
    
    return jsonify({"success": True, "message": "Datos guardados correctamente"})
""" =========================RUTA FLASK========================= """
@app.route('/obtener-informacion-articulo_viejoReglamento')
def obtener_informacion_articulo_route_viejo():
    articulo = request.args.get('articulo')
    datos = obtener_datos_completos_viejoReglamento(articulo)
    return jsonify(datos)

@app.route('/obtener-informacion-articulo_nuevoReglamento')
def obtener_informacion_articulo_route_nuevo():
    articulo = request.args.get('articulo')
    datos = obtener_datos_completos_nuevoReglamento(articulo)
    return jsonify(datos)
""" =============================FIN DE FUNCIONES============================= """

""" ======================FUNCION PARA CANCELAR APRENDICES - CORREGIDA====================== """
# Constante para la medida formativa de cancelación
MEDIDA_CANCELACION = "DE ACUERDO A PARAMETRIZACION DEL SISTEMA CESCAB, SE SUGIERE CANCELAR AL APRENDIZ SEGUN EL ACUERDO 009 DEL 2024"

def verificar_y_cancelar_aprendices():
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    try:        
        # SOLUCIÓN: Convertir ambos campos a STRING para asegurar la comparación correcta
        sql_aprendices_con_medidas = "SELECT DISTINCT CAST(mf.numeroDocumento AS CHAR) FROM medidas_formativas mf INNER JOIN aprendices a ON CAST(mf.numeroDocumento AS CHAR) = CAST(a.numeroDocumento AS CHAR)WHERE (a.medida_formativa IS NULL OR a.medida_formativa != %s)"
        cursor.execute(sql_aprendices_con_medidas, (MEDIDA_CANCELACION,))
        aprendices_con_medidas = cursor.fetchall()
        
        print(f"Aprendices con medidas formativas encontrados: {len(aprendices_con_medidas)}")
        print("-" * 60)
        
        aprendices_a_cancelar = []
        
        for (numero_documento,) in aprendices_con_medidas:
            print(f"\nRevisando aprendiz con documento: {numero_documento}")
            
            cancelar = False
            motivo_cancelacion = []
            
            sql_comite_realizado = """
            SELECT COUNT(*) FROM comites 
            WHERE CAST(documentoAprendizCitado AS CHAR) = %s 
            AND LOWER(TRIM(estadoComite)) = 'realizado'
            """
            cursor.execute(sql_comite_realizado, (str(numero_documento),))
            comites_realizados = cursor.fetchone()[0]
            
            print(f"  → Comités realizados: {comites_realizados}")
            
            if comites_realizados == 0:
                print(f"  ⚠️  No tiene comités realizados - NO se puede cancelar")
                continue  # Saltar al siguiente aprendiz
            
            # 1. Verificar medidas académicas por fase - CONVERTIR TIPOS
            sql_academico_fase = """
            SELECT fase, COUNT(*) as cantidad 
            FROM medidas_formativas 
            WHERE CAST(numeroDocumento AS CHAR) = %s 
            AND TRIM(tipo) = 'Académico' 
            GROUP BY fase
            """
            cursor.execute(sql_academico_fase, (str(numero_documento),))
            academico_por_fase = cursor.fetchall()
            
            print(f"  → Medidas académicas por fase: {academico_por_fase}")
            
            for fase, cantidad in academico_por_fase:
                if cantidad > 2:
                    cancelar = True
                    motivo = f"Excede límite de medidas académicas en {fase} ({cantidad}/2)"
                    motivo_cancelacion.append(motivo)
                    print(f"    ⚠️  {motivo}")
            
            # 2. Verificar medidas disciplinarias totales
            sql_disciplinario_total = """
            SELECT COUNT(*) as cantidad 
            FROM medidas_formativas 
            WHERE CAST(numeroDocumento AS CHAR) = %s 
            AND TRIM(tipo) = 'Disciplinario'
            """
            cursor.execute(sql_disciplinario_total, (str(numero_documento),))
            disciplinario_total = cursor.fetchone()[0]
            
            print(f"  → Medidas disciplinarias totales: {disciplinario_total}")
            
            if disciplinario_total > 2:
                cancelar = True
                motivo = f"Excede límite de medidas disciplinarias por programa ({disciplinario_total}/2)"
                motivo_cancelacion.append(motivo)
                print(f"    ⚠️  {motivo}")
            
            # 3. Verificar planes de mejoramiento académico por fase
            sql_plan_academico_fase = """
            SELECT fase, COUNT(*) as cantidad 
            FROM medidas_formativas 
            WHERE CAST(numeroDocumento AS CHAR) = %s 
            AND tipo LIKE '%Plan%Académico%' 
            GROUP BY fase
            """
            cursor.execute(sql_plan_academico_fase, (str(numero_documento),))
            plan_academico_por_fase = cursor.fetchall()
            
            if plan_academico_por_fase:
                print(f"  → Planes académicos por fase: {plan_academico_por_fase}")
                for fase, cantidad in plan_academico_por_fase:
                    if cantidad > 2:
                        cancelar = True
                        motivo = f"Excede límite de planes académicos en {fase} ({cantidad}/2)"
                        motivo_cancelacion.append(motivo)
                        print(f"    ⚠️  {motivo}")
            
            # 4. Verificar planes de mejoramiento disciplinario por fase
            sql_plan_disciplinario_fase = """
            SELECT fase, COUNT(*) as cantidad 
            FROM medidas_formativas 
            WHERE CAST(numeroDocumento AS CHAR) = %s 
            AND tipo LIKE '%Plan%Disciplinario%' 
            GROUP BY fase
            """
            cursor.execute(sql_plan_disciplinario_fase, (str(numero_documento),))
            plan_disciplinario_por_fase = cursor.fetchall()
            
            if plan_disciplinario_por_fase:
                print(f"  → Planes disciplinarios por fase: {plan_disciplinario_por_fase}")
                for fase, cantidad in plan_disciplinario_por_fase:
                    if cantidad > 1:
                        cancelar = True
                        motivo = f"Excede límite de planes disciplinarios en {fase} ({cantidad}/1)"
                        motivo_cancelacion.append(motivo)
                        print(f"    ⚠️  {motivo}")
            
            # 5. Verificar condicionamientos de matrícula (total en todo el proceso)
            sql_condicionamiento_total = """
            SELECT COUNT(*) as cantidad 
            FROM medidas_formativas 
            WHERE CAST(numeroDocumento AS CHAR) = %s 
            AND tipo LIKE '%Condicionamiento%'
            """
            cursor.execute(sql_condicionamiento_total, (str(numero_documento),))
            condicionamiento_total = cursor.fetchone()[0]
            
            if condicionamiento_total > 0:
                print(f"  → Condicionamientos totales: {condicionamiento_total}")
                if condicionamiento_total > 2:
                    cancelar = True
                    motivo = f"Excede límite de condicionamientos de matrícula ({condicionamiento_total}/2)"
                    motivo_cancelacion.append(motivo)
                    print(f"    ⚠️  {motivo}")
            
            # Mostrar resultado para este aprendiz
            if cancelar:
                print(f"  🚫 DEBE SER CANCELADO (tiene comités realizados)")
                aprendices_a_cancelar.append({
                    'documento': numero_documento,
                    'motivos': motivo_cancelacion
                })
            else:
                print(f"  ✅ Dentro de los límites permitidos")
        
        print("\n" + "=" * 60)
        print("APRENDICES A LOS QUE SE LES DEBERIA HACER EL PROCESO DE CANCELACION DE MATRICULA")
        print("=" * 60)
        
        if not aprendices_a_cancelar:
            print("No hay aprendices para cancelar.")
            return
        
        # Cancelar los aprendices que exceden los límites
        aprendices_cancelados = 0
        
        for aprendiz in aprendices_a_cancelar:
            documento = aprendiz['documento']
            print(f"\nProcesando cancelación de aprendiz: {documento}")
            
            # SOLUCIÓN: Convertir tipos en la verificación también
            sql_verificar = """
            SELECT numeroDocumento, nombres, apellidos, medida_formativa 
            FROM aprendices 
            WHERE CAST(numeroDocumento AS CHAR) = %s
            """
            cursor.execute(sql_verificar, (str(documento),))
            aprendiz_data = cursor.fetchone()
            
            if not aprendiz_data:
                print(f"  ❌ ERROR: No se encontró el aprendiz con documento {documento}")
                continue
            
            nombre_completo = f"{aprendiz_data[1]} {aprendiz_data[2]}"
            medida_formativa_actual = aprendiz_data[3]
            
            print(f"  → Aprendiz encontrado: {nombre_completo}")
            print(f"  → Medida formativa actual: {medida_formativa_actual}")
            
            # Verificar si ya tiene la medida de cancelación asignada
            if medida_formativa_actual == MEDIDA_CANCELACION:
                print(f"  ⚠️  Ya tiene asignada la medida de cancelación")
                continue
            
            # SOLUCIÓN: Convertir tipos en el UPDATE también
            sql_cancelar = """
            UPDATE aprendices 
            SET medida_formativa = %s 
            WHERE CAST(numeroDocumento AS CHAR) = %s
            """
            cursor.execute(sql_cancelar, (MEDIDA_CANCELACION, str(documento)))
            
            if cursor.rowcount > 0:
                aprendices_cancelados += 1
                print(f"  ✅ MEDIDA FORMATIVA DE CANCELACIÓN ASIGNADA EXITOSAMENTE")
                print(f"     Motivos:")
                for motivo in aprendiz['motivos']:
                    print(f"     - {motivo}")
            else:
                print(f"  ❌ No se pudo asignar la medida formativa")
        
        # Confirmar cambios
        conexion.commit()
        
        print("\n" + "=" * 60)
        print(f"Aprendices con medidas formativas revisados: {len(aprendices_con_medidas)}")
        print(f"Aprendices que debían ser cancelados: {len(aprendices_a_cancelar)}")
        print(f"Aprendices con medida de cancelación asignada exitosamente: {aprendices_cancelados}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conexion.rollback()
    
    finally:
        cursor.close()
        conexion.close()


# Se debe tener esta definicion descomentada para que la funcion funcione:
verificar_y_cancelar_aprendices()

""" ====================FIN DE LA FUNCION PARA CANCELAR APRENDICES==================== """


""" =========FUNCION PARA VER LOS APRENDICES CON MEDIDA DE CANCELACION ASIGNADA========= """
@app.route('/mostrar_cancelados', methods=['GET'])
def mostrar_aprendices_recomendados_para_cancelacion():
    if 'logueado' in session and session['logueado']:
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        
        nombre_instructor = f"{nombre_logueado} {apellido_instructor}"
        
        # Consulta unificada usando únicamente la tabla comites con información de fichas
        sql_comites_unificada = """
        SELECT 
            c.usuario_logueado,
            c.ficha, 
            c.nombreFicha,
            c.areaPrograma,
            c.documentoAprendizCitado,
            c.nombreAprendizCitado,
            c.estadoAprendizCitado,
            c.correoAprendizCitado,
            c.telefonoAprendizCitado,
            c.clasificacionComite,
            c.competencia,
            c.resultadoAprendizaje,
            c.nombreCapituloFalla,
            c.calificacionComite,
            c.fechaPresentacionQueja,
            c.fechaAgendacion,
            c.correos,
            c.estadoComite,
            c.articuloFalla,
            c.descripcion,
            c.lugarComite,
            c.informacionArticulo,
            f.nivel_formacion,
            f.modalidad
        FROM comites c 
        INNER JOIN aprendices a ON CAST(c.documentoAprendizCitado AS CHAR) = CAST(a.numeroDocumento AS CHAR)
        INNER JOIN fichas f ON c.ficha = f.numeroFicha
        WHERE c.usuario_logueado = %s 
            AND a.medida_formativa = %s 
            AND c.estadoComite = 'realizado'
        ORDER BY c.fechaAgendacion DESC
        """
        
        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()
            
            # Ejecutar consulta unificada
            cursor.execute(sql_comites_unificada, (nombre_instructor, MEDIDA_CANCELACION))
            comites = cursor.fetchall()
            
            # Agrupar los aprendices por documento
            aprendices_agrupados = {}
            
            # Procesar información de comités
            for comite in comites:
                documento = str(comite[4])  # documentoAprendizCitado
                nombre = comite[5]  # nombreAprendizCitado
                
                if documento not in aprendices_agrupados:
                    aprendices_agrupados[documento] = {
                        'ficha': comite[1],  # c.ficha
                        'programa': comite[2],  # c.nombreFicha
                        'modalidad': comite[23],  # f.modalidad
                        'documento': documento,  # c.documentoAprendizCitado
                        'nombre': nombre,  # c.nombreAprendizCitado
                        'nivel_formacion': comite[22],  # f.nivel_formacion
                        'comites': [],
                        'ultima_fecha': comite[15]  # fechaAgendacion
                    }
                
                # Agregar información del comité al aprendiz
                aprendices_agrupados[documento]['comites'].append({
                    'usuario_logueado': comite[0],
                    'ficha': comite[1],
                    'nombreFicha': comite[2],
                    'areaPrograma': comite[3],
                    'documentoAprendizCitado': comite[4],
                    'nombreAprendizCitado': comite[5],
                    'estadoAprendizCitado': comite[6],
                    'correoAprendizCitado': comite[7],
                    'telefonoAprendizCitado': comite[8],
                    'clasificacionComite': comite[9],
                    'competencia': comite[10],
                    'resultadoAprendizaje': comite[11],
                    'nombreCapituloFalla': comite[12],
                    'calificacionComite': comite[13],
                    'fechaPresentacionQueja': comite[14],
                    'fechaAgendacion': comite[15],
                    'correos': comite[16],
                    'estadoComite': comite[17],
                    'articuloFalla': comite[18],
                    'descripcion': comite[19],
                    'lugarComite': comite[20],
                    'informacionArticulo': comite[21],
                    'nivel_formacion': comite[22],
                    'modalidad': comite[23]
                })
                
                # Actualizar la última fecha (mantener la más reciente)
                if comite[15] > aprendices_agrupados[documento]['ultima_fecha']:
                    aprendices_agrupados[documento]['ultima_fecha'] = comite[15]
            
            cursor.close()
            
        except Exception as e:
            print(f"Error en la consulta: {e}")
            aprendices_agrupados = {}
        
        return render_template('instructor/recomendacion_cancelacion.html',
                             aprendices_agrupados=aprendices_agrupados,
                             nombre_instructor=nombre_instructor)
    else:
        return redirect(url_for('login'))




"""============================↓↓↓↓↓ BORRADOR DE ACTAS ↓↓↓↓↓================================"""
#citados, situacion, condiciones


from flask import Flask, render_template, send_file, flash, redirect, url_for, session
import sqlite3  # Cambia por tu driver de BD (pymysql, psycopg2, etc.)
from docx import Document
from docx.shared import Inches
from datetime import datetime
import os
import tempfile


def consultar_datos():
    """Ejecuta la consulta SQL y retorna los datos"""
    # Verificar que el usuario esté logueado
    if 'nombre' not in session or 'apellido' not in session:
        return None
    
    # Obtener datos del usuario logueado
    nombre_logueado = session['nombre']
    apellido_instructor = session['apellido']
    usuario_logueado = f"{nombre_logueado} {apellido_instructor}"
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Consulta para obtener comités agendados del coordinador logueado
        sql = """
           SELECT ficha, nombreFicha, documentoAprendizCitado, nombreAprendizCitado, 
                  telefonoAprendizCitado, correoAprendizCitado, estadoAprendizCitado 
           FROM comites 
           WHERE estadoComite = 'agendado' AND usuario_logueado = %s
           ORDER BY ficha, nombreAprendizCitado
        """
        
        cursor.execute(sql, (usuario_logueado,))
        datos = cursor.fetchall()
        
        # Convertir a lista de diccionarios para facilitar manejo
        columnas = [desc[0] for desc in cursor.description]
        resultado = []
        for fila in datos:
            resultado.append(dict(zip(columnas, fila)))
            
        return resultado
        
    except Exception as e:
        print(f"Error en consulta: {e}")
        return None
    finally:
        conn.close()





def consultar_datos_coordinador():
    """Ejecuta la consulta SQL y retorna los datos para coordinadores"""
    # Verificar que el usuario esté logueado
    if 'nombre' not in session or 'apellido' not in session:
        return None
        
    # Obtener datos del usuario logueado
    nombre_logueado = session['nombre']
    apellido_coordinador = session['apellido']
    coordinador_logueado = f"{nombre_logueado} {apellido_coordinador}"
        
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
                
        # Consulta para obtener comités agendados del COORDINADOR logueado
        # Hacemos JOIN entre comites y fichas usando el numero de ficha
        sql = """
           SELECT c.ficha, c.nombreFicha, c.documentoAprendizCitado, c.nombreAprendizCitado,
                  c.telefonoAprendizCitado, c.correoAprendizCitado, c.estadoAprendizCitado
           FROM comites c
           INNER JOIN fichas f ON c.ficha = f.numeroFicha
           WHERE c.estadoComite = 'agendado' AND f.nombreCoordinador = %s
           ORDER BY c.ficha, c.nombreAprendizCitado
        """
                
        cursor.execute(sql, (coordinador_logueado,))
        datos = cursor.fetchall()
                
        # Convertir a lista de diccionarios para facilitar manejo
        columnas = [desc[0] for desc in cursor.description]
        resultado = []
        for fila in datos:
            resultado.append(dict(zip(columnas, fila)))
                    
        return resultado
            
    except Exception as e:
        print(f"Error en consulta: {e}")
        return None
    finally:
        conn.close()



def eliminar_duplicados(datos):
    """Elimina aprendices duplicados basándose en el documento"""
    if not datos:
        return []
    
    aprendices_unicos = {}
    for registro in datos:
        documento = registro.get('documentoAprendizCitado', '')
        # Solo mantener el primer registro de cada documento
        if documento and documento not in aprendices_unicos:
            aprendices_unicos[documento] = registro
    
    return list(aprendices_unicos.values())

def agrupar_por_ficha(datos):
    """Agrupa los datos por ficha y elimina duplicados"""
    if not datos:
        return {}
    
    fichas_agrupadas = {}
    for registro in datos:
        ficha = registro.get('ficha', 'Desconocida')
        if ficha not in fichas_agrupadas:
            fichas_agrupadas[ficha] = []
        fichas_agrupadas[ficha].append(registro)
    
    # Eliminar duplicados en cada ficha
    for ficha in fichas_agrupadas:
        fichas_agrupadas[ficha] = eliminar_duplicados(fichas_agrupadas[ficha])
    
    return fichas_agrupadas

def crear_documento_word_por_ficha(datos_ficha, usuario_logueado, ficha, nombre_ficha):
    """Crea un documento Word para una ficha específica"""
    if not datos_ficha:
        return None

    doc = Document()
    doc.add_heading('Reporte de Aprendices Citados', 0).alignment = 1

    doc.add_paragraph(f'Instructor: {usuario_logueado}')
    doc.add_paragraph(f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    doc.add_paragraph('')

    # Información de la ficha
    doc.add_heading(f'Ficha: {ficha} - {nombre_ficha}', level=2)
    doc.add_paragraph('')  # Espacio

    # PRIMERA TABLA: Información de contacto de aprendices
    doc.add_heading('1. Información de Contacto de Aprendices', level=3)
    columnas = ['documentoAprendizCitado', 'nombreAprendizCitado', 'telefonoAprendizCitado', 'correoAprendizCitado', 'estadoAprendizCitado']
    tabla1 = doc.add_table(rows=1, cols=len(columnas))
    tabla1.style = 'Light Grid Accent 1'

    # Encabezados de la primera tabla
    encabezado1 = tabla1.rows[0].cells
    encabezados_nombres1 = ['DOCUMENTO', 'NOMBRE', 'TELÉFONO', 'CORREO', 'ESTADO']
    for i, nombre in enumerate(encabezados_nombres1):
        encabezado1[i].text = nombre
        for p in encabezado1[i].paragraphs:
            for run in p.runs:
                run.bold = True

    # Agregar filas de datos a la primera tabla
    for reg in datos_ficha:
        fila1 = tabla1.add_row().cells
        for i, col in enumerate(columnas):
            fila1[i].text = str(reg.get(col, '') or '')

    doc.add_paragraph('')  # Espacio entre tablas

    # SEGUNDA TABLA: Documento, Nombre y Situación
    doc.add_heading('2. Situación de Aprendices', level=3)
    tabla2 = doc.add_table(rows=1, cols=3)
    tabla2.style = 'Light Grid Accent 1'

    # Encabezados de la segunda tabla
    encabezado2 = tabla2.rows[0].cells
    encabezados_nombres2 = ['DOCUMENTO', 'NOMBRE COMPLETO', 'SITUACIÓN']
    for i, nombre in enumerate(encabezados_nombres2):
        encabezado2[i].text = nombre
        for p in encabezado2[i].paragraphs:
            for run in p.runs:
                run.bold = True

    # Agregar filas de datos a la segunda tabla
    for reg in datos_ficha:
        fila2 = tabla2.add_row().cells
        fila2[0].text = str(reg.get('documentoAprendizCitado', '') or '')
        fila2[1].text = str(reg.get('nombreAprendizCitado', '') or '')
        fila2[2].text = ''  # Vacío para rellenar manualmente

    doc.add_paragraph('')  # Espacio entre tablas

    # TERCERA TABLA: Calificación y Medidas Formativas
    doc.add_heading('3. Calificación y Medidas Formativas', level=3)
    
    # Agregar explicación de siglas
    doc.add_paragraph(
         'Siglas medidas formativas:\n'
    'Felicitación escrita: F.E\n'
    'Levantar condicionamiento: L.C\n'
    'Llamado de atención verbal: A.V\n'
    'Llamado de atención por escrito: A.E\n'
    'Plan de mejoramiento académico: M.A\n'
    'Plan de mejoramiento disciplinario: M.D\n'
    'Condicionamiento de matrícula: C.M\n'
    'Cancelación de registro: C.R'
    )
    doc.add_paragraph('')
    doc.add_paragraph('')
    doc.add_paragraph('')
    # Crear tabla con medidas formativas (11 columnas: Documento, Nombre, Calificación, + 8 siglas)
    siglas = ['F.E', 'L.C', 'A.V', 'A.E', 'M.A', 'M.D', 'C.M', 'C.R']
    num_columnas = 3 + len(siglas)  # Documento + Nombre + Calificación + 8 siglas
    tabla3 = doc.add_table(rows=1, cols=num_columnas)
    tabla3.style = 'Light Grid Accent 1'

    # Encabezados de la tercera tabla
    encabezado3 = tabla3.rows[0].cells
    encabezado3[0].text = 'DOCUMENTO'
    encabezado3[1].text = 'NOMBRE COMPLETO'
    encabezado3[2].text = 'CALIFICACIÓN'
    
    # Agregar encabezados de siglas
    for i, sigla in enumerate(siglas):
        encabezado3[3 + i].text = sigla
    
    # Hacer negrita todos los encabezados
    for celda in encabezado3:
        for p in celda.paragraphs:
            for run in p.runs:
                run.bold = True

    # Agregar filas de datos a la tercera tabla
    for reg in datos_ficha:
        fila3 = tabla3.add_row().cells
        fila3[0].text = str(reg.get('documentoAprendizCitado', '') or '')
        fila3[1].text = str(reg.get('nombreAprendizCitado', '') or '')
        fila3[2].text = ''  # Vacío para rellenar manualmente (calificación)
        
        # Dejar vacías las celdas de siglas para marcar con X
        for i in range(len(siglas)):
            fila3[3 + i].text = ''

    # Ajustar ancho de columnas para las siglas (más pequeñas)
    from docx.shared import Inches
    for i in range(len(siglas)):
        for row in tabla3.rows:
            row.cells[3 + i].width = Inches(0.4)

    doc.add_page_break()
    doc.add_heading('Resumen del Reporte', level=1)
    doc.add_paragraph(f'Ficha: {ficha} - {nombre_ficha}')
    doc.add_paragraph(f'Total de aprendices citados: {len(datos_ficha)}')
    doc.add_paragraph('')
    doc.add_paragraph('Tablas incluidas:')
    doc.add_paragraph('1. Información de contacto completa')
    doc.add_paragraph('2. Situación de aprendices (para rellenar manualmente)')
    doc.add_paragraph('3. Calificación y medidas formativas (para rellenar manualmente)')
    doc.add_paragraph('')
    doc.add_paragraph('Generado automáticamente por el sistema.')

    return doc

@app.route('/word')
def index2():
    """Página principal con el botón"""
    return render_template('instructor/borrador_acta.html')


@app.route('/word2')
def index3():
    """Página principal con el botón de coordinador"""
    return render_template('instructor/borrador_acta.html')




@app.route('/generar_reporte')
def generar_reporte():
    """Ruta que ejecuta la consulta y genera un Word por cada ficha"""
    try:
        # Verificar que el usuario esté logueado
        if 'nombre' not in session or 'apellido' not in session:
            flash('Debes estar logueado para generar reportes', 'error')
            return redirect(url_for('index2'))
        
        # Obtener nombre completo del usuario
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        usuario_logueado = f"{nombre_logueado} {apellido_instructor}"
        
        # Consultar datos
        datos = consultar_datos()
        
        if datos is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('index2'))
        
        if not datos:
            flash(f'No se encontraron comités agendados para {usuario_logueado}', 'error')
            return redirect(url_for('index2'))
        
        # Agrupar datos por ficha
        fichas_agrupadas = agrupar_por_ficha(datos)
        
        # Ruta dinámica al Escritorio del usuario que corre Flask
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        carpeta_destino = os.path.join(escritorio, "reportes_comites")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_generados = []
        
        # Generar un documento por cada ficha
        for ficha, datos_ficha in fichas_agrupadas.items():
            # Obtener el nombre de la ficha del primer registro
            nombre_ficha = datos_ficha[0].get('nombreFicha', 'Desconocido')
            
            # Crear documento para esta ficha
            documento = crear_documento_word_por_ficha(datos_ficha, usuario_logueado, ficha, nombre_ficha)
            
            if documento:
                # Limpiar nombre de ficha para usar en el archivo (remover caracteres especiales)
                nombre_ficha_limpio = "".join(c for c in nombre_ficha if c.isalnum() or c in (' ', '-', '_')).rstrip()
                usuario_limpio = usuario_logueado.replace(" ", "_")
                
                # Nombre del archivo con ficha y nombre de ficha
                nombre_archivo = f'Borrador_acta_Ficha_{ficha}_{nombre_ficha_limpio}_{usuario_limpio}_{timestamp}.docx'
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
                
                # Guardar el documento
                documento.save(ruta_completa)
                archivos_generados.append({
                    'ficha': ficha,
                    'nombre_ficha': nombre_ficha,
                    'ruta': ruta_completa,
                    'nombre_archivo': nombre_archivo,
                    'cantidad_aprendices': len(datos_ficha)
                })
        
        # Mensaje de éxito con información de todos los archivos generados
        mensaje_exito = f'Se generaron {len(archivos_generados)} reportes exitosamente:__'
        for archivo in archivos_generados:
            mensaje_exito += f'• Ficha {archivo["ficha"]} ({archivo["nombre_ficha"]}): {archivo["cantidad_aprendices"]} aprendices__'
        mensaje_exito += f'__Archivos guardados en: {carpeta_destino}'
        
        flash(mensaje_exito, 'success')
        
        # Si solo hay un archivo, enviarlo para descarga
        # Si hay múltiples, el usuario puede ir a la carpeta para descargarlos
        if len(archivos_generados) == 1:
            return send_file(
                archivos_generados[0]['ruta'],
                as_attachment=True,
                download_name=archivos_generados[0]['nombre_archivo'],
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            return redirect(url_for('index2'))
        
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('index2'))





@app.route('/generar_reporte_coordinador')
def generar_reporte_coordinador():
    """Ruta que ejecuta la consulta y genera un Word por cada ficha"""
    try:
        # Verificar que el usuario esté logueado
        if 'nombre' not in session or 'apellido' not in session:
            flash('Debes estar logueado para generar reportes', 'error')
            return redirect(url_for('index2'))
        
        # Obtener nombre completo del usuario
        nombre_logueado = session['nombre']
        apellido_instructor = session['apellido']
        usuario_logueado = f"{nombre_logueado} {apellido_instructor}"
        
        # Consultar datos
        datos = consultar_datos_coordinador()
        
        if datos is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('index3'))
        
        if not datos:
            flash(f'No se encontraron comités agendados para {usuario_logueado}', 'error')
            return redirect(url_for('index3'))
        
        # Agrupar datos por ficha
        fichas_agrupadas = agrupar_por_ficha(datos)
        
        # Ruta dinámica al Escritorio del usuario que corre Flask
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        carpeta_destino = os.path.join(escritorio, "reportes_comites")
        os.makedirs(carpeta_destino, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_generados = []
        
        # Generar un documento por cada ficha
        for ficha, datos_ficha in fichas_agrupadas.items():
            # Obtener el nombre de la ficha del primer registro
            nombre_ficha = datos_ficha[0].get('nombreFicha', 'Desconocido')
            
            # Crear documento para esta ficha
            documento = crear_documento_word_por_ficha(datos_ficha, usuario_logueado, ficha, nombre_ficha)
            
            if documento:
                # Limpiar nombre de ficha para usar en el archivo (remover caracteres especiales)
                nombre_ficha_limpio = "".join(c for c in nombre_ficha if c.isalnum() or c in (' ', '-', '_')).rstrip()
                usuario_limpio = usuario_logueado.replace(" ", "_")
                
                # Nombre del archivo con ficha y nombre de ficha
                nombre_archivo = f'Borrador_acta_Ficha_{ficha}_{nombre_ficha_limpio}_{usuario_limpio}_{timestamp}.docx'
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
                
                # Guardar el documento
                documento.save(ruta_completa)
                archivos_generados.append({
                    'ficha': ficha,
                    'nombre_ficha': nombre_ficha,
                    'ruta': ruta_completa,
                    'nombre_archivo': nombre_archivo,
                    'cantidad_aprendices': len(datos_ficha)
                })
        
        # Mensaje de éxito con información de todos los archivos generados
        mensaje_exito = f'Se generaron {len(archivos_generados)} reportes exitosamente:__'
        for archivo in archivos_generados:
            mensaje_exito += f'• Ficha {archivo["ficha"]} ({archivo["nombre_ficha"]}): {archivo["cantidad_aprendices"]} aprendices__'
        mensaje_exito += f'__Archivos guardados en: {carpeta_destino}'
        
        flash(mensaje_exito, 'success')
        
        # Si solo hay un archivo, enviarlo para descarga
        # Si hay múltiples, el usuario puede ir a la carpeta para descargarlos
        if len(archivos_generados) == 1:
            return send_file(
                archivos_generados[0]['ruta'],
                as_attachment=True,
                download_name=archivos_generados[0]['nombre_archivo'],
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            return redirect(url_for('index2'))
        
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('index2'))












@app.teardown_request
def limpiar_temporales(exception):
    """Función mantenida para compatibilidad"""
    pass


@app.route("/agendado_lote", methods=['POST'])
def agendado_lote_route():
    try:
        # Recoger los IDs de los comités y la fecha del formulario
        comite_ids = request.form.getlist('comite_ids')
        fecha_agendacion = request.form['agendar_fecha']
        lugar_enlace = request.form.get('lugar/enlace', '')
        
        print(f"IDs de comités recibidos: {comite_ids}")
        print(f"Fecha recibida: {fecha_agendacion}")
        print(f"Lugar/enlace recibido: {lugar_enlace}")
        
        # Validar que se recibieron comités
        if not comite_ids:
            flash('No se seleccionaron comités para agendar', 'error')
            return redirect('/mostrar_solicitados')
        
        # Establecer la configuración regional en español (si está disponible)
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            # Si no está disponible el locale español, continuar sin él
            pass
        
        # Ajustar el formato de la cadena de fecha y hora
        fecha_agendacion = fecha_agendacion.replace('T', ' ')
        
        # Convertir la fecha a un objeto datetime
        formato = "%Y-%m-%d %H:%M"
        datetime_fecha = datetime.strptime(fecha_agendacion, formato)
        print(f"Fecha convertida: {datetime_fecha}")
        
        # Formatear la fecha como necesites
        fecha_formateada = datetime_fecha
        print(f"Fecha formateada: {fecha_formateada}")
        
        # Llamar a la función 'agendado_lote' con los datos
        agendado_lote(comite_ids, fecha_formateada, lugar_enlace)
        
        flash(f'Se agendaron {len(comite_ids)} comités exitosamente para el {fecha_formateada}', 'success')
        
        # Redireccionar a la página mostrar_agendados
        return redirect('/mostrar_agendados')
        
    except ValueError as ve:
        print(f"Error de formato de fecha: {ve}")
        flash('Error en el formato de la fecha proporcionada', 'error')
        return redirect('/mostrar_solicitados')
        
    except Exception as e:
        print(f"Error al agendar el lote: {e}")
        flash(f'Error al agendar el lote de comités: {str(e)}', 'error')
        return redirect('/mostrar_solicitados')

@app.route("/rechazar_lote", methods=['POST'])
def rechazar_lote_route():
    try:
        # Recoger los IDs de los comités
        comite_ids = request.form.getlist('comite_ids')
        
        print(f"IDs de comités a rechazar: {comite_ids}")
        
        # Validar que se recibieron comités
        if not comite_ids:
            flash('No se seleccionaron comités para rechazar', 'error')
            return redirect('/mostrar_solicitados')
        
        # Llamar a la función 'rechazar_lote' con los datos
        rechazar_lote(comite_ids)
        
        flash(f'Se rechazaron {len(comite_ids)} comités exitosamente', 'success')
        
        # Redireccionar a la página mostrar_solicitados
        return redirect('/mostrar_solicitados')
        
    except Exception as e:
        print(f"Error al rechazar el lote: {e}")
        flash(f'Error al rechazar el lote de comités: {str(e)}', 'error')
        return redirect('/mostrar_solicitados')





@app.route("/reagendado_lote", methods=['POST'])
def reagendado_lote():
    try:
        # Recoger los IDs de los comités y la fecha del formulario
        comite_ids = request.form.getlist('comite_ids')
        fecha_agendacion = request.form['agendar_fecha']
        lugar_enlace = request.form.get('lugar/enlace', '')
        
        print(f"IDs de comités recibidos: {comite_ids}")
        print(f"Fecha recibida: {fecha_agendacion}")
        print(f"Lugar/enlace recibido: {lugar_enlace}")
        
        # Validar que se recibieron comités
        if not comite_ids:
            flash('No se seleccionaron comités para agendar', 'error')
            return redirect('/mostrar_solicitados')
        
        # Establecer la configuración regional en español (si está disponible)
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            # Si no está disponible el locale español, continuar sin él
            pass
        
        # Ajustar el formato de la cadena de fecha y hora
        fecha_agendacion = fecha_agendacion.replace('T', ' ')
        
        # Convertir la fecha a un objeto datetime
        formato = "%Y-%m-%d %H:%M"
        datetime_fecha = datetime.strptime(fecha_agendacion, formato)
        print(f"Fecha convertida: {datetime_fecha}")
        
        # Formatear la fecha como necesites
        fecha_formateada = datetime_fecha
        print(f"Fecha formateada: {fecha_formateada}")
        
        # Llamar a la función 'agendado_lote' con los datos
        F_reagendado_lote(comite_ids, fecha_formateada, lugar_enlace)
        
        flash(f'Se agendaron {len(comite_ids)} comités exitosamente para el {fecha_formateada}', 'success')
        
        # Redireccionar a la página mostrar_agendados
        return redirect('/mostrar_agendados')
        
    except ValueError as ve:
        print(f"Error de formato de fecha: {ve}")
        flash('Error en el formato de la fecha proporcionada', 'error')
        return redirect('/mostrar_solicitados')
        
    except Exception as e:
        print(f"Error al agendar el lote: {e}")
        flash(f'Error al agendar el lote de comités: {str(e)}', 'error')
        return redirect('/mostrar_solicitados')



@app.route('/agendado_lote_multiple', methods=['POST'])
def agendado_lote_multiple():
    # Manejar el agendado de múltiples lotes
    comite_ids = request.form.getlist('comite_ids')
    fecha = request.form.get('agendar_fecha')
    lugar = request.form.get('lugar/enlace')
    
    try:
        # Recoger los IDs de los comités y la fecha del formulario
        comite_ids = request.form.getlist('comite_ids')
        fecha_agendacion = request.form['agendar_fecha']
        lugar_enlace = request.form.get('lugar/enlace', '')
        
        print(f"IDs de comités recibidos: {comite_ids}")
        print(f"Fecha recibida: {fecha_agendacion}")
        print(f"Lugar/enlace recibido: {lugar_enlace}")
        
        # Validar que se recibieron comités
        if not comite_ids:
            flash('No se seleccionaron comités para agendar', 'error')
            return redirect('/mostrar_solicitados')
        
        # Establecer la configuración regional en español (si está disponible)
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            # Si no está disponible el locale español, continuar sin él
            pass
        
        # Ajustar el formato de la cadena de fecha y hora
        fecha_agendacion = fecha_agendacion.replace('T', ' ')
        
        # Convertir la fecha a un objeto datetime
        formato = "%Y-%m-%d %H:%M"
        datetime_fecha = datetime.strptime(fecha_agendacion, formato)
        print(f"Fecha convertida: {datetime_fecha}")
        
        # Formatear la fecha como necesites
        fecha_formateada = datetime_fecha
        print(f"Fecha formateada: {fecha_formateada}")
        
        # Llamar a la función 'agendado_lote' con los datos
        agendado_lote(comite_ids, fecha_formateada, lugar_enlace)
        
        flash(f'Se agendaron {len(comite_ids)} comités exitosamente para el {fecha_formateada}', 'success')
        
        # Redireccionar a la página mostrar_agendados
        return redirect('/mostrar_agendados')
        
    except ValueError as ve:
        print(f"Error de formato de fecha: {ve}")
        flash('Error en el formato de la fecha proporcionada', 'error')
        return redirect('/mostrar_solicitados')
        
    except Exception as e:
        print(f"Error al agendar el lote: {e}")
        flash(f'Error al agendar el lote de comités: {str(e)}', 'error')
    return redirect('/mostrar_agendados') # o donde quieras redirigir

@app.route('/rechazar_lote_multiple', methods=['POST'])
def rechazar_lote_multiple():
    # Manejar el rechazo de múltiples lotes
    comite_ids = request.form.getlist('comite_ids')
    
    try:
            # Recoger los IDs de los comités
            comite_ids = request.form.getlist('comite_ids')
            
            print(f"IDs de comités a rechazar: {comite_ids}")
            
            # Validar que se recibieron comités
            if not comite_ids:
                flash('No se seleccionaron comités para rechazar', 'error')
                return redirect('/mostrar_solicitados')
            
            # Llamar a la función 'rechazar_lote' con los datos
            rechazar_lote(comite_ids)
            
            flash(f'Se rechazaron {len(comite_ids)} comités exitosamente', 'success')
            
            # Redireccionar a la página mostrar_solicitados
            return redirect('/mostrar_solicitados')
    except Exception as e:
        print(f"Error al rechazar el lote: {e}")
        flash(f'Error al rechazar el lote de comités: {str(e)}', 'error')
    return redirect('/mostrar_solicitados') # o donde quieras redirigir



@app.route('/rechazar_lote_multiple_agendados', methods=['POST'])
def rechazar_lote_multiple_agendados():
    # Manejar el rechazo de múltiples lotes
    comite_ids = request.form.getlist('comite_ids')
    
    try:
            # Recoger los IDs de los comités
            comite_ids = request.form.getlist('comite_ids')
            
            print(f"IDs de comités a rechazar: {comite_ids}")
            
            # Validar que se recibieron comités
            if not comite_ids:
                flash('No se seleccionaron comités para rechazar', 'error')
                return redirect('/mostrar_agendados')
            
            # Llamar a la función 'rechazar_lote' con los datos
            rechazar_lote(comite_ids)
            
            flash(f'Se rechazaron {len(comite_ids)} comités exitosamente', 'success')
            
            # Redireccionar a la página mostrar_solicitados
            return redirect('/mostrar_agendados')
    except Exception as e:
        print(f"Error al rechazar el lote: {e}")
        flash(f'Error al rechazar el lote de comités: {str(e)}', 'error')
    return redirect('/mostrar_agendados')



@app.route('/reagendado_lote_multiple', methods=['POST'])
def reagendado_lote_multiple():

    
   
    try:
        # Recoger los datos del formulario
        comite_ids = request.form.getlist('comite_ids')
        fecha_agendacion = request.form.get('agendar_fecha')
        lugar_enlace = request.form.get('lugar/enlace', '')
        
        # Logging para debugging
        print(f"=== REAGENDADO MÚLTIPLE ===")
        print(f"IDs de comités recibidos: {comite_ids}")
        print(f"Cantidad de comités: {len(comite_ids)}")
        print(f"Fecha recibida: {fecha_agendacion}")
        print(f"Lugar/enlace recibido: {lugar_enlace}")
        
        # Validaciones básicas
        if not comite_ids:
            flash('No se seleccionaron comités para reagendar', 'error')
            return redirect('/mostrar_agendados')
        
        if not fecha_agendacion:
            flash('No se proporcionó una fecha para reagendar', 'error')
            return redirect('/mostrar_agendados')
        
        if not lugar_enlace.strip():
            flash('No se proporcionó un lugar/enlace para reagendar', 'error')
            return redirect('/mostrar_agendados')
        
        # Limpiar y validar los IDs de comités
        comite_ids = [id.strip() for id in comite_ids if id.strip()]
        if not comite_ids:
            flash('No se encontraron IDs de comités válidos', 'error')
            return redirect('/mostrar_agendados')
        
        # Configurar locale para español si está disponible
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es_ES')
            except locale.Error:
                pass  # Continuar sin locale español
        
        # Procesar la fecha
        fecha_agendacion = fecha_agendacion.replace('T', ' ')
        
        try:
            datetime_fecha = datetime.strptime(fecha_agendacion, "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Formato de fecha inválido. Use el formato correcto.', 'error')
            return redirect('/mostrar_agendados')
        
        # Validar que la fecha no sea en el pasado
        if datetime_fecha < datetime.now():
            flash('No se puede reagendar para una fecha en el pasado', 'error')
            return redirect('/mostrar_agendados')
        
        print(f"Fecha procesada: {datetime_fecha}")
        
        # Llamar a la función mejorada de reagendado
        resultado = reagendado_lote_multiple_mejorado(comite_ids, datetime_fecha, lugar_enlace)
        
        # Generar mensajes de resultado
        if resultado['exito'] > 0:
            mensaje_exito = f'Se reagendaron {resultado["exito"]} comités exitosamente'
            if resultado['fallidos'] > 0:
                mensaje_exito += f' (no se pudieron reagendar {resultado["fallidos"]} comités)'
            flash(mensaje_exito, 'success')
        else:
            flash('No se pudo reagendar ningún comité', 'error')
        
        if resultado['fallidos'] > 0:
            flash(f'Comités que no se pudieron reagendar: {", ".join(map(str, resultado["ids_fallidos"]))}', 'warning')
        
        return redirect('/mostrar_agendados')
        
    except ValueError as ve:
        print(f"Error de validación: {ve}")
        flash(f'Error de validación: {str(ve)}', 'error')
        return redirect('/mostrar_agendados')
    
    except Exception as e:
        print(f"Error inesperado al reagendar lotes múltiples: {e}")
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect('/mostrar_agendados')





if __name__ == '__main__':
    app.run(debug=True)# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←  
    #app.run(host="0.0.0.0", port=5000)#←REEMPLAZAR POR ↑↑       #enlace para que otros en la misma red prueben CESCAB http://192.168.137.1:5000