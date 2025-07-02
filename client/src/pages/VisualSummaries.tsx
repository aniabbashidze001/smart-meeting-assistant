import { useState } from "react";
import Layout from "../components/Layout";

interface Visual {
  title: string;
  description: string;
  image: string;
}

function VisualSummaries() {
  const [visuals, setVisuals] = useState<Visual[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:5050/api/visual-summary", {
        method: "POST",
      });

      const data = await res.json();

      if (!data.visuals) {
        setError("❌ No visuals generated.");
        return;
      }

      const generatedVisuals: Visual[] = Object.values(data.visuals).map(
        (item: any) => ({
          title: item.title,
          description: item.description,
          image: item.url,
        })
      );

      setVisuals((prev) => [...prev, ...generatedVisuals]);
    } catch (err) {
      console.error("❌ Error generating visuals:", err);
      setError("⚠️ Failed to generate visuals. Check your backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 py-8 text-white">
        {/* 🔮 Header */}
        <h1 className="text-4xl font-extrabold text-gradient animate-shimmer mb-10">
          AI-Generated Visual Summaries
        </h1>

        {/* 📥 Generate Button */}
        <div className="mb-10">
          <button
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg transition"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "🎨 Generating..." : "🎨 Generate New Visuals"}
          </button>
          {error && <p className="mt-3 text-red-400">{error}</p>}
        </div>

        {/* 🖼️ Visual Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {visuals.map((visual, idx) => (
            <div
              key={idx}
              className="bg-white text-gray-800 rounded-xl overflow-hidden shadow-lg transform transition duration-300 hover:scale-105 hover:-translate-y-1"
            >
              <img
                src={visual.image}
                alt={visual.title}
                className="w-full h-48 object-cover transition-transform duration-300"
              />
              <div className="p-4">
                <h3 className="text-lg font-bold mb-1">{visual.title}</h3>
                <p className="text-sm text-gray-600">{visual.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default VisualSummaries;
