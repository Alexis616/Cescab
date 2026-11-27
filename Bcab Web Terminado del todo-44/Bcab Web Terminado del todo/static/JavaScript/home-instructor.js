let isAgendadosVisible = true;

function showAgendados() {
    isAgendadosVisible = true;
    document.getElementById('conten_agendados').style.display = 'grid';
    document.getElementById('conten_solicitados').style.display = 'none';
    document.getElementById('btn_agendados').classList.add('button-selected');
    document.getElementById('btn_agendados').classList.remove('button-default');
    document.getElementById('btn_solicitados').classList.add('button-default');
    document.getElementById('btn_solicitados').classList.remove('button-selected');
}

function showSolicitados() {
    isAgendadosVisible = false;
    document.getElementById('conten_agendados').style.display = 'none';
    document.getElementById('conten_solicitados').style.display = 'grid';
    document.getElementById('btn_agendados').classList.add('button-default');
    document.getElementById('btn_agendados').classList.remove('button-selected');
    document.getElementById('btn_solicitados').classList.add('button-selected');
    document.getElementById('btn_solicitados').classList.remove('button-default');
}