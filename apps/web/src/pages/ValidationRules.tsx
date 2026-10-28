import React, { useEffect, useState } from 'react';
import { ShieldCheck, Plus, Trash2, Database } from 'lucide-react';
import { fetchDatasets, fetchRules, deleteRule } from '../api';

export const ValidationRules: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [rules, setRules] = useState<any[]>([]);

  useEffect(() => {
    fetchDatasets().then((ds) => {
      setDatasets(ds);
      if (ds.length > 0) {
        setSelectedDatasetId(ds[0].id);
        fetchRules(ds[0].id).then(setRules);
      }
    });
  }, []);

  const handleSelect = (id: string) => {
    setSelectedDatasetId(id);
    fetchRules(id).then(setRules);
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm('Delete rule?')) return;
    try {
      await deleteRule(ruleId);
      if (selectedDatasetId) {
        const updated = await fetchRules(selectedDatasetId);
        setRules(updated);
      }
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Validation Rules Registry</h2>
          <p className="text-sm text-slate-400 mt-1">
            Browse assertion policies, integrity checks, and categorical boundaries configured across datasets.
          </p>
        </div>

        <select
          value={selectedDatasetId}
          onChange={(e) => handleSelect(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
        >
          {datasets.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
        {rules.length > 0 ? (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/50">
                <th className="py-3 px-6 font-semibold">Rule Name</th>
                <th className="py-3 px-6 font-semibold">Type</th>
                <th className="py-3 px-6 font-semibold">Target Columns</th>
                <th className="py-3 px-6 font-semibold">Severity</th>
                <th className="py-3 px-6 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {rules.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-medium text-white">{r.name}</td>
                  <td className="py-4 px-6">
                    <span className="font-mono text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                      {r.rule_type}
                    </span>
                  </td>
                  <td className="py-4 px-6 font-mono text-xs text-slate-300">
                    {r.target_columns.join(', ')}
                  </td>
                  <td className="py-4 px-6">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        r.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : r.severity === 'ERROR'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {r.severity}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <button
                      onClick={() => handleDelete(r.id)}
                      className="text-slate-500 hover:text-rose-400 p-1 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="py-12 text-center text-slate-500 text-sm">
            No rules configured for this dataset yet. Go to Dataset details to author rules.
          </div>
        )}
      </div>
    </div>
  );
};
