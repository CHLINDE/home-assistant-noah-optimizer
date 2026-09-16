class NoahEnergyFlowCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  static getStubConfig() {
    return {
      title: "Current energy flow",
      entities: {},
    };
  }

  setConfig(config) {
    if (!config || !config.entities) {
      throw new Error("NOAH energy-flow card requires an entities object");
    }

    const required = [
      "grid_import",
      "grid_export",
      "solar_power",
      "output_power",
      "charging_power",
      "discharging_power",
      "soc",
      "home_load",
    ];

    for (const key of required) {
      if (!config.entities[key]) {
        throw new Error(`NOAH energy-flow card is missing entities.${key}`);
      }
    }

    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 5;
  }

  _numeric(entityId) {
    if (!this._hass || !entityId) return null;
    const state = this._hass.states[entityId];
    if (!state || ["unknown", "unavailable", ""].includes(state.state)) {
      return null;
    }
    const value = Number(state.state);
    if (!Number.isFinite(value)) return null;

    const unit = state.attributes?.unit_of_measurement;
    if (unit === "kW") return value * 1000;
    return value;
  }

  _soc(entityId) {
    const value = this._numeric(entityId);
    if (value === null) return null;
    return Math.max(0, Math.min(100, value));
  }

  _formatPower(value) {
    if (value === null) return "–";
    const absolute = Math.abs(value);
    if (absolute >= 1000) {
      const formatted = (absolute / 1000).toLocaleString(undefined, {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      });
      return `${formatted} kW`;
    }
    return `${Math.round(absolute)} W`;
  }

  _formatSoc(value) {
    if (value === null) return "–";
    return `${Math.round(value)} %`;
  }

  _flowClass(value, reverse = false) {
    if (!Number.isFinite(value) || value <= 0.5) return "flow inactive";
    return `flow active${reverse ? " reverse" : ""}`;
  }

  _flowDuration(value) {
    if (!Number.isFinite(value) || value <= 0.5) return "4s";
    const clamped = Math.max(20, Math.min(3000, value));
    const duration = 2.8 - ((clamped - 20) / 2980) * 2.0;
    return `${Math.max(0.8, duration).toFixed(2)}s`;
  }

  _moreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        bubbles: true,
        composed: true,
        detail: { entityId },
      }),
    );
  }

  _node({ x, y, cssClass, icon, title, main, details = [], entity }) {
    const detailHtml = details
      .filter((item) => item !== null && item !== undefined)
      .map((item) => `<div class="node-detail">${item}</div>`)
      .join("");

    return `
      <button
        class="node ${cssClass}"
        style="left:${x}%;top:${y}%"
        data-entity="${entity}"
        type="button"
      >
        <div class="node-icon"><ha-icon icon="${icon}"></ha-icon></div>
        <div class="node-main">${main}</div>
        ${detailHtml}
        <div class="node-title">${title}</div>
      </button>
    `;
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;

    const e = this._config.entities;
    const labels = {
      grid: "Grid",
      pv: "PV",
      noah: "NOAH",
      home: "Home",
      output: "Output",
      charging: "Charging",
      discharging: "Discharging",
      ...(this._config.labels || {}),
    };

    const gridImport = Math.max(this._numeric(e.grid_import) ?? 0, 0);
    const gridExport = Math.max(this._numeric(e.grid_export) ?? 0, 0);
    const solar = Math.max(this._numeric(e.solar_power) ?? 0, 0);
    const output = Math.max(this._numeric(e.output_power) ?? 0, 0);
    const charging = Math.max(this._numeric(e.charging_power) ?? 0, 0);
    const discharging = Math.max(this._numeric(e.discharging_power) ?? 0, 0);
    const home = Math.max(this._numeric(e.home_load) ?? 0, 0);
    const soc = this._soc(e.soc);

    const gridFlow = gridImport > 0.5 ? gridImport : gridExport;
    const gridReverse = gridExport > gridImport;

    const noahColor = charging > discharging + 0.5
      ? "charging"
      : discharging > charging + 0.5
        ? "discharging"
        : "idle";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; }
        ha-card {
          padding: 18px 16px 14px;
          overflow: hidden;
        }
        .title {
          font-size: 1.35rem;
          line-height: 1.35;
          margin: 0 0 8px 2px;
          color: var(--primary-text-color);
        }
        .stage {
          position: relative;
          width: 100%;
          aspect-ratio: 1.28 / 1;
          min-height: 310px;
        }
        svg {
          position:absolute;
          inset: 0;
          width:100%;
          height:100%;
          overflow:visible;
          pointer-events:none;
        }
        .base-line {
          fill:none;
          stroke: color-mix(in srgb, var(--secondary-text-color) 70%, transparent);
          stroke-width:1.2;
          opacity:.8;
        }
        .flow {
          fill:none;
          stroke-width:2.4;
          stroke-linecap:round;
          stroke-dasharray: 1 8;
          opacity:0;
        }
        .flow.active {
          opacity:1;
          animation-name: move-flow;
          animation-timing-function: linear;
          animation-iteration-count: infinite;
        }
        .flow.reverse { animation-direction: reverse; }
        .grid-flow { stroke:#42a5f5; }
        .grid-flow.reverse { stroke:#8e44ad; }
        .pv-flow { stroke:#ff9800; }
        .output-flow { stroke:#26a69a; }
        @keyframes move-flow { to { stroke-dashoffset:-36; } }
        .node {
          position:absolute;
          transform:translate(-50%,-50%);
          width:78px;
          min-height:78px;
          padding:7px 4px 5px;
          border-radius:50%;
          border:2px solid var(--secondary-text-color);
          background:var(--ha-card-background, var(--card-background-color));
          color:var(--primary-text-color);
          display:flex;
          flex-direction:column;
          align-items:center;
          justify-content:center;
          cursor:pointer;
          font:inherit;
          box-sizing:border-box;
          z-index:2;
        }
        .node:hover { filter:brightness(1.08); }
        .node.grid, .node.home { border-color:#42a5f5; }
        .node.pv { border-color:#ff9800; }
        .node.noah.idle { border-color:#26a69a; }
        .node.noah.charging { border-color:#ec407a; }
        .node.noah.discharging { border-color:#26c6da; }
        .node-icon {
          height:19px;
          line-height:19px;
          margin-bottom:1px;
        }
        ha-icon { --mdc-icon-size:18px; }
        .node-main { font-size:12px; font-weight:700; line-height:15px; }
        .node-detail { font-size:10px; line-height:12px; white-space:nowrap; }
        .node-title {
          position:absolute;
          top:calc(100% + 5px);
          font-size:11px;
          font-weight:500;
          white-space:nowrap;
          color:var(--primary-text-color);
        }
        .node.pv .node-main { color:#ff9800; }
        .node.noah.charging .charge { color:#ec407a; }
        .node.noah.discharging .discharge { color:#26c6da; }
        .line-label {
          position:absolute;
          left:68%;
          top:69%;
          transform:translate(-50%,-50%);
          padding:2px 5px;
          border-radius:8px;
          background:color-mix(in srgb, var(--ha-card-background, var(--card-background-color)) 88%, transparent);
          color:var(--secondary-text-color);
          font-size:10px;
          white-space:nowrap;
          z-index:1;
        }
        @media (max-width:420px) {
          .stage { min-height:285px; }
          .node { width:72px; min-height:72px; }
          .line-label { font-size:9px; }
        }
      </style>
      <ha-card>
        <div class="title">${this._config.title || ""}</div>
        <div class="stage">
          <svg viewBox="0 0 500 390" preserveAspectRatio="none" aria-hidden="true">
            <path class="base-line" d="M82 190 L418 190" />
            <path
              class="${this._flowClass(gridFlow, gridReverse)} grid-flow${gridReverse ? " reverse" : ""}"
              style="animation-duration:${this._flowDuration(gridFlow)}"
              d="M82 190 L418 190"
            />

            <path class="base-line" d="M250 112 L250 308" />
            <path
              class="${this._flowClass(solar)} pv-flow"
              style="animation-duration:${this._flowDuration(solar)}"
              d="M250 112 L250 308"
            />

            <path class="base-line" d="M278 306 C320 280 365 235 418 200" />
            <path
              class="${this._flowClass(output)} output-flow"
              style="animation-duration:${this._flowDuration(output)}"
              d="M278 306 C320 280 365 235 418 200"
            />
          </svg>

          ${this._node({
            x: 10,
            y: 49,
            cssClass: "grid",
            icon: "mdi:transmission-tower",
            title: labels.grid,
            main: `→ ${this._formatPower(gridImport)}`,
            details: [`← ${this._formatPower(gridExport)}`],
            entity: e.grid_import,
          })}

          ${this._node({
            x: 50,
            y: 22,
            cssClass: "pv",
            icon: "mdi:solar-power",
            title: labels.pv,
            main: this._formatPower(solar),
            entity: e.solar_power,
          })}

          ${this._node({
            x: 90,
            y: 49,
            cssClass: "home",
            icon: "mdi:home",
            title: labels.home,
            main: this._formatPower(home),
            entity: e.home_load,
          })}

          ${this._node({
            x: 50,
            y: 82,
            cssClass: `noah ${noahColor}`,
            icon: "mdi:battery",
            title: labels.noah,
            main: this._formatSoc(soc),
            details: [
              `<span class="charge">↓ ${this._formatPower(charging)}</span>`,
              `<span class="discharge">↑ ${this._formatPower(discharging)}</span>`,
            ],
            entity: e.soc,
          })}

          <div class="line-label">${labels.output}: ${this._formatPower(output)}</div>
        </div>
      </ha-card>
    `;

    for (const node of this.shadowRoot.querySelectorAll(".node")) {
      node.addEventListener("click", () => this._moreInfo(node.dataset.entity));
    }
  }
}

if (!customElements.get("noah-energy-flow-card")) {
  customElements.define("noah-energy-flow-card", NoahEnergyFlowCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "noah-energy-flow-card")) {
  window.customCards.push({
    type: "noah-energy-flow-card",
    name: "NOAH Energy Flow Card",
    description: "Energy-flow card for the Growatt NOAH topology.",
    preview: true,
  });
}
