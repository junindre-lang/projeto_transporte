// 1. Inicialização do Mapa focado na região de Sousa
var map = L.map('map').setView([-6.7578, -38.2325], 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Arrays para controle do fluxo de cliques e elementos gráficos
var pontosClicados = [];
var arrayPontosEnvio = [];
var marcadoresTemporarios = [];

// Linha da rota (Verde viva, grossa e acompanhando as ruas)
var linhaTratada = L.polyline([], {
    color: '#2ecc71',
    weight: 6,
    opacity: 0.9,
    lineJoin: 'round'
}).addTo(map);

// 2. Evento de Clique - Mapeia a Origem e o Destino
map.on('click', function(e) {
    if (pontosClicados.length >= 2) {
        alert("Você já definiu a Origem e o Destino! Clique em 'Limpar Trajeto' para refazer.");
        return;
    }

    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    pontosClicados.push({ lat: lat, lon: lon });
    atualizarContadorVisual(pontosClicados.length);

    var legenda = pontosClicados.length === 1 ? "Origem (Início)" : "Destino (Fim)";
    var novoMarcador = L.marker([lat, lon]).addTo(map).bindPopup(`<b>${legenda}</b>`).openPopup();
    marcadoresTemporarios.push(novoMarcador);

    if (pontosClicados.length === 2) {
        calcularRotaNasRuas();
    }
});

// 3. Busca o trajeto real do mapa pelas ruas e aplica o Zoom
function calcularRotaNasRuas() {
    var origem = pontosClicados[0];
    var destino = pontosClicados[1];

    var urlOSRM = `https://router.project-osrm.org/route/v1/driving/${origem.lon},${origem.lat};${destino.lon},${destino.lat}?overview=full&geometries=geojson`;

    fetch(urlOSRM)
        .then(response => response.json())
        .then(data => {
            if (data.code === 'Ok' && data.routes.length > 0) {
                var coordenadasRuas = data.routes[0].geometry.coordinates;
                var caminhoFormatado = coordenadasRuas.map(ponto => [ponto[1], ponto[0]]);

                // Desenha a linha verde no mapa
                linhaTratada.setLatLngs(caminhoFormatado);

                // 🔥 NOVO: Dá zoom automático e enquadra a rota inteira na tela com um respiro (padding)
                map.fitBounds(linhaTratada.getBounds(), { padding: [50, 50] });

                // Alimenta a lista que será enviada ao banco de dados
                arrayPontosEnvio = coordenadasRuas.map(ponto => ({ lat: ponto[1], lon: ponto[0] }));
            } else {
                alert("Não foi possível traçar uma rota automática entre essas ruas.");
            }
        })
        .catch(err => {
            console.error("Erro na API OSRM:", err);
            alert("Erro de conexão ao calcular trajeto pelas ruas.");
        });
}

// 4. Atualiza o texto do painel lateral de forma flexível
function atualizarContadorVisual(quantidade) {
    var elemento = document.getElementById('qtd-pontos');
    if (elemento) {
        elemento.innerText = quantidade + " / 2";
    } else {
        // Caso o elemento não tenha ID, procura pelo texto do bloco verde na sidebar
        var spans = document.querySelectorAll('span, div, p');
        spans.forEach(el => {
            if (el.textContent.includes('Pontos marcados:')) {
                el.innerHTML = `Pontos marcados: <strong>${quantidade} / 2</strong>`;
            }
        });
    }
}

// 5. Limpa o mapa por completo
function limparMapa() {
    marcadoresTemporarios.forEach(marcador => map.removeLayer(marcador));
    marcadoresTemporarios = [];
    pontosClicados = [];
    arrayPontosEnvio = [];
    linhaTratada.setLatLngs([]);
    atualizarContadorVisual(0);
}

// 6. Envia o trajeto mapeado para o Servidor salvar no Banco
function enviarRota() {
    if (arrayPontosEnvio.length < 2) {
        alert("Por favor, marque a Origem e o Destino no mapa antes de salvar.");
        return;
    }

    const nomeDaRota = prompt("Digite um nome de identificação para esta rota:", "Sousa - Centro");
    if (!nomeDaRota) {
        alert("A rota precisa de um nome descritivo para ser salva!");
        return;
    }

    fetch('/api/viagem/criar-via-mapa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            rota: nomeDaRota,
            pontos: arrayPontosEnvio
        })
    })
    .then(response => response.json())
    .then(dados => {
        if (dados.sucesso) {
            alert("Sucesso: A rota foi salva e a viagem criada!");
            window.location.href = '/list_viagem'; // Redireciona para a lista geral
        } else {
            alert("Erro ao salvar rota: " + (dados.erro || "Falha interna"));
        }
    })
    .catch(err => {
        console.error("Erro na requisição AJAX:", err);
        alert("Não foi possível conectar ao servidor.");
    });
}

// 🔥 NOVO: Ativa o funcionamento dos botões mapeando o clique pelos nomes visuais
document.addEventListener("DOMContentLoaded", function() {
    var botoes = document.querySelectorAll('button, a');

    botoes.forEach(btn => {
        if (btn.textContent.includes('Salvar Rota Planejada')) {
            btn.addEventListener('click', enviarRota);
        }
        if (btn.textContent.includes('Limpar Trajeto')) {
            btn.addEventListener('click', limparMapa);
        }
    });
});