document.addEventListener("DOMContentLoaded", function() {
    let cerrarSeccion = document.getElementById('salir');

    cerrarSeccion.addEventListener('click', function(e) {
        e.preventDefault(); e

       
        let confirmationMessage = "¿Estás seguro que deseas cerrar sesión?";
        if (!confirm(confirmationMessage)) {
            return;
        }
        window.location.href = "/login";
    });
});
