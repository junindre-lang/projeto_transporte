const lista = document.getElementById('lista-viagens');
const badge = document.getElementById('badge-status');

function escapeHtml(valor) {
    const div = document.createElement('div');
    div.textContent = valor ?? '';
    return div.innerHTML;
}

function atualizarBadge(status) {
    badge.textContent = status;
    badge.className = `badge ${status === 'Disponível' ? 'disponivel' : 'indisponivel'}`;
}

async function carregarViagensAgendadas() {
    lista.innerHTML = '<p class="carregando">Carregando viagens...</p>';
    const resposta = await fetch('/api/motorista/viagens-agendadas');
    if (!resposta.ok) {
        lista.innerHTML = '<p class="sem-viagens">Não foi possível carregar as viagens.</p>';
        return;
    }
    const viagens = await resposta.json();
    if (!viagens.length) {
        lista.innerHTML = '<p class="sem-viagens">Não há viagens deferidas para você.</p>';
        return;
    }
    lista.innerHTML = viagens.map(v => `
        <article class="card-viagem">
            <div class="header-card"><span class="tag-id">Viagem #${v.id}</span><span class="horario">${escapeHtml(v.horario)}</span></div>
            <div class="detalhes-viagem"><h3>${escapeHtml(v.rota)}</h3><p>Veículo: ${escapeHtml(v.veiculo)}</p><p>Status: ${escapeHtml(v.status)}</p></div>
            <button class="${v.status === 'Em Andamento' ? 'btn-concluir' : 'btn-iniciar'}" data-viagem="${v.id}" data-acao="${v.status === 'Em Andamento' ? 'concluir' : 'iniciar'}">${v.status === 'Em Andamento' ? 'Concluir viagem' : 'Iniciar viagem'}</button>
        </article>`).join('');
}

document.getElementById('btn-status').addEventListener('click', async () => {
    const resposta = await fetch('/api/motorista/status-livre', {method: 'POST'});
    const dados = await resposta.json();
    if (!resposta.ok) return alert(dados.erro);
    atualizarBadge(dados.status);
});

document.getElementById('btn-atualizar').addEventListener('click', carregarViagensAgendadas);
lista.addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-viagem]');
    if (!botao) return;
    const rota = botao.dataset.acao === 'iniciar' ? 'iniciar-viagem' : 'concluir-viagem';
    const resposta = await fetch(`/api/motorista/${rota}`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id_viagem: Number(botao.dataset.viagem)})});
    const dados = await resposta.json();
    if (!resposta.ok) return alert(dados.erro);
    atualizarBadge(dados.status === 'Em Andamento' ? 'Em Viagem' : 'Disponível');
    carregarViagensAgendadas();
});

fetch('/api/motorista/status').then(r => r.ok ? r.json() : null).then(d => d && atualizarBadge(d.status));
carregarViagensAgendadas();
