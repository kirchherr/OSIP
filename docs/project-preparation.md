# OSIP Project Preparation

Stand: 2026-06-12

Dieses Dokument ist meine fachliche Vorbereitung fuer die Arbeit an OmniSense Runtime und OSIP. Es uebersetzt `Masterplan.md` in eine Standards-, Forschungs- und Open-Source-Landkarte, damit spaetere Implementierungsschritte wissenschaftlich pruefbar, modular und anschlussfaehig bleiben.

## Lokale Ausgangslage

- Repository enthaelt aktuell `Masterplan.md` als zentrale Leitlinie.
- Projektkern ist OSIP: ein offenes Percept-, Context- und Action-Protokoll.
- Erste technische Prioritaet laut Masterplan: Repository Foundation, OSIP Schemas, In-memory Bus, Scenario Replay, Context Engine v0.1, Decision Runtime v0.1, Gateway API, Benchmark Runner.
- Nicht-Ziele fuer die erste Phase: echte Hardware als Pflicht, monolithische KI, freie autonome Aktionen, Datenschutz-Fokusprojekt, externe LLMs im Reflex Layer.

## Leitthese fuer die Umsetzung

OSIP sollte als offenes, versioniertes Interchange Protocol entstehen, nicht als Python-interne Datenklasse. Die Python-Implementierung ist Referenzruntime; die eigentliche Projektleistung ist die stabile Schnittstelle zwischen spezialisierten Sinnesmodellen, Kontextfusion und begrenzten Aktionen.

Praktische Konsequenz:

- `packages/osip` definiert Semantik und Validierung.
- `protocols/schemas` exportiert maschinenlesbare JSON Schemas.
- `protocols/openapi` beschreibt synchrone HTTP-APIs.
- `protocols/asyncapi` beschreibt Event-Channels.
- Transportadapter duerfen austauschbar bleiben.

## Standards-Stack

### 1. Contract- und Schema-Schicht

**JSON Schema Draft 2020-12**

Nutzen: normative Schema-Sprache fuer OSIP JSON-Dokumente und Contract Tests. Draft 2020-12 ist passend, weil moderne JSON-Schema-Vokabulare, dynamische Referenzen und Bundling vorgesehen sind. Quelle: https://json-schema.org/draft/2020-12

OSIP-Entscheidung:

- JSON Schema als exportiertes Contract-Artefakt verwenden.
- Pydantic v2 als Referenzmodell nutzen, aber JSON Schema als oeffentlichen Vertrag behandeln.
- Dynamische Referenzen sparsam einsetzen, weil sie Validierung und Tooling komplexer machen.

**OpenAPI**

Nutzen: HTTP API Contract fuer Gateway, SDK-Generierung und externe App-Integration. Die aktuell publizierte OpenAPI-Spec ist 3.2.0; fuer den Python/FastAPI-Prototyp sollte OpenAPI 3.1-kompatibel gestartet werden, falls die Toolchain 3.2 noch nicht sauber unterstuetzt. Quelle: https://spec.openapis.org/oas/latest.html

OSIP-Entscheidung:

- Gateway API in OpenAPI 3.1+ beschreiben.
- JSON Schema-Kompatibilitaet aktiv pruefen.
- Keine Semantik nur in Endpoint-Namen verstecken; OSIP Message Types bleiben eigenstaendig.

**AsyncAPI**

Nutzen: maschinenlesbare Beschreibung von Event-Channels und Pub/Sub-Operationen. AsyncAPI 3.1.0 ist protocol-agnostic und passt zu NATS, MQTT, WebSockets und spaeteren Bridges. Quelle: https://www.asyncapi.com/docs/reference/specification/latest

OSIP-Entscheidung:

- `omnisense.percepts.<modality>.<model_id>` und weitere Topics als AsyncAPI Channels modellieren.
- Sender- und Receiver-Operationen getrennt beschreiben.
- Bindings erst hinzufuegen, wenn NATS/MQTT konkret implementiert sind.

**CloudEvents**

