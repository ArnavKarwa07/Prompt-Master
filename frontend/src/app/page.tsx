"use client";

import { Header } from "@/components/header";
import { PromptOptimizer } from "@/components/prompt-optimizer";
import { GlobalLoading } from "@/components/global-loading";
import { Footer } from "@/components/footer";
import Link from "next/dist/client/link";
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { isSignedIn, isLoaded } = useUser();
  const router = useRouter();

  // Redirect signed-in users to dashboard
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push("/dashboard");
    }
  }, [isLoaded, isSignedIn, router]);

  // Show loading state while checking auth
  if (!isLoaded || isSignedIn) {
    return <GlobalLoading message="Initializing Prompt Master" />;
  }

  return (
    <div className="flex min-h-screen flex-col dark">
      <Header />

      <main className="flex-1 mesh-gradient">
        <div className="page-center">
          <div className="page-inner">
            {/* Main Optimizer Section */}
            <section className="py-6 md:py-12">
              <div className="space-y-8">
                {/* Hero Text */}
                <div className="text-center space-y-4 mb-12">
                  <div className="inline-block">
                    <div className="flex items-center gap-2 text-sm font-medium text-primary bg-primary/10 border border-primary/20 rounded-full px-4 py-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                      <span>Multi-Agent AI System</span>
                    </div>
                  </div>

                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
                    Master Your Prompts with
                    <br />
                    <span className="bg-linear-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                      AI-Powered Optimization
                    </span>
                  </h1>

                  <p className="max-w-2xl mx-auto text-lg text-muted-foreground">
                    Get instant feedback and optimized prompts from our
                    specialized AI agents. No sign-up required to try it out.
                  </p>
                </div>

                {/* Optimizer Interface */}
                <PromptOptimizer />
              </div>
            </section>

            {/* Features Section */}
            <section className="">
              <div className="mx-auto max-w-4xl glass-strong rounded-2xl p-8 md:p-10">
                <div className="text-center mb-6">
                  <h2 className="text-2xl md:text-3xl font-bold mb-3">
                    Unlock More with a Free Account
                  </h2>
                  <p className="text-muted-foreground">
                    Sign up to access premium features and save your
                    optimization history
                  </p>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Save History</h3>
                    <p className="text-sm text-muted-foreground">
                      Keep track of all your optimized prompts
                    </p>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Unlimited Access</h3>
                    <p className="text-sm text-muted-foreground">
                      No rate limits on optimizations
                    </p>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-sky-500 to-indigo-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 15v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12m0 0l-4-4m4 4l4-4"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Upload Context</h3>
                    <p className="text-sm text-muted-foreground">
                      Upload files or paste rich context to ground your
                      optimizations
                    </p>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-amber-500 to-orange-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 7h6v10H3zM15 7h6v5h-6zM15 15h6v2a2 2 0 01-2 2h-4v-4z"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Project Parts</h3>
                    <p className="text-sm text-muted-foreground">
                      Organize prompts by project sections to keep workflows
                      tidy
                    </p>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 5v14l7-3 7 3V5H5zm7 5h.01"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Better Prompts</h3>
                    <p className="text-sm text-muted-foreground">
                      Unlock curated templates and examples tailored to your
                      domain
                    </p>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 mx-auto bg-linear-to-br from-pink-500 to-purple-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold">Advanced Analytics</h3>
                    <p className="text-sm text-muted-foreground">
                      Track your improvement over time
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Minimal Footer */}
            <Footer />
          </div>
        </div>
      </main>
    </div>
  );
}
