"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

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
  const [navigatorMount, setNavigatorMount] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const main = document.querySelector("main");
    if (!main) return;

    const sections = Array.from(main.querySelectorAll<HTMLElement>(":scope > section"));
    const mount = main.querySelector<HTMLElement>(".pageSectionNavigatorMount");
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
      setNavigatorMount(mount);
    });

    const atmosphereLayers: HTMLElement[] = [];
    const reactiveSurfaces = Array.from(
      main.querySelectorAll<HTMLElement>(
        "article, .actionLinkGrid > a, .methodDownloadCards > a, .methodDownloads > a, .contactCards > a, .releaseActions > a",
      ),
    );

    sections.forEach((section, index) => {
      if (section.matches(".pageHero, .microCaseHero, .cinematicInterlude, .cityAerialStory, .landscapeStory, .systemVisualFeature, .signalScene")) return;
      section.classList.add("immersiveSection");
      section.dataset.scene = ["orbit", "scan", "constellation", "wave"][index % 4];
      const layer = document.createElement("div");
      layer.className = "sectionAtmosphere";
      layer.setAttribute("aria-hidden", "true");
      for (let point = 0; point < 6; point += 1) layer.append(document.createElement("i"));
      section.prepend(layer);
      atmosphereLayers.push(layer);
    });

    reactiveSurfaces.forEach((surface) => {
      surface.classList.add("reactiveSurface");
      if (!surface.querySelector(":scope > .surfaceGlow")) {
        const glow = document.createElement("span");
        glow.className = "surfaceGlow";
        glow.setAttribute("aria-hidden", "true");
        surface.prepend(glow);
      }
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

    const updateScrollState = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      progressRef.current?.style.setProperty("--reading-progress", `${value * 100}%`);

      const anchorLine = Math.min(220, window.innerHeight * 0.3);
      let current = outline[0]?.id ?? "";
      sections.forEach((section) => {
        if (section.id && section.getBoundingClientRect().top <= anchorLine) current = section.id;
      });
      if (current) setActiveId(current);
    };

    const updatePointer = (event: PointerEvent) => {
      document.documentElement.style.setProperty("--pointer-x", `${event.clientX}px`);
      document.documentElement.style.setProperty("--pointer-y", `${event.clientY}px`);
      const surface = (event.target as HTMLElement | null)?.closest<HTMLElement>(".reactiveSurface");
      if (surface) {
        const bounds = surface.getBoundingClientRect();
        surface.style.setProperty("--surface-x", `${event.clientX - bounds.left}px`);
        surface.style.setProperty("--surface-y", `${event.clientY - bounds.top}px`);
      }
    };

    updateScrollState();
    window.addEventListener("scroll", updateScrollState, { passive: true });
    window.addEventListener("resize", updateScrollState, { passive: true });
    window.addEventListener("pointermove", updatePointer, { passive: true });

    return () => {
      window.cancelAnimationFrame(initialStateFrame);
      observer.disconnect();
      window.removeEventListener("scroll", updateScrollState);
      window.removeEventListener("resize", updateScrollState);
      window.removeEventListener("pointermove", updatePointer);
      atmosphereLayers.forEach((layer) => layer.remove());
      reactiveSurfaces.forEach((surface) => {
        surface.classList.remove("reactiveSurface");
        surface.querySelector(":scope > .surfaceGlow")?.remove();
      });
    };
  }, []);

  function moveTo(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    window.history.replaceState(null, "", `#${id}`);
    setActiveId(id);
  }

  return (
    <>
      <span className="readingProgress" ref={progressRef} aria-hidden="true" />
      {navigatorMount && items.length > 2
        ? createPortal(
            <nav className="pageSectionNavigator" aria-label="Explore this page">
              <span className="pageSectionNavigatorLabel">Explore this page</span>
              <div>
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
              </div>
            </nav>,
            navigatorMount,
          )
        : null}
    </>
  );
}
