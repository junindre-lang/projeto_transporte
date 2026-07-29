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
            const linha = document.getElementById(`viagem-${idViagem}`);
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

// ==========================================================================
// 4. EVENTOS DOM (TOGGLE SIDEBAR, BUSCA E CADASTRO AJAX)
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {

    // ----------------------------------------------------------------------
    // A. LÓGICA DE EMPURRAR / PUXAR A SIDEBAR (TOGGLE)
    // ----------------------------------------------------------------------
    const toggleBtn = document.getElementById("sidebar-toggle");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-collapsed");
        });
    }

    // ----------------------------------------------------------------------
    // B. BUSCA DINÂMICA NO MENU LATERAL
    // ----------------------------------------------------------------------
    const searchInput = document.querySelector(".search-box input");
    const menuItems = document.querySelectorAll(".sidebar-menu li");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const termoBusca = searchInput.value.toLowerCase().trim();

            menuItems.forEach(function (item) {
                const textoOpcao = item.textContent.toLowerCase();

                if (textoOpcao.includes(termoBusca)) {
                    item.style.display = "";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }

    // ----------------------------------------------------------------------
    // C. CADASTRO DE MOTORISTA VIA AJAX
    // ----------------------------------------------------------------------
    const formMotorista = document.getElementById('form-cadastrar-motorista');
    const resultadoBox = document.getElementById('resultado-cadastro-motorista');

    if (formMotorista) {
        formMotorista.addEventListener('submit', function(e) {
            e.preventDefault();

            const dados = {
                nome: document.getElementById('cad-nome').value,
                cpf: document.getElementById('cad-cpf').value,
                senha: document.getElementById('cad-senha').value
            };

            fetch('/api/motorista/cadastrar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            })
            .then(response => response.json())
            .then(data => {
                if (resultadoBox) {
                    resultadoBox.style.display = 'block';

                    if (data.sucesso) {
                        formMotorista.reset();

                        resultadoBox.style.backgroundColor = '#22c55e1a';
                        resultadoBox.style.border = '1px solid #22c55e';
                        resultadoBox.style.color = '#22c55e';
                        resultadoBox.innerHTML = `
                            <strong>🎉 Motorista Cadastrado!</strong><br><br>
                            <strong>Matrícula (CPF):</strong> <span style="background:#334155; padding:2px 6px; border-radius:4px; color:#38bdf8; font-family:monospace; font-weight:bold;">${dados.cpf}</span><br>
                            <p style="margin-top:10px; font-size:0.8rem; color:#94a3b8;">O acesso já está configurado com a senha definida.</p>
                        `;
                    } else {
                        resultadoBox.style.backgroundColor = '#ef44441a';
                        resultadoBox.style.border = '1px solid #ef4444';
                        resultadoBox.style.color = '#ef4444';
                        resultadoBox.innerHTML = `❌ Erro: ${data.erro}`;
                    }
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
                if (resultadoBox) {
                    resultadoBox.style.display = 'block';
                    resultadoBox.style.backgroundColor = '#ef44441a';
                    resultadoBox.style.border = '1px solid #ef4444';
                    resultadoBox.style.color = '#ef4444';
                    resultadoBox.innerHTML = '❌ Falha de rede ou conexão com o servidor.';
                }
            });
        });
    }
});