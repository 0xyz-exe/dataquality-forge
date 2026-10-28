import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FolderKanban,
  Database,
  PlayCircle,
  Award,
  ArrowUpRight,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import { fetchOverview } from '../api';

export const Overview: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="h-8 bg-slate-800 rounded w-48"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-slate-800/60 rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Platform Overview</h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time quality health, schema compliance, and validation telemetry across all datasets.
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/datasets"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-blue-500/20"
          >
            <Plus className="w-4 h-4" />
            Upload Dataset
          </Link>
          <Link
            to="/runs"
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-sm font-medium transition"
          >
            <PlayCircle className="w-4 h-4 text-emerald-400" />
            Validation Runs
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Total Projects</span>
            <FolderKanban className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{data?.total_projects || 0}</div>
          <div className="text-xs text-slate-500 mt-2">Active isolation domains</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Ingested Datasets</span>
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{data?.total_datasets || 0}</div>
          <div className="text-xs text-slate-500 mt-2">CSV, JSONL, Parquet formats</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Validation Executions</span>
            <PlayCircle className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{data?.total_validation_runs || 0}</div>
          <div className="text-xs text-slate-500 mt-2">Automated quality passes</div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Mean Quality Score</span>
            <Award className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-emerald-400 mt-3">
            {data?.average_quality_score !== null && data?.average_quality_score !== undefined
              ? `${data.average_quality_score}%`
              : 'N/A'}
          </div>
          <div className="text-xs text-slate-500 mt-2">Weighted severity formula</div>
        </div>
      </div>

      {/* Two column grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Runs Table */}
        <div className="lg:col-span-2 bg-[#111827] border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white text-base">Recent Validation Runs</h3>
            <Link to="/runs" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
              View all <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {data?.recent_runs?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                    <th className="pb-3 font-semibold">Run ID</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold">Quality Score</th>
                    <th className="pb-3 font-semibold">Passed / Failed</th>
                    <th className="pb-3 font-semibold">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {data.recent_runs.map((r: any) => (
                    <tr key={r.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 font-mono text-xs text-slate-300">
                        <Link to={`/runs/${r.id}`} className="hover:text-blue-400 underline decoration-slate-700">
                          {r.id.slice(0, 8)}...
                        </Link>
                      </td>
                      <td className="py-3">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" /> {r.status}
                        </span>
                      </td>
                      <td className="py-3 font-semibold text-white">
                        {r.quality_score !== null ? `${r.quality_score}%` : 'N/A'}
                      </td>
                      <td className="py-3 text-xs">
                        <span className="text-emerald-400 font-medium">{r.passed_rules} passed</span>
                        {r.failed_rules > 0 && (
                          <span className="text-rose-400 font-medium ml-2">{r.failed_rules} failed</span>
                        )}
                      </td>
                      <td className="py-3 text-xs text-slate-400">
                        {r.created_at ? new Date(r.created_at).toLocaleString() : 'Recent'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-500 text-sm">
              No validation runs executed yet. Select a dataset and execute a run.
            </div>
          )}
        </div>

        {/* Recent Datasets */}
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white text-base">Active Datasets</h3>
            <Link to="/datasets" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
              Browse <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {data?.recent_datasets?.length > 0 ? (
              data.recent_datasets.map((d: any) => (
                <Link
                  key={d.id}
                  to={`/datasets/${d.id}`}
                  className="block p-3 rounded-lg border border-slate-800 bg-slate-900/50 hover:bg-slate-800/50 transition group"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm text-slate-200 group-hover:text-blue-400 transition">
                      {d.name}
                    </span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {d.file_format}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-500 mt-2">
                    <span>{d.row_count || 0} rows</span>
                    <span>&bull;</span>
                    <span>{d.column_count || 0} columns</span>
                  </div>
                </Link>
              ))
            ) : (
              <div className="py-10 text-center text-slate-500 text-sm">
                No datasets ingested yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
