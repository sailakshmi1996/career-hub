# update_hub.py
import re

with open("dutch-career-hub.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Navigation
old_nav = '''  <div class="nav-links">
    <a href="#corridor" class="nav-link">Corridor Map</a>
    <a href="#tracks" class="nav-link">Two-Track Roles</a>
    <a href="#vacancies" class="nav-link">Jobs & Employers</a>
    <a href="#prep" class="nav-link">Prep Playbook</a>
    <a href="#stories" class="nav-link">STAR Stories</a>
    <a href="#toolkit" class="nav-link">Outreach & Tracker</a>
    <a href="cv_power_bi_developer.pdf" target="_blank" class="nav-cta">Download ATS CV</a>
  </div>'''

new_nav = '''  <div class="nav-links">
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

html = html.replace(old_nav, new_nav)

# 2. Add Extra CSS Styles before </style>
extra_css = '''
    /* ── Timeline & Seasonality Styles ── */
    .timeline-phase {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 26px 28px;
      margin-bottom: 24px;
      position: relative;
    }
    .phase-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: var(--radius-full);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }
    .phase-badge.pre { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .phase-badge.arrival { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .phase-badge.surge { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    .milestone-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }
    .milestone-box {
      background: var(--surface2);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: var(--radius-md);
      padding: 16px 18px;
      font-size: 0.85rem;
      line-height: 1.5;
    }
    .milestone-box strong { color: var(--text-primary); }
    .milestone-date {
      font-size: 0.76rem;
      font-weight: 700;
      color: #38bdf8;
      text-transform: uppercase;
      margin-bottom: 6px;
      display: block;
    }

    /* ── Compensation Table & Cards ── */
    .comp-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }
    .comp-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 22px;
    }
    .comp-val {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.7rem;
      font-weight: 800;
      color: #34d399;
      margin-bottom: 4px;
    }
    .comp-lbl {
      font-size: 0.78rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }
    .comp-breakdown {
      font-size: 0.82rem;
      color: #cbd5e1;
      line-height: 1.55;
    }
    .comp-breakdown li {
      margin-bottom: 6px;
      list-style-type: disc;
      margin-left: 18px;
    }

    /* ── Code Comparison & Architecture Boxes ── */
    .code-comparison-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }
    .code-box-wrap {
      background: #090e17;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: var(--radius-md);
      padding: 16px;
      font-family: 'Fira Code', monospace;
      font-size: 0.8rem;
      color: #e2e8f0;
      line-height: 1.5;
      overflow-x: auto;
    }
    .code-tag-slow {
      display: inline-block;
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .code-tag-fast {
      display: inline-block;
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    /* ── Address & Transit Chips ── */
    .address-chip {
      font-size: 0.74rem;
      color: #94a3b8;
      background: rgba(15, 23, 42, 0.7);
      padding: 3px 8px;
      border-radius: 4px;
      margin-top: 4px;
      display: inline-block;
    }
  </style>'''

html = html.replace('  </style>', extra_css)

# 3. Enhance Corridor Station Cards with Exact Addresses & Directions
old_corridor = '''    <div class="corridor-grid">
      <!-- Utrecht Station -->
      <div class="station-card">
        <div class="station-badge">Home Base Hub</div>
        <h3 class="station-title">Utrecht Centraal</h3>
        <div class="station-time">0 min · Central Intercity Junction</div>
        <ul class="station-employers">
          <li><strong>Rabobank:</strong> Global HQ (Croeselaan, 2 min walk)</li>
          <li><strong>bol.com:</strong> Tech & Retail HQ (Papendorp)</li>
          <li><strong>VodafoneZiggo:</strong> Central Office (Hoog Catharijne)</li>
          <li><strong>Capgemini NL:</strong> Tech Campus (Leidsche Rijn)</li>
          <li><strong>SC Johnson:</strong> Regional Center (Mijdrecht/Utrecht)</li>
        </ul>
      </div>

      <!-- Amsterdam Hub -->
      <div class="station-card">
        <div class="station-badge">Financial & Tech Hub</div>
        <h3 class="station-title">Amsterdam (Zuid & Bijlmer)</h3>
        <div class="station-time">15–22 min direct NS Intercity</div>
        <ul class="station-employers">
          <li><strong>ING Bank:</strong> Cedar HQ (Bijlmer ArenA – 15 min train)</li>
          <li><strong>ABN AMRO:</strong> Global HQ (Zuidas – 22 min train)</li>
          <li><strong>Booking.com:</strong> Global Tech Campus (Centraal)</li>
          <li><strong>Adyen & FinTechs:</strong> Central Amsterdam & Rokin</li>
          <li><strong>Uber / Tech Scaleups:</strong> Amsterdam South axis</li>
        </ul>
      </div>

      <!-- Amersfoort Hub -->
      <div class="station-card">
        <div class="station-badge">Enterprise & FMCG Hub</div>
        <h3 class="station-title">Amersfoort Centraal</h3>
        <div class="station-time">14 min direct NS Intercity</div>
        <ul class="station-employers">
          <li><strong>Royal FrieslandCampina:</strong> Global HQ (Stationsplein)</li>
          <li><strong>Applied Medical:</strong> European HQ (Wiekenweg)</li>
          <li><strong>Royal HaskoningDHV:</strong> Global HQ (Laan 1914)</li>
          <li><strong>Yokogawa Europe:</strong> Regional HQ (Euroweg)</li>
          <li><strong>VolkerWessels:</strong> Corporate Infrastructure HQ</li>
        </ul>
      </div>
    </div>'''

new_corridor = '''    <div class="corridor-grid">
      <!-- Utrecht Station -->
      <div class="station-card">
        <div class="station-badge">Home Base Hub</div>
        <h3 class="station-title">Utrecht Centraal</h3>
        <div class="station-time">0 min · Main Intercity Hub (Every 10–15 min)</div>
        <ul class="station-employers">
          <li>
            <div><strong>Rabobank Global HQ:</strong> Croeselaan 18</div>
            <div class="address-chip">🚶 2 min walk from Jaarbeurs exit · 100% English Data Tribe</div>
          </li>
          <li>
            <div><strong>bol.com Campus:</strong> Papendorpseweg 100</div>
            <div class="address-chip">🚌 12 min via Bus 24/295 from Centraal · Agile Commercial Analytics</div>
          </li>
          <li>
            <div><strong>VodafoneZiggo Central Office:</strong> Spoorstraat 3</div>
            <div class="address-chip">🚶 Direct indoor connection to station hall · Tech & Data Squads</div>
          </li>
          <li>
            <div><strong>Capgemini NL Campus:</strong> Reykjavikplein 1</div>
            <div class="address-chip">🚆 4 min Sprinter to Utrecht Leidsche Rijn · Insights & Data Practice</div>
          </li>
          <li>
            <div><strong>SC Johnson:</strong> Groot Mijdrechtstraat 81</div>
            <div class="address-chip">🚗 Regional FMCG Center · Fluent English Supply Chain BI</div>
          </li>
        </ul>
      </div>

      <!-- Amsterdam Hub -->
      <div class="station-card">
        <div class="station-badge">Financial & Tech Hub</div>
        <h3 class="station-title">Amsterdam (Zuid & Bijlmer)</h3>
        <div class="station-time">15–22 min direct NS Intercity</div>
        <ul class="station-employers">
          <li>
            <div><strong>ING Bank Cedar HQ:</strong> Bijlmerdreef 106</div>
            <div class="address-chip">🚆 15 min IC to Amsterdam Bijlmer ArenA + 3 min walk · Central Data Office</div>
          </li>
          <li>
            <div><strong>ABN AMRO Global HQ:</strong> Gustav Mahlerlaan 10</div>
            <div class="address-chip">🚆 22 min IC to Amsterdam Zuid (Zuidas) · Enterprise Tabular Models</div>
          </li>
          <li>
            <div><strong>Booking.com Tech Campus:</strong> Oosterdokseiland 1</div>
            <div class="address-chip">🚆 26 min IC to Amsterdam Centraal · Global Analytics Infrastructure</div>
          </li>
          <li>
            <div><strong>Adyen & FinTechs:</strong> Simon Carmiggeltstraat 6</div>
            <div class="address-chip">🚆 25 min IC to Centraal / Rokin · Global Payments Analytics</div>
          </li>
          <li>
            <div><strong>Uber EMEA HQ:</strong> Mr. Treublaan 7</div>
            <div class="address-chip">🚆 18 min IC to Amsterdam Amstel · Operations BI & Pricing Data</div>
          </li>
        </ul>
      </div>

      <!-- Amersfoort Hub -->
      <div class="station-card">
        <div class="station-badge">Enterprise & FMCG Hub</div>
        <h3 class="station-title">Amersfoort Centraal</h3>
        <div class="station-time">14 min direct NS Intercity (Every 15 min)</div>
        <ul class="station-employers">
          <li>
            <div><strong>Royal FrieslandCampina HQ:</strong> Stationsplein 4</div>
            <div class="address-chip">🚶 Literally 60 seconds across station plaza! · Global People Analytics</div>
          </li>
          <li>
            <div><strong>Applied Medical European HQ:</strong> Wiekenweg 21</div>
            <div class="address-chip">🚲 7 min bike / bus from Centraal · European CRM & Power BI</div>
          </li>
          <li>
            <div><strong>Royal HaskoningDHV HQ:</strong> Laan 1914 no. 35</div>
            <div class="address-chip">🚌 8 min bus from Centraal · Asset Management BI Consulting</div>
          </li>
          <li>
            <div><strong>Yokogawa Europe Regional HQ:</strong> Euroweg 2</div>
            <div class="address-chip">🚆 Industrial IoT & Process Control Analytics</div>
          </li>
          <li>
            <div><strong>VolkerWessels HQ:</strong> Podium 9, Amersfoort</div>
            <div class="address-chip">🚆 Infrastructure Data Products & Executive Reporting</div>
          </li>
        </ul>
      </div>
    </div>'''

html = html.replace(old_corridor, new_corridor)

# 4. Insert Section: 7-Week Countdown & Dutch Seasonal Hiring Matrix (before #tracks)
timeline_section = '''
  <!-- SECTION: 7-WEEK COUNTDOWN & SEASONAL HIRING MATRIX -->
  <section id="timeline" class="sec-head">
    <span class="sec-tag">Time & Seasonality</span>
    <h2 class="sec-title">7-Week Countdown & Dutch Hiring Calendar</h2>
    <p class="sec-desc">
      Detailed weekly execution roadmap from mid-November 2026 to arrival on 4 January 2027 and through your first month in Utrecht.
    </p>
  </section>

  <!-- Pre-Arrival Phase -->
  <div class="timeline-phase">
    <div class="phase-badge pre">Phase 1: Pre-Arrival Strategy (Mid-Nov to 3 Jan 2027)</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Weeks 1–2 · 13 Nov – 27 Nov 2026</span>
        <strong>Apostille & Municipal Booking Window:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Submit Marriage Certificate & Birth Certificate for <strong>MEA Apostille stamp in India</strong> (takes 7–12 business days). <em>Gemeente Utrecht strictly requires an apostille for BRP registration!</em><br/>
          • <strong>Book Gemeente Utrecht appointment:</strong> Municipal registration slots at <em>Stadskantoor Utrecht</em> (Jaarbeursplein 1) open 4–6 weeks ahead. Book your slot now for 5–8 January 2027.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Weeks 3–4 · 28 Nov – 11 Dec 2026</span>
        <strong>Agency Sprint & Early Screening:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Connect directly with specialized BI recruiters at <strong>Visser & Van Baars (Vibe Group)</strong>, <strong>Huxley</strong>, <strong>Adams Multilingual</strong>, and <strong>Randstad IT</strong>.<br/>
          • Conduct initial screening calls, clarifying your dependent status (<code>Arbeid vrij toegestaan, TWV niet vereist</code>) and full onsite availability along the corridor starting early January.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Weeks 5–6 · 12 Dec 2026 – 3 Jan 2027</span>
        <strong>Dutch Holiday Lull (*Kerstvakantie*):</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • <strong>Market Reality:</strong> Dutch corporate offices operate on skeleton staff from 19 Dec to 4 Jan. Hiring decisions pause.<br/>
          • <strong>Preparation Action:</strong> Practice DAX VertiPaq tuning and STAR stories; assemble the physical relocation document binder (Apostilled certificates, passports, MVV approvals, rental contract with <em>inschrijving</em> rights).
        </p>
      </div>
    </div>
  </div>

  <!-- Arrival & Surge Phase -->
  <div class="timeline-phase">
    <div class="phase-badge arrival">Phase 2: Arrival Week & Formalities (4 Jan – 10 Jan 2027)</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Day 1 · 4 January 2027</span>
        <strong>Arrival in the Netherlands:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          Arrive with husband in Utrecht; check into accommodation. Purchase personal anonymous/initial OV-chipkaart at Utrecht Centraal station for local transit.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Days 2–4 · 5–8 January 2027</span>
        <strong>Gemeente Utrecht & BSN Issuance:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          Attend appointment at <strong>Stadskantoor Utrecht</strong> (Jaarbeursplein 1, 3521 CA Utrecht). Present apostilled marriage certificate, passports, and tenancy agreement. <strong>Your BSN (Burgerservicenummer) is issued on the spot.</strong>
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Days 5–6 · 8–10 January 2027</span>
        <strong>IND Desk & Residence Card Collection:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          Visit the IND Desk (IND Utrecht or Amsterdam) to collect your physical residence permit card. <strong>Verify the endorsement on the reverse:</strong> <code>"Arbeid vrij toegestaan, TWV niet vereist"</code>.
        </p>
      </div>
    </div>
  </div>

  <div class="timeline-phase">
    <div class="phase-badge surge">Phase 3: January Budget Unlock & Offer Signing (11 Jan – Feb 2027)</div>
    <div class="milestone-grid">
      <div class="milestone-box">
        <span class="milestone-date">Weeks 8–9 · 11 Jan – 24 Jan 2027</span>
        <strong>Dutch Q1 Corporate Hiring Surge:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Corporate hiring budgets unlock across Dutch banking and retail sectors.<br/>
          • Open Dutch bank account (ING, ABN AMRO, Rabobank, or bunq) with your BSN.<br/>
          • Activate Dutch health insurance (<em>basisverzekering</em>) retroactive to 4 Jan.<br/>
          • Book mandatory chest X-ray screening at <strong>GGD Regio Utrecht</strong> (Jaarbeursplein 6) using the TB referral form.
        </p>
      </div>

      <div class="milestone-box">
        <span class="milestone-date">Weeks 10–12 · 25 Jan – Mid-Feb 2027</span>
        <strong>Corridor Onsite Interview Loops & Contract:</strong>
        <p style="margin-top:6px; color:var(--text-secondary); font-size:0.82rem;">
          • Attend 2nd/3rd round onsite interviews in Utrecht, Amsterdam, and Amersfoort.<br/>
          • Negotiate package: Base salary + 8% <em>vakantiegeld</em> + NS-Business Card + pension scheme + 25+ vacation days.<br/>
          • Sign contract and commence onboarding.
        </p>
      </div>
    </div>
  </div>
'''

html = html.replace('<section id="tracks" class="sec-head">', timeline_section + '\n  <section id="tracks" class="sec-head">')

# 5. Insert Section: Dutch Compensation & CAO Breakdown (before #vacancies)
comp_section = '''
  <!-- SECTION: ROLE COMPENSATION & CAO BREAKDOWN -->
  <section id="compensation" class="sec-head">
    <span class="sec-tag">Salary & Benefits</span>
    <h2 class="sec-title">Dutch Compensation Architecture & CAO Benchmarks</h2>
    <p class="sec-desc">
      How compensation is structured in the Netherlands, including base salary, statutory holiday allowance (*vakantiegeld*), and collective agreements.
    </p>
  </section>

  <div class="comp-grid">
    <div class="comp-card">
      <div class="comp-val">€52K – €72K+</div>
      <div class="comp-lbl">Track 1: Power BI Developer Base</div>
      <ul class="comp-breakdown">
        <li><strong>Gross Monthly:</strong> €4,300 – €6,000 / month (based on 36–40 hr week).</li>
        <li><strong>+ 8% Vakantiegeld:</strong> €4,160 – €5,760 paid in May (statutory annual holiday allowance).</li>
        <li><strong>+ 13th Month / Bonus:</strong> ~€4,300 – €6,000 common in banking CAOs (Rabobank, ING, ABN AMRO).</li>
        <li><strong>Total Package:</strong> <strong>€60,000 – €83,000+</strong> gross annual compensation.</li>
      </ul>
    </div>

    <div class="comp-card">
      <div class="comp-val">€58K – €78K+</div>
      <div class="comp-lbl">Track 2: BI Project Coordinator Base</div>
      <ul class="comp-breakdown">
        <li><strong>Gross Monthly:</strong> €4,800 – €6,500 / month.</li>
        <li><strong>+ 8% Vakantiegeld:</strong> €4,640 – €6,240 paid in May.</li>
        <li><strong>+ 13th Month / Bonus:</strong> ~€4,800 – €6,500 in consultancies and enterprise logistics.</li>
        <li><strong>Total Package:</strong> <strong>€67,000 – €90,000+</strong> gross annual compensation.</li>
      </ul>
    </div>

    <div class="comp-card">
      <div class="comp-val">100% Covered</div>
      <div class="comp-lbl">Mandatory & Standard Benefits</div>
      <ul class="comp-breakdown">
        <li><strong>NS-Business Card:</strong> 100% employer-funded train, tram, bus travel across the Netherlands.</li>
        <li><strong>Vacation Allowance:</strong> 25 statutory days + 5–10 ADV/ATV extra time-off days under corporate CAO.</li>
        <li><strong>Employer Pension:</strong> 60–70% of industry pension contributions paid directly by employer.</li>
        <li><strong>Home-Office Budget:</strong> ~€2.35/day tax-free allowance + €500–€750 ergonomic setup budget.</li>
      </ul>
    </div>
  </div>
'''

html = html.replace('<section id="vacancies" class="sec-head">', comp_section + '\n  <section id="vacancies" class="sec-head">')

# 6. Enhance #prep with Technical Code Comparisons & Architectural Blueprints
old_prep_grid = '''  <div class="prep-grid">
    <!-- Step-by-Step 40% Speedup -->
    <div class="prep-box">
      <h3>⚡ How You Achieved 40% Speedup</h3>
      <ul class="prep-list">
        <li><strong>Step 1 (Diagnosis):</strong> Profiled visual load times using <strong>Performance Analyzer</strong> in Power BI. Exported queries into <strong>DAX Studio</strong> to inspect VertiPaq Storage Engine (SE) vs Formula Engine (FE) execution splits.</li>
        <li><strong>Step 2 (Data Model):</strong> Eliminated expensive snowflake relationships and bidirectional cross-filtering. Converted tables into a strict <strong>Star Schema</strong> with single-direction 1:many filters.</li>
        <li><strong>Step 3 (DAX Optimization):</strong> Replaced heavy row-level iterators (like <code>SUMX(FILTER(Table,...))</code>) with context-aware <code>CALCULATE()</code> and <code>KEEPFILTERS()</code>. Moved calculated columns into Power Query/SQL to maximize dictionary encoding.</li>
        <li><strong>Step 4 (Visual Tuning):</strong> Limited visuals to under 10 per tab; used bookmarks and drill-through pages instead of rendering high-cardinality charts concurrently.</li>
      </ul>
    </div>'''

new_prep_grid = '''  <div class="prep-grid">
    <!-- Step-by-Step 40% Speedup with Code Comparison -->
    <div class="prep-box" style="grid-column: 1 / -1;">
      <h3>⚡ How You Achieved 40% Speedup (VertiPaq Storage Engine Mechanics)</h3>
      <p style="font-size:0.86rem; color:var(--text-secondary); margin-bottom:14px; line-height:1.55;">
        In Dutch technical interviews, you will be asked: <em>"How exactly did you isolate and resolve the bottleneck?"</em> Explain that the VertiPaq engine operates two execution pathways: the <strong>Storage Engine (SE)</strong>, which is multi-threaded and blazing fast on compressed columns, and the <strong>Formula Engine (FE)</strong>, which is single-threaded and slow. Slow reports occur when complex iterators force VertiPaq to generate thousands of callbacks to the Formula Engine.
      </p>

      <div class="code-comparison-grid">
        <div class="code-box-wrap">
          <span class="code-tag-slow">❌ Slow DAX (Formula Engine Heavy — Callback Lag)</span>
<pre><code>// Inefficient row-by-row iteration forcing FE execution:
Delayed Sustainability Issues = 
SUMX(
    SustainabilityEvents,
    IF(
        SustainabilityEvents[ResolutionDate] &gt; SustainabilityEvents[TargetDate] 
        &amp;&amp; SustainabilityEvents[Severity] = "High",
        SustainabilityEvents[ImpactScore],
        0
    )
)</code></pre>
        </div>

        <div class="code-box-wrap">
          <span class="code-tag-fast">✔ Optimized DAX (Multi-threaded xmSQL Storage Engine)</span>
<pre><code>// Pushed directly to VertiPaq Storage Engine (40% Speedup):
Delayed Sustainability Issues = 
CALCULATE(
    SUM(SustainabilityEvents[ImpactScore]),
    KEEPFILTERS(SustainabilityEvents[ResolutionDate] &gt; SustainabilityEvents[TargetDate]),
    SustainabilityEvents[Severity] = "High"
)</code></pre>
        </div>
      </div>

      <div style="margin-top:14px; font-size:0.84rem; color:var(--text-secondary); line-height:1.5;">
        <strong>Storage Compression Optimization:</strong> Moved calculated columns into SQL views and Power Query (M), allowing VertiPaq to build optimal Run-Length Encoding (RLE) bit-packed dictionaries. Sorted the primary fact table by high-cardinality foreign keys prior to ingestion.
      </div>
    </div>'''

html = html.replace(old_prep_grid, new_prep_grid)

# 7. Add Qlik-to-Power BI Rosetta Stone & Agentic AI Workflow Box in #prep
old_ai_box = '''    <!-- AI & Automation -->
    <div class="prep-box">
      <h3>🤖 AI Automation & Process Mining</h3>
      <ul class="prep-list">
        <li><strong>Agentic AI Workflows:</strong> Leveraging autonomous agents to automate data reconciliation, query generation, and periodic report generation.</li>
        <li><strong>Prompt Engineering for Analytics:</strong> Designing structured system prompts to generate optimized DAX formulas, summarize dashboard anomaly spikes, and write automated executive commentary.</li>
        <li><strong>Celonis Process Mining Integration:</strong> Connecting event log telemetry with Power BI to visualize throughput friction, identify cycle-time bottlenecks, and measure process conformance.</li>
      </ul>
    </div>'''

new_ai_box = '''    <!-- Qlik to Power BI Rosetta Stone -->
    <div class="prep-box">
      <h3>🔄 Qlik-to-Power BI Migration Rosetta Stone</h3>
      <p style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:10px;">
        Accenture migration talking points: How you converted legacy Qlik Set Analysis into modern DAX:
      </p>
      <div class="code-box-wrap" style="font-size:0.75rem; padding:10px;">
        <span style="color:#fb923c; font-weight:700;">Qlik Set Analysis:</span><br/>
        <code>Sum({&lt;Year={$(=Max(Year))}, Status={'Active'}&gt;} Revenue)</code><br/><br/>
        <span style="color:#34d399; font-weight:700;">Power BI DAX Equivalent:</span><br/>
        <code>CALCULATE(SUM(Sales[Revenue]), Sales[Status] = "Active", Sales[Year] = MAX(Sales[Year]))</code>
      </div>
      <ul class="prep-list" style="margin-top:10px;">
        <li>Rationalized 150+ duplicate legacy metrics into unified corporate semantic measures.</li>
        <li>Standardized color palettes and accessibility contrast ratios in Power BI Service.</li>
      </ul>
    </div>

    <!-- Agentic AI & Prompt Engineering Workflows -->
    <div class="prep-box">
      <h3>🤖 Agentic AI & Analytics Prompt Engineering</h3>
      <p style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:10px;">
        Showcase how you bridge Microsoft Fabric, Power BI, and generative AI agents:
      </p>
      <div class="code-box-wrap" style="font-size:0.73rem; padding:10px;">
        <span style="color:#38bdf8; font-weight:700;">Automated Data Reconciliation Agent (Python/Azure):</span><br/>
        <code># Autonomous Agent inspects Gold delta table schema integrity:
def verify_gold_health(delta_table):
    null_rate = delta_table.filter(col("KPI_Value").isNull()).count() / delta_table.count()
    if null_rate &gt; 0.01:
        trigger_alert("Data quality drop detected. Pausing Power BI refresh.")
    else:
        invoke_power_bi_rest_api_refresh(dataset_id)</code>
      </div>
      <ul class="prep-list" style="margin-top:10px;">
        <li><strong>AI Prompt Engineering:</strong> Crafted few-shot prompts to generate executive summaries of anomaly metric spikes directly inside Power BI Copilot.</li>
        <li><strong>Agentic Automation:</strong> Automated pipeline health checks, eliminating manual staging validation before executive morning briefings.</li>
      </ul>
    </div>'''

html = html.replace(old_ai_box, new_ai_box)

with open("dutch-career-hub.html", "w", encoding="utf-8") as f:
    f.write(html)

print("dutch-career-hub.html successfully enriched! New size:", len(html))
