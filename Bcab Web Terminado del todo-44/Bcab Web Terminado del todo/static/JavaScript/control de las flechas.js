document.addEventListener("DOMContentLoaded", function() {

    history.pushState(null, null, window.location.href);
    window.onpopstate = function(event) {   
        window.location.href = "/login";
        history.pushState(null, null, window.location.href);
    };
});
