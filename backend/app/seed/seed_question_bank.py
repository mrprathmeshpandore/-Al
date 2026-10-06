import os
import sys
import uuid
from datetime import datetime, timezone

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.user import User
from app.models.question import InterviewQuestion

SAMPLE_UPSC_QUESTIONS = [
    # 1. Administrative Leadership & Conflict Resolution
    {
        "text": "If you are appointed as District Magistrate in an agrarian region where a major national highway project is stalled due to intense protests by farmers alleging inadequate compensation, how would you resolve this conflict while ensuring infrastructure progress?",
        "category": "GOVERNANCE",
        "topic": "District Administration & Conflict Resolution",
        "difficulty": "CHALLENGING",
        "explanation": "Tests administrative discretion, stakeholder mediation, land acquisition law knowledge, and empathetic governance.",
        "why_this_matters": "Crucial for assessing an officer's capability to balance developmental imperatives with grassroots public trust."
    },
    {
        "text": "As a Sub-Divisional Magistrate, you face a communal tension situation triggered by a religious procession permit dispute during festival season. What step-by-step measures will you take to prevent law and order breakdown?",
        "category": "SECURITY",
        "topic": "Law & Order Management",
        "difficulty": "HARD",
        "explanation": "Probes crisis leadership, preventive legal measures (Sec 144 / BNSS provisions), peace committee engagement, and neutral enforcement.",
        "why_this_matters": "Directly evaluates situational agility and commitment to secular administrative neutrality."
    },
    {
        "text": "How can a District Collector effectively combat illegal sand mining driven by local political-mafia nexus without compromising personal integrity or administrative authority?",
        "category": "ETHICS",
        "topic": "Resource Governance & Anti-Corruption",
        "difficulty": "CHALLENGING",
        "explanation": "Evaluates institutional mechanisms, technological monitoring (drone/GPS tracking), inter-departmental coordination, and moral courage.",
        "why_this_matters": "Tests resilience against political pressure and enforcement of environmental rule of law."
    },
    {
        "text": "In a district plagued by severe drought, funds under MGNREGA are running low while distress migration is increasing. How would you prioritize relief work and resource allocation?",
        "category": "GOVERNANCE",
        "topic": "Drought Relief & Rural Employment",
        "difficulty": "MODERATE",
        "explanation": "Tests fiscal management, emergency convergence of schemes, creation of durable water harvesting assets, and vulnerability targeting.",
        "why_this_matters": "Evaluates welfare administration during humanitarian crises."
    },
    {
        "text": "What strategies would you adopt to bridge the trust deficit between tribal populations and district administration in Left-Wing Extremism (LWE) affected areas?",
        "category": "SECURITY",
        "topic": "Internal Security & Tribal Welfare",
        "difficulty": "CHALLENGING",
        "explanation": "Focuses on Forest Rights Act (FRA) implementation, PESA empowerment, development delivery, and winning hearts and minds.",
        "why_this_matters": "Assesses security-development nexus understanding in sensitive zones."
    },

    # 2. Ethics, Integrity & Discretion
    {
        "text": "What is the difference between 'Constitutional Morality' and 'Public Morality'? As a civil servant, which one takes precedence when public opinion strongly opposes a progressive judicial verdict?",
        "category": "ETHICS",
        "topic": "Constitutional Morality & Discretion",
        "difficulty": "CHALLENGING",
        "explanation": "Probes constitutional philosophy, judicial supremacy, protection of minority rights, and duty to rule of law over majoritarian sentiment.",
        "why_this_matters": "Core ethics question for testing constitutional grounding."
    },
    {
        "text": "If a senior minister orally instructs you to approve a land allotment proposal that technically complies with rules but clearly favors a private firm, what ethical framework would guide your response?",
        "category": "ETHICS",
        "topic": "Administrative Discretion & Ministerial Oversight",
        "difficulty": "HARD",
        "explanation": "Tests written documentation protocols, civil service conduct rules, public interest safeguards, and polite firmness.",
        "why_this_matters": "Evaluates professional integrity under hierarchical pressure."
    },
    {
        "text": "Whistleblowing within civil services often leads to personal retaliation. How should administrative law balance public interest disclosure with civil service discipline?",
        "category": "ETHICS",
        "topic": "Whistleblower Protection & Transparency",
        "difficulty": "MODERATE",
        "explanation": "Evaluates Whistleblowers Protection Act, internal grievance redressal mechanisms, institutional safeguards, and systemic accountability.",
        "why_this_matters": "Assesses understanding of institutional ethics versus personal risk."
    },
    {
        "text": "Is 'Anonymity' still a relevant civil service virtue in the age of social media, where civil servants active on platforms build personal fan followings?",
        "category": "ETHICS",
        "topic": "Civil Service Anonymity & Social Media Ethics",
        "difficulty": "MODERATE",
        "explanation": "Debates Masterman Committee principles, public communication, self-aggrandizement risks, and administrative neutrality.",
        "why_this_matters": "Modern ethical dilemma frequently discussed in civil service interviews."
    },
    {
        "text": "How do you distinguish between 'Error of Judgment' and 'Corruption' while conducting administrative inquiries against subordinate officers?",
        "category": "ETHICS",
        "topic": "Vigilance & Fair Disciplinary Inquiries",
        "difficulty": "MODERATE",
        "explanation": "Explores mens rea, bona fide decision-making protection, CVC guidelines, and preventing paralysis of administrative initiative.",
        "why_this_matters": "Essential for understanding administrative law and managerial fairness."
    },

    # 3. Public Administration & Digital Governance
    {
        "text": "While Digital India has expanded e-governance rapidly, the 'Digital Divide' threatens to exclude illiterate and elderly citizens. How would you design a digital delivery framework that ensures 100% last-mile inclusion?",
        "category": "GOVERNANCE",
        "topic": "E-Governance & Digital Inclusion",
        "difficulty": "MODERATE",
        "explanation": "Covers Assisted Digital Service Kiosks (CSC), vernacular voice-assisted interfaces, offline fallback channels, and digital literacy camps.",
        "why_this_matters": "Tests technology deployment with social empathy."
    },
    {
        "text": "Data is called the new oil. What measures must a District Magistrate take to ensure citizen data privacy while implementing AI-driven predictive policing and targeted welfare analytics?",
        "category": "GOVERNANCE",
        "topic": "Data Governance & DPDP Act Compliance",
        "difficulty": "CHALLENGING",
        "explanation": "Applies Digital Personal Data Protection (DPDP) Act, consent architecture, algorithm bias mitigation, and cybersecurity audits.",
        "why_this_matters": "Highly relevant for modern technology-driven administration."
    },
    {
        "text": "Lateral Entry into senior civil service posts has sparked debate regarding administrative accountability and meritocracy. What are the pros and cons of domain specialists versus generalist IAS officers?",
        "category": "GOVERNANCE",
        "topic": "Administrative Reforms & Lateral Entry",
        "difficulty": "CHALLENGING",
        "explanation": "Analyzes ARC recommendations, domain expertise benefits, institutional memory, tenure stability, and public service ethos.",
        "why_this_matters": "Key public administration debater topic."
    },
    {
        "text": "Citizen Charters are often criticized as toothless decorative posters in government offices. How can we transform Citizen Charters into legally enforceable service guarantees?",
        "category": "GOVERNANCE",
        "topic": "Right to Public Services & Citizen Charters",
        "difficulty": "EASY",
        "explanation": "Examines Sevottam model, Right to Services Acts, automated compensation for delay, and independent audit mechanisms.",
        "why_this_matters": "Directly impacts daily citizen-government interaction."
    },
    {
        "text": "How can Direct Benefit Transfer (DBT) and Aadhaar Enabled Payment Systems (AePS) be strengthened to prevent leakages without denying benefits due to biometric authentication failures?",
        "category": "GOVERNANCE",
        "topic": "Welfare Delivery & Biometric Safeguards",
        "difficulty": "MODERATE",
        "explanation": "Evaluates exception handling mechanisms, non-biometric authentication fallbacks, social audits, and grievance escalation.",
        "why_this_matters": "Balances anti-leakage efficiency with humanitarian safeguards."
    },

    # 4. Economic Development & Agrarian Reform
    {
        "text": "Despite high GDP growth rates, India faces persistent 'jobless growth' and informal sector vulnerability. What policy interventions would you recommend to boost labor-intensive manufacturing and micro-entrepreneurship?",
        "category": "POLITY",
        "topic": "Employment Generation & Industrial Policy",
        "difficulty": "CHALLENGING",
        "explanation": "Analyzes PLI schemes, MSME credit access, skill development alignment, labor reform implementation, and rural non-farm employment.",
        "why_this_matters": "Core macro-economic challenge facing Indian policymakers."
    },
    {
        "text": "Agrarian distress in India is often rooted in price volatility, climate shocks, and small landholdings. How can Farmer Producer Organizations (FPOs) and agri-tech startups transform smallholder economics?",
        "category": "POLITY",
        "topic": "Agricultural Economics & FPOs",
        "difficulty": "MODERATE",
        "explanation": "Evaluates economies of scale, direct market linkages, cold chain infrastructure, crop diversification, and institutional credit.",
        "why_this_matters": "Directly affects rural livelihoods and agrarian prosperity."
    },
    {
        "text": "Inflation targeting by the RBI focuses primarily on monetary policy, but food supply shocks frequently drive CPI inflation in India. How should fiscal and monetary authorities coordinate during food inflation spikes?",
        "category": "POLITY",
        "topic": "Macroeconomic Policy & Inflation Management",
        "difficulty": "CHALLENGING",
        "explanation": "Analyzes supply-side interventions, buffer stock management, export-import duty adjustments, and price stabilization funds.",
        "why_this_matters": "Tests inter-institutional economic coordination."
    },
    {
        "text": "Urbanization in India is rapidly expanding, but municipal corporations suffer from chronic financial deficits and weak capacity. How can the 74th Constitutional Amendment be empowered to revitalize municipal governance?",
        "category": "POLITY",
        "topic": "Urban Governance & Municipal Finance",
        "difficulty": "MODERATE",
        "explanation": "Discusses municipal bonds, property tax reforms, devolution of 18 functions, state finance commissions, and city leadership.",
        "why_this_matters": "Critical for sustainable urban transition."
    },
    {
        "text": "What steps can state governments take to transition smoothly towards Renewable Energy (Solar/Wind) without jeopardizing thermal power livelihoods and discom financial health?",
        "category": "ENVIRONMENT",
        "topic": "Just Energy Transition & Discom Reforms",
        "difficulty": "CHALLENGING",
        "explanation": "Explores Just Transition frameworks, green hydrogen initiatives, discom tariff rationalization, and battery storage infrastructure.",
        "why_this_matters": "Top climate-economics policy question."
    },

    # 5. Social Justice, Education & Healthcare
    {
        "text": "The National Education Policy (NEP) 2020 emphasizes foundational literacy and numeracy (FLN) in mother tongue. As District Education Officer, how would you address teacher shortages and multilingual classroom challenges?",
        "category": "GOVERNANCE",
        "topic": "Primary Education & NEP 2020",
        "difficulty": "MODERATE",
        "explanation": "Focuses on NIPUN Bharat mission, community volunteer teaching, bilingual learning material, and continuous teacher training.",
        "why_this_matters": "Tests implementation capability in social sector education."
    },
    {
        "text": "High Out-of-Pocket Expenditure (OOPE) on health plunges millions of families into poverty annually. How effective is Ayushman Bharat PM-JAY in mitigating catastrophic health expenditure?",
        "category": "GOVERNANCE",
        "topic": "Public Healthcare & Ayushman Bharat",
        "difficulty": "MODERATE",
        "explanation": "Evaluates tertiary insurance vs primary Health and Wellness Centres (HWCs), hospital empanelment quality, and fraud prevention.",
        "why_this_matters": "Essential for evaluating human development indicators."
    },
    {
        "text": "Female Labor Force Participation Rate (FLFPR) in India remains relatively low despite rising female literacy. What structural socio-economic barriers exist, and how can administration address them?",
        "category": "POLITY",
        "topic": "Gender Empowerment & FLFPR",
        "difficulty": "CHALLENGING",
        "explanation": "Analyzes unpaid care work, safe public transport, workplace creche facilities, micro-enterprise SHG linkage, and social norms.",
        "why_this_matters": "Key inclusive growth metric."
    },
    {
        "text": "Manual scavenging persists despite legislative prohibition under the PEMSR Act. What systemic technological and administrative interventions are needed to ensure complete mechanization of sanitation work?",
        "category": "GOVERNANCE",
        "topic": "Social Justice & Sanitation Mechanization",
        "difficulty": "MODERATE",
        "explanation": "Covers NAMASTE scheme, robotic sewer cleaning machines (e.g. Bandicoot), sanitary worker cooperatives, and strict legal accountability.",
        "why_this_matters": "Directly addresses constitutional dignity and human rights."
    },
    {
        "text": "India's elderly population is projected to double by 2050. What policy measures should be instituted today to build an age-inclusive social security and geriatric healthcare architecture?",
        "category": "GOVERNANCE",
        "topic": "Demographic Shift & Senior Citizen Welfare",
        "difficulty": "EASY",
        "explanation": "Discusses pension security, silver economy incentives, community geriatric care centres, and Maintenance and Welfare of Parents Act.",
        "why_this_matters": "Prepares candidate for long-term policy vision."
    },

    # 6. Environmental Governance & Climate Action
    {
        "text": "Stubble burning in northern states triggers severe winter air pollution in the NCR region annually. Why have technological subsidies for Happy Seeders failed to completely stop burning, and what holistic solution would you propose?",
        "category": "ENVIRONMENT",
        "topic": "Air Quality Governance & Stubble Burning",
        "difficulty": "CHALLENGING",
        "explanation": "Analyzes crop diversification away from paddy, bio-decomposer technologies, ex-situ straw utilization in bio-CBG plants, and inter-state coordination.",
        "why_this_matters": "Classic environmental governance problem."
    },
    {
        "text": "Human-Wildlife Conflict is escalating in forest-fringe districts due to habitat fragmentation. How can a Divisional Forest Officer balance wildlife conservation with tribal forest-dwellers' safety and livelihood?",
        "category": "ENVIRONMENT",
        "topic": "Forestry & Human-Wildlife Conflict",
        "difficulty": "MODERATE",
        "explanation": "Discusses eco-sensitive zones, bio-fencing, solar power deterrence, rapid compensation mechanisms, and community eco-tourism.",
        "why_this_matters": "Tests ecological empathy alongside administrative law."
    },
    {
        "text": "Groundwater depletion in northwest India has reached alarming levels. How can water pricing, crop diversification incentives, and micro-irrigation mandate reverse this crisis?",
        "category": "ENVIRONMENT",
        "topic": "Water Governance & Groundwater Conservation",
        "difficulty": "MODERATE",
        "explanation": "Applies Atal Bhujal Yojana principles, power subsidy rationalization, rainwater harvesting mandates, and community water budgeting.",
        "why_this_matters": "Critical for ecological resilience and food security."
    },
    {
        "text": "Disaster management in India has successfully shifted from 'Relief-centric' to 'Prevention & Mitigation'. How can coastal districts prepare for climate-induced intense cyclones using nature-based solutions?",
        "category": "ENVIRONMENT",
        "topic": "Disaster Risk Reduction & Coastal Governance",
        "difficulty": "MODERATE",
        "explanation": "Highlights mangrove restoration, shelterbelts, early warning dissemination (ICONE), resilient housing, and community mock drills.",
        "why_this_matters": "Key Senday Framework implementation topic."
    },
    {
        "text": "Plastic waste management regulations exist on paper, but single-use plastics remain widespread. What supply-chain intervention and consumer behavioral nudges are required to enforce zero plastic pollution?",
        "category": "ENVIRONMENT",
        "topic": "Solid Waste Management & Circular Economy",
        "difficulty": "EASY",
        "explanation": "Analyzes Extended Producer Responsibility (EPR), biodegradable alternative subsidies, municipal enforcement, and LiFE movement nudges.",
        "why_this_matters": "Practical civic administration question."
    }
]


