import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Import theme CSS
import "@radix-ui/themes/styles.css";

// Import Tailwind (if you're using it)
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
