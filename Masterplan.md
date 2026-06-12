# Masterplan.md — OmniSense Runtime

> **Arbeitsdokument für Codex**  
> Dieses Dokument ist die zentrale technische Leitlinie für die Entwicklung von **OmniSense Runtime**: einem offenen Echtzeit-Schnittstellensystem, in dem spezialisierte Sinnesmodelle Teilwahrnehmungen veröffentlichen, eine Kontext-Engine daraus einen dynamischen Raumzustand erzeugt und eine begrenzte Action Runtime autonome Reaktionen auslöst.

---

## 0. Kurzdefinition

Architekturweite Einordnung:

> OSIP besteht aus einem domain-neutralen Grundkonzept und andockbaren Application Profiles. Der Kern beschreibt Perception, Context/World Model und Bounded Action. Profile wie Rooms, Physical AI oder spaeter Application XXX liefern Domain-Vokabular, Szenarien, Adapter und Safety-Regeln.

> Ergänzend entsteht eine kontrollierte Experience & Learning Layer: OSIP kann aus Percepts, Context Updates, Entscheidungen, Actions, Ergebnissen und späteren Outcomes lernbare Erfahrungen extrahieren, damit zukünftige Modelle aus belegten Erkenntnissen trainiert, kalibriert und bewertet werden können.

> Als weitere Ebene entsteht emergente Autonomie: OSIP darf aus Surprise, epistemischem Wert und digitaler Homöostase eigene Zielhypothesen erzeugen. Diese Ziele bleiben jedoch auditierbare `goal.packet`-Kandidaten und dürfen nur über Profile, Policies, Simulation, Benchmarks und Action Contracts in Handlungen übersetzt werden.

Smart Rooms bleiben der erste Referenzdemonstrator. Die Grundarchitektur muss jedoch so allgemein bleiben, dass spaetere Profile fuer Robotik, mobile Plattformen, Manipulatoren, Simulationen, Safety-Controller oder andere autonome Systeme dieselben OSIP-Prinzipien nutzen koennen.

**OmniSense Runtime** ist ein offenes, modulares **Perception-to-Action-System** für intelligente Räume.

Nicht das Ziel:

- keine universelle Raum-AGI,
- kein monolithisches Modell, das alles versteht,
- kein Fokusprojekt zu Datenschutz,
- keine Abhängigkeit von realer Hardware in der ersten Phase,
- keine frei improvisierende autonome KI ohne Aktionsgrenzen,
- kein selbstveränderndes Produktionsmodell, das ohne Review, Benchmark und Registry-Freigabe Live-Verhalten ändert,
- keine Zielgenerierung, die menschliche Sicherheit, Profile, Action Contracts oder Review-Pfade übergeht.

Das Ziel:

> Viele spezialisierte Sinnesmodelle liefern standardisierte Wahrnehmungspakete. Eine Echtzeit-Kontextschicht fusioniert diese Pakete zu einem operativen Weltzustand. Eine dreistufige Entscheidungslogik löst innerhalb definierter Latenz-, Evidenz- und Aktionsverträge autonome Reaktionen aus.

Zusätzlich dokumentiert OSIP diese Laufzeitkette als versionierte Experience Traces, aus denen später reproduzierbare Datensätze, Kalibrierungen, Modellkarten und kontrolliert freigegebene Modelle entstehen können.

---

## 1. Projektthese

Die zentrale technische These lautet:

> **Extrem schnelle autonome KI-Aktionen sind möglich, ohne allgemeines Weltverstehen lösen zu müssen, wenn Wahrnehmung, Kontext und Handlung über begrenzte, standardisierte Schnittstellen gekoppelt werden.**

OmniSense beweist diese These durch einen lauffähigen Referenzprototypen mit:

1. austauschbaren Sinnesmodellen,
2. einheitlichem Percept-Protokoll,
3. asynchronem Context Bus,
4. temporaler und räumlicher Fusion,
5. dreistufiger Decision Runtime,
6. Action Contracts,
7. Simulations- und Benchmark-Umgebung,
8. reproduzierbaren Demonstratoren,
9. kontrollierter Experience-to-Learning-Pipeline,
10. begrenzter emergenter Autonomie über Goal Generation, nicht über freie Aktionen.

---

### 1.1 OSIP Core und Application Profiles

OSIP wird in zwei Ebenen gedacht:

1. **Grundkonzept / OSIP Core**: versionierte Pakete, Claims, Context Updates, Action Contracts, Bus Topics, Replay, Benchmarks, Validierung, Evidenz, Unsicherheit und Safety Boundaries.
2. **Application Profiles**: domänenspezifische Erweiterungen, Vokabulare, Szenarien, Adapter, Benchmarks und Safety-Regeln.

Startprofile:

- **Application Profile: Rooms** - intelligente Raeume, Smart Buildings, Ambient Sensing, HVAC, Licht, Speaker, Komfort und Sicherheit.
- **Application Profile: Physical AI** - Robotik, Embodied AI, autonome Systeme, 3D-Kinematik, Manipulation, Navigation, Sim2Real und physische Safety Bounds.
- **Application Profile: XXX** - Platzhalter fuer neue andockbare Domaenen. Jede neue Anwendung startet als Profil, nicht als Core-Aufblaehung.

Regel:

> Neue Domain-Details gehoeren zuerst in ein Application Profile. Ein Konzept wird erst OSIP Core, wenn mindestens zwei Profile es wirklich gemeinsam brauchen.

---

### 1.2 Physical-AI-These

Die OSIP-Trennung von Perception, Context und Action entspricht dem Kern jeder Physical AI:

1. **Perception**: Kameras, Mikrofone, LiDAR, Radar, IMUs, Kraft-Momenten-Sensoren, Joint States, Tactile Arrays und propriozeptive Modelle liefern Percept Packets.
2. **Context**: Sensorfusion erzeugt ein operatives Weltmodell mit Objekten, Menschen, Hindernissen, Greifbarkeit, Kinematik, Unsicherheit, Evidenz und Widerspruechen.
3. **Action**: Nur Action Contracts erlauben physische Wirkung. Fuer Smart Rooms sind das diskrete Aktionen; fuer Robotik kommen kontinuierliche oder hochfrequente Commands hinzu, die immer durch Safety Bounds, Rate Limits, Workspace Limits und Precondition Checks begrenzt werden.

Fuer die Roadmap bedeutet das:

- Smart-Room-Szenarien bleiben MVP-Pfad.
- Physical-AI-Erweiterungen werden als offene Adapter, zusaetzliche Schemas und Benchmarks geplant, nicht als monolithische Neuausrichtung.
- Sim2Real wird als explizites Ziel gefuehrt: Szenarien, Sensoren, Weltmodelle und Action Contracts muessen zuerst reproduzierbar in Simulation pruefbar sein, bevor echte Hardware angeschlossen wird.
- Kontinuierliche Steuerung bleibt von OSIP Core getrennt: OSIP beschreibt Vertrage, Kontext, Bounds, Kommandos und Ergebnisse; harte Echtzeit-Regelkreise gehoeren in spezialisierte Controller oder Safety-Layer.

---

### 1.3 Experience & Learning Layer

OSIP soll ein eigenes maschinenlernfähiges Erfahrungsmodell vorbereiten. Jede relevante Kette aus Wahrnehmung, Kontext, Entscheidung, Aktion, Ergebnis und späterem Outcome kann als nachvollziehbarer Trace gespeichert und zu Lernbeispielen verdichtet werden:

```text
PerceptPacket -> ContextUpdate -> ActionProposal -> ActionCommand -> ActionResult -> Outcome -> Experience Dataset
```

Als Trainingsdaten-Fabrik wird daraus ein Experience Tuple:

```text
State_t + ActionContract_t + PostActionPercepts_t+delta -> Outcome_t+delta -> RewardSignal_t+delta
```

Die nachfolgenden `percept.packet`-Rückmeldungen werden dabei über Trace-ID, Action-ID, Zeitfenster, Profil, Szenario und Modellversion mit der ausgeführten oder geblockten Aktion verbunden. Dadurch entsteht ein besonders reichhaltiger multimodaler Datensatz. Er ist aber nicht automatisch perfekt: Rewards können verzögert, verrauscht, konfundiert, unvollständig oder durch Sensor-/Policy-Bias verzerrt sein und müssen deshalb explizit bewertet werden.

Ziel ist nicht, die Runtime sich selbst unkontrolliert umschreiben zu lassen. Ziel ist ein wissenschaftlich prüfbarer Lernkreislauf:

1. Runtime Trace erfassen.
2. Provenance, Schema-Versionen, Profil, Szenario, Modellfähigkeiten und Zeitfenster sichern.
3. Features, Labels, False Positives, False Negatives, Action Blocks und Outcome-Signale extrahieren.
4. Offline trainieren oder kalibrieren.
5. Gegen deterministische Szenarien und Benchmarks testen.
6. Modellkarte, Dataset-Datasheet und Registry-Eintrag erzeugen.
7. Neues Modell nur über Shadow Mode, Review, Rollback und Action-Contract-Gates freigeben.

Lernbare OSIP-Erkenntnisse:

- bessere Konfidenzkalibrierung pro Modell und Claim,
- bessere Fusionsgewichte für widersprüchliche Evidenz,
- Erkennung wiederkehrender Fehlalarme und verpasster Ereignisse,
- Vorhersage, wann Actions erfolgreich, geblockt oder riskant sind,
- Vorschläge für neue Profile, Claims, Preconditions oder Action Contracts, immer mit menschlicher Review.

