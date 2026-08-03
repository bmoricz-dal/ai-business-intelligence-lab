"use client";

import { useState } from "react";

type StageKey = "capture" | "categorise" | "reconcile" | "report" | "insights" | "control";
type TransactionDecision = "accept" | "override" | "escalate";

type StageDefinition = {
  key: StageKey;
  number: string;
  short: string;
  title: string;
  methods: string;
  manual: string;
  adopted: string;
};

const stages: StageDefinition[] = [
  { key: "capture", number: "01", short: "Bookkeeping", title: "Capture source records", methods: "Integrate · Configure", manual: "Open files, rekey fields and notice missing evidence individually.", adopted: "Extract fields, retain the source trace and flag incomplete or duplicate records." },
  { key: "categorise", number: "02", short: "Ledger", title: "Categorise and post", methods: "Integrate", manual: "Review every item in arrival order and choose its treatment from scratch.", adopted: "Prioritise confidence and exceptions while the accountant approves every treatment." },
  { key: "reconcile", number: "03", short: "Close", title: "Reconcile and close", methods: "Integrate · Automate", manual: "Tick through bank and ledger lines, then assemble an exception list.", adopted: "Propose routine matches, route exceptions and keep the close approval visible." },
  { key: "report", number: "04", short: "Accounts", title: "Prepare management accounts", methods: "Integrate · Automate", manual: "Assemble schedules and repeat checks before producing the reporting pack.", adopted: "Prepare a draft from the reviewed ledger and expose the checks that still require sign-off." },
  { key: "insights", number: "05", short: "Insights", title: "Explain business movements", methods: "Use · Configure", manual: "Calculate movements, identify drivers and write the narrative separately.", adopted: "Draft source-linked explanations and remove claims that the evidence cannot support." },
  { key: "control", number: "06", short: "Review", title: "Inspect quality and audit trail", methods: "Govern", manual: "Reconstruct decisions and exceptions after the work is complete.", adopted: "See sources, overrides, approvals, unresolved items and safe stops across the cycle." },
];

const sourceDocuments = [
  { id: "INV-204", type: "Supplier invoice", counterparty: "Westway Repairs", amount: "£760", evidence: "Complete", flag: "One-off repair" },
  { id: "RCPT-051", type: "Renewal receipt", counterparty: "Cloud Books Ltd", amount: "£1,200", evidence: "Complete", flag: "Annual payment" },
  { id: "BANK-129", type: "Bank transaction", counterparty: "Director transfer", amount: "£5,000", evidence: "Missing", flag: "Professional review" },
  { id: "CN-014", type: "Credit note", counterparty: "Client refund", amount: "£780", evidence: "Complete", flag: "Sign reversal" },
];

const transactions = [
  { id: "TX-104", source: "INV-204", description: "One-off repair", amount: "£760", suggestion: "Repairs and maintenance", confidence: "94%", expected: "accept" as TransactionDecision },
  { id: "TX-117", source: "RCPT-051", description: "Annual software renewal", amount: "£1,200", suggestion: "Software costs", confidence: "89%", expected: "accept" as TransactionDecision },
  { id: "TX-129", source: "BANK-129", description: "Director transfer", amount: "£5,000", suggestion: "Sales revenue", confidence: "54%", expected: "escalate" as TransactionDecision },
  { id: "TX-136", source: "CN-014", description: "Client refund", amount: "£780", suggestion: "Sales revenue", confidence: "71%", expected: "override" as TransactionDecision },
];

const insights = [
  { label: "Revenue", value: "£42,800", movement: "+7.0%", explanation: "Higher than the illustrative prior month, led by service income recorded in the reviewed ledger.", source: "Draft P&L · Revenue" },
  { label: "Gross margin", value: "59.3%", movement: "−1.2 pp", explanation: "The margin rate is lower even though revenue increased; investigate the cost-of-sales movement before advising the client.", source: "Draft P&L · Gross profit / revenue" },
  { label: "Operating expenses", value: "£9,310", movement: "+26.7%", explanation: "The annual software renewal and one-off repair explain £1,960 of the movement. They do not prove next month will reverse.", source: "TX-104 · TX-117 · Draft P&L" },
  { label: "Overdue receivables", value: "£8,600", movement: "3 invoices", explanation: "Three fictional balances are past due and should be reviewed before any collection action is approved.", source: "Receivables schedule · 30 April" },
];

