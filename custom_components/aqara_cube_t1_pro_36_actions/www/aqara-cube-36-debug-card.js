class AqaraCube36DebugCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('entity is required, use the *_last_action sensor created by Aqara Cube T1 Pro 36 Actions');
    }
    this.config = {
      show_help: true,
      show_history: true,
      history_size: 5,
      compact: false,
      ...config,
    };
  }

  static getStubConfig(hass) {
    const entity = Object.keys(hass.states).find((e) =>
      e.startsWith('sensor.') && e.includes('cube36') && e.endsWith('_last_action')
    ) || Object.keys(hass.states).find((e) => e.startsWith('sensor.') && e.endsWith('_last_action')) || '';
    return { entity, show_help: true, history_size: 5 };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return this.config?.compact ? 4 : 7;
  }

  _state(entityId) {
    return this._hass?.states?.[entityId];
  }

  _baseEntity() {
    const entity = this.config.entity;
    if (entity && entity.endsWith('_last_action')) return entity.replace(/_last_action$/, '');
    return entity || '';
  }

  _sensor(suffix) {
    const base = this._baseEntity();
    return `${base}_${suffix}`;
  }

  _clean(value, fallback = '—') {
    if (value === undefined || value === null) return fallback;
    const str = String(value);
    if (['unknown', 'unavailable', 'none', 'None', ''].includes(str)) return fallback;
    return value;
  }

  _main() {
    return this._state(this.config.entity);
  }

  _attr(name, fallback = '—') {
    const main = this._main();
    const value = main?.attributes?.[name];
    if (value !== undefined && value !== null && !['unknown', 'unavailable', 'none', 'None', ''].includes(String(value))) {
      return value;
    }

    // Backward-compatible fallback for older test builds:
    // if attributes are missing, try the sibling diagnostic sensor.
    const st = this._state(this._sensor(name));
    return this._clean(st?.state, fallback);
  }

  _mainValue(fallback = '—') {
    return this._clean(this._main()?.state, fallback);
  }

  _actionStyle(action) {
    if ((action || '').includes('rotate')) return ['mdi:rotate-3d-variant', 'linear-gradient(135deg, rgba(33,150,243,0.22), rgba(33,150,243,0.06))'];
    if ((action || '').includes('flip')) return ['mdi:axis-arrow', 'linear-gradient(135deg, rgba(255,193,7,0.22), rgba(255,193,7,0.06))'];
    if (action === 'shake') return ['mdi:vibrate', 'linear-gradient(135deg, rgba(76,175,80,0.22), rgba(76,175,80,0.06))'];
    if (action === 'throw') return ['mdi:gesture-swipe-down', 'linear-gradient(135deg, rgba(244,67,54,0.22), rgba(244,67,54,0.06))'];
    if (action === 'tap') return ['mdi:gesture-tap', 'linear-gradient(135deg, rgba(156,39,176,0.22), rgba(156,39,176,0.06))'];
    if (action === 'slide') return ['mdi:arrow-left-right-bold', 'linear-gradient(135deg, rgba(0,188,212,0.22), rgba(0,188,212,0.06))'];
    return ['mdi:cube-outline', 'linear-gradient(135deg, rgba(120,120,120,0.16), rgba(120,120,120,0.04))'];
  }

  render() {
    if (!this._hass || !this.config) return;

    const main = this._main();
    if (!main) {
      this.innerHTML = `
        <ha-card>
          <div class="cube-card">
            <div class="cube-title">AQARA CUBE T1 PRO</div>
            <div class="cube-empty">Entity not found: ${this._escape(this.config.entity)}</div>
          </div>
        </ha-card>
        <style>${this._styles()}</style>
      `;
      return;
    }

    const action = this._mainValue();
    const side = this._attr('last_side');
    const activeSide = this._attr('active_side');
    const fromSide = this._attr('last_from_side');
    const angle = this._attr('last_angle');
    const lqi = this._attr('last_lqi');
    const battery = this._attr('battery');
    const voltage = this._attr('voltage');
    const mode = this._attr('operation_mode');
    const eventCount = this._attr('event_count', '0');
    const lastTime = this._attr('last_event_time');

    let history = main.attributes?.event_history;
    if (!Array.isArray(history)) {
      const historyEntity = this._state(this._sensor('event_history'));
      history = historyEntity?.attributes?.history || [];
    }

    const [icon, background] = this._actionStyle(String(action));

    const historyRows = (history || [])
      .slice(0, Number(this.config.history_size || 5))
      .map((e, idx) => `<div class="cube-row ${idx === 0 ? 'cube-row-last' : ''}">${this._escape(e)}</div>`)
      .join('');

    const help = this.config.show_help ? `
      <div class="cube-help">
        <div class="cube-label">GESTURE TRAINING</div>
        <div class="cube-tip"><b>Use a hard surface.</b> Soft beds/sofas make slide, tap and rotate unreliable.</div>
        <div class="cube-tip"><b>shake</b> = sharp up/down shake</div>
        <div class="cube-tip"><b>throw</b> = short sharp downward jerk in hand</div>
        <div class="cube-tip"><b>slide</b> = slow short 2–3 cm slide on table</div>
        <div class="cube-tip"><b>rotate</b> = slow rotation on table</div>
        <div class="cube-tip"><b>tap</b> = two light taps with the cube on the table</div>
      </div>` : '';

    this.innerHTML = `
      <ha-card style="background:${background};">
        <div class="cube-card">
          <div class="cube-head">
            <div>
              <div class="cube-title">AQARA CUBE T1 PRO</div>
              <div class="cube-sub">36 Actions · debug/training feed · ${this._escape(mode)}</div>
            </div>
            <div class="cube-count">#${Number(eventCount || 0).toFixed(0)}</div>
          </div>

          <div class="cube-grid">
            <div class="cube-box cube-main">
              <ha-icon icon="${icon}"></ha-icon>
              <div>
                <div class="cube-label">ACTION</div>
                <div class="cube-value">${this._escape(action)}</div>
              </div>
            </div>

            <div class="cube-box">
              <div>
                <div class="cube-label">SIDE / ACTIVE</div>
                <div class="cube-value">${this._escape(fromSide)} → ${this._escape(side)} · active ${this._escape(activeSide)}</div>
              </div>
            </div>

            <div class="cube-box">
              <div>
                <div class="cube-label">ANGLE</div>
                <div class="cube-value">${this._escape(angle)}°</div>
              </div>
            </div>

            <div class="cube-box">
              <div>
                <div class="cube-label">RADIO / BATTERY</div>
                <div class="cube-value">${this._escape(lqi)} LQI · ${this._escape(battery)}% · ${this._escape(voltage)}mV</div>
              </div>
            </div>
          </div>

          <div class="cube-box cube-time">
            <div class="cube-label">LAST EVENT TIME</div>
            <div class="cube-small">${this._escape(lastTime)}</div>
          </div>

          ${this.config.show_history ? `
            <div class="cube-history">
              <div class="cube-label">HISTORY</div>
              ${historyRows || '<div class="cube-empty">Waiting for the first cube action…</div>'}
            </div>` : ''}

          ${help}
        </div>
      </ha-card>
      <style>${this._styles()}</style>
    `;
  }

  _escape(value) {
    return String(value ?? '—')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  _styles() {
    return `
      ha-card {
        border-radius: 16px;
        padding: 0;
        border: 1px solid rgba(255,255,255,0.14);
        box-shadow: 0 6px 18px rgba(0,0,0,0.22);
        overflow: hidden;
      }
      .cube-card { padding: 12px; }
      .cube-head { display:flex; align-items:center; justify-content:space-between; gap:10px; padding-bottom:8px; }
      .cube-title { font-size:14px; font-weight:800; letter-spacing:0.8px; }
      .cube-sub { margin-top:2px; font-size:11px; opacity:0.65; }
      .cube-count { min-width:52px; padding:6px 8px; border-radius:999px; text-align:center; font-size:13px; font-weight:800; background:rgba(255,255,255,0.10); border:1px solid rgba(255,255,255,0.12); }
      .cube-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
      .cube-box { min-height:54px; padding:9px 10px; border-radius:13px; background:rgba(0,0,0,0.18); border:1px solid rgba(255,255,255,0.10); display:flex; align-items:center; gap:9px; box-sizing:border-box; }
      .cube-main ha-icon { width:24px; height:24px; opacity:0.9; }
      .cube-label { font-size:10px; font-weight:700; opacity:0.58; letter-spacing:0.5px; }
      .cube-value { margin-top:3px; font-size:15px; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%; }
      .cube-small { margin-top:3px; font-size:12px; font-weight:600; opacity:0.85; }
      .cube-time { margin-top:8px; min-height:42px; }
      .cube-history, .cube-help { margin-top:8px; padding:9px 10px; border-radius:13px; background:rgba(0,0,0,0.18); border:1px solid rgba(255,255,255,0.10); }
      .cube-row { margin-top:5px; padding:5px 7px; border-radius:9px; background:rgba(255,255,255,0.055); font-size:12px; font-weight:600; text-align:left; opacity:0.78; }
      .cube-row-last { background:rgba(255,255,255,0.13); opacity:1; }
      .cube-empty { margin-top:6px; font-size:12px; opacity:0.6; text-align:left; }
      .cube-tip { margin-top:5px; font-size:12px; line-height:1.32; opacity:0.82; }
      @media (max-width: 520px) { .cube-grid { grid-template-columns:1fr; } }
    `;
  }
}

if (!customElements.get('aqara-cube-36-debug-card')) {
  customElements.define('aqara-cube-36-debug-card', AqaraCube36DebugCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'aqara-cube-36-debug-card',
  name: 'Aqara Cube 36 Debug Card',
  description: 'Debug and training card for Aqara Cube T1 Pro 36 Actions. Shows action, side, angle, LQI, battery and history.',
  preview: true,
});
