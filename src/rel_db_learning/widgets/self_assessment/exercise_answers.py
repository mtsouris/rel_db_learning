"""Central answer key file  for ``sql_query_check`` exercises.

This module holds the correct SQL and expected result rows for every
``sql_query_check`` exercise in the Module 04 and Module 05 notebooks, so that
students do not see the expected answer in the notebook they are working in.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


EXERCISE_ANSWERS: Dict[str, Dict[str, object]] = {
    # ----------------------------------------------------------------------
    # Module 04 - 03_select_basics.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_03_exercise_1": {
        "correct_sql": "SELECT full_name FROM member WHERE country = 'Greece'",
        "expected_rows": [
                ('Nikos Papadopoulos',),
                ('Maria Georgiou',),
                ('Kostas Alexiou',),
                ('Eleni Makri',),
                ('Dimitris Stavros',),
                ('Vasilis Nikolaou',),
                ('Sofia Papageorgiou',),
            ],
    },
    "m04_nb_03_exercise_2": {
        "correct_sql": "SELECT title FROM book WHERE title LIKE '%Ring%'",
        "expected_rows": [
                ('The Fellowship of the Ring',),
            ],
    },
    "m04_nb_03_exercise_3": {
        "correct_sql": "SELECT title FROM book WHERE publisher_city = 'London'",
        "expected_rows": [
                ('The Hobbit',),
                ('The Fellowship of the Ring',),
                ('The Two Towers',),
                ('The Return of the King',),
                ('The Silmarillion',),
                ('Unfinished Tales',),
                ("Harry Potter and the Philosopher's Stone",),
                ('Harry Potter and the Chamber of Secrets',),
                ('Harry Potter and the Prisoner of Azkaban',),
                ('Harry Potter and the Goblet of Fire',),
                ('Harry Potter and the Order of the Phoenix',),
                ('Harry Potter and the Half-Blood Prince',),
                ('Harry Potter and the Deathly Hallows',),
                ('Good Omens',),
                ('Guards! Guards!',),
                ('Small Gods',),
                ('Mort',),
                ('American Gods',),
                ('Neverwhere',),
                ('Stardust',),
                ('Coraline',),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 04_order_by.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_04_exercise_1": {
        "correct_sql": "SELECT title FROM book ORDER BY title LIMIT 10",
        "expected_rows": [
                ('A Clash of Kings',),
                ('A Dance with Dragons',),
                ('A Feast for Crows',),
                ('A Game of Thrones',),
                ('A Storm of Swords',),
                ('American Gods',),
                ('Coraline',),
                ('Elantris',),
                ('Good Omens',),
                ('Guards! Guards!',),
            ],
    },
    "m04_nb_04_exercise_2": {
        "correct_sql": "SELECT DISTINCT publisher_city FROM book",
        "expected_rows": [
                ('London',),
                ('New York',),
            ],
    },
    "m04_nb_04_exercise_3": {
        "correct_sql": "SELECT full_name FROM member ORDER BY full_name LIMIT 5",
        "expected_rows": [
                ('Amanda White',),
                ('Christopher Lee',),
                ('Dimitris Stavros',),
                ('Eleni Makri',),
                ('Emily Thompson',),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 05_aggregate_functions_and_grouping.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_05_exercise_1": {
        "correct_sql": "SELECT COUNT(*) FROM member",
        "expected_rows": [
                (20,),
            ],
    },
    "m04_nb_05_exercise_2": {
        "correct_sql": "SELECT publisher_city, COUNT(*) FROM book GROUP BY publisher_city",
        "expected_rows": [
                ('London', 21),
                ('New York', 14),
            ],
    },
    "m04_nb_05_exercise_3": {
        "correct_sql": "SELECT country, COUNT(*) FROM member GROUP BY country",
        "expected_rows": [
                ('France', 3),
                ('Germany', 2),
                ('Greece', 7),
                ('United Kingdom', 4),
                ('United States', 4),
            ],
    },
    "m04_nb_05_exercise_4": {
        "correct_sql": "SELECT publisher_name, COUNT(*) FROM book GROUP BY publisher_name HAVING COUNT(*) > 6",
        "expected_rows": [
                ('Bloomsbury Publishing', 7),
                ('Tor Books', 7),
                ('Victor Gollancz', 8),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 06_practice_queries.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_06_exercise_1": {
        "correct_sql": "SELECT name FROM artist WHERE name LIKE '%Black%'",
        "expected_rows": [
                ('Banda Black Rio',),
                ('Black Eyed Peas',),
                ('Black Label Society',),
                ('Black Sabbath',),
                ('The Black Crowes',),
            ],
    },
    "m04_nb_06_exercise_2": {
        "correct_sql": "SELECT COUNT(*) FROM track WHERE unit_price = 0.99",
        "expected_rows": [
                (3290,),
            ],
    },
    "m04_nb_06_exercise_3": {
        "correct_sql": "SELECT name FROM track ORDER BY milliseconds DESC LIMIT 5",
        "expected_rows": [
                ('Occupation / Precipice',),
                ('Through a Looking Glass',),
                ('Greetings from Earth, Pt. 1',),
                ('The Man With Nine Lives',),
                ('Battlestar Galactica, Pt. 2',),
            ],
    },
    "m04_nb_06_exercise_4": {
        "correct_sql": "SELECT MIN(milliseconds), MAX(milliseconds) FROM track",
        "expected_rows": [
                (1071, 5286953),
            ],
    },
    "m04_nb_06_exercise_5": {
        "correct_sql": "SELECT name FROM genre ORDER BY name",
        "expected_rows": [
                ('Alternative',),
                ('Alternative & Punk',),
                ('Blues',),
                ('Bossa Nova',),
                ('Classical',),
                ('Comedy',),
                ('Drama',),
                ('Easy Listening',),
                ('Electronica/Dance',),
                ('Heavy Metal',),
                ('Hip Hop/Rap',),
                ('Jazz',),
                ('Latin',),
                ('Metal',),
                ('Opera',),
                ('Pop',),
                ('R&B/Soul',),
                ('Reggae',),
                ('Rock',),
                ('Rock And Roll',),
                ('Sci Fi & Fantasy',),
                ('Science Fiction',),
                ('Soundtrack',),
                ('TV Shows',),
                ('World',),
            ],
    },
    "m04_nb_06_exercise_6": {
        "correct_sql": "SELECT DISTINCT billing_country FROM invoice ORDER BY billing_country",
        "expected_rows": [
                ('Argentina',),
                ('Australia',),
                ('Austria',),
                ('Belgium',),
                ('Brazil',),
                ('Canada',),
                ('Chile',),
                ('Czech Republic',),
                ('Denmark',),
                ('Finland',),
                ('France',),
                ('Germany',),
                ('Hungary',),
                ('India',),
                ('Ireland',),
                ('Italy',),
                ('Netherlands',),
                ('Norway',),
                ('Poland',),
                ('Portugal',),
                ('Spain',),
                ('Sweden',),
                ('United Kingdom',),
                ('USA',),
            ],
    },
    "m04_nb_06_exercise_7": {
        "correct_sql": "SELECT genre_id, COUNT(*) FROM track GROUP BY genre_id ORDER BY COUNT(*) DESC, genre_id LIMIT 5",
        "expected_rows": [
                (1, 1297),
                (7, 579),
                (3, 374),
                (4, 332),
                (2, 130),
            ],
    },
    "m04_nb_06_exercise_8": {
        "correct_sql": "SELECT media_type_id, COUNT(*) FROM track GROUP BY media_type_id",
        "expected_rows": [
                (1, 3034),
                (2, 237),
                (3, 214),
                (4, 7),
                (5, 11),
            ],
    },
    "m04_nb_06_exercise_9": {
        "correct_sql": "SELECT COUNT(*) FROM track WHERE genre_id = 1 AND milliseconds > 300000",
        "expected_rows": [
                (407,),
            ],
    },
    "m04_nb_06_exercise_10": {
        "correct_sql": "SELECT artist_id, COUNT(*) FROM album GROUP BY artist_id HAVING COUNT(*) > 10 ORDER BY COUNT(*) DESC, artist_id",
        "expected_rows": [
                (90, 21),
                (22, 14),
                (58, 11),
            ],
    },
    "m04_nb_06_exercise_11": {
        "correct_sql": "SELECT country, COUNT(*) FROM customer GROUP BY country HAVING COUNT(*) > 4 ORDER BY COUNT(*) DESC, country",
        "expected_rows": [
                ('USA', 13),
                ('Canada', 8),
                ('Brazil', 5),
                ('France', 5),
            ],
    },
    "m04_nb_06_exercise_12": {
        "correct_sql": "SELECT composer, COUNT(*) FROM track WHERE composer IS NOT NULL GROUP BY composer HAVING COUNT(*) > 20 ORDER BY COUNT(*) DESC, composer",
        "expected_rows": [
                ('Steve Harris', 80),
                ('U2', 44),
                ('Jagger/Richards', 35),
                ('Billy Corgan', 31),
                ('Kurt Cobain', 26),
                ('Bill Berry-Peter Buck-Mike Mills-Michael Stipe', 25),
                ('The Tea Party', 24),
                ('Chico Science', 23),
                ('Chris Cornell', 23),
                ('Gilberto Gil', 23),
                ('Miles Davis', 23),
                ('Titãs', 22),
            ],
    },
    "m04_nb_06_exercise_13": {
        "correct_sql": "SELECT billing_country, COUNT(*) FROM invoice GROUP BY billing_country HAVING COUNT(*) >= 7 ORDER BY billing_country",
        "expected_rows": [
                ('Argentina', 7),
                ('Australia', 7),
                ('Austria', 7),
                ('Belgium', 7),
                ('Brazil', 35),
                ('Canada', 56),
                ('Chile', 7),
                ('Czech Republic', 14),
                ('Denmark', 7),
                ('Finland', 7),
                ('France', 35),
                ('Germany', 28),
                ('Hungary', 7),
                ('India', 13),
                ('Ireland', 7),
                ('Italy', 7),
                ('Netherlands', 7),
                ('Norway', 7),
                ('Poland', 7),
                ('Portugal', 14),
                ('Spain', 7),
                ('Sweden', 7),
                ('United Kingdom', 21),
                ('USA', 91),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 07_joins.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_07_exercise_1": {
        "correct_sql": """SELECT b.title FROM loan l
        JOIN book b ON l.book_id = b.book_id
        JOIN member m ON l.member_id = m.member_id
        WHERE m.full_name = 'Dimitris Stavros'""",
        "expected_rows": [
                ('A Clash of Kings',),
                ('A Dance with Dragons',),
                ('Good Omens',),
            ],
    },
    "m04_nb_07_exercise_2": {
        "correct_sql": """SELECT b.title, COUNT(*) FROM book b
        JOIN loan l ON b.book_id = l.book_id
        GROUP BY b.title HAVING COUNT(*) > 1""",
        "expected_rows": [
                ('A Clash of Kings', 2),
                ('A Game of Thrones', 2),
                ('A Storm of Swords', 2),
                ('Good Omens', 2),
                ('Guards! Guards!', 2),
                ('Harry Potter and the Chamber of Secrets', 2),
                ("Harry Potter and the Philosopher's Stone", 2),
                ('Harry Potter and the Prisoner of Azkaban', 2),
                ('Mistborn: The Final Empire', 2),
                ('Small Gods', 2),
                ('The Fellowship of the Ring', 2),
                ('The Hero of Ages', 2),
                ('The Hobbit', 2),
                ('The Two Towers', 2),
                ('The Well of Ascension', 2),
            ],
    },
    "m04_nb_07_exercise_3": {
        "correct_sql": """SELECT m.full_name, COUNT(*) FROM member m
        JOIN loan l ON m.member_id = l.member_id
        GROUP BY m.full_name HAVING COUNT(*) = 3""",
        "expected_rows": [
                ('Dimitris Stavros', 3),
                ('Eleni Makri', 3),
                ('Emily Thompson', 3),
                ('James Wilson', 3),
                ('Kostas Alexiou', 3),
                ('Maria Georgiou', 3),
                ('Nikos Papadopoulos', 3),
                ('Robert Clark', 3),
                ('Sofia Papageorgiou', 3),
                ('Vasilis Nikolaou', 3),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 08_update_delete.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_08_exercise_1": {
        "correct_sql": "SELECT title FROM book WHERE is_available = false",
        "expected_rows": [
                ('The Silmarillion',),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 09_with_clauses.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_09_exercise_1": {
        "correct_sql": """WITH loan_counts AS (
        SELECT member_id, COUNT(*) AS cnt FROM loan GROUP BY member_id
    )
    SELECT m.full_name, lc.cnt
    FROM member m JOIN loan_counts lc ON m.member_id = lc.member_id
    WHERE lc.cnt = 3""",
        "expected_rows": [
                ('Dimitris Stavros', 3),
                ('Eleni Makri', 3),
                ('Emily Thompson', 3),
                ('James Wilson', 3),
                ('Kostas Alexiou', 3),
                ('Maria Georgiou', 3),
                ('Nikos Papadopoulos', 3),
                ('Robert Clark', 3),
                ('Sofia Papageorgiou', 3),
                ('Vasilis Nikolaou', 3),
            ],
    },
    "m04_nb_09_exercise_2": {
        "correct_sql": """WITH book_loans AS (
        SELECT book_id, COUNT(*) AS cnt FROM loan GROUP BY book_id
    )
    SELECT b.title, bl.cnt
    FROM book b JOIN book_loans bl ON b.book_id = bl.book_id
    WHERE bl.cnt > 1""",
        "expected_rows": [
                ('A Clash of Kings', 2),
                ('A Game of Thrones', 2),
                ('A Storm of Swords', 2),
                ('Good Omens', 2),
                ('Guards! Guards!', 2),
                ('Harry Potter and the Chamber of Secrets', 2),
                ("Harry Potter and the Philosopher's Stone", 2),
                ('Harry Potter and the Prisoner of Azkaban', 2),
                ('Mistborn: The Final Empire', 2),
                ('Small Gods', 2),
                ('The Fellowship of the Ring', 2),
                ('The Hero of Ages', 2),
                ('The Hobbit', 2),
                ('The Two Towers', 2),
                ('The Well of Ascension', 2),
            ],
    },
    "m04_nb_09_exercise_3": {
        "correct_sql": """WITH country_counts AS (
        SELECT country, COUNT(*) AS cnt FROM member GROUP BY country
    )
    SELECT country, cnt FROM country_counts WHERE cnt > 3""",
        "expected_rows": [
                ('Greece', 7),
                ('United Kingdom', 4),
                ('United States', 4),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 10_views.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_10_exercise_1": {
        "correct_sql": "SELECT reservation_id FROM pending_reservations ORDER BY reservation_id",
        "expected_rows": [
                (2,),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 12_domains.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_12_exercise_1": {
        "correct_sql": "SELECT email IS NOT NULL AND phone IS NOT NULL FROM member WHERE member_id = 2",
        "expected_rows": [
                (True,),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 13_transactions.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_13_exercise_1": {
        "correct_sql": "SELECT is_available FROM book WHERE book_id = 10",
        "expected_rows": [
                (False,),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 04 - 14_final_review.ipynb
    # ----------------------------------------------------------------------
    "m04_nb_14_exercise_1": {
        "correct_sql": "SELECT name FROM media_type",
        "expected_rows": [
                ('MPEG audio file',),
                ('Protected AAC audio file',),
                ('Protected MPEG-4 video file',),
                ('Purchased AAC audio file',),
                ('AAC audio file',),
            ],
    },
    "m04_nb_14_exercise_2": {
        "correct_sql": "SELECT name, milliseconds FROM track ORDER BY milliseconds DESC, track_id LIMIT 10",
        "expected_rows": [
                ('Occupation / Precipice', 5286953),
                ('Through a Looking Glass', 5088838),
                ('Greetings from Earth, Pt. 1', 2960293),
                ('The Man With Nine Lives', 2956998),
                ('Battlestar Galactica, Pt. 2', 2956081),
                ('Battlestar Galactica, Pt. 1', 2952702),
                ('Murder On the Rising Star', 2935894),
                ('Battlestar Galactica, Pt. 3', 2927802),
                ('Take the Celestra', 2927677),
                ('Fire In Space', 2926593),
            ],
    },
    "m04_nb_14_exercise_3": {
        "correct_sql": "SELECT first_name, last_name, city FROM customer WHERE country = 'Brazil'",
        "expected_rows": [
                ('Luís', 'Gonçalves', 'São José dos Campos'),
                ('Eduardo', 'Martins', 'São Paulo'),
                ('Alexandre', 'Rocha', 'São Paulo'),
                ('Roberto', 'Almeida', 'Rio de Janeiro'),
                ('Fernanda', 'Ramos', 'Brasília'),
            ],
    },
    "m04_nb_14_exercise_4": {
        "correct_sql": "SELECT title FROM album WHERE title LIKE '%Greatest%'",
        "expected_rows": [
                ('Greatest Hits',),
                ('Greatest Hits I',),
                ('Greatest Hits II',),
                ('Greatest Kiss',),
                ('Motley Crue Greatest Hits',),
                ('Rotten Apples: Greatest Hits',),
                ('The Police Greatest Hits',),
                ("Vault: Def Leppard's Greatest Hits",),
            ],
    },
    "m04_nb_14_exercise_5": {
        "correct_sql": "SELECT ROUND(AVG(milliseconds)) AS avg_ms FROM track",
        "expected_rows": [
                (393599.0,),
            ],
    },
    "m04_nb_14_exercise_6": {
        "correct_sql": "SELECT g.name, COUNT(*) AS track_count FROM track t JOIN genre g ON t.genre_id = g.genre_id GROUP BY g.name HAVING COUNT(*) > 100 ORDER BY track_count DESC",
        "expected_rows": [
                ('Rock', 1297),
                ('Latin', 579),
                ('Metal', 374),
                ('Alternative & Punk', 332),
                ('Jazz', 130),
            ],
    },
    "m04_nb_14_exercise_7": {
        "correct_sql": "SELECT al.title FROM album al JOIN artist ar ON al.artist_id = ar.artist_id WHERE ar.name = 'Iron Maiden'",
        "expected_rows": [
                ('A Matter of Life and Death',),
                ('A Real Dead One',),
                ('A Real Live One',),
                ('Brave New World',),
                ('Dance Of Death',),
                ('Fear Of The Dark',),
                ('Iron Maiden',),
                ('Killers',),
                ('Live After Death',),
                ('Live At Donington 1992 (Disc 1)',),
                ('Live At Donington 1992 (Disc 2)',),
                ('No Prayer For The Dying',),
                ('Piece Of Mind',),
                ('Powerslave',),
                ('Rock In Rio [CD1]',),
                ('Rock In Rio [CD2]',),
                ('Seventh Son of a Seventh Son',),
                ('Somewhere in Time',),
                ('The Number of The Beast',),
                ('The X Factor',),
                ('Virtual XI',),
            ],
    },
    "m04_nb_14_exercise_8": {
        "correct_sql": "SELECT ar.name, COUNT(*) AS album_count FROM album al JOIN artist ar ON al.artist_id = ar.artist_id GROUP BY ar.name ORDER BY album_count DESC, ar.name LIMIT 10",
        "expected_rows": [
                ('Iron Maiden', 21),
                ('Led Zeppelin', 14),
                ('Deep Purple', 11),
                ('Metallica', 10),
                ('U2', 10),
                ('Ozzy Osbourne', 6),
                ('Pearl Jam', 5),
                ('Faith No More', 4),
                ('Foo Fighters', 4),
                ('Lost', 4),
            ],
    },
    "m04_nb_14_exercise_9": {
        "correct_sql": "SELECT c.first_name, c.last_name, SUM(i.total) AS total_spent FROM customer c JOIN invoice i ON c.customer_id = i.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spent DESC, c.customer_id LIMIT 10",
        "expected_rows": [
                ('Helena', 'Holý', 49.62),
                ('Richard', 'Cunningham', 47.62),
                ('Luis', 'Rojas', 46.62),
                ('Ladislav', 'Kovács', 45.62),
                ('Hugh', "O'Reilly", 45.62),
                ('Frank', 'Ralston', 43.62),
                ('Julia', 'Barnett', 43.62),
                ('Fynn', 'Zimmermann', 43.62),
                ('Astrid', 'Gruber', 42.62),
                ('Victor', 'Stevens', 42.62),
            ],
    },
    "m04_nb_14_exercise_10": {
        "correct_sql": "WITH genre_counts AS (SELECT genre_id, COUNT(*) AS cnt FROM track GROUP BY genre_id) SELECT g.name, gc.cnt FROM genre_counts gc JOIN genre g ON gc.genre_id = g.genre_id ORDER BY gc.cnt DESC, g.name LIMIT 5",
        "expected_rows": [
                ('Rock', 1297),
                ('Latin', 579),
                ('Metal', 374),
                ('Alternative & Punk', 332),
                ('Jazz', 130),
            ],
    },
    "m04_nb_14_exercise_11": {
        "correct_sql": "SELECT title FROM book WHERE is_available = false AND title LIKE 'Harry Potter%'",
        "expected_rows": [
                ("Harry Potter and the Philosopher's Stone",),
                ('Harry Potter and the Chamber of Secrets',),
                ('Harry Potter and the Prisoner of Azkaban',),
                ('Harry Potter and the Order of the Phoenix',),
            ],
    },
    "m04_nb_14_exercise_12": {
        "correct_sql": "SELECT m.full_name, COUNT(*) AS loan_count FROM member m JOIN loan l ON m.member_id = l.member_id GROUP BY m.member_id, m.full_name HAVING COUNT(*) > 3 ORDER BY loan_count DESC, m.full_name",
        "expected_rows": [
                ('Isabelle Martin', 4),
                ('Pierre Dupont', 4),
                ('Sarah Hartley', 4),
            ],
    },
    "m04_nb_14_exercise_13": {
        "correct_sql": "SELECT full_name, title FROM overdue_loans",
        "expected_rows": [
                ('Sarah Hartley', 'Stardust'),
                ('Pierre Dupont', 'The Great Hunt'),
                ('Isabelle Martin', 'Lord of Chaos'),
                ('Anna Pappa', 'The Tombs of Atuan'),
                ('Grace Taylor', 'Northern Lights'),
                ('Hugo Garnier', 'The Blade Itself'),
                ('Daniel Moore', 'Prince of Thorns'),
            ],
    },
    "m04_nb_14_exercise_14": {
        "correct_sql": "SELECT b.title, COUNT(*) AS copies FROM book b JOIN book_copy bc ON b.book_id = bc.book_id_book GROUP BY b.book_id, b.title ORDER BY copies DESC, b.title",
        "expected_rows": [
                ("Harry Potter and the Philosopher's Stone", 4),
                ('The Hobbit', 4),
                ('A Game of Thrones', 2),
                ('Mistborn: The Final Empire', 2),
                ('The Name of the Wind', 2),
                ('The Way of Kings', 2),
                ('The Eye of the World', 1),
                ('The Fellowship of the Ring', 1),
            ],
    },
    "m04_nb_14_exercise_15": {
        "correct_sql": "WITH book_loans AS (SELECT book_id, COUNT(*) AS cnt FROM loan GROUP BY book_id) SELECT b.title, bl.cnt FROM book_loans bl JOIN book b ON bl.book_id = b.book_id ORDER BY bl.cnt DESC, b.title LIMIT 5",
        "expected_rows": [
                ('A Clash of Kings', 2),
                ('A Game of Thrones', 2),
                ('A Storm of Swords', 2),
                ('American Gods', 2),
                ('Before They Are Hanged', 2),
            ],
    },
    # ----------------------------------------------------------------------
    # Module 05 - 02_first_normal_form.ipynb
    # ----------------------------------------------------------------------
    "m05_nb_02_exercise_1": {
        "correct_sql": r"""
        SELECT a.name
        FROM author a
        JOIN book_author ba ON ba.author_id = a.author_id
        JOIN book b ON b.book_id = ba.book_id
        WHERE b.title = 'The Silmarillion'
        ORDER BY a.name
    """,
        "expected_rows": [
                ['Christopher Tolkien'],
                ['J.R.R. Tolkien'],
            ],
    },
    # ----------------------------------------------------------------------
    # Module 05 - 04_third_normal_form.ipynb
    # ----------------------------------------------------------------------
    "m05_nb_04_exercise_1": {
        "correct_sql": r"""
        SELECT p.name AS publisher, COUNT(*) AS books
        FROM publisher p
        JOIN book b ON b.publisher_id = p.publisher_id
        GROUP BY p.name
        ORDER BY books DESC, p.name
    """,
        "expected_rows": [
                ['Gollancz', 23],
                ['Tor Books', 17],
                ['Bantam Books', 8],
                ['Bloomsbury Publishing', 7],
                ['George Allen & Unwin', 7],
                ['Harper Voyager', 7],
                ['Orbit', 4],
                ['DAW Books', 2],
            ],
    },
}
