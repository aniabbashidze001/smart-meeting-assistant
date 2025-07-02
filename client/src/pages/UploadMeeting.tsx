import { useState, useEffect } from "react";
import Layout from "../components/Layout";

function UploadMeeting() {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [transcript, setTranscript] = useState<{ speaker: string; text: string }[]>([]);
  const [filename, setFilename] = useState<string | null>(null);

  // ✅ Clear previously stored transcript filename on fresh page load
  useEffect(() => {
    localStorage.removeItem("transcriptFilename");
  }, []);

  useEffect(() => {
    if (!isTranscribing) return;

    let fakeProgress = 0;
    const interval = setInterval(() => {
      fakeProgress += Math.random() * 5;
      setProgress((prev) => Math.min(prev + fakeProgress, 95));
    }, 400);

    return () => clearInterval(interval);
  }, [isTranscribing]);

  const colors = [
    "text-blue-600",
    "text-green-600",
    "text-purple-600",
    "text-pink-600",
    "text-yellow-600",
    "text-red-600",
    "text-indigo-600",
    "text-teal-600",
    "text-orange-600",
    "text-rose-600",
  ];

  const speakerColorMap: { [speaker: string]: string } = {};
  let colorIndex = 0;
  transcript.forEach((entry) => {
    if (!speakerColorMap[entry.speaker]) {
      speakerColorMap[entry.speaker] = colors[colorIndex % colors.length];
      colorIndex++;
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setProgress(0);
      setShowTranscript(false);
      setFilename(null); // reset filename
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setProgress(0);
      setShowTranscript(false);
      setFilename(null); // reset filename
    }
  };

  const handleTranscribe = async () => {
    if (!file) return;

    setIsTranscribing(true);
    setProgress(0);
    setShowTranscript(false);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5050/api/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok && Array.isArray(data.transcript)) {
        setTranscript(data.transcript);
        setFilename(data.filename);
        localStorage.setItem("transcriptFilename", data.filename); // 💾 Store filename for summary
        setShowTranscript(true);
        console.log("✅ Saved filename:", data.filename);
      } else {
        console.error("Transcription failed:", data.error);
        alert("Transcription failed: " + data.error);
      }
    } catch (error) {
      console.error("Error uploading:", error);
      alert("Error uploading file");
    } finally {
      setIsTranscribing(false);
      setProgress(100);
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto bg-white p-6 rounded-xl shadow-lg mt-6 animate-fade-in">
        <h2 className="text-3xl font-extrabold text-blue-600 mb-2 flex items-center gap-2">
          🎙️ <span>Upload Meeting Audio</span>
        </h2>
        <p className="text-gray-600 mb-6">
          Supported formats: <span className="font-medium text-gray-800">.mp3, .wav, .m4a</span>
        </p>

        <label
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-blue-400 w-full h-40 rounded-xl flex items-center justify-center text-blue-500 hover:border-blue-600 hover:bg-blue-50 transition cursor-pointer text-sm font-medium mb-4"
        >
          {file ? (
            <span>✅ {file.name}</span>
          ) : (
            <span>📂 Drag & drop your file here or click to browse</span>
          )}
          <input
            type="file"
            accept=".mp3,.wav,.m4a"
            className="hidden"
            onChange={handleFileChange}
          />
        </label>

        {file && !isTranscribing && (
          <button
            onClick={handleTranscribe}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:opacity-90 transition shadow-md"
          >
            Transcribe
          </button>
        )}

        {isTranscribing && (
          <div className="mt-6">
            <p className="text-sm text-gray-700 mb-1">
              Transcribing... <span className="font-medium">{progress.toFixed(0)}%</span>
            </p>
            <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {showTranscript && (
          <div className="mt-6 bg-gray-50 p-5 rounded-xl border border-gray-200">
            <h3 className="text-lg font-semibold text-blue-600 mb-4">📝 Transcript</h3>
            {transcript.map((entry, idx) => (
              <p key={idx} className={`mb-2 ${speakerColorMap[entry.speaker] || "text-gray-800"}`}>
                <strong>{entry.speaker}:</strong> {entry.text}
              </p>
            ))}

            {filename && (
              <p className="mt-4 text-xs text-gray-500 italic">
                🔖 Saved as: <code>{filename}</code>
              </p>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}

export default UploadMeeting;
