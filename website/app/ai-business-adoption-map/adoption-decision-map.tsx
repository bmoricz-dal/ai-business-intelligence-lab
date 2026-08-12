"use client";

import type { KeyboardEvent, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./adoption-decision-map.module.css";

type FunctionId = "marketing" | "service" | "operations" | "knowledge" | "reporting";
type Outcome = "time" | "quality" | "speed" | "knowledge" | "decision";

type Route = {
  id: string;
  number: string;
  function: FunctionId;
  functionLabel: string;
  title: string;
  problem: string;
  process: string;
  task: string;
  outcome: Outcome;
  outcomeLabel: string;
  capability: string;
  pattern: string;
  delivery: string;
  complexity: "Low" | "Medium" | "High";
  why: string;
  tools: string;
  data: string;
  people: string;
  risks: string[];
  controls: string[];
  measure: string;
  manage: string;
  source: string;
  evidence: "Documented guidance" | "Vendor example" | "Inference";
};

const routes: Route[] = [
  { id: "r01", number: "01", function: "marketing", functionLabel: "Marketing & sales", title: "Brief to campaign-ready draft", problem: "Small teams lose time turning a rough idea, product facts and brand guidance into a usable campaign brief or first draft.", process: "Marketing planning → briefing → copy draft → review", task: "Draft and adapt text for a defined audience and channel.", outcome: "time", outcomeLabel: "Save time on repeat work", capability: "Drafting and summarisation", pattern: "Human-in-the-loop content assistant", delivery: "Buy or configure", complexity: "Low", why: "Good fit when the task is bounded, source material is supplied and a named reviewer owns the final claim and tone. Not a substitute for positioning, fact checking or consent decisions.", tools: "Writing assistant in an approved work suite; CMS or campaign platform assistant; prompt template with brand and evidence fields. Illustrative examples: Microsoft 365 Copilot, Google Workspace Gemini, Adobe Express.", data: "Approved product facts, brand rules, audience notes, claims library and channel constraints. Keep customer or special-category data out unless the lawful basis and controls are clear.", people: "Marketing owner; subject-matter reviewer; light information-governance check.", risks: ["Fabricated claims or inappropriate tone", "Copyright or confidential source material leakage", "Inconsistent review across channels"], controls: ["Use a source pack and required-claims checklist", "Mark output as draft; require named human approval", "Log prompt/template version and final editor"], measure: "Baseline cycle time and rework rate; track time-to-first-draft, factual correction rate, approval turnaround and campaign performance separately.", manage: "Monthly sample review; refresh the source pack and prompt when products, policy or brand guidance changes; pause if correction rate rises.", source: "Inference informed by ICO data protection principles and NIST govern/map/measure/manage.", evidence: "Inference" },
  { id: "r02", number: "02", function: "marketing", functionLabel: "Marketing & sales", title: "Lead intake to qualified next step", problem: "Enquiries arrive through forms, email and social channels, and the team spends time reading, classifying and routing them.", process: "Lead capture → qualification → CRM update → follow-up", task: "Extract signals, classify intent and propose a next action.", outcome: "speed", outcomeLabel: "Respond or route faster", capability: "Classification and routing", pattern: "Rules + AI classification + human exception queue", delivery: "Configure or integrate", complexity: "Medium", why: "Appropriate when categories are stable, examples exist and false positives can be safely held for review. Avoid automatic rejection or pricing decisions until accuracy and fairness are demonstrated.", tools: "CRM-native lead scoring or classification; form-to-CRM workflow; email triage; integration platform. Illustrative examples: HubSpot AI, Salesforce Einstein, Zapier AI.", data: "Lead form fields, source channel, approved qualification rubric, CRM IDs and outcome labels. Define retention and access for personal data.", people: "Sales or marketing owner; CRM administrator; reviewer for exceptions.", risks: ["Biased or brittle qualification criteria", "Wrong routing or duplicate CRM records", "Unclear consent or profiling expectations"], controls: ["Start with assistive recommendations, not auto-rejection", "Audit categories by channel and segment", "Keep an exception queue and reversible CRM actions"], measure: "Time from enquiry to owner, routing accuracy, duplicate rate, qualified-to-opportunity conversion and manual override rate.", manage: "Weekly exception review during pilot, then monthly; reconfigure categories when products, channels or lead mix changes.", source: "Inference; data-protection and fairness controls should be assessed with ICO guidance.", evidence: "Inference" },
  { id: "r03", number: "03", function: "marketing", functionLabel: "Marketing & sales", title: "Calls and meetings to usable sales notes", problem: "Important context from sales calls is captured inconsistently, making follow-up and handover slower.", process: "Call or meeting → transcription → summary → CRM follow-up", task: "Transcribe, summarise decisions and extract actions.", outcome: "time", outcomeLabel: "Save time on repeat work", capability: "Speech and transcription", pattern: "Transcription + structured summary + reviewer sign-off", delivery: "Buy or configure", complexity: "Low", why: "Good fit for repeatable internal notes where attendees understand the recording and a human checks names, numbers and commitments. It is not a reliable substitute for a signed contract or formal record.", tools: "Meeting transcription, call-recording or CRM assistant; structured note template. Illustrative examples: Microsoft Teams, Zoom AI Companion, Otter.ai.", data: "Recording consent/notice, participant names, meeting metadata and CRM fields. Define storage, deletion and access rules before enabling recording.", people: "Call owner; sales operations owner; privacy/contact point as needed.", risks: ["Missing or misheard commitments", "Recording without appropriate notice", "Sensitive information copied into the wrong system"], controls: ["Provide notice and an opt-out/alternative where needed", "Require human review before CRM write-back", "Restrict retention and permissions"], measure: "Note completion rate, time to follow-up, correction rate and action completion - not transcript word count.", manage: "Sample notes monthly; review vendor changes and storage settings; update templates when sales process changes.", source: "Inference informed by ICO transparency, security and data minimisation guidance.", evidence: "Inference" },
  { id: "r04", number: "04", function: "service", functionLabel: "Customer service", title: "Support inbox to triage queue", problem: "A small service team cannot read every inbound message quickly enough to identify urgency, topic and owner.", process: "Inbound message → classify → route → respond", task: "Classify intent, urgency and required team; detect duplicates or missing information.", outcome: "speed", outcomeLabel: "Respond or route faster", capability: "Classification and routing", pattern: "AI triage with deterministic routing rules", delivery: "Configure or integrate", complexity: "Medium", why: "A strong early use case when the customer request is text-based and routing mistakes are recoverable. Keep refunds, complaints, vulnerable-customer signals and legal issues in a controlled human queue.", tools: "Helpdesk triage, shared inbox automation, CRM workflow or integration platform. Illustrative examples: Zendesk AI, Intercom, Zapier AI.", data: "Historical tickets, taxonomy, service-level rules, escalation contacts and approved macros. Remove unnecessary personal data from training examples.", people: "Customer-service owner; taxonomy maintainer; escalation owner.", risks: ["Urgent or vulnerable cases hidden in the wrong queue", "Overconfident automated replies", "Taxonomy drift as products and policies change"], controls: ["High-risk categories always escalate", "Separate triage from answer generation", "Monitor false-negative rate and provide manual override"], measure: "Time to first human review, routing accuracy by category, backlog age, escalation capture and customer recontact rate.", manage: "Review an exception sample weekly; change categories through a logged owner-approved process; test after vendor or policy changes.", source: "CMA consumer-law guidance is relevant where AI agents interact with customers or process refunds.", evidence: "Documented guidance" },
  { id: "r05", number: "05", function: "service", functionLabel: "Customer service", title: "Knowledge base to grounded answer draft", problem: "Agents search across policy pages, product notes and previous answers before replying, and may rely on outdated material.", process: "Customer question → retrieve approved source → draft answer → human send", task: "Find relevant passages and draft a response tied to those passages.", outcome: "knowledge", outcomeLabel: "Find and reuse knowledge", capability: "Internal knowledge search", pattern: "Retrieval-grounded assistant with citations", delivery: "Configure or integrate", complexity: "Medium", why: "Appropriate when the source set is authoritative, versioned and maintained. It is not appropriate to hide uncertainty or answer outside the approved source boundary.", tools: "Help-centre assistant, enterprise search, knowledge-base copilot or retrieval layer. Illustrative examples: Microsoft 365 Copilot, Intercom Fin, Zendesk AI.", data: "Approved, versioned knowledge sources, ownership metadata, effective dates, access controls and escalation rules.", people: "Knowledge owner; support lead; subject-matter approvers; technical integrator if sources span systems.", risks: ["Outdated or conflicting source material", "Answer sounds cited but is not supported", "Access-control leakage between teams or customers"], controls: ["Show source links and effective dates", "Return not found / escalate when support is absent", "Test permissions and remove stale documents"], measure: "Answer acceptance rate, source-supported rate, time to answer, escalation quality and outdated-source incidents.", manage: "Content owner reviews stale-source queue; monthly retrieval evaluation; re-test after index, model or policy changes.", source: "Design inference aligned with ICO accuracy/transparency and NIST measure/manage.", evidence: "Inference" },
  { id: "r06", number: "06", function: "service", functionLabel: "Customer service", title: "Support message to response draft", problem: "Agents write similar responses repeatedly, but customer context and policy exceptions still need human judgement.", process: "Ticket → context gather → draft → review → send", task: "Draft a response using approved policy and customer context.", outcome: "time", outcomeLabel: "Save time on repeat work", capability: "Drafting and summarisation", pattern: "Agent-assist draft, never send-by-default", delivery: "Buy or configure", complexity: "Low", why: "Useful when the response can be checked quickly and the system is explicitly bounded by policy. Keep a human accountable for complaints, compensation, safety, accessibility and exceptions.", tools: "Helpdesk writing assistant, email assistant or response-macro generator. Illustrative examples: Zendesk AI, Intercom, Microsoft 365 Copilot.", data: "Current policy text, ticket history, customer preferences where appropriate and approved tone guidance.", people: "Support agent; team lead for quality sampling; policy owner.", risks: ["Incorrect promises or policy interpretation", "Personal data appearing in drafts or logs", "Tone causing avoidable customer harm"], controls: ["Limit sources; no unsupported policy improvisation", "Human send action and edit trail", "Quality sample with high-risk category checks"], measure: "Time to draft, edit distance, first-contact resolution, reopen rate, complaint rate and customer feedback.", manage: "Weekly quality sample initially; update macros and policy sources; track changes in vendor model behaviour.", source: "Inference; apply ICO guidance where personal data are processed.", evidence: "Inference" },
  { id: "r07", number: "07", function: "operations", functionLabel: "Administration & operations", title: "Invoices and receipts to structured records", problem: "Staff re-key supplier documents into accounting or operations systems, creating delays and avoidable errors.", process: "Document received → extract fields → validate → approve → post", task: "Extract supplier, date, amount, tax and reference fields from documents.", outcome: "quality", outcomeLabel: "Reduce errors or inconsistency", capability: "Document extraction", pattern: "OCR/document understanding + deterministic validation + approval", delivery: "Buy or integrate", complexity: "Medium", why: "Often appropriate because the input and output are structured. Accuracy must be tested across layouts, suppliers and handwritten or poor-quality documents; automatic posting should be gated by rules and approval.", tools: "Accounting capture, expense management, document AI or workflow platform. Illustrative examples: Dext, Microsoft AI Builder, UiPath Document Understanding.", data: "Representative documents, supplier master, chart of accounts, tax rules and approval thresholds. Treat bank, employee and supplier data as sensitive.", people: "Finance or operations owner; approver; system administrator.", risks: ["Wrong amount or tax code", "Fraudulent or altered documents", "Sensitive financial data exposed to an external processor"], controls: ["Field confidence thresholds and validation rules", "Dual approval for exceptions/high values", "Vendor due diligence, access control and audit logs"], measure: "Extraction accuracy by field, exception rate, posting cycle time, duplicate rate and manual correction time.", manage: "Monthly supplier/layout drift review; retain samples and errors for regression testing; review vendor/model updates before promotion.", source: "Inference; ICO security and data-minimisation guidance is relevant when personal data appear in documents.", evidence: "Inference" },
  { id: "r08", number: "08", function: "operations", functionLabel: "Administration & operations", title: "Admin inbox to workflow queue", problem: "A shared admin inbox contains requests that need different owners, deadlines and evidence, and nothing gives a consistent view of progress.", process: "Request arrives → classify → assign → track → close", task: "Extract request type, urgency, owner and missing fields.", outcome: "speed", outcomeLabel: "Respond or route faster", capability: "Workflow automation", pattern: "Structured intake + rules + AI extraction for unstructured text", delivery: "Configure or integrate", complexity: "Medium", why: "Use AI to handle messy language at the edge of a well-defined workflow. Do not automate a workflow whose service levels, authority or exception path are not clear.", tools: "Forms/inbox-to-ticket workflow, low-code automation, task system or CRM. Illustrative examples: Microsoft Power Automate, Make, Zapier AI.", data: "Request taxonomy, service levels, owner directory, required fields and system IDs.", people: "Process owner; operations coordinator; system administrator; staff who handle exceptions.", risks: ["Requests routed to a person without authority", "Missed deadlines due to poor extraction", "Automation creates silent failures"], controls: ["Write every request to a visible queue", "Deterministic SLA timers and failure alerts", "Manual fallback and weekly unresolved-item review"], measure: "Time to assignment, queue completeness, SLA breach rate, misroute rate and unhandled-failure count.", manage: "Weekly queue health check; quarterly process review; re-authorise connections and permissions after team changes.", source: "Inference informed by NCSC secure operation and maintenance guidance.", evidence: "Inference" },
  { id: "r09", number: "09", function: "knowledge", functionLabel: "Research & knowledge", title: "Long documents to decision brief", problem: "Owners and consultants spend too long turning reports, policies or research packs into a short, traceable briefing.", process: "Documents → extract → summarise → compare → review", task: "Summarise, compare and surface open questions with page references.", outcome: "knowledge", outcomeLabel: "Find and reuse knowledge", capability: "Drafting and summarisation", pattern: "Source-bounded summariser with evidence links", delivery: "Buy or configure", complexity: "Low", why: "Good fit for first-pass compression when the user can inspect the source. Never treat a summary as a substitute for checking a material legal, financial, technical or safety conclusion.", tools: "Document assistant, PDF/knowledge workspace or research notebook. Illustrative examples: Microsoft 365 Copilot, Adobe Acrobat AI Assistant, NotebookLM.", data: "Authoritative documents, version/date, page or section anchors and access permissions.", people: "Research or knowledge owner; subject-matter reviewer; document custodian.", risks: ["Omission of caveats or uncertainty", "Confusion between sources or versions", "Confidential documents sent to an unapproved service"], controls: ["Require source citations and version metadata", "Use a fixed briefing schema with unknown/open question fields", "Restrict document upload and retention"], measure: "Briefing time, citation coverage, reviewer correction rate and decision-maker usefulness feedback.", manage: "Review source/version hygiene monthly; sample summaries after model or prompt changes; retire obsolete document collections.", source: "Inference aligned with NIST map/measure and ICO accuracy/transparency.", evidence: "Inference" },
  { id: "r10", number: "10", function: "knowledge", functionLabel: "Research & knowledge", title: "Meetings to actions and searchable memory", problem: "Decisions disappear into notes, making follow-up and institutional memory dependent on individual habits.", process: "Meeting → transcription → actions → searchable record", task: "Capture decisions, owners, dates and unresolved questions.", outcome: "quality", outcomeLabel: "Reduce errors or inconsistency", capability: "Speech and transcription", pattern: "Transcription + structured action extraction + owner confirmation", delivery: "Buy or configure", complexity: "Low", why: "Useful for internal coordination when participants know how notes are used. It is not sufficient as the sole record for regulated decisions, contractual commitments or sensitive conversations.", tools: "Meeting suite transcription, project workspace or knowledge-base assistant. Illustrative examples: Microsoft Teams, Zoom AI Companion, Notion AI.", data: "Meeting notice/consent, calendar context, approved workspace, action schema and retention rules.", people: "Meeting owner; action owners; knowledge administrator.", risks: ["Incorrect action owner/date", "Sensitive discussion shared too broadly", "Record becomes stale or untrusted"], controls: ["Owner confirms actions before they become tasks", "Permission groups and retention policy", "Mark transcript as draft; preserve meeting context"], measure: "Action capture rate, overdue action rate, follow-up time and correction rate.", manage: "Meeting owner reviews actions at close; monthly audit of stale pages; update templates when governance changes.", source: "Inference informed by ICO transparency and NCSC secure operation principles.", evidence: "Inference" },
  { id: "r11", number: "11", function: "reporting", functionLabel: "Reporting & analysis", title: "Operational data to narrative report", problem: "Teams spend time assembling recurring reports and explaining movements that are visible in the data but not yet interpreted.", process: "Data refresh → checks → analysis → narrative → review", task: "Describe changes, anomalies and questions using a defined metric set.", outcome: "decision", outcomeLabel: "Improve planning or decisions", capability: "Data analysis", pattern: "Semantic model + analytical assistant + reviewer narrative", delivery: "Configure or integrate", complexity: "Medium", why: "Appropriate when definitions, denominators and data quality checks are already stable. AI can help draft a narrative; it should not invent the metric, hide uncertainty or make an unreviewed business decision.", tools: "BI assistant, spreadsheet/SQL copilot or reporting workflow. Illustrative examples: Power BI Copilot, Tableau Agent, Excel Copilot.", data: "Versioned data model, metric definitions, periods, comparison rules, exception flags and a known refresh process.", people: "Data owner; analyst; business reviewer; BI administrator where needed.", risks: ["Wrong denominator or stale refresh", "Narrative overstates causality", "Access-control errors in reports"], controls: ["Show source/date/definition beside every metric", "Run validation checks before narrative generation", "Human approval of claims and anomalies"], measure: "Report production time, validation failure rate, correction rate, stakeholder decision usefulness and refresh timeliness.", manage: "Reconcile metrics each refresh; review semantic model changes; sample narratives and maintain a change log.", source: "Inference aligned with the project's traceability rules and NIST measure/manage.", evidence: "Inference" },
  { id: "r12", number: "12", function: "reporting", functionLabel: "Reporting & analysis", title: "Sales or stock history to planning signal", problem: "Small retailers and service teams need a better view of likely demand, capacity or stock pressure, but have limited time for analysis.", process: "Historical data → clean/validate → forecast or scenario → human plan", task: "Estimate likely ranges and identify drivers or exceptions.", outcome: "decision", outcomeLabel: "Improve planning or decisions", capability: "Forecasting and prediction", pattern: "Baseline forecast + scenario comparison + human planning decision", delivery: "Buy or configure first", complexity: "High", why: "Consider only when the business has enough clean, comparable historical data and can tolerate uncertainty. Prefer a simple baseline and range over a confident single number; do not use it to make high-impact decisions without review.", tools: "Demand-planning, spreadsheet/BI forecasting, retail analytics or custom model. Illustrative examples: Shopify analytics, Power BI forecasting, Google Vertex AI Forecasting.", data: "Time-stamped sales/stock/capacity history, promotions, closures, seasonality and known disruptions. Document gaps and structural breaks.", people: "Business owner; analyst; operations planner; technical support if integrating a model.", risks: ["False precision and overconfidence", "Seasonality or structural change makes history misleading", "Bad data drives purchasing or staffing errors"], controls: ["Compare against naive baseline", "Show range, assumptions and data gaps", "Keep planning authority with a named person; cap automation"], measure: "Forecast error against a chosen baseline, stockout/overstock or capacity miss rate, planning time and override reasons.", manage: "Review each planning cycle; monitor drift and error by segment; re-baseline after product, price, channel or operating-model changes.", source: "Inference; uncertainty and ongoing measurement are consistent with NIST measure/manage principles.", evidence: "Inference" },
];

const outcomes: { value: Outcome; label: string }[] = [
  { value: "time", label: "Save time on repeat work" },
  { value: "quality", label: "Reduce errors or inconsistency" },
  { value: "speed", label: "Respond or route faster" },
  { value: "knowledge", label: "Find and reuse knowledge" },
  { value: "decision", label: "Improve planning or decisions" },
];

const bulletList = (items: string[]) => <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>;
const firstSentence = (text: string) => text.match(/^.*?[.!?](?:\s|$)/)?.[0]?.trim() ?? text;
const firstClause = (text: string) => text.split(";")[0].trim();

export function AdoptionDecisionMap() {
  const [filter, setFilter] = useState<FunctionId | "all">("all");
  const [selectedFunction, setSelectedFunction] = useState<FunctionId | "">("");
  const [selectedOutcome, setSelectedOutcome] = useState<Outcome | "">("");
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);

  const visibleRoutes = useMemo(() => filter === "all" ? routes : routes.filter((route) => route.function === filter), [filter]);
  const matchedRoute = useMemo(() => {
    if (!selectedFunction || !selectedOutcome) return null;
    return routes.find((route) => route.function === selectedFunction && route.outcome === selectedOutcome) ?? routes.find((route) => route.function === selectedFunction) ?? null;
  }, [selectedFunction, selectedOutcome]);
  const alternativeRoutes = useMemo(() => {
    if (!matchedRoute) return [];
    return routes.filter((route) => route.function === matchedRoute.function && route.id !== matchedRoute.id).slice(0, 2);
  }, [matchedRoute]);
  const compareRoutes = useMemo(() => compareIds.map((id) => routes.find((route) => route.id === id)).filter((route): route is Route => Boolean(route)), [compareIds]);
  const workflowRoute = matchedRoute ?? selectedRoute ?? routes[3];
  const workflowSteps = workflowRoute.process.split("→").map((step) => step.trim());

  function toggleCompare(route: Route) {
    setCompareIds((current) => {
      if (current.includes(route.id)) return current.filter((id) => id !== route.id);
      return current.length < 3 ? [...current, route.id] : current;
    });
  }

  return (
    <>
      <section className={`pageSection adoptionDecisionMapSection ${styles.mapTheme}`} id="map">
        <DecisionHighwayScene />
        <div className="adoptionDecisionMapIntro"><div><p className="kicker">How the decision works</p><h2>A useful AI use case starts with a measurable business problem.</h2><p>Define the task and desired outcome first. Then test value, feasibility and risk before choosing a tool.</p></div><aside><strong>Rule of thumb</strong><p>Do not automate a process that has no clear owner, baseline or recovery path.</p></aside></div>
        <div className="adoptionDecisionSteps" aria-label="AI adoption decision sequence">
          {[['01','Problem','business type · function'],['02','Work','process · task · outcome'],['03','Fit','capability · solution pattern'],['04','Adopt','data · people · controls'],['05','Operate','measure · review · improve']].map(([number,title,detail]) => <div key={number}><span>{number}</span><strong>{title}</strong><small>{detail}</small></div>)}
        </div>
        <div className="adoptionDecisionGuide">
          <div>
            <p className="kicker light">Find a practical starting point</p>
            <h3>Choose where the work happens and what needs to improve.</h3>
            <p>We will show a route to investigate—not a recommendation to buy.</p>
          </div>
          <div className="adoptionDecisionGuideControls">
            <div className={styles.controlField}>
              <label htmlFor="business-function">Business function</label>
              <div className={styles.selectorShell} data-active={Boolean(selectedFunction) || undefined}>
                <span className={styles.selectorIcon} aria-hidden="true">F</span>
                <select id="business-function" value={selectedFunction} onChange={(event) => setSelectedFunction(event.target.value as FunctionId | "")}>
                  <option value="">Choose a function</option><option value="marketing">Marketing & sales</option><option value="service">Customer service</option><option value="operations">Administration & operations</option><option value="knowledge">Research & knowledge</option><option value="reporting">Reporting & analysis</option>
                </select>
                <i className={styles.selectorSignal} aria-hidden="true" />
              </div>
            </div>
            <div className={styles.controlField}>
              <label htmlFor="desired-outcome">Desired outcome</label>
              <div className={styles.selectorShell} data-active={Boolean(selectedOutcome) || undefined}>
                <span className={styles.selectorIcon} aria-hidden="true">O</span>
                <select id="desired-outcome" value={selectedOutcome} onChange={(event) => setSelectedOutcome(event.target.value as Outcome | "")}>
                  <option value="">Choose an outcome</option>{outcomes.map((outcome) => <option key={outcome.value} value={outcome.value}>{outcome.label}</option>)}
                </select>
                <i className={styles.selectorSignal} aria-hidden="true" />
              </div>
            </div>
            <div className={`adoptionDecisionGuideResult ${styles.guideResult}`} data-ready={Boolean(matchedRoute) || undefined} aria-live="polite">
              {matchedRoute ? (
                <>
                  <div className={styles.resultSummary}>
                    <small>Starting hypothesis</small>
                    <strong>{matchedRoute.title}</strong>
                    <p>{firstSentence(matchedRoute.why)}</p>
                    <dl className={styles.resultChecks}>
                      <div><dt>Pilot condition</dt><dd>{matchedRoute.controls[0]}</dd></div>
                      <div><dt>Baseline first</dt><dd>{firstClause(matchedRoute.measure)}</dd></div>
                      <div><dt>Status</dt><dd>Matched on function and outcome. Validate the workflow before choosing a product.</dd></div>
                    </dl>
                    {alternativeRoutes.length > 0 ? <div className={styles.alternatives}><span>Also consider</span>{alternativeRoutes.map((route) => <button key={route.id} type="button" onClick={() => setSelectedRoute(route)}>{route.title}</button>)}</div> : null}
                  </div>
                  <div className={styles.resultActions}>
                    <button type="button" className="primaryButton" onClick={() => setSelectedRoute(matchedRoute)}>Inspect route →</button>
                    <a className={styles.workflowLink} href="#workflow">See the workflow ↓</a>
                  </div>
                </>
              ) : <div><small>Your starting point</small><strong>Select a function and an outcome to see a route.</strong></div>}
            </div>
          </div>
        </div>
      </section>

      <section className={`pageSection ${styles.workflowSection}`} id="workflow" aria-labelledby="workflow-title">
        <PlanetScene />
        <div className={styles.workflowHeader}>
          <div>
            <p className="kicker light">Workflow visualisation</p>
            <h2 id="workflow-title">Watch the work change before you choose a tool.</h2>
            <p>Every route keeps a human checkpoint visible. The moving signal is a prompt to test the hand-off—not a promise of automation.</p>
          </div>
          <div className={styles.workflowBadge}><span>{matchedRoute ? "MATCHED ROUTE" : "FEATURED ROUTE"}</span><strong>{workflowRoute.title}</strong><small>{workflowRoute.functionLabel} · {workflowRoute.complexity} complexity</small></div>
        </div>
        <div className={styles.workflowCanvas} aria-label={`Workflow visualisation for ${workflowRoute.title}`}>
          <div className={styles.workflowRail} aria-hidden="true"><span className={styles.workflowPulse} /></div>
          <ol className={styles.workflowNodes}>
            {workflowSteps.map((step, index) => <li key={`${workflowRoute.id}-${step}`}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong><small>{index === 0 ? "Current input" : index === workflowSteps.length - 1 ? "Measured output" : "Workflow hand-off"}</small></li>)}
          </ol>
        </div>
        <div className={styles.workflowReadouts}>
          <article><span>AI role</span><strong>{workflowRoute.task}</strong></article>
          <article><span>Human checkpoint</span><strong>{workflowRoute.controls[0]}</strong></article>
          <article><span>Measure first</span><strong>{firstClause(workflowRoute.measure)}</strong></article>
        </div>
      </section>

      <section className={`pageSection adoptionRouteSection ${styles.routeTheme}`} id="routes"><LibraryScene /><div className="sectionLead"><p className="kicker light">MVP route library</p><h2>12 common SME workflows.</h2><p>Each route shows the business problem, potential role for AI, conditions for a pilot, human controls and measures of success. Select up to three routes to compare their trade-offs.</p></div><div className="adoptionRouteFilters" aria-label="Filter route cards">{([['all','All routes'],['marketing','Marketing & sales'],['service','Customer service'],['operations','Administration & operations'],['knowledge','Research & knowledge'],['reporting','Reporting & analysis']] as const).map(([value,label]) => <button key={value} type="button" aria-pressed={filter === value} onClick={() => setFilter(value)}>{label}</button>)}<span>{visibleRoutes.length} routes shown</span></div><div className="adoptionRouteGrid">{visibleRoutes.map((route) => <article className="adoptionRouteCard" data-matched={matchedRoute?.id === route.id || undefined} data-compared={compareIds.includes(route.id) || undefined} key={route.id}><div className="adoptionRouteCardTop"><span>{route.number}</span><b className={`complexity ${route.complexity.toLowerCase()}`}>{route.complexity} complexity</b></div><h3>{route.title}</h3><p>{route.problem}</p><footer><small>{route.capability}</small><div className={styles.routeActions}><button type="button" onClick={() => setSelectedRoute(route)}>Open route →</button><button type="button" className={styles.compareButton} aria-pressed={compareIds.includes(route.id)} onClick={() => toggleCompare(route)}>{compareIds.includes(route.id) ? "Compared ✓" : "Compare"}</button></div></footer></article>)}</div></section>

      <section className={`pageSection ${styles.comparisonSection}`} id="compare" aria-labelledby="compare-title">
        <ComparisonScene />
        <div className={styles.comparisonHeader}>
          <div><p className="kicker light">Comparison mode</p><h2 id="compare-title">Make the trade-offs visible.</h2><p>Compare candidate routes on value, control burden and the first measure to collect. This is a prioritisation aid—not a universal score.</p></div>
          <div className={styles.comparisonCounter}><strong>{compareRoutes.length}<span>/3</span></strong><small>routes selected</small>{compareRoutes.length > 0 ? <button type="button" onClick={() => setCompareIds([])}>Clear selection</button> : <span>Select Compare on any route card</span>}</div>
        </div>
        {compareRoutes.length === 0 ? <div className={styles.comparisonEmpty}><span>01</span><div><strong>Choose routes to compare</strong><p>Start with two routes that address the same outcome or sit in the same function. Their differences will appear here.</p></div></div> : <div className={styles.comparisonTable} style={{ gridTemplateColumns: `minmax(175px, .62fr) repeat(${compareRoutes.length}, minmax(0, 1fr))` }} role="region" aria-label="Selected route comparison"><div className={styles.comparisonMetric}><span>Decision lens</span><small>What to inspect</small></div>{compareRoutes.map((route) => <article key={route.id} className={styles.comparisonRoute}><span>{route.number} · {route.complexity}</span><h3>{route.title}</h3><small>{route.functionLabel}</small></article>)}<div className={styles.comparisonMetric}><span>Potential outcome</span><small>What could improve</small></div>{compareRoutes.map((route) => <div key={`${route.id}-outcome`} className={styles.comparisonCell}><strong>{route.outcomeLabel}</strong><p>{firstSentence(route.why)}</p></div>)}<div className={styles.comparisonMetric}><span>Control burden</span><small>What must remain human</small></div>{compareRoutes.map((route) => <div key={`${route.id}-control`} className={styles.comparisonCell}><strong>{route.controls[0]}</strong><p>{route.risks[0]}</p></div>)}<div className={styles.comparisonMetric}><span>Measure first</span><small>Baseline before pilot</small></div>{compareRoutes.map((route) => <div key={`${route.id}-measure`} className={styles.comparisonCell}><strong>{firstClause(route.measure)}</strong><p>{route.manage}</p></div>)}</div>}
      </section>

      <section className={`pageSection adoptionEvidenceSection ${styles.evidenceTheme}`} id="evidence"><EvidenceScene /><div className="sectionLead"><p className="kicker light">Evidence discipline</p><h2>Know what supports each part of the decision.</h2><p>Route fit, control guidance and product capability are different claims. The map labels them separately; none guarantees savings, compliance or suitability.</p></div><div className="adoptionEvidenceCards"><article><span>Route fit</span><strong>Treat as a hypothesis.</strong><p>Test the workflow logic against a named owner, current baseline and representative examples.</p></article><article><span>Control basis</span><strong>Use as a guardrail.</strong><p>Regulator, standards-body or public-sector guidance supports the risk and governance patterns.</p></article><article><span>Product example</span><strong>Verify before buying.</strong><p>Vendor pages describe current capabilities; they do not prove your workflow, data or business case.</p></article></div><div className="adoptionSourceRegister"><h3>Primary source register</h3><div className="adoptionSourceGrid"><Source id="01" title="ICO - Guidance on AI and data protection" detail="Privacy, transparency, accuracy, fairness, security and accountability." href="https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/" /><Source id="02" title="NCSC - Guidelines for secure AI system development" detail="Secure design, development, deployment, operation and maintenance." href="https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/guidelines" /><Source id="03" title="NIST - AI Risk Management Framework 1.0" detail="Govern, map, measure and manage across the AI lifecycle." href="https://www.nist.gov/itl/ai-risk-management-framework" /><Source id="04" title="GOV.UK / DSIT - UK AI regulatory principles" detail="Safety, transparency, fairness, accountability, contestability and redress." href="https://www.gov.uk/government/publications/implementing-the-uks-ai-regulatory-principles-initial-guidance-for-regulators/implementing-the-uks-ai-regulatory-principles-initial-guidance-for-regulators" /><Source id="05" title="CMA - Using AI agents: complying with consumer law" detail="Consumer-law responsibility where AI interacts with customers or processes refunds." href="https://www.gov.uk/government/publications/complying-with-consumer-law-when-using-ai-agents" /><Source id="06" title="Microsoft 365 Copilot product information" detail="One illustrative, time-sensitive product source—not evidence of business value or suitability." href="https://www.microsoft.com/en-us/microsoft-365-copilot/business" /></div></div></section>

      <section className={`pageSection adoptionMethodSection ${styles.methodTheme}`} id="method"><MethodScene /><div className="sectionLead"><p className="kicker light">How to use it</p><h2>Turn the route into a controlled pilot.</h2><p>Proceed only when the owner can explain the current baseline, the AI system boundary and the recovery path when it is wrong.</p></div><div className="adoptionMethodGrid"><article><span>01 · Before</span><h3>Map the current work.</h3><p>Name the process owner, inputs, outputs, exceptions, decision rights and baseline. If the work cannot be described, pause the AI decision.</p></article><article><span>02 · Pilot</span><h3>Run a bounded pilot.</h3><p>Use representative examples, human review and a rollback path. Compare with the current process, not a hoped-for future.</p></article><article><span>03 · Operate</span><h3>Monitor and improve.</h3><p>Review quality, cost, latency, incidents, user feedback, data access and vendor changes. Retire or rework the system when its control burden exceeds its value.</p></article></div></section>
      {selectedRoute && <RouteDialog route={selectedRoute} onClose={() => setSelectedRoute(null)} />}
    </>
  );
}

