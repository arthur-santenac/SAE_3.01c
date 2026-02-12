class Page {
    constructor() {
        console.log("Page: Initialisée");
    }

    async getStats(informations) {
        const réponse = await fetch("/api/calculer_stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(informations)
        });
        return await réponse.json();
    }

    async exporterGroupes(informations) {
        const réponse = await fetch("/exporter_groupes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(informations)
        });
        return await réponse.blob();
    }

    async relancerRepartition(informations) {
        const réponse = await fetch("/repartition/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(informations)
        });
        return await réponse.text();
    }
}


class DragAndDrop {
    constructor() {
        this.élémentEnCoursDeDéplacement = null;
        this.init();

        document.addEventListener('dom-refreshed', () => {
            this.init();
        });
    }

    init() {
        this.ajouterDragEvent();
        this.ajouterDragZone();
    }

    ajouterDragEvent() {
        const lignes = document.querySelectorAll(".liste-eleves tr.eleve");
        lignes.forEach(ligne => {
            ligne.addEventListener("dragstart", (e) => this.dragStart(e, ligne));
            ligne.addEventListener("dragend", () => this.dragEnd(ligne));
        });
    }

    ajouterDragZone() {
        const zonesDeDépôt = document.querySelectorAll(".liste-eleves");
        zonesDeDépôt.forEach(corpsTableau => {
            const tableau = corpsTableau.closest("table");
            corpsTableau.addEventListener("dragover", (e) => this.dragOver(e, tableau));
            corpsTableau.addEventListener("dragleave", (e) => this.dragLeave(e, corpsTableau, tableau));
            corpsTableau.addEventListener("drop", (e) => this.handleDrop(e, corpsTableau, tableau));
        });
    }

    dragStart(e, ligne) {
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/html", ligne.innerHTML);
        this.élémentEnCoursDeDéplacement = ligne;
        ligne.classList.add("dragging");
    }

    dragEnd(ligne) {
        ligne.classList.remove("dragging");
        this.élémentEnCoursDeDéplacement = null;
    }

    dragOver(e, tableau) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        if (tableau) tableau.classList.add("over");
    }

    dragLeave(e, corpsTableau, tableau) {
        if (!corpsTableau.contains(e.relatedTarget) && tableau) {
            tableau.classList.remove("over");
        }
    }

    handleDrop(e, corpsTableau, tableau) {
        e.preventDefault();
        if (tableau) tableau.classList.remove("over");

        if (!this.élémentEnCoursDeDéplacement) return;

        corpsTableau.querySelector("tbody").appendChild(this.élémentEnCoursDeDéplacement);
        this.updateRowActions(this.élémentEnCoursDeDéplacement, corpsTableau);

        document.dispatchEvent(new CustomEvent('update-counts'));
    }

    updateRowActions(ligne, corpsTableau) {
        const estDansUnGroupe = corpsTableau.closest("#eleves_classes") !== null;
        const estDansLaSectionRestants = corpsTableau.closest("#eleves_restants") !== null;
        const celluleActions = ligne.querySelector("td.actions");

        if (!celluleActions) return;

        const btnSupprimer = celluleActions.querySelector(".supprimer");

        if (estDansUnGroupe && !btnSupprimer) {
            const nouveauBouton = document.createElement("button");
            nouveauBouton.className = "supprimer";
            nouveauBouton.setAttribute("aria-label", "Supprimer");
            nouveauBouton.textContent = "×";
            celluleActions.appendChild(nouveauBouton);
        } else if (estDansLaSectionRestants && btnSupprimer) {
            btnSupprimer.remove();
        }
    }
}


class Interface {
    constructor(apiService) {
        this.apiService = apiService;
        this.init();
    }

    init() {
        this.miseAJourCompteur();
        this.action();

        document.addEventListener('update-counts', () => {
            this.miseAJourCompteur();
            this.miseAJourSats();
        });
    }

