import { useState, useEffect } from "react";

interface Run {
  enemies_killed: number;
  survived: boolean;
  date: string;
}

function App() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/runs")
      .then((response) => response.json())
      .then((data) => setRuns(data))
      .catch(() => setError("Couldn't reach the API. Is it running?"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 600, margin: "40px auto" }}>
      <h1>Deadlock — Leaderboard</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>Date</th>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>Result</th>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>Kills</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run, i) => (
            <tr key={i}>
              <td>{run.date}</td>
              <td>{run.survived ? "Survived" : "Died"}</td>
              <td>{run.enemies_killed}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;