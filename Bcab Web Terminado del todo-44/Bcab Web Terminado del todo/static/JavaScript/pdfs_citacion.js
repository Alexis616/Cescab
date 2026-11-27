function generarPDFs() {
    const formData = new FormData();
    const fileInput = document.getElementById("firma");

    // Si se seleccionó un archivo de firma, lo agregamos al FormData.
    if (fileInput.files.length > 0) {
        formData.append("firma", fileInput.files[0]);
    }

    fetch('/ejecutar_clase', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => alert(data.mensaje))
    .catch(error => console.error('Error:', error));
}