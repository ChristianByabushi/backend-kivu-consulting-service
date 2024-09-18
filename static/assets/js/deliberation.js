$.ajax({
    url: '/cotes/fetch',
    method: 'GET',
    success: function (data) {
        console.log(data.annee);
        const year = data.annee[0].libelle;
        $('#year').empty()
        $('#year').append(`Espace de deliberation -------- <span>${year}</span>`)

        const classesSelect = $("#classes")
        const coursSelect = $("#cours")

        $("#options").change(e => {
            const optionChoisie = e.target.value;
            classesSelect.empty()
            classesSelect.append(`<option>-------</option>`)

            data.classes.filter(classe => classe.option_id == e.target.value).forEach(classe => {
                classesSelect.append(`<option value=${classe.id}>${classe.designation}</option>`)
            });

            selectedOption = data.options.find(option => option.id == optionChoisie).designation;

            $('#criteres').empty()
            if (selectedOption == 'EB') {
                $('#criteres').append(
                    `
                      <div class="col-6 mb-3">
                        <div class="col form-group">
                          <label for="min" class="fw-extrabold">Pourcentage minimum : </label>
                          <input type="number" class="form-control" value="45" min="0" max="100" id="min">
                        </div>
                        <div class="col form-group">
                          <label for="max" class="fw-extrabold">Pourcentage maximum : </label>
                          <input type="number" class="form-control" value="90" min='0' max="100" id="max">
                        </div>
                      </div>
                      <div class="col-6 form-group">
                        <label for="min" class="fw-extrabold">Domaines à valider</label>
                        <select name="domaine" id="domaines" class="form-control" multiple>
                          <option value="">----------</option>
                        </select>
                      </div>
                    `);
            } else {
                $('#criteres').append(
                    `
                    <div class='row ml-5'>
                        <h3 class='text-primary text-center m-3 text-decoration-underline'>Limites des cas à délibérer selon le pourcentage</h3>
                        <div class="col-6 form-group mb-3">
                            <label for="min" class="fw-extrabold">Pourcentage minimum : </label>
                            <input type="number" class="form-control" value="5" min="0" max="100" id="min">
                        </div>
                        <div class="col-6 form-group mb-3">
                            <label for="max" class="fw-extrabold">Pourcentage maximum : </label>
                            <input type="number" class="form-control" value="10" min='0' max="100" id="max">
                        </div>
                    </div>
                    <h3 class='text-primary text-center text-decoration-underline'>Nombres d'échecs tolérables aux cours selon leur pondération</h3>
                    <div class="col-6 mb-3">
                        <div class="col form-group">
                          <label for="min" class="fw-extrabold">Cours dont TG = 80 : </label>
                          <input type="number" class="form-control" value="5" min="0" max="100" id="tg80">
                        </div>
                        <div class="col form-group">
                          <label for="max" class="fw-extrabold">Cours dont TG = 160 : </label>
                          <input type="number" class="form-control" value="10" min='0' max="100" id="tg160">
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="col form-group">
                          <label for="min" class="fw-extrabold">Cours dont TG = 180 : </label>
                          <input type="number" class="form-control" value="12" min="0" max="100" id="tg180">
                        </div>
                        <div class="col form-group">
                          <label for="max" class="fw-extrabold">Cours dont TG = 240 : </label>
                          <input type="number" class="form-control" value="15" min='0' max="100" id="tg240">
                        </div>
                    </div>
                    <div class='row ml-5'>
                        <div class="col-6 form-group">
                            <label for="min" class="fw-extrabold">Cours dont TG = 360 : </label>
                            <input type="number" class="form-control" value="18" min="0" max="100" id="tg360">
                        </div>
                        <div class="col-6 form-group">
                            <label for="max" class="fw-extrabold">Cours dont TG = 400 : </label>
                            <input type="number" class="form-control" value="20" min='0' max="100" id="tg400">
                        </div>
                    </div>
                `);
            }
        })

        let selectedClasse = "0";

        classesSelect.change(e => {
            selectedClasse = e.target.value
            coursSelect.empty()
            coursSelect.append(`<option>-------</option>`)

            data.cours.filter(cours => data.ponderer.some(ponderation =>
                ponderation.cours_id == cours.id && ponderation.classe_id == e.target.value
            )).forEach(cours => {
                coursSelect.append(`<option value=${cours.id}>${cours.designation}</option>`)
            })
        })

        coursSelect.change(e => {
            const coursSelected = e.target.value

            cotesTousLesEleves = data.cotes.filter(cote =>
                data.eleves_inscrits.some(inscrit => inscrit.classe_id == selectedClasse && inscrit.eleve_id == cote.eleve_id)
            ).map(cote => ({
                ...cote,
                epreuve: data.epreuves.find(epreuve => epreuve.id == cote.epreuve_id).intitule,
                ponderation: data.ponderer.find(ponderation => ponderation.cours_id == coursSelected && data.epreuves.find(epreuve => epreuve.id == cote.epreuve_id).categorie_id == ponderation.categorie_id).max,
            }));

            const totalPointsClasse = data.ponderer.filter(ponderation => ponderation.classe_id == selectedClasse).map(
                ponderation => ({
                    ...ponderation,
                    categorie: data.categories_epreuves.find(categorie => categorie.id == ponderation.categorie_id).designation,
                })
            ).reduce((acc, ponderation) => acc + (ponderation.categorie == 'Période' ? ponderation.max * 4 : ponderation.max * 2), 0);

            const ponderations = data.ponderer.filter(ponderation => ponderation.classe_id == selectedClasse && ponderation.cours_id == coursSelected).map(
                infos_ponderation => ({
                    ...infos_ponderation,
                    designation: data.categories_epreuves.find(categorie => categorie.id == infos_ponderation.categorie_id).designation,
                }));


            const elevesClasse = data.eleves_inscrits.filter(inscrit => inscrit.classe_id == selectedClasse).map(inscrit => {
                const eleve = data.tousLesEleves.find(eleve => eleve.id == inscrit.eleve_id);
                return ({
                    ...inscrit, noms: `${eleve.nom} ${eleve.postnom} ${eleve.prenom}`,
                    id: eleve.id,
                    totalPointsGen: cotesTousLesEleves.reduce((acc, cote) => acc + (cote.eleve_id == eleve.id ? cote.valeur : 0), 0),
                    totalPoints: cotesTousLesEleves.reduce((acc, cote) => acc + (cote.eleve_id == eleve.id ? (cote.cours_id == coursSelected ? cote.valeur : 0) : 0), 0),
                    pourcentage: ((cotesTousLesEleves.reduce((acc, cote) => acc + (cote.eleve_id == eleve.id ? cote.valeur : 0), 0)) / totalPointsClasse * 100).toFixed(2),
                })
            })

            if (ponderations.find(ponderation => ponderation.categorie_id == 2)?.max != null && ponderations.find(ponderation => ponderation.categorie_id == 1)?.max != null) {
                maxima = ((ponderations.find(ponderation => ponderation.categorie_id == 2)?.max) * 4 + (ponderations.find(ponderation => ponderation.categorie_id == 1)?.max) * 2)
            } else if (ponderations.find(ponderation => ponderation.categorie_id == 2)?.max == null && ponderations.find(ponderation => ponderation.categorie_id == 1)?.max != null) {
                maxima = (ponderations.find(ponderation => ponderation.categorie_id == 1)?.max) * 2
            } else if (ponderations.find(ponderation => ponderation.categorie_id == 2)?.max != null && ponderations.find(ponderation => ponderation.categorie_id == 1)?.max == null) {
                maxima = (ponderations.find(ponderation => ponderation.categorie_id == 2)?.max) * 4
            } else {
                maxima = 0
            }

            $('#data').empty()

            $('#data').append(`<div class='row'>
             <div class='col-4'>
            </div>
             <div class='col-1 text-center ms-3'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 2)?.max || 0}</span>
                    </div>
                    <div class='col-1 text-center'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 2)?.max || 0}</span>
                    </div>
                    <div class='col-1 text-end ms-3'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 1)?.max || 0}</span>
                    </div>
                    <div class='col-1 text-end ms-2'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 2)?.max || 0}</span>
                    </div>
                    <div class='col-1 text-end ms-3'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 2)?.max || 0}</span>
                    </div>
                    <div class='col-1 text-end ms-3'>
                        <span>/${ponderations.find(ponderation => ponderation.categorie_id == 1)?.max || 0}</span>
                    </div>
                    <div class='col-1 fw-bolder text-danger text-white text-end ms-3'>
                        <span>/${maxima || 0}</span>
                    </div>
            </div>`)

            $('#points').empty()
            $('#points').append(`
                <div class='row border-1 border-success'>
                    <div class='col-6 fw-extrabold text-end'>Points à ajouter pour ce cours : </div>
                    <div class='col-6 '>
                        <input type='number' value='${maxima * 0.0625}' name='points' class='col-6 form-control'>
                    </div>
                </div>
            `)

            $('#domaines').empty();
            const domaines = data.domaines;

            domaines.forEach(domaine => {
                $('#domaines').append(`
                    <option value="${domaine.id}">${domaine.designation}</option>
                `)
            });

            elevesClasse.forEach((eleve, index) => {
                $('#data').append(`
                <div class='row mb-2'>
                    <div class='col'>
                        <input type='text' data-id='${eleve.id}' value='${index + 1}' disabled class='border text-center text-dark form-control'>
                    </div>
                    <div class='col-3'>
                        <input type='text' value='${eleve.noms} (${eleve.pourcentage}%)' class='form-control fw-extrabold text-dark' readOnly>
                    </div>
                    <div class='col'>
                        <div class='input-group'>
                            <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == '1e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}' value='${cotesTousLesEleves.find(cote => cote.epreuve == '1e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                </div>
                        </div>
                        <div class='col'>
                            <div class='input-group'>
                                <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == '2e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}' value='${cotesTousLesEleves.find(cote => cote.epreuve == '2e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                    </div>
                            </div>
                                <div class='col'>
                                    <div class='input-group'>
                                        <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == 'EXAM1' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}'  value='${cotesTousLesEleves.find(cote => cote.epreuve == 'EXAM1' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                            </div>
                                    </div>
                                    <div class='col'>
                                        <div class='input-group'>
                                            <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == '3e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}'  value='${cotesTousLesEleves.find(cote => cote.epreuve == '3e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                                </div>
                                        </div>
                                        <div class='col'>
                                            <div class='input-group'>
                                                <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == '4e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}'  value='${cotesTousLesEleves.find(cote => cote.epreuve == '4e P' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                                    </div>
                                            </div>
                                            <div class='col'>
                                                <div class='input-group'>
                                                    <input type='number' data-id='${cotesTousLesEleves.find(cote => cote.epreuve == 'EXAM2' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.id || 0}'  value='${cotesTousLesEleves.find(cote => cote.epreuve == 'EXAM2' && cote.eleve_id == eleve.id && cote.cours_id == coursSelected)?.valeur || 0}' class='border text-center text-dark form-control'>
                                                        </div>
                                                </div>
                                                <div class='col border-2 bg-danger '>
                                                        <label class='text-center text-white fw-extrabold p-2'>${eleve.totalPoints || 0} pts</label>
                                                </div>
                                            </div>
                    `)
            });

            $('#buttons').empty();
            $('#buttons').append(`
                <button class='btn btn-warning'>Annuler</button>
              <button class='btn btn-primary' type='submit' id='btn-save'>Sauvegarger les modifications</button>
            `);

            $('#btn-validate-criteres').click(function (e) {
                e.preventDefault();
                const min = $('#min').val();
                const max = $('#max').val();
                const tg80 = $('#tg80').val();
                const tg160 = $('#tg160').val();
                const tg180 = $('#tg180').val();
                const tg240 = $('#tg240').val();
                const tg360 = $('#tg360').val();
                const tg400 = $('#tg400').val();
                const domaines = $('#domaines').val()

                let domaines_a_valider = []

                if (domaines != null) {
                    domaines.forEach((domaine, index) => {
                        domaines_a_valider.push(data.domaines.find(domaine => domaine.id == domaines[index]))
                    });
                }


                console.log(min, max, tg80, tg160, tg180, tg240, tg360, tg400, domaines_a_valider);
            });

            console.log(cotesTousLesEleves);

            $(document).ready(function () {
                $('#btn-save').click(function (event) {
                    //event.preventDefault();

                    const fields = $('#data input[type="number"]');
                    const ids = $('#data input[type="text"]');
                    const notesModifiees = [];

                    const coursId = coursSelected;

                    fields.each(function () {
                        // const eleveId = $(this).data('id');
                        const coteId = $(this).data('id');
                        const nouvelleNote = $(this).val();
                        notesModifiees.push({ coteId, nouvelleNote, coursId });

                    })

                    console.log(notesModifiees)

                    $.ajaxSetup({
                        headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() }
                    });

                    $.ajax({
                        url: '/cotes/edit',
                        method: 'POST',
                        data: { 'cotes': JSON.stringify(notesModifiees) },
                        success: function (response) {
                            console.log('success');
                        },
                        error: function (response) {
                            console.log('erreur survenue')
                        }
                    });
                });
            });
        });
    }
});