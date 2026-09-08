"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
type Job = {id:string; title:string; company:string; location:string; work_type:string; description:string; url:string; posted_at:string};
export default function LiveJobs() {
  const [filters,setFilters]=useState({q:"",location:"",remote:false,page:1});
  const [message,setMessage]=useState("");
  const [savedSuccessfully,setSavedSuccessfully]=useState(false);
  const [busy,setBusy]=useState("");
  useEffect(()=>{
    if (!message || !savedSuccessfully) return;
    const timer=window.setTimeout(()=>setMessage(""),3000);
    return ()=>window.clearTimeout(timer);
  },[message,savedSuccessfully]);
  const jobs=useQuery<{results:Job[];has_more:boolean;fetched_at:string;stale:boolean}>({
    queryKey:["public-jobs",filters],
    queryFn:()=>api("/jobs/search/live?"+new URLSearchParams({q:filters.q,location:filters.location,remote:String(filters.remote),page:String(filters.page)})),
    staleTime:60000,retry:1
  });
  async function save(id:string) {
    setBusy(id);setMessage("");setSavedSuccessfully(false);
    try {await api("/applications?job_id="+id,{method:"POST"});setSavedSuccessfully(true);setMessage("This job has been saved in Job Saved.");}
    catch(e){setMessage(e instanceof Error?e.message:"Unable to save. Sign in and upload a resume first.");}
    finally{setBusy("");}
  }
  return <main style={{maxWidth:1100,margin:"auto",padding:"40px 24px"}}>
    <nav style={{display:"flex",gap:24,marginBottom:32}}><Link href="/">CareerPilot AI</Link><Link href="/sign-in">Sign in</Link><Link href="/jobs/saved">Job Saved</Link></nav>
    <span className="tag neutral">REAL JOBS · ARBEITNOW</span>
    <h1 style={{fontSize:"clamp(32px,5vw,54px)",margin:"16px 0"}}>Find your next opportunity.</h1>
    <p>Browse without an account. Sign in and upload a resume to save applications. This feed primarily covers Europe; remote roles may have location restrictions.</p>
    <form className="job-filters" style={{margin:"24px 0",flexWrap:"wrap"}} onSubmit={e=>{
      e.preventDefault();const data=new FormData(e.currentTarget);
      setFilters({q:String(data.get("q")||""),location:String(data.get("location")||""),remote:data.get("remote")==="on",page:1});
    }}>
      <label>Role or keyword<input name="q" placeholder="Python, engineer, design" maxLength={120}/></label>
      <label>Location<input name="location" placeholder="Berlin, Germany…" maxLength={120}/></label>
      <label><input name="remote" type="checkbox"/> Remote only</label>
      <button className="button primary">Search</button>
    </form>
    <p>Filters apply to the current source page. Use Next to explore more listings.</p>
    {message&&<aside aria-label="Application save notification" style={{position:"fixed",top:"50%",left:"50%",transform:"translate(-50%, -50%)",zIndex:1000,width:"min(390px, calc(100vw - 48px))",padding:20,borderRadius:16,background:savedSuccessfully?"#143e32":"#512c28",color:"#fff",boxShadow:"0 12px 40px #0003",border:"1px solid #ffffff33"}}>
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:16}}>
        <strong>{savedSuccessfully?"✓ Job saved":"Unable to save job"}</strong>
        <button type="button" aria-label="Dismiss notification" onClick={()=>setMessage("")} style={{background:"transparent",border:0,color:"#fff",fontSize:24,cursor:"pointer",minWidth:44,minHeight:44}}>×</button>
      </div>
      <p role={savedSuccessfully?"status":"alert"} style={{margin:"8px 0",color:"#fff"}}>{message}</p>
      {savedSuccessfully&&<p style={{fontSize:13,margin:0,color:"#e1eee8"}}>Saved for tracking. No application has been sent to the employer.</p>}
    </aside>}
    {jobs.isFetching&&<p role="status">Loading opportunities…</p>}
    {jobs.error&&<div role="alert">{jobs.error.message} <button className="button secondary" onClick={()=>jobs.refetch()}>Retry</button></div>}
    {jobs.data&&<><p>{jobs.data.results.length} results · Retrieved {new Date(jobs.data.fetched_at).toLocaleString()}{jobs.data.stale?" · Source unavailable: showing cached data":""}</p>
      {!jobs.data.results.length&&<section className="panel">No matches on this page. Broaden your search or try the next page.</section>}
      {jobs.data.results.map(job=><article className="panel" key={job.id} style={{margin:"16px 0"}}>
        <p>{job.company} · {job.location} · {job.work_type==="remote"?"Remote":"Work arrangement not specified"}</p>
        <h2>{job.title}</h2><p>Posted {new Date(job.posted_at).toLocaleDateString()} · Salary not provided</p>
        <details><summary>Read job description</summary><p style={{whiteSpace:"pre-wrap"}}>{job.description}</p></details>
        <div style={{display:"flex",gap:12,marginTop:16,flexWrap:"wrap"}}><a className="button primary" href={job.url} target="_blank" rel="noopener noreferrer">View on Arbeitnow ↗</a>
          <button className="button secondary" disabled={!!busy} onClick={()=>save(job.id)}>{busy===job.id?"Saving…":"Save application"}</button></div>
      </article>)}
      <div style={{display:"flex",gap:16,alignItems:"center"}}><button className="button secondary" disabled={filters.page===1||jobs.isFetching} onClick={()=>setFilters({...filters,page:filters.page-1})}>Previous</button><span>Page {filters.page}</span><button className="button secondary" disabled={!jobs.data.has_more||jobs.isFetching} onClick={()=>setFilters({...filters,page:filters.page+1})}>Next</button></div>
    </>}
  </main>;
}
