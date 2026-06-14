const API = "http://localhost:8000";

// app state
let allPlants = [];
let selectedPlantId = null;
let currentLayout = null;
let currentTierConfigs = {}; // if this was TS, Record<number, string> (e.g. { 1: "leaf", 2: "original" })
let currentPockets = {}; // key: "tier-pocket", value: { plantId: number, quantity: number}, e.g. { "1-1": 3 }

async function init() {
  await loadPlants();
  await loadLayouts();
  setupEventListeners();
}

async function loadPlants() {
  const res = await fetch(`${API}/plants/`);
  allPlants = await res.json();

  renderPlantList(allPlants);
}

function renderPlantList(plants) {
  const el = document.getElementById("plant-list");
  el.innerHTML = "";

  const list = document.createElement("ul");
  list.className = "plant-list";
  list.setAttribute("aria-label", "List of Plants");

  plants.forEach((p) => {
    const li = document.createElement("li");
    const tooltipId = `tooltip-plant-${p.id}`;

    const card = document.createElement("button");
    card.type = "button";
    card.className = "plant-card";
    card.dataset.id = p.id;
    card.setAttribute("aria-describedby", tooltipId);
    card.innerHTML = `
            <div class="plant-card-name">${p.name}</div>
            <div class="plant-card-meta">
                <span class="badge">${p.type}</span>
                <span class="badge ${p.sunlight}">${p.sunlight} sun</span>
                <span class="badge ${p.water}">${p.water} water</span>
                ${p.days_to_harvest ? `<span class="badge">${p.days_to_harvest}d</span>` : ""}
            </div>
        `;

    const tooltipText = [
      p.notes,
      p.max_per_pocket ? `Max ${p.max_per_pocket} per pocket.` : "",
    ]
      .filter(Boolean)
      .join(" ");

    const hiddenTooltip = document.createElement("div");
    hiddenTooltip.id = tooltipId;
    hiddenTooltip.setAttribute("role", "tooltip");
    hiddenTooltip.className = "sr-only";
    hiddenTooltip.textContent = tooltipText;

    card.addEventListener("click", () => selectPlant(p.id));

    if (p.notes) {
      card.addEventListener("mouseenter", (e) => showTooltip(e, tooltipText));
      card.addEventListener("mousemove", (e) => moveTooltip(e));
      card.addEventListener("mouseleave", hideTooltip);
    }

    li.appendChild(card);
    li.appendChild(hiddenTooltip);
    list.appendChild(li);
  });

  el.appendChild(list);
}

function selectPlant(id) {
  selectedPlantId = selectedPlantId === id ? null : id;
  document.querySelectorAll(".plant-card").forEach((c) => {
    c.classList.toggle("selected", parseInt(c.dataset.id) === selectedPlantId);
  });
}

// ALL layouts
async function loadLayouts() {
  const res = await fetch(`${API}/layouts/`);
  const layouts = await res.json();
  const sel = document.getElementById("layout-select");
  sel.innerHTML = `<option value="">Select a layout</option>`;

  layouts.forEach((l) => {
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = `${l.name} (${l.tiers}-tier)`;
    sel.appendChild(opt);
  });
}

// single layout
async function loadLayout(id) {
  const res = await fetch(`${API}/layouts/${id}`);
  const data = await res.json();
  currentLayout = data.layout;
  currentTierConfigs = {};
  currentPockets = {};

  data.tier_configs.forEach((c) => {
    currentTierConfigs[c.tier] = c.tier_type;
  });

  data.pockets.forEach((p) => {
    if (p.plant_id) {
      currentPockets[`${p.tier}-${p.pocket}`] = {
        plantId: p.plant_id,
        quantity: p.quantity,
      };
    }
  });

  renderPlanter();
}

