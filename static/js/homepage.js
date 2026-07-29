document.addEventListener("DOMContentLoaded", function () {
    // ==================================================================
    // 1. LÓGICA DE EMPURRAR / PUXAR A SIDEBAR (TOGGLE)
    // ==================================================================
    const toggleBtn = document.getElementById("sidebar-toggle");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            // Adiciona/Remove a classe 'sidebar-collapsed' no elemento body
            document.body.classList.toggle("sidebar-collapsed");
        });
    }

    // ==================================================================
    // 2. BUSCA DINÂMICA DE OPÇÕES NO MENU LATERAL
    // ==================================================================
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
});