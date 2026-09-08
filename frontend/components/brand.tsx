import { Navigation } from "lucide-react";
export function Brand() {
  return (
    <span className="brand">
      <span className="brand-mark">
        <Navigation size={23} fill="currentColor" />
      </span>
      CareerPilot<span className="brand-ai">AI</span>
    </span>
  );
}