async function createLayout(name, tiers, color) {
  const body = { name, tiers };
  if (color) {
    body.color = color;
  }

  const res = await fetch(`${API}/layouts/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const layout = await res.json();
  await loadLayouts();
  document.getElementById("layout-select").value = layout.id;
  await loadLayout(layout.id);
}

function renderPlanter() {
  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("planter-wrap").classList.remove("hidden");
  document.getElementById("compat-result").classList.add("hidden");

  document.getElementById("layout-title").textContent = currentLayout.name;
  document.getElementById("tier-count-label").textContent =
    `${currentLayout.tiers} tiers · 6 pockets each`;

  const grid = document.getElementById("planter-grid");
  grid.innerHTML = "";

  for (let tier = 1; tier <= currentLayout.tiers; tier++) {
    const row = document.createElement("div");
    row.className = "tier-row";

    const tierInfo = document.createElement("div");
    tierInfo.className = "tier-info";

    const label = document.createElement("div");
    label.className = "tier-label";
    label.textContent = `Tier ${tier}`;

    const tierType = currentTierConfigs[tier] ?? "original";

    const toggle = document.createElement("button");
    toggle.className = `tier-toggle ${tierType}`;
    const tierTypeText = tierType === "original" ? "original" : "leaf";
    toggle.textContent = tierTypeText.toUpperCase();
    toggle.setAttribute("aria-pressed", tierType === "leaf");
    toggle.setAttribute(
      "aria-label",
      `Tier ${tier} type: ${tierType}. Click to switch tier to ${tierTypeText}.`,
    );

    toggle.addEventListener("click", () => handleTierToggle(tier, tierType));

    tierInfo.appendChild(label);
    tierInfo.appendChild(toggle);
    row.appendChild(tierInfo);

    const pockets = document.createElement("div");
    pockets.className = "tier-pockets";

    for (let pocket = 1; pocket <= 6; pocket++) {
      const key = `${tier}-${pocket}`;
      const { plantId, quantity } = currentPockets[key] ?? {};
      const plant = plantId ? allPlants.find((p) => p.id == plantId) : null;

      const el = document.createElement("div");
      el.className = `pocket${plant ? " filled" : ""}`;
      el.dataset.tier = tier;
      el.dataset.pocket = pocket;

      if (plant) {
        el.innerHTML = `
            <button class="pocket-clear" aria-label="Remove ${plant.name.toLowerCase()} from tier ${tier} pocket ${pocket}">x</button>
            <div class="pocket-name">${plant.name}</div>
            <div class="pocket-stepper">
                <button class="qty-btn" data-action="decrease" aria-label="Decrease ${plant.name.toLowerCase()} quantity" ${quantity <= 1 ? "disabled" : ""}>-</button>
                <span class="qty-value">${quantity}</span>
                <button class="qty-btn" data-action="increase" aria-label="Increase ${plant.name.toLowerCase()} quantity">+</button>
            </div>
        `;

        if (plant.max_per_pocket && quantity > plant.max_per_pocket) {
          el.classList.add("warning");
          el.title = `Best with max ${plant.max_per_pocket} per pocket`;
        }

        el.querySelector(".pocket-clear").addEventListener("click", (e) => {
          e.stopPropagation();
          handlePocketClear(tier, pocket);
        });

        el.querySelector('[data-action="decrease"]').addEventListener(
          "click",
          (e) => {
            e.stopPropagation();
            handleQuantityChange(tier, pocket, plantId, quantity - 1);
          },
        );

        el.querySelector('[data-action="increase"]').addEventListener(
          "click",
          (e) => {
            e.stopPropagation();
            handleQuantityChange(tier, pocket, plantId, quantity + 1);
          },
        );
      } else {
        el.textContent = "+";
      }

      el.addEventListener("click", () => handlePocketClick(tier, pocket));
      pockets.appendChild(el);
    }

    row.appendChild(pockets);
    grid.appendChild(row);
  }
}

async function handleTierToggle(tier, currentType) {
  const updatedType = currentType === "original" ? "leaf" : "original";

  const res = await fetch(`${API}/layouts/${currentLayout.id}/tiers`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tier, tier_type: updatedType }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail);
    return;
  }

  currentTierConfigs[tier] = updatedType;
  renderPlanter();
}

async function handlePocketClick(tier, pocket) {
  if (!currentLayout) return;
  if (!selectedPlantId) return; // if plant not selected and then pocket is clicked, do nothing

  const key = `${tier}-${pocket}`;
  const newPlantId = selectedPlantId;

  const res = await fetch(`${API}/layouts/${currentLayout.id}/pockets`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tier, pocket, plant_id: newPlantId, quantity: 1 }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail);
    return;
  }

  currentPockets[key] = { plantId: newPlantId, quantity: 1 };

  renderPlanter();
}

async function handlePocketClear(tier, pocket) {
  const key = `${tier}-${pocket}`;

  const res = await fetch(`${API}/layouts/${currentLayout.id}/pockets`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tier, pocket, plant_id: null, quantity: 1 }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail);
    return;
  }

  delete currentPockets[key];
  renderPlanter();
}

async function handleQuantityChange(tier, pocket, plantId, quantity) {
  const key = `${tier}-${pocket}`;

  const res = await fetch(`${API}/layouts/${currentLayout.id}/pockets`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tier, pocket, plant_id: plantId, quantity }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail);
    return;
  }

  currentPockets[key] = { plantId, quantity };
  renderPlanter();
}

async function checkCompatibility() {
  const plantIds = [
    ...new Set(Object.values(currentPockets).map(({ plantId }) => plantId)),
  ];

  if (plantIds.length < 2) {
    alert("Add at least 2 different plants to check compatibility.");
    return;
  }

  const res = await fetch(`${API}/layouts/check-compatibility`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plant_ids: plantIds }),
  });

  const result = await res.json();
  const body = document.getElementById("compat-body");
  body.innerHTML = "";

  if (result.warnings.length === 0 && result.suggestions.length === 0) {
    body.innerHTML = `<div class="compat-line">No issues found here! You're planter is ready to go!</div>`;
  }

  [...result.warnings, ...result.suggestions].forEach((msg) => {
    const line = document.createElement("div");
    line.className = "compat-line";
    line.textContent = msg;
    body.appendChild(line);
  });

  document.getElementById("compat-result").classList.remove("hidden");
  document
    .getElementById("compat-result")
    .scrollIntoView({ behavior: "smooth" });
}

