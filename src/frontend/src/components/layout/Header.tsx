export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-sm font-bold">SL</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold">SCISLiSA</h1>
            <p className="text-xs text-muted-foreground">Scholarly Analytics</p>
          </div>
        </div>
      </div>
    </header>
  );
}