Extrahierbare Modellfamilien:

- **Knowledge Distillation**: langsame Deliberative-Entscheidungen oder human-reviewte Entscheidungen werden als Teacher genutzt, um kleine, schnelle Student-Modelle für Reflex-Claims oder Contract-Ranking zu trainieren. Student-Modelle dürfen keine neuen Aktionsflächen öffnen, sondern nur innerhalb bestehender Contracts beschleunigen.
- **Predictive World Models**: Modelle lernen `P(Percepts_t+h, Context_t+h | State_t, ActionContract_t)` und erlauben Action-Dry-Runs, bevor eine Aktion ausgeführt wird. Sie bleiben beratend, bis Replay-, Benchmark-, Unsicherheits- und Safety-Gates erfüllt sind.
- **Inverse Reinforcement Learning / Reward Models**: erfolgreiche Traces, geblockte Aktionen und Feedback werden genutzt, um Kandidaten für Komfort-, Sicherheits-, Energie- oder Manipulations-Rewards zu lernen. Diese Rewards sind prüfbare Hypothesen, keine automatische normative Wahrheit.

Guardrails:

- Keine Online-Selbstoptimierung im Reflex Layer.
- Keine automatische Modellpromotion in Produktion.
- Kein gelerntes Modell darf Action Contracts, Bounds, Preconditions, Cooldowns, Safe States oder Idempotency umgehen.
- OSIP Core definiert nur generische Trace- und Learning-Verträge; Profile definieren Outcome-Labels, sensible Datenregeln, Metriken und Safety Cases.
- Reale Daten brauchen explizite Governance für Zustimmung, Aufbewahrung, Pseudonymisierung, Lizenz und Löschung.
- Reward-Signale müssen auf Leakage, Konfundierung, Zeitverzug, Zielkonflikte und Profilwechsel geprüft werden.

---

### 1.4 Emergent Autonomy und Goal Generation Engine

OSIP soll Autonomie nicht als frei improvisierende Handlung verstehen, sondern als Fähigkeit, aus Wahrnehmung und Weltmodell **Zielhypothesen** zu erzeugen. Diese Zielhypothesen werden erst später durch Profile, Policies, Simulation, Benchmarks und Action Contracts in erlaubte Handlungen übersetzt.

Die Goal Generation Engine (GGE) sitzt zwischen Context/World Model und Deliberative/Decision Runtime:

```text
PerceptPacket -> Context / World Model -> Goal Generation Engine -> GoalPacket -> Decision Runtime -> Action Contracts
```

Sie berechnet drei transparente Scores:

1. **Surprise / Prediction Error**: Wie stark weicht die beobachtete Realität von der Vorhersage des Weltmodells ab?
2. **Epistemic Value**: Wie wertvoll wäre zusätzliche Information, um Unsicherheit, Widersprüche oder fehlende Modalitäten aufzulösen?
3. **Digital Homeostasis**: Wie stark ist die eigene Wahrnehmungs-, Rechen- oder Handlungsfähigkeit des Systems gefährdet?

Aus diesen Scores kann ein `goal.packet` entstehen, zum Beispiel:

- `goal.explain_surprise`,
- `goal.reduce_ambiguity`,
- `goal.restore_sensor_quality`,
- `goal.request_human_confirmation`,
- `goal.find_safe_subgoal`.

Wichtig: Surprise ist kein automatischer Auftrag, die Welt wieder "normal" zu machen. Surprise erzeugt zuerst ein Untersuchungsziel. Ein geöffnetes Fenster, fallende VOC-Werte oder ein unbekanntes Signal können menschlich gewollt, sicherheitsrelevant oder harmlos sein. OSIP muss deshalb zwischen **erklären**, **mehr Evidenz sammeln**, **bestätigen lassen** und **handeln** unterscheiden.

Ein `goal.packet` ist ein normaler, versionierter OSIP-Kandidat mit:

- Goal-ID, Profil, Kontextbezug und Ablaufzeit,
- Surprise-, Epistemic- und Homeostatic-Score,
- Evidenz, Widersprüchen und Unsicherheit,
- erlaubten und verbotenen Action-Contract-Klassen,
- Safety-Klasse, Confirmation-Anforderung und Review-Status.

Guardrails:

- Keine versteckten Werte: Profile müssen Präferenzrahmen, Safety Cases und Zielprioritäten explizit dokumentieren.
- Keine direkte physische Wirkung: Ein Ziel darf nur über registrierte Action Contracts zu `ActionProposal` oder `ActionCommand` führen.
- Keine Selbst-Erhaltung über Menschen: digitale Homöostase darf menschliche Sicherheit und Profilregeln nicht überstimmen.
- Keine automatische Goal-Policy-Promotion: neue Zielgeneratoren brauchen Simulation, Benchmark, Shadow Mode, Audit Trail, Rollback und Review.
- Wenn kein sicherer Contract existiert, wird das Ziel verworfen oder in ein sicheres Informations- oder Rückfrage-Subziel zerlegt.

---

## 2. Codex-Arbeitsprinzipien

Codex soll dieses Projekt **schnittstellen-, test- und simulationsgetrieben** entwickeln.

### 2.1 Immer zuerst tun

Bei jeder Aufgabe:

1. Lies dieses `Masterplan.md`.
2. Prüfe, ob es eine lokale `AGENTS.md` gibt.
3. Identifiziere die betroffenen Module.
4. Schreibe oder aktualisiere Tests vor beziehungsweise während der Implementierung.
5. Verändere nur den kleinsten sinnvollen Bereich.
6. Dokumentiere neue öffentliche Interfaces.
7. Führe relevante Checks aus.
8. Fasse am Ende zusammen:
   - geänderte Dateien,
   - getroffene Designentscheidungen,
   - ausgeführte Tests,
   - bekannte Grenzen.

### 2.2 Niemals tun

Codex darf nicht:

- eine große monolithische `main.py` bauen,
- Modelllogik hart in die Context Engine einbauen,
- externe LLM-Aufrufe in den Reflex Layer einbauen,
- Hardwarezugriff als Voraussetzung für Tests machen,
- Schemas ohne Versionierung brechen,
- Aktionen ohne Action Contract ausführen,
- fehlende Sensoren als Fehler behandeln, wenn ein Fallback möglich ist,
- Simulation und Produktion vermischen,
- beliebige autonome Aktionen ohne Preconditions erlauben,
- Latenzpfade durch Datenbank-, Netzwerk- oder LLM-Aufrufe blockieren,
- Learning- oder Trainingslogik in den Reflex/Fast Path einbauen,
- gelernte Modelle ohne Trace-Provenance, Datasheet, Model Card, Benchmark-Gate und Rollback-Pfad freigeben,
- selbstgenerierte Ziele direkt in Aktionen übersetzen, ohne Profile, Policies, Simulation, Action Contracts und Safety-Gates zu prüfen.

### 2.3 Definition of Done für jede Codex-Aufgabe

Eine Aufgabe ist erst fertig, wenn:

- alle neuen öffentlichen Datenstrukturen typisiert sind,
- Validierung existiert,
- mindestens ein positiver und ein negativer Test existieren,
- relevante Tests grün sind,
- keine offensichtlichen Race Conditions oder Blocking Calls im Fast Path existieren,
- Dokumentation oder Beispiele aktualisiert sind,
- die Änderung klein genug für Review ist.

---

## 3. Empfohlene Repository-Struktur

Codex soll diese Struktur anlegen oder schrittweise dahin refactoren.

```text
omnisense/
├── AGENTS.md
├── Masterplan.md
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── Makefile
├── docs/
│   ├── architecture.md
│   ├── osip-spec.md
│   ├── action-contracts.md
│   ├── decision-runtime.md
│   ├── benchmark-plan.md
│   └── demo-scenarios.md
├── protocols/
│   ├── openapi/
│   │   └── omnisense-api.yaml
│   ├── asyncapi/
│   │   └── omnisense-events.yaml
│   └── schemas/
│       ├── model_capability.schema.json
│       ├── percept_packet.schema.json
│       ├── context_update.schema.json
│       ├── action_contract.schema.json
│       ├── action_proposal.schema.json
│       └── action_command.schema.json
├── packages/
│   ├── osip/
│   │   ├── pyproject.toml
│   │   └── omnisense_osip/
│   │       ├── __init__.py
│   │       ├── schemas.py
│   │       ├── validation.py
│   │       ├── serialization.py
│   │       └── vocabulary.py
│   ├── bus/
│   │   └── omnisense_bus/
│   │       ├── __init__.py
│   │       ├── memory_bus.py
│   │       ├── nats_bus.py
│   │       ├── mqtt_bridge.py
│   │       └── topics.py
│   ├── context_engine/
│   │   └── omnisense_context/
│   │       ├── __init__.py
│   │       ├── engine.py
│   │       ├── graph.py
│   │       ├── fusion.py
│   │       ├── conflict_resolution.py
│   │       ├── temporal_window.py
│   │       └── explanations.py
│   ├── decision_runtime/
│   │   └── omnisense_decision/
│   │       ├── __init__.py
│   │       ├── reflex.py
│   │       ├── fast_fusion.py
│   │       ├── planner.py
│   │       ├── action_contracts.py
│   │       ├── policy.py
│   │       └── executor.py
│   ├── simulators/
│   │   └── omnisense_sim/
│   │       ├── __init__.py
│   │       ├── scenario_loader.py
│   │       ├── percept_generators.py
│   │       ├── clocks.py
│   │       └── replay.py
│   ├── gateway/
│   │   └── omnisense_gateway/
│   │       ├── __init__.py
│   │       ├── app.py
│   │       ├── routes_models.py
│   │       ├── routes_percepts.py
│   │       ├── routes_context.py
│   │       ├── routes_actions.py
│   │       └── websocket.py
│   └── sdk_python/
│       └── omnisense_sdk/
│           ├── __init__.py
│           ├── client.py
│           ├── publisher.py
│           └── subscribers.py
├── scenarios/
│   ├── kitchen_burning_food.yaml
│   ├── fall_candidate.yaml
│   ├── stale_air_high_occupancy.yaml
│   ├── sensor_conflict_smoke.yaml
│   └── sensor_dropout.yaml
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── latency/
│   └── fixtures/
└── examples/
    ├── publish_fake_percepts.py
    ├── run_context_engine.py
    ├── run_decision_runtime.py
    └── dashboard_stub.py
```

