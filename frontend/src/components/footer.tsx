import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-white/10 mt-10">
      <div className="page-center">
        <div className="page-inner px-4 md:px-6 py-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full" />
              <p>© 2025 Prompt Master. Built by Arnav Karwa</p>
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-8">
              <span className="font-medium text-primary">Contact Me</span>
              <div className="flex gap-8">
                <Link
                  href="mailto:arnavkarwa07@gmail.com"
                  className="hover:text-primary transition-colors font-medium"
                >
                  Email
                </Link>
                <Link
                  href="https://www.linkedin.com/in/arnav-karwa/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors font-medium"
                >
                  LinkedIn
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
