"use client";

import { useEffect, useRef, useState } from "react";

type OutlineItem = {
  id: string;
  label: string;
};

function slugify(value: string, fallback: string) {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return slug || fallback;
}

export function EditorialExperience() {
  const progressRef = useRef<HTMLSpanElement>(null);
  const [items, setItems] = useState<OutlineItem[]>([]);
  const [activeId, setActiveId] = useState("");
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const main = document.querySelector("main");
    if (!main) return;

    const sections = Array.from(main.querySelectorAll<HTMLElement>(":scope > section"));
    const usedIds = new Set<string>();
    const outline = sections
      .map((section, index) => {
        const heading = section.querySelector<HTMLElement>("h1, h2");
        if (!heading?.textContent) return null;
        const base = section.id || slugify(heading.textContent, `section-${index + 1}`);
        let id = base;
        let suffix = 2;
        while (usedIds.has(id)) {
          id = `${base}-${suffix}`;
          suffix += 1;
        }
        usedIds.add(id);
        section.id = id;
        return { id, label: heading.textContent.trim() };
      })
      .filter((item): item is OutlineItem => Boolean(item));

    const initialStateFrame = window.requestAnimationFrame(() => {
      setItems(outline);
      setActiveId(outline[0]?.id ?? "");
    });

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reducedMotion) {
      sections.forEach((section) => {
        section.classList.add("editorialReveal");
        if (section.getBoundingClientRect().top < window.innerHeight * 0.92) {
          section.classList.add("isRevealed");
        }
      });
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("isRevealed");
            setActiveId((entry.target as HTMLElement).id);
          }
        });
      },
      { rootMargin: "-18% 0px -62% 0px", threshold: 0.01 },
    );
    sections.forEach((section) => observer.observe(section));

    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      progressRef.current?.style.setProperty("--reading-progress", `${value * 100}%`);
    };

    const updatePointer = (event: PointerEvent) => {
      document.documentElement.style.setProperty("--pointer-x", `${event.clientX}px`);
      document.documentElement.style.setProperty("--pointer-y", `${event.clientY}px`);
    };

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("pointermove", updatePointer, { passive: true });
    window.addEventListener("keydown", closeOnEscape);

    return () => {
      window.cancelAnimationFrame(initialStateFrame);
      observer.disconnect();
      window.removeEventListener("scroll", updateProgress);
      window.removeEventListener("pointermove", updatePointer);
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  async function copyPageLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  function moveTo(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    setOpen(false);
  }

  return (
    <>
      <span className="readingProgress" ref={progressRef} aria-hidden="true" />
      {items.length > 2 ? (
        <aside className={`editorialOutline ${open ? "isOpen" : ""}`} aria-label="Page tools">
          <button
            aria-controls="editorial-outline-panel"
            aria-expanded={open}
            className="editorialOutlineToggle"
            onClick={() => setOpen((value) => !value)}
            type="button"
          >
            <span aria-hidden="true">{open ? "×" : "≡"}</span>
            <strong>{open ? "Close" : "Page outline"}</strong>
          </button>
          <div className="editorialOutlinePanel" id="editorial-outline-panel">
            <header><span>ON THIS PAGE</span><b>{String(items.length).padStart(2, "0")} SECTIONS</b></header>
            <nav aria-label="On this page">
              {items.map((item, index) => (
                <button
                  aria-current={activeId === item.id ? "location" : undefined}
                  key={item.id}
                  onClick={() => moveTo(item.id)}
                  type="button"
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{item.label}</strong>
                </button>
              ))}
            </nav>
            <button className="copyPageLink" onClick={copyPageLink} type="button">
              {copied ? "Link copied" : "Copy page link"}
            </button>
          </div>
        </aside>
      ) : null}
    </>
  );
}
