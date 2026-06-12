# OSIP Project Preparation

Stand: 2026-06-12

Dieses Dokument ist meine fachliche Vorbereitung fuer die Arbeit an OmniSense Runtime und OSIP. Es uebersetzt `Masterplan.md` in eine Standards-, Forschungs- und Open-Source-Landkarte, damit spaetere Implementierungsschritte wissenschaftlich pruefbar, modular und anschlussfaehig bleiben.

## Lokale Ausgangslage

- Repository enthaelt aktuell `Masterplan.md` als zentrale Leitlinie.
- Projektkern ist OSIP: ein offenes Percept-, Context- und Action-Protokoll.
- Erste technische Prioritaet laut Masterplan: Repository Foundation, OSIP Schemas, In-memory Bus, Scenario Replay, Context Engine v0.1, Decision Runtime v0.1, Gateway API, Benchmark Runner.
- Neue Konzeptprioritaet: Experience & Learning Layer als kontrollierter Weg von Runtime-Traces zu Datensaetzen, Kalibrierung, Modellbewertung und spaeterer Modellpromotion.
- Neue Autonomieprioritaet: Goal Generation Engine als kontrollierte Schicht fuer Surprise, epistemischen Wert und digitale Homoeostase, ohne direkte Aktionsautoritaet.
- Nicht-Ziele fuer die erste Phase: echte Hardware als Pflicht, monolithische KI, freie autonome Aktionen, Datenschutz-Fokusprojekt, externe LLMs im Reflex Layer.

## Leitthese fuer die Umsetzung

OSIP sollte als offenes, versioniertes Interchange Protocol entstehen, nicht als Python-interne Datenklasse. Die Python-Implementierung ist Referenzruntime; die eigentliche Projektleistung ist die stabile Schnittstelle zwischen spezialisierten Sinnesmodellen, Kontextfusion und begrenzten Aktionen.

Erweiterte Leitthese:

OSIP ist ein generisches Perception-to-Action-Protokoll mit einem domain-neutralen Core und andockbaren Application Profiles. Der Smart-Room-MVP beweist die Pipeline im Profil `rooms`; dieselbe Architektur muss spaeter das Profil `physical-ai` und neue Profile wie `xxx` tragen koennen.

OSIP soll zusaetzlich als Experience-to-Learning-System vorbereitet werden: Entscheidungen, Actions, Results und Outcomes werden nicht nur geloggt, sondern mit Provenance, Schema-Versionen, Modellfaehigkeiten und Benchmark-Kontext so strukturiert, dass daraus spaeter reproduzierbare Lernbeispiele entstehen.

OSIP soll ausserdem emergente Autonomie vorbereiten: Das System darf aus Surprise, Unsicherheit und Systemgesundheit Zielhypothesen generieren, aber diese Ziele bleiben `goal.packet`-Kandidaten und muessen durch Profile, Policies, Simulation, Benchmarks und Action Contracts begrenzt werden.

Praktische Konsequenz:

- `packages/osip` definiert Semantik und Validierung.
- `protocols/schemas` exportiert maschinenlesbare JSON Schemas.
- `protocols/openapi` beschreibt synchrone HTTP-APIs.
- `protocols/asyncapi` beschreibt Event-Channels und Pub/Sub-Operationen.
- Transportadapter duerfen austauschbar bleiben.
- Physical-AI-Erweiterungen gehoeren zuerst in Vocabulary, Schemas, Simulatoren, Benchmarks und Adapter-Designs, nicht in direkte Hardwaresteuerung.
- Learning-Erweiterungen gehoeren zuerst in Trace-, Dataset-, Model-Card-, Registry- und Benchmark-Vertraege, nicht in selbstveraendernde Runtime-Logik.
- Autonomie-Erweiterungen gehoeren zuerst in `goal.packet`, Goal-to-Contract-Mapping, Negative Tests, Simulation und Review-Status, nicht in freie Zielausfuehrung.

## Application-Profile-Modell

OSIP wird in Core und Profile getrennt:

- **OSIP Core**: versionierte Message-Typen, Validierung, Claims, Context Updates, Action Contracts, Topic-Regeln, Replay, Benchmarks, Unsicherheit, Evidenz und Safety-Boundary-Prinzipien.
- **Application Profile `rooms`**: Smart Rooms, Gebaeude, Ambient Sensing, HVAC, Licht, Speaker, Komfort, Sicherheit und Brick/WoT/SOSA-Mapping.
- **Application Profile `physical-ai`**: Robotik, Embodied AI, autonome Systeme, 3D-Weltmodelle, Propriozeption, Manipulation, Navigation, Simulatoren, Sim2Real und Safety Bounds.
- **Application Profile `xxx`**: bewusstes Andockmuster fuer neue Domaenen. Neue Anwendungen starten als Profil mit eigener Doku, Fixtures, Szenarien und Tests.

