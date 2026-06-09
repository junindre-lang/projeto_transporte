// ==========================================================================
// 1. GERENCIAMENTO DE VIAGENS (Admin)
// ==========================================================================
function processarViagem(idViagem, acao, nomeMotorista) {
    const urlRota = acao === 'Deferida' ? '/pag_admin/deferir_viagem' : '/pag_admin/indeferir_viagem';

    fetch(urlRota, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_viagem: idViagem, motorista: nomeMotorista })
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            const linha = document.getElementById(`viagem-${idViagem}`); // Ajustado ID
            if(linha) {
                linha.style.transition = '0.3s';
                linha.style.opacity = '0';
                setTimeout(() => linha.remove(), 300);
            }
            alert(`Viagem do motorista ${data.motorista} foi ${data.status} com sucesso!`);
        } else {
            alert('Erro: ' + data.erro);
        }
    });
}

// ==========================================================================
// 2. GERENCIAMENTO DE SERVIDORES (Admin)
// ==========================================================================
function processarServidor(idServidor, acao) {
    const urlRota = acao === 'aprovar' ? `/lista_servidores/aprovar/${idServidor}` : `/lista_servidores/excluir/${idServidor}`;

    if (acao === 'excluir' && !confirm('Tem certeza que deseja excluir?')) return;

    fetch(urlRota, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            const linha = document.getElementById(`servidor-${idServidor}`);
            if(linha) {
                linha.style.opacity = '0';
                setTimeout(() => linha.remove(), 300);
            }
        } else {
            alert(data.erro);
        }
    });
}

// ==========================================================================
// 3. UTILS DE MODAL
// ==========================================================================
function abrirModal(idModal) {
    const m = document.getElementById(idModal);
    if(m) { m.style.display = 'flex'; m.classList.add('ativo'); }
}

function fecharModal(idModal) {
    const m = document.getElementById(idModal);
    if(m) { m.classList.remove('ativo'); setTimeout(() => m.style.display = 'none', 300); }
}