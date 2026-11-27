document.addEventListener("DOMContentLoaded", function () {
    let rawData = localStorage.getItem("aprendicesSeleccionados");

    if (!rawData) {
        console.warn("⚠️ No hay datos en localStorage.");
        return;
    }

    let data;
    try {
        data = JSON.parse(rawData);
    } catch (error) {
        console.error("❌ Error al parsear JSON:", error);
        return;
    }

    llenarTablaAprendices(data);
    llenarTablaArticulos(data);
    configurarBotonEnviar();
    configurarCierreDropdowns(); // AGREGADO: Configurar cierre de dropdowns
});

// AGREGADO: Función para cerrar todos los dropdowns cuando se hace clic fuera de ellos
function configurarCierreDropdowns() {
    document.addEventListener('click', function(event) {
        // Si el clic no fue en un botón de dropdown ni en su contenido
        if (!event.target.closest('.dropdown-content') && 
            !event.target.classList.contains('boton-activo') &&
            !event.target.classList.contains('personalizarBotonResultados')) {
            
            // Cerrar todos los dropdowns
            const allDropdowns = document.querySelectorAll('.dropdown-content');
            allDropdowns.forEach(item => {
                item.style.display = "none";
            });
        }
    });
}

// MODIFICADO: Función para alternar la visibilidad de los dropdowns
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    if (dropdown) {
        if (dropdown.style.display === "block") {
            dropdown.style.display = "none";
        } else {
            // Cerrar todos los demás dropdowns primero
            const allDropdowns = document.querySelectorAll('.dropdown-content');
            allDropdowns.forEach(item => {
                if (item.id !== id) {
                    item.style.display = "none";
                }
            });
            dropdown.style.display = "block";
        }
    }
}

function llenarTablaAprendices(data) {
    let tableBody = document.querySelector("#tablaAprendices tbody");

    if (!tableBody) {
        console.error("❌ Error: No se encontró la tabla de aprendices.");
        return;
    }

    Object.keys(data.nombres_completos).forEach(documento => {
        let nombre = data.nombres_completos[documento];
        let estado = data.estado?.[documento] || "No definido";
        let ficha = data.ficha?.[documento] || "No definido";
        let fichaPrograma = data.fichaPrograma || "No definido";
        let nombreCoordinador = data.nombreCoordinador || "No definido";
        let correoCoordinador = data.correoCoordinador || "No definido";
        let correo_electronico = data.correo_electronico?.[documento] || "No definido";
        let telefono = data.telefono?.[documento] || "No definido";
        let competencias = data.resultados_competencia?.[documento] || {};
        let competenciasKeys = Object.keys(competencias);

        let selectClasificacion = `
            <select onchange="verificarClasificacion(this, '${documento}')"
                data-competencias='${JSON.stringify(competenciasKeys)}'>
                <option value="Académico">Académico</option>
                <option value="Disciplinario">Disciplinario</option>
                <option value="Académico Disciplinario">Académico Disciplinario</option>
            </select>`;

        let selectCalificacion = `
            <select>
                <option value="Leve">Leve</option>
                <option value="Grave">Grave</option>
                <option value="Gravísima">Gravísima</option>
            </select>`;

        let selectFase = `
            <select>
                <option value="Fase 1">Fase 1</option>
                <option value="Fase 2">Fase 2</option>
                <option value="Fase 3">Fase 3</option>
                <option value="Fase 4">Fase 4</option>
            </select>`;

        let selectCompetencia = crearSelectCompetencias(documento, competenciasKeys);

        let row = tableBody.insertRow();
        row.innerHTML = `
            <td>${nombre}</td>
            <td class = "estado" >${estado}</td>
            <td>${selectClasificacion}</td>
            <td>${selectCalificacion}</td>
            <td>${selectFase}</td>
            <td id="td-competencia-${documento}">${selectCompetencia}</td>
            <td id="td-resultados-${documento}" class="texto_resultados">Seleccione una competencia de aprendizaje</td>
            <input type="hidden" name="documento" value="${documento}">
            <input type="hidden" name="ficha" value="${ficha}">
            <input type="hidden" name="fichaPrograma" value="${fichaPrograma}">
            <input type="hidden" name="nombreCoordinador" value="${nombreCoordinador}">
            <input type="hidden" name="correoCoordinador" value="${correoCoordinador}">
            <input type="hidden" name="correo_electronico" value="${correo_electronico}">
            <input type="hidden" name="telefono" value="${telefono}">
        `;
    });
}

