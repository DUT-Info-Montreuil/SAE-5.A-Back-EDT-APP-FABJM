SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'b654d98118d491d60f80cc28e3ac67ef'); -- élève
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'b654d98118d491d60f80cc28e3ac67ef'); -- admin
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'b654d98118d491d60f80cc28e3ac67ef'); -- professeur
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'b654d98118d491d60f80cc28e3ac67ef');


INSERT INTO Admin (idUtilisateur) values (2);


-- Semestre(idSemestre, Numero)
INSERT INTO Semestre (Numero) values (3);

-- Ressource(idRessource, titre, numero, nbrHeureSemestre, codeCouleur, idSemestre)
INSERT INTO Ressource (titre, numero, nbrHeureSemestre, idSemestre) values ('Dev', 'R3-04', 360000, '1');
INSERT INTO Ressource (titre, numero, nbrHeureSemestre, idSemestre) values ('Math', 'R3-12', 360000, '1');



-- Cours (idCours, HeureDebut, NombreHeure, Jour, idRessource, TypeCours)

;
INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource, TypeCours)
VALUES 
('20:18:06 ', '02:00:00', '2023-12-06', '1', 'Sae'),
('16:49:49 ', '02:00:00', '2023-10-06', '1', 'Td'),
('10:00:00', '02:30:00', '2024-01-05', '1', 'Td'),
('14:30:00', '03:00:00', '2024-01-10', '1', 'Td'),
('09:15:00', '02:30:00', '2024-01-15', '1', 'Amphi'),
('13:45:00', '02:00:00', '2024-01-20', '1', 'Sae'),
('11:30:00', '03:00:00', '2024-01-25', '1', 'Tp'),
('15:00:00', '02:30:00', '2024-01-30', '1', 'Amphi');

-- Salle (idSalle, nom ,capacite);
INSERT INTO Salle (nom, capacite) values ('A2-05', 35);
INSERT INTO Salle (nom, capacite) values ('A1-01', 20);

-- Groupe(idGroupe ,nom,idGroupeParent)
INSERT INTO Groupe(nom) values ('A1');

-- Professeur(idProf, initiale, idSalle, idUtilisateur)
INSERT INTO Professeur( initiale, idSalle, idUtilisateur) values ('AR', 1, 3);
INSERT INTO Professeur( initiale, idSalle, idUtilisateur) values ('TS', 1, 4);

-- Enseigner(idProf, idCours)
INSERT INTO Enseigner(idProf, idCours) 
values 
(1,1),
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8);

-- Etudier(idgroupe, idcours)
INSERT INTO Etudier(idgroupe, idcours) values (1,1);

-- Eleve(idEleve,idGroupe,idUtilisateur)
INSERT INTO Eleve(idGroupe,idUtilisateur) values (1,1);

-- Responsable(idProf, idRessource)
INSERT INTO Responsable(idProf, idRessource) values (1,2);

-- Accuellir(idSalle, idCours)
INSERT INTO Accuellir(idSalle, idCours) values (2,1);

-- Manager(idManager, idProf, idGroupe)
INSERT INTO Manager(idProf, idGroupe) values (2,1);


