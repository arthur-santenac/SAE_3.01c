// Sélection des tableaux et des lignes d'élèves
const tables = document.querySelectorAll(".liste-eleves tbody");
const rows = document.querySelectorAll(".liste-eleves tr.eleve");

// Fonction pour mettre à jour les compteurs d'élèves
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

// Configuration du drag & drop pour les lignes d'élèves
rows.forEach(row => {
  // Début du drag
  row.addEventListener("dragstart", e => {
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", row.innerHTML);
    row.classList.add("dragging");
  });

  // Fin du drag
  row.addEventListener("dragend", e => {
    row.classList.remove("dragging");
  });
});

// Configuration des zones de drop (tbody des tableaux)
tables.forEach(tbody => {
  const table = tbody.closest("table");
  
  // Survol de la zone de drop
  tbody.addEventListener("dragover", e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (table) table.classList.add("over");
  });

  // Sortie de la zone de drop
  tbody.addEventListener("dragleave", e => {
    // Vérifier qu'on quitte vraiment le tbody
    if (!tbody.contains(e.relatedTarget)) {
      if (table) table.classList.remove("over");
    }
  });

  // Drop de l'élément
  tbody.addEventListener("drop", e => {
    e.preventDefault();
    if (table) table.classList.remove("over");
    
    const dragged = document.querySelector(".dragging");
    if (!dragged) return;

    // Vérifier si on est dans la section des classes ou des restants
    const isInClassesSection = tbody.closest('#eleves_classes') !== null;
    const isInRestantsSection = tbody.closest('#eleves_restants') !== null;

    // Déplacer la ligne
    tbody.appendChild(dragged);

    // Gestion du bouton supprimer
    const actionsCell = dragged.querySelector('td.actions');
    if (actionsCell) {
      const btnSupprimer = actionsCell.querySelector('.supprimer');
      
      if (isInClassesSection) {
        // Ajouter le bouton supprimer s'il n'existe pas
        if (!btnSupprimer) {
          const newBtnSupprimer = document.createElement('button');
          newBtnSupprimer.className = 'supprimer';
          newBtnSupprimer.setAttribute('aria-label', 'Supprimer');
          newBtnSupprimer.textContent = '×';
          actionsCell.appendChild(newBtnSupprimer);
        }
      } else if (isInRestantsSection) {
        // Supprimer le bouton supprimer s'il existe
        if (btnSupprimer) {
          btnSupprimer.remove();
        }
      }
    }

    // Mettre à jour les compteurs
    updateCounts();
  });
});

// Gestion du clic sur le bouton supprimer (retour aux élèves restants)
document.getElementById('eleves_classes').addEventListener('click', function(e) {
  if (e.target.classList.contains('supprimer')) {
    const row = e.target.closest('tr');
    if (!row) return;

    // Trouver le tbody des élèves restants
    const tbodyRestants = document.querySelector('#eleves_restants .liste-eleves tbody');
    if (!tbodyRestants) return;

    // Déplacer la ligne
    tbodyRestants.appendChild(row);

    // Supprimer le bouton supprimer
    e.target.remove();

    // Mettre à jour les compteurs
    updateCounts();
  }
});

// Initialisation des compteurs au chargement
updateCounts();