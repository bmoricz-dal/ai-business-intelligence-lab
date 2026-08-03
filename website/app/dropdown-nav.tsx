"use client";

import Link from "next/link";
import { useId, useRef, useState } from "react";

type DropdownItem = {
  href: string;
  label: string;
  items?: DropdownItem[];
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
  const [nestedOpen, setNestedOpen] = useState<string | null>(null);
  const menuId = useId();
  const toggleRef = useRef<HTMLButtonElement>(null);

  return (
    <div
      className={`navMenu${open ? " open" : ""}`}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) {
          setOpen(false);
          setNestedOpen(null);
        }
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => {
        setOpen(false);
        setNestedOpen(null);
      }}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          setOpen(false);
          setNestedOpen(null);
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
            {items.map((item, index) => item.items ? (
              <div
                className={`navNestedMenu${nestedOpen === item.label ? " open" : ""}`}
                key={item.label}
                onMouseEnter={() => setNestedOpen(item.label)}
                onMouseLeave={() => setNestedOpen(null)}
              >
                <div className="navNestedTrigger">
                  <Link className="navNestedLink" href={item.href} onClick={() => setOpen(false)}>
                    {item.label}
                  </Link>
                  <button
                    aria-controls={`${menuId}-nested-${index}`}
                    aria-expanded={nestedOpen === item.label}
                    aria-label={`Toggle ${item.label} studies submenu`}
                    className="navNestedToggle"
                    onClick={() => setNestedOpen((current) => current === item.label ? null : item.label)}
                    type="button"
                  >
                    <span aria-hidden="true">›</span>
                  </button>
                </div>
                {nestedOpen === item.label ? (
                  <div className="navNestedDropdown" id={`${menuId}-nested-${index}`}>
                    <div className="navNestedPanel">
                      {item.items.map((nestedItem) => (
                        <Link
                          href={nestedItem.href}
                          key={nestedItem.label}
                          onClick={() => {
                            setNestedOpen(null);
                            setOpen(false);
                          }}
                        >
                          {nestedItem.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
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
