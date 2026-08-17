import Link from "next/link";

export default function Home() {
  return (
    <>
      {/* ── Header ── */}
      <header className="border-b border-paper-border bg-paper/80 backdrop-blur supports-[backdrop-filter]:bg-paper/60 sticky top-0 z-50">
        <div className="container">
          <nav className="flex items-center justify-between h-14">
            <div className="flex items-center gap-6">
              <Link href="/" className="font-bold text-xl text-ink">
                LiteMind CLI
              </Link>
              <div className="hidden sm:flex gap-6">
                <Link href="#features" className="text-sm text-ink-weak hover:text-ink transition-colors">Features</Link>
                <Link href="#install" className="text-sm text-ink-weak hover:text-ink transition-colors">Install</Link>
                <Link href="https://github.com/debabratamishra/litemind-cli#keyboard-shortcuts" className="text-sm text-ink-weak hover:text-ink transition-colors">Shortcuts</Link>
                <Link href="https://github.com/debabratamishra/litemind-ui/blob/main/docs/api-contract.md" className="text-sm text-ink-weak hover:text-ink transition-colors">API Docs</Link>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3">
                <img
                  src="https://img.shields.io/pypi/v/litemind-cli?color=22c55e&label=PyPI&labelColor=0a0a0e&style=flat"
                  alt="PyPI version"
                  className="h-6 w-auto"
                  width={60}
                  height={20}
                />
              </div>
              <div className="w-px h-5 bg-paper-border"></div>
              <a
                href="https://github.com/debabratamishra/litemind-cli"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-ink-weak hover:text-ink transition-colors"
                aria-label="GitHub"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd"
                    d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75 0 3.45 1.31 6.36 3.407 8.044.1.08.135-.182.135-.403V14.71c-.51.18-.62-.43-.62-.868 0-.305-.01-1.11-.02-1.95-.02-.414-.01-1.03-.05-1.45a3.491 3.491 0 01-.17-.445c-.3-.08-.62-.11-.94-.11-.47 0-.83.32-.83.72 0 .204.09.416.14.576a1.73 1.73 0 002.18 1.516c.07.253.1.515.1 1.028v4.057c-.34.83-.52 1.75-.52 3.537 0 2.452.875 4.386 2.185 5.02.17.05.22-.13.22-.29v-1.81c-.87.19-1.77.29-2.67.29-2.18 0-3.94-1.75-3.94-3.91 0-.87.31-1.58.82-2.15a4.96 4.96 0 01-.22-2.06c0-.45.16-.81.43-1.11a4.938 4.938 0 001.38-1.22c0-.31.08-.63.12-.87a2.871 2.871 0 01-.34-.98 4.816 4.816 0 010-1.22c.16-.55.47-1.04.9-1.41.32-.28.7-.51 1.13-.65-.14-.35-.23-.73-.23-1.12 0-.22.01-.44.04-.66a4.321 4.321 0 012.32-2.32c.27-.11.57-.17.88-.17 1.07 0 2.02.42 2.78 1.13l.01-.01c.3-.3.67-.55 1.08-.68.16-.05.33-.08.5-.1 1.11-.3 2.33.06 3.4.92.46.34.85.8 1.13 1.32.03.06.06.12.09.18l.01.02c1.7-.52 3.5-.82 5.37-.82 2.18 0 4.19.74 5.68 1.97 1.17 1.01 2.15 2.35 2.73 3.87.05.15.1.29.14.44.02.14.04.29.06.44.26-.08.54-.11.82-.11 2.18 0 3.94 1.75 3.94 3.91 0 .87-.31 1.58-.82 2.15.03.22.05.45.07.67.02.22.03.44.03.66 0 2.18-1.75 3.94-3.91 3.94-2.18 0-3.94-1.75-3.94-3.94 0-2.18 1.75-3.94 3.94-3.94h.01"
                    clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </nav>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="container section">
        <div className="hero-grid items-center">
          {/* Hero text */}
          <div className="space-y-6">
            <h1 className="text-4xl sm:text-5xl font-bold text-ink leading-tight">
              AI in your terminal.
            </h1>
            <p className="text-xl text-ink-weak max-w-md">
              Chat with local and cloud AI models. Query your own documents with RAG.
              All from the terminal.
            </p>
            <div className="flex flex-wrap hero-ctas pt-2">
              <a
                href="https://pypi.org/project/litemind-cli/"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12 0C5.3 0 0 5.3 0 12s5.3 12 12 12 12-5.3 12-12S18.7 0 12 0zm0 22c-5.5 0-10-4.5-10-10S6.5 2 12 2s10 4.5 10 10-4.5 10-10 10z" />
                </svg>
                Install from PyPI
              </a>
              <a
                href="https://github.com/debabratamishra/litemind-cli"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
              >
                View on GitHub
              </a>
            </div>
          </div>

          {/* Hero terminal window */}
          <div className="terminal-wrapper">
            <div className="terminal-window">
              <div className="terminal-titlebar">
                <span className="terminal-dot red"></span>
                <span className="terminal-dot amber"></span>
                <span className="terminal-dot green"></span>
                <span className="ml-2">user@litemind ~ $</span>
              </div>
              <div className="terminal-content font-mono">
                <div className="terminal-line" style={{ animationDelay: "0ms" }}>
                  <span className="terminal-prompt">$</span> <span className="terminal-output">litemind-cli</span>
                </div>
                <div className="terminal-line terminal-dim" style={{ animationDelay: "400ms" }}>&nbsp;</div>
                <div className="terminal-line" style={{ animationDelay: "600ms" }}>
                  {`  _     _ _       __  __ _           _    ____ _     ___ `}
                </div>
                <div className="terminal-line" style={{ animationDelay: "750ms" }}>
                  {` | |   (_) |_ ___|  \\/  (_)_ __   __| |  / ___| |   |_ _|`}
                </div>
                <div className="terminal-line" style={{ animationDelay: "900ms" }}>
                  {` | |   | | __/ _ \\ |\\/| | | '_ \\ / _\` | | |   | |    | | `}
                </div>
                <div className="terminal-line" style={{ animationDelay: "1050ms" }}>
                  {` | |___| | ||  __/ |  | | | | | | | (_| | | |___| |___ | | `}
                </div>
                <div className="terminal-line" style={{ animationDelay: "1200ms" }}>
                  {` |_____|_|\\__\\___|_|  |_|_|_|_|\\__,_|  \\____|_____|___|`}
                </div>
                <div className="terminal-line terminal-dim" style={{ animationDelay: "1400ms" }}>&nbsp;</div>
                <div className="terminal-line terminal-dim" style={{ animationDelay: "1500ms" }}>
                  {`         Terminal interface for LiteMindUI  ·  Chat · RAG`}
                </div>
                <div className="terminal-line terminal-dim" style={{ animationDelay: "1700ms" }}>&nbsp;</div>
                <div className="terminal-line" style={{ animationDelay: "1900ms" }}>
                  <span className="terminal-prompt">$</span> litemind-cli status
                </div>
                <div className="terminal-line terminal-success" style={{ animationDelay: "2100ms" }}>
                  <span className="terminal-success">✓</span> Backend: Healthy at localhost:8000
                </div>
                <div className="terminal-line terminal-success" style={{ animationDelay: "2300ms" }}>
                  <span className="terminal-success">✓</span> Models: openai/gpt-5.6-luna-pro, ~anthropic/claude-fable-latest, deepseek/deepseek-v4-pro-0813
                </div>
                <div className="terminal-line terminal-dim" style={{ animationDelay: "2500ms" }}>&nbsp;</div>
                <div className="terminal-line" style={{ animationDelay: "2700ms" }}>
                  <span className="terminal-prompt">$</span> Ready. Type a message or press Q to quit.
                  <span className="terminal-cursor"></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="section-alt">
        <div className="container">
          <h2 className="text-3xl font-bold text-center text-ink mb-3">Features</h2>

          <div className="features-stack">
            {/* Chat */}
            <div className="feature-card">
              <div className="w-10 h-10 rounded-lg bg-stdout/10 flex items-center justify-center mb-4">
              </div>
              <h3 className="text-lg font-semibold text-ink mb-2">Streaming Chat</h3>
              <p className="text-sm text-ink-weak mb-3">
                Full conversation history with real-time streaming. Works with Ollama, OpenRouter, and NVIDIA NIM.
              </p>
              <pre className="code-block text-xs max-w-full overflow-x-auto">
<span className="terminal-prompt">$</span> <span className="terminal-output">litemind-cli</span>
<span className="terminal-dim">{'>'} What is RAG?</span>

<span className="terminal-output">RAG retrieves docs before answering,
so you always see your latest data.
No retraining needed.</span></pre>
            </div>

            {/* RAG */}
            <div className="feature-card">
              <div className="w-10 h-10 rounded-lg bg-stdout/10 flex items-center justify-center mb-4">
              </div>
              <h3 className="text-lg font-semibold text-ink mb-2">Document RAG</h3>
              <p className="text-sm text-ink-weak mb-3">
                Upload PDFs, Word docs, spreadsheets. Query with natural language.
              </p>
              <pre className="code-block text-xs max-w-full overflow-x-auto">
                <span className="terminal-prompt">$</span> <span className="terminal-output">litemind-cli rag</span>
                <span className="terminal-dim"> Query: Security risks?</span>

                <span className="terminal-output">[From 12 uploaded docs]</span>
                <span className="terminal-success">•</span> Injection attacks — top risk
                <span className="terminal-success">•</span> Access control needs review</pre>
            </div>

            {/* Multi-Provider */}
            <div className="feature-card">
              <div className="w-10 h-10 rounded-lg bg-stdout/10 flex items-center justify-center mb-4">
              </div>
              <h3 className="text-lg font-semibold text-ink mb-2">Multi-Provider</h3>
              <p className="text-sm text-ink-weak mb-3">
                Switch between Ollama, OpenRouter, and NIM inline. No restart.
              </p>
              <pre className="code-block text-xs max-w-full overflow-x-auto">
<span className="terminal-dim">Providers:</span> <span className="terminal-success">[Ollama]</span> OpenRouter  NIM
<span className="terminal-dim">Models: </span> <span className="terminal-output"> openai/gpt-5.6-luna-pro | ~anthropic/claude-fable-latest | deepseek/deepseek-v4-pro-0813</span>
<span className="terminal-dim">Switch with Ctrl+1/2/3</span></pre>
            </div>
          </div>
        </div>
      </section>

      {/* ── Installation ── */}
      <section id="install" className="container section">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-ink mb-3">Quick Start</h2>
          <p className="text-center text-ink-weak max-w-2xl mx-auto mb-10">
            Get up and running in under a minute.
          </p>

          <div className="terminal-window">
            <div className="terminal-titlebar">
              <span className="terminal-dot red"></span>
              <span className="terminal-dot amber"></span>
              <span className="terminal-dot green"></span>
              <span className="ml-2">user@litemind ~ $</span>
            </div>
            <div className="terminal-content font-mono text-sm">
              <div className="mb-2">
                <span className="terminal-prompt">$</span> <span className="terminal-output">pip install litemind-cli</span>
              </div>
              <div className="terminal-dim mb-3"># Start the backend (Docker)</div>
              <div className="mb-2">
                <span className="terminal-prompt">$</span> <span className="terminal-output">curl -fsSL https://raw.githubusercontent.com/debabratamishra/litemind-ui/main/install.sh | bash</span>
              </div>
              <div className="terminal-dim mb-3"># Launch the TUI</div>
              <div className="mb-2">
                <span className="terminal-prompt">$</span> <span className="terminal-output">litemind-cli</span>
              </div>
              <div className="terminal-dim mb-3"># Check connectivity</div>
              <div>
                <span className="terminal-prompt">$</span> <span className="terminal-output">litemind-cli status</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="section-alt">
        <div className="container">
          <h2 className="text-3xl font-bold text-center text-ink mb-3">How It Works</h2>
          <p className="text-center text-ink-weak max-w-2xl mx-auto mb-12">
            LiteMind CLI is a terminal frontend for the LiteMindUI backend. It streams
            responses over SSE and supports RAG with multiple document formats.
          </p>
          <div className="grid-3 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="step-number mx-auto mb-3">01</div>
              <h3 className="font-semibold text-ink mb-2">Start Backend</h3>
              <p className="text-sm text-ink-weak">
                Run the LiteMindUI backend via Docker or from source. It serves the REST API at localhost:8000.
              </p>
            </div>
            <div className="text-center">
              <div className="step-number mx-auto mb-3">02</div>
              <h3 className="font-semibold text-ink mb-2">Install CLI</h3>
              <p className="text-sm text-ink-weak">
                Install from <a href="https://pypi.org/project/litemind-cli/" className="text-stdout hover:opacity-80">PyPI</a> or build
                from source. The TUI launches with <span className="code-inline">litemind-cli</span>.
              </p>
            </div>
            <div className="text-center">
              <div className="step-number mx-auto mb-3">03</div>
              <h3 className="font-semibold text-ink mb-2">Chat & Query</h3>
              <p className="text-sm text-ink-weak">
                Chat with AI models, upload documents for RAG, and switch providers
                inline - all without leaving your terminal.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Related Projects ── */}
      <section className="container section">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-ink mb-3">Part of the LiteMind ecosystem</h2>
          <p className="text-ink-weak mb-8">
            LiteMind CLI is the terminal frontend for the <a href="https://github.com/debabratamishra/litemind-ui" className="text-stdout hover:opacity-80">LiteMindUI </a>
            backend - a fullstack AI platform with REST API, Web UI, and Docker deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://github.com/debabratamishra/litemind-ui"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-ghost"
            >
              View LiteMindUI Backend
            </a>

          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-paper-border bg-paper">
        <div className="container py-8">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">

            <div className="flex gap-6 text-sm text-ink-weak">
              <a href="https://github.com/debabratamishra/litemind-cli" target="_blank" rel="noopener noreferrer">GitHub </a>
              <span className="text-ink-weak"> | </span>
              <a href="https://pypi.org/project/litemind-cli/" target="_blank" rel="noopener noreferrer">PyPI</a>
              <span className="text-ink-weak"> | </span>
              <a href="https://github.com/debabratamishra/litemind-ui" target="_blank" rel="noopener noreferrer">Backend</a>
            </div>
          </div>
          <div className="mt-6 text-xs text-ink-weaker">
            &copy; 2026 LiteMind CLI. Built with <a href="https://textual.textualize.io/" target="_blank" rel="noopener noreferrer" className="text-ink-weak hover:text-ink">Textual</a>.
          </div>
        </div>
      </footer>
    </>
  );
}
