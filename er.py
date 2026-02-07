import graphviz

# Create the Graph for Chen's Notation
gra = graphviz.Graph('ChenER', comment='Doctor Patient ER Diagram', engine='neato')
gra.attr(overlap='false', splines='true', sep='+25')

# --- 1. Define Node Styles ---
# Entities: Rectangles
gra.attr('node', shape='box', style='filled', fillcolor='#FFFFFF', fontname='Helvetica', fontsize='12', width='1.5')
gra.node('DOCTOR')
gra.node('PATIENT')
gra.node('HOSPITAL')
gra.node('DISEASE')
gra.node('CONSULTATION_FEE')

# Relationships: Diamonds
gra.attr('node', shape='diamond', style='filled', fillcolor='#F5F5F5', fontsize='10', width='1.2', height='0.8')
gra.node('APPOINTMENT')
gra.node('WORKS_IN')
gra.node('HAS_EXPERTISE')
gra.node('DEFINES_FEE')

# Attributes: Ovals
gra.attr('node', shape='ellipse', style='solid', fillcolor='white', fontsize='9', width='0.8', height='0.5')

# --- 2. Add Attributes (Underline PKs) ---

# DOCTOR Attributes
gra.node('doc_id', label=r'<<U>Doctor_ID</U>>')
gra.node('doc_name', label='Name')
gra.node('doc_spec', label='Specialization')
gra.node('doc_cont', label='Contact_No')
gra.edge('DOCTOR', 'doc_id')
gra.edge('DOCTOR', 'doc_name')
gra.edge('DOCTOR', 'doc_spec')
gra.edge('DOCTOR', 'doc_cont')

# PATIENT Attributes
gra.node('pat_id', label=r'<<U>Patient_ID</U>>')
gra.node('pat_name', label='Name')
gra.edge('PATIENT', 'pat_id')
gra.edge('PATIENT', 'pat_name')

# HOSPITAL Attributes
gra.node('hosp_id', label=r'<<U>Hospital_ID</U>>')
gra.node('hosp_name', label='Name')
gra.node('hosp_loc', label='Location')
gra.node('hosp_lat', label='Latitude')
gra.node('hosp_long', label='Longitude')
gra.node('hosp_cont', label='Contact_No')
gra.node('hosp_rate', label='Rating')
gra.node('hosp_rev', label='Total_Reviews')
gra.node('hosp_fac', label='Facilities')
gra.node('hosp_hrs', label='Operational_Hours')

for attr in ['hosp_id', 'hosp_name', 'hosp_loc', 'hosp_lat', 'hosp_long', 'hosp_cont', 'hosp_rate', 'hosp_rev', 'hosp_fac', 'hosp_hrs']:
    gra.edge('HOSPITAL', attr)

# DISEASE Attributes
gra.node('dis_id', label=r'<<U>Disease_ID</U>>')
gra.node('dis_name', label='Name')
gra.node('dis_desc', label='Description')
gra.edge('DISEASE', 'dis_id')
gra.edge('DISEASE', 'dis_name')
gra.edge('DISEASE', 'dis_desc')

# CONSULTATION_FEE Attributes
gra.node('fee_id', label=r'<<U>Fee_ID</U>>')
gra.node('fee_type', label='Consultation_Type')
gra.node('fee_base', label='Base_Fee')
gra.node('fee_ins', label='Insurance_Accepted')
gra.edge('CONSULTATION_FEE', 'fee_id')
gra.edge('CONSULTATION_FEE', 'fee_type')
gra.edge('CONSULTATION_FEE', 'fee_base')
gra.edge('CONSULTATION_FEE', 'fee_ins')

# --- 3. Relationship Attributes ---

# APPOINTMENT Attributes (Intersection Table)
gra.node('slot_id', label=r'<<U>Slot_ID</U>>')
gra.node('slot_date', label='Slot_Date')
gra.node('slot_time', label='Slot_Time')
gra.node('duration', label='Duration_Min')
gra.node('booked', label='Is_Booked')
gra.edge('APPOINTMENT', 'slot_id')
gra.edge('APPOINTMENT', 'slot_date')
gra.edge('APPOINTMENT', 'slot_time')
gra.edge('APPOINTMENT', 'duration')
gra.edge('APPOINTMENT', 'booked')

# HAS_EXPERTISE Attributes (Intersection Table)
gra.node('exp_id', label=r'<<U>Expertise_ID</U>>')
gra.node('exp_yrs', label='Experience_Yrs')
gra.node('exp_succ', label='Success_Rate')
gra.node('exp_tot', label='Total_Cases')
gra.edge('HAS_EXPERTISE', 'exp_id')
gra.edge('HAS_EXPERTISE', 'exp_yrs')
gra.edge('HAS_EXPERTISE', 'exp_succ')
gra.edge('HAS_EXPERTISE', 'exp_tot')

# --- 4. Connect Entities & Relationships ---

# Doctor - Appointment - Patient (M:N)
gra.edge('DOCTOR', 'APPOINTMENT', label='M')
gra.edge('PATIENT', 'APPOINTMENT', label='N')

# Doctor - Works_In - Hospital (N:1)
gra.edge('DOCTOR', 'WORKS_IN', label='N')
gra.edge('HOSPITAL', 'WORKS_IN', label='1')

# Doctor - Has_Expertise - Disease (M:N)
gra.edge('DOCTOR', 'HAS_EXPERTISE', label='M')
gra.edge('DISEASE', 'HAS_EXPERTISE', label='N')

# Doctor - Defines_Fee - Consultation_Fee (1:N)
gra.edge('DOCTOR', 'DEFINES_FEE', label='1')
gra.edge('CONSULTATION_FEE', 'DEFINES_FEE', label='N')

gra.render('ChenER', view=True, format='pdf')