export default function Home() {
  return (
    <div className="max-w-2xl w-full space-y-8 text-center">
      <div className="glass p-12 space-y-6 animate-float">
        <h1 className="text-6xl font-bold tracking-tight bg-gradient-to-r from-primary via-white to-secondary bg-clip-text text-transparent">
          Aura Stock
        </h1>
        <p className="text-xl text-text-muted font-light leading-relaxed">
          The future of Mexican retail investing, built on trust and high-performance technology.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <button className="px-8 py-3 rounded-full bg-primary text-bg-dark font-bold hover:scale-105 transition-transform">
            Start Trading
          </button>
          <button className="px-8 py-3 rounded-full border border-glass-border hover:bg-white/5 transition-colors">
            Learn More
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Security", val: "Level 4" },
          { label: "Fees", val: "0.01%" },
          { label: "Uptime", val: "99.9%" }
        ].map((item, i) => (
          <div key={i} className="glass p-4">
            <p className="text-xs text-text-muted uppercase tracking-widest">{item.label}</p>
            <p className="text-lg font-bold">{item.val}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
