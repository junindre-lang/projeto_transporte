document.addEventListener("DOMContentLoaded", function () {
    // Seleciona o campo de entrada de busca na sidebar
    const searchInput = document.querySelector(".search-box input");
    // Seleciona todas as linhas de opções do menu lateral
    const menuItems = document.querySelectorAll(".sidebar-menu li");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const termoBusca = searchInput.value.toLowerCase().trim();

            menuItems.forEach(function (item) {
                // Obtém o texto do link dentro do li
                const textoOpcao = item.textContent.toLowerCase();

                // Se o texto corresponder ao que foi digitado, exibe. Se não, oculta.
                if (textoOpcao.includes(termoBusca)) {
                    item.style.display = "";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }
});