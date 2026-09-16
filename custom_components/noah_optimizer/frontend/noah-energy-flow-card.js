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
    if (value === null || !Number.isFinite(value)) return "–";
    const absolute = Math.abs(value);

    if (absolute >= 1000) {
      return `${(absolute / 1000).toLocaleString(undefined, {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      })} kW`;
    }

    return `${Math.round(absolute)} W`;
  }

  _formatSoc(value) {
    if (value === null || !Number.isFinite(value)) return "–";
    return `${Math.round(value)} %`;
  }

  _flowDuration(value) {
    if (!Number.isFinite(value) || value <= 0.5) return 4.0;
    const clamped = Math.max(20, Math.min(3000, value));
    return Math.max(0.8, 3.0 - ((clamped - 20) / 2980) * 2.2);
  }

  _movingDots(path, value, color) {
    if (!Number.isFinite(value) || value <= 0.5) return "";

    const duration = this._flowDuration(value);
    const starts = [0, -(duration / 3), -(duration * 2 / 3)];

    return starts
      .map(
        (begin, index) => `
          <circle r="${index === 0 ? 4.3 : 3.6}" fill="${color}" opacity="${index === 0 ? 1 : 0.82}">
            <animateMotion
              dur="${duration.toFixed(2)}s"
              begin="${begin.toFixed(2)}s"
              repeatCount="indefinite"
              path="${path}"
            />
          </circle>
        `,
      )
      .join("");
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
        data-entity="${entity || ""}"
        type="button"
      >
        <div class="node-icon"><ha-icon icon="${icon}"></ha-icon></div>
        <div class="node-main">${main}</div>
        ${detailHtml}
        <div class="node-title">${title}</div>
      </button>
    `;
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

    const gridImportRaw = this._numeric(e.grid_import);
    const gridExportRaw = this._numeric(e.grid_export);
    const solarRaw = this._numeric(e.solar_power);
    const outputRaw = this._numeric(e.output_power);
    const chargingRaw = this._numeric(e.charging_power);
    const dischargingRaw = this._numeric(e.discharging_power);
    const homeRaw = this._numeric(e.home_load);
    const soc = this._soc(e.soc);

    const gridImport = Math.max(gridImportRaw ?? 0, 0);
    const gridExport = Math.max(gridExportRaw ?? 0, 0);
    const solar = Math.max(solarRaw ?? 0, 0);
    const output = Math.max(outputRaw ?? 0, 0);
    const charging = Math.max(chargingRaw ?? 0, 0);
    const discharging = Math.max(dischargingRaw ?? 0, 0);

    const gridPath = gridImport > 0.5
      ? "M82 190 L418 190"
      : "M418 190 L82 190";
    const gridFlow = gridImport > 0.5 ? gridImport : gridExport;

    const pvPath = "M250 104 L250 300";
    const outputPath = "M283 306 C330 285 370 225 418 197";

    const noahClass = charging > discharging + 0.5
      ? "charging"
      : discharging > charging + 0.5
        ? "discharging"
        : "idle";

    const outputDetail = `<span class="output-value">→ ${this._formatPower(outputRaw)}</span>`;
    const batteryDetail = `
      <span class="charge-value">↓ ${this._formatPower(chargingRaw)}</span>
      <span class="separator"> · </span>
      <span class="discharge-value">↑ ${this._formatPower(dischargingRaw)}</span>
    `;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; }

        ha-card {
          padding:18px 16px 16px;
          overflow:hidden;
        }

        .title {
          margin:0 0 8px 2px;
          color:var(--primary-text-color);
          font-size:1.35rem;
          line-height:1.35;
        }

        .stage {
          position:relative;
          width:100%;
          aspect-ratio:1.31 / 1;
          min-height:315px;
        }

        svg {
          position:absolute;
          inset:0;
          width:100%;
          height:100%;
          overflow:visible;
          pointer-events:none;
        }

        .base-line {
          fill:none;
          stroke:color-mix(in srgb, var(--secondary-text-color) 72%, transparent);
          stroke-width:1.25;
          opacity:.9;
        }

        .base-line.output {
          stroke:color-mix(in srgb, #26a69a 58%, var(--secondary-text-color));
        }

        .node {
          position:absolute;
          transform:translate(-50%,-50%);
          width:80px;
          min-height:80px;
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
          height:18px;
          line-height:18px;
          margin-bottom:1px;
        }

        ha-icon { --mdc-icon-size:18px; }

        .node-main {
          font-size:12px;
          font-weight:700;
          line-height:15px;
          white-space:nowrap;
        }

        .node-detail {
          font-size:9px;
          line-height:11px;
          white-space:nowrap;
        }

        .node-title {
          position:absolute;
          top:calc(100% + 5px);
          color:var(--primary-text-color);
          font-size:11px;
          font-weight:500;
          white-space:nowrap;
        }

        .node.pv .node-main { color:#ff9800; }
        .node.noah .output-value { color:#26a69a; }
        .node.noah.charging .charge-value { color:#ec407a; }
        .node.noah.discharging .discharge-value { color:#26c6da; }
        .separator { color:var(--secondary-text-color); }

        @media (max-width:420px) {
          .stage { min-height:290px; }
          .node { width:74px; min-height:74px; }
          .node-main { font-size:11px; }
          .node-detail { font-size:8.5px; }
        }
      </style>

      <ha-card>
        <div class="title">${this._config.title || ""}</div>
        <div class="stage">
          <svg viewBox="0 0 500 390" preserveAspectRatio="none" aria-hidden="true">
            <path class="base-line" d="M82 190 L418 190" />
            <path class="base-line" d="M250 104 L250 300" />
            <path class="base-line output" d="M283 306 C330 285 370 225 418 197" />

            ${this._movingDots(gridPath, gridFlow, gridImport > 0.5 ? "#42a5f5" : "#8e44ad")}
            ${this._movingDots(pvPath, solar, "#ff9800")}
            ${this._movingDots(outputPath, output, "#26a69a")}
          </svg>

          ${this._node({
            x: 10,
            y: 49,
            cssClass: "grid",
            icon: "mdi:transmission-tower",
            title: labels.grid,
            main: `→ ${this._formatPower(gridImportRaw)}`,
            details: [`← ${this._formatPower(gridExportRaw)}`],
            entity: e.grid_import,
          })}

          ${this._node({
            x: 50,
            y: 22,
            cssClass: "pv",
            icon: "mdi:solar-power",
            title: labels.pv,
            main: this._formatPower(solarRaw),
            entity: e.solar_power,
          })}

          ${this._node({
            x: 90,
            y: 49,
            cssClass: "home",
            icon: "mdi:home",
            title: labels.home,
            main: this._formatPower(homeRaw),
            entity: e.home_load,
          })}

          ${this._node({
            x: 50,
            y: 82,
            cssClass: `noah ${noahClass}`,
            icon: "mdi:battery",
            title: labels.noah,
            main: this._formatSoc(soc),
            details: [outputDetail, batteryDetail],
            entity: e.soc,
          })}
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
