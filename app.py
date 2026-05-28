from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from mock_data import EXAM_MOCK_BANK, ALTERNATIVES
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'crackit_secret_2026')
app.permanent_session_lifetime = timedelta(hours=2)

# ── Configuration ───────────────────────────
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
SLOTS_PER_BATCH_PER_DAY = 3
BATCH_SLOT_TIMES = {
    'Morning':   ['9:00 - 10:00 AM', '10:15 - 11:15 AM', '11:30 AM - 12:30 PM'],
    'Afternoon': ['2:00 - 3:00 PM',  '3:15 - 4:15 PM',   '4:30 - 5:30 PM'],
}

def get_db():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "crackit_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS")
    )

def login_required(view):
    @wraps(view)
    def wrapper(*a, **kw):
        if 'student_id' not in session:
            return redirect(url_for('login'))
        return view(*a, **kw)
    return wrapper

def admin_required(view):
    @wraps(view)
    def wrapper(*a, **kw):
        if 'admin_id' not in session:
            return redirect(url_for('login', role='admin'))
        return view(*a, **kw)
    return wrapper

@app.context_processor
def inject_notifications():
    if 'student_id' in session:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM notifications WHERE student_id=%s AND is_read=FALSE", (session['student_id'],))
        count = cur.fetchone()[0]
        cur.execute("SELECT eligibility_test_score FROM students WHERE student_id=%s", (session['student_id'],))
        row = cur.fetchone()
        conn.close()
        if row:
            return dict(unread_notifications_count=count, eligibility_passed=(row[0] is not None))
        else:
            session.pop('student_id', None) # Clean up invalid session
    return dict(unread_notifications_count=0, eligibility_passed=False)

@app.before_request
def check_eligibility():
    protected_routes = ['dashboard', 'explore', 'timetable', 'exam_detail', 'enroll', 'drop', 'profile']
    if 'student_id' in session and request.endpoint in protected_routes:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT eligibility_test_score FROM students WHERE student_id=%s", (session['student_id'],))
        row = cur.fetchone()
        conn.close()
        if not row:
            session.pop('student_id', None)
            return redirect(url_for('login'))
        if row[0] is None:
            flash("Please complete the Eligibility Mock Test to access the platform.", "info")
            return redirect(url_for('mock_test'))

# ── LANDING ──────────────────────────────────────
@app.route('/')
def index():
    if 'student_id' in session: return redirect(url_for('dashboard'))
    if 'admin_id' in session:   return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

# ── LOGIN ──────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        role     = request.form.get('role', 'student')

        conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if role == 'admin':
            cur.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (email, password))
            admin = cur.fetchone()
            if admin:
                session['admin_id']   = admin['admin_id']
                session['admin_name'] = admin['admin_name']
                session.permanent = True
                conn.close()
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials.', 'error')
        else:
            cur.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
            student = cur.fetchone()
            if student:
                cur.execute("UPDATE students SET last_login_at=NOW() WHERE student_id=%s", (student['student_id'],))
                conn.commit()
                session['student_id']   = student['student_id']
                session['student_name'] = student['student_name']
                session.permanent = True
                conn.close()
                return redirect(url_for('dashboard'))
            flash('Account not found or password incorrect.', 'error')
        conn.close()

    return render_template('unified_login.html')

# ── SIGNUP ─────────────────────────────────────
@app.route('/signup', methods=['GET','POST'])
def signup():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM exams ORDER BY exam_id")
    exams = cur.fetchall()
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        phone    = request.form.get('phone','')
        city     = request.form.get('city','')
        exam_id  = request.form.get('target_exam_id') or None
        # --- Backend Validation ---
        if not re.match(r'^[A-Za-z ]+$', name):
            flash('Name should only contain letters and spaces.', 'error')
            return render_template('signup.html', exams=exams)
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Please enter a valid email address.', 'error')
            return render_template('signup.html', exams=exams)
        if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$', password):
            flash('Password must contain upper, lower, numbers and special characters.', 'error')
            return render_template('signup.html', exams=exams)
        if not re.match(r'^\d{10}$', phone):
            flash('Phone number must be exactly 10 digits.', 'error')
            return render_template('signup.html', exams=exams)

        cur.execute("""INSERT INTO students (student_name,email,password,phone,city,target_exam_id)
                       VALUES (%s,%s,%s,%s,%s,%s)""", (name,email,password,phone,city,exam_id))
        conn.commit(); conn.close()
        flash('Account created! Welcome to CrackIt.', 'success')
        return redirect(url_for('login'))
    conn.close()
    return render_template('signup.html', exams=exams)

