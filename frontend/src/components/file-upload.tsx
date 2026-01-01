"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  X,
  FileText,
  Image as ImageIcon,
  File,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  accept?: string;
  maxSizeMB?: number;
  maxFiles?: number;
  className?: string;
}

export function FileUpload({
  onUpload,
  accept = "image/*,.pdf,.txt,.md,.doc,.docx",
  maxSizeMB = 5,
  maxFiles = 2,
  className,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): string | null => {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File size exceeds ${maxSizeMB}MB limit`;
    }
    // Validate type against accept list
    const tokens = accept.split(",").map((t) => t.trim().toLowerCase());
    const mime = (file.type || "").toLowerCase();
    const name = file.name.toLowerCase();

    const isAllowed = tokens.some((tok) => {
      if (!tok) return false;
      if (tok.endsWith("/*")) {
        const prefix = tok.slice(0, -2);
        return mime.startsWith(prefix + "/");
      }
      if (tok.startsWith(".")) {
        return name.endsWith(tok);
      }
      // exact mime type
      return mime === tok;
    });

    if (!isAllowed) {
      return "Unsupported file type";
    }
    return null;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    const files = Array.from(e.dataTransfer.files || []);
    if (!files.length) return;

    const next: File[] = [];
    for (const f of files) {
      const validationError = validateFile(f);
      if (validationError) {
        setError(validationError);
        continue;
      }
      next.push(f);
      if (selectedFiles.length + next.length >= maxFiles) break;
    }

    const combined = [...selectedFiles, ...next].slice(0, maxFiles);
    if (selectedFiles.length + files.length > maxFiles) {
      setError(`You can upload up to ${maxFiles} files`);
    }
    setSelectedFiles(combined);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setError(null);

    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    const next: File[] = [];
    for (const f of files) {
      const validationError = validateFile(f);
      if (validationError) {
        setError(validationError);
        continue;
      }
      next.push(f);
      if (selectedFiles.length + next.length >= maxFiles) break;
    }

    const combined = [...selectedFiles, ...next].slice(0, maxFiles);
    if (selectedFiles.length + files.length > maxFiles) {
      setError(`You can upload up to ${maxFiles} files`);
    }
    setSelectedFiles(combined);
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;

    setUploading(true);
    setError(null);

    try {
      for (const f of selectedFiles) {
        await onUpload(f);
      }
      setSelectedFiles([]);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith("image/")) {
      return <ImageIcon className="w-8 h-8 text-blue-400" />;
    } else if (file.type.includes("pdf")) {
      return <FileText className="w-8 h-8 text-red-400" />;
    }
    return <File className="w-8 h-8 text-gray-400" />;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className={cn("w-full", className)}>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        multiple
        onChange={handleChange}
        disabled={uploading}
      />

      <div
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 transition-all",
          dragActive
            ? "border-primary bg-primary/10"
            : "border-border hover:border-primary/50",
          uploading && "opacity-50 pointer-events-none"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <AnimatePresence mode="wait">
          {selectedFiles.length ? (
            <motion.div
              key="file-selected"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="space-y-2">
                {selectedFiles.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-4 p-4 bg-background/50 rounded-lg"
                  >
                    {getFileIcon(file)}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        const next = selectedFiles.filter((_, i) => i !== idx);
                        setSelectedFiles(next);
                        if (inputRef.current && next.length === 0) {
                          inputRef.current.value = "";
                        }
                      }}
                      disabled={uploading}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>

              <Button
                onClick={handleUpload}
                disabled={uploading}
                className="w-full gap-2 gradient-primary text-white"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    {selectedFiles.length === 1
                      ? "Upload 1 file"
                      : `Upload ${selectedFiles.length} files`}
                  </>
                )}
              </Button>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center space-y-4"
            >
              <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">
                  Drop files here or click to upload
                </h3>
                <p className="text-sm text-muted-foreground">
                  Supports images, PDFs, and text documents (max {maxSizeMB}MB,
                  up to {maxFiles} files)
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => inputRef.current?.click()}
                className="gap-2"
              >
                <Upload className="w-4 h-4" />
                Browse Files
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-destructive mt-2"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
}
