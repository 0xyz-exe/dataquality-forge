import React, { useEffect, useState } from 'react';
import { FileSpreadsheet, Download, FileText, Code } from 'lucide-react';
import { fetchValidationRuns } from '../api';

export const Reports: React.FC = () => {
  const [runs, setRuns] = useState<any[]>([]);

  useEffect(() => {
    fetchValidationRuns().then(setRuns).catch(console.error);
  }, []);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Quality Reports & Data Exports</h2>
        <p className="text-sm text-slate-400 mt-1">
          Generate compliance artifacts, audit proofs, and CSV/HTML summaries for engineering and stakeholder reviews.
        </p>
      </div>

      <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
        {runs.length === 0 ? (
          <div className="p-12 text-center text-slate-500">No validation runs available to export.</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/50">
                <th className="py-3.5 px-6 font-semibold">Run ID</th>
                <th className="py-3.5 px-6 font-semibold">Quality Score</th>
                <th className="py-3.5 px-6 font-semibold">Rules Status</th>
                <th className="py-3.5 px-6 font-semibold">Executed At</th>
                <th className="py-3.5 px-6 font-semibold text-right">Download Formats</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-mono text-xs text-white">{r.id.slice(0, 8)}...</td>
                  <td className="py-4 px-6 font-bold text-cyan-400">{r.quality_score}%</td>
                  <td className="py-4 px-6 text-xs text-slate-300">
                    <span className="text-emerald-400">{r.passed_rules} passed</span> &bull;{' '}
                    <span className="text-rose-400">{r.failed_rules} failed</span>
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-400">
                    {r.created_at ? new Date(r.created_at).toLocaleString() : 'Recent'}
                  </td>
                  <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <a
                        href={`/api/v1/validation-runs/${r.id}/report?format=html`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 inline-flex items-center gap-1"
                      >
                        <FileText className="w-3.5 h-3.5 text-blue-400" /> HTML
                      </a>
                      <a
                        href={`/api/v1/validation-runs/${r.id}/report?format=csv`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 inline-flex items-center gap-1"
                      >
                        <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" /> CSV
                      </a>
                      <a
                        href={`/api/v1/validation-runs/${r.id}/report?format=json`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 inline-flex items-center gap-1"
                      >
                        <Code className="w-3.5 h-3.5 text-amber-400" /> JSON
                      </a>
                    </div>
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
