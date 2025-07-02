import { useEffect, useState } from "react";
import Layout from "../components/Layout";

function MeetingSummary() {
  const [summary, setSummary] = useState("");
  const [actionItems, setActionItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const filename = localStorage.getItem("transcriptFilename");
    if (!filename) {
      setSummary("❌ No file selected. Please upload and transcribe a meeting first.");
      setLoading(false);
      return;
    }

    const fetchSummary = async () => {
      console.log("🧠 Fetching summary for:", filename);
      try {
        const res = await fetch(`http://localhost:5050/api/summary?filename=${encodeURIComponent(filename)}`);
        const data = await res.json();
        if (res.ok && data.summary) {
          setSummary(data.summary);
          if (Array.isArray(data.action_items)) {
            setActionItems(data.action_items);
          }
        } else {
          setSummary("⚠️ Failed to load summary.");
        }
      } catch (err) {
        setSummary("🚨 Error loading summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6 sm:p-10 rounded-2xl shadow-xl bg-gradient-to-br from-white via-gray-50 to-gray-100 border border-gray-200 animate-fade-in">
        <h2 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 text-transparent bg-clip-text mb-10 tracking-tight text-center">
           Meeting Summary
        </h2>

        {loading ? (
          <p className="text-gray-500 text-lg text-center">⏳ Generating summary...</p>
        ) : (
          <>
            <section className="mb-10">
              <h3 className="text-2xl font-bold text-purple-600 flex items-center gap-2 mb-4">
                📝 Summary
              </h3>
              <div className="bg-white p-6 rounded-lg border-l-4 border-purple-400 shadow-md text-gray-800 leading-relaxed whitespace-pre-wrap transition hover:shadow-lg">
                {summary}
              </div>
            </section>

            {actionItems.length > 0 && (
              <section>
                <h3 className="text-2xl font-bold text-blue-600 flex items-center gap-2 mb-4">
                  ✅ Action Items
                </h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  {actionItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-white border border-blue-200 rounded-xl shadow hover:shadow-blue-300 transition-all duration-200 hover:scale-[1.02]"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-blue-500 text-xl">📌</span>
                        <span className="text-gray-700">{item}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </Layout>
  );
}

export default MeetingSummary;
