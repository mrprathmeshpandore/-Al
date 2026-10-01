import io
import os
import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.models.user import User
from app.models.resource import Resource
from app.models.document import Document, ProcessingStatus
from app.services.storage_service import get_storage_service
from app.services.document_processor import process_document

logger = logging.getLogger("seed_upsc_resources")

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"
SYSTEM_USER_EMAIL = "system@prashasak.ai"

def generate_pdf_bytes_for_resource(resource_data: Dict[str, Any]) -> bytes:
    """Generates valid, well-structured PDF binary content using ReportLab for a built-in UPSC resource."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0B1628'),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#9A3412'),
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4
    )

    story = [
        Paragraph(resource_data["title"], title_style),
        Paragraph(
            f"<b>CATEGORY:</b> {resource_data['category'].upper()} &nbsp;|&nbsp; "
            f"<b>SUBJECT:</b> {resource_data['subject'].upper()} &nbsp;|&nbsp; "
            f"<b>SOURCE:</b> {resource_data['source']}",
            meta_style
        ),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceBefore=2, spaceAfter=10),
        Paragraph(f"<b>OFFICIAL OVERVIEW:</b> {resource_data['description']}", body_style),
        Spacer(1, 8),
    ]

    for paragraph_text in resource_data["content"].split("\n\n"):
        clean_p = paragraph_text.strip()
        if not clean_p:
            continue
        if clean_p.startswith("### "):
            story.append(Paragraph(clean_p[4:], heading_style))
        else:
            story.append(Paragraph(clean_p.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buffer.getvalue()


BUILT_IN_UPSC_RESOURCES: List[Dict[str, Any]] = [
    {
        "title": "UPSC Civil Services Syllabus & Examination Pattern",
        "category": "Syllabus & Guidance",
        "subject": "Syllabus",
        "topic": "Exam Overview & Scheme",
        "source": "UPSC Official Publication",
        "source_url": "https://upsc.gov.in",
        "description": "Official UPSC Civil Services Examination syllabus covering Prelims (GS-1 & CSAT), Mains (GS I-IV, Essay & Optionals), and Personality Test standards.",
        "content": """### I. PRELIMINARY EXAMINATION SCHEME
The Preliminary Examination consists of two objective-type papers (MCQs) of 200 marks each. Paper-I covers General Studies including Current Events of national and international importance, History of India and Indian National Movement, Indian and World Geography, Indian Polity and Governance, Economic and Social Development, General issues on Environmental Ecology, Bio-diversity and Climate Change, and General Science. Paper-II (CSAT) is a qualifying paper with a minimum threshold of 33%.

### II. MAIN EXAMINATION STRUCTURE
The Main Examination comprises 9 written papers of conventional essay type. Two qualifying language papers (Paper A Indian Language, Paper B English) of 300 marks each. Seven papers counted for merit (250 marks each): Paper I Essay; Paper II General Studies I (Indian Heritage and Culture, History and Geography of the World and Society); Paper III General Studies II (Governance, Constitution, Polity, Social Justice and International relations); Paper IV General Studies III (Technology, Economic Development, Bio-diversity, Environment, Security and Disaster Management); Paper V General Studies IV (Ethics, Integrity and Aptitude); Paper VI & VII Optional Subject Paper I & II.