function crearSelectCompetencias(documento, competenciasKeys) {
    return `<select id="selectDeLosResultados" onchange="actualizarResultados(this, '${documento}')">
        <option value="">Seleccione una competencia de aprendizaje</option>
        ${competenciasKeys.map(comp => `<option id="optionDeLosResultados" value="${comp}">${comp}</option>`).join("")}
    </select>`;
}

function actualizarResultados(select, documento) {
    let competenciaSeleccionada = select.value;
    let contenedorResultados = document.getElementById(`td-resultados-${documento}`);
    let rawData = localStorage.getItem("aprendicesSeleccionados");
    let data = JSON.parse(rawData);
    let resultados = data.resultados_competencia[documento]?.[competenciaSeleccionada] || [];

    if (resultados.length === 0) {
        contenedorResultados.innerHTML = "Seleccione una competencia de aprendizaje";
        return;
    }

    const id = `resultados-${documento}`;
    const checkboxesHTML = resultados.map(resultado => `
        <label><input type="checkbox" style="height: 25px;width: 25px;" value="${resultado}" onchange="guardarResultadosTemporal('${documento}')"> ${resultado}</label>`
    ).join("<br>");

    contenedorResultados.innerHTML = `
        <div class="dropdown">
            <button id="btn-${id}" class="boton-activo personalizarBotonResultados" onclick="toggleDropdown('dropdown-${id}')">Seleccionar Resultados</button>
            <div id="dropdown-${id}" class="dropdown-content">${checkboxesHTML}</div>
        </div>`;
}


function guardarResultadosTemporal(documento) {
    const id = `resultados-${documento}`;
    const checkboxes = document.querySelectorAll(`#dropdown-${id} input[type="checkbox"]:checked`);
    const seleccionados = Array.from(checkboxes).map(cb => cb.value);

    const contenedor = document.getElementById(`td-resultados-${documento}`);
    contenedor.dataset.seleccionados = JSON.stringify(seleccionados);

    const boton = document.getElementById(`btn-${id}`);
    if (boton) {
        boton.textContent = seleccionados.length > 0
            ? `Resultados seleccionados: (${seleccionados.length})`
            : "Seleccionar Resultados";
    }
}


function verificarClasificacion(select, documento) {
    let clasificacion = select.value;
    let tdCompetencia = document.getElementById(`td-competencia-${documento}`);
    let tdResultados = document.getElementById(`td-resultados-${documento}`);
    let competenciasKeys = JSON.parse(select.getAttribute("data-competencias"));

    if (clasificacion === "Disciplinario") {
        tdCompetencia.innerHTML = `<div>No aplica</div>`;
        tdResultados.innerHTML = `<div>No aplica</div>`;
    } else {
        tdCompetencia.innerHTML = crearSelectCompetencias(documento, competenciasKeys);
        tdResultados.innerHTML = "Seleccione una competencia";
    }
}

