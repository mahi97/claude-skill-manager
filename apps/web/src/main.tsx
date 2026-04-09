import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { GraphPage } from './pages/GraphPage'
import { ProposalsPage } from './pages/ProposalsPage'
import { SourcesPage } from './pages/SourcesPage'
import { InstalledPage } from './pages/InstalledPage'
import { ItemDetail } from './pages/ItemDetail'
import { SnapshotsPage } from './pages/SnapshotsPage'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/proposals" element={<ProposalsPage />} />
            <Route path="/sources" element={<SourcesPage />} />
            <Route path="/installed" element={<InstalledPage />} />
            <Route path="/items/:itemId" element={<ItemDetail />} />
            <Route path="/snapshots" element={<SnapshotsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
