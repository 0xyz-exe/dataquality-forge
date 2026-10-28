import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, Database, CheckCircle2 } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [live, setLive] = useState<boolean | null>(null);

  useEffect(() => {
    fetch('/health/live')
      .then((res) => (res.ok ? setLive(true) : setLive(false)))
      .catch(() => setLive(false));
  }, []);

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0d1322]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <h1 className="text-base font-medium text-slate-200">
          Data Quality Profiling & Validation Workspace
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs px-2.5 py-1 rounded-full border border-slate-800 bg-slate-900/60">
          {live ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium">API Connected</span>
            </>
          ) : (
            <>
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-amber-400 font-medium">Connecting...</span>
            </>
          )}
        </div>
        <div className="h-4 w-px bg-slate-800"></div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Database className="w-3.5 h-3.5 text-blue-400" />
          <span>Storage: Local / Safe Sandbox</span>
        </div>
      </div>
    </header>
  );
};
