// Abre o modal de cadastro adicionando a classe CSS 'ativo'
function abrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.add('ativo');
    }
}

// Fecha o modal removendo a classe CSS
function fecharModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.remove('ativo');
    }
}

// Fecha o pop-up caso o administrador dê um clique fora do formulário central
window.onclick = function(event) {
    const modal = document.getElementById('modalVeiculo');
    if (event.target === modal) {
        modal.classList.remove('ativo');
    }
}