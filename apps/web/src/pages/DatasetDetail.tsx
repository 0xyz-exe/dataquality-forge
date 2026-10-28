import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Database,
  BarChart2,
  Table as TableIcon,
  ShieldCheck,
  History,
  FileCode,
  Play,
  Plus,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Download,
  Info,
} from 'lucide-react';
import {
  fetchDataset,
  fetchDatasetPreview,
  fetchLatestProfile,
  runProfile,
  fetchRules,
  createRule,
  deleteRule,
  runValidation,
  fetchValidationRuns,
  fetchSchemaDiff,
  saveExpectedSchema,
} from '../api';

export const DatasetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'preview' | 'profiles' | 'schema' | 'rules' | 'runs'>('overview');

  // Preview
  const [preview, setPreview] = useState<any>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Profiling
  const [profile, setProfile] = useState<any>(null);
  const [profiling, setProfiling] = useState(false);

  // Rules
  const [rules, setRules] = useState<any[]>([]);
  const [showRuleModal, setShowRuleModal] = useState(false);
  const [ruleName, setRuleName] = useState('');
  const [ruleType, setRuleType] = useState('not_null');
  const [targetCol, setTargetCol] = useState('');
  const [severity, setSeverity] = useState('ERROR');
  const [paramKey, setParamKey] = useState('');
  const [paramVal, setParamVal] = useState('');

  // Runs
  const [runs, setRuns] = useState<any[]>([]);
  const [validating, setValidating] = useState(false);
  const [activeRun, setActiveRun] = useState<any>(null);

  // Schema diff
  const [schemaDiff, setSchemaDiff] = useState<any>(null);

  useEffect(() => {
    if (!id) return;
    fetchDataset(id).then(setDataset).catch(console.error);
    fetchLatestProfile(id).then(setProfile).catch(console.error);
    fetchRules(id).then(setRules).catch(console.error);
    fetchValidationRuns(id).then(setRuns).catch(console.error);
    fetchSchemaDiff(id).then(setSchemaDiff).catch(console.error);
  }, [id]);

  useEffect(() => {
    if (activeTab === 'preview' && id && !preview) {
      setPreviewLoading(true);
      fetchDatasetPreview(id, 50)
        .then(setPreview)
        .catch(console.error)
        .finally(() => setPreviewLoading(false));
    }
  }, [activeTab, id]);

  const handleRunProfile = async () => {
    if (!id) return;
    setProfiling(true);
    try {
      const res = await runProfile(id);
      setProfile(res.summary);
      setActiveTab('profiles');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setProfiling(false);
    }
  };

  const handleRunValidation = async () => {
    if (!id) return;
    setValidating(true);
    try {
      const res = await runValidation(id);
      setActiveRun(res);
      const updatedRuns = await fetchValidationRuns(id);
      setRuns(updatedRuns);
      setActiveTab('runs');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setValidating(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !ruleName.trim() || !targetCol) return;
    let parameters: any = {};
    if (ruleType === 'min_value' || ruleType === 'max_value') {
      parameters[ruleType] = parseFloat(paramVal || '0');
    } else if (ruleType === 'value_between') {
      const parts = paramVal.split(',').map((p) => parseFloat(p.trim()));
      parameters = { min_value: parts[0] || 0, max_value: parts[1] || 100 };
    } else if (ruleType === 'in_set') {
      parameters = { allowed_values: paramVal.split(',').map((s) => s.trim()) };
    } else if (ruleType === 'regex_match') {
      parameters = { pattern: paramVal };
    }

    try {
      await createRule(id, {
        name: ruleName,
        rule_type: ruleType,
        target_columns: [targetCol],
        parameters,
        severity,
      });
      const updated = await fetchRules(id);
      setRules(updated);
      setShowRuleModal(false);
      setRuleName('');
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('Delete this validation rule?')) return;
    try {
      await deleteRule(ruleId);
      if (id) {
        const updated = await fetchRules(id);
        setRules(updated);
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSaveExpected = async () => {
    if (!id || !dataset?.schema_metadata) return;
    try {
      await saveExpectedSchema(id, dataset.schema_metadata);
      const diff = await fetchSchemaDiff(id);
      setSchemaDiff(diff);
      alert('Current schema saved as baseline Expected Schema!');
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (!dataset) {
    return <div className="p-8 text-slate-500 animate-pulse">Loading dataset metadata...</div>;
  }

  const columnsList = dataset.schema_metadata ? Object.keys(dataset.schema_metadata) : [];

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight text-white">{dataset.name}</h2>
            <span className="uppercase text-xs font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {dataset.file_format}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            ID: {dataset.id} &bull; Checksum: {dataset.file_checksum ? dataset.file_checksum.slice(0, 16) : 'N/A'}...
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunProfile}
            disabled={profiling}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            {profiling ? 'Profiling...' : 'Run Profiler'}
          </button>
          <button
            onClick={handleRunValidation}
            disabled={validating}
            className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-blue-500/20 disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            {validating ? 'Validating...' : 'Run Validation'}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-1">
        {[
          { key: 'overview', label: 'Overview', icon: Database },
          { key: 'preview', label: 'Data Preview', icon: TableIcon },
          { key: 'profiles', label: 'Column Profiles', icon: BarChart2 },
          { key: 'schema', label: 'Schema & Diff', icon: FileCode },
          { key: 'rules', label: `Rules (${rules.length})`, icon: ShieldCheck },
          { key: 'runs', label: `Runs (${runs.length})`, icon: History },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key as any)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition -mb-px ${
                activeTab === t.key
                  ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Row Count</div>
              <div className="text-2xl font-bold text-white mt-2">{dataset.row_count || 0}</div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Column Count</div>
              <div className="text-2xl font-bold text-white mt-2">{dataset.column_count || 0}</div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">File Size</div>
              <div className="text-2xl font-bold text-white mt-2 font-mono">
                {(dataset.file_size_bytes / 1024).toFixed(1)} KB
              </div>
            </div>
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
              <div className="text-xs text-slate-400 uppercase font-semibold">Active Rules</div>
              <div className="text-2xl font-bold text-emerald-400 mt-2">{rules.length}</div>
            </div>
          </div>

          <div className="bg-[#111827] border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold text-white text-base mb-3">Dataset Description</h3>
            <p className="text-sm text-slate-300">
              {dataset.description || 'No description provided.'}
            </p>
          </div>
        </div>
      )}

      {/* Tab: Data Preview */}
      {activeTab === 'preview' && (
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white text-base">Bounded Data Preview (Top 50 Rows)</h3>
            <span className="text-xs text-slate-400">Total Rows: {dataset.row_count}</span>
          </div>

          {previewLoading ? (
            <div className="py-12 text-center text-slate-500 animate-pulse">Loading preview rows...</div>
          ) : preview?.rows?.length > 0 ? (
            <div className="overflow-x-auto border border-slate-800 rounded-lg">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase">
                    {preview.columns.map((c: string) => (
                      <th key={c} className="py-2.5 px-4 font-semibold whitespace-nowrap">
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {preview.rows.map((row: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      {preview.columns.map((c: string) => (
                        <td key={c} className="py-2 px-4 whitespace-nowrap font-mono text-slate-300">
                          {row[c] !== null && row[c] !== undefined ? String(row[c]) : (
                            <span className="text-rose-400/80 italic">null</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500">No preview records returned.</div>
          )}
        </div>
      )}

      {/* Tab: Column Profiles */}
      {activeTab === 'profiles' && (
        <div className="space-y-6">
          {!profile ? (
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-12 text-center">
              <BarChart2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white">No Profiling Data</h3>
              <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
                Execute profiling engine to compute statistics, distribution metrics, and identify anomalies.
              </p>
              <button
                onClick={handleRunProfile}
                disabled={profiling}
                className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium"
              >
                <BarChart2 className="w-4 h-4" /> {profiling ? 'Profiling...' : 'Generate Profile'}
              </button>
            </div>
          ) : (
            <>
              {/* Profile KPI */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Duplicate Rows</div>
                  <div className="text-2xl font-bold text-amber-400 mt-2">
                    {profile.duplicate_rows} ({profile.duplicate_row_percentage}%)
                  </div>
                </div>
                <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Missing Cells</div>
                  <div className="text-2xl font-bold text-rose-400 mt-2">
                    {profile.missing_cells} ({profile.missing_cell_percentage}%)
                  </div>
                </div>
                <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Complete Rows</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-2">
                    {profile.complete_rows} ({profile.complete_row_percentage}%)
                  </div>
                </div>
                <div className="bg-[#111827] border border-slate-800 rounded-xl p-5">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Execution Time</div>
                  <div className="text-2xl font-bold text-white mt-2 font-mono">
                    {profile.duration_ms} ms
                  </div>
                </div>
              </div>

              {/* Profiles Table */}
              <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                  <h3 className="font-semibold text-white text-sm">Column Distribution & Statistics</h3>
                  <span className="text-xs text-slate-400 font-mono">Mode: {profile.mode}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-900/30">
                        <th className="py-3 px-4 font-semibold">Column</th>
                        <th className="py-3 px-4 font-semibold">Type</th>
                        <th className="py-3 px-4 font-semibold">Nulls (%)</th>
                        <th className="py-3 px-4 font-semibold">Distinct (%)</th>
                        <th className="py-3 px-4 font-semibold">Metrics & Distribution</th>
                        <th className="py-3 px-4 font-semibold">Frequent Values</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {profile.column_profiles.map((cp: any) => (
                        <tr key={cp.name} className="hover:bg-slate-800/20">
                          <td className="py-3 px-4 font-semibold text-white">{cp.name}</td>
                          <td className="py-3 px-4">
                            <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-800 text-blue-400">
                              {cp.inferred_type}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono">
                            {cp.null_count} ({cp.null_percentage}%)
                          </td>
                          <td className="py-3 px-4 font-mono">
                            {cp.distinct_count} ({cp.distinct_percentage}%)
                          </td>
                          <td className="py-3 px-4 text-slate-300 font-mono">
                            {cp.numeric_stats && (
                              <div>
                                min={cp.numeric_stats.min}, max={cp.numeric_stats.max}, mean={cp.numeric_stats.mean}
                              </div>
                            )}
                            {cp.min_length !== undefined && (
                              <div>
                                len=[{cp.min_length}-{cp.max_length}], whitespace={cp.whitespace_count}
                              </div>
                            )}
                            {cp.datetime_stats && (
                              <div>
                                range: {cp.datetime_stats.min?.slice(0, 10)} to {cp.datetime_stats.max?.slice(0, 10)}
                              </div>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex flex-wrap gap-1">
                              {cp.top_values?.slice(0, 3).map((tv: any, i: number) => (
                                <span
                                  key={i}
                                  className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300 font-mono"
                                >
                                  {tv.value} ({tv.count})
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Tab: Schema & Diff */}
      {activeTab === 'schema' && (
        <div className="space-y-6">
          <div className="bg-[#111827] border border-slate-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-white text-base">Baseline Schema Comparison</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Detect breaking schema modifications, missing columns, and incompatible type mutations.
                </p>
              </div>
              <button
                onClick={handleSaveExpected}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition"
              >
                Set Current as Expected Schema
              </button>
            </div>

            {schemaDiff?.has_expected_schema ? (
              <div className="space-y-4">
                <div
                  className={`p-4 rounded-lg border ${
                    schemaDiff.diff.is_compatible
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                      : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
                  }`}
                >
                  <div className="font-semibold text-sm">
                    {schemaDiff.diff.is_compatible ? 'Compatible Schema' : 'Breaking Schema Changes Detected'}
                  </div>
                  <div className="text-xs mt-1">{schemaDiff.diff.summary}</div>
                </div>

                {schemaDiff.diff.breaking_changes?.length > 0 && (
                  <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/50">
                    <div className="text-xs font-semibold text-rose-400 uppercase mb-2">Breaking Violations:</div>
                    <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                      {schemaDiff.diff.breaking_changes.map((bc: string, i: number) => (
                        <li key={i}>{bc}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-8 text-center text-slate-500 text-sm">
                No expected baseline schema registered yet. Click &ldquo;Set Current as Expected Schema&rdquo; to track future drifts.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab: Validation Rules */}
      {activeTab === 'rules' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-white text-base">Validation Policies</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Rules enforced during automated CI/CD and interactive validation runs.
              </p>
            </div>
            <button
              onClick={() => setShowRuleModal(true)}
              className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition"
            >
              <Plus className="w-3.5 h-3.5" /> Add Rule
            </button>
          </div>

          <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/50">
                  <th className="py-3 px-6 font-semibold">Rule Name</th>
                  <th className="py-3 px-6 font-semibold">Rule Type</th>
                  <th className="py-3 px-6 font-semibold">Target Column</th>
                  <th className="py-3 px-6 font-semibold">Severity</th>
                  <th className="py-3 px-6 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30">
                    <td className="py-3.5 px-6 font-medium text-white">{r.name}</td>
                    <td className="py-3.5 px-6">
                      <span className="font-mono text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                        {r.rule_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 font-mono text-xs text-slate-300">
                      {r.target_columns.join(', ')}
                    </td>
                    <td className="py-3.5 px-6">
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
                    <td className="py-3.5 px-6 text-right">
                      <button
                        onClick={() => handleDeleteRule(r.id)}
                        className="text-slate-500 hover:text-rose-400 p-1 transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Validation History */}
      {activeTab === 'runs' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white text-base">Validation Execution Runs</h3>
            <button
              onClick={handleRunValidation}
              disabled={validating}
              className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              {validating ? 'Validating...' : 'Trigger New Run'}
            </button>
          </div>

          {runs.map((rn) => (
            <div key={rn.id} className="bg-[#111827] border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm text-slate-200 font-semibold">Run {rn.id.slice(0, 8)}</span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {rn.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Executed: {rn.created_at ? new Date(rn.created_at).toLocaleString() : 'Recent'} &bull; Duration:{' '}
                    {rn.duration_ms} ms
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Quality Score</div>
                    <div className="text-2xl font-bold text-cyan-400">{rn.quality_score}%</div>
                  </div>
                  <div className="flex gap-2">
                    <a
                      href={`/api/v1/validation-runs/${rn.id}/report?format=html`}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-medium transition flex items-center gap-1.5"
                    >
                      <Download className="w-3.5 h-3.5" /> HTML Report
                    </a>
                  </div>
                </div>
              </div>

              {/* Rules in this run */}
              {rn.rule_results && (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-slate-400 uppercase border-b border-slate-800/80">
                        <th className="pb-2 font-semibold">Status</th>
                        <th className="pb-2 font-semibold">Rule Name</th>
                        <th className="pb-2 font-semibold">Severity</th>
                        <th className="pb-2 font-semibold">Passed</th>
                        <th className="pb-2 font-semibold">Failed</th>
                        <th className="pb-2 font-semibold">Pass Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/40">
                      {rn.rule_results.map((rr: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-800/20">
                          <td className="py-2.5">
                            {rr.passed ? (
                              <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5" /> PASS
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-rose-400 font-medium">
                                <XCircle className="w-3.5 h-3.5" /> FAIL
                              </span>
                            )}
                          </td>
                          <td className="py-2.5 font-medium text-white">{rr.rule_name}</td>
                          <td className="py-2.5 font-mono text-[10px] text-amber-400">{rr.severity}</td>
                          <td className="py-2.5 font-mono text-emerald-400">{rr.passed_records}</td>
                          <td className="py-2.5 font-mono text-rose-400">{rr.failed_records}</td>
                          <td className="py-2.5 font-mono">{rr.pass_percentage}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal: Add Rule */}
      {showRuleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#111827] border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-4">Add Quality Rule</h3>
            <form onSubmit={handleCreateRule} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Rule Name *</label>
                <input
                  type="text"
                  required
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  placeholder="e.g. Email must have valid format"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Column *</label>
                <select
                  required
                  value={targetCol}
                  onChange={(e) => setTargetCol(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select column...</option>
                  {columnsList.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Rule Family *</label>
                <select
                  value={ruleType}
                  onChange={(e) => setRuleType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="not_null">Completeness: Not Null</option>
                  <option value="not_empty_string">Completeness: Not Empty String</option>
                  <option value="unique_column">Uniqueness: Unique Values</option>
                  <option value="email_format">Pattern: Valid Email Format</option>
                  <option value="min_value">Range: Minimum Value</option>
                  <option value="max_value">Range: Maximum Value</option>
                  <option value="value_between">Range: Value Between (min,max)</option>
                  <option value="in_set">Categorical: In Allowed Set (comma-separated)</option>
                  <option value="not_future_date">Date: Not In Future</option>
                  <option value="iqr_outlier_check">Statistical: IQR Outlier Check</option>
                  <option value="zscore_outlier_check">Statistical: Z-Score Outlier Check</option>
                </select>
              </div>

              {(ruleType === 'min_value' ||
                ruleType === 'max_value' ||
                ruleType === 'value_between' ||
                ruleType === 'in_set' ||
                ruleType === 'regex_match') && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Parameter Value</label>
                  <input
                    type="text"
                    value={paramVal}
                    onChange={(e) => setParamVal(e.target.value)}
                    placeholder={
                      ruleType === 'value_between'
                        ? '0, 100'
                        : ruleType === 'in_set'
                        ? 'USA, CAN, GBR'
                        : 'Threshold value'
                    }
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Severity *</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="CRITICAL">CRITICAL (Weight: 4.0)</option>
                  <option value="ERROR">ERROR (Weight: 3.0)</option>
                  <option value="WARNING">WARNING (Weight: 1.5)</option>
                  <option value="INFO">INFO (Weight: 0.5)</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowRuleModal(false)}
                  className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium"
                >
                  Create Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
