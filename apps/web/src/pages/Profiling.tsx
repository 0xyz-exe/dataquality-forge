import React, { useEffect, useState } from 'react';
import { BarChart2, Database, Play, CheckCircle2 } from 'lucide-react';
import { fetchDatasets, runProfile, fetchLatestProfile } from '../api';

export const Profiling: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDatasets().then((ds) => {
      setDatasets(ds);
      if (ds.length > 0) {
        setSelectedDatasetId(ds[0].id);
        fetchLatestProfile(ds[0].id).then(setProfile);
      }
    });
  }, []);

  const handleSelect = (id: string) => {
    setSelectedDatasetId(id);
    fetchLatestProfile(id).then(setProfile);
  };

  const handleRun = async () => {
    if (!selectedDatasetId) return;
    setLoading(true);
    try {
      const res = await runProfile(selectedDatasetId);
      setProfile(res.summary);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedDs = datasets.find((d) => d.id === selectedDatasetId);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Data Profiling Studio</h2>
          <p className="text-sm text-slate-400 mt-1">
            Automated exploratory data analysis, distinct value counting, and outlier profiling.
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
                {d.name} ({d.file_format})
              </option>
            ))}
          </select>
          <button
            onClick={handleRun}
            disabled={loading || !selectedDatasetId}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            <BarChart2 className="w-4 h-4" />
            {loading ? 'Profiling...' : 'Generate Profile'}
          </button>
        </div>
      </div>

      {profile ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Total Rows / Columns</div>
              <div className="text-2xl font-bold text-white mt-2">
                {profile.total_rows} &bull; {profile.total_columns}
              </div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Missing Rate</div>
              <div className="text-2xl font-bold text-rose-400 mt-2">
                {profile.missing_cell_percentage}%
              </div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Duplicate Rows</div>
              <div className="text-2xl font-bold text-amber-400 mt-2">
                {profile.duplicate_rows} ({profile.duplicate_row_percentage}%)
              </div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Execution Time</div>
              <div className="text-2xl font-bold text-cyan-400 mt-2 font-mono">
                {profile.duration_ms} ms
              </div>
            </div>
          </div>

          <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 bg-slate-900/50 border-b border-slate-800 font-semibold text-sm text-white">
              Column Analysis Details ({profile.column_profiles.length} columns)
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-900/20">
                    <th className="py-3 px-4 font-semibold">Column</th>
                    <th className="py-3 px-4 font-semibold">Type</th>
                    <th className="py-3 px-4 font-semibold">Null Count</th>
                    <th className="py-3 px-4 font-semibold">Distinct</th>
                    <th className="py-3 px-4 font-semibold">Statistics & Distributions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {profile.column_profiles.map((cp: any) => (
                    <tr key={cp.name} className="hover:bg-slate-800/20">
                      <td className="py-3 px-4 font-semibold text-white">{cp.name}</td>
                      <td className="py-3 px-4 font-mono text-[11px] text-blue-400">{cp.inferred_type}</td>
                      <td className="py-3 px-4 font-mono">{cp.null_count} ({cp.null_percentage}%)</td>
                      <td className="py-3 px-4 font-mono">{cp.distinct_count} ({cp.distinct_percentage}%)</td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {cp.numeric_stats && `min=${cp.numeric_stats.min}, max=${cp.numeric_stats.max}, mean=${cp.numeric_stats.mean}`}
                        {cp.min_length !== undefined && `length=[${cp.min_length}-${cp.max_length}], whitespace=${cp.whitespace_count}`}
                        {cp.datetime_stats && `range: ${cp.datetime_stats.min?.slice(0, 10)} to ${cp.datetime_stats.max?.slice(0, 10)}`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-12 text-center text-slate-500">
          No profile found for selected dataset. Click &ldquo;Generate Profile&rdquo; to start.
        </div>
      )}
    </div>
  );
};
