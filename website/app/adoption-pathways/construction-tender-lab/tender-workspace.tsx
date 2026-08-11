"use client";

import { useMemo, useState } from "react";

const requirements = [
  { id: "R-01", clause: "2.1", title: "Provide three comparable refurbishment projects", evidence: "P-014 · Mill Lane Library", risk: "Evidence covers two projects; one remains missing." },
  { id: "R-02", clause: "3.4", title: "Confirm mobilisation within four weeks", evidence: "Programme v3 · mobilisation note", risk: "Programme assumption needs delivery-lead confirmation." },
  { id: "R-03", clause: "5.2", title: "Describe occupied-site safeguarding controls", evidence: "H&S library · draft control set", risk: "Specialist review required; do not generate a final method statement." },
  { id: "R-04", clause: "7.1", title: "Submit social-value commitments and measures", evidence: "Social value register · SV-08", risk: "Commitments need named owners and cost validation." },
];

const stages = ["Opportunity gate", "Requirements", "Evidence", "Draft control", "Challenge", "Assurance"];

export function TenderWorkspace() {
  const [stage, setStage] = useState(0);
  const [reviewed, setReviewed] = useState<string[]>([]);
  const [approved, setApproved] = useState<string[]>([]);
  const [resolved, setResolved] = useState<string[]>([]);
  const [baselineHours, setBaselineHours] = useState(48);
  const [pilotHours, setPilotHours] = useState(32);
  const [reviewHours, setReviewHours] = useState(8);

  const allReviewed = reviewed.length === requirements.length;
  const allApproved = approved.length === requirements.length;
  const allResolved = resolved.length === requirements.length;
  const decision = allReviewed && allApproved && allResolved ? "READY FOR HUMAN SIGN-OFF" : "HOLD";
  const netHours = baselineHours - pilotHours - reviewHours;
  const completion = Math.round(((reviewed.length + approved.length + resolved.length) / (requirements.length * 3)) * 100);

  const stageText = useMemo(() => [
    ["Decide whether to bid", "Check strategic fit, capacity, deadline and prohibited assumptions before any drafting."],
    ["Extract and verify requirements", "Compare each synthetic clause with the source wording. Marking it reviewed does not mean it is satisfied."],
    ["Match approved evidence", "Approve only evidence that is current, relevant and owned. Gaps stay visible."],
    ["Control the first draft", "A draft must point to its clause and evidence. Safety, pricing and commitments remain outside autonomous generation."],
    ["Challenge delivery and commercial risk", "Resolve, assign or hold every flagged assumption before submission assurance."],
    ["Run final human assurance", "The lab can organise evidence; an accountable person makes the submission decision."],
  ][stage], [stage]);

  function toggle(list: string[], setter: (value: string[]) => void, id: string) {
    setter(list.includes(id) ? list.filter((item) => item !== id) : [...list, id]);
  }

  function reset() { setStage(0); setReviewed([]); setApproved([]); setResolved([]); setBaselineHours(48); setPilotHours(32); setReviewHours(8); }

  function exportSession() {
    const payload = { scenario: "Northstar Build Ltd — fictional", decision, reviewed, approved, resolved, illustrativeHours: { baselineHours, pilotHours, reviewHours, netHours } };
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = "construction-tender-lab-session.json"; link.click(); URL.revokeObjectURL(url);
  }

  return <section className="tenderWorkspace" id="tender-lab">
    <header><div><span>FICTIONAL BID · COMMUNITY-CENTRE REFURBISHMENT</span><h2>Northstar Build Ltd tender control room</h2><p>Deterministic synthetic workflow. Inputs stay in this browser and are not sent to DAL or an AI model.</p></div><div className="tenderStatus"><span>Completion</span><strong>{completion}%</strong><i><b style={{width: `${completion}%`}} /></i></div></header>

    <nav aria-label="Tender workstations">{stages.map((label,index) => <button key={label} type="button" className={stage === index ? "active" : ""} onClick={() => setStage(index)}><span>{String(index+1).padStart(2,"0")}</span>{label}</button>)}</nav>

    <div className="tenderStageIntro"><div><span>WORKSTATION {stage+1}</span><h3>{stageText[0]}</h3><p>{stageText[1]}</p></div><strong className={decision === "HOLD" ? "hold" : "ready"}>{decision}</strong></div>

    {stage === 0 && <div className="tenderGate"><article><span>Strategic fit</span><strong>Conditional proceed</strong><p>Public-building refurbishment matches the fictional portfolio.</p></article><article><span>Capacity</span><strong>Needs confirmation</strong><p>Mobilisation overlaps one live project.</p></article><article><span>Prohibited delegation</span><strong>Human owned</strong><p>Final price, programme, safety method and contractual commitments.</p></article></div>}

    {stage === 1 && <div className="tenderRequirementList">{requirements.map((item) => <article key={item.id}><div><span>{item.id} · CLAUSE {item.clause}</span><strong>{item.title}</strong><p>{item.risk}</p></div><button type="button" aria-pressed={reviewed.includes(item.id)} onClick={() => toggle(reviewed,setReviewed,item.id)}>{reviewed.includes(item.id) ? "Reviewed ✓" : "Mark source reviewed"}</button></article>)}</div>}

    {stage === 2 && <div className="tenderRequirementList">{requirements.map((item) => <article key={item.id}><div><span>{item.id} · CANDIDATE EVIDENCE</span><strong>{item.evidence}</strong><p>{item.risk}</p></div><button type="button" aria-pressed={approved.includes(item.id)} onClick={() => toggle(approved,setApproved,item.id)}>{approved.includes(item.id) ? "Approved ✓" : "Approve evidence"}</button></article>)}</div>}

    {stage === 3 && <div className="tenderDraft"><article><span>SOURCE-LINKED FIRST DRAFT</span><h3>Response skeleton—not submission copy</h3><p>Northstar Build Ltd would begin by linking the client requirement to approved project evidence, then drafting only the factual structure supported by that evidence.</p><ul><li>Clause reference remains visible.</li><li>Unsupported third-project claim remains a gap.</li><li>Safety content routes to a competent reviewer.</li><li>Commitments remain unapproved until costed and owned.</li></ul></article><aside><span>Draft control</span><strong>{allReviewed && allApproved ? "Source chain assembled" : "Source chain incomplete"}</strong><p>Review and approve every requirement/evidence pair before the draft can move to challenge.</p></aside></div>}

    {stage === 4 && <div className="tenderRequirementList">{requirements.map((item) => <article key={item.id}><div><span>{item.id} · CHALLENGE</span><strong>{item.risk}</strong><p>Resolve only when an accountable owner has checked the underlying assumption.</p></div><button type="button" aria-pressed={resolved.includes(item.id)} onClick={() => toggle(resolved,setResolved,item.id)}>{resolved.includes(item.id) ? "Resolved ✓" : "Resolve / assign"}</button></article>)}</div>}

    {stage === 5 && <div className="tenderAssurance"><div><span>FINAL CONTROL RESULT</span><strong>{decision}</strong><p>{decision === "HOLD" ? "Return to requirements, evidence or challenge. At least one control remains incomplete." : "All simulated controls are complete. A human must still validate and authorise any real submission."}</p></div><dl><div><dt>Requirements reviewed</dt><dd>{reviewed.length}/{requirements.length}</dd></div><div><dt>Evidence approved</dt><dd>{approved.length}/{requirements.length}</dd></div><div><dt>Challenges resolved</dt><dd>{resolved.length}/{requirements.length}</dd></div></dl></div>}

    <section className="tenderPlanner" aria-label="Illustrative baseline versus pilot"><div><span>ILLUSTRATIVE MANAGEMENT CALCULATION</span><h3>Baseline versus pilot</h3><p>Replace these assumptions with measured local data. A positive hour balance is not ROI.</p></div><label>Baseline preparation hours<input type="number" min="0" value={baselineHours} onChange={(e) => setBaselineHours(Number(e.target.value))} /></label><label>Pilot preparation hours<input type="number" min="0" value={pilotHours} onChange={(e) => setPilotHours(Number(e.target.value))} /></label><label>Additional review/correction<input type="number" min="0" value={reviewHours} onChange={(e) => setReviewHours(Number(e.target.value))} /></label><div className="tenderNet"><span>Net capacity signal</span><strong>{netHours} hours</strong><small>Before licences, setup, training, assurance, incidents and opportunity cost.</small></div></section>

    <footer><button type="button" onClick={reset}>Reset fictional case</button><button type="button" onClick={exportSession}>Export session</button><p>No uploads. No real bid, price, programme, method statement, safety or regulatory decision.</p></footer>
  </section>;
}
