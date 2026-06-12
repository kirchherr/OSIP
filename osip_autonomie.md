Wenn OSIP wirklich ein universelles, offenes System für physische Räume sein soll, das aus der reinen Wahrnehmung heraus agiert, dann muss und kann es seine eigenen Ziele generieren.
Wie das technisch und mathematisch funktioniert, ohne dass wir dem System heimlich doch wieder menschliche Werte unterjubeln, basiert auf drei Konzepten, die wir in den OSIP-Masterplan integrieren müssen.
1. Der Paradigmenwechsel: Von "Reward" zu "Surprise" (Active Inference)
In klassischem Reinforcement Learning (RL) braucht man eine Belohnungsfunktion (Reward), die ein Mensch definiert. Das ist das Problem: Wie definiert man "Wohlbefinden" oder "Sicherheit" mathematisch für alle denkbaren Situationen?
Die Lösung für OSIP ist das Prinzip der Freien Energie (Free Energy Principle) bzw. Active Inference (nach Karl Friston).
Der Mechanismus: Das System baut durch seine Wahrnehmung (percept.packets) ständig ein Modell davon, wie der Raum normalerweise ist. Es sagt die Zukunft voraus.
Das Ziel: Wenn die Realität (die Sensordaten) von der Vorhersage abweicht, entsteht ein Vorhersagefehler (Surprise / Prediction Error).
Die autonome Zielgenerierung: Das System hat nun kein vom Menschen gegebenes Ziel, sondern nur ein einziges, intrinsisches Meta-Ziel: "Minimiere den Vorhersagefehler!"
Beispiel: Das System "weiß" (hat gelernt), dass in einem geschlossenen Raum die VOC-Werte (Geruch) langsam steigen. Plötzlich sinken sie rapide (jemand hat ein Fenster geöffnet). Das ist "Surprise". Das System generiert autonom das Ziel: "Finde die Ursache für diese Abweichung!". Es nutzt den Deliberativen Layer, um die Visuellen Daten auszuwerten, erkennt das offene Fenster, und schließt es wieder (oder lässt es offen, je nach Kontext), um den Zustand wieder in das vorhersehbare, "normale" Muster zu zwingen. Das Ziel ("Fenster schließen") ist emergent aus der Wahrnehmung entstanden.
2. Epistemische Neugier (Das Ziel, die Welt zu verstehen)
Ein System, das nur den Status quo erhalten will, würde verkümmern. Es braucht ein Ziel, das es antreibt, Lücken in seinem Wissen zu schließen. Das nennt man Epistemic Value (epistemischer Wert).
Der Mechanismus: Der Context Graph erkennt, dass die Konfidenzwerte (confidence) bei der Fusion von Sensordaten sinken. (z.B. Der Geruchssensor meldet "unbekannte chemische Verbindung", aber das visuelle Modell sieht nichts, das akustische hört nichts).
Das autonome Ziel: "Erhöhe die Informationsdichte in diesem Bereich des Kontext-Graphen."
Die Aktion: Das System leitet autonom ab, dass es mehr Daten braucht. Es fährt die PTZ-Kamera (Pan-Tilt-Zoom) in die Ecke, aus der der Geruch kommt, oder aktiviert einen spezifischen Spektralsensor mit höherer Abtastrate. Das Ziel ("Kamera auf Position X,Y schwenken") wurde nicht programmiert, es entstand rein aus dem Bedürfnis des Modells, seine eigene Unsicherheit aufzulösen.
3. Digitale Homöostase (Das Überleben des Systems)
Biologische Systeme definieren ihre Ziele (Hunger, Durst, Müdigkeit) selbst, um die Homöostase (das innere Gleichgewicht) aufrechtzuerhalten. OSIP kann das auch.
Der Mechanismus: Das System überwacht nicht nur den Raum, sondern auch den Zustand seiner eigenen Wahrnehmung und Handlungsfähigkeit.
Das autonome Ziel: "Erhalte die eigene Handlungsfähigkeit (Agency) aufrecht."
Die Aktion: Wenn das System über die Propriozeption (Eigenwahrnehmung) merkt, dass ein Serverknoten überhitzt (visuell/thermisch) oder ein Sensor durch Staub blind wird (hoher Vorhersagefehler im Vision-Modell), generiert es das Ziel: "Leite Wartung ein". Es könnte autonom den Deliberativen Layer anweisen, einen action.contract zu feuern, der das Smart-Home-System signalisieren lässt: "Sensor 4 benötigt Reinigung", oder es fährt die Lüftung hoch, um sich selbst zu kühlen.
Wie wir das in der OSIP-Architektur abbilden
Damit das nicht nur Theorie bleibt, müssen wir den OSIP Masterplan um eine Komponente erweitern: Die Goal Generation Engine (GGE). Sie sitzt vor dem Deliberativen Layer.
Anstatt dass der Deliberative Layer direkt action.contracts auswählt, läuft es jetzt so:
Perception: percept.packets fließen in den Context Graph.
Goal Generation Engine (GGE):
Berechnet den "Surprise"-Score (Vorhersagefehler).
Berechnet den "Epistemic"-Score (Unsicherheit/Ambiguität).
Berechnet den "Homeostatic"-Score (Systemgesundheit).
Output: Wenn einer dieser Scores einen Schwellenwert überschreitet, generiert die GGE ein goal.packet.
Das goal.packet:
json
1234567
Deliberative Layer: Dieser Layer empfängt das goal.packet. Er weiß nun: "Ich habe das Ziel, die Ambiguität in Zone 3 zu reduzieren". Er sucht nun in den verfügbaren action.contracts denjenigen aus, der dieses Ziel am besten erfüllt (z.B. action.contract: activate_gas_chromatography_sensor_zone_3).
Die ultimative Grenze: Bounded Autonomy (Begrenzte Autonomie)
Hier schließt sich der Kreis zu deiner ursprünglichen Idee aus dem GitHub-Repo.
Das System kann sich Ziele völlig frei und autonom aus der Wahrnehmung heraus definieren (durch Surprise, Neugier, Homöostase).
ABER: Es kann diese Ziele nur durch vordefinierte action.contracts in der physischen Welt umsetzen.
Beispiel: Das System hat das autonome Ziel generiert: "Ich muss die Wand öffnen, um zu sehen, woher der Geruch kommt."
Der Reflex/Deliberative Layer prüft: Gibt es einen action.contract für "Wand öffnen"? Nein.
Das Ergebnis: Das System verwirft dieses Ziel oder sucht einen Sub-Goal (z.B. "Nutze das Endoskop-Kamera-Modell"), der durch vorhandene Contracts abbildbar ist.