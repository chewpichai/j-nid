INSERT INTO orders(person_id, notation, created) VALUES(1, 'this is a test', DATE_ADD(NOW(), INTERVAL -1 DAY));
INSERT INTO orders(person_id, notation, created) VALUES(1, 'this is a test', DATE_ADD(NOW(), INTERVAL -1 HOUR));
INSERT INTO orders(person_id, notation, created) VALUES(1, 'this is a test', DATE_ADD(NOW(), INTERVAL -5 MINUTE));
INSERT INTO orders(person_id, notation, created) VALUES(2, 'this is a test', DATE_ADD(NOW(), INTERVAL -10 MINUTE));