function DecisionHighwayScene() {
  return <div className={styles.highwayScene} aria-hidden="true"><span className={styles.highwayPhoto} /><span className={styles.highwayHorizon} /><span className={styles.highwayRoad} /><span className={styles.highwayLaneA} /><span className={styles.highwayLaneB} /><span className={styles.highwayCity} /><i /><i /><i /><i /><i /><i /></div>;
}

function PlanetScene() {
  return <div className={styles.planetScene} aria-hidden="true"><span className={styles.planetPhoto} /><span className={styles.planet}><i /><i /><i /></span><span className={styles.planetRing} /><span className={`${styles.planetRing} ${styles.planetRingTwo}`} /><span className={styles.planetMoon} /><span className={styles.planetScan} /></div>;
}

function LibraryScene() {
  return <div className={styles.libraryScene} aria-hidden="true"><span className={styles.libraryPhoto} /><span className={styles.libraryAisle} /><span className={`${styles.libraryShelf} ${styles.shelfOne}`} /><span className={`${styles.libraryShelf} ${styles.shelfTwo}`} /><span className={`${styles.libraryShelf} ${styles.shelfThree}`} /><span className={styles.libraryLight} /><i /><i /><i /><i /><i /></div>;
}

function ComparisonScene() {
  return <div className={styles.comparisonScene} aria-hidden="true"><span /><span /><span /><span /><i /><i /><i /></div>;
}

