-- Drop tables if they exist
DROP TABLE IF EXISTS Accuellir cascade;
DROP TABLE IF EXISTS Enseigner cascade;
DROP TABLE IF EXISTS Equiper cascade;
DROP TABLE IF EXISTS Etudier cascade;
DROP TABLE IF EXISTS Responsable cascade;
DROP TABLE IF EXISTS Cours cascade;
DROP TABLE IF EXISTS Eleve cascade;
DROP TABLE IF EXISTS Professeur cascade;
DROP TABLE IF EXISTS Admin cascade;
DROP TABLE IF EXISTS Token cascade;
DROP TABLE IF EXISTS Action cascade;
DROP TABLE IF EXISTS Manager cascade;
DROP TABLE IF EXISTS Utilisateur cascade;
DROP TABLE IF EXISTS Ressource cascade;
DROP TABLE IF EXISTS Semestre cascade;
DROP TABLE IF EXISTS Equipement cascade;
DROP TABLE IF EXISTS Salle cascade;
DROP TABLE IF EXISTS Groupe cascade;

-- CREATE SEQUENCE code_sequence_idUtilisateur;

-- Create tables
CREATE TABLE Groupe(
   idGroupe INTEGER,
   Nom VARCHAR(50) ,
   AnneeScolaire INTEGER,
   Annee TIMESTAMP,
   idGroupe_1 INTEGER,
   PRIMARY KEY(idGroupe),
   FOREIGN KEY(idGroupe_1) REFERENCES Groupe(idGroupe)
);

CREATE TABLE Salle(
   idSalle INTEGER,
   Numero VARCHAR(50) ,
   Capacite INTEGER,
   PRIMARY KEY(idSalle),
   UNIQUE(Numero)
);

CREATE TABLE Equipement(
   idEquipement INTEGER,
   Nom VARCHAR(50) ,
   PRIMARY KEY(idEquipement)
);

CREATE TABLE Semestre(
   idSemestre INTEGER,
   Numero INTEGER,
   PRIMARY KEY(idSemestre)
);

CREATE TABLE Ressource(
   idRessource INTEGER,
   Titre VARCHAR(50) ,
   Numero VARCHAR(50) ,
   NbrHeureSemestre INTEGER,
   CodeCouleur VARCHAR(50) ,
   idSemestre INTEGER NOT NULL,
   PRIMARY KEY(idRessource),
   UNIQUE(Numero),
   FOREIGN KEY(idSemestre) REFERENCES Semestre(idSemestre)
);

CREATE TABLE Utilisateur(
   idUtilisateur VARCHAR(50) , -- nextval('code_sequence_idUtilisateur')
   FirstName VARCHAR(50) ,
   LastName VARCHAR(50) ,
   Username VARCHAR(50) ,
   PassWord VARCHAR(50) ,
   FirstLogin Boolean DEFAULT true,
   PRIMARY KEY(idUtilisateur),
   UNIQUE(Username)
);


CREATE TABLE Manager(
   idManager VARCHAR(50) ,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(idManager),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Action(
   idAction SERIAL,
   ActionName VARCHAR(50) ,
   TimeAction TIMESTAMP,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(idAction),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Token(
   idToken SERIAL,
   CodeToken VARCHAR(50) ,
   TimeCreation TIME,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(idToken),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Admin(
   IDAdmin INTEGER,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(IDAdmin),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Professeur(
   idProf INTEGER,
   Initiale VARCHAR(50) ,
   idSalle INTEGER NOT NULL,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(idProf),
   UNIQUE(Initiale),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Eleve(
   idEleve INTEGER,
   idGroupe INTEGER NOT NULL,
   idUtilisateur VARCHAR(50)  NOT NULL,
   PRIMARY KEY(idEleve),
   FOREIGN KEY(idGroupe) REFERENCES Groupe(idGroupe),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Cours(
   idCours INTEGER,
   HeureDebut TIME,
   NombreHeure INTEGER,
   Jour TIMESTAMP,
   idRessource INTEGER NOT NULL,
   PRIMARY KEY(idCours),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);

CREATE TABLE Accuellir(
   idSalle INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idSalle, idCours),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours)
);

CREATE TABLE Equiper(
   idSalle INTEGER,
   idEquipement INTEGER,
   PRIMARY KEY(idSalle, idEquipement),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idEquipement) REFERENCES Equipement(idEquipement)
);

CREATE TABLE Enseigner(
   idProf INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idProf, idCours),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours)
);

CREATE TABLE Responsable(
   idProf INTEGER,
   idRessource INTEGER,
   PRIMARY KEY(idProf, idRessource),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);

CREATE TABLE Etudier(
   idGroupe INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idGroupe, idCours),
   FOREIGN KEY(idGroupe) REFERENCES Groupe(idGroupe),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours)
);

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur values ('1','Junko', 'Enoshima', 'monokuma', 'despair', false);
INSERT INTO Utilisateur values ('2','Gilgamesh', 'Elish', 'Uruk', 'Enkidu', true);
INSERT INTO Utilisateur values ('3','Aya', 'Rindo', 'detective', 'immortal', true);
INSERT INTO Utilisateur values ('4','Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller', true);

