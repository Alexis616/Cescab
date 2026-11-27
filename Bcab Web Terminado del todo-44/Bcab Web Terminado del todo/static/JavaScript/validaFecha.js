document.addEventListener("DOMContentLoaded", function() {
    console.log("El DOM ha sido completamente cargado.");
    
    let dateInputs = document.querySelectorAll('#validaFecha');
    console.log(`Se encontraron ${dateInputs.length} elementos con ID 'validaFecha'.`);

    dateInputs.forEach(function(dateInput) {
        // Limpiar el valor del input de fecha al cargar la página
        dateInput.value = '';
        console.log(`Limpiando el valor de '${dateInput.id}'.`);

        dateInput.addEventListener('change', function() {
            console.log(`Evento 'change' detectado en '${dateInput.id}'.`);
            let selectedDate = new Date(dateInput.value);
            let today = new Date();

            if (selectedDate < today) {
                dateInput.setCustomValidity('Seleccione una fecha igual o posterior a hoy.');
                console.log(`Fecha seleccionada en '${dateInput.id}' es anterior a hoy.`);
            } else {
                dateInput.setCustomValidity('');
                console.log(`Fecha seleccionada en '${dateInput.id}' es válida.`);
            }
        });

        dateInput.addEventListener('invalid', function() {
            dateInput.style.borderColor = "red";
            console.log(`Fecha inválida en '${dateInput.id}'. Estableciendo borde rojo.`);
        });

        dateInput.addEventListener('input', function() {
            dateInput.style.borderColor = '';
            console.log(`Evento 'input' detectado en '${dateInput.id}'. Restaurando borde.`);
        });
    });
});