### III. PERSONALITY TEST (INTERVIEW) STANDARDS
The candidate is interviewed by a Board who will have before them a record of the candidate's career. The candidate will be asked questions on matters of general interest. The object of the Interview is to assess the personal suitability of the candidate for a career in public service by a Board of competent and unbiased observers. The test is intended to judge the mental alertness, critical powers of assimilation, clear and logical exposition, balance of judgement, variety and depth of interest, ability for social cohesion and leadership, intellectual and moral integrity. The Interview carries 275 marks."""
    },
    {
        "title": "UPSC Civil Services Examination Rules & Selection Process",
        "category": "Syllabus & Guidance",
        "subject": "Exam Rules",
        "topic": "Eligibility & Selection",
        "source": "Government of India Gazette Notification",
        "source_url": "https://upsc.gov.in",
        "description": "Official rules governing CSE eligibility, attempt limits, age relaxations, service allocation, and medical standards.",
        "content": """### I. NATIONALITY AND ELIGIBILITY CRITERIA
For the Indian Administrative Service (IAS), Indian Foreign Service (IFS), and Indian Police Service (IPS), a candidate must be a citizen of India. For other services, a candidate must be either a citizen of India, a subject of Nepal, a subject of Bhutan, or a Tibetan refugee who came over to India before 1st January 1962 with the intention of permanently settling in India.

### II. AGE LIMITS AND NUMBER OF ATTEMPTS
A candidate must have attained the age of 21 years and must not have attained the age of 32 years on the 1st of August of the examination year. The upper age limit is relaxable for OBC candidates (up to 3 years), SC/ST candidates (up to 5 years), and Persons with Benchmark Disabilities (up to 10 years). General candidates are permitted 6 attempts; OBC candidates 9 attempts; SC/ST candidates unlimited attempts up to upper age limit.

### III. SERVICE ALLOCATION AND MEDICAL STANDARDS
Service allocation is conducted strictly based on merit rank, category availability, service preferences filled in the Detailed Application Form (DAF), and medical fitness certification. Physical and medical standards specified in Appendix-III of the Examination Rules govern eligibility for technical services including IPS, Indian Railway Protection Force Service, and DANIPS."""
    },
    {
        "title": "Previous Year Question Trends & Analysis (2018-2024)",
        "category": "Syllabus & Guidance",
        "subject": "PYQs",
        "topic": "Question Trends",
        "source": "UPSC Official PYQ Archive",
        "source_url": "https://upsc.gov.in",
        "description": "Comprehensive analysis of recurring themes, subject weightage, and high-yield areas across 7 years of UPSC Mains and Interview papers.",
        "content": """### I. GENERAL STUDIES PAPER-I TREND ANALYSIS
Over the 2018-2024 period, Modern Indian History questions emphasize socio-religious reform movements, tribal uprisings, and revolutionary struggles. Art and Culture focuses on temple architecture, Buddhist philosophy, and classical literature. World History questions consistently target 20th-century decolonization and world wars. Indian Society highlights urbanization challenges, women empowerment, globalization impact, and regionalism.

### II. GENERAL STUDIES PAPER-II TREND ANALYSIS
Polity questions prominently feature Judicial Review, Federalism friction points (Governor's role, inter-state river disputes), Constitutional Amendments (103rd, 104th, 105th, 106th), and Electoral Reforms. Governance sections prioritize e-governance implementation, Citizen Charters, 2nd ARC recommendations, and NGO accountability. International Relations highlights India's Neighborhood First doctrine, Indo-Pacific diplomacy, and multilateral forums (G20, BRICS, Quad).

### III. INTERVIEW BOARD QUESTION PATTERNS
Analysis of candidate transcripts indicates that 60-70% of board probing links directly to DAF entries (academic background, home district/state, employment history, optional subject, and hobbies). The remaining 30-40% tests awareness of current national policy debates, ethical dilemmas, and administrative problem-solving scenarios."""
    },
    {
        "title": "UPSC Personality Test & Interview Evaluation Framework",
        "category": "Interview & DAF",
        "subject": "Interview Prep",
        "topic": "Board Evaluation",
        "source": "UPSC Official Interview Guidelines",
        "source_url": "https://upsc.gov.in",
        "description": "Official guidelines detailing the 275-mark Personality Test evaluation criteria, board expectations, and candidate assessment parameters.",
        "content": """### I. THE NATURE OF THE PERSONALITY TEST
The Personality Test is not a test of specialized knowledge, which has already been assessed through the written Mains examination. Candidates are expected to have taken an intelligent interest not only in their special subjects of academic study but also in the events which are happening around them both within and outside their own State or Country, as well as in new currents of thought and in new discoveries.

### II. CORE EVALUATION PARAMETERS
The Board evaluates candidates on six primary attributes:
1. Mental Alertness: Ability to grasp complex questions quickly and respond accurately without hesitation.
2. Critical Powers of Assimilation: Capacity to synthesize conflicting viewpoints and extract core administrative issues.
3. Clear and Logical Exposition: Precise, structured, and articulate verbal communication.
4. Balance of Judgement: Nuanced, objective, and unbiased stance on controversial socio-political questions.
5. Variety and Depth of Interest: Genuine curiosity about national progress, local issues, and personal hobbies.
6. Intellectual and Moral Integrity: Administrative honesty, courage of conviction, and adherence to Constitutional values."""
    },
    {
        "title": "Detailed Application Form (DAF) Filling & Strategy Guide",
        "category": "Interview & DAF",
        "subject": "DAF Profile",
        "topic": "DAF Preparation",
        "source": "Prashasak AI Administrative Guidance",
        "description": "Comprehensive framework for analyzing DAF entries including home state/district nuances, educational background, work experience, and hobbies.",
        "content": """### I. MAPPING DAF KEYWORDS TO INTERVIEW PROBES
Every entry in your Detailed Application Form (DAF-I and DAF-II) is a potential trigger for interview board questions. Candidates must systematically break down their DAF into five primary zones: Personal Identity (Name meaning, place of birth, family background), Education (Schooling, University, major projects, academic choices), Home State/District (Socio-economic data, cultural heritage, local administration), Employment (Job role, institutional challenges, reasons for leaving), and Extra-Curriculars (Hobbies, sports, leadership positions).

### II. PREPARING HOME DISTRICT AND STATE PROFILES
Formulate a comprehensive administrative dossier for your home district containing:
1. Demographic Indicators: Population density, sex ratio, literacy rate, key ethnic groups.
2. Economic Base: Principal crops, industrial hubs, mineral wealth, major employers.
3. Administrative Issues: Law and order challenges, disaster vulnerability, infrastructure bottlenecks.
4. Historical & Cultural Significance: Freedom struggle events, UNESCO sites, local festivals."""
    },
    {
        "title": "Comprehensive UPSC Interview Preparation Manual",
        "category": "Interview & DAF",
        "subject": "Interview Prep",
        "topic": "Interview Strategy",
        "source": "Prashasak AI Preparation Board",
        "description": "Master guide on body language, voice modulation, structuring oral answers, managing unknown questions, and maintaining board neutrality.",
        "content": """### I. NON-VERBAL COMMUNICATION AND ETIQUETTE
1. Entry & Greeting: Walk confidently into the interview room with an upright posture. Greet the Honorable Chairperson first, followed by lady members (if present), and then remaining members.
2. Seating Posture: Sit straight with your back against the chair, feet flat on the floor, hands resting comfortably on your lap. Avoid excessive hand gestures, slumping, or leaning forward aggressively.
3. Eye Contact: Maintain respectful, natural eye contact with the board member asking the question. Occasionally scan other board members when delivering a detailed multi-part answer.

### II. STRATEGY FOR HANDLING UNKNOWN QUESTIONS
If asked a factual question outside your knowledge base:
1. Admit limitations politely: State calmly, "I am sorry, Sir/Ma'am, I am unable to recall the exact details at this moment."
2. Avoid wild guessing: Never bluff or fabricate figures. Interview board members possess decades of domain experience and easily detect speculation.
3. Educated estimation: If appropriate, ask permission: "Sir, I do not know the exact figure, but if permitted, I may make an educated estimate based on..." """
    },
    {
        "title": "Indian Polity & Constitutional Framework",
        "category": "General Studies",
        "subject": "Polity",
        "topic": "Constitutional Law",
        "source": "Constitution of India / Official Legislative Briefs",
        "source_url": "https://legislative.gov.in",
        "description": "Core constitutional principles, Fundamental Rights, Directive Principles, Parliamentary democracy, Judicial Review, and Federal structure.",
        "content": """### I. BASIC STRUCTURE DOCTRINE AND CONSTITUTIONALISM
The landmark Kesavananda Bharati judgment (1973) established that Parliament's amending power under Article 368 is not absolute and cannot alter the 'Basic Structure' of the Constitution. Essential features of the Basic Structure include Supremacy of the Constitution, Republican and Democratic form of government, Secular character, Separation of Powers between Legislature, Executive and Judiciary, Federalism, and Judicial Review.

### II. FUNDAMENTAL RIGHTS VS DIRECTIVE PRINCIPLES
Articles 12-35 confer enforceable Fundamental Rights to individuals against State action. Articles 36-51 lay down non-justiciable Directive Principles of State Policy (DPSP) aimed at establishing a welfare state. In Minerva Mills (1980), the Supreme Court affirmed that the Indian Constitution is founded on the bedrock of the balance between Fundamental Rights and Directive Principles.

### III. FEDERAL DYNAMICS AND LEGISLATIVE RELATIONS
Article 1 describes India as a 'Union of States'. The Seventh Schedule demarcates legislative jurisdiction between Union List (List I), State List (List II), and Concurrent List (List III). Key federal friction areas include the appointment and discretionary powers of Governors under Article 163, imposition of President's Rule under Article 356, deployment of central armed forces, and inter-state water disputes under Article 262."""
    },
    {
        "title": "Governance, Public Policy & Statutory Bodies",
        "category": "General Studies",
        "subject": "Governance",
        "topic": "Public Administration",
        "source": "2nd Administrative Reforms Commission (ARC) Reports",
        "source_url": "https://darpg.gov.in",
        "description": "Good governance parameters, e-governance initiatives, Citizen Charters, RTI implementation, Civil Services reforms, and statutory bodies.",
        "content": """### I. 2ND ARC RECOMMENDATIONS ON CITIZEN-CENTRIC ADMINISTRATION
The 2nd Administrative Reforms Commission emphasizes seven pillars of Good Governance: Transparency, Accountability, Responsiveness, Efficiency, Inclusivity, Rule of Law, and Empowerment. Major recommendations include enacting public service delivery guarantee acts, streamlining civil service tenure stability through Civil Services Boards, and reforming performance evaluation metrics.

### II. RIGHT TO INFORMATION (RTI) ACT 2005 EVALUATION
The RTI Act 2005 empowered citizens to seek information from public authorities, enhancing administrative transparency. Key operational challenges include pendency in Information Commissions, misuse of Section 8 exemption clauses, protection of whistleblowers, and maintaining digital records management across rural local bodies.

### III. STATUTORY AND INDEPENDENT OVERSIGHT BODIES
Independent statutory and constitutional oversight bodies—including the Comptroller and Auditor General (CAG), Central Vigilance Commission (CVC), Lokpal and Lokayuktas, and National Human Rights Commission (NHRC)—serve as crucial checks against administrative malfeasance and executive overreach."""
    },
    {
        "title": "Indian Economy & Sustainable Growth",
        "category": "General Studies",
        "subject": "Economy",
        "topic": "Macroeconomics",
        "source": "Economic Survey & Ministry of Finance Reports",
        "source_url": "https://www.indiabudget.gov.in",
        "description": "Macroeconomic indicators, fiscal policy, monetary policy framework, banking sector reforms, inflation management, and inclusive growth.",
        "content": """### I. MACROECONOMIC STABILITY AND FISCAL CONSOLIDATION
India's macroeconomic strategy focuses on balancing high economic growth with fiscal discipline. The Fiscal Responsibility and Budget Management (FRBM) framework targets reducing the central government fiscal deficit towards 4.5% of GDP. Capital Expenditure (Capex) investments in physical and digital infrastructure act as a multiplier for private sector investment and long-term economic productivity.

### II. MONETARY POLICY FRAMEWORK AND INFLATION TARGETING
The Reserve Bank of India operates under a statutory Flexible Inflation Targeting framework (4% CPI with a +/- 2% tolerance band). The Monetary Policy Committee (MPC) uses policy repo rates, Liquidity Adjustment Facility (LAF), and Open Market Operations (OMOs) to stabilize prices while supporting economic growth.

### III. FINANCIAL SECTOR REFORMS AND DIGITAL PUBLIC INFRASTRUCTURE
Key banking sector reforms include the Insolvency and Bankruptcy Code (IBC) 2016 for timely resolution of stressed assets, creation of the National Asset Reconstruction Company Limited (NARCL), and financial inclusion driven by the Jan Dhan-Aadhaar-Mobile (JAM) trinity and Unified Payments Interface (UPI)."""
    },
    {
        "title": "History of Modern India & Freedom Movement",
        "category": "General Studies",
        "subject": "History",
        "topic": "Modern History",
        "source": "National Archives of India / Public Educational Material",
        "description": "Socio-religious reform movements, Constitutional development under British rule, Freedom struggle phases, and Post-Independence integration.",
        "content": """### I. PHASES OF THE INDIAN NATIONAL MOVEMENT
1. Moderate Phase (1885-1905): Characterized by constitutional methods, petitions, resolutions, and economic critique of colonialism (Dadabhai Naoroji's Drain of Wealth theory).
2. Extremist Phase (1905-1919): Triggered by the Partition of Bengal; led by Tilak, Lajpat Rai, and Bipin Chandra Pal using Swadeshi, Boycott, and National Education as resistance tools.
3. Gandhian Phase (1919-1947): Mass mobilization through Satyagraha, Non-Cooperation Movement (1920), Civil Disobedience Movement (1930), and Quit India Movement (1942).

### II. CONSTITUTIONAL EVOLUTION UNDER BRITISH RULE
Key milestones include the Regulating Act 1773, Charter Acts of 1813 and 1833, Indian Councils Acts of 1861 and 1892, Government of India Act 1909 (Morley-Minto Reforms introducing separate electorates), Government of India Act 1919 (Montagu-Chelmsford Reforms introducing Dyarchy in provinces), and Government of India Act 1935 (Provincial Autonomy and proposed All-India Federation).

### III. POST-INDEPENDENCE INTEGRATION AND STATE REORGANIZATION
Under the leadership of Sardar Vallabhbhai Patel and V.P. Menon, over 560 princely states were integrated into the Indian Union through Instruments of Accession and diplomatic negotiation. The State Reorganization Commission (1953) headed by Fazl Ali led to the linguistic reorganization of states under the State Reorganization Act 1956."""
    },
    {
        "title": "Physical, Human & Economic Geography of India",
        "category": "General Studies",
        "subject": "Geography",
        "topic": "Indian Geography",
        "source": "Survey of India & Ministry of Earth Sciences",
        "description": "Physiographic divisions, Monsoon mechanism, river systems, resource distribution, industrial location factors, and urban planning.",
        "content": """### I. PHYSIOGRAPHY AND DRAINAGE SYSTEMS OF INDIA
India features five major physiographic divisions: The Northern Mountains (Himalayas), Northern Plains (Indo-Gangetic-Brahmaputra), Peninsular Plateau, Coastal Plains, and Islands (Andaman & Nicobar, Lakshadweep). Himalayan rivers (Indus, Ganga, Brahmaputra) are perennial, snow-fed, and antecedent, whereas Peninsular rivers (Godavari, Krishna, Mahanadi, Kaveri, Narmada, Tapti) are seasonal, rain-fed, and older.

### II. INDIAN MONSOON MECHANISM AND CLIMATE DYNAMICS
The Indian Monsoon is driven by thermal contrast between landmass and ocean, seasonal shift of the Inter-Tropical Convergence Zone (ITCZ), Tibetan Plateau heating, Tropical Easterly Jet, and Somali Jet dynamics. Climate variability is heavily influenced by global atmospheric-oceanic phenomena including El Niño-Southern Oscillation (ENSO) and Indian Ocean Dipole (IOD).

### III. RESOURCE DISTRIBUTION AND URBANIZATION CHALLENGES
Mineral resources in India are concentrated in the Chota Nagpur Plateau belt (iron ore, coal, mica, bauxite). Human geography challenges encompass rapid urbanization, informal housing, urban heat islands, water stress, and managing rural-urban migration through sustainable spatial planning."""
    },
    {
        "title": "Environment, Ecology & Biodiversity Conservation",
        "category": "General Studies",
        "subject": "Environment",
        "topic": "Environmental Science",
        "source": "Ministry of Environment, Forest and Climate Change (MoEFCC)",
        "source_url": "https://moef.gov.in",
        "description": "Climate change mitigation, COP commitments, Renewable energy transition, National Parks/Wildlife Corridors, and Environmental Protection Acts.",
        "content": """### I. CLIMATE CHANGE MITIGATION AND INDIA'S NDCs
India has updated its Nationally Determined Contributions (NDCs) under the Paris Agreement: targeting a 45% reduction in emissions intensity of GDP by 2030 (compared to 2005 levels), achieving 50% cumulative electric power installed capacity from non-fossil fuel-based energy resources by 2030, and creating an additional carbon sink of 2.5 to 3 billion tonnes of CO2 equivalent through forest cover.

### II. LEGISLATIVE AND INSTITUTIONAL CONSERVATION FRAMEWORK
1. Wildlife Protection Act 1972: Categorizes protected species and establishes Protected Area networks (National Parks, Wildlife Sanctuaries, Conservation Reserves).
2. Environment (Protection) Act 1986: Umbrella legislation authorizing Central Government to protect environmental quality and regulate industrial pollution.
3. Biological Diversity Act 2002: Three-tier structure (National Biodiversity Authority, State Boards, local Biodiversity Management Committees) for fair benefit-sharing.

### III. BIODIVERSITY HOTSPOTS AND CONSERVATION PROJECTS
India hosts four global Biodiversity Hotspots: Western Ghats, Eastern Himalayas, Indo-Burma, and Sundaland (Nicobar Islands). Key species-focused conservation initiatives include Project Tiger (1973), Project Elephant (1992), Project Snow Leopard, and Project Cheetah reintroduction."""
    },
    {
        "title": "Science & Technology for Civil Services",
        "category": "General Studies",
        "subject": "Science & Tech",
        "topic": "Emerging Technologies",
        "source": "Department of Science and Technology (DST) & ISRO",
        "source_url": "https://dst.gov.in",
        "description": "Space missions (Chandrayaan/Gaganyaan), Artificial Intelligence, Biotechnology/Genome India, Cyber Security, and Defence R&D.",
        "content": """### I. INDIAN SPACE PROGRAMME AND DEEP-SPACE EXPLORATION
ISRO's flagship missions demonstrate cost-effective space exploration capabilities:
1. Chandrayaan-3: Historic soft-landing on the lunar south pole using LVM3 launch vehicle.
2. Aditya-L1: Solar observation satellite deployed at the Sun-Earth Lagrangian Point L1.
3. Gaganyaan Programme: India's human spaceflight demonstration aiming to send astronauts to Low Earth Orbit.

### II. EMERGING TECHNOLOGIES AND DIGITAL INITIATIVES
National technological missions include:
1. National Quantum Mission: Developing quantum computing, communications, and quantum sensing hardware.
2. Artificial Intelligence Strategy: Promoting ethical AI, IndiaAI Mission for compute infrastructure, and public AI deployment.
3. Biotechnology & Genome India Project: Sequencing whole genomes to accelerate disease research and precision medicine."""
    },
    {
        "title": "International Relations & India's Foreign Policy",
        "category": "General Studies",
        "subject": "International Relations",
        "topic": "Foreign Policy",
        "source": "Ministry of External Affairs (MEA) Official Briefings",
        "source_url": "https://mea.gov.in",
        "description": "India's Neighborhood First policy, Multilateral forums (G20, BRICS, SCO, Quad), UN Security Council reforms, and Strategic Autonomy.",
        "content": """### I. STRATEGIC DOCTRINE AND NEIGHBORHOOD FIRST POLICY
India's foreign policy is anchored in 'Strategic Autonomy'—pursuing multi-alignment based on sovereign national interests rather than military alliance blocks. The 'Neighborhood First' policy prioritizes regional connectivity, trade integration, humanitarian assistance, and maritime security under the SAGAR (Security and Growth for All in the Region) vision.

### II. MULTILATERAL ENGAGEMENT AND GLOBAL SOUTH LEADERSHIP
India actively shapes global governance through multilateral and minilateral platforms:
1. G20 Leadership: Championed inclusive growth, digital public infrastructure, and permanent African Union membership.
2. BRICS & SCO: Strengthening financial alternatives and Eurasian security dialogue.
3. Quad (India, US, Japan, Australia): Promoting a free, open, inclusive, and rules-based Indo-Pacific region.

### III. REFORM OF MULTILATERAL INSTITUTIONS
India advocates comprehensive reform of global institutions established post-WWII, advocating permanent seat expansion in the UN Security Council (G4 coalition) to reflect contemporary geopolitical realities."""
    },
    {
        "title": "Indian Society & Social Justice",
        "category": "General Studies",
        "subject": "Society",
        "topic": "Social Issues",
        "source": "Ministry of Social Justice and Empowerment",
        "source_url": "https://socialjustice.gov.in",
        "description": "Social structure, Women empowerment, Poverty and Hunger alleviation, Health and Education policies, and Marginalized section welfare.",
        "content": """### I. DIVERSITY, PLURALISM AND SOCIAL COHESION IN INDIA
Indian society is characterized by caste, linguistic, religious, regional, and tribal diversity. Key social processes include secularism, communalism, regionalism, and caste dynamics. The Constitutional framework guarantees affirmative action, protection of minority rights (Articles 29 & 30), and abolition of untouchability (Article 17).

### II. GENDER EQUALITY AND WOMEN EMPOWERMENT
Key statutory and policy measures include the Nari Shakti Vandan Adhiniyam (106th Constitutional Amendment Act reserving 33% seats for women in Lok Sabha and State Assemblies), Protection of Women from Domestic Violence Act 2005, POSH Act 2013, and targeted financial inclusion schemes (Pradhan Mantri Matru Vandana Yojana).

### III. HEALTH, EDUCATION AND SOCIAL JUSTICE POLICIES
Social justice policies emphasize human capital development through National Education Policy (NEP 2020), Ayushman Bharat universal healthcare cover, Rights of Persons with Disabilities Act 2016, and targeted welfare initiatives for Scheduled Castes, Scheduled Tribes, and Particularly Vulnerable Tribal Groups (PVTGs)."""
    },
    {
        "title": "Ethics, Integrity & Aptitude (GS Paper IV)",
        "category": "General Studies",
        "subject": "Ethics",
        "topic": "Administrative Ethics",
        "source": "ARC Reports & Public Administration Frameworks",
        "description": "Ethics in public service, Emotional Intelligence, Probity in governance, Moral thinkers, and Case Study analysis methodology.",
        "content": """### I. FOUNDATIONAL VALUES FOR CIVIL SERVICES
Civil servants are expected to embody key foundational values: Integrity (uncompromising adherence to moral principles), Impartiality and Non-partisanship (serving governments of different political persuasions without bias), Objectivity (decisions based strictly on empirical evidence and merit), Dedication to Public Service, Empathy, Tolerance, and Compassion towards weaker sections.

### II. EMOTIONAL INTELLIGENCE IN ADMINISTRATION
Emotional Intelligence (EI)—encompassing Self-Awareness, Self-Regulation, Motivation, Empathy, and Social Skills—enables administrators to handle stress during crises, resolve interpersonal conflicts, negotiate with diverse stakeholders, and deliver empathetic public service.

### III. ETHICAL DECISION-MAKING MATRIX FOR CASE STUDIES
When analyzing ethical case studies:
1. Identify Key Stakeholders: Citizens, administration, political executive, vulnerable groups.
2. Highlight Ethical Dilemmas: Duty vs Compassion, Personal Safety vs Public Duty, Transparency vs Confidentiality.
3. Evaluate Options: Assess consequences against Legal Mandates, Constitutional Morality, and Public Interest."""
    },
    {
        "title": "Internal Security & Border Management",
        "category": "General Studies",
        "subject": "Internal Security",
        "topic": "Security Challenges",
        "source": "Ministry of Home Affairs (MHA) Annual Reports",
        "source_url": "https://mha.gov.in",
        "description": "Left-Wing Extremism, Cross-border terrorism, Cyber warfare, Maritime security, Money laundering (PMLA), and Border fencing.",
        "content": """### I. LEFT-WING EXTREMISM AND INTERNAL COUNTER-INSURGENCY
The government's multi-pronged strategy against Left-Wing Extremism (LWE) integrates security operations with targeted socio-economic development: expanding road connectivity, installing mobile towers in remote districts, establishing Eklavya Model Residential Schools, and deploying specialized security units (Cobra, Greyhounds).

### II. CYBER SECURITY THREATS AND CRITICAL INFRASTRUCTURE
Cyber security challenges include ransomware attacks on health/banking networks, critical infrastructure vulnerability, social media radicalization, and deepfakes. Institutional defenses include the Indian Cyber Crime Coordination Centre (I4C), CERT-In, and National Critical Information Infrastructure Protection Centre (NCIIPC).

### III. BORDER MANAGEMENT AND MARITIME SECURITY
India shares land borders with seven countries across diverse terrain. Integrated border management strategies involve smart fencing (CIBMS), border roads development (BRO), One Border One Force policy (BSF, ITBP, SSB), and enhanced coastal surveillance radar chains post-26/11."""
    },
    {
        "title": "Ethical Situations & Administrative Dilemmas Manual",
        "category": "Interview & DAF",
        "subject": "Ethics",
        "topic": "Ethical Dilemmas",
        "source": "Prashasak AI Ethics Board",
        "description": "25 real-world administrative ethical dilemmas tested by UPSC interview boards with structured constitutional resolution frameworks.",
        "content": """### I. SCENARIO 1: POLITICAL PRESSURE VS LEGAL COMPLIANCE
Dilemma: As District Magistrate, a senior political figure pressures you to bypass environmental clearance norms for a commercial project promising local employment.
Resolution Framework: Stand firm on statutory compliance. Clearly communicate legal consequences of non-compliance in writing. Propose lawful expedited evaluation mechanisms without compromising environmental impact standards.

### II. SCENARIO 2: PUBLIC PROTEST VS INFRASTRUCTURE DEVELOPMENT
Dilemma: Local residents protest against land acquisition for a national highway project, alleging inadequate compensation.
Resolution Framework: Initiate multi-stakeholder dialogue. Verify compensation calculations under LARR Act 2013. Address genuine grievances, ensure transparent rehabilitation, and maintain public order without using excessive force."""
    },
    {
        "title": "Administrative Scenarios & Decision-Making Casebook",
        "category": "Interview & DAF",
        "subject": "Governance",
        "topic": "Crisis Management",
        "source": "National Institute of Disaster Management (NIDM)",
        "source_url": "https://nidm.gov.in",
        "description": "Disaster response protocols, Law & Order maintenance, Riot control procedures, and Multi-departmental coordination scenarios.",
        "content": """### I. DISASTER RESPONSE PROTOCOL (CYCLONE / FLOOD CRISIS)
1. Immediate Action: Activate District Disaster Management Authority (DDMA) Control Room. Deploy NDRF/SDRF teams to high-risk zones.
2. Evacuation & Relief: Execute pre-planned evacuation to safe shelters. Ensure clean drinking water, food distribution, medical kits, and power backup.
3. Communication & Rehabilitation: Restore telecommunications, conduct rapid damage assessment, and disburse immediate ex-gratia relief transparently.

### II. LAW AND ORDER MANAGEMENT DURING COMMUNAL TENSION
1. Preventive Measures: Issue Section 144 orders where necessary. Convene peace committees involving community elders.
2. Enforcement: Deploy adequate police forces at vulnerable intersections. Monitor social media to curb rumor-mongering.
3. Administrative Neutrality: Ensure firm, fair, and impartial law enforcement without favoring any group."""
    },
    {
        "title": "Governance & Public Service Delivery Case Studies",
        "category": "Interview & DAF",
        "subject": "Governance",
        "topic": "Public Delivery",
        "source": "DARPG Good Governance Index Reports",
        "source_url": "https://darpg.gov.in",
        "description": "Best practices in public service delivery, Direct Benefit Transfer (DBT), Grievance Redressal mechanisms, and Aspirational Districts Programme.",
        "content": """### I. CASE STUDY: DIRECT BENEFIT TRANSFER (DBT) REVOLUTION
By leveraging Jan Dhan accounts, Aadhaar biometric verification, and mobile connectivity (JAM trinity), India eliminated ghost beneficiaries and leaked subsidies across welfare programs (PMAY, PM-KISAN, PAHAL). This public delivery model saved tens of thousands of crores in public funds while guaranteeing timely benefit transfers directly to targeted citizens.

### II. CASE STUDY: ASPIRATIONAL DISTRICTS PROGRAMME
The Aspirational Districts Programme transforms 112 under-developed districts through real-time data tracking across 49 Key Performance Indicators spanning Health & Nutrition, Education, Agriculture, Financial Inclusion, and Basic Infrastructure. The strategy emphasizes Convergence of central and state schemes, Collaboration among officers, and Competition between districts."""
    },
    {
        "title": "Current Affairs Interview Probing & Critical Analysis",
        "category": "Interview & DAF",
        "subject": "Current Affairs",
        "topic": "National & Global Debates",
        "source": "PIB & Official Press Information Bureau Briefings",
        "source_url": "https://pib.gov.in",
        "description": "Balanced commentary frameworks for controversial current events, socio-economic debates, and international geopolitical conflicts.",
        "content": """### I. ANALYZING CONTROVERSIAL NATIONAL ISSUES
When responding to sensitive topics during interview board sessions:
1. Avoid extreme polar positions. Acknowledge valid perspectives on both sides of national debates.
2. Ground arguments in Constitutional principles, Supreme Court rulings, and official committee recommendations.
3. Conclude with a constructive, forward-looking administrative solution focused on national unity, economic progress, and social equity.

### II. FRAMEWORK FOR GLOBAL GEOPOLITICAL DEBATES
Analyze international conflicts through:
1. National Interest & Energy Security: Impact on India's energy imports, diaspora welfare, and trade corridors.
2. Diplomatic Neutrality & Dialogue: Consistent advocacy for peaceful negotiation, sovereignty respect, and international law."""
    },
    {
        "title": "Structured Answer Frameworks (STAR & PESTLE for UPSC)",
        "category": "Interview & DAF",
        "subject": "Interview Prep",
        "topic": "Answer Structure",
        "source": "Prashasak AI Pedagogy Wing",
        "description": "Methodology for delivering concise 90-second interview answers using PESTLE (Political, Economic, Social, Tech, Legal, Env) and STAR methods.",
        "content": """### I. THE 3-PART ORAL ANSWER STRUCTURE
1. Introduction (15 Seconds): State your direct thesis clearly. Frame the context of the question without repeating the prompt verbatim.
2. Multidimensional Core (60 Seconds): Present 3-4 distinct dimensions (e.g., Economic impact, Social consequences, Legal mechanism). Use transition markers ('Firstly', 'Secondly', 'From a governance perspective').
3. Synthesis & Conclusion (15 Seconds): End with a balanced, forward-looking statement aligning with Constitutional values.

### II. THE PESTLE ANALYSIS METHOD FOR OPEN-ENDED QUESTIONS
Break down complex policy questions into:
- Political / Administrative dimension
- Economic / Fiscal implications
- Social / Cultural factors
- Technological interventions
- Legal / Constitutional mandate
- Environmental sustainability"""
    },
    {
        "title": "UPSC Personality Test Guidance & Communication Excellence",
        "category": "Interview & DAF",
        "subject": "Interview Prep",
        "topic": "Communication Skills",
        "source": "Prashasak AI Candidate Guidance",
        "description": "Guide to voice clarity, eye contact, respectful posture, handling disagreement, and admitting limitations ('I don't know') gracefully.",
        "content": """### I. VERBAL CLARITY AND MODULATION
1. Pace: Speak at a moderate, deliberate pace (110-130 words per minute). Avoid speaking too fast due to nervousness.
2. Tone: Maintain a respectful, confident, and warm tone. Avoid sounding confrontational or overly submissive.
3. Pause before answering: Take a 2-3 second pause after a member finishes a question to collect your thoughts before speaking.

### II. MANAGING STRESS AND AGGRESSIVE PROBING
If a board member challenges your answer or adopts a counter-argument stance:
1. Remains calm and smiling. Do not show irritation or defensiveness.
2. Acknowledge the member's perspective: "Sir, that is a valid point of view..."
3. Politely present your reasoning without arguing: "However, my perspective is based on..." If convinced by the member, concede gracefully: "I see your point, Sir, and I stand corrected." """
    },
    {
        "title": "DAF Specialization: Home District & State Nuances",
        "category": "Interview & DAF",
        "subject": "DAF Profile",
        "topic": "Regional Administration",
        "source": "Census of India & State Planning Boards",
        "source_url": "https://censusindia.gov.in",
        "description": "Framework for researching state socio-economic indicators, historical significance, cultural heritage, and local administrative challenges.",
        "content": """### I. PREPARING STATE-SPECIFIC DOSSIER
Candidates must prepare comprehensive data cards for their state of domicile and state of education:
1. Socio-Economic Profile: State GDP contribution, agricultural sector share, major industries, unemployment rate.
2. Welfare Innovations: Flagship state government schemes (e.g., Rythu Bandhu, Kanyashree, Ladli Behna, Magadh initiatives).
3. Regional Debates: State border disputes, demands for special category status, environmental concerns, water sharing.

### II. INTERVIEW QUESTION PROBES ON HOME STATE
Common board question patterns include:
- "What are the three major administrative problems facing your home state?"
- "If made District Magistrate of your home district, what would be your top three priorities?"
- "How does your state compare with neighboring states in terms of Human Development Index (HDI)?" """
    }
]


