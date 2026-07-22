let emViagem = false;

document.addEventListener("DOMContentLoaded", () => {
    carregarViagens();
});

// 1. Busca as viagens direcionadas ao motorista no backend
function carregarViagens() {
    fetch('/api/motorista/viagens-agendadas')
        .then(res => res.json())
        .then(viagens => {
            const container = document.getElementById('lista-viagens');
            container.innerHTML = '';

            if (!viagens || viagens.length === 0) {
                container.innerHTML = `
                    <div class="sem-viagens">
                        <i class="fa-solid fa-calendar-xmark"></i>
                        <p>Nenhuma viagem direcionada no momento.</p>
                    </div>`;
                return;
            }

            viagens.forEach(v => {
                container.innerHTML += `
                    <div class="card-viagem" id="viagem-${v.id}">
                        <div class="header-card">
                            <span class="tag-id">Viagem #${v.id}</span>
                            <span class="horario"><i class="fa-regular fa-clock"></i> ${v.horario}</span>
                        </div>
                        <div class="detalhes-viagem">
                            <h3><i class="fa-solid fa-location-dot"></i> ${v.rota}</h3>
                            <p><i class="fa-solid fa-van-shuttle"></i> <strong>Veículo:</strong> ${v.veiculo}</p>
                        </div>
                        <div class="acoes-viagem">
                            <button id="btn-acao-${v.id}" onclick="alternarEstadoViagem(${v.id})" class="btn-iniciar">
                                <i class="fa-solid fa-play"></i> Iniciar Viagem
                            </button>
                        </div>
                    </div>
                `;
            });
        })
        .catch(err => {
            console.error("Erro ao carregar viagens:", err);
            document.getElementById('lista-viagens').innerHTML = `
                <div class="sem-viagens">
                    <p style="color: #e74c3c;">Erro ao conectar com o servidor.</p>
                </div>`;
        });
}

// 2. Controla a troca de estado (Iniciar / Concluir)
function alternarEstadoViagem(idViagem) {
    if (!emViagem) {
        iniciarViagem(idViagem);
    } else {
        concluirViagem(idViagem);
    }
}

// 3. API: Iniciar Viagem (Status do motorista muda para Indisponível / Em Viagem)
function iniciarViagem(id) {
    fetch('/api/motorista/iniciar-viagem', { method: 'POST' })
        .then(res => res.json())
        .then(dados => {
            if (dados.status === 'sucesso') {
                emViagem = true;

                // Atualiza Status para Indisponível
                const badge = document.getElementById('badge-status');
                badge.className = 'badge indisponivel';
                document.getElementById('texto-status').innerText = 'Indisponível (Em Viagem)';

                // Atualiza o botão da viagem ativa para Concluir
                const btn = document.getElementById(`btn-acao-${id}`);
                btn.className = 'btn-concluir';
                btn.innerHTML = '<i class="fa-solid fa-flag-checkered"></i> Concluir Viagem';

                alert("Boa viagem! Seu veículo está sendo monitorado em tempo real.");
            }
        })
        .catch(err => console.error("Erro ao iniciar viagem:", err));
}

// 4. API: Concluir Viagem (Status do motorista volta para Disponível)
function concluirViagem(id) {
    fetch('/api/motorista/concluir-viagem', { method: 'POST' })
        .then(res => res.json())
        .then(dados => {
            if (dados.status === 'sucesso') {
                emViagem = false;

                // Atualiza Status para Disponível
                const badge = document.getElementById('badge-status');
                badge.className = 'badge disponivel';
                document.getElementById('texto-status').innerText = 'Disponível';

                // Remove o card da viagem concluída
                const card = document.getElementById(`viagem-${id}`);
                if (card) card.remove();

                alert("Viagem finalizada com sucesso! Seu status foi alterado para Disponível.");
                carregarViagens(); // Busca se há novas viagens atribuídas
            }
        })
        .catch(err => console.error("Erro ao concluir viagem:", err));
}

// 5. API: Ficar Livre / Disponível
function ficarLivre() {
    fetch('/api/motorista/status-livre', { method: 'POST' })
        .then(res => res.json())
        .then(dados => {
            const badge = document.getElementById('badge-status');
            badge.className = 'badge disponivel';
            document.getElementById('texto-status').innerText = 'Disponível';
            alert(dados.mensagem);
        })
        .catch(err => console.error("Erro ao atualizar status:", err));
}