Promotion-Regel:

- Ein Konzept bleibt im Profil, solange es nur einer Anwendung dient.
- Ein Konzept darf erst in OSIP Core wandern, wenn mindestens zwei Profile es brauchen und es transport-/vendor-neutral formuliert werden kann.

## Experience-&-Learning-Modell

OSIP trennt Live-Entscheidung und Lernen:

- **Runtime**: Percepts, Context Updates, Decisions, Actions und Results laufen ueber validierte OSIP-Vertraege und Action Contracts.
- **Experience Trace**: relevante Ereignisse werden als nachvollziehbare Kette gespeichert: `PerceptPacket -> ContextUpdate -> ActionProposal -> ActionCommand -> ActionResult -> Outcome`.
- **Decision Trace / Experience Tuple**: jede Aktion wird als `State_t + ActionContract_t + PostActionPercepts_t+delta -> Outcome_t+delta -> RewardSignal_t+delta` auswertbar. Die post-action Percepts werden ueber Trace-ID, Action-ID, Feedback-Fenster, Profil, Szenario und Modellversion mit der Aktion verbunden.
- **Dataset Layer**: Traces werden offline zu Beispielen, Labels, Splits, Features, Hashes und Datasheets verdichtet.
- **Learning Layer**: Modelle werden offline trainiert, kalibriert oder evaluiert.
- **Registry/Promotion Layer**: Modelle werden nur mit Model Card, Benchmark Pass, Shadow Mode, Rollback und explizitem Approval nutzbar.

Learning-Regeln:

- Kein Training, Registry-Zugriff oder Modellpromotion im Reflex/Fast Path.
- Kein gelerntes Modell darf Action Contracts, Preconditions, Bounds, Safe States, Cooldowns oder Idempotency umgehen.
- OSIP Core enthaelt nur generische Lern-Vertraege; Profile definieren Outcome-Labels, Datenschutz/Retention, Metriken und Safety Cases.
- Reale Daten brauchen vor Export oder Training explizite Regeln fuer Zustimmung, Pseudonymisierung, Aufbewahrung, Lizenz und Loeschung.
- Feedbackdaten sind reichhaltig, aber nicht automatisch wahr: Reward-Signale muessen Delay, Leakage, Konfundierung, Sensor-Bias, Zielkonflikte und Profilwechsel sichtbar machen.

Modellfamilien aus Experience Tuples:

- **Knowledge Distillation**: langsamere Deliberative-Entscheidungen, Ensembles oder human-reviewte Traces dienen als Teacher fuer kleine Student-Modelle. Ziel ist Reflex-Beschleunigung bei gleichbleibender Contract-Beschraenkung.
- **Predictive World Models**: Modelle lernen, welche Percepts oder Contexts nach `State_t + ActionContract_t` wahrscheinlich entstehen. Ziel ist Action-Dry-Run, Szenarioerweiterung und Sim2Real-Gap-Analyse.
- **Inverse Reinforcement Learning / Reward Models**: Historische erfolgreiche Aktionen, geblockte Aktionen und explizites Feedback liefern Kandidaten fuer Komfort-, Sicherheits-, Energie- oder Manipulationsziele. Diese Rewards sind pruefbare Hypothesen und brauchen Review.

## Emergent-Autonomy-Modell

OSIP trennt Zielgenerierung und Zielausfuehrung:

- **Context / World Model**: liefert beobachteten Zustand, Unsicherheit, Evidenz, Widersprueche und spaeter Vorhersagemetadaten.
- **Goal Generation Engine**: berechnet Surprise-/Prediction-Error-, Epistemic-Value- und Homeostatic-Scores.
- **GoalPacket Layer**: erzeugt auditierbare Zielhypothesen mit Kontextbezug, Score-Begruendung, Ablaufzeit, Safety-Klasse, erlaubten/verbotenen Contract-Klassen und Review-Status.
- **Decision Runtime**: uebersetzt Goals nur dann in `ActionProposal`, wenn ein registrierter Action Contract, passende Preconditions, Profilfreigabe und Safety-Gates existieren.

Autonomie-Regeln:

