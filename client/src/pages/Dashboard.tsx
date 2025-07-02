import Layout from "../components/Layout";

function Dashboard() {
  return (
    <Layout>
      <div className="max-w-5xl mx-auto text-white space-y-10 animate-fade-in">
        {/* 🧠 Welcome Section */}
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-slide-in-down">
          👋 Welcome to Your Smart Meeting Assistant
        </h1>

        {/* 📊 Quick Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            { label: "Meetings Uploaded", value: 12, emoji: "🎙️" },
            { label: "Summaries Generated", value: 9, emoji: "📝" },
            { label: "Questions Asked", value: 24, emoji: "🔍" },
          ].map((stat, idx) => (
            <div
              key={idx}
              className={`bg-white text-gray-800 rounded-lg p-5 shadow-lg transform transition duration-300 hover:scale-105 animate-fade-in`}
              style={{ animationDelay: `${idx * 200}ms`, animationFillMode: "both" }}
            >
              <p className="text-5xl mb-2">{stat.emoji}</p>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm text-gray-600">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* 🕒 Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow text-gray-800 animate-fade-in delay-300">
          <h2 className="text-xl font-semibold mb-3">🕒 Recent Activity</h2>
          <ul className="list-disc pl-5 space-y-2 text-gray-700">
            <li>✅ Summary generated for "Team Sync – July 1"</li>
            <li>⏳ Transcription in progress for "Marketing Sprint Planning"</li>
            <li>🔍 Searched: “What are Q2 blockers?”</li>
          </ul>
        </div>

        {/* 🚀 Quick Actions */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Upload", emoji: "🎙️", path: "/upload" },
            { label: "Summary", emoji: "📝", path: "/summary" },
            { label: "Search", emoji: "🔍", path: "/search" },
            { label: "Visuals", emoji: "🖼️", path: "/visuals" },
          ].map((action, idx) => (
            <a
              key={idx}
              href={action.path}
              className="bg-gradient-to-br from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white text-center p-4 rounded-lg font-semibold shadow-lg transform transition duration-300 hover:scale-105"
            >
              <div className="text-3xl">{action.emoji}</div>
              <div className="mt-2">{action.label}</div>
            </a>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default Dashboard;
