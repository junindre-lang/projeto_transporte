// ==========================================================================
// ENVIO E VALIDAÇÃO DO CADASTRO DE HORÁRIOS FIXOS
// ==========================================================================
function salvarHorarioFixo(event) {
    event.preventDefault();

    // 1. Obtém os dias marcados (name="dias" sincronizado com o HTML)
    const caixasDias = document.querySelectorAll('input[name="dias"]:checked');
    const diasSelecionados = [];

    caixasDias.forEach((checkbox) => {
        diasSelecionados.push(checkbox.value);
    });

    if (diasSelecionados.length === 0) {
        alert("Erro: Selecione pelo menos um dia da semana para vincular este horário.");
        return;
    }

    // 2. Mapeamento perfeito dos IDs do HTML
    const dadosFormulario = {
        motorista: document.getElementById('motorista').value,
        veiculo: document.getElementById('veiculo').value,
        rota_nome: document.getElementById('rota-nome').value,
        horario_partida: document.getElementById('horario-partida').value,
        horario_retorno: document.getElementById('horario-retorno').value || null,
        dias_semana: diasSelecionados,
        itinerario: document.getElementById('itinerario').value
    };

    // 3. Envio dos dados para a API Flask
    fetch('/api/horarios/cadastrar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dadosFormulario)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            alert("Sucesso: Nova grade de horários cadastrada com sucesso!");
            window.location.href = '/pag_admin';
        } else {
            alert("Não foi possível salvar: " + data.erro);
        }
    })
    .catch(error => {
        console.error("Erro na comunicação HTTP:", error);
        alert("Erro crítico: Falha ao estabelecer contato com o servidor do EXPRESSO.");
    });
}