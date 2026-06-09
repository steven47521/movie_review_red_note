import { Suspense } from "react";

import WorkspaceShell from "@/components/workspace/WorkspaceShell";

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="rp-app app-shell" style={{ padding: 24 }}>加载工作台…</div>}>
      <WorkspaceShell />
    </Suspense>
  );
}
