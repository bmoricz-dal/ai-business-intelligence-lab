"use client";

import Link from "next/link";
import { useState } from "react";

const programmeStages = [
  {
    id: "readiness",
    number: "01",
    label: "Readiness",
    title: "Establish the sector baseline",
    description: "Adoption, integration, governance, use cases and pathways remain distinct signals rather than one maturity score.",
    signal: "Current state",
    href: "/sectors/accounting",
    action: "Open readiness study",
  },
  {
    id: "benefits",
    number: "02",
    label: "Benefits",
    title: "Locate measurable workflow value",
    description: "Bookkeeping, transaction processing and close support show the clearest evidence when controls and professional review remain inside the system.",
    signal: "System fit",
    href: "/sectors/accounting/benefits",
    action: "Open benefits evidence",
  },
  {
    id: "journeys",
    number: "03",
    label: "Journeys",
    title: "Follow implementation into real work",
    description: "Published cases reveal selection, pilots, setbacks, adaptations and outcomes without blending unrelated firms into one story.",
    signal: "Real adoption",
    href: "/sectors/accounting/adoption-journeys",
    action: "Explore adoption journeys",
  },
  {
    id: "lab",
    number: "04",
    label: "Experience Lab",
    title: "Test-drive an AI-enabled accounting cycle",
    description: "Synthetic records move through bookkeeping, ledger, close, accounts, insight and quality control in a browser-only demonstration.",
    signal: "Practical demonstration",
    href: "/adoption-pathways/accounting-micro-case-study",
    action: "Enter the Experience Lab",
  },
];

const readinessDimensions = [
  ["01", "AI use", "Material, no longer niche", "Direct sources show meaningful use, but no official open source isolates a single UK accounting-SME prevalence rate."],
  ["02", "Integration", "Behind task-level access", "External tools and embedded features are visible; verified connection to recurring accounting systems is less consistently measured."],
  ["03", "Governance", "A separate capability", "Approved tools, permitted data, skills and human review cannot be inferred from access to AI."],
  ["04", "Use cases", "Information work leads", "Research, drafting, summarisation, document processing and selected reporting are the clearest entry points."],
  ["05", "Pathways", "Buy and embed dominate", "General tools, vendor features and task applications are more common than bespoke builds or autonomous decisions."],
];

const journeyCases = [
  {
    id: "bookkeeping",
    label: "Integrated bookkeeping",
    grade: "A / B",
    context: "Peer-reviewed US field evidence",
    stages: ["Workflow mapped", "AI integrated", "Reliance risk found", "Confidence + review", "Outcomes measured"],
    outcome: "+17.5 percentage points classification accuracy in the framed experiment",
    boundary: "Narrow experiment; operational adoption was endogenous and is not a UK SME benchmark.",
  },
  {
    id: "lya",
    label: "Love Your Accountants",
    grade: "E",
    context: "Named UK practitioner case",
    stages: ["Admin problem", "Tools reviewed", "Portal developed", "Use constrained", "Saving estimated"],
    outcome: "10–15 hours per week manager-estimated saving on scanned-mail administration",
    boundary: "Self-reported; no independent baseline or evaluation was published.",
  },
  {
    id: "audit",
    label: "Audit-firm pattern",
    grade: "B / C",
    context: "Transparent multi-source synthesis",
    stages: ["Readiness assessed", "Central rollout", "Training friction", "Controls expanded", "Long-run associations"],
    outcome: "Training, scale, explainability and accountability repeatedly shaped implementation",
    boundary: "Not one company journey; large-firm audit evidence cannot provide a UK micro-practice effect size.",
  },
];

