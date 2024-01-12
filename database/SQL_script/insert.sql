SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, firstName, lastName, username, passWord, firstLogin)
INSERT INTO Utilisateur (firstName, lastName, username, passWord) values ('Junko', 'Enoshima', 'monokuma', 'despair'); -- élève
INSERT INTO Utilisateur (firstName, lastName, username, passWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu'); -- admin
INSERT INTO Utilisateur (firstName, lastName, username, passWord) values ('Aya', 'Rindo', 'detective', 'immortal'); -- professeur
INSERT INTO Utilisateur (firstName, lastName, username, passWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller'); -- manager


-- Admin (idAdmin, idUtilisateur)
INSERT INTO Admin (idUtilisateur) values (2);

-- Semestre(idSemestre, Numero)
INSERT INTO Semestre (Numero) values (3);

-- Ressource(idRessource, titre, numero, nbrHeureSemestre, codeCouleur, idSemestre)
INSERT INTO Ressource (titre, numero, nbrHeureSemestre, idSemestre) values ('Dev', 'R3-04', '10:00:00', '1');
INSERT INTO Ressource (titre, numero, nbrHeureSemestre, idSemestre) values ('Math', 'R3-12', '08:00:00', '1');


-- Cours (idCours, heureDebut, nombreHeure, jour, idRessource)

INSERT INTO Cours (heureDebut, nombreHeure, jour, idRessource) values ('10:00:00', '04:00:00', '2023-10-06', '1');
INSERT INTO Cours (heureDebut, nombreHeure, jour, idRessource) values ('15:00:00', '02:00:00', '2024-10-06', '1');


-- Salle (idSalle, nom ,capacite);
INSERT INTO Salle (nom, capacite) values ('A2-05', 35);
INSERT INTO Salle (nom, capacite) values ('A1-01', 20);

-- Groupe(idGroupe ,nom,idGroupeParent)
INSERT INTO Groupe(nom) values ('Groupe A1');

-- Professeur(idProf, initiale, idSalle, idUtilisateur)
INSERT INTO Professeur( initiale, idSalle, idUtilisateur) values ('AR', 1, 3);
INSERT INTO Professeur( initiale, idSalle, idUtilisateur) values ('TS', 1, 4);

-- Enseigner(idProf, idCours)
INSERT INTO Enseigner(idProf, idCours) values (1,1);

-- Etudier(idgroupe, idcours)
INSERT INTO Etudier(idgroupe, idcours) values (1,1);

-- Eleve(idEleve,idGroupe,idUtilisateur)
INSERT INTO Eleve(idGroupe,idUtilisateur) values (1,1);

-- Responsable(idProf, idRessource)
INSERT INTO Responsable(idProf, idRessource) values (1,2);

-- Accuellir(idSalle, idCours)
INSERT INTO Accuellir(idSalle, idCours) values (2,1);

-- Manager(idManager, idProf)
INSERT INTO Manager(idProf) values (2);



