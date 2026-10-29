-- Student intake schema
-- student, tool, student_tool, time_slot, student_availability

CREATE TYPE school_year AS ENUM (
    'First-year',
    'Sophomore',
    'Junior',
    'Senior'
);

CREATE TYPE intro_programming AS ENUM (
    'took_it',
    'equivalent',
    'neither'
);

CREATE TYPE day_type AS ENUM (
    'weekday',
    'weekend'
);

CREATE TYPE time_period AS ENUM (
    'morning',
    'afternoon',
    'evening'
);

CREATE TABLE student (
    id                      SERIAL PRIMARY KEY,
    netid                   VARCHAR(64) NOT NULL UNIQUE,
    email                   VARCHAR(255),
    name                    VARCHAR(255) NOT NULL,
    school_year             school_year NOT NULL,
    intro_programming       intro_programming NOT NULL,
    skill_programming       SMALLINT NOT NULL CHECK (skill_programming BETWEEN 1 AND 5),
    skill_data_stats        SMALLINT NOT NULL CHECK (skill_data_stats BETWEEN 1 AND 5),
    skill_frontend_design   SMALLINT NOT NULL CHECK (skill_frontend_design BETWEEN 1 AND 5),
    skill_business_pitch    SMALLINT NOT NULL CHECK (skill_business_pitch BETWEEN 1 AND 5),
    working_style           TEXT,
    interests               TEXT,
    semester_goal           TEXT,
    submitted_at            TIMESTAMPTZ NOT NULL
);

CREATE TABLE tool (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE student_tool (
    student_id  INTEGER NOT NULL REFERENCES student (id) ON DELETE CASCADE,
    tool_id     INTEGER NOT NULL REFERENCES tool (id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, tool_id)
);

CREATE TABLE time_slot (
    id          SERIAL PRIMARY KEY,
    day_type    day_type NOT NULL,
    period      time_period NOT NULL,
    UNIQUE (day_type, period)
);

CREATE TABLE student_availability (
    student_id      INTEGER NOT NULL REFERENCES student (id) ON DELETE CASCADE,
    time_slot_id    INTEGER NOT NULL REFERENCES time_slot (id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, time_slot_id)
);

INSERT INTO time_slot (day_type, period) VALUES
    ('weekday', 'morning'),
    ('weekday', 'afternoon'),
    ('weekday', 'evening'),
    ('weekend', 'morning'),
    ('weekend', 'afternoon'),
    ('weekend', 'evening');
