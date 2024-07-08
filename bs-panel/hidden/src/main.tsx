import ReactDOM from "react-dom/client";
import "./index.css";
import { Colors, OverlayToaster, OverlaysProvider } from "@blueprintjs/core";
import App from "./App";

const Main = () => {
  return (
    <OverlaysProvider>
      <div>
        <div className="toaster-container">
          <OverlayToaster />
        </div>
        <App />
      </div>
    </OverlaysProvider>
  );
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <>
    <Main />
  </>
);