def seed_questions():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("Error: No user found in database.")
            return

        # Delete existing exact duplicates of e-governance question
        egov_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.question_text.ilike("%How can civil servants ensure effective e-governance%")
        ).all()
        
        if len(egov_questions) > 1:
            print(f"Cleaning {len(egov_questions) - 1} duplicate e-governance questions from DB...")
            for q in egov_questions[1:]:
                db.delete(q)
            db.commit()

        # Check existing questions to prevent re-seeding identical texts
        existing_texts = {q.question_text.strip().lower() for q in db.query(InterviewQuestion).all()}
        
        added_count = 0
        for item in SAMPLE_UPSC_QUESTIONS:
            clean_t = item["text"].strip().lower()
            if clean_t not in existing_texts:
                new_q = InterviewQuestion(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    question_text=item["text"],
                    question_type="MAIN",
                    category=item["category"],
                    topic=item["topic"],
                    difficulty=item["difficulty"],
                    explanation=item["explanation"],
                    why_this_matters=item["why_this_matters"],
                    status="ACTIVE",
                    is_personalized=False,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_q)
                existing_texts.add(clean_t)
                added_count += 1
        
        db.commit()
        total_now = db.query(InterviewQuestion).count()
        print(f"[SUCCESS] Seeding Complete! Added {added_count} new high-quality questions. Total questions in DB: {total_now}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_questions()