- Surprise erzeugt zuerst Untersuchungsziele, nicht automatische Weltkorrektur.
- Epistemische Ziele duerfen Sensordaten, Blickwinkel, Sampling oder Rueckfragen verbessern, aber nicht heimlich riskante Aktionen starten.
- Digitale Homoeostase darf Sensor-/Systemgesundheit sichern, aber niemals menschliche Sicherheit, Profilregeln oder Not-Aus/Safe-State-Pfade ueberstimmen.
- Kein `goal.packet` ist eine Permission. Ohne Contract wird das Ziel verworfen oder in sichere Informations-Subgoals zerlegt.
- Praeferenzrahmen und Prioritaeten gehoeren in Application Profiles und Safety Cases; sie duerfen nicht als versteckte Werte in Modellen oder Heuristiken liegen.

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

### 2.1 Physical AI, Simulation und Robotik

**Physical AI / Embodied AI**

Nutzen: OSIPs Perception -> Context -> Action Loop entspricht dem Grundmuster robotischer und autonomer Systeme. Sensoren und Modelle liefern Wahrnehmungen, eine Fusion-Schicht erzeugt ein Weltmodell, und Actions duerfen nur innerhalb harter Safety- und Contract-Grenzen wirken.

OSIP-Entscheidung:

- Smart Rooms bleiben der erste lauffaehige Demonstrator.
- Physical AI wird als Erweiterungspfad gefuehrt: Robot State, 3D Pose, Transform Frames, Joint States, Wrench/Tactile Claims, Workspace Bounds, Manipulation, Navigation und Safety Events.
- Kontinuierliche oder hochfrequente Regelkreise gehoeren nicht in OSIP Core. OSIP beschreibt Contracts, Bounds, Kommandos, Ergebnisse und Evidenz; harte Realtime-Control bleibt in spezialisierten Controllern oder Adaptern.

**ROS 2 QoS / DDS**

Nutzen: Physical-AI-Systeme muessen Latenz, Zuverlaessigkeit, Durability, History und Deadline-Verhalten bewusst konfigurieren. ROS 2 beschreibt QoS-Policies fuer Publisher/Subscriber, Services und Actions. Quelle: https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html

OSIP-Entscheidung:

- QoS ist Transport-/Adapterkonfiguration, nicht OSIP-Semantik.
- OSIP-Payloads bleiben brokerunabhaengig validierbar.
- Adapter muessen Topic-, Timing-, Deadline- und Dropout-Informationen in Benchmarks sichtbar machen.
- AsyncAPI exportiert QoS-Intent als `x-osip-qos`, damit DDS, ROS 2, MQTT oder
  NATS spaeter konsistent gemappt werden koennen.

**URDF / SDF / OpenUSD**

Nutzen: Robotik und Simulation brauchen maschinenlesbare Beschreibungen von Robotern, Sensoren, Gelenken, Links, Weltgeometrie, Materialien und Szenen. ROS 2 nutzt URDF fuer Robotermodelle; SDFormat beschreibt Roboter- und Simulationswelten; OpenUSD ist ein verbreitetes Szenenformat in modernen Simulationspipelines. Quellen: https://docs.ros.org/en/rolling/Tutorials/Intermediate/URDF/URDF-Main.html, https://sdformat.org/spec und https://openusd.org/release/index.html

OSIP-Entscheidung:

- OSIP referenziert Frames, Posen, Sensoren, Roboterteile und Weltobjekte ueber stabile IDs.
- Robot-/World-Description-Dateien bleiben externe Artefakte mit Version/Hash in Szenarien oder Benchmarks.
- Kein RDF-, USD-, URDF- oder SDF-Zwang im OSIP Core.

**MuJoCo, Gazebo, Isaac Sim, PyBullet**

Nutzen: Simulation ist der sichere Entwicklungsraum fuer Physical AI. MuJoCo ist ein Physik-Engine- und Modellformat fuer Robotik/Biomechanik/Graphics Research; Gazebo/SDF ist im ROS-Umfeld verbreitet; Isaac Sim nutzt NVIDIA Omniverse/OpenUSD fuer Robotiksimulation; PyBullet ist ein leichter Python-naher Simulator. Quellen: https://mujoco.readthedocs.io/en/stable/overview.html, https://gazebosim.org/docs/latest/getstarted/, https://docs.isaacsim.omniverse.nvidia.com/latest/index.html und https://pybullet.org/wordpress/

OSIP-Entscheidung:

