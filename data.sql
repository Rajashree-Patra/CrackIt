-- Instructors table values
INSERT INTO instructors (instructor_name, email, expertise) VALUES
('Dr. Rajesh Sharma',    'rajesh.s@crackit.in',  'Physics'),
('Prof. Ananya Menon',   'ananya.m@crackit.in',  'Chemistry'),
('Dr. Vikram Nair',      'vikram.n@crackit.in',  'Mathematics'),
('Prof. Sunita Rao',     'sunita.r@crackit.in',  'Biology'),
('Dr. Karthik Iyer',     'karthik.i@crackit.in', 'Computer Science'),
('Prof. Deepa Krishnan', 'deepa.k@crackit.in',   'Electronics'),
('Dr. Arun Mehta',       'arun.m@crackit.in',    'Mechanical Engineering'),
('Prof. Priya Bhat',     'priya.b@crackit.in',   'English & General'),
('Dr. Suresh Pillai',    'suresh.p@crackit.in',  'Mathematics & CS'),
('Prof. Meena Joshi',    'meena.j@crackit.in',   'Physics & Electronics');

-- Exams table values
INSERT INTO exams (exam_name, exam_code, description, level) VALUES
('JEE Mains',    'JEE-M',   'Joint Entrance Examination Mains for NITs and IIITs', 'UG'),
('JEE Advanced', 'JEE-A',   'Joint Entrance Examination Advanced for IITs',        'UG'),
('NEET',         'NEET',    'National Eligibility cum Entrance Test for Medical',  'UG'),
('KCET',         'KCET',    'Karnataka Common Entrance Test',                      'UG'),
('GATE CS/IT',   'GATE-CS', 'GATE - Computer Science & IT',                        'PG'),
('GATE ECE',     'GATE-EC', 'GATE - Electronics & Communication',                  'PG'),
('GATE ME',      'GATE-ME', 'GATE - Mechanical Engineering',                       'PG'),
('COMED-K',      'COMED',   'Consortium of Medical Engineering Colleges Karnataka','UG'),
('CUET',         'CUET',    'Common University Entrance Test',                     'UG');

--Values to subjects table 
-- JEE MAINS (1)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',    1,1,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Chemistry',  1,2,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Mathematics',1,3,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Physics',    1,1,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Chemistry',  1,2,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Mathematics',1,3,'Afternoon','2:00 PM – 5:00 PM',  50,50);

-- JEE ADVANCED (2)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',    2,1,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Chemistry',  2,2,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Mathematics',2,3,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Physics',    2,1,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Chemistry',  2,2,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Mathematics',2,3,'Afternoon','2:00 PM – 5:00 PM',  40,40);

-- NEET (3)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',  3,1,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Chemistry',3,2,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Biology',  3,4,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Physics',  3,1,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Chemistry',3,2,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Biology',  3,4,'Afternoon','2:00 PM – 5:00 PM',  50,50);

-- KCET (4)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',    4,1,'Morning',  '9:00 AM – 12:00 PM',60,60),
('Chemistry',  4,2,'Morning',  '9:00 AM – 12:00 PM',60,60),
('Mathematics',4,3,'Morning',  '9:00 AM – 12:00 PM',60,60),
('Biology',    4,4,'Morning',  '9:00 AM – 12:00 PM',60,60),
('Physics',    4,1,'Afternoon','2:00 PM – 5:00 PM',  60,60),
('Chemistry',  4,2,'Afternoon','2:00 PM – 5:00 PM',  60,60),
('Mathematics',4,3,'Afternoon','2:00 PM – 5:00 PM',  60,60),
('Biology',    4,4,'Afternoon','2:00 PM – 5:00 PM',  60,60);

-- GATE CS/IT (5)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Engineering Mathematics',          5,9,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Digital Logic',                    5,5,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Computer Organization & Architecture',5,5,'Morning','9:00 AM – 12:00 PM',40,40),
('Programming & Data Structures',    5,5,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Algorithms',                       5,9,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Theory of Computation',            5,5,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Compiler Design',                  5,5,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Operating Systems',                5,9,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Databases',                        5,9,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Computer Networks',                5,5,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Engineering Mathematics',          5,9,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Digital Logic',                    5,5,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Computer Organization & Architecture',5,5,'Afternoon','2:00 PM – 5:00 PM',40,40),
('Programming & Data Structures',    5,5,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Algorithms',                       5,9,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Theory of Computation',            5,5,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Compiler Design',                  5,5,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Operating Systems',                5,9,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Databases',                        5,9,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Computer Networks',                5,5,'Afternoon','2:00 PM – 5:00 PM',  40,40);

-- GATE ECE (6)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Engineering Mathematics',      6,9, 'Morning',  '9:00 AM – 12:00 PM',40,40),
('Networks, Signals & Systems',  6,6, 'Morning',  '9:00 AM – 12:00 PM',40,40),
('Electronic Devices',           6,10,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Analog Circuits',              6,6, 'Morning',  '9:00 AM – 12:00 PM',40,40),
('Digital Circuits',             6,10,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Control Systems',              6,6, 'Morning',  '9:00 AM – 12:00 PM',40,40),
('Communications',               6,10,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Electromagnetics',             6,6, 'Morning',  '9:00 AM – 12:00 PM',40,40),
('Engineering Mathematics',      6,9, 'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Networks, Signals & Systems',  6,6, 'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Electronic Devices',           6,10,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Analog Circuits',              6,6, 'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Digital Circuits',             6,10,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Control Systems',              6,6, 'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Communications',               6,10,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Electromagnetics',             6,6, 'Afternoon','2:00 PM – 5:00 PM',  40,40);

-- GATE ME (7)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Engineering Mathematics',                          7,9,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Applied Mechanics & Design',                       7,7,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Fluid Mechanics & Thermal Sciences',               7,7,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Materials, Manufacturing & Industrial Engineering',7,7,'Morning',  '9:00 AM – 12:00 PM',40,40),
('Engineering Mathematics',                          7,9,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Applied Mechanics & Design',                       7,7,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Fluid Mechanics & Thermal Sciences',               7,7,'Afternoon','2:00 PM – 5:00 PM',  40,40),
('Materials, Manufacturing & Industrial Engineering',7,7,'Afternoon','2:00 PM – 5:00 PM',  40,40);

-- COMED-K (8)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',    8,1,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Chemistry',  8,2,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Mathematics',8,3,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Biology',    8,4,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Physics',    8,1,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Chemistry',  8,2,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Mathematics',8,3,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Biology',    8,4,'Afternoon','2:00 PM – 5:00 PM',  50,50);

-- CUET (9)
INSERT INTO subjects (subject_name,exam_id,instructor_id,batch,batch_time,total_seats,available_seats) VALUES
('Physics',      9,1,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Chemistry',    9,2,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Mathematics',  9,3,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Biology',      9,4,'Morning',  '9:00 AM – 12:00 PM',50,50),
('English',      9,8,'Morning',  '9:00 AM – 12:00 PM',50,50),
('General Test', 9,8,'Morning',  '9:00 AM – 12:00 PM',50,50),
('Physics',      9,1,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Chemistry',    9,2,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Mathematics',  9,3,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('Biology',      9,4,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('English',      9,8,'Afternoon','2:00 PM – 5:00 PM',  50,50),
('General Test', 9,8,'Afternoon','2:00 PM – 5:00 PM',  50,50);