Nutzen: optionaler Event Envelope fuer Interoperabilitaet ueber Broker und Cloud-native Tools hinweg. CloudEvents v1.0.2 bietet Core-Spec und Bindings unter anderem fuer HTTP, Kafka, MQTT und NATS. Quelle: https://github.com/cloudevents/spec

OSIP-Entscheidung:

- OSIP Messages bleiben eigenstaendig validierbar.
- CloudEvents kann als Envelope-Adapter kommen, nicht als Pflicht fuer In-memory Tests.
- Mapping: `id`, `source`, `type`, `time`, `datacontenttype`, `data`.

### 2. Event- und Realtime-Transport

**In-memory Bus**

Nutzen: deterministische Unit- und Integrationstests ohne externe Dienste.

OSIP-Entscheidung:

- Phase 1/2 immer in-memory lauffaehig halten.
- Kein Core-Test darf NATS, MQTT oder Netzwerk benoetigen.

**NATS**

Nutzen: leichtgewichtige, schnelle Subject-basierte Messaging-Infrastruktur fuer lokale Demos, Edge und Command-and-Control. NATS beschreibt sich als connective technology fuer moderne verteilte Systeme und IoT/Edge Use Cases. Quelle: https://docs.nats.io/nats-concepts/overview

OSIP-Entscheidung:

- NATS als empfohlener Demo-Broker.
- JetStream erst fuer Replay/Persistenz pruefen; nicht in den Reflex Fast Path legen.
- Subject-Konventionen aus Masterplan beibehalten.

**MQTT 5**

Nutzen: IoT-kompatible Pub/Sub Bridge fuer Sensoren, Aktoren und bestehende Smart-Home-Systeme. MQTT 5 ist OASIS Standard. Quelle: https://mqtt.org/mqtt-specification/

OSIP-Entscheidung:

- MQTT als Bridge, nicht als semantischer Kern.
- OSIP Payloads bleiben JSON und schema-validiert.
- MQTT Topics werden aus OSIP/AsyncAPI Topics abgeleitet.

**ROS 2 / DDS**

Nutzen: spaeterer Robotik- und Echtzeit-Hardware-Adapter. DDS definiert Data-Centric Publish-Subscribe mit QoS fuer effiziente Lieferung der richtigen Information zur richtigen Zeit; ROS 2 nutzt austauschbare RMW-Implementierungen, damit die Codebasis nicht an eine Middleware gebunden ist. Quellen: https://www.omg.org/spec/DDS/ und https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Different-Middleware-Vendors.html

OSIP-Entscheidung:

- ROS 2 Adapter erst nach MVP.
- QoS-Profile als Adapterkonfiguration, nicht im OSIP Core.
- OSIP-Temporalitaet (`timestamp`, `received_at`, `valid_for_ms`, `latency_ms`) muss fuer DDS-Adapter sauber bleiben.

### 3. Sensor-, Aktor- und Smart-Building-Semantik

**W3C Web of Things Thing Description 1.1**

Nutzen: offene Beschreibung von IoT Things mit Properties, Actions und Events, inklusive Security-Metadaten und JSON/JSON-LD. Quelle: https://www.w3.org/TR/wot-thing-description11/

OSIP-Entscheidung:

- Action Contracts sollten spaeter in WoT Action Affordances abbildbar sein.
- Sensor-/Aktormetadaten koennen als WoT Thing Description exportiert werden.
- OSIP bleibt leichter als WoT, aber anschlussfaehig.

**W3C/OGC SOSA/SSN**

Nutzen: Ontologie fuer Sensors, Observations, Samples und Actuators. SOSA ist der leichte Kern; SSN ist ausdrucksstaerker. Quelle: https://www.w3.org/TR/vocab-ssn/

OSIP-Entscheidung:

- OSIP-Felder auf SOSA-Begriffe mappen: source sensor/model, observation/percept, observed property/claim, actuator/action.
- Kein RDF-Zwang im MVP.
- Semantische Export- oder Mapping-Datei spaeter als Forschungsartefakt.

**OGC SensorThings API**

