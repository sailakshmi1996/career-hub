// app.js - Single Page Application logic for SynapseArchitect

document.addEventListener('DOMContentLoaded', () => {
  // Load data from global scope
  const data = window.SYNAPSE_DATA;
  if (!data) {
    console.error("Knowledge base data not found!");
    return;
  }

  // State Management
  let activeTab = 'walkthroughs';
  let activeArchitectureId = data.architectures[0].id;
  let selectedNodeId = null;
  let useCaseCategoryFilter = 'All';
  let useCaseSearchQuery = '';

  // DOM Elements - Navigation
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.view-section');
  const explorerLink = document.getElementById('explore-architectures-btn');

  // Navigation Event Listeners
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = link.getAttribute('data-view');
      switchView(targetView);
    });
  });

  if (explorerLink) {
    explorerLink.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('walkthroughs');
    });
  }

  function switchView(viewName) {
    activeTab = viewName;
    
    // Update active nav links
    navLinks.forEach(link => {
      if (link.getAttribute('data-view') === viewName) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Toggle active sections
    sections.forEach(section => {
      if (section.id === `${viewName}-section`) {
        section.classList.add('active');
      } else {
        section.classList.remove('active');
      }
    });

    // Run view-specific setups
    if (viewName === 'walkthroughs') {
      renderArchitecturesSidebar();
      renderArchitectureDiagram(activeArchitectureId);
    } else if (viewName === 'components') {
      renderComponentsGrid();
    } else if (viewName === 'calculator') {
      setupCostCalculator();
    } else if (viewName === 'cases') {
      renderCasesAndStories();
    } else if (viewName === 'roadmap') {
      renderFabricRoadmap();
    }

    // Scroll to top of view container
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /* -------------------------------------------------------------
     VIEW 1: ARCHITECTURAL WALKTHROUGHS & INTERACTIVE DIAGRAMS
     ------------------------------------------------------------- */
  function renderArchitecturesSidebar() {
    const sidebarMenu = document.getElementById('architectures-menu');
    if (!sidebarMenu) return;

    sidebarMenu.innerHTML = '';
    data.architectures.forEach(arch => {
      const button = document.createElement('button');
      button.className = `sidebar-btn ${arch.id === activeArchitectureId ? 'active' : ''}`;
      button.setAttribute('data-id', arch.id);
      button.innerHTML = `
        <span>${arch.name}</span>
        <span class="arrow">→</span>
      `;

      button.addEventListener('click', () => {
        // Update active selection
        document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        activeArchitectureId = arch.id;
        selectedNodeId = null;
        renderArchitectureDiagram(arch.id);
      });

      sidebarMenu.appendChild(button);
    });
  }

  function renderArchitectureDiagram(archId) {
    const arch = data.architectures.find(a => a.id === archId);
    const diagramTitle = document.getElementById('diagram-title');
    const diagramDesc = document.getElementById('diagram-desc');
    const canvas = document.getElementById('diagram-canvas');
    const detailsDrawer = document.getElementById('node-details');
    const stepsContainer = document.getElementById('steps-list');

    if (!arch || !canvas) return;

    // Set Header
    diagramTitle.textContent = arch.name;
    diagramDesc.textContent = arch.description;

    // Clear and Render Canvas Elements
    canvas.innerHTML = '';
    selectedNodeId = null;
    detailsDrawer.style.display = 'none';

    arch.diagram.forEach((node, idx) => {
      // Create Node
      const nodeEl = document.createElement('div');
      nodeEl.className = 'diagram-node';
      nodeEl.setAttribute('data-id', node.id);
      nodeEl.setAttribute('data-type', node.type);
      nodeEl.innerHTML = `
        <span class="node-type">${node.type}</span>
        <span class="node-label">${node.label}</span>
      `;

      nodeEl.addEventListener('click', () => {
        // Toggle selection
        document.querySelectorAll('.diagram-node').forEach(n => n.classList.remove('selected'));
        
        if (selectedNodeId === node.id) {
          selectedNodeId = null;
          detailsDrawer.style.display = 'none';
        } else {
          selectedNodeId = node.id;
          nodeEl.classList.add('selected');
          showNodeDetails(node);
        }
      });

      canvas.appendChild(nodeEl);

      // Add Connector if not last element
      if (idx < arch.diagram.length - 1) {
        const connector = document.createElement('div');
        connector.className = 'diagram-connector';
        canvas.appendChild(connector);
      }
    });

    // Render step by step workflow list
    if (stepsContainer) {
      stepsContainer.innerHTML = '';
      arch.flow.forEach(flowStep => {
        const stepNum = flowStep.split('.')[0];
        const stepText = flowStep.substring(flowStep.indexOf('.') + 1).trim();

        const stepEl = document.createElement('div');
        stepEl.className = 'step-item';
        stepEl.innerHTML = `
          <span class="step-num">${stepNum}</span>
          <span class="step-text">${stepText}</span>
        `;
        stepsContainer.appendChild(stepEl);
      });
    }
  }

  function showNodeDetails(node) {
    const detailsDrawer = document.getElementById('node-details');
    const detailsTitle = document.getElementById('details-title');
    const detailsBadge = document.getElementById('details-badge');
    const detailsDesc = document.getElementById('details-description');

    if (!detailsDrawer || !node) return;

    detailsDrawer.style.display = 'block';
    detailsTitle.textContent = node.label;
    detailsBadge.textContent = node.type;
    detailsBadge.className = 'node-details-badge';
    detailsDesc.textContent = node.desc;

    // Apply color styling to badge
    let badgeBg = '#333';
    let badgeColor = '#fff';
    switch (node.type) {
      case 'source': badgeBg = 'rgba(245, 158, 11, 0.15)'; badgeColor = '#f59e0b'; break;
      case 'process': badgeBg = 'rgba(0, 242, 254, 0.15)'; badgeColor = 'var(--color-primary)'; break;
      case 'storage': badgeBg = 'rgba(16, 185, 129, 0.15)'; badgeColor = '#10b981'; break;
      case 'compute': badgeBg = 'rgba(99, 102, 241, 0.15)'; badgeColor = '#6366f1'; break;
      case 'client': badgeBg = 'rgba(236, 72, 153, 0.15)'; badgeColor = '#ec4899'; break;
      case 'network': badgeBg = 'rgba(0, 202, 227, 0.15)'; badgeColor = '#00cae3'; break;
      case 'governance': badgeBg = 'rgba(167, 139, 250, 0.15)'; badgeColor = '#a78bfa'; break;
    }
    detailsBadge.style.backgroundColor = badgeBg;
    detailsBadge.style.color = badgeColor;
  }

  /* -------------------------------------------------------------
     VIEW 2: CORE COMPONENT DIRECTORY
     ------------------------------------------------------------- */
  function renderComponentsGrid() {
    const componentsGrid = document.getElementById('components-grid');
    if (!componentsGrid) return;

    componentsGrid.innerHTML = '';
    data.components.forEach(comp => {
      const card = document.createElement('div');
      card.className = 'component-card';

      // SVG Icon map
      let iconSvg = '';
      if (comp.icon === 'database') {
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-2.239 10-5V7c0-2.761-4.477-5-10-5S2 4.239 2 7v10c0 2.761 4.477 5 10 5z"></path><path d="M2 7c0 2.761 4.477 5 10 5s10-2.239 10-5"></path><path d="M2 12c0 2.761 4.477 5 10 5s10-2.239 10-5"></path></svg>`;
      } else if (comp.icon === 'cloud') {
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>`;
      } else if (comp.icon === 'terminal') {
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>`;
      } else {
        iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"></path><path d="M8 3H3v5"></path><path d="M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18z"></path></svg>`;
      }

      const listItems = comp.bestPractices.map(item => `<li>${item}</li>`).join('');

      card.innerHTML = `
        <div class="component-icon">${iconSvg}</div>
        <h3>${comp.name}</h3>
        <p>${comp.details}</p>
        <h4>Implementation Best Practices</h4>
        <ul>${listItems}</ul>
      `;
      componentsGrid.appendChild(card);
    });
  }

  /* -------------------------------------------------------------
     VIEW 3: COST ESTIMATOR CALCULATOR
     ------------------------------------------------------------- */
  let calculatorConfigured = false;

  function setupCostCalculator() {
    if (calculatorConfigured) {
      calculateCosts(); // Re-evaluate cost calculations on tab switch
      return;
    }

    // Inputs
    const sqlModelSwitch = document.getElementById('calc-sql-model');
    const dwuSlider = document.getElementById('calc-dwu-tier');
    const runningHoursSlider = document.getElementById('calc-running-hours');
    const serverlessScannedSlider = document.getElementById('calc-serverless-scanned');
    const sparkHoursSlider = document.getElementById('calc-spark-hours');
    const storageSlider = document.getElementById('calc-storage');
    const pipelinesSlider = document.getElementById('calc-pipelines');
    const reservedSelect = document.getElementById('calc-reserved-discount');

    // Section containers to hide/show based on SQL Model Switch
    const dedicatedDwuRow = document.getElementById('dedicated-dwu-row');
    const dedicatedHoursRow = document.getElementById('dedicated-hours-row');
    const serverlessScannedRow = document.getElementById('serverless-scanned-row');
    const reservedContainer = document.getElementById('reserved-discount-container');

    // Dynamic Display values
    const dwuValueLabel = document.getElementById('calc-dwu-value');
    const runningHoursLabel = document.getElementById('calc-hours-value');
    const serverlessScannedLabel = document.getElementById('calc-serverless-value');
    const sparkHoursLabel = document.getElementById('calc-spark-value');
    const storageLabel = document.getElementById('calc-storage-value');
    const pipelinesLabel = document.getElementById('calc-pipelines-value');

    // Change listeners for Display labels update
    sqlModelSwitch.addEventListener('change', () => {
      const isDedicated = sqlModelSwitch.checked;
      if (isDedicated) {
        dedicatedDwuRow.style.display = 'block';
        dedicatedHoursRow.style.display = 'block';
        reservedContainer.style.display = 'flex';
        serverlessScannedRow.style.display = 'none';
      } else {
        dedicatedDwuRow.style.display = 'none';
        dedicatedHoursRow.style.display = 'none';
        reservedContainer.style.display = 'none';
        serverlessScannedRow.style.display = 'block';
      }
      calculateCosts();
    });

    dwuSlider.addEventListener('input', () => {
      const tierIndex = dwuSlider.value;
      const tier = data.pricingTiers[tierIndex];
      dwuValueLabel.textContent = `${tier.tier} (${tier.computeNodes} Compute Node${tier.computeNodes > 1 ? 's' : ''})`;
      calculateCosts();
    });

    runningHoursSlider.addEventListener('input', () => {
      runningHoursLabel.textContent = `${runningHoursSlider.value} Hours/Day`;
      calculateCosts();
    });

    serverlessScannedSlider.addEventListener('input', () => {
      serverlessScannedLabel.textContent = `${serverlessScannedSlider.value} TB/Month`;
      calculateCosts();
    });

    sparkHoursSlider.addEventListener('input', () => {
      sparkHoursLabel.textContent = `${sparkHoursSlider.value} vCore-Hours`;
      calculateCosts();
    });

    storageSlider.addEventListener('input', () => {
      storageLabel.textContent = `${storageSlider.value} TB`;
      calculateCosts();
    });

    pipelinesSlider.addEventListener('input', () => {
      pipelinesLabel.textContent = `${pipelinesSlider.value} Activity Runs`;
      calculateCosts();
    });

    reservedSelect.addEventListener('change', calculateCosts);

    // Initial label set
    const initialTier = data.pricingTiers[dwuSlider.value];
    dwuValueLabel.textContent = `${initialTier.tier} (${initialTier.computeNodes} Compute Node${initialTier.computeNodes > 1 ? 's' : ''})`;
    runningHoursLabel.textContent = `${runningHoursSlider.value} Hours/Day`;
    serverlessScannedLabel.textContent = `${serverlessScannedSlider.value} TB/Month`;
    sparkHoursLabel.textContent = `${sparkHoursSlider.value} vCore-Hours`;
    storageLabel.textContent = `${storageSlider.value} TB`;
    pipelinesLabel.textContent = `${pipelinesSlider.value} Activity Runs`;

    calculatorConfigured = true;
    calculateCosts();
  }

  function calculateCosts() {
    const sqlModelSwitch = document.getElementById('calc-sql-model');
    const dwuSlider = document.getElementById('calc-dwu-tier');
    const runningHoursSlider = document.getElementById('calc-running-hours');
    const serverlessScannedSlider = document.getElementById('calc-serverless-scanned');
    const sparkHoursSlider = document.getElementById('calc-spark-hours');
    const storageSlider = document.getElementById('calc-storage');
    const pipelinesSlider = document.getElementById('calc-pipelines');
    const reservedSelect = document.getElementById('calc-reserved-discount');

    // Summary Display Elements
    const breakDwuVal = document.getElementById('break-dwu-val');
    const breakDwuLabel = document.getElementById('break-dwu-lbl');
    const breakSparkVal = document.getElementById('break-spark-val');
    const breakStorageVal = document.getElementById('break-storage-val');
    const breakPipelinesVal = document.getElementById('break-pipelines-val');
    const totalPriceLabel = document.getElementById('calc-monthly-total');

    let sqlMonthlyCost = 0;
    const isDedicated = sqlModelSwitch.checked;

    if (isDedicated) {
      const tierIndex = dwuSlider.value;
      const tier = data.pricingTiers[tierIndex];
      const ratePerHour = tier.costPerHour;
      const hoursPerMonth = runningHoursSlider.value * 30;
      let cost = ratePerHour * hoursPerMonth;

      // Apply Reserved Capacity Discounts
      const discountType = reservedSelect.value;
      if (discountType === '1year') {
        cost = cost * (1 - 0.37); // 37% Off
      } else if (discountType === '3year') {
        cost = cost * (1 - 0.65); // 65% Off
      }

      sqlMonthlyCost = cost;
      breakDwuLabel.textContent = `SQL Compute (${tier.tier})`;
    } else {
      const tbScanned = serverlessScannedSlider.value;
      sqlMonthlyCost = tbScanned * 5.00; // $5.00 per TB scanned
      breakDwuLabel.textContent = "SQL Serverless Query";
    }

    // Spark vCore costs: ~$0.06 per vCore-hour
    const sparkMonthlyCost = sparkHoursSlider.value * 0.06;

    // ADLS Storage costs: ~$18.00 per TB
    const storageMonthlyCost = storageSlider.value * 18.00;

    // Pipelines activity runs: $1.00 per 1000 runs
    const pipelinesMonthlyCost = (pipelinesSlider.value / 1000) * 1.00;

    // Sum Total
    const totalCost = sqlMonthlyCost + sparkMonthlyCost + storageMonthlyCost + pipelinesMonthlyCost;

    // Format and Update DOM
    breakDwuVal.textContent = `$${sqlMonthlyCost.toFixed(2)}`;
    breakSparkVal.textContent = `$${sparkMonthlyCost.toFixed(2)}`;
    breakStorageVal.textContent = `$${storageMonthlyCost.toFixed(2)}`;
    breakPipelinesVal.textContent = `$${pipelinesMonthlyCost.toFixed(2)}`;
    
    totalPriceLabel.textContent = `$${totalCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  /* -------------------------------------------------------------
     VIEW 4: INDUSTRY USE CASES & SUCCESS STORIES
     ------------------------------------------------------------- */
  const categoryFilters = document.querySelectorAll('.tag-filter');
  const searchInput = document.getElementById('cases-search');

  categoryFilters.forEach(tag => {
    tag.addEventListener('click', () => {
      categoryFilters.forEach(t => t.classList.remove('active'));
      tag.classList.add('active');
      useCaseCategoryFilter = tag.getAttribute('data-cat');
      renderCasesAndStories();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      useCaseSearchQuery = e.target.value.toLowerCase().trim();
      renderCasesAndStories();
    });
  }

  function renderCasesAndStories() {
    const storiesGrid = document.getElementById('stories-grid');
    const casesGrid = document.getElementById('use-cases-grid');

    if (!storiesGrid || !casesGrid) return;

    // 1. Render Success Stories (ABN AMRO, T-Mobile)
    storiesGrid.innerHTML = '';
    data.successStories.forEach(story => {
      const card = document.createElement('div');
      card.className = 'story-card';
      card.innerHTML = `
        <div class="story-header">
          <div class="company-logo-badge">${story.logoText}</div>
          <span class="company-name">${story.company}</span>
        </div>
        <div class="story-block">
          <div class="story-subtitle">The Challenge</div>
          <div class="story-content">${story.challenge}</div>
        </div>
        <div class="story-block">
          <div class="story-subtitle">The Integration</div>
          <div class="story-content">${story.solution}</div>
        </div>
        <div class="story-result-box">
          <p>🎯 Result: ${story.result}</p>
        </div>
      `;
      storiesGrid.appendChild(card);
    });

    // 2. Render Use Cases with filters & search
    casesGrid.innerHTML = '';
    
    const filteredCases = data.useCases.filter(c => {
      const matchesCategory = (useCaseCategoryFilter === 'All' || c.category === useCaseCategoryFilter);
      const matchesSearch = (
        c.title.toLowerCase().includes(useCaseSearchQuery) ||
        c.challenge.toLowerCase().includes(useCaseSearchQuery) ||
        c.solution.toLowerCase().includes(useCaseSearchQuery) ||
        c.impact.toLowerCase().includes(useCaseSearchQuery)
      );
      return matchesCategory && matchesSearch;
    });

    if (filteredCases.length === 0) {
      casesGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-dim);">
          No use cases found matching your criteria.
        </div>
      `;
      return;
    }

    filteredCases.forEach(c => {
      const card = document.createElement('div');
      card.className = 'use-case-card';
      card.innerHTML = `
        <span class="use-case-badge">${c.category}</span>
        <h3>${c.title}</h3>
        <div class="case-detail">
          <div class="case-label">Business Challenge</div>
          <div class="case-text">${c.challenge}</div>
        </div>
        <div class="case-detail">
          <div class="case-label">Architecture Solution</div>
          <div class="case-text">${c.solution}</div>
        </div>
        <div class="case-detail">
          <div class="case-label">Estimated Impact</div>
          <div class="case-text" style="color: var(--color-primary); font-weight: 600;">${c.impact}</div>
        </div>
      `;
      casesGrid.appendChild(card);
    });
  }

  /* -------------------------------------------------------------
     VIEW 5: MICROSOFT FABRIC MIGRATION ROADMAP
     ------------------------------------------------------------- */
  function renderFabricRoadmap() {
    const roadmapContainer = document.getElementById('fabric-roadmap');
    if (!roadmapContainer) return;

    roadmapContainer.innerHTML = '';
    data.fabricChecklist.forEach(step => {
      const item = document.createElement('div');
      item.className = 'roadmap-item';
      item.innerHTML = `
        <div class="roadmap-marker"></div>
        <div class="roadmap-card">
          <div class="roadmap-step-num">Step 0${step.id}</div>
          <h3>${step.title}</h3>
          <p>${step.desc}</p>
        </div>
      `;
      roadmapContainer.appendChild(item);
    });
  }

  // Initialize View on First Load
  switchView('walkthroughs');
});
