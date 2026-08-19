document.addEventListener("DOMContentLoaded", function () {
    // Seleciona o campo de entrada de busca na sidebar
    const searchInput = document.querySelector(".search-box input");
    // Seleciona todas as opções da lista do menu lateral
    const menuItems = document.querySelectorAll(".sidebar-menu li");

    // Verifica se a barra de busca existe na página atual antes de aplicar o evento
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const termoBusca = searchInput.value.toLowerCase().trim();

            menuItems.forEach(function (item) {
                // Captura o texto de dentro do link para comparar
                const textoOpcao = item.textContent.toLowerCase();

                // Mostra a opção se corresponder à busca, se não, oculta
                if (textoOpcao.includes(termoBusca)) {
                    item.style.display = "";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }
});