async function clearAll() {
  if (!confirm("Clear all plant from this layout?")) return;

  for (const key of Object.keys(currentPockets)) {
    const [tier, pocket] = key.split("-").map(Number);
    await fetch(`${API}/layouts/${currentLayout.id}/pockets`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tier, pocket, plant_id: null, quantity: 1 }),
    });
  }

  currentPockets = {};
  renderPlanter();
}

function showTooltip(e, text) {
  const tip = document.getElementById("tooltip");
  tip.textContent = text;
  tip.classList.remove("hidden");
  moveTooltip(e);
}

function moveTooltip(e) {
  const tip = document.getElementById("tooltip");
  tip.style.left = `${e.clientX + 12}px`;
  tip.style.top = `${e.clientY + 12}px`;
}

function hideTooltip() {
  document.getElementById("tooltip").classList.add("hidden");
}

function setupEventListeners() {
  document.getElementById("layout-select").addEventListener("change", (e) => {
    if (e.target.value) {
      loadLayout(e.target.value);
    }
  });

  document.getElementById("new-layout-btn").addEventListener("click", () => {
    document.getElementById("modal-overlay").classList.remove("hidden");
    document.getElementById("modal-name").focus();
  });

  document.getElementById("modal-cancel").addEventListener("click", () => {
    document.getElementById("modal-overlay").classList.add("hidden");
  });

  document
    .getElementById("modal-create")
    .addEventListener("click", async () => {
      const name = document.getElementById("modal-name").value.trim();
      const tiers = parseInt(document.getElementById("modal-tiers").value);

      const color = document.getElementById("modal-color").value.trim();
      if (!name) {
        alert("Please enter a layout name.");
        return;
      }

      document.getElementById("modal-overlay").classList.add("hidden");
      document.getElementById("modal-name").value = "";
      document.getElementById("modal-color").value = "";

      await createLayout(name, tiers, color);
    });

  document
    .getElementById("check-compat-btn")
    .addEventListener("click", checkCompatibility);
  document.getElementById("clear-btn").addEventListener("click", clearAll);

  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".filter-btn")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const type = btn.dataset.type;
      const filtered =
        type === "all" ? allPlants : allPlants.filter((p) => p.type === type);
      renderPlantList(filtered);
    });
  });
}

init();
