DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS exams CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS instructors CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;

CREATE TABLE instructors (
    instructor_id SERIAL PRIMARY KEY,
    instructor_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    expertise VARCHAR(100)
);

CREATE TABLE exams (
    exam_id SERIAL PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL UNIQUE,
    exam_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    level VARCHAR(2) NOT NULL CHECK (level IN ('UG','PG'))
);

CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(150) NOT NULL,
    exam_id INT NOT NULL,
    instructor_id INT NOT NULL,
    batch VARCHAR(20) NOT NULL CHECK (batch IN ('Morning', 'Afternoon')),
    batch_time VARCHAR(30) NOT NULL,
    total_seats INT NOT NULL DEFAULT 50,
    available_seats INT NOT NULL DEFAULT 50,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE CASCADE
);

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL CHECK (student_name ~ '^[A-Za-z ]+$'),
    email VARCHAR(100) NOT NULL UNIQUE CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) CHECK (phone ~ '^[0-9]{10}$'),
    city VARCHAR(50),
    target_exam_id INT,
    eligibility_test_score INT DEFAULT NULL,
    last_login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bio TEXT,
    FOREIGN KEY (target_exam_id) REFERENCES exams(exam_id) ON DELETE SET NULL
);

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE registrations (
    registration_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'dropped')),
    UNIQUE (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);



-- ── Seat triggers ──

-- Automatically decrease the number of available seats in a SUBJECT table whenever a new record is inserted
CREATE OR REPLACE FUNCTION decrease_seats()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT available_seats 
        FROM subjects 
        WHERE subject_id = NEW.subject_id) = 0 
        THEN RAISE EXCEPTION 'No seats available for this subject.';
    END IF;
    UPDATE subjects 
    SET available_seats = available_seats - 1 
    WHERE subject_id = NEW.subject_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger will be activated AFTER a new record is inserted in REGISTRATIONS table
CREATE TRIGGER trg_decrease_seats
AFTER INSERT ON registrations
FOR EACH ROW EXECUTE FUNCTION decrease_seats();



-- Increase the number of available seats with +1 if a student drops the subject
CREATE OR REPLACE FUNCTION increase_seats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'dropped' AND OLD.status = 'enrolled' THEN
        UPDATE subjects SET available_seats = available_seats + 1 WHERE subject_id = NEW.subject_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger will be activated AFTER a new record is inserted in REGISTRATIONS table
CREATE TRIGGER trg_increase_seats
AFTER UPDATE ON registrations
FOR EACH ROW EXECUTE FUNCTION increase_seats();



-- ── UG / PG mutual-exclusion guard ──

-- Prevents enrolling in a PG subject if any UG enrollment exists, and vice versa.
CREATE OR REPLACE FUNCTION enforce_level_lock()
RETURNS TRIGGER AS $$
DECLARE
    new_level VARCHAR(2); -- Stores the level ('UG' or 'PG') of the subject being enrolled in
    other_level VARCHAR(2); --  Stores the opposite level
    has_other INT; -- Stores the count of conflicting enrollments
BEGIN
    SELECT e.level INTO new_level -- Saves the enrollment level directly into variable
    FROM subjects s JOIN exams e ON e.exam_id = s.exam_id -- Combines rows from subjects and exams tables where exam_id matches
    WHERE s.subject_id = NEW.subject_id;

    other_level := CASE WHEN new_level = 'UG' THEN 'PG' ELSE 'UG' END; -- := is assignment operator 

    SELECT COUNT(*) INTO has_other
    FROM registrations r
    JOIN subjects s ON s.subject_id = r.subject_id
    JOIN exams e    ON e.exam_id = s.exam_id
    WHERE r.student_id = NEW.student_id
      AND r.status = 'enrolled'
      AND e.level = other_level;

    IF has_other > 0 THEN
        RAISE EXCEPTION 'You are already enrolled in % courses. UG and PG cannot be mixed.', other_level;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger will be activated BEFORE a new record is inserted in REGISTRATIONS table
CREATE TRIGGER trg_enforce_level_lock
BEFORE INSERT ON registrations
FOR EACH ROW EXECUTE FUNCTION enforce_level_lock();



