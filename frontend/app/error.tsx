"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="empty-state" style={{ minHeight: "80dvh" }}>
      <h1>Let�s try that again.</h1>
      <p>
        Something interrupted this page. Your saved profile remains in your
        account.
      </p>
      <button className="button" onClick={reset}>
        Retry page
      </button>
    </main>
  );
}
