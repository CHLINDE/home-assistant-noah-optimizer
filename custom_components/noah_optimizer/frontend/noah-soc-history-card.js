class NoahSocHistoryCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = null;
    this._selectedDate = this._todayString();
    this._history = {};
    this._snapshots = [];
    this._snapshotIndex = -1;
    this._loading = false;
    this._error = null;
    this._lastLoad = 0;
    this._loadToken = 0;
    this._tooltipPinned = false;
  }

  setConfig(config) {
    const required = [
      "entry_id",
      "soc_entity",
      "dynamic_target_entity",
      "target_soc_entity",
    ];
    for (const key of required) {
      if (!config[key]) {
        throw new Error(`Missing required option: ${key}`);
      }
    }
    this._config = {
      title: "SOC schedule history",
      labels: {},
      ...config,
    };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._config) return;
    if (!this.shadowRoot.querySelector(".card")) this._render();

    const isToday = this._selectedDate === this._todayString();
    if (!this._lastLoad || (isToday && Date.now() - this._lastLoad > 60000)) {
      this._loadData();
    }
  }

  getCardSize() {
    return 6;
  }

  static getStubConfig() {
    return {};
  }

  _todayString() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  _labels() {
    return {
      previous: "Previous day",
      next: "Next day",
      today: "Today",
      planSnapshot: "Plan snapshot",
      noSnapshot: "No saved plan",
      actualSoc: "Actual SOC",
      dynamicTarget: "Dynamic target",
      targetSoc: "Target SOC",
      savedPlan: "Saved plan",
      loading: "Loading history…",
      noData: "No history data available for this day.",
      forecastUpdated: "Forecast updated",
      effectiveForecast: "Effective forecast",
      plannedEndSoc: "Forecast end SOC",
      retention: "Snapshots retained for {days} days",
      ...this._config?.labels,
    };
  }

  _render() {
    if (!this._config) return;
    const labels = this._labels();
    const today = this._todayString();
    const nextDisabled = this._selectedDate >= today ? "disabled" : "";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .card {
          background: var(--ha-card-background, var(--card-background-color));
          border-radius: var(--ha-card-border-radius, 12px);
          box-shadow: var(--ha-card-box-shadow, none);
          border: var(--ha-card-border-width, 0) solid var(--ha-card-border-color, transparent);
          color: var(--primary-text-color);
          padding: 16px;
          box-sizing: border-box;
        }
        .header { display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
        .title { font-size: 16px; font-weight: 600; }
        .date-controls { display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
        button, input, select {
          font: inherit;
          color: var(--primary-text-color);
          background: var(--secondary-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          min-height: 34px;
          box-sizing: border-box;
        }
        button { cursor:pointer; padding: 0 10px; }
        button.icon { min-width: 36px; font-size: 22px; line-height: 1; }
        button:disabled { opacity:.4; cursor:default; }
        input, select { padding: 4px 8px; }
        .snapshot-row { margin-top:10px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
        .snapshot-row label { color: var(--secondary-text-color); font-size: 13px; }
        .chart-wrap { margin-top:12px; width:100%; overflow:hidden; position:relative; }
        svg { width:100%; height:auto; display:block; }
        .grid { stroke: var(--divider-color); stroke-width:1; stroke-dasharray:4 4; }
        .axis-label { fill: var(--secondary-text-color); font-size: 12px; }
        .line { fill:none; vector-effect:non-scaling-stroke; }
        .actual { stroke: #2196F3; stroke-width:2.5; }
        .dynamic { stroke: #009B21; stroke-width:3; }
        .target { stroke: #FF6A00; stroke-width:1.5; stroke-dasharray:6 4; }
        .saved { stroke: #FFD800; stroke-width:2.5; stroke-dasharray:8 5; }
        .hover-line { stroke: var(--primary-text-color); stroke-width:1; stroke-dasharray:4 4; opacity:.55; vector-effect:non-scaling-stroke; pointer-events:none; }
        .hover-marker { stroke: var(--ha-card-background, var(--card-background-color)); stroke-width:2; vector-effect:non-scaling-stroke; pointer-events:none; }
        .hitbox { fill:transparent; pointer-events:all; touch-action:pan-y; cursor:crosshair; }
        .tooltip {
          position:absolute;
          display:none;
          min-width:220px;
          max-width:min(320px, calc(100% - 16px));
          padding:10px 12px;
          border:1px solid var(--primary-text-color);
          border-radius:6px;
          background:var(--ha-card-background, var(--card-background-color));
          color:var(--primary-text-color);
          box-shadow:0 4px 14px rgba(0,0,0,.35);
          font-size:12px;
          line-height:1.4;
          box-sizing:border-box;
          z-index:3;
          pointer-events:none;
        }
        .tooltip-time { font-weight:600; padding-bottom:7px; margin-bottom:6px; border-bottom:1px solid var(--divider-color); }
        .tooltip-row { display:flex; align-items:center; gap:7px; padding:3px 0; }
        .tooltip-row .name { flex:1; min-width:0; }
        .tooltip-row .value { font-weight:600; white-space:nowrap; }
        .legend { display:flex; gap:16px; flex-wrap:wrap; justify-content:center; margin-top:6px; font-size:12px; }
        .legend span { display:inline-flex; align-items:center; gap:5px; }
        .dot { width:10px; height:10px; border-radius:50%; display:inline-block; flex:0 0 auto; }
        .meta { margin-top:10px; color:var(--secondary-text-color); font-size:12px; line-height:1.5; }
        .message { min-height:280px; display:flex; align-items:center; justify-content:center; color:var(--secondary-text-color); text-align:center; }
        .error { color: var(--error-color); }
      </style>
      <ha-card class="card">
        <div class="header">
          <div class="title">${this._escape(this._config.title)}</div>
          <div class="date-controls">
            <button class="icon" id="prev" title="${this._escape(labels.previous)}">‹</button>
            <input id="date" type="date" value="${this._selectedDate}" max="${today}">
            <button class="icon" id="next" title="${this._escape(labels.next)}" ${nextDisabled}>›</button>
            <button id="today">${this._escape(labels.today)}</button>
          </div>
        </div>
        <div class="snapshot-row" id="snapshot-row"></div>
        <div class="chart-wrap" id="chart"></div>
        <div class="legend" id="legend"></div>
        <div class="meta" id="meta"></div>
      </ha-card>
    `;

    this.shadowRoot.getElementById("prev").addEventListener("click", () => this._shiftDate(-1));
    this.shadowRoot.getElementById("next").addEventListener("click", () => this._shiftDate(1));
    this.shadowRoot.getElementById("today").addEventListener("click", () => this._setDate(this._todayString()));
    this.shadowRoot.getElementById("date").addEventListener("change", (ev) => this._setDate(ev.target.value));
    this._tooltipPinned = false;
    this._renderData();
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _shiftDate(days) {
    const date = new Date(`${this._selectedDate}T12:00:00`);
    date.setDate(date.getDate() + days);
    const next = this._localDateString(date);
    if (next <= this._todayString()) this._setDate(next);
  }

  _localDateString(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  _setDate(value) {
    if (!value || value > this._todayString()) return;

    this._loadToken += 1;
    this._loading = false;
    this._selectedDate = value;
    this._snapshotIndex = -1;
    this._history = {};
    this._snapshots = [];
    this._error = null;
    this._lastLoad = 0;
    this._tooltipPinned = false;
    this._render();
    this._loadData();
  }

  async _loadData() {
    if (!this._hass || !this._config || this._loading) return;
    this._loading = true;
    this._error = null;
    const token = ++this._loadToken;
    this._renderData();

    const start = new Date(`${this._selectedDate}T00:00:00`);
    const end = new Date(start);
    end.setDate(end.getDate() + 1);

    try {
      const historyPromise = this._hass.callWS({
        type: "history/history_during_period",
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        entity_ids: [
          this._config.soc_entity,
          this._config.dynamic_target_entity,
          this._config.target_soc_entity,
        ],
        include_start_time_state: true,
        significant_changes_only: false,
        minimal_response: false,
        no_attributes: true,
      });

      const snapshotPromise = this._hass.callWS({
        type: "noah_optimizer/history_snapshots",
        entry_id: this._config.entry_id,
        date: this._selectedDate,
      });

      const [historyResult, snapshotResult] = await Promise.allSettled([
        historyPromise,
        snapshotPromise,
      ]);
      if (token !== this._loadToken) return;

      if (historyResult.status === "rejected") throw historyResult.reason;
      this._history = historyResult.value || {};
      this._snapshots = snapshotResult.status === "fulfilled"
        ? (snapshotResult.value?.snapshots || [])
        : [];
      this._retentionDays = snapshotResult.status === "fulfilled"
        ? snapshotResult.value?.retention_days
        : null;

      this._snapshotIndex = this._snapshots.length ? this._snapshots.length - 1 : -1;
      this._lastLoad = Date.now();
    } catch (err) {
      this._error = err?.message || String(err);
    } finally {
      if (token === this._loadToken) {
        this._loading = false;
        this._render();
      }
    }
  }

  _parseSeries(entityId) {
    const raw = this._history?.[entityId] || [];
    const points = [];
    for (const item of raw) {
      const state = item.state ?? item.s;
      const value = Number(state);
      if (!Number.isFinite(value)) continue;
      let time = item.last_updated ?? item.last_changed ?? item.lu ?? item.lc;
      if (typeof time === "number") time *= 1000;
      else time = Date.parse(time);
      if (!Number.isFinite(time)) continue;
      points.push([time, value]);
    }
    points.sort((a, b) => a[0] - b[0]);
    return points;
  }

  _selectedSnapshot() {
    if (this._snapshotIndex < 0 || this._snapshotIndex >= this._snapshots.length) return null;
    return this._snapshots[this._snapshotIndex];
  }

  _renderData() {
    const chart = this.shadowRoot?.getElementById("chart");
    const legend = this.shadowRoot?.getElementById("legend");
    const meta = this.shadowRoot?.getElementById("meta");
    const snapshotRow = this.shadowRoot?.getElementById("snapshot-row");
    if (!chart || !legend || !meta || !snapshotRow || !this._config) return;
    const labels = this._labels();

    if (this._loading) {
      chart.innerHTML = `<div class="message">${this._escape(labels.loading)}</div>`;
      legend.innerHTML = "";
      meta.innerHTML = "";
      snapshotRow.innerHTML = "";
      return;
    }
    if (this._error) {
      chart.innerHTML = `<div class="message error">${this._escape(this._error)}</div>`;
      legend.innerHTML = "";
      meta.innerHTML = "";
      snapshotRow.innerHTML = "";
      return;
    }

    this._renderSnapshotSelector(snapshotRow, labels);

    const start = new Date(`${this._selectedDate}T00:00:00`).getTime();
    const endDate = new Date(`${this._selectedDate}T00:00:00`);
    endDate.setDate(endDate.getDate() + 1);
    const end = endDate.getTime();
    const actual = this._clipSeries(this._parseSeries(this._config.soc_entity), start, end);
    const dynamic = this._clipSeries(this._parseSeries(this._config.dynamic_target_entity), start, end);
    const target = this._clipSeries(this._parseSeries(this._config.target_soc_entity), start, end);
    const snapshot = this._selectedSnapshot();
    const saved = this._snapshotPlan(snapshot, start, end);

    if (!actual.length && !dynamic.length && !target.length && !saved.length) {
      chart.innerHTML = `<div class="message">${this._escape(labels.noData)}</div>`;
      legend.innerHTML = "";
      this._renderMeta(meta, snapshot, labels);
      return;
    }

    const width = 900;
    const height = 360;
    const margin = { left: 50, right: 18, top: 16, bottom: 34 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;
    const seriesEnd = this._seriesEnd(end);
    const x = (t) => margin.left + ((t - start) / (end - start)) * plotW;
    const y = (v) => margin.top + (1 - Math.max(0, Math.min(100, v)) / 100) * plotH;

    let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${this._escape(this._config.title)}">`;
    for (const value of [0, 25, 50, 75, 100]) {
      const yy = y(value);
      svg += `<line class="grid" x1="${margin.left}" y1="${yy}" x2="${width - margin.right}" y2="${yy}"></line>`;
      svg += `<text class="axis-label" x="${margin.left - 8}" y="${yy + 4}" text-anchor="end">${value}</text>`;
    }
    for (let i = 0; i <= 4; i++) {
      const fraction = i / 4;
      const xx = margin.left + fraction * plotW;
      const t = new Date(start + fraction * (end - start));
      const hh = String(t.getHours()).padStart(2, "0");
      const mm = String(t.getMinutes()).padStart(2, "0");
      svg += `<line class="grid" x1="${xx}" y1="${margin.top}" x2="${xx}" y2="${height - margin.bottom}"></line>`;
      svg += `<text class="axis-label" x="${xx}" y="${height - 10}" text-anchor="middle">${hh}:${mm}</text>`;
    }

    svg += this._path(actual, x, y, false, "actual", seriesEnd);
    svg += this._path(dynamic, x, y, true, "dynamic", seriesEnd);
    svg += this._path(target, x, y, true, "target", seriesEnd);
    svg += this._path(saved, x, y, false, "saved");
    svg += `<line id="hover-line" class="hover-line" x1="0" y1="${margin.top}" x2="0" y2="${height - margin.bottom}" visibility="hidden"></line>`;
    svg += `<circle id="hover-actual" class="hover-marker" r="5" fill="#2196F3" display="none"></circle>`;
    svg += `<circle id="hover-dynamic" class="hover-marker" r="5" fill="#009B21" display="none"></circle>`;
    svg += `<circle id="hover-target" class="hover-marker" r="5" fill="#FF6A00" display="none"></circle>`;
    svg += `<circle id="hover-saved" class="hover-marker" r="5" fill="#FFD800" display="none"></circle>`;
    svg += `<rect id="hitbox" class="hitbox" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${plotH}"></rect>`;
    svg += `</svg><div class="tooltip" id="tooltip"></div>`;
    chart.innerHTML = svg;

    const legendItems = [];
    if (actual.length) legendItems.push(this._legend("#2196F3", labels.actualSoc));
    if (dynamic.length) legendItems.push(this._legend("#009B21", labels.dynamicTarget));
    if (target.length) legendItems.push(this._legend("#FF6A00", labels.targetSoc));
    if (saved.length) legendItems.push(this._legend("#FFD800", labels.savedPlan));
    legend.innerHTML = legendItems.join("");

    this._installTooltip(chart, {
      start,
      end,
      width,
      height,
      margin,
      plotW,
      plotH,
      seriesEnd,
      actual,
      dynamic,
      target,
      saved,
      labels,
      y,
    });
    this._renderMeta(meta, snapshot, labels);
  }

  _seriesEnd(dayEnd) {
    if (this._selectedDate < this._todayString()) return dayEnd;
    return Math.min(dayEnd, Date.now());
  }

  _clipSeries(points, start, end) {
    const clipped = [];
    for (const [time, value] of points) {
      if (time > end) continue;
      const clippedTime = Math.max(time, start);
      if (clipped.length && clipped[clipped.length - 1][0] === clippedTime) {
        clipped[clipped.length - 1] = [clippedTime, value];
      } else {
        clipped.push([clippedTime, value]);
      }
    }
    return clipped;
  }

  _snapshotPlan(snapshot, start, end) {
    if (!snapshot) return [];
    const points = (snapshot.soc_plan || [])
      .map((point) => [Date.parse(point[0]), Number(point[1])])
      .filter((point) => Number.isFinite(point[0]) && Number.isFinite(point[1]))
      .sort((a, b) => a[0] - b[0]);
    if (!points.length) return [];

    const clipped = this._clipSeries(points, start, end);
    if (!clipped.length) return [];

    if (clipped[0][0] > start) {
      const initial = Number(snapshot.min_soc);
      clipped.unshift([start, Number.isFinite(initial) ? initial : clipped[0][1]]);
    }
    if (clipped[clipped.length - 1][0] < end) {
      clipped.push([end, clipped[clipped.length - 1][1]]);
    }
    return clipped;
  }

  _path(points, x, y, step, cls, extendTo = null) {
    const filtered = points.filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (!filtered.length) return "";
    let d = `M ${x(filtered[0][0]).toFixed(2)} ${y(filtered[0][1]).toFixed(2)}`;
    let previous = filtered[0];
    for (const current of filtered.slice(1)) {
      if (step) {
        d += ` L ${x(current[0]).toFixed(2)} ${y(previous[1]).toFixed(2)}`;
      }
      d += ` L ${x(current[0]).toFixed(2)} ${y(current[1]).toFixed(2)}`;
      previous = current;
    }
    if (extendTo && extendTo > previous[0]) {
      d += ` L ${x(extendTo).toFixed(2)} ${y(previous[1]).toFixed(2)}`;
    }
    return `<path class="line ${cls}" d="${d}"></path>`;
  }

  _valueAt(points, time, step = false, extendTo = null) {
    if (!points.length || time < points[0][0]) return null;
    const last = points[points.length - 1];
    if (time > last[0]) {
      return extendTo !== null && time <= extendTo ? last[1] : null;
    }

    let low = 0;
    let high = points.length - 1;
    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      if (points[mid][0] <= time) low = mid + 1;
      else high = mid - 1;
    }

    const index = Math.max(0, high);
    const current = points[index];
    if (step || index >= points.length - 1 || current[0] === time) {
      return current[1];
    }

    const next = points[index + 1];
    const span = next[0] - current[0];
    if (span <= 0) return current[1];
    const fraction = Math.max(0, Math.min(1, (time - current[0]) / span));
    return current[1] + (next[1] - current[1]) * fraction;
  }

  _formatTooltipTime(time) {
    const locale = this._hass?.language || navigator.language;
    const date = new Date(time);
    return new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date);
  }

  _installTooltip(chart, context) {
    const svg = chart.querySelector("svg");
    const hitbox = chart.querySelector("#hitbox");
    const tooltip = chart.querySelector("#tooltip");
    const hoverLine = chart.querySelector("#hover-line");
    if (!svg || !hitbox || !tooltip || !hoverLine) return;

    const markerIds = {
      actual: "#hover-actual",
      dynamic: "#hover-dynamic",
      target: "#hover-target",
      saved: "#hover-saved",
    };
    const hide = () => {
      tooltip.style.display = "none";
      hoverLine.setAttribute("visibility", "hidden");
      for (const selector of Object.values(markerIds)) {
        const marker = chart.querySelector(selector);
        if (marker) marker.setAttribute("display", "none");
      }
    };

    const update = (event) => {
      const svgRect = svg.getBoundingClientRect();
      const chartRect = chart.getBoundingClientRect();
      if (!svgRect.width || !chartRect.width) return;

      const rawSvgX = (event.clientX - svgRect.left) * context.width / svgRect.width;
      const svgX = Math.max(
        context.margin.left,
        Math.min(context.width - context.margin.right, rawSvgX),
      );
      const fraction = (svgX - context.margin.left) / context.plotW;
      const time = context.start + fraction * (context.end - context.start);

      const values = [
        {
          key: "actual",
          color: "#2196F3",
          label: context.labels.actualSoc,
          value: this._valueAt(context.actual, time, false, context.seriesEnd),
        },
        {
          key: "dynamic",
          color: "#009B21",
          label: context.labels.dynamicTarget,
          value: this._valueAt(context.dynamic, time, true, context.seriesEnd),
        },
        {
          key: "target",
          color: "#FF6A00",
          label: context.labels.targetSoc,
          value: this._valueAt(context.target, time, true, context.seriesEnd),
        },
        {
          key: "saved",
          color: "#FFD800",
          label: context.labels.savedPlan,
          value: this._valueAt(context.saved, time),
        },
      ];

      const visible = values.filter((item) => Number.isFinite(item.value));
      if (!visible.length) {
        hide();
        return;
      }

      hoverLine.setAttribute("x1", svgX.toFixed(2));
      hoverLine.setAttribute("x2", svgX.toFixed(2));
      hoverLine.setAttribute("visibility", "visible");

      for (const item of values) {
        const marker = chart.querySelector(markerIds[item.key]);
        if (!marker) continue;
        if (!Number.isFinite(item.value)) {
          marker.setAttribute("display", "none");
          continue;
        }
        marker.setAttribute("cx", svgX.toFixed(2));
        marker.setAttribute("cy", context.y(item.value).toFixed(2));
        marker.setAttribute("display", "block");
      }

      const rows = visible.map((item) => `
        <div class="tooltip-row">
          <i class="dot" style="background:${item.color}"></i>
          <span class="name">${this._escape(item.label)}:</span>
          <span class="value">${Number(item.value).toFixed(1)} %</span>
        </div>
      `).join("");
      tooltip.innerHTML = `<div class="tooltip-time">${this._escape(this._formatTooltipTime(time))}</div>${rows}`;
      tooltip.style.display = "block";

      const pointerX = event.clientX - chartRect.left;
      const pointerY = event.clientY - chartRect.top;
      const tooltipWidth = tooltip.offsetWidth;
      const tooltipHeight = tooltip.offsetHeight;
      let left = pointerX + 12;
      if (left + tooltipWidth > chart.clientWidth - 8) {
        left = pointerX - tooltipWidth - 12;
      }
      left = Math.max(8, Math.min(left, chart.clientWidth - tooltipWidth - 8));

      let top = pointerY - tooltipHeight - 12;
      if (top < 8) top = pointerY + 12;
      top = Math.max(8, Math.min(top, chart.clientHeight - tooltipHeight - 8));
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${top}px`;
    };

    hitbox.addEventListener("pointermove", (event) => {
      if (event.pointerType === "mouse" && !this._tooltipPinned) update(event);
    });
    hitbox.addEventListener("pointerleave", (event) => {
      if (event.pointerType === "mouse" && !this._tooltipPinned) hide();
    });
    hitbox.addEventListener("pointerup", (event) => {
      if (event.pointerType !== "mouse") {
        this._tooltipPinned = true;
        update(event);
      }
    });
    hitbox.addEventListener("click", (event) => {
      if (!event.pointerType || event.pointerType === "mouse") {
        this._tooltipPinned = false;
        update(event);
      }
    });
  }

  _legend(color, text) {
    return `<span><i class="dot" style="background:${color}"></i>${this._escape(text)}</span>`;
  }

  _renderSnapshotSelector(container, labels) {
    if (!this._snapshots.length) {
      container.innerHTML = `<label>${this._escape(labels.planSnapshot)}: ${this._escape(labels.noSnapshot)}</label>`;
      return;
    }
    const locale = this._hass?.language || navigator.language;
    const options = this._snapshots.map((snapshot, index) => {
      const timestamp = snapshot.captured_at || snapshot.forecast_updated_at;
      const date = timestamp ? new Date(timestamp) : null;
      const text = date && Number.isFinite(date.getTime())
        ? new Intl.DateTimeFormat(locale, { hour: "2-digit", minute: "2-digit" }).format(date)
        : `#${index + 1}`;
      return `<option value="${index}" ${index === this._snapshotIndex ? "selected" : ""}>${this._escape(text)}</option>`;
    }).join("");
    container.innerHTML = `<label for="snapshot">${this._escape(labels.planSnapshot)}</label><select id="snapshot">${options}</select>`;
    container.querySelector("#snapshot").addEventListener("change", (ev) => {
      this._snapshotIndex = Number(ev.target.value);
      this._tooltipPinned = false;
      this._renderData();
    });
  }

  _renderMeta(container, snapshot, labels) {
    const parts = [];
    const locale = this._hass?.language || navigator.language;
    if (snapshot?.forecast_updated_at) {
      const d = new Date(snapshot.forecast_updated_at);
      if (Number.isFinite(d.getTime())) {
        parts.push(`${this._escape(labels.forecastUpdated)}: ${this._escape(new Intl.DateTimeFormat(locale, { dateStyle: "short", timeStyle: "short" }).format(d))}`);
      }
    }
    if (Number.isFinite(Number(snapshot?.effective_day_energy_kwh))) {
      parts.push(`${this._escape(labels.effectiveForecast)}: ${Number(snapshot.effective_day_energy_kwh).toFixed(2)} kWh`);
    }
    if (Number.isFinite(Number(snapshot?.planned_end_soc))) {
      parts.push(`${this._escape(labels.plannedEndSoc)}: ${Number(snapshot.planned_end_soc).toFixed(1)} %`);
    }
    if (this._retentionDays) {
      parts.push(this._escape(labels.retention.replace("{days}", this._retentionDays)));
    }
    container.innerHTML = parts.join(" · ");
  }
}

if (!customElements.get("noah-soc-history-card")) {
  customElements.define("noah-soc-history-card", NoahSocHistoryCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "noah-soc-history-card")) {
  window.customCards.push({
    type: "noah-soc-history-card",
    name: "NOAH SOC History Card",
    description: "Date-selectable NOAH Optimizer SOC schedule history",
    preview: false,
  });
}
