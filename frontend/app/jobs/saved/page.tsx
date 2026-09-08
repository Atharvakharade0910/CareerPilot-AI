"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
type SavedJob={application_id:string;saved_at:string;status:string;job:{id:string;title:string;company:string;location:string;url:string}};
export default function SavedJobs(){
  const saved=useQuery<SavedJob[]>({queryKey:["saved-jobs"],queryFn:()=>api("/saved-jobs"),retry:false,refetchOnMount:"always"});
  return <main style={{maxWidth:1000,margin:"auto",padding:"40px 24px"}}>
    <Link href="/jobs">← Browse opportunities</Link>
    <h1 style={{margin:"24px 0"}}>Job Saved</h1>
    <p>Your saved opportunities are stored in your CareerPilot account.</p>
    {saved.isLoading&&<p role="status">Loading saved jobs…</p>}
    {saved.error&&<div role="alert"><p>{saved.error.message}</p><Link className="button primary" href="/sign-in">Sign in</Link><button className="button secondary" onClick={()=>saved.refetch()}>Retry</button></div>}
    {saved.data?.length===0&&<section className="panel"><h2>No saved jobs yet</h2><p>Choose Save application on an opportunity to add it here.</p><Link href="/jobs">Find jobs</Link></section>}
    {saved.data?.map(item=><article className="panel" key={item.application_id} style={{margin:"16px 0"}}>
      <h2>{item.job.title}</h2><p>{item.job.company} · {item.job.location}</p>
      <p>Saved {new Date(item.saved_at).toLocaleString()} · {item.status}</p>
      {item.job.url.startsWith("https://")&&<a className="button primary" href={item.job.url} target="_blank" rel="noopener noreferrer">View original listing ↗</a>}
    </article>)}
  </main>;
}
