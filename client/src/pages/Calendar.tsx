import { useEffect, useState } from "react";
import Layout from "../components/Layout";

interface Event {
  date: string;
  title: string;
  emoji?: string;
}

function Calendar() {
  const [events, setEvents] = useState<Event[]>([]);
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());

  const monthName = new Date(currentYear, currentMonth).toLocaleString("default", { month: "long" });
  const firstDay = new Date(currentYear, currentMonth, 1);
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const startWeekday = firstDay.getDay();

  const colorClasses = [
    "bg-pink-300 text-pink-900",
    "bg-blue-300 text-blue-900",
    "bg-green-300 text-green-900",
    "bg-yellow-300 text-yellow-900",
    "bg-purple-300 text-purple-900",
    "bg-orange-300 text-orange-900",
  ];

  useEffect(() => {
    fetch("http://localhost:5050/data/calendar_events.json")
      .then((res) => res.json())
      .then((data) => {
        console.log("✅ Loaded events:", data);
        setEvents(data);
      })
      .catch(() => setEvents([]));
  }, []);

  function getDayMeetings(day: number): Event[] {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    const matches = events.filter((e) => e.date.trim() === dateStr);
    if (matches.length > 0) {
      console.log(`✅ Found ${matches.length} event(s) for ${dateStr}:`, matches);
    }
    return matches;
  }

  function prevYear() {
    setCurrentYear((y) => y - 1);
  }

  function nextYear() {
    setCurrentYear((y) => y + 1);
  }

  function prevMonth() {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((y) => y - 1);
    } else {
      setCurrentMonth((m) => m - 1);
    }
  }

  function nextMonth() {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((y) => y + 1);
    } else {
      setCurrentMonth((m) => m + 1);
    }
  }

  function FancyButton({ label, onClick }: { label: string; onClick: () => void }) {
    return (
      <button
        onClick={onClick}
        className="px-3 py-1 mx-1 text-white border border-blue-500 rounded-md shadow-md hover:bg-blue-600 hover:shadow-blue-400/50 transition-all duration-200"
      >
        {label}
      </button>
    );
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto p-6">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-6 px-6 max-w-2xl mx-auto">
          <div className="flex space-x-2">
            <FancyButton label="«" onClick={prevYear} />
            <FancyButton label="‹" onClick={prevMonth} />
          </div>

          <h1 className="text-3xl font-bold text-white text-center min-w-[180px]">
            📅 {monthName} {currentYear}
          </h1>

          <div className="flex space-x-2">
            <FancyButton label="›" onClick={nextMonth} />
            <FancyButton label="»" onClick={nextYear} />
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-4 text-center text-white">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
            <div key={d} className="font-semibold text-blue-300">{d}</div>
          ))}

          {Array.from({ length: startWeekday }, (_, i) => (
            <div key={`empty-${i}`} />
          ))}

          {Array.from({ length: daysInMonth }, (_, i) => {
            const day = i + 1;
            const meetings = getDayMeetings(day);

            return (
              <div
                key={day}
                className="bg-white/10 rounded-lg p-2 h-32 overflow-hidden flex flex-col items-start justify-start text-left border border-white/20 hover:scale-[1.02] transition-transform"
              >
                <div className="text-sm font-bold">{day}</div>

                {meetings.slice(0, 2).map((m, idx) => (
                  <div
                    key={idx}
                    className={`mt-1 px-1 py-0.5 text-xs rounded-md truncate w-full cursor-default ${colorClasses[idx % colorClasses.length]}`}
                    title={m.title}
                  >
                    <span className="truncate inline-block w-full">
                      {m.emoji || "📌"} {m.title}
                    </span>
                  </div>
                ))}

                {meetings.length > 2 && (
                  <div className="mt-1 text-xs text-gray-300">+{meetings.length - 2} more</div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Layout>
  );
}

export default Calendar;
