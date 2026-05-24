// static/js/chat_ui.jsx
const { useState, useEffect, useRef } = React;

function QuickPill({ text, onClick }) {
  return (
    <button className="quick-pill" onClick={() => onClick(text)}>{text}</button>
  );
}

function Message({ m, onRate }) {
  return (
    <div className={`msg ${m.role === 'user' ? 'user' : (m.role === 'assistant' ? 'assistant' : 'system')}`}>
      <div className="msg-text">{m.text}</div>
      {m.role === 'assistant' && (
        <div className="msg-meta">
          <button className="rate" title="Helpful" onClick={() => onRate(m.id, 'up')}>👍</button>
          <button className="rate" title="Not helpful" onClick={() => onRate(m.id, 'down')}>👎</button>
        </div>
      )}
    </div>
  );
}

function ChatUI({ apiUrl = "/api/ask" }) {
  const [messages, setMessages] = useState([
    { id: "sys-1", role: "system", text: "Hello! I'm CampusBuddy — ask me anything about your college." },
  ]);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [quickReplies, setQuickReplies] = useState([
    "Placement stats",
    "Hostel availability",
    "College timings",
  ]);
  const listRef = useRef(null);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  function addMessage(role, txt) {
    setMessages(m => [...m, { id: Date.now() + Math.random(), role, text: txt }]);
  }

  async function sendMessage(e, manualText) {
    if (e) e.preventDefault();
    const trimmed = (manualText ?? text).trim();
    if (!trimmed) return;
    addMessage("user", trimmed);
    setText("");
    setSending(true);
    try {
      const payload = { message: trimmed };
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        addMessage("assistant", "Server error: " + res.status);
        setSending(false);
        return;
      }
      const data = await res.json();
      const reply = data.reply ?? "(no reply)";
      addMessage("assistant", reply);
    } catch (err) {
      console.error(err);
      addMessage("assistant", "Network error: couldn't reach the server.");
    } finally {
      setSending(false);
    }
  }

  function handleQuick(t) {
    sendMessage(null, t);
  }

  function handleRate(id, kind) {
    // demo: append a system message. Replace with API call to record rating if you want.
    addMessage("system", `Recorded "${kind}" for message ${id}.`);
  }

  async function handleUpload(ev) {
    const f = ev.target.files && ev.target.files[0];
    if (!f) return;
    addMessage("user", `Uploaded: ${f.name}`);
    const form = new FormData();
    form.append("file", f);
    try {
      const r = await fetch("/api/chat/upload", { method: "POST", body: form });
      const j = await r.json();
      addMessage("assistant", j.message ?? "File uploaded.");
    } catch {
      addMessage("assistant", "Upload failed.");
    }
  }

  return (
    <div className="container">
      <aside className="sidebar">
        <div className="conversations-header">
          <div className="title">Conversations</div>
          <div className="demo">Demo</div>
        </div>

        <div className="conversations">
          <button className="btn" onClick={() => setMessages([{ id: "sys-1", role: "system", text: "New conversation started." }])}>+ New conversation</button>
          <button className="btn" onClick={() => { if (confirm("Clear all messages?")) setMessages([{ id: "sys-1", role: "system", text: "New conversation started." }]); }}>Clear chat</button>
        </div>

        <div className="tip">Tip: Enter to send • Shift+Enter for newline</div>
      </aside>

      <main className="main" role="main">
        <div className="header">
          <div className="header-left">
            <img className="avatar" src="/static/img/bot.png" alt="Bot avatar" onError={(e)=>{e.target.onerror=null; e.target.src='https://i.pravatar.cc/120?img=32'}} />
            <div>
              <div className="h-title">Campus Buddy</div>
              <div className="tagline">We typically reply in a few minutes.</div>
            </div>
          </div>

          <div className="header-actions">
            <label htmlFor="file-upload" className="icon-btn" title="Upload file">📤</label>
            <input id="file-upload" type="file" style={{display:'none'}} onChange={handleUpload} />
            <button className="icon-btn" title="Copy log" onClick={() => navigator.clipboard && navigator.clipboard.writeText(JSON.stringify(messages, null, 2))}>📋</button>
          </div>
        </div>

        <div className="quick-row" aria-hidden={false}>
          {quickReplies.map((q,i) => <QuickPill key={i} text={q} onClick={handleQuick} />)}
        </div>

        <div ref={listRef} className="messages" aria-live="polite">
          {messages.map(m => <Message key={m.id} m={m} onRate={handleRate} />)}
        </div>

        <form onSubmit={sendMessage} className="composer" aria-label="Send message">
          <div className="input-row">
            <div className="input-wrap">
              <textarea
                className="input"
                placeholder="Type your message..."
                value={text}
                onChange={e => setText(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              />
              <div className="composer-actions">
                <label htmlFor="file-upload-small" className="small-icon" title="Attach">📎</label>
                <input id="file-upload-small" type="file" style={{display:'none'}} onChange={handleUpload} />
                <button type="button" className="small-icon" title="Emoji" onClick={() => { const s = "🙂"; setText(t => t + (t ? " " : "") + s); }}>😊</button>
              </div>
            </div>

            <button type="submit" className="send-btn" disabled={sending}>{sending ? "Sending..." : "➤"}</button>
          </div>
        </form>

        <div className="footer">Powered by your Flask backend • Page: /chat</div>
      </main>
    </div>
  );
}

const el = document.getElementById("root");
ReactDOM.createRoot(el).render(<ChatUI apiUrl="/api/ask" />);
