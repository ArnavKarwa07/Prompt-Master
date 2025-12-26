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
} from "lucide-react";
import { Header } from "@/components/header";
import { PromptOptimizer } from "@/components/prompt-optimizer";
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
  const [newProjectName, setNewProjectName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Set API token when user is loaded
  useEffect(() => {
    async function setToken() {
      if (user) {
        const token = await getToken();
        api.setToken(token);
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

  // Load history when project is selected
  useEffect(() => {
    async function loadHistory() {
      if (!selectedProject) {
        setHistory([]);
        return;
      }

      setIsLoadingHistory(true);
      try {
        const response = await api.getPromptHistory(selectedProject.id);
        setHistory(response.history);
      } catch (error) {
        console.error("Failed to load history:", error);
        toast.error("Failed to load history");
      } finally {
        setIsLoadingHistory(false);
      }
    }

    loadHistory();
  }, [selectedProject]);

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    setIsCreating(true);
    try {
      const project = await api.createProject(newProjectName.trim());
      setProjects([project, ...projects]);
      setNewProjectName("");
      setSelectedProject(project);
      toast.success("Project created successfully");
    } catch (error) {
      console.error("Failed to create project:", error);
      toast.error("Failed to create project");
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await api.deleteProject(projectId);
      setProjects(projects.filter((p) => p.id !== projectId));
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
      }
      toast.success("Project deleted");
    } catch (error) {
      console.error("Failed to delete project:", error);
      toast.error("Failed to delete project");
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
        <div className="container px-8 md:px-12 py-8">
          {/* Welcome Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              Welcome back, {user.firstName || "User"}! 👋
            </h1>
            <p className="text-muted-foreground">
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
              className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
            >
              <div className="glass-strong rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg bg-blue-500/20">
                    <Zap className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Total Prompts
                    </p>
                    <p className="text-2xl font-bold">{totalPrompts}</p>
                  </div>
                </div>
              </div>

              <div className="glass-strong rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg bg-green-500/20">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Avg Score</p>
                    <p className="text-2xl font-bold">{avgScore}/100</p>
                  </div>
                </div>
              </div>

              <div className="glass-strong rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg bg-purple-500/20">
                    <Award className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Favorite Agent
                    </p>
                    <p className="text-2xl font-bold capitalize">
                      {favoriteAgent}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Main Content */}
          <Tabs defaultValue="optimize" className="space-y-6">
            <TabsList className="glass-strong border-0 p-1">
              <TabsTrigger
                value="optimize"
                className="data-[state=active]:bg-primary/20"
              >
                Optimize
              </TabsTrigger>
              <TabsTrigger
                value="projects"
                className="data-[state=active]:bg-primary/20"
              >
                Projects
              </TabsTrigger>
              <TabsTrigger
                value="history"
                className="data-[state=active]:bg-primary/20"
              >
                History
              </TabsTrigger>
            </TabsList>

            {/* Optimize Tab */}
            <TabsContent value="optimize" className="space-y-4">
              <PromptOptimizer
                projectId={selectedProject?.id}
                onResult={() => {
                  if (selectedProject) {
                    api
                      .getPromptHistory(selectedProject.id)
                      .then((response) => {
                        setHistory(response.history);
                      });
                  }
                }}
              />
            </TabsContent>

            {/* Projects Tab */}
            <TabsContent value="projects">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Create New Project Card */}
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="glass-strong rounded-xl p-6 border-2 border-dashed border-white/10 hover:border-primary/30 transition-colors"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-lg bg-linear-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                      <Plus className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Create Project</h3>
                      <Input
                        placeholder="Project name"
                        value={newProjectName}
                        onChange={(e) => setNewProjectName(e.target.value)}
                        onKeyDown={(e) =>
                          e.key === "Enter" && handleCreateProject()
                        }
                        className="mb-2 bg-background/50 border-white/10"
                      />
                      <Button
                        onClick={handleCreateProject}
                        disabled={isCreating || !newProjectName.trim()}
                        className="w-full gradient-primary text-white border-0"
                        size="sm"
                      >
                        Create
                      </Button>
                    </div>
                  </div>
                </motion.div>

                {/* Project Cards */}
                {projects.map((project) => (
                  <motion.div
                    key={project.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setSelectedProject(project)}
                    className={`glass-strong rounded-xl p-6 cursor-pointer transition-all group ${
                      selectedProject?.id === project.id
                        ? "ring-2 ring-primary shadow-lg shadow-primary/20"
                        : "hover:shadow-lg"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-linear-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                        <Folder className="w-6 h-6 text-white" />
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteProject(project.id);
                        }}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                    <h3 className="font-semibold text-lg mb-1">
                      {project.name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Created{" "}
                      {project.created_at
                        ? new Date(project.created_at).toLocaleDateString()
                        : "Unknown"}
                    </p>
                  </motion.div>
                ))}
              </div>
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history">
              {!selectedProject ? (
                <div className="glass-strong rounded-xl p-12 text-center">
                  <Folder className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">
                    No Project Selected
                  </h3>
                  <p className="text-muted-foreground">
                    Select a project to view its history
                  </p>
                </div>
              ) : isLoadingHistory ? (
                <div className="glass-strong rounded-xl p-12 text-center">
                  <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-muted-foreground">Loading history...</p>
                </div>
              ) : history.length === 0 ? (
                <div className="glass-strong rounded-xl p-12 text-center">
                  <History className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No History Yet</h3>
                  <p className="text-muted-foreground">
                    Start optimizing prompts to build your history
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {history.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-strong rounded-xl p-6"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold ${
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
                            <Badge className="mb-1 capitalize">
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
                      <p className="text-sm leading-relaxed line-clamp-3 text-muted-foreground">
                        {item.prompt_text}
                      </p>
                    </motion.div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
