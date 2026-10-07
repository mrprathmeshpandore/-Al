import os
import sys
import uuid
import sqlite3
from datetime import datetime, timezone

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"

# Multi-lingual UPSC Question Dataset
MARATHI_UPSC_QUESTIONS = [
    {
        "text": "भारतीय सनदी सेवेत (IAS) पारदर्शकता आणि उत्तरदायित्व वाढवण्यासाठी तुम्ही तंत्रज्ञानाचा कसा वापर कराल?",
        "category": "GOVERNANCE",
        "topic": "E-Governance & Digital Administration",
        "difficulty": "MODERATE",
        "explanation": "उमेदवाराने तंत्रज्ञानाचा वापर करून तक्रार निवारण आणि सेवा वितरणातील पारदर्शकता कशी आणावी हे स्पष्ट केले पाहिजे.",
        "why_this_matters": "प्रशासनातील डिजिटल परिवर्तनाची जाण आणि अंमलबजावणी क्षमता तपासण्यासाठी."
    },
    {
        "text": "महाराष्ट्रातील शेतकरी आत्महत्या आणि कृषी संकटावर मात करण्यासाठी जिल्हाधिकारी म्हणून तुमचे अल्पकालीन व दीर्घकालीन उपाय काय असतील?",
        "category": "AGRICULTURE",
        "topic": "Agrarian Crisis & Rural Economy",
        "difficulty": "CHALLENGING",
        "explanation": "जलव्यवस्थापन, पतपुरवठा, आणि बाजारपेठ सुधारणा या त्रिसूत्रीवर भर द्यावा.",
        "why_this_matters": "जमीनस्तरावरील सामाजिक-आर्थिक समस्यांवर उपाय शोधण्याची क्षमता."
    },
    {
        "text": "प्रशासकीय निर्णय घेताना नैतिक मूल्ये आणि कायद्याची काटेकोर अंमलबजावणी यातील संघर्षाच्या वेळी तुम्ही काय भूमिका घ्याल?",
        "category": "ETHICS",
        "topic": "Ethics & Administrative Discretion",
        "difficulty": "HARD",
        "explanation": "घटनात्मक नैतिकता आणि कायद्याची चौकट अबाधित ठेवून लोकहित साध्य करणे अभिप्रेत आहे.",
        "why_this_matters": "उमेदवाराचा घटनात्मक विवेक आणि निर्णयक्षमता मूल्यमापन करण्यासाठी."
    },
    {
        "text": "महिला सक्षमीकरण आणि बाल पोषण सुधारण्यासाठी जिल्हा पातळीवर कोणत्या नावीन्यपूर्ण योजना राबवता येतील?",
        "category": "SOCIAL_JUSTICE",
        "topic": "Women & Child Development",
        "difficulty": "MODERATE",
        "explanation": "स्वयं सहाय्यता गट, अंगणवाडी सक्षमीकरण आणि डिजिटल ट्रेकिंगचा वापर सुचवावा.",
        "why_this_matters": "सामाजिक कल्याण आणि समावेशक विकासाची दृष्टी."
    },
    {
        "text": "आपत्ती व्यवस्थापनात (उदा. पूर किंवा दुष्काळ) स्थानिक संस्था आणि स्वयंसेवी संस्थांचे सहकार्य कसे मिळवाल?",
        "category": "SECURITY",
        "topic": "Disaster Management & Community Resilience",
        "difficulty": "MODERATE",
        "explanation": "पूर्वसूचना प्रणाली, समुदाय सहभाग आणि जलद मदत कार्याचे नियोजन असावे.",
        "why_this_matters": "संकट काळातील नेतृत्व आणि समन्वयाची परीक्षा."
    },
    {
        "text": "पर्यावरण रक्षण आणि औद्योगिक विकास यातील समतोल कसा साधाल? पश्चिम घाटाच्या संरक्षणाचे उदाहरण देऊन सांगा.",
        "category": "ENVIRONMENT",
        "topic": "Sustainable Development & Ecology",
        "difficulty": "CHALLENGING",
        "explanation": "शाश्वत विकास आणि स्थानिक लोकांच्या उपजीविकेचा समतोल राखणे.",
        "why_this_matters": "पर्यावरणीय संवेदनशीलतेसह आर्थिक विकासाचा दृष्टिकोन."
    },
    {
        "text": "भारताच्या परराष्ट्र धोरणात 'शेजारी प्रथम' (Neighbourhood First) धोरणाचे महत्त्व काय आहे?",
        "category": "INTERNATIONAL_RELATIONS",
        "topic": "Foreign Policy & Regional Cooperation",
        "difficulty": "MODERATE",
        "explanation": "प्रादेशिक स्थैर्य, व्यापार आणि धोरणात्मक सुरक्षेच्या दृष्टिकोनातून विश्लेषित करा.",
        "why_this_matters": "भू-राजकीय घडामोडी आणि परराष्ट्र धोरणाची सखोल समज."
    },
    {
        "text": "सायबर सुरक्षा आणि डेटा गोपनीयता जपण्यासाठी प्रशासकीय पातळीवर कोणत्या उपाययोजना आवश्यक आहेत?",
        "category": "SECURITY",
        "topic": "Cyber Security & Data Governance",
        "difficulty": "CHALLENGING",
        "explanation": "डिजिटल पायाभूत सुविधांचे रक्षण आणि नागरिकांच्या डेटा संरक्षणावर भर द्यावा.",
        "why_this_matters": "आधुनिक तांत्रिक आव्हानांना तोंड देण्याची सज्जता."
    },
    {
        "text": "राजकोषीय संघराज्यवाद (Fiscal Federalism) आणि केंद्र-राज्य आर्थिक संबंधातील सद्य आव्हाने कोणती आहेत?",
        "category": "POLITY",
        "topic": "Constitutional Structure & State Grants",
        "difficulty": "HARD",
        "explanation": "जीएसटी परतावा, वित्त आयोग वाटप आणि राज्यांची आर्थिक स्वायत्तता यावर चर्चा करा.",
        "why_this_matters": "भारतीय राज्यघटनेच्या संघराज्यात्मक रचनेची पकड."
    },
    {
        "text": "पोलीस सुधारणा आणि जनता-पोलीस संबंध सुधारण्यासाठी उपविभागीय दंडाधिकारी (SDM) म्हणून तुम्ही काय पावले उचाल?",
        "category": "GOVERNANCE",
        "topic": "Police Reforms & Public Trust",
        "difficulty": "MODERATE",
        "explanation": "कम्युनिटी पोलिसींग, मानवाधिकार संरक्षण आणि उत्तरदायित्व वाढवणे.",
        "why_this_matters": "कायदा व सुव्यवस्था प्रशासनातील सुधारणावादी दृष्टी."
    }
]

