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
DROP SCHEMA IF EXISTS EDT;

CREATE SCHEMA EDT;
SET SEARCH_PATH TO EDT;
-- CREATE SEQUENCE code_sequence_idUtilisateur;

-- Create tables
CREATE TABLE Groupe(
   idGroupe SERIAL,
   Nom VARCHAR(50) ,
   AnneeScolaire INTEGER,
   Annee INTEGER,
   idGroupe_1 INTEGER,
   PRIMARY KEY(idGroupe),
   FOREIGN KEY(idGroupe_1) REFERENCES Groupe(idGroupe) ON DELETE CASCADE
);

CREATE TABLE Salle(
   idSalle SERIAL,
   Numero VARCHAR(50) ,
   Capacite INTEGER,
   PRIMARY KEY(idSalle),
   UNIQUE(Numero)
);

CREATE TABLE Equipement(
   idEquipement SERIAL,
   Nom VARCHAR(50) ,
   PRIMARY KEY(idEquipement)
);

CREATE TABLE Semestre(
   idSemestre SERIAL,
   Numero INTEGER,
   PRIMARY KEY(idSemestre)
);

CREATE TABLE Ressource(
   idRessource SERIAL,
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
   idUtilisateur SERIAL,
   FirstName VARCHAR(50) ,
   LastName VARCHAR(50) ,
   Username VARCHAR(50) ,
   PassWord VARCHAR(50) ,
   FirstLogin BOOLEAN DEFAULT true,
   PRIMARY KEY(idUtilisateur),
   UNIQUE(Username)
);

CREATE TABLE Action(
   idAction SERIAL,
   ActionName VARCHAR(50) ,
   TimeAction TIMESTAMP,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idAction),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Token(
   idToken SERIAL,
   CodeToken VARCHAR(50) ,
   TimeCreation TIME,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idToken),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Admin(
   IDAdmin SERIAL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(IDAdmin),
   UNIQUE(idUtilisateur),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Professeur(
   idProf SERIAL,
   Initiale VARCHAR(50) ,
   idSalle INTEGER NOT NULL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idProf),
   UNIQUE(idUtilisateur),
   UNIQUE(Initiale),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Eleve(
   idEleve SERIAL,
   idGroupe INTEGER NOT NULL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idEleve),
   UNIQUE(idUtilisateur),
   FOREIGN KEY(idGroupe) REFERENCES Groupe(idGroupe),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Cours(
   idCours SERIAL,
   HeureDebut TIME,
   NombreHeure INTEGER,
   Jour TIMESTAMP,
   idRessource INTEGER NOT NULL,
   PRIMARY KEY(idCours),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);

CREATE TABLE Manager(
   idManager SERIAL,
   idProf INTEGER NOT NULL,
   PRIMARY KEY(idManager),
   UNIQUE(idProf),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf)
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
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'despair');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'immortal');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller');

-- Salle (idSalle, Numero ,Capacite);
INSERT INTO Salle (Numero, Capacite) values ('A2-05', 35);
INSERT INTO Salle (Numero, Capacite) values ('A1-01', 20);