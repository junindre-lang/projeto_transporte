document.addEventListener("DOMContentLoaded", function () {
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
