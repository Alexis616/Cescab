const camposPorTabla = {
    aprendices: ['tipoDocumento', 'numeroDocumento', 'ficha', 'nombres', 'apellidos', 'telefono', 'correo_electronico', 'estado', 'juicio', 'fechaInicio', 'fechaFin'],
    fichas: ['numeroFicha', 'programaFormacion', 'fechaInicio','fechaFin','modalidad','duracionPrograma','sectorPrograma','nivel_formacion','nombreCoordinador','correoCoordinador'],
    juicios_evaluativos: ['documentoIdentidad', 'competencia', 'resultadoAprendizaje', 'juicios_evaluacion', 'fechaHora_je', 'funcionario'],
    usuarios: ['nombre', 'apellido', 'cedula', 'correo_electronico', 'telefono', 'tipo_vinculacion', 'fecha_fin_contrato', 'rol']
};

document.addEventListener('DOMContentLoaded', () => {
  
    document.getElementById('tabla').addEventListener('change', reiniciarFilas);
});

function actualizarInputOculto() {
    const filas = document.querySelectorAll('.fila-mapeo');  // <-- ESTO FALTABA
    const mapeos = [];

    filas.forEach(fila => {
        const col = fila.querySelector('.columna-csv').value;
        const campo = fila.querySelector('.campo-bd').value;
        if (col && campo) mapeos.push(`${col}:${campo}`);
    });

    document.getElementById('columnas-hidden').value = mapeos.join('\n');
}

function agregarFila() {
    const tabla = document.getElementById('tabla').value;
    if (!tabla) return;

    const container = document.getElementById('mapeo-container');
   
    var totalCols = parseInt(document.getElementById("total_cols").value, 10);

    const fila = document.createElement('div');
    fila.className = 'fila-mapeo';
    fila.innerHTML = `
        <select class="columna-csv" onchange="verificarAutoAgregar()">
            <option value="">Col CSV</option>
            ${Array.from({ length: totalCols }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}
        </select>
        <select class="campo-bd" onchange="verificarAutoAgregar()">
            <option value="">Campo BD</option>
            ${camposPorTabla[tabla].map(c => `<option value="${c}">${c}</option>`).join('')}
        </select>
    `;
    container.appendChild(fila);
    actualizarInputOculto();
}

function verificarAutoAgregar() {
    actualizarInputOculto();

    const filas = document.querySelectorAll('.fila-mapeo');
    const ultimaFila = filas[filas.length - 1];
    const col = ultimaFila.querySelector('.columna-csv').value;
    const campo = ultimaFila.querySelector('.campo-bd').value;

    if (col && campo) {
        agregarFila();
    }
}

function reiniciarFilas() {
    document.getElementById('mapeo-container').innerHTML = '';
    agregarFila();
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('tabla').addEventListener('change', reiniciarFilas);
    document.getElementById('total_cols').addEventListener('input', () => {
        // Solo agregamos fila si hay un número válido en total_cols
        const totalCols = parseInt(document.getElementById("total_cols").value, 10);
        if (!isNaN(totalCols) && totalCols > 0) {
            document.getElementById('mapeo-container').innerHTML = '';
            agregarFila();
        }
    });
});
