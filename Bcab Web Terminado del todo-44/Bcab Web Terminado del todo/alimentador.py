from flask import Blueprint, request, render_template, current_app
import os
import pymysql
from conexion import get_db_connection


alimentador = Blueprint('alimentador', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# RUTA ORIGINAL PARA JUICIOS EVALUATIVOS 
@alimentador.route('/alimentador', methods=['GET', 'POST'])
def alimentador_index():
    if request.method == 'POST':
        total_cols = int(request.form['total_cols'])
        tabla = request.form['tabla']
        columnas_raw = request.form.get('columnas', '').strip().splitlines()

        mapeo = {}
        for linea in columnas_raw:
            if ':' in linea:
                csv_col, campo_db = linea.split(':')
                mapeo[int(csv_col.strip())] = campo_db.strip()

        if not mapeo:
            return "No se definieron asociaciones válidas entre columnas y campos de BD.", 400

        archivos_subidos = request.files.getlist('file')
        for archivo in archivos_subidos:
            if archivo and archivo.filename.endswith('.csv'):
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
                archivo.save(path)
                procesar_csv(path, total_cols, mapeo, tabla)

        return f"{len(archivos_subidos)} archivos procesados con éxito."

    return render_template('alimentador.html')


def procesar_csv(path_archivo, total_cols, mapeo, tabla):
    columnas_csv = ', '.join([f"@col{i}" for i in range(1, total_cols + 1)])
    columnas_temp = ', '.join([campo for _, campo in sorted(mapeo.items())])
    set_clauses = ', '.join([f"{campo} = TRIM(BOTH '\"' FROM @col{col})" for col, campo in mapeo.items()])

    path_archivo_sql = path_archivo.replace("\\", "/")
    tabla_temporal = f"{tabla}_tmp"

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Crear tabla temporal
        campos_sql = ', '.join([f"{campo} TEXT" for _, campo in sorted(mapeo.items())])
        cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
        cur.execute(f"CREATE TABLE {tabla_temporal} ({campos_sql})")

        # 2. Cargar datos en la tabla temporal
        sql_load = f"""
        LOAD DATA LOCAL INFILE '{path_archivo_sql}'
        INTO TABLE {tabla_temporal}
        FIELDS TERMINATED BY ',' ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 13 ROWS
        ({columnas_csv})
        SET {set_clauses};
        """
        cur.execute(sql_load)

        # 3. Verificar columnas disponibles en la tabla temporal
        cur.execute(f"SHOW COLUMNS FROM {tabla_temporal}")
        columnas_disponibles = [row[0] for row in cur.fetchall()]

        # 4. Determinar campo identificador
        identificadores_por_tabla = {
            'aprendices': 'numeroDocumento',
            'fichas': 'numeroFicha',
            'juicios_evaluativos': 'documentoIdentidad',
            'comites': 'id',
            'usuarios': 'id'
        }

        campo_identificador = identificadores_por_tabla.get(tabla)

        if campo_identificador and campo_identificador in columnas_disponibles:
            cur.execute(f"SELECT DISTINCT {campo_identificador} FROM {tabla_temporal}")
            valores = [row[0] for row in cur.fetchall()]
            if valores:
                format_strings = ','.join(['%s'] * len(valores))
                sql_delete = f"DELETE FROM {tabla} WHERE {campo_identificador} IN ({format_strings})"
                cur.execute(sql_delete, valores)

        elif columnas_disponibles:
            # Si no hay identificador definido o no está en la tabla, usar el primer campo disponible
            primer_campo = columnas_disponibles[0]
            cur.execute(f"SELECT DISTINCT {primer_campo} FROM {tabla_temporal}")
            valores = [row[0] for row in cur.fetchall()]
            if valores:
                format_strings = ','.join(['%s'] * len(valores))
                sql_delete = f"DELETE FROM {tabla} WHERE {primer_campo} IN ({format_strings})"
                cur.execute(sql_delete, valores)

        # 5. Insertar nuevos registros
        sql_insert = f"""
        INSERT INTO {tabla} ({columnas_temp})
        SELECT {columnas_temp} FROM {tabla_temporal};
        """
        cur.execute(sql_insert)

        conn.commit()
    except Exception as e:
        print(f"Error en procesar_csv: {e}")
        conn.rollback()
        raise
    finally:
        cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
        cur.close()
        conn.close()



# NUEVA RUTA PARA FICHAS
@alimentador.route('/alimentador_fichas', methods=['GET', 'POST'])
def alimentador_fichas():
    if request.method == 'POST':
        total_cols = int(request.form['total_cols'])
        columnas_raw = request.form.get('columnas', '').strip().splitlines()
        
        mapeo = {}
        for linea in columnas_raw:
            if ':' in linea:
                csv_col, campo_db = linea.split(':')
                mapeo[int(csv_col.strip())] = campo_db.strip()
        
        if not mapeo:
            return "No se definieron asociaciones válidas entre columnas y campos de BD.", 400
        
        archivos_subidos = request.files.getlist('file')
        for archivo in archivos_subidos:
            if archivo and archivo.filename.endswith('.csv'):
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
                archivo.save(path)
                procesar_csv_fichas(path, total_cols, mapeo)
        
        return f"{len(archivos_subidos)} archivos procesados con éxito."
    
    return render_template('alimentador_fichas.html')

def procesar_csv_fichas(path_archivo, total_cols, mapeo):
    columnas_csv = ', '.join([f"@col{i}" for i in range(1, total_cols + 1)])
    columnas_temp = ', '.join([campo for _, campo in sorted(mapeo.items())])
    set_clauses = ', '.join([f"{campo} = TRIM(BOTH '\"' FROM @col{col})" for col, campo in mapeo.items()])
    
    path_archivo_sql = path_archivo.replace("\\", "/")
    tabla_temporal = "fichas_tmp"
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Crear tabla temporal
        campos_sql = ', '.join([f"{campo} TEXT" for _, campo in sorted(mapeo.items())])
        cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
        cur.execute(f"CREATE TABLE {tabla_temporal} ({campos_sql})")
        
        # 2. Cargar datos en la tabla temporal
        sql_load = f"""
        LOAD DATA LOCAL INFILE '{path_archivo_sql}'
        INTO TABLE {tabla_temporal}
        FIELDS TERMINATED BY ',' ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
        ({columnas_csv})
        SET {set_clauses};
        """
        cur.execute(sql_load)
        
        # 3. Deduplicar fichas por numeroFicha (conservar solo una por cada ficha)
        deduplicated_view = f"""
        SELECT * FROM (
            SELECT {columnas_temp},
                   ROW_NUMBER() OVER (PARTITION BY numeroFicha ORDER BY numeroFicha) AS rn
            FROM {tabla_temporal}
        ) AS sub
        WHERE rn = 1
        """
        
        # 4. Obtener lista de numeroFicha únicas del CSV deduplicado
        cur.execute(f"SELECT DISTINCT numeroFicha FROM ({deduplicated_view}) AS fichas_dedup")
        fichas = [row[0] for row in cur.fetchall()]
        
        if fichas:
            # 5. Borrar en la tabla principal todas las que se reemplazarán
            format_strings = ','.join(['%s'] * len(fichas))
            sql_delete = f"DELETE FROM fichas WHERE numeroFicha IN ({format_strings})"
            cur.execute(sql_delete, fichas)
        
        # 6. Insertar todos los datos únicos del CSV a la tabla principal
        campos_seleccion = ', '.join([f"{campo}" for _, campo in sorted(mapeo.items())])

        sql_insert = f"""
        INSERT INTO fichas ({campos_seleccion})
        SELECT {campos_seleccion} FROM (
            SELECT {campos_seleccion},
                ROW_NUMBER() OVER (PARTITION BY numeroFicha ORDER BY numeroFicha) AS rn
            FROM {tabla_temporal}
        ) AS sub
        WHERE rn = 1;
        """
        cur.execute(sql_insert)
        
        # 7. Confirmar los cambios
        conn.commit()
    finally:
        cur.close()
        conn.close()




# NUEVA RUTA PARA APRENDICES
@alimentador.route('/alimentador_aprendices', methods=['GET', 'POST'])
def alimentador_aprendices():
    if request.method == 'POST':
        total_cols = int(request.form['total_cols'])
        columnas_raw = request.form.get('columnas', '').strip().splitlines()
        
        mapeo = {}
        for linea in columnas_raw:
            if ':' in linea:
                csv_col, campo_db = linea.split(':')
                mapeo[int(csv_col.strip())] = campo_db.strip()
        
        if not mapeo:
            return "No se definieron asociaciones válidas entre columnas y campos de BD.", 400
        
        archivos_subidos = request.files.getlist('file')
        for archivo in archivos_subidos:
            if archivo and archivo.filename.endswith('.csv'):
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
                archivo.save(path)
                procesar_csv_aprendices(path, total_cols, mapeo)
        
        return f"{len(archivos_subidos)} archivos procesados con éxito."
    
    return render_template('alimentador_aprendices.html')

def procesar_csv_aprendices(path_archivo, total_cols, mapeo):
    print(f"=== DIAGNÓSTICO COMPLETO CSV APRENDICES ===")
    print(f"Archivo: {path_archivo}")
    print(f"Total columnas esperadas: {total_cols}")
    print(f"Mapeo recibido: {mapeo}")
    
    # PASO 1: Análisis detallado del CSV
    print(f"\n=== PASO 1: ANÁLISIS DETALLADO DEL CSV ===")
    try:
        with open(path_archivo, 'r', encoding='utf-8-sig') as f:  # utf-8-sig maneja BOM
            lineas = f.readlines()
            print(f"Total líneas en archivo: {len(lineas)}")
            
            print(f"\nPrimeras 5 líneas del archivo:")
            for i in range(min(5, len(lineas))):
                linea = lineas[i].strip()
                columnas = linea.split(',')
                print(f"  Línea {i+1}: {len(columnas)} columnas -> {linea[:100]}...")
            
            # Analizar líneas de datos reales (después de IGNORE 13)
            print(f"\nLíneas de DATOS (después de IGNORE 13):")
            for i in range(13, min(18, len(lineas))):  # Líneas 14-18
                if i < len(lineas):
                    linea = lineas[i].strip()
                    if linea:  # Solo si no está vacía
                        columnas = linea.split(',')
                        print(f"  Línea {i+1}: {len(columnas)} columnas")
                        for j, col in enumerate(columnas[:10]):  # Solo primeras 10 columnas
                            col_clean = col.strip('"').strip()
                            print(f"    Col {j+1}: '{col_clean}'")
                        if len(columnas) > 10:
                            print(f"    ... y {len(columnas) - 10} columnas más")
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return
    
    # PASO 2: Verificar mapeo vs estructura real
    print(f"\n=== PASO 2: VERIFICACIÓN DEL MAPEO ===")
    columnas_csv = ', '.join([f"@col{i}" for i in range(1, total_cols + 1)])
    print(f"Variables CSV generadas: {columnas_csv}")
    
    # Preparar mapeo con debugging
    set_clauses = []
    apellido1_col = None
    apellido2_col = None
    campos_finales = []
    
    print(f"\nProcesando mapeo campo por campo:")
    for col, campo in sorted(mapeo.items()):
        print(f"  Columna {col} del CSV -> Campo '{campo}' en BD")
        
        if campo == 'apellidos':
            clause = f"`apellidos` = NULLIF(TRIM(BOTH '\"' FROM @col{col}), '')"
            set_clauses.append(clause)
            campos_finales.append('apellidos')
            print(f"    SET: {clause}")
        elif campo == 'apellido1':
            apellido1_col = col
            print(f"    Guardado para concatenar con apellido2")
        elif campo == 'apellido2':
            apellido2_col = col
            print(f"    Guardado para concatenar con apellido1")
        else:
            clause = f"`{campo}` = NULLIF(TRIM(BOTH '\"' FROM @col{col}), '')"
            set_clauses.append(clause)
            campos_finales.append(campo)
            print(f"    SET: {clause}")
    
    # Manejo especial de apellidos concatenados
    if apellido1_col and apellido2_col:
        clause = f"`apellidos` = NULLIF(CONCAT(TRIM(BOTH '\"' FROM @col{apellido1_col}), ' ', TRIM(BOTH '\"' FROM @col{apellido2_col})), ' ')"
        set_clauses.append(clause)
        if 'apellidos' not in campos_finales:
            campos_finales.append('apellidos')
        print(f"  Concatenación apellidos: columna {apellido1_col} + columna {apellido2_col}")
        print(f"    SET: {clause}")
    
    print(f"\nCampos finales para la tabla: {campos_finales}")
    print(f"Total SET clauses: {len(set_clauses)}")
    
    # PASO 3: Crear y cargar tabla temporal
    path_archivo_sql = path_archivo.replace("\\", "/")
    tabla_temporal = "aprendices_tmp"
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print(f"\n=== PASO 3: CREACIÓN DE TABLA TEMPORAL ===")
        
        # Crear tabla temporal con todos los campos como TEXT
        cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
        campos_sql = ', '.join([f"`{campo}` TEXT DEFAULT NULL" for campo in campos_finales])
        create_sql = f"CREATE TABLE {tabla_temporal} ({campos_sql})"
        print(f"SQL CREATE: {create_sql}")
        cur.execute(create_sql)
        
        # PASO 4: Cargar datos con diagnóstico
        print(f"\n=== PASO 4: CARGA DE DATOS ===")
        set_clause = ',\n        '.join(set_clauses)
        
        # Usar una versión más robusta de LOAD DATA
        sql_load = f"""
        LOAD DATA LOCAL INFILE '{path_archivo_sql}'
        INTO TABLE {tabla_temporal}
        CHARACTER SET utf8mb4
        FIELDS 
            TERMINATED BY ',' 
            OPTIONALLY ENCLOSED BY '"'
            ESCAPED BY '\\\\'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
        ({columnas_csv})
        SET {set_clause}
        """
        
        print(f"SQL LOAD DATA:")
        print(sql_load)
        
        # Intentar la carga
        try:
            cur.execute(sql_load)
            print(f"✓ LOAD DATA ejecutado sin errores")
        except Exception as load_error:
            print(f"✗ Error en LOAD DATA: {load_error}")
            raise
        
        # PASO 5: Verificación detallada de datos cargados
        print(f"\n=== PASO 5: VERIFICACIÓN DE DATOS CARGADOS ===")
        
        cur.execute(f"SELECT COUNT(*) FROM {tabla_temporal}")
        total = cur.fetchone()[0]
        print(f"Total registros en tabla temporal: {total}")
        
        if total == 0:
            print("❌ NO SE CARGARON DATOS - Revisando posibles causas:")
            
            # Intentar con diferentes configuraciones
            print("\nIntentando con configuración alternativa...")
            cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
            cur.execute(create_sql)
            
            # Versión más simple
            sql_load_simple = f"""
            LOAD DATA LOCAL INFILE '{path_archivo_sql}'
            INTO TABLE {tabla_temporal}
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\\n'
            IGNORE 13 ROWS
            ({columnas_csv})
            SET {set_clause}
            """
            
            try:
                cur.execute(sql_load_simple)
                cur.execute(f"SELECT COUNT(*) FROM {tabla_temporal}")
                total = cur.fetchone()[0]
                print(f"Con configuración simple: {total} registros")
            except Exception as e2:
                print(f"También falló configuración simple: {e2}")
        
        if total > 0:
            print(f"✓ Datos cargados exitosamente")
            
            # Verificar contenido por campo
            print(f"\nAnálisis por campo:")
            for campo in campos_finales:
                cur.execute(f"SELECT COUNT(*) FROM {tabla_temporal} WHERE `{campo}` IS NOT NULL AND `{campo}` != ''")
                count_valid = cur.fetchone()[0]
                
                cur.execute(f"SELECT `{campo}` FROM {tabla_temporal} WHERE `{campo}` IS NOT NULL AND `{campo}` != '' LIMIT 3")
                ejemplos = [row[0] for row in cur.fetchall()]
                
                print(f"  {campo}: {count_valid}/{total} valores válidos")
                if ejemplos:
                    print(f"    Ejemplos: {ejemplos}")
                else:
                    print(f"    ⚠️ Sin datos válidos")
            
            # Mostrar registros completos de ejemplo
            print(f"\nPrimeros 2 registros completos:")
            campos_select = ', '.join([f"`{campo}`" for campo in campos_finales])
            cur.execute(f"SELECT {campos_select} FROM {tabla_temporal} LIMIT 2")
            registros = cur.fetchall()
            
            for i, registro in enumerate(registros, 1):
                print(f"  Registro {i}:")
                for j, valor in enumerate(registro):
                    print(f"    {campos_finales[j]}: '{valor}'")
            
            # PASO 6: Inserción en tabla principal
            print(f"\n=== PASO 6: INSERCIÓN EN TABLA PRINCIPAL ===")
            
            # Limpiar registros existentes si hay campo identificador
            if 'numeroDocumento' in campos_finales:
                cur.execute(f"SELECT DISTINCT `numeroDocumento` FROM {tabla_temporal} WHERE `numeroDocumento` IS NOT NULL AND `numeroDocumento` != ''")
                docs = [row[0] for row in cur.fetchall()]
                if docs:
                    placeholders = ','.join(['%s'] * len(docs))
                    cur.execute(f"DELETE FROM aprendices WHERE `numeroDocumento` IN ({placeholders})", docs)
                    print(f"Eliminados {cur.rowcount} registros existentes")
            
          # Insertar datos nuevos
            campos_insert = ', '.join([f"`{campo}`" for campo in campos_finales])
            sql_insert = f"""
            INSERT INTO aprendices ({campos_insert})
            SELECT {campos_insert} 
            FROM {tabla_temporal}
            WHERE NOT ({' AND '.join([f"(`{campo}` IS NULL OR `{campo}` = '')" for campo in campos_finales[:3]])})
            """

            
            print(f"SQL INSERT: {sql_insert}")
            cur.execute(sql_insert)
            insertados = cur.rowcount
            print(f"✓ {insertados} registros insertados en tabla principal")
            
            conn.commit()
            return f"Éxito: {insertados} registros procesados"
        else:
            return "Error: No se cargaron datos en la tabla temporal"
            
    except Exception as e:
        print(f"❌ ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        raise
    finally:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {tabla_temporal}")
        except:
            pass
        cur.close()
        conn.close()