import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { Overview } from './pages/Overview';
import { Projects } from './pages/Projects';
import { Datasets } from './pages/Datasets';
import { DatasetDetail } from './pages/DatasetDetail';
import { Profiling } from './pages/Profiling';
import { ValidationRules } from './pages/ValidationRules';
import { ValidationRuns } from './pages/ValidationRuns';
import { SchemaRegistry } from './pages/SchemaRegistry';
import { Reports } from './pages/Reports';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#0b0f19] text-slate-100">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />
          <main className="flex-1 pb-16">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/datasets" element={<Datasets />} />
              <Route path="/datasets/:id" element={<DatasetDetail />} />
              <Route path="/profiling" element={<Profiling />} />
              <Route path="/rules" element={<ValidationRules />} />
              <Route path="/runs" element={<ValidationRuns />} />
              <Route path="/runs/:id" element={<ValidationRuns />} />
              <Route path="/schema" element={<SchemaRegistry />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
