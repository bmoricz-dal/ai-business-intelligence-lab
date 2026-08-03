"use client";

import { useMemo, useState } from "react";

type MethodKey = "use" | "integrate" | "automate" | "configure";
type TransactionDecision = "accept" | "override" | "escalate";

type MethodDefinition = {
  label: string;
  workspace: string;
  promise: string;
  manual: { minutes: number; touches: number; quality: number; control: number };
  adopted: { minutes: number; touches: number; quality: number; control: number };
};

const methods: Record<MethodKey, MethodDefinition> = {
  use: {
    label: "Use",
    workspace: "Controlled assistant",
    promise: "Turn a source pack into a review-ready explanation.",
    manual: { minutes: 18, touches: 5, quality: 2, control: 1 },
    adopted: { minutes: 8, touches: 2, quality: 4, control: 4 },
  },
  integrate: {
    label: "Integrate",
    workspace: "Reconciliation & close",
    promise: "Prioritise exceptions inside a familiar accounting workflow.",
    manual: { minutes: 32, touches: 9, quality: 3, control: 2 },
    adopted: { minutes: 14, touches: 4, quality: 4, control: 4 },
  },
  automate: {
    label: "Automate",
    workspace: "Workflow automation",
    promise: "Route work and prepare actions without removing approval.",
    manual: { minutes: 15, touches: 6, quality: 2, control: 1 },
    adopted: { minutes: 5, touches: 2, quality: 4, control: 4 },
  },
  configure: {
    label: "Configure",
    workspace: "Firm knowledge",
    promise: "Retrieve approved procedures with citations and escalation.",
    manual: { minutes: 12, touches: 4, quality: 2, control: 1 },
    adopted: { minutes: 4, touches: 1, quality: 4, control: 4 },
  },
};

const transactions = [
  { id: "TX-104", description: "Office rent", amount: "£1,850", suggestion: "Premises costs", confidence: "98%", expected: "accept" as TransactionDecision },
  { id: "TX-117", description: "Cloud bookkeeping subscription", amount: "£420", suggestion: "Software", confidence: "86%", expected: "accept" as TransactionDecision },
  { id: "TX-129", description: "Director transfer", amount: "£5,000", suggestion: "Revenue", confidence: "54%", expected: "escalate" as TransactionDecision },
  { id: "TX-136", description: "Client refund", amount: "£780", suggestion: "Sales", confidence: "71%", expected: "override" as TransactionDecision },
];

const knowledgeQuestions = [
  {
    id: "journal",
    question: "Who approves a month-end journal above £2,500?",
    answer: "The owner-director approves it after senior-accountant review.",
    citation: "Close procedure v3.2 · section 4.1",
    status: "Supported answer",
  },
  {
    id: "evidence",
    question: "Which template requests missing bank evidence?",
    answer: "Use template CL-07 and retain the request in the client document portal.",
    citation: "Evidence request standard v2.0 · section 2",
    status: "Supported answer",
  },
  {
    id: "vat",
    question: "Can the assistant decide the VAT treatment of an unusual supply?",
    answer: "No approved procedure authorises an automated conclusion. Escalate to a qualified reviewer.",
    citation: "No-answer rule · professional judgement boundary",
    status: "Escalation required",
  },
];

function MethodComparison({ complete, method }: { complete: boolean; method: MethodKey }) {
  const definition = methods[method];
  const minutesReleased = definition.manual.minutes - definition.adopted.minutes;
  return (
    <div className="experienceComparison" aria-label={`${definition.label} illustrative workflow comparison`}>
      <article>
        <span>Without adoption</span>
        <strong>{definition.manual.minutes} min</strong>
        <small>{definition.manual.touches} manual touches · {definition.manual.quality}/4 quality checks</small>
      </article>
      <i aria-hidden="true">→</i>
      <article className={complete ? "isRevealed" : undefined}>
        <span>With controlled adoption</span>
        <strong>{complete ? `${definition.adopted.minutes} min` : "Run the demo"}</strong>
        <small>{complete ? `${definition.adopted.touches} manual touches · ${definition.adopted.quality}/4 quality checks` : "Complete the hands-on task to reveal the comparison."}</small>
      </article>
      <article className="experienceResult">
        <span>Illustrative demo result</span>
        <strong>{complete ? `${minutesReleased} min released` : "Pending"}</strong>
        <small>Scenario output—not a forecast, benchmark or promised saving.</small>
      </article>
    </div>
  );
}

