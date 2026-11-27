document.addEventListener('DOMContentLoaded', () => {
    const regresarBtns = document.querySelectorAll(".btn-regresar");
    const siguienteBtns = document.querySelectorAll(".btn_siguiente");
    const progreso = document.getElementById('progreso');
    const pasosFormularios = document.querySelectorAll('.pasos_del_formulario');
    const pasosProgresos = document.querySelectorAll('.pasos_progreso');

    let pasoActual = 0;

    siguienteBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            if (pasoActual < pasosFormularios.length - 1) {
                pasoActual++;
                actualizarPasosFormularios();
                actualizarProgreso();
            }
        });
    });

    regresarBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            if (pasoActual > 0) {
                pasoActual--;
                actualizarPasosFormularios();
                actualizarProgreso();
            }
        });
    });

    function actualizarPasosFormularios() {
        pasosFormularios.forEach((paso, index) => {
            if (index === pasoActual) {
                paso.classList.add("pasos_del_formulario_activo");
            } else {
                paso.classList.remove("pasos_del_formulario_activo");
            }
        });
    }

    function actualizarProgreso() {
        pasosProgresos.forEach((paso, idx) => {
            if (idx <= pasoActual) {
                paso.classList.add("progreso_activo");
            } else {
                paso.classList.remove("progreso_activo");
            }
        });

        const progresoActivos = document.querySelectorAll(".progreso_activo");
        progreso.style.width = ((progresoActivos.length - 1) / (pasosProgresos.length - 1)) * 100 + "%";
    }
});