# Sai Lakshmi Elusuri — Portfolio & Netherlands Career Command Center

[![CI/CD Pipeline](https://github.com/sailakshmi1996/career-hub/actions/workflows/ci-cd-netlify.yml/badge.svg)](https://github.com/sailakshmi1996/career-hub/actions/workflows/ci-cd-netlify.yml)
[![Live Site](https://img.shields.io/badge/Live%20Site-sailakshminl.netlify.app-blue)](https://sailakshminl.netlify.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Executive Power BI Developer & Lakehouse Analytics Specialist**  
> Utrecht Region, Netherlands · Full unrestricted IND Dutch labor market authorization (*"Arbeid vrij toegestaan, TWV niet vereist"*)

---

## 📄 Candidate CVs & Resumes

| Document | Focus | Format | Direct File |
| :--- | :--- | :---: | :--- |
| **Master Resume** | Full Technical & Delivery Leadership | PDF / HTML | [`Sai_Lakshmi_Elusuri_Resume.pdf`](./Sai_Lakshmi_Elusuri_Resume.pdf) · [`resume.html`](./resume.html) |
| **Power BI Developer CV** | DAX, VertiPaq, Fabric Lakehouse, Semantic Modeling | PDF / HTML | [`cv_power_bi_developer.pdf`](./cv_power_bi_developer.pdf) · [`cv_power_bi_developer.html`](./cv_power_bi_developer.html) |
| **BI Delivery Lead CV** | Agile Delivery, Qlik-to-Power BI Migrations, Governance | PDF / HTML | [`cv_bi_project_delivery.pdf`](./cv_bi_project_delivery.pdf) · [`cv_bi_project_delivery.html`](./cv_bi_project_delivery.html) |
| **Career Bundle** | Complete Recruiter ZIP Archive | ZIP | [`Netherlands_Career_Hub_Sai_Lakshmi.zip`](./Netherlands_Career_Hub_Sai_Lakshmi.zip) |

---

## 🏆 Microsoft Certifications

* **PL-300:** Microsoft Certified: Power BI Data Analyst Associate
* **DP-600:** Microsoft Certified: Fabric Analytics Engineer Associate
* **DP-900:** Microsoft Certified: Azure Data Fundamentals
* **AZ-900:** Microsoft Certified: Azure Fundamentals
* **AI-900:** Microsoft Certified: Azure AI Fundamentals

---

## 🛠️ Build & Test Automation

The repository includes an automated build pipeline that compiles PDFs from semantic HTML sources using headless Chrome, embeds metadata via PyMuPDF, runs automated integrity and compliance tests, and packages production assets for Netlify.

### 1. Run Automated Test Suite
```bash
python3 tests/run_all_tests.py
```
*Validates 156 test cases spanning internal anchor integrity, date consistency, and GDPR/AVG privacy constraints.*

### 2. Compile Resumes & Assemble Distribution
```bash
python3 build.py
```
*Outputs compiled 2-page candidate PDFs, validates test suite, and builds the `dist/` directory with `_redirects` and `_headers`.*

---

## 🌐 Live Portfolio & Contact

* **Live Portfolio Website:** [https://sailakshminl.netlify.app/](https://sailakshminl.netlify.app/)
* **LinkedIn:** [https://www.linkedin.com/in/sailakshmielusuri-data-analyst/](https://www.linkedin.com/in/sailakshmielusuri-data-analyst/)
* **Email:** sailakshmi.elusuri@gmail.com