    action() {
        document.addEventListener("click", (e) => {
            const btnPopup = e.target.closest(".btn-popup");
            if (btnPopup) {
                this.popup(btnPopup.dataset.target, true);
                return;
            }
            const btnValider = e.target.closest(".btn-valider");
            if (btnValider) {
                this.popup(btnValider.dataset.target, false);
                return;
            }

            if (e.target.classList.contains("supprimer")) {
                this.suprimer(e);
                return;
            }

            if (e.target.closest("#btn-relancer")) {
                this.relancerRepartition();
                return;
            }

            if (e.target.closest("#exporter")) {
                this.exporter();
                return;
            }
        });
    }

    miseAJourCompteur() {
        document.querySelectorAll("article").forEach((article) => {
            const corpsTableau = article.querySelector(".liste-eleves tbody");
            const spanCompteur = article.querySelector(".count");
            if (corpsTableau && spanCompteur) {
                const nombreEleves = corpsTableau.querySelectorAll("tr.eleve").length;
                spanCompteur.textContent = `${nombreEleves} ${nombreEleves > 1 ? "élèves" : "élève"}`;
            }
        });
    }

    async miseAJourSats() {
        const nomsCritères = this.collectCriteriaNames();
        const donnéesGroupes = this.collectGroupsData(nomsCritères);

        const dicoImportance = {};
        document.querySelectorAll('.section-importance input[type="number"]').forEach((input) => {
            const valeur = parseInt(input.value);
            if (input.name && !isNaN(valeur)) dicoImportance[input.name] = valeur;
        });

        const stats = await this.apiService.getStats({
            groupes: donnéesGroupes,
            dico_importance: dicoImportance
        });

        if (stats && stats.success) {
            const conteneurStats = document.querySelector(".stats-row");
            if (!conteneurStats) return;

            const indicateurs = conteneurStats.querySelectorAll(".stat-item");
            if (indicateurs.length >= 1) {
                const indicateurRespect = indicateurs[0];
                const valeurRespect = indicateurRespect.querySelector(".stat-value");
                const barreRespect = indicateurRespect.querySelector(".fill");
                if (valeurRespect) valeurRespect.textContent = `${stats.score}%`;
                if (barreRespect) barreRespect.style.width = `${stats.score}%`;
            }

            if (indicateurs.length >= 2) {
                const indicateurPlace = indicateurs[1];
                const valeurPlace = indicateurPlace.querySelector(".stat-value");
                const barrePlace = indicateurPlace.querySelector(".fill");
                if (valeurPlace) valeurPlace.textContent = stats.place_text;
                if (barrePlace) {
                    barrePlace.style.width = `${stats.prc_place}%`;
                    if (stats.is_complete) {
                        barrePlace.classList.replace("red", "blue");
                    } else {
                        barrePlace.classList.replace("blue", "red");
                    }
                }
            }
        }
    }

    suprimer(e) {
        const ligne = e.target.closest("tr");
        const corpsRestants = document.querySelector("#eleves_restants .liste-eleves tbody");
        if (ligne && corpsRestants) {
            corpsRestants.appendChild(ligne);
            e.target.remove();
            document.dispatchEvent(new CustomEvent('update-counts'));
        }
    }

    collectCriteriaNames() {
        const liste = [];
        const premierTableau = document.querySelector(".liste-eleves");
        if (premierTableau) {
            const cellulesEntête = premierTableau.querySelectorAll("thead th, thead td");
            cellulesEntête.forEach((cellule) => {
                const texte = cellule.textContent.trim();
                if (texte && !["Num", "Prénom", "Nom", "Actions"].includes(texte)) {
                    liste.push(texte);
                }
            });
        }
        return liste;
    }

    collectGroupsData(nomsCritères) {
        const tousLesGroupes = [];
        const traiterLignes = (lignes) => {
            const eleves = [];
            lignes.forEach(ligne => {
                const cellules = ligne.querySelectorAll("td");
                if (cellules.length < 3) return;
                const eleve = {
                    num: cellules[0].textContent.trim(),
                    prenom: cellules[1].textContent.trim(),
                    nom: cellules[2].textContent.trim(),
                    criteres: {}
                };
                nomsCritères.forEach((critère, index) => {
                    if (cellules[3 + index]) {
                        eleve.criteres[critère] = cellules[3 + index].textContent.trim();
                    }
                });
                eleves.push(eleve);
            });
            return eleves;
        };

        document.querySelectorAll("#eleves_classes article").forEach((article) => {
            const lignes = article.querySelectorAll(".liste-eleves tr.eleve");
            tousLesGroupes.push(traiterLignes(lignes));
        });
        const lignesRestantes = document.querySelectorAll("#eleves_restants .liste-eleves tr.eleve");
        tousLesGroupes.push(traiterLignes(lignesRestantes));
        return tousLesGroupes;
    }

