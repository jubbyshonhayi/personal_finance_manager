document.addEventListener("DOMContentLoaded", () => {
    const toggleButtons = document.querySelectorAll(".password-toggle");

    for (const button of toggleButtons) {
        button.addEventListener("click", () => {
            const targetId = button.dataset.target;
            const passwordInput = document.getElementById(targetId);

            if (!passwordInput) {
                return;
            }

            const isHidden = passwordInput.type === "password";

            passwordInput.type = isHidden ? "text" : "password";

            button.textContent = isHidden ? "Hide" : "Show";

            button.setAttribute(
                "aria-label",
                isHidden ? "Hide password" : "Show password"
            );

            button.setAttribute(
                "aria-pressed",
                isHidden ? "true" : "false"
            );
        });
    }
});