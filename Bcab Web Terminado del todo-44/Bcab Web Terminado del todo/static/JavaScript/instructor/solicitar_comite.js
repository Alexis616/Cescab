// Vector para guardar los documentos de los aprendices seleccionados
var vector_aprendices = [];

document.addEventListener("DOMContentLoaded", function () {
    // Captura el evento cuando se marca/desmarca una checkbox
    document.querySelectorAll("input[type='checkbox']").forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            toggleClasificacion(this);
        });
    });

    // Captura el envío del formulario y manda los datos al backend con fetch
    document.querySelector("#form_aprendices").addEventListener("submit", function (event) {
        event.preventDefault(); // Evita el envío tradicional del formulario
        enviarAprendices();
    });
});

// Función para capturar el número de documento del aprendiz seleccionado
function toggleClasificacion(campo) {
    let numDocumento = campo.id.replace("check_", ""); // Extrae el número de documento del ID
    let index = vector_aprendices.indexOf(numDocumento);

    if (campo.checked) {
        if (index === -1) {
            vector_aprendices.push(numDocumento); // Agrega el documento si no está en el array
        }
    } else {
        if (index !== -1) {
            vector_aprendices.splice(index, 1); // Elimina el documento si ya estaba en el array
        }
    }

    console.log("Aprendices seleccionados:", vector_aprendices);
}

// Función para enviar los aprendices seleccionados al backend
function enviarAprendices() {
    if (vector_aprendices.length === 0) {
        alert("No has seleccionado ningún aprendiz.");
        return;
    }

    fetch("/procesar_aprendices", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ numeroDocumento_procesado: vector_aprendices })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data);
        if (data.success) {
            localStorage.setItem("aprendicesSeleccionados", JSON.stringify(data));
            
            // Obtener la fecha de inicio de la ficha
            const fechaInicio = data.fechaInicio;
            
            // Verificar si fechaInicio existe
            if (fechaInicio) {
                // Convertir la fecha de inicio a un objeto Date para comparación
                const fechaInicioObj = new Date(fechaInicio);
                const fechaReferencia = new Date('2024-11-05'); // Fecha de referencia
                
                // Decidir la redirección basada en la fecha
                if (fechaInicioObj < fechaReferencia) {
                    console.log("Redirigiendo a reglamento antiguo");
                    //window.location.href = "/aprendices_seleccionados";
                } else {
                    console.log("Redirigiendo a nuevo reglamento");
                    //window.location.href = "/aprendices_seleccionados_nuevoReglamento"; 
                }
            } else {
                // Si no hay fecha, redirección por defecto
                console.log("No se encontró fecha de inicio, usando redirección por defecto");
                //window.location.href = "/aprendices_seleccionados";
            }
        } else {
            alert("Error al procesar aprendices: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}









/*modal hisrorial*/


document.addEventListener('DOMContentLoaded', () => {
    // Limpiar checkboxes al cargar
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(chk => chk.checked = false);

    const form = document.getElementById('form_aprendices');
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();  // Evita que se recargue la página
            
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            const documentos = [];
            checkboxes.forEach(chk => {
                const id = chk.id.replace('check_', '');
                documentos.push(id);
            });

            if (documentos.length === 0) {
                alert("Por favor selecciona al menos un aprendiz.");
                return;
            }

            await verificarHistorial(documentos);
        });
    }
});


// PASO 1: Verificar si hay historial (NO procesa nada todavía)
async function verificarHistorial(documentos) {
    try {
        const response = await fetch('/verificar_historial', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numeroDocumento_procesado: documentos })
        });

        const data = await response.json();
        
        if (data.success) {
            console.log("Verificación de historial:", data);
            
            if (data.tiene_historial) {
                // MOSTRAR MODAL Y ESPERAR DECISIÓN DEL USUARIO
                mostrarModalHistorial(data);
            } else {
                // No hay historial, procesar directamente
                procesarAprendicesConfirmado(documentos);
            }
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Error en la verificación:", error);
        alert("Error al verificar el historial.");
    }
}

