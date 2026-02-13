function setupCheckboxes() {
    const containers = document.querySelectorAll('.checkbox-container');

    containers.forEach(container => {
        if (container.dataset.checkboxInit) return;
        container.dataset.checkboxInit = "1";

        container.addEventListener('change', function(e) {
            const target = e.target;

            if (target.type === 'checkbox' && !target.checked) {
                const nbCoches = container.querySelectorAll('input[type="checkbox"]:checked').length;
                if (nbCoches === 0) {
                    target.checked = true;
                    alert("Attention : Vous ne pouvez pas décocher toutes les valeurs.\nUn critère doit avoir au moins une option active.");
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", setupCheckboxes);
document.addEventListener("dom-refreshed", setupCheckboxes);