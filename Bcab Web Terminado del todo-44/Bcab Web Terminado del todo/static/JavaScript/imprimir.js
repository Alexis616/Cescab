function imprimir() {
    var contenido = document.documentElement.outerHTML;
    var ventana = window.open('', '_blank');
    ventana.document.open();
    ventana.document.write(contenido);
    ventana.document.close();
    setTimeout(function() {
        ventana.print();
        ventana.close();
    }, 1000);
}