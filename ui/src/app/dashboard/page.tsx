"use client";
import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { FileText, Upload, Eye, MessageSquare, Trash } from "lucide-react";

interface UploadedFile {
  id: string;
  fileName: string;
  path: string;
  fileStatus: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    try {
      const res = await apiClient.get("/api/file/list");
      setFiles(res.data);
    } catch (err) {
      console.error("Failed to fetch files", err);
    }
  };

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    fetchFiles();
    
    // Poll every 5 seconds if any file is in PROCESSING or PENDING state
    const interval = setInterval(() => {
      setFiles(currentFiles => {
        const needsPolling = currentFiles.some(f => f.fileStatus === 'PROCESSING' || f.fileStatus === 'PENDING');
        if (needsPolling) {
          fetchFiles();
        }
        return currentFiles;
      });
    }, 5000);
    
    return () => clearInterval(interval);
  }, [router]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await apiClient.post("/api/file/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // Wait a bit for processing before refreshing
      setTimeout(fetchFiles, 2000);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const viewFile = async (fileName: string) => {
    try {
      const res = await apiClient.post(`/api/file/getfile?filename=${encodeURIComponent(fileName)}`);
      if (res.data && res.data.url) {
        window.open(res.data.url, "_blank");
      }
    } catch (err) {
      console.error("Failed to view file", err);
      alert("Could not view file");
    }
  };

  const deleteFile = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document? All related chat history will also be deleted.")) return;
    try {
      await apiClient.delete(`/api/file/${id}`);
      fetchFiles();
    } catch (err) {
      console.error("Failed to delete file", err);
      alert("Could not delete file");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUCCESS': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'FAILED': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      case 'PROCESSING': return 'text-amber-400 bg-amber-400/10 border-amber-400/20 animate-pulse';
      default: return 'text-slate-300 bg-slate-800 border-slate-700';
    }
  };

  return (
    <>
      <Navbar />
      <main className="flex-1 p-6 lg:p-12 max-w-6xl mx-auto w-full">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-heading font-bold text-slate-50">My Documents</h1>
            <p className="text-slate-400 mt-1">Upload and query your PDFs.</p>
          </div>
          <div>
            <input type="file" accept="application/pdf" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
            <Button onClick={handleUploadClick} disabled={uploading} className="gap-2">
              <Upload size={16} /> {uploading ? "Uploading..." : "Upload PDF"}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {files.length === 0 ? (
            <div className="col-span-full py-12 text-center text-slate-500 border border-dashed border-slate-700 rounded-xl bg-slate-900/20">
              No documents found. Upload a PDF to get started!
            </div>
          ) : (
            files.map((file) => (
              <Card key={file.id} className="flex flex-col hover:border-indigo-500/50 transition-colors">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg flex items-start gap-3">
                    <FileText className="text-indigo-400 shrink-0 mt-1" size={20} />
                    <span className="truncate" title={file.fileName}>{file.fileName}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className={`text-xs inline-flex items-center px-2.5 py-1 rounded-full border ${getStatusColor(file.fileStatus)}`}>
                    Status: {file.fileStatus}
                  </div>
                </CardContent>
                <CardFooter className="flex gap-2 pt-0 flex-wrap">
                  <Button variant="outline" size="sm" className="flex-1 gap-1" onClick={() => viewFile(file.fileName)}>
                    <Eye size={14} /> View
                  </Button>
                  <Button size="sm" className="flex-1 gap-1" onClick={() => router.push(`/query/${file.id}`)} disabled={file.fileStatus !== 'SUCCESS'}>
                    <MessageSquare size={14} /> Chat
                  </Button>
                  <Button variant="destructive" size="sm" className="w-full mt-2 gap-2 bg-rose-500/20 text-rose-400 hover:bg-rose-500/40 hover:text-rose-300 border border-rose-500/20" onClick={() => deleteFile(file.id)}>
                    <Trash size={14} /> Delete
                  </Button>
                </CardFooter>
              </Card>
            ))
          )}
        </div>
      </main>
    </>
  );
}
