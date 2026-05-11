import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/Button";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="flex flex-1 flex-col items-center justify-center px-4 text-center">
        <h1 className="font-heading text-5xl sm:text-7xl font-bold tracking-tight mb-6">
          Unleash Your <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-violet-400">Documents</span>
        </h1>
        <p className="max-w-2xl text-lg sm:text-xl text-slate-400 mb-10">
          Upload your PDFs and instantly ask questions. Powered by advanced RAG and state-of-the-art Large Language Models.
        </p>
        <div className="flex gap-4">
          <Link href="/register">
            <Button size="lg" className="px-8">Get Started</Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg" className="px-8">Login</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
