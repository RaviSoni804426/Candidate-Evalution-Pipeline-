import { useEffect, useMemo, useState } from 'react';
import {
  API_BASE_URL,
  bulkEvaluateCandidates,
  createJobDescription,
  getDashboard,
  getLatestJob,
} from './api';

const initialJobForm = {
  role: 'AI Product Analyst',
  skillsRequired: 'python, sql, machine learning, communication',
  experienceRequired: '2+ years',
  description: 'Screen candidates for AI, product, and analytics roles.',
};

function formatScore(value) {
  return Number(value || 0).toFixed(1);
}

function formatPercent(value) {
  return `${Math.round(Number(value) || 0)}%`;
}

function skillsToText(value) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  return value || '';
}

function App() {
  const [dashboard, setDashboard] = useState({ metrics: null, candidates: [], latest_job: null });
  const [latestJob, setLatestJob] = useState(null);
  const [jobForm, setJobForm] = useState(initialJobForm);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingJob, setIsSavingJob] = useState(false);
  const [isBulkSubmitting, setIsBulkSubmitting] = useState(false);

  async function refreshDashboard() {
    const [dashboardData, jobData] = await Promise.all([getDashboard(), getLatestJob()]);
    setDashboard(dashboardData);
    setLatestJob(jobData);
    return dashboardData;
  }

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [dashboardData, jobData] = await Promise.all([getDashboard(), getLatestJob()]);
        if (!mounted) {
          return;
        }
        setDashboard(dashboardData);
        setLatestJob(jobData);
        setMessage('Loaded live ranking data from the backend.');
      } catch (error) {
        if (mounted) {
          setMessage(error.message || 'Unable to load data. Start the backend and try again.');
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const activeJob = useMemo(() => latestJob || jobForm, [latestJob, jobForm]);
  const rankedCandidates = dashboard.candidates || [];
  const metrics = dashboard.metrics;

  async function handleSaveJob(event) {
    event.preventDefault();
    setIsSavingJob(true);
    setMessage('Saving job description...');
    try {
      const result = await createJobDescription({
        role: jobForm.role,
        skills_required: jobForm.skillsRequired.split(',').map((item) => item.trim()).filter(Boolean),
        experience_required: jobForm.experienceRequired,
        description: jobForm.description,
      });
      setLatestJob(result);
      setMessage(`Saved job description for ${result.role}.`);
    } catch (error) {
      setMessage(error.message || 'Failed to save job description.');
    } finally {
      setIsSavingJob(false);
    }
  }

  async function handleBulkUpload(event) {
    event.preventDefault();
    if (!resumeFiles.length) {
      setMessage('Please choose one or more resume files first.');
      return;
    }

    setIsBulkSubmitting(true);
    setMessage('Ranking uploaded resumes...');
    try {
      const formData = new FormData();
      formData.append('job_role', activeJob.role);
      formData.append('skills_required', skillsToText(activeJob.skills_required ?? activeJob.skillsRequired));
      formData.append('experience_required', activeJob.experience_required ?? activeJob.experienceRequired ?? '');
      formData.append('description', activeJob.description ?? jobForm.description ?? '');
      resumeFiles.forEach((file) => {
        formData.append('resumes', file);
      });

      const result = await bulkEvaluateCandidates(formData);
      const updatedDashboard = await refreshDashboard();
      setMessage(`Ranked ${result.uploaded_count} resumes. Top score: ${formatScore(updatedDashboard.candidates[0]?.score || 0)}.`);
      setResumeFiles([]);
      event.target.reset();
    } catch (error) {
      setMessage(error.message || 'Bulk ranking failed.');
    } finally {
      setIsBulkSubmitting(false);
    }
  }

  const topCandidates = rankedCandidates.slice(0, 12);

  return (
    <div className="app-shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />

      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">AI Recruitment Automation</p>
          <h1>One job description. Bulk resume upload. Ranked scores beside every candidate.</h1>
          <p className="hero-text">
            Set the JD once, upload all resumes together, and let the pipeline sort candidates by score with a clear ranking view.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href="#bulk-upload">Upload resumes</a>
            <a className="button button-secondary" href="#rankings">View rankings</a>
          </div>
          <div className="hero-metrics">
            <div>
              <strong>{metrics ? metrics.total_candidates : '0'}</strong>
              <span>candidates tracked</span>
            </div>
            <div>
              <strong>{metrics ? formatScore(metrics.average_score) : '0.0'}</strong>
              <span>average score</span>
            </div>
            <div>
              <strong>{metrics ? formatPercent(metrics.shortlist_rate) : '0%'}</strong>
              <span>shortlist rate</span>
            </div>
          </div>
        </div>

        <aside className="hero-card">
          <div className="hero-card-top">
            <span className="status-pill live">Bulk ranking flow</span>
            <span className="status-pill neutral">Backend: {API_BASE_URL}</span>
          </div>
          <div className="pipeline">
            <div>
              <span>1</span>
              <strong>Save the JD</strong>
              <p>Define role, skills, and experience once.</p>
            </div>
            <div>
              <span>2</span>
              <strong>Upload all resumes</strong>
              <p>Select multiple PDF or DOCX files in one batch.</p>
            </div>
            <div>
              <span>3</span>
              <strong>Rank by score</strong>
              <p>See the strongest candidates immediately, with scores next to each name.</p>
            </div>
          </div>
        </aside>
      </header>

      <main className="layout-grid">
        <section className="panel" id="job-description">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Job description</p>
              <h2>Set the role once, then use it for every bulk upload.</h2>
            </div>
            <span className="status-pill">Saved JD</span>
          </div>

          <form className="form-grid" onSubmit={handleSaveJob}>
            <label className="full-width">
              Role
              <input
                value={jobForm.role}
                onChange={(event) => setJobForm((current) => ({ ...current, role: event.target.value }))}
              />
            </label>
            <label>
              Required skills
              <textarea
                rows="3"
                value={jobForm.skillsRequired}
                onChange={(event) => setJobForm((current) => ({ ...current, skillsRequired: event.target.value }))}
              />
            </label>
            <label>
              Experience required
              <input
                value={jobForm.experienceRequired}
                onChange={(event) => setJobForm((current) => ({ ...current, experienceRequired: event.target.value }))}
              />
            </label>
            <label className="full-width">
              Description
              <textarea
                rows="4"
                value={jobForm.description}
                onChange={(event) => setJobForm((current) => ({ ...current, description: event.target.value }))}
              />
            </label>
            <div className="form-actions full-width">
              <button className="button button-secondary" type="submit" disabled={isSavingJob}>
                {isSavingJob ? 'Saving...' : 'Save job description'}
              </button>
              <span className="helper-copy">{latestJob ? `Active role: ${latestJob.role}` : 'No saved job description yet'}</span>
            </div>
          </form>
        </section>

        <section className="panel" id="bulk-upload">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Bulk resume upload</p>
              <h2>Upload all resumes together and get a ranked list with scores.</h2>
            </div>
            <span className="status-pill">Multi-file upload</span>
          </div>

          <form className="form-grid" onSubmit={handleBulkUpload}>
            <label className="full-width">
              Resume files
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                multiple
                onChange={(event) => setResumeFiles(Array.from(event.target.files || []))}
              />
            </label>

            <div className="form-actions full-width">
              <button className="button button-primary" type="submit" disabled={isBulkSubmitting}>
                {isBulkSubmitting ? 'Ranking...' : 'Rank uploaded resumes'}
              </button>
              <span className="helper-copy">
                {resumeFiles.length ? `${resumeFiles.length} file(s) selected` : 'Select multiple resumes and rank them together'}
              </span>
            </div>
          </form>
        </section>
      </main>

      <section className="panel dashboard-panel" id="rankings">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Rankings</p>
            <h2>Scores are shown beside each candidate, sorted from highest to lowest.</h2>
          </div>
          {metrics ? (
            <div className="metrics-strip">
              <span>{metrics.processed_resumes} processed resumes</span>
              <span>{metrics.total_candidates} total candidates</span>
            </div>
          ) : null}
        </div>

        {isLoading ? <div className="loading-state">Loading live data...</div> : null}

        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>Score</th>
                <th>Technical</th>
                <th>Experience</th>
                <th>Skills</th>
              </tr>
            </thead>
            <tbody>
              {topCandidates.map((candidate, index) => (
                <tr key={candidate.id}>
                  <td>
                    <span className="rank-pill">{index + 1}</span>
                  </td>
                  <td>
                    <div className="candidate-cell">
                      <strong>{candidate.name}</strong>
                      <span>{candidate.job_title || 'Candidate profile'}</span>
                    </div>
                  </td>
                  <td>
                    <span className="score-pill">{formatScore(candidate.score)}</span>
                  </td>
                  <td>{formatPercent(candidate.technical_score)}</td>
                  <td>{formatPercent(candidate.experience_score)}</td>
                  <td>
                    <div className="skill-preview">
                      {(candidate.skills || []).slice(0, 3).map((skill) => (
                        <span key={skill}>{skill}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel notes-panel">
        <div>
          <p className="eyebrow">Status</p>
          <h2>{message || 'Ready for bulk ranking.'}</h2>
        </div>
      </section>

      <footer className="footer-bar">
        <span>Use the backend at {API_BASE_URL}</span>
        <span>{latestJob ? `Active JD: ${latestJob.role}` : 'No active job description yet'}</span>
      </footer>
    </div>
  );
}

export default App;
