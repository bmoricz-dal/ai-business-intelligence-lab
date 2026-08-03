"use client";

import { useMemo, useState, type CSSProperties } from "react";

type PathwayKey = "use" | "integrate" | "automate" | "configure";
type GateDecision = "not_reviewed" | "proceed" | "revise" | "stop";

const pathways: Record<PathwayKey, { label: string; fit: string; steps: string[] }> = {
  use: {
    label: "Use",
    fit: "Internal research, summaries and first drafts without a live system connection.",
    steps: [
      "Approve one controlled tool and its terms",
      "Define prohibited data and permitted tasks",
      "Create bounded prompts with sources and caveats",
      "Prepare known tasks and edge cases",
      "Run tests with intended users",
      "Score support, omissions and correction time",
      "Permit limited use with named approval",
      "Review usage, corrections and incidents",
    ],
  },
  integrate: {
    label: "Integrate",
    fit: "Coding, matching, reconciliation and close support inside an existing accounting platform.",
    steps: [
      "Select one measured ledger or close bottleneck",
      "Review supplier data flows, access, logs, export and exit",
      "Construct historical known cases and unusual items",
      "Compare suggestions, confidence, exceptions and review time",
      "Run two close cycles in shadow mode",
      "Approve a limited low-complexity client segment",
      "Route low-confidence, unusual and high-value items",
      "Prohibit automatic material postings and retain overrides",
      "Compare full effort, quality and cost after the pilot",
    ],
  },
  automate: {
    label: "Automate",
    fit: "Internal routing and draft actions with approval before communication or posting.",
    steps: [
      "Draw trigger, data, decision, action, review and log",
      "Use deterministic rules where ordinary rules are sufficient",
      "List every technically permitted action",
      "Make the first release read-only or draft-only",
      "Test wrong-client, duplicate, conflict and outage cases",
      "Shadow proposed actions against staff decisions",
      "Require approval before external messages or ledger action",
      "Monitor, pause, rollback and re-authorise after change",
    ],
  },
  configure: {
    label: "Configure",
    fit: "Retrieval over approved firm procedures, checklists and templates with citations.",
    steps: [
      "Define the knowledge question and authorised users",
      "Inventory document owners, versions, access and expiry",
      "Remove duplicates and obsolete material",
      "Restrict the corpus to approved sources",
      "Require document and section citations",
      "Test direct, conflicting, outdated and no-answer questions",
      "Pilot on internal procedures without client files",
      "Add refresh, deletion, access-review and incident processes",
      "Record the configure, build or no-build decision",
    ],
  },
};

const gateLabels = ["G0 Scope", "G1 Data", "G2 Known cases", "G3 Shadow", "G4 Pilot", "G5 Scale"];

const initialMetrics = {
  baselinePreparation: 40,
  baselineReview: 18,
  baselineCorrection: 6,
  pilotPreparation: 32,
  pilotReview: 20,
  pilotCorrection: 7,
  licence: 250,
  setup: 600,
  training: 350,
  assurance: 300,
  loadedRate: 35,
};

