import Link from "next/link";
import {
  ArrowUpRight,
  ArrowRight,
  FileText,
  ScanLine,
  ShieldCheck,
  Compass,
  Sparkles,
  Check,
  Route,
} from "lucide-react";
import { Brand } from "@/components/brand";
export default function Landing() {
  return (
    <main className="landing">
      <nav className="landing-nav">
        <Link href="/">
          <Brand />
        </Link>
        <div className="landing-links">
          <a href="#how">How it works</a>
          <a href="#trust">Built on trust</a>
          <Link href="/demo">Explore the product</Link>
        </div>
        <Link className="button secondary" href="/sign-in">
          Sign in <ArrowUpRight size={16} />
        </Link>
      </nav>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="live-dot" /> A more intentional job search
          </span>
          <h1>
            Your next chapter.
            <br />
            <span>A clearer direction.</span>
          </h1>
          <p>
            Your AI Career Agent. Turn your real experience into a profile you
            can trust—and a job search with purpose.
          </p>
          <div className="button-row">
            <Link className="button" href="/sign-up">
              Get started <ArrowRight size={18} />
            </Link>
            <Link className="button secondary" href="/demo">
              View demo <ArrowUpRight size={18} />
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="path-label">
            <Route size={16} /> YOUR CAREER, CONNECTED
          </div>
          <div className="resume-preview">
            <div className="row">
              <span className="file-icon">
                <FileText />
              </span>
              <span>
                <strong>Your master resume</strong>
                <small>The starting point. Always.</small>
              </span>
              <ShieldCheck className="green" />
            </div>
            <div className="paper-lines">
              <i />
              <i />
              <i />
            </div>
            <div className="row space">
              <span className="tag">Evidence included</span>
              <Check size={18} className="green" />
            </div>
          </div>
          <div className="opportunity-preview">
            <span className="mini-label">A MORE INFORMED NEXT STEP</span>
            <h3>
              See the opportunity.
              <br />
              Understand the fit.
            </h3>
            <div className="row">
              <span className="tag">Your skills</span>
              <span className="tag">Your projects</span>
              <span className="tag">Your goals</span>
            </div>
            <div className="preview-rule" />
            <p>
              <ShieldCheck size={17} /> Your experience. Never invented.
            </p>
          </div>
          <span className="floating-compass">
            <Compass size={32} />
          </span>
        </div>
      </section>
      <section className="workflow-strip">
        <span>
          One profile.
          <br />
          <strong>A connected journey.</strong>
        </span>
        {["Resume", "Match", "Improve", "Apply", "Track"].map((s, i) => (
          <div key={s}>
            <span className="step-number">0{i + 1}</span>
            {s}
            {i < 4 && <ArrowRight size={16} />}
          </div>
        ))}
      </section>
      <section id="how" className="landing-section">
        <span className="eyebrow">FROM RESUME TO OPPORTUNITY</span>
        <h2>Start with what makes you, you.</h2>
        <p>A thoughtful foundation for every career decision.</p>
        <div className="feature-grid">
          <article>
            <FileText />
            <h3>Your experience, organized.</h3>
            <p>
              Upload a PDF or DOCX. Review extracted skills, education and
              projects alongside their original evidence.
            </p>
            <span className="tag">Available now</span>
          </article>
          <article>
            <ScanLine />
            <h3>Clarity behind every match.</h3>
            <p>
              Explore the demo vision for explainable matching, recurring skill
              gaps and learning priorities.
            </p>
            <span className="tag neutral">Product preview</span>
          </article>
          <article>
            <Compass />
            <h3>You stay in the pilot seat.</h3>
            <p>
              The roadmap connects truthful resume tailoring, application review
              and career analytics.
            </p>
            <span className="tag neutral">Coming in later phases</span>
          </article>
        </div>
      </section>
      <section id="trust" className="trust-section">
        <ShieldCheck size={44} />
        <div>
          <h2>Ambition, grounded in truth.</h2>
          <p>
            Your resume is private. Every extracted fact has a source. Your
            career story stays yours.
          </p>
        </div>
        <Link className="button secondary" href="/sign-up">
          Build your profile <ArrowUpRight size={18} />
        </Link>
      </section>
      <footer>
        <Brand />
        <span>From resume to opportunity — intelligently.</span>
        <span>Phase 1 · Evidence-first foundation</span>
        <span><Link href="/terms">Terms</Link> · <Link href="/privacy">Privacy</Link></span>
      </footer>
    </main>
  );
}
