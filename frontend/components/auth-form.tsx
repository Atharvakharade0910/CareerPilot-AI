"use client";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  ArrowRight,
  ShieldCheck,
  Eye,
  EyeOff,
  LoaderCircle,
  ArrowLeft,
} from "lucide-react";
import { Brand } from "./brand";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
const schema = z.object({
  full_name: z.string().optional(),
  gender: z.string().optional(),
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(10, "Use at least 10 characters.").max(128),
});
type Values = z.infer<typeof schema>;
export function AuthForm({
  mode,
}: {
  mode: "sign-in" | "sign-up" | "forgot-password";
}) {
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);
  const router = useRouter();
  const [error, setError] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema) });
  const signup = mode === "sign-up",
    forgot = mode === "forgot-password";
  async function submit(data: Values) {
    setBusy(true);
    setError("");
    try {
      if (signup && (!data.full_name || data.full_name.trim().length < 2))
        throw new Error("Please enter your full name.");
      await api("/auth/" + (signup ? "register" : "login"), {
        method: "POST",
        body: JSON.stringify(data),
      });
      router.push(signup ? "/onboarding" : "/dashboard");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="auth-layout">
      <aside className="auth-story">
        <Link href="/">
          <Brand />
        </Link>
        <div>
          <span className="eyebrow">A CAREER THAT FEELS LIKE YOU</span>
          <h1>
            Great things start
            <br />
            with a little
            <br />
            <span>direction.</span>
          </h1>
          <p>
            Your experience is more than a list of keywords. Let’s give it a
            clear, confident story.
          </p>
          <div className="auth-path">
            Discover <ArrowRight /> Match <ArrowRight /> Improve
          </div>
        </div>
        <span className="row">
          <ShieldCheck size={18} /> Private by design. Grounded in your resume.
        </span>
      </aside>
      <section className="auth-form-wrap">
        <Link href="/" className="back-link">
          <ArrowLeft size={16} /> Back to home
        </Link>
        <div className="auth-form">
          <span className="eyebrow">YOUR NEXT CHAPTER</span>
          <h2>
            {forgot
              ? "Let’s get you back in."
              : signup
                ? "Find your direction."
                : "Welcome back."}
          </h2>
          <p>
            {forgot
              ? "Password recovery needs a configured email service."
              : signup
                ? "Create your personal career workspace."
                : "Your next opportunity starts where you left off."}
          </p>
          {forgot ? (
            <>
              <div className="notice">
                Email delivery is not configured in this Phase 1 installation.
                Contact your deployment administrator to recover access. No
                reset email has been sent.
              </div>
              <Link className="button" href="/sign-in">
                Return to sign in <ArrowRight size={18} />
              </Link>
            </>
          ) : (
            <form method="post" onSubmit={handleSubmit(submit)}>
              {signup && (
                <label>
                  Full name
                  <input
                    autoComplete="name"
                    placeholder="Your full name"
                    {...register("full_name")}
                  />
                </label>
              )}
              {signup && (
                <label>
                  Gender <span className="muted">(optional)</span>
                  <select defaultValue="prefer_not_to_say" {...register("gender")}>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                    <option value="woman">Woman</option>
                    <option value="man">Man</option>
                    <option value="non_binary">Non-binary</option>
                    <option value="self_describe">Prefer to self-describe</option>
                  </select>
                </label>
              )}
              <label>
                Email address
                <input
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  {...register("email")}
                />
                {errors.email && (
                  <span className="field-error">{errors.email.message}</span>
                )}
              </label>
              <label>
                Password
                <div className="password-input">
                  <input
                    type={show ? "text" : "password"}
                    autoComplete={signup ? "new-password" : "current-password"}
                    placeholder="At least 10 characters"
                    {...register("password")}
                  />
                  <button
                    type="button"
                    aria-label={show ? "Hide password" : "Show password"}
                    onClick={() => setShow(!show)}
                  >
                    {show ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                {errors.password && (
                  <span className="field-error">{errors.password.message}</span>
                )}
              </label>
              {!signup && (
                <Link className="forgot" href="/forgot-password">
                  Forgot password?
                </Link>
              )}
              {error && (
                <div className="error" role="alert">
                  {error}
                </div>
              )}
              <Button className="button full" disabled={busy || !ready}>
                {busy ? (
                  <LoaderCircle className="spin" size={18} />
                ) : (
                  <>
                    {signup ? "Create your account" : "Sign in"}
                    <ArrowRight size={18} />
                  </>
                )}
              </Button>
              {signup && <p className="form-note">By creating an account, you agree to our <Link href="/terms">Terms</Link> and acknowledge our <Link href="/privacy">Privacy policy</Link>.</p>}
              <p className="auth-switch">
                {signup ? "Already have an account?" : "New to CareerPilot?"}{" "}
                <Link href={signup ? "/sign-in" : "/sign-up"}>
                  {signup ? "Sign in" : "Create an account"}
                </Link>
              </p>
            </form>
          )}
          <div className="auth-demo">
            <span>Just taking a look?</span>
            <Link href="/demo">
              Explore the demo <ArrowUp />
            </Link>
          </div>
        </div>
        <small className="auth-foot">
          Your resume is stored privately and only accessible to your account.
        </small>
      </section>
    </main>
  );
}
function ArrowUp() {
  return <ArrowRight size={15} />;
}
