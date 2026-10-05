-- Seed data for the Library my_project database (Stage 1 schema).
--
-- Contains intentional normalization anomalies for Module 05 discovery:
--
--   1NF violations
--     book.authors  -- comma-separated when multiple authors
--                   -- e.g. 'J.R.R. Tolkien, Christopher Tolkien'
--     book.genres   -- comma-separated multi-value attribute
--                   -- e.g. 'Fantasy, Adventure', 'Fantasy, Comedy'
--
--   2NF violations
--     book.publisher_name, book.publisher_address, book.publisher_city
--     -- These attributes depend on the publisher, not on book_id.
--     -- The same publisher data repeats identically across every book
--     -- from that publisher (George Allen & Unwin appears 6 times,
--     -- Bloomsbury 7 times, Bantam Books 5 times, etc.).
--
--   3NF violations
--     member.country is transitively determined by member.city, not
--     by member_id. Every member in 'Athens' has 'Greece'; every
--     member in 'London' has 'United Kingdom'. The dependency
--     member_id -> city -> country is visible across multiple rows.
--
-- Insert order satisfies FK constraints:
--   book and member first, then loan and member_card.

-- ────────────────────────────────────────────────────────────────────────────
-- book  (35 rows)
-- ────────────────────────────────────────────────────────────────────────────
-- 2NF anomaly: publisher columns repeat for each publisher group.
-- 1NF anomaly: authors and genres are comma-separated multi-value strings.

INSERT INTO book (book_id, title, authors, genres, publisher_name, publisher_address, publisher_city) VALUES
-- George Allen & Unwin (6 books) ----------------------------------------
(1,  'The Hobbit',
     'J.R.R. Tolkien',
     'Fantasy',
     'George Allen & Unwin', '40 Museum Street', 'London'),
(2,  'The Fellowship of the Ring',
     'J.R.R. Tolkien',
     'Fantasy, Adventure',
     'George Allen & Unwin', '40 Museum Street', 'London'),
(3,  'The Two Towers',
     'J.R.R. Tolkien',
     'Fantasy, Adventure',
     'George Allen & Unwin', '40 Museum Street', 'London'),
(4,  'The Return of the King',
     'J.R.R. Tolkien',
     'Fantasy, Adventure',
     'George Allen & Unwin', '40 Museum Street', 'London'),
(5,  'The Silmarillion',
     'J.R.R. Tolkien, Christopher Tolkien',
     'Fantasy, Mythology',
     'George Allen & Unwin', '40 Museum Street', 'London'),
(6,  'Unfinished Tales',
     'J.R.R. Tolkien, Christopher Tolkien',
     'Fantasy, Mythology',
     'George Allen & Unwin', '40 Museum Street', 'London'),
