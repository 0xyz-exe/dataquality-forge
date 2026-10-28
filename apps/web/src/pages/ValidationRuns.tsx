import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PlayCircle, CheckCircle2, XCircle, ArrowUpRight, Download } from 'lucide-react';
import { fetchValidationRuns } from '../api';

export const ValidationRuns: React.FC = () => {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchValidationRuns()
      .then(setRuns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Validation Execution Runs</h2>
        <p className="text-sm text-slate-400 mt-1">
          Audit trail of automated data assertions, quality scoring, and rule pass/fail distributions.
        </p>
      </div>

      <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500 animate-pulse">Loading runs history...</div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">No validation runs found.</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/50">
                <th className="py-3 px-6 font-semibold">Run ID</th>
                <th className="py-3 px-6 font-semibold">Status</th>
                <th className="py-3 px-6 font-semibold">Quality Score</th>
                <th className="py-3 px-6 font-semibold">Passed / Failed</th>
                <th className="py-3 px-6 font-semibold">Duration</th>
                <th className="py-3 px-6 font-semibold">Timestamp</th>
                <th className="py-3 px-6 font-semibold text-right">Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-mono text-xs text-blue-400">
                    <Link to={`/datasets/${r.dataset_id}`} className="hover:underline">
                      {r.id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td className="py-4 px-6">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" /> {r.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 font-bold text-white text-base">
                    {r.quality_score !== null ? `${r.quality_score}%` : 'N/A'}
                  </td>
                  <td className="py-4 px-6 text-xs">
                    <span className="text-emerald-400 font-semibold">{r.passed_rules} passed</span>
                    {r.failed_rules > 0 && (
                      <span className="text-rose-400 font-semibold ml-2">{r.failed_rules} failed</span>
                    )}
                  </td>
                  <td className="py-4 px-6 font-mono text-xs text-slate-400">{r.duration_ms} ms</td>
                  <td className="py-4 px-6 text-xs text-slate-400">
                    {r.created_at ? new Date(r.created_at).toLocaleString() : 'Recent'}
                  </td>
                  <td className="py-4 px-6 text-right">
                    <a
                      href={`/api/v1/validation-runs/${r.id}/report?format=html`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium"
                    >
                      <Download className="w-3.5 h-3.5" /> HTML
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