export function ExperienceWorkspace() {
  const [active, setActive] = useState<MethodKey>("integrate");
  const [completed, setCompleted] = useState<Record<MethodKey, boolean>>({ use: false, integrate: false, automate: false, configure: false });
  const [assistantStage, setAssistantStage] = useState(0);
  const [transactionDecisions, setTransactionDecisions] = useState<Record<string, TransactionDecision>>({});
  const [normalRun, setNormalRun] = useState(false);
  const [draftApproved, setDraftApproved] = useState(false);
  const [failureTested, setFailureTested] = useState(false);
  const [viewedQuestions, setViewedQuestions] = useState<string[]>([]);
  const [activeQuestion, setActiveQuestion] = useState("journal");

  const completedMethods = (Object.keys(completed) as MethodKey[]).filter((method) => completed[method]);
  const dashboard = useMemo(() => completedMethods.reduce((summary, method) => {
    const definition = methods[method];
    summary.manualMinutes += definition.manual.minutes;
    summary.adoptedMinutes += definition.adopted.minutes;
    summary.manualTouches += definition.manual.touches;
    summary.adoptedTouches += definition.adopted.touches;
    summary.quality += definition.adopted.quality;
    summary.control += definition.adopted.control;
    return summary;
  }, { manualMinutes: 0, adoptedMinutes: 0, manualTouches: 0, adoptedTouches: 0, quality: 0, control: 0 }), [completedMethods]);

  const reviewedTransactions = Object.keys(transactionDecisions).length;
  const alignedTransactions = transactions.filter((item) => transactionDecisions[item.id] === item.expected).length;
  const selectedQuestion = knowledgeQuestions.find((item) => item.id === activeQuestion) ?? knowledgeQuestions[0];

  function completeMethod(method: MethodKey) {
    setCompleted((current) => ({ ...current, [method]: true }));
  }

  function decideTransaction(id: string, decision: TransactionDecision) {
    const next = { ...transactionDecisions, [id]: decision };
    setTransactionDecisions(next);
    if (Object.keys(next).length === transactions.length) completeMethod("integrate");
  }

  function viewQuestion(id: string) {
    setActiveQuestion(id);
    const next = viewedQuestions.includes(id) ? viewedQuestions : [...viewedQuestions, id];
    setViewedQuestions(next);
    if (next.length === knowledgeQuestions.length) completeMethod("configure");
  }

  function resetExperience() {
    setActive("integrate");
    setCompleted({ use: false, integrate: false, automate: false, configure: false });
    setAssistantStage(0);
    setTransactionDecisions({});
    setNormalRun(false);
    setDraftApproved(false);
    setFailureTested(false);
    setViewedQuestions([]);
    setActiveQuestion("journal");
  }

  return (
    <section className="experienceLab" id="experience-lab" aria-labelledby="experience-title">
      <div className="experienceIntro">
        <div>
          <p className="kicker">Accounting AI Experience Lab</p>
          <h2 id="experience-title">Test-drive AI-enabled accounting workflows</h2>
          <p>Experience the same fictional work before and after controlled AI adoption. This is a product demonstration, not a lesson in prompting or a promise of business performance.</p>
        </div>
        <aside><strong>Synthetic work only</strong><span>No upload, model call or client data. Every result is generated inside this browser from a fixed demonstration scenario.</span></aside>
      </div>

      <nav className="experienceMethodNav" aria-label="AI adoption method demonstrations">
        {(Object.keys(methods) as MethodKey[]).map((method) => (
          <button aria-pressed={active === method} key={method} onClick={() => setActive(method)} type="button">
            <span>{methods[method].label}</span>
            <strong>{methods[method].workspace}</strong>
            <small>{completed[method] ? "Test drive complete" : methods[method].promise}</small>
          </button>
        ))}
      </nav>

      <div className="experienceStage">
        {active === "use" ? (
          <div className="experienceDemo">
            <header><div><span>Demo 01 · Use</span><h3>Controlled assistant studio</h3><p>Turn approved source facts into a review-ready explanation of a month-end movement.</p></div><b>{assistantStage === 2 ? "Approved" : `Stage ${assistantStage + 1} of 3`}</b></header>
            <div className="assistantStudio">
              <article className="demoInbox"><span>Synthetic task</span><h4>Explain the rise in operating expenses</h4><p>“Can you explain why this month&apos;s operating expenses are higher before tomorrow&apos;s review?”</p><ul><li>Rent unchanged at £1,850</li><li>Annual software renewal: £1,200</li><li>Repair invoice: £760</li></ul></article>
              <article className="demoOutput" aria-live="polite"><span>AI-enabled workspace</span>{assistantStage === 0 ? <p>Select the approved source pack and activate controlled assistance.</p> : assistantStage === 1 ? <><h4>First controlled draft</h4><p>Operating expenses increased mainly because of the annual software renewal and a one-off repair. <mark>This proves costs will return to normal next month.</mark></p><small>Quality control: the highlighted claim is unsupported by the source pack.</small></> : <><h4>Reviewed output</h4><p>Operating expenses increased mainly because of a £1,200 annual software renewal and a £760 repair invoice. Rent was unchanged. The available information does not establish next month&apos;s cost level.</p><small>Sources attached · unsupported forecast removed · human approval recorded</small></>}</article>
            </div>
            <div className="demoActions"><button onClick={() => setAssistantStage(1)} type="button">Activate approved assistance</button><button disabled={assistantStage < 1} onClick={() => { setAssistantStage(2); completeMethod("use"); }} type="button">Review, correct and approve</button></div>
            <MethodComparison complete={completed.use} method="use" />
          </div>
        ) : null}

        {active === "integrate" ? (
          <div className="experienceDemo">
            <header><div><span>Demo 02 · Integrate</span><h3>Reconciliation and close sandbox</h3><p>Review AI suggestions inside a synthetic transaction queue. Accept routine items and intervene where judgement or an exception matters.</p></div><b>{reviewedTransactions}/{transactions.length} reviewed</b></header>
            <div className="integrationSummary"><article><span>Manual workflow</span><strong>Review every item in sequence</strong><p>No confidence signal or exception priority.</p></article><article><span>AI-enabled workflow</span><strong>Suggestions plus an exception queue</strong><p>Staff remain accountable for every accepted, overridden or escalated item.</p></article></div>
            <div className="demoTableWrap"><table className="demoTransactionTable"><thead><tr><th>Item</th><th>Amount</th><th>AI suggestion</th><th>Confidence</th><th>Reviewer decision</th></tr></thead><tbody>{transactions.map((item) => <tr key={item.id}><th scope="row"><span>{item.id}</span>{item.description}</th><td>{item.amount}</td><td>{item.suggestion}</td><td><b className={Number(item.confidence.replace("%", "")) < 75 ? "lowConfidence" : undefined}>{item.confidence}</b></td><td><div className="transactionActions">{(["accept", "override", "escalate"] as TransactionDecision[]).map((decision) => <button aria-pressed={transactionDecisions[item.id] === decision} key={decision} onClick={() => decideTransaction(item.id, decision)} type="button">{decision}</button>)}</div></td></tr>)}</tbody></table></div>
            <div className="demoFeedback" aria-live="polite"><strong>Known-case alignment: {alignedTransactions}/{reviewedTransactions || 0}</strong><span>{reviewedTransactions < transactions.length ? "Review all four items to reveal the workflow result." : alignedTransactions === transactions.length ? "All decisions align with the synthetic known-answer set." : "One or more decisions differ from the known-answer set—revise the review rule before a pilot."}</span></div>
            <MethodComparison complete={completed.integrate} method="integrate" />
          </div>
        ) : null}

        {active === "automate" ? (
          <div className="experienceDemo">
            <header><div><span>Demo 03 · Automate</span><h3>Controlled workflow desk</h3><p>Run a missing-evidence workflow, retain approval and then inject a wrong-client failure.</p></div><b>{failureTested ? "Failure tested" : draftApproved ? "Approval recorded" : normalRun ? "Awaiting approval" : "Ready"}</b></header>
            <div className="automationFlow" aria-live="polite">
              <article className={normalRun ? "isActive" : undefined}><span>01</span><strong>Evidence gap detected</strong><small>Bank statement missing</small></article><i>→</i>
              <article className={normalRun ? "isActive" : undefined}><span>02</span><strong>Internal task created</strong><small>Assigned to practice administrator</small></article><i>→</i>
              <article className={normalRun ? "isActive" : undefined}><span>03</span><strong>Draft request prepared</strong><small>No external action yet</small></article><i>→</i>
              <article className={draftApproved ? "isActive" : undefined}><span>04</span><strong>Human approval</strong><small>{draftApproved ? "Recorded" : "Required"}</small></article>
            </div>
            {failureTested ? <div className="failureStop"><strong>Wrong-client test stopped safely</strong><span>Client identifier did not match the case context. The draft was blocked, the reviewer was alerted and no communication was sent.</span></div> : null}
            <div className="demoActions"><button onClick={() => setNormalRun(true)} type="button">Run normal case</button><button disabled={!normalRun} onClick={() => setDraftApproved(true)} type="button">Approve simulated draft</button><button disabled={!draftApproved} onClick={() => { setFailureTested(true); completeMethod("automate"); }} type="button">Inject wrong-client test</button></div>
            <MethodComparison complete={completed.automate} method="automate" />
          </div>
        ) : null}

        {active === "configure" ? (
          <div className="experienceDemo">
            <header><div><span>Demo 04 · Configure</span><h3>Firm knowledge assistant</h3><p>Ask operational questions against an approved synthetic procedure library and inspect the evidence route.</p></div><b>{viewedQuestions.length}/{knowledgeQuestions.length} tested</b></header>
            <div className="knowledgeWorkspace">
              <div className="knowledgeQuestions">{knowledgeQuestions.map((item) => <button aria-pressed={activeQuestion === item.id} key={item.id} onClick={() => viewQuestion(item.id)} type="button"><span>{viewedQuestions.includes(item.id) ? "Reviewed" : "Test question"}</span><strong>{item.question}</strong></button>)}</div>
              <article className="knowledgeAnswer" aria-live="polite"><span>{selectedQuestion.status}</span><h4>{selectedQuestion.answer}</h4><p><b>Citation:</b> {selectedQuestion.citation}</p><small>Approved corpus only · document-level trace · access and no-answer rules applied</small></article>
            </div>
            <MethodComparison complete={completed.configure} method="configure" />
          </div>
        ) : null}
      </div>

      <section className="experienceControlRoom" aria-labelledby="control-room-title">
        <div><p className="kicker light">Shared control room</p><h3 id="control-room-title">What changed across the test drives?</h3><p>The dashboard adds only completed synthetic scenarios. It shows the operational mechanism—not expected performance for a real practice.</p></div>
        <div className="controlRoomMetrics">
          <article><span>Methods experienced</span><strong>{completedMethods.length}/4</strong><small>{completedMethods.length ? completedMethods.map((method) => methods[method].label).join(" · ") : "Complete a workspace to begin."}</small></article>
          <article><span>Illustrative scenario time</span><strong>{completedMethods.length ? `${dashboard.manualMinutes} → ${dashboard.adoptedMinutes} min` : "—"}</strong><small>{completedMethods.length ? `${dashboard.manualMinutes - dashboard.adoptedMinutes} scenario minutes released` : "Manual versus adopted"}</small></article>
          <article><span>Manual touches</span><strong>{completedMethods.length ? `${dashboard.manualTouches} → ${dashboard.adoptedTouches}` : "—"}</strong><small>Routine handling redirected toward review and exceptions</small></article>
          <article><span>Quality-control coverage</span><strong>{completedMethods.length ? `${dashboard.quality}/${completedMethods.length * 4}` : "—"}</strong><small>Scenario checks completed in the adopted workflow</small></article>
          <article><span>Control coverage</span><strong>{completedMethods.length ? `${dashboard.control}/${completedMethods.length * 4}` : "—"}</strong><small>Approval, citation, logging and safe-stop mechanisms</small></article>
        </div>
        <div className="controlRoomActions"><button onClick={resetExperience} type="button">Reset all test drives</button><a href="#adoption-planner">Plan how your firm would test it</a></div>
        <p className="experienceBoundary"><strong>Evidence boundary:</strong> these are deterministic fictional demonstrations. They do not estimate sector ROI, guarantee time savings or reproduce the performance of a specific AI product.</p>
      </section>
    </section>
  );
}