// Mostrar modal y ESPERAR decisión del usuario
function mostrarModalHistorial(data) {
    const historialHtml = data.avisos_llamados.map(aviso =>
        `<li>⚠️ ${aviso}</li>`
    ).join('');
    
    const historialContainer = document.getElementById('historial_modal_body');
    if (historialContainer) {
        historialContainer.innerHTML = `
            <div class="alerta-historial">
                <p><strong>¡ATENCIÓN!</strong> Se encontró historial previo de medidas formativas para los siguientes aprendices:</p>
                <ul class="lista-historial">${historialHtml}</ul>
                <p><strong>¿Desea continuar con el procesamiento de todos modos?</strong></p>
            </div>
        `;
    }

    const modal = document.getElementById('modalHistorial');
    if (modal) {
        modal.classList.remove('oculto');
        
        // Remover event listeners anteriores
        const cerrarBtn = document.getElementById('cerrarModal');
        const continuarBtn = document.getElementById('continuarBtn');
        const cancelarBtn = document.getElementById('cancelarBtn');
        
        // Event listener para cerrar modal (cancelar)
        if (cerrarBtn) {
            const nuevoCerrarBtn = cerrarBtn.cloneNode(true);
            cerrarBtn.parentNode.replaceChild(nuevoCerrarBtn, cerrarBtn);
            
            nuevoCerrarBtn.addEventListener('click', () => {
                modal.classList.add('oculto');
                console.log("Procesamiento cancelado por el usuario");
            });
        }
        
        // Event listener para cancelar
        if (cancelarBtn) {
            const nuevoCancelarBtn = cancelarBtn.cloneNode(true);
            cancelarBtn.parentNode.replaceChild(nuevoCancelarBtn, cancelarBtn);
            
            nuevoCancelarBtn.addEventListener('click', () => {
                modal.classList.add('oculto');
                console.log("Procesamiento cancelado por el usuario");
            });
        }
        
        // Event listener para continuar - AQUÍ ES DONDE REALMENTE PROCESA
        if (continuarBtn) {
            const nuevoContinuarBtn = continuarBtn.cloneNode(true);
            continuarBtn.parentNode.replaceChild(nuevoContinuarBtn, continuarBtn);
            
            nuevoContinuarBtn.addEventListener('click', async () => {
                modal.classList.add('oculto');
                console.log("Usuario confirmó continuar con el procesamiento");
                
                // Mostrar loading mientras procesa
                mostrarLoading(true);
                
                // AHORA SÍ PROCESAR CON EL SEGUNDO ENDPOINT
                await procesarAprendicesConfirmado(data.documentos);
            });
        }
        
        // Cierre al hacer clic fuera del modal
        const modalCloseHandler = (e) => {
            if (e.target === modal) {
                modal.classList.add('oculto');
                console.log("Modal cerrado - procesamiento cancelado");
                modal.removeEventListener('click', modalCloseHandler);
            }
        };
        modal.addEventListener('click', modalCloseHandler);
        
    } else {
        alert("Modal no encontrado");
        // Si no hay modal, procesar de todos modos
        procesarAprendicesConfirmado(data.documentos);
    }
}

// PASO 2: Procesar después de confirmación del usuario
async function procesarAprendicesConfirmado(documentos) {
    try {
        mostrarLoading(true);
        
        const response = await fetch('/procesar_aprendices_confirmado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numeroDocumento_procesado: documentos })
        });

        const data = await response.json();
        
        mostrarLoading(false);
        
        if (data.success) {
            console.log("Procesamiento completado:", data);
            
            // AQUÍ ES DONDE VAS A LA SIGUIENTE INTERFAZ
            const fechaInicio = data.fechaInicio;
            if (fechaInicio) {
                const fechaInicioObj = new Date(fechaInicio);
                const fechaReferencia = new Date('2024-11-05');

                if (fechaInicioObj < fechaReferencia) {
                    window.location.href = "/aprendices_seleccionados";
                } else {
                    window.location.href = "/aprendices_seleccionados_nuevoReglamento";
                }
            } else {
                window.location.href = "/aprendices_seleccionados";
            }

            
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        mostrarLoading(false);
        console.error("Error en el procesamiento:", error);
        alert("Error al procesar los aprendices.");
    }
}

// Función para ir a la siguiente interfaz
function irASiguienteInterfaz(data) {
    console.log("Redirigiendo a la siguiente interfaz con datos:", data);
    
    // Guardar datos para la siguiente interfaz
    localStorage.setItem('datosAprendicesProcesados', JSON.stringify(data));
    
    // AQUÍ IMPLEMENTA CÓMO QUIERES IR A LA SIGUIENTE INTERFAZ:
    
    // Opción 1: Redirigir a otra página
    //window.location.href = '/aprendices_seleccionados';
    
    // Opción 2: Mostrar otra sección en la misma página
    // document.getElementById('seccion_actual').style.display = 'none';
    // document.getElementById('seccion_siguiente').style.display = 'block';
    
    // Opción 3: Llamar a otra función
    // mostrarInterfazSiguiente(data);
}

// Función auxiliar para mostrar/ocultar loading
function mostrarLoading(mostrar) {
    let loadingElement = document.getElementById('loading');
    
    if (!loadingElement) {
        // Crear elemento de loading si no existe
        loadingElement = document.createElement('div');
        loadingElement.id = 'loading';
        loadingElement.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Procesando aprendices...</p>
                </div>
            </div>
        `;
        loadingElement.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
        `;
        document.body.appendChild(loadingElement);
    }
    
    loadingElement.style.display = mostrar ? 'flex' : 'none';
}