// MODIFICADO: Función para el nuevo formato simplificado CON DROPDOWN FUNCIONAL
function llenarTablaArticulos(data) {
    let tableBody = document.getElementById("tablaArticulos");

    if (!tableBody || !data.nombres_completos) {
        console.error("❌ No se encontró el tbody con ID 'tablaArticulos' o los datos 'nombres_completos'.");
        return;
    }

    Object.keys(data.nombres_completos).forEach(documento => {
        let nombre = data.nombres_completos[documento];

        let row = tableBody.insertRow();
        row.innerHTML = `
            <td>${nombre}</td>
            <td id="info-${documento}-1" class="info-field">
                <div class="dropdown">
                    <button id="btn-info-${documento}-1" class="boton-activo" onclick="toggleDropdown('dropdown-info-${documento}-1')">Seleccionar Información</button>
                    <div id="dropdown-info-${documento}-1" class="dropdown-content" style="display: none;">
                        <div id="loading-${documento}-1">Cargando...</div>
                    </div>
                </div>
            </td>
            <td id="info-${documento}-2" class="info-field">
                <div class="dropdown">
                    <button id="btn-info-${documento}-2" class="boton-activo" onclick="toggleDropdown('dropdown-info-${documento}-2')">Seleccionar Información</button>
                    <div id="dropdown-info-${documento}-2" class="dropdown-content" style="display: none;">
                        <div id="loading-${documento}-2">Cargando...</div>
                    </div>
                </div>
            </td>
            <td id="info-${documento}-3" class="info-field">
                <div class="dropdown">
                    <button id="btn-info-${documento}-3" class="boton-activo" onclick="toggleDropdown('dropdown-info-${documento}-3')">Seleccionar Información</button>
                    <div id="dropdown-info-${documento}-3" class="dropdown-content" style="display: none;">
                        <div id="loading-${documento}-3">Cargando...</div>
                    </div>
                </div>
            </td>
            <td id="celda-descripcion-${documento}">
                <div class="contenedor-boton-descripcion">
                    <button id="boton-descripcion-${documento}" class="botonModal" type="button">
                        Agregar descripción
                    </button>
                </div>
            </td>
        `;

        // Cargar información de cada artículo automáticamente
        cargarInformacionArticulo(documento, 1, 9);   // Artículo 9 - Deberes
        cargarInformacionArticulo(documento, 2, 10);  // Artículo 10 - Prohibiciones
        cargarInformacionArticulo(documento, 3, 22);  // Artículo 22 - Otro
    });
}

// MODIFICADO: Nueva función para cargar información de artículos directamente CON DROPDOWN FUNCIONAL
function cargarInformacionArticulo(documento, columna, numeroArticulo) {
    const informacionArticulo = document.getElementById(`info-${documento}-${columna}`);
    
    fetch(`/obtener-informacion-articulo_viejoReglamento?articulo=${numeroArticulo}`)
        .then(response => response.json())
        .then(jsonData => {
            const checkboxesHTML = jsonData.informacion_articulo.map(info => `
                <label><input type="checkbox" value="${info}" onchange="actualizarSeleccion('${documento}-${columna}')" style="height: 25px;width: 25px;"> ${info}</label><br>`).join("");                

            informacionArticulo.innerHTML = `
                <div class="dropdown">
                    <button id="btn-info-${documento}-${columna}" class="boton-activo" onclick="toggleDropdown('dropdown-info-${documento}-${columna}')">Seleccionar Información</button>
                    <div id="dropdown-info-${documento}-${columna}" class="dropdown-content" style="display: none;">${checkboxesHTML}</div>
                </div>`;
        })
        .catch(error => {
            console.error("❌ Error al obtener información del artículo:", error);
            informacionArticulo.innerHTML = `
                <div class="dropdown">
                    <button id="btn-info-${documento}-${columna}" class="boton-inactivo" disabled>Error al cargar</button>
                    <div id="dropdown-info-${documento}-${columna}" class="dropdown-content" style="display: none;"><label>Error al cargar</label></div>
                </div>`;
        });
}

function actualizarSeleccion(id) {
    const checkboxes = document.querySelectorAll(`#dropdown-info-${id} input[type="checkbox"]:checked`);
    const seleccionados = Array.from(checkboxes).map(cb => cb.value);

    const boton = document.getElementById(`btn-info-${id}`);
    if (boton) {
        boton.dataset.seleccionados = JSON.stringify(seleccionados);
        boton.textContent = seleccionados.length > 0
            ? `Información seleccionada: (${seleccionados.length})`
            : "Seleccionar Información";
    }
}

// ELIMINADO: La función toggleDropdown anterior que no funcionaba bien
// ELIMINADO: El window.onclick que conflictuaba con el sistema de dropdowns

