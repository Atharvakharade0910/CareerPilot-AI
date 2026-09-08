import { Workspace } from "@/components/workspace";
export default async function Page({
  params,
}: {
  params: Promise<{ section?: string[] }>;
}) {
  const { section } = await params;
  return <Workspace demo section={section?.[0] || "dashboard"} />;
}
