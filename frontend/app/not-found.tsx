import Link from "next/link";
import { Brand } from "@/components/brand";
export default function NotFound() {
  return (
    <main className="empty-state" style={{ minHeight: "100dvh" }}>
      <Brand />
      <h1 style={{ marginTop: 30 }}>A small detour.</h1>
      <p>This page isn�t on the map. Let�s get you back to your workspace.</p>
      <Link className="button" href="/">
        Back to CareerPilot
      </Link>
    </main>
  );
}