Nutzen: offener Web-Standard fuer IoT Sensing mit Things, Locations, Datastreams, Sensors, ObservedProperties, Observations und FeaturesOfInterest. Quelle: https://docs.ogc.org/is/18-088/18-088.html

OSIP-Entscheidung:

- Gute Referenz fuer Sensorhistorie und Datastreams.
- Nicht direkt als Fast Path nutzen, da REST/OData-Historienmodell nicht zur Reflex-Latenz passt.
- Adapter/export fuer SensorThings kann spaeter Forschung und Interoperabilitaet staerken.

**Brick Schema**

Nutzen: open-source Semantik fuer physische, logische und virtuelle Assets in Gebaeuden und deren Beziehungen. Quelle: https://brickschema.org/

OSIP-Entscheidung:

- Fuer Raum-, HVAC-, Licht-, Sicherheits- und Gebaeude-Assets bevorzugt Brick-kompatible Begriffe pruefen.
- OSIP Claim Labels bleiben kurz und maschinenlesbar; Brick kann als Mapping-Schicht dienen.
- Damit bleibt OSIP leicht, aber Smart-Building-kompatibel.

### 4. Observability und Messbarkeit

**OpenTelemetry**

Nutzen: vendor-neutrales Framework fuer Traces, Metrics und Logs. Quelle: https://opentelemetry.io/docs/what-is-opentelemetry/

OSIP-Entscheidung:

- Latenzpfade mit Spans/Events instrumentieren.
- Correlation IDs aus OSIP IDs und idempotency keys ableiten.
- Keine schwere Telemetrie im Reflex-Pfad blockierend exportieren.

**Prometheus / OpenMetrics**

Nutzen: einfache Metrik-Exposition fuer p50/p95/p99, Fehlerraten und Contract-Blocks. Prometheus unterstuetzt textbasierte Formate und OpenMetrics als standardisierte Metric-Wire-Format-Richtung. Quelle: https://prometheus.io/docs/instrumenting/exposition_formats/

OSIP-Entscheidung:

- `/metrics` frueh vorsehen.
- Metriken aus Masterplan direkt abbilden: `p95_context_latency_ms`, `action_contract_blocks`, `sensor_dropout_survival_rate`.
- Histogramme fuer Latenzen statt nur Durchschnittswerte.

## Wissenschaftliche Arbeitsweise

### Reproduzierbarkeit

OSIP muss als Forschungsartefakt reproduzierbar sein. FAIR fordert auffindbare, zugaengliche, interoperable und wiederverwendbare Daten/Metadaten, mit persistenten IDs, standardisierten Protokollen, klaren Lizenzen und Provenance. Quelle: https://www.go-fair.org/fair-principles/

Konkrete Regeln:

- Jede Demo braucht ein versioniertes Szenario.
- Benchmark-Ausgabe als JSON plus Markdown.
- Jede Messung enthaelt Git-Commit, Schema-Version, Szenarioname, Seed, Runtime-Konfiguration und Hardware/OS-Hinweis.
- Rohdaten der Reports bleiben maschinenlesbar.

### Artifact Review

ACM Artifact Badging trennt unter anderem verfuegbare Artefakte, evaluierte Artefakte und reproduzierte/replicierte Ergebnisse. Quelle: https://www.acm.org/publications/policies/artifact-review-and-badging-current

OSIP-Zielbild:

- MVP so bauen, dass ein externer Reviewer die Demo ohne Hardware ausfuehren kann.
- Scripts fuer Setup, Szenario-Replay und Benchmark bereitstellen.
- Erwartete Ergebnisse als toleranzbasierte Checks, nicht als fragile exakte Laufzeitwerte.

### Sensor Fusion

Fachlicher Rahmen:

- Multisensor Fusion unterscheidet grob Signal-/Feature-/Entity-Fusion, Situation Assessment und Impact/Decision-Ebenen. Das passt direkt zur OSIP-Pipeline Percept -> Context -> Decision.
- JDL/DFIG ist als Strukturmodell nuetzlich, aber nicht als starre Pipeline zu verstehen. OSIP sollte asynchron, fensterbasiert und widerspruchsfaehig bleiben.
- Unsicherheit muss explizit modelliert werden: confidence, quality, latency, valid_for_ms, evidence und contradictions sind Kernfelder.

