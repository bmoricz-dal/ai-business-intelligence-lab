"use client";

import Link from "next/link";
import { useId, useRef, useState } from "react";

type DropdownItem = {
  href: string;
  label: string;
};

export function NavDropdown({
  active = false,
  href,
  label,
  items,
}: {
  active?: boolean;
  href: string;
  label: string;
  items: DropdownItem[];
}) {
  const [open, setOpen] = useState(false);
  const menuId = useId();
  const toggleRef = useRef<HTMLButtonElement>(null);

  return (
    <div
      className={`navMenu${open ? " open" : ""}`}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          setOpen(false);
          toggleRef.current?.focus();
        }
      }}
    >
      <Link
        aria-current={active ? "page" : undefined}
        className="navMenuLink"
        href={href}
      >
        {label}
      </Link>
      <button
        aria-controls={menuId}
        aria-expanded={open}
        aria-label={`Toggle ${label} submenu`}
        className="navMenuToggle"
        onClick={() => setOpen((current) => !current)}
        ref={toggleRef}
        type="button"
      >
        <span aria-hidden="true">⌄</span>
      </button>
      {open ? (
        <div className="navDropdown" id={menuId}>
          <div className="navDropdownPanel">
            {items.map((item) => (
              <Link href={item.href} key={item.label} onClick={() => setOpen(false)}>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
