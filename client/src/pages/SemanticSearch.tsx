import { useState } from "react";
import Layout from "../components/Layout";

function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const res = await fetch("http://localhost:5050/api/semantic-search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch semantic search results");
      }

      const data = await res.json();
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      console.error("❌ Error:", err);
      setAnswer("❌ Sorry, something went wrong. Please try again.");
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-lg animate-fade-in">
        <h2 className="text-3xl font-bold mb-4 text-gray-900 flex items-center gap-2">
          🔎 <span className="text-gradient">Semantic Search</span>
        </h2>
        <p className="text-gray-600 mb-6">
          Ask any question about your meetings. Our AI assistant will scan transcripts and provide the most relevant answers.
        </p>

        <div className="flex items-center gap-2 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What did the team decide about Q3 marketing?"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow shadow-sm text-black"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className={`${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-700 hover:bg-blue-800"
            } text-white px-5 py-2 rounded-lg shadow transition`}
          >
            {loading ? "⏳ Thinking..." : "🚀 Ask"}
          </button>
        </div>

        {answer && (
          <div className="bg-[#0f172a] text-white p-5 rounded-lg shadow-md mb-4 border border-blue-500 animate-fade-in">
            <p className="text-blue-300 font-semibold mb-2">🤖 AI Answer</p>
            <p className="text-lg leading-relaxed whitespace-pre-wrap">{answer}</p>
          </div>
        )}

        {sources.length > 0 && (
          <div className="bg-gray-100 p-4 rounded-md border border-gray-200 shadow-sm">
            <p className="font-semibold text-gray-700 mb-2">📂 Top Sources:</p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              {sources.map((src, i) => (
                <li key={i} className="hover:underline cursor-pointer">
                  {src}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default SemanticSearch;