Quellenanker:

- Hall, D. L. und Llinas, J., "An introduction to multisensor data fusion", Proceedings of the IEEE, 1997. DOI: https://doi.org/10.1109/5.554205
- Dempster-Shafer/Evidence Theory ist relevant fuer widerspruechliche Evidenz, aber im MVP reicht eine transparente gewichtete Fusion mit Evidence/Contradictions. Weiterfuehrend: https://arxiv.org/abs/1106.3876

### Kontextmodellierung

Context Awareness betrachtet Kontext als Information zur Charakterisierung der Situation einer Entitaet. Fuer OSIP heisst das: Raum, Zone, Entitaet, Zeitfenster, Evidenz, Widerspruch, Dringlichkeit und erlaubte Aktionen sind explizit zu modellieren.

Quellenanker:

- Dey, A. K., "Understanding and Using Context", Personal and Ubiquitous Computing, 2001. DOI: https://doi.org/10.1007/s007790170019
- W3C/OGC SOSA/SSN fuer Observation/Actuation-Begriffe: https://www.w3.org/TR/vocab-ssn/

### Confidence Calibration

Modellkonfidenz darf nicht blind als Wahrscheinlichkeit behandelt werden. Moderne neuronale Modelle koennen fehlkalibriert sein; deshalb ist `confidence_calibrated` im Masterplan wichtig. Quelle: https://arxiv.org/abs/1706.04599

OSIP-Regeln:

- `confidence` ist Claim-Level, nicht Paket-Level.
- Capability Descriptor muss angeben, ob Confidence kalibriert ist.
- Context Engine darf unkalibrierte Konfidenzen niedriger gewichten oder pro Modell kalibrieren.
- Benchmarks muessen False Positive und False Negative Rates ausweisen.

## Open-Source- und Governance-Leitplanken

**Open Source Definition**

Open Source ist mehr als Source-Zugang; Lizenzen muessen freie Weitergabe, Source Code, abgeleitete Werke und Nichtdiskriminierung ermoeglichen. Quelle: https://opensource.org/osd

OSIP-Entscheidung:

- Vor Public Release eine OSI-konforme Lizenz waehlen.
- Fuer breite Industrieadoption ist Apache-2.0 oft passend, weil Patentlizenz und permissive Nutzung gut zu Standards passen. Final entscheiden, wenn Projektstrategie klar ist.

**REUSE / SPDX**

REUSE definiert maschinenlesbare Copyright- und Lizenzinformationen pro Datei, basierend auf SPDX. Quelle: https://reuse.software/spec-3.3/

OSIP-Entscheidung:

- Spaetestens vor externer Veroeffentlichung REUSE-kompatible Lizenzdateien und SPDX Header/REUSE.toml einrichten.
- Generated Schemas und Beispiele klar lizenzieren.

**SLSA**

SLSA beschreibt inkrementelle Supply-Chain-Sicherheitsgarantien mit Levels, Provenance und Attestations. Quelle: https://slsa.dev/spec/v1.2/

OSIP-Entscheidung:

- Nach Foundation CI mit pinned actions/dependencies aufbauen.
- Spaeter Build Provenance fuer Releases planen.
- Kein Release ohne reproduzierbare Tests und dokumentierten Build.

**OpenSSF Scorecard**

OpenSSF Scorecard bewertet Open-Source-Projekte anhand automatisierter Security Checks fuer Code, Build, Dependencies, Tests und Maintenance. Quelle: https://scorecard.dev/

OSIP-Entscheidung:

- Vor Public Launch Scorecard als Readiness-Check verwenden.
- Security Policy, License, CI Tests, Dependency Updates, Branch Protection und pinned dependencies frueh einplanen.

## Interface-Entscheidungen fuer OSIP v0.1

### Message Types

