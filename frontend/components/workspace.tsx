"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import * as Dialog from "@radix-ui/react-dialog";
import { motion, useReducedMotion } from "motion/react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  LayoutDashboard,
  Sparkles,
  Search,
  Target,
  BriefcaseBusiness,
  Video,
  FileText,
  ChartNoAxesCombined,
  ChartPie,
  Bell,
  User,
  Settings,
  ArrowUpRight,
  ArrowRight,
  ChevronDown,
  Plus,
  ShieldCheck,
  Check,
  Bookmark,
  MapPin,
  Clock3,
  Menu,
  X,
  LogOut,
  CircleHelp,
  Command,
  Moon,
  Sun,
  Upload,
  TrendingUp,
  ChevronRight,
  Compass,
  LockKeyhole,
} from "lucide-react";
import { JobCard, ScoreRing, Empty } from "./workspace-cards";
import { MockInterviewPanel } from "./mock-interview";
import { Brand } from "./brand";
import { demoJobs, navigation, trend } from "@/lib/demo";
import { api } from "@/lib/api";
const icons = [
  LayoutDashboard,
  Sparkles,
  Search,
  Target,
  BriefcaseBusiness,
  Video,
  FileText,
  ChartNoAxesCombined,
  ChartPie,
  Bell,
  User,
  Settings,
];
export function Workspace({
  demo = false,
  section = "dashboard",
}: {
  demo?: boolean;
  section?: string;
}) {
  const reducedMotion = useReducedMotion();
  const router = useRouter();
  const path = usePathname();
  const [menu, setMenu] = useState(false);
  const [command, setCommand] = useState(false);
  const [search, setSearch] = useState("");
  const [dark, setDark] = useState(false);
  const [toast, setToast] = useState("");
  const [filter, setFilter] = useState("All opportunities");
  const [saved, setSaved] = useState<string[]>([]);
  const [selected, setSelected] = useState<(typeof demoJobs)[number] | null>(
    null,
  );
  const user = useQuery({
    queryKey: ["me"],
    queryFn: () => api("/auth/me"),
    enabled: !demo,
  });
  const profile = useQuery({
    queryKey: ["profile"],
    queryFn: () => api("/profile"),
    enabled: !demo && !!user.data,
  });
  const metrics = useQuery({
    queryKey: ["overview"],
    queryFn: () => api("/analytics/overview"),
    enabled: !demo && !!user.data,
  });
  const versions = useQuery({
    queryKey: ["versions"],
    queryFn: () => api<any[]>("/resume/versions"),
    enabled: !demo && !!user.data,
  });
  const notifications = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api<any[]>("/notifications"),
    enabled: !demo && !!user.data,
  });
  const realJobs = useQuery<any[]>({
    queryKey: ["jobs", search],
    queryFn: () => api(`/jobs?q=${encodeURIComponent(search)}`),
    enabled: !demo && !!user.data && (section === "jobs" || section === "matches"),
  });
  const realApplications = useQuery<any[]>({
    queryKey: ["applications"],
    queryFn: () => api("/applications"),
    enabled: !demo && !!user.data && section === "applications",
  });
  useEffect(() => {
    if (user.error) router.replace("/sign-in");
  }, [user.error, router]);
  useEffect(() => {
    setDark(localStorage.getItem("careerpilot-theme") === "dark");
    const key = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setCommand((c) => !c);
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, []);
  useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(""), 4000);
      return () => clearTimeout(id);
    }
  }, [toast]);
  const href = (slug: string) =>
    demo
      ? `/demo${slug === "dashboard" ? "" : "/" + slug}`
      : `/${slug === "dashboard" ? "dashboard" : "workspace/" + slug}`;
  const title = navigation.find((n) => n.slug === section)?.label || "Overview";
  const name = demo ? "Alex" : user.data?.full_name?.split(" ")[0] || "there";

  function toggleSave(id: string) {
    setSaved((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id],
    );
    setToast("Demo shortlist updated for this visit.");
  }
  const jobs = demoJobs.filter(
    (j) =>
      (filter !== "Remote only" || j.type === "Remote") &&
      (filter !== "Saved" || saved.includes(j.id)) &&
      `${j.role} ${j.company}`.toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <div className={`workspace ${dark ? "dark" : ""}`}>
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <Link href={href("dashboard")}>
          <Brand />
        </Link>
        <div className="workspace-switch">
          <span className="workspace-avatar">P</span>
          <div>
            Personal workspace
            <small>{demo ? "Demo experience" : "Your career space"}</small>
          </div>
          <ChevronDown size={15} />
        </div>
        <span className="nav-label">WORKSPACE</span>
        <nav>
          {navigation.map((n, i) => {
            const Icon = icons[i];
            return (
              <Link
                onClick={() => setMenu(false)}
                href={href(n.slug)}
                key={n.slug}
                className={`nav-item ${section === n.slug ? "active" : ""}`}
              >
                <Icon size={18} />
                <span>{n.label}</span>
                {n.slug === "assistant" && <span className="tiny-ai">AI</span>}
                {demo && n.slug === "applications" && (
                  <span className="nav-count">9</span>
                )}
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <div className="truth-note">
            <ShieldCheck size={21} />
            <strong>Your story. Only the truth.</strong>
            <p>Every claim starts with your experience.</p>
          </div>
          <button
            className="nav-item"
            onClick={() =>
              setToast(
                "Start with Resume Studio. Upload a text-based PDF or DOCX, then review the source evidence.",
              )}
          >
            <CircleHelp size={18} /> Help & getting started
          </button>
          <div className="user-row">
            <span className="user-avatar">{name[0]}</span>
            <div>
              <strong>
                {demo ? "Alex Morgan" : user.data?.full_name || "Your account"}
              </strong>
              <small>{demo ? "Demo candidate" : "Personal account"}</small>
            </div>
            <button
              aria-label={demo ? "Leave demo" : "Log out"}
              onClick={async () => {
                if (!demo) await api("/auth/logout", { method: "POST" });
                window.location.href = "/";
              }}
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
      {menu && (
        <button
          aria-label="Close navigation"
          className="drawer-shade"
          onClick={() => setMenu(false)}
        />
      )}
      <div className="main-shell">
        <header className="topbar">
          <div className="row">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setMenu(true)}
            >
              <Menu size={20} />
            </button>
            <span className="breadcrumb">
              Workspace <ChevronRight size={13} /> <strong>{title}</strong>
            </span>
          </div>
          <div className="row">
            <button
              className="command-trigger"
              onClick={() => setCommand(true)}
            >
              <Search size={16} />
              <span>Search anything...</span>
              <kbd>⌘ K</kbd>
            </button>
            <button
              className="icon-button"
              aria-label="Toggle color theme"
              onClick={() => {
                localStorage.setItem(
                  "careerpilot-theme",
                  dark ? "light" : "dark",
                );
                setDark(!dark);
              }}
            >
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <Link
              href={href("notifications")}
              className="icon-button"
              aria-label="Notifications"
            >
              <Bell size={19} />
            </Link>
            <span className="top-avatar">{name[0]}</span>
          </div>
        </header>
        <main className="dashboard-content">
          {demo && (
            <div className="demo-banner">
              <span>
                <Compass size={15} />
                <strong>Demo workspace</strong> · Fictional candidate, companies
                and illustrative scores.
              </span>
              <Link href="/sign-up">
                Make it yours <ArrowRight size={14} />
              </Link>
            </div>
          )}
          {!demo && user.isPending ? (
            <div className="loading-state">
              <div className="skeleton" />
              <div className="skeleton" />
              <p>Opening your workspace…</p>
            </div>
          ) : (
            <motion.div
              key={path}
              initial={reducedMotion ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              {!demo && (profile.error || metrics.error) && (
                <div className="error" role="alert">
                  Could not load workspace data.{" "}
                  <button
                    onClick={() => {
                      profile.refetch();
                      metrics.refetch();
                    }}
                  >
                    Try again
                  </button>
                </div>
              )}
              <div className="page-heading">
                <div>
                  <div className="date-line">YOUR CAREER, IN FOCUS</div>
                  <h1>
                    {section === "dashboard"
                      ? `A little clarity. A lot of possibility.`
                      : title}
                  </h1>
                  <p>
                    {section === "dashboard"
                      ? `Welcome${demo ? "" : " back"}, ${name}. ${demo ? "Here’s where your next chapter is taking shape." : "Let’s build your career profile on real evidence."}`
                      : section === "resume"
                        ? "One source of truth. Every version of your story."
                        : section === "skills"
                          ? "Turn recurring gaps into your next advantage."
                          : "A clear view of your career journey."}
                  </p>
                </div>
                {section === "dashboard" && (
                  <Link
                    className="button secondary"
                    href={demo ? "/demo/jobs" : "/onboarding"}
                  >
                    {demo ? <Search size={16} /> : <Plus size={16} />}{" "}
                    {demo ? "Explore opportunities" : "Build your profile"}
                  </Link>
                )}
              </div>
              {section === "dashboard" ? (
                <>
                  <section className="momentum-banner">
                    <div>
                      <span className="banner-eyebrow">
                        <Sparkles size={15} /> YOUR NEXT BEST MOVE
                      </span>
                      <h2>
                        {demo
                          ? "Your potential is bigger than a job title."
                          : profile.data?.reviewed
                            ? "Your profile has a solid starting point."
                            : "Good opportunities start with your story."}
                      </h2>
                      <p>
                        {demo ? (
                          <>
                            You have <strong>18 strong matches</strong>. A
                            little focus on deployment skills could open even
                            more doors.
                          </>
                        ) : profile.data?.reviewed ? (
                          "Your resume and preferences are saved. Visit Resume Studio to review your evidence and versions."
                        ) : (
                          "Upload your master resume. We’ll organize your experience so you can review every detail."
                        )}
                      </p>
                      <Link
                        href={
                          demo
                            ? "/demo/matches"
                            : profile.data?.reviewed
                              ? "/workspace/resume"
                              : "/onboarding"
                        }
                      >
                        {demo
                          ? "See my strongest matches"
                          : profile.data?.reviewed
                            ? "Open Resume Studio"
                            : "Create my career profile"}{" "}
                        <ArrowRight size={17} />
                      </Link>
                    </div>
                    <div className="momentum-art">
                      <div className="compass-circle">
                        <Compass size={66} strokeWidth={1} />
                      </div>
                      <span className="orbit-caption">YOUR NORTH STAR</span>
                    </div>
                  </section>
                  <section className="metrics-grid">
                    {[
                      {
                        label: "Profile completeness",
                        value: demo
                          ? "82%"
                          : `${metrics.data?.profile_completeness || 0}%`,
                        note: demo
                          ? "A strong foundation"
                          : "Based on 4 setup steps",
                        Icon: User,
                      },
                      {
                        label: "Relevant opportunities",
                        value: demo ? "47" : "0",
                        note: demo
                          ? "18 strong matches"
                          : "Job discovery · Phase 2",
                        Icon: BriefcaseBusiness,
                      },
                      {
                        label: "Applications",
                        value: demo ? "9" : "0",
                        note: demo
                          ? "3 awaiting your review"
                          : "Application flow · Phase 6",
                        Icon: FileText,
                      },
                      {
                        label: "Interviews",
                        value: demo ? "2" : "0",
                        note: demo
                          ? "Your next chapter awaits"
                          : "No interviews recorded",
                        Icon: Target,
                      },
                    ].map((m) => (
                      <article className="metric" key={m.label}>
                        <div className="row space">
                          <span>{m.label}</span>
                          <m.Icon size={17} />
                        </div>
                        <strong>{m.value}</strong>
                        <small>{m.note}</small>
                      </article>
                    ))}
                  </section>
                  <div className="dashboard-columns">
                    <div className="primary-column">
                      <section className="panel">
                        <div className="section-title">
                          <div>
                            <h2>
                              {demo
                                ? "Opportunities worth your attention"
                                : "Your profile checklist"}
                            </h2>
                            <p>
                              {demo
                                ? "Selected for your skills, projects and ambitions."
                                : "A few thoughtful steps. A stronger foundation."}
                            </p>
                          </div>
                          {demo && (
                            <Link href={href("jobs")}>
                              View all <ArrowUpRight size={15} />
                            </Link>
                          )}
                        </div>
                        {demo ? (
                          <>
                            {demoJobs.slice(0, 3).map((job) => (
                              <JobCard
                                key={job.id}
                                job={job}
                                saved={saved.includes(job.id)}
                                onSave={() => toggleSave(job.id)}
                                onView={() => setSelected(job)}
                              />
                            ))}
                          </>
                        ) : (
                          <div className="checklist">
                            {[
                              [
                                "Upload your master resume",
                                !!profile.data?.resume,
                                "PDF or DOCX, up to 5 MB.",
                              ],
                              [
                                "Tell us where you want to go",
                                !!profile.data?.preferences?.target_roles
                                  ?.length,
                                "Set target roles and work preferences.",
                              ],
                              [
                                "Review your source evidence",
                                !!profile.data?.reviewed,
                                "Accept or reject extracted facts.",
                              ],
                            ].map(([label, done, note], i) => (
                              <Link href="/onboarding" key={i}>
                                <span
                                  className={`check-circle ${done ? "done" : ""}`}
                                >
                                  {done ? <Check size={16} /> : i + 1}
                                </span>
                                <div>
                                  <strong>{label}</strong>
                                  <p>{note}</p>
                                </div>
                                <ArrowUpRight size={17} />
                              </Link>
                            ))}
                          </div>
                        )}
                      </section>
                      <section className="panel trend-panel">
                        <div className="section-title">
                          <div>
                            <h2>
                              {demo
                                ? "Your momentum, over time"
                                : "Evidence you can trace"}
                            </h2>
                            <p>
                              {demo
                                ? "Average job match · illustrative demo trend"
                                : "Your resume stays the source of truth."}
                            </p>
                          </div>
                          {demo && (
                            <span className="tag">
                              +23 pts <TrendingUp size={13} />
                            </span>
                          )}
                        </div>
                        {demo ? (
                          <div className="chart-wrap">
                            <ResponsiveContainer width="100%" height={180}>
                              <AreaChart
                                data={trend}
                                margin={{
                                  top: 10,
                                  right: 8,
                                  left: -28,
                                  bottom: 0,
                                }}
                              >
                                <defs>
                                  <linearGradient
                                    id="matchGradient"
                                    x1="0"
                                    y1="0"
                                    x2="0"
                                    y2="1"
                                  >
                                    <stop
                                      offset="0%"
                                      stopColor="#27836b"
                                      stopOpacity={0.22}
                                    />
                                    <stop
                                      offset="100%"
                                      stopColor="#27836b"
                                      stopOpacity={0}
                                    />
                                  </linearGradient>
                                </defs>
                                <CartesianGrid
                                  strokeDasharray="4 4"
                                  vertical={false}
                                  stroke="var(--border)"
                                />
                                <XAxis
                                  dataKey="week"
                                  tickLine={false}
                                  axisLine={false}
                                  tick={{ fontSize: 11, fill: "#81908a" }}
                                />
                                <YAxis
                                  domain={[40, 100]}
                                  tickLine={false}
                                  axisLine={false}
                                  tick={{ fontSize: 11, fill: "#81908a" }}
                                />
                                <Tooltip
                                  contentStyle={{
                                    background: "var(--surface)",
                                    border: "1px solid var(--border)",
                                    borderRadius: 8,
                                    color: "var(--ink)",
                                  }}
                                />
                                <Area
                                  type="monotone"
                                  dataKey="match"
                                  stroke="#27836b"
                                  strokeWidth={2.5}
                                  fill="url(#matchGradient)"
                                  isAnimationActive={false}
                                />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        ) : (
                          <div className="evidence-empty">
                            <ShieldCheck size={38} />
                            <p>
                              {metrics.data?.facts
                                ? `${metrics.data.facts} accepted facts in your latest resume.`
                                : "No resume evidence yet. Upload your resume to get started."}
                            </p>
                            <Link href="/workspace/resume">
                              Visit Resume Studio <ArrowRight size={15} />
                            </Link>
                          </div>
                        )}
                      </section>
                    </div>
                    <div className="secondary-column">
                      <section className="panel readiness">
                        <div className="section-title">
                          <h2>
                            {demo ? "Career readiness" : "Profile foundation"}
                          </h2>
                          <ShieldCheck size={18} />
                        </div>
                        <ScoreRing
                          score={
                            demo ? 82 : metrics.data?.profile_completeness || 0
                          }
                          large
                        />
                        <h3>
                          {demo
                            ? "You’re building something good."
                            : profile.data?.reviewed
                              ? "Ready for your next step."
                              : "Start with what you know."}
                        </h3>
                        <p>
                          {demo
                            ? "Career Readiness Estimate. A directional view, not a hiring probability."
                            : "Profile completeness measures setup progress, not your employability."}
                        </p>
                        <Link href={demo ? href("analytics") : "/onboarding"}>
                          View your profile <ArrowRight size={15} />
                        </Link>
                      </section>
                      <section className="panel gaps-panel">
                        <div className="section-title">
                          <h2>
                            {demo
                              ? "Small steps. Bigger possibilities."
                              : "Built on your evidence"}
                          </h2>
                        </div>
                        {demo ? (
                          <>
                            <p>Recurring gaps across 20 sample roles.</p>
                            {[
                              ["AWS", 70, "High priority"],
                              ["Docker", 60, "High priority"],
                              ["Kubernetes", 35, "Worth exploring"],
                            ].map(([skill, score, label]) => (
                              <div className="gap-row" key={skill}>
                                <div className="row space">
                                  <strong>{skill}</strong>
                                  <small>{label}</small>
                                </div>
                                <div className="progress-track">
                                  <span style={{ width: score + "%" }} />
                                </div>
                                <small>{score}% of sample roles</small>
                              </div>
                            ))}
                            <Link href={href("skills")}>
                              Explore skill intelligence{" "}
                              <ArrowRight size={15} />
                            </Link>
                          </>
                        ) : (
                          <>
                            <ShieldCheck className="green" size={30} />
                            <p>
                              We preserve source text, keep resume versions, and
                              let you reject incorrect extractions.
                            </p>
                            <span className="tag">
                              Local parser · No AI provider
                            </span>
                          </>
                        )}
                      </section>
                    </div>
                  </div>
                </>
              ) : section === "resume" ? (
                <section className="panel resume-studio">
                  <div className="section-title">
                    <div>
                      <h2>Master resume</h2>
                      <p>Your original document is always preserved.</p>
                    </div>
                    <Link
                      className="button"
                      href={demo ? "/sign-up" : "/onboarding"}
                    >
                      <Upload size={16} /> Upload resume
                    </Link>
                  </div>
                  {demo ? (
                    <div className="demo-resume">
                      <FileText size={40} />
                      <h3>Alex_Morgan_Resume.pdf</h3>
                      <p>Sample document · Illustrative profile only</p>
                      <div className="chips">
                        {["Python", "FastAPI", "RAG", "PostgreSQL"].map((s) => (
                          <span className="tag" key={s}>
                            {s}
                          </span>
                        ))}
                      </div>
                      <Link href="/sign-up">
                        Upload your own resume <ArrowRight size={16} />
                      </Link>
                    </div>
                  ) : profile.data?.resume ? (
                    <>
                      <div className="row">
                        <span className="file-icon">
                          <FileText />
                        </span>
                        <div>
                          <h3>{profile.data.resume.filename}</h3>
                          <p>
                            {profile.data.reviewed
                              ? "Profile review complete"
                              : "Awaiting your review"}{" "}
                            · Local evidence parser
                          </p>
                        </div>
                        <a
                          className="button secondary"
                          href={`/api/resume/${profile.data.resume.id}/download`}
                        >
                          Download original
                        </a>
                      </div>
                      <div className="source-panel">
                        <h3>Source text</h3>
                        <pre>{profile.data.resume.text}</pre>
                      </div>
                      <h3>Version history</h3>
                      {versions.data?.map((v) => (
                        <div className="version-row" key={v.id}>
                          <FileText size={18} />
                          <strong>{v.filename}</strong>
                          <span>
                            {new Date(v.created_at).toLocaleDateString()}
                          </span>
                          <a href={`/api/resume/${v.id}/download`}>Download</a>
                        </div>
                      ))}
                    </>
                  ) : (
                    <Empty
                      title="Your story starts here."
                      text="Upload your master resume to organize your skills, experience and projects."
                      href="/onboarding"
                      action="Upload master resume"
                    />
                  )}
                </section>
              ) : section === "profile" ? (
                <section className="panel">
                  <div className="section-title">
                    <h2>Your career profile</h2>
                    <Link
                      className="button secondary"
                      href={demo ? "/sign-up" : "/onboarding"}
                    >
                      Edit profile <ArrowUpRight size={16} />
                    </Link>
                  </div>
                  <div className="profile-details">
                    <span className="user-avatar">{name[0]}</span>
                    <h2>{demo ? "Alex Morgan" : user.data?.full_name}</h2>
                    <p>
                      {demo
                        ? "Fictional entry-level AI engineer"
                        : user.data?.email}
                    </p>
                    <div className="chips">
                      {(demo
                        ? ["AI Engineer", "GenAI Engineer"]
                        : profile.data?.preferences?.target_roles || []
                      ).map((r: string) => (
                        <span className="tag" key={r}>
                          {r}
                        </span>
                      ))}
                    </div>
                    <p>
                      {demo
                        ? "Bengaluru · Open to remote"
                        : profile.data?.personal?.location ||
                          "Location not set"}
                    </p>
                  </div>
                </section>
              ) : section === "settings" ? (
                <section className="panel">
                  <h2>Workspace settings</h2>
                  <div className="settings-row">
                    <div>
                      <strong>Appearance</strong>
                      <p>Choose a comfortable workspace theme.</p>
                    </div>
                    <button
                      className="button secondary"
                      onClick={() => {
                        localStorage.setItem(
                          "careerpilot-theme",
                          dark ? "light" : "dark",
                        );
                        setDark(!dark);
                      }}
                    >
                      {dark ? "Switch to light" : "Switch to dark"}
                    </button>
                  </div>
                  <div className="settings-row">
                    <div>
                      <strong>AI provider</strong>
                      <p>
                        Provider integration begins in Phase 4. Resume
                        extraction runs locally.
                      </p>
                    </div>
                    <span className="tag neutral">Not configured</span>
                  </div>
                  <div className="settings-row">
                    <div>
                      <strong>Resume privacy</strong>
                      <p>
                        Authenticated access. Private document storage.
                        Account-scoped evidence.
                      </p>
                    </div>
                    <ShieldCheck className="green" />
                  </div>
                </section>
              ) : section === "notifications" ? (
                <section className="panel">
                  <h2>Recent activity</h2>
                  {demo ? (
                    [
                      "Your sample resume is ready to review.",
                      "3 sample applications are awaiting review.",
                      "Docker appears in 12 of 20 sample roles.",
                    ].map((s) => (
                      <div className="activity-row" key={s}>
                        <Bell size={18} />
                        {s}
                        <span className="tag neutral">Demo</span>
                      </div>
                    ))
                  ) : notifications.data?.length ? (
                    notifications.data.map((n) => (
                      <div className="activity-row" key={n.id}>
                        <ShieldCheck size={18} />
                        <strong>{n.event.replaceAll(".", " · ")}</strong>
                        <small>{new Date(n.created_at).toLocaleString()}</small>
                      </div>
                    ))
                  ) : (
                    <Empty
                      title="A fresh start."
                      text="Your resume and profile activity will appear here."
                    />
                  )}
                </section>
          ) : section === "jobs" || section === "matches" ? (
                <section className="panel">
                  <div className="job-filters">
                    <div className="input-with-icon">
                      <Search size={18} />
                      <input
                        aria-label="Search sample jobs"
                        placeholder="Search roles or companies"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                      />
                    </div>
                    <select
                      aria-label="Filter jobs"
                      value={filter}
                      onChange={(e) => setFilter(e.target.value)}
                    >
                      {["All opportunities", "Remote only", "Saved"].map(
                        (s) => (
                          <option key={s}>{s}</option>
                        ),
                      )}
                    </select>
                    <Link className="button primary" href="/jobs">Browse real jobs ↗</Link>
                  </div>
              {demo ? (jobs.length ? (
                jobs.map((j) => (
                  <JobCard key={j.id} job={j} saved={saved.includes(j.id)} onSave={() => toggleSave(j.id)} onView={() => setSelected(j)} />
                ))
              ) : (
                <Empty title="No opportunities in this view." text="Try another search or filter." />
              )) : realJobs.data?.length ? realJobs.data.map((j) => (
                <article className="job-card" key={j.id}><span className="company-avatar mint">{j.company[0]}</span><div className="job-main"><span className="company-name">{j.company} · {j.source}</span><h3 className="job-title">{j.title}</h3><div className="job-meta"><span><MapPin size={12}/>{j.location}</span><span>{j.work_type}</span><span>{j.salary}</span></div><div className="chips">{j.requirements.required.map((s:string)=><span className="skill-chip" key={s}><Check size={11}/>{s}</span>)}</div></div><button className="button secondary" onClick={async()=>{await api(`/applications?job_id=${j.id}`,{method:"POST"});setToast("Saved to your applications.");realApplications.refetch()}}>Save</button></article>
              )) : (
                <Empty
                  title={demo ? "No opportunities in this view." : "No opportunities yet."}
                  text={demo ? "Try another search or filter." : "Your curated opportunity feed is ready. Try a different search."}
                />
              )}
            </section>
              ) : section === "interviews" && !demo ? (
                <MockInterviewPanel />
              ) : section === "skills" ? (
                <section className="panel">
                  <h2>Focus on the skills that keep coming up.</h2>
                  <p>
                    Illustrative analysis of 20 fictional jobs. These are not
                    personalized recommendations.
                  </p>
                  {[
                    ["AWS", 14],
                    ["Docker", 12],
                    ["Kubernetes", 7],
                  ].map(([skill, n]) => (
                    <div className="learning-row" key={skill}>
                      <div>
                        <h3>{skill}</h3>
                        <p>
                          Missing evidence in {n} of 20 sample opportunities
                        </p>
                      </div>
                      <div>
                        <strong>{Number(n) * 5}% demand frequency</strong>
                        <p>
                          Learn the fundamentals → apply to a real project →
                          update your resume with evidence.
                        </p>
                      </div>
                    </div>
                  ))}
                </section>
              ) : (
            <section className="panel">
              <Empty
                    title={
                      section === "assistant"
                        ? "A career partner, with context."
                        : section === "applications"
                          ? "Every application. One clear picture."
                          : section === "analytics"
                            ? "Insight starts with evidence."
                            : "Your next opportunity is ahead."
                    }
                    text={`${title} is planned for ${section === "assistant" ? "Phase 4" : section === "applications" ? "Phase 6" : section === "skills" ? "Phase 3" : section === "analytics" ? "Phase 8" : "Phase 2"}. ${demo ? "This preview does not run agents, retrieve live jobs, or submit applications." : "Your profile and resume foundation are available now."}`}
                    href={demo ? "/sign-up" : "/onboarding"}
                    action={
                      demo ? "Create your profile" : "Review your profile"
                    }
              />
            </section>
              )}
            </motion.div>
          )}
          <div className="workspace-footer">
            <span>
              <ShieldCheck size={13} /> Grounded in your experience. Guided by
              you.
            </span>
            <span>
              {demo
                ? "Interactive product preview"
                : "Phase 1 · Profile & resume foundation"}
            </span>
          </div>
        </main>
      </div>
      <Dialog.Root open={command} onOpenChange={setCommand}>
        <Dialog.Portal>
          <Dialog.Overlay className="modal-overlay" />
          <Dialog.Content className="command-modal">
            <Dialog.Title>Where would you like to go?</Dialog.Title>
            <Dialog.Description>
              Search workspace pages. Shortcut: Ctrl + K.
            </Dialog.Description>
            <input
              autoFocus
              aria-label="Search workspace pages"
              placeholder="Try resume, applications, skills…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="command-results">
              {navigation
                .filter((n) =>
                  n.label.toLowerCase().includes(search.toLowerCase()),
                )
                .map((n) => (
                  <Link
                    key={n.slug}
                    href={href(n.slug)}
                    onClick={() => {
                      setCommand(false);
                      setSearch("");
                    }}
                  >
                    {n.label}
                    <ArrowUpRight size={16} />
                  </Link>
                ))}
            </div>
            <Dialog.Close className="modal-close" aria-label="Close search">
              <X size={20} />
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
      <Dialog.Root
        open={!!selected}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
        }}
      >
        <Dialog.Portal>
          <Dialog.Overlay className="modal-overlay" />
          <Dialog.Content className="analysis-modal">
            <Dialog.Title>{selected?.role}</Dialog.Title>
            <Dialog.Description>
              {selected?.company} · Fictional opportunity
            </Dialog.Description>
            {selected && (
              <>
                <ScoreRing score={selected.score} large />
                <h3>Why this sample candidate matches</h3>
                <div className="chips">
                  {selected.skills.map((s) => (
                    <span className="tag" key={s}>
                      <Check size={13} />
                      {s}
                    </span>
                  ))}
                </div>
                <div className="notice">
                  Missing evidence: {selected.gap}. This illustrative score is
                  not calculated from your resume. The deterministic matching
                  engine is scheduled for Phase 2.
                </div>
                <button
                  className="button full"
                  onClick={() => toggleSave(selected.id)}
                >
                  <Bookmark size={16} />
                  {saved.includes(selected.id)
                    ? "Remove from sample shortlist"
                    : "Save to sample shortlist"}
                </button>
              </>
            )}
            <Dialog.Close className="modal-close" aria-label="Close analysis">
              <X size={20} />
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          {toast}
          <button
            aria-label="Dismiss notification"
            onClick={() => setToast("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
