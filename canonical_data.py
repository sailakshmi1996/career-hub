"""
canonical_data.py
Single Canonical Source of Truth for Sai Lakshmi Elusuri's Portfolio, CVs, and Career Assets.
All CVs, PDFs, and website content derive their core facts from this module.
"""

import os
import re

CANDIDATE = {
    "name": "Sai Lakshmi Elusuri",
    "target_title_pbi": "Senior Power BI Developer & Lakehouse Analytics Specialist",
    "target_title_delivery": "Analytics Delivery Lead & BI Programme Manager",
    "location": "Utrecht region, Netherlands",
    "email": "sailakshmi.elusuri@gmail.com",
    "phone": "+91 8142674401",
    "phone_display": "+91 8142674401 (Direct / WhatsApp)",
    "linkedin_url": "https://www.linkedin.com/in/sailakshmielusuri-data-analyst/",
    "linkedin_display": "linkedin.com/in/sailakshmielusuri-data-analyst",
    "github_url": "https://github.com/sailakshmi1996/career-hub",
    "portfolio_url": "https://sailakshmi1996.github.io/career-hub/",
    "experience_years": "8+",
    "work_auth_status": "Unrestricted Dutch labor market access",
    "ind_endorsement": "Arbeid vrij toegestaan, TWV niet vereist",
    "work_auth_summary": (
        "Based in the Utrecht region, Netherlands. Full unrestricted labor market access under "
        "official IND endorsement: 'Arbeid vrij toegestaan, TWV niet vereist' (no employer "
        "sponsorship or work permit / TWV required; available for immediate Dutch employment contract start)."
    ),
    "education": {
        "degree": "Bachelor of Technology (B.Tech.) in Computer Science & Engineering",
        "institution": "Raghu Engineering College",
        "location": "Visakhapatnam, India",
        "year": "2017"
    },
    "languages": [
        {"name": "English", "proficiency": "Professional working proficiency (C1)"},
        {"name": "Dutch", "proficiency": "Elementary (A1, actively learning; committed to Dutch language integration)"},
        {"name": "Telugu", "proficiency": "Native proficiency"},
        {"name": "Hindi", "proficiency": "Conversational working proficiency"}
    ],
    "certifications": [
        {
            "code": "PL-300",
            "name": "Microsoft Certified: Power BI Data Analyst Associate",
            "issuer": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/"
        },
        {
            "code": "DP-600",
            "name": "Microsoft Certified: Fabric Analytics Engineer Associate",
            "issuer": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/fabric-analytics-engineer-associate/"
        },
        {
            "code": "DP-900",
            "name": "Microsoft Certified: Azure Data Fundamentals",
            "issuer": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-data-fundamentals/"
        },
        {
            "code": "AZ-900",
            "name": "Microsoft Certified: Azure Fundamentals",
            "issuer": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/"
        },
        {
            "code": "AI-900",
            "name": "Microsoft Certified: Azure AI Fundamentals",
            "issuer": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/"
        }
    ],
    "employment": [
        {
            "company": "Apexon",
            "division": "Enterprise Analytics Division",
            "title": "Senior Data Analyst",
            "dates": "Apr 2026–Present",
            "current": True,
            "location": "Remote / Enterprise Client Engagements"
        },
        {
            "company": "Accenture",
            "division": "Enterprise Analytics & Sustainability Practice",
            "title": "Power BI Developer",
            "dates": "February 2022 – April 2026",
            "current": False,
            "location": "Hyderabad, India"
        },
        {
            "company": "Genpact",
            "division": "Financial Risk & Compliance Analytics",
            "title": "Data Risk Analyst",
            "dates": "April 2021 – January 2022",
            "current": False,
            "location": "Noida, India"
        },
        {
            "company": "Conduent",
            "division": "Analytics & Business Operations",
            "title": "Data Analyst",
            "dates": "June 2018 – April 2021",
            "current": False,
            "location": "Visakhapatnam, India"
        }
    ]
}

# Verified Key Performance Metrics (Single Source of Truth)
KEY_METRICS = {
    "dashboard_load_reduction": "40%",
    "data_refresh_latency_cut": "45%",
    "licensing_cost_saved": "€350K+",
    "monthly_export_hours_saved": "30+",
    "staging_query_speedup": "35%",
    "weekly_active_adoption_gain": "40%",
    "conduent_monthly_hours_saved": "60+",
    "sla_compliance_elevation": "91% to 98%",
    "mortgage_reconciliation": "100%",
    "experience_years": "8+",
    "certifications_count": "5"
}

# Hub Asset Definitions
PORTFOLIO_ASSETS = {
    "pdfs": [
        "cv_power_bi_developer.pdf",
        "cv_bi_project_delivery.pdf",
        "Sai_Lakshmi_Elusuri_Resume.pdf"
    ],
    "html_cvs": [
        "cv_power_bi_developer.html",
        "cv_bi_project_delivery.html",
        "resume.html"
    ],
    "markdown_cvs": [
        "cv_power_bi_developer.md",
        "cv_bi_project_delivery.md"
    ],
    "hub_pages": [
        "index.html",
        "dutch-career-hub.html",
        "job-finder.html",
        "linkedin-optimizer.html",
        "strategy.html",
        "influencer-insights.html"
    ],
    "zip_bundle": "Netherlands_Career_Hub_Sai_Lakshmi.zip"
}


def validate_synchronization(base_dir: str) -> bool:
    """
    Validates that core canonical facts are faithfully propagated across key artifacts.
    Returns True if synchronized, raises ValueError with details if discrepancy found.
    """
    target_files = [
        "index.html",
        "cv_power_bi_developer.html",
        "cv_bi_project_delivery.html",
        "resume.html"
    ]
    for rel_path in target_files:
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check IND endorsement
        if CANDIDATE["ind_endorsement"] not in content:
            raise ValueError(f"Missing IND endorsement in {rel_path}")

        # Check employer presence
        for emp in CANDIDATE["employment"]:
            if emp["company"] not in content:
                raise ValueError(f"Missing employer {emp['company']} in {rel_path}")

        # Check Apexon current role dates
        if "Apr 2026–Present" not in content and "Apr 2026 - Present" not in content:
            raise ValueError(f"Missing Apexon current dates 'Apr 2026–Present' in {rel_path}")

    return True
