"use client";

import Link from "next/link";
import { SignInButton, SignUpButton, UserButton, useUser } from "@clerk/nextjs";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  const { isSignedIn, isLoaded } = useUser();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 glass backdrop-blur-xl px-2 sm:px-4">
      <div className="flex h-14 sm:h-16 w-full items-center justify-between gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-1.5 sm:gap-2 group">
          <div className="relative">
            <div className="absolute inset-0 bg-linear-to-r from-purple-500 to-pink-500 blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
            <div className="relative bg-linear-to-br from-purple-500 to-pink-500 p-1.5 sm:p-2 rounded-lg">
              <Zap className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
            </div>
          </div>
          <span className="font-bold text-lg sm:text-xl bg-linear-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            <span className="hidden xs:inline">Prompt Master</span>
            <span className="xs:hidden">PM</span>
          </span>
        </Link>

        {/* Right Side */}
        <div className="flex items-center gap-2 sm:gap-3">
          {isLoaded && (
            <>
              {isSignedIn ? (
                <div className="flex items-center gap-2 sm:gap-3">
                  <Link href="/dashboard">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="hover:bg-white/10 text-xs sm:text-sm px-2 sm:px-3"
                    >
                      <span className="hidden sm:inline">Dashboard</span>
                      <span className="sm:hidden">Dash</span>
                    </Button>
                  </Link>
                  <UserButton
                    signInUrl="/"
                    appearance={{
                      elements: {
                        avatarBox:
                          "w-8 h-8 sm:w-9 sm:h-9 ring-2 ring-primary/20",
                      },
                    }}
                  />
                </div>
              ) : (
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <SignInButton mode="modal">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="hover:bg-white/10 cursor-pointer text-xs sm:text-sm px-2 sm:px-3"
                    >
                      Sign In
                    </Button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <Button
                      size="sm"
                      className="gradient-primary text-white border-0 shadow-lg shadow-primary/25 cursor-pointer text-xs sm:text-sm px-2 sm:px-4"
                    >
                      <span className="hidden xs:inline">Get Started</span>
                      <span className="xs:hidden">Start</span>
                    </Button>
                  </SignUpButton>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </header>
  );
}
