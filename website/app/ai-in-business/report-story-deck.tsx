"use client";

import { useState, type CSSProperties } from "react";

type EvidencePoint = {
  label: string;
  value: number;
  display: string;
  role?: "benchmark";
};

type ReportSlide = {
  number: string;
  theme: string;
  title: string;
  headline: string;
  summary: string;
  denominator: string;
  boundary: string;
  href: string;
  variant: string;
  points: EvidencePoint[];
};

const sizeLabels = ["Micro", "Small", "Medium", "Large"];

const reportSlides: ReportSlide[] = [
  {
    number: "01",
    theme: "AI use",
    title: "AI Use by Business Size",
    headline: "AI use rises with business size.",
    summary: "Reported use is already material among micro businesses, while each larger size group records a higher point estimate.",
    denominator: "All UK businesses in each published size group",
    boundary: "Descriptive estimates with supplied confidence intervals; the chart does not establish a causal size effect.",
    href: "/reports/SME_Report_01_AI_Use_by_Business_Size.pdf",
    variant: "reach",
    points: [
      { label: "Micro", value: 37.4, display: "37.4%" },
      { label: "Small", value: 50.8, display: "50.8%" },
      { label: "Medium", value: 57.1, display: "57.1%" },
      { label: "Large", value: 78.2, display: "78.2%", role: "benchmark" },
    ],
  },
  {
    number: "02",
    theme: "Integration",
    title: "AI Adoption and System Integration",
    headline: "Tool use does not mean system integration.",
    summary: "Among businesses already using AI, SME integration estimates cluster between 26.9% and 31.5%; the large-business benchmark is higher.",
    denominator: "UK businesses already reporting AI use",
    boundary: "These percentages cannot be treated as shares of all businesses or combined with Report 01 as a conversion funnel.",
    href: "/reports/SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf",
    variant: "integration",
    points: [
      { label: "Micro", value: 26.9, display: "26.9%" },
      { label: "Small", value: 31.5, display: "31.5%" },
      { label: "Medium", value: 30.9, display: "30.9%" },
      { label: "Large", value: 57.4, display: "57.4%", role: "benchmark" },
    ],
  },
  {
    number: "03",
    theme: "Governance",
    title: "AI Governance by Business Size",
    headline: "Guidance remains uneven—especially for micro AI users.",
    summary: "Formal or informal AI policy and guidance has a 20.1% point estimate among micro AI users and rises across the published size groups.",
    denominator: "UK businesses already reporting AI use",
    boundary: "Policy presence is not a quality score, and the published estimates alone do not establish formal pairwise significance.",
    href: "/reports/SME_Report_03_AI_Governance_by_Business_Size.pdf",
    variant: "governance",
    points: [
      { label: "Micro", value: 20.1, display: "20.1%" },
      { label: "Small", value: 29.0, display: "29.0%" },
      { label: "Medium", value: 36.8, display: "36.8%" },
      { label: "Large", value: 67.7, display: "67.7%", role: "benchmark" },
    ],
  },
  {
    number: "04",
    theme: "Use cases",
    title: "How UK Businesses Use AI",
    headline: "Research is the leading listed use case at every size.",
    summary: "Information discovery provides a consistent entry point, from 25.9% of micro businesses to 53.7% of the large-business benchmark.",
    denominator: "All UK businesses in each published size group",
    boundary: "The source question permits multiple responses. Use-case percentages overlap and must not be added into a whole.",
    href: "/reports/SME_Report_04_How_UK_Businesses_Use_AI.pdf",
    variant: "usecases",
    points: [
      { label: "Micro", value: 25.9, display: "25.9%" },
      { label: "Small", value: 36.0, display: "36.0%" },
      { label: "Medium", value: 38.5, display: "38.5%" },
      { label: "Large", value: 53.7, display: "53.7%", role: "benchmark" },
    ],
  },
];