-- ── Batch conflict guard ──
-- Prevents enrolling in the same subject from the same exam in any batch.
CREATE OR REPLACE FUNCTION enforce_batch_conflict()
RETURNS TRIGGER AS $$
DECLARE
    new_subject_name VARCHAR(150); -- Store the name of the subject being enrolled in
    new_exam_id INT; -- Store the exam id which belongs to
    conflict_count INT; -- Store how many duplicate enrollments exist
BEGIN
    SELECT subject_name, exam_id INTO new_subject_name, new_exam_id
    FROM subjects
    WHERE subject_id = NEW.subject_id;

    SELECT COUNT(*) INTO conflict_count
    FROM registrations r
    JOIN subjects s ON s.subject_id = r.subject_id
    WHERE r.student_id = NEW.student_id
      AND r.status = 'enrolled'
      AND s.exam_id = new_exam_id
      AND s.subject_name = new_subject_name;

    IF conflict_count > 0 THEN
        RAISE EXCEPTION 'You are already enrolled in % for this exam. You cannot enroll in the same subject in another batch.', new_subject_name;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger will be activated BEFORE a new record is inserted in REGISTRATIONS table
CREATE TRIGGER trg_enforce_batch_conflict
BEFORE INSERT ON registrations
FOR EACH ROW EXECUTE FUNCTION enforce_batch_conflict();



-- ── Procedures ──
CREATE OR REPLACE PROCEDURE enroll_student(p_student_id INT, p_subject_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO registrations (student_id, subject_id, status)
    VALUES (p_student_id, p_subject_id, 'enrolled');
END;
$$;

CREATE OR REPLACE PROCEDURE drop_subject(p_student_id INT, p_subject_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE registrations SET status = 'dropped'
    WHERE student_id = p_student_id AND subject_id = p_subject_id AND status = 'enrolled';
    IF NOT FOUND THEN RAISE EXCEPTION 'No active enrollment found.'; END IF;
END;
$$;

-- ── Indexing for Performance ──
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_registrations_student ON registrations(student_id);
CREATE INDEX idx_subjects_exam ON subjects(exam_id);

-- ── Audit Logging System ──
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    action_type VARCHAR(10), -- INSERT, UPDATE, DELETE
    record_id INT,
    old_data TEXT,
    new_data TEXT,
    changed_by_student_id INT,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for Audit Log (Registrations)
CREATE OR REPLACE FUNCTION log_registration_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_logs (table_name, action_type, record_id, new_data, changed_by_student_id)
        VALUES ('registrations', 'INSERT', NEW.registration_id, 'Enrolled in subject ' || NEW.subject_id, NEW.student_id);
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_logs (table_name, action_type, record_id, old_data, new_data, changed_by_student_id)
        VALUES ('registrations', 'UPDATE', NEW.registration_id, OLD.status, NEW.status, NEW.student_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_registrations
AFTER INSERT OR UPDATE ON registrations
FOR EACH ROW EXECUTE FUNCTION log_registration_changes();


-- ── Stored Procedure with CURSOR ──
-- Generates a string summary of all students in an exam using a cursor
CREATE OR REPLACE FUNCTION generate_exam_summary(p_exam_id INT)
RETURNS TEXT AS $$
DECLARE
    row_data RECORD;
    summary_text TEXT := 'Exam Enrollment Report: ';
    student_cursor CURSOR FOR 
        SELECT DISTINCT st.student_name, e.exam_name
        FROM students st
        JOIN registrations r ON r.student_id = st.student_id
        JOIN subjects s ON s.subject_id = r.subject_id
        JOIN exams e ON e.exam_id = s.exam_id
        WHERE e.exam_id = p_exam_id AND r.status = 'enrolled';
BEGIN
    OPEN student_cursor;
    LOOP
        FETCH student_cursor INTO row_data;
        EXIT WHEN NOT FOUND;
        IF summary_text <> 'Exam Enrollment Report: ' THEN
            summary_text := summary_text || ', ';
        END IF;
        summary_text := summary_text || row_data.student_name || ' (' || row_data.exam_name || ')';
    END LOOP;
    CLOSE student_cursor;
    
    IF summary_text = 'Exam Enrollment Report: ' THEN
        RETURN 'No active enrollments for this exam.';
    END IF;

    RETURN summary_text;
END;
$$ LANGUAGE plpgsql;


-- Default admin 
INSERT INTO admins (admin_name, email, password)
VALUES ('CrackIt Admin', 'admin@crackit.in', 'admin123');
