// 1. Inicializa o mapa centralizado em Sousa, PB
var centroMapa = [-6.7578, -38.2325];
var map = L.map('map').setView(centroMapa, 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Estruturas de controle dos marcadores em rota
var marcadoresVeiculos = {};

/**
 * Consome a API do Flask para atualizar os veículos no mapa
 */
function buscarDadosTransito() {
    // Requisição para a rota criada no Flask
    fetch('/api/transito/tempo-real')
        .then(response => response.json())
        .then(viagens => {

            if (viagens.length === 0) {
                document.getElementById('transporte-status').innerText = "Nenhuma viagem em andamento";
                document.getElementById('status-conexao').classList.remove('connected');
                return;
            }

            document.getElementById('transporte-status').innerText = `${viagens.length} viagem(ns) ativa(s)`;
            document.getElementById('status-conexao').classList.add('connected');
            document.getElementById('transporte-atualizacao').innerText = new Date().toLocaleTimeString();

            viagens.forEach(viagem => {
                var posicao = [viagem.lat, viagem.lon];

                // Atualiza a barra lateral com os dados da primeira viagem encontrada
                document.getElementById('info-motorista').innerText = viagem.motorista;
                document.getElementById('info-veiculo').innerText = viagem.veiculo;
                document.getElementById('info-rota').innerText = viagem.rota;
                document.getElementById('info-velocidade').innerText = viagem.velocidade + " km/h";

                // Se o marcador dessa viagem específica já existe, move. Se não, cria.
                if (!marcadoresVeiculos[viagem.id]) {
                    marcadoresVeiculos[viagem.id] = L.marker(posicao).addTo(map)
                        .bindPopup(`
                            <b>Motorista:</b> ${viagem.motorista}<br>
                            <b>Veículo:</b> ${viagem.veiculo}<br>
                            <b>Rota:</b> ${viagem.rota}<br>
                            <b>Velocidade:</b> ${viagem.velocidade} km/h
                        `);
                } else {
                    marcadoresVeiculos[viagem.id].setLatLng(posicao);
                    marcadoresVeiculos[viagem.id].getPopup().setContent(`
                        <b>Motorista:</b> ${viagem.motorista}<br>
                        <b>Veículo:</b> ${viagem.veiculo}<br>
                        <b>Rota:</b> ${viagem.rota}<br>
                        <b>Velocidade:</b> ${viagem.velocidade} km/h
                    `);
                }
            });
        })
        .catch(error => {
            console.error("Erro ao buscar dados de trânsito:", error);
            document.getElementById('transporte-status').innerText = "Erro de conexão com o servidor";
            document.getElementById('status-conexao').classList.remove('connected');
        });
}

// Executa a busca assim que a página carrega
buscarDadosTransito();

// Fica atualizando de forma limpa a cada 5 segundos (5000ms)
setInterval(buscarDadosTransito, 5000);