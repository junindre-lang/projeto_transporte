// ==========================================================================
// CONTROLE DO MODAL DE VEÍCULOS
// ==========================================================================
function abrirModal(idModal) {
    document.getElementById(idModal).classList.add('ativo');
}

function fecharModal(idModal) {
    document.getElementById(idModal).classList.remove('ativo');
}

// Fecha o modal se o administrador clicar fora da caixinha do formulário
window.onclick = function(event) {
    const modal = document.getElementById('modalVeiculo');
    if (event.target == modal) {
        modal.classList.remove('ativo');
    }
}

// ==========================================================================
// INTERAÇÃO DA TABELA (DEFERIR / INDEFERIR)
// ==========================================================================
function processarViagem(idLinha, acao, nomeMotorista) {
    // Alerta informativo na tela
    alert(`A solicitação de ${nomeMotorista} foi ${acao} com sucesso!`);

    // Remove a linha correspondente de forma dinâmica na interface
    const linha = document.getElementById(idLinha);
    if (linha) {
        linha.remove();
    }

    // Caso todas as solicitações acabem, gera um feedback amigável de sucesso
    const tabelaCorpo = document.getElementById('corpo-tabela-viagens');
    if (tabelaCorpo && tabelaCorpo.rows.length === 0) {
        tabelaCorpo.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: #888; padding: 30px;">
                    <i class="fa-solid fa-circle-check" style="color: #2ecc71; margin-right: 5px;"></i>
                    Todas as solicitações pendentes foram processadas!
                </td>
            </tr>
        `;
    }
}