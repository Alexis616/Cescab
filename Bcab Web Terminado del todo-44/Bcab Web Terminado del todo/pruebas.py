import mysql.connector

def get_db_connection():
      mydb = mysql.connector.connect(
        host='localhost', #85.31.231.136
        user='root',    #bcab
        password='', #Bc4b
        database='bcab2'        
    )           
      return mydb

def consulta_instructor_agendados():
    conexion = get_db_connection()
    cursor = conexion.cursor()
    sql = "SELECT alias_ficha, id_ficha, fecha_agendacion FROM comite WHERE estado = 'agendado'"
    cursor.execute(sql)
    agendados = cursor.fetchall()
    conexion.commit()
    return agendados

# Llama a la función mostrar_solicitud() y almacena los datos devueltos en una variable
datos_solicitud = consulta_instructor_agendados()

# Verifica si se obtuvieron datos
if datos_solicitud:
    print("Datos de solicitud obtenidos correctamente:")
    # Itera sobre los datos e imprímelos
    for solicitud in datos_solicitud:
        print(solicitud)
else:
    print("No se obtuvieron datos de solicitud.")



# Llama a la función mostrar_solicitud() y almacena los datos devueltos en una variable
def consulta_instructor_solicitado():
    conexion = get_db_connection()
    cursor = conexion.cursor()
    sql = "SELECT alias_ficha, id_ficha, fecha_hora_formateada FROM comite WHERE estado = 'solicitud' AND nombre_instructor = 'Juan Carlos Posada'"
    cursor.execute(sql)
    solicitados = cursor.fetchall()
    conexion.commit()
    return solicitados

agenda =  consulta_instructor_solicitado()

# Verifica si se obtuvieron datos
if agenda:
    print("Datos de solicitud obtenidos correctamente:")
    # Itera sobre los datos e imprímelos
    for solicitud in agenda:
        print(solicitud)
else:
    print("No se obtuvieron datos de solicitud.")

#instalador de notify ↓↓↓
# pip install notify-py