"use client";

import { useState, useEffect } from "react";
import { useUser, useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import {
  Plus,
  Folder,
  Trash2,
  History,
  TrendingUp,
  Zap,
  Award,
  Upload as UploadIcon,
} from "lucide-react";
import { Header } from "@/components/header";
import { PromptOptimizer } from "@/components/prompt-optimizer";
import { FileUpload } from "@/components/file-upload";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, type Project, type PromptHistoryItem } from "@/lib/api";
import { toast } from "sonner";

export default function DashboardPage() {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();

  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [history, setHistory] = useState<PromptHistoryItem[]>([]);
  const [historyLimit, setHistoryLimit] = useState<number>(5);
  const [newProjectName, setNewProjectName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<
    Array<{ filename: string; storage_path: string; uploaded_at: string }>
  >([]);

  // Set API token when user is loaded
  useEffect(() => {
    async function setToken() {
      if (user) {
        const token = await getToken();
        api.setToken(token);
        // Set token refresh callback for automatic token renewal
        api.setTokenRefreshCallback(async () => {
          const newToken = await getToken();
          return newToken;
        });
      }
    }
    setToken();
  }, [user, getToken]);

  // Load projects with retry logic for token timing issues
  useEffect(() => {
    async function loadProjects(retryCount = 0) {
      if (!user) return;

      try {
        // Add delay to handle JWT timing issues - increase on retries
        await new Promise((resolve) =>
          setTimeout(resolve, 1000 + retryCount * 1000)
        );

        // Ensure token is set before making API call
        const token = await getToken();
        api.setToken(token);

        const response = await api.listProjects();
        setProjects(response.projects);
      } catch (error) {
        console.error("Failed to load projects:", error);

        // Retry on token timing errors (up to 2 retries)
        if (
          error instanceof Error &&
          (error.message.includes("iat") || error.message.includes("token")) &&
          retryCount < 2
        ) {
          console.log(`Retrying loadProjects... attempt ${retryCount + 2}`);
          return loadProjects(retryCount + 1);
        }

        // Only show error for non-auth errors
        if (
          error instanceof Error &&
          !error.message.includes("Authentication") &&
          !error.message.includes("token") &&
          !error.message.includes("iat")
        ) {
          toast.error("Failed to load projects");
        }
      } finally {
        setIsLoadingProjects(false);
      }
    }

    if (isLoaded && user) {
      loadProjects();
    } else if (isLoaded) {
      setIsLoadingProjects(false);
    }
  }, [user, isLoaded, getToken]);

  // Load global history for user with limit
  useEffect(() => {
    async function loadGlobalHistory() {
      if (!user) {
        setHistory([]);
        return;
      }

      setIsLoadingHistory(true);
      try {
        const response = await api.getHistory(historyLimit);
        setHistory(response.history);
      } catch (error) {
        console.error("Failed to load history:", error);
        toast.error("Failed to load history");
      } finally {
        setIsLoadingHistory(false);
      }
    }

    loadGlobalHistory();
  }, [user, historyLimit]);

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    setIsCreating(true);
    try {
      // Ensure we have a fresh token
      const token = await getToken();
      api.setToken(token);

      const project = await api.createProject(newProjectName.trim());
      setProjects([project, ...projects]);
      setNewProjectName("");
      setSelectedProject(project);
      toast.success("Project created successfully");
    } catch (error) {
      console.error("Failed to create project:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Failed to create project";
      toast.error(errorMessage);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      // Ensure we have a fresh token
      const token = await getToken();
      api.setToken(token);

      await api.deleteProject(projectId);
      setProjects(projects.filter((p) => p.id !== projectId));
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
      }
      toast.success("Project deleted");
    } catch (error) {
      console.error("Failed to delete project:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete project";
      toast.error(errorMessage);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!selectedProject) {
      toast.error("Please select a project first");
      throw new Error("No project selected");
    }

    try {
      // Ensure we have a fresh token
      const token = await getToken();
      api.setToken(token);

      const result = await api.uploadContextFile(selectedProject.id, file);

      setUploadedFiles([
        {
          filename: result.filename,
          storage_path: result.storage_path,
          uploaded_at: new Date().toISOString(),
        },
        ...uploadedFiles,
      ]);

      toast.success(`${file.name} uploaded successfully`);
    } catch (error) {
      console.error("Failed to upload file:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Failed to upload file";
      toast.error(errorMessage);
      throw error;
    }
  };

  // Calculate stats
  const totalPrompts = history.length;
  const avgScore =
    history.length > 0
      ? Math.round(
          history.reduce((sum, h) => sum + h.score, 0) / history.length
        )
      : 0;
  const mostUsedAgent =
    history.length > 0
      ? history.reduce((acc, h) => {
          acc[h.agent_used] = (acc[h.agent_used] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      : {};
  const favoriteAgent =
    Object.keys(mostUsedAgent).length > 0
      ? Object.entries(mostUsedAgent).sort((a, b) => b[1] - a[1])[0][0]
      : "None";

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center dark mesh-gradient">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center space-y-4"
        >
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading...</p>
        </motion.div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen flex-col dark">
        <Header />
        <main className="flex-1 mesh-gradient flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-strong rounded-xl p-12 text-center max-w-md"
          >
            <h1 className="text-3xl font-bold mb-4">Sign In Required</h1>
            <p className="text-muted-foreground">
              Please sign in to access your dashboard and projects.
            </p>
          </motion.div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col dark">
      <Header />

      <main className="flex-1 mesh-gradient">
        <div className="page-center">
          <div className="page-inner py-4 sm:py-6 md:py-8">
            {/* Welcome Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 sm:mb-6 md:mb-8"
            >
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-1 sm:mb-2">
                Welcome back, {user.firstName || "User"}! 👋
              </h1>
              <p className="text-sm sm:text-base text-muted-foreground">
                {selectedProject
                  ? `Working on: ${selectedProject.name}`
                  : "Select a project or create one to get started."}
              </p>
            </motion.div>

            {/* Stats Cards */}
            {selectedProject && history.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6 sm:mb-8"
              >
                <div className="glass-strong rounded-xl p-4 sm:p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 sm:p-3 rounded-lg bg-blue-500/20">
                      <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        Total Prompts
                      </p>
                      <p className="text-xl sm:text-2xl font-bold">
                        {totalPrompts}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="glass-strong rounded-xl p-4 sm:p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 sm:p-3 rounded-lg bg-green-500/20">
                      <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        Avg Score
                      </p>
                      <p className="text-xl sm:text-2xl font-bold">
                        {avgScore}/100
                      </p>
                    </div>
                  </div>
                </div>

                <div className="glass-strong rounded-xl p-4 sm:p-6 sm:col-span-2 lg:col-span-1">
                  <div className="flex items-center gap-3">
                    <div className="p-2 sm:p-3 rounded-lg bg-purple-500/20">
                      <Award className="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        Favorite Agent
                      </p>
                      <p className="text-xl sm:text-2xl font-bold capitalize">
                        {favoriteAgent}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Main Content */}
            <Tabs defaultValue="optimize" className="space-y-4 sm:space-y-6">
              <TabsList className="glass-strong border-0 p-1 inline-flex mx-auto justify-center overflow-x-auto sm:overflow-visible">
                <TabsTrigger
                  value="optimize"
                  className="data-[state=active]:bg-primary/20 flex-1 sm:flex-initial text-xs sm:text-sm"
                >
                  Optimize
                </TabsTrigger>
                <TabsTrigger
                  value="projects"
                  className="data-[state=active]:bg-primary/20 flex-1 sm:flex-initial text-xs sm:text-sm"
                >
                  Projects
                </TabsTrigger>
                <TabsTrigger
                  value="history"
                  className="data-[state=active]:bg-primary/20 flex-1 sm:flex-initial text-xs sm:text-sm"
                >
                  History
                </TabsTrigger>
              </TabsList>

              {/* Optimize Tab */}
              <TabsContent value="optimize" className="space-y-6">
                {/* Quick Actions Bar - Always visible */}
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-strong rounded-xl p-4"
                >
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-linear-to-br from-blue-500 to-cyan-500">
                        <Folder className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">
                          {selectedProject ? (
                            <>
                              Working on:{" "}
                              <span className="text-primary">
                                {selectedProject.name}
                              </span>
                            </>
                          ) : (
                            "No project selected"
                          )}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {selectedProject
                            ? "Your prompts will be saved to this project"
                            : "Select a project in the Projects tab to save your work"}
                        </p>
                      </div>
                      {selectedProject && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-xs text-muted-foreground hover:text-foreground"
                          onClick={() => setSelectedProject(null)}
                        >
                          Clear
                        </Button>
                      )}
                    </div>

                    {/* File Upload Button - Only when project selected */}
                    {selectedProject && (
                      <div className="flex items-center gap-2 w-full sm:w-auto">
                        <input
                          type="file"
                          id="context-file-upload"
                          className="hidden"
                          accept="image/*,.pdf,.txt,.md,.doc,.docx"
                          multiple
                          onChange={async (e) => {
                            const files = Array.from(e.target.files || []);
                            if (files.length) {
                              const maxFiles = 2;
                              const selected = files.slice(0, maxFiles);
                              if (files.length > maxFiles) {
                                toast.error(
                                  `You can upload up to ${maxFiles} files at a time`
                                );
                              }
                              for (const file of selected) {
                                try {
                                  await handleFileUpload(file);
                                } catch {
                                  // Error already handled in handleFileUpload
                                }
                              }
                              e.target.value = "";
                            }
                          }}
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          className="gap-2 border-white/10 hover:bg-white/5 w-full sm:w-auto"
                          onClick={() =>
                            document
                              .getElementById("context-file-upload")
                              ?.click()
                          }
                        >
                          <UploadIcon className="h-4 w-4" />
                          <span className="hidden xs:inline">
                            Add Context Files
                          </span>
                          <span className="xs:hidden">Add Files</span>
                        </Button>
                        {uploadedFiles.length > 0 && (
                          <Badge variant="secondary" className="text-xs">
                            {uploadedFiles.length} file
                            {uploadedFiles.length !== 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Uploaded Files Preview */}
                  {uploadedFiles.length > 0 && selectedProject && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-4 pt-4 border-t border-white/10"
                    >
                      <p className="text-xs text-muted-foreground mb-2">
                        Context Files:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {uploadedFiles.map((file, index) => (
                          <Badge
                            key={index}
                            variant="outline"
                            className="text-xs gap-1 border-green-500/30 text-green-400"
                          >
                            <UploadIcon className="w-3 h-3" />
                            {file.filename.length > 20
                              ? file.filename.substring(0, 17) + "..."
                              : file.filename}
                          </Badge>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </motion.div>

                <PromptOptimizer
                  projectId={selectedProject?.id}
                  onResult={() => {
                    api.getHistory(historyLimit).then((response) => {
                      setHistory(response.history);
                    });
                  }}
                />
              </TabsContent>

              {/* Projects Tab */}
              <TabsContent value="projects">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {/* Create New Project Card */}
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="glass-strong rounded-xl p-4 sm:p-6 border-2 border-dashed border-white/10 hover:border-primary/30 transition-colors"
                  >
                    <div className="space-y-3 sm:space-y-4">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <Plus className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold mb-2 text-sm sm:text-base">
                          Create Project
                        </h3>
                        <Input
                          placeholder="Project name"
                          value={newProjectName}
                          onChange={(e) => setNewProjectName(e.target.value)}
                          onKeyDown={(e) =>
                            e.key === "Enter" && handleCreateProject()
                          }
                          className="mb-2 bg-background/50 border-white/10 text-sm"
                        />
                        <Button
                          onClick={handleCreateProject}
                          disabled={isCreating || !newProjectName.trim()}
                          className="w-full gradient-primary text-white border-0 text-sm"
                          size="sm"
                        >
                          {isCreating ? "Creating..." : "Create"}
                        </Button>
                      </div>
                    </div>
                  </motion.div>

                  {/* Project Cards */}
                  {isLoadingProjects ? (
                    <div className="glass-strong rounded-xl p-6 sm:p-8 flex items-center justify-center col-span-full">
                      <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : projects.length === 0 ? (
                    <div className="glass-strong rounded-xl p-6 sm:p-8 text-center col-span-full sm:col-span-1">
                      <Folder className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                      <p className="text-sm text-muted-foreground">
                        No projects yet. Create your first one!
                      </p>
                    </div>
                  ) : (
                    projects.map((project) => (
                      <motion.div
                        key={project.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() =>
                          setSelectedProject(
                            selectedProject?.id === project.id ? null : project
                          )
                        }
                        className={`glass-strong rounded-xl p-4 sm:p-6 cursor-pointer transition-all group ${
                          selectedProject?.id === project.id
                            ? "ring-2 ring-primary shadow-lg shadow-primary/20"
                            : "hover:shadow-lg active:shadow-md"
                        }`}
                      >
                        <div className="flex items-start justify-between mb-3 sm:mb-4">
                          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-linear-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                            <Folder className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity h-8 w-8"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteProject(project.id);
                            }}
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
                        </div>
                        <h3 className="font-semibold text-base sm:text-lg mb-1 truncate">
                          {project.name}
                        </h3>
                        <p className="text-xs sm:text-sm text-muted-foreground">
                          Created{" "}
                          {project.created_at
                            ? new Date(project.created_at).toLocaleDateString()
                            : "Unknown"}
                        </p>
                        {selectedProject?.id === project.id && (
                          <Badge className="mt-2 text-xs" variant="secondary">
                            Selected (click to deselect)
                          </Badge>
                        )}
                      </motion.div>
                    ))
                  )}
                </div>
              </TabsContent>

              {/* History Tab */}
              <TabsContent value="history">
                {isLoadingHistory ? (
                  <div className="glass-strong rounded-xl p-8 sm:p-12 text-center">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3 sm:mb-4" />
                    <p className="text-sm text-muted-foreground">
                      Loading history...
                    </p>
                  </div>
                ) : history.length === 0 ? (
                  <div className="glass-strong rounded-xl p-8 sm:p-12 text-center">
                    <History className="w-12 h-12 sm:w-16 sm:h-16 text-muted-foreground mx-auto mb-3 sm:mb-4" />
                    <h3 className="text-base sm:text-lg font-semibold mb-2">
                      No History Yet
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Start optimizing prompts to build your history
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-3 sm:gap-4">
                    {history.map((item, index) => (
                      <motion.div
                        key={item.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="glass-strong rounded-xl p-4 sm:p-6"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2 sm:gap-3">
                            <div
                              className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center text-lg sm:text-xl font-bold ${
                                item.score >= 80
                                  ? "bg-green-500/20 text-green-400"
                                  : item.score >= 60
                                  ? "bg-yellow-500/20 text-yellow-400"
                                  : "bg-red-500/20 text-red-400"
                              }`}
                            >
                              {item.score}
                            </div>
                            <div>
                              <Badge className="mb-1 capitalize text-xs">
                                {item.agent_used}
                              </Badge>
                              <p className="text-xs text-muted-foreground">
                                {item.created_at
                                  ? new Date(item.created_at).toLocaleString()
                                  : "Unknown"}
                              </p>
                            </div>
                          </div>
                        </div>
                        <p className="text-xs sm:text-sm leading-relaxed line-clamp-3 text-muted-foreground">
                          {item.prompt_text}
                        </p>
                      </motion.div>
                    ))}
                    <div className="flex justify-center mt-2">
                      {historyLimit < 10 ? (
                        <Button
                          variant="outline"
                          size="sm"
                          className="border-white/10 hover:bg-white/5"
                          onClick={() => setHistoryLimit(10)}
                        >
                          See more
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          className="border-white/10 hover:bg-white/5"
                          onClick={() => setHistoryLimit(5)}
                        >
                          Show less
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  );
}
