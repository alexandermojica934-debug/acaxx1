import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Store, FileText, BookOpen, Globe2, Sparkles, Loader2, Download, Copy, Link2, CreditCard, CheckCircle2, X, Trash2,
  ShoppingCart, KeyRound, AlertTriangle, Package, ExternalLink
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const ICON = { rfp_kit: FileText, prompt_library: BookOpen, seo_pack: Globe2 };
const fmt = (iso) => { try { return iso ? new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; } catch { return ""; } };
const money = (v) => `$${Number(v || 0).toLocaleString()}`;

export default function Apex() {
  const [catalog, setCatalog] = useState(null);
  const [product, setProduct] = useState("rfp_kit");
  const [inputs, setInputs] = useState({});
  const [opps, setOpps] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [deliverables, setDeliverables] = useState([]);
  const [current, setCurrent] = useState(null);
  const [orders, setOrders] = useState([]);
  const [orderForm, setOrderForm] = useState({ buyer_email: "", buyer_name: "", price_usd: "" });

  const load = useCallback(async () => {
    try {
      const [c, d, o] = await Promise.all([axios.get(`${API}/apex/products`), axios.get(`${API}/apex/deliverables`), axios.get(`${API}/apex/orders`)]);
      setCatalog(c.data); setDeliverables(d.data); setOrders(o.data);
    } catch { toast.error("Could not load Apex Nexus"); }
  }, []);
  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (product === "rfp_kit") axios.get(`${API}/radar/opportunities`, { params: { limit: 40 } }).then((r) => setOpps(r.data)).catch(() => {});
  }, [product]);

  const p = catalog?.products.find((x) => x.id === product);
  const set = (k, v) => setInputs((i) => ({ ...i, [k]: v }));

  const generate = async () => {
    setGenerating(true); setCurrent(null);
    try {
      const r = await axios.post(`${API}/apex/generate`, { product, inputs }, { timeout: 300000 });
      setCurrent(r.data); toast.success(`${r.data.title} ready - ${r.data.placeholders} [FILL] placeholder(s) to complete`); load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Generation failed"); }
    finally { setGenerating(false); }
  };
  const openDeliverable = async (id) => { try { setCurrent((await axios.get(`${API}/apex/deliverables/${id}`)).data); window.scrollTo({ top: 0, behavior: "smooth" }); } catch { /* ignore */ } };
  const removeDeliverable = async (id) => { try { await axios.delete(`${API}/apex/deliverables/${id}`); if (current?.id === id) setCurrent(null); load(); } catch { toast.error("Delete failed"); } };
  const copy = async (t) => { try { await navigator.clipboard.writeText(t); toast.success("Copied"); } catch { toast.error("Copy failed"); } };

  const createOrder = async () => {
    if (!current) { toast.error("Generate or open a deliverable first"); return; }
    try {
      const r = await axios.post(`${API}/apex/orders`, { product: current.product, deliverable_id: current.id, buyer_email: orderForm.buyer_email, buyer_name: orderForm.buyer_name || null, price_usd: orderForm.price_usd ? Number(orderForm.price_usd) : null });
      toast.success(`Order created for ${r.data.buyer_email} - ${r.data.payment_provider === "stripe" ? "checkout link ready" : "mark paid when payment arrives"}`);
      setOrderForm({ buyer_email: "", buyer_name: "", price_usd: "" }); load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Order failed"); }
  };
  const patchOrder = async (id, body) => { try { await axios.patch(`${API}/apex/orders/${id}`, body); load(); } catch (e) { toast.error(e?.response?.data?.detail || "Update failed"); } };
  const unlockLink = (o) => `${API}/apex/unlock/${o.unlock_token}`;

  return (
    <div className="ax-wrap" data-testid="apex-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Store size={18} /> Apex Nexus</div>
          <p>Zero-capital digital products generated on demand and sold with an <b>order → pay → unlock</b> flow. Three vectors are live: the <b>RFP Response Kit</b> (built on real Radar solicitations), the <b>Prompt Library</b> (Markdown + JSON + a gated API key), and the <b>Local SEO Content Pack</b>. Everything is a first draft with <code>[FILL]</code> placeholders where facts are missing - you review, complete and deliver; nothing is submitted or sent automatically.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{deliverables.length}</span><span className="l">deliverables</span></div>
          <div className="chr-stat gold"><span className="v">{money(orders.filter((o) => o.status === "paid").reduce((a, o) => a + (o.price_usd || 0), 0))}</span><span className="l">paid orders</span></div>
        </div>
      </div>

      {catalog && (
        <div className={`ax-pay ${catalog.payments.stripe_configured ? "on" : ""}`} data-testid="apex-payments">
          <CreditCard size={14} /> <b>Payments: {catalog.payments.stripe_configured ? "Stripe Checkout" : "manual unlock"}</b> - {catalog.payments.note}
        </div>
      )}

      {/* Product picker */}
      <div className="ax-products" data-testid="apex-products">
        {(catalog?.products || []).map((x) => { const I = ICON[x.id] || Package; return (
          <button key={x.id} className={`ax-product ${product === x.id ? "active" : ""}`} onClick={() => { setProduct(x.id); setInputs({}); }} data-testid={`apex-product-${x.id}`}>
            <div className="ax-product-top"><I size={16} /> <b>{x.name}</b> <span className="ax-price">{money(x.price_usd)}</span></div>
            <small>{x.tagline}</small>
            <small className="ax-buyer">Buyer: {x.buyer} · vector #{x.vector} · {x.deliverables} made · {x.paid_orders} paid</small>
          </button>); })}
      </div>

      {/* Workbench */}
      {p && (
        <div className="fa-console" data-testid="apex-workbench">
          <div className="fa-head"><Sparkles size={16} /> {p.name} workbench <em>{p.deliverable}</em></div>
          <div className="rd-grid3 ax-form">
            {product === "rfp_kit" && <>
              <label className="rd-span3">Radar opportunity (real RFP/grant) — or paste text below
                <select className="cw-input" data-testid="ax-opp" value={inputs.opportunity_id || ""} onChange={(e) => set("opportunity_id", e.target.value || undefined)}>
                  <option value="">— pick from Radar ({opps.length} loaded) —</option>
                  {opps.map((o) => <option key={o.id} value={o.id}>{o.title.slice(0, 90)} · {o.organization_name || "?"} · {o.score?.total}</option>)}
                </select>
              </label>
              <label className="rd-span3">Or paste the RFP / solicitation text<textarea className="cw-textarea" rows={4} data-testid="ax-rfp-text" value={inputs.rfp_text || ""} onChange={(e) => set("rfp_text", e.target.value)} placeholder="Scope of work, requirements, evaluation criteria, deadline..." /></label>
              <label>Bidder name<input className="cw-input" value={inputs.bidder_name || ""} onChange={(e) => set("bidder_name", e.target.value)} placeholder="from Radar profile if blank" /></label>
              <label>Capabilities (facts only)<input className="cw-input" value={inputs.bidder_capabilities || ""} onChange={(e) => set("bidder_capabilities", e.target.value)} /></label>
              <label>Differentiators<input className="cw-input" value={inputs.differentiators || ""} onChange={(e) => set("differentiators", e.target.value)} /></label>
              <label>Price basis<input className="cw-input" value={inputs.price_basis || ""} onChange={(e) => set("price_basis", e.target.value)} placeholder="e.g. $95/hr, fixed $12k, monthly $349" /></label>
            </>}
            {product === "prompt_library" && <>
              <label>Domain *<input className="cw-input" data-testid="ax-domain" value={inputs.domain || ""} onChange={(e) => set("domain", e.target.value)} placeholder="e.g. moving company operations" /></label>
              <label>Audience<input className="cw-input" value={inputs.audience || ""} onChange={(e) => set("audience", e.target.value)} /></label>
              <label>Count (10-30)<input type="number" className="cw-input" value={inputs.count || 15} onChange={(e) => set("count", Number(e.target.value))} /></label>
              <label className="rd-span3">Use cases to cover<input className="cw-input" value={inputs.use_cases || ""} onChange={(e) => set("use_cases", e.target.value)} placeholder="comma-separated" /></label>
              <label>Tone<input className="cw-input" value={inputs.tone || ""} onChange={(e) => set("tone", e.target.value)} placeholder="professional" /></label>
            </>}
            {product === "seo_pack" && <>
              <label>Business *<input className="cw-input" data-testid="ax-business" value={inputs.business || ""} onChange={(e) => set("business", e.target.value)} /></label>
              <label>Service *<input className="cw-input" data-testid="ax-service" value={inputs.service || ""} onChange={(e) => set("service", e.target.value)} placeholder="e.g. office relocation" /></label>
              <label>City / region *<input className="cw-input" data-testid="ax-region" value={inputs.city_region || ""} onChange={(e) => set("city_region", e.target.value)} placeholder="Boston, MA" /></label>
              <label>Pages (5-15)<input type="number" className="cw-input" value={inputs.count || 8} onChange={(e) => set("count", Number(e.target.value))} /></label>
              <label className="rd-span3">Terms (optional - blank lets ACASO propose high-intent terms)<input className="cw-input" value={inputs.terms || ""} onChange={(e) => set("terms", e.target.value)} placeholder="comma-separated" /></label>
              <label className="rd-span3">Proof points (facts only)<input className="cw-input" value={inputs.proof_points || ""} onChange={(e) => set("proof_points", e.target.value)} placeholder="e.g. 'insured, 2 trucks, same-day quotes' - missing facts become [FILL]" /></label>
            </>}
          </div>
          <div className="cw-row">
            <button className="rd-btn primary" data-testid="ax-generate" onClick={generate} disabled={generating}>{generating ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {generating ? "Generating (30-90s)..." : `Generate ${p.name}`}</button>
            <span className="rd-dim">One model call. Output is a draft with [FILL] placeholders - never sold or sent without your review.</span>
          </div>
        </div>
      )}

      {/* Current deliverable */}
      <AnimatePresence>
        {current && (
          <motion.div className="ax-deliverable" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} data-testid="ax-deliverable">
            <div className="ax-del-head">
              <div>
                <div className="fa-head"><Package size={16} /> {current.title}</div>
                <div className="cw-meta">{fmt(current.created_at)} · {current.model_label} · {current.chars} chars · <b className={current.placeholders ? "rd-urgent" : ""}>{current.placeholders} [FILL]</b>{current.count ? ` · ${current.count} items` : ""}{current.source_url ? <> · <a href={current.source_url} target="_blank" rel="noreferrer">source <ExternalLink size={10} /></a></> : null}</div>
              </div>
              <div className="cw-actions">
                <a className="rd-btn" href={`${API}/apex/deliverables/${current.id}/export?fmt=md`} target="_blank" rel="noreferrer" data-testid="ax-export-md"><Download size={13} /> .md</a>
                {current.data && <a className="rd-btn" href={`${API}/apex/deliverables/${current.id}/export?fmt=json`} target="_blank" rel="noreferrer" data-testid="ax-export-json"><Download size={13} /> .json</a>}
                <button className="rd-btn" onClick={() => copy(current.markdown)}><Copy size={13} /> Copy</button>
                {current.api_key && <button className="rd-btn" onClick={() => copy(`${API}/apex/library/${current.id}?key=${current.api_key}`)} title="Gated API endpoint - works after a paid order" data-testid="ax-api-key"><KeyRound size={13} /> API link</button>}
                <button className="rd-ic" onClick={() => setCurrent(null)}><X size={14} /></button>
              </div>
            </div>
            <div className="ax-del-grid">
              <div className="ax-md"><Markdown text={current.markdown} /></div>
              <aside className="ax-sell">
                <div className="cw-side-title"><ShoppingCart size={14} /> Sell this deliverable</div>
                <input className="cw-input" placeholder="buyer email *" data-testid="ax-buyer-email" value={orderForm.buyer_email} onChange={(e) => setOrderForm({ ...orderForm, buyer_email: e.target.value })} />
                <input className="cw-input" placeholder="buyer name" value={orderForm.buyer_name} onChange={(e) => setOrderForm({ ...orderForm, buyer_name: e.target.value })} />
                <input className="cw-input" type="number" placeholder={`price (default ${money(p?.price_usd)})`} value={orderForm.price_usd} onChange={(e) => setOrderForm({ ...orderForm, price_usd: e.target.value })} />
                <button className="rd-btn primary" onClick={createOrder} data-testid="ax-create-order"><ShoppingCart size={14} /> Create order</button>
                <div className="rd-lbl-note">{catalog?.payments.stripe_configured ? "A Stripe Checkout link is attached to the order." : "Manual mode: send the buyer your payment link, then press Mark paid - the unlock link starts working immediately."}</div>
                <div className="ax-warn"><AlertTriangle size={12} /> Complete every [FILL] before delivering. Drafts carry no guarantee of award, ranking or results.</div>
              </aside>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Orders */}
      <div className="fa-console">
        <div className="fa-head"><CreditCard size={16} /> Orders <em>{orders.length} total · {orders.filter((o) => o.status === "paid").length} paid</em></div>
        {orders.length === 0 ? <div className="attach-empty" data-testid="ax-orders-empty">No orders yet. Generate a deliverable, then create an order for a buyer.</div> : (
          <div className="ax-orders" data-testid="ax-orders">
            {orders.map((o) => (
              <div key={o.id} className={`ax-order s-${o.status}`} data-testid={`ax-order-${o.id}`}>
                <span className={`bb-tag`}>{o.product}</span>
                <span className="ax-order-buyer">{o.buyer_email}{o.buyer_name ? ` · ${o.buyer_name}` : ""}</span>
                <span className="ax-order-price">{money(o.price_usd)}</span>
                <span className={`ln-status s-${o.status === "paid" ? "done" : o.status === "pending_payment" ? "proposed" : "failed"}`}>{o.status.replace("_", " ")}</span>
                <span className="ln-when">{fmt(o.created_at)}{o.downloads ? ` · ${o.downloads} download(s)` : ""}</span>
                <button className="rd-ic" title="Copy buyer unlock link" onClick={() => copy(unlockLink(o))} data-testid="ax-copy-unlock"><Link2 size={13} /></button>
                {o.status === "pending_payment" && <button className="rd-btn sm primary" onClick={() => patchOrder(o.id, { status: "paid" })} data-testid="ax-mark-paid"><CheckCircle2 size={13} /> Mark paid</button>}
                {o.status === "pending_payment" && <button className="rd-ic" title="Cancel" onClick={() => patchOrder(o.id, { status: "cancelled" })}><X size={13} /></button>}
                {o.status === "paid" && <button className="rd-btn sm" onClick={() => patchOrder(o.id, { status: "refunded" })}>Refund</button>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Deliverable library */}
      <div className="fa-console">
        <div className="fa-head"><Package size={16} /> Deliverables <em>{deliverables.length}</em></div>
        {deliverables.length === 0 ? <div className="attach-empty" data-testid="ax-deliverables-empty">Nothing generated yet.</div> : (
          <div className="cw-history" data-testid="ax-deliverables">
            {deliverables.map((d) => (
              <div key={d.id} className="cw-hrow">
                <button className="cw-hmain" onClick={() => openDeliverable(d.id)} data-testid={`ax-del-${d.id}`}>
                  <span className="bb-tag">{d.product}</span>
                  <span className="cw-htitle">{d.title}</span>
                  <span className="cw-hmeta">{fmt(d.created_at)} · {d.placeholders} [FILL]{d.count ? ` · ${d.count} items` : ""}</span>
                </button>
                <a className="attach-btn" href={`${API}/apex/deliverables/${d.id}/export?fmt=md`} target="_blank" rel="noreferrer" title="Download"><Download size={13} /></a>
                <button className="attach-btn danger" onClick={() => removeDeliverable(d.id)} title="Delete"><Trash2 size={13} /></button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
