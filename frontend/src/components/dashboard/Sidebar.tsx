import Link from "next/link";

const NAV_ITEMS = [
  { href: "/dashboard", label: "工作台" },
  { href: "/dashboard/create", label: "新建创作" },
  { href: "/dashboard/review", label: "Review Room" },
];

type SidebarProps = {
  activeHref?: string;
};

export default function Sidebar({ activeHref = "/dashboard" }: SidebarProps) {
  return (
    <aside className="od-sidebar">
      <div style={{ marginBottom: "var(--space-8)", paddingInline: "var(--space-2)" }}>
        <p className="od-eyebrow">RedNote</p>
        <h1 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-1)" }}>
          片语
        </h1>
        <p className="od-muted" style={{ marginTop: "var(--space-1)" }}>
          经典电影创作助手
        </p>
      </div>

      <nav style={{ display: "flex", flex: 1, flexDirection: "column", gap: "var(--space-1)" }}>
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={
              activeHref === item.href ? "od-nav-link od-nav-link-active" : "od-nav-link"
            }
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="od-card" style={{ padding: "var(--space-3)", fontSize: "var(--text-xs)" }}>
        <span className="od-muted">nexu-io/open-design · Linear + dashboard</span>
      </div>
    </aside>
  );
}
