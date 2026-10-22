document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".pagina-transito #sidebar, .sidebar, .sidebar-rotas");

    if (sidebar) {
        const mobileViewport = window.matchMedia("(max-width: 768px)");

        if (!sidebar.id) {
            sidebar.id = "mobile-sidebar";
        }

        if (sidebar.classList.contains("sidebar-rotas")) {
            document.body.classList.add("mobile-route-page");
        }

        const toggleButton = document.createElement("button");
        toggleButton.className = "mobile-sidebar-toggle";
        toggleButton.type = "button";
        toggleButton.setAttribute("aria-label", "Abrir menu");
        toggleButton.setAttribute("aria-controls", sidebar.id);
        toggleButton.setAttribute("aria-expanded", "false");
        toggleButton.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';

        const overlay = document.createElement("button");
        overlay.className = "mobile-sidebar-overlay";
        overlay.type = "button";
        overlay.setAttribute("aria-label", "Fechar menu");
        overlay.hidden = true;

        function setSidebarOpen(isOpen) {
            document.body.classList.toggle("mobile-sidebar-open", isOpen);
            toggleButton.setAttribute("aria-expanded", String(isOpen));
            toggleButton.setAttribute("aria-label", isOpen ? "Fechar menu" : "Abrir menu");
            overlay.hidden = !isOpen;
            sidebar.inert = mobileViewport.matches && !isOpen;
        }

        setSidebarOpen(false);
        document.body.append(toggleButton, overlay);
        const handleViewportChange = function (event) {
            sidebar.inert = event.matches && !document.body.classList.contains("mobile-sidebar-open");
        };

        if (mobileViewport.addEventListener) {
            mobileViewport.addEventListener("change", handleViewportChange);
        } else {
            mobileViewport.addListener(handleViewportChange);
        }

        toggleButton.addEventListener("click", function () {
            setSidebarOpen(!document.body.classList.contains("mobile-sidebar-open"));
        });

        overlay.addEventListener("click", function () {
            setSidebarOpen(false);
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && document.body.classList.contains("mobile-sidebar-open")) {
                setSidebarOpen(false);
                toggleButton.focus();
            }
        });

        sidebar.querySelectorAll(".sidebar-menu a, .sidebar-footer a").forEach(function (link) {
            link.addEventListener("click", function () {
                setSidebarOpen(false);
            });
        });
    }

    const searchInput = document.querySelector(".sidebar .search-box input, .sidebar-rotas .search-box input, #sidebar .search-box input");
    const menuItems = document.querySelectorAll(".sidebar-menu li");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim().toLocaleLowerCase();
        menuItems.forEach(function (item) {
            item.hidden = !item.textContent.toLocaleLowerCase().includes(query);
        });
    });
});
