  const lists = document.querySelectorAll(".liste-eleves");
  const items = document.querySelectorAll(".liste-eleves li.eleve");

  function updateCounts() {
      document.querySelectorAll("article").forEach(article => {
          const list = article.querySelector(".liste-eleves");
          const countSpan = article.querySelector(".count");
          if (list && countSpan) {
              const nb = list.querySelectorAll("li.eleve").length;
              countSpan.textContent = nb + (nb > 1 ? " élèves" : " élève");
          }
      });
  }
  items.forEach(item => {
      item.addEventListener("dragstart", e => {
          e.dataTransfer.setData("text/plain", e.target.textContent);
          e.target.classList.add("dragging");
      });
      item.addEventListener("dragend", e => {
          e.target.classList.remove("dragging");
      });
  });
  lists.forEach(list => {
      list.addEventListener("dragover", e => {
          e.preventDefault();
          list.classList.add("over");
      });
      list.addEventListener("dragleave", () => {
          list.classList.remove("over");
      });
      list.addEventListener("drop", e => {
          e.preventDefault();
          list.classList.remove("over");
          const dragged = document.querySelector(".dragging");
          if (dragged) {
              list.appendChild(dragged);
              if (list.closest('#eleves_classes')) {
                  if (!dragged.querySelector('.supprimer')) {
                      const btnSupprimer = document.createElement('button');
                      btnSupprimer.className = 'supprimer';
                      btnSupprimer.setAttribute('aria-label', 'Supprimer');
                      btnSupprimer.textContent = 'croix';
                      dragged.appendChild(btnSupprimer);
                  }
              } else if (list.closest('#eleves_restants')) {
                  const btnSupprimer = dragged.querySelector('.supprimer');
                  if (btnSupprimer) {
                      btnSupprimer.remove();
                  }
              }
              updateCounts();
          }
      });
  });
  updateCounts();
  document.getElementById('eleves_classes').addEventListener('click', function(e) {
      if (e.target.classList.contains('supprimer')) {
          const li = e.target.closest('li');
          const listeRestants = document.querySelector('#eleves_restants .liste-eleves');
          listeRestants.appendChild(li);
          e.target.remove();
          updateCounts();
      }
  });

  //Page importer

const dropZone = document.getElementById("drop-zone");

dropZone.addEventListener("drop", dropHandler);
window.addEventListener("drop", (e) => {
  if ([...e.dataTransfer.items].some((item) => item.kind === "file")) {
    e.preventDefault();
  }
});
dropZone.addEventListener("dragover", (e) => {
  const fileItems = [...e.dataTransfer.items].filter(
    (item) => item.kind === "file",
  );
  if (fileItems.length > 0) {
    e.preventDefault();
    if (fileItems.some((item) => item.type === "text/csv")) {
      e.dataTransfer.dropEffect = "copy";
    } else {
      e.dataTransfer.dropEffect = "none";
    }
  }
});

window.addEventListener("dragover", (e) => {
  const fileItems = [...e.dataTransfer.items].filter(
    (item) => item.kind === "file",
  );
  if (fileItems.length > 0) {
    e.preventDefault();
    if (!dropZone.contains(e.target)) {
      e.dataTransfer.dropEffect = "none";
    }
  }
});
const preview = document.getElementById("preview");

function displayFiles(files) {
  for (const file of files) {
    if (file.type === "text/csv" || file.name.endsWith(".csv")) {
      const li = document.createElement("li");
      li.appendChild(document.createTextNode(file.name));
      preview.appendChild(li);
    }
  }
}

function dropHandler(ev) {
  ev.preventDefault();
  const files = [...ev.dataTransfer.items]
    .map((item) => item.getAsFile())
    .filter((file) => file);
  displayFiles(files);
}
const fileInput = document.getElementById("file-input");
fileInput.addEventListener("change", (e) => {
  displayFiles(e.target.files);
});
const clearBtn = document.getElementById("clear-btn");
clearBtn.addEventListener("click", () => {
  preview.textContent = "";
});