-- ====================================================================
-- ECHONET MOCK DATA INJECTION
-- Citizen ID: d5740d3b-a05c-4d73-aefd-9c52f9da51a1 (ebi)
-- Volunteer ID: 09fe5af1-148a-48a3-9f48-776b9bd8c163 (COMMANDER SH)
-- ====================================================================

-- 1. ADD VOLUNTEER SKILLS
-- Gives the volunteer specific skills for matching algorithms
INSERT INTO volunteer_skills (volunteer_id, skill) VALUES
    ('09fe5af1-148a-48a3-9f48-776b9bd8c163', 'MEDICAL'),
    ('09fe5af1-148a-48a3-9f48-776b9bd8c163', 'RESCUE')
ON CONFLICT DO NOTHING;

-- 2. SET VOLUNTEER LOCATION (Simulated coordinates)
-- Allows the volunteer to appear on the tactical map
INSERT INTO volunteer_locations (volunteer_id, location, last_updated) VALUES
    ('09fe5af1-148a-48a3-9f48-776b9bd8c163', ST_SetSRID(ST_MakePoint(75.7873, 26.9124), 4326), NOW())
ON CONFLICT (volunteer_id) DO UPDATE SET location = EXCLUDED.location, last_updated = NOW();

-- 3. NOMINATE EMERGENCY CONTACTS FOR CITIZEN
-- Populates the Guardian Network for 'ebi'
INSERT INTO emergency_contacts (id, user_id, name, phone, is_primary) VALUES
    (uuid_generate_v4(), 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'Sarah Jenkins (Mom)', '+91 98765 43210', true),
    (uuid_generate_v4(), 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'David Smith', '+91 98765 43211', false);

-- 4. CREATE INCIDENTS REPORTED BY CITIZEN
-- Using fixed UUIDs so we can easily link tasks and messages to them
INSERT INTO incidents (id, reporter_id, category, description, location, status, required_volunteers, reported_at) VALUES
    -- Incident 1: Active Medical Emergency (Will be assigned to the volunteer)
    ('11111111-1111-1111-1111-111111111111', 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'MEDICAL', 'Individual experiencing severe chest pains. Needs immediate medical assistance.', ST_SetSRID(ST_MakePoint(75.7880, 26.9130), 4326), 'ASSIGNED', 1, NOW()),
    
    -- Incident 2: Pending Flood Alert (Will show in 'Nearby Incidents')
    ('22222222-2222-2222-2222-222222222222', 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'FLOOD', 'Water level rising rapidly in Sector 4. 3 individuals stranded on rooftop.', ST_SetSRID(ST_MakePoint(75.7900, 26.9150), 4326), 'PENDING', 2, NOW() - INTERVAL '1 hour'),
    
    -- Incident 3: Resolved Fire Incident (For historical stats)
    ('33333333-3333-3333-3333-333333333333', 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'FIRE', 'Small electrical fire contained at main intersection.', ST_SetSRID(ST_MakePoint(75.7850, 26.9100), 4326), 'RESOLVED', 1, NOW() - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- 5. ASSIGN TASKS TO VOLUNTEER
-- This populates the "Mission Count" and "Active Tasks" in the Volunteer Profile
INSERT INTO tasks (id, incident_id, volunteer_id, status, assigned_at, completed_at) VALUES
    -- Accept the active medical emergency
    (uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', '09fe5af1-148a-48a3-9f48-776b9bd8c163', 'ACCEPTED', NOW(), NULL),
    
    -- Complete the old fire incident (Adds to total stats)
    (uuid_generate_v4(), '33333333-3333-3333-3333-333333333333', '09fe5af1-148a-48a3-9f48-776b9bd8c163', 'COMPLETED', NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours')
ON CONFLICT DO NOTHING;

-- 6. GENERATE CHAT LOGS
-- Simulates real-time messaging between the Citizen and Volunteer for the active medical emergency
INSERT INTO messages (id, incident_id, sender_id, content, timestamp) VALUES
    (uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', 'd5740d3b-a05c-4d73-aefd-9c52f9da51a1', 'Please hurry, breathing is heavy.', NOW() - INTERVAL '5 minutes'),
    (uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', '09fe5af1-148a-48a3-9f48-776b9bd8c163', 'I am 2 minutes away, keep them calm and seated.', NOW() - INTERVAL '2 minutes');