---

## 4. Empfohlener Tech Stack für den ersten Prototyp

Der erste Prototyp soll robust, testbar und schnell entwickelbar sein.

### 4.1 Sprache und Runtime

- Python 3.12+
- `uv` für Dependency-Management
- `pydantic` v2 für Schemas und Validierung
- `fastapi` für HTTP/WebSocket-Gateway
- `pytest` für Tests
- `ruff` für Linting und Formatierung
- `mypy` oder `pyright` für Typprüfung
- `orjson` optional für schnelle JSON-Serialisierung

### 4.2 Event Bus

Phase 1:

- In-memory Bus für Unit- und Integrationstests
- NATS als empfohlener schneller Pub/Sub-Bus für lokale Demos

Phase 2:

- MQTT Bridge für IoT-Kompatibilität
- ROS 2 / DDS Adapter optional für Robotik- oder Echtzeit-Hardware

### 4.3 Datenhaltung

Phase 1:

- kein Datenbank-Zwang im Fast Path,
- In-memory State Store,
- JSONL Event Replay für reproduzierbare Tests.

Phase 2:

- TimescaleDB oder PostgreSQL für Ereignishistorie,
- Qdrant oder FAISS für Embedding-Suche,
- Objekt-/Kontextgraph optional in Neo4j oder in eigener Graph-Struktur.

### 4.4 Architekturregel

Der Reflex Layer darf keine Datenbank, kein LLM und keine externe API benötigen. Er muss allein aus aktuellen Percepts, lokalen Contracts und In-memory State entscheiden können.

---

## 5. Systemarchitektur

```text
[Sensoren / Datenquellen]
   ↓
[Modality Adapter]
   ↓
[Spezialisierte Sinnesmodelle]
   ↓
[OSIP Percept Packets]
   ↓
[OmniSense Context Bus]
   ↓
[Time-Space Synchronizer]
   ↓
[Context Graph Engine]
   ↓
[Decision Runtime]
   ├── Reflex Layer
   ├── Fast Fusion Layer
   └── Deliberative Layer
   ↓
[Action API]
   ↓
[Aktoren / Geräte / Apps / Roboter]
```

### 5.1 Sensoren und Adapter

Sensoren sind keine Kernabhängigkeit der Runtime. Sie werden über Adapter angebunden.

Beispiele:

- Kamera, RGB-D, LiDAR, Thermal
- Mikrofonarray
- VOC, CO₂, CO, Temperatur, Feuchte, Partikel
- Druckboden, Möbelkontakt, Smart Textiles
- mmWave-Radar, UWB, IMUs
- Smart-Home-Zustände wie Herd, Fenster, Türen, Licht, HVAC

### 5.2 Sinnesmodelle

Jedes Sinnesmodell ist austauschbar und registriert seine Fähigkeiten.

Beispiele:

- `vision.object_pose_v1`
- `audio.event_classifier_v1`
- `chemical.voc_pattern_v1`
- `tactile.pressure_contact_v1`
- `radar.motion_presence_v1`
- `environment.air_quality_v1`
- `object_state.device_status_v1`

### 5.3 OSIP Percept Bus

OSIP steht für:

> **OmniSense Interchange Protocol**

OSIP ist der Kern des Projekts. Es definiert, wie Modelle ihre Wahrnehmung veröffentlichen.

### 5.4 Kontext-Engine

Die Kontext-Engine macht aus einzelnen Claims einen operativen Raumzustand.

Sie beantwortet:

- Was passiert?
- Wo passiert es?
- Seit wann passiert es?
- Welche Modelle stützen die Interpretation?
- Welche Modelle widersprechen?
- Wie dringend ist die Lage?
- Welche Aktionen sind erlaubt?

### 5.5 Decision Runtime

Die Decision Runtime wählt Aktionen aus, aber nur innerhalb definierter Action Contracts.

Sie ist dreigeteilt:

1. Reflex Layer
2. Fast Fusion Layer
3. Deliberative Layer

---

## 6. OSIP: OmniSense Interchange Protocol

OSIP definiert die stabilen Schnittstellen zwischen Modellen, Kontext und Aktionen.

### 6.1 Pakettypen

Mindestens diese Pakettypen müssen existieren:

1. `model.capability`
2. `percept.packet`
3. `context.update`
4. `event.detected`
5. `action.contract`
6. `action.proposal`
7. `action.command`
8. `action.result`

### 6.2 Grundinvarianten

Jede Wahrnehmung muss enthalten:

- `schema_version`
- `id`
- `source_model`
- `modality`
- `timestamp`
- `received_at`, wenn vom System empfangen
- `valid_for_ms`
- `latency_ms`
- mindestens einen Claim
- Konfidenz pro Claim
- Sensor- oder Modellqualität
- optional Raum-/Zonen-/Koordinatenreferenz
- optional Embedding-Referenz

Jede Aktion muss enthalten:

- `action_id`
- Zielsystem
- Operation
- Parameter
- Preconditions
- Deadline
- Idempotency-Key
- Rollback oder Safe State, sofern möglich
- Priorität
- Ergebnisstatus

---

## 7. Zentrale Datenmodelle

Codex soll diese Modelle zuerst in `packages/osip/omnisense_osip/schemas.py` implementieren.

### 7.1 ModelCapabilityDescriptor

```json
{
  "schema_version": "osip/0.1",
  "type": "model.capability",
  "model_id": "vision.pose_activity_v1",
  "display_name": "Vision Pose and Activity Model",
  "version": "0.1.0",
  "modalities": ["rgb", "depth"],
  "outputs": [
    "person.presence",
    "person.pose",
    "event.fall_candidate",
    "object.interaction"
  ],
  "latency_profile": {
    "p50_ms": 25,
    "p95_ms": 80,
    "max_budget_ms": 120
  },
  "spatial_reference": "room_xyz",
  "confidence_calibrated": false,
  "embedding": {
    "available": true,
    "dimension": 768,
    "space": "vision_pose_activity_v1"
  }
}
```

### 7.2 PerceptPacket

```json
{
  "schema_version": "osip/0.1",
  "type": "percept.packet",
  "id": "perc_000001",
  "source_model": "audio.event_classifier_v1",
  "modality": "audio",
  "timestamp": "2026-06-12T14:31:09.210Z",
  "valid_for_ms": 800,
  "latency_ms": 18,
  "location": {
    "room": "living_room",
    "zone": "sofa_area",
    "azimuth_deg": 42
  },
  "claims": [
    {
      "label": "audio.impact_sound",
      "confidence": 0.82,
      "value": true
    },
    {
      "label": "audio.human_shout",
      "confidence": 0.64,
      "value": true
    }
  ],
  "embedding": {
    "ref": "emb_audio_7742",
    "dimension": 512,
    "space": "audio_event_v1"
  },
  "quality": {
    "status": "usable",
    "signal_noise": 0.18,
    "drift_score": null
  }
}
```

### 7.3 ContextUpdate

```json
{
  "schema_version": "osip/0.1",
  "type": "context.update",
  "context_id": "ctx_20260612_143109_001",
  "timestamp": "2026-06-12T14:31:09.350Z",
  "time_window_ms": 250,
  "room": "living_room",
  "entities": [
    {
      "id": "person_anon_1",
      "type": "person",
      "zone": "sofa_area",
      "state": "possibly_on_floor",
      "confidence": 0.79
    }
  ],
  "events": [
    {
      "label": "event.fall_candidate",
      "confidence": 0.86,
      "urgency": 0.81,
      "evidence": [
        "tactile.floor_pressure_spike",
        "audio.impact_sound",
        "radar.motion_drop"
      ],
      "contradictions": []
    }
  ],
  "global_risk": {
    "safety": 0.82,
    "comfort": 0.21,
    "maintenance": 0.05
  }
}
```

### 7.4 ActionContract

```json
{
  "schema_version": "osip/0.1",
  "type": "action.contract",
  "action_id": "hvac.ventilation_boost",
  "target": "hvac.living_room",
  "operation": "ventilation.boost",
  "risk_class": "low",
  "allowed_contexts": [
    "context.bad_air",
    "context.possible_smoke_low_risk",
    "context.high_occupancy_stale_air"
  ],
  "preconditions": [
    "hvac.available == true"
  ],
  "min_confidence": 0.60,
  "max_decision_latency_ms": 250,
  "cooldown_ms": 30000,
  "rollback": "hvac.ventilation_normal",
  "idempotent": true
}
```