- Simulatoren sind Adapter und Testumgebungen, keine Core-Abhaengigkeiten.
- Szenarien muessen deterministische Seeds, Simulatorversion, Robot/World Description, Sensor Noise Model und Domain-Randomization-Parameter dokumentieren.
- Sim2Real-Reports muessen zeigen, welche Annahmen nur in Simulation gelten und welche Contracts auf echter Hardware durch Safety Controller abgesichert werden.

**Robot Safety / Functional Safety**

Nutzen: Physical AI braucht Safety-by-Design. Relevante Designanker sind Robotersicherheit fuer industrielle Roboter, kollaborative Robotik, funktionale Sicherheit und Automotive-Safety-Denken. Quellen: https://www.iso.org/ics/25.040.30/x/, https://www.iso.org/standard/62996.html, https://www.iec.ch/functionalsafety/ und https://www.iso.org/standard/68383.html

OSIP-Entscheidung:

- OSIP darf keine Zertifizierung behaupten, aber Safety Cases vorbereiten.
- Action Contracts fuer physische Aktoren brauchen Preconditions, Workspace Bounds, Velocity/Force/Rate Limits, Deadlines, Stop Conditions, Safe State, Rollback/Fallback und Audit Trail.
- Benchmarks muessen Action-Contract-Blocks, Bound Violations, Emergency-Stop-Pfade und Latenz-Jitter erfassen.

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

### 5. Experience Learning und MLOps

**W3C PROV**

Nutzen: PROV modelliert Herkunft, Ableitung, Aktivitaeten und beteiligte Entitaeten, damit Datenqualitaet, Zuverlaessigkeit und Vertrauen bewertet werden koennen. Quelle: https://www.w3.org/TR/prov-overview/

OSIP-Entscheidung:

- Jeder Experience Trace muss Quelle, Schema-Version, Profil, Szenario, Modellfaehigkeiten, Zeitschnitt und abgeleitete Beispiele nachvollziehbar verknuepfen.
- Dataset- und Modellartefakte muessen auf ihre Ursprungstraces und Feature-Extraktionsversion zurueckfuehrbar sein.

**OpenLineage**

Nutzen: OpenLineage ist ein offener Rahmen fuer Lineage-Erfassung und -Analyse mit Dataset-, Job- und Run-Entitaeten sowie erweiterbaren Facets. Quelle: https://openlineage.io/docs/

OSIP-Entscheidung:

- Learning-Pipelines koennen spaeter OpenLineage-kompatible Events fuer Dataset-Erzeugung, Feature-Extraktion, Training und Evaluation emittieren.
- OSIP-spezifische Facets sollten Profil, Szenario, Schema-Version, Action-Contract-Version und Benchmark-Gate erfassen.

**MLflow Model Registry Konzepte**

Nutzen: Eine Model Registry verwaltet Modellversionen, Lifecycle, Lineage, Aliase, Tags und Metadaten vom Experiment bis zur Produktion. Quelle: https://mlflow.org/docs/latest/ml/model-registry/

OSIP-Entscheidung:

- OSIP soll kein Registry-Produkt fest verdrahten, aber Registry-Konzepte als offenen Vertrag vorbereiten: Modellversion, Approval State, Alias, Rollback Target, Benchmark Gate und Deployment Constraints.
- Runtime darf nur explizit freigegebene, versionierte Modelle referenzieren.

**Model Cards und Datasheets for Datasets**

Nutzen: Model Cards dokumentieren intendierte Nutzung, Leistungscharakteristika, Evaluationsverfahren und Grenzen von Modellen; Datasheets dokumentieren Motivation, Zusammensetzung, Sammlung, empfohlene Nutzung und Grenzen von Datensaetzen. Quellen: https://arxiv.org/abs/1810.03993 und https://arxiv.org/abs/1803.09010

OSIP-Entscheidung:

- Jeder gelernte OSIP-Modellkandidat braucht vor Promotion eine Model Card.
- Jeder aus OSIP-Traces erzeugte Trainings- oder Evaluationsdatensatz braucht ein Datasheet.
- Karten und Datasheets muessen Profil, Szenarien, Benchmarks, bekannte Fehlerfaelle und nicht unterstuetzte Nutzungen nennen.

**NIST AI Risk Management Framework**

Nutzen: Das AI RMF bietet einen freiwilligen Rahmen fuer vertrauenswuerdige AI-Risikobetrachtung in Design, Entwicklung, Nutzung und Evaluation. Quelle: https://www.nist.gov/itl/ai-risk-management-framework

OSIP-Entscheidung:

