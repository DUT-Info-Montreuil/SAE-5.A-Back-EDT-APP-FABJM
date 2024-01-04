SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'despair'); -- élève
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'immortal'); -- professeur
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller');

-- Semestre(idSemestre, Numero)
INSERT INTO Semestre (Numero) values (3);

-- Ressource(idRessource, Titre, Numero, NbrHeureSemestre, CodeCouleur, idSemestre)
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('test ', 'R3-04', '10', '1');


-- Cours (idCours, HeureDebut, HeureFin, Jour, idRessource)

INSERT INTO Cours (HeureDebut, HeureFin, Jour, idRessource) values ('20:18:06 ', '22:18:06 ', '2023-12-06', '1');
INSERT INTO Cours (HeureDebut, HeureFin, Jour, idRessource) values ('16:49:49 ', '18:49:49 ', '2023-10-06', '1');


-- Salle (idSalle, Numero ,Capacite);
INSERT INTO Salle (Numero, Capacite) values ('A2-05', 35);
INSERT INTO Salle (Numero, Capacite) values ('A1-01', 20);

-- Groupe(idGroupe ,Nom, AnneeScolaire,Annee ,idGroupe_parent)
INSERT INTO Groupe(Nom, AnneeScolaire,Annee ) values ('Groupe A1', 2024, 2023);

-- Professeur(idProf, Initiale, idSalle, idUtilisateur)
INSERT INTO Professeur( Initiale, idSalle, idUtilisateur) values ('AR', 1, 3);

-- Enseigner(idProf, idCours)
INSERT INTO Enseigner(idProf, idCours) values (1,1);

-- Etudier(idgroupe, idcours)
INSERT INTO Etudier(idgroupe, idcours) values (1,1);

-- Eleve(idEleve,idGroupe,idUtilisateur)
INSERT INTO Eleve(idGroupe,idUtilisateur) values (1,1);

-- Responsable(idProf, idRessource)
INSERT INTO Responsable(idProf, idRessource) values (1,1);

-- Accuellir(idSalle, idCours)
INSERT INTO Accuellir(idSalle, idCours) values (2,1);