def ensure_system_user(db: Session) -> User:
    """Ensures the official system user exists in the database."""
    user = db.query(User).filter(User.id == SYSTEM_USER_ID).first()
    if not user:
        user = User(
            id=SYSTEM_USER_ID,
            email=SYSTEM_USER_EMAIL,
            full_name="Prashasak AI Official System",
            password_hash="system_protected_account_not_for_login",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created official system user record ({SYSTEM_USER_ID}).")
    return user


def seed_upsc_resources(db: Session) -> Dict[str, Any]:
    """
    Idempotent database seeding for the Built-in UPSC Knowledge Base.
    Ensures all 24 curated UPSC resources exist, generates valid PDFs,
    saves them via storage service, and executes full RAG text extraction,
    chunking, and embedding.
    """
    system_user = ensure_system_user(db)
    storage = get_storage_service()

    seeded_count = 0
    skipped_count = 0

    for res_data in BUILT_IN_UPSC_RESOURCES:
        # Idempotency check: Check if official resource with same title exists
        existing_res = db.query(Resource).filter(
            Resource.title == res_data["title"],
            Resource.is_official == True
        ).first()

        if existing_res:
            # Verify if document is already processed
            existing_doc = db.query(Document).filter(
                Document.resource_id == existing_res.id,
                Document.processing_status == ProcessingStatus.PROCESSED.value
            ).first()

            if existing_doc:
                skipped_count += 1
                continue

        # Generate PDF binary content using ReportLab
        pdf_bytes = generate_pdf_bytes_for_resource(res_data)
        safe_filename = f"builtin_{uuid.uuid4().hex[:12]}.pdf"

        # Save to Storage Service Abstraction
        storage.save_file(pdf_bytes, safe_filename)

        if not existing_res:
            # Create Resource Record
            resource = Resource(
                title=res_data["title"],
                description=res_data["description"],
                category=res_data["category"],
                subject=res_data["subject"],
                topic=res_data["topic"],
                resource_type="pdf",
                source=res_data["source"],
                is_official=True,
                created_by=system_user.id
            )
            db.add(resource)
            db.flush()
        else:
            resource = existing_res

        # Create Document Record
        document = Document(
            resource_id=resource.id,
            original_filename=f"{res_data['title']}.pdf",
            stored_filename=safe_filename,
            mime_type="application/pdf",
            file_size=len(pdf_bytes),
            page_count=0,
            processing_status=ProcessingStatus.UPLOADED.value,
            created_by=system_user.id
        )
        db.add(document)
        db.commit()
        db.refresh(resource)
        db.refresh(document)

        # Run Document Processor (Extraction -> Cleaning -> Chunking -> Embedding -> Persistence)
        success = process_document(document.id, db)
        if success:
            seeded_count += 1
            logger.info(f"Seeded official resource: '{resource.title}' ({document.id})")
        else:
            logger.error(f"Failed to process seeded resource document: '{resource.title}'")

    return {
        "status": "success",
        "seeded_count": seeded_count,
        "skipped_count": skipped_count,
        "total_official_resources": db.query(Resource).filter(Resource.is_official == True).count()
    }