const pathwaySeries = [
  { id: "integration", label: "System integration", denominator: "AI users", values: [26.9, 31.5, 30.9, 57.4] },
  { id: "decisions", label: "Automated decisions", denominator: "AI users", values: [5.3, 3.4, 4.9, 8.4] },
  { id: "guidance", label: "Policy or guidance", denominator: "AI users", values: [20.1, 29.0, 36.8, 67.7] },
  { id: "development", label: "In-house development", denominator: "All businesses", values: [3.3, 3.6, 6.5, 10.5] },
];

const synthesisNodes = [
  { label: "Reach", title: "Use", text: "AI use is visible across every size group, but access alone says little about operating depth." },
  { label: "Connection", title: "Integrate", text: "System integration is measured among AI users and remains a separate capability." },
  { label: "Control", title: "Govern", text: "Policy, guidance and accountable review do not follow automatically from tool access." },
  { label: "Work", title: "Apply", text: "Research and information work are leading entry points, with use cases overlapping." },
  { label: "Route", title: "Choose", text: "Integration, automation, guidance and in-house development describe different operating routes." },
  { label: "Outcome", title: "Measure", text: "The reports describe adoption patterns; business benefit requires a separate evaluation." },
];

function EvidenceBars({ points, active, onSelect }: { points: EvidencePoint[]; active: number; onSelect: (index: number) => void }) {
  const selected = points[active];
  return (
    <div className="reportEvidenceGraphic">
      <div className="reportBars" role="group" aria-label="Select a business size to inspect its estimate">
        {points.map((point, index) => (
          <button
            aria-pressed={active === index}
            className={point.role === "benchmark" ? "isBenchmark" : undefined}
            key={point.label}
            onClick={() => onSelect(index)}
            style={{ "--bar-value": `${point.value}%` } as CSSProperties}
            type="button"
          >
            <span className="reportBarTrack"><i /></span>
            <strong>{point.display}</strong>
            <small>{point.label}{point.role === "benchmark" ? " · benchmark" : ""}</small>
          </button>
        ))}
      </div>
      <div className="reportChartReadout" aria-live="polite">
        <span>Selected signal</span><strong>{selected.label} · {selected.display}</strong><small>{selected.role === "benchmark" ? "Reference benchmark outside the primary SME scope" : "Primary SME evidence"}</small>
      </div>
    </div>
  );
}

