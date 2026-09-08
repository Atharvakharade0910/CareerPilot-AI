import Link from "next/link";
import { Check, Bookmark, MapPin, Compass, ArrowRight } from "lucide-react";
import { demoJobs } from "@/lib/demo";
export function JobCard({
  job,
  saved,
  onSave,
  onView,
}: {
  job: (typeof demoJobs)[number];
  saved: boolean;
  onSave: () => void;
  onView: () => void;
}) {
  return (
    <article className="job-card">
      <span className={`company-avatar ${job.color}`}>{job.initial}</span>
      <div className="job-main">
        <div className="row space">
          <span className="company-name">
            {job.company} <span>· 2 days ago</span>
          </span>
          <button
            aria-label={saved ? `Unsave ${job.role}` : `Save ${job.role}`}
            className="save-button"
            onClick={onSave}
          >
            <Bookmark size={17} fill={saved ? "currentColor" : "none"} />
          </button>
        </div>
        <button className="job-title" onClick={onView}>
          {job.role}
        </button>
        <div className="job-meta">
          <span>
            <MapPin size={12} />
            {job.location}
          </span>
          <span>{job.type}</span>
          <span>{job.salary}</span>
        </div>
        <div className="chips">
          {job.skills.map((s) => (
            <span className="skill-chip" key={s}>
              <Check size={11} />
              {s}
            </span>
          ))}
          <span className="skill-chip missing">{job.gap}</span>
        </div>
      </div>
      <button className="job-score" onClick={onView}>
        <ScoreRing score={job.score} />
        <span>Strong match</span>
      </button>
    </article>
  );
}
export function ScoreRing({
  score,
  large = false,
}: {
  score: number;
  large?: boolean;
}) {
  return (
    <div
      className={`score-ring ${large ? "large" : ""}`}
      role="img"
      aria-label={`${score} out of 100`}
      style={{
        background: `conic-gradient(var(--green) ${score * 3.6}deg, var(--border) 0deg)`,
      }}
    >
      <div>
        <strong>
          {score}
          <small>{large ? "/ 100" : ""}</small>
        </strong>
        {!large && <small>% match</small>}
      </div>
    </div>
  );
}
export function Empty({
  title,
  text,
  href,
  action,
}: {
  title: string;
  text: string;
  href?: string;
  action?: string;
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Compass size={34} />
      </span>
      <h2>{title}</h2>
      <p>{text}</p>
      {href && (
        <Link className="button" href={href}>
          {action}
          <ArrowRight size={16} />
        </Link>
      )}
    </div>
  );
}
