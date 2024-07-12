import ReactDOM from "react-dom/client";
import "./index.css";
import { Colors, OverlayToaster, OverlaysProvider } from "@blueprintjs/core";
import { useAtom } from "jotai";
import { darkModeAtom } from "./store/auth";
import App from "./App";
const Main = () => {
  const [isDarkMode] = useAtom(darkModeAtom);
  return (
    <OverlaysProvider>
      <div
        style={{
          background: isDarkMode ? Colors.DARK_GRAY1 : Colors.LIGHT_GRAY1,
        }}
        className={`${
          isDarkMode ? "bp5-dark" : "bp5-light"
        } min-h-screen w-full`}
      >
        <div className="toaster-container">
          <OverlayToaster />
        </div>
        <App />
      </div>
    </OverlaysProvider>
  );
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  // <React.StrictMode>
  <>
    <Main />
  </>
  // </React.StrictMode>
);
