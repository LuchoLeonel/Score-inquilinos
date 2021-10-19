function allowScore (id, id_user) {
    fetch(`/allowScore/${id}/${id_user}`, {
        method: 'POST',
    })
    .then(response => response.text())
    .then(agregar => {
        if (agregar == 'True') {
            allow = document.querySelector('#change-allow')
            allow.innerHTML = `<div>Habilitaste a este usuario a calificarte.</div>`
        } else {
            allow = document.querySelector('#change-allow')
            allow.innerHTML = `<div>No fue posible realizar esta acción.</div>`
        }
    });
}

function makeScore (id, id_user) {
    make = document.querySelector('#submit-score')
    make.style.display = 'block';
    unmake = document.querySelector('#make-score')
    unmake.style.display = 'none'
}

function unmakeScore (id, id_user) {
    make = document.querySelector('#submit-score')
    make.style.display = 'none';
    unmake = document.querySelector('#make-score')
    unmake.style.display = 'block'
}