### 7.5 ActionProposal

```json
{
  "schema_version": "osip/0.1",
  "type": "action.proposal",
  "proposal_id": "actprop_000001",
  "based_on_context": "ctx_20260612_143109_001",
  "action_id": "room.speaker.ask_help_needed",
  "priority": "high",
  "confidence": 0.84,
  "deadline_ms": 500,
  "reason": "Fall candidate supported by pressure, audio and radar.",
  "requires_confirmation": false
}
```

### 7.6 ActionCommand

```json
{
  "schema_version": "osip/0.1",
  "type": "action.command",
  "command_id": "cmd_000001",
  "proposal_id": "actprop_000001",
  "target": "room.speaker",
  "operation": "speak",
  "parameters": {
    "text": "Brauchst du Hilfe?"
  },
  "execute_before_ms": 300,
  "idempotency_key": "ctx_20260612_143109_001:ask_help_needed"
}
```

---

## 8. Vokabular und Naming

Labels müssen stabil und maschinenlesbar sein.

### 8.1 Claim Naming Pattern

```text
<domain>.<object_or_signal>.<property_or_event>
```

Beispiele:

```text
vision.person.presence
vision.smoke.visible_near_stove
audio.impact_sound
audio.glass_break
audio.human_shout
chemical.air.voc_spike
chemical.air.smoke_like_pattern
thermal.stove.hotspot
tactile.floor.pressure_spike
radar.person.motion_drop
object.stove.power_on
environment.air.co2_high
```

### 8.2 Kontextklassen

```text
context.normal_activity
context.unattended_cooking_risk
context.possible_burning_food
context.probable_fire
context.possible_fall
context.possible_intrusion
context.glass_break
context.bad_air
context.high_occupancy_stale_air
context.sensor_conflict
context.sensor_dropout
context.device_fault
```

### 8.3 Actionklassen

```text
action.notify.local
action.speaker.ask_user
action.light.warning_signal
action.hvac.ventilation_boost
action.stove.power_off
action.door.unlock_for_emergency
action.log.event
action.request.human_confirmation
action.escalate.contact
```

---

## 9. Transport- und API-Design

OmniSense soll transportagnostisch sein. Die Semantik liegt in OSIP, nicht im Transportprotokoll.

### 9.1 Event Topics

```text
omnisense.models.registered
omnisense.percepts.<modality>.<model_id>
omnisense.context.updates
omnisense.events.detected
omnisense.actions.contracts
omnisense.actions.proposals
omnisense.actions.commands
omnisense.actions.results
omnisense.telemetry.latency
omnisense.telemetry.health
```

### 9.2 HTTP API

Mindest-Endpunkte:

```http
GET  /healthz
GET  /metrics
POST /v1/models/register
GET  /v1/models
POST /v1/percepts
GET  /v1/context/current
GET  /v1/context/{context_id}
GET  /v1/events/stream
POST /v1/actions/register
GET  /v1/actions/contracts
GET  /v1/actions/proposals
POST /v1/actions/execute
POST /v1/scenarios/run
GET  /v1/scenarios/{run_id}
```

### 9.3 WebSocket Streams

```text
/ws/percepts
/ws/context
/ws/events
/ws/actions
/ws/telemetry
```

### 9.4 Spezifikationen

Codex soll generieren oder pflegen:

- `protocols/openapi/omnisense-api.yaml`
- `protocols/asyncapi/omnisense-events.yaml`
- `protocols/schemas/*.schema.json`

OpenAPI soll HTTP-Endpunkte beschreiben. AsyncAPI soll Event-Channels und Message-Schemas beschreiben. CloudEvents kann optional als Event Envelope verwendet werden.

---

## 10. Decision Runtime

### 10.1 Drei Entscheidungsbahnen

#### A. Reflex Layer

Für sehr schnelle, harte Reaktionen.

Ziel:

```text
10–100 ms reine Entscheidungszeit im lokalen Prozess
```

Eigenschaften:

- keine LLM-Abfragen,
- kein Datenbankzugriff,
- keine Cloud-Abhängigkeit,
- kleine Regeln oder kompakte Klassifikatoren,
- harte Timeouts,
- Action Contracts erforderlich.

Beispiele:

```text
chemical.air.smoke_like_pattern > 0.85
AND thermal.stove.hotspot > 0.70
AND object.stove.power_on == true
→ action.light.warning_signal
→ action.hvac.ventilation_boost
```

#### B. Fast Fusion Layer

Für multimodale Ereignisse.

Ziel:

```text
50–300 ms Entscheidungszeit
```

Beispiele:

```text
tactile.floor.pressure_spike
audio.impact_sound
radar.person.motion_drop
→ context.possible_fall
→ action.speaker.ask_user
```

#### C. Deliberative Layer

Für nicht zeitkritische Planung, Erklärung und Langzeitoptimierung.

Ziel:

```text
500 ms bis mehrere Sekunden
```

Darf größere Modelle oder LLMs verwenden, aber niemals als einziger Pfad für zeitkritische Ereignisse.

---

## 11. Kontextfusion

### 11.1 Minimum Viable Fusion

Für Phase 1 reicht eine erklärbare gewichtete Fusion.

Input:

- Claims aus Percept Packets,
- Zeitfenster,
- Raumzonen,
- Modellqualität,
- Widersprüche,
- Action Contracts.

Output:

- Kontextklasse,
- Konfidenz,
- Urgency,
- Evidence-Liste,
- Contradiction-Liste,
- empfohlene Action Proposals.

### 11.2 Fusionsformel für Prototyp

Für ein Ereignis `E`:

```text
score(E) = Σ weight(claim_i, modality_i, quality_i, freshness_i) - Σ contradiction_penalty_j
```

Dann:

```text
confidence(E) = calibrated_sigmoid(score(E))
urgency(E) = confidence(E) * severity(E) * time_sensitivity(E)
```

Für den ersten Prototyp darf die Kalibrierung simpel sein. Wichtig ist, dass sie austauschbar ist.

### 11.3 Spätere Fusionsvarianten

Später vergleichen:

1. regelbasierte Fusion,
2. gewichtete probabilistische Fusion,
3. temporaler Graph,
4. Graph Neural Network,
5. Cross-Attention Transformer,
6. Mixture-of-Experts,
7. uncertainty-aware Fusion.

Die Schnittstelle muss alle Varianten erlauben.

---

## 12. Context Graph

Der Context Graph ist die operative Weltrepräsentation.

### 12.1 Knotentypen

```text
Room
Zone
Sensor
Model
PersonAnon
Object
Device
Signal
Claim
Event
Context
Action
```

### 12.2 Kantentypen

```text
OBSERVED_BY
SUPPORTED_BY
CONTRADICTED_BY
LOCATED_IN
TEMPORALLY_NEAR
TRIGGERS
BLOCKED_BY
EXECUTED_ON
RESULTED_IN
```

### 12.3 Minimum Implementation

Phase 1:

- In-memory Graph mit Python-Klassen oder NetworkX.
- Keine harte Datenbankabhängigkeit.
- Graph muss serialisierbar sein.
- Jeder Context Update muss evidence- und contradiction-fähig sein.

---

## 13. Action Contracts

Action Contracts sind der Schlüssel, um autonome KI-Aktionen trotz offener Welt begrenzt und schnell zu machen.

### 13.1 Grundregel

> Keine Aktion ohne Contract.

### 13.2 Contract-Felder

Jeder Contract braucht:

- `action_id`
- `target`
- `operation`
- `risk_class`
- `allowed_contexts`
- `required_evidence`, optional
- `preconditions`
- `min_confidence`
- `max_decision_latency_ms`
- `cooldown_ms`
- `rollback`
- `idempotent`
- `requires_confirmation`, optional

### 13.3 Risikoklassen

```text
low          Komfort, Licht, Lüftung, Logging
medium       Warnung, lauter Alarm, Benachrichtigung
high         Geräte abschalten, Türen öffnen, externe Eskalation
critical     physisch gefährliche oder irreversible Aktionen; im Prototyp vermeiden
```

### 13.4 Action Safety Rules

Auch wenn Datenschutz nicht Fokus ist, muss Aktionssicherheit Fokus sein.

- Riskantere Aktionen brauchen mehr Evidenz.
- Jede Aktion braucht Cooldown oder Idempotency.
- Jede Aktion muss Ergebnis zurückmelden.
- Fehlgeschlagene Aktionen müssen sichtbar sein.
- Der Simulator muss Aktionsfolgen prüfen.

---

## 14. Simulationsstrategie

Das Projekt wird **simulation-first** entwickelt.

### 14.1 Warum Simulation zuerst?

- Schnittstellen können ohne Hardware bewiesen werden.
- Latenzpfade sind reproduzierbar.
- Tests bleiben stabil.
- Codex kann autonom entwickeln, ohne Sensorzugriff zu benötigen.
- Spätere Hardwareadapter werden nur Producer von OSIP-Paketen.

### 14.2 Szenarioformat

Beispiel `scenarios/kitchen_burning_food.yaml`:

