import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Database, Upload, Trash2, ArrowRight, FileText, CheckCircle2 } from 'lucide-react';
import { fetchDatasets, fetchProjects, uploadDataset, deleteDataset } from '../api';

export const Datasets: React.FC = () => {
  const [searchParams] = useSearchParams();
  const projectIdParam = searchParams.get('project_id');

  const [datasets, setDatasets] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(projectIdParam || '');
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    Promise.all([fetchDatasets(projectIdParam || undefined), fetchProjects()])
      .then(([ds, projs]) => {
        setDatasets(ds);
        setProjects(projs);
        if (!selectedProject && projs.length > 0) {
          setSelectedProject(projs[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [projectIdParam]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedProject) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDataset(file, selectedProject, name || file.name, description);
      setFile(null);
      setName('');
      setDescription('');
      setShowModal(false);
      load();
    } catch (err: any) {
      setError(err.message || 'Failed to upload dataset');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete dataset '${name}'?`)) return;
    try {
      await deleteDataset(id);
      load();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Datasets Catalog</h2>
          <p className="text-sm text-slate-400 mt-1">
            Browse, inspect, and ingest CSV, JSON, JSONL, and Parquet data collections.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-blue-500/20"
        >
          <Upload className="w-4 h-4" />
          Ingest Dataset
        </button>
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-slate-800/40 rounded-xl"></div>
          ))}
        </div>
      ) : datasets.length === 0 ? (
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-12 text-center">
          <Database className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white">No datasets found</h3>
          <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
            Upload a structured file (CSV, JSON, JSONL, or Parquet) to profile distributions and validate data quality.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium"
          >
            <Upload className="w-4 h-4" /> Ingest Dataset
          </button>
        </div>
      ) : (
        <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/50">
                <th className="py-3.5 px-6 font-semibold">Dataset Name</th>
                <th className="py-3.5 px-6 font-semibold">Format</th>
                <th className="py-3.5 px-6 font-semibold">Dimensions</th>
                <th className="py-3.5 px-6 font-semibold">File Size</th>
                <th className="py-3.5 px-6 font-semibold">Status</th>
                <th className="py-3.5 px-6 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {datasets.map((d) => (
                <tr key={d.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-4 px-6">
                    <Link
                      to={`/datasets/${d.id}`}
                      className="font-medium text-slate-200 hover:text-blue-400 transition flex items-center gap-2.5"
                    >
                      <FileText className="w-4 h-4 text-blue-400" />
                      <span>{d.name}</span>
                    </Link>
                    {d.description && (
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{d.description}</p>
                    )}
                  </td>
                  <td className="py-4 px-6">
                    <span className="uppercase text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">
                      {d.file_format}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-300">
                    <span className="font-semibold">{d.row_count || 0}</span> rows &bull;{' '}
                    <span className="font-semibold">{d.column_count || 0}</span> cols
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                    {(d.file_size_bytes / 1024).toFixed(1)} KB
                  </td>
                  <td className="py-4 px-6">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" /> {d.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end gap-3">
                      <Link
                        to={`/datasets/${d.id}`}
                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
                      >
                        Inspect <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        onClick={() => handleDelete(d.id, d.name)}
                        className="text-slate-500 hover:text-rose-400 p-1 transition"
                        title="Delete dataset"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#111827] border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-4">Ingest Structured Dataset</h3>
            {error && (
              <div className="p-3 mb-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {error}
              </div>
            )}
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Project *</label>
                <select
                  required
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Dataset File *</label>
                <input
                  type="file"
                  required
                  accept=".csv,.tsv,.json,.jsonl,.parquet"
                  onChange={(e) => {
                    const f = e.target.files?.[0] || null;
                    setFile(f);
                    if (f && !name) setName(f.name.replace(/\.[^/.]+$/, ''));
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Supported formats: CSV, TSV, JSON, JSON Lines (.jsonl), Parquet
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Dataset Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Customers Master Q3"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional details regarding dataset origin or semantics..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-slate-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !file}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
                >
                  {uploading ? 'Processing File...' : 'Upload & Ingest'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
