document.addEventListener('DOMContentLoaded', function() {

    // Gestion de l'affichage du nombre d'élèves
    const tables = document.querySelectorAll(".liste-eleves");
    const rows = document.querySelectorAll(".liste-eleves tr.eleve");

    function updateCounts() {
        document.querySelectorAll("article").forEach(article => {
            const tbody = article.querySelector(".liste-eleves tbody");
            const countSpan = article.querySelector(".count");
            if (tbody && countSpan) {
                const nb = tbody.querySelectorAll("tr.eleve").length;
                countSpan.textContent = nb + (nb > 1 ? " élèves" : " élève");
            }
        });
    }

    // Gestion du Drag & Drop
    rows.forEach(row => {
        row.addEventListener("dragstart", e => {
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData("text/html", row.innerHTML);
            row.classList.add("dragging");
        });
        row.addEventListener("dragend", e => {
            row.classList.remove("dragging");
        });
    });

    tables.forEach(tbody => {
        const table = tbody.closest("table");
        tbody.addEventListener("dragover", e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            if (table) table.classList.add("over");
        });
        tbody.addEventListener("dragleave", e => {
            if (!tbody.contains(e.relatedTarget)) {
                if (table) table.classList.remove("over");
            }
        });
        tbody.addEventListener("drop", e => {
            e.preventDefault();
            if (table) table.classList.remove("over");
            const dragged = document.querySelector(".dragging");
            if (!dragged) return;
            const isInClassesSection = tbody.closest('#eleves_classes') !== null;
            const isInRestantsSection = tbody.closest('#eleves_restants') !== null;
            table.querySelector("tbody").appendChild(dragged);
            const actionsCell = dragged.querySelector('td.actions');
            if (actionsCell) {
                const btnSupprimer = actionsCell.querySelector('.supprimer');
                if (isInClassesSection) {
                    if (!btnSupprimer) {
                        const newBtnSupprimer = document.createElement('button');
                        newBtnSupprimer.className = 'supprimer';
                        newBtnSupprimer.setAttribute('aria-label', 'Supprimer');
                        newBtnSupprimer.textContent = '×';
                        actionsCell.appendChild(newBtnSupprimer);
                    }
                } else if (isInRestantsSection) {
                    if (btnSupprimer) {
                        btnSupprimer.remove();
                    }
                }
            }
            updateCounts();
        });
    });

    // Gestion des suppressions
    const containerClasses = document.getElementById('eleves_classes');
    if (containerClasses) {
        containerClasses.addEventListener('click', function(e) {
            if (e.target.classList.contains('supprimer')) {
                const row = e.target.closest('tr');
                if (!row) return;
                const tbodyRestants = document.querySelector('#eleves_restants .liste-eleves tbody');
                if (!tbodyRestants) return;
                tbodyRestants.appendChild(row);
                e.target.remove();
                updateCounts();
            }
        });
    }


    // Gestion des Pop-up
    const boutonsOuvrir = document.querySelectorAll('.btn-popup');
    boutonsOuvrir.forEach(bouton => {
        bouton.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const modale = document.getElementById(targetId);
            if (modale) modale.style.display = "block";
        });
    });

    const boutonsFermer = document.querySelectorAll('.btn-valider');
    boutonsFermer.forEach(bouton => {
        bouton.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const modale = document.getElementById(targetId);
            if (modale) modale.style.display = "none";
        });
    });
    // gestion du bouton exporter
    const btnExporter = document.getElementById("exporter");
    if (btnExporter) {
        btnExporter.addEventListener("click", () => {
            fetch("/exporter_groupes", {
                    method: "POST",
                    headers: {
                        "Content-Type": "text/html"
                    },
                    body: document.documentElement.outerHTML,
                })
                .then(res => {
                    if (res.ok) return res.blob();
                    throw new Error("Erreur lors de la génération du fichier");
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = "groupes_finaux.csv";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                })
                .catch(err => {
                    console.error(err);
                    alert("Une erreur est survenue lors du téléchargement.");
                });
        });
    }


    const btnRelancer = document.getElementById("btn-relancer");
    
    if (btnRelancer) {
        btnRelancer.addEventListener("click", () => {


            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(input => {
                if (input.checked) {
                    input.setAttribute('checked', 'checked');
                } else {
                    input.removeAttribute('checked');
                }
            });

            fetch("/repartition/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "text/html"
                    },
                    body: document.documentElement.outerHTML,
                })
                .then(res => {
                    if (res.ok) {
                        return res.text();
                    }
                    throw new Error("Erreur lors du rechargement");
                })
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                })
                .catch(err => {
                    console.error(err);
                    alert("Une erreur est survenue lors du rechargement.");
                });
        });
    }

});
