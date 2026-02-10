document.addEventListener("DOMContentLoaded", function() {
    const containers = document.querySelectorAll('.checkbox-container');
    
    containers.forEach(container => {
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
});