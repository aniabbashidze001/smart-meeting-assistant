import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import UploadMeeting from "./pages/UploadMeeting";
import MeetingSummary from "./pages/MeetingSummary";
import SemanticSearch from "./pages/SemanticSearch";
import VisualSummaries from "./pages/VisualSummaries";
import Calendar from "./pages/Calendar";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<UploadMeeting />} />
        <Route path="/summary" element={<MeetingSummary />} />
        <Route path="/search" element={<SemanticSearch />} />
        <Route path="/visuals" element={<VisualSummaries />} />
        <Route path="/calendar" element={<Calendar />} />
      </Routes>
    </Router>
  );
}

export default App;
