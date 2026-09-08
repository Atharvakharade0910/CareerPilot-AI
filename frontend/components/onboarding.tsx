"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  FileText,
  Upload,
  ShieldCheck,
  LoaderCircle,
  X,
  ChevronRight,
} from "lucide-react";
import { Brand } from "./brand";
import { api } from "@/lib/api";
const steps = [
  "About you",
  "Master resume",
  "Target roles",
  "Preferences",
  "Review your profile",
];
const roles = [
  "AI Engineer",
  "Machine Learning Engineer",
  "GenAI Engineer",
  "Data Scientist",
  "Software Engineer",
  "NLP Engineer",
];
export function Onboarding() {
  const router = useRouter();
  const qc = useQueryClient();
  const input = useRef<HTMLInputElement>(null);
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [custom, setCustom] = useState("");
  const [personal, setPersonal] = useState({
    full_name: "",
    phone: "",
    location: "",
  });
  const [preferences, setPreferences] = useState({
    target_roles: [] as string[],
    locations: [] as string[],
    work_type: "remote",
    experience_level: "entry",
    minimum_match: 75,
    relocation: false,
  });
  const [locationText, setLocationText] = useState("");
  const [resume, setResume] = useState<any>(null);
  const [facts, setFacts] = useState<any[]>([]);
  const [review, setReview] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const user = useQuery({ queryKey: ["me"], queryFn: () => api("/auth/me") });
  useEffect(() => {
    if (user.error) router.replace("/sign-in");
  }, [user.error, router]);
  useEffect(() => {
    if (!user.data) return;
    api("/profile")
      .then(async (p) => {
        setPersonal({
          full_name: user.data.full_name,
          phone: "",
          location: "",
          ...p.personal,
        });
        setPreferences((prev) => ({ ...prev, ...p.preferences }));
        setLocationText((p.preferences.locations || []).join(", "));
        setResume(p.resume);
        setFacts(await api("/profile/facts"));
        setLoaded(true);
      })
      .catch((e) => setError(e.message));
  }, [user.data]);
  async function upload(file?: File) {
    if (!file) return;
    setError("");
    if (!/\.(pdf|docx)$/i.test(file.name)) {
      setError("Choose a PDF or DOCX resume.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Resume must be 5 MB or smaller.");
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await api("/resume/upload", {
        method: "POST",
        body: form,
      });
      setResume(result);
      setReview(false);
      setFacts(await api("/profile/facts"));
      await qc.invalidateQueries({ queryKey: ["profile"] });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function saveExit() {
    setBusy(true);
    setError("");
    try {
      await api("/profile", {
        method: "PUT",
        body: JSON.stringify({
          personal,
          preferences: {
            ...preferences,
            locations: locationText
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          },
          reviewed: false,
        }),
      });
      await qc.invalidateQueries();
      router.push("/dashboard");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function next() {
    setError("");
    if (
      step === 0 &&
      (!personal.full_name.trim() || !personal.location.trim())
    ) {
      setError("Please enter your name and location.");
      return;
    }
    if (step === 1 && !resume) {
      setError("Upload a resume before continuing.");
      return;
    }
    if (step === 2 && !preferences.target_roles.length) {
      setError("Choose at least one target role.");
      return;
    }
    if (step === 4 && !review) {
      setError("Review the source evidence and confirm before finishing.");
      return;
    }
    setBusy(true);
    try {
      await api("/profile", {
        method: "PUT",
        body: JSON.stringify({
          personal,
          preferences: {
            ...preferences,
            locations: locationText
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          },
          reviewed: step === 4,
        }),
      });
      if (step === 4) {
        await qc.invalidateQueries();
        router.push("/dashboard");
      } else setStep(step + 1);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function toggleFact(f: any) {
    setError("");
    try {
      await api(`/profile/facts/${f.id}?accepted=${!f.accepted}`, {
        method: "PATCH",
      });
      setFacts((prev) =>
        prev.map((v) => (v.id === f.id ? { ...v, accepted: !v.accepted } : v)),
      );
      setReview(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <main className="onboarding">
      <header>
        <Link href="/">
          <Brand />
        </Link>
        <button disabled={busy || !loaded} onClick={saveExit}>
          Save & exit <X size={16} />
        </button>
      </header>
      <div className="onboarding-layout">
        <aside>
          <span className="eyebrow">LET’S SET YOUR DIRECTION</span>
          <h1>
            A career profile.
            <br />
            Uniquely yours.
          </h1>
          <p>Start with your experience. We’ll help you bring it into focus.</p>
          <ol>
            {steps.map((s, i) => (
              <li
                className={step === i ? "current" : step > i ? "complete" : ""}
                key={s}
              >
                <span>{step > i ? <Check size={16} /> : i + 1}</span>
                <div>
                  {s}
                  <small>
                    {
                      [
                        "The person behind the profile",
                        "Your single source of truth",
                        "Where you want to go",
                        "What matters to you",
                        "Every fact, checked by you",
                      ][i]
                    }
                  </small>
                </div>
              </li>
            ))}
          </ol>
          <div className="onboarding-trust">
            <ShieldCheck size={22} />
            <p>
              Your original resume stays private.
              <br />
              Your experience is never invented.
            </p>
          </div>
        </aside>
        <section className="wizard-panel">
          <div className="wizard-progress">
            <span>STEP {step + 1} OF 5</span>
            <span>{Math.round((step + 1) * 20)}% of the journey</span>
          </div>
          <div className="progress-track">
            <span style={{ width: (step + 1) * 20 + "%" }} />
          </div>
          <h2>
            {
              [
                "First, a little about you.",
                "Your experience starts here.",
                "What’s your next chapter?",
                "Find your kind of opportunity.",
                "Your story. Your final say.",
              ][step]
            }
          </h2>
          <p className="wizard-subtitle">
            {
              [
                "A few details to make this workspace yours.",
                "Upload your master resume. We’ll extract what’s there, with evidence.",
                "Choose roles that interest you, or add your own.",
                "These preferences will guide matching in the next phase.",
                "Check the extracted evidence. Reject anything that doesn’t represent you.",
              ][step]
            }
          </p>
          {!loaded && !error ? (
            <p className="row">
              <LoaderCircle className="spin" size={18} /> Loading your profile…
            </p>
          ) : (
            <>
              {step === 0 && (
                <div className="wizard-fields">
                  <label>
                    Full name
                    <input
                      value={personal.full_name}
                      maxLength={120}
                      onChange={(e) =>
                        setPersonal({ ...personal, full_name: e.target.value })
                      }
                      autoComplete="name"
                    />
                  </label>
                  <label>
                    Email address
                    <input value={user.data?.email || ""} disabled />
                  </label>
                  <div className="two-fields">
                    <label>
                      Phone <small>(optional)</small>
                      <input
                        type="tel"
                        value={personal.phone}
                        onChange={(e) =>
                          setPersonal({ ...personal, phone: e.target.value })
                        }
                        placeholder="+91"
                        maxLength={40}
                      />
                    </label>
                    <label>
                      Current location
                      <input
                        value={personal.location}
                        onChange={(e) =>
                          setPersonal({ ...personal, location: e.target.value })
                        }
                        placeholder="City, Country"
                        maxLength={160}
                      />
                    </label>
                  </div>
                </div>
              )}
              {step === 1 && (
                <>
                  <input
                    ref={input}
                    type="file"
                    accept=".pdf,.docx"
                    className="sr-only"
                    aria-label="Choose master resume"
                    onChange={(e) => upload(e.target.files?.[0])}
                  />
                  <button
                    disabled={busy}
                    className={`upload-zone ${drag ? "dragging" : ""}`}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setDrag(true);
                    }}
                    onDragLeave={() => setDrag(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setDrag(false);
                      if (!busy) upload(e.dataTransfer.files[0]);
                    }}
                    onClick={() => input.current?.click()}
                  >
                    {busy ? (
                      <LoaderCircle size={32} className="spin" />
                    ) : (
                      <span className="upload-icon">
                        <Upload size={28} />
                      </span>
                    )}
                    <strong>
                      {busy ? "Reading your resume…" : "Drop your resume here"}
                    </strong>
                    <span>
                      or <b>browse files</b> from your device
                    </span>
                    <small>
                      PDF or DOCX · Up to 5 MB · Text-based documents
                    </small>
                  </button>
                  {resume && (
                    <div className="uploaded-file">
                      <FileText size={26} />
                      <div>
                        <strong>{resume.filename}</strong>
                        <small>
                          {resume.extraction.fields.length} evidence items
                          extracted · Original preserved
                        </small>
                      </div>
                      <Check className="green" size={20} />
                    </div>
                  )}
                  <div className="notice">
                    <ShieldCheck size={18} />
                    <div>
                      <strong>Evidence first, always.</strong>
                      <p>
                        Local parsing is active. Scanned PDFs need OCR, which is
                        not enabled. No document is sent to an AI provider.
                      </p>
                    </div>
                  </div>
                </>
              )}
              {step === 2 && (
                <>
                  <div className="role-options">
                    {[...new Set([...roles, ...preferences.target_roles])].map(
                      (r) => (
                        <button
                          key={r}
                          className={
                            preferences.target_roles.includes(r) ? "chosen" : ""
                          }
                          onClick={() =>
                            setPreferences({
                              ...preferences,
                              target_roles: preferences.target_roles.includes(r)
                                ? preferences.target_roles.filter(
                                    (v) => v !== r,
                                  )
                                : [...preferences.target_roles, r],
                            })
                          }
                        >
                          {r}
                          {preferences.target_roles.includes(r) ? (
                            <Check size={17} />
                          ) : (
                            <span>+</span>
                          )}
                        </button>
                      ),
                    )}
                  </div>
                  <label>
                    Add a custom role
                    <div className="row">
                      <input
                        placeholder="e.g. Research Engineer"
                        value={custom}
                        maxLength={100}
                        onChange={(e) => setCustom(e.target.value)}
                      />
                      <button
                        className="button secondary"
                        onClick={() => {
                          if (custom.trim()) {
                            setPreferences({
                              ...preferences,
                              target_roles: [
                                ...new Set([
                                  ...preferences.target_roles,
                                  custom.trim(),
                                ]),
                              ],
                            });
                            setCustom("");
                          }
                        }}
                      >
                        Add
                      </button>
                    </div>
                  </label>
                </>
              )}
              {step === 3 && (
                <div className="wizard-fields">
                  <label>
                    Preferred locations
                    <input
                      placeholder="Mumbai, Pune, Bengaluru"
                      value={locationText}
                      onChange={(e) => setLocationText(e.target.value)}
                    />
                    <small>Separate locations with commas.</small>
                  </label>
                  <div className="two-fields">
                    <label>
                      Work style
                      <select
                        value={preferences.work_type}
                        onChange={(e) =>
                          setPreferences({
                            ...preferences,
                            work_type: e.target.value,
                          })
                        }
                      >
                        {["remote", "hybrid", "onsite", "any"].map((v) => (
                          <option key={v} value={v}>
                            {v[0].toUpperCase() + v.slice(1)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Experience level
                      <select
                        value={preferences.experience_level}
                        onChange={(e) =>
                          setPreferences({
                            ...preferences,
                            experience_level: e.target.value,
                          })
                        }
                      >
                        <option value="entry">Fresher / entry level</option>
                        <option value="mid">Mid level</option>
                        <option value="senior">Senior</option>
                      </select>
                    </label>
                  </div>
                  <label>
                    Minimum match score{" "}
                    <strong>{preferences.minimum_match}%</strong>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={preferences.minimum_match}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          minimum_match: Number(e.target.value),
                        })
                      }
                    />
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={preferences.relocation}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          relocation: e.target.checked,
                        })
                      }
                    />{" "}
                    I’m open to relocation
                  </label>
                  <small>
                    This is a preference, not a claim about experience in your
                    resume.
                  </small>
                </div>
              )}
              {step === 4 && (
                <>
                  <div className="review-summary">
                    <span className="user-avatar">{personal.full_name[0]}</span>
                    <div>
                      <h3>{personal.full_name}</h3>
                      <p>
                        {personal.location} ·{" "}
                        {preferences.target_roles.join(", ")}
                      </p>
                    </div>
                  </div>
                  <div className="notice">
                    These are extracted mentions, not verified proficiency. To
                    correct a factual statement, revise your master resume and
                    upload a new version. You can reject inaccurate extraction
                    below.
                  </div>
                  <div className="evidence-list">
                    {facts.length ? (
                      facts.map((f) => (
                        <article
                          className={!f.accepted ? "rejected" : ""}
                          key={f.id}
                        >
                          <div className="row space">
                            <span>
                              <small>{f.category}</small>
                              <strong>{f.value}</strong>
                            </span>
                            <button
                              className={`review-toggle ${f.accepted ? "accepted" : ""}`}
                              aria-label={`${f.accepted ? "Reject" : "Accept"} ${f.value}`}
                              onClick={() => toggleFact(f)}
                            >
                              {f.accepted ? (
                                <Check size={15} />
                              ) : (
                                <X size={15} />
                              )}{" "}
                              {f.accepted ? "Accepted" : "Excluded"}
                            </button>
                          </div>
                          <blockquote>{f.evidence}</blockquote>
                        </article>
                      ))
                    ) : (
                      <p>
                        No structured facts were detected. Review the source
                        text below; you can re-upload a resume with clear
                        section headings.
                      </p>
                    )}
                  </div>
                  <details className="source-panel">
                    <summary>Compare with original source text</summary>
                    <pre>{resume?.text}</pre>
                  </details>
                  <label className="checkbox-label review-confirm">
                    <input
                      type="checkbox"
                      checked={review}
                      onChange={(e) => setReview(e.target.checked)}
                    />{" "}
                    I have reviewed this profile and its source evidence.
                  </label>
                </>
              )}
            </>
          )}
          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}
          <div className="wizard-actions">
            <button
              className="button secondary"
              disabled={step === 0 || busy}
              onClick={() => {
                setError("");
                setStep(step - 1);
              }}
            >
              <ArrowLeft size={16} /> Back
            </button>
            <span>
              {step === 4
                ? "Ready when you are."
                : "Your progress is saved on continue."}
            </span>
            <button
              className="button"
              disabled={busy || !loaded}
              onClick={next}
            >
              {busy ? (
                <LoaderCircle className="spin" size={17} />
              ) : (
                <>
                  {step === 4 ? "Finish my profile" : "Continue"}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
