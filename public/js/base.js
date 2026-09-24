document.addEventListener("DOMContentLoaded", () => {
    const navbarToggler =
        document.querySelector("#navbarToggler");
    const navbar =
        document.querySelector("#mainNavbar");

    if (navbarToggler && navbar) {
        navbarToggler.addEventListener("click", () => {
            const isExpanded =
                navbarToggler.getAttribute("aria-expanded") === "true";

            navbarToggler.setAttribute(
                "aria-expanded",
                String(!isExpanded)
            );
            navbar.classList.toggle("navbar-open", !isExpanded);
        });
    }

    const flashMessages =
        document.querySelectorAll(".flash-message");

    for (const message of flashMessages) {
        const closeButton =
            message.querySelector(".flash-close");

        if (closeButton) {
            closeButton.addEventListener("click", () => {
                message.classList.add("flash-message-hidden");
            });
        }

        if (
            message.classList.contains("flash-success") ||
            message.classList.contains("flash-info")
        ) {
            window.setTimeout(() => {
                message.classList.add("flash-message-hidden");
            }, 6000);
        }
    }
});