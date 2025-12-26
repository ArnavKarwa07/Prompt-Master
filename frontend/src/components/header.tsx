"use client";

import Link from "next/link";
import { SignInButton, SignUpButton, UserButton, useUser } from "@clerk/nextjs";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  const { isSignedIn, isLoaded } = useUser();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 glass backdrop-blur-xl padding-x-2 px-2">
      <div className="container flex h-16 items-center">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="relative">
            <div className="absolute inset-0 bg-linear-to-r from-purple-500 to-pink-500 blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
            <div className="relative bg-linear-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
              <Zap className="h-5 w-5 text-white" />
            </div>
          </div>
          <span className="font-bold text-xl bg-linear-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Prompt Master
          </span>
        </Link>

        {/* Right Side */}
        <div className="flex items-center gap-3 ml-auto">
          {isLoaded && (
            <>
              {isSignedIn ? (
                <div className="flex items-center gap-3">
                  <Link href="/dashboard">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="hover:bg-white/10"
                    >
                      Dashboard
                    </Button>
                  </Link>
                  <UserButton
                    signInUrl="/"
                    appearance={{
                      elements: {
                        avatarBox: "w-9 h-9 ring-2 ring-primary/20",
                      },
                    }}
                  />
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <SignInButton mode="modal">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="hover:bg-white/10 cursor-pointer"
                    >
                      Sign In
                    </Button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <Button
                      size="sm"
                      className="gradient-primary text-white border-0 shadow-lg shadow-primary/25 cursor-pointer"
                    >
                      Get Started
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