```yaml
id: kitchen_burning_food
name: Kitchen burning food scenario
duration_ms: 3000
room: kitchen
expected_contexts:
  - context.possible_burning_food
expected_actions:
  - action.notify.local
  - action.hvac.ventilation_boost
latency_budget_ms:
  first_context_update: 250
  first_action_proposal: 500
percepts:
  - at_ms: 0
    source_model: object_state.device_status_v1
    modality: object_state
    claims:
      - label: object.stove.power_on
        confidence: 0.99
        value: true
  - at_ms: 120
    source_model: thermal.hotspot_v1
    modality: thermal
    claims:
      - label: thermal.stove.hotspot
        confidence: 0.91
        value: true
  - at_ms: 250
    source_model: chemical.voc_pattern_v1
    modality: chemical
    claims:
      - label: chemical.air.smoke_like_pattern
        confidence: 0.86
        value: true
  - at_ms: 320
    source_model: vision.smoke_v1
    modality: vision
    claims:
      - label: vision.smoke.visible_near_stove
        confidence: 0.72
        value: true
```

### 14.3 Pflichtszenarien

1. `kitchen_burning_food.yaml`
2. `fall_candidate.yaml`
3. `stale_air_high_occupancy.yaml`
4. `sensor_conflict_smoke.yaml`
5. `sensor_dropout.yaml`
6. `normal_cooking_no_alarm.yaml`
7. `object_falls_not_person.yaml`
8. `steam_without_fire.yaml`

---

## 15. Demonstratoren

### 15.1 Demo 1: Autonome Küchensicherheit

Modalitäten:

- chemisch/VOC,
- thermal,
- vision,
- objektstatus,
- optional audio.

Kontexte:

- normales Kochen,
- Dampf ohne Gefahr,
- anbrennendes Essen,
- Herd an und unbeaufsichtigt,
- wahrscheinliche Brandgefahr.

Aktionen:

- lokale Warnung,
- Lüftung erhöhen,
- Lichtsignal,
- optional Herdabschaltung im Simulator.

### 15.2 Demo 2: Sturz- und Notfallkandidat

Modalitäten:

- tactile/pressure,
- audio,
- radar,
- optional vision pose.

Kontexte:

- Mensch setzt sich,
- Gegenstand fällt,
- Mensch fällt,
- Mensch liegt bewegungslos,
- Hilferuf.

Aktionen:

- Rückfrage per Lautsprecher,
- Licht einschalten,
- lokale Benachrichtigung,
- Eskalation nur im Simulator.

### 15.3 Demo 3: Kontextbasierte Raumsteuerung

Modalitäten:

- CO₂,
- VOC,
- Temperatur,
- Feuchte,
- Belegung,
- Bewegung,
- Tageslicht.

Kontexte:

- schlechte Luft,
- hohe Belegung,
- Aktivität wechselt,
- Energie sparen,
- Komfort verbessern.

Aktionen:

- Lüftung,
- Licht,
- Temperaturziel,
- Energiesparmodus.

---

## 16. Entwicklungsphasen

### Phase 0 — Repository Foundation

Ziel:

- Projektgerüst,
- Tooling,
- AGENTS.md,
- CI-Grundlagen,
- erstes README.

Tasks:

- `pyproject.toml` mit Workspace/Packages anlegen.
- `ruff`, `pytest`, Typprüfung konfigurieren.
- `Makefile` mit Standardbefehlen erstellen.
- `docker-compose.yml` mit optionalem NATS anlegen.
- `AGENTS.md` aus Template in Abschnitt 21 erstellen.

Akzeptanzkriterien:

- `make test` läuft.
- `make lint` läuft.
- `make typecheck` läuft oder ist bewusst als späterer Gate markiert.
- README erklärt Vision und Quickstart.

---

### Phase 1 — OSIP Schemas

Ziel:

- stabile Datenverträge.

Tasks:

- Pydantic-Modelle für alle Kernpakete.
- JSON Schema Export.
- Validierungsfehler klar und testbar machen.
- Vocabulary-Modul für Labels und Kontextklassen.

Akzeptanzkriterien:

- ungültige Percept Packets werden abgelehnt,
- gültige Beispiele serialisieren/deserialisieren stabil,
- JSON Schemas werden generiert,
- Tests für Versionierung existieren.

---

### Phase 2 — In-memory Context Bus

Ziel:

- lokale Event-Kommunikation ohne externe Infrastruktur.

Tasks:

- Async Publish/Subscribe Interface definieren.
- In-memory Bus implementieren.
- Topic-Konventionen zentralisieren.
- Event Replay aus JSONL ermöglichen.

Akzeptanzkriterien:

- Percepts können publiziert und abonniert werden,
- mehrere Subscriber funktionieren,
- Reihenfolge innerhalb eines Topics ist deterministisch testbar,
- Integrationstest publiziert Percept → empfängt Percept.

---

### Phase 3 — Simulatoren und Szenario-Replay

Ziel:

- reproduzierbare Daten ohne Hardware.

Tasks:

- YAML-Szenariolader bauen.
- PerceptGenerator implementieren.
- SimulatedClock implementieren.
- ReplayRunner implementieren.
- Beispiel-Szenarien anlegen.

Akzeptanzkriterien:

- `kitchen_burning_food.yaml` kann abgespielt werden,
- erwartete Percepts erscheinen mit korrektem Timing,
- Tests laufen ohne Sleep-Flakiness,
- Szenario-Erwartungen können geprüft werden.

---

### Phase 4 — Context Engine v0.1

Ziel:

- erste nutzbare Fusion.

Tasks:

- TemporalWindow implementieren.
- Claim Aggregation implementieren.
- einfache Fusionsregeln für erste Kontexte.
- Evidence und Contradictions ausgeben.
- ContextUpdate publizieren.

Akzeptanzkriterien:

- Kitchen-Szenario erzeugt `context.possible_burning_food`,
- Fall-Szenario erzeugt `context.possible_fall`,
- Normal Cooking erzeugt keinen Alarm,
- Konfliktszenario erzeugt `context.sensor_conflict` oder reduzierte Konfidenz,
- ContextUpdate enthält Evidence.

---

### Phase 5 — Decision Runtime v0.1

Ziel:

- Action Proposals aus Kontexten erzeugen.

Tasks:

- ActionContract-Modell implementieren.
- Contract Registry bauen.
- Reflex Layer implementieren.
- Fast Fusion Decision Rules implementieren.
- ActionProposal und ActionCommand erzeugen.
- Cooldown und Idempotency implementieren.

Akzeptanzkriterien:

- kein ActionProposal ohne Contract,
- niedrige Konfidenz blockiert Aktion,
- fehlende Preconditions blockieren Aktion,
- Cooldown verhindert Spam,
- Kitchen-Szenario erzeugt Warnung und Lüftung,
- Fall-Szenario erzeugt Rückfrage.

---

### Phase 6 — Gateway API und Streams

Ziel:

- externe Apps können Modelle registrieren, Percepts senden und Context/Actions abonnieren.

Tasks:

- FastAPI-App erstellen.
- HTTP-Endpunkte implementieren.
- WebSocket-Streams implementieren.
- OpenAPI exportieren.
- Basic SDK Client erstellen.

Akzeptanzkriterien:

- `POST /v1/models/register` funktioniert,
- `POST /v1/percepts` publiziert auf Bus,
- `GET /v1/context/current` liefert aktuellen Zustand,
- `/ws/events` streamt Ereignisse,
- SDK kann Percepts senden.

---

### Phase 7 — Benchmarks

Ziel:

- Machbarkeit belegen.

Tasks:

- Latenzmessung instrumentieren.
- p50/p95/p99 berechnen.
- Szenario-Suite ausführen.
- Sensor-Dropout testen.
- Modell-Austausch testen.

Akzeptanzkriterien:

- Benchmark-Report wird als Markdown/JSON erzeugt,
- End-to-End-Latenz wird gemessen,
- Fehlalarme und verpasste Kontexte werden gezählt,
- `sensor_dropout` führt nicht zum Crash,
- Modellregistrierung bleibt austauschbar.

---

### Phase 8 — Adapter und reale Modell-Stubs

Ziel:

- erste echte oder halb-echte Inputs anbinden.

Tasks:

- Adapter-Interface definieren.
- CSV/JSONL Adapter bauen.
- MQTT Bridge bauen.
- Beispiel für externes Modell als separater Prozess.
- optional Webcam-/Mikrofon-Stubs, aber nicht als Testvoraussetzung.

Akzeptanzkriterien:

- externes Modell kann via SDK Percepts senden,
- Runtime kennt Modell nur über Capability Descriptor,
- Tests bleiben hardwareunabhängig.

---

### Phase 9 — Demo Dashboard

Ziel:

- Systemzustand sichtbar machen.

Tasks:

- einfaches Web-Dashboard oder CLI-TUI.
- Anzeige von Percepts, Kontexten, Actions, Latenzen.
- Szenario starten und Ergebnis sehen.

Akzeptanzkriterien:

- Demo kann ohne echte Sensoren laufen,
- Kitchen- und Fall-Szenario sind visuell nachvollziehbar,
- Actions werden mit Evidence angezeigt.

---

### Phase 10 — Forschungsartefakte

Ziel:

- Projekt als Forschungsbeweis dokumentieren.

Deliverables:

- `docs/osip-spec.md`
- `docs/architecture.md`
- `docs/benchmark-plan.md`
- `docs/results.md`
- `protocols/openapi/omnisense-api.yaml`
- `protocols/asyncapi/omnisense-events.yaml`
- Demo-Videos oder Demo-Skripte
- reproduzierbarer Benchmark

---

## 17. Benchmarks und Beweisführung

### 17.1 Was bewiesen werden soll

OmniSense soll zeigen:

1. Unterschiedliche Sinnesmodelle lassen sich über ein gemeinsames Percept-Format integrieren.
2. Die Kontext-Engine kann asynchrone, unterschiedlich schnelle Modalitäten fusionieren.
3. Die Decision Runtime kann in festen Latenzbudgets reagieren.
4. Austausch eines Modells erfordert keine Änderung am Core.
5. Sensor-Ausfall reduziert Qualität, aber bringt das System nicht zum Absturz.
6. Action Contracts begrenzen Autonomie, ohne Reaktionsfähigkeit zu verlieren.

### 17.2 Metriken

Technisch:

```text
p50_context_latency_ms
p95_context_latency_ms
p99_context_latency_ms
p50_action_proposal_latency_ms
p95_action_proposal_latency_ms
schema_validation_failures
bus_delivery_errors
context_detection_f1
false_positive_rate
false_negative_rate
action_contract_blocks
action_success_rate
sensor_dropout_survival_rate
```

Architektonisch:

```text
model_swap_lines_changed
new_model_integration_time
number_of_core_changes_for_new_modality
schema_breakages_per_release
```

### 17.3 Latency Budgets

Für den Prototyp:

```text
Percept ingestion:           p95 < 25 ms
Context update simple:       p95 < 100 ms
Context update multimodal:   p95 < 300 ms
Action proposal:             p95 < 500 ms
Reflex decision local:       p95 < 100 ms
```

Diese Werte sind Forschungsziele, keine Garantien für beliebige Hardware.

---

## 18. Teststrategie

### 18.1 Unit Tests

- Schema Validation
- Vocabulary
- TemporalWindow
- Fusion Scores
- Contract Evaluation
- Cooldown Logic
- Idempotency

### 18.2 Contract Tests

- JSON Schema Beispiele validieren
- OpenAPI/AsyncAPI gegen Schemas prüfen
- Breaking Changes erkennen

### 18.3 Integration Tests

- Percept → Bus → ContextUpdate
- ContextUpdate → ActionProposal
- Scenario Replay → Expected Contexts
- Scenario Replay → Expected Actions

### 18.4 Latency Tests

- künstliche Percept-Bursts
- mehrere Modalitäten parallel
- p95/p99 messen
- keine harten absoluten Grenzen in CI, außer sehr grobe Regression Gates

### 18.5 Fault Injection

- fehlende Modalität
- verspätete Percepts
- widersprüchliche Percepts
- ungültiger Claim
- Sensorqualität `degraded`
- Drift Score hoch
- duplicate messages

---

## 19. Erste Backlog-Epics

### Epic A — OSIP Core

- A1: Pydantic-Modelle für OSIP anlegen
- A2: JSON Schema Export einbauen
- A3: Beispielpakete unter `tests/fixtures/osip/` anlegen
- A4: Validierungstests schreiben
- A5: Vocabulary-Modul anlegen

### Epic B — Bus

- B1: Bus Protocol Interface definieren
- B2: InMemoryBus implementieren
- B3: Topic-Konventionen testen
- B4: Replay aus JSONL implementieren
- B5: NATS Adapter optional vorbereiten

### Epic C — Simulator

- C1: YAML-Szenarioformat definieren
- C2: ScenarioLoader bauen
- C3: SimulatedClock bauen
- C4: ReplayRunner bauen
- C5: erste drei Szenarien erstellen

### Epic D — Context Engine

- D1: TemporalWindow implementieren
- D2: Claim Index bauen
- D3: Weighted Fusion Engine bauen
- D4: Evidence/Contradiction Tracking
- D5: ContextUpdate Publisher

### Epic E — Decision Runtime

- E1: ActionContract Registry
- E2: Preconditions Evaluator
- E3: Reflex Rule Engine
- E4: Fast Fusion Decision Engine
- E5: ActionProposal Publisher
- E6: ActionCommand Executor Stub

### Epic F — Gateway und SDK

- F1: FastAPI App
- F2: Model Registration API
- F3: Percept Ingestion API
- F4: Context API
- F5: WebSocket Event Stream
- F6: Python SDK Publisher
- F7: CapabilityGate im Gateway, damit Percepts nur registrierte Modalitaeten
  und Claim-Labels ihrer ModelCapabilityDescriptoren nutzen

### Epic G — Benchmark

- G1: Metrics Collector
- G2: Scenario Benchmark Runner
- G3: Latency Report
- G4: Dropout Tests
- G5: Model Swap Demo
- G6: Benchmark-Gates mit Application-Profile-Metadaten und fail-closed
  Verhalten fuer unbekannte Profile ausgeben

### Epic H - Application Profiles

- H1: Profil-Architektur dokumentieren: OSIP Core vs. Application Profile, Erweiterungsregeln, Tests und Governance
- H2: Application Profile `rooms` als ersten Referenzdemonstrator dokumentieren und gegen MVP-Roadmap spiegeln
- H3: Application Profile `physical-ai` fuer Robotik, Manipulation, Navigation, Propriozeption, Sim2Real und Safety Bounds ausarbeiten
- H4: Application Profile Template fuer zukuenftige Domaenen wie `xxx` anlegen
- H5: Profil-spezifische Vokabulare, Fixtures, Szenarien, Benchmarks und Safety Cases voneinander trennen
- H6: Adapter-Regel definieren: Simulatoren, ROS 2/DDS, MQTT, NATS, Robot-SDKs und Gebaeudetechnik bleiben ausserhalb von OSIP Core
- H7: Core-Promotion-Regel einfuehren: Ein Profilkonzept wird erst Core, wenn mindestens zwei Profile es gemeinsam brauchen
- H8: Runtime-Registries fuer Profil-Fusion und Profil-Policies einfuehren, damit `rooms`, `physical-ai` und `xxx` ohne Core-Umbau andocken koennen
- H9: `ApplicationProfile` Protocol einfuehren, das Profil-Metadaten, Context-Fusion und Decision-Profil als andockbares Runtime-Bundle beschreibt

### Epic I - Experience & Learning Layer

- I1: Experience-Trace-Konzept dokumentieren: Perception, Context, Decision, Action, Result und Outcome als zusammenhaengende Lernkette
- I2: Versionierte Trace- und Dataset-Manifeste entwerfen, inklusive Schema-Version, Profil, Szenario, Modellfaehigkeiten, Provenance und Hashes
- I3: Label- und Outcome-Schema fuer False Positives, False Negatives, Action Blocks, Action Success und Sensorqualitaet vorbereiten
- I4: Feature- und Label-Extraktion als offline Benchmark-/Dataset-Schritt planen, nicht als Reflex/Fast-Path-Logik
- I5: Model Cards, Dataset Datasheets, Registry-Eintraege und Lineage-Metadaten als Pflichtartefakte fuer gelernte Modelle definieren
- I6: Shadow-Mode-, Benchmark-, Rollback- und Action-Contract-Gates fuer jede Modellpromotion festlegen
- I7: `trace_id`, `correlation_id` und strukturierte `EvidenceRef`-Quellen als kompatible OSIP-v0.1-Trace-Grundlage einfuehren
- I7: Drift-, Kalibrierungs- und Re-Evaluation-Regeln fuer wiederholt gelernte Modelle beschreiben
- I8: Decision Trace und Experience Tuple entwerfen: `State_t`, `ActionContract_t`, `PostActionPercepts_t+delta`, `Outcome_t+delta` und `RewardSignal_t+delta`
- I9: Modellfamilien als Roadmap-Slots trennen: Knowledge Distillation fuer Reflex-Beschleunigung, Predictive World Models fuer Action-Dry-Runs, IRL/Reward Models fuer Ziel- und Komforthypothesen
- I10: Reward-Signal-Audit definieren: Delay, Leakage, Konfundierung, Sensor-Bias, Zielkonflikte, Profilwechsel und menschliche Review

### Epic J - Emergent Autonomy und Goal Generation

- J1: Emergent-Autonomy-Konzept dokumentieren: Surprise, epistemischer Wert, digitale Homoeostase und Bounded Autonomy
- J2: `goal.packet` als zukuenftigen OSIP-Vertrag entwerfen, inklusive Scores, Kontextbezug, Evidenz, Ablaufzeit, Safety-Klasse und Review-Status
- J3: Goal Generation Engine als Schicht zwischen Context/World Model und Decision Runtime beschreiben
- J4: Goal-to-Contract-Mapping definieren: Ziele duerfen nur registrierte Action Contracts vorschlagen oder sichere Subgoals erzeugen
- J5: Negative Autonomy Tests planen: kein Contract, verbotener Contract, zu hohe Unsicherheit, Safety-Prioritaet, fehlende Profilfreigabe
- J6: Surprise-Audit definieren: Prediction Error erzeugt zuerst Untersuchungsziele, nicht automatische Korrekturhandlungen
- J7: Homeostatic-Audit definieren: Systemerhalt darf menschliche Sicherheit und Profilregeln niemals ueberstimmen
- J8: Shadow-Mode- und Benchmark-Gates fuer neue Goal-Generatoren festlegen

---

## 20. Konkrete Codex-Prompts

Diese Prompts können direkt in Codex verwendet werden.

### Prompt 1 — Repository initialisieren

```text
Lies Masterplan.md vollständig. Erstelle das minimale Repository-Gerüst für OmniSense Runtime nach Abschnitt 3 und Phase 0. Lege pyproject.toml, README.md, AGENTS.md, Makefile, docs/ und packages/ an. Implementiere noch keine komplexe Logik. Richte pytest und ruff ein. Done when: make test und make lint laufen erfolgreich, README enthält Quickstart, AGENTS.md enthält die wichtigsten Regeln aus Masterplan.md.
```