# ── LOGOUT ─────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── DASHBOARD ──────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get target exam info
    cur.execute("""
        SELECT e.* FROM students s 
        LEFT JOIN exams e ON e.exam_id = s.target_exam_id 
        WHERE s.student_id=%s
    """, (session['student_id'],))
    target_exam = cur.fetchone()

    # Get enrolled subjects
    cur.execute("""
        SELECT r.registration_id, e.exam_name, e.exam_code, e.level,
               s.subject_name, s.batch, s.batch_time,
               i.instructor_name, r.registration_date, s.subject_id, s.exam_id
        FROM registrations r
        JOIN subjects s ON s.subject_id = r.subject_id
        JOIN exams e ON e.exam_id = s.exam_id
        JOIN instructors i ON i.instructor_id = s.instructor_id
        WHERE r.student_id=%s AND r.status='enrolled'
        ORDER BY e.exam_name, s.batch, s.subject_name
    """, (session['student_id'],))
    enrolled = cur.fetchall()

    # Calculate Readiness Score (Wow Feature)
    readiness = 0
    if target_exam:
        cur.execute("SELECT COUNT(*) FROM subjects WHERE exam_id=%s", (target_exam['exam_id'],))
        total_subjects = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FROM registrations r 
            JOIN subjects s ON s.subject_id = r.subject_id 
            WHERE r.student_id=%s AND s.exam_id=%s AND r.status='enrolled'
        """, (session['student_id'], target_exam['exam_id']))
        my_subjects = cur.fetchone()[0]
        if total_subjects > 0:
            readiness = int((my_subjects / total_subjects) * 100)

    exams_dict = {}
    for row in enrolled:
        key = row['exam_name']
        if key not in exams_dict:
            exams_dict[key] = {'exam_code': row['exam_code'], 'subjects': []}
        exams_dict[key]['subjects'].append(row)
    
    conn.close()
    return render_template('dashboard.html', 
        exams_dict=exams_dict, 
        target_exam=target_exam,
        readiness=readiness)

# ── PROFILE ─────────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        city = request.form['city']
        bio = request.form['bio']
        target_exam_id = request.form.get('target_exam_id') or None
        
        # --- Backend Validation ---
        if not re.match(r'^[A-Za-z ]+$', name):
            flash('Name should only contain letters and spaces.', 'error')
            return redirect(url_for('profile'))
        if not re.match(r'^\d{10}$', phone):
            flash('Phone number must be exactly 10 digits.', 'error')
            return redirect(url_for('profile'))

        cur.execute("""
            UPDATE students SET student_name=%s, phone=%s, city=%s, bio=%s, target_exam_id=%s
            WHERE student_id=%s
        """, (name, phone, city, bio, target_exam_id, session['student_id']))
        conn.commit()
        session['student_name'] = name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    cur.execute("SELECT * FROM students WHERE student_id=%s", (session['student_id'],))
    student = cur.fetchone()
    cur.execute("SELECT * FROM exams ORDER BY exam_name")
    exams = cur.fetchall()
    conn.close()
    return render_template('profile.html', student=student, exams=exams)

# ── MOCK TEST ──────────────────────────────
@app.route('/mock_test', methods=['GET', 'POST'])
@login_required
def mock_test():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT eligibility_test_score, target_exam_id FROM students WHERE student_id=%s", (session['student_id'],))
    student_record = cur.fetchone()
    
    if student_record['eligibility_test_score'] is not None:
        conn.close()
        return redirect(url_for('dashboard'))

    cur.execute("SELECT exam_name, exam_id FROM exams WHERE exam_id=%s", (student_record['target_exam_id'],))
    exam_row = cur.fetchone()
    target_name = exam_row['exam_name']
    
    # Robust mapping to Bank Key
    key = target_name.upper()
    bank_key = 'CUET'
    if 'JEE MAIN' in key: bank_key = 'JEE MAINS'
    elif 'JEE ADVANCED' in key or 'ADV' in key: bank_key = 'JEE ADVANCED'
    elif 'NEET' in key: bank_key = 'NEET'
    elif 'KCET' in key: bank_key = 'KCET'
    elif 'COMED' in key: bank_key = 'COMED-K'
    elif 'GATE CS' in key or 'GATE IT' in key: bank_key = 'GATE CS/IT'
    elif 'GATE EC' in key: bank_key = 'GATE ECE'
    elif 'GATE ME' in key: bank_key = 'GATE ME'
    
    questions = EXAM_MOCK_BANK.get(bank_key, EXAM_MOCK_BANK['CUET'])

    if 'mock_idx' not in session:
        session['mock_idx'] = 0
        session['mock_score'] = 0
        session['mock_history'] = [] # To track performance by category

    idx = session['mock_idx']

    if request.method == 'POST':
        user_ans = (request.form.get('answer') or "").strip()
        current_q = questions[idx]
        actual_ans = str(current_q.get('ans')).strip()
        
        # Flex check for short-answer vs MCQ
        if current_q.get('options'):
            is_correct = (user_ans.upper() == actual_ans.upper())
        else:
            is_correct = (user_ans.lower() == actual_ans.lower())
        
        if is_correct:
            session['mock_score'] += 1
        
        # Track metadata for analysis
        session['mock_history'].append({
            'diff': current_q.get('diff'),
            'type': current_q.get('type', 'Conceptual'),
            'correct': is_correct
        })
        
        session['mock_idx'] += 1
        idx = session['mock_idx']
        
        if idx >= len(questions):
            score = session['mock_score']
            total = len(questions)
            history = session['mock_history']
            
            # --- Detailed Performance Evaluation ---
            accuracy = (score / total) * 100
            readiness = "Excellent" if accuracy >= 85 else "Good" if accuracy >= 70 else "Average" if accuracy >= 40 else "Needs Improvement"
            
            # Subject-wise / Type-wise feedback
            numerical_correct = len([h for h in history if h['type'] == 'Numerical' and h['correct']])
            numerical_total = len([h for h in history if h['type'] == 'Numerical'])
            hard_correct = len([h for h in history if h['diff'] == 'Hard' and h['correct']])
            
            # Logic for Subject Feedback
            if accuracy >= 80:
                sub_feedback = f"Outstanding grasp of {target_name} fundamentals. Your core concepts are rock solid."
                strat = "Maintain your momentum. Focus on speed and high-difficulty variations of multi-concept problems."
                conf = "High. You showed consistent accuracy across all difficulty levels."
            elif accuracy >= 60:
                sub_feedback = f"Good foundational knowledge. Some challenges observed in complex {bank_key} patterns."
                strat = "Deepen your understanding of Hard difficulty topics. Practice more application-based problems."
                conf = "Moderate. Strong on basics, but slightly hesitant on advanced analytical questions."
            else:
                sub_feedback = f"Foundational gaps detected in {target_name} syllabus. Basic concepts need immediate attention."
                strat = "Start from the basics. Revisit the NCERT/standard textbooks and resolve basic numerical doubts."
                conf = "Inconsistent. Performance fluctuates under pressure and higher difficulty."

            # Analytical / Weak Area Detection
            if numerical_total > 0 and (numerical_correct / numerical_total) < 0.5:
                weak_area = "Numerical Aptitude"
                sub_feedback += " Numerical calculations seem to be a hurdle."
            elif hard_correct == 0 and accuracy > 0:
                weak_area = "Advanced Problem Solving"
                sub_feedback += " Higher-order thinking questions were missed."
            else:
                weak_area = "None specific; overall refinement needed."

            # Final Recommendation & Alternatives
            if readiness in ['Excellent', 'Good']:
                msg = f"Fantastic! You are well-prepared for {target_name}. Focus on maintaining this consistency."
                alts = None
            else:
                alts = ALTERNATIVES.get(bank_key, "State Engineering Exams, Foundation Courses")
                msg = f"Good effort. However, {target_name} is highly competitive. We suggest strengthening your basics or exploring these alternatives."

            # Save to Database
            cur.execute("UPDATE students SET eligibility_test_score=%s WHERE student_id=%s", (score, session['student_id']))
            cur.execute("INSERT INTO notifications (student_id, title, message) VALUES (%s, %s, %s)",
                        (session['student_id'], 'Mock Test Completed', f"Status: {readiness}. {msg}"))
            conn.commit(); conn.close()
            
            final_data = {
                'score': score, 
                'total': total, 
                'readiness': readiness, 
                'subject_feedback': sub_feedback,
                'confidence_analysis': conf,
                'strategy': strat,
                'target': target_name,
                'alternatives': alts
            }
            
            # Clean up session
            session.pop('mock_idx', None)
            session.pop('mock_score', None)
            session.pop('mock_history', None)
            
            return render_template('mock_result.html', **final_data)

    conn.close()
    return render_template('mock_test.html', 
        q=questions[idx], 
        idx=idx+1, 
        total=len(questions),
        target_name=target_name)

# ── NOTIFICATIONS ──────────────────────────────
@app.route('/notifications')
@login_required
def notifications():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM notifications WHERE student_id=%s ORDER BY created_at DESC", (session['student_id'],))
    notes = cur.fetchall()
    cur.execute("UPDATE notifications SET is_read=TRUE WHERE student_id=%s AND is_read=FALSE", (session['student_id'],))
    conn.commit(); conn.close()
    return render_template('notifications.html', notifications=notes)

# ── EXPLORE EXAMS ──────────────────────────────
@app.route('/explore')
@login_required
def explore():
    search = request.args.get('q', '').strip()
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if search:
        cur.execute("SELECT * FROM exams WHERE exam_name ILIKE %s OR exam_code ILIKE %s ORDER BY level, exam_id", (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("SELECT * FROM exams ORDER BY level, exam_id")
    exams = cur.fetchall()

    cur.execute("""
        SELECT DISTINCT e.exam_id, e.level FROM registrations r
        JOIN subjects s ON s.subject_id = r.subject_id
        JOIN exams e    ON e.exam_id = s.exam_id
        WHERE r.student_id=%s AND r.status='enrolled'
    """, (session['student_id'],))
    rows = cur.fetchall()
    enrolled_exam_ids = [r['exam_id'] for r in rows]
    locked_levels = list({r['level'] for r in rows})
    conn.close()
    return render_template('explore.html',
        exams=exams,
        enrolled_exam_ids=enrolled_exam_ids,
        locked_levels=locked_levels,
        search=search)

# ── EXAM DETAIL ──────────────────────────────
@app.route('/exam/<int:exam_id>')
@login_required
def exam_detail(exam_id):
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM exams WHERE exam_id=%s", (exam_id,))
    exam = cur.fetchone()
    cur.execute("""
        SELECT s.*, i.instructor_name FROM subjects s
        JOIN instructors i ON i.instructor_id = s.instructor_id
        WHERE s.exam_id=%s ORDER BY s.batch, s.subject_name
    """, (exam_id,))
    all_subjects = cur.fetchall()
    cur.execute("""
        SELECT r.subject_id FROM registrations r
        WHERE r.student_id=%s AND r.status='enrolled'
    """, (session['student_id'],))
    enrolled_ids = [r['subject_id'] for r in cur.fetchall()]

    cur.execute("""
        SELECT DISTINCT e.level FROM registrations r
        JOIN subjects s ON s.subject_id = r.subject_id
        JOIN exams e    ON e.exam_id = s.exam_id
        WHERE r.student_id=%s AND r.status='enrolled'
    """, (session['student_id'],))
    locked_levels = [r['level'] for r in cur.fetchall()]
    conn.close()

    is_locked = bool(locked_levels) and exam['level'] not in locked_levels
    other_level = 'PG' if exam['level'] == 'UG' else 'UG'

    morning   = [s for s in all_subjects if s['batch'] == 'Morning']
    afternoon = [s for s in all_subjects if s['batch'] == 'Afternoon']

    return render_template('exam_detail.html',
        exam=exam, morning=morning, afternoon=afternoon,
        enrolled_ids=enrolled_ids,
        is_locked=is_locked, other_level=other_level)

# ── ENROLL ─────────────────────────────────────
@app.route('/enroll/<int:subject_id>')
@login_required
def enroll(subject_id):
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("CALL enroll_student(%s,%s)", (session['student_id'], subject_id))
        
        cur.execute("SELECT subject_name FROM subjects WHERE subject_id=%s", (subject_id,))
        sname = cur.fetchone()['subject_name']
        cur.execute("INSERT INTO notifications (student_id, title, message) VALUES (%s, %s, %s)",
                    (session['student_id'], 'New Enrollment', f'Successfully enrolled in {sname}.'))
        
        conn.commit()
        flash(f'Successfully enrolled in {sname}!', 'success')
    except Exception as e:
        conn.rollback()
        flash(str(e).split('\n')[0], 'error')
    finally:
        cur.execute("SELECT exam_id FROM subjects WHERE subject_id=%s", (subject_id,))
        exam_id = cur.fetchone()['exam_id']
        conn.close()
    return redirect(url_for('exam_detail', exam_id=exam_id))

# ── DROP ───────────────────────────────────────
@app.route('/drop/<int:subject_id>')
@login_required
def drop(subject_id):
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT subject_name FROM subjects WHERE subject_id=%s", (subject_id,))
        sname = cur.fetchone()['subject_name']
        cur.execute("CALL drop_subject(%s,%s)", (session['student_id'], subject_id))
        cur.execute("INSERT INTO notifications (student_id, title, message) VALUES (%s, %s, %s)",
                    (session['student_id'], 'Subject Dropped', f'You have dropped {sname}.'))
        conn.commit()
        flash(f'Subject {sname} dropped.', 'success')
    except Exception as e:
        conn.rollback()
        flash(str(e).split('\n')[0], 'error')
    finally: conn.close()
    return redirect(url_for('dashboard'))

# ── TIMETABLE ──────────────────────────────────
@app.route('/timetable')
@login_required
def timetable():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT r.registration_id, s.subject_id, s.subject_name, s.batch,
               e.exam_name, e.exam_code, e.level, i.instructor_name
        FROM registrations r
        JOIN subjects s    ON s.subject_id = r.subject_id
        JOIN exams e       ON e.exam_id = s.exam_id
        JOIN instructors i ON i.instructor_id = s.instructor_id
        WHERE r.student_id=%s AND r.status='enrolled'
        ORDER BY e.exam_id, s.subject_name, r.registration_id
    """, (session['student_id'],))
    enrolled = cur.fetchall()
    conn.close()

    by_batch = {'Morning': [], 'Afternoon': []}
    for s in enrolled:
        by_batch[s['batch']].append(s)

    capacity = len(DAYS) * SLOTS_PER_BATCH_PER_DAY
    grid = {b: [[None]*SLOTS_PER_BATCH_PER_DAY for _ in DAYS] for b in by_batch}
    for batch, subs in by_batch.items():
        if not subs: continue
        if len(subs) <= SLOTS_PER_BATCH_PER_DAY:
            for day_idx in range(len(DAYS)):
                for slot_idx in range(len(subs)):
                    grid[batch][day_idx][slot_idx] = subs[slot_idx]
        else:
            for slot in range(capacity):
                subject = subs[slot % len(subs)]
                day_idx = slot // SLOTS_PER_BATCH_PER_DAY
                slot_idx = slot % SLOTS_PER_BATCH_PER_DAY
                grid[batch][day_idx][slot_idx] = subject

    return render_template('timetable.html',
        days=DAYS, slot_times=BATCH_SLOT_TIMES, grid=grid, total=len(enrolled))

