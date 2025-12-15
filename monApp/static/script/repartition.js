const tables = document.querySelectorAll(".liste-eleves tbody");
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
rows.forEach(row => {
  row.addEventListener("dragstart", e => {
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", row.innerHTML);
    row.classList.add("dragging");
  }
  );
  row.addEventListener("dragend", e => {
    row.classList.remove("dragging");
  }
  );
}
);
tables.forEach(tbody => {
  const table = tbody.closest("table");
  tbody.addEventListener("dragover", e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (table) table.classList.add("over");
  }
  );
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
    tbody.appendChild(dragged);
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
  }
  );
}
);
document.getElementById('eleves_classes').addEventListener('click', function (e) {
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
document.getElementById('eleves_classes').addEventListener('click', function (e) {
  if (e.target.classList.contains('supprimer_critere')) {
    const row = e.target.closest('tr');
    if (!row) return;
    const tbodyRestants = document.querySelector('#eleves_restants .liste-eleves tbody');
    if (!tbodyRestants) return;
    const tr = e.target.closest('tr');
    if (tr) {
      tr.remove();
    }
  }
}
);
updateCounts();
document.getElementById("exporter").addEventListener("click", () => {
  fetch("/exporter_groupes", {
    method: "POST", headers: { "Content-Type": "text/html" }
    , body: document.documentElement.outerHTML,
  }
  )
    .then(res => res.json())
    .then(result => {
      alert("Groupes exportés avec succès !");
      console.log(result);
    }
    )
    .catch(err => console.error(err));
}
);