### Prompt 2 — OSIP Schemas

```text
Implementiere Phase 1 aus Masterplan.md: OSIP Schemas in packages/osip. Nutze Pydantic v2. Implementiere ModelCapabilityDescriptor, PerceptPacket, Claim, Location, SensorQuality, EmbeddingRef, ContextUpdate, ActionContract, ActionProposal, ActionCommand und ActionResult. Erzeuge JSON Schema Export unter protocols/schemas. Schreibe Unit- und Contract-Tests für gültige und ungültige Beispiele. Done when: pytest grün, Schemas exportierbar, Beispiele in tests/fixtures/osip vorhanden.
```

### Prompt 3 — In-memory Bus

```text
Implementiere Phase 2: einen asynchronen InMemoryBus mit publish/subscribe, Topic-Konventionen und deterministischen Tests. Der Bus muss OSIP-Pakete transportieren können, aber nicht selbst deren Semantik kennen. Done when: Integrationstest Percept -> Bus -> Subscriber funktioniert und mehrere Subscriber dieselbe Nachricht erhalten.
```

### Prompt 4 — Simulator

```text
Implementiere Phase 3: YAML ScenarioLoader, SimulatedClock und ReplayRunner. Nutze die Szenario-Spezifikation aus Masterplan.md. Lege kitchen_burning_food.yaml, fall_candidate.yaml und stale_air_high_occupancy.yaml an. Done when: Szenarien ohne reale Sleeps reproduzierbar abgespielt werden und Percepts auf dem InMemoryBus erscheinen.
```

### Prompt 5 — Context Engine v0.1

```text
Implementiere Phase 4: TemporalWindow, einfache gewichtete Fusionslogik und ContextUpdate-Erzeugung. Starte mit den Kontexten context.possible_burning_food, context.possible_fall und context.high_occupancy_stale_air. Jede ContextUpdate-Ausgabe muss Evidence und Contradictions enthalten. Done when: die drei Szenarien die erwarteten Kontexte erzeugen und normal_cooking_no_alarm keinen Alarm erzeugt.
```

### Prompt 6 — Decision Runtime v0.1

```text
Implementiere Phase 5: ActionContract Registry, Preconditions Evaluator, Reflex Layer, Fast Fusion Rule Engine und ActionProposal-Ausgabe. Keine Aktion ohne Contract. Implementiere Cooldown und Idempotency. Done when: kitchen_burning_food erzeugt Warnung und Lüftung, fall_candidate erzeugt Rückfrage, niedrige Confidence und fehlende Preconditions blockieren Aktionen.
```

### Prompt 7 — Gateway API

```text
Implementiere Phase 6: FastAPI Gateway mit Model Registration, Percept Ingestion, Current Context und WebSocket Event Stream. Generiere oder aktualisiere OpenAPI. Baue einen kleinen Python SDK Publisher. Done when: ein Beispielskript ein Modell registriert, Percepts sendet und ein ContextUpdate empfangen werden kann.
```

### Prompt 8 — Benchmark Runner

```text
Implementiere Phase 7: Benchmark Runner für Szenarien mit p50/p95/p99 Latenzen, Context Detection Results, Action Proposal Results und JSON/Markdown Report. Done when: make benchmark einen Report unter docs/results/latest.md erzeugt.
```

### Prompt 9 — Review

```text
Reviewe die aktuelle Implementierung gegen Masterplan.md. Suche besonders nach: Monolithen, fehlenden Tests, hart verdrahteten Modellnamen im Core, Blocking Calls im Reflex/Fast Path, fehlender Schema-Versionierung, Actions ohne Contracts und schlecht dokumentierten öffentlichen Interfaces. Erstelle konkrete Fixes oder Issues.
```

### Prompt 10 - Application Profiles

```text
Teile OSIP sauber in Grundkonzept/Core und Application Profiles auf. Lege Profile fuer Rooms und Physical AI an und erzeuge ein Template fuer zukuenftige Profile wie XXX. Dokumentiere, welche Begriffe, Schemas, Szenarien, Adapter und Safety-Regeln im Profil bleiben und welche Konzepte in OSIP Core duerfen. Done when: docs/core-concept.md, docs/applications/rooms.md, docs/applications/physical-ai.md und ein Profil-Template existieren, Masterplan/AGENTS/Skill die Profile-Regel nennen und make test/lint/typecheck gruen sind.
```

### Prompt 11 - Experience & Learning Layer

```text
Erweitere OSIP um ein kontrolliertes Experience-to-Learning-Konzept. Dokumentiere, wie PerceptPacket, ContextUpdate, ActionProposal, ActionCommand, ActionResult, nachfolgende PerceptPackets und Outcome zu versionierten Decision Traces, Experience Tuples, Dataset-Manifests, Model Cards und Registry-Eintraegen werden. Nenne Knowledge Distillation, Predictive World Models und IRL/Reward Models als getrennte Modellfamilien. Wichtig: keine Online-Selbstoptimierung im Reflex Layer, keine Modellpromotion ohne Benchmark, Shadow Mode, Rollback, Reward-Audit und Action-Contract-Gates. Done when: docs/learning-layer.md existiert, Masterplan/AGENTS/Skill/README/Core-Konzept die Learning-Grenzen nennen und make test/lint/typecheck gruen sind.
```

### Prompt 12 - Emergent Autonomy und Goal Generation

```text
Erweitere OSIP um emergente Autonomie. Nutze osip_autonomie.md als Ideengeber und dokumentiere eine Goal Generation Engine, die Surprise/Prediction Error, epistemischen Wert und digitale Homoeostase in auditierbare goal.packet-Kandidaten uebersetzt. Wichtig: Goal-Packets sind Zielhypothesen, keine direkten Aktionen; jede Wirkung laeuft weiter ueber Profile, Policies, Simulation, Benchmarks und Action Contracts. Done when: docs/emergent-autonomy.md existiert, Masterplan/AGENTS/Skill/README/Core-Konzept/OSIP-Spec die Goal-Grenzen nennen und make test/lint/typecheck gruen sind.
```

---

## 21. Vorschlag für AGENTS.md

Codex soll diese Datei in gekürzter Form im Repo-Root anlegen.

```markdown
# AGENTS.md — OmniSense Runtime

## Project Goal

Build OmniSense Runtime: an open, modular, simulation-first Perception-to-Action system for intelligent rooms. Specialized sensory models publish OSIP Percept Packets; a context engine fuses them into operational room context; a bounded decision runtime triggers actions through Action Contracts.

## Read First

- Read `Masterplan.md` before making architectural changes.
- Keep `AGENTS.md` concise. Put detailed planning in `Masterplan.md` or docs.

## Architecture Rules

- Interface-first: public schemas before internal logic.
- Simulation-first: no real hardware required for tests.
- No monoliths: keep OSIP, bus, context, decision, simulator, gateway and SDK separated.
- No LLM or external network calls in Reflex Layer.
- No action without ActionContract.
- Every Percept must include schema_version, source_model, modality, timestamp, valid_for_ms, latency_ms, claims and quality.
- Every ContextUpdate must include evidence when it claims an event.
- Every public schema change must update tests and docs.

## Commands

- `make test` — run tests
- `make lint` — run ruff
- `make format` — format code
- `make typecheck` — run type checks when configured
- `make benchmark` — run scenario benchmarks when implemented

## Done Means

- Tests pass.
- New behavior has tests.
- Public interfaces are documented.
- No hardware dependency in CI.
- Summary includes changed files, decisions and tests run.
```

---

## 22. Qualitäts- und Review-Checkliste

Bei jedem größeren PR prüfen:

### Architektur

- [ ] Bleibt die Änderung modular?
- [ ] Ist das Core-System unabhängig vom konkreten Modell?
- [ ] Sind neue Adapter wirklich Adapter, nicht Core-Logik?
- [ ] Ist die Schnittstelle versioniert?

### Echtzeitfähigkeit

- [ ] Keine unnötigen Blocking Calls im Fast Path?
- [ ] Keine Datenbankpflicht vor Action Proposal?
- [ ] Keine LLM-Abhängigkeit im Reflex Layer?
- [ ] Latenzmetriken vorhanden?

### Schemas

- [ ] Pydantic-Modelle aktualisiert?
- [ ] JSON Schemas aktualisiert?
- [ ] Beispiele aktualisiert?
- [ ] Negative Tests vorhanden?

### Context Engine

- [ ] Evidence enthalten?
- [ ] Widersprüche abgebildet?
- [ ] Sensorqualität berücksichtigt?
- [ ] verspätete Percepts behandelt?

### Decision Runtime

- [ ] Action Contract vorhanden?
- [ ] Preconditions geprüft?
- [ ] Confidence Threshold geprüft?
- [ ] Cooldown vorhanden?
- [ ] Idempotency vorhanden?
- [ ] ActionResult verarbeitet?

### Tests

- [ ] Unit Tests
- [ ] Integration Tests
- [ ] Contract Tests
- [ ] Scenario Replay
- [ ] Fault Injection, sofern relevant

---

## 23. Minimaler End-to-End-Erfolg

Der erste echte Erfolg des Projekts ist erreicht, wenn dieser Ablauf funktioniert:

```text
1. Ein simuliertes chemisches Modell veröffentlicht chemical.air.smoke_like_pattern.
2. Ein simuliertes Thermal-Modell veröffentlicht thermal.stove.hotspot.
3. Ein simuliertes Object-State-Modell veröffentlicht object.stove.power_on.
4. Der Context Bus transportiert alle Percepts.
5. Die Context Engine erzeugt context.possible_burning_food.
6. Die Decision Runtime findet passende Action Contracts.
7. Sie erzeugt action.notify.local und action.hvac.ventilation_boost.
8. Ein Action Executor Stub führt die Commands aus.
9. Der Benchmark misst die End-to-End-Latenz.
10. Der Report zeigt Evidence, Context, Action und Latenzen.
```

Das ist der Machbarkeitsbeweis für:

> spezialisierte Sinnesmodelle → gemeinsames Interface → Kontextfusion → autonome Aktion.

---

## 24. Erweiterungspfad nach dem MVP

Nach dem MVP:

1. NATS Adapter produktionsreifer machen.
2. MQTT Bridge für IoT-Geräte bauen.
3. ROS 2 Adapter für Robotik/Echtzeit-Hardware bauen.
4. EmbeddingRef und Embedding Store integrieren.
5. Context Graph persistierbar machen.
6. Modell-Plug-in-System verbessern.
7. Dashboard erweitern.
8. reale Sensoradapter ergänzen.
9. Learned Fusion Modelle experimentell ergänzen.
10. wissenschaftlichen Benchmark veröffentlichen.

---

## 25. Forschungsoutputs

Das Projekt soll am Ende diese Artefakte liefern:

1. **OSIP v0.1 Spezifikation**  
   Offenes Percept-, Context- und Action-Protokoll.

2. **Referenzruntime**  
   Lauffähige modulare Runtime mit Bus, Context Engine und Decision Runtime.

3. **Simulationsbenchmark**  
   Reproduzierbare Szenarien für Kitchen Safety, Fall Candidate und Smart Comfort.

4. **Latency- und Robustness-Report**  
   Beweis der reaktiven Entscheidungspfade.

5. **API-Spezifikationen**  
   OpenAPI, AsyncAPI und JSON Schemas.

6. **Demo-Anwendungen**  
   Mindestens drei End-to-End-Demos.

7. **Modelladapter-Beispiele**  
   Beispiel, wie ein neues Sinnesmodell ohne Core-Änderung integriert wird.

---

## 26. Wichtigste Designentscheidungen

### 26.1 Interface vor Modell

Das Forschungsprojekt gewinnt nicht dadurch, dass sofort perfekte Modelle existieren. Es gewinnt dadurch, dass gute und schlechte Modelle gleichermaßen über dieselbe Schnittstelle integrierbar sind.

### 26.2 Bounded Autonomy statt allgemeiner KI

Das System muss keine allgemeine Weltlogik lösen. Es muss für definierte Kontexte schnell und begrenzt handeln.

### 26.3 Reflex ist kein Planner

Der Reflex Layer ist bewusst klein, schnell und begrenzt. Komplexere KI darf nur im Deliberative Layer laufen.

### 26.4 Simulation ist ein Feature

Simulation ist keine Notlösung. Sie ist der Mechanismus, um die Schnittstelle und Beweisführung reproduzierbar zu machen.

### 26.5 Action Contracts sind das Sicherheitsgeländer

Autonomie entsteht nicht durch freie Aktionen. Autonomie entsteht durch schnelle Auswahl aus erlaubten, geprüften, maschinenlesbaren Action Contracts.

---

## 27. Dokumentationsstandard

Jedes Modul braucht eine kurze `README.md` oder Modul-Dokumentation mit:

- Zweck,
- öffentliche Interfaces,
- Beispiel,
- Tests,
- bekannte Grenzen.

Öffentliche Spezifikationen gehören nach `docs/` und `protocols/`.

---

## 28. Beispiel: End-to-End-Pipeline in Pseudocode

```python
async def main() -> None:
    bus = InMemoryBus()
    context_engine = ContextEngine(bus=bus, fusion=WeightedFusion())
    decision_runtime = DecisionRuntime(bus=bus, contracts=load_contracts())
    simulator = ScenarioReplayRunner(bus=bus)

    await context_engine.start()
    await decision_runtime.start()

    result = await simulator.run("scenarios/kitchen_burning_food.yaml")

    assert "context.possible_burning_food" in result.contexts
    assert "action.hvac.ventilation_boost" in result.actions
    assert result.latency.p95_action_proposal_ms < 500
```

---

## 29. Offene Forschungsfragen für spätere Iterationen

1. Welche Felder sind wirklich minimal notwendig im Percept Packet?
2. Wie gut funktioniert gewichtete Fusion gegenüber Graph Fusion?
3. Wie werden Konfidenzen zwischen Modellen kalibriert?
4. Wie stark verbessert Sensorqualität/Drift-Score die Kontextstabilität?
5. Wie werden langsamere Modalitäten wie Geruch mit schnellen Modalitäten wie Audio synchronisiert?
6. Wie viel Kontext-Historie ist nötig, bevor Latenz leidet?
7. Welche Action Contracts sind ausreichend expressiv, ohne zu komplex zu werden?
8. Wie lassen sich neue Modelle registrieren, ohne semantisches Label-Chaos zu erzeugen?
9. Wie kann ein Drittmodell beweisen, welche Claims es unterstützt?
10. Wann braucht das System gelerntes Fusion-Modelling statt Regeln?

---

## 30. Aktuelle Priorität

Die nächsten Aufgaben sind in dieser Reihenfolge umzusetzen:

1. Repository Foundation.
2. OSIP Schemas.
3. In-memory Bus.
4. Scenario Replay.
5. Context Engine v0.1.
6. Decision Runtime v0.1.
7. Gateway API.
8. Benchmark Runner.
9. Application Profiles: Grundkonzept/Core von Anwendungen trennen, `rooms` als MVP-Profil fuehren, `physical-ai` als spaeteres Profil vorbereiten und `xxx` als andockbares Profil-Template vorsehen.
10. Experience & Learning Layer: Trace-, Dataset-, Model-Card-, Registry- und Promotion-Gates vorbereiten, bevor echte ML-Modelle aus OSIP-Erfahrungen trainiert oder produktiv genutzt werden.
11. Emergent Autonomy: Goal Generation Engine, `goal.packet`, Surprise-/Epistemic-/Homeostatic-Scores und Goal-to-Contract-Gates vorbereiten, bevor autonom generierte Ziele runtimewirksam werden.

Codex soll keine Hardwareadapter, kein Dashboard, keine komplexen ML-Modelle, keine Goal-Generatoren mit Live-Wirkung und keine direkte physische Aktorsteuerung bauen, bevor die MVP-Pipeline funktioniert. Die Learning Layer beginnt deshalb mit offenen Trace-/Dataset-Vertraegen und Governance, nicht mit einem trainierten Produktionsmodell. Emergent Autonomy beginnt mit Doku, `goal.packet`-Entwurf, Simulation, Negative Tests und Contract-Gates, nicht mit freier Zielausfuehrung. Neue Anwendungsdomaenen beginnen als Application Profile mit Docs, Vokabular, Fixtures, Simulation, Safety Bounds und Adapter-Design, nicht als Core-Umbau.

---

## 31. Quellen und Anschluss an bestehende Standards

Diese Quellen sind als Hintergrund relevant, aber das Projekt soll unabhängig lauffähig bleiben:

- OpenAI Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex best practices: https://developers.openai.com/codex/learn/best-practices
- OpenAI Codex customization: https://developers.openai.com/codex/concepts/customization
- OpenAI Codex skills: https://developers.openai.com/codex/skills
- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- AsyncAPI Specification: https://www.asyncapi.com/docs/reference/specification/latest
- CloudEvents: https://cloudevents.io/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- W3C PROV Overview: https://www.w3.org/TR/prov-overview/
- OpenLineage documentation: https://openlineage.io/docs/
- MLflow Model Registry: https://mlflow.org/docs/latest/ml/model-registry/
- Model Cards for Model Reporting: https://arxiv.org/abs/1810.03993
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
- Distilling the Knowledge in a Neural Network: https://arxiv.org/abs/1503.02531
- World Models: https://arxiv.org/abs/1803.10122
- Algorithms for Inverse Reinforcement Learning: https://ai.stanford.edu/~ang/papers/icml00-irl.pdf
- Whence the Expected Free Energy?: https://arxiv.org/abs/2004.08128
- Expanding the Active Inference Landscape: https://arxiv.org/abs/1806.08083
- Active Inference and Epistemic Value in Graphical Models: https://arxiv.org/abs/2109.00541
- ROS 2 Middleware and QoS: https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Different-Middleware-Vendors.html
- ROS 2 QoS settings: https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html
- SDFormat specification for robot/world descriptions: https://sdformat.org/spec
- MuJoCo documentation: https://mujoco.readthedocs.io/en/stable/overview.html
- NVIDIA Isaac Sim documentation: https://docs.isaacsim.omniverse.nvidia.com/latest/index.html
- OpenUSD documentation: https://openusd.org/release/index.html
- ISO robot safety standards overview: https://www.iso.org/ics/25.040.30/x/

---

## 32. Ein-Satz-Ziel für das gesamte Projekt

> **OmniSense Runtime soll zeigen, dass offene, austauschbare Sinnesmodelle über ein gemeinsames Percept-Protokoll in Echtzeit zu Kontext und autonomen Aktionen fusioniert werden können — ohne monolithische KI und ohne unbounded autonomy.**