function configurarBotonEnviar() {
    let botonEnviar = document.getElementById("solicitar_comite_funcion");
    if (!botonEnviar) return;
  
    botonEnviar.addEventListener("click", function () {
      let aprendices = [];
      let tableRows = document.querySelectorAll("#tablaAprendices tbody tr");
  
      // Usamos un bucle for...of para poder romper la ejecución en caso de error
      for (let row of tableRows) {
        // Obtenemos de inmediato el nombre del aprendiz de la primera celda
        let nombre = row.cells[0].innerText;
        let documento = row.querySelector("input[name='documento']").value;
  
        let articulos = [];
        // Recorremos los 3 artículos (9, 10, 22)
        const numerosArticulos = [9, 10, 22];
        const titulosArticulos = [
            "Capitulo III. DEBERES DEL APRENDIZ SENA", 
            "Capitulo IV. PROHIBICIONES", 
            "Capitulo VII. PROCESO DE FORMACIÓN- INCUMPLIMIENTO-DESERCION"
        ];
        
        for (let i = 1; i <= 3; i++) {
          let titulo = titulosArticulos[i-1];
          let articulo = numerosArticulos[i-1].toString();
          let infoCheckboxes = document.querySelectorAll(`#info-${documento}-${i} input[type="checkbox"]:checked`);
          let informacion = Array.from(infoCheckboxes).map(cb => cb.value);
  
          // Si hay información seleccionada, agregamos el artículo
          if (informacion.length > 0) {
            articulos.push({ titulo, articulo, informacion });
          }
        }
  
        // Se valida que se haya completado al menos un artículo
        if (articulos.length === 0) {
          alert(`Por favor, selecciona al menos una información de los artículos para el aprendiz ${nombre}.`);
          return;
        }
  
        // Recopilamos el resto de la información del aprendiz
        let ficha = row.querySelector("input[name='ficha']").value;
        let fichaPrograma = row.querySelector("input[name='fichaPrograma']").value;
        let nombreCoordinador = row.querySelector("input[name='nombreCoordinador']").value;
        let correoCoordinador = row.querySelector("input[name='correoCoordinador']").value;
        let correo_electronico = row.querySelector("input[name='correo_electronico']").value;
        let telefono = row.querySelector("input[name='telefono']").value;
        let estado = row.cells[1].innerText;
        let clasificacion = row.cells[2].querySelector("select")?.value || "No aplica";
        let calificacion = row.cells[3].querySelector("select")?.value || "No aplica";
        let fase = row.cells[4].querySelector("select")?.value || "Fase 1";
        let competencia = row.cells[5].querySelector("select")?.value || "No aplica";
        let contenedor = document.getElementById(`td-resultados-${documento}`);
        let resultados = contenedor.dataset.seleccionados ? JSON.parse(contenedor.dataset.seleccionados) : [];
        let inputDescripcion = document.querySelector(`#descripcion-${documento}`);
        let descripcion = inputDescripcion ? inputDescripcion.value : "";
  
        aprendices.push({
          documento,
          ficha,
          fichaPrograma,
          nombreCoordinador,
          correoCoordinador,
          correo_electronico,
          telefono,
          nombre,
          estado,
          clasificacion,
          calificacion,
          fase,
          competencia,
          resultados,
          descripcion,
          articulos // Al menos uno garantizado por la validación
        });
      }
  
      // Envía los datos al backend si todas las validaciones pasaron
      fetch("/solicitar_comite_funcion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ aprendices })
      })
        .then(response => {
          if (response.ok) window.location.href = "/home_instructor_solicitado_agendados";
          else return response.text().then(text => { throw new Error(text) });
        })
        .catch(error => console.error("Error al enviar los datos:", error));
    });
}
  

// Modificación en el event listener del botón "Siguiente"