- Learning-Funktionen werden als risikobehaftete Systemaenderungen behandelt, nicht als reine Optimierung.
- Promotion-Gates muessen bekannte Fehlerfaelle, Unsicherheit, Monitoring, Rollback und Safety-Bounds sichtbar machen.

**Knowledge Distillation**

Nutzen: Teacher-Student-Lernen kann grosse oder langsame Modelle in kleinere Modelle komprimieren und eignet sich deshalb fuer OSIPs Idee, Deliberative-Entscheidungen in Reflex-nahe Modelle zu destillieren. Quelle: https://arxiv.org/abs/1503.02531

OSIP-Entscheidung:

- Distillation darf nur fuer eng definierte Claims, Contract-Ranking oder Vorfilter starten.
- Student-Modelle muessen gegen harte Negativszenarien, Latenzbudget und Teacher-Version evaluiert werden.
- Student-Modelle duerfen keine neuen Actions oder Bounds einfuehren.

**Predictive World Models**

Nutzen: World Models lernen interne Vorhersagemodelle der Umgebung und koennen zukuenftige Zustandsfolgen fuer Planung oder Simulation bereitstellen. Quelle: https://arxiv.org/abs/1803.10122

OSIP-Entscheidung:

- World Models sagen zukuenftige Percepts/Contexts mit Unsicherheit und Horizont voraus.
- Sie duerfen Action-Auswahl beraten, aber nicht allein Aktionen ausfuehren oder Contracts erweitern.
- Bewertung erfolgt horizon-spezifisch: Kurzfrist-Fehler, Kalibrierung, Rare Events, Safety False Negatives und Sim2Real-Gap.

**Inverse Reinforcement Learning / Reward Learning**

Nutzen: IRL kann aus beobachtetem Verhalten Kandidaten fuer die zugrunde liegende Reward-Funktion ableiten, wenn Ziele wie Komfort oder Wohlbefinden schwer direkt zu formulieren sind. Quelle: https://ai.stanford.edu/~ang/papers/icml00-irl.pdf

OSIP-Entscheidung:

- Gelernte Rewards sind Hypothesen, keine automatische Wahrheit.
- Reward-Modelle brauchen menschliche oder profilverantwortliche Review, bevor gegen sie optimiert wird.
- Transfer in andere Raeume, Roboter oder Profile braucht Drift- und Validierungsberichte.

**Active Inference / Expected Free Energy**

Nutzen: Active Inference formuliert Wahrnehmung und Handlung als Inferenz unter Unsicherheit. Expected Free Energy verbindet Zielerreichung mit epistemischen Anteilen wie Informationsgewinn und Ambiguitaetsreduktion. Quellen: https://arxiv.org/abs/2004.08128 und https://arxiv.org/abs/2109.00541

OSIP-Entscheidung:

- OSIP nutzt Active Inference als Forschungsanker fuer Goal Generation, nicht als Behauptung biologischer Allgemeingueltigkeit.
- Surprise und Expected-Free-Energy-artige Scores werden als transparente Diagnostik und Goal-Hypothesen modelliert.
- Ziele duerfen nur durch Action Contracts, Profile und Benchmarks wirksam werden.

**Intrinsic Motivation**

Nutzen: Intrinsische Motivationen beschreiben Informationssuche, Neugier und andere nicht rein externe Reward-Signale im Perception-Action Loop. Quelle: https://arxiv.org/abs/1806.08083

OSIP-Entscheidung:

- Epistemische Ziele werden auf messbare Unsicherheit, Widerspruch und erwarteten Informationsgewinn begrenzt.
- Explorative Aktionen brauchen engere Bounds als reaktive Sicherheitsaktionen.
- Human confirmation ist ein valider epistemischer Action Contract, wenn Sensorik nicht ausreicht.

**Digital Homeostasis / Allostatic Control**

Nutzen: Homeostase und Allostase liefern ein Vorbild fuer Systemgesundheit und vorausschauende Stabilisierung. In OSIP wird das nicht biologisiert, sondern als Sensor-, Aktor-, Modell- und Runtime-Health umgesetzt.

OSIP-Entscheidung:

- Homeostatic Goals duerfen Wartung, Kalibrierung, Lastreduktion oder Fallbacks vorschlagen.
- Systemerhalt bleibt nachrangig gegen Menschen, Safety Cases und Profilprioritaeten.
- Health-Goals brauchen Audit Trails, weil sie sonst leicht zu versteckter Selbstpriorisierung werden.

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

### Sim2Real und Physical-AI-Benchmarking

