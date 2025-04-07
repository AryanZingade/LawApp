import React, { useState } from "react";
import { Theme } from "@radix-ui/themes"; // <- Import Theme
import "@radix-ui/themes/styles.css"; // <- Import Radix styles
import TitleArea from "./components/TitleArea";
import TextInput from "./components/TextInput";
import PdfUpload from "./components/UploadDocSum";
import ResponseBox from "./components/ResponseBox";
import Translate from "./components/TranslateDrop";
import "@radix-ui/themes/styles.css";

function App() {
  const [response, setResponse] = useState<any>(null);
  const [targetLanguage, setTargetLanguage] = useState("en");
  const [documentReady, setDocumentReady] = useState(false);

  return (
    <Theme>
      {" "}
      {/* 👈 Wrap everything in Theme */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          minHeight: "100vh",
          textAlign: "center",
        }}
      >
        <TitleArea />
        <TextInput setResponse={setResponse} />
        <Translate
          targetLanguage={targetLanguage}
          setTargetLanguage={setTargetLanguage}
        />
        <PdfUpload
          setResponse={setResponse}
          targetLanguage={targetLanguage}
          setDocumentReady={setDocumentReady}
        />
        {response && <ResponseBox response={response} />}
      </div>
    </Theme>
  );
}

export default App;
