-- Full Stage 6 seed for the Library my_project database (all 7 tables).
--
-- This is the rich dataset for the final stage: about 2x-3x the core
-- data of seed_data.sql, used after notebook 13 to experiment with
-- transactions and in the final review notebook. It requires the full
-- Stage 6 schema (book, member, loan, member_card, reservation,
-- librarian, book_copy) to already exist.
--
-- The intentional normalization anomalies for Module 05 are preserved:
--   1NF: book.authors and book.genres are comma-separated strings.
--   2NF: book.publisher_name/address/city repeat per publisher.
--   3NF: member.country is determined by member.city, not member_id.
--
-- Consistency guarantees baked into this seed:
--   * Every foreign key references an id that exists here.
--   * book.is_available is false exactly for books with an active
--     (not returned) loan, true otherwise.
--   * Emails match the email_address domain (something@something.something).
--   * Phones match the phone_number domain (digits, spaces, + - ( ) only).
--
-- Insert order satisfies FK constraints: book, member, librarian first;
-- then book_copy, member_card, reservation, and loan.

-- ----------------------------------------------------------------------------
-- book  (75 rows)
-- ----------------------------------------------------------------------------
-- is_available is false exactly for books with an active loan below.

INSERT INTO book (book_id, title, authors, genres, publisher_name, publisher_address, publisher_city, is_available) VALUES
(1, 'The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(2, 'The Fellowship of the Ring', 'J.R.R. Tolkien', 'Fantasy, Adventure', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(3, 'The Two Towers', 'J.R.R. Tolkien', 'Fantasy, Adventure', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(4, 'The Return of the King', 'J.R.R. Tolkien', 'Fantasy, Adventure', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(5, 'The Silmarillion', 'J.R.R. Tolkien, Christopher Tolkien', 'Fantasy, Mythology', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(6, 'Unfinished Tales', 'J.R.R. Tolkien, Christopher Tolkien', 'Fantasy, Mythology', 'George Allen & Unwin', '40 Museum Street', 'London', true),
(7, 'Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', false),
(8, 'Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', false),
(9, 'Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', false),
(10, 'Harry Potter and the Goblet of Fire', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', true),
(11, 'Harry Potter and the Order of the Phoenix', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', false),
(12, 'Harry Potter and the Half-Blood Prince', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', true),
(13, 'Harry Potter and the Deathly Hallows', 'J.K. Rowling', 'Fantasy', 'Bloomsbury Publishing', '50 Bedford Square', 'London', true),
(14, 'A Game of Thrones', 'George R. R. Martin', 'Fantasy, Drama', 'Bantam Books', '1745 Broadway', 'New York', false),
(15, 'A Clash of Kings', 'George R. R. Martin', 'Fantasy, Drama', 'Bantam Books', '1745 Broadway', 'New York', false),
(16, 'A Storm of Swords', 'George R. R. Martin', 'Fantasy, Drama', 'Bantam Books', '1745 Broadway', 'New York', false),
(17, 'A Feast for Crows', 'George R. R. Martin', 'Fantasy, Drama', 'Bantam Books', '1745 Broadway', 'New York', true),
(18, 'A Dance with Dragons', 'George R. R. Martin', 'Fantasy, Drama', 'Bantam Books', '1745 Broadway', 'New York', true),
(19, 'Mistborn: The Final Empire', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(20, 'The Well of Ascension', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(21, 'The Hero of Ages', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', true),
(22, 'The Way of Kings', 'Brandon Sanderson', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(23, 'Words of Radiance', 'Brandon Sanderson', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(24, 'Elantris', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', true),
(25, 'The Eye of the World', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(26, 'Good Omens', 'Terry Pratchett, Neil Gaiman', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', false),
(27, 'Guards! Guards!', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', false),
(28, 'Small Gods', 'Terry Pratchett', 'Fantasy, Satire', 'Gollancz', 'Carmelite House', 'London', true),
(29, 'Mort', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', true),
(30, 'American Gods', 'Neil Gaiman', 'Fantasy, Mystery', 'Gollancz', 'Carmelite House', 'London', false),
(31, 'Neverwhere', 'Neil Gaiman', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', true),
(32, 'Stardust', 'Neil Gaiman', 'Fantasy, Romance', 'Gollancz', 'Carmelite House', 'London', false),
(33, 'Coraline', 'Neil Gaiman', 'Fantasy, Horror', 'Gollancz', 'Carmelite House', 'London', true),
(34, 'The Name of the Wind', 'Patrick Rothfuss', 'Fantasy', 'DAW Books', '375 Hudson Street', 'New York', false),
(35, 'The Wise Man''s Fear', 'Patrick Rothfuss', 'Fantasy', 'DAW Books', '375 Hudson Street', 'New York', true),
(36, 'The Great Hunt', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(37, 'The Dragon Reborn', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(38, 'The Shadow Rising', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(39, 'The Fires of Heaven', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', true),
(40, 'Lord of Chaos', 'Robert Jordan', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(41, 'Oathbringer', 'Brandon Sanderson', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(42, 'Rhythm of War', 'Brandon Sanderson', 'Fantasy, Epic', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(43, 'A Wizard of Earthsea', 'Ursula K. Le Guin', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', true),
(44, 'The Tombs of Atuan', 'Ursula K. Le Guin', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', false),
(45, 'The Farthest Shore', 'Ursula K. Le Guin', 'Fantasy, Adventure', 'Gollancz', 'Carmelite House', 'London', false),
(46, 'The Lion, the Witch and the Wardrobe', 'C.S. Lewis', 'Fantasy, Adventure', 'Harper Voyager', '195 Broadway', 'New York', false),
(47, 'Prince Caspian', 'C.S. Lewis', 'Fantasy, Adventure', 'Harper Voyager', '195 Broadway', 'New York', true),
(48, 'The Voyage of the Dawn Treader', 'C.S. Lewis', 'Fantasy, Adventure', 'Harper Voyager', '195 Broadway', 'New York', false),
(49, 'The Silver Chair', 'C.S. Lewis', 'Fantasy, Adventure', 'Harper Voyager', '195 Broadway', 'New York', true),
(50, 'Northern Lights', 'Philip Pullman', 'Fantasy, Adventure', 'Bantam Books', '1745 Broadway', 'New York', false),
(51, 'The Subtle Knife', 'Philip Pullman', 'Fantasy, Adventure', 'Bantam Books', '1745 Broadway', 'New York', true),
(52, 'The Amber Spyglass', 'Philip Pullman', 'Fantasy, Adventure', 'Bantam Books', '1745 Broadway', 'New York', false),
(53, 'The Slow Regard of Silent Things', 'Patrick Rothfuss', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', true),
(54, 'The Last Wish', 'Andrzej Sapkowski', 'Fantasy, Adventure', 'Orbit', 'Carmelite House', 'London', false),
(55, 'Blood of Elves', 'Andrzej Sapkowski', 'Fantasy, Adventure', 'Orbit', 'Carmelite House', 'London', true),
(56, 'The Time of Contempt', 'Andrzej Sapkowski', 'Fantasy, Adventure', 'Orbit', 'Carmelite House', 'London', false),
(57, 'Baptism of Fire', 'Andrzej Sapkowski', 'Fantasy, Adventure', 'Orbit', 'Carmelite House', 'London', true),
(58, 'The Blade Itself', 'Joe Abercrombie', 'Fantasy, Drama', 'Gollancz', 'Carmelite House', 'London', false),
(59, 'Before They Are Hanged', 'Joe Abercrombie', 'Fantasy, Drama', 'Gollancz', 'Carmelite House', 'London', false),
(60, 'Last Argument of Kings', 'Joe Abercrombie', 'Fantasy, Drama', 'Gollancz', 'Carmelite House', 'London', true),
(61, 'The Colour of Magic', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', false),
(62, 'Reaper Man', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', true),
(63, 'Night Watch', 'Terry Pratchett', 'Fantasy, Satire', 'Gollancz', 'Carmelite House', 'London', false),
(64, 'Going Postal', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', true),
(65, 'Hogfather', 'Terry Pratchett', 'Fantasy, Comedy', 'Gollancz', 'Carmelite House', 'London', true),
(66, 'Prince of Thorns', 'Mark Lawrence', 'Fantasy, Drama', 'Harper Voyager', '195 Broadway', 'New York', false),
(67, 'King of Thorns', 'Mark Lawrence', 'Fantasy, Drama', 'Harper Voyager', '195 Broadway', 'New York', true),
(68, 'Emperor of Thorns', 'Mark Lawrence', 'Fantasy, Drama', 'Harper Voyager', '195 Broadway', 'New York', true),
(69, 'The Alloy of Law', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(70, 'Shadows of Self', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', false),
(71, 'The Bands of Mourning', 'Brandon Sanderson', 'Fantasy', 'Tor Books', '175 Fifth Avenue', 'New York', true),
(72, 'The Children of Hurin', 'J.R.R. Tolkien, Christopher Tolkien', 'Fantasy, Mythology', 'George Allen & Unwin', '40 Museum Street', 'London', false),
(73, 'Tehanu', 'Ursula K. Le Guin', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', true),
(74, 'The Ocean at the End of the Lane', 'Neil Gaiman', 'Fantasy', 'Gollancz', 'Carmelite House', 'London', true),
(75, 'Nation', 'Terry Pratchett', 'Fantasy, Adventure', 'Gollancz', 'Carmelite House', 'London', true);

-- ----------------------------------------------------------------------------
-- member  (48 rows)
-- ----------------------------------------------------------------------------
-- 3NF anomaly: members sharing a city always share the same country.
-- About two thirds carry email and phone; the rest are NULL.

INSERT INTO member (member_id, full_name, address, city, country, penalty_days, phone, email) VALUES
(1, 'Nikos Papadopoulos', 'Odos Ermou 15', 'Athens', 'Greece', 0, '+30 210 555 0001', 'nikos.papadopoulos@example.com'),
(2, 'Maria Georgiou', 'Leoforos Vouliagmenis 28', 'Athens', 'Greece', 0, '+30 210 555 0002', 'maria.georgiou@example.com'),
(3, 'Kostas Alexiou', 'Odos Stadiou 7', 'Athens', 'Greece', 0, NULL, NULL),
(4, 'Eleni Makri', 'Odos Patision 44', 'Athens', 'Greece', 2, '+30 210 555 0004', 'eleni.makri@example.com'),
(5, 'Dimitris Stavros', 'Odos Akadimias 12', 'Athens', 'Greece', 0, '+30 210 555 0005', 'dimitris.stavros@example.com'),
(6, 'Vasilis Nikolaou', 'Odos Egnatia 85', 'Thessaloniki', 'Greece', 0, NULL, NULL),
(7, 'Sofia Papageorgiou', 'Odos Mitropoleos 33', 'Thessaloniki', 'Greece', 0, '+30 210 555 0007', 'sofia.papageorgiou@example.com'),
(8, 'James Wilson', '42 Baker Street', 'London', 'United Kingdom', 0, '+44 20 7946 0008', 'james.wilson@example.com'),
(9, 'Emily Thompson', '17 Oxford Street', 'London', 'United Kingdom', 0, NULL, NULL),
(10, 'Robert Clark', '8 Victoria Road', 'London', 'United Kingdom', 0, '+44 20 7946 0010', 'robert.clark@example.com'),
(11, 'Sarah Hartley', '21 Deansgate', 'Manchester', 'United Kingdom', 5, '+44 20 7946 0011', 'sarah.hartley@example.com'),
(12, 'Pierre Dupont', '14 Rue de Rivoli', 'Paris', 'France', 0, NULL, NULL),
(13, 'Isabelle Martin', '7 Boulevard Haussmann', 'Paris', 'France', 0, '+33 1 42 68 0013', 'isabelle.martin@example.com'),
(14, 'Francois Lefevre', '22 Rue du Faubourg', 'Paris', 'France', 0, '+33 1 42 68 0014', 'francois.lefevre@example.com'),
(15, 'Hans Mueller', '15 Unter den Linden', 'Berlin', 'Germany', 0, NULL, NULL),
(16, 'Katrin Becker', '33 Kurfuerstendamm', 'Berlin', 'Germany', 0, '+49 30 1234 0016', 'katrin.becker@example.com'),
(17, 'Michael Johnson', '350 Fifth Avenue', 'New York', 'United States', 1, '(212) 555-0017', 'michael.johnson@example.com'),
(18, 'Jennifer Davis', '200 Park Avenue', 'New York', 'United States', 0, NULL, NULL),
(19, 'Christopher Lee', '100 West 42nd Street', 'New York', 'United States', 0, '(212) 555-0019', 'christopher.lee@example.com'),
(20, 'Amanda White', '75 Rockefeller Plaza', 'New York', 'United States', 0, '(212) 555-0020', 'amanda.white@example.com'),
(21, 'Georgios Antoniou', 'Odos Aiolou 9', 'Athens', 'Greece', 0, NULL, NULL),
(22, 'Elena Dimitriou', 'Odos Solonos 21', 'Athens', 'Greece', 0, '+30 210 555 0022', 'elena.dimitriou@example.com'),
(23, 'Christos Vlachos', 'Odos Tsimiski 54', 'Thessaloniki', 'Greece', 0, '+30 210 555 0023', 'christos.vlachos@example.com'),
(24, 'Anna Pappa', 'Odos Korinthou 18', 'Patras', 'Greece', 0, NULL, NULL),
(25, 'Stefanos Roussos', 'Odos Maizonos 40', 'Patras', 'Greece', 0, '+30 210 555 0025', 'stefanos.roussos@example.com'),
(26, 'Oliver Smith', '11 Regent Street', 'London', 'United Kingdom', 0, '+44 20 7946 0026', 'oliver.smith@example.com'),
(27, 'Charlotte Brown', '5 King''s Road', 'London', 'United Kingdom', 0, NULL, NULL),
(28, 'Harry Evans', '30 Market Street', 'Manchester', 'United Kingdom', 0, '+44 20 7946 0028', 'harry.evans@example.com'),
(29, 'Grace Taylor', '9 Portland Street', 'Manchester', 'United Kingdom', 0, '+44 20 7946 0029', 'grace.taylor@example.com'),
(30, 'Camille Bernard', '3 Rue Saint-Honore', 'Paris', 'France', 0, NULL, NULL),
(31, 'Lucas Moreau', '18 Avenue Montaigne', 'Paris', 'France', 0, '+33 1 42 68 0031', 'lucas.moreau@example.com'),
(32, 'Juliette Faure', '2 Place Bellecour', 'Lyon', 'France', 0, '+33 1 42 68 0032', 'juliette.faure@example.com'),
(33, 'Hugo Garnier', '27 Rue de la Republique', 'Lyon', 'France', 3, NULL, NULL),
(34, 'Lukas Schmidt', '44 Friedrichstrasse', 'Berlin', 'Germany', 0, '+49 30 1234 0034', 'lukas.schmidt@example.com'),
(35, 'Anna Wagner', '12 Alexanderplatz', 'Berlin', 'Germany', 0, '+49 30 1234 0035', 'anna.wagner@example.com'),
(36, 'Felix Braun', '8 Marienplatz', 'Munich', 'Germany', 0, NULL, NULL),
(37, 'Marie Hoffmann', '19 Leopoldstrasse', 'Munich', 'Germany', 0, '+49 30 1234 0037', 'marie.hoffmann@example.com'),
(38, 'David Miller', '60 Wall Street', 'New York', 'United States', 0, '(212) 555-0038', 'david.miller@example.com'),
(39, 'Laura Wilson', '120 Broadway', 'New York', 'United States', 0, NULL, NULL),
(40, 'Daniel Moore', '15 Beacon Street', 'Boston', 'United States', 0, '(212) 555-0040', 'daniel.moore@example.com'),
(41, 'Emma Taylor', '40 Newbury Street', 'Boston', 'United States', 0, '(212) 555-0041', 'emma.taylor@example.com'),
(42, 'Ioanna Nikolaidou', 'Odos Agias Sofias 7', 'Thessaloniki', 'Greece', 0, NULL, NULL),
(43, 'Dimitra Pappa', 'Odos Riga Fereou 22', 'Patras', 'Greece', 0, '+30 210 555 0043', 'dimitra.pappa@example.com'),
(44, 'Sophie Wright', '14 Oxford Road', 'Manchester', 'United Kingdom', 0, '+44 20 7946 0044', 'sophie.wright@example.com'),
(45, 'Antoine Petit', '6 Cours Lafayette', 'Lyon', 'France', 0, NULL, NULL),
(46, 'Klara Fischer', '23 Sendlinger Strasse', 'Munich', 'Germany', 0, '+49 30 1234 0046', 'klara.fischer@example.com'),
(47, 'James Anderson', '88 Boylston Street', 'Boston', 'United States', 0, '(212) 555-0047', 'james.anderson@example.com'),
(48, 'Eleni Christou', 'Odos Kifisias 100', 'Athens', 'Greece', 0, NULL, NULL);

-- ----------------------------------------------------------------------------
-- librarian  (5 rows, 2 managers)
-- ----------------------------------------------------------------------------

INSERT INTO librarian (librarian_id, full_name, hire_date, is_manager) VALUES
(1, 'Anna Vandelay', '2018-05-14', true),
(2, 'Petros Galanis', '2020-09-01', false),
(3, 'Lena Hoffmann', '2021-03-22', false),
(4, 'Mark Davies', '2017-11-08', true),
(5, 'Sofia Russo', '2023-06-30', false);

-- ----------------------------------------------------------------------------
-- book_copy  (18 rows, multiple copies of popular books)
-- ----------------------------------------------------------------------------
-- book_id_book is the FK column the relationship tool generates.

INSERT INTO book_copy (copy_id, acquisition_date, condition, book_id_book) VALUES
(1, '2019-01-15', 'new', 1),
(2, '2019-05-15', 'good', 1),
(3, '2019-09-12', 'worn', 1),
(4, '2020-01-10', 'damaged', 7),
(5, '2020-05-09', 'new', 7),
(6, '2020-09-06', 'good', 7),
(7, '2021-01-04', 'worn', 14),
(8, '2021-05-04', 'damaged', 14),
(9, '2021-09-01', 'new', 19),
(10, '2021-12-30', 'good', 19),
(11, '2022-04-29', 'worn', 22),
(12, '2022-08-27', 'damaged', 22),
(13, '2022-12-25', 'new', 34),
(14, '2023-04-24', 'good', 34),
(15, '2023-08-22', 'worn', 25),
(16, '2023-12-20', 'damaged', 2),
(17, '2024-04-18', 'new', 7),
(18, '2024-08-16', 'good', 1);

-- ----------------------------------------------------------------------------
-- member_card  (42 rows, one card per member - 1:1 relationship)
-- ----------------------------------------------------------------------------
-- member_id_member is the FK column the relationship tool generates.

INSERT INTO member_card (card_id, issue_date, expiry_date, member_id_member) VALUES
(1, '2023-01-10', '2025-01-10', 1),
(2, '2023-01-28', '2025-01-28', 2),
(3, '2023-02-15', '2025-02-15', 3),
(4, '2023-03-05', '2025-03-05', 4),
(5, '2023-03-23', '2025-03-23', 5),
(6, '2023-04-10', '2025-04-10', 6),
(7, '2023-04-28', '2025-04-28', 7),
(8, '2023-05-16', '2025-05-16', 8),
(9, '2023-06-03', '2025-06-03', 9),
(10, '2023-06-21', '2025-06-21', 10),
(11, '2023-07-09', '2025-07-09', 11),
(12, '2023-07-27', '2025-07-27', 12),
(13, '2023-08-14', '2025-08-14', 13),
(14, '2023-09-01', '2025-09-01', 14),
(15, '2023-09-19', '2025-09-19', 15),
(16, '2023-10-07', '2025-10-07', 16),
(17, '2023-10-25', '2025-10-25', 17),
(18, '2023-11-12', '2025-11-12', 18),
(19, '2023-11-30', '2025-11-30', 19),
(20, '2023-12-18', '2025-12-18', 20),
(21, '2024-01-05', '2026-01-05', 21),
(22, '2024-01-23', '2026-01-23', 22),
(23, '2024-02-10', '2026-02-10', 23),
(24, '2024-02-28', '2026-02-28', 24),
(25, '2024-03-17', '2026-03-17', 25),
(26, '2024-04-04', '2026-04-04', 26),
(27, '2024-04-22', '2026-04-22', 27),
(28, '2024-05-10', '2026-05-10', 28),
(29, '2024-05-28', '2026-05-28', 29),
(30, '2024-06-15', '2026-06-15', 30),
(31, '2024-07-03', '2026-07-03', 31),
(32, '2024-07-21', '2026-07-21', 32),
(33, '2024-08-08', '2026-08-08', 33),
(34, '2024-08-26', '2026-08-26', 34),
(35, '2024-09-13', '2026-09-13', 35),
(36, '2024-10-01', '2026-10-01', 36),
(37, '2024-10-19', '2026-10-19', 37),
(38, '2024-11-06', '2026-11-06', 38),
(39, '2024-11-24', '2026-11-24', 39),
(40, '2024-12-12', '2026-12-12', 40),
(41, '2024-12-30', '2026-12-30', 41),
(42, '2025-01-17', '2027-01-17', 42);

-- ----------------------------------------------------------------------------
-- reservation  (10 rows, mix of fulfilled and pending)
-- ----------------------------------------------------------------------------

INSERT INTO reservation (reservation_id, book_id, member_id, reservation_date, is_fulfilled) VALUES
(1, 5, 3, '2026-05-20', false),
(2, 19, 8, '2026-05-22', false),
(3, 41, 12, '2026-05-25', true),
(4, 7, 17, '2026-05-28', false),
(5, 34, 21, '2026-06-01', false),
(6, 22, 26, '2026-06-02', true),
(7, 54, 30, '2026-06-03', false),
(8, 14, 35, '2026-06-04', true),
(9, 63, 40, '2026-06-05', false),
(10, 2, 44, '2026-06-06', false);

-- ----------------------------------------------------------------------------
-- loan  (110 rows: 66 returned, 44 active including 7 overdue)
-- ----------------------------------------------------------------------------
-- librarian_id_librarian is the FK column the relationship tool
-- generates; it is NULL for older loans (before staff tracking).

INSERT INTO loan (loan_id, book_id, member_id, loan_date, return_date, is_returned, librarian_id_librarian) VALUES
(1, 1, 1, '2024-09-01', '2024-09-19', true, NULL),
(2, 2, 2, '2024-09-07', '2024-09-25', true, NULL),
(3, 3, 3, '2024-09-13', '2024-10-01', true, NULL),
(4, 4, 4, '2024-09-19', '2024-10-07', true, NULL),
(5, 5, 5, '2024-09-25', '2024-10-13', true, NULL),
(6, 6, 6, '2024-10-01', '2024-10-19', true, NULL),
(7, 7, 7, '2024-10-07', '2024-10-25', true, NULL),
(8, 8, 8, '2024-10-13', '2024-10-31', true, NULL),
(9, 9, 9, '2024-10-19', '2024-11-06', true, NULL),
(10, 10, 10, '2024-10-25', '2024-11-12', true, NULL),
(11, 11, 11, '2024-10-31', '2024-11-18', true, NULL),
(12, 12, 12, '2024-11-06', '2024-11-24', true, NULL),
(13, 13, 13, '2024-11-12', '2024-11-30', true, NULL),
(14, 14, 14, '2024-11-18', '2024-12-06', true, NULL),
(15, 15, 15, '2024-11-24', '2024-12-12', true, NULL),
(16, 16, 16, '2024-11-30', '2024-12-18', true, NULL),
(17, 17, 17, '2024-12-06', '2024-12-24', true, NULL),
(18, 18, 18, '2024-12-12', '2024-12-30', true, NULL),
(19, 19, 19, '2024-12-18', '2025-01-05', true, NULL),
(20, 20, 20, '2024-12-24', '2025-01-11', true, NULL),
(21, 21, 21, '2024-12-30', '2025-01-17', true, NULL),
(22, 22, 22, '2025-01-05', '2025-01-23', true, NULL),
(23, 23, 23, '2025-01-11', '2025-01-29', true, NULL),
(24, 24, 24, '2025-01-17', '2025-02-04', true, NULL),
(25, 25, 25, '2025-01-23', '2025-02-10', true, NULL),
(26, 26, 26, '2025-01-29', '2025-02-16', true, NULL),
(27, 27, 27, '2025-02-04', '2025-02-22', true, NULL),
(28, 28, 28, '2025-02-10', '2025-02-28', true, NULL),
(29, 29, 29, '2025-02-16', '2025-03-06', true, NULL),
(30, 30, 30, '2025-02-22', '2025-03-12', true, NULL),
(31, 31, 31, '2025-02-28', '2025-03-18', true, NULL),
(32, 32, 32, '2025-03-06', '2025-03-24', true, NULL),
(33, 33, 33, '2025-03-12', '2025-03-30', true, NULL),
(34, 34, 34, '2025-03-18', '2025-04-05', true, NULL),
(35, 35, 35, '2025-03-24', '2025-04-11', true, NULL),
(36, 36, 36, '2025-03-30', '2025-04-17', true, NULL),
(37, 37, 37, '2025-04-05', '2025-04-23', true, NULL),
(38, 38, 38, '2025-04-11', '2025-04-29', true, NULL),
(39, 39, 39, '2025-04-17', '2025-05-05', true, NULL),
(40, 40, 40, '2025-04-23', '2025-05-11', true, NULL),
(41, 41, 41, '2025-04-29', '2025-05-17', true, NULL),
(42, 42, 42, '2025-05-05', '2025-05-23', true, NULL),
(43, 43, 43, '2025-05-11', '2025-05-29', true, NULL),
(44, 44, 44, '2025-05-17', '2025-06-04', true, NULL),
(45, 45, 45, '2025-05-23', '2025-06-10', true, NULL),
(46, 46, 46, '2025-05-29', '2025-06-16', true, NULL),
(47, 47, 47, '2025-06-04', '2025-06-22', true, NULL),
(48, 48, 48, '2025-06-10', '2025-06-28', true, NULL),
(49, 49, 1, '2025-06-16', '2025-07-04', true, NULL),
(50, 50, 2, '2025-06-22', '2025-07-10', true, NULL),
(51, 51, 3, '2025-06-28', '2025-07-16', true, NULL),
(52, 52, 4, '2025-07-04', '2025-07-22', true, NULL),
(53, 53, 5, '2025-07-10', '2025-07-28', true, NULL),
(54, 54, 6, '2025-07-16', '2025-08-03', true, NULL),
(55, 55, 7, '2025-07-22', '2025-08-09', true, NULL),
(56, 56, 8, '2025-07-28', '2025-08-15', true, NULL),
(57, 57, 9, '2025-08-03', '2025-08-21', true, NULL),
(58, 58, 10, '2025-08-09', '2025-08-27', true, NULL),
(59, 59, 11, '2025-08-15', '2025-09-02', true, NULL),
(60, 60, 12, '2025-08-21', '2025-09-08', true, NULL),
(61, 61, 13, '2025-08-27', '2025-09-14', true, NULL),
(62, 62, 14, '2025-09-02', '2025-09-20', true, NULL),
(63, 63, 15, '2025-09-08', '2025-09-26', true, NULL),
(64, 64, 16, '2025-09-14', '2025-10-02', true, NULL),
(65, 65, 17, '2025-09-20', '2025-10-08', true, NULL),
(66, 66, 18, '2025-09-26', '2025-10-14', true, NULL),
(67, 32, 11, '2026-01-12', NULL, false, 1),
(68, 36, 12, '2026-02-03', NULL, false, 2),
(69, 40, 13, '2026-02-20', NULL, false, 3),
(70, 44, 24, '2026-03-09', NULL, false, 4),
(71, 50, 29, '2026-03-28', NULL, false, 5),
(72, 58, 33, '2026-04-15', NULL, false, 1),
(73, 66, 40, '2026-04-30', NULL, false, 2),
(74, 1, 1, '2026-05-27', NULL, false, 1),
(75, 2, 2, '2026-05-28', NULL, false, 2),
(76, 3, 3, '2026-05-29', NULL, false, 3),
(77, 5, 4, '2026-05-30', NULL, false, 4),
(78, 7, 5, '2026-05-31', NULL, false, 5),
(79, 9, 6, '2026-06-01', NULL, false, 1),
(80, 11, 7, '2026-06-02', NULL, false, 2),
(81, 14, 8, '2026-06-03', NULL, false, 3),
(82, 16, 9, '2026-06-04', NULL, false, 4),
(83, 19, 10, '2026-06-05', NULL, false, 5),
(84, 22, 11, '2026-06-06', NULL, false, 1),
(85, 25, 12, '2026-06-07', NULL, false, 2),
(86, 26, 13, '2026-06-08', NULL, false, 3),
(87, 30, 14, '2026-05-27', NULL, false, 4),
(88, 34, 15, '2026-05-28', NULL, false, 5),
(89, 37, 16, '2026-05-29', NULL, false, 1),
(90, 41, 17, '2026-05-30', NULL, false, 2),
(91, 45, 18, '2026-05-31', NULL, false, 3),
(92, 48, 19, '2026-06-01', NULL, false, 4),
(93, 52, 20, '2026-06-02', NULL, false, 5),
(94, 54, 21, '2026-06-03', NULL, false, 1),
(95, 56, 22, '2026-06-04', NULL, false, 2),
(96, 59, 23, '2026-06-05', NULL, false, 3),
(97, 61, 24, '2026-06-06', NULL, false, 4),
(98, 63, 25, '2026-06-07', NULL, false, 5),
(99, 69, 26, '2026-06-08', NULL, false, 1),
(100, 72, 27, '2026-05-27', NULL, false, 2),
(101, 4, 28, '2026-05-28', NULL, false, 3),
(102, 8, 29, '2026-05-29', NULL, false, 4),
(103, 15, 30, '2026-05-30', NULL, false, 5),
(104, 20, 31, '2026-05-31', NULL, false, 1),
(105, 23, 32, '2026-06-01', NULL, false, 2),
(106, 27, 33, '2026-06-02', NULL, false, 3),
(107, 38, 34, '2026-06-03', NULL, false, 4),
(108, 42, 35, '2026-06-04', NULL, false, 5),
(109, 46, 36, '2026-06-05', NULL, false, 1),
(110, 70, 37, '2026-06-06', NULL, false, 2);