export function ReportStoryDeck() {
  const [selectedBars, setSelectedBars] = useState<Record<string, number>>({ "01": 0, "02": 0, "03": 0, "04": 0, "05": 0 });
  const [pathwayId, setPathwayId] = useState(pathwaySeries[0].id);
  const [synthesisIndex, setSynthesisIndex] = useState(0);
  const activePathway = pathwaySeries.find((item) => item.id === pathwayId) ?? pathwaySeries[0];
  const pathwayPoints = activePathway.values.map((value, index) => ({ label: sizeLabels[index], value, display: `${value.toFixed(1)}%`, role: index === 3 ? "benchmark" as const : undefined }));

  return (
    <section className="reportStoryDeck" id="reports" aria-labelledby="report-story-title">
      <header className="reportStoryDeckIntro">
        <p className="kicker">Six-part evidence experience</p>
        <h2 id="report-story-title">One report per scene. One decision signal at a time.</h2>
        <p>Interact with the evidence, keep each denominator visible and open the complete report when you need the full method, intervals and source trail.</p>
      </header>

      {reportSlides.map((slide, slideIndex) => (
        <article className={`reportStorySlide reportStorySlide--${slide.variant}`} id={`report-${slide.number}`} key={slide.number}>
          <div className="reportSlideField" aria-hidden="true"><i /><i /><i /><span /><span /><span /></div>
          <div className="reportSlideCopy">
            <div className="reportSlideMeta"><span>REPORT {slide.number}</span><b>{String(slideIndex + 1).padStart(2, "0")} / 06</b></div>
            <p>{slide.theme}</p>
            <h3>{slide.headline}</h3>
            <strong>{slide.title}</strong>
            <p>{slide.summary}</p>
            <dl><div><dt>Denominator</dt><dd>{slide.denominator}</dd></div><div><dt>Evidence boundary</dt><dd>{slide.boundary}</dd></div></dl>
            <a href={slide.href}>Open full report <span aria-hidden="true">↗</span></a>
          </div>
          <EvidenceBars points={slide.points} active={selectedBars[slide.number] ?? 0} onSelect={(index) => setSelectedBars((current) => ({ ...current, [slide.number]: index }))} />
        </article>
      ))}

      <article className="reportStorySlide reportStorySlide--pathways" id="report-05">
        <div className="reportSlideField" aria-hidden="true"><i /><i /><i /><span /><span /><span /></div>
        <div className="reportSlideCopy">
          <div className="reportSlideMeta"><span>REPORT 05</span><b>05 / 06</b></div>
          <p>Operational pathways</p>
          <h3>Integration and guidance are more visible than deeper automation.</h3>
          <strong>Operational AI Adoption Pathways</strong>
          <p>Select an indicator to compare its published point estimates. The interface keeps AI-user and all-business measures explicitly separate.</p>
          <dl><div><dt>Current denominator</dt><dd>{activePathway.denominator === "AI users" ? "UK businesses already reporting AI use" : "All UK businesses in each size group"}</dd></div><div><dt>Evidence boundary</dt><dd>The indicators are not stages, are never added and do not form a maturity score.</dd></div></dl>
          <a href="/reports/SME_Report_05_Operational_AI_Adoption_Pathways.pdf">Open full report <span aria-hidden="true">↗</span></a>
        </div>
        <div className="pathwayInteractiveGraphic">
          <div className="pathwayMetricTabs" role="tablist" aria-label="Operational pathway indicators">
            {pathwaySeries.map((series) => <button aria-selected={series.id === pathwayId} key={series.id} onClick={() => setPathwayId(series.id)} role="tab" type="button"><span>{series.denominator}</span><strong>{series.label}</strong></button>)}
          </div>
          <EvidenceBars points={pathwayPoints} active={selectedBars["05"] ?? 0} onSelect={(index) => setSelectedBars((current) => ({ ...current, "05": index }))} />
        </div>
      </article>

      <article className="reportStorySlide reportStorySlide--synthesis" id="synthesis">
        <div className="reportSlideField" aria-hidden="true"><i /><i /><i /><span /><span /><span /></div>
        <div className="reportSlideCopy">
          <div className="reportSlideMeta"><span>CROSS-REPORT SYNTHESIS</span><b>06 / 06</b></div>
          <p>Connected view</p>
          <h3>Access is not the same as operational depth.</h3>
          <strong>AI Adoption and Operationalisation</strong>
          <p>The synthesis connects six decision signals without pretending they form one funnel or score.</p>
          <dl><div><dt>Evidence model</dt><dd>Distinct indicators retain their source population, denominator and limitation.</dd></div><div><dt>Decision use</dt><dd>Move from “Do firms use AI?” to “Where does it operate, under what control, and with what measured result?”</dd></div></dl>
          <a href="/reports/SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation.pdf">Open the synthesis <span aria-hidden="true">↗</span></a>
        </div>
        <div className="synthesisOrbit" role="group" aria-label="Explore the six cross-report decision signals">
          <div className="synthesisCore"><span>{synthesisNodes[synthesisIndex].label}</span><strong>{synthesisNodes[synthesisIndex].title}</strong><p>{synthesisNodes[synthesisIndex].text}</p></div>
          {synthesisNodes.map((node, index) => <button aria-pressed={synthesisIndex === index} className={`synthesisNode synthesisNode--${index + 1}`} key={node.title} onClick={() => setSynthesisIndex(index)} type="button"><span>{String(index + 1).padStart(2, "0")}</span><strong>{node.title}</strong></button>)}
        </div>
      </article>
    </section>
  );
}
