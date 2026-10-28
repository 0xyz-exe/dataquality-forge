import React, { useEffect, useState } from 'react';
import { FileCode, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';
import { fetchDatasets, fetchSchemaDiff, saveExpectedSchema } from '../api';

export const SchemaRegistry: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [diff, setDiff] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDatasets().then((ds) => {
      setDatasets(ds);
      if (ds.length > 0) {
        setSelectedDatasetId(ds[0].id);
        loadDiff(ds[0].id);
      }
    });
  }, []);

  const loadDiff = (id: string) => {
    setLoading(true);
    fetchSchemaDiff(id)
      .then(setDiff)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleSelect = (id: string) => {
    setSelectedDatasetId(id);
    loadDiff(id);
  };

  const handleSetBaseline = async () => {
    if (!selectedDatasetId || !diff?.actual_schema) return;
    try {
      await saveExpectedSchema(selectedDatasetId, diff.actual_schema);
      loadDiff(selectedDatasetId);
      alert('Saved current schema as baseline!');
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Schema Registry & Evolution</h2>
          <p className="text-sm text-slate-400 mt-1">
            Detect contract violations, added/dropped fields, and breaking type drifts across dataset versions.
          </p>
        </div>

        <div className="flex items-center gap-3">
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
          <button
            onClick={handleSetBaseline}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition"
          >
            Save Baseline
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500 animate-pulse">Comparing schemas...</div>
      ) : diff?.has_expected_schema ? (
        <div className="space-y-6">
          <div
            className={`p-5 rounded-xl border flex items-center justify-between ${
              diff.diff.is_compatible
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}
          >
            <div className="flex items-center gap-3">
              {diff.diff.is_compatible ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-rose-400" />
              )}
              <div>
                <div className="font-semibold text-sm">
                  {diff.diff.is_compatible ? 'Contract In Sync' : 'Breaking Changes Detected'}
                </div>
                <div className="text-xs opacity-90">{diff.diff.summary}</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-white text-sm mb-3">Expected Contract</h3>
              <pre className="bg-slate-950 p-4 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto max-h-96">
                {JSON.stringify(diff.expected_schema, null, 2)}
              </pre>
            </div>

            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-white text-sm mb-3">Actual Inferred Schema</h3>
              <pre className="bg-slate-950 p-4 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto max-h-96">
                {JSON.stringify(diff.actual_schema, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-12 text-center text-slate-500">
          No baseline expected schema registered for this dataset. Click &ldquo;Save Baseline&rdquo; to lock current schema.
        </div>
      )}
    </div>
  );
};
