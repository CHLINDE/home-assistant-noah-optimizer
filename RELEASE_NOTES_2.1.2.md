# Growatt NOAH Optimizer 2.1.2

## 2.1.2 – Nachtruhe und nicht verfügbare Messwerte

Wenn der NOAH bei Mindest-SOC nachts erwartungsgemäß abschaltet, zeigt der
Datenstatus **Nachtruhe am Mindest-SOC**. Andere Offline-Ursachen bleiben als
**Stellgröße nicht verfügbar** sichtbar und erzeugen weiterhin die vorgesehene
Benachrichtigung. Es werden in beiden Fällen keine Stellbefehle gesendet und
keine gecachten NOAH-Leistungen für PV-Learning verwendet.

Im automatisch erzeugten Dashboard ersetzen kompakte Hinweiskarten bei
fehlenden Stellwerten die Energieflusskarte und die vier Warn-Gauges. Der
Reglerstatus zeigt dann nur die wesentlichen Angaben. Die vorhandenen
Tageskarten bleiben mit ihrer bisherigen Darstellung erhalten. Ein zuletzt
gemeldeter SOC ist ausdrücklich **kein Live-Wert**. Netzleistung, Netzbezug
und Netzeinspeisung werden unabhängig vom NOAH aus dem konfigurierten
Netzsensor aktualisiert, sofern dieser verfügbar ist.

Die Migration auf Dashboard-Template 22 erfasst erkannte Standardkarten im
integrationseigenen Dashboard. Selbst angelegte Dashboards oder stark
veränderte Karten werden nicht automatisch umgeschrieben.

Basis: `main` `635583735b8a986d87f8525e63695c0bffebaf29`.
