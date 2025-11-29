import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ArticleNew from './pages/ArticleNew'
import ArticleDetail from './pages/ArticleDetail'
import KeywordSelection from './pages/KeywordSelection'
import KeywordAnalysis from './pages/KeywordAnalysis'
import KeywordDataAnalysis from './pages/KeywordDataAnalysis'
import Settings from './pages/Settings'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'

const queryClient = new QueryClient()

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/articles/new"
            element={
              <PrivateRoute>
                <Layout>
                  <ArticleNew />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/articles/:id"
            element={
              <PrivateRoute>
                <Layout>
                  <ArticleDetail />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/articles/:id/keywords"
            element={
              <PrivateRoute>
                <Layout>
                  <KeywordSelection />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/keyword-analysis"
            element={
              <PrivateRoute>
                <Layout>
                  <KeywordAnalysis />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/keyword-data-analysis"
            element={
              <PrivateRoute>
                <Layout>
                  <KeywordDataAnalysis />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Layout>
                  <Settings />
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App