# ── ADMIN ──────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT COUNT(*) AS c FROM students");        total_students     = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM exams");           total_exams        = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM subjects");        total_subjects     = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM registrations WHERE status='enrolled'")
    total_enrollments = cur.fetchone()['c']

    # Improve Exam Popularity: Count by Target Exam in Students
    cur.execute("""
        SELECT e.exam_name, COUNT(st.student_id) AS count
        FROM exams e
        LEFT JOIN students st ON st.target_exam_id = e.exam_id
        GROUP BY e.exam_name 
        ORDER BY count DESC, e.exam_name ASC
    """)
    exam_stats = cur.fetchall()

    # Improve UG/PG Split: Count students by the level of their target exam
    cur.execute("""
        SELECT e.level, COUNT(st.student_id) AS c
        FROM students st
        JOIN exams e ON e.exam_id = st.target_exam_id
        GROUP BY e.level
    """)
    level_split = {row['level']: row['c'] for row in cur.fetchall()}

    # Recent activity
    cur.execute("""
        SELECT st.student_name, n.title, n.created_at 
        FROM notifications n 
        JOIN students st ON st.student_id = n.student_id 
        ORDER BY n.created_at DESC LIMIT 5
    """)
    recent_activity = cur.fetchall()

    conn.close()
    return render_template('admin_dashboard.html',
        total_students=total_students, total_exams=total_exams,
        total_subjects=total_subjects, total_enrollments=total_enrollments,
        exam_stats=exam_stats, level_split=level_split, recent_activity=recent_activity)

