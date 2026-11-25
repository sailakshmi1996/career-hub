"""
canonical_data.py
Single Canonical Source of Truth for Sai Lakshmi Elusuri's Public Portfolio & CV.
"""

import html
import os

CANDIDATE = {
    "name": "Sai Lakshmi Elusuri",
    "target_title": "Senior Power BI & Microsoft Fabric Developer",
    "location": "Utrecht region, Netherlands",
    "email": "sailakshmi.elusuri@gmail.com",
    "linkedin_url": "https://www.linkedin.com/in/sailakshmielusuri-data-analyst/",
    "linkedin_display": "linkedin.com/in/sailakshmielusuri-data-analyst",
    "github_url": "https://github.com/sailakshmi1996/career-hub",
    "showcase_url": "https://github.com/sailakshmi1996/career-hub/tree/main/technical-showcase",
    "portfolio_url": "https://sailakshmi1996.github.io/career-hub/",
    "experience_years": "8+",
    "work_auth_status": "Unrestricted Dutch labor market access",
    "ind_endorsement": "Arbeid vrij toegestaan, TWV niet vereist",
    "contract_preference": "Permanent (vast) or fixed-term · 32–40 hrs/week",
    "education": {
        "degree": "Bachelor of Technology (B.Tech.) in Computer Science & Engineering",
        "institution": "Raghu Engineering College",
        "location": "Visakhapatnam, India",
        "year": "2017",
    },
    "languages": [
        {"name": "English", "proficiency": "Professional working proficiency (C1)"},
        {"name": "Dutch", "proficiency": "Elementary (A1 — actively learning toward B1)"},
        {"name": "Telugu", "proficiency": "Native"},
        {"name": "Hindi", "proficiency": "Conversational"},
    ],
    "certifications": [
        {
            "code": "PL-300",
            "name": "Microsoft Certified: Power BI Data Analyst Associate",
            "issuer": "Microsoft",
            "primary": True,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/",
        },
        {
            "code": "DP-600",
            "name": "Microsoft Certified: Fabric Analytics Engineer Associate",
            "issuer": "Microsoft",
            "primary": True,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/fabric-analytics-engineer-associate/",
        },
        {
            "code": "DP-900",
            "name": "Microsoft Certified: Azure Data Fundamentals",
            "issuer": "Microsoft",
            "primary": False,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-data-fundamentals/",
        },
        {
            "code": "AZ-900",
            "name": "Microsoft Certified: Azure Fundamentals",
            "issuer": "Microsoft",
            "primary": False,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/",
        },
        {
            "code": "AI-900",
            "name": "Microsoft Certified: Azure AI Fundamentals",
            "issuer": "Microsoft",
            "primary": False,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/",
        },
    ],
    "employment": [
        {
            "company": "Apexon",
            "division": "Enterprise Analytics Division",
            "title": "Senior Data Analyst",
            "dates": "Apr 2026–Present",
            "current": True,
            "location": "Remote (Enterprise Client Engagements)",
        },
        {
            "company": "Accenture",
            "division": "Enterprise Analytics & Sustainability Practice",
            "title": "Power BI Developer",
            "dates": "February 2022 – April 2026",
            "current": False,
            "location": "Hyderabad, India",
        },
        {
            "company": "Genpact",
            "division": "Financial Risk & Compliance Analytics",
            "title": "Data Risk Analyst",
            "dates": "April 2021 – January 2022",
            "current": False,
            "location": "Noida, India",
        },
        {
            "company": "Conduent",
            "division": "Analytics & Business Operations",
            "title": "Data Analyst",
            "dates": "June 2018 – April 2021",
            "current": False,
            "location": "Visakhapatnam, India",
        },
    ],
}

PORTFOLIO_ASSETS = {
    "primary_pdf": "Sai_Lakshmi_Elusuri_CV.pdf",
    "web_pages": [
        "index.html",
        "resume.html",
        "404.html",
    ],
    "static_files": [
        "shared.css",
        "og-cover.png",
        "robots.txt",
        "sitemap.xml",
    ],
}


def validate_synchronization(base_dir: str) -> bool:
    """
    Validates that core canonical facts are faithfully propagated across public
    web pages and CV sources, and that no private leaks remain.
    """
    target_files = ["index.html", "resume.html"]
    forbidden_public_strings = [
        "+91 8142674401",
        "+918142674401",
        "job-finder.html",
        "FACTS_TO_CONFIRM.md",
        "dutch-career-hub.html",
        "Netherlands_Career_Hub_Sai_Lakshmi.zip",
    ]

    for rel_path in target_files:
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            raise ValueError(f"Missing required public file: {rel_path}")
        with open(full_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        content = html.unescape(raw_content)

        if CANDIDATE["ind_endorsement"] not in content:
            raise ValueError(f"Missing IND endorsement in {rel_path}")

        if CANDIDATE["target_title"] not in content:
            raise ValueError(f"Missing unified title '{CANDIDATE['target_title']}' in {rel_path}")

        for emp in CANDIDATE["employment"]:
            if emp["company"] not in content:
                raise ValueError(f"Missing employer {emp['company']} in {rel_path}")

        if "Apr 2026–Present" not in content and "Apr 2026 - Present" not in content:
            raise ValueError(f"Missing Apexon current dates 'Apr 2026–Present' in {rel_path}")

        for leak in forbidden_public_strings:
            if leak in content:
                raise ValueError(f"Forbidden private/legacy trace '{leak}' found in {rel_path}")

    return True