OSIP v0.1 sollte mindestens enthalten:

- `model.capability`
- `percept.packet`
- `context.update`
- `event.detected`
- `action.contract`
- `action.proposal`
- `action.command`
- `action.result`

### Envelope

Empfehlung:

- OSIP-interner Envelope bleibt schlank und schema-versioniert.
- Optionaler CloudEvents Envelope wird als Adapter implementiert.
- Keine harte CloudEvents-Pflicht fuer In-memory Bus oder Fixtures.

### Time Semantics

Pflichtfelder:

- `timestamp`: Zeitpunkt der Beobachtung/Erzeugung beim Modell.
- `received_at`: Zeitpunkt des Runtime-Eingangs, sobald vorhanden.
- `valid_for_ms`: Gueltigkeitsfenster fuer Fusion.
- `latency_ms`: Modell- oder Adapterlatenz.

Testpflicht:

- verspaetete Percepts
- doppelte Percepts
- `valid_for_ms` abgelaufen
- widerspruechliche Percepts im selben Fenster

### Confidence und Quality

Pflichtfelder:

- Claim-Level `confidence`.
- Paket- oder Sensorqualitaet mit Status wie `usable`, `degraded`, `unusable`.
- Optional `drift_score`.
- Capability-Level `confidence_calibrated`.

Regel:

- Context Engine muss Evidence und Contradictions ausgeben, nicht nur Endlabel.

### Actions

Pflichtkonzept:

- Keine ActionProposal ohne ActionContract.
- Contract prueft allowed contexts, min confidence, preconditions, max decision latency, cooldown, idempotency und rollback/safe state.
- Risk class muss vorhanden sein.

## Forschungsfragen als Backlog-Leitplanken

Kurzfristig:

- Welche OSIP-Felder sind wirklich minimal fuer PerceptPacket v0.1?
- Wie lassen sich Confidence, Quality und Latency transparent in einen ersten Fusion Score einbringen?
- Welche Negative Tests verhindern Semantikdrift bei Labels?
- Wie messen wir End-to-End-Latenz ohne echte Hardware fair?

Mittelfristig:

- Wann lohnt sich CloudEvents Envelope verbindlich?
- Wann reicht Brick-Mapping, wann braucht OSIP eigenes Raum-/Asset-Vokabular?
- Wie wird Modellkonfidenz kalibriert oder modellweise normalisiert?
- Wie verhindert man Label-Chaos bei Drittmodellen?

Spaeter:

- Learned Fusion vs. regelbasierte Fusion.
- DDS/ROS 2 QoS-Mapping.
- SensorThings/SSN/RDF Export.
- OPA/Rego oder aehnliche Policy Engine fuer komplexere Action Contracts, sofern der Fast Path nicht blockiert.

## Praktische Vorbereitung fuer kommende Tasks

Wenn eine Implementierungsaufgabe startet:

1. Masterplan und `AGENTS.md` lesen.
2. Phase bestimmen.
3. Public Contract zuerst skizzieren.
4. Fixture fuer ein gueltiges und ein ungueltiges Beispiel anlegen.
5. Tests fuer Validierung und Semantik schreiben.
6. Erst dann Runtime-Logik bauen.
7. Falls ein externer Standard betroffen ist, Quelle im Doc oder Spec-Kommentar verlinken.
8. Check ausfuehren und Ergebnis dokumentieren.

## Empfohlene erste Umsetzung

Naechster sinnvoller Schritt ist "Repository Foundation":

- `README.md`
- `pyproject.toml`
- `Makefile`
- `docs/architecture.md`
- `docs/osip-spec.md`
- `packages/osip`
- `tests/`
- minimale Toolchain mit `pytest`, `ruff`, Typpruefung vorbereitet

Danach direkt "OSIP Schemas":

- Pydantic v2 Modelle
- JSON Schema Export
- Fixtures
- positive und negative Contract Tests
- erstes Vocabulary-Modul

Damit entsteht die richtige Basis: offene Schnittstelle zuerst, Referenzruntime danach.