    async relancerRepartition() {
        const chargeur = document.getElementById("loader-overlay");
        if (chargeur) chargeur.style.display = "flex";
        const dicoImportance = {};
        document.querySelectorAll('.section-importance input[type="number"]').forEach((input) => {
            const valeur = parseInt(input.value);
            if (input.name && !isNaN(valeur)) dicoImportance[input.name] = valeur;
        });
        const criteresGroupes = [];
        document.querySelectorAll('.overlay .popup-card').forEach((modale) => {
            const titre = modale.querySelector('h3').textContent;
            const match = titre.match(/\d+/);
            const numGroupe = match ? parseInt(match[0]) : 0;

            modale.querySelectorAll('fieldset').forEach((fieldset) => {
                const nomCrit = fieldset.querySelector('legend').textContent;
                const valeursCochées = Array.from(fieldset.querySelectorAll('input:checked')).map(cb => cb.value);
                if (valeursCochées.length > 0) {
                    criteresGroupes.push({
                        groupe: numGroupe,
                        nom_critere: nomCrit,
                        valeurs: valeursCochées
                    });
                }
            });
        });

        const nouveauHtml = await this.apiService.relancerRepartition({
            dico_importance: dicoImportance,
            criteres_groupes: criteresGroupes
        });

        const analyseur = new DOMParser();
        const doc = analyseur.parseFromString(nouveauHtml, 'text/html');
        document.body.innerHTML = doc.body.innerHTML;
        document.dispatchEvent(new CustomEvent('dom-refreshed'));

        const chargeurActuel = document.getElementById("loader-overlay");
        if (chargeurActuel) chargeurActuel.style.display = "none";
    }

    async exporter() {
        const nomsCritères = this.collectCriteriaNames();
        const groupesBruts = this.collectGroupsData(nomsCritères);
        const tousLesElevesPlats = [];
        groupesBruts.forEach((groupe, indexGroupe) => {
            const estDernierGroupe = indexGroupe === groupesBruts.length - 1;
            const nomGroupe = estDernierGroupe ? "Non classé" : (indexGroupe + 1);
            
            groupe.forEach(eleve => {
                const valeursCriteres = nomsCritères.map(nom => eleve.criteres[nom] || "");
                
                tousLesElevesPlats.push({
                    num: eleve.num,
                    nom: eleve.nom,
                    prenom: eleve.prenom,
                    criteres: valeursCriteres,
                    groupe: nomGroupe
                });
            });
        });

        const blocDonnées = await this.apiService.exporterGroupes({
            eleves: tousLesElevesPlats,
            noms_criteres: nomsCritères
        });

        const url = window.URL.createObjectURL(blocDonnées);
        const lien = document.createElement("a");
        lien.href = url;
        lien.download = "groupes_finaux.csv";
        document.body.appendChild(lien);
        lien.click();
        lien.remove();
        window.URL.revokeObjectURL(url);
    }

    popup(id, estVisible) {
        const modale = document.getElementById(id);
        if (modale) modale.style.display = estVisible ? "block" : "none";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const apiService = new Page();
    new DragAndDrop();
    new Interface(apiService);
});


function submitWithLoader() {
    const loader = document.getElementById('loader-overlay');
    if (loader) {
        loader.style.display = 'flex';
    }
    setTimeout(() => {
        const form = document.getElementById('form-repartition');
        if (form) {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'btn';
            hiddenInput.value = 'btn-repartition';
            form.appendChild(hiddenInput);
            form.submit();
        }
    }, 50);
}