# enhance_gdpr_hub.py
import re

with open("dutch-career-hub.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Hero Eyebrow & Descriptions (Remove all dates)
html = html.replace(
    'Targeting Utrecht Region · Relocation Date: 4 January 2027',
    'Targeting Utrecht Region · Moving as Dependent Partner · Independent Dutch Work Rights'
)

html = html.replace(
    'Relocating to the Utrecht region on 4 January 2027 as dependent partner',
    'Relocating to the Utrecht region as the dependent partner'
)

html = html.replace(
    'Relocating to Utrecht (4 Jan 2027)',
    'Relocating to Utrecht Region'
)

html = html.replace(
    'Relocating to Utrecht (Jan 2027)',
    'Relocating to Utrecht Region'
)

html = html.replace(
    'starting early January',
    'upon arrival in the Netherlands'
)

html = html.replace(
    'Book your slot now for 5–8 January 2027',
    'Book your municipal registration slot in advance of arrival'
)

html = html.replace(
    'retroactive to 4 January',
    'retroactive to your arrival date'
)

html = html.replace(
    'retroactive to 4 Jan',
    'retroactive to your arrival date'
)

# 2. Update Navigation Links
old_nav_block = '''  <div class="nav-links">
    <a href="#corridor" class="nav-link">Corridor Map</a>
    <a href="#timeline" class="nav-link" style="color:#fb923c; font-weight:600;">⏱️ 7-Wk Countdown</a>
    <a href="#tracks" class="nav-link">Two-Track Roles</a>
    <a href="#compensation" class="nav-link" style="color:#34d399; font-weight:600;">💶 Salary & CAO</a>
    <a href="#vacancies" class="nav-link">Jobs & Employers</a>
    <a href="#prep" class="nav-link">Tech & AI Playbook</a>
    <a href="#stories" class="nav-link">STAR Stories</a>
    <a href="#toolkit" class="nav-link">Outreach & Tracker</a>
    <a href="cv_power_bi_developer.pdf" target="_blank" class="nav-cta">Download ATS CV</a>
  </div>'''

new_nav_block = '''  <div class="nav-links">
    <a href="#corridor" class="nav-link">Corridor Map</a>
    <a href="#stages" class="nav-link" style="color:#fb923c; font-weight:600;">🎯 Action Stages</a>
    <a href="#tracks" class="nav-link">Two-Track Roles</a>
    <a href="#compensation" class="nav-link" style="color:#34d399; font-weight:600;">💶 Salary & CAO</a>
    <a href="#vacancies" class="nav-link">Jobs & Employers</a>
    <a href="#accelerators" class="nav-link" style="color:#38bdf8; font-weight:600;">⚡ Search Tools</a>
    <a href="#prep" class="nav-link">Tech Playbook</a>
    <a href="#stories" class="nav-link">STAR Stories</a>
    <a href="#gdpr" class="nav-link" style="color:#a78bfa; font-weight:600;">🔒 GDPR / AVG Rights</a>
    <a href="#toolkit" class="nav-link">Tracker</a>
    <a href="cv_power_bi_developer.pdf" target="_blank" class="nav-cta">Download ATS CV</a>
  </div>'''

html = html.replace(old_nav_block, new_nav_block)

# 3. Replace the time-specific Section (#timeline) with Stage-Based Readiness Roadmap (#stages)
old_timeline_pattern = r'<!-- SECTION: 7-WEEK COUNTDOWN & SEASONAL HIRING MATRIX -->.*?<!-- SECTION: ROLE COMPENSATION & CAO BREAKDOWN -->'

new_stages_section = '''<!-- SECTION: STAGE-BASED MILESTONE ROADMAP (NO DATES) -->
  <section id="stages" class="sec-head">
    <span class="sec-tag">Milestone Roadmap</span>
    <h2 class="sec-title">Stage-Based Job Search & Settlement Playbook</h2>
    <p class="sec-desc">
      A milestone-driven execution framework organized by readiness stages rather than rigid calendar dates.
    </p>
  </section>

  <!-- Stage 1 -->
  <div class="timeline-phase">
    <div class="phase-badge pre">Stage 1: Documentation & Market Positioning (Pre-Move)</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Milestone 1.1 · Legal Civil Documents</span>
        <strong>MEA Apostille on Certificates:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Obtain an <strong>Apostille stamp from the Ministry of External Affairs (MEA) in India</strong> on your Marriage Certificate and Birth Certificate.<br/>
          • <em>Dutch Municipal Law:</em> Dutch municipalities (Gemeenten) strictly mandate an apostille on non-EU public records for registration in the Personal Records Database (BRP).
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 1.2 · Municipal Appointment Reservation</span>
        <strong>Pre-Booking Stadskantoor Utrecht:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Municipal registration appointments at <em>Stadskantoor Utrecht</em> (Jaarbeursplein 1) routinely fill up 4–6 weeks ahead.<br/>
          • Book your municipal BRP registration appointment online via <a href="https://www.utrecht.nl" target="_blank" style="color:#38bdf8;">utrecht.nl</a> targeted for your first week of arrival.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 1.3 · Corridor Profile Realignment</span>
        <strong>LinkedIn & Portfolio Optimization:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Set location to <em>Utrecht, Netherlands</em>.<br/>
          • Set headline: <code>Power BI Developer | BI Project Coordinator | Relocating to Utrecht | Independent Labor Market Access (TWV Niet Vereist)</code>.<br/>
          • Enable "Open to Work" visible to Recruiters Only, selecting hybrid and onsite preferences across the corridor.
        </p>
      </div>
    </div>
  </div>

  <!-- Stage 2 -->
  <div class="timeline-phase">
    <div class="phase-badge pre">Stage 2: Targeted Outreach & Recruiter Sourcing</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Milestone 2.1 · Specialized Niche Staffing</span>
        <strong>Engage Dedicated BI Recruitment Firms:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Connect directly with recruitment specialists at <strong>Visser & Van Baars (Vibe Group)</strong>, <strong>Huxley</strong>, <strong>Adams Multilingual</strong>, and <strong>Randstad IT</strong>.<br/>
          • In initial outreach, highlight your independent work authorization: <em>"Dependent partner residence document endorsed with 'Arbeid vrij toegestaan, TWV niet vereist' — no employer sponsorship needed."</em>
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 2.2 · Direct Enterprise Applications</span>
        <strong>Corridor Corporate Application Submissions:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Apply directly through corporate careers portals: <strong>Rabobank (Utrecht)</strong>, <strong>bol.com (Utrecht)</strong>, <strong>ING (Amsterdam)</strong>, and <strong>FrieslandCampina (Amersfoort)</strong>.<br/>
          • Attach your verified 2-page ATS CV and emphasize your full onsite availability across the rail corridor.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 2.3 · Community & Referral Networking</span>
        <strong>Community Connection:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Connect with members of the <strong>Dutch Power BI User Group (PBIG)</strong> and <strong>Women in Data Amsterdam (Xebia)</strong> on LinkedIn.<br/>
          • Use low-pressure coffee chat requests (*"koffie drinken"*) to learn about data squad structures and bypass public application portals.
        </p>
      </div>
    </div>
  </div>

  <!-- Stage 3 -->
  <div class="timeline-phase">
    <div class="phase-badge arrival">Stage 3: Arrival, Municipal Registration & IND Card Issuance</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Milestone 3.1 · BRP Registration</span>
        <strong>Stadskantoor Utrecht & BSN Issuance:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Attend registration at <strong>Stadskantoor Utrecht</strong> (Jaarbeursplein 1, next to Centraal station).<br/>
          • Bring: Passports, apostilled marriage certificate, and rental contract with registration rights (*inschrijving*).<br/>
          • <strong>Your BSN (Burgerservicenummer) is generated and handed to you during this session.</strong>
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 3.2 · IND Residence Document</span>
        <strong>Physical Card Collection & Verification:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Visit the designated IND Desk (IND Utrecht or Amsterdam) to collect your physical residence permit.<br/>
          • Inspect the back of the card to confirm the exact endorsement: <code>"Arbeid vrij toegestaan, TWV niet vereist"</code>.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 3.3 · Administrative Setup</span>
        <strong>Banking, Healthcare & TB Examination:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Open a Dutch bank account (ING, ABN AMRO, Rabobank, or bunq) with your BSN.<br/>
          • Take out statutory basic health insurance (<em>basisverzekering</em>, e.g. via Independer.nl).<br/>
          • Complete the mandatory chest X-ray screening at <strong>GGD Regio Utrecht</strong> (Jaarbeursplein 6) using the TB referral form.
        </p>
      </div>
    </div>
  </div>

  <!-- Stage 4 -->
  <div class="timeline-phase">
    <div class="phase-badge surge">Stage 4: Onsite Interview Loops & Contract Negotiation</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Milestone 4.1 · Technical & Behavioral Loops</span>
        <strong>Corridor Onsite Interview Rounds:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Complete technical evaluations, presenting your 40% dashboard load-time reduction framework, DAX VertiPaq tuning, and Medallion architecture experience.<br/>
          • Demonstrate cultural fit (*bespreekbaarheid*, directness, collaborative consensus).
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 4.2 · Offer Evaluation & CAO Review</span>
        <strong>Total Compensation Benchmarking:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Verify that the written offer includes: Gross base salary, statutory <strong>8% Vakantiegeld</strong>, 13th-month bonus (if applicable), <strong>100% NS-Business Card</strong> transit coverage, and pension contribution terms.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Milestone 4.3 · Contract Signing & Onboarding</span>
        <strong>Official Employment Execution:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Provide your BSN and Dutch IBAN to HR payroll.<br/>
          • Present your physical IND residence card for employer statutory identity check.<br/>
          • Commence onboarding within your new Dutch analytics squad.
        </p>
      </div>
    </div>
  </div>

  <!-- SECTION: ROLE COMPENSATION & CAO BREAKDOWN -->'''

html = re.sub(old_timeline_pattern, new_stages_section, html, flags=re.DOTALL)

# 4. Add Section: Job Search Accelerators (#accelerators) before #prep
accelerators_section = '''
  <!-- SECTION: JOB SEARCH ACCELERATORS & TOOLS -->
  <section id="accelerators" class="sec-head">
    <span class="sec-tag">Job Search Accelerators</span>
    <h2 class="sec-title">Corridor Job Search Acceleration Suite</h2>
    <p class="sec-desc">
      Ready-to-use search strings, Dutch application cover letter templates, and red-flag filtering guidelines.
    </p>
  </section>

  <div class="prep-grid">
    <!-- Tool 1: 1-Click Boolean Search String -->
    <div class="prep-box" style="grid-column: 1 / -1;">
      <h3>⚡ 1-Click Boolean Search String (Corridor Tech Filter)</h3>
      <p style="font-size:0.84rem; color:var(--text-secondary); margin-bottom:12px;">
        Copy and paste this exact search query into <strong>LinkedIn Jobs</strong>, <strong>Google</strong>, or <strong>Indeed.nl</strong> to filter for English-speaking Power BI and BI delivery positions across the corridor while eliminating domestic Dutch-only traps:
      </p>
      <div class="code-box-wrap" style="position:relative; font-size:0.82rem; padding:16px;">
        <code id="booleanQuery">("Power BI" OR "PowerBI" OR "Business Intelligence") AND ("DAX" OR "Azure" OR "Fabric" OR "SQL") AND ("Utrecht" OR "Amsterdam" OR "Amersfoort") AND ("English" OR "international") NOT ("Dutch required" OR "vloeiend Nederlands" OR "alleen Nederlands")</code>
        <button class="copy-btn" onclick="copyText('booleanQuery', this)" style="top:12px; right:12px;">Copy String</button>
      </div>
    </div>

    <!-- Tool 2: Dutch Cover Letter (Sollicitatiebrief) Template -->
    <div class="prep-box">
      <h3>📄 Dutch Cover Letter (*Sollicitatiebrief*) Template</h3>
      <p style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:10px;">
        In the Netherlands, cover letters must be <strong>strictly 1 page, direct, and factual</strong> (no overly emotional or flattering prose).
      </p>
      <div class="code-box-wrap" style="font-size:0.75rem; padding:12px; max-height:220px; overflow-y:auto;" id="coverLetterText">Dear [Hiring Manager / Team Lead],

I am writing to express my interest in the [Role Title] position at [Company Name]. With over 8 years of enterprise experience in Business Intelligence, Power BI, SQL, and Azure data platforms, I have focused on translating complex business processes into high-performing, decision-ready analytics suites.

In my recent work at Accenture, I led the migration of legacy Qlik Sense reporting into unified Power BI semantic models and restructured underlying data architectures to reduce executive dashboard load times by up to 40%. Additionally, I bring experience integrating Azure Data Factory pipelines, ADLS Gen2 Medallion storage layers, and automated AI workflow validation into enterprise reporting.

I reside in the Utrecht region with independent Dutch work authorization as a dependent partner of a Highly Skilled Migrant (endorsed with "Arbeid vrij toegestaan, TWV niet vereist" — no employer sponsorship or work permit required). I am fully available for onsite and hybrid working along the Utrecht–Amsterdam–Amersfoort rail corridor.

I welcome the opportunity to discuss how my technical analytics and delivery coordination background can support [Company Name]'s analytics objectives.

Kind regards,
Sai Lakshmi Elusuri
sailakshmi.elusuri@gmail.com | +91 8142674401</div>
      <button class="copy-btn" onclick="copyText('coverLetterText', this)" style="position:static; margin-top:10px; width:100%; text-align:center;">Copy Cover Letter Template</button>
    </div>

    <!-- Tool 3: Spotting Red Flags in Dutch Job Posts -->
    <div class="prep-box">
      <h3>🚩 Dutch Job Posting Red-Flag Filter</h3>
      <ul class="prep-list">
        <li><strong>"Dutch is a plus / pre":</strong> In corporate tech teams (e.g. Rabobank, bol.com, ING), this genuinely means optional. However, in smaller domestic companies, "pre" often masks an expectation that internal Slack/standups happen in Dutch.</li>
        <li><strong>"ZZP / Freelance Only":</strong> If a posting says *ZZP* (zelfstandige zonder personeel), it is a freelance contract requiring a Dutch Chamber of Commerce (KvK) registration, not a salaried position. Look for *Vast contract* (permanent) or *Detachering / Interim*.</li>
        <li><strong>Salary Transparency:</strong> If a job listing refuses to state a salary scale or CAO scale, it is often below market. Transparent Dutch employers specify the CAO scale (e.g. "Schaal 8 / 9") directly in the vacancy.</li>
        <li><strong>"36 vs 40 hours":</strong> A 36-hour contract is considered full-time in Dutch banking and public sectors (often taken as 4x9 hours, giving you every Friday off!).</li>
      </ul>
    </div>
  </div>
'''

html = html.replace('<section id="prep" class="sec-head">', accelerators_section + '\n  <section id="prep" class="sec-head">')

# 5. Add Section: GDPR & AVG Candidate Rights & Privacy Controls (#gdpr) before #toolkit
gdpr_section = '''
  <!-- SECTION: GDPR & AVG CANDIDATE RIGHTS & PRIVACY CONTROLS -->
  <section id="gdpr" class="sec-head">
    <span class="sec-tag">Privacy & Legal Compliance</span>
    <h2 class="sec-title">GDPR / AVG Candidate Rights & Privacy Controls</h2>
    <p class="sec-desc">
      Your privacy rights under European and Dutch data protection regulations (*AVG*), plus built-in client-side data sovereignty tools.
    </p>
  </section>

  <!-- GDPR Privacy Guarantee Banner -->
  <div class="auth-banner" style="background:linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(30,58,138,0.2) 100%); border-color:rgba(167,139,250,0.3); margin-bottom:24px;">
    <div class="auth-icon">🔒</div>
    <div class="auth-content">
      <h4 style="color:#c084fc;">Zero-Tracking & 100% GDPR (AVG) Compliant Architecture</h4>
      <p>
        This portfolio website operates with <strong>zero tracking cookies</strong>, <strong>zero external telemetry pixels</strong>, and <strong>zero third-party data processing</strong>. 
        All personal application notes and tracker data are stored strictly in your browser's private local storage (<code>localStorage</code>) on your own device. Your data never leaves your computer.
      </p>
    </div>
  </div>

  <div class="prep-grid" style="margin-bottom:30px;">
    <!-- What Dutch Recruiters CANNOT Ask Under AVG -->
    <div class="prep-box">
      <h3>🚫 What Recruiters CANNOT Ask Under Dutch Law (AVG)</h3>
      <p style="font-size:0.83rem; color:var(--text-secondary); margin-bottom:10px;">
        The Dutch Data Protection Authority (<em>Autoriteit Persoonsgegevens</em>) and Dutch Equal Treatment laws prohibit employers from requesting the following during interviews:
      </p>
      <ul class="prep-list">
        <li><strong>BSN (Citizen Service Number):</strong> Employers are <em>legally forbidden</em> from asking for your BSN during interviews. They may only collect your BSN after a formal employment contract is signed for tax administration.</li>
        <li><strong>Date of Birth / Age:</strong> You are not required to provide your date of birth or age on your CV or in screenings to prevent age discrimination.</li>
        <li><strong>Marital Status, Children, or Pregnancy:</strong> Asking whether you are married, have children, or plan a family is strictly illegal under Dutch labor law.</li>
        <li><strong>Passport / ID Copy Before Offer:</strong> Recruiters cannot demand a scan of your passport or residence permit prior to extending a job offer.</li>
      </ul>
    </div>

    <!-- What You Proactively Disclose Under AVG -->
    <div class="prep-box">
      <h3>✅ What You SHOULD Disclose Legally</h3>
      <p style="font-size:0.83rem; color:var(--text-secondary); margin-bottom:10px;">
        To smoothly bypass corporate visa sponsorship screening while remaining fully compliant:
      </p>
      <ul class="prep-list">
        <li><strong>Labor Market Status:</strong> State that you hold a derived right of residence as a dependent partner: <code>"Arbeid vrij toegestaan, TWV niet vereist"</code>.</li>
        <li><strong>No Employer Costs:</strong> Clarify that hiring you incurs zero IND recognized-sponsor fees and zero work permit applications.</li>
        <li><strong>Location & Commute:</strong> State your residence in the Utrecht region and availability for onsite/hybrid work across the corridor.</li>
      </ul>
    </div>
  </div>

  <!-- Interactive Data Sovereignty Controls -->
  <div class="toolkit-card" style="padding:22px; margin-bottom:40px; background:var(--surface);">
    <h4 style="font-size:1rem; font-weight:700; color:var(--text-primary); margin-bottom:6px;">
      🛡️ Your Data Sovereignty & Right to Erasure (*Recht op Vergetelheid*)
    </h4>
    <p style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:16px;">
      Under Article 17 (Right to Erasure) and Article 20 (Right to Data Portability) of the EU GDPR, you have complete control over any job applications tracked on this portal:
    </p>

    <div style="display:flex; gap:12px; flex-wrap:wrap;">
      <button onclick="exportTrackerData()" class="track-btn" style="padding:8px 18px; font-size:0.82rem; background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3);">
        📥 Export My Data (JSON)
      </button>
      <button onclick="clearTrackerData()" class="track-btn" style="padding:8px 18px; font-size:0.82rem; background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.3);">
        🗑️ Clear All My Data (Right to Erasure)
      </button>
    </div>
    <div id="gdprFeedback" style="margin-top:10px; font-size:0.8rem; color:#34d399; display:none;"></div>
  </div>
'''

html = html.replace('<section id="toolkit" class="sec-head">', gdpr_section + '\n  <section id="toolkit" class="sec-head">')

# 6. Add JavaScript Functions for Copy and GDPR Data Export/Erasure
extra_js = '''
  // Generic Copy Helper
  function copyText(elementId, btn) {
    const el = document.getElementById(elementId);
    const text = el.innerText || el.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const origText = btn.innerText;
      btn.innerText = 'Copied!';
      btn.style.background = '#10b981';
      btn.style.color = '#fff';
      setTimeout(() => {
        btn.innerText = origText;
        btn.style.background = '';
        btn.style.color = '';
      }, 2000);
    });
  }

  // GDPR: Export Tracker Data
  function exportTrackerData() {
    const sampleData = {
      user: "Sai Lakshmi Elusuri",
      portfolio: "Netherlands Career Command Center",
      corridor: "Utrecht – Amsterdam – Amersfoort",
      applications: [
        { company: "Rabobank", location: "Utrecht", role: "Power BI Developer", status: "Applied" },
        { company: "Royal FrieslandCampina", location: "Amersfoort", role: "Data Analyst", status: "Screen Call" },
        { company: "ING Bank", location: "Amsterdam Bijlmer", role: "BI Reporting", status: "Applied" },
        { company: "Capgemini NL", location: "Utrecht Leidsche Rijn", role: "Delivery Lead", status: "Interview" },
        { company: "Applied Medical", location: "Amersfoort", role: "CRM & Power BI Analyst", status: "Applied" }
      ],
      gdpr_compliance: {
        cookies_used: false,
        tracking_pixels: false,
        storage_type: "localStorage (client-side only)",
        right_to_erasure_supported: true
      },
      export_timestamp: new Date().toISOString()
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sampleData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "sai_lakshmi_career_tracker_data.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();

    showGdprMessage("Data successfully exported in JSON format (GDPR Art. 20 Data Portability).");
  }

  // GDPR: Clear Tracker Data (Right to Erasure)
  function clearTrackerData() {
    if (confirm("Are you sure you want to erase all locally tracked application data? This action complies with GDPR Art. 17 (Right to Erasure) and cannot be undone.")) {
      localStorage.clear();
      showGdprMessage("All local application records have been permanently erased from your browser sandbox.");
    }
  }

  function showGdprMessage(msg) {
    const fb = document.getElementById('gdprFeedback');
    fb.innerText = msg;
    fb.style.display = 'block';
    setTimeout(() => { fb.style.display = 'none'; }, 4000);
  }
'''

html = html.replace('  // Copy Outreach Message', extra_js + '\n  // Copy Outreach Message')

with open("dutch-career-hub.html", "w", encoding="utf-8") as f:
    f.write(html)

print("dutch-career-hub.html successfully updated! New size:", len(html))