HINDI_UPSC_QUESTIONS = [
    {
        "text": "लोक सेवा में सत्यनिष्ठा और पारदर्शिता सुनिश्चित करने के लिए आप एक मुख्य विकास अधिकारी (CDO) के रूप में क्या कदम उठाएंगे?",
        "category": "ETHICS",
        "topic": "Probity in Governance",
        "difficulty": "MODERATE",
        "explanation": "नागरिक चार्टर, सोशल ऑडिट और पारदर्शी ई-गवर्नेंस प्रणालियों के उपयोग पर जोर दें।",
        "why_this_matters": "प्रशासनिक ईमानदारी और नेतृत्व कौशल का परीक्षण।"
    },
    {
        "text": "ग्रामीण भारत में डिजिटल साक्षरता और वित्तीय समावेशन को बढ़ावा देने के लिए आपकी क्या रणनीति होगी?",
        "category": "GOVERNANCE",
        "topic": "Financial Inclusion & Digital Literacy",
        "difficulty": "MODERATE",
        "explanation": "जनधन-आधार-मोबाइल (JAM) त्रिमूर्ति और जन सेवा केंद्रों (CSC) के सुदृढ़ीकरण पर चर्चा करें।",
        "why_this_matters": "समावेशी विकास और जमीनी स्तर पर सेवा वितरण की समझ।"
    },
    {
        "text": "जलवायु परिवर्तन के प्रभावों का सामना करने के लिए जिला स्तर पर जलवायु अनुकूल कृषि (Climate-Smart Agriculture) को कैसे लागू करेंगे?",
        "category": "ENVIRONMENT",
        "topic": "Climate Adaptation & Agriculture",
        "difficulty": "CHALLENGING",
        "explanation": "सूखा प्रतिरोधी फसलें, सूक्ष्म सिंचाई और किसान संवेदीकरण तकनीकों का उल्लेख करें।",
        "why_this_matters": "पर्यावरण और आजीविका सुरक्षा के बीच समन्वय।"
    },
    {
        "text": "संवैधानिक नैतिकता और प्रशासनिक विवेकाधिकार में संतुलन कैसे स्थापित किया जाना चाहिए?",
        "category": "POLITY",
        "topic": "Constitutional Morality",
        "difficulty": "HARD",
        "explanation": "मूल अधिकारों की रक्षा और जनहित के बीच संतुलन बनाने की प्रशासनिक क्षमता।",
        "why_this_matters": "संवैधानिक मूल्यों के प्रति प्रतिबद्धता।"
    },
    {
        "text": "आंतरिक सुरक्षा के संदर्भ में वामपंथी उग्रवाद (LWE) से प्रभावित क्षेत्रों में विकास और सुरक्षा का संतुलन कैसे बनाएंगे?",
        "category": "SECURITY",
        "topic": "Internal Security & Counter-Insurgency",
        "difficulty": "HARD",
        "explanation": "बुनियादी ढांचे का निर्माण, युवाओं का कौशल विकास और सुरक्षा बलों का तालमेल।",
        "why_this_matters": "जटिल सुरक्षा और प्रशासनिक चुनौतियों का समाधान।"
    }
]

def seed_db(db_path):
    if not os.path.exists(db_path):
        print(f"Skipping non-existent DB: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    added_count = 0
    # Seed Marathi
    for item in MARATHI_UPSC_QUESTIONS:
        q_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO interview_questions 
            (id, user_id, question_text, question_type, difficulty, category, topic, explanation, why_this_matters, is_personalized, status, created_at, updated_at)
            VALUES (?, ?, ?, 'MAIN', ?, ?, ?, ?, ?, 0, 'ACTIVE', ?, ?)
        """, (q_id, SYSTEM_USER_ID, item["text"], item["difficulty"], item["category"], item["topic"], item["explanation"], item["why_this_matters"], now_iso, now_iso))
        added_count += 1

    # Seed Hindi
    for item in HINDI_UPSC_QUESTIONS:
        q_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO interview_questions 
            (id, user_id, question_text, question_type, difficulty, category, topic, explanation, why_this_matters, is_personalized, status, created_at, updated_at)
            VALUES (?, ?, ?, 'MAIN', ?, ?, ?, ?, ?, 0, 'ACTIVE', ?, ?)
        """, (q_id, SYSTEM_USER_ID, item["text"], item["difficulty"], item["category"], item["topic"], item["explanation"], item["why_this_matters"], now_iso, now_iso))
        added_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully seeded {added_count} questions into {db_path}")

if __name__ == "__main__":
    seed_db("backend/prashasak_ai_dev.db")
    seed_db("prashasak_ai_dev.db")
