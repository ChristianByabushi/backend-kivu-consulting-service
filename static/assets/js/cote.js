$.ajax({
  type: "get",
  url: "/cotes/fetchInscrits",
  dataType: "json",
  success: function (data) {
    $("#classe").change(function (e) {
      const classe_id = e.target.value;
      const epreuve_id = parseInt($("#epreuve").val());
      const anneeScolaire_id = parseInt($("#anneeScolaire").val());
      const categorie_id = data.epreuves.find(
        (epreuve) => epreuve.id == epreuve_id
      )?.categorie_id;
      const inscritsClasse = data.inscrits.filter(
        (inscrit) => inscrit.classe_id == classe_id
      );
      $("#cours").empty();
      $("#cours").append("<option>Sélectionnez un cours</option>");
      data.cours
        .filter((cours) =>
          data.ponderer.some(
            (ponderation) =>
              cours.id == ponderation.cours_id &&
              ponderation.classe_id == classe_id &&
              ponderation.categorie_id == categorie_id &&
              data.cotes.filter(
                (cote) =>
                  cote.cours_id == cours.id &&
                  cote.anneeScolaire_id == anneeScolaire_id &&
                  cote.epreuve_id == epreuve_id &&
                  cote.anneeScolaire_id == anneeScolaire_id
              ).length != inscritsClasse.length
          )
        )
        .forEach((cours) => {
          $("#cours").append(
            `<option value='${cours.id}'>${cours.designation}</option>`
          );
        });

      $("#cours").change((e) => {
        const cours_id = e.target.value;
        const coterBtn = $("#coter");
        const fiche = $("#fiche");
        const ponderation = data.ponderer.find(
          (ponderation) =>
            ponderation.categorie_id == categorie_id &&
            ponderation.cours_id == cours_id &&
            ponderation.classe_id == classe_id
        )?.max;
        coterBtn.removeAttr("disabled");
        coterBtn.click(function (e) {
          e.preventDefault();
          $("#span_cours").html(
            data.cours.find((cours) => cours.id == cours_id).designation
          );
          fiche.empty();
          fiche.append(
            `<input type='number' name='classe' value='${classe_id}' hidden>`
          );
          fiche.append(
            `<input type='number' name='cours' value='${cours_id}' hidden>`
          );
          inscritsClasse
            .map((inscrit) => {
              const eleve = data.eleves.find(
                (eleveItem) => eleveItem.id == inscrit.eleve_id
              );
              return {
                ...inscrit,
                eleve: `${eleve?.nom} ${eleve?.postnom} ${
                  eleve.prenom == null ? "" : eleve.prenom
                }`,
              };
            })
            .forEach((inscrit) => {
              fiche.append(`
              <div class="row justofy-content-center align-items-center">
              <div class="col-5">
                <span>${inscrit.eleve}</span>
              </div>
              <div class="col-7">
                <div class="input-group mb-3">
                  <input
                    type="number"
                    class="form-control"
                    placeholder="cote"
                    aria-label="cote"
                    min="0"
                    value="0"
                    max="${ponderation}"
                    name="valeur_${inscrit.eleve_id}"
                    aria-describedby="basic-addon1"
                  />
                  <span class="input-group-text" id="basic-addon1"
                    >/${ponderation}</span
                  >
                </div>
              </div>
            </div>
              `);
            });
          $("#fiche input.form-control").on("input", (e) => {
            if (parseInt(e.target.value) > ponderation) {
              $(this).val(ponderation);
            }
          });
        });
      });
    });
  },
});
