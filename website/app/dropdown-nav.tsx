"use client";

import { useId, useState } from "react";

type DropdownItem = {
  href: string;
  label: string;
};

export function NavDropdown({
  label,
  items,
}: {
  label: string;
  items: DropdownItem[];
}) {
  const [open, setOpen] = useState(false);
  const menuId = useId();

  return (
    <div
      className={`navMenu${open ? " open" : ""}`}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        aria-controls={menuId}
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
        type="button"
      >
        {label}
      </button>
      {open ? (
        <div className="navDropdown" id={menuId}>
          <div className="navDropdownPanel">
            {items.map((item) => (
              <a href={item.href} key={item.label} onClick={() => setOpen(false)}>
                {item.label}
              </a>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
