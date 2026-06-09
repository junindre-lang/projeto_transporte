/**
 * Controla abertura forçando display block/flex
 * para anular problemas de cache do navegador.
 */
function abrirModal(idModal) {
    var modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = 'flex';
        // Pequeno atraso para o efeito visual de fade funcionar
        setTimeout(function() {
            modal.classList.add('ativo');
        }, 10);
    }
}

/**
 * Fecha o modal removendo as propriedades ativas.
 */
function fecharModal(idModal) {
    var modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.remove('ativo');
        setTimeout(function() {
            modal.style.display = 'none';
        }, 250);
    }
}

/**
 * Fecha a janela se clicar em qualquer área cinza fora da caixa.
 */
window.onclick = function(event) {
    var modal = document.getElementById('modalVeiculo');
    if (event.target === modal) {
        fecharModal('modalVeiculo');
    }
}