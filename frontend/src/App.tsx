import { useEffect, useState, type FormEvent } from "react";
import "./App.css";
import type { AnalysisHistoryItem, AnalysisResponse } from "./types";

function App() {
  const [cvText, setCvText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem("career-agent-history");
    if (saved) {
      try {
        setHistory(JSON.parse(saved));
      } catch {
        setHistory([]);
      }
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(
      "career-agent-history",
      JSON.stringify(history),
    );
  }, [history]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cv_text: cvText,
          job_description: jobDescription,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to analyze the profile right now.");
      }

      const data = (await response.json()) as AnalysisResponse;
      setResult(data);
      setHistory((current) => [
        {
          ...data,
          id: `${Date.now()}`,
          created_at: new Date().toISOString(),
        },
        ...current,
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  }

  function handleRecall(item: AnalysisHistoryItem) {
    setResult(item);
  }

  function handleClearHistory() {
    setHistory([]);
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <h1>AI Career Agent MVP</h1>
        <p>
          Paste your CV and a job description to receive a structured match
          report.
        </p>
      </section>

      <form className="analysis-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>CV / profile</span>
          <textarea
            value={cvText}
            onChange={(event) => setCvText(event.target.value)}
            placeholder="Paste your CV or profile summary"
            rows={10}
          />
        </label>

        <label className="field">
          <span>Job description</span>
          <textarea
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            placeholder="Paste the target role description"
            rows={10}
          />
        </label>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing…" : "Analyze match"}
        </button>
      </form>

      {error ? <p className="error">{error}</p> : null}

      {isLoading ? (
        <div className="result-card loading-state">
          <h3>Analyzing your profile</h3>
          <p>We are comparing your background with the job requirements.</p>
        </div>
      ) : null}

      {!result && !isLoading ? (
        <div className="result-card empty-state">
          <h3>Ready to review a role</h3>
          <p>
            Paste a CV and a job description to get a structured match report.
          </p>
        </div>
      ) : null}

      {result ? (
        <>
          <section className="results-panel">
            <div className="score-card">
              <h2>Match score</h2>
              <div className="score-value">{result.match_score}%</div>
              <div className="recommendation">{result.recommendation}</div>
            </div>

            <div className="result-card">
              <h3>Profile summary</h3>
              <ul>
                {result.profile_summary.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="result-grid">
              <div className="result-card">
                <h3>Technologies</h3>
                <ul>
                  {result.technologies.map((technology) => (
                    <li key={technology}>{technology}</li>
                  ))}
                </ul>
              </div>
              <div className="result-card">
                <h3>Experience</h3>
                <p>{result.experience_years} years inferred</p>
              </div>
              <div className="result-card">
                <h3>Education</h3>
                <ul>
                  {result.education.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="result-grid">
              <div className="result-card">
                <h3>Matching skills</h3>
                <ul>
                  {result.matching_skills.map((skill) => (
                    <li key={skill}>{skill}</li>
                  ))}
                </ul>
              </div>
              <div className="result-card">
                <h3>Missing skills</h3>
                <ul>
                  {result.missing_skills.map((skill) => (
                    <li key={skill}>{skill}</li>
                  ))}
                </ul>
              </div>
              <div className="result-card">
                <h3>Weak skills</h3>
                <ul>
                  {result.weak_skills.map((skill) => (
                    <li key={skill}>{skill}</li>
                  ))}
                </ul>
              </div>
              <div className="result-card">
                <h3>Experience gaps</h3>
                <ul>
                  {result.experience_gaps.map((gap) => (
                    <li key={gap}>{gap}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="result-card">
              <h3>Why this score</h3>
              <ul>
                {result.reasoning.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>

            <div className="result-card">
              <h3>Suggested learning</h3>
              <ul>
                {result.learning_recommendations.map((topic) => (
                  <li key={topic}>{topic}</li>
                ))}
              </ul>
            </div>
          </section>

          {history.length > 0 ? (
            <section className="history-panel">
              <div className="history-header">
                <h2>Recent analyses</h2>
                <button
                  type="button"
                  className="clear-history"
                  onClick={handleClearHistory}
                >
                  Clear history
                </button>
              </div>
              <div className="history-grid">
                {history.slice(0, 4).map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className="history-card history-card-button"
                    onClick={() => handleRecall(item)}
                  >
                    <div className="history-heading">
                      <span>{item.match_score}%</span>
                      <strong>{item.recommendation}</strong>
                    </div>
                    <p>
                      {new Date(item.created_at).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </p>
                    <div className="history-summary">
                      <strong>Top skills:</strong>{" "}
                      {item.matching_skills.slice(0, 3).join(", ") || "None"}
                    </div>
                  </button>
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </main>
  );
}

export default App;