document.addEventListener("DOMContentLoaded", () => {
    const paso1 = document.getElementById("paso-1");
    const paso2 = document.getElementById("paso-2");
    const btnSiguiente = document.getElementById("btnSiguientePaso");
    const btnAtras = document.getElementById("btnAtrasPaso");

    const indicadorPaso1 = document.getElementById("indicador-paso-1");
    const indicadorPaso2 = document.getElementById("indicador-paso-2");
    const lineaBarra = document.querySelector(".linea-barra");

    // Mostrar solo el paso 1 al inicio
    paso1.classList.add("activo");
    paso2.classList.remove("activo");

    btnSiguiente.addEventListener("click", () => {
        // Realizar validación antes de cambiar de paso
        if (!validarClasificacionYCompetencias()) {
            return;
        }

        paso1.classList.remove("activo");
        paso2.classList.add("activo");

        indicadorPaso1.classList.remove("activo");
        indicadorPaso1.classList.add("amarillo");
        indicadorPaso2.classList.add("activo");

        lineaBarra.classList.add("activa");

        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    btnAtras.addEventListener("click", () => {
        paso2.classList.remove("activo");
        paso1.classList.add("activo");

        indicadorPaso2.classList.remove("activo");
        indicadorPaso1.classList.remove("amarillo");
        indicadorPaso1.classList.add("activo");

        lineaBarra.classList.remove("activa");

        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

function validarClasificacionYCompetencias() {
    let tableRows = document.querySelectorAll("#tablaAprendices tbody tr");
    
    for (let row of tableRows) {
        let nombre = row.cells[0].innerText;
        let documento = row.querySelector("input[name='documento']").value;
        let clasificacion = row.cells[2].querySelector("select")?.value;
        
        // Si la clasificación es "Académico" o "Académico Disciplinario"
        if (clasificacion === "Académico" || clasificacion === "Académico Disciplinario") {
            // Verificar que se haya seleccionado una competencia
            let competenciaSelect = row.cells[5].querySelector("select");
            let competenciaSeleccionada = competenciaSelect?.value;
            
            if (!competenciaSeleccionada || competenciaSeleccionada === "") {
                alert(`Por favor, selecciona una COMPETENCIA para el aprendiz ${nombre} con clasificación ${clasificacion}.`);
                return false;
            }
            
            // Verificar que se hayan seleccionado resultados
            let contenedorResultados = document.getElementById(`td-resultados-${documento}`);
            let resultadosSeleccionados = contenedorResultados.dataset.seleccionados 
                ? JSON.parse(contenedorResultados.dataset.seleccionados) 
                : [];
            
            if (resultadosSeleccionados.length === 0) {
                alert(`Por favor, selecciona al menos un RESULTADO DE APRENDIZAJE para el aprendiz ${nombre} con clasificación ${clasificacion}.`);
                return false;
            }
        }
    }
    
    return true;
}

let documentoActivoDescripcion = null;

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modalDescripcion");
    const cerrarModal = document.getElementById("cerrarModal");
    const guardarDescripcion = document.getElementById("guardarDescripcion");
    const descripcionInput = document.getElementById("descripcionInput");

    // Abrir el modal
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id.startsWith("boton-descripcion-")) {
            documentoActivoDescripcion = e.target.id.replace("boton-descripcion-", "");

            const inputExistente = document.getElementById(`descripcion-${documentoActivoDescripcion}`);
            descripcionInput.value = inputExistente ? inputExistente.value : "";

            modal.style.display = "block";
        }
    });

    // Cerrar el modal
    cerrarModal.onclick = function () {
        modal.style.display = "none";
    };

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Guardar la descripción
    guardarDescripcion.onclick = function () {
        if (!documentoActivoDescripcion) return;

        let descripcion = descripcionInput.value.trim();

        // Verifica si ya existe el input hidden
        let inputDescripcion = document.getElementById(`descripcion-${documentoActivoDescripcion}`);
        if (!inputDescripcion) {
            // Si no existe, crearlo
            inputDescripcion = document.createElement("input");
            inputDescripcion.type = "hidden";
            inputDescripcion.id = `descripcion-${documentoActivoDescripcion}`;
            inputDescripcion.name = `descripcion-${documentoActivoDescripcion}`;

            // Insertarlo en el botón mismo
            const botonDescripcion = document.getElementById(`boton-descripcion-${documentoActivoDescripcion}`);
            botonDescripcion.parentElement.appendChild(inputDescripcion);
        }

        inputDescripcion.value = descripcion;
        
        // Cambiar el texto del botón si hay descripción
        const botonDescripcion = document.getElementById(`boton-descripcion-${documentoActivoDescripcion}`);
        if (descripcion.length > 0) {
            botonDescripcion.textContent = "Descripción agregada";
        } else {
            botonDescripcion.textContent = "Agregar descripción";
        }
        
        modal.style.display = "none";
    };
});