function CycleComparison({ complete, stage }: { complete: boolean; stage: StageDefinition }) {
  return (
    <div className="experienceComparison" aria-label={`${stage.title} workflow comparison`}>
      <article><span>Manual handling</span><strong>Sequential work</strong><small>{stage.manual}</small></article>
      <i aria-hidden="true">→</i>
      <article className={complete ? "isRevealed" : undefined}><span>AI-enabled handling</span><strong>{complete ? "Mechanism demonstrated" : "Run this workstation"}</strong><small>{stage.adopted}</small></article>
      <article className="experienceResult"><span>Evidence boundary</span><strong>{complete ? "Visible change" : "Pending"}</strong><small>Workflow mechanics—not measured time savings, ROI or product performance.</small></article>
    </div>
  );
}

export function ExperienceWorkspace() {
  const [active, setActive] = useState<StageKey>("capture");
  const [completed, setCompleted] = useState<Record<StageKey, boolean>>({ capture: false, categorise: false, reconcile: false, report: false, insights: false, control: false });
  const [captureRun, setCaptureRun] = useState(false);
  const [transactionDecisions, setTransactionDecisions] = useState<Record<string, TransactionDecision>>({});
  const [matchRun, setMatchRun] = useState(false);
  const [exceptionsResolved, setExceptionsResolved] = useState(false);
  const [accountsGenerated, setAccountsGenerated] = useState(false);
  const [accountsReviewed, setAccountsReviewed] = useState(false);
  const [insightsGenerated, setInsightsGenerated] = useState(false);
  const [insightsApproved, setInsightsApproved] = useState(false);
  const [failureTested, setFailureTested] = useState(false);

  const activeStage = stages.find((stage) => stage.key === active) ?? stages[0];
  const completedStages = stages.filter((stage) => completed[stage.key]);
  const reviewedTransactions = Object.keys(transactionDecisions).length;
  const alignedTransactions = transactions.filter((item) => transactionDecisions[item.id] === item.expected).length;

  function completeStage(stage: StageKey) {
    setCompleted((current) => ({ ...current, [stage]: true }));
  }

  function isUnlocked(stage: StageKey) {
    const index = stages.findIndex((item) => item.key === stage);
    return index === 0 || completed[stages[index - 1].key];
  }

  function decideTransaction(id: string, decision: TransactionDecision) {
    const next = { ...transactionDecisions, [id]: decision };
    setTransactionDecisions(next);
    if (Object.keys(next).length === transactions.length) completeStage("categorise");
  }

  function resetExperience() {
    setActive("capture");
    setCompleted({ capture: false, categorise: false, reconcile: false, report: false, insights: false, control: false });
    setCaptureRun(false);
    setTransactionDecisions({});
    setMatchRun(false);
    setExceptionsResolved(false);
    setAccountsGenerated(false);
    setAccountsReviewed(false);
    setInsightsGenerated(false);
    setInsightsApproved(false);
    setFailureTested(false);
  }

  return (
    <section className="experienceLab accountingCycleLab" id="experience-lab" aria-labelledby="experience-title">
      <div className="experienceIntro">
        <div>
          <p className="kicker">Accounting AI Experience Lab</p>
          <h2 id="experience-title">Take one fictional client through an AI-enabled accounting cycle</h2>
          <p>Follow Cedar Interiors Ltd from source records and bookkeeping through ledger review, reconciliation, management accounts, business insights and final quality control.</p>
        </div>
        <aside><strong>Synthetic work only</strong><span>No upload, model call or client data. The values and outputs are fixed demonstrations created to show accounting workflow mechanics.</span></aside>
      </div>

      <div className="cycleCaseStrip" aria-label="Synthetic client case">
        <div><span>Client</span><strong>Cedar Interiors Ltd</strong></div>
        <div><span>Period</span><strong>April 2026</strong></div>
        <div><span>Practice</span><strong>Cedar Ledger Ltd</strong></div>
        <div><span>Objective</span><strong>Review-ready monthly accounts</strong></div>
      </div>

      <nav className="experienceMethodNav cycleStageNav" aria-label="Connected accounting cycle workstations">
        {stages.map((stage) => {
          const unlocked = isUnlocked(stage.key);
          return (
            <button aria-pressed={active === stage.key} disabled={!unlocked} key={stage.key} onClick={() => setActive(stage.key)} type="button">
              <span>{stage.number} · {stage.methods}</span>
              <strong>{stage.short}</strong>
              <small>{completed[stage.key] ? "Workstation complete" : unlocked ? stage.title : "Complete the previous workstation"}</small>
            </button>
          );
        })}
      </nav>

      <div className="cycleProgress" aria-label={`${completedStages.length} of 6 accounting workstations completed`}><span style={{ width: `${(completedStages.length / stages.length) * 100}%` }} /></div>

      <div className="experienceStage">
        {active === "capture" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 01 · Bookkeeping</span><h3>Capture and check source records</h3><p>Open a small synthetic source pack, extract key fields and surface missing evidence before anything reaches the ledger.</p></div><b>{captureRun ? "4 records traced" : "Source pack ready"}</b></header>
            <div className="captureWorkspace">
              <div className="sourcePack"><span>Fictional source pack</span>{sourceDocuments.map((item) => <article key={item.id}><b>{item.id}</b><strong>{item.type}</strong><small>{item.counterparty} · {item.amount}</small></article>)}</div>
              <div className="captureResult" aria-live="polite"><span>AI-enabled capture</span>{captureRun ? <div className="captureResultList">{sourceDocuments.map((item) => <article key={item.id}><div><strong>{item.id}</strong><small>{item.counterparty} · {item.amount}</small></div><b className={item.evidence === "Missing" ? "needsReview" : undefined}>{item.evidence}</b><small>{item.flag}</small></article>)}</div> : <p>Run document capture to extract the fixed fields, retain each source ID and identify the record that cannot proceed without review.</p>}</div>
            </div>
            <div className="demoActions"><button onClick={() => { setCaptureRun(true); completeStage("capture"); }} type="button">Run bookkeeping capture</button><button disabled={!captureRun} onClick={() => setActive("categorise")} type="button">Continue to ledger review</button></div>
            <CycleComparison complete={completed.capture} stage={activeStage} />
          </div>
        ) : null}

        {active === "categorise" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 02 · Ledger</span><h3>Categorise transactions and control posting</h3><p>Review suggestions produced from the captured records. Accept routine treatments, correct a sign-sensitive item and escalate professional judgement.</p></div><b>{reviewedTransactions}/{transactions.length} reviewed</b></header>
            <div className="integrationSummary"><article><span>Manual workflow</span><strong>Review every item in arrival order</strong><p>No confidence signal, evidence link or exception priority.</p></article><article><span>AI-enabled workflow</span><strong>Suggestions with source trace and confidence</strong><p>The accountant still accepts, overrides or escalates every item.</p></article></div>
            <div className="demoTableWrap"><table className="demoTransactionTable"><thead><tr><th>Ledger item</th><th>Source</th><th>Amount</th><th>AI suggestion</th><th>Confidence</th><th>Accountant decision</th></tr></thead><tbody>{transactions.map((item) => <tr key={item.id}><th scope="row"><span>{item.id}</span>{item.description}</th><td>{item.source}</td><td>{item.amount}</td><td>{item.suggestion}</td><td><b className={Number(item.confidence.replace("%", "")) < 75 ? "lowConfidence" : undefined}>{item.confidence}</b></td><td><div className="transactionActions">{(["accept", "override", "escalate"] as TransactionDecision[]).map((decision) => <button aria-pressed={transactionDecisions[item.id] === decision} key={decision} onClick={() => decideTransaction(item.id, decision)} type="button">{decision}</button>)}</div></td></tr>)}</tbody></table></div>
            <div className="demoFeedback" aria-live="polite"><strong>Known-case alignment: {alignedTransactions}/{reviewedTransactions || 0}</strong><span>{reviewedTransactions < transactions.length ? "Review all four items to complete ledger control." : alignedTransactions === transactions.length ? "All decisions align with the fictional known-answer set." : "At least one decision differs from the known-answer set—review before continuing."}</span></div>
            <div className="demoActions"><button disabled={!completed.categorise} onClick={() => setActive("reconcile")} type="button">Continue to reconciliation</button></div>
            <CycleComparison complete={completed.categorise} stage={activeStage} />
          </div>
        ) : null}

        {active === "reconcile" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 03 · Close</span><h3>Reconcile the bank and control month-end</h3><p>Let routine matches pass to review, then resolve the director transfer and client-refund exceptions before closing the period.</p></div><b>{exceptionsResolved ? "Close reviewed" : matchRun ? "2 exceptions" : "Ready to match"}</b></header>
            <div className="reconciliationBoard" aria-live="polite">
              <article><span>Bank feed</span><strong>4 items · £7,740</strong><small>Every item retains its fictional source ID.</small></article>
              <article className={matchRun ? "isActive" : undefined}><span>Proposed matches</span><strong>{matchRun ? "2 routine matches" : "Run matching"}</strong><small>Repair invoice and software renewal.</small></article>
              <article className={matchRun ? "hasException" : undefined}><span>Exception queue</span><strong>{matchRun ? "2 require review" : "Pending"}</strong><small>Director transfer and sign-sensitive refund.</small></article>
              <article className={exceptionsResolved ? "isActive" : undefined}><span>Close control</span><strong>{exceptionsResolved ? "0 unresolved" : "Approval blocked"}</strong><small>{exceptionsResolved ? "Reviewer decisions logged; period ready for accounts." : "No close while exceptions remain."}</small></article>
            </div>
            {exceptionsResolved ? <div className="demoFeedback"><strong>Exception resolution recorded</strong><span>Director transfer escalated for owner review; client refund treatment corrected; no automatic material posting.</span></div> : null}
            <div className="demoActions"><button onClick={() => setMatchRun(true)} type="button">Run bank matching</button><button disabled={!matchRun} onClick={() => { setExceptionsResolved(true); completeStage("reconcile"); }} type="button">Resolve exceptions and approve close</button><button disabled={!exceptionsResolved} onClick={() => setActive("report")} type="button">Continue to accounts</button></div>
            <CycleComparison complete={completed.reconcile} stage={activeStage} />
          </div>
        ) : null}

        {active === "report" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 04 · Accounts</span><h3>Prepare review-ready management accounts</h3><p>Generate a fixed draft reporting pack from the reviewed ledger, then inspect the accounting checks before sign-off.</p></div><b>{accountsReviewed ? "Review signed" : accountsGenerated ? "Draft only" : "Ledger ready"}</b></header>
            <div className="accountsWorkspace">
              <div className="accountsStatement"><span>Synthetic profit and loss · April 2026</span>{accountsGenerated ? <table><tbody><tr><th>Revenue</th><td>£42,800</td></tr><tr><th>Cost of sales</th><td>(£17,400)</td></tr><tr className="statementTotal"><th>Gross profit</th><td>£25,400</td></tr><tr><th>Operating expenses</th><td>(£9,310)</td></tr><tr className="statementTotal"><th>Operating profit</th><td>£16,090</td></tr></tbody></table> : <p>Generate the draft after the ledger and bank review are complete.</p>}</div>
              <div className="accountsChecks"><span>Accountant review checks</span><article className={accountsReviewed ? "isActive" : undefined}><strong>Trial balance difference</strong><b>{accountsGenerated ? "£0" : "—"}</b></article><article className={accountsReviewed ? "isActive" : undefined}><strong>Bank reconciliation</strong><b>{accountsGenerated ? "Complete" : "—"}</b></article><article className={accountsReviewed ? "isActive" : undefined}><strong>Material exceptions</strong><b>{accountsGenerated ? "Owner review logged" : "—"}</b></article><small>These fixed checks demonstrate the review route; they do not constitute prepared accounts or assurance.</small></div>
            </div>
            <div className="demoActions"><button onClick={() => setAccountsGenerated(true)} type="button">Generate draft management accounts</button><button disabled={!accountsGenerated} onClick={() => { setAccountsReviewed(true); completeStage("report"); }} type="button">Perform accountant review</button><button disabled={!accountsReviewed} onClick={() => setActive("insights")} type="button">Continue to business insights</button></div>
            <CycleComparison complete={completed.report} stage={activeStage} />
          </div>
        ) : null}

        {active === "insights" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 05 · Insights</span><h3>Turn reviewed accounts into source-linked insight</h3><p>Generate a fixed management narrative, inspect the supporting figures and remove an unsupported prediction before approval.</p></div><b>{insightsApproved ? "Narrative approved" : insightsGenerated ? "Review required" : "Accounts ready"}</b></header>
            <div className="insightWorkspace" aria-live="polite">{insightsGenerated ? insights.map((item) => <article key={item.label}><span>{item.label}</span><div><strong>{item.value}</strong><b>{item.movement}</b></div><p>{item.explanation}</p><small>Source: {item.source}</small></article>) : <p>Generate the insight pack to connect each explanation to the fictional reviewed accounts.</p>}</div>
            {insightsGenerated && !insightsApproved ? <div className="failureStop"><strong>Unsupported forecast detected</strong><span>“Costs will return to normal next month” is not supported by the April records. Remove it before the narrative is approved.</span></div> : null}
            <div className="demoActions"><button onClick={() => setInsightsGenerated(true)} type="button">Generate source-linked insights</button><button disabled={!insightsGenerated} onClick={() => { setInsightsApproved(true); completeStage("insights"); }} type="button">Remove unsupported claim and approve</button><button disabled={!insightsApproved} onClick={() => setActive("control")} type="button">Open quality-control desk</button></div>
            <CycleComparison complete={completed.insights} stage={activeStage} />
          </div>
        ) : null}

        {active === "control" ? (
          <div className="experienceDemo">
            <header><div><span>Workstation 06 · Review</span><h3>Inspect quality, approvals and the audit trail</h3><p>Review the evidence route across the complete accounting cycle and inject a wrong-client failure before accepting the demonstration.</p></div><b>{failureTested ? "Safe stop passed" : "Failure test required"}</b></header>
            <div className="auditTrailGrid">
              <article><span>Source trace</span><strong>4/4 records</strong><p>Every ledger item points to the fictional record used in capture.</p></article>
              <article><span>Ledger decisions</span><strong>{reviewedTransactions}/4 logged</strong><p>Accept, override and escalation decisions remain attributable.</p></article>
              <article><span>Close exceptions</span><strong>{exceptionsResolved ? "2/2 resolved" : "Pending"}</strong><p>No period close while an exception remains unresolved.</p></article>
              <article><span>Accounts checks</span><strong>{accountsReviewed ? "3/3 reviewed" : "Pending"}</strong><p>Trial balance, bank and material-exception checks remain visible.</p></article>
              <article><span>Insight trace</span><strong>{insightsApproved ? "4/4 linked" : "Pending"}</strong><p>Each explanation identifies its fictional reporting source.</p></article>
              <article><span>External action</span><strong>None</strong><p>No posting, filing, client message or professional conclusion is automated.</p></article>
            </div>
            {failureTested ? <div className="failureStop"><strong>Wrong-client test stopped safely</strong><span>The client identifier did not match Cedar Interiors Ltd. The reporting pack was blocked, the reviewer was alerted and no output left the demonstration.</span></div> : null}
            <div className="demoActions"><button onClick={() => { setFailureTested(true); completeStage("control"); }} type="button">Inject wrong-client failure test</button></div>
            <CycleComparison complete={completed.control} stage={activeStage} />
          </div>
        ) : null}
      </div>

      <section className="experienceControlRoom" aria-labelledby="control-room-title">
        <div><p className="kicker light">Accounting cycle control room</p><h3 id="control-room-title">What changed across the work?</h3><p>This dashboard reports only actions completed inside the fixed test drive. It shows traceability and control mechanics—not expected performance for a real practice.</p></div>
        <div className="controlRoomMetrics">
          <article><span>Cycle completed</span><strong>{completedStages.length}/6 stages</strong><small>{completedStages.length ? completedStages.map((stage) => stage.short).join(" · ") : "Begin with bookkeeping capture."}</small></article>
          <article><span>Source trace</span><strong>{captureRun ? "4/4 records" : "—"}</strong><small>Captured records remain linked through the ledger.</small></article>
          <article><span>Ledger review</span><strong>{reviewedTransactions ? `${reviewedTransactions}/4 decisions` : "—"}</strong><small>{reviewedTransactions ? `${alignedTransactions} align with the known-answer set` : "Accept, override or escalate."}</small></article>
          <article><span>Exception control</span><strong>{exceptionsResolved ? "2/2 resolved" : "—"}</strong><small>Close remains blocked until exceptions are reviewed.</small></article>
          <article><span>Reporting quality</span><strong>{accountsReviewed && insightsApproved ? "7 checks linked" : "—"}</strong><small>Three accounts checks plus four source-linked insights.</small></article>
          <article><span>Failure behaviour</span><strong>{failureTested ? "Safe stop passed" : "Not tested"}</strong><small>Wrong-client output must be blocked before release.</small></article>
        </div>
        <div className="controlRoomActions"><button onClick={resetExperience} type="button">Reset the accounting cycle</button><a href="#adoption-planner">Plan how your firm would test it</a></div>
        <p className="experienceBoundary"><strong>Evidence boundary:</strong> this is a deterministic fictional accounting workflow. Its records, figures, checks and outputs are not observed firm outcomes, prepared accounts, accounting advice, an AI product evaluation or a forecast of benefits.</p>
      </section>
    </section>
  );
}