Physical-AI-Experimente muessen beweisen, dass Verhalten nicht nur in einer Demo plausibel aussieht, sondern unter Sensorrauschen, Latenz, Dropout, Kollisionen, Domain Randomization und Safety-Limits reproduzierbar bleibt.

OSIP-Regeln:

- Jede Physical-AI-Demo braucht ein versioniertes Szenario, Robot-/World-Description-Version, Simulatorversion, Seed und Sensor Noise Model.
- Physical-AI-Szenarien sollen Domain-Randomization-Metadaten fuer Sensorrauschen,
  Reibung, Masse, Traegheit, Latenz-Jitter oder Dropout enthalten.
- Jede Aktion mit physischer Wirkung braucht einen pruefbaren Action Contract mit Bounds und Safe State.
- Benchmarks erfassen neben p50/p95/p99 auch Jitter, Bound Violations, Contract Blocks, Collision/Safe-Stop Events, Recovery Time und False Positive/False Negative Rates.
- Sim2Real-Reports trennen Simulationsergebnisse, Hardware-Annahmen und reale Messungen klar voneinander.
- Hardwaretests duerfen niemals Voraussetzung fuer Core-CI sein.

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

### Experience Learning

OSIP-Lernen muss wie wissenschaftliche Datenerzeugung behandelt werden:

- Jede Lernbeispiel-Extraktion braucht reproduzierbare Skripte, Feature-Version, Labeldefinition, Trace-IDs, Split-Strategie und Hashes.
- Train/Eval/Test-Splits duerfen nicht durch dieselben Szenarien oder zeitlich benachbarte Traces lecken.
- Outcome-Labels muessen getrennt von Modellvorhersagen entstehen, damit das System nicht seine eigenen Fehler als Wahrheit lernt.
- Learned Fusion darf erst regelbasierte Fusion ersetzen, wenn Replay, Benchmark, Kalibrierung und Shadow Mode bessere oder gleich sichere Ergebnisse zeigen.
- Drift Monitoring muss unterscheiden zwischen Modell-Drift, Sensor-Drift, Profil-Aenderung und veraenderten Action Contracts.
- Distillation misst Teacher-Agreement, Safety-Fehler, harte Negativszenarien und Latenzbudget.
- World Models messen Vorhersagefehler pro Horizont, Unsicherheitskalibrierung, Rare-Event-Recall und Safety-False-Negatives.
- IRL/Reward Models messen Zielkonflikte, Transferverhalten, menschliche Akzeptanz, Counterexamples und Reward-Hacking-Risiken.

### Emergent Autonomy

Autonomie muss als messbares, falsifizierbares Verhalten behandelt werden:

- Jede Zielgenerierung braucht Trigger-Context, Score-Version, Schwellenwert, Evidenz, Widerspruch, Ablaufzeit und Profilfreigabe.
- Negative Tests muessen beweisen, dass Ziele ohne Contract, mit verbotenem Contract, zu hoher Unsicherheit oder Safety-Konflikt blockiert werden.
- Surprise-Metriken muessen zwischen harmloser Abweichung, menschlicher Intervention, Sensorfehler und echter Gefahr unterscheiden.
- Epistemic Goals muessen Informationsgewinn gegen Risiko, Kosten, Latenz und Privatsphaere abwaegen.
- Homeostatic Goals muessen zeigen, dass Systemerhalt nicht ueber Personen-, Raum- oder Robotersicherheit gestellt wird.

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
- Welche Outcomes sind stark genug, um als Label fuer gelerntes Verhalten zu dienen?
- Welche Teile der Fusionslogik duerfen gelernt werden, ohne Safety-Nachvollziehbarkeit zu verlieren?
- Wie berechnet OSIP Surprise so, dass menschlich gewollte Abweichungen nicht automatisch korrigiert werden?
- Welche Goal-Prioritaeten gehoeren ins Profil, welche duerfen Core-Primitiven werden?

Spaeter:

- Learned Fusion vs. regelbasierte Fusion.
- Registry- und Promotion-Policy fuer gelernte OSIP-Modelle.
- Goal Generation Engine und `goal.packet`.
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
8. Bei Learning-Themen zuerst Trace-, Dataset-, Model-Card-, Registry- und Benchmark-Gates definieren.
9. Bei Autonomie-Themen zuerst `goal.packet`, Negative Tests, Profilfreigabe, Goal-to-Contract-Mapping und Audit Trail definieren.
10. Check ausfuehren und Ergebnis dokumentieren.

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
