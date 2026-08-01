import Link from "next/link";
import { ReactNode } from "react";

const navItems = [
  { href: "/summary", label: "Summary" },
  { href: "/visualizer", label: "Visualizer" },
  { href: "/detector", label: "Detector" },
  { href: "/hypothesis", label: "Hypothesis" },
  { href: "/performance", label: "Performance" },
];

type AppShellProps = {
  children: ReactNode;
};

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="site">
      <header className="topbar">
        <div>
          <p className="eyebrow">Plant Disease Classification</p>
          <h1 className="brand">Leaf Intelligence Console</h1>
        </div>
        <a className="readme-link" href="https://github.com/teman67/Plant-Disease-Classification-MLOps" target="_blank" rel="noreferrer">
          Repository
        </a>
      </header>

      <nav className="nav-grid" aria-label="Primary">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href} className="nav-pill">
            {item.label}
          </Link>
        ))}
      </nav>

      <main className="page">{children}</main>
    </div>
  );
}
