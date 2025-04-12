import random as r 

# companies, position & settings for random context generation
companies = [
    {"name": "MetaMancer", "email_domain": "@metamancer.io"},
    {"name": "Googlorithm", "email_domain": "@googlorithm.com"},
    {"name": "Amazinex", "email_domain": "@amazinex.net"},
    {"name": "MicroSynth", "email_domain": "@microsynth.tech"},
    {"name": "Applecore Systems", "email_domain": "@applecore.co"},
    {"name": "Twixter", "email_domain": "@twixter.social"},
    {"name": "Snapstack", "email_domain": "@snapstack.app"},
    {"name": "LinkedZen", "email_domain": "@linkedzen.org"},
    {"name": "Nettflixa", "email_domain": "@nettflixa.tv"},
    {"name": "Oracloud", "email_domain": "@oracloud.biz"},
    {"name": "TeslaNova", "email_domain": "@teslanova.ai"},
    {"name": "SpaceNix", "email_domain": "@spacenix.space"},
    {"name": "ChattrBox", "email_domain": "@chattrbox.chat"},
    {"name": "Netsoftique", "email_domain": "@netsoftique.dev"},
    {"name": "Adobea Labs", "email_domain": "@adobealabs.com"},
    {"name": "Cybriant", "email_domain": "@cybriant.io"},
    {"name": "Zyngr", "email_domain": "@zyngr.systems"},
    {"name": "Redwatt", "email_domain": "@redwatt.energy"},
    {"name": "Pingfinity", "email_domain": "@pingfinity.net"},
    {"name": "Fibria", "email_domain": "@fibria.cloud"},
    {"name": "CloudNook", "email_domain": "@cloudnook.io"},
    {"name": "Slaccorp", "email_domain": "@slaccorp.team"},
    {"name": "Intellix", "email_domain": "@intellix.ai"},
    {"name": "Fauxbook", "email_domain": "@fauxbook.me"},
    {"name": "CyberNode", "email_domain": "@cybernode.tech"}
]

positions = [
    "Chief Technology Officer (CTO)",
    "Senior Software Engineer",
    "Product Design Lead",
    "Human Resources Coordinator",
    "Finance Manager",
    "Director of IT Security",
    "Cloud Solutions Architect",
    "Data Analyst",
    "Customer Success Specialist",
    "Executive Assistant to CEO",
    "Compliance Officer",
    "Marketing Operations Manager",
    "DevOps Engineer",
    "UX Researcher",
    "Internal Auditor",
    "Head of Procurement",
    "Technical Recruiter",
    "Legal Counsel",
    "Sales Development Representative (SDR)",
    "Mobile App Developer",
    "Network Administrator",
    "Corporate Training Specialist",
    "Business Intelligence Analyst",
    "Payroll Administrator",
    "Systems Integration Lead"
]

email_reasons = [
    "Team update",
    "Security alert",
    "Meeting reminder",
    "IT policy change",
    "Password reset request",
    "Account suspension notice",
    "Invoice payment reminder",
    "System downtime notification",
    "New software update",
    "Vacation request approval",
    "Internal project announcement",
    "Benefit enrollment reminder",
    "Employee performance review",
    "Policy violation warning",
    "Annual report distribution",
    "Urgent action required",
    "Employee onboarding instructions",
    "Subscription renewal reminder",
    "Security breach notification",
    "Access request approval",
    "Job application status update",
    "Training program invitation",
    "Company-wide survey request",
    "Important document submission deadline",
    "Network maintenance schedule",
    "Software installation request"
]


class CONTEXT:
    def __init__(self):
        # Correcting the issue by removing commas
        self._chosen_domain_ = r.choice(companies)  # This will give a single dictionary
        print(self._chosen_domain_)  # To check the correct dictionary is selected
        self.company_name = self._chosen_domain_["name"]
        self.user_email = self._chosen_domain_["email_domain"]
        self.position = r.choice(positions)
        self.reason_for_contact = r.choice(email_reasons)
    

def generate_context():
    return CONTEXT()