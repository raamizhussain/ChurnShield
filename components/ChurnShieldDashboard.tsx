'use client';

import React, { useState, useMemo } from 'react';
import {
  BarChart3,
  AlertTriangle,
  Zap,
  Users,
  ChevronRight,
  X,
  Check,
  Loader2,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';

interface CustomerRow {
  customer_id: string;
  login_velocity_drop: number;
  support_friction_score: number;
  days_inactive: number;
  priority_status: 'P0' | 'P1' | 'P2';
}

interface InferencePayload {
  customer_id: string;
  login_velocity_drop: number;
  click_velocity_drop: number;
  feature_velocity_drop: number;
  support_friction_score: number;
  click_to_login_ratio: number;
  days_since_last_activity: number;
}

interface InferenceResponse {
  status: string;
  customer_id: string;
  computed_metrics: {
    churn_probability_30d: number;
    causal_uplift_score: number;
    action_priority: string;
  };
}

const ChurnShieldDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roi' | 'watchlist' | 'inference'>('roi');
  const [retentionCost, setRetentionCost] = useState(150);
  const [averageClv, setAverageClv] = useState(2500);
  const [pageIndex, setPageIndex] = useState(0);
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);
  const [dispatchedCustomers, setDispatchedCustomers] = useState<Set<string>>(new Set());
  const [inferenceLoading, setInferenceLoading] = useState(false);
  const [inferenceResult, setInferenceResult] = useState<InferenceResponse | null>(null);
  const [inferenceForm, setInferenceForm] = useState<InferencePayload>({
    customer_id: 'CUST_12847',
    login_velocity_drop: -0.45,
    click_velocity_drop: -0.22,
    feature_velocity_drop: -0.10,
    support_friction_score: 3,
    click_to_login_ratio: 1.25,
    days_since_last_activity: 4,
  });

  const mockWatchlistData: CustomerRow[] = [
    { customer_id: 'CUST_00451', login_velocity_drop: -0.42, support_friction_score: 4.2, days_inactive: 12, priority_status: 'P0' },
    { customer_id: 'CUST_00892', login_velocity_drop: -0.38, support_friction_score: 3.8, days_inactive: 8, priority_status: 'P0' },
    { customer_id: 'CUST_01203', login_velocity_drop: -0.35, support_friction_score: 3.5, days_inactive: 6, priority_status: 'P0' },
    { customer_id: 'CUST_01754', login_velocity_drop: -0.32, support_friction_score: 3.2, days_inactive: 5, priority_status: 'P0' },
    { customer_id: 'CUST_02156', login_velocity_drop: -0.28, support_friction_score: 2.9, days_inactive: 3, priority_status: 'P1' },
    { customer_id: 'CUST_02489', login_velocity_drop: -0.25, support_friction_score: 2.6, days_inactive: 2, priority_status: 'P1' },
    { customer_id: 'CUST_02901', login_velocity_drop: -0.22, support_friction_score: 2.4, days_inactive: 1, priority_status: 'P1' },
    { customer_id: 'CUST_03214', login_velocity_drop: -0.18, support_friction_score: 2.1, days_inactive: 0, priority_status: 'P2' },
    { customer_id: 'CUST_03567', login_velocity_drop: -0.15, support_friction_score: 1.8, days_inactive: 0, priority_status: 'P2' },
    { customer_id: 'CUST_03890', login_velocity_drop: -0.12, support_friction_score: 1.5, days_inactive: 0, priority_status: 'P2' },
  ];

  const itemsPerPage = 5;
  const paginatedData = mockWatchlistData.slice(pageIndex * itemsPerPage, (pageIndex + 1) * itemsPerPage);
  const totalPages = Math.ceil(mockWatchlistData.length / itemsPerPage);

  const savedValue = useMemo(() => {
    const atrCount = mockWatchlistData.filter(c => c.priority_status === 'P0').length;
    return atrCount * (averageClv - retentionCost);
  }, [averageClv, retentionCost]);

  const totalRevenueAtRisk = mockWatchlistData.length * averageClv;
  const savingsRate = totalRevenueAtRisk > 0 ? (savedValue / totalRevenueAtRisk) * 100 : 0;

  const handleDispatchRetention = (customerId: string) => {
    setDispatchedCustomers(prev => new Set([...prev, customerId]));
  };

  const handleInferenceSubmit = async () => {
    setInferenceLoading(true);
    setInferenceResult(null);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const simulated_lift = (Math.abs(inferenceForm.login_velocity_drop) * 0.45) + (inferenceForm.support_friction_score * 0.05);
      const simulated_churn = Math.min(0.99, (inferenceForm.days_since_last_activity * 0.12) + Math.abs(inferenceForm.login_velocity_drop * 0.35));

      const response: InferenceResponse = {
        status: 'SUCCESS',
        customer_id: inferenceForm.customer_id,
        computed_metrics: {
          churn_probability_30d: Math.round(simulated_churn * 10000) / 10000,
          causal_uplift_score: Math.round(simulated_lift * 10000) / 10000,
          action_priority: simulated_lift > 0.15 ? 'HIGH' : 'STANDARD',
        },
      };

      setInferenceResult(response);
    } catch (error) {
      console.error('Inference failed:', error);
    } finally {
      setInferenceLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-surface-light bg-surface">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-8 h-8 text-accent-emerald" />
            <h1 className="text-4xl font-bold">ChurnShield</h1>
          </div>
          <p className="text-surface-light text-lg">Real-Time Causal Inference & Retention Intelligence</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex gap-2 mb-8 border-b border-surface-light">
          {[
            { id: 'roi', label: 'Executive ROI Hub', icon: BarChart3 },
            { id: 'watchlist', label: 'Critical Watchlist', icon: AlertTriangle },
            { id: 'inference', label: 'Causal Inference', icon: Zap },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => {
                setActiveTab(id as 'roi' | 'watchlist' | 'inference');
                setPageIndex(0);
                setExpandedRowId(null);
                setInferenceResult(null);
              }}
              className={`flex items-center gap-2 px-5 py-3 font-medium border-b-2 transition-all ${
                activeTab === id
                  ? 'border-accent-indigo text-accent-indigo'
                  : 'border-transparent text-surface-light hover:text-foreground'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {activeTab === 'roi' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard
                label="Total Revenue At Risk"
                value={`$${totalRevenueAtRisk.toLocaleString()}`}
                icon={TrendingDown}
                color="rose"
                subtext={`${mockWatchlistData.length} customers`}
              />
              <KPICard
                label="Saved Capital (Uplift)"
                value={`$${Math.round(savedValue).toLocaleString()}`}
                icon={TrendingUp}
                color="emerald"
                subtext={`${savingsRate.toFixed(1)}% savings rate`}
              />
              <KPICard
                label="Campaign Reach Efficiency"
                value={`${Math.round((dispatchedCustomers.size / mockWatchlistData.length) * 100)}%`}
                icon={Users}
                color="indigo"
                subtext={`${dispatchedCustomers.size} campaigns live`}
              />
              <KPICard
                label="Active Monitored Cohorts"
                value={mockWatchlistData.length.toString()}
                icon={BarChart3}
                color="emerald"
                subtext="Real-time tracking"
              />
            </div>

            <div className="bg-surface rounded-lg border border-surface-light p-8">
              <h2 className="text-2xl font-bold mb-8">Budget Configuration Module</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div>
                  <label className="block text-lg font-semibold mb-4">
                    Retention Promo Cost: <span className="text-accent-emerald">${retentionCost}</span>
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="500"
                    value={retentionCost}
                    onChange={(e) => setRetentionCost(parseInt(e.target.value))}
                    className="w-full h-2 bg-surface-light rounded-lg appearance-none cursor-pointer accent-accent-emerald"
                  />
                  <div className="flex justify-between text-surface-light text-sm mt-3">
                    <span>$50</span>
                    <span>$500</span>
                  </div>
                </div>

                <div>
                  <label className="block text-lg font-semibold mb-4">
                    Average User CLV: <span className="text-accent-indigo">${averageClv}</span>
                  </label>
                  <input
                    type="range"
                    min="1000"
                    max="10000"
                    step="100"
                    value={averageClv}
                    onChange={(e) => setAverageClv(parseInt(e.target.value))}
                    className="w-full h-2 bg-surface-light rounded-lg appearance-none cursor-pointer accent-accent-indigo"
                  />
                  <div className="flex justify-between text-surface-light text-sm mt-3">
                    <span>$1K</span>
                    <span>$10K</span>
                  </div>
                </div>
              </div>

              <div className="mt-12 p-6 bg-background rounded-lg border border-surface-light">
                <h3 className="text-lg font-semibold mb-4">ROI Projection Card</h3>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-surface-light text-sm mb-2">Estimated Margin</p>
                    <p className="text-2xl font-bold text-accent-emerald">
                      ${averageClv - retentionCost}
                    </p>
                  </div>
                  <div>
                    <p className="text-surface-light text-sm mb-2">Max Portfolio Impact</p>
                    <p className="text-2xl font-bold text-accent-rose">
                      ${Math.round((averageClv - retentionCost) * mockWatchlistData.length).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'watchlist' && (
          <div className="space-y-6">
            <div className="bg-surface rounded-lg border border-surface-light overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-surface-light">
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Customer ID</th>
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Login Velocity</th>
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Support Friction</th>
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Days Inactive</th>
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Priority</th>
                      <th className="px-6 py-4 text-left font-semibold text-surface-light">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedData.map((row) => (
                      <React.Fragment key={row.customer_id}>
                        <tr
                          onClick={() =>
                            expandedRowId === row.customer_id ? setExpandedRowId(null) : setExpandedRowId(row.customer_id)
                          }
                          className="border-b border-surface-light hover:bg-background cursor-pointer transition-colors"
                        >
                          <td className="px-6 py-4 font-mono text-foreground">{row.customer_id}</td>
                          <td
                            className={`px-6 py-4 font-semibold ${
                              row.login_velocity_drop <= -0.3 ? 'text-accent-rose' : 'text-surface-light'
                            }`}
                          >
                            {row.login_velocity_drop.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 text-surface-light">{row.support_friction_score.toFixed(1)}</td>
                          <td className="px-6 py-4 text-surface-light">{row.days_inactive}d</td>
                          <td className="px-6 py-4">
                            <span
                              className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                                row.priority_status === 'P0'
                                  ? 'bg-accent-rose/20 text-accent-rose'
                                  : row.priority_status === 'P1'
                                    ? 'bg-accent-indigo/20 text-accent-indigo'
                                    : 'bg-surface-light/20 text-surface-light'
                              }`}
                            >
                              {row.priority_status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            {dispatchedCustomers.has(row.customer_id) ? (
                              <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-emerald/20 text-accent-emerald font-semibold cursor-default">
                                <Check className="w-4 h-4" />
                                Dispatched
                              </button>
                            ) : (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDispatchRetention(row.customer_id);
                                }}
                                className="px-4 py-2 rounded-lg bg-accent-indigo hover:bg-accent-indigo/90 text-white font-semibold transition-colors"
                              >
                                Trigger Playbook
                              </button>
                            )}
                          </td>
                        </tr>
                        {expandedRowId === row.customer_id && (
                          <tr className="border-b border-surface-light bg-background">
                            <td colSpan={6} className="px-6 py-6">
                              <CustomerDetailsPanel customer={row} />
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex items-center justify-between px-6 py-4 border-t border-surface-light bg-background">
                <p className="text-surface-light text-sm">
                  Showing {pageIndex * itemsPerPage + 1} to {Math.min((pageIndex + 1) * itemsPerPage, mockWatchlistData.length)} of{' '}
                  {mockWatchlistData.length}
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setPageIndex(Math.max(0, pageIndex - 1))}
                    disabled={pageIndex === 0}
                    className="px-4 py-2 rounded-lg border border-surface-light hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <div className="flex items-center gap-2">
                    {Array.from({ length: totalPages }).map((_, i) => (
                      <button
                        key={i}
                        onClick={() => setPageIndex(i)}
                        className={`w-8 h-8 rounded-lg font-semibold transition-colors ${
                          pageIndex === i ? 'bg-accent-indigo text-white' : 'border border-surface-light hover:bg-surface'
                        }`}
                      >
                        {i + 1}
                      </button>
                    ))}
                  </div>
                  <button
                    onClick={() => setPageIndex(Math.min(totalPages - 1, pageIndex + 1))}
                    disabled={pageIndex === totalPages - 1}
                    className="px-4 py-2 rounded-lg border border-surface-light hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inference' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-surface rounded-lg border border-surface-light p-8">
              <h2 className="text-2xl font-bold mb-8">Causal Inference Sandbox</h2>
              <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handleInferenceSubmit(); }}>
                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">Customer ID</label>
                  <input
                    type="text"
                    value={inferenceForm.customer_id}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, customer_id: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg bg-background border border-surface-light text-foreground placeholder-surface-light focus:outline-none focus:border-accent-indigo"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Login Velocity Drop: <span className="text-accent-rose">{inferenceForm.login_velocity_drop.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="-1"
                    max="0"
                    step="0.01"
                    value={inferenceForm.login_velocity_drop}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, login_velocity_drop: parseFloat(e.target.value) })}
                    className="w-full h-2 bg-surface-light rounded-lg appearance-none cursor-pointer accent-accent-rose"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Click Velocity Drop: <span className="text-accent-rose">{inferenceForm.click_velocity_drop.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="-1"
                    max="0"
                    step="0.01"
                    value={inferenceForm.click_velocity_drop}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, click_velocity_drop: parseFloat(e.target.value) })}
                    className="w-full h-2 bg-surface-light rounded-lg appearance-none cursor-pointer accent-accent-rose"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Feature Velocity Drop: <span className="text-accent-rose">{inferenceForm.feature_velocity_drop.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="-1"
                    max="0"
                    step="0.01"
                    value={inferenceForm.feature_velocity_drop}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, feature_velocity_drop: parseFloat(e.target.value) })}
                    className="w-full h-2 bg-surface-light rounded-lg appearance-none cursor-pointer accent-accent-rose"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Support Friction Score: <span className="text-accent-indigo">{inferenceForm.support_friction_score.toFixed(1)}</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    value={inferenceForm.support_friction_score}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, support_friction_score: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 rounded-lg bg-background border border-surface-light text-foreground focus:outline-none focus:border-accent-indigo"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Click-to-Login Ratio: <span className="text-accent-indigo">{inferenceForm.click_to_login_ratio.toFixed(2)}</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.01"
                    value={inferenceForm.click_to_login_ratio}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, click_to_login_ratio: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 rounded-lg bg-background border border-surface-light text-foreground focus:outline-none focus:border-accent-indigo"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-foreground">
                    Days Since Last Activity: <span className="text-accent-indigo">{inferenceForm.days_since_last_activity.toFixed(0)}</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="365"
                    step="1"
                    value={inferenceForm.days_since_last_activity}
                    onChange={(e) => setInferenceForm({ ...inferenceForm, days_since_last_activity: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 rounded-lg bg-background border border-surface-light text-foreground focus:outline-none focus:border-accent-indigo"
                  />
                </div>

                <button
                  type="submit"
                  disabled={inferenceLoading}
                  className="w-full py-3 px-4 rounded-lg bg-accent-indigo hover:bg-accent-indigo/90 disabled:opacity-50 text-white font-bold transition-colors flex items-center justify-center gap-2"
                >
                  {inferenceLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  Execute Causal Inference
                </button>
              </form>
            </div>

            <div className="bg-surface rounded-lg border border-surface-light p-8">
              <h2 className="text-2xl font-bold mb-8">Inference Response</h2>
              {inferenceLoading && (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-12 h-12 text-accent-indigo animate-spin mb-4" />
                  <p className="text-surface-light">Computing causal uplift metrics...</p>
                </div>
              )}
              {!inferenceLoading && inferenceResult && (
                <div className="bg-background rounded-lg p-6 space-y-6">
                  <div className="border-b border-surface-light pb-4">
                    <p className="text-surface-light text-sm mb-1">Status</p>
                    <p className="text-xl font-bold text-accent-emerald">{inferenceResult.status}</p>
                  </div>
                  <div className="border-b border-surface-light pb-4">
                    <p className="text-surface-light text-sm mb-1">Customer ID</p>
                    <p className="text-xl font-mono font-bold">{inferenceResult.customer_id}</p>
                  </div>
                  <div className="space-y-4">
                    <p className="text-surface-light text-sm font-semibold">Computed Metrics</p>
                    <div className="grid grid-cols-1 gap-4">
                      <div className="bg-surface rounded-lg p-4 border border-surface-light">
                        <p className="text-surface-light text-sm mb-2">30-Day Churn Probability</p>
                        <p className="text-2xl font-bold text-accent-rose">
                          {(inferenceResult.computed_metrics.churn_probability_30d * 100).toFixed(2)}%
                        </p>
                      </div>
                      <div className="bg-surface rounded-lg p-4 border border-surface-light">
                        <p className="text-surface-light text-sm mb-2">Causal Uplift Score</p>
                        <p className="text-2xl font-bold text-accent-emerald">
                          {inferenceResult.computed_metrics.causal_uplift_score.toFixed(4)}
                        </p>
                      </div>
                      <div className="bg-surface rounded-lg p-4 border border-surface-light">
                        <p className="text-surface-light text-sm mb-2">Action Priority</p>
                        <p
                          className={`text-lg font-bold ${
                            inferenceResult.computed_metrics.action_priority === 'HIGH'
                              ? 'text-accent-rose'
                              : 'text-accent-emerald'
                          }`}
                        >
                          {inferenceResult.computed_metrics.action_priority}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {!inferenceLoading && !inferenceResult && (
                <div className="flex flex-col items-center justify-center py-12 text-surface-light">
                  <p>Submit the form to execute inference</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface KPICardProps {
  label: string;
  value: string;
  icon: React.ComponentType<{ className: string }>;
  color: 'emerald' | 'rose' | 'indigo';
  subtext?: string;
}

const KPICard: React.FC<KPICardProps> = ({ label, value, icon: Icon, color, subtext }) => {
  const colorClass = {
    emerald: 'text-accent-emerald bg-accent-emerald/10 border-accent-emerald/30',
    rose: 'text-accent-rose bg-accent-rose/10 border-accent-rose/30',
    indigo: 'text-accent-indigo bg-accent-indigo/10 border-accent-indigo/30',
  }[color];

  return (
    <div className={`rounded-lg border p-6 ${colorClass}`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-surface-light text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {subtext && <p className="text-sm mt-2 text-surface-light">{subtext}</p>}
        </div>
        <Icon className="w-6 h-6" />
      </div>
    </div>
  );
};

interface CustomerDetailsPanelProps {
  customer: CustomerRow;
}

const CustomerDetailsPanel: React.FC<CustomerDetailsPanelProps> = ({ customer }) => {
  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold mb-6">Customer Feature Breakdown: {customer.customer_id}</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">LOGIN_VELOCITY_DROP</p>
          <p className={`text-lg font-bold ${customer.login_velocity_drop <= -0.3 ? 'text-accent-rose' : 'text-accent-emerald'}`}>
            {customer.login_velocity_drop.toFixed(3)}
          </p>
        </div>
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">SUPPORT_FRICTION</p>
          <p className="text-lg font-bold text-accent-indigo">{customer.support_friction_score.toFixed(2)}</p>
        </div>
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">DAYS_INACTIVE</p>
          <p className="text-lg font-bold text-foreground">{customer.days_inactive}d</p>
        </div>
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">ESTIMATED_CLV_AT_RISK</p>
          <p className="text-lg font-bold text-accent-rose">$2,500</p>
        </div>
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">RECOMMENDED_ACTION</p>
          <p className="text-lg font-bold text-accent-emerald">PREMIUM_OFFER</p>
        </div>
        <div className="bg-surface rounded-lg p-4 border border-surface-light">
          <p className="text-surface-light text-xs mb-2">CRM_ROUTING</p>
          <p className="text-lg font-bold text-accent-indigo">P0_QUEUE</p>
        </div>
      </div>
    </div>
  );
};

export default ChurnShieldDashboard;
