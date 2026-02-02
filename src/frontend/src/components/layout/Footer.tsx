export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container mx-auto px-6 py-4">
        <div className="flex flex-col md:flex-row justify-between items-center gap-2 text-sm text-muted-foreground">
          <div>
            Copyright © 2026. All rights reserved.
          </div>
          <div>
            Developed by <span className="font-medium text-foreground">24MCPC14 (ABC Trust)</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