export function AdoptionWorkspace() {
  const [pathway, setPathway] = useState<PathwayKey>("integrate");
  const [employees, setEmployees] = useState(7);
  const [clients, setClients] = useState(180);
  const [workflow, setWorkflow] = useState("Reconciliation and month-end close");
  const [completed, setCompleted] = useState<Record<string, boolean>>({});
  const [gates, setGates] = useState<Record<string, GateDecision>>(
    Object.fromEntries(gateLabels.map((gate) => [gate, "not_reviewed"]))
  );
  const [metrics, setMetrics] = useState(initialMetrics);

  const active = pathways[pathway];
  const completedCount = active.steps.filter((_, index) => completed[`${pathway}-${index}`]).length;
  const progress = Math.round((completedCount / active.steps.length) * 100);

  const result = useMemo(() => {
    const baselineHours = metrics.baselinePreparation + metrics.baselineReview + metrics.baselineCorrection;
    const pilotHours = metrics.pilotPreparation + metrics.pilotReview + metrics.pilotCorrection;
    const hoursReleased = baselineHours - pilotHours;
    const directPilotCost = metrics.licence + metrics.setup + metrics.training + metrics.assurance;
    const grossCapacityValue = hoursReleased * metrics.loadedRate;
    return {
      baselineHours,
      pilotHours,
      hoursReleased,
      directPilotCost,
      grossCapacityValue,
      netCapacityValue: grossCapacityValue - directPilotCost,
    };
  }, [metrics]);

  const gateOutcome = useMemo(() => {
    const values = Object.values(gates);
    if (values.includes("stop")) return "STOP";
    if (values.includes("revise")) return "REVISE";
    if (values.every((value) => value === "proceed")) return "PROCEED";
    return "INCOMPLETE";
  }, [gates]);

  function setMetric(key: keyof typeof metrics, value: number) {
    setMetrics((current) => ({ ...current, [key]: Number.isFinite(value) ? Math.max(0, value) : 0 }));
  }

  function exportSession() {
    const payload = {
      exportedAt: new Date().toISOString(),
      notice: "Illustrative planning session. No client-identifiable or confidential data should be entered.",
      firm: { employees, clients, workflow },
      pathway,
      completedSteps: active.steps.filter((_, index) => completed[`${pathway}-${index}`]),
      gates,
      metrics,
      calculatedManagementEstimate: result,
      gateOutcome,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `accounting-ai-adoption-${pathway}-session.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function resetWorkspace() {
    setPathway("integrate");
    setEmployees(7);
    setClients(180);
    setWorkflow("Reconciliation and month-end close");
    setCompleted({});
    setGates(Object.fromEntries(gateLabels.map((gate) => [gate, "not_reviewed"])));
    setMetrics(initialMetrics);
  }

  return (
    <section className="adoptionWorkspace" id="adoption-planner" aria-labelledby="workspace-title">
      <div className="workspaceHeading">
        <div><p className="kicker">Secondary workspace · implementation planner</p><h2 id="workspace-title">Plan how your firm would test adoption</h2><p>After experiencing the demonstrations, replace the fictional assumptions with illustrative or aggregated operating figures. Entries stay in this browser session and are not sent to DAL.</p></div>
        <div className="workspaceSafety"><strong>Do not enter client data</strong><span>No names, tax identifiers, payroll records, bank details or confidential documents.</span></div>
      </div>

      <div className="workspaceLayout">
        <aside className="workspaceControls" aria-label="Practice and pathway settings">
          <fieldset><legend>1. Practice setup</legend>
            <label>Employees<input type="number" min="1" max="9" value={employees} onChange={(event) => setEmployees(Math.min(9, Math.max(1, Number(event.target.value))))} /></label>
            <label>Illustrative clients<input type="number" min="0" value={clients} onChange={(event) => setClients(Math.max(0, Number(event.target.value)))} /></label>
            <label>Workflow<select value={workflow} onChange={(event) => setWorkflow(event.target.value)}><option>Reconciliation and month-end close</option><option>Transaction categorisation</option><option>Internal technical research</option><option>Client document requests</option><option>Firm procedure retrieval</option></select></label>
          </fieldset>
          <fieldset><legend>2. Adoption method</legend>
            <div className="pathwayChooser">{(Object.keys(pathways) as PathwayKey[]).map((key) => <button type="button" key={key} aria-pressed={pathway === key} onClick={() => setPathway(key)}><b>{pathways[key].label}</b><span>{pathways[key].fit}</span></button>)}</div>
          </fieldset>
          <div className="workspaceActions"><button type="button" onClick={exportSession}>Export session</button><button type="button" className="secondary" onClick={resetWorkspace}>Reset demo</button></div>
        </aside>

        <div className="workspaceCanvas">
          <section className="workspacePanel pathwayPanel" aria-labelledby="active-pathway-title">
            <div className="workspacePanelHeader"><div><span>Selected method</span><h3 id="active-pathway-title">{active.label}</h3><p>{active.fit}</p></div><div className="progressDonut" style={{ "--progress": `${progress * 3.6}deg` } as CSSProperties}><strong>{progress}%</strong><span>complete</span></div></div>
            <ol className="workspaceSteps">{active.steps.map((step, index) => { const key = `${pathway}-${index}`; return <li key={key} className={completed[key] ? "isComplete" : ""}><label><input type="checkbox" checked={Boolean(completed[key])} onChange={(event) => setCompleted((current) => ({ ...current, [key]: event.target.checked }))} /><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong></label></li>; })}</ol>
          </section>

          <section className="workspacePanel" aria-labelledby="measurement-title">
            <div className="workspacePanelHeader"><div><span>Comparable period</span><h3 id="measurement-title">Baseline versus pilot</h3><p>Example values demonstrate the calculation. Replace them with non-sensitive, aggregated figures from the same workflow and period.</p></div></div>
            <div className="metricInputGrid">
              <fieldset><legend>Baseline hours</legend>{([['baselinePreparation','Preparation'],['baselineReview','Review'],['baselineCorrection','Correction']] as const).map(([key,label]) => <label key={key}>{label}<input type="number" min="0" step="0.5" value={metrics[key]} onChange={(event) => setMetric(key, Number(event.target.value))} /></label>)}</fieldset>
              <fieldset><legend>Pilot hours</legend>{([['pilotPreparation','Preparation'],['pilotReview','Review'],['pilotCorrection','Correction']] as const).map(([key,label]) => <label key={key}>{label}<input type="number" min="0" step="0.5" value={metrics[key]} onChange={(event) => setMetric(key, Number(event.target.value))} /></label>)}</fieldset>
              <fieldset><legend>Direct pilot cost (£)</legend>{([['licence','Licences'],['setup','Setup'],['training','Training'],['assurance','Assurance']] as const).map(([key,label]) => <label key={key}>{label}<input type="number" min="0" step="10" value={metrics[key]} onChange={(event) => setMetric(key, Number(event.target.value))} /></label>)}<label>Loaded hourly cost<input type="number" min="0" step="1" value={metrics.loadedRate} onChange={(event) => setMetric("loadedRate", Number(event.target.value))} /></label></fieldset>
            </div>
            <div className="workspaceResults" aria-live="polite">
              <article><span>Baseline</span><strong>{result.baselineHours.toFixed(1)} h</strong></article>
              <article><span>Pilot</span><strong>{result.pilotHours.toFixed(1)} h</strong></article>
              <article><span>Hours released</span><strong>{result.hoursReleased.toFixed(1)} h</strong></article>
              <article><span>Direct pilot cost</span><strong>£{result.directPilotCost.toFixed(0)}</strong></article>
              <article><span>Net capacity estimate</span><strong className={result.netCapacityValue < 0 ? "negative" : ""}>£{result.netCapacityValue.toFixed(0)}</strong></article>
            </div>
            <p className="workspaceFootnote">This is a firm-specific illustrative management calculation—not ROI evidence. Add any omitted supplier, incident, opportunity or ongoing governance costs before making a decision.</p>
          </section>

          <section className="workspacePanel gatePanel" aria-labelledby="gate-title">
            <div className="workspacePanelHeader"><div><span>Decision control</span><h3 id="gate-title">Six gates</h3><p>A stop decision overrides the other gates. Revise means change the design and retest.</p></div><div className={`gateOutcome ${gateOutcome.toLowerCase()}`}><span>Current outcome</span><strong>{gateOutcome}</strong></div></div>
            <div className="gateDecisionGrid">{gateLabels.map((gate) => <label key={gate}><span>{gate}</span><select value={gates[gate]} onChange={(event) => setGates((current) => ({ ...current, [gate]: event.target.value as GateDecision }))}><option value="not_reviewed">Not reviewed</option><option value="proceed">Proceed</option><option value="revise">Revise</option><option value="stop">Stop</option></select></label>)}</div>
          </section>
        </div>
      </div>
    </section>
  );
}