-- Bloomsbury Publishing (7 books) ----------------------------------------
(7,  'Harry Potter and the Philosopher''s Stone',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(8,  'Harry Potter and the Chamber of Secrets',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(9,  'Harry Potter and the Prisoner of Azkaban',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(10, 'Harry Potter and the Goblet of Fire',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(11, 'Harry Potter and the Order of the Phoenix',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(12, 'Harry Potter and the Half-Blood Prince',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
(13, 'Harry Potter and the Deathly Hallows',
     'J.K. Rowling',
     'Fantasy',
     'Bloomsbury Publishing', '50 Bedford Square', 'London'),
-- Bantam Books (5 books) --------------------------------------------------
(14, 'A Game of Thrones',
     'George R. R. Martin',
     'Fantasy, Drama',
     'Bantam Books', '1745 Broadway', 'New York'),
(15, 'A Clash of Kings',
     'George R. R. Martin',
     'Fantasy, Drama',
     'Bantam Books', '1745 Broadway', 'New York'),
(16, 'A Storm of Swords',
     'George R. R. Martin',
     'Fantasy, Drama',
     'Bantam Books', '1745 Broadway', 'New York'),
(17, 'A Feast for Crows',
     'George R. R. Martin',
     'Fantasy, Drama',
     'Bantam Books', '1745 Broadway', 'New York'),
(18, 'A Dance with Dragons',
     'George R. R. Martin',
     'Fantasy, Drama',
     'Bantam Books', '1745 Broadway', 'New York'),
-- Tor Books (7 books) -----------------------------------------------------
(19, 'Mistborn: The Final Empire',
     'Brandon Sanderson',
     'Fantasy',
     'Tor Books', '120 Broadway', 'New York'),
(20, 'The Well of Ascension',
     'Brandon Sanderson',
     'Fantasy',
     'Tor Books', '120 Broadway', 'New York'),
(21, 'The Hero of Ages',
     'Brandon Sanderson',
     'Fantasy',
     'Tor Books', '120 Broadway', 'New York'),
(22, 'The Way of Kings',
     'Brandon Sanderson',
     'Fantasy, Epic',
     'Tor Books', '120 Broadway', 'New York'),
(23, 'Words of Radiance',
     'Brandon Sanderson',
     'Fantasy, Epic',
     'Tor Books', '120 Broadway', 'New York'),
(24, 'Elantris',
     'Brandon Sanderson',
     'Fantasy',
     'Tor Books', '120 Broadway', 'New York'),
(25, 'The Eye of the World',
     'Robert Jordan',
     'Fantasy, Epic',
     'Tor Books', '120 Broadway', 'New York'),
-- Victor Gollancz (8 books) -----------------------------------------------
(26, 'Good Omens',
     'Terry Pratchett, Neil Gaiman',
     'Fantasy, Comedy',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(27, 'Guards! Guards!',
     'Terry Pratchett',
     'Fantasy, Comedy',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(28, 'Small Gods',
     'Terry Pratchett',
     'Fantasy, Satire',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(29, 'Mort',
     'Terry Pratchett',
     'Fantasy, Comedy',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(30, 'American Gods',
     'Neil Gaiman',
     'Fantasy, Mystery',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(31, 'Neverwhere',
     'Neil Gaiman',
     'Fantasy',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(32, 'Stardust',
     'Neil Gaiman',
     'Fantasy, Romance',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
(33, 'Coraline',
     'Neil Gaiman',
     'Fantasy, Horror',
     'Victor Gollancz', '14 Henrietta Street', 'London'),
-- DAW Books (2 books) -----------------------------------------------------
(34, 'The Name of the Wind',
     'Patrick Rothfuss',
     'Fantasy',
     'DAW Books', '375 Hudson Street', 'New York'),
(35, 'The Wise Man''s Fear',
     'Patrick Rothfuss',
     'Fantasy',
     'DAW Books', '375 Hudson Street', 'New York');

-- ────────────────────────────────────────────────────────────────────────────
-- member  (20 rows)
-- ────────────────────────────────────────────────────────────────────────────
-- 3NF anomaly: country is determined by city, not by member_id.
-- Members sharing a city always have the same country.
-- city -> country is the transitive dependency.

INSERT INTO member (member_id, full_name, address, city, country) VALUES
-- Athens, Greece (5 members) ----------------------------------------------
(1,  'Nikos Papadopoulos',  'Odos Ermou 15',              'Athens',        'Greece'),
(2,  'Maria Georgiou',      'Leoforos Vouliagmenis 28',   'Athens',        'Greece'),
(3,  'Kostas Alexiou',      'Odos Stadiou 7',             'Athens',        'Greece'),
(4,  'Eleni Makri',         'Odos Patision 44',           'Athens',        'Greece'),
(5,  'Dimitris Stavros',    'Odos Akadimias 12',          'Athens',        'Greece'),
-- Thessaloniki, Greece (2 members) ----------------------------------------
(6,  'Vasilis Nikolaou',    'Odos Egnatia 85',            'Thessaloniki',  'Greece'),
(7,  'Sofia Papageorgiou',  'Odos Mitropoleos 33',        'Thessaloniki',  'Greece'),
-- London, United Kingdom (3 members) --------------------------------------
(8,  'James Wilson',        '42 Baker Street',            'London',        'United Kingdom'),
(9,  'Emily Thompson',      '17 Oxford Street',           'London',        'United Kingdom'),
(10, 'Robert Clark',        '8 Victoria Road',            'London',        'United Kingdom'),
-- Manchester, United Kingdom (1 member) ------------------------------------
(11, 'Sarah Hartley',       '21 Deansgate',               'Manchester',    'United Kingdom'),
-- Paris, France (3 members) -----------------------------------------------
(12, 'Pierre Dupont',       '14 Rue de Rivoli',           'Paris',         'France'),
(13, 'Isabelle Martin',     '7 Boulevard Haussmann',      'Paris',         'France'),
(14, 'Francois Lefevre',    '22 Rue du Faubourg',         'Paris',         'France'),
-- Berlin, Germany (2 members) ---------------------------------------------
(15, 'Hans Mueller',        '15 Unter den Linden',        'Berlin',        'Germany'),
(16, 'Katrin Becker',       '33 Kurfuerstendamm',         'Berlin',        'Germany'),
-- New York, United States (4 members) -------------------------------------
(17, 'Michael Johnson',     '350 Fifth Avenue',           'New York',      'United States'),
(18, 'Jennifer Davis',      '200 Park Avenue',            'New York',      'United States'),
(19, 'Christopher Lee',     '100 West 42nd Street',       'New York',      'United States'),
(20, 'Amanda White',        '75 Rockefeller Plaza',       'New York',      'United States');

-- ────────────────────────────────────────────────────────────────────────────
-- loan  (50 rows: 25 returned, 5 overdue, 20 active)
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO loan (loan_id, book_id, member_id, loan_date, return_date) VALUES
-- Returned loans (loan_id 1-25, return_date not null) ---------------------
(1,  1,  1,  '2024-10-01', '2024-10-15'),
(2,  7,  2,  '2024-10-03', '2024-10-20'),
(3,  14, 3,  '2024-10-05', '2024-10-25'),
(4,  19, 4,  '2024-10-07', '2024-11-01'),
(5,  26, 5,  '2024-10-10', '2024-11-05'),
(6,  2,  6,  '2024-10-12', '2024-11-08'),
(7,  8,  7,  '2024-10-15', '2024-11-10'),
(8,  15, 8,  '2024-10-18', '2024-11-15'),
(9,  20, 9,  '2024-10-20', '2024-11-20'),
(10, 27, 10, '2024-10-22', '2024-11-25'),
(11, 3,  11, '2024-10-25', '2024-11-28'),
(12, 9,  12, '2024-10-28', '2024-12-02'),
(13, 16, 13, '2024-11-01', '2024-12-05'),
(14, 21, 14, '2024-11-03', '2024-12-08'),
(15, 28, 15, '2024-11-05', '2024-12-10'),
(16, 4,  16, '2024-11-08', '2024-12-15'),
(17, 10, 17, '2024-11-10', '2024-12-18'),
(18, 17, 18, '2024-11-12', '2024-12-20'),
(19, 22, 19, '2024-11-15', '2024-12-22'),
(20, 30, 20, '2024-11-18', '2024-12-28'),
(21, 5,  1,  '2024-11-20', '2025-01-05'),
(22, 11, 3,  '2024-11-22', '2025-01-08'),
(23, 18, 5,  '2024-11-25', '2025-01-12'),
(24, 23, 7,  '2024-12-01', '2025-01-15'),
(25, 31, 9,  '2024-12-05', '2025-01-20'),
-- Overdue loans (loan_id 26-30, old loan_date, return_date null) -----------
(26, 32, 11, '2024-02-10', NULL),
(27, 33, 12, '2024-03-15', NULL),
(28, 34, 13, '2024-04-22', NULL),
(29, 35, 14, '2024-05-08', NULL),
(30, 29, 15, '2024-06-30', NULL),
-- Active loans (loan_id 31-50, recent loan_date, return_date null) ---------
(31, 12, 2,  '2025-01-10', NULL),
(32, 13, 4,  '2025-01-12', NULL),
(33, 6,  6,  '2025-01-15', NULL),
(34, 24, 8,  '2025-01-18', NULL),
(35, 25, 10, '2025-01-20', NULL),
(36, 1,  16, '2025-01-22', NULL),
(37, 7,  17, '2025-01-25', NULL),
(38, 14, 18, '2025-01-28', NULL),
(39, 19, 19, '2025-02-01', NULL),
(40, 26, 20, '2025-02-03', NULL),
(41, 2,  1,  '2025-02-05', NULL),
(42, 8,  3,  '2025-02-08', NULL),
(43, 15, 5,  '2025-02-10', NULL),
(44, 20, 7,  '2025-02-12', NULL),
(45, 27, 9,  '2025-02-15', NULL),
(46, 3,  2,  '2025-02-18', NULL),
(47, 9,  4,  '2025-02-20', NULL),
(48, 16, 6,  '2025-02-22', NULL),
(49, 21, 8,  '2025-02-25', NULL),
(50, 28, 10, '2025-03-01', NULL);

-- ────────────────────────────────────────────────────────────────────────────
-- member_card  (20 rows, one card per member — 1:1 relationship)
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO member_card (card_id, issue_date, expiry_date, member_id_member) VALUES
(1,  '2023-02-15', '2025-02-15', 1),
(2,  '2023-03-20', '2025-03-20', 2),
(3,  '2023-04-10', '2025-04-10', 3),
(4,  '2023-05-05', '2025-05-05', 4),
(5,  '2023-06-12', '2025-06-12', 5),
(6,  '2023-07-18', '2025-07-18', 6),
(7,  '2023-08-22', '2025-08-22', 7),
(8,  '2023-09-08', '2025-09-08', 8),
(9,  '2023-10-14', '2025-10-14', 9),
(10, '2023-11-30', '2025-11-30', 10),
(11, '2024-01-07', '2026-01-07', 11),
(12, '2024-02-14', '2026-02-14', 12),
(13, '2024-03-21', '2026-03-21', 13),
(14, '2024-04-05', '2026-04-05', 14),
(15, '2024-05-19', '2026-05-19', 15),
(16, '2024-06-03', '2026-06-03', 16),
(17, '2024-07-27', '2026-07-27', 17),
(18, '2024-08-11', '2026-08-11', 18),
(19, '2024-09-16', '2026-09-16', 19),
(20, '2024-10-01', '2026-10-01', 20);