export function ProgrammeConsole() {
  const [activeId, setActiveId] = useState(programmeStages[0].id);
  const active = programmeStages.find((stage) => stage.id === activeId) ?? programmeStages[0];

  return (
    <div className="programmeConsole">
      <div className="consoleTopline"><span>ACCOUNTING RESEARCH SYSTEM</span><b><i /> SIGNAL ONLINE</b></div>
      <div className="programmeConsoleGrid">
        <div className="programmeStageRail" role="tablist" aria-label="Accounting research programme">
          {programmeStages.map((stage) => (
            <button
              aria-controls="programme-console-panel"
              aria-selected={stage.id === active.id}
              className={stage.id === active.id ? "isActive" : undefined}
              key={stage.id}
              onClick={() => setActiveId(stage.id)}
              role="tab"
              type="button"
            >
              <span>{stage.number}</span><strong>{stage.label}</strong><i aria-hidden="true" />
            </button>
          ))}
        </div>
        <div className="programmeConsolePanel" id="programme-console-panel" role="tabpanel">
          <div className="consoleSignal"><span>{active.signal}</span><i /><i /><i /></div>
          <p>{active.number} / 04</p>
          <h3>{active.title}</h3>
          <p>{active.description}</p>
          <Link href={active.href}>{active.action} <span aria-hidden="true">↗</span></Link>
        </div>
      </div>
    </div>
  );
}

export function ReadinessConsole() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = readinessDimensions[activeIndex];

  return (
    <section className="readinessConsole" aria-labelledby="readiness-console-title">
      <div className="readinessConsoleHeader">
        <div><span>FIVE-DIMENSION VIEW</span><h2 id="readiness-console-title">Explore operational readiness without a composite score.</h2></div>
        <b><i /> SECONDARY EVIDENCE</b>
      </div>
      <div className="readinessConsoleBody">
        <div className="readinessDial" aria-hidden="true">
          <div><span>{active[0]}</span><strong>{active[1]}</strong></div>
          {readinessDimensions.map((item, index) => <i className={index === activeIndex ? "isActive" : undefined} key={item[0]} />)}
        </div>
        <div className="readinessControls" role="tablist" aria-label="Readiness dimensions">
          {readinessDimensions.map((item, index) => (
            <button aria-selected={index === activeIndex} className={index === activeIndex ? "isActive" : undefined} key={item[0]} onClick={() => setActiveIndex(index)} role="tab" type="button">
              <span>{item[0]}</span><strong>{item[1]}</strong>
            </button>
          ))}
        </div>
        <div className="readinessReadout" role="tabpanel">
          <span>Current signal</span><strong>{active[2]}</strong><p>{active[3]}</p>
        </div>
      </div>
    </section>
  );
}

export function JourneyExplorer() {
  const [activeId, setActiveId] = useState(journeyCases[0].id);
  const active = journeyCases.find((item) => item.id === activeId) ?? journeyCases[0];

  return (
    <section className="journeyExplorer" aria-labelledby="journey-explorer-title">
      <div className="journeyExplorerHeader">
        <div><span>INTERACTIVE CASE EXPLORER</span><h2 id="journey-explorer-title">Compare how adoption moved—and where evidence stops.</h2></div>
        <b>SELECT CASE / TRACE LIFECYCLE</b>
      </div>
      <div className="journeyExplorerTabs" role="tablist" aria-label="Adoption journey cases">
        {journeyCases.map((item) => (
          <button aria-selected={item.id === active.id} className={item.id === active.id ? "isActive" : undefined} key={item.id} onClick={() => setActiveId(item.id)} role="tab" type="button">
            <span>{item.grade}</span><strong>{item.label}</strong><small>{item.context}</small>
          </button>
        ))}
      </div>
      <div className="journeyExplorerPanel" role="tabpanel">
        <ol>
          {active.stages.map((stage, index) => <li key={stage}><span>{String(index + 1).padStart(2, "0")}</span><i aria-hidden="true" /><strong>{stage}</strong></li>)}
        </ol>
        <div><span>Outcome signal</span><strong>{active.outcome}</strong><p>{active.boundary}</p></div>
      </div>
    </section>
  );
}
