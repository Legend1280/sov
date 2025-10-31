import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { MirrorProvider } from "./core/MirrorContext";
import { registerComponents } from "./core/registerComponents";
import { appRegistry } from "./core/AppRegistry";
import { useEffect } from "react";
import Home from "./pages/Home";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  useEffect(() => {
    // Register all components on startup
    registerComponents();
    
    // Discover and register apps
    appRegistry.discoverApps().then(() => {
      console.log('[Mirror] App discovery complete');
    });
  }, []);

  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <MirrorProvider apiBaseUrl="http://localhost:8001">
          <TooltipProvider>
            <Toaster />
            <Router />
          </TooltipProvider>
        </MirrorProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