@app.route('/admin/students')
@admin_required
def admin_students():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT st.student_id, st.student_name, st.email, st.phone, st.city,
               e.exam_name AS target_exam,
               COUNT(r.registration_id) FILTER (WHERE r.status='enrolled') AS enrolled_count
        FROM students st
        LEFT JOIN exams e          ON e.exam_id = st.target_exam_id
        LEFT JOIN registrations r  ON r.student_id = st.student_id
        GROUP BY st.student_id, st.student_name, st.email, st.phone, st.city, e.exam_name
        ORDER BY st.student_id DESC
    """)
    students = cur.fetchall()
    conn.close()
    return render_template('admin_students.html', students=students)

@app.route('/admin/exam/<int:exam_id>')
@admin_required
def admin_exam_detail(exam_id):
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM exams WHERE exam_id=%s", (exam_id,))
    exam = cur.fetchone()
    cur.execute("""
        SELECT st.student_id, st.student_name, st.email, st.city,
               s.subject_name, s.batch, r.registration_date
        FROM registrations r
        JOIN students st ON st.student_id = r.student_id
        JOIN subjects s  ON s.subject_id  = r.subject_id
        WHERE s.exam_id=%s AND r.status='enrolled'
        ORDER BY st.student_name, s.subject_name
    """, (exam_id,))
    rows = cur.fetchall()
    conn.close()
    return render_template('admin_exam_detail.html', exam=exam, rows=rows)

@app.route('/admin/system')
@admin_required
def admin_system():
    conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # 1. Fetch Audit Logs (Trigger based)
    cur.execute("SELECT * FROM audit_logs ORDER BY performed_at DESC LIMIT 20")
    logs = cur.fetchall()
    
    # 2. Fetch Exam Summaries (Cursor based Procedure)
    cur.execute("SELECT exam_id, exam_name FROM exams")
    all_exams = cur.fetchall()
    
    summaries = []
    for ex in all_exams:
        # Call the CURSOR-based function
        cur.execute("SELECT generate_exam_summary(%s)", (ex['exam_id'],))
        summ = cur.fetchone()[0]
        summaries.append({'name': ex['exam_name'], 'data': summ})
        
    conn.close()
    return render_template('admin_system.html', logs=logs, summaries=summaries)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('index'))

@app.route('/init_db')
def init_db():
    try:
        conn = get_db(); cur = conn.cursor()
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())
        with open('data.sql', 'r') as f:
            cur.execute(f.read())
        conn.commit(); conn.close()
        return "Database Initialized Successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
