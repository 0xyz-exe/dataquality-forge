import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  Database,
  BarChart2,
  ShieldCheck,
  PlayCircle,
  FileCode,
  FileSpreadsheet,
} from 'lucide-react';

interface SidebarProps {
  currentProject?: string;
}

export const Sidebar: React.FC<SidebarProps> = () => {
  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Projects', path: '/projects', icon: FolderKanban },
    { name: 'Datasets', path: '/datasets', icon: Database },
    { name: 'Profiling', path: '/profiling', icon: BarChart2 },
    { name: 'Validation Rules', path: '/rules', icon: ShieldCheck },
    { name: 'Validation Runs', path: '/runs', icon: PlayCircle },
    { name: 'Schema Registry', path: '/schema', icon: FileCode },
    { name: 'Reports', path: '/reports', icon: FileSpreadsheet },
  ];

  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/30">
          DQ
        </div>
        <div>
          <div className="font-semibold text-sm tracking-wide text-white">DataQuality Forge</div>
          <div className="text-[11px] text-slate-400 font-mono">v0.1.0 • Open Source</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800/80">
        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs">
          <div className="text-slate-400 mb-1">Engine Engine Mode</div>
          <div className="flex items-center gap-2 text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            DuckDB In-Memory &bull; Local
          </div>
        </div>
      </div>
    </aside>
  );
};
