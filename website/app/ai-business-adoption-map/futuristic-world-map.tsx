"use client";

import { useRef, type PointerEvent } from "react";
import styles from "./adoption-decision-map.module.css";

export function FuturisticWorldMap() {
  const mapRef = useRef<HTMLDivElement>(null);

  function moveMap(event: PointerEvent<HTMLDivElement>) {
    const element = mapRef.current;
    if (!element) return;
    const bounds = element.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    element.style.setProperty("--map-tilt-x", `${y * -5}deg`);
    element.style.setProperty("--map-tilt-y", `${x * 7}deg`);
    element.style.setProperty("--map-focus-x", `${(x + 0.5) * 100}%`);
    element.style.setProperty("--map-focus-y", `${(y + 0.5) * 100}%`);
  }

  function resetMap() {
    const element = mapRef.current;
    if (!element) return;
    element.style.setProperty("--map-tilt-x", "0deg");
    element.style.setProperty("--map-tilt-y", "0deg");
    element.style.setProperty("--map-focus-x", "72%");
    element.style.setProperty("--map-focus-y", "42%");
  }

  return (
    <div className={styles.heroWorldMap} ref={mapRef} onPointerMove={moveMap} onPointerLeave={resetMap} aria-hidden="true">
      <div className={styles.mapPhoto} />
      <div className={styles.heroWorldMapScan} />
      <div className={styles.mapHalo} />
      <svg viewBox="0 0 1200 680" role="presentation">
        <defs>
          <radialGradient id="world-glow" cx="42%" cy="34%" r="72%">
            <stop offset="0" stopColor="#b9f8ff" stopOpacity=".18" />
            <stop offset=".52" stopColor="#42bed4" stopOpacity=".08" />
            <stop offset="1" stopColor="#061725" stopOpacity=".05" />
          </radialGradient>
          <linearGradient id="coast-fill" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#9ef2ec" stopOpacity=".2" />
            <stop offset="1" stopColor="#738cff" stopOpacity=".08" />
          </linearGradient>
          <clipPath id="world-sphere"><ellipse cx="640" cy="344" rx="505" ry="280" /></clipPath>
          <filter id="map-glow"><feGaussianBlur stdDeviation="4" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        </defs>
        <ellipse className={styles.mapSphere} cx="640" cy="344" rx="505" ry="280" fill="url(#world-glow)" />
        <g className={styles.mapGraticule} clipPath="url(#world-sphere)">
          <ellipse cx="640" cy="344" rx="505" ry="280" />
          <ellipse cx="640" cy="344" rx="388" ry="280" />
          <ellipse cx="640" cy="344" rx="220" ry="280" />
          <ellipse cx="640" cy="344" rx="68" ry="280" />
          <ellipse cx="640" cy="344" rx="505" ry="72" />
          <ellipse cx="640" cy="344" rx="505" ry="154" />
          <ellipse cx="640" cy="344" rx="505" ry="232" />
        </g>
        <g className={styles.mapContinents} clipPath="url(#world-sphere)">
          <path d="M186 239l26-37 46-22 57-8 31-29 49 13 21 31 42 12 35 41-14 31-33 11-15 38-48 18-36-24-44 4-18-26-49-10-19-27z" />
          <path d="M406 343l34 12 25 39-7 54-29 75-30 58-29 5-11-46 14-47-16-55 20-45-6-35z" />
          <path d="M496 196l38-32 43 5 28 31 29 4 24 34-23 25-50-4-35-27-38-7z" />
          <path d="M567 235l36-44 48-20 54 9 36-14 45 11 34-17 52 23 36 4 35 30 67 10 44 39-5 33-42 13-16 40-52-5-30 21-52-8-34 23-45-12-39 17-30-24-54 7-28-39-50-15-9-45z" />
          <path d="M650 381l41-24 48 4 36 37 13 55-27 63-42 42-37-11-25-52-29-36 6-47z" />
          <path d="M899 449l29-25 48-2 19 22 39 5 27 27-16 31-48 9-42-18-31 7-31-31z" />
          <path d="M1075 358l26-13 28 8 6 17-18 15-34-7z" />
          <path d="M485 118l28-19 35 10 5 25-29 18-35-10z" />
        </g>
        <g className={styles.mapBorders} clipPath="url(#world-sphere)">
          <path d="M234 216l75 34 75-31 66 28M283 304l59-45 93 5M389 387l54 32-38 59M600 233l64 55 86-44 75 58 95-34M661 377l72 25 26 70M850 213l-21 93 94 42M928 445l63 48" />
        </g>
        <g className={styles.mapRoutes} filter="url(#map-glow)">
          <path d="M286 253C455 91 672 132 820 267s177 169 220 212" />
          <path d="M403 437C543 292 703 287 918 304" />
          <path d="M530 136C687 190 830 252 1015 477" />
          <path d="M724 425C602 374 468 321 286 253" />
        </g>
        <g className={styles.mapNodes}>
          <circle cx="286" cy="253" r="6" /><circle cx="403" cy="437" r="5" /><circle cx="530" cy="136" r="5" /><circle cx="724" cy="425" r="6" /><circle cx="820" cy="267" r="5" /><circle cx="918" cy="304" r="5" /><circle cx="1015" cy="477" r="7" />
        </g>
        <g className={styles.mapTravellers}>
          <circle r="4"><animateMotion dur="6.5s" repeatCount="indefinite" path="M286 253C455 91 672 132 820 267s177 169 220 212" /></circle>
          <circle r="3"><animateMotion dur="8s" begin="-3s" repeatCount="indefinite" path="M403 437C543 292 703 287 918 304" /></circle>
        </g>
      </svg>
      <div className={styles.mapTelemetry}>
        <span><i /> 07 LIVE SIGNALS</span>
        <span>LATENCY 18 MS</span>
        <span>MODEL: WORKFLOW FIT</span>
      </div>
      <span className={styles.mapCoordinate}>51.5074° N · 0.1278° W</span>
    </div>
  );
}
