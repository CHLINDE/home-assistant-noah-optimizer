# Third-Party Software and Services

The Home Assistant Growatt NOAH Optimizer interacts with or optionally uses
several third-party projects.

Unless explicitly stated otherwise, these projects are **not bundled,
copied, modified, or redistributed** as part of this repository.

Users install and operate the required third-party components separately.

---

## Home Assistant

The Growatt NOAH Optimizer is a custom integration for Home Assistant.

Home Assistant provides the runtime environment, entity model, configuration
entries, Lovelace dashboard system, services, and other APIs used by this
integration.

Home Assistant is developed independently of this project.

This project is not affiliated with or endorsed by the Home Assistant project
or Nabu Casa.

---

## HACS

HACS (Home Assistant Community Store) can be used to install and update the
Growatt NOAH Optimizer and the optional dashboard cards.

HACS is not bundled with this project and must be installed separately.

This project is not affiliated with or endorsed by the HACS project.

---

## Noah-MQTT

Project:

`mtrossbach/noah-mqtt`

License:

`Apache License 2.0`

Noah-MQTT provides MQTT-based access to Growatt NOAH 2000 data and control
functions and can expose the entities used by the Growatt NOAH Optimizer.

The Growatt NOAH Optimizer does not include or redistribute Noah-MQTT source
code.

Users must install and configure Noah-MQTT separately.

Noah-MQTT is an independent community project.

---

## Forecast.Solar

The optimizer can use the Forecast.Solar integration available in Home
Assistant to obtain the expected remaining photovoltaic production for the
current day.

Forecast.Solar and its Home Assistant integration are not included in this
repository.

The Growatt NOAH Optimizer only reads the configured Home Assistant forecast
entity.

---

## Power Flow Card Plus

Project:

`flixlix/power-flow-card-plus`

Current source project:

`flixlix/flixlix-cards`

Power Flow Card Plus is used by the optional NOAH Optimizer dashboard to
visualize the current energy flow between:

- photovoltaic generation
- grid import and export
- household consumption
- battery charging and discharging

Power Flow Card Plus is **not bundled or redistributed** with the Growatt NOAH
Optimizer.

Users install it separately, typically through HACS.

At the time this notice was written, the current Power Flow Card Plus
distribution repository and source monorepo did not expose an explicit
repository license declaration. Therefore this project does not claim or
assign a license to Power Flow Card Plus.

The copyright and licensing terms of Power Flow Card Plus remain entirely with
its respective authors and contributors.

---

## ApexCharts Card

Project:

`RomRider/apexcharts-card`

License:

`MIT License`

ApexCharts Card is used by the optional NOAH Optimizer dashboard for graphical
history and planning views, including:

- photovoltaic and grid power
- NOAH output power
- battery power and state of charge
- forecast and energy planning
- optimizer target values
- controller behavior

ApexCharts Card is **not bundled or redistributed** with the Growatt NOAH
Optimizer.

Users install it separately, typically through HACS.

ApexCharts Card is an independent project and remains subject to its own
license terms.

---

## Growatt / NOAH 2000

Growatt, NOAH and related product names and trademarks belong to their
respective owners.

The Home Assistant Growatt NOAH Optimizer is an independent community project.

It is not developed, maintained, sponsored, approved, or endorsed by Growatt.

The project uses data and control entities made available to Home Assistant by
separately installed third-party software.

No Growatt firmware, application code, cloud service code, proprietary
protocol implementation, logos, or other Growatt assets are distributed in
this repository.

---

## No bundled third-party code

This repository does not currently contain copied source code from:

- Home Assistant
- HACS
- Noah-MQTT
- Forecast.Solar
- Power Flow Card Plus
- ApexCharts Card

References to these projects in source code or documentation are used only for
integration, interoperability, installation instructions, and attribution.

Each third-party project remains subject to its own copyright and license
terms.

---

## Project license

The Home Assistant Growatt NOAH Optimizer itself is distributed under the
license contained in:

`LICENSE`

This license applies only to code and documentation belonging to this project
and does not replace, modify, or extend the licenses of third-party projects
listed above.