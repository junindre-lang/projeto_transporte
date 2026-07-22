document.addEventListener("DOMContentLoaded", function() {
    const buscaInput = document.getElementById("busca-viagem");
    const botoesFiltro = document.querySelectorAll(".btn-filtro");
    const linhasViagem = document.querySelectorAll(".linha-viagem");

    // ==========================================
    // 1. SISTEMA DE FILTRO POR TEXTO E BOTÕES
    // ==========================================
    function aplicarFiltros() {
        const termoBusca = buscaInput.value.toLowerCase();
        const filtroAtivo = document.querySelector(".btn-filtro.ativo").getAttribute("data-filtro");

        linhasViagem.forEach(linha => {
            const textoLinha = linha.textContent.toLowerCase();
            const tipoCadastro = linha.getAttribute("data-tipo"); // 'mapa' ou 'manual'

            // Verifica match de texto
            const bateuTexto = textoLinha.includes(termoBusca);

            // Verifica match de categoria (Todos, Manual ou Mapa)
            const bateuCategoria = (filtroAtivo === "todos") || (tipoCadastro === filtroAtivo);

            if (bateuTexto && bateuCategoria) {
                linha.style.display = "";
            } else {
                linha.style.display = "none";
            }
        });

        // Se todas as linhas sumirem, você pode opcionalmente mostrar a mensagem de "Nenhum dado"
        verificarTabelaVazia();
    }

    // Ouvinte para a barra de pesquisa
    if (buscaInput) {
        buscaInput.addEventListener("input", aplicarFiltros);
    }

    // Ouvinte para os botões de categoria (Todas, Manuais, Via Mapa)
    botoesFiltro.forEach(botao => {
        botao.addEventListener("click", function() {
            botoesFiltro.forEach(btn => btn.classList.remove("ativo"));
            this.classList.add("ativo");
            aplicarFiltros();
        });
    });

    function verificarTabelaVazia() {
        const linhasVisiveis = document.querySelectorAll(".linha-viagem[style='']");
        const semDadosTr = document.getElementById("sem-dados");

        if (linhasVisiveis.length === 0 && !semDadosTr) {
            // Se não houver linhas visíveis, opcionalmente avisa o usuário
        }
    }
});

// ==========================================
// 2. FUNÇÃO AJAX PARA EXCLUIR REGISTRO
// ==========================================
function deletarViagem(idViagem) {
    if (!confirm("Tem certeza que deseja remover permanentemente este registro de viagem e sua rota?")) {
        return;
    }

    // Dispara para a rota do seu bp_admin.py
    fetch(`/api/viagem/excluir/${idViagem}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(dados => {
        if (dados.sucesso) {
            alert("Sucesso: " + dados.mensagem);

            // Remove a linha da tabela de forma suave sem recarregar a página
            const linha = document.getElementById(`viagem-${idViagem}`);
            if (linha) {
                linha.remove();
            }
        } else {
            alert("Erro ao excluir: " + (dados.erro || "Falha desconhecida"));
        }
    })
    .catch(err => {
        console.error("Erro na requisição de exclusão:", err);
        alert("Não foi possível conectar ao servidor para excluir o registro.");
    });
}