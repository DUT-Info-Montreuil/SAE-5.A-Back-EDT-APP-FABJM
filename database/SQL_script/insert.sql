SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'despair'); -- élève
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu'); -- admin
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'immortal'); -- professeur
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller'); -- manager


-- Admin (idAdmin, idUtilisateur)
INSERT INTO Admin (idUtilisateur) values (2);

-- Semestre(idSemestre, Numero)
INSERT INTO Semestre (Numero) values (3);

-- Ressource(idRessource, Titre, Numero, NbrHeureSemestre, CodeCouleur, idSemestre)
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('Dev', 'R3-04', '10:00:00', '1');
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('Math', 'R3-12', '08:00:00', '1');


-- Cours (idCours, HeureDebut, NombreHeure, Jour, idRessource)

INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('10:00:00', '04:00:00', '2023-10-06', '1');
INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('15:00:00', '02:00:00', '2024-10-06', '1');


-- Salle (idSalle, Numero ,Capacite);
INSERT INTO Salle (Nom, Capacite) values ('A2-05', 35);
INSERT INTO Salle (Nom, Capacite) values ('A1-01', 20);

-- Groupe(idGroupe ,Nom, AnneeScolaire,Annee ,idGroupe_parent)
INSERT INTO Groupe(Nom) values ('Groupe A1');

-- Professeur(idProf, Initiale, idSalle, idUtilisateur)
INSERT INTO Professeur( Initiale, idSalle, idUtilisateur) values ('AR', 1, 3);
INSERT INTO Professeur( Initiale, idSalle, idUtilisateur) values ('TS', 1, 4);

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

-- Manager(idManager, idProf)
INSERT INTO Manager(idProf) values (2);



