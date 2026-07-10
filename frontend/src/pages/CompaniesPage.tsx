import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { useCatalog } from '../api/hooks';
import { Card, Spinner } from '../components/ui';

const COMPANY_ICONS: Record<string, string> = {
  Google: '🔍', Meta: '👥', Amazon: '📦', Microsoft: '🪟', Apple: '🍎', Netflix: '🎬',
  Nvidia: '🟩', Tesla: '⚡', Stripe: '💳', Airbnb: '🏠', LinkedIn: '💼', 'X (Twitter)': '🐦',
  Snap: '👻', Pinterest: '📌', Spotify: '🎵', Shopify: '🛍️', 'Block (Square)': '⬛',
  PayPal: '💸', Salesforce: '☁️', Adobe: '🎨', Atlassian: '🧩', ServiceNow: '⚙️',
  Workday: '📅', SAP: '🏭', Oracle: '🗄️', IBM: '🖥️', Intel: '🔲', Qualcomm: '📶',
  Cisco: '🌐', VMware: '🗃️', 'Red Hat': '🎩', Zoom: '📹', Dropbox: '📁', Cloudflare: '🛡️',
  Twilio: '📨', Datadog: '🐶', Palantir: '🔮', Databricks: '🧱', Snowflake: '❄️',
  'Goldman Sachs': '🏦', 'JP Morgan': '💰', 'Morgan Stanley': '📈', Bloomberg: '📟',
  Citadel: '🏰', 'Two Sigma': '∑', 'Jane Street': '🃏', 'DE Shaw': '📐',
  'American Express': '💳', Visa: '🌍', Mastercard: '🟠', Uber: '🚗', Lyft: '🚕',
  DoorDash: '🚪', Instacart: '🥕', Coinbase: '🪙', Robinhood: '🏹', Flipkart: '🛒',
  Swiggy: '🍔', Zomato: '🍕', Paytm: '📱', PhonePe: '💜', Razorpay: '⚡', CRED: '💎',
  Zerodha: '📊', Ola: '🚙', Freshworks: '🌱', TCS: '🏢', Infosys: '🏢', Wipro: '🏢',
  HCLTech: '🏢', Accenture: '🏢', Cognizant: '🏢', Capgemini: '🏢',
  'Service-Based': '🏢', Startup: '🚀', 'Airtel/Telecom': '📡',
};

export default function CompaniesPage() {
  const { data: catalog, isLoading } = useCatalog();
  const [search, setSearch] = useState('');

  const filtered = useMemo(
    () =>
      (catalog?.companies ?? []).filter(
        (c) => !search || c.name.toLowerCase().includes(search.toLowerCase())
      ),
    [catalog, search]
  );

  if (isLoading) return <div className="py-20"><Spinner label="Loading companies…" /></div>;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Company-Specific Interviews</h1>
          <p className="text-sm text-slate-500">
            {catalog?.companies.length ?? 0} companies — each tunes the interviewer's style, question
            bank, focus areas and difficulty to match the real thing.
          </p>
        </div>
        <input
          className="input !w-64"
          placeholder="Search companies…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((company) => (
          <Link key={company.name} to="/app/interview" state={{ company: company.name }}>
            <Card className="h-full transition hover:border-brand-500/60">
              <div className="text-3xl">{COMPANY_ICONS[company.name] ?? '🏢'}</div>
              <div className="mt-2 font-bold">{company.name}</div>
              <p className="mt-1 text-sm text-slate-500">{company.blurb}</p>
              <div className="mt-3 text-xs font-semibold text-brand-500">Practice this style →</div>
            </Card>
          </Link>
        ))}
        {!filtered.length && (
          <p className="col-span-full py-10 text-center text-sm text-slate-500">
            No companies match “{search}”.
          </p>
        )}
      </div>
    </div>
  );
}
