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

    if (state.attributes?.unit_of_measurement === "kW") {
      return value * 1000;
    }

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
    if (!Number.isFinite(value) || value <= 0.5) return 3.4;

    const clamped = Math.max(20, Math.min(3000, value));
    return Math.max(0.9, 3.4 - ((clamped - 20) / 2980) * 2.4);
  }

  _flowDot(path, value, color) {
    if (!Number.isFinite(value) || value <= 0.5) return "";

    return `
      <circle r="4.2" fill="${color}" class="flow-dot">
        <animateMotion
          dur="${this._flowDuration(value).toFixed(2)}s"
          repeatCount="indefinite"
          path="${path}"
        />
      </circle>
    `;
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

    const gridFlow = gridImport > 0.5 ? gridImport : gridExport;
    const gridPath = gridImport > 0.5
      ? "M90 195 H410"
      : "M410 195 H90";

    /*
     * PV and the household AC bus visually cross, but are not directly
     * connected. The small bridge in this path makes that topology explicit.
     */
    const pvPath =
      "M250 112 V176 C250 184 242 184 242 195 C242 206 250 206 250 214 V300";

    /*
     * This is the only NOAH-to-home path and is driven exclusively by
     * output_power.
     */
    const outputPath =
      "M286 305 C334 292 367 232 410 202";

    const noahClass = charging > discharging + 0.5
      ? "charging"
      : discharging > charging + 0.5
        ? "discharging"
        : "idle";

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

        ha-card {
          padding: 18px 18px 16px;
          overflow: hidden;
        }

        .title {
          margin: 0 0 4px;
          color: var(--primary-text-color);
          font-size: 1.35rem;
          line-height: 1.35;
          font-weight: 500;
        }

        .stage {
          position: relative;
          width: 100%;
          aspect-ratio: 1.33 / 1;
          min-height: 320px;
        }

        svg {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          overflow: visible;
          pointer-events: none;
        }

        .base-line {
          fill: none;
          stroke: color-mix(
            in srgb,
            var(--secondary-text-color) 68%,
            transparent
          );
          stroke-width: 1.35;
          stroke-linecap: round;
          opacity: 0.78;
        }

        .base-line.output {
          stroke: color-mix(
            in srgb,
            #26a69a 48%,
            var(--secondary-text-color)
          );
        }

        .bridge-mask {
          fill: none;
          stroke: var(--ha-card-background, var(--card-background-color));
          stroke-width: 5;
          stroke-linecap: round;
        }

        .flow-dot {
          filter: drop-shadow(0 0 1.5px currentColor);
        }

        .node {
          position: absolute;
          transform: translate(-50%, -50%);
          width: 86px;
          min-height: 86px;
          padding: 7px 5px 6px;
          border-radius: 50%;
          border: 2px solid var(--secondary-text-color);
          background: var(--ha-card-background, var(--card-background-color));
          color: var(--primary-text-color);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          box-sizing: border-box;
          cursor: pointer;
          font: inherit;
          z-index: 2;
        }

        .node:hover {
          filter: brightness(1.06);
        }

        .node.grid,
        .node.home {
          border-color: #42a5f5;
        }

        .node.pv {
          border-color: #ff9800;
        }

        .node.noah.idle {
          border-color: #26a69a;
        }

        .node.noah.charging {
          border-color: #ec407a;
        }

        .node.noah.discharging {
          border-color: #26c6da;
        }

        .node-icon {
          height: 19px;
          line-height: 19px;
          margin-bottom: 1px;
        }

        ha-icon {
          --mdc-icon-size: 18px;
        }

        .node-main {
          font-size: 12px;
          font-weight: 700;
          line-height: 15px;
          white-space: nowrap;
        }

        .node-detail {
          font-size: 9.5px;
          line-height: 11.5px;
          white-space: nowrap;
        }

        .node-title {
          position: absolute;
          top: calc(100% + 5px);
          color: var(--primary-text-color);
          font-size: 11px;
          font-weight: 500;
          white-space: nowrap;
        }

        .node.pv .node-main {
          color: #ff9800;
        }

        .output-value {
          color: #26a69a;
        }

        .charge-value {
          color: #ec407a;
        }

        .discharge-value {
          color: #26c6da;
        }

        .separator {
          color: var(--secondary-text-color);
        }

        @media (max-width: 420px) {
          .stage {
            min-height: 295px;
          }

          .node {
            width: 78px;
            min-height: 78px;
          }

          .node-main {
            font-size: 11px;
          }

          .node-detail {
            font-size: 8.5px;
          }
        }
      </style>

      <ha-card>
        <div class="title">${this._config.title || ""}</div>

        <div class="stage">
          <svg viewBox="0 0 500 390" preserveAspectRatio="none" aria-hidden="true">
            <!-- Grid / household AC bus -->
            <path class="base-line" d="M90 195 H410" />

            <!-- PV -> NOAH, with a visual bridge over the AC bus -->
            <path
              class="bridge-mask"
              d="M250 176 C250 184 242 184 242 195 C242 206 250 206 250 214"
            />
            <path
              class="base-line"
              d="M250 112 V176 C250 184 242 184 242 195 C242 206 250 206 250 214 V300"
            />

            <!-- NOAH -> Home -->
            <path
              class="base-line output"
              d="M286 305 C334 292 367 232 410 202"
            />

            ${this._flowDot(
              gridPath,
              gridFlow,
              gridImport > 0.5 ? "#42a5f5" : "#8e44ad",
            )}

            ${this._flowDot(
              pvPath,
              solar,
              "#ff9800",
            )}

            ${this._flowDot(
              outputPath,
              output,
              "#26a69a",
            )}
          </svg>

          ${this._node({
            x: 10,
            y: 50,
            cssClass: "grid",
            icon: "mdi:transmission-tower",
            title: labels.grid,
            main: `→ ${this._formatPower(gridImportRaw)}`,
            details: [`← ${this._formatPower(gridExportRaw)}`],
            entity: e.grid_import,
          })}

          ${this._node({
            x: 50,
            y: 21,
            cssClass: "pv",
            icon: "mdi:solar-power",
            title: labels.pv,
            main: this._formatPower(solarRaw),
            entity: e.solar_power,
          })}

          ${this._node({
            x: 90,
            y: 50,
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
            details: [
              `<span class="output-value">→ ${this._formatPower(outputRaw)}</span>`,
              `<span class="charge-value">↓ ${this._formatPower(chargingRaw)}</span><span class="separator"> · </span><span class="discharge-value">↑ ${this._formatPower(dischargingRaw)}</span>`,
            ],
            entity: e.soc,
          })}
        </div>
      </ha-card>
    `;

    for (const node of this.shadowRoot.querySelectorAll(".node")) {
      node.addEventListener(
        "click",
        () => this._moreInfo(node.dataset.entity),
      );
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