function EvidenceScene() {
  return <div className={styles.evidenceScene} aria-hidden="true"><span className={styles.evidenceCore} /><span className={styles.evidenceOrbitA} /><span className={styles.evidenceOrbitB} /><i /><i /><i /><i /><i /></div>;
}

function MethodScene() {
  return <div className={styles.methodScene} aria-hidden="true"><span className={styles.methodHorizon} /><span className={styles.methodBeam} /><i /><i /><i /><i /></div>;
}

function Source({ id, title, detail, href }: { id: string; title: string; detail: string; href: string }) { return <a className="adoptionSource" href={href} target="_blank" rel="noreferrer"><span>{id}</span><div><strong>{title}</strong><p>{detail}</p><small>Open primary source ↗</small></div></a>; }

function RouteDialog({ route, onClose }: { route: Route; onClose: () => void }) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeButtonRef.current?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus();
    };
  }, []);

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLElement>("button, a[href], input, select, textarea, summary, [tabindex]:not([tabindex='-1'])") ?? []).filter((element) => !element.hasAttribute("disabled"));
    if (focusable.length === 0) {
      event.preventDefault();
      dialogRef.current?.focus();
      return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <div className="adoptionDialogBackdrop" role="presentation" onKeyDown={handleKeyDown} onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <div className="adoptionDialog" role="dialog" aria-modal="true" aria-labelledby="adoption-dialog-title" aria-describedby="adoption-dialog-summary" ref={dialogRef} tabIndex={-1}>
        <header><div><p className="kicker light">{route.number} · {route.functionLabel}</p><h2 id="adoption-dialog-title">{route.title}</h2></div><button type="button" aria-label="Close route details" onClick={onClose} ref={closeButtonRef}>×</button></header>
        <div className="adoptionDialogBody">
          <p className="adoptionDialogLead" id="adoption-dialog-summary">{route.why}</p>
          <div className={styles.dialogSummaryGrid} aria-label="Route decision summary">
            <article><span>Potential outcome</span><strong>{route.outcomeLabel}</strong><p>{route.pattern}</p></article>
            <article><span>Pilot only if</span><p>{route.controls[0]}</p></article>
            <article><span>Control boundary</span><p>{route.controls[1] ?? route.controls[0]}</p></article>
            <article><span>Baseline first</span><p>{firstClause(route.measure)}</p></article>
          </div>
          <div className={styles.detailSections}>
            <details open><summary>Work and intended outcome</summary><div className="adoptionDetailGrid"><Detail title="Business problem">{route.problem}</Detail><Detail title="Process and task">{route.process}<br /><br /><strong>Task:</strong> {route.task}</Detail><Detail title="Desired outcome">{route.outcomeLabel}</Detail><Detail title="Capability"><strong>{route.capability}</strong><br />{route.pattern}</Detail></div></details>
            <details><summary>Implementation requirements</summary><div className="adoptionDetailGrid"><Detail title="Buy / configure / integrate / build"><strong>{route.delivery}</strong><br />Start with the least complex option that meets the control and integration requirements.</Detail><Detail title="Implementation complexity"><strong>{route.complexity}</strong><br />A practical estimate for a bounded first pilot, not a vendor or project quote.</Detail><Detail title="Required data and systems" wide>{route.data}</Detail><Detail title="People and skills">{route.people}</Detail><Detail title="Tool categories and examples">{route.tools}</Detail></div></details>
            <details><summary>Risks, controls and accountability</summary><div className="adoptionDetailGrid"><Detail title="Risks">{bulletList(route.risks)}</Detail><Detail title="Controls and accountability">{bulletList(route.controls)}</Detail></div></details>
            <details><summary>Measures and ongoing management</summary><div className="adoptionDetailGrid"><Detail title="Success measures" wide>{route.measure}</Detail><Detail title="Post-implementation management" wide>{route.manage}</Detail></div></details>
          </div>
        </div>
        <footer className={styles.evidenceFooter}><div><strong>Route fit:</strong> Design inference to test against your workflow and baseline.</div><div><strong>Control basis:</strong> {route.evidence}. {route.source}</div></footer>
      </div>
    </div>
  );
}

function Detail({ title, children, wide = false }: { title: string; children: ReactNode; wide?: boolean }) { return <div className={`adoptionDetail ${wide ? "wide" : ""}`}><h3>{title}</h3><div>{children}</div></div>; }
