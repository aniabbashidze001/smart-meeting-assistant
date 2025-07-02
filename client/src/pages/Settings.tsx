import Layout from "../components/Layout";
import { useState, useEffect } from "react";

function Settings() {
  const [language, setLanguage] = useState("English");
  const [detailedSummary, setDetailedSummary] = useState(true);
  const [speakerLabels, setSpeakerLabels] = useState(true);
  const [theme, setTheme] = useState("Futuristic");

  // Georgian translation feature states
  const [georgianFiles, setGeorgianFiles] = useState([]);
  const [translating, setTranslating] = useState(false);
  const [translationStatus, setTranslationStatus] = useState("");

  // Fetch Georgian transcript files on component mount
  useEffect(() => {
    fetchGeorgianFiles();
  }, []);

  const fetchGeorgianFiles = async () => {
    try {
      const response = await fetch("http://localhost:5050/api/georgian-files");
      if (response.ok) {
        const files = await response.json();
        setGeorgianFiles(files);
      }
    } catch (error) {
      console.error("Failed to fetch Georgian files:", error);
    }
  };

  const handleTranslateGeorgian = async () => {
    if (georgianFiles.length === 0) {
      setTranslationStatus("No Georgian files found to translate.");
      return;
    }

    setTranslating(true);
    setTranslationStatus("Starting translation process...");

    try {
      const response = await fetch("http://localhost:5050/api/translate-georgian", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const result = await response.json();
        setTranslationStatus(result.message || "Translation completed successfully!");
        // Refresh the Georgian files list
        fetchGeorgianFiles();
      } else {
        const error = await response.json();
        setTranslationStatus(`Translation failed:`);
      }
    } catch (error) {
      setTranslationStatus(`Translation error:`);
    } finally {
      setTranslating(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-xl shadow animate-fade-in">
        <h2 className="text-3xl font-extrabold text-gradient mb-6">
          ⚙️ Settings
        </h2>

        {/* 🌐 Language Selector */}
        <div className="mb-6">
          <label className="block text-gray-700 font-semibold mb-2">
            🌐 Transcription Language
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full p-2 border rounded focus:outline-none focus:ring focus:border-blue-400 text-black"
          >
            <option>English</option>
            <option>Georgian</option>
          </select>
        </div>

        {/* 🧠 Summary Detail Toggle */}
        <div className="mb-6">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={detailedSummary}
              onChange={() => setDetailedSummary(!detailedSummary)}
              className="h-5 w-5 text-blue-600"
            />
            <span className="text-gray-800">
              🧠 Enable Detailed Summaries
            </span>
          </label>
        </div>

        {/* 🗣️ Speaker Labels */}
        <div className="mb-6">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={speakerLabels}
              onChange={() => setSpeakerLabels(!speakerLabels)}
              className="h-5 w-5 text-purple-600"
            />
            <span className="text-gray-800">
              🗣️ Show Speaker Labels in Transcript
            </span>
          </label>
        </div>

        {/* 🎨 Theme Selector (Static) */}
        <div className="mb-6">
          <label className="block text-gray-700 font-semibold mb-2">
            🎨 Theme Mode
          </label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="w-full p-2 border rounded focus:outline-none focus:ring focus:border-purple-400 text-black"
          >
            <option>Dark</option>
            <option>Light</option>
          </select>
        </div>

        {/* 🌍 Georgian Translation Section */}
        <div className="mb-6 p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            🌍 Georgian Translation Manager
          </h3>

          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              Found {georgianFiles.length} Georgian transcript(s) ready for translation
            </p>

            {georgianFiles.length > 0 && (
              <div className="mb-3">
                <h4 className="font-semibold text-gray-700 mb-2">Georgian Files:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {georgianFiles.map((file, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-orange-400 rounded-full"></span>
                      <span>{file}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <button
            onClick={handleTranslateGeorgian}
            disabled={translating || georgianFiles.length === 0}
            className={`px-4 py-2 rounded font-semibold transition-all duration-200 ${
              translating || georgianFiles.length === 0
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transform hover:scale-105"
            }`}
          >
            {translating ? "🔄 Translating..." : "🌍 Translate Georgian Files"}
          </button>

          {translationStatus && (
            <div className={`mt-3 p-3 rounded ${
              translationStatus.includes("successfully") || translationStatus.includes("completed")
                ? "bg-green-100 text-green-800"
                : translationStatus.includes("failed") || translationStatus.includes("error")
                ? "bg-red-100 text-red-800"
                : "bg-blue-100 text-blue-800"
            }`}>
              {translationStatus}
            </div>
          )}
        </div>

      </div>
    </Layout>
  );
}

export default Settings;